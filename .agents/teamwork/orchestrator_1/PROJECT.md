# Project: ansys-unified-mcp 第一階段重構【止血與排毒 (Detox)】

## Architecture
- 單一事實來源 (SSOT)：全面收斂至 `products/mechanical/facade.py`，移除重複的 `products/mechanical.py`。
- Agent Skills 規範化：遵循 `agentskills.io` 開放標準，frontmatter `name` 與資料夾名完全一致，標準化 `references/` 與 `scripts/` 子目錄。
- 專案根目錄收斂：`scripts/` 僅保留專案維護與發布工具（`deploy/`, `maintenance/`），業務專案除錯腳本歸檔至 `examples/mesh_debug/`。

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | 刪除舊版 mechanical.py | 徹底移除根層級重複的 `products/mechanical.py` | M1 | ORIGINAL_REQUEST R1 |
| 2 | 更新全庫 mechanical 引用 | 將 tools, tests, examples, skills 中舊版引用改向 `facade` | M1 | ORIGINAL_REQUEST R1 |
| 3 | Skills YAML frontmatter 一致化 | 修正 `shock-analysis-workflow` 8 個子模組 name 與目錄一致 | M2 | ORIGINAL_REQUEST R2 |
| 4 | Skills 目錄結構標準化 | 22 處 `reference/` 改為複數 `references/`，超連結更新 | M2 | ORIGINAL_REQUEST R2 |
| 5 | 消除幾何技能重複技術債 | 消除 `ansys-spaceclaim-modeling` 與 `ansys-geometry-modeling` 冗餘 | M2 | Survey 發現 |
| 6 | 清理散落技能腳本 | 將 `pdf-to-md/convert.py` 移入 `scripts/`，修復 README 表格 | M2 | Survey 發現 |
| 7 | 歸檔網格排障腳本 | 遷移 `_archive_mesh_fix_202609/` 12 腳本至 `examples/mesh_debug/` | M3 | ORIGINAL_REQUEST R3 |
| 8 | 根目錄 scripts 淨化 | 確保根目錄 `scripts/` 僅存 `deploy/` 與 `maintenance/` | M3 | ORIGINAL_REQUEST R3 |
| 9 | 修復測試套件 AST 與路徑 | 修復 138 工具統計與 audit 路徑，實現 pytest 100% 通過 | M4 | ORIGINAL_REQUEST AC |
| 10| 全域完整性門禁與稽核 | 通過 Reviewer、Challenger 與 Forensic Auditor 驗證 | M4 | ORIGINAL_REQUEST AC |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: 消除代碼重複與技術債 | 刪除 mechanical.py 並更新所有引用至 facade | none | DONE |
| 2 | M2: 實踐 Agent Skills 規範與漸進式揭露 | 重構 skills/ 目錄、frontmatter、子目錄名與冗餘消除 | none | DONE |
| 3 | M3: 清理與收斂專案根目錄腳本 | 遷移 _archive 網格腳本至 examples/mesh_debug/ | none | DONE |
| 4 | M4: 全專案 pytest 100% 驗收與終審 | 測試路徑修復、全域 pytest 執行、三方客觀審核 | M1, M2, M3 | DONE |

## Interface Contracts
### Mechanical Controller SSOT
- 模組路徑：`ansys_unified_mcp.products.mechanical.facade`
- 公開符號：`MechanicalController`, `controller`, `PRODUCT`, `_esc`, `DEFAULT_SCRIPT_TIMEOUT`
- 外部相容層：`ansys_unified_mcp.products.mechanical.__init__` 保留轉發導出。

### Agent Skills Directory Structure
- 規範依據：`agentskills.io`
- 命名規範：`skills/<skill-name>/SKILL.md`，frontmatter `name: <skill-name>` 必須完全相符。
- 目錄規範：`skills/<skill-name>/references/`（複數）、`skills/<skill-name>/scripts/`。

### Root Scripts Scope
- `scripts/deploy/act_plugins/`：保留 ACT 外掛發布資產。
- `scripts/maintenance/`：保留專案級合規審核與環境設定腳本。
- `examples/mesh_debug/`：收納伺服器機箱網格除錯特定歷史腳本。
