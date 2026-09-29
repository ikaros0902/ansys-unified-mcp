"""
01_build_pcb_geometry.py
--------------------------------------------------------------------------------
ANSYS SpaceClaim Geometry Generation Script for PCB Warpage Analysis
- Reads PCB stackup layers and dimensions from Excel (MCP_Test.xlsx).
- Connects to active SpaceClaim or launches new GUI instance via PyAnsys Geometry.
- Builds 79 separate solid bodies from Top (L01) to Bottom (L79).
- Enforces Share Topology = Share via sub-component to enable conformal mesh.
- Model export (.scdocx, .step, .pmdb) is DISABLED by default (manual/on-demand).
"""

import os
import sys
import time
import argparse
from pathlib import Path

# 強制設定標準輸出編碼為 UTF-8，防止 Windows cp950 編碼異常
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import pandas as pd
from ansys.geometry.core import Modeler, launch_modeler_with_spaceclaim
from ansys.geometry.core.designer import SharedTopologyType
from ansys.geometry.core.sketch import Sketch
from ansys.geometry.core.math import Point2D, Plane, Point3D

def get_or_launch_modeler(port: int = 50051, timeout: int = 5):
    """
    穩健連接或啟動 SpaceClaim Modeler：
    1. 優先嘗試快速探測本機活躍的 SpaceClaim (wnua 驗證模式)
    2. 若未探測到或超時，自動啟動新的可視化 SpaceClaim 實例
    """
    print(f"[*] 嘗試連線現有 SpaceClaim 實例 (Port: {port}, transport_mode: 'wnua')...")
    try:
        modeler = Modeler(port=port, transport_mode='wnua', timeout=timeout)
        design = modeler.read_existing_design()
        if design is not None:
            print(f"[OK] 成功連接至活躍 SpaceClaim 設計: '{design.name}' (Port: {port})")
            return modeler, design
        else:
            design = modeler.create_design("PCB_Warpage_Model")
            print(f"[OK] 成功連接並建立新設計: '{design.name}'")
            return modeler, design
    except Exception as err:
        print(f"[-] 連線現有實例未成功 ({err})，啟動全新 SpaceClaim GUI 實例...")

    modeler = launch_modeler_with_spaceclaim(hidden=False, timeout=120)
    design = modeler.create_design("PCB_Warpage_Model")
    print(f"[OK] 全新 SpaceClaim 實例啟動成功，建立設計: '{design.name}'")
    return modeler, design

def export_geometry_files(design, output_dir: Path, basename: str, formats: list = None):
    """
    手動/指定時匯出幾何檔案 (.scdocx, .step, .pmdb)
    """
    if not formats:
        formats = ["scdocx", "step", "pmdb"]

    output_dir.mkdir(parents=True, exist_ok=True)
    exported_map = {}
    print(f"\n[*] 依指令手動匯出幾何模型至: {output_dir}")

    if "scdocx" in formats:
        scdocx_path = output_dir / f"{basename}.scdocx"
        try:
            design.export_to_scdocx(str(scdocx_path))
            print(f"[OK] SCDOCX 匯出成功: {scdocx_path}")
            exported_map["scdocx"] = str(scdocx_path)
        except Exception as e:
            print(f"[-] SCDOCX 匯出失敗: {e}")

    if "step" in formats:
        step_path = output_dir / f"{basename}.step"
        try:
            design.export_to_step(str(step_path))
            print(f"[OK] STEP 匯出成功:   {step_path}")
            exported_map["step"] = str(step_path)
        except Exception as e:
            print(f"[-] STEP 匯出失敗:   {e}")

    if "pmdb" in formats:
        pmdb_path = output_dir / f"{basename}.pmdb"
        try:
            design.export_to_pmdb(str(pmdb_path))
            print(f"[OK] PMDB 匯出成功:   {pmdb_path}")
            exported_map["pmdb"] = str(pmdb_path)
        except Exception as e:
            print(f"[-] PMDB 匯出失敗:   {e}")

    return exported_map

def build_pcb_geometry(excel_path: str, port: int = 50051, export_files: bool = False, export_formats: list = None):
    """
    建立 PCB 幾何模型。
    預設 export_files=False（不主動匯出檔案，保留在 SpaceClaim 中即時檢視與後續調用）。
    """
    print("=" * 70)
    print("開始執行 PCB 疊構幾何自動化建模")
    print(f"讀取 Excel 設定檔: {excel_path}")
    print("=" * 70)

    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"找不到指定的 Excel 檔案: {excel_path}")

    output_dir = Path(excel_path).parent

    df_param = pd.read_excel(excel_path, sheet_name='Parameters')
    df_stack = pd.read_excel(excel_path, sheet_name='Stackup')

    L_mm = float(df_param[df_param['Parameter'] == 'L']['Value'].values[0])
    W_mm = float(df_param[df_param['Parameter'] == 'W']['Value'].values[0])
    L_m = L_mm / 1000.0
    W_m = W_mm / 1000.0

    total_thickness_mm = df_stack['Thickness (mm)'].sum()
    total_thickness_m = total_thickness_mm / 1000.0
    total_layers = len(df_stack)

    print(f"PCB 板外觀尺寸: 長 L = {L_mm} mm ({L_m} m), 寬 W = {W_mm} mm ({W_m} m)")
    print(f"PCB 總厚度: {total_thickness_mm:.4f} mm | 總疊構層數: {total_layers} 層")

    modeler, design = get_or_launch_modeler(port=port)

    # 清除設計中既有的元件與實體
    for c in list(design.components):
        try:
            design.delete_component(c)
        except Exception:
            pass

    for b in list(design.bodies):
        try:
            design.delete_body(b)
        except Exception:
            pass

    time.sleep(0.2)

    # 建立疊構專用子元件並啟用拓撲共享 (Share Topology)
    pcb_comp = design.add_component(f"PCB_Stackup_{total_layers}L")
    try:
        pcb_comp.set_shared_topology(SharedTopologyType.SHARETYPE_SHARE)
        print(f"[OK] 元件 '{pcb_comp.name}' 建立完成，拓撲共享已設為: {pcb_comp.shared_topology}")
    except Exception as e:
        print(f"[!] 設定 Shared Topology 警告: {e}")

    # 由頂層 (Top, L01) 向底層 (Bottom, L79) 依序建立實體
    print("-" * 70)
    print(f"開始由頂層至底層依序拉伸 {total_layers} 層實體...")
    z_top_m = total_thickness_m

    for idx, row in df_stack.iterrows():
        layer_num = int(row.iloc[0])
        thick_mm = float(row['Thickness (mm)'])
        cu_pct = float(row['Cu (%)'])
        mat = str(row['Material']).strip().replace('(', '_').replace(')', '')
        
        thick_m = thick_mm / 1000.0
        body_name = f"L{layer_num:02d}_{mat}_Cu{cu_pct:.1f}pct"
        z_plane_m = z_top_m - thick_m

        sketch = Sketch()
        sketch.plane = Plane(Point3D([0, 0, z_plane_m]))
        sketch.box(Point2D([0, 0]), L_m, W_m)

        body = pcb_comp.extrude_sketch(name=body_name, sketch=sketch, distance=thick_m)
        print(f"  [{layer_num:02d}/{total_layers:02d}] 拉伸 {body_name:<30} | 厚度: {thick_mm:.4f} mm | Z: [{z_plane_m*1000:7.4f} ~ {z_top_m*1000:7.4f}] mm")

        z_top_m = z_plane_m
        time.sleep(0.03)  # UI 緩衝保護

    print("=" * 70)
    print(f"[OK] SpaceClaim {total_layers} 層 PCB 幾何建模完成！")
    print(f"    元件名稱: {pcb_comp.name}")
    print(f"    拓撲共享: {pcb_comp.shared_topology}")
    print(f"    實體總數: {len(pcb_comp.bodies)} 個獨立實體")
    print("-" * 70)

    exported_files = {}
    if export_files:
        basename = f"PCB_Stackup_{total_layers}L"
        exported_files = export_geometry_files(design, output_dir, basename, export_formats)
    else:
        print("[*] 檔案匯出設定為手動模式（已略過自動儲存 .scdocx / .step / .pmdb）。")

    print("=" * 70)
    return {
        "success": True,
        "layers": total_layers,
        "length_mm": L_mm,
        "width_mm": W_mm,
        "thickness_mm": total_thickness_mm,
        "exported_files": exported_files
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ANSYS SpaceClaim PCB 疊構幾何建模腳本")
    parser.add_argument("excel", nargs="?", default=r"D:\ANSYS_MCP_Connect\PCB_Stackup_material\MCP_Test.xlsx", help="PCB 疊構 Excel 檔案路徑")
    parser.add_argument("--port", type=int, default=50051, help="SpaceClaim gRPC 連線埠號")
    parser.add_argument("--export", action="store_true", default=False, help="手動指定是否匯出幾何檔案（預設不匯出）")
    parser.add_argument("--formats", nargs="+", default=["scdocx", "step", "pmdb"], help="匯出格式清單 (scdocx step pmdb)")
    args = parser.parse_args()

    build_pcb_geometry(
        excel_path=args.excel,
        port=args.port,
        export_files=args.export,
        export_formats=args.formats
    )
