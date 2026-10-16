# 進階局部控制與方法 GUI 操作要點 (advanced_controls_gui_operations.md)

本手冊補充 12 項網格局部控制與劃分方法在 ANSYS Meshing GUI 中的操作邏輯、選單路徑與常見陷阱，與既有的 ACT 程式碼範例（`local_controls_and_washers.md`、`mesh_methods_and_geometry_healing.md`）互補：那兩份給程式碼，本檔給操作邏輯與選單路徑背後的原理。來源：ANSYS Meshing 官方教學課程（Session 1-5 系列），已逐題查證並附對應 Session。

---

## 一、Sphere of Influence（Session 3.1） — 選取方式決定 Type 自動切換

`Mesh → Insert → Sizing` 之後，`Type` 下拉選單是否出現 `Sphere of Influence` 取決於選取的幾何：選取 Vertex 時，`Type` 會**自動**切換為 `Sphere of Influence` 且不可改回其他選項；選取 Edge/Face/Body 則維持 `Element Size` 可選。影響範圍只在球體內部生效，球外仍遵循全域 Sizing，交界處依全域 `Growth Rate` 過渡。

## 二、Contact Sizing（Session 4.1） — CAD 端前提條件

使用前提：模型必須由兩個以上**獨立實體**（Independent Bodies）組成，CAD 端（SpaceClaim/DesignModeler）**不可以**用 `Form New Part` 把這些實體合併成單一 Part——合併後軟體不會自動產生 Contact Region，`Contact Sizing` 就無法選取或生效。匯入 ANSYS Meshing 後軟體會自動在獨立實體交界處偵測並建立可選的 Contact Region。

## 三、Refinement（Session 4.2） — 僅接受整數 1/2/3

`Mesh → Insert → Refinement` 的 `Refinement Factor` 只能填 `1`、`2` 或 `3`，數字越大網格切割越細。這個參數會讓單元與節點數量倍增，設為 `3` 套用在大面積曲面時容易讓記憶體暴增，使用前先評估範圍大小。

## 四、Face Meshing（Session 4.3） — 頂點指定操作路徑

結構化面網格需要軟體能辨識出邊界的拓樸角點。對五邊形、六邊形等非標準四邊形曲面，要在 `Advanced` 區塊手動指定三種頂點類型（`Specified Ends`/`Specified Sides`/`Specified Corners`）；三者各自的發散網格線數與 N+4 配對法則定義見 [`local_controls_and_washers.md`](local_controls_and_washers.md) 第四節，本節只補充操作上的陷阱：未按配對比例指定會導致拓樸解不出來、Mapped Mesh 生成失敗，且軟體不會明確指出是哪個頂點配置錯誤，需要逐一減少 Corner 數量排查。

## 五、Mesh Copy（Session 4.4） — Source/Target 幾何必須完全一致

`Mesh → Insert → Mesh Copy` 要求 `Source Geometry`（已有理想網格的來源）與 `Target Geometry`（要套用相同網格的目標）在拓樸形狀、尺寸、頂點數量上**完全相同**。選取時必須挑選兩者方位對應的同一特徵面（例如都選上端面）。任何微小差異（尺寸、倒角、邊線數量不符）都會讓 Mesh Copy 直接報錯拒絕執行。適用情境：陣列零件、對稱幾何、裝配體中完全同規格的組件。

## 六、Match Control（Session 4.5） — 旋轉軸座標系陷阱

`Mesh → Insert → Match Control` 用於週期性對稱面（Periodic Faces）生成完全一致的面網格，常見於扇形葉片通道、弧形管道。設定時要指定 `High Geometry`/`Low Geometry` 兩組對應面，並設定 `Axis of Rotation`。**關鍵陷阱**：若直接選用預設的全域座標系（Global Coordinate System），且其 Z 軸不是模型真實的旋轉軸，軟體會直接報錯無法生成網格。必須新建一個自訂座標系，把 Z 軸重新定向為實際旋轉軸方向（例如選內曲面為基準，把全域 Y 軸定義為新座標系的 Z 軸），再回到 Match Control 選用這個新座標系。

## 七、Pinch Control（Session 4.6，另見 Meshing Complex Geometry 課程） — Tolerance 雙重限制（補充既有定義）

`Master Geometry`/`Slave Geometry` 的定義見 [`mesh_methods_and_geometry_healing.md`](mesh_methods_and_geometry_healing.md) 第二節。本節補充該文件未提到的 `Tolerance` 另一側限制：**Tolerance 必須同時滿足兩個條件**，不是只有「小於局部網格尺寸」這一個方向：

1. 必須大於欲消除的幾何縫隙/短邊實際長度（太小會因搜尋不到目標而報錯，`mesh_methods_and_geometry_healing.md` 建議值 20~30% 局部單元尺寸是指上界，下界取決於實際縫隙大小）。
2. 必須小於該區域的局部網格單元尺寸（太大會過度拉扯周圍正常幾何邊界，造成變形或扭曲）。

也可以用 `Create Pinch Controls`（自動搜尋模式）讓軟體自動掃描整個模型找出可捏合的候選項，再手動確認要套用哪些。

## 八、Inflation（Session 1.5 全域設定、Session 4.7 局部設定） — 三種控制模式的參數定義

| 模式 | 核心參數 | 說明 |
|---|---|---|
| **Total Thickness** | `Maximum Thickness`、`Number of Layers`、`Growth Rate` | 已知邊界層總厚度估算值時使用，直接限制整體膨脹層佔據空間 |
| **First Layer Thickness** | `First Layer Height`、`Maximum Layers`、`Growth Rate` | CFD 近壁面 Y+ 控制的核心工具，依紊流模型精確指定第一層網格高度 |
| **Smooth Transition**（預設） | `Transition Ratio`、`Maximum Layers`、`Growth Rate` | 讓膨脹層最外層與內部四面體網格平滑過渡；`Transition Ratio` 是最外層膨脹層高度與緊鄰四面體高度的比值 |

**使用前提**：無法對已有 Mapped/Quadrilateral 網格的幾何直接套用自動 Inflation，必須先把該幾何的 Method 改為 `Tetrahedrons`。

**CFD Y+ 配合**：Inflation 的 `First Layer Height` 要配合目標 Y+ 反算，Y+ 分級門檻與黏性底層/緩衝層禁區/對數律區判斷見 `ansys-fluent/references/fluent_judgment.md`，本檔不重複定義數值。

## 九、Virtual Topology（Session 1.3 概念、Meshing Complex Geometry 課程實作） — 法向角度限制

`Model → Insert → Virtual Topology` 的 `Merge Faces`/`Merge Edges` 只能合併**空間相鄰、且法線向量相近**的曲面。嘗試合併角度落差過大（跨越劇烈轉折）的曲面集合會直接報錯（原因是被選取面集合的平均法向量落差過大）。正確做法是分區、逐組選取角度相近的碎面局部合併，不要一次框選整個複雜模型的所有曲面。過度合併還會影響後續邊界條件選取——若把不同功能區域的曲面都合併成一個虛擬面，後續在 Fluent/Mechanical 中會無法單獨選取該局部區域設定邊界條件。

## 十、Body Fitted Cartesian Mesh（Session 2.5） — Projection Factor 權衡

`Method` 選 `Body Fitted Cartesian` 後，`Projection Factor` 介於 0 到 1：

- `0`：維持完美規則的正六面體，正交品質極佳，但完全不貼合真實幾何曲面（例如圓柱表面會失真變形）。
- `1`：完全貼合真實幾何邊界與曲率，但在曲率較大或不同幾何體銜接處，網格會因過度拉扯而扭曲、品質下降。

若選 `Projection Factor = 1` 以保留真實外形，建議同時縮小 `Element Size`，用更密的網格緩解曲面銜接處的扭曲。這個方法與 Layered Tetrahedron 都屬於工程實務中較少使用的方法，優先建議用 MultiZone 或 Sweep。

## 十一、Layered Tetrahedron Mesh（Session 2.6） — 與 Adaptive Sizing 互斥

套用 `Layered Tetrahedron` 方法時，軟體會跳出錯誤：Adaptive Sizing 不能跟這個方法同時啟用。必須先到全域 `Mesh → Sizing` 把 `Use Adaptive Sizing` 手動改成 `No`，才能繼續設定 `Layer Height` 參數並生成網格。

## 十二、Structured Tetrahedral Mesh（Session 5）（圓管/連續曲面）— CAD 前置切割流程

對圓管、圓柱這類連續曲面幾何，直接套用 Sweep/MultiZone/Face Meshing 通常無法解出結構化拓樸，常見錯誤或退化成非結構化四面體。要生成結構化六面體網格（O-grid），需在 CAD 端（DesignModeler/SpaceClaim）先完成拓樸切割：

1. 在圓管端面中心繪製矩形草圖。
2. `Extrude`，`Operation` 改為 `Slice Material`，拉伸長度貫穿整個圓管，產生「中央矩形柱體」與「外圍圓管主體」兩個獨立實體。
3. （可選）用 `Slice` 配合 YZ/XZ 基準平面，把外圍區域再切成 4 個象限（X 形十字分區），只切外圍、保持中央矩形柱體完整。
4. 選取所有切割產生的 Body，右鍵 `Form New Part`——這一步是關鍵，確保分區交界面共享拓樸（Shared Topology），讓後續網格節點連續不產生斷層。
5. 進 ANSYS Meshing：對該 Part 套用 `Sweep` 或 `MultiZone`；`Face Meshing` 同時選取端面的矩形面與外圍弧形面；在中央矩形的 4 條邊插入 `Edge Sizing`，`Type` 設 `Number of Divisions`、`Behavior` 設 `Hard`。

這個流程同樣適用於需要徑向網格密度精確控制的其他連續曲面幾何（如翼型 C-grid/O-grid），只是切割形狀依幾何特徵調整。
