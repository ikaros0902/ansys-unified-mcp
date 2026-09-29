# ANSYS Unified MCP — 專案核心上下文

> 本檔是維護者與 AI 接手本專案的**入口文件**。新對話請先讀本檔，再視需要讀 `README.md`、`specs/*.md` 與 `ARCHITECTURE.md`。
> 目的：用最短篇幅建立正確的心智模型，讓不熟悉本專案的人也能安全地維護與擴充。

## 1. 這是什麼

`ansys-unified-mcp` 是一個 **MCP（Model Context Protocol）server**，讓 AI 代理透過統一介面驅動多個 ANSYS 產品（Mechanical、Workbench、Fluent、optiSLang、LS-DYNA / LS-PrePost）。

- 對外：以單一 MCP server 暴露約 114 個工具（`@mcp.tool()`），供 AI 代理呼叫。
- 對內：把「連線到 ANSYS」與「在 ANSYS 裡執行動作」拆成分層，並以文件檢索工具讓 AI 查 API。
- 執行環境：Windows；Python 由專案內 `.venv` 提供；透過 stdio 與 MCP client 溝通。

## 2. 核心設計理念：thin generic script runner

**最重要的一個決策**：本專案不去逐一包裝每個 ANSYS 高階 API，而是把核心原語定為「送一段原生 Python 腳本進目標 App 執行，並取回輸出」。

- Mechanical → `controller.run_script(script)`
- optiSLang → `_osl.run_python_script(script)`
- Workbench → `execute_workbench_script(script)`

多數 `@mcp.tool()` 其實是**圍繞這個原語組腳本字串**的便利包裝。這樣做的理由：各版本（25R1 / 25R2 / 26R1…）ANSYS 高階 API 常變動，走原生腳本原語可跨版本通用。

> 維護含意：新增功能時，優先考慮「能不能用既有 script runner 組腳本達成」，而非新增一個綁死某版本高階 API 的工具。

## 3. 四層架構

資料流方向：**AI 呼叫工具 → 工具委派產品控制器 → 控制器存取 session 登錄 → 連線管理器負責找到 ANSYS 實例**。

```
tools/*.py        薄工具層（114 個 @mcp.tool）
                  檢查連線 → 組腳本字串 → 委派；回傳一律走 _json 信封
      │
      ▼
products/         產品控制器（真正的 connect / launch / run_script / disconnect）
drivers/          某些產品的實作放這（如 Fluent 在 drivers/sim_impl.py）
bridges/          Workbench 的檔案 IPC bridge 實作
      │
      ▼
core/sessions.py  SessionRegistry（全域單例，thread-safe，多 session/產品，key=port/pid）
      │
      ▼
connection_manager.py   掃 port / 掃進程，找出正在跑的 ANSYS 實例
core/paths.py           統一解析 ANSYS 各 exe 路徑
config.py               偵測 ANSYS 安裝（registry / 環境變數），找不到走 degraded 非致命
```

檔案定位速查：

| 路徑 | 職責 |
|---|---|
| `shared.py` | 建立唯一的 `mcp = FastMCP("ansys-unified-mcp")`，所有工具掛在它身上 |
| `__main__.py` | 進入點：載入 7 個 tools 模組（觸發 `@mcp.tool()` 註冊）→ 預掃執行中的 ANSYS 進程 → `mcp.run(stdio)` |
| `tools/mechanical.py` | Mechanical 工具（39） |
| `tools/workbench_bridge.py` | Workbench bridge 工具（31） |
| `tools/sim_tools.py` | Fluent 工具（29） |
| `tools/workbench.py` | Workbench 批次 job 工具（6） |
| `tools/optislang.py` | optiSLang 工具（5） |
| `tools/docs_tools.py` | ANSYS API 文件檢索工具（4） |
| `tools/connection_doctor.py` | 連線診斷 |
| `products/mechanical.py` | `MechanicalController`：Mechanical session 邏輯 |
| `products/optislang.py` | `OptislangController`：optiSLang session 邏輯（走 `SessionRegistry`） |
| `drivers/sim_impl.py` | Fluent（PyFluent）實作 |
| `bridges/workbench_bridge.py` | Workbench 檔案 IPC bridge 實作 |
| `core/sessions.py` | `SessionRegistry` 單例 |
| `core/paths.py` | 統一 ANSYS exe 路徑解析 |
| `config.py` | ANSYS 安裝偵測（非致命 degraded） |
| `connection_manager.py` | `ConnectionManager`：掃 port / 進程 |
| `docs/` | 文件檢索子系統（見第 5 節） |

## 4. 兩條執行通道（重要）

到達 ANSYS 有**兩種不同機制**，維護時要分清楚：

1. **gRPC 即時 session**（Mechanical / Fluent / optiSLang）
   透過 PyMechanical / PyFluent / PyOptiSLang 連上正在跑的 App，session 存進 `SessionRegistry`，之後把腳本丟進去即時執行。Mechanical 用 temp-file 捕捉 stdout，以跨 gRPC 邊界可靠取回 `print()` 輸出。

2. **檔案 IPC bridge / 批次子程序**（Workbench）
   `bridges/workbench_bridge.py` 把命令寫成 JSON 丟進 `COMMANDS_DIR`，輪詢 `RESULTS_DIR` 等回應（搭配跑在 Workbench 裡的 `.wbjn` journal）。另有 `tools/workbench.py` 走非同步批次（`RunWB2 -R` / `ansys-mechanical.exe -i`）。

## 5. 文件檢索子系統（docs/）

讓 AI **不必整檔載入**（原始文件多達數 MB）就能查 ANSYS API。

- Pipeline：`Documentation_md/`（原始）→ `docs/clean.py` 清洗 → `Documentation_clean/`（精選副本）→ 分塊 → SQLite FTS5（trigram）索引 `Documentation_clean/docs_index.sqlite`。
- 檢索：`search_ansys_docs`（搜片段）→ `get_ansys_doc_chunk`（取整塊），另有 `list_ansys_docs`、`rebuild_ansys_docs_index`。
- 哪些文件進索引由 `docs/config.py` 的 `API_DOCS` 白名單決定（每筆有 `name/title/category/product/style`）。
- 限制：FTS5 trigram 只做關鍵字/子字串比對；中文→英文的概念級比對不在範圍內（未來語意層再處理）。

## 6. 已知不一致 / 技術債（誠實記錄）

維護前先知道這些「架構偏亂」的具體來源，避免踩雷或以為是自己搞錯：

1. **`workbench_bridge.py` 有兩份**：`bridges/`（實作）與 `tools/`（31 個工具，且自行從 `config` 推 `RUNWB2` 等路徑常數）。後者與 `core/paths.py` 想統一路徑解析的目標**重複**。
2. **產品分層尚未完全對稱**：`products/` 目前有 `mechanical.py` 與 `optislang.py`；**Fluent 實作仍在 `drivers/sim_impl.py`**（尚未收斂為 `products/fluent.py` 控制器）。這是剩餘的收斂目標。
3. **session 模式已大致統一（optiSLang 已修）**：Mechanical 與 optiSLang 皆已用 `SessionRegistry`（見 `products/`）。優先修正的模組全域 `_osl` 技術債已移除。**剩餘**：Fluent（`drivers/sim_impl.py`）尚未確認是否全走 `SessionRegistry`，為後續收斂項。
4. **文件涵蓋未齊**：`API_DOCS` 目前僅 5 檔、涵蓋 3 產品（mechanical / ls-prepost / optislang）。目標是涵蓋全部五產品（待補 fluent / spaceclaim / lsdyna），並以 `category` 把 api/scripting 與 guide/tutorial 分流。
5. **`SKILLs/` 與 `.kiro/skills/` 持續同步問題**：已建立 `sync_skills.ps1` 解決。
6. **Documentation Pipeline 中 2 個漏網檔未進入索引**：`LS-DYNA_Keyword_and_Theory_Manuals.md`, `Structural_Optimization_Analysis_Guide.md`。
7. **Workbench 三通道競爭問題**：Batch subprocess / File-IPC / PyWorkbench gRPC 需決定主通道。
8. **Fluent/Geometry 未收斂至 products/ 層**：仍使用全域變數。
9. **測試覆蓋率僅 4/15 模組**。

## 7. 維護與擴充指引

- **新增一個工具**：放進對應 `tools/<product>.py`，用 `@mcp.tool()`；命名與回傳信封遵循 `ARCHITECTURE.md` 的慣例；底層優先走 script runner。
- **新增一個產品**：目標是 `tools/<product>.py`（工具）+ `products/<product>.py`（控制器，用 `SessionRegistry`）成對出現，逐步收斂上述不一致。
- **改連線 / session 核心**（`core/`、`connection_manager.py`、`products/`）：這些路徑目前**無測試覆蓋**，改動前先補冒煙測試，並讓審查者與實作者為不同人／實例。
- **加文件到索引**：在 `docs/config.py` 的 `API_DOCS` 增列，設好 `product/category`，跑 `rebuild_ansys_docs_index()` 重建。

## 8. 相關文件

- `ARCHITECTURE.md`：分層職責、工具命名規則、`_json` 回傳信封慣例（C2）。
- `pyansys-mapping-and-roadmap.md`：Workbench/授權模組 ↔ 官方 pyansys 套件 ↔ 官方 MCP ↔ 安裝現況對照，及專案後續規劃 roadmap。
- `README.md`：安裝與啟動（如存在）。
- `specs/*.md`：個別功能規格（如存在）。
