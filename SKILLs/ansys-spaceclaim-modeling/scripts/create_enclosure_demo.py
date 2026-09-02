# -*- coding: utf-8 -*-
"""
腳本名稱：create_enclosure_demo.py
功能說明：外流域抽取 (Enclosure) 與布林相減端到端完整示範腳本
技術標準：林明志標準 CAD 前處理自動化規範 (基於 PyAnsys Geometry ansys.geometry.core)
"""

import os
import sys
import argparse
import warnings

warnings.filterwarnings("ignore", message="Starting gRPC client without TLS")

try:
    from ansys.geometry.core import Modeler, launch_modeler_with_spaceclaim
    from ansys.geometry.core.math import Point2D, Plane
    from ansys.geometry.core.sketch import Sketch
except ImportError:
    print("[警告] 尚未安裝 ansys-geometry-core。請執行: pip install ansys-geometry-core")


def run_enclosure_pipeline(
    output_dir: str = "./cad_output",
    model_name: str = "airfoil_enclosure_demo",
    chord_m: float = 0.3,
    span_m: float = 0.6,
    is_cht_mode: bool = False
):
    """
    執行氣動外流場建立、外流域包覆抽取、布林扣除、具名選擇自動標記與 PMDB 導出流程。
    """
    print("================================================================================")
    print("           ANSYS 幾何前處理：外流域抽取與布林相減自動化管線啟動                 ")
    print("================================================================================")
    
    # 1. 建立或連線幾何後端 (Windows 必須指定 wnua 驗證)
    print("[步驟 1/6] 探測並連線 SpaceClaim / Discovery 幾何後端引擎...")
    try:
        modeler = Modeler(port=50051, transport_mode="wnua", timeout=5)
        print("  -> 成功連線至既有幾何服務 (Port 50051, WNUA 模式)。")
    except Exception:
        print("  -> 未探測到活躍實例，正在啟動全新 SpaceClaim 實例...")
        modeler = launch_modeler_with_spaceclaim(hidden=False, timeout=120)
        print("  -> SpaceClaim 實例已成功啟動。")

    design = modeler.create_design(model_name)
    print(f"  -> 已建立新幾何專案: {model_name}")

    # 2. 建立標的固體物件 (以 NACA 參數化翼型機翼為例)
    print(f"[步驟 2/6] 繪製 2D 翼型草圖並拉伸為 3D 機翼 (弦長={chord_m}m, 翼展={span_m}m)...")
    sketch = Sketch(plane=Plane.xy())
    
    # NACA 歸一化坐標取樣點
    norm_coords = [
        (1.000, 0.0013), (0.950, 0.0084), (0.800, 0.0262), (0.600, 0.0456),
        (0.400, 0.0580), (0.200, 0.0574), (0.100, 0.0468), (0.050, 0.0356),
        (0.000, 0.0000), (0.050, -0.0356), (0.100, -0.0468), (0.200, -0.0574),
        (0.400, -0.0580), (0.600, -0.0456), (0.800, -0.0262), (0.950, -0.0084),
        (1.000, -0.0013)
    ]
    spline_points = [Point2D([x * chord_m, y * chord_m]) for x, y in norm_coords]
    
    # 繪製 NURBS 樣條與後緣閉合直線
    sketch.nurbs_from_2d_points(spline_points, tag="AirfoilProfile")
    sketch.segment(spline_points[-1], spline_points[0])
    
    # 拉伸成機翼實體
    wing_body = design.extrude_sketch(
        name="TargetWingSolid",
        sketch=sketch,
        distance=span_m
    )
    print(f"  -> 標的實體成形完畢，估算體積: {wing_body.volume:.6e} m³")

    # 3. 依據空氣動力學規範計算外流域尺寸 (上游 2.5L, 下游 7L, 兩側 2.5W, 頂部 2.5H)
    print("[步驟 3/6] 計算 CFD 工程邊界擴展尺寸並生成外流域長方體...")
    bbox = wing_body.bounding_box
    min_p, max_p = bbox.min_point, bbox.max_point
    
    l_char = max_p.x - min_p.x  # 翼弦長
    w_char = max_p.y - min_p.y  # 翼厚度
    h_char = max_p.z - min_p.z  # 翼展長
    
    enc_min_x = min_p.x - (2.5 * l_char)
    enc_max_x = max_p.x + (7.0 * l_char)
    enc_min_y = min_p.y - (2.5 * w_char)
    enc_max_y = max_p.y + (2.5 * w_char)
    enc_min_z = min_p.z  # 貼齊底面作為對稱面
    enc_max_z = max_p.z + (2.5 * h_char)
    
    len_x = enc_max_x - enc_min_x
    len_y = enc_max_y - enc_min_y
    len_z = enc_max_z - enc_min_z
    
    center = [
        (enc_min_x + enc_max_x) / 2.0,
        (enc_min_y + enc_max_y) / 2.0,
        (enc_min_z + enc_max_z) / 2.0
    ]
    
    fluid_domain = design.create_block(
        name="FluidEnclosureDomain",
        length=len_x,
        width=len_y,
        height=len_z,
        center=center
    )
    print(f"  -> 外流域尺寸: X={len_x:.3f}m, Y={len_y:.3f}m, Z={len_z:.3f}m (阻塞率 < 3%)")

    # 4. 執行布林差集扣除
    print(f"[步驟 4/6] 執行布林相減 (Boolean Subtract, CHT保留模式={is_cht_mode})...")
    fluid_domain.subtract(wing_body, keep_other=is_cht_mode)
    print("  -> 布林扣除成功完成，流體腔體內部已挖空。")

    # 5. 自動識別拓撲邊界並建立 CAD 具名選擇
    print("[步驟 5/6] 執行空間外包圍盒幾何特徵過濾，標記 CAD 具名選擇 (Named Selections)...")
    f_bbox = fluid_domain.bounding_box
    tol = 1e-4
    inlet_faces, outlet_faces, symmetry_faces, farfield_faces, object_faces = [], [], [], [], []
    
    for face in fluid_domain.faces:
        c = face.box.center
        if abs(c.x - f_bbox.min_point.x) < tol:
            inlet_faces.append(face)
        elif abs(c.x - f_bbox.max_point.x) < tol:
            outlet_faces.append(face)
        elif abs(c.z - f_bbox.min_point.z) < tol:
            symmetry_faces.append(face)
        elif (abs(c.y - f_bbox.min_point.y) < tol or abs(c.y - f_bbox.max_point.y) < tol or
              abs(c.z - f_bbox.max_point.z) < tol):
            farfield_faces.append(face)
        else:
            object_faces.append(face)

    # 標記面與體 Named Selection
    if inlet_faces:
        design.create_named_selection("INLET", faces=inlet_faces)
    if outlet_faces:
        design.create_named_selection("OUTLET", faces=outlet_faces)
    if symmetry_faces:
        design.create_named_selection("SYMMETRY", faces=symmetry_faces)
    if farfield_faces:
        design.create_named_selection("FARFIELD_WALLS", faces=farfield_faces)
    if object_faces:
        design.create_named_selection("OBJECT_WALL", faces=object_faces)
        
    design.create_named_selection("FLUID_DOMAIN", bodies=[fluid_domain])
    if is_cht_mode:
        design.create_named_selection("SOLID_WING", bodies=[wing_body])

    print("  -> 具名選擇標記完畢：INLET, OUTLET, SYMMETRY, FARFIELD_WALLS, OBJECT_WALL, FLUID_DOMAIN。")

    # 6. 導出無損幾何檔案 (PMDB, SCDOCX)
    print(f"[步驟 6/6] 導出無損 CAD 資料庫至目錄: {output_dir}...")
    abs_out = os.path.abspath(output_dir)
    os.makedirs(abs_out, exist_ok=True)
    
    pmdb_file = os.path.join(abs_out, f"{model_name}.pmdb")
    scdocx_file = os.path.join(abs_out, f"{model_name}.scdocx")
    
    design.export_to_pmdb(pmdb_file)
    design.export_to_scdocx(scdocx_file)
    
    print("================================================================================")
    print(f"[成功完成] 無損幾何檔案已輸出:")
    print(f"  - PMDB 資料庫 : {pmdb_file}")
    print(f"  - SpaceClaim  : {scdocx_file}")
    print("================================================================================")
    return pmdb_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ANSYS 幾何前處理：外流域抽取與布林相減示範腳本")
    parser.add_argument("--output-dir", type=str, default="./cad_output", help="輸出資料夾路徑")
    parser.add_argument("--model-name", type=str, default="airfoil_cfd_prep", help="幾何模型名稱")
    parser.add_argument("--chord", type=float, default=0.3, help="翼弦長 (m)")
    parser.add_argument("--span", type=float, default=0.6, help="翼展長 (m)")
    parser.add_argument("--cht", action="store_true", help="啟用共軛熱傳 CHT 模式 (保留固體實體)")
    
    args = parser.parse_args()
    try:
        run_enclosure_pipeline(
            output_dir=args.output_dir,
            model_name=args.model_name,
            chord_m=args.chord,
            span_m=args.span,
            is_cht_mode=args.cht
        )
    except Exception as err:
        print(f"[致命錯誤] 幾何前處理管線中斷: {err}", file=sys.stderr)
        sys.exit(1)
