# PCB 多層板熱翹曲工作流字典

本頁整理本專案現存的 Stackup → 幾何 → arithmetic ROM 材料巨集 → Mechanical設定流程。程式原始碼的靜態行為、目前可讀輸入、歷史記錄及物理驗證分開記錄；`pending_physical_validation` 仍保留。此處的ROM是 **Rule of Mixtures**，不是reduced-order model，也沒有證明已得到經校準的正交異向性材料。

來源以現行[skill](../../agents/skills/materials-reliability/pcb-warpage-analysis/SKILL.md)（[來源清冊](sources.csv#agents_skills_materials-reliability_pcb-warpage-analysis_SKILL)）與四份scripts為入口；[Mechanical](mechanical.md)、[Thermal](thermal.md)、[SpaceClaim](spaceclaim.md)另有產品字典。官方MAPDL說明為v261；現存scratch log標示MAPDL2025R1。程式本身未宣告已驗證的完整產品配對，不能由這兩者推定runtime相容。

## Stackup輸入與幾何自動化

### 實際檔案與資料形狀

本輪只讀盤點的輸入位於歷史記錄所指資料目錄，並記下SHA快照：

| 輸入 | 程式讀取的欄位／用途 | 本輪可讀內容 |
| --- | --- | --- |
| MCP_Test.xlsx／Parameters | `Parameter`、`Value`；`L`、`W`、`Ti`、`Tf` | L=420mm、W=380mm、Ti=30°C、Tf=220°C。[來源清冊](sources.csv#local_pcb_stackup_xlsx) |
| MCP_Test.xlsx／Stackup | 首欄layer ID、`Thickness (mm)`、`Cu (%)`、`Material` | 79列，ID1–79，厚度總和5.345049mm；Cu0–97.1951%。 |
| Copper.csv | `T (C)`、`E (GPa)`、`CTE (ppm)`、`Poisson` | 23個非空點，30–260°C。[來源清冊](sources.csv#local_pcb_copper_csv) |
| EM-370.csv | 同上；額外空欄不作主要物性 | 21個非空點，50–250°C。[來源清冊](sources.csv#local_pcb_em370_csv) |
| EM-892K2.csv | 同上 | 23個非空點，30–260°C。[來源清冊](sources.csv#local_pcb_em892k2_csv) |

這些是目前user input的內容，沒有供應商datasheet、測試方法或CTE量測定義證據。程式讀的是 **Parameters／Stackup**，不是舊字典的Dimensions工作表。

### 01幾何程式的實作範圍

[build_pcb_geometry](../../agents/skills/materials-reliability/pcb-warpage-analysis/scripts/01_build_pcb_geometry.py)（[來源清冊](sources.csv#internal_pcb_script_geometry)）讀取L／W／thickness後將mm除以1000轉為m，從頂層逐列向下extrude。幾何層數取決於Stackup列數；本次資料是79列。程式要求shared topology，呼叫失敗只印warning，不能把完成訊息當成已驗證共節點網格。

這個函式會清除目前design中的components與bodies，連線先嘗試`wnua`，失敗後可啟動可見SpaceClaim。`export_files=False`是函式預設；指定匯出才嘗試scdocx／step／pmdb，個別格式失敗會被捕捉。這些是執行前應檢閱的副作用，不是本輪已執行結果。

### Parameters的溫度不會自動傳到底

材料程式讀Parameters的`Ti`輸出TREF；Mechanical setup卻直接指定30°C與220°C，沒有讀取workbook的Ti／Tf。改Excel溫度不會自動證明Mechanical負載已同步。幾何程式可依列數建立多層，但Mechanical設定仍硬編碼選擇`L79`，需在每個實際模型核對。

來源：[02材料程式](../../agents/skills/materials-reliability/pcb-warpage-analysis/scripts/02_calculate_rom_materials.py)（[來源清冊](sources.csv#internal_pcb_script_rom)）、[03 Mechanical設定](../../agents/skills/materials-reliability/pcb-warpage-analysis/scripts/03_setup_mechanical_bc_and_solution.py)（[來源清冊](sources.csv#internal_pcb_script_mechanical)）。

## ROM材料生成與APDL巨集

### 實作中的混合模型與材料選擇

`generate_rom_apdl_macro`將Cu (%)除以100形成`f_cu`，逐點計算
`eff_E=f_cu*cu_E+(1-f_cu)*sub_E`，CTE與Poisson亦作同型算術混合。材料字串包含`370`時用EM-370，**其他字串一律走EM-892K2分支**；這不是材料名稱驗證。

程式只輸出EX、ALPX及PRXY，未輸出EY／EZ／各向CTE／shear moduli。雖輸入有`EM370(Z)`名稱，程式沒有據此建立材料座標或正交異向矩陣。將殘銅面積比例當混合分率、線性混合CTE以及材料方向的合理性，都仍需專案物理驗證。

來源：[generate_rom_apdl_macro](../../agents/skills/materials-reliability/pcb-warpage-analysis/scripts/02_calculate_rom_materials.py)（[來源清冊](sources.csv#internal_pcb_script_rom)）（函式由實際原始碼核對）。

### 23點插值、範圍與單位

目標溫度表固定為30、50、60、…、260°C，共23點。來源`E (GPa)`乘1e9成Pa、`CTE (ppm)`乘1e-6；Poisson取CSV第一列後做混合。這些原始macro量值必須與實際solver unit system核對，不能由Mechanical畫面使用mm就推定會替command snippet轉換。

程式使用`numpy.interp`且沒有傳left／right。官方文件定義範圍外預設延用端點值；目前EM-370只覆蓋50–250°C，因此30°C與260°C目標點是端點延用，不是由供應商曲線推得的外推模型。輸入T須遞增與無NaN，這次資料的四個必要欄位均非空、T嚴格遞增。

來源：[插值與輸出實作](../../agents/skills/materials-reliability/pcb-warpage-analysis/scripts/02_calculate_rom_materials.py)（[來源清冊](sources.csv#internal_pcb_script_rom)）、[numpy.interp官方文件](https://numpy.org/doc/stable/reference/generated/numpy.interp.html)（[來源清冊](sources.csv#official_pcb_numpy_interp_stable)）。stable頁本輪標示NumPy2.5；未據此指定專案執行環境版本。

### MPTEMP／MPDATA／TREF的來源界線

| 項目 | 來源能證實的內容 |
| --- | --- |
| MPTEMP | 定義溫度表；v261官方要求non-descending，最多100項、每次6欄；全空參數會清表。 |
| MPDATA | 溫度需先定義；SLOC選資料起點，每次最多6值；EX是彈性模數、ALPX是secant CTE、CTEX才是instantaneous CTE。 |
| MP | 定義材料線性物性，PRXY是major Poisson ratio。 |
| TREF | 結構熱應變參考溫度；ALPX／CTEX等定義不同，且溫度相依CTE須注意定義溫度及MPAMOD。 |

來源：[MPTEMP](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/ans_cmd/Hlp_C_MPTEMP.html)（[來源清冊](sources.csv#official_pcb_mptemp_v261)）、[MPDATA](https://ansyshelp.ansys.com/public/views/secured/corp/v261/en/ans_cmd/Hlp_C_MPDATA.html)（[來源清冊](sources.csv#official_pcb_mpdata_v261)）、[MP](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/ans_cmd/Hlp_C_MP.html)（[來源清冊](sources.csv#official_pcb_mp_v261)）、[TREF](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/ans_cmd/Hlp_C_TREF.html)（[來源清冊](sources.csv#official_pcb_tref_v261)）。

本專案generator／[template](../../agents/skills/materials-reliability/pcb-warpage-analysis/assets/apdl_rom_materials_template.mac)（[來源清冊](sources.csv#internal_pcb_apdl_template)）將`MP,PRXY`放在EX／ALPX表前，並以FINISH、/SOLU結尾。這是現存輸出順序；本輪官方命令頁沒有提供「在MPTEMP後輸入PRXY就清除全部材料」的通用規則，因此不再把那句作為已證實的MAPDL限制。

## Mechanical支承、熱載荷與結果核對

### 03設定程式實際做的事

[setup_mechanical_analysis](../../agents/skills/materials-reliability/pcb-warpage-analysis/scripts/03_setup_mechanical_bc_and_solution.py)（[來源清冊](sources.csv#internal_pcb_script_mechanical)）作用於`Analyses[0]`，刪除既有method、command snippets、thermal/displacement/fixed-support及stress/deformation類物件，建立MultiZone與15mm element size，匯入macro，施加30°C reference／environment及220°C thermal condition。這些數字是此腳本設定，並非所有PCB分析的預設或標準條件。

macro會定義material IDs；本函式沒有建立79個Named Selections或逐層EMODIF／材料指派流程。不能僅因macro匯入就宣稱每層元素用了正確材料。網格品質、實際材料IDs、接觸、CTE定義、單位、幾何與溫度場仍待讀回。

### L79三點選取與fallback contact

程式取名稱含L79的第一個body，篩選Z約為0的vertices，依X／Y組合挑三點：

| 位移物件 | 原始碼寫入的分量 |
| --- | --- |
| 3Point_P1_UX0_UY0_UZ0 | UX／UY／UZ為0。 |
| 3Point_P2_UY0_UZ0 | UY／UZ為0；程式沒有寫X分量。 |
| 3Point_P3_UZ0 | UZ為0；程式沒有寫X／Y分量。 |

三點是否唯一、非共線、實際自由分量及是否只消除所需rigid-body modes，要以模型與求解後反力／變形驗證；靜態程式不能證明無寄生應力。

fallback的觸發條件是`total_contacts==0`，之後按body名稱排序為相鄰層建Bonded contacts。它不是逐對共享節點檢查。shared topology是否成功、是否不必要地又加contact及選面正確性，都仍在`pending_physical_validation`範圍。

### Directional Deformation與PV報告範圍

程式建立L79底面（找到時）及all layers的Z Directional Deformation，另加Total Deformation；函式沒有呼叫Solve或計算peak-to-valley。

若專案選用位移型PV，需先指定同一face／node set、座標方向、reference plane／tilt處理及單位，再定義`PV=max(u_Z)-min(u_Z)`。直接取所有層變形後的Z座標範圍會混入原始厚度；這個位移範圍也不能直接當成IPC量測程序或package warpage合格門檻。

## Workflow scripts與輸出模板

[run_workflow](../../agents/skills/materials-reliability/pcb-warpage-analysis/scripts/run_full_warpage_workflow.py)（[來源清冊](sources.csv#internal_pcb_script_runner)）目前只以subprocess執行01幾何與02材料生成；step3只印出macro位置及「Execute Mechanical script to solve」。它沒有呼叫03設定、Mechanical gRPC或solver。

[相容入口README](../../docs/examples/pcb_warpage/README.md)（[來源清冊](sources.csv#internal_pcb_workflow_readme)）也說明本例不會自動求解；實作集中在skill/scripts，docs/examples中的同名入口是轉交用。[歷史AUTOMATION_LOG](../../docs/examples/pcb_warpage/AUTOMATION_LOG.md)（[來源清冊](sources.csv#internal_pcb_automation_log)）的固定79層、節點／單元數、耗時、insecure連線與全流程成功敘述，不用來覆蓋目前原始碼或證明這次已執行。 README以`PCB_STACKUP_DIR`或第一個CLI參數指定資料目錄；本輪環境變數未設定，以明確歷史路徑只讀盤點輸入。

## 目前可讀的歷史證據

已找到一份scratch `solve.out`（[來源清冊](sources.csv#local_pcb_scratch_solveout_20260802)）：標示MAPDL2025R1、jobname=file0、PCB_Warpage_Test，日期AUG02,2026。本文快照有81個WARNING標記，尾端仍是迭代資訊，沒有`SOLUTION IS DONE`或`RUN COMPLETED`字串。這只能證明該文字快照存在；沒有把它與現行四個腳本、四個輸入或可重算RST結果建立一致的provenance。

本輪沒有啟動或檢查任何活躍solver，也沒有從PNG／歷史節點數判定物理結果通過。原有 `pending_physical_validation` 不變。

## IPC／JEDEC可靠度參考來源

| 來源 | 本輪可核對的範圍 | 限制 |
| --- | --- | --- |
| IPC-9701B公開封面／目錄 | February2022，標題是surface mount attachments的thermal cycling fatigue-life test；封面寫supersedes IPC-9701A（February2006）。 | 只有目錄，不是完整標準；沒有宣稱B是所有情境最新適用版。[來源清冊](sources.csv#official_pcb_ipc9701b_toc) |
| IPC-TM-650 2.4.22C | June1999，板／panel的Bow and Twist百分比程序；scope不含assembled-board特殊考量。 | 程序與測試條件須匹配；不把原字典0.15mm或0.5%當通用驗收值。[來源清冊](sources.csv#official_pcb_ipc_tm650_2422c) |
| JESD22-B112原文 | 官方URL本輪不可讀／robots限制。 | 版本、方法與門檻未核對。[來源清冊](sources.csv#official_pcb_jedec_b112_unavailable) |
| 本機IPC／JEDEC note | 自述由NotebookLM改寫。 | 只當查找線索；未以其數字作為已證實規範。[來源清冊](sources.csv#agents_skills_materials-reliability_pcb-warpage-analysis_references_ipc_jedec_reliability_standards) |

公開來源：[IPC-9701B TOC PDF](https://www.ipc.org/TOC/IPC-9701B_TOC.pdf)（[來源清冊](sources.csv#official_pcb_ipc9701b_toc)）、[IPC 2.4.22C PDF](https://www.ipc.org/sites/default/files/test_methods_docs/2.4.22c.pdf)（[來源清冊](sources.csv#official_pcb_ipc_tm650_2422c)）。板彎扭量測、package熱翹曲與焊點疲勞是不同驗收工作；本頁沒有完成標準全文或物理驗收。

## 來源與轉換狀態

本機 catalog 沒有 PCB Warpage 條目。來源清冊的 14 筆本機檔是 Markdown、Python、APDL 模板、XLSX、CSV 與歷史 log，未列 PDF 或 HTML。本輪沒有新增轉換。先前僅在線核讀兩個 IPC 公開 PDF 的指定頁、目錄或適用範圍，未保存全文。JEDEC 原文仍列 `source_limited`。


## 2026-11-04：Wave 7 本機來源盤點與限制說明

來源清冊有 22 筆，其中 14 筆本機檔的 SHA-256 與既有紀錄相符。其餘 8 筆為線上參考或受限來源，無本機正文可核對。11 月 4 日批次未擷取這 8 個網址。歷史求解 log 缺完成標記，保留 `pending_physical_validation`。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/pcb_warpage_module_conversion_report_20261104.md)。
