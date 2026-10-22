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


---

## 六、全平面法向點積投票與微特徵半徑分流準則 (Multi-Plane Voting & Branching)

### 1. 全平面厚度投票法（取代單一面猜測）
在伺服器上蓋等具備沖壓壓薄（如 0.125mm 斷差）之複雜零件中，單純依賴面積最大面會造成局部階梯誤判。
演算法應收集所有面積 $> 1.0	ext{ mm}^2$ 之平面，針對所有反向平行對（$n_1 \cdot n_2 \le -0.999$）量測投影距離：
$$	ext{dist} = \left| (o_2 - o_1) \cdot n_1 ight|$$
對標準厚度集合（$t \in [0.3, 3.0]	ext{ mm}$，步長 $0.1	ext{ mm}$，容差 $\pm 0.02	ext{ mm}$）以 $\min(	ext{Area}_1, 	ext{Area}_2)$ 權重累加投票，以得票最高者作為全件唯一基準板厚 $t_{	ext{best}}$。

### 2. 法向計算強制底線
- **禁止使用 `geom.Frame.DirZ`**：在有孔鈑金中高達 89% 反向。
- **禁止使用 `normal.Dot()`**：`SpaceClaim.Api.Direction` 無此方法。
- **強制分量展開**：
  $$ec{n}_1 \cdot ec{n}_2 = n_{1x} n_{2x} + n_{1y} n_{2y} + n_{1z} n_{2z} \le -0.999$$

### 3. 微特徵半徑分流準則（Track 1 vs Track 2）
若主相切鏈面集包含微小圓角或孔環圓柱面：
$$r_{\min} = \min_{f \in 	ext{ug1, Cylinder}} \left( 	ext{Radius}(f) ight)$$
- **Case A: $r_{\min} \ge 0.9 \cdot (t / 2)$**：
  幾何曲率大於厚化半徑，**啟用 Track 1（單側連續厚化偏移 Single-Skin Offset）**。1 步提取活動面，完整保留沖壓斷差且絕不破片。
- **Case B: $r_{\min} < 0.9 \cdot (t / 2)$**：
  厚化會引發向內自相交中斷，**啟用 Track 2（原生 Midsurface + 碎屑自愈濾除 Native Debris-Filtered）**。保留主體 Body 0，自動清除面積 $< 20	ext{ mm}^2$ 之微小導柱/孔環附帶碎屑。
