# PyAnsys Source Intelligence

## 範圍與證據界線

本盤點涵蓋目前 `ansys-unified-mcp` checkout 與其 `.venv`。目前沒有已確認的上游 PyAnsys SDK 原始碼 checkout；同層 `pyansys-common-mcp` 是另一個 MCP 專案，名稱不能證明它是上游 SDK 來源。

套件、圖譜與產品宿主是不同證據層：`pyproject.toml` 表示選用相依需求，`uv.lock` 表示解析版本，distribution metadata 表示本環境已安裝套件，SDK snapshot 表示擷取器記錄的符號。這些資料都不能替代上游 commit 或 ANSYS runtime 行為。

## 目前可回查的來源

| 來源 | 已記錄狀態 | 覆蓋與限制 |
| --- | --- | --- |
| CodeGraph | 2026-10-29 [計畫 checkpoint](../planning/FOLDER_TREE_REORGANIZATION_PLAN.md) 記錄全量重建後同步 8 個變更檔，共 470 files、7,659 nodes、17,318 edges。 | 此處引用既有 checkpoint，本次未重建或查詢狀態；只涵蓋本 repo，沒有上游 SDK checkout。 |
| Graphify 日期圖譜 | 本機 `graphify-out/2026-10-29/graph.json` 有 10,159 nodes、19,303 links；同目錄 `manifest.json` 有 887 個路徑記錄。 | 這是現存 JSON 的資料量，不是成功解析程式檔數。計畫先前記錄 512 個程式檔、10,160 nodes、19,307 edges；兩者差異尚未釐清，不合併為同一測量。 |
| Graphify 舊報告 | 日期目錄中的 `GRAPH_REPORT.md` 頁首仍是 2026-10-26，列出 746 files、8,745 nodes、16,102 edges。 | 報告與日期圖譜內容不同步，不能用舊報告說明目前圖譜。查詢必須明確指定 `graph.json` 路徑。 |
| Serena | 前次工作階段曾讀取 active checkout 的目前符號。 | 工具可用性以當次工具清單與回應為準；設定或舊連線記錄不能證明目前可用，單次符號查詢也不能證明整庫完整度。 |
| codebase-memory-mcp | 既有盤點記錄 2026-10-21 索引、9,272 nodes、23,992 edges、watch 關閉；後續 `index_status` 曾回報 `Transport closed`。 | 舊索引早於目錄重構。先前記錄 3 檔部分解析、5 目錄排除；目前暴露的工具是唯讀 profile，沒有重建入口。 |
| SDK 字典 | 本機 `docs/api_inventory/curated/sdk/index.md` 列出 19 份版本化字典。 | 只涵蓋各擷取器的範圍，套件版本不等於產品 release，也不證明宿主相容性。 |
| 套件相依盤點 | `.audit/repo-restructure/pyansys-source-intelligence/current_environment.json` 記錄 49 個 `ansys-*`/`pyaedt` distributions、25 個 manifest SDK 名稱中 15 個已安裝，以及 142 條 ANSYS 套件相依邊。 | 來源觀察時間為 2026-10-28T23:06:04 UTC；只描述專案 `.venv`，不涵蓋 global Python、全機 ANSYS 安裝或上游來源 commit。 |

圖譜與環境產物均留在本機忽略目錄。新增數字時必須記錄工具、輸出路徑、日期及統計口徑；`manifest paths`、已解析 files、nodes、edges/links 各有不同意義。Graphify 計畫 checkpoint 另記錄 27 個格式跳過、2 個 SQL 檔缺少 `tree_sitter_sql`、13 個程式檔未產生符號；這些限制尚未在本次重新確認。

## 已擷取的版本化 SDK

下表依本機 SDK 字典索引整理；原始 snapshot、字典及環境資料尚未完成公開散布審查。

| Source key | Distribution | 擷取版本 |
| --- | --- | --- |
| `cfx` | `ansys-cfx-core` | `0.3.0` |
| `dpf` | `ansys-dpf-core` | `0.16.1` |
| `fluent` | `ansys-fluent-core` | `0.42.1` |
| `geometry_core` | `ansys-geometry-core` | `0.17.1` |
| `mapdl` | `ansys-mapdl-core` | `0.74.1` |
| `mechanical_core` | `ansys-mechanical-core` | `0.13.2` |
| `motorcad` | `ansys-motorcad-core` | `0.8.8` |
| `optislang_core` | `ansys-optislang-core` | `1.6.0` |
| `primemesh` | `ansys-meshing-prime` | `0.10.5` |
| `pyaedt` | `pyaedt` | `1.9.0` |
| `pydyna` | `ansys-dyna-core` | `0.12.1` |
| `pytwin` | `pytwin` | `0.13.0` |
| `reaction_chemkin` | `ansys-chemkin-core` | `0.2.0` |
| `rocky` | `ansys-rocky-core` | `0.6.2` |
| `sherlock_core` | `ansys-sherlock-core` | `2.1.4` |
| `sound` | `ansys-sound-core` | `0.3.0` |
| `speos` | `ansys-speos-core` | `0.9.2` |
| `system_coupling` | `ansys-systemcoupling-core` | `0.13.0` |
| `workbench` | `ansys-workbench-core` | `0.14.0` |

PyTwin 與 PyAEDT 的 manifest 產品映射和產品版次仍未知。其他套件也須依各 snapshot 的 scope 判讀；直接 AST 宣告、動態 API、繼承成員、protocol schema 與產品宿主支援不可混為完整 SDK 表面。

## 本 repo 的重建與查找入口

以下命令以 repo root 為工作目錄，語法來自目前 CLI help；本次只讀 help，沒有執行重建。重建會改寫被忽略的本機圖譜，因此先固定來源 revision，並保留既有產物需要的版本記錄。

| 工具 | 工作方式 | 需保留的界線 |
| --- | --- | --- |
| CodeGraph | 完整重建：`codegraph index .`；增量同步：`codegraph sync .`；定位與讀來源：`codegraph explore "<symbol or question>"`。 | `.codegraph/` 只代表這個 checkout。搬移後應同步來源路徑；查得符號仍須以目前檔案判讀，不以索引計數證明行為。 |
| Graphify | 程式擷取更新：`graphify update . --no-cluster`；讀日期快照：`graphify query "<question>" --graph graphify-out/2026-10-29/graph.json`。 | `update` 的預設輸出與日期快照分開管理。`cluster-only` 只重分群，不能替代來源重擷取；圖譜中的推論邊須保留其 confidence。不要以 `--force` 掩蓋未解的節點減少。 |
| Serena | 工具存在時先讀 `initial_instructions`，確認 active project，再依序使用 `get_symbols_overview`、`find_symbol` 與 `find_referencing_symbols` 定位介面及使用端。 | 這是當次來源導覽，不是可攜的上游套件圖譜；工具不存在或連線失敗時，記錄限制並改用目前檔案。 |
| codebase-memory-mcp | 連線可用時先讀 `index_status`，再對引用路徑用 `check_index_coverage`，以 `search_graph`、`get_code_snippet`、`trace_path` 追蹤符號。 | 目前唯讀 profile 無法完成索引重建；須由服務管理者或可用的更新入口刷新，之後才可引用新 generation。`Transport closed` 時不得沿用舊圖宣稱新鮮。 |

CodeGraph 與 Graphify 的建置命令只產生來源結構資料；它們不啟動 ANSYS，也不能替代軟體、宿主或物理驗收。各圖譜與 SDK 相依 inventory 的範圍應分別記錄。

## 上游 checkout 與跨 repo 圖譜缺口

Stage 3 仍需取得已授權的上游 PyAnsys checkout。每個來源至少記錄 repository URL、本機 checkout 路徑、完整 commit SHA、dirty 狀態、distribution/版本對應、使用與分享範圍，以及圖譜工具版本、輸出路徑和解析跳過項目；目前 `.venv` metadata 無法補出這些欄位。

先為每個確認來源建立獨立圖譜，再以 package import、公開介面或已查明的呼叫連結對齊跨 repo 關係。Graphify 的 `merge-graphs` 可合併既有圖檔，但合併操作本身不能證明跨 repo 呼叫正確；未對齊的符號保留為缺口。尚未確認的兄弟 MCP 專案不納入上游 SDK 範圍。

接續工作為：確認需要的上游 repositories 與授權、取得 checkout/commit 對應、分庫產生模組及符號圖、處理解析缺口，再安排跨 repo 查找驗收。依目前使用者要求，索引重建與測試/查詢驗收分開記錄；本次文件整理沒有執行這些操作。

Stage 3 維持進行中。現有證據支持本 repo 結構與本機套件相依盤點，尚未支持完整 PyAnsys 上游來源圖譜。
