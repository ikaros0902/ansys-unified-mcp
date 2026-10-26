# 衝擊脈衝邊界條件 (Shock Pulse Boundary Conditions) 深度規範

本手冊整理 LS-DYNA Explicit 衝擊/落摔分析之半正弦波脈衝公式與初始速度/速度歷程施加方式。
標準 LS-DYNA Analysis Settings（Hourglass Type 6、TSSFAC=0.9、雙精度求解等）之完整矩陣已在
[`../../shock-analysis-workflow/06-constraint-load/SKILL.md`](../../shock-analysis-workflow/06-constraint-load/SKILL.md)
定義，本文件不重複該求解器設定，僅聚焦邊界本身的脈衝公式推導與 API 施加邏輯。

API 真實性：`AddInitialVelocity()`、`AddVelocity()` 已於既有 ACT 原廠腳本
（`MECH_ACT_LSDYNA_Analysis_Settings_Shock.py`）實測驗證存在且可用。

---

## 1. 半正弦波脈衝公式推導 (Half-Sine Pulse Derivation)

工業標準衝擊測試（如 IEC 60068-2-27、NEBS GR-63-CORE）常以半正弦加速度脈衝描述衝擊歷程：

$$a(t) = A_0 \sin\left(\frac{\pi t}{T}\right), \quad 0 \le t \le T$$

其中 $A_0$ 為峰值加速度（G 轉換為 mm/s²：$A_0 = G \times 9806.65$），$T$ 為脈衝持續時間（秒）。

對加速度積分可得速度歷程：

$$v(t) = \frac{A_0 T}{\pi}\left[1 - \cos\left(\frac{\pi t}{T}\right)\right]$$

脈衝結束時刻 $t=T$ 的總速度變化量（Delta-V）：

$$\Delta v = \frac{2 A_0 T}{\pi}$$

> 範例：35G / 11ms 衝擊，$A_0 \approx 343232.75\ \text{mm/s}^2$，$T=0.011\ \text{s}$，
> 可得 $\Delta v \approx 2403.45\ \text{mm/s}$。完整換算細節與六方向衝擊矩陣（±X/±Y/±Z）
> 已於 [`../../shock-analysis-workflow/06-constraint-load/references/shock_pulse_and_boundary_conditions.md`](../../shock-analysis-workflow/06-constraint-load/references/shock_pulse_and_boundary_conditions.md)
> 完整列出，本文件不重複列表，僅延伸補充 ACT 腳本層級的 API 施加細節。

---

## 2. 初始速度邊界 (Initial Velocity) — ACT API 施加

落摔/衝擊試驗常以「初始速度 + 剛性基板速度歷程」組合模擬撞擊瞬間：

```python
# analysis 須為 LS-DYNA Explicit Dynamics 分析系統
analysis = Model.Analyses[0]

# 新增初始速度（通常施加於全部可動 Body，Named Selection: Scr_All_Bodies）
ini_vel = analysis.AddInitialVelocity()
ini_vel.Name = "Scr_Initial_vel_-Y_Bottom"
ini_vel.Location = ExtAPI.DataModel.GetObjectsByName("Scr_All_Bodies")[0]
ini_vel.DefineBy = LoadDefineBy.Components

# 落摔方向為 -Y，給定該軸分量初始速度（跌落撞擊瞬間速度）
ini_vel.YComponent = Quantity("-2403.45 [mm sec^-1]")
```

> [!NOTE]
> `DefineBy = LoadDefineBy.Components` 讓速度可依 X/Y/Z 分量分別給值，未指定分量預設為 0。
> 此 Enum 用法引用自原廠 ACT 腳本實測可用，非憑空假設。

---

## 3. 速度歷程邊界 (Velocity History) — 剛性基板速度曲線

剛性基板（如衝擊台面、固定夾具）常需施加完整速度-時間歷程曲線，而非單一常數：

```python
vel = analysis.AddVelocity()
vel.Name = "Scr_Velocity_-Y_Bottom"
vel.Location = ExtAPI.DataModel.GetObjectsByName("NS_SCR_FIXTURE_BOTTOM")[0]
vel.DefineBy = LoadDefineBy.Components

# 時間點陣列 (單位: 秒)
time_list = [0.0, 0.00055, 0.0011, 0.00165, 0.0022]  # 範例：11ms 脈衝切 20 點之一段

# Y 方向速度歷程 (單位: mm/s)，依半正弦公式 v(t) 逐點計算後代入
vel.YComponent.Inputs[0].DiscreteValues = [Quantity(str(t) + "[s]") for t in time_list]
vel.YComponent.Output.DiscreteValues = [Quantity("0.0[mm/s]") for t in time_list]  # 以實際 v(t) 數值取代

# 非作用軸分量固定為 0，避免殘留上一工況速度
vel.XComponent.Inputs[0].DiscreteValues = [Quantity(str(t) + "[s]") for t in time_list]
vel.XComponent.Output.DiscreteValues = [Quantity("0.0[mm/s]") for t in time_list]
```

> [!IMPORTANT]
> 速度歷程陣列的時間點與數值點數必須一一對應（`Inputs[0].DiscreteValues` 與
> `Output.DiscreteValues` 長度相同），且時間序列必須嚴格遞增，否則 LS-DYNA 求解器
> 讀取 `*DEFINE_CURVE` 時會出現非單調曲線錯誤。

---

## 4. 六方向衝擊切換邏輯

多方向衝擊評估（±X/±Y/±Z）常見作法是：每個方向各建立一組 InitialVelocity + Velocity 物件，
透過 `Suppressed` 屬性切換啟用/抑制，避免重複建模：

```python
# 切換至 -Y 方向：啟用對應方向物件，抑制其餘方向
for ic in analysis.InitialConditions:
    if ic.Name.startswith("Scr_Initial_vel_"):
        ic.Suppressed = not ic.Name.endswith("-Y_Bottom")

for child in analysis.Children:
    if child.Name.startswith("Scr_Velocity_"):
        child.Suppressed = not child.Name.endswith("-Y_Bottom")
```

此切換邏輯與既有 Fixture 幾何抑制機制（依軸向字串比對 Body 名稱）互相配合，
完整的 Fixture 幾何啟用/抑制腳本範例可見本技能 [`../scripts/apply_boundary_conditions.py`](../scripts/apply_boundary_conditions.py)
的 `shock` 分支。

---

## 5. 數值阻尼與 Analysis Settings 交叉引用

衝擊波傳遞激發的高頻數值震盪抑制（`*DAMPING_GLOBAL`，VALDMP = 0.02~0.05）與完整求解參數矩陣
（TSSFAC、Hourglass Type 6、雙精度、D3PLOT 輸出間隔）**不在本文件重複**，請直接查閱：
[`../../shock-analysis-workflow/06-constraint-load/SKILL.md`](../../shock-analysis-workflow/06-constraint-load/SKILL.md) 第 1 節。

---

## 6. 單位制提醒

LS-DYNA 衝擊分析慣用 NMM 單位制（mm, ton, s, N, MPa），速度單位常見 mm/s 或 mm/ms，
施加前務必確認 `ExtAPI.Application.ActiveUnitSystem` 已設為 `MechanicalUnitSystem.StandardNMM`，
避免與熱分析 SI 單位制（W, °C, m）混用造成速度量級錯誤 1000 倍。
