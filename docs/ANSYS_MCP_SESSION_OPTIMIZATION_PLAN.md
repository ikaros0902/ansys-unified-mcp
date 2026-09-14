# 其他 Session 完整盤點與全流程標準化優化實施計畫

本計畫針對 `ansys-unified-mcp` 專案中衝擊分析工作流（Session 01 ~ 08）、PCB 熱翹曲管線、驅動層與全域工具之「未優化內容」、「殘留硬編碼路徑」與「測試斷鏈」進行全面盤點與根因分析，並提出完整的分階段優化方案。

---

## 需使用者審查與確認事項 (User Review Required)

> [!IMPORTANT]
> **關鍵修復與架構升級決策**：
> 1. **全衝擊管線升級 (Session 01 ~ 08 全閉環)**：
>    目前 `execute_full_shock_act_pipeline.py` 明確僅執行至 Session 06，缺少 Session 07（求解調度與能量監控）及 Session 08（後處理與量化失效判定）。我們將全面升級為端到端 01 ~ 08 完整閉環，並將輸出路徑徹底解耦為專案動態目錄。
> 2. **消除所有殘留硬編碼 (跨平台與跨機遷移相容性)**：
>    全面移除散落在 `SKILLs/`、`src/`、`workbench_plugin/`、`examples/`、`scripts/` 與 `tests/` 中的 `d:\Ikaros`、`D:\ANSYS_MCP_Connect`、`F:\Ming_python` 等寫死路徑，改採 `Path(__file__).resolve()` 與 `sys.executable`。

---

## 現況盤點與缺陷診斷報告 (Diagnostic Audit)

### 1. 衝擊分析管線（`SKILLs/shock-analysis-workflow/`）嚴重缺漏
- **Session 05 (`05-section-assignment`)**：缺少 `reference/` 技術細節手冊（未有薄板 ELFORM=16 與厚度積分點 NIP=5 之物理背景手冊）。`SKILL.md` 中第 84 行含有寫死路徑 `python d:/Ikaros/ANSYS-unified-MCP/...`。
- **Session 06 (`06-constraint-load`)**：缺少 `reference/` 技術手冊，且**缺少獨立驗證腳本 `scripts/test_session_06.py`**。
- **Session 07 (`07-solve-monitor`)**：`SKILL.md` 僅有 24 行極為簡陋；缺少 `reference/` 技術手冊（未有 LS-DYNA `glstat` 能量守恆比 $0.9 \sim 1.1$ 算法手冊）；且**缺少獨立驗證腳本 `scripts/test_session_07.py`**。
- **Session 08 (`08-post-process-report`)**：`SKILL.md` 僅 31 行；缺少 `reference/` 技術手冊（未有金屬 EPS 0.01 貫穿單元、BGA 焊點 EPS 0.0022、塑料降伏強度等判定細則）；且**缺少獨立驗證腳本 `scripts/test_session_08.py`**。
- **Session 01 ~ 04**：各 Session 的 `SKILL.md` 內均寫死 `python d:/Ikaros/ANSYS-unified-MCP/...` 測試指令，換機或不同磁碟槽即報錯。

### 2. 端到端批次腳本鏈條斷裂與路徑硬編碼
- `examples/shock_analysis/execute_full_shock_act_pipeline.py`：
  - 代碼第 27 行與 335 行標記為 `SESSION 01 TO 06`，**直接遺漏了 Session 07 與 Session 08**。
  - 第 323 行寫死 `out_dir = r"d:\Ikaros\ACT_Test\Shock_35G_KFiles"`。
- `examples/shock_analysis/run_shock_35g_pipeline.py`：
  - 第 221 行寫死 `out_dir = r"d:\Ikaros\ACT_Test\Shock_35G_KFiles"`。

### 3. 全專案其他模組之硬編碼路徑盤點
- **驅動層 (`src/ansys_unified_mcp/drivers/`)**：
  - `icepak_driver.py` (L111): 寫死 `r"F:\Ming_python\ansys-unified-mcp\.venv\Scripts\python.exe"`。
  - `optislang_driver.py` (L114): 寫死 `r"F:\Ming_python\ansys-unified-mcp\.venv\Scripts\python.exe"`。
  - `spaceclaim_driver.py` (L120): 寫死 `r"F:\Ming_python\ansys-unified-mcp\.venv\Scripts\python.exe"`。
- **PCB 熱翹曲管線 (`SKILLs/pcb-warpage-analysis/scripts/`)**：
  - `01_build_pcb_geometry.py` (L207): 寫死 `r"D:\ANSYS_MCP_Connect\PCB_Stackup_material\MCP_Test.xlsx"`。
  - `02_calculate_rom_materials.py` (L144): 寫死 `folder = r'D:\ANSYS_MCP_Connect\PCB_Stackup_material'`。
  - `run_full_warpage_workflow.py` (L17, 51): 寫死 `folder = r"D:\ANSYS_MCP_Connect\PCB_Stackup_material"`。
- **Workbench 外掛監聽 (`workbench_plugin/`)**：
  - `wb_event_listener.py` (L40) 與 `main.py` (L46): 寫死 `fallback = r"D:\Ikaros\ANSYS-unified-MCP\workbench_queue"`。
- **合規檢查與測試腳本**：
  - `scripts/audit_architecture_compliance.py` (L27-28): 寫死 `F:\Ming_python` 與 `C:\Users\Ming`。
  - `tests/test_remediation_m5.py` (L16-19, L126): 寫死 `F:\Ming_python`。

---

## 預定變更內容 (Proposed Changes)

### 第一階段：補齊 Session 05 ~ 08 參考文檔、規格擴充與小批次獨立驗證腳本

#### [NEW] [section_controls_and_shell_thickness.md](file:///F:/Ming_python/ansys-unified-mcp/SKILLs/shock-analysis-workflow/05-section-assignment/reference/section_controls_and_shell_thickness.md)
- 撰寫薄板中面抽取後的厚度指派技術手冊、LS-DYNA `*SECTION_SHELL` 完全積分公式 (ELFORM=16, NIP=5) 與實體單元 (ELFORM=10/1) 之控制原理。

#### [NEW] [shock_pulse_and_boundary_conditions.md](file:///F:/Ming_python/ansys-unified-mcp/SKILLs/shock-analysis-workflow/06-constraint-load/reference/shock_pulse_and_boundary_conditions.md)
- 撰寫 6 向半正弦脈衝加速度轉速度積分曲線、`*BOUNDARY_PRESCRIBED_MOTION_RIGID` 與數值阻尼 `*DAMPING_GLOBAL` 設置手冊。

#### [NEW] [test_session_06.py](file:///F:/Ming_python/ansys-unified-mcp/SKILLs/shock-analysis-workflow/scripts/test_session_06.py)
- 撰寫 Session 06 獨立驗證腳本：連線至 Port 10000，檢驗 6 個方向的衝擊速度歷史曲線、時間步長安全係數 (TSSFAC=0.9)、IHQ=6 沙漏設定與求解精確度 Double Precision。

#### [MODIFY] [SKILL.md (Session 07)](file:///F:/Ming_python/ansys-unified-mcp/SKILLs/shock-analysis-workflow/07-solve-monitor/SKILL.md)
- 將 24 行極簡手冊重構擴充至 120+ 行標準規範，納入求解器監控狀態機、`glstat` 即時解析與異常阻斷機制。

#### [NEW] [energy_balance_tracking.md](file:///F:/Ming_python/ansys-unified-mcp/SKILLs/shock-analysis-workflow/07-solve-monitor/reference/energy_balance_tracking.md)
- 撰寫 LS-DYNA 能量平衡比追蹤手冊，詳細說明 Total Energy / (Initial Energy + External Work) 比值在 0.9 ~ 1.1 區間的判定算法與沙漏能佔比超標處理。

#### [NEW] [test_session_07.py](file:///F:/Ming_python/ansys-unified-mcp/SKILLs/shock-analysis-workflow/scripts/test_session_07.py)
- 撰寫 Session 07 獨立驗證腳本：驗證求解器呼叫管線、`glstat` 數值模擬解析器以及能量比異常中斷邏輯。

#### [MODIFY] [SKILL.md (Session 08)](file:///F:/Ming_python/ansys-unified-mcp/SKILLs/shock-analysis-workflow/08-post-process-report/SKILL.md)
- 擴充 Session 08 規格：定義完整的金屬、塑料、BGA 焊點失效指標評估演算法、自動多視角截圖與 Office 自動化報告輸出規範。

#### [NEW] [failure_criteria_and_strain_limits.md](file:///F:/Ming_python/ansys-unified-mcp/SKILLs/shock-analysis-workflow/08-post-process-report/reference/failure_criteria_and_strain_limits.md)
- 撰寫後處理失效判定準則技術手冊：包含金屬 EPS 0.01 貫穿、BGA 焊點 EPS 0.0022、塑膠降伏強度判定標準。

#### [NEW] [test_session_08.py](file:///F:/Ming_python/ansys-unified-mcp/SKILLs/shock-analysis-workflow/scripts/test_session_08.py)
- 撰寫 Session 08 獨立驗證腳本：驗證應變場提取、量化矩陣判定（PASS / MARGINAL / FAIL）與自動生成結構完整性報告流程。

---

### 第二階段：重構衝擊全流程腳本為 Session 01 ~ 08 完整閉環

#### [MODIFY] [execute_full_shock_act_pipeline.py](file:///F:/Ming_python/ansys-unified-mcp/examples/shock_analysis/execute_full_shock_act_pipeline.py)
- 將原本僅執行至 Session 06 的流程擴充為完整的 Session 01 ~ 08 閉環：
  - 整合 Session 07：求解調度、LS-DYNA 關鍵字導出與能量監控。
  - 整合 Session 08：後處理應變提取與失效指標 PASS/FAIL 評估。
- 移除 `d:\Ikaros\ACT_Test\Shock_35G_KFiles` 硬編碼，改採相對於專案目錄的動態路徑。

#### [MODIFY] [run_shock_35g_pipeline.py](file:///F:/Ming_python/ansys-unified-mcp/examples/shock_analysis/run_shock_35g_pipeline.py)
- 移除 `d:\Ikaros\ACT_Test\Shock_35G_KFiles` 硬編碼，改採相對於專案目錄的動態路徑。

---

### 第三階段：全庫殘留硬編碼徹底清除與路徑解耦

#### [MODIFY] [Session 01 ~ 05 SKILL.md](file:///F:/Ming_python/ansys-unified-mcp/SKILLs/shock-analysis-workflow/)
- 修正各 Session `SKILL.md` 中的執行命令，移除 `d:/Ikaros/ANSYS-unified-MCP`，改為使用標準相對路徑。

#### [MODIFY] [pcb-warpage-analysis scripts](file:///F:/Ming_python/ansys-unified-mcp/SKILLs/pcb-warpage-analysis/scripts/)
- `01_build_pcb_geometry.py`、`02_calculate_rom_materials.py`、`run_full_warpage_workflow.py`：移除 `D:\ANSYS_MCP_Connect` 寫死路徑，改為預設相對於腳本同層之範例目錄或支援命令列引數傳入。

#### [MODIFY] [drivers](file:///F:/Ming_python/ansys-unified-mcp/src/ansys_unified_mcp/drivers/)
- `icepak_driver.py`、`optislang_driver.py`、`spaceclaim_driver.py`：移除寫死的 `F:\Ming_python\...` Python 執行檔路徑，改為使用 `sys.executable`。

#### [MODIFY] [workbench_plugin](file:///F:/Ming_python/ansys-unified-mcp/workbench_plugin/)
- `wb_event_listener.py`、`main.py`：移除寫死 `D:\Ikaros`，改為使用環境變數或專案動態目錄 fallback。

#### [MODIFY] [audit_architecture_compliance.py](file:///F:/Ming_python/ansys-unified-mcp/scripts/audit_architecture_compliance.py) & [test_remediation_m5.py](file:///F:/Ming_python/ansys-unified-mcp/tests/test_remediation_m5.py)
- 移除寫死的絕對路徑，改採 `Path(__file__).resolve()` 動態取得專案根目錄與使用者目錄。

---

### 第四階段：驗證、全域技能鏡像同步與 Git 提交

1. **小批次與單元測試驗證**：
   - 執行 `scripts/test_session_06.py`、`test_session_07.py`、`test_session_08.py` 驗證其語法與獨立斷言。
   - 執行全庫 `pytest tests/` 確保核心功能 100% 通過。
2. **雙向鏡像同步**：
   - 執行 `python scripts/sync_skills_bidirectional.py`，將最新優化的技能雙向鏡像至全域 `~/.gemini/config/skills`。
3. **Git 版本控制**：
   - 提交並推播至 GitHub 遠端倉庫。

---

## 驗證計畫 (Verification Plan)

### 自動化測試 (Automated Tests)
- 執行 Session 01 ~ 08 所有驗證腳本：
  ```powershell
  python SKILLs/shock-analysis-workflow/scripts/test_session_01.py
  python SKILLs/shock-analysis-workflow/scripts/test_session_02.py
  python SKILLs/shock-analysis-workflow/scripts/test_session_03.py
  python SKILLs/shock-analysis-workflow/scripts/test_session_04.py
  python SKILLs/shock-analysis-workflow/scripts/test_session_05.py
  python SKILLs/shock-analysis-workflow/scripts/test_session_06.py
  python SKILLs/shock-analysis-workflow/scripts/test_session_07.py
  python SKILLs/shock-analysis-workflow/scripts/test_session_08.py
  ```
- 執行專案全體測試套件：
  ```powershell
  .venv\Scripts\python.exe -m pytest tests/
  ```
- 執行架構合規性檢查：
  ```powershell
  .venv\Scripts\python.exe scripts/audit_architecture_compliance.py
  ```
- 執行雙向同步：
  ```powershell
  .venv\Scripts\python.exe scripts/sync_skills_bidirectional.py
  ```

### 人工查核 (Manual Verification)
- 檢視 `git diff`，確認全專案所有檔案再無殘留硬編碼磁碟槽與特定使用者路徑。
- 檢核 `examples/shock_analysis/execute_full_shock_act_pipeline.py` 已包含完整的 Session 01 到 Session 08 呼叫邏輯。
