# encoding: utf-8
# ANSYS Mechanical Python Script: LS-DYNA Mesh 5mm MultiZone
import traceback

def apply_lsdyna_mesh_direct():
    model = ExtAPI.DataModel.Project.Model
    mesh = model.Mesh
    geo = ExtAPI.DataModel.GeoData

    # 1. 取得 SYS\PCB 的 Body Id
    body_ids = []
    if geo.Assemblies.Count > 0:
        for p in geo.Assemblies[0].Parts:
            for b in p.Bodies:
                body_ids.append(b.Id)
    print("Selecting Body IDs:", body_ids)

    sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    sel.Ids = body_ids

    # 2. 清理現有舊控制項
    for child in list(mesh.Children):
        if "Sizing" in child.Name or "Method" in child.Name:
            try:
                child.Delete()
            except Exception:
                pass

    # 3. 新增 Sizing (5mm) 並綁定 Location
    sizing = mesh.AddSizing()
    sizing.Name = "Body Mesh Sizing (5mm)"
    sizing.Location = sel
    try:
        sizing.ElementSize = Quantity("5 [mm]")
    except Exception:
        sizing.ElementSize = 0.005
    print("Created Body Sizing (5mm)")

    # 4. 新增 MultiZone Method 並綁定 Location
    method = mesh.AddAutomaticMethod()
    method.Name = "MultiZone Method"
    method.Location = sel
    method.Method = MethodType.MultiZone
    print("Created MultiZone Method")

    # 5. 重新劃分網格 (Generate Mesh)
    mesh.GenerateMesh()
    print("SUCCESS: LS-DYNA 5mm MultiZone Mesh Generated!")

try:
    apply_lsdyna_mesh_direct()
except Exception as e:
    print("Error: " + str(e))
    print(traceback.format_exc())
