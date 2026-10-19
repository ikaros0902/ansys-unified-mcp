# 官方 Mixing Elbow：準備與求解分離

來源：[新版水密幾何工作流](https://fluent.docs.pyansys.com/version/stable/user_guide/meshing/new_meshing_workflows.html)；[官方範例資料](https://github.com/ansys/example-data/tree/main/pyfluent/mixing_elbow)（MIT）；[PyFluent](https://github.com/ansys/pyfluent)（MIT；保留固定版本 LICENSE）。

## 輸入／輸出與版本路由

`scripts/run_mixing_elbow_e2e.py` 匯入時不下載、不啟動。保留 `run_mixing_elbow_simulation` 入口，但預設 phase=prepare 且授權旗標皆 False。CLI：
`--phase prepare --version 251|252|261 --allow-launch --allow-model-changes`。此命令會啟動產品並修改新網格模型，須已有兩項授權；不初始化、不求解。PMDB 以 `examples.download_file("mixing_elbow.pmdb", "pyfluent/mixing_elbow")` 取得，亦可 `--geometry-file` 指向已核對本機檔。輸入單位 in；輸出非空 `mixing_elbow.msh.h5`。既有同名輸出拒絕覆寫。

251／252 使用 `workflow.TaskObject` 與 Execute/Arguments；261 使用 `watertight(legacy=False)` 與新版 task callable。已唯讀檢查本機 PyFluent 0.42.1 的 `Meshing.watertight(legacy=None)` 與 `BaseMeshing._fallback_check`：<=252 legacy、>=261 新版；launch 使用 `ui_mode`，不使用已移除的 show_gui。這只是 API 檢查，三版均未實跑。

`--phase solve --case-file <已配置.cas.h5> --allow-launch --allow-model-changes --allow-solve` 明確讀取已完成物理設定的 case，初始化與迭代後寫出非空 case/data；`--iters` 預設150。prepare 的 mesh 尚未包含材料／模型／邊界條件，不能直接當 solve case。修改模型授權後應依官方 mixing elbow solver 範例設定流體、水／能量／湍流與實際 inlet/outlet zone 名稱，讀回確認，另存 case 後再授權求解。

## 可觀察驗收

prepare 驗收包含實際輸入 hash、工作流版本、非空 mesh、正體積與網格品質報告；輸出檔存在僅代表已輸出，不能推定品質通過。solve 驗收包含 raw Fluent log、實際迭代數、殘差／出口溫度監控與經建立的入口／出口 mass-flow reports、case/data 檔。依該工況設定質量守恆與監控穩定門檻；不得在報表未建立／讀取失敗時宣稱物理通過。本腳本只負責階段隔離與存檔，物理品質仍需上述報告驗收。

## 取得紀錄與版本

輸入只由產品 examples/download API 或 `ansys.tools.common.example_download.download_manager` 取得；既有本機資料先核對來源，不在技能內封裝二進位。保留下載 URL、上游 commit/tag、SDK 版本、產品版本與時間；下載完成用 `Get-FileHash -Algorithm SHA256 <檔案>` 記錄每個輸入與輸出，不能以檔名取代版本。需要固定內容時將官方 URL 的 main/stable/dev 換為已核對的 commit/tag。僅下載當次需要的檔案，不下載整庫或大模型。

目標產品 v251／v252／v261；本次均未啟動產品、未完成跨版行為驗證。SDK 能載入與官方頁面結果不代表本機產品已驗收；先記錄可用 API／後端版本，缺少能力時明確停止。例子下載授權與 ANSYS 產品執行授權分開：啟動、模型修改、求解／DOE 各按使用者既有授權執行，閱讀本文件不授權執行它們。

