# 物理模型與共軛熱傳分析指南 (physics_models.md)

本手冊詳述 ANSYS Fluent 中常用湍流模型、能量守恆方程式、自然對流浮力驅動機制、共軛熱傳 (CHT) 流固交界面配置與溫變材料物性設定標準。

---

## 一、湍流模型工程選型矩陣

ANSYS Fluent 提供多種雷諾平均納維-斯托克斯 (RANS) 湍流模型，工程選型矩陣如下：

| 湍流模型 | 核心優勢 | 典型適用工程情境 | 局限性與風險 | 壁面處理建議 |
|---|---|---|---|---|
| **SST $k-\omega$ (預設首選)** | 結合近壁 $k-\omega$ 精度與遠場 $k-\epsilon$ 穩定性；具備剪切應力限制器 | 混合管流、翼型分離、流固換熱、逆壓梯度流動、強迴流渦 | 計算成本略高於標準 $k-\epsilon$ | 建議 $y^+ \le 1$；亦支援自動壁面函數 |
| **Realizable $k-\epsilon$** | 滿足雷諾應力物理可實現性；旋轉與彎曲流線預測優良 | 射流衝擊、管道均勻流、旋流器、大尺度建築外流場 | 逆壓梯度分離點預測偏晚 | 壁面函數 ($30 < y^+ < 300$) |
| **Spalart-Allmaras (S-A)** | 單一方程模型，數值收斂性極佳，記憶體開銷低 | 航空外流空氣動力學、附著或輕度分離流場 | 無法精確預測二次流與自由剪切流 | 需解析至 $y^+ \approx 1$ |
| **LES / DES / SAS** | 直接解析大尺度瞬態湍流渦結構 | 高雷諾數非定常氣動噪聲、強烈週期性渦脫落 | 網格密度與時間步極度嚴苛 | 必須全場精細網格 |

### SST $k-\omega$ 物理混合機制
SST 模型透過平滑混合函數 $F_1$ 實現方程式空間權重切換：
$$\Phi = F_1 \Phi_{k-\omega} + (1 - F_1) \Phi_{k-\epsilon}$$
- **在近壁面邊界層內部 ($F_1 \approx 1$)**：退化為 Wilcox 標準 $k-\omega$ 方程，無需求解複雜的經驗阻尼函數即可直抵黏性底層，精準預測壁面剪切摩擦。
- **在邊界層外緣及自由流區 ($F_1 \approx 0$)**：轉換為高雷諾數 $k-\epsilon$ 變換形式，徹底克服傳統 $k-\omega$ 模型對遠場自由流湍流輸入值過度敏感的數值缺陷。
- **渦黏係數 $\mu_t$ 引入限制器**：
  $$\mu_t = \frac{\rho k}{\omega} \frac{1}{\max\left(1, \frac{\Omega F_2}{a_1 \omega}\right)}$$
  其中 $\Omega$ 為渦量幅值，$F_2$ 為第二混合函數。此限制器保證雷諾剪切應力與湍動能比值不超過常數 $a_1 \approx 0.31$，有效防止逆壓梯度區過度高估湍動能導致分離延遲。

---

## 二、能量方程式與熱傳機制

啟用能量方程：`setup.models.energy.enabled = True`

### 1. 能量守恆方程式通式
$$\frac{\partial (\rho E)}{\partial t} + \nabla \cdot (\mathbf{u}(\rho E + p)) = \nabla \cdot \left( k_{eff} \nabla T - \sum_j h_j \mathbf{J}_j + (\boldsymbol{\tau}_{eff} \cdot \mathbf{u}) \right) + S_h$$
其中有效導熱係數 $k_{eff} = k + \frac{c_p \mu_t}{Pr_t}$，湍流普朗特數 $Pr_t$ 預設為 0.85。

### 2. 黏性耗散項 (Viscous Dissipation) 開啟準則
黏性應力做功產熱項 $(\boldsymbol{\tau}_{eff} \cdot \mathbf{u})$ 在多數常溫常速流動中可忽略。但在下列情境**必須啟用**：
- **高速可壓縮流動**：馬赫數 $Ma = \frac{U}{c} > 0.3$。
- **高黏性潤滑流體**：布林克曼數 $Br = \frac{\mu U^2}{k \Delta T} > 1$（如重油軸承潤滑、聚合物熔體擠出）。

### 3. 自然對流浮力驅動模型選型
- **Boussinesq 近似模型**：
  - 適用條件：封閉腔體溫差較小，滿足 $\beta (T - T_0) \ll 1$（通常 $\Delta T < 20 \sim 30^\circ\text{C}$）。
  - 密度處理：除浮力項 $(\rho - \rho_0)g \approx -\rho_0 \beta (T - T_0)g$ 外，其餘方程式中密度視為常數。
  - 需設定參考溫度 $T_0$（Operating Temperature）與熱膨脹係數 $\beta$。
- **理想氣體狀態方程 (Ideal Gas)**：
  - 適用條件：大溫差熱羽流、煙道燃燒、開放大氣對流；密度與絕對溫度反比 $\rho = \frac{p_{op}}{R T}$。
  - 需開啟重力場並設定操作密度（Operating Density）。

---

## 三、共軛熱傳 (Conjugate Heat Transfer, CHT) 架構

共軛熱傳涉及流體流動與固體內部熱傳導之雙向耦合求解。

### 1. 流固交界面 (Coupled Wall) 處理
當網格劃分完成匯入 Fluent 後，流體與固體交界面會自動生成成對壁面：`wall-fluid-solid` 與 `wall-fluid-solid:shadow`。
- **邊界設定**：在 Thermal 標籤頁中選取 **"Coupled"**。
- **能量守恆物理條件**：
  - 溫度連續性：$T_{fluid}|_{interface} = T_{solid}|_{interface}$
  - 熱通量連續性：$-k_f \left(\frac{\partial T_f}{\partial n}\right)_{wall} = -k_s \left(\frac{\partial T_s}{\partial n}\right)_{wall}$
- **接觸熱阻 (Thermal Contact Resistance)**：若兩固體接觸面存在微觀氣隙或導熱膏熱阻，可指定薄層厚度與虛擬接觸面導熱係數，或設定接觸熱阻值 $R_{tc} = \frac{\Delta x}{k}$。

---

## 四、材料物性資料庫與溫變模型配置

在共軛熱傳與流體分析中，物性定義直接決定計算精度：

```python
# 1. 啟用能量方程式與 SST k-omega 湍流模型
solver.setup.models.energy.enabled = True
solver.setup.models.viscous.model = "k-omega"
solver.setup.models.viscous.k_omega_model = "sst"

# 2. 定義流體材料 (以空氣為例)
air = solver.setup.materials.fluid["air"]
air.density.option = "constant"
air.density.value = 1.225
air.viscosity.value = 1.7894e-05
air.specific_heat.value = 1006.43
air.thermal_conductivity.value = 0.0242

# 3. 氣體黏度 Sutherland 定律 (高溫流動): mu(T) = mu0 * (T/T0)^(3/2) * (T0 + S)/(T + S)
# air.viscosity.option = "sutherland"

# 4. 溫變物性定義 (多項式範例: k(T) = a0 + a1*T + a2*T^2)
air.thermal_conductivity.option = "polynomial"
air.thermal_conductivity.polynomial_coefficients = [0.002, 7.5e-05, -1.5e-08]

# 5. 指派區域材料
solver.setup.cell_zone_conditions.fluid["fluid-domain"].material = "air"
solver.setup.cell_zone_conditions.solid["solid-domain"].material = "aluminum"
```

---

## 五、共軛熱傳分析工程校核注意事項

1. **交界面兩側網格過渡比**：流體側與固體側交界面處單元體積比應控制在 1:2 至 2:1 以內，避免過大的空間步長突變引發局部熱通量虛假震盪。
2. **固體域網格熱穿透深度**：固體域內部若存在高溫梯度（如電子散熱晶片或冷卻通道周圍），固體側壁面亦需劃分 3~5 層稜柱層以準確捕捉熱傳導法向梯度。
3. **能量方程殘差收斂標準**：相較於動量殘差（$10^{-3} \sim 10^{-4}$），能量方程殘差必須降至 **$10^{-6}$** 以下，同時配合流固界面熱通量平衡監控（誤差 $< 0.1\%$）。
