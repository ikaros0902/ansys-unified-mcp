"""Build the ANSYS-ready ODB++ from the vendor archive and the normalized stackup."""
from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from . import odb
from .asker import Asker, Question
from .intake import Layer
from .stp import stp_bbox_mm
from .util import MIL_PER_OZ, ToolError

PREFERRED_STEP_NAMES = ("PCB", "UNIT", "BOARD", "EDIT", "ORIG", "SINGLE")


@dataclass
class BuildResult:
    tgz: Path
    job_dir: Path                 # extracted, edited job (kept until coverage is done)
    step_dir: Path
    shift_in: tuple[float, float]
    profile_before_in: tuple
    profile_after_in: tuple
    dropped_steps: list[str]
    dropped_layers: list[str]
    notes: list[tuple[str, str]] = field(default_factory=list)


def choose_step(job: odb.JobInfo, cfg_step: str | None, asker: Asker, notes: list) -> str:
    if cfg_step:
        s = cfg_step.upper()
        if s not in job.steps:
            raise ToolError(f"step {cfg_step!r} not in the ODB++ (steps: {job.steps})")
        return s
    cands = odb.step_candidates(job)
    if len(job.steps) == 1:
        return job.steps[0]
    pref = [s for s in cands if s in PREFERRED_STEP_NAMES]
    if len(pref) == 1:
        notes.append(("INFO", f"step {pref[0]} chosen automatically from {len(job.steps)} steps "
                              f"(single-board steps: {cands})"))
        return pref[0]
    opts = []
    for s in cands or job.steps:
        try:
            x0, y0, x1, y1 = odb.profile_bbox(job.profiles.get(s, ""))
            size = f"profile {(x1 - x0) * 25.4:.1f} x {(y1 - y0) * 25.4:.1f} mm"
        except ToolError:
            size = "no profile"
        opts.append((s, size))
    a = asker.choose(Question("odb.step", f"The ODB++ has {len(job.steps)} steps and the ANSYS reader accepts "
                                          "only one. Which step is the single PCB?", opts))
    return a


def compute_shift(mode, bbox_in, offset_mm) -> tuple[float, float]:
    x0, y0, _, _ = bbox_in
    if mode == "profile_lower_left":
        return -x0, -y0
    if mode == "keep":
        return 0.0, 0.0
    if mode == "offset_mm":
        if not offset_mm or len(offset_mm) != 2:
            raise ToolError('origin.mode "offset_mm" needs origin.offset_mm = [dx, dy]')
        return offset_mm[0] / 25.4, offset_mm[1] / 25.4
    raise ToolError(f"unknown origin.mode {mode!r} (profile_lower_left | keep | offset_mm)")


def build(cfg: dict, job: odb.JobInfo, layers: list[Layer], work: Path, out_tgz: Path,
          asker: Asker, log) -> BuildResult:
    notes: list[tuple[str, str]] = []
    step = choose_step(job, cfg["options"].get("pcb_step"), asker, notes)
    step_dir = job.step_dirs[step]
    copper = job.copper
    keep = {d["NAME"].lower() for d in copper}
    log(f"  extracting step {step} with {len(keep)} copper layers ...")
    jdir = odb.extract_selected(job.tgz, work / "src", step_dir, keep)
    job_name = cfg["project"]["output_job_name"]
    jnew = jdir.parent / job_name
    jdir.rename(jnew)
    jdir = jnew
    notes.append(("INFO", odb.stamp_info(jdir, job_name)))
    default_units = (job.info.get("UNITS") or "INCH").upper()

    sdir = jdir / "steps" / step_dir
    if not (sdir / "profile").exists():
        raise ToolError(f"step {step} has no profile (board outline)")
    hdr = (sdir / "stephdr").read_text(encoding="latin-1") if (sdir / "stephdr").exists() else ""
    if "STEP-REPEAT" in hdr:
        raise ToolError(f"step {step} is a panel (STEP-REPEAT) - choose the single-board step")

    ocfg = cfg["options"].get("origin", {"mode": "profile_lower_left"})
    before = odb.profile_bbox((sdir / "profile").read_text(encoding="latin-1"))
    dx, dy = compute_shift(ocfg.get("mode", "profile_lower_left"), before, ocfg.get("offset_mm"))
    log(f"  profile {before[0]:.4f},{before[1]:.4f} .. {before[2]:.4f},{before[3]:.4f} in; "
        f"shift dx={dx:+.5f} dy={dy:+.5f} in ({dx * 25.4:+.3f}, {dy * 25.4:+.3f} mm)")
    odb.shift_file(sdir / "profile", dx, dy, default_units)
    if (sdir / "stephdr").exists():
        odb.shift_stephdr(sdir / "stephdr", dx, dy)
    after = odb.profile_bbox((sdir / "profile").read_text(encoding="latin-1"))

    stp_path = cfg["inputs"].get("step_2d_drawing", {}).get("path")
    if stp_path:
        sx0, sy0, sx1, sy1 = stp_bbox_mm(Path(stp_path))
        ax0, ay0, ax1, ay1 = (v * 25.4 for v in after)
        same_size = abs((sx1 - sx0) - (ax1 - ax0)) < 0.5 and abs((sy1 - sy0) - (ay1 - ay0)) < 0.5
        same_origin = abs(sx0 - ax0) < 0.5 and abs(sy0 - ay0) < 0.5
        msg = (f"2D drawing {Path(stp_path).name}: {sx1 - sx0:.2f} x {sy1 - sy0:.2f} mm at ({sx0:.2f}, {sy0:.2f}); "
               f"ODB++ profile after shift: {ax1 - ax0:.2f} x {ay1 - ay0:.2f} mm at ({ax0:.2f}, {ay0:.2f})")
        if same_size and same_origin:
            notes.append(("INFO", msg + " - aligned"))
        else:
            notes.append(("WARN", msg + " - NOT the same rectangle. External Data maps by absolute "
                                        "coordinates: check that the copper lands on the right place of the "
                                        "3D model (docs/03_vendor_odb_defects.md, D10)."))

    copper_layers = [L for L in layers if L.kind == "copper"]
    if len(copper_layers) != len(copper):
        raise ToolError(f"stackup has {len(copper_layers)} copper layers, ODB++ has {len(copper)}")
    out_layers: list[dict] = []
    cu_i = 0
    for L in layers:
        name = L.odb_name
        if not odb.NAME_OK.match(name):
            raise ToolError(f"layer name {name!r} is not valid for ODB++ (A-Z 0-9 _ + - . only)")
        if L.kind == "copper":
            d = dict(copper[cu_i])
            cu_i += 1
            old = d["NAME"]
            src = sdir / "layers" / old.lower()
            dst = sdir / "layers" / name.lower()
            if not src.is_dir():
                src.mkdir(parents=True)
                notes.append(("WARN", f"copper layer {old} had no folder in step {step}; created empty"))
            src.rename(dst)
            feats = odb.features_file(dst)
            n = odb.shift_file(feats, dx, dy, default_units)
            odb.put_attrs_first(dst / "attrlist", {".copper_weight": f"{L.thickness_mil / MIL_PER_OZ:.6f}",
                                                   ".layer_dielectric": "0.000000"})
            for s in list(dst.glob(".*.sum")):
                s.unlink()
            d.update(NAME=name, OLD_NAME=old)
            out_layers.append(d)
            log(f"  {name:<20} <- {old:<8} {L.thickness_mil:>7.3f} mil, {n} records shifted")
        else:
            dst = sdir / "layers" / name.lower()
            dst.mkdir(parents=True)
            (dst / "features").write_text("#\n#Layer features\n#\n", encoding="latin-1", newline="\n")
            odb.put_attrs_first(dst / "attrlist", {".layer_dielectric": f"{L.thickness_mil / 1000:.6f}"})
            d = {"CONTEXT": "BOARD", "TYPE": "DIELECTRIC", "NAME": name, "POLARITY": "POSITIVE",
                 "DIELECTRIC_TYPE": "CORE" if L.diel_type == "core" else "PREPREG",
                 "DIELECTRIC_NAME": L.material if cfg["options"].get("write_dielectric_name", True) else "",
                 "START_NAME": "", "END_NAME": "", "OLD_NAME": ""}
            out_layers.append(d)
            log(f"  {name:<20} <- new      {L.thickness_mil:>7.3f} mil ({L.diel_type})")
    leftovers = [p.name for p in (sdir / "layers").iterdir()
                 if p.name not in {d["NAME"].lower() for d in out_layers}]
    if leftovers:
        raise ToolError(f"unexpected layer folders left in the step: {leftovers}")
    for s in (jdir / "matrix").glob(".*.sum"):
        s.unlink()
    (jdir / "matrix" / "matrix").write_text(odb.format_matrix([{"NAME": step}], out_layers),
                                            encoding="latin-1", newline="\n")
    odb.pack_tgz(jdir, out_tgz)
    dropped_layers = [d["NAME"] for d in job.layers if not odb.is_copper(d)]
    return BuildResult(out_tgz, jdir, sdir, (dx, dy), before, after,
                       [s for s in job.steps if s != step], dropped_layers, notes)


def cleanup(work: Path) -> None:
    shutil.rmtree(work, ignore_errors=True)
