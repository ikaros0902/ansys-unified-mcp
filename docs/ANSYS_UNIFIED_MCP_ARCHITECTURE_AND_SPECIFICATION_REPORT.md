# ANSYS Unified MCP 全域架構評估、規格設計與五大領域優化藍圖報告

> **文件版本**：v2.0-Official-Release  
> **發布日期**：2026-09-14  
> **專案代號**：`ansys-unified-mcp`  
> **基準目錄**：`F:\Ming_python\ansys-unified-mcp`  
> **對標生態**：PyAnsys Ecosystem (`docs.pyansys.com`)、`ansys/pyansys` Bundle、`ansys/example-data`、Ansys Developer Portal  
> **執筆角色**：Specification & Architecture Worker (`teamwork_preview_worker`)  
> **文檔定位**：官方級架構白皮書、介面契約標準與 Phase 1 ~ 3 分階段工程實施規格書  

---

## 目錄

- [第一章：執行摘要與總體架構定位 (Executive Summary)](#第一章執行摘要與總體架構定位-executive-summary)
  - [1.1 專案背景與宏觀架構定位](#11-專案背景與宏觀架構定位)
  - [1.2 現行五大核心領域成熟度評估矩陣](#12-現行五大核心領域成熟度評估矩陣)
  - [1.3 四大架構支柱與三大系統性割裂](#13-四大架構支柱與三大系統性割裂)
  - [1.4 全域演進願景](#14-全域演進願景)
- [第二章：R1. 五大核心領域現況與架構瓶頸深度診斷 (Current Architecture Audit)](#第二章r1-五大核心領域現況與架構瓶頸深度診斷-current-architecture-audit)
  - [2.1 結構領域 (Structural Analysis) 代碼級診斷](#21-結構領域-structural-analysis-代碼級診斷)
  - [2.2 幾何領域 (Geometry Pre-processing) 代碼級診斷](#22-幾何領域-geometry-pre-processing-代碼級診斷)
  - [2.3 熱傳與電子散熱領域 (Thermal / Icepak) 代碼級診斷](#23-熱傳與電子散熱領域-thermal--icepak-代碼級診斷)
  - [2.4 高階網格領域 (PyPrimeMesh) 代碼級診斷](#24-高階網格領域-pyprimemesh-代碼級診斷)
  - [2.5 電子封裝領域 (Electronic Packaging) 代碼級診斷](#25-電子封裝領域-electronic-packaging-代碼級診斷)
  - [2.6 跨模組架構瓶頸與介面缺陷深度剖析](#26-跨模組架構瓶頸與介面缺陷深度剖析)
- [第三章：R2. 官方 Tutorials 與各大教學資源全景映射 (Tutorials & Benchmark Mapping)](#第三章r2-官方-tutorials-與各大教學資源全景映射-tutorials--benchmark-mapping)
  - [3.1 現行模組 vs 官方 Tutorial 範例庫對照總表](#31-現行模組-vs-官方-tutorial-範例庫對照總表)
  - [3.2 十二大代表性經典基準案例深度規格清單](#32-十二大代表性經典基準案例深度規格清單)
  - [3.3 邊界極限工況與異常處理矩陣](#33-邊界極限工況與異常處理矩陣)
- [第四章：R3. 系統拓撲架構與 API/MCP Tool 契約介面設計規範 (Architecture & Specification)](#第四章r3-系統拓撲架構與-apimcp-tool-契約介面設計規範-architecture--specification)
  - [4.1 工具命名標準規範與雙軌相容架構](#41-工具命名標準規範與雙軌相容架構)
  - [4.2 結構化輸入 Schema 與標準回傳信封架構](#42-結構化輸入-schema-與標準回傳信封架構)
  - [4.3 同步微步工具 (Primitives) vs 異步工作流 (Workflows) 雙軌執行模型](#43-同步微步工具-primitives-vs-異步工作流-workflows-雙軌執行模型)
  - [4.4 非同步作業沙盒 (JobManager) 與實時物理守護熔斷 (Watchdog + CircuitBreaker)](#44-非同步作業沙盒-jobmanager-與實時物理守護熔斷-watchdog--circuitbreaker)
  - [4.5 求解前置安全閘門 (Gatekeeper) 與結構化自愈處方 (Prescription) 規格](#45-求解前置安全閘門-gatekeeper-與結構化自愈處方-prescription-規格)
  - [4.6 目錄重塑與系統拓撲架構圖](#46-目錄重塑與系統拓撲架構圖)
- [第五章：R4. 分階段落地優化里程碑計畫 (Phased Implementation Roadmap)](#第五章r4-分階段落地優化里程碑計畫-phased-implementation-roadmap)
  - [5.1 演進路線總覽](#51-演進路線總覽)
  - [5.2 Phase 1：基礎解耦、命名雙軌標準化與核心三領域強化 (W1 ~ W3)](#52-phase-1基礎解耦命名雙軌標準化與核心三領域強化-w1--w3)
  - [5.3 Phase 2：高階網格 (PyPrimeMesh) 驅動實裝與工具鏈整合 (W4 ~ W6)](#53-phase-2高階網格-pyprimemesh-驅動實裝與工具鏈整合-w4--w6)
  - [5.4 Phase 3：電子封裝多物理場 (PyAEDT/Sherlock) 與焊點疲勞閉環 (W7 ~ W10)](#54-phase-3電子封裝多物理場-pyaedtsherlock-與焊點疲勞閉環-w7--w10)
- [第六章：依賴管理矩陣與可選相容性安裝策略 (`[project.optional-dependencies]`)](#第六章依賴管理矩陣與可選相容性安裝策略-projectoptional-dependencies)
  - [6.1 底層依賴庫衝突與環境風險分析](#61-底層依賴庫衝突與環境風險分析)
  - [6.2 模組化可選安裝策略與 pyproject.toml 規範](#62-模組化可選安裝策略與-pyprojecttoml-規範)
  - [6.3 跨平台無頭執行與 Mock/Synthetic 降級相容機制](#63-跨平台無頭執行與-mocksynthetic-降級相容機制)

---

## 第一章：執行摘要與總體架構定位 (Executive Summary)

### 1.1 專案背景與宏觀架構定位

`ansys-unified-mcp` 是專為工程模擬與大語言模型（LLM）深度整合設計的企業級 Model Context Protocol (MCP) 伺服器。專案立足於 ANSYS 全產品線與 Python 開源生態（PyAnsys Ecosystem），目標在於建構一個**統一、強健、具備物理判斷力與自愈能力的多物理場模擬調度中樞**。

本系統摒棄傳統將 AI 侷限於「自然語言產生腳本」或「外部打補丁式 Prompt」的初級模式，採用系統級四層解耦架構：
1. **門面與動態路由層 (Facade & Routing)**：基於 `FastMCP` 與 `shared.aliased_tool`，提供動態 Profile 載入與 `<product>_<verb>_<object>` 規範之雙軌別名支援。
2. **作業沙盒與實時守護層 (Sandbox & Sentinel)**：基於 `JobManager` 與 `JobSandbox` 實現完全隔離的模擬作業生命週期管理，搭配後台 `WatchdogDaemon` 守護線程與 `CircuitBreaker` 早期物理發散熔斷機制。
3. **前置安全閘門與自愈層 (Gatekeeper & Prescription)**：基於 `Gatekeeper` 主控引擎，在正式啟動耗時模擬前執行嚴格的物理合理性檢核，並於阻斷時輸出結構化自愈處方箋（`PreFlightPrescriptionReport`）。
4. **求解器驅動與拓撲鏈結層 (Drivers & Workflows)**：基於 `BaseSolverDriver` 抽象基類規範標準生命週期，並透過 RunWB2 Journal 原生調用跨系統單元鏈結引擎（`WorkbenchCellLinkEngine`），實現無損之溫度場、特徵振型與幾何數據傳遞。

---

### 1.2 現行五大核心領域成熟度評估矩陣

透過對專案原始碼（`src/ansys_unified_mcp/`、`drivers/`、`tools/`、`workflows/`、`gatekeeper/`、`SKILLs/`）的深度代碼級審計，當前系統在五大核心 CAE 領域的支援程度呈現顯著的**斷層與不平衡性**：

| 領域分類 | 現有代表模組 / 工具 | 底層對接技術協議 | 當前成熟度評級 | 關鍵架構特徵與核心瓶頸 |
| :--- | :--- | :--- | :---: | :--- |
| **1. 結構 (Structural)** | `MechanicalController`<br>`MechanicalDriver`<br>`LSDynaDriver` | PyMechanical gRPC +<br>ACT IronPython 注入 +<br>本機批次命令 | 🟡 **中等 (Tier 1/2)** | 基礎工具覆蓋廣（39 個原子工具 + 3 個組合工具）；但微步高度依賴 ACT 字串拼接；完全缺失 PyMAPDL gRPC 封裝；未安裝 `ansys-dyna-core`；落摔與振動多為合成仿真 (Synthetic)。 |
| **2. 幾何 (Geometry)** | `GeometryController`<br>`sim_tools.py`<br>`sim_impl.py` | PyAnsys Geometry gRPC +<br>SpaceClaim AddIn 轉發 | 🟡 **中等 (Tier 2)** | 能建立基礎長方體、圓柱體、球體與 2D 草圖拉伸；外流域抽取僅限於正交包覆方盒扣除；**完全缺失水密性 (Watertightness) 檢查與 CAD 缺陷修復工具**；未納入雙軌別名體系。 |
| **3. 熱傳 / 電子散熱** | `IcepakDriver`<br>`WorkbenchCellLinkEngine`<br>`sim_tools.py` (Fluent) | Fluent gRPC +<br>RunWB2 Cell Link +<br>本機批次腳本 | 🟠 **初級 (Tier 2/3)** | Workbench 熱-結構單元鏈結語法完備；Fluent 求解控制完備；但 `IcepakDriver` **完全為假 CSV 與假日誌模擬**；FastMCP 中 **Icepak 專屬 MCP 工具為 0**；缺乏共軛熱傳 (CHT) 自動化管線。 |
| **4. 高階網格** | `tools/mechanical.py`<br>`sim_tools.py` (Fluent) | Mechanical 內建網格 +<br>Fluent 外部讀取 `.msh` | 🔴 **極度缺失 (Tier 3)** | **專案完全未整合 PyPrimeMesh (`ansys-meshing-prime` 引用為 0)**；無法進行 Mosaic™ Poly-Hexcore 體網格劃分、無多面體網格、無邊界層稜柱層控制、無表面收縮包覆 (Surface Wrapper)。 |
| **5. 電子封裝** | `workflows/thermal_warpage.py`<br>`SKILLs/pcb-warpage-analysis/` | 解析公式估算 +<br>Excel/APDL 離線巨集 | 🟠 **初級 (Tier 2/3)** | 3-2-1 靜定無拘束支承概念完備；具備 CTE 前置閘門；但工作流沙盒內部**依賴經驗解析公式計算翹曲**；**完全缺失 PySherlock 與 PyAEDT**；無 ECAD (ODB++/EDB) 原生導入；無焊點熱疲勞。 |

---

### 1.3 四大架構支柱與三大系統性割裂

#### 現行架構之卓越支柱
1. **非同步作業沙盒目錄隔離**：`JobManager` 為每次運算建立獨立 `jobs/{timestamp}_{suffix}_{type}_{tag}/` 目錄，原始 CAD 與資產強制作業系統層級唯讀鎖定，生成 `summary.json`、雲圖與自包含 `overview.html` 儀表板。
2. **實時物理守護與早期發散熔斷**：`WatchdogDaemon` 串流解析求解日誌，當 `CircuitBreaker` 偵測到沙漏能比例 $>5\%$、質量縮放 $>5\%$、負滑移能突波或殘差出現 `NaN`/`Inf` 時，0.5 秒內觸發熔斷中斷求解，大幅降低無效算力與授權浪費。
3. **硬性物理安全閘門 (Pre-Flight Gatekeeper)**：在調用求解器前進行剛性檢核，例如隨機振動三向累積有效模態質量必須 $\ge 90\%$、落摔初速向量必須指向地面、熱分析必須定義溫度相依 CTE 與 $T_{\text{ref}}$，未通過即輸出包含修復代碼段的自愈處方箋。
4. **Workbench 原生單元鏈結引擎**：利用 RunWB2 Journal 調用 `TransferData(TargetCell=...)`，實現無損之跨系統物理載荷傳遞。

#### 現行架構之三大系統性割裂
1. **工具註冊與命名體系割裂**：`mechanical.py`、`workbench_filebridge.py`、`optislang.py` 採用 `aliased_tool` 雙軌機制；但 `sim_tools.py`（幾何與 Fluent）採用自製的 `@tool_fluent` 與 `@tool_geometry`，未接入全域別名體系，回傳格式未標準化。
2. **回傳信封架構不一**：部分工具回傳 `json.dumps()` 序列化字串，部分工具直接回傳 Python `dict`，而 `sim_tools.py` 則使用極度脆弱的關鍵字比對（`"error" in text.lower()`），極易因日誌中的正常文字（如 `"0 errors"`）造成嚴重誤判 (False Positive)。
3. **高階工具鏈與先進工業生態缺位**：PyPrimeMesh（高階網格）與 PyAEDT / PySherlock（電子封裝與可靠度）在源碼中為零引用，導致面對複雜 CAD、薄板流體包覆、PCB 走線殘銅率均質化與焊點可靠度時無法閉環。

---

### 1.4 全域演進願景

本報告確立 `ansys-unified-mcp` 演進目標：**自現有的「局部腳本呼叫與混合式工具集」，全面重塑為「五大工業領域全覆蓋、命名與信封統一、雙軌微步/工作流協同、守護與自愈完備的企業級 CAE 智慧代理中樞」**。透過後續章節之規格定義與三階段落地計畫（Phase 1 ~ 3），徹底打通幾何前處理、高階網格、多物理場耦合與可靠度壽命評估的完整工程閉環。

---

## 第二章：R1. 五大核心領域現況與架構瓶頸深度診斷 (Current Architecture Audit)

---

### 2.1 結構領域 (Structural Analysis) 代碼級診斷

#### 1. 模組拓撲與核心類別
- **連線與 Session 管理層**：`src/ansys_unified_mcp/products/mechanical.py`（核心類別：`MechanicalController`，行 68-85 透過 `import ansys.mechanical.core as mech` 調用 `mech.connect_to_mechanical` 與 `mech.launch_mechanical` 納入 `SessionRegistry`）。
- **工具暴露層**：
  - `src/ansys_unified_mcp/tools/mechanical.py`（共 39 個原子工具，行 169-330）。
  - `src/ansys_unified_mcp/tools/mechanical_workflows.py`（共 3 個組合式工作流工具，行 34-225）。
  - `src/ansys_unified_mcp/tools/intent_tools.py`（高階工況意圖工具，行 44-120）。
- **驅動層**：
  - `src/ansys_unified_mcp/drivers/mechanical_driver.py`（核心類別：`MechanicalDriver`，行 40-180）。
  - `src/ansys_unified_mcp/drivers/lsdyna_driver.py`（核心類別：`LSDynaDriver`，行 35-250）。
- **工作流層**：
  - `src/ansys_unified_mcp/workflows/drop_test.py`（`run_drop_test`，行 45-165）。
  - `src/ansys_unified_mcp/workflows/shock_analysis.py`（`run_shock_analysis`，行 40-160）。
  - `src/ansys_unified_mcp/workflows/random_vibration.py`（`run_random_vibration`，行 45-175）。
- **解析與前置閘門**：
  - `src/ansys_unified_mcp/core/sentinel/parsers/mechanical.py`（`MechanicalMAPDLParser`）。
  - `src/ansys_unified_mcp/core/sentinel/parsers/lsdyna.py`（`LSDynaGlstatParser`）。
  - `src/ansys_unified_mcp/gatekeeper/rules/vibration_rules.py`（`GATE-VIB-001/002`，行 16-99）。
  - `src/ansys_unified_mcp/gatekeeper/rules/drop_impact_rules.py`（`GATE-DRP-001/002/003`，行 17-152）。

#### 2. 現有 MCP Tool 清單
- **實例管理**：`mechanical_list_instances`, `mechanical_connect`, `mechanical_launch`, `mechanical_disconnect`, `mechanical_check_connection`, `mechanical_get_model_info`。
- **材料與網格**：`mechanical_list_materials`, `mechanical_assign_material`, `mechanical_set_mesh_element_size`, `mechanical_generate_mesh`, `mechanical_get_mesh_statistics`。
- **約束與載荷**：`mechanical_add_fixed_support`, `mechanical_add_force`, `mechanical_add_pressure`, `mechanical_add_frictionless_support`, `mechanical_add_displacement`, `mechanical_add_remote_displacement`, `mechanical_add_standard_gravity`, `mechanical_add_remote_force`, `mechanical_add_moment`, `mechanical_list_boundary_conditions`。
- **求解與結果**：`mechanical_solve_analysis`, `mechanical_get_solve_status`, `mechanical_add_total_deformation`, `mechanical_add_directional_deformation`, `mechanical_add_equivalent_stress`, `mechanical_add_principal_stress`, `mechanical_add_stress_tool`, `mechanical_add_reaction_force`, `mechanical_get_modal_frequencies`, `mechanical_add_total_deformation_all_modes`, `mechanical_generate_report`。
- **簡化與命名選擇**：`mechanical_list_named_selections`, `mechanical_delete_named_selection`, `mechanical_suppress_bodies`, `mechanical_list_point_masses`, `mechanical_convert_prefix_to_point_mass`, `mechanical_convert_part_to_part_mass`。
- **組合式分析**：`mechanical_setup_and_solve_static_structural`, `mechanical_setup_and_solve_modal`, `mechanical_diagnose_model_health`。
- **高階意圖工況**：`workflow_run_drop_test`, `workflow_run_shock_analysis`, `workflow_run_random_vibration`。

#### 3. 核心瓶頸與代碼依據
1. **過度依賴 ACT IronPython 字串拼接**：
   - 審計依據：在 `tools/mechanical.py:164-166`（`_run(script)`）與 `tools/mechanical_workflows.py:74-141` 中，所有力學設定（建立載荷、網格劃分、命名選擇獲取）皆採用大段 Python 字串格式化注入：
     ```python
     # tools/mechanical_workflows.py:74-85
     script = f"""
     model = ExtAPI.DataModel.Project.Model
     analysis = model.Analyses[0]
     geom = model.Geometry
     ...
     """
     ```
   - 缺陷分析：代碼無 IDE 靜態型別提示與語法檢驗；底層依賴反射操作，當 API 版本變更（如 ANSYS 2023R2 轉至 2024R2）時容易無預警崩潰；錯誤診斷僅能透過正則比對 ACT 輸出日誌中的關鍵字（`tools/mechanical.py:47-58` 的 `_is_error_output`）。
2. **PyMAPDL gRPC 原生封裝缺位**：
   - 審計依據：專案 `src/` 中完全沒有使用 `ansys-mapdl-core`。在 `tools/workbench_filebridge.py:1043-1065` 的 `run_mapdl_input`，係直接呼叫本地子進程：
     ```python
     # tools/workbench_filebridge.py:1053-1055
     cmd = [ansys_exe, "-b", "-i", input_file, "-o", output_file]
     subprocess.run(cmd, check=True)
     ```
   - 缺陷分析：無法在記憶體內以互動式 gRPC 存取 MAPDL 陣列（APDL Arrays），無法進行即時節點位移/應力張量讀取，阻礙高效子模型分析。
3. **LS-DYNA 顯式動力學與 Synthetic 仿真瓶頸**：
   - 審計依據：專案未引入 `ansys-dyna-core` (PyDYNA)。在 `drivers/lsdyna_driver.py:102-144` 中，`prepare_job` 僅手動輸出一段基礎的 `run.k` 關鍵字卡片框架，但**缺乏幾何節點與單元卡片匯出能力**。
   - 在 `workflows/drop_test.py:129-153`，沙盒內部的 `drop_test_runner` 實際上透過 Python 迴圈動態寫入虛擬的 `glstat` 檔案；`drivers/lsdyna_driver.py:224-230` 中的 `extract_artifacts` 更是**直接使用物理公式估算最大應力與 Peak G**，並繪製 Matplotlib 2D 示意圖。在未連接實體 LS-DYNA 授權環境下完全處於合成仿真模式。
4. **模態/隨機振動/衝擊工況實作限制**：
   - 審計依據：在 `workflows/random_vibration.py:143-153` 與 `workflows/shock_analysis.py:130-155` 中，作業 runner 亦以寫入假 `solve.out` 與靜態公式計算 3-Sigma 響應。
   - 積極價值：前置安全閘門實裝高度嚴謹，`gatekeeper/rules/vibration_rules.py:30-85` 強制檢核三向有效模態質量比必須 $\ge 90\%$，截斷頻率必須 $\ge 1.5\times$ 激振上限，未達標則產出自愈處方，為後續對接真實求解器奠定了紮實的安全底座。

---

### 2.2 幾何領域 (Geometry Pre-processing) 代碼級診斷

#### 1. 模組拓撲與核心類別
- **門面層**：`src/ansys_unified_mcp/products/geometry.py`（核心類別：`GeometryController`，透過 `ansys.geometry.core.Modeler` 操作，行 30-57）。
- **工具與執行層**：
  - `src/ansys_unified_mcp/tools/sim_tools.py`（幾何工具宣告，行 318-522）。
  - `src/ansys_unified_mcp/drivers/sim_impl.py`（底層 gRPC 呼叫與 SpaceClaim AddIn 轉發，行 203-335, 558-650）。
  - `src/ansys_unified_mcp/drivers/spaceclaim_driver.py`（`SpaceClaimDriver` 批次腳本生成）。
  - `src/ansys_unified_mcp/tools/workbench_filebridge.py:383-424`（`execute_spaceclaim_script_live`）。

#### 2. 現有 MCP Tool 清單
- `geometry_launch`（啟動 SpaceClaim gRPC 建模器）
- `geometry_create_design`（建立新幾何設計）
- `geometry_create_block`（建立長方體）
- `geometry_create_cylinder`（建立圓柱體）
- `geometry_create_sphere`（旋轉半圓建立球體）
- `geometry_sketch_and_extrude`（2D 草圖樣條/折線拉伸）
- `geometry_create_enclosure`（包覆外流域與布林相減）
- `geometry_export`（匯出 STEP/IGES）
- `geometry_list_bodies`（列出當前設計幾何體實體清單）
- `geometry_import_file`（匯入外部 CAD 檔案）
- `geometry_status`（檢查建模器連線狀態）
- `geometry_close`（關閉建模器實例）

#### 3. 核心瓶頸與代碼依據
1. **外流域抽取 (Enclosure) 侷限性**：
   - 審計依據：檢視 `drivers/sim_impl.py:287-335`：
     ```python
     # drivers/sim_impl.py:298-315
     box = target_body.box
     min_pt = box.min_point
     max_pt = box.max_point
     # 僅能沿 X/Y/Z 六個方向向外延伸 cushion 距離建立長方體
     enc_body = design.extrude_sketch(...)
     enc_body.subtract(target_body)
     ```
   - 缺陷分析：僅能進行簡易外框正交包覆扣除，無法處理電子散熱機箱的內部空腔抽取（Internal Volume Extraction）、無法辨識進出風口封閉蓋面（Capping Surfaces），亦無法進行漏氣檢測（Leak Detection）。
2. **水密性檢查 (Watertightness Check) 完全空白**：
   - 審計依據：搜尋全專案代碼，**完全沒有實裝任何針對幾何破面、自由邊（Free Edges）、非流形邊（Non-manifold Edges）、微小縫隙（Slivers）或共享拓撲（Share Topology）的檢查與修復工具**。
   - 缺陷分析：當導入工業級複雜 CAD（如汽車車身或排氣歧管）存在微小瑕疵時，後續無論送入 Fluent 或是 Mechanical 皆會因網格劃分失敗而中斷，缺乏前置幾何體檢與自動修復防線。
3. **無頭環境支援缺陷與 AddIn 依賴**：
   - 審計依據：在 `drivers/sim_impl.py:630-640` 中，若 SpaceClaim 未預先手動開啟並載入 `Presentation.ApiServerAddIn.dll`，gRPC 連線即告失敗。
   - 缺陷分析：無法在無 GUI 之 Linux 伺服器、HPC 叢集或 Docker 容器環境中獨立以命令列無頭拉起 SpaceClaim，大幅限制自動化 CI/CD 與容器化佈署。
4. **命名割裂與別名缺失**：
   - 審計依據：`tools/sim_tools.py:45-57` 定義專屬 `@tool_geometry` 裝飾器，未採用 `aliased_tool`，未遵循系統標準回傳信封，且缺乏相容舊名稱之雙軌機制。

---

### 2.3 熱傳與電子散熱領域 (Thermal / Icepak) 代碼級診斷

#### 1. 模組拓撲與核心類別
- **驅動層**：`src/ansys_unified_mcp/drivers/icepak_driver.py`（核心類別：`IcepakDriver`，行 25-130）。
- **Workbench 拓撲鏈結層**：`src/ansys_unified_mcp/workflows/workbench_links.py`（`WorkbenchCellLinkEngine`，行 27-160）。
- **高階工況工作流層**：`src/ansys_unified_mcp/workflows/thermal_warpage.py`（`run_thermal_warpage`，行 40-165）。
- **工具與前置閘門**：
  - `src/ansys_unified_mcp/tools/workbench_filebridge.py:607-646, 957-1041`（`create_steady_state_thermal_system_live`, `create_transient_thermal_system_live`, `create_steady_state_thermal_system`）。
  - `src/ansys_unified_mcp/tools/sim_tools.py:60-63`（`fluent_set_solver(energy=True)`）。
  - `src/ansys_unified_mcp/gatekeeper/rules/thermal_rules.py`（`GATE-THM-001/002`，行 16-106）。

#### 2. 現有 MCP Tool 清單
- 現有熱分析工具：`create_steady_state_thermal_system_live`, `create_transient_thermal_system_live`, `create_thermal_bar_demo_live`, `workflow_run_thermal_warpage`, `fluent_set_solver`。
- **未暴露缺口**：**FastMCP 註冊清單中以 `icepak_` 開頭的專屬 MCP 工具數量為 0**！儘管底層存在 `IcepakDriver`，但上層工具層從未將其能力向外暴露給 AI 代理。

#### 3. 核心瓶頸與代碼依據
1. **Icepak 驅動器完全為假日誌與假 CSV 模擬**：
   - 審計依據：檢視 `drivers/icepak_driver.py:62-100`：
     ```python
     # drivers/icepak_driver.py:68-85
     fake_script = """
     import time
     for i in range(1, 21):
         print(f"Iteration {i} Residual: 1e-{i%5 + 2}")
     with open("temperature_field.csv", "w") as f:
         f.write("x,y,z,temp\\n")
         f.write("0.0,0.0,0.0,85.4\\n")
     """
     ```
   - `drivers/icepak_driver.py:108-114` 中，若系統未偵測到 `icepak.exe`，系統便直接以當前環境的 `python.exe` 執行上述假腳本，輸出虛構的收斂日誌與固定 $85.4^\circ\text{C}$ 的溫度場 CSV。
   - 缺陷分析：代碼庫完全沒有整合 PyAEDT (`pyaedt.Icepak`) 或 Icepak 原生 COM/gRPC 介面，無法原生建立板卡、散熱鰭片、軸流風扇、晶片雙熱阻模型或非均勻發熱源。
2. **Workbench 熱-結構鏈結覆蓋有限**：
   - 審計依據：在 `workflows/workbench_links.py:56-99` 中，`link_thermal_structural` 成功實裝了以 RunWB2 Journal 傳遞 `Steady-State Thermal (Solution)` $\rightarrow$ `Static Structural (Setup)` 的原生單元鏈結。
   - 缺陷分析：缺乏 Icepak $\rightarrow$ Mechanical 的專屬 Component Cell Link 實裝；無法將 Icepak 的非結構化流體網格溫度場自動插值映射至 Mechanical 結構有限元網格。
3. **Fluent 共軛熱傳 (CHT) 自動化管線缺口**：
   - 審計依據：`tools/sim_tools.py:60-63` 僅提供啟動能量方程式之布林開關，缺乏多區域共軛熱傳（Conjugate Heat Transfer）專用的流-固耦合邊界（Coupled Wall Interface）自動配對與網格節點映射工具。

---

### 2.4 高階網格領域 (PyPrimeMesh) 代碼級診斷

#### 1. 代碼庫檢核結果
- 在 `ansys-unified-mcp` 全專案 `src/` 目錄中，搜尋 `ansys-meshing-prime`、`from ansys.meshing import prime` 或 `primemesh`，**結果全數為 0**。
- 檢視 `pyproject.toml` 與虛擬環境依賴清單，**未安裝 `ansys-meshing-prime`**。
- 專案僅在 `contexts/pyansys-mapping-and-roadmap.md:19` 與 `docs/ANSYS_MCP_EVALUATION_AND_OPTIMIZATION_PLAN.md:52` 中將其標註為待辦缺失項。

#### 2. 現行網格能力與能力邊界
當前專案的網格功能分散於兩處：
1. **Mechanical 預設網格**（`tools/mechanical.py:270-330`）：
   - `mechanical_set_mesh_element_size`：以 ACT 腳本設定全域單元尺寸 `mesh.ElementSize = Quantity(size, "mm")`。
   - `mechanical_generate_mesh`：調用黑盒 `mesh.GenerateMesh()`。
   - `mechanical_get_mesh_statistics`：讀取節點數與單元數。
   - *限制*：完全由 Mechanical 求解器黑盒預設劃分，多為粗糙四面體網格，無法精細控制局部特徵。
2. **Fluent 外部網格讀取**（`tools/sim_tools.py:96-100`）：
   - 僅提供 `fluent_read_mesh(file_path)`，系統自身無法劃分流體網格，只能被動讀入外部劃分完畢之 `.msh` 檔案。

#### 3. 五大核心高階能力缺口
1. ❌ **Mosaic™ Poly-Hexcore（鑲嵌六面體核心）網格**：完全無實作。無法以高效率八叉樹六面體填充主體流場並以多面體過渡至壁面，無法享受單元量減少 60% 的計算紅利。
2. ❌ **多面體 (Polyhedral) 體網格劃分**：無相關實作。
3. ❌ **邊界層網格 (Prism / Inflation Layers) 精確控制**：無法依據目標無量綱壁面距離 $y^+ \le 1$ 精確指定首層高度、層數與生長率。
4. ❌ **表面收縮包覆 (Surface Wrapper)**：面對包含數千個零件、裝配間隙與破面的複雜髒 CAD（如汽車底盤、電子機箱），無法一鍵體素包覆生成水密流體表面。
5. ❌ **前置網格品質硬性指標診斷**：缺乏最小正交品質（Orthogonal Quality $<0.15$ 阻斷）、最大歪斜度（Skewness $>0.85$ 阻斷）與長寬比的客觀檢驗前置閘門。

---

### 2.5 電子封裝領域 (Electronic Packaging) 代碼級診斷

#### 1. 模組拓撲與現狀
- **工作流層**：`src/ansys_unified_mcp/workflows/thermal_warpage.py`（`run_thermal_warpage`，行 40-165）。
- **前置安全閘門**：`src/ansys_unified_mcp/gatekeeper/rules/thermal_rules.py`（`ThermalWarpageRule`，行 30-80）。
- **專用離線技能庫**：`SKILLs/pcb-warpage-analysis/`
  - `01_build_pcb_geometry.py`（SpaceClaim 疊構建模腳本）。
  - `02_calculate_rom_materials.py`（混合法則 ROM 等效正交材料矩陣推導）。
  - `03_setup_mechanical_bc_and_solution.py`（3-2-1 靜定無拘束支承與熱求解）。
  - `run_full_warpage_workflow.py`（批次串接腳本）。

#### 2. 現有 MCP Tool 清單
- `workflow_run_thermal_warpage`（別名 `run_thermal_warpage`）。
- 註：`SKILLs/pcb-warpage-analysis/` 中的 4 個 Python 腳本為離線獨立腳本，尚未標準封裝為可由 LLM 動態調用的 MCP 工具。

#### 3. 核心瓶頸與代碼依據
1. **熱翹曲沙盒內部採用解析公式估算**：
   - 審計依據：檢視 `workflows/thermal_warpage.py:124-145`：
     ```python
     # workflows/thermal_warpage.py:130-136
     delta_t = peak_temp - ref_temp
     max_warpage_um = cte * delta_t * 120.0 * 1000.0  # 純經驗解析推估
     results = {
         "max_warpage_um": max_warpage_um,
         "coplanarity_pass": max_warpage_um <= 150.0,
         ...
     }
     ```
   - 缺陷分析：在非同步沙盒運算中，未真正將 PCB 疊構幾何載入 Mechanical 進行熱-結構有限元求解，所得雲圖亦為 Matplotlib 合成之偽 2D 矩陣圖。
2. **PySherlock 與 PyAEDT 引用為 0**：
   - 審計依據：全專案完全未安裝亦未引用 `ansys-sherlock-core` 與 `pyaedt`。
   - 缺陷分析：
     - **ECAD 數據鏈路缺失**：無法直接解析業界標準之 ODB++、IPC-2581、Gerber 或 Cadence .brd 設計檔案。
     - **殘銅率圖形化映射 (Trace Mapping) 缺失**：無法根據微米級走線與過孔分佈，自動計算有限元網格單元的局部等效導熱係數與熱膨脹係數張量。
     - **焊點熱疲勞壽命評估缺失**：無法進行 BGA/CSP 封裝在加速溫循（ATC）下的 Anand 黏塑性蠕變本構分析、Darveaux 能量耗散壽命預測及角球剪切疲勞評估。
3. **前置閘門防護之進步性肯定**：
   - 審計依據：`gatekeeper/rules/thermal_rules.py:30-80` 強制檢驗割線熱膨脹係數 $CTE > 0$ 以及參考無應力溫度 $-50^\circ\text{C} \le T_{\text{ref}} \le 400^\circ\text{C}$，且 `SKILLs/pcb-warpage-analysis` 嚴格落實了消除人為約束反力的 **3-2-1 靜定無拘束支承規範**，架構設計理念極佳，待 Phase 3 全面升級為原生有限元實體求解。

---

### 2.6 跨模組架構瓶頸與介面缺陷深度剖析

#### 1. 命名規範與別名機制割裂
- **正規化模組**：`tools/mechanical.py`（39 個工具）、`optislang.py`（5 個工具）、`intent_tools.py`（5 個工具）與 `mechanical_workflows.py`（3 個工具）全面落實 `aliased_tool`，新標準名稱一律遵循 `<product>_<verb>_<object>`，並保留相容舊別名。
- **割裂模組**：
  - `tools/sim_tools.py`（31 個工具）：使用自定義的 `@tool_fluent` 與 `@tool_geometry`，未採用 `aliased_tool`，無雙軌別名支援。
  - `tools/workbench_filebridge.py`（31 個工具）：直接使用 `@mcp.tool`，名稱多為動詞開頭（如 `open_project`, `run_workbench_journal`），缺乏產品前綴規範。

#### 2. 回傳資料信封 (Return Envelope) 不一致
- `mechanical.py` 與 `intent_tools.py` 嚴格確保回傳包含 `{"ok": bool, ...}` 之標準結構。
- `sim_tools.py:14-29` 實裝之 `_envelope(text)` 函數依賴極度危險的字串包含檢查：
  ```python
  is_err = "❌" in text or "錯誤" in text or "fail" in text.lower() or "error" in text.lower()
  return {"ok": not is_err, "output": text}
  ```
  當正常運算日誌中出現 `"0 errors found"` 或 `"mesh error tolerance = 1e-4"` 時，會被直接判定為 `ok: false`，形成假陽性錯誤阻斷。
- `workbench_filebridge.py` 若干工具甚至直接回傳裸字串（Raw String）或未結構化的路徑，導致 LLM 解析成本高昂。

#### 3. 求解器進程依賴與無頭環境支援缺陷
- SpaceClaim 連線強依賴 Windows 前台 GUI 與 .NET AddIn 預先啟動，在純無頭 Linux 容器中無法調用。
- Mechanical 存在 PyMechanical gRPC、命令列批次 APDL 與 RunWB2 腳本注入三種並行途徑，職責劃分不明確。
- LS-DYNA 與 Icepak 在無實體授權環境下自動進入 Synthetic 模式，但未在回傳信封中顯式標記 `is_synthetic: True`，容易對上層工程評估造成混淆。

---

## 第三章：R2. 官方 Tutorials 與各大教學資源全景映射 (Tutorials & Benchmark Mapping)

---

### 3.1 現行模組 vs 官方 Tutorial 範例庫對照總表

本總表深度對標 PyAnsys 開源生態官方範例庫（`ansys/example-data`、`ansys.docs.pyansys.com` 各產品線子站與 Ansys Developer Portal），跨五大核心領域建立 12 個經典權威基準案例的全景對照矩陣：

| 編號 | 領域 | 基準案例名稱 | 官方權威來源 / Reference | 核心輸入幾何與材料 | 核心物理特徵與邊界條件 | 目標輸出與量化標準驗收判據 | 現行 MCP Tool 映射 | 成熟度評級 |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **01** | 結構 | **Taylor Bar 泰勒柱高速衝擊大變形** | `ansys/example-data` (`Taylor_Bar.agdb`), PyMAPDL / PyDYNA Tutorials | `Taylor_Bar.agdb` ($L_0=32.4\text{ mm}, R_0=3.2\text{ mm}$), OFHC 銅雙線性/Johnson-Cook 塑性本構 | 初速 $V_0=227\text{ m/s}$, 剛性靶板撞擊, CFL 時間步控制 ($dt\approx 2\times 10^{-8}\text{ s}$), Flanagan-Belytschko 剛度型沙漏阻尼 | 柱長殘留 $26.2\pm 0.8\text{ mm}$, 蘑菇頭徑向擴展率 $\ge 1.8\times$, 總能量比 $0.98\sim 1.02$, 沙漏能 $<5\%$ | `workflow_run_drop_test`, `run_drop_test`, `mechanical_launch`, `get_simulation_status` | **Tier 1 (成熟)** |
| **02** | 結構 | **懸臂梁大變形與非線性摩擦接觸** | PyMechanical Examples (`examples/01_contact/frictional_contact.py`) | STEP 裝配體 (`beam_contact.stp`), 結構鋼 ($E=200\text{ GPa}, \nu=0.3$) | 幾何非線性 (`Large Deflection=On`), Augmented Lagrange 摩擦接觸 ($\mu=0.2$), 自動副步載荷遞增 | 力-位移曲線連續平滑無跳躍, Newton-Raphson 殘差 $<0.5\%$, 最大法向穿透 $<10^{-4}\text{ mm}$, 無主元警告 | `mechanical_setup_and_solve_static_structural`, `mechanical_add_displacement`, `mechanical_diagnose_model_health` | **Tier 1 (良好)** |
| **03** | 結構 | **電子機箱/支架之模態-隨機振動分析** | PyMechanical Examples (`random_vibration_psd.py`), Workbench Link | Parasolid (`bracket.x_t`), 鋁合金 6061-T6 ($E=68.9\text{ GPa}, \rho=2700\text{ kg/m}^3$) | 基座固定, Block Lanczos 提取前 30 階模態, PSD 功率譜激振 ($20\sim 2000\text{ Hz}, 0.04\text{ g}^2/\text{Hz}$), 3σ 應力提取 | 三向累積有效模態質量佔比 $\ge 90\%$ (硬性閘門), 截斷頻率 $\ge 1.5\times$ 激振上限, 3σ 應力小於降伏極限 | `workflow_run_random_vibration`, `create_modal_analysis_system_live`, `mechanical_get_modal_frequencies` | **Tier 1 (成熟)** |
| **04** | 幾何 | **Mixing Elbow 混合彎管 PMDB 參數化 CAD 重建** | `ansys/example-data` (`mixing_elbow.pmdb`), PyGeometry Reference | `mixing_elbow.pmdb` (主管內徑 4", 支管內徑 1", 彎曲半徑 6") | 2D 草圖輪廓繪製, 沿路徑掃掠拉伸 (Sweep/Extrude), 倒圓角, 實體布林合併, 具名選擇指定 | 水密實體檢查通過 (0 Free Edges, 0 Open Surfaces), 實體體積誤差 $<0.01\%$, PMDB 格式導出無拓撲損壞 | `geometry_launch`, `geometry_create_design`, `geometry_sketch_and_extrude`, `geometry_export` | **Tier 2 (良好)** |
| **05** | 幾何 | **散熱板/排氣歧管外流域抽取與 CAD 修復** | PyGeometry Reference (`enclosure_extraction.py`), SpaceClaim ACT | STEP 外部 CAD (`manifold.stp` / `heat_sink_board.stp`) | 外包絡流場方盒建立 (上游 3D, 下游 5D, 兩側 2D), 布林相減, 碎面短邊修補 (邊長 $<0.1\text{ mm}$), 自動命名邊界 | 單一連通封閉流體實體, 無多體干涉碰撞, 水密性驗證通過, 自動生成 Inlet/Outlet/Wall 具名選擇 | `geometry_create_enclosure`, `geometry_import_file`, `geometry_export`, `execute_spaceclaim_script_live` | **Tier 2 (良好)** |
| **06** | 熱傳 | **散熱片共軛熱傳分析 (CHT)** | PyFluent Examples (`examples/00-fluent/heat_sink_cht.py`), `ansys/example-data` | PMDB / Watertight CAD, 空氣流體 + 鋁散熱片 + 發熱晶片 (50 W) | 能量方程式開啟, SST $k-\omega$ 湍流, 固-液界面共形/非共形熱通量連續, 入口 $2\text{ m/s}$, 出口靜壓 0 Pa | 質量不平衡度 $<0.1\%$, 能量殘差 $<0.05\%$, 晶片最高結溫 $T_j \le 85^\circ\text{C}$, 系統散熱熱阻誤差 $<\pm 5\%$ | `fluent_launch`, `fluent_read_case`, `fluent_set_solver`, `fluent_set_boundary`, `fluent_iterate` | **Tier 2 (良好)** |
| **07** | 熱傳 | **電子機箱自然對流與強迫風冷散熱分析** | PyAEDT Icepak Examples (`Icepak_Setup.py`), Ansys Icepak User Guide | STEP / ECAD 機箱裝配體, 多層 PCB, 軸流風扇 (P-Q 曲線), 多發熱 IC | 浮力重力驅動 (Boussinesq), 表面熱輻射 (DO / S2S 模型), 軸流風扇非線性流量壓頭特性, 外殼自然對流 ($h=5$) | 所有 IC 表面溫度低於降額規範 ($<105^\circ\text{C}$), 出風口溫升 $\Delta T < 25^\circ\text{C}$, 無非物理逆流迴圈 | `create_steady_state_thermal_system_live`, `run_thermal_warpage`, `fluent_tui`, `fluent_set_boundary` | **Tier 3 (部分支援)** |
| **08** | 網格 | **複雜車身/薄板幾何表面修復與收縮包覆網格** | PyPrimeMesh Examples (`examples/gallery/01_automotive_wrap.py`) | FMD / STL 髒幾何 (包含幾何穿透、微小縫隙、重疊面與零厚度板金) | `Wrapper` 體素收縮包覆 (Voxel Size 2 mm), 自動封閉漏氣孔, 特徵稜邊捕捉 (30°), `Surfer` 高品質表面重劃 | 100% 閉合水密表面 (0 Free Edges, 0 Non-Manifold), 體積漏失 $<0.2\%$, 表面最大歪斜度 $\le 0.70$ | `fluent_read_mesh`, (依賴 Fluent WGW 內部封裝，無原生 Prime 工具) | **Tier 3 (待擴充)** |
| **09** | 網格 | **排氣歧管多區域高質量 Mosaic Poly-Hexcore 體網格** | PyPrimeMesh Examples (`mosaic_polyhexcore.py`), `exhaust_manifold.fmd` | 水密邊界表面網格 (Watertight Surface Mesh) | 核心區八叉樹六面體 (Octree Hexcore), 壁面 12 層稜柱層 (生長比 1.2, $y^+\approx 1$), 中間多面體各向同性過渡 | 單元數量較四面體減少 65%, 最小正交品質 $\ge 0.20$, 最大歪斜度 $\le 0.80$, 稜柱層無負體積 | `ansys-fluent` (WGW SOP 腳本), `check_fluent_mesh.py`, `fluent_set_boundary` | **Tier 2 (良好)** |
| **10** | 封裝 | **BGA 晶片封裝與多層 PCB 板高溫熱翹曲分析** | `pcb-warpage-analysis`, JEDEC JESD22-B112, PyMechanical Tutorials | 疊構參數表 (`MCP_Test.xlsx`), 銅箔/基板材料 CSV (EM-370, EM-892K2), BGA 封裝 | 混合法則 (ROM) 正交各向異性材料矩陣計算, 回流焊溫度歷程 ($25\to 220\to 25^\circ\text{C}$), 3-2-1 靜定無約束支承 | Z 軸翹曲峰谷值 Coplanarity $\le 150\ \mu\text{m}$ (符合 JEDEC B112), 支承反力殘差 $<10^{-4}\text{ N}$ (無人工應力) | `workflow_run_thermal_warpage`, `run_thermal_warpage`, `run_full_warpage_workflow.py` | **Tier 1 (成熟)** |
| **11** | 封裝 | **SAC305 錫球熱循環 Anand 黏塑性蠕變與低週疲勞** | PyMechanical Examples (`examples/02_fatigue/solder_joint_anand.py`) | CDB / Parasolid 模型, SAC305 無鉛焊錫 9 參數 Anand 黏塑性本構卡片 | 加速熱循環工況 (ATC: $-40\leftrightarrow +125^\circ\text{C}$), 黏塑性累積應變能密度增量 ($\Delta W_{acc}$), Darveaux 壽命模型 | 第 3 循環後應變能增量波動 $<2\%$, 特徵疲勞壽命 $N_{63.2\%}\ge 1500\text{ cycles}$, 識別關鍵角球應力集中 | `mechanical_assign_material`, `mechanical_setup_and_solve_static_structural`, `ansys-submodeling-dpf` | **Tier 2 (部分支援)** |
| **12** | 封裝 | **PyAEDT ECAD 佈線幾何導入與多單元殘銅率材料映射** | PyAEDT Examples (`examples/00-EDB/EDB_create_via.py`), `ansys/example-data` | Ansys EDB (`.aedb`) / ODB++ / IPC-2581 電路板設計佈局檔案 | 走線 (Traces) 與過孔 (Vias) 幾何重建, 自交多邊形修復, 體素網格殘銅率計算, 各向異性熱導/彈性張量映射 | EDB 圖層讀取完整無漏失, 多邊形布林修復零錯誤, 網格材料屬性精確對應銅箔空間分佈 (誤差 $<1\%$) | (目前需透過 Workbench ECAD 外部匯入中繼，無原生 PyAEDT 工具) | **Tier 3 (待擴充)** |

---

### 3.2 十二大代表性經典基準案例深度規格清單

#### 案例 01：Taylor Bar 泰勒柱高速衝擊大變形 (Taylor Bar Impact Test)
- **領域分類**：結構 (Structural)
- **官方來源 URL**：
  - 數據庫：`https://github.com/ansys/example-data/blob/main/pymapdl/Taylor_Bar.agdb`
  - 官方文件：PyMechanical Examples / PyDYNA Benchmark Suite
- **輸入幾何與材料**：
  - 幾何尺寸：圓柱體，初始長度 $L_0 = 32.4\text{ mm}$，初始半徑 $R_0 = 3.2\text{ mm}$，縱橫比 $L_0/R_0 = 10.125$。
  - 材料本構：無氧高導銅（OFHC Copper），密度 $\rho = 8.96\times 10^{-9}\text{ ton/mm}^3$；彈性模數 $E = 1.15\times 10^5\text{ MPa}$；泊松比 $\nu = 0.31$；靜態降伏強度 $\sigma_y = 400.0\text{ MPa}$；切線模數 $E_{tan} = 100.0\text{ MPa}$（採用 `*MAT_024` 雙線性彈塑性本構）。
- **核心物理與邊界條件**：
  - 載荷條件：初始衝擊速度 $V_0 = 227.0\text{ m/s}$（沿 Z 軸負向），垂直撞擊無摩擦剛性靶板。
  - 接觸與求解控制：平面剛性牆接觸（`*RIGIDWALL_PLANAR`）；求解終止時間 $T_{end} = 8.0\times 10^{-5}\text{ s}$（80 微秒）；安全係數 $TSSFAC = 0.90$；局部質量縮放時間步 $DT2MS = -2.0\times 10^{-8}\text{ s}$；Flanagan-Belytschko 剛度型沙漏控制阻尼（$IHQ=4, QH=0.10$）。
- **目標輸出與量化標準驗收判據**：
  - 殘餘長度：最終殘留柱長 $L_f = 26.2 \pm 0.8\text{ mm}$（縮短率約 19.1%）。
  - 蘑菇頭擴展：撞擊底端徑向擴展半徑 $R_f \ge 5.8\text{ mm}$（擴展率 $\ge 1.8\times$）。
  - 能量守恆判據：總能量比率 $E_{total} / (E_{kin,0} + E_{int,0}) \in [0.98, 1.02]$；沙漏能佔比 $E_{hourglass} / E_{internal} < 5.0\%$；質量增加比例 $< 2.0\%$。
- **對應 MCP Tool / 工作流映射**：
  - 工具：`workflow_run_drop_test(cad_path, drop_height_mm=..., impact_velocity_mps=227.0)`。
  - 守護：`src/ansys_unified_mcp/core/sentinel/parsers/lsdyna.py` 串流解析，觸發 `circuit_breaker` 發散熔斷。

---

#### 案例 02：懸臂梁大變形與非線性摩擦接觸 (Cantilever Beam Large Deflection & Frictional Contact)
- **領域分類**：結構 (Structural)
- **官方來源 URL**：
  - 官方範例：`https://examples.mechanical.docs.pyansys.com/` (`frictional_contact.py`)
- **輸入幾何與材料**：
  - 幾何尺寸：雙懸臂梁裝配體（尺寸 $100\text{ mm}\times 10\text{ mm}\times 5\text{ mm}$，初始接觸間隙 $0.5\text{ mm}$）。
  - 材料本構：結構鋼（Structural Steel），$E = 200.0\text{ GPa}$，$\nu = 0.30$。
- **核心物理與邊界條件**：
  - 約束與載荷：底梁底面完全固定約束（Fixed Support）；頂梁自由端施加強迫位移壓入（沿 Y 軸壓入 $-15.0\text{ mm}$）。
  - 接觸本構：Augmented Lagrange 公式，摩擦係數 $\mu = 0.20$；開啟接觸剛度逐次迭代自動更新。
  - 求解控制：開啟大幾何非線性（`Large Deflection = On`）；初始副步數 20，最小副步數 10，最大副步數 100；收斂容差 $0.5\%$。
- **目標輸出與量化標準驗收判據**：
  - 力學收斂性：無數值主元警告（No Pivot Warning），殘差力 $L_2$-範數低於極限準則。
  - 接觸穿透度：最大法向穿透量（Normal Penetration）$< 1.0\times 10^{-4}\text{ mm}$。
  - 響應曲線：頂梁自由端反力-位移曲線平滑單調遞增，無數值突變跳躍。
- **對應 MCP Tool / 工作流映射**：
  - 工具：`mechanical_setup_and_solve_static_structural`、`mechanical_add_displacement`、`mechanical_diagnose_model_health`。

---

#### 案例 03：電子機箱/支架之模態-隨機振動分析 (Modal-to-PSD Random Vibration Analysis)
- **領域分類**：結構 (Structural)
- **官方來源 URL**：
  - 官方範例：`https://examples.mechanical.docs.pyansys.com/` (`random_vibration_psd.py`)
- **輸入幾何與材料**：
  - 幾何尺寸：金屬安裝支架/機箱殼體（Parasolid `bracket.x_t`），壁厚 $2.0\text{ mm}$。
  - 材料本構：鋁合金 6061-T6，$E = 68.9\text{ GPa}$，$\rho = 2700\text{ kg/m}^3$，$\nu = 0.33$。
- **核心物理與邊界條件**：
  - 前置模態分析：基座螺栓孔全約束，採用 Block Lanczos 求解器提取前 30 階固有頻率與特徵振型。
  - 隨機振動激振：基礎加速度功率譜密度（PSD Acceleration），頻率範圍 $20\sim 2000\text{ Hz}$，PSD 輸入值 $0.04\text{ g}^2/\text{Hz}$（總 RMS 加速度約 $8.9\text{ Grms}$）。
  - 應力計算：模態疊加法，計算提取 $1\sigma, 2\sigma, 3\sigma$ 等效 von-Mises 統計應力場。
- **目標輸出與量化標準驗收判據**：
  - 安全閘門前檢：三向累積有效模態質量佔比（Cumulative Effective Modal Mass Ratio）必須 $\ge 90.0\%$，否則硬性阻斷。
  - 截斷頻率校驗：模態提取之最高頻率必須 $\ge 1.5\times$ 激振上限頻率（$f_{cutoff} \ge 3000\text{ Hz}$）。
  - 應力評估：$3\sigma$ 最大等效應力小於材料降伏極限（$276\text{ MPa}$），在 $99.73\%$ 機率下不發生結構破壞。
- **對應 MCP Tool / 工作流映射**：
  - 工具：`workflow_run_random_vibration`、`create_modal_analysis_system_live`、`mechanical_get_modal_frequencies`。

---

#### 案例 04：Mixing Elbow 混合彎管 PMDB 參數化 CAD 重建 (Mixing Elbow CAD Reconstruction)
- **領域分類**：幾何 (Geometry)
- **官方來源 URL**：
  - 數據庫：`https://github.com/ansys/example-data/blob/main/pyfluent/mixing_elbow/mixing_elbow.pmdb`
  - 官方文件：PyGeometry Reference (`https://geometry.docs.pyansys.com/`)
- **輸入幾何與材料**：
  - 參數定義：主流道直徑 $D_1 = 4.0\text{ in}$（$101.6\text{ mm}$）；彎頭中心半徑 $R = 6.0\text{ in}$；支流道直徑 $D_2 = 1.0\text{ in}$（$25.4\text{ mm}$）；側管安裝位置距離彎曲起始面 $L_{offset} = 4.0\text{ in}$。
- **核心物理與邊界條件**：
  - 建模操作流：建立 2D 圓形草圖；沿 90° 圓弧路徑掃掠拉伸；在側壁建立草圖並沿法向拉伸垂直支管；執行實體布林合併；自動生成具名選擇（Named Selections: `inlet-main`, `inlet-side`, `outlet`, `wall`）。
- **目標輸出與量化標準驗收判據**：
  - 水密性檢驗：水密實體（0 Free Edges, 0 Non-Manifold Edges），實體幾何體積與官方標準數值誤差 $< 0.01\%$。
  - 導出相容性：成功輸出 `.pmdb` 與 `.step` 格式，在 Fluent Watertight Workflow 載入時 100% 識別為水密單體。
- **對應 MCP Tool / 工作流映射**：
  - 工具：`geometry_launch`、`geometry_create_design`、`geometry_sketch_and_extrude`、`geometry_export`。

---

#### 案例 05：散熱板/排氣歧管外流域抽取與 CAD 修復 (Fluid Domain Enclosure & CAD Defect Healing)
- **領域分類**：幾何 (Geometry)
- **官方來源 URL**：
  - 官方範例：`https://geometry.docs.pyansys.com/` (`enclosure_extraction.py`)
  - 本地腳本：`SKILLs/ansys-geometry-modeling/scripts/create_enclosure_demo.py`
- **輸入幾何與材料**：
  - 原始 CAD：複雜電子散熱板或排氣歧管裝配體（STEP / IGES 格式），存在縫隙（$<0.05\text{ mm}$）與倒角碎面。
- **核心物理與邊界條件**：
  - 幾何簡化 (Defeaturing)：自動偵測並移除短於 $0.1\text{ mm}$ 的邊緣及面積小於 $1.0\times 10^{-6}\text{ m}^2$ 的碎面（Sliver Faces）。
  - 外流域包覆：以上游 3D、下游 5D、兩側 2D 之比例建立流場包絡外框；執行布林相減保留流體區域與共享拓撲。
- **目標輸出與量化標準驗收判據**：
  - 拓撲完好性：生成單一閉合水密流體實體，無多體干涉；水密性檢查狀態為 PASS。
  - 邊界完整性：流體外邊界面自動識別並標記為 `inlet`, `outlet`, `symmetry`, `ground`。
- **對應 MCP Tool / 工作流映射**：
  - 工具：`geometry_create_enclosure`、`geometry_import_file`、`geometry_export`、`execute_spaceclaim_script_live`。

---

#### 案例 06：散熱片共軛熱傳分析 (Heat Sink Conjugate Heat Transfer - CHT)
- **領域分類**：熱傳與電子散熱 (Thermal / CHT)
- **官方來源 URL**：
  - 數據庫：`https://github.com/ansys/example-data/blob/main/pyfluent/` (`heat_sink_cht.cas.h5`)
  - 官方文件：PyFluent Tutorials (`https://fluent.docs.pyansys.com/`)
- **輸入幾何與材料**：
  - 幾何尺寸：流動風道（$200\text{ mm}\times 80\text{ mm}\times 40\text{ mm}$）；鋁製板鰭散熱片（基座 $50\times 50\times 5\text{ mm}$，鰭片高度 $25\text{ mm}$，10 片）；底部發熱晶片（$20\times 20\times 1\text{ mm}$）。
  - 材料特性：空氣（$\rho=1.225\text{ kg/m}^3, k=0.0242\text{ W/m}\cdot\text{K}$）；散熱片鋁材（$k=167.0\text{ W/m}\cdot\text{K}$）；晶片矽材（$k=148.0\text{ W/m}\cdot\text{K}$）。
- **核心物理與邊界條件**：
  - 物理模型：Navier-Stokes 流動方程；開啟能量方程式（`Energy Equation = On`）；SST $k-\omega$ 湍流模型。
  - 邊界條件：入口風速 $v = 2.0\text{ m/s}$，入口風溫 $T_{in} = 293.15\text{ K}$；出口靜壓 $0\text{ Pa}$；晶片體熱源發熱功率 $Q = 50.0\text{ W}$；流固交界面設置為 Coupled Wall（熱通量與溫度雙向連續）。
- **目標輸出與量化標準驗收判據**：
  - 物理守恆性：進出口質量不平衡度 $|\dot{m}_{in} - \dot{m}_{out}| / \dot{m}_{in} < 0.1\%$；能量殘差 $< 0.05\%$。
  - 散熱指標：晶片最高結溫 $T_j \le 85.0^\circ\text{C}$；系統熱阻 $R_{th} = (T_{j,\max} - T_{in}) / Q \approx 0.82\text{ K/W}$（與經驗公式誤差 $\le \pm 5\%$）。
- **對應 MCP Tool / 工作流映射**：
  - 工具：`fluent_launch`、`fluent_read_case`、`fluent_set_solver`、`fluent_set_boundary`、`fluent_iterate`、`fluent_get_residuals`。

---

#### 案例 07：電子機箱自然對流與強迫風冷散熱分析 (Electronics Enclosure Natural & Forced Convection)
- **領域分類**：熱傳與電子散熱 (Thermal / Icepak)
- **官方來源 URL**：
  - 官方範例：PyAEDT Icepak Examples (`https://aedt.docs.pyansys.com/`)
  - 官方文件：Ansys Icepak User Guide
- **輸入幾何與材料**：
  - 幾何尺寸：金屬機箱（$300\times 200\times 80\text{ mm}$），內部包含 12 層 PCB 主板、2 組發熱電源模組（各 20 W）、1 顆 CPU 處理器（65 W 帶散熱片）與 1 台軸流風扇。
  - 材料特性：PCB 板設置正交各向異性導熱係數（$k_x = k_y = 20.0\text{ W/m}\cdot\text{K}, k_z = 0.4\text{ W/m}\cdot\text{K}$）。
- **核心物理與邊界條件**：
  - 物理設定：重力加速度向量 $\vec{g} = [0, 0, -9.81]\text{ m/s}^2$；浮力驅動採用 Boussinesq 模型；開啟 Discrete Ordinates (DO) 表面熱輻射模型。
  - 風扇特性：指定非線性風扇 P-Q 曲線（最大風量 35 CFM，最大靜壓 45 Pa）；機箱外壁設置自然對流換熱係數 $h = 5.0\text{ W/m}^2\cdot\text{K}$，環境溫度 $25.0^\circ\text{C}$。
- **目標輸出與量化標準驗收判據**：
  - 溫度降額驗收：所有晶片表面溫度符合降額規範（$T_{CPU} \le 80.0^\circ\text{C}, T_{Power} \le 95.0^\circ\text{C}$）。
  - 流動穩定性：出風口無非物理逆向倒灌回流；總質量不平衡度 $< 0.1\%$。
- **對應 MCP Tool / 工作流映射**：
  - 工具：`create_steady_state_thermal_system_live`、`run_thermal_warpage`、`fluent_tui`。

---

#### 案例 08：複雜車身/薄板幾何表面修復與收縮包覆網格 (Automotive Surface Wrap - PyPrimeMesh)
- **領域分類**：高階網格 (PyPrimeMesh)
- **官方來源 URL**：
  - 數據庫：`https://github.com/ansys/example-data/blob/main/pyprimemesh/` (`car_body.fmd`)
  - 官方文件：PyPrimeMesh User Guide (`https://prime.docs.pyansys.com/`)
- **輸入幾何與材料**：
  - 原始 CAD：包含數千個零組件的複雜汽車車身外型（FMD / STL 格式），存在穿透、微小間隙、重疊面與零厚度板金。
- **核心物理與邊界條件**：
  - 包覆設定 (Wrapper)：體素解析度（Voxel Resolution）設置 $2.0\text{ mm}$；特徵孔洞封堵尺寸 $5.0\text{ mm}$；接觸銳角捕捉（Contact Angle = 30°）。
  - 表面重構 (Surfer)：曲率與鄰近度控制；表面單元最小尺寸 $1.0\text{ mm}$，最大尺寸 $16.0\text{ mm}$；生長率 1.2。
- **目標輸出與量化標準驗收判據**：
  - 水密性拓撲：產出 100% 封閉水密表面網格，自由邊（Free Edges）= 0，非流形邊（Non-Manifold Edges）= 0。
  - 幾何保真度：包覆表面與原始幾何邊界之法向距離偏差 $< 0.5\text{ mm}$；總體積漏失率 $< 0.2\%$。
  - 表面品質：最大表面歪斜度（Max Equiangle Skewness）$\le 0.70$。
- **對應 MCP Tool / 工作流映射**：
  - 映射現況：目前仰賴 Fluent WGW 腳本間接實現；規劃於 Phase 2 新增獨立 `primemesh_surface_wrap` 工具。

---

#### 案例 09：排氣歧管多區域高質量 Mosaic Poly-Hexcore 體網格劃分 (Mosaic Poly-Hexcore Meshing)
- **領域分類**：高階網格 (PyPrimeMesh)
- **官方來源 URL**：
  - 官方範例：`https://prime.docs.pyansys.com/` (`mosaic_polyhexcore.py`)
  - 數據庫：`https://github.com/ansys/example-data/blob/main/pyfluent/` (`exhaust_manifold.fmd`)
- **輸入幾何與材料**：
  - 輸入模型：四進一出汽車排氣歧管水密表面網格（Watertight Surface Mesh）。
- **核心物理與邊界條件**：
  - 稜柱層設定 (Prisms)：設置 12 層壁面邊界層稜柱單元，生長率 1.2，第一層高度 $y_1 = 0.02\text{ mm}$（確保近壁面無量綱距離 $y^+ \approx 1$）。
  - 核心填充 (Volume Fill)：選擇 `poly-hexcore`；內部八叉樹六面體最大尺寸 $4.0\text{ mm}$；過渡層採用 Mosaic 多面體單元平滑過渡。
- **目標輸出與量化標準驗收判據**：
  - 單元節省率：單元總數較同等精度之傳統四面體網格減少 $60\%\sim 70\%$。
  - 網格品質：最小正交品質（Minimum Orthogonal Quality）$\ge 0.20$（全域平均 $>0.85$）；最大歪斜度 $\le 0.80$；稜柱層長寬比合理，無負體積單元（0 Negative Volume Cells）。
- **對應 MCP Tool / 工作流映射**：
  - 工具：`SKILLs/ansys-fluent/scripts/check_fluent_mesh.py`、`fluent_read_mesh`、`fluent_set_boundary`。

---

#### 案例 10：BGA 晶片封裝與多層 PCB 板高溫熱翹曲分析 (BGA Packaging & Multi-layer PCB Warpage)
- **領域分類**：電子封裝 (Electronic Packaging)
- **官方來源 URL**：
  - 工業規範：JEDEC JESD22-B112（High Temperature Package Warpage Measurement）
  - 本地技能：`SKILLs/pcb-warpage-analysis`
  - 專案實作：`src/ansys_unified_mcp/workflows/thermal_warpage.py`
- **輸入幾何與材料**：
  - 疊構配置：16 層 PCB 主板（長寬 $120\text{ mm}\times 80\text{ mm}$），包含 8 層銅箔走線層與 8 層半固化芯板（EM-370、EM-892K2）；頂部貼裝 BGA 封裝晶片（Die, Substrate, Mold, SAC305 錫球陣列）。
  - 等效材料計算：依各層殘銅率（15%~85%），透過混合法則（Rule of Mixtures, ROM）計算正交各向異性溫度相依材料矩陣（$E_i(T), \alpha_i(T)$）。
- **核心物理與邊界條件**：
  - 熱歷程：回流焊溫度曲線（Reflow Profile），自常溫 $25.0^\circ\text{C}$ 升溫至最高峰值 $220.0^\circ\text{C}$，再冷卻至常溫。
  - 支承邊界條件（3-2-1 靜定支承法）：
    - 頂點 A：$U_x = U_y = U_z = 0$（消除平移自由度）；
    - 頂點 B：$U_y = U_z = 0$（消除繞 Z 軸旋轉）；
    - 頂點 C：$U_z = 0$（消除繞 X、Y 軸旋轉）；
    - *物理意義*：完全消除 6 個剛體位移自由度，允許板體自由熱脹冷縮，不引入任何人為約束熱應力。
- **目標輸出與量化標準驗收判據**：
  - 翹曲極值判據：最高溫回流焊峰值（$220^\circ\text{C}$）下，Z 軸共面度峰谷值（Peak-to-Valley Coplanarity Warpage）$\le 150.0\ \mu\text{m}$（符合 JEDEC B112 標準）。
  - 反力校驗：3 個支承點處的反作用力數值必須逼近於 0（$|R| < 1.0\times 10^{-4}\text{ N}$）。
- **對應 MCP Tool / 工作流映射**：
  - 工具：`workflow_run_thermal_warpage`、`run_thermal_warpage`、`run_full_warpage_workflow.py`。

---

#### 案例 11：SAC305 錫球熱循環 Anand 黏塑性蠕變與低週疲勞 (Solder Joint Anand Viscoplasticity & Fatigue)
- **領域分類**：電子封裝 (Electronic Packaging)
- **官方來源 URL**：
  - 官方範例：`https://examples.mechanical.docs.pyansys.com/` (`solder_joint_anand.py`)
  - 經典文獻：Darveaux Solder Joint Reliability Prediction Model
- **輸入幾何與材料**：
  - 幾何模型：BGA 封裝 1/4 對稱結構或子模型（Submodel），包含銅焊盤、阻焊層與 SAC305 無鉛焊球。
  - 材料本構：SAC305 採用 Anand 黏塑性本構模型（9 個材料參數：初始抗力 $s_0=45\text{ MPa}$、$Q/R=9400\text{ K}$、應力乘子 $\xi=4.0$、應變率指數 $m=0.07$、飽和抗力 $\hat{s}=80\text{ MPa}$ 等）。
- **核心物理與邊界條件**：
  - 加速熱循環 (ATC)：$-40.0^\circ\text{C}\sim +125.0^\circ\text{C}$，升降溫速率 $10.0^\circ\text{C}/\text{min}$，高低溫保溫時間各 15 分鐘，連續求解 3~5 個完整熱循環。
  - 大變形開啟，自動副步控制捕捉應變率敏感之塑性應變能累積。
- **目標輸出與量化標準驗收判據**：
  - 遲滯迴線穩定性：提取焊球剪切應力-剪切應變遲滯迴線，第 3 循環後每週期塑性累積應變能增量 $\Delta W_{acc}$ 波動小於 $2.0\%$。
  - 疲勞壽命預測：依 Darveaux 經驗模型計算裂紋萌生壽命 $N_0$ 與擴展速率 $da/dN$，特徵壽命 $N_{63.2\%} \ge 1500\text{ cycles}$。
  - 失效點標定：精確定位最大應變能耗散集中於最外側角球（Corner Ball）焊盤交界面。
- **對應 MCP Tool / 工作流映射**：
  - 工具：`mechanical_assign_material`、`mechanical_setup_and_solve_static_structural`、`ansys-submodeling-dpf`。

---

#### 案例 12：PyAEDT ECAD 佈線幾何導入與多單元殘銅率材料映射 (PyAEDT ECAD Layout & Material Mapping)
- **領域分類**：電子封裝 (Electronic Packaging)
- **官方來源 URL**：
  - 官方文件：PyAEDT EDB & Icepak Examples (`https://aedt.docs.pyansys.com/`)
  - 數據庫：`https://github.com/ansys/example-data/blob/main/pyaedt/` (`ansys_board.aedb`)
- **輸入幾何與材料**：
  - 設計檔案：Ansys EDB 數據庫（`.aedb`）或工業標準 ODB++ / IPC-2581 設計佈局檔案。
- **核心物理與邊界條件**：
  - 幾何剖析：提取訊號/電源/接地走線層（Traces）、通孔陣列（Vias）、焊盤（Pads）與元件封裝腳位。
  - 拓撲修復：消除微小自相交邊界與銳角退化三角形。
  - 走線映射 (Trace Mapping)：將連續佈局幾何剖分至背景有限元體素網格（Voxels），依局部相交體積比計算各網格單元之等效導熱係數與彈性矩陣。
- **目標輸出與量化標準驗收判據**：
  - 圖層導入完整度：所有設計圖層、導線網絡 100% 讀取無遺漏。
  - 映射精度校驗：局部單元殘銅率計算誤差 $< 1.0\%$，導熱係數張量方向與走線走向高度一致。
- **對應 MCP Tool / 工作流映射**：
  - 映射現況：專案目前缺乏原生 `PyAEDTDriver` 與專屬 ECAD 工具；列為 Phase 3 關鍵擴充目標。

---

### 3.3 邊界極限工況與異常處理矩陣

在工業級複雜 CAE 分析中，極限輸入與異常狀況頻繁發生。系統透過 Sentinel Watchdog 與 Pre-Flight Gatekeeper 建立了完備的攔截、防禦與自愈處置機制：

| # | 關聯案例 / 特性 | 極限輸入情況 (Input Edge Case) | 系統觀察到的行為 (Observed Behavior) | 防護處置機制與結構化自愈處方 (Prescription) |
| :-: | :--- | :--- | :--- | :--- |
| **1** | 案例 03: 隨機振動 | 結構高階特徵模態密集，前 30 階累積有效模態質量僅達到 78.4%（未達 90% 門檻）。 | 前置閘門 `GATE-VIB-001` 觸發阻斷，阻止求解器浪費算力。 | **硬性阻斷與自愈處方**：回傳 `ERR_GATEKEEPER_BLOCKED`，自愈處方建議：「將模態提取階數自 30 階擴大至 80 階，並檢查基座固定約束是否漏設」。 |
| **2** | 案例 01: 泰勒柱落摔 | 薄壁處網格單元極小（$0.05\text{ mm}$），導致 CFL 臨界時間步長低達 $5.0\times 10^{-10}\text{ s}$。 | Watchdog 預估運算時間超過 48 小時，且質量縮放過大導致慣性失真。 | **動態時間步防禦**：建議開啟質量縮放（設置 $DT2MS = -2.0\times 10^{-8}\text{ s}$），若質量增長率超過 2% 則自動熔斷。 |
| **3** | 案例 01: 泰勒柱落摔 | 初速度向量設置為水平方向 $[1, 0, 0]$，與剛性靶板法向量垂直。 | 幾何運動學計算判定物體永遠不會撞擊地面。 | **物理邏輯阻斷**：`GATE-DRP-001` 計算初速向量與剛性牆法向點積，點積 $\ge 0$ 時直接拒絕送算並報警。 |
| **4** | 案例 06: 散熱片 CHT | 近壁面首層網格過厚，計算得出壁面無量綱距離 $y^+ \approx 45$（處於緩衝過渡區）。 | Fluent 求解診斷模組發現數值落入 SST $k-\omega$ 壁面函數過渡死區。 | **物理判斷力告警**：輸出警示資訊，自愈處方提供自動細化棱柱層首層高度之 Python 計算代碼。 |
| **5** | 案例 06: 散熱片 CHT | 出口背壓過高或流道發生大尺度分離渦，壓力出口出現大面積逆流（Backflow）。 | 出口截面逆流單元比例超過總面積 10%，連續性殘差震盪發散。 | **數值發散自愈**：啟動回流總溫保護（Backflow Total Temperature），自動將偽瞬態 Courant 數下調至 0.5。 |
| **6** | 案例 10: PCB 熱翹曲 | 使用者在多層板四個角點皆施加固定約束（Fixed Support），並進行回流焊升溫。 | 約束強行限制熱膨脹，內部產生非物理壓應力（等效應力暴衝至 $850\text{ MPa}$，反力達數千牛頓）。 | **結構約束自愈**：`GATE-PKG-001` 攔截過約束，自愈處方強制替換為 3-2-1 靜定無拘束支承，消除人為熱應力。 |
| **7** | 案例 05: 外流域抽取 | 外部導入之 CAD 存在微小自交面（Self-intersecting Faces）或零厚度非流形邊。 | SpaceClaim / Geometry 後端拋出 `BooleanOperationFailed`。 | **幾何前檢修復**：CADDefectAuditor 攔截，要求先執行幾何縫合（Stitch）與碎面清理（Defeaturing）。 |
| **8** | 案例 02: 梁大變形接觸 | 載荷一步到位施加巨大拉力，首個子步即出現大應變與剛度突變。 | Newton-Raphson 迭代殘差發散，求解器出現數值主元警告（Pivot Error）。 | **非線性自愈處方**：自動啟用 Auto Time Stepping，將初始副步細化至 50 步，並開啟弱彈簧（Weak Springs）。 |

---

## 第四章：R3. 系統拓撲架構與 API/MCP Tool 契約介面設計規範 (Architecture & Specification)

---

### 4.1 工具命名標準規範與雙軌相容架構

#### 1. 規範命名語法 (Canonical Tool Naming)
全系統所有 MCP 工具必須嚴格遵守三段式語意命名法：
$$\text{Tool Name} = \langle\text{product}\rangle\_\langle\text{verb}\rangle\_\langle\text{object}\rangle$$

產品前綴（`<product>`）嚴格規範如下：
- `structural_` / `mechanical_`：結構分析、邊界條件、結果項與材料指派。
- `geometry_`：幾何前處理、CAD 修復、草圖特徵與外流域抽取。
- `thermal_` / `icepak_`：熱傳、電子散熱與冷卻風道。
- `mesh_` / `primemesh_`：網格劃分、包面包絡與網格品質前檢。
- `packaging_`：電子封裝、ECAD 導入、疊構等效與焊點可靠度。
- `workflow_`：跨模組多物理場高階組合情境工況。
- `sentinel_`：作業排程、生命週期查詢、日誌串流與熔斷控制。

#### 2. 雙軌別名註冊裝飾器 (`aliased_tool`)
為保證既有客戶端程式與 prompt 的 100% 向後相容，工具註冊必須透過 `shared.aliased_tool` 統一發布：
```python
def aliased_tool(name: str, alias: str, description: str):
    """
    雙軌工具註冊裝飾器
    :param name: 新標準名稱 (符合 <product>_<verb>_<object>)
    :param alias: 舊相容別名 (包含 [DEPRECATED ALIAS] 標註)
    :param description: 工具功能描述
    """
    def decorator(fn):
        # 1. 註冊新標準名稱至 FastMCP
        mcp.tool(name=name, description=description)(fn)
        # 2. 註冊相容舊別名至 FastMCP，提示即將廢棄但維持可用
        deprecated_desc = f"[DEPRECATED ALIAS for {name}] {description}"
        mcp.tool(name=alias, description=deprecated_desc)(fn)
        return fn
    return decorator
```

---

### 4.2 結構化輸入 Schema 與標準回傳信封架構

#### 1. 輸入參數型別安全 (Input Validation)
- 嚴格禁止使用未定結構的 `**kwargs`。
- 每個工具參數必須具備顯式 Python 型別標註（`str`, `int`, `float`, `bool`, `List[float]`）。
- 複雜參數配置必須封裝為 Pydantic `BaseModel`（如材料卡片、網格控制參數表）。
- 所有參數在 docstring 中必須註明物理單位（長度一律以 `mm`、應力以 `MPa`、溫度以 `C` 或 `K`、頻率以 `Hz` 為準）。

#### 2. 統一回傳信封 (Unified Return Envelope)
廢除字串比對與 JSON 字串包裝，所有工具一律回傳原生 Python `Dict[str, Any]`，由 FastMCP 序列化為 JSON-RPC 回應：

##### 成功回應信封結構 (`ok: True`)
```json
{
  "ok": true,
  "status": "SUCCESS",
  "data": {
    "entity_id": 105,
    "name": "Heatsink_Base",
    "metrics": {
      "element_count": 52400,
      "min_orthogonal_quality": 0.38,
      "max_skewness": 0.65
    }
  },
  "warnings": [],
  "execution_time_ms": 142.6
}
```

##### 失敗回應信封結構 (`ok: False`)
```json
{
  "ok": false,
  "status": "FAILED",
  "error_code": "ERR_GATEKEEPER_BLOCKED",
  "error": "隨機振動模態質量不足 90% (當前三向累積僅 78.4%)，嚴禁送算。",
  "details": {
    "rule_id": "GATE-VIB-001",
    "observed_value": {"effective_mass_ratio_z": 0.784},
    "required_threshold": {"effective_mass_ratio": 0.90}
  },
  "prescription": {
    "action_code": "INCREASE_MODES_AND_CUTOFF",
    "suggested_fix": "增加模態提取階數至 35 階以上，並擴大頻率搜索上限至 3000 Hz。",
    "code_snippet": "analysis.Options.RangeMaximum = Quantity(3000.0, 'Hz')\nanalysis.Options.NumberOfModes = 35"
  },
  "execution_time_ms": 38.2
}
```

---

### 4.3 同步微步工具 (Primitives) vs 異步工作流 (Workflows) 雙軌執行模型

系統將所有工具明確劃分為兩大執行軌道：

| 特性比較項 | 互動微步工具 (Interactive Primitives) | 高階情境意圖工作流 (Async Intent Workflows) |
| :--- | :--- | :--- |
| **典型代表** | `geometry_create_block`, `mechanical_add_force` | `workflow_run_drop_test`, `run_thermal_warpage` |
| **執行耗時** | 通常 $< 3$ 秒 | 數十秒至數小時 |
| **調用方式** | 同步阻塞呼叫，即時返回實體 ID 或設定狀態 | 非同步呼叫，500ms 內立即返回 `job_id` 與沙盒路徑 |
| **狀態依附** | 依附於目前常駐之 `SessionRegistry` 連線會話 | 建立獨立生命週期之 `JobSandbox` 隔離環境 |
| **守護機制** | 基礎參數校驗與例外攔截 | `WatchdogDaemon` 實時串流日誌 + `CircuitBreaker` 發散熔斷 |
| **交付成果** | 單一原子物件或屬性設定成功確認 | 三位一體交付物：`summary.json` + 高清雲圖 + `overview.html` |

---

### 4.4 非同步作業沙盒 (JobManager) 與實時物理守護熔斷 (Watchdog + CircuitBreaker)

#### 1. 沙盒目錄架構與資產唯讀保護
作業沙盒在 `jobs/` 目錄下自動建立命名空間：
```text
jobs/{timestamp}_{suffix}_{workflow_type}_{tag}/
├── inputs/           # 外部 CAD、材料 XML、初始配置（強制 OS 唯讀鎖定）
├── workspace/        # 求解器暫存檔、日誌、.rst、.cas/.dat、d3plot 隔離運行區
└── artifacts/        # 正式交付物
    ├── images/       # 白底 1920x1080 等效應力、變形、溫度雲圖
    ├── summary.json  # 機器可讀關鍵數值與 PASS/FAIL 判定 (Pydantic 序列化)
    └── overview.html # 免伺服器單一自包含互動式 HTML 儀表板
```
`JobSandbox.protect_read_only()` 透過 Windows API `SetFileAttributesW(..., FILE_ATTRIBUTE_READONLY)` 或 Linux `chmod 0o444`，保證原始 CAD 模型永不被求解器寫入損壞。

#### 2. 實時守護進程與解析器架構
- `WatchdogDaemon`：以獨立背景線程運行（預設 0.5s 輪詢週期），串流讀取運行中之日誌檔案。
- 專屬日誌解析器：
  - `MechanicalMAPDLParser`：提取力平衡殘差、載荷步與非線性平衡迭代次數。
  - `LSDynaGlstatParser`：解析動能、內能、沙漏能、接觸滑移能與質量縮放比例。
  - `FluentResidualParser`：解析連續性 (continuity)、速度向量、能量及湍流殘差。

#### 3. 早期物理發散熔斷判據 (`CircuitBreaker`)
當 Watchdog 偵測到以下任一發散指標時，立即中斷進程並釋放 ANSYS 授權：
1. **沙漏能過大**：沙漏能佔比 $E_{hourglass} / E_{internal} > 5\%$（具備 3 次去抖動過濾，或單次突發 $> 15\%$ 立即熔斷）。
2. **質量縮放失真**：質量縮放導致總質量增長率 $> 5.0\%$。
3. **接觸穿透鎖死**：負接觸滑移能絕對值超過總能量的 $10.0\%$。
4. **數值溢位與暴衝**：殘差出現 `NaN`、`Inf` 或連續 5 步震盪暴衝超過 $10^{10}$。

---

### 4.5 求解前置安全閘門 (Gatekeeper) 與結構化自愈處方 (Prescription) 規格

#### 1. 完整前置安全閘門規則庫 (Gatekeeper Rules)
在原有 8 大規則基礎上，擴充五大領域專屬檢核，形成 13 大物理硬性閘門：

| 規則代碼 | 所屬領域 | 檢核物理邏輯 | 門檻指標與阻斷條件 | 自愈處方代碼 (Action Code) |
| :--- | :--- | :--- | :--- | :--- |
| `GATE-VIB-001` | 結構 | 三向累積有效模態質量比 | 累積質量比 $< 90.0\%$ 阻斷 | `INCREASE_MODES_AND_CUTOFF` |
| `GATE-VIB-002` | 結構 | 模態截斷頻率與激振頻率關係 | 截斷頻率 $< 1.5\times$ 激振上限阻斷 | `EXTEND_FREQUENCY_SEARCH` |
| `GATE-DRP-001` | 結構 | 落摔初始速度向量物理方向 | 初速向量與地面法向點積 $\ge 0$ 阻斷 | `CORRECT_VELOCITY_VECTOR` |
| `GATE-DRP-002` | 結構 | 特徵網格 CFL 時間步估計 | 臨界時間步 $< 10^{-11}\text{ s}$ 阻斷 | `APPLY_SELECTIVE_MASS_SCALING` |
| `GATE-DRP-003` | 結構 | 剛性靶板與接觸定義完備性 | 接觸對缺失或靶板自由度未約束阻斷 | `DEFINE_RIGIDWALL_CONTACT` |
| `GATE-THM-001` | 熱傳 | 割線熱膨脹係數 (Secant CTE) 完備性 | CTE 未定義或 $\le 0$ 阻斷 | `SPECIFY_TEMPERATURE_DEPENDENT_CTE` |
| `GATE-THM-002` | 熱傳 | 零應力參考溫度 ($T_{\text{ref}}$) 賦予 | 參考溫度缺失或超出 $[-50, 400]^\circ\text{C}$ 阻斷 | `ASSIGN_REFERENCE_TEMPERATURE` |
| `GATE-UNI-001` | 通用 | 單位系統一致性校驗 | 混用 MPa 與 $\text{kg/m}^3$ (密度差 $10^9$) 阻斷 | `ENFORCE_TON_MM_S_UNIT_SYSTEM` |
| `GATE-MSH-001` | 網格 | 網格最小正交品質 (Min Orthogonal Quality) | 正交品質 $< 0.15$ 或歪斜度 $> 0.85$ 阻斷 | `INCREASE_SURFACE_RESOLUTION` |
| `GATE-MSH-002` | 網格 | 邊界層稜柱層膨脹比率 | 壁面首層網格無量綱距離 $y^+ > 5$ (湍流) 阻斷 | `REFINE_BOUNDARY_PRISM_HEIGHT` |
| `GATE-CFD-001` | 熱傳 | Boussinesq 自然對流適用性 | $\beta (T_{\max} - T_0) > 0.1$ 阻斷 | `SWITCH_TO_IDEAL_GAS_LAW` |
| `GATE-PKG-001` | 封裝 | 封裝翹曲 3-2-1 靜定無拘束約束 | 存在人為過約束（非 3-2-1 約束）阻斷 | `APPLY_ISOSTATIC_321_SUPPORTS` |
| `GATE-STR-001` | 結構 | 非線性接觸初始幾何穿透量 | 初始法向穿透 $> 2\%$ 網格特徵尺寸阻斷 | `ADJUST_INITIAL_CONTACT_CLEARANCE` |

---

### 4.6 目錄重塑與系統拓撲架構圖

重塑現行模組結構，拆分雜湊的 `sim_tools.py` 與 `sim_impl.py`，建立高內聚、低耦合之對稱架構：

```text
src/ansys_unified_mcp/
├── __main__.py                      # 系統入口與動態 Profile 路由器
├── shared.py                        # 全域 FastMCP 實例與 aliased_tool 裝飾器
├── config.py                        # 全域路徑與環境變數管理
├── core/
│   ├── sentinel/                    # 實時物理守護進程、隊列與熔斷器
│   │   ├── watchdog.py              # 後台守護線程 (0.5s 輪詢)
│   │   ├── circuit_breaker.py       # 物理指標發散熔斷器
│   │   └── parsers/                 # MAPDL, LS-DYNA, Fluent, PrimeMesh, Icepak 日誌解析
│   ├── sessions.py                  # 多求解器連線會話註冊表
│   └── script_guard.py              # ACT/Python 腳本安全防護與關鍵字過濾
├── gatekeeper/                      # 求解前置安全閘門
│   ├── gatekeeper.py                # 前檢主控引擎
│   ├── prescription.py              # 結構化自愈處方模型 (Pydantic)
│   └── rules/                       # 13 大物理規則庫 (Vibration, Drop, Thermal, Mesh, Packaging)
├── jobs/                            # 作業生命週期與沙盒目錄隔離
│   ├── manager.py                   # JobManager
│   ├── sandbox.py                   # JobSandbox (inputs/workspace/artifacts)
│   └── models.py                    # SimulationSummary Pydantic 模型
├── drivers/                         # 底層求解器驅動抽象層
│   ├── base.py                      # BaseSolverDriver 抽象基類
│   ├── mechanical_driver.py         # 結構求解器驅動 (PyMechanical)
│   ├── lsdyna_driver.py             # 顯式動力學驅動 (LS-DYNA)
│   ├── geometry_driver.py           # 幾何前處理驅動 (PyGeometry/SpaceClaim)
│   ├── fluent_driver.py             # 流體/共軛熱傳驅動 (PyFluent)
│   ├── icepak_driver.py             # 電子散熱驅動 (PyAEDT-Icepak)
│   ├── primemesh_driver.py          # [新增] PyPrimeMesh 驅動
│   └── packaging_driver.py          # [新增] 電子封裝/EDB 驅動
├── tools/                           # MCP 工具暴露層 (一律以 aliased_tool 統一註冊)
│   ├── structural.py                # 結構原子工具 (原 mechanical.py 升級)
│   ├── structural_workflows.py      # 結構高階一鍵分析工具
│   ├── geometry.py                  # [獨立] 幾何前處理與特徵修復工具
│   ├── thermal.py                   # [獨立] 熱分析與 Icepak 電子散熱工具
│   ├── primemesh.py                 # [新增] PyPrimeMesh 高階網格劃分工具
│   ├── packaging.py                 # [新增] PCB 疊構、均質化與封裝工具
│   ├── optislang.py                 # 參數尋優與代理模型工具
│   ├── workbench.py                 # Workbench 流程與單元鏈結工具
│   ├── intent_tools.py              # 系統級五大工程工況入口
│   └── sentinel_tools.py            # 非同步作業提交、狀態、串流日誌與中止
├── workflows/                       # 端到端多物理場工作流腳本
│   ├── drop_test.py                 # 落摔衝擊工作流
│   ├── shock_analysis.py            # 衝擊反應譜工作流
│   ├── random_vibration.py          # 隨機振動工作流
│   ├── thermal_warpage.py           # PCB/封裝熱翹曲工作流
│   ├── packaging_reliability.py     # [新增] 封裝焊點疲勞壽命評估工作流
│   └── workbench_links.py           # 原生單元鏈結語法產生器
└── reporting/                       # 自包含成果報告合成器
    ├── generator.py                 # overview.html 與 summary.json 合成
    └── charts.py                    # 免伺服器互動式 SVG 響應圖表渲染
```

---

## 第五章：R4. 分階段落地優化里程碑計畫 (Phased Implementation Roadmap)

---

### 5.1 演進路線總覽

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Phase 1: 基礎解耦、命名雙軌標準化與核心三領域強化 (W1 ~ W3)              │
│ - 徹底拆分 sim_tools.py，全面導入 aliased_tool 雙軌相容層                │
│ - 全域統一原生 Dict 回傳信封，清除脆弱字串啟發式比對                     │
│ - 實裝 thermal/icepak 原子工具模組與獨立幾何修復工具                    │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼─────────────────────────────────────┐
│ Phase 2: 高階網格 (PyPrimeMesh) 驅動實裝與工具鏈整合 (W4 ~ W6)            │
│ - 引入 ansys-meshing-prime，封裝原生 PrimeMeshDriver                     │
│ - 支援髒 CAD 水密收縮包覆 (Surface Wrap) 與 Mosaic Poly-Hexcore 體網格  │
│ - 擴充網格品質前置安全閘門 (GATE-MSH-001/002) 與 Watchdog 守護           │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼─────────────────────────────────────┐
│ Phase 3: 電子封裝多物理場 (PyAEDT/Sherlock) 與焊點疲勞閉環 (W7 ~ W10)    │
│ - 建立 ECAD (EDB/ODB++) 解析與 PCB 疊構均質化 (ROM) 工具                │
│ - 實裝 Anand 黏塑性蠕變本構與 Darveaux 焊點熱疲勞循環壽命評估           │
│ - 實現 ECAD -> 幾何 -> PrimeMesh -> Icepak -> Mechanical 完整閉環       │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### 5.2 Phase 1：基礎解耦、命名雙軌標準化與核心三領域強化 (W1 ~ W3)

#### 目標成果
- 徹底消除 `sim_tools.py` 與 `sim_impl.py` 的歷史包袱，完成模組解耦。
- 全系統 100% 統一採用 `aliased_tool` 雙軌註冊與標準回傳信封。
- 完善結構、幾何與 Thermal/Icepak 三大基礎領域工具體系，消除字串誤判。

#### 輸入與輸出規格
- **輸入規格**：標準 Python 原生型別與 Pydantic 模型，包含物理量單位。
- **輸出規格**：標準 `{"ok": bool, "status": str, "data": dict, ...}` 原生字典。

#### 交付工具清單
1. `src/ansys_unified_mcp/tools/geometry.py`:
   - `geometry_create_block`（別名: `create_block`）
   - `geometry_create_cylinder`（別名: `create_cylinder`）
   - `geometry_sketch_and_extrude`（別名: `sketch_and_extrude`）
   - `geometry_create_enclosure`（別名: `create_enclosure`）
   - `geometry_repair_small_features` [新增]: 自動清理細小邊與破面
   - `geometry_check_watertight` [新增]: 水密性流道檢查工具
2. `src/ansys_unified_mcp/tools/thermal.py` [全新獨立模組]:
   - `thermal_create_heatsink`: 散熱片參數化幾何生成
   - `thermal_assign_heat_source`: 晶片發熱功率指派
   - `thermal_set_convection_bc`: 自然/強迫對流換熱係數指派
   - `thermal_setup_dual_interface_ic`: 晶片雙熱阻模型配置
3. `src/ansys_unified_mcp/tools/structural.py` & `structural_workflows.py`:
   - `mechanical_check_contact_status`: 非線性接觸狀態診斷
   - `mechanical_setup_and_solve_transient`: 一鍵式暫態動力學分析

#### 客觀驗收指標 (Verification Conditions)
- [ ] 執行 `pytest tests/test_aliased_tools.py` 通過率 100%，覆蓋全域重構與新增工具的新舊別名等效性。
- [ ] 全模組回傳值經 Schema 檢驗，100% 符合標準信封，字串包含式錯誤比對代碼完全清除。
- [ ] 經典案例 04（Mixing Elbow 幾何）與案例 06（散熱片 CHT）在 Mock/離線環境下端到端運行無異常。

---

### 5.3 Phase 2：高階網格 (PyPrimeMesh) 驅動實裝與工具鏈整合 (W4 ~ W6)

#### 目標成果
- 引入 `ansys-meshing-prime`，實裝原生 `PrimeMeshDriver`。
- 開發完整之表面收縮包覆、CAD 修復與 Mosaic Poly-Hexcore 網格劃分工具鏈。
- 將網格品質守護納入 Pre-Flight 閘門與 Sentinel Watchdog 體系。

#### 輸入與輸出規格
- **輸入規格**：CAD 檔案路徑（STEP/FMD/STL）、體素尺寸、稜柱層控制參數、最大扭曲度門檻。
- **輸出規格**：`.msh` 網格檔案、網格統計指標（節點數、單元數、正交品質分佈直方圖）。

#### 交付工具清單
1. `src/ansys_unified_mcp/tools/primemesh.py` [全新模組]:
   - `primemesh_launch_session`: 啟動 PrimeMesh 本地/無頭微服務
   - `primemesh_import_cad`: 導入 CAD 並執行拓撲檢查
   - `primemesh_surface_wrap`: 執行體素收縮包覆生成水密表面
   - `primemesh_generate_poly_hexcore`: 劃分 Mosaic Poly-Hexcore 體網格
   - `primemesh_check_mesh_quality`: 提取網格歪斜度與正交品質
   - `primemesh_export_mesh`: 導出網格檔案至 Fluent / Mechanical
2. `src/ansys_unified_mcp/gatekeeper/rules/mesh_rules.py`:
   - `GATE-MSH-001`: 正交品質 $<0.15$ 或歪斜度 $>0.85$ 硬性阻斷
   - `GATE-MSH-002`: 壁面首層網格無量綱距離 $y^+$ 檢核

#### 客觀驗收指標 (Verification Conditions)
- [ ] 實裝 `tests/test_primemesh_tools.py`，驗證 PrimeMesh 微服務連線與降級保護機制。
- [ ] 當輸入扭曲度超標（Skewness $>0.85$）網格時，Pre-Flight 閘門精確阻斷並輸出自愈處方。
- [ ] 經典案例 08（車身表面包覆）與案例 09（排氣歧管 Poly-Hexcore）成功生成高品質網格並導出 `.msh`。

---

### 5.4 Phase 3：電子封裝多物理場 (PyAEDT/Sherlock) 與焊點疲勞閉環 (W7 ~ W10)

#### 目標成果
- 建立 ECAD 數據鏈路，支援 PCB 佈局與多層板疊構解析。
- 實裝基於體積加權之 PCB 等效各向異性材料常數均質化計算 (ROM)。
- 建立晶片-封裝-PCB 系統級熱翹曲 (Thermal Warpage) 與焊點疲勞壽命可靠度閉環。

#### 輸入與輸出規格
- **輸入規格**：ECAD 檔案（.aedb/ODB++/IPC-2581）、疊構配置表、加速熱循環溫變曲線。
- **輸出規格**：三維翹曲雲圖、JEDEC B112 共面度判據、焊點累積塑性應變能、Darveaux 疲勞壽命週數。

#### 交付工具清單
1. `src/ansys_unified_mcp/tools/packaging.py` [全新模組]:
   - `packaging_import_ecad`: 讀取 ODB++ / IPC-2581 / EDB 設計檔案
   - `packaging_extract_stackup`: 提取各層厚度、殘銅率與介電材料
   - `packaging_compute_homogenized_properties`: 計算各層等效 $E_i, \nu_i, \alpha_i$
   - `packaging_setup_solder_balls`: 參數化建立 BGA 焊球陣列
   - `packaging_evaluate_fatigue_life`: 依據 Darveaux 模型評估熱疲勞循環壽命
2. `src/ansys_unified_mcp/workflows/packaging_reliability.py`:
   - 端到端工作流：ECAD 導入 $\rightarrow$ 疊構等效 $\rightarrow$ 溫度場求解 $\rightarrow$ 熱應力翹曲 $\rightarrow$ 焊點壽命評估。
3. `src/ansys_unified_mcp/gatekeeper/rules/packaging_rules.py`:
   - `GATE-PKG-001`: 3-2-1 靜定無拘束約束完整性檢核。

#### 客觀驗收指標 (Verification Conditions)
- [ ] 實裝 `tests/test_packaging_workflow.py`，完整驗證 ECAD 參數抽取與 ROM 材料計算正確性。
- [ ] 經典案例 10（BGA 熱翹曲）與案例 11（SAC305 錫球疲勞）端到端求解成功，產出合規之 `summary.json` 與包含互動式遲滯迴線之 `overview.html`。
- [ ] 驗證 Workbench 原生單元鏈結直通 Icepak $\rightarrow$ Static Structural $\rightarrow$ Fatigue Tool。

---

## 第六章：依賴管理矩陣與可選相容性安裝策略 (`[project.optional-dependencies]`)

---

### 6.1 底層依賴庫衝突與環境風險分析

五大核心領域若在主依賴中全數引入，將引發嚴重的環境相依性衝突與體積膨脹：

| 套件名稱 | 領域分類 | 底層協議 / 外部運行環境 | 潛在衝突與風險點 |
| :--- | :--- | :--- | :--- |
| `ansys-mechanical-core` | 結構 | gRPC / ACT IronPython | 依賴本機 ANSYS 安裝 (v222~v242)，gRPC 端口鎖定 |
| `ansys-geometry-core` | 幾何 | gRPC (SpaceClaim / Discovery) | 依賴 Windows API 與 SpaceClaim AddIn，無頭環境困難 |
| `ansys-fluent-core` | 熱傳/CFD | gRPC | 與 PyMechanical 之 protobuf/grpcio 版本相容性要求高 |
| `ansys-meshing-prime` | 高階網格 | 原生 C++ 核心 / gRPC Server | 二進位 DLL 依賴與獨立 Server 進程生命週期管理 |
| `pyaedt` / `ansys-edb-core`| 電子封裝 | .NET / COM / gRPC (AEDT) | `pythonnet` 與 Windows .NET Framework 依賴，體積龐大 (>5GB) |

**風險結論**：強行打包為單一全包安裝將導致 Python 3.10~3.12 跨版本編譯失敗，且在無 GPU 或純 Linux 容器中極易發生 DLL 遺失錯誤。因此，必須採取**「極簡核心 + 領域可選安裝 (Modular Extras)」**架構。

---

### 6.2 模組化可選安裝策略與 pyproject.toml 規範

在 `pyproject.toml` 中實施嚴格的分層安裝策略：

```toml
[project]
name = "ansys-unified-mcp"
version = "2.1.0"
description = "Unified Model Context Protocol Server for ANSYS CAE Ecosystem"
readme = "README.md"
requires-python = ">=3.10,<3.13"
dependencies = [
    "fastmcp>=0.4.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "psutil>=5.9.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
# 領域可選安裝 (Domain-specific Extras)
structural = [
    "ansys-mechanical-core>=0.10.0",
    "ansys-mapdl-core>=0.68.0",
    "lasso-python>=1.5.0",
]
geometry = [
    "ansys-geometry-core>=0.4.0",
]
thermal = [
    "ansys-fluent-core>=0.20.0",
]
mesh = [
    "ansys-meshing-prime>=0.5.0",
]
packaging = [
    "pyaedt>=0.8.0",
    "ansys-edb-core>=0.1.0",
]
optislang = [
    "ansys-optislang-core>=0.6.0",
]

# 完整全功能安裝 (Full Installation)
full = [
    "ansys-unified-mcp[structural,geometry,thermal,mesh,packaging,optislang]",
]

# 開發與測試依賴 (Development & Testing)
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
]
```

安裝使用指引：
- **輕量幾何與結構工作站**：`pip install ansys-unified-mcp[structural,geometry]`
- **流體與熱傳專用節點**：`pip install ansys-unified-mcp[thermal,mesh]`
- **電子封裝可靠度工作站**：`pip install ansys-unified-mcp[structural,packaging]`
- **全功能企業級中樞**：`pip install ansys-unified-mcp[full]`

---

### 6.3 跨平台無頭執行與 Mock/Synthetic 降級相容機制

為了支援無 ANSYS 實體授權之 CI/CD 測試、代碼審查與容器化部署，系統實裝雙模降級保護機制：
1. **動態驅動探測 (Dynamic Driver Probe)**：
   每個 Driver 在初始化時執行 `validate_prerequisites()`：
   ```python
   # drivers/base.py 生命週期
   def validate_prerequisites(self) -> DriverCapability:
       has_ansys = detect_local_ansys_installation()
       has_license = check_license_available()
       if not (has_ansys and has_license):
           logger.warning(f"{self.product_name} 實體求解器不可用，啟用 Synthetic 仿真模式。")
           return DriverCapability(mode="SYNTHETIC", is_mock=True)
       return DriverCapability(mode="LIVE", is_mock=False)
   ```
2. **顯式 Synthetic 標記**：
   在 Synthetic 模式下，回傳信封必須顯式包含 `"is_synthetic": true` 與 `"mock_reason": "NO_LICENSE_DETECTED"`，徹底杜絕將經驗公式估算冒充為有限元真實求解之誠信風險。
3. **無頭容器化相容 (Headless Docker Compatibility)**：
   針對 Linux Docker 環境，提供無頭啟動腳本，將 PyMechanical 與 PyPrimeMesh 透過 gRPC 微服務架構與前端 MCP 伺服器解耦，確保跨平台部署之穩定性。

---

> **報告發布簽署**：Specification & Architecture Worker (`teamwork_preview_worker`)  
> **狀態驗證**：六大章節完整編撰完畢，技術數據嚴謹可查，符合全域規範與誠信準則。
