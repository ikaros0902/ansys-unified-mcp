"""Files written for the next steps of the workflow.

  <name>_workinggerber.csv       LayerBuilder input: Layer Name, Thickness (um), Copper Ratio
                                 (UTF-8 with BOM, CRLF - same as the SYE/Founder files)
  layer_map.csv                  every layer: new name, vendor ODB++ name, sheet rows, thickness, coverage,
                                 copper weight, function / glass style
  mechanical/<v6 script>         v6 all-in-one script with the library materials of this board embedded
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

from . import matlib
from .intake import Layer
from .util import ToolError, UM_PER_MIL, fmt


def _write_csv(path: Path, header: list[str], rows: list[list], bom=True, crlf=True) -> None:
    with open(path, "w", encoding="utf-8-sig" if bom else "utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\r\n" if crlf else "\n")
        w.writerow(header)
        w.writerows(rows)


def remark(L: Layer) -> str:
    if L.kind == "copper":
        parts = []
        if L.func:
            parts.append(f"func={L.func}")
        if L.foil:
            parts.append(f"foil={L.foil}")
        return "; ".join(parts)
    return "; ".join(p for p in (L.diel_type, L.glass) if p)


def write_workinggerber_csv(path: Path, layers: list[Layer]) -> None:
    rows = []
    for L in layers:
        ratio = 0.0 if L.kind != "copper" else (L.coverage if L.coverage is not None else 0.5)
        rows.append([L.layer_name, fmt(L.thickness_mil * UM_PER_MIL, 3), f"{ratio:.3f}"])
    _write_csv(path, ["Layer Name", "Thickness (um)", "Copper Ratio"], rows)


def write_layer_map(path: Path, layers: list[Layer]) -> None:
    regions = sorted({k for L in layers for k in L.coverage_region})
    rows = []
    for L in layers:
        rows.append([L.seq, L.odb_name, L.layer_name, L.kind, L.diel_type, L.material, L.material_raw,
                     fmt(L.thickness_mil, 4), fmt(L.thickness_mil * UM_PER_MIL, 3), L.vendor_odb_name,
                     L.vendor_sheet_name, L.ecad_name, L.vendor_row, L.design_row,
                     "" if L.design_thickness_mil is None else fmt(L.design_thickness_mil, 4), L.copper_oz,
                     remark(L)]
                    + [("" if L.coverage_region.get(r) is None else f"{L.coverage_region[r]:.4f}") for r in regions])
    _write_csv(path, ["seq", "odb_layer", "layer_name", "kind", "dielectric_type", "material", "material_as_written",
                      "thickness_mil", "thickness_um", "vendor_odb_layer", "vendor_sheet_layer", "design_layer",
                      "vendor_sheet_rows", "design_sheet_rows", "design_thickness_mil", "copper_oz", "remark"]
               + [f"coverage_{r}" for r in regions], rows)


def write_mechanical_script(template: Path, out_dir: Path, lib: matlib.Library, bases: list[str]) -> Path:
    """Copy of the v6 script with the library materials of this board (and the copper) embedded.
    `bases` = library material names without _Ortho / _Iso, in stackup order."""
    out_dir.mkdir(parents=True, exist_ok=True)
    src = template.read_text(encoding="utf-8")
    xml = matlib.subset_xml(lib, bases).strip("\n")
    pat = re.compile(r"(# BEGIN EMBEDDED_MATERIAL_XML\n).*?(# END EMBEDDED_MATERIAL_XML\n)", re.S)
    if not pat.search(src):
        raise ToolError(f"marker EMBEDDED_MATERIAL_XML not found in {template.name}")
    src = pat.sub(lambda m: m.group(1) + f'EMBEDDED_MATERIAL_XML = """{xml}\n"""\n' + m.group(2), src, count=1)
    info = f"{lib.path.name} sha256 {lib.sha[:12]}; materials {', '.join(bases)}"
    src, n = re.subn(r'^LIBRARY_INFO = ".*"$', lambda m: f'LIBRARY_INFO = "{info}"', src, count=1, flags=re.M)
    if not n:
        raise ToolError(f"LIBRARY_INFO not found in {template.name}")
    out = out_dir / template.name
    out.write_text(src, encoding="utf-8", newline="\n")
    return out
