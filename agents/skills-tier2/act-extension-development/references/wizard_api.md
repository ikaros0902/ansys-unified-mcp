# ACT Wizard API 完整成員與 Step 存取 (wizard_api.md)

本手冊彙整 ACT Wizard 相關介面之官方 API 成員清單，並說明 Wizard Step 內屬性讀寫、UI 元件存取與 Callback 事件生命週期。來源：NotebookLM「Ansys ACT Developer's Guide Release 2026 R1」官方 API 參考手冊。

> [!NOTE]
> **查證範圍聲明**：本檔案列出的 `IWizard`/`IWizardStep`/`IStepUserInterface`/`IPropertyCollection`/`ISimProperty`/`ISimPropertyGroup` 等介面成員，於 `docs/api_inventory/*.json`（API 快照）中查無記錄 —— 這是預期狀況，因為該快照以 Mechanical/SpaceClaim 等產品的 DataModel 物件為主，未收錄 ACT Wizard 框架介面。本檔內容的查證依據為 NotebookLM 官方文件引用（含來源頁碼），非 `api_inventory` 交叉比對；使用前仍建議以 `api_search(product="act")` 或實機測試二次確認。

> [!CAUTION]
> 原版本示範的 `wizard.Open()`、`step.Update()` 經查證**於 `IWizard`/`IWizardStep` 介面中並不存在**，為錯誤示範，已移除。正確的 Wizard 啟動與步驟推進方式見第 3 節。

---

## 一、`IWizard` 介面（`Ansys.ACT.Interfaces.Wizard`）

Wizard 本身的屬性皆為**唯讀**，沒有 `Open()` 方法；Wizard 實例是由啟動命令（見第三節）回傳取得。

| 成員 | 說明 |
|---|---|
| `CurrentStep` (屬性, `IWizardStep`) | 取得目前使用者所在的步驟 |
| `Description` (屬性, `string`) | Wizard 描述文字 |
| `Extension` (屬性, `IExtension`) | 關聯的 ACT Extension 實例 |
| `Filename` (屬性, `string`) | 定義此 Wizard 的檔案名稱 |
| `Folder` (屬性, `string`) | Wizard 所在資料夾路徑 |
| `Name` (屬性, `string`) | Wizard 內部名稱 |
| `Steps` (屬性, `IDictionary<string, IWizardStep>`) | 以步驟名稱為鍵的所有步驟字典 |

## 二、`IWizardStep` 介面

| 成員 | 說明 |
|---|---|
| `ComponentName` (可讀寫, `string`) | 關聯的 Workbench Component 名稱 |
| `Context` (唯讀, `string`) | 應用情境名稱（如 `Mechanical`、`Project`、`SpaceClaim`） |
| `HelpFile` (可讀寫, `string`) | 此步驟對應的 HTML 說明檔路徑 |
| `IsEnabled` (可讀寫, `bool`) | 是否啟用此步驟（可動態略過） |
| `Layout` (可讀寫, `string`) | 此步驟使用的 UI 版面配置名稱 |
| `NextEnabledStep` / `PreviousEnabledStep` (唯讀, `IWizardStep`) | 下一個/上一個「已啟用」步驟 |
| `NextStep` / `PreviousStep` (唯讀, `IWizardStep`) | 緊鄰的下一個/上一個步驟 |
| `StepId` (唯讀, `int`) | 步驟序號 |
| `SystemName` (可讀寫, `string`) | 關聯的 Workbench 系統名稱 |
| `UserInterface` (唯讀, `IStepUserInterface`) | 此步驟的 UI 存取物件 |
| `Wizard` (唯讀, `IWizard`) | 回指所屬的 Wizard |
| `Properties` (唯讀, `IPropertyCollection`) | 此步驟的輸入/輸出屬性集合（實務最常用） |

## 三、`IStepUserInterface` 介面

| 成員 | 說明 |
|---|---|
| `Panel` (唯讀, `IPanel`) | 取得此步驟的根 UI 容器 |
| `GetComponent(string name)` (方法, 回傳 `IComponentRenderer`) | 依名稱取得具名 UI 元件（如 `"Properties"`、`"Progress"`、`"Steps"`、自訂 Dialog 名稱） |

```python
# 一般繁體中文註解：取得目前步驟的 Properties 面板並強制重新整理畫面
panel = step.UserInterface.GetComponent("Properties")
panel.UpdateData()
panel.Refresh()
```

## 四、屬性存取：`IPropertyCollection` 與 `ISimProperty`

`step.Properties` 回傳 `IPropertyCollection`，其成員：

- `Count` (唯讀, `int`)
- `Item[string name]` (索引子，回傳 `ISimProperty`) — 一般以 `step.Properties["屬性名稱"]` 存取
- `GetByName(string name)` (方法)
- `Contains(ISimProperty property)` (方法)

`ISimProperty` 常用成員：`Value`、`ValueString`、`Caption`、`Name`、`Control`（UI 控制類型，如 `text`/`float`/`select`/`fileopen`/`scoping`）、`DefaultValue`、`ReadOnly`、`Visible`、`IsValid`、`StateMessage`、`Options`（下拉選單選項）、`UnitString`、`ParentPropertyGroup`。

屬性群組（`ISimPropertyGroup`）成員：`Properties`（子屬性集合）、`AllDescendants`（遞迴取得所有子孫屬性）、`Display`（顯示型態列舉 `PropertyDisplayEnum`）。

```python
# 一般繁體中文註解：讀寫步驟屬性值（最常見的 Wizard 腳本操作）
step.Properties["Group"].Properties["Prop"].Value = val
step.Properties["Mesh/Nodes"].Value = model.Mesh.Nodes.ToString()
```

## 五、Wizard 啟動與步驟推進（正確 API）

Wizard 沒有實例方法可直接呼叫「開啟」或「下一步」，而是透過 `Ansys.ACT.WorkBench.Commands` 命名空間下的靜態命令類別驅動，僅支援 UI 模式（不支援批次/batch 模式）：

| 命令類別 | 用途 |
|---|---|
| `StartWizardCommand` | 依 Extension ID 與 Wizard 名稱啟動一個 Wizard，回傳啟動後的 `IWizard` 實例 |
| `ExecuteNextStepCommand` | 等同於點擊畫面上的「Next」按鈕，執行當前步驟並載入下一步 |
| `ExecutePreviousStepCommand` | 等同於點擊「Back」按鈕，返回上一步 |

兩個 Execute 命令皆提供 `InvokeAndWait(...)`（同步阻塞直到完成）與 `InvokeAsync(...)`（非同步，立即返回）兩種呼叫形式，部分多載可額外傳入 `InvokeConfiguration`、`IProtectedContext` 或 `IProgressMonitor` 以客製化執行環境與進度回報。

```python
# 一般繁體中文註解：以 Next 命令推進至下一步（同步阻塞直到該步驟執行完成）
Ansys.ACT.WorkBench.Commands.ExecuteNextStepCommand.InvokeAndWait(None)
```

## 六、Step 生命週期 Callback（XML `<callbacks>` 標籤）

每個步驟可在 XML 中以 `<callbacks>` 綁定 IronPython 函式，常見事件：

| Callback 標籤 | 觸發時機 |
|---|---|
| `<onupdate>` | 使用者點擊 Next，確認並送出本步驟資料時 |
| `<onreset>` | 使用者點擊 Back，重置本步驟狀態時 |
| `<onrefresh>` | 進入/初始化本步驟，用於更新顯示資料或版面配置 |
| `<oninit>` / `<oncreate>` | 步驟物件被建立時 |
| `<onvalidate>` （屬性層級的 `<IsValid>`） | 驗證使用者輸入是否合法，決定 Next 按鈕是否可用 |

```python
# 一般繁體中文註解：onupdate callback 函式接收當前 step 作為參數
def on_update_geometry_step(step):
    pass
```

---

## 七、Workbench 精準 Component 刷新

避免引發全域重算，僅刷新幾何或材料變更之元件：

```python
proj = ExtAPI.DataModel.Project
for sys_item in proj.Systems:
    if hasattr(sys_item, "Components"):
        for comp in sys_item.Components:
            if hasattr(comp, "Refresh"):
                comp.Refresh()
            if hasattr(comp, "Update"):
                comp.Update()
```
