# ANSYS-unified-MCP 程式碼審視報告

範圍：`refactor/unified-arch` 分支，`src/ansys_unified_mcp/` 全部原始碼（約 24 個 Python 檔）
方法：逐檔讀取（非僅 grep 抽樣）、架構比對 `ARCHITECTURE.md`/`contexts/context.md`、測試實跑範圍檢查、git 狀態核實
說明：本報告基於實際讀取的當前程式碼，非推測；每項缺陷皆附檔案位置與原因。

---

## 總體評估

| 維度 | 狀態 | 說明 |
|---|---|---|
| 架構設計 | 🟢 良好 | 四層（tools/products/drivers-bridges/core）分工清楚，`connection_manager.py`/`config.py`/`core/sessions.py` 品質高：thread-safe、非致命降級、無裸露例外 |
| Session 管理（新架構） | 🟢 良好 | `SessionRegistry` 設計乾淨，`Mechanical`/`optiSLang`/`Workbench` 三個 controller 已統一走它 |
| Session 管理（舊架構殘留） | 🔴 未收斂 | `drivers/sim_impl.py`（Fluent + Geometry/SpaceClaim）仍用模組全域變數 `_fluent_session`/`_modeler`，未走 `SessionRegistry` |
| 回傳信封一致性 | 🟡 不一致 | `mechanical.py`/`optislang.py` 走 `{"ok":..}` 信封；`workbench_bridge.py`（舊 file-IPC bridge）常回純字串或 `Error: ...` |
| 工具層命名 | 🟡 不一致 | Mechanical 工具多數無 `mechanical_` 前綴（如 `list_instances`、`add_force`）；optiSLang 前綴/無前綴混用 |
| 測試覆蓋率 | 🟡 部分覆蓋 | 4 個測試檔（`test_sessions.py`, `test_mechanical_controller.py`, `test_optislang_controller.py`, `test_workbench_controller.py`） |
| 連線層驗證 | 🔴 未驗證 | `products/workbench.py`、`tools/workbench_pyworkbench.py` 明確標註 `UNVERIFIED`，從未連過真實 Workbench server |
| 文件檢索子系統 | 🟢 良好 | 28 份文件、涵蓋 5 產品（mechanical/lsdyna/ls-prepost/optislang/spaceclaim），FTS5 索引正常；僅缺 Fluent |
| Timeout 機制 | 🟡 部分缺失 | `bridges/workbench_bridge.py` 的檔案 IPC 輪詢有 timeout（預設 30s）；但 gRPC 直連路徑（Mechanical/optiSLang controller 的 `run_script`）無 timeout，會無限等待 |
| 依賴聲明 | 🟡 待補 | `pyproject.toml`/`requirements.txt` 缺 `ansys-workbench-core`（`products/workbench.py` 需要它才能 import） |

---

## 已知缺陷清單

### 🔴 Critical

**C1. Fluent/Geometry 仍用模組全域 session，未走 `SessionRegistry`**
- 位置：`drivers/sim_impl.py:37-39`（`_fluent_session = None`、`_modeler = None`）
- 問題：`core/sessions.py` 的 docstring 明確寫著它是為了「取代 `_fluent_session`、`_modeler` 這些散落的模組全域變數」而設計的，但 `sim_impl.py` 本身沒有跟進遷移。這代表：
  - 若同一 MCP server process 需要同時操作 Fluent/Geometry 與 Mechanical/optiSLang，前者無法納入 `SessionRegistry.snapshot()` 這類統一狀態檢視。
  - 多 session（同時開兩個 Fluent）不可能，因為只有一個模組級變數能存活。
  - 這是專案自己 `contexts/context.md` 第 6 節列出的已知技術債，**目前仍未修**。
- 影響：中高（功能限制 + 架構不一致，非當機風險）
- 修法：仿照 `products/mechanical.py` 的模式，寫 `products/fluent.py`、`products/geometry.py` controller，session 存入 `registry`，`sim_impl.py` 改為委派。

**C2. gRPC 直連路徑無 timeout，會無限卡住 (🟢 已修復)**
- 位置：`products/mechanical.py`, `products/optislang.py`, `products/workbench.py`
- 狀態：已實作 `core/timeout.py`，上述檔案均已套用 `run_with_timeout` 解決無限卡住問題。

**C3. `products/workbench.py` 依賴的套件未在 `pyproject.toml`/`requirements.txt` 宣告**
- 位置：`products/workbench.py` 內 `from ansys.workbench.core import launch_workbench`；`pyproject.toml` dependencies 只列了 `ansys-mechanical-core`/`ansys-fluent-core`/`ansys-geometry-core`/`ansys-optislang-core`，沒有 `ansys-workbench-core`
- 問題：`import ImportError` 有被接住（回 `{"ok": false, "error": "ansys-workbench-core not installed."}`），所以不會讓 server 崩潰，但這代表**這個套件目前必然裝不上**，`workbench_launch_server`/`workbench_connect_server` 兩個工具在任何乾淨環境下必定回錯誤。
- 影響：中（功能形同不存在，但已被優雅降級接住，不是當機風險）
- 修法：`pyproject.toml` 加 `ansys-workbench-core`，並在你有連線環境時做一次 `pip install` + import 驗證。

### 🟡 Design Issues

**D1. 回傳信封不一致（新舊架構交界處）**
- 位置：`ARCHITECTURE.md` 第 3 節已誠實記錄此現況偏差；`bridges/workbench_bridge.py` 的 `_format_bridge_result()` 會依情況回純字串（成功輸出文字）或 `"Error: ..."` 字串，而非 `{"ok": ...}` JSON 信封
- 影響：低-中（AI 客戶端要解析 Workbench 系工具的回傳時，無法統一用 `json.loads(result)["ok"]` 判斷成功/失敗，得額外判斷字串前綴）
- 修法：`ARCHITECTURE.md` 已定義收斂方向；純粹是排期問題，非隱藏 bug。

**D2. Mechanical 工具命名普遍缺 `mechanical_` 前綴**
- 位置：`tools/mechanical.py` 內 `list_instances`、`connect_to_mechanical`、`add_force`、`solve_analysis` 等
- 問題：`ARCHITECTURE.md` 表格已列出此偏差。`list_instances` 這個名稱特別容易誤導——它其實是查全域已註冊的 ANSYS 實例（不限 Mechanical），放在 `tools/mechanical.py` 裡卻沒有 product 前綴，AI 客戶端在工具列表裡看到一堆裸動詞（`add_force`、`get_model_info`）很難一眼看出屬於哪個產品。
- 影響：低（可用性問題，非功能缺陷）；但**改名屬對外介面變更**，AI client 快取的工具名會失效，需要成批規劃，不宜隨手改。

**D3. `sim_impl.py` 用兩套工具註冊機制混合**
- 位置：`drivers/sim_impl.py` 用原生 `mcp.types.Tool` + `TextContent` 定義 `ALL_TOOLS` 清單（給 `sim_tools.py` 的 `async def ... res = await sim_impl.call_tool(...)` 轉接），而其他模組（`tools/mechanical.py` 等）直接用 `@mcp.tool()` 裝飾器
- 問題：多一層轉接（`sim_tools.py` 手寫轉發函式 → `sim_impl.call_tool(name, args)` dispatcher → 回傳 `list[TextContent]` → 再 `"\n".join([c.text for c in res])`），增加維護成本且容易在轉接時漏掉參數（例如新增一個 Tool 的 inputSchema 欄位，必須同時改 `sim_impl.py` 的 `ALL_TOOLS` 和 `sim_tools.py` 的轉發函式，兩處手動同步）。
- 影響：低-中（純維護負擔，非執行期缺陷）
- 修法：長期可把 `sim_tools.py` 的轉發函式改成用 `@mcp.tool()` 直接包 `sim_impl` 裡的邏輯函式，砍掉 `Tool`/`TextContent` 這層。非急迫。

**D4. `SessionRegistry.drop()` 的 promotion 邏輯依賴 dict 插入順序**
- 位置：`core/sessions.py` 的 `drop()`：`remaining = next(iter(product_sessions), None)`
- 問題：拿「剩下第一個 key」當新的 current，其實是拿 dict 迭代順序（Python 3.7+ 保證插入順序）裡最舊的存活 session，而不是「最近使用」的。這不是 bug（測試 `test_drop_promotes_then_clears` 已驗證此行為符合預期），但語意上「哪個該變成新的 current」值得留意——目前是「最舊的存活者」，如果之後有人假設是「次新的」會踩坑。
- 影響：極低（目前行為一致且有測試鎖住），僅記錄供未來維護者注意語意。

### 🟢 已解決 / 非問題（compact 前的誤判修正）

先前（context compact 前）記錄的以下項目經重新核實**不成立**，特此更正：
- ~~`core/session_registry.py` 有 `except Exception: pass` 吞掉異常~~ → 實際檔案是 `core/sessions.py`，內容乾淨、無此問題，且全專案掃描後找到的所有 `except ...: pass` 都是**合理的資源清理**場景（如 `os.remove()` 失敗時不中斷主流程、`psutil.NoSuchProcess` 掃描時忽略已消失的進程），不是吞掉關鍵錯誤。
- ~~`connection_manager.py` 缺重複連線檢查~~ → 實際上 `_is_port_open()` 用 0.2s timeout socket 探測，設計合理；「連線但應用已死」的偵測屬於 C2（無 heartbeat/timeout）的子問題，已合併進 C2。
- ~~無 `tests/` 目錄~~ → 實際存在 `tests/`，包含 4 個測試檔（`test_sessions.py`, `test_mechanical_controller.py`, `test_optislang_controller.py`, `test_workbench_controller.py`）。
- ~~`products/mechanical.py` 有 `MechanicalWrapper` 且標 `UNVERIFIED`~~ → 實際類別是 `MechanicalController`，程式碼裡沒有 `UNVERIFIED` 標註（該標註只出現在 `products/workbench.py`），Mechanical 路徑的成熟度高於先前記錄。

---

## 測試覆蓋率缺口（具體化）

| 模組 | 現況 | 缺口 |
|---|---|---|
| `core/sessions.py` | ✅ 4 個測試，覆蓋 put/get/current/drop/snapshot | 無明顯缺口 |
| `products/optislang.py` | ✅ 5 個測試，覆蓋 not-connected/connected/disconnect/exception | 無明顯缺口 |
| `products/mechanical.py` | ❌ 無測試 | `connect()`/`launch()`/`run_script()`/`disconnect()` 皆可用 fake session 注入 `registry` 做冒煙測試（仿 `test_optislang_controller.py` 的 `FakeOsl` 模式），不需真實 Mechanical |
| `products/workbench.py` | ❌ 無測試 | 同上，可用 fake client 測 `launch`/`connect`/`run_script`/`upload_file` 的分支邏輯（尤其 key 解析：`resolved_port` vs `port` vs `"launched"` 三種情況） |
| `connection_manager.py` | ❌ 無測試 | `_is_port_open()`、`get_registered_instances()` 的清理邏輯（過期 PID 檔案自動刪除）可用 tmp_path + mock psutil 測試，不需真實網路 |
| `drivers/sim_impl.py` | ❌ 無測試 | 因未走 `SessionRegistry`，測試需 mock 模組全域變數，此為 C1 修復後應同步補測試的理由之一 |

**建議**：修 C1（Fluent/Geometry 遷移到 `SessionRegistry`）與補 `products/mechanical.py`、`products/workbench.py` 的冒煙測試，可用同一套「fake session 注入 registry」模式，成本低、複用現有測試設計。

---

## 升級優先序清單

排序原則：**影響範圍 × 修復成本**，優先做「低成本、高風險降低」的項目；已明確標註何時該做 vs. 何時可以在恢復連線後再做。

### P0 — 不需連線即可做，做完立刻降低風險

| # | 項目 | 對應缺陷 | 預估工作量 |
|---|---|---|---|
| 1 | 補 `products/mechanical.py`、`products/workbench.py` 的冒煙測試（fake session） | 測試缺口 | 0.5–1 天，複用 `test_optislang_controller.py` 模式 |
| 2 | `pyproject.toml`/`requirements.txt` 補 `ansys-workbench-core` | C3 | 5 分鐘 + 待有網路環境驗證安裝 |
| 3 | gRPC 直連路徑加 timeout 包裝（`ThreadPoolExecutor` + `future.result(timeout=)`） | C2 | 0.5 天，三個 controller（Mechanical/optiSLang/Workbench）的 `run_script` 都要改，邏輯可共用一個 helper |

### P1 — 需要連線驗證才能真正收尾，但程式碼可以先寫好

| # | 項目 | 對應缺陷 | 預估工作量 |
|---|---|---|---|
| 4 | Fluent/Geometry 遷移到 `SessionRegistry`（寫 `products/fluent.py`、`products/geometry.py`） | C1 | 1–2 天寫 + 需連線驗證 gRPC 行為不變 |
| 5 | `products/workbench.py` 連線驗證（`launch`/`connect`/`run_script`），移除 `UNVERIFIED` 標註或修正發現的問題 | C3 延伸 | 需連線環境；程式碼審視已完成，剩實測 |
| 6 | Mechanical/SpaceClaim 連線驗證（gRPC 埠掃描、`connect_to_mechanical`、`geometry_launch`） | 整體驗證 | 需連線環境 |

### P2 — 架構收斂，非緊急但長期會累積技術債

| # | 項目 | 對應缺陷 | 預估工作量 |
|---|---|---|---|
| 7 | 統一回傳信封（`bridges/workbench_bridge.py` 改回 `{"ok":...}`） | D1 | 1 天，需檢查所有呼叫端解析邏輯是否受影響 |
| 8 | `sim_tools.py`/`sim_impl.py` 砍掉雙層轉接，改直接 `@mcp.tool()` | D3 | 1–2 天，機械式改寫但範圍大（29 個 Fluent 工具 + 9 個 Geometry 工具） |
| 9 | Mechanical 工具命名補前綴（`list_instances` → `mechanical_list_instances` 等） | D2 | 需規劃對外相容性（AI client 快取工具名可能失效），建議與 D3 一起做一次性大改 |
| 10 | Fluent 文件加入 `docs/config.py` 索引（目前 5 產品缺 Fluent） | 文件缺口 | 需要 Fluent 官方文件來源，非純程式碼工作 |

### 與你要求的「GitHub 競品比較」結論（先前已完成，此處重申結論不重複過程）
你的 thin-script-runner 設計（不綁死高階 API）是這類專案裡少見的務實選擇，多數同類開源 MCP 專案直接包裝特定版本 API，遇到 ANSYS 版本升級就大改。這是你的架構優勢，不在本次缺陷清單內，但值得在後續文件/README 中明確寫出來當作設計賣點。

---

## 給你的實務建議

1. **先做 P0**：三項都不需要連線 ANSYS，你在 RDP 環境現在就能做，且直接降低「AI 呼叫卡死」這種對使用體驗傷害最大的風險（C2）。
2. **C1（Fluent/Geometry 遷移）程式碼可以先寫、先過 review，但別急著刪 `sim_impl.py` 的舊變數**——等你有機會連上真實 Fluent/SpaceClaim 驗證新路徑行為一致後才切換，避免在沒驗證環境下大改連線邏輯。
3. 之前 compact 前的審視記錄了幾個實際不存在的問題（見「已解決/非問題」節），代表**你的程式碼其實比我一開始評估的更成熟**，尤其 `core/sessions.py`、`config.py`、`connection_manager.py` 三個核心檔案品質相當扎實。真正的缺口集中在「新舊架構交接處」（Fluent/Geometry 沒跟上遷移、Workbench 沒驗證過、gRPC 路徑沒 timeout），而不是隨機分佈的粗糙 bug。

---

## 更新記錄

- **2026-08-14**:
  - 標註 C2 (gRPC Timeout) 為已修復：已實作 `core/timeout.py` 並套用於 `products/mechanical.py`, `optislang.py`, `workbench.py`。
  - 更新測試覆蓋率：測試檔增加至 4 個（`test_sessions.py`, `test_mechanical_controller.py`, `test_optislang_controller.py`, `test_workbench_controller.py`）。
