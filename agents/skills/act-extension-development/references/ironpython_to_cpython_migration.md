# IronPython 到 CPython 遷移對照 (ironpython_to_cpython_migration.md)

依 `Ansys_Scripting_in_Mechanical_Guide`（Release 2026 R1, p.50-51）原文：「The Mechanical application supports both IronPython and CPython for scripting starting in 2026R1.」本手冊彙整兩者在語法與 API 層級的具體差異。與 `ironpython_quirks.md`（IronPython 2.7 本身的限制）互補，本檔專注於「兩引擎之間的轉換落差」。

---

## 一、切換引擎的 XML 宣告

預設引擎為 IronPython，可在 Extension XML 中切換為 CPython（僅 Mechanical 環境支援）：

```xml
<engine context="Mechanical" type="CPython"></engine>
```

> 原文：「The <engine> tag specifies which Python engine is used for ACT extensions. It defaults to IronPython but can be switched to CPython as follows... CPython is only supported for the Mechanical application.」

**大小寫注意事項（風險標記，未經官方 Schema 規範逐字確認）**：官方兩份手冊在同一個標籤上出現不同大小寫寫法——`Ansys_Scripting_in_Mechanical_Guide` 範例寫作小寫 `<engine>`，`Ansys_ACT_XML_Reference_Guide` 的正式 Tag 索引寫作大寫 `<Engine>`。這可能只是文件撰寫慣例不同，不代表 XML 解析器本身對大小寫寬容——XML 1.0 規範本身是大小寫敏感的，沒有找到 ACT 解析器明確放寬此限制的官方逐字說明。**實際開發時建議統一採用 `Ansys_ACT_XML_Reference_Guide` 的正式大寫寫法 `<Engine>`**，若要用小寫範例寫法，先在實際 Mechanical 環境驗證過再採用，不要只依賴本檔的推論。

**限制**：Extension 與 Scripting Console 的引擎類型必須一致才能在同一個 extension context 中互動；CPython 寫的 ACT extension 檔名必須唯一。

## 二、基礎語法差異

| 項目 | IronPython | CPython (Python.NET) | 出處 |
|---|---|---|---|
| Python 版本規範 | Python 2.x | Python 3.x，所有 2→3 語法差異都適用 | p.50 |
| `import clr`/`import System` 順序 | 任意順序皆可 | 必須先 `import clr` 才能 `import System` | p.51 |
| JSON 解析 | 可用 `Newtonsoft.Json` | 不支援 `Newtonsoft.Json`，改用標準庫 `json` | p.51 |

## 三、.NET 型別處理差異

- **`str()` 取代 `.ToString()`**：Python.NET 不會自動幫 `int` 等型態產生 `.ToString()` 方法，一律改用 Python 原生 `str()`。
- **`len()` 取代 `.Count`**：Python.NET 不會為 list 產生 `.Count` 屬性（IronPython 過去的 `.Count` 支援本身就不穩定），一律改用 `len()`。
- **`ICollection` 真值判斷**：Python.NET 對實作 `ICollection`/`ICollection<>` 的物件支援 `len()`；若該集合 `Count` 為 0，`if collection:` 會判定為 `False`。要區分「物件是 None」與「集合是空的」，應寫 `if collection is not None:`。
- **`out` 參數呼叫差異**：

```python
# IronPython：呼叫含 out 參數的 C# 方法不需要傳入 out 引數
result = some_method(arg1)

# CPython (Python.NET)：即使不會被修改，也必須明確傳入 out 引數
result = some_method(arg1, out_arg)
```

## 四、Enum 列舉型態處理

```python
# 具名別名語法
# IronPython:
import Namespace.Namespace.EnumName as NewEnumName
# Python.NET:
from Namespace.Namespace import EnumName as NewEnumName
```

**關鍵字衝突**：Python.NET 無法把 Python 關鍵字（如 `None`）當 Enum 成員存取：

```python
# IronPython 可以直接寫：
preload = Ansys.Mechanical.DataModel.Enums.SpringPreloadType.None

# Python.NET 必須改用 System.Enum.Parse()：
preload = System.Enum.Parse(Ansys.Mechanical.DataModel.Enums.SpringPreloadType, "None")
```

## 五、類別繼承與介面實作

- 繼承 .NET Managed Class 的 Python 類別，若覆寫了 `__init__()`，必須明確呼叫基底建構子（`BaseName.__init__(self)` 或 `super().__init__()`）。
- 實作 .NET Managed Interface 的 Python 類別必須在類別定義中宣告 `__namespace__` 屬性，且每次腳本執行時該命名空間必須保持唯一（來源：PythonNet GitHub Issue 674）。

## 六、已知限制（CPython 側）

- **`Ansys.UI.Toolkit` 不完全支援**：Python.NET 在「隱藏回傳類別的屬性（Property Hiding）」上有限制，呼叫被隱藏的 managed property 時會呼叫到舊的（被隱藏的）版本而非新版，因此 `Ansys.UI.Toolkit` 無法完全相容。需要 GUI 時建議改用其他 Python 原生 GUI 套件。
- CPython 目前只支援 Mechanical 應用，不支援 Workbench 層級。
