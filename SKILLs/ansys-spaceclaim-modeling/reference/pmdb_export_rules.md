# 無損 PMDB/FMD 導出與下游網格無縫接軌規範手冊 (PMDB Export Rules)

在 ANSYS 全流程自動化架構中，中介檔案格式的選擇決定了幾何資訊傳遞的忠實度。傳統 STEP/IGES 格式在跨軟體傳遞時，經常面臨公差接縫撕裂、微小面畸變、以及最重要的——**CAD 具名選擇 (Named Selection) 遺失**。本手冊定義 PMDB/FMD 無損資料庫格式的導出規範與下游網格無縫接軌準則。

---

## 一、幾何格式特性對比矩陣

| 評估維度 | ANSYS PMDB (`.pmdb`) | Fluent Meshing DB (`.fmd`) | SpaceClaim 原生 (`.scdocx`) | 標準中介檔 (`.step`) |
|---|---|---|---|---|
| **幾何內核表示** | 原生 Parasolid B-Rep | 原生 Parasolid / Faceted | 原生 SpaceClaim ACIS/Parasolid | 標準邊界表示 (AP214/AP242) |
| **拓撲接縫公差** | **零誤差 (原生直通)** | **零誤差 (原生直通)** | 零誤差 | 需下游軟體進行重構縫合 |
| **CAD 具名選擇保留** | **100% 完整精確保留** | **100% 完整精確保留** | 完整保留 | 極易遺失或退化為無效組名 |
| **拓撲共享 (Shared Topology)** | **原生嵌入共面壓印節點** | 原生支援 | 原生支援 | 無法原生定義共面網格映射 |
| **下游適用工具** | Mechanical, Fluent Meshing, PyPrimeMesh | Fluent Meshing (專用) | SpaceClaim, Discovery, Workbench | 通用第三方 CAD/CAE 軟體 |
| **自動化推薦度** | ★★★★★ (首選無損格式) | ★★★★☆ (Fluent 專用) | ★★★★☆ (工程存檔用) | ★★☆☆☆ (僅限第三方交換) |

---

## 二、拓撲共享 (Shared Topology) 設置規範

在多實體裝配（如散熱片與發熱晶片之共軛熱傳 CHT，或多件結構裝配）中，必須在 SpaceClaim 或 PyAnsys Geometry 中設置拓撲共享，以確保下游網格在交界面上**節點完全共用 (Conformal Mesh)**，避免使用數值插值或非保形接觸對 (Non-conformal contact)。

### 1. 設置模式
- **Share Mode = Share (共享)**：幾何引擎自動對相交表面進行布林壓印 (Imprint)，產生單一公共幾何面。下游網格生成器將保證交界面上網格節點 1:1 完全重合。
- **檢驗判據**：在 SpaceClaim 中檢查共面邊緣顏色是否轉為粉紅色 (Shared Edge Indicator)。

### 2. SpaceClaim 腳本設定拓撲共享
```python
# 設定整體零件啟用 Shared Topology
part = GetRootPart()
part.SharedTopology = SharedTopology.Share
```

---

## 三、無損導出前檢查清單 (Pre-Export Checklist)

在呼叫 `export_to_pmdb()` 之前，必須嚴格逐項勾稽下列檢查清單，任一項不滿足嚴禁導出：

- [ ] **草圖輔助幾何清理**：所有臨時繪製的 2D 草圖線、輔助點、構造線已全數清除或已固化為實體。
- [ ] **無多餘廢棄體 (Dead Bodies)**：布林相減後產生的零碎切屑體已刪除，場景中僅保留參與分析之目標體。
- [ ] **水密性驗證 (Watertight Check)**：所有實體均為流形封閉實體，無開放面 (Open Surface)。
- [ ] **CAD 缺陷零檢出**：已通過 CAD 診斷庫檢查，微小面 (Sliver Faces) 為 0，短邊為 0，無自交邊。
- [ ] **具名選擇完備性**：所有邊界外表面（Inlet, Outlet, Wall, Symmetry 等）及體域（Fluid/Solid）均已建立有效 Named Selections。
- [ ] **輸出目錄可寫入性**：目標資料夾存在且具備寫入權限，路徑無不相容之特殊非法字元。

---

## 四、PyAnsys Geometry 導出無損多格式腳本

```python
import os
from ansys.geometry.core.designer import Design

def export_lossless_geometry_suite(design: Design, output_dir: str, base_name: str = "simulation_model"):
    """
    導出以 PMDB 為核心的工業級無損幾何檔案集合
    """
    abs_dir = os.path.abspath(output_dir)
    os.makedirs(abs_dir, exist_ok=True)
    
    pmdb_path = os.path.join(abs_dir, f"{base_name}.pmdb")
    scdocx_path = os.path.join(abs_dir, f"{base_name}.scdocx")
    step_path = os.path.join(abs_dir, f"{base_name}.step")
    
    # 1. 導出 PMDB 原生幾何資料庫 (下游核心通道)
    design.export_to_pmdb(pmdb_path)
    
    # 2. 導出 SCDOCX 原生工程檔 (工程師審查與版本保存)
    design.export_to_scdocx(scdocx_path)
    
    # 3. 導出標準 STEP 格式 (第三方備份，非必須)
    design.export_to_step(step_path)
    
    return {
        "pmdb": pmdb_path,
        "scdocx": scdocx_path,
        "step": step_path
    }
```

---

## 五、下游求解器無縫接軌指引

### 1. 對接 Fluent Meshing (Watertight Geometry Workflow)
在 Fluent Meshing 啟動腳本中，直接載入導出的 `.pmdb` 檔案：
```python
# Fluent Meshing Python Journal
workflow.InitializeWorkflow(WorkflowType='Watertight Geometry')
workflow.TaskObject['Import Geometry'].Arguments.set_state({
    'FileName': r"C:\Path\To\simulation_model.pmdb",
    'LengthUnit': 'm'
})
workflow.TaskObject['Import Geometry'].Execute()
# 所有 CAD Named Selections 自動識別為 Capping Zones 與 Boundary Conditions！
```

### 2. 對接 PyPrimeMesh
```python
from ansys.meshing.prime import launch_prime, FileIO, CadRefactoring

prime = launch_prime()
model = prime.model
file_io = FileIO(model)

# 載入 PMDB，自動將 CAD Named Selections 映射為 Prime Part Zones
file_io.import_cad(file_name=r"C:\Path\To\simulation_model.pmdb")
```

### 3. 對接 ANSYS Mechanical
在 PyMechanical 或 Mechanical 批次腳本中，載入 `.pmdb` 幾何後，樹狀目錄下的 Named Selections 群組將原樣呈現，可直接作為載荷與支承的幾何作用範圍 (Scoping Mechanism)。
