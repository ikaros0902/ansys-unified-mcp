# 階層配對策略細節 (Pairing Strategy Reference)

本手冊詳述 `classify_and_group_engine.ironpy` 的階層配對策略判定邏輯，完整對應 `SC_RM_grp_creation.py` 原始引擎中的 `CheckHierarchicalPairing` 與 `GetHierarchyTypeForStats` 函式，僅去除 ACT UI Properties 綁定，判定邏輯本身不變。

---

## 一、階層配對策略判定 (CheckHierarchicalPairing)

SpaceClaim 的幾何階層為 `Edge -> Body (Parent) -> Component/Part (Parent.Parent)`。配對策略決定兩條候選邊是否允許被視為一組有效配對：

| 策略名稱 | 原始 ACT Properties 選項值 | 判定邏輯 | 工程意義 |
|---|---|---|---|
| **Ignore Component** | `"Ignore Component"` | 一律回傳 `True`（不檢查階層歸屬） | 全域配對：允許任意兩個 Component 之間的邊配對，包含跨元件連接（如螺絲孔對機殼孔）。 |
| **Within Component** | `"Within Component"` | `comp1 == comp2`（兩邊所屬 Component 物件相同才回傳 `True`） | 僅允許同一元件內部的邊配對（如同一零件上的對穿孔配對），嚴禁跨元件誤配對。 |

```python
# 通用函式參數版本（classify_and_group_engine.ironpy）
def check_hierarchical_pairing(edge1, edge2, pairing_strategy):
    try:
        comp1 = edge1.Parent.Parent  # Body.Parent -> Component/Part
        comp2 = edge2.Parent.Parent
        if "Ignore Component" in pairing_strategy:
            return True
        elif "Within Component" in pairing_strategy:
            return comp1 == comp2
        return True  # 未知策略時預設為寬鬆允許（與原引擎行為一致）
    except Exception:
        return True  # 階層資訊無法取得時預設允許，避免因例外中斷整體流程
```

**原始引擎中已移除的策略**：早期版本曾有 `Across Component`（僅允許跨元件、排除同元件內配對）選項，依使用者需求已於原始 ACT 腳本中移除，`classify_and_group_engine.ironpy` 不應重新引入此選項，除非明確有新需求。

---

## 二、階層統計分類 (GetHierarchyTypeForStats)

此函式**僅用於統計回報**，不影響配對是否成立的判定（判定邏輯見上節）：

```python
def get_hierarchy_type_for_stats(edge1, edge2):
    try:
        body1 = edge1.Parent
        body2 = edge2.Parent
        if body1 == body2:
            return "SameBody"      # 同一個 Body 上的兩條邊（如同一零件兩端孔）
        comp1 = body1.Parent
        comp2 = body2.Parent
        if comp1 == comp2:
            return "Internal"      # 不同 Body，但同一 Component 內部
        else:
            return "External"      # 跨 Component 配對
    except Exception:
        return ""
```

統計結果用於工程師複核配對合理性，例如：若 `External`（跨元件）配對數異常偏高，可能代表 `Pairing_Strategy` 設定錯誤或孔徑篩選範圍過寬導致誤配對。

---

## 三、距離分級 (Distance Grouping)

啟用 `enable_distance_grouping` 時，依配對邊間最短距離 (`MeasureHelper.MinDistanceBetweenObjects`，已確認存在於 `spaceclaim_api.json`) 劃分三級並附加命名後綴：

```python
def get_distance_suffix(distance, distance_level1_m, distance_level2_m):
    if distance <= distance_level1_m:
        return "_Near"
    elif distance <= distance_level2_m:
        return "_Medium"
    return "_Far"
```

| 層級 | 判定條件 | 預設建議值（可依產品線調整） |
|---|---|---|
| Near | `distance <= Distance_Level1` | 5 mm |
| Medium | `Distance_Level1 < distance <= Distance_Level2` | 5~20 mm |
| Far | `distance > Distance_Level2` | > 20 mm |

**注意**：此分級僅影響具名群組的命名後綴（如 `Scr_RMgrp_1_Near`），不影響配對本身是否成立；配對成立與否完全由 `Distance_min_check_circle`/`Distance_max_check_circle`（配對搜尋半徑門檻）決定。

---

## 四、配對有效性複合判據（圓孔 vs 任意邊）

原引擎對圓形邊配對與任意邊（NURBS/ProceduralCurve）配對採用不同的複合判據組合，`classify_and_group_engine.ironpy` 完整保留此分工：

**圓形邊配對（兩邊皆為 Circle）**：
1. 最短距離落在 `(Distance_min_check_circle, Distance_max_check_circle)` 區間。
2. 兩邊不共用任何面（`l1.intersection(l2).Count == 0`，避免同一倒角邊誤配）。
3. 軸間距離 (`MeasureHelper.MinDistanceBetweenAxes`) 小於 `Holes_axis_dist_max`。
4. 兩圓軸向方向平行 (`Axis.Direction.IsParallel(...)`)。
5. 若兩邊所屬 Body 皆為實體（`Volume != 0`）且屬於同一 Body，則排除（避免同零件內部誤配）。

**任意邊配對（非 Circle，如 NURBS/ProceduralCurve）**：
1. 最短距離落在門檻區間內（同上）。
2. 兩邊不共用任何面。
3. 法向夾角與中點連線的叉積距離 (`axesdist`) 小於 `Holes_axis_dist_max`。
4. 兩邊法向夾角 (`deg12`) 小於 `Deg_max_circles` 門檻。
5. 同一實體 Body 內部配對排除規則同上。

**Mode 1（任意邊模式）**：僅檢查最短距離門檻與不共面條件，不檢查軸向/法向判據，適用於非孔位類型的通用邊配對場景（如卡勾對應缺口）。
