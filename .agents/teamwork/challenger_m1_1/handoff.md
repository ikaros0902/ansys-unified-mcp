# 對抗挑戰實證驗證報告 (Handoff Report) — Milestone 1

- **代理人 (Agent)**：`challenger_m1_1` (EMPIRICAL CHALLENGER / critic / specialist)
- **交付類型 (Handoff Type)**：Hard (實證挑戰與邊界壓測全數執行完畢)
- **接收者 (Recipient)**：`b64f9ba5-0d28-4ac0-a95d-862e7b398eaf` (parent)
- **審查目標**：Milestone 1 (R1 消除代碼重複與技術債)
- **驗證結論**：**REJECT (拒絕驗收，須修正致命循環匯入缺陷後重新提測)**

---

## 1. Observation (觀察事實)

本挑戰者拒絕盲信實作者的日誌宣稱，親自撰寫並執行全套經驗對抗測試，直接觀察到以下客觀事實：

1. **實體檔案消除與別名對抗測試現況**：
   - 執行指令：`Test-Path "src/ansys_unified_mcp/products/mechanical.py"`
     - 輸出：`False`（確認檔案已徹底自檔案系統物理刪除）。
   - 執行指令：`.venv\Scripts\pytest.exe tests/adversarial/test_m1_alias_challenge.py -v`
     - 輸出：`5 passed in 2.15s`。39 個 Canonical 工具與 39 個 Legacy 別名在 FastMCP Schema、參數簽名與離線呼叫等價性上 100% 對稱。
   - 執行指令：`.venv\Scripts\pytest.exe tests/unit/`
     - 輸出：`257 passed, 2 skipped in 8.42s`。

2. **致命缺陷：公開導出契約觸發循環匯入崩潰 (Circular Import Failure)**：
   - 本挑戰者撰寫獨立對抗測試 `tests/adversarial/test_m1_facade_adversarial_challenge.py`，於測試 `test_circular_import_vulnerability_on_driver_export` 中實證觸發崩潰。
   - 在全新終端執行直接匯入指令：
     ```powershell
     $env:PYTHONPATH="src"; .venv\Scripts\python.exe -c "from ansys_unified_mcp.products.mechanical import MechanicalDriver; print('Driver OK:', MechanicalDriver)"
     ```
   - 終端**逐字報錯 (Verbatim Traceback)** 如下：
     ```text
     Traceback (most recent call last):
       File "<string>", line 1, in <module>
         from ansys_unified_mcp.products.mechanical import MechanicalDriver; print('Driver OK:', MechanicalDriver)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
       File "F:\Ming_python\ansys-unified-mcp\src\ansys_unified_mcp\products\mechanical\__init__.py", line 21, in __getattr__
         from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver
       File "F:\Ming_python\ansys-unified-mcp\src\ansys_unified_mcp\products\mechanical\driver.py", line 20, in <module>
         from ansys_unified_mcp.drivers.base import BaseSolverDriver, SolverDriverError
       File "F:\Ming_python\ansys-unified-mcp\src\ansys_unified_mcp\drivers\__init__.py", line 22, in <module>
         from ansys_unified_mcp.drivers.mechanical_driver import MechanicalDriver
     ImportError: cannot import name 'MechanicalDriver' from 'ansys_unified_mcp.drivers.mechanical_driver' (F:\Ming_python\ansys-unified-mcp\src\ansys_unified_mcp\drivers\mechanical_driver.py)
     ```
   - 程式碼確切位置：
     - `src/ansys_unified_mcp/products/mechanical/__init__.py` 第 32 行將 `"MechanicalDriver"` 列於 `__all__`，並於第 21 行 `__getattr__` 進行延遲匯入。
     - `src/ansys_unified_mcp/products/mechanical/driver.py` 第 20 行匯入 `from ansys_unified_mcp.drivers.base import BaseSolverDriver`。
     - 該匯入觸發 `src/ansys_unified_mcp/drivers/__init__.py` 執行第 22 行：`from ansys_unified_mcp.drivers.mechanical_driver import MechanicalDriver`。
     - `src/ansys_unified_mcp/drivers/mechanical_driver.py` 第 6–8 行藉由遍歷 `_driver.__dict__` 反射拷貝符號。但此時 `driver.py` 正停在第 20 行，其底下的 `class MechanicalDriver` 尚未定義，導致 `mechanical_driver` 模組未取得該類別，拋出致命 `ImportError`。

3. **架構隱患：多執行緒併發調用時暫存檔競爭 (Race Condition on PID Temp File)**：
   - 檢視 `src/ansys_unified_mcp/products/mechanical/facade.py` 第 160–161 行：
     ```python
     tmp_dir = Path(tempfile.gettempdir())
     out_file = (tmp_dir / f"mech_out_{os.getpid()}.txt").as_posix()
     script_file = (tmp_dir / f"mech_script_{os.getpid()}.py").as_posix()
     ```
   - 實證結果：當在同一 Python Process 內以 10 個執行緒同時併發呼叫 `controller.run_script(...)` 時：
     - 由於 `core/timeout.py` 設有 `_MAX_WORKERS = 8` 限制，第 9 與第 10 個執行緒被直接拒絕：`Error: Thread pool exhausted (8/8 workers busy). Some ANSYS sessions may be unresponsive.`。
     - 其餘執行緒因共用同一個以 Process PID 命名的暫存檔案，會發生競爭寫入與提早被其他線程之 `finally` 區塊 `os.remove` 刪除，導致部分執行緒回傳空字串或 `(done)`。

4. **容錯盲區：Probe 快取 TTL 造成的斷線誤判**：
   - 檢視 `facade.py` 第 136–146 行：
     `_PROBE_CACHE` 快取時間為 `_PROBE_TTL = 10.0`。
   - 實證測試 `test_probe_cache_ttl_and_failure_eviction`：若連線在 Probe 成功後立即中斷（例如 Broken pipe），在接下來的 10 秒內，`_probe_session` 與 `is_connected()` 仍會因命中快取而誤判為 True，呼叫端需承擔 10 秒的狀態判定盲區。

5. **通過之穩健性驗證 (正面實證)**：
   - **字串跳脫神諭 (AST Round-trip Oracle)**：針對包含反斜線、引號炸彈、雙引號、Windows 路徑、繁體中文、特殊符號與 Emoji 等 12 種邊界字串，`_esc` 嵌入 IronPython double-quoted literal 後，以 `ast.literal_eval` 驗證皆 100% 精準還原原字串。
   - **安全守衛阻擋**：當 `ANSYS_MCP_SCRIPT_GUARD=strict` 時，惡意指令（如 `subprocess`）能被 `facade.controller.run_script` 成功攔截並回傳規範之錯誤字串。
   - **單例狀態連動**：`facade.controller` 與 `mechanical.controller` 指向同一個記憶體位址 (`is`)，且在 `SessionRegistry` 上的增刪改查即時雙向連動。

---

## 2. Logic Chain (推導邏輯鏈)

1. **從觀察 1 與 5 推導基礎整潔度與外圍相容性良好**：
   - 舊版 `mechanical.py` 物理檔案確實已不存在，全庫 16 處原本引用舊檔案之處皆已更新指向 `facade`。
   - FastMCP 工具面之 39 對別名完全等價，全專案 257 項既有單元測試無回歸。
2. **從觀察 2 推導違反原始需求驗收標準 (Acceptance Criteria Failure)**：
   - 原始需求明確規範：`執行全專案 pytest，測試 100% 通過，無任何 ImportError 或殘留的舊版引用。`
   - `mechanical/__init__.py` 透過 `__all__` 對外公開宣稱支援導出 `MechanicalDriver`。
   - 然而，由於 `mechanical/driver.py` 與 `drivers/mechanical_driver.py` 存在循環依賴，當外界依約使用 `from ansys_unified_mcp.products.mechanical import MechanicalDriver` 時，直接爆發未捕獲之 `ImportError`。
   - 既有測試未發現此問題，係因既有測試從未以獨立乾淨的匯入鏈路觸發此公開 API。
3. **從觀察 3 與 4 推導邊界架構風險**：
   - 雖非本階段阻塞性指標，但 `mech_out_{os.getpid()}.txt` 在多執行緒下必然碰撞，未來在 FastMCP 非同步伺服器高併發場景下具備高風險；`_PROBE_CACHE` 的 10 秒 TTL 盲區亦應有文檔說明。
4. **綜合判定**：
   - 因存在公開 API 循環匯入致命崩潰（硬性違約），本階段驗收**無法給予通過 (REJECT)**，必須退回實作者修復該循環依賴。

---

## 3. Caveats (限制與注意事項)

1. **Live Mechanical 物理連線未覆蓋**：本測試環境未安裝 ANSYS Mechanical 2024/2026 商業版授權與實體軟體，所有通訊係以 mock session 與偽造之 gRPC 核心進行語法與通訊協定級壓測。
2. **併發競爭之觸發條件**：多執行緒檔案覆蓋隱患僅在同一 Process 內多執行緒同時呼叫 `run_script` 時發生；若使用者為單執行緒序列呼叫則不受影響。

---

## 4. Conclusion (最終評定結論)

### 評定結果：**REJECT (拒絕驗收)**

**原因**：
`src/ansys_unified_mcp/products/mechanical/__init__.py` 對外導出之 `MechanicalDriver` 存在循環匯入致命缺陷，在終端直接執行 `from ansys_unified_mcp.products.mechanical import MechanicalDriver` 必然觸發 `ImportError`，直接違反 ORIGINAL_REQUEST.md 之「無任何 ImportError」驗收標準。

**修復建議 (針對實作者 worker_m1)**：
1. **解開循環依賴**：
   修改 `src/ansys_unified_mcp/drivers/mechanical_driver.py`，避免在模組頂層利用 `_driver.__dict__` 反射拷貝未初始化完成的模組；改為明確的 `from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver`（或使用 `__getattr__` 延遲導出）。
2. **併發暫存檔建議（後續改進）**：
   在 `facade.py` 的暫存檔名加入執行緒 ID 或 UUID（例如 `f"mech_out_{os.getpid()}_{threading.get_ident()}.txt"`），徹底杜絕檔案競爭。

---

## 5. Verification Method (獨立覆核與實證方式)

實作者或母代理可於專案根目錄下直接執行以下命令覆核本挑戰者的發現：

1. **實證致命循環匯入缺陷 (必崩潰)**：
   ```powershell
   $env:PYTHONPATH="src"; .venv\Scripts\python.exe -c "from ansys_unified_mcp.products.mechanical import MechanicalDriver; print('OK')"
   # 當前行為：拋出 ImportError: cannot import name 'MechanicalDriver' from 'ansys_unified_mcp.drivers.mechanical_driver'
   # 修復後預期：輸出 OK，Exit code 0
   ```

2. **執行本挑戰者編寫之完整對抗挑戰套件**：
   ```powershell
   .venv\Scripts\pytest.exe tests/adversarial/test_m1_facade_adversarial_challenge.py -v
   # 當前行為：22 passed, 1 failed (test_circular_import_vulnerability_on_driver_export 失敗)
   # 修復後預期：23 passed 全數通過
   ```

3. **執行既有別名對抗測試**：
   ```powershell
   .venv\Scripts\pytest.exe tests/adversarial/test_m1_alias_challenge.py -v
   # 預期：5 passed in ~2s
   ```
