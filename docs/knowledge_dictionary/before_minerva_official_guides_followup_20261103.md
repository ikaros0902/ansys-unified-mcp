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

目前來源不足以證實 Aras Innovator 底層架構、資料生命週期狀態名稱、修訂／分支規則、角色權限、模擬 metadata 擷取、Vault 分塊傳輸、OAuth2、OData、token 效期或具體 REST endpoints。原先字典中的 Python API 範例、HTTP 409／504 情境、60 分鐘 token 等數值與協定敘述已移除，因為現有來源沒有依據。

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
