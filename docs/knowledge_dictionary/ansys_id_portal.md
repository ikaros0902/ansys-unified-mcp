# Ansys ID Portal 管理字典

> 本頁依本機 Developer Portal 快照整理；來源 release 均標為 `unknown`。Portal 概覽與管理指南為同一 URL 的內容副本。同步指南含操作流程與範例，但部分 API／服務端契約仍須以目標環境文件確認。

## Account、Group 與 Entitlements

- **Account** 代表組織，並定義其 Ansys entitlements 存取。
- **Group** 可用於更細的成員管理，例如依產品、license pool 或 feature 分組。
- 本機概覽沒有說明席位如何分配、授權如何計數、API schema 或 account number 與後台商務系統的映射；不能從「entitlements access」推定這些細節。

來源：[Portal Overview](../ANSYS_Document/Ansys_ID_Portal/unknown/guides_and_tutorials/OVERVIEW.md)（`ansys_bad069f7688645b4245c8183`）、[管理指南](../ANSYS_Document/Ansys_ID_Portal/unknown/guide/2e74baf83b4f-ansys-id-portal.md)（`ansys_868603051167abf57414b2f5`）。兩頁均 release `unknown`。

## Entra ID Membership Sync

同步工具將 Microsoft Entra ID security group 成員同步到 Ansys ID Portal 的 account 或 account 內 named group。文件描述的是**單向同步**：每次執行都比對來源與目標成員，新增差異並移除來源中已不存在的成員；直接在 Portal 做的變更可能在下次同步被覆寫。沒有反向同步。

| 項目 | 文件所述行為 | 使用邊界 |
|---|---|---|
| 成員識別 | 使用 Entra 使用者的 `mail` 屬性；沒有 primary email 的成員會被警告並略過。 | 不要假設會以 UPN 代替 `mail`。 |
| 巢狀群組 | 以 Graph `transitiveMembers` 取得巢狀群組成員。 | 文件稱會展開成員；不代表工具可直接管理巢狀群組結構。 |
| `--target-type account` | 同步 account membership；account 必須先存在。 | 工具不建立 account。 |
| `--target-type group` | 同步 named group；group 不存在時建立 General 類型 group，新增的 group member 也會加入 account。 | 工具只管理 membership，不管理角色或權限。 |
| `--dry-run`／`-DryRun` | 記錄預計新增與移除項目，不寫入變更。 | 在執行有副作用的同步前先檢查預演輸出。 |
| `--preserve-email`／`-PreserveEmail` | 指定永不因同步移除的 email。 | 若 PAT 使用者不在來源群組，保留其 account membership，避免後續同步憑證失效。 |

Python 與 PowerShell 範例使用下列旗標名稱：`--entra-domain`、`--entra-group`、`--entra-client-id`、`--entra-client-secret`、`--ansys-pat`、`--target-type`、`--account-number`、`--group-name`、`--dry-run`、`--preserve-email`。PowerShell 對應為 PascalCase 參數。同步指南亦列出 `--send-email`、`--log-file` 等選項；完整語法依來源腳本及其版本確認，不把字典範例視為已執行程式。

來源：[Membership Sync Setup and Usage](../ANSYS_Document/Ansys_ID_Portal/unknown/guides_and_tutorials/ansys-id-portal-membership-sync-setup-and-usage/index.md)（`ansys_629ab7d33eaef48ee14b98ca`；來源修訂日期 2026-05-13）。沒有在本機執行同步腳本或連線 Portal。

## Entra App Registration 與 Client Secret

同步指南要求建立 Entra app registration，以 application permissions 讀取群組與成員資料：

| Microsoft Graph 權限 | 文件用途 |
|---|---|
| `Group.Read.All` | 依名稱尋找 security group 並讀取基本資料。 |
| `User.Read.All` | 讀取成員個人資料，包括 `mail`。 |

兩個權限都需以 **Application permissions** 設定並由租戶管理員授予 admin consent。目標群組需為 Security group，名稱需與 `--entra-group` 傳入值一致。Client Secret 是敏感憑證，指南要求安全保存；輪替流程是到期前建立新 secret、更新排程、驗證新設定後刪除舊 secret。來源將維護標為 annual maintenance，但未規定通用到期長度或固定提前天數。

來源：[Entra app registration setup](../ANSYS_Document/Ansys_ID_Portal/unknown/guides_and_tutorials/ansys-id-portal-membership-sync-setup-and-usage/entra-setup.md)（`ansys_834cfbd2bfbd6a2f1759006a`）。

## PAT 角色與同步安全界線

同步工具使用 Ansys PAT 呼叫 Portal API。PAT 所屬使用者必須是目標 account 成員，並具備 **ASC** 或 **Customer Administrator** 角色；若該使用者不在 Entra 來源群組，應以 `--preserve-email` 保留。指南要求將 PAT 當作敏感憑證管理，且用 `--dry-run` 檢查計畫變更。

本機 PAT 指南描述由 helper script 將 PAT 交給 Ansys ID SSO，換取供 API 使用的 access token；同步文件說明 Portal API 部署在 `iam.ansys.com`。本機快照未提供足以獨立核實的同步 API endpoint schema、錯誤碼或完整授權模型；API 文件入口列於 `https://iam.ansys.com/swagger/index.html`。

PAT 指南另說明 PAT 與特定使用者、Ansys account 及 scope 關聯，可設定到期日並可撤銷；建立流程包含在 Portal 選擇 account、設定名稱／到期日／scope，並將建立後顯示的 token 複製保存。該指南要求 PAT 視同密碼。它描述的認證鏈是 PAT 經 Ansys ID SSO 驗證後換取短效 access token，再以 Bearer token 呼叫 API；不要將 PAT 與 API 呼叫所用的 access token 混為一談。文件範例選擇 `Full Access`，但這不能推定為所有 API 或組織的最小權限設定；應依目標 API 與帳戶政策確認 scope。

指南內有兩個需人工核實的契約差異：PAT guide 將 PAT 描述為可選 scope、可設定效期，而同步指南只列出 PAT 帳戶成員及角色要求，未說明其 token scope；PAT guide 的 API 範例以示意 `<portal-url>/api/accounts` 表示，與同步指南提到的 `iam.ansys.com` Swagger 入口不足以建立完整 endpoint／schema 對照。故本字典只記錄各文件明確陳述，不推定同步工具實際使用的 scope、到期政策或 endpoint。

來源：[Membership Sync Setup](../ANSYS_Document/Ansys_ID_Portal/unknown/guides_and_tutorials/ansys-id-portal-membership-sync-setup-and-usage/index.md)（`ansys_629ab7d33eaef48ee14b98ca`；頁面標示 2026-05-13 更新）、[PAT Authentication Guide](../ANSYS_Document/Ansys_ID_Portal/unknown/guides_and_tutorials/ansys-id-sso/pat-authentication-guide.md)（`ansys_ee80b55dadf40fb900ba6394`；頁面標示 2026-03-19 更新）。未登入、建立 PAT 或呼叫 API。

## 主題清冊與來源缺口

| 主題 | 狀態 | 邊界 |
|---|---|---|
| Account、Group 與 entitlements | complete | 只依概覽說明組織、entitlements 存取與群組用途；未涵蓋席位分配或 account API schema。 |
| Entra membership sync | complete | 整理單向差異同步、group/account 標的、nested members 與 dry-run；未執行。 |
| App registration 與憑證 | complete | 整理兩項 Graph application permissions、admin consent 與輪替順序；不推定 tenant 的 secret policy。 |
| PAT 前置條件與防鎖定 | complete | 整理 account membership、ASC／Customer Administrator 及 preserve-email；未驗證服務端權限。 |
| PAT scope、效期與 token exchange | partial | PAT guide 說明可設定效期、可撤銷、scope 與 SSO access-token 交換；同步工具的實際 scope／API 權限仍無法由快照證實。 |

來源 release 均為 `unknown`，頁面更新日期只代表文件標示日期，不等同產品／API 版本。Portal overview 與管理指南是同一 URL 的內容副本；SSO 是相鄰文件範圍，僅在 PAT 認證關聯處引用。此字典不包含使用者實際 account、group、secret 或 PAT 值。完整來源盤點、轉換狀態、官方連結擴展和搜尋抽查見維護報告 [ansys_id_portal_review.md](../maintenance/knowledge_dictionary_passes/2026-11-02/ansys_id_portal_review.md)。


## 2026-11-04：Wave 6 本機來源盤點與限制說明

本批完成 ansys_id_portal 模組既有本機 catalog 文件（共 6 筆）與 sources 清冊（共 6 筆）之完整雜湊、正文路徑與標籤結構核對。本機未快取或具備企業授權/登入限制之線上主題誠實標記為缺口（保持現有非 complete 狀態），未擅自虛構未核實之線上 API 簽名或執行求解運算。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/ansys_id_portal_module_conversion_report_20261104.md)。
