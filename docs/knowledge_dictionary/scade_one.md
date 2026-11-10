# SCADE One / PyScadeOne 知識字典

> 本字典包含兩條來源線：Scade One 產品文件（標準函式庫 2025 R1、2025 R2、2026 R1；Swan Primer 2025.1）及 PyScadeOne SDK（本機鏡像 0.8）。SDK 版號不代表產品版號；標準函式庫和 SDK 的版本不可互相推定。

## 產品與 Swan 語言

官方開發者入口將 Scade One 定位為模型式嵌入式應用軟體開發環境。其開發資源包含 PyScadeOne Python library、Swan 語言及標準函式庫；官方入口稱 Scade One libraries 支援 Windows、Linux，並提供 Python 與 Swan 資源。Swan 是同步資料流領域語言，可用圖形或文字記法混合描述控制與狀態機模型。

《The Swan Language Primer》封面標示版本 `2025.1`、文件版 `2.6`、日期 `2025-11-24`。目錄顯示它涵蓋 Swan 語法、宣告、使用者定義 operators、expressions、modules/namespaces，以及 temporal/spatial window、array flatten、tagged unions、匿名 operators、partial application 等擴充。這裡只作內容導覽；語法細節須回到 PDF 指定頁核對，不能只依目錄推導語意。

來源：[官方產品入口](../ANSYS_Document/Scade_One/unknown/guides_and_tutorials/OVERVIEW.md)（source `ansys_1d21da7baaf87cfe3946c7e2`；release unknown）及 [Swan Language Primer](../ANSYS_Document/Scade_One/unknown/archives/SwanPrimer_Rev_2.6.pdf)（source `ansys_13fdac0dd128b56cb64b9f54`，PDF p.1–3；版本標記如上）。

## 標準函式庫導覽與版本

標準函式庫目錄明確用於模型設計、模擬及 debug。2026 R1（目錄標記 `v261`，頁面更新日 2026-03-09）列出下列群組：

| 函式庫 | 文件用途摘要 | 適合查詢的主題 |
|---|---|---|
| `Bitfield` | 位元陣列或視為位元陣列的整數操作、Boolean 陣列轉換、bit-field 與 byte 組裝／拆解 | 位元操作、byte 轉換 |
| `Check` | 建立 test harness oracle 的檢查 operators | harness 輸出檢查 |
| `Digital` | 數位資料處理的基本函式 | 數位訊號處理 |
| `Float` | 浮點數使用規範相關 operators | 浮點運算 |
| `Flows` | flow 操作，例如 delay、counter、timer | 時序、計數、延遲 |
| `Math::Common`, `Math::Complex`, `Math::Trigo` | 基本數學、複數型別與操作、三角及反三角函式 | 數學函式 |
| `Matrix`, `Vector` | 矩陣與向量常用操作 | 線性代數 |
| `Sources` | 主要供 test harness 使用的 flow generators，多為數值來源 | 測試刺激來源 |

2025 R1 索引（`v251`，2025-07-17）另列 `Math::Matrix`、`Math::Vector` 名稱；2025 R2（`v252`，2025-07-16）與 2026 R1 索引使用 `Matrix`、`Vector`。這是文件索引呈現的命名差異，不足以證明 operator API 或行為變更。2026 R1 changelog 說明該版「No changes in this release」；此句僅限該標準函式庫版本公告，不表示跨年版零差異。

以上是索引層級的範圍摘要，不代替每個 operator 的型別、參數、clock/size 約束及範例。具體操作應再開對應 operator 條目，並依目標 Scade One library release 核實。

來源： [2025 R1 索引](../ANSYS_Document/Scade_One/v251/guide/001d7496c40d-index.md)（`ansys_afd5fc388056ffe10fd9d490`）、[2025 R2 索引](../ANSYS_Document/Scade_One/v252/guide/607a179d6fb6-index.md)（`ansys_6eeaa3d6d1555727ab2bd206`）、[2026 R1 索引](../ANSYS_Document/Scade_One/v261/guide/9d2dd59e936c-index.md)（`ansys_8edd422f8e2345921a3de939`）及 [2026 R1 changelog](../ANSYS_Document/Scade_One/v261/guides_and_tutorials/scade-one-standard-libraries-2026-r1/changelog.md)（`ansys_5c27e7714ec6bf600e2b3ff4`）。

## Swan 時間視窗 `window` 與延遲值

Primer 2.6 的時間視窗用陣列形式存取 flow 的過去值，文件說明 code generator 可將它實作為 circular buffer。形式 `window<<N>>(I)(e)` 中，`N` 是視窗長度，`I` 是初始陣列，`e` 是被觀察的 flow；`w[0]` 在目前 cycle 取 `pre e`，後續位置依序保存更早的視窗值。視窗不含目前輸入值，因此像滑動加權平均或 FIR 計算若需要 `x` 當前值，必須另外把它納入運算。

Primer 的例子用視窗長度 4 保存輸入 `x` 的過去值，將 `x` 當前值與 `w[0..3]` 加權求和；另一個雙 flow 例子以不同初值建立兩個視窗，並把目前值加總進公式。文件也指出時間視窗可用於 FIR、IIR 濾波器，且可按陣列大小參數化階數。這些是 Primer 的 Swan 語言示例，不代表特定標準函式庫 operator 或特定產品版本的實測效能。

來源：[Swan Language Primer 2.6](../ANSYS_Document/Scade_One/unknown/archives/SwanPrimer_Rev_2.6.pdf) PDF p.31–34（文件版本 2.6、語言版本 2025.1）。轉換文字位於同目錄 `SwanPrimer_Rev_2.6.md` 的 PDF Page 31–34；以上例子保留頁碼，若需依賴型別或完整語法，請回 PDF 核對原始排版。

## Tagged union 的分支與 clock

Primer 以 `tagged union` 表示同一 flow 可攜帶不同變體，例如 `coord2D` 在 `Polar` 與 `Cartesian` 兩種資料結構間選擇。tag 保證不同分支互斥；文件將 variant 的 clock 對應到 tag。`match` 分支可依 variant tag 選擇並擷取對應 payload；`when match` 可在 dataflow 表達式中取出匹配分支的值，不匹配時沒有值。若在模式中捕捉 payload，Primer 指出該變數不可直接作為 `last` 對象；若需保留狀態，需在分支中宣告新變數並提供所需初始化。

此摘要僅整理 Swan Primer 2.6 的 tagged union 概念和限制，不延伸為 SDK Python Variant 或 Simulation data API 的行為說明。

來源：[Swan Language Primer 2.6](../ANSYS_Document/Scade_One/unknown/archives/SwanPrimer_Rev_2.6.pdf) PDF p.38–40；對應轉換文字在 `SwanPrimer_Rev_2.6.md` 的 PDF Page 38–40。轉換中的數學及程式碼符號可能因 PDF 排版抽取而失真，完整語法須檢查原頁。

## PyScadeOne 物件入口

`ScadeOne` 是 PyScadeOne API 的入口，可載入 project 並進一步操作 Swan models。文件範例以 `ScadeOne(install_dir=...)` 建立應用程式，也可用 context manager 管理生命週期。若 project 使用 Scade One standard libraries，需設定 `install_dir`。API 錯誤透過 `ScadeOneException` 回報；錯誤與警告也記錄到執行目錄中的 `pyscadeone.log`。

來源：0.8 [Overview](../ANSYS_Document/Scade_One/sdk/ansys-scadeone-core/0.8/guide/417c875137e8-overview.md)、[User guide](../ANSYS_Document/Scade_One/sdk/ansys-scadeone-core/0.8/guide/ffe870a6b6d1-index.md)。

## Project 與模型操作

PyScadeOne `ScadeOne` app 透過 `load_project(path)` 載入 `.sproj`；官方 Modeler 範例指出路徑可用 `str` 或 `pathlib.Path`。專案存在時回傳 `Project`，不存在時回傳 `None`；可連續載入多個 project，並由 `app.projects` 取得已載入專案。

```python
app = ScadeOne(install_dir=install_dir)
project = app.load_project(project_path)
if project is not None:
    model = project.model
    sources = project.swan_sources(all=True)
    dependencies = project.dependencies(all=True)
```

### 專案來源與依賴

- `project.swan_sources()` 回傳專案內 Swan body（`.swan`）與 interface（`.swani`）檔案；`all=True` 會把依賴專案的來源也納入。
- `project.dependencies()` 只回傳直接依賴；`project.dependencies(all=True)` 遞迴納入全部依賴，同一個 dependency 只出現一次。
- `project.model` 是由專案來源建立的 Swan `Model`，可進一步讀取 modules、declarations、types、constants、sensors 與 operator definitions。由 model 可透過 `model.project.app` 回到對應的 ScadeOne app。

### Swan Model 的載入行為

PyScadeOne 對大型專案採 lazy loading：查詢集合（例如 `model.sensors`）可能要求載入全部來源；`model.find_declaration(predicate)` 則逐步載入／搜尋，找到目標 declaration 後即可停止。Modeler 範例以 `GlobalDeclaration` 作為 filter 輸入，再用型別及名稱條件選取 operator。這是依官方 0.8 文件描述的載入策略，不保證任意自訂 traversal 都只讀取部分來源。

### 儲存的覆寫行為

`Project.save()` 儲存 project modules、dependencies、resources 與 `.sproj` version。API reference 特別區分新建與載入的專案：新專案寫入 `.sproj` 位置；載入既有專案時會儲存並取代舊檔案。呼叫 `save()` 前應確認 project path、來源控制或備份狀態，避免把對模型的修改覆寫回原專案。

來源：[Project management，PyScadeOne SDK 0.8 本機 API reference](../ANSYS_Document/Scade_One/sdk/ansys-scadeone-core/0.8/api_reference/aea323127150-project.md)（[來源清冊](sources.csv#ansys_6575eb7b99f5b58ed91178f1)，網址使用 `version/stable`）；[Modeler guide](../ANSYS_Document/Scade_One/sdk/ansys-scadeone-core/0.8/guide/ae64c1b1d1e4-modeler.md)（[來源清冊](sources.csv#ansys_0183a36731dc11c18ee8c623)，網址使用 `version/stable`）。版本依本機鏡像目錄限定為 SDK 0.8；stable URL 不代表遠端頁面精確版號。未開啟 Scade One、未載入或儲存專案，也未執行 code generation。

## CLI 工作

### PyScadeOne CLI 版本、格式與子命令 help（SDK 0.8）

PyScadeOne CLI 文件說明，`pyscadeone` 隨 Python 安裝在 `Scripts` 目錄；若 shell 找不到命令，先確認該目錄已加入 `PATH`。`pyscadeone --version` 回報 CLI 版本，`--formats` 列出支援格式；重複指定 `-v`／`--verbosity` 會提高輸出詳細程度。需要查特定 `fmu`、`pycodewrap` 或 `simdata` 參數時，使用 `pyscadeone <command> --help`，並以實際安裝版本的 help 為準。

來源頁只描述命令入口與通用 switches，沒有列出各子命令完整參數，也沒有定義 verbosity 層級對應的 log 細節。此摘要限 PyScadeOne SDK 0.8 本機文件；catalog release 與產品 release 均 unknown。未在本機執行 CLI。

來源：[Command line interface](../ANSYS_Document/Scade_One/sdk/ansys-scadeone-core/0.8/guide/09b49d5a1e68-cli.md) · `ansys_9a0070fd22b79d547103ec1a`。

| 子命令 | 文件描述的用途 |
|---|---|
| `pyscadeone fmu` | 產生 FMU package |
| `pyscadeone pycodewrap` | 產生 Scade One Python wrapper |
| `pyscadeone simdata --show` | 顯示 simulation data 檔案資訊 |
| `--help`, `--version`, `--formats`, `--verbosity` | 查詢用法、版本、支援格式及輸出詳細程度 |

`pyscadeone` 命令位於 Python installation 的 `Scripts` 目錄，需確保該目錄在 PATH。先執行各子命令的 `--help` 確認該安裝版本接受的參數。

來源：0.8 [Command line interface](../ANSYS_Document/Scade_One/sdk/ansys-scadeone-core/0.8/guide/09b49d5a1e68-cli.md)。

## Simulation data 檔案生命週期與值語意

Simulation data（`.SD`）用序列資料表示模擬值：可在 test harness 的 data source block 作為輸入刺激，也可在 oracle block 保存預期輸出供 model test 比較。文件提供三種檔案入口：`open_file(path)` 以唯讀方式開啟；`create_file(path)` 建立新檔；`edit_file(path)` 以編輯模式開啟既有檔案。完成後以 `close()` 關閉檔案。

| 資料 | 官方頁所述行為 | 使用邊界 |
|---|---|---|
| `none` | Stimuli operator 的第一個 cycle 必須有值；後續 cycle 的 `none` 表示沿用前值。Simulator trace 的 `none` 表示該變數 clock 為 false。 | 兩種用途的 `none` 語意不同，不要混為缺失數值。 |
| 複合型別 | 支援 Swan types、Variants、Groups；imported types 以 byte array 儲存。支援結構、固定大小 table、enum、string。 | 不支援 partial data；複合型別需要提供所有欄位值。 |
| 值序列 | `append_value()` 加入單值；`append_values_sequence()` 加入一段值序列，scalar values 可指定 repeat factor。 | repeat factor 不可用於 arrays／structures；有值的 array／structure 應使用 `append_value()`，依 API 頁限制操作。 |
| 儲存與讀取 | 頁面描述資料按需讀取、不必把整個檔案載入記憶體，並以增量讀寫避免關閉時重寫全部內容。 | 這是文件描述的設計特性，未作大檔效能測量。 |

官方 CLI 範例以 `pyscadeone simdata --show some_file.sd > some_file.txt` 將 `.SD` 內容輸出成文字檢視，不需開啟 Scade One 或 Signal Editor。此摘要限 PyScadeOne Simulation data API 頁已載明的 `.SD` 操作與資料語意；網址採 `version/stable`，本機鏡像目錄為 SDK `0.8`，catalog 的精確 release 仍為 unknown。未建立、編輯或預覽 `.SD` 檔案。

來源：[Simulation data API](../ANSYS_Document/Scade_One/sdk/ansys-scadeone-core/0.8/api_reference/08693205ceda-simdata.md)（[來源清冊](sources.csv#ansys_1959c787760341716316d2d0)）。

## FMU 匯出流程（FMI 2.0 tutorial）

PyScadeOne 0.8 官方範例以 QuadFlightControl 說明 FMI 2.0 FMU packaging，必要順序如下：

1. 在 Scade One IDE 執行 project 的 `CodeGen` job，產生 Swan model 的 C code；FMU 範例不會替代這個 code generation job。
2. Python 建立 `ScadeOne(install_dir=...)`、載入 project，再建立 `FMU_2_Export(project, "CodeGen")`。
3. 先檢查 `fmu.codegen.is_code_generated`；官方範例若為 false 會停止流程，避免嘗試用未產生的 code 建包。
4. 呼叫 `generate(kind, output_dir)` 產生 FMI 2.0 檔案，再呼叫 `build(...)` 封裝。範例以 `kind="ME"` 建 Model Exchange FMU；`kind="CS"` 則建 Co-Simulation FMU。這只說明 tutorial 支援的兩種 FMI 2.0 kind，不代表所有 project 都可直接匯出。

建置時的工具與 include 邊界：

- 範例預設使用 Scade One 提供的 GCC；若 PATH 中已有 compiler，或需指定其他位置，可依官方說明使用 `gcc_path` build argument。
- QuadFlightControl 範例使用 Math library operator，需把 `math_stdc.h` 的 `#include` 放入 `swan_config.h`；tutorial 透過 `swan_config_end` build argument 加入。這是該範例的 library dependency，其他 project 不應照搬此檔案路徑。
- 同頁提供 `pyscadeone fmu` CLI 入口，參數包含 project path、`CodeGen` job、`--install_dir`、`--outdir`、`--with_sources` 與 `--build_arguments`；依安裝版本先查 CLI `--help`。

此摘要限 PyScadeOne 0.8 的 FMI 2.0 tutorial；官方網址使用 `version/stable`，產品 release 仍 unknown。未產生 FMU、未執行 codegen 或 compiler，也未驗證匯出產物可在特定 FMU importer 執行。

來源：0.8 [Export FMU tutorial](../ANSYS_Document/Scade_One/sdk/ansys-scadeone-core/0.8/tutorial/364fda37cd37-index.md)（來源 ID `ansys_774fc39a3d60234a0c3c9a38`；官方頁含 [FMU export API](https://scadeone.docs.pyansys.com/version/stable/api/svc/fmu_export.html) 與 CLI 參考連結）。

## 範圍與限制

本頁涵蓋產品定位、Swan Primer 目錄導覽、標準函式庫群組及 PyScadeOne SDK entry point、project、CLI 與 FMU 範例。Swan 語法、標準函式庫逐項 operator 規格及 code generation job 設定尚未完整整理。SDK 文件網址使用 `version/stable`；引用 SDK 摘要時以本機 `0.8` 路徑為準。

本機來源與轉換狀態逐筆清冊：[SCADE One 來源檢查 CSV](../maintenance/knowledge_dictionary_passes/2026-11-02/scade_one_sources_review.csv)。該清冊核對檔案存在、轉換 sidecar 非空與 SHA-256；它不代表線上頁重新擷取成功，也不代表逐頁圖片、表格或掃描品質均已人工驗收。



## 2026-11-04：Wave 3 本機來源盤點與限制說明

本批完成 scade_one 模組既有本機 catalog 文件（共 375 筆）與 sources 清冊（共 13 筆）之完整雜湊、正文路徑與標籤結構核對。本機未快取或具備企業授權/登入限制之線上主題誠實標記為缺口（保持現有非 complete 狀態），未擅自虛構未核實之線上 API 簽名或執行求解運算。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/scade_one_module_conversion_report_20261104.md)。
