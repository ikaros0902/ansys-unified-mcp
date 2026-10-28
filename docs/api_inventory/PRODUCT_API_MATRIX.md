# ANSYS 產品 API 來源與缺口索引

本索引依目前 coverage 清冊列出的 57 個產品 ID，彙整直接 API 快照、已映射 REA 組件證據和來源缺口。30 份 API／SDK／protocol 快照中，26 份映射至 16 個產品 ID；APIKB 另索引 55 個 REA 靜態候選來源鍵和 33 份 native export 清冊，逐來源細節見 [API Catalog](./API_CATALOG.md)及[REA source index](./curated/rea/index.md)。

## 證據狀態

- **直接快照**：清冊列有一份或多份產品或 SDK API 快照。快照不涵蓋未列出的成員或版本。
- **REA 組件證據**：清冊列有靜態組件證據，但未必已對應到產品公開 API。
- **待來源／映射**：目前沒有直接快照或已映射的 REA 組件。須先取得版本相符來源，再判斷能否分析。
- **無快照不代表無 API**；文件覆蓋和 API 擷取是兩項不同狀態。所有組件 metadata 和 native export 都不得當作產品支援承諾。

## 產品清單

| 產品 | 現有證據 | 直接 API 快照 | REA v251 組件證據 | 映射狀態與缺口 |
| --- | --- | --- | --- | --- |
| `ACP` (`acp`) | REA 組件證據 | — | [ACP.dll](./REA_EVIDENCE.md)（v251） | 已記錄 ACP managed component 靜態 metadata 候選；SDK 版本、官方 API 對照及支援狀態仍待核對。 (`product_component_evidence_only`) |
| `ACT` (`act`) | REA 組件證據 | — | [Ansys.ACT.Interfaces.dll; Ansys.ACT.Core.dll](./REA_EVIDENCE.md)（v251） | 已記錄相關組件證據；產品歸屬或官方 API 對照仍待處理。 (`product_component_evidence_only`) |
| `Additive` (`additive`) | REA 組件證據 | — | [Ansys.Api.Additive.dll](./REA_EVIDENCE.md)（v251） | 已記錄相關組件證據；產品歸屬或官方 API 對照仍待處理。 (`product_component_evidence_only`) |
| `ADR` (`adr`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `AEDT` (`aedt`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `Ansys_ID_Portal` (`ansys_id_portal`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `Ansys_ID_SSO` (`ansys_id_sso`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `AnsysEM` (`ansysem`) | REA 組件證據 | — | [Ansys.Ansoft.CoreCOMScripting.dll; Ansys.Ansoft.CoreDotNet.dll](./REA_EVIDENCE.md)（v251） | 已記錄相關組件證據；產品歸屬或官方 API 對照仍待處理。 (`product_component_evidence_only`) |
| `Aqwa` (`aqwa`) | REA 組件證據 | — | [Ans.AQWA.Core.dll; Ans.AQWA.RemoteItf.dll](./REA_EVIDENCE.md)（v251） | 兩份組件均為 REA 靜態 metadata 候選；產品支援狀態與官方 API 對照仍待處理。 (`product_component_evidence_only`) |
| `AVxcelerate` (`avxcelerate`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `CFF` (`cff`) | 待來源／映射 | — | — | 只找到 `Ans.Fluent.CffWrapper.dll` 共用 wrapper 候選，型別屬 Fluent namespace；不足以映射為 CFF API。 (`not_assessed`) |
| `CFX` (`cfx`) | PyAnsys CFX SDK snapshot 與 REA 組件證據 | [cfx_api.json](./cfx_api.json)（ansys-cfx-core 0.3.0；47 modules、93 classes、149 methods、21 properties、60 functions） | [Ans.CFX.CadApi.dll; Ans.CFX.CFXCore.dll](./REA_EVIDENCE.md)（v251） | 快照直接擷取不含底線名稱的 AST 宣告；套件 distribution METADATA 要求本機授權 CFX 安裝，並說明 PyCFX 支援 CFX 2025 R2 SP3 以上；不能作為 v251 相容證據。動態 flobject/TUI surface 未擷取，宿主行為及官方 API 對照未確認。 (`direct_product_id`) |
| `Discovery` (`discovery`) | 直接快照與 REA 組件證據 | [discovery_protocol_api.json](./discovery_protocol_api.json)（ansys-api-discovery 1.2.12：142 modules、130 services、1,422 RPC、1,742 messages、4,119 fields） | [Ansys.Collaboration.Api.dll; Ansys.Gateway.Api.dll; Ansys.Geometry.Api.dll; Ansys.OnScale.Api.dll; Ansys.Physics.Api.dll; Ansys.Project.Api.dll; Ansys.Results.Api.dll](./REA_EVIDENCE.md)（v251） | 協定 schema 與 v251 REA 組件證據分開列示；產品版本對照、支援狀態及宿主行為未核實。 (`direct_product_id`) |
| `DPF` (`dpf`) | 直接快照 | [dpf_api.json](./dpf_api.json)（unknown；類別 5、方法 52、屬性 26、函式 0） | [23 個 DPF PE 元件（REA/PE sweep）](./REA_EVIDENCE.md)（v251） | 清冊以產品 ID 對應來源；快照僅涵蓋所列版本與範圍。 (`direct_product_id`) |
| `edupack` (`edupack`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `EnSight` (`ensight`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `FENSAP-ICE` (`fensap_ice`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `Fluent` (`fluent`) | 直接快照 | [fluent_api.json](./fluent_api.json)（PyFluent 0.42.1）；[fluent_protocol_api.json](./fluent_protocol_api.json)（ansys-api-fluent 0.6.0：28 services、290 RPC、813 messages、1,697 fields） | [Ans.Fluent.dll](./REA_EVIDENCE.md)（v251） | 協定 schema 描述 gRPC 傳輸介面；不代表產品 API 完整或 runtime 可用。 (`direct_product_id`) |
| `Geometry` (`geometry`) | 直接快照 | [geometry_core_api.json](./geometry_core_api.json)（PyAnsys Geometry 0.17.1）；[geometry_protocol_api.json](./geometry_protocol_api.json)（ansys-api-geometry 0.4.92：17 services、298 RPC、491 messages、1,272 fields） | — | 協定 schema 描述 gRPC 傳輸介面；不代表產品 API 完整或 runtime 可用。 (`direct_product_id`) |
| `Granta_MI` (`granta_mi`) | REA 組件證據 | — | [Ansys.Apip.Client.dll](./REA_EVIDENCE.md)（v251） | 已記錄相關組件證據；產品歸屬或官方 API 對照仍待處理。 (`product_component_evidence_only`) |
| `HFSS` (`hfss`) | REA 組件證據 | — | [Ans.Ansoft.HFSSAddinPlugin.dll](./REA_EVIDENCE.md)（v251） | 已記錄相關組件證據；產品歸屬或官方 API 對照仍待處理。 (`product_component_evidence_only`) |
| `ICEM_CFD` (`icem_cfd`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `Icepak` (`icepak`) | REA 組件證據 | — | [Ans.Icepak.Core.dll; Ans.Ansoft.IcepakAddinPlugin.dll](./REA_EVIDENCE.md)（v251） | 已記錄相關組件證據；產品歸屬或官方 API 對照仍待處理。 (`product_component_evidence_only`) |
| `Installation_and_Licensing` (`installation_and_licensing`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `LS-PrePost` (`ls_prepost`) | 待來源／映射 | — | — | v251 managed inventory 未找到名稱明確指向 LS-PrePost 的組件；仍需產品安裝樹或官方介面來源。 (`not_assessed`) |
| `LS-DYNA` (`lsdyna`) | 直接快照 | [lsdyna_api.json](./lsdyna_api.json)（Ansys 2025 R1 (LS-DYNA / LS-PrePost 4.12)；類別 0、方法 0、屬性 0、函式 0）<br>[pydyna_api.json](./pydyna_api.json)（unknown；類別 1、方法 19、屬性 17、函式 0） | [Ansys.ACTLSDYNA.Interfaces.dll](./REA_EVIDENCE.md)（v251） | 清冊以產品 ID 對應來源；快照僅涵蓋所列版本與範圍。 (`direct_product_id`) |
| `Lumerical` (`lumerical`) | REA 組件證據 | — | [Python `interopapi.dll`、`interopapi-remote.dll` 與 Tcl `lumapi.dll`](./REA_EVIDENCE.md)（v251） | 已記錄 39 個 native export 候選；函式簽名、產品支援與 runtime 均未確認。 (`product_component_evidence_only`) |
| `MAPDL` (`mapdl`) | 直接快照 | [mapdl_api.json](./mapdl_api.json)（PyMAPDL 0.74.1）；[mapdl_protocol_api.json](./mapdl_protocol_api.json)（ansys-api-mapdl 0.6.0：3 services、84 RPC、105 messages、227 fields） | — | 協定 schema 描述 gRPC 傳輸介面；不代表產品 API 完整或 runtime 可用。 (`direct_product_id`) |
| `Maxwell` (`maxwell`) | REA 組件證據 | — | [Ans.Ansoft.MaxwellAddinPlugin.dll](./REA_EVIDENCE.md)（v251） | 已記錄相關組件證據；產品歸屬或官方 API 對照仍待處理。 (`product_component_evidence_only`) |
| `Mechanical` (`mechanical`) | 直接快照 | [mechanical_api.json](./mechanical_api.json)（2025 R1 v251）；[mechanical_core_api.json](./mechanical_core_api.json)（PyMechanical 0.13.2）；[mechanical_protocol_api.json](./mechanical_protocol_api.json)（ansys-api-mechanical 0.1.4：1 service、5 RPC、9 messages、18 fields） | [Mechanical DataModel; Ansys.Mechanical.Interfaces.dll; Ansys.Mechanical.DataModel.dll](./REA_EVIDENCE.md)（v251） | 清冊以產品 ID 對應快照；協定 schema 與 Python client 各自記錄，不代表宿主 API 完整或 runtime 可用。 (`direct_product_id`) |
| `Minerva` (`minerva`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `ModelCenter` (`modelcenter`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `Motion` (`motion`) | REA 組件證據 | — | [MotionAPI.dll](./REA_EVIDENCE.md)（v251） | 已記錄 managed metadata 候選；官方 API 對照與支援狀態仍待核對。 (`product_component_evidence_only`) |
| `MotorCAD` (`motorcad`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `optiSLang` (`optislang`) | 直接快照 | [optislang_api.json](./optislang_api.json)（1.6.1；類別 241、方法 1691、屬性 0、函式 133）<br>[optislang_core_api.json](./optislang_core_api.json)（unknown；類別 1、方法 18、屬性 9、函式 0） | — | 清冊以產品 ID 對應來源；快照僅涵蓋所列版本與範圍。 (`direct_product_id`) |
| `Polyflow` (`polyflow`) | REA 組件證據 | — | [Ans.Polyflow.dll](./REA_EVIDENCE.md)（v251） | 已記錄相關組件證據；產品歸屬或官方 API 對照仍待處理。 (`product_component_evidence_only`) |
| `PrimeMesh` (`primemesh`) | 直接快照 | [primemesh_api.json](./primemesh_api.json)（PyPrimeMesh 0.10.5）；[primemesh_protocol_api.json](./primemesh_protocol_api.json)（ansys-api-meshing-prime 0.2.0：1 service、7 RPC、10 messages、11 fields） | — | 協定 schema 描述 gRPC 傳輸介面；不代表產品 API 完整或 runtime 可用。 (`direct_product_id`) |
| `PyAnsys` (`pyansys`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `Q3D` (`q3d`) | REA 組件證據 | — | [Ans.Ansoft.Q3DExtractorAddinPlugin.dll](./REA_EVIDENCE.md)（v251） | 已記錄相關組件證據；產品歸屬或官方 API 對照仍待處理。 (`product_component_evidence_only`) |
| `Reaction_Chemkin` (`reaction_chemkin`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `Rigid_Body_Dynamics` (`rigid_body_dynamics`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `Rocky` (`rocky`) | PyAnsys SDK snapshot | [rocky_api.json](./rocky_api.json)（ansys-rocky-core 0.6.2；8 modules、11 classes、5 methods、1 property、16 functions） | — | 統計只含直接 AST 宣告且名稱不以底線開頭；SDK package 版本不代表 Rocky product release，官方支援狀態與宿主行為未確認。 (`direct_product_id`) |
| `SAF` (`saf`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `SCADE` (`scade`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `Scade_One` (`scade_one`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `Sherlock` (`sherlock`) | PyAnsys SDK 快照與 REA 組件證據 | [sherlock_core_api.json](./sherlock_core_api.json)（ansys-sherlock-core 2.1.4；25 modules、208 classes、241 methods、19 functions） | [Ans.Sherlock.Addin.dll](./REA_EVIDENCE.md)（v251） | SDK package version 不代表 Sherlock product release；公開支援狀態、官方 API 對照及宿主行為未確認。 (`direct_product_id`) |
| `SimAI` (`simai`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `SIwave` (`siwave`) | REA 組件證據 | — | [Ansys.Ansoft.SIwave.LibIronPythonCmd.dll](./REA_EVIDENCE.md)（v251） | 有名稱與型別可辨識的 managed metadata 候選；官方 API 對照及支援狀態未確認。 (`product_component_evidence_only`) |
| `Sound` (`sound`) | 直接快照 | [sound_api.json](./sound_api.json)（unknown；類別 2、方法 13、屬性 6、函式 0） | — | 清冊以產品 ID 對應來源；快照僅涵蓋所列版本與範圍。 (`direct_product_id`) |
| `SpaceClaim` (`spaceclaim`) | 直接快照 | [spaceclaim_api.json](./spaceclaim_api.json)（2025 R1 (v251)；類別 0、方法 2845、屬性 1551、函式 0） | [SpaceClaim.Api.V251.dll; SpaceClaim.Api.V251.Scripting.dll](./REA_EVIDENCE.md)（v251） | 清冊以產品 ID 對應來源；快照僅涵蓋所列版本與範圍。 (`direct_product_id`) |
| `Speos` (`speos`) | PyAnsys SDK 與 gRPC/protobuf snapshots，加上 REA 組件證據 | [speos_api.json](./speos_api.json)（ansys-speos-core 0.9.2；48 modules、197 classes、417 methods、246 properties、29 functions）<br>[speos_protocol_api.json](./speos_protocol_api.json)（ansys-api-speos 0.16.3；33 modules、372 classes、163 methods、697 properties） | [Optical Products/Speos/bin/ApipWrapper.dll](./REA_EVIDENCE.md)（v251） | 套件 metadata 例子同時出現 product version 2025.1、Docker image tag 261 與 AWP_ROOT251 本機路徑，版本線索不一致，產品相容性未知。SDK AST 與 protocol schema 均未經宿主驗證。 (`direct_product_id`) |
| `System_Coupling` (`system_coupling`) | REA 組件證據 | — | [SysC.AnsRpc.Wrapper.dll; SysC.SystemCouplingParticipant.dll（native PE exports）](./REA_EVIDENCE.md)（v251） | 已記錄 native export 候選；產品公開 API 映射、協定、簽名及 runtime 仍未確認。 (`product_component_evidence_only`) |
| `Thermal_Desktop` (`thermal_desktop`) | 待來源／映射 | — | — | v251 managed inventory 未找到名稱明確指向 Thermal Desktop 的組件；仍需產品安裝樹或官方介面來源。 (`not_assessed`) |
| `TurboGrid` (`turbogrid`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `TwinAI` (`twinai`) | 待來源／映射 | — | — | 尚未完成來源、版本或 API owner 盤點。 (`not_assessed`) |
| `Workbench` (`workbench`) | 直接快照 | [workbench_api.json](./workbench_api.json)（ansys-workbench-core 0.14.0）；[workbench_protocol_api.json](./workbench_protocol_api.json)（ansys-api-workbench 0.4.0） | — | Python SDK 與 transport protocol 分開記錄；未核對官方支援狀態或伺服器相容性。 (`direct_product_id`) |
| `Zemax` (`zemax`) | REA 組件證據 | — | [Zemax OpticStudio/ZOSAPI.dll; Zemax OpticStudio/ZOSAPI_Interfaces.dll](./REA_EVIDENCE.md)（v251） | 已記錄相關組件證據；產品歸屬或官方 API 對照仍待處理。 (`product_component_evidence_only`) |

## 尚未映射或支援狀態未確認的 v251 元件候選

下列 REA source keys 已納入 APIKB，但目前僅依靜態組件 metadata 建立候選索引，尚未確認公開 API、產品支援狀態或宿主行為。它們不計入產品 coverage mapping。

| 元件候選 | 安裝相對路徑 | APIKB source key | 證據 |
| --- | --- | --- | --- |
| Engineering Data Core | `Addins/EngineeringData/bin/Win64/Ans.EngineeringData.Core.dll` | `engineeringdata_core_rea` | [REA evidence](./REA_EVIDENCE.md) |
| Engineering Data DataProvider | `Addins/EngineeringData/bin/Win64/Ans.EngineeringData.DataProvider.dll` | `engineeringdata_dataprovider_rea` | [REA evidence](./REA_EVIDENCE.md) |
| DesignModeler Core | `Addins/DesignModeler/bin/Win64/Ans.DesignModeler.Core.dll` | `designmodeler_core_rea` | [REA evidence](./REA_EVIDENCE.md) |
| Material Designer Core | `Addins/MaterialDesigner/bin/Win64/Ans.MaterialDesigner.Core.dll` | `materialdesigner_core_rea` | [REA evidence](./REA_EVIDENCE.md) |
| TurboSystem AFDCore | `Addins/TurboSystem/bin/Win64/Ans.TurboSystem.AFDCore.dll` | `turbosystem_afd_core_rea` | [REA evidence](./REA_EVIDENCE.md) |
| TurboSystem CCDCore | `Addins/TurboSystem/bin/Win64/Ans.TurboSystem.CCDCore.dll` | `turbosystem_ccd_core_rea` | [REA evidence](./REA_EVIDENCE.md) |
| TurboSystem CPDCore | `Addins/TurboSystem/bin/Win64/Ans.TurboSystem.CPDCore.dll` | `turbosystem_cpd_core_rea` | [REA evidence](./REA_EVIDENCE.md) |
| TurboSystem RTDCore | `Addins/TurboSystem/bin/Win64/Ans.TurboSystem.RTDCore.dll` | `turbosystem_rtd_core_rea` | [REA evidence](./REA_EVIDENCE.md) |

## 版本與缺口處理

- 只有 snapshot 明確記錄產品 release 或 SDK version 時，才以該欄位作版本證據；`unknown` 不可推定為 2025 R1。
- 官方文件是否可檢索，另見 [機器可讀產品覆蓋清冊](./api_coverage.json)。文件已收錄不代表 API 已擷取。
- 不將 REA metadata 的 `public` access flag 解讀為官方支援狀態。Native export 只記錄 PE export table 可見名稱，不代表已知簽名或可呼叫性。
- 本索引不宣稱涵蓋所有 ANSYS 產品、版本或公開介面。來源不足或無法分析時，保留缺口並記錄需要的來源或產品映射。
