# 伺服器機箱網格劃分排障實戰範例 (Server Chassis Mesh Debugging Examples)

本目錄收錄 2026 年 9 月工程團隊針對大型高密度伺服器機箱結構進行網格劃分與排障之歷史實戰腳本。該批腳本展示了面對 100+ 複雜裝配體實體時，如何透過 PyMechanical gRPC 自動化實現分區劃分、視覺隔離、自動降級與狀態審核。

---

## 專案實戰背景 (Context & Problem Statement)

在複雜伺服器機箱（包含 **114 個幾何實體 Body**，如主底盤 `SM-BASEPAN-GDZ`、後背板 `Rear_wall`、前飾蓋 `SM-FRONT-COVER-GDZ`、硬碟籠 `E1S_CAGE_GDZ`、網路加速卡 `CX7`、`OCP`、電源分配模組 `PDB`、中置背板 `E1_Midplane`、頂蓋 `TOP-COVER-GDZ`、前框架 `1F-FRONT-END-GDZ` 等）的有限元前處理過程中，常面臨以下挑戰：

1. **全域劃分容易卡死 (Global Meshing Hangs)**：整機 114 個幾何體同時生成網格容易因小特徵、非流形邊或接觸面微小間隙導致網格生成器長時間無回應。
2. **六面體掃掠失敗率高 (MultiZone Sweep Failures)**：衝壓件、彎折處及細部開孔往往無法以 MultiZone 成功劃分六面體核心網格。
3. **模型樹控制項雜亂 (Tree Clutter & Invalid Scoping)**：數十個網格方法（Mesh Methods）與局部尺寸（Sizing）若未依資料夾歸類，容易產生孤立控制項（Lone Controls）或無效設定（UnderDefined / Invalid）。
4. **圖形視窗刷新負載 (Graphics Overhead)**：全模型可視狀態下反覆重新劃分會消耗大量顯存與 CPU 繪圖資源。

---

## 核心解決策略與架構 (Engineering Strategies)

本批除錯腳本確立了以下四大自動化處置原則：

1. **分區隔離劃分 (Partitioned Meshing & Visual Isolation)**：
   - 依模型樹資料夾（Folder Partitions）逐一劃分，當處理特定分區時，腳本自動將其餘部件設為隱藏（`Visible = False`），劃分完成後再批次恢復，大幅降低圖形繪製負擔。
2. **自動降級機制 (Automatic Fallback to AllTriAllTet)**：
   - 優先套用高品質 MultiZone 六面體網格劃分。
   - 若特定部件劃分失敗或耗時超過門檻（例如 > 180 秒），腳本自動將該部件網格方法降級為四面體（`MethodType.AllTriAllTet`）並重新劃分，確保自動化流程不中斷。
3. **客觀節點數驗證 (Objective Node-Count Verification)**：
   - 不依賴介面顯示狀態，而是透過 `ExtAPI.DataModel.MeshData.MeshRegionById(geo_body.Id)` 讀取 `region.NodeCount > 0`，客觀驗證每一實體是否真正具備有效網格。
4. **模型樹自動整潔化 (Model Tree Hygiene)**：
   - 自動將孤立控制項移入對應分區資料夾，並將整體模型樹自動折疊收攏至第二層級（`th.CollapseToLevel(2)`），提供乾淨的工程介面。

---

## 腳本清單與職責詳解 (Script Inventory)

目錄下 12 個除錯腳本之具體職責與應用場景如下：

| 腳本名稱 | 核心職責 | 關鍵方法 / 特性 |
|---|---|---|
| `inspect_mesh_setup.py` | 網格控制項健康檢查 | 掃描所有 Mesh Children，檢測標記 `?`、`UnderDefined` 或 `Invalid` 的控制項，並檢查是否有重複 Scoping 衝突。 |
| `check_stuck_geometry.py` | 診斷卡死或未劃分幾何體 | 遍歷所有 Body，確認其 `Elements` 與幾何狀態，精確定位阻礙網格劃分的卡死部件。 |
| `clean_and_collapse_tree.py` | 模型樹整理與顯示復原 | 確保全機 114 個 Body 100% 恢復可視（`Visible = True`），將孤立控制項（如 `Tet_Component1\\PDB_STANDOFF_GDZ1`）重整歸組至 `Component1` 資料夾，並將模型樹收攏至 Level 2。 |
| `rebuild_step1.py` | 階段一步驟：基礎重構 | 清除衝突的歷史網格設定，重新依伺服器主要模組建立基本網格控制架構。 |
| `rebuild_step1_and_step2.py` | 階段一與階段二聯合重構 | 連續執行主結構與次結構網格重建，配置 MultiZone 參數與關鍵區域尺寸。 |
| `reset_methods_to_multizone.py` | 批次重設為 MultiZone | 針對特定部件（如非 `1F-FRONT-END-GDZ` 部件）批次套用 MultiZone 劃分法，以爭取最高六面體網格比例。 |
| `run_step3_partitioned_mesh.py` | 階段三分區網格劃分器 | 循序巡迴各部件資料夾（`SM-BASEPAN-GDZ`, `Rear_wall`, `CX7`, `OCP` 等）進行劃分，記錄耗時與劃分狀態。 |
| `step3_partition_mesh_and_fallback.py` | 核心分區劃分與超時自動降級 | 具備完整超時防護與自動降級邏輯：MultiZone 劃分失敗或超過 180 秒時，自動轉為四面體並二次重試，最終產出未劃分部件客觀清單（`unmeshed_count`）。 |
| `stepped_mesher_with_visibility.py` | 步進式視覺隔離網格劃分 | 結合圖形視窗 `Graphics.Redraw()` 與動態顯示控制，實現劃分進度實時視覺反饋。 |
| `finish_remaining_parts_robust.py` | 強健性掃尾劃分 | 針對前幾階段遺留之零節點殘留部件，進行專門的二次強制作業與四面體補劃分。 |
| `test_mech_direct.py` | Mechanical gRPC 基礎通訊測試 | 快速檢驗本機連接埠 10000 上的 Mechanical 連線、專案名稱與基本 API 可通性。 |
| `test_tet_meshing.py` | 四面體網格劃分單體驗證 | 針對單一極端複雜幾何部件，獨立測試四面體網格生成器極限與記憶體佔用。 |

---

## 典型調用方式 (Usage & Prerequisites)

本批腳本設計為透過 `ansys-mechanical-core` (PyMechanical) 直連 Mechanical 實體：

1. **前置需求**：
   - 啟動 ANSYS Mechanical 並開啟 gRPC 服務（預設埠號：`10000`）。
   - 本機 Python 環境已安裝 `ansys-mechanical-core`。

2. **執行範例**：
   ```powershell
   # 1. 驗證 gRPC 連線
   python examples/mesh_debug/test_mech_direct.py

   # 2. 檢查現有網格設定與未定義控制項
   python examples/mesh_debug/inspect_mesh_setup.py

   # 3. 執行分區劃分與自動降級排障流程
   python examples/mesh_debug/step3_partition_mesh_and_fallback.py

   # 4. 恢復全機可視性與整頓模型樹
   python examples/mesh_debug/clean_and_collapse_tree.py
   ```
