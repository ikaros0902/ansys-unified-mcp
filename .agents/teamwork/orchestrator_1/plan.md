# 實施計畫 (Implementation Plan)

## 任務背景與目標
依據 `ORIGINAL_REQUEST.md`，推進 `ansys-unified-mcp` 架構重構第一階段【止血與排毒 (Detox)】。
重點在於：
1. 刪除 `src/ansys_unified_mcp/products/mechanical.py` 並將全專案引用切換至 `facade`。
2. 重構 `skills/` 目錄符合 `agentskills.io` 規範（YAML frontmatter、漸進式揭露、子目錄劃分）。
3. 清理根目錄 `scripts/_archive_mesh_fix_202609/`，歸檔至 `skills/ansys-mesh/scripts/` 或 `examples/mesh_debug/`。
4. 全面執行 pytest 達到 100% 通過與門禁驗證。

---

## 階段劃分與實施步驟

### 階段 0: 全域探查 (Survey Phase)
- 並行派發 3 位 Explorer：
  - `explorer_survey_1`: 探查 R1 (mechanical.py 內容、與 facade 差異、全專案引用分布)。
  - `explorer_survey_2`: 探查 R2 (skills/ 目錄清單、YAML frontmatter、行數超標情況、漸進式揭露結構)。
  - `explorer_survey_3`: 探查 R3 與當前測試 (scripts/ 目錄現況、_archive 內容、當前 pytest 執行基線與環境)。
- 輸出：彙整探查報告，建立 `PROJECT.md` 與 `GATE_STATUS.md`。

### 階段 1: 里程碑 M1 - 消除代碼重複與技術債 (R1)
- 派發 Worker 實作：
  - 徹底刪除 `src/ansys_unified_mcp/products/mechanical.py`。
  - 將所有相依引用改為 `ansys_unified_mcp.products.mechanical.facade`。
  - 確保無殘留引入。
- 派發 Reviewer & Challenger 進行程式碼審查與測試驗證。

### 階段 2: 里程碑 M2 - 實踐 Agent Skills 規範與漸進式揭露 (R2)
- 派發 Worker 實作：
  - 調整 skills/ 資料夾命名與內部 `SKILL.md` 的 YAML frontmatter (`name`, `description`) 一致。
  - 依漸進式揭露原則，將超長代碼與參考資料拆解至 `scripts/` 與 `references/`，使主 `SKILL.md` 精簡。
- 派發 Reviewer 審查規範合規性。

### 階段 3: 里程碑 M3 - 清理與收斂根目錄腳本 (R3)
- 派發 Worker 實作：
  - 清理 `scripts/_archive_mesh_fix_202609/`，搬移歸檔至 `skills/ansys-mesh/scripts/` 或 `examples/mesh_debug/`。
  - 確保根目錄 `scripts/` 僅保留專案級建置/維護工具。
- 派發 Reviewer 審查目錄整潔度。

### 階段 4: 里程碑 M4 - 全專案測試驗收與審計 (AC & Final Gate)
- 執行全專案 `pytest`，確保 100% 通過。
- 派發 Challenger 與 Forensic Auditor (`teamwork_preview_auditor`) 進行完整獨立查驗。
- 通過後整理最終產出並向 Sentinel 發送完成回報。
