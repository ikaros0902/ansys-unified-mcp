# Ansys SIwave 知識字典

> 來源為 Ansys Electromagnetics Suite 2026 R1。兩份入門 PDF 分別處理 PCB model 與 SIwave-CPA package model；其流程範圍分開整理。

## Scripting Guide

《SIwave Scripting Guide》v261 的入口章節描述執行 `.py` 腳本的三種方式，並將 SIwave 內建環境標為 IronPython 2.7／.NET Framework 4.0。此摘要限於腳本啟動與環境；後續 `Scr...` API command reference 尚未逐條整理，不代表涵蓋所有自動化功能。

### 執行入口

- GUI：Tools > Scripting > Run Script，選取 `.py` 檔後執行。
- 命令列：`<path to siwave.exe> <path to *.siw file> -RunScript <path to *.py file>` 會開啟 SIwave 並執行腳本；改用 `-RunScriptAndExit` 則在執行後關閉 SIwave。`.siw` 專案路徑與腳本路徑均須換成實際檔案路徑。
- 互動式 shell：Tools > Scripting > IronPython Command Shell 開啟 command window，可直接輸入腳本命令。
- 手冊另記載 VBScript：設環境變數 `SIWAVE_ENABLE_VB_SCRIPT_SUPPORT=1` 可啟用；VBScript 也可由命令列執行而不設定此環境變數。這是手冊中的相容入口，本文不延伸建議其新專案用途。

### IronPython 環境界線

SIwave 內建 IronPython 以 .NET runtime 為目標，手冊標示版本為 2.7、基於 .NET Framework 4.0；可使用 Python 語法及標準函式庫，也可呼叫 .NET classes。文件提醒依賴 C extension 的 Python 套件（例如 NumPy、SciPy）不能預期可直接在該環境工作，因此不可把一般 CPython 套件相容性直接套用到內建 shell。

在 shell 中可用 Python `dir(module)` 檢視方法名稱、`help(name)` 查詢內建說明。縮排屬 Python 語法的一部分；指南建議使用 spaces，區塊內容須保持一致縮排。這些是手冊的入門說明，不是完整 Python 教學。

來源：[SIwave Scripting Guide PDF](../ANSYS_Document/SIwave/v261/manuals/SIwaveScriptingGuide.pdf#page=19)（PDF Pages 19–22：執行腳本、IronPython shell、版本相容與方法查詢）；封面 PDF Page 1 標示 Ansys Electromagnetics Suite 2026 R1。逐頁 Markdown sidecar 已存在並列於來源清冊。

## PCB model 設定與代表性分析流程

《Getting Started with SIwave: A PCB Model》以 8 層 PCB 為例，Layer 2 與 Layer 7 為 power／ground planes。它是逐步教學案例，不代表所有 PCB 都要採相同設定或分析順序。

### 建立與驗證 PCB 專案

1. 從 Ansys Neutral File（`.anf`）匯入 geometric PCB；教學範例使用 `siwave_board.anf`，並包含幾何、layer stackup、padstacks、vias、materials 與 discrete components。匯入 nets／components 後另存 `.siw` 專案。
2. 使用 Layer Stackup Editor 檢視層疊。教學案例特別檢視 L2 與 L7 的 plane 關係。
3. 在 Nets workspace 的 Power/Ground Identification 執行 Auto Identify，並人工檢查分類：大型 plane 應列為 power／ground，含 microstrip／stripline routing 的 signal net 應列為 non-power／ground。手冊說明此分類會影響 solver 的 mesh refinement 與 optimization 策略。
4. 開始 simulation 前執行 Tools > Validation Check；教學指出沒有 errors 時設計才可進入 simulation。若提供 Auto Fix，確認錯誤／警告項目後再儲存。

來源：[SIwave Getting Started Guide PDF](../ANSYS_Document/SIwave/v261/manuals/SIwave%20Getting%20Started%20Guide.pdf#page=9)（匯入／設計設定 PDF Pages 9–18；驗證前置條件見 PDF Pages 16–18）。

### 範例分析路徑

| 分析 | 教學中的用途與前置 | 教學案例設定／觀察 |
| --- | --- | --- |
| Resonant Modes | 作為非理想 power／ground plane 行為的初步檢視 | Minimum Frequency `2.55238E+08`（若不同則 Restore Recommended Minimum Frequency）；Maximum Frequency `2e9`；Modes `10`。結果可檢視 table 或疊加在 PCB 的 2D plots。 |
| SIwave SYZ | 透過 pin groups 建立 VCC 對 GND 的 port，查看供電 plane 頻率相依阻抗 | U41 範例將 reference impedance 設為 `1 Ohm`；sweep 為 0–1 GHz、200 points、Linear、Discrete。該教學將 resonant-mode 頻點與 SYZ impedance peaks 對照。 |
| PSI SYZ | 以 PSI solver 計算同一組 pin groups／port 的頻率相依阻抗 | 先完成 SIwave SYZ 的 pin groups／port；教學使用 10 MHz–1 GHz、Interpolating Sweep (AFS)、Fast Sweep 與 Adaptive Sampling。Fast Sweep 需要較多記憶體；不足時不可用。 |
| PSI AC Current | 以指定 excitation 檢視 plane surface current | 教學先建立 1 V、frequency-independent voltage source，再使用 500 MHz–1 GHz、50 points、Linear；手冊提醒每個 frequency point 會寫入多個資料檔，需預留 disk space。 |

以上數值都是 2026 R1 教學範例設定，不是通用 solver defaults 或工程建議值。資料來源：[Resonant Modes](../ANSYS_Document/SIwave/v261/manuals/SIwave%20Getting%20Started%20Guide.pdf#page=19)（PDF Pages 19–25）、[SYZ](../ANSYS_Document/SIwave/v261/manuals/SIwave%20Getting%20Started%20Guide.pdf#page=27)（PDF Pages 27–36）、[PSI SYZ](../ANSYS_Document/SIwave/v261/manuals/SIwave%20Getting%20Started%20Guide.pdf#page=37)（PDF Pages 37–42）。

### PSI AC current 與電壓頻率掃描（章節 6–7）

- **PSI AC Current（PDF Pages 43–52）**：案例以 U41 VCC/GND pin groups 建立 frequency-independent 1 V 電壓源（parasitic resistance `1E-06 Ohms`、phase 0°），執行 500 MHz–1 GHz、50 點、linear distribution 的 AC current sweep。結果可按頻率查看 plane surface-current 2D plot，並可將 total radiated power 匯出 CSV。手冊提醒每個頻點會寫出多個資料檔，設定點數前需考量磁碟空間。
- **Frequency Sweep of Voltages（PDF Pages 53–61）**：先停用前一節的電壓源，再在 U41 VCC/GND 間建立 frequency-independent current source（案例 `1E-5 A`、parasitic resistance `5E+07 Ohms`、phase 0°），於 L7(VCC) 與 L2(GND) 間、座標 `(8500 mil, 0 mil)` 放置 voltage probe。案例執行 500 MHz–1 GHz、200 點、linear sweep，繪製 probe voltage magnitude；手冊指出案例峰值對應 resonant modes 4、8、10。

此處的 source/probe 參數、頻率、點數及 peak/mode 對應都只描述該 PCB 教學案例，不能直接當成其他設計的設定建議或驗證門檻。來源：[PSI AC Current](../ANSYS_Document/SIwave/v261/manuals/SIwave%20Getting%20Started%20Guide.pdf#page=43) · [Frequency Sweep of Voltages](../ANSYS_Document/SIwave/v261/manuals/SIwave%20Getting%20Started%20Guide.pdf#page=53)。

## SIwave-CPA RLGC extraction

《Getting Started with SIwave CPA: A Package Model》描述 CPA 對 package power／signal nets 執行 3D FEM-based RLGC extraction；手冊列出 per-bump 或 user-defined pin-group models，產物包括 passive RLGC SPICE netlist，並可供 RedHawk Chip + Package co-simulation 使用。此為手冊功能描述，不代表本文已驗證求解精度或特定專案相容性。

### 範例前處理與 extraction

1. 匯入 package 的 `.anf` 幾何模型及 component 資料，教學範例為 `analysis.anf`；先檢視 layer stackup，確認 power／ground nets 分類。
2. CPA extraction 由 project 中的 pin groups 控制。若匯入 RedHawk PLOC 後已建立 pin groups，可沿用；否則透過 Tools > Create/Manage Pin Groups，依 part、reference designator 與 net 建立 groups。教學案例在 BGA 與 FCHIP 上，對 VDD、VDD_15、VSS 分別建立 pin groups。
3. 從 Simulation > CPA > Compute RLCG 開啟 Launch CPA。案例使用 CPA Channel Setup，Extraction Type 選 RLCG，CPA Options 的 Model Type 設為 Package；接著選 FCHIP 並設為 included in solution，使用 layout 中定義的 die groups 後啟動。
4. 教學說明：CPA Channel Setup 且未選 Q3D Solver 時，會自動求解 RedHawk 相容模型需要的各項參數，即使 Parameters to Compute 的核取方塊未勾選；該選項只適用於 Individual Source/Sink Setup 或 Q3D Solver。Adaptive Refinement 設定則只在選擇 Q3D Solver 時生效。這些限制是該指南對此案例設定視窗的說明。

教學對效能的建議為至少 8 cores、最佳 12–16 cores；此為文件中的效能建議，不是解算正確性的門檻。

### 結果位置與型態

RLGC Table 可查看 RL 與 CG tabs；教學列出的結果目錄包含 `analysis.siwaveresults/0000_CPA_Sim_1/adsCPA/Extraction`，內有 package RLCG netlist（`.sp`）、RL／CG matrices、DC／AC RLCG data、PLOC 及 package IBIS model 等。Results workspace 另可顯示 pin partial-inductance 與 loop-inductance maps。檔名及路徑依教學案例；其他版本或設定可能不同。

來源：[SIwave-CPA Getting Started Guide PDF](../ANSYS_Document/SIwave/v261/manuals/SIwave-CPA%20Getting%20Started%20Guide.pdf#page=7)（功能範圍 PDF Page 7）、[PDF Pages 17–26](../ANSYS_Document/SIwave/v261/manuals/SIwave-CPA%20Getting%20Started%20Guide.pdf#page=17)（pin groups／extraction）、[PDF Pages 28–30](../ANSYS_Document/SIwave/v261/manuals/SIwave-CPA%20Getting%20Started%20Guide.pdf#page=28)（results）。

## PCB 與 package 模型如何選文件

| 教學來源 | 模型與輸入 | 教學聚焦 |
| --- | --- | --- |
| SIwave Getting Started Guide | 8-layer PCB 範例；輸入 `siwave_board.anf`，檢視 L2／L7 power／ground planes | PCB setup／validation、resonant modes、SYZ／PSI、voltage sweep 與 plane current。 |
| SIwave-CPA Getting Started Guide | package 範例；輸入 `analysis.anf`，依 package part／die nets 建立 pin groups | CPA RLCG extraction、package SPICE／IBIS 等結果與 pin inductance maps。 |

依模型目的選用對應指南；以上差異是兩份 v261／2026 R1 Getting Started 教學案例的範圍比較，不構成 SIwave 與 SIwave-CPA 全部能力或所有輸入格式的完整比較。來源：[PCB model guide](../ANSYS_Document/SIwave/v261/manuals/SIwave%20Getting%20Started%20Guide.pdf#page=7) · [package model guide](../ANSYS_Document/SIwave/v261/manuals/SIwave-CPA%20Getting%20Started%20Guide.pdf#page=7)。

## Scripting API 命令參考導覽與代表操作

Scripting Guide 的目錄把 API 列為 2 章 Script Commands；目錄跨 PDF Pages 3–16，逐項方法參考從 PDF Page 39 開始，延伸至 PDF Pages 269 前。以下按工作目的歸類目錄中的方法，供查找完整簽章，不代表所有方法已整理或每一項都經實際執行。

| 工作階段 | 目錄中的方法例子 | 原文可確認的代表行為 | 原文位置 |
|---|---|---|---|
| 專案與資料匯入 | `OpenProject`、`Save`、`ScrImportAnf`、`ScrImportEDB`、`ScrImportIPC2581` | `ScrImportAnf(<anfBstr>)` 匯入指定 ANF，回傳 BOOL；`1` 成功、`0` 失敗。 | TOC PDF pp.3–10；`ScrImportAnf` PDF p.139 |
| PCB 結構與 nets | `ScrAddLayer`、`ScrSetLayerThickness`、`ScrCreatePinGroups`、`ScrSetPowerGroundNets`、`ScrSanitizeLayout` | `ScrCreatePinGroups(partName, refDes, pinNumbers, groupName, applyToAllComponents)` 依元件／參考代號及 pin 清單建立 pin group；`applyToAllComponents=True` 時忽略 `refDes` 並套用至相同 part name 的元件。手冊範例回傳 BOOL（0 失敗、1 成功）。`ScrSetPowerGroundNets` 第二參數 TRUE 時保留既有分類；FALSE 時，清單外 nets 設為 non-power/ground。 | TOC PDF pp.4–16；`ScrCreatePinGroups` PDF pp.67–68；`ScrSetPowerGroundNets` PDF p.224 |
| 驗證與修正 | `ScrRunValidationCheck`、`ScrRunValidationCheckWithOptions`、`ScrCorrectValChkErrorsWarnings` | `ScrRunValidationCheck()` 回傳 errors、warnings 數量；WithOptions 可指定檢查類別和相關模擬類型。此檢查結果仍需依專案設計審查。 | TOC PDF pp.5、11；方法說明 PDF pp.171–172 |
| 求解與 sweep 設定 | `ScrRunDcSimulation`、`ScrRunResonantModeSimulation`、`ScrRunSyzParameterSimulation`、`ScrSetSweepFreqRange` | `ScrRunDcSimulation(reprocessGeom)` 中 `1` 會執行 DC IR simulation，`0` 僅設定而不執行；此差異應在自動化腳本中明確處理。 | TOC PDF pp.11、15；方法說明 PDF p.166 |
| 匯出與結果交換 | `ScrExportNamedSimToTouchstone`、`ScrExportAnf`、`ScrExportDcSimReport`、`ScrExportIcepakProject` | Touchstone 匯出要求既有 simulation 名稱及可建立的路徑；`simType` 限 `syz`、`psi_syz`、`hfss_syz`。若路徑已含副檔名，文件提醒副檔名中的埠數須正確，否則可能產生兩個副檔名。 | TOC PDF pp.7–8；方法說明 PDF p.107 |

`ScrSetSweepFreqRange` 的參數說明將 `minFreq`／`maxFreq` 標為 Hz，但範例換算寫成 `1e-6 = 1MHz`、`1e-9 = 1GHz`，與 SI 前綴的量級不符。故不據此換算或推定 API 對輸入值的處理；需查核原 PDF、官方勘誤或產品行為後再補。目錄分類只是導覽，命令的參數型別、回傳值、前置條件及錯誤碼需逐項查閱對應方法頁，不能只憑方法名稱推定。

來源：[SIwave Scripting Guide PDF Pages 3–16（目錄）及 Pages 139、166、171–172、224、107（代表方法）](../ANSYS_Document/SIwave/v261/manuals/SIwaveScriptingGuide.pdf#page=139)／[逐頁 Markdown](../ANSYS_Document/SIwave/v261/manuals/SIwaveScriptingGuide.md#pdf-page-139) · `ansys_0de3584aeab4aa7fa4c17ada`。以上為 2026 R1 文件內容；沒有在 SIwave 中執行任何命令。

## 限制

本字典完成三項入門指南主題，以及 Scripting Guide 的執行入口／IronPython environment 子範圍；完整 `Scr...` command reference 尚未逐項整理；本節只提供目錄分類與少數命令的原文摘要。未開啟 SIwave、執行腳本、匯入 PCB/package、產生結果或求解；分析數值與檔案列表均為教學案例內容。


## 三份指南章節清單與整理範圍

下表依各 PDF 目錄列出章節和主要操作，`PDF p.` 是實際 PDF 頁標，不是目錄印刷頁碼。`部分整理` 表示字典有該主題的來源摘要，並不表示整章逐頁驗收；Scripting Guide 的 command reference 尤其尚未逐條整理。未整理項目可按章節列追蹤，不以 sidecar 存在或頁標連續當作內容驗收。

### Getting Started with SIwave: A PCB Model（v261）

| 章節 | 目錄中的主要操作／概念 | PDF 定位 | 字典狀態 |
|---|---|---|---|
| 1 Introduction | PCB 模型、預期結果與阻抗／電壓 ripple 的關係 | [PDF p.7](../ANSYS_Document/SIwave/v261/manuals/SIwave%20Getting%20Started%20Guide.pdf#page=7) | 部分整理；涵蓋 8 層範例與預期分析關係 |
| 2 Setting Up the Design | 匯入／儲存、元素顯示、layer stackup、power/ground nets、validation | [PDF pp.9–18](../ANSYS_Document/SIwave/v261/manuals/SIwave%20Getting%20Started%20Guide.pdf#page=9) | 部分整理；涵蓋匯入、分類與驗證前置 |
| 3 Resonant Modes Analysis | 啟動分析、查看 table／2D plots、plane voltage difference 與 phase animation | [PDF pp.19–25](../ANSYS_Document/SIwave/v261/manuals/SIwave%20Getting%20Started%20Guide.pdf#page=19) | 部分整理；設定與查看結果有摘要，操作細節未逐頁整理 |
| 4 SIwave SYZ Analysis | pin groups、port、SYZ parameters、impedance response | [PDF pp.27–36](../ANSYS_Document/SIwave/v261/manuals/SIwave%20Getting%20Started%20Guide.pdf#page=27) | 部分整理；有案例設定與阻抗用途 |
| 5 PSI SYZ Analysis | 使用 PSI solver 生成 SYZ parameters、查看 frequency-dependent impedance | [PDF pp.37–42](../ANSYS_Document/SIwave/v261/manuals/SIwave%20Getting%20Started%20Guide.pdf#page=37) | 部分整理；含案例設定與記憶體限制 |
| 6 PSI AC Current Analysis | voltage source、AC surface current、2D plots、total radiated power CSV | [PDF pp.43–52](../ANSYS_Document/SIwave/v261/manuals/SIwave%20Getting%20Started%20Guide.pdf#page=43) | 本輪補充摘要；未視覺核對圖表或執行 |
| 7 Frequency Sweep of Voltages | 停用電壓源、建立 current source 與 voltage probe、frequency sweep、plot probe voltage | [PDF pp.53–61](../ANSYS_Document/SIwave/v261/manuals/SIwave%20Getting%20Started%20Guide.pdf#page=53) | 本輪補充摘要；未視覺核對圖表或執行 |

### Getting Started with SIwave CPA: A Package Model（v261）

| 章節 | 目錄中的主要操作／概念 | PDF 定位 | 字典狀態 |
|---|---|---|---|
| 1 Introduction | CPA solver、package RLGC/SPICE model、應用範圍 | [PDF p.6](../ANSYS_Document/SIwave/v261/manuals/SIwave-CPA%20Getting%20Started%20Guide.pdf#page=6) | 摘要已整理；未評估精度或相容性 |
| 2 Setting Up the Design | ANF project、layers、power/ground nets | [PDF pp.8–15](../ANSYS_Document/SIwave/v261/manuals/SIwave-CPA%20Getting%20Started%20Guide.pdf#page=8) | 部分整理；未逐步核讀全部操作 |
| 3 SIwave-CPA RLGC Extraction | power/ground pin groups、CPA options、啟動 RLCG extraction | [PDF pp.16–27](../ANSYS_Document/SIwave/v261/manuals/SIwave-CPA%20Getting%20Started%20Guide.pdf#page=16) | 部分整理；含教學案例與設定限制，未執行求解 |
| 4 Viewing CPA RLGC Results | tabular／SPICE files、graphical results | [PDF pp.28–31](../ANSYS_Document/SIwave/v261/manuals/SIwave-CPA%20Getting%20Started%20Guide.pdf#page=28) | 部分整理；摘要輸出類型，未檢查實際結果檔 |

### SIwave Scripting Guide（v261）

| 章節／命令族 | 目錄涵蓋內容 | PDF 定位 | 字典狀態 |
|---|---|---|---|
| 1 Introduction to Scripting | 執行入口、IronPython shell、相容性、縮排、尋找方法與 help | [PDF pp.19–22](../ANSYS_Document/SIwave/v261/manuals/SIwaveScriptingGuide.pdf#page=19) | 已整理此限定範圍；沒有執行腳本 |
| 2 project／general methods | project open/save/close、project metadata、版本及 solution data | [PDF pp.34–42](../ANSYS_Document/SIwave/v261/manuals/SIwaveScriptingGuide.pdf#page=34) | 目錄可定位；未逐項整理 |
| 2 layout／nets／pin groups／circuit elements | 建立／修改 geometry、layers、materials、nets、pin groups、ports、sources、probes | [PDF pp.42–94](../ANSYS_Document/SIwave/v261/manuals/SIwaveScriptingGuide.pdf#page=42) | 少數方法已核（如 `ScrCreatePinGroups` PDF pp.67–68）；大部分未整理 |
| 2 exports／reports | 3D/AEDT/ANF、Touchstone、simulation reports、資料匯出 | [PDF pp.94–120](../ANSYS_Document/SIwave/v261/manuals/SIwaveScriptingGuide.pdf#page=94) | 少數方法已核（如 Touchstone）；大部分未整理 |
| 2 query／get methods | 讀取 component、layer、net、pin、simulation 等資訊 | [PDF pp.120–139](../ANSYS_Document/SIwave/v261/manuals/SIwaveScriptingGuide.pdf#page=120) | 目錄可定位；未逐項整理 |
| 2 import／file methods | ANF、EDB、GDSII、IPC2581、stackup、settings 等匯入 | [PDF pp.139–152](../ANSYS_Document/SIwave/v261/manuals/SIwaveScriptingGuide.pdf#page=139) | 少數方法已核（如 `ScrImportAnf` PDF p.139）；大部分未整理 |
| 2 net／placement／selection methods | nets 關係、元件放置、port placement、selection | [PDF pp.152–164](../ANSYS_Document/SIwave/v261/manuals/SIwaveScriptingGuide.pdf#page=152) | 目錄可定位；未逐項整理 |
| 2 simulation／validation methods | DC、resonant、frequency sweep、SYZ、validation 與 result controls | [PDF pp.164–177](../ANSYS_Document/SIwave/v261/manuals/SIwaveScriptingGuide.pdf#page=164) | 少數方法已核（如 `ScrRunDcSimulation`、`ScrRunValidationCheck`）；其餘未整理 |
| 2 solver／mesh／analysis options | bondwire、DC mesh/refinement、PSI、FWS、near-field、thermal 等設定 | [PDF pp.177–225](../ANSYS_Document/SIwave/v261/manuals/SIwaveScriptingGuide.pdf#page=177) | 目錄可定位；未逐項整理 |
| 2 frequency／Touchstone／remaining options | sweep、interpolation、Touchstone、Z0／crosstalk 等設定 | [PDF pp.225–256](../ANSYS_Document/SIwave/v261/manuals/SIwaveScriptingGuide.pdf#page=225) | `ScrSetSweepFreqRange` 有未解文字量級矛盾；其餘未逐項整理 |

命令族只按 PDF 目錄所列名稱和用途作導覽，不能替代每個方法的簽章、參數、回傳值、前置條件與錯誤處理。Scripting Guide 目錄頁是 PDF pp.3–16，API 正文逐條定義從 PDF p.34 起；PDF pp.257–269 的索引／文件尾頁未納入內容整理。三份手冊都尚未逐頁做視覺、表格及掃描品質檢查。


## 2026-11-04：Wave 4 本機來源盤點與限制說明

本批完成 siwave 模組既有本機 catalog 文件（共 3 筆）與 sources 清冊（共 3 筆）之完整雜湊、正文路徑與標籤結構核對。本機未快取或具備企業授權/登入限制之線上主題誠實標記為缺口（保持現有非 complete 狀態），未擅自虛構未核實之線上 API 簽名或執行求解運算。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/siwave_module_conversion_report_20261104.md)。
