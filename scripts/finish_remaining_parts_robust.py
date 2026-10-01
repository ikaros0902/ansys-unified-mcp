import json
import time
import ansys.mechanical.core as mech

def finish_meshing():
    app = mech.Mechanical(port=10000)
    
    script = """
import json

model = ExtAPI.DataModel.Project.Model
mesh = model.Mesh
geo = model.Geometry

all_bodies = geo.GetChildren(DataModelObjectCategory.Body, True)

# Group by parent Part
part_map = {}
for b in all_bodies:
    p_name = b.Parent.Name.strip() if b.Parent is not None else "Unassigned"
    if p_name not in part_map:
        part_map[p_name] = []
    part_map[p_name].append(b)

results = []

for p_name, bodies in part_map.items():
    unmeshed_in_part = [b for b in bodies if b.Elements == 0]
    if len(unmeshed_in_part) == 0:
        results.append({"part": p_name, "status": "already_meshed", "count": len(bodies)})
        continue
        
    # 1. Visibility: Show this part, hide others
    for b in all_bodies:
        if (b.Parent.Name.strip() if b.Parent else "") == p_name:
            b.Visible = True
        else:
            b.Visible = False
    ExtAPI.Graphics.Redraw()
    
    part_log = {"part": p_name, "total": len(bodies), "meshed": 0, "fixed_with_tet": 0, "failed": 0}
    
    # 2. Mesh unmeshed bodies
    for b in unmeshed_in_part:
        try:
            b.GenerateMesh()
        except:
            pass
            
        if b.Elements > 0:
            part_log["meshed"] += 1
        else:
            # Fallback to AllTriAllTet
            b_id = b.GetGeoBody().Id
            for c in list(mesh.Children):
                if hasattr(c, "Location") and c.Location is not None and b_id in list(c.Location.Ids):
                    try:
                        c.Delete()
                    except:
                        pass
            try:
                new_m = mesh.AddAutomaticMethod()
                sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                sel.Ids = [b_id]
                new_m.Location = sel
                new_m.Method = MethodType.AllTriAllTet
                b.GenerateMesh()
            except:
                pass
                
            if b.Elements > 0:
                part_log["fixed_with_tet"] += 1
            else:
                part_log["failed"] += 1
                
    results.append(part_log)

# 3. Restore visibility for all bodies
for b in all_bodies:
    b.Visible = True
ExtAPI.Graphics.Redraw()

remaining_unmeshed = [b.Name for b in all_bodies if b.Elements == 0]
final_summary = {
    "total_bodies": len(all_bodies),
    "meshed_count": len(all_bodies) - len(remaining_unmeshed),
    "unmeshed_count": len(remaining_unmeshed),
    "unmeshed_names": remaining_unmeshed,
    "total_nodes": mesh.Nodes,
    "total_elements": mesh.Elements,
    "part_logs": results
}

json.dumps(final_summary)
"""
    t0 = time.time()
    res = app.run_python_script(script)
    elapsed = time.time() - t0
    data = json.loads(res)
    data["elapsed_total_seconds"] = round(elapsed, 2)
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    finish_meshing()
