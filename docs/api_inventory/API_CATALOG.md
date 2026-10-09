# ANSYS 四大模組 API 全量萃取總目錄與查閱手冊 (API Catalog)

本目錄彙整 ANSYS 2025 R1 (`v251`) 環境下四大核心模組（Mechanical、SpaceClaim、LS-DYNA、optiSLang）之完整 Function、Class、Method、Property 與 Keyword 字典。

所有 API 均以結構化 JSON 格式持久化儲存於硬碟離線手冊庫中，供工程自動化、代碼生成、智慧補全與 Agent 精準檢索使用，徹底杜絕全量載入引發之 Context Window / Token 膨脹問題。

---

## 一、API 萃取統計總覽 (Extraction Statistics)

| 模組名稱 | 原始來源 | 導出檔案 | 涵蓋範疇 | 核心統計數據 | 檔案大小 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ANSYS Mechanical** | `ansys-mechanical-stubs/v251` (ACT DataModel) | [`mechanical_api.json`](./mechanical_api.json) | Analysis, Mesh, BoundaryConditions, Connections, Results, Solution | **105** 模組<br>**1,728** 類別<br>**40,886** 方法<br>**46,626** 屬性 | ~23.9 MB |
| **SpaceClaim (SCDM)** | `SpaceClaim.Api.V251.Scripting.dll` (.NET Reflection) | [`spaceclaim_api.json`](./spaceclaim_api.json) | Geometry, Part, Body, Face, Edge, Selection, Tools, Component | **1,266** 型別<br>**2,845** 方法<br>**1,551** 屬性<br>**114** 列舉 | ~1.59 MB |
| **optiSLang** | `ansys.optislang.core` & `v251/optiSLang/scripting` | [`optislang_api.json`](./optislang_api.json) | Client, Project, RootSystem, Node, Parameter, Criterion, MOP, Algorithms | **37** 模組<br>**241** 類別<br>**1,691** 方法<br>**133** 頂層函式<br>**9** 類內建演算法 | ~1.44 MB |
| **LS-DYNA & LS-PrePost** | `LsPrePost`, `DataCenter`, SCL C-API & Keyword Deck | [`lsdyna_api.json`](./lsdyna_api.json) | LSPP Python, SCL 命令集, DataCenter 提取, 核心關鍵字字典 (*CONTROL, *MAT, *CONTACT 等) | **3** Python API<br>**10** DataCenter 查詢鍵<br>**8** SCL C-API 函式<br>**35** 核心關鍵字定義 | ~15.6 KB |

---

## 二、四大模組架構與核心 API 導覽

### 1. ANSYS Mechanical (ACT DataModel API)
* 檔案路徑：[`mechanical_api.json`](./mechanical_api.json)
* 核心架構階層：
  * **Model / Geometry**: `Ansys.ACT.Automation.Mechanical.Model`, `Geometry`, `Body`, `Part`
  * **Mesh Controls**: `Ansys.ACT.Automation.Mechanical.Mesh`, `MeshControl`, `Sizing`, `Inflation`
  * **Boundary Conditions**: `FixedSupport`, `Force`, `Pressure`, `Displacement`, `RemoteDisplacement`, `StandardEarthGravity`
  * **Connections**: `Connections`, `ConnectionGroup`, `ContactRegion` (Bonded, Frictional, Frictionless)
  * **Analysis / Solution**: `Analysis`, `AnalysisSettings`, `Solution`, `SolverData`
  * **Results**: `TotalDeformation`, `EquivalentStress`, `EquivalentPlasticStrain`, `DirectionalDeformation`, `StressTool`
* 典型 ACT 代碼模式（IronPython / ASCII）：
  ```python
  # Access active model and geometry
  model = ExtAPI.DataModel.Project.Model
  geom = model.Geometry
  mesh = model.Mesh
  mesh.ElementSize = Quantity("2.5 [mm]")
  mesh.GenerateMesh()
  
  # Add Boundary Condition
  analysis = model.Analyses[0]
  fixed_support = analysis.AddFixedSupport()
  fixed_support.Location = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
  
  # Solve and Evaluate
  analysis.Solve(True)
  eqv_stress = analysis.Solution.AddEquivalentStress()
  eqv_stress.EvaluateAllResults()
  max_stress = eqv_stress.Maximum.Value
  ```

---

### 2. SpaceClaim (SCDM Scripting API)
* 檔案路徑：[`spaceclaim_api.json`](./spaceclaim_api.json)
* 核心命名空間：`SpaceClaim.Api.V251.Scripting`
* 核心類別清單：
  * **主控制器與視窗**：`Window`, `Document`, `Part`, `Component`
  * **幾何物件模型**：`Body`, `Face`, `Edge`, `Vertex`, `DesignBody`, `DesignFace`
  * **草圖與拓撲建立**：`SketchPoint`, `SketchLine`, `SketchCircle`, `Plane`, `Point`, `Direction`
  * **特徵操作工具**：`FixErrors`, `Midsurface`, `VolumeExtract`, `PowerSelect`, `ExtrudeFaces`, `RevolveFaces`
* 典型 SpaceClaim 腳本模式：
  ```python
  # Set sketch plane and draw circle
  result = DatumPlaneCreator.Create(Point.Create(0, 0, 0), Direction.DirZ)
  plane = result.CreatedPlanes[0]
  ViewHelper.SetSketchPlane(plane)
  SketchCircle.Create(Point2D.Create(0, 0), 25.0)
  ViewHelper.SetViewMode(InteractionMode.Solid)
  
  # Pull (Extrude) face into 3D cylinder
  faces = Selection.Create(GetRootPart().Bodies[0].Faces[0])
  options = ExtrudeFaceOptions()
  options.ExtrudeType = ExtrudeType.Add
  FixSimplify.FindAndFix()
  ```

---

### 3. optiSLang (PyOptiSLang & Scripting API)
* 檔案路徑：[`optislang_api.json`](./optislang_api.json)
* 核心架構階層：
  * **客戶端連接與進程**：`ansys.optislang.core.Optislang`, `OslServerProcess`
  * **專案與系統節點**：`Project`, `RootSystem`, `System`, `Node`
  * **參數與評價指標**：`Parameter`, `Criterion`, `Design`, `DesignVariable`
  * **演算法與節點庫**：`Sensitivity`, `Optimization`, `MOP` (Metamodel of Optimal Prognosis), `Sobol`, `ARSM`
* 典型 Python 自動化模式：
  ```python
  from ansys.optislang.core import Optislang
  
  with Optislang() as osl:
      project = osl.project
      root_sys = project.root_system
      
      # Add Sensitivity and MOP node
      sens_node = root_sys.create_node("Sensitivity")
      mop = sens_node.get_actor()
      
      # Register Parameters and Criteria (Verified APIs)
      root_sys.parameter_manager.add_parameter("thickness", 1.2, 0.8, 2.0)
      root_sys.criterion_manager.add_criterion("max_stress", "< 250")
      
      # Execute run
      project.start()
  ```

---

### 4. LS-DYNA & LS-PrePost (Solver & Post-Processing API)
* 檔案路徑：[`lsdyna_api.json`](./lsdyna_api.json)
* 核心架構三軌制：
  * **軌道一：LS-PrePost 內嵌 Python 自動化 (`LsPrePost`, `DataCenter`)**
    ```python
    import LsPrePost as lspp
    import DataCenter as dc
    
    # Switch to final state and compute fringe
    num_states = dc.get_data("num_states")
    lspp.execute_command(f"state {num_states}")
    lspp.execute_command("fringe 7; pfringe")
    
    # Query maximum von Mises stress
    max_vm_stress = lspp.cmd_result_get_value(1)
    ```
  * **軌道二：LS-PrePost SCL (Scripting Command Language) C-API**
    * 向量與張量提取：`SCLGetDataCenterFloat`, `SCLGetDataCenterVector`, `SCLGetDataCenterTensor`
    * 狀態切換與控制：`SCLSwitchStateTo`, `SCLPrintMessage`
  * **軌道三：LS-DYNA 關鍵字驅動體系 (Keyword Deck)**
    * 求解器調用：`lsdyna_dp.exe i=run.k ncpu=8 memory=4000m`
    * 關鍵字分組覆蓋：`*CONTROL`, `*DATABASE`, `*MAT`, `*SECTION`, `*CONTACT`, `*BOUNDARY`, `*LOAD`

---

## 三、API 知識庫與 FastMCP 工具使用指南

本專案將萃取之 API 知識整合至高效的 SQLite 知識層（`api_kb.sqlite`），並封裝了 4 個即時 MCP 查詢與防護工具：

| MCP 工具名稱 | 功能說明 | 典型呼叫範例 |
| :--- | :--- | :--- |
| **`api_search`** | 快速檢索類別、方法、屬性或關鍵字 (FTS5 + Trigram) | `api_search(query="fixed support", product="mechanical")` |
| **`api_get`** | 獲取特定 API 符號之所有成員、型別出入邊與文檔 | `api_get(fqname="Analysis", include="members,edges")` |
| **`api_path`** | 在知識星譜圖中尋找物件存取導航鏈 (BFS 拓撲) | `api_path(from_type="Analysis", to_type="EquivalentStress")` |
| **`api_validate_script`** | 腳本靜態防幻覺校驗器，比對未定義屬性並給予建議 | `api_validate_script(code="...", product="mechanical")` |

---

## 四、更新與維護機制

本專案於 `scripts/` 目錄內建了一鍵式批次萃取與知識庫自動建置流水線：
```powershell
python scripts/extract_all_apis.py
```
執行後將自動完成四大模組 API 抽取，並同步重新編譯 `Documentation_clean/api_kb.sqlite` 索引庫與型別關係圖。
