---
name: 06-constraint-load
description: Shock dynamic boundary conditions and exact company standard LS-DYNA Analysis Settings.
---

# Session 06: Constraint, Shock Load & Standard Analysis Settings

## Objective
Configure dynamic drop/shock boundary conditions and apply the standard LS-DYNA Explicit Solver Analysis Settings (Memory, CPU, Unit System, Hourglass Type 6, Time Step Safety Factor).

## 1. Standard LS-DYNA Analysis Settings (標準求解參數矩陣)

| Category (類別) | Parameter (設定項) | Target Value (標準值) | LS-DYNA Keyword / Context |
| :--- | :--- | :--- | :--- |
| **Time Step** | Time Step Safety Factor | **0.9** | `*CONTROL_TIMESTEP` (TSSFAC = 0.9) |
| | Maximum Number Of Cycles | **10,000,000** (1e7) | `*CONTROL_TERMINATION` (MAXCYC) |
| | Automatic Mass Scaling | **No** | DT2MS = 0 (無非物理質量縮放) |
| | Number of Cases | **0** | Single Case |
| **CPU & Memory** | Memory Allocation | **Manual** | - |
| | Memory Value (MB) | **64,000 MB** (64 GB) | `MEMORY=64000M` |
| | Number Of CPUs | **8 Cores** | `NCPU=8` (SMP/MPP) |
| | Processing Type | **Program Controlled** | - |
| **Solver Controls** | Solver Type | **Program Controlled** | - |
| | Solver Precision | **double** (Double Precision) | `lsdyna_dp.exe` (消除累積數值截斷誤差) |
| | Solver Units | **Manual** | - |
| | Solver Unit System | **nmm** (mm, ton, s, N, MPa) | Standard CAE Unit System |
| | Explicit Solution Only | **Yes** | Pure Explicit Dynamics |
| **Hourglass Controls** | Hourglass Type | **Belytschko-Bindeman** | `*CONTROL_HOURGLASS` (IHQ = **6**) |
| | LS-DYNA ID | **6** | Assumed strain co-rotational |
| | Default Hourglass Coeff. | **0.1** | `QH = 0.1` |
| **Joint Controls** | Formulation | **Program Controlled** | Penalty / Lagrange Multiplier |
| **Output Controls** | Calculate Results At | **Equally Spaced Points** | `*DATABASE_BINARY_D3PLOT` |
| | Number of Output Points | **1000 Points** | $\Delta t_{\text{plot}} = \text{End Time} / 1000$ |

## 2. Dynamic Boundary Conditions (載荷與約束施加)
- **Velocity / Impact**:
  - Initial Velocity components: $\pm X$, $\pm Y$, $\pm Z$ (e.g. `Scr_Velocity_-Y_Bottom = 5420 mm/s` for 1.5m drop).
  - Half-Sine Prescribed Motion: `*BOUNDARY_PRESCRIBED_MOTION_RIGID` with curve table `*DEFINE_CURVE`.
- **Numerical Damping**:
  - Inject `*DAMPING_GLOBAL` (`VALDMP = 0.02 ~ 0.05`) to suppress high-frequency ringing without dampening primary impact impulse.

## 3. ExtAPI Automation Implementation
```python
analysis = Model.Analyses[0]
settings = analysis.AnalysisSettings

# Time Step Controls
settings.TimeStepSafetyFactor = 0.9
settings.MaximumNumberOfCycles = 10000000
settings.AutomaticMassScaling = False

# CPU and Memory Management
settings.MemoryAllocation = MemoryAllocationType.Manual
settings.MemoryValue = Quantity(64000, "MB")
settings.NumberOfCPUs = 8

# Solver Controls
settings.SolverPrecision = SolverPrecisionType.Double
settings.SolverUnitSystem = SolverUnitSystemType.Nmm
settings.ExplicitSolutionOnly = True

# Hourglass Controls (Type 6 Belytschko-Bindeman)
settings.HourglassType = HourglassType.BelytschkoBindeman
settings.DefaultHourglassCoefficient = 0.1

# Time History Output Controls (1000 points)
settings.CalculateResultsAt = CalculateResultsAtType.EquallySpacedPoints
settings.NumberOfPoints = 1000
```

## Human Intervention & Verification Gates
1. **Drop Direction & Velocity Vector**: Confirm active impact direction ($\pm X, \pm Y, \pm Z$) before initiating solve.
2. **Analysis End Time**: Confirm whether rebound capture is required (default: 15 ms).

---

## 4. 相關參考手冊 (Related References)

| 手冊名稱 | 內容摘要 |
| :--- | :--- |
| [`references/shock_pulse_and_boundary_conditions.md`](references/shock_pulse_and_boundary_conditions.md) | 半正弦波脈衝公式、*BOUNDARY_PRESCRIBED_MOTION_RIGID 卡片與多方向速度向量配置 |




## Reference: shock_pulse_and_boundary_conditions.md

# Session 06 技術手冊：衝擊波形換算與動力學邊界條件規範 (Shock Pulse & Boundary Conditions)

## 1. 物理衝擊規格與半正弦波換算 (Half-Sine Pulse Physics)

工業標準半正弦衝擊測試（如 35G / 11ms 或 50G / 11ms）在數值模擬中常用兩種方式施加：
1. **剛性面基座速度載荷 (Prescribed Velocity Pulse)**
2. **基座加速度載荷 (Base Acceleration / Rigid Body Motion)**

### 1.1 半正弦加速度脈衝公式
$$a(t) = A_0 \sin\left(\frac{\pi t}{T}\right), \quad 0 \le t \le T$$
其中：
- $A_0$：衝擊峰值加速度。例如 $35\text{G} = 35 \times 9806.65\text{ mm/s}^2 \approx 343232.75\text{ mm/s}^2$。
- $T$：脈衝持續時間。例如 $11\text{ ms} = 0.011\text{ s}$。

### 1.2 速度歷程積分解析解
對加速度進行積分可得質點速度曲線：
$$v(t) = \int_0^t a(\tau) d\tau = \frac{A_0 T}{\pi} \left[1 - \cos\left(\frac{\pi t}{T}\right)\right]$$
在脈衝結束時刻 $t = T$：
$$\Delta v = \frac{2 A_0 T}{\pi}$$
對於 35G / 11ms 衝擊：
$$\Delta v = \frac{2 \times 343232.75 \times 0.011}{\pi} \approx 2403.45\text{ mm/s}$$

---

## 2. 6 個衝擊方向配置矩陣 (6-Directional Shock Matrix)

伺服器設備規範（如 NEBS, IEC 60068-2-27）要求在 6 個正交空間方向進行衝擊評估：
1. `+X` (Right Shock) / `-X` (Left Shock)
2. `+Y` (Top Shock) / `-Y` (Bottom Shock, 通常為重力同向最大考驗)
3. `+Z` (Front Shock) / `-Z` (Rear Shock)

### 2.1 速度載荷組態卡片 (`*BOUNDARY_PRESCRIBED_MOTION_RIGID`)
LS-DYNA 關鍵字透過剛性基板（Rigid Wall 或 Impact Plate）傳遞動量：
```
*BOUNDARY_PRESCRIBED_MOTION_RIGID
$#     pid      dof      vad      lcid        sf       vid     death     birth
         1        2        2       101     1.000         0     0.015     0.000
```
- `pid`: 衝擊基板 Part ID。
- `dof`: 運動自由度（1=X, 2=Y, 3=Z）。
- `vad`: 速度向量控制（vad=2 代表指定速度歷程）。
- `lcid`: 引用之載荷曲線 ID (`*DEFINE_CURVE`)。
## 3. 全局數值阻尼最佳實踐 (`*DAMPING_GLOBAL`)

在顯式動力學分析中，衝擊波傳遞會激發高頻數值震盪（Numerical Ringing），若不加抑制會導致局部應力虛高與求解步長驟降：
- **關鍵字**：`*DAMPING_GLOBAL`
- **推薦阻尼比**：$\text{VALDMP} = 0.02 \sim 0.05$（即臨界阻尼的 $2\% \sim 5\%$）。
- **注意事項**：阻尼僅用於衰減非物理的高頻噪音，不可過大（$>0.10$），否則會衰減主脈衝能量，導致峰值加速度與變形低估。

---

## 4. LS-DYNA 求解參數矩陣檢核表 (Explicit Solver Analysis Settings)

| 參數類別 | 控制項 | 標準值 | 功能目的 |
| :--- | :--- | :--- | :--- |
| **時間步長** | `TSSFAC` (Time Step Scale Factor) | **0.9** | 確保滿足 Courant-Friedrichs-Lewy (CFL) 數值穩定判據 |
| **終止控制** | `ENDTIM` (Termination Time) | **0.015 s (15 ms)** | 完整捕捉 11 ms 衝擊與後續回彈震盪 |
| **質量縮放** | `DT2MS` (Mass Scaling) | **0.0 (禁用)** | 禁止非物理質量縮放，確保動量與慣性精準守恆 |
| **精度模式** | `Solver Precision` | **Double Precision** | 雙精度消除微小時間步長（$10^{-7}\text{ s}$）下的大規模累積數值截斷誤差 |
| **沙漏控制** | `IHQ` (Hourglass Type) | **6 (Belytschko-Bindeman)** | 剛度型共旋轉應變算法，物理保真度最高 |
| **數據輸出** | `D3PLOT` 輸出間隔 | **1000 步** | 確保衝擊歷程有充足幀率進行動畫與峰值追蹤 |
