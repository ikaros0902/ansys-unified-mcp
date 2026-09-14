# Session 08 技術手冊：結構失效判定準則與塑性應變門檻 (Failure Criteria & Strain Limits)

## 1. 物理失效模式與工程背景 (Failure Modes in Electronic Hardware)

在伺服器機箱、板卡與電子組件的衝擊與跌落試驗中，失效現象主要可分為以下三類：
1. **鈑金結構永久變形與開裂 (Sheet Metal Plastic Rupture)**：
   - 沖孔邊緣、翻邊（Flange）以及螺孔周圍在衝擊彎矩作用下產生高塑性變形。
   - 若塑性變形擴展至貫穿整個網格單元，實體產品將出現可見裂紋甚至斷裂。
2. **塑料卡扣脆斷與疲勞脫扣 (Plastic Latch Rupture)**：
   - PC+ABS 材料具有中等延展性，但在高速動態應變率（$\dot{\varepsilon} \ge 10^2\text{ s}^{-1}$）下表現出脆性特徵。
   - 應變帶一旦貫穿厚度，卡扣即失去自鎖能力。
3. **BGA / 晶片焊點疲勞剝離與錫裂 (Solder Joint Cracking)**：
   - SAC305 無鉛焊錫屈服強度低，在跌落衝擊瞬間，PCB 與晶片基板熱膨脹與剛度不匹配，PCB 彎曲在最外圈角部焊點（Corner Solder Balls）產生極高剪切與剝離應變。
   - 反覆跌落將引發焊點底部開裂，導致電氣開路失效。

---

## 2. 定量失效門檻與判定細則 (Quantitative Failure Criteria)

### 2.1 金屬薄板與實體 (Metal Structures: SGCC, SUS, AL6061)
- **等效塑性應變門檻**：$\text{EPS} \ge 0.0100$ ($1.0\%$)。
- **幾何貫穿判定法則 (Go-through Criterion)**：
  1. **貫穿單一完整網格單元**：若連續一整排單元的頂底面塑性應變均超過 $1\%$，視為初始裂紋貫穿（Crack Initiation）。
  2. **縫焊孔 (Seam-Weld Hole)**：孔周圓弧塑性應變超標長度達到 $1/4$ 圓周長度。
  3. **螺栓/銷釘固定孔 (Standoff Hole)**：孔周圓弧塑性應變超標長度達到 $1/2$ 圓周長度。

### 2.2 塑料零件 (Plastic Components: PC+ABS Cycoloy C6200)
- **動態衝擊開裂門檻**：$\text{EPS} \ge 0.0100$ 且應變帶連續貫穿整個零件斷面。
- **靜態強度門檻**：Von-Mises 應力必須小於材料屈服極限 $\sigma_y \approx 55\text{ MPa}$。

### 2.3 BGA / CSP 焊點 (SAC305 Solder Joints)
- **等效塑性應變門檻**：$\text{EPS} \ge 0.0022$ ($0.22\%$)。
- **網格建模要求**：焊點直徑通常在 $0.4\sim 0.6\text{ mm}$，高度方向必須至少劃分 3 層六面體單元，提取最外層近焊盤界面處的單元平均值。

---

## 3. 安全裕度與等級分類 (Safety Margin Classification)

定義安全裕度（Margin of Safety, MoS）：
$$\text{MoS} = \frac{\text{Threshold} - \text{Max EPS}}{\text{Threshold}}$$

- **PASS（合格）**：$\text{MoS} > 0.15$（即 $\text{Max EPS} < 0.85 \times \text{Threshold}$），結構無破壞風險。
- **MARGINAL（臨界邊緣）**：$0.00 \le \text{MoS} \le 0.15$（即應變處於門檻的 $85\% \sim 100\%$），結構雖未破壞但安全裕度不足，標註為高風險並建議結構優化。
- **FAIL（失效破壞）**：$\text{MoS} < 0.00$（即 $\text{Max EPS} \ge \text{Threshold}$）且滿足貫穿條件，判定產品結構測試不合格，必須開立工程變更（ECR）。
