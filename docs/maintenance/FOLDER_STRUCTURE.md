# 目錄分工與文件維護

## GitHub 正式目錄

```text
agents/   模組分類的技能，每項技能以 SKILL.md 為入口
src/      可安裝套件、正式程式碼與 resources/manifests/
scripts/  API 擷取、文件同步、治理與驗證工具
tests/    單元、整合、端到端、評測及測試資料
docs/     架構、API 字典、指南、操作文件與維護紀錄
```

GitHub 根目錄只保留以上五個正式資料目錄。ANSYS 官方文件原件、清理後語料、索引與執行資料位於本機忽略目錄。README、pyproject.toml、鎖定檔與相容啟動入口 `mcp_server.py` 留在根目錄；安裝與操作文件集中於 `docs/deployment/`。

本機可能有被 Git 忽略的 `agents/skills-workspace/`，用於技能開發評測與工作輸出；它不屬於可發布的技能目錄，也不列入 GitHub 正式樹。其他文件庫、快取與執行輸出同樣留在各自忽略路徑，不因實體目錄鄰近正式根目錄而納入版本控制。

## `docs/` 子目錄

| 路徑 | 保存內容 |
|---|---|
| `docs/api_inventory/` | API 快照、覆蓋清冊與人讀字典 |
| `docs/architecture/` | 現行系統架構說明 |
| `docs/archive/` | 明確標示為歷史快照的舊計畫、規格與交付紀錄 |
| `docs/deployment/` | 現行安裝與部署 SOP |
| `docs/examples/` | 可讀取或執行的產品範例與相容入口 |
| `docs/maintenance/` | 文件庫維護、來源清冊、資料夾地圖與清理紀錄 |
| `docs/planning/` | 正在執行的專案計畫 |
| `docs/reviews/` | 時間戳記的稽核發現與決策證據；不作現行操作指令 |
| `docs/skills/` | 技能共用的產品來源與支援邊界矩陣 |
| `docs/testing/` | 測試分層與執行規範；測試程式在 `tests/` |

`docs/archive/` 和 `docs/reviews/` 都保留過往資料，但前者是已封存的內容快照，後者是審查證據；`docs/maintenance/` 和 `docs/planning/` 分別維護現況操作知識與待辦決策，不互相複製。

## 資源責任

`agents/skills/<module>/<skill>/` 依模組分類。每個技能包含 `SKILL.md`，並只保留實際使用的 `references/`、`scripts/`、`assets/` 與 `evals/`。`skill_tiers.json` 已移除。2026-10-28 清掉 31 個只含通用說明的資源 README 與 41 個空 `assets/`／`references/` 目錄；備份檔雜湊及移除路徑記在本機忽略路徑 `.runtime/folder-tree-reorganization/empty-skill-resource-backup/manifest.json`，沒有移除技能指令或實際資產。

`headless_skill_evaluator.py` 仍接受舊 `agents/skills-tier2/<skill>/` 輸入，並將它解析到目前 `agents/skills/<module>/<skill>/`。這是呼叫相容路徑，不是技能儲存目錄；新引用應直接使用模組路徑。

`src/ansys_unified_mcp/resources/manifests/` 保存套件執行期使用的權限、DAMG 與官方文件來源設定。`tests/evaluations/` 保存 MCP 評測執行器、案例與結果。文件索引位於 `docs/index.md`。

`tests/` 保留隔離測試、整合／端到端案例、評測輸入與共用 fixtures。保留測試目錄不要求每次工作執行全套測試；按變更範圍選擇性執行的原則見 [`docs/testing/TEST_INFRA.md`](../testing/TEST_INFRA.md)。

`src/` 不存放本機文件索引或語料。2026-10-28 將殘留於 `src/Documentation_clean/` 的舊 57,344-byte APIKB SQLite 檔移至忽略目錄 `.runtime/api-rag/legacy-src-api_kb-20261009.sqlite`；原檔以 SHA-256 確認搬移前後一致，未刪除。

技能依模組整理於 `agents/skills/<module>/<skill>/`。44 個技能搬移時的來源與目的路徑、搬移前 SHA-256 與大小見[技能搬移清單](SKILL_MIGRATION_MAP.json)；該清單記錄搬移事件，不代表每列資源都仍在目前目錄。其後資源清理的備份見本機忽略路徑 `.runtime/folder-tree-reorganization/empty-skill-resource-backup/manifest.json`。34 個舊 tier 技能原件備份於 `.runtime/folder-tree-reorganization/skill-root-migration/originals/`；10 個 domain router 以搬移前 Git HEAD 記錄。

根目錄評測、manifests、報告及技能治理工具的舊路徑、搬移前 SHA-256 與目前目的位置見[根目錄搬移清單](ROOT_REORGANIZATION_MAP.json)。清單中的雜湊只描述搬移前 Git 版本，不代表目的檔已比對。

技能連結治理工具位於 `scripts/skill_governance/`；`setup_skill_links.py` 是唯一實作，`setup_skill_junctions.py` 僅保留舊命令相容入口。Root-level `mcp_server.py` 是已文件化的舊客戶端相容入口，實作委派至 `src/ansys_unified_mcp/__main__.py`。

`src/` 內的 `core/`、`products/`、`analytics/`、`bridges/`、`tools/`、`workflows/` 和 `workers/` 各自負責執行基礎、產品介面、查詢分析、傳輸、工具註冊、流程與工作執行。`drivers/` 提供共用介面與既有匯入相容路徑；產品 driver 保留於 `products/<product>/`。名稱相近不代表職責相同，合併前須檢查呼叫端和套件資源載入方式。

## 相似命名目錄的邊界

- `agents/skills/<module>/<skill>/scripts/` 是技能專用資產；`scripts/api_extraction/`、`maintenance/`、`skill_governance/` 與 `verification/` 是維護整個 repo 的工具，各自處理 API 擷取、工作區／文件維護、技能治理與 repo 檢查。對兩個根內 130 個 Python／PowerShell／批次腳本做 SHA-256 對照，沒有完全相同的跨根副本；未因此合併用途不同的腳本。
- 技能內的 `evals/` 隸屬單一技能；`tests/evaluations/` 保存 MCP 專案級評測執行器與案例。其名稱相似，但輸入、執行方式與責任範圍不同。
- `docs/examples/` 說明範例工作流；`agents/skills/` 保存可路由的工作指引。PCB warpage 範例中的 Python 檔是相容入口，實作集中在 `pcb-warpage-analysis` 技能的 `scripts/`，保留入口以免範例使用者改變呼叫方式。兩邊 402 個目前檔案的 SHA-256 對照只找到三個範例入口共用相同 wrapper 內容；入口依自身 basename 對應 canonical skill script，屬刻意保留的相容殼，不是重複實作。此摘要不代表語意近似內容已全數排除。
- `docs/skills/DOMAIN_SOURCE_AND_SUPPORT.md` 是多個技能共用的來源／支援邊界矩陣，不是另一套技能入口；矩陣路徑須指向現行模組分類，語料位置以 `ANSYS_DOCS_ROOT` 表示。`docs/testing/TEST_INFRA.md` 記錄測試規範，實際評測與測試案例分別由 `tests/evaluations/` 和其他 `tests/` 子目錄持有。
- `docs/archive/` 保存已標示的歷史快照；`docs/reviews/` 保存曾發現的問題與決策證據。歷史文件中的舊路徑是稽核證據，不當作現行操作入口。
- `docs/api_inventory/` 保存來源快照、覆蓋清冊與人工整理字典；`src/ansys_unified_mcp/analytics/apikb/` 和 `analytics/docsearch/` 是套件內的檢索與索引程式。資料與程式分開維護，不把 API 快照或本機索引搬入安裝套件。
- Dyna、Icepak 與 `products/multiphysics/` 的目錄形狀不同，分別承載產品工具／driver、產品 driver，以及跨產品橋接；目前的呼叫端不同，不以一致目錄外觀為由合併。

舊 `agents/skills-tier2/` 只殘留的本機 `.zvec-grep/` 快取已移至被忽略的 `.runtime/folder-tree-reorganization/archived-caches/skills-tier2-zvec-grep/` 保留；根目錄 `.zvec-grep/` 也列為本機索引快取，不納入 GitHub。

本機 ANSYS 語料、索引、執行輸出與 Python 套件建置產物（例如根目錄 `dist/`）保留於工作樹並由 `.gitignore` 排除；不納入 GitHub 正式目錄清單。`agents/skills-workspace/` 是本機 Skill-Creator 評測工作區，保存 `with_skill/`／`without_skill/` 的比較結果；相同 JSON 結果也可能因案例而重複，保留原狀且不列入 GitHub 技能樹。

## 維護規則

- API 擷取器寫入有版本與來源證據的快照；APIKB 和 docsearch 提供檢索，不負責擷取 SDK。
- 官方文件原件保留在本機語料庫。GitHub 僅發布可分享的字典、索引與衍生內容。
- 移動檔案前檢查引用與雜湊；更新呼叫端後執行相關測試。刪除前保存可還原副本。
- `scripts/verification/verify_directory_topology.py` 驗證五個正式根目錄及 runtime 忽略規則。
