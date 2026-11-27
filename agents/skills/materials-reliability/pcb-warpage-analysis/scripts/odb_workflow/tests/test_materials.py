"""Material chain: workbook -> XML (converter) -> subset in the v6 script -> values used for mixing."""
import importlib.util
import sys
from pathlib import Path

import openpyxl
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from odbtool import matlib, outputs  # noqa: E402
from odbtool.util import ToolError  # noqa: E402


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


conv = _load(ROOT / "3_materials" / "Update_PCB_Material_Library.py", "matconv")
V6 = ROOT / "1_Scripts" / "Mech_py_EquivalentMaterial_v6.py"
HEAD = ["Vendor", "Model Name", "Vendor + Model Name", "Model Name + Axis", "Vendor + Model Name + Tg", "Resin Content",
        "Glass Fiber", "Items", "Unit", "Axis", "Temperature", "Value", "WB Value", "Remark", "Reference"]


def _row(model, item, unit, axis, T, val, rc=None, vendor="V"):
    return [vendor, model, None, None, None, rc, None, item, unit, axis, T, val, None, None, None]


def _full(model, rc=None, t0=30, cte_t0=30, e_axes=("X", "Y"), young=True):
    rows = [_row(model, "Poiison's Ratio", "mm/mm", None, 25, 0.15, rc), _row(model, "Density", "kg/m^3", None, 25, 1500, rc)]
    if young:
        rows.append(_row(model, "Young's Modulus", "MPa", None, 25, 21000, rc))
    for ax in e_axes:
        for T, v in ((t0, 20000), (150, 15000), (250, 5000)):
            rows.append(_row(model, "Storage Modulus", "MPa", ax, T, v + (500 if ax == "Y" else 0), rc))
    for ax, base in (("X", 12), ("Y", 13), ("Z", 40)):
        for T, v in ((cte_t0, base), (150, base + 2), (260, base * 4)):
            rows.append(_row(model, "CTE", "ppm/C", ax, T, v, rc))
    return rows


def _book(tmp, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Table"
    ws.append(HEAD)
    for r in rows:
        ws.append(r)
    p = tmp / "lib.xlsx"
    wb.save(p)
    return p


@pytest.fixture()
def library(tmp_path):
    rows = (_full("AB-100(Z)", 0.51) + _full("AB-100(Z)", 0.6) + _full("CD-200", None, e_axes=("",))
            + _full("LATE-E", None, t0=50, young=False)            # E from 50 C, no Young's -> copied to 30 C
            + _full("LATE-CTE", None, cte_t0=80)                    # CTE from 80 C -> incomplete
            + [r for r in _full("NO-NU") if not r[7].startswith("Poi")]
            + _full("BAD-UNIT") + [_row("BAD-UNIT", "Density", "lb/ft3", None, 25, 90)]
            + _full("TWICE") + [_row("TWICE", "CTE", "ppm/C", "Z", 150, 99)])
    res = conv.convert(str(_book(tmp_path, rows)))
    return tmp_path, res


def test_converter_includes_and_excludes(library):
    tmp, res = library
    assert [m["base"] for m in res["included"]] == ["AB-100(Z)_RC51", "AB-100(Z)_RC60", "CD-200_RCNA", "LATE-E_RCNA"]
    why = {m["base"]: " | ".join(m["problems"]) for m in res["excluded"]}
    assert "CTE X starts at 80 C" in why["LATE-CTE_RCNA"]
    assert "Poisson's Ratio is missing" in why["NO-NU_RCNA"]
    assert "unit 'lb/ft3'" in why["BAD-UNIT_RCNA"]
    assert "two different values" in why["TWICE_RCNA"]
    rep = (tmp / "PCB_Material_Library_report.md").read_text(encoding="utf-8")
    assert "LATE-CTE_RCNA" in rep and "copied to 30 C" in rep
    assert (tmp / "PCB_Material_Library.xml").read_bytes().isascii()


def test_converter_is_repeatable_and_archives(library):
    tmp, res = library
    wb = tmp / "lib.xlsx"
    again = conv.convert(str(wb))
    assert again["state"].startswith("no change") and not (tmp / "archive").exists()
    book = openpyxl.load_workbook(wb)
    book["Table"].append(_row("CD-200", "Thermal Conductivity", "W/m-K", None, 25, 0.7))
    book.save(wb)
    third = conv.convert(str(wb))
    assert third["state"].startswith("updated") and len(list((tmp / "archive").glob("*.xml"))) == 1
    assert third["sha"] != res["sha"]


def test_v6_reads_the_library_with_the_agreed_rules(library):
    tmp, _ = library
    v6 = _load(V6, "v6a")
    v6.MATERIAL_XML = str(tmp / "PCB_Material_Library.xml")
    with pytest.raises(Exception, match="several materials for AB100Z"):
        v6.load_library()
    v6.MATERIAL_CHOICE = {"AB100Z": "AB-100(Z)_RC51"}
    fr4, order, cu, _ = v6.load_library()
    assert order == ["AB100Z", "CD200", "LATEE"]
    assert (cu["e"], cu["nu"], cu["dens"], cu["k"], cu["cp"]) == (110000.0, 0.34, 8960.0, 400.0, 380.0)
    assert cu["cte"] == pytest.approx(17e-6)
    a = fr4["AB100Z"]
    i25, i30 = a["T"].index(25.0), a["T"].index(30.0)
    assert a["ex"][i25] == pytest.approx(21000) and a["ey"][i25] == pytest.approx(21000)     # Young's point
    assert a["ex"][i30] == pytest.approx(20000) and a["ey"][i30] == pytest.approx(20500)     # Ex != Ey
    assert a["ez"][i30] == pytest.approx(0.6 * 20250)
    assert a["gxy"][i30] == pytest.approx(20250 / 2.3) and a["gyz"][i30] == pytest.approx(0.6 * 20250 / 2.3)
    assert a["cx"][i30] == pytest.approx(12e-6) and a["cy"][i30] == pytest.approx(13e-6)
    assert a["T"][-1] == 260 and a["ex"][-1] == pytest.approx(5000)                          # E held above 250 C
    assert (a["k"], a["cp"], a["dens"]) == (0.59, 1100.0, 1500.0)
    c = fr4["CD200"]                                                                          # one in-plane set
    assert c["ex"] == c["ey"]
    late = fr4["LATEE"]
    assert late["T"][0] == 30 and late["ex"][0] == pytest.approx(20000)                      # 50 C value copied
    v6.FR4_MODEL = "ISO"
    iso = v6.load_library()[0]["AB100Z"]
    assert iso["name"].endswith("_Iso")
    assert iso["ex"][i30] == iso["ez"][i30] == pytest.approx(20250)
    assert iso["cz"][i30] == pytest.approx(40e-6)                                             # CTE stays orthotropic


def test_mixing_is_the_volume_rule_and_turner_is_optional(library):
    tmp, _ = library
    v6 = _load(V6, "v6b")
    v6.MATERIAL_XML = str(tmp / "PCB_Material_Library.xml")
    v6.MATERIAL_CHOICE = {"AB100Z": "AB-100(Z)_RC51"}
    fr4, order, cu, _ = v6.load_library()
    f = fr4["AB100Z"]
    i = f["T"].index(30.0)
    p = dict(zip(v6.LABELS, v6.get_inst_properties(i, 0.5, f, cu)))
    assert p["EX"] == pytest.approx(0.5 * 110000 + 0.5 * 20000) and p["EY"] == pytest.approx(0.5 * 110000 + 0.5 * 20500)
    assert p["CTEX"] == pytest.approx(0.5 * 17e-6 + 0.5 * 12e-6)
    assert p["GXY"] == pytest.approx(0.5 * 110000 / 2.68 + 0.5 * 20250 / 2.3)
    assert dict(zip(v6.LABELS, v6.get_inst_properties(i, 0.0, f, cu)))["EZ"] == pytest.approx(f["ez"][i])
    v6.METHOD_CTE_XY = "TURNER"
    t = dict(zip(v6.LABELS, v6.get_inst_properties(i, 0.5, f, cu)))
    assert t["CTEX"] == pytest.approx((17e-6 * 110000 + 12e-6 * 20000) / (110000 + 20000))
    apdl, bad = v6.material_apdl(fr4, order, ["AB100Z"], cu, v6.UNIT_TABLE["MM_TONNE_N_S"], "T")
    assert bad == 0 and sum(1 for l in apdl if l.startswith("MP,DENS")) == v6.NUM_BINS
    assert v6.frac_bin(0.005) == 1 and v6.frac_bin(0.0049) == 0 and v6.frac_bin(1.0) == 100


def test_tool_embeds_only_the_materials_of_the_board(library, tmp_path):
    tmp, _ = library
    lib = matlib.load(tmp / "PCB_Material_Library.xml")
    assert lib.by_key["AB100Z"] == ["AB-100(Z)_RC51", "AB-100(Z)_RC60"] and "LATECTE" not in lib.keys
    assert "left out of the XML" in matlib.why_missing(lib, "LATE-CTE") and "CTE X starts" in matlib.why_missing(lib, "LATE-CTE")
    assert "not in the workbook" in matlib.why_missing(lib, "UNKNOWN-9")
    out = outputs.write_mechanical_script(V6, tmp_path / "mech", lib, ["CD-200_RCNA", "AB-100(Z)_RC60"])
    text = out.read_text(encoding="utf-8")
    assert text.isascii() and "AB-100(Z)_RC51" not in text and "sha256 " + lib.sha[:12] in text
    v6 = _load(out, "v6c")
    fr4, order, cu, source = v6.load_library()
    assert order == ["CD200", "AB100Z"] and fr4["AB100Z"]["base"] == "AB-100(Z)_RC60" and source.startswith("embedded")
    assert v6.parse_layer_name("Layer_53_AB100Z_0.296") == (53, "AB100Z")
    assert v6.parse_layer_name("Layer_2_CD200_0.000") == (2, "CD200") and v6.parse_layer_name("Solid") == (None, None)
    with pytest.raises(ToolError, match="PCB_Material_Library.xml"):
        matlib.load(tmp / "lib.xlsx")
    with pytest.raises(Exception, match="template of the tool folder"):
        _load(V6, "v6d").load_library()
