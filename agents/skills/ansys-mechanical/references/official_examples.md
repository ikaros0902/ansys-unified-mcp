# 官方 AGDB 靜態結構範例

來源：[Static structural analysis](https://examples.mechanical.docs.pyansys.com/examples/00_basic/example_01_simple_structural_solve.html)；資料：[ansys/example-data](https://github.com/ansys/example-data)（MIT，保留該版本 LICENSE）；程式來源：[pymechanical-examples](https://github.com/ansys/pymechanical-examples)（MIT，核對固定版本 LICENSE）。不複製整篇範例。

## 輸入、步驟與可觀察驗收

以 `ansys.mechanical.core.examples.download_file("example_01_geometry.agdb", "pymechanical", "00_basic")` 取得 AGDB。輸入包含檔案路徑／hash、具名選擇、座標系統、材料與載荷單位。連線既有 Mechanical 後上傳資料至遠端 project_directory，遠端路徑不能直接使用 CPython 本機路徑。

模型修改授權後，依官方範例建立 Static Structural、匯入具名選擇／座標系統、設定 MKS、網格、支承與 remote force／thermal condition；建立 Directional/Total Deformation 與反力結果。先輸出實際 NS 名稱、scoping 數量、材料、網格節點／元素數與載荷清單，缺漏即停止。不可將官方固定 children index 套用至使用者模型。

求解另行授權後才呼叫 `Solution.Solve(True)`。輸出 solve.out、結果檔、Directional Deformation 的 Minimum/Maximum/Average（含單位）與反力；確認求解狀態及檔案非空，再與同一輸入／版本的官方結果比較。官方公開輸出約 0.104 m 僅作該工況參考，不能當所有模型的固定驗收值，也不以「完成呼叫」取代收斂證據。

## 取得紀錄與版本

輸入只由產品 examples/download API 或 `ansys.tools.common.example_download.download_manager` 取得；既有本機資料先核對來源，不在技能內封裝二進位。保留下載 URL、上游 commit/tag、SDK 版本、產品版本與時間；下載完成用 `Get-FileHash -Algorithm SHA256 <檔案>` 記錄每個輸入與輸出，不能以檔名取代版本。需要固定內容時將官方 URL 的 main/stable/dev 換為已核對的 commit/tag。僅下載當次需要的檔案，不下載整庫或大模型。

目標產品 v251／v252／v261；本次均未啟動產品、未完成跨版行為驗證。SDK 能載入與官方頁面結果不代表本機產品已驗收；先記錄可用 API／後端版本，缺少能力時明確停止。例子下載授權與 ANSYS 產品執行授權分開：啟動、模型修改、求解／DOE 各按使用者既有授權執行，閱讀本文件不授權執行它們。

