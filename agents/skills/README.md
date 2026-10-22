# ANSYS CAE Engineering Skills Index

本目錄為 `ansys-unified-mcp` 專屬的 ANSYS CAE 技能庫，僅包含與 ANSYS 有限元分析、幾何建模、外掛開發與優化相關的專業工程技能：

---

## 專案核心 CAE 技能清單（完整數量以下表實際列出項目為準）

| 技能名稱 | 專業領域 | 核心技術 / 觸發關鍵字 |
| :--- | :--- | :--- |
| **[`ansys-spaceclaim-component-library`](ansys-spaceclaim-component-library/SKILL.md)** | **裝配體元件擷取與查表建庫** | BOM／GUI 分類、元件樹盤點、既有 gRPC 查證、獨立元件另存與重新匯入驗證；`Common Part`, `元件擷取`, `元件樹盤點`, `開啟元件另存` |
| **[`ansys-geometry-modeling`](ansys-geometry-modeling/SKILL.md)** | **PyAnsys Geometry 現代化幾何** | `ansys.geometry.core` 參數化草圖 / 拉伸旋轉, Named Selection, 無損 PMDB 直通；`PyAnsys Geometry`, `參數化幾何`, `Enclosure`, `匯出PMDB` |
| **[`ansys-spaceclaim`](ansys-spaceclaim/SKILL.md)** | **SpaceClaim 建模與腳本雙軌控制** | PyAnsys Geometry 與原生 ACT IronPython 雙軌 API、作用中設計 STEP 匯出；`SpaceClaim建模`, `SCDM腳本`, `SpaceClaim幾何`, `幾何前處理` |
| **[`ansys-spaceclaim-modeling`](ansys-spaceclaim-modeling/SKILL.md)** | **SpaceClaim/Discovery 幾何前處理與無損流轉** | 2D 草圖拉伸, 外流域抽取 (Enclosure), 布林相減, CAD 缺陷診斷, 無損 PMDB 導出；`外流域抽取`, `PMDB導出`, `CAD缺陷診斷`, `Discovery前處理` |
| **[`ansys-mesh`](ansys-mesh/SKILL.md)** | **Mechanical / LS-DYNA 網格工程與 CFL 調優** | 自動網格劃分 (AutoMesh), 網格干涉檢查, CFL 最小時間步長量測, Node Merge / 局部 Pinch 調優；`ansys-mesh`, `網格劃分`, `網格品質`, `CFL步長`, `網格調優` |
| **[`simplify-ram`](simplify-ram/SKILL.md)** | **RAM 幾何簡化流程** | 先索取主機板 / RAM / socket 三個 body 名稱，再以 `geometry_simplify_ram(_batch)` 合併成板面方塊並建底面 NS；`簡化RAM`, `簡化記憶體`, `simplify RAM` |
| **[`simplify-heatsink`](simplify-heatsink/SKILL.md)** | **散熱片幾何簡化流程** | `geometry_simplify_heatsink` 鰭片填實、保留底面特徵與圓形鎖孔、移除螺絲，反推等效密度命名 `_rho<kg/m³>`；單一或多 body 組件；`簡化heatsink`, `簡化散熱片`, `simplify heatsink` |
| **[`pcb-warpage-analysis`](pcb-warpage-analysis/SKILL.md)** | **PCB 多層疊構熱翹曲分析** | ROM 複合材料巨集, Share Topology 疊構建模, 3-2-1 靜定支承；`PCB熱翹曲`, `PCB疊構`, `ROM材料計算`, `3-2-1支承` |
| **[`ansys-mechanical`](ansys-mechanical/SKILL.md)** | **Mechanical 結構、模態與熱耦合** | ACT Scripting (`ExtAPI`, `DataModel`), 非線性接觸, 網格前檢, 主元錯誤與應力奇異點判定；`靜態結構`, `模態分析`, `熱應力分析` |
| **[`ansys-submodeling-dpf`](ansys-submodeling-dpf/SKILL.md)** | **DPF 結果提取與局部子模型** | `on_coordinates` 形函數插值, `LocalMapdlPool` 併發求解, 聖維南切面連續性驗證；`子模型分析`, `Submodeling`, `DPF結果提取` |
| **[`ansys-optislang`](ansys-optislang/SKILL.md)** | **optiSLang 敏感度與最佳化設計** | LHS / DoE 抽樣, MOP 代理模型與 CoP, TSI 降維, NLPQLP / NSGA-II Pareto 尋優；`optiSLang`, `代理模型`, `敏感度分析`, `Pareto` |
| **[`ansys-parametric-study`](ansys-parametric-study/SKILL.md)** | **Workbench 參數集與雙軌選型** | Parameter Set 批次更新 (`UpdateAllDesignPoints`), DX 與 optiSLang 選型決策矩陣；`參數化研究`, `DesignXplorer`, `參數集更新` |
| **[`ansys-lsdyna`](ansys-lsdyna/SKILL.md)** | **LS-DYNA 顯式動力學與落摔** | `*KEYWORD` / `*MAT_024` / `*CONTACT_AUTOMATIC` / `*RIGIDWALL` 卡片, CFL 時間步長, 沙漏能與質量縮放診斷；`落摔試驗`, `Drop test`, `衝擊分析` |
| **[`shock-analysis-workflow`](shock-analysis-workflow/SKILL.md)** | **Shock / Drop 端到端管線編排** | 8 個模組化 session 技能串接（材料指派 → 接觸 → 網格 dt ≥ 2e-8 s → 遠端質量 → 截面 → 載荷 → 求解監控 → 報告）；`shock分析流程`, `落摔工作流`, `能量平衡監控` |
| **[`ansys-ls-prepost`](ansys-ls-prepost/SKILL.md)** | **LS-PrePost 前後處理** | SCL / cfile / Python data-center API, d3plot 結果查詢與雲圖輸出；`LS-PrePost`, `cfile`, `SCL`, `d3plot`, `fringe` |
| **[`ansys-fluent`](ansys-fluent/SKILL.md)** | **Fluent CFD 與共軛熱傳** | PyFluent 水密幾何 Poly-Hexcore 網格, SST k-omega, Coupled 求解, y+ 與質量守恆評估；`Fluent分析`, `PyFluent`, `CFD模擬`, `共軛熱傳`, `CHT` |
| **[`ansys-spaceclaim-defeature`](ansys-spaceclaim-defeature/SKILL.md)** | **SpaceClaim 特徵簡化與缺陷修復** | 孔洞/倒角/圓角批次辨識與移除、微小邊縫縫合、CAD 幾何破面修復；`簡化孔洞`, `移除倒角`, `CAD破面修復`, `defeature` |
| **[`ansys-bga-modeling`](ansys-bga-modeling/SKILL.md)** | **BGA 錫球陣列自動化幾何建模** | 矩形/周邊陣列錫球自動生成、PCB/晶片接觸印記、等效材料指派；`BGA建模`, `錫球陣列`, `BGA array`, `solder ball` |
| **[`ansys-material-assignment`](ansys-material-assignment/SKILL.md)** | **Mechanical / LS-DYNA 材料與等效密度自動指派** | BOM 表格對應、關鍵字比對、自訂密度反推計算、未指派幾何體檢核；`材料指派`, `BOM對應`, `材料賦予`, `assign material` |
| **[`act-extension-development`](act-extension-development/SKILL.md)** | **ACT 外掛開發實戰** | IronPython 2.7 避坑, `FileSystemWatcher` 檔案 IPC 監聽, ACT Wizard (`.wbex`) 程式化調用；`ACT外掛`, `ACT開發`, `IronPython限制` |
| **[`pymechanical-operations`](pymechanical-operations/SKILL.md)** | **PyMechanical 遠端操作** | gRPC (port 10000+) 直連, `run_python_script` 遠端驅動, Body Sizing / MultiZone 網格自動化；`PyMechanical連線`, `Mechanical遠端控制`, `自動網格劃分` |
| **[`ansys-error-catalog`](ansys-error-catalog/SKILL.md)** | **CAE 錯誤分類與排查** | Workbench, Mechanical, SpaceClaim, ACT 報錯根因與修復對策；`ANSYS報錯`, `IronPython錯誤`, `Mechanical排障`, `ACT除錯` |
| **[`pdf-to-md`](pdf-to-md/SKILL.md)** | **ANSYS 說明文檔轉換** | `pymupdf4llm` 抽取純文字與表格, 逐頁標記, 產出 RAG / 檢索用 Markdown；`PDF轉Markdown`, `文檔轉換`, `說明書建索引` |
| **[`ansys-spaceclaim-interface-check`](ansys-spaceclaim-interface-check/SKILL.md)** | **SpaceClaim 裝配體求解前閘門檢查** | 水密性/非manifold邊/自由邊/重複面拓撲診斷, 體間干涉 bounding-box 粗篩+精篩兩階段偵測；`干涉檢查`, `水密性`, `拓撲診斷`, `interference check` |
| **[`ansys-spaceclaim-classify-group`](ansys-spaceclaim-classify-group/SKILL.md)** | **body/face 自動分類與具名群組** | 孔徑篩選, 全圓/半圓邊判別, Within Component / Ignore Component 階層配對, 距離分級；`孔位配對`, `分類群組`, `classify group` |
| **[`ansys-spaceclaim-midsurface`](ansys-spaceclaim-midsurface/SKILL.md)** | **鈑金件中面抽取與修復** | 薄板候選偵測, 對向面配對, 中面抽取, 間隙重疊修復與法向校正；`中面抽取`, `midsurface`, `鈑金殼單元` |
| **[`ansys-named-selection-rm-contact`](ansys-named-selection-rm-contact/SKILL.md)** | **SpaceClaim→Mechanical 具名選擇命名橋接** | `Connect Topology`/`_Mobile`/`_Reference`/`Scr_RM_grp` 命名字典, static/thermal/LS-DYNA 消費差異表；`具名選擇命名`, `named selection`, `RM命名規範` |
| **[`ansys-mechanical-section-assign`](ansys-mechanical-section-assign/SKILL.md)** | **厚度/截面/單元公式通用指派** | Mechanical `Thickness`/`CrossSection` 隱式路徑, LS-DYNA `*SECTION_SHELL`/`*SECTION_SOLID` 顯式卡片雙模式；`截面指派`, `厚度指派`, `section assign` |
| **[`ansys-mechanical-connections`](ansys-mechanical-connections/SKILL.md)** | **接觸/運動副/遠端點建立與檢查** | 由 NS 命名自動判斷類型建立 Bonded Contact / Joint / Remote Point, Contact Tool 驗證, Error 20110 過度約束防呆；`接觸建立`, `運動副`, `connections check` |
| **[`ansys-mechanical-boundary-conditions`](ansys-mechanical-boundary-conditions/SKILL.md)** | **約束與載荷施加雙模式** | 靜態結構/熱分析穩態邊界 (Convection/Radiation/HeatFlux) 與 LS-DYNA shock 半正弦衝擊脈衝/初始速度；`邊界條件`, `shock衝擊載荷`, `boundary conditions` |

> 註：`ansys-spaceclaim-modeling` 原於重整中因「與 `ansys-geometry-modeling` 完全重複」被移除，後於 2026-10-02 重新評估：其內容聚焦幾何前處理全流程（草圖→成形→外流域抽取→布林相減→CAD 缺陷診斷→無損 PMDB 導出），與 `ansys-geometry-modeling`（PyAnsys Geometry API 操作參考）及 `ansys-spaceclaim`（雙軌 API 連線/Session 管理）分工不同，故已恢復為獨立技能，不再視為重複；原 `ansys-lsdyna-explicit`、`ansys-mechanical-multiphysics`、`ansys-optislang-optimization` 三個僅含一行路由指引的 stub 技能仍維持已於重整中移除之狀態，其路由職責分別由 **`ansys-lsdyna`**、**`ansys-mechanical`**、**`ansys-optislang`** 主技能完整涵蓋。

---

## 目錄結構規範（漸進式揭露）

每個 skill 統一遵循四層資源結構：

```
<skill-name>/
├── SKILL.md       # 總指揮官：用途、觸發情境、Router 表、Don'ts（≤150 行）
├── references/    # 按需讀取的深度知識庫（API 字典、物理邊界、報錯對照）
├── scripts/        # 可直接執行的示範/驗證腳本
└── assets/         # 輸出產物會直接引用的靜態模板骨架（非文檔、非程式碼）
```

**2026-10-16 新增紀錄**：
- 新增 7 個跨 server/機構衝擊分析(shock)/wireline/payment 多產品線共用技能，填補 SpaceClaim 介面檢查、分類群組、中面抽取與 Mechanical 截面/接觸/邊界條件缺口：
  - SpaceClaim 側：`ansys-spaceclaim-interface-check`、`ansys-spaceclaim-classify-group`、`ansys-spaceclaim-midsurface`、`ansys-named-selection-rm-contact`（命名橋接）。
  - Mechanical 側：`ansys-mechanical-section-assign`、`ansys-mechanical-connections`、`ansys-mechanical-boundary-conditions`。
  - 素材來源：既有生產環境 ACT 腳本（孔位配對分類引擎、Joint Creation 腳本、Mechanical 干涉檢查、SpaceClaim 中面抽取工具）改寫抽象化，去除 ACT UI Properties 綁定與機敏路徑/到期日邏輯，所有 API 引用均比對 `docs/api_inventory/*.json` 查證存在性，查無者誠實標註「待 api_search 查證」。
  - `ansys-spaceclaim-modeling/SKILL.md` Router 表新增 4 列指向上述 SpaceClaim 新技能與既有 defeature/simplify-ram/simplify-heatsink，避免重複定義簡化 SOP。
  - 已通過獨立 `loop_reviewer` 稽核：frontmatter 合法性、行數 ≤150、Router 表零死連結、`.ironpy` 零非 ASCII 字元、API 真實性比對全數通過；修正 1 項阻斷缺陷（3 支 PyMechanical 驅動腳本誤宣稱相容 ACT IronPython 2.7，實際使用 `from __future__ import annotations`/`dataclasses` 等 Python 3.7+ 專屬語法，已修正 docstring 明確排除 ACT Script Editor 直接貼入情境）。

**2026-10-14 補齊紀錄**：
- 修復 `ansys-spaceclaim-modeling` 殘缺（原僅剩空 `scripts/__pycache__`，已從來源補齊 `SKILL.md` + 2 支腳本 + 6 份 `references/`）。
- 全部 24 個頂層 skill（含 `shock-analysis-workflow` 8 個子模組）新增 `assets/` 目錄：
  - 4 個具實質模板骨架：`ansys-mechanical/assets/report_section_template.md`、`shock-analysis-workflow/08-post-process-report/assets/failure_report_template.md`、`pcb-warpage-analysis/assets/apdl_rom_materials_template.mac`、`act-extension-development/assets/wbex_manifest_template.xml`。
  - 其餘 20 個 skill（純建模/查詢/排障類，無固定輸出產物需求）新增 `assets/README.md` 說明性占位文件，為各自職責客製化說明文字，非逐字複製。

---

## 統一規範
- 全案通用/非 ANSYS 技能（如去 AI 味、Git 審查、Obsidian 筆記等）保留於全域技能庫，不污染本 CAE 倉庫。
- 本倉庫保持 100% 純淨的 ANSYS 模擬、自動化與 MCP 驅動專用架構。

## 文件來源與新增領域入口

- [`ansys-mcp-foundation`](ansys-mcp-foundation/SKILL.md)：新建或修改本專案 ANSYS MCP skills、tools、workflows 時的共同入口；含按需程式碼地圖、來源查找與驗證參考。

領域來源、版本與支援狀態對照見 [`DOMAIN_SOURCE_AND_SUPPORT.md`](../../docs/skills/DOMAIN_SOURCE_AND_SUPPORT.md)。新增入口：

- [`ansys-random-vibration`](ansys-random-vibration/SKILL.md)：Mechanical PSD 隨機振動流程與統計結果判讀。
- [`ansys-thermal-analysis`](ansys-thermal-analysis/SKILL.md)：穩態/暫態熱、熱應力與熱場映射路由。
- [`ansys-sherlock`](ansys-sherlock/SKILL.md)、[`ansys-icepak`](ansys-icepak/SKILL.md)：文件/API 對照；不宣稱新 connector。
- [`ansys-optical-engineering`](ansys-optical-engineering/SKILL.md)：光學產品路由；細分 [`Speos`](ansys-speos/SKILL.md)、[`Zemax`](ansys-zemax/SKILL.md)、[`Lumerical`](ansys-lumerical/SKILL.md)。
