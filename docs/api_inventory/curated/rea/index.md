# REA v251 managed candidate index

This index covers 46 captured REA JSON snapshots. Together, they contain 12,456 class records and 96,357 MethodDef rows.

> These are static metadata rows. They can include non-public members. They do not establish product ownership, public API status, vendor support, or runtime behavior.
> Use [the product matrix](../../PRODUCT_API_MATRIX.md) for current product mapping and gaps. Use APIKB for member-level search.

## Snapshot summary

| APIKB source key | Assembly | Modules | Class records | MethodDef rows | Snapshot |
| --- | --- | ---: | ---: | ---: | --- |
| `acp_core_rea` | `ACP.dll` | 8 | 210 | 2172 | [JSON](../../acp_core_rea_api.json) |
| `act_core_rea` | `Ansys.ACT.Core.dll` | 51 | 1258 | 10243 | [JSON](../../act_core_rea_api.json) |
| `act_interfaces_rea` | `Ansys.ACT.Interfaces.dll` | 22 | 297 | 1621 | [JSON](../../act_interfaces_rea_api.json) |
| `additive_rea` | `Ansys.Api.Additive.dll` | 10 | 208 | 2314 | [JSON](../../additive_rea_api.json) |
| `ansysem_coredotnet_rea` | `Ansys.Ansoft.CoreDotNet.dll` | 6 | 26 | 169 | [JSON](../../ansysem_coredotnet_rea_api.json) |
| `api_discovery_rea` | `Infrastructure.ApiDiscoveryV251.dll` | 3 | 211 | 766 | [JSON](../../api_discovery_rea_api.json) |
| `api_geometry_rea` | `Infrastructure.ApiGeometryV251.dll` | 3 | 149 | 678 | [JSON](../../api_geometry_rea_api.json) |
| `aqwa_addin_rea` | `Ans.AQWA.Core.dll` | 13 | 290 | 3464 | [JSON](../../aqwa_addin_rea_api.json) |
| `aqwa_remote_itf_rea` | `Ans.AQWA.RemoteItf.dll` | 3 | 12 | 74 | [JSON](../../aqwa_remote_itf_rea_api.json) |
| `autodyn_rea` | `Ans.AUTODYN.DataModel.dll` | 1 | 24 | 242 | [JSON](../../autodyn_rea_api.json) |
| `cfx_addin_rea` | `Ans.CFX.CFXCore.dll` | 12 | 240 | 2505 | [JSON](../../cfx_addin_rea_api.json) |
| `designer_addin_rea` | `Ans.Ansoft.DesignerAddinPlugin.dll` | 1 | 2 | 11 | [JSON](../../designer_addin_rea_api.json) |
| `designxplorer_rea` | `Ans.DesignXplorer.PublicAPIs.dll` | 5 | 33 | 228 | [JSON](../../designxplorer_rea_api.json) |
| `discovery_collaboration_rea` | `Ansys.Collaboration.Api.dll` | 9 | 287 | 1202 | [JSON](../../discovery_collaboration_rea_api.json) |
| `discovery_gateway_rea` | `Ansys.Gateway.Api.dll` | 5 | 12 | 37 | [JSON](../../discovery_gateway_rea_api.json) |
| `discovery_geometry_rea` | `Ansys.Geometry.Api.dll` | 3 | 29 | 113 | [JSON](../../discovery_geometry_rea_api.json) |
| `discovery_onscale_rea` | `Ansys.OnScale.Api.dll` | 5 | 1074 | 9059 | [JSON](../../discovery_onscale_rea_api.json) |
| `discovery_physics_rea` | `Ansys.Physics.Api.dll` | 5 | 29 | 106 | [JSON](../../discovery_physics_rea_api.json) |
| `discovery_project_rea` | `Ansys.Project.Api.dll` | 6 | 101 | 424 | [JSON](../../discovery_project_rea_api.json) |
| `discovery_results_rea` | `Ansys.Results.Api.dll` | 5 | 47 | 179 | [JSON](../../discovery_results_rea_api.json) |
| `engineeringdata_rea` | `Ans.EngineeringData.DataModel.dll` | 2 | 39 | 400 | [JSON](../../engineeringdata_rea_api.json) |
| `fluent_addin_rea` | `Ans.Fluent.dll` | 11 | 482 | 7652 | [JSON](../../fluent_addin_rea_api.json) |
| `granta_mi_rea` | `Ansys.Apip.Client.dll` | 1 | 6 | 80 | [JSON](../../granta_mi_rea_api.json) |
| `hfss_addin_rea` | `Ans.Ansoft.HFSSAddinPlugin.dll` | 1 | 2 | 8 | [JSON](../../hfss_addin_rea_api.json) |
| `icepak_addin_rea` | `Ans.Icepak.Core.dll` | 13 | 115 | 1588 | [JSON](../../icepak_addin_rea_api.json) |
| `icepak_ansoft_addin_rea` | `Ans.Ansoft.IcepakAddinPlugin.dll` | 1 | 2 | 8 | [JSON](../../icepak_ansoft_addin_rea_api.json) |
| `lsdyna_interfaces_rea` | `Ansys.ACTLSDYNA.Interfaces.dll` | 2 | 8 | 69 | [JSON](../../lsdyna_interfaces_rea_api.json) |
| `materialdesigner_rea` | `Ans.MaterialDesigner.Wrapper.dll` | 2 | 6 | 115 | [JSON](../../materialdesigner_rea_api.json) |
| `maxwell_addin_rea` | `Ans.Ansoft.MaxwellAddinPlugin.dll` | 1 | 2 | 10 | [JSON](../../maxwell_addin_rea_api.json) |
| `mechanical_ansoft_addin_rea` | `Ans.Ansoft.MechanicalAddinPlugin.dll` | 1 | 2 | 8 | [JSON](../../mechanical_ansoft_addin_rea_api.json) |
| `mechanical_datamodel_rea` | `Ansys.Mechanical.DataModel.dll` | 34 | 1019 | 813 | [JSON](../../mechanical_datamodel_rea_api.json) |
| `mechanical_interfaces_rea` | `Ansys.Mechanical.Interfaces.dll` | 2 | 36 | 187 | [JSON](../../mechanical_interfaces_rea_api.json) |
| `meshing_addin_rea` | `Ans.Meshing.Core.dll` | 18 | 399 | 3925 | [JSON](../../meshing_addin_rea_api.json) |
| `motion_api_rea` | `MotionAPI.dll` | 3 | 7 | 36 | [JSON](../../motion_api_rea_api.json) |
| `polyflow_addin_rea` | `Ans.Polyflow.dll` | 6 | 283 | 3263 | [JSON](../../polyflow_addin_rea_api.json) |
| `q3d_addin_rea` | `Ans.Ansoft.Q3DExtractorAddinPlugin.dll` | 1 | 2 | 9 | [JSON](../../q3d_addin_rea_api.json) |
| `sherlock_addin_rea` | `Ans.Sherlock.Addin.dll` | 44 | 465 | 5357 | [JSON](../../sherlock_addin_rea_api.json) |
| `simplorer_addin_rea` | `Ans.Ansoft.SimplorerAddinPlugin.dll` | 2 | 5 | 17 | [JSON](../../simplorer_addin_rea_api.json) |
| `siwave_libironpythoncmd_rea` | `Ansys.Ansoft.SIwave.LibIronPythonCmd.dll` | 2 | 95 | 710 | [JSON](../../siwave_libironpythoncmd_rea_api.json) |
| `spaceclaim_core_rea` | `SpaceClaim.Api.V251.dll` | 16 | 3904 | 21426 | [JSON](../../spaceclaim_core_rea_api.json) |
| `turbosystem_ccd_rea` | `Ans.TurboSystem.CCDInterface.dll` | 1 | 1 | 243 | [JSON](../../turbosystem_ccd_rea_api.json) |
| `turbosystem_ccm_rea` | `Ans.TurboSystem.CCMInterface.dll` | 1 | 1 | 76 | [JSON](../../turbosystem_ccm_rea_api.json) |
| `units_rea` | `Ans.Units.DataModel.dll` | 3 | 13 | 63 | [JSON](../../units_rea_api.json) |
| `vista_tf_rea` | `Ans.VistaTF.DataModel.dll` | 6 | 96 | 1124 | [JSON](../../vista_tf_rea_api.json) |
| `zemax_zosapi_interfaces_rea` | `ZOSAPI_Interfaces.dll` | 45 | 919 | 13469 | [JSON](../../zemax_zosapi_interfaces_rea_api.json) |
| `zemax_zosapi_rea` | `ZOSAPI.dll` | 2 | 8 | 94 | [JSON](../../zemax_zosapi_rea_api.json) |

## Assembly evidence

- `acp_core_rea` — SHA-256 `441a04df502ce419540279c4a389f592306f49946f9e3e7c6205cb0adb10c49e`; MVID `e9bf8578-00b3-48ce-b089-7dbe2ab05e0c`; REA Evidence ID `ev_821ff672bbb6c7e195d7e57bd25703f1067fe70435c8091b8a14313b0902f067`.
- `act_core_rea` — SHA-256 `61f9c36f0ef405e004a5900efc4c3e52e12bdc972a0dc74c70bb7d50b1243748`; MVID `8fdcc48b-5659-4d61-bfaf-58253f7c2623`; REA Evidence ID `ev_f374772cb90eddac44164054ffd51f6c435f1be4afec8da04429cf7d17f7978b`.
- `act_interfaces_rea` — SHA-256 `bcd42394f08566f2ba97f506e9e47c7f34362efd5c8284285a4aea5db75c32d0`; MVID `c8fea0c5-fadc-410f-beb2-05891e93f28b`; REA Evidence ID `ev_95ebfb349467333ee3250d426d7d18942067c4260d61ab3f55a4347a376caa45`.
- `additive_rea` — SHA-256 `8351bd20a26f4c800049090a90870352796208ffd4880d4ccbb0675b1913f105`; MVID `1bbcdac1-ab57-40b4-890a-b654aefdf87b`; REA Evidence ID `ev_5c7a662ce281d8a0f47fb10d6fd2208d910d48660ef440e5997f80eafb686949`.
- `ansysem_coredotnet_rea` — SHA-256 `1c3854a230c82800db738db61da3e6570d72b160085e40289b36773fdf8ae06b`; MVID `a51f184d-ffec-446d-b547-b21b096eb75d`; REA Evidence ID `ev_56774b4b188bed717ee26d06ecc53705cb0f8582d819f133b6101906d58523a1`.
- `api_discovery_rea` — SHA-256 `2c40c7244138997c268c9d66312bbb1d0371082653669ce316b5d75c64691997`; MVID `f28799ba-69e5-46ae-b12e-27f50b63f660`; REA Evidence ID `ev_cec2f2048ef041b031b6fa03e96ae74585d42e19379d0a4574549ed31ea8e7b7`.
- `api_geometry_rea` — SHA-256 `bf9a302f0b78f8ca8f32a59a7623c7b73eb74aaab5167cc864f9fe58c9eccd76`; MVID `52d2c08a-5e95-4d7f-95e0-59d87f5b405d`; REA Evidence ID `ev_9d8b98b67c0e827c9b8b99fc24da87e41f1eac812cbd7dde6b07c782e02a8b32`.
- `aqwa_addin_rea` — SHA-256 `2733eb3c5b4e68ed05f74c76c4cda5a5eb0e85aa895b53bfa827d251d60c37aa`; MVID `24fc83bc-72cf-41a7-b725-7a6a53166748`; REA Evidence ID `ev_ec6ec94ac0298cfde397a2e3ce4827ffbf2e6b22cbd8a766bef5289afeb6b569`.
- `aqwa_remote_itf_rea` — SHA-256 `0751eb9e76fa77c897a42643ed0c31ebc95229c285f49de0e9414a040b1fa5e0`; MVID `453a71de-a1d7-4284-a0bb-b60fc48c4422`; REA Evidence ID `ev_b925106850ff1204878666c3dd8b9058963c74e5a5870420b291e983cbf858fb`.
- `autodyn_rea` — SHA-256 `0c195c4280cedd228ad73a9e9d4045d62b59fb40f8af83a4bddfd94753edb332`; MVID `004cc603-63cb-4596-89cb-01a69d88104a`; REA Evidence ID `ev_e5c123fc75d8a76417149215e78644377568b4f2b2ce3cd03751aaa646fcbca1`.
- `cfx_addin_rea` — SHA-256 `421e31ab499d1993a2520e353ef8e9871e0c0cd512fc25fd09905b50c440e34b`; MVID `d6f7081c-c12c-42ad-8bae-4e97bfce78ed`; REA Evidence ID `ev_5b1ce8ca5541a66590512c80cd6dfc5142c90644d4980e9657a5a1362a3645fb`.
- `designer_addin_rea` — SHA-256 `708e64d83d00d61a6393bdb74e60d16845823aa51f5a2305b3546f5e77e499bd`; MVID `d98d2791-9eed-4056-8216-8306c265a2ef`; REA Evidence ID `ev_2baa62f029b5e7df3d5cfa621c825be6fcd299ef0e2eac2beb35c59e1a672faf`.
- `designxplorer_rea` — SHA-256 `f2249c1ce824597444e993c793277a180528ab90d4b9bdb741ae57ef358df922`; MVID `4170aeef-388a-44da-8fe5-9e697afb2804`; REA Evidence ID `ev_7a554cb4ca6b1e91dc29f4f01197b5f24e80bb29921fcd779397d306749240b2`.
- `discovery_collaboration_rea` — SHA-256 `142cccb682c7613869c5d06608ac3eeacc7a399e6aec765b7a340b6ae55f8e73`; MVID `67a75d04-de69-47e2-87a2-f5ed8fa94675`; REA Evidence ID `ev_6fe465b848c1f6827927bf9b5bb92777ab303716dc29a457e2180bffc804b0dd`.
- `discovery_gateway_rea` — SHA-256 `657f9d5039b7e062db4dd9ad67bd00c70c8993cb713d500b206c29e5a637df66`; MVID `7e3b230d-887e-4505-961c-7ed3b15ed99b`; REA Evidence ID `ev_ceae69ecf15fa25826bd151860dedf794c40b5e56d333f4cb9746e7726ae8811`.
- `discovery_geometry_rea` — SHA-256 `4866343565cd738d079533abc19e0d5d4c76a5d4cb568553907e2d2982050a25`; MVID `4b3e892f-854b-4f5f-9897-379b182a389a`; REA Evidence ID `ev_08f75a05db1352d8c2671f90ccb45c8d40b8c0aff340085763bd5f73d02eefb0`.
- `discovery_onscale_rea` — SHA-256 `c23362dd0be272ccb48f4d5e6d2c0c58f6171b40cdaadd8b4b38944161647980`; MVID `696b1c4c-da2a-46a7-8f9b-2a7206109867`; REA Evidence ID `ev_44b31d5c4a82f1d3a8d38be0b4ae4a77da4e96e1d5c5e1498772e11c7df7b93f`.
- `discovery_physics_rea` — SHA-256 `78a04ae7973d17009717a6309e5bea1622150d53d1bd7d264722fd6f6b038073`; MVID `a70177e6-22c2-41ee-a624-cd75c6e8ad26`; REA Evidence ID `ev_45ae02a8e01148fa98245a65bc5aae66d940768bc92a17650f174171ff80b62f`.
- `discovery_project_rea` — SHA-256 `4133e9316e39598cf7c6a97d16f9ae3311dafb75df340639cd85e552fc6c0f4e`; MVID `df2caded-b668-421a-891c-0460478c235b`; REA Evidence ID `ev_870242a1ba1e12f08f34fa1746952d2d0b2a1106f85f4b51cb0ec3206cde5547`.
- `discovery_results_rea` — SHA-256 `d3cb87be1e292d34705bb1576fa88dbdf9233302c686db6934c700456f0c2130`; MVID `c2a737c4-9a82-4055-ad29-8c6630d7b77f`; REA Evidence ID `ev_92d1ae539084d2abb885782a8baa61c1435b1cc6305ae915a97810d027b6eeaa`.
- `engineeringdata_rea` — SHA-256 `70bb92bb6c7ea1178ae6377f9992f4685886ac23b9ca40ce0ec93bd39d426251`; MVID `d7a87bd8-cc9e-4f1c-8ace-6ee800628160`; REA Evidence ID `ev_e803ac2182f6d6bf3de1eee1a3894ac1a34bede584709260cdcc71f1e9357a85`.
- `fluent_addin_rea` — SHA-256 `e1742d642bab37ebe26aa147ac4aa4d5a034b26c534da7e963ec18bd9e4f96b4`; MVID `30798882-87b3-442f-b9bc-a784f287950d`; REA Evidence ID `ev_02ab1aa25aa1b97e07ea9d7c4e93cb4cf3c944605d9fe985435f53ed187a85df`.
- `granta_mi_rea` — SHA-256 `b243db8f5e75ef0453ead5dfd58bce686d66ee6f1130f19c02128ac7c537bda1`; MVID `ee7ecc0b-0c05-4fc5-8b71-9267041dd4dd`; REA Evidence ID `ev_e5c44ef9e3b4ac8cb4335e0a6adca6bd8a91f8a82649c9a2b518c2a40a3d0ebf`.
- `hfss_addin_rea` — SHA-256 `0b042c5cb5a2df9a191b45e5f4b0b4201e9fab1717058a6eb80e566892f61685`; MVID `ef78f98a-e63d-4916-891e-570d2a2b7a0a`; REA Evidence ID `ev_a34a6017824741cb2271983bcbcbf47a906fbd9263ec27e1386ed005768c7a5b`.
- `icepak_addin_rea` — SHA-256 `1e5c4b058a6ec33ff077fe8633605e8157b632aeaa90dc7d84621895163b8bc8`; MVID `80d97523-9c84-4df1-91f3-b19a1096471a`; REA Evidence ID `ev_1ee942b070e6c88dcac9cc4ab08276757e9db998faae78901d874e63e25443e2`.
- `icepak_ansoft_addin_rea` — SHA-256 `d06fcf8943e6234ecda588a082923f86481cde3097a0244c98c12840f8b8d85f`; MVID `9fb03e80-474f-4a22-af14-c593e4c6288f`; REA Evidence ID `ev_e685e48aa242f42fefccc4bc30ffdc2899a1af2ce4bb606ccb7425f12f53f2ba`.
- `lsdyna_interfaces_rea` — SHA-256 `01e7d0a3f0bb56668665fb3ad90f198666373a40a7c56166701069f4c3fd8120`; MVID `68001726-0e3b-4c1c-b1eb-4afd5b70bdce`; REA Evidence ID `ev_45f58ec39e3b6e09ff1773639f0d10b2d10e8f2dd0c57124a88fa669e4a2e1c7`.
- `materialdesigner_rea` — SHA-256 `bdb3b0c299de464e5da87a55675591145aed96838a06bf8090044d3920d7f6a9`; MVID `05fb2510-d57d-4c25-9dae-7daf611b2922`; REA Evidence ID `ev_f6ed1ef74be4bbbc4e2d77699e7e83217f1502359489dff1d6d0672c6d207c4c`.
- `maxwell_addin_rea` — SHA-256 `01d40fa16190805089990a102541ca3c786ed45ea2374b4d3d16e7fe4a89fa37`; MVID `53e45b29-27d4-49bf-9b41-0c5b7a8896ab`; REA Evidence ID `ev_de29863d9004012d5c0aa7113d6107c674d56460d1c881e4cfacc6338166b24f`.
- `mechanical_ansoft_addin_rea` — SHA-256 `ce022de4b1ecd8ce5a3064548c777739d50608f249e53d741329209998bb1f91`; MVID `cf2ef528-f65d-4e08-bb98-ef82ab0badc2`; REA Evidence ID `ev_f5467182c9d66994d899e33c2304861032bf7af4712757942573aeb3afb41e6d`.
- `mechanical_datamodel_rea` — SHA-256 `c3a8de009f71f8d7a8a67a870d2c6a1273d7455d87c1536221c4178486281435`; MVID `90519b63-186f-4533-9899-575ad499c6e7`; REA Evidence ID `ev_4e53de05f4e13f6a507df9d24f5fd5abed5f060b712e6b52e5dd798aa5063ea5`.
- `mechanical_interfaces_rea` — SHA-256 `3bb2c691b4853ad20d7f59505370839fbf27e01c2ac36af35257c393046fa54c`; MVID `84f499b0-f0fa-4f4c-9053-25c80f5e1492`; REA Evidence ID `ev_9bdf4417101c3b8dbff148342573fe3b5831237293637e484d8ffdde25c21df8`.
- `meshing_addin_rea` — SHA-256 `bbc9d3b9216e26097c6a726ad5249c7f406ebaf3843a5a31fc9750a3a9390356`; MVID `fd294b54-b266-4a9e-8c4c-1537510abe72`; REA Evidence ID `ev_4c59f1b00d1953fc40f6501246dd1cd8b8bce13b67d71914f416df9941802845`.
- `motion_api_rea` — SHA-256 `16f4d9ea21db2dfd54a4f35cb24e8da4ca948aa31f17b4cf53b0f50776ba0908`; MVID `42af1136-5856-4d26-b8aa-3112c2d5f3e1`; REA Evidence ID `ev_4afc0b4c875028a3b73040b00f2847c87dcb44aba2c7ae1891df06ed8a213ca4`.
- `polyflow_addin_rea` — SHA-256 `2b40cc3cc511170dfb63f4fb6b233750899b3ad1d7b81fcea536f9ca7739e19e`; MVID `3cfa1cf7-9403-4755-bd8f-c7ed3bf26f51`; REA Evidence ID `ev_d540d49f47827d1d26472f8f9e4a33988c26f32233aa4e63f1ef6ebd162103fd`.
- `q3d_addin_rea` — SHA-256 `152288642233e5aed659424f64138c12833647f94a994782bfa4053e70f7db9b`; MVID `3f884677-04f6-4b41-a4e9-40f66e5dd28d`; REA Evidence ID `ev_6460dfe92cdba68cbc85605adc2b4554a71289bedbfed085edd4c8cc06198123`.
- `sherlock_addin_rea` — SHA-256 `50e7b2d3bf8f00a976206ed7026c211f22f79cd7a775e996bd10efffbff01c11`; MVID `4a63eb54-86b8-4406-bc55-c88ea89e439b`; REA Evidence ID `ev_c8068896ce4c32b935f91f820680f51b1fc98549cf660adcfb9df4320c797e62`.
- `simplorer_addin_rea` — SHA-256 `bba079e08078996e1ffeb7491234732e673bd8365dadcde52cfd520efeab3088`; MVID `02dd607e-0fb9-4681-bfd4-39ce62e72f7f`; REA Evidence ID `ev_c652559083b9c565bd888b2be7cd86bd439eb1571e7b627c74922e3ebe2caee1`.
- `siwave_libironpythoncmd_rea` — SHA-256 `73b7de096fabf53f18293248706082eef982f3d6a7ee3e05e9395165da5aec8d`; MVID `d4c1ce51-265b-46e1-8c51-90604ba9dbe6`; REA Evidence ID `ev_7dfa98fb8636c8d57b384efde9161101582f658ebb548d390171c0cef5b538db`.
- `spaceclaim_core_rea` — SHA-256 `329adf81f2678da5ffaf671a10691ec6cb41963b92f652f2baaa555646a0b55d`; MVID `df791fca-9ae8-4699-98d4-a6e792f098bf`; REA Evidence ID `ev_1ff332940176d8fd198d0005264756f2ae91929b8c01d558ec4f029788de79fd`.
- `turbosystem_ccd_rea` — SHA-256 `9fc49bfeff27c31fdac05278d3447cb1ac6b4953661ccad360b864ff706a0908`; MVID `2f302501-30ae-4f91-8e0d-cfca2da245df`; REA Evidence ID `ev_555e2c61a984672dcd78aeee90c8ca070e19ab380a0a8ef1881b014bb9acebec`.
- `turbosystem_ccm_rea` — SHA-256 `f89e4afba2eebbdc202f254bddc67043657fd635435a5427d7afb53c91b57c53`; MVID `a8bb0268-da89-4bba-927a-0382bccd2d4a`; REA Evidence ID `ev_4aeb1dd7fcbd77a6e0b885610698768af5547e9d745e1f59154b7999450f1864`.
- `units_rea` — SHA-256 `679ffda588d077c61995b29e75632c9d33f9ea07c4fa7e187cd5c2cb038c4257`; MVID `76e9a67a-ad49-4fb2-88f8-f171d43f50c7`; REA Evidence ID `ev_59c603b7f0758dec5397700d165871320e493530bf166c5368f5a29130941e63`.
- `vista_tf_rea` — SHA-256 `8c12df7c9328003226c25df297f125e687fa02e747454259f0f6dce38c65a9e5`; MVID `366d7f58-a980-474c-85e6-53d425ae0e94`; REA Evidence ID `ev_599202df788c66f1286e25b175a564dd18a283e505b529eccd40cf118284e282`.
- `zemax_zosapi_interfaces_rea` — SHA-256 `eb18966f82c76821ee310c21c9bafa137b34e2e7fafe2dde6041a796187371a9`; MVID `15f830bc-ee7d-4c86-8059-ec0011ec59f9`; REA Evidence ID `ev_91895470bb640045126d4e5ccce806f4ab315895ad7303225a3fc74eacc094c8`.
- `zemax_zosapi_rea` — SHA-256 `573d6b7dda9013c0e2b1448658794ee033afc6c4f01c49c83b9b2823dcd5270c`; MVID `ab95b788-961c-4b4b-9ef0-8e71ad169685`; REA Evidence ID `ev_dde9d2ecc2d876859b46e1e02bd514ed4573b9e9eaec10a393216f4bff99d6a4`.

## Regenerate this index

```powershell
python scripts/api_extraction/render_rea_source_index.py
```
