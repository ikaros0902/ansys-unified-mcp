# 水密幾何網格劃分與 Poly-Hexcore 技術手冊 (watertight_meshing.md)

本手冊規範基於 ANSYS Fluent Watertight Geometry Workflow (WGW) 的自動化體網格劃分流程，詳述 Mosaic (Poly-Hexcore) 核心技術、邊界層稜柱層計算與網格品質驗收標準。

---

## 一、WGW 工作流核心 Task 鏈條

Fluent Meshing 的水密幾何工作流依序包含 9 大核心任務節點：

```text
[1. Import Geometry] 
        ↓
[2. Add Local Sizing] 
        ↓
[3. Generate the Surface Mesh] 
        ↓
[4. Describe Geometry] 
        ↓
[5. Apply Share Topology] 
        ↓
[6. Update Boundaries] 
        ↓
[7. Update Regions] 
        ↓
[8. Add Boundary Layers] 
        ↓
[9. Generate the Volume Mesh]
```

### 各任務節點參數設定標準

| 任務節點名稱 | 關鍵設定參數 | 工程推薦值 | 說明 |
|---|---|---|---|
| `Import Geometry` | `FileName`, `LengthUnit` | `"in"` 或 `"mm"` | 幾何匯入需校核單位，防止尺度縮放錯誤 |
| `Add Local Sizing` | `CurvatureNormalAngle` | `18.0` deg | 圓弧面曲率解析法向夾角 |
| `Add Local Sizing` | `ProximityNumCells` | `3` | 狹窄間隙流道至少佈置單元層數 |
| `Generate Surface Mesh`| `MinSize`, `MaxSize` | 依特徵尺度定義 | 表面三角形網格極限尺寸 |
| `Generate Surface Mesh`| `GrowthRate` | `1.20` | 表面網格由密到疏的膨脹率（嚴禁 $> 1.3$） |
| `Describe Geometry` | `SetupType` | Fluid only / CHT | 指定純流體域或固體共軛熱傳域 |
| `Apply Share Topology` | `Tolerance` | 預設自動匹配 | 多體域交界面執行共節點壓印 |
| `Update Boundaries` | `BoundaryFlowType` | 自動推斷 | 依據 CAD 命名選擇識別 inlet/outlet/wall |
| `Update Regions` | `RegionType` | `fluid` / `solid` | 確認各封閉腔體之計算介質類型 |
| `Add Boundary Layers` | `NumberOfLayers` | `5` ~ `15` | 壁面邊界層稜柱層層數 |
| `Add Boundary Layers` | `TransitionRatio` | `0.272` | 第一層體單元與最後一層稜柱層厚度過渡比 |
| `Add Boundary Layers` | `GrowthRate` | `1.20` | 邊界層法向等比遞增率（建議 $\le 1.2$） |
| `Generate Volume Mesh` | `VolumeFill` | `"poly-hexcore"` | 啟用 Mosaic 六面體-多面體混合填充技術 |
| `Generate Volume Mesh` | `HexMaxCellLength` | 表面 MaxSize 等值 | 核心正交六面體之最大單元邊長 |

---

## 二、Mosaic (Poly-Hexcore) 核心技術架構

### 1. 空間填充拓撲結構
- **內部核心區 (Hexcore)**：以高精度八叉樹 (Octree) 笛卡爾坐標生成純正交六面體單元，單元正交品質接近 1.0，顯著降低流體主動量方向的數值假擴散。
- **近壁邊界層 (Prism Layers)**：在幾何邊界精準生成四邊形/三稜柱層，精確捕捉剪切應力與溫度梯度。
- **過渡緩衝區 (Mosaic Polyhedral)**：利用 Ansys Mosaic 專利演算法，在六面體與稜柱層交界處以共形多面體單元無縫連接，完全取代傳統易畸變的高長寬比四面體。

### 2. 工程效益
- 單元數量相較純四面體網格減少 **40% ~ 60%**。
- 求解記憶體佔用顯著降低，求解收斂速度提升 2~3 倍。
- 邊界層過渡處的正交品質通常保證在 0.25 以上。

---

## 三、邊界層第一層高度 ($y_1$) 計算指引

為滿足 $y^+$ 目標，首層網格法向高度 $y_1$ 需依平版或管流邊界層理論估算：

1. **雷諾數計算**：$Re = \frac{\rho U L}{\mu}$
2. **壁面摩擦係數 ($C_f$)**：
   - 湍流估算：$C_f \approx 0.0592 Re^{-0.2}$
3. **壁面剪切應力 ($\tau_w$) 與摩擦速度 ($u_\tau$)**：
   $$\tau_w = \frac{1}{2} C_f \rho U^2, \quad u_\tau = \sqrt{\frac{\tau_w}{\rho}}$$
4. **第一層網格厚度 ($y_1$)**：
   $$y_1 = \frac{y^+ \mu}{\rho u_\tau}$$

---

## 四、網格品質驗收紅線

在將網格切換至求解器 (`meshing.switch_to_solver()`) 前，必須強制校核下列指標：

```text
+----------------------------+-----------+-----------+-----------+
| 檢驗指標                   | 綠燈放行  | 黃燈觀察  | 紅燈攔截  |
+----------------------------+-----------+-----------+-----------+
| 最小正交品質 (Min Ortho)   | >= 0.20   | 0.15~0.20 | < 0.15    |
| 最大歪斜度 (Max Skewness)  | <= 0.80   | 0.80~0.85 | > 0.85    |
| 最大長寬比 (Aspect Ratio)  | < 50      | 50~100    | > 100     |
| 負體積單元 (Negative Volume)| 0         | 0         | > 0 (致命)|
+----------------------------+-----------+-----------+-----------+
```

---

## 五、PyFluent WGW 自動化腳本模式

```python
import ansys.fluent.core as pyfluent

meshing = pyfluent.launch_fluent(mode="meshing", precision="double", processor_count=4)
wf = meshing.workflow
wf.InitializeWorkflow(WorkflowType="Watertight Geometry")

# 1. 匯入幾何
wf.TaskObject["Import Geometry"].Arguments.set_state({"FileName": "elbow.pmdb", "LengthUnit": "in"})
wf.TaskObject["Import Geometry"].Execute()

# 2. 局部尺寸與表面網格
wf.TaskObject["Add Local Sizing"].Execute()
wf.TaskObject["Generate the Surface Mesh"].Arguments.set_state({
    "CFDSurfaceMeshControls": {"MinSize": 0.05, "MaxSize": 0.3, "GrowthRate": 1.2}
})
wf.TaskObject["Generate the Surface Mesh"].Execute()

# 3. 幾何描述
wf.TaskObject["Describe Geometry"].Arguments.set_state({
    "SetupType": "The geometry consists of only fluid regions with no voids"
})
wf.TaskObject["Describe Geometry"].Execute()

# 4. 邊界與區域
wf.TaskObject["Update Boundaries"].Execute()
wf.TaskObject["Update Regions"].Execute()

# 5. 稜柱邊界層
wf.TaskObject["Add Boundary Layers"].Arguments.set_state({
    "NumberOfLayers": 4, "TransitionRatio": 0.272, "GrowthRate": 1.2
})
wf.TaskObject["Add Boundary Layers"].Execute()

# 6. Poly-Hexcore 體網格生成
gen_vol = wf.TaskObject["Generate the Volume Mesh"]
gen_vol.Arguments.set_state({
    "VolumeFill": "poly-hexcore",
    "VolumeFillControls": {"HexMaxCellLength": 0.3}
})
gen_vol.Execute()

# 7. 切換至求解器
solver = meshing.switch_to_solver()
```
