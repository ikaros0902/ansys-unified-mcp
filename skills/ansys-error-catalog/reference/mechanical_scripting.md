# Mechanical Scripting 錯誤紀錄

---

## ERR-MECH-001: Mesh Sizing/Method 出現 ❓ 黃色警告圖示

**觸發場景**: 透過 PyMechanical 腳本建立 `AddSizing()` 或 `AddAutomaticMethod()` 後，
Mechanical Tree 中該控制項顯示黃色 ❓ 圖示（Under Defined）。

**根因**: `Location` 屬性未設定，或設定的 `SelectionInfo.Ids` 為空陣列。
Mesh 控制必須有明確的 Scoping 才能生效。

**解決方案**:
```python
from Ansys.ACT.Interfaces.Common import SelectionTypeEnum

sel = ExtAPI.SelectionManager.CreateSelectionInfo(
    SelectionTypeEnum.GeometryEntities
)
sel.Ids = [body_id]  # 必須包含有效的 GeoBody ID

sizing.Location = sel
method.Location = sel
```

**驗證**: 設定後檢查 `sizing.Location` 是否非 None，且 Tree 圖示變為 ✓。
phase_gate:
  requires: []
  produces: []
---

## ERR-MECH-002: `Quantity` 未定義

**觸發場景**: 在 PyMechanical `run_python_script()` 中使用 `Quantity("5.0 [mm]")`
但收到 `NameError: name 'Quantity' is not defined`。

**根因**: `Quantity` 不是 Mechanical 環境的預設全域變數，需要明確 import。

**解決方案**:
```python
from Ansys.Core.Units import Quantity
sizing.ElementSize = Quantity("5.0 [mm]")
```

---

## ERR-MECH-003: `SelectionTypeEnum` 未定義

**觸發場景**: 在 PyMechanical 腳本中使用 `SelectionTypeEnum.GeometryEntities`
但收到 `NameError`。

**根因**: 需要明確 import。

**解決方案**:
```python
from Ansys.ACT.Interfaces.Common import SelectionTypeEnum
```

---

## ERR-MECH-004: gRPC 連線失敗 (Connection Refused)

**觸發場景**: 使用 `pymech.connect_to_mechanical(port=10000)` 但連線被拒。

**可能根因**:
1. Mechanical 尚未完全啟動（需等待 GUI 完全載入）
2. Port 被佔用或 Mechanical 使用了不同的 port
3. Mechanical 未啟用 gRPC server（需透過 ACT 插件啟動）

**解決方案**:
```python
import ansys.mechanical.core as pymech

# 嘗試多個 port
for port in [10000, 10001, 10002]:
    try:
        mc = pymech.connect_to_mechanical(port=port)
        print(f"Connected on port {port}")
        break
    except Exception:
        continue
```

---

## ERR-MECH-005: `run_python_script` 中 `__name__` 不是 `"__main__"`

**觸發場景**: 腳本底部使用 `if __name__ == "__main__":` guard，
透過 PyMechanical 執行時 main block 不會被執行。

**根因**: PyMechanical `run_python_script()` 中 `__name__` 是 `"<string>"`。

**解決方案**: 直接在腳本底部呼叫入口函式，不使用 `__name__` guard：

```python
def main():
    # 主要邏輯
    pass

# 直接呼叫，不用 if __name__ == "__main__"
main()
```

---

## ERR-MECH-006: `Transaction` 未定義或 import 失敗

**觸發場景**: 在 PyMechanical 腳本中使用 `with Transaction(True):` 但 import 失敗。

**解決方案**: 加上 fallback 空實作：

```python
try:
    from Ansys.ACT.Automation.Mechanical import Transaction
except ImportError:
    class Transaction(object):
        def __init__(self, flag):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
```

---

## ERR-MECH-007: 多 Mechanical 視窗無法區分 (Static Structural vs LS-DYNA)

**觸發場景**: Workbench 同時開啟 Static Structural 和 LS-DYNA 兩個 Mechanical 視窗，
PyMechanical gRPC 連線到其中一個但無法確定是哪個。

**根因**: PyMechanical `connect_to_mechanical()` 只接受 port 參數，
無法直接指定 Analysis System 類型。

**解決方案**: 連線後執行探測腳本確認：

```python
result = mc.run_python_script("""
analysis = DataModel.Project.Model.Analyses[0]
print(analysis.AnalysisType.ToString())
print(analysis.Solver.Name)
""")
# 根據回傳判斷是 Static Structural 還是 LS-DYNA
```

---

## ERR-MECH-008: ACT DataModel 物件缺少 `Id` 屬性

**觸發場景**: 嘗試讀取網格控制項（如 `AutomaticMethod`、`Sizing`）的 `.Id`。
**錯誤訊息**: `AttributeError: 'AutomaticMethod' object has no attribute 'Id'`。
**根因**: 幾何實體核心才具備 `.Id`（如 `GeoBody.Id`、`GeoFace.Id`），ACT DataModel 物件樹之識別符為 `.ObjectId`。
**解決方案**: 識別樹中物件唯一性一律使用 `.ObjectId`：
```python
grouped_ids = set([item.ObjectId for item in folder.Children])
```

---

## ERR-MECH-009: `MethodType` 枚舉缺少 `QuadTri`

**觸發場景**: 對 Sheet Body 設定面網格時嘗試指派 `method.Method = MethodType.QuadTri`。
**錯誤訊息**: `AttributeError: type object 'MethodType' has no attribute 'QuadTri'`。
**根因**: ANSYS Mechanical ACT 中薄板若要使用 MultiZone Quad/Tri，枚舉值依然是 `MethodType.MultiZone`，底層視對象為 Sheet 會自動處理為面網格。
**解決方案**: Solid 與 Sheet 一律統一使用 `MethodType.MultiZone`：
```python
method.Method = MethodType.MultiZone
```

---

## ERR-MECH-010: `MeshData` 物件層級存取錯誤

**觸發場景**: 嘗試直接透過 `ExtAPI.DataModel.MeshData` 讀取網格資料庫。
**錯誤訊息**: `AttributeError: 'MechanicalDataModel' object has no attribute 'MeshData'`。
**根因**: `MeshData` 附屬於 `Mesh` 物件層級下，正確路徑為 `ExtAPI.DataModel.Project.Model.Mesh.MeshData` 或 `mesh.MeshData`。
**解決方案**: 
```python
mesh_data = ExtAPI.DataModel.Project.Model.Mesh.MeshData
region = mesh_data.MeshRegionById(geo_body.Id)
node_count = region.NodeCount if region else 0
```

---

## ERR-MECH-011: 動態新建網格控制項游離於樹狀目錄外

**觸發場景**: 透過 `mesh.AddAutomaticMethod()` 或 `mesh.AddSizing()` 動態新建控制項時，物件暴露在 Model Tree 根目錄外。
**根因**: ACT API 新建物件之預設 Parent 為 `Mesh`，若未顯式納入資料夾，會破壞 Model Tree 資料夾結構。
**解決方案**: 新建控制項後，立即呼叫資料夾歸類指令：
```python
new_method = mesh.AddAutomaticMethod()
# 收納入對應資料夾
folder.AddObject(new_method)
# 或重新 Group
ExtAPI.DataModel.Tree.Group(folder_controls)
```

