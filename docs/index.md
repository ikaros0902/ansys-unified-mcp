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

- [PCB 熱翹曲自動化紀錄](PCB_WARPAGE_AUTOMATION_LOG.md): PCB 多層疊構熱翹曲分析管線的建置過程與問題排除紀錄。
- [Session 經驗總結與排障手冊](session_learnings_and_troubleshooting.md): ANSYS Mechanical ACT Model Tree 底層物件模型等實戰經驗沉澱。
- [MultiZone 幾何分類候選規則](mesh_classification_heuristics.md): 網格分類候選規則觀察庫，狀態為 Shadow Mode（記錄觀察中，暫不啟用）。

## 外部對標分析（根目錄）

- [架構優化與重構總計畫對比](ARCHITECTURE_COMPARISON_AND_REFACTOR_PLAN.md): 基於 CAE-Agent-Hub 三個 ANSYS MCP 目錄源碼精讀之架構對比分析。
- [官方 PyAnsys MCP 評估報告](PYANSYS_MCP_EVALUATION.md): 官方 PyAnsys MCP Server 系列功能定位與整合可能性評估。

## Agent 規範路由入口（根目錄）

> 以下兩份非知識文件，是 AI agent 開工時的規範路由入口。

- [`AGENTS.md`](AGENTS.md): 全域與專案 Agent 指導核心規範路由。
- [`ANTIGRAVITY.md`](ANTIGRAVITY.md): 開工準則與安全防線精簡入口。

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
- 技能庫索引：[`skills/README.md`](../skills/README.md)
