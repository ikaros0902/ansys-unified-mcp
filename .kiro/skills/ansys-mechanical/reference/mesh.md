# ANSYS Mechanical 網格劃分與品質控制指南

本手冊提供 ANSYS Mechanical 網格控制之標準 ACT 程式碼規範，涵蓋全域網格設定、局部尺寸控制（Sizing）、特徵劃分方法（Method）、薄壁結構多層單元要求，以及網格品質量化評估標準。

---

## 一、全域網格控制與產生

全域網格控制透過 `Model.Mesh` 物件管理：

```python
mesh = Model.Mesh

# 1. 切換啟動網格樹狀節點
mesh.Activate()

# 2. 全域物理場與單元階數偏好
mesh.PhysicsType = Ansys.Mechanical.DataModel.Enums.MeshPhysicsType.Mechanical
mesh.ElementOrder = Ansys.Mechanical.DataModel.Enums.ElementOrder.ProgramControlled  # 結構推薦高階單元 (Quadratic)

# 3. 全域單元尺寸設定 (公尺或 Quantity)
mesh.ElementSize = Quantity("0.005 [m]")  # 5 mm

# 4. 捕捉特徵與細部消除 (Curvature & Proximity)
mesh.UseCurvature = True
mesh.UseProximity = True
mesh.CurvatureNormalAngle = Quantity("18 [deg]")
mesh.ProximityNumCellsAcrossGap = 3

# 5. 觸發網格重新生成
mesh.GenerateMesh()
print("全域網格生成完成！節點數: {}, 單元數: {}".format(mesh.Nodes, mesh.Elements))
```

---

## 二、局部尺寸控制 (Mesh Sizing)

局部 Sizing 可精確綁定至實體（Body）、面（Face）或邊線（Edge）：

```python
# 1. 局部邊線劃分 (指定等分數或邊線單元尺寸)
edge_ns = ExtAPI.DataModel.GetObjectsByName("NS_HOLE_EDGES")[0]
edge_sizing = mesh.AddSizing()
edge_sizing.Name = "孔緣特徵加密"
edge_sizing.Location = edge_ns
edge_sizing.Type = Ansys.Mechanical.DataModel.Enums.SizingType.NumberOfDivisions
edge_sizing.NumberOfDivisions = 24
edge_sizing.Behavior = Ansys.Mechanical.DataModel.Enums.SizingBehavior.Hard  # Hard 強制鎖定

# 2. 局部面尺寸控制 (指定單元尺寸與漸變率)
face_ns = ExtAPI.DataModel.GetObjectsByName("NS_CRITICAL_FACES")[0]
face_sizing = mesh.AddSizing()
face_sizing.Name = "接觸面局部細化"
face_sizing.Location = face_ns
face_sizing.Type = Ansys.Mechanical.DataModel.Enums.SizingType.ElementSize
face_sizing.ElementSize = Quantity("0.001 [m]")  # 1 mm
face_sizing.GrowthRate = 1.15                    # 控制過渡膨脹率 <= 1.2
```

---

## 三、網格劃分方法 (Mesh Methods)

依幾何拓撲特徵指定最佳單元劃分方法：

```python
body_ns = ExtAPI.DataModel.GetObjectsByName("NS_MAIN_BODY")[0]
method = mesh.AddAutomaticMethod()
method.Location = body_ns

# 可選劃分方法 (MethodType):
# - MethodType.AllTriAllTet: 全四面體 (適用於複雜有機形狀/鑄造件)
# - MethodType.HexDominant: 六面體主導 (適用於大體積實體)
# - MethodType.Sweep: 掃掠網格 (適用於具備規則導動方向的拉伸/旋轉體)
# - MethodType.MultiZone: 多區域六面體網格 (適用於複雜裝配塊)
method.Method = Ansys.Mechanical.DataModel.Enums.MethodType.HexDominant
```

### 薄壁板金件的「厚度方向多層」強制規範
> [!IMPORTANT]
> 嚴禁對薄壁零件在厚度方向僅劃分 1 層一階四面體單元（會因**剪切自鎖 Shear Locking** 導致剛度虛高 $200\% \sim 500\%$）。
> - **最佳實踐 A**：透過 SpaceClaim 抽取中面，改用薄殼單元（Shell Element）分析。
> - **最佳實踐 B**：若維持實體單元，必須採用掃掠（Sweep）或薄掃掠（Thin Swept），強制設定厚度方向劃分 $\ge 3$ 層高階六面體單元（SOLID186）。

```python
# 掃掠單元厚度方向層數控制範例
sweep_method = mesh.AddAutomaticMethod()
sweep_method.Location = body_ns
sweep_method.Method = Ansys.Mechanical.DataModel.Enums.MethodType.Sweep
sweep_method.SweepNumberDivisions = 3  # 厚度方向劃分 3 層單元
```

---

## 四、網格品質量化評估標準與門檻

網格生成後，必須立即計算幾何畸變度指標。嚴禁在劣質網格下進行有限元求解：

| 評估指標 | 優秀 (Excellent) | 良好 (Good) | 可接受 (Acceptable) | 警示 (Warning) | 嚴禁求解 (Fail) |
|---|---|---|---|---|---|
| **歪斜度 (Skewness)** | $0.0 \sim 0.25$ | $0.25 \sim 0.50$ | $0.50 \sim 0.75$ | $0.75 \sim 0.85$ | $> 0.85$（非線性禁止）<br>$> 0.95$（全面禁止） |
| **正交品質 (Orthogonal)** | $0.9 \sim 1.0$ | $0.7 \sim 0.9$ | $0.3 \sim 0.7$ | $0.15 \sim 0.3$ | $< 0.15$（非線性禁止）<br>$< 0.05$（全面禁止） |
| **長寬比 (Aspect Ratio)** | $1.0 \sim 3.0$ | $3.0 \sim 10.0$ | $10.0 \sim 20.0$ | $20.0 \sim 50.0$ | $> 100.0$（嚴重自鎖） |

### 網格統計資訊讀取 ACT 範例
```python
mesh_data = Model.Analyses[0].MeshData  # 或 Model.Mesh
print("=== 網格統計數據 ===")
print("單元總數: {}".format(mesh.Elements))
print("節點總數: {}".format(mesh.Nodes))

# 透過 MeshStatistics 讀取品質指標極值與平均值
stats = mesh.MeshStatistics
print("最小正交品質: {:.4f}".format(stats.MinOrthogonalQuality))
print("最大歪斜度:   {:.4f}".format(stats.MaxSkewness))
print("平均正交品質: {:.4f}".format(stats.AverageOrthogonalQuality))

if stats.MaxSkewness > 0.85 or stats.MinOrthogonalQuality < 0.15:
    print("[品質警報] 檢測到劣質單元超標，請加密局部特徵或調整過渡方法！")
else:
    print("[品質驗證通過] 網格品質符合高精度求解標準。")
```

---

## 五、MCP 工具對照

| ACT API | ANSYS MCP 工具 | 用途描述 |
|---|---|---|
| `Mesh.ElementSize = ...` | `set_mesh_element_size` | 設定全域單元尺寸 |
| `Mesh.GenerateMesh()` | `generate_mesh` | 執行網格劃分與更新 |
| `Mesh.Nodes / Elements` | `get_mesh_statistics` | 讀取模型單元與節點數量 |
