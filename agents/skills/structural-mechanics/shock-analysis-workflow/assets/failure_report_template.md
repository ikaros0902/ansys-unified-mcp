<!--
  Session 08 失效判定報告骨架
  用途：供後處理評估腳本輸出 PASS / MARGINAL / FAIL 三級判定報告，欄位對齊 SKILL.md 第 2 節
       「標準失效指標評估矩陣」與第 3 節「三級評估狀態機」之命名，確保報表欄位與判定邏輯一致。
  佔位符命名慣例：{{UPPER_SNAKE_CASE}}，缺值一律保留 N/A，不得刪除整列。
-->

# 衝擊分析失效判定報告 (Shock Analysis Failure Evaluation Report)

| 項目 | 內容 |
|---|---|
| 分析案名 (Case Name) | {{CASE_NAME}} |
| 衝擊脈波條件 (Shock Pulse Condition) | {{SHOCK_PULSE_CONDITION}} <!-- 如 35G / 11ms Half-Sine --> |
| 求解器 (Solver) | LS-DYNA |
| 報告產出日期 (Report Date) | {{REPORT_DATE}} |
| 整體判定 (Overall Verdict) | {{OVERALL_VERDICT}} <!-- PASS / MARGINAL / FAIL --> |

---

## 1. 零件層級失效判定表 (Component-Level Failure Matrix)

欄位對齊 SKILL.md 第 2 節「標準失效指標評估矩陣」：零件類別、材料、單元形態、EPS 門檻、安全裕度、判定狀態。

| 零件名稱 (Part) | 零件類別 (Component Category) | 材料 (Material) | 單元形態 (Element Type) | 最大塑性應變 (Max EPS) | EPS 門檻 (Failure Index Threshold) | 安全裕度 (Safety Margin) | 截面貫穿 (Cross-Section Penetrated) | 判定狀態 (Status) |
|---|---|---|---|---|---|---|---|---|
| {{PART_NAME_1}} | {{PART_CATEGORY_1}} <!-- 金屬薄板 / 金屬實體 / 塑料零件 / BGA 焊點 --> | {{MATERIAL_1}} <!-- SGCC / SPCC / SUS301 / 6061-T6 / PC+ABS / SAC305 --> | {{ELEMENT_TYPE_1}} <!-- Shell / Solid --> | {{MAX_EPS_1}} | {{EPS_THRESHOLD_1}} <!-- 0.0100 (一般金屬/塑料) / 0.0022 (BGA 焊點) --> | {{SAFETY_MARGIN_1}} | {{PENETRATION_FLAG_1}} <!-- Yes / No --> | {{STATUS_1}} <!-- PASS / MARGINAL / FAIL --> |
| {{PART_NAME_2}} | {{PART_CATEGORY_2}} | {{MATERIAL_2}} | {{ELEMENT_TYPE_2}} | {{MAX_EPS_2}} | {{EPS_THRESHOLD_2}} | {{SAFETY_MARGIN_2}} | {{PENETRATION_FLAG_2}} | {{STATUS_2}} |
<!-- 依實際零件數量重複上述列 -->

---

## 2. 三級評估狀態機判讀依據 (Three-Tier Evaluation Logic Reference)

| 材料分類 | PASS 門檻 | MARGINAL 門檻 | FAIL 門檻 |
|---|---|---|---|
| 金屬 / 塑料 (一般閾值 0.0100) | EPS < 0.0085 | 0.0085 ≤ EPS < 0.0100 | EPS ≥ 0.0100 且截面貫穿 |
| BGA 焊點 SAC305 (閾值 0.0022) | EPS < 0.00187 | 0.00187 ≤ EPS < 0.00220 | EPS ≥ 0.00220 |

---

## 3. 應變雲圖與視角 (Strain Contour Views)

| 視角 (View) | 零件範圍 (Scope) | 圖檔路徑 (Image Path) |
|---|---|---|
| {{VIEW_NAME_1}} | {{VIEW_SCOPE_1}} | {{IMAGE_PATH_1}} |
| {{VIEW_NAME_2}} | {{VIEW_SCOPE_2}} | {{IMAGE_PATH_2}} |

---

## 4. MARGINAL / FAIL 零件覆核建議 (Review & Mitigation Notes)

| 零件名稱 | 判定狀態 | 建議對策 (Mitigation) | 負責覆核人員 (Reviewer) |
|---|---|---|---|
| {{REVIEW_PART_1}} | {{REVIEW_STATUS_1}} | {{REVIEW_ACTION_1}} <!-- 如：補強肋板 / 調整孔位倒角 / 人工覆核截面貫穿情形 --> | {{REVIEWER_1}} |

---

## 5. 結論與交付狀態 (Conclusion & Delivery Status)

{{CONCLUSION_TEXT}}
<!-- 工具端填入綜合結論，例如：全機 12 個監測零件中 10 個 PASS、1 個 MARGINAL（卡扣根部）、0 個 FAIL，整體判定 PASS，MARGINAL 零件已轉人工覆核。 -->

| 交付檔案 (Deliverable) | 路徑 (Path) |
|---|---|
| Excel 摘要表 | {{XLSX_REPORT_PATH}} |
| PPTX 簡報 | {{PPTX_REPORT_PATH}} |
