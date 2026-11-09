# ANSYS 熱分析與熱結構耦合跨產品主題字典

`thermal` 在本文件庫是跨產品索引標籤。先辨識產品、analysis type、版本、材料、時間與來源資料，再選 API 或傳遞方式。本頁整理 Mechanical／System Coupling／Motor-CAD 的有界流程；[Icepak](icepak.md)、[Thermal Desktop](thermal_desktop.md)、[Mechanical](mechanical.md)、[System Coupling](system_coupling.md)、[Motor-CAD](motorcad.md) 各有專頁。

版本分開記錄：Mechanical、Fluent、System Coupling 官方頁為 **v261／Release 2026 R1**；Motor-CAD 的可讀官方 Thermal 頁為 **v252／Release 2025 R2**。本機 Motor-CAD 教學雖印有 **8 October 2025**，沒有產品 release 標記，仍為 **unknown**。內部[熱分析技能](../../agents/skills/thermal-cooling/ansys-thermal-analysis/SKILL.md)只是工作路由提示（[來源清冊](sources.csv#agents_skills_thermal-cooling_ansys-thermal-analysis_SKILL)）。

## 宿主識別與熱分析路由

| 工作目的 | 先查的來源／字典 | 本頁界線 |
| --- | --- | --- |
| 穩態或暫態溫度場 | Mechanical analysis type 文件 | 選定 solver target 後再看材料與邊界；不固定為某一舊單元家族。 |
| 將溫度載入結構模型 | Thermal-Stress／Imported Body Temperature | 支援 shared 與 unshared mesh 的不同流程。 |
| 參與者間交換熱資料 | System Coupling；Fluent／Mechanical 變數定義 | 交換量、方向與數值耦合方法依參與者設定。 |
| 電機的集總熱模型與 duty cycle | Motor-CAD Thermal | v252 lumped circuit 定義與 unknown-release 教學分開使用。 |

System Coupling Participant Library 的[v261 capabilities](../ANSYS_Document/System_Coupling/v261/guide/8191e91f9c7f-participant-library-capabilities.md)（[來源清冊](sources.csv#ansys_bf8fbeb9403ea4bde8b120ab)）還區分 steady／transient、implicit／explicit 與 mesh／point cloud；這些是耦合介面能力，不證明任一產品模型已被求解。

### 熱產品文件與轉換範圍

跨產品文件與轉換進度按各產品清冊追蹤。本次核對本頁實際引用的 Motor-CAD 教學與三份 System Coupling Markdown，並保留 PDF 讀序、表格、公式與圖像的品質缺口。Icepak 和 Thermal Desktop 的來源覆蓋見各自字典。

OpenTD 開發指南與 API 參考屬 Thermal Desktop 的獨立來源範圍。版本、逐來源核對與未驗收項目見 [Thermal Desktop 字典](thermal_desktop.md)。

## Mechanical 穩態與暫態熱分析

| 項目 | Steady-State Thermal | Transient Thermal |
| --- | --- | --- |
| 主要輸出用途 | 平衡溫度、thermal gradients、heat flow rates／heat fluxes。 | 隨時間變動的溫度及熱量；可供熱應力分析載入。 |
| 材料輸入 | Thermal Conductivity。 | Thermal Conductivity、Density、Specific Heat。 |
| 非線性來源 | 溫度相依物性、輻射或溫度相依對流係數。 | 同類非線性加上時間演化；需設定初始溫度與時間步。 |

暫態初始條件可用 uniform temperature，或來源穩態溫度場；文件所列預設初始溫度不是應力自由參考溫度的通用選值。Output Controls 決定保存的結果時間，並不等於每個內部求解增量都寫出。

來源：[Steady-State Thermal Analysis](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_sim/ds_static_thermal_analysis_type.html)（[來源清冊](sources.csv#official_thermal_steady_v261)）、[Transient Thermal Analysis](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_sim/ds_transient_thermal_analysis_type.html)（[來源清冊](sources.csv#official_thermal_transient_v261)）。

## 熱應力、CTE 與溫度場映射檢查

### Thermal Strain 的材料與參考溫度

v261 Thermal Strain 說明以 CTE 與結構溫度載荷計算熱應變，部件／body 的 `Thermal Strain Effects` 要設 Yes。該頁使用 **Secant** coefficient，並允許結構 analysis 的 Reference Temperature，或材料各自的 stress-free temperature。不能由環境溫度、焊料液相線或固化溫度直接推定所有材料的參考值。

來源：[Thermal Strain](https://ansyshelp.ansys.com/public/views/secured/corp/v261/en/wb_sim/ds_therm_strain.html)（[來源清冊](sources.csv#official_thermal_strain_v261)）。

### Shared／Unshared Model 與時間欄位

Thermal-Stress 專節明確支援相同網格及不同網格；不同網格時會映射與插值。`Source Time` 選熱來源時刻，`Analysis Time` 選施加時刻；可設定多列與 All／Range。Graphics preview 若指定時間不在表內，原文說顯示最接近的表列時間，不能把預覽當成精確時刻結果。

Unshared Model 可檢查 Source Bodies 配對摘要，來源重算後須 refresh／re-import。**來源文字差異：**兩個熱 analysis 概要頁寫後續結構分析 mesh must be identical；同版 Thermal-Stress 專節則明列 unshared mapping。此處保留差異，以所選工作流程的專節確認。

來源：[Thermal-Stress Analysis](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_sim/ds_thermal_stress.html)（[來源清冊](sources.csv#official_thermal_stress_v261)）、前節兩個 analysis type 來源。

### Mapping 的資料意義與可觀察檢查

**Profile Preserving** 用來保留如溫度的場分佈；**Conservative** 保持相應總量，並非對溫度做總量守恆。該 Mechanical 頁面將 Conservative 選項限於 Imported Force。原頁可建立 Mapped／Unmapped／Outside named selections，Outside 的回填／忽略行為依 weighting 與選項而變；不能僅用 bounding box 或固定 100% 規則取代資料檢查。

`Mapping Validation` 可做 Reverse Validation、Distance Based Average Comparison 或 Source Value；其圖形差異顯示設定不是工程驗收容差。應依模型目的評估溫度分佈、未定義點與局部差異。

來源：[Data Transfer Mesh Mapping](https://ansyshelp.ansys.com/public/views/secured/corp/v261/en/wb_sim/ds_appen_data_transfer.html)（[來源清冊](sources.csv#official_thermal_meshmap_v261)）、[Mapping Validation](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_sim/sect_mapping_validation_611.html)（[來源清冊](sources.csv#official_thermal_validation_v261)）。

### Mapped Data：To Input File／To Binary File

`To Input File` 將映射載荷寫進輸入資料；`To Binary File` 使用 DPF binary 傳遞。對 Imported Body Temperature，來源可為支援的上游熱分析、External Data 或 MAPDL results。**To Binary File 的同一 imported load object 中不要重複 Source Time／Source Frequency**；需要重複值時拆成不同物件。這是特定選項的資料限制，不是要求熱與結構所有求解時間步完全相同。

來源：[Load Mapping Workflow Specification](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_sim/ds_imported_load_map.html)（[來源清冊](sources.csv#official_thermal_loadmap_v261)）。本頁不提供未核對的 `FilePath`／`GetOutsideNodesCount` 自動化程式。

## System Coupling CHT 傳遞量

### Mechanical wall region 的變數名稱

下表只摘錄 v261 Mechanical wall-region 的方向與 quantity；不能把 Heat Flow 的名稱自動換成 heat flux 或 W/m²。

| Display／Internal Name | 方向 | Quantity Type |
| --- | --- | --- |
| Heat Flow／`HFLW` | Input and Output | Heat Rate |
| Heat Transfer Coefficient／`HCOE` | Input | Heat Transfer Coefficient |
| Temperature／`TEMP` | Input and Output | Temperature |
| Near Wall Temperature／`TBULK` | Input | Temperature |

來源：[Variables Available for System Coupling](https://ansyshelp.ansys.com/public/views/secured/corp/v261/en/wb_sim/ds_sc_variables.html)（[來源清冊](sources.csv#official_thermal_scvars_v261)）。Body-region 的變數是另一張表，不能套用 wall-region 的方向。

### q-T 與 T-hTref 是不同耦合方法

**q-T** 交換一側的 heat flux q 與另一側溫度 T，兩邊由誰送哪個量會影響數值穩定性。**T-hTref** 改送 h 與 convection reference temperature；System Coupling負責 mapping／sending，計算與使用由參與者負責。其 Tref 不是上節材料的 stress-free Reference Temperature。

T-hTref 通常較穩定，但不保證收斂快，且原文指出界面 heat rate 不再保持 q 的守恆。原字典的固定 1% 能量誤差門檻沒有來源，已移除。

來源：[The q-T Method](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/sysc_th/sysc_th_cht_qtmethod.html)（[來源清冊](sources.csv#official_thermal_qt_v261)）、[The T-hTref Method](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/sysc_th/sysc_th_cht_thtrefmethod.html)（[來源清冊](sources.csv#official_thermal_htref_v261)）。

### Fluent 的 via System Coupling 與方向

v261 Fluent 可輸入 temperature、heat flow（heat rate）、HTC；輸出另有 near wall temperature。要從其他參與者接收熱資料，wall thermal condition 要選 `via System Coupling`；只有輸出資料時不必選。若選了它卻沒有接收任何耦合資料，原文說該邊界行為等同 adiabatic。每個transfer的變數仍由設定指定，不能把「流體固定送heat flux、固體固定送temperature」當成所有工作流的規則。

來源：[Boundary Conditions — Heat Transfer Through System Coupling](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/flu_ug/flu_ug_bcs_sec_bound_cond.html)（[來源清冊](sources.csv#official_thermal_fluent_v261)），8.4.15.5.11。

### Participant Library 教學是 mock 例子

[v261 square-channel tutorial](../ANSYS_Document/System_Coupling/v261/guide/07b13e8afb2e-channel-flow-tutorial.md)（[來源清冊](sources.csv#ansys_f1990f1ede4e84c5c78b5802)）明列 Fluent 加 mock solver：mock 在四個 quad elements 各送 5 W（總20 W），接收節點溫度。這證明該教學資料形狀與 setup 示範，不是完整固體熱 solver 或物理驗證案例。[participant setup](../ANSYS_Document/System_Coupling/v261/guide/0fb1b14f4473-participant-setup.md)（[來源清冊](sources.csv#ansys_4f7f01532c8728617908c7af)）另區分 SCP file 與 direct setup；SCP不含實際mesh／solution data。

## Motor-CAD LPTN 熱網路摘要

官方 v252 Thermal 頁將 Motor-CAD 描述為 **3-dimensional lumped circuit model**，可計算穩態與暫態熱特性；Thermal model type 與有效 Therm module license 是該頁的介面前提。沒有來源支持原字典「數秒內精確求完整循環」的通用保證。

來源：[Thermal — Motor-CAD](https://ansyshelp.ansys.com/public/Views/Secured/MotorCAD/v252/en/Motor-CAD_UG/MotorCAD/topics/thermal.html)（[來源清冊](sources.csv#official_thermal_motor_v252)）。既有紀錄將兩個 v261 頁面標為不可取。這次未重新擷取，v252 摘要仍按原版號使用。存取紀錄：[Thermal URL](sources.csv#official_thermal_motorcad_thermal_v261_unavailable)、[Thermal Modeling URL](sources.csv#official_thermal_motorcad_thermal_modeling_v261_unavailable)。

### 本機 unknown-release 的 transient／duty-cycle 教學

[本機PDF](../ANSYS_Document/MotorCAD/unknown/guides_and_tutorials/Thermal_Transient_Analysis.pdf)（[來源清冊](sources.csv#ansys_81be4bec7c700b26b4340cd6)）已有17頁canonical文字，日期8 October2025。

- 教學第一條路徑在實頁3要求先建立 Lab model，再做 duty cycle；耦合選項仍有下述原文差異。
- [實頁9–11](../ANSYS_Document/_catalog/pdf_text_v4/0f3953ee0e2c5a117f964f99eeadc51982ce25accc2a087f3a4aadab7c32e0fd.md#pdf-page-9)：specified losses 路徑可使用自己的 machine loss data；Thermal模型下將calculation type設Transient，再分 **Simple Transient**（fixed load）與 **Duty-Cycle Analysis**（load/losses隨時間變動）。
- [實頁14–17](../ANSYS_Document/_catalog/pdf_text_v4/0f3953ee0e2c5a117f964f99eeadc51982ce25accc2a087f3a4aadab7c32e0fd.md#pdf-page-14)：查看node temperature、power losses與component間heat flow，並可在radial／axial cross-section檢視最後溫度。這些是教學的結果入口，未在本輪執行。

**待覆核的原文差異：**[實頁2](../ANSYS_Document/_catalog/pdf_text_v4/0f3953ee0e2c5a117f964f99eeadc51982ce25accc2a087f3a4aadab7c32e0fd.md#pdf-page-2)說BrushlessPM／SYNCREL／SYNC／IM sinusoidal current可用close-coupled方案；[實頁4](../ANSYS_Document/_catalog/pdf_text_v4/0f3953ee0e2c5a117f964f99eeadc51982ce25accc2a087f3a4aadab7c32e0fd.md#pdf-page-4)步驟卻選No Coupling，[實頁9](../ANSYS_Document/_catalog/pdf_text_v4/0f3953ee0e2c5a117f964f99eeadc51982ce25accc2a087f3a4aadab7c32e0fd.md#pdf-page-9)又把IM／SYNC列入尚無coupled EMag model的例子。保留 `pending_source_review`，不自行猜測產品版本或改掉原文。

## 來源、轉換與未完成覆蓋

本機catalog沒有product=`thermal`的PDF／HTML項目；本輪重用其他產品的原始來源ID。Motor-CAD教學已有canonical v4及同名Markdown，沒有缺失轉換可補；三份SystemCoupling來源本身是Markdown。來源原件、既有轉換及共享catalog未改寫。

官方HTML保留URL、版本及摘要，全文未離線快取；完整API、Icepak／ThermalDesktop／全部Motor-CAD工作流、所有公式圖片與實際thermal/mapping求解仍未覆核。新完整覆蓋主題保留 `source_limited`，本頁不提供自動求解模板或統一物理驗收門檻。


## 2026-11-04：Wave 8 本機來源盤點與限制說明

本機 catalog 無 `thermal` 專屬文件。15 筆來源列包含一份本機技能、12 筆未快取的線上摘要與兩筆不可取的 Motor-CAD v261 網頁。14 個網址未於本批擷取。Motor-CAD PDF 與三份 System Coupling Markdown 維持原產品歸屬。Motor-CAD PDF 的分享權限、頁內讀序、圖表與公式仍待核對。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/thermal_module_conversion_report_20261104.md)。
