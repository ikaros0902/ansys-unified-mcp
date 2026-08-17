# -*- coding: utf-8 -*-
"""
Master Workflow Runner: PCB Thermal Warpage Analysis.
"""
import sys
import os

# 將同目錄 script 加入路徑
sys.path.append(os.path.dirname(__file__))
from 02_calculate_rom_materials import export_apdl_macro

def run_workflow():
    print("==================================================")
    print("   PCB Multi-Layer Thermal Warpage Workflow")
    print("==================================================")
    
    print("\n[Step 1] 生成 ROM 複合材料屬性與 APDL 巨集文件...")
    mac_file = os.path.join(os.path.dirname(__file__), "apdl_rom_materials.mac")
    export_apdl_macro(mac_file, num_layers=79)
    
    print("\n[Step 2] 建立 SpaceClaim 79 層 PCB 幾何模型 (Share Topology)...")
    print("-> 腳本位置: scripts/01_build_pcb_geometry.py")
    
    print("\n[Step 3] 設定 Mechanical 3-2-1 靜不定邊界條件與求解...")
    print("-> 腳本位置: scripts/03_setup_mechanical_bc_and_solution.py")
    
    print("\n=== 全自動化分析流程部署完成 ===")

if __name__ == "__main__":
    run_workflow()
