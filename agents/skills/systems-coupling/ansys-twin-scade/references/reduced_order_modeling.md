# 降階模型 (ROM) 構建工法

> [!NOTE]
> 本手冊依據官方知識字典 `twinai.md` 與 `scade_one` 權威技術規格擴充，提供深度工程指導。

## 1. 原理與設定準則

本模組於高精度數值模擬時，必須遵循以下邊界設定與收斂規範：
- 數值精度與單位一致性：務必先確認全域坐標系統、材料參數庫與求解單位（MKS/SI）。
- 網格劃分策略：實施局部特徵網格加密，並於梯度變化劇烈區域進行自適應細化。
- 監控物理量：除了求解器預設殘差之外，必須定義面通量、力矩或特徵頻率等客觀物理監控器。

## 2. 核心規範與字典精要

# PyTwin / TwinAI 知識字典

> 依本機 PyTwin 0.13.0 文件與 Users Guide 1.62 PDF 整理。SDK package 版號不等同 TwinAI 產品 release；產品 release 未知時維持 unknown。

## Twin model 執行生命週期

PyTwin 以 `TwinRuntime` 載入與執行 TWIN。官方 Runtime API 頁描述的生命週期可按以下職責理解：

1. `twin_load(log_level, fmi_type=FmiType.UNDEFINED)` 開啟並載入 TWIN。`log_level` 可選 `TWIN_LOG_ALL`、`TWIN_LOG_WARNING`、`TWIN_LOG_ERROR`、`TWIN_LOG_FATAL` 或 `TWIN_NO_LOG`；FMI 類型可選 `FmiType.CS`、`FmiType.ME` 或 `FmiType.UNDEFINED`。若模型不支援指定的 FMI 類型，文件指出會引發錯誤。
2. `twin_instantiate()` 建立 TWIN model instance。
3. `twin_initialize()` 初始化模型；API 明確要求此呼叫必須在 `twin_instantiate()` 之後。
4. 模擬或評估完成後呼叫 `twin_close()` 關閉模型。呼叫後原 `TwinRuntime` instance 不再有效；要再呼叫其他 Runtime 函式前，文件要求建立新的 `TwinRuntime` model instance。

這些 API 頁描述單一 model 的生命週期與 FMI/logging 參數，沒有詳述錯誤碼、錯誤恢復或重新載入同一物件的行為。`twin_simulate(time_stop, time_step=0)` 從目前時間推進至 stop point；`time_step=0` 表示一次 stepping call，內部積分仍可能使用較小步長。大於零時會以指定步長多次 stepping，不要將外部輸出點間隔等同求解器內部積分步長。

來源：PyTwin 0.13.0 文件集合中的 **`twin_load`**、**`twin_instantiate`**、**`twin_initialize`**、**`twin_close`**。各頁網址使用 `version/stable`，清冊產品 release 維持 unknown；PyTwin SDK 路徑中的 0.13.0 不等於 TwinAI 產品版號。

## 單次與批次評估

| 方法 | 輸入 | 步長與輸出語意 | 來源 |
|---|---|---|---|
| `twin_simulate` | `time_stop`，可選 `time_step` | 從目前時間推進；0 為單次 stepping call | PyTwin 0.13.0 API |
| `twin_simulate_batch_mode` | `pandas.DataFrame`、輸出欄名 | 回傳 DataFrame；`step_size=0` 使用輸入時間點，非零時等距輸出；支援 `interpolate` 與 `time_as_index` | PyTwin 0.13.0 API |
| `twin_simulate_batch_mode_csv` | 輸入與輸出 CSV 路徑 | CSV 第一欄為時間，其後為輸入／輸出；輸出路徑為空時不產生輸出 | PyTwin 0.13.0 API |

步長語意：單次 `twin_simulate` 的 `time_step=0` 只呼叫一次 stepping，從前一個 stop point 推進到 `time_stop`；模型內部仍可採用更小的數值積分步長。非零 `time_step` 則以 h 多次推進。批次 API 的 `step_size=0` 以輸入時間點作為輸出點；非零時輸出等距 h。輸出點間隔不代表模型內部積分步長。

DataFrame API 的 `output_column_names` 須以 `Time` 為第一欄；`time_as_index=True` 會重設輸入 DataFrame index，預設為 False。CSV API 的輸入與輸出皆以時間為第一欄、其後依序為 inputs／outputs，輸入標題列可有可無；`output_csv` 為空字串或 `NULL` 時不產生輸出檔。兩種 batch API 的 `interpolate` 僅在 `step_size > 0` 時用於 real continuous variables；文件沒有保證任意型別或輸入資料均可插值。使用前應核對模型輸入欄名與輸出欄位順序。

來源：**`twin_simulate`**、**`twin_simulate_batch_mode`**、**`twin_simulate_batch_mode_csv`**。三頁 URL 均使用 `version/stable`；本機 SDK 路徑為 0.13.0，產品 release 維持 unknown。

## TWIN 檔案與 ROM 範例範圍

本機 PyTwin examples index 將範例分成 Twin creation、Twin evaluation、TBROM evaluation 與 Twin deployment。以下整理本機快取的三個詳細範例；index 中其餘範例目前只有標題與用途簡介，不能據此重建完整步驟。

| 範例 | 文件展示的流程 | 適用範圍與限制 |
| --- | --- | --- |
| Static ROM creation, Twin generation and evaluation | 以 PyAEDT 根據 training data 建立 static ROM、組成並匯出 TWIN，再以 PyTwin 載入和評估；範例對 probe 23 的時間歷程作後處理並與參考結果比較。 | 文件明示需安裝 Twin Builder 2025 R1 或更新版本。案例資料與 probe 結果不構成通用精度保證。 |
| Twin evaluation（Coupled Clutches） | 載入含三個 coupled clutches 的動態 Twin，從外部 CSV 取得輸入，分別以 step-by-step 及 batch mode 執行並比較輸出。範例模型有 4 個 inputs、3 個 outputs。 | 輸入輸出數量及 CSV 格式對應該 Twin；其他模型欄位須按實際模型檢查。 |
| Parametric dynamic twin evaluation（Electric Range） | 對電動車續航 Twin 改變 vehicle mass 與 electric power load 等參數，模擬重複 WLTP class 3 速度循環，再比較速度與續航輸出。 | 課程案例的負載、車重與駕駛循環不是一般車輛預測設定或驗證資料。 |

index 另外列出 TBROM examples：影像生成、field snapshot／NumPy array、輸入場投影、CFD／FEA 網格視覺化、資料轉交 pyMAPDL、靜態結構分析與最佳化、parametric field history；deployment 分類列有 TBROM interactive visualization GUI。這些只是 index 的範例分類與標題，詳細 workflow 尚未逐頁整理。TBROM 範例涉及 field ROM，不能推定每個 TWIN 檔案都含相同 ROM、網格或資源目錄。

來源：**Examples index**（`ansys_96a71dbfb91ed9e210abb5a6`）；**Static ROM creation, Twin generation and evaluation**（`ansys_67197aea9faf532a65a17e82`）；**Twin evaluation**（`ansys_4a4ff6995b03f7e684884794`）；**Parametric dynamic twin evaluation**（`ansys_85fc893d60a2672873dc36ec`）。來源網站使用 `version/stable`，本機文件路徑為 PyTwin 0.13.0，產品 release 維持 unknown。

## 版本與待查

API 文件來自 PyTwin 0.13.0 SDK 路徑；官方網址使用 `version/stable`，因此擷取時的網址未固定到不可變版本標籤。清冊另將 `TwinAI/unknown/manuals/UsersGuide_1.62.pdf` 歸在 TwinAI，但 PDF Page 1 封面標示為 *OPTIMICA Compiler Toolkit, Version 1.62*，已排除於 PyTwin 字典及產品搜尋；索引標籤改為 `general`。該 PDF sidecar 仍可全文檢索並留在來源清冊供分類稽核。尚未逐頁視覺校對該 PDF 的表格與圖片，也未執行 PyTwin 模擬。

## 高階 TwinModel 評估

PyTwin 提供 `TwinModel` 高階封裝，適合以 Python 整合模型評估流程；它包括 scalar inputs/outputs、TBROM field inputs/outputs 等介面。這是 API 使用層的便利封裝，不能推論會改變 Twin runtime 的模型物理行為。官方入門頁指出，與 Twin runtime 互動可能依案例需要 TwinAI license；此授權需求應按實際模型與部署情境確認。

- 呼叫 `initialize_evaluation()` 後才能使用逐步或批次評估。`evaluate_step_by_step(step_size, inputs=None, field_inputs=None)` 的步長單位是秒，且必須為正值；未提供的 scalar input 保留目前值，名稱不在模型 `input_names` 的 key 不更新輸入。`field_inputs` 結構為 `{tbrom_name: {field_input_name: snapshot}}`，snapshot 可用 NumPy array 或檔案路徑。若同一 TBROM 的 field input 與 `inputs` 中的 mode coefficient inputs 同時提供，field input 會覆蓋該 ROM 的係數輸入。
- `evaluate_batch(inputs_df, field_inputs=None)` 要求輸入 DataFrame 含 `Time` 欄及各輸入欄，且時間序列自 `t=0 s` 起；欄名須對應 Twin input 名稱。未提供的 input 維持初始化值。每個 field input 須對應每一個時間點的一個 snapshot（array 或檔案路徑）；輸出為對應的 DataFrame。官方 API 列出缺少 `Time`、缺少零時刻、snapshot 數量不符及 field/ROM 名稱錯誤等例外。
- 低階 Runtime API 另提供 `twin_set_inputs(input_array)` 一次設定所有輸入、`twin_get_outputs()` 讀取所有輸出；這些位置式 list API 的順序應先由模型輸入／輸出名稱清單確認，不要只依猜測排列。

來源：**PyTwin overview**（`ansys_9324670351196a1e520446fe`）、**initialize_evaluation**（`ansys_e92bb3543aaf7c5b6e9daa9d`）、**evaluate_step_by_step**（`ansys_d3a05e52f8ce4cfd71193b61`）、**evaluate_batch**（`ansys_e3ca2bf67fd851d3758b6d03`）、**twin_set_inputs**（`ansys_ad687d5775f080bcb1fc774e`）、**twin_get_outputs**（`ansys_2de5b828e54590175332059b`）。官方網址均使用 `version/stable`，本機側錄路徑為 PyTwin 0.13.0；不代表 Ansys TwinAI 產品 release。

## 工作目錄與全域日誌

PyTwin 0.13.0 User Guide 說明預設啟用 `INFO` logging，模擬輸出檔放在 `%temp%/pytwin`。`modify_pytwin_working_dir(path, erase=False)` 可變更工作目錄；`erase=False` 是 API 文件列出的預設值。`modify_pytwin_logging(new_option, new_level)` 可把日誌導向檔案或 console，也可停用；預設是 file 與 `INFO`。日誌設定為同一 Python process 的所有 PyTwin objects 共用，因此在多模型程式中改 logging option/level 會影響同 process 的其他 PyTwin 物件。可用 `get_pytwin_log_file()` 查詢目前 log path。這些是全域設定，使用前應明確設定與保存日誌路徑。

來源：**User guide — Global settings**、**modify_pytwin_working_dir**（`ansys_76694e50586a59ed155eb2c0`）、**modify_pytwin_logging**（`ansys_4db94e053435bc0cd2a6eedc`）。User Guide HTML URL 為 `https://twin.docs.pyansys.com/version/stable/user_guide/index.html`；API URL 使用 stable。

## TwinModel 狀態保存與續算

`save_state()` 可在模型初始化後以及 step-by-step evaluation 後保存 TwinModel 狀態，官方範例將它與 `load_state()` 配對：新 TwinModel 載入同一 `.twin` 檔，再依舊模型的 `id` 與 `evaluation_time` 載入狀態後續算。這段文件未說明狀態檔的耐久性、跨 PyTwin 或 Twin model 版本相容性、保存位置管理與失敗復原；不應假定可任意跨模型檔或版本復用。

來源：**save_state**（`ansys_9f7ccae54c6b7dde59ef2f12`）、**load_state**（`ansys_3a4923b03efb3d90342fc9f7`）。

## TBROM 場輸出與網格投影

TwinModel 的 `get_tbrom_output_field(rom_name)` 回傳以 point cloud 形式表達的 PyVista DataSet，值對應 TwinModel 目前狀態，模型每次評估後會更新。文件列出的限制包括：模型需含 TBROM、ROM 名稱有效、有可用 point file，且 TBROM mode coefficients outputs 已連接到 twin outputs。

若要把 TBROM output field 投影到目標 mesh，須先呼叫 `project_tbrom_on_mesh()`，再呼叫 `get_tbrom_output_field_on_mesh(rom_name)`。未提供 named selection 時結果是全域 PyVista DataSet；使用 named selection 投影時回傳以 selection 名稱對應 DataSet 的 dictionary。投影後的場同樣隨 TwinModel evaluation 狀態更新。文件中的 `interpolate=True` 範例是 API 使用示例，不能視為所有網格、拓樸或場資料都可成功插值的保證。

來源：**get_tbrom_output_field**（`ansys_fb5a6319aa6819e94c7e3272`）、**project_tbrom_on_mesh**（`ansys_836ca7b8020c485bdeb33e1e`）、**get_tbrom_output_field_on_mesh**（`ansys_9c80ca35d4e3d5a64a5d0585`）。



## 本機 tutorial 原碼補件（2026-11-04）

三組 tutorial 的 Notebook 與 Python 原件已另建逐 cell／全文文字補件，可按來源 ID 搜尋。Notebook 共 23 個 code 與 26 個 Markdown cells；Python 另有 3 個全文程式區塊。補件不含 Notebook outputs、圖片、下載資料或執行結果，未執行模擬。資料夾標記 `pytwin/0.13.0` 與 stable URL 分別記錄；附件 catalog 的 release／SDK 版本 unknown 保持不變。

| 案例 | 原碼資料形狀與邊界 | 文字補件 |
| --- | --- | --- |
| Coupled Clutches | 原碼下載 `.twin`、CSV 和 JSON config，再以 `TwinModel` 初始化，分別呼叫 `evaluate_step_by_step` 與 `evaluate_batch` 比較結果；欄名與步長以該模型輸入為準。 | **ipynb**（`ansys_329d4e5cc926d2e8d6a576bc`）；**py**（`ansys_f2ec4f52ef1c276f8904a5bb`） |
| Static ROM／Twin creation | 原碼解開 training-data ZIP，再啟動 `TwinBuilder` 建立 ROM、組成並匯出 TWIN，之後用 `TwinModel` 評估；包含 `shutil.rmtree(training_data_folder)` 清理資料夾，也會變更 AEDT session 的 Desktop configuration。 | **ipynb**（`ansys_ca92a3148b691c23edb56e51`）；**py**（`ansys_69c4c56b7114d53a11e41c47`） |
| Electric Range | 原碼用 `ElectricRange_powerLoad` 與 `ElectricRange_vehicleMass` 組成三組 parameter dictionaries，逐組初始化並按時間步評估；案例參數不代表一般車輛設定。 | **ipynb**（`ansys_7790ea8c678877ab31930971`）；**py**（`ansys_4d3715258efbaf1ff8c66d12`） |

三組原碼都包含 `download_file(..., force_download=True)`；外部檔案沒有因文字擷取而被下載或執行。Static ROM 範例原文要求 Twin Builder 2025 R1 或更新版本，此要求僅屬該範例；來源版本與執行環境相容性尚未實測。

## 官方 stable 網頁補件（2026-11-04 擷取）

本批從既有 Markdown 同站連結重試 20 個頁面，全部保存原始 HTML 與文字版。這批是擷取日期當下的 stable 網頁，未推定為本機 0.13.0 快照；與舊版共通或衝突的 API 語意仍須逐項比對。以下連結可回到獨立來源正文，原 HTML 保留圖像與版面回查依據。

| 官方頁面 | 類別／來源 ID | 本機文字 |
| --- | --- | --- |
| download_file — PyTwin | api_reference；`twinai_web_1ff449ca6c56e201_225494200afc` | **文字與原HTML連結** |
| load_data — PyTwin | api_reference；`twinai_web_96e4de9842b07a16_8983b7de09d6` | **文字與原HTML連結** |
| read_binary — PyTwin | api_reference；`twinai_web_4b3b0adf7987d383_73dcd7c9148e` | **文字與原HTML連結** |
| read_snapshot_size — PyTwin | api_reference；`twinai_web_599d93250c66d8c7_648b4f56a00a` | **文字與原HTML連結** |
| snapshot_to_array — PyTwin | api_reference；`twinai_web_7e3dba934abaa55e_61478f6c4a23` | **文字與原HTML連結** |
| write_binary — PyTwin | api_reference；`twinai_web_f75887c273320a95_ede6f5a5a066` | **文字與原HTML連結** |
| Contribute — PyTwin | guide；`twinai_web_83992ffab800c863_4e719a81a88b` | **文字與原HTML連結** |
| Parametric twin evaluation of a response surface ROM — PyTwin | tutorial；`twinai_web_821e2f39d9474450_47b13dea6393` | **文字與原HTML連結** |
| Twin evaluation of a scalar dynamic ROM — PyTwin | tutorial；`twinai_web_1fe1332969d4e896_a5088aee8371` | **文字與原HTML連結** |
| 3D field ROM example for images generation — PyTwin | tutorial；`twinai_web_f3a7d720ccab3bfa_af07597fdb61` | **文字與原HTML連結** |
| Twin evaluation of a 3D field ROM and data transfer to FEA model inputs — PyTwin | tutorial；`twinai_web_2863027b7bb061a2_7628a6c0fa35` | **文字與原HTML連結** |
| 3D field ROM example for input field snapshot projection and snapshot generation on demand — PyTwin | tutorial；`twinai_web_d4d1fafcb4c8d47c_c52dc32bb21e` | **文字與原HTML連結** |
| 3D field ROM example for field snapshot input and output as Numpy array — PyTwin | tutorial；`twinai_web_bbb68f1515fef2b7_8a872c4e2feb` | **文字與原HTML連結** |
| 3D field ROM example with CFD mesh based visualization — PyTwin | tutorial；`twinai_web_5d95d71e7f8731ac_00e556173588` | **文字與原HTML連結** |
| 3D field ROM example with FEA mesh based visualization — PyTwin | tutorial；`twinai_web_d7b55f7c1b5a4e4c_b9daad007f1b` | **文字與原HTML連結** |
| Static structural analysis and optimization using 3D field ROM — PyTwin | tutorial；`twinai_web_02584487cb002dc7_999f7b622f8c` | **文字與原HTML連結** |
| 3D parametric field history ROM example — PyTwin | tutorial；`twinai_web_a69d0a4548628727_95e08223ca93` | **文字與原HTML連結** |
| TBROM interactive visualization GUI application — PyTwin | tutorial；`twinai_web_fc38e6fb4e217f74_8093283f130c` | **文字與原HTML連結** |
| Index — PyTwin | guide；`twinai_web_e0563edc3dc953a5_2d45f682d08c` | **文字與原HTML連結** |
| Getting started — PyTwin | guide；`twinai_web_2c46cf13136702c3_b25b897c92b3` | **文字與原HTML連結** |

新取回的 11 個詳細 tutorial 本批只完成原文保存與索引，尚未整理全部操作步驟、API 變更、案例輸出與物理驗證；原先待整理主題保留。Index／Contribute 為導覽與開發流程來源，不能代替技術操作說明。本批未繼續遞迴擷取這 20 頁的新連結，餘下網址列在 URL 清冊。

## 3. 常見陷阱與防呆措施

1. **未定義求解範圍**：求解前未限定掃頻範圍或時間步長，導致求解發散。
2. **材料模型失配**：非線性材料未設定適當的切線模數或溫度相依曲線。
3. **介面通訊失敗**：多物理場耦合未對齊變數傳遞單位，導致數值非物理震盪。
