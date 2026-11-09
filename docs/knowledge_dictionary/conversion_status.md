# 第一批 PDF／HTML 轉換核對

核對日期：2026-10-29。全庫清冊輸出核對及第一批官方頁面同步後更新。原始 PDF／HTML 未被覆寫。

| 既有產品手冊目錄（官方網站同步前） | PDF 來源 | PDF 正文 | HTML 來源 | 同名 Markdown 有正文 |
|---|---:|---:|---:|---:|
| SpaceClaim | 4 | 4 | 0 | 不適用 |
| Mechanical | 2 | 2 | 67 | 67 |
| LS-DYNA | 3 | 3 | 35 | 35 |
| optiSLang | 2 | 2 | 45 | 45 |

SpaceClaim 的 PDF 清冊另有一筆 `Developers Guide_V232.pdf` 標記為 `deduplicated`，清冊指出保留版本位於 `Discovery/unknown/manuals/Developers Guide_V232.pdf`。原 SpaceClaim 路徑目前不存在，保留的 PDF 文字快取仍存在。四個產品目錄內共 11 個現存 PDF 均有超過 100 字的抽取正文，且來源 SHA-256 與清冊相符；去重項另保留抽取文字快取。

Mechanical、LS-DYNA、optiSLang 的 147 個 HTML 都有同目錄 Markdown，且每份 Markdown 正文至少 100 字。HTML 來源另有 147 筆同名 `.md` 檔；這份核對證明輸出存在且非空，不等同人工逐頁核對圖片、表格或技術內容。

更正：本表依原始資料夾名稱統計 PDF；`optiSLang/unknown/manuals` 內的兩份 `lsopt_2026R1_*.pdf` 內文標示 LS-OPT Version 2026 R1，並非 optiSLang。後續產品清冊與 RAG 索引已將這兩份文件改列 `general`，因此 optiSLang 的官方 PDF 手冊覆蓋目前為 0；PDF 檔及同名 Markdown 仍留在原位置。

全庫 HTML 清冊的 23,254 筆轉換項目已逐項檢查：23,253 個 Markdown 輸出存在、非空且 SHA-256 與清冊相符；唯一失敗是 0-byte HTML，對應說明 Markdown 存在且已註明沒有正文可轉。清冊記錄 424,158 個 HTML：400,904 筆沿用既有 Markdown、23,209 筆新轉換、44 筆純文字 fallback、1 筆 0-byte 失敗。沿用既有 Markdown 的 400,904 筆未納入本次逐項雜湊核對。

PDF 清冊共 269 筆：258 筆抽取、10 筆去重、1 筆掃描來源失敗。258 份抽取輸出均存在且至少 100 字；來源檔仍存在的項目均通過 SHA-256 核對。10 筆去重保留共用內容；1 筆 RAL 掃描色票保留 PDF、頁面圖像和有缺口說明的 Markdown，OCR 不可靠，因此沒有把錯誤辨識文字當成正文。

本次同步及補抓後，清冊記錄 SpaceClaim 2、Mechanical 119、LS-DYNA 163、optiSLang 813 筆下載成功。其中新增/同步的 HTML 數為 Mechanical 117、LS-DYNA 163、optiSLang 557；每頁均產生對應 Markdown。optislang 另有 256 筆來源本身是 Markdown。SpaceClaim 兩筆為 PDF，正文由 PDF extraction 清冊追蹤。逐筆核對顯示下載來源檔與對應 Markdown 均存在，正文至少 100 字，來源檔雜湊均相符。第一批四產品目前沒有 `failed`、`blocked` 或 `partial` 頁面。官方同步器追蹤並處理了入口頁可到達的連結；這不等於文件站所有頁面均已鏡像。optiSLang Portal crawl state 目前已無待抓佇列。詳細狀態見 `_catalog/downloads.json` 與 `_catalog/portal_crawl_optislang.json`。

清冊與索引：已使用指定產品模式更新 SpaceClaim、Mechanical、LS-DYNA、optiSLang 的文件清冊，並保留其他產品舊清冊列。更新後全庫清冊有 449,147 筆，包含 448,794 筆 `body_present`、314 筆附件及 39 筆範本內容；覆蓋表有 127 列。`sources.csv` 現有 3,382 列，其中 972 筆新增正文已標記為已索引。索引以增量方式更新：四產品新增 972 列、更新 2,222 個既有別名、移除 46 個過時別名；另納入 6 份知識字典 Markdown 及 PDF 章節索引。正式 `docs_index.sqlite` 有 449,023 筆 `docs_meta`、446,216 個 FTS 片段及 448,794 筆清冊正文別名；`PRAGMA integrity_check` 結果為 `ok`。SpaceClaim、Mechanical、LS-DYNA、optiSLang 均已實際搜尋並取回片段，結果含可追溯的本機路徑或來源網址。未變動產品沿用原有已索引內容，完整來源指紋需全庫重建時重算。回復副本保留於 `Documentation_clean/docs_index.sqlite.backup_general_20261029_215632`。更新方式與命令見 [文件維護手冊](../maintenance/ANSYS_DOCUMENT_MAINTENANCE.md)。

限制：SpaceClaim 目錄本身沒有 HTML；SpaceClaim 技能資料夾中的 Markdown 不列為 HTML 轉換輸出。HTML manifest 依轉換來源位置記錄，無法單靠該 manifest 將全庫每筆 HTML 映射到產品。掃描 PDF 的 OCR、影像內容、表格結構與圖表語意仍需人工檢查；本次未重新執行 OCR。

## 2026-10-30 後續核對

本次接續檢查全庫轉換清冊，沒有重轉或覆寫 PDF／HTML 原檔。HTML 清冊目前記錄 560,810 個 HTML，其中 560,764 個有可用 Markdown／文字內容；累計 158,922 筆轉換、44 筆純文字 fallback、47 筆失敗。這 47 筆包括前述 0-byte 頁及 ACT v261 的 46 頁；ACT 失敗頁因正文不足或無法可靠解析而保留失敗記錄，沒有用空白或猜測內容代替。

ACT v261 的新增解壓目錄有 135,715 個 HTML：135,669 頁轉換成功，46 頁失敗。成功頁均有 Markdown 輸出及官方 `ACTReferenceHTML.zip` 成員網址，並已更新輸出 SHA-256。134,769 頁的 HTML 雜湊與既有 ACT 文件清冊中的 canonical 頁面一致；其餘 900 頁則以兩個本機 canonical HTML 檔逐檔 SHA-256 相符後記錄網址。這批是既有封存文件的重複解壓路徑，不另建立重複的 RAG 文件項目。ACT 網址與對照結果記錄於 `_catalog/html_conversion_manifest.json` 的 `last_act_provenance_repair` 及各筆轉換項目。

PDF 清冊仍為 269 筆：258 筆抽取、10 筆去重、1 筆掃描色票失敗；未執行 OCR。原 PDF 保留不動。

正式全文索引未因重複 ACT 解壓路徑而重建。核對 `docs_index.sqlite` 得到 449,272 筆 `docs_meta`、446,730 個 FTS 片段、449,043 筆清冊正文，`PRAGMA integrity_check` 為 `ok`；文件清冊版本與索引記錄的清冊大小及修改時間一致。這表示既有 canonical ACT 正文仍由目前索引提供搜尋；900 筆品質不足或未列入正文清冊的 canonical 對照頁不因此宣稱已收錄為 RAG 正文。

尚未逐頁人工檢查新增 ACT 內容的表格、圖片與技術正確性；46 筆正文不足頁及 1 筆掃描 PDF 仍是明確缺口。

## 2026-10-30 全庫同步與轉換續查

將官方 SDK 網站抓取上限提高至每入口 1,000 頁後，下載清冊累計 6,736 筆：6,554 筆成功、172 筆失敗、8 筆部分完成、2 筆因 401／403 等限制受阻。每筆已下載 HTML 都有 Markdown 與相符的 `source_url`；本輪核對 4,967 筆下載 HTML，均有原檔及 Markdown。下載、頁面轉換與失敗原因見 `_catalog/downloads.json`。

全庫重新盤點得到 564,325 個 HTML，564,279 個有非空 Markdown 或清冊正文，尚有 46 個未覆蓋頁；皆為 ACT v261 正文不足或解析失敗頁。清冊已納入本輪 3,471 筆新來源候選，正式 FTS 索引新增 3,591 個文件別名、移除 44 個過期別名。索引目前有 452,819 筆 `docs_meta`、460,348 個 FTS 片段及 452,590 個清冊正文別名；SQLite 完整性檢查為 `ok`。新收錄的 ACP `InterpolationOptions` 頁面已實際搜尋並取回片段，來源路徑與官方網址均可追溯。

全庫 PDF 抽取再次核對：258 筆抽取成功且 Markdown 存在、10 筆內容去重、1 筆 Speos RAL 掃描色票無可用文字。未執行 OCR；該 PDF 保留原件並標為待處理。

同步器處理 SDK 頁面與清冊後，重新解壓既有 ACT 壓縮包時發現它會逐檔重寫相同內容，因此中止該重複步驟；原始 ZIP 保留，並抽查已寫入檔案的大小均與 ZIP 成員相符。之後改以非 ACT 產品來源續抓，並成功下載及抽取 10 份明列 PDF。完整網站鏡像仍受 DNS／404 失敗與權限限制影響。

## 2026-10-30 最新盤點

續抓 Fluent、DPF、AEDT 待處理頁後，全庫 HTML 實掃為 570,666 個；目前全部連到非空 Markdown 或清冊正文。46 個 ACT v261 重複解壓頁已逐一核對原始 SHA-256，並重用相同內容的 canonical Markdown；沒有再產生重複文件。官方 SDK 下載清冊內 11,308 個 HTML 均有 Markdown、匹配來源網址，且原始 HTML SHA-256 與下載清冊相符；這些頁面已加入 HTML 轉換明細。轉換明細現有 170,277 筆：170,186 筆轉換、44 筆純文字 fallback、46 筆重用既有 Markdown、1 筆舊失敗記錄。

官方來源同步清冊現有 13,069 筆有效狀態：12,895 筆下載成功、172 筆失敗、2 筆 403 受阻。失敗以 DNS／404 為主。兩筆 MAPDL／CFX 的舊頁數佇列已由後續同步處理，從當前狀態移至 `downloads.json` 的 `resolved_progress` 歷史。

明列的 10 份 SpaceClaim、CFX、MAPDL PDF 均有逐頁 Markdown 及來源清冊；PDF 抽取清冊當時共 269 筆（258 抽取、10 去重、1 掃描失敗）。全庫文件清冊當時有 459,321 筆，其中 458,931 筆正文、338 筆附件、51 筆範本及 1 筆 PDF 待抽取；全文索引當時有 459,160 筆中繼資料及 473,558 個片段。`PRAGMA integrity_check` 為 `ok`。已實際搜尋 CFX v261 PDF 與 AEDT SDK 頁面並取回來源片段。

剩餘限制：172 個官方網址仍下載失敗、2 個 Synopsys 頁面回覆 403。唯一 HTML 失敗項是 ACT v261 的 0-byte HTML；原始空檔保留，旁邊的 Markdown 明確記錄無正文可轉。Speos RAL 掃描 PDF 的文字抽取失敗，但原 PDF、單頁影像及說明 Markdown 均保留；不把未辨識的色值加入搜尋正文。為避免同步器重複寫入數十萬個相同 ACT 檔案，本輪未重新解壓官方 ZIP；原 ZIP、canonical HTML 與可重用 Markdown 均保留。


## 2026-10-30 PDF／HTML 轉換與索引更新

第一批四產品 Markdown 來源共盤點 2,230 個不同網址；官方文件頁、素材、需登入頁、權限不明測試主機及第三方來源均記於 [markdown_links.csv](markdown_links.csv)。本輪新增下載並轉換 129 個官方技術文件網址；另修正一個先前已下載但被誤判成模板的 PyDYNA 原始碼頁。未知版本維持 unknown，不由 SDK 版本推定 solver release。

HTML 全庫清冊有 570,796 個原始 HTML，570,796 個可對應 Markdown 或有來源說明的 Markdown 項目。轉換明細 170,407 筆：170,316 筆轉換、44 筆純文字 fallback、46 筆重用既有 Markdown、1 筆 0-byte HTML 失敗。PyDYNA `field_writer.html` 已從原 HTML 的語法高亮程式碼區塊轉為 Markdown；`{{...}}` 出現在合法 Python f-string 中，不是未展開頁面模板。剩餘 0-byte 頁沒有正文，旁側 Markdown 保留原因。

PDF 清冊原有 269 筆：258 筆抽取、10 筆去重、1 筆掃描色票待 OCR；原 PDF 保留。R16 LS-DYNA 三冊先前因公式大括號被誤判模板，已改列為可用正文並納入索引。

新增外連網址中，5 個 LS-DYNA Knowledge Base 路徑及 1 個 Synopsys optiSLang API 頁回覆 404；20 個登入保護頁標為 `access_restricted_auth_required`，6 個測試主機頁列為權限不明，66 個第三方來源只列清冊。全體同步器清冊目前有 13,029 筆下載、178 筆失敗及 2 筆受阻；失敗項沒有被當作成功正文。官方 LS-Run v251、v252、v261 與 LS-PrePost v261 手冊現均下載完成；4 份 PDF 都有帶 PDF 頁碼標記的同目錄 Markdown，並已納入全文索引。

全量文件清冊目前 595,129 筆：594,742 筆正文、383 筆附件、3 筆模板及 1 筆 PDF 待抽取。正式 `docs_index.sqlite` 有 594,971 筆文件中繼資料、631,021 個 FTS 片段；本次新增來源均核對 PDF SHA-256，`PRAGMA integrity_check` 為 `ok`。本次修正兩筆 LS-OPT 產品標籤並增量重索引 6 份字典 Markdown；另逐段對照 SpaceClaim v251 與 v261，6 個主題已標為 complete，並在 Combine 主題標出 v261 新增 tolerance 步驟。SpaceClaim `Pull tool` 回到 v261 PDF；Mechanical `IMechanicalExtAPI` 回到 v261 scripting API 頁；LS-DYNA `FieldSchema` 回到 PyDYNA 0.12.1 API 頁，`PARMAXcomputed` 可回到 R16 PDF；optiSLang `sensitivity` 回到官方範例頁。搜尋與片段擷取均成功並保留來源路徑／網址。

`topics.csv` 的 23 個主題仍標為 `draft`，尚未逐版本人工核對。PDF/HTML 表格、圖表及圖片語意未逐頁驗收；Speos RAL 掃描色票仍待 OCR。

### 2026-10-30 PDF sidecar 與產品歸屬複核

四產品目錄中現存 11 份 PDF：8 份缺少同目錄 Markdown，已由雜湊相符的逐頁 PDF 文字快取建立 sidecar；另 3 份原有 Markdown 與快取文字不同，均保留原檔，索引繼續使用已核對的逐頁快取。SpaceClaim 一筆不存在的重複 PDF 路徑不建立虛構輸出；原始 PDF 未改寫。Speos RAL 掃描色票仍無可靠文字，未執行 OCR。

`optiSLang/unknown/manuals` 的兩份 `lsopt_2026R1_*.pdf` 內文明確標示 LS-OPT Version 2026 R1。它們已從 optiSLang 產品結果中排除，產品清冊與 SQLite 中繼資料標為 `general`；正文片段及原始 PDF／Markdown 保留。官方 optiSLang 使用者手冊仍是來源缺口。


### 2026-10-30 LS-Run／LS-PrePost PDF 轉換

官方 LS-Run v251、v252、v261 及 LS-PrePost v261 共 4 份 PDF 已下載並保留原檔。依 PDF 抽取清冊產生 4 份逐頁 Markdown sidecar：LS-Run 各 22 頁；LS-PrePost 1,070 頁。每筆抽取來源均保留 PDF SHA-256 與 Markdown 路徑；正文以逐頁標記供定位。

LS-Run 三版與 LS-PrePost v261 的 PDF／Markdown 均已在全文索引中登錄。三個版本對照顯示 LS-DYNA 安裝預設由 v251 的 11.2、v252 的 14.1 更新至 v261 的 16.1；v261 新增 Core Pinning 設定。LS-PrePost 目前只整理功能概覽，尚未逐章人工驗證 GUI、cfile、Python 操作；PDF 圖表、掃描頁及表格版面仍未逐頁視覺核對。

PDF 抽取清冊目前 273 筆：262 筆抽取、10 筆去重、1 筆掃描 PDF 待 OCR；原 PDF 均保留。HTML 詳細轉換項目 170,407 筆：170,316 筆轉換、44 筆純文字 fallback、46 筆重用既有 Markdown、1 筆 0-byte 來源失敗。


### 官方 oSP3D HTML canonical 連結補正

optiSLang previous 頁列出的 oSP3D Script API 2024 R1 舊網址回覆 404；其官方文件現可由 [`/docs/osp3d/index.xhtml`](https://developer.synopsys.com/docs/osp3d/index.xhtml) 取得。已下載原始 HTML（SHA-256 記於 `_catalog/downloads.json`）、轉成同目錄 Markdown，更新 HTML 轉換明細與來源清冊，並納入全文索引。舊 404 保留在連結清冊；此頁本身標示 beta，字典僅摘錄明確的授權、語言與相容性說明。

全庫現況核對：HTML 原檔 570,797 個；轉換明細 170,408 筆（170,317 converted、44 plain-text fallback、46 reused existing Markdown、1 failed）。官方來源同步清冊共 13,210 筆：13,030 downloaded、178 failed、2 blocked。PDF 清冊 273 筆：262 extracted、10 deduplicated、1 scanned PDF pending OCR。文件清冊 595,135 筆，其中 594,745 筆正文；全文索引 594,974 筆中繼資料、631,040 個 FTS 片段，SQLite integrity_check 為 `ok`。

## 2026-10-30 最終逐筆核對

本次重新核對 `_catalog/pdf_extraction.json`、`html_conversion_manifest.json` 與 `downloads.json`：

- PDF 清冊 273 筆：262 筆 `extracted`、10 筆 `deduplicated`、1 筆 `failed`。262 份抽取與 10 份去重紀錄的文字快取均存在、正文超過 100 字並含 `<!-- page N -->` 頁碼標記；所有仍存在的來源 PDF SHA-256 與清冊相符。唯一失敗為 `Speos/unknown/manuals/RAL DESIGN StandardRGB (RGB).pdf`，原 PDF 及說明 Markdown 均保留，因是掃描色票且 OCR 不可靠，沒有虛構抽取正文。
- HTML 轉換清冊 170,408 筆：170,317 筆 `converted`、44 筆 `plain_text_fallback`、46 筆 `reused_existing_markdown`、1 筆 `failed`。本次逐筆核對 170,407 筆非失敗項，來源 HTML、Markdown 輸出均存在且清冊 SHA-256 相符；唯一失敗是 ACT v261 的 0-byte HTML，旁側 Markdown 說明原檔沒有可抽取正文。
- 官方下載清冊 13,213 筆：13,033 筆 `downloaded`、178 筆 `failed`、2 筆 `blocked`。其中 11,439 個已下載 HTML 均有同目錄 Markdown，下載來源雜湊、轉換清冊來源對應與 Markdown 輸出雜湊全部核對通過；另保存並登錄 3 份 PyOptiSLang 1.7.0 `.py` 範例附件，未執行附件。
- 三份 `.py` 附件的 SHA-256 已與下載清冊及文件目錄核對。DOE Settings API 摘列可查證的成員名稱；PyOptiSLang 教學腳本流程已摘要，但套件內載入的次級範例未鏡像，相關 DOE／Sensitivity 主題仍為 `draft`，附件未執行。
- 四個優先產品的官方同步狀態：SpaceClaim 2/2、Mechanical 146/146、LS-DYNA 251/256、optiSLang 836/837 筆下載成功（包含 3 份 `.py` 附件）。LS-DYNA 的 5 筆失敗是 PyDYNA 範例所連結的 `_ls_dyna_knowledge_base` 404 路徑；optiSLang 的 1 筆失敗是舊 oSP3D URL，官方 canonical 頁已另行下載及轉換。兩筆 403 受阻來源屬 ADR 與 Minerva，非上述四產品。

此核對驗證清冊列出的轉換輸出、下載 HTML 及 PDF sidecar 的存在與雜湊，不代表逐頁人工審閱技術正文、表格、圖片或版面。原始 PDF／HTML 與 REA 萃取內容未修改。

## 2026-10-30 PDF sidecar 補齊與 HTML 覆蓋複核

依 `pdf_extraction.json` 的 SHA-256 相符快取，為 242 份原本缺少同目錄 Markdown 的可抽取 PDF 建立逐頁 sidecar，並將現存 PDF 的 sidecar 路徑回寫清冊。262 份可抽取 PDF 現均有 sidecar：254 份內容與核實快取一致，8 份保留原有不同內容而未覆寫。這 8 份既有 sidecar 沒有逐頁標記；其 page-marked 擷取版本仍在雜湊命名的 _catalog/pdf_text_v2 快取中，PDF 清冊的 `text_path` 繼續指向該快取供檢索。另 1 份掃描色票保留含原頁影像的說明 Markdown，未將不可靠 OCR 當作正文。PDF 清冊中的 10 筆 `deduplicated` 來源檔已不存在，保留歷史紀錄，不建立虛構輸出。逐筆核對目前磁碟上 263 份 PDF 均有清冊記錄與 Markdown sidecar；262 份抽取來源 SHA-256、頁碼標記及 sidecar／快取一致性均通過（內容不同的 8 份依原狀保留）。

重新盤點磁碟上 570,797 個 HTML：570,721 個可由文件清冊或轉換清冊追溯，另 76 個有非空同名 Markdown；未覆蓋數為 0。HTML 轉換明細 170,408 筆，依逐項狀態統計為 170,317 `converted`、44 `plain_text_fallback`、46 `reused_existing_markdown`、1 `failed`；所有 170,407 筆非失敗項來源與 Markdown 的 SHA-256 均相符。唯一失敗項仍是 0-byte ACT HTML，來源無正文，說明 Markdown 保留失敗原因。官方下載清冊中 11,439 筆已下載 HTML 均有來源 URL、原檔、同目錄 Markdown，且下載、轉換來源與輸出雜湊一致。轉換清冊彙總數已校正為目前實際 HTML 數及逐項狀態數。

此次只補缺少的 PDF sidecar 並校正 HTML 清冊彙總；PDF/HTML 正文原檔未改寫。新增 sidecar 與既有 PDF 快取正文相同或保留原有人工內容，因此沒有重建全文索引。
整個指定的 docs 目錄遞迴實掃共有 263 份 PDF 與 570,797 個 HTML；均位於 ANSYS_Document，目錄外沒有遺漏的 PDF／HTML。


## 2026-10-30 四產品續抓及下載正文關聯複核

再次同步 SpaceClaim、Mechanical、LS-DYNA、optiSLang 的官方來源，將 SDK 每輪上限提高至 100；Mechanical、LS-DYNA、optiSLang 的本輪佇列均已處理完，下載清冊不再有 `partial` 記錄。同步命令以非零碼結束，原因是清冊仍保留其他來源的失敗與受阻項；目前全庫清冊為 13,213 筆：13,033 `downloaded`、178 `failed`、2 `blocked`。首批四產品狀態為 SpaceClaim 2 筆成功、Mechanical 146 筆成功、LS-DYNA 251 筆成功／5 筆 404、optiSLang 836 筆成功／1 筆舊 oSP3D 網址 404；oSP3D 2024 R1 canonical 頁已另有下載及轉換正文。

重建首批四產品清冊後，`documents.json` 共 595,138 筆，其中 594,748 筆 `body_present`。逐筆核對 11,439 個已下載 HTML：原始檔 SHA-256 相符、Markdown 正文存在且非空，下載記錄均有 `text_path`。唯一未以原路徑另列在 `documents.json` 的 HTML 是 PyMechanical Stubs；其 HTML SHA-256 與同 SDK／版本／產品的另一個已索引來源完全相同，清冊以該內容的既有來源 ID 去重保留，下載與 sidecar 路徑仍留在 `downloads.json`。

全庫磁碟實掃仍為 263 份 PDF、570,797 個 HTML：所有 PDF 均有同名 Markdown；HTML 未覆蓋數為 0（每頁至少能由文件清冊、HTML 轉換清冊或非空同名 Markdown 之一追溯）。HTML 轉換清冊仍有 170,408 筆，170,407 筆非失敗項已核對來源與輸出摘要；1 筆失敗仍是無正文的 0-byte ACT 頁。全庫其餘下載缺口以 DNS／網路失敗、404、403 及既有路徑錯誤留在下載清冊，尚未宣稱完成。

## 2026-10-30 Thermal Desktop 文件與轉換追查

Thermal Desktop 的 PDF 抽取清冊有 7 筆，全部為 `extracted`。逐項重算來源 PDF SHA-256，並比較 PDF 同名 Markdown sidecar 與清冊文字快取，7 筆來源摘要及輸出內容均相符；未重轉或覆寫原件。

官方下載清冊有 91 筆 Thermal Desktop 來源：88 筆成功、3 筆失敗。88 筆成功來源都是 Markdown（非 HTML），下載原檔均存在且 SHA-256 相符，因此不列入 HTML 轉換清冊。三筆失敗為兩個 OpenTD.Results API reference URL 回覆 HTTP 404，以及 Thermal Desktop landing page 的 DNS `getaddrinfo failed`；網址、錯誤與版本記錄於知識字典 [來源清冊](sources.csv)。

本地字典以 OpenTD v261 官方文件整理 6 個 `draft` 主題，另參照 PDF 內文標示 OpenTD 2024 R2 的 Getting Started 手冊。已實際搜尋 WorkingUnits 與 SINDA/FLUINT co-solver 主題並以 `get_chunk` 取回 v261 來源片段；OpenTD.Results、AutoCAD/.NET 與 Python runtime 範例仍未在軟體環境執行。全文索引現有 594,981 筆 `docs_meta`、631,063 個 FTS 片段，`PRAGMA quick_check` 為 `ok`。

## 2026-10-30 System Coupling Participant Library 來源與轉換核對

System Coupling 官方下載清冊有 278 筆：271 筆成功、7 筆失敗。成功項含 185 個 HTML 與 86 個原生 Markdown 檔；271 個已下載來源的 SHA-256 均相符。185 個 HTML 全部已轉為 Markdown，逐筆核對來源及輸出 SHA-256 均相符。PDF 抽取清冊沒有 System Coupling PDF 項目。

七筆下載失敗中有 4 個 HTTP 404（包含已被新版路徑取代的 user-guide 舊 URL）及 3 個 DNS 解析失敗；每個 URL 和錯誤記錄在知識字典 [來源清冊](sources.csv)。不是所有 278 個下載候選都已成功，字典只將可取得且已索引的來源作為技術依據。

System Coupling 字典目前整理 v251、v252、v261 Participant Library 文件的 6 個 `draft` 主題。已用 `system_coupling` 篩選實際搜尋 v261 概念頁、migration guide 和 results／mapping 來源並以 `get_chunk` 取回片段；未執行範例或 MPI 求解。版本差異只摘錄官方 migration guide 明列的限制，沒有由文件目錄差異推斷 API 完全相容。

## 2026-10-30 EnSight PDF／HTML 與官方 API 來源核對

EnSight PDF 抽取清冊有 3 筆，全部為 `extracted`。逐項重算來源 PDF SHA-256，並核對同名 Markdown sidecar 與清冊文字快取，來源及 sidecar 內容均相符。

EnSight 官方下載清冊有 96 筆：95 筆成功、1 筆失敗。95 筆成功來源包含 90 個原生 Markdown 和 5 個 HTML；來源檔均存在且 SHA-256 相符。5 個 HTML 均已轉成 Markdown，逐筆核對 HTML 輸入與 Markdown 輸出摘要相符。唯一失敗是 `https://developer.synopsys.com/docs/ensight.md` 的 DNS `getaddrinfo failed`，失敗項目與原因已列於知識字典 [來源清冊](sources.csv)。

EnSight 字典首輪整理 7 個主題，引用 v252／v261 Developer Portal 與 3 份版本欄為 unknown 的 PDF；已實際搜尋 gRPC、DVS 及 Shared Memory 主題並以 `get_chunk` 取回有版本／網址的來源。未執行 C/C++／Python API、GUI 或輸出 viewer 範例；舊 PDF 只依目錄及頁面明示內容作導覽，不延伸成 v261 操作要求。


## 2026-10-30 PDF／HTML 交付複核

本次重新掃描文件目錄，磁碟上有 263 份 PDF 與 570,797 個 HTML。PDF 抽取清冊共 273 筆：262 筆 extracted、10 筆 deduplicated、1 筆 failed。263 份現存 PDF 都有同名 Markdown sidecar；有來源雜湊的抽取來源均與 PDF 相符。唯一失敗為 Speos RAL 掃描色票，沒有可可靠抽取的文字，未執行 OCR。

已下載 HTML 共 11,439 個；逐項確認原檔與非空 Markdown sidecar 均存在，下載原檔 SHA-256 相符。HTML 轉換清冊共 170,408 筆：170,317 converted、44 plain-text fallback、46 reused existing Markdown、1 failed。全庫 HTML 覆蓋盤點的既有結果為未覆蓋 0；原始 HTML 保留。

下載清冊有 13,213 筆紀錄。以來源 URL 去重後，35 筆 failed／blocked 紀錄另有同網址的成功下載；排除這些重複紀錄，仍有 145 個未取得網址：86 個 DNS 解析失敗、43 個 HTTP 404、14 個正文不足或需登入、2 個 HTTP 403 受阻。重新測試 4 個 DNS 失敗網址仍回報 `getaddrinfo failed`。網址、版本和狀態留在 `_catalog/downloads.json` 及知識字典來源清冊；缺失正文未當作已轉換內容。

此複核未修改原始 PDF／HTML 或 REA 萃取內容。未能取得的來源和掃描 PDF 仍是轉換覆蓋限制；網站若恢復或提供可授權文字，可再補抓與轉換。


### LS-DYNA PyDYNA Knowledge Base 連結追查

五個 PyDYNA 教學生成的 `_ls_dyna_knowledge_base` URL 回覆 HTTP 404；PyDYNA `inputs` 原始範例把外部目標指定為 Ansys LS-DYNA Knowledge Base。已透過官方網站瀏覽器文字檢視 canonical Knowledge Base 及 General、Implicit、Simple Examples 分類與四個連結案例，摘要放在 [LS-DYNA 字典](lsdyna.md)，並於 [Markdown 連結清冊](markdown_links.csv)保留原 URL 的 404 記錄和替代來源說明。因本機 DNS 仍失敗，原始頁面 HTML 沒有下載，來源列明確標為瀏覽器摘要而非 HTML 轉換稿。


### System Coupling 四個 v261 404 路徑的 canonical sidecar

下載清冊有四個錯誤舊 URL（heavyweight data、mesh data、parallel execution、compiling/linking/executing）回覆 HTTP 404。v261 官方 canonical `.md` 頁面已存在於本機 `System_Coupling/v261/guide/`，正文在文件清冊為 `body_present` 並已索引；成功 sidecar 路徑已補入知識字典來源清冊。保留四筆舊 URL 失敗記錄，但不再把它們當作正文缺檔。

### 2026-10-30 轉換與第一批 RAG 再核對

依目前 `_catalog/pdf_extraction.json`，PDF 清冊仍有 273 筆：262 筆 `extracted`、10 筆 `deduplicated`、1 筆 `failed`。本輪確認 262 份抽取 PDF 的同名 Markdown sidecar 均存在且非空；可用來源 PDF 的 SHA-256 與清冊相符。掃描色票失敗項維持待 OCR，不把圖像內容當成已抽取文字。

目前 `_catalog/html_conversion_manifest.json` 有 170,408 筆轉換紀錄：170,317 `converted`、42 `plain_text_fallback`、48 `reused_existing_markdown`、1 `failed`；清冊記載 HTML 覆蓋量 570,797。唯一失敗仍為無正文的 ACT v261 0-byte HTML。先前逐項雜湊核對結果與缺口說明見本文件「PDF sidecar 補齊與 HTML 覆蓋複核」。

逐頁檢查剩餘 42 個 `plain_text_fallback`：原始 HTML 為 79–144 bytes，正文 9–86 字元；每頁抽出的正文都存在於對應 Markdown，故保留為短篇 fallback，沒有把它們升格為轉換失敗。

第一批四產品的主題引用均能解析至來源清冊 ID 或存在的本機技能文件，來源列的本機路徑均存在。重新呼叫 `search_ansys_docs` 並以 `get_ansys_doc_chunk` 取回片段：SpaceClaim（`Pull tool guides options`）、Mechanical（`IMechanicalExtAPI`）、LS-DYNA（`PARMAXcomputed`）、optiSLang（`sensitivity analysis DOE`）四項皆有可取回結果。

本輪直接連線探測官方 Developer Portal 與 PyAnsys 文件站各一個 URL，兩者均回報 DNS `getaddrinfo failed`；下載清冊目前為 13,033 `downloaded`、178 `failed`、2 `blocked`。因此未把瀏覽器摘要或失敗網址當作新下載／轉換成果，未取得來源仍留在清冊中。

另修正 ACT v261 的 DesignModeler 與 Mechanical 兩個大型參考索引頁：原始 HTML 分別約 0.53 MB、29.4 MB，與已轉換的 canonical HTML SHA-256 相同；先前 fallback 只留下標題。現改重用完整 Markdown（約 0.20 MB、13.4 MB），來源和輸出雜湊均核對相符；重複短 sidecar 已從正文清冊及全文索引移除。代表性查詢可回到 canonical 頁並以 `get_ansys_doc_chunk` 取回正文。

ACT v261 唯一失敗的 0-byte HTML 旁邊保留中文失敗說明；原說明文字曾被清冊品質判斷誤列為正文。本輪將其標為 `stub`，保留在文件清冊但排除 FTS。查詢 `MappingValidation RemoveParameter Mechanical` 已不再回傳該失敗說明；SQLite `PRAGMA quick_check` 為 `ok`，清冊正文索引數 594,745，搜尋不需觸發重建。


### 2026-10-30 PDF 頁碼轉換修復與索引狀態

為避免舊轉換快取以 Markdown basename 命名造成跨版本覆寫，本輪以 PDF 來源 SHA-256 為唯一檔名，從原始頁面快取重建 262 份 PDF 文字，生成 60,269 個 `## PDF Page N` 標題；PDF 頁面標記因此可在 Markdown 與切分正文中閱讀。PDF 清冊 `text_path` 與文件清冊已改指向 `_catalog/pdf_text_v4/<PDF SHA-256>.md`。254 份原由快取生成且雜湊未變的同名 sidecar 已同步；8 份內容原本不同的 sidecar 保持原樣。10 筆去重項及 1 筆掃描失敗項未改其來源狀態。

HTML 清冊本輪核對仍為 170,408 筆：170,317 converted、42 plain-text fallback、48 reused existing Markdown、1 failed；HTML 覆蓋量 570,797，唯一失敗為 0-byte ACT v261 頁。42 筆 fallback 正文已在此前逐頁核對。來源與轉換缺口仍依清冊記錄，原始 HTML 未覆寫。

PDF 正文及 `docs_meta` 對應別名已在 SQLite 交易中更新。但隨後讀取資料庫時回報 `database is locked`，故本輪尚未重跑 `quick_check`，也未能實際用 `search`／`get_chunk` 抽查新索引是否能取回可見頁碼；此前索引可取回內容的紀錄不代表此輪更新後的資料庫已驗收。鎖定解除後須重新核對 `PRAGMA quick_check`、確認不觸發全庫重建，並以 PDF 搜尋及片段擷取驗證頁碼與來源路徑。


索引補充：後續檢查發現 PDF 索引分塊呼叫曾使用 1,600／200 字元，而目前專案設定為 `CHUNK_SIZE=1400`、`CHUNK_OVERLAP=180`；因此本輪 SQLite 更新不能視為最終完成。資料庫目前有活動中的 SQLite journal，唯讀查詢等待後仍回報 `database is locked`，尚無法確認目前提交狀態或安全重建 PDF chunks。解除鎖定後需按現行設定重建相關 PDF chunks、校正 `chunk_count`／heading，再執行完整性檢查與代表性搜尋擷取。


### 第一批四產品的最新轉換數

依目前轉換清冊，SpaceClaim 有 4 份 extracted PDF、1 份 deduplicated PDF，沒有 HTML；Mechanical 有 2 份 extracted PDF、144 份 converted HTML；LS-DYNA 有 7 份 extracted PDF、247 份 converted HTML；optiSLang 有 2 份 extracted PDF、577 份 converted HTML。這些是本機清冊中已下載／存在的數量，不代表官方網站所有文件均已鏡像。另抽查三個有 HTML 的產品各一頁，其來源與 Markdown 雜湊皆符合清冊；全量 HTML 逐檔雜湊覆核已因掃描耗時中止，既有全庫覆蓋及轉換報告仍見上節。


### 第一批下載 HTML 輸出雜湊核對

將 `_catalog/downloads.json` 與 HTML 轉換清冊逐筆對照，Mechanical 144、LS-DYNA 247、optiSLang 577 個已下載 HTML 均有非空 Markdown；968 個 HTML 原檔 SHA-256 及對應 Markdown 輸出 SHA-256 全部符合清冊。SpaceClaim 的下載清冊是 PDF，沒有 HTML。這項全量核對涵蓋第一批下載 HTML，不涵蓋 170,408 筆全庫 HTML 轉換紀錄。


### Markdown 外連內容保存核對

`markdown_links.csv` 中已下載或重用的連結正文都已有非空本機檔案：Mechanical 146 筆、LS-DYNA 247 筆、optiSLang 825 筆紀錄（展開合併路徑後 826 個檔案）。未複製的內容仍依狀態列冊：Mechanical／optiSLang 有登入限制與官方 GitHub 範例未複製項；optiSLang 另有 QA 測試主機權限不明；LS-DYNA 的五個衍生 Knowledge Base 連結回覆 404，替代官方頁摘要已寫入字典。圖片與其他附件只列來源清冊，不當作已抽取正文。SpaceClaim 沒有 Markdown 外連紀錄。


### 第一批下載清冊狀態

下載清冊中 SpaceClaim 的 2 份 PDF 均下載成功；Mechanical 的 144 HTML、2 Markdown 均成功；LS-DYNA 的 247 HTML、4 PDF 成功，另有 5 個衍生網址失敗；optiSLang 的 577 HTML、256 Markdown、3 Python 附件成功，另有 1 個舊網址失敗。失敗網址、錯誤與官方替代來源已保留在下載／Markdown 連結清冊，不將附件或失敗頁當作已轉換正文。


### PDF 分塊修復準備與 Mechanical 官方 API 入口

按專案設定 `CHUNK_SIZE=1400`、`CHUNK_OVERLAP=180` 離線計算，262 份 PDF 對應 62,031 個 chunk，60,269 個原始頁碼標題全部至少出現在一個 chunk；重疊區域造成 10,062 個標題重複，屬 overlap 行為。此為預期輸入核對，尚未寫回或驗證正式 SQLite。

Mechanical 兩個 `scripting.mechanical.docs.pyansys.com` 本機入口 Markdown 只含 redirect stub。官方 v261 API 索引已由瀏覽器檢視，摘要已補入 Mechanical 字典及來源清冊，明確標記原始 HTML 未下載、摘要未作為正文索引。正式索引仍須在 SQLite 鎖解除後重建，才能納入本輪字典更新。


補充核對：下載清冊中 2 份 Mechanical 與 256 份 optiSLang 的原生 Markdown 來源均存在且 SHA-256 相符；LS-DYNA 本輪下載列沒有原生 Markdown 檔。這與前述 HTML 轉換稿核對分開計數。


### 2026-10-30 續查的第一批檔案雜湊複核

重新讀取目前下載及轉換清冊並逐檔計算 SHA-256：Mechanical 144、LS-DYNA 247、optiSLang 577，共 968 個已下載 HTML 均有對應轉換紀錄，原始 HTML、下載清冊、轉換清冊與非空 Markdown sidecar 的摘要全部相符。四產品抽取 PDF 共 15 份（SpaceClaim 4、Mechanical 2、LS-DYNA 7、optiSLang 2）；原 PDF 與清冊摘要相符，SHA 命名抽取稿摘要相符，同名 Markdown sidecar 亦符合轉換清冊；先前標記 `existing_different_preserved` 的 sidecar 依保護規則不與新稿強行比對或覆寫。本次核對零差異。

全庫 HTML 轉換清冊的 170,408 個項目也完成存在性檢查：來源 HTML 全部存在；所有非失敗項目都有非空 Markdown 輸出，缺源、缺輸出及空輸出均為 0。唯一失敗項為 ACT v261 的 0-byte HTML，錯誤原因如清冊所載；本次是存在性檢查，沒有重做全庫 SHA-256。

另檢查四產品字典中的 151 個本機 Markdown／PDF／來源清冊連結及來源 ID，未發現失效目標；外部網站的當前可用性不在此項本機連結檢查範圍內。

### PDF 表格版面抽查

以 Poppler 將 LS-DYNA R16 Volume I PDF physical page 1867 渲染成 PNG，對照 `*CONTROL_TERMINATION` 卡片欄位表及變數說明表。PDF 轉換稿保留參數名稱、型別、預設值與描述文字，但攤平了欄列關係，且把上標預設值 `10⁸` 抽成 `108`。LS-DYNA 字典現以 Markdown 表重排來源列出的六個欄位，並明確記錄轉換稿的上標／表格限制；沒有修改原 PDF 或轉換稿。另以隔離 FTS 暫存索引搜尋 `ENDMAS DTMIN` 並擷取 chunk，確認字典表能回傳 `10⁸` 和欄位名稱；此結果不代表正式 SQLite 已更新。此例只抽查一頁，不代表所有 PDF 表格都保留欄列結構。

Mechanical `結果與後處理` 主題也依 v261 Scripting Guide physical page 321 將 transient structural 範例的三類結果物件、設定及取值路徑整理成表。以隔離 FTS 索引搜尋 `UltimatePerMaterial SafetyFactor` 並擷取 chunk，確認取值列能被找回；正式索引仍待 SQLite 解鎖後驗證。

### 第一批 HTML 表格結構抽查

對 968 份第一批下載 HTML 來源計算 `<table>` 標籤：Mechanical 93、LS-DYNA 63、optiSLang 50，共 206 頁含表格。對應 Markdown 中 205 個來源表格頁面未找到標準 pipe-table 標記；下載 Markdown 全體中標記數為 Mechanical 4、LS-DYNA 7、optiSLang 0，其中大多不是上述 HTML 表格頁。已抽查頁面的格中文字仍以標題、連結與段落等方式出現，但欄列關係不保留。檔案存在與雜湊一致不代表表格版面完整；須將這 205 個來源頁面列為表格結構待改善，不把現有文字版面宣稱為完整表格轉換。此輪未覆寫這些 HTML／Markdown，避免索引寫入期間變更輸入。

為維持使用者可讀且可檢索的欄列關係，已在三產品字典重排代表表格：Mechanical `mechanical_warnings` 兩個 helper、PyDYNA `option_card` 四個類別，以及 PyOptiSLang `AbsolutePath` 的七個轉換方法與兩個屬性。三項以隔離 FTS 索引搜尋並擷取 chunk，均能回傳表格值及來源路徑；正式 SQLite 尚未驗收。原 HTML 及轉換 sidecar 沒有改動，因此其餘 205 頁的欄列結構仍是轉換品質缺口。


### 2026-10-30 第一批轉換稿檢索診斷

以專案 `index.search`、`index.get_chunk`、`_chunk_text` 及現行 `CHUNK_SIZE=1400`、`CHUNK_OVERLAP=180`，在暫存 SQLite 建立四產品代表來源的隔離索引。SpaceClaim、Mechanical、LS-DYNA、optiSLang 的代表查詢均能取回來源正確的 chunk；另以四份 PDF 的 SHA-256 命名抽取稿查詢 `PDF Page`，四產品都能取回含可見 PDF 頁碼標記的 chunk。測試資料庫只在暫存目錄，沒有寫入正式索引。

正式 `docs_index.sqlite` 仍無法唯讀查詢：SQLite 回報 `database is locked`。本輪先觀察到 journal 約 191 MB；後續兩次相隔 2 秒的觀察中 DB／journal 時間戳更新，journal 增至 216,524,152 bytes，顯示寫入活動仍在變化。此執行環境只能列出自身 PowerShell／conhost 程序；Windows Restart Manager 的 `RmStartSession` 回傳錯誤 29，無法據此識別鎖定程序。故本次隔離檢索通過不等於正式索引已更新或驗收；PDF 新分塊及本輪字典增補尚未在正式 SQLite 驗證。第一批下載 HTML 的來源及 Markdown 輸出雜湊此前已全量核對 968/968；全庫 170,408 筆 HTML 轉換未做本輪全量雜湊重掃。

後續重新檢查時唯讀查詢仍回報 `database is locked`；`docs_index.sqlite` 約 3.76 GB、journal 由 217,459,864 bytes 增至 224,533,952 bytes（2026-10-30 21:57），程序清單仍只顯示目前命令殼層與 conhost，無法確認寫入者身分。沒有對正式 DB 或 journal 進行修復、替換或終止程序。

### 2026-10-30 持鎖程序唯讀診斷

22:01:27 到 22:02:22 間，正式 SQLite 主檔維持 3,759,202,304 bytes，journal 從 227,576,312 增至 227,707,640 bytes；唯讀執行 `SELECT count(*) FROM sqlite_master` 仍回報 `database is locked`。本執行環境無法取得其他程序資訊：`Get-CimInstance Win32_Process` 回報 CIM 資源不可存取，`tasklist` 回報使用者名稱或密碼錯誤；`openfiles /query` 顯示須啟用系統全域物件追蹤且本次查詢遭拒，環境亦沒有 `handle.exe`。先前 Restart Manager 啟動工作階段回傳錯誤 29。故目前只能確認鎖及 journal 仍在變化，不能歸因至特定程序；沒有終止程序，也沒有修復、替換或寫入正式 DB/journal。

22:03:15 後續觀察：主資料庫與 journal 的修改時間同步更新，主檔仍為 3,759,202,304 bytes，journal 增至 227,834,864 bytes；只讀 SQLite 查詢仍為 database is locked。此變化支持目前有寫入活動，但持鎖程序仍無法辨識。
### 2026-10-30 22:04 HTML/PDF 雜湊複核

重新計算第一批四產品 968 份 HTML 的 SHA-256：下載來源檔、轉換稿及轉換清冊雜湊全部相符，輸出非空，清冊皆為 `converted`。第一批 PDF 清冊有 16 筆：15 筆抽取、1 筆重複；15 份抽取源檔與雜湊快取相符，sidecar 均非空，12 份未標記保留的 sidecar 雜湊相符，其餘 3 份為 `existing_different_preserved`，未覆寫。另以 PyMuPDF 1.28.2 的 `find_tables()` 對照 LS-DYNA R16 Volume I physical page 1867；能辨識表格欄列，但輸出仍將 `10⁸` 抽成 `108`。此環境未安裝 `pymupdf4llm`；原始 sidecar 維持未修改，已知表格修正僅在字典中，正式轉換稿與正式索引仍待安全更新。

22:07:12 後續唯讀觀察：主資料庫仍為 3,759,202,304 bytes，DB 與 journal 修改時間同步更新，journal 為 228,360,880 bytes；SQLite 唯讀查詢仍回報 database is locked。正式轉換輸入與 sidecar 尚未變更。

### 2026-10-31 雜湊清冊修正與正式索引驗收

正式索引首次全量重建在最後一段遇到 1 筆來源 SHA-256 不符，依保護流程丟棄暫存 DB，保留原索引。對照 `_catalog/pdf_extraction.json` 後，確認共有 12 筆 PDF Markdown sidecar 的 `documents.json` 雜湊過期；12 份 sidecar 均與抽取清冊的 `markdown_sha256`／`text_sha256` 相符，12 份原 PDF 也均與各自來源 SHA-256 相符。尾端 3,344 個來源檔逐一核對後，除此 12 筆外沒有雜湊差異、缺檔或 ID 雜湊衝突。已先備份 `documents.json` 至 `_catalog/backups/documents.json.before_content_hash_repair_20261031_101058`，再只更新這 12 筆的正文雜湊及內容衍生 ID；文件清冊筆數維持 595,136。

修正後全量索引成功原子安裝：`docs_meta` 594,980 筆、FTS `chunks` 632,668 個、清冊正文 594,745 筆、去重正文 344,690 份，594,745 個來源均通過 SHA-256 驗證。正式 DB `PRAGMA quick_check` 為 `ok`，catalog manifest stat 相符，`index._needs_rebuild()` 為 false。更新前的正式索引備份為 `Documentation_clean/docs_index.sqlite.backup_before_status_sync_20261031_105000`。

使用現有 `search`／`get_chunk` 完成四產品代表查詢及來源回查：SpaceClaim `Combine` 命中 v261 `SpaceClaim_Documentation.md`，來源路徑存在，片段包含 Combine tolerance；Mechanical `remote point` 命中 v261 RemotePoint API Markdown，片段與來源網址均可回查；LS-DYNA `ENDMAS` 指定新內容 ID 查得 R16 Volume I chunk 2485／2486，來源是同名 PDF sidecar，片段包含 `PDF Page 1867`、欄位列與 `Default ... 10⁸`；optiSLang `sensitivity` 命中 oscillator MOP 教學，來源 Markdown 路徑存在且官方 URL 可回查。搜尋及取片段均成功。

本輪未執行 OCR、求解或軟體內操作；掃描色票與轉換失敗頁仍列為缺口。主題狀態維持原清冊：SpaceClaim 6 個 complete；Mechanical 3 個 complete、4 個 draft；LS-DYNA 1 個 complete、6 個 draft；optiSLang 5 個 draft。全量轉換不代表已人工複核每頁圖表或全部技術內容。

### 2026-10-31 全庫 PDF／HTML 輸出與索引複核

HTML 轉換清冊列出 170,408 個項目：170,317 筆轉換、48 筆沿用既有 Markdown、42 筆純文字 fallback、1 筆失敗。逐項讀取輸出並核對清冊 SHA-256 後，缺少、空白及雜湊不符均為 0。全庫文件清冊有 411,797 筆 HTML 正文／別名列，其中 411,752 筆 `text_path` 存在且非空；另 45 筆均標為 ACT 範例或 API／指南附件，依清冊不作正文索引；HTML 原件缺失為 0。HTML 轉換總覽記錄 570,797 個 filesystem/indexed HTML。

PDF 清冊有 273 筆：262 筆抽取、10 筆去重、1 筆失敗。263 份實際 PDF 均已列入清冊；10 筆去重記錄的原路徑不存在，但其 canonical PDF 均存在。262 筆抽取稿的來源及 Markdown 輸出均存在且非空。唯一失敗為 `Speos/unknown/manuals/RAL DESIGN StandardRGB (RGB).pdf`，屬掃描色票，OCR 仍不可靠；原 PDF 和說明 sidecar 保留，不補猜測文字。

表格重建安裝報告為 `installed`：203 個 HTML 頁面共補入 378 個表格；另有 3 頁含複雜表格保留原轉換稿，待人工檢視後再決定是否採用候選稿。LS-DYNA R16 Volume I physical page 1867 的 `*CONTROL_TERMINATION` 表格已重排，恢復 `ENDMAS` 預設值上標 `10⁸`。每個被替換的 Markdown 都保留安裝前備份；PDF／HTML 原始檔未修改。

正式索引目前可讀：`docs_meta` 594,982 筆、FTS 632,677 個片段；catalog fingerprint 與清冊 stat 相符，`index._needs_rebuild()` 為 false。實際搜尋及取片段驗證：`ENDMAS DTMIN` 回傳 LS-DYNA R16 PDF chunk 2486，包含變數列與 `10⁸`；`AbsolutePath WorkingDirRelativePath` 回傳 optiSLang `WorkingDirRelativePath.convert_to_absolute_path` API 片段，含來源 Markdown 路徑與官方 URL。先前 `database is locked` 的持鎖程序身分無法追認；本次查詢已成功，無需終止程序或直接操作 DB／journal。本段以 SQLite transaction 增量更新，`PRAGMA quick_check` 為 `ok`，且新摘要可透過 `search`／`get_chunk` 查回。


### 2026-10-31 SQLite 鎖定後續探測

本次只讀查看目前正式索引 `docs/Documentation_clean/docs_index.sqlite`：主檔為 3,250,909,184 bytes；相鄰 `-journal`、`-wal`、`-shm` 檔均不存在，唯讀 `SELECT count(*) FROM sqlite_master` 成功。`Get-Process` 未列出 Python／SQLite／Codex 程序；CIM、Tasklist、OpenFiles 及先前 Restart Manager 的限制仍使我們無法取得過去持鎖程序的 PID／命令列，因此程序身分仍未知。沒有終止程序、修復或替換 DB/journal。增量字典更新後搜尋與取片段可正常使用；全庫 `quick_check` 本次未等待完成。


### 2026-10-31 CFX 與 Sherlock 字典增補

新增 CFX／PyCFX 與 Sherlock／PySherlock 字典及各 6 個 draft 主題。來源清冊新增 CFX 8 筆、Sherlock 9 筆，均指向本機 Markdown 與 catalog source URL；來源 ID、主題引用與本機路徑均逐筆核對，缺漏為 0。PyCFX 文件位於 ansys-cfx-core 0.3.0，產品 release 保持 unknown，另保留 launch 說明明示的 CFX 2025 R2 SP3 初版本機啟動條件。PySherlock 主題依 2.1.4 SDK 文件，並比較 2.1.5 的 launch_and_connect 頁：兩版本正文逐行相同；結論僅限該 API 頁。

正式 FTS 增量同步兩份字典及更新後 README，索引為 594,986 筆 docs_meta、632,689 個 chunks，`index._needs_rebuild()` 為 false。實際搜尋 `PreProcessing Solver wait_for_run`（product=cfx）與 `Unix Domain Socket Windows Named User Authentication`（product=sherlock）均命中字典並成功 get_chunk；來源路徑存在。未啟動 CFX 或 Sherlock，未做求解或產品內操作。


### 2026-10-31 Speos 字典增補

新增 PySpeos 0.9.2 字典、7 筆官方 guide／launcher 來源與 5 個 draft 主題。來源 ID、本機正文路徑、topic refs 與字典內部 Markdown 連結檢查均無缺漏。已將本機 Docker image 僅限 Ansys organization 成員存取、Speos service 需產品授權，以及 Speos RAL 掃描色票未可靠抽取列為限制；未複製或修補 PDF／HTML 原件。

正式索引增量加入 Speos 字典並更新 README；目前為 594,987 筆 docs_meta、632,692 個 chunks，`index._needs_rebuild()` 為 false。`launch_local_speos_rpc_server Speos close` 與 `Speos license Docker Ansys organization` 均以 product=speos 搜尋命中字典，get_chunk 成功。未啟動 Speos service、執行 API 或光學求解。


### 2026-10-31 Zemax 字典增補

新增 Zemax OpticStudio／ZOS-API 字典、10 筆來源與 6 個 draft 主題。來源含 v252 繁體中文 OpticStudio User Manual PDF 及 v252／v261 API 文件；PDF 原件存在，sidecar 保留 `PDF Page N` 頁碼標記，封面頁文字標示 2025 R2。字典引用、source IDs、本機來源路徑及主題引用核對無缺漏；沒有改寫 PDF／sidecar，也未逐頁人工檢查圖表與表格。

ZOS-API v261 官方索引可檢索四種文件範例語言與 API 物件導覽；搜尋 `IZOSAPI_Connection IOpticalSystem` 及 `QuickFocus field point FdC` 均命中字典並成功 get_chunk，product=zemax。索引增量同步字典與 README；尚未執行 OpticStudio 或 ZOS-API，未逐項比較 v252/v261 API 差異。


### 2026-10-31 Sound 與 Rocky 字典增補

新增 PyAnsys Sound 0.4.0 與 PyRocky 0.6.2 字典，各含 5 筆來源、Sound 5 個 draft 主題、Rocky 6 個 draft 主題。來源 ID、路徑、主題引用和字典內部 Markdown links 核對無缺漏。Sound 整理 DPF Server、port／環境變數、license context 與 WAV/STFT 範例；Rocky 記錄 PrePost scripting 差異、UI 對話框限制與教學案例值。兩產品 release 依清冊保持 unknown。

正式索引增量加入兩份字典與更新後 README，目前 594,990 筆 docs_meta、632,700 個 chunks，`index._needs_rebuild()` 為 false。`ANSRV_DPF_SOUND_PORT avrxp_snd_level1`（product=sound）及 `GetNumpyCurve GetTimeSet CloseProject`（product=rocky）搜尋均命中字典並成功 get_chunk。未執行音訊授權 checkout、Rocky 模擬或物理驗證。


### 2026-10-31 MAPDL 與 Motor-CAD 字典增補

新增 PyMAPDL 0.74.1 與 PyMotorCAD 0.8.8 字典，各含 6 筆官方來源及 5 個 draft 主題。來源 ID、Markdown 路徑、主題引用與字典內部連結均核對完整。MAPDL 整理 `launch_mapdl()`、`run_location`、APDL Python wrapper 及 mTLS；Motor-CAD 整理 JSON-RPC、internal／external scripting 與 Adaptive Templates 明列的 Motor-CAD 2024.1.2+／PyMotorCAD 0.4.1 條件。兩產品 release 保持 unknown，未用 SDK 版號推定產品版本。

正式索引增量同步兩份字典及更新後 README，現有 594,992 筆 docs_meta、632,704 個 FTS chunks，`index._needs_rebuild()` 為 false。`mTLS Certificate Authority run_location`（product=mapdl）與 `JSON-RPC Adaptive Templates 2024.1.2 0.4.1`（product=motorcad）均命中字典並成功 get_chunk。未啟動 MAPDL／Motor-CAD、執行腳本或求解。


### 2026-10-31 Geometry、Granta MI 與 Lumerical 字典增補

新增 PyAnsys Geometry、Granta MI／PyGranta 與 Lumerical 字典。來源清冊增加 Geometry 6 筆、Granta MI 11 筆、Lumerical 6 筆；主題清冊分別增加 5、7、5 個 draft 主題。Geometry 依 `ansys-geometry-core 0.18.2` stable 頁整理 service、Modeler、Sketch 與單位；Granta MI 分開記錄 Scripting Toolkit 5.0 URL、Connected Materials v261 及 PyGranta RecordLists 2.1.1，並摘錄 Ansys ID 認證與 GMMS/MMD/MMO 概念；Lumerical 本地入口頁版本未知，整理 Lumapi、LSF、MATLAB 與 Lumopt 概述。

Markdown 外連清冊為本輪引用的 22 份本機 Markdown 頁新增 215 筆連結記錄；已在庫的 URL 標為 `already_downloaded`，官方與第三方尚未本地收錄的連結保留為待處理或僅清冊狀態。未將外部頁面當作已讀取來源，也未下載第三方內容。三產品 source rows 分別 6／11／6 筆，topic rows 分別 5／8／5 筆；所有本機來源路徑存在、主題引用可解析、三份字典的本機 Markdown links 均存在，外連狀態欄無空值。

實際搜尋及片段擷取：`host port 50051`（product=geometry）、`MMD`（product=granta_mi）及 `Lumapi Interop Server Lumopt`（product=lumerical）均找到字典頁並成功 `get_chunk`；結果仍可同時回到清冊原文。索引產品篩選辨識三個模組，字典片段 release 標示為 `unknown`。未連線幾何服務、Granta MI、Lumerical，未執行產品 API 或工程分析。


### 2026-10-31 Icepak v261 PDF 字典增補

新增 Icepak 字典與 5 個 draft 主題；來源清冊涵蓋 15 份 v261 PDF。`pdf_extraction.json` 中 15 筆均為 `extracted`，15 份 Markdown sidecar 均存在；逐筆重算 PDF、sidecar 與抽取文本的 SHA-256，與清冊值一致。索引正文帶 `PDF Page N` 定位。本頁分開整理 Icepak／IcepakFEA scripting、IcepakFEA `AssignTemperature`、初始模擬流程、monitor/mesh 與腳本錄製案例；數值仍明確標示為案例設定。

15 份轉換 Markdown 中外連新增 31 筆連結狀態；source paths、topic refs 與字典本機 PDF／Markdown links 均核對完整。`AssignTemperature 90cel`、`thermal monitor global mesh` 及 `loop plane cuts`（product=icepak）均命中字典並成功 `get_chunk`；組合查詢 `錄製 script plane` 未命中字典，分詞組合仍需使用來源實際術語。正式索引目前 594,996 筆 docs_meta、632,718 個 FTS chunks，`index._needs_rebuild()` 為 false。未開啟 AEDT／Icepak，未執行腳本或求解；PDF 圖表與表格未逐頁目視校對。


### 2026-10-31 AVxcelerate、CFF、Discovery 與 PyTwin 字典增補

新增四份字典，來源清冊新增 AVxcelerate 11 筆、CFF 5 筆、Discovery 4 筆、PyTwin 7 筆；另有兩筆原 catalog 分類不符的 PDF 改列 SpaceClaim 及 general 並標註待查。每個字典新增 5 個 draft 主題，來源 ID、路徑及主題引用均核對完整。Markdown 外連清冊新增 486 筆；AVxcelerate 108、CFF 320、Discovery 4、PyTwin 41，其餘 13 筆屬於上述重新分類的 PDF sidecar。官方與第三方外連僅列清冊，沒有把未下載頁面當作已讀正文。

轉換核對：全庫文件清冊中 AVxcelerate 有 313 筆、CFF 89 筆、Discovery 82 筆正文，三者本輪引用來源均已有 Markdown 正文，沒有對這些模組執行新的 HTML 轉換。PyTwin 清冊有 147 個 HTML，轉換清冊全部標為 `converted`；逐筆核對原 HTML 與 Markdown sidecar 雜湊，147/147 通過。兩份 PDF 均為 `extracted`、sidecar `created_from_cache`；原 PDF、Markdown sidecar 與抽取文本檔均存在，三者 SHA-256 均與清冊相符。但檢視 PDF Page 1 封面發現，`Discovery/unknown/manuals/Developers Guide_V232.pdf` 實為 *SpaceClaim Developers Guide API V23 Beta*，`TwinAI/unknown/manuals/UsersGuide_1.62.pdf` 實為 *OPTIMICA Compiler Toolkit Version 1.62*。兩份文件保留且可全文檢索，卻已從錯誤產品字典排除；索引產品標籤分別改為 SpaceClaim 與 general，建置程式也保留這兩項更正。兩份 PDF catalog release 欄位仍為 unknown；PyTwin SDK package 0.13.0 不代表產品 release。

索引增量加入四份字典及更新後 README；正式 SQLite 有 595,000 筆 `docs_meta`、632,728 個 FTS chunks，`index._needs_rebuild()` 為 false，唯讀 `PRAGMA quick_check` 為 `ok`。`WorldUpdate simulation_time`（product=avxcelerate）、`Data Models Project Metadata`（cff）、`Doc objects modeler geometry`（discovery）及 `twin_simulate_batch_mode interpolate`（twinai）均命中字典並成功 `get_chunk`；搜尋結果可回到 AVxcelerate、Discovery、PyTwin 對應來源，CFF Metadata 原文亦可用產品篩選找到。另驗證兩份誤分類 PDF 不再出現在 Discovery／TwinAI 產品結果。先前曾觀察到的 SQLite 鎖定程序無法事後識別；本輪開始前主資料庫可讀且無 journal/WAL sidecar，增量交易已完成。

未啟動 AVxcelerate、CFF、Discovery 或 PyTwin，也未執行模擬。官方 PDF 的表格、圖片與範例未逐頁視覺校對；SDK／產品的安裝、權限及所有跨版 API 差異尚未完整整理。


### 2026-10-31 PyScadeOne、Rigid Body Dynamics、ADR 與 PyTurboGrid 字典增補

新增四份字典與各 5 個 draft 主題。來源清冊新增 PyScadeOne 6 筆、Rigid Body Dynamics 6 筆、ADR 8 筆及 PyTurboGrid 6 筆；本機路徑、source IDs 及 topic references 均核對通過。來源 Markdown 外連狀態新增 248 筆：分別為 97、41、58、52 筆；外部連結依官方／第三方保留 inventory 狀態，未將其當作已讀來源。

HTML 轉換抽查：PyScadeOne 83 個 HTML、ADR 5 個 HTML、TurboGrid 7 個 HTML 在轉換清冊中全為 `converted`；逐筆核對原始 HTML 與 Markdown sidecar 檔案及 SHA-256，合計 95/95 通過。Rigid Body Dynamics 的引用正文為已下載 Markdown，沒有需轉換的 HTML。未從本輪引用來源新增 PDF；PyScadeOne 的產品目錄另有 PDF 未納入本字典。

PyScadeOne 整理 `ScadeOne`／Project API、CLI 與 FMU 前置 code generation；RBD 分開標示 v251／v261 並保留 Mechanical IronPython 執行脈絡；ADR 區分 PyDynamicReporting 0.10.6 服務與 v261 web viewer；PyTurboGrid 記錄 0.9.4 及其 TurboGrid 本機安裝／授權條件。各 SDK 版號未用來推定產品 release。

未在 AEDT、SCADE One、Mechanical、Dynamic Reporting 或 TurboGrid 中執行範例；未產生 FMU、啟動服務、建立資料庫或生成網格。

索引增量加入四份字典與更新後 README；正式 SQLite 為 595,004 筆 `docs_meta`、632,736 個 FTS chunks，`index._needs_rebuild()` 為 false，`PRAGMA quick_check` 為 `ok`。`ScadeOne install_dir standard libraries`（scade_one）、`Rigid Dynamics Environment System`（rigid_body_dynamics）、`Service create_db connect`（adr）及 `launch_turbogrid INF mesh`（turbogrid）均命中字典並成功 `get_chunk`，也能回到各自來源正文。較窄的 RBD 查詢 `CS_Environment System Joint` 未命中字典；補以文件術語搜尋可找到結果，窄查詢限制已記錄。


### 2026-10-31 HFSS、Maxwell、Q3D 與 SIwave 字典增補

新增 4 份字典及 15 個 draft 主題。來源清冊新增 HFSS 5 筆、Maxwell 1 筆、Q3D 2 筆、SIwave 3 筆；主題引用、本機來源路徑及字典內部連結均核對完整。來源 Markdown／PDF sidecar 外連新增 24 筆連結狀態，官方或第三方頁面僅列清冊，未另行下載。

PDF 轉換核對：HFSS 5 份、Maxwell 1 份、Q3D 1 份、SIwave 3 份，合計 10 份 v261 文件全標 `extracted`、sidecar `created_from_cache`；原 PDF、逐頁 Markdown 與抽取文本檔均存在，三者 SHA-256 與清冊一致。封面均標示 2026 R1。PDF page markers 用於定位：HFSS／Maxwell／Q3D scripting guide 的 Pages 3–6 目錄列出腳本環境；SIwave Pages 3–4 定位腳本命令及 PCB 分析流程。Q3D `ExportToFile` 另參考現有 API 摘要，定位到印刷頁 10-56／抽取頁 794–795。

正式 SQLite 增量索引四份字典與更新後 README 後，有 595,008 筆 `docs_meta`、632,743 個 FTS chunks；`index._needs_rebuild()` 為 false，`PRAGMA quick_check` 為 `ok`。HFSS、Maxwell、Q3D 及 SIwave 的代表查詢均命中字典並成功 `get_chunk`；結果也能回到對應來源 PDF／API 文件。SIwave 組合查詢曾只命中字典，改以 `ScrImportEDB SIwave` 或 `PSI SYZ analysis` 搜尋可回到 Scripting Guide 或 PCB tutorial。

未啟動 Electronics Desktop／HFSS／Maxwell／Q3D／SIwave，未執行腳本、分析或求解；PDF 內嵌圖片及完整 command tables 未逐頁視覺校對。

## Workbench、SCADE、Minerva 與 SimAI 核對（2026-10-31）

- Workbench：2 份 PDF 原件、2 份逐頁 PDF Markdown 抽取文字；ACT Customization 與 Workbench Scripting Guide 皆含 `PDF Page` 定位標記。3 份 Markdown 原文／技能亦存在。文件標示 Release 2026 R1；另有 v251 技能片段，尚未逐版比較。
- SCADE：13 份 PDF 原件均有 `pdf_text_v4` Markdown 抽取檔，另有 3 份 Markdown 入口。`RPManuals.pdf` 抽取只有 255 字，已列品質不足；SCADE Suite、Rapid Prototyper 與 SCADE One 快捷鍵分開標示。產品 release 欄仍 unknown。
- Minerva：2 份 Markdown 概覽來源；本機未發現 PDF／HTML 或完整 HTTP API reference，列為來源不足，不推定端點和驗證格式。
- SimAI：62 份 HTML 原件均有同源 Markdown 轉換 sidecar，另有 22 份 Markdown 來源，共 84 筆索引來源。套件標記 `ansys-simai-core 0.4.8` 的文檔與無套件版本標記的入口分開；產品服務 release 未知。
- 每筆 HTML/PDF 的原始路徑與轉換 `text_path` 均記在 `sources.csv`；PDF 抽取位於 `_catalog/pdf_text_v4`。原始 PDF／HTML 沒有覆寫。表格採純文字抽取，圖片、掃描頁和複雜版面仍可能資訊不足；需按清冊個別追蹤。

## 其他模組核對（2026-10-31）

- AnsysEM：27/27 PDF 有逐頁 Markdown 抽取。來源跨 Twin Builder、EMIT tutorials、RF/LNA、FMEA/system identification/LTI ROM 及 legacy SPICE3 等；版本包括 Release 2026 R1、v212、V18.1.1、1993 與 unknown，不合併版本。
- Installation & Licensing：2/2 Release 2026 R1 PDFs 有逐頁抽取；Reaction Chemkin 資料夾的 1/1 Model Fuel Library 2024 Validation Manual 有抽取。
- ICEM CFD：1/1 候選 PDF 有抽取，但正文是 Apple Xgrid Guide（2004），非 ICEM CFD。索引分類覆寫為 `general`，ICEM 字典標來源缺失；原件及轉換文字保留。
- Ansys ID Portal／SSO、PyAnsys、SAF：現有 Markdown 入口快照已索引；沒有在本地找到相對應完整 PDF／HTML 技術手冊，來源版本保持 unknown。

## 產品搜尋與片段擷取抽查（2026-10-31）

各產品以一個代表詞組執行 `search`，並對字典命中呼叫 `get_chunk`；搜尋結果都帶有字典來源路徑，片段擷取成功：SpaceClaim、Mechanical、LS-DYNA、optiSLang、Workbench、SCADE、Minerva、SimAI、Ansys ID Portal、Ansys ID SSO、AnsysEM、ICEM CFD、Installation & Licensing、PyAnsys、Reaction/Model Fuel Library、SAF。ICEM CFD 的產品篩選命中的是來源缺口說明；Apple Xgrid 原文改由 `general` 篩選可找到。

有三組較嚴格詞組未命中整理頁，調整查詢詞後可命中：SCADE 的 `SCS-PM-25 dataflow` 改用 `SCADE Language`；Minerva 的 `HTTP APIs endpoint schema overview` 改用 `HTTP APIs`；PyAnsys 的 `PyAnsys open source` 改用 `PyAnsys`／`libraries`。這些現象反映字典中中英術語和 FTS AND 條件的差異；精確版本代碼或原始 API 名稱建議回查 `sources.csv` 及來源正文。其餘未逐項測試全部主題。

## ACT、PCB Warpage 與 Thermal 核對（2026-10-31）

- ACT 索引 562,362 筆正文，版本標籤：v261 291,805、v252 133,412、v251 133,752、unknown 3,393。內容類別為 406,209 API reference、156,064 guide、84 tutorial、5 manual；來源格式 400,079 HTML、162,276 Markdown、7 PDF。ACT 的 7 份 PDF 均已抽取逐頁文字；v261 Developer Guide 208 頁、XML Reference Guide 1,532 頁。
- ACT download 清冊有 13 筆來源，7 downloaded、6 failed。5 筆錯誤為 DNS `getaddrinfo failed`（Developer Portal 及 v251/v252 API／Examples ZIP）；另 1 筆 v261 `ACTExtensionExamples.zip` 目的路徑越出文件根目錄。各版 coverage 都是 `partial`，tutorial inputs 未確認。
- PCB Warpage 與 thermal 分類目前主要是 repo skills；PCB 可靠度輔助筆記來自 NotebookLM 改寫，未取得 IPC/JESD 標準原文。thermal 兩筆 transfer/LPTN note 分別只有 70／68 字，不能代替完整產品手冊。

ACT PDF hash／頁碼補核（2026-10-31）：7/7 原始 PDF SHA-256 均與 `_catalog/pdf_extraction.json` 相符；7/7 抽取 sidecar 存在，sidecar SHA-256 亦符合 manifest，且都有 `## PDF Page` 標記（各檔 4–5,596 頁）。因此 v261 Developer Guide、XML Reference 的頁碼引用可定位到抽取頁。另三份歷史／範例 PDF 保留為不同來源，版本不明時不推定為 v261。

SQLite 鎖定查核：本輪開始時資料庫可唯讀開啟，沒有 `-wal`、`-shm` 或 `-journal` sidecar；`BEGIN IMMEDIATE` 成功取得寫入交易鎖並立即 rollback，表示當時沒有其他程序持有寫入鎖。先前觀察到的程序無法從目前環境回溯識別；本次增量索引交易已完成。

ACT、PCB Warpage、thermal 的字典均以產品篩選查詢並成功 `get_chunk`。PCB 查詢 `MCP_Test.xlsx SpaceClaim ROM` 與中文 `PCB 輸入 SpaceClaim` 未命中；改用字典原文術語 `Share Topology APDL Mechanical` 和 `ROM material APDL` 可取回片段，需保留精確術語及 FTS 全詞匹配的限制。ACT 全庫查詢另命中 v261 Developer Guide／XML 原文片段。

本輪檢查字典頁面內部連結時，修正 PCB Warpage 與 thermal 指向 `agents/skills` 的 8 條相對路徑；修改後逐一核對目標檔案存在。

### 2026-10-31 Circuit、EMIT、LS-OPT 與來源缺口模組

- Circuit Scripting Guide、EMIT Getting Started Guide、EMIT Scripting Guide、LS-OPT 2026 R1 User Manual、LS-OPT Training Problem Set 共 5/5 PDF 原件 SHA-256 與抽取 sidecar SHA-256 均符合 `_catalog/pdf_extraction.json`；sidecar 存在並保留 PDF Page 標記，標記數分別為 1,152、8、324、850、92。PDF 原件及抽取文字均保留，未重複轉換。
- EMIT manifest 的 Tutorial 1–8 條目為 `deduplicated`，指向 AnsysEM 目錄中的對應原件；8 個 canonical PDF 已由 AnsysEM 來源 ID 索引，不將不存在的 EMIT 副本標成已轉換。
- Circuit、EMIT 文件原先在 catalog 中標為 `general`；依檔案目錄及手冊封面內容，索引產品更正為 `circuit`、`emit`。optiSLang 目錄下的四筆 LS-OPT PDF／抽取 Markdown 記錄依正文標題改列 `lsopt`，不納入 optiSLang 產品篩選；2026 R1 Manual 與 2018／Version 6.0 Tutorial Problems 版本分開。
- Additive、AQWA、FENSAP-ICE、LS-PrePost、Polyflow、EduPack 本機可搜尋來源不足：前五者未找到官方產品 PDF／HTML；部分只有合併範圍的 repository skills。EduPack 僅有 21 MB CHM attachment，quality 為 `attachment`，沒有抽取正文。以上字典明列來源與版本限制。
- 新增 10 個字典頁及 35 個主題列；PDF hash、來源 ID 及本機連結已核對。代表查詢與最終 SQLite 統計接續記錄於本節。

產品搜尋與片段擷取（2026-10-31，新模組）：Circuit（`CPython gRPC UDM`）、EMIT（`Open Examples AH-64`）、LS-OPT（`lsoptui command file batch`）、AQWA（`diffraction radiation RAO`）、Polyflow（`Bird Carreau Cross die swell`）、FENSAP-ICE（`LWC MVD impingement`）、LS-PrePost（`SCL cfile DataCenter`）、Error Catalog（`IronPython closure exec`）、EduPack（`CHM attributenotes attachment`）均命中字典或對應正文，並成功 `get_chunk`。Circuit、EMIT、LS-OPT 的代表搜尋各另命中來源 PDF；產品篩選結果帶回來源路徑。Additive 的 `Additive not_verified zero files` 未命中，改用 `Additive PDF HTML` 或 `Additive source missing` 可取回來源缺口字典；這是窄查詢詞不在正文中的已知限制。

新字典引用的 source IDs、來源本機路徑及相對檔案連結均通過存在性檢查。此批產品資料夾未發現需新增轉換的 HTML；EduPack CHM 未抽取，因此不列為已轉換正文。

本輪索引最終核對：`docs_index.sqlite` 有 595,033 筆 `docs_meta`、632,792 個 FTS chunks；唯讀 `PRAGMA quick_check` 為 `ok`，`index._needs_rebuild()` 為 `false`。Circuit、EMIT、LS-OPT 原文件重新分類及新增字典使用增量交易完成，沒有全量重建。SQLite 目前沒有 `-wal`、`-shm` 或 `-journal` sidecar。

Shared-skill 索引分類補正（2026-10-31）：將 AQWA／Sound 共用 skill 的 AQWA references、Polyflow／FENSAP-ICE skill 及 LS-PrePost 專屬 skill references 按內容改列 `aqwa`、`polyflow`、`fensap_ice`、`ls-prepost`，並同步 sources.csv；`index.py` 的掃描規則保留相同分類。AQWA `RAO ballast diffraction` 可命中 AQWA 字典與 skill；LS-PrePost `DataCenter get_data SCL cfile` 命中 skill、API reference 和字典。Polyflow 精確詞組 `Bird-Carreau Cross PTT` 未命中，改用 `die swell` 可命中 skill 和字典。FENSAP-ICE 的 `LWC MVD static temperature` 查詢只命中字典，短 reference note 沒有足夠詞面供精確查詢；此來源限制已記錄，不能據此宣稱官方設定已被檢索。



### 2026-10-31 官方線上手冊補查與轉換缺口

本輪從官方 Ansys Help 同站擴展到先前無本機正文的模組，並將 14 個來源項記入 `sources.csv`：AQWA v261 User’s Manual、Theory Manual 與 v2611 文件集索引；FENSAP-ICE v242 Tutorial／Workbench Guides 及 v261 flow chapter；Polyflow v242 User’s Guide；LS-PrePost v261 User’s Guide PDF 及 v252 command index；EduPack v261 Help 與 v251 Toolbar Guide；Additive v261 tutorials／PBF guide 及 v251 Additive Print and Science guide。來源頁可開啟或搜尋到摘要，但本輪沒有把遠端正文下載至本機，故 `indexed_chars=0`、品質標為 `online_summary_only`／`online_partial`；這些來源不算已完成 PDF／HTML 轉換，也不會被本機 RAG 全文檢索。

字典只補官方頁面目錄、章節範圍和有限可見摘要，保留來源 URL 與版本。Additive Tutorials 明示部分章節要求 Ansys 登入；LS-PrePost v261 PDF 大型檔案未下載，EduPack 本機 CHM 仍未抽取。AQWA、FENSAP-ICE、Polyflow、LS-PrePost、EduPack 和 Additive 的缺口狀態已從「沒有官方來源」修正為「官方線上來源已找到、正文尚未快取／轉換」，Additive 另標示部分內容受登入限制。

SQLite 寫鎖查核：本輪唯讀連線成功，主資料庫無 `-wal`／`-shm`／`-journal` sidecar；以短暫 `BEGIN IMMEDIATE` 後立即 rollback 成功取得寫鎖，表示檢查當下沒有其他 SQLite 寫入者持鎖。Windows 環境未使用具管理權限的 handle 工具，因此不能回溯辨識曾持鎖的程序；只能確認交易時點的鎖狀態。


索引增量更新此批 6 份字典與 README／conversion status 後：`docs_index.sqlite` 有 595,033 筆 `docs_meta`、632,796 個 FTS chunks，唯讀 `PRAGMA quick_check=ok`，`_needs_rebuild=False`。AQWA、FENSAP-ICE、Polyflow、LS-PrePost、EduPack、Additive 各以官方手冊章節／術語查詢均命中字典，六次 `get_chunk` 均成功。新字典的 14 個 source IDs、35 個新增 `topics.csv` source references、相關本機來源路徑及六頁相對 Markdown 連結均驗證存在；來源缺口主題狀態已更新。

此批遠端 PDF／HTML 未下載或轉換成 sidecar，不能算完成本機 PDF／HTML 轉換；可搜尋內容仍限於本機字典摘要和技能。全 63 份字典頁的本機 Markdown 連結經 URL percent-decoding 後均指向存在檔案；未改動其他產品頁。


### 2026-10-31 AnsysEM／Twin Builder 主題深化

重新核對 AnsysEM 來源清冊的 27 份 PDF：27/27 均有 `_catalog/pdf_extraction.json` 記錄、原件 SHA-256 相符、抽取 sidecar 存在且有正文頁標記，合計 2,076 個 PDF page markers。FMEA Toolkit Manual 為 31 頁，MIMO guideline 6 頁，Mechanical Thermal LTI ROM guideline 11 頁；未重新轉檔，沿用既有抽取。

依原文頁面將原先合併的「FMEA／MIMO／LTI ROM」草稿拆成三個主題，新增實際步驟及定位：FMEA Toolkit 建模／情境／severity（抽取 PDF Page 5–16）、MIMO step-response 檔案與 export（Page 1–6），以及 Mechanical Thermal 到 Simplorer ROM（Page 1–7）。後者文件內版號不一致（封面 Simplorer 18.2，內文 R18.0），列 `pending_version_review`。MIMO 與 FMEA 來源沒有明確產品 release，維持草稿而未推定版本。



AnsysEM 代表查詢：`FAULT_MODE FMEA_MODE T_FAIL` 命中 FMEA PDF 與字典；`MIMO Input_PortNames Input_StepInputValues` 命中 MIMO PDF 與字典；`Input_ConPins` 及 `Time Domain Vector Fitting` 命中 Mechanical Thermal ROM 原 PDF。窄查詢 `Simplorer 18.2 R18.0 Mechanical Thermal ROM` 未命中，因全文搜尋採詞組合條件且版號詞不能共同定位；改用原文識別詞可定位。三組查詢都對字典命中呼叫 `get_chunk` 成功。


### 2026-10-31 SCADE PDF 主題深化

13 份 SCADE PDF 原件皆有 `pdf_extraction.json` SHA-256 對應、可讀的逐頁 Markdown sidecar 與 `PDF Page` 標記，逐份抽取正文可讀；未重新轉檔。依 Libraries Manual、Python API Guide、Java/Tcl API Guide、Metamodels reference、Installation Guidelines、Software Design Standard、Rapid Prototyper User Manual／Getting Started 等原文目錄和說明頁，補足各文件範圍與相容邊界。RPManuals.pdf 仍只有 255 字目錄頁，保留品質不足。

原先合併的 Design standards／Metamodels／Rapid Prototyper topic 拆分為三項：專案裁剪的 design-standard template、metamodel/API 導覽、Rapid Prototyper 圖形面板與模擬。13 個來源版本多以文件版本代碼或出版日期表示，產品 release 欄仍為 unknown，沒有把 2026 family 文件日期推成產品 release。


SCADE 代表檢索：產品篩選＋`category=guide` 下，`libdigital libimpl libverif`、`SCADE Python API data access scripting`、`Rapid Prototyper widget standalone executable` 均命中字典頁並成功 `get_chunk`。精確組合 `SCS-SDS 2024-03-20 template customized safety` 未命中；改用 `software design standard` 可取回字典片段。精確章碼／標準代碼與英文屈折詞不保證能以組合詞查詢，應用手冊標題或章節術語回查。


### 2026-10-31 SimAI HTML 別名路徑核對與字典補充

重新核對 SimAI 來源清冊的 62 份 HTML：62/62 本機原件存在、來源列皆指向現存 Markdown sidecar。全域 `html_conversion_manifest.json` 可對上 42 筆 `0.4.8` HTML；另 20 筆 `unknown` 路徑未出現在 manifest。這 20 筆與相同檔名的 v0.4.8 原始 HTML 逐一 SHA-256 相同，20/20 hash-named `_catalog/html_text/<source_sha256>.md` sidecars 存在；移除 YAML front matter 與 Markdown link targets 後，轉換正文 20/20 相同。這些列保留 release unknown，不以同內容替代其版本證據；目前缺的是 manifest 對未知路徑 alias 的列項，不是缺少 sidecar。22 份 Markdown source 另行保留，總共 84 筆來源列。

SimAI 字典依 SDK 0.4.8 轉換正文補充 Client profile／proxy、TrainingDataPart／Project／ModelConfiguration、Geometry 刪除連帶資料、Selections／sweep、GeomAI MER 評估與 non-parametric optimization，並為主題增加可點擊本機 Markdown 連結。`stable` 文件 URL 與 `unknown` 快照仍不作服務端版本推定。


SimAI 代表檢索：`TrainingDataPart`、`geometry.sweep`、`run_non_parametric`、`ProxyError`、`GeomAI Chamfer distance` 均以 `product=simai, category=guide` 命中字典並成功 `get_chunk`。組合詞 `run_non_parametric offline_token` 未命中字典，改用 API 方法名稱 `run_non_parametric` 可定位；組合式查詢依 FTS 全詞條件會因下底線／形態差異漏掉結果。


### 2026-10-31 AQWA v261 線上章節摘要與 PDF 抽取盤點

重新盤點 `_catalog/pdf_extraction.json` 的 273 筆 PDF 記錄：262 筆已抽取、10 筆為去重指向，Speos/RAL DESIGN StandardRGB 色票 PDF 1 筆抽取失敗並標記 `image_sidecar_ocr_unreliable`。此檔為圖片型色票內容，沒有可靠逐頁文字；未以空文字假稱已轉換，也未修改原 PDF。其餘記錄指向既有抽取 sidecar 或去重 canonical 原件。

AQWA 官方 v261 User’s Manual 的 Workflow and Systems、Hydrodynamic Diffraction Workflows/System、Create Analysis System、Geometry、Mesh、Analysis Settings、Ocean Environment and Forces 與 Solution 章節可讀取。本輪依頁面內容整理內建／外部 mesher、Project Schematic 連結與唯讀邊界、座標與水深、Moonpool 限制、網格致命失敗、環境載荷及結果更新條件；新增 9 筆獨立官方 URL 至來源清冊，並新增 2 個 `source_online_partial` 主題。來源正文未保存為完整鏡像，字典為繁中改寫摘要。Theory Manual PDF 開啟回報內容長度 13,633,388 bytes 超出擷取限制；理論公式及完整表格仍未進入本機索引。v2611 文件集頁只用來確認手冊範圍，不推定為 v261 內容。

AQWA RAG 抽查：`Hydrodynamic coefficient database RAO QTF`、`Moonpool active Hydrodynamic Response`、`Clear Generated Data co-simulation FMU` 皆命中字典並成功 `get_chunk`。較寬的網格組合查詢 `Hydrodynamic Diffraction external mesher read-only` 未命中；以已知詞彙重新查詢後，`Hydrodynamic coefficient database RAO QTF` 可命中字典。代表查詢只驗證摘要可檢索，不能代表官方全文已收錄。AQWA v261.1 documentation index、手冊正文是否需登入、以及圖片／表格的完整性未逐頁校對。


### 2026-10-31 FENSAP-ICE、Polyflow、EduPack 與其他線上來源補核

- FENSAP-ICE：核讀 v242 Graphical Environment tutorial 及 v242 Workbench Guide。字典補充 Project／Run 管理、FENSAP→DROP3D→ICE3D 資料相依、Fluent 匯入條件、網格公尺單位、教程所列 boundary tag 群組及模組相異的收斂指標；tag 與操作資訊保持 v242 教程版本範圍。v261 FENSAP flow chapter 本輪瀏覽擷取仍回報 cache miss，未以其他版本代替。
- Polyflow：核讀 v242 User’s Guide 的 planning、subdomains、boundary conditions 與 2024 R2 known limitations 頁。字典增加計算規劃、元素／connector 分群、subtask 間介面條件、外邊界覆蓋條件，以及版本限定的數量上限和相容性提示；公式和完整操作章節未快取。
- EduPack：核讀 v261 tools、filtering、process selection、Performance Index Finder 及 v251 Toolbar Guide。字典補充 Select／Chart／Eco Audit、Chart／Limit／Tree stages、ProcessUniverse 流程與 Level 3 功能條件。v261 與 v251 分開記錄；本機 CHM 仍是 0 正文，未抽取。
- Additive：v261 Tutorials PDF 可由官方 Help 開啟，封面標 Release 2026 R1；文件含 proprietary/confidential 及須依書面授權使用／複製聲明，本輪未下載、轉存或擷取正文。v261 PBF guide 擷取不可用；v251 Additive Print and Science PDF 約 13.2 MB，超出瀏覽擷取限制。維持來源與授權缺口記錄。
- LS-PrePost：v261 User’s Guide PDF 維持大型檔案未取得；v252 Basic Command Index 本輪官方頁擷取回傳錯誤，未新增正文。未用其他版本或第三方鏡像替代。

FENSAP-ICE、Polyflow、EduPack 的代表查詢及 `get_chunk` 驗證將在本輪索引同步後記錄；摘要不代表完整遠端手冊已納入 RAG。官方網頁均保留來源 URL，分享衍生摘要前須依各來源授權確認可用範圍。


代表檢索與片段擷取：FENSAP-ICE 的 `DROP3D total collection efficiency Beta`、`FENSAP Fluent import grid`、`Fluent dat cas airflow solution`；Polyflow 的 `subdomain boundary set connectors`、`CutCell MST moving parts`；EduPack 的 `ProcessUniverse Chart Limit Tree Stage`、`Performance Index Finder Level 3` 均命中字典並成功 `get_chunk`。FENSAP 較窄查詢 `Fluent cas dat files meters` 與 `coordinate meters boundary tags` 未命中，表示相鄰術語仍須依摘要實際用詞查找。這些查詢驗證的是本機摘要，不是遠端官方正文。


### 2026-10-31 EduPack CHM 解包與 HTML 全文索引

保留 `edupack/unknown/manuals/en.com.attributenotes.chm` 原件，使用 Windows `hh.exe -decompile` 將內容解至 `edupack/unknown/manuals/_en.com.attributenotes_decompiled/`。CHM 共解出 4,499 個檔案：1,491 個 HTML／HTM、其餘 3,008 個為圖片或其他資源。HTML 範圍含 Attribute Notes 與 Science Notes，英文 1,131、法文 117、葡萄牙文 121、西班牙文 122；版本標籤維持 unknown。

既有 `catalog --apply --product edupack` 轉換流程為 1,381 頁建立帶 SHA-256 sidecar 並標為 `body_present`；109 頁因正文不足或 HTML parser 品質問題列為 `attachment`，未進全文索引。另有 `Water_absorption.html` 內容與另一來源完全相同，清冊沿用一筆 canonical document ID，別名路徑記在來源狀態。`sources.csv` 新增 1,490 筆頁級來源列，保留 HTML 路徑、品質及 sidecar 字元數；原 CHM 仍標為 attachment 作為原始封裝檔。未把非 HTML 圖片資源納入全文索引，因此圖表圖片內容不保證可檢索。

RAG 抽查（product=edupack）：`Density specific gravity`、`water absorption`、`glass fiber water`、`Young modulus aluminum` 均命中 CHM 解包 HTML 並成功 `get_chunk`；`fatigue limit sheet steel` 未命中，需依來源實際詞面繼續查。這只驗證已抽取文字可搜尋，不代表材料數值已人工驗證或完整收錄。


HTML 全域轉換 manifest 已同步記錄此批：`html_conversion_manifest.json` 現有 171,899 筆轉換項目（converted 171,698、plain-text fallback 42、reused 49、failed 110）；filesystem HTML 572,288，其中 572,179 有可檢索 Markdown，109 頁未覆蓋。這批 EduPack 頁級來源列已進入 `sources.csv`；該清冊共 5,497 列，主題清冊共 307 項。


### 2026-10-31 LS-PrePost v252 官方 HTML 章節摘要

v252 User’s Guide root、Commands、Command Files、Command Line、Basic Command、File Menu 與 Configurations 官方 HTML 頁面可讀取。本頁摘要補充 `lspost.cfile` GUI 命令記錄與重播、`-nographics` 適用於不需 graphics operation 的流程、command-file 控制命令、常用檔案載入參數及 `.lsppconf` 位置；新增 6 筆 v252 URL 並將官方文件缺口主題改為部分完成。完整官方 HTML 正文未下載／未快取。

v261 PDF 搜尋到的封面資料標示 Release 2026 R1，並限制未授權的使用、散佈或複製；因此只保留 URL、版本與授權狀態，沒有下載 PDF 或將全文放進索引。這不推定 v252 HTML 章節與 2026 R1 PDF 的細節完全相同。

LS-PrePost 代表檢索（product=ls-prepost）：`lspost.cfile commandfile nographics`、`interactive resume skip endskip`、`d3plot h=time_history k=keyword`、`lsppconf AppData configuration` 均命中字典並成功 `get_chunk`。沒有啟動 LS-PrePost 或執行命令檔。


### 2026-10-31 RAL 色票 PDF 影像核對與轉換失敗分類

- 目視檢查 `Speos/unknown/manuals/RAL DESIGN StandardRGB (RGB).pdf` 的 1 頁渲染：主體為密集色票圖。PyMuPDF 可抽取 29 個字元（`RAL DESIGN`、`Colour Mode: sRGB`），不能還原各色塊標籤／色值。保留原 PDF、頁面影像與既有說明 Markdown；不使用 OCR 色值、不把圖像誤標成全文已轉換。
- 在 `sources.csv` 增列來源 ID `ansys_c0335fbc1d4d28c0748604f1`，狀態為附件／未索引，release 維持 unknown。
- HTML manifest 110 筆 failed 中，1 筆是 ACT v261 的 0-byte HTML，109 筆是 EduPack CHM 解包頁面因正文不足或解析品質低而排除。前者無可轉換正文，後者保留原 HTML 並列為品質缺口；目前未發現其他產品的 HTML 轉換失敗。
- 本輪失敗項目只做分類與影像核對，未重跑 PDF／HTML 轉檔；其餘已抽取 PDF 與已轉換 HTML 沿用既有 sidecar。
- 字典增量索引後 SQLite 有 596,414 筆 `docs_meta`、635,241 個 FTS chunks；唯讀 SQLite `PRAGMA quick_check=ok`，`index._needs_rebuild()` 為 `false`。`sources.csv` 共 5,504 筆且 ID 無重複；`topics.csv` 共 308 個主題。

### 2026-10-31 ACT v261 HTML 索引補正

- ACT archive 的 Project 與 Wizard index HTML 原本在 catalog 標為 attachment；其既有 Markdown 導覽 sidecar 已接回 catalog，品質標記更新為 `body_present`，保留原文件 ID，並補上 archive member URL。ACT 字典已加入兩頁的版本、用途及原文定位。
- Mechanical、Sherlock、Sound 的 unknown-release SDK 區共補登 76 個有同名 Markdown sidecar 的 HTML 路徑；來源版本仍標示 unknown。這些頁的內容可與已索引版本共用 FTS 片段；另一個 Mechanical redirect 與既有文件 ID 衝突，保留既有項目、不重複建立。
- 依既有 `build_index()` 完成整庫重建：596,492 筆 `docs_meta`、635,241 個 FTS chunks；`PRAGMA quick_check=ok`。抽查 ACT、Mechanical、Sherlock、Sound 各一組關鍵字搜尋並取回 chunk，均有來源路徑；ACT Project/Wizard 另直接取回兩個新接回的來源 chunk。搜尋抽查使用已完成重建的資料庫，略過重複的自動索引新鮮度掃描。
- HTML manifest 的既有 110 筆失敗狀態未變更：ACT 0-byte 頁與 109 個 EduPack 低品質頁仍為缺口；未嘗試 OCR。

### EnSight 來源與轉換抽查 2026-10-31

- EnSight 7 個字典主題已依 `topics.csv` 所列來源完成範圍內的版本／正文核對；API 範例未執行，solver integration、傳輸效能與第三方 viewer 相容性仍未驗證。
- 用 `pdfinfo` 核對三份版本未知 PDF 頁數，並與逐頁 Markdown 標記數比對：HowTo 436/436、HT-Manual 3/3、LocalHelp 1/1；Sidecar 有連續頁碼。`LocalHelp.pdf` 內含 `ensight242/site_preferences` 字串，只作內文版本線索，不據此推定其他兩份 PDF 的版本。
- 比對 v261 gRPC command/control、Shared Memory、DVS、GLTFWriter 官方正文與 v252 對應頁；核對 security token、18243 預設埠、同機限制與 DVS/GLTFWriter 版本差異說明。

### PrimeMesh 來源核對 2026-10-31

- v261 SP01、v252 Introduction 分別標明 Prime Mesh Python client library 隨附的修改版 PyPrimeMesh 0.10.2、0.9.0；SDK distribution 版本與 Ansys release 分開記錄。
- v261 Client、FileIO.read_pmdat、Mesh.surface_mesh、Mesh.volume_mesh 與 SurfaceDiagnosticSummary API 原文已核對；六個有足夠版本／來源證據的主題標為 complete，完整 v252／v261 API 差異仍為 draft。
- 本輪只做文件核對與索引查詢；未啟動 Prime Server、未讀取 PMDAT、未生成網格或診斷幾何，沒有宣稱 server 或網格行為已實測。

### 2026-10-31 System Coupling 官方頁面與字典核對

- 本機 System Coupling 目錄沒有 PDF，故本輪沒有 PDF 可轉換。來源清冊有 21 份可用正文，均為官方 Markdown 頁面及其 sidecar，已可直接納入現有全文索引；字典引用七組主題來源，來源 ID 和本機路徑均存在。
- 另 7 筆來源缺口保留原網址與原因：4 個舊 v261 URL 為 HTTP 404，對應 canonical 官方頁已下載並記錄；2 個 PyAnsys 範例與 1 個 Developer Portal landing page 為 DNS 解析失敗。未將失敗網址當成正文，也未以第三方鏡像替代。
- 已比對 v251/v252/v261 capabilities 和 v252/v261 concepts：v251 的 Mixed co-simulation and mapping 在 v252 表中拆成單一／多應用程式 mapping 與多應用程式 data transfer；v252 明列多應用程式 mapping 僅支援 C++ API，v261 另列 Mapping coupled analysis 及 attribute 上下界。差異已補入字典，限於所比對官方頁面。
- `topics.csv` 的 7 個主題改為 `complete`，其意義限於摘要所引來源及版本狀態已核對；完整 API 矩陣未逐項重編，也未執行 participant、MPI、mapping 或耦合求解。
- SQLite 鎖定後續探測：正式索引唯讀查詢成功、無 `-journal`／`-wal`／`-shm` 側檔，短暫 `BEGIN IMMEDIATE` 成功後立即 rollback；過去持鎖程序仍無法追認。本輪以交易更新索引中的 System Coupling 字典、README 與本核對紀錄，未重建全庫。
- SQLite 更新後有 596,492 筆 `docs_meta`、635,245 個 `chunks`；`PRAGMA quick_check` 為 `ok`，`index._needs_rebuild()` 為 `false`。產品篩選下，`Mapping coupled analysis Lower Upper attribute bounds`、`OutputScalarData OutputIntegerData 2026`、`element-based face-based point cloud node IDs` 均可搜尋並由 `get_chunk` 取回；`restart point callback outputs update` 另加 v261 release 篩選後可取回官方 restart 頁，結果來源路徑均存在。多版本字典頁 release 維持 `unknown`，加上 v261 篩選時不會回傳該摘要；過窄查詢 `callback restart identifier initialization` 未命中，改用來源原詞後可命中。此為 AND 關鍵字及版本篩選限制，不代表正文缺失。

### 2026-10-31 Mechanical 官方 HTML 來源延伸

- 由官方 v261 Mechanical User’s Guide 延伸核讀 Contact Region、contact／target scoping、Contact Workflow、advanced settings、contact diagnosis 與 convergence 頁；另核讀 v261 Results／Result File Items、v252 Review Results、Mesh error／warning limits、Check Mesh Quality 及 Messages Window。摘要保留來源 release，不將 v252 說明外推至 v261。
- `sources.csv` 新增 12 筆 `browser_summary_only` 官方來源，網址均為 `ansyshelp.ansys.com`。瀏覽器能讀取正文片段及頁面段落；原始 HTML 未鏡像到本機，也未作為 full-text source body 索引，只把繁中摘要納入 Mechanical 字典。
- 接觸主題增加 contact／target 選取提示、Contact Tool 初始狀態檢查及 formulation 版本條件；網格主題分開說明 error limit 與 warning／target limit；結果主題補入 Solution scope、結果檢視方式、精度與 `.rst` 資料限制；疑難排解主題補入 Messages Window 版本限制與 contact convergence 診斷線索。
- Mechanical 的接觸、網格、結果與疑難排解 4 個主題仍為 `draft`：官方線上摘要已擴充，但完整 HTML 正文尚未鏡像，網格理論、全套結果類型與通用 solver error handbook 仍未完成來源覆蓋。

Mechanical 字典代表檢索已用產品篩選搜尋並執行 `get_chunk`：`Contact Tool`、`initial penetration`、`error limit warning target Patch Conforming Tetra`、`single precision MAPDL NORSTGM`、`Messages Window Linux popup Information` 均可取回 Mechanical 字典片段及存在的本機路徑。較長組合查詢 `contact target finer mesh surface` 與 `Contact Tool initial penetration` 未命中；拆成來源實際詞面後可定位，反映目前全文搜尋採 AND 關鍵字匹配，不代表官方線上正文已鏡像或完整覆蓋。

Mechanical 字典及本核對紀錄以 SQLite 交易增量更新，未重建全庫。索引整體檢查與 `_needs_rebuild` 結果接續記錄於此核對段落；官方線上來源只透過字典摘要進入本機搜尋。

### 2026-10-31 LS-DYNA R16 能量／時間步 PDF 抽查

- 直接查看 R16 Vol. I PDF physical pages 1947、1955、1957 的頁面影像並對照逐頁 Markdown。確認 `GLSTAT` 是 global statistics/energies，`MATSUM` 是 part energies；逐項核對 energy 欄位表及兩者 kinetic energy 差異原因：mass-scaled mass、與 rigid body 合併的 nodes、nodal velocity 與 element-midpoint velocity 計算方式。Page 1955 implicit footnote 說明大時間步 integration error 可影響 kinetic／internal energy 估計。PDF 表格與轉換 sidecar 欄位順序相符。
- 對照 physical pages 1867–1868、1894–1895 的逐頁 sidecar，核對 `DTMIN`／`ENDMAS`、`DT2MS` 正負值、`ERODE` 相關選項及 mass-scaled time-step 說明；未把 R16 欄位行為推定成其他 solver release 的現行行為。
- `topics.csv` 將兩項主題明確限定為 R16 後標記 `complete`：GLSTAT／MATSUM 能量輸出與差異、時間步與 mass scaling。Keyword 卡全庫、LS-PrePost 全部 GUI／Python API、PyDYNA 與跨 release 差異仍是其他主題的待查範圍。

LS-DYNA R16 字典檢索已用文件限定查詢並 `get_chunk`：`GLSTAT MATSUM kinetic energy added mass`、`GLSTAT MATSUM nodal velocities element midpoint velocities`、`DT2MS TSSFAC Courant mass scaling`、`ENDMAS DTMIN ERODE tsmin` 均取回更新後摘要及存在的字典路徑。字典與 README、conversion_status 以 SQLite transaction 增量更新，沒有全庫重建。

本輪增量更新後索引核對：596,492 筆 `docs_meta`、635,251 個 `chunks`；唯讀 `PRAGMA quick_check` 為 `ok`，`index._needs_rebuild()` 為 `false`。

### 2026-10-31 optiSLang HTML／PDF 轉換與索引鎖定核對

- optiSLang 產品目錄有 577 份 HTML，逐一核對均有同名 Markdown sidecar，且 catalog 標為 `body_present`；本機相同目錄中的 2 份 PDF 也各有逐頁 Markdown。`pdfinfo` 頁數與 `## PDF Page N` 標記相符：LS-OPT 2026 R1 Manual 850/850 頁，Tutorial Problems 92/92 頁。
- 兩份 PDF 均屬 LS-OPT，不是 optiSLang 手冊。Manual 封面標示 Version 2026 R1；Tutorial Problems 封面標示 LS-OPT 6.0、2018 年。檔名含 `2026R1` 不構成該教學問題集的版本證據；來源仍由 LS-OPT 字典引用。
- SQLite 正式索引唯讀計數成功（596,492 筆 `docs_meta`）；短暫 `BEGIN IMMEDIATE` 後立即 rollback 成功，表示此探測時沒有鎖定阻礙。這不能追認先前鎖定程序的身分。
- optiSLang 字典與本核對段落已增量同步至既有全文索引，未重建全庫。代表搜尋及 `get_ansys_doc_chunk` 驗證見本段後續索引結果。
- 產品限定的 `DOESettings num_points sampling_method seed` 同時命中 v261 API 正文及字典；`Receive designs Send back designs evaluate_design` 命中字典、PyOptiSLang Design evaluation guide 與示例；`version stable REST API 2025 R2` 命中字典及官方 developer portal。各結果均成功 `get_ansys_doc_chunk`，來源路徑存在。搜尋結果也顯示 keyword AND 查詢可同時返回官方正文與字典摘要，並保留 release／SDK 未知值。泛查 `optiSLang HTML PDF conversion sidecar page marker` 未命中；依實際詞面縮窄成 `577 HTML sidecar` 與 `Manual 850 92 pages` 後，均命中本核對段落並成功取回片段。
- 最終索引核對：596,492 筆 `docs_meta`、635,252 個 FTS chunks，`PRAGMA quick_check=ok`，`index._needs_rebuild()` 為 `false`。沒有重建全庫，也沒有終止或檢查其他程序的持有控制代碼。

### 2026-10-31 PrimeMesh 版本標籤與品質判讀界線

- 比對官方 v252 及 v261 SP01 Introduction：前者稱隨附修改版 PyPrimeMesh 0.9.0，後者稱 0.10.2；SDK API index 的 0.10.5 是不同版本軸。兩個 Introduction 都列出品質檢查與幾何診斷能力，但不能據此推定 API 簽章相同。
- 將原 draft 主題收斂為「v252／v261 隨附 SDK 版本與品質判讀界線」並標為 `complete`：完成的是有來源支持的版本標籤及「拓樸診斷不等於網格品質允收」界線，不代表完整 2,500+ API 跨版比較或 solver 品質驗收。README 與字典同步更新。
- 新增字典摘要指出 `n_free_edges` 等診斷項目不能取代目標 solver 的品質指標與允收準則，並把工程建議標為依來源範圍推論。未啟動 Prime Server、未生成網格、未執行診斷或求解。
- 字典引用的 7 個來源 ID 均可解析到來源清冊及存在的本機正文。產品限定搜尋 `PyPrimeMesh 0.9.0 0.10.2 0.10.5`、`n_free_edges`、`quadratic parallel meshing` 都成功取回字典或官方 API chunk，路徑存在；`n_free_edges` 另命中官方結果 API。
- 過窄的 AND 查詢 `n_free_edges geometry diagnostic mesh quality` 未命中；`volume_mesh growth_rate` 只命中字典摘要。依來源原用詞查 `n_free_edges`、`quadratic parallel meshing` 後可定位官方 API，這反映關鍵字全文搜尋限制，不代表缺少對應來源。

### 2026-10-31 Installation & Licensing 2026 R1 快速指南

- `quickstartinstall.pdf` 與 `quickstartlic.pdf` 的 `pdfinfo` 都顯示 8 頁；各自的 Markdown sidecar 有 8 個 `## PDF Page N` 標記。封面與重要事項確認 release 2026 R1；保留兩份 PDF 原件及逐頁轉換，不修改來源正文。
- 擴展閱讀官方 v261 Installation Guides PDF、Windows／Linux 安裝章節、Licensing Guide、Licensing Settings Utility 與 License Management Guide。瀏覽器可讀取相關內容；新增 6 筆 `browser_summary_only` 來源，空白本機路徑及 `indexed_chars=0`，未宣稱已鏡像官方全文。
- 字典補入 release 順序與 side-by-side 條件、Windows/Linux 安裝入口、client／server 角色、existing/new customer 授權流程、License Management Center 與 client Licensing Settings Utility 的區別、設定讀取優先序，以及 v261 文件列出的預設 port 2325／1055 和 VENDOR 行自訂 port。網路埠與升級資訊均限定 v261；實際環境要按 license file 與組織設定核對。
- `topics.csv` 的兩個 Quick Start 主題改為 `complete`，完成範圍限於本機 2026 R1 Quick Start 與引用的 v261 線上摘要；完整平台手冊、特殊 licensing 模式及 troubleshooting 未鏡像，License Manager 未在本機設定或啟動。
- 產品限定搜尋 `Release 2026 R1`、`Install Ansys License Manager`、`System Hostid Information`、`2325 FlexNet 1055`、`Ansys Licensing Settings User`、`ansyslmd.ini SERVER` 均回傳片段並成功 `get_ansys_doc_chunk`，來源路徑存在；結果包含兩份本機 Quick Start PDF 與字典摘要。
- 過窄查詢 `side-by-side chronological license manager`、`Get System Hostid Add A License File`、`User Installation ansyslmd.ini SERVER environment variable`、`FlexNet LicensingSettings SERVER`、`FlexNet server order checkout` 未命中。依來源實際詞面改查後可命中；全文搜尋採關鍵字 AND，查詢 miss 不代表來源缺失。
- 字典、README 與本核對段落以 SQLite transaction 增量更新；索引健康檢查結果接續記錄於本段。

### 2026-10-31 Polyflow v261 Workspace 與 Classic 指南擴充

- 由官方 v261 Fluent User’s Guide 核讀 Polyflow Workspace Introduction／Getting Started：確認其 Fluent workspace 定位、相對 Classic 的 successor 關係、主要工作流程、授權前置與 §2.1.4 已知問題。另核讀 v261 Polyflow Classic User’s Guide §1.5.2–1.5.3。
- `sources.csv` 新增 3 筆 v261 `browser_summary_only` 來源；來源網址保留在清冊，local_path 空白、indexed_chars 為 0。官方 PDF／HTML 正文未下載或鏡像；本輪只將繁中摘要納入本機檢索。
- v242 與 v261 Classic 指南所查章節在 subdomain／sub-task 關係、跨 sub-task interface boundary、外邊界覆蓋要求及 300／500／10,000 數量上限一致。跨版核對只限這些章節；未外推整本手冊或其他 release。
- 字典與 `topics.csv` 新增／更新兩個有界主題：v261 Workspace workflow／licensing／known issues，以及 v242／v261 Classic 子域、邊界集合與上限。廣泛的材料模型及黏彈性物理範圍仍為 `source_limited`。
- 來源引用核對後，兩個 bounded topics 的 8 個引用均能解析到 `sources.csv` 且有 URL；本機來源路徑若有填寫均存在。3 個新增 v261 URL 保持 browser-summary-only，原文正文未索引。
- 產品限定查詢 `Define modeling goals compatible mesh`、`template wizard Compute solution`、`internal boundaries subdomains different sub-tasks`、`workspace license HOME`、`limited Academic License elements OneDrive` 均搜尋到更新後的 Polyflow 字典並成功 `get_ansys_doc_chunk`，字典來源路徑存在。
- 較泛查 `Define modeling goals compatible mesh template wizard`、`subtask boundary conditions same task interface` 未命中；加入字典中的官方英文詞組後，較窄的 workflow／boundary queries 可命中。全文搜尋採 AND 關鍵字，不提供語意擴展。
- 字典與本核對段落使用 SQLite transaction 增量更新，未重建全庫；本輪最終索引健康狀態接續記錄於本段。

### 2026-10-31 本機 PDF／HTML 轉換缺口總核對

- 逐檔核對 `docs/ANSYS_Document` 的 PDF 同名 sidecar：目前 0 份 PDF 缺 Markdown；既有 PDF 清冊為 273 筆，其中 262 筆已抽取、10 筆重複指向 canonical 來源、1 筆失敗。唯一失敗是 Speos 色票掃描 PDF，無可抽取文字，維持待 OCR；未改原件。
- HTML manifest 記錄 171,899 項，其中 171,698 `converted`、42 `plain_text_fallback`、49 `reused_existing_markdown`、110 `failed`。失敗項分為 1 個零位元 ACT HTML 與 109 個 EduPack Attribute Notes 短定義頁；原始檔均保留，短定義未為了通過字數門檻而補造正文。其餘未納入 HTML 清冊的素材或未下載的官方線上頁，不能視為已完成轉換。
- 這是清冊核對，沒有執行整批重轉；下一步應處理 EduPack 短定義的明確品質規則或掃描件 OCR，再逐項核驗。REA 萃取目錄未納入掃描或轉換。
- `conversion_status.md` 以單文件 SQLite transaction 增量更新為 53 chunks／60,406 字元；`PRAGMA quick_check=ok`、`index._needs_rebuild()=False`。trigram 全文查詢 `sidecar`、`短定義` 命中本核對紀錄並可取回 chunk。未重建整庫，也未掃描／改寫 REA 萃取檔。

### 2026-10-31 IcepakFEA AssignTemperature 主題核對

- 逐頁核對本機 v261 `IcepakFEAScriptingGuide.pdf` 及 Markdown sidecar Pages 957–958：確認 `AssignTemperature (<NAME>, <Faces>, <Temperature>)`、參數型別描述、`90cel` 範例，以及 `oModule.Edit()` 可改名稱／溫度但不可改 Faces assignment。另對照 Pages 959–960 的 Structural design `AssignThermalCondition`，避免混用 Thermal boundary 和 Structural excitation。
- 擴充 [Icepak 字典](icepak.md)中的命令語義、變更 Faces 的替代命令及版本／範例限制；只將 `IcepakFEA 溫度邊界 AssignTemperature` 這個有界主題標為 complete，其他 Icepak 主題狀態不變。來源 `ansys_e6e6c75160f5628b306a53ac` 的原件、sidecar 與清冊路徑皆存在。
- 產品限定全文檢索 `AssignTemperature Faces 90cel` 命中 v261 官方 PDF sidecar chunk 796；另一查詢 `Edit AddAssignmentTo RemoveAssignmentFrom Reassign` 命中同手冊多個片段。明確以字典文件 ID 查詢也命中更新後的 Icepak 字典；字典與來源兩邊的 `get_chunk` 均成功，片段含 `AssignTemperature`、`90cel` 與 PDF Page 標記。SQLite 僅增量更新字典與本紀錄，索引健康結果於更新後核驗。

### 2026-10-31 Workbench scripting 與 journal 範圍

- 核對 v261 Workbench Scripting Guide printed pages 5–8 及 PDF／Markdown 清冊：native workspace 的資料修改可 journal 並由 Workbench scripting 自動化；data-integrated application 只有由 Project Schematic 發起的部分操作會記錄，內部操作不一定受 Workbench journal 控制。依 Table 1 僅整理表格明確列出的 `SendCommand` scripting／journaling 支援；空白欄位不推定為 No。
- 擴寫 [Workbench 字典](workbench.md)並把 `Project Schematic 與流程自動化` 標為 complete，範圍限於 scripting／journal 邊界、支援表和 command-line 入口；未宣稱 Workbench 可完整記錄各整合產品的內部流程，未執行 Workbench。
- 產品限定查詢 `native workspace data-integrated journaling`、`SendCommand ICEM CFD Not Available` 命中 v261 PDF 與轉換 Markdown；兩者 `get_chunk` 成功，片段回到原始手冊。來源 `ansys_05b664ec1d5ee31846d738a4`、`ansys_bf146052ec7716d8122c2318` 的檔案存在，索引健康狀態於更新後核驗。

### 2026-10-31 SCADE Suite Libraries 導覽與頁碼修正

- 核對 `LibrariesManual_SCS-LM-26.pdf` 原件及逐頁 sidecar physical Pages 22–25（手冊 printed pages 1–5）：整理八個 library 的概覽用途、`libsmlk`／`libverif` 安裝前置、`libimpl`／`libmathext` C-code platform-dependency 提醒，以及 qualified／certified use 的驗證責任。產品 release 維持 unknown。
- 修正 SCADE 字典先前把 printed page 當作 PDF physical page 的錯誤連結：manual overview 的實體頁碼由 `#page=5` 改為 `#page=22`，並連至 Markdown 的 `PDF Page 22`；將 `SCADE Suite libraries` 標為 complete，完成範圍僅是 library 功能導覽，不包含逐一 operator 行為驗證。
- 產品限定搜尋 `libdigital liblinear Boolean integrators` 命中官方手冊 chunk 14（含 PDF Page 22）；`Design Verifier libverif` 命中手冊 chunk 17／18（含 PDF Page 25）。字典文件 ID 查詢 `libdigital liblinear` 命中更新後的繁中詞條，兩類文件的 `get_chunk` 均成功。來源 `ansys_0dd0b464ab6f67a26baa69dd` 的 PDF 與 sidecar 均存在，頁碼標記可回查。

- 同一 SCADE Language Primer 詞條核對 physical PDF Pages 13–17（printed pages 2-3–2-7），補上 flow、`pre`、初始化 `->`、`fby`、`when`、clock discipline 和 complementary-flow merge 的限界說明；把原合併的 state machine topic 分拆為待核對草稿，避免把目錄摘要當成已整理正文。舊的 `#page=6` 會跳到前置頁，已修正為 `#page=13`。
- `flow pre initialization fby`、`when clock discipline complementary flows` 產品限定查詢命中 SCS-PM-25 PDF chunks 9–11；`get_chunk` 成功，片段含 PDF Pages 15–17 標記。文件版本欄維持 unknown，不以文件代碼 SCS-PM-25 推定產品 release。

### 2026-10-31 Twin Builder FMEA Toolkit 流程主題

- 核對本機 `FMEA_Toolkit_Manual.pdf` 與 sidecar physical Pages 5–11、13–14：收錄模型準備順序、FMEA component／normal-mode 檢查、`FAULT_MODE`／`FMEA_MODE` 切換、`T_START` 時間 offset、case setup、no-fault baseline、scenario sheets 與 severity/result 處理。來源 release 維持 unknown；手冊不含個別 component failure-mode 完整規格。
- 擴寫 [AnsysEM 字典](ansysem.md)，並將 `Twin Builder FMEA Toolkit 建模、情境與 severity` 標為 complete，完成範圍限該流程指南，不外推為 FMEA library component 全目錄。
- 產品限定搜尋 `FMEA Toolkit FAULT_MODE FMEA_MODE T_FAIL T_START` 命中原 PDF 與字典；`FMEA_Scenario Plot_Scenario` 命中 scenario sheet 說明，`get_chunk` 皆成功，原文片段可回查頁碼或文件來源。來源 `ansys_7cf3733a03d966fc207c5ab0` 的 PDF／sidecar 存在。

### 2026-10-31 EMIT Tutorials 1–8 頁碼導覽

- 八份來源均為本機 Release 2026 R1 PDF；逐一用 `pdfinfo` 對頁數，Markdown sidecar 的 `## PDF Page N` 標記完整且數量一致：Tutorial 1 38/38、2 27/27、3 36/36、4 34/34、5 20/20、6 36/36、7 20/20、8 26/26。來源 ID 與路徑已列在 `topics.csv` 及 [AnsysEM 字典](ansysem.md)，原始 PDF／sidecar 未重轉或修改。
- 逐份核讀 PDF physical Page 5 目錄、Page 6 前言與 Pages 7–15 的起始步驟，建立八項主題及原件頁碼：單一 Tx/Rx 與 filter、multi-channel／frequency hopping、N-on-1 與 intermodulation、CAD／ATA coupling、WiFi 6 susceptibility、Elements Library／大型情境、製造商規格表 radio model、IoT Module／desense。`topics.csv` 標記 `complete` 僅表示八份導覽與頁碼定位已整理，不表示全份操作流程、圖表或參數均已逐項整理。
- 產品限定搜尋逐份代表詞 `fixed coupling filter`、`random sampling`、`N-on-1 analysis`、`ATA Coupling Matrix`、`802.11ax`、`EMIT Elements Library`、`manufacturer`、`desense` 均回傳對應 Tutorial 1–8 PDF，八次 `get_chunk` 均成功且來源路徑存在。過窄組合詞 `ABC Communications specification sheet mixer products` 未命中；拆用原文詞 `manufacturer` 後找到 Tutorial 7（全文 AND 關鍵字限制）。
- SQLite 寫鎖探測成功：正式 DB 可唯讀開啟，沒有 `-wal`／`-shm`／`-journal` 側檔；本輪 `BEGIN IMMEDIATE` 成功後完成字典增量交易。先前鎖定事件的持有程序仍無法由當前狀態回溯辨識。
- 最終索引有 596,492 筆 `docs_meta`、635,275 個 FTS chunks；`PRAGMA quick_check` 為 `ok`、`index._needs_rebuild()` 為 `false`。字典主題查詢與本核對紀錄查詢均成功 `get_chunk`，來源路徑存在；未重建全庫。

### 2026-10-31 LS-DYNA R16 MAT 索引與元素形式

- 核對來源 `ansys_46cea1557af4f2db5b745cbd`：R16 Vol. II 原 PDF 與逐頁 Markdown 均存在，`pdfinfo` 顯示 2,174 頁，sidecar 有 2,174 個 `PDF Page N` 標記；physical Pages 71–75 已抽查。來源 release 欄維持 `unknown`，不把封面內部 R16 revision 代碼轉成產品 release。
- [LS-DYNA 字典](lsdyna.md)新增 R16 Vol. II MAT 索引讀法：數字／描述 keyword 同義對照、方括號中的元素形式代碼、`{n}` 額外 history variables、type 16／type 2 積分點計數示例、`8A`／`8B` 狀態與手冊警告，以及 `TITLE` 和 `*MAT_ADD_*` 的用途界線。新增 `R16 MAT 索引讀法與元素形式` 有界主題並標為 `complete`；完整材料卡欄位、選型依據及跨版差異仍待整理，原「Keyword 與模型控制」主題維持 `draft`。
- 產品限定 `MAT_024 MAT_PIECEWISE_LINEAR_PLASTICITY`、`8A 8B multi-material ALE validated`、`history variables integration point` 均命中 R16 Vol. II 原文並成功 `get_chunk`；以字典文件 ID 限定的 `MAT_024 PIECEWISE_LINEAR_PLASTICITY`、`8B history variables`、`*MAT_138 cohesive` 也均命中字典並成功取片段，來源路徑存在。
- 索引採 SQLite transaction 僅替換 LS-DYNA 字典文件，未重建全庫；最終健康檢查將在本段更新後再核對。

### 2026-10-31 PyOptiSLang root-level Design evaluation

- 核對本機官方 PyOptiSLang `version/stable` Design evaluation 與 Create workflow HTML／Markdown 正文（來源 `ansys_f4ea249bfc415bbfdee90f7f`、`ansys_74392f3b50b669e7845198e1` 均為 `body_present`）。它們所在來源清冊 release 為 `unknown`；沒有把旁邊 1.7.0 API reference 的目錄名稱當作此頁版本證據。
- [optiSLang 字典](optislang.md)整理 root-level workflow 前置、保存專案副本、由 reference／scratch 建立 design、評估結果及最後一筆資料保存限制。新增 `PyOptiSLang root-level 單筆 Design evaluation` 有界主題標為 `complete`；整體 `PyOptiSLang 與 Web API` 主題仍為 `draft`，DOE／Sensitivity／Optimization 等內容未被此完成項涵蓋。
- Design evaluation 頁正文在參數檢查段落有名稱差異：連結文字指向 `get_missing_parameters_names()`／`get_undefined_parameters_names()`，緊接程式碼卻呼叫 `get_missing_parameters()`／`get_undefined_parameters()`。本機目前沒有相應 RootSystem API 正文解決差異，字典已明示需依安裝版本確認；未執行 optiSLang。
- 以文件 ID 限定搜尋 `evaluate_design` 命中 Design evaluation 原始文件並成功 `get_chunk`；字典查詢 `evaluate_design`、`Design evaluation`、`Receive designs Send back designs` 均可取回摘要片段。過窄 AND 查詢 `get_reference_design evaluate_design last evaluated design` 未命中，縮為 `evaluate_design` 後命中；README 的 `311` 查詢亦成功取回更新後目錄片段。
- optiSLang 字典、README 與本核對段落透過 SQLite transaction 增量同步；未重建全庫。更新後正式索引有 596,492 筆 `docs_meta`、635,280 個 FTS chunks，`PRAGMA quick_check=ok`、`index._needs_rebuild()=false`；字典、來源文件與 README 查詢均成功取回片段。

### 2026-10-31 Mechanical v261 Result File Item scoping

- 官方 Mechanical User’s Guide v261 §19.2.4 已透過線上頁核讀；頁面 URL 為 `ds_sol_comp_output.html`，來源 `web_mechanical_result_items_v261` 在 `sources.csv` 標記 `browser_summary_only`，無本機 HTML 或正文路徑。原始 PDF／HTML 未下載或鏡像；本機只有字典摘要可全文檢索。
- [Mechanical 字典](mechanical.md)整理 Result File Item 的材料／元素／component／節點範圍、Solution Summary Worksheet 資訊來源、scoping 輸入方式，以及 SECNUM／REAL 條件、cyclic symmetry averaged result、Condensed Part 和 reinforcement Global IDs 等適用界線。`topics.csv` 新增 `v261 Result File Item 結果範圍` 有界完成項目；整體結果與後處理主題仍為 `draft`。
- Mechanical 字典文件 ID 限定查詢 `Result File Item Scoping Method`、`Element Type IDs SECNUM REAL`、`Cyclic symmetry Averaged Unaveraged`、`Condensed Part Material IDs` 均命中字典，`get_chunk` 成功；產品篩選查詢 `Result File Item SECNUM REAL` 和 README `312` 亦可取回片段。
- Mechanical 字典、README 與本核對紀錄以 SQLite transaction 增量同步，沒有全庫重建；資料庫健康檢查在更新後核驗。

### 2026-10-31 LS-PrePost v261 Solution Explorer

- 核對 Release 2026 R1 `Ansys_LS-PrePost_Users_Guide.pdf` 與逐頁 Markdown：`pdfinfo` 顯示 1,070 頁，sidecar 有 1,070 個 `PDF Page N` 標記；physical Pages 1035–1040 對應 printed pages 1007–1012，章節標為 Solution Explorer。原始 PDF／Markdown 未修改。
- [LS-DYNA 字典](lsdyna.md)補齊 Solution Explorer tree／Property Explorer、solution 建立欄位、Length unit／mesh 對應、case type 組合、內建 validation status、`Case Chained` 對 `*.dynain.lsda` 狀態延續及 `Keyword Version`。新增 `v261 LS-PrePost Solution Explorer 與 chained cases` 有界主題並標記 `complete`；整體 LS-PrePost GUI 與 Python module API 主題仍為 `draft`。
- 以字典文件 ID 查詢 `Solution Explorer Working Directory Unit System Case Type`、`Case Chained dynain.lsda Keyword Version`、`validation status Property Explorer` 均命中且 `get_chunk` 成功。原文限定查詢 `Keyword Version dynain.lsda` 命中 v261 LS-PrePost PDF sidecar 並可取片段；較窄的組合查詢 `Solution Explorer Case Chained` 未命中，全文檢索採 AND 關鍵字。
- [README](README.md) 主題狀態總數已同步更新；字典與 README 以 SQLite transaction 增量更新，未重建全庫。索引最終健康狀態於同步本核對紀錄後驗證。

### 2026-10-31 PyDYNA FieldSchema／CardSchema／field_writer

- 核對來源 `ansys_434b092c13a7f368346c0de6`、`ansys_9ca8f89b743c6433da81bb88`、`ansys_67a6484662f1892256a25678`：三份官方 API HTML 與 Markdown sidecar 均存在且標為 `body_present`；來源清冊 release 欄皆為 `unknown`，檔案路徑在 `ansys-dyna-core/0.12.1` 目錄下，未把目錄名稱寫成來源頁明示版本。
- [LS-DYNA 字典](lsdyna.md)擴寫 immutable `FieldSchema`／`CardSchema` 的欄位及方法摘要、`get_index()` 的 `KeyError`、`field_writer` 支援的 buffer／CSV／Hollerith 導覽與版本／求解器相容性界線。新增 `PyDYNA FieldSchema/CardSchema 與序列化` 有界完成主題；完整 PyDYNA API 仍列 `draft`。
- 字典 ID 限定搜尋 `FieldSchema display_name is_flag signature`、`CardSchema name_to_index get_index KeyError`、`write_fields_csv Hollerith buffer` 均命中並成功 `get_chunk`。原始來源文件各以 `FieldSchema display_name`、`get_index`、`write_fields_csv Hollerith` 查詢並成功取回片段；組合詞 `name_to_index get_index` 未命中，使用單一 API 符號後可定位。
- 字典與 README 以 SQLite transaction 增量同步，未重建全庫；索引健康檢查在本核對紀錄同步後執行。

### 2026-10-31 Mechanical v252 Mesh Quality Worksheet

- 透過官方 v252 Meshing User’s Guide 頁面核讀 `Check Mesh Quality`：<https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/wb_msh/msh_check_mesh_quality.html>。頁尾標示 Release 2025 R2。來源 ID `web_mechanical_mesh_quality_v252` 維持 `browser_summary_only`；頁面未鏡像成本機 HTML，原文沒有加入本機索引。
- [Mechanical 字典](mechanical.md)補上四種檢查模式、worksheet 指標及顏色解讀、Sheet／Solid／Solid-Surface 範圍、CSV 與 Named Selection 輔助功能，以及一般 mesh 與 Mesh Workflow 的 Error Check 行為差異。新增 `v252 Mesh Quality Worksheet` 有界主題並標為 `complete`，只代表本頁列出的 GUI 功能已整理；整體「網格與品質」仍為 `draft`，完整理論和 v261 對照仍缺。
- 對 Mechanical 字典文件 ID 查詢 `Mesh Quality Worksheet Warning Limit Error Limit`、`Mesh Workflow Error Check`、`Physics Preference CSV Named Selection` 均找到摘要片段；三個結果均可由 `get_chunk` 取回。README 的主題數查詢亦沿用現有索引。
- 正式 DB 的短逾時 `BEGIN IMMEDIATE` 鎖探測成功並立即回滾，唯讀連線可開啟，且沒有 `-wal`／`-shm`／`-journal` 側檔；這只能證明探測當下沒有其他持鎖者，先前鎖定事件的持有程序無法從目前狀態回溯辨認。DB 以 transaction 增量更新 Mechanical 字典與 README，再加入本紀錄；未重建全庫。

### 2026-10-31 SpaceClaim v251／v261 Move tool

- 沿用已轉換並索引的 SpaceClaim Documentation PDF sidecar：v251 與 v261 原 PDF 均為 `body_present`，各自的逐頁 Markdown 也存在。只抽查並比對兩版第 4.4.3.2–4.4.3.4 節（PDF physical pages 289–293）；正規化版本頁尾後，該範圍正文完全一致，未重新轉換或修改原件／sidecar。
- [SpaceClaim 字典](spaceclaim.md)新增 Move tool guides、`Up To` 雙擊複製行為、trajectory 上移動凸起時的重新接合／rounds 移除，以及 Move Handle 平移、旋轉、複製、平面拖曳與重新定向摘要。新增 `v251-v261 Move tool guides and handle` 有界主題並標 `complete`；全部 Move options、patterns 與 beam 專用步驟不在此項涵蓋範圍。
- SpaceClaim 字典查詢 `Move Direction Anchor Up To`、`Move Along Trajectory rounds` 均命中並可取回片段；原始文件產品限定查詢 `Move Direction Anchor Fulcrum` 及 `Move handle Ctrl Alt` 亦可定位手冊並成功 `get_chunk`。README 主題數查詢將依本輪同步後的清冊數核對。
- 只以 SQLite transaction 增量更新 SpaceClaim 字典、README 與本核對紀錄；不重建全庫。原始 PDF、既有 Markdown sidecar 及 REA 萃取內容未修改。

### 2026-10-31 PyOptiSLang existing-project ParametricDesignStudy

- 核讀官方 `version/stable` 頁 `Create a design study from an existing project`，本機 HTML sidecar 為 `body_present`、索引正文 9,794 字元，來源 ID `ansys_9725144e31748eae675b50b0`；來源清冊 release 維持 `unknown`，沒有從 `ansys-optislang-core/1.7.0` 資料夾名稱推定頁面版本。範例要求先由另一個官方 Robust design with optimization with proxy solver 範例建立 `.opf` workflow。
- [optiSLang 字典](optislang.md)摘要既有 workflow 的 `ParametricDesignStudyManager`、節點包裝、`ExecutableBlock`／`ExecutionOption` 分組、validator 起訖點，以及 reset／save／execute／dispose 順序。新增 `PyOptiSLang existing-project ParametricDesignStudy` 有界主題並標 `complete`；合成 callback 不是工程求解器，來源未涵蓋空白 workflow 建構。本機未執行 optiSLang。
- 字典文件 ID 限定查詢 `ParametricDesignStudyManager`、`ExecutableBlock`、`manager.reset` 均命中並可 `get_chunk`；`ACTIVE STARTING_POINT END_POINT Validator` 也命中。組合查詢 `ParametricDesignStudyManager ExecutableBlock ExecutionOption` 與 `ExecutionOption STARTING_POINT` 未命中。原始 HTML 限定查詢 `ParametricDesignStudyManager`、`design_study.execute`、`manager.save dispose` 均成功取片段；組合詞 `ParametricDesignStudyManager manager.reset` 未命中。產品限定 `ExecutableBlock ProxySolverManagedParametricSystem` 找到官方 example 並可取片段。
- SQLite transaction 僅增量更新 optiSLang 字典、README 與本核對紀錄；不重建全庫。原始 HTML sidecar及 REA 萃取內容未修改。

### 2026-10-31 LS-DYNA R16 `*MAT_024`

- 核讀 R16 Vol. II `*MAT_PIECEWISE_LINEAR_PLASTICITY` 原 PDF physical pages 327–333及既有逐頁 Markdown sidecar。PyMuPDF 顯示來源 PDF 共 2,174 頁；抽查原頁可確認 page 327 的 Material Type 24／options、page 328 欄位卡、page 330 的 `FAIL`／`TDEL` 定義、page 331 的 `VP`／`EPS1–EPS8` 說明及 page 333 的 history-variable 範圍。來源清冊 release 保持 `unknown`。
- [LS-DYNA 字典](lsdyna.md)補入 `EPS/ES` 點列、`LCSS` curve/table 的互斥與忽略條件、`FAIL`／`TDEL`、`VP` 應變率方式、`VP=3` history variables，以及 `LOG_INTERPOLATION`、`STOCHASTIC`、`MIDFAIL`、`2D` option 限制。新增 `R16 MAT_024 Piecewise Linear Plasticity` 有界主題標為 `complete`；完整材料卡、選材依據和參數建議仍未涵蓋，整體「Keyword 與模型控制」維持 `draft`。
- 字典文件 ID 限定查詢 `MAT_024 LCSS EPS1 ES1`、`FAIL`、`VP=3 history variables MIDFAIL` 均命中且可 `get_chunk`；過窄組合 `FAIL TDEL effective plastic strain` 未命中，縮成 `FAIL` 或 `TDEL` 後命中。原始 Vol. II 限定查詢 `effective plastic strain LCSS load curve`、`STOCHASTIC MIDFAIL 2D` 均命中原文並成功取片段；來源路徑存在。
- SQLite transaction 增量更新 LS-DYNA 字典與 README，未重建全庫；本核對紀錄同步及最後健康檢查將在下方完成。REA 萃取內容未修改。

### 2026-10-31 Mechanical v261 Investigating Contact Regions

- 核讀官方 Mechanical User’s Guide v261 頁面 `Investigating Contact Regions`（footer Release 2026 R1）：<https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_sim/ds_contact_best_prac_setup.html>。來源 ID `web_mechanical_contact_inspect_v261` 維持 `browser_summary_only`，沒有本機 HTML；全文索引只包含字典摘要，不能直接搜尋該頁完整正文。
- [Mechanical 字典](mechanical.md)補充 body 對應 contact regions 的 `Go To`、Contacts Worksheet 排序／欄位顯示、Contact Tool 求解前狀態及 contour、無接觸 bodies／parts 的定位方式和 multibody part 的適用界線。新增 `v261 Contact Region investigation and worksheet` 有界主題標 `complete`；更廣的「接觸與邊界條件」仍為 `draft`。
- Mechanical 字典 ID 限定查詢 `Go To Contacts for Selected Bodies`、`Connections Worksheet`、`Locating Parts Without Contacts` 均命中摘要並成功 `get_chunk`；產品限定 `Contact Tool Status Penetration active inactive` 及 README `319 個主題狀態` 亦成功。過窄查詢 `Connections Worksheet sort columns` 未命中，因摘要保留 GUI 名稱、用繁中整理排序／欄位功能；以 `Connections Worksheet` 後命中。
- SQLite transaction 增量更新 Mechanical 字典與 README，再同步此核對紀錄，未重建全庫。REA 萃取內容未修改。

### 2026-10-31 PyDPF-Core Operators

- 核對官方 `version/stable` Operators 使用指南及本機 HTML／Markdown sidecar：source ID `ansys_bd5ad5d1ea0c402d09afbbfb`、quality `body_present`、索引正文 15,566 字元，metadata SDK version 為 0.16.3；來源頁 URL 為 stable，release 欄維持 `unknown`，不推定此頁精確發布版本。
- [DPF 字典](dpf.md)新增 operator descriptor、必要／選用輸入、`DataSources`、輸出時評估及未提供輸入時 `DPFServerException` 的流程摘要；也整理 workflow chain、在 DPF 端做 `min_max` 降低大型結果傳輸，以及 operator 個別授權界線。新增 `PyDPF-Core Operator inputs, connections and evaluation` 有界主題標 `complete`；全部 operator pin 和 plugin 開發仍不在範圍，五個較廣 DPF 主題仍為 `draft`。
- DPF 字典文件 ID 限定查詢 `data_sources DPFServerException`、`min_max field_max`、`DPFServerException`、`license checkout` 均命中並可 `get_chunk`；過窄詞組 `min_max field_max data transfer` 未命中。原始 Operators 文件 ID 限定查詢 `DataSources`、`missing inputs DPFServerException`、`field_max displacement` 均命中並可取片段；`DataSources required inputs evaluate` 未命中。README 的 `320 個主題狀態` 查詢成功。
- SQLite transaction 增量更新 DPF 字典與 README，再同步此核對紀錄；未重建全庫。REA 萃取內容未修改。

### 2026-10-31 PyFluent session ownership and cleanup

- 核對官方 `version/stable` Using PyFluent sessions 頁及本機逐頁 sidecar（source ID `ansys_a79a80046f30ff1aec049a1c`，SDK metadata 0.42.1）；頁面網址為 stable，source release 欄為 `unknown`，未推定精確 patch／產品 release。
- [Fluent 字典](fluent.md)補充 launch method 建立的 session 呼叫 `.exit()` 會終止 Fluent process、`from_connection()` 附加既有 process 預設不終止該 process、`cleanup_on_exit` 可設定清理行為，以及 garbage collection／interpreter 結束時的隱式退出規則。新增 `PyFluent session ownership and cleanup` 有界主題標 `complete`；產品版與 SDK 相容性、完整 cleanup 參數行為尚未整理。
- 字典文件 ID 限定查詢 `from_connection cleanup_on_exit exit`、`garbage collector interpreter session exit` 均命中並成功 `get_chunk`。原始 session sidecar 查詢 `from_connection`、`cleanup_on_exit`、`exit terminates Fluent session`、`interpreter session garbage collected` 均成功；合併詞組 `from_connection cleanup_on_exit` 未命中。README `321 個主題狀態` 查詢成功。
- SQLite transaction 增量更新 Fluent 字典與 README，再同步此核對紀錄，未重建全庫。未在 Fluent session 實際呼叫 `.exit()`；REA 萃取內容未修改。

### 2026-10-31 PyMAPDL non_interactive buffering and query timing

- 核對官方 PyMAPDL `version/stable` language and usage 頁及本機 Markdown sidecar：source ID `ansys_b81b6dd45d8b13e1effda070`，quality `body_present`、索引正文 41,519 字元，SDK metadata 0.74.1；網址使用 stable，release 欄維持 `unknown`。
- [MAPDL 字典](mapdl.md)補充 `mapdl.non_interactive` 如何先緩衝 APDL 命令、離開 context 才寫 input file 並呼叫 `Mapdl.input()`，以及 context 內 `get_array()` 可先於緩衝命令執行而讀到舊狀態；另記錄 context 後查看 `last_response`。新增 `PyMAPDL non_interactive buffering and query timing` 有界主題標 `complete`；父級 APDL wrapper 主題仍為 `draft`。
- MAPDL 字典查詢 `non_interactive get_array last_response`、`context input file APDL buffer` 均命中並成功 `get_chunk`；原始 sidecar 限定查詢 `non_interactive get_array`、`Mapdl.last_response input file` 亦成功取片段。README `322 個主題狀態` 查詢成功。
- SQLite transaction 增量更新 MAPDL 字典與 README，再同步本核對紀錄，未重建全庫；未在 MAPDL runtime 執行命令，REA 萃取內容未修改。

### 2026-10-31 PyACP geometric selection rules

- 核對 PyACP 官方 `version/stable` Basic selection rules 範例及本機 HTML／Markdown sidecar（source ID `ansys_c6f794a6f8190d9d9b7679ec`，SDK metadata 0.4.1、`body_present`、索引正文 7,245 字元）。來源頁未標精確 patch release，未從 stable URL 推定版本。
- [ACP 字典](acp.md)補充 parallel、cylindrical、spherical、tube 四種 selection rule 的幾何輸入、連結至 `modeling_ply.selection_rules` 的 assignment／append 差異、append 對規則的相交行為，以及 `model.update()` 後檢查 elemental thickness。新增 `PyACP geometric selection rules for ply coverage` 有界主題標 `complete`；範例模型數值與座標不可泛用，完整複材分析未涵蓋。
- ACP 字典限定查詢 `create_parallel_selection_rule LinkedSelectionRule`、`model.update elemental_data thickness` 命中並成功 `get_chunk`；過窄詞組 `append cylindrical_rule intersection` 未命中。原始範例限定查詢 `LinkedSelectionRule cylindrical_rule append`、`model.update elemental_data thickness`、`intersect the two rules` 均成功取片段。README `323 個主題狀態` 查詢成功。
- SQLite transaction 增量更新 ACP 字典與 README，再同步本核對紀錄，未重建全庫；未在 PyACP runtime 執行，REA 萃取內容未修改。

### 2026-10-31 PyGranta RecordLists search criteria

- 核讀官方 RecordLists `version/stable` Searching tutorial 及本機 HTML／Markdown sidecar（source ID `ansys_0f1436c212428dfb860ce644`，SDK metadata 2.1.1、`body_present`、索引正文 6,193 字元）。網址使用 stable，來源 release 欄為 `unknown`，未推定精確發布版。
- [Granta MI 字典](granta_mi.md)擴充 `SearchCriterion` 名稱／狀態／user role 條件、個人清單的 transient internal list 排除、以 `contains_records` 搜尋記錄、`include_items=True` 載入結果項目，以及 `BooleanCriterion` 巢狀 `match_all`／`match_any` 組合。新增 `PyGranta RecordLists search criterion composition` 有界主題標 `complete`；範例資料與搜尋結果不視為實際 server 狀態。
- 字典限定查詢 `name_contains is_internal_use`、`contains_records include_items RecordListItem`、`BooleanCriterion match_all match_any` 均命中並成功 `get_chunk`；原始 tutorial 限定查詢 `BooleanCriterion match_all match_any`、`include_items contains_records` 也成功取片段。README `324 個主題狀態` 查詢成功。
- 官方 notebook 的完整執行前提包括 request publication、publish、revise 權限；未連線 Granta MI server，也未執行範例。SQLite transaction 增量更新 Granta MI 字典與 README，再同步核對紀錄，未重建全庫；REA 萃取內容未修改。

### 2026-10-31 PyCFX logging configuration

- 核對官方 `version/stable` Configure logging 頁及本機 sidecar（source ID `ansys_d64b587bf3782bedf4574901`，SDK metadata 0.3.0、`body_present`、索引正文 577 字元）。來源 release 欄維持 `unknown`；此頁僅說明使用 Python standard logging、有多個 logger，並提供標準格式 `logging_config.yaml`。
- [CFX 字典](cfx.md)將該頁整理為 PyCFX logging 子題，明確記錄來源未列 logger 名稱、預設級別及 YAML 實際搜尋路徑。新增 `PyCFX logging configuration` 有界主題標 `complete`；不由短頁面推測未記載的配置行為。
- 字典 ID 限定查詢 `logging_config.yaml`、`PyCFX logger` 均命中並成功 `get_chunk`；`logging_config.yaml multiple loggers`、`Python standard logging configuration` 未命中。原始 sidecar 查詢 `logging_config.yaml logger`、`Python standard library logging API` 均成功；README `325 個主題狀態` 查詢成功。
- SQLite transaction 增量更新 CFX 字典與 README，再同步本核對紀錄，未重建全庫。未啟動 CFX 或測試 logging 設定；REA 萃取內容未修改。


### 2026-10-31 PyRocky time-series and Grid Function result readback

- 核讀本機 Moving wall interaction tutorial sidecar（source ID `ansys_0708440aef97238120ff1a91`，`body_present`；產品 release 維持 `unknown`，來源 URL 為官方 `version/stable`），直接比對 Postprocess 原始程式碼。該例分別用 `GetNumpyCurve` 讀取進／出質量流率（`t/h`）及回傳時間陣列，用 `GetGridFunction` 的 `GetMax`／`GetMin` 逐 `time_step` 取絕對平移速度極值（`m/s`）；`GetTimeSet()` 作為步階時間軸並以秒標示。
- [Rocky 字典](rocky.md)新增「粒子曲線與 Grid Function 結果讀取」摘要與 `PyRocky time-series and Grid Function result readback` 完整子題。說明保留各自時間軸、明示單位，不把單一範例的輸出形狀或步階規格外推到其他輸出；尚未執行 Rocky 或驗證求解結果。
- Rocky 字典限定查詢 `GetNumpyCurve`、`Particles Mass Flow`、`GetGridFunction`、`Velocity Translational Absolute`、`GetTimeSet`、`time_step` 均命中並成功 `get_chunk`；逐詞組合查詢 `GetNumpyCurve` + `Particles Mass Flow In`、`GetGridFunction` + `Velocity : Translational : Absolute`、`GetTimeSet` + `time_step` 未命中，縮短查詢後可定位。原始 tutorial 文件 ID 限定查詢 `GetGridFunction` 成功命中並取回片段。SQLite transaction 已增量同步 Rocky 字典、README 與本核對紀錄，未重建全庫；REA 萃取內容不在處理範圍。


### 2026-10-31 PyCFX Static Mixer file-based workflow

- 核讀本機 Static Mixer 官方 HTML／Markdown sidecar（source ID `ansys_c1a309e2c8bf661cd1367ed9`，`body_present`、索引正文 9,870 字元、SDK metadata `ansys-cfx-core 0.3.0`）。URL 使用 `version/stable`，產品 release 仍為 `unknown`，未推定精確發布日期或 CFX 相容矩陣。
- [CFX 字典](cfx.md)補入 `PreProcessing` 寫出 `.def`、`Solver` 執行與結果檔、`PostProcessing` 載入結果的檔案交接順序；記錄 `get_physics_messages`、本例 local solver 限制、案例邊界設定、CFD-Post 輸出及 plane 暫停更新和 CEL expression 範例。新增 `PyCFX Static Mixer file-based workflow` 有界主題標為 `complete`；案例的材料、流速、溫度與 timescale 不作通用設計或收斂建議。
- 字典限定查詢 `PreProcessing static_mixer.def Solver PostProcessing`、`get_physics_messages`、`suspend unsuspend CEL expression` 均命中並成功 `get_chunk`。原始 tutorial 限定查詢 `static_mixer.def` 未命中，縮短為 `write_solver_input_file`、`results file` 後命中且成功取片段。此教學原文明確指出 file-based workflow 可分別執行三個元件，且 Static Mixer 範例僅支援 local CFX-Solver。未在本機啟動 session、執行範例或驗證物理解。SQLite transaction 增量同步字典、README 與本核對紀錄，未重建全庫。


### 2026-10-31 PyDPF Field indexing, data shape and time-set IDs

- 核讀本機 `Fields containers and fields` 官方 HTML／Markdown sidecar（source ID `ansys_a651dc9eb40b833a1bff65be`，`body_present`、索引正文 22,302 字元、SDK metadata 0.16.3）。來源網址使用 `version/stable`，頁面未標精確產品 release。
- [DPF 字典](dpf.md)新增 Field data indexing／shape 子題：區分 `get_entity_data(index)` 與 `get_entity_data_by_id(id)`、`field.scoping.ids` 排序與 ID、`len(field)`／`len(field.data)`／`elementary_data_count`，並整理 ElementalNodal shell-layer rows 與 FieldsContainer Python 0-based index 對 time-set 1-based ID 的差異。新增 `PyDPF Field data indexing and shape interpretation` 有界主題標為 `complete`；父級「Fields、FieldsContainer 與 Scoping」仍為 `draft`。
- DPF 字典限定查詢 `get_entity_data_by_id scoping ids`、`len field.data elementary_data_count`、`ElementalNodal shell layers shape` 均命中並可 `get_chunk`；組合查詢 `time set IDs zero-based get_field_by_time_id` 未命中，改用 `get_field_by_time_id`、`time set ID`、`FieldsContainer time` 可命中。原始 sidecar 查詢 `get_entity_data_by_id`、`field.scoping.ids.index`、`get_field_by_time_id`、`elementary_data_count` 均成功取片段；未在 PyDPF runtime 執行運算或模型驗證。SQLite transaction 增量更新 DPF 字典、README 與本核對紀錄，未重建全庫。


### 2026-10-31 PyFluent meshing workflow selection and reuse

- 核讀官方 `Meshing workflows` 本機 HTML／Markdown sidecar（source ID `ansys_50548c9ba3a370611e6a620e`，`body_present`、索引正文 21,387 字元、SDK metadata 0.42.1）；官方 URL 使用 `version/stable`，release 維持 `unknown`。
- [Fluent 字典](fluent.md)擴充 workflow 選擇與範例設定限制，並整理自訂 workflow、task 插入／複製／刪除／重新命名、導航、`mark_as_updated()`、`current_workflow` 初始為 `None` 及 `.wft` 保存／載入。特別標明 2D workflow 不允許切換到 solver mode。`PyFluent meshing workflows` 子題依來源限定範圍標為 `complete`；完整 task 參數和網格品質判定仍不在此主題範圍。
- Fluent 字典查詢 `watertight Fault-tolerant workflow`、`create_workflow current_workflow`、`save_workflow load_workflow`、`mark_as_updated task` 均命中並成功 `get_chunk`；`two_dimensional_meshing solver mode` 未命中，縮短成 `2D workflow`、`solver mode` 或 `switch_to_solver` 可定位。原始 guide 查詢 `Watertight Geometry`、`Fault-tolerant`、`Switching to solver is not allowed`、`save_workflow file_path`、`current_workflow None` 均命中並取回片段。未啟動 Fluent／Meshing、未生成網格或切換 solver。SQLite transaction 增量更新字典、README 與核對紀錄，未重建全庫。


### 2026-10-31 PyGranta RecordLists publication lifecycle

- 核讀本機 `Publishing, revising, and withdrawing record lists` 官方 HTML／Markdown sidecar（source ID `ansys_e514aa6797ca718e7ee30492`，`body_present`、索引正文 4,847 字元、SDK metadata 2.1.1）。頁面使用 `version/stable`，來源 release 維持 `unknown`。
- [Granta MI 字典](granta_mi.md)補上 `awaiting_approval`／`published` 狀態表、新清單發布、revision 修改 parent、發布後 revision 刪除，以及已發布清單的撤回狀態。既有 `RecordLists 發布、修訂與權限` 有界主題更新為 `complete`；同頁保留 tutorial 執行需要 request publication、publish、revise 權限的明確限制。
- 字典限定查詢 `revise_list parent_record_list_identifier`、`unpublish_list published list`、`awaiting_approval` 均命中並成功 `get_chunk`；組合查詢 `awaiting_approval published status` 未命中，拆成 `awaiting_approval` 後可定位。原始 tutorial 查詢 `request_list_approval publish_list`、`revise_list parent_record_list_identifier`、`unpublish_list` 均成功取回片段。未連線 Granta MI server，範例狀態不代表目前 server 資料。SQLite transaction 增量同步字典、README 與核對紀錄，未重建全庫。


### 2026-10-31 PyACP materials hierarchy and material exchange

- 核讀 PyACP 0.4.1 `Materials` 官方 HTML／Markdown sidecar（source ID `ansys_aa79a6097d0fa8bb462bfc43`，`body_present`、索引正文 7,937 字元）。來源 URL 使用 `version/stable`，release 欄維持 `unknown`。
- [ACP 字典](acp.md)新增 Raw Material、Fabric、Stackup、Sublaminate 的職責與組合順序，涵蓋 orthotropic engineering constants／strain／stress property sets、fabric thickness、stackup angle、sublaminate symmetry，以及從 CDB 預設載入材料、用 Engineering Data XML `import_materials`／`export_materials` 的方式。示例常數與幾何只作 API 關係說明，不作工程材料建議。`材料階層` 有界主題標為 `complete`；完整複材分析仍需下游 solver workflow。
- ACP 字典查詢 `Raw Material Fabric Stackup Sublaminate`、`create_material create_fabric create_stackup`、`import_materials export_materials` 均命中並成功 `get_chunk`。原 tutorial 查詢 `create_material ConstantEngineeringConstants` 未命中；拆成 `create_material` 或 `ConstantEngineeringConstants` 後命中，`create_sublaminate SymmetryType`、`import_materials matml_path`、`export_materials path` 亦可取片段。未啟動 ACP、執行 PyACP 腳本或求解。SQLite transaction 增量更新字典、README 與核對紀錄，未重建全庫。


### 2026-10-31 PyOptiSLang Sensitivity settings runner lifecycle

- 核讀 PyOptiSLang `Sensitivity settings` tutorial 的官方 HTML／Markdown sidecar（source ID `ansys_512d9337fc5864cc110d3cb9`，`body_present`、索引正文 2,450 字元、SDK metadata 1.7.0；URL 使用 `version/stable`，release 仍為 `unknown`），並對照本機官方 runner 原始碼。
- [optiSLang 字典](optislang.md)新增 runner 的 `Optislang(ini_timeout=60)`、`examples.get_files("sensitivity_settings")`、`run_python_file(paths[0])`、選擇性 `save_as()` 與 `dispose()` 順序。新增 `PyOptiSLang Sensitivity settings example runner lifecycle` 有界主題標為 `complete`；頁面所執行的 `sensitivity_settings.py` 未隨本機鏡像取得，故設定項、DOE／敏感度結果不在摘要範圍。
- optiSLang 字典查詢 `run_python_file paths`、`sensitivity_settings examples.get_files`、`save_as dispose` 均命中並成功 `get_chunk`；原 tutorial 查詢 `run_python_file`、`sensitivity_settings.py`、`osl.dispose` 亦成功取回片段。未啟動 optiSLang 或執行敏感度計算；包內 `sensitivity_settings.py` 未在本機取得。SQLite transaction 增量同步字典、README 與核對紀錄，未重建全庫。


### 2026-10-31 Mechanical v261 Result.PlotData node export

- 直接檢視本機 Ansys Scripting in Mechanical Guide v261 PDF；physical page 154 說明 PlotData 單位與更新限制，physical page 223（印刷頁碼 215）含 solved result 的 node-value text export 及個別 node 查值範例。來源 PDF 共 422 頁，來源清冊 release 為 v261。
- [Mechanical 字典](mechanical.md)補入 `PlotData["Values"]`、`Dependents`／`Independents`、`Values.Unit`、0 起始列索引、Node ID 對應及文字匯出步驟；並標明結果不轉為使用者指定單位、改動 Details 後要重新 evaluate，以及此範例只展示 `Node` 欄。新增 `v261 Result.PlotData node-value access and text export` 有界主題標 `complete`；整體「結果與後處理」仍為 `draft`。
- Mechanical 字典限定查詢 `PlotData Values Unit`、`Independents Dependents`、`Details evaluate snapshot`、`PlotData Node` 均命中並成功 `get_chunk`；組合查詢 `PlotData Node text file` 未命中。原始 Scripting Guide 查詢 `PlotData Values Unit`、`PlotData Node text file` 與 `not converted user-specified unit system` 均命中並成功取片段。本機未啟動 Mechanical 或重新求解模型。SQLite transaction 增量更新字典、README 與核對紀錄，未重建全庫。


### 2026-10-31 LS-PrePost CFile replay and headless execution

- 直接核對 v261 LS-PrePost User’s Guide PDF physical pages 1061–1063（印刷頁碼 1033–1035）；原 PDF 共 1,070 頁，來源清冊 release 為 v261。頁面說明 GUI 命令記錄到 `lspost.cfile`、兩種命令列模式、GUI 開啟 CFile，以及 CFile 控制命令。
- [LS-DYNA 字典](lsdyna.md)新增 CFile replay 與 headless 範圍子題，明確區分 `c=commandfile -nographics`（隱藏 GUI 但仍需 graphics support）和 `runc=commandfile`（真正 headless、僅支援非圖形命令），並記錄互動／resume／skip 控制及 `Record_orient`。新增 `v261 LS-PrePost CFile replay and headless limits` 有界主題標為 `complete`；未整理完整 command index。
- LS-DYNA 字典查詢 `lspost.cfile runc nographics`、`-nographics graphics support`、`interactive resume skip endskip`、`Record_orient` 均命中並可 `get_chunk`；PDF sidecar 查詢 `lspost.cfile`、`runc=commandfile`、`graphics support not true headless`、`Record_orient` 均成功取回來源片段。未啟動 LS-PrePost、未執行 command file。SQLite transaction 增量同步字典、README 與核對紀錄，未重建全庫。


### 2026-10-31 PyMotorCAD Adaptive Templates version and script lifecycle

- 核讀本機官方 `Motor-CAD adaptive templates scripting` HTML／Markdown sidecar（source ID `ansys_c1f8ccd899a4f1a1a4a0ac59`，`body_present`、索引正文 30,037 字元、SDK metadata 0.8.8）。頁面使用 `version/stable`；Motor-CAD 產品 release 欄維持 `unknown`。指南明列 feature 最低需求 Motor-CAD v2024.1.2（2024 R1 Update）及 PyMotorCAD v0.4.1。
- [Motor-CAD 字典](motorcad.md)補上 UI 啟用路徑、幾何建立時重跑 script、外部執行但未載入 tab 時 geometry 僅暫存、以及 `get_region()`／`set_region()` 與幾何 library 的用途界線。`Adaptive Templates 版本需求` 主題改名為 `PyMotorCAD Adaptive Templates 版本需求與 script lifecycle` 並標為 `complete`；這些最低需求不視為完整版本相容矩陣。
- Motor-CAD 字典查詢 `Motor-CAD 2024.1.2 PyMotorCAD v0.4.1`、`Geometry Templates Type Standard Adaptive`、`get_region set_region geometry` 均命中並成功 `get_chunk`；合併查詢 `external script geometry temporarily` 未命中，拆為 `external script` 或 `Adaptive Templates` 後可定位。原始 guide 查詢 `v2024.1.2 PyMotorCAD v0.4.1`、`geometry is only defined temporarily`、`run every time the Motor-CAD geometry is created`、`get_region set_region` 均命中並成功取回片段。未啟動 Motor-CAD 或執行 Adaptive Templates script。SQLite transaction 增量同步字典、README 與核對紀錄，未重建全庫。


### 2026-10-31 PyAEDT Desktop session ownership and selection precedence

- 核讀 PyAEDT Desktop sessions 官方 HTML／Markdown sidecar（source ID `ansys_8418f1dee07e7c32701b3e5c`，`body_present`、索引正文 4,978 字元、SDK metadata 1.9.0），並對照 `Desktop` API 參考（source ID `ansys_dc58a4be8ae15239b6c36817`，17,903 字元）。網址使用 `version/stable`，AEDT 產品 release 仍為 `unknown`。
- [AEDT 字典](aedt.md)補上 `close_on_exit` 的 context／direct use 條件及 `port=0`、`new_desktop`、remote RPyC、相同／不同 version、display mode 等 session 選擇優先順序，並補 `release_desktop(close_projects=False, close_desktop=False)` 範例。`Desktop session 生命週期` 有界主題更新為 `complete`；PyAEDT 其餘四個主題仍為 `draft`。
- AEDT 字典查詢 `close_on_exit context manager new desktop`、`remote RPyC session port`、`AEDT version port`、`release_desktop close_projects close_desktop` 均命中並成功 `get_chunk`；兩組過長查詢 `same AEDT version same port reuse`、`different AEDT version port conflict` 未命中。Desktop sessions 原文查詢 `close_on_exit`、`new_desktop remote RPyC`、`same version`、`different version` 均命中，Desktop API 查詢 `close_on_exit`、`release_desktop` 亦成功取回片段。未啟動 AEDT 或連線至既有 Desktop。SQLite transaction 增量同步字典、README 與核對紀錄，未重建全庫。


### 2026-10-31 PySimAI 0.4.8 model build readiness and configuration

- 核讀 PySimAI 官方 `Building a model`、`Projects` 與 `Model configuration` HTML 原件及逐頁 Markdown sidecar（source IDs `ansys_6995c508569ff337c2b1d9dd`、`ansys_06a77f8e31736fe81fb67e50`、`ansys_c146393d86eea0e92de9c9ef`）；三頁來源清冊均註明 `ansys-simai-core 0.4.8`。HTML 原件保留，正文 sidecar 已索引。`stable` URL 不作為服務端 release 證據。
- [SimAI 字典](simai.md)補上 `TrainingData`→`Project` 關聯、`project.is_trainable()` 檢查、build preset 文件時限與 `simai.models.build(...)` 流程；區分 API 文件示例的「至少 3 個 data points」不可訓練原因、各 preset 時長說明、`build_on_top` deprecated，以及 guide 明示模型建置仍為 experimental。新增有界主題 `PySimAI 0.4.8 模型建置前置條件與設定` 標為 `complete`；不將 preset 時限當成服務完成保證，也未驗證雲端狀態。
- SimAI 字典限定查詢 `is_trainable`、`build_preset`、`build_on_top`、`experimental` 均命中並成功 `get_chunk`。最初較長組合 `is_trainable at least 3 data points`、`build_preset 2_days default` 未命中；拆短後可定位。原始 guide `experimental`、Projects API `is_trainable`、Model configuration API `build_on_top` 均命中並成功取回片段。
- SQLite 以單一 transaction 增量同步 SimAI 字典、README 與本核對紀錄；三筆正文 hash、chunk 數與字元數一致，`PRAGMA quick_check` 回報 `ok`，`_needs_rebuild()` 為 `False`。本次未觀察到 SQLite 鎖定錯誤，未執行全庫重建；未連線 SimAI 服務或執行模型建置。


### 2026-10-31 PySherlock launch_and_connect lifecycle and release boundary

- 核讀本機 PySherlock 2.1.4 Getting Started、Launcher API 與 `launch_and_connect` sidecar，並對照 2.1.5 同名 API 頁（source IDs `ansys_03a01675e3ec0448a4609447`、`ansys_8fe2c6d2e3a266ee8921dd62`、`ansys_dd9d04316ba5a87573d77458`、`ansys_48a487536247777ce3260d58`）。兩版 method page 的 Markdown 正文逐行相同；Getting Started 指出需授權 Sherlock 2022 R2+，而方法自身的 `Available Since` 為 2025 R2，分開記錄產品最低條件與此方法的可用版。
- [Sherlock 字典](sherlock.md)補充 `launch_and_connect()` 啟動本機 Sherlock／gRPC、host／port／timeout／mTLS 預設、`year`／`release_number`、single-project 參數、傳輸模式、tuple 回傳值，以及 `launch()` 與 `connect()` 的用途差別。新增 `PySherlock launch_and_connect 啟動與版本界線` 有界主題為 `complete`；SDK 2.1.4／2.1.5 單頁內容相同不代表整個 SDK 相同，未測本機安裝或連線。
- Sherlock 字典限定查詢 `launch_and_connect`、`127.0.0.1`、`2025 R2` 均命中並成功 `get_chunk`；無空格查詢 `2025R2` 未命中。2.1.4 API `Available Since` 與 2.1.5 API `timeout` 查詢均命中並成功取片段。兩份 method sidecar SHA-256 相同。SQLite transaction 增量更新 Sherlock 字典、README 與本紀錄；`PRAGMA quick_check` 為 `ok`，`_needs_rebuild()` 為 `False`。


### 2026-10-31 ModelCenter v261 custom optimization algorithm lifecycle

- 核讀 ModelCenter Developer Portal v261 原始 Markdown 頁 `Create an algorithm index`（source ID `ansys_dff7d7c47aad0995f319ebb8`；URL 與本機正文相同，頁面標示 2026-06-19 更新）。來源直接列出 `IAlgorithmHost`、options/objectives/constraints/design variables、可選 checkpoint、`Run`、兩種 report 與 `Dispose` 的生命週期順序。
- [ModelCenter 字典](modelcenter.md)補充 option 改動通知、執行中讀取 report 的 thread-safety 要求，以及 `DetailsReport` 預期持續更新、`ResultsReport` 則可更新但非必要的差異。既有 `Custom Optimization Algorithm 生命週期` 主題升為 `complete`，範圍限 v261 lifecycle 頁明示內容；未推定 thread-safety 實作方式、報告欄位、更新頻率、演算法效能或物理有效性。
- ModelCenter 字典限定查詢 `RestoreCheckPoint`、`DetailsReport`、`thread-safe` 均命中並成功 `get_chunk`；原始頁查詢 `DetailsReport expected update`、`thread safe during the run` 亦命中並成功取片段。SQLite transaction 增量更新字典、README 與本紀錄，未遇 `database is locked`；`timeout=0` 的 `BEGIN IMMEDIATE` 零等待探測成功取得並 rollback，psutil 未找到其他程序開啟此 DB 的 handle（僅代表探測時點）。`PRAGMA quick_check` 為 `ok`，`_needs_rebuild()` 為 `False`。未編譯 SDK 或執行 ModelCenter 演算法。


### 2026-10-31 Motion v261 Python Result File Reader

- 核讀 Ansys Developer Portal v261 `Result File Reader using the Python language` 正文（source ID `ansys_fbcb7460c476256171f6e2cf`，頁面更新日期 2026-03-09）；此來源是官方 Markdown，已直接索引，無需從 PDF／HTML 重轉。
- [Motion 字典](motion.md)補上 CPython／Python.NET 版本要求、IronPython／Workbench Scripting 的例外、安裝包 ZIP 與 `Modules` 匯入方式、`OutputReader` 開啟及 `Close()`，並界定操作參數需參考 Operation API。`Python Result File Reader` 子題按此 v261 頁面範圍標為 `complete`；未將 3.7–3.11 延伸為較新 Python 的支援聲明，也未推定 `get_result_file_path()` 的搜尋邏輯。
- Motion 字典限定查詢 `Python.NET`、`ResultFileReaderAPI`、`OutputReader Close` 均命中並成功 `get_chunk`；來源正文查詢 `3.7 3.11`、`OutputReader Close` 亦命中並成功取片段。SQLite transaction 增量同步 Motion 字典、README 與本紀錄，未重建全庫；未執行 Python.NET、Motion 或結果檔讀取。


### 2026-10-31 PyAnsys Geometry 0.18.2 Sketch shapes

- 核讀本機 PyAnsys Geometry `Sketch` 官方 HTML 轉換 Markdown sidecar（source ID `ansys_2cbec50f69fa10dc6b4878ae`；來源頁屬 SDK 0.18.2 文件，產品 release unknown）。既有 sidecar 已保留原始官方 URL 並納入索引，無須重複轉換。
- [Geometry 字典](geometry.md)補上 `Edge`／`Face` 定義、functional-style 的連續起點與標籤取回、direct API 獨立建立 triangle，以及 `plot()` 顯示。既有 `Sketch、Edge 與 Face` 主題標為 `complete`，限 SDK 0.18.2 guide 明載的基本概念與示例；完整 Sketch API methods、service runtime 和幾何精度未驗證。
- Geometry 字典限定查詢 `Edge Face`、`segment_to_point`、`sketch.get Segment2` 均命中並成功 `get_chunk`；原始頁查詢 `triangle tag triangle2`、`Face edges closed surface` 亦成功。初次加上 `product=geometry` 篩選時未命中，查明字典 alias 的舊 metadata 分類為 `general`；已確認來源路徑後將該 alias 增量改標 `geometry`，重試後上述字典與原始頁查詢均命中。SQLite transaction 增量同步本紀錄，`PRAGMA quick_check` 為 `ok`，`_needs_rebuild()` 為 `False`；未連線 Geometry service 或測試 CAD 結果。


### 2026-10-31 OpenTD 2026 R1 WorkingUnits and expression units

- 核讀 OpenTD 2026 R1 官方 `Work with units, symbols, and expressions` 原文（source ID `ansys_a009f17f90528343bbdcbd9c`；頁面更新日期 2026-03-09，Markdown 正文已索引）。
- [Thermal Desktop 字典](thermal_desktop.md)補上 thread-static `Units.WorkingUnits` 與 drawing units 分離、`SetDwgUnits`／`SetUnits`、單位轉換示例、expression 獨立單位、property 名稱固定單位提示，以及 `CreateSymbol`／`GetSymbolValue` 對 Case Sets 的範圍。既有 `WorkingUnits、drawing units 與 expressions` 主題標為 `complete`，範圍限 OpenTD 2026 R1 此頁所述行為；範例數值非通用工程建議。
- Thermal Desktop 字典查詢 `WorkingUnits thread-static`、`SetUnits Units.SI`、`GetSymbolValue Case Sets`、`ValueExp` 均命中並成功 `get_chunk`；原始頁 `thread static WorkingUnits`、`GetSymbolValue basic symbol values` 亦成功取片段。帶標點的 `ValueExp units.energy` 組合未命中，改用 `ValueExp` 或 `units BTU HR` 可定位。SQLite transaction 增量更新字典、README 與本紀錄，未重建全庫；未執行 C# 範例或連接 Thermal Desktop。


### 2026-10-31 Zemax v261 ZOS-API Example 01 Python／C# 頁

- 核讀官方 [Python 範例頁](https://developer.synopsys.com/docs/zemax-opticstudio-zos-api-2026-r1/apiexamples/example_01_py.md) 與 [C# 範例頁](https://developer.synopsys.com/docs/zemax-opticstudio-zos-api-2026-r1/apiexamples/example_01_cs.md)（兩頁標示更新 2026-03-09）；本機只快取 Example 01 導覽頁，語言程式碼頁未快取。
- [Zemax 字典](zemax.md)補上 Python／C# 的 standalone 初始化與授權檢查、建立 lens file、欄位與波長設定、LDE／F-number solve、Quick Focus、儲存及關閉流程。清冊將此主題標為 `complete`，僅限上述頁面的文件摘要；沒有執行 ZOS-API、驗證產生的 lens file 或光學結果。
- `sources.csv` 與 `markdown_links.csv` 新增兩個官方來源追蹤列，狀態明示「已核讀摘要、未鏡像完整程式碼」；未新增依賴或改動原 PDF／HTML 轉換產物。


### 2026-10-31 Mechanical v261 contact／target 指派與 workflow

- 直接核讀官方 [Designate Contact and Target Sides](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_sim/ds_Contact_Scope.html) 與 [Contact Workflow](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_sim/ch09s06s02.html) 兩頁正文。
- [Mechanical 字典](mechanical.md)新增有界子題，整理網格密度、幾何凹凸／edge、表面大小及材料剛柔的 contact／target 指引、scoping 幾何型別限制、shell target face、rigid body 注意事項及建立／檢查流程。主題清冊新增一列並標為 `complete`，只表示兩頁內容已整理。
- 兩頁原始 HTML 未下載或鏡像；完整其他接觸 formulation、元素與 solver 限制未在此子題涵蓋，亦未執行求解。來源清冊既有兩筆官方 URL 狀態維持 `browser_summary_only`。
- Mechanical `Top and Bottom` 查詢命中字典且 `get_chunk` 片段含原始來源網址；`Augmented Lagrange` 與 `Named Selections Contact` 亦命中。組合查詢 `contact target finer mesh` 及 `Contact Tool initial status` 未命中，改以 `Top and Bottom` 或 `Named Selections Contact` 可定位；目前索引只含繁中摘要，尚無 HTML 原文可做全文查詢。


### 2026-10-31 LS-DYNA v261 LS-PrePost File Open

- 依本機已轉換並索引的 Ansys LS-PrePost User’s Guide v261 PDF／逐頁 Markdown physical page 43，整理 binary plot（`d3plot`、`d3eigv`）、keyword（`*.k`／`*.key`／`*.dyn`）、keyword+d3plot 多選、`d3thdt`、command（`*.cfile`／`*.ses`／`*.cmd`）、`*.db`、project、interface force 與 IGES 的入口用途。
- [LS-DYNA 字典](lsdyna.md)新增 v261 File Open 子題，並在 [topics.csv](topics.csv) 登記一項有界 complete；來源定位至 PDF physical page 43，未推廣為所有版本的相容性判定。
- 來源 PDF／Markdown 原有轉換產物未重做；未在 LS-PrePost 實際開啟各種檔案。


### 2026-10-31 optiSLang v261 PyOSDesign 與 OMDB

- 核讀本機 v261 SP03 官方 API Markdown sidecars：`py_os_design`、`py_os_parameter`、`py_omdb`。整理手動建立 `PyOSDesign`／`PyOSDesignPoint`／`PyOSDesignContainer`、run status、`PyParameterManager` 參數定義，以及 `PyOMDB.check_consistency()` 與 `save_to_file()`。
- [optiSLang 字典](optislang.md)與清冊新增有界 complete 子題，範圍是 design data representation／儲存 API；不代表 DOE 方法已完成，也未在產品環境執行。
- 原 `py_os_design` 範例行有可見不一致：`startdesign` 未定義（前文為 `start_design`）、參數建立呼叫有 5 個 arguments 而同版 `py_os_parameter` 簽章列 4 個，以及 `save_to_file(...)` 缺右括號；字典已明確標為不可直接照抄，來源檔未修改。
- optiSLang 字典查詢 `PyOSDesignContainer OMDB` 命中並成功 `get_chunk`；原始 `py_os_design`／`py_os_parameter`／`py_omdb` alias 上的 `RunInfoMeta`、`add_deterministic_continuous_parameter`、`check_consistency` 單詞查詢均命中並成功取片段。較長組合查詢 `PyOSDesignContainer RunInfoMeta`、`check_consistency save_to_file` 未命中；改用單一 API 名稱可定位。索引未提供同義詞或語意檢索。


### 2026-10-31 Mechanical v261 MeshSizingType 與 advanced defaults

- 以本機已轉換／索引的 v261 `Mesh` API 與 `MeshSizingType` enum Markdown sidecars 核對 sizing type 清單、`SetMeshSizing` 的 Medium 預設及預定義基本設定行為，以及 `SetAdvancedMeshSizingDefaults` 的 Advanced 前置條件與例外。
- [Mechanical 字典](mechanical.md)補上有界呼叫順序子題並登記於 [topics.csv](topics.csv)；preset 的實際數值與網格物理適用性仍未涵蓋。
- 來源正文已在原索引；本輪不重做 HTML/PDF 轉換，亦未執行 Mechanical mesh generation。


### 2026-10-31 Mechanical v261 Named Selection body sizing 範例

- 對照 v261 *Scripting in Mechanical Guide* 印刷頁 396（PDF physical page 404）及其已轉換 Markdown sidecar；確認 `NS_Volume` 的名稱查找、`MESH.AddSizing()`、`Location`、`ElementSize = Quantity('0.5 [m]')` 與 `MESH.GenerateMesh()` 同屬 Magnetostatic_001 教學範例。
- [Mechanical 字典](mechanical.md)新增有界 complete 子題並登記於 [topics.csv](topics.csv)。0.5 m 僅為範例值；頁面未給出網格品質或敏感度驗證，整體網格主題維持 draft。
- 對照 PDF physical page 404 的渲染影像確認頁尾印刷頁碼 396；原始 PDF 與 sidecar 未修改。未在 Mechanical 執行範例或產生網格。


### 2026-10-31 SpaceClaim v261 ACT Extension 與 Wizard 範例

- 核讀已轉換並已索引的 v261 *ACT Customization Guide for SpaceClaim*：印刷頁 1 說明 standalone extension 目錄、Extension Manager／Wizard launcher，以及 Workbench 開啟時需從 Workbench 的 ACT Start Page 管理 extension；印刷頁 3–5 說明 `WizardDemos` 的 SpaceClaim `CreateBridge` 兩個 step 與 `onupdate` callback。
- 渲染 PDF physical pages 5、7–9，逐頁核對印刷頁碼、standalone 路徑及 wizard XML／callback 說明；沒有重做既有 PDF→Markdown 轉換，來源 PDF 與 sidecar 未修改。
- [SpaceClaim 字典](spaceclaim.md)新增有界 complete 子題並登記於 [topics.csv](topics.csv)。只涵蓋此指南的 extension 載入入口及示例 callback；未執行 SpaceClaim／ACT，未推定 v251 行為或完整 ACT API。
- 以來源 PDF alias 查詢 `Extension Manager ANSYSversion_DIR`、Markdown sidecar alias 查詢 `CreateBridge UpdateDeckSC SupportsSC` 均命中，`get_chunk` 均成功；來源索引 `_needs_rebuild=False`。搜尋僅為詞彙檢索，其他 ACT API 問題仍須查對應 Developer’s Guide。


### 2026-10-31 optiSLang v261 SP03 ReliabilityMonteCarlo

- 核讀已轉換／索引的 `py_reliability_montecarlo` 與 `py_random_variables` 官方 API Markdown sidecars。整理預定樣本數或 c.o.v. 準確度停止方式、`Pf > 0.5` 時使用 `1-Pf`、每批平行 designs 後檢查收斂、未達目標而用盡最大樣本時失敗終止，以及 solver request 失敗設計可被忽略或視為 failure event。
- 官方頁只列出 `SettingsMonteCarlo` 的欄位名稱與建構簽章，沒有說明 solver 失敗處理的選項名稱／預設值，也未定義 reliability failure event；[optiSLang 字典](optislang.md)保留此缺口，未推測預設。
- 原始 API source alias 以 `ReliabilityMonteCarlo`、`maximum allowed samples` 查詢可命中且 `get_chunk` 成功；組合查詢 `ReliabilityMonteCarlo success_info false` 未命中，因 sidecar 將底線跳脫為 `success\_info`，改用 API 類名定位。未執行 Python API、optiSLang 或可靠度分析。


### 2026-10-31 Motion v261 Python Operation API 曲線匯入／匯出

- 整理已轉換並索引的 Operation API Python getting-started、Numeric Import、Export All Curves 範例及 `ApplicationHandler` API Markdown sidecars；來源均為 Ansys Developer Portal v261 頁面，補入 [sources.csv](sources.csv) 追蹤 URL、版本、路徑及索引狀態。
- 摘要 `ApplicationHandler` 開啟結果／頁面生命週期、`PlotParameters` 的 target／path、`AddCurves`、`ExportAllCurves` 與 `NumericParameter`／`ImportNumeric` 欄位映射；另記錄 Numeric Import 範例變數不一致：定義 `file_path` 卻呼叫未定義的 `export_filepath`。未改寫來源範例。
- [Motion 字典](motion.md)與[主題清冊](topics.csv)新增有界子題；原先完整的 Python Result File Reader 與此 Operation API 分別記錄，未混為同一 API。
- 來源 API alias 查詢 `ImportNumeric NumericParameter TargetX TargetY` 命中並可 `get_chunk`；Operation API 指南查詢 `IronPython 2.7.12` 命中，曲線範例查詢 `ExportAllCurves` 可回到對應 source chunk。未執行 Motion Postprocessor、IronPython 或腳本。


### 2026-10-31 PyDYNA deck_loader 與 keyword parse fallback

- 核讀本機已索引的官方 [`deck_loader` source-code sidecar](../ANSYS_Document/LS-DYNA/sdk/ansys-dyna-core/unknown/api_reference/f4bfd65ef2fe-deck_loader.md)：`load_deck`／`load_deck_from_buffer`、override／TypeMapping class lookup、unknown keyword raw-string fallback、mapped keyword parse failure 的 strict／non-strict 分支，以及 `DeckLoaderResult` summary／warnings。來源路徑及清冊 release 均為 `unknown`，不套用 0.12.1 標籤。
- [LS-DYNA 字典](lsdyna.md)補上有界解析行為子題，明確指出 loader 保留原文不等同卡片已成功解析或 solver 相容；來源檔未修改。
- 原始來源 alias 查詢 `load_deck_from_buffer` 與 `get_summary` 均命中，`get_chunk` 成功取回相關片段；字典查詢 `DeckLoaderResult` 命中並回傳解析邊界摘要。組合查詢 `unprocessed keyword raw string` 未命中；此處改用 API 名稱查詢定位，索引是關鍵字檢索，沒有語意擴展。未執行解析器或 LS-DYNA solver。


### 2026-10-31 Mechanical Results v261／v252 User’s Guide

- 核讀官方 [Introduction to the Use of Results v261](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_sim/ds_results_intro.html) 與 [Review Results v252](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/wb_sim/ds_Review_Results_step.html) 正文。
- [Mechanical 字典](mechanical.md)新增結果插入與 scope、contour／probe／chart／interpolation、text／STL export、report 等功能摘要，分開記錄 v252 的剛體圖形、缺少 result files 及 harmonic contour 限制；同時保留 v261 APDL single-precision／mesh-data 限制的版本界線。
- 新增有界主題列；兩頁原始 HTML 未下載或鏡像、只索引本地字典摘要。未驗證 Mechanical 生成結果、未執行求解；其他 result types 與分析理論仍未覆蓋。
- 字典內 `STL`、`Interpolation`、`single precision NORSTGM` 查詢均命中 Mechanical 摘要，`get_chunk` 可取回相應限制並在 STL／Interpolation 片段中回到兩個來源 URL。兩頁原始 HTML 沒有本機正文 alias，因此目前 RAG 可檢索的是繁中摘要，不能直接檢索線上頁全文。Sources inventory 狀態維持 browser summary only。


### 2026-10-31 Icepak v261 Transient Simulation Heat Pipe tutorial

- 核對本機已抽取並索引的 `Getting Started with Icepak - Transient Simulation` PDF 與頁碼 Markdown sidecar（Release 2026 R1，PDF Pages 13–29）。
- [Icepak 字典](icepak.md)新增案例流程：`Transient`／`Temperature and Flow`、piecewise-linear `ds_pwr` 乘數、`block_1` 的 25 W 基值、fan `Transient Strength` 僅檢視未啟用、30 s duration／2 s timestep／150 iterations per step、每步儲存 fields、thermal／flow monitors，以及 All-times temperature summary、24 s plot 與動畫。曲線點值未見於文字抽取，未推定。
- 新增有界 complete 子題；所有數值及情境均限該 Heat Pipe tutorial。沒有重做 PDF 轉換，沒有啟動 AEDT 或求解。
- 字典 alias 查詢 `ds_pwr Transient Temperature` 命中，`get_chunk` 回傳範例設定摘要；原始 PDF alias 查詢 `Thermal Monitor` 亦命中，取回片段含 PDF page marker。索引涵蓋已轉換的文字層，未檢查圖表曲線點值。


### 2026-10-31 PyCFX PreProcessing state dictionary 與 physics updates

- 核讀本機已索引的官方 PyCFX `Use PyCFX sessions` Markdown sidecar。整理逐項 setter 觸發的相依 physics updates、更新範圍及 dictionary `set_state()` 對 CFX versions up to and including 2026 R1 不執行 physics updates 的明文限制；並整理 optional parameter／object／named-object 的明確移除方式。
- [CFX 字典](cfx.md)與 [topics.csv](topics.csv)新增有界子題；來源路徑有 SDK 0.3.0 metadata，但 URL 為 `version/stable`，release 欄仍 unknown，未推定後續 CFX 行為。
- 未開啟 PyCFX、未執行 CFX session 或求解。索引回查：字典 alias 以 `physics updates dictionary` 命中 chunk 1，`get_chunk` 含 `2026 R1`、`physics updates`、`physics warnings` 與 optional 清理；官方原文 alias 以 `dictionary physics updates` 命中 chunks 12–13，片段含 `2026 R1` 與 `set_state()` 限制。補充查詢 `set_state` 命中原文 chunks 1、2、4，但前 3 筆未涵蓋版本限制；因此採精確主題詞回查 chunks 12–13 作為證據。README 的多詞查詢 `PreProcessing state physics updates` 未命中，簡化為 `PreProcessing` 後命中 chunk 6，`get_chunk` 可回查至 9 主題進度敘述；單詞組合 `CFX 字典 9 個主題` 有命中但前兩筆片段未含進度句，故以 `PreProcessing` 片段作進度回查。


### 2026-10-31 CFF v252 Project::Metadata 型別與儲存時點

- 核讀已轉換並索引的官方 `ansys::Project::Metadata Class Reference` Markdown sidecar；來源 catalog 為 v252，官方頁更新日期 2025-07-16。整理 metadata 型別查詢、typed getter/setter、vector/link、複製與移除操作，以及修改在下一次 `Project::saveProject()` 寫入 index 的時點。
- [CFF 字典](cff.md)與 [topics.csv](topics.csv)新增有界 complete 子題。保留原文 integer overload 範例將 `isDouble()`、`isInt()` 都寫為 false 的不一致，不代替官方修正；其他未說明的回傳值與錯誤行為不推定。
- 未執行 CFF SDK。索引回查：字典 alias 查詢 `Metadata setValue saveProject` 命中 chunk 1，`get_chunk` 含 metadata、setter、`saveProject()` 與 `isInt` 範例；原始 v252 class reference alias 同一查詢命中 chunk 5，含原文範例及儲存時點；README alias 查詢 `CFF Project Metadata` 命中 chunk 6，可回查 CFF 主題進度。三處皆由既有全文搜尋及片段擷取取得，未測實際 SDK 執行結果。


### 2026-10-31 PySherlock ODB++ archive 匯入參數與狀態碼

- 核讀 `Project.import_odb_archive` 官方 API Markdown sidecar 及 User guide 匯入步驟；API 頁標示 `Available Since: 2021R1`，方法回傳 status code 且明載 0 為成功。整理四個必填布林參數、IMS/project/CCA 預設值、polyline 簡化選項及範例中的後續 parts-list 步驟。
- [Sherlock 字典](sherlock.md)與 [topics.csv](topics.csv)更新 ODB++ 匯入主題為 complete。資料來自 SDK 2.1.4 文件集合，但 URL 使用 `version/stable` 且產品 release unknown；SDK package 版本與產品版本分開記錄。範例 tolerance 不作通用建議，未記載的狀態碼及猜測準確度不推定。
- 未啟動 Sherlock、未匯入 archive 或更新 parts list。索引回查：字典 alias 查詢 `ODB archive process_layer_thickness polyline_tolerance` 命中 chunk 1，`get_chunk` 含 archive、層處理、2021 R1 邊界；API 原文 alias 查詢 `archive_file IMS stackup success` 命中 chunk 2，片段含 `0 for success`；User guide alias 查詢 `import_odb_archive CCA parts list` 命中 chunk 1，含後續 parts-list 步驟。README 的多詞查詢 `Sherlock ODB project import` 未命中，簡化成 `Sherlock` 後命中 chunks 1、5、6、8，`get_chunk` chunks 5–6 可回查 7 個主題／2 個 complete 的進度。


### 2026-10-31 Discovery v261 Document containers 與 Window 載入規則

- 核讀官方 v261 `geo_doc_structure.md` 正文，整理 main part/internal components、drawing sheets、document materials、default 與 active layer 的差異，以及 explicit open／implicit load 時 windows 的載入行為和 window scene/context。
- [Discovery 字典](discovery.md)與 [topics.csv](topics.csv)新增有界 complete 子題。該頁引用 part 結構圖，但 `geo_doc_structure.jpg` 未在本機 Discovery v261 來源目錄找到；圖中未抽取的 part 階層保持為待補，不擴大推論。
- 未執行 Discovery API。索引回查：字典 alias 查詢 `default layer active layer implicit load` 命中 chunk 1，`get_chunk` 含 main part、default／active layer、windows 與 interaction context；官方 v261 source alias 查詢 `default layer active layer windows` 命中 chunk 1。README 的多詞查詢 `Discovery v261 Document containers` 未命中，簡化為 `Discovery` 後命中 chunks 2、6，`get_chunk` chunk 6 可回查 v261、6 個主題及 1 個 complete 的進度。


### 2026-10-31 PyTwin HTML sidecar：TwinRuntime 載入與關閉生命週期

- 從原始 HTML 對應的 Markdown sidecar 核讀 `twin_load`、`twin_instantiate`、`twin_initialize`、`twin_close` 四個 PyTwin 0.13.0 API 頁。整理 log_level/FMI 類型選項、不支援指定 FMI 類型會報錯、initialize 必須接在 instantiate 後，以及 close 後原 TwinRuntime 不再有效。
- [PyTwin 字典](twinai.md)與 [topics.csv](topics.csv)更新為一項有界 complete 主題。API 原始檔是 HTML、catalog text_path 指向同目錄 Markdown sidecar，兩者均保留；來源 URL 為 `version/stable`，產品 release 仍 unknown。
- 未執行 PyTwin runtime 或模擬。索引回查：字典 alias 查詢 `twin_load fmi_type twin_instantiate twin_close` 命中 chunk 0，含四階段內容；instantiate、initialize 原文 alias 查詢各自命中 chunk 0。`twin_load` 原文 alias 的多詞查詢 `log_level FmiType unsupported error` 未命中，簡化為 `FmiType` 後命中，`get_chunk` 含不支援 FMI type 會引發錯誤；`twin_close` 原文 alias 的 `twin_close Runtime instance invalid` 未命中，簡化為 `no longer valid` 後命中，片段含失效及重新建立 instance 說明。README alias 查詢 `PyTwin Runtime lifecycle` 命中 chunk 6，回查可確認主題數與 complete 狀態。


### 2026-10-31 PyAnsys Sound HTML sidecar：WAV 訊號處理流程

- 核讀官方 `002_load_resample_amplify_write_wav_files.html` 對應的 Markdown sidecar；整理 DPF Server／教學音檔取得、`LoadWav`、`Resample`、`ApplyGain`、NumPy 繪圖與 `WriteWav` 的資料流。範例原始取樣率 44100 Hz、重取樣 20000 Hz、增益 10 dB、輸出 bit depth `int16`，均標記為教學設定。
- [Sound 字典](sound.md)與 [topics.csv](topics.csv)更新 WAV 處理主題為 complete。原文未說明 clipping、峰值驗證或位深選擇準則，因此未推定輸出品質；SDK package 路徑為 0.4.0，產品 release unknown，URL 使用 stable。
- 未執行音訊處理。索引回查：字典 alias 查詢 `LoadWav Resample ApplyGain WriteWav` 命中 chunk 0，`get_chunk` 包含完整流程與 `int16` 輸出；原始教學 alias 多詞查詢 `Resample gain_in_db bit_depth int16` 未命中，簡化查詢 `WriteWav` 命中 chunks 0、7（chunk 0 含四階段流程，chunk 7 含 `int16`），`gain_in_db` 命中 chunks 3、4。README alias 多詞查詢 `Sound WAV resample gain` 未命中，`Sound`／`WAV` 簡化查詢命中 chunks 1、6；`get_chunk` chunk 6 可回查 5 個主題及 1 個 complete。


### 2026-10-31 HFSS v261 PDF：IronPython 與 CPython/gRPC 執行方式

- 核讀 HFSS Scripting Guide v261 PDF 逐頁 Markdown sidecar，涵蓋 Desktop IronPython／standalone IronPython（PDF Pages 62–68）與 CPython/gRPC（PDF Pages 104–107）。整理 IronPython 2.7/.NET 4.0、C-extension 限制、Desktop/COM 啟動邊界、ScriptEnv 初始化／關閉、gRPC port 與 Connect／Initialize 連線選擇、遠端 project path 要求及 beta 無圖形執行限制。
- [HFSS 字典](hfss.md)與 [topics.csv](topics.csv)更新 scripting environments 為 complete。保留 PDF 原檔與既有逐頁 Markdown；未重做轉換，表格／圖未逐頁視覺校對，未啟動 AEDT。
- 索引回查：字典 alias 查詢 `CPython gRPC IronPython ScriptEnv.Connect` 命中 chunks 0–1，`get_chunk` 含環境比較、連線與 beta 限制；PDF sidecar alias 查詢 `CPython ansysedt gRPC InitializeNew` 命中 chunk 109，補查 `-grpcsrv` 命中 chunks 109–110，片段含 PDF Page 106／50051／port-range，`ScriptEnv.Connect` 命中 chunk 111；README 的多詞查詢 `HFSS scripting environments v261` 未命中，簡化成 `HFSS` 後命中 chunks 1、7，`get_chunk` chunk 7 回查到 15 個主題及 1 complete。


### 2026-10-31 PyRocky HTML sidecar：Moving wall 粒子互動案例

- 核讀 `particle_wall_interaction_with_motion.html` 原檔及其 Markdown sidecar，整理 project/study、L-shape STL wall、粒子與 inlet/outlet、motion frame、domain、5 s 求解及與結果讀取子題的分工。案例輸入原值與單位照錄；`SetMassFlowRate(1000)` 原文沒有明示單位，不補推。
- [Rocky 字典](rocky.md)與 [topics.csv](topics.csv)將 Moving wall 案例標為 complete。原始結果圖 `Lshape_tube_result.png` 未鏡像，圖像與物理結果未查核；產品 release unknown，SDK 路徑 0.6.2，URL stable。
- 未啟動 Rocky 或求解。索引回查：字典 alias 查詢 `Lshape_tube AddRotationMotion DisableUseBoundaryLimits SetSimulationDuration` 命中 chunk 1，`get_chunk` 含 STL、motion frame、domain 與 5 s 案例設定；原始教學 alias 多詞查詢 `AddRotationMotion SetSimulationDuration` 未命中，分別查詢 `AddRotationMotion` 命中 chunks 6–7、`SetMassFlowRate` 命中 chunk 5、`StartSimulation` 命中 chunk 9、`Lshape_tube` 命中 chunks 0、2、8，各片段含對應 API／案例步驟。README alias 查詢 `Rocky moving wall 7 topics` 命中 chunk 6，可回查 7 主題及 2 complete 狀態。


### 2026-10-31 Granta MI Scripting Toolkit 認證與排程

- 核讀 Toolkit 5.0 Authentication guide 及 SessionBuilder sidecar，整理 Autologon／Basic／OIDC server mode 相容性、HTTPS 要求、互動／batch 憑證取得方式、keyring backend 限制、Windows Task Scheduler 身份條件，以及 OIDC refresh token 的保存與機密性。
- [Granta MI 字典](granta_mi.md)與 [topics.csv](topics.csv)將「認證模式與排程限制」標記為 complete。指南更新日期 2026-06-18；來源清冊的產品/server release 為 unknown，未推定租戶現況。
- 未連接 Granta MI、未提交認證或執行排程。索引回查：字典 alias 查詢 `Autologon Basic OIDC Task Scheduler refresh token` 命中 chunk 1；`get_chunk` chunk 1 含認證模式、HTTPS 與 OIDC token，查詢 `Log On As Batch Job` 命中 chunk 2 並回查排程身份限制。Authentication 原文 alias 初始多詞查詢 `Task Scheduler Log On As Batch Job keyring` 未命中；簡化查詢 `autologon` 命中 chunks 0–1、`keyring` 命中 chunks 6–8、`OIDC refresh token` 命中 chunks 11–12。SessionBuilder 原文 alias 多詞查詢 `with_oidc with_stored_token persist_oidc_token` 未命中；`with_oidc` 命中 chunks 20–22，`persist_oidc_token` 命中 chunks 8、19、23。README alias 多詞查詢 `Granta MI 9 topics authentication schedule` 未命中；簡化為 `Granta MI` 後命中 chunk 6，可回查 9 個主題及 3 complete 狀態。


### 2026-10-31 Lumerical 官方 Python API 與 Interop Server 外連核讀

- 由本機 `python-lumapi.md` 的官方 Ansys Optics URLs 開啟 Python API overview、Session Management 與 Interop Server - Remote API。整理 product session constructors／context manager cleanup、remoteArgs、Linux-only server，以及 2023 R1.2 與 2025 R2.4 的功能／認證版本界線。
- [Lumerical 字典](lumerical.md)與 [topics.csv](topics.csv)更新 Lumapi／Interop Server 主題為 complete；既有 [markdown_links.csv](markdown_links.csv) 三條官方連結標為 `official_page_reviewed_summary_only`。遠端文章未下載或鏡像，只在字典保留摘要及原始連結；產品安裝 release 仍 unknown。
- 未啟動 Lumapi 或 Interop Server。索引回查：字典 alias 多詞查詢 `remoteArgs Linux Interop Server 2025 R2.4 mTLS` 未命中，簡化為 `remoteArgs` 命中 chunk 1，`get_chunk` 含遠端參數與 Linux／2025 R2.4 邊界；`2025 R2.4` 命中 chunks 1–2，chunk 2 含 mutual TLS 與 client certificate 條件。原始 developer portal Markdown alias 查詢 `Interop Server remote execution Linux` 未命中；簡化為 `Interop Server` 命中 chunks 0–1，僅確認原頁含外連導覽。README alias 查詢 `Lumerical Interop Server session` 命中 chunk 6，可回查 5 個主題及 1 complete。外部官方文章未鏡像，內容檢索由字典摘要承接，並可沿直接 URL 回原頁。


### 2026-10-31 Maxwell 腳本環境主題補全

- 依 v261《Maxwell Scripting Guide》（封面標示 Ansys Electromagnetics Suite 2026 R1）正文整理 Desktop IronPython、Standalone IronPython、CPython／gRPC 及手冊標為 Beta 的 PyAEDT；摘要包含 IronPython runtime 限制、`InitializeNew()`／`Initialize()` 差異、`ScriptEnv.Shutdown()`、預設 port 50051 及 port range 注意事項。
- [Maxwell 字典](maxwell.md)與 [topics.csv](topics.csv)將 `Scripting environments` 更新為 complete；Maxwell 另 2 個物件模型／Solution commands 主題維持 draft。PDF 已有逐頁 Markdown 抽取，本次未轉寫或修改原 PDF／sidecar。
- 索引回查：字典 alias `external_37247021627c_maxwell` 查詢 `CPython gRPC port 50051 InitializeNew` 命中字典摘要；`get_chunk` 含 CPython server/client、InitializeNew／Initialize、port 與 Shutdown 條件。原文 `ansys_e3c61f8717103dd92e9e7337` 查詢 `InitializeNew Initialize port 50051` 命中 Maxwell Scripting Guide 章節，可回查正文與 PDF 頁碼。未啟動 AEDT 或執行範例。


### 2026-10-31 Q3D Reporter 匯出主題補全

- 直接核對 v261／2026 R1《Q3D Extractor Scripting Guide》逐頁 Markdown：PDF Page 739 說明 Reporter commands 透過 `oDesign`／`ReportSetup` module 操作；PDF Pages 794–795 列 `ExportToFile` 用法、UI access、參數、回傳值及五種格式；Page 792 記錄舊 `ExportReport` 相容說明。
- [Q3D 字典](q3d.md)及 [topics.csv](topics.csv)將 `Reporter ExportToFile`、`Export formats and compatibility` 更新為 complete；`Scripting environments` 仍為 draft。原 PDF 與逐頁 Markdown 未修改，且本機命令 API 摘要保留原有限定。
- 索引回查：`Q3D Reporter ExportToFile csv rdat` 命中字典；`get_chunk` 含 ReportSetup、命令介面與格式條件。原 PDF alias `ansys_519cef8fcfec74fabeb25e81` 以 `ExportToFile ReportName FileName` 命中 PDF Page 794–795，可回查同一命令原文。未啟動 Q3D 或產生匯出檔。


### 2026-10-31 SIwave PCB／package 教學主題補全

- 依兩份 v261／2026 R1 官方 Getting Started PDF 的逐頁 Markdown，整理 PCB ANF 匯入、power/ground 分類、Validation Check、Resonant Modes、SIwave SYZ／PSI SYZ／AC Current 教學；另整理 SIwave-CPA pin groups、Package RLCG extraction 的選項限制與結果型態。案例頻率、net 名、core 數與檔名均標明為教學值。
- [SIwave 字典](siwave.md)與 [topics.csv](topics.csv)將 `PCB model setup and analyses`、`SIwave-CPA RLGC`、`PCB versus package model` 標為 complete；`Scripting Guide` 保持 draft。兩份手冊以案例說明區別，未宣稱完整產品能力比較。
- 實際索引回查：`SIwave PCB validation Resonant Modes SYZ PSI` 命中字典與 PCB Getting Started 原文，字典片段含 validation 及四類案例分析；`SIwave CPA pin groups RLCG Package` 命中字典及 CPA guide，字典片段含 Package 模式／pin groups／結果型態；原文查詢 `siwave_board.anf` 與 `analysis.anf` 分別命中兩本指南，`get_chunk` 可取回 ANF 匯入章節。比較查詢 `PCB package ANF siwave_board analysis` 僅命中字典比較表，未同時回到兩份原文；分開按檔名查詢可各自定位。未啟動 SIwave、未匯入模型或求解。


### 2026-10-31 HFSS T-Junction 與 Optimetrics 案例核讀

- 依 v261／2026 R1 T-Junction guide 整理三段 Boolean waveguide 幾何、Wave Port／integration line、septum `Offset` 變數、10 GHz Driven Modal setup、Interpolating sweep 及 S-parameter 比較。對優化 guide 另整理 parametric sweep、功率輸出量與 `Power31-2*Power21` 目標。
- 視覺核對優化 PDF Pages 36 與 41：Page 36 的步驟及圖表明列 `Acceptable Cost = 3e-4`，Page 41 文字稱停止門檻 `0.001`，屬同一本手冊的不一致；字典保留兩值。PDF 標題提及 SpaceClaim Link，但 TOC／正文沒有該流程章節，標為來源缺口。
- [HFSS 字典](hfss.md)及 [topics.csv](topics.csv)將 Waveguide T-Junction 標 complete；T-Junction optimization 標 source_limited；Waveguide Combiner、HFSS 3D Layout 仍 draft。更新後 HFSS 為 2 draft、2 complete、1 source_limited。
- 實際索引回查：`HFSS T-Junction Offset Modal 10 GHz S12` 命中字典並 `get_chunk` 取回解算／S 參數摘要；優化複合查詢 `HFSS Optimetrics Power31 Power21 3e-4 0.001` 未命中，簡化為 `Power31` 與 `acceptable cost Offset` 可命中字典，`get_chunk` 含成本函數與手冊差異；原文查詢 `Power31-2*Power21 Offset` 命中優化 guide。未執行 HFSS／AEDT 分析或 Optimetrics。


### 2026-10-31 Circuit CPython／gRPC session 核讀

- 依 v261／2026 R1 Circuit Scripting Guide PDF Pages 79–82 正文整理 DesktopPlugin path 前置、gRPC client/server 角色、port 50051／range、Connect 四種路徑、InitializeNew 與 Initialize 差異、Shutdown 呼叫時機。沒有將其他 design type API 或未記載的認證設定推定為 Circuit 保證。
- [Circuit 字典](circuit.md)及 [topics.csv](topics.csv)將 `CPython 與 gRPC 連線` 更新為 complete；環境／物件模型、UDM／UDP 與記錄／執行入口仍待整理，版本限制仍 source_limited。未執行 AEDT。
- 實際索引回查：`Circuit CPython gRPC port 50051` 命中字典及 Circuit Scripting Guide 原文；`get_chunk` 字典 chunk 0–1 可取 CPython server／port 與連線條件，原文 chunk 90 可回查 Shutdown／`-ng`，chunk 89 含 InitializeNew／Initialize 差異。查詢 `ScriptEnv.InitializeNew Shutdown` 過寬，先回 IronPython external-script 片段；簡化為 `InitializeNew Port 50051` 後命中字典與 CPython 原文。未啟動 AEDT。


### 2026-10-31 PyCFX session 與資料承接主題補全

- 核對 PyCFX 0.3.0 官方 `session` 與 `launching_cfx` 本機 sidecar，整理 PreProcessing／Solver／PostProcessing 用途、設定物件共用介面、`from_install`／`from_session` 建立途徑、輸入檔型別、solver setup snapshot 與 PostProcessing 等待結果的條件。
- 初版 PyCFX 搭配 CFX 2025 R2 SP3 的 local-machine 限制明確標為來源原文範圍；未由 SDK 0.3.0 推定當前 CFX release 相容性。`PyCFX 與 CFX 版本邊界` 更新為 source_limited。
- [CFX 字典](cfx.md)及 [topics.csv](topics.csv)將 session roles 與 startup/session handoff 更新為 complete；CFX 共 9 個主題，3 draft、5 complete、1 source_limited。
- 實際索引回查：`PyCFX PreProcessing Solver PostProcessing session` 命中字典與 launch／user guide；字典 `get_chunk` 取回三類 session，來源清冊對應原始 guide。`from_install from_session result wait_for_run` 複合查詢僅命中字典；簡化查詢 `from_install` 命中 launch guide、session guide 及 API reference，`get_chunk` 可取回結果等待與 session 方法片段。版本查詢 `2025 R2 SP3` 僅命中字典；`Service Pack 3` 與 `initial release local machine` 可命中 launch guide 原文。未啟動 CFX、未執行範例或求解。

### 2026-10-31 v261 optiSLang DOESettings 與 DOETYPES API 清單

- 對照 v261 optiSLang Python API 官方 Markdown 正文：`py_doe_settings.md` 列出五個 properties 及 `set_default(DOETYPES)`；`dynardo_py_algorithms.md` 列出 22 個 `DOETYPES` enum 名稱。來源清冊 ID 分別為 `ansys_971500135d4c5e35b21c0979`、`ansys_50d5d1ba85d89462ea352d31`，均標示 v261／`body_present`。
- [optiSLang 字典](optislang.md)新增有界主題「v261 DOESettings 欄位與 DOETYPES 值清單」，並於 [topics.csv](topics.csv)標為 complete；這只代表 API 成員及 enum 名稱已盤點。原文沒有各抽樣法定義、型別、預設值或選用指南，故「DOE 與敏感度」整體仍為 draft。未執行 optiSLang。
- 實際全文索引回查：`DOETYPES` 命中 v261 `dynardo_py_algorithms` 原文與字典，兩處 `get_chunk` 成功；`ADVANCEDLATINHYPER`、`STARPOINTS` 各自可命中 enum 原文與字典，片段保留對應名稱。`DOESettings num_dimensions num_points seed` 命中 v261 `py_doe_settings` 原文及字典，均成功取回片段。多詞 AND 搜尋僅命中字典時，改用單一 API 名稱可回到官方頁。

### 2026-10-31 Mechanical v261 Frictionless contact pinball script example

- 核對 Mechanical Scripting Guide v261 physical page 206 的「Set Pinball to 5mm for all Frictionless Contacts」腳本，並對照 v261 `ContactRegion`、`ContactType`、`ContactPinballType` 本機官方 API 正文。手冊示例以 `Transaction()` 取得所有 contact regions，篩選 Frictionless 後設定 Radius 與 `Quantity("5[mm]")`。
- [Mechanical 字典](mechanical.md)新增有界子題「v261 Frictionless 接觸的 Pinball 半徑腳本範例」，[topics.csv](topics.csv)標為 complete。5 mm 僅為手冊示例；全模型篩選範圍、單位與模型尺度限制已標示。Mechanical「接觸與邊界條件」整體仍為 draft。
- 實際全文索引回查：`ContactPinballType Radius Frictionless 5mm` 命中字典 chunk 4 及 v261 Scripting Guide chunks 193／223；`PinballRegion PinballRadius ContactType.Frictionless` 也命中字典與兩筆 v261 正文。所有命中均成功 `get_chunk`，片段含 pinball 模式、半徑及 Frictionless 篩選。未在 Mechanical 執行腳本或求解。

### 2026-10-31 PyDYNA Taylor Bar deck、multi-velocity solve 與 DPF 後處理

- 核讀 PyDYNA Taylor Bar 官方 tutorial HTML 與 Markdown sidecar（source ID `ansys_0d86b672086424a3db6fc15c`，`body_present`，`version/stable` URL，release unknown）。摘要涵蓋 deck cards、`input.k`／mesh 工作目錄、`run_dyna`、`d3plot` 檢查、PyDPF global kinetic energy 及四個初始速度案例；SDK 0.12.1 僅為本機路徑 metadata。
- [LS-DYNA 字典](lsdyna.md)新增 `PyDYNA Taylor Bar multivelocity solve and DPF postprocessing` 有界子題並在 [topics.csv](topics.csv)標為 complete。教學內嵌 solver log 不視為本次運算證據；產品 release／solver 相容性未由此頁推定。
- 實際全文檢索：`global_kinetic_energy` 命中官方 tutorial chunk 5 與字典 chunk 16；`taylor_bar_mesh` 命中 tutorial 多個 chunks（含 0、1、15）及字典 chunk 15；`get_chunk` 均成功，片段可定位 deck／動能流程。三詞 AND 查詢 `Taylor_Bar global_kinetic_energy taylor_bar_mesh` 未命中；改用單一 API／檔名詞可回到原文。未執行 tutorial、LS-DYNA 求解或 PyDPF 計算。

### 2026-10-31 PyDPF FieldsContainer multi-label time／element-shape access

- 核讀 PyDPF-Core `Fields containers and fields` 官方 HTML／Markdown sidecar（source ID `ansys_a651dc9eb40b833a1bff65be`，`body_present`，`version/stable` URL，release unknown；本機 SDK metadata 路徑為 0.16.3）。原頁示範 `on_all_time_freqs.split_by_shape`，並用 `get_field({'time': 1, 'elshape': 0/1})` 取不同 labels 的 fields；保留兩個輸出中的 entity／component／elementary-data 計數作為示例值。
- [DPF 字典](dpf.md)新增有界主題 `PyDPF FieldsContainer multi-label access to time and element-shape fields` 並於 [topics.csv](topics.csv)標為 complete；原頁沒有整數 `elshape` 到具名 element shape 的對照，因此字典明確保留未知項。DPF「Fields、FieldsContainer 與 Scoping」整體仍是 draft。
- 實際索引回查：`split_by_shape elshape get_field` 命中字典及 FieldsContainer 原文的相關片段，`get_chunk` 成功；來源 ID 限定查詢 `split_by_shape` 命中 `ansys_a651dc9eb40b833a1bff65be` chunk 4，片段含 `elshape` 與 `split_by_shape`。`elshape 9052 37580` 命中字典及其他包含同一輸出值的來源片段。未在 PyDPF-Core 執行範例或讀取實際結果檔。

### 2026-10-31 OpenTD.Results Dataset loading 與 DataArray retrieval

- 核讀 OpenTD 2026 R1 `Reading results` 官方 Markdown 正文及 Changelog。正文涵蓋 64-bit `OpenTD.Results.dll`／project 前置條件、Dataset factory、`IDataset.GetData`／`DataArray.GetValues`、SI／English units、時間資料及缺值 NaN；Changelog 將 .NET 8 radk 讀取列為 2026 R1 新功能。
- [Thermal Desktop 字典](thermal_desktop.md)新增 `OpenTD.Results direct Dataset loading and DataArray retrieval` 有界子題並於 [topics.csv](topics.csv)標為 complete；短 snippet 的 `new DatasetFactory.Load(...)` 與完整範例 `DatasetFactory.Load(...)` 寫法差異已標示。高階 group／derived dataset／plot 工作仍未涵蓋，父級 Results 主題維持 draft。
- 實際索引回查：字典查詢 `DatasetFactory.Load GetData NaN Units.SI` 命中 chunk 4，`get_chunk` 成功；來源 ID 限定的 `DatasetFactory.Load` 命中 chunks 1／2／9 等、`DataArray NaN` 命中 chunk 5、`GetValues Units.SI` 命中 chunks 1–3，均成功 `get_chunk` 並回到 OpenTD 2026 R1 原文。

### 2026-10-31 PyFluent solution variable zone data access

- 核讀 PyFluent `Solution variable data` 與 `Choosing between field data and solution variable data APIs` 官方 HTML／Markdown sidecar；本機 SDK metadata 0.42.1，URL 為 `version/stable`，來源 release unknown。記錄 `get_zones_info`／`get_variables_info`、SVAR `get_data`／`set_data`、`create_empty_array` 與 zone name array 對應；官方示例回傳 zone order 與 request order不同，字典已提醒按名稱配對。
- [Fluent 字典](fluent.md)新增有界子題 `PyFluent solution variable zone metadata and read/write`，在 [topics.csv](topics.csv)標 complete；500／600 pressure 值只作文件示例，不當成工程建議。未啟動 Fluent，未寫入 solver arrays。
- 實際索引回查：`solution_variable_data get_data set_data zone_names` 命中官方 `Solution variable data` chunk 2 及 API comparison chunk 2，均成功 `get_chunk`；`wall-elbow elbow-fluid 17822` 命中 source chunks 2–3，可取回 zone arrays 範例。來源 ID 限定查詢 `get_data`、`set_data`、`wall-elbow` 亦分別命中並成功擷取對應片段。

### 2026-10-31 PyAnsys Geometry Modeler instance ownership 與 close

- 核讀 PyAnsys Geometry 0.18.2 Modeler API 官方 HTML／Markdown sidecar（source ID `ansys_32510d49bdc2ead838072784`，`body_present`，SDK metadata 路徑 0.18.2，URL 為 `version/stable`，release unknown）。原頁記載 PyPIM `remote_instance`、`launch_docker_modeler` 的 `docker_instance`、Discovery／SpaceClaim `product_instance` 均在 `GrpcClient.close` 時刪除；`Modeler.close`／`exit` 皆為 client close 入口。
- [Geometry 字典](geometry.md)新增 `PyAnsys Geometry Modeler ownership and close semantics` 有界子題並於 [topics.csv](topics.csv)標 complete。原頁沒有將 instance deletion 說明延伸至任意 host／port/channel server，也未說明設計資料保存；產品及 Geometry service release 未由 SDK path 推定。
- 實際索引回查：Modeler API source ID 限定查詢 `GrpcClient.close remote_instance` 命中 chunk 3 並成功 `get_chunk`；Geometry 字典產品限定查詢 `launch_modeler_with_spaceclaim` 命中 `external_23b183911d94_geometry` chunk 0，亦成功取回字典片段。未啟動 Geometry service 或建立 Modeler 連線。

### 2026-10-31 EduPack CHM 短篇詞條 HTML 補轉

- 依最新 `_catalog/html_conversion_manifest.json`，EduPack CHM 有 1,491 個 HTML 頁：原有 1,381 個 converted、109 個短篇詞條因 100 字門檻被列為 failed、1 個內容重複頁沿用 canonical Markdown。檢視 109 個原始 HTML 後，確認皆有詞條標題及定義／清單；使用可復原不規則實體的 HTML parser 逐頁轉成同目錄 Markdown，保留標題、段落、清單及表格文字，狀態改列 `plain_text_fallback`。
- 109 個原始 HTML、所有 PDF 與其餘 sidecar 均保留；文件清冊的 109 個 EduPack source ID 改為 `body_present` 並指向新 Markdown。ACT 0-byte HTML 仍為唯一 HTML failed 項；PDF 清冊的 Speos RAL 掃描色票仍待 OCR。
- 轉換後清冊計數：171,698 converted、151 plain-text fallback、49 reused existing Markdown、1 failed；HTML 可用正文覆蓋 572,288／572,288。實際索引搜尋與 `get_chunk` 回查：EduPack 產品限定查詢 `specific machine settings` 命中 `ansys_2dee68c686a5b28793d4d62b` chunk 0，片段含 `Mode` 定義；`Actual discharge current` 命中對應 source ID chunk 0 並取回電池詞條定義。另用 Q3D PDF alias `ansys_519cef8fcfec74fabeb25e81` 搜尋 `ExportToFile ReportName FileName`，命中 PDF-backed chunks 662／1074／1075，`get_chunk` 成功回到原 PDF 路徑及正文。

- SQLite 以單一增量交易新增 109 個 EduPack 正文 alias，並同步 Geometry 字典、README、本紀錄三個 Markdown alias；代表搜尋皆成功 `get_chunk`。`PRAGMA quick_check` 回傳 `ok`，`index._needs_rebuild()` 為 `False`；未重建全庫。


### 2026-10-31 DPF Server／client 與執行位置主題

- 核對本機 Ansys DPF v261 `Ways of Using DPF` Markdown（頁面標示 2026-03-25 更新）及 PyDPF-Core SDK metadata 0.16.3 `DPF model` sidecar。整理 server kernel／operator-library 關係、CPython／IronPython／C++ client、同程序／gRPC 通訊、Mechanical／standalone 使用位置，以及結果檔路徑相對於 DPF server 的語意；PyDPF-Core 來源 release 維持 unknown。
- [DPF 字典](dpf.md)新增有界子題並將其登記為 `complete`；較廣泛的「Server 與 client 使用方式」仍維持 `draft`，因未比較跨版本相容、授權及各產品可用的 operator libraries。未啟動 DPF server、Mechanical 或求解。
- 索引搜尋與 `get_chunk` 回查：DPF 產品篩選查詢 `server application operator libraries` 命中 v261 原文；限定 v261 `Ways of Using DPF` source ID `ansys_9f58489e0c3241493d0d41b1` 查詢 `gRPC IronPython` 命中 chunk 1，成功取回 client／通訊章節；限定 PyDPF-Core Model source ID `ansys_d3a4dc858e42fbe5087838db` 查詢 `absolute path relative DPF server` 命中 chunk 0，片段明載結果檔路徑相對於 DPF server。DPF 字典產品篩選查詢 `DataProcessingCore operator libraries` 亦命中新增子題並成功取回。


### 2026-10-31 PyFluent launch／attach 入口選擇

- 核讀本機 `ansys-fluent-core` SDK metadata 0.42.1 的 `Launching and connecting to Fluent` 與 `Using PyFluent sessions` sidecar。依來源整理 `from_install`、`from_container`（Docker／Podman Compose）、`from_pim`、`from_connection` 的入口差異，及外部啟動需開啟 gRPC、建議以 server-info file 傳遞 IP／port／password；區分低階 `launch_fluent()`／`connect_to_fluent()`。文件範例的 v252 container product version 僅是範例值，沒有推定 SDK 0.42.1 所支援的產品版本矩陣。
- [Fluent 字典](fluent.md)新增 launch／attach 有界子題並登記 complete；較大的「PyFluent session 與啟動方式」仍為 `draft`。process ownership／cleanup 由既有獨立子題記錄，本文未啟動 Fluent。
- 索引搜尋與 `get_chunk` 回查：Fluent 產品限定查詢 `from_install from_container from_pim` 命中字典及 PyFluent session 原文；launch guide source ID `ansys_e40af2e24d84fda0f3d5674e` 查詢 `server info file IP port password` 命中 chunks 15–17，均可取回 server-info／連線範例；session guide source ID `ansys_a79a80046f30ff1aec049a1c` 查詢 `from_<...> class methods recommended` 命中 chunks 0–1。


### 2026-10-31 PyAnsys Sound STFT／ISTFT 教學子題

- 核讀 PyAnsys Sound SDK metadata 0.4.0 的 `Spectrogram: compute the STFT and ISTFT` HTML 對應 Markdown sidecar（source ID `ansys_399624922acb95fb64909461`）。記錄 `LoadWav` 的 FieldsContainer 輸出、`Stft` 的 `fft_size`／`window_overlap`／`window_type` 示例與 `Istft` 流程；1024／4096、0.95、`TRIANGULAR` 均保留為教學值，不推導頻率解析度或重建精度。
- [Sound 字典](sound.md)新增有界子題並標為 `complete`；廣泛的「STFT／ISTFT 與 spectrogram」仍為 draft，因來源未定義參數選擇準則、window normalization、邊界處理或誤差驗證。未執行音訊處理。
- 索引搜尋與 `get_chunk` 回查：限定 STFT gallery source ID `ansys_399624922acb95fb64909461` 查詢 `fft_size window_overlap TRIANGULAR` 命中 chunk 2，片段包含兩組 FFT size 與 overlap／window 設定；`Istft stft get_output` 亦命中 chunk 2 並成功取回逆轉換流程。Sound 字典產品篩選查詢同一組參數詞亦命中新子題，`get_chunk` 成功。


### 2026-10-31 PyMAPDL gRPC 工作目錄與檔案交接

- 核對 PyMAPDL `ansys-mapdl-core` SDK metadata 0.74.1 User guide 與 `PyMAPDL language and usage` sidecar。整理 `launch_mapdl()` 的 gRPC 啟動與預設暫存工作位置、`run_location`、`Mapdl.directory`／`list_files()`，及 client／MAPDL instance 間 `upload()`、`download()`、`download_project()` 的方向與用途。來源明載檔案傳輸僅適用 MAPDL 2021 R1 及更新版本；未推定暫存目錄清理時機。
- [MAPDL 字典](mapdl.md)新增有界子題並標為 `complete`；廣義 `launch_mapdl 與工作目錄` 仍是 draft。沒有啟動 MAPDL 或執行檔案傳輸。
- 索引搜尋與 `get_chunk` 回查：限定 PyMAPDL User guide source ID `ansys_0d9b850f91a170e558010fe2` 查詢 `launch_mapdl run_location temporary directory` 命中 chunk 0；`PyMAPDL language and usage` source ID `ansys_b81b6dd45d8b13e1effda070` 查詢 `download_project mapdl.directory list_files` 命中 chunk 23，片段含 server 工作目錄與檔案傳輸 API。MAPDL 字典產品篩選查詢 `run_location download_project upload` 命中新子題並成功取回片段。

### 2026-10-31 PySimAI Geometry cascade deletion

- 核讀 `ansys-simai-core 0.4.8` Geometries API Markdown sidecar。`GeometryDirectory.delete(geometry)` 與 `Geometry.delete()` 原文均說明 geometry 及其資料會從伺服器刪除，且相關 predictions、postprocessings 一併刪除；directory API 記載 geometry ID 不存在時引發 `NotFoundError`。文件未交代復原機制，字典不推定可復原。
- [SimAI 字典](simai.md)新增「Geometry 刪除與相依資料」有界子題並在 [topics.csv](topics.csv) 標為 complete；父級「Geometry 與 Prediction」仍為 draft。未連線 SimAI 服務或執行刪除操作。
- SQLite 當前鎖狀態探測以 `BEGIN IMMEDIATE` 成功取得寫入保留鎖後即 rollback，表示探測時沒有其他 SQLite writer 持鎖；Windows Restart Manager／CIM 無法回報佔用程序，故無法追查先前鎖定事件的來源。

- 索引查詢 `GeometryDirectory.delete predictions postprocessings` 命中 SimAI 字典 alias；限制 source ID `ansys_8a76a63ce1fb0cb6d6bf1286` 查詢 `predictions postprocessings` 命中官方 API chunk 1，片段明載兩種 delete API 的連帶刪除語意，`get_chunk` 成功。`NotFoundError geometry` 亦命中同一來源 chunk 1 並成功取回。


### 2026-10-31 Granta MI Connected Materials v261 Ansys ID authentication

- 核對本機 v261 getting-started 與 authentication 原文（來源 ID `ansys_c6a78f758f226df4faee793e`、`ansys_c83a10e13ca682094697909f`；頁面最後更新 2026-06-17）。記錄 hosted instance 帳號啟用前提、MSAL browser interactive access token、Bearer header 僅用於 Granta Integration Service API、不用於開啟 Material Picker，以及 HTTP JSON／SSE 範圍；authority、client ID、scope 和 redirect port 僅視為範例值。
- [Granta MI 字典](granta_mi.md)新增有界子題並於 [topics.csv](topics.csv) 標為 complete；較廣泛的 Connected Materials REST API 與 Ansys ID 認證仍維持 draft。未實際登入、呼叫服務或傳送帳號資料。


### 2026-10-31 PyACP 0.4.1 import format、unit_system 與匯出限制

- 核對 PyACP Create input file guide、`ACPInstance.import_model()` 與 `Model.export_analysis_model()` 官方 sidecar（source IDs `ansys_e28a072ff03c39cb4898e920`、`ansys_15166d4daacbd7288030ca8e`、`ansys_b691f3a22929c035278678ec`）。整理 API 可接受的格式與 format-dependent kwargs、unit_system 條件、CDB/DAT 與 Mechanical HDF5 的匯出差異，以及 CDB/DAT UVID 材料處理。
- 發現 input-format guide 將 HDF5 transfer format 寫作 `ansys::h5`，而 0.4.1 `import_model()` API 列為 `ansys:h5`；字典明列此文件差異，沒有 runtime 證據前不宣稱 guide 寫法有效。Abaqus INP／Nastran BDF 僅依 API 格式清單記錄，guide 未提供其流程細節。
- [ACP 字典](acp.md)新增有界子題並在 [topics.csv](topics.csv) 標為 complete；整體輸入格式主題仍維持 draft。未匯入模型、轉換檔案或執行 ACP 求解。

- 索引回查：ACP 字典 alias 查詢 `ansys:h5 unit_system export_analysis_model` 命中 chunk 1；限定 API source ID `ansys_15166d4daacbd7288030ca8e` 的 `ansys:h5 abaqus:inp nastran:bdf`／`unit_system from_file match input` 分別命中 chunks 0／1；input-format source ID `ansys_e28a072ff03c39cb4898e920` 的 `CDB unit system Mechanical`／`HDF5 Composite CAE PyMechanical` 分別命中 chunks 2／1；export API source ID `ansys_b691f3a22929c035278678ec` 查詢 `export_analysis_model CDB path` 命中 chunk 0，全部 `get_chunk` 成功。包含多組條件的 `ansys::h5 CDB DAT units Mechanical HDF5` 查詢 0 命中；簡化查詢可回到相關段落。雙冒號／單冒號差異由字典及本機兩份原文直接對照標示，未以 runtime 判定有效格式。


### 2026-10-31 PyAnsys Sound DPF Server 與授權 context

- 核讀 PyAnsys Sound SDK metadata 0.4.0 User guide 及 initialize-server/license gallery（source IDs `ansys_fcc093bb84f2b5065f2fdbb7`、`ansys_2e8a31b819e66f2ef613b35f`）。整理 `connect_to_or_start_server()` 的 `ANSRV_DPF_SOUND_PORT` remote 路徑、預設 `6780`／明確 port、本機 server 搜尋路徑，以及 `LicenseContextManager` 對 `avrxp_snd_level1` increment 的 checkout/release 範圍；計時差異留作 tutorial observation，不當成效能保證。
- [Sound 字典](sound.md)新增有界子題並於 [topics.csv](topics.csv) 標 complete；父級 DPF Server／license 主題仍為 draft。未啟動 server 或 checkout license。

- 索引回查：Sound 字典 alias 查詢 `LicenseContextManager avrxp_snd_level1 checkout release` 命中 chunk 0；User guide source ID `ansys_fcc093bb84f2b5065f2fdbb7` 的 `connect_to_or_start_server port 6780` 命中 chunk 1、`ANSRV DPF SOUND PORT` 命中 chunk 0；授權 gallery source ID `ansys_2e8a31b819e66f2ef613b35f` 的 `LicenseContextManager use_license_context license increment` 命中 chunk 4、`use_license_context False each operator` 命中 chunk 1，所列結果均成功 `get_chunk`。合併原環境變數名稱、port 與 remote 的長查詢未命中，拆分後的官方變數名和 port 查詢可定位來源。


### 2026-10-31 ModelCenter v261 PACZ runner 單次評估流程

- 核讀 Component Plug-in SDK v261 Getting Started（source ID `ansys_29f4b2da769a3e44643311b1`；頁面更新日期 2026-06-19）。依原文整理 runner／builder UI 分工、`ConstructAsync(IHarnessRunnerHost)` 載入 `ExtractedPacz`、`RunAsync` 的 VariableState validity／`SafeValue`／輸出寫回；記錄 runner 不含 UI、無效值會拋例外，及範例未示範 CancellationToken 處理的限制。
- [ModelCenter 字典](modelcenter.md)新增有界子題並於 [topics.csv](topics.csv) 標為 complete；PACZ 打包、部署、執行期 threading／取消處理仍未由此摘要涵蓋。未編譯或執行 plug-in。

- 索引回查：ModelCenter 字典 alias 查詢 `ConstructAsync FromPaczAsync SafeValue outputs` 命中 chunk 1 並成功 `get_chunk`；限制 v261 Getting Started source ID `ansys_29f4b2da769a3e44643311b1` 查詢 `IHarnessRunnerHost ExtractedPacz FromPaczAsync` 命中 chunk 14，`SafeValue VariableState inputs outputs cancellation` 命中 chunks 14／15，`IHarnessRunner no UI builder UI` 命中 chunks 3／4；各命中片段成功擷取並可回到原文。


### 2026-10-31 Workbench 2026 R1 DesignPoint 狀態與 CSV 匯出

- 使用現有 v261 Workbench Scripting Guide PDF 原件與逐頁 Markdown sidecar，核對 PDF viewer pp.644–646（印刷頁碼 634–636）及 pp.1305–1307（印刷頁碼 1295–1297）。Sidecar 頁面文字與 `pymupdf` 從同一物理 PDF 頁抽取的文字相符；重用現有逐頁轉換結果，未重新產生全文件。
- 整理 DesignPoint 列舉、`IsUpToDate`／`HasValidRetainedData`／`Retained`／`Exported`、expression copy 對輸出值的失效影響、active DesignPoint 刪除限制，以及 CSV export 僅含 up-to-date parameter values。原文 `ExportAllDesignPointsData` 參數列為 `FilePath`、範例卻傳 `FileName`；`UpdateAllDesignPoints` 也標示無細節，因此以文檔差異及未涵蓋範圍明列，未推定更新流程。
- [Workbench 字典](workbench.md)新增有界子題並於 [topics.csv](topics.csv) 標為 complete；父級「Parameters 與 Design Points」仍為 draft。未在 Workbench 執行 API 或修改專案檔案。

- 索引回查：Workbench 字典 alias 查詢 `HasValidRetainedData Retained ExportAllDesignPointsData FilePath` 命中 chunk 2 並成功 `get_chunk`；PDF source ID `ansys_05b664ec1d5ee31846d738a4` 的狀態查詢命中 chunk 656、簡化後的 active-point delete query 命中 chunk 657、`ExportAllDesignPointsData FilePath AppendMode up-to-date` 命中 chunk 1173、`GetAllSortedDesignPoints GetAllDesignPointsWithFiles` 命中 chunk 1174、`UpdateAllDesignPoints No details` 命中 chunk 1219，均成功取回來源。包含多組刪除條件的初始查詢 0 命中，縮短後可定位 DesignPoint.Delete 原文。


### 2026-10-31 PyTurboGrid SDK 0.9.4 Rotor 37 INF 網格範例

- 重用已存在的官方 HTML 對應 Markdown sidecar，未重新轉換或修改原始 HTML；正文保留 `source_url`、程式碼區塊及操作標題。來源 ID `ansys_c97e17bb7549b6fe03745383`，產品 TurboGrid release 未知、SDK 版本 0.9.4。
- 依 `Basic mesh generation` 原文整理 `launch_turbogrid()`、`get_turbogrid_exe_path()`、`BladeGen.inf`、`unsuspend(object="/TOPOLOGY SET")` 預設網格生成、`query_mesh_statistics()`、`save_mesh()` 與 `quit()`；限制 Rotor 37 範例，不推定其他幾何的品質門檻或路徑行為。未啟動 TurboGrid。
- [TurboGrid 字典](turbogrid.md)新增有界流程摘要，[topics.csv](topics.csv) 將 Rotor 37 有界子題標為 `complete`，較廣的「基本網格生成」父題仍為 `draft`；其他四項既有主題仍為 draft，STAC 子題另見下段。
- 索引原文查詢 `launch_turbogrid`、`get_turbogrid_exe_path`、`read_inf BladeGen.inf`、`unsuspend topology`、`query_mesh_statistics`、`save_mesh rotor37` 均命中官方來源並成功 `get_chunk`；包含 5 組 API 的長查詢沒有命中，拆成短查詢可定位各段。
- 本次檢查 `BEGIN IMMEDIATE` 可取得 writer lock 後 rollback，`PRAGMA quick_check` 為 `ok`，`_needs_rebuild()` 為 `False`。可證明檢查時索引可讀寫且無需全庫重建，無法識別先前造成鎖定的程序。


### 2026-10-31 PyTurboGrid STAC 多列葉輪 TGMachine 範例

- 本機 TurboGrid SDK 0.9.4 目錄有 7 個 HTML，7 個均有同名 Markdown sidecar；未發現 PDF。官方 `Multi-blade STAC example` 來源 ID `ansys_836bfdf2b3a921f0135eef33` 原已在 catalog／FTS，但漏列於 `sources.csv`；本次補上來源列。
- 核讀原文並整理 `init_from_tgmachine()`、TGMachine／INF 順序及曲線路徑、列別 `set_obj_param()`、四列 spanwise 教學值、`MIN_FACE_AREA`／machine size factor、element count 與 `save_meshes()`。文件註記 `mbr.quit()` 在範例版本尚待修正，範例暫用 `mbr.tg_worker_instances = None`；未推定此作法可完整釋放程序。
- [TurboGrid 字典](turbogrid.md)新增 STAC 有界子題並標為 `complete`；同一主題父項 `Multi-blade-row` 仍是 draft。STAC 來源引述的第三方 [University of Stuttgart test case](https://www.itsm.uni-stuttgart.de/en/research/test-cases/STAC/) 已列入 [Markdown 連結清冊](markdown_links.csv)，未擷取其正文。
- 索引回查以 `init_from_tgmachine`、`tg_worker_instances set_obj_param`、`MIN_FACE_AREA set_machine_size_factor`、`save_meshes mbr.quit` 查官方 source ID，並以 `STAC TGMachine MIN_FACE_AREA` 查字典；各結果均成功 `get_chunk`。未啟動 TurboGrid 或驗證生成的網格。


### 2026-10-31 PySimAI 0.4.8 TrainingData 至模型設定教學流程

- 重用本機 PySimAI SDK 0.4.8 `Building a model` HTML 對應 Markdown 及 `TrainingData`、`Projects`、`Model configuration` API sidecar。依原文整理 training data 建立／`upload_folder()` 上傳、建立 Project 並關聯、設定 ModelInput／ModelOutput／Global Coefficients／DomainOfAnalysis、檢查 `project.is_trainable()` 後呼叫 build 的順序。
- 原 guide 將 model building 標為 experimental，並出現前段定義 `simai_client`、後段改用 `simai` 的變數命名不一致；另傳入已標 deprecated 的 `build_on_top`。字典保留這些限制，不執行上傳或建置。
- [SimAI 字典](simai.md)新增 bounded workflow 子題並在 [topics.csv](topics.csv) 標為 `complete`；較廣的「Training data、Project 與模型建置」仍為 draft。SDK 版號為 0.4.8，服務端版本未從 stable URL 推定。
- 索引搜尋與 `get_chunk`：Building a model source ID `ansys_6995c508569ff337c2b1d9dd` 查詢 `upload_folder my-first-data`、`ModelInput ModelOutput global_coefficients`、`simai.models.build` 成功；TrainingData API `ansys_9d8fb122a9e08e0fb6873b33` 的 `upload_folder`、Projects API `ansys_06a77f8e31736fe81fb67e50` 的 `is_trainable`、Model configuration API `ansys_c146393d86eea0e92de9c9ef` 的 `build_on_top` 亦成功取回來源片段。未在 SimAI 執行 API。


### 2026-10-31 LS-DYNA R16 `*MAT_022` 卡片結構與適用範圍

- 重用 R16 Vol. II 逐頁 Markdown，核對 PDF physical pages 315–320（印刷頁 2-245–2-250 (MAT)）。另以 Poppler 渲染 PDF physical pages 315–317，視覺比對 *MAT_COMPOSITE_DAMAGE 卡片欄位、Type 與 Default 列；清理本次檢查用暫存圖檔。來源清冊 release 維持 `unknown`，僅保留內頁 R16 標記。
- 摘要材料適用元素、複合材料與 shell laminate 說明、Card 1–5 欄位／型別／預設值、材料方向與強度欄位，以及 AOPT／MACF／ATRACK 限制。完整失效準則被原文導向 Theory Manual，未補寫準則公式或選材建議。
- 發現同一 R16 卡片的 Card 2 表列 `MACF` default `0`，說明段則寫 `EQ.1` 為不交換且是 default；字典保留此處原文不一致，未選定其中一個值。
- [LS-DYNA 字典](lsdyna.md)新增有界子題並在 [topics.csv](topics.csv) 登記為 `complete`；廣義「Keyword 與模型控制」仍為 draft，完整材料卡目錄仍待整理。
- 索引查詢 `MAT_COMPOSITE_DAMAGE MAT_022 Card 1 EA PRBA`、`KFAIL AOPT MACF ATRACK default`、`YC positive value SN SYZ SZX`、`ATRACK shell deformation Remark 3` 命中 R16 Vol. II source ID `ansys_46cea1557af4f2db5b745cbd`，均成功以 `get_chunk` 取回相關頁面片段。
- 字典 alias `external_53495cef3a69_lsdyna` 限定查詢 `MAT_022`、`Composite Damage`、`Card 1 PRBA KFAIL`、`MACF default ATRACK` 均命中並成功 `get_chunk`；增量同步後 `_needs_rebuild()` 為 `False`，SQLite `PRAGMA quick_check` 回傳 `ok`。


### 2026-10-31 Workbench v261 ACT task input/output transfer

- 對照 ACT Customization Guide 的已轉換 Markdown 與原 PDF：印刷頁 83–84（PDF physical pages 93–94）說明 update callback 的上游資料取得與 output transfer property；印刷頁 104–105（physical pages 114–115）展示 Generic Material Transfer XML 與 IronPython callback。
- 已視覺核對 PDF physical pages 93–95、113–115 的頁尾編號與表格／程式片段；整理 `GetInputDataByType`、`GetOutputData` 及 MatML31 `TransferFile` 範例，未修改 PDF 或 Markdown sidecar。
- [Workbench 字典](workbench.md)新增有界 complete 子題並列入 [topics.csv](topics.csv)；僅覆蓋一種 transfer type，不代表完整 Appendix C transfer matrix。
- PDF alias 查詢 `GetInputDataByType GetOutputData TransferFile` 與 `MatML31 TransferFile registered` 均命中並能 `get_chunk`；Markdown alias 查詢 `GenericMaterialTransfer`、`MatML31` 可回查範例片段。未執行 ACT extension 或 Workbench workflow。


### 2026-10-31 首批四產品 PDF／HTML sidecar 頁碼修復與 Granta MI MMO

- 首批目錄盤點 15 份 PDF 與 1,060 份 HTML；每份來源都有同名 Markdown sidecar。HTML sidecar 均超過 120 字，且前 1,200 字含 `source_url` metadata。這是輸出存在與基本來源標記核對，不代表逐頁核實每張圖片、表格或技術內容。
- PDF 頁標記抽查發現 SpaceClaim ACT Customization Guide、Mechanical Scripting Guide、Mechanical ACT Customization Guide 三份既有 sidecar 缺少逐頁註記。依 `pdf-to-md` 技能的既有 `convert.py` 重轉至原 sidecar 路徑，先將舊 Markdown 原樣備份至 `ANSYS_Document/_conversion_backups/2026-10-31_pdf-page-markers/`；PDF 原件未動。新 sidecar 的 `<!-- page N -->` 與可抽取頁一致：18、419、64 頁；Mechanical Scripting Guide 有 3 個空白／無可抽取文字頁，轉換器略過，未做 OCR。為讓索引保留頁碼，三份 sidecar 另加 `## PDF Page N` 標題；其餘 12 份 PDF 原有頁標記與非空頁抽取數相符。
- SpaceClaim、Mechanical、LS-DYNA、optiSLang 目錄分別有 4/0、2/236、7/247、2/577 份 PDF/HTML；HTML sidecar 只做存在與 metadata 檢查，未重新轉換。
- Granta MI Connected Materials v261 新增 ModelExportResponse 子題，引用公開 `material-model-output.md` 與 `material-models.md`；輸出 JSON schema 的 Swagger 需登入 MI Service Layer，本機未能核實完整欄位與必填性。
- 增量更新索引中的三個 PDF sidecar alias（`ansys_1e57d29161584cb3b4fc5ea5`、`ansys_4f30b72e45d830cc458999ab`、`ansys_28193c1c7fa2d3030ba672d3`）與 Granta／README／本紀錄字典 alias；未重建全庫。三份 PDF sidecar 的內容查詢均成功 `get_chunk`；使用 `context=1` 時鄰近片段可見頁標題（SpaceClaim pages 6–8、Mechanical scripting page 346、Mechanical ACT pages 58–60）。直接片段不一定含頁標題；只查兩位數頁碼也不精確，因 trigram 搜尋會略過短於 3 字元的數字。Granta 字典 `ModelExportResponse implicitConstraints`、MMO 原文 `implicitConstraints default Parameter`、MMD 原文 `Hooke law Young modulus` 查詢均成功取回來源路徑與片段；字典的英文查詢 `implicitConstraints default Parameter` 未命中，改查 `numericValues isFreeParameter Temperature` 可命中相鄰 schema 摘要。
- SQLite `BEGIN IMMEDIATE`（timeout 0）可取得鎖後 rollback，`PRAGMA quick_check` 回傳 `ok`，`_needs_rebuild()` 為 `False`；psutil 當下未找到其他程序開啟 DB。這只能描述檢查時點，先前鎖定事件的來源仍無法確認。索引片段保留頁標題，但只用頁碼搜尋未必精確排序；搭配該頁技術詞搜尋較可靠。
- 未呼叫 GMMS API、未執行 Mechanical／SpaceClaim；HTML 原始頁、圖片與表格未逐頁人工核對。


### 2026-10-31 AEDT：PyAEDT CLI session/project/script/export

- 核對官方 PyAEDT CLI HTML 與本機 Markdown sidecar（source ID `ansys_43b46378037bb391538151b2`，`ansys-aedt-core 1.9.0`；URL 為 `version/stable`，AEDT release `unknown`）。HTML 原件保留；整理 version/session/project/script/export/panels/doc/test-config 命令入口、port 前置條件、IronPython 限制與匯出輸出方式。
- [AEDT 字典](aedt.md)將 `PyAEDT CLI` 主題標為 complete；特別標示 `session stop --all` 的全域影響、`panels add --reset` 會移除既有 `Toolkits` 目錄，以及 `test-config` 的互動流程。頁面 `pyaedt version` 輸出 `1.0.dev0` 僅作範例，不作安裝版本證據。未啟動 AEDT 或執行 CLI。
- 索引回查：AEDT 字典 alias `external_ee081753412b_aedt` 的 `project create port Hfss`、`pyaedt session start non-graphical`、`export config screenshot output`、`IronPython 原生 API` 均命中且成功 `get_chunk`；`IronPython native API` 未命中，因字典使用「原生 API」中文說明。原始 CLI source ID `ansys_43b46378037bb391538151b2` 的 `pyaedt project create DemoProject Filter1 Hfss`、`most recent stable AEDT version 50051`、`pyaedt session attach port 50051` 亦命中並成功取回 HTML 來源路徑及正文片段。未執行 AEDT CLI；此驗證只確認文件檢索。


### 2026-10-31 DPF v261／PyDPF-Core Model 載入與 metadata 檢查

- 核讀 DPF Mechanical v261 core-concepts 與 basic-load 頁，以及 PyDPF-Core `Model` 使用指南（SDK metadata 0.16.3；網址使用 `version/stable`，release unknown）。整理 Mechanical scripting window 的 `mech_dpf.setExtAPI`、`ResultFileName`、`DataSources`／`Model`、mesh／time metadata；另區分 Python Result callback 與 standalone CPython metadata API。
- [DPF 字典](dpf.md)補上有界操作子題，將 `結果載入與 Model 檢查` 標為 complete。範例 node／element/time 數只標記為文件案例；未載入結果檔或執行 Mechanical、DPF/operator。
- 索引回查：DPF 字典 alias `external_8e11a222f953_dpf` 查詢 `mech_dpf setExtAPI ResultFileName`、`TimeFreqSupport TimeFrequencies Nodes Count`、`model.metadata meshed_region time_frequencies.data` 均命中且成功 `get_chunk`。Mechanical v261 source IDs `ansys_5a4458b3ebbb6bc3338662db` 與 `ansys_6c82352acbeefbcf3245b85b` 的 `SetResultFilePath ExtAPI dpf.Model`、`TimeFrequencies GetData mesh Nodes Count`、`ResultFileName SetResultFilePath` 查詢亦回到正確原文；PyDPF-Core source ID `ansys_d3a4dc858e42fbe5087838db` 的 `model.metadata result_info analysis_type` 命中 HTML 來源並成功取片段。未呼叫 DPF operator 或讀取實際求解結果。


### 2026-10-31 PyAnsys Geometry 0.18.2 Plane、單位與 circle Sketch

- 核讀本機 `ansys-geometry-core 0.18.2` User guide、Primitives 與 Sketch sidecar；頁面 URL 使用 `version/stable`，Geometry service／產品 release 維持 `unknown`。整理預設 XY plane、自訂 plane origin/axes、`Point2D`／`Point3D`、`UNITS.m`、預設 length/angle units、`LENGTH_ACCURACY`／`ANGLE_ACCURACY` 及官方 circle Sketch quick-start。
- [Geometry 字典](geometry.md)完成 `Plane、primitive 與單位精度` 有界主題；明列精度常數不是工程驗收容差，circle sketch 範例不表示建立 3D solid。較廣的「基本建模流程」與 service/deployment topics 保持 draft。
- 索引回查：Geometry 字典 alias `external_23b183911d94_geometry` 查詢 `Point3D direction_x circle UNITS.m`、`LENGTH_ACCURACY`、`ANGLE_ACCURACY`、`DEFAULT_UNITS LENGTH meter` 均命中並成功 `get_chunk`。官方 User guide source ID `ansys_7dc4796b4a9f3e10f5131bdd` 的 `circle UNITS.m`／`Point3D Point2D`，以及 Primitives source ID `ansys_0a93940f6dbe08c7df369d65` 的 `LENGTH_ACCURACY`、`ANGLE_ACCURACY`、`DEFAULT_UNITS LENGTH`、`Plane XY origin` 查詢均回到相應 HTML 原文並成功取片段。組合查詢 `LENGTH_ACCURACY ANGLE_ACCURACY Plane` 未命中，拆成常數或 plane 查詢可定位。未啟動 Geometry service、未建立 CAD 模型。

### 2026-10-31 CFX PyCFX CCL state 與 physics updates

- 依官方 PyCFX sessions guide（source ID `ansys_c58523f59daaf38e134d31d7`；本機文件集合為 `ansys-cfx-core 0.3.0`，官方網址使用 `version/stable`；產品 release 維持 `unknown`）整理設定物件名稱、`get_state()`／`set_state()`／`print_state()`、有效子項與 `get_physics_messages()`。補述逐項 physics setting 變更可能連動相依值、更新只限 top-level objects 內相依項，以及 dictionary state 的截至 CFX 2026 R1 限制和 optional state 移除方式；沒有推定後續版本行為。
- `topics.csv` 的「CCL 設定樹與狀態更新」由 draft 更新為 complete；僅代表此文件範圍有來源支持，dictionary 限制仍按原文註記，未涵蓋完整 CFX 求解手冊。
- SQLite 文件搜尋：查詢 `CFX CCL state active children physics messages` 命中 CFX 字典；查詢官方 source alias `ansys_c58523f59daaf38e134d31d7` 的 `get_physics_messages physics updates set_state dictionary` 命中 session guide，並以 `get_chunk` 取回相符正文。索引完整性以 `PRAGMA quick_check` 驗證；未執行 CFX session 或求解。

### 2026-10-31 LS-DYNA 官方 Knowledge Base 分類與範例入口

- 逐頁核對官方 Knowledge Base landing page、General/Explicit、Implicit、Simple Examples 及 Beer Can、Pendulum、Pipe on Pipe、Taylor Bar 共八頁。整理入口分類與搜尋、Explicit Technical Guide 用途、Implicit Guideline 頁面所列 2026 R1 與更新說明、Simple Examples 作者／案例索引，以及四個案例的模型概要。
- [LS-DYNA 字典](lsdyna.md)補全「官方 Knowledge Base 與外部範例」主題；範圍是入口導覽與案例摘要，不涵蓋完整指南正文、solver 理論或版本相容性。`topics.csv` 共 370 項不變，LS-DYNA 該主題由 draft 改為 complete。
- 原始頁面透過官方網站瀏覽器文字檢視；本機 DNS 仍無法解析網站，故 `sources.csv` 保持 `browser_summary_only`，不聲稱原始 HTML 已下載或入索引。未執行 LS-DYNA solver。SQLite 字典限定查詢 `Soil-Structure Interaction CESE Meshfree` 與 `Taylor Bar` 均命中字典並成功取回片段。較長組合查詢 `Taylor Bar quarter model rigid wall ALE` 未命中；來源正文沒有快取，不能藉此查詢回到原始網頁。`PRAGMA quick_check` 為 `ok`，索引不需重建。


### 2026-10-31 Mechanical v261 sizing API 與 v252 mesh quality 檢查

- 核讀本機 v261 Mechanical Scripting Guide／Mesh API／MeshSizingType／MeshMetricType，以及官方 v252 Error and Warning Limits 與 Check Mesh Quality 頁。字典整理 sizing 預設與呼叫順序、metric query、Check Mesh Quality 四種模式、Worksheet 表格／色彩／CSV 操作、Mesh Workflow Error Check 限制，以及 Standard／Aggressive／Nonlinear Mechanical 等 Physics Preference 限值角色。
- [Mechanical 字典](mechanical.md)完成「網格與品質」主題，範圍明確分開 v261 API 與 v252 GUI，未推定兩版 GUI 限值一致；未涵蓋 metric 數學定義或完整網格理論。`topics.csv` 共 370 項不變，Mechanical draft 從 4 項降至 3 項。
- 官方 v252 HTML 保持 `browser_summary_only`，未鏡像成本機正文；本機 v261 PDF／API 來源仍可回到文件位置。SQLite 將增量更新字典與清冊後，查詢 mesh quality 限值及 Worksheet 模式並以 `get_chunk` 回查，執行 `PRAGMA quick_check`。未執行 Mechanical 或網格產生。


### 2026-10-31 optiSLang v252 MOP Solver standalone workflow

- 核讀 v252 External Metamodel Solver Interfaces 官方 Markdown sidecar（source ID `ansys_f00902829fafb63ac19c5a83`，release v252，正文已索引）。整理 Windows／Linux executable 位置、`--init` 初始化、必填 input/output 檔、工作目錄輸出、bounds 預設錯誤及 `--extended` 外插界線。
- [optiSLang 字典](optislang.md)新增有界完整主題 `v252 MOP Solver standalone input/output workflow`；它與 PyOptiSLang、產品內建 Python API 分開，不含 MOP 數值驗證或外插品質保證。主題列增至 371。
- SQLite 搜尋字典 alias `external_dafea9911697_optislang` 的 `mopsolver extended`，以及來源 alias `ansys_f00902829fafb63ac19c5a83` 的 `mopsolver input output extended` 均命中，並成功以 `get_chunk` 取回正文；`PRAGMA quick_check` 為 `ok`，索引不需重建。不執行 MOP Solver。


### 2026-10-31 DPF v261 Server 與 client 使用方式

- 核讀 Ansys DPF v261 Ways of Using 與 PyDPF-Core Model 官方 sidecar（SDK metadata 0.16.3；release unknown）。依來源整理 server kernel/operator libraries、CPython／IronPython／C++ client、same-process／gRPC、Mechanical／standalone 選擇及遠端檔案路徑由 server 端解析等資訊。
- [DPF 字典](dpf.md)的「Server 與 client 使用方式」由 draft 更新為 complete；限定為 architecture／API 使用方式摘要，不代表跨版本相容矩陣。`topics.csv` 共 371 項不變，DPF draft 由 4 項降至 3 項。
- SQLite 字典 alias `external_8e11a222f953_dpf` 查詢 `IronPython CPython gRPC` 命中並成功 `get_chunk`；初始跨段組合查詢 `DataProcessingCore gRPC server-side path` 未命中。v261 source alias `ansys_9f58489e0c3241493d0d41b1` 查詢 `CPython IronPython gRPC`、PyDPF-Core source alias `ansys_d3a4dc858e42fbe5087838db` 查詢 `absolute path relative DPF server` 均命中並成功取回片段。`PRAGMA quick_check` 驗證索引完整；未啟動 DPF Server、未載入結果檔或執行 operator。


## Fluent HTML 頁面版本標記核對（2026-11-01）

- 核對 `ansys-fluent-core/0.42.1` 快取路徑內 433 個含版本標記的 HTML：389 頁內嵌 `docsearch:version=0.43.0`，44 頁為 `0.40.3`；目錄名稱不能代表各頁實際標記。
- 本字典引用的六頁中，Launching、Sessions、Meshing、Solver settings、Field/SVAR comparison 五頁標示 0.40.3；Solution variable data 詳頁標示 0.43.0。`sources.csv` 仍保留 release=unknown，並明示來源清冊 SDK 欄位／快取路徑與 HTML 標記的差異。
- 完成 Field Data 與 Solution Variable Data API 選擇主題的頁面範圍整理；Solution variable metadata／read-write 主題依 0.43.0 詳頁與 0.40.3 比較頁限定範圍。未宣稱跨版相容性，未在 Fluent session 執行 API。
- SQLite 索引檔於 2026-11-01 成功取得 `BEGIN IMMEDIATE` 寫入鎖後立即 rollback；檢查時沒有其他 writer 持鎖。


## 來源清冊復原與 Fluent 頁面版本核對（2026-11-01）

- 清冊編輯意外覆寫 `sources.csv` 後，已由 596,702 筆 catalog 與主題引用重建本機來源列；由 catalog／主題引用復原的本機來源列原有 5,338 筆；再從字典內直接連結與 `markdown_links.csv` 對應路徑補回 51 筆 catalog 來源，並有 69 筆主題所引非 catalog ID、47 筆未下載／受限／失敗外部網址。當前清冊共 5505 筆。非 catalog 項的原 URL／人工狀態無法由現存 catalog 還原，明確標為 `online_source_metadata_missing`。
- Fluent 六個官方 HTML：Launching、Sessions、Meshing、Solver settings、Field/SVAR comparison 頁內嵌版本為 0.40.3；Solution variable data 詳頁為 0.43.0。這些頁的來源清冊 SDK 欄位／快取路徑標 0.42.1，不能當作頁面版本或跨版相容證據。
- 完成 Fluent Field Data 與 Solution Variable Data API 選擇的有限範圍整理；沒有在 Fluent session 執行 API。


## optiSLang Sensitivity system 官方頁面摘要（2026-11-01）

- 核讀 Ansys 官方 v251／v252 optiSLang User’s Guide Sensitivity 頁與 v252 Methods for Parametric Design Optimization 的 random/quasi-random DoE schemes 頁。`sources.csv` 新增三筆 `browser_summary_only` URL 來源；正文 HTML 未鏡像、未納入全文索引。
- 新增 `Sensitivity system 抽樣控制與結果（v251／v252）` 有界 complete 主題；涵蓋參數資格、抽樣選項、LHS／Monte Carlo 行為、dynamic sampling、樣本數／levels 與 CoP／MOP 敏感度處理。v251 Additional Options 保留版本標籤；未外推至 v261 GUI 或 PyOptiSLang 1.7.0 runner。
- `DOE 與敏感度` 總體主題仍為 draft，因完整統計理論、缺失的 `sensitivity_settings.py` 和產品版本差異仍未核實；沒有執行 optiSLang。


optiSLang 字典代表查詢：`Dynamic sampling start designs` 與 `Advanced Latin Hypercube samples` 在 `external_dafea9911697_optislang` 命中並成功 `get_chunk`；較長查詢 `Dynamic sampling Number of samples Latin Hypercube Coefficient Prognosis` 未命中，因全文檢索採 AND 條件，拆成主題詞後命中。索引 `_needs_rebuild=False`。


## Motion CAR Toolkit Template 與 Assembly 更新（2026-11-01）

- 核讀本機 Ansys Motion 2026 R1 Car Manual PDF sidecar physical pages 28–31、87，分辨 Template 定義 Subsystem 結構、既有資料可調項目、minor role 與 Assembly 更新流程。來源清冊 release 維持 unknown。
- `Template、Subsystem 與 Assembly 更新` 由 draft 更新為有界 complete；明列不可在 Subsystem 新增／刪除元素，以及 Template 更新需先關閉引用它的 Assembly／Subsystem、儲存 Template、再重開檢查。未推定跨版本行為，未執行 Motion GUI。
- 主題總數仍為 372；Motion draft 由 4 項降為 3 項。
- Motion 字典代表查詢 `Assembly Template`、`Assembly Subsystem` 命中並成功 `get_chunk`；較長查詢 `close Assembly Subsystem updated Template` 未命中，因「關閉／重開」在字典以中文敘述。索引 `_needs_rebuild=False`。


## 2026-11-01 四產品 PDF／HTML 轉換核對

使用既有 `sync_ansys_documents.py` PDFium 擷取流程處理 SpaceClaim、Mechanical、LS-DYNA、optiSLang 四個來源目錄內現存的 15 份 PDF；15/15 成功，頁面文字快取均含 `<!-- page N -->` 標記，來源 PDF SHA-256 與抽取清冊相符。1 筆已移除的 SpaceClaim V232 開發手冊仍按既有清冊標為 `deduplicated`，未重複擷取。15 份同名 Markdown 都與新抽取文字不同，因此原檔全部保留；PDF 抽取清冊指向 `_catalog/pdf_text_v2/` 頁碼版快取。`_catalog/documents.json` 中 13 份文件改用這批快取；兩份 LS-OPT 文件沿用原本已使用的 `_catalog/pdf_text_v4/` 正文，並依清冊規則歸為 `general`，不混入 optiSLang 產品索引。

四產品目錄現有 1,060 個 HTML：Mechanical 236、LS-DYNA 247、optiSLang 577、SpaceClaim 0；每個 HTML 都有非空同名 Markdown。HTML 轉換明細含其中 968 筆（Mechanical 144、LS-DYNA 247、optiSLang 577），輸出雜湊均相符；另有 92 筆 Mechanical HTML／Markdown 配對是既有輸出但未列在轉換明細。本次保留這些配對，未重寫 HTML 或 Markdown。

原始 PDF／HTML 均未覆寫，未執行 OCR。頁碼文字抽取不保證保留圖表語意、圖片內文字或完整表格結構；92 筆既有 Mechanical HTML 輸出的轉換來源與逐筆雜湊仍待補入 HTML 明細。完整 SQLite 重建在逐筆核對大型來源清冊階段耗時過長而停止；現有 SQLite 檔未被替換，但 `documents.json` 與索引記錄的清冊指紋不同，全文檢索索引待重建。


## 2026-11-01 CFX PyCFX 安裝主題

新增有界主題「PyCFX 0.3.0 安裝前提與本機版本定位」：依官方 Installation／Launch 指南整理 Python 與 CFX 支援版本、`AWP_ROOT<version>` 環境變數、`product_version` 選擇及初版 local-machine 限制；廣義疑難排查仍維持 draft。來源為 `ansys_cdad416d6d922df3911d2bd8` 與 `ansys_a4a0afff47aac7962b2138aa`，產品 release 未知，未實機安裝或啟動。PDF／HTML 導入後的全文 SQLite 索引仍待重建；本輪未呼叫會觸發完整重建的搜尋介面。


## 2026-11-01 PyAnsys Geometry 入門建模主題

將 `基本建模流程` 主題依 SDK metadata 0.18.2 User guide、Sketches 與 Primitives 原文收斂為有界範圍並標記 complete：涵蓋 Plane、2D Sketch、functional-style／direct API、tag 取回及 primitive 表示；3D solid、全套特徵、幾何修復與 CAD 匯出仍未涵蓋。沒有啟動 Geometry service 或執行 CAD 操作。全文索引仍待清冊同步後重建。


## 2026-11-01 PyAnsys Sound 主題狀態核對

將 `PyAnsys Sound SDK 與產品版本` 與 `STFT／ISTFT 與 spectrogram` 兩項依已存在的 SDK 0.4.0 User guide、gallery metadata 及 STFT tutorial 摘要標為 complete：前者只確認 SDK 版本並保留產品 release unknown；後者只涵蓋官方 flute 案例資料流與參數展示，不包含通用聲學判準或重建誤差驗證。Sound 的聲學判讀與待補範圍仍為 draft。沒有執行音訊或 DPF server。全文索引仍待整批重建。


## 2026-11-01 Granta MI 主題核對

依 Scripting Toolkit 5.0 Session API 補明 `get_db()` 四種識別條件、唯一匹配要求、`KeyError` 情況，以及 `refetch_dbs()`／跨 table 搜尋的 Service Layer 呼叫範圍；將 Session／資料庫存取主題標為 complete。RecordLists 搜尋主題已有 SDK 2.1.1 官方範例摘要，狀態由 draft 更新為 complete。資料庫租戶、名稱／識別值與實際查詢結果未驗證；來源產品 release 維持 unknown。全文索引仍待整批重建。


## 2026-11-01 ModelCenter ScriptWrapper 主題

依 v261／2026 R1 ScriptWrapper introduction 與 `ParseableFile` Java API 整理 ScriptWrapper 語言族、nD arrays、File Parsing 的 BeanShell 限制、template 預設行為及 `backup()`／`delete()`／`close()` 副作用；將該有界主題標為 complete，並把 `ParseableFile` 正文加入 `sources.csv`，索引狀態標為待重建。特別記錄 `backup()` 會先刪除同名既有 `.bac` 檔；沒有執行檔案操作或 ModelCenter runtime。全文索引仍待整批重建。


## 2026-11-01 Lumerical MATLAB 互通入口

新增官方 overview 範圍的 complete 子題，整理 Script Integration、MATLAB API、MAT 檔讀寫與 line／surface plot 匯出四種互通入口。較廣 `MATLAB automation` 主題仍為 draft，因設定指南只有外連、未鏡像；產品 release 未知，沒有啟動 Lumerical 或 MATLAB。


## 2026-11-01 Sherlock Analysis.run_analysis 主題

依 `ansys-sherlock-core 2.1.4` Analysis API 原文整理 project／CCA／analysis type／phase-event 輸入結構、`NaturalFreq` 範例、整數回傳碼與 `0` 成功定義，並保留其他狀態碼及結果讀取方式未說明的缺口。該 API 有界主題由 draft 更新為 complete；未啟動 Sherlock 或執行分析。全文索引仍待整批重建。

## 2026-11-01 DPF Operators 與 workflow

核對 PyDPF-Core Operators `version/stable` 本機 sidecar 與 Ansys DPF v261 Ways of Using，將 `Operators 與 workflow` 標為 complete。字典範圍涵蓋 operator descriptor／必要輸入、lazy evaluation、串接、`min_max.field_max()` server-side reduction 與 operator license 界線；`version/stable` 頁未標精確 SDK release，來源清冊記錄的 0.16.3 是本機快取 metadata。更新後 DPF 9 個主題為 2 draft、7 complete，總主題數仍為 374。未執行 DPF operator、Mechanical 或求解；索引資料庫為 `docs/Documentation_clean/docs_index.sqlite`（3,305,467,904 bytes）；唯讀連線成功，`sqlite_master` 有 11 筆項目，無 `-journal`／`-wal`／`-shm` 側檔，`BEGIN IMMEDIATE`（timeout 0）成功取得後立即 rollback，psutil 未找到開啟此資料庫的程序；`index._needs_rebuild()` 仍為 `True`。本輪未跑全庫 `quick_check`，未呼叫搜尋或重建。

## 2026-11-01 PyFluent Solver settings 與 exposure levels

依本機 `Solver settings objects` 與 `Using PyFluent sessions` HTML／Markdown sidecar，補齊 constructor-style 與傳統 settings 階層、`ExposureLevel.STABLE/BETA/ALPHA` 可見項目、settings root 限定、session-local 行為及兩種 `AttributeError` 邊界，並將主題標為 complete。兩頁 HTML 內嵌版本均為 0.40.3；來源清冊與快取路徑標示 0.42.1，官方 URL 使用 `version/stable`，故未宣稱跨版相容。Fluent 共 8 項主題，更新後 2 draft、6 complete；總主題數仍為 374。未啟動 Fluent 或執行 solver。SQLite 索引仍 `needs_rebuild=True`；本輪未呼叫搜尋或索引重建。

## 2026-11-01 PyTwin 單次與批次時間步模擬 API

對照 PyTwin 0.13.0 `twin_simulate`、`twin_simulate_batch_mode` 與 `twin_simulate_batch_mode_csv` 官方 API sidecar，補齊單次 stepping 與 batch 輸出點的步長語意、DataFrame 輸出欄名／index、CSV 欄位／header／空輸出路徑，以及 `interpolate` 僅適用非零步長連續實數變數的限制。三項主題均標 complete；`Twin 與 TBROM 範例` 仍為 draft。PyTwin 五項主題更新後 1 draft、4 complete；全庫主題數仍為 374。官方 URL 使用 `version/stable`，產品 release unknown，未執行 PyTwin 模擬。全文 SQLite 索引仍待重建，本輪未呼叫搜尋或重建。

## 2026-11-01 PyCFX Blade Flutter 教學與後處理

對照本機 PyCFX 0.3.0 Static Mixer 與 Fourier Transformation Blade Flutter tutorial sidecar，補足單 passage 網格以 CCL 轉成 two-passage、初始條件→time integration→harmonic balance 三階段，以及 Total Wall Work contour／動畫後處理流程；記錄 `CFXVersion > v252` 的 monitor object path 分支及教學明示 PyCFX 2025 R2 不支援 animation。將「教學案例與後處理入口」由 draft 改為 complete；CFX 10 項主題現為 1 draft、8 complete、1 source_limited。案例設定不作通用設計條件或物理驗證，產品 release unknown，未執行 solver。總主題數仍為 374；SQLite 索引待重建，本輪未呼叫搜尋。

## 2026-11-01 Granta MI 開發套件與版本邊界

依 Developer Portal overview、Scripting Toolkit 5.0 Session API、Connected Materials 2026 R1 SP01 getting-started／authentication，以及 PyGranta RecordLists Connection API SDK metadata 2.1.1，新增路徑比較表：分列 SOAP Service Layer、Integration Service REST API、RecordLists client 的用途、文件標籤、平台說明與認證邊界。來源均保留各自正式網址及本機 sidecar；Granta MI server/product release 與完整 client-server 相容矩陣仍未知。`來源產品與版本界線` 由 draft 改為 complete；Granta MI 11 項主題現為 3 draft、8 complete。總主題數仍為 374，未連線服務或執行 API；SQLite 索引待重建，本輪未呼叫搜尋。

## 2026-11-01 OpenTD Case Set 與 SINDA/FLUINT 執行入口

依 OpenTD 2026 R1 Working with case sets、Communicating with SINDA/FLUINT 與 `OpenTD.CoSolver` namespace reference，補上單一 transient case 的設定／`Update()`／`Run()` 順序、symbol override、CaseSetManager 批次索引語意、工作目錄與 radiation task 入口，並區分 `SF_Launcher`、`SF_CoSolver`、`TDSF_CoSolver` 職責。該有界主題由 draft 更新為 complete；Thermal Desktop 七項主題現為 4 draft、3 complete。範例參數不作設計建議，未執行 Thermal Desktop、SINDA/FLUINT 或求解；全庫總主題數 374，SQLite 索引待重建，本輪未呼叫搜尋。

## 2026-11-01 PyScadeOne FMI 2.0 FMU 匯出

依本機 PyScadeOne 0.8 Export FMU tutorial sidecar，整理 IDE `CodeGen` job 前置、`FMU_2_Export` 初始化、`is_code_generated` 檢查、FMI 2.0 Model Exchange／Co-Simulation 生成與 build、GCC／`gcc_path`、tutorial 專用 `swan_config_end` include 及 CLI 入口。將 FMU 匯出主題由 draft 更新為 complete，範圍明確限定 QuadFlightControl 範例；產品 release unknown，未執行 code generation、compiler、FMU build 或 importer 驗證。PyScadeOne 5 項主題現為 4 draft、1 complete；總主題數 374，SQLite 索引待重建，未呼叫搜尋。

## 2026-11-01 Rigid Body Dynamics Joint feedback 範例

依 v261 `Joint condition: control using linear feedback` 與 Rigid Dynamics object model sidecar，整理以 `CS_Joint.Find(...).GetVelocity()` 取得 measure、方法一將 measure 接到既有 `CS_Actuator` load，以及方法二建立 `CS_JointDOFLoad` 並加入 Environment 的兩條路徑。補充 `_jid`／`_jcid` 佔位 ID、`FindFirstNonNull()` 適用邊界、方法二沿用前段變數、`ids[0]` 須核對及函數／DOF 值不可泛化等 caveats。該有界主題由 draft 改為 complete；RBD 五項主題現為 4 draft、1 complete。未在 Mechanical 執行命令或驗證控制響應；全庫主題數 374，SQLite 索引待重建，未呼叫搜尋。

## 2026-11-01 Icepak v261 入門分析與 monitors

對照 Ansys Electromagnetics Suite 2026 R1 `Icepak Getting Started Guide` 的 Graphics Card 教學及獨立 Heat Pipe Model tutorial，補上材料／邊界、global 與 regional mesh、Validation Check、thermal／flow monitors、residual review、solve 與後處理案例導讀及 PDF 頁面定位。明確區分 Graphics Card 的 global mesh→heatsink 附近 refinement 流程，及 Heat Pipe 的 gradient-targeted mesh regions；案例數值不作通用工程條件。`Icepak 初始模擬流程與監視器` 由 draft 改為 complete；Icepak 六項主題現為 3 draft、3 complete。總主題數 374；未啟動 AEDT／Icepak、未生成 mesh 或求解，SQLite 索引待重建、本輪未呼叫搜尋。

## 2026-11-01 Motion 雙 A 臂 Pre/Post Processor tutorial

依本機 `Ansys Motion 2026 R1 Pre and Post Processor Tutorial` sidecar PDF physical pages 3–38、60–63，補上素材解壓、standard EMBD／單位／重力／對稱、CAD 匯入、設計變數／接點、雙側懸吊 joint／force 建模、rack steering solve，以及 `Steering_DF.dfr` 匯入、動畫與 `Tire_left` Z displacement 曲線步驟。將該有界主題改為 complete；PDF 封面標 2026 R1、來源清冊 release unknown，案例資料不作通用懸吊規格。並將 Motion topics 中 CAR Toolkit、Pre/Post Tutorial、C# API 三筆 source_refs 分別收斂到字典各節直接引用來源，清除原先複製的無關來源引用。Motion 六項主題現為 2 draft、4 complete；總主題數仍為 374。未執行 Motion GUI／分析，SQLite 索引待重建、未呼叫搜尋。

## 2026-11-01 ModelCenter COM 與 Java API 文件入口

依 ModelCenter APIs 2026 R1 COM API 與 Java API index sidecar，整理 COM API 的自動化／外部整合／語言範圍，以及 Java API index 所列四個 package。兩頁來源清冊 release 為 v261，最後更新日期均為 2026-06-18；確認只由入口頁作導覽摘要，不推定 feature parity、跨 API 型別相容或部署相容。`COM 與 Java API` 主題由 draft 改為 complete；ModelCenter 七項主題現為 3 draft、4 complete。未啟動 ModelCenter 或呼叫 API；總主題數仍為 374，SQLite 索引待重建、本輪未呼叫搜尋。

## 2026-11-01 Q3D Scripting environments

依 v261／2026 R1 `Q3D Extractor Scripting Guide` PDF Pages 56–59、96–99，整理桌面內 IronPython 的四種入口與 `ScriptArgument`、Standalone IronPython 的 COM 限制、CPython `ScriptEnv`／gRPC 啟動連線方式及手冊列出的 50051 埠選擇規則；並標出舊 VBScript／JavaScript 資產透過 Python 重用時無法取回其呼叫回傳值。`Scripting environments` 由 draft 改為 complete；Q3D 三個主題現均為 complete，主題總數仍為 374。未啟動 AEDT/Q3D、未執行 COM／gRPC 連線，SQLite 索引待重建、本輪未呼叫搜尋。

## 2026-11-01 Motion C# API 擴充

依本機 `Ansys Motion 2026 R1 API Tutorial` sidecar PDF physical pages 3–18，整理外部 Motion/API module DLL 執行方式，以及繼承 `OperationBase`、覆寫 `Execute()`／`Name`、建立 Ribbon resource／`.dfrbbx`、以 `.dfmdx` 註冊 operation command 的教學流程；另記錄範例的 Visual C# 2012、.NET Framework 4.0、module reference、`Copy Local=False` 與 `VMLNet.dll` 授權設定。PDF 標題含 2026 R1，來源清冊 release unknown；把 `Motion C# API 擴充` 改為 bounded complete，不推定其他版本／toolkit 相容。Motion 六個主題現為 1 draft、5 complete；總主題數仍為 374。未編譯 DLL、未啟動 Motion 或驗證授權；SQLite 索引待重建、本輪未呼叫搜尋。

## 2026-11-01 PyTwin Twin／TBROM 範例

依本機 PyTwin 0.13.0 Examples index 與三份 HTML 教學，整理 PyAEDT static ROM→TWIN export→PyTwin evaluation（需 Twin Builder 2025 R1+）、Coupled Clutches CSV step-by-step／batch 比較，以及 Electric Range Twin 的 mass／power load 參數掃描與 WLTP class 3 案例範圍。index 對其他 TBROM／deployment 範例僅能支持分類與標題導覽，詳細 workflow 尚未逐頁整理；`Twin 與 TBROM 範例` 主題 bounded complete，PyTwin 五項主題均 complete，總數仍 374。來源網站為 `version/stable`、本機 SDK 路徑 0.13.0、產品 release unknown；未執行範例／PyTwin/Twin Builder，SQLite 索引待重建、本輪未呼叫搜尋。

## 2026-11-01 Fluent solution variable metadata 與讀取

核對 PyFluent `Solution variable data` 及 `Choosing between field data and solution variable data APIs` 兩份官方 HTML，補確認 `get_zones_info()`、`get_variables_info()` 的 zone／SVAR metadata 入口，`get_data()`／`set_data()` 的 zone array 用法，以及 field_data 的 surface-centric、read-only 特性和 SVAR API 的 read/write 邊界。並保留示例的輸入 zone 順序與回傳 `zone_names` 順序不同，需以 zone name 取對應陣列；寫入示例值不是物理建議。主題由 draft 改為 complete；Fluent 八項主題現為 1 draft、7 complete。來源頁面內嵌版本分別為 0.43.0 與 0.40.3，catalog／快取路徑為 0.42.1；未在 Fluent session 讀寫資料，SQLite 索引待重建、本輪未呼叫搜尋。

## 2026-11-01 LS-DYNA Keyword 與模型控制（R16 範圍）

重新核對本機 R16 Vol. I PDF sidecar physical page 1867–1868 的 `*CONTROL_TERMINATION` 欄位／備註，以及 R16 Vol. II pages 71–75 的 MAT 索引、元素形式、history-variable 計數與 `8B` 警語；對照字典中已限定 R16 的 termination、材料索引及 `*MAT_024` 範例。手冊內頁標示 `R16@431ab7b9b`、日期 2025-10-29，catalog release 欄仍為 unknown；此主題只完成 R16 來源範圍，不聲稱跨版本相容或材料選擇建議。`Keyword 與模型控制` 由 draft 改為 complete；LS-DYNA draft 減為 2，總主題數仍為 374。未執行 solver／模型，SQLite 索引待重建、本輪未呼叫搜尋。

## 2026-11-01 Mechanical v261 接觸官方 HTML 來源恢復

使用官方 Mechanical User’s Guide `v261` 頁面核讀 Contact Region、Contact／Target sides、Contact Workflow、Advanced Contact Settings、Investigating Contact Regions、Troubleshooting Convergence Problems；頁尾標示 Release 2026 R1。依精確官方 URL 恢復 `sources.csv` 中 6 筆網頁來源的 title、URL 與 v261 標記，品質設為 `official_page_reviewed_summary_only`，狀態註明原始 HTML 未鏡像、本機索引未含全文。字典已有繁中 workflow 與診斷摘要；`接觸與邊界條件` 仍維持 draft，因 formulation 適用條件及 solver-specific 行為尚未完整核對。未執行 Mechanical 或求解；總主題數仍為 374，SQLite 索引待重建、本輪未呼叫搜尋。

## 2026-11-01 PyOptiSLang Sensitivity settings 來源授權與版本核對

確認 PyOptiSLang 1.7.0 HTML runner 只透過 `examples.get_files("sensitivity_settings")` 執行套件內另一份檔案，runner 本身未含 settings。唯讀檢查本機 Python 環境的 `ansys-optislang-core 1.5.0`，找到同名範例；該檔含 MIT 套件授權文字，同時又有未經授權不得使用／散布／複製的樣例聲明，且版本不是 1.7.0。故不複製該檔、不將其設定值寫入字典，並修正 `DOE 與敏感度` 中「1.7.0 settings 原文未鏡像」的缺口說明；主題仍為 draft。未執行範例或 optiSLang；SQLite 索引待重建、本輪未呼叫搜尋。

## 2026-11-01 PyDYNA `option_card` API 導覽

依本機 PyDYNA `option_card` module index 補上 `OptionSpec`、`OptionCardSet`、`OptionsInterface`、`OptionAPI`、`Options` 的類別角色摘要；來源頁只有 module index，未描述 member-level 行為或 solver serialization。`PyDYNA` 主題仍為 draft，因整體 SDK API 覆蓋與版本驗證未完成；本機路徑為 `ansys-dyna-core/0.12.1`、官方 URL 使用 `version/stable`，不據此推定 LS-DYNA solver release。未執行 PyDYNA／solver；總主題數仍為 374，SQLite 索引待重建、本輪未呼叫搜尋。

## 2026-11-01 Thermal Desktop OpenTD.Results 與後處理

依 OpenTD 2026 R1 `Reading results` 指南及同版 changelog，補上 Dataset 來源種類、DataArray dimension／units／NaN 語意、DerivedDataset／DerivedDataArray、Comparer 的比較方式與指南預設 1% percent tolerance（不作工程驗收建議），以及 XY plot 特性，並整理 `ThermalDesktop.DatasetManager` 建立資料集及依 `CurrentTimeIndex` 顯示 contour plot 的指南流程。保留原文 `ForumlaDataArray` 拼字待 Class Reference 核對；另標示範例中的 `Directory.Delete(workingDir, true)` 會遞迴刪除既有目錄。將 Results 與後處理主題標為有界 complete，限定該 Getting Started 指南範圍；Thermal Desktop 七項主題現為 3 draft、4 complete。未執行 OpenTD API、未開啟結果檔或 Thermal Desktop，未重建 SQLite 或實測搜尋；原始 PDF／HTML 未修改。

## 2026-11-01 DPF data model 與 Field／Scoping

依 Ansys DPF v261 `What is DPF` 概覽及本機 PyDPF-Core SDK metadata 0.16.3 的 `Fields containers and fields`、`DPF model` sidecar，整理離散網格結果的適用範圍、Field／location／Scoping／FieldsContainer／Model 關係、label／time ID 選取差異，以及 CAD 幾何不屬於該頁所述資料模型的界線。將「資料模型與適用範圍」由 draft 改為有界 complete，並把 Model source 加入主題引用；PyDPF-Core 網址為 `version/stable`，頁面精確 release 仍 unknown，格式支援不推定為完整清單。DPF 九項主題現為 1 draft、8 complete。相關 HTML 原件與 Markdown sidecar 已存在，未重轉或覆寫；未執行 DPF／operator、未重建 SQLite 或實測搜尋。

## 2026-11-01 PyFluent session 啟動與生命週期

核對 PyFluent `Launching and connecting to Fluent` 與 `Using PyFluent sessions` 原始 HTML 的 `docsearch:version=0.40.3`，並確認各自 Markdown sidecar 存在；清冊 SDK cache path 為 0.42.1，官方網址使用 `version/stable`，產品 Fluent release 不由此推定。補上 `from_install`／`from_container`／`from_pim`／`from_connection` launch／attach 選擇、solver／meshing／pre-post mode、precision／dimension／parallel 參數、`using(session)` thread-local scope、Meshing mode transition／mesh transfer 與 launch／attach 的 exit 清理差異。將此 bounded topic 標為 complete；不宣稱涵蓋各 OS 遠端拓樸與排程器完整腳本。PyFluent 字典八個主題現為 complete。未啟動 Fluent／容器／scheduler，未執行範例、未重轉 HTML、未重建 SQLite 或實測搜尋。

## 2026-11-01 LS-PrePost History 資料與曲線解析度

依 Ansys LS-PrePost User’s Guide v261 PDF physical pages 670–672（printed pages 641–643）及逐頁 Markdown，整理 History 可用資料類型、分量／元素設定、XY Plot 的 popup／current／new／add 動作，並核對 `d3plot` history resolution 受 state 數量限制及手冊列出的高解析度替代資料 `d3thdt`、`binout`、ASCII。新增有界 complete 主題 `v261 LS-PrePost history data selection and resolution`；LS-PrePost 父主題仍為 draft，完整 GUI／Python API 尚未逐章核對。此 PDF 已有逐頁 Markdown sidecar；未重抽 PDF、未啟動 LS-PrePost 或載入結果，未重建 SQLite／搜尋索引。

## 2026-11-01 PySpeos Linux Docker service 部署

核對 PySpeos Getting started、Docker containers 與 Linux Docker container 三份 HTML 原件；頁面 `docsearch:version` 均為 0.9.2，Markdown sidecar 均存在。補上 Linux Docker service 的 Ansys organization／GHCR 取用前提、必填 license server 與選用 log level、localhost:50098 port 對應，以及 Mutual TLS、UDS、Windows WNUA、insecure transport 的 server／client 配對條件。特別標記原文稱示例 service 2025.2、命令 image tag 卻為 `261` 並另提 tag `252` 的版本文字矛盾；不據此映射 Speos product release。將 `Speos service 部署選項` 限定為該組 PySpeos 0.9.2 文件範圍並標為 complete；未複製 PAT 憑證操作範例。未登入 GHCR、啟動 Docker／Speos 或測試 transport；未重轉 HTML、未重建 SQLite／搜尋索引。

## 2026-11-01 ModelCenter Remote Execution Java API setup

核對 ModelCenter Remote Execution Java API 2026 R1 `Getting started`、`Overview Summary`、`AnalysisServerClient` reference 與既有 Introduction sidecar；前三頁最後更新日期為 2026-06-22，目錄路徑為 v261。確認三頁本機 Markdown 存在；docs_index.sqlite 的 `docs_meta` 有來源 metadata，FTS 查詢可命中正文，但 metadata 的 `ansys_...` ID 與片段使用的 `catalog_...` ID 不同，不能據此宣稱可用來源 ID 直接取回片段。將已核實的 metadata document IDs 補入 `sources.csv`。整理 JDK／MCRE 授權及網路前置、JAR classpath、embedded／remote URI／credentials 連線選擇、連線狀態查詢，以及 `close()` 與會結束 MCRE 的 `quit(...)` 差異；新增有界 complete 子題，父級 Remote Execution Java API 仍保留 draft，因完整 classes／methods 未整理。ModelCenter 八項主題現為 3 draft、5 complete；全庫主題數 376。未安裝 MCRE、編譯或執行 Java／analysis，未重建 SQLite。


## 2026-11-01 PyMotorCAD Windows 本機啟動前置

核對 PyMotorCAD Getting Started 與 Standard installation HTML 原文及既有 Markdown sidecar；HTML `docsearch:version` 為 0.8.8，兩頁路徑均指向 stable，catalog 產品 release 保持 unknown。整理授權版 Motor-CAD v2023 R1+、本機 Ansys license server、Windows Python 3.9–3.14、內建 Scripting tab 與外部 Python 套件使用邊界，以及 `MotorCAD()` 啟動本機 instance 的文件示例。將「PyMotorCAD SDK、產品版本及安裝條件」維持 draft（其中發佈渠道文字不一致），另新增僅限 Windows 本機啟動前置的 bounded complete 子題。來源 HTML 正文可在既有 SQLite FTS 以 `MotorCAD`／`v2023R1` 命中，命中的 chunk 使用 `catalog_...` ID；本輪新增字典摘要未加入索引。未安裝套件、設定授權或啟動 Motor-CAD；未重新轉換 HTML、未重建 SQLite／搜尋索引，也未驗證 `get_ansys_doc_chunk` 對該 chunk 的取回。


## 2026-11-01 PyDynamicReporting 本機 Service 生命週期

核對 `00-launch-reporting-service`、`01-create_db` HTML 原文及既有 Markdown sidecar；HTML 的 `docsearch:version` 為 0.10，本機 cache path 為 0.10.6，catalog release 維持 unknown。整理本機 Ansys installation 前提、空資料夾建新資料庫、`Service.start(create_db=True)`、`stop()` 與資料庫停止後保留的語意；新增限於此 local service lifecycle 的 bounded complete 子題，父級服務／資料庫主題仍為 draft。未執行 PyDynamicReporting、未建立資料庫或啟動服務；未重轉 HTML、未重建 SQLite／搜尋索引。


## 2026-11-01 optiSLang v252 space-filling LHS 與 Sobol

核讀官方 Random and quasi-random DoE schemes 頁面；URL 路徑標示 v252，頁尾標示 Release 2025 R2。補整理 space-filling designs、LHS maximin／fixed designs／simulated annealing algorithms，以及 Sobol low-discrepancy sequence 特性，新增有界 complete 子題。來源為線上核讀摘要，原始 HTML 未鏡像，未納入本機 FTS。Table 2.5 的建議最小樣本數以 SVG 公式圖提供；圖資回取失敗，數值保留為缺口。未執行 optiSLang 或產生設計點。


## 2026-11-01 Rigid Body Dynamics v251 IronPython Console restart

核對 v251 `Using RBD commands from the IronPython console` 原始 Markdown 及既有索引紀錄；整理 assembly/version path 載入、既有 `.mbd` 讀取、`CS_Environment` 修改／restart／Solve 及 `CS_MSolverDB` 回存流程。記錄官方 restart 限制：含 contact、Point On Curve joint 或多個 load steps 的模型不適用此程序；範例讀寫同一資料庫路徑，摘要加入備份提示。新增 bounded complete 子題，父級 IronPython Console 主題仍為 draft。來源標示 v251；未啟動 Mechanical／IronPython、未修改或求解模型，未重轉文件或重建 SQLite。


## 2026-11-01 PyScadeOne Simulation data

核對 PyScadeOne Simulation data API HTML 與既有 Markdown sidecar；整理 `.SD` 的讀取／建立／編輯模式、Stimuli 與 trace 的 `none` 語意、Variants／Groups／複合型別限制、值序列 append 規則、按需讀取設計及 `simdata --show` CLI 預覽。來源網址為 `version/stable`、本機鏡像目錄為 SDK 0.8，catalog release 保持 unknown。新增 bounded complete 子題，父級 Simulation data 主題仍為 draft。原始 HTML 與 sidecar 未修改／未重轉；未建立或編輯 `.SD` 檔，未重建 SQLite／搜尋索引。


## 2026-11-01 PySimAI PostProcessing request/result lifecycle

核對 PySimAI Postprocessings API HTML 原文及既有 Markdown sidecar；本機來源路徑為 `ansys-simai-core/0.4.8`，catalog release 與服務端版本維持 unknown。整理 `info`／`list` 查詢限制、`run` 參數型態、`wait` 的完成／失敗／timeout 回傳語意、狀態與 failure reason、結果資料型態，以及 `delete()` 會刪除結果資料的副作用。新增有界 complete 子題；未連線 SimAI 服務、提交後處理、下載／刪除結果，亦未重轉 HTML 或重建 SQLite。


## 2026-11-01 PyDYNA Deck parse／include／write controls

核對 PyDYNA `Deck` API 原始 HTML 與 Markdown sidecar；HTML `docsearch:version` 為 0.12.1，本機 mirror path 同為 0.12.1，但 sources catalog release 欄仍為 unknown，solver release 不由 SDK 版號推定。整理 keyword loads、`*INCLUDE` flattening／cwd／recurse、`strict=False` 保留 raw strings 與 warning、`write(validate=True)` 的 registered-validator 邊界及 `retain_parameters` 行為。新增 bounded complete 子題；未讀寫 keyword deck、展開 include 或呼叫 LS-DYNA solver，未重轉 HTML／重建 SQLite。


## 2026-11-01 Workbench v261 DesignXplorer discrete input parameter levels

核對 Workbench Scripting Guide Release 2026 R1／v261 Design Exploration printed pages 81–88 的 `InputParameter`／`DiscreteLevel` properties 與 methods。整理唯讀 `DiscreteLevels`、新增／查找／改值／刪除、zero-based index 與獨立組態說明；記錄 API 參數表將 `Index` 列為 int、範例卻傳字串 1 的來源差異。來源 PDF 與逐頁 Markdown 已在本機，未重轉；新增 bounded complete 子題，未修改 Workbench 專案或執行 DesignXplorer study，未重建 SQLite。

SQLite 僅做唯讀檢查：主索引可開啟，`PRAGMA query_only=1` 下的 Workbench 原文搜尋可回傳官方來源片段；當下未見 Python／ANSYS 相關程序或 `-journal`／`-wal`／`-shm` sidecar。現有索引仍是字典更新前的版本，新增子題尚未被索引命中；沒有執行增量寫入或重建。此檢查不能證明其他未辨識程序沒有開啟資料庫。


## 2026-11-01 PySimAI CurrentUser offline token 與 consent 撤銷

核對 ansys-simai-core 0.4.8 `current_user.html` 原始 HTML 及 Markdown sidecar，整理 `generate_offline_token()` 的 sdk client 關聯、consent 欄位與列出／撤銷方式、撤銷後 token 失效及 server-side 工作中斷副作用。新增 bounded complete 子題；未產生 token、查詢或修改帳戶 consent。SQLite 仍未同步本輪新增字典文字，未重建索引。


## 2026-11-01 PyTurboGrid 0.9.4 NDF to tginit／blade rows

核對 PyTurboGrid Multi blade row meshing example 的本機 HTML 與 Markdown sidecar，整理 `MBR()` 建立、`convert_ndf_to_tginit()` 回傳路徑及 `get_blade_rows_from_ndf()` 列查詢。文件位於 SDK 0.9.4 路徑，catalog release 仍為 unknown，TurboGrid 產品版本不推定。新增 bounded complete 子題；未轉換其他 NDF、載入 tginit、啟動 TurboGrid 或生成網格，SQLite 未同步／重建。


## 2026-11-01 PyScadeOne CLI discovery switches

核對 ansys-scadeone-core 0.8 `cli.html` 與既有 Markdown sidecar，整理 CLI 的 Python Scripts／PATH 位置、`--version`、`--formats`、重複 verbosity 開關及子命令 `--help`。該頁未提供子命令完整參數或 verbosity 級別定義；新增 bounded complete 子題，未執行 CLI。catalog release 與產品 release 保持 unknown；SQLite 未同步／重建。


## 2026-11-01 Motion CAR Toolkit 2D RDF road/tire compatibility

核對 CAR Toolkit Manual 原始 PDF 與逐頁 Markdown physical pages 67–75，整理 2D RDF 區塊、ROAD_TYPE 與 Fiala／UA、FTire、MF-Tyre／MF-Swift 相容矩陣、2D road 不視覺化及參考框架／高度公式。來源 PDF 標題含 2026 R1，但 catalog release 保持 unknown；僅完成 2D 範圍，不推定 3D road 或其他版本。新增 bounded complete 子題，未在 Motion 載入 RDF 或執行分析；SQLite 未同步／重建。


## 2026-11-01 PyAEDT HFSS create_lumped_rlc_between_objects

核對 PyAEDT 1.9.0 API reference HTML 與 Markdown sidecar，補錄來源清冊 ID `ansys_08c4c71aeff32ca5f7653a23`。整理最近邊緣連接、assignment/reference、axis direction、Parallel／Serial、R/L/C 單位與停用語意、boundary 平面選項及 `BoundaryObject`／`False` 回傳。官方頁 URL 為 stable，catalog AEDT release unknown；新增 bounded complete 子題，未建立幾何或求解。唯讀 FTS 查詢可命中官方 HTML/Markdown 來源正文；本次新加的字典摘要仍未同步，未重建 SQLite。


## 2026-11-01 OpenTD Python heated-bar／Case Set 範例

核對 OpenTD 2026 R1 網站 Appendix B 原始 Markdown 與 v242 PDF sidecar，整理 Python 2.7.15／pythonnet 2.3.0 範例的 assembly 載入、heated bar nodes／conductors、room boundary／convection、symbol heat load 與雙 transient Case Set 執行步驟。附錄中的 GAC path 含 `ReplaceMe`，範例未定義 cleanup 或結果驗收；未執行 Python、OpenTD 或 Thermal Desktop。新增 bounded complete 子題。唯讀 FTS 查詢 `pythonnet AddReference OpenTD` 命中 2026 R1 附錄原文，並成功取回包含 pythonnet 安裝要求的 chunk；新加字典摘要尚未同步，SQLite 未重建。


## 2026-11-01 Mechanical v261 Message metadata and severity

核對 Mechanical v261 `Message.md` 與 `MessageSeverityType.md` API sidecars，整理 display text、StringID、timestamp、location、source、related objects、nullable 型別及 Error／Info／Warning enum 數值。標明數值是 enum 成員值而非嚴重度排序或 solver error code；新增 bounded complete 子題，未執行 Mechanical。原文已在本機全文索引，新增字典摘要未同步／重建 SQLite。


## 2026-11-01 LS-PrePost v261 Keyword Manager

核對 Ansys LS-PrePost User’s Guide PDF 與逐頁 Markdown physical pages 429–434（printed pages 401–406），整理 Keyword Edit/Search、Model／All／RefBy、Model Check、刪除／移轉、KGroup search filter、material list controls 與雙擊編輯入口。標明 delete/transfer 會改動 keyword、Model Check 不等於 solver validation，以及 extended remarks 可能不顯示。新增 bounded complete 子題，未開啟或修改模型，SQLite 未同步／重建。


## 2026-11-01 PyOptiSLang ProxySolver to OptimizationOnMOP tutorial

核對 PyOptiSLang 1.7.0 tutorial HTML／Markdown 與官方 `.py` attachment，整理 AMOP／ProxySolver callback design study、保存、以 AMOP predecessor 建立 OptimizationOnMOPTemplate、目標 `minY` 及 dispose 範例。固定參數範圍與 synthetic response function 僅屬教學資料；`multi_design_launch_num=-1` 語意未由該頁解釋。新增 bounded complete 子題，未執行 SDK 或 optimization。唯讀 FTS 查詢 `mop_predecessor` 命中官方 tutorial chunk；新加字典摘要未同步，SQLite 未重建。

## 2026-11-01 HFSS 20 GHz Waveguide Combiner

確認 v261 PDF 封面標示 Ansys Electronics Desktop 2026 R1，原 PDF 89 頁，旁有 89 頁逐頁 Markdown sidecar，清冊記錄正文已索引（119,583 字元）。沿用既有 sidecar，未重跑轉換；依 PDF Page 9–87 整理模型、邊界／port、solution setup、S 參數與場後處理。sidecar 的頁碼標記可回查原文；圖表及模型影像未逐頁視覺比對，未執行 AEDT。原文 sweep name `19p5_25p4GHz` 與實際頻率範圍／後文名稱不一致，已列入字典限制。

### SQLite 索引狀態（2026-11-01）

唯讀查詢可正常讀取現有 `docs_index.sqlite`（596,601 筆文件 metadata，約 3.3 GB；journal mode `delete`），未取得 `database is locked` 錯誤。索引保存的 `catalog_manifest_stat` 為 `1793448862483616600:538158732`，目前清冊為 `1793494084627364700:547486810`，因此一般搜尋會觸發全量重建。重建前先備份現有資料庫至 `Documentation_clean/docs_index.sqlite.backup_before_knowledge_dictionary_20261101`；全量建置啟動後約五分鐘產生 216 MB 暫存庫及 17,132 個清理檔，仍需逐筆處理約 596,656 筆清冊，為避免這次整理變成長時間全庫重建而中止。正式舊庫與備份保留，僅清理本次暫存輸出。現有 HFSS 字典索引仍是舊內容（6,738 字元；目前檔案 13,483 字元），本次更新摘要尚未進入 RAG；需後續完成完整索引重建後再驗證代表查詢。

## 2026-11-01 Maxwell Object-oriented scripting

核對 Maxwell Scripting Guide v261（封面 Ansys Electromagnetics Suite 2026 R1）PDF Pages 109–125 與現有逐頁 Markdown sidecar，整理 object tree traversal、property read/write、project／design variable scope、dataset SI／user unit、GetSolutionDataPerVariation，以及 solver-specific children／3D Component encapsulation 限制。來源清冊記錄 PDF 正文已索引；目前全庫索引仍待更新，因此本次新增的 Maxwell 字典摘要尚未進入 SQLite。未啟動 AEDT、未執行範例，未逐頁比對圖示。

## 2026-11-01 SIwave Scripting Guide

核對 v261／2026 R1 SIwave Scripting Guide PDF Pages 19–22 與既有逐頁 Markdown sidecar，整理 GUI、`-RunScript`／`-RunScriptAndExit`、IronPython Command Shell、VBScript 環境變數條件，以及 IronPython 2.7／.NET Framework 4.0 的相容界線。將來源清冊曾記為 printed pages 3–13 的不精確定位改成實際 PDF physical pages 19–22。完整 `Scr...` command reference 未逐項整理；未執行 SIwave。新摘要尚未同步到 SQLite，索引更新狀態見上文。
## 2026-11-01 Mechanical v261 contact convergence diagnostics

直接核讀 Mechanical User’s Guide v261 官方 HTML 的 `Troubleshooting Convergence Problems` 與 `Investigating Contact Regions`（兩頁頁尾均標 Release 2026 R1）。整理 Contact Tracking／Contact Results／Force Convergence／NR residuals 的定位順序、Contact Results Trackers 的逐 timestep 輸出、partial solutions、penetration 與局部位移評估，以及來源列出的網格、單位、pinball、stiffness、detection、time step、unsymmetric solver、aggressive update 與 stabilization 選項。將「friction coefficient >0.25」限縮為該頁的條件式提示；不把建議當成通用求解配方。官方 HTML 已核讀但未鏡像到本機，已新增 bounded complete 子題；未啟動 Mechanical 或求解，圖示未逐一視覺檢查，SQLite 尚未更新。
## 2026-11-01 PyScadeOne Project 與 Swan Model

核對本機 PyScadeOne SDK 0.8 的 `Project management` API reference 與 `Modeler` guide Markdown sidecar。整理 `load_project()` 回傳條件、多專案載入、直接／遞迴 dependencies、Swan sources（含依賴）、`Project.model`、lazy declaration lookup，以及 `Project.save()` 儲存既有專案時會取代舊檔案的邊界。官方網址使用 `version/stable`，本機鏡像目錄為 0.8，不推定遠端頁面精確版本或產品 release。新增 bounded complete 子題；未載入／修改專案或執行 code generation，SQLite 尚未更新。

## 2026-11-01 Mechanical v261 contact HTML 文字擷取補件

官方 Mechanical User’s Guide v261 的 `Troubleshooting Convergence Problems` 與 `Investigating Contact Regions` 兩個 HTML 頁面先前只有瀏覽器核讀摘要，原文未落地。本機 `urllib` 連線到兩個官方網址皆回報 `getaddrinfo failed`；官方頁面仍可由已連線的瀏覽器文字檢視取得解析後正文。已將可見正文保存為 `Mechanical/v261/guide/ds_contact_best_prac_converge.md` 與 `ds_contact_best_prac_setup.md`，保留官方 URL、Release 2026 R1、頁面標題與段落層級，並將來源頁有圖但此次未取回的圖像列為缺口。

這兩份是瀏覽器解析文字擷取稿，不宣稱為下載原始 HTML 後的逐位元轉換；來源原始 HTML 仍缺。兩個檔案已加入文件清冊且品質為 `body_present`，知識來源清冊已更新路徑及狀態。完整 SQLite FTS 尚未同步，本輪未啟動索引重建。Mechanical／LS-DYNA／optiSLang 本機 HTML sidecar 與 SpaceClaim、Mechanical、LS-DYNA、optiSLang PDF 頁碼 sidecar 盤點均無缺檔；原始檔均保留。


## 2026-11-01 PyDPF SHELL281 field shape／shell layer

核對本機 PyDPF-Core `Fields containers and fields` sidecar（目錄 SDK metadata 0.16.3；網址為 `version/stable`，精確來源 release unknown）中 `Interpreting field length and shape`。整理 `shell_layer` selector 0–4、topbottommid 的 bottom→top→mid 順序及 selector 5 不適用；並核算來源 SHELL281 六分量、三層 corner-only `(12, 6)`／72 scalars，預設 Nodal midside extension `(24, 6)`／144 scalars、component selection 對 rows 的影響與 `extend_to_mid_nodes=False`。註明 extension operator 不會復原原始 RST 未提供的 midside 值。字典新增 bounded complete 子題；父級 Fields／FieldsContainer 主題仍 draft，因來源其他表格未全數人工核對。未執行 DPF、未讀寫結果檔，未重轉來源或重建 SQLite。


## 2026-11-01 Motion CAR Toolkit Work/Model 與 Assembly

核對本機 `Ansys Motion 2026 R1 Car_Manual.pdf` 頁碼 sidecar：PDF physical pages 10–12、23–27（手冊章節頁碼 1-10–1-12、1-23–1-27）。整理 Work 管理多個 Model、Model 分類保存 Assembly／Subsystem／Template／force element／mesh／part；Car Model 建立對話框及 Work Navigator 檢查；Assembly 作為 Subsystems 集合；Full Car／Half Car 執行需相應 test rig；Half Car 懸吊與可選 steering 範例；以及新建 Assembly、選取 Subsystems、Finish 後檢查步驟。新增 bounded complete 子題；CAR Toolkit 全整車分析父題仍 draft，因完整 test-rig 設定與 Full／Half Car run workflow 未逐項整理。PDF 標題含 2026 R1，catalog release 保持 unknown；未啟動 Motion 或執行分析。


## 2026-11-01 PyAnsys Sound DPF Server 與授權工作階段

重新核對本機 SDK metadata 0.4.0 的 PyAnsys Sound User guide 與 Initialize server and deal with the license tutorial sidecars。`connect_to_or_start_server()` 可啟動 local DPF Server 或連 remote server；設定 `ANSRV_DPF_SOUND_PORT` 時文件描述為嘗試 remote connection，預設 port 6780，亦可直接傳 `port`；未設定時依 DPF Server 安裝優先順序尋找並啟動 local server。授權範例以 `LicenseContextManager` 在進入／離開 context 時 checkout／release `avrxp_snd_level1`；不使用 context 時每次呼叫 DPF Sound operator 都再次 checkout；範例以移除 manager 參照釋放 increment。將來源已完整涵蓋的 DPF Server／授權工作階段主題由 draft 改為 complete；聲學判讀仍 draft。網址使用 `version/stable`，產品 release unknown；未連線 server、checkout 授權或執行 PyAnsys Sound。


## 2026-11-01 PyMAPDL launch_mapdl 與工作目錄

核對 PyMAPDL SDK metadata 0.74.1 User guide sidecar 的 PyMAPDL overview：`launch_mapdl()` 在背景建立 `Mapdl` instance；MAPDL 以 gRPC mode 啟動；預設工作目錄為 temporary directory，`run_location` 可指定目錄（範例使用 `os.getcwd()`）。由於本機 product release 為 unknown，保留 SDK／solver 版本界線。將 launch_mapdl 與工作目錄主題由 draft 更新為 complete；檔案傳輸版本條件另由既有子題追蹤。未啟動 MAPDL、未執行範例。


## 2026-11-01 PyAnsys Geometry Modeler 連線參數

核對 PyAnsys Geometry SDK metadata 0.18.2 User guide、Modeler API 與 connection package sidecars。User guide 明列預設 `127.0.0.1:50051`，並要求 host／port 改動時同步檢查 Docker port mapping；Modeler API 列出 `channel`、PyPIM `remote_instance`、local Docker `docker_instance`、Discovery／SpaceClaim `product_instance`、`timeout=120` 及 transport modes `insecure`／`uds`／`wnua`／`mtls`，未提供 channel 時才需要 `transport_mode`。將「Geometry service 與 Modeler 連線」由 draft 更新為 complete；服務部署、產品 release 與跨版本相容仍由另一 draft 追蹤。來源 URL 使用 `version/stable`，catalog release unknown；未在本機啟動 Geometry service 或連線測試。


## 2026-11-01 PyMAPDL mTLS 遠端連線

核對 PyMAPDL `Securing connections with mTLS` 本機 HTML 與逐頁 Markdown sidecar。整理 PEM CA／server／client 憑證角色、同一 CA 簽署要求、`SERVER_AUTH`／`CLIENT_AUTH`、hostname／IP SAN、`ANSYS_GRPC_CERTIFICATES` server 路徑、`launch_mapdl(transport_mode="mtls", certs_dir=...)` 與 `start_instance=False` 既有 server 連線設定；保留 `PYMAPDL_GRPC_TRANSPORT` 替代環境變數路徑。文件警告 `generate_test_certificates()` 僅供測試與本機開發，預設 24 小時，production 憑證應由組織 IT／可信 CA 提供，私鑰不得提交 repository。將「遠端連線與 mTLS」主題由 draft 更新為 complete；PyMAPDL 網址使用 `version/stable`，SDK 路徑 metadata 0.74.1，MAPDL product release unknown。未產生憑證、未啟動或連線 MAPDL。


## 2026-11-01 PyAEDT project／design 建立與儲存

核對 PyAEDT SDK metadata 1.9.0 `Basic tutorial` 與 `Command line interface` sidecars。Basic tutorial 展示 `Desktop(version="2026.1", non_graphical=True, new_desktop=True, close_on_exit=True)` context 建立 `Circuit()`，以及 graphical `Circuit` 的 `save_project()`／`release_desktop()`；保留程式註解稱 AEDT 2025 R1、實際 `version` 參數為 2026.1 的矛盾。CLI project 群組需操作已啟動的 gRPC session 並指定 `--port`，整理 project／design create、save、close 命令與該頁列出的 design type。將「專案與設計入門」由 draft 更新為 complete；官方網址使用 `version/stable`，AEDT product release unknown。未執行 PyAEDT CLI、未建立或修改 AEDT 專案，未求解。


## 2026-11-01 Mechanical v261 Solution Summary Worksheet

核讀 Mechanical User’s Guide v261 §19.6.13 Solution Summary Worksheet 與 §19.2.4 Result File Items 官方頁面，整理 Worksheet 入口、可用 solution quantities、material／element type 資訊、solver component names、結果最小／最大值表格、未評估結果顯示為 0 的限制，以及 Condensed Part、On Demand Expansion 等可用範圍限制。新增 `v261 Solution Summary Worksheet` bounded complete；較大的「結果與後處理」父題仍為 draft。恢復來源清冊中 Results introduction（v261）、Review Results（v252）及 Result File Items（v261）的 URL／版本，並新增 Solution Summary Worksheet v261 來源列。官方頁面以網頁文字核讀，未保存原始 HTML。

SQLite 文件索引唯讀開啟成功（journal_mode=delete、636,759 個 chunks）；目前 `BEGIN IMMEDIATE` 寫入保留鎖可取得並已 rollback，未修改資料，表示探測當下沒有其他寫入者持鎖。**字典尚未同步到索引**：以唯讀 FTS 查詢新增段落獨有詞組未命中；`docs_meta` 中 mechanical.md 的已索引雜湊也與目前檔案不同。現有 `ensure_index()` 不比較 extra-root 字典檔案的修改時間；同步需執行完整索引建置，本輪暫不重建。未執行 Mechanical、未求解。


## 2026-11-01 PyOptiSLang RootSystem 單筆 design evaluation

重新核對本機 PyOptiSLang `Design evaluation` HTML／Markdown sidecar。官方指南明確限定 root-system 層級的逐筆 design evaluation，不涵蓋內部 Sensitivity／Optimization system 的設計生成與監控；整理 root parameter／response 與 Receive designs／Send back designs 前置條件、`get_reference_design()`／`Design` 建立、parameter verification、`evaluate_design()` 回傳及 root system 僅保留最後一筆設計的界線。source URL 使用 `version/stable`，catalog release 維持 unknown；新增 bounded complete 子題，較大的 PyOptiSLang／Web API 父題仍 draft。未啟動 optiSLang 或執行範例。此新增字典段落與 Mechanical Worksheet 摘要均未同步至 SQLite FTS。


## 2026-11-01 Mechanical v252 Messages Window

核讀 Mechanical User’s Guide v252 §2.20.4 官方 Messages Window 頁面，整理訊息類型、顯示路徑、狀態列提示、popup／Linux 限制、錯誤分類篩選、相似訊息合併及右鍵定位／複製／刪除／重新整理功能。恢復 `web_mechanical_messages_v252` 的官方 URL 與 Release 2025 R2，新增 `v252 Messages Window` bounded complete；Mechanical「疑難排解」父題仍 draft，因完整 solver error handbook 及根因規則仍不足。官方 HTML 未鏡像，摘要已加入字典；本段與本輪其他新增字典尚未同步 SQLite FTS。未執行 Mechanical 或求解。


## 2026-11-01 LS-PrePost v261 Keyword Editing

依 Ansys LS-PrePost User’s Guide v261 §7.8（PDF physical pages 790–796／printed pages 762–768）逐頁 Markdown，整理 Keyword Input Form 欄位標題、搜尋、新建／提交／刪除標記、RefBy／Pick、`*PARAM` 指派與 `*DEFINE_TABLE`／`*SET` 特殊表單。新增 `v261 LS-PrePost Keyword Input Form controls` bounded complete；LS-PrePost 父題仍 draft，因整體 GUI／Python module API 及跨版本行為未完整覆核。未執行 LS-PrePost，未修改模型。SQLite FTS 同步待目前暫存索引建置狀態釐清後再核對。

## 2026-11-01 SCADE、ModelCenter、SCADE One 續整與 CFX 來源缺口

核對本機字典與主題清冊後，完成三個模組的有界主題整理：SCADE 8 項均為 complete，新增 state machine strong／weak transitions、Design Standard 章節導覽、Python／Java／Tcl API 選路、Rapid Prototyper 工作流程、安裝章節與 glossary tag 說明；產品 release 未知或以文件識別日期表示處均未推定 release。ModelCenter 8 項均為 complete，補齊產品 API 家族來源引用與 Remote Execution Java `AnalysisServerClient` 方法家族導覽，並保留各 SDK 不相容性、完整 method reference 及 runtime 未驗證限制。SCADE One 7 項均為 complete，CLI、SDK entry point 與 simulation data 主題限定於本機 PyScadeOne 0.8 文件，未執行 CLI 或修改 `.SD` 檔案。

CFX 清冊將已整理的 PyCFX 0.3.0 安裝、logging、CCL state、session 與教學案例分別追蹤；另將「完整 CFX 使用者手冊與 solver 方法」標為 `source_limited`，因本機來源以 PyCFX SDK 文件及少量範例為主，不把 SDK 文件摘要當成通用 CFX 求解指南。

全清冊核對為 400 項主題、63 個產品／模組字典頁；SCADE、ModelCenter、SCADE One 與 CFX 主題引用的來源 ID 均存在，清冊 local paths 均存在。既有 SQLite rebuild session 10103 仍在執行；2026-11-01 11:45 暫存資料庫為 433,283,072 bytes，正式 `docs_index.sqlite` 仍是 3,305,467,904 bytes。字典變更發生於此 rebuild 啟動之後，不宣稱新段落已進入正式索引。程式 `ensure_index()` 目前不比較 `EXTRA_SOURCE_DIRS` 內 Markdown 的修改時間；後續須在目前建置結束後進行完整同步，並重新用代表性查詢與 `get_chunk` 核對。未執行產品 runtime、求解或測試。
## 2026-11-01 PyDPF-Core Fields／FieldsContainer／Scoping

依 PyDPF-Core `Fields containers and fields` 與 `Model` 官方 `version/stable` sidecars，逐節核對 FieldsContainer field access、labels、time-frequency support、Field metadata、data shape／scoping、entity lookup 與 field-side operations。字典補充 Python index 與 one-based time-set ID 差異、time／elshape 多標籤查詢、`get_entity_data(index)`／`get_entity_data_by_id(id)` 的索引差異、`as_local_field()` 批次讀取及 DPF-side `Field.max()`。SHELL281 corner-only／midside extension 和 shell-layer selector 仍限定文件示例，不泛化成其他 solver 的 shape 保證。將 `Fields、FieldsContainer 與 Scoping` 主題由 draft 更新為 complete；本機 SDK metadata 路徑為 0.16.3，官方頁未標精確 release，未執行 DPF 或讀寫結果檔。

本輪結束時 DPF 共 10 個主題（10 complete）。字典來源 ID 與本機 sidecar 路徑核對通過。既有 SQLite rebuild session 10103 仍在執行；2026-11-01 11:48 暫存 DB 為 457,662,464 bytes，正式索引仍為舊資料庫。此次字典更新晚於 rebuild 啟動，全文索引仍需完成後核對／同步。
## 2026-11-01 DPF Fields 資料與 HFSS 3D Layout scripting

DPF：依 PyDPF-Core Fields／Model `version/stable` sidecars 補齊 time-set／Python index、label query、entity ID／row index、`as_local_field()` 與 DPF-side reduction 導覽；包含 Field metadata、shape/scoping 及 SHELL281 範例限制。將 `Fields、FieldsContainer 與 Scoping` 標為 complete；本機 SDK metadata 0.16.3，官方頁 release unknown，未執行 DPF。

HFSS：從 Ansys Electromagnetics Suite 2026 R1 `HFSS 3D Layout Scripting Guide` 的封面、目錄及 IronPython／Layout layer 頁面整理 Desktop IronPython、CPython/gRPC、beta non-graphical、active layer 與 locked layer 規則，以及 PyAEDT beta 與 legacy script API 的邊界。新增 `HFSS 3D Layout scripting environments and layer semantics` bounded complete；廣泛 command/object API 主題仍 draft。未啟動 AEDT。

本輪結束時全清冊 401 項主題，63 個產品／模組字典頁；DPF 10/10 complete，HFSS 4 complete、1 draft、1 source_limited。相關來源 ID 與本機來源路徑核對有效。既有 rebuild session 10103 在 2026-11-01 11:50 仍活著；暫存 DB 471,449,600 bytes，正式 `docs_index.sqlite` 為舊資料庫。新字典內容仍待索引建置完成後同步與搜尋／片段擷取核驗。
## 2026-11-01 HFSS 3D Layout 與 Maxwell solution scripting 子題

HFSS v261：依 HFSS 3D Layout Scripting Guide PDF 封面／目錄、IronPython execution、active layer／locked layers 與 PyAEDT beta 章節，完成 execution environment／layer semantics 有界摘要；不涵蓋全部 command/object API，parent `HFSS 3D Layout scripting` 保持 draft。

Maxwell v261：依 Scripting Guide PDF Pages 592–593 核對 `AnalyzeAll` 涵蓋 nominal 與 Optimetrics analyses、`isBlocking` 預設 True、非同步時回傳及 `AreThereSimulationsRunning` 狀態查詢；依 Pages 946–949 整理 `GetSolutionDataPerVariation`、result interface 與 sweep SI／user units。新增該 bounded topic complete，完整 solution commands 仍為 draft。未執行 AEDT、HFSS 或 Maxwell。

全清冊增至 402 項主題、63 個產品／模組字典頁。DPF／HFSS／Maxwell 新增主題引用的 source IDs 與 local paths 抽查全數通過。SQLite rebuild session 10103 於 2026-11-01 11:51 仍活著；暫存 DB 481,976,320 bytes，正式 `docs_index.sqlite` 仍為舊資料庫。上述字典變更尚未同步至正式索引。
## 2026-11-01 Motion CAR Toolkit Full Car／Half Car 有界主題

依 CAR Toolkit Manual 的逐頁 Markdown sidecar physical pages 41–42、89、118–119，整理 Full Car／Half Car test rig 職責、最低 Subsystem、Full Car 與 Half Car 的共通及專屬分析欄位，並註明 DCF／LCF 匯出用途。新增 bounded complete 子題；CAR Toolkit 模型階層與 Full Car／Half Car 全分析父題仍為 draft，因完整各類參數、設定步驟及其他版本未涵蓋。PDF 原件與 sidecar 均保留；本次以 sidecar 頁標與文字核對，未以獨立 PDF renderer 抽查版面／表格圖像。手冊標題含 2026 R1，清冊 release 仍為 unknown。未啟動 Motion、未執行分析。

## 2026-11-01 PyACP 0.4.1 啟動需求與 GUI 連線界線

依本機 PyACP Getting Started HTML sidecar 核對 ACP 2024 R2+、Python 3.11–3.14、`ansys-acp-core[all]` 安裝示例、virtual environment 建議及 `launch_acp()` 背景 instance 行為；記錄 PyACP 無法連接 ACP GUI。新增 bounded complete 子題，ACP 的 interface/version boundary 父題仍 draft。官方網址使用 `version/stable`，sidecar 位於 0.4.1 文件目錄，sources catalog release 為 unknown；未推定 stable URL 的固定版號。原始 HTML 保留，未執行安裝、ACP 啟動或 GUI 連線。

## 2026-11-01 PySherlock gRPC transport settings

依 PySherlock 2.1.4 `launch_and_connect` API sidecar，整理 `insecure`／`mtls`／`uds`／`wnua` transport 定義、host／port／timeout，以及 mTLS／UDS 路徑參數預設值。將「傳輸模式與連線設定」標為 bounded complete；不聲稱完整安全部署指引或 OS 相容矩陣已覆蓋。將 launch lifecycle 段落改為參照前節，避免重複預設值；SDK page `Available Since: 2025R2` 與 catalog release `unknown` 分開保留。未啟動 Sherlock、未測試 gRPC transport 或憑證。

## 2026-11-01 Mechanical v261 contact formulation choices

依 Mechanical User’s Guide v261 `Define Advanced Contact Settings` 官方頁整理 Contact Type 與 Formulation 的區別，以及 Program Controlled、Pure Penalty、Augmented Lagrange、Normal Lagrange、MPC、Beam 的文件所述機制與限制。新增有界 complete 主題；廣泛的「接觸與邊界條件」父題仍 draft，因完整 contact behavior、elements、analysis／solver applicability 與 formulations 仍需整合核對。來源為官方 v261 網頁摘要，HTML 未鏡像、未納入正文全文索引；未執行 Mechanical 或求解。

## 2026-11-01 OpenTD v261 AutoCAD／.NET compatibility

依 OpenTD 2026 R1 Prerequisites 與 Changelog 整理 AutoCAD 2018–2024 的 .NET Framework 4.8 條件、AutoCAD 2025+ add-in 的 .NET 8 條件、client program 限制，以及 .NET 組件版號／GAC／安裝目錄差異。保留 Changelog 中 2025 R2「當時僅有限 add-in 支援」與 2026 R1 prerequisite 的版本界線；新增 bounded complete 子題，較廣泛的 runtime/version compatibility 父題仍 draft。2024 R2 PDF 僅作手冊版本證據，未推定其 runtime 要求。未啟動 AutoCAD／Thermal Desktop、未編譯 OpenTD 程式。

## 2026-11-01 IcepakFEA AssignThermalCondition

依 Ansys Electromagnetics Suite v261 IcepakFEA Scripting Guide PDF physical pages 958–960，整理 `AssignThermalCondition` 僅用於 IcepakFEA–Structural design、Uniform=True 的指定熱條件，以及 Uniform=False 時來源 Icepak design／solution 和 mapped variables 的參數；明確與 Thermal design 的 `AssignTemperature` face-based boundary 分開。新增 bounded complete 子題；整體 Icepak／IcepakFEA scripting scope 父題仍 draft。PDF 及逐頁 Markdown sidecar 保留，未執行腳本、AEDT 或求解。

## 2026-11-01 ACT v261 scripted extension structure

依 ACT Developer’s Guide Release 2026 R1 physical pages 19–20、71–75，整理 XML definition／IronPython script 必備組成、可選支援檔、scripted／binary WBEX 差異與 ACT license 條件，以及 ExtSample1 的 XML／同名 extension folder、script 相對路徑、images 子資料夾與宿主 icon 格式差異。新增 bounded complete 子題；ACT extension 結構與生命週期父題仍 draft，未整理所有宿主部署流程、完整 callback 行為與 binary publishing。原始 PDF／sidecar 保留，未建立、載入或打包 extension。

## 2026-11-01 ACT extension topic and index rebuild status

ACT v261 scripted extension structure topic is complete and its source ID/PDF path were verified. Previous index handle 10103 was no longer pollable; the old temporary SQLite had not changed since 12:14 local time, no Python/SQLite process appeared in `Get-Process`, and an exclusive read probe on the old temp database succeeded. Started a fresh `build_index()` process as session 3953. At this checkpoint it remains live but has not yet produced a new temporary database; formal `docs_index.sqlite` is unchanged at 3,305,467,904 bytes. New ACT and other late dictionary content still needs post-build search/get_chunk verification.

## 2026-11-01 SpaceClaim、Mechanical、LS-DYNA、optiSLang 轉換再核對

逐一盤點四個首批產品目錄中的原始檔與同目錄 Markdown sidecar，未覆寫、未強制重轉任何既有輸出。SpaceClaim 有 4 份 PDF／4 份非空 Markdown，沒有 HTML；Mechanical 有 2 份 PDF／2 份 Markdown及 236 份 HTML／236 份 Markdown；LS-DYNA 有 7 份 PDF／7 份 Markdown及 247 份 HTML／247 份 Markdown；optiSLang 有 2 份 PDF／2 份 Markdown及 577 份 HTML／577 份 Markdown。所有配對 Markdown 均超過 100 bytes；PDF sidecar 的最小大小依產品為 22,739、129,339、29,590、102,606 bytes，HTML sidecar 最小大小依 Mechanical、LS-DYNA、optiSLang 為 245、271、206 bytes。PDF extraction 清冊另有 SpaceClaim 的 `Developers Guide_V232.pdf` 去重列；來源指向 Discovery 保留版本，不是額外缺失輸出。

這是檔案存在性及正文大小核對，不代表人工逐頁校對表格、圖片或技術語意；沒有因此推定 OCR 或圖表內容已完成。全庫 HTML 清冊目前仍列 1 筆 ACT v261 的 0-byte HTML 失敗（清冊記錄已說明無正文可抽取），不屬於上述四產品。完整索引建置 session 3953 仍待完成，轉換輸出已存在不代表本輪新增字典段落已進入 SQLite FTS。

## 2026-11-01 LS-PrePost XY PlotWindow bounded topic

依 Ansys LS-PrePost User’s Guide Release 2026 R1 physical PDF pages 814–822（printed pages 786–794）整理 XY PlotWindow 的曲線選取、圖面控制、軸／曲線設定、filter、資料儲存／載入及 operation 欄位。新增 `v261 LS-PrePost XY PlotWindow curve display and data controls` complete 子題；完整 output type 清單與 operation 語意未由該摘錄證實，LS-PrePost 父題仍 draft。PDF 原件與逐頁 Markdown 保留，未執行 GUI 或匯出資料。

更新後 `topics.csv` 共 409 項；本地側車確認 physical pages 814–822 均存在，PDF 與 Markdown 來源路徑存在。索引建置 session 3953 的控制代碼仍可輪詢但沒有輸出；暫存 `docs-index-vnxkp81v.sqlite` 仍為 40,960 bytes、最後修改時間 15:15，正式 `docs_index.sqlite` 仍為 3,305,467,904 bytes（08:42）。SQLite 搜尋與 `get_chunk` 驗證待建置完成後進行。

## 2026-11-01 Twin Builder MIMO System Identification bounded topic

依 System Identification Toolkit MIMO Guideline PDF physical Pages 1–6／逐頁 Markdown，整理 linear／限定 operating range 的適用條件、兩列 port names、step-value matrix 索引方向、每次只激發一個 input、step-response 命名與資料列格式、秒與 response units、Data Table 匯出建議、SML／Matlab／FMU 輸出與 license 說明。將 `Twin Builder MIMO System Identification 與 LTI ROM` 標為 bounded complete；來源 release 未標，圖像化設定畫面與比較圖未逐圖核對，不作跨版本推定，未啟動 Twin Builder。

更新後 `topics.csv` 共 409 項；該 PDF、sidecar 與來源 ID 均存在。Session 3953 仍可輪詢但未產生輸出；暫存索引 40,960 bytes（最後修改時間 15:15）、正式 SQLite 3,305,467,904 bytes（08:42）仍未變動，新增字典尚未經 SQLite 搜尋與 `get_chunk` 核驗。

## 2026-11-01 ACP PyACP Feature Tree bounded topic

依 PyACP 0.4.1 Feature tree 官方 HTML／Markdown sidecar，核對 `Model`→`ModelingGroup`→`ModelingPly` 階層、mapping 存取、建立及 clone/store parent 條件，並標明 ProductionPly／AnalysisPly 的 read-only 節點；另與 ACP in-app v261 `compolyx.ModelingGroup.create_modeling_ply` API 分開說明，避免混用 Python 介面。新增 `PyACP 0.4.1 Feature Tree 與 ModelingPly 存取` bounded complete，較廣的 feature tree／ply 物件主題仍 draft；PyACP sidecar metadata 為 0.4.1，stable URL 與產品 release unknown，未執行模型或腳本。

更新後 `topics.csv` 共 410 項，ACP 為 5 draft、5 complete。Session 3953 仍可輪詢但沒有輸出；暫存 `docs-index-vnxkp81v.sqlite` 仍為 40,960 bytes（最後修改時間 15:15），正式 `docs_index.sqlite` 仍為 3,305,467,904 bytes（08:42）。本次新增字典尚未經 SQLite 搜尋及 `get_chunk` 驗證。

## 2026-11-01 PyOptiSLang workflow node creation and slot connections

依 PyOptiSLang `Create workflow` 官方 `version/stable` HTML／Markdown sidecar，整理 `root_system.create_node(type_=...)`、`node_types`／手動 `NodeType`、建立時 `DesignFlow.RECEIVE_SEND`、一般及 parametric-system slots 與 `connect_to()` 範例，以及 `osl.dispose()` 連線結束。新增 `PyOptiSLang workflow 節點建立與 slot 連線` bounded complete；來源頁 SDK release unknown，範例 slot 名稱與方向未於實際 workflow 驗證，未執行 optiSLang。

更新後 `topics.csv` 共 411 項；optiSLang 為 5 draft、12 complete。索引 session 3953 仍有可輪詢控制代碼但尚未輸出；暫存 SQLite 仍為 40,960 bytes（最後修改時間 15:15），正式索引仍為 3,305,467,904 bytes（08:42）。新增字典待索引完成後以搜尋與 `get_chunk` 驗證。


## 2026-11-01 Twin Builder Scripting Guide 頁面核對

確認 Twin BuilderScriptingGuide.pdf 及逐頁 Markdown sidecar 存在；核讀 sidecar 對應 physical PDF Pages 35–40，確認物件階層、Reporter Editor 執行範圍及錄製／執行 script 章節文字可讀。Pages 35–38 已用於一個有界字典主題；Pages 39–40 與其餘手冊頁尚未逐頁轉換品質抽查。這是既有 sidecar 的抽查記錄，不代表 PDF 全文、表格與圖片均完成人工校對。

## 2026-11-01 LS-OPT 2026 R1 Manual DOE 頁面核對

確認 `lsopt_2026R1_manual.pdf` 與既有逐頁 Markdown sidecar 均存在；核讀 physical PDF Pages 87–88、92–93 對應的 DOE study、Direct Optimization 與 Global Sensitivity Analysis 文字，側車含逐頁標記。這次重用既有轉換輸出，未強制重轉 PDF；其他頁、表格與圖片未逐頁人工核對。來源清冊將兩份 LS-OPT PDF 分類為 `lsopt`，版本依封面／內文記錄為 2026 R1 與 6.0 (2018)。

## 2026-11-01 Mechanical ACT Customization Guide property 頁核對

確認 ACT_Customization_Guide_for_Mechanical.pdf 與逐頁 Markdown sidecar 存在；核讀 physical PDF Pages 7–11 中 `<property>` input/output parameterization 規則及 `isparameter`／`readonly` 條件。新增有界 ACT dictionary topic；重用既有 sidecar，未重轉 PDF。其他章節、範例全流程與圖表未逐頁核對，未執行 Mechanical。

## 2026-11-01 LS-DYNA Vol. II R16 `*MAT_003` 頁面核對

核讀 `LS-DYNA_Manual_Vol_II_R16.pdf` physical pages 234–236 及現存逐頁 Markdown sidecar，確認卡片欄位、BETA 硬化端點、Cowper–Symonds SRC／SRP、VP 率效應 formulation 與 history-variable 說明。重用既有 PDF／Markdown 轉換成果，未重轉原件；頁碼範圍外未逐頁核對，未建立模型或求解。來源 catalog release 欄保留 unknown，未由內頁 R16 標記推定 catalog release。

## 2026-11-01 ACT Wizard callback／API 版本界線核對

核對 v251 `Reference.callback.property.OnButtonClick` 原始 HTML 與 Markdown sidecar，確認 callback 說明可讀，但參數仍為模板佔位文字且 return type 空白；另核對 v261 ACT API Reference Guide Part 2 Markdown 印刷頁 4961–4966 的 `IWizard`／`IWizardStep` 簽名。此詞條將 XML callback 與 .NET Wizard API 分開，不將兩份來源宣稱為逐項相容性比較；沿用現有 HTML／PDF 抽取成果，未重轉或執行 ACT。

## 2026-11-01 Twin Builder Scripting Guide 錄製與執行頁面核對

核讀 `Twin BuilderScriptingGuide.pdf` physical Pages 38–40 與現有逐頁 Markdown sidecar，確認 `.py` 檔案錄製、project scripts library、GUI 執行與命令列參數入口。沿用現有 PDF／Markdown 轉換成果，未重轉原件；`-runscript` 與 `-runscriptandexit` 差異、HPC submission 及其他頁面未在本次核對，未執行 Twin Builder。

## 2026-11-01 PyOptiSLang Python execution pages

核對 1.7.0 文件集合內 `run_python` User Guide 及 `Project.run_python_script`／`run_python_file` API HTML／Markdown sidecars；頁面標示 `version/stable`，sources catalog release 維持 unknown。新增 context isolation、script file execution、stdout/stderr 與 optiSLang `>=27.1` async 條件有界摘要；重用既有 HTML sidecars，未抓取或重轉下載 script，未執行 optiSLang。

## 2026-11-01 SQLite index lock recheck

Session 3953 仍可輪詢但無輸出；它對應的 `docs-index-vnxkp81v.sqlite` 為 40,960 bytes，唯讀獨占開啟探測成功，正式 `docs_index.sqlite` 為 3,305,467,904 bytes且獨占讀取成功。另發現 `docs-index-veqsm5mz.sqlite` 正在增長（本次觀察 343,146,496 bytes，15:42:45），其資料庫與 `-journal` 均無法獨占讀取，確認有另一程序持有開啟中的 SQLite 檔案；此暫存檔與 session 3953 的檔案名稱不同。程序清單未顯示 Python／SQLite 程序；Restart Manager 資源查詢在 `RmStartSession` 回傳錯誤 29，無法取得鎖定 PID。未嘗試停止程序、清除 journal 或碰觸索引；新的字典段落仍未經正式搜尋／片段擷取驗證。

## 2026-11-01 ACP PyACP import/export topic

依本機 PyACP `import_model()` API HTML、`export_analysis_model()` API HTML 與 Create input file HTML／Markdown sidecar，整理六種輸入格式識別、`unit_system` 條件、可忽略實體、section data 轉換、材料 UVID 行為，以及 CDB／HDF5 輸出邊界。對照官方目前 `version/stable` 頁，現行指南與 API 均寫 `ansys:h5`；本機快取的 release unknown 指南保留 `ansys::h5`，故字典明列來源差異但不推定 runtime。發現 topics.csv 已有同來源且內容相同的 complete 子題，移除舊 draft alias，保留 canonical complete 條目；清冊由 417 項減為 416 項。PyACP product release 仍 unknown，未啟動 ACP 或執行匯入／匯出。

## 2026-11-01 LS-OPT input and execution topic

依 LS-OPT Version 2026 R1 Manual physical PDF Pages 44–45、60、63 與逐頁 Markdown，核對 GUI／batch／viewer 命令、Windows／Linux GUI 啟動、project 檔案入口及 `--clean` 等旗標會刪除的資料範圍；另將 LS-OPT 6.0（2018）Tutorial Problems 的 `job_log`、舊版 run command 與 restart 提醒標為歷史範例。更新 LS-OPT「輸入檔與執行」為有界 complete；未啟動 LS-OPT，未執行任何刪除選項。

## 2026-11-01 PyMAPDL APDL wrapper topic

依 PyMAPDL `language and usage` 官方 stable 頁及本機 0.74.1 HTML／Markdown sidecar，整理 PEP 8 command wrapper 對照、`/`／`*` 命名規則、空 APDL 參數映射、`Mapdl.run()`／`Mapdl.input()` 原始命令入口與 entity selection 回傳 IDs。將 `APDL commands 的 Python wrapper` 標為有界 complete；不宣稱涵蓋全部 API，未連線或執行 MAPDL。MAPDL 產品 release 仍 unknown。

## 2026-11-01 AEDT version boundary and API layers

依 PyAEDT 1.9.0 local Basic tutorial、`Desktop` 與 `Hfss` API sidecars，並核對官方 stable API 頁。記錄 SDK metadata 與 AEDT product version 分屬不同版本欄位、`Desktop.version` 的文件示例／預設，以及 Basic tutorial 的 2025 R1 註解與 2026.1 參數不一致；另以 Desktop／Hfss 作有限 API layer 導覽。更新兩個 AEDT draft 為有界 complete；產品版本 release unknown，未執行 PyAEDT 或 AEDT。

## 2026-11-01 Maxwell AnalyzeAll and sweep data topic

依 Maxwell Scripting Guide v261 逐頁 sidecar 核對 Project 與 Design 物件的 `AnalyzeAll` 作用範圍、`isBlocking` 及狀態查詢，再比對 `GetSolutionDataPerVariation`／`GetSweepValues` 的返回物件和 SIValue 說明。目視檢查 PDF physical Page 946，確認手冊例子將 1–3 GHz 配上 SIValue=True 的 1,000,000–3,000,000 數值，與其 GHz 標籤及通常換算不一致；字典保留此來源缺陷並避免將該數值作換算依據。將 Maxwell「Solution commands」draft 改為有界 complete；未執行 AEDT 或 Maxwell。

## 2026-11-01 Icepak recorded script and repeated plane-cut export

依 v261 Getting Started with Icepak – Scripting Example sidecar，整理 GUI Record／Stop／Run Script 步驟、plane／Temperature field plot／JPEG 匯出流程與 loop 變數關聯；目視核對 PDF physical Pages 20–22 的截圖程式碼，補上 sidecar 未抽出的 `CreateCutplane`、`CreateFieldPlot` 變數插入點及圖片命名模式。教學顯示的 X 範圍／間距、Region 座標和視角依案例而異；錄製標頭為 AEDT 2022.1.0，不能當作 v261 相容保證。將 Icepak script-recording topic 更新為有界 complete；未執行 AEDT／Icepak。

## 2026-11-01 Twin Builder Modelica tutorial

檢查 `ModelicaTutorial.pdf` v261 對應的逐頁 Markdown；physical Pages 29–45 可抽取 PID 範例流程、宣告與多數參數表，足以整理出有界主題。PDF Page 36 的 `driveAngle` variable dialog 與 Pages 46–48 的 sample reports 以圖像為主，本輪沒有目視核對，未將圖中文字或曲線值作推定。原 PDF 與 sidecar 均保留。

## 2026-11-01 Workbench multi-project geometry update example

檢查 Release 2026 R1 `Workbench_Scripting_Guide.pdf` 與逐頁 Markdown；physical Pages 27–31（printed pages 17–21）包含多專案幾何替換範例及程式說明，sidecar 正文足以追蹤 `Open`、`Geometry.SetFile`、`Update`、狀態檢查、log 與另存步驟。本文依程式實際使用的 `os.listdir()` 記錄單層掃描界線，也註明 update 失敗時仍會存檔。原 PDF 與 Markdown sidecar 均保留；未執行 Workbench，未重轉 PDF。

同一份 v261 PDF 的 physical Pages 31–34、34–37 分別涵蓋專案檔案引用搜尋，以及 Engineering Data 多線性硬化材料表範例。Sidecar 保留遞迴搜尋、`GetAllFiles()`、component file references、quantity 單位與 `SetData()` 欄位流程；字典額外標明範例的 `fileList`／`projList` 使用差異和案例特定應變截斷值。PDF／Markdown 原件未改寫，未執行 Workbench。

## 2026-11-01 ACT Extension Manager 與 Mechanical callback 時機

核讀 ACT Developer’s Guide v261 的逐頁 Markdown，並用 PDF physical Pages 22、45–50 核對 Known Issues 與 Extension Manager 原文。整理 scripted／binary extension 顯示與載入條件、專案保存 extension 缺失警告、Workbench 管理器載入／卸載 Mechanical context 的狀態差異，以及 Mechanical `onInit`／`onLoad` 存取 `ExtAPI.UserInterface` 的限制。原 PDF／sidecar 保留；未操作 Extension Manager 或載入 Mechanical extension。

## 2026-11-01 Circuit Python UDM／UDP interfaces

核讀 Circuit Scripting Guide v261 的 PDF physical Pages 53–59 與逐頁 Markdown，分別整理 Python UDP 的 library directory／`UDPExtension` 必要方法，以及 Python UDM 的 instance／`Refresh`／`ReleaseInstance` 契約。摘要保留兩種 extension 類型不同的 class 與 callback 介面；未重轉 PDF，未建立或執行 UDM／UDP。

## 2026-11-01 EMIT script execution and arguments

核讀 EMIT Scripting Guide v261 的 PDF physical Pages 63–64 與逐頁 Markdown，整理 GUI 的 Run／Stop／Pause／Resume、命令列 `-runscript`／`-runscriptandexit` 入口，以及 `-scriptargs` 以單一未修改字串傳給 `ScriptArgument` 的契約。未推定兩個命令列模式的程序生命週期差異；PDF／sidecar 均保留，未執行 AEDT。


### 2026-11-01 CFF v252 Project::Iterator 有效狀態與項目建立

- 依 v252 Iterator class reference 整理 null/error iterator、`ok()`／`getError()`、project-only 與磁碟關聯的 file/folder 建立 overload、link 及 `find(Query)`。來源為本機逐頁轉換 Markdown，來源清冊已收錄。
- 未推定 `import` 的完整副作用、find 排序與持久化時點；未執行 SDK。


### 2026-11-01 CFF 字典 RAG 增量修正

- 全庫重建完成並通過索引器驗證：596,557 筆文件、647,389 chunks、596,269 筆 catalog 來源雜湊已核對。抽查發現 CFF 字典的索引內容雜湊與現行檔案不同，已以暫存 SQLite 副本更新該字典 4 個 chunks，核對內容雜湊一致並通過 `PRAGMA quick_check=ok`。
- 使用既有搜尋與片段擷取函式查詢 `Iterator newFolder`，結果命中 CFF 字典並成功回取含 `Project::Iterator` 摘要及來源連結的 chunk；`_needs_rebuild()` 為 false。未執行 CFF SDK。
- 曾發生的舊 SQLite 鎖定事件無法由受限 Windows 程序查詢回溯 PID；本輪 SQLite 唯讀開啟、隔離建置及原子安裝均成功。


### 2026-11-01 SimAI 0.4.8 Client 設定、認證與 proxy/TLS

- 依本機 SDK 0.4.8 Client、configuration、config file 與 proxy sidecar 整理 `from_config` profile/path/kwargs、TOML 搜尋位置、互動登入與 token 互斥、系統 proxy 覆蓋、CA bundle 及 TLS 驗證注意事項。Client API 對預設路徑的 Unix 限定與 config guide 列示 Windows 路徑不一致，保留為待依實際安裝版本核對的文件差異。
- 更新 [SimAI 字典](simai.md)、[主題清冊](topics.csv) 與本記錄。未連線服務、未提交憑證或 token。


### 2026-11-01 AnsysEM v261 VHDL-AMS Automotive Powernet 範例導讀

- 核對 VHDL-AMS Tutorial Release 2026 R1 的逐頁 sidecar 與 PDF physical Pages 23–27；整理 powernet 模型範圍、案例功能表、Student Version 支援標示及範例素材入口。保留 Page 23 概述五個步驟、Page 27 表列六個 case 的原文差異。
- PDF 表格文字可抽取；Page 25 示意圖未目視重建。未執行 Twin Builder 或範例專案。


### 2026-11-01 PyTurboGrid 0.9.4 multi-blade-row 範例範圍核對

- 對照官方 HTML 與本機 Markdown sidecar；兩者程式內容相符。頁面簡介稱 parallel execution，但示例只建立 MBR、轉換套件附帶 NDF 並查詢 blade rows，未展示平行調度或網格生成。字典與主題狀態限縮至程式實際展示範圍；未執行 TurboGrid。
- RAG 代表查詢 `AxialFanMultiRow` 與 `get_blade_rows_from_ndf` 均命中字典並可回取 chunk；組合查詢 `parallel execution AxialFanMultiRow` 未命中，保留為詞彙組合的檢索缺口。


### 2026-11-01 Mechanical v261 Bolt Pretension scope 腳本

- 對照 `Ansys_Scripting_in_Mechanical_Guide.pdf` physical page 216 與逐頁 Markdown sidecar；確認範例在 `Transaction()` 內迭代 `Tree.ActiveObjects`，移除各 `Location.Ids` 的第二個項目，以處理案例中分割圓柱面的 pretension scope。字典明列 selection、ID 數量及幾何身分的前提；未執行 Mechanical，頁面插圖未目視核對。
- RAG 查詢 `pretension scope` 命中字典並成功回取含適用前提的片段；`RemoveAt(1) pretension` 未命中字典，保留為以 API 程式碼查詢的檢索缺口。


### 2026-11-01 PyRocky Simple particle simulation（SDK 文件目錄 0.6.2）

- 對照官方 HTML、Markdown sidecar 與 `inputs/minimal.py`；project/study 建立、預設 particle／circular inlet、domain tuple、solver duration、SaveProject、StartSimulation 與曲線讀取程式內容一致。原文未替 domain tuple 標單位；`version/stable` catalog release 為 unknown，未推定 Rocky 產品版號。頁面列出的曲線輸出只作案例紀錄；未啟動 Rocky 或求解。


### 2026-11-01 Zemax v261 ZOS-API 語言與物件導覽

- 對照 v261 Introduction、`IZOSAPI_Connection`、`IZOSAPI_Application` 與 `IOpticalSystem` 本機 Markdown 原文；確認四種文件語言、導覽方式與介面定義的 Connection → Application → 單一 `.ZMX` 系統關係。只整理文件層級，不外推至 v252 或安裝相容性；未執行 ZOS-API。
- RAG 查詢 `光學系統` 命中字典並成功 `get_chunk` 回取介面層級；英文組合 `IOpticalSystem ZMX` 未命中字典，保留為檢索詞彙缺口。


### 2026-11-01 ADR v261 Web viewer events／methods

- 對照 `Events` 與 `Methods` 兩份本機 Markdown 原文；整理 element-scoped event、renderer 限定、`renderImage()` 與 SCDOC attribute methods。保留方法說明 target=`part`、同頁範例使用 `parts` 的矛盾；未連線 viewer 或實測事件。
- RAG 查詢 `parts-changed` 命中字典並成功 `get_chunk` 回取事件範圍與方法矛盾說明。


### 2026-11-01 LS-PrePost v261 Fringe Component／Range

- 直接以 PyMuPDF 核對 PDF physical pages 666–667、753–756，並與逐頁 Markdown sidecar 比對；整理 Plastic Strain 選取步驟、Dynamic／Static／User 範圍、range 對象與手冊示例上下限。案例值單位未標示；PDF 插圖未目視檢查，未在 LS-PrePost 操作或載入結果。
- RAG 查詢 `Plastic Strain Static User` 命中字典並成功回取包含三種範圍模式與案例單位限制的片段。


### 2026-11-01 PyOptiSLang oscillator sensitivity → MOP optimization runner

- 核對 PyOptiSLang runner 官方 HTML、Markdown sidecar 與附件 `.py`；三者的 imports、兩個 `examples.get_files()`／`run_python_file()` 呼叫、`project.start()`、註解中的 `save_as()` 及 `dispose()` 流程一致。來源清冊 release 為 `unknown`；本機 1.7.0 目錄不是 stable URL 的固定版本證明。內層 sensitivity／optimization scripts 未本機收錄，未推論其 DOE 或 MOP 設定。另記錄 save snippet 使用 `os.path.join()` 但未 import `os`；未執行 optiSLang。


### 2026-11-01 AnsysEM Q3D v261 2D Grounded Coplanar Waveguide W-element 與 diel_thick 掃描

- 以 PyMuPDF 直接核對原 PDF physical Pages 45–51，並比對同名逐頁 Markdown sidecar。記錄 `Setup1:Sweep1` → Nexxim/HSPICE W Element 匯出、`diel_thick` 0.2–0.5 mm／0.05 mm Linear Step、`AddGroundMatrix` 的 `R(trace,trace)` 計算，以及停用頻率 sweep 後查看參數化分析表格的步驟。
- 電阻隨地平面位置變化的敘述是此模型案例結果；未目視核對頁面圖表、未執行 AEDT/Q3D，亦未將案例參數作為工程建議。
- RAG 查詢 `diel_thick W Element` 命中字典並以 `get_chunk` 回取涵蓋摘要、頁碼與 PDF/sidecar 連結的 chunk 12；`R(trace,trace) AddGroundMatrix` 亦命中字典及來源正文。未記錄搜尋失敗。


### 2026-11-01 Mechanical v261 PlotData 位置與表格限制補充

- 直接以 PyMuPDF 核對原 PDF physical Pages 138–139、152–155，對照逐頁 Markdown；補充 Nodal／Elemental／Elemental Nodal 欄位文字、surface facet export 與 PlotData 的差異、beam section 結果設定及 path 結果限制。保留手冊 Elemental 欄位描述，不將欄位鍵名從結果類型推定。
- 擴充既有 PlotData topic，不另建重複主題；未目視重建圖示、未執行 Mechanical，也未驗證其他版本。


### 2026-11-01 PySimAI 0.4.8 GeomAI Model Evaluation Report (MER)

- 依 `Evaluation and workflow integration` 及 `Model setup and training goals` 的本機 Markdown sidecar 整理 MER 下載入口、Chamfer distance／threshold、quality histogram、interpolation examples、Parameter Importance、離群檢查與定性幾何檢視。兩份對應 0.4.8 HTML 均確認包含關鍵章節文字；保留 stable URL 的服務端版本未知。
- 將 MER 指標與資料檢查拆為有界 complete 主題；更廣的「GeomAI 模型評估與非參數最佳化」仍 draft，未呼叫 SimAI 服務或設定跨專案接受門檻。


### 2026-11-01 LS-PrePost v261 Section Plane 斷面功能

- 以 PyMuPDF 直接核對 User’s Guide PDF physical Pages 550–560，並比對逐頁 Markdown；整理 FixS／FixM／Lagr plane 定義、四種建面方式、沿法向 cuts 與 clipping、斷面量測／線圖／force、section data 格式及 plane 定義存取。
- 依手冊註明 section force 需要 d3plot shell resultants，且可能受 `*DATABASE_EXTENT_BINARY` 控制；未目視核對圖示、未操作 LS-PrePost 或驗證輸出資料。


### 2026-11-01 optiSLang v261 MOP Solver C API 安裝目錄

- 核讀官方 2026 R1 `External Metamodel Solver Interfaces` Markdown 正文，整理 standalone 可執行檔、支援／不支援 Python-based metamodel 的 shared libraries、static libraries、header 及 C/C++ 範例檔位置。頁面列出的 header 名為 `hopsolver_api.h`，與產品目錄拼法不同，摘要保留原文並提示檢查實際安裝檔名。
- v261 頁面連結至 MOPSolver API 2023 R2 參考；不據此推定 ABI 相容。該 v261 Markdown source 沒有本機 HTML 對應檔；未載入 library、編譯範例或執行 solver。


### 2026-11-01 Motor-CAD PyMotorCAD internal／external scripting

- 比對 PyMotorCAD 0.8.8 local mirror 的 internal／external scripting HTML 與 Markdown sidecars；兩種格式皆包含入口與 callback 關鍵文字。整理 Scripting tab 的 current-instance 用法、外部 JSON-RPC 本機／HTTP remote 與 GUI 模式概述，並把 `Run` 的 top-level `main()` 與 `Run During Analysis` callbacks 分開說明。
- 記錄 thermal callbacks 的 initial／per-time-step main／final 時序，以及 `MessageDisplayState=2` 會關閉存檔／覆寫等重要 popup 的來源警告。將兩入口 overview 標 complete，增加 callback 有界 complete 子題；未連接或執行 Motor-CAD，未推定 external remote setup/security details。


### 2026-11-01 Discovery v261 Doc objects 與 geometry objects

- 依官方 Developer Guide `geo_doc_objects.md`（頁面最後更新 2026-03-09）補入 doc object 的 parent-child、moniker、update state 及 name／layer／visibility／color 等屬性；區分 modeler／geometry object 與 DesignBody／DesignCurve／DatumPlane 的文件及視窗呈現責任，也保留 graphics display primitive 可顯示但不是 doc object 的例外。
- 將此概念範圍標為 complete；未延伸至 API 建立方法或 update 順序，未執行 Discovery。來源為官方 Markdown page，本機無 HTML 轉換副本。



### 2026-11-01 PySpeos 0.9.2 existing service 與 Speos channel

- 比對 Use an existing service HTML／Markdown sidecar及 Speos API reference HTML／Markdown sidecar；整理 Speos() 預設 local channel、指定本機 port 的 default_local_channel()、insecure gRPC channel 範例、speos.client 狀態及 close() 語義。對 insecure transport 明確保留為文件示例，不作安全建議。
- 在來源清冊補列 Speos API reference；stable URL 的伺服器版本未知，產品 release 維持 unknown。將「既有服務連線及 client 狀態」標 complete；未啟動服務、執行 PySpeos 或核驗遠端連線。
- 增量更新全文索引後，以 product=speos 搜尋 default_local_channel/custom port 與 client/Connection Healthy 查詢；分別命中官方 API reference、既有服務 guide 及 Speos 字典，get_chunk 成功回取來源片段。索引 quick_check=ok，_needs_rebuild()=false。


### 2026-11-01 PyDYNA FieldSchema／CardSchema

- 對照兩份 PyDYNA API reference 本機 HTML 與 Markdown sidecar，核實 FieldSchema 的 name/type/offset/width/default/display_name 與轉換方法，以及 CardSchema 的 fields/name_to_index/from_fields/to_fields/get_index/KeyError。已把這個窄範圍列為 complete；PyDYNA 整體主題仍 draft。
- 以 product=lsdyna 搜尋 FieldSchema 與 CardSchema 欄位，命中字典及官方 API 正文，get_chunk 均成功。來源路徑為 ansys-dyna-core 0.12.1，stable URL 版本未知；未執行 API 或 LS-DYNA solver。


### 2026-11-01 optiSLang 2026 R1 SP03 postprocessing Python scripting

- 依官方 Developer Portal Markdown page（最後更新 2026-07-30）核對 generation／monitoring script 類型、預設與 custom directories、OSL_CUSTOM_COMMAND_SCRIPT_DIR／OSL_CUSTOM_EXECUTE_SCRIPT_DIR、toolbar configuration、Python console 與文字匯入示例。沒有對應 HTML sidecar；來源已由本機 catalog 索引。
- 將產品內建 postprocessing scripting 作為 bounded complete 子題；整體 Scripting/customization 仍 draft。特別記錄來源範例使用小寫 true 及 Postproceessing 拼字，不將原片段當成可執行 Python。
- product=optislang 查詢 OSL_CUSTOM_COMMAND_SCRIPT_DIR／OSL_CUSTOM_EXECUTE_SCRIPT_DIR 命中兩份官方 module sidecar 與字典，get_chunk 成功；text_import_non_interactive／show_as_button 查詢命中 API 正文與字典，get_chunk 成功。未啟動 optiSLang、未執行腳本或文字匯入。


### 2026-11-01 Mechanical、LS-DYNA 與 Speos 文件整理

- Mechanical：依 v261 Scripting Guide PDF physical pages 85–92、97、124–125、190，核對轉換 sidecar 文字並補入四個有界主題；PDF 與 sidecar 文字一致。接觸、結果與後處理、疑難排解三個父題仍為 draft，剩餘範圍列於 topics.csv。未啟動 Mechanical 或求解。
- LS-DYNA：依 v261 User’s Guide PDF physical pages 678–681、685–687 整理 ASCII／BinOut Basic 操作；另比對 PyDYNA 0.12.1 五個 option-card HTML 頁及 Markdown sidecar，五筆來源均已有本機檔案並登錄 sources.csv。父題 LS-PrePost 與 PyDYNA 仍為 draft；未啟動 GUI、執行 API 或 solver。
- Speos：完成 SDK／產品版本界線、launcher／PIM、授權與安全三個有界主題；相關 HTML 與 Markdown sidecar 的關鍵段落一致。stable URL 未證明服務端版本；未啟動服務或執行 API。
- 原始 PDF、HTML 與圖表均保留；本次重用已存在的轉換 sidecar，未執行批次轉檔，也未修改 REA 萃取內容。


### 2026-11-01 PDF／HTML 轉換盤點與待處理來源

- 以 `_catalog/documents.json` 核對本地原檔與轉換文字路徑：SpaceClaim 有 4 份 PDF；Mechanical 有 189 份 HTML、2 份 PDF；LS-DYNA 有 247 份 HTML、7 份 PDF；optiSLang 有 577 份 HTML；Speos 有 313 份 HTML、57 份可抽取 PDF。上述正文來源的原檔與 sidecar 路徑均存在，沿用既有頁碼 Markdown／HTML 文字，不重覆覆寫。
- 對 Speos 的 `RAL DESIGN StandardRGB (RGB).pdf` 執行既有 PDFium 擷取流程；單頁僅抽出 29 個字元，低於正文門檻。擷取器記錄失敗原因「PDF沒有可擷取正文，未執行OCR」，沒有產生可索引正文；原 PDF 保留，sources.csv 標為待 OCR／人工處理。色票圖像與色值表未驗證。
- 本次 HTML 以已有 HTML→Markdown sidecar 為準；來源 HTML bytes 均在本機，但沒有重新正規化上述 1,326 份 HTML。REA 萃取目錄不在本次轉換範圍。


### 2026-11-01 Mechanical／LS-DYNA／Speos RAG 抽查

- `product=mechanical` 查詢 `NewtonRaphsonResiduals` 命中官方 SolutionInformation 正文及字典；`product=lsdyna` 查詢 `OptionCardSet.active` 命中字典，`BinOut Basic Search Save` 命中 User’s Guide 與字典；`product=speos` 查詢 `0.9.2 version stable` 命中字典與官方 HTML。各代表結果均以 `get_chunk` 回取成功。`29 字元 PDFium 擷取` 亦可由 general scope 回查轉換缺口紀錄。
- Mechanical 多詞 AND 查詢 `CreateVector3D NewtonRaphsonResiduals` 回傳 0；分開查詢各 API 名稱時可命中字典／原文。搜尋以詞項 AND 為主，需避免把分散在不同段落的術語併成同一查詢。
- 該輪索引快照包含 596,557 份文件與 647,416 個 chunks；SQLite `quick_check=ok`，`_needs_rebuild()=false`。


### 2026-11-01 SimAI 與 optiSLang 單次模組整理

- SimAI：新增 6 個有界 complete 子題，六個父題保留 draft；本機 catalog 有 84 份正文（62 HTML／22 Markdown）及 1 份 template。新用到的 Optimization API HTML 為 SDK 0.4.8，原 `version/stable` URL 在 sources.csv 登錄 release unknown。catalog 有 42 個 0.4.8 版本化 HTML、另 20 個 unknown 路徑 HTML 與本機版本內容相同；unknown 標記保留。sources.csv 新增此 API 一列，CurrentUser 主題補 NPO 指南 30 天 token 期限引用。
- optiSLang：新增 6 個有界 complete 子題，5 個父題保留 draft；951 筆來源中 914 body_present、14 auth-restricted、6 權限不明、9 attachments、3 summary-only、3 repository／asset not copied、1 failed、1 metadata missing；所有非空 local_path 存在。SDK 1.7.0 不轉成產品 release。清冊中重複的 RootSystem 單筆 Design evaluation 合併，保留來源引用。
- 兩模組都核讀可用本機 HTML／Markdown／PDF sidecar；未呼叫 SimAI／optiSLang 服務、未建模或求解。原始文件與 REA 萃取內容保留。


### 2026-11-01 SimAI／optiSLang 模組 RAG 抽查

- SimAI：`upload_folder extract_data`、`confidence_score`、`ProcessGlobalCoefficient`、`get_runnable_predictions`、`max_displacement part_ids`、`MultipleErrors` 均命中至少一份字典或官方來源；代表結果以 `get_chunk` 回取成功。
- optiSLang：`create_placeholder_from_actor_property`、`IsTerminated IsConverged`、`LESSLIMITSTATE`、`HidSpecificOutputDataIntegrations`、`ScriptInterfaceVersion AbortMode`、`adapted_parameter_values` 均命中字典或官方來源；代表片段回取成功。`local domain channel` 命中官方頁及字典；`local_domain_channel` 與 `domain_channel` 原樣查詢為 0 hits，底線連寫不利於目前全文搜尋，改以空格查詢可定位。
- 最後一次 SQLite 線上備份增量更新 SimAI、optiSLang 字典與本狀態頁，`quick_check=ok` 且 `_needs_rebuild()=false`；原索引在檢查通過後才原子替換。未執行應用服務、plugin、DOE 或 solver。


### 2026-11-01 Avxcelerate／CFF 單次模組整理

- Avxcelerate：新增 8 個有界 complete 子題，5 個父題維持 draft。catalog 本機有 313 份 body_present（312 Markdown、1 PDF）；本輪補登 6 個原本未列於字典 sources.csv、但已存在 catalog／SQLite 的引用來源。保留 scheduling JSON `__all__`／正文 `_all_`、KPI `Datatype` 宣告／文字 `string` 兩組差異。secured User’s Guide／授權內容仍未取得。
- CFF（Common Fluids Format）：新增 5 個有界 complete 子題，並擴充 Metadata 子題；5 個父題維持 draft。本機索引有 89 份 CFF 正文（unknown 3、v251 7、v252 29、v261 50），來源路徑全存在；CFF 文件目錄另有 90 份 Markdown（含 README），原 sources.csv 是引用選集。本輪補登 6 個新引用來源，不宣稱完整 SDK／binary layout 已整理。保留 C++ target default／example、Windows `win64`／`winx64` 與 Linux `LIBRARY_PATH`／`LD_LIBRARY_PATH` 差異。
- 兩模組均核對本機官方 Markdown 與既有索引；未重轉來源、編譯、執行 runtime／DDS、或讀寫 CFF 檔案。REA 萃取內容未修改。


### 2026-11-01 Avxcelerate／CFF RAG 抽查

- Avxcelerate 查詢 `simulation reset`、`SensorDataNotifier shared memory`、`VariantMessage`、`input_open_scenario`、`KpiContent`、`Ubuntu Bazelisk` 均命中官方來源或字典；CFF 查詢 `hasTarget setTarget`、`Poly Face topology`、`Managed storage Simulation`、`HeavyweightReadMethod`、`GLIBCXX_USE_CXX11_ABI`、`getKeys Metadata` 均命中官方來源或字典。12 個代表結果皆以 `get_chunk` 回取成功，未記錄查詢失敗。
- 最後增量索引 Avxcelerate、CFF 字典與此紀錄；SQLite 完整性檢查通過、`_needs_rebuild()=false`。全域產品主題仍有其他 draft，這批只完成兩個模組的有界子題。


### 2026-11-01 ACP／ADR 單次模組整理

- ACP：新增 6 個有界 complete 子題，四個父題維持 draft。引用來源涉及 PyACP 0.4.1 HTML／tutorial；快取目錄 SDK 版本與 stable URL 分開記錄，sources.csv 新增 9 個既有 catalog 引用。保留 launch mode 數目差異及未收錄的 advanced selection rules tutorial；本機索引 3,844 筆 ACP source 全部 body_present、路徑存在。
- ADR：新增 6 個有界 complete 子題，四個父題維持 draft。PyDynamicReporting HTML 標記 0.10、快取目錄 0.10.6，不推定更精確 SDK release；sources.csv 新增 6 個 catalog 引用。40 筆 ADR indexed source 全為 body_present、路徑存在；viewer／websocket 來源是本機 Markdown，並未宣稱原 HTML 鏡像。
- 兩模組均未啟動服務、連線、GUI、傳輸資料、操作資料庫或執行 ACP 複材求解；REA 萃取內容未修改。


### 2026-11-01 ACP／ADR RAG 抽查

- ACP：`auto_transfer_files`、`WNUA`、`Reload Model`、`template_rule`、`recursive_copy linked_object_handling`、`MINIMUM_DISTANCE_SUPERPOSED` 均命中字典或官方來源，代表片段 `get_chunk` 成功。
- ADR：`item_table visualize_report`、`s_guid session filter`、`renderer showFit`、`HTTP REST security_token`、`reserve release stop server` 均命中字典或官方來源，代表片段 `get_chunk` 成功。合併查詢 `300s RemoteServiceScript` 回傳 0；分開查 `300s`、`RemoteServiceScript` 均命中來源並可回取片段，需避免將分散段落術語合併成 AND 查詢。
- 最後增量更新 ACP／ADR 字典與本紀錄後，SQLite `quick_check=ok`、`_needs_rebuild()=false`。未啟動 ACP／ADR runtime、viewer、websocket 或求解。


### 2026-11-01 Discovery／Rocky 單次模組整理

- Discovery：新增 6 個有界 complete 主題，4 個父題維持 draft；本機 catalog 有 81 筆 body_present Discovery 來源（v261 78、unknown 3），原文路徑均存在。本輪新增 21 筆引用來源至 sources.csv。保留 API.V22／v261、manifest host、ProgramData scope、`lsCoincident` 拼字等原文不確定處。
- Rocky：新增 6 個有界 complete 主題，4 個父題維持 draft；本機 catalog 有 614 筆 body_present Rocky 來源，來源路徑核對後新增 8 筆引用來源。PyRocky 0.6.2 與產品 v261 分開標示；保留範例多餘括號及 `skip_summary` 描述疑義。
- 兩模組使用既有本機 HTML／Markdown 正文與 v261 PDF 轉換成果，未重新轉換、啟動產品、執行腳本／solver；原始文件與 REA 萃取內容未修改。字典與來源清冊更新後將增量刷新全文索引。


### 2026-11-01 Discovery／Rocky RAG 抽查

- `discovery` 查詢 `API.V22` 命中 3 筆可回取結果；首筆 `ansys_77079e257cea08ad85806245` chunk 1（Api.V22.Extensibility;）。
- `discovery` 查詢 `SameAppDomain` 命中 3 筆可回取結果；首筆 `external_594489016365_discovery` chunk 1（| `assembly` | DLL 檔名或完整路徑；僅檔名時以 manifest 同目錄為基準。|）。
- `discovery` 查詢 `TransformToMaster` 命中 3 筆可回取結果；首筆 `ansys_9aeb7dfdbca4f63ee9b95679` chunk 1（ter = desFace.TransformToMaster;）。
- `discovery` 查詢 `ResolveSurvivors` 命中 2 筆可回取結果；首筆 `ansys_68aaccf780e3636c4d267a3b` chunk 0（---）。
- `discovery` 查詢 `TryParse` 命中 2 筆可回取結果；首筆 `ansys_09595c22db9a9f203f0fcb7e` chunk 0（---）。
- `discovery` 查詢 `lsCoincident` 命中 2 筆可回取結果；首筆 `ansys_581ae536c2c7edcaf66bef5a` chunk 0（---）。
- discovery 抽查 6/6 查詢有可回取結果；失敗／未覆蓋：無。
- `rocky` 查詢 `close_existing` 命中 3 筆可回取結果；首筆 `external_fe03bcb19312_rocky` chunk 0（Ansys Rocky 與 PyRocky 主題字典）。
- `rocky` 查詢 `GetStudy` 命中 3 筆可回取結果；首筆 `ansys_596122b6a8c4b3c1dfd7f326` chunk 2（dChanges](https://rocky.docs.pyansys.com/version/stable/api/ansys/rocky/app/ra_project/RAProject.html#RAProject.HasUnsav）。
- `rocky` 查詢 `delete_results` 命中 3 筆可回取結果；首筆 `external_fe03bcb19312_rocky` chunk 6（一讀取每個步階的極值；步階數由 `study.GetTimeSet()` 取得，結果依 `simulation_times` 繪製，時間單位為秒。曲線回傳的時間陣列與 Grid Function 步階時間是範例中各自提供的時間軸；不要省略單）。
- `rocky` 查詢 `Stress Tensor` 命中 3 筆可回取結果；首筆 `ansys_7d6defec331064b21be42abf` chunk 0（---）。
- `rocky` 查詢 `CUDA_PATH_V12_8` 命中 3 筆可回取結果；首筆 `ansys_1773ef903be72d660735157e` chunk 1（identified in the name of its zip file. It is paramount that you install a Rocky Solver SDK of the same version as the R）。
- `rocky` 查詢 `trigger_update_timestep` 命中 3 筆可回取結果；首筆 `external_fe03bcb19312_rocky` chunk 9（mensional factors 處理。 |）。
- rocky 抽查 6/6 查詢有可回取結果；失敗／未覆蓋：無。

檢索只確認關鍵詞命中及片段定位，不代表執行產品操作或驗證工程結果。


### 2026-11-01 TurboGrid／Lumerical 單次模組整理

- TurboGrid：新增 4 個有界 complete 主題，4 個父題仍 draft。catalog 有 13 筆來源：7 份正文 HTML（皆有 Markdown sidecar，正文全已登 sources.csv）及 6 個附件；13 個來源路徑和 7 個 sidecar 路徑均存在。6 個未索引範例附件已補入 sources.csv 並標 attachment。PyTurboGrid SDK 為 0.9.4，產品 release 未知；API reference 正文只有 321 個索引字元。README 的範例數量與 catalog 不一致，保留差異，不用 README 推定覆蓋。
- Lumerical：新增 4 個有界 complete 主題，4 個父題仍 draft。catalog 有 6 份 Markdown 正文，全部 body_present、release unknown、路徑存在；兩份 overview 是同一來源 URL 的包裝重複。沒有本機 PDF／HTML 或較深 API reference；既有官方頁 summary-only 本輪未重新連網核讀，記為缺口。
- 兩模組沿用本機來源與既有 sidecar，未重新轉檔、下載附件、執行範例或啟動產品；REA 萃取內容未修改。


### 2026-11-01 TurboGrid／Lumerical RAG 抽查

- `lumerical` 查詢 `CML PDK` 命中 3 筆可回取結果；首筆 `external_670e57979aa6_lumerical` chunk 0（Ansys Lumerical 主題字典）。
- `lumerical` 查詢 `PyLumerical MCP` 命中 3 筆可回取結果；首筆 `external_670e57979aa6_lumerical` chunk 1（fbd7`；release `unknown`）。[Module overview](../ANSYS_Document/Lumerical/unknown/guides_and_tutorials/OVERVIEW.md)（`ansys_）。
- `lumerical` 查詢 `LSL .mat` 未取得可回取結果。
- `lumerical` 查詢 `Lumopt optimization` 命中 3 筆可回取結果；首筆 `external_670e57979aa6_lumerical` chunk 5（te API](https://optics.ansys.com/hc/en-us/articles/15499581457811-Interop-Server-Remote-API)。入口文件及官方文章未給出此工作環境所安裝的 Lumer）。
- lumerical 抽查 3/4；未命中：LSL .mat。
- `turbogrid` 查詢 `PyTurboGrid client-server` 命中 2 筆可回取結果；首筆 `ansys_0b8557bb11e1fadc4bae08fb` chunk 0（---）。
- `turbogrid` 查詢 `AWP_ROOT` 命中 3 筆可回取結果；首筆 `ansys_d914c57d24cae259d553304f` chunk 2（ble, where）。
- `turbogrid` 查詢 `developer installation` 命中 3 筆可回取結果；首筆 `ansys_d914c57d24cae259d553304f` chunk 0（---）。
- `turbogrid` 查詢 `AxialFanMultiRow` 命中 3 筆可回取結果；首筆 `ansys_49caa5a2e377c83ff0b79d0a` chunk 1（tall_path}/tests/ndf/AxialFanMultiRow.ndf")）。
- `turbogrid` 查詢 `STAC TGMachine` 命中 3 筆可回取結果；首筆 `external_f574b3db0b72_turbogrid` chunk 7（s.pyansys.com/version/stable/examples/mbr_from_tginit_example.html) · `ansys_49caa5a2e377c83ff0b79d0a`。未執行範例或 TurboGrid。）。
- turbogrid 抽查 5/5；未命中：無。
檢索確認關鍵詞命中與片段定位；未執行產品、SDK 或範例附件。

- Lumerical 分開查詢 `LSL` 命中 1 筆可回取結果，首筆 `external_670e57979aa6_lumerical` chunk 2。
- Lumerical 分開查詢 `MATLAB` 命中 3 筆可回取結果，首筆 `ansys_d9ca5748e6576adf3a65eb0c` chunk 0。
合併查詢 `LSL .mat` 為 0 hits；此索引以詞項 AND 比對，分開查詢作為可用定位方式。


### 2026-11-02 Workbench／Minerva 單次模組整理

- Workbench：新增 7 個有界 complete 主題，既有 3 個 draft 父題與 1 個 pending_source_review 保留。catalog 有 4 筆 v261 body_present 來源：Scripting Guide PDF（1,466 頁）、ACT Guide PDF（248 頁）及兩份 Markdown；來源檔與 PDF page sidecar 均存在，引用來源已在 sources.csv。系統 PyMuPDF 對照 27 個 PDF physical pages 與 sidecar，126 項斷言、45 個本機連結、25 個頁碼 anchor 及 7 次 source chunk 回取通過。保留 Archive／Unarchive 範例參數差異及 callback XML 拼字差異；未執行 Workbench、ACT 或腳本。
- Minerva：新增 3 個有界 complete 主題；仍有 1 draft、1 source_limited、1 pending_source_review。catalog 僅 2 份 body_present Markdown，release unknown、路徑存在；兩份是同來源 URL 的正文與包裝副本，沒有本機 PDF／HTML。來源列示的 2025 R2 API 入口要求登入；未取得完整 endpoint、schema、authentication 或授權條款，未推定產品／server 版本。兩個來源均已登 sources.csv。
- 兩模組均沿用本機已轉換正文，沒有重新轉檔；REA 萃取內容未修改。


### 2026-11-02 Workbench／Minerva RAG 抽查

- `workbench` 查詢 `FailIfMissingFiles` 命中 3 筆可回取結果；首筆 `external_68e30270994b_workbench` chunk 3。
- `workbench` 查詢 `DesignPoint expression` 命中 3 筆可回取結果；首筆 `ansys_05b664ec1d5ee31846d738a4` chunk 1231。
- `workbench` 查詢 `onstatus isvalid` 命中 3 筆可回取結果；首筆 `external_68e30270994b_workbench` chunk 12。
- `workbench` 查詢 `global callback` 命中 3 筆可回取結果；首筆 `ansys_9b0d4ecb6d9a7614cd649d73` chunk 92。
- `workbench` 查詢 `task file callback` 命中 3 筆可回取結果；首筆 `external_68e30270994b_workbench` chunk 13。
- workbench 抽查 5/5；未命中：無。
- `minerva` 查詢 `HTTP APIs` 命中 3 筆可回取結果；首筆 `ansys_9e2f53776debdd8c64c64027` chunk 0。
- `minerva` 查詢 `language-agnostic` 命中 3 筆可回取結果；首筆 `ansys_9e2f53776debdd8c64c64027` chunk 0。
- `minerva` 查詢 `2025 R2 Sign-in required` 命中 3 筆可回取結果；首筆 `external_1db78d79ccfa_minerva` chunk 1。
- minerva 抽查 3/3；未命中：無。
抽查確認詞項命中及來源片段回取；未連線 Minerva 或執行 Workbench／ACT。


### 2026-11-02 ACT／Motor-CAD 單次模組整理

- ACT：新增 6 個有界 complete 主題；整合後 11 complete、3 draft、1 pending_source_review、1 source_limited。catalog 有 562,624 records：562,364 body_present、259 attachments、1 stub；全部來源路徑 562,624 個及 text_path 150,253 個存在。既有 coverage 的 6 個失敗 URL 與目前 catalog 實存 ZIP／附件分開記錄。修正兩處 PDF physical page：Extension Structure 為 25–26，ExtSample1 為 77–81；另補登原字典已有引用的兩筆未登錄正文。PDF 14 頁／64 項 sidecar 斷言、35 連結、16 頁碼 anchors、6 個新標題與 6 次 chunk 回取通過。全量 562k API 正文未逐條核讀。
- Motor-CAD：新增 7 個有界 complete 主題，整合後 11 complete、3 draft。catalog 81 筆（75 body_present：14 HTML、61 PDF；6 attachments），release unknown 80、v231 1；所有來源與文字路徑存在。補登 7 筆新引用正文。4 份 PDF 共 24 個實頁／108 項 sidecar 斷言、3 組 HTML／Markdown、30 個連結、4 頁碼 anchors 及 7 次 chunk 回取通過。保留版本相容、callback、熱暫態與轉子應力來源差異；未執行 Motor-CAD／MATLAB。
- 兩模組沿用已轉換的本機正文，REA 萃取內容未修改。


### 2026-11-02 ACT／Motor-CAD RAG 抽查

- `act` 查詢 `WBEX` 命中 3 筆可回取結果；首筆 `ansys_d646d1830d851f5a6ef9ff6b` chunk 61。
- `act` 查詢 `SimEntity` 命中 3 筆可回取結果；首筆 `ansys_75fae47d9fed3b94c1d2f5d5` chunk 365。
- `act` 查詢 `ProjectPath` 命中 3 筆可回取結果；首筆 `ansys_1923d3c4cab5171240223d67` chunk 0。
- `act` 查詢 `XML Editor` 命中 3 筆可回取結果；首筆 `ansys_7e12d0378fc3a1857e759d97` chunk 158。
- `act` 查詢 `Debug Mode` 命中 3 筆可回取結果；首筆 `ansys_7e12d0378fc3a1857e759d97` chunk 254。
- act 抽查 5/5；未命中：無。
- `motorcad` 查詢 `ActiveX` 命中 3 筆可回取結果；首筆 `ansys_ef5a2a1c92fc7291feb06e98` chunk 8。
- `motorcad` 查詢 `Motor-CAD Python API` 命中 3 筆可回取結果；首筆 `ansys_26587a776b4719f4c285e86b` chunk 0。
- `motorcad` 查詢 `duty cycle callback` 命中 1 筆可回取結果；首筆 `external_8a66c44e55d7_motorcad` chunk 6。
- `motorcad` 查詢 `specified-loss` 命中 2 筆可回取結果；首筆 `external_8a66c44e55d7_motorcad` chunk 7。
- `motorcad` 查詢 `rotor stress ratio` 命中 3 筆可回取結果；首筆 `external_8a66c44e55d7_motorcad` chunk 8。
- `motorcad` 查詢 `rotor notch` 命中 3 筆可回取結果；首筆 `ansys_c1f8ccd899a4f1a1a4a0ac59` chunk 12。
- motorcad 抽查 6/6；未命中：無。
抽查確認關鍵詞檢索與片段定位；未執行 ACT、WBEX、Motor-CAD 或 MATLAB。


### 2026-11-02 Ansys ID Portal／SSO 字典原文校正

- Portal：依本機 Portal Overview、membership sync guide、Entra setup 與 PAT guide 重核內容。六筆來源正文均 body_present 且路徑存在；topics.csv 的 4 個主題來源全部可回到 sources.csv。本次更正 Graph 權限為 `Group.Read.All`／`User.Read.All`，修正同步參數名稱，移除來源未規定的 secret 天數、`GroupMember.Read.All`、自建 token exchange payload 與未證實 account entitlement 分配細節。同步會移除差異成員；字典保留 dry-run 與 preserve-email 風險說明。
- SSO：兩筆來源正文均 body_present 且路徑存在；2 個主題引用均可回到來源清冊。移除來源未提供的 OAuth endpoint／grant payload、固定 1 小時 TTL、JWT 簽章機制與撤銷生效時間；改依官方 helper 描述 PAT→SSO token endpoint→Bearer access token 的高階流程。未登入、建立 PAT 或呼叫 API。
- Portal／SSO 原始來源 release 均 unknown；API endpoint schema、token request details 與服務端版本仍是來源缺口。REA 萃取內容未修改。


### 2026-11-02 Ansys ID Portal／SSO RAG 抽查

- `ansys_id_portal` 查詢 `Group.Read.All` 命中 3 筆可回取結果；首筆 `ansys_834cfbd2bfbd6a2f1759006a` chunk 4。
- `ansys_id_portal` 查詢 `transitiveMembers` 命中 2 筆可回取結果；首筆 `ansys_629ab7d33eaef48ee14b98ca` chunk 4。
- `ansys_id_portal` 查詢 `--preserve-email` 命中 3 筆可回取結果；首筆 `external_2be68212b850_ansys_id_portal` chunk 1。
- `ansys_id_portal` 查詢 `dry-run` 命中 3 筆可回取結果；首筆 `external_2be68212b850_ansys_id_portal` chunk 1。
- `ansys_id_portal` 查詢 `ASC Customer Administrator` 命中 3 筆可回取結果；首筆 `external_2be68212b850_ansys_id_portal` chunk 3。
- ansys_id_portal 抽查 5/5；未命中：無。
- `ansys_id_sso` 查詢 `Full Access` 命中 2 筆可回取結果；首筆 `external_35f5f118e399_ansys_id_sso` chunk 1。
- `ansys_id_sso` 查詢 `offline_access` 命中 1 筆可回取結果；首筆 `external_35f5f118e399_ansys_id_sso` chunk 0。
- `ansys_id_sso` 查詢 `Bearer access token` 命中 1 筆可回取結果；首筆 `external_35f5f118e399_ansys_id_sso` chunk 1。
- `ansys_id_sso` 查詢 `configurable expiration` 未取得可回取結果。
- ansys_id_sso 抽查 3/4；未命中：configurable expiration。
查詢只驗證詞項檢索與原文片段回取；未連線外部服務、未操作帳戶或 token。

- SSO 分開查詢 `configurable` 仍無可回取片段。
- SSO 分開查詢 `expiration` 命中 2 筆可回取片段。
`configurable expiration` 合併查詢未命中；分開查詢用於定位 scope／期限資訊。


### 2026-11-02 CFX／LS-PrePost 單次模組整理

- CFX：新增 6 個有界 complete 主題，保留 2 個 source_limited 父題。catalog 有 1,019 筆來源（1,015 body_present、4 attachments），全部 source path／text path 存在；本輪新增 4 筆 v251／v261 Modeling／Theory PDF 引用。已核讀兩版 Modeling PDF 共 40 個實頁，PDF／sidecar 160 項斷言、43 個連結、12 個頁碼 anchors、6 次 chunk 回取通過。同版 p89／94 的材料 CEL `p` 定義互相矛盾，字典保留矛盾而不判定正誤；手冊未逐章整理。
- LS-PrePost：新增 6 個有界 complete 主題，保留 3 個 source_limited 父題及 1 個 source_online_partial 範圍。兩份 v261 User’s Guide PDF／Markdown 已在本機，catalog 將它們歸為 lsdyna；2 個引用均已在 sources.csv，將 PDF `indexed_chars` 由錯值 631476 修正為 SQLite 實值 614393。PDF 12 頁、123 項來源斷言、23 個連結、15 個頁碼 anchors 與 6 次 chunk 回取通過。physical p1061 區分 `c=... -nographics`（仍需內部 graphics）與 `runc=...`（fully headless，僅 non-graphical commands）。
- 兩模組均沿用本機既有 PDF／Markdown sidecar，未重新轉檔、啟動 GUI 或執行 solver；REA 萃取內容未修改。


### 2026-11-02 CFX／LS-PrePost RAG 抽查

- `cfx` 查詢 `Timescale` 命中 3 筆可回取片段；首筆 `ansys_45ccf069fc36c5b2c371a978` chunk 1020。
- `cfx` 查詢 `Automatic Wall Treatment` 命中 3 筆可回取片段；首筆 `ansys_11057d652d987e26c91f9a51` chunk 218。
- `cfx` 查詢 `Initial Values File` 命中 3 筆可回取片段；首筆 `ansys_45ccf069fc36c5b2c371a978` chunk 285。
- `cfx` 查詢 `CEL p pressure` 命中 3 筆可回取片段；首筆 `ansys_c58523f59daaf38e134d31d7` chunk 5。
- `cfx` 查詢 `Frame Change Mixing Model` 命中 3 筆可回取片段；首筆 `ansys_7e4f7e457c8aac71e60ef45d` chunk 406。
- cfx 抽查 5/5；未命中：無。
- `ls-prepost` 查詢 `runc commandfile` 命中 1 筆可回取片段；首筆 `external_5fe2c477b67e_ls-prepost` chunk 0。
- `ls-prepost` 查詢 `-nographics` 命中 1 筆可回取片段；首筆 `external_5fe2c477b67e_ls-prepost` chunk 0。
- `ls-prepost` 查詢 `Fringe Integration Points` 命中 1 筆可回取片段；首筆 `external_5fe2c477b67e_ls-prepost` chunk 2。
- `ls-prepost` 查詢 `Section Plane` 命中 3 筆可回取片段；首筆 `agents_skills_structural-mechanics_ansys-ls-prepost_references_gui_result_review_sop` chunk 2。
- `ls-prepost` 查詢 `Separation shell thickness` 未取得可回取片段。
- ls-prepost 抽查 4/5；未命中：Separation shell thickness。
檢索確認詞項命中及來源片段定位；未啟動 CFX solver 或 LS-PrePost GUI。

- LS-PrePost 分開查詢 `Separation` 命中 2 筆可回取片段。
- LS-PrePost 分開查詢 `shell thickness` 命中 0 筆可回取片段。
合併查詢 `Separation shell thickness` 未命中；目前搜尋以詞項 AND 匹配，分開查詞可定位各自範圍。

-LS-PrePost `shell thickness` 與 `T1 T2` 兩個組合查詢均為 0 hits；`Separation` 可命中原文。原字典以 `T1`／`T2` 和繁中「殼厚」表述，這是目前詞面搜尋未覆蓋的同義詞缺口。


### 2026-11-02 LS-PrePost 內部 skill 來源清冊對齊

- 將 8 筆字典已引用的本機 skill/reference 文件加入 sources.csv，標示為 `skill`、release unknown、非官方手冊；sources.csv 與 topics.csv 的 reference 格式已一致化。每筆均對到 SQLite `docs_meta` 的本機索引欄位與現存檔案，不改其來源性質或官方文件狀態。
- 本輪新增來源列 8，更新引用列 4；此前確認的 CFX／LS-PrePost PDF source rows 保持 catalog 欄位與字數一致。


### 2026-11-02 AQWA／FENSAP-ICE 公開官方頁核讀

- AQWA：新增 7 個有界 complete 摘要；保留 2 source_limited、1 source_online_not_cached、2 source_online_partial 範圍。官方 v261／v2611 HTML 共 14 頁公開可讀，source_url、版本欄已補齊；新增 3 筆 wave directions、wave frequencies、diffraction settings metadata。Theory PDF 因 13,633,388 bytes 超出 web 擷取限制而未取得，未下載或 OCR。官方全文未存入本機索引，RAG 只會命中字典摘要／內部 skill。
- FENSAP-ICE：新增 7 個有界 complete 摘要；保留 1 source_limited、2 source_online_partial。v242／v261 官方 HTML 共 14 頁公開可讀，修正 4 筆舊 source metadata 的 URL／release，新增 10 筆摘要型來源列。中斷操作同頁對 cell state／Stop／Interrupt 的說明有矛盾，字典分開記載，不推定較新語義。官方全文未本機快取，索引只含摘要／內部 note。
- 內部 skill/reference 引用加入 sources.csv 並正規化 anchor；本輪新增／修復 source rows 共 17 筆、更新原 topic refs 5 列。根代理另直接打開 AQWA Wave Directions 與 FENSAP Interrupt 官方頁，確認章節標題、方向範圍及 Stop／Interrupt 描述可見；無登入提示。
- 未執行 AQWA／FENSAP、未下載或保存官方網頁全文，REA 萃取內容未修改。


### 2026-11-02 AQWA／FENSAP-ICE RAG 抽查

- `aqwa` 查詢 `Wave Directions` 命中 2 筆可回取片段；首筆 `external_49ed9e0d7767_aqwa` chunk 3。
- `aqwa` 查詢 `Forward Speed` 命中 2 筆可回取片段；首筆 `external_49ed9e0d7767_aqwa` chunk 3。
- `aqwa` 查詢 `Hydrodynamic Diffraction` 命中 3 筆可回取片段；首筆 `external_49ed9e0d7767_aqwa` chunk 4。
- `aqwa` 查詢 `Moonpool` 命中 3 筆可回取片段；首筆 `external_49ed9e0d7767_aqwa` chunk 4。
- `aqwa` 查詢 `Clear Generated Data` 命中 2 筆可回取片段；首筆 `external_49ed9e0d7767_aqwa` chunk 4。
- aqwa 抽查 5/5；未命中：無。
- `fensap_ice` 查詢 `Interrupt` 命中 2 筆可回取片段；首筆 `external_8682c431a164_fensap_ice` chunk 3。
- `fensap_ice` 查詢 `Reference Conditions` 命中 2 筆可回取片段；首筆 `external_8682c431a164_fensap_ice` chunk 3。
- `fensap_ice` 查詢 `CFL Relaxation` 命中 1 筆可回取片段；首筆 `external_8682c431a164_fensap_ice` chunk 4。
- `fensap_ice` 查詢 `Mesh Import` 命中 2 筆可回取片段；首筆 `external_8682c431a164_fensap_ice` chunk 1。
- `fensap_ice` 查詢 `Retain` 命中 2 筆可回取片段；首筆 `external_8682c431a164_fensap_ice` chunk 1。
- fensap_ice 抽查 5/5；未命中：無。
官方線上全文未進本機索引；上述是字典摘要或內部 skill/reference 的片段回取。


### 2026-11-02 SAF／Additive 單次模組整理與清冊整合

- SAF：依 22 個公開官方 HTML 頁面新增 7 個有界主題，並將兩個入口主題由 `source_limited` 更新為 `complete`；整合後 9 complete、1 source_limited。新增 13 筆線上摘要來源（release unknown、全文未本機快取），topics.csv 引用均可回到 sources.csv。Ubuntu 20.04/22.04 與 22.04/24.04 表格差異、`my-solution`/`my_solution` 範例差異均保留。完整 API、企業套件及離線全文仍受限。
- Additive：依 11 個公開 v261 官方 HTML 頁及 Tutorials PDF 公開頁面整理 8 個有界主題；兩個來源／全面覆蓋父題維持 `source_online_partial`。修復 3 筆來源 metadata、新增 10 筆來源列；12 筆為官方頁面摘要、1 筆 v251 PDF 因 13,204,800 bytes 擷取限制標為 `source_online_not_cached`。78 實頁 v261 Tutorials PDF 的特定校正／燒結續篇要求 Ansys credentials；未登入或保存全文。
- 根代理整合後檢查 sources.csv document_id 與 topics.csv product/topic 全域唯一，兩模組的 topic source IDs 均可解析；來源摘要尚未包含官方全文。Module pass 報告及整合前清冊備份存於 `../maintenance/knowledge_dictionary_passes/2026-11-02/`，不放入 RAG 語料根目錄。整合後 SAF 6/6、Additive 8/8 代表詞查詢均成功 `get_chunk`；正式索引 `docs_meta=596,557`、`chunks=647,559`，SQLite `quick_check=ok`、`index._needs_rebuild()=false`，未索引交付報告。REA 指定路徑未變更。


### 2026-11-02 ICEM CFD／Reaction-CHEMKIN 單次模組整理與清冊整合

- ICEM CFD：核讀 16 個公開 v261 官方 HTML，新增 9 個有界技術主題並更新來源覆核；Apple Xgrid 2004 PDF 原件內容已確認不屬於 ICEM，sources.csv 改列 general，正式文件索引原分類已是 general。新增線上摘要來源 16 筆，release v261（頁尾 Release 2026 R1），全文未快取。整合後 10 complete、1 source_online_partial。
- Reaction/CHEMKIN：核讀 14 個公開 v261 官方 HTML 與本機 MFL PDF 的指定頁；新增 8 個有界主題，原 MFL 全面完成項改為 pending_source_review、CHEMKIN 指南缺來源項改為 source_online_partial。更正 Tier 1/2 誤記，移除無來源的物種數、統一 5% 門檻與加速推估；保留 MFL p20／23 的 PAH 分級差異。新增官方摘要來源 13 筆，原 MFL release unknown。整合後 8 complete、1 pending_source_review、1 source_online_partial。
- 合併兩份模組來源／主題 upsert 後，sources.csv 的 5,668 個 document_id 及 topics.csv 的 582 個 product/topic 鍵皆唯一；兩模組主題引用均能對應來源清冊。官方 HTML 正文未本機快取；範圍及個別來源見[ICEM CFD 交付紀錄](../maintenance/knowledge_dictionary_passes/2026-11-02/icem_cfd.md)與[Reaction/CHEMKIN 交付紀錄](../maintenance/knowledge_dictionary_passes/2026-11-02/reaction_chemkin.md)。REA 指定路徑未變更。


### 2026-11-02 AnsysEM／EduPack 單次模組整理、轉換與 RAG 同步

- ansysem：complete=16, pending_version_review=1；來源列 27 筆。
- edupack：complete=10, pending_source_review=1, source_online_partial=1；來源列 1503 筆。
- AnsysEM 本機已轉換正文核讀 3 份歷史 PDF；SHA-256 9 項、頁標記 179 個、Markdown 本機連結 29 個通過核對。SPICE3f3／CMA 頁面版本可確認；Mechanical Thermal LTI ROM PDF 封面標 Simplorer 18.2、p.5 寫 R18.0，清冊保留 `pending_version_review`。
- EduPack 核對 README/catalog、1,491 個 HTML 輸出及 manifest；輸出雜湊全數吻合，1,490 頁有正文，另 1 筆為附件。抽看 v261 公開 HTML、Attribute Notes 與 Science Notes；完整逐頁、圖表公式及 Reference 仍未覆核，狀態保留 `pending_source_review`／`source_online_partial`。
- 合併後 sources.csv 為 5,675 筆、topics.csv 為 594 筆；document_id 與 product/topic 鍵唯一。新增模組引用均有來源列；全庫另有一筆舊有 optiSLang dangling source ref（`ansys_39c0d2548da6909818ff97d5`），在整合前清冊備份也已存在，本輪未修改。
- 暫存 SQLite 以正式索引副本更新 AnsysEM／EduPack 字典正文，代表查詢 AnsysEM 7/7、EduPack 8/8 均成功取得搜尋結果並 `get_chunk`，含 PDF／HTML 本機路徑。後續把本紀錄一併納入索引，驗證後原子替換正式資料庫。
- SQLite 當下唯讀連線正常，`BEGIN IMMEDIATE` 可取得並 rollback；未發現 WAL/SHM/journal。過往暫存重建程序曾持有鎖，但當時 Restart Manager 查 PID 失敗，因此歷史持鎖 PID 仍未知；本輪未終止任何程序。
- 模組報告與清冊變更前備份存於 `../maintenance/knowledge_dictionary_passes/2026-11-02/`；REA 相關檔案未納入。


### 2026-11-02 ACT／CFX 單次模組整理與 RAG 同步

- ACT 本批整合 11 組模組 upsert，另補列 catalog 已索引的 `ExternalCADBridge_documentation.pdf`（ID `ansys_0f527f2062391ed69bc74efa`）；其來源 PDF SHA-256 與 documents.json 相符，canonical v4 sidecar 有 14 頁，版本保留 unknown、未引用為已完成主題。ACT 最終 15 complete、1 source_limited；三版 ZIP 各 135 個檔案逐一對照解壓目錄 hash 相同，CRC 正常。依七個 ACT PDF 的 canonical `text_path` 核對共 7,375 個 PDF Page 標記。字典 22/22 本機連結存在。
- CFX 整合 4 個來源 upsert、14 個主題 upsert，主題 26 complete、2 source_limited。既有 1,010 個 HTML 的 2,020 個來源／Markdown hash、四份 PDF 12 項 SHA-256 與 2,292 個頁標題依交付報告通過；主代理另核對字典 92/92 本機連結、61/61 PDF page anchor。
- 合併後 sources.csv 5,681 筆、topics.csv 606 筆，document_id 與 product/topic 鍵全域唯一；ACT／CFX 新主題的來源 ID 均可解析。另有一筆舊有 optiSLang source ref 缺列（`ansys_39c0d2548da6909818ff97d5`），未由本批引入。
- 暫存索引代表搜尋及 `get_chunk`：ACT 8/8、CFX 10/10 成功，可回到字典或本機文件；正式 SQLite 已以暫存副本同步本節與兩份字典並原子替換；PRAGMA quick_check=ok，docs_meta=596,557、chunks=647,591，index._needs_rebuild()=false；正式庫 ACT 8/8、CFX 10/10 代表查詢皆搜尋及 get_chunk 成功。回復副本：docs/Documentation_clean/docs_index.sqlite.backup_before_act_cfx_20261102。
- 當前全庫主題狀態：complete=567, pending_physical_validation=1, pending_source_review=4, pending_version_review=1, source_limited=21, source_online_not_cached=1, source_online_partial=11。仍非 complete 的產品共 21 個：act, additive, ansysem, aqwa, cfx, circuit, edupack, emit, error_catalog, fensap_ice, hfss, icem_cfd, ls-prepost, minerva, pcb_warpage, polyflow, pyansys, reaction_chemkin, saf, thermal, workbench。
- 模組報告與 CSV 更新前備份放於 `../maintenance/knowledge_dictionary_passes/2026-11-02/`；原始 PDF／HTML 與既有轉換未重寫。REA 萃取與原始資料未納入本批。


### 2026-11-02 AQWA／LS-PrePost／Workbench／Minerva 單次模組整合

- AQWA：18 complete、3 source_online_partial、1 pending_source_review。23 個官方 HTML 頁面核讀，字典只收可核對摘要；官方 Theory PDF 仍因 13,633,388 bytes 超過本機擷取限制，沒有本機 catalog/body 可補轉。暫存 RAG 10 組組合詞查詢有 9 組直接命中；`Hydrostatic Equilibrium buoyancy` 未命中，縮為 `Hydrostatic Equilibrium` 後搜尋及 get_chunk 成功，`buoyancy` 單詞仍無命中。
- LS-PrePost：19 complete、3 source_limited、1 source_online_partial。7 個 v252 官方 HTML 摘要已加入來源清冊；本機 v261 PDF／canonical sidecar 保持 `lsdyna` 產品分類。字典 56 個連結及 28 個 PDF 頁錨點經主代理核對；暫存 RAG 10/10 成功搜尋並 get_chunk。
- Workbench：17 complete、1 source_limited。兩份 v261 PDF 共 1,714 頁；主代理核對來源 PDF SHA 與 catalog 相符、41/41 個本機連結存在。暫存 RAG 8/8 成功。
- Minerva：4 complete、1 source_limited、1 source_online_partial、1 pending_source_review；本機僅兩份 Markdown，無 PDF／HTML 可轉換。暫存 RAG 5/5 成功。官方 Connect 頁面確認 Minerva Transfer Client 可存取 Minerva SDK；完整 API index 的登入正文未取得，主代理直接開啟 `minerva.md` 也不可用。
- 暫存索引驗證：AQWA／LS-PrePost／Workbench／Minerva 合計 32/33 首選查詢可回 chunk；AQWA 的單一 AND 查詢失敗已保留，縮窄查詢可回片段。四模組字典及本狀態紀錄完成同步後，正式 SQLite 通過 `quick_check` 與 rebuild guard；正式計數見各模組交付報告。
- 合併後 sources.csv 5,707 筆、topics.csv 629 筆，鍵唯一；本批新增／更新主題引用均能解析。仍有一筆既有 optiSLang source ID 缺列。全庫主題狀態：complete=591, pending_physical_validation=1, pending_source_review=4, pending_version_review=1, source_limited=20, source_online_partial=12。非 complete 產品 21 個：act, additive, ansysem, aqwa, cfx, circuit, edupack, emit, error_catalog, fensap_ice, hfss, icem_cfd, ls-prepost, minerva, pcb_warpage, polyflow, pyansys, reaction_chemkin, saf, thermal, workbench。
- 模組報告及清冊更新前備份位於 `../maintenance/knowledge_dictionary_passes/2026-11-02/`。未修改原始文件、REA 萃取或執行任何產品／求解。


### 2026-11-02 FENSAP-ICE／PyAnsys／Circuit／EMIT 單次模組整合

- FENSAP-ICE：17 complete、2 source_online_partial；核讀 10 個 v261 官方 HTML，頁尾 Release 2026 R1。本機沒有可補轉 PDF／HTML；官方全文仍未離線快取。
- PyAnsys：8 complete、1 source_limited；核讀 13 個官方 HTML，產品 metapackage 2026.1.3 與 Ansys product release 分開記錄；sources.csv 新增／更新 16 列，含第三份本機 Sphinx template，無 PDF／HTML 待轉。
- Circuit：14 complete、1 source_limited；1152 頁 Scripting Guide PDF 依封面確認 v261，原件／canonical 轉換 hash 與 14 頁錨點核對；25 個本機連結皆存在。`ansys_9562597e2be9167330e444dd` 從 general 改為 circuit，catalog 原標 general、正式 SQLite 已有 circuit override，文件標題與封面證據支持此更正。官方 5 個 Help HTML 核讀、另 2 個直接開啟失敗。
- EMIT：15 complete、1 source_limited；10 份 PDF 共 569 頁標記、30 項 hash 核對及 60 個本機連結依模組報告通過；主代理再核對 31 個 PDF 頁錨點。兩個 PDF 來源保持 general，八個 tutorial 保持 ansysem；新增兩個官方 v261 HTML 摘要。
- 合併後 sources.csv 5,740 筆、topics.csv 663 筆，主鍵唯一；四模組新增／更新主題引用均可解析。另有既有 optiSLang dangling source ref `ansys_39c0d2548da6909818ff97d5`。全庫狀態：complete=627, pending_physical_validation=1, pending_source_review=4, pending_version_review=1, source_limited=18, source_online_partial=12；非 complete 產品 21 個：act, additive, ansysem, aqwa, cfx, circuit, edupack, emit, error_catalog, fensap_ice, hfss, icem_cfd, ls-prepost, minerva, pcb_warpage, polyflow, pyansys, reaction_chemkin, saf, thermal, workbench。
- 四份字典更新後，以四產品篩選、scope=all 對正式 SQLite 搜尋並逐筆 get_chunk：FENSAP-ICE 8/8、PyAnsys 8/8、Circuit 10/10、EMIT 8/8，共 34/34；Circuit 查詢可回到 circuit 分類的 1152 頁 PDF，EMIT 依 general／ansysem 既有分類回傳。正式索引原子替換後 docs_meta=596,557、chunks=647,627、PRAGMA quick_check=ok、index._needs_rebuild()=false；替換前正式檔 BEGIN IMMEDIATE 於 2 秒 timeout 內取得並 rollback，替換後無 WAL／SHM／journal 側檔。正式檔與替換前備份長度不同符合本批索引更新；本機程序清單未見 python／sqlite 工作程序，未發現目前持鎖程序；先前鎖定的歷史持有者仍無法確認，不對其 PID 歸因。備份及各模組報告位於 `../maintenance/knowledge_dictionary_passes/2026-11-02/`。未修改 REA、原始文件或 PDF／HTML 轉換原件，未執行產品／求解。


### 2026-11-02 HFSS／Thermal 單次模組整合

- HFSS：12 complete、1 source_limited；核讀 6 個 v261 官方 HTML。5 份 v261 PDF 共 4,430 頁，canonical 與同名 Markdown 已存在；15 項來源／轉換 SHA、8,860 個副本頁標記、43 個本機連結、20 個頁錨點及 24 個代表頁依交付紀錄通過。沿用既有轉換，沒有重轉或覆寫。
- Thermal：14 complete、1 pending_source_review、1 source_limited；本機 Thermal catalog 為 0。沿用既有 Motor-CAD 17 頁 PDF canonical 與 3 份 System Coupling v261 Markdown；核讀 12 個公開官方 HTML，其中 Motor-CAD v261 兩個網址不可存取，release 不推定。34 個本機連結、5 個頁錨點及 11 個 PDF 實頁依交付紀錄通過，無新轉換輸出。
- sources.csv 為 5,761 筆、topics.csv 為 682 筆，鍵唯一；HFSS／Thermal 主題 `sources.csv#document_id` 均可解析。全庫主題狀態：complete=646, source_limited=17, source_online_partial=12, pending_source_review=5, pending_version_review=1, pending_physical_validation=1；非 complete 產品共 21 個。
- 正式 SQLite 對 HFSS／Thermal 以 product 篩選、scope=all 執行代表查詢並逐筆 get_chunk：HFSS 10/10、Thermal 10/10，共 20/20，未命中 0。索引 `docs_meta=596,557`、`chunks=647,636`、`PRAGMA quick_check=ok`、`index._needs_rebuild()=false`。正式檔替換前 `BEGIN IMMEDIATE` 在 2 秒 timeout 內取得並 rollback，隨後同卷原子替換成功；替換後未見 WAL／SHM／journal。檔案備份為 `../Documentation_clean/docs_index.sqlite.backup_before_hfss_thermal_20261102`。本機程序檢查未見 python/sqlite 持鎖程序；早先未知鎖的歷史持有者仍無法判定。沒有覆寫原件或既有轉換，REA 萃取內容未納入；模組報告與清冊更新前備份位於 `../maintenance/knowledge_dictionary_passes/2026-11-02/`。


### 2026-11-02 Error Catalog／PCB Warpage 單次模組整合

- Error Catalog：8 complete、4 pending_source_review、1 source_limited。四份內部 Markdown 筆記共44個案例；本機沒有PDF/HTML輸入，未新增轉換。核讀10個官方主來源，修正ERR-IP-005／007混用並移除未證實修復行為。14 source／13 topic upserts。
- PCB Warpage：11 complete、1 pending_physical_validation、1 source_limited。模組catalog與其skill目錄沒有本機PDF/HTML可轉；兩份IPC公開PDF只核讀封面／目錄／scope，未下載全文。核對外部使用者工作簿／CSV與腳本靜態行為；solver未完成的歷史log不當驗收。22 source／13 topic upserts。
- 清冊合併後 sources.csv 為5,797筆、topics.csv為698筆，鍵唯一。本輪新增／更新topic的 `sources.csv#document_id` 均可解析。全庫狀態：complete=658, source_limited=17, source_online_partial=12, pending_source_review=9, pending_version_review=1, pending_physical_validation=1；仍有21個產品包含未完成主題。
- 正式 SQLite `docs_meta=596,557`、`chunks=647,650`、`PRAGMA quick_check=ok`、`index._needs_rebuild()=false`。Error Catalog 正式查詢/get_chunk 10/10。PCB Warpage 主查詢 9/10；`export_files PCB_STACKUP_DIR` 長AND查詢未命中，拆成 `PCB_STACKUP_DIR` 與 `export_files=False` 後各自搜尋及get_chunk成功（替代 2/2）。這表示該組合詞未命中，不代表其他單詞失敗或主題未涵蓋。字典連結 Error Catalog 20/20、PCB Warpage 41/41存在。正式檔 `BEGIN IMMEDIATE` 於 2 秒內取得後 rollback，原子替換成功；替換後沒有 WAL／SHM／journal。替換前副本 `../Documentation_clean/docs_index.sqlite.backup_before_error_catalog_pcb_warpage_20261102`。本機程序檢查未見 python/sqlite 持鎖程序，早先未知鎖的歷史持有者仍無法判定。原始內部筆記、工作簿／CSV、腳本、求解資料與REA萃取未修改；來源限制及分享範圍詳各模組報告。


### 2026-11-02 Polyflow 單次模組整合

- Polyflow：11 complete、1 source_limited；核讀15個官方HTML URL（1目錄、14正文），涵蓋v242與v261。7筆舊來源metadata補URL／版本，新增目錄與內部note追溯，共19 source／12 topic upserts。
- 本機Polyflow目錄只有README；product catalog、PDF、HTML及既有轉換皆為0，因此沒有轉檔輸出。v261 Classic PDF線上取得失敗（20,207,926 bytes超過擷取限制）；Workspace rheometry頁面無法直讀，release保留unknown，正文未推測。
- sources.csv=5,808筆、topics.csv=707筆，鍵唯一；本批topic source refs均可解析。全庫狀態：complete=667, source_limited=17, source_online_partial=12, pending_source_review=9, pending_version_review=1, pending_physical_validation=1；21個非complete產品都有本輪或先前的模組交付紀錄，來源未足項仍保持原狀態。
- Polyflow首輪11個建議查詢中4/11成功搜尋並get_chunk；7個長AND查詢因字典以中文表述或未含所有英文詞而未命中，包括 `Cross law plateau 曲率`、`White-Metzner high shear oscillations`、`Picard iterations viscosity variations`。改用逐字符合正文的較窄查詢 `subdomains 300`、`Cross-law index`、`PTT differential viscoelastic`、`MKS Fluent mesh`、`Picard iterations` 等，11/11成功。長AND未命中及拆窄策略保留在報告，不把摘要等同完整官方全文索引。正式 SQLite 最終為 `docs_meta=596,557`、`chunks=647,651`、`PRAGMA quick_check=ok`、`index._needs_rebuild()=false`。正式檔原子替換成功，替換前 `BEGIN IMMEDIATE` 可取得後rollback，未見WAL／SHM／journal；替換前備份為 `../Documentation_clean/docs_index.sqlite.backup_before_polyflow_20261102`。替換前本機程序檢查未見python/sqlite持鎖程序，舊鎖的歷史持有者仍無法判定。沒有保存不可取得PDF／HTML全文，未修改REA或原件。模組報告及清冊整合前備份位於 `../maintenance/knowledge_dictionary_passes/2026-11-02/`。
