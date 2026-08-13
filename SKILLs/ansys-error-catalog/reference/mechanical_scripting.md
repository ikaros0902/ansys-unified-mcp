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
