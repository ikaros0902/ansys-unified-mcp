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
