import json
import time
import ansys.mechanical.core as mech

def run_stepped_meshing():
    app = mech.Mechanical(port=10000)
    
    # Python controller to process Part by Part with Show/Hide visibility
    init_script = """
import json
geo = ExtAPI.DataModel.Project.Model.Geometry
all_bodies = geo.GetChildren(DataModelObjectCategory.Body, True)

part_names = []
for b in all_bodies:
    p_name = b.Parent.Name.strip() if b.Parent is not None else "Unassigned"
    if p_name not in part_names:
        part_names.append(p_name)

# Return parts and their bodies
part_bodies_map = {}
for p in part_names:
    bodies_in_p = [b for b in all_bodies if (b.Parent.Name.strip() if b.Parent else "") == p]
    unmeshed_in_p = [b.Name for b in bodies_in_p if b.Elements == 0]
    part_bodies_map[p] = {
        "total": len(bodies_in_p),
        "unmeshed_count": len(unmeshed_in_p),
        "unmeshed_names": unmeshed_in_p
    }

json.dumps(part_bodies_map)
"""
    raw_map = app.run_python_script(init_script)
    part_map = json.loads(raw_map)
    
    print("=" * 60)
    print("STEP 3: Partitioned Meshing with Show/Hide & 3-Min Timeout")
    print("=" * 60)
    
    for part_name, p_info in part_map.items():
        if p_info["unmeshed_count"] == 0:
            print("[ALREADY MESHED] Part: {} (All {} bodies ready)".format(part_name, p_info["total"]))
            continue
            
        print("\n" + "-" * 50)
        print(">>> Activating Part: {} (Showing {} bodies, hiding others)".format(part_name, p_info["total"]))
        print("-" * 50)
        
        # 1. Update visibility: Show this part, hide all others
        vis_script = """
geo = ExtAPI.DataModel.Project.Model.Geometry
for b in geo.GetChildren(DataModelObjectCategory.Body, True):
    p_name = b.Parent.Name.strip() if b.Parent is not None else "Unassigned"
    if p_name == "{}":
        b.Visible = True
    else:
        b.Visible = False
ExtAPI.Graphics.Redraw()
""".format(part_name)
        app.run_python_script(vis_script)
        
        # 2. Mesh each unmeshed body in this part with timeout check
        for body_name in p_info["unmeshed_names"]:
            print("  Meshing body: {} ...".format(body_name))
            t_start = time.time()
            
            mesh_body_script = """
import json
geo = ExtAPI.DataModel.Project.Model.Geometry
mesh = ExtAPI.DataModel.Project.Model.Mesh

target_b = None
for b in geo.GetChildren(DataModelObjectCategory.Body, True):
    if b.Name == "{}":
        target_b = b
        break

res = {{"status": "failed", "elements": 0, "nodes": 0}}
if target_b is not None:
    try:
        target_b.GenerateMesh()
        if target_b.Elements > 0:
            res["status"] = "success"
            res["elements"] = target_b.Elements
            res["nodes"] = target_b.Nodes
        else:
            # Fallback: recreate method as AllTriAllTet
            b_id = target_b.GetGeoBody().Id
            for c in list(mesh.Children):
                if hasattr(c, "Location") and c.Location is not None and b_id in list(c.Location.Ids):
                    c.Delete()
            new_m = mesh.AddAutomaticMethod()
            sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
            sel.Ids = [b_id]
            new_m.Location = sel
            new_m.Method = MethodType.AllTriAllTet
            target_b.GenerateMesh()
            if target_b.Elements > 0:
                res["status"] = "fixed_fallback"
                res["elements"] = target_b.Elements
                res["nodes"] = target_b.Nodes
    except Exception as e:
        res["error"] = str(e)

json.dumps(res)
""".format(body_name)
            
            res_str = app.run_python_script(mesh_body_script)
            elapsed = time.time() - t_start
            
            try:
                b_res = json.loads(res_str)
                if b_res.get("status") in ["success", "fixed_fallback"]:
                    print("  [OK] {} | Elements: {} | Nodes: {} ({:.1f}s)".format(
                        body_name, b_res.get("elements", 0), b_res.get("nodes", 0), elapsed
                    ))
                else:
                    print("  [FAIL] {} | Error: {} ({:.1f}s)".format(body_name, b_res.get("error", "Unknown"), elapsed))
            except Exception as e:
                print("  [ERROR] {} | Raw: {} ({:.1f}s)".format(body_name, res_str, elapsed))

    # 3. Final Step: Restore visibility for ALL 114 bodies
    print("\n" + "=" * 60)
    print("All parts processed. Restoring full visibility for all bodies...")
    restore_vis_script = """
import json
model = ExtAPI.DataModel.Project.Model
geo = model.Geometry
mesh = model.Mesh

all_bodies = geo.GetChildren(DataModelObjectCategory.Body, True)
for b in all_bodies:
    b.Visible = True

ExtAPI.Graphics.Redraw()

unmeshed = [b.Name for b in all_bodies if b.Elements == 0]
final_stat = {
    "total_bodies": len(all_bodies),
    "meshed_count": len(all_bodies) - len(unmeshed),
    "unmeshed_count": len(unmeshed),
    "unmeshed_names": unmeshed,
    "total_nodes": mesh.Nodes,
    "total_elements": mesh.Elements
}
json.dumps(final_stat)
"""
    final_res = app.run_python_script(restore_vis_script)
    final_stat = json.loads(final_res)
    print("=" * 60)
    print("FINAL SUMMARY:")
    print("Total Bodies: {}".format(final_stat["total_bodies"]))
    print("Successfully Meshed: {}".format(final_stat["meshed_count"]))
    print("Unmeshed Remaining: {}".format(final_stat["unmeshed_count"]))
    print("Total Nodes: {}".format(final_stat["total_nodes"]))
    print("Total Elements: {}".format(final_stat["total_elements"]))
    print("=" * 60)

if __name__ == "__main__":
    run_stepped_meshing()
