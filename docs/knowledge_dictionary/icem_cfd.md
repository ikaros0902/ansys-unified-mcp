# ICEM CFD 知識字典

> 2026-11-02 核讀：本機 ICEM_CFD 目錄的唯一 PDF 是誤歸檔的 Apple Xgrid Guide；本輪另讀 16 個公開官方 HTML，頁尾均為 Release 2026 R1（v261）。以下為有界繁中摘要。官方 HTML 全文尚未本機快取；可檢索的是本頁摘要，完整手冊、逐項 API 與所有圖表仍未覆蓋。

## 來源覆核與文件入口

`xgridguide.pdf` 抽取正文顯示 Apple Computer, Inc.、2004 與 Xgrid，內容談 Mac OS X 的 grid／job 管理。正式 SQLite 已將 `ansys_b5063da81b499621e083373c` 歸為 `general`；來源清冊也應同步修正產品欄。原 PDF 與轉換文字保留，不用於 ICEM CFD 技術敘述。[錯誤歸檔原件](../ANSYS_Document/ICEM_CFD/unknown/manuals/xgridguide.pdf)。

官方 [User's Manual](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/icm_user/icm_user.html) · `official_icem_user_v261` 提供 geometry、tetra／prism／hexa、檢查、solver output 與 Workbench 主題；[Programmer's Guide](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/icm_pguide/icm_pguide.html) · `official_icem_programmer_v261` 是 Tcl/Tk scripting、geometry／blocking／meshing／output functions 的文件入口。目錄存在不代表已核讀每個命令。

## 1. 網格流程與幾何準備

基本流程是建立工作目錄／專案、匯入幾何、必要的修補與 blocking、生成網格、檢查／編輯、定義物理，再產生 solver input。Geometry Preparation 指出 tetra mesher 需要封閉體積；若幾何孔洞大於局部 tetra 尺度，可能無法成網。Build Topology 可先辨識問題，並建立擷取特徵所需的曲線／點。這不是所有幾何都可不修補的保證。

來源：[General Meshing Workflow](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/icm_user/iuser_intro_process.html) · `official_icem_workflow_v261`；[Geometry Preparation](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/icm_user/iuser_intro_geom_prep.html) · `official_icem_geometry_v261`。

## 2. Hexa blocking、premesh 與策略

Blocking 是以幾何投影控制網格的環境，適用於部分區域的 structured hexa（2D 為 quad）。先產生與改善 premesh，再轉成 structured 或 unstructured mesh，供合併或傳入 solver。

| 策略 | v261 正文界線 |
|---|---|
| Top Down | 從 3D bounding box 的單一 block 開始，以 split／delete／merge／move 形成拓樸；初始 CAD association 需人工控制 |
| Bottom Up／3D MultiZone | 從 CAD surface structure 建立 blocking faces，再嘗試形成 mapped、swept 或 free blocks；不保證全 hexa |

可以混用兩種策略。品質不足時需調整 topology／mesh sizes；本頁未提供跨模型通用的品質門檻。

來源：[Blocking the Geometry](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/icm_user/iuser_intro_blocking.html) · `official_icem_blocking_v261`；[Blocking Strategy](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/icm_user/iuser_blockingstrategy.html) · `official_icem_blocking_strategy_v261`。

## 3. Tetra/Mixed 方法與 Fluent Meshing 授權

| 方法 | 生成方向與前提 |
|---|---|
| Robust（Octree） | top-down 生成 volume mesh，再貼合幾何並建立 patch-independent boundary surface mesh |
| Quick（Delaunay）／Smooth（Advancing Front） | bottom-up；需要封閉 surface mesh，若尚無則由幾何生成 |
| Fluent Meshing | 由 ICEM CFD 以 batch 呼叫 Fluent；可處理 inflation／hexa core 選項，需啟用 Fluent Meshing 的 license key |

官方列出 `ansys`、`mech_2`、`mech_1`、`preppost`、`dyna` keys 不支援該 Fluent Meshing 選項。沒有幾何時會做純 tetra 而不 inflation；輸入 surface mesh 的 volume 應以 material points 標記。這些限制不能由一般 ICEM CFD license 推定解除。

來源：[Choosing the Tetrahedral Mesh Method](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/icm_user/iuser_tetra_methods.html) · `official_icem_tetra_v261`。

## 4. Prism pre inflation／post inflation

Post inflation 在 boundary shells 與既有 tetra 之間生長 prism，過程可能移除 tetra 並 smooth，以保持與 volume mesh 的 conformal 連接。Pre inflation 先由 surface mesh 生長 boundary layers，再填入剩餘 volume；已有 volume mesh 時會先移除。Pre inflation 經 Fluent Meshing batch 執行，需 volume mesh 或 material point 決定生長方向；同一材料被內部壁面分成多區時，官方要求先有初始 volume mesh。兩種演算法不應被假設產生相同結果。

來源：[Prism Mesh Process](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/icm_user/iuser_prismprocess.html) · `official_icem_prism_v261`；[Choosing the Tetrahedral Mesh Method](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/icm_user/iuser_tetra_methods.html) · `official_icem_tetra_v261`。

## 5. 網格診斷與品質 histogram

`Edit Mesh > Check Mesh` 分別列 Errors 與 Possible problems，可建立 subsets 或逐項 Check/fix。編輯後應重新執行診斷，確認沒有引入錯誤。

`Display Mesh Quality` 可選 mesh types、elements 與 Quality criterion，再用 histogram 定位元素。User's Manual 的一般 quality 圖以 0 代表差、1 代表好；Help Manual 另列 Aspect Ratio、Determinant、Equiangle Skewness、Orthogonal Quality 等不同準則。實際檢查應記錄選定 criterion，不能把一般圖示範圍當成所有指標的統一驗收門檻。

來源：[Checking the Mesh](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/icm_user/iuser_checkmesh.html) · `official_icem_check_v261`；[Quality Metrics](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/icm_user/iuser_qualitymetrics.html) · `official_icem_quality_v261`；[Display Mesh Quality](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/icm_help/iedit_meshquality.html) · `official_icem_display_quality_v261`。

## 6. Replay 錄製、錯誤與清理風險

Replay Control 將互動操作記成 Tcl/Tk 命令，可編輯 `.rpl` 並以 Do one／Do all／Do range 執行。`Ignore errors` 預設停用，遇錯停止；啟用後跳過錯誤命令繼續執行。`Always update` 控制每步或末尾更新。官方建議使用已文件化的 `ic_` functions，避免依賴可能變動的未文件化 Tcl functions。

2D Car 教學給出的 batch 入口是 `icemcfd-batch-script replay-file.rpl`。`Clean` 依 filter 刪除行；教學提醒 `ic_undo` 行可能與 backtracking 有關，保留較長 replay 通常較安全。Help 另指出錄製期間的 Undo 區段需要人工處理，不能假設 Clean 已處理完整。這些是來源操作說明，本輪未執行 replay。

來源：[Replay Scripts](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/icm_help/icm_mm_replayscripts.html) · `official_icem_replay_v261`；[2D Car Replay Tutorial](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/icm_tut/hexa_2dcar_use_replay.html) · `official_icem_replay_tutorial_v261`。

## 7. Workbench Update 與儲存時點

Data-integrated ICEM CFD 可接 Geometry／Mesh／Mechanical Model 上游並連到 CFX、Polyflow Classic、FENSAP-ICE、Mechanical APDL 等下游。Editor 修改須儲存 project／tetin／blocking／Replay 後，Workbench 才會標出過期狀態。

| 條件 | v261 Update 行為 |
|---|---|
| 無 Replay、無 blocking | 預設 tetra mesher |
| 無 Replay、有 blocking | 預設 hexa mesher |
| 有 Replay | mesh input parameters 在執行前設定；blocking parameters 在執行後且 blocking 存在時設定 |
| ICEM CFD 專案仍開啟 | mesh 與 project 需人工儲存；關閉專案後從 Workbench Update 才由該流程儲存 |

含 Workbench input parameters 且需逐行執行時，使用 One-click menu 的 Workbench Replay Control。

來源：[Workbench ICEM CFD](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb2_help/wb2h_IcemCFD.html) · `official_icem_workbench_v261`；[Replay Scripts](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/icm_help/icm_mm_replayscripts.html) · `official_icem_replay_v261`。

## 8. General 設定、journal 與檔名

`File > Settings > General` 可指定 processors；v261 範圍為 0–256、預設 1，0 表示採可用最大數，實際效能仍依操作與機器。Temporary Directory 必須先存在，使用 UNIX-style 路徑分隔，ICEM CFD 不會代建目錄。

`Record Journal File` 以 `.jrf` 保存 session 的 Tcl/Tk 操作，可供除錯；`Keep existing file names` 控制另存專案時是否沿用幾何／網格等檔名。未啟用時，新專案名稱會建立相應名稱的檔案。`Clean up Temporary Files` 會清理專案暫存檔，操作前需確認所需資料已保留。

來源：[General Settings](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/icm_help/icm_mm_general.html) · `official_icem_general_v261`。

## 9. FEA／CFD solver output 分工

FEA Solve Options 用於結構分析設定，可選 Ansys、Nastran、ABAQUS、Autodyn、LS-DYNA；附加參數與 analysis types 依 solver 決定。`Write/View Input File` 產生／檢視輸入檔，`Submit Solver Run` 才是送交求解的動作。Output Mesh 用於 CFD 與支援格式匯出；先選 Output Solver，再設定 boundary conditions／其他參數並寫檔。格式相容性需另查該 solver 的 Output Interfaces，不能由檔案可寫出推定解算設定正確。

來源：[Sending Data to a Solver](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/icm_user/iuser_solveoptions.html) · `official_icem_output_v261`。

## 尚未覆蓋

官方 User／Help／Tutorial／Programmer 全文未本機快取，Tcl API 未逐項整理，CAD interfaces／各 solver output formats／全部品質公式與圖表尚未驗收；tutorial input files、版本差異與 runtime 均未測。本頁未啟動 ICEM CFD 或 solver。團隊分享前仍需確認官方原文及衍生內容的使用範圍。


## 2026-11-04：Wave 9 本機來源盤點與限制說明

本批完成 icem_cfd 模組既有本機 catalog 文件（共 1 筆）與 sources 清冊（共 16 筆）之完整雜湊、正文路徑與標籤結構核對。本機未快取或具備企業授權/登入限制之線上主題誠實標記為缺口（保持現有非 complete 狀態），未擅自虛構未核實之線上 API 簽名或執行求解運算。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/icem_cfd_module_conversion_report_20261104.md)。
