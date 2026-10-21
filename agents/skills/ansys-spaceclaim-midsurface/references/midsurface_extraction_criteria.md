# 中面抽取判定準則與面積守恆門禁 (Midsurface Extraction Criteria)

本手冊定義候選薄板偵測、前置干擾特徵過濾、對向面配對、簡單/複雜模式切換、以及抽取後「面積守恆驗證率（觸發剛體平移 $t/2$ 降級工法）」的量化判定公式。

---

## 一、輸入參數定義

| 參數 | 單位 | ACT wizard 預設 | ACT batch 預設 | 說明 |
| :--- | :--- | :--- | :--- | :--- |
| `max_thickness` | m（API 內部）/ mm（UI） | 3.0 mm | 6.0 mm | 兩面配對允許的最大厚度，超過視為非薄板 |
| `main_surface_ratio` | 比例 (0~1) | 0.40 | 0.70 | 主面（含相切鏈）佔全身面積比例下限 |
| `area_difference_ratio` | 比例 (0~1) | 0.60 | 0.10 | 兩配對面面積差異上限（相對較大面） |
| `complex_area_diff` | 比例 (0~1) | 0.05 | 0.05 | 面積差超過此門檻即判定為複雜鈑金件，切換複雜抽取模式 |
| `min_area_conservation` | 比例 (0~1) | 0.42 | 0.42 | 中面總面積相對於原始實體表面積之守恆下限（理論值約 0.46~0.50），低於此值代表嚴重漏抽，觸發 `Move t/2` 降級工法 |
| `enable_pre_fill` | bool | true | true | 抽取前是否自動 `Fill` 消除沉頭孔錐面與微小無孔凸點/浮雕 |
| `enable_sheet_metal_check` | bool | true | true | 是否執行鈑金體三項判定 |
| `hide_source_bodies` | bool | true | true | 抽取成功後是否隱藏來源實體 |

---

## 二、前置干擾特徵篩選準則 (`Pre-Fill` Criteria)

在執行主對向面配對前，若鈑金上存在以下干擾特徵，會拉低 `main_surface_ratio` 或破壞 `GetTangentChain`：
1. **沉頭孔圓錐面 (`Cone` Surface)**：與圓柱孔同軸且面積 $< 50\text{ mm}^2$ 之錐面，抽取前以 `Fill.Execute` 抹除，使直孔貫穿頂底面。
2. **微小非貫穿凸點/字號浮雕 (Dimple / Text)**：單面面積 $< 2.0\text{ mm}^2$ 且不包含貫穿內孔之微面簇，抽取前 `Fill` 抹平。
3. **高聳壓鉚螺柱 (`Standoff`，$H > 2.5t$)**：沿基板表面執行 `SplitBody` 切離為獨立 3D Solid，不納入鈑金中面抽取。

---

## 三、候選對向面配對演算法 (`find_primary_face_pair`)

1. 取得 Body 全部面（`body.Faces`），依面積（`face.Shape.Area`，失敗時 fallback `face.Area`）由大到小排序。
2. 以面積最大的面為基準面 `first`，依序掃描其餘面作為候選 `second`：
   - **法向篩選**：呼叫 `DesignFaceExtensions.GetFaceNormal(face, 0.5, 0.5)` 取兩面中心法向，`|n1·n2| > 0.99` 才接受。
   - **面積相似度篩選**：`abs(a1-a2)/max(a1,a2) <= area_difference_ratio`。
   - **厚度篩選**：以 `MeasureHelper.DistanceBetweenObjects(FaceSelection.Create(f1), FaceSelection.Create(f2)).Distance` 量測間距，須滿足 `0 < distance <= max_thickness`。
3. 第一個通過全部三項篩選的候選即為配對結果 `(f1, f2, thickness)`；若無候選通過，回傳 `None`。

---

## 四、鈑金體三項判定 (`is_sheet_metal_body`)

對配對出的 `(f1, f2, thickness)`：
1. 透過 `DesignFaceExtensions.GetTangentChain(face)` 取得兩面各自的相切面鏈，去重後合併為 `primary_faces`。
2. 計算：
   - `rad = abs(area(chain1) - area(chain2)) / max(area(chain1), area(chain2))`
   - `psr = area(primary_faces) / area(全身所有面)`
3. 三項同時成立才判定為合格鈑金體：
   - `thickness <= max_thickness`
   - `rad <= area_difference_ratio`
   - `psr >= main_surface_ratio`

---

## 五、簡單模式 vs 複雜模式 vs 剛體平移 $t/2$ 降級切換

1. **模式 A：簡單模式** (`area_diff <= complex_area_diff`)：
   ```python
   cmd.AddMatchingFacePairs(f1, f2, 1.0e-5, True)   # allowMissingFaces=True，交由系統自動尋找相切面
   ```
2. **模式 B：複雜相切鏈模式** (`area_diff > complex_area_diff`，含壓折邊/加強筋)：
   ```python
   cmd.AddMatchingFacePairs(f1, f2, 1.0e-5, False)  # 關閉自動尋找
   for fs in get_tangent_chain(f1):
       cmd.AddMatchingFacePairs(None, fs)
   for fs in get_tangent_chain(f2):
       cmd.AddMatchingFacePairs(None, fs)
   ```
3. **模式 C：面積守恆門禁與「主面複製 + 剛體平移 `Move` $t/2$」降級工法**：
   - 抽取後計算生成之中面總面積 $A_{\text{mid}}$ 與原實體總表面積 $A_{\text{solid}}$ 之比值：
     $$\eta_{\text{area}} = \frac{A_{\text{mid}}}{A_{\text{solid}}}$$
   - 對於正常薄板，$A_{\text{solid}} \approx 2 A_{\text{mid}} + A_{\text{side\_edges}}$，故理論比值 $\eta_{\text{area}} \in [0.45, 0.50]$。
   - 若原生 `Midsurface.Execute()` 拋出例外，或 **$\eta_{\text{area}} < 0.42$（代表超過 15% 的折彎牆或加強筋被漏抽開天窗）**，系統自動回退並啟動**「複製單側主壁面鏈 + 沿各自平面法向剛體 `Move` 平移 $t/2$ + `SharePrep` 容差延伸縫合」**，確保中面 100% 完整不缺片。
