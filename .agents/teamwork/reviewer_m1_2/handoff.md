# Handoff Report — Milestone 1 全域依賴與回歸審查 (Reviewer & Adversarial Critic)

- **Agent**: `reviewer_m1_2` (teamwork_preview_reviewer)
- **Handoff Type**: Hard (審查與對抗性驗收完成)
- **Recipient**: `b64f9ba5-0d28-4ac0-a95d-862e7b398eaf` (parent)
- **Target Task**: Milestone 1 (R1 消除代碼重複與技術債) 全域審查
- **Verdict (判定結論)**: `REQUEST_CHANGES` (要求修正)

---

## 審查總結 (Review & Challenge Summary)

針對 `worker_m1` 提交之 Milestone 1 成果，經過全域檔案掃描、單元測試重現、全庫回歸檢驗以及深層對抗性壓力測試：
1. **誠信檢查 (Integrity Audit)**：`PASS`（未發現硬編碼測試結果、偽造日誌或虛假實作；其實作之檔案刪除與 16 處引用轉換確實已執行，且其所陳述之各項指令輸出與實際相符）。
2. **審查結論**：`REQUEST_CHANGES`。雖然 `tests/unit/`（257 項測試）全部通過，但經獨立審查發現**兩項嚴重缺陷 (Critical Findings)** 與 **兩項重要架構隱患 (Major Findings)**：
   - **Critical 1**：向後相容層 `products/mechanical/__init__.py` 存取 `MechanicalDriver` 時存在致命的**循環相依匯入崩潰**（在乾淨程序執行 `from ansys_unified_mcp.products.mechanical import *` 會直接拋出 `ImportError` 崩潰）。
   - **Critical 2**：`tests/adversarial/test_chapter2_adversarial_verification.py` 中仍殘留對舊版 `products/mechanical.py` 實體檔案存在的斷言，導致全專案測試未達成 ORIGINAL_REQUEST.md 所規範的「全專案 pytest 100% 通過」。
   - **Major 3**：`facade.py` 的 `run_script` 使用 `os.getpid()` 命名臨時輸出檔，在同一進程的多執行緒併發環境下產生資料踩踏與輸出錯亂。
   - **Major 4**：`facade.py` 的 `connect()` 在復用 Session 時僅依據 registry 是否存在 key，盲目復用可能已斷開的死亡 Session，未執行活性探針。

---

## 1. Observation (觀察事實)

### 1.1 實體檔案與引用掃描觀察
- **檔案物理刪除驗證**：
  - 執行指令：`Test-Path "src/ansys_unified_mcp/products/mechanical.py"`
  - 輸出：`False`（檔案確實已從硬碟移除）。
- **16 處核心引用遷移驗證**：
  - 工具層：`src/ansys_unified_mcp/tools/mechanical_workflow_tools.py:15` 已指向 `.facade import controller, _esc`。
  - 測試層：`test_mechanical_controller.py:22`、`test_final_stress_harness.py:23`、`test_m1_envelope_stress_challenge.py:27`、`test_m1_alias_challenge.py:20` 皆已更新指向 `.facade`。
  - 範例與技能腳本：`examples/shock_analysis/` 3 個檔案與 `skills/shock-analysis-workflow/scripts/` 8 個檔案皆已更新為指向 `.facade import MechanicalController`。
- **遺漏更新之測試與註解**：
  - `tests/adversarial/test_chapter2_adversarial_verification.py:86-88`：
    ```python
    mech_prod = src_root / "ansys_unified_mcp" / "products" / "mechanical.py"
    mech_wf = src_root / "ansys_unified_mcp" / "tools" / "mechanical_workflow_tools.py"
    assert mech_prod.exists() and mech_wf.exists()
    ```
    此處直接依賴舊檔實體存在，執行測試直接拋出 `AssertionError: assert False where False = WindowsPath('.../products/mechanical.py').exists`。
  - 部分註解與文件提及舊檔案：如 `test_sentinel_watchdog.py:59`、`sim_impl.py:347`、`test_sessions.py:3`。

### 1.2 測試回歸執行觀察
- **單元測試套件執行**：
  - 執行指令：`.venv\Scripts\pytest.exe tests/unit/`
  - 輸出結果：`257 passed, 2 skipped in 8.86s`（Exit code: 0）。
- **Mechanical 專案核心測試**：
  - 執行指令：`.venv\Scripts\pytest.exe tests/test_mechanical_controller.py tests/adversarial/test_m1_alias_challenge.py tests/adversarial/test_final_stress_harness.py tests/adversarial/test_m1_envelope_stress_challenge.py`
  - 輸出結果：`54 passed, 5 xfailed, 1 xpassed in 3.35s`（Exit code: 0）。
- **全庫測試與對抗性驗證執行**：
  - 執行指令：`.venv\Scripts\pytest.exe tests/`
  - 輸出結果：`2 failed, 451 passed, 2 skipped, 5 xfailed, 1 xpassed in 27.11s`（Exit code: 1）。
  - 失敗 1：`tests/adversarial/test_chapter2_adversarial_verification.py::TestChapter2CodebaseFacts::test_extapi_act_string_concatenation`（由於 `products/mechanical.py` 被刪除而斷言失敗）。
  - 失敗 2：`tests/adversarial/test_chapter2_adversarial_verification.py::TestChapter2CodebaseFacts::test_tool_count_136_ast_verification`（歷史架構重構遺留之工具計數變更）。

### 1.3 向後相容層循環相依實測
- **對抗性測試指令**：
  ```powershell
  $env:PYTHONPATH="src"; .venv\Scripts\python.exe -c "from ansys_unified_mcp.products.mechanical import *"
  ```
- **完整報錯追蹤 (Traceback)**：
  ```text
  Traceback (most recent call last):
    File "<string>", line 1, in <module>
      from ansys_unified_mcp.products.mechanical import *
    File "F:\Ming_python\ansys-unified-mcp\src\ansys_unified_mcp\products\mechanical\__init__.py", line 21, in __getattr__
      from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver
    File "F:\Ming_python\ansys-unified-mcp\src\ansys_unified_mcp\products\mechanical\driver.py", line 20, in <module>
      from ansys_unified_mcp.drivers.base import BaseSolverDriver, SolverDriverError
    File "F:\Ming_python\ansys-unified-mcp\src\ansys_unified_mcp\drivers\__init__.py", line 22, in <module>
      from ansys_unified_mcp.drivers.mechanical_driver import MechanicalDriver
    File "F:\Ming_python\ansys-unified-mcp\src\ansys_unified_mcp\drivers\mechanical_driver.py", line 3, in <module>
      from ansys_unified_mcp.products.mechanical import driver as _driver
  ImportError: cannot import name 'MechanicalDriver' from 'ansys_unified_mcp.drivers.mechanical_driver'
  ```
- 獨立對抗測試檔驗證：
  - 執行指令：`.venv\Scripts\pytest.exe tests/adversarial/test_m1_facade_adversarial_challenge.py`
  - 輸出結果：`1 failed, 22 passed`，失敗點即為 `test_circular_import_vulnerability_on_driver_export`。

---

## 2. Logic Chain (推導邏輯鏈)

1. **從觀察 1.1 與 1.2 推導出回歸測試破裂**：
   - `worker_m1` 雖然達成了刪除 `products/mechanical.py` 的物理目標，但 Acceptance Criteria 明確規定「執行全專案 pytest，測試 100% 通過」。
   - `worker_m1` 僅執行 `tests/unit/`，忽視了 `tests/adversarial/test_chapter2_adversarial_verification.py` 中對該舊檔存在的物理斷言。
   - 因舊檔被刪除，該測試必然亮紅燈，導致全專案整合測試中斷，故不符合全綠燈驗收條件。
2. **從觀察 1.3 推導出向後相容層的致命循環依賴 (Circular Dependency)**：
   - `src/ansys_unified_mcp/products/mechanical/__init__.py` 將 `MechanicalDriver` 納入 `__all__` 並在 `__getattr__` 動態導入 `products.mechanical.driver`。
   - 當直譯器在未載入 `drivers` 套件的狀態下載入 `products.mechanical.driver` 時，其第 20 行 `from ansys_unified_mcp.drivers.base import ...` 觸發了 `drivers/__init__.py`。
   - `drivers/__init__.py` 第 22 行導入 `drivers.mechanical_driver`。
   - `drivers/mechanical_driver.py` 第 3 行嘗試自未完成編譯的 `products.mechanical.driver` 取出屬性。由於 `driver.py` 此時尚未執行到定義 `class MechanicalDriver` 的程式碼，其 `__dict__` 中無該屬性。
   - 導致 `drivers/mechanical_driver` 宣告失敗，回拋 `ImportError`，形成致命死結。
   - 結論：向後相容層目前對 `MechanicalDriver` 的動態 re-export 完全不可用，且會破壞任何使用萬用字元 `from ... import *` 的外部模組。
3. **從對抗性實驗推導出 Facade 的潛在副作用與併發風險**：
   - `facade.py:160-161` 採用 `mech_out_{os.getpid()}.txt`，忽視了 FastMCP 伺服器在多執行緒或異步協程下同時處理多個請求的情境，相同 PID 將引發檔案相互覆蓋（Race Condition），已在 `test_m1_concurrency_reconnect_challenge.py` 中被實證捕獲。
   - `facade.py:95` 的 `connect()` 未校驗 Session 存活即盲目重用，違反穩健性原則。

---

## 3. Caveats (限制與注意事項)

1. **歷史累積債務**：`test_tool_count_136_ast_verification` 的工具總數不符（121 vs 138）是由於歷史架構切片重構所致，非 `worker_m1` 本次引入的變更。
2. **修改範圍界線**：Reviewer 嚴格遵守只讀規範（Review-only），未擅自修改 `__init__.py`、`facade.py` 或 `test_chapter2_adversarial_verification.py`，所有問題均以缺陷報告形式退回修正。

---

## 4. Conclusion (結論與行動建議)

### 判定：`REQUEST_CHANGES` (退回實作者修正)

### 必須修正項目 (Must-Fix Action Items)：

1. **修復 `MechanicalDriver` 循環匯入死結**：
   - 方案 A（推薦）：在 `ansys_unified_mcp.drivers.__init__.py` 中採用延遲導入（Lazy Import / `__getattr__`），使 `import drivers.base` 不會無條件級聯載入所有具象驅動。
   - 方案 B：在 `products/mechanical/__init__.py` 中移除或調整 `MechanicalDriver` 的匯出機制，避免在 `__getattr__` 中觸發未完成的模組字典綁定。
2. **更新對抗測試斷言**：
   - 將 `tests/adversarial/test_chapter2_adversarial_verification.py:86` 的斷言標的更新為 `src/ansys_unified_mcp/products/mechanical/facade.py`，確保全庫 pytest 能順利通過。
3. **消除臨時檔併發競爭**：
   - 在 `facade.py` 的 `run_script` 中，將 `f"mech_out_{os.getpid()}.txt"` 改為包含 UUID 或執行緒 ID 的唯一標識（例如 `f"mech_out_{os.getpid()}_{uuid.uuid4().hex[:8]}.txt"`）。
4. **增強 `connect()` 活性驗證**：
   - 在復用現有 session 前，調用 `_probe_session` 確保底層連線未中斷，若中斷則自動重新連接。

---

## 5. Verification Method (獨立驗證方式)

後續實作者修正完畢後，審查者可執行以下指令進行回歸驗證：

1. **驗證循環匯入修復 (在乾淨直譯器環境)**：
   ```powershell
   $env:PYTHONPATH="src"; .venv\Scripts\python.exe -c "from ansys_unified_mcp.products.mechanical import *; print('Import * OK')"
   $env:PYTHONPATH="src"; .venv\Scripts\python.exe -c "import ansys_unified_mcp.products.mechanical as m; print(m.MechanicalDriver)"
   $env:PYTHONPATH="src"; .venv\Scripts\python.exe -c "from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver; print('Driver OK')"
   ```
   *預期輸出*：皆順利印出 OK，無任何 `ImportError`。

2. **驗證全套單元測試回歸**：
   ```powershell
   .venv\Scripts\pytest.exe tests/unit/
   ```
   *預期輸出*：`257 passed, 2 skipped`。

3. **驗證全庫測試與對抗測試通過**：
   ```powershell
   .venv\Scripts\pytest.exe tests/adversarial/test_chapter2_adversarial_verification.py
   .venv\Scripts\pytest.exe tests/adversarial/test_m1_facade_adversarial_challenge.py
   ```
   *預期輸出*：測試 100% 通過。
