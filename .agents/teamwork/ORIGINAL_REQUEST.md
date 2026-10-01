# Original User Request

## 2026-10-01T13:49:54Z

本專案為 `ansys-unified-mcp` 架構重構的【第一階段：止血與排毒 (Detox)】。目標是消除歷史代碼雙軌技術債、清理混亂的腳本目錄，並強制所有 Agent Skills 符合 `agentskills.io` 開放標準的漸進式揭露規範。此階段不涉及伺服器拆分與新功能實作，旨在為後續的「MCP 實體隔離架構」打下純淨的程式碼地基。

Working directory: F:\Ming_python\ansys-unified-mcp

Integrity mode: demo

## Requirements

### R1. 消除代碼重複與技術債 (Codebase Deduplication)
完全刪除舊版 `src/ansys_unified_mcp/products/mechanical.py`。全面更新專案中所有的引用（包含 `tools.py` 等），使其全部指向 `ansys_unified_mcp.products.mechanical.facade`。確立單一事實來源，消除雙軌維護風險。

### R2. 實踐 Agent Skills 規範與漸進式揭露 (Skills Compliance)
依據 `agentskills.io` 規範重構 `skills/` 目錄：
1. 確保所有 `SKILL.md` 具備標準合規的 YAML frontmatter（`name` 全小寫連字號且與所屬資料夾名稱完全一致、`description` 具備清晰關鍵字）。
2. 將超長 Markdown 瘦身，遵循漸進式揭露（Progressive Disclosure，主指令建議 < 500 行），將重型代碼與文件分別移入各 Skill 的 `scripts/` 與 `references/`。

### R3. 清理與收斂專案根目錄腳本 (Scripts Cleanup)
清理根目錄 `scripts/_archive_mesh_fix_202609/`，將具實戰價值的 CAE 網格腳本歸入 `skills/ansys-mesh/scripts/` 或 `examples/mesh_debug/` 歸檔。使根目錄 `scripts/` 僅保留專案級建置/維護腳本。

## Acceptance Criteria

### 程式碼與測試驗證 (Programmatic)
- [ ] 執行全專案 `pytest`，測試 100% 通過，無任何 `ImportError` 或殘留的舊版引用。
- [ ] 專案內已無 `products/mechanical.py` 實體檔案。

### 目錄樹與 Skills 標準化驗證
- [ ] `skills/` 下所有資料夾名稱與內部 `SKILL.md` 的 `name` 屬性完全一致。
- [ ] 根目錄 `scripts/` 內無任何 `_archive` 或特定的模擬業務除錯腳本。


## 2026-10-01T22:37:01Z

伺服器重啟通知：
請繼續推動 `ansys-unified-mcp` 第一階段排毒任務（M1 已完成，請接續喚醒或推進 M2: Skills 規範重構、M3: 根目錄腳本清理歸檔，以及 M4: 全量測試與 Victory Audit）。
使用者已指示：完成後將 plan 與專案所有更新內容 push 至 github。請全速推進並隨時回報！
