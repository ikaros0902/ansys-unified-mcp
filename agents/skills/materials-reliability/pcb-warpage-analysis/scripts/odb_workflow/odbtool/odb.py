"""ODB++ reading and editing (extracted copies only; the vendor archive is never written).

Facts this module relies on (all verified with the ANSYS 2025 R1 / 2026 R1 readers, see
docs/03_vendor_odb_defects.md and docs/04_build_procedure.md):
  * one job folder per archive; steps/<step>/layers/<layer>/{features[.Z],attrlist}
  * matrix/matrix: STEP {..} and LAYER {..} blocks.  The ANSYS reader rejects the
    'VERSION=0' line written by InCAM 8.x and only needs the classic fields
  * features.Z = Unix 'compress' (LZW); decompressed with unlzw3 (7-Zip as fallback)
  * archive must be GNU tar inside gzip WITHOUT a stored file name, otherwise the
    translator's 7-Zip unpacks to the wrong place ("matrix/matrix does not exist")
"""
from __future__ import annotations

import gzip
import re
import shutil
import subprocess
import tarfile
from dataclasses import dataclass, field
from pathlib import Path

from .util import ToolError, fmt

SEVENZ = r"C:\Program Files\7-Zip\7z.exe"
COPPER_TYPES = ("SIGNAL", "POWER_GROUND", "MIXED")
STEP_DROP = ("netlists", "chk", "tha", "pstack_info", "eda", "boxes")   # caches tied to old layers/coords
JOB_KEEP = ("matrix", "misc", "steps", "symbols", "fonts")               # everything else is CAM history
CLASSIC_FIELDS = ["ROW", "CONTEXT", "TYPE", "NAME", "POLARITY", "DIELECTRIC_TYPE", "DIELECTRIC_NAME",
                  "START_NAME", "END_NAME", "OLD_NAME"]
NAME_OK = re.compile(r"^[A-Z0-9_+\-.]{1,64}$")


# ---------------------------------------------------------------- matrix
def parse_matrix(text: str) -> tuple[list[dict], list[dict]]:
    steps, layers = [], []
    for kind, body in re.findall(r"(STEP|LAYER)\s*\{(.*?)\}", text, re.S):
        d = {}
        for line in body.splitlines():
            if "=" in line:
                k, _, v = line.strip().partition("=")
                d[k.strip()] = v.strip()
        (steps if kind == "STEP" else layers).append(d)
    layers.sort(key=lambda d: int(d.get("ROW", "0")))
    return steps, layers


def format_matrix(steps: list[dict], layers: list[dict]) -> str:
    """Classic matrix: no VERSION line, classic LAYER fields only (accepted by v251 and v261)."""
    out = []
    for i, s in enumerate(steps, 1):
        out.append(f"STEP {{\n    COL={i}\n    NAME={s['NAME']}\n}}\n")
    for i, d in enumerate(layers, 1):
        d = dict(d, ROW=str(i))
        lines = []
        for k in CLASSIC_FIELDS:
            if k in ("DIELECTRIC_TYPE", "DIELECTRIC_NAME") and d.get("TYPE") != "DIELECTRIC":
                continue
            lines.append(f"    {k}={d.get(k, '')}")
        out.append("LAYER {\n" + "\n".join(lines) + "\n}\n")
    return "\n".join(out)


def is_copper(d: dict) -> bool:
    return d.get("CONTEXT") == "BOARD" and d.get("TYPE") in COPPER_TYPES


# ---------------------------------------------------------------- scan
@dataclass
class JobInfo:
    tgz: Path
    job: str
    info: dict
    steps: list[str]                          # names as in the matrix (upper case)
    step_dirs: dict[str, str]                 # upper name -> folder name in the archive
    layers: list[dict]
    stephdr: dict[str, str] = field(default_factory=dict)
    profiles: dict[str, str] = field(default_factory=dict)
    matrix_has_version_line: bool = False

    @property
    def copper(self) -> list[dict]:
        return [d for d in self.layers if is_copper(d)]


def scan(tgz: Path) -> JobInfo:
    """One pass over the archive reading only small text files."""
    tgz = Path(tgz)
    tops, matrix, info, hdr, prof, dirs = set(), None, "", {}, {}, {}
    with tarfile.open(tgz, "r:*") as tf:
        for m in tf:
            p = m.name.strip("/").split("/")
            tops.add(p[0])
            if len(p) == 3 and p[1] == "matrix" and p[2] == "matrix":
                matrix = tf.extractfile(m).read().decode("latin-1")
            elif len(p) == 3 and p[1] == "misc" and p[2] == "info":
                info = tf.extractfile(m).read().decode("latin-1")
            elif len(p) >= 3 and p[1] == "steps":
                dirs[p[2].upper()] = p[2]
                if len(p) == 4 and p[3] == "stephdr":
                    hdr[p[2].upper()] = tf.extractfile(m).read().decode("latin-1")
                elif len(p) == 4 and p[3] == "profile":
                    prof[p[2].upper()] = tf.extractfile(m).read().decode("latin-1")
    if len(tops) != 1:
        raise ToolError(f"{tgz.name}: expected one top-level job folder, found {sorted(tops)}")
    if matrix is None:
        raise ToolError(f"{tgz.name}: matrix/matrix not found - not an ODB++ archive?")
    steps, layers = parse_matrix(matrix)
    kv = dict(l.split("=", 1) for l in info.splitlines() if "=" in l)
    return JobInfo(tgz, tops.pop(), kv, [s["NAME"].upper() for s in steps], dirs, layers, hdr, prof,
                   bool(re.match(r"\s*VERSION\s*=", matrix)))


def step_candidates(job: JobInfo) -> list[str]:
    """Steps that are a single board: no STEP-REPEAT, has a profile."""
    out = []
    for s in job.steps:
        h = job.stephdr.get(s, "")
        if "STEP-REPEAT" in h:
            continue
        if not profile_points(job.profiles.get(s, "")):
            continue
        out.append(s)
    return out


# ---------------------------------------------------------------- extraction
def extract_selected(tgz: Path, dest: Path, step_dir: str, keep_layers: set[str]) -> Path:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    drop = set(STEP_DROP) | {f".{s}.sum" for s in STEP_DROP}
    with tarfile.open(tgz, "r:*") as tf:
        for m in tf:
            p = m.name.strip("/").split("/")
            if len(p) >= 2 and p[1] not in JOB_KEEP:
                continue
            if len(p) >= 3 and p[1] == "steps":
                if p[2] != step_dir:
                    continue
                if len(p) >= 4 and p[3] in drop:
                    continue
                if len(p) >= 5 and p[3] == "layers" and p[4] not in keep_layers:
                    continue
            tf.extract(m, dest, filter="data")
    tops = [d for d in dest.iterdir() if d.is_dir()]
    if len(tops) != 1:
        raise ToolError(f"expected one job folder after extraction, found {tops}")
    return tops[0]


def decompress_z(path: Path) -> Path:
    """features.Z -> features."""
    target = path.with_suffix("")
    data = path.read_bytes()
    try:
        import unlzw3
        target.write_bytes(unlzw3.unlzw(data))
    except Exception:                                          # noqa: BLE001
        tmp = path.parent / "_z_tmp"
        tmp.mkdir(exist_ok=True)
        r = subprocess.run([SEVENZ, "e", "-y", f"-o{tmp}", str(path)], capture_output=True)
        files = list(tmp.iterdir())
        if r.returncode != 0 or len(files) != 1:
            raise ToolError(f"cannot decompress {path}")
        shutil.move(str(files[0]), target)
        tmp.rmdir()
    path.unlink()
    drop_sum(path)
    return target


def features_file(layer_dir: Path) -> Path:
    z = layer_dir / "features.Z"
    if z.exists():
        return decompress_z(z)
    f = layer_dir / "features"
    if not f.exists():
        f.write_text("#\n#Layer features\n#\n", encoding="latin-1", newline="\n")
    return f


def drop_sum(path: Path) -> None:
    for s in (path.parent / f".{path.name}.sum", path.parent / f".{path.name}.Z.sum"):
        if s.exists():
            s.unlink()


# ---------------------------------------------------------------- coordinates
COORD_SLOTS = {
    "P": [(1, 2)], "T": [(1, 2)], "B": [(1, 2)],
    "L": [(1, 2), (3, 4)],
    "A": [(1, 2), (3, 4), (5, 6)],
    "OB": [(1, 2)], "OS": [(1, 2)],
    "OC": [(1, 2), (3, 4)],
}
NUM = re.compile(r"-?\d+(\.\d*)?([eE][-+]?\d+)?$")


def file_units(text: str, default: str = "INCH") -> str:
    m = re.search(r"^(?:UNITS\s*=\s*|U\s+)(INCH|MM)\b", text, re.M | re.I)
    return m.group(1).upper() if m else default


def shift_text(text: str, dx_in: float, dy_in: float, default_units: str = "INCH") -> tuple[str, int, int]:
    """Shift every coordinate record; returns (text, shifted, not_shifted)."""
    k = 25.4 if file_units(text, default_units) == "MM" else 1.0
    dx, dy = dx_in * k, dy_in * k
    out, n, bad = [], 0, 0
    for line in text.splitlines():
        tok = line.split(" ")
        slots = COORD_SLOTS.get(tok[0]) if tok else None
        if slots:
            if all(iy < len(tok) and NUM.match(tok[ix]) and NUM.match(tok[iy]) for ix, iy in slots):
                for ix, iy in slots:
                    tok[ix] = fmt(float(tok[ix]) + dx, 12)
                    tok[iy] = fmt(float(tok[iy]) + dy, 12)
                n += 1
                line = " ".join(tok)
            else:
                bad += 1
        out.append(line)
    return "\n".join(out) + "\n", n, bad


def shift_file(path: Path, dx_in: float, dy_in: float, default_units: str = "INCH") -> int:
    text = path.read_text(encoding="latin-1")
    new, n, bad = shift_text(text, dx_in, dy_in, default_units)
    if bad:
        raise ToolError(f"{path}: {bad} coordinate records could not be parsed - not shifted")
    path.write_text(new, encoding="latin-1", newline="\n")
    drop_sum(path)
    return n


def profile_points(text: str) -> list[tuple[float, float]]:
    pts = []
    k = 1 / 25.4 if file_units(text) == "MM" else 1.0
    for line in text.splitlines():
        tok = line.split()
        if tok and tok[0] in ("OB", "OS"):
            pts.append((float(tok[1]) * k, float(tok[2]) * k))
        elif tok and tok[0] == "OC":
            pts.append((float(tok[1]) * k, float(tok[2]) * k))
    return pts


def profile_bbox(text: str) -> tuple[float, float, float, float]:
    """Bounding box in inch (arcs included through their centres' extreme points)."""
    pts = profile_points(text)
    if not pts:
        raise ToolError("profile has no outline")
    k = 1 / 25.4 if file_units(text) == "MM" else 1.0
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    for line in text.splitlines():
        tok = line.split()
        if tok and tok[0] == "OC":
            xs.append(float(tok[3]) * k)
            ys.append(float(tok[4]) * k)
    return min(xs), min(ys), max(xs), max(ys)


def shift_stephdr(path: Path, dx_in: float, dy_in: float) -> None:
    t = path.read_text(encoding="latin-1")
    k = 25.4 if file_units(t) == "MM" else 1.0
    for key, d in (("X_DATUM", dx_in), ("Y_DATUM", dy_in)):
        t = re.sub(rf"^{key}=(.*)$", lambda m: f"{key}={fmt(float(m.group(1)) + d * k, 12)}", t, flags=re.M)
    path.write_text(t, encoding="latin-1", newline="\n")
    drop_sum(path)


# ---------------------------------------------------------------- attributes / info
def put_attrs_first(path: Path, values: dict[str, str]) -> None:
    """Set attributes right after the UNITS line.  The ANSYS reader stops reading an
    attrlist at the first line it does not understand, so these must come first."""
    lines = path.read_text(encoding="latin-1").splitlines() if path.exists() else []
    lines = [l for l in lines if l.partition("=")[0].strip() not in values]
    at = 1 if lines and lines[0].startswith("UNITS=") else 0
    lines[at:at] = [f"{k} = {v}" for k, v in values.items()]
    path.write_text("\n".join(lines) + "\n", encoding="latin-1", newline="\n")
    drop_sum(path)


def stamp_info(job: Path, job_name: str) -> str:
    p = job / "misc" / "info"
    t = p.read_text(encoding="latin-1") if p.exists() else ""
    major = int(re.search(r"ODB_VERSION_MAJOR=(\d+)", t).group(1)) if "ODB_VERSION_MAJOR" in t else 0
    if major < 8:
        t = re.sub(r"ODB_VERSION_MAJOR=\d+", "ODB_VERSION_MAJOR=8", t) if major else t + "ODB_VERSION_MAJOR=8\n"
        t = re.sub(r"ODB_VERSION_MINOR=\d+", "ODB_VERSION_MINOR=1", t) if "ODB_VERSION_MINOR" in t \
            else t + "ODB_VERSION_MINOR=1\n"
    t = re.sub(r"JOB_NAME=.*", f"JOB_NAME={job_name}", t) if "JOB_NAME=" in t else f"JOB_NAME={job_name}\n" + t
    p.write_text(t, encoding="latin-1", newline="\n")
    drop_sum(p)
    jn = job / "misc" / "job_name"
    if jn.exists():
        jn.write_text(job_name + "\n", encoding="latin-1", newline="\n")
        drop_sum(jn)
    return f"ODB++ {major} -> 8.1 (dielectric layers need 8.x)" if major < 8 else f"ODB++ {major} kept"


# ---------------------------------------------------------------- packing
def pack_tgz(job: Path, out: Path) -> Path:
    if out.exists():
        raise ToolError(f"{out} already exists - not overwriting")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.GNU_FORMAT) as tf:
            tf.add(str(job), arcname=job.name)
    return out
