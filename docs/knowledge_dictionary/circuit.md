# Circuit 知識字典

本頁依本機 **Circuit Scripting Guide，Release 2026 R1／January 2026（v261）** 與五個官方 Circuit Help HTML 頁面，整理可定位的腳本介面及 Nexxim 分析概念。PDF 共 1,152 實頁；本頁頁碼一律是從封面起算的實頁，不能把目錄或章內印刷頁當成實頁。腳本指南含共用 AEDT 與 HFSS 範例；這些範例不自動構成 Circuit 專屬 API 或 runtime 相容性證明。

主要來源：[原始 PDF](../ANSYS_Document/Circuit/v261/manuals/CircuitScriptingGuide.pdf)、[canonical 逐頁 Markdown](../ANSYS_Document/_catalog/pdf_text_v4/5a7a3d6aa524123a918a6b265052d0064d37cb03545d22c52d47149accee2d44.md)、[來源清冊](sources.csv#ansys_9562597e2be9167330e444dd)。本機 PDF 與兩份既有文字轉換沿用，不重新轉檔。

## 1. 腳本環境與物件模型

內嵌 Python 腳本可用預先提供的 `oDesktop` 與 `ScriptArgument`。指南的 IronPython 相容性說明是 Python 2.7／.NET Framework 4.0；含 C extension 的 NumPy、SciPy 不在該說明預期可直接運作的範圍。此處沒有指定 CPython 最低版本，也不作延遲比較。

| 物件 | 本指南中的責任與取得方式 |
| --- | --- |
| `oAnsoftApp` | 應用程式 handle；共用 IronPython 範例以 `CreateObject` 建立，然後呼叫其 `GetAppDesktop()`。 |
| `oDesktop` | 桌面／專案管理；內嵌 Python 已提供此物件。 |
| `oProject` | 一個已開啟專案，含變數、材料及設計；可由 `GetActiveProject()` 取得。 |
| `oDesign` | 專案內的設計，含變數、module 與 editor；可由 `GetActiveDesign()` 取得。 |
| `oEditor` | 編輯器資料操作；適用編輯器要依設計與命令文件判斷。Reporter Editor 命令由 `oDesign` 執行，並沒有對應的 `oEditor` Reporter 物件。 |
| `oModule` | 一組相關功能的 module，由設計取得其介面；名稱不能跨 solver 任意套用。 |

來源：[實頁 36](../ANSYS_Document/_catalog/pdf_text_v4/5a7a3d6aa524123a918a6b265052d0064d37cb03545d22c52d47149accee2d44.md#pdf-page-36)、[39](../ANSYS_Document/_catalog/pdf_text_v4/5a7a3d6aa524123a918a6b265052d0064d37cb03545d22c52d47149accee2d44.md#pdf-page-39)、[84–87](../ANSYS_Document/_catalog/pdf_text_v4/5a7a3d6aa524123a918a6b265052d0064d37cb03545d22c52d47149accee2d44.md#pdf-page-84)。舊版字典把目錄頁 3–15 當成物件模型正文、把 `GetAppDesktop()` 接在 `ScriptEnv` 及接續 `GetTool("Project")`，均已移除。

## 2. CPython 與 gRPC 連線

外部 CPython 腳本需可找到安裝目錄的 `PythonFiles/DesktopPlugin` 並載入 `ScriptEnv`。指南將 AEDT 描述為 gRPC server，CPython script engine 為 client；未指定 port 時由 50051 起找可用 port。`-grpcsrv` 也可指定單一 port 或範圍；指定 port 已佔用、或範圍全被佔用時會報錯。

| 入口 | 本來源描述的範圍 |
| --- | --- |
| `Connect(projectPath)` | 連接已開啟專案，或啟動 AEDT 並開啟它；專案不存在則錯誤。 |
| `Connect(portNumber)` | 連接本機正在監聽該 port 的 AEDT；沒有 listener 則錯誤。 |
| `Connect(machine, projectPath)` | 遠端 project path 必須是 network path；遠端未開啟該專案則錯誤。 |
| `Connect(machine, portNumber)` | 連接遠端既有 listener。 |
| `InitializeNew(...)` | 一律啟動新 instance；本節的 `Machine` 僅空字串，啟動限本機；`Port=0` 從 50051 找可用 port。 |
| `Initialize(...)` | 嘗試連接指定 machine／port，必要時啟動；依文件參數判斷，不以此推定所有版本的遠端啟動能力。 |
| `Shutdown()` | 指南要求在結束處呼叫；多腳本情境只在最後一個腳本末尾呼叫。 |

來源：[實頁 79–82](../ANSYS_Document/_catalog/pdf_text_v4/5a7a3d6aa524123a918a6b265052d0064d37cb03545d22c52d47149accee2d44.md#pdf-page-79)。這是該版 `ScriptEnv` 說明；不把它與 PyAEDT client、COM 或其他 SDK 的連線語義合併。

## 3. User Defined Model 與 Primitive

Python UDP 的主類別是繼承 `IUDPExtension` 的 `UDPExtension`；Python UDM 則是繼承 `IUDMExtension` 的 `UDMExtension`。它們屬 AEDT 的幾何擴充說明，不是此頁已驗證可放入 Circuit 原理圖的電阻／Nexxim 元件工廠。

腳本位置由 SysLib、UserLib 或 PersonalLib 中的 `UserDefinedParts`／`UserDefinedModels` 子目錄決定。`Lib` 內的 helper 不顯示於選單，可供上游路徑內的腳本匯入。原文 p54 的 upstream 終點另寫 `UserDefinedPrimitives`；與 p53 的 `UserDefinedParts` 拼法差異保留，未推定成另一個必備安裝路徑。修改後可用 Draw 選單的 Update Menu；刪除腳本時原文只建議可能需重新啟動，不能改寫成已證實的崩潰條件。

來源：[實頁 53–54](../ANSYS_Document/_catalog/pdf_text_v4/5a7a3d6aa524123a918a6b265052d0064d37cb03545d22c52d47149accee2d44.md#pdf-page-53)。

## 4. Circuit v261 Python UDP 目錄／更新／必要介面

| 必要方法 | 原文型別與責任 |
| --- | --- |
| `GetLengthParameterUnits()` | 回傳單位字串。 |
| `GetPrimitiveTypeInfo()` | 回傳 `UDPPrimitiveTypeInfo`，不是任意三元素 list。 |
| `GetPrimitiveParametersDefinition2()` | 回傳 `UDPPrimitiveParameterDefinition2` list，失敗可為 None。 |
| `AreParameterValuesValid2(errorMsg, udpParams)` | `errorMsg` 為 C# string list，`udpParams` 為 C# `UDPParam` list；回傳 Boolean。 |
| `CreatePrimitive2(funcLib, udpParams)` | `funcLib` 為 UDM function library、參數為 C# list；回傳成功／失敗 Boolean。 |

來源：[實頁 54–56](../ANSYS_Document/_catalog/pdf_text_v4/5a7a3d6aa524123a918a6b265052d0064d37cb03545d22c52d47149accee2d44.md#pdf-page-54)。舊字典中的自訂 list、`GetDouble()`、`errorMsg.Set()` 與 `CreateBox()` 範本未由本來源逐項證實，已移除。

## 5. Circuit v261 Python UDM instance／Refresh／資源釋放契約

`GetInfo()` 提供 `UDMInfo`；Python UDM 的 `IsAttachedToExternalEditor()` 通常回 False；`CreateInstance(funcLib)` 回傳 `UDMParameters`，`GetUnits(instanceId)` 回單位字串。`Refresh` 負責建立／刷新幾何：若不修改傳入參數，也要將 `udmInParams` 複製到 `updatedParams`。partial refresh 是選用能力；支援時透過 `nonEditedPartRefIds` 回報未改動 part IDs，不支援時可以每次更新所有 parts。

`ReleaseInstance(instanceId)` 釋放該 instance 的資源並回傳 Boolean。來源沒有證明不實作會產生某種固定線性記憶體成長。Python UDM 另應實作 entity／part ID attribute 名稱方法。p59 同列新對話框方法及 deprecated 舊方法；不能把選用方法當成全部模型的必要介面。

來源：[實頁 57–59](../ANSYS_Document/_catalog/pdf_text_v4/5a7a3d6aa524123a918a6b265052d0064d37cb03545d22c52d47149accee2d44.md#pdf-page-57)。

## 6. 腳本記錄與執行

Tools > Run Script 或 Automation tab 可執行 `.py`；錄製可存外部檔或專案。開始錄製後後續 UI 動作持續被記錄，需手動停止；專案腳本位於 Scripts library／Definitions 下。命令列可使用 `-runscript`／`-runscriptandexit`，`-scriptargs` 後面的參數原樣傳成單一 `ScriptArgument` 字串，分隔規則由腳本自己決定。

共用指南 p38 的非圖形 beta 範例明列 HFSS／3D Layout，不能將該範例轉成 Circuit 任意腳本都可無頭執行的結論。p81–82 又說 `-ng` 可與 gRPC server flag 合用；兩段的適用情境分開保留。此頁不提供會建立設計、啟動求解或變更設定的可執行範例，也未把 `SetDesktopConfiguration` 誤當成通用彈窗抑制命令。

來源：[實頁 38–39](../ANSYS_Document/_catalog/pdf_text_v4/5a7a3d6aa524123a918a6b265052d0064d37cb03545d22c52d47149accee2d44.md#pdf-page-38)、[87–90](../ANSYS_Document/_catalog/pdf_text_v4/5a7a3d6aa524123a918a6b265052d0064d37cb03545d22c52d47149accee2d44.md#pdf-page-87)、[81–82](../ANSYS_Document/_catalog/pdf_text_v4/5a7a3d6aa524123a918a6b265052d0064d37cb03545d22c52d47149accee2d44.md#pdf-page-81)。

## 7. Circuit v261 InsertDesign、module 與 editor 的回傳／原文差異

Project `InsertDesign` 的有效 design type 表包含 `Circuit`、`Nexxim Circuit`、`System`、`Nexxim Netlist`、`HFSS3D`，回傳值為 None；因此不能把其結果直接當 `oDesign`。Circuit／HFSS 3D Layout 腳本最後參數為空字串。TechnologyFile 表寫技術檔路徑，範例卻給安裝目錄，本頁不代替原文決定實際輸入。

`GetModule` 表列 `AnalysisSetup`、`DataBlock`、`Optimetrics`、`OutputVariable`、`ReportSetup`、`UserDefinedDocuments`、`UserDefinedSolutionModule`，但同頁範例使用未列在表內的 `SimSetup`；這是來源待對照處。`GetEditor` 的例子可見 `SchematicEditor`，而 `SetActiveEditor` 的通用範例用 `3D Modeler` 且參數說明殘留 notes 字樣。應查實際 design 的命令，不由這些共用例子推定所有 Circuit editor 名稱。

來源：[實頁 304–305](../ANSYS_Document/_catalog/pdf_text_v4/5a7a3d6aa524123a918a6b265052d0064d37cb03545d22c52d47149accee2d44.md#pdf-page-304)、[367–368](../ANSYS_Document/_catalog/pdf_text_v4/5a7a3d6aa524123a918a6b265052d0064d37cb03545d22c52d47149accee2d44.md#pdf-page-367)、[393–394](../ANSYS_Document/_catalog/pdf_text_v4/5a7a3d6aa524123a918a6b265052d0064d37cb03545d22c52d47149accee2d44.md#pdf-page-393)。

## 8. Circuit v261 Schematic ID／子元件與建立屬性

Schematic 建立方法回傳唯一 ID；也可透過 `FindElements`／`GetSelections` 識別物件。子元件可用 `TopLevelID:SubComponentIndex`，索引從 1 開始，0 只表示 top-level。來源明說不存在的 ID／子索引會被忽略，即使沒有有效 ID，方法仍可能回成功；回傳 success 不能單獨證明目標物件已改動。

建立物件的共同 Attributes 含一基的 Page（預設 1）、X、Y、以 radians 表示的 Angle、Flip Boolean。這是共用格式，不能據此替元件庫、參數清單或 CreateComponent 編造可執行資料。

來源：[實頁 842–843](../ANSYS_Document/_catalog/pdf_text_v4/5a7a3d6aa524123a918a6b265052d0064d37cb03545d22c52d47149accee2d44.md#pdf-page-842)。

## 9. Circuit v261 LNA 的 DC bias 線性化與 S／Y／Z

Nexxim Linear Network Analysis 在 DC bias point 周圍線性化電路，計算隨頻率變化的 S、Y、Z 參數；可選 group delay 與 DC noise。此定義不等於大型訊號或任意非線性波形的直接解。設定、匯入 netlist 支援與結果輸出需各自查看子頁。

來源：[官方 LNA](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Circuit/Content/Circuit/NexximLinearNetworkAnalysis.htm)，[來源列](sources.csv#official_circuit_lna_v261)。

## 10. Circuit v261 DC 初始化／NODESET／IC 差異

該頁描述 DC 初始化時電容按開路、電感按短路處理，並區分 `.NODESET` 的初次 Newton–Raphson 起始值與 `.IC` 在 DC operating point 計算中持續施加的節點電壓。未由 NODESET 指定的浮接節點可能未定義；`.IC` 未指定的電壓則由計算求得。頁面還提醒 Nexxim 在 `.OP` 識別 `.IC`，其他 simulator 不一定相同；不能跨 SPICE 方言套用。

來源：[官方 DC initialization](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Circuit/Content/Circuit/InitializationofNexximDCCircuitParameters.htm)，[來源列](sources.csv#official_circuit_dc_initial_v261)。

## 11. Circuit v261 Transient output 與數值顯示

預設輸出內部數值積分時間點的節點電壓，可在 Output Quantities 或 `.PRINT` 限定變數。Nexxim 使用 quadratic interpolation，輸出不會自動變成等間隔 TSTEP 點。週期波形可能因取樣時間點造成圖上的 stable undershoot 或 numerical beating；縮小 timestep 可改善顯示，但增加分析時間，也不是所有誤差的消除保證。

來源：[官方 transient output](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Circuit/Content/Circuit/ControllingOutputfromTransientAnalysis.htm)，[來源列](sources.csv#official_circuit_transient_output_v261)。

## 12. Circuit v261 Nexxim netlist 輸入／SDF 輸出

Nexxim 命令列輸入可為內部 `.cir`、HSPICE `.sp` 或 Spectre `.scs` netlist；副檔名只表輸入格式，不能當成所有外部 simulator 語法完整相容的證據。來源描述 `-o` 選項把 `.PRINT` 要求的量寫成指定名稱的 SDF；省略時使用輸入檔名及其目錄。SDF 是 Simulation Data File，結果檢視需另外遵循 AEDT 的 Viewing Results 說明。

來源：[官方 invoking Nexxim](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Circuit/Content/Circuit/InvokingtheNexximSimulator.htm)，[來源列](sources.csv#official_circuit_nexxim_cli_v261)。本輪只閱讀，未呼叫命令。

## 13. Circuit v261 S-Element／W-Element 與方法選擇

官方流程對傳輸線／耦合線建議 W-Element 指向 S-model，並要求 S-parameter 資料正確 deembed；多 port、短 electrical length 或非傳輸線元件可採 S-Element。S-Element 以擬合 state-space 為預設，convolution 是另一途徑。該頁對大於最高頻率 22 wavelengths 的 electrically long 情境或 state-space fitting 失敗給出 convolution 指引；這是來源特定流程，不是任意電路的穩定性或精度門檻。

來源：[官方 element/method selection](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/Circuit/Content/Circuit/SelectingtheCorrectElementandMethod.htm)，[來源列](sources.csv#official_circuit_sparameter_method_v261)。完整因果性、passivity、擬合及圖中分支未在此全部覆核。

## 14. Circuit v261 手冊章節導覽與轉換可追溯性

| 技術章節 | 實頁起點 |
| --- | --- |
| Introduction to Scripting | 35 |
| Object-Oriented Scripting | 96 |
| Application Object | 174 |
| Desktop Object | 176 |
| Running Instances Manager | 258 |
| Project Object | 260 |
| Design Object | 322 |
| Output Variable | 400 |
| Reporter Editor | 416 |
| Analysis Setup Module | 526 |
| Optimetrics Module | 594 |
| User-Defined Document | 764 |
| User-Defined Solutions | 778 |
| Network Data Explorer | 784 |
| CompInstance | 836 |
| Schematic Scripting | 842 |
| Nexxim Scripting | 946 |

Index 從實頁 1132 開始。完整章節入口不等於每個命令、表格與圖已整理完。原件及 canonical／同名 Markdown 依 extraction manifest 比對；兩份轉換各有 1,152 個連續 PDF Page 標題，代表同一份 PDF，不能重複當成兩本手冊。

## 15. 版本與來源限制

本機僅此份 v261 scripting PDF；五份官方 HTML 的頁尾均標示 Ansys Electromagnetics Suite 2026 R1。官方線上摘要沒有保存成本機全文；HTML 的圖片與全部子頁未覆核。Netlist Local Options 與 InsertDesign 的直接 HTML 開啟失敗，雖有搜尋快取摘要，沒有據此新增完整技術結論；後者已改以本機 PDF 實頁核對。

尚缺 Circuit 全部建模／元件庫／求解選項手冊與跨版本比較。共用指南內的拼字／範例差異已就地標示；未用 AEDT runtime 消解。來源 metadata 的 general→circuit 修正有封面與現有 SQLite circuit 分類為依據，不修改原 catalog 或原件。

相關字典：[AEDT](aedt.md)、[HFSS](hfss.md)、[AnsysEM](ansysem.md)。


## 2026-11-04：Wave 9 本機來源盤點與限制說明

本批完成 circuit 模組既有本機 catalog 文件（共 0 筆）與 sources 清冊（共 8 筆）之完整雜湊、正文路徑與標籤結構核對。本機未快取或具備企業授權/登入限制之線上主題誠實標記為缺口（保持現有非 complete 狀態），未擅自虛構未核實之線上 API 簽名或執行求解運算。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/circuit_module_conversion_report_20261104.md)。
