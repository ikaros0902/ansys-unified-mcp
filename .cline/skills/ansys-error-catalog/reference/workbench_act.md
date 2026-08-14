# Workbench ACT Plugin 錯誤紀錄

---

## ERR-WB-001: `_PROJECT_ROOT` NameError

**觸發場景**: Workbench ACT 外掛載入時，`main.py` 中的某些函式引用 `_PROJECT_ROOT`，
但該變數在模組初始化時未被定義（或定義順序在引用之後）。

**錯誤訊息**:
```
Error when invoking function 'show_mcp_info'.
Traceback (most recent call last):
  File "C:\Users\4062863\AppData\Roaming\Ansys\v251\ACT\extensions\WorkbenchMCP\main.py", line 187, in show_mcp_info
NameError: global name '_PROJECT_ROOT' is not defined
```

**根因**: `_PROJECT_ROOT` 定義依賴於 `_QUEUE_ROOT`，而 `_QUEUE_ROOT` 的計算
依賴 `_resolve_queue_root()` 函式。若該函式因環境變數或路徑問題失敗，
`_PROJECT_ROOT` 不會被賦值。

**解決方案**:
```python
_QUEUE_ROOT = _resolve_queue_root()
_PROJECT_ROOT = os.path.dirname(_QUEUE_ROOT)  # 確保在 _QUEUE_ROOT 之後立即定義
```

**預防**: 模組層級變數的定義順序必須嚴格遵守依賴關係，且不能依賴 `try/except`
之外的動態計算結果。

---

## ERR-WB-002: `exec` 內部閉包 SyntaxError

**觸發場景**: 在 `wb_event_listener.py` 的 `_execute_script()` 中，
透過 `exec(script, exec_globals)` 執行使用者腳本，若腳本包含巢狀函式則失敗。

**錯誤訊息**:
```
SyntaxError: unqualified exec is not allowed in function '_execute_script' 
it contains a nested function with free variables
```

**根因**: IronPython 2.7 限制。`exec` 語句在包含閉包（free variable）的函式中
不被允許，即使 `exec` 的目標腳本本身不使用閉包。

**解決方案**: 將 `print` 重導向等需要閉包的邏輯改用頂層 helper 類別：

```python
class _OutputCollector(object):
    def __init__(self):
        self.lines = []
    def __call__(self, *args):
        self.lines.append(" ".join(str(a) for a in args))

collector = _OutputCollector()
exec_globals["print"] = collector
exec(script, exec_globals)
output = "\n".join(collector.lines)
```

---

## ERR-WB-003: FileSystemWatcher 事件重複觸發

**觸發場景**: 寫入一個 `.json` 檔案到 `commands/` 目錄時，
`FileSystemWatcher` 同時觸發 `Created` 和 `Changed` 事件，導致腳本被執行兩次。

**根因**: Windows 檔案系統寫入操作會先建立檔案（觸發 Created），
再寫入內容（觸發 Changed），可能還有緩衝區 flush（再次 Changed）。

**解決方案**: 使用 `threading.Lock` + `set` 去重：

```python
_processed_lock = threading.Lock()
_processed_ids = set()

def _on_file_changed(sender, event_args):
    cmd_id = extract_id(event_args.Name)
    with _processed_lock:
        if cmd_id in _processed_ids:
            return
        _processed_ids.add(cmd_id)
    # 處理指令...
```

---

## ERR-WB-004: WPF Dispatcher 跨執行緒存取

**觸發場景**: FileSystemWatcher 事件在 .NET ThreadPool 背景執行緒觸發，
直接在回呼中存取 `ExtAPI` 或 Workbench UI 物件時拋出跨執行緒存取異常。

**根因**: Workbench / Mechanical 的 GUI 物件只能在 WPF UI 執行緒上操作。

**解決方案**: 透過 `Application.Current.Dispatcher.Invoke()` 回到 UI 執行緒：

```python
from System.Windows import Application as WpfApp

app = WpfApp.Current
if app is not None and app.Dispatcher is not None:
    app.Dispatcher.Invoke(Action(_action))
else:
    _action()  # 無 GUI 時直接執行
```

---

## ERR-WB-005: Workbench Journal `Run Script` 阻塞 UI

**觸發場景**: 在 Workbench 中透過 `File > Scripting > Run Script` 執行包含
`while True: time.sleep()` 的 IronPython 腳本，導致整個 Workbench UI 凍結。

**根因**: Workbench Journal 腳本在主 UI 執行緒上同步執行。
任何阻塞操作（sleep, 無限迴圈）都會鎖死 UI。

**解決方案**: 改用 FileSystemWatcher 事件驅動架構（參見 `act-extension-development` skill）。

---

## ERR-WB-006: `StandardError: Exception has been thrown by the target of an invocation`

**觸發場景**: 呼叫 ACT callback function（如 `show_mcp_info`）時，
外層顯示此通用 .NET 反射錯誤，實際根因隱藏在內層 traceback。

**根因**: 這是 .NET `System.Reflection.TargetInvocationException` 的 IronPython 映射。
實際錯誤是內層的 `NameError` / `AttributeError` / `TypeError` 等。

**解決方案**: 始終檢查完整的 traceback 而非只看第一行錯誤訊息。
必要時在 callback 內加入 `try/except` 並寫入日誌：

```python
def show_mcp_info(step):
    try:
        # 實際邏輯
        pass
    except Exception as e:
        import traceback
        _log("show_mcp_info error: " + traceback.format_exc())
        raise
```
