<!--
  Mechanical 分析報告段落骨架
  用途：供 generate_report 類工具讀取後，以結構化方式填入下列佔位符並輸出完整報告段落。
  佔位符命名慣例：{{UPPER_SNAKE_CASE}}，工具端應逐一替換，未填寫欄位請保留 N/A 而非刪除整行。
  適用分析類型：靜態結構 (Static Structural) / 模態 (Modal) / 熱應力序列耦合 (Thermal-Stress Coupling)。
-->

## {{SECTION_TITLE}}

### 1. 分析概要 (Analysis Overview)

| 項目 | 內容 |
|---|---|
| 分析類型 (Analysis Type) | {{ANALYSIS_TYPE}} <!-- 靜態結構 / 模態分析 / 熱應力序列耦合 --> |
| 模型名稱 (Model Name) | {{MODEL_NAME}} |
| 單位制 (Unit System) | {{UNIT_SYSTEM}} <!-- 如 StandardMKS / StandardNMM --> |
| 求解日期 (Solve Date) | {{SOLVE_DATE}} |
| 求解器版本 (Solver Version) | {{SOLVER_VERSION}} |

### 2. 網格摘要 (Mesh Summary)

| 項目 | 數值 | 判定門檻 | 狀態 |
|---|---|---|---|
| 節點數 (Nodes) | {{NODE_COUNT}} | — | — |
| 單元數 (Elements) | {{ELEMENT_COUNT}} | — | — |
| 平均歪斜度 (Avg. Skewness) | {{AVG_SKEWNESS}} | < 0.85 | {{SKEWNESS_STATUS}} <!-- PASS / FAIL --> |
| 平均正交品質 (Avg. Orthogonal Quality) | {{AVG_ORTHOGONAL_QUALITY}} | > 0.15 | {{ORTHOGONAL_STATUS}} <!-- PASS / FAIL --> |

### 3. 邊界條件與載荷 (Boundary Conditions & Loads)

| 名稱 | 類型 | 施加對象 (Scoping) | 數值 |
|---|---|---|---|
| {{BC_NAME_1}} | {{BC_TYPE_1}} <!-- Fixed Support / Displacement / Force / Pressure --> | {{BC_SCOPE_1}} | {{BC_VALUE_1}} |
| {{BC_NAME_2}} | {{BC_TYPE_2}} | {{BC_SCOPE_2}} | {{BC_VALUE_2}} |
<!-- 依實際邊界條件數量重複上述列 -->

### 4. 結果摘要 (Result Summary)

| 結果項目 | 最大值 | 最小值 | 發生位置 (Scoping) | 單位 |
|---|---|---|---|---|
| 等效應力 (Equivalent von-Mises Stress) | {{MAX_STRESS}} | {{MIN_STRESS}} | {{STRESS_LOCATION}} | {{STRESS_UNIT}} |
| 總變形 (Total Deformation) | {{MAX_DEFORMATION}} | {{MIN_DEFORMATION}} | {{DEFORMATION_LOCATION}} | {{DEFORMATION_UNIT}} |
| 安全係數 (Safety Factor) | {{MIN_SAFETY_FACTOR}} | — | {{SAFETY_FACTOR_LOCATION}} | — |

<!-- 模態分析專用區塊：靜態結構/熱應力分析無此表格時可整段省略 -->
### 4a. 模態結果 (Modal Results)

| 模態階數 (Mode) | 固有頻率 (Natural Frequency) | 振型描述 (Mode Shape) |
|---|---|---|
| 1 | {{MODE_1_FREQ}} Hz | {{MODE_1_SHAPE}} |
| 2 | {{MODE_2_FREQ}} Hz | {{MODE_2_SHAPE}} |
<!-- 依提取階數重複上述列 -->

<!-- 熱應力序列耦合專用區塊：靜態結構/模態分析無此表格時可整段省略 -->
### 4b. 熱-結構耦合結果 (Thermal-Structural Coupling Results)

| 項目 | 數值 | 單位 |
|---|---|---|
| 無應力參考溫度 (Reference Temperature) | {{REFERENCE_TEMPERATURE}} | °C |
| 最高溫度 (Max Temperature) | {{MAX_TEMPERATURE}} | °C |
| 最大熱應變 (Max Thermal Strain) | {{MAX_THERMAL_STRAIN}} | — |

### 5. 收斂狀態 (Convergence Status)

| 檢核項目 | 狀態 | 說明 |
|---|---|---|
| 力殘差收斂 (Force Convergence) | {{FORCE_CONVERGENCE_STATUS}} <!-- Converged / Not Converged --> | {{FORCE_CONVERGENCE_NOTE}} |
| 網格無關性 (Mesh Independence, GCI) | {{GCI_STATUS}} | {{GCI_NOTE}} |
| 奇異點判定 (Singularity Check) | {{SINGULARITY_STATUS}} <!-- 真實應力集中 / 數值奇異點 --> | {{SINGULARITY_NOTE}} |

### 6. 工程判斷與結論 (Engineering Judgment & Conclusion)

{{ENGINEERING_CONCLUSION}}
<!-- 工具端填入綜合判讀文字，例如：結構在最惡劣工況下安全係數大於 1.5，網格無關性驗證通過，判定結構滿足設計要求。 -->
