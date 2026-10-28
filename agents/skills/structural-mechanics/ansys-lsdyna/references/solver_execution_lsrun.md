# LS-Run 求解執行參數對應 (`solver_execution_lsrun.md`)

LS-Run 是 LS-DYNA 求解器的命令產生與排隊工具，本質上只是把 GUI 填的欄位組成一行求解器命令。這份文件把 LS-Run 的設定對應到 `dyna_solve`（`products/dyna/tools.py`）的參數，方便知道目前工具支援到哪、缺口在哪。出處一律標章節，查無章節的標「未驗證」。

## 一、License（手冊 §2.1 Licensing，Chapter 3 LS-DYNA Parallel Processing Capabilities）

License type 預設 `ANSYS`，適用於隨 Ansys 安裝取得的 LS-DYNA。

> 原文（`LS-Run_Users_Guide` chunk #9）：「To use either of these features [SMP or MPP], you must purchase the appropriate number of Ansys LS-DYNA HPC licenses. The HPC license incorporates both SMP and MPP capabilities.」

**SMP 與 MPP 平行運算都需要 Ansys LS-DYNA HPC license**（兩者算在同一種授權裡），不是只有 MPP 才需要。

## 二、NCPU 與一致性（手冊 §2.3 Setting Command Line Options，`LS-Run_Users_Guide` chunk #7）

> 原文：「NCPU: Enter the number of processes that you want to use to run your job. For an SMP solution, if you enter a negative number it will cause the job to be run in a manner that will give you consistent results but will take longer.」

- 負的核心數：SMP 求解器會用保證結果一致（reproducible）的方式跑，但耗時更長。手冊沒有給出具體的時間增幅百分比；若投影片提到「最多多 15% CPU 時間」，那是訓練教材的經驗值，不是手冊原文，使用前應視為估計值。
- `Max running proc.`（LS-Run 設定）用來限制本機佇列同時運行的行程數上限（0 代表不限制）。手冊沒有給出「設成實體核心數」這類具體建議值，此處不做該項建議，避免無出處的推論。

**對應 `dyna_solve` 現況**：目前簽名 `(k_file_path, ncpu=4, memory="100m", working_dir="", dry_run=False, timeout=300.0, precision="dp")`，`facade.py` 直接把 `ncpu` 原值組進命令字串 `ncpu={ncpu}`。負值會被原樣傳下去，`dyna_solve` 的 docstring 已說明此用法（見 `products/dyna/tools.py`），不改變預設行為。

## 三、Precision 與求解器變體（手冊 §2.2.5 Defining Version Presets，`LS-Run_Users_Guide` chunk #4）

> 原文：「LS-DYNA 16.1 is the version that is installed in 2026 R1. The following presets are defined with their associated SOLVER and Expression: SMP single-precision / SMP double-precision / MPP single-precision with IntelMPI / MPP double-precision with IntelMPI / MPP single-precision with MS-MPI (not applicable on Linux) / MPP double-precision with MS-MPI (not applicable on Linux)」

- 內建 6 種 Preset：SMP、MPP(IntelMPI)、MPP(MS-MPI) 各有單精度(SP)/雙精度(DP)。MS-MPI 僅限 Windows。
- Preset 的 `Expression`（命令模板，含 `$SOLVER $INPUT $NCPU $MEMORY` 等變數）展開後就是 `Preview` 顯示的實際執行命令——這一行等價於 `dyna_solve` 最終組出的命令字串。

**對應 `dyna_solve` 現況**：`facade.find_dyna_solver(precision=...)` 支援 `"dp"`（預設，優先找 `lsdyna_dp.exe`）與 `"sp"`（優先找 `lsdyna_sp.exe`），找不到對應精度會回退搜尋其他候選檔名；`dyna_solve` 的 `precision` 參數對應此行為。目前仍未支援 SMP/MPP 或 Intel MPI/MS-MPI 的切換邏輯（求解器執行檔路徑偵測邏輯不分這兩種平行模式）。

## 四、記憶體（手冊 §2.3 Setting Command Line Options，`LS-Run_Users_Guide` chunk #7）

`MEMORY` 欄位開 `AUTO` 時，LS-Run 依模型的節點數估算所需記憶體；手動模式則由使用者自訂（原文：「If memory toggle AUTO=ON, LS-Run will estimate the required memory for the analysis... The estimate is made from the number of nodes in the current model.」）。`dyna_solve` 目前的 `memory` 參數是字串直接傳遞（如 `"100m"`），沒有 AUTO 估算邏輯，使用者需自行決定數值。

## 五、Sense Switch 與中止/續算（手冊 §4.2 Using Sense Switches during Simulation，`LS-Run_Users_Guide` chunk 17）

> 原文：「LS-DYNA sense switches can be sent to the selected job during the simulation by creating a sense switch file (d3kil) in the input file directory. ... A job stopped with "sw1" will create a d3dump file. This file can be used to continue the simulation by doing a simple restart analysis.」

- 中止求解的機制是：在輸入檔案所在目錄建立一個叫 `d3kil` 的檔案，LS-DYNA 求解器會偵測到並依其內容觸發對應的 sense switch 動作。
- 用 `sw1` 停止的任務會產生 `d3dump`（重啟檔），可以用「simple restart」接續運算。
- 完整的 sense switch 代碼表在《LS-DYNA Keyword User's Manual Volume I》，本次查證只確認 `sw1` 這一個代碼，其他代碼（如 sw2/sw3）**未驗證**。

**對應現況**：`dyna_solve` 和既有的 `sentinel_tools.py`（`submit_simulation_job` / `get_simulation_status` / `tail_simulation_log` / `abort_simulation_job`）都沒有「往輸入目錄寫 `d3kil`」這個動作。按 WP5 決定不新增工具，用這份文件說明做法：需要中止時，往求解輸入目錄寫一個檔名為 `d3kil`、內容為對應 sense switch 代碼的文字檔。

## 六、Job Table 與輸出（手冊 §4.1 The Job Table、§2.4.3 Starting a Job in a Command Window、§4.3 Post Simulation Actions）

- Job 依加入順序啟動，但要等資源釋出且相依的 job 完成（Normal Termination）才會真的開始跑（§4.1）。
- 關閉 Command window 選項時，求解輸出導向 `lsrun.stdout.txt`（§2.4.3）。
- **Re-run 會先刪除既有的 LS-DYNA 結果檔，再用相同命令重跑**（§4.3）。這是破壞性動作，執行前要確認不需要保留舊結果。

**對應現況**：`sentinel_tools.py` 的 `submit_simulation_job`/`get_simulation_status`/`tail_simulation_log`/`abort_simulation_job` 已經覆蓋非同步提交、查狀態、讀日誌尾段、中止，功能上對應 Job Table 的大部分能力，不需要重複建置。

## 七、遠端 / 叢集前置條件（手冊 §2.2.4 Setting up Remote Execution / Chapter 3，只列通則，不含任何機器名稱或帳號）

> 原文（`LS-Run_Users_Guide` chunk #4）：「Map local directory: A common file system must exist on client and server... Map local dir [H:\project] to [/disk/proj].」

- 本機與遠端需要共用檔案系統，並在設定中把本機路徑對應到遠端路徑（例：本機 `H:\project` 對應遠端 `/disk/proj`）。
- 叢集內各節點須是同型機器、同作業系統層級、同晶片組與互連；每台都要能遠端登入，資料夾結構一致且不可在執行中改名。
- 每個節點須安裝相同版本的 Ansys（或掛同一個 NFS/UNC 共用安裝），且 MPI 軟體版本在所有節點一致。
