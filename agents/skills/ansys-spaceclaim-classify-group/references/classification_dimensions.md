# 幾何分類維度定義 (Classification Dimensions Reference)

本手冊定義 `classify_and_group_engine.ironpy` 使用的幾何特徵分類維度，邏輯改寫自 `D:\Ikaros\ACT_Test\SC_RM\SC_RM_grp_creation\SC_RM_grp_creation.py` 的 `FindCircles` / `ConvertEdgesByShape` 判準。

---

## 一、孔徑篩選維度 (Diameter Filtering)

| 參數 | 原始 ACT Properties 名稱 | 通用引擎參數名稱 | 說明 |
|---|---|---|---|
| 最小孔徑 | `Diameter_min`（經 `MM()` 轉換） | `diameter_min_mm` | 篩選下限，單位 mm，內部轉換為公尺進行半徑比較。 |
| 最大孔徑 | `Diameter_max`（經 `MM()` 轉換） | `diameter_max_mm` | 篩選上限，單位 mm。 |

篩選邏輯：對邊集合先 `ConvertToEdges()` 再 `ConvertByShape(GeometryType.Circle)`，取得圓形邊後以 `FilterByRadius(D_min/2, D_max/2)` 篩選半徑落在範圍內者。此三個 API（`ConvertToEdges`、`ConvertByShape`、`FilterByRadius`）均已於 `docs/api_inventory/spaceclaim_api.json` 檢索確認存在。

---

## 二、全圓 / 半圓邊判別 (Full Circle vs Half Circle)

原始引擎以 `Cmode` 參數控制三種判別模式，`classify_and_group_engine.ironpy` 保留相同邏輯但以具名常數取代魔術數字：

| Cmode | 判別條件 | 幾何意義 | 典型應用 |
|---|---|---|---|
| `0`（Full Circle） | `edge.Shape.Length > 2*pi*Radius`（NURBS/程序曲線為 `dist_pt12 == 0`，即起訖點重合） | 完整閉合圓孔（360 度） | 鎖孔、螺絲孔、圓柱銷配對 |
| `1`（Half Circle，中模式） | `0.49 * circumference < length < 0.51 * circumference` | 近似半圓邊（約 180 度） | 卡勾、半圓缺口定位結構 |
| `2`（Half Circle，寬模式） | `length < 0.5 * circumference` | 小於半圓的弧邊 | 不規則缺口、局部圓弧特徵 |

**非圓曲線（NURBS/ProceduralCurve）的孔位近似**：若曲線非 `Circle` 型別但起訖點距離 (`Gap.Create(pt1, pt2).Distance`) 為 0，視為近似全圓；否則以弧長反推近似直徑 `d = length / pi` 並套用相同 Cmode 判據。此為原引擎既有的近似處理，非精確解析。

**單面邊排除規則**：若邊所屬 Body 體積為 0（代表殼體/面而非實體）且該邊只關聯 1 個面（`Faces.Count != 1`），則排除出孔位清單；此規則僅適用於殼體邊，**嚴禁套用於實體 Body 的邊**（實體邊天生會關聯 2 個面，若誤套用會導致所有實體孔位被排除）。

---

## 三、未來擴充維度（厚度/曲率/位置/Component 歸屬）

SKILL.md 任務要求的分類維度除孔徑外，尚包含「厚度、曲率、位置、component 歸屬」。目前 `SC_RM_grp_creation.py` 原始引擎**僅實作孔徑與全圓/半圓判別**，以下維度為既有程式碼之外的擴充方向，標記查證狀態：

- **厚度分類**：殼體 Body 的厚度屬性存取方式，可參照既有 `ansys-mechanical/scripts/bonded_contact_creator.py` 或 `ansys-mechanical-section-assign` 技能中已驗證的厚度 API（Mechanical 端）。SpaceClaim 原生端是否有對應的 `Thickness` Property 於 `spaceclaim_api.json` 中—— **待 api_search 查證**。
- **曲率分類**：面的曲率半徑讀取，原引擎僅用於圓形邊的 `edge.Shape.Geometry.Radius`（已確認存在），一般曲面的曲率 API（如 `Face.CurvatureAt(...)`）—— **待 api_search 查證**。
- **位置分類**：以 Body/Face 的 `BoundingBox`（已確認存在，見 `ansys-spaceclaim-interface-check` 技能）之中心座標或極值座標做空間分區，可直接複用該技能的 `GetBoundingBox` 用法。
- **Component 歸屬分類**：原引擎已實作，見 `references/pairing_strategy.md` 第一節 `CheckHierarchicalPairing`/`GetHierarchyTypeForStats`，透過 `edge.Parent.Parent`（Body 的上層 Component）比對歸屬關係。

---

## 四、分類結果資料結構

```json
{
  "holes_found": 48,
  "full_circle_count": 32,
  "half_circle_count": 16,
  "groups_created": {
    "all_holes": "Scr_AllHoles_1",
    "full_circles": "Scr_AllHoles_FullCircles_1",
    "half_circles": "Scr_AllHoles_HalfCircles_1"
  }
}
```
