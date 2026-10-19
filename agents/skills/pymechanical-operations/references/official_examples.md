# 官方 AGDB 遠端操作範例

工作流、輸入／輸出、官方 URL、授權與版本紀錄共用 [Mechanical 官方靜態結構範例](../../ansys-mechanical/references/official_examples.md)，只在需驗證 gRPC 上傳、遠端腳本與下載結果時讀取。

CPython 用產品 `examples.download_file` 取得 AGDB，`mechanical.upload` 後以遠端 project_directory 組路徑。將 ACT 原文交給 `run_python_script`，不要在 ACT import 本專案 CPython 套件。連線與模型準備並不授權 `Solution.Solve`。

可觀察驗收：遠端回傳的輸入路徑存在、模型／NS/scoping 實際讀回符合要求；求解僅經另行授權後進行，下載 solve.out 與非空結果並保留 raw return/錯誤。目標 v251／v252／v261 均未在本次實跑；詳見共用紀錄方法。

## 取得紀錄與版本

輸入只由產品 examples/download API 或 `ansys.tools.common.example_download.download_manager` 取得；既有本機資料先核對來源，不在技能內封裝二進位。保留下載 URL、上游 commit/tag、SDK 版本、產品版本與時間；下載完成用 `Get-FileHash -Algorithm SHA256 <檔案>` 記錄每個輸入與輸出，不能以檔名取代版本。需要固定內容時將官方 URL 的 main/stable/dev 換為已核對的 commit/tag。僅下載當次需要的檔案，不下載整庫或大模型。

目標產品 v251／v252／v261；本次均未啟動產品、未完成跨版行為驗證。SDK 能載入與官方頁面結果不代表本機產品已驗收；先記錄可用 API／後端版本，缺少能力時明確停止。例子下載授權與 ANSYS 產品執行授權分開：啟動、模型修改、求解／DOE 各按使用者既有授權執行，閱讀本文件不授權執行它們。

