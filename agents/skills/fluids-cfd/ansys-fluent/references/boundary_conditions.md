# 邊界條件工程配置手冊 (boundary_conditions.md)

本手冊規範 ANSYS Fluent 各類流體與熱邊界條件的工程設定準則、進出口水力特徵計算、逆向回流防禦機制以及 PyFluent Settings API 配置模式。

---

## 一、常用邊界條件型態與適用場景

| 邊界類型 | 核心指定物理量 | 適用場景 | 工程注意事項 |
|---|---|---|---|
| **速度入口 (Velocity Inlet)** | 速度幅值/向量、溫度、湍流參數 | 不可壓縮流動進口、已知流量風洞 | 不推薦用於強烈可壓縮流動 |
| **質量流量入口 (Mass Flow Inlet)** | 質量流率 $\dot{m}$、總溫、超音速/初壓 | 可壓縮氣流、泵閥已知額定流量 | 內部壓力隨下游阻力浮動 |
| **壓力入口 (Pressure Inlet)** | 總壓 $p_0$、靜壓、總溫 | 自由吸氣環境、大氣開口、儲氣罐放氣 | 速度由全場壓差反算 |
| **壓力出口 (Pressure Outlet)** | 標稱表壓 $p_s$、回流總溫、回流湍流 | 各類流道自由出流、大氣排放口 | 必須配置合理的回流物理量 |
| **壁面邊界 (Wall)** | 無滑移/滑移、熱通量/溫度/對流換熱 | 實體邊界、流固交界面、導流板 | 粗糙度設定需配合近壁網格 |
| **對稱邊界 (Symmetry)** | 法向速度為 0，所有變量法向梯度為 0 | 幾何與流場完全對稱之半模或 1/4 模 | 節省計算資源，禁止穿越對稱面 |

---

## 二、速度入口與湍流參數工程計算

### 1. 水力直徑 ($D_h$) 計算
$$D_h = \frac{4A}{P}$$
- 圓管（內徑 $D$）：$D_h = D$
- 矩形流道（寬 $a$、高 $b$）：$D_h = \frac{2ab}{a+b}$
- 同軸環狀流道（外徑 $D_o$、內徑 $D_i$）：$D_h = D_o - D_i$

### 2. 湍流強度 ($I$) 估算
充分發展的管內湍流強度經驗公式：
$$I = 0.16 \cdot Re_{D_h}^{-1/8} \quad \left(Re = \frac{\rho U D_h}{\mu}\right)$$
- 低湍流度（大型風洞、平靜大氣）：$I < 1\%$
- 中等湍流度（一般通風管流、換熱器）：$I \approx 3\% \sim 5\%$
- 強湍流度（燃燒室、葉片後方、高速射流）：$I > 10\%$

---

## 三、壓力出口回流防禦機制 (Backflow Protection)

在求解迭代初期或出口附近存在二次流、分離渦時，壓力出口常出現局部逆向回流警告：
`reversed flow in xxx faces on pressure-outlet`

### 1. 回流總溫 (Backflow Total Temperature) 致命陷阱
- **現象**：Fluent 預設回流溫度為 **300 K**。
- **風險**：若實際計算領域為高溫排氣（例如 $800\text{ K}$），一旦冷空氣以 $300\text{ K}$ 倒灌，會在出口截面產生劇烈的溫度衝擊與密度突變，引發能量方程嚴重數值震盪甚至浮點溢位（Floating Point Exception）。
- **黃金準則**：**回流總溫必須設定為流場在該出口截面的預期排出溫度**（高溫工況設為高溫，低溫冷媒設為低溫）。

### 2. 回流湍流規格
回流湍流強度與回流湍流黏度比（Turbulent Viscosity Ratio, 通常設為 5~10）應比照入口水平設定，避免倒灌非物理的超高湍流黏度。

---

## 四、壁面熱邊界條件配置模式

在 Wall 的 Thermal 標籤頁中，支援五種熱邊界模型：

1. **熱通量 (Heat Flux, $q$)**：
   - 絕熱壁面（Adiabatic）：$q = 0\text{ W/m}^2$。
   - 電加熱絲、恆定面熱源：指定具體熱通量數值。
2. **固定溫度 (Temperature, $T_w$)**：
   - 恆溫冷卻壁面、相變介質接觸壁面。
3. **對流換熱 (Convection)**：
   - 需指定外部換熱係數 $h$ 及外部流體自由流溫度 $T_\infty$。
   - 熱平衡：$q = h(T_\infty - T_w)$。
4. **薄壁導熱 (Shell Conduction / Thin Wall)**：
   - 適用於不劃分厚度網格的薄金屬外殼，需指定材料名稱與厚度 $\Delta s$，Fluent 自動計算面內沿面導熱。

---

## 五、PyFluent Settings API 邊界配置範例

```python
# 1. 速度入口 (Velocity Inlet) 配置
vin = solver.setup.boundary_conditions.velocity_inlet["inlet"]
vin.momentum.velocity.value = 5.0                       # 流速 5 m/s
vin.thermal.temperature.value = 350.0                    # 入口溫度 350 K
vin.turbulence.turbulent_specification = "Intensity and Hydraulic Diameter"
vin.turbulence.turbulence_intensity = 0.04               # 湍流強度 4%
vin.turbulence.hydraulic_diameter = 0.05                 # 水力直徑 50 mm

# 2. 壓力出口 (Pressure Outlet) 與回流防禦
pout = solver.setup.boundary_conditions.pressure_outlet["outlet"]
pout.momentum.gauge_pressure.value = 0.0                 # 標稱表壓 0 Pa
pout.thermal.temperature.value = 345.0                   # 回流保護總溫 (接近預期出口溫度)
pout.turbulence.turbulence_intensity = 0.05
pout.turbulence.hydraulic_diameter = 0.05

# 3. 恆定熱通量壁面 (Heat Flux Wall)
wall = solver.setup.boundary_conditions.wall["heater-wall"]
wall.thermal.thermal_condition = "Heat Flux"
wall.thermal.heat_flux.value = 1500.0                    # 1500 W/m^2
```

---

## 六、壁面粗糙度與特殊邊界工程準則

1. **壁面粗糙度高度 ($K_s$) 限制**：
   - 當壁面存在物理粗糙度時，需輸入等效沙粒粗糙度高度 $K_s$（Roughness Height）與粗糙度常數 $C_s$（通常取 0.5）。
   - **關鍵紅線**：$K_s$ 不得大於近壁第一層網格的物理中心高度（即 $K_s \le 2 y_1$），否則將破壞有限體積法近壁面通量通量格式的物理邊界假設。
2. **對稱面 (Symmetry) 應用限制**：
   - 僅當流動結構完全對稱且無自發對稱破缺（如卡門渦街、旋流進動）時方可使用；非對稱流場強行採用對稱面將人為壓制真實物理渦結構。
