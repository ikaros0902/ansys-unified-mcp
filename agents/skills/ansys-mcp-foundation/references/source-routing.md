# 來源查找與文件限制

## 先用維護索引縮小範圍

- [領域來源及支援矩陣](../../../../docs/skills/DOMAIN_SOURCE_AND_SUPPORT.md)：產品 → 專項 Skill → 文件來源 → MCP 支援／證據狀態。
- [本機來源清冊說明](../../../../docs/maintenance/ANSYS_SOURCE_INVENTORY.md)：清冊欄位、品質標記、PDF 與 Markdown 索引邊界、重建方式。
- [第三方採用紀錄](../../../../docs/maintenance/EXTERNAL_SOURCE_ADOPTION.md)：哪些 GitHub 來源讀過、採用何種抽象設計、哪些 commit／license 尚未核實。
- 原始文件根目錄：`D:\Ikaros\ACT_Test\3.documents` 與既有 `D:\ansys-docs-local`。路徑僅供本機查找；不要把完整目錄清單或本機私有內容複製進 Skill。

## 查證順序

1. 先從領域矩陣取產品、文件名、版本線索及章節，再使用 `search_ansys_docs` 或本機索引定位關鍵章節；需要 API symbol 時使用 `api_search`、`api_get`、`api_path`。
2. 取得精確 API 或物理判斷前，回看相應 release 的官方手冊／API reference 和 example；記錄文件章節、PDF 頁碼或固定版本 URL。不同宿主的腳本不可只因 API 名稱相同而混用。
3. 需要理解行為時，讀實際程式的入口、被呼叫函式、資料模型及相關測試。API KB 的 symbol 命中是導航線索，不等同參數簽名、型別或 runtime 已驗證。
4. 文件缺漏時如實標記：`LS-DYNA_Keyword_and_Theory_Manuals.md` 是下載入口摘要，不是完整 keyword volumes；PDF、空檔、模板、stub、目錄頁和下載頁不能充當正文證據；同 hash 的多版文件副本不構成多版獨立證明。
5. 第三方來源只在實際讀過內容且記錄 commit/tag、license、檔案路徑後引用；先回查官方文件。未確認的 URL、內容或 license 標為待查，不推定不存在。

## 版本紀錄最小欄位

記錄產品 release、SDK 版本、宿主、介面、來源位置與章節／頁碼、查閱日期，以及證據層級。v251＝2025 R1、v252＝2025 R2、v261＝2026 R1；來源清冊的路徑推定只是線索，需由正文／封面核對。官方 PyAnsys umbrella 是套件集合入口，具體 API 以各產品文件及固定版本 examples 為準。

## 官方方法參考

- [Anthropic Skill Creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)：技能意圖、精簡入口、references 漸進揭露和基於真實任務的驗收設計。
- [Anthropic MCP Builder](https://github.com/anthropics/skills/tree/main/skills/mcp-builder)：工具設計、schema、錯誤處理、工具檢查和 evaluation 的參考；其部署建議不覆蓋本機 ANSYS MCP 專案既有架構。
- [Anthropic Build MCP Server](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/mcp-server-dev/skills/build-mcp-server)：MCP server discovery 與設計路由參考。
- [PyAnsys 官方 GitHub](https://github.com/ansys/pyansys)：套件入口；按產品追到官方 API 文件和 examples。
