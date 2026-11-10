# Ansys CFX 與 PyCFX 主題字典

本頁整理 PyCFX `ansys-cfx-core 0.3.0` 的 session／啟動／範例，以及本機 CFX-Solver Modeling／Theory Guide 的 v251（2025 R1）、v261（2026 R1）有界主題與章節入口。PyCFX stable 網頁的產品 release 維持 `unknown`；PDF 版本則依封面標示，不能由 SDK 版號推定其他 CFX 安裝的相容性。

## PyCFX 的三類 session

PyCFX 0.3.0 文件列出三種 session，分別包裝 CFX-Pre、CFX-Solver 與 CFD-Post：

| Session | 用途 | 常見建立方式 |
| --- | --- | --- |
| `PreProcessing` | 連接 CFX-Pre，設定模擬；其 `setup` hierarchy 對應 CFX-Pre 的 CCL 結構。 | `pycfx.PreProcessing.from_install()`，再以 `file.open_case(file_name=...)` 開啟 `.cfx` case。 |
| `Solver` | 控制 CFX-Solver；可由安裝啟動，或從 preprocessing session 擷取設定建立。 | `pycfx.Solver.from_install(solver_input_file_name=...)`，或 `pycfx.Solver.from_session(pypre)`。 |
| `PostProcessing` | 連接 CFD-Post，載入結果並建立後處理物件。 | 可用結果檔建立，或由 solver session 建立：`pycfx.PostProcessing.from_session(pysolve)`。 |

PreProcessing 與 PostProcessing 都提供階層式 `setup` 物件及 `file` 物件；設定物件名稱依 CCL object type／parameter name 轉小寫並把空格換成底線，CCL 裡的 named object 名稱及參數值則保留原字串。共同介面包括 `get_state()`、`set_state()`、`is_active()`；適用的參數還可查 `allowed_values()`、`min()`、`max()`。設定無效值會被拒絕。

本節描述 PyCFX API 文件的 session object surface，不等同 CFX Solver 物理或收斂指南。設定變更與 physics updates 的限制另見[PreProcessing state 子題](#pycfx-preprocessing-的-state-dictionary-與-physics-updates)。

來源：[PyCFX sessions guide](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/guide/905297a05e5e-session.md)（[來源清冊](sources.csv#ansys_c58523f59daaf38e134d31d7)）、[PyCFX launching guide](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/guide/3b3f3b82028d-launching_cfx.md)（[來源清冊](sources.csv#ansys_a4a0afff47aac7962b2138aa)）。官方網址使用 `version/stable`，本機文件集合 metadata 指向 SDK 0.3.0；產品安裝 release 仍為 unknown。

## 設定樹與狀態

PreProcessing 與 PostProcessing 的 `setup` 物件以階層方式映射 CFX Command Language（CCL）結構；Python 設定物件的名稱由 CCL 類型／參數名稱轉小寫並以底線取代空格，named object 名稱與參數值保留 CCL 原字串。設定物件可用 `get_state()` 讀取、`set_state()` 指定狀態，也可呼叫物件取得其子項狀態，或用 `print_state()` 檢視文字表示。參數物件可用 `allowed_values()`（適用時還有 `min()`、`max()`）查限制；`is_active()` 與 `get_active_child_names()` 可檢查目前 session 中可用的設定項，因物理設定而 inactive 的項目不應假設可操作。PreProcessing setup 節點可呼叫 `get_physics_messages()` 取得全域或局部訊息，並依 `All`、`Beta`、`Information`、`Warning`、`Error` 篩選。

PreProcessing 在逐項變更物理設定時可能連動更新相依設定。例如 domain turbulence model 從 `k epsilon` 改為 `SST` 時，`turbulent_wall_functions` 會由 `Scalable` 改為 `Automatic`。Physics updates 限於 top-level objects 及其內部相依項；domain 內的變更不會自動更新 boundary object。以 dictionary 套用 state 的版本限制、optional state 清除方式與警告詳見[PreProcessing state 子題](#pycfx-preprocessing-的-state-dictionary-與-physics-updates)。

求解啟動後可用 `solution.wait_for_run()` 等待完成。文件亦說明 CFD-Post 的長時間運算操作可能等待較久；自動化流程應依實際呼叫與執行環境安排等待與錯誤處理。

### PyCFX PreProcessing 的 state dictionary 與 physics updates

PyCFX session guide 說明，對 PreProcessing 設定物件逐項指定 physics parameter 時，CFX 可能同步更新相依參數。例如把 domain turbulence model 從 `k epsilon` 改為 `SST`，`turbulent_wall_functions` 可從 `Scalable` 自動變成 `Automatic`。Physics updates 只在 top-level objects 之間連動；在 domain 內變更設定不會自動更新 boundary object。

**Dictionary state 有版本限制：**該頁明確指出，CFX 至 2026 R1（含）若以 dictionary 呼叫 `set_state()`，physics updates 不會執行，狀態會直接套用，因此 PreProcessing 可能落入物理不一致狀態。使用此方式後須檢查 physics warnings／errors；不可只以 setter 呼叫成功判定設定有效。

`set_state()` 的 dictionary 若省略 optional objects 或 parameters，不會將它們自動移除。若要清除，文件要求明確操作：optional parameter 設為 `None`；optional object 將 `enabled=False`；optional named object 使用 `del` 移除。這些是不同物件型別的清理方式，不應假設套用一份不完整 dictionary 就等於替換整個 CCL state。

此限制依 PyCFX `version/stable` session guide 原文，來源清冊 release 為 `unknown`；其中 CFX 版本上限只採文件明載的「up to and including 2026 R1」，不推定後續版本行為。本子題整理 setter／dictionary 差異與 optional-state 清理，不代表已執行 CFX session。

來源：[Use PyCFX sessions，官方 `version/stable` 指南](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/guide/905297a05e5e-session.md)（[來源清冊](sources.csv#ansys_c58523f59daaf38e134d31d7)；SDK metadata 路徑為 0.3.0，release 維持 unknown）。

## PyCFX logging configuration

PyCFX 使用 Python 標準函式庫的 `logging` API；套件包含多個 logger，並提供標準格式的 `logging_config.yaml`，可編輯此 YAML 檔設定 logging。該頁未列出所有 logger 名稱、各 logger 的預設級別或設定檔實際搜尋路徑；需要調整時應依安裝的 PyCFX 版本及部署環境確認檔案位置與可用設定，不要自行假設套件讀取哪一份 YAML。

來源：[Configure logging，PyCFX 官方 `version/stable` 指南](https://cfx.docs.pyansys.com/version/stable/user_guide/log.html)／[本機 sidecar](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/guide/5f69c3181039-log.md)（[來源清冊](sources.csv#ansys_d64b587bf3782bedf4574901)）。來源 metadata 指向 SDK 0.3.0 文件集合，網址使用 stable，release 欄仍為 `unknown`。

## 啟動方式與 session 間資料承接

官方 launch guide 說明兩種主要 session 建立來源：

- `from_install()` 從本機安裝啟動 CFX。文件列出 `product_version`、`case_file_name`（`.cfx`）、`solver_input_file_name`（`.def`／`.mdef`）、既有 `run_directory`（`.dir`）、`results_file_name`（`.res`／`.mres`），以及傳給 `cfx5pre`、`cfx5solve` 或 `cfdpost` 的 `additional_arguments`。若不指定 `product_version`，文件表示會啟動最新支援版本。
- `from_session(existing)` 從既有 PyCFX session 建立下一種 session；新 session 繼承既有 session 的設定，包括 `product_version`。

跨階段資料時點：

1. 由 `PreProcessing` 建立 `Solver` 時，solver session 會擷取啟動當時 CFX-Pre 的 model setup。之後仍可修改原 preprocessing session，但這些變更不會改動已建立 solver session 所持有的設定。
2. 由 `Solver` 建立 `PostProcessing` 時，若 solver 已完成，結果檔會直接開啟；若尚未完成，PostProcessing session 會等待 run 完成後再讀取結果。Solver 亦可用 `solution.wait_for_run()` 等待求解完成。
3. 教學範例以 file-based 流程分別建立 PreProcessing、Solver 與 PostProcessing，並在階段間傳遞 `.def`／結果檔；不要求三個 CFX 元件必須同時存在於同一個 Python session。

**部署限制：**launch guide 明確寫 PyCFX 初版搭配 Ansys CFX 2025 R2 Service Pack 3 時，只支援在執行 Python 的同一部 local machine 啟動 CFX session。這是來源對初版的陳述；本機產品 release 清冊為 unknown，且沒有後續 CFX/PyCFX 完整相容矩陣，因此不據此推定其他版本或 container 支援。

來源：[Launching CFX](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/guide/3b3f3b82028d-launching_cfx.md)（[來源清冊](sources.csv#ansys_a4a0afff47aac7962b2138aa)）、[session guide 的 Solver／PostProcessing 章節](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/guide/905297a05e5e-session.md)（[來源清冊](sources.csv#ansys_c58523f59daaf38e134d31d7)）。

## PyCFX 0.3.0 安裝前提與本機版本定位

PyCFX 安裝指南標示支援 Windows／Linux 的 Python 3.10–3.14；使用者安裝命令為 `pip install ansys-cfx-core`。使用 PyCFX 必須另有授權的 Ansys CFX 安裝；指南明列支援 CFX 2025 R2 Service Pack 3 及更新版本。文件網站使用 `version/stable`，來源清冊的產品 release 仍為 `unknown`，因此此支援下限不表示本機已確認特定版本組合。

PyCFX 依 `AWP_ROOT<version>` 環境變數定位 Ansys 安裝。Windows 安裝程式會設定對應變數；Linux 使用者需自行設定。指南以 `AWP_ROOT252=/usr/ansys_inc/v252` 為例，供目前 shell 使用可執行 `export AWP_ROOT252=/usr/ansys_inc/v252`，要跨 shell 保留則加入使用者的 `~/.profile`。透過 `from_install()` 啟動時，明確傳入 `product_version` 會選用該版；省略時才選最新的受支援安裝版本。

**本機啟動邊界：**launch guide 說明 PyCFX 初版搭配 CFX 2025 R2 SP3 時，只支援在執行 Python 的同一部電腦啟動 CFX session。這是初版配對條件，不外推至後續 PyCFX／CFX release，也不構成遠端、容器或叢集啟動支援的確認。

**開發者安裝與一般使用者安裝不同：**若要從原始碼開發，指南列出 `pip install -e .[doc,tests,style]`；產生 API 類別需執行 `python codegen/allapigen.py`，且該步驟需要 Ansys CFX 安裝。上述 extras 與 code generation 是貢獻開發流程，不是一般使用者安裝命令。

來源：[PyCFX Installation](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/guide/9a36ac675d53-installation.md)（[來源清冊](sources.csv#ansys_cdad416d6d922df3911d2bd8)）、[Launch CFX](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/guide/3b3f3b82028d-launching_cfx.md)（[來源清冊](sources.csv#ansys_a4a0afff47aac7962b2138aa)）。兩頁皆使用官方 `version/stable` URL，SDK 文件集合 metadata 為 0.3.0；本機未驗證 CFX 安裝、license、Python 相容性或 session 啟動。

## 官方範例的適用範圍

PyCFX Static Mixer 範例示範以 PreProcessing 建案、執行 CFX-Solver，再在 CFD-Post 做基本後處理。其模型描述為兩個入口向靜態混合器供水，範例入口速度均為 2 m/s、溫度分別為 315 K 與 285 K。這些是該教學案例的輸入值，不是其他混合器案例可直接沿用的設計條件。

## Static Mixer 教學：以檔案交接三種 session

官方 Static Mixer 範例採 file-based workflow：`PreProcessing` 建立 case、匯入 `StaticMixerMesh.gtm`、設定 domain 與 boundary conditions，呼叫 `get_physics_messages(severity="All")` 檢查設定訊息，再寫出 `static_mixer.def` 並關閉 preprocessing session；之後獨立建立 `Solver` session 執行並等待求解，取得 results file 名稱後關閉 solver；最後以該結果檔建立 `PostProcessing` session。文件說明三個元件可在不同時間、Python session 或機器設定下分開執行，但此範例明確只支援 local CFX-Solver 執行。

案例用兩個入口與一個出口：入口 normal speed 都是 `2 m/s`，static temperature 分別為 `315 K`、`285 K`；材料為 Water，模型採 thermal energy 與 k-epsilon，solver control 使用 upwind，physical timescale 為 `2 s`。這些是教學設定，不是一般靜態混合器的物理模型或收斂建議。

後處理部分載入結果後，以 CFD-Post 建立 Pressure contour、輸出 PNG；建立切片 plane 時先 `suspend()`，完成 ZX slice 設定後 `unsuspend()`，減少逐項修改時的中間重算。範例亦建立 CEL expression `maxVal(Temperature)@out - minVal(Temperature)@out` 並呼叫 `evaluate()`。這些步驟示範 API 操作，不構成收斂、網格獨立性或物理正確性驗證。

來源：[Simulate flow in a static mixer](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/tutorial/fbaea448ebb2-01-introductory-example-static-mixer.md)（[來源清冊](sources.csv#ansys_c1a309e2c8bf661cd1367ed9)；SDK metadata `ansys-cfx-core 0.3.0`，來源為 official `version/stable`，產品 release `unknown`）。


## Fourier Transformation Blade Flutter 教學：初始條件、time integration 與 harmonic balance

官方 PyCFX 範例以單通道軸流壓縮機轉子（完整轉子 36 blades）示範 transient blade flutter。匯入的網格只有一個 passage；範例用 CFX Command Language（CCL）將 mesh transformation 設為兩個 passages，因該 Fourier Transformation 案例需要 two-passage model，且文件說明目前 mesh transformation 須經 CCL 設定。此網格配置屬該範例，不是一般 blade-row 建模規則。

流程依序建立不含 transient blade row method 的初始 solver case 並產生初始條件；接著修改同一 preprocessing setup，以 Fourier Transformation 建立 time-integration case、求解並保存結果；最後沿用該初始條件建立 harmonic-balance case、求解，再對兩組結果後處理。範例指出部分 setup 與後處理可在前一 solver run 尚未結束時先準備；若 CFD-Post 載入尚在計算的結果，PostProcessing session 會等 solver 完成後再讀取。

後處理以 `Total Wall Work = Wall Work Density * Area` 建立 expression，於 R1 Blade 建立 contour，並在支援的版本輸出 animation。教學以 `CFXVersion > v252` 分支使用不同 Aerodynamic Damping monitor object path；頁面另明示 PyCFX 2025 R2 不支援 animation。這些條件只記錄教學中的版本分支，使用者應核對實際安裝版本與 API；案例設定、結果圖及動畫不構成數值收斂或物理驗證。

來源：[Set up a Fourier Transformation Blade Flutter case](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/tutorial/ccb852478997-02-fourier-transformation-blade-flutter.md)（[來源清冊](sources.csv#ansys_df8190712c5398b467b1edc7)；PyCFX SDK metadata 0.3.0，官方 URL 使用 `version/stable`，CFX product release 維持 unknown）。


## v251／v261 收斂判讀：Residual、Global Balance 與目標量

CFX 將 residual 定義為控制體保守方程的局部不平衡，並使用 normalized residual 判斷數值收斂。可選 RMS 或 MAX residual 與 target；手冊提醒湍流輸運方程的 residual 不納入 solver 自動停止的收斂判定，多相 volume-fraction 方程使用的判據則比指定 target 高 10 倍。Transient 計算的 residual 包含時間項，target 控制每一 timestep 的 coefficient iterations，不能把它與時間步獨立性視為同一件事。

| v261 手冊所列 RMS 指引 | 使用界線 |
|---|---|
| 預設 target 為 `1e-4`；手冊稱此為 relatively loose。 | 只是手冊指引，不是所有工程案例的驗收門檻。 |
| `1e-5` 稱為 good convergence；`1e-6` 或更低稱為 very tight。 | 是否需要、是否能達成依模型與目標量而異；手冊明說 single precision 可能無法達成很緊的 target。 |
| MAX 通常約為 RMS 的 10 倍，但也可能高很多。 | 高 MAX 可能集中於局部非定常區；須核對關鍵力、效率或其他目標量的變化。 |

Residual 達 target 後，仍需檢查 global balances 與關鍵 derived quantities。具有很慢物理過程的問題，可能在 global balance 滿足前已達 residual target。每次 run 也應辨別停止原因是達成 convergence criteria，還是只達 Maximum Number of Iterations；定量結果須檢查目標量對 target 的敏感度。

來源：Modeling Guide v261 [PDF Page 585](../ANSYS_Document/_catalog/pdf_text_v4/201853abbcd18a000f3146515b2a8b5e89c9445d1e5d2f0dfe4ef8028604905f.md#pdf-page-585)、[586](../ANSYS_Document/_catalog/pdf_text_v4/201853abbcd18a000f3146515b2a8b5e89c9445d1e5d2f0dfe4ef8028604905f.md#pdf-page-586)、[588](../ANSYS_Document/_catalog/pdf_text_v4/201853abbcd18a000f3146515b2a8b5e89c9445d1e5d2f0dfe4ef8028604905f.md#pdf-page-588)（`ansys_45ccf069fc36c5b2c371a978`）。本輪在 v251 相同實頁核對上述關鍵規則（`ansys_7e4f7e457c8aac71e60ef45d`），未發現這些段落的規則差異；未比對整本手冊。

## v261 Timescale：穩態鬆弛、Auto 與暫態時間

穩態求解可透過 timescale 對非線性方程提供鬆弛；暫態的 timestep／time duration 則追蹤模擬的真實時間。`Physical Timescale` 讓選定方程在流域使用固定 timescale；不能只因名稱含 physical 就把穩態迭代數轉成經過的物理時間。

`Auto Timescale` 是預設 timescale control，手冊稱其估計常較保守。`Timescale Factor` 乘上內部估計，`Maximum Timescale` 則以上限約束內部計算。對 advection-dominated flow，手冊以長度／速度尺度作為估計依據；尺度過大可能呈現跳動或不收斂，過小可能只緩慢、穩定地收斂。這不是所有旋轉、浮力或多物理問題的通用時間步公式。

Timescale 可在 global、domain、phase、equation class 或單一 equation 層級設定；較特定的 equation／phase／domain 設定優先於較廣的設定。手冊的 13 項優先序中，CFX-Pre UI 只支援第 8、12、13 類，其餘需編輯 CCL；對 energy equation 另設 timescale 可能使 global Solid Timescale Factor 不再生效。完整優先序應回原表查閱，不能只看 UI 顯示的一個值。

來源：Modeling Guide v261 [PDF Pages 570–574，自 570 起](../ANSYS_Document/_catalog/pdf_text_v4/201853abbcd18a000f3146515b2a8b5e89c9445d1e5d2f0dfe4ef8028604905f.md#pdf-page-570)（`ansys_45ccf069fc36c5b2c371a978`）；v251 同頁關鍵文字亦核對。此處未替任何模型選定 timestep 或 timescale。

## v261 Frame Change／Mixing Model 的選擇界線

General Connection 的 frame-change／mixing 選項包括 Frozen Rotor、Stage（Mixing-Plane）、Transient Rotor-Stator；原文要求介面兩側都是 surface of revolution，且掃過相同的旋轉曲面。三者對相對位置與時間效應的假設不同。

| 模型 | 文件描述 | 主要限制 |
|---|---|---|
| Frozen Rotor | 兩側相對方位固定；求解 frame／pitch change 的穩態近似，三種模型中計算成本最低。 | 不模擬介面 transient interaction，也不重現真實相對運動混合損失；相對方位可能影響解。 |
| Stage／Mixing-Plane | 對介面 band 的 flux 作周向平均，在各參考系取得穩態解，包含平均化混合損失。 | 忽略 transient interaction；周向非均勻性相對 component pitch 很大時不適用，例如手冊所舉 off-design pump／volute。 |
| Transient Rotor-Stator | 隨 timestep 更新介面相對位置，求解旋轉元件之間的 transient interaction。 | 時間、儲存與後處理成本較高；pitch 不等的 passage 配置需另處理。該 sliding interface 不支援 translational relative motion。 |

若關注啟動過程，須以對應物理初始條件開始；若關注週期性運轉，手冊說可以 Frozen Rotor 穩態解作初始猜測。這是初始化策略，不證明該穩態解或後續暫態已符合工程驗收。

來源：Modeling Guide v261 [PDF Pages 239–242，自 239 起](../ANSYS_Document/_catalog/pdf_text_v4/201853abbcd18a000f3146515b2a8b5e89c9445d1e5d2f0dfe4ef8028604905f.md#pdf-page-239)（`ansys_45ccf069fc36c5b2c371a978`）；v251 同頁關鍵規則亦核對。介面圖與 pitch-change 幾何未作目視或模型驗證。

## v261 Automatic Wall Treatment 與 Yplus 判讀

Wall-function 方法以近壁經驗關係節省解析邊界層的成本；Low-Reynolds-Number 方法則以壁面法向的細網格解析黏性影響區。此處的 low Reynolds number 指近壁 turbulent Reynolds number，不能由整個裝置的 Reynolds number 高低直接判斷是否適用。

Omega-based 模型的 automatic near-wall treatment 可隨網格細化，在 wall-function 與 low-Re near-wall formulation 間平滑切換。v261 手冊建議，要利用細網格帶來的改善，應嘗試以至少 10 個 nodes 解析邊界層；這是手冊對該用途的指引，未取代網格獨立性、近壁傳熱、轉捩或粗糙壁需求的檢查。

CFX 結果同時提供 `Yplus` 與 `Solver Yplus`。前者依壁面至第一個 node 的距離及 wall shear stress 計算，是手冊建議用來判斷近壁網格間距的量；後者為 solver 內部定義及向後相容用途。粗糙壁還需區分 equivalent sand-grain roughness 與實際 geometric roughness，兩者不能直接等同。字典不設定統一的 y+ 合格值。

來源：Modeling Guide v261 [PDF Page 227](../ANSYS_Document/_catalog/pdf_text_v4/201853abbcd18a000f3146515b2a8b5e89c9445d1e5d2f0dfe4ef8028604905f.md#pdf-page-227)、[230–231，自 230 起](../ANSYS_Document/_catalog/pdf_text_v4/201853abbcd18a000f3146515b2a8b5e89c9445d1e5d2f0dfe4ef8028604905f.md#pdf-page-230)（`ansys_45ccf069fc36c5b2c371a978`）；v251 同頁關鍵規則亦核對。未抽查所有 wall-treatment 方程、圖表或網格。

## v251／v261 材料屬性壓力與 CEL `p` 的原文矛盾

Material Properties 章節有一項不能直接當成確定 API 規則的矛盾：兩版實頁 89 的 CEL Expressions 說，材料屬性 expression 中的 `p` 解讀為 **absolute pressure**，reference pressure 則使用 `Pref`；兩版實頁 94 在 Table Generation Pressure and Temperature Limits 又說，density／specific heat expression 裡的 CEL `p` 仍使用 **relative pressure**。本輪從兩版 PDF 直接抽取均找到這兩種說法，不是只有 sidecar 出現。

實頁 94 對 property-table minimum／maximum pressure limits 的說法則明確：這些 limits 以 absolute values 輸入，不相對於 reference pressure；範圍過窄會使 property 值在界限被 clipping。這一條可整理為文件規則，但不能用它消解 `p` 解讀的矛盾。

因此本字典保留此差異，未給出材料 expression 應將 `p` 當哪一類壓力的確定結論。使用前須依目標 CFX 版本的有效官方說明或受控驗證釐清；不應僅因 expression 被接受就視為單位及壓力基準正確。

來源：Modeling Guide v261 [PDF Page 89](../ANSYS_Document/_catalog/pdf_text_v4/201853abbcd18a000f3146515b2a8b5e89c9445d1e5d2f0dfe4ef8028604905f.md#pdf-page-89)、[94](../ANSYS_Document/_catalog/pdf_text_v4/201853abbcd18a000f3146515b2a8b5e89c9445d1e5d2f0dfe4ef8028604905f.md#pdf-page-94)（`ansys_45ccf069fc36c5b2c371a978`）；v251 [PDF Page 89](../ANSYS_Document/_catalog/pdf_text_v4/534a01885159ecacdf7ecd8ba0ac4fd17aadf5889dee8949c27f0fc10729f834.md#pdf-page-89)、[94](../ANSYS_Document/_catalog/pdf_text_v4/534a01885159ecacdf7ecd8ba0ac4fd17aadf5889dee8949c27f0fc10729f834.md#pdf-page-94)（`ansys_7e4f7e457c8aac71e60ef45d`）。

## v261 Initial Values File 與 Continue History

CFX 可從一個或多個既有 results files 讀取初始值；這屬於 Run Definition，而非 physics setup。本輪核讀的規則包括：

- 新模型某個變數不在 initial-values file 時，solver 回到 CFX-Pre 的 Initialization 設定取得該變數，而不是推定所有新變數都能從舊結果補出。
- `Continue History From` 開啟用於較平滑地延續既有 run；關閉則偏向只取初始猜測。若有多個 initial-values files，history 只能選一個來源延續。
- 除特定 Use Mesh From 設定外，run 開始會使用 CFX-Interpolator；應檢查 Output 中的 `Interpolation of Initial Values` 診斷。手冊建議初始條件重要或診斷不符預期時，檢視第一個 timestep／outer iteration 前輸出的 backup／transient file。

從不可壓結果初始化可壓案例時，手冊特別提醒檢查 reference pressure 與壓力合理性；不可壓模型允許的壓力差狀態，不代表可壓模型的 absolute pressure 也物理合理。此處不轉寫實頁 176 跨欄表格內所有 copy／interpolate 條件，以免遺漏 mesh、particle 或變數類型限制。

來源：Modeling Guide v261 [PDF Pages 174–176，自 174 起](../ANSYS_Document/_catalog/pdf_text_v4/201853abbcd18a000f3146515b2a8b5e89c9445d1e5d2f0dfe4ef8028604905f.md#pdf-page-174)（`ansys_45ccf069fc36c5b2c371a978`）；v251 同頁關鍵規則亦核對。未執行 restart、interpolation 或 transient run。

## v261 Thermal Energy 與 Total Energy 的適用界線

Theory Guide 說明，CFX 求解守恆形式的非定常 Navier–Stokes 方程；熱能方程（Thermal Energy）是總能量方程（Total Energy）的簡化形式。低速流可採熱能形式，但若需要正確聲學行為，例如聲速，或是高速流，原文要求使用 Total Energy。液體比熱若隨狀態改變，例如 CEL expression、RGP table 或 Redlich Kwong equation of state，熱能方程所用變數與焓表的處理可能不一致，手冊因此提醒此情況不應使用 Thermal Energy，尤其是 subcooled liquids。

對同時採 Multiple Frames of Reference（MFR）與 Total Energy 的案例，原文明載須選 `Incl. Viscous Work Term`，否則與 MFR interface implementation 不一致，CFX-Pre／Solver 會發出警告。這是 v261 文件條件，不能用一般「黏性功通常可忽略」的敘述代替此設定檢查。

來源：[Theory v261 p.42](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-42)、[p.43–44，自 43 起](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-43)（`ansys_b93d1952273bccaf13eb745a`）。未替個案選定能量模型。

## v261 Element-based Finite Volume 與 Coupled Solver

CFX 採 element-based finite volume method。解變數與流體屬性存於 mesh vertices，並以各節點周圍的 median-dual control volume 寫出守恆式；積分點兩側控制體使用大小相等、方向相反的表面通量，構成局部守恆。有限元素 shape functions 用於積分點插值，不表示 CFX 的流體方程改成一般結構有限元素求解。

Hydrodynamic equations 的 `u, v, w, p` 以同一個 coupled system 求解。每次外層迭代先線性化、組裝係數，再解線性方程；穩態以 physical timescale 控制外層推進，每個外層只有一次內層線性化迭代，暫態每個 timestep 可有多次內層迭代。線性解法使用 Multigrid 加速的 Incomplete Lower Upper（ILU）factorization，Algebraic Multigrid（AMG）由細網格方程建立虛擬粗化方程，不要求使用者另建一套幾何粗網格。這些是解法描述，不構成特定模型的速度或記憶體保證。

來源：[Theory v261 p.373–376，自 373 起](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-373)、[p.387–390，自 387 起](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-387)（`ansys_b93d1952273bccaf13eb745a`）。

## v261 Advection 與 Transient 離散精度

| 離散選項 | 原文的精度／界線 |
|---|---|
| 1st Order Upwind | 穩健，但數值擴散會抹平陡峭空間梯度。 |
| Specified Blend Factor | blend factor 為 1 時形式上為空間二階；不具 boundedness，急變區可能產生非物理振盪。 |
| High Resolution | 各 node 採非線性 blend，盡量接近高階而不產生新的極值；原文只對一維情況說明 TVD 性質。 |
| Bounded Central Difference（BCD） | 儘量採 central difference，違反 convection boundedness criterion 時混入一階 upwind；原文列為 LES／SAS／DES 可用選項。 |
| First Order Backward Euler | 時間一階、implicit、bounded、時間守恆；會擴散陡峭時間梯度。 |
| Second Order Backward Euler | 時間二階、implicit、時間守恆，但可能出現非物理振盪；volume fraction 等需 boundedness 的量另採修改形式。 |

手冊稱兩種 Backward Euler 沒有由該離散式施加的 timestep size limitation；這不免除時間解析度與時間步獨立性檢查。二階暫態預設在第一步使用一階離散，因取值時間位置不同而有啟動守恆誤差；原文提出 `transient startup option` 可部分修正，減小 timestep 也可減輕誤差。本頁不直接給工程 timestep 數值。

來源：[Theory v261 p.380–382，自 380 起](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-380)、[p.385](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-385)（`ansys_b93d1952273bccaf13eb745a`）。

## v261 Normalized Residual 與 Discretization Error

Raw residual 是線性化離散方程的 control-volume imbalance。Normalized residual 還依代表性係數與變數尺度正規化；Theory Guide 明說其完整尺度計算沒有在該節展開。穩態 timescale 只用於鬆弛，因此排除於 residual normalization；暫態的 transient term 則包含在係數內。這個差異可解釋為何不能直接比較不同分析型態的 residual 數值來宣稱相同誤差。

Fully converged discrete solution 與所建模微分方程精確解之間，仍可能有 discretization error。手冊將控制方式分為減少誤差來源與抑制誤差放大：提高離散階次、在解變化快速處細化網格可減少某些誤差來源；幾何品質差、強烈各向異性或摺疊元素仍會引入其他誤差。邊界層的方向性細化須同時維持適當 orthogonality 與 expansion；本節未給統一網格品質合格值。

來源：[Theory v261 p.390–392，自 390 起](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-390)（`ansys_b93d1952273bccaf13eb745a`）；實際收斂判讀另見本頁 Residual／Global Balance 主題。

## v261 GGI 的守恆介面與 RSM 近似

General Grid Interface（GGI）以 control surfaces 連接不同拓樸或分布的兩側網格，並由交集建立共同介面；面積延伸不同時會依重疊部分做 trimming。MFR 使用此技術處理相對旋轉的 domains。原文描述介面通量採 fully implicit，並在計入 pitch change 後維持各方程通量守恆。這描述介面離散的守恆性，不表示任意幾何重疊、pitch 或 frame-change 模型選擇都適當。

一個容易忽略的模型界線是：使用 Reynolds Stress turbulence model 時，GGI 介面沿線 control volumes 的 Reynolds-stress 動量貢獻仍以 eddy-viscosity approach 近似。Stage（Mixing-Plane）的 control-surface balance 與其他介面也有不同空間平均方式；不能只由「GGI」名稱推定其保留全部周向非均勻性。

來源：[Theory v261 p.169–171，自 169 起](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-169)（`ansys_b93d1952273bccaf13eb745a`）。

## v261 Homogeneous／Inhomogeneous Multiphase

Inhomogeneous Eulerian–Eulerian 模型為各 phase 保有自己的 solution field，再經 interphase drag、heat／mass transfer 等項互動。Homogeneous 模型對選定的 transport process 假設各 phase 共用被傳輸量（volume fraction 例外），改解 bulk transport equation；這個假設不必套用到所有方程。例如速度可為 inhomogeneous 而 turbulence 為 homogeneous，或共享速度但各 phase 保有不同溫度。

Modeling Guide 提醒：重力下已分層的 free surface，或無 body force 且 phase velocities 很快平衡的強 drag 情況，可適合 homogeneous 速度假設；重力下落的 droplets 即使 drag 很大仍可能形成固定 slip velocity，只有 slip 相對 mean flow 很小時才可採此近似。Inhomogeneous 下的 Particle／Mixture／Free Surface 子模型又各自決定 interfacial area density；此處的 Particle 子模型與下一節 Lagrangian tracking 不是同一個建模方式。

來源：[Modeling v261 p.306–307，自 306 起](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-306)（`ansys_45ccf069fc36c5b2c371a978`）、[Theory v261 p.184](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-184)、[p.187](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-187)（`ansys_b93d1952273bccaf13eb745a`）。

## v261 Lagrangian Particle Transport 與單向／雙向耦合

Particle Transport 以一組代表粒子追蹤整體 particulate phase，對各粒子的位置、速度、溫度與 species masses 建立時間常微分方程，再沿流域積分。它可描述 solid particles、drops 或 bubbles；不能因名稱有 particle 就將所有固體離散元接觸或高濃度效應視為已納入。

One-way coupling 由流場影響粒子，但粒子不回饋流場；原文將低 dispersed-phase loading、粒子對流場影響可忽略列為可能適用情況，沒有給通用濃度門檻。Two-way coupling 則在流體方程加入粒子追蹤所產生的 source terms。流體變數在粒子位置由所處 element 的 shape functions 從 vertices 插值；粒子樣本數、追蹤限制與來源項收斂仍須另行核對。

來源：[Theory v261 p.251–252，自 251 起](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-251)（`ansys_b93d1952273bccaf13eb745a`）。

## v261 Eddy Viscosity 與 Reynolds Stress Closure

Reynolds averaging 產生 Reynolds stresses 與 turbulent scalar fluxes，需要 closure。Eddy-viscosity 類模型以 mean velocity gradients 與 turbulent viscosity 建模 Reynolds stresses；scalar flux 則常以 eddy diffusivity／turbulent Prandtl number 關聯。不同 eddy-viscosity 模型的差別包括 turbulent viscosity／diffusivity 的取得方式。

Reynolds Stress Model（RSM）不採相同的 eddy-viscosity hypothesis，而為 stress components 建立方程；原文另區分 algebraic 與 differential Reynolds stress models。這個分類是模型假設的差異，不構成 RSM 對所有流況一定較準確的保證；GGI 邊界處仍有前述局部 eddy-viscosity approximation。近壁處理與網格條件另見本頁 Automatic Wall Treatment 主題。

來源：[Theory v261 p.103–106，自 103 起](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-103)、[p.119](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-119)（`ansys_b93d1952273bccaf13eb745a`）。

## v261 EDM／Finite Rate Chemistry 與 Combined Rate

| CFX 燃燒模型 | 原文定義與注意事項 |
|---|---|
| Eddy Dissipation Model（EDM） | 假設化學反應比流場傳輸快，反應受分子混合時間控制；湍流混合尺度由 turbulence properties 決定。Products limiter 預設關閉（係數 B 為 -1）；原文不建議對 multi-step scheme 開啟它。 |
| Finite Rate Chemistry | Elementary reaction 只有定義 backward reaction 時才可逆；內建 rate-constant 形式採 Arrhenius temperature dependence，也可直接指定。Global reaction 的 reaction order 不一定等於 stoichiometric coefficient。 |
| Combined EDM／Finite Rate | Effective rate 取 Finite Chemistry Rate 與 Eddy Dissipation rate 兩者的較小值。 |

以上是 CFX 實作定義，不能直接推論某個化學機制、點火或熄火案例的準確性。Combustion source linearization 用來避免 mass fractions 超出物理界線，但 solver 接受反應設定也不代表機制、單位或邊界條件已驗證。

來源：[Theory v261 p.313–315，自 313 起](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-313)（`ansys_b93d1952273bccaf13eb745a`）。

## v261 Radiation 模型、Optical Thickness 與 Domain 限制

| 模型 | v261 手冊所述適用界線 |
|---|---|
| Rosseland | Optically thick 近似；手冊稱通常適用 optical thickness 大於 5，低於 1 不應使用。壁面有特殊處理，其他 boundary 沒有同樣處理。 |
| P1 | 增加一個 transport equation；原文適用 optical thickness 大於 1，較低值的成功情況不作保證。CFX 實作只允許 opaque diffuse walls。 |
| Discrete Transfer | 固定 ray sampling；thin limit／purely transparent 問題可用，但須考量 angular resolution、ray effects 與缺少直接誤差資訊。 |
| Monte Carlo | 以 photon histories 抽樣；histories 數影響統計估計，不能只以預設 10,000 次宣稱輻射結果精度。 |

CFX 的 fluid／porous domains 可選這些 radiation models；solid domain 只提供 Monte Carlo。光學模型之外還需指定 spectral model、scattering model 與相關材料屬性；absorption coefficient、scattering coefficient、refractive index 可依狀態或頻譜變動。上述 optical-thickness 數值是該手冊對模型近似的條件，不是所有熱傳分析的統一驗收值。

來源：[Modeling v261 p.472–475，自 472 起](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-472)、[p.478](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-478)（`ansys_45ccf069fc36c5b2c371a978`）。

## v261 Inlet／Outlet／Opening 與 Well-posed Boundary Conditions

Inlet／Outlet 主要用於預期單向流的區域；Opening 可在同一邊界同時流入與流出，但只適用 subsonic boundary。需留意 velocity-specified inlet／outlet 仍允許速度條件所指定的反向流；而 pressure inlet 發生不允許的流出時，solver 可能建立 artificial wall。這些行為不能只由 UI 的邊界名稱判斷。

Modeling Guide 的常見配置表把 inlet velocity／mass flow 加 outlet static pressure 列為最穩健的組合；inlet total pressure 加 outlet static pressure 的 mass flow 由解決定，對 initial guess 敏感；inlet static pressure 加 outlet static pressure 約束弱，原文不建議。Total pressure 不能指定於 outlet。這些是該節的配置指引，使用前仍須依可壓縮性、流向、開口及實體實驗條件檢查 well-posedness，不代表所有模型都應改成同一套邊界。

來源：[Modeling v261 p.112–114，自 112 起](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-112)、[p.137](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-137)（`ansys_45ccf069fc36c5b2c371a978`）。

## v261 User CEL Function 的 Fortran 呼叫契約

本機原有 `CFX_USER_CEL_FUNCTION_API_DICTIONARY.md` 是人工彙整的來源 Markdown，並非官方 API 全目錄。核對 `_catalog/documents.json` 後確認：它只有 `path`、`sha256`、`quality` 等來源欄位，沒有 `text_path`；舊 CFX 逐筆稽核表亦明列 `conversion_status=catalog_only`。因此「沒有 `text_path`」代表舊 catalog schema 沒有把這份 Markdown 登記為轉換正文，不代表檔案不存在或內容不可讀。來源 Markdown 有 2,334 個 UTF-8 bytes，並可與 v261 Modeling Guide 原頁核對；既有 SQLite 以 `ansys_8e6e0112326d3b1865fc9933` 索引此 Markdown，`NLOC` 與 `cfx5ext` 均可搜尋並擷取片段。下文另整理其內容供字典閱讀。

v261 Modeling Guide 的 User CEL Function 是 Solver 呼叫的 Fortran routine 介面，與 PyCFX Python API 不同。基本 routine 以 `#include "cfx5ext.h"` 開頭，接著用小寫名稱的 `dllexport(<callingname>)` 匯出每個 Solver 可呼叫的 routine，再宣告固定參數列 `NLOC, NRET, NARG, RET, ARGS, CRESLT, CZ, DZ, IZ, LZ, RZ`。`dllexport` 必須先於對應 routine，且從 Fortran 第 1 欄開始；`cfx5ext.h` 必須是 Fortran 檔第一行。每個 routine 都需要自己的 export macro。

| 欄位 | 手冊定義／使用界線 |
|---|---|
| `NLOC` | 此次呼叫要計算的空間位置數；由呼叫 locale 決定，例如 boundary element group 的面數，或目前 zone 的 vertex 數。 |
| `NARG`、`ARGS(1:NLOC,1:NARG)` | CEL argument list 傳入的參數數量，以及每一位置對應的引數值。 |
| `NRET`、`RET(1:NLOC,1:NRET)` | 回傳變數數量及各位置結果；CFX 目前固定 `NRET=1`。 |
| `CZ/DZ/IZ/LZ/RZ` | 分別為 character、double precision、integer、logical、real stacks；當 CEL 右側引數不足以計算結果時，透過 MMS/utility routines 取得額外資料。 |

Solver 會把指定區域切成多個 piece，且 routine 一個 iteration 內可能被呼叫多次，每次 `NLOC` 也可能不同。因此 routine 必須支援變動陣列長度與重複呼叫，不能假設一次覆蓋整個區域。手冊另說 User Fortran 字串大小寫有別；引數進入 routine 前會轉成 CFX-Pre User Function Argument List 指定的單位，結果離開 routine 時會由 Result Units 轉回 solution units。這是文件所述的單位轉換行為，尚未以本機工具鏈實測。

User CEL Function 和 junction box routine 不可混為一談：junction box 只接收 Solver workspace stacks，沒有 user arguments，且不可直接使用 CEL variables；它在 CFX-Pre 中另外配置呼叫時點。`<CFXROOT>/examples/ucf_template.F` 是手冊列出的模板位置，不是已核實的本機檔案。編譯器、平台 ABI、MMS stack 操作及 runtime 載入均未在本次執行驗證。

來源：[本機 CFX User CEL Fortran 入口字典](../ANSYS_Document/CFX/v261/api_reference/CFX_USER_CEL_FUNCTION_API_DICTIONARY.md)（`ansys_8e6e0112326d3b1865fc9933`，SHA-256 `9046f59ec18cfcf83b77b7d3a5d0ed1f757f0ad8a0641f55098f28fc4c71186c`）；[Modeling Guide v261 PDF Page 645–647](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-645)（`ansys_45ccf069fc36c5b2c371a978`）。

## PyCFX tutorial 附件：可讀正文與索引邊界

四個附件不是二進位或掃描檔（本機確認文字補件已索引；原始 attachment catalog 列仍沒有 `text_path`）：兩個 `.py` 是 UTF-8、Python 語法可解析的原始範例；兩個 `.ipynb` 是 nbformat 4 JSON，內含交錯的 Markdown 說明和 code cells。舊 catalog 將四者列為 `quality=attachment`、`conversion_status=catalog_only`，且沒有 `text_path`，原因是它們是 tutorial 的輸入附件，不是 HTML 轉換頁；實際附件完整存在，source hash 與 catalog hash 相符。故其內容可直接讀取；原始附件本身未直接作為可搜尋 body。四份 `.py`／Notebook 的 Markdown 與 code cells 已製成獨立文字補件並收錄於現有 SQLite `cfx`／`tutorial` 類別；補件不包含 Notebook output、圖片或其額外附件，原始相對連結需回原附件核對。

文字補件清冊：[CFX 附件文字補件](../maintenance/knowledge_dictionary_passes/2026-11-03/cfx_attachment_text_recovery.csv)。補件與原附件均未執行；片段不可視為已驗證的運行結果。

Notebook 包含圖像引用及分節文字，`.py` 包含可執行程式與 reStructuredText 說明註解；兩種形式可互補閱讀，不能只把它們視為互相可替代的純程式碼副本。Python 腳本均通過 AST 語法解析。本輪沒有執行程式或下載外部 mesh/profile，避免啟動 CFX/PyCFX 或改動環境。

### Static Mixer 範例附件

`.py` 有 13,198 字元，Notebook 有 50 cells（23 code cells）；摘要與既有 tutorial HTML→Markdown 頁相互印證。程式步驟為下載 `StaticMixerMesh.gtm`、建立 `PreProcessing` session、新 case、匯入網格，設定 Water、reference pressure `1 [atm]`、Thermal Energy、k-epsilon；兩入口 Normal Speed 均為 `2 [m s^-1]`，溫度分別 `315 K`、`285 K`，出口設 Average Static Pressure `0 [Pa]`。接著以 Upwind、Physical Timescale `2 [s]`、最多兩個 local MPI processes 寫出 `.def`，檢查 physics messages，再用 Solver 執行及 CFD-Post 載入結果。這些數值是範例輸入，不是一般設計或收斂建議。README式敘述及圖片說明可在 Notebook Markdown cells 查閱；原始碼同時保留，未複製進字典。

來源：[Static Mixer `.py`](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/tutorial/inputs/01-introductory-example-static-mixer.py)（`ansys_36e9fd4b356b7ada726a6b3b`）、[Notebook](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/tutorial/inputs/01-introductory-example-static-mixer.ipynb)（`ansys_29b9246a3c0df8d5a51e6ed4`）、[轉換後 tutorial 正文](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/tutorial/fbaea448ebb2-01-introductory-example-static-mixer.md)（`ansys_c1a309e2c8bf661cd1367ed9`）。

### Fourier Transformation Blade Flutter 範例附件

`.py` 有 36,567 字元，Notebook 有 108 cells（52 code cells）。範例說明全轉子 36 blades，但 mesh 是單 passage；它按 tutorial 用 CCL 設定 mesh transformation 為 two passages，不能推成一般 blade-row 規則。流程先執行不含 transient blade-row method 的初始案例產生 initial conditions，再各自建立 Fourier Transformation time-integration 與 harmonic-balance 設定；後者設定 3 modes，兩者皆使用初始結果作為 initial values。程式還下載網格、mode profile、inlet profile，並建立 aerodynamic damping monitors 及 CFD-Post 後處理。程式依 `CFXVersion > v252` 切換特定 monitor object path；動畫分支也受版本支援限制。此為範例碼版本分支；使用前須核對目標安裝/API，不等於已對本機 CFX 版本驗證。

來源：[Blade Flutter `.py`](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/tutorial/inputs/02-fourier-transformation-blade-flutter.py)（`ansys_dd07975d5d55b554745ba750`）、[Notebook](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/tutorial/inputs/02-fourier-transformation-blade-flutter.ipynb)（`ansys_e2dde7fc61b9263804db888e`）、[轉換後 tutorial 正文](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/tutorial/ccb852478997-02-fourier-transformation-blade-flutter.md)（`ansys_df8190712c5398b467b1edc7`）。

## 手冊章節導覽與轉換可追溯性

下表覆蓋兩本手冊的全部頂層技術章節；頁碼為 PDF 實頁，不是抽出文字的行號。兩版頂層章節起始頁相同；子節仍可能移動。列出章節入口表示來源已保存且可定位，不表示整章已轉成繁中知識條目。

| Modeling Guide 章節 | v251／v261 起始實頁 |
|---|---|
| 1 Basic Capabilities | [39](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-39) |
| 2 Boundary Conditions | [111](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-111) |
| 3 Initial Conditions | [161](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-161) |
| 4 Turbulence／Near-wall | [197](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-197) |
| 5 Domain Interfaces | [235](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-235) |
| 6 Turbomachinery Blade Rows | [259](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-259) |
| 7 Multiphase Flow | [299](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-299) |
| 8 Particle Transport | [359](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-359) |
| 9 Combustion | [431](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-431) |
| 10 Radiation | [471](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-471) |
| 11 Rigid Body | [491](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-491) |
| 12 Real Fluid Properties | [497](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-497) |
| 13 Operating Maps | [529](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-529) |
| 14 External Solver Coupling | [535](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-535) |
| 15 Aerodynamic Noise | [551](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-551) |
| 16 Flow Modeling Advice | [563](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-563) |
| 17 Parallel Solver | [597](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-597) |
| 18 Expert Parameters | [613](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-613) |
| 19 User Fortran | [643](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.md#pdf-page-643) |

| Theory Guide 章節 | v251／v261 起始實頁 |
|---|---|
| 1 Basic Solver Capability | [21](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-21) |
| 2 Turbulence／Wall Functions | [101](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-101) |
| 3 GGI／MFR | [169](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-169) |
| 4 Transient Blade Rows | [173](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-173) |
| 5 Multiphase Flow | [183](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-183) |
| 6 Particle Transport | [251](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-251) |
| 7 Combustion | [311](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-311) |
| 8 Radiation | [351](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-351) |
| 9 Electromagnetic Hydrodynamics | [363](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-363) |
| 10 Rigid Body | [369](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-369) |
| 11 Discretization／Solution | [373](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.md#pdf-page-373) |

**版本定位差異：**兩版 Modeling Guide 的 §5.5／§5.7／§6.2／§7.18 起始頁分別由 v251 的 251／256／296／350，移至 v261 的 252／257／297／351。Theory Guide 的 §1.15／§5.6／§5.9／§5.13／§5.14 由 96／203／220／229／248 移至 97／204／221／230／249。這是 PDF bookmarks 核對所得的定位差異，未據此推定模型規則改變。

## 本輪來源盤點與剩餘範圍

本機 catalog 的 CFX 來源共 **1,019 筆**：1,015 筆 `body_present`（1,010 HTML、4 PDF、1 Markdown）與 4 個範例附件（2 `.py`、2 `.ipynb`）。來源版本欄為 unknown 1,014、v251 2、v261 3；全部來源與非空 text paths 存在。SQLite 的 CFX body records 另含本字典，不能直接把 product 分組筆數當原始來源數。

| 已保存手冊 | Source ID | 本輪處理 |
|---|---|---|
| [v251 Modeling Guide PDF](../ANSYS_Document/CFX/v251/manuals/Ansys_CFX-Solver_Modeling_Guide.pdf) | `ansys_7e4f7e457c8aac71e60ef45d` | 754 頁；PDF／cache／同名 Markdown 雜湊相符，754 個連續頁標題。保留先前有界主題，核對全部頂層章節與子節定位差異。 |
| [v261 Modeling Guide PDF](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Modeling_Guide.pdf) | `ansys_45ccf069fc36c5b2c371a978` | 754 頁；PDF／cache／同名 Markdown 雜湊相符，754 個連續頁標題。新增邊界、多相、輻射等指定頁整理。 |
| [v251 Theory Guide PDF](../ANSYS_Document/CFX/v251/manuals/Ansys_CFX-Solver_Theory_Guide.pdf) | `ansys_11057d652d987e26c91f9a51` | 392 頁；PDF／cache／同名 Markdown 雜湊相符，392 個連續頁標題。核對全部頂層章節與子節定位差異，未逐章比對方程。 |
| [v261 Theory Guide PDF](../ANSYS_Document/CFX/v261/manuals/Ansys_CFX-Solver_Theory_Guide.pdf) | `ansys_b93d1952273bccaf13eb745a` | 392 頁；PDF／cache／同名 Markdown 雜湊相符，392 個連續頁標題。新增離散化、coupled solver、closure 與多物理概念的指定頁整理。 |

四份 PDF 合計 2,292 個連續 `## PDF Page N` 標題，未發現無文字而只有圖片的頁面；這是轉換完整性探測，不表示圖、公式或表格都被文字化。原始 PDF 保留圖表與公式；需要符號、上下標或跨欄表格時應回 PDF。1,010 個 HTML 的來源／Markdown 共 2,020 項 SHA-256 與 conversion manifest 相符，狀態全為 `converted`，不需重轉。

| 較廣父題 | 狀態與剩餘範圍 |
|---|---|
| PyCFX／CFX 版本相容性 | `source_limited`；已有安裝下限與初版 local-machine 條件，但沒有完整 PyCFX／產品／Python／平台配對矩陣，未實機核對。 |
| CFX 使用者手冊與 solver 方法 | `source_limited`；兩版 Modeling／Theory PDF 已保存並建立完整章節入口，但 CFX-Pre、Solver Manager、CFD-Post 完整使用者手冊不在本輪本機來源中；本頁只整理可明確回頁的有界主題，完整模型、CCL、物性、網格與 solver theory 尚未逐章核讀。 |

API reference 仍以 catalog 分類與抽樣定位；本輪未逐條閱讀千筆 API、重轉已有且雜湊一致的檔案、執行範例、檢視所有圖表或驗證數值模型。REA 萃取內容未修改。

## 來源與限制

- [PyCFX User guide](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/guide/09919209fc2b-user_guide_contents.md)（`ansys_f34a7ba2d0ad112640d730d8`）與 [session 說明](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/guide/905297a05e5e-session.md)（`ansys_c58523f59daaf38e134d31d7`）
- [Launching CFX](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/guide/3b3f3b82028d-launching_cfx.md)（`ansys_a4a0afff47aac7962b2138aa`）及 [安裝說明](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/guide/9a36ac675d53-installation.md)（`ansys_cdad416d6d922df3911d2bd8`）
- [PyCFX logging](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/guide/5f69c3181039-log.md)（`ansys_d64b587bf3782bedf4574901`）
- [Static Mixer 範例](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/tutorial/fbaea448ebb2-01-introductory-example-static-mixer.md)（`ansys_c1a309e2c8bf661cd1367ed9`）與 [Fourier Transformation Blade Flutter 範例](../ANSYS_Document/CFX/sdk/ansys-cfx-core/0.3.0/tutorial/ccb852478997-02-fourier-transformation-blade-flutter.md)（`ansys_df8190712c5398b467b1edc7`）

本頁包含 PyCFX SDK 與 Modeling Guide 的有界整理，不替代 CFX-Pre、CFX-Solver 或 CFD-Post 完整手冊。PyCFX stable 頁中的產品相容性與 API 行為仍需按實際安裝版本查核；較廣父題依上表保留 `source_limited`。本輪只修改此字典頁，未啟動 CFX session、範例或求解。


## 2026-11-04：Wave 2 本機來源盤點與限制說明

本批完成 cfx 模組既有本機 catalog 文件（共 1019 筆）與 sources 清冊（共 1019 筆）之完整雜湊、正文路徑與標籤結構核對。本機未快取或具備企業授權/登入限制之線上主題誠實標記為缺口（保持現有非 complete 狀態），未擅自虛構未核實之線上 API 簽名或執行求解運算。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/cfx_module_conversion_report_20261104.md)。
