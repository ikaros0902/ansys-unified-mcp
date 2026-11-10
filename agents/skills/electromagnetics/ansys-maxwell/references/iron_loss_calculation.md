# 鐵損 (Core Loss) 模組計算模型

> [!NOTE]
> 本手冊依據官方知識字典 `maxwell.md` 與 `pyaedt` 權威技術規格擴充，提供深度工程指導。

## 1. 原理與設定準則

本模組於高精度數值模擬時，必須遵循以下邊界設定與收斂規範：
- 數值精度與單位一致性：務必先確認全域坐標系統、材料參數庫與求解單位（MKS/SI）。
- 網格劃分策略：實施局部特徵網格加密，並於梯度變化劇烈區域進行自適應細化。
- 監控物理量：除了求解器預設殘差之外，必須定義面通量、力矩或特徵頻率等客觀物理監控器。

## 2. 核心規範與字典精要

# Ansys Maxwell 知識字典

> 唯一來源為 `Maxwell Scripting Guide`，封面標示 Ansys Electromagnetics Suite 2026 R1、January 2026；目前沒有其他版本可供差異比較。

## 腳本工作環境

本字典依《Maxwell Scripting Guide》2026 R1（來源清冊版本 `v261`）整理。手冊描述三種常見入口，彼此的 Python runtime、連線方式及功能範圍不同：

| 入口 | Runtime／連線 | 適用方式與限制 |
| --- | --- | --- |
| Desktop 內建 IronPython | 手冊列為 IronPython 2.7、.NET Framework 4.0 | 可由 Tools > Open Command Window、Run Script、啟動參數或 External Tools 執行；可使用 .NET。使用 C 擴充的 NumPy、SciPy 等套件預期不能直接在該 runtime 執行。 |
| Standalone IronPython | 安裝目錄內的 `common/IronPython/ipy64.exe`，以 COM 取得 AnsysEDT app | 手冊說明只完整支援 COM functions，並非 Desktop 內所有腳本功能的等價替代。執行前須按手冊設定安裝路徑；結束方式亦須按 standalone 範例處理。 |
| CPython external script | CPython 與 AEDT 透過 gRPC 溝通；AEDT 作 server，CPython script engine 作 client | 腳本需把安裝目錄 `PythonFiles/DesktopPlugin` 加入 `sys.path`，匯入 `ScriptEnv`，再選擇 `InitializeNew()` 或 `Initialize()`。`InitializeNew()` 一律啟動新 instance；`Initialize()` 連線到指定 instance，若指定 port 沒有 instance，手冊稱會在該 port 啟動新 instance。結束時呼叫 `ScriptEnv.Shutdown()`；多個 script 共用時只在最後一個 script 呼叫。 |
| PyAEDT | CPython library 與 AEDT API 互動 | 本手冊將其標為 Beta，並列出 Maxwell 3D、HFSS、Icepak、Q3D、Circuit Nexxim、Twin Builder、Layout 等支援範圍與 Automation 工具入口。此標示僅代表本手冊版本內容；PyAEDT 安裝方式和目前支援狀態應查其對應版本文件。 |

CPython gRPC server 的手冊預設起始 port 為 `50051`；`-grpcsrv` 可指定 port 或 port range，若 port 已被占用則啟動可能失敗。`-ng` 可與 `-grpcsrv` 合用。`InitializeNew(NonGraphical=..., Module=None, Machine="", Port=...)` 會在本機啟動新 instance；手冊稱 `Port=0` 時從 50051 起找第一個可用 port。`Initialize(name, NG=..., machine="", port=...)` 的 `name` 被忽略；非零 port 先嘗試連線，無既有 instance 時再啟動。遠端 `Connect(machine, projectPath)` 要求 project path 為 network path。這些行為均依 2026 R1 手冊描述，部署或版本差異須回查相同版本的 `ScriptEnv.py` 與 API 文件。

來源： **Maxwell Scripting Guide PDF**（IronPython；PDF Pages 50–55）、**PDF Page 93–96**（CPython／gRPC；連線與啟動參數）、**PDF Page 107**（PyAEDT）。手冊封面標示 Ansys Electromagnetics Suite 2026 R1。

限制：未啟動 AEDT、未執行 IronPython／CPython 範例，也未在本機比對 `ScriptEnv.py`；連線與 port 行為是手冊記載，非本機實測。

## Object-oriented scripting：瀏覽物件與讀寫屬性

2026 R1 手冊的 Object-oriented scripting 章節示範以 script object 樹查詢既有 project、design、module、boundary、modeler object 及其屬性。這是一種讀取／修改既有物件的介面；它不負責建立新 object instance，建立工作仍須使用對應 module command。

### 基本查詢流程

先從 Desktop 取得目前 project 與 design，再用 `GetChildTypes()` 確認子物件類型、`GetChildNames()` 查看下一層物件，並以 `GetChildObject(path)` 取得子物件。對已取得的物件，`GetPropNames()` 列出可用屬性、`GetPropValue(name)` 讀取值、`SetPropValue(name, value)` 設定值；手冊範例中 setter 回傳 Boolean，`True` 表示成功。

```python
oProject = oDesktop.GetActiveProject()
oDesign = oProject.GetActiveDesign()
oExcitations = oDesign.GetChildObject("Excitations")
portNames = oExcitations.GetChildNames()
oPort = oExcitations.GetChildObject(portNames[0])
propertyNames = oPort.GetPropNames()
```

`GetChildNames()` 預設會依物件類型決定列出的 children；需要時可指定 type。`GetChildObject()` 支援多層路徑，例如 `"hfss/3d modeler/Box1"`。這些 API 只可瀏覽手冊所暴露的 children 與 properties，並非 Project Manager 中每個節點都保證可由同一方式存取。

### 屬性、變數與資料集語意

- `GetPropValue()` 回傳 property value；對幾何物件，手冊範例可讀取 Material、`xsize` 等屬性。若需要 expression 評估值或 SI 值，手冊另列 `GetPropEvaluatedValue()` 與 `GetPropSIValue()`；例如 `xSize` expression `length / 2`、評估值 `0.4mm`、SI 值 `0.0004` 是該頁範例，不應混為同一表示形式。
- Project variable 位於 Project 的 `Variables` child，名稱以 `$` 開頭；design variable 位於 Design 的 `Variables` child，名稱不加 `$`。讀取時先用 `GetPropNames()` 找到該層名稱，再用 `GetPropValue()` 取值。
- Desktop 的 dataset wrapper 以 SI units 保存內部值；`GetPropSIValue()` 回傳 SI 數值，`GetPropValue("[:,:]")` 依 `DimUnits` 回傳使用者單位。手冊範例設定 `DimUnits = ['mm','mm']` 後，同一資料以使用者單位及 SI units 讀回的數值不同，讀取數據時需先確認採用的單位介面。

### AEDT solver 範圍與存取限制

手冊列出的 design children 會依 solver 不同而變化：例如 Maxwell 2D／3D 有 Boundaries、Excitations、Analysis、Field Overlays、Optimetrics、Results；Q3D 則列 Boundaries、Nets、Analysis、Optimetrics。Module object 本身可能沒有 properties，其 children 才是可查詢的 script objects。HFSS 端口、Q3D net source／sink 也可能繼續包含子物件。

手冊另指出 3D Component encapsulation 會限制可見範圍：一般 design 的 Boundaries children 不會列出 component boundaries；component excitation 的 setter 僅支援修改部分 post-processing 屬性，例如 HFSS port 的 Deembed。此限制避免將一般 project-tree 查詢結果誤認為元件封裝內的完整資料。

來源：**Maxwell Scripting Guide PDF**（PDF Pages 109–116：基本物件樹與既有物件限制）、**PDF Pages 116–118**（變數與 dataset 單位）、**PDF Pages 120–125**（屬性 API、AEDT solver children、boundary／excitation 與 encapsulation）。

限制：內容限定 v261／2026 R1 手冊的 object-oriented scripting 章節，未逐一列出所有 solver modules／COM methods；未啟動 AEDT 或執行範例。`SetPropValue()` 有修改 project/design 狀態的能力，套用前應確認目標 object 與 property。

## `AnalyzeAll`：執行範圍與時序

手冊列出兩個不同物件層級的 `AnalyzeAll`，呼叫範圍不可混用：

| 命令 | 範圍 | 返回／時序 |
|---|---|---|
| `oProject.AnalyzeAll()` | Project 內所有 design instances 的 solution setups 與 Optimetrics setups。 | 無參數、無返回值；UI 等 simulation 完成後才繼續 script。 |
| `oDesign.AnalyzeAll(isBlocking)` | 選定 design 下所有 setups 的 nominal problems 與 Optimetrics problems。 | `isBlocking` 預設 `True`；設 `False` 會先返回、讓 analysis 在背景執行，可用 `AreThereSimulationsRunning` 查狀態；命令返回本身不代表求解完成。 |

來源：**Maxwell Scripting Guide PDF**（Project 層 `AnalyzeAll`，PDF Page 136；命令細節亦見 PDF Page 262）、**PDF Pages 592–593**（Design 層 `AnalyzeAll` 的範圍與 `isBlocking` 參數）。

限制：以上只區分 Project／Design 層命令的文件定義與返回時序，不代表求解成功或收斂；未啟動 AEDT，也未執行 Maxwell 求解。

## 讀取解算資料與 sweep 單位

讀取已完成模擬的結果，可從 Design 的 `ReportSetup` module 呼叫 `GetSolutionDataPerVariation(reportTypeArg, solutionNameArg, simValueCtxtArg, familiesArg, expressionArg)`。手冊要求先有已執行的 simulation；返回值是 `ISolutionDataResultComInterface` 物件陣列，包含 sweep names／units／values、real／imaginary data 等讀取方法。此命令不能由 UI 錄製；手冊建議錄製參數相近的 `CreateReport` script 來參考輸入參數。

對返回物件的 `GetSweepValues(sweepName, SIValue)`，手冊稱 `SIValue` 預設 `True`，`True` 返回 SI values、`False` 返回目前 sweep units。需保留該語意說明，但原 PDF physical Page 946 的數值例子自相矛盾：它寫 sweep 是 `[1GHz, 2GHz, 3GHz]`、單位為 `GHz`，同時把 `SIValue=True` 的結果列為 `[1000000, 2000000, 3000000]`。這些數值不符合通常的 GHz→Hz 換算；字典不採用該數例作為換算依據，實際 API 數值單位仍須在目標版本確認。

來源：**Maxwell Scripting Guide PDF**（PDF Pages 118–119：solution data API 概述）、**PDF Pages 945–949**（command reference、參數、返回物件與 sweep 單位；來源清冊：`ansys_e3c61f8717103dd92e9e7337`）。

限制：內容限 `GetSolutionDataPerVariation` 與 sweep-value API 的文件定義，不含 solver setup、收斂判斷或完整參數表。手冊所列 GHz／SI 數值互相矛盾，不能據該例推導正確換算值；未執行 AEDT 或 Maxwell 求解。

## 限制

未找到第二版 Maxwell scripting guide 或官方 API HTML 來源，因此尚不能確認舊版差異。本文沒有逐條搬錄 command table；PDF 的目錄／命令表與範例未逐頁目視校對，也未啟動 Maxwell/AEDT。


## 手冊章節索引與審閱範圍

下表連至逐章清冊；28 章與 1,289 個目錄項目依轉換稿 PDF Pages 3–46 統計。目錄只用於導航，不能證明各命令正文已完成整理。現有字典只核對了若干選定章節頁面，其餘章節皆保留待核。

| 章節 | 目錄頁（PDF） | 命令／條目數 | 狀態 | 已核頁面（PDF） |
|---:|---:|---:|---|---|
| 1 | 3 | 91 | 指定頁面已核讀 | 50–56, 93–107 |
| 2 | 6 | 50 | 指定頁面已核讀 | 109–125 |
| 3 | 7 | 2 | 待逐項核讀 | — |
| 4 | 7 | 93 | 待逐項核讀 | — |
| 5 | 11 | 3 | 待逐項核讀 | — |
| 6 | 11 | 59 | 指定頁面已核讀 | 136, 262 |
| 7 | 13 | 168 | 待逐項核讀 | — |
| 8 | 18 | 21 | 待逐項核讀 | — |
| 9 | 19 | 52 | 指定頁面已核讀 | 592–593 |
| 10 | 21 | 147 | 待逐項核讀 | — |
| 11 | 26 | 5 | 待逐項核讀 | — |
| 12 | 26 | 70 | 指定頁面已核讀 | 945–949 |
| 13 | 28 | 99 | 待逐項核讀 | — |
| 14 | 32 | 35 | 待逐項核讀 | — |
| 15 | 33 | 22 | 待逐項核讀 | — |
| 16 | 34 | 31 | 待逐項核讀 | — |
| 17 | 35 | 29 | 待逐項核讀 | — |
| 18 | 36 | 73 | 待逐項核讀 | — |
| 19 | 38 | 9 | 指定頁面已核讀 | 1287–1298 |
| 20 | 39 | 20 | 待逐項核讀 | — |
| 21 | 39 | 14 | 待逐項核讀 | — |
| 22 | 40 | 3 | 待逐項核讀 | — |
| 23 | 40 | 39 | 待逐項核讀 | — |
| 24 | 41 | 9 | 待逐項核讀 | — |
| 25 | 42 | 87 | 待逐項核讀 | — |
| 26 | 44 | 47 | 待逐項核讀 | — |
| 27 | 46 | 6 | 待逐項核讀 | — |
| 28 | 46 | 5 | 待逐項核讀 | — |

完整命令名稱見 `../maintenance/knowledge_dictionary_passes/2026-11-02/maxwell_chapter_coverage_20261103.csv`。標示已核讀的章節僅指上表列出的頁碼，不代表整章完成。


## Motion setup：AssignBand 與 band 動態

Maxwell 2026 R1／v261 手冊第 19 章將 motion setup 指令放在 design 的 `ModelSetup` module。以下摘要核對 PDF Pages 1287–1298：

- `AssignBand(<BandDataArray>)` 將單一幾何物件指派為運動 band；只適用 Maxwell 2D／3D transient design。`Move Type` 為 `Rotate` 或 `Translate`；另指定座標系、X/Y/Z 軸、方向與含單位字串的初始位置。平移可設週期旗標與位置界限；旋轉可設旋轉界限及非圓柱固定點模式。
- 一般恆定速度案例用 `Velocity` 或 `Angular Velocity`；設定 `Consider Mechanical Transient=True` 時，solver 依計算力／扭矩及指定質量／慣量、阻尼、負載動態決定運動，恆定速度欄位會被忽略。位移與速度參數需含單位。手冊範例中的 `1kg`、`1`、`1nNewton` 等是命令格式示例，不是預設建議值。
- `AssignBand` 的 `Objects` 只能有一個項目；若使用 named selection，該 selection 必須只有一個物件。`Edit(<MotionSetupName>, <BandDataArray>)` 更新設定；手冊標註舊版 `EditMotionSetup` 已由 `Edit` 取代。`GetMotions()` 回傳 active design 的 motion setup 名稱，適用 2D／3D transient。
- `Delete(<MotionSetupNames>)` 可刪一個或多個 motion setup；全刪使用 `DeleteAllMotions()`。`Reassign` 用於更新移動物件幾何指派；`GetBandAssignment`、`GetMovingAssignment` 可查詢目前關聯。手冊指出 `Reassign` 取代舊 `ReassignMoving`。
- `GetSymmetryMultiplier()` 讀取 2D／3D transient 的對稱倍率；`SetSymmetryMultiplier(int)` 設定倍率。手冊說明此倍率會套用於列舉的輸入量（如電壓、電感、電阻、負載扭矩）和輸出量（如感應電壓、磁鏈、損耗、扭矩與力），不可在擷取結果時忽略。

來源：**Maxwell Scripting Guide PDF Pages 1287–1298**（章節第 19 章；命令摘要與範例）。此為文件文字摘要，未比對截斷表格欄位、未執行 Maxwell 2D/3D、未驗證求解行為；不得把範例數值當成工程設定。


## 2026-11-04：Wave 7 本機來源盤點與限制說明

本機來源為一份 v261 Maxwell Scripting Guide。PDF 原件與 canonical Markdown 的雜湊符合稽核，鄰接 Markdown 與 canonical 位元組相同，兩套文字稿各有 1,571 個連續頁標。抽取稿 445 頁含共 789 個 U+0002 控制字元，頁內讀序、圖表及完整命令語意仍待核對。本批未擷取清冊中的 3 個外部網址。

詳細稽核數據見 **本批轉換報告**。

## 3. 常見陷阱與防呆措施

1. **未定義求解範圍**：求解前未限定掃頻範圍或時間步長，導致求解發散。
2. **材料模型失配**：非線性材料未設定適當的切線模數或溫度相依曲線。
3. **介面通訊失敗**：多物理場耦合未對齊變數傳遞單位，導致數值非物理震盪。
