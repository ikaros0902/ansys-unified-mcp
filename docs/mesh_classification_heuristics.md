# ANSYS Mechanical MultiZone 幾何分類候選規則與觀察庫 (Candidate Heuristics)

狀態：**記錄觀察中，暫不啟用 (Shadow Mode / Disabled)**  
更新日期：2026-10-01  
說明：本檔案記錄針對實體幾何自動判定 MultiZone vs Tetra 之 Level 3 與 Level 4 候選規則。依工程手則，目前**維持全幾何預設 MultiZone 策略**，僅在步驟三實際劃分失敗或超時（3 分鐘）時由自愈機制個別降級，待累積更多樣化幾何驗證數據後再評估是否正式上線。

---

## 一、 候選規則定義 (Candidate Rules)

### Level 3: 拓撲複雜度門檻 (Topological Complexity)
* **判定條件**：`Faces > 40` 或 `Edges > 100`。
* **物理與演算法依據**：
  * MultiZone 演算法基於 3D 塊拓撲分解（Blocking）。當非單向拉伸之實體面數大於 40 時，內部過渡圓角與特徵交界極度密集，Blocking 引擎在尋找閉合映射環路時極易引發 Jacobian 畸變、死鎖或超過 3 分鐘逾時。
* **例外豁免 (Exemption)**：
  * **PCBA 平板與單向鰭片散熱座**：即使面數達 60~80 面，因其特徵孔洞均為垂直中面的貫穿拉伸特徵，具備單源多目標掃掠性，予以豁免保持 MultiZone。

### Level 4: 不可掃掠語義與機構特徵過濾 (Un-sweepable Features)
* **判定條件**：零件名稱含特定機構特徵關鍵字。
* **特徵特徵庫**：
  * `T-NUT`：帶凸緣異形螺帽，環形截面突變。
  * `PLUG` / `CONNECTOR`：多軸向金屬端子插槽，具垂直卡榫。
  * `LATCH` / `LEVER`：具備旋轉轉軸與斜向加強肋之卡榫把手。
  * `RAIL` / `HOLDER`：多向鏤空與階梯滑軌。
  * `AMP`：高密度連接器座。
  * `JVHDW1037096`：階梯錐形倒角特殊扣件。
  * `TPIN 2`：階梯沉頭銷釘（較一般銷釘多 1 台階面）。

---

## 二、 實體幾何觀察數據庫 (21 個 Tetra 零件實測詳情)

| 零件名稱 | 父組件 | 面數 (Faces) | 邊數 (Edges) | 命中 Level 3 | 命中 Level 4 | 失敗主因拓撲特徵 |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `SM-RACK-LATCH-3OU-GDZ` (2件) | SM-BASEPAN-GDZ | 260 | 648 | ✅ (嚴重超標) | ✅ (LATCH) | 轉軸孔、斜向肋、掏空凹槽，無映射環路 |
| `JVPLS1088210221` (1件) | 1F-FRONT-END-GDZ | 180 | 477 | ✅ (嚴重超標) | ❌ | 複雜塑膠機構件，多方向分叉結構 |
| `PL-ODP-HOLDER-GDZ` (1件) | 1F-FRONT-END-GDZ | 137 | 369 | ✅ (嚴重超標) | ✅ (HOLDER) | 固定架，三向安裝孔與側向補強肋 |
| `OCPNIC-RAIL-PL-GDZ` (4件) | 1F-FRONT-END-GDZ | 64~66 | 178~188 | ✅ (超標) | ✅ (RAIL) | 滑軌卡扣槽，截面多段階梯變化 |
| `SFF1002-168ST-02-AMP` (1件) | 1F-FRONT-END-GDZ | 72 | 173 | ✅ (超標) | ✅ (AMP) | 高速連接器座，端子排盲槽 |
| `JVMET1096414` (2件) | 1F-FRONT-END-GDZ | 46 | 130 | ✅ (超標) | ❌ | 沖壓金屬支架，翻邊凸台交界處扭曲 |
| `Connector_..._E3_1C_PLUG` (2件)| E1_Midplane | 22 | 57 | ❌ | ✅ (PLUG) | 小型盲端子插頭，多向卡扣與插槽 |
| `T-NUT-STRG-CAGE-BOT-GDZ` (3件) | Rear_wall | 8 | 7 | ❌ | ✅ (T-NUT) | 凸緣台階圓錐交界未切分 (Uncut Slice) |
| `JVHDW1037096-A` (3件) | SM-FRONT-COVER-GDZ| 7 | 6 | ❌ | ✅ (JVHDW...) | 階梯軸扣件，沉頭倒角環形突變 |
| `T-NUT-STRG-LEVER-HOLDER-GDZ` (1件)| Component1 | 6 | 5 | ❌ | ✅ (T-NUT) | 異形螺帽座，厚薄突變交界面 |
| `tpin 2` (1件) | Component1 | 6 | 5 | ❌ | ✅ (TPIN 2) | 較標準 5 面銷釘多 1 台階倒角 |

---

## 三、 目前專案運作準則 (Current Protocol)

1. **配置原則**：
   - 薄板件：一律套用 `MultiZone Quad/Tri`。
   - 實體件：一律優先指派 `MultiZone`。
2. **排障處置 (步驟三執行時)**：
   - 採取完全動態自愈：僅在特定幾何 MultiZone 劃分確認失敗或運算超過 180 秒時，單件切換為 `AllTriAllTet`。
   - 不主動預先依 Level 3/4 進行 Tetra 指派，維持最高六面體網格覆蓋意圖。
