---
name: pymechanical-operations
description: >-
  PyMechanical gRPC 連線、遠端腳本執行、幾何 Scoping、Mesh 控制自動化的實戰知識。
  當需要透過 PyMechanical 連線 Mechanical 進行自動化操作時載入此 skill。
keywords: PyMechanical, gRPC, connect_to_mechanical, run_python_script, SelectionManager, Scoping, Mesh, Sizing, MultiZone, GenerateMesh
---

# PyMechanical 遠端操作 (實戰知識)

本 skill 來自實際 session 中透過 PyMechanical gRPC 連線 Mechanical
並執行 Mesh 自動化的經驗總結。

---

## 1. gRPC 連線

### 1.1 基本連線

```python
import ansys.mechanical.core as pymech

# 連線到已開啟的 Mechanical (預設 port 10000)
mc = pymech.connect_to_mechanical(port=10000)
print(mc)  # 顯示連線資訊
```

### 1.2 多 Mechanical 視窗情境

Workbench 可同時開啟多個 Mechanical 視窗（如 Static Structural + LS-DYNA），
每個視窗有獨立的 gRPC port。

```python
# Static Structural 通常在 port 10000
mc_static = pymech.connect_to_mechanical(port=10000)

# LS-DYNA 可能在 port 10001 或其他
mc_lsdyna = pymech.connect_to_mechanical(port=10001)
```

**注意**: 無法從外部直接偵測哪個 port 對應哪個 Analysis System，
需要連線後執行腳本確認。

### 1.3 SpaceClaim 連線 (PyGeometry)

```python
from ansys.geometry.core import Modeler

m = Modeler(port=50051, transport_mode='insecure')
design = m.read_existing_design()
```

---

## 2. 遠端腳本執行

### 2.1 `run_python_script()`

```python
result = mc.run_python_script("""
Model = DataModel.Project.Model
mesh = Model.Mesh
print("Mesh nodes:", mesh.Nodes)
""")
print(result)
```

### 2.2 腳本環境差異

在 `run_python_script()` 環境中：
- `ExtAPI`, `DataModel`, `Model` 等全域變數已預設可用
- `__name__` 是 `"<string>"`，不是 `"__main__"`
- 不能使用 `import` 載入外部 .py 檔案（除非在 sys.path 中）
- `print()` 的輸出會被捕獲為回傳值

---

## 3. 幾何 Scoping API

### 3.1 建立 SelectionInfo 並指定 Body ID

這是 Mesh 控制（Sizing / Method）Scoping 的標準模式：

```python
from Ansys.ACT.Interfaces.Common import SelectionTypeEnum

# 建立選取資訊物件
sel = ExtAPI.SelectionManager.CreateSelectionInfo(
    SelectionTypeEnum.GeometryEntities
)

# 指定 Body ID（從 GeoData 取得）
sel.Ids = [body_id]  # 陣列形式

# 套用到 Mesh 控制
sizing.Location = sel
method.Location = sel
```

### 3.2 從 GeoData 取得 Body ID

```python
geo_data = ExtAPI.DataModel.GeoData

for assembly in geo_data.Assemblies:
    for part in assembly.Parts:
        for body in part.Bodies:
            if not body.Suppressed:
                body_type = body.BodyType.ToString()
                # "GeoBodySolid" = 實體, "GeoBodySheet" = 薄殼
                print(body.Name, body.Id, body_type)
```

### 3.3 備用方式：從 DataModel Tree 取得

```python
from Ansys.Mechanical.DataModel.Enums import DataModelObjectCategory

model = ExtAPI.DataModel.Project.Model
bodies = model.Geometry.GetChildren(
    DataModelObjectCategory.Body, True  # True = 遞迴搜尋
)
for b in bodies:
    geo_body = b.GetGeoBody()
    if geo_body:
        print(b.Name, geo_body.Id, geo_body.BodyType)
```

---

## 4. Mesh 控制自動化

### 4.1 Body Sizing

```python
mesher = Model.Mesh
sizing = mesher.AddSizing()
sizing.Name = "Body Sizing (2.0 mm)"
sizing.Location = sel  # SelectionInfo
sizing.ElementSize = Quantity("2.0 [mm]")
sizing.CaptureCurvature = False
```

### 4.2 Mesh Method (MultiZone / Sweep)

```python
from Ansys.Mechanical.DataModel.Enums import MethodType

method = mesher.AddAutomaticMethod()
method.Name = "Solid Mesh Method (MultiZone)"
method.Location = sel

# MultiZone
method.Method = MethodType.MultiZone
try:
    method.SurfaceMeshMethod = 1  # Program Controlled
except Exception:
    pass

# 或 Sweep
method.Method = MethodType.Sweep
method.FreeFaceMeshType = 2
```

### 4.3 Edge Sizing + Washer (孔洞控制)

```python
from Ansys.Mechanical.DataModel.Enums import SizingType, SizingBehavior

# Edge Sizing
edge_sizing = mesher.AddSizing()
edge_sizing.Location = edge_sel
edge_sizing.Type = SizingType.ElementSize
edge_sizing.ElementSize = Quantity("1.5 [mm]")
edge_sizing.Behavior = SizingBehavior.Hard

# Washer
washer = mesher.AddWasher()
washer.Location = edge_sel
washer.NumberOfWasherLayers = 1
```

### 4.4 GenerateMesh()

```python
import time
start = time.time()
mesher.GenerateMesh()
print("Mesh generated in {:.2f}s".format(time.time() - start))
```

### 4.5 Transaction 批次操作

```python
from Ansys.ACT.Automation.Mechanical import Transaction

with Transaction(True):
    # 所有 Mesh 控制操作在同一 Transaction 內
    sizing = mesher.AddSizing()
    method = mesher.AddAutomaticMethod()
    # ... 其他控制
# Transaction 結束時自動 Commit
```

---

## 5. 已驗證的完整工作流程

### AutoMesh 自動化流程（來自 MECH_AutoMesh.py）

1. 遍歷 `GeoData.Assemblies > Parts > Bodies`
2. 分類 Solid (`GeoBodySolid`) 和 Shell (`GeoBodySheet`)
3. 為 Solid 建立 Body Sizing (2.0mm) + MultiZone Method
4. 為 Shell 建立 Body Sizing (3.0mm) + QuadTri Method
5. 搜尋 Named Selection 中的孔洞邊緣
6. 為孔洞建立 Edge Sizing (1.5mm) + Washer (1 layer)
7. 執行 `GenerateMesh()`

參考實作: `d:\Ikaros\ACT_Test\scratch\apply_automesh_act.py`

---

## 6. 常見問題

| 問題 | 原因 | 解法 |
|---|---|---|
| Sizing/Method 出現 ❓ 黃色圖示 | `Location` 未設定或 Scoping 為空 | 確保 `sel.Ids` 包含有效 Body ID |
| `Quantity` 未定義 | 缺少 import | `from Ansys.Core.Units import Quantity` |
| `SelectionTypeEnum` 未定義 | 缺少 import | `from Ansys.ACT.Interfaces.Common import SelectionTypeEnum` |
| 無法連線 gRPC | Port 錯誤或 Mechanical 未啟動 | 確認 port 與 Mechanical 視窗對應 |
