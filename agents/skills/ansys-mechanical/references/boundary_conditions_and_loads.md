# ANSYS Mechanical 邊界條件與載荷 (Boundary Conditions & Loads) 指南

本手冊提供結構邊界約束、外力載荷、壓力、遠程載荷以及螺栓預緊力（Bolt Pretension）三步載荷法之標準 ACT 程式碼規範與防剛體位移實務。

---

## 一、邊界約束 (Supports)

邊界條件需掛載於特定分析系統（`Model.Analyses[i]`）下，並透過 `.Location` 指定幾何面、邊或 Named Selection。

### 1. 固定約束 (Fixed Support)
拘束全部 6 個自由度（平移與旋轉為 0）：
```python
analysis = Model.Analyses[0]
fixed_support = analysis.AddFixedSupport()
fixed_support.Name = "機座固定底面"
fixed_support.Location = ExtAPI.DataModel.GetObjectsByName("NS_BASE_FIXED_FACES")[0]
```

### 2. 無摩擦支撐 (Frictionless Support)
法向位移約束為 0，切向允許自由滑移。常作為對稱邊界（Symmetry Plane）或滑軌接觸約束：
```python
fric_support = analysis.AddFrictionlessSupport()
fric_support.Name = "對稱面法向約束"
fric_support.Location = ExtAPI.DataModel.GetObjectsByName("NS_SYMMETRY_FACES")[0]
```

### 3. 分量位移約束 (Displacement)
精確控制各軸平移自由度（可固定為 0、給定強制位移值，或保留 Free）：
```python
disp = analysis.AddDisplacement()
disp.Name = "導軌導向位移"
disp.Location = ExtAPI.DataModel.GetObjectsByName("NS_GUIDE_FACES")[0]

# X 軸允許自由滑動 (Free: 不做設定)
# Y 與 Z 軸限制為 0
disp.YComponent.Output.SetDiscreteValue(0, Quantity("0 [m]"))
disp.ZComponent.Output.SetDiscreteValue(0, Quantity("0 [m]"))
```

### 4. 遠程位移 (Remote Displacement)
可同時約束 3 個平移與 3 個旋轉自由度，並指定旋轉中心點座標與行為（Rigid / Deformable）：
```python
rem_disp = analysis.AddRemoteDisplacement()
rem_disp.Location = ExtAPI.DataModel.GetObjectsByName("NS_SHAFT_END_FACES")[0]
rem_disp.Behavior = Ansys.Mechanical.DataModel.Enums.LoadBehavior.Deformable
rem_disp.RotationZ.Output.SetDiscreteValue(0, Quantity("0 [rad]"))
```

---

## 二、外力與表面載荷 (Loads)

### 1. 表面壓力 (Pressure)
作用於垂直表面，正值為壓縮（壓向內部），負值為拉伸：
```python
pressure = analysis.AddPressure()
pressure.Name = "腔體內壁水壓"
pressure.Location = ExtAPI.DataModel.GetObjectsByName("NS_INTERNAL_CAVITY")[0]
pressure.AppliedBy = Ansys.Mechanical.DataModel.Enums.LoadAppliedBy.SurfaceEffect
pressure.Magnitude.Output.SetDiscreteValue(0, Quantity("2.5 [MPa]"))
```

### 2. 集中力 / 向量力 (Force)
推薦依分量（Components）精準施加三軸向量力：
```python
force = analysis.AddForce()
force.Name = "耳板懸掛載荷"
force.Location = ExtAPI.DataModel.GetObjectsByName("NS_LUG_HOLE_FACES")[0]
force.DefineBy = Ansys.Mechanical.DataModel.Enums.LoadDefineBy.Components
force.XComponent.Output.SetDiscreteValue(0, Quantity("0 [N]"))
force.YComponent.Output.SetDiscreteValue(0, Quantity("-15000 [N]"))  # -15 kN
force.ZComponent.Output.SetDiscreteValue(0, Quantity("0 [N]"))
```

### 3. 遠程力 (Remote Force)
將力施加於實體外部空間座標點，自動將等效力與偏心彎矩耦合傳遞至幾何面：
```python
rem_force = analysis.AddRemoteForce()
rem_force.Location = ExtAPI.DataModel.GetObjectsByName("NS_FLANGE_FACE")[0]
rem_force.XLocation = Quantity("0.0 [m]")
rem_force.YLocation = Quantity("0.2 [m]")  # 偏心 200 mm
rem_force.ZLocation = Quantity("0.0 [m]")
rem_force.DefineBy = Ansys.Mechanical.DataModel.Enums.LoadDefineBy.Components
rem_force.YComponent.Output.SetDiscreteValue(0, Quantity("-5000 [N]"))
```

### 4. 全域重力加速度 (Standard Earth Gravity)
```python
gravity = analysis.AddStandardEarthGravity()
gravity.Direction = Ansys.Mechanical.DataModel.Enums.GravityOrientationType.NegativeYAxis
```

---

## 三、螺栓預緊力 (Bolt Pretension) 三步載荷法

螺栓連接在工程分析中必須採用多載荷步（Multi-step Loading）準確模擬裝配與工作狀態：

> [!IMPORTANT]
> **螺栓預緊標準三步流程**：
> - **Step 1 (裝配預緊)**：施加螺栓預緊拉力（如 $12000 \text{ N}$）。
> - **Step 2 (螺栓鎖死)**：設定為 `Lock`（鎖定長度），固定螺栓相對變形。
> - **Step 3 (外力加載)**：施加工作載荷（外部壓力/力），螺栓以鎖死剛度承受外力分配。

```python
# 新增螺栓預緊力物件
bolt = analysis.AddBoltPretension()
bolt.Location = ExtAPI.DataModel.GetObjectsByName("NS_BOLT_CYLINDER_FACES")[0]

# Step 1: 預緊裝配 (Load)
bolt.PreloadType = Ansys.Mechanical.DataModel.Enums.PreloadType.Load
bolt.Preload.Output.SetDiscreteValue(0, Quantity("12000 [N]"))

# Step 2: 鎖死狀態 (Lock)
bolt.SetPreloadType(1, Ansys.Mechanical.DataModel.Enums.PreloadType.Lock)

# Step 3: 工作狀態 (維持鎖死)
bolt.SetPreloadType(2, Ansys.Mechanical.DataModel.Enums.PreloadType.Lock)
```

---

## 四、剛體位移防範與約束完整性檢查

在求解靜態結構時，若約束不完全會導致剛度矩陣奇異（主元為零）。
- **完整約束判定**：平移 $T_x, T_y, T_z$ 與轉動 $R_x, R_y, R_z$ 必須全部受到直接拘束或接觸阻抗。
- **浮動裝配體防護**：可於求解控制開啟 `Weak Springs = True`（弱彈簧）輔助診斷剛體運動方向。

---

## 五、MCP 工具對照

| ACT 原生 API | ANSYS MCP 工具 | 用途描述 |
|---|---|---|
| `analysis.AddFixedSupport()` | `add_fixed_support` | 新增固定支撐邊界條件 |
| `analysis.AddForce()` | `add_force` | 新增外力載荷 |
| `analysis.AddPressure()` | `add_pressure` | 新增表面壓力 |
| `analysis.AddDisplacement()` | `add_displacement` | 新增分量位移約束 |
| `analysis.AddStandardEarthGravity()` | `add_standard_gravity` | 施加標準重力加速度 |
