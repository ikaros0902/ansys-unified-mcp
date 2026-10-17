# Session 07 技術手冊：LS-DYNA 能量平衡比追蹤與數值穩定性手冊 (Energy Balance Tracking)

## 1. 物理能量守恆律 (First Law of Thermodynamics in LS-DYNA)

在顯式動力學數值求解中，能量平衡方程式（Energy Balance Equation）為判定數值解是否可信的最關鍵依據：
$$E_{\text{total}} = E_{\text{kin}} + E_{\text{int}} + E_{\text{si}} + E_{\text{rw}} + E_{\text{damp}} + E_{\text{hg}}$$
其中：
- $E_{\text{kin}}$：全系統動能（Kinetic Energy）
- $E_{\text{int}}$：內能（Internal Energy，包含彈性應變能與塑性耗散功）
- $E_{\text{si}}$：滑移接觸界面能（Sliding Interface Energy）
- $E_{\text{rw}}$：剛性牆做功（Rigid Wall Energy）
- $E_{\text{damp}}$：系統阻尼耗散能（System Damping Energy）
- $E_{\text{hg}}$：沙漏能（Hourglass Energy，非物理數值能量）

---

## 2. 能量比公式與門禁閾值 (Energy Ratio Gates)

### 2.1 能量比計算
$$\text{Ratio} = \frac{E_{\text{total}}}{E_{\text{kin}}^0 + E_{\text{int}}^0 + W_{\text{ext}}}$$
在 LS-DYNA `glstat` 輸出中，對應欄位為 `total energy / initial energy`。

### 2.2 數值門禁標準
| 能量指標 | 合格標準 (PASS) | 警告區間 (WARN) | 阻斷條件 (ABORT) | 物理機制與處置對策 |
| :--- | :--- | :--- | :--- | :--- |
| **能量平衡比 (Ratio)** | $0.98 \le R \le 1.02$ | $0.90 \le R < 0.98$<br>$1.02 < R \le 1.10$ | **$R < 0.90$ 或 $R > 1.10$** | **$R > 1.10$**：接觸剛度過大引發穿透爆炸，需降低懲罰係數；<br>**$R < 0.90$**：阻尼過大虛擬吸能。 |
| **沙漏能佔比 ($E_{\text{hg}} / E_{\text{int}}$)** | $< 5\%$ | $5\% \sim 10\%$ | **$\ge 10\%$** | 單點積分網格產生非物理零能模式，需提升沙漏係數或改用完全積分單元 (`ELFORM=16`)。 |
| **負接觸能 ($E_{\text{contact}}$)** | $\ge 0$ | $-0.05 E_{\text{tot}} \le E_{\text{c}} < 0$ | **$E_{\text{c}} < -0.05 E_{\text{tot}}$** | 節點穿透接觸面或法向顛倒，需啟用 `SOFT=2` 分割段接觸算法。 |

---

## 3. `glstat` 檔案格式與 Python 即時解析邏輯

LS-DYNA 生成之 ASCII `glstat` 檔案包含定期間隔輸出的全局統計數據：
```
 time...................................  1.000000E-03
 kinetic energy.........................  1.254000E+04
 internal energy........................  3.412000E+03
 spring energy..........................  0.000000E+00
 hourglass energy.......................  1.200000E+02
 sliding interface energy...............  4.500000E+01
 total energy...........................  1.611700E+04
 energy ratio w/o eroded energy.........  1.001200E+00
```

### Python 解析核心演算法
```python
def parse_glstat_block(text_block):
    data = {}
    for line in text_block.splitlines():
        if "kinetic energy" in line:
            data["kinetic"] = float(line.split()[-1])
        elif "internal energy" in line:
            data["internal"] = float(line.split()[-1])
        elif "hourglass energy" in line:
            data["hourglass"] = float(line.split()[-1])
        elif "total energy" in line:
            data["total"] = float(line.split()[-1])
        elif "energy ratio" in line:
            data["ratio"] = float(line.split()[-1])
            
    # 物理守恆門禁判斷
    if "ratio" in data:
        r = data["ratio"]
        if r < 0.90 or r > 1.10:
            raise ValueError(f"Energy ratio violation: {r:.4f} outside [0.90, 1.10]!")
    if "hourglass" in data and "internal" in data and data["internal"] > 0:
        hg_pct = data["hourglass"] / data["internal"]
        if hg_pct > 0.10:
            raise ValueError(f"Hourglass energy ratio {hg_pct*100:.2f}% exceeds 10% limit!")
    return data
```
