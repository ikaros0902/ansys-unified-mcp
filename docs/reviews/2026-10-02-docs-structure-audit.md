# docs/ 現況 vs 計畫文件辨識度稽核

稽核目的：AI agent 讀取 `docs/` 時，無法區分「描述現況的文件」與「描述未實作願景的計畫文件」，曾導致引用 Phase 2 & 3 計畫中的 split-server 架構誤判為現況。本報告僅稽核與列建議，**不修改、不搬動任何現有文件**；是否套用由使用者後續決定。

稽核範圍：`docs/` 目錄下的文件分類標示與交叉引用，不含程式碼或 `skills/` 目錄內容修改。

---

## 摘要

`docs/ARCHITECTURE.md` 描述的現況是單一統一伺服器架構；`docs/planning/ANSYS_MCP_MASTER_PLAN_V4.md`、`docs/planning/PHASE_2_AND_3_EXECUTION_PLAN.md`、`docs/architecture/DIRECTORY_STRUCTURE_REORGANIZATION.md` 描述的是尚未實作的 split-server 願景。這兩份 planning 文件完全未被 `docs/index.md` 索引，且本身無任何「尚未實作」標示，也內嵌已不存在的舊專案路徑 `F:\Ming_python\ansys-unified-mcp`（現況為 `D:\Ikaros\ANSYS-unified-MCP`）。三者疊加，是 AI agent 誤判現況的根因。

**Verdict**: NEEDS_CHANGES（待使用者決定是否套用下列建議）

---

## Watch for

- **Planning 核心願景文件完全未被索引（confirmed）**：`docs/index.md` 的 planning 區塊僅列 `ANSYS_MCP_EVALUATION_AND_OPTIMIZATION_PLAN.md`、`ANSYS_MCP_SESSION_OPTIMIZATION_PLAN.md` 兩份，`ANSYS_MCP_MASTER_PLAN_V4.md` 與 `PHASE_2_AND_3_EXECUTION_PLAN.md`——恰是本次問題觸發點——未被索引，AI agent 若靠 index.md 導覽會直接漏看，若靠全文搜尋找到則會因無標頭而誤判現況。
- **願景文件缺少「尚未實作」標頭（confirmed）**：見 Task 1，兩份文件目前皆無任何現況/計畫區分標示。
- **願景文件內嵌已不存在的舊路徑（confirmed）**：見 Task 2，`F:\Ming_python\ansys-unified-mcp` 於 5 個檔案中出現，當前專案路徑為 `D:\Ikaros\ANSYS-unified-MCP`。
- **index.md 圖表清單少列 1 個檔案（confirmed）**：`docs/diagrams/` 實際有 5 個 HTML，index.md 只列 4 個，缺 `ansys_rearchitecture_overview.html`。
- **根目錄 7 份文件未分類（confirmed）**：`PCB_WARPAGE_AUTOMATION_LOG.md`、`session_learnings_and_troubleshooting.md`、`mesh_classification_heuristics.md`、`PYANSYS_MCP_EVALUATION.md`、`ARCHITECTURE_COMPARISON_AND_REFACTOR_PLAN.md`、`AGENTS.md`、`ANTIGRAVITY.md` 皆未被 index.md 提及，性質混雜（現況知識／外部對標分析／規範路由入口）。
- **技能數量寫死且口徑不穩定（confirmed）**：`skills/README.md`、`archive/README.md` 皆以寫死數字描述技能清單；`ansys-spaceclaim-modeling` 缺 `SKILL.md` 導致是否計入有歧義，`shock-analysis-workflow` 算 1 個或 8 個子技能亦無統一口徑。
- **`ansys-spaceclaim-modeling` 為孤立 stub（confirmed）**：目錄下僅有 `scripts/`，無 `SKILL.md`，非文件辨識度問題但一併記錄。

---

## Task 1：願景文件警示標頭設計

### `docs/planning/ANSYS_MCP_MASTER_PLAN_V4.md`（決策願景型）

建議插入位置：檔案最上方，標題之後第一行。

```markdown
> [!NOTE]
> 本文件為尚未實作之架構願景（Phase 2 & 3 重構方向），描述的 split-server /
> 多實例動態埠架構**非當前實作**。當前實際架構為單一統一伺服器，見
> [ARCHITECTURE.md](../ARCHITECTURE.md)。本文件僅供決策參考，執行與否尚待確認。
```

### `docs/planning/PHASE_2_AND_3_EXECUTION_PLAN.md`（執行計畫型，風險較高）

建議插入位置：檔案最上方，標題之後、現有「專案路徑」區塊之前。

```markdown
> [!CAUTION]
> 本文件為執行計畫草稿，**Phase 2 與 Phase 3 均尚未實作**。文件內「專案路徑」與
> 關聯文件連結指向舊工作目錄 `F:\Ming_python\ansys-unified-mcp`，現況專案路徑為
> `D:\Ikaros\ANSYS-unified-MCP`，連結可能已失效。當前實際架構見
> [ARCHITECTURE.md](../ARCHITECTURE.md)。
```

兩段標頭语气差異：MASTER_PLAN_V4 用 `[!NOTE]`（決策尚未定案，語氣中性）；PHASE_2_AND_3 用 `[!CAUTION]`（已是具體執行步驟+含失效路徑，風險更高，語氣更強）。

---

## Task 2：全 docs/ 範圍 F:\Ming_python 殘留清單

全 `docs/` 目錄掃描，確認殘留分布於以下 5 個檔案。

### 不動組（歷史快照／審查記錄原文，不應修改本文）

| 檔案 | 出現次數 | 處置建議 |
| --- | --- | --- |
| `docs/architecture/historical_specs/ORIGINAL_REQUEST.md` | 8 處 | 已有歸檔警示機制（見該檔上層 `historical_specs/` 定位），僅建議既有警示補一句「含過時路徑，為歷史原文」，不動正文 |
| `docs/reviews/2026-09-24-153530-chore-restructure.md` | 約 5 處 | 審查記錄引述舊路徑作為稽核證據，屬性是「記錄曾經的問題」，不應修改本文 |

### 待改組（現況/計畫文件，建議修正）

**`docs/PCB_WARPAGE_AUTOMATION_LOG.md`**（現況知識沉澱文件，3 處）

| 行號 | 原文片段 | 建議改法 |
| --- | --- | --- |
| 10 | `[src/ansys_unified_mcp/drivers/sim_impl.py](file:///F:/Ming_python/ansys-unified-mcp/src/ansys_unified_mcp/drivers/sim_impl.py)` | 改為專案相對連結 `../src/ansys_unified_mcp/drivers/sim_impl.py` |
| 13 | `[src/ansys_unified_mcp/tools/workbench_filebridge.py](file:///F:/Ming_python/ansys-unified-mcp/src/ansys_unified_mcp/tools/workbench_filebridge.py)` | 改為專案相對連結 `../src/ansys_unified_mcp/tools/workbench_filebridge.py` |
| 113 | `` `F:\Ming_python\ansys-unified-mcp\workbench_queue\` `` | 改為 `` `<專案根目錄>\workbench_queue\`（現況為 D:\Ikaros\ANSYS-unified-MCP） `` |

**`docs/architecture/DIRECTORY_STRUCTURE_REORGANIZATION.md`**（2 處）

| 行號 | 原文片段 | 建議改法 |
| --- | --- | --- |
| 3 | `**模組路徑**：\`F:\Ming_python\ansys-unified-mcp\`` | 改為「**模組路徑**：`<專案根目錄>`（本文件撰寫時路徑為 `F:\Ming_python\ansys-unified-mcp`，現況為 `D:\Ikaros\ANSYS-unified-MCP`）」，保留原始路徑作歷史標註而非直接刪除 |
| 43 | `F:\Ming_python\ansys-unified-mcp\`（目錄樹頂層） | 同上，改為 `<專案根目錄>\` 並加註原路徑 |

**`docs/planning/PHASE_2_AND_3_EXECUTION_PLAN.md`**（2 處，與 Task 1 標頭呼應）

| 行號 | 原文片段 | 建議改法 |
| --- | --- | --- |
| 3 | `> **專案路徑**：\`F:\Ming_python\ansys-unified-mcp\`` | 改為「> **專案路徑**：`<專案根目錄>`（原文撰寫時為 `F:\Ming_python\ansys-unified-mcp`，現況為 `D:\Ikaros\ANSYS-unified-MCP`）」 |
| 4 | `> **關聯文件**：[ANSYS_MCP_MASTER_PLAN_V4.md](file:///F:/Ming_python/ansys-unified-mcp/docs/planning/ANSYS_MCP_MASTER_PLAN_V4.md)` | 改為專案相對連結 `[ANSYS_MCP_MASTER_PLAN_V4.md](./ANSYS_MCP_MASTER_PLAN_V4.md)` |

---

## Task 3：docs/index.md 完整版草稿

```markdown
# ANSYS Unified MCP 文件索引

本索引涵蓋 `docs/` 下的全部文件資產。文件依用途分為六個目錄：架構、計畫、部署、測試、圖表與歷史歸檔。

---

## 架構 (`architecture/`)

- [ANSYS Unified MCP 架構與規格評估白皮書](architecture/ANSYS_UNIFIED_MCP_ARCHITECTURE_AND_SPECIFICATION_REPORT.md): 涵蓋結構、幾何、熱傳/Icepak、PyPrimeMesh 與電子封裝五大領域的架構與規格評估。
- [目錄樹架構收斂與精簡規範](architecture/DIRECTORY_STRUCTURE_REORGANIZATION.md): 目錄混亂根因排查與重組後架構分層；⚠️ 文件內含部分未實作之 split-server 願景內容，現況以 `ARCHITECTURE.md` 為準。
- [Mechanical 連線解析與長求解超時修復紀錄](architecture/FIX_MECHANICAL_CONNECTION_AND_SOLVE_TIMEOUT.md): PCB 79 層熱翹曲分析任務中連線埠解析與求解逾時問題的根因分析與修復記錄。
- [歷史規格快照](architecture/historical_specs/): Phase 1 原始需求書與規格書，供追溯決策脈絡，不可作為現況依據。
- 系統分層與工具命名信封慣例請參閱根目錄 [`ARCHITECTURE.md`](../ARCHITECTURE.md)。

## 計畫 (`planning/`)

> ⚠️ 下列文件描述尚未實作之架構願景或執行計畫草稿，**非專案現況**。現況架構請見 [`ARCHITECTURE.md`](../ARCHITECTURE.md)。

- [ANSYS Unified MCP 重構大計畫 (Master Plan v4.0)](planning/ANSYS_MCP_MASTER_PLAN_V4.md): 對標官方 PyAnsys 架構之 split-server / 動態埠願景，決策尚未定案。
- [重構實施計畫：Phase 2 & Phase 3](planning/PHASE_2_AND_3_EXECUTION_PLAN.md): 承接 Master Plan v4 之執行步驟草稿，Phase 2、3 均尚未實作，文件內部分路徑引用已過時。
- [ANSYS MCP 五大領域全面評估與優化計畫書](planning/ANSYS_MCP_EVALUATION_AND_OPTIMIZATION_PLAN.md): 深度對標 PyAnsys 官方 Tutorial 與各大教學網站之優化里程碑計畫書。
- [Session 完整盤點與全流程標準化優化實施計畫](planning/ANSYS_MCP_SESSION_OPTIMIZATION_PLAN.md): 衝擊分析管線 Session 05~08 補齊、端到端全閉環與全庫硬編碼路徑解耦實施計畫。

## 部署 (`deployment/`)

- [ANSYS Unified MCP 安裝與部署標準作業手冊 (Deployment SOP)](deployment/DEPLOYMENT_SOP.md): 針對全新機器環境的完整安裝、虛擬環境、外掛註冊、AI 客戶端配置與三重驗證 SOP。

## 測試 (`testing/`)

- [測試基礎設施規範 (TEST_INFRA)](testing/TEST_INFRA.md): 4-Tier 漸進式測試防線架構、自動化執行命令、覆蓋門檻、Mocking 設施與合成端到端場景驗收規格。

## 圖表 (`diagrams/`)

自包含互動式 HTML 架構圖，可直接以瀏覽器開啟：

- [`ansys_mcp_architecture.html`](diagrams/ansys_mcp_architecture.html): MCP 伺服器整體架構圖。
- [`ansys_current_actual_architecture.html`](diagrams/ansys_current_actual_architecture.html): 現行實際架構盤點圖。
- [`ansys_rearchitecture_overview.html`](diagrams/ansys_rearchitecture_overview.html): 重構願景架構總覽圖（對應 `planning/` 之未實作計畫）。
- [`ansys_agent_skills_architecture.html`](diagrams/ansys_agent_skills_architecture.html): Agent 技能庫分層架構圖。
- [`act_workflow_comparison.html`](diagrams/act_workflow_comparison.html): ACT 工作流對照圖。

## 現況知識沉澱（根目錄）

- [PCB 熱翹曲自動化紀錄](../docs/PCB_WARPAGE_AUTOMATION_LOG.md): PCB 多層疊構熱翹曲分析管線的建置過程與問題排除紀錄。
- [Session 經驗總結與排障手冊](../docs/session_learnings_and_troubleshooting.md): ANSYS Mechanical ACT Model Tree 底層物件模型等實戰經驗沉澱。
- [MultiZone 幾何分類候選規則](../docs/mesh_classification_heuristics.md): 網格分類候選規則觀察庫，狀態為 Shadow Mode（記錄觀察中，暫不啟用）。

## 外部對標分析（根目錄）

- [架構優化與重構總計畫對比](../docs/ARCHITECTURE_COMPARISON_AND_REFACTOR_PLAN.md): 基於 CAE-Agent-Hub 三個 ANSYS MCP 目錄源碼精讀之架構對比分析。
- [官方 PyAnsys MCP 評估報告](../docs/PYANSYS_MCP_EVALUATION.md): 官方 PyAnsys MCP Server 系列功能定位與整合可能性評估。

## Agent 規範路由入口（根目錄）

> 以下兩份非知識文件，是 AI agent 開工時的規範路由入口。

- [`AGENTS.md`](../docs/AGENTS.md): 全域與專案 Agent 指導核心規範路由。
- [`ANTIGRAVITY.md`](../docs/ANTIGRAVITY.md): 開工準則與安全防線精簡入口。

## 審查記錄 (`reviews/`)

- 歷次文件結構 / 程式碼變更的獨立審查記錄，記錄當時發現的問題與 Verdict，供追溯用，內容不隨現況更新。

## 歷史歸檔 (`archive/`)

> ⚠️ 歸檔文件皆為歷史快照，數據已過期，**不可作為現況依據**。清單與各自歸檔理由見 [`archive/README.md`](archive/README.md)。

---

## 工程實例與教學

- [衝擊分析 (35G LS-DYNA 管線)](../examples/shock_analysis/README.md): 35G 六向半正弦衝擊波生成、材料自動匹配、接觸與接合設定、網格控制與 input deck 導出。
- [幾何清理 (SpaceClaim 與 PyAnsys Geometry)](../examples/geometry_cleanup/README.md): 自動特徵消除、螺絲扣件刪除與零厚度/薄片實體移除。

## 核心架構模組（原始碼）

- `src/ansys_unified_mcp/connection_manager.py`: 動態 gRPC 埠探測與實例偵測。
- `src/ansys_unified_mcp/jobs/`: 模擬沙盒管理與成果生命週期。
- `src/ansys_unified_mcp/gatekeeper/`: 前置物理檢核與安全閘門。
- `src/ansys_unified_mcp/core/sentinel/`: 非同步求解器即時守護與發散熔斷。

## 其他入口

- 專案概觀與快速上手：[`README.md`](../README.md)
- AI 代理規範路由：[`AGENTS.md`](../AGENTS.md)
- 專案心智模型：[`contexts/context.md`](../contexts/context.md)
- 技能庫索引：[`SKILLs/README.md`](../SKILLs/README.md)
```

> 備註：草稿中「技能庫索引」連結沿用原文的 `SKILLs/README.md` 大小寫，實際專案現況目錄為小寫 `skills/`，連結路徑是否需同步修正建議併入後續執行階段處理，本次僅忠實呈現草稿。

---

## Task 4：技能數量標示問題與 stub 問題

### 技能數量寫死問題

`skills/README.md`、`archive/README.md` 皆以寫死數字描述技能清單。統計口徑本身不穩定，原因：

1. `ansys-spaceclaim-modeling/` 目錄僅有 `scripts/`，無 `SKILL.md`，是否計入技能總數，各文件寫法不一致、無共同判準。
2. `shock-analysis-workflow/` 是 1 個頂層技能，內部又拆成 8 個子技能各自的 `SKILL.md`（`01-material-assignment` 至 `08-post-process-report`），統計時「算 1 個」或「算 8 個」沒有明確規則。
3. 數字每次新增/刪除技能都需要人工同步到至少兩個文件，過去已發生過漂移（見 `docs/reviews/2026-09-24-153530-chore-restructure.md` 記載的「16 vs 20」矛盾案例），屬重複性維護負擔，手動改一次數字不解決根本問題。

**建議**：將兩份文件中寫死的技能數字措辭改為引用式，例如「技能清單與完整數量見 [`skills/README.md`](../../skills/README.md)」，不在多處重複寫死同一數字，避免未來再度漂移。

### `ansys-spaceclaim-modeling` 孤立 stub（已處置）

`skills/ansys-spaceclaim-modeling/` 原僅有 `scripts/` 子目錄，缺少 `SKILL.md`。經追查，`skills/README.md` 記載此技能先前已因「與 `ansys-geometry-modeling` 完全重複」被刻意移除；但其對應的全域技能（`~/.gemini/config/skills/ansys-spaceclaim-modeling/`）內容完整，聚焦幾何前處理全流程（草圖→成形→外流域抽取→布林相減→CAD 缺陷診斷→無損 PMDB 導出），與 `ansys-geometry-modeling`、`ansys-spaceclaim` 的現有範圍不重複。

**處置結果（2026-10-02）**：選項 A，已從全域技能庫完整複製 `SKILL.md` + 6 份 `reference/*.md` + 2 份 `scripts/*.py` 回專案目錄，並同步修正 `skills/README.md` 中「已移除」的過時記載與技能索引表。

---

## 待決事項（供使用者決定是否套用）

| # | 建議動作 | 影響檔案數 | 風險 |
| --- | --- | --- | --- |
| 1 | 套用 Task 1 的兩段警示標頭 | 2 | 低，純增量 |
| 2 | 套用 Task 2 待改組的路徑修正 | 3 | 低，純文字替換 |
| 3 | 套用 Task 3 的 index.md 草稿 | 1 | 中，大幅改版現有索引 |
| 4 | 套用 Task 4 的措辭改法 | 2 | 低，純文字替換 |
| 5 | 處置 `ansys-spaceclaim-modeling` stub | 1→9 | 已完成（選項 A，含同步修正 skills/README.md 記載） |

**更新**：待決事項 1–5 已全數套用完成。
