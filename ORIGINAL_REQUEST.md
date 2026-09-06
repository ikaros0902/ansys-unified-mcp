# Original User Request

## 2026-09-05T13:44:11Z

以 PyAnsys 官方範例數據庫（ansys/example-data）與核心工作流（ansys/pyansys）為工程基準，全面優化、更新既有技能（Mechanical、LS-DYNA、optiSLang、SpaceClaim/Geometry），並正式新增「ansys-fluent」流體分析完整技能，落實林明志標準架構（主控 < 200 行 + reference/ 子手冊 + scripts/ 端到端可執行腳本 + 判斷力/自愈庫），並完成雙向同步與地端模型考評驗證。

Working directory: F:\Ming_python\ansys-unified-mcp\SKILLs 及 C:\Users\Ming\.gemini\config\skills
Integrity mode: development

## 參考資料與數據庫來源
- 官方範例數據庫：https://github.com/ansys/example-data（包含 mixing_elbow.pmdb、Taylor_Bar.agdb、manifold_solution、ten_bar_truss.opf、pydyna 關鍵字卡等）
- 官方生態與工作流：https://github.com/ansys/pyansys（涵蓋 PyFluent、PyMechanical、PyDYNA、PyOptiSLang、PyGeometry 與 DPF）

## Requirements

### R1. 新增「ansys-fluent」流體分析完整技能體系
以官方經典 mixing_elbow（混合彎管 T-Junction）及 exhaust_system（排氣歧管）為基準：
- 建置 ansys-fluent/SKILL.md（總行數 <= 200 行，定義水密幾何工作流 WGW、求解器初始化與監控、後處理 SOP 及 Don'ts）。
- 建置 6 本專精子手冊：watertight_meshing.md（Poly-Hexcore 體網格）、physics_models.md（SST k-omega 湍流、熱傳模型）、boundary_conditions.md、solver_settings.md、fluent_judgment.md（y+ 網格邊界層評估、殘差震盪排查、逆向回流警告）、fluent_diagnostics.md（發散自愈 SOP）。
- 在 scripts/ 提供完整端到端腳本：run_mixing_elbow_e2e.py（載入 example-data、幾何、網格、求解到導出溫度雲圖）。

### R2. 汲取官方範例強化現有四大產品線技能與腳本
- Mechanical：引入泰勒柱衝擊（Taylor_Bar.agdb）與葉片熱/CFD壓力映射（pymapdl/cfx_mapping），增補 scripts/run_taylor_bar_demo.py 與熱-結構負載映射指引。
- LS-DYNA：依據 pydyna/ball_plate 與 drop_test 官方卡片，充實 reference/material_cards.md（*MAT_024 應變率硬化曲線）與 scripts/run_drop_test_demo.py 的精確關鍵字結構。
- optiSLang：引入 ten_bar_truss 拓撲尋優範例，完善 reference/mop_metamodel.md 與多目標 Pareto 尋優實作腳本。
- SpaceClaim / Geometry：結合 mixing_elbow.pmdb 與排氣歧管特徵，深化外流域抽取（Enclosure）與水密性檢查腳本 scripts/create_enclosure_demo.py。

### R3. 嚴格遵循林明志標準架構與雙軌註解規範
- 所有產品線之 SKILL.md 嚴格控制在 200 行以內。
- 知識深度分流至 reference/*.md（每本約 100~200 行）。
- 所有文檔說明、思考過程與代碼註解一律採用專業繁體中文（ANSYS ACT 原生巨集保持全英文雙軌制）。
- 所有新產生的技能與手冊必須 100% 雙向同步至 C:\Users\Ming\.gemini\config\skills\ 與 F:\Ming_python\ansys-unified-mcp\SKILLs\。

### R4. 自動化量化考評與地端驗證
- 編寫/擴充自動化驗證測試套件 scratch/verify_all_skills_llamacpp.py（涵蓋 Mechanical、LS-DYNA、optiSLang、SpaceClaim 及新加入的 Fluent 共 5 大模組）。
- 執行所有 Python 示範腳本之 python -m py_compile 語法檢驗（Exit Code 0）。
- 透過本地語言模型（llama.cpp / Ollama）執行 5 大領域閱讀理解、SOP 步驟與 Don'ts 禁忌防禦測驗，平均得分須達合格門檻。

## Acceptance Criteria

### 架構與檔案完整性
- [ ] ansys-fluent 技能成功建立，包含 SKILL.md（<= 200 行）、6 本 reference/*.md 及 scripts/run_mixing_elbow_e2e.py。
- [ ] 四大既有技能（Mechanical、LS-DYNA、optiSLang、Geometry）均吸收官方範例數據集完成擴充更新。
- [ ] 全域目錄與專案目錄共 10 處對應技能資料夾經 SHA-256 / 結構檢驗 100% 同步。

### 程式碼與語法正確性
- [ ] 所有新增及修改之 Python 腳本（scripts/*.py）通過 python -m py_compile，語法錯誤為 0。
- [ ] 所有 SKILL.md frontmatter 與路由表連結正確無死鏈。

### 地端模型閱讀理解考評
- [ ] 自動化考評腳本涵蓋五大模組（含 Fluent 考題：y+ 判定、Watertight 流程與逆流處置）。
- [ ] 本地模型（llama.cpp）五科考評全數通過，平均成績 >= 90 分。

## 2026-09-06T00:43:44Z

以林明志專家教學的系統級架構為標竿，徹底打破單純的「Skill 提示詞補丁」思維，針對使用者涵蓋 Workbench、Structural (Static/Transient)、LS-DYNA、Vibration (Modal/Harmonic/Random/Spectrum)、optiSLang、SpaceClaim/Discovery、LS-Run/LS-Prepost、Icepak 等全產品線與六大核心分析工況（衝擊、落摔、隨機振動、熱翹曲、零件分析、代理模型），實施 ANSYS MCP 2.0 全域架構重塑。全面建立「非同步求解沙盒、實時物理守護、Workbench 原生拓撲直通、前置安全閘門與自包含互動式 HTML 報告閉環」。

Working directory: F:\Ming_python\ansys-unified-mcp
Integrity mode: development

## 參考資料與架構對齊基準
- 參考標竿：https://github.com/linmingchih/Training-Material（打造 AI 模擬助理三層式架構、Job 目錄隔離、Pre-flight 檢驗、overview.html 報告生成）
- 現有代碼庫：F:\Ming_python\ansys-unified-mcp（具備 Drivers、Controllers、Skills 基礎）

## Requirements

### R1. 模擬作業生命週期與沙盒目錄隔離 (Job Sandbox & Artifact Lifecycle)
- 獨立沙盒結構：在 F:\Ming_python\ansys-unified-mcp\jobs\ 下，每次模擬執行均自動建立獨立命名空間 jobs/{timestamp}_{analysis_type}_{tag}/。
- 原始資產絕對唯讀：原始 CAD 模型（PMDB/STEP/SCDOC）、材料庫 XML、基礎模板保持唯讀，任何運算產生物（網格、日誌、rst、d3plot）僅能寫入沙盒內部。
- 標準交付物矩陣：作業完成後，沙盒內部必須自動生成三位一體之標準成果：
  1. summary.json：機器可讀之關鍵純量指標（最大應力、安全係數、最大翹曲位移、一階頻率、沙漏能比率、PASS/FAIL 判定）。
  2. 高解析度白底雲圖 PNG（等效應力、總變形、溫度分佈）。
  3. overview.html：免伺服器、單一檔案自包含之互動式 HTML 儀表板。

### R2. 非同步作業排程與實時物理守護 (Async Solver Sentinel & Real-time Watchdog)
- 非同步非阻塞介面：新增系統級 MCP 工具：
  - submit_simulation_job(workflow_type, config)：立即返回 job_id 與沙盒路徑，絕不發生客戶端超時。
  - get_simulation_status(job_id)：查詢作業狀態（QUEUED, RUNNING, SOLVED, FAILED, ABORTED）。
  - tail_simulation_log(job_id, lines)：串流獲取即時日誌。
  - abort_simulation_job(job_id)：優雅終止求解器進程。
- 實時物理健康監控 (Watchdog Daemon)：
  - 後台守護線程串流解析求解日誌（.solve.out、glstat、matter.out、fluent.log）。
  - 即時換算進度百分比（%）、當前時間步與收斂殘差。
  - 早期發散熔斷：當偵測到沙漏能比例 > 5%、質量縮放失控、或殘差出現 NaN/Inf 發散徵兆時，主動發送中斷訊號中止求解，節省算力。

### R3. Workbench 原生拓撲直通與高階工況工作流 (Workbench Schematic Cell Link & Intent Workflows)
- 頂層高階情境工作流 (Intent Workflows)：
  - run_drop_test：手機/電子產品落摔衝擊端到端工作流（整合 LS-DYNA / LS-Run / LS-Prepost）。
  - run_shock_analysis：半正弦/梯形波衝擊響應分析（含反應譜 Response Spectrum 模態疊加）。
  - run_random_vibration：模態提取 -> 模態質量檢查 -> PSD 功率譜密度隨機振動分析。
  - run_thermal_warpage：Icepak/Thermal 散熱場 -> 熱應力與材料 CTE 映射 -> PCB/封裝翹曲分析。
  - train_surrogate_model：參數化採樣 -> FEA 自動求解 -> optiSLang MOP 代理模型建置。
- Workbench 原生單元鏈結引擎 (Schematic Cell Link Engine)：
  - 放棄易碎的外部 CSV/文字中繼，全面透過 RunWB2 Journal 調用原生跨系統單元鏈結（Cell Transfer Links）：
    1. 熱-結構翹曲：Steady-State/Transient Thermal 或 Icepak 之 Solution 單元 -> Static/Transient Structural 之 Setup 單元（自動建立無損溫度場載荷傳遞）。
    2. 振動與反應譜：Modal 之 Solution 單元 -> Harmonic Response / Random Vibration / Response Spectrum 之 Setup 單元（自動綁定預應力環境與特徵振型）。
    3. 參數化尋優：Parameters Set 直通 optiSLang 原生工作流節點。
- 底層統一求解器驅動抽象 (BaseSolverDriver)：
  - 統一封裝 MechanicalDriver、LSDynaDriver、OptislangDriver、SpaceClaimDriver、IcepakDriver。

### R4. 求解前置安全閘門與自愈處方箋 (Pre-Flight Physical Gatekeeper & Prescription)
- 硬性物理阻斷檢核：調用求解器前強制進行物理指標核驗，未達標嚴禁送算：
  - 隨機振動 / 反應譜：三向有效模態質量佔比必須 >= 90%，截斷頻率必須大於激振頻率 1.5x。
  - 落摔 / 衝擊：檢查初速度向量指向剛性地面、單元特徵尺寸時間步估計 delta t、剛體接觸定義完整性。
  - 熱翹曲：檢查溫度相依 CTE 割線熱膨脹係數、零應力參考溫度 T_ref 賦予完整性。
  - 單位制嚴格防護：強制檢查長度-質量-時間單位系統一致性（防止 MPa 與 kg/m^3 混用造成 10^6 級別加速度與應力暴衝）。
- 結構化自愈處方箋 (Prescription)：阻斷時回傳標準 JSON 錯誤碼與精確修復引導。

### R5. 自包含互動式 HTML 儀表板 (overview.html) 與報告合成器
- 單一免伺服器 HTML 報告 (overview.html)：
  - 關鍵指標卡 (KPI Metric Cards)：最大等效應力、安全係數、最大翹曲位移、一階頻率、沙漏能比率，直接標記 PASS/FAIL。
  - 互動式圖表：嵌入免聯網之輕量 SVG/Canvas 渲染曲線（PSD 頻響圖、落摔衝擊加速度歷程、optiSLang MOP 響應面雲圖）。
  - 白底高清雲圖相簿：直觀呈現應力與變形雲圖。
  - 對話引用摘要：自動產生 Markdown 摘要片段供 AI 直接於對話中回覆使用者。

## Acceptance Criteria

### 架構與核心模組實裝
- [ ] src/ansys_unified_mcp/jobs/ 目錄下建立完整 JobManager 沙盒管理器，每次執行產生獨立 jobs/{timestamp}_{type}/。
- [ ] src/ansys_unified_mcp/core/sentinel/ 實裝非同步長任務守護進程與實時日誌解析器（支援進度換算與早期發散中斷）。
- [ ] src/ansys_unified_mcp/gatekeeper/ 實裝 Pre-Flight 安全閘門，涵蓋振動有效質量 >= 90%、落摔接觸/時間步、熱翹曲 CTE/T_ref 與單位制校驗。
- [ ] src/ansys_unified_mcp/workflows/workbench_links.py 實裝 Workbench 原生 Cell Link 生成器（熱-結構、模態-振動/反應譜、參數-optiSLang）。
- [ ] src/ansys_unified_mcp/reporting/ 實裝報告合成器，能自動產出 overview.html、summary.json 與 Markdown 摘要。

### 高階工況工作流與驅動層
- [ ] 實裝 5 大高階情境工作流工具：run_drop_test、run_shock_analysis、run_random_vibration、run_thermal_warpage、train_surrogate_model。
- [ ] BaseSolverDriver 抽象基類及其衍生類（MechanicalDriver, LSDynaDriver, OptislangDriver, IcepakDriver）通過單元測試。

### 自動化測試與端到端驗證
- [ ] 單元測試套件（tests/）全數通過（涵蓋 Job 沙盒隔離、Pre-flight 閘門阻斷與自愈處方、非同步 Watchdog 監控）。
- [ ] 全套代碼通過 python -m py_compile 與 flake8/ruff 代碼品質檢查（0 語法錯誤）。
- [ ] 模擬端到端執行測試（包含隨機振動模態質量不足阻斷案例、落摔沙漏超標早期中斷案例、熱翹曲 cell link 成功案例），產出合規之 overview.html 與 summary.json。

