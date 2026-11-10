# Ansys Workbench 知識字典

本頁依本機 **Release 2026 R1（v261）** 的 Workbench Scripting Guide 與 ACT Customization Guide for Workbench 整理有界主題。頁碼均指 **PDF 實頁**；兩本文件的主要正文印刷頁約比實頁少 10，仍以各頁頁尾核對。文件 API 宣告不代表已在 Workbench 執行。

## 章節閱讀進度與轉換品質

逐章進度見[Workbench 章節及轉換覆核清冊](../maintenance/knowledge_dictionary_passes/2026-11-02/workbench_chapter_progress_20261103.md)。18 個字典主題代表已核讀的章節片段，不表示兩本手冊全章或全部 API 都已整理。

PDF canonical v4 Markdown 已保留逐頁標記，兩份來源分別為 1,466 與 248 頁；不重轉既有產物。PDF 共含多個嵌入圖像（初步統計 Scripting Guide 5 個、ACT Guide 56 個），canonical Markdown 未內嵌圖像，因此流程圖、UI 截圖及圖示資訊不能只靠文字轉換確認。表格亦須逐頁核對：例如 Scripting Guide 實頁 18 的 SendCommand 支援矩陣在轉換文字中已線性化，字典以手工重排表格並保留空白欄的限制。掃描／圖片頁、公式與其餘表格尚未逐頁完成視覺校對；請回到 PDF 原頁核實。

## 來源、版本與閱讀入口

| 來源 | PDF 實頁 | 可追溯正文 | 來源 ID |
| --- | ---: | --- | --- |
| [Workbench Scripting Guide](../ANSYS_Document/Workbench/v261/manuals/Workbench_Scripting_Guide.pdf) | 1,466 | [canonical 逐頁 Markdown](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md) | `ansys_05b664ec1d5ee31846d738a4` |
| [ACT Customization Guide for Workbench](../ANSYS_Document/Workbench/v261/manuals/ACT_Customization_Guide_for_Workbench.pdf) | 248 | [canonical 逐頁 Markdown](../ANSYS_Document/_catalog/pdf_text_v4/1946241954ca369f6c394222651030fa29424a9c3b9249316c4e731e50507918.md) | `ansys_843b9c0be2bced4d8651f4a6` |

兩份封面均明列 Release 2026 R1／March 2026。來源同名 Markdown 仍保留：[Scripting 舊轉換](../ANSYS_Document/Workbench/v261/manuals/Workbench_Scripting_Guide.md)（`ansys_bf146052ec7716d8122c2318`）、[ACT 舊轉換](../ANSYS_Document/Workbench/v261/manuals/ACT_Customization_Guide_for_Workbench.md)（`ansys_9b0d4ecb6d9a7614cd649d73`）。它們與 canonical PDF 轉換不同，`pdf_extraction.json` 記為 `existing_different_preserved`；本頁逐頁引用使用上表 canonical 版本，未覆寫既有轉換。

## 1. Project Schematic 與流程自動化

**Native workspace** 建於 Workbench framework；手冊列出 Project Schematic、Engineering Data、Design Exploration。修改原生工作區資料的操作會 journal，並可用 Workbench scripting 自動化。**Data-integrated application** 是獨立應用，Project Schematic 可啟動它、傳遞資料／參數，但只保證由 Schematic 發起的操作會進 Workbench journal；應用內操作未必會被記錄。

`SendCommand` 可把原生腳本送至支援的應用。v261 支援表仍將 Mechanical 的語言列為 JScript；不應把這張表改寫成所有版本的 Mechanical Python／ACT 支援矩陣。

| v261 手冊列示應用 | Native language | Scripting with SendCommand | Journaling with SendCommand |
| --- | --- | --- | --- |
| CFX、CFD-Post | CCL | Yes | Yes |
| Fluent | Scheme | Yes | Yes |
| ICEM CFD | TCL | Yes | No |
| Mechanical | JScript | Yes | 原表未標 Yes |
| Polyflow Classic、IcePak | Not Available | 原表未標 Yes | 原表未標 Yes |

空白欄僅按原表保留，不能推導其他介面是否可用。來源：[Scripting 實頁 17–18](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-17)。

## 2. Workbench scripting 物件與專案狀態

| 英文術語 | 本機手冊中的範圍 |
| --- | --- |
| Project | 系統、組件、資料與連接的完整集合。 |
| System | 為工程目標串起一組 components，也可只有單一 component。 |
| Component | 資料與 editor 的集合；UI 中顯示為 Schematic cell，提供資料輸入／輸出服務。 |
| Data Container | 個別 component 的資料及操作服務；component 可有多個 container。 |
| Data Entity／Data Reference | container 內定義的資料結構，及指向其實例的 handle。 |

查詢通常先取得 container／entity reference，再讀寫允許的 property 或呼叫 method。物件、ACT `UserTask`、UI cell 和各資料容器的 state 不可直接視為同一種 API。原頁未支持舊字典的通用 `GetCell` 範例、記憶體 singleton／必然破壞模型等宣稱，故不保留其結論。

來源：[Scripting 實頁 18–24](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-18)。ACT state 另見第 16 節。

## 3. Parameters 與 Design Points

`Parameters` namespace 提供 project-level parameters、design points 與 DesignXploration 查詢。Parameter 的 `Expression` 可為常數或依賴其他參數；`Value` 是目前求值結果且唯讀。DesignPoint 提供指定點的 `GetParameterValue`、`SetParameterExpression` 與批次 expression 設定。

數量可用 `Value [Unit]` 字串。手冊也允許省略單位、採目前 project unit system；因此不能宣稱所有未附單位的輸入一定無效。需要跨單位重播時，應把 quantity 與目前單位的依據記清楚。

`UpdateAllDesignPoints` 是命令條目，但 v261 寫著「No details are provided」。已列 `CannotCompleteBehavior`／`ErrorBehavior` 預設 `Continue`、`ReupdateInterrupted=False` 等選項；本頁不補推序列、RSM/HPC 排程或失敗必然中斷行為。

來源：[Scripting 實頁 24–25](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-24)、[644–648](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-644)、[1347](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-1347)。

## 4. Workbench 2026 R1 DesignPoint 狀態、保留與 CSV 匯出

`IsUpToDate` 表示該點整個 project 是否最新；`StateOfParameters` 是 design point parameters 的狀態。`Retained` 可讀寫；`HasValidRetainedData` 是資料及檔案是否仍保留且有效的唯讀指示，可能出現在 retained DP，或尚未清除先前保留資料的非 retained DP。Base design point 在查 retained／exported 集合的條目中註明總是 retained。

| `DesignPointState` | v261 定義摘要 |
| --- | --- |
| `NeverSolvedAndFailed` | 從未成功更新，最近更新失敗。 |
| `NeverSolved` | 從未更新。 |
| `Failed` | 曾 UpToDate，但最近更新失敗。 |
| `OutOfDate` | 輸入值或非參數 project 變更使既有結果失效。 |
| `Interrupted` | 參數已更新但更新流程被中斷。 |
| `UpToDate` | 參數成功更新。 |

`DesignPoint.Delete` 會刪除該點、目錄及檔案；active DP 不能刪除。CSV 命令為 `Parameters.ExportAllDesignPointsData`，只匯出 up-to-date parameter values。原參數表使用 `FilePath`，緊接的範例卻使用 `FileName`；應保留這個文件差異並在實際版本查證，不提供未執行的替代參數保證。

來源：[Scripting 實頁 644–646](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-644)、[1305–1308](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-1305)、[1384](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-1384)。

## 5. ACT extensions 與 UI customization

Workbench ACT 的 project-level 入口包括 `ExtAPI.DataModel.Project`、`Context`、`Tasks`、`TaskGroups`。後兩者是已存在的具體 instances，不包括 master template-like tasks/groups。Task 的 automation wrapper 位於 `Ansys.ACT.WorkBench.Automation.Workflows`；wrapper 在 member 呼叫時才存取資料，而 ACT-defined callbacks 仍接收 `UserTask`。

手冊的 custom interface 範例在 task 下用 `<contextmenus>`／`<entry>`／`<onclick>` 定義 UI 操作，並在 `<workflow context="Project">` 下宣告工作流。它不是舊字典所示的通用 `<system>`／`TaskStatus` 假想程式。

來源：[ACT 實頁 13–15](../ANSYS_Document/_catalog/pdf_text_v4/1946241954ca369f6c394222651030fa29424a9c3b9249316c4e731e50507918.md#pdf-page-13)、[34–37](../ANSYS_Document/_catalog/pdf_text_v4/1946241954ca369f6c394222651030fa29424a9c3b9249316c4e731e50507918.md#pdf-page-34)。

## 6. v261 ACT custom workflow task input/output transfer

Workflow XML 宣告 output type 後，update routine 必須填入 downstream consumer 會讀的 transfer properties。`GetInputDataByType` 回傳某類型的 upstream `List<object>`；`GetOutputData` 回傳 `Dictionary<string, List<DataReference>>`。例如 MatML31 material transfer 要把已註冊的材料 XML file reference 指派給 output data object 的 `TransferFile`。

`GeneralTransfer.TransferData` 是 string/object dictionary，可在 task 間傳資料而不必把一切包成檔案；也可用 `enableGenericTransfer="False"` 關閉該 task 的通用 transfer。下游若需要額外處理，仍須實作適當 callback。

Generic Material Transfer 的 XML 與說明文字存在 `update`／`producer_update`、`type`／`outputtype` 用語不一致；此處整理資料流程，不把範例視為已驗證可直接載入的 extension。

來源：[ACT 實頁 73–76](../ANSYS_Document/_catalog/pdf_text_v4/1946241954ca369f6c394222651030fa29424a9c3b9249316c4e731e50507918.md#pdf-page-73)、[93–94](../ANSYS_Document/_catalog/pdf_text_v4/1946241954ca369f6c394222651030fa29424a9c3b9249316c4e731e50507918.md#pdf-page-93)、[114–116](../ANSYS_Document/_catalog/pdf_text_v4/1946241954ca369f6c394222651030fa29424a9c3b9249316c4e731e50507918.md#pdf-page-114)。

## 7. Workbench 與 ACT 版本相容性：來源仍受限

本機 Workbench catalog 只有上述 v261 兩本 PDF 與兩個 Markdown 別名。Scripting 實頁 15 的 backwards compatibility 規則是：執行較舊腳本前，先指定它**最初建立時**的 `SetScriptVersion`，並受 known issues／limitations 約束；這不能證明任意 v251／v261 extension 或 native application API 相容。

ACT Workbench 導言明確把完整 API changes／known issues 導向 ACT Developer's Guide 的 Migration Notes 與 Known Issues。本頁未取得可對照的 v251 Workbench 完整手冊，也未做跨宿主／WBEX runtime 檢查。local skill 片段中的 v251 路徑不能代替相容矩陣。此主題由 `pending_source_review` 改列 `source_limited`，沒有推定版本差異已消失。

來源：[Scripting 實頁 15](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-15)、[ACT 實頁 11](../ANSYS_Document/_catalog/pdf_text_v4/1946241954ca369f6c394222651030fa29424a9c3b9249316c4e731e50507918.md#pdf-page-11)。

## 8. v261 DesignXplorer discrete input parameter levels

`DiscreteLevel` 的 `Index` 為 zero-based；`Value` 可是 integer 或 string，例如孔數、材料名稱或幾何檔名。`AddDiscreteLevel` 建立 level，未給 index 時附加於尾端；`GetDiscreteLevel` 依名稱查找，`SetValue` 改值，`DeleteDiscreteLevels` 接收實體清單。這與 continuous input parameter 的 `AddLevels` manufacturable-values filter 不同。

手冊 `AddDiscreteLevel` 參數表將 `Index` 定為 int，但範例傳 `Index="1"`。`DeleteLevels` 範例還包含 `mmm` 單位字樣；兩者保留為文件疑義，不移植為推薦腳本。

來源：[Scripting 實頁 92–100](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-92)。

## 9. Workbench v261 多專案幾何替換與更新範例

官方範例先在單一 `Original` 目錄用 `os.listdir` 找 `.wbpj`，逐一開啟、清訊息、列舊參數，對各 system 嘗試 `GetContainer(ComponentName="Geometry")` 並 `SetFile`，再做 project `Update()`。更新後以 `IsProjectUpToDate()` 決定記錄新參數或 project messages，最後另存至 `Modified`。

範例的掃描不是遞迴；它 catch update exception 後仍會另存修改後專案，不能把「已存檔」當成成功更新。輸入專案、幾何與實際求解結果未在本輪執行。

來源：[Scripting 實頁 27–31](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-27)。

## 10. Workbench v261 專案檔案引用位置查找

另一範例遞迴找 project，提供兩種檢查法：`GetAllFiles()` 可做平面檔名搜尋；逐一走訪 `system.Components`、取得 `component.DataContainer.GetFiles()` 則可記錄是哪個 system/component 使用檔案，以及 `Location`、`Size`、`LastModifiedTime`。

原 helper 的形參叫 `fileList`，加入結果卻引用外部 `projList`；檔名以 substring 比對。這些是原範例的具體界線，不能將其描述為不會誤配的通用檔案依賴分析器。

來源：[Scripting 實頁 31–34](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-31)。

## 11. Workbench v261 Engineering Data 多線性硬化材料表建立

範例由 Engineering Data 匯入 Polyethylene，讀 Elasticity 的 Young's Modulus，用 quantity 算 `Plastic Strain = Total Strain - Stress/E`。原碼以 `CreateProperty(Name="Isotropic Hardening", Definition="Multilinear")` 建特性，並以 `SheetName="Isotropic Hardening"`、`SheetQualifiers={"Definition Method": "Multilinear"}` 與 Temperature／Plastic Strain／Stress 三欄填表。

範例把小於 `1e-4` 的計算塑性應變歸零、使用同一溫度 0 °C；這是該案例的處理，不是所有材料的校正門檻或溫度要求。表格值可為帶單位 quantity，亦可依 project units 解讀數值。

來源：[Scripting 實頁 34–37](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-34)。

## 12. v261 IronPython、腳本重播與 command API 版本

v261 Scripting Guide 明列 IronPython 2.7.4，Windows 使用 .NET Framework、Linux 使用 Mono CLR；並非全部 C-based Python modules 可用。

| `runwb2` 參數 | 原文行為摘要 |
| --- | --- |
| `-B` | Batch mode，不顯示 UI、開啟 console window。 |
| `-R` | 啟動時重播腳本；搭配 `-B` 時，完成後退出。 |
| `-I` | Interactive；搭配 `-B` 會同時開 UI 與 console。 |
| `-X` | 互動執行後在腳本完成時退出，通常搭配 `-R`。 |
| `-F` | 啟動時載入指定 project。 |
| `-E` | 啟動時執行 scripting command；可用分號分隔或重複此參數。 |

`SetScriptVersion` 接受 2-part 或 3-part version string，指定執行腳本時的 command API 版本；不是自動 runtime 相容性測試。來源：[Scripting 實頁 15–16](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-15)、[1342](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-1342)。

## 13. v261 專案封存、還原與重設的資料界線

| 命令 | 資料行為／需核對處 |
| --- | --- |
| `Save` | 將目前 project 存碟；`FilePath`、`Overwrite` 為 optional。 |
| `Archive` | project 必須先保存；由目前 project files/content 建 archive。可分別控制 external imported、results/solution、user_files。 |
| `Unarchive` | 從 `ArchivePath` 還原；`Overwrite` 必填，optional `ProjectPath` 省略時用設定的暫存位置或 system temp。 |
| `Reset` | 回到空 project；未保存修改會遺失。 |

原 `Archive` 表列 `FailIfMissingFiles`，範例卻用 `FailIfFilesNeedRepair`；`Unarchive` 表列 `ProjectPath`，範例卻用 `ProjectFilePath`。本頁保留這兩組參數名稱衝突，不提供未核對的還原腳本。

來源：[Scripting 實頁 1315–1316](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-1315)、[1340](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-1340)、[1346–1347](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-1346)。

## 14. v261 DesignPoint 建立、參數 expression 與維度限制

`Parameters.CreateDesignPoint` 會建立含全部參數的新 DP，起初值為 null；`Exported`、`Retained` 預設 False。可在特定 DP 上以 `SetParameterExpression` 指定 input expression。Parameter 的 `ValueQuantityName` 可限制 parameter values 的 dimensions，但原文說這不限制 named expressions。

表達式的 quantity、unit system、parameter dimension 是不同層次；本頁只整理宣告，沒有建立、更新、刪除 DP。來源：[Scripting 實頁 646–648](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-646)、[1302–1304](../ANSYS_Document/_catalog/pdf_text_v4/d5954cd25f78732899c61b206af79c8ecf79eae7575917430a01205333bff122.md#pdf-page-1302)。

## 15. v261 ACT workflow XML 與 task／system 定義

Workbench 自訂 system 對應 ACT 的 **task group**，XML 使用 `<taskgroups>`／`<taskgroup>`，以 `<includetask>`／`<includeGroup>` 組成工作流。`<workflow context="Project">` 下可宣告 `<tasks>`、task-level property/input/output/parameter 與 global callbacks。Task 和 task group 定義至少需要 name／version。

手冊明列：ACT-defined tasks 目前不能加入 Ansys-installed task groups；Workbench 不辨識 task group 內再巢狀 task groups。實作前仍須查該版本 XML Reference，不能用概念名詞 `system` 直接猜測 XML tag。

來源：[ACT 實頁 64–66](../ANSYS_Document/_catalog/pdf_text_v4/1946241954ca369f6c394222651030fa29424a9c3b9249316c4e731e50507918.md#pdf-page-64)、[71–73](../ANSYS_Document/_catalog/pdf_text_v4/1946241954ca369f6c394222651030fa29424a9c3b9249316c4e731e50507918.md#pdf-page-71)、[93](../ANSYS_Document/_catalog/pdf_text_v4/1946241954ca369f6c394222651030fa29424a9c3b9249316c4e731e50507918.md#pdf-page-93)。

## 16. v261 ACT task state、onstatus 與 isvalid

ACT `Ansys.ACT.Interfaces.Common.State` 包含 `UpToDate`、`RefreshRequired`、`UpdateRequired`、`Unfulfilled`、`Disabled`、`Error`、`EditRequired`、`Interrupted`、`UpstreamChangesPending`、`Unknown`；`OutOfDate`／`Modified` 原表限制為 Mechanical。這個 enumeration 不等同第 4 節 `DesignPointState`。

Task `onstatus` 可回傳兩項 list：State 值與 quick-help string；範例回 `None` 時由 framework 算 state。原文不建議回傳舊 `ComponentState`，除非維持 backwards compatibility。未自訂 `onstatus` 時，invalid task property 會使 default handler 使用 unfulfilled。

Property `isvalid` 最少接收 `(entity, property)` 並回 Boolean；它是 property callback，不是所有 task callbacks 的共同簽章。Task-level callbacks 表列 `oninitialize`、`onupdate`、`onrefresh`、`onreset`、`onedit`、`onstatus`、`onreport`、`ondelete`、`canconsumedata`，沒有舊字典所假設的通用 `oninit`／`oncleandata` 生命週期。

來源：[ACT 實頁 24–26](../ANSYS_Document/_catalog/pdf_text_v4/1946241954ca369f6c394222651030fa29424a9c3b9249316c4e731e50507918.md#pdf-page-24)、[78–81](../ANSYS_Document/_catalog/pdf_text_v4/1946241954ca369f6c394222651030fa29424a9c3b9249316c4e731e50507918.md#pdf-page-78)。

## 17. v261 ACT global callback 的觀察、篩選與順序

Global workflow callbacks 的預設作用對象包含 Ansys-installed 與 ACT-defined tasks；例如 `onaftertaskupdate` 每完成一個 eligible task 便呼叫一次。可在 callback 內依 task/template 篩選。相同操作的多個 callbacks 依 `order` 從小到大執行，同值時由 extension load order 解決衝突。

v261 定義 11 個 Project Schematic 操作的 pre/post callbacks，另有 design-point-change 操作。實頁 65–66 的 schema 使用 `onbeforetaskcreation`／`onbeforetaskdeletion`，實頁 69 的說明表卻寫 `onbeforetaskcreate`／`onbeforetaskdelete`；本頁不猜測它們是否是別名。After CanUseTransfer／Status 等 callbacks 還可能拿到 system-calculated value，不能一概當成只有 `(task)`。

來源：[ACT 實頁 35–37](../ANSYS_Document/_catalog/pdf_text_v4/1946241954ca369f6c394222651030fa29424a9c3b9249316c4e731e50507918.md#pdf-page-35)、[66–71](../ANSYS_Document/_catalog/pdf_text_v4/1946241954ca369f6c394222651030fa29424a9c3b9249316c4e731e50507918.md#pdf-page-66)。

## 18. v261 ACT task-level files 與 callback 失敗傳遞

`UserTask.ActiveDirectory` 是目前 design point 的 task directory；`RegisteredFiles` 是註冊檔案集合；`RegisterFile`／`UnregisterFile` 管理其 task 關聯。手冊提醒：unregister 只有對已與該 task 關聯的檔案才會完全移除關聯。檔案 transfer 需設定對應 output data object 的 `TransferFile`，不是通用的 `SetOutputData()` 假想介面。

Task-level callback 發生 exception 時，原文說 exception 會交給 Workbench framework 以偵測失敗、管理 task states，細節寫入 log。不能把所有 callback 強制包成 catch-and-return-False，否則會改變原本錯誤傳遞。`canconsumedata` 的 code example 與 callback table 引數形式亦有差異，實作前須在實際版本查證。

來源：[ACT 實頁 75–79](../ANSYS_Document/_catalog/pdf_text_v4/1946241954ca369f6c394222651030fa29424a9c3b9249316c4e731e50507918.md#pdf-page-75)、[93–94](../ANSYS_Document/_catalog/pdf_text_v4/1946241954ca369f6c394222651030fa29424a9c3b9249316c4e731e50507918.md#pdf-page-93)。

## 轉換品質與待處理範圍

本輪核對四個 catalog 原件 SHA-256、兩個 canonical text SHA-256，1,714 個 PDF Page 標記與 PDF page count 連續吻合。Scripting 實頁 47–48 是低文字頁，沒有發現「無文字但有圖片」的掃描頁；此機械檢查不代表所有圖、公式或跨欄表格均完整。Workbench catalog 沒有 HTML 原件，無需補轉 HTML。

尚缺可比較的其他 release Workbench 完整文件／相容矩陣；本輪未執行 Workbench、ACT extension build/load、DesignPoint update 或求解。原始文件含 proprietary/confidential 標示，分享仍遵守原來源條款。


## 2026-11-04：Wave 8 本機來源盤點與限制說明

本批完成 workbench 模組既有本機 catalog 文件（共 4 筆）與 sources 清冊（共 4 筆）之完整雜湊、正文路徑與標籤結構核對。本機未快取或具備企業授權/登入限制之線上主題誠實標記為缺口（保持現有非 complete 狀態），未擅自虛構未核實之線上 API 簽名或執行求解運算。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/workbench_module_conversion_report_20261104.md)。
