# 官方 STEP／Named Selection 流轉驗收

來源、授權、版本／hash 紀錄與 STEP → PMDB → Mechanical 操作共用 [Geometry 官方範例](../../ansys-geometry-modeling/references/official_examples.md)。

輸入是官方 twoCars.stp 與明確的 NS 名稱／幾何成員；輸出為 PMDB 與 Mechanical 讀回的 NS/scoping 清單。先驗證官方命名選擇可保留，再依本技能命名契約建立 RM/contact；官方例子不會自動生成 Scr_RM_grp 群組，不能以檔案匯入成功宣稱 Joint／Contact 正確。

可觀察驗收：名稱、成員幾何／數量、空群組與重複群組檢查；匯出與匯入模型修改按既有授權執行，無需求解。目標 v251／v252／v261 均未於本次實跑。

## 取得紀錄與版本

輸入只由產品 examples/download API 或 `ansys.tools.common.example_download.download_manager` 取得；既有本機資料先核對來源，不在技能內封裝二進位。保留下載 URL、上游 commit/tag、SDK 版本、產品版本與時間；下載完成用 `Get-FileHash -Algorithm SHA256 <檔案>` 記錄每個輸入與輸出，不能以檔名取代版本。需要固定內容時將官方 URL 的 main/stable/dev 換為已核對的 commit/tag。僅下載當次需要的檔案，不下載整庫或大模型。

目標產品 v251／v252／v261；本次均未啟動產品、未完成跨版行為驗證。SDK 能載入與官方頁面結果不代表本機產品已驗收；先記錄可用 API／後端版本，缺少能力時明確停止。例子下載授權與 ANSYS 產品執行授權分開：啟動、模型修改、求解／DOE 各按使用者既有授權執行，閱讀本文件不授權執行它們。

