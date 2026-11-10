# 幾何 Scoping 與 Mesh 控制自動化 (scoping_and_mesh.md)

本手冊說明如何使用 Mechanical ACT API 操作 `SelectionInfo` 進行幾何 Scoping，並自動化指派 Sizing 與 Mesh Method。

---

## 1. 建立 SelectionInfo 與指定 Body ID

```python
from Ansys.ACT.Interfaces.Common import SelectionTypeEnum
from Ansys.Core.Units import Quantity

sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
sel.Ids = [body_id]  # 指定實體 ID 陣列
```

從 `GeoData` 提取 Body ID：
```python
geo_data = ExtAPI.DataModel.GeoData
for assembly in geo_data.Assemblies:
    for part in assembly.Parts:
        for body in part.Bodies:
            if not body.Suppressed:
                print(body.Name, body.Id, body.BodyType.ToString())
```

---

## 2. Mesh 控制自動化

```python
mesher = Model.Mesh

# 1. Body Sizing
sizing = mesher.AddSizing()
sizing.Name = "Body Sizing (2.0 mm)"
sizing.Location = sel
sizing.ElementSize = Quantity("2.0 [mm]")

# 2. MultiZone Method
from Ansys.Mechanical.DataModel.Enums import MethodType
method = mesher.AddAutomaticMethod()
method.Name = "Solid MultiZone Method"
method.Location = sel
method.Method = MethodType.MultiZone

# 3. 觸發網格生成
mesher.GenerateMesh()
```
