# 超彈性與黏彈性材料模型選型指南 (hyperelastic_viscoelastic_materials.md)

本手冊補充 ANSYS Mechanical 超彈性（橡膠、彈性體）與黏彈性（高分子聚合物、電子封裝膠材）材料模型的選型依據與參數意義，是本 skill 全新主題（既有 `materials.md` 只涵蓋線彈性/塑性批次指派，未涉及這兩類非線性材料模型）。來源：Ansys Mechanical Nonlinear Materials for Elastomers 2021 R1 官方培訓教材 M01/M01A/M02/M03。

---

## 一、超彈性模型選型四大依據

1. **可獲得的材料實驗數據**：單軸拉伸、等雙軸拉伸、平面剪切、體積壓縮，數據完整性直接限制模型選擇範圍。
2. **應變範圍與載荷條件**：小應變（<30%）、中等應變（<100%）、大應變（>100%~300%）。
3. **材料類型與可壓縮性**：密實橡膠近乎不可壓縮；多孔泡沫橡膠需要體積與偏量耦合的可壓縮模型。
4. **擬合精度與數值穩定性**：最優模型是最貼近實驗曲線、且在分析應變範圍內滿足 Drucker 穩定性的模型。

## 二、常用模型選型決策表

| 材料測試數據狀況 | 預期應變範圍 | 推薦模型 | 選型依據 |
|---|---|---|---|
| 僅單軸拉伸數據 | 小應變（<30~40%） | **Neo-Hookean** | 結構最簡單、計算快，適合初步評估；不捕捉大應變硬化效應 |
| 僅單軸拉伸數據 | 中大應變（>100%） | **Yeoh（N=3）** 或 **Arruda-Boyce** | 僅依賴第一應變不變量 $I_1$，忽略 $I_2$ 可避免單軸數據外推失真，對多軸變形預測性最好 |
| 多軸完整數據（單軸+雙軸+剪切） | 中低應變（<90~100%） | **2-term Mooney-Rivlin** | 經典穩定，中低應變貼合良好；但剪切模量為常數，無法捕捉大應變硬化 |
| 多軸完整數據 | 大應變且要求高精度 | **Ogden（N≥3）** 或高階 Polynomial | 直接基於主伸長率擬合，精度最高，但計算成本略高 |
| 高可壓縮泡沫橡膠 | 任何應變 | **Ogden Compressible Foam** 或 **Blatz-Ko** | 體積與偏量應變強耦合，Blatz-Ko 隱含 $\nu = 0.25$ |

### 模型細節補充

- **Mooney-Rivlin / Polynomial Form**：ANSYS 提供 2/3/5/9-term 形式，是 Polynomial Form 的特例。N=2 或 N=3 可用到 100~300% 應變，但 N>3 很少使用。
- **Yeoh（Reduced Polynomial）**：常用 N=3（Cubic Form）：$c_{10}$ 為正（約為初始剪切模量一半）、$c_{20}$ 為負（小應變軟化，約 $0.01\sim0.1 \times c_{10}$）、$c_{30}$ 為正（大應變硬化，約 $10^{-4}\sim10^{-2} \times c_{10}$）。
- **Ogden**：建議至少 3 項。第一項代表小應變（$1.0<\alpha_1<2.0$）、第二項代表大應變硬化（$\alpha_2>2.0$，$\mu_2 \ll \mu_1$）、第三項代表壓縮行為（$\alpha_3<-0.5$，$\mu_3 \ll \mu_1$）。
- **Neo-Hookean**：Mooney-Rivlin 的特例（N=1，$c_{01}=0$）。有效拉伸範圍 30~40%，壓縮範圍到 30%。

## 三、Drucker 穩定性檢查（求解前自動執行）

ANSYS 在求解初期自動檢查切線剛度矩陣是否在伸長率 $0.1 \sim 10.0$ 範圍內保持正定（單軸、等雙軸、平面剪切，拉伸與壓縮各算一次，共六種應力路徑）。若收到穩定性警告：

- 通常代表實驗數據覆蓋範圍不足，或模型階數過高導致外推失真。
- 處理方式：切換到對數據量要求較低的模型（如從高階 Polynomial 降回 Yeoh），或補齊多軸測試數據。
- 穩定性檢查失敗不代表求解一定會失敗，但是收斂困難的常見前兆（negative/small pivot 警告的根因之一）。

## 四、黏彈性模型（Prony Series）

適用材料：高分子聚合物、電子封裝膠材（Underfill、Mold Compound）、玻璃。基於廣義 Maxwell 模型：

$$G(t) = G_0 \left[ \alpha_\infty^G + \sum_{i=1}^{N} \alpha_i^G e^{-t/\tau_i^G} \right]$$

### 關鍵參數

| 參數 | 意義 |
|---|---|
| $G_0$（瞬時模量） | $t=0$ 時材料初始剛度；與超彈性模型結合時由應變能函數係數自動算出 |
| $G_\infty$（長期模量） | $t \to \infty$ 應力完全鬆弛後的殘餘模量 |
| $\alpha_i$（相對模量） | 無因次比值 $G_i/G_0$，代表第 $i$ 個 Maxwell 單元佔總瞬時模量的衰減比例；$\sum \alpha_i \le 1$，若等於 1 代表 $G_\infty = 0$ |
| $\tau_i$（鬆弛時間） | 當 $t = \tau_i$ 時，該單元的相對模量衰減到初始值的 $e^{-1} \approx 36.8\%$ |

工程實務上通常需要跨數個時間數量級（如 $10^{-3}\text{s} \sim 10^{4}\text{s}$）的多組 Prony pair 才能完整捕捉應力鬆弛/蠕變行為。數據來源：短期應力鬆弛測試（直接量 $E(t)$ 換算 $G(t)$/$K(t)$）或 DMA 動態頻率測試（量 storage/loss modulus，需在 MAPDL 做頻域 curve fitting）。

## 五、時溫等效原理（TRS）與移位函數

高分子材料多為「熱流變簡單（Thermorheologically Simple）」：高溫短時間響應等效於低溫長時間響應，在對數時間軸上不同溫度的鬆弛曲線只做水平平移。ANSYS 用縮減時間（Reduced Time）$\xi(t) = \int_0^t dt'/A(T(t'))$ 把非等溫過程轉為等溫公式求解，$A(T)$ 即移位函數。

| 移位函數 | 公式 | 適用材料 |
|---|---|---|
| **WLF**（William-Landel-Ferry） | $\log_{10} A(T) = -\dfrac{C_1(T-T_r)}{C_2+(T-T_r)}$ | 高分子橡膠、電子封裝膠材（Underfill、Mold Compound），常以 $T_g$ 為參考溫度 |
| **TN**（Tool-Narayanaswamy，本質是 Arrhenius 式） | $\ln A(T) = \dfrac{C}{R}\left(\dfrac{1}{T_r}-\dfrac{1}{T}\right)$ | 玻璃產業；可擴充引入虛構溫度（Fictive Temperature）描述冷卻過程的結構鬆弛 |

$C_1$、$C_2$ 雖通常在玻璃轉化溫度 $T_g$ 評估，但不限於此，可在任意參考溫度 $T_r$ 評估。WLF 與 TN 是兩個獨立的函數家族（WLF 用溫度差的有理函數形式，TN 本質是 Arrhenius 溫度倒數差形式），公式結構不同是函數家族本身的差異，不是誤植；兩者皆透過 `TB,SHIFT` 指令指定 $T_r$ 與對應常數。

## 六、分析設定注意事項

- 黏彈性模型必須搭配線彈性（EX & NUXY）或非線性超彈性材料才算完整定義。
- 黏彈性與超彈性結合使用時，**Large Deflection 必須設為 ON**。
- 時間步長需確保足夠小，尤其在溫度變化較快或應力陡降的鬆弛初期階段；溫度變化應在單個 substep 內保持線性假設成立的小幅度。
- 大型模型且求解耗時長時，建議設置 Restart Control 策略，以應付需要調整時間步範圍或收斂準則的情況。

## 七、與 PCB Warpage 分析的關聯

`pcb-warpage-analysis` skill 中的 underfill、mold compound 材料本構若涉及應力鬆弛或溫度相關的黏彈性行為，可參照本檔第四、五節的 Prony series 與 WLF 移位函數設定；若只做純熱-結構線彈性分析（目前 `pcb-warpage-analysis` 預設流程），不需要本檔內容。
