import json
import time
import ansys.mechanical.core as mech

def run_step1_and_step2():
    app = mech.Mechanical(port=10000)
    script = """
import json

model = ExtAPI.DataModel.Project.Model
mesh = model.Mesh
geo = model.Geometry

# 1. Clear existing mesh controls safely under Transaction
with Transaction(True):
    for child in list(mesh.Children):
        try:
            child.Delete()
        except:
            pass

all_bodies = geo.GetChildren(DataModelObjectCategory.Body, True)

# Group bodies by their parent Part
part_map = {}
for b in all_bodies:
    p_name = b.Parent.Name.strip() if b.Parent is not None else "Unassigned"
    if p_name not in part_map:
        part_map[p_name] = []
    part_map[p_name].append(b)

total_methods = 0
total_sizings = 0
folders_created = []

# Helper to create SelectionInfo for single body
def create_single_body_selection(body):
    sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    sel.Ids = [body.GetGeoBody().Id]
    return sel

# 2. Execute Step 1 (1x1 AutoMesh) and Step 2 (Go to Mesh Controls by Part) under single Transaction
with Transaction(True):
    for part_name, bodies in part_map.items():
        part_controls = []
        for b in bodies:
            body_type_str = ""
            try:
                if b.GetGeoBody() is not None:
                    body_type_str = str(b.GetGeoBody().BodyType)
            except:
                pass
            
            is_sheet = "Sheet" in body_type_str
            
            # Create Method
            m = mesh.AddAutomaticMethod()
            m.Location = create_single_body_selection(b)
            if is_sheet:
                # User specification: Surface set multizone quad/tri
                m.Method = MethodType.QuadTri
                m.Name = "QuadTri_" + b.Name
            else:
                # User specification: Solid set multizone
                m.Method = MethodType.MultiZone
                m.Name = "MultiZone_" + b.Name
            total_methods += 1
            part_controls.append(m)
            
            # Create Sizing
            s = mesh.AddSizing()
            s.Location = create_single_body_selection(b)
            if is_sheet:
                s.ElementSize = Quantity("3.0 [mm]")
            elif any(kw in b.Name.upper() for kw in ["BACKPLANE", "MIDPLANE", "PCBA", "PCB", "NIC_V3_SFF"]):
                s.ElementSize = Quantity("1.5 [mm]")
            else:
                s.ElementSize = Quantity("2.0 [mm]")
            s.Name = "Sizing_" + b.Name
            total_sizings += 1
            part_controls.append(s)
            
        # Step 2: Group controls of this Part into its own TreeGroupingFolder
        if part_controls:
            try:
                folder = ExtAPI.DataModel.Tree.Group(part_controls)
                folder.Name = part_name
                folders_created.append(part_name)
            except:
                pass

# 3. Clean Validation using ObjectState (Zero Warnings in Extension Log)
question_marks = []
for child in mesh.Children:
    state = str(getattr(child, "ObjectState", "Unknown"))
    name = child.Name
    if "?" in name or "UnderDefined" in state or "Invalid" in state:
        question_marks.append((name, state))

summary = {
    "total_bodies": len(all_bodies),
    "total_methods": total_methods,
    "total_sizings": total_sizings,
    "total_controls": total_methods + total_sizings,
    "folders_count": len(folders_created),
    "folders_created": folders_created,
    "question_mark_count": len(question_marks),
    "question_marks": question_marks,
    "mesh_nodes": mesh.Nodes,
    "mesh_elements": mesh.Elements
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
    run_step1_and_step2()
