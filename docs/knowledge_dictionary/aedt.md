# Ansys Electronics Desktop（AEDT）與 PyAEDT 主題字典

本頁聚焦 PyAEDT 以 Python 控制 AEDT 的入門、Desktop session 與命令列入口。來源來自 `ansys-aedt-core 1.9.0` 文件；文件清冊的 AEDT release 為 `unknown`。`stable` 文件中的產品版本範例只作範例，不據此推定安裝版本。

## PyAEDT 與 AEDT 的版本邊界

PyAEDT 是操作 AEDT 的 Python API。文件路徑標示 SDK `ansys-aedt-core 1.9.0`，但產品 release 未由本機來源清冊證實。入門教學中的 `version="2026.1"` 是啟動範例參數，不表示 PyAEDT 1.9.0 只能搭配該 AEDT 版本；實際版本相容性需按安裝與相應版本文件核對。

`Desktop.version` 是所選 AEDT 版本，不是 PyAEDT 套件版號。官方 API 頁列出 `261`、`26.1`、`2026.1` 和 `"2026.1"` 等輸入示例；預設 `None` 使用 active setup 或最新安裝版本。入門範例註解寫「AEDT 2025 R1」，程式卻傳入 `version="2026.1"`；API 另以 `Desktop(261)` 示範 AEDT 2025 R1。保留這些來源標示，不替範例差異做版本換算或建立相容矩陣。來源頁均使用 `version/stable`，release 欄維持 unknown。

來源：[PyAEDT Basic tutorial](../ANSYS_Document/AEDT/sdk/ansys-aedt-core/1.9.0/guide/74bb6d3e7a2d-intro.html)（[來源清冊](sources.csv#ansys_2b813d04b54d9596c7027fe6)）；[`Desktop` API](https://aedt.docs.pyansys.com/version/stable/API/_autosummary/ansys.aedt.core.desktop.Desktop.html)（[本機 HTML](../ANSYS_Document/AEDT/sdk/ansys-aedt-core/1.9.0/api_reference/2a563df2ce9d-ansys.aedt.core.desktop.Desktop.html)；[來源清冊](sources.csv#ansys_dc58a4be8ae15239b6c36817)）。

PyAEDT 以應用類別表示不同設計類型，例如 `Circuit` 和 `Hfss`；AEDT session 由 `Desktop` 管理。不同 solver 的建模、setup 和結果 API 各有專屬類別，不能只依共通的 Desktop 啟動範例推定全部設計流程相同。

## Desktop session 生命週期

PyAEDT `Desktop` 可以啟動新的 AEDT session，也可以連到已存在的 session。離開 context manager 或 Python interpreter 時是否關閉 session，受 `close_on_exit` 控制：

| 使用方式 | 文件所述預設行為 |
| --- | --- |
| 在 `with Desktop(...)` 中使用，未指定 `close_on_exit` | 視為 `True`，離開區塊時關閉。 |
| 不使用 context manager，且 PyAEDT 啟動新 session | `close_on_exit` 視為 `True`。 |
| 不使用 context manager，且 PyAEDT 連到既有 session | `close_on_exit` 視為 `False`。 |
| 明確指定 `close_on_exit=True` 或 `False` | 依明確設定執行。 |

自動化腳本應明確決定是否新建 AEDT、是否使用 non-graphical 模式，以及是否由腳本負責關閉 session，避免誤關閉使用者既有的 Desktop。官方入門範例在 `with Desktop(...)` 中建立 `Circuit`；另一範例使用 `save_project()` 並在結束前釋放 Desktop。

**新建與附加 session 的選擇順序**

Desktop sessions guide 另說明啟動時如何決定連線對象。若 `port=0`，先配置實際 port；若要求 `new_desktop=True`，PyAEDT 優先啟動新 AEDT instance，遇到該 port 已被占用時會另找可用 port。若設定 remote RPyC session，則改用遠端 session、將 `new_desktop` 設為 `False`，並停止後續本機 port 檢查。

沒有上述條件時，PyAEDT 會依序檢查：同一 AEDT version 且 port 相同的 active session 會被重用；若 version 相同、port 相同但 graphical／non-graphical 模式相反，會切換 `non_graphical` 旗標並重用該 session；若 port 被不同 AEDT version 使用，會為新 instance 選另一個可用 port；沒有可重用 session 時則用要求的 port 啟動新 instance。這些條件是該 guide 對 PyAEDT SDK 1.9.0 的選擇順序摘要；部署時仍應記錄 version、port、display mode 及 remote RPC 設定，以解釋實際連到的 AEDT。

直接建立 `Desktop(...)` 時，可明確呼叫 `release_desktop(close_projects=False, close_desktop=False)` 管理釋放行為；此例不關閉專案或 Desktop。自動化應把「連上既有 session」與「允許關閉該 session」分別決定，不要只根據 `with` 語法判定應用程序所有權。

## 命令列介面與常用工作

PyAEDT CLI 可從終端管理 AEDT session、專案、腳本與匯出工作。執行 `pyaedt --help` 可查目前安裝版本可用命令；CLI 文件列出的主要命令如下：

| 命令 | 文件列出的用途 |
| --- | --- |
| `version`、`aedt-versions` | 查 PyAEDT 版本與本機已安裝 AEDT 版本。 |
| `session` | 啟動、列出、停止或連接 AEDT session。 |
| `project` | 列出、開啟、建立、儲存或關閉專案。 |
| `script` | 在 AEDT 中執行 Python 腳本。 |
| `export` | 匯出截圖或設計組態資料。 |
| `panels`、`doc` | 安裝 PyAEDT panels、開啟文件。 |
| `test-config` | 建立、檢查或更新本機測試設定。 |

CLI 指令可加 `--json` 取得 JSON 格式輸出。這些是 PyAEDT 1.9.0 文件列出的 CLI 功能；實際選項以安裝版本執行 `pyaedt --help` 的結果為準。

### PyAEDT CLI：session、project、script 與 export 工作流程（SDK 1.9.0）

官方 CLI 指南列出的入口包含 `version`、`aedt-versions`、`session`、`project`、`script`、`export`、`panels`、`doc` 及 `test-config`。所有命令可加 `--json` 輸出 JSON；`pyaedt --help` 與各子命令的 `--help` 是查詢目前安裝版選項的入口。

| 任務 | 指南示例 | 條件與結果 |
|---|---|---|
| 啟動 session | `pyaedt session start --non-graphical --port 50051` | 預設使用本機最新穩定版 AEDT 與 port `50051`；可用 `--port 0` 讓 AEDT 指派可用 port。 |
| 查看／附加 session | `pyaedt session list`；`pyaedt session attach --port 50051` | list 顯示 PID、AEDT 版本與 port；attach 未給 port 時會列出互動式 session 選單，若安裝 IPython 則使用它作互動 console。 |
| 操作 project/design | `pyaedt project create --port 50051 --project DemoProject --design Filter1 --type Hfss` | `project` 群組在已運行的 AEDT gRPC session 上操作，命令必須提供 `--port`；設計型別依官方列出的應用類別選擇。 |
| 執行 Python | `pyaedt run my_script.py --port 50051` | 腳本可使用 CLI 附加的 `desktop` 物件；加 `--ironpython` 時只支援 AEDT 原生 API。 |
| 匯出 | `pyaedt export screenshot --port 50051 --project DemoProject --design Filter1`；`pyaedt export config --port 50051 --output config.json` | export 需連到 session；config 未指定 `--output` 時將 JSON 印到終端。 |

文件也示範啟動、列出 session、列出 project、再以指定 port 停止該 session。需特別注意 `pyaedt session stop --all` 會停止所有 session；`pyaedt panels add --reset` 會先移除既有 `Toolkits` 目錄；`pyaedt test-config` 會啟動互動式設定流程。只有在確認影響範圍後才使用這些選項。

來源頁位於 `ansys-aedt-core 1.9.0` 本機文件路徑，但官方 URL 使用 `version/stable`，AEDT 產品 release 仍是 `unknown`。頁面中的 `pyaedt version` 範例輸出 `1.0.dev0` 是文件示例，不能用來推定本機套件版本；安裝環境應以 `pyaedt version`、`pyaedt aedt-versions` 及命令 `--help` 的實際輸出確認。未在本機啟動 AEDT 或執行 CLI；本子題整理的是文件所述命令行介面，不代表求解或 solver API 驗證。

來源：[PyAEDT command line interface，官方頁面](https://aedt.docs.pyansys.com/version/stable/Getting_started/cli.html) · [本機 Markdown](../ANSYS_Document/AEDT/sdk/ansys-aedt-core/1.9.0/guide/8ef297946829-cli.md)（`ansys_43b46378037bb391538151b2`）。

### PyAEDT project／design 建立與儲存（SDK metadata 1.9.0）

官方 Basic tutorial 展示兩種 Python 入口。第一種用 `Desktop(version="2026.1", non_graphical=True, new_desktop=True, close_on_exit=True)` 啟動新 AEDT session，並在 context 內建立 `Circuit()`；離開 context 時關閉 session。來源程式註解卻寫「Launch AEDT 2025 R1」，與實際傳入的 `version="2026.1"` 不一致，應以程式參數與目標安裝版本另行核對，不能把註解當作相容性結論。

第二種建立 `Circuit(non_graphical=False)`，呼叫 `save_project(my_path)` 儲存，最後以 `release_desktop(close_projects=True, close_desktop=True)` 關閉專案及 Desktop。這是 tutorial 的 GUI 範例流程；`my_path` 的實際值由使用者提供，來源沒有展示路徑處理或覆寫保護。

CLI 的 project 群組操作**已啟動的 AEDT gRPC session**，各 project command 都須提供 `--port`。指南示範先以 `pyaedt session start` 啟動 session，再用 `pyaedt project create --port 50051 --project DemoProject --design Filter1 --type Hfss` 建立專案與設計；支援的 design type 以該頁列出的 `Hfss`、`Maxwell2d`、`Maxwell3d`、`Q3d`、`Q2d`、`Icepak`、`Circuit`、`TwinBuilder`、`Mechanical`、`Emit`、`Rmxprt`、`Hfss3dLayout`、`MaxwellCircuit` 為限。`project save` 可儲存 active project，也可用 `--path` 指定另存路徑；`project close` 可關閉目前專案或以 `--project` 指定名稱。CLI 範例 port `50051` 與 project 名稱只是示例值。

PyAEDT Basic tutorial 與 CLI 均位於 `ansys-aedt-core 1.9.0` 文件集合，官方網址使用 `version/stable`；AEDT 產品 release 仍為 unknown。SDK 文件版本、範例參數與安裝中的 AEDT 版本分開核對。本節僅整理建立／保存流程與 CLI session 前置條件，未建立 AEDT 專案、執行 CLI 或驗證求解。

來源：[Basic tutorial](../ANSYS_Document/AEDT/sdk/ansys-aedt-core/1.9.0/guide/74bb6d3e7a2d-intro.md)（[來源清冊](sources.csv#ansys_2b813d04b54d9596c7027fe6)）；[Command line interface](../ANSYS_Document/AEDT/sdk/ansys-aedt-core/1.9.0/guide/8ef297946829-cli.md)（[來源清冊](sources.csv#ansys_43b46378037bb391538151b2)）。

## API 導覽與待補範圍

本機 `ansys-aedt-core 1.9.0` API 索引包含 `Desktop` session 管理、HFSS 設計類別與 modeler 等 API。遇到 HFSS 3D Layout、Maxwell、Circuit、Icepak 等不同 AEDT 設計時，需切換到相應應用類別與 API 文件；本頁不以某個 solver 的類別預設取代其他 solver 的工作流。

| 類別 | 官方 API 頁明列的責任 | 預設／限制 |
|---|---|---|
| `Desktop` | 提供 AEDT interface；管理 session、project 及 design 等桌面層操作。 | `version=None` 使用 active setup 或最新安裝版本；session 的關閉行為依 `close_on_exit` 與啟動／附加情況判定，詳見前節。 |
| `Hfss` | 提供 HFSS application interface，可連接既有設計或建立新設計；參數包含 `project`、`design`、`solution_type`、`setup`。 | `project`／`design` 未指定時先嘗試 active project/design；若不存在則建立空 project/design。solution type 頁列 `Terminal`、`Modal`、`SBR+`、`Transient`、`Eigenmode`。 |

此表只用 `Desktop` 與 `Hfss` 示範 AEDT session 層和 solver-specific app 層；API 頁的其餘 solver 類別仍需逐一查相應文件，不從 HFSS 的參數或操作推定 Maxwell、Circuit、Icepak 等完整工作流。來源：[Desktop API](https://aedt.docs.pyansys.com/version/stable/API/_autosummary/ansys.aedt.core.desktop.Desktop.html)（[來源清冊](sources.csv#ansys_dc58a4be8ae15239b6c36817)）；[`Hfss` API](https://aedt.docs.pyansys.com/version/stable/API/_autosummary/ansys.aedt.core.hfss.Hfss.html)（[來源清冊](sources.csv#ansys_9e13d39551c6a85779de8956)）。本機 sidecar 路徑標示 SDK 1.9.0；AEDT product release unknown。

### HFSS 物件間的 Lumped RLC boundary（PyAEDT SDK 1.9.0）

`Hfss.create_lumped_rlc_between_objects(assignment, reference, ...)` 以兩個物件的最近邊緣建立 lumped RLC，`assignment` 是 integration line 起點物件（字串或字串清單），`reference` 是終點物件，可用物件名稱、ID 或 `Object3d`。`start_direction` 控制 boundary 方向，預設為 `XNeg`；正式模型應按幾何與座標方向核對，不要照搬範例的方向值。

| 參數 | 文件預設／單位 | 用途 |
|---|---|---|
| `rlc_type` | `Parallel`；可選 `Parallel`／`Serial` | RLC 拓樸型態。 |
| `resistance` | `None`；Ω | 設為 `None` 時停用該元件參數。 |
| `inductance` | `None`；H | 設為 `None` 時停用該元件參數。 |
| `capacitance` | `None`；F | 設為 `None` 時停用該元件參數。 |
| `is_boundary_on_plane` | `True` | 是否在垂直於指定 axis direction 的平面建立 boundary。 |
| `name` | `None` | 未提供時自動命名。 |

成功時回傳 `BoundaryObject`，失敗時回傳 `False`；後續腳本應檢查回傳值再使用 boundary。官方示例以兩個 copper box 建立 `Lumped RLC`，示例的 50 Ω、1e-9 H、1e-6 F 是測試程式數值，不是設計建議。這個摘要限 HFSS API 該方法，不涵蓋其他 solver 的 lumped boundary 或求解設定。

來源：[HFSS `create_lumped_rlc_between_objects` API](../ANSYS_Document/AEDT/sdk/ansys-aedt-core/1.9.0/api_reference/fe31cc6462e8-ansys.aedt.core.hfss.Hfss.create_lumped_rlc_between_objects.md) · [官方 HTML](https://aedt.docs.pyansys.com/version/stable/API/_autosummary/ansys.aedt.core.hfss.Hfss.create_lumped_rlc_between_objects.html) · `sources.csv#ansys_08c4c71aeff32ca5f7653a23`。本機文件路徑標示 SDK 1.9.0，AEDT 產品 release 仍 unknown；未建立 HFSS geometry 或執行求解。

## 來源

- [PyAEDT Basic tutorial](../ANSYS_Document/AEDT/sdk/ansys-aedt-core/1.9.0/guide/74bb6d3e7a2d-intro.md)（`ansys_2b813d04b54d9596c7027fe6`）
- [PyAEDT Desktop sessions](../ANSYS_Document/AEDT/sdk/ansys-aedt-core/1.9.0/guide/72135c76efad-desktop_sessions.md)（`ansys_8418f1dee07e7c32701b3e5c`）與 [`Desktop` API](../ANSYS_Document/AEDT/sdk/ansys-aedt-core/1.9.0/api_reference/2a563df2ce9d-ansys.aedt.core.desktop.Desktop.md)（`ansys_dc58a4be8ae15239b6c36817`）
- [PyAEDT command line interface](../ANSYS_Document/AEDT/sdk/ansys-aedt-core/1.9.0/guide/8ef297946829-cli.md)（`ansys_43b46378037bb391538151b2`）
- [`Hfss` API](../ANSYS_Document/AEDT/sdk/ansys-aedt-core/1.9.0/api_reference/72213083180a-ansys.aedt.core.hfss.Hfss.md)（`ansys_9e13d39551c6a85779de8956`）

## 注意事項

- PyAEDT SDK 版號、AEDT 產品版號與文件中的範例版號是不同欄位，未確認時各自保留，不互相推定。
- 關閉既有 AEDT session 可能影響其他工作；按 `Desktop` session 文件明確設定 `close_on_exit`。
- 本頁未執行 AEDT、PyAEDT 腳本或電磁求解。幾何、邊界、網格、收斂與物理結果須依實際 solver 和分析類型另行驗證。
- `Desktop session 生命週期`、`PyAEDT CLI`、project/design 建立／儲存、Desktop／Hfss API 層級與 HFSS RLC boundary 均為依指定來源整理的有界主題。其他 API methods 與 solver-specific workflows 未逐一整理；本字典未涵蓋 1,600 餘筆 API 項目或所有 PyAEDT extension。

## AEDT 來源與轉換盤點（2026-11-02）

AEDT catalog 共 1,722 筆 HTML 文件；逐筆來源 HTML SHA-256 均符合 catalog，text_path Markdown 存在且非空，HTML 文件本體共 1,722 個。本機 AEDT 文件樹未發現 PDF。這代表來源與轉換文字檔可用，不代表抽取後文字忠實保留表格、程式範例、欄位或語義；本輪不曾逐筆核閱 1,722 篇正文。逐文件記錄（document ID、來源及文字檔路徑、版本、URL、雜湊檢查、字元數、處理狀態及語義覆核狀態）見[AEDT 來源清冊](../maintenance/knowledge_dictionary_passes/2026-11-02/aedt_sources.csv)。每筆 `semantic_review=not_reviewed`。

共享 `sources.csv` 有 7 筆 AEDT 引用列，其中 6 筆用於技術主題，一筆是 PyAEDT 文件入口。完整 catalog 有 1,666 筆 API reference 與 56 筆 guide，含這 7 筆。其餘文件的逐篇語意、表格與程式範例覆核已在 `topics.csv` 列為 `pending_source_review`。HFSS 等應用類別的 PyAEDT SDK 文件保留 AEDT 歸屬，HFSS 產品手冊另有清冊。

本字典的 6 項主題僅限既有來源所支持的 SDK 版本邊界、Desktop sessions、CLI、project/design 入門、Desktop/Hfss API 導覽與 HFSS lumped RLC API；不得視為 AEDT 全產品字典完成。


## 2026-11-04：Wave 8 本機來源盤點與限制說明

本機 catalog 有 1,722 份 PyAEDT SDK HTML 與對應 Markdown，來源及轉換稿雜湊均有稽核紀錄。共享清冊的 7 筆是引用子集。11 月 4 日批次未擷取清冊的 6,037 個網址。圖表、公式、程式範例、離線覆蓋與分享權限仍待核對。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/aedt_module_conversion_report_20261104.md)。
