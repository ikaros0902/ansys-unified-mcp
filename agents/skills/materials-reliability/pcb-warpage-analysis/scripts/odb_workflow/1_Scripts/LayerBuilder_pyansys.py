# -*- coding: utf-8 -*-
"""Step 3 - LayerBuilder (PyAnsys Geometry): stacked 3D PCB from the 2D board drawing.

The planar face of the STEP file is extruded once per row of the stackup CSV written by
run_odb_tool.py (<project>_Stackup_<vendor>_workinggerber.csv: Layer Name, Thickness um, Copper
Ratio). Row 1 is the TOP layer (highest Z); the last row sits on the original face. Every body
is named  <Layer Name>_<Copper Ratio>  (e.g. Layer_1_EM892K2_0.296) - the Mechanical v5 script
reads the layer number from this name, so do not rename bodies. The original face is deleted,
Share Topology is set on the stack component and a .scdocx is saved.

How to use
  All settings live in the "layerbuilder" section of the project JSON
  (see 4_config/project_config.template.json). Then either
      python LayerBuilder_pyansys.py <project.json>
  or set CONFIG_FILE below and press Run in VS Code.
  Needs an ANSYS Geometry service (Discovery / SpaceClaim licence) on this PC.

Exit codes: 0 done, 1 failed while building, 3 input error.
"""
import json
import os
import sys
import time
from pathlib import Path

# ----------------------------------------------------------------------------------------
CONFIG_FILE = r""          # e.g. r"C:\Projects\TH5\TH5_SYE.json"  ("" = use the command line)
# ----------------------------------------------------------------------------------------

TOOL_ROOT = Path(__file__).resolve().parent.parent
NORMAL_TOLERANCE = 1e-3    # allowed deviation of the start-face normal from the Z axis
EXIT_OK, EXIT_FAIL, EXIT_INPUT = 0, 1, 3


class InputError(Exception):
    pass


def resolve_settings(config_path: Path) -> dict:
    """Project JSON -> stackup CSV, STEP file, output file (all absolute)."""
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    base = config_path.parent
    lb = cfg.get("layerbuilder") or {}

    def fix(p):
        p = str(p).replace("{tool}", str(TOOL_ROOT))
        q = Path(os.path.expandvars(p))
        return q if q.is_absolute() else (base / q).resolve()

    csv_p = lb.get("stackup_csv")
    if csv_p:
        csv_p = fix(csv_p)
    else:                                              # newest run folder that has a workinggerber CSV
        root = fix((cfg.get("output") or {}).get("root") or "runs")
        cands = sorted(root.glob("*/*_workinggerber.csv"), key=lambda p: p.parent.name)
        if not cands:
            raise InputError(f"no *_workinggerber.csv in any run folder under {root}. Run step 2 "
                             f"(run_odb_tool.py) first or set layerbuilder.stackup_csv.")
        csv_p = cands[-1]
        rep = csv_p.parent / "verification_report.md"
        if not rep.is_file() or "Result: **PASS**" not in rep.read_text(encoding="utf-8", errors="replace"):
            raise InputError(f"the newest run {csv_p.parent.name} has no PASS verification report. "
                             f"Fix step 2 first, or set layerbuilder.stackup_csv to the run you want.")
    stp = lb.get("step_file") or ((cfg.get("inputs") or {}).get("step_2d_drawing") or {}).get("path")
    if not stp:
        raise InputError("no 2D drawing: set inputs.step_2d_drawing.path or layerbuilder.step_file")
    proj = cfg.get("project") or {}
    out = lb.get("output_scdocx") or f"geometry/{proj.get('name', 'PCB')}_{proj.get('vendor', '')}_Stackup.scdocx"
    return {"csv": Path(csv_p), "step": fix(stp), "out": fix(out),
            "component": lb.get("component_name") or "Stackup",
            "open_folder": bool(lb.get("open_folder_when_done", False))}


def load_stackup(csv_path: Path) -> list:
    """-> [(body name, thickness um), ...] top layer first."""
    import pandas as pd
    df = pd.read_csv(str(csv_path), sep=None, engine="python", encoding="utf-8-sig").dropna(how="all")
    if df.shape[1] < 3:
        raise InputError(f"{csv_path.name}: needs 3 columns (name, thickness um, copper ratio), has {df.shape[1]}")
    layers = []
    for row_no, row in enumerate(df.itertuples(index=False), start=2):
        name = str(row[0]).strip()
        try:
            thick_um, ratio = float(row[1]), float(row[2])
        except (TypeError, ValueError):
            raise InputError(f"{csv_path.name} row {row_no}: not numeric: {tuple(row)[:3]}")
        if thick_um <= 0:
            raise InputError(f"{csv_path.name} row {row_no}: thickness must be > 0, is {thick_um}")
        layers.append((f"{name}_{ratio}", thick_um))
    if not layers:
        raise InputError(f"{csv_path.name}: no layer rows")
    return layers


def collect_bodies(comp, out: list) -> list:
    out.extend(getattr(comp, "bodies", []))
    for c in getattr(comp, "components", []):
        collect_bodies(c, out)
    return out


def build(s: dict) -> int:
    from ansys.geometry.core import launch_modeler
    from ansys.geometry.core.designer import DesignFileFormat, SharedTopologyType
    from ansys.geometry.core.math import UnitVector3D
    from ansys.geometry.core.misc import UNITS, Distance

    z_up, z_down = UnitVector3D([0, 0, 1]), UnitVector3D([0, 0, -1])
    layers = load_stackup(s["csv"])
    total_um = sum(t for _, t in layers)
    print(f"stackup : {s['csv']}")
    print(f"drawing : {s['step']}")
    print(f"output  : {s['out']}")
    print(f"layers  : {len(layers)}, total {total_um:.3f} um = {total_um / 1000:.4f} mm")
    modeler = None
    t0 = time.time()
    try:
        print("starting the ANSYS Geometry service ...")
        modeler = launch_modeler()
        design = modeler.open_file(str(s["step"]))
        bodies = collect_bodies(design, [])
        if not bodies or not bodies[0].faces:
            raise RuntimeError("no start face found: the STEP file must contain one planar surface")
        base_body = bodies[0]
        base_face = base_body.faces[0]
        n = base_face.normal()
        if abs(abs(n.z) - 1.0) > NORMAL_TOLERANCE:
            raise RuntimeError(f"the start face is not horizontal (normal {n.x:.4f}, {n.y:.4f}, {n.z:.4f})")
        bb = base_body.bounding_box
        x0, y0 = bb.min_corner.x.m_as("mm"), bb.min_corner.y.m_as("mm")
        x1, y1 = bb.max_corner.x.m_as("mm"), bb.max_corner.y.m_as("mm")
        print(f"start face '{base_body.name}': X {x0:.3f} .. {x1:.3f} mm, Y {y0:.3f} .. {y1:.3f} mm")
        if abs(x0) > 1e-3 or abs(y0) > 1e-3:
            print(f"WARNING: the start face begins at ({x0:.3f}, {y0:.3f}) mm, not at (0, 0). The ODB++ of step 2 "
                  f"has the board outline corner at (0, 0). This is fine when the face is simply smaller than the "
                  f"outline rectangle (cut-outs, an edge that is set back); it is wrong when the drawing uses another "
                  f"origin. A human must confirm which it is before step 4.")
        base_z = bb.min_corner.z.m_as("m")
        stack = design.add_component(s["component"])        # Share Topology cannot be set on the design root
        top_z = base_z + total_um * 1e-6
        for i, (name, thick_um) in enumerate(layers, start=1):
            thick_m = thick_um * 1e-6
            bottom_z = top_z - thick_m
            body = stack.extrude_face(name=name, face=base_face, distance=Distance(thick_m, UNITS.m))
            offset = bottom_z - body.bounding_box.min_corner.z.m_as("m")
            if abs(offset) > 1e-12:
                stack.translate_bodies(bodies=[body], direction=z_up if offset > 0 else z_down,
                                       distance=Distance(abs(offset), UNITS.m))
            if i == 1 or i == len(layers) or i % 10 == 0:
                print(f"  [{i}/{len(layers)}] {name}  {thick_um} um")
            top_z = bottom_z
        base_body.parent_component.delete_body(base_body)
        try:
            stack.set_shared_topology(SharedTopologyType.SHARETYPE_SHARE)
            print(f"Share Topology on '{stack.name}': {stack.shared_topology.name}")
        except Exception as e:                                  # noqa: BLE001
            print(f"WARNING: Share Topology could not be set ({e}). Set it by hand in SpaceClaim.")
        s["out"].parent.mkdir(parents=True, exist_ok=True)
        design.download(s["out"], DesignFileFormat.SCDOCX)
        if not s["out"].is_file() or s["out"].stat().st_size == 0:
            raise RuntimeError(f"export failed: {s['out']} is missing or empty")
        print(f"RESULT: DONE  {len(layers)} bodies, total {total_um / 1000:.4f} mm, "
              f"{s['out'].stat().st_size / 1024:.0f} KB, {time.time() - t0:.0f} s")
        print(f"         {s['out']}")
        if s["open_folder"]:
            os.startfile(s["out"].parent)
        return EXIT_OK
    except Exception as e:                                      # noqa: BLE001
        print(f"ERROR: {type(e).__name__}: {e}")
        return EXIT_FAIL
    finally:
        if modeler:
            try:
                modeler.close()
            except Exception:                                   # noqa: BLE001
                pass


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv and CONFIG_FILE:
        argv = [CONFIG_FILE]
    if not argv:
        print("usage: LayerBuilder_pyansys.py <project.json>")
        return EXIT_INPUT
    try:
        cfg_path = Path(argv[0]).resolve()
        if not cfg_path.is_file():
            raise InputError(f"project JSON not found: {cfg_path}")
        s = resolve_settings(cfg_path)
        for key in ("csv", "step"):
            if not s[key].is_file():
                raise InputError(f"file not found: {s[key]}")
        if s["out"].exists():
            raise InputError(f"output exists and is never overwritten: {s['out']}. Rename or move it, "
                             f"or set layerbuilder.output_scdocx.")
        if "--check" in argv:                                   # resolve and validate only, no ANSYS
            layers = load_stackup(s["csv"])
            print(f"stackup : {s['csv']}\ndrawing : {s['step']}\noutput  : {s['out']}")
            print(f"CHECK OK: {len(layers)} layers, total {sum(t for _, t in layers) / 1000:.4f} mm")
            return EXIT_OK
    except InputError as e:
        print(f"INPUT ERROR: {e}")
        return EXIT_INPUT
    except (OSError, json.JSONDecodeError) as e:
        print(f"INPUT ERROR: {type(e).__name__}: {e}")
        return EXIT_INPUT
    try:
        return build(s)
    except InputError as e:
        print(f"INPUT ERROR: {e}")
        return EXIT_INPUT


if __name__ == "__main__":
    sys.exit(main())
