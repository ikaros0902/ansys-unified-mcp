# 中面抽取判定準則 (Midsurface Extraction Criteria)

本手冊定義候選薄板偵測、對向面配對與簡單/複雜模式切換的量化判定公式。原始邏輯來源：`ansys-spaceclaim-modeling/scripts/midsurface_agent.ironpy`（ACT batch 版）與 `D:\Ikaros\ACT_Test\1.Release Verison\SC-Midsurface\SC_midsurface_Agent\SC_midsurface_Agent.py`（ACT wizard 版，二者演算法等價，僅輸入來源不同：前者讀 `argsDict`，後者讀 `step.Properties`）。

---

## 一、輸入參數定義

| 參數 | 單位 | ACT wizard 預設 | ACT batch 預設 | 說明 |
| :--- | :--- | :--- | :--- | :--- |
| `max_thickness` | m（API 內部）/ mm（UI） | 3.0 mm | 6.0 mm | 兩面配對允許的最大厚度，超過視為非薄板 |
| `main_surface_ratio` | 比例 (0~1) | 0.40 | 0.70 | 主面（含相切鏈）佔全身面積比例下限 |
| `area_difference_ratio` | 比例 (0~1) | 0.60 | 0.10 | 兩配對面面積差異上限（相對較大面） |
| `complex_area_diff` | 比例 (0~1) | 0.05 | 0.05 | 面積差超過此門檻即判定為複雜鈑金件，切換複雜抽取模式 |
| `enable_sheet_metal_check` | bool | true | true | 是否執行鈑金體三項判定 |
| `hide_source_bodies` | bool | true | true | 抽取成功後是否隱藏來源實體 |

> 注意：wizard 版與 batch 版的 `main_surface_ratio` / `area_difference_ratio` 預設值不同（0.40/0.60 vs 0.70/0.10）。整合腳本採用較嚴格的 batch 版數值作為預設，並允許外部覆寫。

---

## 二、候選對向面配對演算法 (`find_primary_face_pair`)

1. 取得 Body 全部面（`body.Faces`），依面積（`face.Shape.Area`，失敗時 fallback `face.Area`）由大到小排序。
2. 以面積最大的面為基準面 `first`，依序掃描其餘面作為候選 `second`：
   - **法向篩選**：呼叫 `DesignFaceExtensions.GetFaceNormal(face, 0.5, 0.5)` 取兩面中心法向，`|n1·n2| > 0.99` 才接受（容許同向或反向，鈑金彎折處兩面法向可能同向）。
   - **面積相似度篩選**：`abs(a1-a2)/max(a1,a2) <= area_difference_ratio`。
   - **厚度篩選**：以 `MeasureHelper.DistanceBetweenObjects(FaceSelection.Create(f1), FaceSelection.Create(f2)).Distance` 量測間距，須滿足 `0 < distance <= max_thickness`。
3. 第一個通過全部三項篩選的候選即為配對結果 `(f1, f2, thickness)`；若無候選通過，回傳 `None`（該 Body 標記為 FAIL，不嘗試抽取）。

---

## 三、鈑金體三項判定 (`is_sheet_metal_body`)

對配對出的 `(f1, f2, thickness)`：
1. 透過 `DesignFaceExtensions.GetTangentChain(face)` 取得兩面各自的相切面鏈（處理圓角、壓折邊延伸面），去重後合併為 `primary_faces`。
2. 計算：
   - `rad = abs(area(chain1) - area(chain2)) / max(area(chain1), area(chain2))`
   - `psr = area(primary_faces) / area(全身所有面)`
3. 三項同時成立才判定為合格鈑金體：
   - `thickness <= max_thickness`
   - `rad <= area_difference_ratio`
   - `psr >= main_surface_ratio`
4. `enable_sheet_metal_check = False` 時跳過本判定，直接進入抽取（風險：非薄板件可能被誤抽取，僅供特殊除錯情境使用）。

---

## 四、簡單模式 vs 複雜模式切換

抽取前，依配對面積差異比例判定複雜度：

```text
area_diff = abs(area(f1) - area(f2)) / max(area(f1), area(f2))
is_complex = area_diff > complex_area_diff   # 預設門檻 0.05 (5%)
```

- **簡單模式** (`is_complex == False`)：
  ```python
  cmd.AddMatchingFacePairs(f1, f2, 1.0e-5, True)   # allowMissingFaces=True，交由系統自動尋找相切面
  ```
- **複雜模式** (`is_complex == True`，常見於含壓折邊/加強肋/非均勻厚度的鈑金件)：
  ```python
  cmd.AddMatchingFacePairs(f1, f2, 1.0e-5, False)  # 關閉自動尋找
  for fs in get_tangent_chain(f1):
      cmd.AddMatchingFacePairs(None, fs)
  for fs in get_tangent_chain(f2):
      cmd.AddMatchingFacePairs(None, fs)
  ```
  手動迴圈加入兩側全部相切面，避免系統自動搜尋在壓折邊轉角處漏判導致中面不完整（缺角、破孔）。

`AddMatchingFacePairs` 的簽名已於 `api_kb.sqlite` 查證存在（`CreateMidsurfaceNamedSelection.AddMatchingFacePairs` 多個 overload，含 `(face1, face2, thicknessTolerance, allowMissingFaces)`），對應素材中使用的 `Midsurface.AddMatchingFacePairs` 為同系列指令別名，兩份原始素材皆直接呼叫且實測可用。

---

## 五、`MidsurfaceOptions` 標準配置

兩份原始素材一致採用：

| 屬性 | 值 | 用途 |
| :--- | :--- | :--- |
| `AllowNonManifold` | `False` | 禁止產生非 manifold 中面，避免下游網格劃分失敗 |
| `ExtendSurfaces` | `True` | 中面延伸至原實體邊界，避免邊緣內縮造成接觸遺漏 |
| `CreationLocation` | `CreationLocation.ActiveComponent` | 中面建立於當前作用中元件層級 |
| `Group` | `True` | 自動群組化多個中面輸出 |
| `OffsetType` | `MidSurfaceOffsetType.Middle` | 中面置於兩面正中央（而非偏向任一側） |

---

## 六、輸出判定與統計

抽取完成後統計三類結果（對應原始腳本回傳欄位）：
- `success`：成功建立中面且（可選）已隱藏來源 Body。
- `skipped`：通過厚度配對但未通過鈑金體三項判定（僅在 `enable_sheet_metal_check=True` 時發生）。
- `failed`：找不到有效配對面，或 `Midsurface.Execute()` 回傳 `Success=False`（捕捉為例外）。

批次處理多個 Body 時，單一 Body 失敗不應中斷整體流程（素材採逐一 `try/except` 隔離錯誤）。
