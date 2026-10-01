## 2026-10-01T14:44:12Z
你的身份：worker_m2 (teamwork_preview_worker)
工作目錄：F:\Ming_python\ansys-unified-mcp\.agents\teamwork\worker_m2
專案根目錄：F:\Ming_python\ansys-unified-mcp
原始需求檔案：F:\Ming_python\ansys-unified-mcp\.agents\teamwork\ORIGINAL_REQUEST.md
專案規劃檔案：F:\Ming_python\ansys-unified-mcp\.agents\teamwork\orchestrator_1\PROJECT.md
調研交接文件：F:\Ming_python\ansys-unified-mcp\.agents\teamwork\explorer_survey_2\handoff.md

【MANDATORY INTEGRITY WARNING】
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. An auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

【核心任務：實作 Milestone 2 (R2 實踐 Agent Skills 規範與漸進式揭露)】
請詳閱 ORIGINAL_REQUEST.md 與 explorer_survey_2 的 handoff.md。
你擁有 `skills/` 目錄的專屬修改與重構權限，請執行以下項目：

1. 【資料夾名稱與 SKILL.md name 完全一致】：
   - 驗收標準要求：「skills/ 下所有資料夾名稱與內部 SKILL.md 的 name 屬性完全一致」。
   - 特別針對 `skills/shock-analysis-workflow/` 下 8 個子目錄：
     若資料夾為 `01-material-assignment`，則將其 `SKILL.md` 的 YAML frontmatter `name` 更新為 `01-material-assignment`（或將資料夾與 name 同步更名為全小寫連字號之合規名稱），確保兩者 100% 逐字相同。
   - 遍歷並確保 `skills/` 底下所有層級的每一份 `SKILL.md`，其所屬資料夾名稱與 frontmatter 中的 `name` 完全一致，且具備 `description`。

2. 【標準化 references/ 目錄與超連結】：
   - 將 `skills/` 底下所有 22 處單數資料夾 `reference/` 更名為標準複數 `references/`。
   - 批次更新相關 `.md` 檔案內部指向 `reference/` 的 Markdown 超連結與路徑，改為 `references/`。

3. 【消除重複技能冗餘】：
   - 刪除完全重複的 `skills/ansys-spaceclaim-modeling/`（與 `skills/ansys-geometry-modeling/` 100% 相同）。若有專案文件或 README 提及，統一導向 `ansys-geometry-modeling` 或 `ansys-spaceclaim`。

4. 【目錄結構整理與散落腳本歸位】：
   - 將 `skills/pdf-to-md/convert.py` 移入 `skills/pdf-to-md/scripts/convert.py`。
   - 修復 `skills/README.md` 的表格破裂問題，確保所有技能均被正確索引。

5. 【客觀自檢驗證】：
   - 執行 Python 驗證腳本：檢驗 `skills/` 下所有資料夾名稱是否與其內部的 `SKILL.md` 之 `name` 100% 一致。
   - 檢驗全專案是否已無任何單數 `reference` 資料夾殘留。
   - 執行 `.venv\Scripts\pytest.exe tests/unit/` 確保現有單元測試零回歸。

【輸出規範】
1. 嚴格使用繁體中文撰寫完整實作與測試報告於 `handoff.md`。
2. 保持 progress.md 隨時更新。
3. 完成後使用 send_message 回報母代理。
