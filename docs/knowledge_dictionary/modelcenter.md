# Ansys ModelCenter 主題字典

本機來源以 ModelCenter 開發者文件為主，包含 v261（2026 R1）COM、Java、Remote Execution、ScriptWrapper、Component Plug-in 與 custom optimization algorithm SDK。產品入口頁版本未知；下列 SDK API 依各自文件版本標示，不互相推定相容性。

## 產品定位與 API 家族

官方開發者入口將 ModelCenter 描述為支援多領域分析與設計最佳化（MDAO）、可整合 MBSE frameworks 的 model-based systems engineering 軟體。API 與 libraries 用於自動化跨領域工作流、整合工程工具、擴充 plugin、後處理，以及遠端連接 workflow。

入口頁列出的 API／library 平台為 Windows、Linux；語言包含 Python、Java、C++（COM）與 C#／.NET。v261 開發文件拆分為多個獨立 API 或 SDK：

| 文件族 | v261 文件描述的範圍 |
| --- | --- |
| ModelCenter COM API | 以 COM 自動化、客製化或擴充 ModelCenter；文件說明核心物件、components、assemblies、data 及介面。 |
| ModelCenter Java API | Java packages 與 ModelCenter API 類別。 |
| Remote Execution Java API | 遠端執行相關 Java API，另有獨立 Getting Started 與 classpath 指引。 |
| ScriptWrapper API | 腳本可用的全域 `wrapper` 物件、各類變數物件與檔案解析能力。 |
| Component Plug-in SDK | 建立 PACZ（parametric analysis component zipped）component plug-in。 |
| Custom Optimization Algorithm SDK | 建立及執行自訂最佳化演算法，生命週期由 `IAlgorithm` 等介面描述。 |

### COM 與 Java API v261 文件入口

| API | 官方索引頁明示的範圍 | 可回查的入口線索 |
|---|---|---|
| ModelCenter COM API | 以 COM 技術自動化、客製化、擴充 ModelCenter；可程式化控制、整合外部應用，並以 Python、VBScript 或 C# 開發 plugin／automation scripts；索引說明可查 core objects、components、assemblies、data、classes、interfaces、methods、properties | COM API index；頁面更新日期 2026-06-18 |
| ModelCenter Java API | 索引列出 `com.phoenix_int.ModelCenter`、`com.phoenix_int.ModelCenter.Geometry`、`com.phoenix_int.ModelCenter.logging`、`com.phoenix_int.ModelCenter.util` 四個 package | Java API index；頁面更新日期 2026-06-18 |

兩頁均來自 ModelCenter APIs 2026 R1 文件集合，來源清冊標 `v261`。這些索引可用來選擇文件族與深入 package／class reference；它們沒有建立 COM 與 Java 的 feature parity、互通型別對照或部署相容矩陣。範例或方法簽名需再開啟各自 API reference，不能只依索引頁實作。

來源：[ModelCenter COM API index（v261）](../ANSYS_Document/ModelCenter/v261/api_reference/bc5477e4834a-index.md)（`ansys_e5d064d3aa0c74340efef493`）；[ModelCenter Java API index（v261）](../ANSYS_Document/ModelCenter/v261/api_reference/3422bd6007b1-index.md)（`ansys_1ac461d0254dd4bc2e03af5b`）。未啟動 ModelCenter、呼叫 COM／Java API 或驗證跨語言相容性。

### Remote Execution Java API 設定與連線生命週期

ModelCenter Remote Execution（MCRE）Java API 2026 R1 的 Getting Started 頁面更新日期為 2026-06-22；指南要求使用目標 MCRE 安裝所支援的 JDK、確保 MCRE 已安裝且授權，或可透過網路連到授權伺服器，並將該安裝或 SDK 所提供的 Java API JAR 加入 classpath。文件列出 IDE module dependency、Maven `system` scope 與 Gradle `files()` 等 classpath 方式；沒有據此推定 JAR 發佈到一般 Maven repository。

| 用途 | API／文件說明 | 注意事項 |
|---|---|---|
| 建立連線 client | `com.phoenix_int.aserver.client.v2.AnalysisServerClient` 是 Getting Started 指定的主要入口。 | classpath 需使用與目標 MCRE／SDK 相符的 JAR。 |
| 連線到內嵌 instance | `connectEmbedded()` 連到 in-process MCRE。 | 不代表可連到任意外部 server。 |
| 連線到遠端 instance | `connect(URI)` 接受 MCRE URI，指南舉例 `mcre://hostname`。 | server 若要求認證，使用帶 username／password 的 `connect` overload；不在文件中保存或貼出憑證。 |
| 查連線狀態與關閉 client | `isConnected()`、`getUri()`、`getHostname()` 可檢查連線；`close()` 關閉 client 與 server 的連線。 | `close()` 與下列 `quit(...)` 是不同操作。 |
| 結束 MCRE 執行個體 | API reference 將 `quit(background)` 描述為強制結束目前 analysis 並關閉 MCRE。 | 這有 server／analysis 副作用；不可把它當一般 client cleanup。 |

`AnalysisServerClient` API reference 將常用能力分成以下方法家族；這是查找地圖，不保證每個 server、component 或 workflow 都支援相同操作：

| 能力 | API reference 中的代表入口 | 使用前要確認 |
|---|---|---|
| 分析與資料夾探索 | `listAnalyses(...)`、`listFolders(...)` | `folderPath` 可為 `null`；回傳清單不等同於已啟動 analysis。 |
| Analysis instance 控制 | `start(analysis, instanceName)`、`execute(instanceName, background)`、`end(instanceName)` | reference 分別描述建立 instance、執行與結束；實際執行順序、錯誤處理及是否背景執行，應依所用 workflow 與 method detail 核對。 |
| 變數值與資料結構 | `get(...)`／`set(...)`，另有 dimensions、hierarchy、file 及 URL 相關方法 | 核對完整 variable path、資料型別、陣列維度與傳輸方法；不能只依簡化方法名稱推定資料轉換。 |
| 非同步呼叫與監看 | 多數 client 操作有 `...Async` 變體；package overview 另列 process／output monitors | 非同步呼叫使用 callback；需處理 callback、連線與通訊錯誤。 |
| 元件、PACZ 與資料型別 | component library、PACZ API、`com.phoenix_int.aserver.types` | overview 說明型別可帶 description、units 等 metadata；本表未涵蓋每個 PACZ／component interface。 |

Package overview 另將 client、component library、monitor、types、utility、ScriptWrapper 與 PACZ API 分開列示。完整 method signatures、exceptions、callback contract 及 component-specific 行為，仍以對應 class reference 為準。

來源：[Remote Execution Java API Getting started（2026 R1；更新 2026-06-22）](../ANSYS_Document/ModelCenter/v261/api_reference/modelcenter-remote-execution-java-api-2026-r1/started.md)（`ansys_924ed165917464311432bcde`）；[Package overview](../ANSYS_Document/ModelCenter/v261/api_reference/modelcenter-remote-execution-java-api-2026-r1/overview-summary.md)（`ansys_5c1cfe7ce2c4b657b35ef455`）；[`AnalysisServerClient` reference](../ANSYS_Document/ModelCenter/v261/api_reference/modelcenter-remote-execution-java-api-2026-r1/com/phoenix_int/aserver/client/v2/AnalysisServerClient.md)（`ansys_1eed263d18bd9fe4f25de351`）；[API introduction](../ANSYS_Document/ModelCenter/v261/api_reference/dcd54bb2d8fd-index.md)（`ansys_1535e2d29a25109aaa1644c0`）。來源頁面及 class reference 均標示 2026 R1／更新日期 2026-06-22。未安裝 MCRE、編譯 Java 程式或連線／執行 analysis。

這些文件族是不同 SDK／API 的導覽入口；使用時要先確認目標是桌面自動化、腳本包裝、元件外掛、演算法擴充或遠端執行，再選對應版本文件。

## PyAnsys ModelCenter Workflow SDK：建立、執行與儲存 workflow

ModelCenter 文件集合另包含 PyAnsys ModelCenter Workflow SDK。此文件在本機 SDK metadata 為 `ansys-modelcenter-workflow 0.1.4`，官方文件使用 `version/stable` 路徑；產品 release 欄位為 unknown，因此本節只標 SDK metadata，不推定與 ModelCenter APIs 2026 R1 的版本對應或互通性。它與前述 ModelCenter COM／Java、Remote Execution、ScriptWrapper 及 plug-in 文件是不同 API 文件族。

官方 User guide 的最小示例使用 `ansys.modelcenter.workflow.grpc_modelcenter`：以 `Engine()` context manager 建立 engine；呼叫 `new_workflow(path)` 建立 workflow；用 `create_component(server_path, name, parent)` 將 component 加入 workflow；以 `workflow.run(validation_names=[...])` 執行指定驗證名稱；最後 `save_workflow()` 儲存。文件範例的 component server path 是 `common:\Functions\Quadratic`，名稱 `NewQuadratic`、父層 `Model`，驗證路徑 `Model.NewQuadratic.y`，輸出路徑為示例 `d:\\example.pxcz`。這些字串是文件示例值，需依本機 component library、workflow 結構與作業路徑調整。

```python
import ansys.modelcenter.workflow.grpc_modelcenter as grpcmc

with grpcmc.Engine() as mc:
    with mc.new_workflow(r"d:\example.pxcz") as workflow:
        workflow.create_component(
            server_path=r"common:\Functions\Quadratic",
            name="NewQuadratic",
            parent="Model",
        )
        workflow.run(validation_names=["Model.NewQuadratic.y"])
        workflow.save_workflow()
```

`with` 區塊示例了文件所用 engine 與 workflow 的生命週期管理形式；User guide 沒有在該頁解釋 context manager 的錯誤／回復語義，也沒有定義 component 查找失敗或 run 驗證失敗時的處理方式，本文不補作推論。後續例子請查同一文件的 `/examples`；未在此將 v0.1.4 文件中的 API 擴展到其他 SDK 或 ModelCenter 桌面 API。

來源：[PyAnsys ModelCenter Workflow User guide（SDK metadata 0.1.4；官方路徑 version/stable）](../ANSYS_Document/ModelCenter/sdk/ansys-modelcenter-workflow/0.1.4/guide/de457707bbb4-index.md)（`ansys_2f0e8346fc96c37238ac6e80`；[來源網址](https://modelcenter.docs.pyansys.com/version/stable/user_guide/index.html)）；[SDK 文件入口](../ANSYS_Document/ModelCenter/sdk/ansys-modelcenter-workflow/0.1.4/guide/da02f1f15e50-stable.md)（`ansys_a41ac58f21f995fad0feb1bb`）。此處依本機 sidecar 整理，未連線 ModelCenter、執行範例或儲存 workflow。

### PyAnsys Workflow SDK 0.1.4 HTML 表格補件

catalog 記錄 138 份 PyAnsys Workflow SDK 0.1.4 HTML 與非空 Markdown sidecar；文件路徑使用 `version/stable`，catalog release 未指定。轉換側文字涵蓋原頁內容，但表格列結構未在一般 sidecar 中保留。已另產生 [174 張 HTML 表格 Markdown 補件](../maintenance/knowledge_dictionary_passes/2026-11-02/modelcenter_html_table_recovery_20261103.csv)，共 444 列、888 儲存格；逐列保留原 HTML 的儲存格順序及 `th` 標記，原始 HTML 與 sidecar 保持不變。補件標明來源網址、原始檔案連結及 SHA-256。

逐檔補件範例：[gRPC error interpretation](ANSYS_Document/modelcenter_api_reference_html_table_recovery_20261103/modelcenter/modelcenter_table_ansys_035663c191be169a807c9944.md)、[variable value conversion](ANSYS_Document/modelcenter_api_reference_html_table_recovery_20261103/modelcenter/modelcenter_table_ansys_bf01af2b954da321d153b826.md)、[ReferenceArrayDatapin](ANSYS_Document/modelcenter_api_reference_html_table_recovery_20261103/modelcenter/modelcenter_table_ansys_924046da6ba858d3335c2c05.md)。本機補件放在既有 `ANSYS_Document/` 忽略目錄，供本機搜尋使用。機械核對 119 份 HTML 中 174 表的 888 個儲存格 token 與列順序皆對應；連結目標未複製到 Markdown，表格的 heading／資料語義、可見版面與連結用途尚未逐表人工驗收。此補件不是完整 API 語義審閱，不能由中繼資料判定 0.1.4 與其他 ModelCenter API 家族的相容性。

來源：[SDK 0.1.4 API reference index](../ANSYS_Document/ModelCenter/sdk/ansys-modelcenter-workflow/0.1.4/api_reference/f685d08953d2-index.md)（來源 ID `ansys_b9b06fbbf753dbd8e85865ec`；共享來源清冊待補列）。逐 HTML 轉換檢查：[ModelCenter HTML 盤點](../maintenance/knowledge_dictionary_passes/2026-11-02/modelcenter_html_conversion_review_20261103.csv)。

### PyAnsys Workflow SDK ReferenceArrayDatapin

本機 SDK metadata 為 0.1.4；對應的 `ReferenceArrayDatapin` API reference 使用 `version/stable` 網址，故 0.1.4 是本機取得版本，不代表 stable 網頁當前版本。文件說明 client 不應直接建立 `ReferenceArrayDatapin`；從 `Engine` 取得有效 `Workflow` 後再取得此 datapin。

- `__getitem__` 接受整數 index 或 `slice`，分別回傳元素或一段 `Sequence`。
- `__len__` 回傳 reference array 長度。
- `set_length(new_size)` 改變陣列長度；縮短會丟棄尾端元素，擴長會加入空元素。呼叫前應確認截短不會移除仍需的 reference。
- `get_reference_properties()` 回傳 property 名稱到 reference property 的 mapping。

以上簽章與行為來自該 0.1.4 API reference sidecar；未執行程式或驗證 backend 行為。[本機 API reference](../ANSYS_Document/ModelCenter/sdk/ansys-modelcenter-workflow/0.1.4/api_reference/321d433dd20a-ReferenceArrayDatapin.md)（文件 source ID `ansys_924046da6ba858d3335c2c05`；該 ID 尚未在共享 sources.csv 登錄）。

## ScriptWrapper

v261（2026 R1）ScriptWrapper 文件描述腳本可取得名為 `wrapper` 的全域物件，並以專用物件代表不同型別的變數。文件列出 VBScript Object API、Java Object API 與 Python Object Library；使用 Java scripting language 或 Jython 時，文件指出可使用 ModelCenter Remote Execution Java API。這些是不同語言的物件 API，型別使用方式仍需依各自介面頁面確認。

### nD array 輸入與輸出

來源以 `PHXDoubleArray` 等依元素型別命名的特殊類別表示 nD arrays；預設陣列可自動調整維度與長度。對輸入陣列，呼叫端可改變維度或長度，因此 ScriptWrapper 應檢查維度與長度後再存取；輸出陣列則可用 `setDimensions()` 調整大小。此為 API 文件的容器行為描述，不表示 ModelCenter 會替腳本驗證工程上的陣列語意或單位。

### File Parsing API 與檔案副作用

File Parsing API 重用 FileWrapper 的檔案解析能力，且 API 為純 Java；要在 ScriptWrapper 使用它，文件要求選用 BeanShell Java implementation。這個語言限制僅適用 File Parsing API，不是所有 ScriptWrapper 語言的限制。`ParseableFile` 是處理檔案的介面（不是 file variable），`InputFile`／`OutputFile` 是其子介面；`setFileToGenerateOrParse()` 指定輸入或輸出檔，`setTemplateFile()` 指定 template。若未指定 template，文件說明會預設使用被解析或產生的檔案；`readTemplate()` 可讀取 template 並填入預設值，但文件指出這不是必要步驟。

**檔案副作用：**`backup()` 會在原路徑產生 `.bac` 備份；若同名 `.bac` 已存在，API 文件說明會先刪除舊檔，再移動檔案建立備份。`delete()` 會刪除磁碟上的檔案。執行前應確認目的路徑與既有檔案可被覆寫／刪除，並依腳本工作流程負責釋放 `close()` 資源。`setTempEmbedded()` 的 API 文件註明只適用 ModelCenter，在 ModelCenter Remote Execution 中沒有作用。

來源：[ScriptWrapper API introduction，v261／2026 R1](../ANSYS_Document/ModelCenter/v261/api_reference/06ff76277a62-index.md)（[來源清冊](sources.csv#ansys_b7ad923ced6257d3cadd153d)）；[`ParseableFile` Java API](../ANSYS_Document/ModelCenter/v261/api_reference/modelcenter-scriptwrapper-api-2026-r1/java_scriptwrapper_api/api/ParseableFile.md)（[來源清冊](sources.csv#ansys_0ba0c86ac66c736ef7908265)；頁面更新日期 2026-06-22）。未執行 ModelCenter、ScriptWrapper 或檔案解析程式。

## Component Plug-in 與 PACZ

Component Plug-in SDK v261 Getting Started 以建立第一個 PACZ component plug-in 為目標，涵蓋 .NET 開發環境、NuGet 套件來源與測試。文件提到的 TestUI 是 SDK 附帶的測試工具，來源明確聲明它不是 production tool。Visual Studio wizard 指引另外註明 Visual Studio 2022 尚未支援該 wizard；不要將 SDK 支援 Visual Studio 2019／2022 與 wizard 相容性混為一談。

### ModelCenter v261 PACZ runner 初始化與單次評估

官方 Getting Started 將 PACZ plug-in 分成 runner 與 builder UI：runner 實作 `IHarnessRunner`、負責執行計算，明確要求 runner 本身不放 UI；builder UI 則負責使用者設定介面。`ConstructAsync(IHarnessRunnerHost)` 是 runner 的第一個呼叫點，文件範例保存 host，再以 `VariableBasedBuilderModel.FromPaczAsync(host.ExtractedPacz)` 載入 PACZ 設定。指南指出，若 PACZ 尚未初始化，`FilePathAbsolute` 可能為 `null`；資源密集的應用程式也可考慮延後到首次執行才載入。

每次評估呼叫 `RunAsync(inputs, outputs, cancellation)`：`inputs` 是 `IReadOnlyDictionary<string, VariableState>`，其中值帶有 validity 狀態；指南建議用 `SafeValue` 讀取有效輸入，無效時會拋出例外。計算結果要以新的 `VariableState` 寫入 `VariableValueScope outputs`，範例用兩個 `RealValue` 輸入相乘並設定輸出 `y`。簽章包含 `CancellationToken`，但 Getting Started 範例沒有示範如何處理取消；threading 與取消行為須另查專門指南，不從此範例推定。[Component Plug-in SDK Getting Started](https://developer.synopsys.com/docs/component-plug-in-sdk-2026-r1/started.md) · [本機 Markdown](../ANSYS_Document/ModelCenter/v261/guide/1042ab6e2be4-started.md) · `ansys_29f4b2da769a3e44643311b1`（Release 2026 R1／v261；頁面更新日期 2026-06-19）。未編譯、部署或執行 PACZ plug-in。

### PACZ 變數階層、命名與值的生命週期

Component Plug-in FAQ 說明，以句點分隔的巢狀變數名稱（例如 `a1.a2.x1`）會在 component tree 自動形成 ModelCenter assembly；runner 以相同完整名稱讀取輸入。變數名稱依 FAQ 所述採近似 Java identifier 規則：首字元為字母或底線，後續使用英數字或底線；不支援 `$`，句點只用作階層分隔，空格、標點及其他特殊字元不允許。使用前應按目標 SDK 文件與實際變數型別核對名稱及階層。

FAQ 將 `DefaultValue` 與執行時 `Value` 區分：Builder context 可設定預設值，但不可讀取執行值；Runner context 才可讀取 `Value`。文件說明 host process（例如 ModelCenter）負責把 Builder 設定的預設值複製成變數執行值。FAQ 另示範透過 `VariableType.BooleanArray` 及 `BooleanArrayValue` 建立陣列變數，並以 `FileValue` 宣告檔案輸出、執行時從輸出路徑讀取檔案內容。這些是 SDK 範例，不代表檔案路徑、覆寫政策或陣列長度會自動符合使用者工作流程。

來源：[Component Plug-in SDK FAQ（v261／2026 R1）](../ANSYS_Document/ModelCenter/v261/guide/1c90b49fddc6-faq.md)（`ansys_1ba19d81f99d8ed2be9e360e`；更新日期 2026-06-19）。

### PACZ runner 與 Builder UI 執行緒

Threading 指南指出，SDK 將 Runner 與 Builder UI 各自序列化到唯一專用執行緒，兩者不是同一執行緒；Runner 呼叫會排隊逐一處理。UI 元件只能從 UI 執行緒存取；Builder UI 要呼叫 Runner 方法時，使用 `IHarnessBuilderUIHost.CallRunnerAsync<T>()`，Runner 不應建立、修改或顯示 UI。SDK 提供 `async`／`await` 支援，文件描述 await continuation 會回到對應的 synchronization context。

文件也提醒，明確切到 thread pool 後不可直接碰 Runner／UI 狀態；共享的可變狀態須自行同步。長時間初始化的外部工具可考慮延遲至首次 `RunAsync()` 載入並在 Runner 欄位快取，必要時實作 `IDisposable` 清理。這些保證和建議限定於該 PACZ SDK 指南，不能外推到 COM、Remote Execution 或其他 SDK；外部工具本身的執行緒安全仍需各自確認。

來源：[Component Plug-in SDK Threading（v261／2026 R1）](../ANSYS_Document/ModelCenter/v261/guide/9010b182d09c-threading.md)（`ansys_f0d26927777facd3a940a2c8`；更新日期 2026-06-19）。未執行並行、UI thread affinity 或外部工具整合測試。

## Custom optimization algorithm 生命週期

Custom Optimization Algorithm SDK v261 官方 lifecycle 頁將 `IAlgorithm` 呼叫順序列為：建立演算法並呼叫 `SetHost(IAlgorithmHost)`；設定 `Options`、`SetObjectives(...)`、`SetConstraints(...)` 與 `SetDesignVariables(...)`；讀取 options 以反映演算法修改並在有修改時傳送 warning status message；若指定 checkpoint 才呼叫 `RestoreCheckPoint(...)`；呼叫 `Run`；取得 `ResultsReport`／`DetailsReport`；最後 `Dispose`。

報告讀取不只在 `Run` 結束後進行：兩個 report properties 都可能在執行期間被呼叫，故都必須 thread-safe；`DetailsReport` 預期在執行期間更新，供使用者監看進度，而 `ResultsReport` 可更新但不要求持續更新。來源沒有指定 thread-safety 的實作方式，也沒有給演算法必須回報的欄位或頻率，這些不在此推定。[v261 lifecycle 原文](../ANSYS_Document/ModelCenter/v261/guide/5eda53e65253-create_algo_index.md)（`ansys_dff7d7c47aad0995f319ebb8`；頁面更新日期 2026-06-19）。

此流程說明 SDK 物件生命週期，不定義任一最佳化問題的物理模型、收斂準則或演算法效能；這些需依工程問題與實際演算法驗證。

## 來源

- [ModelCenter 開發者入口](../ANSYS_Document/ModelCenter/unknown/guide/981eb0415fbb-modelcenter.md)（`ansys_d6082aa4284299871475e632`）
- [v261 Component Plug-in SDK Getting Started](../ANSYS_Document/ModelCenter/v261/guide/1042ab6e2be4-started.md)（`ansys_29f4b2da769a3e44643311b1`）
- [v261 Custom Optimization Algorithm lifecycle](../ANSYS_Document/ModelCenter/v261/guide/5eda53e65253-create_algo_index.md)（`ansys_dff7d7c47aad0995f319ebb8`）
- [v261 COM API](../ANSYS_Document/ModelCenter/v261/api_reference/bc5477e4834a-index.md)（`ansys_e5d064d3aa0c74340efef493`）與 [Java API](../ANSYS_Document/ModelCenter/v261/api_reference/3422bd6007b1-index.md)（`ansys_1ac461d0254dd4bc2e03af5b`）
- [v261 Remote Execution Java API Introduction](../ANSYS_Document/ModelCenter/v261/api_reference/dcd54bb2d8fd-index.md)（`ansys_1535e2d29a25109aaa1644c0`）
- [v261 ScriptWrapper API Introduction](../ANSYS_Document/ModelCenter/v261/api_reference/06ff76277a62-index.md)（`ansys_b7ad923ced6257d3cadd153d`）

## 待補與限制

- 本頁為 developer API 導覽；未整理 ModelCenter GUI 使用者手冊、安裝管理、所有 API 類別與各版本變更。
- 本機主要版本依來源標示為 v261；ModelCenter API、Remote Execution、ScriptWrapper 與外掛 SDK 需各自核對版本，不能假定不同 SDK 的型別或部署方式互通。
- 本輪未安裝 ModelCenter、編譯外掛、執行 remote workflow 或最佳化演算法；PACZ runner、Custom Optimization Algorithm lifecycle 與 ScriptWrapper／File Parsing API 為有界 complete 範圍，其餘主題仍為 `draft`。


## 2026-11-04：Wave 4 本機來源盤點與限制說明

本批完成 modelcenter 模組既有本機 catalog 文件（共 1691 筆）與 sources 清冊（共 151 筆）之完整雜湊、正文路徑與標籤結構核對。本機未快取或具備企業授權/登入限制之線上主題誠實標記為缺口（保持現有非 complete 狀態），未擅自虛構未核實之線上 API 簽名或執行求解運算。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/modelcenter_module_conversion_report_20261104.md)。
