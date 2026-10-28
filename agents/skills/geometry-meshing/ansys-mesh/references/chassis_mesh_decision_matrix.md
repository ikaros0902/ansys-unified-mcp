# 整機幾何特徵定量決策矩陣與極短邊熔斷手冊

本手冊定義已進入 ANSYS Mechanical 之整機模型（Full-Chassis Assembly）在完全尊重當下幾何激活狀態下的幾何特徵量化提取公式、`Mesh Method` 路由判定、`Mesh Size` 定量計算與極短邊預檢熔斷標準。

---

## 一、客觀幾何拓撲特徵提取公式

設待評估之未抑制實體（Unsuppressed Body）的軸對齊包圍盒（Bounding Box）三軸尺寸由大至小排序為：
$$D_{\text{max}} \ge D_{\text{mid}} \ge D_{\text{min}}$$
實體體積為 $V$，總表面積為 $A_{\text{surf}}$，總面數為 $N_{\text{faces}}$。

### 1. 等效特徵壁厚 ($t_{\text{eq}}$)
$$t_{\text{eq}} = \frac{2 \cdot V}{A_{\text{surf}}}$$
- **工程物理意義**：針對折彎鈑金件、L型/U型支架、散熱鰭片或中空框體，包圍盒 $D_{\text{min}}$ 往往因空間跨距而嚴重失真；$\frac{2V}{A_{\text{surf}}}$ 精準反映該實體在法向上的真實平均肉厚。

### 2. 薄壁展弦比 / 瘦長度 ($R_{\text{slender}}$)
$$R_{\text{slender}} = \frac{D_{\text{mid}}}{t_{\text{eq}}}$$
- $R_{\text{slender}} \ge 10$：判定為 **3D 薄壁實體件**（厚度方向對彎曲極敏感，需防剪切自鎖）。
- $R_{\text{slender}} < 10$：判定為 **厚實塊體件**。

### 3. 平面面積佔比 ($\rho_{\text{planar}}$)
$$\rho_{\text{planar}} = \frac{\sum A_{\text{plane}}}{A_{\text{surf}}}$$
- $\rho_{\text{planar}} \ge 0.70$：具備高度規則正交特徵，為 `Sweep` 或 `MultiZone` 的首選對象。

---

## 二、Mesh Method 定量選擇路由表

| 幾何特徵與量化條件 | 判定類別 | 指派 Method | 關鍵設定 | 核心效益 |
| :--- | :--- | :--- | :--- | :--- |
| `BodyType == GeoBodySheet` | 2D 薄殼件 | **`QuadDominant`** | `FreeFaceMeshType = QuadDominant` | 四邊形主導薄殼，單元數比三角形減少 50% 且抗彎精度極佳。 |
| `Solid` 且 $\rho_{\text{planar}} \ge 0.70$ 且 $R_{\text{slender}} \ge 8$ 且 $N_{\text{faces}} \le 120$ | 規則薄壁實體 (如 PCB、均厚支架) | **`Sweep`** | `SweepNumberDivisions = 2 ~ 3` | 解耦面內尺寸與厚度尺寸，面內可用大單元，單元量暴減 70%~80%。 |
| `Solid` 且 $\rho_{\text{planar}} \ge 0.75$ 且 $N_{\text{faces}} \le 200$ | 正交塊體 (如 PSU、硬碟盒、散熱底座) | **`MultiZone`** | `MappedMeshType = Hexa` | 自動分解多塊體，生成高品質 Hex Core 核心網格。 |
| `Solid` 且曲面多或異形 ($R_{\text{slender}} \ge 10$ 或 $N_{\text{faces}} > 200$) | 複雜異形件 (壓鑄件、卡扣、連接器) | **`PatchConformingTet`** | `GrowthRate = 1.25 ~ 1.30`<br/>`CurvatureNormalAngle = 24°~30°` | 貼合微小曲面特徵；配合 1.25 增長率讓內部快速過渡粗化，抑制單元暴增。 |

---

## 三、Mesh Size 定量計算依據表

| 零件特徵分類 | 計算主導因子 | `Element Size` 計算公式 | 邊界約束 (Clamping) |
| :--- | :--- | :--- | :--- |
| **1. 2D 薄殼件 (`Sheet`)** | 次大尺度 $D_{\text{mid}}$ | $$S_{\text{shell}} = \frac{D_{\text{mid}}}{20}$$ | $\text{clamp}(S, 2.0\text{ mm}, 8.0\text{ mm})$ |
| **2. 可 Sweep 薄壁實體** | 面內尺度與壁厚 $t_{\text{eq}}$ | **面內**：$S_{\text{in}} = \min(D_{\text{mid}}/15, 4.0 \cdot t_{\text{eq}})$<br/>**厚度**：`Divisions = 2 ~ 3` | 面內長寬比 $\le 8.0$ |
| **3. 不可 Sweep 薄壁實體** | 等效壁厚 $t_{\text{eq}}$ | $$S_{\text{tet\_thin}} = 1.2 \cdot t_{\text{eq}}$$ | $\text{clamp}(S, 0.8\text{ mm}, 4.0\text{ mm})$ |
| **4. 厚實塊體 / 大型次系統** | 特徵尺度 $L_{\text{char}} = (D_x D_y D_z)^{1/3}$ | $$S_{\text{block}} = \frac{L_{\text{char}}}{10}$$ | $\text{clamp}(S, 1.5\text{ mm}, 12.0\text{ mm})$ |
| **5. 圓孔特徵** | 孔直徑 $d_{\text{hole}}$ | $$S_{\text{hole}} = \frac{\pi \cdot d_{\text{hole}}}{8 \sim 12}$$ | 圓周固定 8~12 等份 + 1層 Washer |

---

## 四、極短邊預檢熔斷與視覺隔離 SOP

1. **預檢執行**：在正式劃分前調用 `chassis_mesh_gatekeeper.py`。
2. **熔斷判定**：若偵測到任何邊長 $L_{\text{edge}} < \tau_{\text{short}}$（預設 $0.25\text{ mm}$）：
   - 立即拋出熔斷例外，終止 `GenerateMesh`。
   - **視覺隔離**：`active_bodies` 中僅問題 Body 設為 `Visible = True`，其餘正常 Body 設為 `Visible = False`。
   - **自動建立 NS**：
     - `NS_ShortEdges_ALL`：全機極短邊總集。
     - `NS_Short_<BodyName>`：各問題零件專屬極短邊集。
3. **使用者確認決策**：
   - 終端印出問題幾何清單、短邊數量與最短邊長。
   - 使用者於 Mechanical 視窗聚焦檢視該 Named Selection，決定是否授權加入 `approved_defeature_bodies` 清單重新執行。
