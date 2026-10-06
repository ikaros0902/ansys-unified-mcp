# ANSYS CAE 自動化 Session 經驗總結與排障手冊 (Session Learnings & Troubleshooting)

**記錄日期**：2026-10-01  
**專案環境**：ANSYS Mechanical 2025 R1 (v251) - LS-DYNA (Explicit Dynamics), Python 3.12 / IronPython 2.7  
**核心主題**：全模型 114 個幾何零件之 MultiZone 優先策略、分區資料夾歸類、動態超時自愈劃分與拓撲判定規則沉澱。

---

## 一、 核心學習與架構認知 (What We Learned)

### 1. ANSYS Mechanical ACT Model Tree 的底層物件模型
* **Parent 物件本質**：
  在 Mechanical ACT 中，無論控制項（Sizing、AutomaticMethod）被收納於哪一個 `TreeGroupingFolder`，其在資料庫底層的物理父物件 `item.Parent` **永遠是 `Mesh`**。`TreeGroupingFolder` 在 ACT 中是屬於 UI 視圖的虛擬分組容器。
* **游離項防護機制**：
  透過 `mesh.AddAutomaticMethod()` 或 `mesh.AddSizing()` 新建的控制項，預設直接掛在 `Mesh` 根目錄。若未顯式執行 `folder.AddObject(new_control)` 或 `Tree.Group(...)`，該控制項會游離懸掛在所有資料夾外層。
* **極速收納與 UI 凍結**：
  批次建立或修改網格控制項時，必須包裹在 `with Transaction(True):` 中。此舉能凍結 UI 樹的即時重繪，避免產生嚴重卡頓（從數十秒縮減至秒級完成）。

### 2. MultiZone vs AllTriAllTet 演算法機理與幾何適用邊界
* **MultiZone 核心依賴**：
  MultiZone 依賴於 **3D Blocking（塊拓撲分解）** 與 **多源/多目標掃掠（Multi-Source / Multi-Target Sweeping）**。要求幾何在拓撲上能拆解為結構化六面體區塊。
* **長不出來（劃分失敗/死鎖）的幾何拓撲三大根因**：
  1. **非單調截面變化（Non-swept Cross-Section）**：零件存在多向加強肋、卡榫倒鉤、多軸向鏤空（如 260 面的拉手 Latch、180 面的塑膠件），找不到閉合映射側環。
  2. **特徵尺寸跨度過大（Scale Disparity）**：毫米級本體伴隨密集 0.2~0.3mm 微小過渡圓角，導致局部 O-Grid 塊體 Aspect Ratio 嚴重爆炸、Jacobian 退化。
  3. **階梯軸台階未切分（Uncut Slice）**：小型 T-Nut 螺帽、台階插銷（tpin 2），環形突變交界面未做切塊前處理，無法生成閉合 Hex 方塊。

### 3. 使用者專屬 7 步 SOP 實踐閉環
* **步驟一**：1x1 AutoMesh，每個幾何獨立配置 Method 與 Sizing（Sheet 3.0mm, PCBA 1.5mm, Solid 2.0mm）。
* **步驟二**：Go to Mesh Controls，依組件 Part 建立資料夾歸類，維持外部游離項為 0。
* **步驟三**：分區隔離劃分（當前分區 Show、其餘 Hide）；預設 MultiZone，只有失敗或超時（3 分鐘）才單件自愈改為 Tetra；完成後全域 Show 並以 `CollapseToLevel(2)` 摺疊樹。
* **步驟四**：Interface Check 單元干涉檢查。
* **步驟五**：TimeStepCalc 單一物件計算全域最小時間步長 CFL。
* **步驟六 & 七**：針對 $\Delta t < 50\text{ ns}$ 之瓶頸幾何透過 MeshTuner 局部微調並循環達標。

---

## 二、 遇到的問題、Error Log、Root Cause 與解決對策 (8 大案例)

### 案例 1：Model Tree 外層游離孤立控制項
* **現象**：Model Tree 中 12 個資料夾整整齊齊，但底下突兀地露出一個 `Tet_Component1\PDB_STANDOFF_GDZ1`。
* **Root Cause**：排障邏輯在刪除失敗的 MultiZone 並呼叫 `mesh.AddAutomaticMethod()` 重新建立 Tet 時，未將新物件移入 `Component1` 資料夾。
* **Solution**：動態建立控制項後立即呼叫 `folder.AddObject(ctrl)` 或重新封裝 `Tree.Group`，並透過檢查遍歷所有子項確保游離項恆為 0。

### 案例 2：`'AutomaticMethod' object has no attribute 'Id'`
* **Error Log**：`details = "'AutomaticMethod' object has no attribute 'Id'"`
* **Root Cause**：幾何核心物件才具備 `.Id`（如 `GeoBody.Id` 為整數），而 ACT DataModel 樹物件的唯一識別屬性為 `.ObjectId`。
* **Solution**：DataModel 物件唯一性識別統一改用 `item.ObjectId`。

### 案例 3：`MethodType.QuadTri` 枚舉不存在
* **Error Log**：`AttributeError: type object 'MethodType' has no attribute 'QuadTri'`
* **Root Cause**：ANSYS Mechanical ACT 中薄板若要使用 MultiZone Quad/Tri，其枚舉值依然是 `MethodType.MultiZone`，底層視對象為 Sheet 自動指派面網格。
* **Solution**：Solid 與 Sheet 一律統一使用 `MethodType.MultiZone`。

### 案例 4：Python 字串轉義反斜線匹配失敗
* **現象**：零件名稱帶反斜線（如 `Component1\tpin`），在多層字串格式化時 `\\\\` 轉義不一致，導致無法匹配目標控制項。
* **Solution**：控制項命名統一改用連字號或底線（如 `Tet_{folder}_{clean_name}`），並以幾何核心 `GeoBody.Id` 作為唯一索引。

### 案例 5：`'MechanicalDataModel' object has no attribute 'MeshData'`
* **Error Log**：`details = "'MechanicalDataModel' object has no attribute 'MeshData'"`
* **Root Cause**：`MeshData` 存在於 `Mesh` 物件層級下，直接從 `ExtAPI.DataModel` 存取會拋出屬性錯誤。
* **Solution**：修正存取路徑為 `ExtAPI.DataModel.Project.Model.Mesh.MeshData` 或 `mesh.MeshData`。

### 案例 6：Part 名稱前綴空格導致幾何映射遺漏
* **現象**：`TOP-COVER-GDZ` 的 Part 名稱在幾何樹中為 `" TOP-COVER-GDZ"`（前綴帶空格），字串直接比對時遺漏該零件下的 13 個幾何。
* **Solution**：所有名稱比對處均加上 `.strip()` 清除前後空白字符。

### 案例 7：網格劃分偽成功判定漏洞
* **現象**：`Body` 物件可能未實作 `Meshed` 屬性，若在腳本中使用 `else: mesh_ok = True` 會掩蓋劃分失敗。
* **Solution**：改採底層客觀物理指標 `mesh.MeshData.MeshRegionById(geo_body.Id).NodeCount > 0` 驗證真實網格生成。

### 案例 8：`b.GenerateMesh()` 阻塞式呼叫與超時保護
* **現象**：在 IronPython 腳本內部，`b.GenerateMesh()` 為同步阻塞式呼叫，若底層演算法死鎖，腳本無法在內部達成 Preemptive 中斷。
* **Solution**：內部腳本在調用結束後記錄耗時，超過 180 秒即觸發降級重劃；外部則可依賴 PyMechanical 進程層級進行超時防護。

---

## 三、 四層幾何分類判斷式 (Four-Tier Classifier 成果)

| 層級 | 判定維度 | 規則條件 | 決策結果 |
| :--- | :--- | :--- | :--- |
| **Level 1** | 幾何型態 | `"Sheet" in BodyType` | `MultiZone Quad/Tri` |
| **Level 2** | 先驗可掃掠豁免 | 純零件名含 `PCB`, `PCBA`, `BACKPLANE`, `HS_` 等 | `MultiZone Solid` |
| **Level 3** | 拓撲複雜度 (候選) | `Faces > 40` 或 `Edges > 100` | `AllTriAllTet` |
| **Level 4** | 機構語義特徵 (候選) | 純零件名含 `T-NUT`, `PLUG`, `LATCH`, `RAIL`, `PIN 2` 等 | `AllTriAllTet` |
| **Level 5** | 預設常規實體 | 其餘規則柱狀、壓塊、標準扣件 | `MultiZone Solid` |

*當前狀態：Level 3 & 4 記錄歸檔於 `docs/mesh_classification_heuristics.md`，暫不啟用（維持全幾何預設 MultiZone，劃分失敗才動態降級）。*
