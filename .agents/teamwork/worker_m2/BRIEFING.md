# BRIEFING — 2026-10-01T14:45:00Z

## Mission
實作 Milestone 2 (R2 實踐 Agent Skills 規範與漸進式揭露)：規範化 skills/ 目錄架構、資料夾與 SKILL.md name 完全一致、標準化 references/ 目錄與連結、消除冗餘技能、腳本歸位、修復 skills/README.md，並確保客觀驗證與單元測試零回歸。

## 🔒 My Identity
- Archetype: teamwork_preview_worker
- Roles: implementer, qa, specialist
- Working directory: F:\Ming_python\ansys-unified-mcp\.agents\teamwork\worker_m2
- Original parent: b64f9ba5-0d28-4ac0-a95d-862e7b398eaf
- Milestone: Milestone 2 (R2 實踐 Agent Skills 規範與漸進式揭露)

## 🔒 Key Constraints
- 嚴格使用繁體中文撰寫所有文件、報告、註解與訊息
- 嚴禁造假作弊：不得硬編碼測試結果，必須真實修改與真實測試驗證
- 驗收標準：skills/ 下所有資料夾名稱與內部 SKILL.md 的 name 屬性完全一致且有 description
- 將 skills/ 底下所有單數 reference/ 目錄更名為 references/，並批次更新相關 .md 連結
- 刪除完全重複的 skills/ansys-spaceclaim-modeling/，更新索引與引用
- 將 skills/pdf-to-md/convert.py 移至 scripts/convert.py
- 修復 skills/README.md 表格破裂
- 執行客觀自檢驗證與 pytest 單元測試零回歸

## Current Parent
- Conversation ID: b64f9ba5-0d28-4ac0-a95d-862e7b398eaf
- Updated: 2026-10-01T14:45:00Z

## Task Summary
- **What to build**: 規範化 skills/ 資料夾結構與 metadata，修復 references 路徑與文件索引，刪除重複技能，歸位腳本
- **Success criteria**: 
  1. 所有包含 SKILL.md 的資料夾，其名稱與 SKILL.md 中的 `name` 逐字相同，且具備 `description`
  2. 無任何單數 `reference/` 資料夾殘留，所有 markdown 超連結均已更新
  3. `skills/ansys-spaceclaim-modeling/` 成功刪除且文檔已更新指向
  4. `skills/pdf-to-md/scripts/convert.py` 成功就位
  5. `skills/README.md` 表格結構完整且正確索引所有現存技能
  6. 專屬驗證腳本全數 PASS，pytest 單元測試通過
- **Interface contracts**: F:\Ming_python\ansys-unified-mcp\.agents\teamwork\orchestrator_1\PROJECT.md
- **Code layout**: skills/

## Key Decisions Made
- [TBD]

## Artifact Index
- F:\Ming_python\ansys-unified-mcp\.agents\teamwork\worker_m2\DISPATCH.md — 指派記錄
- F:\Ming_python\ansys-unified-mcp\.agents\teamwork\worker_m2\BRIEFING.md — 工作記憶
- F:\Ming_python\ansys-unified-mcp\.agents\teamwork\worker_m2\progress.md — 心跳與進度追蹤
- F:\Ming_python\ansys-unified-mcp\.agents\teamwork\worker_m2\handoff.md — 完工交接報告

## Change Tracker
- **Files modified**: [TBD]
- **Build status**: [TBD]
- **Pending issues**: 無

## Quality Status
- **Build/test result**: [TBD]
- **Lint status**: [TBD]
- **Tests added/modified**: 撰寫專案技能一致性客觀檢查腳本與執行現有單元測試

## Loaded Skills
- Source: None
