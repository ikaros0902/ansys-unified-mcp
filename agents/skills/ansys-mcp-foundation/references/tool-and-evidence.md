# 工具契約、工程判斷與驗證

## MCP 工具與連線

- 工具層保持薄封裝，重用既有 `tools/`、`connection/`、controllers、`SessionRegistry` 和 script runner；先找現有能力再新增另一條路徑。
- 先盤點使用者需要的操作與現有工具目錄；少量穩定動作使用清楚、專責的工具，龐大 API 面積則先搜尋／篩選再查詢或執行，不把所有底層 API 一次暴露給 Agent。任何新模式都要符合 repo 現存註冊與 session 契約。
- 工具的輸入欄位描述單位、允許值、必要性和目標產品；輸出保留既有扁平 `ok/error` 信封與呼叫參數相容性。錯誤要指出可操作原因，例如缺套件、版本不符、session 無效、宿主未就緒或功能未支援。
- FastMCP 工具註記沿用專案實際欄位 `readOnlyHint`、`destructiveHint`、`idempotentHint`、`openWorldHint`；可參照 `tools/apikb_tools.py`。只在 SDK 支援時設定，並讓值反映真實副作用，不能為改善 Agent 觀感而標錯。
- 將安裝、SDK 匯入、transport、host script、模型狀態和 license 分層報告。未做的檢查標 unknown；離線診斷不得為方便而啟動 ANSYS 或建立模型。
- 明確區分附掛的使用者程序和 MCP 自行啟動程序；只清理本 MCP 擁有的程序。Timeout 後先查作業狀態；可能已修改模型或已求解時，不盲目重送非冪等命令。
- 新增 MCP tool 應有 schema／description、成功與失敗測試；需要外部互動時採 integration marker，普通 pytest 必須 mock ANSYS、gRPC、COM 和檔案輸出。

## 工程判斷

每個判斷都標明其類別與適用條件：

- **必要條件**：缺少就不能可靠建立或驗證目標分析，例如單位、材料必要參數、非空 scoping、有效結果檔。
- **官方建議**：附產品 release、分析類型、材料／單元條件與文件章節；只有適用範圍內才使用。
- **專案 heuristic**：明確標示經驗性、適用模型、關注量和調整依據，不轉成跨產品硬門檻。

網格品質、模態充分性、PSD 頻帶／單位、沙漏能、質量縮放、CTE、參考溫度及最佳化可行性皆需依具體分析判斷。不可用測試紅燈當理由放寬物理門檻；DOE 失敗點不可填零參與最佳解排序。

## 結果來源及宣告

沿用下列標籤並一路傳遞到解析結果和報告：

- `synthetic`：合成測試資料。
- `estimated`：解析式、代理模型或工程估算。
- `solver_result`：真實求解器完成並讀回的結果。
- `unverified`：結果檔、來源或完整性未確認。

只有求解狀態、原始日誌與實際輸出互相吻合，才可宣告已求解；工程有效性另需按案例的平衡、收斂、守恆或解析基準驗證。Mock、腳本產生成功、CSV 存在或安裝目錄存在均不等於 `solver_result`。

## 驗證與交付

- 先跑與修改範圍相符的離線測試、lint 或語法檢查；repo 預設 `pytest` 排除 integration，真機測試需明確標記並記錄環境。使用隔離暫存目錄，不依賴既有暫存資料。
- 每個真機案例記錄產品 build/release、SDK、宿主、輸入與腳本版本、單位、關注量、日誌及輸出位置；缺環境、缺授權、失敗、功能不支援和未執行分開列。
- Skill 變更驗證 frontmatter、目錄／reference 連結和專案 Skill 架構限制；不要只用標題／字串比對宣稱行為有效。
- 最終報告精確說明實際跑了什麼、結果如何、哪些結論只由靜態／mock 支持，以及仍待真機驗證的範圍。
