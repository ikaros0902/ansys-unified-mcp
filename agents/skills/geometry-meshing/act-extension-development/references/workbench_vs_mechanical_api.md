# Workbench 與 Mechanical API 層級對照 (workbench_vs_mechanical_api.md)

ACT 腳本在 Workbench Project Schematic 層級與 Mechanical 層級分屬不同的架構職責、入口點與命名空間。來源：`Workbench_Scripting_Guide`、`Ansys_ACT_Developers_Guide`、`Ansys_Scripting_in_Mechanical_Guide`、`Ansys_ACT_API_Reference_Guide`（Release 2026 R1）。

---

## 一、架構職責對比

| 層級 | 定位 | 核心職責 |
|---|---|---|
| **Workbench** | 框架層級（Framework Level），Project Schematic 專案管理平台 | 工作流整合、資料傳送（Data Transfer）、參數集管理、跨系統調度 |
| **Mechanical** | 數據整合應用層級（Data-Integrated Application） | 幾何/網格處理、邊界條件加載、APDL 求解指令注入、後處理結果計算 |

## 二、DataModel 入口點對照

### Workbench 層級

```python
project = ExtAPI.DataModel.Project       # 框架層級專案、檔案管理
context = ExtAPI.DataModel.Context       # 會話與專案公用程式
tasks = ExtAPI.DataModel.Tasks           # Schematic 上所有具體 Component/Cell 實例
taskGroups = ExtAPI.DataModel.TaskGroups # Schematic 上所有具體 System/TaskGroup 實例
# 便捷查詢
ExtAPI.DataModel.GetTaskByName(taskName)
ExtAPI.DataModel.GetTaskGroupByName(taskGroupName)
```

> 原文：「Tasks — This is all of the tasks in the Project Schematic, which includes both ACT-defined and Ansys-installed tasks. It does not include the "master task" level... Only concrete task instances are included.」

### Mechanical 層級

```python
Model = DataModel.Project.Model          # UI 樹狀根節點：Geometry/Mesh/Analyses/Connections
DataModel.Tree                           # UI 樹狀結構，可用 Tree.FirstActiveObject / Tree.Activate()
DataModel.GeoData                        # 底層幾何拓樸：Assemblies -> Parts -> Bodies -> Faces
DataModel.MeshByName("Global")           # 底層網格 FE 資料：NodeIds/ElementIds/連通性
```

> 關鍵區分（原文）：「Model.Mesh accesses the object Mesh in the Mechanical tree... DataModel.MeshByName("Global") accesses FE information (node and element locations, element connectivity, and so on).」同理，`Model.Geometry` 是樹狀 UI 物件，`DataModel.GeoData` 是底層幾何資料，兩者不可混用。

## 三、API 命名空間對照

| 層級 | 命名空間 | 內容 |
|---|---|---|
| Workbench | `Ansys.ACT.WorkBench.Automation.Workflows` | `Task`/`ITask`、`TaskGroup`/`ITaskGroup`、`Parameter`/`IWBParameter`、`Property`/`IWBProperty`、`TaskTemplate`、`TaskGroupTemplate` |
| Workbench | `Ansys.ACT.Interfaces.Workflow` | 介面定義：`ITask`、`ITaskGroup`、`IWBParameter`、`ParameterUsage` |
| Workbench | `Ansys.ACT.WorkBench.Schematic` | `UserTask`、`UserTaskGroup`、`UserTaskTemplate` |
| Mechanical | `Ansys.ACT.Automation.Mechanical` | 樹狀節點主體：`Analysis`、`Model`、`Geometry`、`NamedSelection`、`Material` |
| Mechanical | `Ansys.ACT.Automation.Mechanical.Results`（及子命名空間 `.StressResults`/`.DeformationResults`/`.ContactToolResults`/`.ThermalResults`/`.ProbeResults`） | 後處理結果類別 |
| Mechanical | `Ansys.ACT.Automation.Mechanical.BoundaryConditions` / `.Connections` | 邊界條件與連接 |
| Mechanical | `Ansys.ACT.Automation.Mechanical.MeshControls` / `.FE`（含 `.CDB`/`.NASTRAN`/`.ABAQUS` 解析器） | 網格控制與有限元素資料 |
| Mechanical | `Ansys.ACT.Interfaces.Mechanical`、`Ansys.Mechanical.DataModel` / `.DataModel.Enums` | 介面與資料模型 |

## 四、Task/Parameter/Property 存取範例（Workbench）

```python
# Task 存取（透過 Dictionary 介面讀寫 Property）
task = ExtAPI.DataModel.Tasks[0]
task.Properties["GeometryImportSolidBodies"].Value = True

# Parameter 存取
p0 = task.Parameters[0]
value = p0.Value
p0.Value = value * 2

# Property 存取
p1 = task.Properties["PropertyOne"]
value = p1.Value
```

> 注意：ACT-defined callbacks 仍接收 `UserTasks` 作為引數；`UserTaskTemplate` 現在可透過 `Template` 屬性存取。

## 五、Job Dependency 的選型判斷

`<rsmjob>` 搭配 `<callbacks>` 的 `<onjobstatus>`、`<onjobcancellation>`、`<onjobreconnect>` 用於遠端求解/非同步任務的狀態監控，常搭配 `System.IO.File.Exists()` 做輪詢判斷：

```python
def getJobStatus(task, outputFiles):
    outputFilePath = outputFiles[0]
    finished = System.IO.File.Exists(outputFilePath)
    return finished
```

此機制與 `filesystemwatcher_pattern.md` 的 `FileSystemWatcher` 事件驅動模式是兩種不同手法：`FileSystemWatcher` 適合本機即時監聽；`<onjobstatus>` 輪詢適合遠端/RSM 排程任務，無法用事件驅動時的備援方案。
