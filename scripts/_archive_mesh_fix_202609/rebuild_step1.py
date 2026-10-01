import json
import ansys.mechanical.core as mech

def rebuild_step1_1x1_automesh():
    app = mech.Mechanical(port=10000)
    script = """
import json

model = ExtAPI.DataModel.Project.Model
mesh = model.Mesh
geo = model.Geometry

# 1. Clear all existing mesh controls and folders safely
children_to_delete = []
for child in mesh.Children:
    children_to_delete.append(child)

for child in children_to_delete:
    try:
        child.Delete()
    except:
        pass

# 2. Get all 114 bodies (strictly preserve any suppressed state)
all_bodies = geo.GetChildren(DataModelObjectCategory.Body, True)

sheet_bodies = []
pcba_bodies = []
complex_bodies = []

pcba_keywords = ["BACKPLANE", "MIDPLANE", "PCBA", "PCB", "NIC_V3_SFF"]

for b in all_bodies:
    body_type_str = ""
    try:
        if b.GetGeoBody() is not None:
            body_type_str = str(b.GetGeoBody().BodyType)
    except:
        pass
        
    if "Sheet" in body_type_str:
        sheet_bodies.append(b)
    else:
        is_pcba = False
        for kw in pcba_keywords:
            if kw.lower() in b.Name.lower():
                is_pcba = True
                break
        if is_pcba:
            pcba_bodies.append(b)
        else:
            complex_bodies.append(b)

# 3. Create 1x1 (one geometry, one method, one sizing) strictly following MECH_AutoMesh logic
created_methods = 0
created_sizings = 0

# Helper to create SelectionInfo for single body
def create_single_body_selection(body):
    sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    sel.Ids = [body.GetGeoBody().Id]
    return sel

# A. Shell Bodies (Sheet): Prime Method + 3.0mm Body Sizing
for b in sheet_bodies:
    # 1 Method
    m = mesh.AddAutomaticMethod()
    m.Location = create_single_body_selection(b)
    m.Method = MethodType.Prime
    m.Name = "PrimeMethod_" + b.Name
    created_methods += 1
    
    # 1 Sizing
    s = mesh.AddSizing()
    s.Location = create_single_body_selection(b)
    s.ElementSize = Quantity("3.0 [mm]")
    s.Name = "Sizing_" + b.Name
    created_sizings += 1

# B. PCBA Solids: MultiZone Method + 1.5mm Body Sizing
for b in pcba_bodies:
    # 1 Method
    m = mesh.AddAutomaticMethod()
    m.Location = create_single_body_selection(b)
    m.Method = MethodType.MultiZone
    m.Name = "MultiZone_" + b.Name
    created_methods += 1
    
    # 1 Sizing
    s = mesh.AddSizing()
    s.Location = create_single_body_selection(b)
    s.ElementSize = Quantity("1.5 [mm]")
    s.Name = "Sizing_" + b.Name
    created_sizings += 1

# C. Complex Solids: AllTriAllTet Method + 2.0mm Body Sizing
for b in complex_bodies:
    # 1 Method
    m = mesh.AddAutomaticMethod()
    m.Location = create_single_body_selection(b)
    m.Method = MethodType.AllTriAllTet
    m.Name = "TetMethod_" + b.Name
    created_methods += 1
    
    # 1 Sizing
    s = mesh.AddSizing()
    s.Location = create_single_body_selection(b)
    s.ElementSize = Quantity("2.0 [mm]")
    s.Name = "Sizing_" + b.Name
    created_sizings += 1

# 4. Verify 100% validity of newly created controls (Check for ? or invalid states)
question_mark_controls = []
invalid_controls = []

for child in mesh.Children:
    state = str(getattr(child, "ObjectState", getattr(child, "State", "Unknown")))
    name = child.Name
    if "?" in name or "UnderDefined" in state or "Invalid" in state:
        question_mark_controls.append((name, state))

summary = {
    "total_bodies": len(all_bodies),
    "sheet_bodies_count": len(sheet_bodies),
    "pcba_bodies_count": len(pcba_bodies),
    "complex_bodies_count": len(complex_bodies),
    "created_methods": created_methods,
    "created_sizings": created_sizings,
    "total_created_controls": created_methods + created_sizings,
    "current_mesh_children": len(mesh.Children),
    "question_mark_count": len(question_mark_controls),
    "question_marks": question_mark_controls
}

json.dumps(summary)
"""
    res = app.run_python_script(script)
    data = json.loads(res)
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    rebuild_step1_1x1_automesh()
