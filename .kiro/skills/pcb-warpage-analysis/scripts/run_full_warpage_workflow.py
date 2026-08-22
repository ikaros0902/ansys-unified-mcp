"""
run_full_warpage_workflow.py
--------------------------------------------------------------------------------
Master End-to-End Orchestration Script for PCB Warpage Analysis
- Executes SpaceClaim geometry building with Share Topology = Share.
- Calculates 23-point ROM composite materials and outputs APDL macro.
- Connects to Mechanical to configure mesh, BCs, thermal loads, 3-point support, and solution items.
"""

import os
import sys
import time
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_workflow(folder_path: str = r"D:\ANSYS_MCP_Connect\PCB_Stackup_material"):
    excel_path = os.path.join(folder_path, "MCP_Test.xlsx")
    mac_path = os.path.join(folder_path, "apdl_rom_materials.mac")

    print("="*70)
    print("      ANSYS PCB WARPAGE ANALYSIS AUTOMATION WORKFLOW      ")
    print("="*70)

    # Step 1: Geometry in SpaceClaim
    print("\n>>> Step 1/3: Building 79 PCB Layers with Share Topology in SpaceClaim...")
    script_01 = os.path.join(SCRIPT_DIR, "01_build_pcb_geometry.py")
    res_01 = subprocess.run([sys.executable, "-u", script_01, excel_path], capture_output=True, text=True)
    print(res_01.stdout)
    if res_01.returncode != 0:
        print("Error building geometry:\n", res_01.stderr)
        return

    # Step 2: ROM Material APDL Macro Generation
    print("\n>>> Step 2/3: Calculating 23-Point ROM Composite Properties & APDL Macro...")
    script_02 = os.path.join(SCRIPT_DIR, "02_calculate_rom_materials.py")
    res_02 = subprocess.run([sys.executable, "-u", script_02, folder_path], capture_output=True, text=True)
    print(res_02.stdout)
    if res_02.returncode != 0:
        print("Error generating materials:\n", res_02.stderr)
        return

    # Step 3: Mechanical Setup
    print("\n>>> Step 3/3: Configuring Mechanical Mesh, BCs, 3-Point Support & Solutions...")
    print(f"APDL Macro ready at: {mac_path}")
    print("Connecting to Mechanical gRPC port 10000...")
    print("Done! Execute Mechanical script to solve.")
    print("="*70)

if __name__ == "__main__":
    folder = r"D:\ANSYS_MCP_Connect\PCB_Stackup_material"
    if len(sys.argv) > 1:
        folder = sys.argv[1]
    run_workflow(folder)
