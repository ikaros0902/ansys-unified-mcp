# Ansys Lumerical 主題字典

本頁整理目前可回查的官方文件內容，範圍涵蓋產品層級、Lumerical Scripting Language（LSL）、Python Lumapi／Lumopt 與 MATLAB 互通。產品版本在本機文件中標為 `unknown`；外連官方文章另依其頁面明列版本註記。這份字典不等於完整求解器手冊或執行驗證。

## 主題導覽

| 主題 | 範圍 | 主要來源 |
|---|---|---|
| 產品與自動化入口 | component/system、求解產品、Python API 範圍 | [Developer Overview](../ANSYS_Document/Lumerical/unknown/guide/09b94fbcc7fe-lumerical.md)、[Module Overview](../ANSYS_Document/Lumerical/unknown/guides_and_tutorials/OVERVIEW.md) |
| LSL | 腳本用途、執行入口、命令類別及資料交換 | [LSL Overview](../ANSYS_Document/Lumerical/unknown/guides_and_tutorials/lumerical/scripting-language.md) |
| Python Lumapi | 本機 session、產品 class、Linux Interop Server 邊界 | [Python API Overview](../ANSYS_Document/Lumerical/unknown/guides_and_tutorials/lumerical/python-lumapi.md)；外連 [Session Management](https://optics.ansys.com/hc/en-us/articles/360041873053-Session-Management-Python-API)、[Interop Server](https://optics.ansys.com/hc/en-us/articles/15499581457811-Interop-Server-Remote-API) |
| Lumopt | 逆向設計、FOM、shape/topology 與文件版本差異 | [Lumopt Overview](../ANSYS_Document/Lumerical/unknown/guides_and_tutorials/lumerical/python-lumopt.md)；外連 [Getting Started](https://optics.ansys.com/hc/en-us/articles/360050995394-Getting-Started-with-lumopt-Python-API)、[Optimizable Geometry](https://optics.ansys.com/hc/en-us/articles/360052044913) |
| MATLAB | Lumerical 內呼 MATLAB、MAT 檔與 MATLAB API 入口 | [MATLAB Overview](../ANSYS_Document/Lumerical/unknown/guides_and_tutorials/lumerical/matlab.md)；外連 [Configuration Guide](https://optics.ansys.com/hc/en-us/articles/360026142074-MATLAB-script-integration-configuration-guide) |

## 1. 產品層級與自動化

官方 developer overview 將 Lumerical 套件分為 component 與 system 兩層：前者在物理層建模光學、電氣、熱及量子效應；後者用於光子積體電路（PIC）及其與 EDA 模擬器的整合，並可建立供 foundry PDK 使用的 compact model library（CML）。Overview 列舉的應用包括 nanophotonics、metalens、uLED 與 CMOS image sensor。這是概覽層級描述，不能據此推斷每個產品或版本支援所有列舉物理功能。

Developer overview 將自動化入口列為 Script File Editor、外部 IDE 中的 LSL／Python／MATLAB，以及 Python API 和 MATLAB interop。Python API 官方總覽將 API 分為 Lumapi 自動化、Lumopt 逆向設計與 Slurm 排程整合，並列出 FDTD、MODE、Multiphysics（`DEVICE` class）和 INTERCONNECT 的自動化入口。產品 class 與功能細節以安裝版 API reference 為準；本機鏡像沒有各求解器完整手冊。

**來源定位：**兩份本機 overview（版本 unknown）；官方 [Python API overview](https://optics.ansys.com/hc/en-us/articles/360037824513-Python-API-overview)（線上核讀，頁面未標產品版本）。

## 2. Lumerical Scripting Language（LSL）

LSL 用於自動操作模擬物件、啟動模擬、分析及視覺化結果。官方 overview 說明腳本可輸入 script prompt、由 `.lsf` 檔執行，或用於部分 simulation objects；語法以 MATLAB 為基礎但存在差異。官方命令分類頁另提醒，命令不一定適用所有產品，須查看各命令的產品支援欄。

常見命令類別可按任務理解：物件建立與選取、屬性設定、模擬控制、結果分析、檔案輸入輸出及 interoperability。Python Lumapi 可將 LSL 命令作為 session method 呼叫；應核對 API 文件以確認具體 method、參數和回傳資料。LSL 有 MAT、CSV、STL、STEP、HDF5 等資料交換入口的概覽，但各命令的資料型態與版本適用範圍不在本機短篇正文中，故不在此給出未驗證的格式契約。

**來源定位：**本機 [Scripting Language Overview](../ANSYS_Document/Lumerical/unknown/guides_and_tutorials/lumerical/scripting-language.md)；外連官方 [命令分類](https://optics.ansys.com/hc/en-us/articles/360037228834-Lumerical-scripting-language-By-category) 與 [命令字母表](https://optics.ansys.com/hc/en-us/articles/360034923553)。命令分類頁含完整命令目錄，本文只取概念與執行入口。

## 3. Python Lumapi 與 session

Lumapi 是 Lumerical Python API。Session Management 官方頁列出的建構子包括 `lumapi.FDTD()`、`lumapi.MODE()`、`lumapi.DEVICE()` 與 `lumapi.INTERCONNECT()`；同產品可建立多個 session。外部 Python 環境的安裝與模組路徑依 Lumerical 安裝版本而異，不應把某一安裝目錄寫成通用路徑。

官方 Session Management 說明，自 2023 R1.2 起可連到 Linux 上的 Interop Server；建立遠端 session 時以 `remoteArgs` 傳入 `hostname` 和 server 設定的起始 `port`。官方 Interop Server 頁明列安全版本界線：2025 R2.4 以前連線 client 不做認證，遠端指令具備啟動 server 使用者的權限；2025 R2.4 起以 TLS mutual authentication 和 SSL certificates 提供認證。舊版部署建議限於受限內網，使用受限帳號，避免 root/sudo 權限。這些是官方文章所述版本邊界，部署前仍須核對目標安裝包說明與組織安全政策。

**來源定位：**本機 [Python API overview](../ANSYS_Document/Lumerical/unknown/guides_and_tutorials/lumerical/python-lumapi.md)；官方 [Session Management](https://optics.ansys.com/hc/en-us/articles/360041873053-Session-Management-Python-API) 與 [Interop Server - Remote API](https://optics.ansys.com/hc/en-us/articles/15499581457811-Interop-Server-Remote-API)。第三方 SimuTech 網址僅列於本機 overview 的連結清單，未採作技術依據。

## 4. Lumopt 逆向設計

Lumopt 是隨 Lumerical Python 工作流程提供的 photonic inverse design／optimization 模組。官方入門頁說明可從 CAD Script Editor、command line 或 Python IDE 執行，並建議先以 Application Gallery 範例作為模板；模擬設定有效及 convergence testing 是優化前提。Lumopt 文件主要設定項包括專案輸入與 simulation objects、FOM、幾何、optimizer 和 optimization class。

官方文件區分 shape optimization 與 topology optimization。Shape optimization 以參數化幾何函式及參數界限描述設計；可把製造規則納入參數化。官方幾何頁指出，shape derivative 需要額外的 `d_eps_calculation` mesh 計算；參數增加會增加此步驟成本，2025 R2 起該步驟可按參數空間定位和工作數平行化。這不代表完整優化固定只需兩次 solver run，也不應將單一教學案例的 FOM 或收斂結果視為通用設計保證。

官方 Lumopt 入門頁特別區分隨 Lumerical 產品附帶的版本與早期公開 Lumopt 專案文件：兩者有共通處，但本文與產品教學指 bundled Lumerical version。引用 `lumopt.readthedocs.io` 時需保留此版本／專案差異。

**來源定位：**本機 [Lumopt overview](../ANSYS_Document/Lumerical/unknown/guides_and_tutorials/lumerical/python-lumopt.md)；官方 [Photonic Inverse Design Overview](https://optics.ansys.com/hc/en-us/articles/360049853854)、[Getting Started with lumopt](https://optics.ansys.com/hc/en-us/articles/360050995394-Getting-Started-with-lumopt-Python-API)、[Optimizable Geometry](https://optics.ansys.com/hc/en-us/articles/360052044913)。

## 5. MATLAB 互通

本機官方 overview 列出四類 MATLAB 整合：在 Lumerical script 內呼叫 MATLAB；由 MATLAB Automation API 控制 Lumerical；以 MAT 檔讀寫；將 Lumerical line/surface 圖匯至 MATLAB。它列出 setup guide 及 script integration 外連，但本機沒有鏡像其完整設定步驟。

官方 script integration 設定頁限定此功能支援 64-bit MATLAB，並註明產品版本與 MATLAB／OS 組合不保證全面相容；頁面所述 MATLAB 版本支援區間為 2006b–2022a，近期 MATLAB 版的 script integration 不支援 Linux。以上均是該頁目前列載的設定資訊，不宜延伸成所有 MATLAB Automation API 的支援矩陣。實際部署應依產品版本與 MATLAB 版本重新查該頁及安裝指南。

**來源定位：**本機 [MATLAB overview](../ANSYS_Document/Lumerical/unknown/guides_and_tutorials/lumerical/matlab.md)；官方 [MATLAB script integration](https://optics.ansys.com/hc/en-us/articles/360034923913) 與 [configuration guide](https://optics.ansys.com/hc/en-us/articles/360026142074-MATLAB-script-integration-configuration-guide)。

## 6. Python API：工作階段、命令與模擬物件

Lumapi 以產品 class 建立互動 session：`FDTD`、`MODE`、`DEVICE`（Multiphysics）與 `INTERCONNECT`；同一產品可同時建立多個 session。官方 Session Management 範例支援 Python `with` context manager，結束區塊時關閉 session；發生例外時亦會關閉，錯誤以 Python exception 顯示。一般變數引用離開作用範圍時 session 也會自動關閉，亦可明確呼叫 `close()`。啟動時的 `serverArgs` 用於傳入求解器命令列參數；remote session 用 `remoteArgs` 提供 `hostname` 和 server 起始 `port`，服務端另須依 Interop Server 指南設定。

大多數 LSL script command 可作為 session method 使用；名稱相同。例如 `fdtd.addfdtd()` 建立模擬區域，`fdtd.set("x span", 1e-6)` 設定目前選取物件。建立物件時可用 `properties` dictionary 或 keyword arguments；含空格的 property name 在 keyword form 中以底線替換（`x span` → `x_span`）。參數依賴設定順序時官方建議用 `OrderedDict`，因 keyword assignment 的次序不保證。對需參數的非 constructor 命令應傳 positional arguments，例如 `set("x span", 1e-6)`；文件範例指出 `set(property=..., value=...)` 不適用。命令支援範圍仍須查該命令的產品欄，不可推定所有 LSL command 均可跨產品使用。

Python 和 Lumerical 之間傳遞的是值的副本，不是共享工作空間。官方資料轉換表列 `String → str`、`Real → float`、矩陣／複數 → NumPy array、cell array → `list`、struct/dataset → `dict`；傳入 Python integer 會在 Lumerical workspace 轉成 float。一般 dict 轉成 struct 時不保留順序；Python 複數輸入需包在單元素 NumPy array。其他未列出的 Python 型別不支援。

`getresult()` 回傳的 dataset 在 Python 端以 dict 表示，含 `Lumerical_dataset` metadata key，以保留 dataset 結構供 round-trip；不要在需往返轉換時任意刪除此 key。Parameters 是一維 NumPy array；attributes 的維度取決於 dataset type、attribute type 和 parameter 數目。例如 rectilinear scalar attribute 維度為 `[Nx, Ny, Nz, Np1, …]`，vector attribute 末端另有 3；未使用的空間維度可能以 singleton 維度呈現，可用 `numpy.squeeze` 或 `pinch()` 移除。陣列軸與 singleton 維度應按實際 dataset schema 判讀。

**來源定位：**官方 [Session Management](https://optics.ansys.com/hc/en-us/articles/360041873053-Session-Management-Python-API)、[Script Commands as Methods](https://optics.ansys.com/hc/en-us/articles/360041579954-Script-Commands-as-Methods-Python-API)、[Working with Simulation Objects](https://optics.ansys.com/hc/en-us/articles/39744946400659-Working-with-Simulation-Objects-Python-API)、[Passing Data](https://optics.ansys.com/hc/en-us/articles/360041401434-Passing-Data-Python-API)、[Accessing Simulation Results](https://optics.ansys.com/hc/en-us/articles/39744236202771-Accessing-Simulation-Results-Python-API)。皆為線上核讀摘要，原文未快取、未執行。

## 7. Slurm 排程入口（lumslurm）

官方 Python API overview 將 `lumslurm` 列為第三種 Python 模組，供 HPC workflow 依相依關係提交 simulation 與 post-processing jobs。Lumslurm 入門頁列出的支援條件為 Ansys Lumerical 2023 R2.2 及更新版本，且只支援 Slurm，其他 job scheduler 不支援。文件說明 parametric sweep 搭配 Enterprise license sharing 時，整段 sweep 期間會檢出 Lumerical GUI license。

頁面列出 `fdtd_memory_estimate(filename)` 估算模擬記憶體，回傳 dict 欄位包括 memory（bytes）、gridpoints、time_steps；`partition_info()` 查詢 Slurm partitions。模組提供 mpirun、MPI library、FDTD engine／GUI、`PYTHONPATH` 與 Python executable 的預設設定，也可於安裝程式旁的 `lumslurm.config` 或使用者家目錄的 `.lumslurm.config` 設定 JSON。這是官方頁面列出的功能摘要；未提供通用叢集配置或 license 建議，實際值需按安裝位置與叢集環境設定，本文未連線或提交 job。

**來源定位：**官方 [Python API overview](https://optics.ansys.com/hc/en-us/articles/360037824513-Python-API-overview) 與 [Getting Started with lumslurm](https://optics.ansys.com/hc/en-us/articles/20990924220691-Getting-Started-with-lumslurm-Python-API)。原文未快取、未執行；產品實際最低版本及 license 權益須再核對目標安裝版文件。

## 來源範圍與缺口

- 本機 Lumerical 文件樹有 6 份 Markdown（developer overview、module overview、LSL、Lumapi、Lumopt、MATLAB），均標 release `unknown`；本機 Lumerical 目錄未發現 PDF、HTML 原件或 PDF／HTML 轉換成果。
- 本機正文主要是 overview 與外連導覽，並非完整 API／產品手冊。Ansys Optics 官方外連按上述範圍核讀；並未下載或新增外連正文副本。官方入口亦鏈到 Ansys Help、應用範例、API reference 及設計教學，尚未逐篇擴展。
- 本機 Lumapi/Lumopt/MATLAB 頁列出的 SimuTech、lumopt Read the Docs 等第三方來源未作本字典依據；其使用限制／版本關係需另行審查。
- 未執行 Lumerical、Python API、LSL、MATLAB 或 Lumopt 範例；沒有驗證實際授權、安裝、連線、收斂、效能或不同版本相容性。原始文件和轉換均未修改。

## 建議 RAG 代表查詢

1. `Lumerical component-level 和 system-level 工具分別處理什麼？`
2. `Lumerical Python API overview 列出哪些 API 模組和求解產品？`
3. `LSL 腳本有哪些執行入口？命令是否都適用每個產品？`
4. `Lumapi 的 FDTD、MODE、DEVICE、INTERCONNECT session 怎麼建立？`
5. `Interop Server 支援哪個作業系統？remoteArgs 要帶什麼欄位？`
6. `Interop Server 在 2025 R2.4 前後的認證方式有何差異？`
7. `Bundled Lumopt 和早期 lumopt.readthedocs 文件有什麼版本範圍差別？`
8. `Lumopt 的 shape 和 topology optimization 如何區分？`
9. `MATLAB script integration 對 MATLAB 位元架構、版本和 Linux 有何限制？`
10. `這個 Lumerical 字典中哪些功能沒有本機 PDF/HTML 正文或執行驗證？`


## 2026-11-04：官方 HTML 正文與本機檢索

固定 catalog 的六份 Markdown 原件 hash 與索引 metadata 已核對；本機沒有 PDF、HTML 或附件可重轉。原先十四個官方線上摘要來源已保存公開 HTML 及 Markdown，可由下表回取完整正文。程式區塊逐字保留，表格以 cell matrix 核對；合併儲存格保留原 HTML。外連圖片只保留官方絕對網址，未另行下載；原始六份 Markdown 與既有字典筆記保留。

產品 release 與 SDK version 仍標 unknown；內文列出的版本條件保留在各篇正文，不把單一最低版或安全界線推定為整份文章的版本。這次正文保存不代表實際功能、認證、安全部署、相容性、收斂或範例已執行驗收。

| 官方頁 | 本機全文 | 來源 ID |
| --- | --- | --- |
| [Python API overview](https://optics.ansys.com/hc/en-us/articles/360037824513-Python-API-overview) | [link_032ee02ffe64afa7dbcac9d3](ANSYS_Document/Lumerical/unknown/official_body_20261104/link_032ee02ffe64afa7dbcac9d3.md) | `sources.csv#link_032ee02ffe64afa7dbcac9d3` |
| [MATLAB script integration configuration guide](https://optics.ansys.com/hc/en-us/articles/360026142074-MATLAB-script-integration-configuration-guide) | [link_475dc261440b75b25776c724](ANSYS_Document/Lumerical/unknown/official_body_20261104/link_475dc261440b75b25776c724.md) | `sources.csv#link_475dc261440b75b25776c724` |
| [MATLAB script integration](https://optics.ansys.com/hc/en-us/articles/360034923913-MATLAB-script-integration) | [link_4ff6975cc8be62df303e1d38](ANSYS_Document/Lumerical/unknown/official_body_20261104/link_4ff6975cc8be62df303e1d38.md) | `sources.csv#link_4ff6975cc8be62df303e1d38` |
| [Interop Server - Remote API](https://optics.ansys.com/hc/en-us/articles/15499581457811-Interop-Server-Remote-API) | [link_7f05908185248c4b80a0ae85](ANSYS_Document/Lumerical/unknown/official_body_20261104/link_7f05908185248c4b80a0ae85.md) | `sources.csv#link_7f05908185248c4b80a0ae85` |
| [Getting Started with lumopt - Python API](https://optics.ansys.com/hc/en-us/articles/360050995394-Getting-Started-with-lumopt-Python-API) | [link_84feff97e81bfbfc986d395e](ANSYS_Document/Lumerical/unknown/official_body_20261104/link_84feff97e81bfbfc986d395e.md) | `sources.csv#link_84feff97e81bfbfc986d395e` |
| [Photonic Inverse Design Overview - Python API](https://optics.ansys.com/hc/en-us/articles/360049853854-Photonic-Inverse-Design-Overview-Python-API) | [link_a4b86b16ad919b4136db8262](ANSYS_Document/Lumerical/unknown/official_body_20261104/link_a4b86b16ad919b4136db8262.md) | `sources.csv#link_a4b86b16ad919b4136db8262` |
| [Session Management - Python API](https://optics.ansys.com/hc/en-us/articles/360041873053-Session-Management-Python-API) | [link_c642359a011861d6a54004b9](ANSYS_Document/Lumerical/unknown/official_body_20261104/link_c642359a011861d6a54004b9.md) | `sources.csv#link_c642359a011861d6a54004b9` |
| [Lumerical scripting language - By category](https://optics.ansys.com/hc/en-us/articles/360037228834-Lumerical-scripting-language-By-category) | [link_e26fb24b79985b70a64d774d](ANSYS_Document/Lumerical/unknown/official_body_20261104/link_e26fb24b79985b70a64d774d.md) | `sources.csv#link_e26fb24b79985b70a64d774d` |
| [Optimizable Geometry - Python API](https://optics.ansys.com/hc/en-us/articles/360052044913-Optimizable-Geometry-Python-API) | [link_e4a12461bc655308e692d6d5](ANSYS_Document/Lumerical/unknown/official_body_20261104/link_e4a12461bc655308e692d6d5.md) | `sources.csv#link_e4a12461bc655308e692d6d5` |
| [Script Commands as Methods - Python API](https://optics.ansys.com/hc/en-us/articles/360041579954-Script-Commands-as-Methods-Python-API) | [link_274d35a5f733c1af2277a436](ANSYS_Document/Lumerical/unknown/official_body_20261104/link_274d35a5f733c1af2277a436.md) | `sources.csv#link_274d35a5f733c1af2277a436` |
| [Working with Simulation Objects – Python API](https://optics.ansys.com/hc/en-us/articles/39744946400659-Working-with-Simulation-Objects-Python-API) | [link_4088e1ff2f0f519c913e8b23](ANSYS_Document/Lumerical/unknown/official_body_20261104/link_4088e1ff2f0f519c913e8b23.md) | `sources.csv#link_4088e1ff2f0f519c913e8b23` |
| [Passing Data - Python API](https://optics.ansys.com/hc/en-us/articles/360041401434-Passing-Data-Python-API) | [link_386e427d8c85a6a873a19f0b](ANSYS_Document/Lumerical/unknown/official_body_20261104/link_386e427d8c85a6a873a19f0b.md) | `sources.csv#link_386e427d8c85a6a873a19f0b` |
| [Accessing Simulation Results – Python API](https://optics.ansys.com/hc/en-us/articles/39744236202771-Accessing-Simulation-Results-Python-API) | [link_bb4e1b262b3ff0acbbfa3edd](ANSYS_Document/Lumerical/unknown/official_body_20261104/link_bb4e1b262b3ff0acbbfa3edd.md) | `sources.csv#link_bb4e1b262b3ff0acbbfa3edd` |
| [Getting Started with lumslurm - Python API](https://optics.ansys.com/hc/en-us/articles/20990924220691-Getting-Started-with-lumslurm-Python-API) | [link_3a0dd48eef814987d6fecf0b](ANSYS_Document/Lumerical/unknown/official_body_20261104/link_3a0dd48eef814987d6fecf0b.md) | `sources.csv#link_3a0dd48eef814987d6fecf0b` |

官方正文補齊前文「原文未快取」狀態；第三方、外連附件及其他命令／產品手冊仍列缺口。詳[本批報告](../maintenance/knowledge_dictionary_passes/2026-11-04/lumerical_module_conversion_report_20261104.md)。
