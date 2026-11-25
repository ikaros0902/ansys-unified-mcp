#!/usr/bin/env python
"""以 OCCT 嘗試抽取等厚直擠平板的中面。"""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import tempfile
from pathlib import Path

import OCP
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepGProp import BRepGProp
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.GProp import GProp_GProps
from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Plane
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Reader, STEPControl_Writer
from OCP.TColStd import TColStd_SequenceOfAsciiString
from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Trsf, gp_Vec


def subshapes(shape, kind):
    explorer = TopExp_Explorer(shape, kind)
    values = []
    while explorer.More():
        values.append(explorer.Current())
        explorer.Next()
    return values


def measure(shape, surface=False):
    props = GProp_GProps()
    if surface:
        BRepGProp.SurfaceProperties_s(shape, props)
    else:
        BRepGProp.VolumeProperties_s(shape, props)
    return abs(props.Mass())


def translate(shape, vector):
    transform = gp_Trsf()
    transform.SetTranslation(vector)
    operation = BRepBuilderAPI_Transform(shape, transform, True)
    if not operation.IsDone():
        raise RuntimeError("幾何平移失敗")
    return operation.Shape()


def boolean_shape(operation, left, right):
    result = operation(left, right)
    result.Build()
    if not result.IsDone():
        raise RuntimeError("幾何布林運算失敗")
    return result.Shape()


def distance(left, right):
    operation = BRepExtrema_DistShapeShape(left, right)
    operation.Perform()
    if not operation.IsDone():
        raise RuntimeError("幾何距離計算失敗")
    return operation.Value()


class OcctGeometry:
    """集中處理 OCCT 幾何讀取、量測與 STEP 輸出。"""

    def read(self, path):
        reader = STEPControl_Reader()
        if reader.ReadFile(str(path)) != IFSelect_RetDone:
            raise ValueError("無法讀取 STEP")
        lengths, angles, solid_angles = (TColStd_SequenceOfAsciiString() for _ in range(3))
        reader.FileUnits(lengths, angles, solid_angles)
        units = [lengths.Value(i).ToCString() for i in range(1, lengths.Length() + 1)]
        if len(set(units)) != 1:
            raise ValueError("STEP 長度單位缺失或不一致")
        reader.SetSystemLengthUnit(1.0)
        if reader.TransferRoots() < 1:
            raise ValueError("STEP 未包含可轉換的幾何")
        shape = reader.OneShape()
        if shape.IsNull() or not BRepCheck_Analyzer(shape).IsValid():
            raise ValueError("STEP 幾何無效")
        return shape, units

    def write_new(self, shape, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp = tempfile.mkstemp(suffix=".step", dir=path.parent)
        os.close(fd)
        try:
            writer = STEPControl_Writer()
            if writer.Transfer(shape, STEPControl_AsIs) != IFSelect_RetDone:
                raise RuntimeError("STEP 轉換失敗")
            if writer.Write(temp) != IFSelect_RetDone:
                raise RuntimeError("STEP 寫入失敗")
            check, _ = self.read(Path(temp))
            if len(subshapes(check, TopAbs_FACE)) != 1:
                raise RuntimeError("輸出 STEP 回讀後面數不符")
            with open(temp, "rb") as source, path.open("xb") as destination:
                try:
                    shutil.copyfileobj(source, destination)
                except OSError:
                    destination.close()
                    path.unlink()
                    raise
        finally:
            os.unlink(temp)


def inspect_bends(faces):
    """列出圓柱面幾何，供折彎候選的保守判讀。"""
    cylinders = []
    for index, face in enumerate(faces):
        surface = BRepAdaptor_Surface(face)
        if surface.GetType() != GeomAbs_Cylinder:
            continue
        cylinder = surface.Cylinder()
        axis = cylinder.Axis()
        point, direction = axis.Location(), axis.Direction()
        cylinders.append({"face": index, "radius_mm": cylinder.Radius(),
                          "axis_point_mm": [point.X(), point.Y(), point.Z()],
                          "axis_direction": [direction.X(), direction.Y(), direction.Z()]})
    pairs = []
    for i, a in enumerate(cylinders):
        for b in cylinders[i + 1:]:
            u, v = a["axis_direction"], b["axis_direction"]
            dot = sum(x * y for x, y in zip(u, v))
            if abs(dot) < 1 - 1e-7:
                continue
            delta = [y - x for x, y in zip(a["axis_point_mm"], b["axis_point_mm"])]
            projection = sum(x * y for x, y in zip(delta, u))
            axis_distance = math.sqrt(sum((x - projection * y) ** 2 for x, y in zip(delta, u)))
            pairs.append({"faces": [a["face"], b["face"]], "axis_distance_mm": axis_distance,
                          "radius_difference_mm": abs(a["radius_mm"] - b["radius_mm"])})
    return cylinders, pairs


def extract(shape, tolerance):
    """只接受可由單一平面輪廓直擠還原的封閉實體。"""
    solids = subshapes(shape, TopAbs_SOLID)
    faces = [TopoDS.Face_s(f) for f in subshapes(shape, TopAbs_FACE)]
    cylinders, cylinder_pairs = inspect_bends(faces)
    report = {"status": "unsupported", "thickness_mm": None, "face_count": len(faces),
              "solid_count": len(solids), "cylinders": cylinders, "parallel_cylinder_pairs": cylinder_pairs,
              "parallel_planar_candidates": [], "handled_features": [], "unresolved_features": [],
              "warnings": [], "validation": {}}
    if len(solids) != 1:
        report["unresolved_features"].append("僅支援單一封閉實體")
        return None, report
    solid = solids[0]
    volume = measure(solid)
    candidates = []
    for i, first in enumerate(faces):
        a = BRepAdaptor_Surface(first)
        if a.GetType() != GeomAbs_Plane:
            continue
        area = measure(first, True)
        normal = a.Plane().Axis().Direction()
        origin = a.Plane().Location()
        for j, second in enumerate(faces[i + 1:], start=i + 1):
            b = BRepAdaptor_Surface(second)
            if b.GetType() != GeomAbs_Plane:
                continue
            other = b.Plane().Axis().Direction()
            if abs(normal.Dot(other)) < 1 - 1e-8:
                continue
            p = b.Plane().Location()
            delta = gp_Vec(origin, p).Dot(gp_Vec(normal))
            thickness = abs(delta)
            if thickness <= tolerance or math.sqrt(area) / thickness < 5:
                continue
            other_area = measure(second, True)
            report["parallel_planar_candidates"].append(
                {"faces": [i, j], "plane_distance_mm": thickness,
                 "areas_mm2": [area, other_area], "note": "平面距離不代表已確認板厚"})
            if abs(area - other_area) > max(tolerance * math.sqrt(area) * 4, area * 1e-7):
                continue
            candidates.append((area, first, second, gp_Vec(normal).Multiplied(delta), thickness))
    candidates.sort(key=lambda item: item[0], reverse=True)
    for area, first, second, vector, thickness in candidates:
        try:
            shifted = translate(first, vector)
            common = boolean_shape(BRepAlgoAPI_Common, shifted, second)
            overlap_error = abs(area - measure(common, True))
            area_tol = max(tolerance * math.sqrt(area) * 4, area * 1e-7)
            if overlap_error > area_tol:
                continue
            prism = BRepPrimAPI_MakePrism(first, vector).Shape()
            missing = measure(boolean_shape(BRepAlgoAPI_Cut, solid, prism))
            extra = measure(boolean_shape(BRepAlgoAPI_Cut, prism, solid))
            volume_tol = max(area * tolerance * 2, volume * 1e-7)
            if missing + extra > volume_tol:
                continue
            mid = translate(first, vector.Multiplied(0.5))
            if not BRepCheck_Analyzer(mid).IsValid():
                continue
            d1, d2 = distance(mid, first), distance(mid, second)
            if max(abs(d1 - thickness / 2), abs(d2 - thickness / 2)) > tolerance:
                continue
            report.update(status="complete", thickness_mm=thickness,
                          handled_features=["單一等厚直擠平板", "原始輪廓與孔洞"],
                          validation={"surface_area_mm2": area, "overlap_area_error_mm2": overlap_error,
                                      "solid_missing_volume_mm3": missing, "solid_extra_volume_mm3": extra,
                                      "distance_to_skin_mm": [d1, d2], "connected_faces": 1,
                                      "method": "表皮重疊與實體直擠雙向差集"})
            return mid, report
        except RuntimeError as exc:
            report["warnings"].append(str(exc))
    report["unresolved_features"].append("未找到能以單一平面輪廓直擠驗證的薄壁；折彎與複雜成形不支援")
    if cylinders:
        report["warnings"].append("圓柱面可能是孔或折彎；尚未分類，未建立彎角候選中面")
    return None, report


def main(argv=None):
    parser = argparse.ArgumentParser(description="以 OCCT 抽取可驗證的等厚直擠平板中面")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--tolerance-mm", type=float, default=0.01)
    args = parser.parse_args(argv)
    paths = [args.input.resolve(), args.output.resolve(), args.report.resolve()]
    if len(set(paths)) != 3 or not math.isfinite(args.tolerance_mm) or args.tolerance_mm <= 0:
        parser.error("輸入、輸出及報告路徑必須不同，容差須為有限正數")
    if args.output.exists() or args.report.exists():
        parser.error("輸出或報告已存在，拒絕覆寫")
    report = {"engine": "Open CASCADE", "ocp_version": OCP.__version__, "working_unit": "mm",
              "input": str(args.input.resolve()), "tolerance_mm": args.tolerance_mm}
    exit_code = 1
    try:
        geometry = OcctGeometry()
        shape, units = geometry.read(args.input)
        report["source_length_units"] = units
        mid, result = extract(shape, args.tolerance_mm)
        report.update(result)
        if mid is not None:
            geometry.write_new(mid, args.output)
            report["output"] = str(args.output.resolve())
            exit_code = 0
        else:
            exit_code = 2
    except Exception as exc:
        report.update(status="error", error=f"{type(exc).__name__}: {exc}")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
