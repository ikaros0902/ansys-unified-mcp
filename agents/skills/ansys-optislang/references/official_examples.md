# 官方 Oscillator sensitivity／MOP optimization

來源：[Oscillator sensitivity and optimization on MOP](https://optislang.docs.pyansys.com/version/stable/examples/gallery_examples/run_python_script/02_4_oscillator_MOP_sensitivity_and_optimization.html)；[PyOptiSLang](https://github.com/ansys/pyoptislang)（MIT，保留 SDK 固定版本 LICENSE）。

## 輸入／輸出與階段

以 `ansys.optislang.core.examples.get_files("oscillator_sensitivity_mop")` 與 `get_files("oscillator_optimization_on_mop")` 取得 SDK 隨附範例路徑，先確認每組主腳本及相依檔案存在並記錄 hash。不複製全文。

Optislang() 可能啟動產品，需既有啟動授權。模型修改授權後，依序以 `osl.application.project.run_python_file(paths[0])` 建立 sensitivity 與 optimization on MOP，先讀回參數、response、流程節點／連結與設計範圍，再另存新專案。不得覆蓋使用者既有專案。

`osl.application.project.start()` 會執行 DOE／MOP／最佳化，不是純模型準備，須另行計算授權；勿在匯入範例後自動呼叫。

## 可觀察驗收

prepare：非空 opf、參數／response/scoping 與實際流程圖。run：原始執行狀態、完成／失敗設計數、CoP 與訓練／驗證誤差、最佳設計及約束符合性；對最佳設計以原始模型獨立重算需相應授權。MOP prediction 或 UI 綠燈本身不能當原模型驗證通過。

## 取得紀錄與版本

輸入只由產品 examples/download API 或 `ansys.tools.common.example_download.download_manager` 取得；既有本機資料先核對來源，不在技能內封裝二進位。保留下載 URL、上游 commit/tag、SDK 版本、產品版本與時間；下載完成用 `Get-FileHash -Algorithm SHA256 <檔案>` 記錄每個輸入與輸出，不能以檔名取代版本。需要固定內容時將官方 URL 的 main/stable/dev 換為已核對的 commit/tag。僅下載當次需要的檔案，不下載整庫或大模型。

目標產品 v251／v252／v261；本次均未啟動產品、未完成跨版行為驗證。SDK 能載入與官方頁面結果不代表本機產品已驗收；先記錄可用 API／後端版本，缺少能力時明確停止。例子下載授權與 ANSYS 產品執行授權分開：啟動、模型修改、求解／DOE 各按使用者既有授權執行，閱讀本文件不授權執行它們。

