# Q3D 寄生矩陣提取規範

> [!NOTE]
> 本手冊依據官方知識字典 `q3d.md` 與 `pyaedt` 權威技術規格擴充，提供深度工程指導。

## 1. 原理與設定準則

本模組於高精度數值模擬時，必須遵循以下邊界設定與收斂規範：
- 數值精度與單位一致性：務必先確認全域坐標系統、材料參數庫與求解單位（MKS/SI）。
- 網格劃分策略：實施局部特徵網格加密，並於梯度變化劇烈區域進行自適應細化。
- 監控物理量：除了求解器預設殘差之外，必須定義面通量、力矩或特徵頻率等客觀物理監控器。

## 2. 核心規範與字典精要

# Q3D Extractor 知識字典

> 來源標示 Ansys Electromagnetics Suite 2026 R1；另外保留本機 v261 `Q3D_REPORT_EXPORT_API_DICTIONARY.md` 的 Reporter 匯出整理。該整理明確限定於單一命令，並非完整 API 清單。

## 腳本介面導覽

Q3D Extractor Scripting Guide 的目錄涵蓋 IronPython、CPython、external script、`ansysedt` gRPC server、Electronics Desktop conventions，以及 object／project／design 操作。實際腳本環境、物件和參數需直接對應 Q3D guide 條目，不因其與其他 Electronics Desktop products 共用 host 就推定命令行為完全一致。

來源：**Q3D Extractor Scripting Guide PDF sidecar**，PDF Page 1 標版本，Pages 3–6 列目錄。

## Scripting environments（v261／2026 R1）

手冊把 AEDT 腳本入口分成桌面內執行、Standalone IronPython 和 CPython 外部腳本。選擇時應看執行位置與連線方式；它們並非同一執行環境的可互換啟動參數。

| 環境 | 手冊列出的入口／連線 | 文件明示的邊界 |
| --- | --- | --- |
| 桌面內 IronPython | Tools > Open Command Window；Tools > Run Script（選 IronPython）；以 script argument 啟動產品；註冊為 Tools > External Tools | AEDT 提供預設變數與函式。Run Script 對話框的引數由 `ScriptArgument` 取得；`oDesktop` 可直接使用。 |
| Standalone IronPython | 以安裝目錄 `common/IronPython/ipy64.exe` 執行 `.py`，再透過 COM 取得 AEDT app handle | 手冊指出 standalone 不具備桌面內執行的全部功能，只完整支援 COM functions。 |
| CPython | 外部 Python interpreter 載入安裝目錄 `PythonFiles/DesktopPlugin` 下的 `ScriptEnv`；可用 `InitializeNew` 啟動新 AEDT，或用 `Initialize` 連線／必要時啟動 | CPython script engine 與 `ansysedt` 透過 gRPC 通訊；手冊說明預設從 50051 起尋找可用埠，亦可指定埠或埠範圍。 |

手冊另說明，現有 VBScript／JavaScript 資產可由 Python 呼叫對應的 `Run<*>Command` 方法重用，但無法取得那些 VBScript／JavaScript 呼叫的回傳值；需要雙向傳遞時，應由 Python 直接呼叫 scripting objects。此為手冊對 AEDT scripting 的描述，未在 Q3D／AEDT host 驗證安裝版本、COM 註冊、gRPC 連線或埠占用行為。

來源：**Q3D Extractor Scripting Guide PDF Pages 56–59**（桌面 IronPython、`ScriptArgument`、Standalone IronPython；印刷頁 1-4–1-7）、**PDF Pages 96–99**（CPython／gRPC；印刷頁 1-44–1-47）、**PDF Pages 57–58**（舊 VBScript／JavaScript 資產限制）。

## Reporter 匯出

在 v261／2026 R1 手冊的 Reporter Editor Script Commands 章節，命令透過 `ReportSetup` module 操作：先由 `oDesign.GetModule("ReportSetup")` 取得 module，再呼叫 `oModule.ExportToFile(<ReportName>, <FileName>)`。命令會將 data table 或 plot 匯出至檔案；`ReportName` 是報表名稱，`FileName` 是含路徑與檔名的目標。手冊的 UI 入口為在 Project tree 對報表名稱按右鍵並選 Export。文件列出的回傳值為 `None`。

此為手冊所列介面及行為，不代表所有 report type 都會產生相同欄位或單位；輸出內容應按實際報表設定及生成檔案確認。

來源：**Q3D Extractor Scripting Guide PDF**（Reporter command PDF Pages 794–795，印刷頁 10-56）、**Reporter 匯出 API 字典**；Reporter module 入口見 PDF Page 739。

## Nets 與 Source／Sink 激勵

Q3D 的 `AssignNet` 建立 net，輸入為命名結構陣列，至少指定 net 名稱及所指派物件。`AssignSource` 與 `AssignSink` 分別建立 current source 和 current sink；來源與接收端可按幾何種類以 `Objects:=`、`Faces:=` 或 `Edges:=` 提供 ID，並可指定 net 與 `TerminalType`。手冊列出的 terminal type 為 `UniformCurrent` 與 `ConstantVoltage`。

文件把 net association 列為可選參數，但同時明確提醒：在 simulation 前須將 source/sink 關聯至 net，simulation 才有效。這是文件的建模前置提醒，字典沒有推定分析結果或端子配置會自動正確。`AssignTerminals` 另有獨立命令與 1D/2D terminal 結構，不應與建立 net 或 source/sink 的命令混為一談。

來源：**Q3D Extractor Scripting Guide PDF Pages 1033–1037**（印刷頁 11-193–11-196）：`AssignNet`、`AssignSource`、`AssignSink`、`AssignTerminals`。版本為 Ansys Electromagnetics Suite 2026 R1／v261；未在 AEDT/Q3D 執行或求解。

## Python UDM／UDP 擴充

手冊區分 User Defined Primitive（UDP）與 User Defined Model（UDM）：Python UDP 實作 `UDPExtension`，Python UDM 實作 `UDMExtension`。腳本放在 `SysLib`、`UserLib` 或 `PersonalLib` 下的 `UserDefinedParts`／`UserDefinedModels` 子目錄，之後由相應 Draw 選單載入。`Lib` 子目錄不顯示於選單，其 helper scripts 可由沿途搜尋路徑匯入。

UDP 必須實作長度單位、primitive type／參數定義、參數有效性檢查及 `CreatePrimitive2` 等方法；幾何建立函式透過 function library 執行。UDM 必須提供 instance 建立及 `Refresh` 等方法，文件指出幾何建立／更新在 `Refresh` 中完成，並需提供 instance units 及釋放 instance 資源的 `ReleaseInstance`。支援 `refreshModifiedPartsOnly` 可作大型模型增量更新，但文件說明這項最佳化可選；不支援時應完整更新，不能回傳未更新的參數或假定部分更新已發生。這些是介面文件摘要，並非可直接執行的完整類別範本。

來源：**Q3D Extractor Scripting Guide PDF Pages 71–80**（印刷頁 1-19–1-28）：安裝路徑、helper library、UDP 必要／可選方法、UDM `Refresh` 與 function library。PDF 文字抽取可能破壞程式碼符號及縮排；編寫實際擴充前需以原 PDF 頁面核對完整簽名，並在目標 Q3D 版本驗證。

## PyAEDT Q3D API 範圍界線

除 Ansys 的 v261 Scripting Guide 外，本機 AEDT SDK 文件還索引 `ansys-aedt-core` 1.9.0 的 Q3D／2D Extractor API 頁面；來源清冊以產品 `aedt` 分類，文件路徑帶有 SDK 1.9.0，但 `docs_meta.release` 為 `unknown`。這些 API 頁面是 PyAEDT 封裝介面，不能視為 AEDT 原生 script command，也不能因目前目錄含 1.9.0 就推定產品 release 相同。

單以 SDK API reference 路徑及 `q3d.Q3d`／`q3d.Q2d` 原始來源路徑盤點，索引有 461 個 HTML 原始頁面（238 個 Q3d、223 個 Q2d）；本輪未逐頁檢查內容或同名 Markdown 轉換品質。此數量用於標示後續整理範圍，不等於完整 API 覆蓋。代表入口包括 Q3D `duplicate_design`、`setup_names` 及 `net_sources`，Q2D `auto_assign_conductors`；需以 AEDT／PyAEDT 模組獨立主題逐步整理，再決定清冊是否將其分類成 `q3d`、`q2d` 或沿用 `aedt`。

## 匯出格式與舊命令相容性

`ExportToFile` 條目列出的副檔名及文件說明：

| 副檔名 | 手冊說明 |
| --- | --- |
| `.txt` | Post processor format file |
| `.csv` | Comma-delimited data file |
| `.tab` | Tab-separated file |
| `.dat` | Ansys plot data file |
| `.rdat` | Ansys report data file |

手冊另記載，`ExportReport(<ReportName>, <FileName>)` 已被 `ExportToFile` 取代，但為既有腳本保留向後相容，並建議新腳本使用 `ExportToFile`。這是 2026 R1／v261 手冊的相容性說明，不推定其他 release 的支援狀態。附近的 `ExportReportDataToFile`、`ExportTableToFile` 與 `ExportUniformPointsToFile` 是各自獨立的命令條目；不要只因名稱相似就當作 `ExportToFile` 的參數變體。

來源：**Q3D Extractor Scripting Guide PDF**（`ExportReport` 相容說明，印刷頁 10-54）及 **PDF Pages 794–795**（格式表）。

## 來源清冊與處理狀態

| 項目 | 版本／類型 | 正文與轉換 | 狀態與限制 |
| --- | --- | --- | --- |
| Q3D Extractor Scripting Guide | v261／2026 R1 PDF | 原件 7,804,611 bytes；本機 PDF sidecar 有 1,787,220 chars，含 `## PDF Page N` 標記；catalog extraction status `extracted`，轉換狀態 `created_from_cache` | 正文可檢索；目前字典只整理腳本環境與 Reporter 匯出，未逐頁核讀其餘 methods／參數／範例。原件標示 proprietary/confidential，按授權限本機使用。 |
| Q3D Reporter 匯出 API 字典 | v261／本機衍生 Markdown | catalog 收錄，正文 1,118 chars | 僅為單條 `ExportToFile` 整理，依據回鏈官方手冊；不是完整 API 清單。 |
| HTML | v261／15 份官方 HTML | 15/15 HTTP 200；原始 HTML 與 Markdown 均保存在後表所列 ignored corpus，全文索引。 | 每頁可回官方 URL、來源 ID、raw HTML 與 Markdown；HTML 沒有實體頁碼，沿標題／段落定位。 |
| v261 官方來源 URL 清冊 | v261／15 HTML + 4 PDF | 清冊 19/19 URL HTTP 200；本機原文、轉換稿、SHA-256、頁數與轉換狀態逐項記錄。 | 下表列出來源 ID、官方 URL、gitignored 本地原件及轉換稿；HTML 依標題定位、PDF 使用本地 Markdown 頁標和 PDF `#page=`。分享授權仍待確認。 |

### 2026-11-05 官方來源逐筆定位

本表涵蓋已清冊的 19 個 v261 官方 URL（15 HTML、4 PDF）。19 份 Markdown 均已在本地索引；所有原件與轉換稿位於 gitignored 保護路徑。PDF Markdown 以 `<!-- page N -->` 分頁；超連結開啟本機稿後可按頁標搜尋，原始 PDF 亦附物理頁碼位置。HTML 沒有穩定的物理頁碼，因此以轉換稿標題及段落定位。逐頁文字相等不等於已核對圖表影像或版面。

| 文件 | 類型／版本 | 本機原文與轉換（gitignored） | 官方來源／本機位置與頁碼 |
| --- | --- | --- | --- |
| Welcome to Q3D Extractor | HTML／v261 | `online_q3d_v261_welcome` | [官方頁面](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Q3DExtractor/Content/GettingStarted/WelcometoQ3DExtractorHelp.htm)；**轉換 Markdown**；**原始 HTML**（HTML 無實體頁碼；依文件標題／段落定位） |
| Getting Started with Q3D Extractor | HTML／v261 | `online_q3d_v261_getting_started` | [官方頁面](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Q3DExtractor/Content/Variables/GettingStartedwithQ3DExtractor.htm)；**轉換 Markdown**；**原始 HTML**（HTML 無實體頁碼；依文件標題／段落定位） |
| Setting Up a Design in Q3D Extractor | HTML／v261 | `online_q3d_v261_design_setup` | [官方頁面](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Q3DExtractor/Content/Variables/SettingUpaDesigninQ3DExtractor.htm)；**轉換 Markdown**；**原始 HTML**（HTML 無實體頁碼；依文件標題／段落定位） |
| Assigning Nets Automatically | HTML／v261 | `online_q3d_v261_auto_nets` | [官方頁面](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Q3DExtractor/Content/Q3D/AssigningNetsAutomatically.htm)；**轉換 Markdown**；**原始 HTML**（HTML 無實體頁碼；依文件標題／段落定位） |
| Assigning Nets Manually | HTML／v261 | `online_q3d_v261_manual_nets` | [官方頁面](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Q3DExtractor/Content/Q3D/AssigningNetsManually.htm)；**轉換 Markdown**；**原始 HTML**（HTML 無實體頁碼；依文件標題／段落定位） |
| Assigning Terminals (Sources and Sinks) | HTML／v261 | `online_q3d_v261_terminals` | [官方頁面](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Q3DExtractor/Content/Q3D/AssigningTerminals.htm)；**轉換 Markdown**；**原始 HTML**（HTML 無實體頁碼；依文件標題／段落定位） |
| Using Reduce Matrix Operations in Q3D Extractor | HTML／v261 | `online_q3d_v261_reduce_matrix` | [官方頁面](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Q3DExtractor/Content/Q3D/UsingReduceMatrixOpsinQ3DExtractor.htm)；**轉換 Markdown**；**原始 HTML**（HTML 無實體頁碼；依文件標題／段落定位） |
| Solution Process | HTML／v261 | `online_q3d_v261_solution_process` | [官方頁面](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Q3DExtractor/Content/Q3D/SolutionProcess.htm)；**轉換 Markdown**；**原始 HTML**（HTML 無實體頁碼；依文件標題／段落定位） |
| Post Processing and Generating Reports in Q3D Extractor | HTML／v261 | `online_q3d_v261_postprocessing` | [官方頁面](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Q3DExtractor/Content/Q3D/PostProcessingandGeneratingReportsinQ3DExtractor.htm)；**轉換 Markdown**；**原始 HTML**（HTML 無實體頁碼；依文件標題／段落定位） |
| Spice Matrix | HTML／v261 | `online_q3d_v261_spice_matrix` | [官方頁面](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Q3DExtractor/Content/Q3D/SpiceMatrix.htm)；**轉換 Markdown**；**原始 HTML**（HTML 無實體頁碼；依文件標題／段落定位） |
| Setting Q3D Extractor Options | HTML／v261 | `online_q3d_v261_options` | [官方頁面](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Q3DExtractor/Content/Q3D/Q3DExtractorOptions.htm)；**轉換 Markdown**；**原始 HTML**（HTML 無實體頁碼；依文件標題／段落定位） |
| Q3D Extractor Getting Started Guides | HTML／v261 | `online_q3d_v261_guides_index` | [官方頁面](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Q3DExtractor/Content/GettingStarted/Q3DExtractorGettingStartedGuides.htm)；**轉換 Markdown**；**原始 HTML**（HTML 無實體頁碼；依文件標題／段落定位） |
| Assigning Contact Resistance Boundaries in Q3D Extractor | HTML／v261 | `online_q3d_v261_contact_resistance` | [官方頁面](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Q3DExtractor/Content/Q3D/AssigningContactResistanceBoundaries.htm)；**轉換 Markdown**；**原始 HTML**（HTML 無實體頁碼；依文件標題／段落定位） |
| Help Menu | HTML／v261 | `online_q3d_v261_help_menu` | [官方頁面](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Q3DExtractor/Content/GettingStarted/HelpMenu.htm)；**轉換 Markdown**；**原始 HTML**（HTML 無實體頁碼；依文件標題／段落定位） |
| Q3D Extractor PDFs | HTML／v261 | `online_q3d_v261_pdf_catalog` | [官方頁面](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Q3DExtractor/Content/Q3D_PDFs.htm)；**轉換 Markdown**；**原始 HTML**（HTML 無實體頁碼；依文件標題／段落定位） |
| Q3D Extractor Help PDF | PDF／v261 | `online_q3d_v261_help` | [官方頁面](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/PDFs/Q3D%20Extractor.pdf)；**Markdown p.1–2430**；**原始 PDF**（全文 PDF Pages 1–2430；逐頁文字比對通過；其餘命令待逐章主題化） |
| Q3D Extractor Scripting Guide PDF | PDF／v261 | `online_q3d_v261_scripting` | [官方頁面](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/PDFs/Q3D%20ExtractorScriptingGuide.pdf)；**Markdown p.1–1800**；**原始 PDF**（全文 PDF Pages 1–1800；逐頁文字比對通過；字典核對頁 56–59、71–80、96–99、792、794–795、1033–1037、1116–1122、1135–1136、1239–1244） |
| Q3D Extractor 3D PCB Via Model Getting Started PDF | PDF／v261 | `online_q3d_v261_3d_via` | [官方頁面](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/PDFs/Q3D%20Extractor%20A%203D%20PCB%20Via%20Model.pdf)；**Markdown p.1–61**；**原始 PDF**（全文 PDF Pages 1–61；逐頁文字比對通過；字典摘要 pp.5–7、37–43；表格核對 pp.27、51、57） |
| 2D Extractor Grounded Coplanar Waveguide Getting Started PDF | PDF／v261 | `online_q3d_v261_2d_cpw` | [官方頁面](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/PDFs/2D%20Extractor%20A%202D%20Grounded%20Coplanar%20Waveguide%20Model.pdf)；**Markdown p.1–51**；**原始 PDF**（全文 PDF Pages 1–51；逐頁文字比對通過；字典摘要 pp.5–7；封面疑似表格不作表格驗收） |


catalog 文件 ID：手冊 `ansys_519cef8fcfec74fabeb25e81`；衍生字典 `ansys_981395211f371ccb2223eeea`。既有 catalog PDF SHA-256：`c8b9e6c0ec4d712c204e7832c490656daf0a455d2e9efa2992b2df50af5f285f`。本機 PDF 文字 sidecar：**Q3D PDF text**。既有本地轉換稿：**Q3D ExtractorScriptingGuide.md**。注意：上方 2026-11-05 官方 URL 擷取的 Scripting Guide 原始 PDF SHA-256 為 `8726ebc7ebfcde4555329ed3b42644f575524f8c8dd425ffcb2da34fc5e5ea6c`，與舊 catalog PDF 不同；兩者均標 v261，但本字典不假定其二進位內容相同。新擷取版本的來源、Markdown 及頁數另列於逐來源表。

## 仍待整理與驗證

- 將 PDF 目錄列出的各章節及命令拆成主題，先核對原文的 API 物件、參數表、回傳值及示例；不可由 AEDT 通用文件推定 Q3D 行為。
- 轉換稿含頁標記且本次抽查的頁碼可定位；全書表格與圖片／掃描品質尚未全面逐頁抽查，不宣稱所有版面均無損。
- 目前未執行 Q3D host 腳本。Reporter 匯出檔格式內容及 CPython／COM／gRPC 連線都只是文件所述，仍需在目標版本做功能驗證。
- 主題 upsert 建議、檢索抽查及缺口記錄見**本輪 Q3D 維護報告**。


## PyAEDT Q3D API 的範圍界線

除了 Ansys v261 Scripting Guide，本機 AEDT SDK 文件還索引 `ansys-aedt-core` 1.9.0 的 Q3D／2D Extractor API 頁面；來源清冊以產品 `aedt` 分類，路徑帶有 SDK 1.9.0，但 `docs_meta.release` 為 `unknown`。這些頁面描述 PyAEDT 封裝介面，不能視為 AEDT 原生 script command，也不能由 SDK 路徑推定產品 release。

本機全文索引按 `Q3d.Q3d` 及 `Q3d.Q2d` 原始路徑找到 461 個 PyAEDT SDK HTML API 頁面（238 個 Q3d、223 個 Q2d）；本輪未逐頁檢查內容或同名 Markdown 轉換品質。這個數量表示待整理範圍，不代表 API 覆蓋完整。代表頁面含 Q3D `duplicate_design`、`setup_names`、`net_sources`，以及 Q2D `auto_assign_conductors`。應以 AEDT SDK 獨立主題整理，再決定清冊分類，不與 Q3D 原生手冊混列。

逐來源狀態見**Q3D 來源清冊**及**本輪覆核報告**。


## Q3D solution setup 與 matrix quantities（v261）

Q3D 分析設定由 `AnalysisSetup` module 建立；`InsertSetup` 的 setup type 是 `"Matrix"`。頂層結構含 setup 名稱、`AdaptiveFreq`、`SaveFields` 與 `Enabled`，並可帶入 `Cap`、`DC`、`AC` 區塊；這些是不同求解量的設定欄位，不能把某個區塊缺省解讀成所有 quantities 都會計算。

- `Cap` 區塊包含最大／最小 adaptive passes、最小收斂 pass、誤差與網格細化百分比；另有自動提高解階、解階、solver type。選 `Direct` 時可以提供 compression tolerance，手冊要求在 `Iterative` 情況省略該欄位。
- `DC` 區塊的 `SolveResOnly=True` 表示只求 resistance；`False` 表示求 resistance／inductance。其下分成 `Cond`（conduction）與 `Mult`（inductance）兩組 pass／誤差／細化參數，另有 solution order。
- `AC` 區塊在此命令格式列出 pass 數、收斂 pass、誤差與細化參數。
- `InsertSetup` 只建立設定；若要啟動分析，手冊另列 `SolveSetup(<SetupName>)`。字典僅說明命令邊界，不代表本輪有建模或求解。

手冊範例中的 `1GHz` adaptive frequency、pass 數、`PerError=1`、`PerRefine=30`、`High` solution order 等是範例資料，不構成 Q3D 通用建議、收斂保證或物理精度門檻。正式設定須依模型、所需矩陣量及目標版本文件確認。

來源：**Q3D Extractor Scripting Guide PDF Pages 1116–1122**（印刷頁 13-36–13-42，`InsertSetup (Q3D Extractor)` 結構與範例）；**PDF Pages 1135–1136**（印刷頁 13-55–13-56，`SolveSetup`）。本輪未在 AEDT host 執行，PDF 表格與程式範例未做影像逐頁比對。


## 手冊章節追蹤狀態

手冊目錄共 26 章。逐章追蹤表依 PDF Contents 的章名與印刷起始頁建立；`selected_pages_reviewed` 只代表列出的實體 PDF 頁被核讀，所在章的其他命令、欄位、表格及範例仍可能待整理。現有核讀落在第 1、10、11、13、15 章，其餘 21 章尚未逐章語意核讀。完整章名、目錄所在實體頁、印刷起始頁、各章目錄命令／條目（合計 1,376 筆目錄文字）、狀態及已核頁碼見**Q3D 逐章覆蓋清冊**。此清冊列的是來源目錄，不代表 26 章已完成。


## `EditSources` 後處理激勵表（Q3D v261）

`Solutions` module 的 `EditSources(acData, capData, dcData, harmonicLossData)` 對應 UI 的 Fields > Edit Sources，用來設定欄位後處理各 tab 的 source 數值。手冊特別指出 Q3D 與 2D Extractor 使用不同的結構；不可直接把 Q3D 參數陣列套用到 2D。

Q3D 的四組資料分別對應 AC RL、CG、DC RL、Harmonic Loss。AC 與 DC 可將 `Value Type` 設為 voltage (`V`) 或 current (`A`)，並以同順序的 source name、magnitude、phase 陣列配對；CG tab 的 `Value Type` 為 `N`（null），資料同樣按來源名稱及 magnitude／phase 對位。DC 區塊另有 `DC Loss Type`，手冊列出 `True DC Loss` 與 `DC Loss Including Low Frequency Sinusoidals` 兩種計算假設。Harmonic Loss 區塊將來源名稱與 real／imag current dataset names 依相同順序對應。

這個命令配置的是 Fields 後處理的來源值，不等於先前 `AssignSource`／`AssignSink` 的幾何端子指派；二者用途不同。文件中的範例轉換文字有陣列換行與符號失真，因此此處只整理參數語義，不複製範例陣列當作可執行程式。

來源：**Q3D Extractor Scripting Guide PDF Pages 1239–1244**（印刷頁 15-5–15-10，`EditSources` 的 Q3D／2D 區別、AC／CG／DC／Harmonic Loss 結構）。本輪未執行 `EditSources` 或 AEDT host。

## v261 線上教學入口：2D 波導與 3D PCB Via

官方目錄列出兩本 2026 R1 教學；本輪已保存 3D PCB Via（61 頁）與 2D Grounded Coplanar Waveguide（51 頁）PDF，逐頁轉換及文字比對通過。兩者流程與適用對象不同；全文已可檢索，但本節只整理有限頁面的主題摘要，不代表逐圖／逐表人工核讀：

| 教學 | 模型與文件中列出的流程 | 來源 |
| --- | --- | --- |

## 3. 常見陷阱與防呆措施

1. **未定義求解範圍**：求解前未限定掃頻範圍或時間步長，導致求解發散。
2. **材料模型失配**：非線性材料未設定適當的切線模數或溫度相依曲線。
3. **介面通訊失敗**：多物理場耦合未對齊變數傳遞單位，導致數值非物理震盪。
