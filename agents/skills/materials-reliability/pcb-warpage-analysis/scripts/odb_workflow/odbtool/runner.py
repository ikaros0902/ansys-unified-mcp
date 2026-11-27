"""End-to-end run driven by one project JSON (see 4_config/project_config.template.json)."""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

from . import __version__, build as build_mod, coverage, matlib, odb, outputs, report, verify
from .asker import Asker, save_answers
from .intake import run_intake
from .stp import stp_bbox_mm
from .util import Log, NeedAnswer, ToolError, sha256, timestamp

TOOL_ROOT = Path(__file__).resolve().parent.parent
EXIT_OK, EXIT_FAIL, EXIT_QUESTION, EXIT_INPUT = 0, 1, 2, 3


def _resolve(cfg: dict, base: Path) -> None:
    """Relative paths in the config are relative to the config file; '{tool}' = tool folder."""
    def fix(p):
        if not p:
            return p
        p = p.replace("{tool}", str(TOOL_ROOT))
        q = Path(os.path.expandvars(p))
        return str(q if q.is_absolute() else (base / q).resolve())
    for v in cfg["inputs"].values():
        if isinstance(v, dict) and v.get("path"):
            v["path"] = fix(v["path"])
    cfg["output"]["root"] = fix(cfg["output"]["root"])
    tpl = cfg["options"].get("mechanical_script_template")
    if tpl:
        cfg["options"]["mechanical_script_template"] = fix(tpl)


def _rel(p: Path, base: Path) -> str:
    """Path as written in the report: relative to the project JSON (no personal folders), if possible."""
    try:
        return os.path.relpath(p, base)
    except ValueError:                      # other drive
        return str(p)


def load_config(path: Path) -> dict:
    cfg = json.loads(path.read_text(encoding="utf-8"))
    for key in ("project", "inputs", "options", "output"):
        if key not in cfg:
            raise ToolError(f"{path.name}: missing section '{key}'")
    cfg.setdefault("answers", {})
    _resolve(cfg, path.parent)
    p = cfg["project"]
    for k in ("name", "vendor"):
        if not p.get(k):
            raise ToolError(f"{path.name}: project.{k} is empty")
    p.setdefault("output_job_name", f"{p['name']}_{p['vendor']}".lower().replace(" ", "_"))
    for role in ("vendor_odb", "vendor_stackup", "design_material_table"):
        q = cfg["inputs"].get(role, {}).get("path")
        if not q:
            raise ToolError(f"{path.name}: inputs.{role}.path is empty")
        if not Path(q).is_file():
            raise ToolError(f"inputs.{role}.path not found: {q}")
    for role in ("material_library", "step_2d_drawing"):
        q = cfg["inputs"].get(role, {}).get("path")
        if q and not Path(q).is_file():
            raise ToolError(f"inputs.{role}.path not found: {q}")
    return cfg


def run(config_path: Path, interactive: bool | None = None, intake_only: bool = False) -> int:
    config_path = Path(config_path).resolve()
    early = Log(None)
    try:
        cfg = load_config(config_path)
    except ToolError as e:
        early(f"INPUT ERROR: {e}")
        return EXIT_INPUT
    if interactive is None:
        interactive = bool(cfg["options"].get("interactive", True))
    proj, vendor = cfg["project"]["name"], cfg["project"]["vendor"]
    run_name = cfg["output"].get("name_pattern", "{project}_{vendor}_{timestamp}").format(
        project=proj, vendor=vendor, timestamp=timestamp())
    out_dir = Path(cfg["output"]["root"]) / run_name
    work = Path(cfg["options"].get("work_dir") or tempfile.gettempdir()) / "pcb_thermal_warpage" / run_name
    log = early
    asker = Asker(interactive, {k: v for k, v in cfg["answers"].items() if not k.startswith("_")}, log)
    hashes = {}
    try:
        log(f"ODB Modifying Tool {__version__} (pcb-thermal-warpage)  project {proj} / {vendor}")
        for role in ("vendor_odb", "vendor_stackup", "design_material_table"):
            p = Path(cfg["inputs"][role]["path"])
            hashes[role] = (p, sha256(p))
        log("[1/6] scanning ODB++ ...")
        job = odb.scan(Path(cfg["inputs"]["vendor_odb"]["path"]))
        cu = [d["NAME"] for d in job.copper]
        log(f"  job {job.job}, ODB++ {job.info.get('ODB_VERSION_MAJOR', '?')}.{job.info.get('ODB_VERSION_MINOR', '?')}, "
            f"{len(job.steps)} steps, {len(job.layers)} layers, {len(cu)} copper: {cu[0]} .. {cu[-1]}")
        if not cu:
            raise ToolError("no BOARD SIGNAL/POWER_GROUND/MIXED layer in the matrix")
        log("[2/6] intake (vendor stackup + design material table) ...")
        intake = run_intake(cfg, cu, asker, log)
        for lvl, t in intake.notes:
            log(f"  {lvl}: {t}")
        # step choice may also need an answer - ask before creating any output
        build_notes: list = []
        build_mod.choose_step(job, cfg["options"].get("pcb_step"), asker, build_notes)
    except NeedAnswer as e:
        qfile = config_path.parent / f"open_questions_{proj}_{vendor}.md"
        if asker.pending:
            asker.write_pending(qfile)
            log(f"STOPPED: question '{asker.pending[0].key}' needs an answer. See {qfile}")
        else:
            log(f"STOPPED: {e}")
        if asker.asked:
            save_answers(config_path, asker.answers)
        return EXIT_QUESTION
    except ToolError as e:
        log(f"INPUT ERROR: {e}")
        if asker.asked:
            save_answers(config_path, asker.answers)
        return EXIT_INPUT
    if asker.asked:
        save_answers(config_path, asker.answers)
        log(f"  answers saved into {config_path.name}")
    if intake_only:
        log("")
        log(f"{'#':>3} {'ODB++ layer':<20} {'kind':<8} {'thick mil':>9} {'vendor ODB':<10} {'design':<6} "
            f"{'vendor rows':<11} {'design rows':<11}")
        for L in intake.layers:
            log(f"{L.seq:>3} {L.odb_name:<20} {(L.kind if L.kind == 'copper' else L.diel_type):<8} "
                f"{L.thickness_mil:>9.4f} {L.vendor_odb_name:<10} {L.ecad_name:<6} {L.vendor_row:<11} {L.design_row:<11}")
        log(f"INTAKE OK: {len(intake.layers)} layers, total {sum(L.thickness_mil for L in intake.layers):.3f} mil")
        return EXIT_OK

    if out_dir.exists():
        log(f"INPUT ERROR: output folder exists: {out_dir}")
        return EXIT_INPUT
    out_dir.mkdir(parents=True)
    log = Log(out_dir / "run.log")
    log("\n".join(early.lines))
    asker.log = log
    layers = intake.layers
    try:
        log("[3/6] building ODB++ ...")
        tgz = out_dir / f"{run_name}.tgz"
        b = build_mod.build(cfg, job, layers, work, tgz, asker, log)
        log(f"  written {tgz.name} ({tgz.stat().st_size / 1e6:.1f} MB)")

        log("[4/6] copper coverage ...")
        ccfg = cfg["options"].get("coverage", {})
        cov = None
        regions = ["profile"]
        if ccfg.get("enabled", True):
            extra = {}
            stp = cfg["inputs"].get("step_2d_drawing", {}).get("path")
            if stp and ccfg.get("also_drawing_region", True):
                x0, y0, x1, y1 = stp_bbox_mm(Path(stp))
                extra["drawing"] = (x0 / 25.4, y0 / 25.4, x1 / 25.4, y1 / 25.4)
            for name, rect in (ccfg.get("extra_regions_mm") or {}).items():
                extra[name] = tuple(v / 25.4 for v in rect)
            regions += list(extra)
            cu_new = [L.odb_name for L in layers if L.kind == "copper"]
            cov = coverage.compute(b.job_dir, b.step_dir, cu_new,
                                   (b.step_dir / "profile").read_text(encoding="latin-1"),
                                   float(ccfg.get("resolution_mil", 1.0)), extra,
                                   (job.info.get("UNITS") or "INCH").upper(),
                                   out_dir / "coverage_preview" if ccfg.get("preview_png", True) else None,
                                   int(ccfg.get("workers", 3)), log)
            use = ccfg.get("region_for_outputs", "profile")
            if use not in regions:
                raise ToolError(f"coverage.region_for_outputs {use!r} not in {regions}")
            for L in layers:
                if L.kind == "copper":
                    r = cov[L.odb_name.lower()]["regions"]
                    L.coverage_region = {k: (v["coverage"] if v else None) for k, v in r.items()}
                    L.coverage = L.coverage_region.get(use)

        log("[5/6] writing CSV files and Mechanical script ...")
        stem = f"{proj}_Stackup_{vendor}_workinggerber"
        wg = out_dir / f"{stem}.csv"
        outputs.write_workinggerber_csv(wg, layers)
        lm = out_dir / "layer_map.csv"
        outputs.write_layer_map(lm, layers)
        out_files = [(tgz.name, "ANSYS-ready ODB++ (Workbench External Data / SpaceClaim / EDB)"),
                     (wg.name, "LayerBuilder input (Layer Name, Thickness um, Copper Ratio)"),
                     (lm.name, "layer-by-layer mapping between all sources"),
                     ("run.log", "full console log"), ("verification_report.md", "this report")]
        tpl = cfg["options"].get("mechanical_script_template")
        lib = cfg["inputs"].get("material_library", {}).get("path")
        if tpl and lib:
            bases = []
            for L in layers:
                base = intake.material_choice.get(L.material)
                if base and base not in bases:
                    bases.append(base)
            ms = outputs.write_mechanical_script(Path(tpl), out_dir / "mechanical", matlib.load(Path(lib)), bases)
            out_files.append((f"mechanical/{ms.name}", "step 6: v6 equivalent-material script with the library "
                                                       f"materials of this board embedded ({', '.join(bases)})"))
        if cov and cfg["options"].get("coverage", {}).get("preview_png", True):
            out_files.append(("coverage_preview/", "one PNG per copper layer (white = copper)"))

        log("[6/6] ANSYS translator check ...")
        vwork = work / "verify"
        vwork.mkdir(parents=True, exist_ok=True)
        local_tgz = vwork / tgz.name
        shutil.copy2(tgz, local_tgz)          # translator unpacks next to its input: keep that off OneDrive
        vres = []
        for ver in cfg["options"].get("ansys_versions", ["v251", "v261"]):
            try:
                vres.append(verify.check(ver, local_tgz, layers, vwork, out_dir, log))
            except FileNotFoundError as e:
                vr = verify.VersionResult(ver, False, str(e))
                vres.append(vr)
                log(f"  {ver}: {e}")
        for lf in out_dir.glob("translate_*.log"):
            out_files.append((lf.name, "translator log"))

        same = {role: sha256(p) == h for role, (p, h) in hashes.items()}
        checks = []
        for v in vres:
            checks.append((f"translator {v.version}: 0 errors", v.summary.startswith("Total Errors: 0"), v.summary))
            checks.append((f"{v.version}: layer names, types, thickness (+-{verify.TOL_MIL} mil)",
                           v.mismatches == 0 and bool(v.rows), f"{v.mismatches} mismatches"))
            checks.append((f"{v.version}: total thickness", abs(v.total_edb - v.total_ref) <= verify.TOL_MIL,
                           f"{v.total_edb:.3f} vs {v.total_ref:.3f} mil"))
        n_cu = sum(1 for L in layers if L.kind == "copper")
        checks.append(("layer count", len(layers) == 2 * n_cu - 1, f"{n_cu} copper + {len(layers) - n_cu} dielectric"))
        x0, y0 = b.profile_after_in[0], b.profile_after_in[1]
        mode = cfg["options"].get("origin", {}).get("mode", "profile_lower_left")
        if mode == "profile_lower_left":
            checks.append(("profile lower-left at (0,0)", abs(x0) < 1e-6 and abs(y0) < 1e-6,
                           f"({x0:.6f}, {y0:.6f}) in"))
        checks.append(("vendor input files unchanged", all(same.values()), ", ".join(f"{k}" for k in same)))
        overall = all(c[1] for c in checks)
        report.write(out_dir / "verification_report.md", {
            "overall_ok": overall, "project": proj, "vendor": vendor, "run_name": run_name,
            "tool_version": __version__, "config_path": config_path.name, "checks": checks,
            "inputs": [(r, _rel(p, config_path.parent), same[r]) for r, (p, _) in hashes.items()],
            "notes": intake.notes + b.notes, "answers": asker.answers, "layers": layers, "build": b,
            "step": job.step_dirs and b.step_dir.name, "coverage": cov,
            "coverage_res": cfg["options"].get("coverage", {}).get("resolution_mil", 1.0),
            "coverage_regions": regions,
            "coverage_region_for_outputs": cfg["options"].get("coverage", {}).get("region_for_outputs", "profile"),
            "verify": vres, "outputs": out_files})
        for lvl, t in b.notes:
            log(f"  {lvl}: {t}")
        log("")
        log(f"RESULT: {'PASS' if overall else 'FAIL'}  ->  {out_dir}")
        return EXIT_OK if overall else EXIT_FAIL
    except NeedAnswer as e:
        qfile = config_path.parent / f"open_questions_{proj}_{vendor}.md"
        asker.write_pending(qfile)
        save_answers(config_path, asker.answers)
        log(f"STOPPED during build: {e}. See {qfile}")
        return EXIT_QUESTION
    except ToolError as e:
        log(f"ERROR: {e}")
        return EXIT_INPUT
    except Exception:                                    # noqa: BLE001
        import traceback
        log("INTERNAL ERROR (please report with run.log):")
        log(traceback.format_exc())
        return EXIT_FAIL
    finally:
        if not cfg["options"].get("keep_work_dir", False):
            shutil.rmtree(work, ignore_errors=True)


def reverify(run_dir: Path, versions=("v251", "v261")) -> int:
    """Re-run only the translator check of an existing run (e.g. after a licence outage)."""
    import csv
    from .intake import Layer
    run_dir = Path(run_dir).resolve()
    tgzs = list(run_dir.glob("*.tgz"))
    lm = run_dir / "layer_map.csv"
    if len(tgzs) != 1 or not lm.exists():
        print(f"INPUT ERROR: {run_dir} must contain one .tgz and layer_map.csv")
        return EXIT_INPUT
    layers = []
    with open(lm, encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            L = Layer(seq=int(r["seq"]), kind=r["kind"], thickness_mil=float(r["thickness_mil"]),
                      material=r["material"])
            layers.append(L)
    stamp = timestamp()
    log = Log(run_dir / f"reverify_{stamp}.log")
    work = Path(tempfile.gettempdir()) / "pcb_thermal_warpage" / f"reverify_{stamp}"
    work.mkdir(parents=True, exist_ok=True)
    try:
        local = work / tgzs[0].name
        shutil.copy2(tgzs[0], local)
        logs = run_dir / f"reverify_{stamp}"
        logs.mkdir()
        res = [verify.check(v, local, layers, work, logs, log) for v in versions]
    finally:
        shutil.rmtree(work, ignore_errors=True)
    ok = all(r.ok for r in res)
    lines = [f"# Re-verification {stamp} of `{tgzs[0].name}`", "",
             f"Result: **{'PASS' if ok else 'FAIL'}** (replaces the translator part of verification_report.md)", "",
             "| Version | Summary | EDB total mil | Stackup total mil | Mismatches | Result |", "|---|---|---|---|---|---|"]
    for r in res:
        lines.append(f"| {r.version} | {r.summary} | {r.total_edb:.3f} | {r.total_ref:.3f} | {r.mismatches} | "
                     f"{'PASS' if r.ok else 'FAIL'} |")
    (run_dir / f"reverification_{stamp}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"RESULT: {'PASS' if ok else 'FAIL'} -> reverification_{stamp}.md")
    return EXIT_OK if ok else EXIT_FAIL


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("usage: run_odb_tool.py <project.json> [--non-interactive] [--intake-only]\n"
              "       run_odb_tool.py --reverify <run folder>")
        return EXIT_INPUT
    if argv[0] == "--reverify":
        return reverify(Path(argv[1]))
    inter = False if "--non-interactive" in argv else None
    return run(Path([a for a in argv if not a.startswith("--")][0]), inter, "--intake-only" in argv)
