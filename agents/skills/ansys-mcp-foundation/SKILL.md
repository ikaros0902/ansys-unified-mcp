---
name: ansys-mcp-foundation
description: Use when creating, updating, or reviewing ANSYS Unified MCP skills, tool integrations, workflows, API mappings, or engineering automation in this repository. Routes agents to the maintained source and code references so they can inspect only the relevant product and release instead of rereading the full manuals or codebase.
---

# ANSYS MCP 基礎 Skill

本 Skill 是後續 ANSYS MCP 工作的入口與共同詞彙表，不取代產品專項 Skill、官方手冊或原始碼。先讀本頁；依任務只載入下列必要參考，再核對實際要改的程式與版本。

## 開始工作

1. 從 [技能目錄](../README.md) 找出既有專項 Skill；優先延伸正確領域，避免另造重複入口。
2. 按領域選路由：**P1** Mechanical、Mesh、Connections、SpaceClaim、LS-DYNA、LS-PrePost、Random Vibration；**P2** Thermal、optiSLang、Sherlock、Icepak；**P3** Speos／Illumination、Zemax、Lumerical；其餘為 **P4**。領域來源與實際支援邊界見 [來源及支援矩陣](../../../docs/skills/DOMAIN_SOURCE_AND_SUPPORT.md)。
3. 先定位負責模組及公開 MCP 工具，再追到實作、測試與文件。依 [程式碼地圖](references/repository-map.md) 使用符號搜尋或窄範圍搜尋；只讀與變更直接相關的函式、呼叫端和測試，不為熟悉專案而讀完整個 source tree。
4. 若要新增或修改 MCP 工具，依 [工具契約與驗證](references/tool-and-evidence.md) 保持既有相容性、明確錯誤分類，並以離線 mock 測試驗證；不要為診斷或單元測試啟動真實 ANSYS。
5. 若工作涉及工程判斷、腳本或結果報告，先辨識產品版本、SDK、宿主與介面；將必要條件、官方建議及專案 heuristic 分開，並保留結果來源標籤。
6. 若正在撰寫進階 Skill，讀 [進階 Skill 撰寫流程](references/skill-authoring.md)：先抽取使用情境與完成條件，再以精確來源形成決策指引，最後驗證連結、API 依據與代表性案例。

## 共同界線

- 本專案技能唯一維護位置是 `agents/skills/`。入口保持精簡；只有會改變決策的知識才放入 references，手冊全文留在原始文件庫。
- 不由檔名、安裝目錄、API 名稱存在或 mock 通過推論出版本相容、產品連線、授權可用或真實求解成功。
- v251、v252、v261 是不同產品 release；Python SDK 版本、產品版本、宿主（CPython、Mechanical ACT、SpaceClaim 內嵌腳本、Workbench journal、LS-PrePost）和介面需分開記錄。遇到版本歧義時列出候選並回查，不任選最新版。
- 官方產品手冊／API reference 確認介面和適用條件，官方 examples 支援可重現流程；PyAnsys umbrella 只作產品套件路由。第三方倉庫提供候選設計，不直接採用未核實的 API、工程門檻或程式碼。
- 對於 Sherlock、Icepak、Speos、Zemax、Lumerical 等無完整 MCP connector 的領域，可交付知識與 API 映射；不得寫成已可由本 MCP 連線或求解。
- 文件索引／API KB 是可重建資料。新增來源須記錄版本、路徑或 URL、章節／頁碼、hash 或 commit、license 狀態及內容品質；不要複製大批手冊、機敏路徑或 solver 二進位檔進技能。

## 按需參考

- 需要找文件、判別版本或檢查來源品質時，讀 [來源查找與文件限制](references/source-routing.md)。
- 需要改工具、連線、流程或報告，或判斷測試證據強度時，讀 [工具契約與驗證](references/tool-and-evidence.md)。
- 需要定位 Python 模組、測試位置與驗證命令時，讀 [程式碼地圖](references/repository-map.md)。
- 需要撰寫本專案的進階產品／流程 Skill 時，讀 [進階 Skill 撰寫流程](references/skill-authoring.md)。

## 完成交付

交付時說明變更入口及其對應的來源／API／測試；報告實際跑過的驗證、結果來源標籤與版本。將未執行的真機測試、未確認的版本或環境阻擋列為未驗證，不以計畫或 mock 結果代替完成證據。
