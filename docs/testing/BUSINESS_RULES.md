# ANSYS Unified MCP 業務與物理規則規格書 (BUSINESS_RULES.md)

本文件依據 CAE 代碼現代化（`cae-code-modernization`）與行為驅動開發（BDD）標準，定義系統的核心業務規則、物理邊界、檢索等價性要求與程式碼生成防呆約束。

---

## 模組與物理邊界規則 (Physical & Behavioral Rules)

### Rule P01: 結構靜力與邊界條件 (Structural Mechanics & Boundary Conditions)
- **Given**: 使用者要求對結構模型施加固定約束、遠端力或重力載荷。
- **When**: 透過 MCP 生成 Mechanical ACT (IronPython) 或 PyMechanical (CPython) 腳本。
- **Then**:
  - 內嵌 ACT 腳本內部註解必須為純 ASCII 英文。
  - 固定約束必須透過合法入口 `ExtAPI.DataModel.Project.Model.Analyses[0].AddFixedSupport()` 或相應 scoping 方法建立。
  - 邊界條件必須包含有效 Scoping（幾何面/邊/點或 Named Selection），嚴禁無效空選擇。

### Rule P02: 暫態衝擊與跌落分析 (Shock & Drop Test Simulation)
- **Given**: 模型材料為鋁合金或結構鋼，需承受 50G 半正弦波（11ms）衝擊或跌落分析。
- **When**: 透過 LS-DYNA Keyword、PyDYNA 或 Mechanical 執行分析。
- **Then**:
  - 材料模型應優先使用 `*MAT_PIECEWISE_LINEAR_PLASTICITY` (`*MAT_024`) 或線彈性 `*MAT_001`。
  - 求解控制卡必須明確指定終止時間 `*CONTROL_TERMINATION` 與時間步長安全係數 `*CONTROL_TIMESTEP`（通常為 0.9）。
  - 跌落接觸必須指定 `*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE` 或 `*CONTACT_AUTOMATIC_SINGLE_SURFACE`。

### Rule P03: CFD 流場與傳熱分析 (CFD & Thermal Boundary Rules)
- **Given**: 流體域包含入口、出口與發熱體邊界。
- **When**: 透過 PyFluent 或 Fluent Journal 設定邊界條件。
- **Then**:
  - 邊界條件類型（Velocity Inlet, Pressure Outlet, Wall with Heat Flux）必須與網格區域拓撲嚴格匹配。
  - 殘差收斂準則通常應滿足連續方程與動量方程殘差 $\le 10^{-4}$，能量方程殘差 $\le 10^{-6}$。

---

## 檢索與語料庫業務規則 (Documentation & APIKB Retrieval Rules)

### Rule D01: 檢索等價性與零退化 (Retrieval Equivalence & Zero Regression)
- **Given**: 語料庫完成瘦身（刪除冗餘備份與暫存目錄）並重建 SQLite 索引後。
- **When**: 對現行黃金測試集（Mechanical, MAPDL, Fluent, DPF, optiSLang, SpaceClaim, Sherlock 等）執行關鍵字檢索。
- **Then**:
  - 核心 API 簽名與手冊章節的 Top-5 命中結果必須與重構前基準保持 100% 語意等價。
  - `compare.py` 比對報告退出碼必須為 `0`。

### Rule D02: 程式碼語法三軌分流 (Tri-Track Code Syntax Discipline)
- **Given**: AI 代理為任一 ANSYS 模組生成自動化代碼。
- **When**: 決定目標執行宿主環境。
- **Then**:
  - **Track 1 (CPython 3.10+ / PyAnsys)**: 使用標準 `ansys.<product>.core` 套件，註解可使用繁體中文或英文。
  - **Track 2 (In-Process IronPython 2.7 / ACT / SCDM)**: 必須依賴宿主預注入之全域變數（如 `ExtAPI`, `DataModel`, `GetRootPart()`），代碼內部註解**嚴格禁用非 ASCII 字元**（防止 IronPython 解譯器編碼崩潰）。
  - **Track 3 (Solver Native Deck / APDL / TUI / Keyword)**: 使用求解器原生指令集（如 APDL `/PREP7`, `D, ALL, ALL`），嚴禁混入 Python 物件語法。

---

## 多版本與 Agent 執行防護規格 (Multi-Version & Agent Readiness Rules)

### Rule M01: 多版本 ANSYS 探測與動態切換 (Multi-Version Discovery & Dynamic Switching)
- **Given**: 宿主電腦同時安裝多個 ANSYS 版本（例如 v202, v242, v251）。
- **When**: 呼叫 `ans_list_installed_versions()` 或 `ans_set_active_version(version)`。
- **Then**:
  - 系統必須列出本機所有合法版本，且 `total_installed >= 1`（若有安裝）。
  - 切換版本時，全域 `config` 必須動態刷新路徑，`AWP_ROOT<ver>` 與 `ANSYS_VERSION` 必須與目標版本一致，無須重啟 MCP 進程。

### Rule M02: ASD-STE100 提示詞合規與診斷常駐 (ASD-STE100 & Resident Diagnostics)
- **Given**: FastMCP 伺服器啟動或套用任何 Profile（`all`, `core`, `mechanical` 等）。
- **When**: 檢查 `shared.INSTRUCTIONS` 與工具列表。
- **Then**:
  - `INSTRUCTIONS` 內部必須符合 ASD-STE100 規範：無分號、單句長度 $\le 20$ 字、主動語態。
  - 核心診斷工具（`check_ansys_installation`, `ans_list_installed_versions`, `ans_set_active_version`）必須恆可見且回傳正規扁平信封 `{"ok": True, ...}`。

### Rule M03: 雙軌求解器與基準引擎透明性 (Dual-Track Transparency Discipline)
- **Given**: 呼叫未安裝或無商業授權之多物理領域工具（如 HFSS, Maxwell, Rocky, Chemkin）。
- **When**: 觸發 Track 2 數值基準引擎（Benchmark Numerical Engine）。
- **Then**:
  - 回傳信封之 `execution_mode` 必須明確標註為 `benchmark_fallback`。
  - AI 代理嚴禁將解析基準近似解宣稱為商業 ANSYS 求解器計算結果。

---

## 防呆與金絲雀破壞性驗證 (Canary Failure Guardrails)

### Rule C01: 金絲雀破壞檢驗防線 (Canary Test Enforcement)
- **Given**: 檢索系統或 CAE 腳本測試全部亮綠燈。
- **When**: 刻意在代碼中注入致命破壞（例如顛倒載荷方向、破壞 APIKB 權重、或使材料模量設為 0）。
- **Then**:
  - 測試套件與 `compare.py` **必須明確失敗（Fail）並返回 Exit Code 1**。
  - 若測試依然亮綠燈，判定該測試為無效假測試（Bogus Test），嚴禁發布上線。
