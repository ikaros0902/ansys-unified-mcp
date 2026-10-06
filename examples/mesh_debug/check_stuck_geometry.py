import json
import ansys.mechanical.core as mech

def check_stuck():
    try:
        app = mech.Mechanical(port=10000)
        script = """
import json

model = ExtAPI.DataModel.Project.Model
mesh = model.Mesh
geo = model.Geometry

all_bodies = geo.GetChildren(DataModelObjectCategory.Body, True)

meshed_bodies = []
unmeshed_bodies = []

for b in all_bodies:
    p_name = b.Parent.Name.strip() if b.Parent is not None else "Unassigned"
    body_type_str = ""
    try:
        if b.GetGeoBody() is not None:
            body_type_str = str(b.GetGeoBody().BodyType)
    except:
        pass
    
    info = {
        "Name": b.Name,
        "Parent": p_name,
        "BodyType": body_type_str,
        "Elements": b.Elements,
        "Nodes": b.Nodes
    }
    
    if b.Elements > 0:
        meshed_bodies.append(info)
    else:
        unmeshed_bodies.append(info)

# Check messages
messages = []
try:
    for m in ExtAPI.DataModel.Messages:
        messages.append({
            "Severity": str(m.Severity),
            "Text": m.Text
        })
except:
    pass

summary = {
    "total_bodies": len(all_bodies),
    "meshed_count": len(meshed_bodies),
    "unmeshed_count": len(unmeshed_bodies),
    "unmeshed_list": unmeshed_bodies,
    "recent_messages": messages[-10:] if messages else []
}

json.dumps(summary)
"""
        res = app.run_python_script(script)
        data = json.loads(res)
        print(json.dumps(data, indent=2))
    except Exception as e:
        print("Error checking stuck geometry:", e)

if __name__ == "__main__":
    check_stuck()
