# IronPython 2.7 通用錯誤紀錄

本文件記錄 ANSYS 環境中 IronPython 2.7 的通用限制與陷阱，
不限於特定模組（Workbench / Mechanical / SpaceClaim）。

---

## ERR-IP-001: `exec` 不能包含閉包 (Closure)

**觸發場景**: 在包含 `exec()` 語句的函式中，同時定義了巢狀函式（nested function）
或 lambda，且巢狀函式引用了外層函式的局部變數。

**錯誤訊息**:
```
SyntaxError: unqualified exec is not allowed in function '...' 
it contains a nested function with free variables
```

**根因**: IronPython 2.7 (以及 CPython 2.x) 限制——若函式內有 `exec`，
則不允許該函式包含帶有 free variables 的巢狀函式，
因為 `exec` 可能修改局部命名空間，使閉包行為不可預測。

**影響範圍**: 所有使用 `exec()` 的 ACT callback、事件處理函式。

**解決方案**:
1. 將需要閉包的邏輯提取為模組層級的 class 或 function
2. 使用 `__call__` 取代 lambda
3. 避免在同一函式中混用 `exec()` 和巢狀函式

```python
# ❌ 觸發錯誤
def handler():
    items = []
    def collect():  # 閉包：引用 items
        items.append(1)
    exec("pass")  # exec 與閉包衝突

# ✅ 解法：提取為類別
class Collector(object):
    def __init__(self):
        self.items = []
    def add(self, val):
        self.items.append(val)

def handler():
    c = Collector()
    exec("pass")
```

---

## ERR-IP-002: `__name__` 在不同執行環境中的值

**觸發場景**: 腳本假設 `__name__ == "__main__"` 來決定是否執行入口函式。

**各環境下 `__name__` 的值**:

| 環境 | `__name__` 值 |
|---|---|
| CPython 直接執行 | `"__main__"` |
| PyMechanical `run_python_script()` | `"<string>"` |
| Workbench Journal `Run Script` | `"__main__"` (有時) |
| ACT callback (`onupdateStep`) | 模組名稱 |
| `exec(script, globals)` | 取決於 `globals["__name__"]` |

**解決方案**: 不要依賴 `__name__` guard，直接在腳本底部呼叫入口函式。

---

## ERR-IP-003: `clr.AddReference()` 重複載入拋出異常

**觸發場景**: 多次呼叫 `clr.AddReference("SameAssembly")`，
若 assembly 已在 AppDomain 中載入，可能拋出異常。

**解決方案**: 統一用 `try/except` 包裝：

```python
try:
    import clr
    clr.AddReference("System")
except Exception:
    pass
```

---

## ERR-IP-004: 模組 `reload()` 在 ACT 環境中的必要性

**觸發場景**: 修改了 ACT 外掛的 Python 模組後，
Workbench 中的行為未更新（仍使用舊版程式碼）。

**根因**: IronPython 模組在首次 `import` 後被快取到 `sys.modules`，
即使檔案已更新，後續的 `import` 不會重新載入。

**解決方案**: 在 `main.py` 的載入點使用 `reload()`：

```python
import wb_event_listener
reload(wb_event_listener)  # 強制重新載入

# 然後使用最新版本
wb_event_listener.start_listener()
```

**注意**: `reload()` 不會更新已經從模組 import 的名稱：

```python
# ❌ 這不會更新 start_listener
from wb_event_listener import start_listener
reload(wb_event_listener)
start_listener()  # 仍是舊版

# ✅ 這會使用最新版本
reload(wb_event_listener)
wb_event_listener.start_listener()  # 最新版
```

---

## ERR-IP-005: `print` 在 ACT/Workbench 環境中的行為差異

**觸發場景**: 使用 `print()` 但輸出沒有出現在預期位置。

**各環境下 `print` 的行為**:

| 環境 | `print` 輸出位置 |
|---|---|
| Workbench Journal | Workbench 輸出視窗 |
| Mechanical Script | Mechanical 訊息視窗 |
| PyMechanical `run_python_script()` | 捕獲為回傳字串 |
| ACT callback | ExtAPI.Log 或 Console (視設定) |
| FileSystemWatcher 背景執行緒 | Console (可能不可見) |

**解決方案**: 關鍵輸出寫入日誌檔而非依賴 `print`：

```python
def _log(msg):
    with open(log_path, "a") as f:
        f.write("{} {}\n".format(time.strftime("%H:%M:%S"), msg))
```

---

## ERR-IP-006: `from __future__ import` 必須在檔案最頂部

**觸發場景**: `from __future__ import print_function` 不在檔案第一個非註解行。

**根因**: Python 語法要求 `__future__` import 必須在模組的最開頭（docstring 之後、
其他 import 之前）。

**解決方案**: 確保 `from __future__ import` 在 docstring 之後的第一行。
