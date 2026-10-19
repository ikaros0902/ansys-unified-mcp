# 官方 STEP → Named Selection → PMDB

來源：[官方具名選擇流轉範例](https://geometry.docs.pyansys.com/version/stable/examples/04_applied/04_mechanical_named_selections.html)；輸入：[twoCars.stp](https://github.com/ansys/pyansys-geometry/blob/main/tests/integration/files/import/twoCars.stp)。PyAnsys Geometry 原始碼／此檔由該儲存庫 MIT LICENSE 管理，固定 commit 並保留授權。

## 輸入與操作界線

官方 STEP 位於 pyansys-geometry，而非 example-data；優先檢查本機產品 examples downloader 是否支援該來源，否則依官方固定 commit 的單檔 URL 取得；不要把錯誤路徑傳給 example-data downloader，也不複製整份 notebook。記錄 STEP hash、實體數／名稱、NS 名稱／實體 ID 與單位。

連線既有服務時保留使用者明確 transport；未指定則由 SDK 能力自動選擇，不以 Windows 一律強制 wnua。新啟動另需授權。模型修改授權後 open_file(STEP)、建立具名選擇並 export_to_pmdb；Mechanical 匯入時啟用 ProcessNamedSelections，再讀回名稱與實際 scoping。官方嵌入 Mechanical App 的預設也會啟動產品，不得閱讀範例時直接執行。

## 可觀察驗收

STEP 與 PMDB 皆非空，匯出前後實體數／NS 名稱與 scoping 數量符合預期；PMDB 在 Mechanical 匯入後重讀具名選擇，保留讀回證據。實體 ID 可能因格式轉換改變，應比對成員幾何與數量，不能只比名稱。只輸出 PMDB 不代表 Mechanical 流轉已驗收。本流程不需求解。

## 取得紀錄與版本

輸入只由產品 examples/download API 或 `ansys.tools.common.example_download.download_manager` 取得；既有本機資料先核對來源，不在技能內封裝二進位。保留下載 URL、上游 commit/tag、SDK 版本、產品版本與時間；下載完成用 `Get-FileHash -Algorithm SHA256 <檔案>` 記錄每個輸入與輸出，不能以檔名取代版本。需要固定內容時將官方 URL 的 main/stable/dev 換為已核對的 commit/tag。僅下載當次需要的檔案，不下載整庫或大模型。

目標產品 v251／v252／v261；本次均未啟動產品、未完成跨版行為驗證。SDK 能載入與官方頁面結果不代表本機產品已驗收；先記錄可用 API／後端版本，缺少能力時明確停止。例子下載授權與 ANSYS 產品執行授權分開：啟動、模型修改、求解／DOE 各按使用者既有授權執行，閱讀本文件不授權執行它們。

