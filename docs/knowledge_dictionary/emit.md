# Ansys EMIT 知識字典

本頁整理 Ansys Electronics Desktop 的 EMIT 射頻干擾（RFI）入門、腳本與教學導覽。本機 PDF 封面均為 **Release 2026 R1／January 2026（v261）**。以下頁碼一律為 PDF 實頁；例如 Scripting 的實頁 63 對應印刷頁 1-47。`complete` 僅表示清冊所列的有界主題已依來源整理，完整物理理論、API 及全部圖表仍有缺口。

EMIT 以不同精細程度（multi-fidelity）的 Tx／Rx 模型及天線耦合資料評估 RFI；官方入口列出 EMI Margin、Sensitivity、Desense、Availability 等指標。增加量測或模型資訊可改善模型描述；本頁沒有為任意情境給出準確度保證。來源：[EMIT Help](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/EMIT/Content/GettingStarted/WelcometoEMITHelp.htm)（[來源清冊](sources.csv#official_emit_welcome_v261)）。

## 本機來源與逐頁文字

| 文件 | 實頁數 | 逐頁文字入口 | 來源 ID |
| --- | ---: | --- | --- |
| EMIT Getting Started Guide | 8 | [封面／逐頁 Markdown](../ANSYS_Document/_catalog/pdf_text_v4/0c3441f7d99aa92a82c3ad9e355a661575b100a7f86daa7befa2ffa260d1a477.md#pdf-page-1) | [來源清冊](sources.csv#ansys_c657170da6fb87e3d7a54b84) |
| EMITScriptingGuide | 324 | [封面／逐頁 Markdown](../ANSYS_Document/_catalog/pdf_text_v4/305db5a7489814a325d2d538ccc23ed150e63b5cc75512bc97dbb77ea65c86cd.md#pdf-page-1) | [來源清冊](sources.csv#ansys_3ca212f89dc7a8ed85bd5702) |
| Tutorial 1 | 38 | [封面／逐頁 Markdown](../ANSYS_Document/_catalog/pdf_text_v4/64319d67971f850343fcb0e4f2581e27af3125079576f62eb7b452e9b0cbea09.md#pdf-page-1) | [來源清冊](sources.csv#ansys_0a0b3c43a0c9da85ecbf6e0b) |
| Tutorial 2 | 27 | [封面／逐頁 Markdown](../ANSYS_Document/_catalog/pdf_text_v4/730b74efce0856c0d528563ce28bcbcd1100410411c6150db375b299d404773a.md#pdf-page-1) | [來源清冊](sources.csv#ansys_e2192aa85f362d6bdadd8795) |
| Tutorial 3 | 36 | [封面／逐頁 Markdown](../ANSYS_Document/_catalog/pdf_text_v4/29aa78718a535d897b8417da98d3430e657d7e12b20150169ff6481f22326885.md#pdf-page-1) | [來源清冊](sources.csv#ansys_334335a06eefb0179fe18391) |
| Tutorial 4 | 34 | [封面／逐頁 Markdown](../ANSYS_Document/_catalog/pdf_text_v4/36a0c1391d80bb1ad1c776702d0fb973e54f1047a3752e47634ec099754df3f2.md#pdf-page-1) | [來源清冊](sources.csv#ansys_89b22ba722a15dc10fb19c0a) |
| Tutorial 5 | 20 | [封面／逐頁 Markdown](../ANSYS_Document/_catalog/pdf_text_v4/ada3a353027517dbf4d8046da98cffb1d1bf6500a760a77c220d87f0c966d688.md#pdf-page-1) | [來源清冊](sources.csv#ansys_4df00a4bea46795b52873eab) |
| Tutorial 6 | 36 | [封面／逐頁 Markdown](../ANSYS_Document/_catalog/pdf_text_v4/4ede16f6b361d0300a86e8015e47973b99d2b1746982b1483a550b761ee63325.md#pdf-page-1) | [來源清冊](sources.csv#ansys_10a274f5ffe86236d44a3334) |
| Tutorial 7 | 20 | [封面／逐頁 Markdown](../ANSYS_Document/_catalog/pdf_text_v4/b30d3099cfb71214b082b1c6c8293381d28898379d29b92175907ce16aed7b2e.md#pdf-page-1) | [來源清冊](sources.csv#ansys_1e84345f7b3c5587c6fc24d3) |
| Tutorial 8 | 26 | [封面／逐頁 Markdown](../ANSYS_Document/_catalog/pdf_text_v4/d690ccc29ed27aeabacbd6cfbb25bdc769f967da5a4037c36de0a7de6202cdf2.md#pdf-page-1) | [來源清冊](sources.csv#ansys_50785b3a8097895820665c03) |

兩份 EMIT PDF 的 catalog 產品標籤目前是 `general`，八份 Tutorial 是 `ansysem`；這些來源 ID 可跨主題引用。以 `product=emit` 搜尋主要會找到本字典；原文也可依來源 ID 搜尋。來源分類不在本次改寫範圍內。

## 入門案例與文件導覽

Getting Started 實頁 7 列出 `AH-64 Apache Cosite`、`Cell Phone RFI Desense`、`PlanarInvertedF_MIPI_C_Demonstration`。操作入口為 `File > Open Examples`，再開 EMIT 資料夾；選入專案後，Project Manager 可提供詳細 PDF 導覽。原文安裝範例路徑為 `C:\Program Files\ANSYS Inc\v261\AnsysEM\Examples\EMIT\Tutorials`。這個清單沒有逐一證明各案例內的無線電種類或授權 feature 名稱。

來源：[Getting Started 實頁 7](../ANSYS_Document/_catalog/pdf_text_v4/0c3441f7d99aa92a82c3ad9e355a661575b100a7f86daa7befa2ffa260d1a477.md#pdf-page-7)、[來源清冊](sources.csv#ansys_c657170da6fb87e3d7a54b84)。

## 操作說明與線上說明

本機 Getting Started 實頁 4 說明產品 Help、Scripting Help 與 Getting Started Guides，並說明 F1 依活動 design type／游標對應項目開啟說明。v261 線上 Help Menu 的實際選單列為 **EMIT Help、EMIT Scripting Help、EMIT PDFs**；Student 版只有 PDF documentation。兩份來源描述層級不同，操作時以所用版本的選單為準。

來源：[Getting Started 實頁 4](../ANSYS_Document/_catalog/pdf_text_v4/0c3441f7d99aa92a82c3ad9e355a661575b100a7f86daa7befa2ffa260d1a477.md#pdf-page-4)、[v261 Help Menu](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/EMIT/Content/GettingStarted/HelpMenu.htm)（[來源清冊](sources.csv#official_emit_help_menu_v261)）。

## 腳本與 AEDT 自動化入口

EMIT Scripting Guide 同時包含 AEDT 共用腳本介紹與物件命令。`oDesktop` 的存在不代表任意 HFSS／Circuit 命令都適用於 EMIT；應回到各命令的參數、回傳值與設計類型。原本字典中的未核對 PyAEDT 求解範例已移除，本頁保留文件定義與導航。

### v261 IronPython 與 CPython 邊界

Scripting 實頁 18 明列 IronPython **2.7**、.NET Framework **4.0**，並提醒依賴 C extension 的 Python library（原文舉 NumPy／SciPy）不可直接假設可用。實頁 17 列出的 PyAEDT（Beta）是該版文件中的入口描述；不能從這個標籤推定目前 PyAEDT 套件的 API／版本狀態。

CPython 節使用 `ScriptEnv` 與 AEDT gRPC server；它與以 `ansys.aedt.core.Emit` 為入口的 PyAEDT 介面應分別查證。來源：[實頁 17–18](../ANSYS_Document/_catalog/pdf_text_v4/305db5a7489814a325d2d538ccc23ed150e63b5cc75512bc97dbb77ea65c86cd.md#pdf-page-17)、[實頁 56](../ANSYS_Document/_catalog/pdf_text_v4/305db5a7489814a325d2d538ccc23ed150e63b5cc75512bc97dbb77ea65c86cd.md#pdf-page-56)、[來源清冊](sources.csv#ansys_3ca212f89dc7a8ed85bd5702)。

### GUI、命令列與 ScriptArgument

`Tools > Run Script` 或 Automation tab 的 Run Script 可執行 `.py`，並提供 Script Arguments；執行中可 Stop／Pause／Resume。命令列可使用 `-runscriptandexit` 或 `-runscript` 與 `-scriptargs`。實頁 64 明確說明 `-scriptargs` 後的內容不修改地作為**單一字串（single string）**傳入 `ScriptArgument`，不能假設自動成為列表。這兩頁未完整定義兩個 runscript 模式的全部生命週期差別。

來源：[實頁 20–21](../ANSYS_Document/_catalog/pdf_text_v4/305db5a7489814a325d2d538ccc23ed150e63b5cc75512bc97dbb77ea65c86cd.md#pdf-page-20)、[實頁 63–64](../ANSYS_Document/_catalog/pdf_text_v4/305db5a7489814a325d2d538ccc23ed150e63b5cc75512bc97dbb77ea65c86cd.md#pdf-page-63)、[來源清冊](sources.csv#ansys_3ca212f89dc7a8ed85bd5702)。

### ScriptEnv 初始化與連接

| 入口 | 實頁 57–58 定義的界線 |
| --- | --- |
| `Connect(projectPath)` | 連接已開啟專案，或啟動並開啟該專案；專案不存在報錯。 |
| `Connect(portNumber)` | 連接本機該 port 上的既有 AEDT，沒有 listener 報錯。 |
| `Connect(machine, projectPath)` | 連接遠端已開啟專案，路徑須為 network path；未開啟報錯。 |
| `Connect(machine, portNumber)` | 連接指定遠端 port 的既有 AEDT。 |
| `InitializeNew(...)` | 總是啟動新 instance；原文此處限制在本機，`Machine` 留空。 |
| `Initialize(..., port=...)` | 嘗試連接，必要時啟動；port=0 時從 50051 起找可用 port。 |
| `ScriptEnv.Shutdown()` | 文件指定用於結束腳本／Desktop；多腳本時只放最後一份末尾。 |

`-grpcsrv` 頁面內有原文差異：實頁 56 說預設從 50051 起找可用埠，實頁 59 說省略埠使用 50051；實頁 58 又依 `Initialize`／`InitializeNew` 分別描述。選定介面後應依其說明與實際版本確認，不能把所有啟動路徑視為完全相同。來源：[實頁 56–59](../ANSYS_Document/_catalog/pdf_text_v4/305db5a7489814a325d2d538ccc23ed150e63b5cc75512bc97dbb77ea65c86cd.md#pdf-page-56)、[來源清冊](sources.csv#ansys_3ca212f89dc7a8ed85bd5702)。

### AEDT 腳本物件階層

| 物件 | 文件用途 |
| --- | --- |
| `oAnsoftApp` | 取得 Electronics Desktop 的應用程式 handle。 |
| `oDesktop` | Desktop 層級操作與專案管理。 |
| `oProject` | 已開啟專案的 variables、materials、designs。 |
| `oDesign` | 設計與其 variables、modules、editors。 |
| `oEditor` | 特定 editor 的資料操作；其名稱／功能須依 design 查證。 |
| `oModule` | 設計內一組相關功能。 |

實頁 61 特別指出 Reporter Editor 沒有對應的 `oEditor` object，其命令由 `oDesign` 執行。實頁 62 的 `BoundarySetup`／`3D Modeler` 範例是 AEDT 共用示例，不在本頁當成 EMIT 專屬可執行範例。來源：[實頁 59–62](../ANSYS_Document/_catalog/pdf_text_v4/305db5a7489814a325d2d538ccc23ed150e63b5cc75512bc97dbb77ea65c86cd.md#pdf-page-59)、[來源清冊](sources.csv#ansys_3ca212f89dc7a8ed85bd5702)。

### Named arguments 與數值

命名資料／陣列使用 `<Name>:=` 或陣列首項 `NAME:<name>`，用來識別後續值的意義。原文說錄製腳本可能包含完整資料；手寫變更時可按具體命令只提供需要改動的命名資料。數值參數可依該命令接受數字、含單位字串或變數；不可刪除命名標記後期待等效重播。

來源：[實頁 67–69](../ANSYS_Document/_catalog/pdf_text_v4/305db5a7489814a325d2d538ccc23ed150e63b5cc75512bc97dbb77ea65c86cd.md#pdf-page-67)、[來源清冊](sources.csv#ansys_3ca212f89dc7a8ed85bd5702)。

## 教學檔與重複來源

下表是實頁 5–6 的目標與前置導覽，沒有宣稱所有操作步驟、結果或模型預設已驗證。

| Tutorial | 已核對的範圍 | 專案前置 | 來源 |
| --- | --- | --- | --- |
| 1 | 1-Tx／1-Rx、固定 ATA coupling、EMI margin 與 filter mitigation | 新建案例 | [實頁 6](../ANSYS_Document/_catalog/pdf_text_v4/64319d67971f850343fcb0e4f2581e27af3125079576f62eb7b452e9b0cbea09.md#pdf-page-6)、[來源清冊](sources.csv#ansys_0a0b3c43a0c9da85ecbf6e0b) |
| 2 | 多 channels、random sampling、Scenario Details／Availability | Tutorial 1 | [實頁 6](../ANSYS_Document/_catalog/pdf_text_v4/730b74efce0856c0d528563ce28bcbcd1100410411c6150db375b299d404773a.md#pdf-page-6)、[來源清冊](sources.csv#ansys_e2192aa85f362d6bdadd8795) |
| 3 | 多 Tx／Rx、N-on-1、outboard amplifier 與 inter-Tx intermodulation | Tutorial 1 | [實頁 6](../ANSYS_Document/_catalog/pdf_text_v4/29aa78718a535d897b8417da98d3430e657d7e12b20150169ff6481f22326885.md#pdf-page-6)、[來源清冊](sources.csv#ansys_334335a06eefb0179fe18391) |
| 4 | CAD 平台、antennas、ATA coupling models 與 Coupling Matrix | 獨立，新建 aircraft／four antennas | [實頁 6](../ANSYS_Document/_catalog/pdf_text_v4/36a0c1391d80bb1ad1c776702d0fb973e54f1047a3752e47634ec099754df3f2.md#pdf-page-6)、[來源清冊](sources.csv#ansys_89b22ba722a15dc10fb19c0a) |
| 5 | 依 WiFi 6 說明建立 receiver susceptibility model | 獨立 | [實頁 6](../ANSYS_Document/_catalog/pdf_text_v4/ada3a353027517dbf4d8046da98cffb1d1bf6500a760a77c220d87f0c966d688.md#pdf-page-6)、[來源清冊](sources.csv#ansys_4df00a4bea46795b52873eab) |
| 6 | EMIT Elements Library、library components、tunable filters／larger scenarios | Tutorial 4 | [實頁 6](../ANSYS_Document/_catalog/pdf_text_v4/4ede16f6b361d0300a86e8015e47973b99d2b1746982b1483a550b761ee63325.md#pdf-page-6)、[來源清冊](sources.csv#ansys_10a274f5ffe86236d44a3334) |
| 7 | 從 manufacturer specification sheet 建立 detailed radio model | 獨立 | [實頁 6](../ANSYS_Document/_catalog/pdf_text_v4/b30d3099cfb71214b082b1c6c8293381d28898379d29b92175907ce16aed7b2e.md#pdf-page-6)、[來源清冊](sources.csv#ansys_1e84345f7b3c5587c6fc24d3) |
| 8 | IoT module、personal library models 與 Desense metrics | 獨立 | [實頁 6](../ANSYS_Document/_catalog/pdf_text_v4/d690ccc29ed27aeabacbd6cfbb25bdc769f967da5a4037c36de0a7de6202cdf2.md#pdf-page-6)、[來源清冊](sources.csv#ansys_50785b3a8097895820665c03) |

### Tutorial 1：固定天線耦合的基準

實頁 6 使用 frequency-independent coupling 的 1-Tx／1-Rx 情境，檢視 EMI margin 並加 filter 緩解。頁中的 50 MHz／40 dBm Tx、500 MHz Rx 與 -100 dBm susceptibility 是**教學設定**，不移用為產品預設或工程驗收門檻。來源：[Tutorial 1 實頁 6](../ANSYS_Document/_catalog/pdf_text_v4/64319d67971f850343fcb0e4f2581e27af3125079576f62eb7b452e9b0cbea09.md#pdf-page-6)。

### Tutorial 2：channels、sampling 與 Availability

實頁 6 以前一教學專案為起點，加入多 channels 與 random sampling，導覽 Scenario Details 及 Availability。原文要求 Save As 為 Tutorial 2，刪除 Tutorial 1 的 Tx low-pass filter 並重接 antenna；不能把舊 filter 狀態默認沿用。來源：[Tutorial 2 實頁 6](../ANSYS_Document/_catalog/pdf_text_v4/730b74efce0856c0d528563ce28bcbcd1100410411c6150db375b299d404773a.md#pdf-page-6)。

### Tutorial 3：多 Tx 與 inter-Tx coupling

實頁 6 說明多 Tx 同時作用於 victim Rx 時，除了直接信號疊加，還需考慮 Tx 間耦合、PA 非線性所生的 intermodulation。教學使用固定 Global Default Coupling=-40 dB，因此該情境的 antenna 位置不影響此固定耦合設定；不是所有 EMIT coupling model 都不受位置影響。來源：[Tutorial 3 實頁 6](../ANSYS_Document/_catalog/pdf_text_v4/29aa78718a535d897b8417da98d3430e657d7e12b20150169ff6481f22326885.md#pdf-page-6)。

### Tutorial 4：CAD 與 ATA Coupling Matrix

實頁 6 建立 aircraft 與四根 antenna，探索 ATA models、Coupling Editor 及 Antenna Coupling Matrix。它是獨立教學；導覽沒有要求先執行 HFSS 求解。本頁不把所有 ATA model 的數值條件或 HFSS coupling 匯入 API 視為已核對。來源：[Tutorial 4 實頁 6](../ANSYS_Document/_catalog/pdf_text_v4/36a0c1391d80bb1ad1c776702d0fb973e54f1047a3752e47634ec099754df3f2.md#pdf-page-6)。

## 轉換與來源缺口

10 份原始 PDF、canonical v4 逐頁文字及同名 Markdown 都已有產物，本輪沿用並核對來源／轉換 SHA。八份教學目前位於 `AnsysEM/v261/manuals`；extraction manifest 留有從 EMIT 路徑指向它們的歷史 `deduplicated_to`。該紀錄不表示歷史兩個檔案的 bytes／SHA 相同，也不保證教學 `.aedt` inputs 已在本機可執行。

本輪有界核讀：Getting Started 4／7、Scripting 17–21／56–64／67–69、Tutorial 1–8 的封面／目錄／實頁 6。完整 EMIT Theory、全部 radio／coupling API、後續教學圖表、PyAEDT 版本配對與產品 runtime 未驗證；來源總覽主題保留 `source_limited`。兩個官方 HTML 僅記摘要與 URL，全文未離線快取。

相關字典：[AnsysEM](ansysem.md)、[HFSS](hfss.md)、[Circuit](circuit.md)。


## 2026-11-04：Wave 9 本機來源盤點與限制說明

本批完成 emit 模組既有本機 catalog 文件（共 0 筆）與 sources 清冊（共 2 筆）之完整雜湊、正文路徑與標籤結構核對。本機未快取或具備企業授權/登入限制之線上主題誠實標記為缺口（保持現有非 complete 狀態），未擅自虛構未核實之線上 API 簽名或執行求解運算。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/emit_module_conversion_report_20261104.md)。
