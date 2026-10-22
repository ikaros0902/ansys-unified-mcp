# IronPython 2.7 限制與避坑指南 (ironpython_quirks.md)

本手冊彙整 ANSYS ACT 與 Mechanical / Workbench 內嵌 IronPython 2.7 解譯器的特殊限制與避坑寫法。

---

## 1. `exec` 不支援內部閉包 (Closure)

**問題**: IronPython 2.7 的 `exec()` 環境中不能定義包含內部閉包的函式。

```python
# ❌ 錯誤：exec 內部的 nested function 會拋出 SyntaxError
exec("""
def outer():
    items = []
    def inner():  # 閉包在 exec 中會失敗
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

---

## 2. `__name__` 在 PyMechanical 中不是 `"__main__"`

**問題**: 當腳本透過 `mc.run_python_script()` 執行時，`__name__` 是 `"<string>"` 而非 `"__main__"`。

```python
# ❌ 這段永遠不會執行
if __name__ == "__main__":
    apply_automesh()

# ✅ 直接呼叫頂層函式
apply_automesh()
```

---

## 3. `clr.AddReference()` 重複載入防護

**問題**: 若 assembly 已載入，重複調用 `clr.AddReference()` 可能拋出異常。

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

---

## 4. 模組 `reload()` 的必要性

**問題**: ACT 外掛的 Python 模組在 Workbench 啟動後被快取，修改後不會自動重新載入。

```python
import wb_event_listener
reload(wb_event_listener)
```

---

## 5. 全域便利巨集（`GetRootPart()`, `MM()`）在 ACT 回呼中未宣告陷阱

**問題**: `GetRootPart()` 與 `MM()` 是 SpaceClaim / Discovery 互動式 Script 控制台注入的便利巨集函式。在 ACT Wizard 回呼（如 `onupdateStep`）或透過 `execfile()` / 外部模組載入時，這些符號在 IronPython 獨立命名空間中**並未自動注入**，會直接拋出 `NameError: global name 'GetRootPart' is not defined`。

```python
# ❌ 易崩潰：直接呼叫全域巨集
root = GetRootPart()
thick = MM(1.0)

# ✅ 正確：封裝防禦性取得器
def _get_root_part(api):
    try:
        return GetRootPart()
    except:
        try:
            return api.Window.ActiveWindow.Document.MainPart
        except:
            return None

def _to_meters(val):
    try:
        return MM(val)
    except:
        return float(val) * 0.001
```

---

## 6. ACT 腳本全 ASCII/英文強制規範與編碼崩潰預防

**問題**: IronPython 2.7 底層將字串視為 .NET String (UTF-16)，但預設字元編碼器為 ASCII。當腳本內部包含中文字串字面量、中文註解或對物件名稱調用 `str()` 時，極易觸發 `UnicodeEncodeError: ('unknown', '\x00', ...)` 或解譯器語法解析中斷。

**防禦底線**:
1. ACT 擴充外掛與內嵌腳本的代碼、變數、註解一律嚴格使用全英文 ASCII。
2. 彈窗或訊息提示文字若需多語系，一律使用 Unicode 字面量（如 `u"提示文字"`）並在開頭宣告 `# -*- coding: utf-8 -*-`。
3. 讀寫日誌或外部檔案時，必須透過 `codecs.open(path, "w", encoding="utf-8")` 明確指定編碼。
