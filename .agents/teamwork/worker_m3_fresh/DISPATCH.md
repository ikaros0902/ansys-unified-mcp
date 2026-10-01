## 2026-10-01T22:38:39Z
你的身份：worker_m3_fresh (teamwork_preview_worker)
工作目錄：F:\Ming_python\ansys-unified-mcp\.agents\teamwork\worker_m3_fresh
專案根目錄：F:\Ming_python\ansys-unified-mcp
原始需求檔案：F:\Ming_python\ansys-unified-mcp\.agents\teamwork\ORIGINAL_REQUEST.md
專案規劃檔案：F:\Ming_python\ansys-unified-mcp\.agents\teamwork\orchestrator_1\PROJECT.md
調研交接文件：F:\Ming_python\ansys-unified-mcp\.agents\teamwork\explorer_survey_3\handoff.md

【MANDATORY INTEGRITY WARNING】
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. An auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

【核心任務：實作 Milestone 3 (R3 清理與收斂專案根目錄腳本)】
請詳閱 ORIGINAL_REQUEST.md 與 explorer_survey_3 的 handoff.md。
你擁有 `scripts/` 與 `examples/` 目錄的搬遷與整理權限：

1. 【搬移歸檔】：
   - 將 `scripts/_archive_mesh_fix_202609/` 內部所有的 12 個網格除錯腳本完整遷移至 `examples/mesh_debug/`。
   - 刪除舊目錄 `scripts/_archive_mesh_fix_202609/`。
   - 在 `examples/mesh_debug/README.md` 中撰寫說明文件（繁體中文），說明該批腳本為 2026 年 9 月伺服器機箱（包含 114 個 body、SM-BASEPAN-GDZ 等）網格劃分排障之歷史實戰範例。

2. 【收斂驗證】：
   - 驗證專案根目錄 `scripts/` 下僅保留 `deploy/` 與 `maintenance/` 兩大專案級維護與發布目錄，無任何 `_archive` 殘留或雜散腳本。
   - 執行 `.venv\Scripts\pytest.exe tests/unit/` 確保搬移未對測試造成任何負面影響。

【輸出規範】
1. 嚴格使用繁體中文撰寫完整實作與測試報告於 `handoff.md`。
2. 保持 progress.md 隨時更新。
3. 完成後使用 send_message 回報母代理。
