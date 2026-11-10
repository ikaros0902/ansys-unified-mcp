# Ansys ACT 知識字典

本頁整理 ACT 擴充套件的檔案結構、安裝與載入、編譯與專案分享、Console／Editor／Debugger，以及已核讀的 Wizard 與 Mechanical 參數化條目。主要依據本機 Release 2026 R1（v261）文件；舊版已知問題另標示為 2024 R1（v241）。`complete` 表示清冊中該有界主題已整理，不代表全部 ACT API、產品或範例皆經逐項驗證。

## 1. 來源、版本與頁碼

本頁的「實頁」指 PDF 檔案從 1 起算的頁次；「印刷頁」指頁腳頁碼。以實頁定位原件，再用章節名稱核對。

| 來源 | 版本證據與定位 | 用途 |
| --- | --- | --- |
| [ACT Developer's Guide](../ANSYS_Document/ACT/v261/manuals/Ansys_ACT_Developers_Guide.pdf) | 封面 Release 2026 R1；共 208 實頁；正文印刷頁通常比實頁少 6 | 結構、工具、部署、Console、已知問題、除錯；`sources.csv#ansys_d646d1830d851f5a6ef9ff6b` |
| [ACT API Reference Guide](../ANSYS_Document/ACT/v261/manuals/Ansys_ACT_API_Reference_Guide.pdf) | Release 2026 R1；共 5,596 實頁 | .NET 介面；Wizard 命名空間實頁 5295–5300＝印刷頁 4961–4966；`sources.csv#ansys_a1e4d4189deddf58abda84c7` |
| [ACT XML Reference Guide](../ANSYS_Document/ACT/v261/manuals/Ansys_ACT_XML_Reference_Guide.pdf) | Release 2026 R1；共 1,532 實頁 | XML 元素、屬性與 callback 的查閱入口；`sources.csv#ansys_8042af7cc70f4a77c7fbd338` |
| [ACT Known Issues](../ANSYS_Document/ACT/unknown/archives/ACTKnownIssues.pdf)／[Markdown](../ANSYS_Document/ACT/unknown/archives/ACTKnownIssues.md) | 封面明列 2024 R1；10 實頁；原目錄 `unknown` 不改動 | 舊版限制；`sources.csv#ansys_e59201d8a6146112088712a7` |
| [ACT Migration Notes](../ANSYS_Document/ACT/unknown/archives/ACTMigrationNotes.pdf)／[Markdown](../ANSYS_Document/ACT/unknown/archives/ACTMigrationNotes.md) | 封面明列 2024 R1；4 實頁 | 舊版遷移說明；`sources.csv#ansys_8074c413b74a6afa8a702614` |
| [ACT Customization Guide for Mechanical](../ANSYS_Document/Mechanical/v261/manuals/ACT_Customization_Guide_for_Mechanical.pdf) | Release 2026 R1；實頁 9–11＝印刷頁 5–7 | `isparameter`、`readonly` 與結果輸出；`sources.csv#ansys_dabc1dfd103cdeaf363a86a2` |

原件及轉換正文保留原有授權標記；本機整理不表示可公開散布。頁面影像、圖表與原件仍是核對依據。

## 2. ACT extension 結構與開發生命週期

**Scripted extension** 的基本組成是 XML 定義檔與 IronPython script；可另帶圖示、輸入檔、函式庫或 .NET assembly。**Binary extension** 是從 scripted extension 建置出的 WBEX，可供執行，內容無法以 ACT 工具直接查看或編輯。v261 手冊要求載入 scripted extension、建置 WBEX 時有 ACT license；執行 binary extension 不要求 ACT license。依據：Developer's Guide 實頁 18、25–26、77–80（印刷頁 12、19–20、71–74）。

開發工作依序可分為：定義 XML／script → 放入正確目錄 → 設定 extension options → 安裝與載入 → 除錯 → 視需求建置 WBEX。這是開發步驟；各 XML 元素的 callback 依事件觸發，不能從這張流程推定所有宿主都執行同一條 `oninit → onload → solve → postprocess` 鏈。依據：實頁 30–31、78–80。

### ACT v261 scripted extension 檔案結構

手冊範例 `ExtSample1` 的 XML 與同名子目錄位於相同層級；script、images 放在子目錄中。script 不在預設目錄時，`<script>` 須給明確路徑。

```text
extension_folder/
  ExtSample1.xml
  ExtSample1/
    sample1.py
    images/
      hand.bmp
```

此範例以 `<interface context="Mechanical">` 指定介面 context；`<onclick>` 指向 script 中的函式。不要將原始範例改寫成未經核對的根節點 `target="mechanical"` 語法。範例 XML 與 script 可查本機 [ExtSample1.xml](../ANSYS_Document/ACT/v261/archives/ACTExtensionExamples/ExtSample1.xml) 和 [sample1.py](../ANSYS_Document/ACT/v261/archives/ACTExtensionExamples/ExtSample1/sample1.py)，以及 Developer's Guide 實頁 79–80。

圖示有兩個不同上下文：實頁 79 的傳統 toolbar 範例要求 Mechanical 用 BMP、其他產品用 PNG；實頁 82 對 2019 R2 起的 Mechanical ribbon menu icon 另列 16、24、32、48 像素 PNG 與 `icon_<name>_<size>x<size>.png` 命名。請依所用 UI 元素查閱對應規則。

## 3. ACT v261 Extension Manager 安裝／載入／預設載入

執行 extension 前須安裝並載入。圖形式入口是 ACT Start Page 的 **Manage Extensions**；表格式入口是 **Extensions → Manage Extensions**。scripted extension 只在 ACT license 可用時列出；binary extension 一律列出。依據：Developer's Guide 實頁 45–50（印刷頁 39–44）。

| 操作 | 文件規則與注意事項 |
| --- | --- |
| 安裝 scripted extension | 將 XML／同名資料夾放到選定位置，以 Additional Extension Folders 指向該位置；獨立 Mechanical 可從 Automation → Extension Manager 的齒輪加入資料夾 |
| 安裝 binary extension | 用 Install Extension 選 WBEX；v261 預設安裝位置為 `%APPDATA%\Ansys\v261\ACT\extensions`；移動時 WBEX 與生成的資料夾須一起保留 |
| Uninstall | 右鍵 Uninstall 僅適用 binary；會永久刪除定義檔和資料夾，包含使用者在 extension 資料夾的修改。scripted extension 以移除檔案方式解除安裝 |
| Load／Unload | installed 不代表 loaded；在 Extension Manager 切換載入狀態。從 Workbench 卸載 Mechanical context 的 extension 時，Mechanical 不會同步知道它已卸載 |
| Load as Default | 目標產品啟動時自動載入。已存於 project 的 extension 亦可能因專案依賴而自動載入；缺少必要 extension 時，開啟專案會發出警告 |

### ACT v261 extension 搜尋路徑與非遞迴規則

**Tools → Options → Extensions → Additional Extension Folders** 可用分號分隔多個資料夾，或在圖形式 Extension Manager 的齒輪加入資料夾。這些路徑加入 ApplicationData 預設路徑；預設資料夾搜尋不遞迴，extension 應放在搜尋目錄的頂層。路徑／extension 衝突會記到 Extensions Log。依據：實頁 85–86（印刷頁 79–80）。

## 4. ACT v261 多腳本 WBEX 編譯與共用 scope

XML 可有多個 `<script>`。ACT 會把這些 script 放進單一 scope，效果像合併成同一檔案。標為 `compiled="true"` 的 script 會編入 binary buffer；安裝 WBEX 後，內容仍進入共用 scope，原本的 script module 不再以檔案形式供彼此匯入。手冊要求在這種建置方式移除彼此的 import 與 module prefix；另一選項是先將 IronPython modules 編譯成 DLL，再由主 script 匯入。依據：Developer's Guide 實頁 57–58（印刷頁 51–52）。此處未建置或載入 WBEX。

### ACT v261 WBEX sharing 與專案保存／開啟副作用

建置時的 **Security Option For Sharing** 與使用端 **Save Binary Extensions with Project** 共同決定是否將 extension 存入專案；存檔時還必須開啟 Load by Default。依據：實頁 55–57、86。

| 建置安全設定 | 使用端 Never | 使用端 Copied but locked／Always |
| --- | --- | --- |
| `cancopy` | 不存入 project | 存入；開啟後的可跨專案使用性依使用端設定而異 |
| `cancopylocked` | 不存入 project | 存入，限制於該 project |
| `notcopied` | 不存入 project | 不存入；建置安全設定優先 |

v261 手冊實頁 86 明確警告：開啟含已保存 extensions 的 `.wbpj`／`.wbpz` 時，Extension Manager 會解除安裝本機版本並刪除本機 extension 檔案，改用專案內版本；可能影響 `%APPDATA%`、Addins 或額外搜尋目錄中的既有檔案。預設值是 **Never**。專案分享前應核對這兩組設定與原件備份。

## 5. IronPython、ACT Console 與 XML Editor

本頁以手冊列出的 **IronPython** 與 .NET assembly 整合為範圍；未從這批來源確認固定的 IronPython patch version。Developer's Guide 實頁 119–120 說明可使用能產生 .NET assemblies 的語言，並列出 ACT 安裝目錄內的產品函式庫。這不等於每個 CPython 套件均可在 ACT 執行。

### ACT v261 Console scope 與 Automation／SimEntity 物件

`ExtAPI` 是 ACT API 入口；`ExtAPI.DataModel` 回傳高層介面。每個 extension 有自己的 script engine，若要存取某 extension 的全域變數或函式，先在 **Select scope** 選擇該 extension。Console 的 ACT API 說明列出 Workbench、DesignModeler、Mechanical；各宿主的介面與腳本入口仍應查產品指南。依據：實頁 58–61（印刷頁 52–55）。

Automation 物件包裝產品的使用者功能；Console／`ExtAPI.DataModel` 常用到這層。extension callback 的參數則常是 SimEntity 物件。文件提供此辨識方式，沒有據此建立「所有 callback 可互換 Automation 型別」的保證。Mechanical v261 的 Scripting view 可從 Automation → Scripting 開啟；要改回 ACT Console，手冊列出 **File → Options → Mechanical → UI Options → New Scripting UI**，改動後須重啟 Mechanical。依據：實頁 59–60。

### ACT v261 XML Editor 與 Resource Manager 編輯界線

App Builder 的 XML Editor 可查看／修改視覺介面未顯示的元素與屬性；Advanced XML Editor 設定還能顯示額外的非公開屬性。這些額外屬性不因可見就成為已驗證的公開 API。Resource Manager 用斜體標示 App Builder 正在使用的唯讀項目；不能在該工具改 extension folder 名稱、project XML、extension XML 或其 IronPython scripts，其他可編輯項目可新增、匯入、輸出或編輯文字／HTML help。依據：實頁 113–119（印刷頁 107–113）。本頁未驗證 XML Editor 能自動檢查 Python callback 是否存在。

## 6. ACT v261 Debug Mode 的宿主時機與平台限制

**Tools → Options → Extensions → Debug Mode** 或 Extension Manager 齒輪可開啟 debug mode；Workbench Project 頁立即生效，DesignModeler／Mechanical 須退出並重啟產品。ACT Debugger 應從 extension 真正執行的宿主啟動，才會 attach 到正確程序；例如 Workbench 的 debugger 不能因此除錯 Mechanical extension。此工具支援 Workbench Project、DesignModeler、Mechanical，文件明列不支援 Linux script debugging。依據：Developer's Guide 實頁 175–177（印刷頁 169–171）。

### Mechanical v261 onInit／onLoad 與 UserInterface 存取時機

在 Mechanical 的 `onInit` callback 或全域初始化存取 `ExtAPI.UserInterface`，文件記載可能產生錯誤與不穩定；改在 `onLoad` 或其他非 `onInit` 位置存取。`onLoad` 只在 Mechanical 啟動時觸發；GUI Reload Extension 不會再次呼叫它。依據：實頁 22（印刷頁 16）。本頁沒有把 `-actdebug` 啟動參數或固定 `%TEMP%` log 路徑列為已核實操作。

## 7. Mechanical v261 ACT property 參數化

Mechanical customization guide 實頁 9–11（印刷頁 5–7）列出的規則如下：

| 用途 | XML 條件 | 使用端步驟 |
| --- | --- | --- |
| 輸入參數 | property 加 `isparameter="true"` | Details view 勾選參數化後，顯示於 Parameter Set 的 Outline／Table |
| 輸出參數 | 同時加 `isparameter="true"` 與 `readonly="true"` | 仍須在 Details view 勾選參數化 |
| quantity 預設值 | 例如 `default="12 [C]"`，數值與方括號單位一起定義 | 核對物理量與單位 |
| ACT result 的 minimum／maximum | 預設可作輸出參數；由 Mechanical 環境提供 | 依結果物件介面選取 |

這些頁面示範 `control="float"` 與 `unit="Pressure"`，未提供「所有 string／scoping 參數化都會崩潰」的證據，因此不將該說法列為通用限制。

## 8. ACT API Reference 與宿主 API 字典

Developer's Guide 實頁 28–29 區分 API Reference（介面層 API）、XML Reference（XML 元素／tag）及產品 customization guide；手冊建議以線上／下載 HTML Reference 查閱 global、automation、object 三層資訊。查 API 時先固定產品與 release，再核對 member 頁的宣告、參數及限制。

[Mechanical Model 導覽字典](../ANSYS_Document/ACT/unknown/api_reference/Mechanical/Types/Ansys.ACT.Automation.Mechanical.Model.md) 列有 `Geometry`、`Mesh`、`Analyses`、`CoordinateSystems`、`NamedSelections` 等屬性與 member 頁連結，來源版本仍是 `unknown`（`sources.csv#ansys_217d3b007b31a97257c7bb18`）。這份導覽不能單獨證明完整的建模、網格、邊界條件或求解腳本。產品指南與 member 頁未核對的簽名，不在本頁提供可直接執行範例。

### Wizard XML callback 與 .NET API 文件界線

v251 [property.OnButtonClick 的原始轉換頁](../ANSYS_Document/ACT/v251/archives/ACTReferenceHTML/Wizard/Reference.callback.property.OnButtonClick.md) 說明按下 property button 時觸發，但 Parameters 留有 `@PARAMETER_NAME@`／`@PARAMETER_TYPE@` 等模板，Return Value 也沒有有效型別值。標題的 `Void` 不足以補出 CLR 簽名。該頁 HTML／Markdown 雜湊與 conversion manifest 相符；品質缺口存在於原文。

v261 PDF 另有 .NET `Ansys.ACT.Interfaces.Wizard` 介面，可確認下列宣告：

| 介面／屬性 | 宣告重點 | PDF 定位 |
| --- | --- | --- |
| `IWizard.CurrentStep` | `IWizardStep`、唯讀 | 實頁 5296／印刷頁 4962 |
| `IWizard.Steps` | `IDictionary<string, IWizardStep>`、唯讀 | 實頁 5297／印刷頁 4963 |
| `IWizardStep.HelpFile`、`IsEnabled` | 分別為 string／bool，可讀寫 | 實頁 5298／印刷頁 4964 |
| `IWizardStep.StepId` | 宣告是 `int`、唯讀；說明卻寫 associated component name，保留文件矛盾 | 實頁 5299／印刷頁 4965 |
| `IExtensionManager.CurrentExtension`、`Extensions` | 目前 extension 與已載入 extension 清單 | 實頁 5485–5486／印刷頁 5151–5152 |

既有 [Wizard API 導覽](../ANSYS_Document/ACT/v261/api_reference/ACT_WIZARD_API_DICTIONARY.md) 可作跳轉入口；`IWizard` 的起始印刷頁應以 PDF 的 **4962** 為準。來源：`sources.csv#ansys_6eb48640165a4baf55e9c000`、`sources.csv#ansys_a1e4d4189deddf58abda84c7`、`sources.csv#ansys_c4eb4b77406420f9188ab203`、`sources.csv#ansys_3636211033d95efdf5be9596`。

## 9. Known Issues、Migration Notes 與相容性

本節完成的是本機 **v241 獨立文件**及 **v261 Developer's Guide** 的指定限制／遷移說明整理。Mechanical 自身的 API Known Issues／Migration Notes 另由 Scripting in Mechanical Guide 管理；沒有從這兩份 ACT 總體文件推定所有 Mechanical API 相容。

| 問題或範圍 | 版本與原件位置 | 整理結果 |
| --- | --- | --- |
| Wizard help／HTML 資源 | v241 Known Issues 實頁 5–6；v261 Developer's Guide 實頁 19–20 | wizard help 僅支援 on-disk `file:///`；HTML component 的 image／custom JS／CSS 需 file URL protocol |
| 網路／mapped drive 圖示 | v241 實頁 5；v261 實頁 19 | web browser-based ACT view 的圖片可能不顯示；文件說 extension 仍可執行 |
| Workbench reload／property | v241 實頁 6–7；v261 實頁 20 | 建立自訂 systems 後 reload extension 可能產生非預期行為；custom workflow 不支援所有 `<property>` optional attributes，例如 `visibleon` |
| 機械唯讀／attributes／UI 初始化 | v241 實頁 8–9；v261 實頁 22 | Mechanical read-only mode 不支援 ACT 操作；`OrderedDict` attributes、巨型 dictionary attributes、`onInit` 存取 UserInterface 各有已知限制 |
| 平台與產品工具 | v241 實頁 7、9–10；v261 實頁 21、23、175–177 | DesignModeler Console／Log／wizards、Fluent ACT、ACT Debugger／App Builder 有文件列明的 Windows 範圍；App Builder 不支援 AEDT；Linux 有 start-page、JPEG、Graphics API 條件限制 |
| SpaceClaim extension 預設位置 | v241 實頁 8；v261 實頁 21 | 舊獨立文件內的 workaround 仍寫 `%APPDATA%\Ansys\v212\ACT\extensions`；v261 指南寫 v261。保留原文版本差異，不把 v212 路徑套用到本機版本 |
| geometry selection scoping | 僅本輪 v261 原件實頁 19 明列自 2024 R2 起的問題 | 同時用 `scoping` 與 `geometry_selection`、且後者為 `default_geometry` 時可能共用幾何 IDs；手冊要求令前者 `default_scoping=false` |
| ACT postprocessing analysis types | v261 實頁 19 | ACT postprocessing API 不支援 Harmonic、Complex Modal、Damped Modal；此句的範圍是 ACT postprocessing API |
| ACT 開啟與 PowerShell path | v261 實頁 19 | 文件列出 PowerShell 7 PATH 指向錯誤 library 的診斷情境；本輪未執行系統 PATH 調整 |

v241 Migration Notes 實頁 4 與 v261 Developer's Guide 實頁 18 均表示「該次 release 沒有會影響既有 ACT extensions 的 API changes」。這是各文件對其 release 的敘述，不能證明任意版本間都可無修改使用。v241 文件另記錄 Workbench SDK／External Connection Add-In 支援在 Ansys 19.0 結束；此為歷史遷移資訊。

## 10. 大型 ACT 清冊、轉換與範例的實際狀態

以本機 `_catalog/documents.json`（updated_at 2026-11-01）重新計數：ACT 有 **562,624 個清冊列**，其中 **562,364 body_present、259 attachments、1 stub**。這些列含 API、guide、manual、tutorial，且同內容可能有不同版本／HTML／Markdown 別名；不能稱作 562,364 個唯一 API。`coverage.json` 的 unknown indexed_candidates 比現行 documents 少一列，反映清冊衍生資料尚未完全同步。

| release | body_present | attachment | stub |
| --- | ---: | ---: | ---: |
| unknown | 3,393 | 124 | 0 |
| v251 | 133,752 | 44 | 0 |
| v252 | 133,412 | 44 | 0 |
| v261 | 291,807 | 47 | 1 |

已轉換 PDF 共 7 份，canonical cache 的實頁標記共 **7,375** 個，均連續且涵蓋全 PDF；source／cache 雜湊均與 `pdf_extraction.json` 相符。3 份 v261 指南的既有 sidecar 因內容不同而由轉換器保留，RAG canonical cache 另存；本輪未覆寫它們。HTML conversion manifest 中有 158,969 個 ACT 處理項：158,878 converted、48 reused_existing_markdown、42 plain_text_fallback、1 failed；這是該 manifest 的處理列數，沒有涵蓋全部既存正文的逐頁語意審查。

### 範例已取得，歷史下載失敗紀錄仍在

本機 [v251](../ANSYS_Document/ACT/v251/archives/ACTExtensionExamples.zip)、[v252](../ANSYS_Document/ACT/v252/archives/ACTExtensionExamples.zip)、[v261 ACTExtensionExamples.zip](../ANSYS_Document/ACT/v261/archives/ACTExtensionExamples.zip) 都存在。三者 SHA-256 均為 `a0f9979e596ee66020c46d1fb9b48197edbfe6efbf50ccb14c3f5b2085dec287`，各有 135 個非目錄檔案、49 個目錄項；downloads 記錄的 184 是兩者合計。三包 CRC 及 405 個解壓檔逐項雜湊核對皆通過。

v261 包含 27 個 XML、32 個 Python、37 個 BMP、24 個 PNG、11 個 HTML 等檔案；`DataSquares` 與 `Squares` 各有一個 EXE，本輪只做靜態封裝／雜湊核對。三版本提供相同 ZIP 內容，不等於已證明每個範例在三版本宿主都可執行。`downloads.json` 同時留有成功與後續 DNS／path-boundary 失敗紀錄，現存檔案證據優先；「v261 範例未取得」已不符合目前狀態。

### 保留的缺口（source_limited）

- `MappingValidation.RemoveParameter.html` 的一份 v261 原件是 **0 bytes**；[對應 Markdown](../ANSYS_Document/ACT/v261/archives/ansys-zip-ro3no34_/Mechanical/Reference.methode.Ansys.ACT.Automation.Mechanical.MappingValidation.RemoveParameter.md) 只記錄無正文，catalog 列為 stub（`sources.csv#ansys_61d26fdaa796aa63eea85029`）。不能從轉換產物補出方法宣告。
- `OnButtonClick` 的模板參數缺失屬原始文件品質問題。42 筆 plain-text fallback 的表格／圖片完整性未逐頁核對；全部 ACT API 亦未逐項核讀。
- 範例 package 已有完整的靜態檔案對照；`ready_examples=0` 與 `tutorial_inputs` 缺口仍存在於 coverage。宿主載入、跨版本相容性、外部輸入與求解未經本輪驗證，故不把 package 存在改列成 runtime 通過。

範圍來源：[_catalog/documents.json](../ANSYS_Document/_catalog/documents.json)、[coverage.json](../ANSYS_Document/_catalog/coverage.json)、[downloads.json](../ANSYS_Document/_catalog/downloads.json)、[PDF extraction manifest](../ANSYS_Document/_catalog/pdf_extraction.json)、[HTML conversion manifest](../ANSYS_Document/_catalog/html_conversion_manifest.json)。範例來源 ID：`sources.csv#ansys_3ea4f5f2d1530ab81e4274ef`、`sources.csv#ansys_62421fe295033a24952c52ce`、`sources.csv#ansys_3c851d2a10a4b8d546b4c755`。


## 2026-11-04：Wave 5 本機來源盤點與限制說明

本批 inventory 記錄本機 catalog 共 562,624 筆文件、`sources.csv` 共 33 筆來源。保存的 source audit 只列 2,000 筆 catalog 文件，這些列的來源與正文 hash 相同；其餘 560,624 筆沒有列入該稽核 JSON。PDF 頁面與 HTML 頁面稽核欄位為空，因此本批不宣稱全 catalog 完成逐筆 hash 或頁面品質核驗。HTML conversion manifest 依 `source` 路徑以 `ACT/` 開頭篩選，共 158,969 筆；其中 42 筆狀態為 `plain_text_fallback`，尚未逐頁核對表格與圖片。本機未快取或受登入／授權限制的主題仍標為缺口，未推測未核實的 ACT API，也未執行求解。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/act_module_conversion_report_20261104.md)。
