# Handoff Report — R1 Codebase Deduplication Survey

- **Agent**: `explorer_survey_1` (teamwork_preview_explorer)
- **Handoff Type**: Hard (調研完成)
- **Recipient**: `b64f9ba5-0d28-4ac0-a95d-862e7b398eaf` (parent)
- **Target Task**: R1 消除代碼重複與技術債 (Codebase Deduplication)

---

## 1. Observation (觀察事實)

1. **實體檔案二進位比對**：
   - 檔案 1：`F:\Ming_python\ansys-unified-mcp\src\ansys_unified_mcp\products\mechanical.py` (229 行, 9,972 Bytes)
   - 檔案 2：`F:\Ming_python\ansys-unified-mcp\src\ansys_unified_mcp\products\mechanical\facade.py` (229 行, 9,972 Bytes)
   - 比對命令：`python -c "import filecmp; print(filecmp.cmp('src/.../mechanical.py', 'src/.../mechanical/facade.py', shallow=False))"`
   - 輸出結果：`Identical: True`（兩者位元組完全一致）。

2. **模組導出內容**：
   兩者均導出：
   - 常數：`PRODUCT = "mechanical"`, `DEFAULT_SCRIPT_TIMEOUT = 60.0`
   - 輔助函數：`_esc(s: str) -> str`
   - 核心類別：`MechanicalController`（具備 `connect`, `launch`, `run_script`, `disconnect`, `is_connected`, `status`, `_resolve_target_port`, `_probe_session` 等方法）
   - 單例實例：`controller = MechanicalController()`

3. **運行時載入行為**：
   - 執行命令：`python -c "import ansys_unified_mcp.products.mechanical as m; print(m.__file__)"`
   - 輸出：`.../src/ansys_unified_mcp/products/mechanical/__init__.py`
   - 事實：因 `products/mechanical/` 目錄存在且包含 `__init__.py`，Python 優先載入套件目錄，使得根層級的 `mechanical.py` 實際處於被遮蔽（shadowed）的死代碼狀態。

4. **全專案依賴與引用掃描 (共 20 處核心程式碼與腳本)**：
   - **核心原始碼** (1 處)：
     - `src/ansys_unified_mcp/tools/mechanical_workflow_tools.py:15`: `from ansys_unified_mcp.products.mechanical import controller, _esc`
   - **測試套件** (4 處)：
     - `tests/test_mechanical_controller.py:22`: `from ansys_unified_mcp.products.mechanical import MechanicalController, PRODUCT`
     - `tests/adversarial/test_final_stress_harness.py:23`: `import ansys_unified_mcp.products.mechanical as mechanical_mod`
     - `tests/adversarial/test_m1_envelope_stress_challenge.py:27`: `import ansys_unified_mcp.products.mechanical as mechanical_mod`
     - `tests/adversarial/test_m1_alias_challenge.py:20`: `import ansys_unified_mcp.products.mechanical as mechanical_mod`
   - **範例與技能測試腳本** (11 處)：
     - `examples/shock_analysis/audit_rm_deep.py:6`
     - `examples/shock_analysis/execute_full_shock_act_pipeline.py:7`
     - `examples/shock_analysis/run_shock_35g_pipeline.py:7`
     - `skills/shock-analysis-workflow/scripts/test_session_01.py:17` ~ `test_session_08.py:16` (共 8 個檔案)
   - **向後相容層與內部垂直切片（維持現狀）** (4 處)：
     - `src/ansys_unified_mcp/products/mechanical/__init__.py:9-14` (已匯入 facade 並 re-export)
     - `src/ansys_unified_mcp/products/mechanical/api.py:8` (已指向 facade)
     - `src/ansys_unified_mcp/products/mechanical/tools.py:14` (已指向 facade)
     - `src/ansys_unified_mcp/products/mechanical_api.py:3` (指向 api)

---

## 2. Logic Chain (推導邏輯鏈)

1. **從觀察 1 推導無遺失邏輯**：
   因為 `mechanical.py` 與 `mechanical/facade.py` 的內容經二進位級別比對完全相同 (`filecmp.cmp == True`)，所以刪除 `mechanical.py` 不會丟失任何單一方法、函數、字串或型別註解。
2. **從觀察 2 與 3 推導架構冗餘**：
   因為 `products/mechanical/__init__.py` 已將 `facade` 的所有公共符號 (`MechanicalController`, `PRODUCT`, `controller`, `_esc`) 對外 re-export，且 Python 模組解析時優先選取套件目錄，故 `products/mechanical.py` 在專案中已是完全多餘的複本。
3. **從觀察 4 推導遷移路徑**：
   雖然外部客戶端仍可透過 `__init__.py` 存取符號，但依據 `ORIGINAL_REQUEST.md` 之 R1 要求與最佳解耦實踐，將全庫引用精準更新為 `ansys_unified_mcp.products.mechanical.facade`，能直接鎖定 Session 管理的核心單一事實來源 (Single Source of Truth)，並使單元測試中的 mock/patch 直接作用於源頭單例實例。

---

## 3. Caveats (限制與注意事項)

1. **套件級副效應**：目前 `products/mechanical/__init__.py` 第 16 行匯入了 `tools as _tools`。若後續將外部引用切換為直接導入 `mechanical.facade`，可避免直接載入 MCP 工具層，但因 Python 在載入子模組時仍會初始化父模組，若需徹底輕量化，後續架構重構可考慮將 `tools` 註冊改為 lazy 載入。
2. **範例與技能維護**：`skills/shock-analysis-workflow/scripts/` 下的 8 個腳本雖然不在 MCP 核心運行路徑，但作為工程腳本，建議一併更新以免未來閱讀混淆。

---

## 4. Conclusion (結論與行動建議)

1. **結論**：舊版 `src/ansys_unified_mcp/products/mechanical.py` 完全具備安全刪除條件，無任何未涵蓋邏輯，刪除後將徹底消除歷史雙軌技術債。
2. **具體執行建議**：
   - **檔案操作**：直接刪除 `src/ansys_unified_mcp/products/mechanical.py`。
   - **代碼更新**：
     - 修改 `src/ansys_unified_mcp/tools/mechanical_workflow_tools.py` 行 15。
     - 修改 `tests/test_mechanical_controller.py` 行 22。
     - 修改 `tests/adversarial/` 下 3 個 challenge/harness 檔案的 import。
     - 修改 `examples/` 與 `skills/` 下 11 處腳本。

---

## 5. Verification Method (獨立驗證方式)

交付給 implementer 與 reviewer 的客觀驗證判準：

1. **實體檔案不存在驗證**：
   ```powershell
   Test-Path "src/ansys_unified_mcp/products/mechanical.py"
   # 預期輸出：False
   ```
2. **全專案 import 引用驗證**：
   ```powershell
   # 檢查是否全數指向 facade 或子模組，無殘留舊版 products.mechanical 單檔引用
   python -c "from ansys_unified_mcp.products.mechanical.facade import MechanicalController, controller; print('Facade OK:', controller)"
   ```
3. **單元測試回歸驗證**：
   ```powershell
   pytest tests/test_mechanical_controller.py
   # 預期輸出：測試全數 PASS
   ```
