## 2026-10-01T14:18:08Z
你的身份：explorer_m1_fix_3 (teamwork_preview_explorer)
工作目錄：F:\Ming_python\ansys-unified-mcp\.agents\teamwork\explorer_m1_fix_3
專案根目錄：F:\Ming_python\ansys-unified-mcp
原始需求檔案：F:\Ming_python\ansys-unified-mcp\.agents\teamwork\ORIGINAL_REQUEST.md
失敗報告檔案：F:\Ming_python\ansys-unified-mcp\.agents\teamwork\challenger_m1_2\handoff.md
挑戰測試檔案：F:\Ming_python\ansys-unified-mcp\tests\adversarial\test_m1_concurrency_reconnect_challenge.py

【核心任務：探查與制定 facade.py 併發競爭、斷線重連與快取盲區修復策略】
你在探查階段切勿修改任何原始碼！
請深入調研：
1. 檢驗 `tests/adversarial/test_m1_concurrency_reconnect_challenge.py` 的 3 項失敗測試：
   - `test_concurrent_run_script_file_collision` (PID 暫存檔衝突)
   - `test_reconnect_when_session_dead` (connect 盲目復用死亡 Session)
   - `test_session_dies_during_run_script_not_evicted_due_to_ttl_cache` (10s TTL 盲區與 Session 未驅逐)
2. 深入 `src/ansys_unified_mcp/products/mechanical/facade.py`：
   - 在 `run_script` 中評估改用 `uuid.uuid4().hex` 或唯一標記的方案。
   - 在 `connect()` 中評估先執行 `_probe_session(existing)`，若死亡則 `drop` 並重連的方案。
   - 在 `run_script` 的 exception 區塊中評估主動清理 probe 快取與 registry drop 的方案。
3. 確保修復方案不會破壞現有 7 個 Controller 單元測試、5 個別名測試與 42 個壓力測試。
4. 提出具體可由實作者（Worker）直接落地的代碼修改建議。

【輸出規範】
1. 嚴格使用繁體中文撰寫完整調研報告於 `handoff.md`。
2. 完成後使用 send_message 回報母代理。
