import json
import ansys.mechanical.core as mech

def check_current_mesh_setup():
    app = mech.Mechanical(port=10000)
    script = """
import json

model = ExtAPI.DataModel.Project.Model
mesh = model.Mesh

controls_info = []
question_mark_controls = []
duplicate_scoping = {}

for child in mesh.Children:
    cat = str(child.DataModelObjectCategory)
    name = child.Name
    state = str(getattr(child, "ObjectState", getattr(child, "State", "Unknown")))
    
    # Check if there is ? in name or state is not fully defined
    has_question_mark = "?" in name or "UnderDefined" in state or "Invalid" in state
    
    # Get scoping info if available
    scoped_ids = []
    if hasattr(child, "Location") and child.Location is not None:
        try:
            scoped_ids = list(child.Location.Ids)
        except:
            pass
            
    info = {
        "Name": name,
        "Category": cat,
        "State": state,
        "HasQuestionMark": has_question_mark,
        "ScopedCount": len(scoped_ids),
        "ScopedIdsSample": scoped_ids[:5]
    }
    controls_info.append(info)
    if has_question_mark:
        question_mark_controls.append(name)
        
    scope_key = tuple(sorted(scoped_ids))
    if scope_key and len(scope_key) > 0:
        if scope_key not in duplicate_scoping:
            duplicate_scoping[scope_key] = []
        duplicate_scoping[scope_key].append((name, cat))

duplicates = {}
for k, v in duplicate_scoping.items():
    if len(v) > 1:
        # Check if they are duplicate method on same bodies or duplicate sizing on same bodies
        categories = [item[1] for item in v]
        if len(categories) != len(set(categories)):
            duplicates[str(k[:3]) + "..."] = v

all_bodies = model.Geometry.GetChildren(DataModelObjectCategory.Body, True)
meshed_count = sum(1 for b in all_bodies if b.Elements > 0)

summary = {
    "total_controls": len(controls_info),
    "question_mark_count": len(question_mark_controls),
    "question_mark_names": question_mark_controls,
    "duplicates_count": len(duplicates),
    "duplicates_details": duplicates,
    "total_bodies": len(all_bodies),
    "meshed_bodies": meshed_count,
    "mesh_nodes": mesh.Nodes,
    "mesh_elements": mesh.Elements,
    "controls_list": controls_info
}

json.dumps(summary)
"""
    res = app.run_python_script(script)
    try:
        data = json.loads(res)
        print(json.dumps(data, indent=2))
    except Exception as e:
        print("Raw result:", repr(res))

if __name__ == "__main__":
    check_current_mesh_setup()
