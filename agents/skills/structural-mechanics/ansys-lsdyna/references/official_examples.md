# 官方 Taylor Bar deck 準備

來源：[Taylor bar example](https://dyna.docs.pyansys.com/version/dev/examples/Taylor_Bar/plot_taylor_bar.html)；[PyDYNA](https://github.com/ansys/pydyna) 與 [example-data](https://github.com/ansys/example-data)（MIT，核對固定版本 LICENSE）。dev 範例含運算，不能整篇直接執行。

## 輸入／輸出與授權

以 `ansys.tools.common.example_download.download_manager.download_file("taylor_bar_mesh.k", "ls-dyna/Taylor_Bar")` 取得網格；依官方 cards 在本機生成 input.k，保持 include 相對路徑且將網格放在同一工作目錄。準備階段只解析／匯出 deck，不啟動求解器。

PyDYNA >=0.11 已移除 `ansys.dyna.core.run`／pre；不要複製舊 run API。實際求解在使用者另行授權後，走專案既有產品求解入口或已核對版本的 solver launcher；不能因生成 deck 成功自動求解。範例的多次參數試算也屬求解授權範圍。

## 可觀察驗收

prepare：input.k 與 include 非空、include 可解析、節點／單元／材料／part 連結完整、時間與單位系統明確，保留輸入 hash 與 cards 摘要。solve：保留原始退出碼與 solver log、正常終止標誌、非空 d3plot/glstat，依該模型核對動能轉化、變形與能量歷程。退出碼0或檔案存在不能單獨宣稱物理通過。

## 取得紀錄與版本

輸入只由產品 examples/download API 或 `ansys.tools.common.example_download.download_manager` 取得；既有本機資料先核對來源，不在技能內封裝二進位。保留下載 URL、上游 commit/tag、SDK 版本、產品版本與時間；下載完成用 `Get-FileHash -Algorithm SHA256 <檔案>` 記錄每個輸入與輸出，不能以檔名取代版本。需要固定內容時將官方 URL 的 main/stable/dev 換為已核對的 commit/tag。僅下載當次需要的檔案，不下載整庫或大模型。

目標產品 v251／v252／v261；本次均未啟動產品、未完成跨版行為驗證。SDK 能載入與官方頁面結果不代表本機產品已驗收；先記錄可用 API／後端版本，缺少能力時明確停止。例子下載授權與 ANSYS 產品執行授權分開：啟動、模型修改、求解／DOE 各按使用者既有授權執行，閱讀本文件不授權執行它們。

