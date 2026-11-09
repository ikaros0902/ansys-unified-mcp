# Ansys ID SSO 與 PAT 知識字典

> 依本機 Ansys ID SSO Developer Overview、Developer Guide 與 PAT Authentication Guide 整理。來源 release 均為 `unknown`；PAT guide 標示最後更新 2026-03-19。不可由網頁修訂日推定目前服務端版本。

## Ansys ID、IdP 與 SSO

Ansys ID SSO 用於 Ansys 產品及內外部系統的身分驗證。PAT 指南列出 OpenID Connect（OIDC）支援。PAT flow 的高階步驟是：在 Ansys ID Portal 建立 PAT，交給 helper script 或 authentication flow，經 Ansys ID SSO 驗證後取得 access token，再以該 access token 呼叫 API。

SSO Overview 列出的主要平台／語言包含 .NET、JavaScript／TypeScript、Java、Python、Android、iOS／macOS 與 Go。該清單不等於每一項產品 API 都提供相同 SDK 或完整支援矩陣。

來源：[SSO Overview](../ANSYS_Document/Ansys_ID_SSO/unknown/guides_and_tutorials/OVERVIEW.md)（`ansys_dedb72419243d8f52321d60a`）、[SSO Developer Guide](../ANSYS_Document/Ansys_ID_SSO/unknown/guide/a8f7fca7fef7-ansys-id-sso.md)（`ansys_754fbfff592814e6af03729d`）。兩者 release `unknown`。

## PAT 身分、account、scope 與期限

PAT 是供非互動式工具使用的長效憑證。指南說 PAT 與特定使用者、Ansys account 及 scope／permission 關聯，並可設定到期時間及由 Ansys ID Portal 撤銷。建立 PAT 前需有 Ansys ID SSO 使用者，並在 Salesforce 關聯 customer account number；若關聯多個 account，可在建立流程選擇目標 account。

| 項目 | 來源內容 | 限制 |
|---|---|---|
| Scopes | 說明例子包含 `openid`、`offline_access` 與產品／資源專屬 scopes。PAT 建立步驟指示為 SSO authentication 選 `Full Access`。 | 不代表所有 API 都需要相同 scope。 |
| Expiration | 使用者建立 PAT 時選擇 expiration date；PAT 可在 Portal 撤銷。 | 本機指南沒有通用期限範圍、固定 token TTL 或撤銷生效時間。 |
| Access token | PAT 驗證後取得短效 access token；大多數 API 呼叫以 `Authorization: Bearer <access token>` 傳送。 | 文件未在此處規定固定有效分鐘數或 JWT 簽章驗證方式。 |
| ID／refresh tokens | PAT guide 說明 Ansys ID SSO 可提供 access、ID 與 refresh tokens。 | 本機頁面未完整規定各類 token 的生命週期或 refresh 呼叫契約。 |

PAT 代表建立者身分，來源要求將其視同密碼：安全保存、定期輪替、不分享，並刪除未使用的 token。來源未規定通用輪替間隔。

來源：[PAT Authentication Guide](../ANSYS_Document/Ansys_ID_Portal/unknown/guides_and_tutorials/ansys-id-sso/pat-authentication-guide.md)（`ansys_ee80b55dadf40fb900ba6394`；最後更新 2026-03-19）。未登入 Portal 或建立／撤銷 token。

## PAT 換取 API Access Token

官方指南提供 Python helper `get_auth_code_with_access_token.py` 與 PowerShell helper `Get-AccessTokenAndCallApi.ps1`，並說明 helper 會以 PAT 向 Ansys ID SSO token endpoint 取得 access、ID 與 refresh tokens。API 一般以 Bearer access token 呼叫。Portal API 文件入口為 `https://iam.ansys.com/swagger/index.html`；PAT guide 的通用 API 範例使用 `https://<portal-url>/api/accounts` 佔位網址。

本機指南沒有列出可直接重建的 token endpoint URL、HTTP payload、grant type 或 scope request 細節。因此本字典不提供自製 token-exchange 程式碼，也不將示意端點當作可執行契約。請依官方 helper 與目標服務文件操作。

來源：[PAT Authentication Guide — Python／PowerShell helper 與 Portal API quick reference](../ANSYS_Document/Ansys_ID_Portal/unknown/guides_and_tutorials/ansys-id-sso/pat-authentication-guide.md)（`ansys_ee80b55dadf40fb900ba6394`）。官方 helper 位於該頁連結的 Ansys DevRelPublic repository；本輪未下載或執行。

## 主題清冊與缺口

| 主題 | 狀態 | 來源界線 |
|---|---|---|
| IdP／Service Provider 與 SSO 概念 | complete | 整理 SSO Overview 的身分驗證、平台與語言清單，以及 PAT 指南的 OIDC 說明；未推定 JWT 簽章或各服務端相容性。 |
| PAT 身分、account、scope、期限與撤銷 | complete | 整理 PAT guide 的綁定、可配置期限、scope 例子與 Portal 撤銷方式；未推定 TTL 或撤銷延遲。 |

來源 release 均為 `unknown`。完整 token endpoint／request schema、各 API 的 scope matrix 與服務端版本仍缺本機原文依據。

## 與其他字典

- [Ansys ID Portal 管理字典](ansys_id_portal.md)：Entra membership sync、account/group 與同步 PAT 角色條件。
- [Granta MI 字典](granta_mi.md) 與 [Minerva 字典](minerva.md)：各產品 API 的實際授權規則應依其自身來源文件確認。

## 建立條件、Helper 與 Portal API 使用界線

PAT Authentication Guide 的建立條件是：使用者已有 Ansys ID SSO 帳號，且 Salesforce 中關聯 customer account number；若 Portal 顯示多個 account，建立前選擇目標 account。指南範例在 SSO authentication scope 選 `Full Access`。這是該指南的操作指示，不能推廣成所有產品 API 的最小權限設定。PAT 代表使用者身分，文件建議安全保存、定期輪替、不分享，並刪除未使用的 token；未指定固定輪替週期。

指南列出 Python helper `get_auth_code_with_access_token.py`（需 `msal`、`httpx`、`requests`）及 PowerShell helper `Get-AccessTokenAndCallApi.ps1`（需 `MSAL.PS`），流程取得 `access_token`、`id_token`、`refresh_token`；應以 `access_token` 呼叫 API。指南的 Portal API 範例使用 `Authorization: Bearer <access token>`、`Content-Type: application/json`，並以 `https://<portal-url>/api/accounts` 作佔位網址；正式環境參考入口為 [Ansys ID Portal Swagger](https://iam.ansys.com/swagger/index.html)。指南沒有提供可直接重建交換流程所需的 token endpoint URL、grant type、完整 HTTP payload，也沒有給出 API scope matrix，因此請依官方 helper 和目標 API 文件，不要由此頁推導自行交換契約。

來源定位：[PAT Authentication Guide — PAT 建立要求](../ANSYS_Document/Ansys_ID_Portal/unknown/guides_and_tutorials/ansys-id-sso/pat-authentication-guide.md#how-to-generate-a-pat)、[Python／PowerShell helper 與 API quick reference](../ANSYS_Document/Ansys_ID_Portal/unknown/guides_and_tutorials/ansys-id-sso/pat-authentication-guide.md#using-the-python-helper-script)、[SSO Overview](../ANSYS_Document/Ansys_ID_SSO/unknown/guides_and_tutorials/OVERVIEW.md)。PAT guide 在來源清冊的產品分類是 `ansys_id_portal`；依內容其 SSO/PAT 主題也供本字典引用，搜尋時需注意此跨產品分類。

## 本機來源與索引範圍

SSO catalog 有兩份原生 Markdown，分別為 Developer Guide 與 Overview。兩份共用來源 URL，正文重疊，Overview 另有匯整頁標頭及來源欄。兩份原件與 catalog SHA-256 相符，release 均為 `unknown`。PAT Authentication Guide 與其導覽頁另外歸類為 `ansys_id_portal`，兩者可在本機 catalog 回查。PAT 指南的更新日 2026-03-19 是文件日期。

本批使用既有 Markdown。來源集合沒有 PDF 或 HTML 原件。PAT 指南的圖片與 helper 留待核實。11/04 URL 清冊的八列含兩筆帶格式尾碼的重複網址，共六個獨立網址。該批未擷取網址，本輪採用本機快照。線上文件現況、分享權、交換端點、HTTP 請求格式及各 API scope 仍待核實。

11/04 四筆歷史查詢中，`Identity` 命中 Developer Guide，`SSO`、`Token`、`OIDC` 命中字典。僅以 `product=ansys_id_sso` 篩選會排除歸類為 Portal 的 PAT 指南。查閱 PAT 指南全文時，使用 `ansys_id_portal` 篩選、跨產品查詢或直接開啟來源。11/03 的查詢紀錄曾回報繁中顯示異常。11/08 唯讀 SQLite 回讀確認舊字典片段可讀，本輪的查核範圍為 SQLite 片段，介面端顯示仍待驗收。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/ansys_id_sso_module_conversion_report_20261104.md)。
