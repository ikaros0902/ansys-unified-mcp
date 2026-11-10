# 文件整併與 REA 工作計畫

日期：2026-10-29。下方保留執行初期的盤點快照；請以文件末尾的執行狀態更新判讀目前結果。

## 目標與目前證據

將 `ANSYS_Document/` 與 `Documentation_clean/` 整理至 `docs/`。將 `docs/` 的 PDF 和 HTML 轉為 Markdown。處理重複 PDF。盤點並萃取尚未處理的 ANSYS 模組。

唯讀盤點發現 `ANSYS_Document/` 有 623,907 個檔案，其中 HTML 424,158、Markdown 198,258、PDF 269。`Documentation_clean/` 有 210,785 個檔案，其中 Markdown 210,780，另有 SQLite、journal、view 和 subgraph 資料。`docs/` 現有 247 個檔案。此為當次掃描結果，不包含完整雜湊核對。

現有計畫記錄 ANSYS_Document 的 424,158 個 HTML 來源及 269 個 PDF 的轉換清冊。該結果不涵蓋整個 `docs/` 和 `Documentation_clean/`。零位元組 HTML、掃描型 PDF 和轉換品質仍須列為缺口。參考 [既有計畫](FOLDER_TREE_REORGANIZATION_PLAN.md) 與 [文件維護流程](../maintenance/ANSYS_DOCUMENT_MAINTENANCE.md)。

REA 現有 55 個 managed snapshot 與 47 個候選檢查結果的母體不同。既有清冊的 1,172 和 1,288 個候選也未統一口徑。不能以這些數字宣稱全部產品或全部 API 已完成。參考 [REA 證據](../api_inventory/REA_EVIDENCE.md)與[來源盤點](../maintenance/ANSYS_SOURCE_INVENTORY.md)。

## 執行原則

- 保留來源子樹及版本。先建立來源、目的、大小和 SHA-256 清冊。分批搬遷，核對目的內容後才處理來源。不得覆寫衝突檔。
- SQLite、journal、view、subgraph 先判定是否為活躍資料或可重建產物。停止相關寫入並確保一致的備份，再決定目的地。不得將活躍 journal 當普通檔案搬走。
- 先檢查目標路徑的 Git 忽略狀態。確認受限原件與衍生內容仍限本機，並依 [公開發佈檢查](../maintenance/PUBLICATION_REVIEW.md) 處理。保留既有追蹤狀態與使用者修改。
- PDF／HTML 原件保留至轉換、引用及備份核對完成。轉換清冊逐項記錄來源 hash、輸出、狀態、工具與限制。空檔、掃描頁與失敗項明確列出，不以空白 Markdown 充作成功。
- 只將 SHA-256 相同且內容核對一致的 PDF 視為完全重複。保留一份，先更新引用並準備可還原備份，再移除多餘副本。不同版本、不同 hash 或相似頁面列為人工審查，不自動移除。原件的保留策略須涵蓋轉換結果與索引來源。
- REA 先定義全部目標產品及版本，逐產品建立狀態表。依實際安裝、模組路徑及 hash 建立候選母體，區分 managed、native、第三方與未辨識來源。native 另列適用方法或缺口，不能用 managed metadata absent 當作沒有 API。先核對工具身分與實際授權範圍。缺檔、工具不可用、授權未確認或分析失敗均列缺口，不推定完成。此工作不包含 ANSYS 求解。

## 工作分工與依賴

實際可同時運作的代理數受執行環境限制，分批派工。每項工作完成後由整合者核對證據。必要時由未參與實作的 reviewer 獨立驗收。

| 任務 | 負責範圍與交付 | 前置 |
| --- | --- | --- |
| T1 清冊 | 全量路徑、大小、hash、類型與來源狀態；列出預計目的路徑及衝突。 | 無 |
| T2 路徑與保護 | 查核 ignore、設定、呼叫端、連結和索引；列出遷移與回復方案。 | T1 |
| T3 文件搬遷 | 分批搬遷兩個來源，保留子樹；核對數量、hash、衝突與引用。修改受影響的預設路徑、環境變數和呼叫端。SQLite 等資料先依其狀態處理；需重建時先更新 catalog，再重建索引。 | T1、T2 |
| T4 HTML 轉換 | 清查 `docs/` 全部 HTML，沿用可信既有成果，補齊轉換及逐檔清冊，列失敗項。 | T3 |
| T5 PDF 轉換 | 清查 `docs/` 全部 PDF，沿用可信既有成果，補齊轉換及逐檔清冊，列掃描頁與失敗項。 | T3 |
| T6 PDF 去重 | 以 hash、完整內容、版本與引用建立候選；備份、核對後分批移除確定副本，保留清單與回復方式。 | T3、T5 |
| T7 REA 母體 | 盤點已安裝產品及候選 DLL，對齊既有清冊、版本、hash、產品映射及工具和授權狀態。 | 無 |
| T8 REA 萃取 | 對 T7 中可執行且已獲授權的來源分批靜態萃取。記錄命令、工具版本、輸入 hash、結果、失敗及快照。 | T7 |
| T9 整合驗收 | 對搬遷、轉換、去重、路徑與 REA 結果做獨立抽查，執行受影響的行為測試，彙整未完成項。 | T4、T5、T6、T8 |

`T4` 和 `T5` 可分開執行，寫入目標與清冊須隔離。`T7` 可與文件工作並行。若 T8 遇到授權或工具阻擋，保存缺口並報告，不能將 T9 記為全數通過。

### 本次 subagent 分工（8 位）

| Subagent | 工作範圍 | 結果 |
| --- | --- | --- |
| `inventory` | 來源文件與目標路徑清冊、差異盤點 | 完成 |
| `path_migration` | 搬遷路徑、索引與引用更新 | 完成 |
| `inventory_execution` | 執行分批清冊核對與搬遷工作 | 完成 |
| `path_review` | 獨立檢查路徑、引用及遷移結果 | 完成 |
| `conversion` | HTML／PDF 轉 Markdown 與失敗項清冊 | 完成，保留明列的來源例外 |
| `dedup` | PDF 重複內容辨識、備份及移除證據 | 完成 |
| `rea_scope_audit` | REA 範圍與來源／雜湊獨立稽核 | 完成；10 個 PE 解析失敗仍列缺口 |
| `rea_gap_audit` | 文件、索引及 REA 缺口獨立檢查 | 完成 |


## 驗收與回復

1. 每個來源檔均有目的路徑、hash 和狀態，所有搬遷碰撞已解決或明列。驗證來源及目的數量與 hash。
2. 每個 PDF／HTML 均有 Markdown 或具體失敗原因。抽查正文、頁碼、表格及圖片缺口。確認索引能讀取新路徑。
3. 每筆移除均有相同內容證據、保留路徑、引用更新、備份與還原步驟。無法確認者保留。
4. REA 候選逐一有來源、版本、hash、分析狀態與輸出，並明列缺檔、無授權及失敗項。樣本與原始 metadata 核對。產品映射不等於官方支援或完整 API。
5. 實測路徑設定、文件查詢與受影響測試。列出未測範圍，不用工具成功訊息代替行為證據。

清冊完整只代表所有項目均有狀態。轉換或 REA 全部完成須所有範圍內的項目成功，且通過適用的品質核對。任何失敗、授權或工具缺口都使對應工作保持未完成。

執行初期快照：`ANSYS_Document` 與 `Documentation_clean` 已移至 `docs/`。兩份 SHA-256 完全相同的 PDF 已備份並移除一份副本。ANSYS catalog 有 448,224 份文件；HTML manifest 記錄 23,253 份轉換及 56 份純文字 fallback，並有一份 0-byte HTML 失敗。PDF 清冊有 268 份抽取成功、一份掃描型 PDF 待 OCR。docsearch 索引有 448,052 筆 docs_meta、447,829 筆 catalog 來源已驗證；SQLite `integrity_check` 為 `ok`，舊根目錄 source_path 數為 0。`Mechanical` 查詢回傳新根目錄來源。另核對本機 66 份 REA JSON：55 份 managed metadata complete、8 份 absent、3 份只有 artifact identity；66 份都有可定位 DLL 且雜湊相符。再以 REA 6.0.0 對 17 個不同安裝路徑的 DLL 執行 `inspect-managed-members`，17 個命令均成功，metadata complete，輸入與輸出 hash 相同，共回報 8,886 個 TypeDef 與 52,102 個 MethodDef。完整證據位於被忽略的 `.runtime/rea-audit-20261029/`。REA 證據仍未定義完整產品/版本母體，也未盤點所有安裝樹元件。全量檔案雜湊、轉換逐項品質與完整行為驗收仍待處理。

## 2026-10-29 執行狀態更新

### 文件整理、轉換與 PDF 去重

- `ANSYS_Document/` 與 `Documentation_clean/` 已移至 `docs/` 下，舊根目錄已不存在。catalog 與工具預設路徑已更新。
- HTML 清冊涵蓋 424,158 個來源：400,904 份沿用既有 Markdown，23,197 份新轉換，56 份以純文字保存，1 份 0-byte HTML 失敗。所有 23,253 份新產生或 fallback 的 Markdown 輸出均存在。失敗項是 `ACT/v261/archives/ansys-zip-ro3no34_/Mechanical/Reference.methode.Ansys.ACT.Automation.Mechanical.MappingValidation.RemoveParameter.html`。
- PDF 清冊涵蓋原始 269 筆：258 筆抽取成功，10 筆重複內容已去重，1 筆掃描 PDF 尚無 OCR。10 筆包括 2 組來源 SHA-256 相同的副本，以及 8 組頁數和逐頁 render hash 相同的 PDF。移除前已備份原件和對應 Markdown；PDF 參考索引保留別名並指向保留版本。
- 初次執行狀態曾將 RAL 掃描 PDF 記為 OCR 工具不可用。後續確認本機 EasyOCR 可執行，但輸出未通過可讀性檢查；Markdown 已改嵌入頁面影像並記錄限制。早先清理另移除 6 份內容完全相同的 SpaceClaim PDF；其 relocation provenance 已移至 history，並連到保留檔及備份清冊。
- PDF 去重後 catalog 有 448,216 筆文件。docsearch SQLite 已精確移除 8 筆指向已去重 PDF 的 metadata，保留仍由其他文件使用的共用 FTS 正文。`PRAGMA integrity_check` 為 `ok`，`docs_meta` 有 448,044 筆、重複來源列為 0，`_needs_rebuild()` 為 false，實際查詢回傳 `docs/ANSYS_Document/` 路徑。SQLite 原檔備份位於被忽略的 `.runtime/catalog-rebuild-20261029/`。catalog fingerprint 全量重算耗時過長而停止；此欄位留空，搜尋與重建判定不讀取該欄位，索引仍以 manifest stat 對齊。

### REA 靜態 metadata 萃取

- 本機 v251 清冊有 1,479 個不同 SHA-256 的 ANSYS 命名 DLL；其中 58 個 hash 已有既存 REA 證據，本次新做 1,421 個 hash 的 `inspect-managed-members` 萃取。全批 source hash、REA subject hash、Evidence ID、metadata 狀態及輸出檔均已核對。詳細逐檔證據留在被忽略的 `.runtime/rea-audit-20261029/`。
- TurboGrid 與 TwinAI 的候選清冊另有 576 個唯一 hash；既有結果與本次 472 筆清單合計覆蓋此清冊。472 筆由獨立 reviewer 逐筆驗收：2 筆 `complete`、470 筆 `absent`，無失敗或 hash mismatch。其他 91 筆安裝 API 候選與 7 筆 TwinAI ROM 候選也有 REA 結果。
- 本次完成的是本機可用檔案的 REA 靜態檢查，不等於全部 ANSYS 產品或版本均已安裝，也不等於完整 API 清冊。v251 安裝盤點中有 20 個產品目錄不存在。`metadata absent` 不代表沒有 native API；native export、官方支援狀態、公開 API 映射及 runtime 行為仍未完成。本次未載入或執行 DLL，也未執行 ANSYS 求解。


### 2026-10-29 收尾核對

- `docs/ANSYS_Document/` 現有 424,940 個 HTML。catalog 的 401,686 筆 HTML source 均在磁碟，且每筆 `text_path` 輸出都存在；原先缺少 `text_path` 的 45 筆已修復。catalog 與轉換 manifest 有 46 筆重疊，另有 46 個 Mechanical SDK HTML 不在兩者中，但已有同名 Markdown 和 `source_url`。已將這 46 筆 hash 與輸出路徑加入 `.runtime/html-gap-conversion-20261029/html-manifest-final.json`。以 catalog-only、轉換 manifest 和 sibling Markdown 三組合併後，424,940 個 HTML 全部有 Markdown 對應，未映射數為 0。
- 轉換 manifest 有 23,254 筆：23,209 筆轉換、44 筆純文字 fallback、1 筆零位元組來源失敗；另 46 筆已有的 sibling Markdown 也經 hash 核對。23,299 個成功或重用的 Markdown 輸出均存在；所有 23,300 個來源狀態紀錄的 SHA-256 核對相符，0 個輸出缺失或 hash 不符。12 個 ACT API 索引頁已由 268–289 byte 的短備註升級為含來源 metadata、導覽連結及正文的 Markdown，並刷新 manifest 的輸出 hash。
- 唯一失敗來源是 `ACT/v261/archives/ansys-zip-ro3no34_/Mechanical/Reference.methode.Ansys.ACT.Automation.Mechanical.MappingValidation.RemoveParameter.html`，大小為 0 byte。438 byte 的對應 Markdown 說明沒有來源正文可抽取，不列為成功轉換。
- PDF manifest 269 筆：258 筆文字抽取、10 筆去重、1 筆掃描型例外。實體保留 259 份 PDF；目前 259 筆 catalog PDF 各有存在的 Markdown `text_path`。10 筆移除副本的 PDF 備份雜湊均相符。RAL 單頁色票已渲染為 300 dpi JPEG，Markdown 嵌入該頁，並說明 EasyOCR 輸出不可靠；不推測色值。PDF catalog 現以此 Markdown 作為搜尋正文。
- PDF 參考索引的 541 個本機連結經百分比解碼後全部存在。RAL PDF、Markdown 與頁面影像均有引用。
- docsearch 定向更新 3 筆受影響文件記錄：HTML 映射、RAL Markdown 內容雜湊及 PDF 正文別名。SQLite `quick_check(1)` 回報 `ok`，`_needs_rebuild()` 為 false；實際搜尋 `RAL DESIGN` 回傳新的 RAL Markdown 路徑。`docs_meta` 為 448,090 筆。主索引與 `api_kb.sqlite` 的 `quick_check` 均回報 `ok`。全量 catalog fingerprint 仍留空，索引以 `catalog_manifest_stat` 對齊；沒有重跑全量重建。唯讀 reviewer 另發現非設定主路徑的 `docs-index-a0cs5j2a.sqlite` 暫存檔及 journal；為避免破壞資料，未予清理。
- HTML 與 PDF 仍各有 1 筆無法產生正文 Markdown 的來源：0-byte ACT HTML 無正文；RAL 掃描色票 OCR 不可靠但保留頁面影像。這兩筆已有可追溯說明，不列為成功抽取。
- REA 本機 v251、TurboGrid/TwinAI 與其他候選批次的結果及限制見上節與 [REA 證據](../api_inventory/REA_EVIDENCE.md)。20 個產品目錄不在本機安裝中；native export 與完整產品／版本覆蓋未驗證。
### REA 2025 R1 全媒體 DLL 萃取（2026-10-29）

七份本機 2025 R1 ISO 的 235 個 7z 套件已唯讀解包，並納入 DISK1 的 2 個散置 DLL 與 Tcl runtime 套件的 4 個 DLL。清冊共有 31,512 個 DLL 路徑、20,030 個唯一 SHA-256。既有證據覆蓋 3,456 個 hash；本次新增 16,574 筆 REA 結果。全域狀態為 9,094 `complete`、10,913 `absent`、13 `malformed`、10 筆原始 PE 解析失敗；批次 manifest 記為 `subject digest mismatch`，逐檔錯誤內容指出 `truncated PE data-directory table`。六個散置 DLL 均有有效 Evidence ID、來源與 subject hash 相符，metadata 為 `absent`。清冊及彙總位於被忽略的 `.runtime/rea-audit-20261029/iso-media-packages/`。

此結果完整覆蓋這七份 ISO 中清點出的 DLL 路徑與唯一 hash，但有 10 個 PE 原始檔因目錄數量欄位錯誤而未能產生同 hash 的 REA subject digest。將該欄位只在副本修為 16 後，REA 對 10 個副本均回報 `absent`；這支持其目錄表沒有 CLR metadata directory，但衍生 Evidence 不能代替原始 hash 證據，原始 10 個仍列解析失敗。`absent` 不判斷 native API。此結果不證明未安裝的產品或其他版本完整，也不等同公開／受支援 API 清單。本機 v251 安裝樹有 29,969 個 DLL 路徑、18,907 個唯一 hash；獨立 reviewer 重算全數來源，0 筆缺檔或 hash／大小不符。18,906 個 hash 對應至媒體結果（含 10 個 PE 解析失敗 hash），另 1 個 hash 有 `absent` REA 證據，無未映射 hash。未載入或執行 DLL，未驗證 native API、支援狀態或 runtime 行為，未執行求解。詳細證據見[REA 證據](../api_inventory/REA_EVIDENCE.md)。
