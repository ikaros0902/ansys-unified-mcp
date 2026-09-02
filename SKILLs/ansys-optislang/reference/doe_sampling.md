# optiSLang 實驗設計與 LHS 抽樣手冊 (`doe_sampling.md`)

實驗設計（Design of Experiments, DoE）是構建高品質代理模型（Metamodel）的基石。抽樣策略必須在有限的 CAE 求解預算內，實現對多維輸入參數空間的最大程度探索。

---

## 一、拉丁超立方抽樣 (Latin Hypercube Sampling, LHS)

相較於隨機蒙地卡羅（Monte Carlo）抽樣容易產生局部樣本聚集或空白，LHS 具備優異的**分層均勻空間填充性 (Space-Filling Properties)**。

### 1. 核心數學原理
- 將每個變數的邊界區間均分為 $N$ 個機率相等的子區間。
- 每個子區間在每個變數維度上僅被抽樣一次。
- 透過隨機排列組合多維座標，保證每個維度的投影均勻分佈。

### 2. 進階空間填充準則 (Advanced Space-Filling)
在 optiSLang 中，推薦啟用 **Maximin 距離準則**：
$$\max \left( \min_{i \ne j} d(\vec{x}_i, \vec{x}_j) \right)$$
最大化任意兩樣本點間的最小歐氏距離，徹底杜絕樣本點靠得太近，提升空間覆蓋均勻度。

---

## 二、樣本容量工程估算準則

工程實務中，抽樣數量 $N$ 與輸入參數維度 $k$ 的規劃建議：

| 物理響應特性 | 推薦樣本容量公式 | 典型數值 ($k=5$ 時) | 典型數值 ($k=10$ 時) |
| :--- | :---: | :---: | :---: |
| **線性 / 弱非線性（靜力學/穩態熱）** | $N \ge 10 \cdot k$ | $N = 50 \sim 60$ | $N = 100 \sim 120$ |
| **中度非線性（塑性降伏/大位移）** | $N \ge 15 \cdot k$ | $N = 75 \sim 100$ | $N = 150 \sim 200$ |
| **高度非線性 / 接觸 / 衝擊碰撞** | $N \ge 20 \sim 30 \cdot k$ | $N = 100 \sim 150$ | $N = 200 \sim 300$ |

---

## 三、隨機參數分佈型式配置

在 optiSLang 中，參數支援多種機率分佈：

1. **均勻分佈 (Uniform Distribution)**：
   - 形式：$X \sim U(x_{\min}, x_{\max})$。
   - 應用場景：設計探索、尋優階段，所有設計區間內具有同等可能性。
2. **常態分佈 (Normal Distribution)**：
   - 形式：$X \sim \mathcal{N}(\mu, \sigma^2)$。
   - 應用場景：公差分析、製造離散性、穩健性 (Robustness) 分析。

---

## 四、optiSLang 原生 Python API 抽樣配置示範

在透過 `run_optislang_script` 發送腳本時，抽樣設定代碼如下：

```python
import actors

# 建立 Sensitivity 分析節點
sens_node = actors.SensitivityActor("Sensitivity_LHS")
add_actor(sens_node)

# 設定抽樣方法為進階拉丁超立方抽樣 (Advanced Latin Hypercube)
sens_node.set_setting("sampling_method", "advanced_latin_hypercube")
sens_node.set_setting("number_of_samples", 100)
sens_node.set_setting("criterion", "maximin")  # 最大化樣本間最小距離
```
