import json
import time
import ansys.mechanical.core as mech

def run_step3():
    app = mech.Mechanical(port=10000)
    script = """
import json

model = ExtAPI.DataModel.Project.Model
mesh = model.Mesh
geo = model.Geometry

all_bodies = geo.GetChildren(DataModelObjectCategory.Body, True)

# Group bodies by their parent Part
part_map = {}
for b in all_bodies:
    p_name = b.Parent.Name.strip() if b.Parent is not None else "Unassigned"
    if p_name not in part_map:
        part_map[p_name] = []
    part_map[p_name].append(b)

# Helper to find method control for a specific body
def get_body_method(body):
    for child in mesh.Children:
        if child.DataModelObjectCategory == DataModelObjectCategory.TreeGroupingFolder:
            for c in child.Children:
                if "Method" in str(c.DataModelObjectCategory) or "MultiZone" in c.Name or "QuadTri" in c.Name:
                    if hasattr(c, "Location") and c.Location is not None:
                        if body.GetGeoBody().Id in list(c.Location.Ids):
                            return c
    return None

part_results = {}
total_fixed_by_fallback = 0

for part_name, bodies in part_map.items():
    part_stat = {
        "total": len(bodies),
        "initial_success": 0,
        "failed_initially": 0,
        "fixed": 0,
        "remaining_failed": 0,
        "failed_bodies": []
    }
    
    # 1. Generate mesh for bodies in this part
    for b in bodies:
        try:
            b.GenerateMesh()
        except:
            pass
            
    # 2. Check and handle any failed bodies in this part
    for b in bodies:
        if b.Elements > 0:
            part_stat["initial_success"] += 1
        else:
            part_stat["failed_initially"] += 1
            part_stat["failed_bodies"].append(b.Name)
            
            # Individual error recovery: fallback to AllTriAllTet
            m = get_body_method(b)
            if m is not None:
                try:
                    m.Method = MethodType.AllTriAllTet
                    b.GenerateMesh()
                except:
                    pass
                    
            if b.Elements > 0:
                part_stat["fixed"] += 1
                total_fixed_by_fallback += 1
            else:
                # Second fallback: micro size adjustment
                try:
                    sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                    sel.Ids = [b.GetGeoBody().Id]
                    ls = mesh.AddSizing()
                    ls.Location = sel
                    ls.ElementSize = Quantity("1.5 [mm]")
                    b.GenerateMesh()
                except:
                    pass
                if b.Elements > 0:
                    part_stat["fixed"] += 1
                    total_fixed_by_fallback += 1
                else:
                    part_stat["remaining_failed"] += 1

    part_results[part_name] = part_stat

# Final global verification
unmeshed = [b.Name for b in all_bodies if b.Elements == 0]

summary = {
    "total_bodies": len(all_bodies),
    "unmeshed_count": len(unmeshed),
    "unmeshed_names": unmeshed,
    "total_fixed_by_fallback": total_fixed_by_fallback,
    "mesh_nodes": mesh.Nodes,
    "mesh_elements": mesh.Elements,
    "part_results": part_results
}

json.dumps(summary)
"""
    t0 = time.time()
    res = app.run_python_script(script)
    elapsed = time.time() - t0
    data = json.loads(res)
    data["elapsed_seconds"] = round(elapsed, 2)
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    run_step3()
