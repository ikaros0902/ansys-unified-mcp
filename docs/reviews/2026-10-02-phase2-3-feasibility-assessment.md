# Phase 2 & 3 計畫可行性評估與實作任務清單

> 本文件為**規劃評估**，不涉及任何架構變更執行。對應 `docs/planning/ANSYS_MCP_MASTER_PLAN_V4.md` 與 `docs/planning/PHASE_2_AND_3_EXECUTION_PLAN.md` 兩份願景文件。評估基準：2026-10-02 實際程式碼現況。

---

## 一、現況比對：計畫聲明 vs 實際程式碼

| 計畫聲稱的問題 / 待建項目 | 實際現況 | 判定 |
| --- | --- | --- |
| 「單一巨石伺服器，138 個 Tools 一次性載入」 | `__main__.py` 已有 `ANSYS_MCP_PROFILE` 環境變數，依 profile（all/mechanical/fluent/geometry/workbench/optislang）選擇性 import 對應 `products/*/tools.py`，非強制全載 | **部分已解決**：有輕量 profile 路由雛形，但非物理隔離（仍是單一進程單一 FastMCP 實例），且預設值仍是 `all` |
| 「多實例衝突，開第二個 SpaceClaim 無法被偵測」 | `bridges/connection_manager.py` 的 `ConnectionManager` 已實作 `scan_for_mechanical_grpc`/`scan_for_spaceclaim_grpc`/`scan_for_fluent_grpc`，皆為**範圍掃描**（如 50051~50070）而非寫死單一埠；另有 `workbench_queue/registry/` 以 PID 為鍵的 JSON 實例登錄，`find_all_instances()` 已回傳多產品多實例狀態 | **已大部分解決**：核心的「偵測多開」能力已存在。缺的是：(a) 啟動**新**實例時指定 `--port`/`--host` 的能力，目前只能被動掃描已開啟的實例；(b) 工具呼叫回傳文字中沒有即時顯示 Port/PID（Phase 2 要求的「黑盒子」改善項仍成立） |
| 「Phase 1 已完成，移除 mechanical.py 重複代碼」 | 查無 `products/mechanical.py`（已確實移除），但 `tools/mechanical_tools.py`、`tools/fluent_tools.py`、`tools/workbench_tools.py`、`tools/mechanical_workflow_tools.py` 四個檔案仍存在，內容與 `products/*/tools.py` 幾乎相同，只是 `__main__.py` 未 import 它們 | **聲稱不實**：重複代碼只是變成「死代碼」，沒有真正刪除。`products/mechanical_api.py` 則是刻意保留的 backward-compat shim，非重複 |
| 「SpaceClaim 連線複雜度高於 Mechanical，需統一 SessionManager」 | 目前兩產品各自有獨立的 `facade.py`（`MechanicalController`、`GeometryController`），皆遵循「`products/<name>/{facade,tools,driver}.py` 成對出現、session 走 `SessionRegistry`」的既定慣例（`docs/ARCHITECTURE.md` 已記載此目標形態） | **方向一致**：現有 `core/sessions.py` 的 `SessionRegistry` 已是跨產品統一的 session 登錄機制，Phase 3 的 `AnsSessionManager` 本質是在既有 `SessionRegistry` 之上加一層更友善的 `connect(product, port)` 介面，非從零建造 |
| 「SpaceClaim 批次腳本直通，延遲降 70%」 | `drivers/sim_impl.py`（740 行）已是 SpaceClaim 操作的主要實作，但採逐點 gRPC 呼叫模式；查無任何批次腳本直通或效能基準測試 | **全新項目**：無既有程式碼基礎，「降 70%」「15 秒→0.8 秒」兩個數字無任何基準測試佐證，屬未驗證假設 |
| 「`.mcp-workspaces/` 物理隔離目錄」「`servers/*.py` 獨立伺服器」「`connection/port_finder.py`」「`connection/session_manager.py`」「`resources/`」「`products/geometry/batch_executor.py`」 | 全部路徑查無 | **完全未開始** |
| 「`tests/unit/test_port_finder.py` 等驗證測試」 | 全部路徑查無 | **完全未開始**，Verification Plan 目前是空中樓閣 |

---

## 二、風險點與不確定性

1. **多進程化與現有全域 Session 狀態衝突（計畫完全未提及，屬最大風險）**
   `core/sessions.py` 的 `SessionRegistry` 目前是**單一進程內的全域記憶體狀態**。Phase 2 若把伺服器拆成 `servers/mechanical_server.py`、`servers/geometry_server.py` 等獨立進程，每個進程會有自己獨立的 `SessionRegistry` 實例——這其實是計畫想要的效果（物理隔離），但代價是：若使用者在 Mechanical workspace 連線後，想在 Geometry workspace 查詢「目前有哪些產品已連線」這類跨產品查詢（現有 `find_all_instances()` 提供的能力）會失效，除非額外設計跨進程共享機制（例如回退依賴 `workbench_queue/registry/` 的檔案系統登錄表作為唯一真相來源）。此設計決策兩份計畫文件都沒處理。

2. **拆分時容易複製到錯誤版本的程式碼**
   `tools/*.py` 與 `products/*/tools.py` 的重複檔案若不先清理，Phase 2 拆分獨立伺服器時，若誤引用 `tools/mechanical_tools.py`（死代碼、可能已過時）而非 `products/mechanical/tools.py`（實際運作版本），會引入已修復過的舊 bug。

3. **效能數字為未驗證假設**
   「SpaceClaim 批次腳本延遲降 70%」「15 秒→0.8 秒」無基準測試支持，可能是估計或口號式目標，不能當作驗收標準直接寫入 Verification Plan。

4. **MCP Resources 原語的 SDK 相容性未查證**
   Phase 3 要求实作 `ansys://mechanical/model-tree` 等 `@mcp.resource`，需確認專案所用的 MCP SDK（`shared.py` 中 `from ansys_unified_mcp.shared import mcp`）版本是否支援 resource 原語。`docs/ARCHITECTURE.md` 第 3 節提到 `@mcp.resource` 回傳 `str` 的例外規則，顯示 resource 原語本身已有先例（`workbench_tools.py` 的 `installation_resource`、`workbench_status_resource`），**技術上可行**，但 Phase 3 要擴充到 Mechanical/Geometry 的 model-tree、materials、named-selections 等新 Resource，工作量不小。

5. **`mcp_server.py` 刪除風險（2026-10-02 執行階段更正：原評估錯誤，不應刪除）**
   原稽核僅查證本機這份專案自己的 `pyproject.toml`、`mcp_config.json`，確認兩者皆未經過 `mcp_server.py`，據此判定「刪除無下游影響」。**此判定錯誤**：`docs/deployment/DEPLOYMENT_SOP.md` 的方案 A（Claude Desktop）與方案 B（Antigravity）皆明確教學外部使用者將 AI 客戶端設定檔指向 `mcp_server.py`，並稱其為「最穩健的啟動入口」。刪除會讓依照此 SOP 安裝的使用者設定直接失效。已改為方案 C：保留檔案並加註解說明其對外用途與誤判原因，防止下一輪重構再次誤刪。

6. **角色分工（`ansys_cae_specialist`、`system_one_judge`、`loop_reviewer`）為計畫文件自創名詞**
   `ANSYS_MCP_MASTER_PLAN_V4.md` 的「分工」段落提到的這些角色名稱，在專案 steering 規範或既有工具鏈中查無對應定義，需先確認這是否為實際可調用的 Sub-Agent 角色，或只是計畫撰寫時的佔位敘述。

---

## 三、可行性結論

| 項目 | 可行性 | 理由 |
| --- | --- | --- |
| Phase 2：清理 `tools/*.py` 死代碼 | **高，建議優先執行** | 範圍明確、風險低、直接償還 Phase 1 未完成的技術債 |
| Phase 2：Port 回顯機制（工具回傳文字含 Port/PID） | **高** | 現有 `ConnectionManager` 已有所需資訊來源，純粹是把現有資料加進回傳信封，不涉及架構變更 |
| Phase 2：`--port`/`--host` 啟動參數化 | **中高** | 需新增 `port_finder.py`，但可基於現有 `_is_port_open` 邏輯擴充，非從零開始 |
| Phase 2：`.mcp-workspaces/` 物理隔離 + 獨立伺服器進程 | **中，需先解決風險 1** | 技術上可行但需先設計跨進程 session 共享策略，否則會犧牲現有 `find_all_instances()` 的跨產品可見性 |
| Phase 3：統一 `AnsSessionManager` | **高** | 本質是在既有 `SessionRegistry` 上加一層介面封裝，非新建地基 |
| Phase 3：SpaceClaim 批次腳本直通 | **中，需先補基準測試** | 技術方向合理（類似 Mechanical 的 ACT 直通模式），但效能目標數字需先建立測量基準，不能照抄計畫文件的數字 |
| Phase 3：MCP Resources | **中高** | 專案已有 resource 原語先例可參考，純粹是擴充既有模式到更多端點 |

**總體判斷**：Phase 2 & 3 計畫方向與現有架構**不衝突**，大部分基礎設施（連線掃描、session 登錄、profile 路由）已有雛形，不是從零開始。但計畫文件本身對「多進程化後 session 如何共享」這個核心設計問題完全沒處理，是啟動實作前必須先補的設計缺口；且 Verification Plan 的測試檔案與效能數字目前都是空想，需要在實作過程中同步建立。

---

## 四、Phase 1 / 2 / 3 全部待辦項目逐條任務清單

本節逐條對照 `ANSYS_MCP_MASTER_PLAN_V4.md` 與 `PHASE_2_AND_3_EXECUTION_PLAN.md` 兩份文件中列出的**每一個** `[DELETE]`/`[MODIFY]`/`[NEW]` 項目，不重新分階段、不省略。每條皆標註現況查證結果與對應的具體任務。來源標記：`[MP4]` = `ANSYS_MCP_MASTER_PLAN_V4.md`，`[P23]` = `PHASE_2_AND_3_EXECUTION_PLAN.md`（僅含 Phase 2、3，Phase 1 以 `[MP4]` 為唯一來源）。

### Phase 1：止血與代碼去重複（Detox）

#### 任務 1.1 `[DELETE]` 清理 `src/ansys_unified_mcp/products/mechanical.py`
- **來源**：`[MP4]`「清理雙胞胎代碼」。
- **現況查證**：`products/mechanical.py` 本體**已不存在**，已被拆成 `products/mechanical/{facade.py, tools.py, api.py, driver.py}` 套件形式。此條**已完成**。
- **任務**：無需動作，僅記錄完成狀態。

#### 任務 1.2 `[MODIFY]` `src/ansys_unified_mcp/tools.py` 全數引用 `mechanical.facade`
- **來源**：`[MP4]`。
- **現況查證**：專案不存在單一的 `tools.py` 檔案（計畫文件寫的路徑本身已過時，現況是 `tools/` 目錄下多個檔案）。但等價問題仍存在：`tools/mechanical_tools.py`、`tools/mechanical_workflow_tools.py` 兩個死代碼檔案**沒有**引用 `products/mechanical/facade.py`，而是各自保有一份與 `products/mechanical/tools.py` 幾乎相同的獨立實作，且未被 `__main__.py` import。
- **任務**：
  1. 確認 `tools/mechanical_tools.py`、`tools/mechanical_workflow_tools.py`、`tools/fluent_tools.py`、`tools/workbench_tools.py` 四個檔案是否被任何測試或其他模組 import（非 `__main__.py` 以外的路徑）。
  2. 若確認無人引用：刪除此四檔案。
  3. 若發現測試依賴它們：先將測試改為引用 `products/*/tools.py` 對應版本，確認測試仍通過後再刪除死代碼。
  4. 驗證條件：全專案 `grep` 四個模組路徑字串，僅能在 `.pyc` 快取與本任務的提交記錄中出現，原始碼無其他引用。

#### 任務 1.3 `[MODIFY]` `scripts/` 目錄，將測試腳本遷移至 `examples/`
- **來源**：`[MP4]`。
- **現況查證**：`scripts/` 目前內容為 `scripts/maintenance/`、`scripts/deploy/`（見 `pyproject.toml` 的 ruff 排除規則 `scripts/deploy/**/*.py`），性質是部署與維護腳本，非測試腳本；`examples/` 已存在且有 `shock_analysis/`、`geometry_cleanup/`、`pcb_warpage/`、`mesh_debug/`、`samples/` 等工程範例目錄。
- **任務**：
  1. 盤點 `scripts/` 下是否還有「測試用」性質（而非部署/維護用）的腳本殘留（計畫文件未指名具體檔案，需實際列出 `scripts/` 全部內容後逐一歸類）。
  2. 若盤點後發現 `scripts/` 已不含測試腳本（可能在先前的重整中已處理掉），記錄為「已完成或已不適用」。
  3. 若有殘留，逐一搬移至 `examples/` 對應子目錄，並更新任何引用這些路徑的文件或程式碼。
  4. 驗證條件：`scripts/` 下僅剩部署/維護性質檔案，`examples/` 下的新增檔案可被現有或新增測試驗證可執行。

#### 任務 1.4 `[MODIFY]` `skills/` 目錄，統一 YAML 規範與漸進式揭露
- **來源**：`[MP4]`。
- **現況查證**：`skills/README.md` 顯示已有相當程度的統一（四預設角色、`name`/`description` front matter 慣例），且本次對話前段已處理過 `ansys-spaceclaim-modeling` 的技能完整性問題。但未逐一核對全部 17 個頂層技能是否每份皆符合 `11-skill-evolution.md` 的「根檔 ≤150 行、漸進式揭露三層結構」規範。
- **任務**：
  1. 逐一檢查 `skills/*/SKILL.md` 的行數是否皆 ≤150 行（`11-skill-evolution.md` 規定上限）。
  2. 核對每份 `SKILL.md` 的 YAML front matter 是否皆有 `name`、`description`，且觸發關鍵字夠精準（非泛用詞）。
  3. 核對超過 20 行的範例程式碼是否皆已外置到對應的 `scripts/*.py`，而非留在 `SKILL.md` 正文。
  4. 驗證條件：產出一份逐技能檢查表，記錄每份是否合規；不合規者列出具體修正項。

### Phase 2：對標官方的模組化拆分與多開支援（Modular MCP Servers）

#### 任務 2.1 `[NEW]` 拆分獨立產品入口 `servers/mechanical.py`、`servers/geometry.py`、`servers/mapdl.py`
- **來源**：`[MP4]` 簡述三檔；`[P23]` 擴充為五檔：`servers/mechanical_server.py`、`servers/geometry_server.py`、`servers/mapdl_server.py`、`servers/fluent_server.py`、`servers/core_server.py`。
- **現況查證**：`src/ansys_unified_mcp/servers/` 目錄完全不存在。
- **任務**：**依賴任務 0.1 決策結果**，若決策為選項 B（真拆多進程）才執行：
  1. 建立 `src/ansys_unified_mcp/servers/` 目錄。
  2. 逐一建立 `mechanical_server.py`、`geometry_server.py`、`mapdl_server.py`、`fluent_server.py`、`core_server.py`，每個檔案建立獨立 `FastMCP` 實例並僅 import 對應 `products/<name>/tools.py`（`mapdl` 目前無對應 `products/` 子目錄，需先確認是否要新增或此項暫緩）。
  3. 驗證條件：每個伺服器可獨立啟動，`mcp.list_tools()` 僅回傳對應產品的工具且數量符合 `[P23]` 標註的範圍（Mechanical 15、Geometry 12）。

#### 任務 2.2 `[DELETE]` 巨石入口 `mcp_server.py`（執行結果：改為不刪除，原計畫前提有誤）
- **來源**：`[P23]`。
- **原現況查證（有誤）**：原稽核僅查證本機 `pyproject.toml`、`mcp_config.json` 皆未經過此檔案，據此誤判刪除無下游影響。
- **執行階段發現**：`docs/deployment/DEPLOYMENT_SOP.md` 方案 A、B 皆明確教學外部使用者將 AI 客戶端指向 `mcp_server.py`，是文件化的官方安裝入口。此外，此檔案本身也不是計畫所指的「巨石伺服器」問題（巨石問題來自 `__main__.py` 的 `ANSYS_MCP_PROFILE` 預設值 `all`，與此入口腳本是否存在無關），刪除它不會解決計畫真正想解決的問題。
- **最終處置**：不刪除。在 `mcp_server.py` 檔案頂部加註解，說明其對外用途與先前的誤判原因，防止後續重構再次誤刪。
- **若未來仍要刪除**：須同步改寫 `DEPLOYMENT_SOP.md` 兩個方案的設定範例為 `-m ansys_unified_mcp.__main__`，並驗證改用此啟動方式時 `src` 目錄仍會正確加入 `sys.path`。

#### 任務 2.3 `[NEW]` 導入 `--port`、`--host` 參數支援與自動空閒 Port 偵測（執行結果：縮小範圍，不做 CLI 參數）
- **來源**：`[MP4]` 簡述；`[P23]` 具體化為 `src/ansys_unified_mcp/connection/port_finder.py` 提供 `find_free_port(start_port=50051)`，並要求所有伺服器入口支援 argparse。
- **執行階段查證**：重讀 `README.md`「自動連線機制」一節確認：本專案實際運作模式是「使用者手動開啟 ANSYS，MCP Agent 被動掃描偵測」，不是「MCP 主動以指定 Port 啟動新 ANSYS 實例」。進一步查證 `products/geometry/tools.py` 的 `geometry_launch(port, host, ...)` 與 `products/fluent/tools.py` 的 `fluent_launch(..., port, ip, ...)` 皆已接受 `port` 參數；僅 `MechanicalController.launch(self, batch: bool = True)` 完全沒有 port 參數。因此計畫原始設想的「CLI 啟動參數」情境在此架構下不成立。
- **已完成**：
  1. 新增 `src/ansys_unified_mcp/connection/port_finder.py`，提供 `find_free_port(start_port, end_port, host)` 與 `is_port_open(port, host, timeout)`，從 `ConnectionManager._is_port_open` 抽出為獨立可重用函式。
  2. 不新增 CLI `--port`/`--host`/`--auto-port` 參數（計畫文件的使用情境不成立，見上）。
  3. 新增 `tests/unit/test_port_finder.py`，覆蓋「埠已被占用時找到下一個空閒埠」「範圍耗盡回傳 None」「非法埠值一律視為未開啟」三種情境，共 3 個測試案例。
- **驗證條件**：`pytest tests/unit/test_port_finder.py` 3 個測試全通過；全專案測試 501 passed（較前一輪新增 3 個）。
- **遺留事項**：若未來確定需要「`MechanicalController.launch()` 讓呼叫端指定想要的 port」這個情境（例如多開時想精確控制新實例的埠號），可呼叫本模組的 `find_free_port` 補上該參數，但這是獨立的新功能需求，不在本次任務範圍內一併做。

#### 任務 2.4 `[NEW]` Port 可視化與日誌反饋機制（已完成）
- **來源**：`[MP4]`「杜絕黑盒子」；`[P23]` 具體化為日誌與回傳文字格式範例 `[ANSYS Session Ready] Product / Endpoint / Process PID / Status`。
- **執行階段查證**：`workbench_queue/registry/` 僅由 Mechanical/Workbench 的 ACT 外掛寫入 PID 對應資訊，SpaceClaim/Fluent/optiSLang 經 PyAnsys 直連啟動的 session 不會出現在此登錄表中，故無法沿用 `MechanicalController._resolve_target_port` 現有的 registry 查詢方式取得 PID。
- **已完成**：
  1. 在 `ConnectionManager` 新增 `find_pid_by_port(port)`，以 `psutil.net_connections(kind="tcp")` 掃描 `CONN_LISTEN` 狀態連線反查 PID，不限定於 Mechanical，任何以埠號通訊的產品皆可用。
  2. `MechanicalController.connect()`、`launch()`：回傳信封補上 `pid` 欄位（原已有 `port`）。
  3. `GeometryController.launch()`：回傳信封補上 `port`、`pid`（原僅有 `key`）。
  4. `FluentController.launch()`：回傳信封補上 `port`、`pid`（原 port 僅存在於自由文字 `message` 內）。
  5. `OptislangController.connect()`：補上 `pid`，但改用 `find_running_ansys_processes()` 的進程名稱比對（`optislang.exe`），因 optiSLang 無獨立 gRPC Port 概念，與其他三者的埠號反查邏輯不同。
  6. 格式遵循專案既有扁平信封慣例（`{"ok": True, "port": ..., "pid": ..., ...}`），不照抄計畫文件的多行文字範例格式；未額外修改 `logger.info` 呼叫（現況各 facade 多數沒有 info 等級日誌，屬於更大範圍的日誌規範化工作，不在本次最小變更範圍內）。
- **驗證條件**：新增 `tests/unit/test_connection_manager.py` 五個測試覆蓋 `find_pid_by_port`（成功匹配、忽略非 LISTEN 連線、無匹配、psutil 例外、非法埠值）；全專案測試 506 passed（較前一輪新增 5 個）。

#### 任務 2.5 `[NEW]` 建立 `.mcp-workspaces/` 隔離工作區
- **來源**：`[MP4]`「阻斷 Context 污染」；`[P23]` 具體化為 `.mcp-workspaces/{mechanical,geometry,fluent}/.mcp.json`，各自掛載對應子伺服器（約 10~15 工具），聲稱 Token 消耗從 15,000+ 降至 1,500 左右。
- **現況查證**：目錄不存在；「Token 消耗降至 1,500」為未經測量的目標數字。
- **任務**：**依賴任務 0.1 決策結果**，若決策為選項 B 才執行：
  1. 建立 `.mcp-workspaces/mechanical/`、`.mcp-workspaces/geometry/`、`.mcp-workspaces/fluent/` 目錄結構。
  2. 各目錄下建立 `.mcp.json`，指向對應任務 2.1 建立的獨立伺服器入口。
  3. 實測各 workspace 啟動後的實際 Token 占用（而非照抄計畫文件的 1,500 數字），記錄實測值。
  4. 驗證條件：在其中一個 workspace 啟動會話，確認僅能看到該 workspace 對應產品的工具，且無法呼叫其他產品的工具。

### Phase 3：連線門面統一與資源化（Unified Facade & Resources）

#### 任務 3.1 `[NEW]` 統一連線門面 `AnsSessionManager`（已完成）
- **來源**：`[MP4]` 簡述；`[P23]` 具體化為 `src/ansys_unified_mcp/connection/session_manager.py`，提供 `SessionManager.connect(product="spaceclaim", port=50051)` 統一介面，內部封裝 Windows 原生安全驗證、焦點檢測與多文件上下文綁定。
- **執行階段查證**：逐一比對四個 facade 的 `connect`/`launch` 簽名後確認無法收斂成單一位置參數簽名——`MechanicalController.connect(port, pid)`、`GeometryController.launch(port, host, transport_mode, connect_timeout)`、`FluentController.launch(processors, cwd, port, ip, password, connect_timeout)`、`OptislangController.connect(project_path, ini_timeout)` 四者參數結構差異大，且 Geometry/Fluent 無獨立 `connect`（以 `launch` 身兼兩種行為），optiSLang 無 port 概念。
- **已完成**：
  1. 新增 `src/ansys_unified_mcp/connection/session_manager.py`，`AnsSessionManager` 提供 `connect(product, **kwargs)`、`launch(product, **kwargs)`、`status(product, **kwargs)`、`disconnect(product, **kwargs)` 四個統一入口，依 `product` 字串委派至對應 controller 的原生方法，`**kwargs` 透傳而非強制統一簽名。
  2. 不廢棄任何既有 controller 或 `SessionRegistry`，純委派層，不重新實作連線邏輯。
  3. 未知 `product` 名稱回傳標準失敗信封（`{"ok": False, "error": "..."}`），不拋出例外。
- **驗證條件**：新增 `tests/unit/test_session_manager.py` 8 個測試（涵蓋四產品的 connect/launch/status/disconnect 委派正確性，含方法名稱因產品而異如 `close`/`exit`/`disconnect` 的差異，以及未知產品錯誤處理）；既有 `tests/test_sessions.py`、`tests/test_mechanical_controller.py`、`tests/test_optislang_controller.py` 全數維持通過；全專案測試 514 passed（較前一輪新增 8 個）。

#### 任務 3.2 `[MODIFY]` SpaceClaim 連線優化：批次腳本通道
- **來源**：`[MP4]`「使其速度追平 Mechanical」；`[P23]` 具體化為 `src/ansys_unified_mcp/products/geometry/batch_executor.py`，聲稱複雜特徵抽取延遲由 15 秒降至 0.8 秒以內。
- **現況查證**：`products/geometry/` 現有 `facade.py`、`tools.py`、`driver.py`，皆無批次腳本直通實作；SpaceClaim 操作透過 `drivers/sim_impl.py`（740 行）逐點 gRPC 呼叫。「15 秒→0.8 秒」為未經測量的目標數字。
- **任務**：
  1. **先建立效能基準**：在現有逐點 gRPC 模式下，對一個具代表性的操作（例如建立外流域並布林相減，對應剛才復原的 `ansys-spaceclaim-modeling` 技能的 `create_enclosure_demo.py` 情境）量測實際延遲，取得基準值。
  2. 新增 `src/ansys_unified_mcp/products/geometry/batch_executor.py`，仿照 Mechanical 的 ACT 腳本直通模式（`MechanicalController.run_script()` 的「組一段腳本字串、一次性丟給 `ExtAPI` 執行」做法），改為一次性丟一段完整 IronPython/SpaceClaim API 腳本而非逐點 RPC。
  3. 用同一個代表性操作重新量測延遲，與基準值對比，得出實際改善幅度（不預設為 70%）。
  4. 驗證條件：新增 `tests/integration/test_batch_geometry.py`，涵蓋批次腳本直通執行穩定性；基準測試前後數據附在 PR 或對應的 Memory_File 記錄中。

#### 任務 3.3 `[NEW]` 實作 MCP Resources（模型樹、材料庫端點）（部分完成，1 項因無既有能力可包裝而不實作）
- **來源**：`[MP4]` 簡述；`[P23]` 具體化為 `src/ansys_unified_mcp/resources/` 下四個 URI：`ansys://mechanical/model-tree`、`ansys://mechanical/materials`、`ansys://geometry/model-tree`、`ansys://geometry/named-selections`，聲稱節省 80% Tool 呼叫額度。
- **執行階段查證**：
  1. 確認既有 `@mcp.resource` 先例（`workbench_tools.py` 的 `installation_resource`、`workbench_status_resource`）皆為同步函式、回傳 `json.dumps(...)` 字串，無既有測試覆蓋。
  2. 查證 `drivers/sim_impl.py` 的 `call_tool` 分派表後確認：全專案**無任何**既有具名選擇（Named Selection）查詢能力可供 `ansys://geometry/named-selections` 包裝——這需要新寫 PyAnsys Geometry 查詢邏輯，屬獨立新功能需求，不是「擴充既有模式至更多端點」，故不在本次範圍內實作。
  3. 未新增獨立 `src/ansys_unified_mcp/resources/` 目錄：三個已實作的 Resource 各自放在對應產品的 `tools.py` 內（緊鄰其委派的既有工具函式），與既有 `installation_resource`/`workbench_status_resource` 放在 `workbench/tools.py` 的既定慣例一致，不另立新目錄打破現有佈局。
- **已完成**（3/4）：
  1. `ansys://mechanical/model-tree`（`products/mechanical/tools.py`）：委派 `MechanicalController.run_script`，與 `mechanical_get_model_info` 工具共用同一段 ACT 查詢腳本。
  2. `ansys://mechanical/materials`（`products/mechanical/tools.py`）：委派同一 controller，與 `mechanical_list_materials` 共用查詢腳本。
  3. `ansys://geometry/model-tree`（`products/geometry/tools.py`，`async def`）：委派既有 `geometry_list_bodies` 的 `sim_impl.call_tool` 邏輯。因 Geometry 工具層本身是 `async`，此 Resource 亦為 `async def`，與 Mechanical 側的同步寫法不同，皆為忠實反映各產品既有程式碼風格。
- **未實作**（1/4）：`ansys://geometry/named-selections`——無既有能力可包裝，列為後續若有需求時的獨立功能待辦，不在本次任務中生造。
- **驗證條件**：新增 `tests/unit/test_mcp_resources.py` 6 個測試（Mechanical 兩個 Resource 各自的未連線/成功解析/解析失敗情境，Geometry Resource 的委派驗證）；全專案測試 520 passed（較前一輪新增 6 個）。「節省 80% Tool 呼叫額度」未實測（無法在未連線真實 ANSYS 的環境下測量），不照抄計畫文件估計值，如實記錄為未驗證。

### 決策前置任務（阻塞 2.1、2.5，建議最先處理）

#### 任務 0.1 Session 共享策略決策

**背景補充（詳閱 `core/sessions.py` 與 `products/mechanical/facade.py` 後確認）**：`SessionRegistry` 存放的不是可序列化的連線資訊，而是**存活的 Python 物件本身**——例如 `MechanicalController.connect()` 呼叫 `mech.connect_to_mechanical(port=target_port)` 後，拿到的是一個持有開放 gRPC channel 的 PyMechanical session 物件，直接 `registry.put(PRODUCT, key, session)` 存進去；之後每次 `run_script()` 都是對這個記憶體中的物件呼叫方法。這代表 session 本質上**無法跨進程共享**，只能活在建立它的那個進程裡。三個選項的核心差異，就是「進程邊界改變後，這個限制怎麼處理」。

#### 選項 A：維持單一進程，僅靠 `ANSYS_MCP_PROFILE` 限制工具載入範圍

**做法**：不新增任何進程邊界。`__main__.py` 現有的 `ANSYS_MCP_PROFILE` 機制已經可以讓使用者在啟動時只載入某個產品的工具（例如 `ANSYS_MCP_PROFILE=mechanical` 只載入 `products/mechanical/tools.py`），藉此降低單次會話的 Context 佔用。若要更進一步，可以把這個環境變數的切換包裝成每個「工作區」各自的啟動設定（例如不同的 `mcp_config.json` profile，分別對應不同 `ANSYS_MCP_PROFILE` 值），但底層仍是同一份原始碼、同一個 `SessionRegistry` 類別。

**對 Session 共享的影響**：完全不受影響。因為只有一個進程、一個 `SessionRegistry` 實例，`find_all_instances()`、跨產品查詢等現有能力全部維持原狀。

**優點**：
- 零遷移風險，現有 `products/*/facade.py` 完全不用改。
- 立即可用：只要在啟動設定（`mcp_config.json` 或等效設定）多開幾組不同 `ANSYS_MCP_PROFILE` 值的設定檔即可。
- 跨產品可見性（例如「我同時連了 Mechanical 和 SpaceClaim，想一次查詢兩者狀態」）天然保留。

**缺點**：
- 不是真正的物理隔離。如果使用者在 `mechanical` profile 的會話中，仍有辦法透過某種路徑誤觸其他產品的程式碼（雖然目前 `import` 層級已經做了範圍限制，但不像獨立進程那樣有作業系統層的硬邊界），安全邊界比 Phase 2 原始設計弱。
- Token 降載效果取決於「使用者是否真的只開一種 profile 的會話」，如果同一個會話視窗仍常態切換多個 profile，省下的 Context 有限。
- 不滿足 Master Plan v4 原始訴求「多個獨立 MCP Server 程序」，如果這是對外（例如對標官方 `ansys-mechanical-mcp` 的工具生態）展示架構對齊的硬性要求，選項 A 無法滿足。

**適用情境**：若 Phase 2 的真正目的是「降低單次會話 Context 佔用」，選項 A 用最小代價達成；若目的是「對標官方獨立 MCP Server 生態、或要有進程級別的安全隔離」，選項 A 不夠。

---

#### 選項 B：真正拆成多進程獨立伺服器，犧牲即時跨進程可見性

**做法**：依計畫原始設計，建立 `servers/mechanical_server.py`、`servers/geometry_server.py` 等各自獨立的入口腳本，每個腳本各自 `import` 對應的 `products/<name>/tools.py` 並啟動**自己的** `FastMCP` 實例與**自己的** `SessionRegistry` 實例（因為 `SessionRegistry` 目前是模組層級的 process-wide singleton，每個獨立進程啟動後會各自產生一份全新的、互不相通的 registry）。

**對 Session 共享的影響**：
- 同一進程內的 session 查詢（例如 Mechanical server 進程內部查「目前有哪些 Mechanical 連線」）完全不受影響，`SessionRegistry` 原邏輯照常運作。
- **跨進程**的查詢會完全失去即時性：例如 Geometry server 進程無法直接問 Mechanical server 進程「你現在連了誰」，因為兩者是不同作業系統進程、不同記憶體空間。
- 補救方式：依賴現有的 `workbench_queue/registry/`（PID 鍵的 JSON 檔案）作為跨進程的「唯一真相來源」。各 server 進程在建立/中斷連線時，除了寫自己的 `SessionRegistry`，額外同步寫一筆 JSON 到這個共用目錄；查詢跨產品狀態時，改讀這個檔案系統登錄表而非記憶體物件。但這只能提供「連線中繼資料」（Port、PID、產品名稱），**不能**讓另一個進程直接拿到 session 物件本身去執行腳本——若使用者想從 Geometry workspace 操作 Mechanical，仍必須透過某種進程間通訊（IPC）或是切換到 Mechanical workspace 重新連線。

**優點**：
- 符合 Master Plan v4 原始訴求的物理隔離與對標官方生態。
- 作業系統層級的進程邊界，安全性與故障隔離性最強（一個產品的伺服器崩潃不影響其他產品）。
- 每個 workspace 的工具數量可嚴格控制在計畫要求的「≤ 20 個」。

**缺點**：
- 需要新設計跨進程通訊層（至少是「唯一真相來源」的讀寫協議），這是計畫文件完全沒處理、必須額外開發的部分。
- 使用者在不同產品間切換操作的體驗變複雜：原本「連線 Mechanical 又連線 SpaceClaim」可以在同一個會話視窗完成，拆開後可能需要切換 workspace 設定或開多個會話視窗。
- 既有 `tests/test_sessions.py`、`tests/test_mechanical_controller.py` 等測試若假設單一全域 `registry`，需要重新評估是否仍適用於多進程場景。
- 工作量明顯大於選項 A：需新增 `servers/` 目錄下至少 4-5 個入口腳本、新增跨進程登錄表讀寫邏輯、重新設計 `.mcp-workspaces/*/\.mcp.json` 的掛載方式。

**適用情境**：若對外架構對齊（例如與官方 `ansys-mechanical-mcp` 生態的相容性）或安全隔離是硬性需求，選項 B 是唯一能真正滿足的方案，但需要先接受「跨產品即時查詢」這個現有能力會降級。

---

#### 選項 C：維持單一進程，查證 FastMCP 是否支援單進程內的邏輯隔離掛載（**已查證：可行**）

**查證結果（2026-10-02）**：專案實際安裝的 `fastmcp==3.4.5`（`.venv/Lib/site-packages/fastmcp/server/server.py:2124`）的 `FastMCP.mount(server, namespace=None, ...)` 方法**確實提供此機制**：

- `mount()` 讓一個 `FastMCP` 實例把另一個 `FastMCP` 實例「掛載」進來，掛載後父伺服器會把對應工具呼叫**即時轉發**給被掛載的子伺服器，兩者仍在**同一個 Python 進程、同一塊記憶體空間**內運作。
- 掛載時可指定 `namespace`：子伺服器的工具會以 `{namespace}_{tool_name}` 形式出現在父伺服器的工具清單中；不指定 `namespace` 時以原名出現，多個子伺服器可同時掛載、依序嘗試比對。
- 官方文件明確區分 `mount()`（動態即時轉發，子伺服器之後的變更會立即反映）與 `import_server()`（靜態一次性複製），本情境應使用前者。

**對 Session 共享的影響（修正前次分析）**：因為 `mount()` 是單進程機制，所有被掛載的子伺服器與父伺服器共享同一個 Python 記憶體空間，`core/sessions.py` 的 `SessionRegistry`（process-wide singleton）**天然維持全域唯一、不受影響**——這與選項 A 相同，不像選項 B 需要額外設計跨進程通訊層。

**若採用選項 C 的實際改動範圍**：
1. 現況 `shared.py` 的 `mcp = FastMCP("ansys-unified-mcp", ...)` 是**單一全域實例**，各 `products/*/tools.py` 皆直接 `from ansys_unified_mcp.shared import mcp` 並在其上 `@mcp.tool()` 註冊。
2. 改用 `mount()` 需要讓每個產品改用**各自獨立**的 `FastMCP` 實例（例如 `mechanical_mcp = FastMCP("mechanical")`），把該產品的 `@mcp.tool()` 改指向自己的實例，再於頂層伺服器視 `ANSYS_MCP_PROFILE` 決定掛載哪些子伺服器。
3. 此改動**機械且低風險**：`aliased_tool`、`as_envelope`、`SessionRegistry` 等既有機制完全不受影響，純粹是改變每個 `tools.py` 內 `@mcp.tool()` 裝飾器指向的目標實例，屬於一次性、可逐產品分批進行的重構，不是架構重寫。

**優點**（維持前次分析，確定可行後更新為肯定語氣）：
- 確定可同時取得「對外行為上像是物理隔離」（依 profile 只掛載對應子伺服器，workspace 只看到該產品工具）與「內部不犧牲 session 共享」兩者的好處。
- 不需要新增跨進程通訊層或檔案系統登錄表作為唯一真相來源，`find_all_instances()` 等既有跨產品查詢能力全部保留。
- 改動範圍機械可控，可逐產品分批執行，不是一次性大改。

**缺點**：
- 仍是單進程，無法提供選項 B 的作業系統層級安全邊界（例如一個產品的程式碼仍有辦法在同進程內存取到其他產品的物件）；若安全隔離是硬性需求，選項 C 不滿足。
- 若未來真的需要「對標官方獨立 MCP Server 生態」做跨機器部署或獨立發布單一產品的 MCP Server，選項 C 仍是單進程單一部署單元，無法滿足。

**適用情境**：若 Phase 2 的真正目的是「依 workspace 限制工具可見範圍、降低 Context 占用，同時保留跨產品 session 可見性」，選項 C 現已確認技術可行，且改動成本低於選項 B。

---

**三選項比較摘要（已依查證結果更新）**：

| 比較項目 | 選項 A | 選項 B | 選項 C |
| --- | --- | --- | --- |
| 跨產品 session 即時可見性 | 保留 | 犧牲（降級為檔案系統登錄表） | 保留 |
| 作業系統層級安全隔離 | 無 | 有 | 無 |
| 對標官方獨立 MCP Server 生態 | 不滿足 | 滿足 | 不滿足（仍單進程單一部署單元） |
| 新增開發工作量 | 最低（接近零） | 最高（需新建跨進程通訊層） | 中（改動機械可控，可逐產品分批） |
| 技術可行性確定性 | 已確認可行 | 已確認可行（但有額外設計工作） | **已確認可行**（`fastmcp==3.4.5` 的 `FastMCP.mount()`） |
| 現有測試相容性 | 全部不受影響 | 需重新評估部分測試假設 | 需逐產品調整 `@mcp.tool()` 註冊目標，但核心邏輯測試不受影響 |

決策建議（已更新）：選項 C 的技術可行性已於 2026-10-02 查證確認，不再是未知風險。若 Phase 2 的目標是「降低 Context 占用 + 依 workspace 限制工具可見範圍」而非「對標官方生態做獨立進程部署」，選項 C 在同等達成前者目標的前提下，付出的改動成本與風險皆低於選項 B，且不犧牲選項 A 的 session 共享優勢，是目前三者中較均衡的選擇；若明確需要作業系統層級隔離或獨立部署能力，仍須選選項 B。

#### 任務 0.2 分工角色定義查證
- **來源**：`[MP4]` 的「分工」段落提及 `system_one_judge`、`loop_reviewer`、`ansys_cae_specialist` 三個角色名稱。
- **現況查證**：這些名稱與 `.kiro/agents/` 下的 Sub-Agent 定義是否對應，尚未查證（本次評估未深入檢查 `.kiro/agents/` 目錄內容）。
- **任務**：確認這三個角色名稱是否為可直接調用的既有 Sub-Agent，或僅為計畫撰寫時的敘述性佔位詞；若是後者，決定由誰（或哪個既有角色）實際承擔對應工作。
- **驗證條件**：產出角色對應表，或確認「分工」段落僅供參考、實際執行時不特別區分角色。

---

## 六、多開埠遞進能力查證（2026-10-02 補充，影響任務 2.1/2.3/2.5 的前提假設）

本節查證「多開 Mechanical / SpaceClaim 時，Port 是否會自動遞進」，直接影響 Phase 2 多開支援相關任務的可行性前提。

### 查證方法

- **Mechanical**：讀 `scripts/deploy/act_plugins/main.py`（本專案自己撰寫的 ACT 外掛）。
- **SpaceClaim**：讀 `scripts/deploy/act_plugins/start_api_server.py`（本專案自己撰寫的啟動腳本），並對本機實際安裝的 `D:\ANSYS Inc\v251\Addins\ApiServer\Presentation.ApiServerAddIn.dll` 與 `Infrastructure.ApiGrpcServer.dll` 進行 .NET reflection（檢視公開/非公開方法簽章與欄位），輔以在組件二進位內搜尋 `ANSRV_GEO_PORT`、`50051` 等字串常值。

### 查證結果

| | Mechanical | SpaceClaim |
| --- | --- | --- |
| 第一個實例預設埠 | 10000 | 50051 |
| 多開第二個實例時 | **會自動遞進**至 10001、10002... | **不會遞進**，仍嘗試綁定 50051，失敗 |
| 遞進邏輯來源 | **本專案自己寫的** `main.py` 內 `find_free_port(10000, max_attempts=100)`（逐一嘗試 `socket.bind()`，綁定成功即回傳），再呼叫 `ExtAPI.Application.StartGrpcServer(grpc_port)` | 無。`start_api_server.py` 直接呼叫 ANSYS 官方 `ApiServerAddIn.Initialize()` / `.Connect()`，零參數、不含任何埠選擇邏輯 |
| 根因層級 | 本專案的 Python 外掛主動做了埠探測 | 本專案的啟動腳本**沒有**做埠探測，不是 Windows 或 ANSYS 底層的限制 |

**關鍵澄清**：Master Plan v4 文件所述「SpaceClaim 手動多開時 Windows 不會自動遞增 Port」，根因不是作業系統或 ANSYS 無法支援，而是**本專案目前的 SpaceClaim 啟動腳本本身沒有實作像 Mechanical 那樣的埠探測邏輯**。

### 底層 ANSYS 元件是否支援自訂埠（.NET reflection 查證）

- `ApiServerAddIn`（`Presentation.ApiServerAddIn.dll`）公開方法僅 `Connect()`、`Disconnect()`、`GetCustomUI()`、`Initialize()`、`AddServerServices(services, owner)`，**`Initialize()` 零參數，無法從外部傳入埠號**。
- 往下層的 `ApiGrpcServer`（`Infrastructure.ApiGrpcServer.dll`，真正做 gRPC 綁定的類別）則提供 `StartServer(IEnumerable<T> ports)`、`InitializeServer(string address)`、`Start(string endPoint)`——**底層基礎設施本身支援指定埠清單，`50051` 並非寫死在這層**。
- 在 `ApiServerAddIn.dll`、`Infrastructure.ApiGrpcServer.dll`、`Infrastructure.ApiDiscoveryV251.dll`、`Infrastructure.ApiGeometryGrpcServices.dll` 等相關組件的二進位內搜尋 `50051`、`ANSRV_GEO_PORT` 字串常值，**全部查無結果**——代表這個預設埠值並非以明文常數存在於這些組件，應是透過更上層的設定機制（環境變數讀取、DI 容器注入，或 SpaceClaim 主程式啟動時組裝參數）決定後再餵進 `StartServer(ports)`。
- **查證上限**：受限於本環境僅能用 .NET reflection 檢視方法簽章與欄位，無法反編譯 IL 方法主體（無 `ildasm`/`dnSpy` 等工具），故**無法確認**「`ANSRV_GEO_PORT` 環境變數在 `Initialize()` 內部調用鏈中究竟如何被讀取並傳給 `StartServer`」這一步的實際接線方式。

### 對計畫任務的影響

| 任務 | 原假設 | 查證後更新 |
| --- | --- | --- |
| 任務 2.1（獨立伺服器入口，依賴任務 0.1 決策） | 多開支援對 Mechanical、SpaceClaim 一視同仁 | **Mechanical 多開已有解（複製現有 `find_free_port` 模式即可）；SpaceClaim 多開需要先驗證「啟動前設定不同 `ANSRV_GEO_PORT` 環境變數值」是否真的會讓 `Initialize()` 綁定到該埠**——這是一個需要實測（啟動兩個 SpaceClaim 進程、各自設定不同環境變數、觀察實際綁定埠）才能確認的假設，不能直接當作已驗證事實排入開發排程 |
| 任務 2.3（`port_finder.py`） | 已完成，但範圍限定在「尋找空閒埠」這一純函式能力 | 不變，此函式本身與 ANSYS 端如何套用該埠號無關；若 SpaceClaim 多開可行性確認後要用上這個函式，仍可直接複用 |
| 任務 2.5（`.mcp-workspaces/`，依賴任務 0.1 決策） | 隔離工作區假設所有產品都能乾淨多開 | 若採用選項 B（真拆多進程）且使用情境包含「同時開兩個 SpaceClaim workspace」，**必須先完成上述 SpaceClaim 多開實測**，否則第二個 workspace 連接的 SpaceClaim 後端可能根本啟動失敗，此風險應併入任務 0.1 決策的評估範圍 |

### 後續建議（原列為待辦，現已完成實測並落地）

1. **~~實測 SpaceClaim 多開~~（已完成，2026-10-02 由使用者於有桌面畫面環境手動實測確認）**：
   - 查證過程中已先透過 PyAnsys Geometry 原始碼（`ansys/geometry/core/connection/product_instance.py`）確認官方 `launch_modeler_with_spaceclaim(port=...)` 內部透過環境變數 **`API_PORT`**（非 Master Plan 原文猜測的 `ANSRV_GEO_PORT`——此猜測已證實有誤）傳遞埠號給 SpaceClaim 子進程。
   - 本機（無桌面畫面環境）測試一度逾時未能確認，因 SpaceClaim 啟動過程可能卡在互動對話框，無頭環境無法排查。
   - 使用者於有桌面畫面的環境手動實測後確認：**設定 `API_PORT` 環境變數後啟動 SpaceClaim，確實能讓其綁定到指定的非預設埠**，機制有效。
2. **已落地的解決方案**（已實作，見下方程式碼變更）：採用「背景常駐 Port Watcher」策略，而非逐一手動指定埠——因為 SpaceClaim 多開情境下，使用者通常是在 Workbench 內依序點開多個 SpaceClaim 系統，而非透過程式化呼叫逐一指定埠號，故設計為持續更新環境變數，讓每次新開啟的 SpaceClaim 自動繼承當前最新的空閒埠。

### 已落地的程式碼變更（2026-10-02）

#### `scripts/deploy/act_plugins/main.py`

1. **`find_free_port` 強化**：原版僅用 `socket.bind()` 單一方式測試埠是否空閒；新版改為兩段式驗證：
   - 先嘗試 `connect()` 到該埠，若連線成功代表已有服務在監聽（occupied），跳過。
   - 連線失敗後，再用 `bind(('0.0.0.0', port))`（不使用 `SO_REUSEADDR`）驗證是否真正可綁定。
   - 此修改讓埠偵測更嚴謹，避免 `SO_REUSEADDR` 可能造成的誤判（綁定成功但實際上埠已被其他程序以非 reuse 模式佔用的邊界情況）。
2. **新增 `_start_spaceclaim_port_watcher()`**：Workbench Project Schematic 載入時（`on_project_init`）啟動一個背景常駐執行緒（`threading.Thread(daemon=True)`），每秒執行一次 `find_free_port(50051)`，並透過 `System.Environment.SetEnvironmentVariable("API_PORT", str(port))` 持續把目前的 Workbench 進程環境變數更新為「當前最新的空閒埠」。
   - **設計理由**：使用者在 Workbench 內依序開啟多個 SpaceClaim 系統時，每個 SpaceClaim 子進程繼承父進程（Workbench）當時的環境變數快照。只要在使用者點擊開啟 SpaceClaim 之前，`API_PORT` 已被 watcher 更新為最新空閒埠，新開的 SpaceClaim 就會自動綁定到該埠，不需使用者手動介入或逐一指定參數。
   - 用 `_WORKBENCH_MCP_SC_WATCHER_STARTED` sentinel 旗標防止重複啟動多個 watcher 執行緒。

#### 新增 `scripts/launch_spaceclaim_auto.bat`

獨立的 Windows 批次檔，供**不透過 Workbench、直接啟動單一 SpaceClaim**的情境使用：以 PowerShell 內嵌邏輯從 50051 起掃描第一個空閒埠，設定 `$env:API_PORT`，再啟動 `SpaceClaim.exe`。

**已知限制（待後續處理，非本次任務阻塞項）**：此批次檔內的 SpaceClaim 執行檔路徑 `D:\ANSYS Inc\v261\scdm\SpaceClaim.exe` 是**寫死的機器特定絕對路徑**，與專案既有的 `core/paths.py` 統一路徑解析原則（支援 `AWP_ROOT*` 環境變數與多候選版本）不一致，在其他機器或其他 ANSYS 版本上會失效。建議後續改為呼叫 `core/paths.py` 的路徑解析邏輯，或至少改用環境變數覆蓋，而非硬編碼單一路徑。

### 對計畫任務的最終影響（更新）

| 任務 | 查證前假設 | 最終落地結果 |
| --- | --- | --- |
| 任務 2.1（獨立伺服器入口，依賴任務 0.1 決策） | SpaceClaim 多開可行性未知，可能阻塞 | **SpaceClaim 多開已確認可行且已落地**，Mechanical 與 SpaceClaim 皆有各自的埠遞進機制，任務 2.1/2.5 若採用選項 B，不再有 SpaceClaim 端的多開可行性風險 |
| 任務 2.3（`port_finder.py`） | 已完成，純函式能力與 ANSYS 端套用方式無關 | 不變；若後續要把 `main.py` 的 `find_free_port`（IronPython 環境專用，無法直接 import 本專案套件）與 `connection/port_finder.py`（CPython 環境）的邏輯統一，可列為技術債，但非阻塞項 |
| 任務 2.5（`.mcp-workspaces/`，依賴任務 0.1 決策） | 風險：SpaceClaim 多 workspace 可能因埠衝突而無法運作 | 風險已解除：SpaceClaim 的 Port Watcher 機制讓多開時序上自然錯開，不會卡在固定 50051 |

---

## 七、建議執行順序

1. **任務 0.1、0.2**（決策前置，優先處理）
2. **Phase 1 全部任務**：1.1（已完成，無需動作）→ 1.2、1.3、1.4（風險低，可優先執行，償還既有技術債）
3. **Phase 2 不依賴任務 0.1 決策結果的部分**：2.2（刪除 `mcp_server.py`）→ 2.3（`port_finder.py`，但需先確認使用情境）→ 2.4（Port 回顯機制）
4. **SpaceClaim 多開可行性實測**（第六節後續建議第 1 項，建議在任務 2.1/2.5 動工前完成，避免排入開發排程後才發現 SpaceClaim 端無法真正多開）
5. **等待任務 0.1 決策底定後**：若決策為選項 B 或 C，執行 2.1（獨立伺服器入口或各產品改用獨立 `FastMCP` 實例）→ 2.5（`.mcp-workspaces/`，若選 B）；若決策為選項 A，此兩項大幅簡化或取消
6. **Phase 3**：3.1（`AnsSessionManager`，不依賴任務 0.1 決策結果，可與 Phase 2 平行）→ 3.3（MCP Resources，技術風險最低，可提前於 3.2 執行）→ 3.2（SpaceClaim 批次腳本，需先建基準測試，工作量較大）

任務 0.1、0.2 與 Phase 1 的 1.2–1.4 皆可立即開始，不互相阻塞；Phase 2 的 2.1、2.5 是整份計畫中唯一真正卡在決策點之後才能動工的項目，且 2.1/2.5 若涉及 SpaceClaim 多開，額外卡在第六節的實測結果。
