# 中面抽取降級工法與拓撲修復手法 (Midsurface Fallback & Repair Patterns)

本手冊規範原生中面抽取失敗或漏抽時的「主面複製 + 法向剛體平移 $t/2$」強韌降級工法，以及抽取完成後常見拓撲缺陷（間隙、重疊、法向翻轉、壓薄區厚度映射、雙層點焊板間距保護）的處置標準。

---

## 一、常見缺陷類型與偵測訊號

| 缺陷類型 | 成因 | 偵測訊號與處置 |
| :--- | :--- | :--- |
| **漏抽開天窗 (Missing Flanges)** | 單側加強筋、盲孔或拔模角導致相切鏈配對中斷 | 面積守恆率 $\eta_{\text{area}} = A_{\text{mid}} / A_{\text{solid}} < 0.42$ $\rightarrow$ 啟動 `Copy + Move t/2` 降級工法 |
| **間隙 (Gap)** | 多片中面交界處或去圓角轉角未完全縫合 | 鄰接中面邊緣存在自由邊 (free edge) $\rightarrow$ `SharePrep` (`StitchBodies = True`) 容差縫合 |
| **重疊 (Overlap)** | 180° 反折死邊 (Hem) 或壓折邊相切鏈歧義 | 同一空間存在重疊面片 $\rightarrow$ 前置截斷 Hem 唇邊 + `SharePrepOptions.SeparateOverlaps` |
| **法向不一致 (Normal Flip)** | `AddMatchingFacePairs` 對複雜拓撲選錯主側面 | 相鄰面法向夾角接近 180° $\rightarrow$ 抽取前以 `FlipFacePair` 統一外法向 |
| **短邊與尖刺 (Sliver / Spike)** | 折彎止裂槽 (Bend Relief) 或圓角交界產生退化幾何 | 前置 `Fill` 消除止裂槽 + `SharePrepOptions.RemoveShortEdges / RemoveSlivers` |
| **雙層點焊板誤縫合** | 兩緊貼零件抽中面後相距 $(t_1+t_2)/2$ 被跨件強拉縫合 | **嚴禁跨 Component/Body 將平行貼合中面 Stitch 在一起**，僅對「同一零件內部」之中面片執行縫合 |

---

## 二、核心工法與修復流程（依執行順序）

### 1. 強韌降級工法：主面複製 + 沿法向剛體平移 $t/2$ (`Copy + Move` $t/2$)
當原生 `Midsurface` 失敗或面積守恆率不足時：
1. **收集單側主壁面集**：以最大基準面 `f1` 及其同側平面壁鏈（忽略折彎過渡圓角 `Fillet`）為目標。
2. **複製並剛體平移**：
   - 對每一主壁面 `face`，讀取其單位外法向 $\vec{n} = \text{GetFaceNormal}(\text{face}, 0.5, 0.5)$。
   - 沿內法向向量 $\vec{v} = -\vec{n} \cdot (t / 2)$ 執行平移，將面體移至正中央中面位置。
   - **優勢**：面內所有圓孔、滑軌葫蘆孔、方槽均為純剛體平移，**100% 保持原尺寸零變形**。
3. **轉角延伸與容差縫合**：原本被折彎圓角隔開的相鄰主壁面，透過 `SharePrep`（容差設為折彎半徑量級 $1.2 \cdot t$）自動延伸邊界相交並縫合為單一連續折線殼體。

### 2. 容差縫合與清理：`SharePrep`（全面取代脆弱 `Combine`）
```python
# 已於 api_kb.sqlite 查證：
# SharePrep.Execute(targetBodySel, options: SharePrepOptions, info) -> SharePrepResult
opts = SharePrepOptions()
opts.Tolerance = stitch_tolerance_m          # 建議設為 0.1 * thickness ~ 0.5 * thickness
opts.StitchBodies = True                     # 縫合容差內的間隙（取代硬布林 Combine）
opts.SeparateOverlaps = True                 # 分離重疊面
opts.RemoveShortEdges = True                 # 清理退化短邊
opts.RemoveSlivers = True                    # 清理狹長微小面
result = SharePrep.Execute(target_selection, opts, info)
```
> **重要邊界保護**：`SharePrep` 必須**按「單一原始零件（Per-Part / Per-Source-Body）」分組執行**，嚴禁將兩個緊貼的雙層點焊板（Lap Joint）選在一起做大容差 Stitch，確保雙層板維持 $\frac{t_1+t_2}{2}$ 的物理中面間距。

### 3. 局部壓薄區 (Coining) 與密集散熱網 (Louver/Vent) 屬性映射
- **局部壓薄區 (#14)**：維持平整底面平移出的單一連續中面（不產生 $0.2\text{ mm}$ 台階斷差），以壓薄區邊界印記分割子面（`Imprint` / `SplitFace`），並在輸出厚度字典中標記 `{body_name_coined_face: thin_thickness_mm}`。
- **密集散熱網孔 (#5)**：批量 `Fill` 填平密集小孔後，在報告中輸出開孔率 $\phi = \frac{\sum A_{\text{holes}}}{A_{\text{zone}}}$，供下游 Mechanical 賦予折減彈性模數 $E_{\text{eff}} = (1-\phi)^2 E_0$。

### 4. 法向校正與來源實體隱藏
- 於指令執行前透過 `FlipFacePair` 確保同組配對面法向一致向外。
- 抽取與修復通過面積守恆檢驗後，呼叫 `ViewHelper.SetObjectVisibility(BodySelection.Create(body), VisibilityType.Hide, False, False)` 隱藏原始 3D 實體。


### 5. 單側連續集合厚化偏移抽取工法 (Single-Skin Continuous Offset Pattern)
針對具備局部壓薄、階梯斷差（如 0.125mm 沖壓下陷）或多折邊的零件，原生 Midsurface 容易遺漏或產生 47 塊分離碎片。解法為**單側整片複製並一次性厚化**：
```python
# 1. 複製單側完整 skin_a (包含主相切鏈、沖壓面與階梯台階面)
snap0 = set(PartExtensions.GetAllBodies(root))
Copy.Execute(FaceSelection.Create(list(skin_a)))
snap1 = set(PartExtensions.GetAllBodies(root))
copied_surf = list(snap1 - snap0)[0]

# 2. 以最大面法向向內厚化半板厚 (-half_t)
faces = list(copied_surf.Faces)
faces.sort(key=lambda f: f.Shape.Area, reverse=True)
dir_seed = DesignFaceExtensions.GetFaceNormal(faces[0], 0.5, 0.5)

ThickenFaces.Execute(FaceSelection.Create(faces), dir_seed, -half_t_m, ThickenFaceOptions())
snap2 = set(PartExtensions.GetAllBodies(root))

# 3. 捕捉 SpaceClaim 自動留於 Active Selection 中的偏移面
active_sel = Selection.GetActive()
active_faces = [it for it in active_sel.Items if isinstance(it, IDesignFace)]

if active_faces and len(active_faces) >= len(skin_a) * 0.8:
    Copy.Execute(FaceSelection.Create(active_faces))
    snap3 = set(PartExtensions.GetAllBodies(root))
    final_midsurface = list(snap3 - snap2)[0]

# 4. 刪除中間過渡生成的厚化實體
Delete.Execute(BodySelection.Create(list((snap2 - snap0) & snap2)))
```
**效益**：完全避開多面片縫合（`StitchFaces`）與布林相交（`Combine`），一步直接產出單一連續、保留完整階梯特徵的中曲面。

### 6. 原生中面伴生微碎屑面積自動過濾器 (Debris Elimination Pattern)
對於散熱網孔、微小倒角（$r < t/2$）零件調用原生 `Midsurface` 時，常附帶生成數十個面積 $< 5\text{ mm}^2$ 的微小圓環、導柱片碎屑。
```python
new_bodies = list(snap_after - snap_before)
if new_bodies:
    # 依面積排序，Body[0] 為主要完整中面
    new_bodies.sort(key=lambda b: sum(f.Shape.Area for f in b.Faces), reverse=True)
    main_midsurface = new_bodies[0]
    
    # 識別並刪除小於 20 mm² 的微碎屑
    debris = [b for b in new_bodies[1:] if sum(f.Shape.Area * 1e6 for f in b.Faces) < 20.0]
    if debris:
        Delete.Execute(BodySelection.Create(debris))
```
此模式確保輸出幾何樹中僅保留單一乾淨的主體中面，消除下游網格劃分與接觸對設定的巨大干擾。
