# 求解器演算法與數值離散格式手冊 (solver_settings.md)

本手冊規範 ANSYS Fluent 求解器壓力-速度耦合演算法選型、Pseudo Transient（偽瞬態）求解控制、空間離散格式標準以及流場高效初始化策略。

---

## 一、壓力-速度耦合演算法對比與選型

| 演算法 | 求解機制 | 記憶體開銷 | 收斂速度與強健性 | 典型適用工況 |
|---|---|---|---|---|
| **Coupled (預設推薦)** | 隱式聯立求解連續方程與動量方程組 | 較大 (約 1.5~2 倍) | 極快、極強健；對大網格歪斜度與強剪切流抗干擾能力強 | 強對流換熱、共軛熱傳 (CHT)、跨音速流動、非結構 Mosaic 網格 |
| **SIMPLE** | 分離式求解 (先動量再壓力修正) | 小 | 中等；依賴精細的亞鬆弛因子 (URF) 調節 | 記憶體受限之大型穩態網格、低速層流 |
| **SIMPLEC** | 分離式求解 (動量截斷項增強一致性) | 小 | 略優於 SIMPLE；允許較高動量 URF (如 1.0) | 幾何簡單、網格正交度極高的層流/湍流 |
| **PISO** | 包含多次壓力校正迴圈 | 中等 | 瞬態單時間步內收斂極快 | 大時間步瞬態流動 (Transient Aerodynamics) |

---

## 二、Pseudo Transient（偽瞬態）控制機制

在穩態 Coupled 演算法中，推薦強制啟用 **Pseudo Transient（偽瞬態）**：
`solver.solution.methods.pseudo_transient = True`

### 1. 數值原理
偽瞬態在穩態代數方程主對角線上引入虛擬時間步長項 $\frac{\rho V_p}{\Delta \tau}$，大幅提升代數剛度矩陣的對角佔優性（Diagonal Dominance），能極有效壓制非線性強耦合引發的數值發散與低頻晃盪。

### 2. 時間尺度與 Courant 數 (CFL) 調節
- **自動時間尺度 (Automatic)**：Fluent 依據單元體積與局部對流/擴散特徵速度自動計算局部時間步長 $\Delta \tau = \frac{\Delta x}{U_{local}}$。
- **Courant 數 (CFL)**：預設值為 **200**。
  - 初期流場震盪：可降至 **20 ~ 50** 以平穩渡過初始擾動；
  - 流場平穩後：逐步階梯提升回 **100 ~ 200** 以全速收斂。

---

## 三、空間離散格式工程規範 (Discretization Schemes)

離散格式直接決定計算結果的精度與數值耗散：

```text
+-----------------------+-----------------------------+-----------------------------+
| 方程式項              | 工程推薦格式 (二階精度)     | 適用與禁忌說明              |
+-----------------------+-----------------------------+-----------------------------+
| 梯度項 (Gradient)     | Least Squares Cell Based    | 預設首選，計算成本低且精度高 |
| 壓力項 (Pressure)     | Second Order                | 一般連續流動推薦            |
| 壓力項 (特殊)         | PRESTO!                     | 強旋流、自然對流浮力、多相流|
| 動量項 (Momentum)     | Second-Order Upwind         | 嚴禁最終算例採用一階迎風    |
| 能量項 (Energy)       | Second-Order Upwind         | 精確捕捉熱邊界層與溫度梯度  |
| 湍流項 (k, omega)     | First/Second-Order Upwind   | 初期一階穩定，終收斂切二階  |
+-----------------------+-----------------------------+-----------------------------+
```

> [!WARNING]
> **嚴禁以一階迎風格式 (First-Order Upwind) 作為最終工程交付結果**：
> 一階格式存在巨大的一階截斷誤差（即數值假擴散，Numerical False Diffusion），會人為人為平滑掉邊界層剪切應力、激波位置與溫度梯度，導致 Nusselt 數或流阻計算失真高達 20%~40%。

---

## 四、流場初始化策略

### 1. Hybrid Initialization（混合初始化，首選）
- **機制**：求解一組簡化的無黏拉普拉斯方程，迅速生成全場連續的壓力場與平滑無散度速度場。
- **優勢**：大幅減少傳統初始化初期出現的局部極值與超調現象，通常能在 5~10 次虛擬掃描後完成，節省後續 30%~50% 的迭代步數。
- **執行命令**：`solver.solution.initialization.hybrid_initialize()`。

### 2. Standard Initialization（標準初始化）
- **機制**：自指定進口或計算域手動賦予全場恆定均勻初值。
- **適用場景**：當混合初始化因複雜孔隙介質或特殊多相流失敗時回退採用。

---

## 五、PyFluent 求解控制標準代碼片段

```python
# 1. 配置壓力-速度耦合為 Coupled 並開啟偽瞬態
methods = solver.solution.methods
methods.pressure_velocity_coupling.scheme = "Coupled"
methods.pseudo_transient = True

# 2. 指定二階空間離散格式
methods.discretization_scheme["pressure"] = "second-order"
methods.discretization_scheme["momentum"] = "second-order-upwind"
methods.discretization_scheme["temperature"] = "second-order-upwind"
methods.discretization_scheme["k"] = "second-order-upwind"
methods.discretization_scheme["omega"] = "second-order-upwind"

# 3. 執行 Hybrid 初始化
solver.solution.initialization.hybrid_initialize()

# 4. 執行迭代求解 (150 步)
solver.solution.run_calculation.iterate(iter_count=150)
```

---

## 六、收斂監控器 (Monitors) 設置規範

除了依賴預設的代數殘差外，必須在求解前設定實體物理監控點：

1. **關鍵截面監控量**：
   - 出口截面面積加權平均溫度（`area-weighted-average` of temperature）
   - 進出口壓降差 $\Delta p = p_{inlet} - p_{outlet}$
   - 固體發熱壁面最高溫度（`vertex-maximum` of temperature）
2. **收斂終止判據**：
   - 監控物理量在連續 50 步迭代內的相對變化率 $< 0.1\%$；
   - 質量流量不平衡度 $< 0.1\%$ 且保持平穩無漂移。
