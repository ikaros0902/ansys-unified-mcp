# -*- coding: utf-8 -*-
"""
Auto Mesh Generator for ANSYS Mechanical.
Features:
- Automated Body Classification (Solid vs. Sheet/Shell).
- Feature-adaptive Sizing and Mesh Method assignment.
- Edge Sizing and Edge Washer generation on bolt hole Named Selections.
- Mesh Defeaturing to eliminate tiny CAD defect features.
- Hex-to-Tetra Automatic Fallback Self-Healing.
- Compatible with IronPython 2.7 (Mechanical ACT) and CPython 3.x (PyMechanical).
"""

import sys

def run_auto_mesh_pipeline(config=None):
    """
    Main entry point for automated feature-adaptive meshing.
    Args:
        config (dict, optional): Tuning and threshold configurations.
    """
    if config is None:
        config = {
            "solid_size": 2.0,            # mm
            "shell_size": 3.0,            # mm
            "solid_defeature": 0.4,       # mm
            "shell_defeature": 0.5,       # mm
            "washer_layers": 1,           # layers
            "edge_size_rm": 1.5,          # mm
            "ns_bolt_prefix": "Scr_RM_grp",
            "enable_washer": True,
            "enable_defeature": True
        }

    # Verify Mechanical environment handle
    try:
        model = ExtAPI.DataModel.Project.Model
        mesh = model.Mesh
    except NameError:
        print("[Error] ExtAPI or DataModel is not available. Please run inside ANSYS Mechanical ACT environment.")
        return False

    print("==================================================")
    print("Starting ANSYS Automated Feature-Adaptive Mesher...")
    print("==================================================")

    # 1. Global Defeaturing Settings
    if config.get("enable_defeature", True):
        try:
            mesh.AutomaticMeshDefeaturing = True
            mesh.DefeaturingTolerance = Quantity(config.get("solid_defeature", 0.4), "mm")
            print("[Global] Configured Mesh Defeaturing Tolerance: {} mm".format(config.get("solid_defeature", 0.4)))
        except Exception as ex:
            print("[Warning] Failed to set global defeaturing: {}".format(ex))

    # 2. Classify Bodies into Solid and Shell
    solid_body_ids = []
    shell_body_ids = []
    all_bodies = model.Geometry.GetChildren(DataModelObjectCategory.Body, True)

    for body in all_bodies:
        if getattr(body, "Suppressed", False):
            continue
        try:
            geo_body = body.GetGeoBody()
            body_type = geo_body.BodyType.ToString()
            if body_type == "GeoBodySolid":
                solid_body_ids.append(body.Id)
            elif body_type in ["GeoBodySheet", "GeoBodySurface"]:
                shell_body_ids.append(body.Id)
        except Exception as ex:
            pass

    print("[Topology] Detected {} Solid Bodies, {} Shell Bodies.".format(len(solid_body_ids), len(shell_body_ids)))

    # 3. Apply Solid Controls (Sizing + Method)
    if solid_body_ids:
        try:
            sel_solid = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
            sel_solid.Ids = solid_body_ids

            # Solid Sizing
            solid_sizing = mesh.AddSizing()
            solid_sizing.Name = "Auto_Solid_BodySizing"
            solid_sizing.Location = sel_solid
            solid_sizing.ElementSize = Quantity(config.get("solid_size", 2.0), "mm")
            solid_sizing.DefeaturingTolerance = Quantity(config.get("solid_defeature", 0.4), "mm")

            # Solid Method (MultiZone with Fallback)
            solid_method = mesh.AddAutomaticMethod()
            solid_method.Name = "Auto_Solid_Method"
            solid_method.Location = sel_solid
            try:
                solid_method.Method = Ansys.Mechanical.DataModel.Enums.MethodType.MultiZone
            except Exception:
                solid_method.Method = Ansys.Mechanical.DataModel.Enums.MethodType.AllTriAllTet
            print("[Solid Control] Created Sizing ({} mm) and Method.".format(config.get("solid_size", 2.0)))
        except Exception as ex:
            print("[Error] Failed applying solid controls: {}".format(ex))

    # 4. Apply Shell Controls (Sizing + Quad-Dominant Method)
    if shell_body_ids:
        try:
            sel_shell = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
            sel_shell.Ids = shell_body_ids

            shell_sizing = mesh.AddSizing()
            shell_sizing.Name = "Auto_Shell_BodySizing"
            shell_sizing.Location = sel_shell
            shell_sizing.ElementSize = Quantity(config.get("shell_size", 3.0), "mm")
            shell_sizing.DefeaturingTolerance = Quantity(config.get("shell_defeature", 0.5), "mm")

            shell_method = mesh.AddAutomaticMethod()
            shell_method.Name = "Auto_Shell_Method"
            shell_method.Location = sel_shell
            try:
                shell_method.Method = Ansys.Mechanical.DataModel.Enums.MethodType.QuadDominant
            except Exception:
                pass
            print("[Shell Control] Created Sizing ({} mm) and Quad-Dominant Method.".format(config.get("shell_size", 3.0)))
        except Exception as ex:
            print("[Error] Failed applying shell controls: {}".format(ex))

    # 5. Bolt Hole Features: Edge Sizing & Edge Washer
    bolt_ns_prefix = config.get("ns_bolt_prefix", "Scr_RM_grp")
    named_selections = model.NamedSelections.Children if hasattr(model, "NamedSelections") and model.NamedSelections else []
    bolt_ns_list = [ns for ns in named_selections if bolt_ns_prefix in ns.Name]

    if bolt_ns_list:
        print("[Bolt Features] Found {} Named Selections matching '{}'.".format(len(bolt_ns_list), bolt_ns_prefix))
        for ns in bolt_ns_list:
            try:
                # Add Edge Sizing on bolt holes
                edge_sizing = mesh.AddSizing()
                edge_sizing.Name = "Auto_EdgeSizing_{}".format(ns.Name)
                edge_sizing.Location = ns
                edge_sizing.Type = Ansys.Mechanical.DataModel.Enums.SizingType.ElementSize
                edge_sizing.ElementSize = Quantity(config.get("edge_size_rm", 1.5), "mm")
                edge_sizing.Behavior = Ansys.Mechanical.DataModel.Enums.SizingBehavior.Hard

                # Add Edge Washer if enabled
                if config.get("enable_washer", True):
                    try:
                        washer = mesh.AddWasher()
                        washer.Name = "Auto_Washer_{}".format(ns.Name)
                        washer.Location = ns
                        washer.NumberOfLayers = config.get("washer_layers", 1)
                    except Exception as w_ex:
                        # Washer creation fallback
                        pass
            except Exception as ex:
                print("[Warning] Failed applying washer/sizing for {}: {}".format(ns.Name, ex))
    else:
        print("[Bolt Features] No Named Selection with prefix '{}' found. Skipping Washer.".format(bolt_ns_prefix))

    # 6. Generate Mesh with Automatic Hex->Tet Fallback
    print("[Generation] Generating initial mesh...")
    mesh.ClearGeneratedData()
    mesh.GenerateMesh()

    # Self-healing check for unmeshed bodies
    unmeshed_count = 0
    for body in all_bodies:
        if getattr(body, "Suppressed", False):
            continue
        state_str = str(getattr(body, "ObjectState", "")).lower()
        if "meshed" not in state_str and "ready" not in state_str and "solved" not in state_str:
            unmeshed_count += 1

    if unmeshed_count > 0:
        print("[Self-Healing] Detected {} unmeshed bodies. Attempting fallback to Tetrahedrons...".format(unmeshed_count))
        # Switch solid method to AllTriAllTet
        for child in mesh.Children:
            if isinstance(child, Ansys.ACT.Automation.Mechanical.MeshControls.AutomaticMethod):
                try:
                    child.Method = Ansys.Mechanical.DataModel.Enums.MethodType.AllTriAllTet
                except Exception:
                    pass
        mesh.ClearGeneratedData()
        mesh.GenerateMesh()
        print("[Self-Healing] Fallback mesh generation completed.")

    print("==================================================")
    print("Auto Mesh Generation Completed!")
    print("Total Nodes: {}, Total Elements: {}".format(mesh.Nodes, mesh.Elements))
    print("==================================================")
    return True

if __name__ == "__main__":
    run_auto_mesh_pipeline()
