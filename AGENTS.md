# 全域工作規範

- 回覆、計畫與任務使用繁體中文。一般程式註解用繁中；ANSYS ACT／APDL／SCDM 內嵌腳本使用 ASCII 英文，保留 API、識別碼與單位。
- 完成已授權的最小完整變更，保留使用者既有工作、輸入校驗及防資料損失處理。可逆工作自主推進；權限、外部訊息、破壞性 Git、資料刪除、部署與求解遵守實際授權及平台限制。
- 代理不得自行建立 Git commit。只有使用者明確要求或授權 commit 時，才可建立 commit；push、發 PR 或其他遠端 Git 操作也須依使用者明確授權執行。
- 完成宣稱附原始證據與未測範圍；編譯、工具 ok 或代理自述不能替代真實行為。物理門檻依專案、分析型態與有效參考，不將統一 5% 套到所有指標。
- 實作者與必要的獨立 reviewer 分開；小任務直接完成。容量不足時分批，不以自審充當必要獨立驗收。
- 重用既有技能及工具，不安裝重複工作模式，不自行 commit／push、發訊息、建立排程或求解。

按任務讀取，不全量載入：

| 情境 | 來源 |
| --- | --- |
| 行為、安全、語言 | [行為](rules/00-behavior.md)、[安全](rules/01-safety.md) |
| 複雜工作、驗收、失敗自愈 | [工程驗證](rules/10-loop-engineering.md)、[證據工作流](rules/12-evidence-workflows.md) |
| 選技能、規格／票、長任務 | [技能路由](rules/60-workflow-routing.md) |
| MCP／hooks／工具與載入差異 | [執行環境](rules/15-runtime-tools.md) |
| 子代理與模型 | [調度](rules/40-workflow-model-tiers.md)、agents/*.toml |
| 重大架構分歧 | [按需探索](rules/20-adhd.md) |
| 技能更新、寫作、Kiro | [技能演化](rules/11-skill-evolution.md)、[寫作](rules/30-writing-style.md)、[Kiro](rules/50-kiro-cli-dispatch.md) |

rules 是按需文件；連結本身不代表全部常駐。skills/ 是技能資源，agents/*.toml 才是原生角色設定。MCP 以當次工具與唯讀探測為準，設定存在不等於已連通。

<!-- CODEGRAPH_START -->
## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
<!-- CODEGRAPH_END -->
