# 流體工程專家準則與物理判斷力手冊 (fluent_judgment.md)

本手冊規範 ANSYS Fluent 計算流體力學 (CFD) 之三大核心專家判據：壁面 $y^+$ 邊界層網格解析度評估、壓力出口逆向回流 (Reversed flow) 診斷處置，以及質量守恆與物理收斂的量化驗收黃金準則。

---

## 一、壁面 $y^+$ 邊界層評估準則

### 1. 理論定義與物理意義
無量綱壁面距離 $y^+$ 定義為：
$$y^+ = \frac{\rho u_\tau y_1}{\mu} = \frac{u_\tau y_1}{\nu}$$
其中：
- $y_1$ 為壁面第一層網格節點距壁面的垂直距離；
- $u_\tau = \sqrt{\frac{\tau_w}{\rho}}$ 為壁面摩擦速度（$\tau_w$ 為壁面剪切應力）；
- $\nu = \frac{\mu}{\rho}$ 為流體運動黏度。

### 2. 邊界層三分區與網格劃分紅線

```text
壁面 (y=0)
  | 
  |--- [1. 黏性底層 Viscous Sublayer] (y+ <= 1, 工程容限 < 5)
  |      分子黏性佔絕對支配地位，剪切應力近似常數。
  |      【要求】：SST k-omega 或低 Re 模型解析精確傳熱、流動分離必須 y+ <= 1。
  |
  |--- [2. 緩衝層 Buffer Layer] (5 < y+ < 30)  ===> 【⚠️ 嚴格禁止禁區！】
  |      分子黏性與湍流雷諾應力相當，缺乏精確解析解。
  |      標準壁面函數在此失效，而湍流阻尼阻尼未完全衰減。
  |      若第一層網格落在此區間，壁面阻力與熱通量將產生 30%~50% 偽數值偏差！
  |
  |--- [3. 對數律區 Log-law Region] (30 < y+ < 300)
  |      湍流雷諾應力佔主導，流速服從對數分佈 u+ = (1/kappa)*ln(y+) + B。
  |      【要求】：適用於大尺度高雷諾數管流，配合壁面函數大幅節省網格數量。
  |
主流核心區 (y+ > 300)
```

---

## 二、壓力出口逆向回流 (Reversed Flow) 工程處置

在計算過程中，控制台頻繁出現：
`reversed flow in xxx faces on pressure-outlet`

### 1. 診斷邏輯決策樹
```text
                          [出現逆向回流警告]
                                   |
                  +----------------+----------------+
                  |                                 |
           [計算初期 < 50 步]              [計算中後期 > 100 步]
                  |                                 |
         【暫態數值擾動】                 【檢查回流面數與物理流場】
                  |                                 |
         繼續計算並觀察殘差                +--------+--------+
                                           |                 |
                                   [回流面數迅速消失]  [回流持續且面數穩定]
                                           |                 |
                                      【正常收斂】     【幾何截斷渦流！】
```

### 2. 工程自愈與處置 SOP
1. **緊急數值防禦**：立即在 `pressure-outlet` 邊界設定合理的 **Backflow Total Temperature（回流總溫）** 與湍流參數，防止非物理的低溫/高溫流體倒灌引發數值發散。
2. **根治處置（下游管長延長）**：
   - 根因分析：計算域出口截面過於接近彎管、台階或障礙物，人為截斷了下游真實存在的迴流分離渦。
   - 修正方案：**必須在出口處將管道沿軸向延長 5 ~ 10 倍水力直徑 ($5 \sim 10 D_h$)**，使迴流渦在計算域內部自然閉合，出流截面恢復為單向流動。

---

## 三、質量守恆與物理收斂黃金準則

> [!CRITICAL]
> **嚴禁僅憑殘差降至 $10^{-3}$ 即斷定計算收斂！**
> 殘差下降僅代表代數求解誤差減小，若網格畸變或邊界不合理，殘差極低時流場仍可能嚴重失真。

### 1. 質量流率不平衡度 (Mass Imbalance) 量化判據
質量守恆是檢驗流場數值收斂的最高黃金準則：
$$\text{Mass Imbalance} = \frac{|\sum \dot{m}_{in} - \sum \dot{m}_{out}|}{\sum \dot{m}_{in}} < 0.1\% \quad (1.0 \times 10^{-3})$$
- 若不平衡度 $> 0.5\%$：計算未收斂，不得交付結果；
- 若不平衡度 $< 0.1\%$：通過質量守恆驗收。

### 2. 關鍵物理監控量平穩準則
在迭代最後 50 步內，選定的工程監控量（如出口面積加權平均溫度、總壓降、目標壁面換熱係數）必須滿足：
$$\frac{\max(P_{50}) - \min(P_{50})}{\text{mean}(P_{50})} < 0.1\% \quad (1.0 \times 10^{-3})$$
且曲線呈現水平直線，無單調漂移或低頻震盪。

---

## 四、PyFluent 質量平衡與 y+ 自動化驗收代碼

```python
# 1. 計算質量通量不平衡度
inflow = solver.solution.report_definitions.flux_mass["flux-in"].compute()
outflow = solver.solution.report_definitions.flux_mass["flux-out"].compute()
net_flux = abs(inflow - outflow)
imbalance_ratio = net_flux / abs(inflow)

print(f"進口質量流量: {inflow:.6f} kg/s, 出口質量流量: {outflow:.6f} kg/s")
print(f"質量不平衡率: {imbalance_ratio * 100:.4f}%")

if imbalance_ratio < 0.001:
    print("[驗收通過] 質量守恆不平衡度 < 0.1%，滿足物理收斂黃金準則。")
else:
    print("[驗收攔截] 質量不平衡度超標，需增補迭代步數或排查回流！")

# 2. 壁面 y+ 分佈自動化查詢
# 透過 TUI 或後處理提取壁面 y+ 統計
tui_cmd = "/plot/surface-integrals/area-weighted-average wall () cell-y-plus no"
```
