# ANSYS Mechanical 工程判斷力庫 (Mechanical Judgment)

本手冊提供資深有限元分析師必備之工程判斷力判據：包含非線性 Newton-Raphson 收斂曲線即時診斷、網格無關性驗證量化標準、ASME 應力線性化評估，以及「應力奇異點 (Singularity)」與「真實應力集中 (Concentration)」辨別原則。

---

## 一、Newton-Raphson 收斂曲線診斷指南

在非線性求解歷程中，`Force Convergence`（殘差力 $F$）與 `Force Criterion`（收斂容差 $F_{\text{crit}}$）曲線是非線性健康度的首要體檢表：

```
殘差力 F
  ^
  |  * (迭代初態殘差高)
  |   \
  |    *---*
  |         \
  |          *-------------------- 容差基準線 F_crit
  |           \
  |            * (殘差 < F_crit -> 收斂並進入下一副步)
  +---------------------------------------------------> 累積迭代次數
```

### 1. 四大典型不收斂曲線特徵與根因診斷

| 曲線特徵表現 | 核心物理根因 | 診斷與工程處置對策 |
|---|---|---|
| **週期性鋸齒震盪 (Chattering)** | 接觸對在開/閉或黏著/滑移間高頻跳動 | 降低法向剛度因子 (`NormalStiffnessFactor = 0.05`)；增加接觸穩定化阻尼；開啟 Line Search。 |
| **殘差爆炸性劇增發散** | 缺少約束引發剛體位移或局部機構翻轉 | 檢查模型是否有零件未受約束飛脫；檢查接觸對是否初始開裂未閉合；開啟弱彈簧。 |
| **反覆二分切步 (Bisection)** | 進入大塑性流動、材料降伏或接觸劇烈衝擊 | 載荷副步初值過大；將 `InitialSubsteps` 提升至 50~100；檢查塑性正切模數是否為零。 |
| **漸進平緩但始終略高於容差** | 數值容差過於嚴苛或微小局部塑性震盪 | 檢查網格質量是否過差；必要時微調收斂公差（Tolerance）由 0.5% 放寬至 1%。 |

---

## 二、網格無關性量化驗證標準 (Mesh Independence)

任何關鍵受力零組件分析，未經網格無關性驗證之應力結果均不具備工程法定效力。

### 1. 網格無關性三級驗證法
- **網格尺寸漸縮**：至少建立三套網格（粗網格 Coarse、中網格 Medium、細網格 Fine），單元特徵尺寸縮小比 $r = h_{\text{coarse}} / h_{\text{fine}} \approx 1.3 \sim 2.0$。
- **相對變化率計算**：
  $$\Delta = \frac{|S_{\text{fine}} - S_{\text{medium}}|}{S_{\text{fine}}} \times 100\%$$

### 2. ASME 推薦 GCI (Grid Convergence Index) 指標
對關鍵監控物理量 $f$，計算漸近收斂解 $f_{\text{extrap}}$ 與 GCI 誤差帶：
$$p = \frac{\ln[(f_3 - f_2)/(f_2 - f_1)]}{\ln(r)}, \quad \text{GCI}_{12} = \frac{1.25 |\frac{f_1 - f_2}{f_1}|}{r^p - 1}$$

### 3. 工業量化判據
- **通過標準 ($\Delta \le 5\%$ 或 $\text{GCI} < 3\%$)**：判定達成網格無關性，可採用中等網格作為設計與量產基準。
- **警戒標準 ($5\% < \Delta \le 10\%$)**：需進一步加密局部圓角與接觸面 Sizing。
- **未達標 ($\Delta > 10\%$)**：結果嚴重依賴網格劃分，禁止直接用於強度評定。

---

## 三、應力奇異點 (Singularity) vs 真實應力集中 (Concentration)

有限元初學者最常犯的錯誤是將「數值奇異點」誤判為「真實結構破壞點」，導致過度設計或陷入網格細化的無窮迴圈。

### 1. 本質特徵對照表

| 評估維度 | 真實應力集中 (Stress Concentration) | 應力奇異點 (Stress Singularity) |
|---|---|---|
| **幾何幾何根源** | 存在物理倒角 (Fillet)、開孔、厚度漸變區 | 尖銳幾何內角（無倒角 90° 內凹角）、尖點接觸 |
| **邊界條件根源** | 分佈面壓力、均勻剪切載荷 | 點載荷、集中力作用節點、剛性固支邊界突變線 |
| **網格細化趨勢** | 網格加密後，最大應力漸進收斂至定值 ($K_t \sigma_0$) | **網格越細，最大應力越高，理論上趨向無窮大** |
| **力學處置建議** | 納入降伏、疲勞強度校核與安全係數計算 | **不可直接讀取尖角單點應力**，需透過下述方法處理 |

---

## 四、應力奇異點工程判定實務處置法

### 1. 節點未平均 vs 已平均應力斷差比對法 (Averaged vs Unaveraged)
在 Mechanical 後處理中，比對 `Unaveraged Stress` 與 `Averaged Stress`：
- 若最大應力節點處：
  $$\text{Diff} = \frac{|\sigma_{\text{unaveraged}} - \sigma_{\text{averaged}}|}{\sigma_{\text{averaged}}} \times 100\% > 20\%$$
  說明單元內應力梯度過陡，通常為網格密度極度不足或存在數值奇異點。

```python
# ACT 範例：建立已平均與未平均等效應力物件比對斷差
solution = Model.Analyses[0].Solution

# 已平均應力
avg_stress = solution.AddEquivalentStress()
avg_stress.Name = "等效應力_已平均"
avg_stress.DisplayOption = Ansys.Mechanical.DataModel.Enums.ResultAveragedOption.Averaged

# 未平均應力
unavg_stress = solution.AddEquivalentStress()
unavg_stress.Name = "等效應力_未平均"
unavg_stress.DisplayOption = Ansys.Mechanical.DataModel.Enums.ResultAveragedOption.Unaveraged

solution.EvaluateAllResults()
s_avg = avg_stress.Maximum.Value
s_unavg = unavg_stress.Maximum.Value
diff_pct = abs(s_unavg - s_avg) / s_avg * 100.0
print("應力斷差率: {:.2f}%".format(diff_pct))
if diff_pct > 20.0:
    print("[警報] 局部應力梯度劇烈或存在數值奇異點，禁止以未平均峰值定性！")
```

### 2. 聖維南原理外擴評估法 (Saint-Venant Distance)
依據聖維南原理，局部奇異點的數值擾動在離開幾何突變處 **1 ~ 2 個特徵尺寸（或壁厚 $t$）** 以外的區域便衰減至可忽略不計：
- **工程做法**：沿著遠離奇異點的路徑繪製路徑應力（Path Stress），以距離奇異點 $1.5t$ 處的真實平緩應力作為結構強度考核基準；或在 SpaceClaim 補充實際加工圓角（如 $R = 0.5 \sim 1.0\text{ mm}$）消除尖角奇異性。

### 3. ASME 應力分類與線性化 (Stress Linearization)
對於壓力容器或厚壁結構，可沿著穿透厚度的應力分類線 (Stress Classification Line, SCL) 提取：
- **膜應力 ($P_m$, Membrane Stress)**：截面均勻拉壓應力分量（自平衡載荷）。
- **彎曲應力 ($P_b$, Bending Stress)**：沿厚度線性分佈的純彎曲分量。
- **峰值應力 ($F$, Peak Stress)**：排除 $P_m + P_b$ 後的局部幾何缺口突變應力。
- **評定規範**：抗靜態破壞校核僅需保證 $P_m \le S_m$ 且 $P_m + P_b \le 1.5 S_m$，局部峰值應力 $F$ 僅用於評估疲勞壽命，不參與靜態強度降伏判定。
