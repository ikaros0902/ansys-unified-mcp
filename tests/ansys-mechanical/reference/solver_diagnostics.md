# ANSYS Mechanical 求解器診斷與自愈庫 (Solver Diagnostics & Self-Healing)

本手冊彙整 ANSYS Mechanical 有限元求解中最常見之四大經典崩潰報錯，深入剖析數值力學根因，並提供立即可套用的 ACT 程式碼級自愈處置對策表。

---

## 一、經典報錯速查與自愈總覽

```
+-----------------------------------------------------------------------------------+
| 報錯代碼 / 經典關鍵字                                  | 物理根因分類    | 核心自愈手段       |
+-----------------------------------------------------------------------------------+
| 1. Small equation solver pivot term ...               | 剛體位移/無約束 | 補足約束 / 弱彈簧  |
| 2. Nonlinear convergence failure / Terminated         | 殘差力不平衡    | 副步細分 / 降低剛度|
| 3. Contact chattering detected                        | 接觸高頻震盪    | 數值阻尼 / 增廣拉格|
| 4. Element ... has become highly distorted / Jacobian | 網格幾何畸變    | 網格細化 / 六面體  |
+-----------------------------------------------------------------------------------+
```

---

## 二、報錯 1：主元為零錯誤 (Small Equation Solver Pivot Term)

### 1. 報錯訊息實例
`"Small equation solver pivot term (0.000E+00) encountered at node 14582 DOF UZ. Check for unconstrained bodies or open contacts."`

### 2. 力學根因排查
- 剛度矩陣 $[K]$ 出現奇異（行列式值為 0）。
- 模型中存在未受充分約束的零件（具備自由平移或轉動機構自由度）。
- 裝配體接觸對初始存在間隙，且未設置探針範圍，導致在第一個副步零件被外力「踢飛」。

### 3. ACT 自動自愈處置代碼
```python
def heal_pivot_error(analysis, contact_pinball_m=0.003):
    """主元為零剛體位移自愈腳本。"""
    settings = analysis.Children[0]
    
    # 1. 自動開啟弱彈簧 (Weak Springs) 防止剛體飛脫
    settings.WeakSprings = Ansys.Mechanical.DataModel.Enums.WeakSpringsType.ProgramControlled
    print("[自愈生效] 已開啟弱彈簧以維持初始剛度平衡。")
    
    # 2. 自動調大所有接觸對的探針球半徑 (Pinball Radius)
    for conn in Model.Connections.Children:
        for contact in conn.Children:
            if hasattr(contact, "PinballRadius"):
                contact.PinballRadius = Quantity("{} [m]".format(contact_pinball_m))
                contact.InterfaceTreatment = Ansys.Mechanical.DataModel.Enums.ContactInitialEffect.AdjustToTouch
                print("[自愈生效] 接觸對 [{}] 已擴大探針球半徑至 {} m 並貼合初始間隙。".format(
                    contact.Name, contact_pinball_m
                ))
```

---

## 三、報錯 2：非線性不收斂 (Nonlinear Convergence Failure)

### 1. 報錯訊息實例
`"The unconverged solution (time 0.456) has been terminated. The solver has reached the maximum number of substeps/bisections."`

### 2. 力學根因排查
- 外部載荷增量步長過大，結構進入塑性流動或大幾何變形時無法找到平衡點。
- 未開啟大變形開關（`LargeDeflection`），使得旋轉與剛度矩陣非線性更新失真。
- 接觸法向剛度因子過硬，導致迭代時在穿透與反彈間反覆振盪。

### 3. ACT 自動自愈處置代碼
```python
def heal_nonlinear_convergence(analysis):
    """非線性迭代不收斂自愈腳本。"""
    settings = analysis.Children[0]
    
    # 1. 強制開啟大變形效應
    settings.LargeDeflection = True
    
    # 2. 自動細分副步 (Substeps) - 放大 5 倍時間解析度
    settings.AutomaticTimeStepping = Ansys.Mechanical.DataModel.Enums.AutomaticTimeStepping.On
    settings.InitialSubsteps = 50
    settings.MinimumSubsteps = 25
    settings.MaximumSubsteps = 500
    
    # 3. 開啟線搜尋 (Line Search) 與 Full Newton-Raphson
    settings.NewtonRaphsonType = Ansys.Mechanical.DataModel.Enums.NewtonRaphsonType.Full
    settings.LineSearch = Ansys.Mechanical.DataModel.Enums.LineSearchType.On
    
    # 4. 調降所有非線性接觸對法向剛度因子至 0.05
    for conn in Model.Connections.Children:
        for contact in conn.Children:
            if hasattr(contact, "NormalStiffnessFactor"):
                contact.NormalStiffnessFactor = 0.05
                contact.UpdateStiffness = Ansys.Mechanical.DataModel.Enums.UpdateContactStiffness.EachIteration
                
    print("[自愈生效] 非線性副步已大幅細化、大變形已開啟、接觸剛度已調降為 0.05。")
```

---

## 四、報錯 3：接觸高頻震盪 (Contact Chattering Detected)

### 1. 報錯訊息實例
`"Contact status has changed drastically between iterations. Contact chattering detected at contact region 3."`

### 2. 力學根因排查
- 接觸表面在微小變形下反覆跳動於開（Open）與閉（Closed）之間，破壞殘差收斂。

### 3. ACT 自動自愈處置代碼
```python
def heal_contact_chattering(contact_region):
    """接觸震盪抖動自愈腳本。"""
    # 1. 切換至增廣拉格朗日法 (Augmented Lagrange)
    contact_region.ContactFormulation = Ansys.Mechanical.DataModel.Enums.ContactFormulation.AugmentedLagrange
    
    # 2. 引入接觸穩定化阻尼 (Stabilization Damping Factor)
    contact_region.StabilizationDampingFactor = 0.02
    
    # 3. 設定每步動態更新剛度
    contact_region.UpdateStiffness = Ansys.Mechanical.DataModel.Enums.UpdateContactStiffness.EachIteration
    print("[自愈生效] 接觸對 [{}] 已配置穩定化阻尼並啟用增廣拉格朗日法。".format(contact_region.Name))
```

---

## 五、報錯 4：單元過度畸變 (Highly Distorted Element / Negative Jacobian)

### 1. 報錯訊息實例
`"Element 89201 has become highly distorted. Excessive distortion of elements may cause solver divergence."`

### 2. 力學根因排查
- 局部應力/應變極大，導致四面體單元被壓縮或扭曲至雅可比行列式小於等於 0。

### 3. 自愈對策方針
1. **網格形態改造**：由一階四面體（SOLID185）改為六面體（Sweep / HexDominant）或高階四面體（SOLID187）。
2. **局部特徵倒角**：消除 CAD 中的無倒角尖銳幾何突起。
3. **載荷副步細化**：縮小單元變形步進速率，允許彈塑性材料平緩流動重分配應力。
