"""獨立 OCCT 中面原型的幾何行為測試。"""

import importlib.util
import json
import math
from pathlib import Path

import pytest

pytest.importorskip("OCP")
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
from OCP.TopAbs import TopAbs_FACE
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt


PATH = Path(__file__).resolve().parents[2] / "agents/skills/ansys-midsurface/scripts/occt_midsurface.py"
spec = importlib.util.spec_from_file_location("occt_midsurface", PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def plate(hole=False):
    shape = BRepPrimAPI_MakeBox(20, 20, 1).Shape()
    if hole:
        drill = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(10, 10, 0), gp_Dir(0, 0, 1)), 3, 1).Shape()
        shape = BRepAlgoAPI_Cut(shape, drill).Shape()
    return shape


@pytest.mark.parametrize("has_hole", [False, True])
def test_plate_midface_preserves_area_and_position(has_hole):
    mid, report = mod.extract(plate(has_hole), .001)
    assert report["status"] == "complete"
    assert report["thickness_mm"] == pytest.approx(1)
    assert report["validation"]["distance_to_skin_mm"] == pytest.approx([.5, .5])
    assert mod.measure(mid, True) == pytest.approx(400 - (math.pi * 9 if has_hole else 0))
    if has_hole:
        from OCP.TopAbs import TopAbs_EDGE
        from OCP.BRepAdaptor import BRepAdaptor_Curve
        from OCP.GeomAbs import GeomAbs_Circle
        from OCP.TopoDS import TopoDS
        curves = [BRepAdaptor_Curve(TopoDS.Edge_s(e)) for e in mod.subshapes(mid, TopAbs_EDGE)]
        circles = [c.Circle() for c in curves if c.GetType() == GeomAbs_Circle]
        assert len(circles) == 1
        assert circles[0].Radius() == pytest.approx(3)
        center = circles[0].Location()
        assert (center.X(), center.Y(), center.Z()) == pytest.approx((10, 10, .5))


def test_cube_and_stepped_plate_rejected():
    cube = BRepPrimAPI_MakeBox(2, 2, 2).Shape()
    assert mod.extract(cube, .001)[1]["status"] == "unsupported"
    recess = BRepPrimAPI_MakeBox(gp_Pnt(5, 5, .5), 5, 5, .5).Shape()
    stepped = BRepAlgoAPI_Cut(plate(), recess).Shape()
    assert mod.extract(stepped, .001)[1]["status"] == "unsupported"


def test_boolean_failure_is_reported(monkeypatch):
    def fail(*args):
        raise RuntimeError("測試布林失敗")

    monkeypatch.setattr(mod, "boolean_shape", fail)
    mid, report = mod.extract(plate(), .001)
    assert mid is None
    assert report["status"] == "unsupported"
    assert "測試布林失敗" in report["warnings"]


def test_step_roundtrip_and_no_overwrite(tmp_path):
    source, output, report = (tmp_path / n for n in ("source.step", "mid.step", "report.json"))
    writer = STEPControl_Writer()
    writer.Transfer(plate(True), STEPControl_AsIs)
    writer.Write(str(source))
    assert mod.main([str(source), "--output", str(output), "--report", str(report)]) == 0
    result = json.loads(report.read_text(encoding="utf-8"))
    assert result["status"] == "complete"
    reread, units = mod.OcctGeometry().read(output)
    assert len(mod.subshapes(reread, TopAbs_FACE)) == 1
    assert units
    before = output.read_bytes()
    with pytest.raises(SystemExit):
        mod.main([str(source), "--output", str(output), "--report", str(tmp_path / "other.json")])
    assert output.read_bytes() == before


def test_invalid_file_records_error(tmp_path):
    source = tmp_path / "bad.step"
    source.write_text("not a step", encoding="ascii")
    output, report = tmp_path / "out.step", tmp_path / "report.json"
    assert mod.main([str(source), "--output", str(output), "--report", str(report)]) == 1
    assert json.loads(report.read_text(encoding="utf-8"))["status"] == "error"
    assert not output.exists()


def test_unsupported_geometry_writes_report_without_step(tmp_path):
    source, output, report = (tmp_path / n for n in ("cube.step", "mid.step", "report.json"))
    writer = STEPControl_Writer()
    writer.Transfer(BRepPrimAPI_MakeBox(2, 2, 2).Shape(), STEPControl_AsIs)
    writer.Write(str(source))
    assert mod.main([str(source), "--output", str(output), "--report", str(report)]) == 2
    result = json.loads(report.read_text(encoding="utf-8"))
    assert result["status"] == "unsupported"
    assert result["unresolved_features"]
    assert not output.exists()


def test_inch_step_is_converted_to_millimetres(tmp_path):
    from OCP.Interface import Interface_Static

    writer = STEPControl_Writer()
    previous = Interface_Static.CVal_s("write.step.unit")
    try:
        assert Interface_Static.SetCVal_s("write.step.unit", "INCH")
        writer.Transfer(BRepPrimAPI_MakeBox(25.4, 25.4, 2.54).Shape(), STEPControl_AsIs)
        source = tmp_path / "inch.step"
        writer.Write(str(source))
    finally:
        Interface_Static.SetCVal_s("write.step.unit", previous)
    shape, units = mod.OcctGeometry().read(source)
    mid, report = mod.extract(shape, .001)
    assert "inch" in units[0].lower()
    assert report["status"] == "complete"
    assert report["thickness_mm"] == pytest.approx(2.54)
    assert mod.measure(mid, True) == pytest.approx(25.4 ** 2)
