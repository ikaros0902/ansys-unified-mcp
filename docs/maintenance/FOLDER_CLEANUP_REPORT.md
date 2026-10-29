# 工作區與 ANSYS 文件庫整理結果

## 目錄整理

- 2026-10-28 續查 `docs/` 的 Markdown／HTML／RST／TXT 正文副本，對 48 個現存檔案計算 SHA-256，沒有完全相同的文件群，因此未再刪除文件。這不涵蓋語意近似、PDF 二進位內容或被 Git 忽略的 ANSYS 文件庫。
- 2026-10-28 清理技能遷移後的資源佔位：備份 31 個只含通用標題／空泛用途的 `assets/README.md` 與 `references/README.md`，SHA-256 清單在被忽略的 `.runtime/folder-tree-reorganization/empty-skill-resource-backup/manifest.json`；移除共 41 個空目錄（32 個 `assets/`、9 個 `references/`；其中 10 個原本為空，其餘由 README 移除後變空）。獨立 reviewer 以 SHA-256／bytes 比對確認 31 份備份相符，並核對 44 份 SKILL.md 仍存在、無文件直接連到刪除的 README。沒有移除 SKILL.md、實際 reference、script、asset 或 eval 資料。原始技能搬移清單保留作為歷史遷移證據。
- 2026-10-28 將 `src/Documentation_clean/api_kb.sqlite`（57,344 bytes，2026-10-09 更新）移至忽略目錄 `.runtime/api-rag/legacy-src-api_kb-20261009.sqlite`。全 repo 來源搜尋未找到對 `src/Documentation_clean/` 的路徑引用；搬移前後 SHA-256 均為 `0AED937DA91C9CB797807756D615A1CA94FCC5A47BFB7D9942BB717ECF049ED4`。保留舊索引，未刪除。

- 將 22,987 個檔案歸位到 `docs/architecture`、`docs/examples`、`docs/maintenance`、`tests/evaluations/reports` 等既有分層；修復文件連結及現行技能／操作引用。
- 第一輪移除 10 份已確認完全相同的 TwinAI、SCADE 與 SpaceClaim legacy Style Guide 副本。之後盤點又發現 7 份 SpaceClaim「Developers Guide_V232/V241/V242/V251/V252/V261/V271」SHA-256 完全相同，封面內容均是 2021 年 API V23 Beta；保留一份並把版本標成 `unknown`。
- 合計移除 16 份正式目錄副本、32,290,389 bytes。其餘版本不同或內容不同的檔案保留。另存的來源備份仍在磁碟，因此不代表目前淨釋出相同容量。
- 新增副本備份記錄：`.runtime/folder-document-cleanup/additional-duplicate-removals.json`。搬移與第一輪備份索引見 `.runtime/folder-document-cleanup/relocations.json`；備份根目錄為 `.runtime/folder-document-cleanup/originals/`。
- 原始全面驗證涵蓋 22,997 個搬移／去重操作、45,984 個備份與目的檔雜湊，0 項不一致。後續 6 份 SpaceClaim 副本亦逐份先複製、驗證 SHA-256 再移除。

目錄職責、一般程式常見分層、維護命令及回復步驟見 [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md)。

## ANSYS 文件庫

- 最終清冊有 **424,962** 筆文件：424,567 筆正文、356 筆附件、38 筆模板、1 份待抽取 PDF。ID 無重複，文件 ID 不含絕對路徑。
- 覆蓋表有 128 個已觀察的產品／版本列；狀態仍以 `partial` 為主，不把入口或未驗證版本宣稱完整。
- 來源清冊目前記錄 2,206 筆下載成功、34 筆受頁數上限限制、28 筆失敗、2 筆受登入／權限限制。失敗及受阻原因保留在 `ANSYS_Document/_catalog/downloads.json`。
- ACT 官方參考包已按 2025 R1 (`v251`)、2025 R2 (`v252`) 與 2026 R1 (`v261`) 分版保存。三版 coverage 均為 partial；v251/v252 尚缺 guide 與可離線教程輸入，v261 尚缺可離線教程輸入。SpaceClaim、CFX、MAPDL 的 v251/v261 也只有部分官方手冊／參考內容，依 coverage 表列出缺口。
- PDF 清冊目前有 268 份成功抽取、1 份失敗。唯一失敗是 `Speos/unknown/manuals/RAL DESIGN StandardRGB (RGB).pdf`（1 頁掃描件，12,329,990 bytes，清冊 ID `ansys_c0335fbc1d4d28c0748604f1`，SHA-256 `f9e445f8e361358886b15546c8cb2ffdd3d72ba9840508d598100985d4dc9429`），沒有可抽取文字。現有環境沒有 OCR 引擎；未安裝或執行 OCR，原件保留。
- 為避免把 28–29 MB 的 ACT `Mechanical/index.html` 目錄頁誤當文件正文，保留三個原件並標為附件；一般 API 類別頁（包含 122–147 KB 的 DataModelObject、ANSYSAnalysisSettings、IFolderDataModelObject）仍納入正文索引。
- SpaceClaim `Developers Guide_V271.pdf` 封面實際標示 API V23 Beta（2021），不是可證實的 2027 R1；已移到 `unknown` 版本語義並與六個完全相同副本去重。

產品版本與缺口細節以本機忽略的 `ANSYS_Document/INDEX.md` 及 `_catalog/coverage.json` 為準。這些檔案不隨 GitHub 文件發布。`partial`、`not_verified`、`input_pending` 均保留，不等於已完成官方全站鏡像或離線案例驗收。

## 搜尋索引

搜尋介面保留舊參數並增加 `product`、`release`、`category`、`sdk_version` 篩選。相同正文只建立一組 FTS chunks，`docs_meta` 保留每個來源的產品、版本與 SDK alias；`search` 與 `get_chunk` 仍以命中的 alias 回傳正確來源。

清冊變更後才重建索引。平常搜尋只檢查清冊檔的修改時間與大小，不逐次重掃 42 萬個原件；直接修改原件後須先重跑 `catalog --apply`，再查詢或明確呼叫 `build_index()`。建置會逐來源路徑核對 SHA-256，並在 SQLite 完整性檢查通過後才切換索引。本次索引有 **424,567** 筆清冊文件、**424,603** 個來源 alias、**174,713** 組全索引唯一正文（其中清冊正文 **174,677** 組，另含 36 組 curated API 正文）、**381,262** 個 FTS chunks；SQLite `integrity_check` 結果為 `ok`。ACT v251/v261、SpaceClaim v251、CFX v261、MAPDL v251 與 Fluent SDK `ansys-fluent-core 0.42.1` 的代表查詢均通過產品／版本／分類／SDK 篩選，且可用命中 alias 取回正文。

## 根目錄 runtime 歸位（2026-10-28）

根目錄的 `logs/` 與 `workbench_queue/` 已歸位到 `.runtime/logs/`、`.runtime/queue/`。同名但內容不同的舊 queue 日誌另存於 `.runtime/logs/legacy-workbench-queue-20261028/`；registry 檔案未覆蓋既有記錄。ACT 預設 queue path、preflight、README 與部署 SOP 均指向 `.runtime/queue/`；明確 queue 環境變數仍可覆寫。現有 ANSYS ACT 安裝副本未更新。

## 維護與限制

```powershell
# 只查看搬移計畫
.venv\Scripts\python.exe scripts\maintenance\reorganize_workspace.py --corpus

# 更新官方文件；DNS/404/權限及頁數限制會保留為清冊狀態
.venv\Scripts\python.exe scripts\maintenance\sync_ansys_documents.py sync --apply

# 擷取 PDF 正文並重建文件清冊、版本覆蓋表及產品索引
.venv\Scripts\python.exe scripts\maintenance\sync_ansys_documents.py catalog --apply --extract-pdf --pdf-python <既有 PDF runtime>
```

本次沒有執行 ANSYS 求解，也沒有 commit/push。來源備份未清除；目錄整理不會自動釋放等量磁碟空間。完整可重跑命令與編碼／清冊更新規則見 [ANSYS_DOCUMENT_MAINTENANCE.md](ANSYS_DOCUMENT_MAINTENANCE.md)。
