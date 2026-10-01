import json
import ansys.mechanical.core as mech

def test_single_tet_meshing():
    app = mech.Mechanical(port=10000)
    script = """
import json

model = ExtAPI.DataModel.Project.Model
mesh = model.Mesh
geo = model.Geometry

# Find the first solid body in 1F-FRONT-END-GDZ
target_body = None
for b in geo.GetChildren(DataModelObjectCategory.Body, True):
    if "1F-FRONT-END-GDZ" in b.Name and "Solid" in str(getattr(b.GetGeoBody(), "BodyType", "")):
        target_body = b
        break

res = {"target_name": target_body.Name if target_body else None}

if target_body is not None:
    # Find its method control
    target_method = None
    for child in mesh.Children:
        if child.DataModelObjectCategory == DataModelObjectCategory.TreeGroupingFolder:
            for c in child.Children:
                if hasattr(c, "Location") and c.Location is not None:
                    if target_body.GetGeoBody().Id in list(c.Location.Ids):
                        target_method = c
                        break
                        
    if target_method is not None:
        target_method.Method = MethodType.AllTriAllTet
        res["method_changed_to"] = "AllTriAllTet"
        
    target_body.GenerateMesh()
    res["elements"] = target_body.Elements
    res["nodes"] = target_body.Nodes

json.dumps(res)
"""
    res = app.run_python_script(script)
    print(res)

if __name__ == "__main__":
    test_single_tet_meshing()
