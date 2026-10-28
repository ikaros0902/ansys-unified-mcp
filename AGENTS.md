# 全域工作規範

- 回覆、計畫與任務使用繁體中文。一般程式註解用繁中；ANSYS ACT／APDL／SCDM 內嵌腳本使用 ASCII 英文，保留 API、識別碼與單位。
- 完成已授權的最小完整變更，保留使用者既有工作、輸入校驗及防資料損失處理。可逆工作自主推進；權限、外部訊息、破壞性 Git、資料刪除、部署與求解遵守實際授權及平台限制。
- 任何代理（包含主代理與子代理）均不得自行建立、amend、rebase 或改寫 Git commit。只有使用者在本任務明確要求或授權時，主代理才可建立 commit；不得將 commit 委派給子代理。push、發 PR 或其他遠端 Git 操作也須依使用者明確授權執行。
- 完成宣稱附原始證據與未測範圍；編譯、工具 ok 或代理自述不能替代真實行為。物理門檻依專案、分析型態與有效參考，不將統一 5% 套到所有指標。
- 實作者與必要的獨立 reviewer 分開；小任務直接完成。容量不足時分批，不以自審充當必要獨立驗收。
- 重用既有技能及工具，不安裝重複工作模式；不得自行發訊息、建立排程或求解。

依任務查閱以下現有文件，不必全量載入：

| 情境 | 來源 |
| --- | --- |
| 行為、安全、語言 | 本檔及[公開發佈檢查](docs/maintenance/PUBLICATION_REVIEW.md) |
| 複雜工作、階段與驗收 | [專案重構計畫](docs/planning/FOLDER_TREE_REORGANIZATION_PLAN.md) |
| 技能分類與發現 | [技能庫索引](agents/skills/README.md) |
| MCP、部署與工具範圍 | [部署手冊](docs/deployment/DEPLOYMENT_SOP.md)、[工具範圍設定](docs/deployment/MCP_TOOL_SCOPING_GUIDE.md) |
| 程式架構與來源圖 | [架構導覽](docs/architecture/ARCHITECTURE.md)、[PyAnsys Source Intelligence](docs/architecture/PYANSYS_SOURCE_INTELLIGENCE.md) |
| Remote Worker 與 Debug Loop | [安全設計](docs/architecture/REMOTE_WORKER_AND_DEBUG_SAFETY.md) |
| 跨代理交接 | [Agent Handoff 範本](docs/maintenance/AGENT_HANDOFF_TEMPLATE.md) |

skills/ 是技能資源。MCP 以當次工具與唯讀探測為準，設定存在不等於已連通。

<!-- CODEGRAPH_START -->
## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
<!-- CODEGRAPH_END -->
