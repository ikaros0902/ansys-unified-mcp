import json
import ansys.mechanical.core as mech

def reset_to_multizone():
    app = mech.Mechanical(port=10000)
    script = """
import json

def run_reset():
    report = {
        "status": "success",
        "folders_processed": 0,
        "multizone_solid_count": 0,
        "multizone_sheet_count": 0,
        "retained_sizing_count": 0,
        "ungrouped_count": 0,
        "details": {},
        "errors": []
    }
    
    try:
        model = ExtAPI.DataModel.Project.Model
        mesh = model.Mesh
        geo = model.Geometry
        
        all_bodies = geo.GetChildren(DataModelObjectCategory.Body, True)
        
        target_folders = []
        for child in list(mesh.Children):
            if child.DataModelObjectCategory == DataModelObjectCategory.TreeGroupingFolder:
                if child.Name.strip() != "1F-FRONT-END-GDZ":
                    target_folders.append(child)
                    
        with Transaction(True):
            for folder in target_folders:
                folder_name = folder.Name
                folder_clean = folder_name.strip()
                folder_children = list(folder.Children)
                
                retained_sizings = []
                old_methods = []
                
                for item in folder_children:
                    cat = item.DataModelObjectCategory
                    if cat == DataModelObjectCategory.Sizing:
                        retained_sizings.append(item)
                    elif cat == DataModelObjectCategory.AutomaticMethod:
                        old_methods.append(item)
                        
                # Delete existing methods
                for om in old_methods:
                    try:
                        om.Delete()
                    except Exception as e_del:
                        report["errors"].append("Delete error in {0}: {1}".format(folder_name, str(e_del)))
                        
                # Directly get all bodies belonging to this part/folder
                associated_bodies = [b for b in all_bodies if b.Parent and b.Parent.Name.strip() == folder_clean]
                
                new_methods = []
                solid_cnt = 0
                sheet_cnt = 0
                
                for b in associated_bodies:
                    try:
                        geobody = b.GetGeoBody()
                        if geobody is None:
                            continue
                        btype = geobody.BodyType.ToString()
                        
                        sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                        sel.Ids = [geobody.Id]
                        
                        method = mesh.AddAutomaticMethod()
                        method.Location = sel
                        method.Method = MethodType.MultiZone
                        
                        clean_body_name = b.Name.replace("\\\\", "_").replace("/", "_")
                        if "Sheet" in btype:
                            method.Name = "MZ_QuadTri_{0}_{1}".format(folder_clean, clean_body_name)
                            sheet_cnt += 1
                        else:
                            method.Name = "MultiZone_{0}_{1}".format(folder_clean, clean_body_name)
                            solid_cnt += 1
                            
                        new_methods.append(method)
                    except Exception as e_m:
                        report["errors"].append("Create method error for {0}: {1}".format(b.Name, str(e_m)))
                        
                all_folder_controls = retained_sizings + new_methods
                report["multizone_solid_count"] += solid_cnt
                report["multizone_sheet_count"] += sheet_cnt
                report["retained_sizing_count"] += len(retained_sizings)
                
                report["details"][folder_clean] = {
                    "solids": solid_cnt,
                    "sheets": sheet_cnt,
                    "sizings": len(retained_sizings)
                }
                
                try:
                    if all_folder_controls:
                        folder.Ungroup()
                        new_f = ExtAPI.DataModel.Tree.Group(all_folder_controls)
                        new_f.Name = folder_name
                        report["folders_processed"] += 1
                except Exception as e_grp:
                    report["errors"].append("Regroup error for {0}: {1}".format(folder_name, str(e_grp)))
                    
        # Verify stray controls
        all_f = [c for c in mesh.Children if c.DataModelObjectCategory == DataModelObjectCategory.TreeGroupingFolder]
        grouped_ids = set()
        for f in all_f:
            for c in f.Children:
                grouped_ids.add(c.ObjectId)
                
        for c in mesh.Children:
            if c.DataModelObjectCategory != DataModelObjectCategory.TreeGroupingFolder:
                if c.ObjectId not in grouped_ids:
                    report["ungrouped_count"] += 1
                    
        # Collapse tree to level 2
        try:
            th = ExtAPI.DataModel.Tree.GetTreeHandler()
            th.CollapseToLevel(2)
        except:
            pass
            
    except Exception as e_global:
        report["status"] = "error"
        report["errors"].append("Global exception: {0}".format(str(e_global)))
        
    return json.dumps(report)

output = run_reset()
json.dumps(output)
"""
    res = app.run_python_script(script)
    data = json.loads(res)
    if isinstance(data, str):
        data = json.loads(data)
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    reset_to_multizone()
