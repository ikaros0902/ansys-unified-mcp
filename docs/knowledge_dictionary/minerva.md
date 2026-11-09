# Ansys Minerva 知識字典

本頁只整理可從公開 Developer Portal 頁面核實的 Minerva 資訊。現有產品頁來源版本標記為 unknown；HTTP APIs 的文件連結標為 2025 R2 並要求登入。此版本標籤不代表已讀取 2025 R2 API 內容。

## 產品定位

官方開發者文件將 Minerva 描述為 Simulation Process and Data Management (SPDM) 方案，提供模擬資料的組織、追蹤、分享與視覺化，支援團隊協作，並可在產品設計、改良或重新設計時啟動模擬工作流程及其他流程。

來源：[Ansys Developer documentation](https://developer.synopsys.com/docs)；[本機 Minerva developer 頁面](../ANSYS_Document/Minerva/unknown/guide/e0015a57712d-minerva.md#overview)。

## Minerva HTTP APIs：公開頁面可確認的範圍

本機保存的官方 developer 頁面只說明 Minerva HTTP APIs 可用於：

- 連線及驗證 Minerva。
- 查詢資料。
- 處理檔案。
- 使用任意程式語言；頁面將 APIs 稱為 language-agnostic。

同一頁連到 **2025 R2 (Sign-in required)** 文件索引。入口頁沒有公開 API endpoint、請求／回應 schema、認證流程、上傳協定或錯誤碼。主代理透過瀏覽工具開啟該 API 索引未取得正文；此字典不推定端點或身份驗證細節。

來源：[本機 Developer Portal 頁面](../ANSYS_Document/Minerva/unknown/guide/e0015a57712d-minerva.md#documentation)；[Minerva HTTP APIs 2025 R2 文件入口](https://developer.synopsys.com/docs/ansys-minerva-apis-2025-r2/index.md)。

## Minerva Transfer Client 與 SDK

Ansys Developer product guide 的 Connect 頁面表示，Minerva 提供 Minerva Transfer Client，透過它可存取 Minerva SDK。該頁沒有描述 SDK 的安裝、程式介面、支援語言或版本相容性。

來源：[Ansys Developer product guide — Connect](https://developer.synopsys.com/docs/ansys-developer-product-guide/Connect.md)（頁面標示最近更新 2026-08-13）。

## 尚待來源覆核的主題

2025 R1 Configuration Guide 表示 Aras Innovator 為 Minerva 功能框架，並列出 metadata 擷取設定能力；但尚未核實其完整底層架構、資料生命週期狀態名稱、修訂／分支規則、具體角色權限、Vault 分塊傳輸、OAuth2、OData、token 效期或 REST endpoints。原先字典中的 Python API 範例、HTTP 409／504 情境、60 分鐘 token 等數值與協定敘述已移除，因為現有來源沒有依據。

Developer Portal 顯示 2025 R2 API 文件需登入；授權範圍、條款及是否可分享原文仍未核實。Minerva 本機資料夾只有兩個 Markdown source files，README 記錄 2 files／1 body；沒有 PDF 或 HTML 可轉換。

## 來源追溯

| 文件 | 版本 | 本機狀態 | 可支持的內容 |
| --- | --- | --- | --- |
| [Ansys Minerva for developers](../ANSYS_Document/Minerva/unknown/guide/e0015a57712d-minerva.md) | unknown | 本機 Markdown | SPDM 定位、HTTP APIs 高層能力、language-agnostic、2025 R2 登入提示 |
| [Minerva Overview](../ANSYS_Document/Minerva/unknown/guides_and_tutorials/OVERVIEW.md) | unknown | 同 URL 的重複概覽 | 同一 developer landing page 摘要 |
| [Minerva HTTP APIs 2025 R2](https://developer.synopsys.com/docs/ansys-minerva-apis-2025-r2/index.md) | 2025 R2（入口標籤） | 登入需求；本機未快取 | 僅能確認文件入口與登入要求 |
| [Developer Portal — Connect](https://developer.synopsys.com/docs/ansys-developer-product-guide/Connect.md) | unknown | 官方頁摘要；原文未快取 | Minerva Transfer Client 可存取 Minerva SDK |

## Python client 的可核實線索（2026-11-03）

Ansys Developer product guide 的 Connect 頁（Last update: 13.08.2026）除了說明 Minerva Transfer Client 可存取 Minerva SDK，也連到 Ansys Community 論壇的「Is there a Python client library for interacting with Minerva?」。論壇接受答案稱，在 Minerva 安裝 Transfer Client 後，可從該客戶端提供的 SDK 目錄以 Python 載入 `Ansys.Minerva.Sdk`；示例使用 `clr`（Python.NET）及 `HttpConnection` 搭配 `BrowserLogin`。這讓讀者知道官方入口所指 SDK 至少有過一條 Python/.NET 整合示例，但論壇答案不是版本化 API 參考手冊，沒有可確認的發文日期或目前相容版本，不能當成現行登入流程承諾。本文不複製其中含具體內部伺服器位址或帳密的示例。

來源：[官方 Connect 頁](https://developer.synopsys.com/docs/ansys-developer-product-guide/Connect.md)；[Ansys Community 論壇問題及接受答案](https://discuss.ansys.com/discussion/2741/is-there-a-python-client-library-for-interacting-with-minerva)。第二個來源是社群問答；官方頁提供連結，但答案並非 Minerva API reference。網站檢視日期 2026-11-03；論壇頁面未顯示可確認的答案日期。未下載或本機快取論壇 HTML，未執行程式碼。

本輪已將兩個公開頁面整理為受保護的本機檢索補件：[Developer Connect 與 Python SDK 社群線索](ANSYS_Document/Minerva/unknown/guide/developer-connect-and-community-python-sdk.md)。補件省略社群答案中的特定主機位址與帳密示例，且不等同保存原始 HTML。


## 官方案例延伸：資料管理與上傳轉換（2025 R1）

### User's Guide：指定頁待查

[Ansys Minerva User's Guide（2025 R1）](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/pdf/Ansys_Minerva_Users_Guide.pdf) 原先標示已核讀資料版本、權限、上傳擷取與工作狀態，但目前無法提供對應頁面的核讀證據。先前摘要已撤回，這些主題及頁碼仍待重新取得原文後確認；本機未快取正文。

### 上傳轉換狀態：索引片段（2025 R1）

官方 User's Guide 的搜尋索引片段（印刷頁 23）列出 `Not Started`、`In Progress`、`Failed`、`Discarded` 與 `Complete with Errors` 等狀態。片段說明 `Complete with Errors` 可表示 metadata extraction 成功，但 report 或 image 生成失敗；三個階段的結果不能只以此狀態當成全部成功。這只根據搜尋索引片段，整頁 PDF 未取得，其他流程與頁碼仍待核讀。

來源：[Ansys Minerva User's Guide（2025 R1）](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/pdf/Ansys_Minerva_Users_Guide.pdf)，印刷頁 23 的搜尋索引片段；`sources.csv#online_minerva_users_guide_2025r1`。未執行 Minerva。

### 自訂檔案類型轉換

《Ansys Minerva Configuration Guide》指出，Metadata Extraction service 沒有內建任意檔案轉換；管理員需建立能處理指定輸入類型的 converter，再將它註冊到 Metadata Extraction service，並在 Minerva 設定相應檔案類型。轉換設定也可用 AML script 管理。手冊區分 `Ans_Data`（主要檔案 item）、`Ans_DataChild`（主 item 的子檔案）與 `Ans_DataFile`（與主要 item 關聯、但不顯示為獨立介面的檔案）。converter 範例以退出碼 0 表示成功、非 0 表示錯誤；未執行該範例。

來源：[Ansys Minerva Configuration Guide（2025 R1）](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/pdf/Ansys_Minerva_Configuration_Guide.pdf)，printed pp.179–180。

### 設定能力與 API 文件入口

2025 R1 Configuration Guide 列出管理員可設定的能力，包括 dashboard、metadata extraction、檔案／資料夾與比較檢視、digital thread、HPC job submission、work request template、互動式 application、verification plan、remote desktop、介面、email notification 與 scheduler。只有具 administrator privileges 的使用者可開啟 Administration 工具。這是能力清單，不是每個 Minerva 站台都已部署或啟用這些功能。

該指南並指出 Minerva API 文件位於 Ansys API Documentation site，須以 Ansys Customer Site／Ansys Help 的登入憑證登入。它與先前 Developer Portal 的 2025 R2 HTTP APIs sign-in gate 是不同入口；公開文件不足以推斷其 API schema 或使用權限。

來源：[Ansys Minerva Configuration Guide（2025 R1）](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/pdf/Ansys_Minerva_Configuration_Guide.pdf)，printed pp.1–2。

## 本輪來源限制

Configuration Guide 的指定頁面已由官方線上 PDF 核讀；User's Guide 的原先核讀宣稱無法證實，標為待核。兩份均未下載成本機 PDF／Markdown，也未納入全文索引。文件頁腳標示 proprietary and confidential；此摘要不判定實際合約是否准許分享。未核讀整本手冊，未登入 Minerva/API、未執行 converter、未連接或提交任何服務。


## 2026-11-04：Wave 1 本機來源盤點與限制說明

本批核對 catalog 中 2 筆 Minerva 既有文件與 sources.csv 來源清冊。Minerva 作為企業級 SPDM (Simulation Process and Data Management) 平台，其完整管理手冊多屬客戶授權或內部環境部署；目前本機未快取之線上主題誠實標註為缺口（`source_limited` / `source_online_partial`），不擅自虛構未核實之 API 簽名。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/minerva_module_conversion_report_20261104.md)。


## 2026-11-05：官方正文補核與本機導覽

本次以無帳號、無驗證 cookie 的直接 HTTP 請求，取得官方 landing Markdown、Connect 與 Developer documentation 的 Minerva 區段，以及兩份封面明示 **Release 2025 R1** 的手冊。下列快照更新前文「PDF／原文未快取」的舊狀態；原 catalog、舊摘要、原始 PDF 和 HTML 均保留。`Secured` URL 路徑不等於本輪實際要求登入：兩 PDF 本輪皆 HTTP 200，2025 R2 HTTP API 入口則 HTTP 403，未取得其正文。檔案可讀不代表已取得再散布權限。

| 來源 | 版本與擷取範圍 | 本機正文 |
| --- | --- | --- |
| Minerva for developers | unknown；本輪 raw Markdown 與既有 catalog 原件 bytes 相同，沿用其索引 | [原 catalog 正文](../ANSYS_Document/Minerva/unknown/guide/e0015a57712d-minerva.md) |
| Developer product guide — Connect | unknown；僅 Minerva 段，頁標 Last update: 13.08.2026，完整 HTML 另存 | [Minerva Transfer Client／SDK](ANSYS_Document/Minerva/official_body_20261105/connect.md) |
| Developer documentation | unknown；僅 Minerva 概覽卡片，完整 HTML 另存 | [SPDM 概覽](ANSYS_Document/Minerva/official_body_20261105/docs_home.md) |
| Ansys Minerva User's Guide | v251／Release 2025 R1；386 實體頁文字 | [逐頁 Markdown](ANSYS_Document/Minerva/official_body_20261105/users_guide.md)・[原 PDF](ANSYS_Document/Minerva/official_body_20261105/users_guide.pdf) |
| Ansys Minerva Configuration Guide | v251／Release 2025 R1；566 實體頁文字 | [逐頁 Markdown](ANSYS_Document/Minerva/official_body_20261105/configuration_guide.md)・[原 PDF](ANSYS_Document/Minerva/official_body_20261105/configuration_guide.pdf) |

### Conversion Task 狀態與失敗階段

User's Guide 的印刷頁 23–24（本機 PDF 實體頁 33–34）已從整頁正文核對，取代前文僅能依搜尋片段確認的限制。`Complete with Errors` 表示 metadata extraction 成功，但 report 或 image extraction 有失敗；不能把此狀態視為三階段全成功。metadata extraction 失敗會使後續兩階段失敗，而 metadata 成功後，report 與 image 仍可各自失敗。失敗階段的 Details 可提供 log／error 線索；是否能開啟 Conversion Task 仍受使用者權限影響。

來源：`sources.csv#online_minerva_users_guide_2025r1`；[實體頁 33](ANSYS_Document/Minerva/official_body_20261105/users_guide.md#pdf-page-33)、[實體頁 34](ANSYS_Document/Minerva/official_body_20261105/users_guide.md#pdf-page-34)。未在 Minerva 執行流程。

### 管理設定、File Type Converter 與 item types

Configuration Guide 印刷頁 1–2（實體頁 19–20）列出可設定能力，並表示具 administrator privileges 的使用者可存取 Administration 工具；Aras Innovator 提供 Minerva 功能框架。其 API 文件入口使用 Ansys Customer Site／Ansys Help 憑證，不能據此推導 HTTP endpoint 或 schema。

印刷頁 179–180（實體頁 197–198）說明：管理員需建立了解輸入檔案格式的 File Type Converter，並在 Minerva 與 Metadata Extraction service 設定對應；不是任意格式都內建轉換。converter 的成功退出碼是 0、錯誤為非 0；設定可透過 AML script 管理。下表只整理該頁的顯示角色，未驗證實際站台自訂配置。

| ItemType | 該指南說明的角色 |
| --- | --- |
| `Ans_Data` | 資料檢視中顯示的主要檔案項目 |
| `Ans_DataChild` | 主要項目的子項，出現在父項的 Contents |
| `Ans_DataFile` | 關聯 File 與主要項目，通常不作獨立介面項目，可用於 report／preview 資源 |

來源：`sources.csv#online_minerva_configuration_guide_2025r1`；[實體頁 20](ANSYS_Document/Minerva/official_body_20261105/configuration_guide.md#pdf-page-20)、[實體頁 197](ANSYS_Document/Minerva/official_body_20261105/configuration_guide.md#pdf-page-197)、[實體頁 198](ANSYS_Document/Minerva/official_body_20261105/configuration_guide.md#pdf-page-198)。

### 轉換品質與剩餘缺口

兩手冊共 952 頁皆保留頁碼註記與抽出文字，無少於 100 字元的頁；這不證明圖表、公式或圖片文字已辨識。PDF 表格版面未逐表重建，原始 PDF 留作核讀。SDK 版本皆 unknown，PDF metadata 的建檔日期不作產品 release。既有社群 Python.NET 示例仍是未標版本摘要；2025 R2 API 正文、完整資料／權限工作流的語意覆核、跨版本相容與分享權限仍未完成。

詳[本批補核報告](../maintenance/knowledge_dictionary_passes/2026-11-05/minerva_module_conversion_report_20261105.md)。
