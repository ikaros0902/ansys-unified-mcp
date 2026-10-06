"""
03_setup_mechanical_bc_and_solution.py
--------------------------------------------------------------------------------
ANSYS Mechanical Automation Script for PCB Warpage Analysis
- Sets MultiZone mesh method with 15mm global element size.
- Imports APDL ROM material macro into Static Structural.
- Sets Environment / Reference Temperature to 30 °C.
- Applies Thermal Condition load (220 °C) to all PCB bodies.
- Applies Statically Determinate 3-Point Displacement Support (3-2-1 Principle) on Layer 79 bottom vertices (Z=0).
- Automatically checks / creates 78 Bonded Contacts across adjacent layers as fallback if topology sharing is incomplete.
- Configures Z-displacement (Directional Deformation Z-axis) on L79 bottom face, all layers, and Total Deformation.
"""

import Ansys

def setup_mechanical_analysis(ExtAPI, apdl_macro_path: str):
    model = ExtAPI.DataModel.Project.Model
    analysis = model.Analyses[0]
    mesh = model.Mesh
    solution = analysis.Solution
    connections = model.Connections

    print("=== Starting Mechanical Setup ===")

    # 1. MultiZone Mesh Setup
    for child in list(mesh.Children):
        if "Method" in child.GetType().Name:
            child.Delete()

    bodies = model.Geometry.GetChildren(DataModelObjectCategory.Body, True)
    sel_all_bodies = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    sel_all_bodies.Ids = [b.GetGeoBody().Id for b in bodies]

    method = mesh.AddAutomaticMethod()
    method.Method = Ansys.Mechanical.DataModel.Enums.MethodType.MultiZone
    method.Location = sel_all_bodies
    mesh.ElementSize = Quantity(15, "mm")

    print("Generating MultiZone Mesh...")
    mesh.GenerateMesh()
    print(f"Mesh Created: Nodes = {mesh.Nodes}, Elements = {mesh.Elements}")

    # 2. Import APDL Material Snippet
    for child in list(analysis.Children):
        if "CommandSnippet" in child.GetType().Name:
            child.Delete()

    apdl_cmd = analysis.AddCommandSnippet()
    apdl_cmd.Name = "APDL_ROM_Materials_79L"
    apdl_cmd.ImportTextFile(apdl_macro_path)
    print(f"Imported APDL Material Snippet: {apdl_macro_path}")

    # 3. Boundary Conditions & Thermal Load
    analysis.EnvironmentTemperature = Quantity(30, "C")
    analysis.AnalysisSettings.ReferenceTemperature = Quantity(30, "C")

    for child in list(analysis.Children):
        if "ThermalCondition" in child.GetType().Name:
            child.Delete()

    thermal_cond = analysis.AddThermalCondition()
    thermal_cond.Name = "Thermal_Condition_220C"
    thermal_cond.Location = sel_all_bodies
    thermal_cond.Magnitude.Output.DiscreteValues = [Quantity(220, "C")]

    # 3-Point Statically Determinate Support on Layer 79 (Z=0)
    for child in list(analysis.Children):
        if "Displacement" in child.GetType().Name or "FixedSupport" in child.GetType().Name:
            child.Delete()

    l79 = [b for b in bodies if "L79" in b.Name][0]
    geo_body_l79 = l79.GetGeoBody()

    z0_vertices = []
    for i in range(geo_body_l79.Vertices.Count):
        v = geo_body_l79.Vertices[i]
        if abs(v.Z) < 1e-6:
            z0_vertices.append(v)

    p1 = min(z0_vertices, key=lambda v: v.X + v.Y)
    p2 = max(z0_vertices, key=lambda v: v.X - v.Y)
    p3 = max(z0_vertices, key=lambda v: v.Y - v.X)

    # P1: UX=0, UY=0, UZ=0 (3 DOFs)
    d1 = analysis.AddDisplacement()
    d1.Name = "3Point_P1_UX0_UY0_UZ0"
    s1 = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    s1.Ids = [p1.Id]
    d1.Location = s1
    d1.XComponent.Output.DiscreteValues = [Quantity(0, "mm")]
    d1.YComponent.Output.DiscreteValues = [Quantity(0, "mm")]
    d1.ZComponent.Output.DiscreteValues = [Quantity(0, "mm")]

    # P2: UY=0, UZ=0 (2 DOFs, UX Free)
    d2 = analysis.AddDisplacement()
    d2.Name = "3Point_P2_UY0_UZ0"
    s2 = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    s2.Ids = [p2.Id]
    d2.Location = s2
    d2.YComponent.Output.DiscreteValues = [Quantity(0, "mm")]
    d2.ZComponent.Output.DiscreteValues = [Quantity(0, "mm")]

    # P3: UZ=0 (1 DOF, UX&UY Free)
    d3 = analysis.AddDisplacement()
    d3.Name = "3Point_P3_UZ0"
    s3 = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    s3.Ids = [p3.Id]
    d3.Location = s3
    d3.ZComponent.Output.DiscreteValues = [Quantity(0, "mm")]

    print("Applied 3-Point Statically Determinate Support on L79!")

    # 4. Fallback Bonded Contacts Generation (If topology is unshared)
    total_contacts = 0
    if connections:
        for child in connections.Children:
            if "ConnectionGroup" in child.GetType().Name or "Contact" in child.GetType().Name:
                total_contacts += len(child.Children)

    if total_contacts == 0:
        print("Creating fallback Bonded Contacts between adjacent layers...")
        contact_group = connections.AddConnectionGroup()
        contact_group.Name = "PCB_79L_Bonded_Contacts"
        
        def get_layer_num(b):
            name = b.Name
            if "L" in name:
                try:
                    return int(name.split("L")[1].split("_")[0])
                except Exception:
                    pass
            return 999

        sorted_bodies = sorted(bodies, key=get_layer_num)
        for idx in range(len(sorted_bodies) - 1):
            b_upper = sorted_bodies[idx]
            b_lower = sorted_bodies[idx + 1]
            
            gb_u, gb_l = b_upper.GetGeoBody(), b_lower.GetGeoBody()
            bot_u = sorted([gb_u.Faces[i] for i in range(gb_u.Faces.Count)], key=lambda f: f.Centroid[2])[0]
            top_l = sorted([gb_l.Faces[i] for i in range(gb_l.Faces.Count)], key=lambda f: f.Centroid[2])[-1]
            
            cr = contact_group.AddContactRegion()
            cr.Name = f"Bonded_{b_upper.Name.split('_')[0]}_{b_lower.Name.split('_')[0]}"
            cr.ContactType = Ansys.Mechanical.DataModel.Enums.ContactType.Bonded
            
            s_src = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
            s_src.Ids = [bot_u.Id]
            cr.SourceLocation = s_src
            
            s_trg = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
            s_trg.Ids = [top_l.Id]
            cr.TargetLocation = s_trg

    # 5. Solution Settings
    for child in list(solution.Children):
        if "Deformation" in child.GetType().Name or "Stress" in child.GetType().Name:
            child.Delete()

    l79_bottom_face = None
    for i in range(geo_body_l79.Faces.Count):
        f = geo_body_l79.Faces[i]
        if abs(f.Centroid[2]) < 1e-6:
            l79_bottom_face = f
            break

    if l79_bottom_face:
        dir_l79 = solution.AddDirectionalDeformation()
        dir_l79.Name = "Z_Displacement_L79_Bottom_Face"
        dir_l79.NormalOrientation = Ansys.Mechanical.DataModel.Enums.NormalOrientationType.ZAxis
        s_f = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        s_f.Ids = [l79_bottom_face.Id]
        dir_l79.Location = s_f

    dir_all = solution.AddDirectionalDeformation()
    dir_all.Name = "Z_Displacement_PCB_All_Layers"
    dir_all.NormalOrientation = Ansys.Mechanical.DataModel.Enums.NormalOrientationType.ZAxis
    dir_all.Location = sel_all_bodies

    tot_def = solution.AddTotalDeformation()
    tot_def.Name = "Total_Deformation_PCB_All_Layers"
    tot_def.Location = sel_all_bodies

    print("Mechanical Setup Completed Successfully!")
