"""
01_build_pcb_geometry.py
--------------------------------------------------------------------------------
ANSYS SpaceClaim Geometry Generation Script for PCB Warpage Analysis
- Reads PCB stackup layers and dimensions from Excel (MCP_Test.xlsx).
- Builds 79 separate solid bodies from Top (L01) to Bottom (L79).
- Enforces Share Topology = Share via sub-component to enable conformal mesh.
- Adds 50ms UI buffer between layer extrusions to prevent GUI pane refresh crashes.
"""

import os
import sys
import time
import pandas as pd
from ansys.geometry.core import Modeler
from ansys.geometry.core.designer import SharedTopologyType
from ansys.geometry.core.sketch import Sketch
from ansys.geometry.core.math import Point2D, Plane, Point3D

def build_pcb_geometry(excel_path: str, port: int = 50051):
    print(f"Reading PCB Stackup Excel: {excel_path}")
    df_param = pd.read_excel(excel_path, sheet_name='Parameters')
    df_stack = pd.read_excel(excel_path, sheet_name='Stackup')

    L_mm = float(df_param[df_param['Parameter'] == 'L']['Value'].values[0])
    W_mm = float(df_param[df_param['Parameter'] == 'W']['Value'].values[0])
    L_m = L_mm / 1000.0
    W_m = W_mm / 1000.0

    total_thickness_mm = df_stack['Thickness (mm)'].sum()
    total_thickness_m = total_thickness_mm / 1000.0

    print(f"Board Dimensions: L = {L_mm} mm ({L_m} m), W = {W_mm} mm ({W_m} m)")
    print(f"Total PCB Thickness: {total_thickness_mm:.4f} mm ({len(df_stack)} Layers)")

    # Connect to SpaceClaim gRPC
    modeler = Modeler(port=port, transport_mode='wnua')
    design = modeler.read_existing_design()
    if not design:
        design = modeler.create_design("SYS")
    print(f"Connected to SpaceClaim active design: '{design.name}'")

    # Clear previous geometry
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

    # Create sub-component and set Share Topology = Share
    pcb_comp = design.add_component("PCB_Stackup_79L")
    pcb_comp.set_shared_topology(SharedTopologyType.SHARETYPE_SHARE)
    print(f"Created Component: '{pcb_comp.name}' with Share Topology = {pcb_comp.shared_topology}")

    # Build layers from Top (L01) to Bottom (L79)
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
        print(f"  [{layer_num:02d}/79] Extruded {body_name} | Thick: {thick_mm:.4f} mm | Z: [{z_plane_m*1000:.4f} ~ {z_top_m*1000:.4f}] mm")

        z_top_m = z_plane_m
        time.sleep(0.05)  # 50ms UI buffer protection

    print("="*60)
    print(f"SpaceClaim PCB Geometry Build Completed!")
    print(f"Component: '{pcb_comp.name}' | Shared Topology: {pcb_comp.shared_topology}")
    print(f"Bodies: {len(pcb_comp.bodies)} (Uncombined separate bodies)")
    print("="*60)

if __name__ == "__main__":
    excel_file = r"D:\ANSYS_MCP_Connect\PCB_Stackup_material\MCP_Test.xlsx"
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
    build_pcb_geometry(excel_file)
