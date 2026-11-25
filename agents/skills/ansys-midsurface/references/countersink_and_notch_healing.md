# 沉頭孔正規化與開口槽自癒協議 (Countersink Normalization & Notch Healing)

> 本文記錄 SpaceClaim 特定案例的做法及啟發式門檻；尺寸與角度不代表通用標準。是否簡化沉孔或修補開口須依分析目的決定。OCCT 原型尚未實作這些處理。

## 一、問題背景與歷史痛點

在板金 CAE 建模中，緊固件沉頭孔（Countersunk Holes）由錐面（Cone）與小圓柱孔（Cylinder）構成。
1. **大破孔問題**：若單側表皮偏置時選取了包含大沉孔倒角的一側，抽出的中面會把孔開到沉孔的最大外緣（如 $r = 3.09\text{ mm}$），而非緊固件穿孔的小圓半徑（如 $r = 1.70\text{ mm}$）。
2. **破口問題**：當沉孔靠近板金邊緣時，大圓開口會切斷外輪廓，在中面上留下開放的槽口（Notch）。
3. **誤傷外輪廓圓角**：若單純以 `isinstance Cone` 判斷沉孔，會將外凸邊界圓角（如 $R=10\text{ mm}$）誤判為沉孔大圓，並因兩端非閉合而觸發 `Fill` 修復，導致平滑圓角被拉平成 45 度的 14.14mm 倒角尖角斜線！

---

## 二、精確判定標準（沉孔 vs 倒角/拔模角）

在 `normalize_countersink_holes` 中，必須透過物理幾何門檻進行嚴格過濾：

```python
# 1. 錐面半頂角過濾（過濾拔模角與圓角）
# 標準 90 度沉孔半角為 45 度 (~0.785 rad)，120 度沉孔半角為 60 度 (~1.05 rad)
# 板金沖壓拔模角通常 < 5~10 度 (< 0.17 rad)
half_ang = getattr(c_geom, "HalfAngle", None)
is_csink_angle = (0.50 <= abs(half_ang) <= 1.35) if half_ang is not None else ((r_max - r_min) >= 0.0004)

# 2. 尺寸與階差過濾
# 緊固件孔徑範圍：穿孔半徑 r_minor >= 0.8 mm，大圓半徑 r_max <= 6.5 mm，沉孔深度階差 delta_r >= 0.4 mm
is_fastener_hole = (0.0008 <= r_min and r_max <= 0.0065 and (r_max - r_min) >= 0.0004)

if is_csink_angle and is_fastener_hole:
    # 判定為標準緊固件沉頭孔
```

---

## 三、雙軌自癒與收縮架構

### 路徑 A：閉合大圓孔（Closed Circle）-> `OffsetEdges` 向內收縮
對於未切斷外緣的完整圓孔，直接以其階差 $\Delta R = R_{\text{major}} - R_{\text{minor}}$ 調用 SpaceClaim 核心偏置：
```python
res_off = ctx.OffsetEdges.Execute(Selection.Create(edge), matching_cs["delta_r"], None)
```

### 路徑 B：開口槽口弧（Open Notch Arc）-> `Fill` 自癒邊界 + `SplitFace` 重新打孔
若沉孔大圓切斷外緣形成開放槽口，端點間距非零：
1. **邊界自癒**：
   ```python
   res_fill = Fill.Execute(Selection.Create(edge))
   ```
   `Fill` 命令會沿著相鄰邊緣切線將外邊界平滑封閉拉直，消除凹槽。
2. **中心定位重切小圓**：
   以沉孔錐面的軸心投影點 $C_{\text{pt}}$ 為中心，在父平面上生成半徑為 $R_{\text{minor}}$ 的閉合圓曲線（`CurveSegment`），透過 `SplitFace.ByCurves` 切割面，再調用 `Delete` 刪除圓形內部面，精確復原閉合緊固件小圓孔。

---

## 四、拓撲變更防呆（防止 COM 指標失效與無窮迴圈）

在 SpaceClaim 底層，每次呼叫 `OffsetEdges` 或 `Fill` 都會重構 B-Rep 拓撲，導致未處理的 `Edge` 指標失效（拋出 `The object is deleted`）。

### 防禦模式：
1. **動態重新掃描（Dynamic Rescan）**：每次幾何修改成功後，立即退出內層循環，重新獲取 `mid_body.Edges`。
2. **標記處理狀態**：在 `csinks` 字典中記錄 `processed: True`，被處理過或已匹配的錐面不再重複計算。
3. **迭代上限保險閥**：外層迴圈最大迭代次數鎖定為 `len(csinks) + 2`，徹底杜絕無窮迴圈。
