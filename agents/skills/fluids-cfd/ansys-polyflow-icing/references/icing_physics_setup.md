# FENSAP-ICE 結冰物理參數設定

> [!NOTE]
> 本手冊依據官方知識字典 `polyflow.md` 與 `polyflow` 權威技術規格擴充，提供深度工程指導。

## 1. 原理與設定準則

本模組於高精度數值模擬時，必須遵循以下邊界設定與收斂規範：
- 數值精度與單位一致性：務必先確認全域坐標系統、材料參數庫與求解單位（MKS/SI）。
- 網格劃分策略：實施局部特徵網格加密，並於梯度變化劇烈區域進行自適應細化。
- 監控物理量：除了求解器預設殘差之外，必須定義面通量、力矩或特徵頻率等客觀物理監控器。

## 2. 核心規範與字典精要

# Ansys Polyflow 知識字典

本頁以繁中整理有界主題，區分 Polyflow Classic v242（2024 R2）與 Fluent Polyflow workspace v261（2026 R1）。官方 HTML 僅核讀所列段落，未鏡像原文；本機 Polyflow 目錄只有 README，沒有 PDF／HTML 或轉換產物。整本指南、方程圖片、完整圖表及案例仍未整理。來源 ID 供主代理整合清冊後追溯，不能據此宣稱已加入 SQLite。

## Classic 子域、邊界與版本比較

`subdomain` 是有限元素集合；`boundary set` 是外部計算域邊界的 connectors 集合。不同 sub-task 交界需要介面邊界條件；同一 sub-task 內的子域交界不需重複設定。外部 boundary sets 的聯集須覆蓋整個外邊界。自由表面鄰接的子域需要 remeshing。

| 核讀項目 | v242 | v261 |
| --- | ---: | ---: |
| subdomains 上限 | 300 | 300 |
| boundary sets 上限 | 500 | 500 |
| PMeshes 上限 | 10,000 | 10,000 |

只確認所列定義、邊界規則與上限相同，沒有比較整本手冊。此處 v261 依據為可讀 HTML，PDF 本輪因回應大小限制未取得。

[1.5.2 Subdomains and Boundary Sets](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/poly_pf/x1-180002.4.2.html) · `official_polyflow_subdomains_v242`

[1.5.3 Boundary Conditions](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/poly_pf/x1-190002.4.3.html) · `official_polyflow_boundary_conditions_v242`

[1.5.2 Subdomains and Boundary Sets](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/poly_pf/x1-180002.4.2.html) · `official_polyflow_subdomains_v261`

[1.5.3 Boundary Conditions](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/poly_pf/x1-190002.4.3.html) · `official_polyflow_boundary_conditions_v261`

v242 known limitations：limited Academic License 不能載入超過 1,000,000 elements 的網格；SpaceClaim meshing 不支援建立 Polyflow shell mesh；MST moving parts 上限為 10；CutCell 不支援包括 VOF、viscoelastic sub-tasks、adaptive meshing 等功能。這是例示，須回原頁核對完整限制，不能外推到 v261。

[Polyflow 2024 R2 Known Limitations](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/poly_pf/pf_ug_sec_start_limit.html) · `official_polyflow_limitations_v242`

## Classic 分析規劃與單位（v242）

先定義工程問題、精度需求、計算域與維度，再選邊界、熱傳、穩態／非穩態及 staged／evolution 策略，估計記憶體與計算時間。

[1.4.1 Planning Your Ansys Polyflow Analysis](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/poly_pf/x1-120002.3.1.html) · `official_polyflow_planning_v242`

Classic 預設由使用者維持單位一致。單位切換只轉換材料性質，不會自動轉換邊界條件中的速度、流量、溫度、力、表面張力，亦不轉換 PMAT dependence parameters。轉換後應逐項核對。

[Units Overview](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/poly_pf/pf_ug_sec_units_overview.html) · `official_polyflow_units_v242`

## Classic 流變模型（v242）

| 模型 | 核讀定義與參數語意 | 原文位置 |
| --- | --- | --- |
| Bird-Carreau | 描述低剪切黏度平台；參數包含 infinite-shear-rate viscosity、zero-shear-rate viscosity、natural time、power-law index | §10.2.2.3 |
| Cross | 同樣描述低剪切平台；含 zero-shear-rate viscosity、natural time、Cross-law index；與 Bird-Carreau 主要差在平台到 power-law 區域的曲率 | §10.2.2.4 |

natural time 是 Newtonian 到 power-law 行為轉換剪切率的倒數。兩種模型屬 generalized Newtonian 黏度律，不能僅由名稱推定具黏彈記憶。原頁公式與多個符號以圖片呈現，本輪未轉錄方程或猜測符號，也未提供材料建議值。

[10.2.2 Shear-Rate-Dependent Viscosity Laws](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/poly_pf/pf_ug_sec_newton_theory_viscosity_isothermal.html) · `official_polyflow_viscosity_laws_v242`

Phan-Thien-Tanner（PTT）是 differential viscoelastic 模型，可表達 shear thinning 與高剪切率下非二次的一次正應力差。多模態模型的純黏性貢獻只由第一模態定義；其餘模態不可重複加入。PTT 公式及符號需回 §11.2.1.3.4 圖式核對。

[11.2.1 Theory and Equations](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/poly_pf/pf_ug_sec_visco_differential_theory.html) · `official_polyflow_differential_theory_v242`

模型選擇應對應實際工作剪切率範圍內的實驗行為；並非只追求高 Weissenberg number。Maxwell 雖為簡單方程，數值上可能困難；White-Metzner 可能有高剪切振盪，官方列 PTT、Giesekus、FENE-P 為較優先的候選。這些是該頁條件式指引，沒有取代流變實驗、參數擬合及獨立驗證。

[11.2.3 Choosing the Differential Viscoelastic Model](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/poly_pf/pf_ug_sec_visco_differential_choosing.html) · `official_polyflow_model_selection_v242`

## Fluent Polyflow Workspace（v261）

Workspace 是 Classic 的 successor，面向高黏度材料加工；兩個介面的流程與功能不可直接視為相同。頁面列的安裝前置包含相應 CFD license、Polyflow Classic、EnSight 與有效 `%HOME%`。功能會依 license level 改變，完整 entitlement 仍需核對授權矩陣。已知限制包含 editor 開啟時不可修改 Workbench Polyflow system、路徑不能含逗號、避免在 OneDrive 目錄執行及 limited Academic License 的 1,000,000 elements 限制。

[2.1 Introduction to the Polyflow Workspace](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/flu_ug_workspaces/flu_man_sec_intro.html) · `official_polyflow_workspace_intro_v261`

工作流程：定義目標 → 準備相容網格 → 啟動／讀網格 → 手動建立物件或套用 template／wizard → 計算 → 檢視及儲存結果。wizard 的範圍限所列簡單 direct／inverse extrusion 與 blow molding，不能推及所有模型。

[2.2 Getting Started](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/flu_ug_workspaces/flu_ws_man_sect_getting_started.html) · `official_polyflow_workspace_getting_started_v261`

### 網格、單位與紀錄

讀網格時 topology names 會轉小寫。Workspace 使用 MKS，網格座標轉為公尺；Fluent mesh 預設以公尺解讀，不再出現單位詢問。對舊 mesh 應確認原始長度單位，避免與 Classic 的材料單位切換混淆。工作目錄必須可寫。

Session 使用 `*.mprcas`，console transcript 為 `*.trn`，Python journal 為 `*.py`。三者用途不同，不能把 transcript 當作可直接重播的 journal。

[2.4 Reading and Writing Files](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/flu_ug_workspaces/flu_ws_man_sect_mesh.html) · `official_polyflow_workspace_files_v261`

### 幾何、計算型態與收斂控制

General Properties 中 planar 為 Vz=0、channel 為 Vz≠0；axisymmetric 以 Y 軸對稱且 Vw=0，swirling 則 Vw≠0。Calculation Type 包含 Steady、Continuation、Transient、Volume of Fluid（填充暫態）。Methods Properties 的 Picard iterations 用來增加穩健性，官方建議在黏度模型變化很大時考慮；實際穩定性與精度仍須依案例檢查。

[2.15 Polyflow Workspace Reference Guide](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/flu_ug_workspaces/flu_chp_man_reference_guide.html) · `official_polyflow_workspace_reference_v261`

## 內部提示與尚未涵蓋

內部共用技能列出 die swell、blow molding、free-surface adaptive remeshing 等檢索詞；其中 FENSAP-ICE 段落不能當作 Polyflow 能力。87 字短箋僅列 PTT、Giesekus、K-BKZ 名稱，不能證實材料參數、完整操作或適用性。此父題仍為 source_limited。

**Polyflow／FENSAP-ICE Skill** · `agents_skills_fluids-cfd_ansys-polyflow-icing_SKILL`；**Viscoelastic models note** · `agents_skills_fluids-cfd_ansys-polyflow-icing_references_viscoelastic_models`。

官方章節導覽：[Polyflow User’s Guide contents](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/poly_pf/poly_pf.html) · `official_polyflow_user_v242`

取得受阻：[Ansys Polyflow Classic User’s Guide PDF](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/pdf/Ansys_Polyflow_Classic_Users_Guide.pdf) · `official_polyflow_classic_user_v261`；[Polyflow Workspace Rheometry (URL version hint only)](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/flu_ug_workspaces/flu_ug_matpro_rheometry.html) · `official_polyflow_workspace_rheometry_failed_v261`

本輪沒有本機轉換輸入，沒有新增轉換檔或 PDF 頁錨點。官方 HTML 只存摘要與 URL，未完成全手冊、圖表／公式辨識、完整授權矩陣、所有 workspace objects、全部材料模型與跨版限制比較。未啟動 Polyflow 或求解；分享前遵守現有來源使用限制及公開發佈檢查。


## 2026-11-04：Wave 10 本機來源盤點與限制說明

本批完成 polyflow 模組既有本機 catalog 文件（共 0 筆）與 sources 清冊（共 19 筆）之完整雜湊、正文路徑與標籤結構核對。本機未快取或具備企業授權/登入限制之線上主題誠實標記為缺口（保持現有非 complete 狀態），未擅自虛構未核實之線上 API 簽名或執行求解運算。

詳細稽核數據見 **本批轉換報告**。

## 3. 常見陷阱與防呆措施

1. **未定義求解範圍**：求解前未限定掃頻範圍或時間步長，導致求解發散。
2. **材料模型失配**：非線性材料未設定適當的切線模數或溫度相依曲線。
3. **介面通訊失敗**：多物理場耦合未對齊變數傳遞單位，導致數值非物理震盪。
