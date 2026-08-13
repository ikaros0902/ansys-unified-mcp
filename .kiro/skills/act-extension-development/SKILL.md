---
name: act-extension-development
description: >-
  ANSYS ACT 擴充外掛開發模式、IronPython 陷阱、Workbench/Mechanical 環境差異、
  FileSystemWatcher 非同步事件監聽、ACT Wizard API 程式化呼叫。
  當開發或除錯 ACT 外掛、XML Wizard、IronPython 腳本時載入此 skill。
keywords: ACT, extension, IronPython, FileSystemWatcher, Wizard, ExtensionManager, wbex, XML, onupdateStep, callback, Workbench, Mechanical
---

# ACT 擴充外掛開發 (實戰知識)

本 skill 來自實際開發 session 的經驗總結，涵蓋 ACT 外掛開發中容易踩坑的
IronPython 限制、跨環境差異、非同步架構設計、以及 ACT Wizard 程式化呼叫。

---

## 1. IronPython 2.7 限制與陷阱

### 1.1 `exec` 不支援內部閉包 (Closure)

**問題**: IronPython 2.7 的 `exec()` 環境中不能定義包含內部閉包的函式。

```python
# ❌ 錯誤：exec 內部的 lambda/nested function 會拋出 SyntaxError
exec("""
def outer():
    items = []
    def inner():  # 閉包 — 在 exec 中會失敗
        items.append(1)
    inner()
""")

# ✅ 正確：改用頂層 helper 類別
class _OutputCollector(object):
    def __init__(self):
        self.lines = []
    def __call__(self, *args):
        self.lines.append(" ".join(str(a) for a in args))
```

### 1.2 `__name__` 在 PyMechanical 中不是 `"__main__"`

**問題**: 當腳本透過 `mc.run_python_script()` 執行時，`__name__` 是 `"<string>"`
而非 `"__main__"`。

```python
# ❌ 這段永遠不會執行
if __name__ == "__main__":
    apply_automesh()

# ✅ 直接呼叫頂層函式
apply_automesh()
```

### 1.3 `clr.AddReference()` 重複載入

**問題**: 若 assembly 已載入，`clr.AddReference()` 可能拋出異常。

```python
# ✅ 安全模式
try:
    import clr
    clr.AddReference("System")
except Exception:
    pass

try:
    clr.AddReference("PresentationFramework")
except Exception:
    pass
```

### 1.4 模組 `reload()` 在 ACT 環境中的必要性

**問題**: ACT 外掛的 Python 模組在 Workbench 啟動後被快取，修改後不會自動重新載入。

```python
# 在 main.py 中強制重新載入子模組
import wb_event_listener
reload(wb_event_listener)
```

---

## 2. Workbench vs Mechanical 環境差異

### 2.1 兩種 ACT 上下文

| 屬性 | Workbench (Project Schematic) | Mechanical (Model Window) |
|---|---|---|
| XML `<interface context="...">` | `"Project"` | `"Mechanical"` |
| 可用 API | `GetAllSystems()`, `Update()` | `ExtAPI`, `DataModel`, `Model` |
| gRPC 連線 | 無原生 gRPC | PyMechanical port 10000+ |
| Script 執行 | IronPython Journal | IronPython / PyMechanical `run_python_script()` |

### 2.2 LS-DYNA 獨立 Mechanical 視窗

**關鍵發現**: LS-DYNA 在 Workbench 中是獨立的 Mechanical GUI 視窗。
Static Structural 和 LS-DYNA 各自有獨立的 Mechanical 實例，
透過 PyMechanical gRPC 只能連到其中一個（通常是先啟動的那個）。

要操作 LS-DYNA 的 Mechanical 視窗，需要：
1. 確認目標視窗的 gRPC port
2. 或使用 Workbench Journal 從 System 層級操作

---

## 3. 非同步事件架構：FileSystemWatcher

### 3.1 架構原則

使用 .NET `System.IO.FileSystemWatcher` 取代 `while True: time.sleep()` 輪詢。
優點：
- 0% 空閒時 CPU 佔用
- 不阻塞 Workbench 主 UI 執行緒
- 事件觸發於 .NET ThreadPool 背景執行緒

### 3.2 關鍵實作模式

```python
from System.IO import FileSystemWatcher, NotifyFilters

watcher = FileSystemWatcher()
watcher.Path = commands_dir
watcher.Filter = "*.json"
watcher.NotifyFilter = NotifyFilters.FileName | NotifyFilters.LastWrite
watcher.Created += on_file_changed
watcher.Changed += on_file_changed
watcher.EnableRaisingEvents = True
```

### 3.3 WPF Dispatcher 安全執行

FileSystemWatcher 事件在 .NET ThreadPool 執行緒觸發，
若需操作 UI 或 ExtAPI，必須透過 WPF Dispatcher 回到主執行緒：

```python
from System.Windows import Application as WpfApp

app = WpfApp.Current
if app is not None and app.Dispatcher is not None:
    app.Dispatcher.Invoke(Action(_action))
```

### 3.4 防重複觸發

FileSystemWatcher 可能對同一檔案觸發多次事件，需加鎖去重：

```python
_processed_lock = threading.Lock()
_processed_ids = set()

with _processed_lock:
    if cmd_id in _processed_ids:
        return
    _processed_ids.add(cmd_id)
```

---

## 4. ACT Wizard 程式化呼叫 (`.wbex` 加密外掛)

### 4.1 原生 API 路徑（4 步驟）

即使沒有原始碼，只有 `.wbex` 加密外掛，也能用以下 API 操作 Wizard：

```python
# Step 1: 取得 ExtensionManager
ext_mgr = ExtAPI.ExtensionManager
# 類型: <Ansys.Mechanical.Customization.Extensions.MechanicalExtensionManager>

# Step 2: 取得指定 Wizard
wizard = ext_mgr.GetWizardByName("MECH_AutoMesh")

# Step 3: 開啟 Wizard 並設定參數
wizard.Open()
step = wizard.Steps[0]
step.Properties["Group"].Properties["Prop"].Value = val

# Step 4: 程式化提交
step.Update()  # 等同於按下 Submit 按鈕
```

### 4.2 列舉所有已安裝的 Wizard

```python
ext_mgr = ExtAPI.ExtensionManager
for ext in ext_mgr.Extensions:
    print("Extension:", ext.Name, "| Unique:", ext.UniqueName)
    wizards = ext.Wizards
    if wizards:
        for w in wizards:
            print("  Wizard:", w.Name)
```

---

## 5. Workbench 專案刷新 API

### 5.1 Component 層級精準刷新（非全域 Update）

```python
# 優先使用 Component 層級刷新，避免觸發不必要的 Solve
proj = ExtAPI.DataModel.Project
for sys_item in proj.Systems:
    if hasattr(sys_item, "Components"):
        for comp in sys_item.Components:
            if hasattr(comp, "Refresh"):
                comp.Refresh()
            if hasattr(comp, "Update"):
                comp.Update()
    if hasattr(sys_item, "Refresh"):
        sys_item.Refresh()
```

### 5.2 Journal API 刷新

```python
# Workbench Journal 環境下可用
systems = GetAllSystems()
for s in systems:
    model_cont = s.GetContainer(ComponentName="Model")
    if model_cont:
        model_cont.Refresh()
```

---

## 參考檔案

| 檔案 | 用途 |
|---|---|
| `reference/ironpython_quirks.md` | IronPython 2.7 詳細陷阱清單 |
| `reference/filesystemwatcher_pattern.md` | FileSystemWatcher 完整範例 |
| `reference/wizard_api.md` | ACT Wizard 程式化呼叫完整 API |
