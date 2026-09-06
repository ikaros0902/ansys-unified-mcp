---
name: ansys-fluent
description: ANSYS Fluent 流體力學與熱傳分析自動化主控手冊。基於 PyFluent (ansys-fluent-core) 與水密幾何網格工作流 (WGW)，涵蓋 Poly-Hexcore 體網格劃分、SST k-omega 湍流模型、共軛熱傳 (CHT)、Coupled 求解器偽瞬態控制、y+ 邊界層評估與發散自愈診斷。
keywords: [ansys-fluent, pyfluent, cfd, watertight-meshing, poly-hexcore, sst-k-omega, coupled-solver, pseudo-transient, y-plus, divergence-remedy]
Use when:
  - 需執行流體流動、強制/自然對流換熱、共軛熱傳 (CHT) 之自動化數值模擬。
  - 需透過水密幾何工作流 (WGW) 自動生成高正交品質之 Poly-Hexcore (Mosaic) 體網格。
  - 需配置 SST k-omega 湍流模型、能量方程式與流體/固體材料屬性。
  - 需設定速度入口 (Velocity Inlet)、壓力出口 (Pressure Outlet) 及熱通量/恆溫壁面條件。
  - 需透過 Coupled 演算法配合 Pseudo Transient 進行穩態高速強健收斂求解。
  - 需進行流體專業判斷：評估壁面 y+ 是否合規、排查出口逆向回流 (Reversed flow) 與校核質量守恆不平衡度 (< 0.1%)。
  - 需處理求解發散自愈：實施亞鬆弛因子 (URF) 或 Courant 數 (CFL) 階梯降階調節。
  - 觸發關鍵字 (繁中/En): Fluent分析, PyFluent, CFD模擬, 水密幾何網格, Poly-Hexcore, 湍流模型, y+評估, 殘差發散自愈, 逆向回流排查.
---

# ANSYS Fluent 流體力學與熱傳分析主控手冊

本技能提供標準化 ANSYS Fluent (PyFluent) 自動化工作流框架，整合水密幾何網格劃分 (WGW)、Coupled 偽瞬態求解控制，並嚴格落實 y+ 網格前檢、質量守恆量化評估與發散自愈機制。

---

## 一、核心物件進入點 (Entry Handles)

在 PyFluent 環境中，標準會話進入點定義如下：

```python
import ansys.fluent.core as pyfluent

# 1. 網格劃分會話 (Meshing Mode)
meshing = pyfluent.launch_fluent(mode="meshing", precision="double", processor_count=4)
workflow = meshing.workflow
workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")

# 2. 求解器會話 (Solver Mode) - 可自網格切換或獨立啟動
solver = meshing.switch_to_solver()
setup = solver.setup
models = setup.models
boundary = setup.boundary_conditions
cell_zone = setup.cell_zone_conditions
solution = solver.solution
methods = solution.methods
controls = solution.controls
monitors = solution.monitors
init = solution.initialization
calc = solution.run_calculation
results = solver.results
```

---

## 二、三大標準工作模式 SOP

### 1. 水密幾何 Poly-Hexcore 網格劃分 SOP (WGW Meshing)
1. **載入幾何與單位**：匯入 CAD 檔案（`.pmdb` / `.scdoc` / `.step`），設定長度單位（如 `in` 或 `mm`）。
2. **表面網格控制**：指定表面單元最小/最大尺寸與曲率/鄰近度法向角；執行 `Generate the Surface Mesh`。
3. **幾何特徵描述**：於 `Describe Geometry` 指定為純流體（Fluid only）或包含固體共軛熱傳（CHT）。
4. **邊界與區域更新**：檢驗進出口及壁面邊界命名選擇，確認區域類型（Fluid / Solid）。
5. **邊界層棱柱層**：設定邊界層層數（5~15 層）、過渡比與膨脹率（$\le 1.2$），確保近壁面第一層網格符合預期 $y^+$ 目標。
6. **Poly-Hexcore 體網格**：指定 `VolumeFill: "poly-hexcore"`，生成 Mosaic 核心六面體與多面體過渡網格。
7. **網格品質放行**：檢驗最小正交品質（Minimum Orthogonal Quality $\ge 0.15$）與最大歪斜度（$\le 0.85$），確認無負體積後切換至求解器。

### 2. 穩態共軛熱傳分析 SOP (Steady Conjugate Heat Transfer)
1. **模型啟用**：開啟能量方程式（`models.energy.enabled = True`），啟用 SST $k-\omega$ 湍流模型。
2. **材料物性定義**：定義流體（如水、空氣）之密度、比熱、導熱係數與黏度；指派固體域材料（如鋁、銅）。
3. **邊界載荷施加**：設定速度入口（速度量值、進口溫度與湍流強度）、壓力出口（背壓 0 Pa、回流總溫），壁面設定無滑移（No-slip）及熱通量或對流換熱係數。
4. **數值格式配置**：採用 Coupled 壓力-速度耦合演算法，啟用 Pseudo Transient（偽瞬態），動量與能量項採用二階上風格式（Second-Order Upwind）。
5. **初始化與監控**：執行 Hybrid 初始化；建立出口溫度與壓力之面平均監控器，設定質量守恆殘差監控。
6. **迭代與物理收斂**：計算 150~300 步，判定殘差趨勢、監控線平穩度及質量不平衡度（$< 0.1\%$）。
7. **後處理導出**：截圖導出對稱面速度/溫度雲圖，儲存 `.cas.h5` 與 `.dat.h5`。

### 3. 瞬態流場與渦脫落分析 SOP (Transient Aerodynamics)
1. **時間設定**：求解器設為瞬態（`setup.general.time = "transient"`）。
2. **時間步長估算**：依據網格特徵尺度與流速計算 Courant 數，確保 $\text{CFL} \le 1.0$（$\Delta t \approx \frac{\Delta x}{U_{max}}$）。
3. **湍流模型**：採用 SST $k-\omega$ 或變形版 SAS / LES 模型捕捉分離渦。
4. **自動副步迭代**：每時間步迭代 15~20 次，監控升力係數 $C_l$ 與阻力係數 $C_d$ 之週期性波動。

---

## 三、模組路由表 (Module Router)

| 分析階段 / 核心問題 | 推薦專精子手冊 | 核心技術要點 |
|---|---|---|
| 水密幾何、Sizing 與 Poly-Hexcore 體網格 | [`reference/watertight_meshing.md`](reference/watertight_meshing.md) | WGW Task 鏈、Mosaic 核心六面體技術、稜柱邊界層、正交品質門檻 |
| 湍流模型、能量方程與共軛熱傳 | [`reference/physics_models.md`](reference/physics_models.md) | SST $k-\omega$、能量守恆、物性參數（溫變非線性）、流固交界面設置 |
| 邊界條件設定與回流防範 | [`reference/boundary_conditions.md`](reference/boundary_conditions.md) | 速度入口、壓力出口、對稱邊界、壁面粗糙度與對流條件、回流總溫防禦 |
| 求解器離散、Coupled 與偽瞬態控制 | [`reference/solver_settings.md`](reference/solver_settings.md) | SIMPLE vs Coupled、Pseudo Transient 時間尺度、二階上風格式、混合初始化 |
| y+ 評估、殘差判讀與質量守恆校核 | [`reference/fluent_judgment.md`](reference/fluent_judgment.md) | 黏性底層 vs 壁面函數、緩衝層禁區、出口逆向回流診斷、質量守恆 $< 0.1\%$ |
| 求解發散、數值震盪與報錯自愈 | [`reference/fluent_diagnostics.md`](reference/fluent_diagnostics.md) | URF 降階調節、CFL 階梯重置、極值截斷排查、負體積自檢修復 SOP |

---

## 四、絕不能做清單 (Don'ts)

> [!CAUTION]
> 1. **嚴禁在未通過網格品質檢驗（正交品質 < 0.15 或歪斜度 > 0.85）下逕行求解**：
>    劣質網格會導致有限體積梯度離散誤差暴增，引發求解器剛度矩陣發散或溫度場浮點溢位（Floating Point Exception）。
> 2. **嚴禁將邊界層第一層網格置於緩衝層（$5 < y^+ < 30$）**：
>    標準壁面函數在此區間失效，而微觀黏性阻尼衰減亦未完全建立，將導致壁面剪切應力與對流傳熱係數產生高達 30%~50% 的偽數值偏差。必須依工況嚴格劃分至 $y^+ \le 1$ 或 $30 < y^+ < 300$。
> 3. **嚴禁僅憑殘差降至 $10^{-3}$ 即斷定計算收斂**：
>    殘差下降僅代表數值代數方程組求解誤差降低，並不保證物理守恆。**必須強制檢驗質量流率不平衡度（Mass Imbalance $< 0.1\%$）**，且關鍵監控量（如出口溫度）連續 50 步波動小於 0.1%。
> 4. **嚴禁忽視壓力出口持續性逆向回流（Reversed flow）警告**：
>    若迭代中持續數百步回流，代表出口截斷了真實流場渦流。未延伸管長強行求解會引入虛假邊界條件，導致能量方程嚴重失真。
