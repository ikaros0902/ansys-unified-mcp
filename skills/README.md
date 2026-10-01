# ANSYS CAE Engineering Skills Index

本目錄為 `ansys-unified-mcp` 專屬的 ANSYS CAE 技能庫，僅包含與 ANSYS 有限元分析、幾何建模、外掛開發與優化相關的專業工程技能：

---

## 專案核心 CAE 技能清單 (16 項)

| 技能名稱 | 專業領域 | 核心技術 / 觸發關鍵字 |
| :--- | :--- | :--- |
| **[`ansys-geometry-modeling`](ansys-geometry-modeling/SKILL.md)** | **PyAnsys Geometry 現代化幾何** | `ansys.geometry.core` 參數化草圖 / 拉伸旋轉, Named Selection, 無損 PMDB 直通；`PyAnsys Geometry`, `參數化幾何`, `Enclosure`, `匯出PMDB` |
| **[`ansys-spaceclaim`](ansys-spaceclaim/SKILL.md)** | **SpaceClaim 建模與腳本雙軌控制** | PyAnsys Geometry 與原生 ACT IronPython 雙軌 API；`SpaceClaim建模`, `SCDM腳本`, `SpaceClaim幾何`, `幾何前處理` |
| **[`ansys-mesh`](ansys-mesh/SKILL.md)** | **Mechanical / LS-DYNA 網格工程與 CFL 調優** | 自動網格劃分 (AutoMesh), 網格干涉檢查, CFL 最小時間步長量測, Node Merge / 局部 Pinch 調優；`ansys-mesh`, `網格劃分`, `網格品質`, `CFL步長`, `網格調優` |
| **[`pcb-warpage-analysis`](pcb-warpage-analysis/SKILL.md)** | **PCB 多層疊構熱翹曲分析** | ROM 複合材料巨集, Share Topology 疊構建模, 3-2-1 靜定支承；`PCB熱翹曲`, `PCB疊構`, `ROM材料計算`, `3-2-1支承` |
| **[`ansys-mechanical`](ansys-mechanical/SKILL.md)** | **Mechanical 結構、模態與熱耦合** | ACT Scripting (`ExtAPI`, `DataModel`), 非線性接觸, 網格前檢, 主元錯誤與應力奇異點判定；`靜態結構`, `模態分析`, `熱應力分析` |
| **[`ansys-submodeling-dpf`](ansys-submodeling-dpf/SKILL.md)** | **DPF 結果提取與局部子模型** | `on_coordinates` 形函數插值, `LocalMapdlPool` 併發求解, 聖維南切面連續性驗證；`子模型分析`, `Submodeling`, `DPF結果提取` |
| **[`ansys-optislang`](ansys-optislang/SKILL.md)** | **optiSLang 敏感度與最佳化設計** | LHS / DoE 抽樣, MOP 代理模型與 CoP, TSI 降維, NLPQLP / NSGA-II Pareto 尋優；`optiSLang`, `代理模型`, `敏感度分析`, `Pareto` |
| **[`ansys-parametric-study`](ansys-parametric-study/SKILL.md)** | **Workbench 參數集與雙軌選型** | Parameter Set 批次更新 (`UpdateAllDesignPoints`), DX 與 optiSLang 選型決策矩陣；`參數化研究`, `DesignXplorer`, `參數集更新` |
| **[`ansys-lsdyna`](ansys-lsdyna/SKILL.md)** | **LS-DYNA 顯式動力學與落摔** | `*KEYWORD` / `*MAT_024` / `*CONTACT_AUTOMATIC` / `*RIGIDWALL` 卡片, CFL 時間步長, 沙漏能與質量縮放診斷；`落摔試驗`, `Drop test`, `衝擊分析` |
| **[`shock-analysis-workflow`](shock-analysis-workflow/SKILL.md)** | **Shock / Drop 端到端管線編排** | 8 個模組化 session 技能串接（材料指派 → 接觸 → 網格 dt ≥ 2e-8 s → 遠端質量 → 截面 → 載荷 → 求解監控 → 報告）；`shock分析流程`, `落摔工作流`, `能量平衡監控` |
| **[`ansys-ls-prepost`](ansys-ls-prepost/SKILL.md)** | **LS-PrePost 前後處理** | SCL / cfile / Python data-center API, d3plot 結果查詢與雲圖輸出；`LS-PrePost`, `cfile`, `SCL`, `d3plot`, `fringe` |
| **[`ansys-fluent`](ansys-fluent/SKILL.md)** | **Fluent CFD 與共軛熱傳** | PyFluent 水密幾何 Poly-Hexcore 網格, SST k-omega, Coupled 求解, y+ 與質量守恆評估；`Fluent分析`, `PyFluent`, `CFD模擬`, `共軛熱傳`, `CHT` |
| **[`act-extension-development`](act-extension-development/SKILL.md)** | **ACT 外掛開發實戰** | IronPython 2.7 避坑, `FileSystemWatcher` 檔案 IPC 監聽, ACT Wizard (`.wbex`) 程式化調用；`ACT外掛`, `ACT開發`, `IronPython限制` |
| **[`pymechanical-operations`](pymechanical-operations/SKILL.md)** | **PyMechanical 遠端操作** | gRPC (port 10000+) 直連, `run_python_script` 遠端驅動, Body Sizing / MultiZone 網格自動化；`PyMechanical連線`, `Mechanical遠端控制`, `自動網格劃分` |
| **[`ansys-error-catalog`](ansys-error-catalog/SKILL.md)** | **CAE 錯誤分類與排查** | Workbench, Mechanical, SpaceClaim, ACT 報錯根因與修復對策；`ANSYS報錯`, `IronPython錯誤`, `Mechanical排障`, `ACT除錯` |
| **[`pdf-to-md`](pdf-to-md/SKILL.md)** | **ANSYS 說明文檔轉換** | `pymupdf4llm` 抽取純文字與表格, 逐頁標記, 產出 RAG / 檢索用 Markdown；`PDF轉Markdown`, `文檔轉換`, `說明書建索引` |

> 註：原 `ansys-spaceclaim-modeling` 與 `ansys-geometry-modeling` 完全重複，已於重整中移除並整併至 `ansys-geometry-modeling` 與 `ansys-spaceclaim`；原 `ansys-lsdyna-explicit`、`ansys-mechanical-multiphysics`、`ansys-optislang-optimization` 三個僅含一行路由指引的 stub 技能亦已於重整中移除，其路由職責分別由 **`ansys-lsdyna`**、**`ansys-mechanical`**、**`ansys-optislang`** 主技能完整涵蓋。

---

## 統一規範
- 全案通用/非 ANSYS 技能（如去 AI 味、Git 審查、Obsidian 筆記等）保留於全域技能庫，不污染本 CAE 倉庫。
- 本倉庫保持 100% 純淨的 ANSYS 模擬、自動化與 MCP 驅動專用架構。
