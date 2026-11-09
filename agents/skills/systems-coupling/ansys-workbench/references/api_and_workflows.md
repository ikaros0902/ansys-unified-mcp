# Ansys Workbench 專案管理與日誌自動化 核心 API 與工作流指南

> [!NOTE]
> 本文件由知識字典 `workbench.md` 精煉而成，提供標準工程流程與自動化腳本簽名。
> 可調用 MCP 工具 `ans_get_knowledge_dictionary(product='workbench')` 查閱完整章節。

## 1. 模組架構與工作流說明

本模組遵循 ANSYS 現代自動化架構與雙軌工程標準：
1. **初始化與通訊連線**：支援本地 gRPC / 批次執行以及遠端伺服器程序掛載。
2. **參數配置與資料交換**：透過結構化物件或日誌檔精準傳遞幾何、材料與網格控制項。
3. **求解監控與非同步等待**：使用 Sentinel 工具或狀態輪詢器追蹤計算收斂情況。
4. **結果匯出與報告整合**：產出結構化數值報表與 3D 視覺化資料。

## 2. 知識字典精華摘錄

# Ansys Workbench 知識字典

本頁依本機 **Release 2026 R1（v261）** 的 Workbench Scripting Guide 與 ACT Customization Guide for Workbench 整理有界主題。頁碼均指 **PDF 實頁**；兩本文件的主要正文印刷頁約比實頁少 10，仍以各頁頁尾核對。文件 API 宣告不代表已在 Workbench 執行。

## 章節閱讀進度與轉換品質

逐章進度見**Workbench 章節及轉換覆核清冊**。18 個字典主題代表已核讀的章節片段，不表示兩本手冊全章或全部 API 都已整理。

PDF canonical v4 Markdown 已保留逐頁標記，兩份來源分別為 1,466 與 248 頁；不重轉既有產物。PDF 共含多個嵌入圖像（初步統計 Scripting Guide 5 個、ACT Guide 56 個），canonical Markdown 未內嵌圖像，因此流程圖、UI 截圖及圖示資訊不能只靠文字轉換確認。表格亦須逐頁核對：例如 Scripting Guide 實頁 18 的 SendCommand 支援矩陣在轉換文字中已線性化，字典以手工重排表格並保留空白欄的限制。掃描／圖片頁、公式與其餘表格尚未逐頁完成視覺校對；請回到 PDF 原頁核實。

## 來源、版本與閱讀入口

| 來源 | PDF 實頁 | 可追溯正文 | 來源 ID |
| --- | ---: | --- | --- |
| **Workbench Scripting Guide** | 1,466 | **canonical 逐頁 Markdown** | `ansys_05b664ec1d5ee31846d738a4` |
| **ACT Customization Guide for Workbench** | 248 | **canonical 逐頁 Markdown** | `ansys_843b9c0be2bced4d8651f4a6` |

兩份封面均明列 Release 2026 R1／March 2026。來源同名 Markdown 仍保留：**Scripting 舊轉換**（`ansys_bf146052ec7716d8122c2318`）、**ACT 舊轉換**（`ansys_9b0d4ecb6d9a7614cd649d73`）。它們與 canonical PDF 轉換不同，`pdf_extraction.json` 記為 `existing_different_preserved`；本頁逐頁引用使用上表 canonical 版本，未覆寫既有轉換。

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

空白欄僅按原表保留，不能推導其他介面是否可用。來源：**Scripting 實頁 17–18**。

## 2. Workbench scripting 物件與專案狀態

| 英文術語 | 本機手冊中的範圍 |
| --- | --- |
| Project | 系統、組件、資料與連接的完整集合。 |
| System | 為工程目標串起一組 components，也可只有單一 component。 |
| Component | 資料與 editor 的集合；UI 中顯示為 Schematic cell，提供資料輸入／輸出服務。 |
| Data Container | 個別 component 的資料及操作服務；component 可有多個 container。 |
| Data Entity／Data Reference | container 內定義的資料結構，及指向其實例的 handle。 |

查詢通常先取得 container／entity reference，再讀寫允許的 property 或呼叫 method。物件、ACT `UserTask`、UI cell 和各資料容器的 state 不可直接視為同一種 API。原頁未支持舊字典的通用 `GetCell` 範例、記憶體 singleton／必然破壞模型等宣稱，故不保留其結論。

來源：**Scripting 實頁 18–24**。ACT state 另見第 16 節。

## 3. Parameters 與 Design Points

`Parameters` namespace 提供 project-level parameters、design points 與 DesignXploration 查詢。Parameter 的 `Expression` 可為常數或依賴其他參數；`Value` 是目前求值結果且唯讀。DesignPoint 提供指定點的 `GetParameterValue`、`SetParameterExpression` 與批次 expression 設定。

數量可用 `Value [Unit]` 字串。手冊也允許省略單位、採目前 project unit system；因此不能宣稱所有未附單位的輸入一定無效。需要跨單位重播時，應把 quantity 與目前單位的依據記清楚。

`UpdateAllDesignPoints` 是命令條目，但 v261 寫著「No details are provided」。已列 `CannotCompleteBehavior`／`ErrorBehavior` 預設 `Continue`、`ReupdateInterrupted=False` 等選項；本頁不補推序列、RSM/HPC 排程或失敗必然中斷行為。

來源：**Scripting 實頁 24–25**、**644–648**、**1347**。

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

來源：**Scripting 實頁 644–646**、**1305–1308**、**1384**。

## 5. ACT extensions 與 UI customization

Workbench ACT 的 project-level 入口包括 `ExtAPI.DataModel.Project`、`Context`、`Tasks`、`TaskGroups`。後兩者是已存在的具體 instances，不包括 master template-like tasks/groups。Task 的 automation wrapper 位於 `Ansys.ACT.WorkBench.Automation.Workflows`；wrapper 在 member 呼叫時才存取資料，而 ACT-defined callbacks 仍接收 `UserTask`。

手冊的 custom interface 範例在 task 下用 `<contextmenus>`／`<entry>`／`<onclick>` 定義 UI 操作，並在 `<workflow context="Project">` 下宣告工作流。它不是舊字典所示的通用 `<system>`／`TaskStatus` 假想程式。

來源：**ACT 實頁 13–15**、**34–37**。

## 6. v261 ACT custom workflow task input/output transfer

Workflow XML 宣告 output type 後，update routine 必須填入 downstream consumer 會讀的 transfer properties。`GetInputDataByType` 回傳某類型的 upstream `List<object>`；`GetOutputData` 回傳 `Dictionary<string, List<DataReference>>`。例如 MatML31 material transfer 要把已註冊的材料 XML file reference 指派給 output data object 的 `TransferFile`。

`GeneralTransfer.TransferData` 是 string/object dictionary，可在 task 間傳資料而不必把一切包成檔案；也可用 `enableGenericTransfer="False"` 關閉該 task 的通用 transfer。下游若需要額外處理，仍須實作適當 callback。

Generic Material Transfer 的 XML 與說明文字存在 `update`／`producer_update`、`type`／`outputtype` 用語不一致；此處整理資料流程，不把範例視為已驗證可直接載入的 extension。

來源：**ACT 實頁 73–76**、**93–94**、**114–116**。

## 7. Workbench 與 ACT 版本相容性：來源仍受限

本機 Workbench catalog 只有上述 v261 兩本 PDF 與兩個 Markdown 別名。Scripting 實頁 15 的 backwards compatibility 規則是：執行較舊腳本前，先指定它**最初建立時**的 `SetScriptVersion`，並受 known issues／limitations 約束；這不能證明任意 v251／v261 extension 或 native application API 相容。

ACT Workbench 導言明確把完整 API changes／known issues 導向 ACT Developer's Guide 的 Migration Notes 與 Known Issues。本頁未取得可對照的 v251 Workbench 完整手冊，也未做跨宿主／WBEX runtime 檢查。local skill 片段中的 v251 路徑不能代替相容矩陣。此主題由 `pending_source_review` 改列 `source_limited`，沒有推定版本差異已消失。

來源：**Scripting 實頁 15**、**ACT 實頁 11**。

## 8. v261 DesignXplorer discrete input parameter levels

`DiscreteLevel` 的 `Index` 為 zero-based；`Value` 可是 integer 或 string，例如孔數、材料名稱或幾何檔名。`AddDiscreteLevel` 建立 level，未給 index 時附加於尾端；`GetDiscreteLevel` 依名稱查找，`SetValue` 改值，`DeleteDiscreteLevels` 接收實體清單。這與 continuous input parameter 的 `AddLevels` manufacturable-values filter 不同。

手冊 `AddDiscreteLevel` 參數表將 `Index` 定為 int，但範例傳 `Index="1"`。`DeleteLevels` 範例還包含 `mmm` 單位字樣；兩者保留為文件疑義，不移植為推薦腳本。

來源：**Scripting 實頁 92–100**。

## 9. Workbench v261 多專案幾何替換與更新範例

官方範例先在單一 `Original` 目錄用 `os.listdir` 找 `.wbpj`，逐一開啟、清訊息、列舊參數，對各 system 嘗試 `GetContainer(ComponentName="Geometry")` 並 `SetFile`，再做 project `Update()`。更新後以 `IsProjectUpToDate()` 決定記錄新參數或 project messages，最後另存至 `Modified`。

範例的掃描不是遞迴；它 catch update exception 後仍會另存修改後專案，不能把「已存檔」當成成功更新。輸入專案、幾何與實際求解結果未在本輪執行。

來源：**Scripting 實頁 27–31**。

## 10. Workbench v261 專案檔案引用位置查找

另一範例遞迴找 project，提供兩種檢查法：`GetAllFiles()` 可做平面檔名搜尋；逐一走訪 `system.Components`、取得 `component.DataContainer.GetFiles()` 則可記錄是哪個 system/component 使用檔案，以及 `Location`、`Size`、`LastModifiedTime`。

原 helper 的形參叫 `fileList`，加入結果卻引用外部 `projList`；檔名以 substring 比對。這些是原範例的具體界線，不能將其描述為不會誤配的通用檔案依賴分析器。

來源：**Scripting 實頁 31–34**。

## 11. Workbench v261 Engineering Data 多線性硬化材料表建立

範例由 Engineering Data 匯入 Polyethylene，讀 Elasticity 的 Young's Modulus，用 quantity 算 `Plastic Strain = Total Strain - Stress/E`。原碼以 `CreateProperty(Name="Isotropic Hardening", Definition="Multilinear")` 建特性，並以 `SheetName="Isotropic Hardening"`、`SheetQualifiers={"Definition Method": "Multilinear"}` 與 Temperature／Plastic Strain／Stress 三欄填表。

範例把小於 `1e-4` 的計算塑性應變歸零、使用同一溫度 0 °C；這是該案例的處理，不是所有材料的校正門檻或溫度要求。表格值可為帶單位 quantity，亦可依 project units 解讀數值。

來源：**Scripting 實頁 34–37**。

## 12. v261 IronPython、腳本重播與 command API 版本

v261 Scripting Guide 明列 IronPython 2.7.4，Windows 使用 .NET Framework、Linux 使用 Mono CLR；並非全部 C-based Python modules 可用。

| `runwb2` 參數 | 原文行為摘要 |
| --- | --- |

## 3. 雙軌數值基準與驗收標準

- **商業求解軌**：連線正式求解器執行高保真模擬。
- **無授權基準軌**：執行 `scripts/verify_workbench_baseline.py` 驗證解析數值正確性（Exit Code 0）。
