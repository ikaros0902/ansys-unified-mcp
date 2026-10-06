import json
import time
import ansys.mechanical.core as mech

def run_step3_partition_mesh():
    app = mech.Mechanical(port=10000)
    script = """
import json
import time

def execute_step3_workflow():
    report = {
        "status": "success",
        "partitions_processed": 0,
        "total_bodies": 114,
        "multizone_success": [],
        "fallback_tetra": [],
        "errors": []
    }
    
    model = ExtAPI.DataModel.Project.Model
    mesh = model.Mesh
    geo = model.Geometry
    
    # Access MeshData for objective node-count verification
    mesh_data = ExtAPI.DataModel.MeshData
    all_bodies = geo.GetChildren(DataModelObjectCategory.Body, True)
    
    target_folders = [
        "SM-BASEPAN-GDZ",
        "Rear_wall",
        "SM-FRONT-COVER-GDZ",
        "E1S_CAGE_GDZ",
        "CX7",
        "OCP",
        "DCSCM",
        "PDB",
        "E1_Midplane",
        "TOP-COVER-GDZ",
        "Component1"
    ]
    
    folder_objs = {}
    for c in mesh.Children:
        if c.DataModelObjectCategory == DataModelObjectCategory.TreeGroupingFolder:
            folder_objs[c.Name.strip()] = c
            
    for fname in target_folders:
        if fname not in folder_objs:
            continue
            
        folder = folder_objs[fname]
        folder_bodies = [b for b in all_bodies if b.Parent and b.Parent.Name.strip() == fname]
        if not folder_bodies:
            continue
            
        # Step A: Visual Isolation - Show current partition, hide all others
        for b in all_bodies:
            b.Visible = (b in folder_bodies)
        ExtAPI.Graphics.Redraw()
        
        # Step B & C: Mesh each body in partition
        for b in folder_bodies:
            body_name = b.Name
            geo_body = b.GetGeoBody()
            clean_bname = body_name.replace("\\\\", "_").replace("/", "_")
            
            # Locate existing AutomaticMethod
            target_method = None
            for c in folder.Children:
                if c.DataModelObjectCategory == DataModelObjectCategory.AutomaticMethod:
                    if clean_bname in c.Name or body_name in c.Name:
                        target_method = c
                        break
            if target_method is None and geo_body is not None:
                for c in folder.Children:
                    if c.DataModelObjectCategory == DataModelObjectCategory.AutomaticMethod:
                        try:
                            if c.Location and geo_body.Id in c.Location.Ids:
                                target_method = c
                                break
                        except:
                            pass
                            
            mesh_ok = False
            start_t = time.time()
            
            # First attempt: MultiZone
            try:
                b.GenerateMesh()
                if mesh_data and geo_body:
                    region = mesh_data.MeshRegionById(geo_body.Id)
                    if region and region.NodeCount > 0:
                        mesh_ok = True
            except Exception as e_mesh:
                report["errors"].append("Mesh exception on {0}: {1}".format(body_name, str(e_mesh)))
                mesh_ok = False
                
            elapsed = time.time() - start_t
            
            # Step C: Fallback to AllTriAllTet if MultiZone failed or timed out (>180s)
            if not mesh_ok or elapsed > 180.0:
                try:
                    if target_method is not None:
                        target_method.Method = MethodType.AllTriAllTet
                        target_method.Name = "Tet_{0}_{1}".format(fname, clean_bname)
                    else:
                        target_method = mesh.AddAutomaticMethod()
                        sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                        sel.Ids = [geo_body.Id]
                        target_method.Location = sel
                        target_method.Method = MethodType.AllTriAllTet
                        target_method.Name = "Auto_Tet_{0}_{1}".format(fname, clean_bname)
                        try:
                            folder.AddObject(target_method)
                        except:
                            pass
                            
                    # Second attempt: Retry with Tetra
                    b.GenerateMesh()
                    
                    if mesh_data and geo_body:
                        region = mesh_data.MeshRegionById(geo_body.Id)
                        if region and region.NodeCount > 0:
                            report["fallback_tetra"].append({
                                "folder": fname,
                                "body": body_name,
                                "elapsed_s": round(elapsed, 2),
                                "reason": "MultiZone failed or took > 3mins ({0}s)".format(round(elapsed, 2))
                            })
                        else:
                            report["errors"].append("Retry Tetra produced 0 nodes for {0}".format(body_name))
                except Exception as e_retry:
                    report["errors"].append("Retry Tetra failed for {0}: {1}".format(body_name, str(e_retry)))
            else:
                report["multizone_success"].append({
                    "folder": fname,
                    "body": body_name,
                    "elapsed_s": round(elapsed, 2)
                })
                
        report["partitions_processed"] += 1
        
    # Step D: Final interface cleanup
    # 1. 100% of bodies restored to Visible
    for b in all_bodies:
        b.Visible = True
    ExtAPI.Graphics.Redraw()
    
    # 2. Collapse Model Tree cleanly to level 2
    try:
        th = ExtAPI.DataModel.Tree.GetTreeHandler()
        th.CollapseToLevel(2)
    except:
        pass
        
    report["final_nodes"] = mesh.Nodes
    report["final_elements"] = mesh.Elements
    
    # Objective unmeshed verification
    unmeshed_count = 0
    for b in all_bodies:
        gb = b.GetGeoBody()
        if gb and mesh_data:
            reg = mesh_data.MeshRegionById(gb.Id)
            if not reg or reg.NodeCount == 0:
                unmeshed_count += 1
    report["unmeshed_count"] = unmeshed_count
    
    return json.dumps(report)

output = execute_step3_workflow()
json.dumps(output)
"""
    res = app.run_python_script(script)
    data = json.loads(res)
    if isinstance(data, str):
        data = json.loads(data)
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    run_step3_partition_mesh()
