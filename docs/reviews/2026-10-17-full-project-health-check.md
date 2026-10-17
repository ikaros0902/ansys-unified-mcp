# ANSYS Unified MCP 專案全面健檢報告

日期：2026-10-17
執行方式：4 個 explorer 子代理平行調查（架構／根目錄／檔案歸類／效能），主代理核實關鍵發現後彙整

---

## 一、核心架構：單向依賴有 2 處真實違反，1 處誤判

### 已核實成立的問題

**1. `products/` 層直接依賴 `bridges/`（9 處，違反分層）**

```
products/workbench/tools.py:17,25,34   → bridges.workbench_batch / workbench_filequeue / transport
products/mechanical/facade.py:50,148   → bridges.connection_manager
products/mechanical/api.py:167         → bridges.connection_manager
products/fluent/facade.py              → bridges.connection_manager
products/geometry/facade.py            → bridges.connection_manager
products/optislang/facade.py           → bridges.connection_manager
```

依 README 所述分層慣例，`bridges/` 應由 `core/` 層統一協調連線，`products/*/facade.py` 不該直接知道傳輸細節。目前 6 個產品的 facade 都直接 import `connection_manager`，等於每個產品各自管理連線邏輯，日後若要換底層傳輸機制（如把 polling 改成事件驅動），要同時改 6 個檔案。

**2. `workbench_socket.py` 不是死代碼，但命名與定位誤導**

子代理原判定「未被任何模組引用」是錯的——核實後發現 `bridges/transport.py:5,29` 確實呼叫 `workbench_socket.send_request()`。真正的問題是：README 明確寫「先前的 file-queue 與 socket-timer 兩種傳輸已於架構重構中移除」，但 `workbench_socket.py` 檔案與呼叫路徑都還在，文件與程式碼對不上。需要澄清：這是刻意保留的備援路徑，還是文件忘了更新。

### 誤判並已排除的項目

**`drivers/__init__.py` 反向依賴 `products/`** —— 子代理誤讀。該檔案第 27-32 行確實有 `from ansys_unified_mcp.products.*.driver import ...`，但這些 import 包在 `if TYPE_CHECKING:` 區塊內，執行期完全不會跑這段程式碼；實際載入邏輯是下方的 `_LAZY_DRIVERS` 字典用字串映射延遲載入（`importlib`），這是正確的延遲載入設計模式，不構成執行期反向依賴。純粹是給 IDE/mypy 做型別提示用。**不需修復。**

### 待確認（子代理報告但未核實，優先度較低）

- `connection/session_manager.py` 是否為應廢棄的舊模組，仍被 `tools/session_manager_tools.py:27` 引用——需確認 `core/sessions.SessionRegistry` 是否已完全取代其功能。
- Mechanical 系列 MCP 工具函式命名缺 `mechanical_` 前綴（與 Fluent/Geometry/Workbench 的命名慣例不一致）。

---

## 二、根目錄雜亂度：中度混亂，多數為零風險清理項

**可立即刪除（無依賴風險）**
- `_rev_out.txt`（4.4KB）、`_rev_out2.txt`（4.3KB）——10/16 產生的暫存輸出檔，與專案功能無關。
- `.agents/skills`、`.cline/skills`——內容為空（0 byte），確認為殭屍設定目錄，`.kiro/` 是唯一實際運作的 agent 設定來源。

**建議歸檔（非零風險，需確認後移動）**
- `spec.md`（110KB，610 個版控檔案的完整掃描報告）——建議移至 `docs/archive/`，減輕根目錄認知負荷。
- `.codex/` 僅含 48 bytes 的 `config.toml`，活躍度低，確認是否仍需要。

**日誌堆積（非阻斷，建議排程清理）**
- `logs/script_audit/` 下 500+ 份日誌檔案，橫跨 2026-08-13 至 2026-10-17，約 600~700KB。無自動輪轉機制。

**確認健康的部分**
- `.gitignore` 對 `.venv/`、`__pycache__/`、`.ruff_cache/`、`.pytest_cache/`、`.codegraph/`、`.serena/` 的排除規則正確且完整。
- 根目錄進入點設計合理：`mcp_server.py` 委派至 `src/ansys_unified_mcp/__main__.py`，兩者職責分離清楚，非重複定義。
- `README.md`、`AGENTS.md`、`spec.md` 三份文件職責不重疊（使用者導覽 / 協作規範 / 技術掃描）。

---

## 三、檔案歸類錯誤：5 處硬編碼路徑是最高優先級問題

**1. `F:\Ming_python\` 絕對路徑硬編碼（5 檔案，高風險）**

```
scripts/extract_all_apis.py:61
scripts/extract_lsdyna_api.py:214
scripts/extract_mechanical_api.py:175
scripts/extract_optislang_api.py:129
scripts/extract_spaceclaim_api.py:136
```

這 5 份 API 抽取腳本的輸出路徑寫死在別人電腦的本機路徑上，換一台電腦執行就會失敗或寫到錯誤位置。這違反 `.kiro/steering/11-skill-evolution.md` 明確禁止事項（「嚴禁沉澱特定電腦的絕對路徑」）。應改為相對於專案根目錄或用環境變數配置。

**2. 已知重複腳本仍未解決（`LESSONS_LEARNED.md` 記錄的技術債延續）**

- `lsdyna_drop_test_setup.py`（ansys-lsdyna）vs `lsdyna_drop_setup.py`（shock-analysis-workflow）
- `lsdyna_shock_analysis_setup.py`（ansys-lsdyna）vs `lsdyna_shock_setup.py`（shock-analysis-workflow）
- `check_mesh_quality.py` 在 `ansys-mesh` 與 `ansys-mechanical` 各有一份，**內容不同**（前者英文註解 PyAnsys 風格，後者繁中註解 ACT 風格）——不是單純重複，是兩個不同實作者各寫一份做同一件事，需要人工比對決定去留，不可直接刪一份。

**3. `ansys-geometry-modeling` 與 `ansys-spaceclaim-modeling` 的 references 檔名完全重疊**（7 個同名檔：`3d_features.md`、`booleans_enclosures.md`、`cad_diagnostics.md`、`named_selections.md`、`pmdb_export_rules.md`、`sketching.md` 等）。兩者分別對應 PyAnsys Geometry 與原生 SpaceClaim API，內容可能不同但命名雷同容易混淆，建議檔名加上後綴區分（如 `sketching_pyansys.md` vs `sketching_scdm.md`）。

**4. `Documentation_clean/` 定位不明**——目前只放一個 22.5MB 的 `api_kb.sqlite`，沒有說明文件，根目錄多一層不透明的黑盒目錄。應併入 `docs/` 體系或加上 README 說明用途。

**5. 新發現的 `agents/skills-workspace/`**——這是上一輪 WP6 評估任務建立的暫存工作區，已正確加入 `.git/info/exclude`，不會誤入版控，屬正常技術債非錯誤歸類，標記供知悉即可。

---

## 四、效能瓶頸：整體健康，兩項可優化項非急迫

**確認無風險的部分**
- `connection_manager.py` 無內建輪詢迴圈，純功能型掃描，呼叫端決定頻率。
- `products/geometry/call_dispatch.py` 實測 2523 行（非上次誤判的 139KB／疑似位元組數），純函式路由無模組層全域狀態建構，import 成本低。
- `analytics/apikb/` 已用 SQLite FTS5 索引查詢，`mechanical_api.json`（23.9MB）確認不會在伺服器啟動時整檔載入記憶體。
- `.codegraph/` 是 IDE 索引工具的產物，非伺服器依賴，無重建開銷。

**可優化但非急迫**
- **6 個 `ansys-*-core` 核心依賴強制 eager import**（`__main__.py:17-24`）：`ansys-mechanical-core`、`ansys-fluent-core`、`ansys-geometry-core`、`ansys-optislang-core`、`ansys-dpf-core` 等在伺服器啟動時一次性載入，即使使用者只需要其中一個產品。`[dyna]` extra 已有延遲載入+try/except 的參考模式，可考慮套用到其他產品依賴。
- **Sentinel 背景監控固定 0.5 秒輪詢**（`core/sentinel/watchdog.py:60-66,206`、`queue.py:405`）：2Hz 輪詢對即時物理監控（求解日誌追蹤）是合理頻率，但待機期間仍會持續喚醒 CPU。可考慮依任務狀態動態調整間隔，或改用 `threading.Event` 事件驅動取代固定 sleep，符合 steering 規範「非必要不採用高頻盲目輪詢」原則。

---

## 五、修復優先序總表

| 優先級 | 項目 | 類別 | 風險 | 工作量 |
|---|---|---|---|---|
| 🔴 P1 | 5 份 extract_*_api.py 硬編碼 `F:\Ming_python\` 路徑 | 檔案歸類 | 高（換機即失敗） | 低 |
| 🔴 P1 | `products/*/facade.py` 直接依賴 `bridges.connection_manager`（6 處） | 架構 | 中（維護成本累積） | 中 |
| 🟡 P2 | `check_mesh_quality.py` 兩份不同實作需人工比對合併 | 檔案歸類 | 中 | 中 |
| 🟡 P2 | `lsdyna_drop/shock_*_setup.py` 命名變體統一 | 檔案歸類 | 中 | 低 |
| 🟡 P2 | `workbench_socket.py` 與 README 敘述不一致，需澄清是否為刻意備援 | 架構 | 低 | 低 |
| 🟢 P3 | `_rev_out*.txt` 刪除、`.agents/`、`.cline/` 殭屍目錄清理 | 根目錄 | 無 | 低（零風險） |
| 🟢 P3 | `spec.md` 歸檔至 `docs/archive/` | 根目錄 | 低 | 低 |
| 🟢 P3 | `ansys-geometry-modeling` / `ansys-spaceclaim-modeling` references 檔名加後綴區分 | 檔案歸類 | 低 | 低 |
| 🟢 P3 | `Documentation_clean/` 補充用途說明或併入 docs/ | 檔案歸類 | 低 | 低 |
| 🔵 P4 | 6 個 `ansys-*-core` 依賴改延遲載入 | 效能 | 低 | 中 |
| 🔵 P4 | Sentinel 0.5 秒輪詢改事件驅動 | 效能 | 低 | 中 |

## 六、總結

專案整體健康度中等偏上，沒有發現會導致功能錯誤或資料遺失的致命問題。最值得優先處理的是 **P1 兩項**：硬編碼路徑是真實的可移植性風險（換電腦就壞），`products/` 對 `bridges/` 的直接依賴是架構層面的技術債累積，兩者都影響不大但修復成本低，建議列入下一輪維護排期。根目錄與檔案歸類的清理項多數零風險，可隨手處理。效能面目前無急迫瓶頸，兩項優化建議可留待有實際效能問題時再處理，不需要為了「理論上更好」而提前重構。
