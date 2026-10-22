# 程式碼地圖

此表供定位之用；實作可能變動，修改前以目前工作樹為準，沿工具呼叫鏈檢查實際函式與測試。

| 任務 | 起始位置 | 往下追查 |
|---|---|---|
| MCP 工具註冊與產品 profile | `src/ansys_unified_mcp/__main__.py` | profile 會載入 `products/<product>/tools.py`；核心通用工具由 `tools/` 載入。工具總表不要只查 `tools/` |
| MCP 工具共用包裝 | `src/ansys_unified_mcp/shared.py` | 工具 decorator／別名、扁平 `ok/error` 信封、錯誤回傳等契約；修改回傳形狀前找呼叫端與契約測試 |
| MCP 工具實作 | `src/ansys_unified_mcp/tools/`、`src/ansys_unified_mcp/products/<product>/tools.py` | 核心工具看前者、產品工具看後者；再追對應 facade、driver、workflow 和工具契約測試 |
| Session／產品連線 | `src/ansys_unified_mcp/tools/session_manager_tools.py`、`connection_tools.py`、`src/ansys_unified_mcp/core/sessions.py` | `SessionRegistry` 在 `core/sessions.py`；再追 `connection/`、產品 controller 和 `tests/unit/`。不要從工具名稱猜產品可連線 |
| Mechanical／幾何／Fluent／optiSLang 行為 | `src/ansys_unified_mcp/products/<product>/`、`src/ansys_unified_mcp/drivers/` | 產品 controller/facade、宿主腳本、回傳解析器與 mock 測試 |
| API KB | `src/ansys_unified_mcp/analytics/apikb/`、`tools/apikb_tools.py` | schema/build/query/validate 與 `tests/unit/test_apikb_*.py`；查詢命中和驗證層級需分開 |
| 文件搜尋 | `src/ansys_unified_mcp/analytics/docsearch/`、`tools/docs_tools.py` | config/index、metadata filters 與 `tests/unit/test_docsearch_*.py` |
| Job 狀態、監控、結果報告 | `core/jobs/`、`core/sentinel/`、`analytics/postprocessing/`、`analytics/reporting/` | 狀態轉換、輸出解析、來源標籤及對應測試 |
| 端到端流程 | `src/ansys_unified_mcp/workflows/` | workflow 所用工具／drivers、輸入條件、真實與估算結果分支 |
| 專項知識 | `agents/skills/<domain>/SKILL.md` 和 `references/` | `agents/skills/README.md` 的路由索引及來源矩陣 |

## 快速查找方式

- 優先 `rg` 搜尋工具名稱、錯誤字串、類別或 API symbol，再讀命中函式周圍的最小範圍。
- 工具改動需同時看註冊 schema 和實作；工作流改動需沿工具一路查到結果生成及報告，避免只改描述文字。
- Repository-wide Python 結構探索可使用已配置的 code graph／Serena；若使用圖索引結論，先檢查相關檔案覆蓋範圍，未涵蓋行再直接讀取。
- 不將工具 metadata、Skill 範例或文件中的 API 名稱當作原始碼存在性的證明。
