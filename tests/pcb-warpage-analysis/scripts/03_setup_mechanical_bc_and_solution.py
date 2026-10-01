"""
03_setup_mechanical_bc_and_solution.py
--------------------------------------------------------------------------------
ANSYS Mechanical Automation Script for PCB Warpage Analysis
- Sets MultiZone mesh method with 15mm global element size (structured hex).
- Generates layer Named Selections (NS_L01..NS_L79) for APDL material mapping.
- Imports APDL ROM temperature-dependent material macro into Static Structural.
- Sets Environment / Reference Temperature to 30 deg C.
- Applies Thermal Condition load (220 deg C) to all PCB bodies.
- Applies Statically Determinate 3-Point Displacement Support (3-2-1 Principle) on L79 bottom vertices (Z=0).
- Automatically checks / creates 78 Bonded Contacts across adjacent layers as fallback if topology sharing is incomplete.
- Configures Z-directional deformation (thermal warpage) exclusively (Total Deformation is strictly omitted).
- Provides camera framing and screenshot export with proper sizing and margin settings.
"""

import Ansys

def setup_mechanical_analysis(ExtAPI, apdl_macro_path):
    model = ExtAPI.DataModel.Project.Model
    analysis = model.Analyses[0]
    mesh = model.Mesh
    solution = analysis.Solution
    connections = model.Connections

    print("=== Starting Mechanical Setup ===")

    # 1. MultiZone Mesh Setup (Structured Hexahedral)
    for child in list(mesh.Children):
        if "Method" in child.GetType().Name:
            child.Delete()

    bodies = model.Geometry.GetChildren(DataModelObjectCategory.Body, True)
    sel_all_bodies = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    sel_all_bodies.Ids = [b.GetGeoBody().Id for b in bodies]

    method = mesh.AddAutomaticMethod()
    method.Method = Ansys.Mechanical.DataModel.Enums.MethodType.MultiZone
    method.Location = sel_all_bodies
    try:
        method.ElementOrder = Ansys.Mechanical.DataModel.Enums.ElementOrder.Linear
    except Exception:
        pass
    try:
        mesh.ElementOrder = Ansys.Mechanical.DataModel.Enums.ElementOrder.Linear
    except Exception:
        pass
    mesh.ElementSize = Quantity(15, "mm")

    print("Generating MultiZone Mesh (Linear Order)...")
    mesh.GenerateMesh()
    print("Mesh Created: Nodes = " + str(mesh.Nodes) + ", Elements = " + str(mesh.Elements))

    # 2. Layer Named Selections Setup (for APDL Material Mapping)
    if model.NamedSelections is not None:
        for child in list(model.NamedSelections.Children):
            child.Delete()

    for b in bodies:
        name = b.Name
        if "L" in name:
            parts = name.split("L")[1].split("_")
            try:
                num = int(parts[0])
                ns = model.AddNamedSelection()
                ns.Name = "NS_L%02d" % num
                sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                sel.Ids = [b.GetGeoBody().Id]
                ns.Location = sel
            except Exception:
                pass

    print("Created Named Selections (NS_L01..NS_L79) for all layers.")

    # 3. Import APDL Material Snippet
    for child in list(analysis.Children):
        if "CommandSnippet" in child.GetType().Name:
            child.Delete()

    apdl_cmd = analysis.AddCommandSnippet()
    apdl_cmd.Name = "APDL_ROM_Materials_79L"
    apdl_cmd.ImportTextFile(apdl_macro_path)
    print("Imported APDL Material Snippet: " + str(apdl_macro_path))

    # 4. Boundary Conditions & Thermal Load
    try:
        analysis.EnvironmentTemperature = Quantity(30, "C")
    except Exception:
        pass
    try:
        analysis.AnalysisSettings.ReferenceTemperature = Quantity(30, "C")
    except Exception:
        pass

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

    # P1: UX=0, UY=0, UZ=0 (3 DOFs constrained)
    d1 = analysis.AddDisplacement()
    d1.Name = "3Point_P1_UX0_UY0_UZ0"
    s1 = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    s1.Ids = [p1.Id]
    d1.Location = s1
    d1.XComponent.Output.DiscreteValues = [Quantity(0, "mm")]
    d1.YComponent.Output.DiscreteValues = [Quantity(0, "mm")]
    d1.ZComponent.Output.DiscreteValues = [Quantity(0, "mm")]

    # P2: UY=0, UZ=0 (2 DOFs constrained, UX Free)
    d2 = analysis.AddDisplacement()
    d2.Name = "3Point_P2_UY0_UZ0"
    s2 = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    s2.Ids = [p2.Id]
    d2.Location = s2
    d2.YComponent.Output.DiscreteValues = [Quantity(0, "mm")]
    d2.ZComponent.Output.DiscreteValues = [Quantity(0, "mm")]

    # P3: UZ=0 (1 DOF constrained, UX & UY Free)
    d3 = analysis.AddDisplacement()
    d3.Name = "3Point_P3_UZ0"
    s3 = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    s3.Ids = [p3.Id]
    d3.Location = s3
    d3.ZComponent.Output.DiscreteValues = [Quantity(0, "mm")]

    print("Applied 3-Point Statically Determinate Support on L79!")

    # 5. Fallback Bonded Contacts Generation (If topology is unshared)
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
            b_name = b.Name
            if "L" in b_name:
                try:
                    return int(b_name.split("L")[1].split("_")[0])
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
            cr.Name = "Bonded_%s_%s" % (b_upper.Name.split('_')[0], b_lower.Name.split('_')[0])
            cr.ContactType = Ansys.Mechanical.DataModel.Enums.ContactType.Bonded

            s_src = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
            s_src.Ids = [bot_u.Id]
            cr.SourceLocation = s_src

            s_trg = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
            s_trg.Ids = [top_l.Id]
            cr.TargetLocation = s_trg

    # 6. Solution Settings (Strictly Z-Directional Deformation, No Total Deformation)
    for child in list(solution.Children):
        if "Deformation" in child.GetType().Name or "Stress" in child.GetType().Name:
            child.Delete()

    # Top surface (L01) Z-displacement
    l01_list = [b for b in bodies if "L01" in b.Name or b.Name.startswith("L01")]
    if l01_list:
        gb_l01 = l01_list[0].GetGeoBody()
        top_faces = sorted([gb_l01.Faces[i] for i in range(gb_l01.Faces.Count)], key=lambda f: f.Centroid[2])
        if top_faces:
            l01_top_face = top_faces[-1]
            dir_l01 = solution.AddDirectionalDeformation()
            dir_l01.Name = "Z_Displacement_L01_Top_Face"
            dir_l01.NormalOrientation = Ansys.Mechanical.DataModel.Enums.NormalOrientationType.ZAxis
            s_top = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
            s_top.Ids = [l01_top_face.Id]
            dir_l01.Location = s_top

    # Bottom surface (L79) Z-displacement
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

    # All layers through-thickness Z-displacement
    dir_all = solution.AddDirectionalDeformation()
    dir_all.Name = "Z_Displacement_PCB_All_Layers"
    dir_all.NormalOrientation = Ansys.Mechanical.DataModel.Enums.NormalOrientationType.ZAxis
    dir_all.Location = sel_all_bodies

    print("Mechanical Setup Completed Successfully (Z-Warpage focused, Total Deformation omitted)!")

def export_warpage_contour_plots(ExtAPI, output_dir, basename="pcb_warpage"):
    """
    Export fine-tuned 2D and 3D warpage contour plots with optimal camera angles and margin.
    """
    import os
    cam = ExtAPI.Graphics.Camera
    axis = Ansys.Mechanical.DataModel.Enums.CameraAxisType

    solution = ExtAPI.DataModel.Project.Model.Analyses[0].Solution
    res_z = [c for c in solution.Children if "Z_Displacement_PCB_All_Layers" in c.Name]
    if not res_z:
        res_z = [c for c in solution.Children if "Z_Displacement" in c.Name]
    if res_z:
        res_z[0].Activate()

    # 1. 2D Front View (Normal to XY board face, zero perspective distortion)
    cam.SetSpecificViewOrientation(Ansys.Mechanical.DataModel.Enums.ViewOrientationType.Front)
    cam.SetFit()
    cam.Zoom(0.85)  # Leave 15% margin to prevent legend overlap
    front_path = os.path.join(output_dir, "%s_front_view.png" % basename)
    ExtAPI.Graphics.ExportImage(front_path)

    # 2. 3D Isometric View (Optimal perspective showing board thickness and curvature)
    cam.SetSpecificViewOrientation(Ansys.Mechanical.DataModel.Enums.ViewOrientationType.Front)
    cam.Rotate(-28, axis.ScreenX)
    cam.Rotate(-25, axis.ScreenY)
    cam.SetFit()
    cam.Zoom(0.82)  # Leave 18% margin for legend clearance
    iso_path = os.path.join(output_dir, "%s_iso_view.png" % basename)
    ExtAPI.Graphics.ExportImage(iso_path)

    print("Exported 2D Front View: " + str(front_path))
    print("Exported 3D Iso View: " + str(iso_path))
    return {"front": front_path, "iso": iso_path}
