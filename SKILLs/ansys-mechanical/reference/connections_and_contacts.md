# ANSYS Mechanical 接觸與連接 (Connections & Contacts) 指南

本手冊提供裝配體接觸對建立、接觸非線性演算法選擇、法向剛度因子微調、穿透控制（Pinball Region）以及接觸穩定化技術之標準 ACT 程式碼規範。

---

## 一、接觸對建立與接觸面/目標面選取原則

接觸由一對面（Contact Face 與 Target Face）組成。正確指定 Contact 與 Target 是收斂關鍵：

> [!TIP]
> **Contact / Target 指定四原則**：
> 1. **幾何曲率**：凸面或平面指定為 Target，凹面指定為 Contact。
> 2. **材料剛度**：剛度較大（較硬）的零件指定為 Target，剛度較小（較軟）的零件指定為 Contact。
> 3. **網格密度**：網格較粗糙的指定為 Target，網格劃分較精細的指定為 Contact。
> 4. **幾何體積**：面積/體積較大的主體指定為 Target。

```python
# 獲取連接群組 (Connections Group)
conn_group = Model.Connections.Children[0]  # 通常為 Connection Group

# 新增自訂接觸對 (Contact Region)
contact = conn_group.AddContactRegion()
contact.Name = "軸套配合接觸面"

# 指定接觸面與目標面 (透過 Named Selection)
contact.SourceLocation = ExtAPI.DataModel.GetObjectsByName("NS_SHAFT_CONTACT_FACE")[0]   # Contact 面
contact.TargetLocation = ExtAPI.DataModel.GetObjectsByName("NS_BUSHING_TARGET_FACE")[0] # Target 面
```

---

## 二、接觸類型與行為模式 (Contact Type & Behavior)

```python
# 接觸行為類型 (ContactType Enum):
# - Bonded: 綁定 (線性接觸，拉伸與剪切皆不分離)
# - NoSeparation: 無分離 (法向不可拉開，切向允許無摩擦微滑移)
# - Frictionless: 無摩擦 (非線性，允許分離與自由滑移，法向不可穿透)
# - Frictional: 有摩擦 (非線性庫倫摩擦，需定義摩擦係數)
# - Rough: 粗糙 (允許法向分離，但切向無滑移，相當於摩擦係數無限大)

contact.ContactType = Ansys.Mechanical.DataModel.Enums.ContactType.Frictional
contact.FrictionalCoefficient = 0.15  # 定義摩擦係數
```

---

## 三、接觸公式 (Formulation) 與法向剛度控制

接觸求解公式決定了法向剛度彈簧與拉格朗日乘子的計算方式：

```python
# 接觸公式設定 (ContactFormulation Enum):
# - AugmentedLagrange: 增廣拉格朗日法 (推薦首選，穿透小且對剛度敏感度較低)
# - PurePenalty: 純罰函數法 (計算快，但剛度過高難收斂、過低穿透大)
# - NormalLagrange: 嚴格法向拉格朗日 (零穿透，但剛度矩陣主元易出 0，非線性難解)
# - MPC: 多點約束方程式 (適用於線性 Bonded/NoSeparation，完全消除自由度)
contact.ContactFormulation = Ansys.Mechanical.DataModel.Enums.ContactFormulation.AugmentedLagrange

# 法向剛度因子 (Normal Stiffness Factor):
# 預設為 1.0。若發生接觸震盪或接觸剛度過大導致不收斂：
# 可降低至 0.01 ~ 0.1 (提高柔度，促進收斂，但須後檢穿透量)
contact.NormalStiffnessFactor = 0.1
contact.UpdateStiffness = Ansys.Mechanical.DataModel.Enums.UpdateContactStiffness.EachIteration  # 每步迭代更新剛度
```

---

## 四、探針球範圍 (Pinball Region) 與初始間隙消除

在實際裝配體 CAD 中，經常存在微米級初始間隙（Gap）或干涉（Interference）。若超出接觸探測範圍，接觸對會處於「未檢測到（Far Open）」狀態，引發剛體位移報錯：

```python
# 探針球半徑設定 (Pinball Region)
contact.PinballRadius = Quantity("0.002 [m]")  # 指定 2 mm 探針半徑，防止零件初始運動飛脫

# 介面初始接觸調整 (Interface Treatment):
# - AddOffsetRamped: 斜坡位移補償 (消除干涉或初始間隙，推薦非線性分析首選)
# - AdjustToTouch: 幾何剛性貼合 (直接將節點微平移至零間隙接觸)
# - AdjustToTouchAndRamp: 結合兩者優勢
contact.InterfaceTreatment = Ansys.Mechanical.DataModel.Enums.ContactInitialEffect.AddOffsetRamped
```

---

## 五、接觸穩定化阻尼 (Stabilization Damping)

當多零件裝配體在初始載荷步處於鬆弛未壓緊狀態時，微小外力即會造成無窮大位移。可開啟接觸阻尼以維持靜態平衡：

```python
# 開啟接觸穩定化 (解決初始剛體飛脫問題)
contact.StabilizationDampingFactor = 0.01  # 引入 1% 數值穩定阻尼
```

---

## 六、接觸狀態後處理檢驗 (Contact Tool)

求解前或求解後，必須使用 Contact Tool 驗證接觸狀態與穿透量：

```python
# 新增 Contact Tool 進行接觸診斷
analysis = Model.Analyses[0]
contact_tool = analysis.Solution.AddContactTool()

# 評估接觸初始狀態與結果
status_res = contact_tool.AddStatus()
penetration_res = contact_tool.AddPenetration()
pressure_res = contact_tool.AddPressure()

contact_tool.EvaluateAllResults()

# 判讀準則：
# 1. 穿透量 (Penetration) 應小於特徵尺寸的 0.1% 或單元尺寸的 1%。
# 2. 接觸狀態 (Status): 應為 Sticking (黏著) 或 Sliding (滑移)，避免發生假開裂 (Open)。
```

---

## 七、MCP 工具對照

| ACT 原生 API | ANSYS MCP 工具 | 用途描述 |
|---|---|---|
| `conn_group.AddContactRegion()` | `run_mechanical_script` | 新增並精細配置接觸對參數 |
| `analysis.Solution.AddContactTool()` | `run_mechanical_script` | 新增接觸工具以評估法向穿透與狀態 |
