# ANSYS Unified MCP 文件索引

本索引涵蓋 `docs/` 下的全部文件資產。文件依用途分為六個目錄：架構、計畫、部署、測試、圖表與歷史歸檔。

---

## 架構 (`architecture/`)

- [ANSYS Unified MCP 架構與規格評估白皮書](architecture/ANSYS_UNIFIED_MCP_ARCHITECTURE_AND_SPECIFICATION_REPORT.md): 涵蓋結構、幾何、熱傳/Icepak、PyPrimeMesh 與電子封裝五大領域的架構與規格評估。
- 系統分層與工具命名信封慣例請參閱根目錄 [`ARCHITECTURE.md`](../ARCHITECTURE.md)。

## 計畫 (`planning/`)

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
- [`ansys_agent_skills_architecture.html`](diagrams/ansys_agent_skills_architecture.html): Agent 技能庫分層架構圖。
- [`act_workflow_comparison.html`](diagrams/act_workflow_comparison.html): ACT 工作流對照圖。

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
