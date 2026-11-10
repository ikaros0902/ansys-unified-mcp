# Fluent／PyFluent 主題字典

本頁整理本機取得的 PyFluent 使用文件。本機 Fluent catalog 有 1,693 筆來源，其中 1,666 筆 API reference 尚未逐頁核讀。完整檔案／轉換盤點及缺口見 [來源與轉換覆核紀錄](../maintenance/knowledge_dictionary_passes/2026-11-04/fluent_source_conversion_review.md)；目前整理屬 PyFluent 指南與指定案例，並非 Fluent solver 全產品手冊。來源清冊的 SDK 欄位與快取目錄均標示 `ansys-fluent-core` 0.42.1，但逐頁 HTML 的 `docsearch:version` 並不一致：本頁核讀的六頁中，五頁標示 0.40.3、一頁標示 0.43.0。以下按頁面內嵌版本標示證據，0.42.1 僅代表來源清冊欄位／快取路徑，不據此推定 Fluent 求解器產品 release 或 SDK 相容性。

## 主題導覽

### 1. PyFluent session 與啟動方式

PyFluent 以 session 物件連接 Fluent。指南列出 `Solver.from_install()`、`Solver.from_container()`、`Solver.from_connection()`、`Solver.from_pim()` 等建立方式；`from_<...>` class methods 是新程式建議使用的入口。Launch guide 也涵蓋 container 啟動與連接既有 session。`Meshing` 可在需要時切換到 solver mode；`PureMeshing` 則不提供切換 solver 的功能。

**使用前確認**

- 依本機安裝、container 或已存在的 server session 選擇連線方式。
- 區分 meshing session 與 solver session；確認輸入 case／data 檔由正確 session 載入。
- 連線成功後由 `solver_session.fields` 與 `solver_session.settings` 取得各自負責的資料與設定介面。

來源：[Launching and connecting to Fluent（頁面內嵌版本 0.40.3；來源清冊欄位 0.42.1）](../ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/guide/3e250b04d6e1-launching_ansys_fluent.md)；[Using PyFluent sessions（頁面內嵌版本 0.40.3；來源清冊欄位 0.42.1）](../ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/guide/1f24dea9506e-session.md)。

#### PyFluent launch／attach 入口選擇與連線資訊

頁面內嵌版本 0.40.3 的指南建議新程式優先使用 session type 的 `from_<...>` class methods；選擇時依 Fluent session 是本機啟動、容器／PIM 啟動，還是外部已啟動來決定：

| 入口 | 文件描述的適用情境 | 先確認 |
|---|---|---|
| `Solver.from_install()`、`Meshing.from_install()` 等 | 從本機安裝啟動 Fluent，不需 Docker／Podman。 | 本機已有可用 Fluent 安裝；此入口代表 launch。 |
| `...from_container()` | 在容器環境啟動；可用 Docker Compose 或 Podman Compose，設定 port mapping，或建立隔離／平行 session。 | Compose 類型與 `container_dict` 的埠映射；文件示例的 `product_version=v252` 是示例，不代表本機 SDK 預設或目前產品版。 |
| `...from_pim()` | PyFluent 在已配置 PIM 的環境中啟動。 | PIM 環境是否已配置。 |
| `...from_connection()` | 附加到先前或外部啟動的 Fluent session，可由另一 process／system 連線。 | 外部 Fluent 必須先啟用 gRPC server；建議傳入 server-info file，內含連線所需 IP、port 與 password。 |

低階 `launch_fluent()` 可由 Python 啟動 Fluent 並啟動 gRPC server；`connect_to_fluent()` 可連到已開啟 gRPC 的 session。指南列出的 server 啟動方式包含 `-sifile=<server_info_file_name>`、solution mode TUI 的 `server/start-server`，以及 GUI 的 Applications／Server／Start 項目；未指定檔名時 server-info file 會自動產生。這些入口說明的是如何建立或附加連線，不取代前一子題所述的 session 結束與 Fluent process 清理規則。

來源：[Launching and connecting to Fluent（頁面內嵌版本 0.40.3；快取路徑 0.42.1）](../ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/guide/3e250b04d6e1-launching_ansys_fluent.md)（[來源清冊](sources.csv#ansys_e40af2e24d84fda0f3d5674e)）；[Using PyFluent sessions（頁面內嵌版本 0.40.3；快取路徑 0.42.1）](../ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/guide/1f24dea9506e-session.md)（[來源清冊](sources.csv#ansys_a79a80046f30ff1aec049a1c)）。官方 URL 使用 `version/stable`，來源 release 維持 unknown。


#### Fluent mode 與啟動參數

文件把 session type 和 Fluent mode 分開說明：`Solver`、`Meshing`、`PureMeshing`、`PrePost` 等 type 決定 client 可用介面；mode 決定啟動 Fluent 時提供的工作環境。低階 `launch_fluent()` 範例涵蓋 `SOLVER`、`MESHING`、`PRE_POST`，以及 `precision`、`dimension`、`processor_count` 等選項。

| 設定 | 指南範例用途 | 注意事項 |
|---|---|---|
| `mode` | 選 solver、meshing 或 pre/post；pre/post 可做 setup／post-processing，不執行計算。 | `launch_fluent()` 未指定時，指南範例等同 solver mode。 |
| `precision`、`dimension` | 例子使用 `Precision.DOUBLE`、`Dimension.TWO`／`THREE`。 | 依模型及產品要求選擇；例子不是適用所有分析的建議。 |
| `processor_count` | 指定本機或分散式執行的處理器數；分散式例子另傳 `-cnf` 至 `additional_arguments`。 | 機器名稱、核心數及資源配置是範例值，需依實際環境與排程設定。 |

同一指南指出 job scheduler 情境下，`launch_fluent()` 會自動偵測機器清單與核心數，並列出 Altair Grid Engine／UGE、SGE、LSF、PBS、Slurm；本字典僅記錄文件能力入口，未整理各 scheduler 的完整提交腳本。來源：[Launching and connecting to Fluent（PyFluent 頁面內嵌版本 0.40.3）](../ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/guide/3e250b04d6e1-launching_ansys_fluent.md#launcher-options)（[來源清冊](sources.csv#ansys_e40af2e24d84fda0f3d5674e)）。

#### PyFluent session 結束與 Fluent process 清理

各 PyFluent session 可獨立結束。對由 `from_<...>` launch method（例如 `Solver.from_install()`）建立的 session 呼叫 `.exit()`，會結束該 PyFluent session 並終止連接的 Fluent session。若 PyFluent 物件是用 `from_connection()` 附加到既有 Fluent process，呼叫 `.exit()` 預設不會終止該 Fluent process；要設定附加既有 process 時的清理行為，官方頁指向直接呼叫 `connect_to_fluent()` 並使用 `cleanup_on_exit` 參數。

文件也指出，PyFluent session 物件被 Python garbage collector 回收時會隱式退出，規則與明確呼叫 `.exit()` 相同；Python interpreter 結束時所有仍活躍的 session 會退出。為避免把連線方式和 process 所有權混為一談，實務上應記錄 session 是 launch 還是 attach，並在工作結束時明確處理其生命週期（這是依文件描述所作的操作建議）。

此摘要只涵蓋 session 結束與 process 清理；不同 `cleanup_on_exit` 設定的完整參數效果及不同啟動環境的 process 管理細節，需查目標 SDK 版本 API。來源頁使用 `version/stable`，頁面內嵌版本為 0.40.3，來源清冊 SDK 欄位為 0.42.1，精確 release 未由頁面標示。

來源：[Using PyFluent sessions，官方 `version/stable` 指南](https://fluent.docs.pyansys.com/version/stable/user_guide/session/session.html)／[本機 sidecar](../ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/guide/1f24dea9506e-session.md)（[來源清冊](sources.csv#ansys_a79a80046f30ff1aec049a1c)）。

#### Active session、session 切換與 case 共用

若要使用 top-level settings objects／functions 而不逐次傳入 session，可在 `with using(session):` 區塊中設定 active session；區塊外的 settings tree 沒有 active session 時不可用，替代方式是明確傳入 `settings_source=...`。多個 session 可各自存在，分開的 `using(session)` 區塊讓呼叫使用對應 session；active session 為 thread-local，不會自動出現在其他 thread。

`Meshing.switch_to_solver()` 會在同一 Fluent instance 切換到 solver，原 `Meshing` session 隨後不可再使用；文件指出沒有由 solution 切回 meshing 的方法。`PureMeshing` 不支援切換（呼叫會觸發 `AttributeError`），但可用 `transfer_mesh_to_solvers(...)` 將 mesh 傳給 solver sessions。這些是頁面所述 session 操作語意，實際轉換與計算未在本機驗證。

來源：[Using PyFluent sessions（頁面內嵌版本 0.40.3）](../ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/guide/1f24dea9506e-session.md#context-manager-for-active-sessions)（[來源清冊](sources.csv#ansys_a79a80046f30ff1aec049a1c)）。

### 2. Meshing workflow 選擇、客製與保存

PyFluent 提供可由 tasks 組成、執行及重用的 meshing workflow。文件區分 Watertight Geometry、Fault-tolerant 與 2D workflows，也允許自訂、插入或複製 task，並保存／載入 workflow。

- **Watertight Geometry**：文件建議用於封閉且幾何較乾淨、CAD 清理需求較少的模型。範例依序匯入幾何、設定局部尺寸、生成表面網格、描述幾何、更新邊界／區域、建立 boundary layers，最後生成 volume mesh。
- **Fault-tolerant**：文件建議用於需要處理重疊、交叉、孔洞或重複面等較複雜 CAD 幾何的案例。
- **流程值不是通用建議值**：範例使用特定模型與單位（例如匯入示例把 `length_unit` 設為 `in`），不能直接套用到其他幾何或單位系統。

完成三維網格後，官方兩個 workflow 範例都可呼叫 `meshing_session.switch_to_solver()` 切換到 solver mode；2D workflow 文件則明確指出不允許切換至 solver。範例中的單位、尺寸與網格參數都是特定幾何的設定，不可直接套用到其他模型。

**客製與重用 workflow**

- `create_workflow()` 建立自訂 workflow；預建 workflow 也能插入及複製 task、刪除 task、重新命名 task，以及用 `children()`／導覽方法檢查目前順序。重複 task 可用數字後綴或索引存取；不帶索引等同第一個 instance。
- task 的 arguments 更新後，文件提供 `mark_as_updated()` 明確標示變更；`current_workflow` 在尚未初始化任何 workflow 時回傳 `None`，使用前先檢查。
- `save_workflow(file_path=...)` 可保存為 `.wft`，之後用 `load_workflow(file_path=...)` 載入既存 workflow，供後續 session 重用。

上述整理涵蓋官方頁列出的 workflow 類型、模式限制、task 管理和保存／載入入口，不涵蓋所有 task 的參數簽名。執行網格後仍須依模型檢查 mesh quality、boundary names 和 units。

來源：[Meshing workflows（快取路徑 0.42.1；頁面內嵌版本 0.40.3）](../ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/guide/4d77c432c9d2-new_meshing_workflows.md)（官方網址為 `version/stable`，來源 release 維持 `unknown`）。

### 3. Solver settings 與 exposure levels

Solver settings objects 提供讀寫設定與執行 commands 的介面。頁面內嵌版本 0.40.3 的文件同時說明 constructor-style 物件，例如 `VelocityInlet(settings_source=solver_session, name="inlet-1")`，以及傳統 `solver_session.settings.file/setup/solution/results` 階層存取；新語法是附加選項，傳統階層仍受支援。

Settings objects、commands、queries 及其 arguments 各有 `stable`、`beta` 或 `alpha` exposure level。預設只公開 stable；設定在當前 session 的 settings root 呼叫，作用只限該 session，新 session 預設回到 stable。

| 呼叫值 | 可見項目 |
|---|---|
| `ExposureLevel.STABLE` | stable |
| `ExposureLevel.BETA` | stable、beta |
| `ExposureLevel.ALPHA` | stable、beta、alpha |

```python
from ansys.fluent.core import ExposureLevel
solver_session.settings.set_exposure_level(ExposureLevel.BETA)
```

`set_exposure_level()` 只在 settings root 提供；在子節點呼叫會出現 `AttributeError`。若尚未開啟所需 exposure 就存取隱藏物件，也會出現 `AttributeError`。直接建立設定物件可用 `VelocityInlet(settings_source=solver_session, name="inlet-1")`；既有 `solver_session.settings.file/setup/solution/results` 階層仍受支援。這些 API 屬該頁所示版本；使用前應核對目標 SDK 與 Fluent session 實際公開項目。

來源：[Solver settings objects（HTML 內嵌版本 0.40.3；來源清冊／快取路徑 metadata 0.42.1）](../ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/guide/37b3dc535387-solver_settings_contents.md)；[Using PyFluent sessions（HTML 內嵌版本 0.40.3；來源清冊／快取路徑 metadata 0.42.1）](../ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/guide/1f24dea9506e-session.md)。官方 URL 使用 `version/stable`，未據此推定其他 SDK 版本行為。

### 4. Field Data 與 Solution Variable Data 的選擇

PyFluent 提供兩種用途不同的欄位資料 API：

| 需求 | `field_data` | `solution_variable_data` |
|---|---|---|
| 資料組織 | 以 surface 為主 | 以 zone 為主（cell／face zones） |
| 常見內容 | scalar/vector fields、mesh geometry/connectivity、pathlines、部分 derived fields | Fluent 內部 solution variable arrays（SVARs）及其 metadata |
| 存取 | read-only | 支援 read/write |
| 適合情境 | 後處理、視覺化、網格／surface 資料擷取 | 直接讀寫 solver arrays、zone-specific automation |
| 限制 | 不涵蓋所有 solver variables；部分欄位是 derived/post-processed | 不提供一般 mesh geometry 或 derived fields，需了解 SVAR 命名方式 |

選用時先確認問題是要「surface 上可供後處理的 field」，還是「zone 上 Fluent 的內部 SVAR」。兩個 API 的資料對象與讀寫能力不同，不要只因欄位名稱相似就互換。

來源：[Choosing between field data and solution variable data APIs（頁面內嵌版本 0.40.3；快取路徑 0.42.1）](../ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/guide/d219d88e50dc-field_vs_svars_data.md)；[Solution variable data（頁面內嵌版本 0.43.0；快取路徑 0.42.1）](../ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/guide/a4610d3d49f9-solution_data.md)。

### 5. Solution variable metadata 與資料讀取

`solver_session.fields.solution_variable_info` 提供 zone 與變數 metadata；文件示例使用 `get_zones_info()` 和 `get_variables_info()`，列出 zone 名稱、數量、ID、類型及可用變數。`solver_session.fields.solution_variable_data` 則用於存取實際陣列。

文件中的示例先讀取 case/data，再查 zone 與變數資訊；這個順序很重要，因為沒有載入結果時，對應的 solution variable objects 可能尚未具備所需資料。讀寫數值前要確認 zone、variable 名稱與陣列長度；SDK 範例不構成特定 case 的物理解讀或數值驗證。

來源：[Solution variable data（頁面內嵌版本 0.43.0；快取路徑 0.42.1）](../ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/guide/a4610d3d49f9-solution_data.md)；[Choosing between field data and solution variable data APIs（頁面內嵌版本 0.40.3；快取路徑 0.42.1）](../ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/guide/d219d88e50dc-field_vs_svars_data.md)。

#### PyFluent solution variable zone metadata、讀取與寫入

PyFluent 頁面內嵌版本 0.43.0 的 `solution_variable_data` 指南展示以 zone 為單位操作 Fluent 內部 solution variable arrays（SVARs），並透過 `solution_variable_info` 查詢 zone／變數 metadata。它與 surface-centric、read-only 的 `field_data` API 用途不同；SVAR API 支援讀取及寫入，但不提供一般 mesh geometry 或 derived fields。

| 步驟 | 文件中的 API | 結果與查核點 |
|---|---|---|
| 讓結果物件可用 | 啟動 `Solver.from_install()`，讀取 case/data 後，從 `solver_session.fields` 取得 `solution_variable_info` 與 `solution_variable_data`。 | 範例載入 mixing elbow case/data；沒有 case/data 或合適 session 時，不應假設已具備可讀的解變數。 |
| 查 zone | `get_zones_info()` 後以名稱選取 zone metadata。 | 文件輸出 `name`、`count`、`zone_id`、`zone_type`；示例 zone ID 與 cell/face 類型屬該 case。 |
| 查變數 | `get_variables_info(zone_names=[...], domain_name="mixture")`。 | 可讀取可用 SVAR 名稱、維度及 field dtype；例如該案例列出的 `SV_P`／`SV_T` 與三維 `SV_CENTROID`。變數清單依 domain／zone 而定。 |
| 讀取陣列 | `get_data(variable_name=VariableCatalog.PRESSURE, zone_names=[...], domain_name="mixture")`。 | 回傳物件包含 domain 與 zone names；以 zone name 取得 NumPy-compatible array，可檢視 `size`／`dtype`。來源示例請求順序為 `elbow-fluid, wall-elbow`，回傳 `zone_names` 卻是 `wall-elbow, elbow-fluid`，所以應用 zone name 對應資料，不要假設陣列位置沿用輸入順序。 |
| 寫回陣列 | `create_empty_array(...)` 建立指定 variable／zone／domain 的陣列，再將 `{zone_name: array}` 傳給 `set_data(...)`。 | 這會修改 Fluent 內部 solution-variable data。來源把 500、600 寫入 pressure array 只是 API 展示值，不是壓力邊界條件或物理建議；寫入前須核對 variable、zone、domain 與陣列長度。 |

這是 API 使用示例，不等於結果正確性驗證。來源 URL 使用 PyFluent `version/stable`；頁面內嵌版本為 0.43.0，來源清冊 SDK 欄位／快取路徑為 0.42.1；沒有在 Fluent session 執行讀取或寫入。

來源：[Solution variable data（頁面內嵌版本 0.43.0；快取路徑 0.42.1）](../ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/guide/a4610d3d49f9-solution_data.md)（[來源清冊](sources.csv#ansys_3661e269d051b80237ab65dd)）；[Choosing between field data and solution variable data APIs](../ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/guide/d219d88e50dc-field_vs_svars_data.md)（[來源清冊](sources.csv#ansys_95b4643d3eafc6a738dcdede)）。

## 版本與來源限制

- 本頁依據的來源清冊 SDK 欄位／快取路徑為 `ansys-fluent-core` 0.42.1，但已核讀 HTML 的內嵌文件版本為 0.40.3 或 0.43.0；版本須按每頁來源標記判讀，產品 release 未由這批 SDK 文件確定。
- 文件網站的 `version/stable` 是動態入口；本機快取目錄及來源清冊欄位和 HTML 內嵌版本有差異，應以逐頁內嵌版本為頁面標記，不能把快取路徑視為頁面版本。
- 本頁尚未整理 Fluent 使用者手冊、各求解模型物理選項、離散格式、收斂判斷或產品版本差異；不能用這份 PyFluent 字典取代求解器方法文件。
- 程式範例未在實際 Fluent session 執行，未驗證網格品質或求解結果。


### 6. 官方 PyFluent 範例：DOE／ML、PEM 電解與凝固

這三篇是可用來理解「PyFluent 如何串接求解設定」的示例，案例數值與模型假設均屬範例輸入，不是可直接套用的設計值，也未在本工作中實際執行驗證。

- **DOE 與監督式回歸**：Mixing Elbow 案例將冷、熱入口速度作為兩個輸入，以出口質量加權平均溫度作為輸出；範例逐組設定速度、初始化並迭代 200 次，接著產生 response surface，並以訓練／測試切分與交叉驗證訓練回歸模型。速度陣列、迭代數、模型種類及資料切分皆是該示例設定。使用者需另檢查 DOE 覆蓋範圍、每組求解收斂與資料洩漏，再解讀代理模型。
- **PEM 電解**：示例建立 3D 陽極／膜／陰極域，啟用電化學與電位模型，使用 Butler–Volmer 反應、VOF 氣液兩相及多孔介質；電位邊界示例約 1.730202 V，陽極液態水入口 333.15 K、質量流率 0.000404 kg/s。催化層／多孔層孔隙率、滲透率、接觸角與雙電導率等皆是示例參數，須依材料、幾何與校準資料設定。
- **凝固／Czochralski 晶體成長**：示例採 2D 軸對稱旋流、重力及 Solidification and Melting，先求穩態導熱場，再啟用瞬態流熱耦合；藉自訂場函數與 patch 指定拉速及旋轉速度相關場，並以液相率檢查相變。案例示例拉速 0.001 m/s、旋轉角速度 1 rad/s、固相線／液相線 1150 K、Marangoni 表面張力溫度梯度 −0.00036 N/(m·K)。這些數值描述範例模型，不能替代材料與邊界條件驗證。

來源：[DOE and ML example](../ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/tutorial/244968a51382-DOE_ML.md)（清冊 `ansys_0f87d0d77ed5e72829b935ad`）；[Electrolysis Modeling](../ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/tutorial/9ce843852829-Electrolysis_Modeling_workflow.md)（`ansys_47d8f212ac2751d32075a577`）；[Modeling Solidification](../ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/tutorial/d173876d82fb-Modeling_solidification_workflow.md)（`ansys_5f7222bde5203ac7bd0ebd30`）。三頁網站均以 `version/stable` 發佈，HTML 內嵌 PyFluent 版本為 0.40.3，快取目錄／清冊 SDK 欄位為 0.42.1；其引用的 Fluent v252 方法文件連結為登入受限頁，未取其內容或確認分享權限。

## 本輪來源與轉換核查

八份 tutorial `.py`／`.ipynb` 附件另製成可搜尋文字補件；Notebook 僅擷取 Markdown／code cell source，不包含 output、圖片或附件。原始附件仍保留，連結及雜湊見 [附件文字補件清冊](../maintenance/knowledge_dictionary_passes/2026-11-03/fluent_attachment_text_recovery.csv)；未執行任何程式或求解。

- 2026-11-03 的本機清冊有 1,693 筆 Fluent 記錄：1,666 筆 API reference HTML、12 筆 guide HTML、4 筆 tutorial HTML、5 筆 Jupyter Notebook、3 筆 Python 範例、3 筆 Markdown（2 教學及 1 索引）。11 月 3 日清冊有 11 筆未填 `text_path`。11 月 4 日稽核對這些記錄使用原件路徑，包括 8 份附件、2 份正文 Markdown 與 1 份模板。兩份正文 Markdown 有索引，附件與模板則沒有直接收錄。逐筆狀態、網址與路徑見 [Fluent 來源狀態清冊](../maintenance/knowledge_dictionary_passes/2026-11-03/fluent_sources.csv)。此為檔案完整性核對，不代表 1,693 項皆已逐頁語意審閱。
- Fluent 來源目錄目前沒有 PDF。未發現 Fluent 產品使用手冊／Theory Guide PDF 或其 PDF 轉換成果；此資料集主要是 `ansys-fluent-core` 的 PyFluent API／user guide，不能代表完整 Fluent 求解器知識。清冊中 `release` 全為 `unknown`，SDK 欄位及路徑標示 0.42.1。1,682 份本機 HTML 的 `docsearch:version` 標記分別為 0.43.0（1,637 份）與 0.40.3（45 份）。
- 已逐段核讀並用於本頁摘要的主要 sidecar 包含 session、launch、solver settings、meshing workflows、fields／solution variables 及上述三個範例；其餘 API reference 雖已轉出 Markdown，未逐項審閱。導航／索引頁不可當成章節正文：例如 `meshing_contents.md` 僅有一段導言（422 字元），`fields_contents.md` 在句中截斷（1,253 字元），`offline_contents.md` 僅 243 字元；應標為導覽頁或轉換不足，需沿章節連結另取正文。
- 官方網址多為 `version/stable` 動態網址；清冊中的來源 URL 與快取副本可回查，但無法僅由網址確定當時版本。此輪未擴展爬取網站其他章節，亦未取得受登入保護的 Fluent v252 方法文件；文件可用性不代表原文／衍生內容可對外分享，分享權利仍須按來源條款確認。
- 尚待整理：Fluent Solver User's Guide、Theory Guide、各物理模型及數值方法、求解控制與收斂判準、版本差異、圖表／掃描頁語意檢查。不得把本頁標成 Fluent 全產品字典完成。



## 2026-11-04：Wave 7 本機來源盤點與限制說明

本機稽核記錄 1,693 筆來源及其雜湊，其中 1,684 筆有正文、8 筆為附件、1 筆為模板。另有 5,412 個網址只列入盤點，本批未擷取。1,666 筆 PyFluent API reference 尚待逐篇核對。主題清冊有 12 項限範圍完成、1 項待來源核對、1 項來源受限。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/fluent_module_conversion_report_20261104.md)。
