# 標準件自動簡化替換 (Standard Part Replacement)

以標準件資料庫 + 三級匹配，自動把伺服器 MCAD 裝配體中的複雜標準件
（DIMM、Slot、風扇、散熱器、Standoff）換成參數化簡化幾何。

實作位置：`ACT_Test/SC_Component_Creation/Component_Creation_Tool/Component_Creation_Tool.py`、
`ACT_Test/Common_Part/Standard_DB/catalog.json`、`mcad_to_jpn_alias.json`。

## 流程

1. 讀 `catalog.json` 與別名表，掃描元件樹，計算每個元件的世界座標包圍盒。
2. 三級匹配（見下），產生候選清單。
3. 依類別呼叫 builder 建立簡化實體，名稱尾綴 `_rho<kg/m3>` 供下游自動賦材料。
4. 收攏 Named Selection：`NS_Std_<類別>_Bodies`、`NS_Std_<類別>_Mount`。
5. 原件移入 `_ORIGINAL_REPLACED_PARTS`，Hide + `SetSuppressForPhysics(True)`，**不直接刪除**
   （可逆、可追溯、可回頭做子模型）。
6. 匯出前後三視圖（Isometric / Front / Top）供人工比對。

## 三級匹配

| 層級 | 條件 | 信賴度 | 預設勾選 |
| --- | --- | --- | --- |
| T1_ALIAS | 別名表 JPN 或元件名稱含 `rules.jpn_patterns` | 1.0 | 是 |
| T2_REGEX_BBOX | `include_regex` 命中、`exclude_regex` 未命中，且排序後三軸尺寸在 `tolerance_percent` 內 | 0.9 | 是 |
| T3_GEOMETRIC | 只靠尺寸，容差收緊到 8% | 0.6 | 否（需使用者確認） |

比對用的尺寸一律先排序（最小到最大）再逐軸比，避免軸向不同造成誤判。

## catalog.json 結構（讀取時注意巢狀）

```json
"DDR5_DIMM": {
  "rules": {"include_regex": "...", "exclude_regex": "...", "jpn_patterns": ["JVPLS1070841"]},
  "spec_dimensions_mm": {"L": 128.5, "W": 6.3, "H": 27.5},
  "tolerance_percent": 15.0,
  "mass_props": {"cg_strategy": "UNIFORM_DENSITY", "density_tag": "rho1127"},
  "named_selections": {"bottom_mount": "NS_Std_DIMM_Bottom"}
}
```
Standoff 用 `D_outer` / `H_total`，讀取時要 fallback：`L/W` 缺少時取 `D_outer`，`H` 缺少時取 `H_total`。
曾因只讀頂層 `spec_L` 與 `rules` 不在頂層，造成匹配 0 筆。

## 雙密度實體（保質心與轉動慣量）

| 類別 | 組成 | 密度標籤 |
| --- | --- | --- |
| 1U Heatsink | 4 mm 銅底板 + 21.4 mm 等效鋁鰭塊 | `_rho8960_copper`、`_rho1420_equiv_al` |
| 6056 Fan | 外框 + 內部轉子芯 | `_rho780`、`_rho3200` |
| DIMM / Slot / Standoff | 單一均質 | `_rho1127` / `_rho1350` / `_rho8500_brass` |

單一均質方塊會讓散熱器重心偏高，在衝擊與落摔分析中產生假性傾覆力矩。

## 軸向判定

`detect_axes_from_spec` 以「最接近寬度的軸 = 寬，其餘最接近長度的軸 = 長」判定，最後一軸為高。
限制：只看 World AABB，旋轉或傾斜姿態的零件、非對稱零件（L 型支架、側吹風扇）會判錯。
Mount 面目前取各實體第一個面，未做底面判定。

## 實測基準（20 件合成主機板）

- 378 面 -> 142 面（-62.4%），耗時約 2.7 s。
- 20/20 匹配：T1 共 12 件（DIMM x4、Standoff x8），T2 共 8 件（Slot x4、Fan x2、Heatsink x2）。
- 前後三視圖與 `benchmark_comparison_report.txt` 位於 `Common_Part/Standard_DB/screenshots/`。

## 已知限制與後續

1. Mount 面改為相對零件主軸或與 PCB 共面判定。
2. 提供自動 Share Topology 選項，減少 Mechanical 接觸對數量。
3. 依實際 BBox 體積動態重算 `_rho`，避免尺寸在容差內偏差時質量失真。
4. 實測用的是合成方塊模型，尚未驗證真實 CAD（含 `.prt.1` 版本後綴、廠編命名）的匹配率。

## 相關錯誤

API 陷阱與桌面隔離見 [`ansys-error-catalog/references/spaceclaim_pygeometry.md`](../../ansys-error-catalog/references/spaceclaim_pygeometry.md)
的 ERR-SC-004 至 011，以及 [`ansys-spaceclaim/references/native_session_and_versions.md`](../../ansys-spaceclaim/references/native_session_and_versions.md)。
