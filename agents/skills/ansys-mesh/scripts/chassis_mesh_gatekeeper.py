# -*- coding: utf-8 -*-
# ==============================================================================
# ANSYS Mechanical ACT Script: Full-Chassis Pre-Mesh Gatekeeper & Adaptive Mesher
# 
# Key Features:
# 1. Objective Geometry Metric Extraction (BBox, t_eq = 2V/A, Fill Ratio, Slenderness, Planar Ratio).
# 2. Short-Edge Gatekeeper & Circuit Breaker:
#    - Scans unsuppressed bodies for edges shorter than threshold.
#    - If found: Halts execution immediately before meshing.
#    - Visual Isolation: Sets problem bodies Visible=True, all normal bodies Visible=False.
#    - Automatic Named Selections: NS_ShortEdges_ALL & NS_ShortEdges_<BodyName>.
# 3. Defeature Authorization Protection:
#    - Never applies global/unauthorized defeaturing.
#    - Only applies DefeaturingTolerance to bodies explicitly listed in approved_defeature_bodies.
# 4. Quantitative Method & Size Decision Engine:
#    - Sheet bodies -> QuadDominant (2D Shell).
#    - Planar thin solids (R_slender >= 8) -> Sweep Hex (2-3 thickness layers).
#    - Orthogonal block solids -> MultiZone.
#    - Complex/Organic solids -> Patch Conforming Tetrahedrons.
# 5. Group Batching: Sequential meshing by group to prevent memory exhaustion and UI lockups.
#
# Note: All internal comments strictly in ASCII per IronPython 2.7 / ANSI rules.
# ==============================================================================

import sys
import math


def run_chassis_mesh_pipeline(config=None):
    """
    Main entry point for full-chassis pre-mesh inspection and adaptive meshing.
    
    Args:
        config (dict, optional):
            - short_edge_threshold_mm (float): Length threshold for short edges (default: 0.25 mm).
            - approved_defeature_bodies (list of str): Body names approved by user for defeaturing.
            - defeature_tolerance_mm (float): Defeaturing tolerance for approved bodies (default: 0.4 mm).
            - global_growth_rate (float): Transition growth rate (default: 1.25).
            - bolt_ns_prefix (str): Prefix for bolt hole Named Selections (default: 'Scr_RM_grp').
            - execute_mesh (bool): Whether to proceed to mesh generation if pre-check passes (default: True).
    """
    if config is None:
        config = {
            "short_edge_threshold_mm": 0.25,
            "approved_defeature_bodies": [],
            "defeature_tolerance_mm": 0.4,
            "global_growth_rate": 1.25,
            "bolt_ns_prefix": "Scr_RM_grp",
            "execute_mesh": True
        }

    short_edge_thresh = config.get("short_edge_threshold_mm", 0.25)
    approved_defeature = set(config.get("approved_defeature_bodies", []))
    defeature_tol = config.get("defeature_tolerance_mm", 0.4)
    growth_rate = config.get("global_growth_rate", 1.25)
    bolt_prefix = config.get("bolt_ns_prefix", "Scr_RM_grp")
    do_mesh = config.get("execute_mesh", True)

    try:
        model = ExtAPI.DataModel.Project.Model
        mesh = model.Mesh
        geom = model.Geometry
        sel_mgr = ExtAPI.SelectionManager
    except NameError:
        print("[Error] ExtAPI or DataModel is not available. Please run in ANSYS Mechanical ACT.")
        return False

    all_bodies = geom.GetChildren(DataModelObjectCategory.Body, True)
    active_bodies = [b for b in all_bodies if not getattr(b, "Suppressed", False)]

    print("==================================================================")
    print("ANSYS Full-Chassis Pre-Mesh Inspection & Decision Pipeline")
    print("Total Active Unsuppressed Bodies: {}".format(len(active_bodies)))
    print("Short-Edge Halt Threshold: {} mm".format(short_edge_thresh))
    print("Approved Defeature Bodies Count: {}".format(len(approved_defeature)))
    print("==================================================================")

    if not active_bodies:
        print("[Warning] No unsuppressed bodies found. Exiting.")
        return True

    # -------------------------------------------------------------------------
    # Phase 1: Metric Extraction & Short-Edge Detection
    # -------------------------------------------------------------------------
    problem_bodies = []
    all_short_edge_ids = []
    body_short_edges_map = {}
    chassis_records = []

    for body in active_bodies:
        geo_body = body.GetGeoBody()
        b_type = geo_body.BodyType.ToString()
        b_name = body.Name

        # Bounding Box (Mechanical internal coordinates in meters -> mm)
        bbox = geo_body.GetBoundingBox()
        dx = abs(bbox[3] - bbox[0]) * 1000.0
        dy = abs(bbox[4] - bbox[1]) * 1000.0
        dz = abs(bbox[5] - bbox[2]) * 1000.0
        dims = sorted([dx, dy, dz], reverse=True)
        d_max, d_mid, d_min = dims[0], dims[1], max(dims[2], 1e-3)

        # Topological Volume, Surface Area, Planar Ratio
        is_sheet = (b_type in ["GeoBodySheet", "GeoBodySurface"])
        vol_mm3 = (geo_body.Volume * 1e9) if not is_sheet else 0.0
        faces = geo_body.Faces
        num_faces = faces.Count
        total_area_mm2 = 0.0
        planar_area_mm2 = 0.0

        for f in faces:
            a = f.Area * 1e6
            total_area_mm2 += a
            if f.SurfaceType.ToString() == "GeoSurfacePlane":
                planar_area_mm2 += a

        planar_ratio = (planar_area_mm2 / total_area_mm2) if total_area_mm2 > 0 else 0.0
        t_eq = (2.0 * vol_mm3 / total_area_mm2) if (not is_sheet and total_area_mm2 > 0) else d_min
        fill_ratio = (vol_mm3 / (d_max * d_mid * d_min)) if (d_max * d_mid * d_min > 0) else 0.0
        slenderness = (d_mid / t_eq) if t_eq > 0 else 1.0

        # Method & Size Decision
        if is_sheet:
            rec_method = "QuadDominant"
            rec_size = max(2.0, min(8.0, round(d_mid / 20.0, 1)))
            group_cat = "Sheet"
        else:
            if planar_ratio >= 0.70 and slenderness >= 8.0 and num_faces <= 120:
                rec_method = "Sweep"
                rec_size = max(1.5, min(6.0, round(min(d_mid / 15.0, 4.0 * t_eq), 1)))
                group_cat = "SolidSweep"
            elif planar_ratio >= 0.75 and num_faces <= 200:
                rec_method = "MultiZone"
                l_char = (d_max * d_mid * d_min) ** (1.0 / 3.0)
                rec_size = max(1.5, min(10.0, round(l_char / 10.0, 1)))
                group_cat = "SolidMultiZone"
            else:
                rec_method = "PatchConformingTet"
                if slenderness >= 10.0:
                    rec_size = max(0.8, min(4.0, round(1.2 * t_eq, 1)))
                else:
                    l_char = (d_max * d_mid * d_min) ** (1.0 / 3.0)
                    rec_size = max(1.5, min(10.0, round(l_char / 10.0, 1)))
                group_cat = "SolidTet"

        # Scan Edges for Short-Edge Defect
        short_edge_ids = []
        min_e_len = 1e9
        for edge in geo_body.Edges:
            e_len = edge.Length * 1000.0
            if e_len < min_e_len:
                min_e_len = e_len
            if e_len < short_edge_thresh:
                short_edge_ids.append(edge.Id)
                all_short_edge_ids.append(edge.Id)

        if short_edge_ids:
            problem_bodies.append(body)
            body_short_edges_map[b_name] = (len(short_edge_ids), min_e_len, short_edge_ids)

        chassis_records.append({
            "body": body,
            "name": b_name,
            "group": group_cat,
            "is_sheet": is_sheet,
            "bbox_str": "{:.1f}x{:.1f}x{:.1f}".format(d_max, d_mid, d_min),
            "t_eq": round(t_eq, 2),
            "method": rec_method,
            "size_mm": rec_size,
            "short_count": len(short_edge_ids),
            "min_edge_mm": round(min_e_len, 4) if min_e_len < 1e8 else 0.0
        })

    # Print Formatted Decision Table
    print("\n[Quantitative Method & Sizing Decision Table]")
    print("{:<28} | {:<10} | {:<18} | {:<6} | {:<20} | {:<7} | {:<10}".format(
        "Body Name", "Category", "BBox (mm)", "t_eq", "Method", "Size", "ShortEdges"))
    print("-" * 115)
    for r in chassis_records:
        print("{:<28} | {:<10} | {:<18} | {:<6.2f} | {:<20} | {:<5.1f}mm | {:<10}".format(
            r["name"][:28], r["group"], r["bbox_str"], r["t_eq"],
            r["method"], r["size_mm"], r["short_count"]))

    # -------------------------------------------------------------------------
    # Phase 2: Short-Edge Gatekeeper Circuit Breaker
    # -------------------------------------------------------------------------
    if problem_bodies:
        print("\n==================================================================")
        print("[CIRCUIT BREAKER ACTIVATED] SHORT EDGES DETECTED ON {} BODIES!".format(len(problem_bodies)))
        print("PAUSING MESH PIPELINE TO PREVENT CRASH OR SEVERE MESH DISTORTION.")
        print("==================================================================")

        # 1. Visual Isolation: Show ONLY problem bodies, hide clean bodies
        problem_ids = set([b.Id for b in problem_bodies])
        with Transaction(True):
            for b in active_bodies:
                b.Visible = (b.Id in problem_ids)

        # 2. Automatically create Named Selections for Short Edges
        sel_all = sel_mgr.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        sel_all.Ids = all_short_edge_ids
        ns_all = model.AddNamedSelection()
        ns_all.Name = "NS_ShortEdges_ALL"
        ns_all.Location = sel_all

        for b_name, (cnt, min_l, e_ids) in body_short_edges_map.items():
            sel_b = sel_mgr.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
            sel_b.Ids = e_ids
            ns_b = model.AddNamedSelection()
            # Truncate name safely
            clean_name = "".join([c if c.isalnum() else "_" for c in b_name])[:22]
            ns_b.Name = "NS_Short_{}".format(clean_name)
            ns_b.Location = sel_b
            print(" -> Body '{}': {} short edges (Min: {:.4f} mm) -> Created '{}'".format(
                b_name, cnt, min_l, ns_b.Name))

        print("\n[Action Taken by Gatekeeper]")
        print("1. Hidden all {} normal bodies. Only {} problematic bodies are visible.".format(
            len(active_bodies) - len(problem_bodies), len(problem_bodies)))
        print("2. Created Named Selection 'NS_ShortEdges_ALL' and per-body short edge sets.")
        print("3. Execution HALTED. Please inspect geometry in Mechanical.")
        print("   -> Next Step: Inform user and obtain approval for which bodies require Defeaturing.")
        return False

    if not do_mesh:
        print("\n[OK] Pre-mesh check passed. execute_mesh is False. Ready for user confirmation.")
        return True

    # -------------------------------------------------------------------------
    # Phase 3: Mesh Controls Setup (Method + Sizing + Approved Defeaturing)
    # -------------------------------------------------------------------------
    print("\n[Phase 3] Applying Automated Mesh Controls...")
    mesh.PhysicsPreference = MeshPhysicsPreferenceType.Mechanical
    mesh.GrowthRate = growth_rate

    # Apply body controls individually or by group
    for r in chassis_records:
        b = r["body"]
        b_name = r["name"]
        geo_id = b.GetGeoBody().Id
        sel_body = sel_mgr.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        sel_body.Ids = [geo_id]

        # 1. Add Body Sizing
        b_sizing = mesh.AddSizing()
        b_sizing.Name = "Auto_Size_{}".format(b_name[:20])
        b_sizing.Location = sel_body
        b_sizing.ElementSize = Quantity(r["size_mm"], "mm")

        # 2. Defeaturing check: ONLY apply if explicitly approved by user
        if b_name in approved_defeature:
            b_sizing.DefeaturingTolerance = Quantity(defeature_tol, "mm")
            print(" -> Body '{}': Defeaturing Tolerance applied ({} mm)".format(b_name, defeature_tol))
        else:
            b_sizing.DefeaturingTolerance = Quantity(0.0, "mm")

        # 3. Add Method
        if r["method"] == "QuadDominant":
            method_obj = mesh.AddAutomaticMethod()
            method_obj.Name = "Method_Quad_{}".format(b_name[:20])
            method_obj.Location = sel_body
            try:
                method_obj.Method = Ansys.Mechanical.DataModel.Enums.MethodType.QuadDominant
            except Exception:
                pass

        elif r["method"] == "Sweep":
            method_obj = mesh.AddAutomaticMethod()
            method_obj.Name = "Method_Sweep_{}".format(b_name[:20])
            method_obj.Location = sel_body
            try:
                method_obj.Method = Ansys.Mechanical.DataModel.Enums.MethodType.Sweep
                method_obj.SweepNumberDivisions = 2
            except Exception:
                pass

        elif r["method"] == "MultiZone":
            method_obj = mesh.AddAutomaticMethod()
            method_obj.Name = "Method_MultiZone_{}".format(b_name[:20])
            method_obj.Location = sel_body
            try:
                method_obj.Method = Ansys.Mechanical.DataModel.Enums.MethodType.MultiZone
            except Exception:
                pass

        elif r["method"] == "PatchConformingTet":
            method_obj = mesh.AddAutomaticMethod()
            method_obj.Name = "Method_Tet_{}".format(b_name[:20])
            method_obj.Location = sel_body
            try:
                method_obj.Method = Ansys.Mechanical.DataModel.Enums.MethodType.AllTriAllTet
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # Phase 4: Bolt Hole Sizing & Edge Washer (Optional)
    # -------------------------------------------------------------------------
    named_selections = model.NamedSelections.Children if hasattr(model, "NamedSelections") and model.NamedSelections else []
    bolt_ns_list = [ns for ns in named_selections if bolt_prefix in ns.Name]
    if bolt_ns_list:
        print("[Bolt Features] Found {} bolt hole Named Selections. Adding washers...".format(len(bolt_ns_list)))
        for ns in bolt_ns_list:
            try:
                w_obj = mesh.AddWasher()
                w_obj.Name = "Washer_{}".format(ns.Name[:20])
                w_obj.Location = ns
                w_obj.NumberOfLayers = 1
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # Phase 5: Sequential Group Batching Mesh Generation
    # -------------------------------------------------------------------------
    print("\n[Phase 5] Sequential Group Batching Generation...")
    groups = ["Sheet", "SolidSweep", "SolidMultiZone", "SolidTet"]

    for g_name in groups:
        g_records = [r for r in chassis_records if r["group"] == g_name]
        if not g_records:
            continue
        print("Meshing Group '{}' ({} bodies)...".format(g_name, len(g_records)))
        # Isolate group for memory protection
        g_bodies = [r["body"] for r in g_records]
        with Transaction(True):
            for b in active_bodies:
                b.Suppressed = (b not in g_bodies)

        mesh.GenerateMesh()
        print("Group '{}' meshed successfully.".format(g_name))

    # Rollback Unsuppress All
    with Transaction(True):
        for b in active_bodies:
            b.Suppressed = False
            b.Visible = True

    print("\n==================================================================")
    print("Full-Chassis Meshing Complete!")
    print("Total Nodes: {}".format(mesh.Nodes))
    print("Total Elements: {}".format(mesh.Elements))
    print("==================================================================")
    return True


if __name__ == "__main__":
    run_chassis_mesh_pipeline()
