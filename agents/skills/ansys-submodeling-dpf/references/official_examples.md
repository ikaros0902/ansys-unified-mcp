# 官方 RST 與 LS-DYNA DPF 讀取範例

來源：[Import a result file in DPF](https://dpf.docs.pyansys.com/version/stable/tutorials/import_data/import_result_file.html)；[PyDPF-Core](https://github.com/ansys/pydpf-core) 與 [example-data](https://github.com/ansys/example-data) 均為 MIT（固定版本並保留 LICENSE）。

## 輸入與資料形狀

靜態範例由 `ansys.dpf.core.examples.find_static_rst()` 定位 static.rst；`dpf.Model(path)` 讀取 mesh/result/time metadata，再依實際可用結果提取 displacement/stress fields。DPF 服務啟動依授權，讀既有結果不需重新求解。

LS-DYNA 使用 `examples.download_d3plot_beam()` 取得 d3plot、所有分段檔與 file.actunits。DataSources 主檔 key 為 d3plot，單位輔助檔以 `add_file_path(..., key="actunits")` 加入。不能只複製主檔、以固定 list index 猜 actunits，或在無單位資訊時默認 SI；以實際檔名分辨，檔案缺失即停止定量比較。

## 可觀察驗收

輸出 result_info、mesh 節點／元素數、time_freq_support、field location/scoping/component_count／unit 與有限數值檢查。DPF 可讀不代表子模型插值通過：若進一步映射，另核對切面座標單位、原 mesh/scoping 與形函數插值覆蓋率。RST 與 d3plot 使用不同的結果語意，不以同名欄位假設等價。本範例只讀既有結果，不執行全域或子模型求解。

## 取得紀錄與版本

輸入只由產品 examples/download API 或 `ansys.tools.common.example_download.download_manager` 取得；既有本機資料先核對來源，不在技能內封裝二進位。保留下載 URL、上游 commit/tag、SDK 版本、產品版本與時間；下載完成用 `Get-FileHash -Algorithm SHA256 <檔案>` 記錄每個輸入與輸出，不能以檔名取代版本。需要固定內容時將官方 URL 的 main/stable/dev 換為已核對的 commit/tag。僅下載當次需要的檔案，不下載整庫或大模型。

目標產品 v251／v252／v261；本次均未啟動產品、未完成跨版行為驗證。SDK 能載入與官方頁面結果不代表本機產品已驗收；先記錄可用 API／後端版本，缺少能力時明確停止。例子下載授權與 ANSYS 產品執行授權分開：啟動、模型修改、求解／DOE 各按使用者既有授權執行，閱讀本文件不授權執行它們。

