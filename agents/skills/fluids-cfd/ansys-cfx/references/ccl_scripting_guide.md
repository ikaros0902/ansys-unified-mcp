# CFX Command Language (CCL) 指南

> [!NOTE]
> 本手冊依據官方知識字典 `cfx.md` 與 `cfx` 權威技術規格擴充，提供深度工程指導。

## 1. 原理與設定準則

本模組於高精度數值模擬時，必須遵循以下邊界設定與收斂規範：
- 數值精度與單位一致性：務必先確認全域坐標系統、材料參數庫與求解單位（MKS/SI）。
- 網格劃分策略：實施局部特徵網格加密，並於梯度變化劇烈區域進行自適應細化。
- 監控物理量：除了求解器預設殘差之外，必須定義面通量、力矩或特徵頻率等客觀物理監控器。

## 2. 核心規範與字典精要

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

來源：**PyCFX sessions guide**（**來源清冊**）、**PyCFX launching guide**（**來源清冊**）。官方網址使用 `version/stable`，本機文件集合 metadata 指向 SDK 0.3.0；產品安裝 release 仍為 unknown。

## 設定樹與狀態

PreProcessing 與 PostProcessing 的 `setup` 物件以階層方式映射 CFX Command Language（CCL）結構；Python 設定物件的名稱由 CCL 類型／參數名稱轉小寫並以底線取代空格，named object 名稱與參數值保留 CCL 原字串。設定物件可用 `get_state()` 讀取、`set_state()` 指定狀態，也可呼叫物件取得其子項狀態，或用 `print_state()` 檢視文字表示。參數物件可用 `allowed_values()`（適用時還有 `min()`、`max()`）查限制；`is_active()` 與 `get_active_child_names()` 可檢查目前 session 中可用的設定項，因物理設定而 inactive 的項目不應假設可操作。PreProcessing setup 節點可呼叫 `get_physics_messages()` 取得全域或局部訊息，並依 `All`、`Beta`、`Information`、`Warning`、`Error` 篩選。

PreProcessing 在逐項變更物理設定時可能連動更新相依設定。例如 domain turbulence model 從 `k epsilon` 改為 `SST` 時，`turbulent_wall_functions` 會由 `Scalable` 改為 `Automatic`。Physics updates 限於 top-level objects 及其內部相依項；domain 內的變更不會自動更新 boundary object。以 dictionary 套用 state 的版本限制、optional state 清除方式與警告詳見[PreProcessing state 子題](#pycfx-preprocessing-的-state-dictionary-與-physics-updates)。

求解啟動後可用 `solution.wait_for_run()` 等待完成。文件亦說明 CFD-Post 的長時間運算操作可能等待較久；自動化流程應依實際呼叫與執行環境安排等待與錯誤處理。

### PyCFX PreProcessing 的 state dictionary 與 physics updates

PyCFX session guide 說明，對 PreProcessing 設定物件逐項指定 physics parameter 時，CFX 可能同步更新相依參數。例如把 domain turbulence model 從 `k epsilon` 改為 `SST`，`turbulent_wall_functions` 可從 `Scalable` 自動變成 `Automatic`。Physics updates 只在 top-level objects 之間連動；在 domain 內變更設定不會自動更新 boundary object。

**Dictionary state 有版本限制：**該頁明確指出，CFX 至 2026 R1（含）若以 dictionary 呼叫 `set_state()`，physics updates 不會執行，狀態會直接套用，因此 PreProcessing 可能落入物理不一致狀態。使用此方式後須檢查 physics warnings／errors；不可只以 setter 呼叫成功判定設定有效。

`set_state()` 的 dictionary 若省略 optional objects 或 parameters，不會將它們自動移除。若要清除，文件要求明確操作：optional parameter 設為 `None`；optional object 將 `enabled=False`；optional named object 使用 `del` 移除。這些是不同物件型別的清理方式，不應假設套用一份不完整 dictionary 就等於替換整個 CCL state。

此限制依 PyCFX `version/stable` session guide 原文，來源清冊 release 為 `unknown`；其中 CFX 版本上限只採文件明載的「up to and including 2026 R1」，不推定後續版本行為。本子題整理 setter／dictionary 差異與 optional-state 清理，不代表已執行 CFX session。

來源：**Use PyCFX sessions，官方 `version/stable` 指南**（**來源清冊**；SDK metadata 路徑為 0.3.0，release 維持 unknown）。

## PyCFX logging configuration

PyCFX 使用 Python 標準函式庫的 `logging` API；套件包含多個 logger，並提供標準格式的 `logging_config.yaml`，可編輯此 YAML 檔設定 logging。該頁未列出所有 logger 名稱、各 logger 的預設級別或設定檔實際搜尋路徑；需要調整時應依安裝的 PyCFX 版本及部署環境確認檔案位置與可用設定，不要自行假設套件讀取哪一份 YAML。

來源：[Configure logging，PyCFX 官方 `version/stable` 指南](https://cfx.docs.pyansys.com/version/stable/user_guide/log.html)／**本機 sidecar**（**來源清冊**）。來源 metadata 指向 SDK 0.3.0 文件集合，網址使用 stable，release 欄仍為 `unknown`。

## 啟動方式與 session 間資料承接

官方 launch guide 說明兩種主要 session 建立來源：

- `from_install()` 從本機安裝啟動 CFX。文件列出 `product_version`、`case_file_name`（`.cfx`）、`solver_input_file_name`（`.def`／`.mdef`）、既有 `run_directory`（`.dir`）、`results_file_name`（`.res`／`.mres`），以及傳給 `cfx5pre`、`cfx5solve` 或 `cfdpost` 的 `additional_arguments`。若不指定 `product_version`，文件表示會啟動最新支援版本。
- `from_session(existing)` 從既有 PyCFX session 建立下一種 session；新 session 繼承既有 session 的設定，包括 `product_version`。

跨階段資料時點：

1. 由 `PreProcessing` 建立 `Solver` 時，solver session 會擷取啟動當時 CFX-Pre 的 model setup。之後仍可修改原 preprocessing session，但這些變更不會改動已建立 solver session 所持有的設定。
2. 由 `Solver` 建立 `PostProcessing` 時，若 solver 已完成，結果檔會直接開啟；若尚未完成，PostProcessing session 會等待 run 完成後再讀取結果。Solver 亦可用 `solution.wait_for_run()` 等待求解完成。
3. 教學範例以 file-based 流程分別建立 PreProcessing、Solver 與 PostProcessing，並在階段間傳遞 `.def`／結果檔；不要求三個 CFX 元件必須同時存在於同一個 Python session。

**部署限制：**launch guide 明確寫 PyCFX 初版搭配 Ansys CFX 2025 R2 Service Pack 3 時，只支援在執行 Python 的同一部 local machine 啟動 CFX session。這是來源對初版的陳述；本機產品 release 清冊為 unknown，且沒有後續 CFX/PyCFX 完整相容矩陣，因此不據此推定其他版本或 container 支援。

來源：**Launching CFX**（**來源清冊**）、**session guide 的 Solver／PostProcessing 章節**（**來源清冊**）。

## PyCFX 0.3.0 安裝前提與本機版本定位

PyCFX 安裝指南標示支援 Windows／Linux 的 Python 3.10–3.14；使用者安裝命令為 `pip install ansys-cfx-core`。使用 PyCFX 必須另有授權的 Ansys CFX 安裝；指南明列支援 CFX 2025 R2 Service Pack 3 及更新版本。文件網站使用 `version/stable`，來源清冊的產品 release 仍為 `unknown`，因此此支援下限不表示本機已確認特定版本組合。

PyCFX 依 `AWP_ROOT<version>` 環境變數定位 Ansys 安裝。Windows 安裝程式會設定對應變數；Linux 使用者需自行設定。指南以 `AWP_ROOT252=/usr/ansys_inc/v252` 為例，供目前 shell 使用可執行 `export AWP_ROOT252=/usr/ansys_inc/v252`，要跨 shell 保留則加入使用者的 `~/.profile`。透過 `from_install()` 啟動時，明確傳入 `product_version` 會選用該版；省略時才選最新的受支援安裝版本。

**本機啟動邊界：**launch guide 說明 PyCFX 初版搭配 CFX 2025 R2 SP3 時，只支援在執行 Python 的同一部電腦啟動 CFX session。這是初版配對條件，不外推至後續 PyCFX／CFX release，也不構成遠端、容器或叢集啟動支援的確認。

**開發者安裝與一般使用者安裝不同：**若要從原始碼開發，指南列出 `pip install -e .[doc,tests,style]`；產生 API 類別需執行 `python codegen/allapigen.py`，且該步驟需要 Ansys CFX 安裝。上述 extras 與 code generation 是貢獻開發流程，不是一般使用者安裝命令。

來源：**PyCFX Installation**（**來源清冊**）、**Launch CFX**（**來源清冊**）。兩頁皆使用官方 `version/stable` URL，SDK 文件集合 metadata 為 0.3.0；本機未驗證 CFX 安裝、license、Python 相容性或 session 啟動。

## 官方範例的適用範圍

PyCFX Static Mixer 範例示範以 PreProcessing 建案、執行 CFX-Solver，再在 CFD-Post 做基本後處理。其模型描述為兩個入口向靜態混合器供水，範例入口速度均為 2 m/s、溫度分別為 315 K 與 285 K。這些是該教學案例的輸入值，不是其他混合器案例可直接沿用的設計條件。

## Static Mixer 教學：以檔案交接三種 session

官方 Static Mixer 範例採 file-based workflow：`PreProcessing` 建立 case、匯入 `StaticMixerMesh.gtm`、設定 domain 與 boundary conditions，呼叫 `get_physics_messages(severity="All")` 檢查設定訊息，再寫出 `static_mixer.def` 並關閉 preprocessing session；之後獨立建立 `Solver` session 執行並等待求解，取得 results file 名稱後關閉 solver；最後以該結果檔建立 `PostProcessing` session。文件說明三個元件可在不同時間、Python session 或機器設定下分開執行，但此範例明確只支援 local CFX-Solver 執行。

案例用兩個入口與一個出口：入口 normal speed 都是 `2 m/s`，static temperature 分別為 `315 K`、`285 K`；材料為 Water，模型採 thermal energy 與 k-epsilon，solver control 使用 upwind，physical timescale 為 `2 s`。這些是教學設定，不是一般靜態混合器的物理模型或收斂建議。

後處理部分載入結果後，以 CFD-Post 建立 Pressure contour、輸出 PNG；建立切片 plane 時先 `suspend()`，完成 ZX slice 設定後 `unsuspend()`，減少逐項修改時的中間重算。範例亦建立 CEL expression `maxVal(Temperature)@out - minVal(Temperature)@out` 並呼叫 `evaluate()`。這些步驟示範 API 操作，不構成收斂、網格獨立性或物理正確性驗證。

來源：**Simulate flow in a static mixer**（**來源清冊**；SDK metadata `ansys-cfx-core 0.3.0`，來源為 official `version/stable`，產品 release `unknown`）。


## Fourier Transformation Blade Flutter 教學：初始條件、time integration 與 harmonic balance

官方 PyCFX 範例以單通道軸流壓縮機轉子（完整轉子 36 blades）示範 transient blade flutter。匯入的網格只有一個 passage；範例用 CFX Command Language（CCL）將 mesh transformation 設為兩個 passages，因該 Fourier Transformation 案例需要 two-passage model，且文件說明目前 mesh transformation 須經 CCL 設定。此網格配置屬該範例，不是一般 blade-row 建模規則。

流程依序建立不含 transient blade row method 的初始 solver case 並產生初始條件；接著修改同一 preprocessing setup，以 Fourier Transformation 建立 time-integration case、求解並保存結果；最後沿用該初始條件建立 harmonic-balance case、求解，再對兩組結果後處理。範例指出部分 setup 與後處理可在前一 solver run 尚未結束時先準備；若 CFD-Post 載入尚在計算的結果，PostProcessing session 會等 solver 完成後再讀取。

後處理以 `Total Wall Work = Wall Work Density * Area` 建立 expression，於 R1 Blade 建立 contour，並在支援的版本輸出 animation。教學以 `CFXVersion > v252` 分支使用不同 Aerodynamic Damping monitor object path；頁面另明示 PyCFX 2025 R2 不支援 animation。這些條件只記錄教學中的版本分支，使用者應核對實際安裝版本與 API；案例設定、結果圖及動畫不構成數值收斂或物理驗證。

來源：**Set up a Fourier Transformation Blade Flutter case**（**來源清冊**；PyCFX SDK metadata 0.3.0，官方 URL 使用 `version/stable`，CFX product release 維持 unknown）。


## v251／v261 收斂判讀：Residual、Global Balance 與目標量

CFX 將 residual 定義為控制體保守方程的局部不平衡，並使用 normalized residual 判斷數值收斂。可選 RMS 或 MAX residual 與 target；手冊提醒湍流輸運方程的 residual 不納入 solver 自動停止的收斂判定，多相 volume-fraction 方程使用的判據則比指定 target 高 10 倍。Transient 計算的 residual 包含時間項，target 控制每一 timestep 的 coefficient iterations，不能把它與時間步獨立性視為同一件事。

| v261 手冊所列 RMS 指引 | 使用界線 |
|---|---|
| 預設 target 為 `1e-4`；手冊稱此為 relatively loose。 | 只是手冊指引，不是所有工程案例的驗收門檻。 |
| `1e-5` 稱為 good convergence；`1e-6` 或更低稱為 very tight。 | 是否需要、是否能達成依模型與目標量而異；手冊明說 single precision 可能無法達成很緊的 target。 |
| MAX 通常約為 RMS 的 10 倍，但也可能高很多。 | 高 MAX 可能集中於局部非定常區；須核對關鍵力、效率或其他目標量的變化。 |

Residual 達 target 後，仍需檢查 global balances 與關鍵 derived quantities。具有很慢物理過程的問題，可能在 global balance 滿足前已達 residual target。每次 run 也應辨別停止原因是達成 convergence criteria，還是只達 Maximum Number of Iterations；定量結果須檢查目標量對 target 的敏感度。

來源：Modeling Guide v261 **PDF Page 585**、**586**、**588**（`ansys_45ccf069fc36c5b2c371a978`）。本輪在 v251 相同實頁核對上述關鍵規則（`ansys_7e4f7e457c8aac71e60ef45d`），未發現這些段落的規則差異；未比對整本手冊。

## v261 Timescale：穩態鬆弛、Auto 與暫態時間

穩態求解可透過 timescale 對非線性方程提供鬆弛；暫態的 timestep／time duration 則追蹤模擬的真實時間。`Physical Timescale` 讓選定方程在流域使用固定 timescale；不能只因名稱含 physical 就把穩態迭代數轉成經過的物理時間。

`Auto Timescale` 是預設 timescale control，手冊稱其估計常較保守。`Timescale Factor` 乘上內部估計，`Maximum Timescale` 則以上限約束內部計算。對 advection-dominated flow，手冊以長度／速度尺度作為估計依據；尺度過大可能呈現跳動或不收斂，過小可能只緩慢、穩定地收斂。這不是所有旋轉、浮力或多物理問題的通用時間步公式。

Timescale 可在 global、domain、phase、equation class 或單一 equation 層級設定；較特定的 equation／phase／domain 設定優先於較廣的設定。手冊的 13 項優先序中，CFX-Pre UI 只支援第 8、12、13 類，其餘需編輯 CCL；對 energy equation 另設 timescale 可能使 global Solid Timescale Factor 不再生效。完整優先序應回原表查閱，不能只看 UI 顯示的一個值。

來源：Modeling Guide v261 **PDF Pages 570–574，自 570 起**（`ansys_45ccf069fc36c5b2c371a978`）；v251 同頁關鍵文字亦核對。此處未替任何模型選定 timestep 或 timescale。

## v261 Frame Change／Mixing Model 的選擇界線

General Connection 的 frame-change／mixing 選項包括 Frozen Rotor、Stage（Mixing-Plane）、Transient Rotor-Stator；原文要求介面兩側都是 surface of revolution，且掃過相同的旋轉曲面。三者對相對位置與時間效應的假設不同。

| 模型 | 文件描述 | 主要限制 |
|---|---|---|
| Frozen Rotor | 兩側相對方位固定；求解 frame／pitch change 的穩態近似，三種模型中計算成本最低。 | 不模擬介面 transient interaction，也不重現真實相對運動混合損失；相對方位可能影響解。 |
| Stage／Mixing-Plane | 對介面 band 的 flux 作周向平均，在各參考系取得穩態解，包含平均化混合損失。 | 忽略 transient interaction；周向非均勻性相對 component pitch 很大時不適用，例如手冊所舉 off-design pump／volute。 |
| Transient Rotor-Stator | 隨 timestep 更新介面相對位置，求解旋轉元件之間的 transient interaction。 | 時間、儲存與後處理成本較高；pitch 不等的 passage 配置需另處理。該 sliding interface 不支援 translational relative motion。 |

若關注啟動過程，須以對應物理初始條件開始；若關注週期性運轉，手冊說可以 Frozen Rotor 穩態解作初始猜測。這是初始化策略，不證明該穩態解或後續暫態已符合工程驗收。

來源：Modeling Guide v261 **PDF Pages 239–242，自 239 起**（`ansys_45ccf069fc36c5b2c371a978`）；v251 同頁關鍵規則亦核對。介面圖與 pitch-change 幾何未作目視或模型驗證。

## v261 Automatic Wall Treatment 與 Yplus 判讀

Wall-function 方法以近壁經驗關係節省解析邊界層的成本；Low-Reynolds-Number 方法則以壁面法向的細網格解析黏性影響區。此處的 low Reynolds number 指近壁 turbulent Reynolds number，不能由整個裝置的 Reynolds number 高低直接判斷是否適用。

Omega-based 模型的 automatic near-wall treatment 可隨網格細化，在 wall-function 與 low-Re near-wall formulation 間平滑切換。v261 手冊建議，要利用細網格帶來的改善，應嘗試以至少 10 個 nodes 解析邊界層；這是手冊對該用途的指引，未取代網格獨立性、近壁傳熱、轉捩或粗糙壁需求的檢查。

CFX 結果同時提供 `Yplus` 與 `Solver Yplus`。前者依壁面至第一個 node 的距離及 wall shear stress 計算，是手冊建議用來判斷近壁網格間距的量；後者為 solver 內部定義及向後相容用途。粗糙壁還需區分 equivalent sand-grain roughness 與實際 geometric roughness，兩者不能直接等同。字典不設定統一的 y+ 合格值。

來源：Modeling Guide v261 **PDF Page 227**、**230–231，自 230 起**（`ansys_45ccf069fc36c5b2c371a978`）；v251 同頁關鍵規則亦核對。未抽查所有 wall-treatment 方程、圖表或網格。

## v251／v261 材料屬性壓力與 CEL `p` 的原文矛盾

Material Properties 章節有一項不能直接當成確定 API 規則的矛盾：兩版實頁 89 的 CEL Expressions 說，材料屬性 expression 中的 `p` 解讀為 **absolute pressure**，reference pressure 則使用 `Pref`；兩版實頁 94 在 Table Generation Pressure and Temperature Limits 又說，density／specific heat expression 裡的 CEL `p` 仍使用 **relative pressure**。本輪從兩版 PDF 直接抽取均找到這兩種說法，不是只有 sidecar 出現。

實頁 94 對 property-table minimum／maximum pressure limits 的說法則明確：這些 limits 以 absolute values 輸入，不相對於 reference pressure；範圍過窄會使 property 值在界限被 clipping。這一條可整理為文件規則，但不能用它消解 `p` 解讀的矛盾。

因此本字典保留此差異，未給出材料 expression 應將 `p` 當哪一類壓力的確定結論。使用前須依目標 CFX 版本的有效官方說明或受控驗證釐清；不應僅因 expression 被接受就視為單位及壓力基準正確。

來源：Modeling Guide v261 **PDF Page 89**、**94**（`ansys_45ccf069fc36c5b2c371a978`）；v251 **PDF Page 89**、**94**（`ansys_7e4f7e457c8aac71e60ef45d`）。

## v261 Initial Values File 與 Continue History

## 3. 常見陷阱與防呆措施

1. **未定義求解範圍**：求解前未限定掃頻範圍或時間步長，導致求解發散。
2. **材料模型失配**：非線性材料未設定適當的切線模數或溫度相依曲線。
3. **介面通訊失敗**：多物理場耦合未對齊變數傳遞單位，導致數值非物理震盪。
