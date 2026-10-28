# REA v251 靜態組件證據

記錄日期：2026-10-28。主候選清冊位於被忽略的 `.audit/repo-restructure/rea-managed-v251/`，保存 47 個 REA 結果，其中 42 個 `normalized_result.metadata.status=complete`、5 個為 `absent`。另補充分析 ACP、AQWA、Motion 與 SIwave managed 組件，詳見「額外產品 managed 候選」段落。另有 23 個 DPF DLL 與三個 Lumerical API DLL 的獨立掃描，見本文件後段。另有 DPF、CFX、System Coupling、ROM、AnsysEM 與 Speos 的 PE 元件分析記錄於本文件後段；這些是本機 v251 樣本，不推定其他產品或版本的覆蓋。

分析使用 REA CLI `6.0.0` 的 `inspect-managed-members`。provider 為 `rea-dotnet-static`（REA managed static analysis provider），provider version 為 `1`。已處理的 managed 組件 metadata 回報 `complete`、version `v4.0.30319`；System Coupling 的 ANSRPC wrapper 與 participant component 均沒有 CLI metadata。這些狀態只描述檔案解析範圍，不表示 API 完整或受支援。

## 組件識別

| 欄位 | Mechanical DataModel | SpaceClaim Scripting |
| --- | --- | --- |
| 可攜來源路徑 | `$env:AWP_ROOT251\aisol\bin\winx64\Ansys.Mechanical.DataModel.dll` | `$env:AWP_ROOT251\scdm\SpaceClaim.Api.V251.Scripting.dll` |
| Module 名稱 | `Ansys.Mechanical.DataModel.dll` | `SpaceClaim.Api.V251.Scripting.dll` |
| 檔案大小（bytes） | 443,776 | 1,909,440 |
| PE architecture | `x86` | `x86_64` |
| MVID | `90519b63-186f-4533-9899-575ad499c6e7` | `06a113f3-00bd-40c2-b02c-53ee8e758a32` |
| SHA-256 | `c3a8de009f71f8d7a8a67a870d2c6a1273d7455d87c1536221c4178486281435` | `9f5f3d03675bfc1d62e6fbf0244c9473c5e861fcacc3242028b329350e268261` |

REA Evidence ID：

- Mechanical：`ev_4e53de05f4e13f6a507df9d24f5fd5abed5f060b712e6b52e5dd798aa5063ea5`
- SpaceClaim：`ev_d458c1dfc8a5f9b5483e8a9fecd1f3a3d27157d38865491804f7d17308f31b4a`

這些 ID 識別本次分析結果，並非可下載的永久網址。REA 將 token 身分標記為 `build-local`，後續比對須同時核對組件 SHA-256 與 MVID。

## Metadata 計數

下列數值直接取自 `normalized_result.metadata.table_row_counts`。

| Metadata table | Mechanical DataModel | SpaceClaim Scripting |
| --- | ---: | ---: |
| `TypeDef` | 1,020 | 1,912 |
| `MethodDef` | 813 | 9,374 |
| `Field` | 6,270 | 4,200 |
| `Property` | 258 | 1,784 |
| `Event` | 2 | 8 |
| `AssemblyRef` | 14 | 46 |

`TypeDef` 和 `MethodDef` 是組件 metadata 列數，可能包含內部、巢狀、編譯器產生的型別及屬性存取方法。它們不能直接當作公開、穩定或可供使用者呼叫的 API 數量。`metadata.status=complete` 僅描述本次 metadata 解析狀態，不代表產品 API 字典完整。

## 重跑與證據限制

在 `AWP_ROOT251` 指向相同安裝根目錄的 PowerShell 執行：

```powershell
rea inspect-managed-members "$env:AWP_ROOT251\aisol\bin\winx64\Ansys.Mechanical.DataModel.dll" --format md --token-limit 1200
rea inspect-managed-members "$env:AWP_ROOT251\scdm\SpaceClaim.Api.V251.Scripting.dll" --format md --token-limit 1200
```

初始分析只保留輸出前段；2026-10-28 另以 `--format json` 保存完整正規化成員結果，原始 JSON 位於本機忽略目錄 `.audit/repo-restructure/rea-members-20261028/`，不納入版本控制。REA Evidence ID 與檔案 SHA-256、組件 SHA-256/MVID 一併記錄於下方比對。REA 的 token 身分為 build-local，原始 JSON 不可脫離對應組件身分使用。

本次分析只解析檔案 metadata，未載入、反射或執行目標組件。相依組件的實際解析與載入行為未驗證。尚未逐項分類公開／未公開 API，也未將這批 REA 成員與官方文件、既有快照或 APIKB 逐項合併。這次沒有執行 ANSYS、求解或 runtime 行為驗證。

## AnsysEM v251 共用 COM scripting 組件

本節記錄本機 `AnsysEM` 目錄中的 `Ansys.Ansoft.CoreCOMScripting.dll`。REA 解析了 managed metadata；這只表示此組件可靜態解析，不證明其成員是公開、受支援或屬於 HFSS、Maxwell 等特定產品 API。

| 欄位 | 值 |
| --- | --- |
| 可攜來源路徑 | `$env:AWP_ROOT251\AnsysEM\Ansys.Ansoft.CoreCOMScripting.dll` |
| Module 名稱 | `Ansys.Ansoft.CoreCOMScripting.dll` |
| 檔案大小（bytes） | 128,000 |
| PE architecture | `x86_64` |
| MVID | `5a997235-f5ca-4346-a5a2-83b163604336` |
| SHA-256 | `38d7034798ced5586753b6c24e51205fdbacfac3cc48b3abd376510acc2dccfb` |

REA Evidence ID：`ev_b9e778411a350e02ba034d3eebda20fb5147f4091899a4f3c9bd55f9b02a1e4b`。此 ID 是本次分析識別值；後續比對須同時核對組件 SHA-256 與 MVID。

REA `inspect-managed-members` 回報 provider `rea-dotnet-static` version `1`，`metadata.status=complete`、metadata version `v4.0.30319`。metadata table row counts 包含 `TypeDef=66`、`MethodDef=586`、`Property=79`、`Field=215`、`Param=3201`、`AssemblyRef=7`。這些是 metadata table 列數，不等於公開 API 數量。篩選後可見型別包含 `Ansys.Ansoft.Testing` 及 `Ansys.Ansoft.CoreCOMScripting` 命名空間；目前沒有把 REA 成員逐項映射到官方 API reference 或既有 snapshot。

### 官方文件的宿主相依證據（v261）

本機 2026 R1 官方 scripting guides 的範例程式均載入 `Ansys.Ansoft.CoreCOMScripting`，並同時載入 `DesktopPlugin`、`PluginCoreDotNet`，以 `ScriptEnv.Initialize('Ansoft.ElectronicsDesktop.<version>')` 取得 `oDesktop`：

| 產品文件 | 範例所在 PDF 頁 | 範例上下文 |
| --- | ---: | --- |
| HFSS Scripting Guide（本機 `ANSYS_Document/HFSS/v261/manuals/HFSSScriptingGuide.pdf`） | 2156–2157 | Electronics Desktop waveguide Python script |
| Q3D Extractor Scripting Guide（本機 `ANSYS_Document/Q3D/v261/manuals/Q3D ExtractorScriptingGuide.pdf`） | 1749–1750 | Electronics Desktop waveguide Python script |
| Icepak Scripting Guide（本機 `ANSYS_Document/Icepak/v261/manuals/IcepakScriptingGuide.pdf`） | 1285–1286 | Electronics Desktop waveguide Python script |

這些例子把組件用途連到 HFSS、Q3D、Icepak 文件中的 Electronics Desktop scripting host；足以支持它是跨產品腳本宿主相依的證據，不能據此宣稱 DLL 的所有成員是這些產品的公開 API。三份 v261 guide 範例的 `desktopVersion` 變數硬編碼為 `2024.2`，所以文件版次不能當成範例已在 v261 runtime 驗證的證據。REA 型別的公開狀態、支援承諾及逐成員產品映射仍未確認。

以 `AWP_ROOT251` 指向同一安裝根目錄的 PowerShell 重跑：

```powershell
rea inspect-managed-members "$env:AWP_ROOT251\AnsysEM\Ansys.Ansoft.CoreCOMScripting.dll" --format md --token-limit 1200
```

本次只保留輸出前段與型別摘要；REA 顯示完整報告約 154,337 tokens，未保存完整報告或全量 JSON。未載入或執行目標組件，也未驗證相依解析、runtime 行為、公開狀態或產品映射；未執行 ANSYS 或求解。

### AnsysEM CoreDotNet 共用元件（v251，2026-10-28）

另對 `AnsysEM\Ansys.Ansoft.CoreDotNet.dll` 執行 REA 靜態 metadata 擷取。元件名稱及命名空間顯示其為 AnsysEM 共用 .NET 元件；目前沒有官方文件證據可將其所有成員映射為 HFSS、Maxwell、Q3D 或 Icepak 的產品 API。

| 欄位 | 值 |
| --- | --- |
| 可攜來源路徑 | `$env:AWP_ROOT251\AnsysEM\Ansys.Ansoft.CoreDotNet.dll` |
| 檔案大小（bytes） | 26,112 |
| PE architecture | `x86_64` |
| MVID | `a51f184d-ffec-446d-b547-b21b096eb75d` |
| SHA-256 | `1c3854a230c82800db738db61da3e6570d72b160085e40289b36773fdf8ae06b` |
| REA Evidence ID | `ev_56774b4b188bed717ee26d06ecc53705cb0f8582d819f133b6101906d58523a1` |

REA `inspect-managed-members` 回報 provider `rea-dotnet-static` version `1`、metadata 狀態 `complete`、metadata version `v4.0.30319`。metadata table 有 27 個 `TypeDef`、169 個 `MethodDef`、11 個 `Property`、34 個 `Field`、201 個 `Param` 及 4 個 `AssemblyRef`。型別集中於 `Ansys.Ansoft.CoreDotNet`、`.Collections`、`.Util`、`.Services` 與 `.IO`。這些數量是組件 metadata 列數，不能視為公開、穩定或受支援 API 數量。

完整 JSON 僅保留在本機忽略路徑 `.audit/repo-restructure/rea-managed-v251/Ansys.Ansoft.CoreDotNet.json`，大小 928,720 bytes，SHA-256 `d93ee43f1d597e06814f5917e829548bddbab7615a389859e8ca7b4e33a1babc`。REA 未載入或執行目標組件。尚未分類成員可見性與支援狀態，也未逐項對照官方文件、SDK 或 API snapshot；本摘要公開散布權仍須按 [公開發佈檢查](../maintenance/PUBLICATION_REVIEW.md)審查。

### SpaceClaim v251 核心 API 組件（2026-10-28）

SpaceClaim Scripting 組件之外，安裝目錄另有核心 `SpaceClaim.Api.V251.dll`。下列 REA 結果是該核心組件的獨立證據，不與 `SpaceClaim.Api.V251.Scripting.dll` 快照合併。metadata 完整只代表解析成功，不證明下列成員都公開、受支援或可由 scripting host 呼叫。

| 欄位 | 值 |
| --- | --- |
| 可攜來源路徑 | `$env:AWP_ROOT251\scdm\SpaceClaim.Api.V251\SpaceClaim.Api.V251.dll` |
| 檔案大小（bytes） | 2,308,288 |
| PE architecture | `x86_64` |
| MVID | `df791fca-9ae8-4699-98d4-a6e792f098bf` |
| SHA-256 | `329adf81f2678da5ffaf671a10691ec6cb41963b92f652f2baaa555646a0b55d` |
| REA Evidence ID | `ev_1ff332940176d8fd198d0005264756f2ae91929b8c01d558ec4f029788de79fd` |

REA `inspect-managed-members` 回報 provider `rea-dotnet-static` version `1`、metadata 狀態 `complete`、metadata version `v4.0.30319`。metadata table 有 3,905 個 `TypeDef`、21,426 個 `MethodDef`、5,382 個 `Property`、7,011 個 `Field`、15,580 個 `Param`、126 個 `Event` 及 58 個 `AssemblyRef`。這些是 metadata 列數，不是公開 API 計數。

完整 REA JSON 僅保存於本機忽略路徑 `.audit/repo-restructure/rea-managed-v251/SpaceClaim.Api.V251.json`，大小 97,153,204 bytes，SHA-256 `d78233688b8375f3180030bdf775f90d32318a4a66366a2e5d4eede261059195`。未載入或執行目標組件，未比對官方 API reference。此核心組件已轉成 `spaceclaim_core_rea_api.json` 並以 APIKB key `spaceclaim_core_rea` 索引。快照包含 3,904 個 class records 與 21,426 個 MethodDef rows，大小 8,820,851 bytes，SHA-256 `f613814f571716a9df54298d3eaefe9b6de509b55ed9183d06f04c8305af2ede`；APIKB source row 同時保存 assembly SHA 與 REA Evidence ID。直接簽名對照與公開散布前的權限審查仍待處理，詳見[公開發佈檢查](../maintenance/PUBLICATION_REVIEW.md)。

### ACT 共用介面組件（v251，2026-10-28）

`Ansys.ACT.Interfaces.dll` 提供 ACT 共用介面。它不是單一產品的完整 API 清冊，產品實際支援範圍仍需按各 extension 和官方文件判定。

| 欄位 | 值 |
| --- | --- |
| 可攜來源路徑 | `$env:AWP_ROOT251\Addins\ACT\bin\Win64\Ansys.ACT.Interfaces.dll` |
| 檔案大小（bytes） | 127,168 |
| PE architecture | `x86` |
| MVID | `c8fea0c5-fadc-410f-beb2-05891e93f28b` |
| SHA-256 | `bcd42394f08566f2ba97f506e9e47c7f34362efd5c8284285a4aea5db75c32d0` |
| REA Evidence ID | `ev_95ebfb349467333ee3250d426d7d18942067c4260d61ab3f55a4347a376caa45` |

metadata version 為 `v4.0.30319`，狀態 `complete`。metadata table 有 298 個 `TypeDef`、1,621 個 `MethodDef`、682 個 `Property`、428 個 `Field`、1,147 個 `Param` 及 8 個 `AssemblyRef`。命名空間涵蓋 ACT Analysis、DataModel、Geometry、Mesh、Post、Project、Reporting、System、UserInterface、Wizard 與 Workflow。完整 JSON 保留於本機忽略路徑 `.audit/repo-restructure/rea-managed-v251/Ansys.ACT.Interfaces.json`，大小 3,799,169 bytes，SHA-256 `a0afbaa49e8550ea82ae94d96abc8443934e08e030187a354240bbe26ed71b42`。REA 未載入或執行目標組件，成員支援狀態未分類。

### LS-DYNA ACT 介面組件（v251，2026-10-28）

`Ansys.ACTLSDYNA.Interfaces.dll` 是 Mechanical ACT extension 的介面組件。此證據只涵蓋該介面，不涵蓋 LS-DYNA solver、keyword deck 或 LS-PrePost API。

| 欄位 | 值 |
| --- | --- |
| 可攜來源路徑 | `$env:AWP_ROOT251\Addins\ACT\extensions\LSDYNA\Ansys.ACTLSDYNA.Interfaces.dll` |
| 檔案大小（bytes） | 22,208 |
| PE architecture | `x86_64` |
| MVID | `68001726-0e3b-4c1c-b1eb-4afd5b70bdce` |
| SHA-256 | `01e7d0a3f0bb56668665fb3ad90f198666373a40a7c56166701069f4c3fd8120` |
| REA Evidence ID | `ev_45f58ec39e3b6e09ff1773639f0d10b2d10e8f2dd0c57124a88fa669e4a2e1c7` |

metadata version 為 `v4.0.30319`，狀態 `complete`。metadata table 有 9 個 `TypeDef`、69 個 `MethodDef`、1 個 `Property`、10 個 `Field`、90 個 `Param` 及 26 個 `ImplMap`。完整 JSON 保留於本機忽略路徑 `.audit/repo-restructure/rea-managed-v251/Ansys.ACTLSDYNA.Interfaces.json`，大小 245,911 bytes，SHA-256 `9fa46f60b8f56494093ca04ea69c2ceb2ef6f3236322f4971f7c7a89c7b4e464`。REA 未載入或執行目標組件，未逐項對照官方 LS-DYNA API 文件。

### Additive service API 組件（v251，2026-10-28）

REA 可解析 `Ansys.Api.Additive.dll` 的 managed metadata。此 DLL 位於 Additive server 目錄；metadata 中有 service API 命名空間，但目前未對照官方 reference 或 server protocol，不把全部成員當作使用者可呼叫的 Additive API。

| 欄位 | 值 |
| --- | --- |
| 可攜來源路徑 | `$env:AWP_ROOT251\Additive\additiveserver\Ansys.Api.Additive.dll` |
| 檔案大小（bytes） | 316,928 |
| PE architecture | `x86` |
| MVID | `1bbcdac1-ab57-40b4-890a-b654aefdf87b` |
| SHA-256 | `8351bd20a26f4c800049090a90870352796208ffd4880d4ccbb0675b1913f105` |
| REA Evidence ID | `ev_5c7a662ce281d8a0f47fb10d6fd2208d910d48660ef440e5997f80eafb686949` |

metadata version 為 `v4.0.30319`，狀態 `complete`。metadata table 有 209 個 `TypeDef`、2,314 個 `MethodDef`、568 個 `Property`、1,045 個 `Field`、1,174 個 `Param` 及 4 個 `AssemblyRef`。完整 JSON 保留於本機忽略路徑 `.audit/repo-restructure/rea-managed-v251/Ansys.Api.Additive.json`，大小 12,658,245 bytes，SHA-256 `6bfc35d98afd8ce622a9af1c492de1eb19df04e573a56f8846660817a904bcf9`。REA 未載入或執行目標組件，公開狀態和 protocol 仍未確認。

### 其他 v251 managed 組件（2026-10-28）

本批新增四個 managed assembly 的 REA 靜態 metadata。它們來自不同 ANSYS 安裝子目錄；除 Mechanical Interfaces 外，尚未將其產品 ID 與官方文件介面建立可追溯映射。組件名稱、metadata 計數和命名空間不等同公開 API 分類。

| 組件 | 可攜來源路徑 | bytes | MVID | Metadata：TypeDef / MethodDef / Property | Assembly SHA-256 | REA Evidence ID |
| --- | --- | ---: | --- | ---: | --- | --- |
| AUTODYN DataModel | `$env:AWP_ROOT251\Addins\AUTODYN\bin\Win64\Ans.AUTODYN.DataModel.dll` | 63,168 | `004cc603-63cb-4596-89cb-01a69d88104a` | 25 / 242 / 64 | `0c195c4280cedd228ad73a9e9d4045d62b59fb40f8af83a4bddfd94753edb332` | `ev_e5c123fc75d8a76417149215e78644377568b4f2b2ce3cd03751aaa646fcbca1` |
| DesignXplorer PublicAPIs | `$env:AWP_ROOT251\Addins\DesignXplorer\bin\Win64\Ans.DesignXplorer.PublicAPIs.dll` | 32,448 | `4170aeef-388a-44da-8fe5-9e697afb2804` | 34 / 228 / 91 | `f2249c1ce824597444e993c793277a180528ab90d4b9bdb741ae57ef358df922` | `ev_7a554cb4ca6b1e91dc29f4f01197b5f24e80bb29921fcd779397d306749240b2` |
| Engineering Data DataModel | `$env:AWP_ROOT251\Addins\EngineeringData\bin\Win64\Ans.EngineeringData.DataModel.dll` | 97,984 | `d7a87bd8-cc9e-4f1c-8ace-6ee800628160` | 40 / 400 / 88 | `70bb92bb6c7ea1178ae6377f9992f4685886ac23b9ca40ce0ec93bd39d426251` | `ev_e803ac2182f6d6bf3de1eee1a3894ac1a34bede584709260cdcc71f1e9357a85` |
| Mechanical Interfaces | `$env:AWP_ROOT251\aisol\bin\winx64\Ansys.Mechanical.Interfaces.dll` | 30,512 | `84f499b0-f0fa-4f4c-9053-25c80f5e1492` | 37 / 187 / 71 | `3bb2c691b4853ad20d7f59505370839fbf27e01c2ac36af35257c393046fa54c` | `ev_9bdf4417101c3b8dbff148342573fe3b5831237293637e484d8ffdde25c21df8` |

四個元件均為 `x86`、metadata version `v4.0.30319`，REA metadata 狀態為 `complete`。完整 JSON 僅存於本機忽略目錄 `.audit/repo-restructure/rea-managed-v251/`：`Ans.AUTODYN.DataModel.json`（1,528,445 bytes，SHA-256 `c5c5c5cc79a7e78ee4eda65358c808618f669954f8b809092b59b3bae3723181`）、`Ans.DesignXplorer.PublicAPIs.json`（412,802 bytes，SHA-256 `f57c156a51a70ce70009978c4f088f0ceff5d6b14a4913ce1aa930bcb23b1da4`）、`Ans.EngineeringData.DataModel.json`（2,918,311 bytes，SHA-256 `a14fdcb0ef56fd12dd6552c5cc9e0bac5699bc785df19d4f7317276cbb5dc4fe`）及 `Ansys.Mechanical.Interfaces.json`（309,321 bytes，SHA-256 `4c5c2c13d66e5ac2579c580e9375e8c27829a753b2aada1d3fd7b79855af2fff`）。REA 未載入或執行這些組件；公開狀態、官方簽名對照和 runtime 可用性均未確認。

REA normalized output 保留 TypeDef、MethodDef、Field、MemberRef 等資料，但沒有輸出 TypeRef table。部分簽名以 `class:<rid>` 表示，且 MethodDef 沒有參數名稱。尚未建立可將這些 RID 解析為完整型別名稱的對照，也未把 metadata flags 分類為公開／非公開。因此目前不能把 raw metadata 直接轉成完整、易讀的 APIKB 簽名清冊。

### System Coupling RPC wrapper（v251，2026-10-28）

REA `inspect-managed-members` 對 `SysC.AnsRpc.Wrapper.dll` 回報 PE 格式、CLI metadata `absent`，因此本次無法讀取 .NET members。此結果不代表 wrapper 沒有 native API，也不代表 System Coupling 產品沒有 API。

| 欄位 | 值 |
| --- | --- |
| 可攜來源路徑 | `$env:AWP_ROOT251\SystemCoupling\runTime\winx64\bin\SysC.AnsRpc.Wrapper.dll` |
| 檔案大小（bytes） | 162,496 |
| SHA-256 | `82e247497aed2bfbd47048762c0861f1ac7c43b2663d5484d15bca105c015b96` |
| REA Evidence ID | `ev_c9ad1e83e9753c2370c51c01c052b80382c0c76ac6a0848fa53d7393f3cb368b` |
| 完整 JSON | 本機 `.audit/repo-restructure/rea-managed-v251/SysC.AnsRpc.Wrapper.json`，2,047 bytes，SHA-256 `dbbdb2c03865f60d15de3683ea1ac013aeb62736c549f9fc2ec89ebd91bb30c5` |

REA managed parser 未取得 .NET members。另以 LLVM `llvm-readobj 19.1.5` 讀取 PE export table，得到 36 個 export 名稱；Windows `dbghelp` 可由 36 個 decorated names 反修飾出 symbol-derived signatures。快照列於 [System Coupling native export 清冊](./system_coupling_rpc_native_exports_api.json)。這些資料不確認 ANSRPC protocol、產品 API 映射或 Ansys 支援狀態。

### System Coupling participant component（v251，2026-10-28）

REA `inspect-managed-artifact` 檢查 `SysC.SystemCouplingParticipant.dll` 時發現 PE 為 x86_64，但 CLI directory 不存在，`metadata.status=absent`。因此無法從此組件擷取 .NET TypeDef 或 MethodDef。這只描述檔案格式，不代表沒有 native interface。

| 欄位 | 值 |
| --- | --- |
| 可攜來源路徑 | `$env:AWP_ROOT251\\SystemCoupling\\runTime\\winx64\\bin\\SysC.SystemCouplingParticipant.dll` |
| 檔案大小（bytes） | 22,767,296 |
| SHA-256 | `8787c2a0c86ddceaa75846f709f99cd3ec3fafe606d8aa97191732de3dc8bd6b` |
| REA Evidence ID | `ev_3ece2435f90dfd19f22697a9164da80ef4c1c644098ca3f23e04701788e7e450` |

LLVM `llvm-readobj 19.1.5 --coff-exports` 讀到 743 個 export 名稱。Windows `dbghelp` 將 508 個 decorated symbol 轉成 symbol-derived signature 字串。這些字串是名稱修飾所編碼的型別提示，不是已驗證的呼叫簽名。快照列於 [System Coupling participant native export 清冊](./system_coupling_participant_native_exports_api.json)，APIKB 來源鍵為 `system_coupling_participant_native`。產品支援狀態、ABI/呼叫慣例與 runtime 行為尚未確認。

### 其他 v251 managed 組件：Granta MI、Material Designer、TurboSystem、Units 與 Vista TF

這六個組件都回報 managed metadata `complete`，但產品 API 的公開／支援狀態尚未與官方文件逐項對照。Granta MI 組件路徑可對應 coverage 產品 `granta_mi`；其餘組件先以獨立候選來源鍵保存，不推測它們對應哪個 coverage 產品 ID。

| 組件 | 可攜來源路徑 | bytes | TypeDef / MethodDef / Property | MVID | Assembly SHA-256 | REA Evidence ID |
| --- | --- | ---: | ---: | --- | --- | --- |
| Granta MI API client | `$env:AWP_ROOT251\Addins\Granta MI\Ansys.Apip.Client.dll` | 20,680 | 7 / 80 / 9 | `ee7ecc0b-0c05-4fc5-8b71-9267041dd4dd` | `b243db8f5e75ef0453ead5dfd58bce686d66ee6f1130f19c02128ac7c537bda1` | `ev_e5c44ef9e3b4ac8cb4335e0a6adca6bd8a91f8a82649c9a2b518c2a40a3d0ebf` |
| Material Designer wrapper | `$env:AWP_ROOT251\Addins\MaterialDesigner\bin\Win64\Ans.MaterialDesigner.Wrapper.dll` | 28,352 | 7 / 115 / 2 | `05fb2510-d57d-4c25-9dae-7daf611b2922` | `bdb3b0c299de464e5da87a55675591145aed96838a06bf8090044d3920d7f6a9` | `ev_f6ed1ef74be4bbbc4e2d77699e7e83217f1502359489dff1d6d0672c6d207c4c` |
| TurboSystem CCD interface | `$env:AWP_ROOT251\Addins\TurboSystem\bin\Win64\Ans.TurboSystem.CCDInterface.dll` | 26,816 | 2 / 243 / 150 | `2f302501-30ae-4f91-8e0d-cfca2da245df` | `9fc49bfeff27c31fdac05278d3447cb1ac6b4953661ccad360b864ff706a0908` | `ev_555e2c61a984672dcd78aeee90c8ca070e19ab380a0a8ef1881b014bb9acebec` |
| TurboSystem CCM interface | `$env:AWP_ROOT251\Addins\TurboSystem\bin\Win64\Ans.TurboSystem.CCMInterface.dll` | 19,648 | 2 / 76 / 38 | `a8bb0268-da89-4bba-927a-0382bccd2d4a` | `f89e4afba2eebbdc202f254bddc67043657fd635435a5427d7afb53c91b57c53` | `ev_4aeb1dd7fcbd77a6e0b885610698768af5547e9d745e1f59154b7999450f1864` |
| Units DataModel | `$env:AWP_ROOT251\Addins\Units\bin\Win64\Ans.Units.DataModel.dll` | 26,816 | 14 / 63 / 16 | `76e9a67a-ad49-4fb2-88f8-f171d43f50c7` | `679ffda588d077c61995b29e75632c9d33f9ea07c4fa7e187cd5c2cb038c4257` | `ev_59c603b7f0758dec5397700d165871320e493530bf166c5368f5a29130941e63` |
| Vista TF DataModel | `$env:AWP_ROOT251\Addins\VistaTF\bin\Win64\Ans.VistaTF.DataModel.dll` | 179,904 | 97 / 1,124 / 135 | `366d7f58-a980-474c-85e6-53d425ae0e94` | `8c12df7c9328003226c25df297f125e687fa02e747454259f0f6dce38c65a9e5` | `ev_599202df788c66f1286e25b175a564dd18a283e505b529eccd40cf118284e282` |

完整 JSON 僅保存於本機忽略目錄 `.audit/repo-restructure/rea-managed-v251/`：`Ansys.Apip.Client.json`（188,857 bytes，SHA-256 `bd41ba46b59d038e1bfd389ca731bc2e77cf3fb059051320e536a04f1362c8cc`）、`Ans.MaterialDesigner.Wrapper.json`（439,701 bytes，SHA-256 `38b1be1b6b88e3261378816cf53c88239e670a1575e4328d7e47343e830caee5`）、`Ans.TurboSystem.CCDInterface.json`（351,158 bytes，SHA-256 `0af27fe8c8b9022d18a6f7875a5d44c07ebc6addc16f1436cc8866ceb170247e`）、`Ans.TurboSystem.CCMInterface.json`（119,372 bytes，SHA-256 `1954818908c42538873b76530542ecb35a556652ad00c08e6572c93570710625`）、`Ans.Units.DataModel.json`（319,386 bytes，SHA-256 `cc32011e9b4f4479b0e3ff2539d6dc62d48f111b4ecc939cbaff7f9a60969e93`）及 `Ans.VistaTF.DataModel.json`（6,046,791 bytes，SHA-256 `5a4cce8c4c3ba036f191b08e8308b40494ca6bb1574bf3257bc58762b5dd59a4`）。REA 未載入或執行組件。

### ROM API PE（v251，managed metadata absent）

REA 將 `Rom.Api.dll` 分類為 PE，managed metadata status 為 `absent`。另以 LLVM `llvm-readobj 19.1.5` 讀取 381 個 native export 名稱。只有 decorated export `GetFactory` 可反修飾出 symbol-derived signature；其餘 export 名稱沒有函式簽名。快照列於 [ROM native export 清冊](./rom_api_native_exports_api.json)。這些名稱仍是靜態實作候選，不表示官方支援 API。

| 欄位 | 值 |
| --- | --- |
| 可攜來源路徑 | `$env:AWP_ROOT251\Addins\ROM\bin\Win64\Rom.Api.dll` |
| 檔案大小（bytes） | 1,284,288 |
| SHA-256 | `a408c7cb336d27fe9ab0b7e39187e69e9f64be41a8c5fc0a3bc38cd961958c5d` |
| REA Evidence ID | `ev_326576a8160d2a2553cb4803b6e8d56e102f0c35f3dad40d581eaf6c9df46a8b` |
| 完整 JSON | 本機 `.audit/repo-restructure/rea-managed-v251/Rom.Api.json`，1,973 bytes，SHA-256 `e95e77ba03f2b7fbdb7b0a689dc60abd40727fb93630f6afe3146019f0a0d298` |

REA Evidence ID `ev_326576a8160d2a2553cb4803b6e8d56e102f0c35f3dad40d581eaf6c9df46a8b` 記錄的是 managed metadata absent 結果；native export snapshot 使用不同的 LLVM 證據，沒有 REA Evidence ID。呼叫慣例、函式本體與產品公開 API 對照仍未檢查。

### Speos APIP wrapper（v251，managed metadata absent）

Speos 安裝目錄中的 `ApipWrapper.dll` 與 `AnsysEM/ApipWrapper.dll` 檔名及大小相同，但 SHA-256 不同，因此分開分析。REA 回報 PE、managed metadata `absent`；LLVM 19.1.5 讀出 155 個 native exports，Windows `dbghelp` 解碼 72 個 decorated names。這些 exports 不表示公開或受支援 API，也未分析函式本體或呼叫慣例。

| 欄位 | 值 |
| --- | --- |
| 可攜來源路徑 | `$env:AWP_ROOT251\Optical Products\Speos\bin\ApipWrapper.dll` |
| 檔案大小（bytes） | 954,880 |
| SHA-256 | `d585fac0c0a4811ec4167a44c21d42847baefee19f86e1d2367b40182438f87c` |
| REA Evidence ID | `ev_127062557ff6c48c835cae903b77546c7478a9e5645f2f5cdf6df52235903eb4` |
| REA metadata 結果 | 本機 `.audit/repo-restructure/rea-managed-v251/Speos.ApipWrapper.json`，1,999 bytes，SHA-256 `f1baf519b93fa6ed6d4b5d564cda6220c7c70b119b2c83b85e14cf85ce9b548b` |
| APIKB snapshot | [Speos APIP native export 清冊](./speos_apip_wrapper_native_exports_api.json)，61,245 bytes，SHA-256 `37c30d156a4273d913ff4a5829508fd095ba050bda6a8e70c42f896b2650d9b2` |

Speos wrapper 使用獨立 APIKB key `speos_apip_wrapper_native`。它未與 AnsysEM wrapper 合併；其 export 以 LLVM 證據保存，不附 REA Evidence ID。

### 產生 APIKB 候選快照

在保留本文件列出的 managed REA JSON 的本機工作樹執行以下命令，可重建四十六份 managed 候選 snapshot 並更新本機 APIKB。此命令只轉換已保存的 JSON，不啟動 ANSYS 或載入 DLL。

```powershell
.venv\Scripts\python.exe scripts\api_extraction\extract_all_apis.py --rea-metadata
```

輸出的四十六份 JSON 位於 `docs/api_inventory/`。原始 REA JSON 仍只保留在被忽略的 `.audit/repo-restructure/rea-managed-v251/`；若該本機證據不存在，轉換會停止並保留既有輸出。

Native PE export 清冊使用獨立命令。它需要 `AWP_ROOT251` 指向 v251 安裝，且 `llvm-readobj` 可從 PATH 取得；也可用 `LLVM_READOBJ` 指定執行檔。此流程讀取 PE export table，不執行 DLL。

```powershell
.venv\Scripts\python.exe scripts\api_extraction\extract_all_apis.py --native-pe-exports
```

## DPF DataModel 與 CFX CadApi：PE 格式與 native export 靜態證據

針對先前 metadata-absent 的兩個候選，改用 REA `inspect-managed-artifact` 檢查 PE/CLI 標頭。兩者均為 x86_64 PE，但 `cli` 欄位為 null、`metadata.status=absent`，並觀察到 `cli-directory-absent`：檔案沒有 CLI data directory，因此 REA 的 .NET metadata／CIL parser 不適用。這只分類了檔案格式，不表示產品沒有 API。

| 候選組件 | 檔案大小（bytes） | SHA-256 | REA Evidence ID | 分類 |
| --- | ---: | --- | --- | --- |
| `$env:AWP_ROOT251\dpf\plugins\dpf_simulationdatamodel\Ans.Dpf.DataModel.dll` | 2,660,352 | `cb9b2b0a0fee4a008f044385702e0b34066c705d3824d017a100f6786e4b7d90` | `ev_a1f2cb23906d23baba7a5338ebefaa4e4ed5f83e769912c1eddaf78c3da4ff91` | PE、not-managed、managed metadata absent |
| `$env:AWP_ROOT251\CFX\lib\winnt-amd64\Ans.CFX.CadApi.dll` | 165,056 | `d0e3a9ccfd99e04b65f0e070c4c55514d47887ed8981c6bcf055f01f79973843` | `ev_8af5fbc1dea038f1902cc39d729687a1360e5d37a4cf68ebff2208310411b68f` | PE、not-managed、managed metadata absent |

REA provider 為 `rea-dotnet-static` version `1`。可在相同 v251 安裝根目錄重跑：

```powershell
rea inspect-managed-artifact "$env:AWP_ROOT251\dpf\plugins\dpf_simulationdatamodel\Ans.Dpf.DataModel.dll" --format md --token-limit 1200
rea inspect-managed-artifact "$env:AWP_ROOT251\CFX\lib\winnt-amd64\Ans.CFX.CadApi.dll" --format md --token-limit 1200
```

在相同安裝根目錄以 `llvm-objdump -p`（LLVM 19.1.5）唯讀解析 PE export directory；兩個輸出檔 SHA-256 均與上表相符。DPF DLL 匯出 1 個名稱 `LoadOperators`；本機文件庫中的 `ANSYS_Document/DPF/v251/guide/83daccbdeaa8-group__group__06__2.md` 明列相同入口簽章 `extern "C" CLAYER_DLLEXPORT int LoadOperators(ansys::dpf::AbstractCore* core_ptr)` 並示範以它註冊 operator。此吻合支持它是 DPF plugin loader entry point 的判讀，但不構成整個 DataModel API 清冊。

CFX CadApi DLL 匯出 43 個名稱：

```text
GM_BBOX_CAD GM_E_CLS_CAD GM_E_LN_CAD GM_E_PER_CAD GM_E_RNG_CAD GM_E_TOL_CAD GM_E_XYZ_CAD
GM_F_AR_CAD GM_F_CLS_CAD GM_F_CRV_CAD GM_F_DAT_CAD GM_F_NML_CAD GM_F_NTESS_CAD GM_F_PER_CAD
GM_F_RNG_CAD GM_F_SNG_CAD GM_F_TESS_CAD GM_F_TOL_CAD GM_F_XYZ_CAD GM_START_CAD GM_TERMT_CAD
GM_TOL_CAD GM_UNITS_CAD GM_V_TOL_CAD GM_V_XYZ_CAD GM_WRITE_CAD
TP_BLST_CAD TP_B_F_CAD TP_B_NF_CAD TP_E_F_CAD TP_E_V_CAD TP_F_E_CAD TP_F_LPT_CAD TP_F_NE_CAD
TP_F_NL_CAD TP_F_PR_CAD TP_LST_CAD TP_NBD_CAD TP_NFEV_CAD TP_V_E_CAD TP_V_F_CAD TP_V_NE_CAD TP_V_NF_CAD
```

這些是 PE 匯出表的觀察值；不代表完整、公開或受支援的產品 API。針對 CFX 匯出名稱在本機 `ANSYS_Document/CFX` 及 v251 `CFX/include` 的精確字串搜尋沒有命中，這項有限搜尋不能證明沒有其他文件或介面。`GHIDRA_INSTALL_DIR` 未設定，預設 `C:\Program Files\Ghidra` 也未找到；因此以下以 LLVM 對可界定的 export 函式作有限反組譯，內部 symbols、完整 call graph、CFX 各符號用途及兩元件與公開產品 API 的映射仍待查。全程未載入或執行目標、未啟動 ANSYS，也未求解。

### 2026-10-28 有界反組譯補充

本機 `AWP_ROOT251` 為 `C:\Program Files\ANSYS Inc\v251`。本次重新計算兩 DLL SHA-256，分別與上表一致。以 LLVM 19.1.5 的 `llvm-readobj --coff-exports` 取得 export RVA，再以 `llvm-readobj --unwind` 的 PE runtime-function 範圍界定函式，最後對每個邊界逐一執行 `llvm-objdump --disassemble --start-address=<VA> --stop-address=<VA>`。此方式只反組譯所選函式範圍，不傾倒整個 `.text`。

- **DPF `LoadOperators`**：export RVA `0x14BA20`；`.pdata` 範圍 VA `0x18014BA20–0x18014BB73`，長 `0x153` bytes。函式以傳入的 `core` 指標呼叫 7 個模組內部位址（`0x18014BC20`、`0x18017F060`、`0x18014FEC0`、`0x1801666B0`、`0x18014CBD0`、`0x18015C000`、`0x1801A7DB0`），最後回傳 `0`。結合前述官方 C++ plugin guide 的 `LoadOperators` 註冊範例，可支持它是 operator 載入／註冊入口的判讀；7 個內部位址尚未命名或逐一追蹤。
- **CFX `Ans.CFX.CadApi.dll`**：43 個具名 exports 全部取得有限反組譯範圍。42 個 export RVA 與 `.pdata` runtime-function 起點吻合，函式範圍長度為 30–382 bytes；`TP_F_PR_CAD` 位於 RVA `0x16650`，沒有獨立 unwind entry，依下一個 export 邊界 `0x16660` 檢視後，指令本體為 6 bytes（從 `RDX` 讀取 32-bit 值並寫到 `R8` 指向位置，接著返回）。42 個匯出函式本體包含 73 個直接呼叫點、26 個唯一直接目標位址，以及 3 個間接呼叫點；直接目標屬於同一 DLL 的 `.text`。以全部 43 個 exports 為根，沿直接呼叫地址對應 `.pdata` 範圍，得到 79 個可界定函式、186 個直接呼叫點；另有 18 個唯一直接目標沒有 `.pdata` 函式邊界，且這些可界定函式中共觀察到 168 個間接呼叫點。這是局部、可重跑的靜態呼叫關係，不能當作完整 call graph。
- **CFX 缺少 `.pdata` 邊界的目標補查**：18 個目標中，三個是可由 IAT 對應的 import thunk：`0x18001744E` 跳轉至 `MSVCP140.dll` 的 `std::uncaught_exception`，`0x180018EFE` 跳轉至 `VCRUNTIME140.dll` 的 `memcpy`，`0x180018F0A` 跳轉至 `VCRUNTIME140.dll` 的 `memset`。另於 exports 本體看到 `GM_START_CAD` 間接呼叫 `ComponentSystem.251.dll!AnsCoInitialize`、`GM_UNITS_CAD` 間接呼叫 `api-ms-win-crt-string-l1-1-0.dll!strncpy`；`GM_TERMT_CAD` 的間接呼叫目標由執行期函式指標決定，未靜態解析。其餘 15 個直接目標沒有 unwind 邊界；已觀察到若干短欄位讀取／寫入或尾端跳轉，但不據此命名 API。
- **代表函式 `GM_BBOX_CAD`**：RVA `0x15970`，`.pdata` 範圍長 240 bytes。反組譯可見多個 64-bit 浮點值被寫入呼叫端傳入的輸出指標；與名稱相符地呈現多值幾何結果輸出，但不能由此單獨證明參數語義、單位或受支援的 API 合約。

以上是對具名 PE exports 的靜態指令觀察，不是完整反編譯，也沒有執行任何 DLL。CFX 名稱雖呈現幾何／拓撲分組，但沒有官方簽章或產品文件對應證據，故不把前綴展開成正式 API 語義。DPF 內部函式名稱、CFX 的間接呼叫解析、兩元件的完整 call graph，以及公開／受支援 API 範圍仍未完成。


## 對照 API snapshot（2026-10-28）

比對使用 `docs/api_inventory/spaceclaim_api.json`（1,266 個類別、介面與列舉型別；2,845 個方法列）及 `mechanical_api.json`（跨多個文件模組的 1,728 個類別）。只將 REA `TypeDef` 的完全限定名稱與 snapshot key 完全相同者視為型別直接對應；REA 方法只比較公開可見、非 special-name、非屬性／事件 accessor，且只在完全相同 owner 上用名稱、已解出的參數數與 static 標記配對。這是可比成員的交集檢查，不代表完整公開 API 覆蓋率。

| 組件 | REA 公開型別列 | 與 snapshot 完全同名 | REA 方法列（對應型別內） | 參數數可解 | 方法鍵相符 |
| --- | ---: | ---: | ---: | ---: | ---: |
| SpaceClaim Scripting | 1,268 | 1,234 | 2,760 | 2,237 | 2,237 |
| Mechanical DataModel | 996 | 704 | 32 | 30 | 29 |

SpaceClaim 尚有 34 個 `NestedPublic` 型別列，其正規化 `full_name` 未保留外層型別，因此不能可靠判定與 snapshot 的型別關係；另有 32 個 snapshot 型別沒有在此組件的公開 `TypeDef` 完全限定名稱中找到。SpaceClaim 可直接配對的屬性 getter 名稱有 1,483 個，均在對應 snapshot 型別找到同名屬性；此項只檢查名稱。方法參數數無法解出的 523 列，以及 snapshot 中未配對的列，仍未判定。

Mechanical 組件命名空間為 `Ansys.ACT.Mechanical`／`Ansys.Mechanical.DataModel`，而 snapshot 是多個文件模組的合併資料。只用完全限定名稱得到的型別交集有限；方法鍵差異與大量 snapshot-only 型別不能據此判為缺漏或額外 API。Mechanical getter 名稱比對是 88 個配對名稱；只驗證名稱，不驗證型別簽章。兩邊快照都不能證明 API 是否受支援或可在 runtime 呼叫。

完整 REA JSON 檔案 SHA-256：SpaceClaim `3715c980f9b4e3e2d420cdefeeefcce859473c1c275a3c1ccd68cd97c15177f8`；Mechanical `9fc6bcbdbefb6a9de7f507e7af1840ec739d6d1b0f17351d4b041130d05c9d38`。兩份均為完整 JSON、metadata `status=complete`，其 `identity_scope` 的組件 SHA-256 與 MVID 均符合上表組件識別。

### 本批新增 REA 組件（2026-10-28）

本批新增三個 managed 靜態快照及一個 metadata-absent 元件。組件雜湊用來識別本機 v251 樣本；不表示 API 已公開或受支援。

| 組件 | REA Evidence ID | 組件 SHA-256 | Metadata table counts | 快照／狀態 |
| --- | --- | --- | --- | --- |
| `Ansys.Mechanical.DataModel.dll` | `ev_4e53de05f4e13f6a507df9d24f5fd5abed5f060b712e6b52e5dd798aa5063ea5` | `c3a8de009f71f8d7a8a67a870d2c6a1273d7455d87c1536221c4178486281435` | TypeDef 1,020; MethodDef 813; Property 258; Field 6,270 | 完整 metadata；APIKB `mechanical_datamodel_rea`；snapshot 1,019 types / 813 methods；MVID `90519b63-186f-4533-9899-575ad499c6e7` |
| `Ansys.ACT.Core.dll` | `ev_f374772cb90eddac44164054ffd51f6c435f1be4afec8da04429cf7d17f7978b` | `61f9c36f0ef405e004a5900efc4c3e52e12bdc972a0dc74c70bb7d50b1243748` | TypeDef 1,259; MethodDef 10,243; Property 2,677; Field 4,507 | 完整 metadata；APIKB `act_core_rea`；MVID `8fdcc48b-5659-4d61-bfaf-58253f7c2623` |
| `Infrastructure.ApiDiscoveryV251.dll` | `ev_cec2f2048ef041b031b6fa03e96ae74585d42e19379d0a4574549ed31ea8e7b7` | `2c40c7244138997c268c9d66312bbb1d0371082653669ce316b5d75c64691997` | TypeDef 212; MethodDef 766; Property 18; Field 508 | 完整 metadata；APIKB `api_discovery_rea`；MVID `f28799ba-69e5-46ae-b12e-27f50b63f660`；產品映射待查 |
| `Infrastructure.ApiGeometryV251.dll` | `ev_9d8b98b67c0e827c9b8b99fc24da87e41f1eac812cbd7dde6b07c782e02a8b32` | `bf9a302f0b78f8ca8f32a59a7623c7b73eb74aaab5167cc864f9fe58c9eccd76` | TypeDef 150; MethodDef 678; Property 25; Field 463 | 完整 metadata；APIKB `api_geometry_rea`；MVID `52d2c08a-5e95-4d7f-95e0-59d87f5b405d`；產品映射待查 |
| `AnsysEM\\ApipWrapper.dll` | `ev_6afce84a9fcd4b8256164b47103964cd416a57e7f300e6c09e83d60aeb17ff78` | `49e755e1515416646138f2f22117b862ca2441417e06602af91a5f853697410e` | metadata absent | 155 native exports；72 個 decorated names 可反修飾；[snapshot](./apip_wrapper_native_exports_api.json)；產品映射未確認 |

三份新 snapshot 初次納入時的 APIKB 統計是歷史 checkpoint；後續候選已分批加入，目前共有 46 份 REA 候選 snapshot 與 33 份 native export 清冊。現行統計列於本文件末段，不能與舊 checkpoint 混用。完整 JSON 原件及 hash 留在被忽略的 `.audit/repo-restructure/rea-managed-v251/`，不列入 Git。`Ansys.Mechanical.DataModel.dll` 位於 `$env:AWP_ROOT251\aisol\bin\winx64\Ansys.Mechanical.DataModel.dll`，assembly SHA-256 為 `c3a8de009f71f8d7a8a67a870d2c6a1273d7455d87c1536221c4178486281435`，MVID 為 `90519b63-186f-4533-9899-575ad499c6e7`，REA Evidence ID 為 `ev_4e53de05f4e13f6a507df9d24f5fd5abed5f060b712e6b52e5dd798aa5063ea5`；完整 REA JSON 為 8,500,434 bytes，SHA-256 `9fc6bcbdbebf6a9de7f507e7af1840ec739d6d1b0f17351d4b041130d05c9d38`。API snapshot 為 570,135 bytes，SHA-256 `0a2e747e42d446e4090b61f82865fda3fbbeefe0e1c8e472ef57253c6e07506e`。`Ansys.ACT.Core.dll` 原件 SHA-256 為 `61f9c36f0ef405e004a5900efc4c3e52e12bdc972a0dc74c70bb7d50b1243748`；兩個 API Server 元件目前不推測所屬產品。

本次以 extract_all_apis.py --rea-metadata 重建四十六份 REA 候選 snapshot，再以 extract_all_apis.py --native-pe-exports 擷取三十三份 native PE export 清冊並更新本機 APIKB。新增 CFX CadApi 與 Acmo 共 60 個 export；System Coupling participant 有 743 個 export；DPF 元件掃描有 10,947 個 export。所有 PE 匯出都只作靜態候選，沒有確認支援或 runtime 行為。這些名稱不證明 API 支援或 runtime 可用。LLVM snapshot 提供組件 SHA-256、export ordinal、RVA 與可解碼 symbol signature；不含 REA Evidence ID。APIKB 查詢結果另含版本、來源快照 SHA 與來源元件 SHA。目前最新建置統計為 31,620 symbols、114,702 unique members、197,302 symbol-members、40,074 edges、144,927 FTS entries；這是索引建置統計，不表示全部產品 API 或官方支援介面。尚未完成全量 APIKB/docsearch 範圍審查與 runtime 驗證；重新發布前仍須確認 REA、SDK 與手冊衍生內容的散布權。

### ACT Interfaces、LS-DYNA Interfaces、AnsysEM CoreDotNet 與 Additive

這四份 complete metadata 原先使用 REA `data` envelope，與 extractor 既有頂層輸出格式不同，因此未進 APIKB。extractor 現在支援兩種 envelope，並用 TypeDef token 對應 `declaring_type_token`，以保留同簡稱型別各自的方法。下列列數取自靜態 metadata；snapshot classes 排除 `<Module>` 列。

| 元件 | REA Evidence ID | 組件 SHA-256 | MVID | TypeDef / MethodDef | APIKB key / snapshot |
| --- | --- | --- | --- | ---: | --- |
| `Ansys.ACT.Interfaces.dll` | `ev_95ebfb349467333ee3250d426d7d18942067c4260d61ab3f55a4347a376caa45` | `bcd42394f08566f2ba97f506e9e47c7f34362efd5c8284285a4aea5db75c32d0` | `c8fea0c5-fadc-410f-beb2-05891e93f28b` | 298 / 1,621 | `act_interfaces_rea`; 297 classes |
| `Ansys.ACTLSDYNA.Interfaces.dll` | `ev_45f58ec39e3b6e09ff1773639f0d10b2d10e8f2dd0c57124a88fa669e4a2e1c7` | `01e7d0a3f0bb56668665fb3ad90f198666373a40a7c56166701069f4c3fd8120` | `68001726-0e3b-4c1c-b1eb-4afd5b70bdce` | 9 / 69 | `lsdyna_interfaces_rea`; 8 classes |
| `Ansys.Ansoft.CoreDotNet.dll` | `ev_56774b4b188bed717ee26d06ecc53705cb0f8582d819f133b6101906d58523a1` | `1c3854a230c82800db738db61da3e6570d72b160085e40289b36773fdf8ae06b` | `a51f184d-ffec-446d-b547-b21b096eb75d` | 27 / 169 | `ansysem_coredotnet_rea`; 26 classes |
| `Ansys.Api.Additive.dll` | `ev_5c7a662ce281d8a0f47fb10d6fd2208d910d48660ef440e5997f80eafb686949` | `8351bd20a26f4c800049090a90870352796208ffd4880d4ccbb0675b1913f105` | `1bbcdac1-ab57-40b4-890a-b654aefdf87b` | 209 / 2,314 | `additive_rea`; 208 classes |

### Product add-in assemblies discovered from the installed v251 tree

The following files come from product-specific add-in folders. REA inspected PE metadata without loading the target code. These assemblies can contain implementation and host integration members. Their presence does not prove that a member is a supported public API.

| Component and install-relative path | REA Evidence ID | Assembly SHA-256 | MVID | TypeDef / MethodDef | APIKB key; snapshot classes |
| --- | --- | --- | --- | ---: | --- |
| `Ans.AQWA.Core.dll` — `Addins/AQWA/bin/Win64` | `ev_ec6ec94ac0298cfde397a2e3ce4827ffbf2e6b22cbd8a766bef5289afeb6b569` | `2733eb3c5b4e68ed05f74c76c4cda5a5eb0e85aa895b53bfa827d251d60c37aa` | `24fc83bc-72cf-41a7-b725-7a6a53166748` | 291 / 3,464 | `aqwa_addin_rea`; 290 classes |
| `Ans.AQWA.RemoteItf.dll` — `aisol/bin/winx64` | `ev_b925106850ff1204878666c3dd8b9058963c74e5a5870420b291e983cbf858fb` | `0751eb9e76fa77c897a42643ed0c31ebc95229c285f49de0e9414a040b1fa5e0` | `453a71de-a1d7-4284-a0bb-b60fc48c4422` | 13 / 74 | `aqwa_remote_itf_rea`; 13 classes |
| `Ans.CFX.CFXCore.dll` — `Addins/CFX/bin/Win64` | `ev_5b1ce8ca5541a66590512c80cd6dfc5142c90644d4980e9657a5a1362a3645fb` | `421e31ab499d1993a2520e353ef8e9871e0c0cd512fc25fd09905b50c440e34b` | `d6f7081c-c12c-42ad-8bae-4e97bfce78ed` | 241 / 2,505 | `cfx_addin_rea`; 240 classes |
| `Ans.Fluent.dll` — `Addins/Fluent/bin/Win64` | `ev_02ab1aa25aa1b97e07ea9d7c4e93cb4cf3c944605d9fe985435f53ed187a85df` | `e1742d642bab37ebe26aa147ac4aa4d5a034b26c534da7e963ec18bd9e4f96b4` | `30798882-87b3-442f-b9bc-a784f287950d` | 483 / 7,652 | `fluent_addin_rea`; 482 classes |
| `Ans.Icepak.Core.dll` — `Addins/Icepak/bin/Win64` | `ev_1ee942b070e6c88dcac9cc4ab08276757e9db998faae78901d874e63e25443e2` | `1e5c4b058a6ec33ff077fe8633605e8157b632aeaa90dc7d84621895163b8bc8` | `80d97523-9c84-4df1-91f3-b19a1096471a` | 116 / 1,588 | `icepak_addin_rea`; 115 classes |
| `Ans.Meshing.Core.dll` — `Addins/Meshing/bin/Win64` | `ev_4c59f1b00d1953fc40f6501246dd1cd8b8bce13b67d71914f416df9941802845` | `bbc9d3b9216e26097c6a726ad5249c7f406ebaf3843a5a31fc9750a3a9390356` | `fd294b54-b266-4a9e-8c4c-1537510abe72` | 400 / 3,925 | `meshing_addin_rea`; 399 classes |
| `Ans.Polyflow.dll` — `Addins/Polyflow/bin/Win64` | `ev_d540d49f47827d1d26472f8f9e4a33988c26f32233aa4e63f1ef6ebd162103fd` | `2b40cc3cc511170dfb63f4fb6b233750899b3ad1d7b81fcea536f9ca7739e19e` | `3cfa1cf7-9403-4755-bd8f-c7ed3bf26f51` | 284 / 3,263 | `polyflow_addin_rea`; 283 classes |
| `Ans.Sherlock.Addin.dll` — `Addins/Sherlock/bin/Win64` | `ev_c8068896ce4c32b935f91f820680f51b1fc98549cf660adcfb9df4320c797e62` | `50e7b2d3bf8f00a976206ed7026c211f22f79cd7a775e996bd10efffbff01c11` | `4a63eb54-86b8-4406-bc55-c88ea89e439b` | 466 / 5,357 | `sherlock_addin_rea`; 465 classes |
| `Ans.Ansoft.HFSSAddinPlugin.dll` — `Addins/Ansoft/bin/Win64` | `ev_a34a6017824741cb2271983bcbcbf47a906fbd9263ec27e1386ed005768c7a5b` | `0b042c5cb5a2df9a191b45e5f4b0b4201e9fab1717058a6eb80e566892f61685` | `ef78f98a-e63d-4916-891e-570d2a2b7a0a` | 3 / 8 | `hfss_addin_rea`; 2 classes |

These add-in snapshots expand the searchable v251 candidate set. They preserve declaring-type ownership, flags, artifact hash, MVID, and REA Evidence ID. They do not establish support status. The proprietary originals and full REA results remain in ignored local `.audit/` storage.

### 額外產品 managed 候選（2026-10-28）

REA 6.0.0 `inspect-managed-members` 檢查下列 v251 組件，沒有載入或執行目標程式。metadata complete 只表示可讀取該檔案的 managed metadata；兩個來源仍是靜態候選，不代表產品支援或穩定公開 API。

| Component and install-relative path | REA Evidence ID | Assembly SHA-256 | MVID | TypeDef / MethodDef | APIKB source key |
| --- | --- | --- | --- | ---: | --- |
| `ACP.dll` — `Addins/ACP/bin/win64` | `ev_821ff672bbb6c7e195d7e57bd25703f1067fe70435c8091b8a14313b0902f067` | `441a04df502ce419540279c4a389f592306f49946f9e3e7c6205cb0adb10c49e` | `e9bf8578-00b3-48ce-b089-7dbe2ab05e0c` | 211 / 2,172 | `acp_core_rea` |
| `Ans.AQWA.RemoteItf.dll` — `aisol/bin/winx64` | `ev_b925106850ff1204878666c3dd8b9058963c74e5a5870420b291e983cbf858fb` | `0751eb9e76fa77c897a42643ed0c31ebc95229c285f49de0e9414a040b1fa5e0` | `453a71de-a1d7-4284-a0bb-b60fc48c4422` | 13 / 74 | `aqwa_remote_itf_rea` |
| `MotionAPI.dll` — `aisol/WBAddins/MechanicalExtensions/ANSYSMotion/dll` | `ev_4afc0b4c875028a3b73040b00f2847c87dcb44aba2c7ae1891df06ed8a213ca4` | `16f4d9ea21db2dfd54a4f35cb24e8da4ca948aa31f17b4cf53b0f50776ba0908` | `42af1136-5856-4d26-b8aa-3112c2d5f3e1` | 8 / 36 | `motion_api_rea` |
| `Ansys.Ansoft.SIwave.LibIronPythonCmd.dll` — `AnsysEM` | `ev_7dfa98fb8636c8d57b384efde9161101582f658ebb548d390171c0cef5b538db` | `73b7de096fabf53f18293248706082eef982f3d6a7ee3e05e9395165da5aec8d` | `d4c1ce51-265b-46e1-8c51-90604ba9dbe6` | 96 / 710 | `siwave_libironpythoncmd_rea` |

Full REA Evidence JSON files remain in ignored `.audit/repo-restructure/rea-managed-v251/`. Snapshot contents can include internal types or members. Public status and host behavior remain unverified.

`commonfiles/fluids/lib/winx64/Ans.Fluent.CffWrapper.dll` was inspected as a CFF candidate. It has 2 TypeDef rows and 5 MethodDef rows, but its type namespace is `Ans.Fluent.CffWrapper`. REA Evidence ID is `ev_86189ba204b2bb7177e088f076d32063fbc6072c7c22c6aadd08ff395e2d2c43`; assembly SHA-256 is `c94a638df525bb8f8cbad4b81b348399cc0a69fb734d55f41c32ec156646ec9d`; MVID is `01f32545-c77b-426e-b61e-b8a0d4f278c4`. It is retained as unassigned evidence and is not mapped to CFF API.

### Discovery product API assemblies

REA `inspect-managed-members` 6.0.0 extracted these assemblies from `$env:AWP_ROOT251\Discovery`. Their folder location supports a Discovery association, but does not establish that each member is public or supported. Each snapshot keeps its own source key.

| Component | Install-relative path | REA Evidence ID | Assembly SHA-256 | MVID | Snapshot classes / methods | APIKB key |
| --- | --- | --- | --- | --- | ---: | --- |
| Collaboration API | `Discovery/Ansys.Collaboration.Api.dll` | `ev_6fe465b848c1f6827927bf9b5bb92777ab303716dc29a457e2180bffc804b0dd` | `142cccb682c7613869c5d06608ac3eeacc7a399e6aec765b7a340b6ae55f8e73` | `67a75d04-de69-47e2-87a2-f5ed8fa94675` | 287 / 1,202 | `discovery_collaboration_rea` |
| Gateway API | `Discovery/Ansys.Gateway.Api.dll` | `ev_ceae69ecf15fa25826bd151860dedf794c40b5e56d333f4cb9746e7726ae8811` | `657f9d5039b7e062db4dd9ad67bd00c70c8993cb713d500b206c29e5a637df66` | `7e3b230d-887e-4505-961c-7ed3b15ed99b` | 12 / 37 | `discovery_gateway_rea` |
| Geometry API | `Discovery/Ansys.Geometry.Api.dll` | `ev_08f75a05db1352d8c2671f90ccb45c8d40b8c0aff340085763bd5f73d02eefb0` | `4866343565cd738d079533abc19e0d5d4c76a5d4cb568553907e2d2982050a25` | `4b3e892f-854b-4f5f-9897-379b182a389a` | 29 / 113 | `discovery_geometry_rea` |
| OnScale API | `Discovery/Ansys.OnScale.Api.dll` | `ev_44b31d5c4a82f1d3a8d38be0b4ae4a77da4e96e1d5c5e1498772e11c7df7b93f` | `c23362dd0be272ccb48f4d5e6d2c0c58f6171b40cdaadd8b4b38944161647980` | `696b1c4c-da2a-46a7-8f9b-2a7206109867` | 1,074 / 9,059 | `discovery_onscale_rea` |
| Physics API | `Discovery/Ansys.Physics.Api.dll` | `ev_45ae02a8e01148fa98245a65bc5aae66d940768bc92a17650f174171ff80b62f` | `78a04ae7973d17009717a6309e5bea1622150d53d1bd7d264722fd6f6b038073` | `a70177e6-22c2-41ee-a624-cd75c6e8ad26` | 29 / 106 | `discovery_physics_rea` |
| Project API | `Discovery/Ansys.Project.Api.dll` | `ev_870242a1ba1e12f08f34fa1746952d2d0b2a1106f85f4b51cb0ec3206cde5547` | `4133e9316e39598cf7c6a97d16f9ae3311dafb75df340639cd85e552fc6c0f4e` | `df2caded-b668-421a-891c-0460478c235b` | 101 / 424 | `discovery_project_rea` |
| Results API | `Discovery/Ansys.Results.Api.dll` | `ev_92d1ae539084d2abb885782a8baa61c1435b1cc6305ae915a97810d027b6eeaa` | `d3cb87be1e292d34705bb1576fa88dbdf9233302c686db6934c700456f0c2130` | `c2a737c4-9a82-4055-ad29-8c6630d7b77f` | 47 / 179 | `discovery_results_rea` |

The seven REA outputs add 1,579 snapshot classes and 11,120 MethodDef rows. The complete local inventory contains 29,969 DLLs; a PE CLI-header filter found 23,658 managed candidates, many of which are third-party or framework dependencies. A filename-only triage found 1,172 `Ansys.*`, `Ans.*`, `Ansoft.*`, or `SpaceClaim.*` candidates and 115 files with API-oriented name fragments. These counts are not a product-complete scan. The candidate list remains local at `.audit/repo-restructure/rea-managed-v251-candidates.tsv`; each remaining assembly needs ownership classification before REA extraction.

### Electronics Desktop add-in metadata candidates

These small managed add-ins were found under the v251 Ansoft add-in folder. Their names and location provide product association evidence, not a supported API guarantee.

| Component | Install-relative path | REA Evidence ID | Assembly SHA-256 | MVID | Snapshot classes / methods | APIKB key |
| --- | --- | --- | --- | --- | ---: | --- |
| Maxwell add-in | `Addins/Ansoft/bin/Win64/Ans.Ansoft.MaxwellAddinPlugin.dll` | `ev_de29863d9004012d5c0aa7113d6107c674d56460d1c881e4cfacc6338166b24f` | `01d40fa16190805089990a102541ca3c786ed45ea2374b4d3d16e7fe4a89fa37` | `53e45b29-27d4-49bf-9b41-0c5b7a8896ab` | 2 / 10 | `maxwell_addin_rea` |
| Q3D Extractor add-in | `Addins/Ansoft/bin/Win64/Ans.Ansoft.Q3DExtractorAddinPlugin.dll` | `ev_6460dfe92cdba68cbc85605adc2b4554a71289bedbfed085edd4c8cc06198123` | `152288642233e5aed659424f64138c12833647f94a994782bfa4053e70f7db9b` | `3f884677-04f6-4b41-a4e9-40f66e5dd28d` | 2 / 9 | `q3d_addin_rea` |
| Icepak add-in | `Addins/Ansoft/bin/Win64/Ans.Ansoft.IcepakAddinPlugin.dll` | `ev_e685e48aa242f42fefccc4bc30ffdc2899a1af2ce4bb606ccb7425f12f53f2ba` | `d06fcf8943e6234ecda588a082923f86481cde3097a0244c98c12840f8b8d85f` | `9fb03e80-474f-4a22-af14-c593e4c6288f` | 2 / 8 | `icepak_ansoft_addin_rea` |

These add-ins add six snapshot classes and 27 MethodDef rows. `REA_EVIDENCE.md` retains member details and build-local metadata evidence.

APIKB 現在索引 46 份 REA managed 候選 snapshot 與 33 份 native PE export 清冊。REA snapshot 涵蓋 12,456 個 snapshot class 與 96,357 個 MethodDef；native 清冊另含 12,516 個 export 名稱，其中 9,925 個 symbol 可反修飾。REA member identity 包含 declaring type，避免同簽名成員跨 owner 合併；access 標籤保留連字號。加上 21 份映射產品 snapshots、四份未映射 protocol snapshots 後共 104 個來源鍵。`api_search` 和 `api_get` 對 REA 結果回傳 snapshot SHA-256、組件 SHA-256、REA Evidence ID、版本、visibility/access 標記及 `static_metadata_only; runtime_unverified` 狀態；native 結果回傳 snapshot SHA、組件 SHA、export name、ordinal、RVA 與可解碼 symbol signature。組件映射、官方簽名對照及公開／支援狀態仍未完成；這些數字不是公開 API 數量。



### Zemax OpticStudio ZOS-API assemblies

The v251 installation contains two managed assemblies directly under `Zemax OpticStudio/`. REA inspected their PE/CLI metadata without loading the target code. Installation location and assembly names associate them with OpticStudio, but do not establish the supported ZOS-API contract.

| Component | REA Evidence ID | Assembly SHA-256 | MVID | TypeDef / MethodDef | Snapshot classes / methods | APIKB key |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `ZOSAPI.dll` | `ev_dde9d2ecc2d876859b46e1e02bd514ed4573b9e9eaec10a393216f4bff99d6a4` | `573d6b7dda9013c0e2b1448658794ee033afc6c4f01c49c83b9b2823dcd5270c` | `ab95b788-961c-4b4b-9ef0-8e71ad169685` | 9 / 94 | 8 / 94 | `zemax_zosapi_rea` |
| `ZOSAPI_Interfaces.dll` | `ev_91895470bb640045126d4e5ccce806f4ab315895ad7303225a3fc74eacc094c8` | `eb18966f82c76821ee310c21c9bafa137b34e2e7fafe2dde6041a796187371a9` | `15f830bc-ee7d-4c86-8059-ec0011ec59f9` | 920 / 13,469 | 919 / 13,469 | `zemax_zosapi_interfaces_rea` |

Both snapshots are indexed as static candidates. Their full REA JSON remains local under the ignored `.audit/repo-restructure/rea-managed-v251/` path. Official ZOS-API documentation and signatures have not yet been compared member by member; runtime behavior and redistribution rights remain unverified.


### Additional Ansoft add-in candidates

REA inspected these assemblies from `Addins/Ansoft/bin/Win64/`. The host add-in location supports an Ansoft integration association only. It does not establish a product mapping or supported API contract.

| Component | REA Evidence ID | Assembly SHA-256 | MVID | TypeDef / MethodDef | Snapshot classes / methods | APIKB key |
| --- | --- | --- | --- | ---: | ---: | --- |
| `Ans.Ansoft.DesignerAddinPlugin.dll` | `ev_2baa62f029b5e7df3d5cfa621c825be6fcd299ef0e2eac2beb35c59e1a672faf` | `708e64d83d00d61a6393bdb74e60d16845823aa51f5a2305b3546f5e77e499bd` | `d98d2791-9eed-4056-8216-8306c265a2ef` | 3 / 11 | 2 / 11 | `designer_addin_rea` |
| `Ans.Ansoft.MechanicalAddinPlugin.dll` | `ev_f5467182c9d66994d899e33c2304861032bf7af4712757942573aeb3afb41e6d` | `ce022de4b1ecd8ce5a3064548c777739d50608f249e53d741329209998bb1f91` | `cf2ef528-f65d-4e08-bb98-ef82ab0badc2` | 3 / 8 | 2 / 8 | `mechanical_ansoft_addin_rea` |
| `Ans.Ansoft.SimplorerAddinPlugin.dll` | `ev_c652559083b9c565bd888b2be7cd86bd439eb1571e7b627c74922e3ebe2caee1` | `bba079e08078996e1ffeb7491234732e673bd8365dadcde52cfd520efeab3088` | `02dd607e-0fb9-4681-bfd4-39ce62e72f7f` | 6 / 17 | 5 / 17 | `simplorer_addin_rea` |

The full REA JSON remains in the ignored local evidence directory. The three snapshots contain static members only. Official signatures, product ownership, runtime behavior, and redistribution rights remain unverified.

### CFX native components with absent CLI metadata (v251)

REA `inspect-managed-members` reported no admitted CLI metadata for these two PE files. `inspect-artifact` retained only the root PE manifest and file occurrence. `llvm-readobj 19.1.5 --coff-exports` then read the native export tables. The exports are candidate names only; they do not provide decoded function signatures or prove a supported CFX API.

| Component | Portable source path | Bytes | Assembly SHA-256 | REA member Evidence ID | REA artifact Evidence ID | Native exports | APIKB key |
| --- | --- | ---: | --- | --- | --- | ---: | --- |
| `Ans.CFX.CadApi.dll` | `$env:AWP_ROOT251\CFX\lib\winnt-amd64\Ans.CFX.CadApi.dll` | 165,056 | `d0e3a9ccfd99e04b65f0e070c4c55514d47887ed8981c6bcf055f01f79973843` | `ev_8cb67681882d5301d4ab48c91c101431ca24f8eb71d7efbc4f5806a91e2eede8` | `ev_d5da3f65be4c514131a5c76044aa9ab5c81bd84a2218c152602e30dbc1338474` | 43 | `cfx_cadapi_native` |
| `Ans.CFX.Acmo.dll` | `$env:AWP_ROOT251\CFX\lib\winnt-amd64\Ans.CFX.Acmo.dll` | 284,864 | `c3aa76898adab0b6d40a396aabd97874531a74c42cc601736568f19074bce126` | `ev_aa6327acc531031341fddc82b53b60b1b9ac2720ad10532137b279b8cd0069f2` | `ev_d10daf10e11c58e0f98d87215b295bcbdb14ba76b3568165313c509c3da31f0b` | 17 | `cfx_acmo_native` |

Both REA member results state metadata `absent`; TypeDef, MethodDef, MVID, and managed signatures are unavailable. The REA and export evidence JSON remains in `.audit/repo-restructure/rea-managed-v251/`. LLVM export snapshots are listed in `API_CATALOG.md`. No native function bodies or calling conventions were analyzed. Product support, runtime behavior, and redistribution rights remain unverified.

### DPF Mechanical Results native component (v251)

REA `inspect-managed-members` reported no admitted CLI metadata for this PE. REA `inspect-artifact` retained its root PE manifest and file occurrence. LLVM 19.1.5 found one native export, `LoadOperators` (ordinal 1, RVA `0x205A0`), with no decoded signature. The name does not establish the supported DPF interface or call contract.

| Component | Portable source path | Bytes | Assembly SHA-256 | REA member Evidence ID | REA artifact Evidence ID | Export snapshot SHA-256 | APIKB key |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| `Ans.Dpf.MechanicalResults.dll` | `$env:AWP_ROOT251\dpf\bin\winx64\Ans.Dpf.MechanicalResults.dll` | 422,400 | `0948ca657a05b341870ed8744f23798f6e2bebfcd2e58d1fa570cbf952d0c50d` | `ev_b2a6c586ad84b4464fa7516adbd37d706e8d457589adc2f0dd340c6e05c4d906` | `ev_c2f5aef6971f1f18019cc1aaa438eb4d32a88992e036793c396e79af9f8ff6cb` | `10d1f607a6d23e2c2d63ab0ff1f1b1a8f588b65a6472371bb491eba0ca06b104` | `dpf_mechanicalresults_native` |

The full REA JSON remains in the ignored local `.audit/repo-restructure/rea-managed-v251/` directory. LLVM export extraction did not inspect function bodies, parameters, calling conventions, or runtime behavior. Product support and redistribution rights remain unverified.

### DPF Engineering Data native component (v251)

REA reported absent CLI metadata for `Ans.Dpf.EngineeringData.dll`. The file has no managed TypeDef or MethodDef rows. LLVM 19.1.5 found one native export, `LoadOperators` (ordinal 1, RVA `0x6DB50`). The export has no decoded signature. Its name does not establish API support or call behavior.

| Component | Portable source path | Bytes | Assembly SHA-256 | REA Evidence ID | Export | APIKB key |
| --- | --- | ---: | --- | --- | --- | --- |
| `Ans.Dpf.EngineeringData.dll` | `$env:AWP_ROOT251\dpf\bin\winx64\Ans.Dpf.EngineeringData.dll` | 1,542,144 | `89b581ece00b807bda9b45bb66d95d11a8217011e550702eff69b39627c20b25` | `ev_ff9549d0840280aae4bc20b48aeff407ff5cc504b9edd2861839a540d01d7002` | `LoadOperators` (ordinal 1, RVA `0x6DB50`) | `dpf_engineeringdata_native` |

The snapshot is [dpf_engineeringdata_native_exports_api.json](./dpf_engineeringdata_native_exports_api.json). LLVM read the PE export table. It did not decode a signature or inspect function code. Runtime behavior and product support remain unverified.

### DPF component sweep: REA metadata and PE exports (v251)

REA checked 23 Ans.Dpf DLL files from the dpf/bin and dpf/plugins folders. All 23 results reported absent CLI metadata. LLVM 19.1.5 found 10,947 named PE exports. Windows dbghelp decoded 9,236 decorated names. Large export sets occur in Compression, AUTODYN, and Multiphysics Mapper. These names may include internal or runtime symbols. They do not prove a supported DPF API or a callable function.

| Component | Named exports | Decoded names | APIKB key |
| --- | ---: | ---: | --- |
| Ans.Dpf.Abaqus.dll | 5 | 4 | [dpf_abaqus_native](./dpf_abaqus_native_exports_api.json) |
| Ans.DPF.Autodyn.dll | 3,183 | 3,181 | [dpf_autodyn_native](./dpf_autodyn_native_exports_api.json) |
| Ans.Dpf.CFF.dll | 1 | 0 | [dpf_cff_native](./dpf_cff_native_exports_api.json) |
| Ans.Dpf.Cgns.dll | 1 | 0 | [dpf_cgns_native](./dpf_cgns_native_exports_api.json) |
| Ans.Dpf.Compression.dll | 6,303 | 4,995 | [dpf_compression_native](./dpf_compression_native_exports_api.json) |
| Ans.Dpf.DataModel.dll | 1 | 0 | [dpf_datamodel_native](./dpf_datamodel_native_exports_api.json) |
| Ans.Dpf.EngineeringData.dll | 1 | 0 | [dpf_engineeringdata_native](./dpf_engineeringdata_native_exports_api.json) |
| Ans.Dpf.FEMutils.dll | 1 | 0 | [dpf_femutils_native](./dpf_femutils_native_exports_api.json) |
| Ans.Dpf.FlowDiagram.dll | 1 | 0 | [dpf_flowdiagram_native](./dpf_flowdiagram_native_exports_api.json) |
| Ans.Dpf.Grpc.dll | 1 | 0 | [dpf_grpc_native](./dpf_grpc_native_exports_api.json) |
| Ans.Dpf.Hdf5.dll | 1 | 0 | [dpf_hdf5_native](./dpf_hdf5_native_exports_api.json) |
| Ans.Dpf.LivePost.dll | 1 | 0 | [dpf_livepost_native](./dpf_livepost_native_exports_api.json) |
| Ans.Dpf.LSDYNAHGP.dll | 1 | 0 | [dpf_lsdynahgp_native](./dpf_lsdynahgp_native_exports_api.json) |
| Ans.Dpf.Math.dll | 7 | 6 | [dpf_math_native](./dpf_math_native_exports_api.json) |
| Ans.Dpf.Mechanical.dll | 1 | 0 | [dpf_mechanical_native](./dpf_mechanical_native_exports_api.json) |
| Ans.Dpf.MechanicalResults.dll | 1 | 0 | [dpf_mechanicalresults_native](./dpf_mechanicalresults_native_exports_api.json) |
| Ans.Dpf.MultiphysicsMapper.dll | 1,051 | 1,050 | [dpf_multiphysicsmapper_native](./dpf_multiphysicsmapper_native_exports_api.json) |
| Ans.Dpf.Native.dll | 1 | 0 | [dpf_native_native](./dpf_native_native_exports_api.json) |
| Ans.Dpf.Prime.dll | 380 | 0 | [dpf_prime_native](./dpf_prime_native_exports_api.json) |
| Ans.Dpf.PythonPluginWrapper.dll | 2 | 0 | [dpf_pythonpluginwrapper_native](./dpf_pythonpluginwrapper_native_exports_api.json) |
| Ans.Dpf.Rbd.dll | 1 | 0 | [dpf_rbd_native](./dpf_rbd_native_exports_api.json) |
| Ans.Dpf.SystemCouplingMapping.dll | 1 | 0 | [dpf_systemcouplingmapping_native](./dpf_systemcouplingmapping_native_exports_api.json) |
| Ans.Dpf.Vtk.dll | 1 | 0 | [dpf_vtk_native](./dpf_vtk_native_exports_api.json) |

The REA JSON for this sweep stays in the ignored .audit/repo-restructure/rea-managed-v251/dpf-module-sweep/ folder. Each export snapshot records its component hash, export ordinal, RVA, tool version, and decoded symbol text when available. No function body or runtime behavior was analyzed.

### Lumerical Python and Tcl native interfaces (v251)

REA checked three DLLs in the Lumerical API folders. Each result reported absent CLI metadata. LLVM 19.1.5 found 19 exports in each Python interop DLL and one export in the Tcl DLL. The names identify entry points only. They do not provide parameter types, call conventions, or runtime behavior.

| Component | Portable source path | Bytes | SHA-256 | REA Evidence ID | Exports | APIKB key |
| --- | --- | ---: | --- | --- | ---: | --- |
| interopapi.dll | $env:AWP_ROOT251/Lumerical/api/python/interopapi.dll | 248,320 | f82c6fe630e2715079fa576b28ad0c532d2cd6889dcb7e622ca56bf27a9bedbf | ev_3430ea8a25b4119151b3da74b985a21fc3b6f92c926b2a21dbaa3e756dc90c13 | 19 | lumerical_interopapi_native |
| interopapi-remote.dll | $env:AWP_ROOT251/Lumerical/api/python/interopapi-remote.dll | 418,816 | ea2aa1ae9ee7944121e377ada5f66f475258cffe619d702975559176bb320e82 | ev_62519be470dfe94ec909fce284ed4106bbb4a0d85dad8d83d829ad228fb90ab5 | 19 | lumerical_interopapi_remote_native |
| lumapi.dll | $env:AWP_ROOT251/Lumerical/api/tcl/lumapi.dll | 66,048 | 21602ad00cf7d082f63aa556d5c5cd91426896ded742c457528749982b23a232 | ev_e3112b17f775292e9901d1c5657dfe76cc7dab67d6ed6eb4da74aa1cc011d91e | 1 | lumerical_lumapi_native |

The two Python interop DLLs export the same 19 names. The Tcl DLL exports Lumapi_Init. API support, signatures, and runtime behavior remain unverified.
