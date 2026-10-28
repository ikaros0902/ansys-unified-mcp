---
name: 08-post-process-report
description: LS-DYNA 模擬結果後處理、塑性應變場 (EPS) 提取、基於公司標準失效矩陣之客觀 PASS/FAIL 判定與自動化報告生成會話。
---

# Session 08: 後處理評估與客觀失效判定報告 (Post-Processing & Failure Evaluation Report)

## 1. 目標 (Objective)
在 LS-DYNA 衝擊分析求解完成後，自動化提取關鍵響應場量（等效塑性應變 EPS、Von-Mises 應力、接觸力），對標業界量化失效指標矩陣，並自動輸出合格判定結論與圖表報告：
1. **場量自動提取**：基於 Mechanical Solution / DPF 或 LS-PrePost 腳本，提取薄板沖孔、螺柱根部、卡扣與 BGA 焊點等高應力熱點之數值。
2. **客觀量化門禁 (Quantitative Failure Evaluation)**：嚴格執行金屬、塑料與焊點之三級分類門禁（PASS / MARGINAL / FAIL）。
3. **自動化報表交付**：輸出包含多視角應變雲圖、關鍵零件安全裕度表格的 `.xlsx` 與 `.pptx` 摘要報告。

---

## 2. 標準失效指標評估矩陣 (Quantitative Failure Criteria Matrix)

| 零件類別 | 材料範例 | 單元形態 | 工況條件 | 破壞/失效特徵 | 高風險量化判定標準 (Failure Index) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **金屬薄板** | SGCC, SPCC, SUS301 | **Shell** | 動態衝擊 (Shock) | 永久塑性變形 / 開裂 | **EPS $\ge$ 0.01** (塑性應變 $\ge 1\%$):<br>• (1) 貫穿單一完整單元 (Go-through 1 element)<br>• (2) 縫焊孔周達 1/4 圓弧<br>• (3) 螺柱/定位銷孔周達 1/2 圓弧 |
| **金屬實體** | 鋁合金 6061-T6, 螺絲 | **Solid** | 動態衝擊 (Shock) | 截面貫穿變形 | **EPS $\ge$ 0.01** 貫穿整個有效承載橫截面 |
| **塑料零件** | PC+ABS (Cycoloy C6200) | **Solid** | 靜態載荷 | 屈服變形 | **Von-Mises Stress $\ge$ 屈服強度 (Y.S $\approx 55\text{ MPa}$)** |
| **塑料零件** | PC+ABS (Cycoloy C6200) | **Solid** | 動態衝擊 (Shock) | 卡扣斷裂 / 碎裂 | **EPS $\ge$ 0.01** 且應變帶完全貫穿卡扣根部截面 |
| **BGA 焊點** | SAC305 (Sn96.5Ag3.0Cu0.5) | **Solid** (3層網格) | 動態落摔 (Drop) | 焊點錫裂 (Solder Crack) | **EPS $\ge$ 0.0022** (塑性應變 $\ge 0.22\%$) |

---

## 3. 三級評估狀態機 (Three-Tier Evaluation Logic)

```mermaid
flowchart TD
    A[提取最大塑性應變 EPS] --> B{評估材料類型}
    B -- 金屬 / 塑料 (閾值 0.01) --> C{EPS 數值}
    B -- SAC305 焊點 (閾值 0.0022) --> D{EPS 數值}
    
    C -- EPS < 0.0085 --> E[PASS: 結構安全]
    C -- 0.0085 <= EPS < 0.0100 --> F[MARGINAL: 臨界警告，需人工覆核]
    C -- EPS >= 0.0100 且截面貫穿 --> G[FAIL: 失效判定，結構需改模補強]
    
    D -- EPS < 0.00187 --> E
    D -- 0.00187 <= EPS < 0.00220 --> F
    D -- EPS >= 0.00220 --> G
```

---

## 4. 後處理自動化腳本架構 (ACT / Python Workflow)

```python
def evaluate_structural_integrity(components_data):
    results_summary = []
    for comp in components_data:
        name = comp["name"]
        mat_type = comp["mat_type"]
        max_eps = comp["max_eps"]
        is_penetrated = comp.get("cross_section_penetration", False)
        
        # 決定判定閾值
        limit = 0.0022 if mat_type == "BGA_SOLDER" else 0.0100
        
        if max_eps >= limit and is_penetrated:
            status = "FAIL"
        elif max_eps >= limit * 0.85:
            status = "MARGINAL"
        else:
            status = "PASS"
            
        safety_margin = (limit - max_eps) / limit
        results_summary.append({
            "part": name,
            "max_eps": max_eps,
            "threshold": limit,
            "safety_margin": safety_margin,
            "status": status
        })
    return results_summary
```

---

## 5. 小批次驗證章節 (Dedicated Verification Section)

本會話提供小型獨立驗證腳本，針對金屬、塑料與 BGA 焊點之塑性應變極限與截面貫穿判定進行斷言測試。

### 5.1 獨立測試腳本執行方式
```powershell
python skills/shock-analysis-workflow/scripts/test_session_08.py
```

### 5.2 驗證指標清單 (Verification Metrics)
- **金屬鈑金孔位判定 (Metal Hole Limit)**：EPS 0.01 貫穿單元準確識別
- **BGA 焊點錫裂判定 (Solder Crack Limit)**：EPS 0.0022 邊界精確捕捉
- **臨界警告分類 (Marginal Range)**：$85\% \sim 100\%$ 閾值精準分流
- **報表匯出狀態 (Report Generation)**：PASS

---

## 6. 相關參考手冊 (Related References)

| 手冊名稱 | 內容摘要 |
| :--- | :--- |
| [`../../../ansys-mechanical/references/failure_criteria_selection.md`](../../../ansys-mechanical/references/failure_criteria_selection.md) | 金屬薄板 EPS 0.01 貫穿單元、BGA 焊點 EPS 0.0022 門禁與圖表匯出實作 |
| [`../../assets/failure_report_template.md`](../../assets/failure_report_template.md) | LS-DYNA 衝擊後處理專用報告骨架，包含材料分類、EPS 門檻、截面貫穿、應變雲圖與覆核欄位 |




## Reference: failure_criteria_and_strain_limits.md

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
## 3. 安全裕度與等級分類 (Safety Margin Classification)

定義安全裕度（Margin of Safety, MoS）：
$$\text{MoS} = \frac{\text{Threshold} - \text{Max EPS}}{\text{Threshold}}$$

- **PASS（合格）**：$\text{MoS} > 0.15$（即 $\text{Max EPS} < 0.85 \times \text{Threshold}$），結構無破壞風險。
- **MARGINAL（臨界邊緣）**：$0.00 \le \text{MoS} \le 0.15$（即應變處於門檻的 $85\% \sim 100\%$），結構雖未破壞但安全裕度不足，標註為高風險並建議結構優化。
- **FAIL（失效破壞）**：$\text{MoS} < 0.00$（即 $\text{Max EPS} \ge \text{Threshold}$）且滿足貫穿條件，判定產品結構測試不合格，必須開立工程變更（ECR）。
