import json
import ansys.mechanical.core as mech

def organize_and_collapse_tree():
    app = mech.Mechanical(port=10000)
    script = """
import json

model = ExtAPI.DataModel.Project.Model
mesh = model.Mesh
geo = model.Geometry

# 1. Ensure all 114 bodies are 100% VISIBLE
all_bodies = geo.GetChildren(DataModelObjectCategory.Body, True)
for b in all_bodies:
    b.Visible = True
ExtAPI.Graphics.Redraw()

# 2. Fix the lone Tet control outside folders into Component1 folder
lone_control = None
comp1_folder = None

for child in list(mesh.Children):
    if child.Name == "Tet_Component1\\\\PDB_STANDOFF_GDZ1":
        lone_control = child
    elif child.DataModelObjectCategory == DataModelObjectCategory.TreeGroupingFolder and child.Name == "Component1":
        comp1_folder = child

msg = ""
if lone_control is not None and comp1_folder is not None:
    # Regroup all controls in Component1 plus this lone control
    all_comp1_controls = list(comp1_folder.Children)
    all_comp1_controls.append(lone_control)
    comp1_folder.Ungroup()
    new_folder = ExtAPI.DataModel.Tree.Group(all_comp1_controls)
    new_folder.Name = "Component1"
    msg = "Successfully moved lone control into Component1 folder!"
elif lone_control is None:
    msg = "Lone control already inside folder."

# 3. Collapse the entire Model Tree cleanly
try:
    th = ExtAPI.DataModel.Tree.GetTreeHandler()
    th.CollapseToLevel(2)
    collapse_status = "Tree collapsed to level 2"
except Exception as e:
    collapse_status = "Collapse error: " + str(e)

# Summary of top-level children under Mesh
mesh_top_items = []
for c in mesh.Children:
    mesh_top_items.append((c.Name, str(c.DataModelObjectCategory)))

res = {
    "msg": msg,
    "collapse_status": collapse_status,
    "mesh_top_count": len(mesh_top_items),
    "mesh_top_items": mesh_top_items,
    "all_bodies_visible": all(b.Visible for b in all_bodies)
}
json.dumps(res)
"""
    res = app.run_python_script(script)
    data = json.loads(res)
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    organize_and_collapse_tree()
