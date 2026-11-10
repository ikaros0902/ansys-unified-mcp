# ANSYS 文件庫維護

沿用 `docs/ANSYS_Document/<產品>/<版本>/<分類>`，SDK 文件另放 `sdk/<套件>/<SDK版本>`。版本未知時使用 `unknown`，不得把 `stable` 當精確版本。產品與 SDK 的發布版本互不推定。

## 可重跑命令

```powershell
# 預設 dry-run，不下載、不修改語料
.venv\Scripts\python.exe scripts\maintenance\sync_ansys_documents.py sync

# 下載清單中的官方核心文件；失敗、登入限制及頁數上限均留在清冊
.venv\Scripts\python.exe scripts\maintenance\sync_ansys_documents.py sync --apply

# 先只補特定產品；可重複 --product
.venv\Scripts\python.exe scripts\maintenance\sync_ansys_documents.py sync --apply --product fluent --product mapdl

# 文件搬移完成後，重建清冊、覆蓋表與各產品 README
.venv\Scripts\python.exe scripts\maintenance\sync_ansys_documents.py catalog --apply

# 只重掃指定產品；既有清冊中的其他產品列會保留
.venv\Scripts\python.exe scripts\maintenance\sync_ansys_documents.py catalog --apply --product spaceclaim --product mechanical

# 使用既有 Codex PDF runtime 擷取文字，保留頁碼；原始 PDF 不變
.venv\Scripts\python.exe scripts\maintenance\sync_ansys_documents.py catalog --apply --extract-pdf

# 只轉指定 PDF；路徑相對於 --root，可重複指定
.venv\Scripts\python.exe scripts\maintenance\sync_ansys_documents.py catalog --apply --extract-pdf --pdf-path LS-DYNA/v252/manuals/LS-Run_Users_Guide.pdf --pdf-path LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf

# 建立/重建全文索引；完成後只印索引統計，避免輸出整份文件清單
.venv\Scripts\python.exe -c "from ansys_unified_mcp.analytics.docsearch.index import build_index; r=build_index(); print({k:r[k] for k in ('indexed_count','chunk_count','catalog_indexed_count','catalog_content_count','catalog_verified_source_count')})"
```

使用 `--root` 可指定文件庫；`--sources` 可指定來源清單。`--max-pages` 是每個 SDK／產品入口每輪的核心頁面上限，預設 30；超額仍有候選時記為 `partial`，不稱全站鏡像。`--workers` 預設 4，最多 8。`--pdf-path` 可重複指定只擷取個別 PDF，路徑相對於文件根目錄且不可與 `--pdf-limit` 併用；未指定時 `--pdf-limit` 限制排序後擷取數量，0 表示全部。`--pdf-python` 可改用另一個已安裝 `pypdf` 的 Python。

`catalog --product` 只掃描所選產品目錄，並沿用既有清冊中其他產品的列；不帶 `--product` 則重建全庫清冊。

## 來源與資料保護

- 可版控的官方來源入口在 `src/ansys_unified_mcp/resources/manifests/document_sources.json`。官方 ACT 頁面明列的 2025 R1、2025 R2、2026 R1 API／範例壓縮包分版本保存；其他版本只追產品入口與 previous 頁實際列出的連結。
- 只接受官方 PyAnsys、ANSYS Help、Ansys Storage、Developer Portal 及 `ansys` GitHub 組織。401／403 列為受阻，404／DNS／格式錯誤列為失敗，不繞過登入。
- HTML 擷取 `main/article/role=main` 或正文 body，不把首頁導覽、未展開的 Sphinx RST／Jinja 模板當作完整文件；ACT 超過 10 MB 的巨型 `index.html` 保留原件，列為附件。
- ZIP 解壓前驗證路徑、符號連結與總大小；不執行任何下載的程式或求解範例。
- 同路徑不同內容以內容摘要另存，不覆蓋舊檔。既有清冊的 `ok` 與舊 D 槽路徑不是完成證據。
- 重建產品 README 前先將舊內容保存至 `_catalog/readme_backups/`；來源、大小與雜湊則保存於清冊。

## 清冊與覆蓋表

- `_catalog/downloads.json`：各官方 URL 的結果、相對路徑、雜湊、SDK 版本證據與失敗原因。
- `_catalog/documents.json`：穩定文件 ID、產品 release、SDK 套件／版本、分類、來源 URL、原檔 `path`、正文 `text_path`、SHA-256 與品質。
- `_catalog/coverage.json`：每產品／版本的現有正文、類別缺口、失敗來源。`not_verified` 表示該 release 的官方可用性尚未確認，不表示官方發行過。
- `_catalog/pdf_extraction.json`：PDF 文字擷取結果與同目錄 Markdown 路徑。缺少 `.md` 時由頁碼文字快取建立；既有且內容不同的 `.md` 不覆寫，索引繼續使用帶頁碼的抽取快取並在清冊標示差異。掃描圖檔或加密 PDF 無可用文字時保留待補，不自動執行 OCR。
- `_catalog/relocations.json`：由整理程序提供的 `moves` 陣列，包含相對 `original_path/new_path`、可信 `release/source_url`；清冊建立器沿用這些證據。

文件 ID 依產品、版本、SDK 與原文內容雜湊產生，不依電腦或檔案絕對路徑。相同內容的搬移保留 ID；正文修訂使用新 ID。只有 `quality=body_present` 的文件送入全文索引。

搜尋快取以 `_catalog/documents.json` 的修改時間與大小判斷是否更新，不會每次查詢逐檔掃描整個文件庫。直接改動來源原件後，先重跑 `catalog --apply`，再查詢或明確呼叫 `build_index()`；索引建置會按每個來源路徑核對 SHA-256，完成 SQLite 完整性檢查後才原子切換。相同正文只存一份 FTS chunks，搜尋結果仍保留各產品／版本／SDK 的來源別名。

範例只下載最多三個代表頁面及明示的下載附件。若輸入檔由 `download_file` 等執行期函式組合路徑，標記 `input_pending`，不能宣稱已成為完整離線案例。下載與索引成功也不代表物理求解驗收。

官方入口：[ACT 開發資源](https://storage.ansys.com/api-a/devresources.html)、[PyAnsys 產品目錄](https://docs.pyansys.com/version/stable/projects.html)。
