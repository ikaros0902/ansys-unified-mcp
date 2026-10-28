# ANSYS API 快照目錄與查閱手冊 (API Catalog)

本目錄整理 26 份 API、SDK 與 protocol 快照。其中 22 份映射到 13 個產品 ID，另 4 份協定 schema 尚未映射。快照涵蓋 Mechanical、SpaceClaim、LS-DYNA、optiSLang、PyMechanical、PyAnsys Geometry、PyOptiSLang Core、PyMAPDL、PyDPF-Core、PyFluent、PyPrimeMesh、PyAnsys Sound、PyDyna、PyWorkbench、PyAnsys Sherlock，以及 Mechanical、Geometry、Fluent、MAPDL、PrimeMesh、Discovery 和 Workbench 的 gRPC protocol。Mechanical、SpaceClaim、LS-DYNA 的組件快照對應 ANSYS 2025 R1 (`v251`)。Python SDK 快照記錄各自的套件版本，不代表 ANSYS 產品 release。

這 26 份產品、SDK 與 protocol 快照是目前整理的 API 擷取範圍，不代表涵蓋所有 ANSYS 產品、版本或公開介面。文件來源清冊列出的產品與 SDK 也不代表其 API 已擷取。APIKB 目前設定 114 個來源鍵：二十六份 API／SDK／protocol 快照、五十五份 REA 靜態候選快照及三十三份 native PE export 快照。coverage 清冊仍按 57 個 manifest 產品 ID 統計，並明列 `pydyna`→`lsdyna`、`mechanical_core`→`mechanical`、`geometry_core`→`geometry`、`optislang_core`→`optislang`、`sherlock_core`→`sherlock`、`workbench_protocol`→`workbench`、`mechanical_protocol`→`mechanical`、`geometry_protocol`→`geometry`、`fluent_protocol`→`fluent`、`mapdl_protocol`→`mapdl`、`primemesh_protocol`→`primemesh`、`discovery_protocol`→`discovery` 十二個 snapshot alias。REA 與 native 候選鍵不等於新產品 ID，也不代表官方支援 API。最近一次本機 APIKB 重建索引 32,555 symbols、122,838 unique members、205,438 symbol-members、40,074 edges、153,976 FTS entries；此為建置統計，未作 API 查詢驗收。55 份 managed snapshot 的來源鍵、組件 hash、MVID 與 Evidence ID 見[REA managed source index](./curated/rea/index.md)。Mechanical Interfaces、Mechanical DataModel 與 ACT Core 已列入 `mechanical`／`act` 組件證據，Granta MI 對應 `granta_mi`。Discovery 目錄的七組件以 `discovery` 記錄；Maxwell、Q3D 與 Icepak Ansoft add-in 各自列為產品候選；Zemax OpticStudio 的 `ZOSAPI.dll` 與 `ZOSAPI_Interfaces.dll` 已獨立索引；Designer、Mechanical、Simplorer Ansoft add-in 仍待產品映射。安裝路徑不代表官方支援狀態。SpaceClaim Core API 使用獨立 `spaceclaim_core_rea` 來源鍵並對應既有 SpaceClaim 產品；ACT Interfaces、LS-DYNA ACT Interfaces、AnsysEM CoreDotNet、Ansys Additive、API Server、Engineering Data Core/DataProvider、DesignModeler Core、Material Designer Core、TurboSystem AFD/CCD/CPD/RTD Core、Units、Vista TF 和 RSM JobManagement 候選鍵仍未映射或未逐項確認。

Workbench Python SDK 與 gRPC snapshots 分開索引。產品協定清單與未映射套件見 [PyAnsys gRPC/protobuf 協定索引](./curated/protocols/index.md)；Workbench 詳細來源見 [Python SDK 摘要](./curated/workbench/sdk_0_14_0_inventory.md)和[協定字典](./curated/workbench/protocol_0_4_0.md)。其他有版本標記的 Python SDK 快照由 [SDK 人讀字典索引](./curated/sdk/index.md)列出。這些來源尚未核對產品宿主相容性。

產品 protocol schema 的套件版本、服務與欄位統計見[PyAnsys gRPC/protobuf 協定索引](./curated/protocols/index.md)。全產品快照、REA 組件證據與映射缺口見[產品 API 來源與缺口索引](./PRODUCT_API_MATRIX.md)。

完整產品來源與直接快照狀態見 [機器可讀 API 覆蓋清冊](./api_coverage.json)。清冊中的 `documentation_coverage` 是獨立的本機文件版本／缺口盤點，不代表 API 擷取狀態；`no_direct_snapshot` 也不表示該產品沒有 API。

Mechanical 與 SpaceClaim v251 的人讀字典及 AI 檢索提示見[Mechanical API 字典](./curated/mechanical/api_reference_v251.md)和[SpaceClaim API 字典](./curated/spaceclaim/api_reference_v251.md)。官方文件確認與 snapshot-only 的簽名分開標示。

現有 MCP APIKB 與官方文件檢索的查詢順序、版本欄位和證據標籤見[API 與文件檢索指南](./API_RAG_GUIDE.md)。

SDK 套件是否安裝及版本是另一份環境證據，見[本機 Python SDK 安裝快照](./sdk_environment.json)。它只檢查 repo `.venv` 的精確 distribution 名稱，不推論其他 Python 環境、ANSYS 產品安裝狀態或 API 擷取完整度。

既有 optiSLang 全域快照記錄 SDK 1.6.1；本機環境 `ansys-optislang-core` 是 1.6.0。另新增只涵蓋 `Optislang` client 的 1.6.0 獨立快照，保留既有快照且不混合兩版。

## APIKB 查詢與來源追溯：Mechanical、SpaceClaim

AI 查詢沿用 `api_search` 找符號，再用 `api_get` 依完整名稱、產品、release 與 interface 取得定義。兩個工具的結果包含版本、介面、來源路徑與快照 SHA-256。repo 內來源使用相對路徑；repo 外本機來源保存絕對路徑，以便後續重建。APIKB 位於被忽略的本機資料目錄，不隨文件上傳。

Native export candidates 可用 `api_search(query="RomBldCfgGetDoe", product="rom_api_native")` 搜尋。CFX v251 的例子是 `api_search(query="GM_BBOX_CAD", product="cfx_cadapi_native")` 與 `api_search(query="DSDB_OPEN", product="cfx_acmo_native")`；DPF v251 的例子是 `api_search(query="LoadOperators", product="dpf_mechanicalresults_native")`。查詢命中表示 snapshot 記錄了該 PE export 名稱，不證明官方支援或可在應用程式呼叫。

| 查詢 | v251 靜態結果 | APIKB 來源 | 驗證狀態 |
| --- | --- | --- | --- |
| Mechanical `AddFixedSupport` | `() → Ansys.ACT.Automation.Mechanical.BoundaryConditions.FixedSupport` | `docs/api_inventory/mechanical_api.json`；SHA-256 `ef8c5c515bf8651d1a517068423998209c3fdebcfea153cd33acb470201b1c2b` | 搜尋／定義查詢成功；`not_classified`；snapshot only，runtime 未驗證 |
| SpaceClaim `DatumPlaneCreator.Create` | Python.NET reflection snapshot 記錄 5 個 overload，輸入型別組合為 `Point+Direction`、`Point+Direction+Direction`、`Plane`、`Frame`、`ISelection`，皆回傳 `DatumPlaneResult`；均另列 `Boolean select` 與 `ICommandInfo info` 參數。尚未與官方 CHM 條目逐項核對 | `docs/api_inventory/spaceclaim_api.json`；SHA-256 `842645f05a06a1097c364648cf9370f1432d2a56c748124ddee7c0c3a5144219` | 搜尋／定義查詢成功；`not_classified`；snapshot only，runtime 未驗證 |

上表記錄本機 APIKB 的 v251 snapshot 查詢。官方 v251 [Mechanical Analysis Object 說明](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/act_script/mech_apis_AnalysisObject.html)示範 `analysis1.AddFixedSupport()` 並將回傳值存入 `support`；官方 [ACT API Reference Guide](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/pdf/Ansys_ACT_API_Reference_Guide.pdf)索引列出 `AddFixedSupport()`。這支持方法存在及無參數呼叫形式，但沒有在此確認回傳型別；回傳型別仍來自 snapshot。SpaceClaim 本機 v251 官方 `SpaceClaim_Documentation.pdf`（SHA-256 `a11b41f9c1039474c7b8d8c53e34df1db08c53369002f0bb268c281d3513fd23`）第 385 頁談 datum plane 的使用行為，沒有列出 `DatumPlaneCreator` API。安裝目錄有 v251 `API_Scripting_Class_Library.chm`（SHA-256 `4d455222d70fed5acdb0a57d55b011fa67208641e4e73d31db24271d8aecb47`）；目前取得五種 overload 簽名僅依 Python.NET reflection snapshot，尚未成功解析 CHM 條目或與官方簽名逐項核對。兩項公開狀態仍為 `not_classified`；未啟動 ANSYS application、未在宿主執行腳本或求解。SpaceClaim snapshot 使用 Python.NET 載入 Scripting assembly 讀取反射 metadata。

SpaceClaim 的五筆簽名來自本機 Python.NET `System.Reflection` v251 snapshot，擷取範圍是 exported types 上 public、declared-only、非 special-name 方法。APIKB 來源列保存 snapshot SHA-256 與 assembly SHA-256，但沒有 REA Evidence ID。獨立 REA 證據記錄同一組件的 SHA-256 `9f5f3d03675bfc1d62e6fbf0244c9473c5e861fcacc3242028b329350e268261`、MVID `06a113f3-00bd-40c2-b02c-53ee8e758a32` 及 Evidence ID `ev_d458c1dfc8a5f9b5483e8a9fecd1f3a3d27157d38865491804f7d17308f31b4a`；REA 與此快照尚未做逐方法交叉核對。以下列出 snapshot 中五筆 `Create` 簽名；不表示參數可省略或方法受支援：

| Overload | v251 snapshot signature |
| --- | --- |
| 1 | `Create(Point origin, Direction zDir, Boolean select, ICommandInfo info) → DatumPlaneResult` |
| 2 | `Create(Point origin, Direction xDir, Direction yDir, Boolean select, ICommandInfo info) → DatumPlaneResult` |
| 3 | `Create(Plane plane, Boolean select, ICommandInfo info) → DatumPlaneResult` |
| 4 | `Create(Frame frame, Boolean select, ICommandInfo info) → DatumPlaneResult` |
| 5 | `Create(ISelection selection, Boolean select, ICommandInfo info) → DatumPlaneResult` |

REA 查詢結果另外提供 `public_status`、`validation_status`、組件 SHA-256 與 REA Evidence ID；`source.sha256` 則是 API snapshot JSON 的雜湊。型別 visibility 或方法 access flags 記為靜態 metadata；例如 `public` 表示 metadata access 標記，不代表 Ansys 對外支援。REA 結果標記 `static_metadata_only; runtime_unverified`；其他快照標記 `snapshot_only; runtime_unverified`，未分類的公開狀態標記 `not_classified`。簽名或 access metadata 不完整時，以原始 snapshot 和官方文件為準。

本機 v251 Mechanical DataModel 與 Interfaces、SpaceClaim API 與 Scripting、AnsysEM CoreCOMScripting 與 CoreDotNet、ACT 共用介面與 Core、LS-DYNA ACT 介面、Additive、AUTODYN、DesignXplorer、Engineering Data、Granta MI、Material Designer、TurboSystem、Units、Vista TF、API Server Discovery/Geometry 的 REA metadata，Zemax ZOS-API 的 REA metadata，以及 DPF、CFX、System Coupling、ROM 和 AnsysEM APIP Wrapper 的 PE 格式證據見 [REA 組件證據摘要](./REA_EVIDENCE.md)。五十五份 REA 候選快照透過獨立 APIKB 來源鍵提供搜尋；結果包含非公開成員候選，部分 signature type RID 和參數名稱尚未解析。這些組件只代表可觀察到的靜態介面，不代表產品完整 API；metadata 或 export 計數不等於公開 API 數量。

2026-10-28 又分析 CFX v251 `Ans.CFX.CadApi.dll` 與 `Ans.CFX.Acmo.dll`。REA 確認兩個 PE 均沒有可讀取的 CLI metadata；另以 `llvm-readobj 19.1.5 --coff-exports` 擷取 43 與 17 個 export 名稱，沒有可解碼的函式簽名。兩個候選快照已加入來源設定並納入 APIKB；建置後 symbol 與 FTS entry 各增加 60。元件雜湊、REA Evidence ID 與限制見 [REA 組件證據摘要](./REA_EVIDENCE.md)。

DPF v251 `Ans.Dpf.MechanicalResults.dll` 的 REA CLI metadata 亦為 `absent`。LLVM 19.1.5 只找到 `LoadOperators` 一個 export，沒有簽名。候選快照已加入 APIKB，當時建置為 17,045 symbols、104,308 unique members、186,908 symbol-members、34,370 edges、119,958 FTS entries，屬歷史 checkpoint；現行建置統計見 [REA 證據摘要](./REA_EVIDENCE.md)。此 export 名稱不證明 API 支援或 runtime 可用。

## REA v251 靜態候選介面

下列資料列出 REA 發現的 TypeDef 與 MethodDef，不是官方支援 API 清冊。APIKB 以獨立來源鍵索引成員名稱和原始可解簽名。REA 候選項目記錄 metadata flags；SpaceClaim 直接 snapshot 另保存組件 SHA-256。兩者仍需官方文件簽名對照；請勿將 metadata 當作產品支援承諾。

| 元件 | APIKB 來源鍵 | 快照 | 型別列 | 方法列 |
| --- | --- | --- | ---: | ---: |
| ACP managed component | `acp_core_rea` | [acp_core_rea_api.json](./acp_core_rea_api.json) | 211 | 2,172 |
| AUTODYN DataModel | `autodyn_rea` | [autodyn_rea_api.json](./autodyn_rea_api.json) | 24 | 242 |
| DesignXplorer PublicAPIs | `designxplorer_rea` | [designxplorer_rea_api.json](./designxplorer_rea_api.json) | 33 | 228 |
| Engineering Data DataModel | `engineeringdata_rea` | [engineeringdata_rea_api.json](./engineeringdata_rea_api.json) | 37 | 400 |
| Engineering Data Core candidate | `engineeringdata_core_rea` | [engineeringdata_core_rea_api.json](./engineeringdata_core_rea_api.json) | 46 | 604 |
| Engineering Data DataProvider candidate | `engineeringdata_dataprovider_rea` | [engineeringdata_dataprovider_rea_api.json](./engineeringdata_dataprovider_rea_api.json) | 132 | 656 |
| DesignModeler Core candidate | `designmodeler_core_rea` | [designmodeler_core_rea_api.json](./designmodeler_core_rea_api.json) | 262 | 3,154 |
| Mechanical Interfaces | `mechanical_interfaces_rea` | [mechanical_interfaces_rea_api.json](./mechanical_interfaces_rea_api.json) | 36 | 187 |
| Mechanical DataModel | `mechanical_datamodel_rea` | [mechanical_datamodel_rea_api.json](./mechanical_datamodel_rea_api.json) | 1,019 | 813 |
| Discovery Collaboration API | `discovery_collaboration_rea` | [discovery_collaboration_rea_api.json](./discovery_collaboration_rea_api.json) | 287 | 1,202 |
| Discovery Gateway API | `discovery_gateway_rea` | [discovery_gateway_rea_api.json](./discovery_gateway_rea_api.json) | 12 | 37 |
| Discovery Geometry API | `discovery_geometry_rea` | [discovery_geometry_rea_api.json](./discovery_geometry_rea_api.json) | 29 | 113 |
| Discovery OnScale API | `discovery_onscale_rea` | [discovery_onscale_rea_api.json](./discovery_onscale_rea_api.json) | 1,074 | 9,059 |
| Discovery Physics API | `discovery_physics_rea` | [discovery_physics_rea_api.json](./discovery_physics_rea_api.json) | 29 | 106 |
| Discovery Project API | `discovery_project_rea` | [discovery_project_rea_api.json](./discovery_project_rea_api.json) | 101 | 424 |
| Discovery Results API | `discovery_results_rea` | [discovery_results_rea_api.json](./discovery_results_rea_api.json) | 47 | 179 |
| ANSYS Motion MotionAPI | `motion_api_rea` | [motion_api_rea_api.json](./motion_api_rea_api.json) | 8 | 36 |
| Maxwell add-in | `maxwell_addin_rea` | [maxwell_addin_rea_api.json](./maxwell_addin_rea_api.json) | 2 | 10 |
| Q3D Extractor add-in | `q3d_addin_rea` | [q3d_addin_rea_api.json](./q3d_addin_rea_api.json) | 2 | 9 |
| Icepak Ansoft add-in | `icepak_ansoft_addin_rea` | [icepak_ansoft_addin_rea_api.json](./icepak_ansoft_addin_rea_api.json) | 2 | 8 |
| Granta MI API client | `granta_mi_rea` | [granta_mi_rea_api.json](./granta_mi_rea_api.json) | 6 | 80 |
| Material Designer wrapper | `materialdesigner_rea` | [materialdesigner_rea_api.json](./materialdesigner_rea_api.json) | 6 | 115 |
| Material Designer Core candidate | `materialdesigner_core_rea` | [materialdesigner_core_rea_api.json](./materialdesigner_core_rea_api.json) | 158 | 1,795 |
| TurboSystem CCD interface | `turbosystem_ccd_rea` | [turbosystem_ccd_rea_api.json](./turbosystem_ccd_rea_api.json) | 1 | 243 |
| TurboSystem CCM interface | `turbosystem_ccm_rea` | [turbosystem_ccm_rea_api.json](./turbosystem_ccm_rea_api.json) | 1 | 76 |
| TurboSystem AFDCore candidate | `turbosystem_afd_core_rea` | [turbosystem_afd_core_rea_api.json](./turbosystem_afd_core_rea_api.json) | 5 | 255 |
| TurboSystem CCDCore candidate | `turbosystem_ccd_core_rea` | [turbosystem_ccd_core_rea_api.json](./turbosystem_ccd_core_rea_api.json) | 3 | 428 |
| TurboSystem CPDCore candidate | `turbosystem_cpd_core_rea` | [turbosystem_cpd_core_rea_api.json](./turbosystem_cpd_core_rea_api.json) | 16 | 276 |
| TurboSystem RTDCore candidate | `turbosystem_rtd_core_rea` | [turbosystem_rtd_core_rea_api.json](./turbosystem_rtd_core_rea_api.json) | 3 | 278 |
| Units DataModel | `units_rea` | [units_rea_api.json](./units_rea_api.json) | 13 | 63 |
| Vista TF DataModel | `vista_tf_rea` | [vista_tf_rea_api.json](./vista_tf_rea_api.json) | 96 | 1,124 |
| ACT Core | `act_core_rea` | [act_core_rea_api.json](./act_core_rea_api.json) | 1,258 | 10,243 |
| API Server Discovery (product mapping pending) | `api_discovery_rea` | [api_discovery_rea_api.json](./api_discovery_rea_api.json) | 211 | 766 |
| API Server Geometry (product mapping pending) | `api_geometry_rea` | [api_geometry_rea_api.json](./api_geometry_rea_api.json) | 149 | 678 |
| ACT Interfaces | `act_interfaces_rea` | [act_interfaces_rea_api.json](./act_interfaces_rea_api.json) | 297 | 1,621 |
| LS-DYNA ACT Interfaces (mapping pending) | `lsdyna_interfaces_rea` | [lsdyna_interfaces_rea_api.json](./lsdyna_interfaces_rea_api.json) | 8 | 69 |
| AnsysEM CoreDotNet (mapping pending) | `ansysem_coredotnet_rea` | [ansysem_coredotnet_rea_api.json](./ansysem_coredotnet_rea_api.json) | 26 | 169 |
| Remote Solve Manager JobManagement (product mapping pending) | `rsm_jobmanagement_rea` | [rsm_jobmanagement_rea_api.json](./rsm_jobmanagement_rea_api.json) | 84 | 449 |
| Ansys Additive (mapping pending) | `additive_rea` | [additive_rea_api.json](./additive_rea_api.json) | 208 | 2,314 |
| SpaceClaim Core API | `spaceclaim_core_rea` | [spaceclaim_core_rea_api.json](./spaceclaim_core_rea_api.json) | 3,904 | 21,426 |
| AQWA Core add-in | `aqwa_addin_rea` | [aqwa_addin_rea_api.json](./aqwa_addin_rea_api.json) | 290 | 3,464 |
| AQWA RemoteItf | `aqwa_remote_itf_rea` | [aqwa_remote_itf_rea_api.json](./aqwa_remote_itf_rea_api.json) | 13 | 74 |
| CFX Core add-in | `cfx_addin_rea` | [cfx_addin_rea_api.json](./cfx_addin_rea_api.json) | 240 | 2,505 |
| Fluent add-in | `fluent_addin_rea` | [fluent_addin_rea_api.json](./fluent_addin_rea_api.json) | 482 | 7,652 |
| Icepak Core add-in | `icepak_addin_rea` | [icepak_addin_rea_api.json](./icepak_addin_rea_api.json) | 115 | 1,588 |
| Meshing Core add-in | `meshing_addin_rea` | [meshing_addin_rea_api.json](./meshing_addin_rea_api.json) | 399 | 3,925 |
| Polyflow add-in | `polyflow_addin_rea` | [polyflow_addin_rea_api.json](./polyflow_addin_rea_api.json) | 283 | 3,263 |
| Sherlock add-in | `sherlock_addin_rea` | [sherlock_addin_rea_api.json](./sherlock_addin_rea_api.json) | 465 | 5,357 |
| SIwave IronPython command library | `siwave_libironpythoncmd_rea` | [siwave_libironpythoncmd_rea_api.json](./siwave_libironpythoncmd_rea_api.json) | 96 | 710 |
| Ansoft HFSS add-in | `hfss_addin_rea` | [hfss_addin_rea_api.json](./hfss_addin_rea_api.json) | 2 | 8 |

這五十五份快照目前涵蓋 13,164 個 snapshot class 與 104,252 個 MethodDef 列。它們保留 private、internal 與 special-name 成員；類別文件記錄型別 visibility，方法文件記錄 access flags。部分簽名使用 `class:<rid>`，且沒有參數名稱。REA 輸出中的同名 TypeDef 以 metadata token 區分，避免不同 declaring type 的方法被合併。新增 add-in、Motion、ACP、AQWA RemoteItf 與 SIwave 候選均來自 v251 安裝樹；它們描述靜態實作候選，並非官方支援 API。AQWA、CFX、Fluent、Icepak、Polyflow、Sherlock、ACP、Motion 與 SIwave 的組件位置提供產品關聯證據；Meshing 與 HFSS 維持獨立候選鍵，不推定為 PrimeMesh 或完整 Electronics Desktop API。所有候選仍需官方文件簽名對照與支援狀態審查。

## Native PE export candidates (v251)

REA managed metadata 對下列 native PE 回報 `absent`。APIKB 另索引 LLVM export table 名稱，並只對可解碼的 MSVC decorated symbol 保存反修飾結果。Export 不表示 API 公開、受支援或可直接呼叫；C export 通常不含參數與回傳型別。

| 元件 | APIKB 來源鍵 | 快照 | Export 名稱 | 可解碼簽名 | 元件 SHA-256 |
| --- | --- | --- | ---: | ---: | --- |
| DPF Mechanical Results plugin（支援狀態未確認） | `dpf_mechanicalresults_native` | [dpf_mechanicalresults_native_exports_api.json](./dpf_mechanicalresults_native_exports_api.json) | 1 | 0 | `0948ca657a05b341870ed8744f23798f6e2bebfcd2e58d1fa570cbf952d0c50d` |
| DPF Engineering Data component（支援狀態未確認） | `dpf_engineeringdata_native` | [dpf_engineeringdata_native_exports_api.json](./dpf_engineeringdata_native_exports_api.json) | 1 | 0 | `89b581ece00b807bda9b45bb66d95d11a8217011e550702eff69b39627c20b25` |
| DPF Abaqus reader | `dpf_abaqus_native` | [dpf_abaqus_native_exports_api.json](./dpf_abaqus_native_exports_api.json) | 5 | 4 | `801897892e7eee2fb36fbc1d8dd53c03d692d7d20817dc0752b7786d1599576c` |
| DPF AUTODYN plugin | `dpf_autodyn_native` | [dpf_autodyn_native_exports_api.json](./dpf_autodyn_native_exports_api.json) | 3,183 | 3,181 | `2d6d33f7dd03a3fc3d06c4f086128195a197b3f888c1ed1f8f19c587a63afade` |
| DPF CFF plugin | `dpf_cff_native` | [dpf_cff_native_exports_api.json](./dpf_cff_native_exports_api.json) | 1 | 0 | `7bd44445ace73292e710759c1c5ed8fd5bba437e82cf7f8adb7bb0d57090df72` |
| DPF CGNS reader | `dpf_cgns_native` | [dpf_cgns_native_exports_api.json](./dpf_cgns_native_exports_api.json) | 1 | 0 | `3f10e3f0c92438876846c1da08bd88cfc1fa6d05a403f50dcaf620b005c5f04e` |
| DPF compression component | `dpf_compression_native` | [dpf_compression_native_exports_api.json](./dpf_compression_native_exports_api.json) | 6,303 | 4,995 | `a950a3ce8c6c9966f472cca522d3264cf2ffa95b95a45575f791fce57d4e8b9d` |
| DPF simulation data model plugin | `dpf_datamodel_native` | [dpf_datamodel_native_exports_api.json](./dpf_datamodel_native_exports_api.json) | 1 | 0 | `cb9b2b0a0fee4a008f044385702e0b34066c705d3824d017a100f6786e4b7d90` |
| DPF FEM utilities | `dpf_femutils_native` | [dpf_femutils_native_exports_api.json](./dpf_femutils_native_exports_api.json) | 1 | 0 | `bd01bc1ca2018cb34fab45257a7bfd2a58bf1cc127972f2b344b128fafea755c` |
| DPF FlowDiagram component | `dpf_flowdiagram_native` | [dpf_flowdiagram_native_exports_api.json](./dpf_flowdiagram_native_exports_api.json) | 1 | 0 | `4aa0b6901e61cd8fdaa86c5cb1a90965c7df3c7206d4003a880c5164e32bc687` |
| DPF gRPC component | `dpf_grpc_native` | [dpf_grpc_native_exports_api.json](./dpf_grpc_native_exports_api.json) | 1 | 0 | `ddfabe03be5456bd7f9c83cc9a44c8fe846c8e23c7ab2dc91b9758337c93e856` |
| DPF HDF5 component | `dpf_hdf5_native` | [dpf_hdf5_native_exports_api.json](./dpf_hdf5_native_exports_api.json) | 1 | 0 | `93ca1868abdfa9e31ae40a7bcbf11f84ba0c6ff5085899e7bb3fc4a34c5745bf` |
| DPF LivePost component | `dpf_livepost_native` | [dpf_livepost_native_exports_api.json](./dpf_livepost_native_exports_api.json) | 1 | 0 | `820fe367a593a2d8650ca1c7afb812c8cde0f41a3293a00be2b646db91adde85` |
| DPF LS-DYNA HGP component | `dpf_lsdynahgp_native` | [dpf_lsdynahgp_native_exports_api.json](./dpf_lsdynahgp_native_exports_api.json) | 1 | 0 | `d2b7070192c24457c9175e58b4d15c4cdf79cc0f38df74fe2d0135126326d8bf` |
| DPF math component | `dpf_math_native` | [dpf_math_native_exports_api.json](./dpf_math_native_exports_api.json) | 7 | 6 | `61a6dfb9b77ff2ce02586af5c0fd5ae544083e3084fa449eb0d94e40626527e4` |
| DPF Mechanical component | `dpf_mechanical_native` | [dpf_mechanical_native_exports_api.json](./dpf_mechanical_native_exports_api.json) | 1 | 0 | `9fffe992ba9b2dee65bd4ab9b9c0b04956aa1d56fb4bc6f752d5301f1895e200` |
| DPF multiphysics mapper plugin | `dpf_multiphysicsmapper_native` | [dpf_multiphysicsmapper_native_exports_api.json](./dpf_multiphysicsmapper_native_exports_api.json) | 1,051 | 1,050 | `270fe17133c7d789f73811bcfa3922193703ed8bea34617db04a53680adb20ad` |
| DPF native component | `dpf_native_native` | [dpf_native_native_exports_api.json](./dpf_native_native_exports_api.json) | 1 | 0 | `931ad7ba39652a4ede3c419ad849dc27fe647785973fa444af70664a68a761e7` |
| DPF Prime plugin | `dpf_prime_native` | [dpf_prime_native_exports_api.json](./dpf_prime_native_exports_api.json) | 380 | 0 | `d754b75c6c6620e5110a48a332ec8912e4ad2591a806b4cb9045aa4494727d63` |
| DPF Python plugin wrapper | `dpf_pythonpluginwrapper_native` | [dpf_pythonpluginwrapper_native_exports_api.json](./dpf_pythonpluginwrapper_native_exports_api.json) | 2 | 0 | `21c43820b22e97002a22868edcb103ff8f930035ad442cb4d539a56a317ac1c3` |
| DPF RBD component | `dpf_rbd_native` | [dpf_rbd_native_exports_api.json](./dpf_rbd_native_exports_api.json) | 1 | 0 | `89866c88cc2b4c3bfe0a4f85b6eef497378aafd183e06c175bc8cefbb3439fb2` |
| DPF System Coupling mapping plugin | `dpf_systemcouplingmapping_native` | [dpf_systemcouplingmapping_native_exports_api.json](./dpf_systemcouplingmapping_native_exports_api.json) | 1 | 0 | `384c0d23f574fd99aefa2a52c7e1f1c0e235cd4155527c2597ffbe280a5c1bcc` |
| DPF VTK component | `dpf_vtk_native` | [dpf_vtk_native_exports_api.json](./dpf_vtk_native_exports_api.json) | 1 | 0 | `6a549d0c5889fb29127a7f349d1dc44364295fc5863aefe9e868e4ea16721fc5` |
| Lumerical Python interop API | `lumerical_interopapi_native` | [lumerical_interopapi_native_exports_api.json](./lumerical_interopapi_native_exports_api.json) | 19 | 0 | `f82c6fe630e2715079fa576b28ad0c532d2cd6889dcb7e622ca56bf27a9bedbf` |
| Lumerical remote Python interop API | `lumerical_interopapi_remote_native` | [lumerical_interopapi_remote_native_exports_api.json](./lumerical_interopapi_remote_native_exports_api.json) | 19 | 0 | `ea2aa1ae9ee7944121e377ada5f66f475258cffe619d702975559176bb320e82` |
| Lumerical Tcl API | `lumerical_lumapi_native` | [lumerical_lumapi_native_exports_api.json](./lumerical_lumapi_native_exports_api.json) | 1 | 0 | `21602ad00cf7d082f63aa556d5c5cd91426896ded742c457528749982b23a232` |
| CFX CadApi native component（支援狀態未確認） | `cfx_cadapi_native` | [cfx_cadapi_native_exports_api.json](./cfx_cadapi_native_exports_api.json) | 43 | 0 | `d0e3a9ccfd99e04b65f0e070c4c55514d47887ed8981c6bcf055f01f79973843` |
| CFX Acmo native component（支援狀態未確認） | `cfx_acmo_native` | [cfx_acmo_native_exports_api.json](./cfx_acmo_native_exports_api.json) | 17 | 0 | `c3aa76898adab0b6d40a396aabd97874531a74c42cc601736568f19074bce126` |
| AnsysEM APIP wrapper（產品映射未確認） | `apip_wrapper_native` | [apip_wrapper_native_exports_api.json](./apip_wrapper_native_exports_api.json) | 155 | 72 | `49e755e1515416646138f2f22117b862ca2441417e06602af91a5f853697410e` |
| ROM API native library（支援狀態未確認） | `rom_api_native` | [rom_api_native_exports_api.json](./rom_api_native_exports_api.json) | 381 | 1 | `a408c7cb336d27fe9ab0b7e39187e69e9f64be41a8c5fc0a3bc38cd961958c5d` |
| System Coupling ANSRPC wrapper（產品 API 映射未確認） | `system_coupling_rpc_native` | [system_coupling_rpc_native_exports_api.json](./system_coupling_rpc_native_exports_api.json) | 36 | 36 | `82e247497aed2bfbd47048762c0861f1ac7c43b2663d5484d15bca105c015b96` |
| System Coupling participant component（支援狀態未確認） | `system_coupling_participant_native` | [system_coupling_participant_native_exports_api.json](./system_coupling_participant_native_exports_api.json) | 743 | 508 | `8787c2a0c86ddceaa75846f709f99cd3ec3fafe606d8aa97191732de3dc8bd6b` |
| Speos APIP wrapper（支援狀態未確認） | `speos_apip_wrapper_native` | [speos_apip_wrapper_native_exports_api.json](./speos_apip_wrapper_native_exports_api.json) | 155 | 72 | `d585fac0c0a4811ec4167a44c21d42847baefee19f86e1d2367b40182438f87c` |

三十三份 snapshot 共提供 12,516 個 export 名稱，9,925 個 symbol 可反修飾。工具使用 LLVM `llvm-readobj 19.1.5` 與 Windows `dbghelp`，只解析本機 v251 PE export table；未分析函式本體、呼叫慣例或 runtime 行為。重新擷取命令見 [REA 組件證據摘要](./REA_EVIDENCE.md)。

---

## 一、現有 API 快照 (Current Snapshots)

檔案大小採十進位單位（1 KB = 1,000 bytes；1 MB = 1,000,000 bytes）。

| 產品與版本資訊 | 原始來源 | 快照檔案 | 涵蓋範疇 | 擷取統計 | 檔案大小 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ANSYS Mechanical** | `ansys-mechanical-stubs/v251` (ACT DataModel) | [`mechanical_api.json`](./mechanical_api.json) | Analysis, Mesh, BoundaryConditions, Connections, Results, Solution | **105** 模組<br>**1,728** 類別<br>**40,886** 方法<br>**46,626** 屬性 | ~23.95 MB |
| **PyMechanical** | 本機 `ansys-mechanical-core` SDK 0.13.2 原始碼 | [`mechanical_core_api.json`](./mechanical_core_api.json) | `Mechanical` client 直接成員及 `launch_mechanical`、`connect_to_mechanical`；本機文件 0.13.4 版次不符，已排除 | **1** 類別<br>**21** 方法<br>**9** 屬性<br>**2** 函式 | ~35.9 KB |
| **PyAnsys Geometry** | 本機 `ansys-geometry-core` SDK 0.17.1 原始碼 | [`geometry_core_api.json`](./geometry_core_api.json) | `Modeler` 直接成員及 `launch_modeler`；本機文件 0.18.2 版次不符，已排除 | **1** 類別<br>**10** 方法<br>**7** 屬性<br>**1** 函式 | ~21.9 KB |
| **SpaceClaim (SCDM)** | `SpaceClaim.Api.V251.Scripting.dll` (.NET Reflection) | [`spaceclaim_api.json`](./spaceclaim_api.json) | Geometry, Part, Body, Face, Edge, Selection, Tools, Component | **1,266** 型別<br>**2,845** 方法<br>**1,551** 屬性<br>**114** 列舉 | ~1.59 MB |
| **optiSLang** | `ansys.optislang.core` & `v251/optiSLang/scripting` | [`optislang_api.json`](./optislang_api.json) | Client, Project, RootSystem, Node, Parameter, Criterion, MOP, Algorithms | **37** 模組<br>**241** 類別<br>**1,691** 方法<br>**133** 頂層函式<br>**9** 類內建演算法 | ~1.44 MB |
| **PyOptiSLang Core** | 本機 `ansys-optislang-core` SDK 1.6.0 原始碼 | [`optislang_core_api.json`](./optislang_core_api.json) | `Optislang` client 直接宣告的公開方法與屬性；本機 API reference 1.7.0 版次不符，已排除 | **1** 類別<br>**18** 方法<br>**9** 屬性 | ~33.3 KB |
| **LS-DYNA & LS-PrePost** | `LsPrePost`, `DataCenter`, SCL C-API & Keyword Deck | [`lsdyna_api.json`](./lsdyna_api.json) | LSPP Python, SCL 命令集, DataCenter 提取, 核心關鍵字字典 (*CONTROL, *MAT, *CONTACT 等) | **3** Python API<br>**10** DataCenter 查詢鍵<br>**8** SCL C-API 函式<br>**35** 核心關鍵字定義 | ~15.6 KB |
| **PyDyna** | 本機 `ansys-dyna-core` SDK 0.12.1 與同版 API reference | [`pydyna_api.json`](./pydyna_api.json) | `Deck` 直接宣告的公開方法與屬性 | **1** 類別<br>**19** 方法<br>**17** 屬性 | ~27.1 KB |
| **PyMAPDL** | `ansys-mapdl-core` SDK 0.74.1 與官方 API reference | [`mapdl_api.json`](./mapdl_api.json) | 文件連結的 `MapdlGrpc` 成員與 `launch_mapdl` | **27** 方法<br>**38** 屬性<br>**1** 函式<br>**2** 文件列出但無法由 class 靜態解析的 instance 屬性 | ~188.4 KB |
| **PyDPF-Core** | 本機 `ansys-dpf-core` SDK 0.16.1 原始碼 | [`dpf_api.json`](./dpf_api.json) | `Model`, `DataSources`, `FieldsContainer`, `Field`, `MeshedRegion` 直接宣告的公開成員 | **5** 類別<br>**52** 方法<br>**26** 屬性 | ~89.4 KB |
| **PyFluent** | 本機 `ansys-fluent-core` SDK 0.42.1 原始碼 | [`fluent_api.json`](./fluent_api.json) | SDK 的 `connect_to_fluent` 與 `launch_fluent` 函式匯出 | **2** 函式 | ~9.2 KB |
| **PyPrimeMesh** | 本機 `ansys-meshing-prime` SDK 0.10.5 與同版 API reference | [`primemesh_api.json`](./primemesh_api.json) | `Client` 的 `run_on_server`, `exit`, `model` 與 `launch_prime` | **1** 類別<br>**2** 方法<br>**1** 屬性<br>**1** 函式 | ~9.6 KB |
| **PyAnsys Sound** | 本機 `ansys-sound-core` SDK 0.3.0 與同版 API reference | [`sound_api.json`](./sound_api.json) | `SoundComposer` 與 `Track` 直接宣告的公開方法及屬性 | **2** 類別<br>**13** 方法<br>**6** 屬性 | ~17.8 KB |

---

## 二、快照內容導覽

### 1. ANSYS Mechanical (ACT DataModel API)
* 檔案路徑：[`mechanical_api.json`](./mechanical_api.json)
* 核心架構階層：
  * **Model / Geometry**: `Ansys.ACT.Automation.Mechanical.Model`, `Geometry`, `Body`, `Part`
  * **Mesh Controls**: `Ansys.ACT.Automation.Mechanical.Mesh`, `MeshControl`, `Sizing`, `Inflation`
  * **Boundary Conditions**: `FixedSupport`, `Force`, `Pressure`, `Displacement`, `RemoteDisplacement`, `StandardEarthGravity`
  * **Connections**: `Connections`, `ConnectionGroup`, `ContactRegion` (Bonded, Frictional, Frictionless)
  * **Analysis / Solution**: `Analysis`, `AnalysisSettings`, `Solution`, `SolverData`
  * **Results**: `TotalDeformation`, `EquivalentStress`, `EquivalentPlasticStrain`, `DirectionalDeformation`, `StressTool`
* 典型 ACT 代碼模式（IronPython / ASCII）：
  ```python
  # Access active model and geometry
  model = ExtAPI.DataModel.Project.Model
  geom = model.Geometry
  mesh = model.Mesh
  mesh.ElementSize = Quantity("2.5 [mm]")
  mesh.GenerateMesh()
  
  # Add Boundary Condition
  analysis = model.Analyses[0]
  fixed_support = analysis.AddFixedSupport()
  fixed_support.Location = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
  
  # Solve and Evaluate
  analysis.Solve(True)
  eqv_stress = analysis.Solution.AddEquivalentStress()
  eqv_stress.EvaluateAllResults()
  max_stress = eqv_stress.Maximum.Value
  ```

---

### 2. SpaceClaim (SCDM Scripting API)
* 檔案路徑：[`spaceclaim_api.json`](./spaceclaim_api.json)
* 核心命名空間：`SpaceClaim.Api.V251.Scripting`
* 核心類別清單：
  * **主控制器與視窗**：`Window`, `Document`, `Part`, `Component`
  * **幾何物件模型**：`Body`, `Face`, `Edge`, `Vertex`, `DesignBody`, `DesignFace`
  * **草圖與拓撲建立**：`SketchPoint`, `SketchLine`, `SketchCircle`, `Plane`, `Point`, `Direction`
  * **特徵操作工具**：`FixErrors`, `Midsurface`, `VolumeExtract`, `PowerSelect`, `ExtrudeFaces`, `RevolveFaces`
* `DatumPlaneCreator.Create` 的 v251 Python.NET reflection snapshot 簽名與證據見上方查詢表；該快照沒有參數預設值，官方 CHM 尚未解析，因此本目錄不將省略 `select`／`info` 的範例標為可直接執行的 v251 呼叫。

---

### 3. optiSLang (PyOptiSLang & Scripting API)
* 檔案路徑：[`optislang_api.json`](./optislang_api.json)
* 核心架構階層：
  * **客戶端連接與進程**：`ansys.optislang.core.Optislang`, `OslServerProcess`
  * **專案與系統節點**：`Project`, `RootSystem`, `System`, `Node`
  * **參數與評價指標**：`Parameter`, `Criterion`, `Design`, `DesignVariable`
  * **演算法與節點庫**：`Sensitivity`, `Optimization`, `MOP` (Metamodel of Optimal Prognosis), `Sobol`, `ARSM`
* 典型 Python 自動化模式：
  ```python
  from ansys.optislang.core import Optislang
  
  with Optislang() as osl:
      project = osl.project
      root_sys = project.root_system
      
      # Add Sensitivity and MOP node
      sens_node = root_sys.create_node("Sensitivity")
      mop = sens_node.get_actor()
      
      # Register Parameters and Criteria (Verified APIs)
      root_sys.parameter_manager.add_parameter("thickness", 1.2, 0.8, 2.0)
      root_sys.criterion_manager.add_criterion("max_stress", "< 250")
      
      # Execute run
      project.start()
  ```

---

### 4. LS-DYNA & LS-PrePost (Solver & Post-Processing API)
* 檔案路徑：[`lsdyna_api.json`](./lsdyna_api.json)
* 核心架構三軌制：
  * **軌道一：LS-PrePost 內嵌 Python 自動化 (`LsPrePost`, `DataCenter`)**
    ```python
    import LsPrePost as lspp
    import DataCenter as dc
    
    # Switch to final state and compute fringe
    num_states = dc.get_data("num_states")
    lspp.execute_command(f"state {num_states}")
    lspp.execute_command("fringe 7; pfringe")
    
    # Query maximum von Mises stress
    max_vm_stress = lspp.cmd_result_get_value(1)
    ```
  * **軌道二：LS-PrePost SCL (Scripting Command Language) C-API**
    * 向量與張量提取：`SCLGetDataCenterFloat`, `SCLGetDataCenterVector`, `SCLGetDataCenterTensor`
    * 狀態切換與控制：`SCLSwitchStateTo`, `SCLPrintMessage`
  * **軌道三：LS-DYNA 關鍵字驅動體系 (Keyword Deck)**
    * 求解器調用：`lsdyna_dp.exe i=run.k ncpu=8 memory=4000m`
    * 關鍵字分組覆蓋：`*CONTROL`, `*DATABASE`, `*MAT`, `*SECTION`, `*CONTACT`, `*BOUNDARY`, `*LOAD`

### 5. PyMAPDL (Python Client API)

* 檔案路徑：[`mapdl_api.json`](./mapdl_api.json)
* 來源範圍：PyMAPDL 0.74.1 官方 `Mapdl` API reference 連結的 `MapdlGrpc` 方法／屬性，以及 `launch_mapdl` 工廠函式。
* 未涵蓋：APDL 動態命令、其他 SDK 模組與 class、未列於來源文件的成員。`finish_job_on_exit` 與 `remove_temp_dir_on_exit` 是文件列出的 instance 屬性，class 靜態檢視無法解析其值，因此只保留為 unresolved evidence，不計入成功解析的屬性。
* 擷取只讀取 SDK 類別描述與文件，不建立 MAPDL instance、不連線、不執行 solver。

### 6. PyDPF-Core (核心資料類別)

* 檔案路徑：[`dpf_api.json`](./dpf_api.json)
* 來源範圍：本機 PyDPF-Core 0.16.1 SDK 原始碼中 `Model`、`DataSources`、`FieldsContainer`、`Field` 與 `MeshedRegion` 直接宣告的公開方法與屬性；各來源檔以 SHA-256 記錄。
* 未涵蓋：繼承成員、動態 operators、其他模組、伺服器行為及本機 0.16.3 文件語料。快照不建立資料類別實例、不連線 DPF server，也不執行 solver。

### 7. PyFluent (Launcher API)

* 檔案路徑：[`fluent_api.json`](./fluent_api.json)
* 來源範圍：本機 PyFluent 0.42.1 SDK 原始碼的 `connect_to_fluent` 與 `launch_fluent` 簽章及 docstring。本機文件庫中的 `ANSYS_Document/Fluent/sdk/ansys-fluent-core/0.42.1/api_reference/8daccb15f8d1-launcher.html` metadata 標示為 0.40.3，因此不作為 0.42.1 版本證據。
* 未涵蓋：其他 PyFluent 模組與 API。擷取只讀取函式描述、簽章與來源，不呼叫連線或啟動函式，也不啟動 Fluent。

### 8. PyPrimeMesh (Client API)

* 檔案路徑：[`primemesh_api.json`](./primemesh_api.json)
* 來源範圍：本機 PyPrimeMesh 0.10.5 的 `Client` 直接宣告成員與 `launch_prime`；相關五頁 API reference 的 HTML metadata 均核對為 0.10.5，SDK 與文件以 SHA-256 記錄。
* 未涵蓋：其他 PyPrimeMesh classes、functions 與 API。擷取只讀取類別／函式描述、簽章與來源；不建立 Client、不呼叫 `run_on_server`／`exit`、不啟動 Prime Server。

### 9. PyAnsys Sound (Sound Composer API)

* 檔案路徑：[`sound_api.json`](./sound_api.json)
* 來源範圍：本機 `ansys-sound-core` 0.3.0 SDK 的 `SoundComposer` 與 `Track` 直接宣告方法、屬性及描述；三份 API reference 的 HTML metadata 均核對為 0.3.0，來源檔以 SHA-256 記錄。
* 未涵蓋：繼承成員、其他 Sound modules 與音訊處理行為。擷取不建立物件、不處理訊號，也不連接 server。

### 10. PyDyna (Deck API)

* 檔案路徑：[`pydyna_api.json`](./pydyna_api.json)
* 來源範圍：本機 `ansys-dyna-core` 0.12.1 SDK 的 `Deck` 直接宣告方法與屬性；同版 API reference HTML metadata 核對為 0.12.1，SDK 與文件以 SHA-256 記錄。
* 未涵蓋：`KeywordBase`、自動產生的關鍵字類別與其他模組。擷取以 AST 讀取 SDK 原始碼，不匯入套件、不建立 Deck、不讀寫模型或執行 solver。覆蓋清冊將此獨立 SDK 快照映射至現有 LS-DYNA 產品 ID。

### 11. PyMechanical (Client API)

* 檔案路徑：[`mechanical_core_api.json`](./mechanical_core_api.json)
* 來源範圍：本機 `ansys-mechanical-core` 0.13.2 SDK 的 `Mechanical` client 直接成員，以及 `launch_mechanical`、`connect_to_mechanical` 函式。同步 API reference 的 HTML metadata 為 0.13.4，版次不符，因此不作為 0.13.2 成員證據。
* 未涵蓋：`LocalMechanicalPool`、其他模組及 Mechanical server 行為。擷取以 AST 靜態讀取 SDK 原始碼，不匯入套件、不連線、不啟動 Mechanical。

### 12. PyAnsys Geometry (Modeler API)

* 檔案路徑：[`geometry_core_api.json`](./geometry_core_api.json)
* 來源範圍：本機 `ansys-geometry-core` 0.17.1 SDK 的 `Modeler` 直接成員及 `launch_modeler` 函式。同步 Modeler API reference HTML metadata 為 0.18.2，版次不符，因此只保留為排除的文件證據，不作 0.17.1 成員來源。
* 未涵蓋：`Modeler` 的繼承成員、其他 launch modes 與 Geometry service 行為。擷取以 AST 靜態讀取 SDK 原始碼，不匯入套件、不建立 Modeler、不連線 service。

### 13. PyOptiSLang Core (Optislang client API)

* 檔案路徑：[`optislang_core_api.json`](./optislang_core_api.json)
* 來源範圍：本機 `ansys-optislang-core` 1.6.0 SDK 的 `Optislang` client 直接宣告的公開方法與屬性；同步 API reference HTML metadata 為 1.7.0，版次不符而只列為排除證據，SDK 與文件 hash 均記錄。
* 未涵蓋：`Optislang` 繼承成員、其他 SDK 模組與 v251 scripting API。擷取以 AST 靜態讀取原始碼，不匯入套件、不建立 client、不啟動或連線 optiSLang。

---

## 三、API 知識庫與 FastMCP 工具使用指南

本專案將上述快照整合至 SQLite API 知識庫（`Documentation_clean/api_kb.sqlite`）。目前提供四個快照查詢工具：

| MCP 工具名稱 | 功能說明 | 典型呼叫範例 |
| :--- | :--- | :--- |
| **`api_search`** | 快速檢索類別、方法、屬性或關鍵字 (FTS5 + Trigram) | `api_search(query="fixed support", product="mechanical")` |
| **`api_get`** | 獲取特定 API 符號之所有成員、型別出入邊與文檔 | `api_get(fqname="ansys.optislang.core.optislang.Optislang", include="members", product="optislang_core", interface="PyOptiSLang 1.6.0 Optislang client")` |
| **`api_path`** | 在知識星譜圖中尋找物件存取導航鏈 (BFS 拓撲) | `api_path(from_type="Analysis", to_type="EquivalentStress")` |
| **`api_validate_script`** | 腳本靜態防幻覺校驗器，比對未定義屬性並給予建議 | `api_validate_script(code="...", product="mechanical")` |

`api_get` 可用 `product`、`release`、`interface` 選取特定快照；未指定且同一符號有多個來源時，會回傳候選清單。

另有 `api_federated_path`、`api_federated_search` 與 `api_cross_bridge` 工具，用於跨知識來源查詢。它們不代表本目錄已收錄其他產品的完整 API 快照。

---

## 四、更新與維護機制

目前批次擷取流程處理上表十三份快照，不會擷取所有 ANSYS 產品或版本：
```powershell
python scripts/api_extraction/extract_all_apis.py
```
流程會呼叫十三個產品擷取器，再重建 `Documentation_clean/api_kb.sqlite`。PyMAPDL、PyDPF-Core、PyFluent、PyPrimeMesh、PyAnsys Sound、PyDyna、PyMechanical 與 PyAnsys Geometry 與 PyOptiSLang Core 擷取範圍分別限於上表說明的文件連結成員、五個核心資料類別、兩個 launcher 函式、一個 client class、兩個 Sound Composer 類別、一個 Deck class、一個 Mechanical client class 及一個 Modeler class 及一個 `Optislang` client class；各產品的來源與版本限制見上表，不同版本需使用獨立快照並明確記錄來源。

重新產生產品覆蓋清冊：
```powershell
python scripts/api_extraction/build_coverage_report.py
```
