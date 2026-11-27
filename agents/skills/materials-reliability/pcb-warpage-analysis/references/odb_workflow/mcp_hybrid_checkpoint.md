# Track 2 GUI-to-MCP 混合檢查點與交接協議

本文件定義 `pcb-warpage-analysis` Track 2 於 **MCP 模式** 與 **純本機模式** 的交接、防呆、長任務管控及 `PROJECT_DIR/project_log.md` 稽核證據規範。

---

## 1. 三段式 MCP 模式偵測與降級

執行任何建模或 Mechanical 操作前，依序完成以下三段檢查並記錄於 `PROJECT_DIR/project_log.md`：
1. 確認當前會話工具清單包含 `ans_session_status` 與 `mechanical_*` 工具。
2. 呼叫 `ans_session_status(product="mechanical")` 確認服務可用。
3. 透過 `mechanical_list_instances` / `mechanical_connect` 附著目標實例，並與工程師確認專案路徑或實例身分。

**降級規則**：僅當三段皆成功時進入 **MCP 模式**；任一步失敗即切換為 **純本機模式**，改由工程師於本機 GUI 操作並貼回輸出。

---

## 2. GUI-to-MCP 交接與防呆協議（步驟 5 完成後）

Track 2 步驟 4–5（Workbench 匯入材料庫與 `.scdocx`、External Data 載入 `.tgz`、劃分網格與 Import Trace Mapping）維持 **工程師 GUI 人機檢查點**。步驟 5 完成後依下列協議交接：

1. **實例身分確認與唯讀前置檢查**：
   - 工程師提供 Mechanical gRPC 埠號或確認實例後，Agent 呼叫 `mechanical_connect` 附著。
   - 使用 `mechanical_get_tree_hierarchy` 與唯讀腳本核對：
     - (a) 專案名稱／模型路徑與工程師確認完全一致；
     - (b) 樹狀結構存在 `Imported Trace` 物件；
     - (c) Body 數量等於步驟 2 報告層數，且名稱符合 `Layer_<n>_<FR4>_<ratio>` 規則。
   - **任一項不符立即停止，禁止寫入材料或屬性。**
2. **寫入前存檔 Checkpoint 與腳本傳遞規則**：
   - 執行步驟 6 前，工程師**必須先儲存專案快照（checkpoint）**。
   - Agent 讀取已產出之實例檔 `runs/track2_odb/<run>/mechanical/Mech_py_EquivalentMaterial_v6.py` **全文字串**，透過 `mechanical_run_script(script=..., timeout_seconds=600)` 傳入執行。
   - **嚴禁呼叫 `mechanical_run_batch_script`**：該工具會啟動獨立空白批次進程，無法操作已開啟且完成 Trace Mapping 的 GUI 實例。
   - **失敗禁止原地重跑**：若腳本執行失敗或部分套用，嚴禁於同一狀態直接重試，必須先還原執行前存檔快照再重跑。
3. **中途斷線降級**：
   - 若 `mechanical_connect` 失敗或 `mechanical_run_script` 中途斷線，立即切換為 **純本機模式**，請工程師於 Mechanical GUI 直接執行同一份 `Mech_py_EquivalentMaterial_v6.py`，並貼回完整 Console 輸出由 Agent 核對。

---

## 3. `T_REF` 三處一致性與稽核證據欄位表

求解前必須確認三處 `T_REF` 數值完全一致（預設 30 °C），任一不符即停止；`PROJECT_DIR/project_log.md` 須逐項標明資料來源為 `Agent 讀取` 或 `工程師回報`：

| 稽核欄位 | 必填內容 / 檢核標準 | MCP 模式來源 | 純本機模式來源 |
| :--- | :--- | :--- | :--- |
| `TRACK` | `Track 1` 或 `Track 2` | `Agent 讀取` / 記錄 | `Agent 讀取` / 記錄 |
| `RESULT SOURCE` | `FEM-TraceMapping` / `FEM-ROM` / `ESTIMATED` | `Agent 讀取` / 記錄 | `Agent 讀取` / 記錄 |
| `T_REF`（`v6` 腳本頂部） | 讀取 `runs/track2_odb/<run>/mechanical/Mech_py_EquivalentMaterial_v6.py` 頂部設定值 | `Agent 讀取` | `Agent 讀取` |
| `T_REF`（Mechanical 環境/參考溫度） | Environment Temperature 與 Reference Temperature 數值 | `Agent 讀取`（唯讀 `mechanical_run_script`） | `工程師回報` |
| `T_REF`（Thermal Condition 首值） | Thermal Condition 負載表格起始溫度 | `Agent 讀取`（唯讀 `mechanical_run_script`） | `工程師回報` |
| Body 數量與命名 | 等於步驟 2 報告層數且符合 `Layer_<n>_<FR4>_<ratio>` | `Agent 讀取`（`mechanical_get_tree_hierarchy`） | `工程師回報` |
| Imported Trace 存在與否 | 是否存在且對應正確 `.tgz` | `Agent 讀取`（`mechanical_get_tree_hierarchy`） | `工程師回報` |
| `RESULT` 行 | `v6` 腳本與 Leveling CLI 之結構化結果輸出行 | `Agent 讀取`（工具回傳 stdout） | `工程師回報`（貼回完整輸出） |
| 時間戳 | 檢查點與求解完成時間（ISO-8601） | `Agent 讀取` / 記錄 | `Agent 讀取` / 記錄 |

---

## 4. 長耗時任務、逾時清理與中斷恢復

啟動前須先告知工程師預估耗時與所需 ANSYS 授權：

- **Timeout 上限**：
  - `run_odb_tool.py`：上限 **3600 秒**（預估 10–40 分鐘）。
  - `LayerBuilder_pyansys.py`：上限 **900 秒**（需 SpaceClaim / Discovery 授權）。
- **非同步零輪詢**：上述長任務一律以背景任務啟動，Agent 立即結束回合等待喚醒，嚴禁輪詢狀態。
- **逾時或掛死清理**：若超過 timeout 上限或程序無回應，使用 `manage_task`（`Action="kill"`）終止任務，並通知工程師檢查殘留 ANSYS 行程與授權釋放。
- **中斷恢復與 Exit Code**：
  - 授權或環境中斷後，透過 `run_odb_tool.py --reverify <run folder>` 恢復驗證。
  - Exit Code 規範：`0` 通過；`1` 檢查失敗停止；`2` 存在未決人工問題（讀取 `open_questions_*.md` 詢問工程師並寫入專案 JSON 後以 `--non-interactive` 重跑）；`3` 輸入錯誤。
