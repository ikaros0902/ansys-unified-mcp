# GitHub 公開發佈前檢查

檢查日期：2026-10-28

## 儲存庫狀態

Git remote 指向 `ikaros0902/ansys-unified-mcp`。GitHub repository metadata 回報此儲存庫為 **public**；因此本分支的新增內容會向所有人公開。

## ANSYS 衍生內容

本地 API inventory 包含從已安裝 ANSYS 組件產生的 Mechanical、SpaceClaim、optiSLang 快照及 REA 證據。另有來自 ANSYS 官方手冊的整理內容。官方 [2025 R2 Legal Notices](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/pdf/Legal_Notices.pdf) 將軟體與程式文件標示為機密及專有，並說明其使用、揭露、移轉或複製須依適用軟體授權條款。它本身不是通用授權書；該 PDF 內另收錄的第三方元件條款不可當作所有 ANSYS 產品的共同授權。[Ansys General Terms and Conditions](https://ansys.com/legal/agtc) 頁面目前列出 2025-11-19 版 AGTC 與 2025-04-09 版 [License Terms](https://ansys.synopsys.com/content/dam/legal/license-terms-april-2025.pdf)。頁面指出適用版本取決於合約簽署時間，個別 Offering 的附加條款與產品代碼依 Order Form 指定。April 2025 License Terms 將程式授權限於 object code 及 internal business purposes，並限制逆向工程；其中的法定例外另要求 Ansys 先拒絕書面資訊請求。這些公開文件無法證明本專案使用者合約的具體範圍，也不能單獨判定由 REA 產生的候選資料是否可公開散布。

2026-10-28 本地分析新增 AUTODYN、DesignXplorer、Engineering Data、Mechanical Interfaces、ACT、LS-DYNA、Additive、AnsysEM、SpaceClaim 等 v251 component metadata 摘要。完整 REA JSON 保留在被忽略的 `.audit/repo-restructure/rea-managed-v251/`。Markdown 摘要本身仍是由 ANSYS 組件產生的衍生資料，不能因未附 raw JSON 就視為可公開。

目前沒有使用者 Order Form、產品代碼、補充條款或 Ansys 書面許可證明本專案的 REA 成員清冊、手冊衍生字典或 RAG 片段可公開散布。授權範圍未釐清前，不將下列來源衍生資料推送到公開 GitHub：

- `docs/api_inventory/mechanical_api.json`、`spaceclaim_api.json`、`optislang_api.json`
- `docs/api_inventory/autodyn_rea_api.json`、`designxplorer_rea_api.json`、`engineeringdata_rea_api.json`、`mechanical_interfaces_rea_api.json`
- `docs/api_inventory/granta_mi_rea_api.json`、`materialdesigner_rea_api.json`、`turbosystem_ccd_rea_api.json`、`turbosystem_ccm_rea_api.json`、`units_rea_api.json`、`vista_tf_rea_api.json`
- `docs/api_inventory/act_core_rea_api.json`、`api_discovery_rea_api.json`、`api_geometry_rea_api.json`
- `docs/api_inventory/REA_EVIDENCE.md`
- 任何從 ANSYS 手冊轉出的 PDF、HTML、Markdown 正文或索引內容

`API_CATALOG.md` 連結上述快照，不能單獨視為已完成分享審查。SDK 快照也需按各套件授權分別確認。

2026-10-28 另查閱 Ansys 官方法律頁面。v251 [Legal Notices](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/ai_ginfo/ai_legal.html) 說明軟體及程式文件屬機密、專有內容，使用、揭露、移轉與複製依軟體授權條款處理；官方 [2025 R2 Legal Notices PDF](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/pdf/Legal_Notices.pdf) 也將文件複製用途限定在適用條款允許的範圍。Ansys [Limited Release License Agreement](https://www.ansys.com/content/dam/legal/ansys-limited-release-license-agreement.pdf) 另含技術與相關文件的保密條款，但該協議只適用於受其條款約束的授權，不能推定套用到本專案。這些官方頁面支持「必須先查明實際合約」的風險判斷，不能單獨判定本機 REA、SDK snapshot 或人工摘要可否公開。

新增的[全產品 API 來源與缺口索引](../api_inventory/PRODUCT_API_MATRIX.md)是由本機 coverage 清冊生成的人讀導覽。它列出快照檔名、版本、成員計數、組件名稱及來源連結，因此仍與來源衍生資料相關；在底層資料權限未確認前，不將它視為已核准的公開版本。API/RAG 指南若連結到受限快照，也需一併納入審查。

## 本機路徑清理

多個 SDK 快照與 `sdk_environment.json` 含 `F:/Ming_python/.../.venv/` 絕對路徑；optiSLang 快照含本機 ANSYS 安裝路徑。這些路徑不應進入公開資料。建立發佈候選前需移除或改成套件內相對路徑，並重掃所有 JSON、Markdown 與差異。

## 發佈阻擋項

- 目標儲存庫為公開儲存庫。需有適用授權或書面散布許可，才能納入受限來源衍生資料；否則應將其保留於本機並由公開字典連向官方來源。
- GitHub CLI 回報目前登入憑證無效，無法透過本機 Git 推送分支或建立 PR。
- 本文件記錄風險與必要工作，不構成法律意見或授權判定。
