---
name: ansys-mechanical
description: ANSYS Mechanical 結構剛強度、模態與熱-結構耦合分析主控手冊。涵蓋 ACT 腳本、非線性接觸、網格前檢與奇異點判定。
Use when:
  - 需進行靜態結構強度剛度校核、固有頻率模態分析或熱應力序列耦合。
  - 需透過 ACT / PyMechanical 腳本配置非線性接觸、網格控制與大變形求解。
  - 需排查求解器主元錯誤 (Pivot Error)、殘差發散或聖維南應力奇異點。
  - 限制: 需在 Mechanical ACT 環境或透過 PyMechanical 連線執行。
  - 觸發關鍵字 (繁中/En): Mechanical分析, 靜態結構, 模態分析, 熱應力分析, PyMechanical, ACT腳本.
---

# ANSYS Mechanical 結構與熱分析主控手冊

本技能提供標準化 ANSYS Mechanical ACT 自動化分析框架，整合靜態強度、模態振動與熱-結構耦合三大標準流程，並嚴格落實網格品質預檢、力學收斂診斷與工程判斷力評估。

---

## 一、核心物件進入點 (Entry Handles)

在 Mechanical ACT 腳本環境中，預設全域物件 handle 如下：

```python
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS
Model       = DataModel.Project.Model       # 頂層幾何與模型核心
Mesh        = Model.Mesh                    # 網格控制核心
Connections = Model.Connections             # 接觸與連接群組
Analysis    = Model.Analyses[0]             # 當前活動分析系統 (如 Static Structural)
Settings    = Analysis.Children[0]          # 求解分析設定 (Analysis Settings)
Solution    = Analysis.Solution             # 求解與後處理結果核心
```

---

## 二、三大標準工作模式 SOP

```mermaid
flowchart LR
    A[1. 幾何與材料] --> B[2. 網格劃分與前檢]
    B --> C[3. 接觸與邊界載荷]
    C --> D[4. 求解器參數配置]
    D --> E[5. 求解與收斂診斷]
    E --> F[6. 後處理與判斷力校核]
```

### 1. 靜態結構分析 SOP (Static Structural)
1. **單位與材料**：設定系統單位制（MKS/NMM），匯入 XML 工程材料庫並指定至主體（Body）。
2. **網格劃分與前檢**：依幾何特徵設定 Sizing 與 Method；**強制檢驗網格品質**（歪斜度 Skewness < 0.85、正交品質 > 0.15），未達標嚴禁求解。
3. **接觸與連接**：定義裝配體接觸對（Contact Regions），指定接觸公式（Augmented Lagrange）與穿透控制。
4. **邊界與載荷**：施加固定約束（Fixed）、位移（Displacement）及載荷（Force/Pressure），**嚴格防範剛體位移**。
5. **求解控制**：配置大變形開關（Large Deflection）、載荷步與自動副步（Auto Time Stepping）。
6. **求解與後處**：執行求解，提取位移、等效應力（von-Mises）及安全係數，並導出白底結果雲圖。
7. **判斷力校核**：檢驗應力集中處是否為數值奇異點（聖維南原理檢驗與節點未平均斷差比對）。

### 2. 模態分析 SOP (Modal Analysis)
1. **幾何與材料**：確認材料密度（Density）、彈性模數（Young's Modulus）與泊松比已完整定義。
2. **網格控制**：薄壁件確保厚度方向至少 3 層單元或採用薄殼單元，避免剪切自鎖高估固有頻率。
3. **邊界設置**：定義無約束自由態（前 6 階為 0 Hz 剛體模態）或實際工況約束態（Fixed/Displacement）。
4. **求解器設定**：配置模態提取演算法（Block Lanczos）與提取階數（通常為前 6 ~ 20 階）。
5. **求解與提取**：執行求解，提取各階固有頻率（Natural Frequencies）與相應總變形振型雲圖。

### 3. 熱應力序列耦合 SOP (Thermal-Stress Coupling)
1. **熱分析求解**：在熱分析系統中施加溫度、熱流率或對流換熱係數（HTC），完成溫度場求解。
2. **結構環境配置**：建立靜態結構分析系統，共享幾何與材料模型（必須包含熱膨脹係數 CTE）。
3. **體溫度導入**：在結構分析建立 `Imported Body Temperature`，載入熱分析對應時間步之溫度場。
4. **無應力參考溫度**：指定結構無應力參考環境溫度（Environment Temperature，通常為 20°C 或 22°C）。
5. **力學約束與求解**：設定結構支撐以約束剛體運動且容許熱脹冷縮；執行非線性應力求解。

---

## 三、模組路由表 (Module Router)

執行各分析步驟時，請查閱 `reference/` 目錄專精手冊：

| 分析階段 / 核心問題 | 推薦專精子手冊 | 核心內容要點 |
|---|---|---|
| 材料導入與批次映射 | [`reference/materials.md`](reference/materials.md) | XML 材料庫匯入、EngineeringData、溫變非線性屬性指派 |
| 網格尺寸、方法與品質檢驗 | [`reference/mesh.md`](reference/mesh.md) | Sizing、Method、網格品質量化評估標準 (Skewness/Orthogonal) |
| 接觸對建立、穿透與震盪 | [`reference/connections_and_contacts.md`](reference/connections_and_contacts.md) | 接觸對公式、法向剛度、Pinball 範圍、穩定化阻尼 |
| 約束條件、載荷施加與螺栓 | [`reference/boundary_conditions_and_loads.md`](reference/boundary_conditions_and_loads.md) | 固定約束、位移自由度、壓力、螺栓預緊三步載荷法 |
| 載荷步、大變形與求解器控制 | [`reference/analysis_setup.md`](reference/analysis_setup.md) | Large Deflection、自動副步細分、Newton-Raphson 控制 |
| 結果評估、雲圖導出與 DPF | [`reference/results_and_postprocessing.md`](reference/results_and_postprocessing.md) | 應力/變形提取、Graphics.ExportImage、DPF 高速場讀取 |
| 收斂曲線診斷、無關性、奇異點 | [`reference/mechanical_judgment.md`](reference/mechanical_judgment.md) | 力殘差收斂判讀、GCI 無關性指標、聖維南原理判定 |
| 多物理場耦合、CFD 負載映射與過渡 | [`reference/multiphysics_mapping.md`](reference/multiphysics_mapping.md) | 熱-結構弱耦合、Fluent 壓力/HTC 映射、聖維南平滑準則 |
| 求解報錯（主元錯誤、不收斂）自愈 | [`reference/solver_diagnostics.md`](reference/solver_diagnostics.md) | Pivot Error、Convergence Failure 自愈對策表 |

示範腳本推薦：
- [`scripts/run_static_structural_demo.py`](scripts/run_static_structural_demo.py)：標準靜態剛強度與模態分析 ACT 示範。
- [`scripts/run_taylor_bar_demo.py`](scripts/run_taylor_bar_demo.py)：泰勒桿高速衝擊大變形、OFHC 銅動態降伏推算與沙漏能診斷。
- [`scripts/check_mesh_quality.py`](scripts/check_mesh_quality.py)：網格歪斜度與正交品質自動化預檢。

---

## 四、絕不能做清單 (Don'ts)

> [!CAUTION]
> 1. **嚴禁在未檢查網格品質（歪斜度/正交品質）下直接求解**：
>    歪斜度 Skewness > 0.85 或正交品質 Orthogonal Quality < 0.15 的劣質單元會導致剛度矩陣嚴重病態，引發不收斂或虛假局部高應力。求解前必須調用檢驗腳本確認放行。
> 2. **嚴禁對薄壁板金零件使用粗實體單元**：
>    壁厚方向僅有 1 層一階四面體（SOLID185）會引發嚴重的「剪切自鎖（Shear Locking）」，導致結構剛度被虛假高估數倍。薄壁件必須中面抽取改用薄殼單元（SHELL181），或在厚度方向劃分至少 3 層高階實體單元（SOLID186）。
> 3. **嚴禁在缺少約束的情況下求解靜態分析**：
>    結構必須在空間 6 個自由度（3 平移 + 3 旋轉）上具備充分約束。缺少約束將引發求解器「Small equation solver pivot（主元為零）」剛體位移錯誤。未完全固定工況需開啟弱彈簧（Weak Springs）或慣性釋放（Inertia Relief）。
