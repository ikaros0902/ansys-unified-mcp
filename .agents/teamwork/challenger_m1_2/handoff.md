# Handoff Report — Milestone 1 壓力與信封邊界挑戰 (Empirical Challenge)

- **Agent**: `challenger_m1_2` (teamwork_preview_challenger)
- **Role**: Critic & Specialist (Empirical Challenger)
- **Handoff Type**: Hard
- **Target Task**: Milestone 1 壓力與信封邊界挑戰
- **Conclusion**: **REJECT** (拒絕交付，發現 3 項關鍵系統漏洞與 1 項測試誤判)

---

## 1. Observation (觀察事實)

### 觀察 1：高頻並行呼叫下暫存檔衝突導致資料踩踏與覆蓋 (Data Corruption)
- **檔案路徑與行號**：`src/ansys_unified_mcp/products/mechanical/facade.py` 第 159–161 行：
  ```python
  tmp_dir = Path(tempfile.gettempdir())
  out_file = (tmp_dir / f"mech_out_{os.getpid()}.txt").as_posix()
  script_file = (tmp_dir / f"mech_script_{os.getpid()}.py").as_posix()
  ```
- **測試命令**：
  ```powershell
  .venv\Scripts\pytest.exe tests/adversarial/test_m1_concurrency_reconnect_challenge.py::test_concurrent_run_script_file_collision -v -s
  ```
- **實測直接輸出 (Verbatim Error)**：
  ```text
  Concurrent run_script results:
  Task 0: expected='OUTPUT_FROM_TASK_0', actual='OUTPUT_FROM_TASK_2'
  Task 3: expected='OUTPUT_FROM_TASK_3', actual='OUTPUT_FROM_TASK_2'
  Task 4: expected='OUTPUT_FROM_TASK_4', actual='OUTPUT_FROM_TASK_2'
  Task 1: expected='OUTPUT_FROM_TASK_1', actual='OUTPUT_FROM_TASK_2'
  Task 2: expected='OUTPUT_FROM_TASK_2', actual='OUTPUT_FROM_TASK_2'
  FAILED
  AssertionError: Concurrent run_script suffered from cross-talk/file collision! Mismatches: [(0, 'OUTPUT_FROM_TASK_0', 'OUTPUT_FROM_TASK_2'), (3, 'OUTPUT_FROM_TASK_3', 'OUTPUT_FROM_TASK_2'), (4, 'OUTPUT_FROM_TASK_4', 'OUTPUT_FROM_TASK_2'), (1, 'OUTPUT_FROM_TASK_1', 'OUTPUT_FROM_TASK_2')]
  ```
- **事實摘要**：在同一個 MCP Server 行程中，多個並行或非同步工作執行緒共用同一個 `os.getpid()`。當 5 個並行請求同時呼叫 `run_script` 時，後進的請求覆蓋了先進請求的腳本檔，且先進請求的 `finally` 區塊刪除了後進請求的輸出檔，造成 80% 的工作輸出混亂、串線或遺失。

---

### 觀察 2：Session 異常中斷後 `connect()` 盲目複用死 Session (Broken Reconnect)
- **檔案路徑與行號**：`src/ansys_unified_mcp/products/mechanical/facade.py` 第 94–97 行：
  ```python
  key = str(target_port)
  if registry.get(PRODUCT, key) is not None:
      registry.set_current(PRODUCT, key)
      return {"ok": True, "port": target_port, "note": "Reused existing session.", "key": key}
  ```
- **測試命令**：
  ```powershell
  .venv\Scripts\pytest.exe tests/adversarial/test_m1_concurrency_reconnect_challenge.py::test_reconnect_when_session_dead -v -s
  ```
- **實測直接輸出 (Verbatim Error)**：
  ```text
  Connect result with dead session in registry: {'ok': True, 'port': 59999, 'note': 'Reused existing session.', 'key': '59999'}
  FAILED
  Failed: VULNERABILITY CONFIRMED: connect() blindly reused a dead session from registry without checking liveness!
  ```
- **事實摘要**：`connect()` 在發現 registry 中已有對應 port 的 key 時，直接回傳 `Reused existing session.`，完全沒有調用 `_probe_session` 或檢查 session 存活狀態。當 Mechanical 連線因崩潰或網路重置中斷後，用戶調用 `connect()` 試圖重新連線，系統只會持續回傳已死亡的連線，斷線重連機制徹底失效。

---

### 觀察 3：執行中斷線未驅逐 Session 且 TTL 快取導致長達 10 秒的假陽性 (Stale TTL & Zombie Session)
- **檔案路徑與行號**：`src/ansys_unified_mcp/products/mechanical/facade.py` 第 131–146 行及 200–201 行：
  ```python
  _PROBE_CACHE: dict[str, float] = {}
  _PROBE_TTL = 10.0
  ...
  except Exception as exc:  # noqa: BLE001
      return "Error: " + str(exc)
  ```
- **測試命令**：
  ```powershell
  .venv\Scripts\pytest.exe tests/adversarial/test_m1_concurrency_reconnect_challenge.py::test_session_dies_during_run_script_not_evicted_due_to_ttl_cache -v -s
  ```
- **實測直接輸出 (Verbatim Error)**：
  ```text
  First run_script result: Error: gRPC connection broken during execution
  Session still in registry: <MagicMock id='...'>
  is_connected() reported: True
  FAILED
  Failed: VULNERABILITY CONFIRMED: is_connected() reported True for a dead session due to stale _PROBE_CACHE TTL!
  ```
- **事實摘要**：若 Session 在通過初始 probe 後執行腳本期間斷線（如 gRPC connection reset），`run_script` 僅將例外轉為字串回傳，完全沒有從 `registry` 中 `drop` 該死 Session，亦未清除 `_PROBE_CACHE`。在此後 10 秒內，`is_connected()` 因 TTL 快取持續報告 `True`（假陽性），掩蓋了真實的斷線狀態。

---

### 觀察 4：既有壓力測試套件在 CLI 獨立執行時誤判退出 (CLI False Alarm)
- **檔案路徑與行號**：`tests/adversarial/test_final_stress_harness.py` 第 336–342 行：
  ```python
  success1 = test_section_1_fourteen_tools_stress()
  ...
  if success1 and success2 and success3 and success4 and success5:
  ```
- **測試命令**：
  ```powershell
  .venv\Scripts\python.exe tests/adversarial/test_final_stress_harness.py
  ```
- **實測直接輸出 (Verbatim Output)**：
  ```text
  【挑戰結論】實證測試發現破口！存在假陽性或型別錯誤！              
  判定結果: DISPROVED
  (Exit code: 1)
  ```
- **事實摘要**：雖然透過 `pytest tests/adversarial/test_final_stress_harness.py` 執行為全數 PASSED（因為 pytest 僅依據無 assertion failure 判定通過），但作為獨立 CLI 工具執行時，5 個 `test_section_*` 函數均無 `return True`（預設回傳 `None`），導致 `if` 條件式判斷為 `False`，輸出 DISPROVED 且 Exit code 為 1。

---

## 2. Logic Chain (推導邏輯鏈)

1. **從觀察 1 推導高頻並行崩潰**：
   - 觀察 1 證實 `run_script` 依賴以 `os.getpid()` 命名的固定實體暫存檔案傳遞腳本與擷取標準輸出。
   - 由於 Python Process 內部的多個並行 Task / Thread 具有完全相同的 PID，當多個工具或客戶端高頻同時請求時，暫存檔發生不可逆的競爭踩踏（Race condition）。
   - 經實測 5 個並行請求發生 80% 串線與覆蓋，這違背了原始架構要求「支援並行與多實例」的強韌性標準。

2. **從觀察 2 與 3 推導連線生命週期與異常處理缺陷**：
   - 觀察 2 證實 `connect()` 採用「只要 key 在字典中就直接重用」的樂觀策略，完全沒有驗證該連線是否真正處於可用狀態。
   - 觀察 3 證實當連線在執行中中斷時，系統未主動清除 registry，且被 10 秒 TTL 快取蒙蔽。
   - 兩者疊加導致：一旦連線因任何原因斷開，後續既無法透過 `is_connected()` 即時察覺，亦無法透過調用 `connect()` 重新連線，客戶端將永遠陷入無法自動恢復的殭屍連線狀態。

3. **從觀察 4 推導測試工具鏈瑕疵**：
   - 實作者交付文件中雖標記 `test_final_stress_harness.py` 通過，但未察覺其作為獨立執行腳本時必定回傳 Exit Code 1，顯示測試工具本身的回傳型別約定未嚴謹對齊。

4. **綜合推導最終判決**：
   - 任務指示明確要求：「檢驗高頻並行呼叫與錯誤注入情境下，facade 是否能正確處理 Session 異常與斷線重連機制。」
   - 實證結果證明 facade 無法承受高頻並行呼叫（檔案碰撞），亦無法在錯誤注入後正確重建連線（殭屍連線），故本階段實作**不符合生產就緒之信封邊界與壓力標準**，必須給予 **REJECT**。

---

## 3. Caveats (限制與注意事項)

1. **R1 基礎清理工作之確認**：
   實作者對 `src/ansys_unified_mcp/products/mechanical.py` 的物理刪除與 16 處檔案的 import 重導向已確實完成，且靜態引用掃描零殘留。本報告的拒絕並非否定檔案清理成果，而是針對其重構目標 `facade.py` 在並行與錯誤注入下的實質執行能力提出挑戰。
2. **測試環境限定**：
   本次對抗測試基於 Mock gRPC session 進行毫秒級並行模擬，實務上 PyMechanical gRPC server 執行時間通常介於 50ms 至數秒，其暫存檔碰撞與檔案鎖衝突機率在真實負載下將更加顯著。

---

## 4. Conclusion (結論與修復建議)

### 判決：**REJECT (拒絕通過)**

### 具體修復方案（供實作者 Worker 執行）：

1. **修復高頻並行暫存檔碰撞**：
   在 `MechanicalController.run_script` 中，改用 `uuid.uuid4().hex` 或 `threading.get_ident()` 生成唯一的臨時檔名，或直接在記憶體中傳遞代碼（若 PyMechanical 支援），徹底杜絕檔案名稱衝突：
   ```python
   import uuid
   req_id = uuid.uuid4().hex
   out_file = (tmp_dir / f"mech_out_{req_id}.txt").as_posix()
   script_file = (tmp_dir / f"mech_script_{req_id}.py").as_posix()
   ```

2. **修復 `connect()` 盲目複用死 Session**：
   在 `connect()` 中重用 Session 前，必須先調用 `_probe_session`。若探針檢測失敗，應立即執行 `registry.drop(PRODUCT, key)`，並重新建立新的 `mech.connect_to_mechanical` 連線：
   ```python
   existing = registry.get(PRODUCT, key)
   if existing is not None and self._probe_session(existing):
       registry.set_current(PRODUCT, key)
       return {"ok": True, "port": target_port, "note": "Reused existing session.", "key": key}
   elif existing is not None:
       registry.drop(PRODUCT, key)
   ```

3. **修復例外發生時死 Session 驅逐與快取清除**：
   在 `run_script` 的例外捕獲區塊中，若捕獲到重大通訊錯誤（或直接判定腳本執行異常），應主動清除 `_PROBE_CACHE` 中的該 Session 紀錄，並考慮驅逐該 Session：
   ```python
   except Exception as exc:
       if session is not None:
           self._PROBE_CACHE.pop(str(id(session)), None)
           registry.drop(PRODUCT, key)
       return "Error: " + str(exc)
   ```

4. **修復 `test_final_stress_harness.py` 的 CLI 回傳值**：
   在 5 個 `test_section_*` 函數末尾加上顯式的 `return True`，確保獨立以 `python.exe test_final_stress_harness.py` 執行時能正確印出 `CONFIRMED` 並回傳 Exit code 0。

---

## 5. Verification Method (獨立重現與驗證方式)

審查者與實作者可於專案根目錄執行以下指令，100% 重現實證挑戰之失敗結果：

1. **重現並行資料踩踏、斷線重連失效與殭屍 Session 缺陷**：
   ```powershell
   .venv\Scripts\pytest.exe tests/adversarial/test_m1_concurrency_reconnect_challenge.py -v -s
   ```
   **預期實證輸出**：3 項測試全數 `FAILED`（分別觸發 `AssertionError: Concurrent run_script suffered from cross-talk/file collision!`、`Failed: VULNERABILITY CONFIRMED: connect() blindly reused a dead session`、以及 `Failed: VULNERABILITY CONFIRMED: is_connected() reported True for a dead session`）。

2. **重現測試腳本 CLI 誤判**：
   ```powershell
   .venv\Scripts\python.exe tests/adversarial/test_final_stress_harness.py
   ```
   **預期實證輸出**：印出 `判定結果: DISPROVED`，且 `$LASTEXITCODE` 為 `1`。
