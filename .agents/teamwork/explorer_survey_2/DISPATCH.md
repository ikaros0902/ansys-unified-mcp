## 2026-10-01T13:51:58Z
你的身份：explorer_survey_2 (teamwork_preview_explorer)
工作目錄：F:\Ming_python\ansys-unified-mcp\.agents\teamwork\explorer_survey_2
專案根目錄：F:\Ming_python\ansys-unified-mcp
原始需求檔案：F:\Ming_python\ansys-unified-mcp\.agents\teamwork\ORIGINAL_REQUEST.md

【核心任務：探查 R2 Agent Skills 規範與漸進式揭露現況 (Skills Compliance)】
請詳閱 ORIGINAL_REQUEST.md。你的任務是只讀探查，切勿修改任何原始碼！
依據 agentskills.io 規範與 Progressive Disclosure 準則：
1. 盤點專案根目錄下 `skills/` 內的所有子資料夾與檔案結構。
2. 檢查每一個 Skill 的 `SKILL.md`：
   - 是否包含正確的 YAML frontmatter？
   - frontmatter 中的 `name` 是否全小寫連字號（kebab-case）且與所在資料夾名稱完全一致？
   - 是否具備清晰的 `description`？
   - 統計各 `SKILL.md` 的行數。有哪些超過 500 行需要進行漸進式揭露瘦身？
   - 檢查是否已有 `scripts/` 或 `references/` 資料夾，哪些重型程式碼或文件需要被移入？
3. 列出具體需要重構的 Skill 清單與建議的調整方式。

【輸出規範】
1. 嚴格使用繁體中文撰寫完整調研報告，存放在工作目錄的 `report.md` 與 `handoff.md`。
2. 保持 progress.md 隨時更新。
3. 調研完成後，使用 send_message 回報母代理。
