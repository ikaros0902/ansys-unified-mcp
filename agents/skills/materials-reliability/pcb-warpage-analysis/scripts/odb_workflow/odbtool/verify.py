"""Closed-loop check with the ANSYS ODB++ translators (2025 R1 = v251, 2026 R1 = v261).

The translator turns the ODB++ into an EDB.  The EDB stackup is stored in edb.def as text
records  SLayer(Layer(N='layer_1_em892k2', T='signal', ...), SubL(Th='3mil', ...))
which are read back with a regular expression and compared with the stackup, layer by
layer.  The EDB itself is deleted afterwards (only the report and the log are kept).
"""
from __future__ import annotations

import mmap
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from .intake import Layer

TRANSLATOR = r"C:\Program Files\ANSYS Inc\{ver}\Electronics\Win64\anstranslator.exe"
UNIT_TO_MIL = {"mil": 1.0, "mm": 1 / 0.0254, "um": 1 / 25.4, "in": 1000.0, "meter": 1 / 2.54e-5,
               "m": 1 / 2.54e-5, "cm": 1 / 0.00254, "nm": 1 / 25400.0}
SLAYER = re.compile(rb"SLayer\(Layer\(N='([^']*)'[^)]*?T='([a-z]+)'(.*?)\)\s*,?\s*SubL\((.*?)\)\)", re.S)
FIELD = re.compile(rb"(\w+)='([^']*)'")
TOL_MIL = 0.01


@dataclass
class VersionResult:
    version: str
    ok: bool
    summary: str
    errors: list[str] = field(default_factory=list)
    warnings: dict[str, int] = field(default_factory=dict)
    rows: list[dict] = field(default_factory=list)
    total_edb: float = 0.0
    total_ref: float = 0.0
    mismatches: int = 0
    log_file: str = ""
    seconds: float = 0.0
    materials: list[str] = field(default_factory=list)


def _to_mil(text: str):
    m = re.fullmatch(r"\s*(-?[0-9.eE+-]+)\s*([a-z]*)\s*", text or "")
    if not m:
        return None
    return float(m.group(1)) * UNIT_TO_MIL.get(m.group(2) or "meter", float("nan"))


def read_edb_stackup(edb_def: Path) -> list[dict]:
    with open(edb_def, "rb") as fh, mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ) as m:
        data = m[:]
    out = []
    for mt in SLAYER.finditer(data):
        layer = dict((k.decode(), v.decode()) for k, v in FIELD.findall(mt.group(3)))
        sub = dict((k.decode(), v.decode()) for k, v in FIELD.findall(mt.group(4)))
        out.append({"name": mt.group(1).decode(), "type": mt.group(2).decode(),
                    "thickness_mil": _to_mil(sub.get("Th", "")),
                    "material": sub.get("Mat", layer.get("Mat", ""))})
    return out


def translate(version: str, tgz: Path, work: Path, log_dir: Path, timeout: int = 1800) -> tuple[Path, Path, float]:
    exe = Path(TRANSLATOR.format(ver=version))
    if not exe.exists():
        raise FileNotFoundError(f"translator not found: {exe}")
    aedb = work / f"verify_{version}.aedb"
    log = log_dir / f"translate_{version}.log"
    for attempt in range(LICENSE_RETRIES + 1):
        if aedb.exists():
            shutil.rmtree(aedb)
        if log.exists():
            log.unlink()
        t0 = time.time()
        subprocess.run([str(exe), str(tgz), str(aedb), f"-l={log}"], capture_output=True, timeout=timeout)
        txt = log.read_text(encoding="latin-1", errors="replace") if log.exists() else ""
        if is_license_problem(txt) and attempt < LICENSE_RETRIES:
            time.sleep(LICENSE_WAIT_S)         # licence busy or licence server not reachable
            continue
        return aedb, log, time.time() - t0
    return aedb, log, 0.0


LICENSE_RETRIES = 4
LICENSE_WAIT_S = 90
_LICENSE_MARKERS = ("Licensed number of users already reached", "Cannot checkout", "FlexNet Licensing error",
                    "License server", "LM_LICENSE_FILE")


def is_license_problem(log_text: str) -> bool:
    return any(m in log_text for m in _LICENSE_MARKERS)


def classify_log(text: str) -> tuple[list[str], dict[str, int]]:
    errs = re.findall(r"Error: ([^\n]*)", text)
    warns: dict[str, int] = {}
    for w in re.findall(r"Warning: ([^\n]*)", text):
        key = re.sub(r"[A-Za-z]:[/\\][^ ']*", "<path>", w)
        key = re.sub(r"'[^']*'", "'..'", key)
        key = re.sub(r"\d+(\.\d+)?", "#", key)[:120]
        warns[key] = warns.get(key, 0) + 1
    return [re.sub(r"[A-Za-z]:[/\\][^ ']*", "<path>", e) for e in errs], warns


def check(version: str, tgz: Path, layers: list[Layer], work: Path, log_dir: Path, log) -> VersionResult:
    log(f"  translating with {version} ...")
    aedb, logf, sec = translate(version, tgz, work, log_dir)
    txt = logf.read_text(encoding="latin-1", errors="replace") if logf.exists() else ""
    m = re.search(r"Total Errors: (\d+) Total Warnings: (\d+)", txt)
    summary = m.group(0) if m else "translator wrote no result line"
    errs, warns = classify_log(txt)
    if is_license_problem(txt):
        summary += " - ANSYS LICENCE NOT AVAILABLE (not an ODB++ problem): rerun verification later"
        errs = ["licence: " + e[:160] for e in errs]
    res = VersionResult(version, False, summary, errs, warns, log_file=logf.name, seconds=sec)
    edb_def = aedb / "edb.def"
    if not edb_def.exists():
        res.errors.append("no edb.def produced")
        return res
    st = read_edb_stackup(edb_def)
    shutil.rmtree(aedb, ignore_errors=True)
    res.materials = sorted({s["material"] for s in st if s["material"]})
    bad = 0
    for i, L in enumerate(layers):
        e = st[i] if i < len(st) else None
        want_type = "signal" if L.kind == "copper" else "dielectric"
        row = {"seq": L.seq, "expected_name": L.odb_name.lower(), "expected_type": want_type,
               "expected_mil": L.thickness_mil,
               "edb_name": e["name"] if e else "-", "edb_type": e["type"] if e else "-",
               "edb_mil": e["thickness_mil"] if e else None, "edb_material": e["material"] if e else ""}
        row["ok"] = bool(e and e["name"].lower() == row["expected_name"] and e["type"] == want_type
                         and e["thickness_mil"] is not None and abs(e["thickness_mil"] - L.thickness_mil) <= TOL_MIL)
        bad += not row["ok"]
        res.rows.append(row)
    extra = len(st) - len(layers)
    res.mismatches = bad + max(0, extra)
    res.total_edb = sum(s["thickness_mil"] or 0 for s in st)
    res.total_ref = sum(L.thickness_mil for L in layers)
    errors_n = int(m.group(1)) if m else -1
    res.ok = (errors_n == 0 and res.mismatches == 0 and len(st) == len(layers)
              and abs(res.total_edb - res.total_ref) <= TOL_MIL)
    log(f"  {version}: {summary}; {len(st)} EDB layers; mismatches {res.mismatches}; "
        f"total {res.total_edb:.3f} / {res.total_ref:.3f} mil -> {'PASS' if res.ok else 'FAIL'}")
    return res
