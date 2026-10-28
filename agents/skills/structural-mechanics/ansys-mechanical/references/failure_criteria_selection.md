# 失效準則選用決定表 (Failure Criteria Selection)

本手冊整理 ANSYS Mechanical 中依材料延展性/脆性/各向異性特性選用對應失效準則的工程判斷依據，與 Stress Tool / Composite Failure Tool 的設定要點。

> 來源說明：理論依據改寫自 NotebookLM 筆記本「Ansys Official」技術發布影片與教學示範之查詢結果，並以自身工程知識補充力學推導脈絡；未逐字搬運原文。

---

## 一、三大失效準則決定表

| 材料特性 | 推薦準則 | 力學假設 | ANSYS Mechanical 對應工具 |
|---|---|---|---|
| **延性金屬**（鋼、鋁合金等等向性材料） | **von Mises（Max Equivalent Stress）** | 畸變能理論（Distortion Energy Theory）：材料降伏由多軸應力狀態轉換成單一等效應力 $\sigma_e$ 判定，與延性金屬實驗降伏數據吻合度高 | **Stress Tool → Max Equivalent Stress Safety Factor**，安全係數 $= \sigma_{yield} / \sigma_e$ |
| **延性金屬（保守評估）** | **Tresca（Max Shear Stress）** | 最大剪應力理論：以 $\tau_{max} = (\sigma_1-\sigma_3)/2$ 對比剪切降伏極限（常取拉伸降伏強度之 0.5 倍），其降伏邊界完全包覆於 von Mises 邊界內，故評估結果較保守 | **Stress Tool → Max Shear Stress**，適用壓力容器、航太等高安全餘裕規範場景 |
| **脆性材料**（鑄鐵、陶瓷、玻璃等） | **Max Principal Stress（最大主應力/Rankine 準則）** | 脆性材料破壞模式以單軸拉伸開裂為主，不具延性金屬的塑性流動重分配能力，故直接以最大主應力對比抗拉極限強度判定，不轉換為等效應力 | **Stress Tool → Max Tensile Stress Safety Factor** |
| **連續纖維複合材料層合板** | **Tsai-Wu / Tsai-Hill / Max Stress / Max Strain**（四準則可並行比對） | 各向異性材料的強度隨方向與拉壓性質不同，傳統等向性等效應力準則無法反映纖維/基材/層間的獨立破壞模式，需用複合材料專屬準則 | **Composite Failure Tool**（需先由 ACP 疊層定義傳遞至 Static Structural） |

---

## 二、複合材料四大失效準則細部比較

| 準則 | 性質 | 核心差異 |
|---|---|---|
| **Tsai-Wu** | 交互作用二次張量多項式準則 | 考慮 $\sigma_1, \sigma_2, \tau_{12}$ 間的交互耦合效應，並區分拉伸/壓縮強度差異；屬泛用型整體風險篩選準則 |
| **Tsai-Hill** | 基於畸變能的交互作用準則 | 由正交異性材料屈服條件演化而來，考慮應力方向組合作用，但預設不嚴格區分同方向拉壓強度差異 |
| **Max Stress** | 非交互作用準則 | 各應力分量（纖維向 $\sigma_1$、基材向 $\sigma_2$、面內剪切 $\tau_{12}$）分別獨立對比各自許用強度（$X_T, X_C, Y_T, Y_C, S$），能直接標示具體破壞模式（如 S1T 纖維拉伸破壞、S2T 基材橫向拉伸破壞） |
| **Max Strain** | 非交互作用應變準則 | 以主軸應變 $\varepsilon_1, \varepsilon_2, \gamma_{12}$ 對比極限應變，同樣不考慮方向交互作用 |

**工程選用建議**（改寫自同一來源的實務經驗分享）：
- 初步篩選/預設計階段：使用 Tsai-Wu 或 Max Stress 即可。
- 安全關鍵結構的細部設計階段：建議**同時啟用至少兩種性質不同的準則**（例如 Max Stress 搭配 Tsai-Wu），若兩者在同一區域皆標示為高風險，代表該處失效風險的判斷更為可靠。
- 若結構以纖維方向受拉為主導（Fiber-dominated，如航太機翼結構）：優先關注 Max Stress 或類似可直接識別纖維斷裂模式的準則。
- 若結構以基材/層間行為為主導（Matrix-dominated，如層間剝離敏感的膠接接頭）：需另外考慮能涵蓋面外效應的進階準則（如 Puck、Hashin，ANSYS Mechanical 是否原生支援 **待 api_search 查證**）。

---

## 三、Composite Failure Tool 設定流程要點

1. **前置條件**：幾何與疊層資訊須先在 ACP (Pre) 模組定義完成，並以 Transfer to Shell/Solid 傳遞至 Static Structural 分析系統；單獨開啟的 Static Structural 系統無法取得複合材料失效準則選項。
2. **插入工具**：在 `Solution` 樹狀目錄右鍵 → `Insert > Composite Failure Tool`。
3. **勾選失效準則**：於 Details 面板 `Reinforcing Ply Criteria` 區域可同時勾選多個準則；特定準則（如 Max Stress）可進一步指定要考慮的應力分量（Fiber/Matrix/In-plane Shear）。
4. **結果輸出物件**：
   - **Safety Factor** 或 **Inverse Reserve Factor (IRF)**：IRF 為安全係數倒數，$\text{IRF} < 1$（即 Safety Factor $> 1$）代表結構安全。
   - **Critical Failure Mode**：標註導致最危險狀況的破壞模式縮寫（如 S2T = 橫向拉伸基材破壞）。
   - **Critical Layer**：標示整個疊層中最先達到臨界失效狀態的層序。
5. **座標系確認**：讀取單層應力/應變結果時應切換至 **Fiber Coordinate System**，確保結果方向與纖維主軸一致，避免與全域座標系混淆誤判。

> ANSYS Mechanical 中上述物件的具體類別名稱與屬性簽名（如 `CompositeFailureTool`、`InverseReserveFactor` 等 ACT/PyMechanical API）未經 `api_search` 驗證，實作前**待 api_search 查證**，避免直接套用本文件中未標註來源的程式碼。

---

## 四、常見誤用提醒

> [!CAUTION]
> 1. **嚴禁對複合材料層合板套用等向性 von Mises 等效應力判定失效**：複合材料的強度具方向相依性與拉壓不對稱性，等向性等效應力準則無法反映纖維斷裂、基材開裂與層間剝離等獨立破壞模式，必須使用 Composite Failure Tool。
> 2. **嚴禁僅憑單一失效準則判定複合材料結構安全**：不同準則對同一應力狀態可能給出不同安全係數，單一準則可能低估風險；安全關鍵結構應交叉比對至少兩種準則。
> 3. **脆性材料嚴禁使用 von Mises 判定**：von Mises 假設材料具塑性流動重分配能力，脆性材料無此機制，套用會低估真實破壞風險，應改用 Max Principal Stress。
