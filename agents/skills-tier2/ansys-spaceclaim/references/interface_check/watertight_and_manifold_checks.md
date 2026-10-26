# 水密性與拓撲一致性判準 (Watertight & Manifold Checks Reference)

本手冊定義裝配體層級拓撲一致性的客觀判準，與 `ansys-spaceclaim-modeling/references/cad_diagnostics.md`（單體微小面/短邊/滲漏）互補，**不重複定義相同判準**，專注於裝配體內多體共存時才會出現的拓撲問題。

---

## 一、三大裝配體拓撲缺陷判斷力庫

| 缺陷類型 | 幾何特徵與診斷判據 | 工程危害 | 修復策略 |
|---|---|---|---|
| **非 Manifold 邊 (Non-Manifold Edge)** | 一條邊被 3 個或以上的面共用（正常拓撲邊最多被 2 個面共用）。常見於多體共面縫合或 T 形接合處。 | 導致網格生成器無法判定法向、殼單元連接性混亂、求解器矩陣病態。 | 於非 manifold 邊處拆分幾何體，或改用 Shared Topology（多體零件而非縫合實體）表達接合關係。 |
| **自由邊 (Free Edge)** | 僅被 1 個面擁有、未與任何其他面配對的邊。對實體 (Solid) 而言，任何自由邊代表水密性破損；對殼體 (Sheet/Surface) 而言，外輪廓邊屬預期自由邊，須與內部破洞自由邊區分。 | 實體上的自由邊代表體積非封閉，無法正確計算質量/體積，網格可能洩漏。 | 若為實體：以 `StitchFaces`/`StitchBodies` 縫合間隙；若為殼體外輪廓：確認屬預期邊界而非破洞。 |
| **重複面 (Duplicate Face)** | 兩個幾何上完全重合（相同位置、法向相反或相同）的面，常見於布林運算失敗殘留或匯入時的面複製。 | 造成網格節點重合、殼單元厚度疊加錯誤、Named Selection 選取歧義。 | 使用 `FixSimplify`/`DeleteFace`（視複雜度選擇）移除冗餘面後重新縫合。 |

---

## 二、裝配體層級水密性彙總規則

單一 Body 的水密性判準沿用 `cad_diagnostics.md`（體積 $V>0$、無零厚度面）。裝配體層級額外要求：

1. **逐體彙總**：對裝配體中每個 Body（含 Suppressed 狀態）執行上述三項拓撲檢查，記錄 `body_name`、`is_suppressed`、`free_edge_count`、`non_manifold_edge_count`、`duplicate_face_count`。
2. **殼體自由邊豁免**：對 `BodyType == Sheet`（薄殼/中面）的 Body，其外輪廓自由邊視為合法邊界，僅統計「內部孔洞型」自由邊（即不構成外輪廓封閉迴路的自由邊）為異常。此區分需透過邊迴路 (Edge Loop) 拓撲走訪判定；若 API 不確定存在，標記「待 api_search 查證」。
3. **裝配體整體判定**：`watertight_assembly = all(body.non_manifold_edge_count == 0 and body.duplicate_face_count == 0 and (body.free_edge_count == 0 or body.is_sheet))`。
4. **狀態分級**：
   - `PASS_READY_FOR_MECHANICAL`：零缺陷。
   - `WARNING_DEFECTS_FOUND`：存在缺陷但非致命（如少量重複面），可繼續但建議修復。
   - `FAIL_TOPOLOGY_BROKEN`：存在非 manifold 邊或實體自由邊，必須中斷流程修復。

---

## 三、SpaceClaim 原生 API 對應（已於 spaceclaim_api.json 確認存在）

以下 API 已於 `docs/api_inventory/spaceclaim_api.json` 檢索確認存在，可直接使用：

- `Body.Faces`, `Body.Edges`：取得面/邊集合，用於走訪計數。
- `Body.Volume`（Property，於 json 中確認為 `Volume`）：體積正定性判據。
- `StitchFaces.Execute(selection, options)` 與 `StitchOptions`：縫合開放曲面/修復自由邊。
- `MeasureHelper.MinDistanceBetweenObjects(selection)`：量測兩物件最短距離，可用於間隙判定。

以下 API 在既有 `cad_diagnostics.md` 範例中出現，但**尚未在 `spaceclaim_api.json` 中逐一確認**，使用前必須先以 `api_search`/`api_get` 查證，不可假設存在：

- `FixSlivers.Execute(...)` / `FixSliversOptions` — **待 api_search 查證**。
- `FindGaps.Execute(...)` / `FindGapsOptions` — **待 api_search 查證**。
- `RemoveSmallEdges.Execute(...)` / `RemoveSmallEdgesOptions` — **待 api_search 查證**。
- 邊迴路 (Edge Loop) 走訪以區分殼體外輪廓邊與內部孔洞自由邊的確切 API 名稱 — **待 api_search 查證**，暫以 `scripts/check_assembly_interference.ironpy` 中的保守計數（僅統計總自由邊數並由人工複核殼體邊界）替代。

---

## 四、裝配體拓撲診斷標準報告格式

```json
{
  "assembly_name": "ServerChassis_Rev2",
  "total_bodies": 24,
  "bodies_audit": [
    {
      "body_name": "Bracket_01",
      "is_suppressed": false,
      "is_sheet": false,
      "volume_m3": 1.234e-5,
      "free_edge_count": 0,
      "non_manifold_edge_count": 0,
      "duplicate_face_count": 0,
      "watertight": true
    }
  ],
  "watertight_assembly": true,
  "overall_status": "PASS_READY_FOR_MECHANICAL"
}
```

若 `overall_status` 非 `PASS_READY_FOR_MECHANICAL`，流程必須中斷並進入修復循環，嚴禁帶著缺陷繼續干涉偵測或匯出。
