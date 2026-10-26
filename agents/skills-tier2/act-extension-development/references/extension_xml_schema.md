# ACT Extension XML 完整結構 (extension_xml_schema.md)

本手冊彙整 ACT Extension XML 定義檔的根節點結構與完整子標籤清單，來源：`Ansys_ACT_Developers_Guide` 與 `Ansys_ACT_XML_Reference_Guide`（Release 2026 R1）。與 `wizard_api.md`（Wizard 程式化呼叫）互補，本檔專注於 XML schema 本身。

> [!WARNING]
> 經查證（來源：NotebookLM「Ansys ACT Developer's Guide Release 2026 R1」），官方文件**沒有任何陳述說明 ACT Extension XML 的大小寫為不敏感或可互換**。`Ansys ACT Developer's Guide` 本文與範例一律使用小寫 `<extension>`，明確稱其為「root 節點」；而 `Ansys ACT XML Reference Guide` 的索引表中則以大寫 `<Extension>` 標示對應的底層 C# 類別名稱（`Class defining an ACT extension`），這是文件慣例上「XML 標籤 vs. 內部類別名」的對照寫法差異，並非官方宣告 XML 解析器大小寫不敏感。
>
> ACT Extension 檔案本質為標準 XML，依 XML 規格標籤名稱即為大小寫敏感。官方文件中所有可直接複製使用的範例與結構說明，標籤一律採小寫（如 `<extension>`、`<interface>`、`<simdata>`、`<script>`、`<guid>`）。**實務撰寫時應嚴格遵循本檔範例的小寫寫法**，不應假設大寫形式同樣可被解析器接受；若需驗證，應在真實 Mechanical/Workbench 環境以小規模範例實測，不可僅憑猜測。

---

## 一、根節點 `<extension>`

所有其他元素都巢狀於 `<extension>` 之下，這是唯一的根節點（原文：「This is the base tag or "root" element under which all other tags/elements fall.」）。

### 必要屬性

| 屬性 | 說明 |
|---|---|
| `name` | 擴充套件名稱（字串），必填 |
| `version` | 主版本號（整數），必填 |

### 選用屬性

| 屬性 | 說明 |
|---|---|
| `minorversion` | 次版本號 |
| `debug` | 是否以偵錯模式啟動腳本擴充套件（`true`/`false`） |
| `icon` | 擴充套件圖示檔名 |
| `allowReload` | 點擊 Reload 時是否允許重新載入 |
| `loadAsDefault` | 啟動應用程式時是否自動載入 |
| `masked` | 自動載入但在 Extension Manager 中隱藏 |
| `isNative` | 標示為原生擴充套件（忽略版本轉移訊息） |

## 二、子標籤清單

| 子標籤 | 用途 |
|---|---|
| `<script src="...">` | 指定 IronPython/CPython 腳本路徑；一個 extension 可引用多個腳本檔 |
| `<guid>` | 全域唯一識別碼；可用 `System.Guid.NewGuid().ToString()` 產生 |
| `<author>` | 作者或開發組織名稱 |
| `<description>` | 功能說明 |
| `<Engine>` | 指定腳本引擎（`IronPython` 預設或 `CPython`） |
| `<assembly src="..." namespace="...">` | 載入外部編譯好的 .NET DLL |
| `<interface context="Project\|Mechanical">` | GUI 介面自訂（自訂工具列按鈕、選單、事件 Callback） |
| `<simdata context="...">` | 模擬環境自訂物件：`<load>`、`<object>`、`<optimizer>`、`<solver>`、`<geometry>`、`<result>`、`<step>` |
| `<workflow context="Project">` | Workbench Project Schematic 自訂工作流（含 `<tasks>`、`<taskgroups>`） |
| `<wizard context="...">` | 引導式精靈，內含多個 `<step>` |
| `<uidefinition>` | 精靈或自訂面板的 UI 版面配置（`<layout>`） |
| `<templates>` | 可重複使用的屬性控制範本（`<controltemplate>`） |
| `<licenses>` | 授權集合 |
| `<application>` | 要上架至 Ansys Store 的 ACT 應用資訊 |
| `<appstoreid>` | Ansys Store 專用唯一識別碼 |
| `<ImageDirectory>` | 額外圖示資料夾路徑 |

## 三、最小可行結構範例

```xml
<extension name="MyACTExtension" version="1" minorversion="0">
    <guid shortid="MyACTExtension">e7fa4157-90b7-4156-ac31-4000d1d687e1</guid>
    <author>Developer Name</author>
    <description>Extension description</description>
    <script src="main.py"/>

    <interface context="Mechanical">
        <images>images</images>
    </interface>

    <simdata context="Mechanical">
        <!-- <result>, <load>, <solver> etc. -->
    </simdata>
</extension>
```

## 四、`<script>` 多檔引用範例

```xml
<extension version="2" minorversion="1" name="WizardDemos">
    <guid shortid="WizardDemos">7fdb141e-3383-433a-a5af-32cb19971771</guid>
    <author>Author Name</author>
    <description>Simple extension to test wizards in different contexts.</description>
    <script src="main.py" />
    <script src="ds.py" />
    <script src="dm.py" />
    <script src="sc.py" />
</extension>
```

## 五、`<interface>` 根據 context 區分 Workbench / Mechanical

```xml
<interface context="[Project | Mechanical]">
    ...
</interface>
```

`context` 屬性決定該 interface 區塊只在對應環境生效：`Project` 對應 Workbench Project Schematic，`Mechanical` 對應 Mechanical 樹狀環境。詳見 `wizard_api.md` 中 Wizard 的 Workbench vs Mechanical 入口差異。
