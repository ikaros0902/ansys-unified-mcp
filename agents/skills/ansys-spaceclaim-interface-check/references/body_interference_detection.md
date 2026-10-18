# 體間干涉兩階段偵測策略 (Body Interference Detection Reference)

本手冊定義裝配體體間干涉（Body-to-Body Interference）的兩階段偵測策略：**粗篩 (Broad Phase) + 精篩 (Narrow Phase)**，目標是在 SpaceClaim 幾何階段先行抓出干涉，避免進入 Mechanical 網格劃分後才透過 `BodyInterferenceMesh` 診斷發現（成本更高）。

設計思路改寫自 `D:\Ikaros\ACT_Test\ACT_to_PYAnsys\mech_interference_check.py` 的 KD-Tree 殼體干涉補充邏輯，但本技能運作於**幾何階段**（Body 層級、無網格），因此改用 Bounding Box 粗篩 + Boolean 體積精篩，而非網格元素層級的 KD-Tree 鄰近搜尋（KD-Tree 適用於已有網格節點座標的場景，幾何階段尚無網格節點可供建樹）。

---

## 一、第一階段：Bounding Box 粗篩 (Broad Phase)

**目的**：以 $O(n^2)$ 但極輕量的 AABB (Axis-Aligned Bounding Box) 比對，快速排除不可能相交的 Body 配對，將需要精篩的配對數降到最低。

**判據**：兩個 Body 的 Bounding Box 在 X/Y/Z 三軸上的區間皆有重疊，才視為「可能干涉」進入精篩：

```
overlap_x = not (bodyA.max_x < bodyB.min_x or bodyB.max_x < bodyA.min_x)
overlap_y = not (bodyA.max_y < bodyB.min_y or bodyB.max_y < bodyA.min_y)
overlap_z = not (bodyA.max_z < bodyB.min_z or bodyB.max_z < bodyA.min_z)
possible_interference = overlap_x and overlap_y and overlap_z
```

**SpaceClaim 對應 API**（已於 `spaceclaim_api.json` 確認存在）：
- `Body.GetBoundingBox(matrix)` — 傳入 `Matrix.Identity` 取世界座標系下的 AABB，回傳物件含 `MinCorner`/`MaxCorner` 兩個角點座標。
- 若 Body 數量 $n$ 較大（如 $n > 100$），建議先依 Bounding Box 中心座標排序後做掃描線 (Sweep and Prune) 優化，避免全量 $O(n^2)$；此為效能優化選項，非必要功能。

**粗篩效能基準**：對於 $n$ 個 Body 的裝配體，粗篩應在數秒內完成（純數值比對，無幾何運算），精篩配對數應顯著小於 $\binom{n}{2}$（總配對數）。

---

## 二、第二階段：Boolean 體積精篩 (Narrow Phase)

**目的**：對粗篩判定「可能干涉」的配對，執行真實的幾何布林求交運算，確認是否存在非零交集體積。

**判據**：
```
intersection_result = Combine.Intersect(Selection(bodyA_copy), Selection(bodyB_copy), MakeSolidsOptions(), None)
intersection_volume = sum(b.Volume for b in <result bodies>)
is_real_interference = intersection_volume > volume_tolerance_m3
```

**容差設定建議**：
- 預設容差 $10^{-9}\,\text{m}^3$（即 $1\,\text{mm}^3$ 的千分之一），避免將裝配公差造成的微量重合（如螺紋嵌合、壓合面）誤判為干涉。
- 若零件特徵尺度較小（如 BGA 錫球、微米級接觸），容差應依最小特徵體積的 $1\%$ 動態調整，而非固定使用預設值。
- 容差必須在報告中明確記錄所使用數值，供後續複核。

**關鍵限制：運算必須在複製體上執行**：
SpaceClaim 的布林運算 `Combine.Intersect`（確認存在於 `spaceclaim_api.json`，簽名為 `Intersect(target, tool, options: MakeSolidsOptions, info)` 回傳 `CombineResult`）會修改參與運算的幾何。精篩必須先用 `Copy.Execute(selection)`（確認存在，回傳 `CopyResult.CreatedObjects`）複製出臨時 Body 再做求交，運算後立即刪除所有臨時 Body，嚴禁直接對原裝配體運算導致幾何被永久破壞。

**已知 API 缺口（待 api_search 查證）**：
- `CombineResult` 在目前萃取的 `spaceclaim_api.json` 中**沒有任何已記錄的 Property**（`properties: []`），因此「如何從 `CombineResult` 取出求交後產生的實際 Body」目前無法僅憑現有庫確認。`scripts/check_assembly_interference.ironpy` 以防禦性寫法嘗試 `CreatedBodies`/`Bodies`/`CreatedObjects` 等常見命名，若皆不存在則將該配對標記為 `needs_manual_review`，而非silently假設無干涉。
- `Suppressed`/`IsSuppressed` 屬性名稱未在 `spaceclaim_api.json` 中檢出，是否存在、確切命名為何，待 `api_search` 查證後補完；目前腳本不嘗試依抑制狀態過濾 Body（預設全部納入檢查）。

---

## 三、與 Mechanical 內建 BodyInterferenceMesh 診斷的分工

| 偵測階段 | 工具 | 運作層級 | 優點 | 限制 |
|---|---|---|---|---|
| **SpaceClaim 幾何階段（本技能）** | `check_assembly_interference.ironpy` | Body 幾何層級，無需網格 | 在網格劃分前即可發現問題，修復成本低；不受網格尺寸影響判定結果 | 無法偵測網格相關的穿透（如殼單元厚度方向重疊，需網格後才能判定） |
| **Mechanical 網格階段（既有工具）** | `ns.GenerationCriteria[].Criterion = BodyInterferenceMesh`（見 `ansys-mechanical` 技能） | 網格元素層級 | 可偵測殼單元厚度方向的真實網格穿透 | 必須先完成網格劃分才能執行，發現問題時修復成本高（需重新劃網格） |

兩者為互補關係：**先用本技能在幾何階段排除明顯幾何干涉，再在 Mechanical 階段用網格層級診斷做最終確認**，不互相取代。

---

## 四、干涉報告標準格式

```json
{
  "assembly_name": "ServerChassis_Rev2",
  "total_bodies": 24,
  "total_pairs": 276,
  "broad_phase_candidates": 18,
  "narrow_phase_confirmed": 2,
  "volume_tolerance_m3": 1e-9,
  "interferences": [
    {
      "body_a": "Bracket_01",
      "body_b": "Screw_M3x8_02",
      "intersection_volume_m3": 4.5e-8,
      "severity": "FAIL"
    }
  ],
  "overall_status": "FAIL_INTERFERENCE_DETECTED"
}
```

若 `narrow_phase_confirmed > 0`，狀態判定為 `FAIL_INTERFERENCE_DETECTED`，流程必須中斷，不得帶著未解決的干涉繼續後續網格劃分或匯出。
