# DPF 主題字典

本頁分別整理 Ansys DPF v261 使用文件與 PyDPF-Core SDK 0.16.3 文件。DPF 是處理離散模擬結果的資料框架；SDK 版本不等於 Ansys 產品版本，本文不將兩者合併推定。

## 主題導覽

### 1. DPF 的資料模型與適用範圍

DPF（Data Processing Framework）以網格上的數值結果為核心：`Field` 保存特定位置（如 `Nodal`、`Elemental` 或 `ElementalNodal`）的數值，資料可沿時間或頻率變化。`Mesh`、`Scoping` 與時間／頻率支援資訊描述結果所依附的網格、實體子集及分析集合。DPF 的運算以這種資料結構為依據，不要求每個通用運算都理解物理量意義。

| 名詞 | 用途 | 讀取時需對照 |
|---|---|---|
| `Field` | 儲存結果值及其 metadata；operator output 可為單一 `Field` 或 `FieldsContainer`。 | `unit`、component 數、資料 shape、`location`、support 與 scoping。 |
| `location` | 指明每筆值的位置型態；文件以 `Nodal`、`Elemental`、`ElementalNodal` 為例。 | `Nodal` 為每 node 一筆；`Elemental` 為每 element 一筆；`ElementalNodal` 為每 element 的每 node 一筆，資料列數可能不同於 scoping ID 數。 |
| `Scoping` | 列出 Field 所涵蓋 support entities 的 IDs，並決定 entity data 的排列對應。 | 對照 `field.scoping.ids`；陣列 row index 是 scoping 順序位置，不是 mesh ID。 |
| `FieldsContainer` | 按 labels 分組並持有多個 `Field`，例如各 time set 或 time／element-shape 組合。 | 以 labels 或 time set ID 取 field；Python list index 是另一種零起始索引，不能與 time ID 混用。 |
| `Model` | 開啟結果檔並提供 result helpers、mesh、analysis 與 time/frequency metadata。 | 可用 result helpers 依檔案內容而異；先檢查 Model metadata 與 server 可讀路徑。 |

官方 v261 導覽列出 Mechanical APDL、Fluent、LS-DYNA 等結果，以及 VTK/VTU、HDF5、CSV 等格式；另指出 DPF 可透過 reader plugin 擴充。純 CAD 幾何（例如 IGES、STEP）不是此結果資料模型的處理對象。實際可讀格式仍應依安裝版本與 reader 支援清單確認。

此處的產品範圍依 Ansys DPF v261 概覽；結構語意例子依本機 PyDPF-Core 0.16.3 頁面整理，並不表示 SDK 0.16.3 就是 DPF v261 的相依版本。v261 概覽列出常見來源及開放格式範例，不是完整 reader／版本支援矩陣。純幾何不是該頁描述的 DPF 資料模型。

來源：[What is DPF（v261）](../ANSYS_Document/DPF/v261/guide/5d2afe40e9f7-what-is-dpf.md)（[來源清冊](sources.csv#ansys_eaf115f5c2bbe89000f253f1)）；[PyDPF-Core：Fields containers and fields（本機 SDK metadata 0.16.3；頁面 release unknown）](../ANSYS_Document/DPF/sdk/ansys-dpf-core/0.16.3/guide/0c9e4bebe48a-fields_container.md)（[來源清冊](sources.csv#ansys_a651dc9eb40b833a1bff65be)）；[DPF model（本機 SDK metadata 0.16.3；頁面 release unknown）](../ANSYS_Document/DPF/sdk/ansys-dpf-core/0.16.3/guide/46622770a3af-model.md)（[來源清冊](sources.csv#ansys_d3a4dc858e42fbe5087838db)）。

### 2. Server、client 與使用方式

DPF 的計算能力由 DPF Server 與其載入的 operator libraries 提供；client API 連線至 server，送入資料與運算流程並取回結果。官方 v261 文件描述同程序及 gRPC 等連線方式，也列出 CPython、IronPython、C++ 等 client 類型。Mechanical 內建環境的 IronPython API 與 PyDPF-Core CPython API 語法不同，程式範例不能直接互換。

**選用前確認**

- 先確認 DPF Server 的部署位置、可用 operator libraries 與連線方式。
- 確認 client 語言、server 版本及產品整合環境；本文未驗證跨版本相容矩陣。
- 遠端 server 情境要確認結果檔路徑由哪一端解析；PyDPF-Core 文件允許使用絕對路徑或相對於 DPF server 的路徑。

來源：[Ways of Using DPF（v261）](../ANSYS_Document/DPF/v261/guide/16e22cf3e7be-ways-of-using.md)；[DPF model（PyDPF-Core SDK 0.16.3）](../ANSYS_Document/DPF/sdk/ansys-dpf-core/0.16.3/guide/46622770a3af-model.md)。

#### v261 DPF Server application、client API 與部署分工

Ansys DPF v261 將提供計算能力的程序稱為 **DPF Server application**：由 `DataProcessingCore`／`DPFClientAPI` kernel 載入 operator libraries；可用的 operators 取決於 server 啟動時載入的 libraries，與 client 使用 CPython、IronPython 或 C++ API 無直接關係。server 可由 Ansys 產品提供，也可由 DPF Server package 提供。

官方列出同程序通訊與 gRPC 通訊兩種 client/server 方式；gRPC 可讓兩端位於不同電腦。選擇 API 前，先決定在 Mechanical 內使用或以 standalone 方式執行：Mechanical 內的 DPF 經 ACT console 使用 IronPython，適合在應用程式內做自訂後處理與視覺化；standalone 可由 CPython、C++ 等 API 存取。IronPython 與 CPython 的 API 語法不同，不能直接互換。

使用 PyDPF-Core `Model` 載入結果時，傳入路徑可為絕對路徑，或相對於 DPF server 的路徑。遠端情境下，檔案必須能由 server 端依該路徑讀取；client 本機檔案路徑不代表 server 可見。實際 operator library、server 版本、授權與產品整合能力仍須依安裝環境核對，本段不構成跨版本相容保證。

來源：[Ways of Using DPF（Ansys DPF v261；頁面標示 Last update 25.03.2026）](../ANSYS_Document/DPF/v261/guide/16e22cf3e7be-ways-of-using.md)（[來源清冊](sources.csv#ansys_9f58489e0c3241493d0d41b1)）；[DPF model（PyDPF-Core SDK metadata 0.16.3；release unknown）](../ANSYS_Document/DPF/sdk/ansys-dpf-core/0.16.3/guide/46622770a3af-model.md)（[來源清冊](sources.csv#ansys_d3a4dc858e42fbe5087838db)）。


### 3. 載入結果與檢查 Model

`Model` 是探索結果檔的入口，通常由結果檔或 `DataSources` 建立。Model 可提供結果、網格中繼資料及時間／頻率資訊。Mechanical v261 範例先從目前 analysis 取得 `ResultFileName`，再建立 `DataSources` 與 `dpf.Model`；範例在 Mechanical scripting window 中先呼叫 `mech_dpf.setExtAPI(ExtAPI)` 設定 Mechanical context。

**基本檢查順序**

1. 確認結果檔存在且由目前分析產生，並確認檔案對執行 DPF 的 server 可讀。
2. 建立 `DataSources`／`Model` 後先列印或檢查 Model metadata。
3. 檢查網格節點數、元素數及 `TimeFreqSupport`，確認結果集合符合預期，再讀取場資料。

Mechanical 範例展示取得節點、元素數及時間點；數量為模型特定值，不能當成通用預期值。若使用 Python Result，需依文件提供的 workflow callback 方式整合，不要把 scripting window 範例原樣視為 Python Result 的完整設定。

來源：[Understanding DPF in Ansys Mechanical（v261）](../ANSYS_Document/DPF/v261/guide/1df9aee95ce2-core-concepts.md)；[Load and inspect results in Mechanical（v261）](../ANSYS_Document/DPF/v261/guide/b173392cd987-basic-load.md)；[DPF model（PyDPF-Core SDK 0.16.3）](../ANSYS_Document/DPF/sdk/ansys-dpf-core/0.16.3/guide/46622770a3af-model.md)。

#### Mechanical v261 與 PyDPF-Core 的 Model 載入及 metadata 檢查

Mechanical v261 的 `Load and inspect results` 範例限定在 Mechanical scripting window：先以 `mech_dpf.setExtAPI(ExtAPI)` 設定 Mechanical context，再從指定 analysis 取得 `ResultFileName`，將結果檔路徑設到 `dpf.DataSources()`，最後建立 `dpf.Model`。`Model` 提供 mesh、results 與時間／頻率等 metadata；範例檢查 nodes、elements、time/frequency set 數量，並列印 time values。 範例以 `Analyses[0]` 選取 analysis；若專案含多個 analyses，需自行選對目標分析，不應把索引 0 當通用選擇規則。

```python
import mech_dpf
import Ans.DataProcessing as dpf

mech_dpf.setExtAPI(ExtAPI)
analysis = ExtAPI.DataModel.Project.Model.Analyses[0]
data_sources = dpf.DataSources()
data_sources.SetResultFilePath(analysis.ResultFileName)
dpf_model = dpf.Model(data_sources)

mesh = dpf_model.Mesh
time_freq_support = dpf_model.TimeFreqSupport
```

若把流程放進 Python Result，v261 範例改用 `define_dpf_workflow(analysis)` callback，仍先設定 `mech_dpf` context；範例讀取 mesh 與 time set 數量後寫入 `this.Text`。這個 callback 例子用來顯示檢查結果，不代表完整 Python Result UI、operator workflow 或求解設定。

PyDPF-Core SDK metadata 0.16.3 的 standalone 範例則以 `from ansys.dpf import core as dpf` 建立 `dpf.Model(path)`。路徑須為絕對路徑，或相對於 DPF Server 的路徑；遠端執行時要確認檔案可由 server 端讀取。可先 `print(model)` 檢視 analysis type、unit system、可用 results、mesh 與 time/frequency support，再以 `model.metadata.result_info.analysis_type`、`model.metadata.meshed_region.nodes.n_nodes`、`model.metadata.meshed_region.elements.n_elements` 或 `model.metadata.time_freq_support.time_frequencies.data` 查欄位。`model.results` 會依結果檔型態動態列出可用結果，不能假設每個檔案都有相同的 result helpers。

Mechanical v261 範例使用 IronPython／.NET API 的 PascalCase 屬性（如 `Mesh.Nodes.Count`、`TimeFreqSupport.TimeFrequencies`）；PyDPF-Core 使用 CPython API 的 snake_case metadata 屬性。兩者都從 `Model` 檢查結果，但 import、物件層級和欄位大小寫不可直接互換。教學輸出的 nodes/elements/time sets 是範例檔數值，不是預期值或模型驗收門檻。此子題只整理結果載入和 metadata 檢查；未載入結果檔、執行 Mechanical／DPF、評估 operator 或驗證求解結果。

來源：[Understanding DPF in Ansys Mechanical（v261）](../ANSYS_Document/DPF/v261/guide/1df9aee95ce2-core-concepts.md)（`ansys_6c82352acbeefbcf3245b85b`）；[Load and inspect results in Mechanical（v261）](../ANSYS_Document/DPF/v261/guide/b173392cd987-basic-load.md)（`ansys_5a4458b3ebbb6bc3338662db`）；[DPF model（PyDPF-Core SDK metadata 0.16.3，release unknown）](../ANSYS_Document/DPF/sdk/ansys-dpf-core/0.16.3/guide/46622770a3af-model.md)（`ansys_d3a4dc858e42fbe5087838db`）。

### 4. Field、FieldsContainer 與 Scoping

`Field` 保存一組關聯到 mesh support 的數值資料；其 `location` 說明數值位於節點、元素或元素節點等位置，`scoping` 指出資料對應的 entity IDs 與順序。`FieldsContainer` 是按標籤（labels）組織的一組 fields，常用於時間步、頻率或其他分組結果。讀取資料時應同時檢查 location、scoping、shape 與標籤，避免把資料列索引誤當成節點或元素 ID。

PyDPF-Core 0.16.3 範例顯示 `FieldsContainer` 可含多個時間點的 field；不同 location 與 shell layer 等資料形態會改變每個 entity 對應的值數量。要取子集可透過 mesh scoping 或時間／頻率 scoping 限定範圍。使用者必須依實際 field 的 location 與資料 shape 解讀數值，不能由欄位長度單獨推斷物理意義。

來源：[Fields containers and fields（PyDPF-Core SDK 0.16.3）](../ANSYS_Document/DPF/sdk/ansys-dpf-core/0.16.3/guide/0c9e4bebe48a-fields_container.md)；[DPF model：選擇 mesh/time scoping（SDK 0.16.3）](../ANSYS_Document/DPF/sdk/ansys-dpf-core/0.16.3/guide/46622770a3af-model.md)。

#### Mechanical v261 以 Scoping 限定 mesh entities 與 time/frequency sets

Mechanical v261 的 `Scoping and support` 將 scoping 定義為帶有 location 的 entity ID 清單；它告訴 operator 要處理哪個子集。Mesh scoping 可用 `dpf.Scoping()` 指定 `Location` 與 `Ids`，也可用 `MeshScopingFactory.NodalScoping(...)`、`ElementalScoping(...)` 建立。查 named selection 時，文件示範先以 `mech_dpf.setExtAPI(ExtAPI)` 設定 Mechanical context，然後用 `MeshScopingFactory.NamedSelectionScoping("MY_SELECTION", model)` 或 `operators.scoping.on_named_selection()`；名稱須大寫。operator 版本可直接接到結果 operator 的 `mesh_scoping` input。

Time/frequency scoping 的集合 ID 是跨 load steps 累計的 **1-based set indices**。文件建議用 `TimeFreqScopingFactory.ScopingByLoadStep`、`ScopingByLoadSteps`、`ScopingBySet`、`ScopingBySets`、`ScopingByStepAndSubstep` 或 `ScopingOnAllTimeFreqs` 建立；簡單情形亦可用 `dpf.Scoping()` 並設 `Location='TimeFreq_sets'`。`TimeFreqSupport` 提供整個分析的時間／頻率集合，並可用於將 load step/substep 轉換為累計 set index。不要將 set ID 與 Python 清單的零起始位置互換；若按 step/substep 選取，應依目標 `Model.TimeFreqSupport` 取得正確集合。

`Working with meshes` 頁的實際範例僅展示讀取 `mesh.Nodes.Count` 和 `mesh.Elements.Count`，並未在該頁示範 connectivity 或 mesh 編輯；需要這些操作時應再查相應 API/operator 文件。上述是文件操作說明，未在 Mechanical 中執行，也未用實際 named selection 或多 load-step 結果驗證。

來源：[Scoping and support（Ansys DPF Mechanical v261；Last update 18.06.2026）](../ANSYS_Document/DPF/v261/guide/47c4b4d24b21-scoping-support.md)（`ansys_12f48c396e9c1dcbbb0a512d`，原文「Mesh scoping」「Named selection scoping」「Time scoping」「TimeFreqSupport」）；[Working with meshes（v261；Last update 18.06.2026）](../ANSYS_Document/DPF/v261/guide/12b8fbd4de7f-working-with-meshes.md)（`ansys_8c3d6f6cee167210939adf2d`，原文「Mechanical example」）。

### 5. Operators 與資料流程

Operator 是 DPF 的資料讀取、轉換、計算或輸出單元。將前一個 operator 的 output 接至下一個 operator 的 input，可組成 workflow。PyDPF-Core 文件說明 operators 採 lazy evaluation：建立連線本身不代表結果已計算；在要求 output／evaluate 時才觸發計算。

**建構時逐項確認**

- Reader operator 的 `DataSources` 是否指向正確結果檔。
- `mesh_scoping`、`time_scoping` 與 field location 是否符合所需子集。
- operator 輸入輸出型別及連線是否相容，並在 evaluate 後檢查輸出 field 的標籤、shape、location。
- 匯出至檔案時確認 server 與 client 的檔案位置；遠端情境可能需從 server 下載輸出檔。

官方示例以位移結果串接向量 norm 與 `min_max` 計算最大正規化位移。這是流程示例，不等同於任何特定模型的驗證結果。

來源：[Operators（PyDPF-Core SDK 0.16.3）](../ANSYS_Document/DPF/sdk/ansys-dpf-core/0.16.3/guide/45d9fef7c2c8-operators.md)；[Ways of Using DPF（v261）](../ANSYS_Document/DPF/v261/guide/16e22cf3e7be-ways-of-using.md)。

#### PyDPF-Core Operator 輸入、連接與評估

建立 operator 後先檢視其輸入／輸出簽名（官方範例以 `print(op)` 列出 pin、型別和必填狀態），再設定必要輸入。例如 displacement operator 需要 `data_sources`；可用 `DataSources` 指定結果檔，並視需求提供 `mesh_scoping`、`time_scoping`。要求 `outputs.fields_container()` 時才會觸發計算；若必要輸入未設定，server 會回報 `DPFServerException`，範例訊息為 `U<-Data sources are not defined.`。

多個運算可串接以延遲執行：前一個 operator 的 output 連至下一個的 input，只有最後請求的 output 需要計算時才評估整條 workflow。對大型結果，將 `displacement` 接到 `min_max` 並只取 `field_max()`，可以避免把完整位移陣列傳到 Python；需要完整 field 資料時才讀取 `.data`。官方文件將在 Python 端用 NumPy 計算定位為小型資料集可接受的做法。個別 operator 可能有自己的 license checkout 要求，須另查該 operator 的授權設定。

上述內容是 operator 通用連接及求值流程，不保證不同 operator 的輸入名稱、型別、必要性或 license 相同；使用前應檢視實際 operator descriptor。此官方頁網址使用 `version/stable`，本機來源清冊 SDK metadata 記錄為 0.16.3，但頁面本身未提供精確 release 標記。

來源：[Operators，PyDPF-Core `version/stable` 使用指南](https://dpf.docs.pyansys.com/version/stable/user_guide/operators.html)／[本機逐頁 sidecar](../ANSYS_Document/DPF/sdk/ansys-dpf-core/0.16.3/guide/45d9fef7c2c8-operators.md)（[來源清冊](sources.csv#ansys_bd5ad5d1ea0c402d09afbbfb)）。

#### PyDPF FieldsContainer 以 time／elshape labels 選取 Field

PyDPF-Core 的官方 FieldsContainer 教學展示，對跨時間且含多種 element shape 的 elastic strain 結果，可在結果 helper 後加上 `split_by_shape`，再對回傳的 `FieldsContainer` 使用 `get_field()` 同時指定 labels：

```python
model = dpf.Model(examples.download_all_kinds_of_complexity())
fields = model.results.elastic_strain.on_all_time_freqs.split_by_shape.eval()
field = fields.get_field({'time': 1, 'elshape': 0})
```

同一頁也示範以 `{'time': 1, 'elshape': 1}` 取另一個 field。範例列印結果中，`elshape:0` field 有 203 entities、6 components、2436 elementary data；`elshape:1` field 有 9052 entities、6 components、37580 elementary data。這些數量是示例結果，不可當成其他檔案的預期值。

這個取法表示查詢同時以 `time` 和 `elshape` label 限定 Field；它不是用結果陣列的 row index 代替 label。該頁沒有說明 `elshape` 的整數值如何對應具名元素形狀，也沒有提供通用的 shape ID 對照表；遇到實際模型時，應先檢查 `FieldsContainer` 標籤／輸出，再解讀各 shape field 的 entity 範圍。`split_by_shape` 只整理結果分組，不能據此推定元素或網格品質。

來源：[Fields containers and fields，PyDPF-Core 官方 `version/stable` 指南](../ANSYS_Document/DPF/sdk/ansys-dpf-core/0.16.3/guide/0c9e4bebe48a-fields_container.md)（[來源清冊](sources.csv#ansys_a651dc9eb40b833a1bff65be)；本機路徑 metadata 為 SDK 0.16.3，來源 release 維持 unknown）。

#### PyDPF Field 資料索引與 shape 解讀

`Field` 是含資料與支援中繼資料的單一結果場；`.data` 會將場資料取到 client 端作為 NumPy 相容陣列。每筆 entity data 的順序依 `field.scoping.ids` 排列，因此 Python row index 不等於 mesh node／element ID；少量實體可用 `get_entity_data_by_id(id)`，大量值應一次取 `.data`，避免逐項跨 DPF service 請求。`get_entity_data(index)` 則取 scoping 排序中的位置。

| 需求 | API／索引方式 | 解讀要點 |
|---|---|---|
| 取 FieldsContainer 第 n 個 field | `fields[n]` | 依 Python list 慣例零起始；例如 `fields[0]` 是第一個 field。 |
| 依 time set 取 field | `get_field_by_time_id(set_id)`、`get_field({'time': set_id})` 或 `get_fields(...)` | 文件所列 time-scoping set ID 從 1 起算；先看 `time_freq_support`，不要把 set ID 當成 list index。 |
| 依多個 labels 取 field | `get_field({'time': 1, 'elshape': 0})` | 先用 `split_by_shape` 產生 shape label，再依實際 labels 選取；來源未提供 `elshape` 整數到具名元素形狀的通用對照表。 |
| 依 support entity 取資料 | `get_entity_data(index)` 或 `get_entity_data_by_id(entity_id)` | `index` 是 `scoping.ids` 中的位置；entity ID 可能不連續，必要時以 `field.scoping.ids.index(entity_id)` 找出其 row index。 |

少量資料可用 `.data` 取得 client-side NumPy-compatible array；若只要 reduction，文件示範以 `field.max()` 在 DPF 端計算，再由結果的 `scoping.ids` 找出各 component 的最大值實體，避免先傳輸整個陣列。重複讀取多個 entity 時，文件示範用 `as_local_field()` 將資料留在本地 field context，再呼叫 `get_entity_data_by_id()`；逐筆呼叫 remote field 會增加 service 往返。這些是文件所示的取值策略，不是固定效能保證。

解讀長度時需分清三種數量：`len(field)` 是 scalar value 總數，`len(field.data)` 是第一軸 row 數，`field.elementary_data_count` 是 uniform field 的資料列數。多分量場每列還有 component 軸；例如六分量 tensor 時，shape `(12, 6)` 共 72 個 scalar。`ElementalNodal` 位置還可能因每個 element 的節點資料或 shell layers 產生比 scoping IDs 更多的 rows，所以不得把 `.data` row 直接映射成單一 element ID。

`FieldsContainer` 可依 time labels 持有多個 `Field`。文件範例中 `fields[0]` 是 Python 零起始的第一個 field，而 `get_field_by_time_id(1)` 或 `get_field({"time": 1})` 使用一開始為 1 的 time set ID；這兩種索引方式勿混用。要確認可用步階及時間值，可檢視 `fields.time_freq_support`。

來源：[Fields containers and fields，PyDPF-Core SDK metadata 0.16.3，完整涵蓋 Access fields within a fields container、Field metadata、Field data、length／shape 及 operate on field data 章節](../ANSYS_Document/DPF/sdk/ansys-dpf-core/0.16.3/guide/0c9e4bebe48a-fields_container.md)（[來源清冊](sources.csv#ansys_a651dc9eb40b833a1bff65be)）；[DPF model：結果 helper 與 mesh scoping](../ANSYS_Document/DPF/sdk/ansys-dpf-core/0.16.3/guide/46622770a3af-model.md)（[來源清冊](sources.csv#ansys_d3a4dc858e42fbe5087838db)）。SHELL281 corner-only 範例為每 element 四角節點、三層、shape `(12, 6)`；啟用 midside extension 的 Nodal 範例為 `(24, 6)`。這些數值僅解釋該資料形態，不是所有 solver/result 的固定維度；來源 URL 使用 `version/stable`，精確 SDK release 未由頁面標明。

#### PyDPF SHELL281 shell layer 選擇與 midside-node extension

PyDPF-Core 的 Fields containers and fields 範例說明，支援 `shell_layer` 輸入的 result operators 使用以下 selector：

| `shell_layer` | 來源定義 |
|---:|---|
| `0` | top |
| `1` | bottom |
| `2` | top and bottom |
| `3` | mid |
| `4` | top, bottom, and mid |

選 `topbottommid` 時，每個 entity/node 的資料順序是 **bottom、top、mid**。來源明確指出 `5` 不是 top-bottom-mid selector，不能用它代替 `4`。

同頁的 MAPDL `SHELL281` stress 範例為六分量資料、三個 shell layers。當 RST 只提供四個 corner nodes 的結果時，corner-only `ElementalNodal` field 的 shape 為 `(12, 6)`，共 72 個 scalar。請求 `Nodal` location 時，midside-node extension 預設啟用；每層八個 nodes，該例變成 24 rows、shape `(24, 6)`、144 個 scalar。選取單一 component 只改變 component 維度、不改變 entity/layer rows；例如 `X` component 的 shape 為 `(24,)`，此時 `len(field)` 為 24。

若 result operator 提供 `extend_to_mid_nodes` pin，可設為 `False` 以保留 corner-node-only 結果。文件亦說明 `dpf.operators.averaging.extend_to_mid_nodes` 和 `extend_to_mid_nodes_fc` 會依 corner values 計算 midside values；它們不會還原原始結果檔中不存在的 midside-node 值。上述 shape 與 selector 依本機 SDK 0.16.3 sidecar 範例整理；實際結果仍須檢查 operator 輸入、location、scoping 與輸出 shape，不推定所有 solver 或 result 都有相同資料形式。

來源：[Fields containers and fields，PyDPF-Core SDK metadata 0.16.3（官方網址為 `version/stable`，release unknown）](../ANSYS_Document/DPF/sdk/ansys-dpf-core/0.16.3/guide/0c9e4bebe48a-fields_container.md#interpreting-field-length-and-shape)（[來源清冊](sources.csv#ansys_a651dc9eb40b833a1bff65be)；原始 HTML 亦保留於同目錄）。本段只核對文件內容，未執行 DPF operator 或結果檔。

## 版本與來源限制

- v261 指 Ansys DPF 2026 R1 文件路徑中的產品文件版本；PyDPF-Core 0.16.3 是 SDK 文件版本，二者不是同一版本標記。
- 本頁只對照上述已取得文件；沒有完成其他 DPF server、reader、operator library 或舊版差異盤點。
- PyDPF-Core 網站使用 `version/stable` 網址，版本以本機文件目錄與索引 metadata 所記錄的 0.16.3 為準；若線上 stable 已更新，須重新取得並核對。
- 本文提供定位與讀者檢查方向，不取代產品版本文件、SDK API reference 或分析結果驗證。


### 6. Standalone DPF 安裝、授權與連線驗證（v261 onboarding）

DPF 使用 client-server 架構：PyDPF-Core 是 client，DPF Server 提供 operators 和資料處理能力。v261 onboarding 將獨立安裝流程拆為 Python、PyDPF-Core、DPF Server、授權設定及啟動驗證；已有 Ansys 安裝時，可由 PyDPF-Core 探測安裝內的 server，文件建議優先使用此方式。standalone server 可另行下載安裝，但文件明確指出它不是免授權工具，執行多數 operators 仍須有效 Ansys license increment。

| 設定 | 何時需要 | 文件列出的用途 |
|---|---|---|
| `ANSYS_DPF_ACCEPT_LA=Y` | standalone DPF Server | 接受 DPF Preview License Agreement；完整 Ansys 安裝的使用者，文件表示安裝時已涵蓋此步驟。 |
| `ANSYSLMD_LICENSE_FILE` | 沒有完整 Ansys 安裝、使用 standalone server | 指向 `.lic` 檔，或 `1055@<license-server>` 格式的 license server；1055 是文件列出的預設 FlexLM port。 |
| `ANSYS_GRPC_CERTIFICATES` | 需使用 mTLS 的 gRPC client/server | 指向憑證目錄；client 和 server 都須配置有效憑證。 |
| `DPF_DEFAULT_GRPC_MODE=insecure` | 文件列為本機開發替代方案 | client 和 server 兩端均設定後，回復未加密 gRPC；不適用於 production 安全連線。 |

授權環境變數依部署型態設定，不可把 `ANSYS_DPF_ACCEPT_LA` 誤當成 license source：接受 license agreement 與取得可用授權是兩件事。若使用完整 Ansys 安裝，v261 onboarding 表示沿用該安裝的 license configuration；若使用 standalone，則需自行提供有效授權來源。相容的 license increment 依組織授權而定，文件列出 `preppost`、`meba`、`mech_2` 作為例子，不保證任一組織皆有這些授權。

基本安裝檢查可先確認 `import ansys.dpf.core as dpf` 成功，再以 `dpf.start_local_server()` 啟動本機 server。onboarding 接著用 entry operator 測試授權；若走 gRPC，還須考慮 mTLS。v261 onboarding 說明 Ansys 2026 R1 起（以及 2025 R2、2025 R1、2024 R2 的部分 service pack）gRPC 預設要求 mutual TLS；其 `DPF_DEFAULT_GRPC_MODE=insecure` 範例會停用加密，只適合文件所稱的 local development 情境。`start_local_server()` 預設 InProcess 模式不受該 gRPC 錯誤影響。若錯誤訊息含 missing certificates，應先辨別連線是否為 gRPC，再核對兩端憑證設定及所用版本，而非直接降低連線安全性。

這些是 v261 onboarding 的安裝與除錯指引，不代表已在本機設定環境變數、確認授權、啟動 server 或驗證企業安全政策。頁面中「latest PyDPF-Core」對舊 Ansys 版本的相容性敘述需搭配其 compatibility 文件及實際 server 版本確認；本文不推定 SDK/server 相容矩陣。

來源：[Installing DPF（v261 onboarding）](../ANSYS_Document/DPF/v261/guides_and_tutorials/dpf-onboarding-2026-r1/setting-up-dpf/how-to-install-dpf.md)（`ansys_c942700435748012fc3850a3`）；[Configuring licensing（v261 onboarding）](../ANSYS_Document/DPF/v261/guides_and_tutorials/dpf-onboarding-2026-r1/setting-up-dpf/licensing.md)（`ansys_74478ffa14632453bd79455e`）；[Verifying your installation（v261 onboarding）](../ANSYS_Document/DPF/v261/guides_and_tutorials/dpf-onboarding-2026-r1/setting-up-dpf/check-your-installation.md)（`ansys_5429ea7395427301c3e598f2`）。


## PyDPF tutorial 附件文字補件

三組教學的 Notebook 與 Python 原始檔各一份，共六份。補件保留程式與 Notebook 的 Markdown／code cells，並連回原始附件及來源 ID；Notebook 執行輸出、圖片及其他附件未擷取，產品 release unknown，範例未執行。

- [00-basic_example.ipynb](ANSYS_Document/dpf_example_inputs_20261104/tutorial/ansys_d08ff29e54841c19569f8bce/dpf.md)（`sources.csv#ansys_d08ff29e54841c19569f8bce`）
- [00-basic_example.py](ANSYS_Document/dpf_example_inputs_20261104/tutorial/ansys_21fd8b768d30488f7c3c02ab/dpf.md)（`sources.csv#ansys_21fd8b768d30488f7c3c02ab`）
- [01-basic_operators.ipynb](ANSYS_Document/dpf_example_inputs_20261104/tutorial/ansys_d580d04a2594e453f2ff16b4/dpf.md)（`sources.csv#ansys_d580d04a2594e453f2ff16b4`）
- [01-basic_operators.py](ANSYS_Document/dpf_example_inputs_20261104/tutorial/ansys_acc4cf095a52af150e1faee8/dpf.md)（`sources.csv#ansys_acc4cf095a52af150e1faee8`）
- [02-basic_field_containers.ipynb](ANSYS_Document/dpf_example_inputs_20261104/tutorial/ansys_c0485369a46ab493b43cec61/dpf.md)（`sources.csv#ansys_c0485369a46ab493b43cec61`）
- [02-basic_field_containers.py](ANSYS_Document/dpf_example_inputs_20261104/tutorial/ansys_040fbbc68673c6942bcf0f90/dpf.md)（`sources.csv#ansys_040fbbc68673c6942bcf0f90`）

逐檔 SHA、cell 數及狀態見 [轉換清冊](../maintenance/knowledge_dictionary_passes/2026-11-04/dpf_attachment_text_recovery.csv)。


## 2026-11-04：Wave 4 本機來源盤點與限制說明

本批完成 dpf 模組既有本機 catalog 文件（共 3855 筆）與 sources 清冊（共 3855 筆）之完整雜湊、正文路徑與標籤結構核對。本機未快取或具備企業授權/登入限制之線上主題誠實標記為缺口（保持現有非 complete 狀態），未擅自虛構未核實之線上 API 簽名或執行求解運算。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/dpf_module_conversion_report_20261104.md)。
