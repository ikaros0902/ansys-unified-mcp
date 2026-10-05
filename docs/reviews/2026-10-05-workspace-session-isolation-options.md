# 多工作區 Session 隔離架構方案對比（任務 2.1 / 2.5）

**狀態**：待決策，本文件不代表最終實作方向。
**查證基準**：本機已安裝 `fastmcp==3.4.5`（`.venv/Lib/site-packages/fastmcp/server/server.py:2124` 起 `FastMCP.mount()` 原始碼實測讀取，非轉述官方文件）。

---

## 一、既有事實基準（三方案共同依賴）

1. `core/sessions.py` 的 `SessionRegistry` 是 **process-wide singleton**，`(product, key)` 二元鍵、`threading.RLock()` 保護，session 物件本身是存活的 gRPC 連線物件，**不可序列化、不可跨進程共享**。
2. `shared.py` 的 `mcp = FastMCP(...)` 是**單一全域實例**，所有 `products/*/tools.py` 透過 `from ansys_unified_mcp.shared import mcp` 共用同一實例，用 `@aliased_tool` / `@mcp.tool()` 註冊。
3. `__main__.py` 的 `ANSYS_MCP_PROFILE` 是**編譯期 import 選擇**（決定哪些 `tools.py` 被 import），不是進程或實例分割。
4. 實測確認 `FastMCP.mount(server, namespace=None, as_proxy=None, tool_names=None, prefix=None)`：
   - 內部呼叫 `self.add_provider(FastMCPProvider(server), namespace=namespace or "")`，是**同進程、同記憶體空間**的即時轉發（非一次性複製，這點與 `import_server()` 不同，後者已標記 deprecated）。
   - 有 `namespace` 時子伺服器工具以 `{namespace}_{tool_name}` 形式出現；無 `namespace` 時維持原名，多個子伺服器依序嘗試比對。
   - `as_proxy`、`prefix` 參數已標記 deprecated，新程式碼不應使用。
5. `AnsSessionManager`（`connection/session_manager.py`）既有的 `connect(product, **kwargs)` 等四個入口已用 `**kwargs` 透傳而非強制統一簽名——這是計畫備註「任務 5 已踩過 kwargs 坑」的具體位置，代表 FastMCP 對工具函式簽名的自動 schema 推導對 `**kwargs` 型參數敏感，日後任何牽動 `@mcp.tool()` 裝飾目標的方案都要重新過一次這條既有相容性假設。
6. `.mcp-workspaces/` 目錄**完全不存在**，零雛形程式碼；全專案 `mount` 關鍵詞零匹配，代表 `mount()` 目前完全未被使用，三方案在這點上都是從零開始。

---

## 二、方案 A：SessionRegistry 加 workspace 維度（邏輯隔離，不動 FastMCP 實例）

### 核心機制
一句話：把 `SessionRegistry` 的鍵從 `(product, key)` 擴展為 `(workspace, product, key)`，隔離靠「鍵命名空間」而非進程或伺服器邊界。

### 實作路徑
- 改 `core/sessions.py`：`_sessions: Dict[str, Dict[str, Any]]` 加一層或把 key 改為複合字串（如 `f"{workspace}:{key}"`）。`get`/`put`/`drop`/`current_key` 等方法簽名增加 `workspace: str = "default"` 參數，預設值確保向後相容。
- 新增一個決定「當前 workspace」的機制：可能是環境變數（如 `ANSYS_MCP_WORKSPACE`）、或从 MCP 請求的 context/meta 帶入。這裡有個關鍵未查證點——**FastMCP 工具呼叫時能否取得「呼叫者所屬 workspace」這個資訊**，若答案是「否」，方案 A 需要額外設計一個 side-channel（例如每個 workspace 各自一個進程、用環境變數區分，但這樣又退化成方案 B 的部署形態）。
- `shared.py`、`__main__.py` 不需要動；各 `products/*/tools.py` 內呼叫 `registry.get/put` 的地方要補上 workspace 參數。

### 優點
- 改動集中在單一檔案（`sessions.py`）+ 呼叫端補參數，不碰 `FastMCP` 實例結構，風險面最小。
- 完全不受 `fastmcp==3.4.5` 版本行為影響（不依賴 `mount()`），版本升級無相容性負擔。
- 現有 `tests/test_sessions.py`、`test_mechanical_controller.py` 等測試只需加 workspace 參數的新測項，既有測項邏輯不必重寫。

### 缺點
- **並未解決 Token / Context 隔離的原始訴求**。方案 A 隔離的是「session 資料」，不是「工具清單」。同一個 MCP 連線仍會看到全部 138 個工具（因為工具註冊仍在同一個 `mcp` 實例、同一個 profile import 範圍），workspace 維度只影響「這個工具呼叫時操作的是哪個連線」，不影響「這個會話能看到哪些工具」。
- 若需求的本質是「不同工作區看到不同、較少的工具集合」（PHASE_2_AND_3_EXECUTION_PLAN.md 明確寫「約 10~15 個工具」），方案 A 單獨使用無法達成，必須疊加既有的 `ANSYS_MCP_PROFILE` 編譯期機制一起用（等於是「A + 現有 profile」的組合，而非 A 單獨）。
- Workspace 身分來源若落在環境變數層級，表示仍是「一個進程一個 workspace」，與現在 `ANSYS_MCP_PROFILE` 的運作模式沒有本質差異，只是多了一層 session 鍵命名空間，實際隔離效果有限。

### 風險與版本相依性
- 無 `fastmcp` 版本相依性（不碰 FastMCP API）。
- 風險在於「workspace 身分如何在工具呼叫時被正確識別」這個設計缺口尚未查證，若最終答案是只能靠進程/環境變數區分，方案 A 的「輕量」優勢會打折。

### 工量估計
- 改 `sessions.py` 核心邏輯：0.5 人日。
- 全專案呼叫端補 workspace 參數（`grep registry\.(get|put|drop)` 預估十餘處）：0.5~1 人日。
- 測試更新：0.5 人日。
- **合計約 1.5~2 人日**，前提是不含「workspace 身分識別機制」這個未決設計缺口的解法——若需另外設計這塊，工量會明顯增加且難以在此預估。

### 可測試性
- 純函式層級測試（`SessionRegistry` 新鍵結構）容易寫，`pytest` 可達 100% 覆蓋新增邏輯。
- 但「workspace 身分識別」若涉及 MCP 協定層的 context 傳遞，需要端到端測試驗證，測試複雜度不低。

---

## 三、方案 B：FastMCP.mount() 單進程多子伺服器（已確認可行機制）

### 核心機制
一句話：每個產品/工作區各自一個獨立 `FastMCP` 子實例，由頂層伺服器依工作區設定動態 `mount()` 對應子集合，子伺服器之間仍共享同一進程記憶體與 `SessionRegistry`。

### 實作路徑
- 新增 `src/ansys_unified_mcp/workspaces/`（或等效目錄），每個產品改為擁有自己的 `FastMCP` 實例，例如 `mechanical_mcp = FastMCP("mechanical")`，`products/mechanical/tools.py` 內 `@mcp.tool()` 改指向 `mechanical_mcp`（而非 `shared.mcp`）。
- `shared.py` 的全域 `mcp` 轉為「頂層聚合器」角色，新增邏輯依工作區設定（例如讀取 `.mcp-workspaces/<name>/.mcp.json` 的某個欄位，或由啟動參數決定）呼叫 `mcp.mount(mechanical_mcp, namespace=None)` 等。
- `aliased_tool` 裝飾器需要能接受「目標 mcp 實例從全域 `mcp` 換成各產品自己的子實例」，目前 `aliased_tool` 已支援 `target_mcp` 參數透傳（讀碼確認 `aliased_tool(mcp_instance, ...)` 第一參數可傳 `FastMCP` 實例），這部分**機械可控**，但需要逐個 `products/*/tools.py` 檢查目前是否全部用隱式全域 `mcp` 還是已傳參數。
- `.mcp-workspaces/mechanical/.mcp.json` 等檔案需要新建（目前完全不存在），需定義其 schema（例如載哪個 workspace key）。
- 需新增一個「依設定決定掛載哪些子伺服器」的啟動邏輯，可能取代或疊加現有 `__main__.py` 的 `ANSYS_MCP_PROFILE` 判斷。

### 優點
- `mount()` 本身是本機已驗證可用的 API（非理論可行性），同進程特性讓 `SessionRegistry` 完全不受影響，不需要額外設計跨進程通訊層。
- 真正能做到「不同工作區只看到對應產品的工具清單」（`list_tools()` 結果因 mount 範圍而異），直接命中計畫文件「約 10~15 個工具」的訴求，比方案 A 更貼近原始目的。
- 改動屬於「機械且逐產品可分批進行」，不是一次性大重構，可以先在一個產品（如 Mechanical）上做 PoC 驗證再推廣。

### 缺點
- 仍是單進程單一部署單元——若使用者或計畫文件的「獨立工作區」隱含「作業系統層級故障隔離」（例如一個產品的工具呼叫把進程搞崩，不影響其他產品），方案 B 不滿足，因為所有子伺服器仍在同一個 Python 進程裡。
- `mount()` 的 `tool_names` 參數與現有 `aliased_tool` 的別名機制（`ALIAS_REGISTRY`/`CANONICAL_TO_ALIASES`）功能有重疊但不是同一套邏輯，兩者疊加使用時命名解析順序需要仔細設計並寫測試覆蓋，否則容易出現「同一個工具透過不同路徑被重複註冊」或「別名解析在 mount 命名空間下失效」的邊界問題。
- `shared.py` 目前對 `mcp.list_tools`、`mcp.call_tool`、`mcp.get_tool` 做了 monkey-patch（`_wrapped_list_tools` 等），這些包裝函式目前只包著單一全域 `mcp` 實例；若改為多實例架構，需要確認這些包裝邏輯要套用在頂層聚合器還是每個子實例，目前程式碼未處理這個情境，是方案 B 必須額外設計的部分。
- 任務 2.1/2.5 要求的「`.mcp.json` 只掛載對應子伺服器」的 schema 與讀取邏輯需要全新設計（計畫文件本身承認「未附帶任何原型程式碼」）。

### 風險與版本相依性
- `mount()` 簽名在 `fastmcp==3.4.5` 已確認存在且無 deprecated 警告（`namespace`/`tool_names` 是現行用法，`as_proxy`/`prefix` 才是 deprecated，不應使用後兩者）。
- `pyproject.toml` 未釘選 `fastmcp` 精確版本（僅聲明相依但未見版本區間，需確認），若未來 `fastmcp` 升級版本變更 `mount()` 行為（例如 namespace 命名規則調整），此方案的耦合面比方案 A 大，升級時需要重新驗證。
- `aliased_tool` 與 `mount()` 的 kwargs 透傳疊加是新組合，沒有既有測試覆蓋，是本方案最大的未知風險面，呼應計畫備註中「任務 5 已踩過 kwargs 坑」的提醒——`@mcp.tool()` 對函式簽名的 schema 推導若遇到 `**kwargs` 型參數會有已知問題，`mount()` 的 `tool_names` 重新命名機制是否會放大這個問題需要實測。

### 工量估計
- PoC（單一產品如 Mechanical 改用獨立子實例 + mount 回頂層）：1~1.5 人日。
- 全部 5 個產品（mechanical/geometry/fluent/workbench/optislang）逐一改造 + `shared.py` monkey-patch 邏輯重新設計：3~4 人日。
- `.mcp-workspaces/*/.mcp.json` schema 設計與讀取邏輯：1 人日。
- 測試（含 mount 命名空間 + alias 疊加的邊界測試）：1.5~2 人日。
- **合計約 6.5~8.5 人日**。

### 可測試性
- `mount()` 後的 `list_tools()` 結果可直接用 `pytest` 斷言工具數量與命名空間前綴，客觀可驗證。
- `aliased_tool` 疊加 `mount()` 的邊界案例需要新寫測試（現有 `test_aliased_tools.py` 需擴充），覆蓋率可達成但需要額外設計測項。

---

## 四、方案 C：進程級實體隔離 + 檔案系統登錄表（折衷／對標官方生態路線）

### 核心機制
一句話：每個工作區各自獨立 Python 進程（各自獨立 `FastMCP` 實例與獨立 `SessionRegistry`），跨工作區的連線中繼資料透過既有 `workbench_queue/registry/` 檔案系統登錄表同步，但 session 物件本身不跨進程共享。

### 實作路徑
- 新增 `servers/mechanical_server.py`、`servers/geometry_server.py`、`servers/fluent_server.py`、`servers/workbench_server.py`、`servers/optislang_server.py`（計畫文件已點名的檔案，目前零實作），每個檔案各自 `FastMCP(...)` + 僅 import 對應 `products/<name>/tools.py`。
- `core/sessions.py` 的 `SessionRegistry` 不需改動核心邏輯（每個新進程啟動後各自產生一份全新 instance，天然隔離），但需要新增「寫入檔案系統登錄表」的 hook：在 `put()`/`drop()` 時額外同步一筆中繼資料（port、PID、product、workspace 名稱）到 `workbench_queue/registry/`（此目錄與既有 `bridges/connection_manager.py` 的 `get_registered_instances()` 已有的機制同源，可擴充而非新建）。
- 跨工作區查詢（例如「我同時連了 Mechanical 和 SpaceClaim，想一次查兩者狀態」）需改為讀取檔案系統登錄表而非記憶體物件，`connection_tools.py` 的既有狀態查詢工具需要擴充邏輯來源。
- `.mcp-workspaces/<name>/.mcp.json` 的作用從「掛載設定」變成「啟動哪個 `servers/*.py` 進程」的設定。

### 優點
- 唯一能提供作業系統層級故障隔離與安全邊界的方案——一個產品的工具呼叫使進程崩潰，不影響其他工作區，真正符合「獨立 MCP Server 生態」的對外形象。
- `SessionRegistry` 核心程式碼完全不需改動（每進程各自一份全新 instance 本來就滿足隔離），改動集中在新增登錄表同步 hook 與新建 `servers/*.py` 入口。
- 不依賴 `fastmcp` 的 `mount()` 行為，版本升級風險與方案 A 相同，是三者中最低。

### 缺點
- **跨進程即時 session 可見性完全犧牲**：登錄表只能同步「連線中繼資料」（port/PID/product），無法讓另一個進程直接取得 session 物件去執行腳本。若使用者想從 Geometry workspace 操作 Mechanical，必須切換到 Mechanical workspace 重新連線，使用體驗比現狀倒退。
- 既有測試中假設單一全域 `registry` 的部分（如 `test_sessions.py`）需要重新評估「單進程單元測試」與「多進程整合測試」的分界，整合測試的建置成本高於方案 A/B。
- 需要新設計並驗證「登錄表寫入時機」（連線建立/中斷時）與「讀取時過期資料清理」的競態條件（既有 `connection_manager.py` 的 `get_registered_instances()` 已有「清理過期實例」邏輯，可參考但仍需為新的 workspace 維度擴充並測試並行寫入安全性）。
- 工作量明顯高於方案 A，且高於方案 B 的核心改動部分（但方案 B 的「全產品改造+mount疊加測試」工量其實與方案 C 接近，需實際比較時留意兩者總工量差距可能沒有想像中大）。

### 風險與版本相依性
- 無 `fastmcp` 版本相依性風險（不使用 `mount()`，每個進程各自建立標準 `FastMCP` 實例，是當前程式碼已驗證過的用法）。
- 風險集中在「新設計的跨進程登錄表同步協議」本身，這是全新程式碼、無既有測試覆蓋，需要從零寫測試並處理並行寫入/讀取競態。

### 工量估計
- `servers/*.py` 5 個入口腳本（可參考現有 `__main__.py` 的 profile 判斷邏輯简化而來）：1.5 人日。
- `SessionRegistry` 登錄表同步 hook（擴充 `connection_manager.py` 既有機制）：1.5~2 人日。
- `connection_tools.py` 跨工作區查詢邏輯改為讀登錄表：1 人日。
- `.mcp-workspaces/*/.mcp.json` schema 設計：0.5 人日。
- 測試（含並行寫入競態、跨進程整合測試）：2~3 人日。
- **合計約 6.5~8 人日**。

### 可測試性
- 單進程內邏輯（`servers/*.py` 啟動、工具 import 範圍）容易用既有 `test_profiles_verification.py` 模式驗證。
- 跨進程整合測試（驗證登錄表同步正確性）需要用 subprocess 啟動多個真實進程做端到端測試，比方案 A/B 的測試建置成本更高，但 `test_m1_import_permutation_stress.py` 已有 `_run_in_fresh_process` 這類既有 fixture 可參考複用。

---

## 五、三方案對比摘要表

| 比較項目 | 方案 A（SessionRegistry 加 workspace 鍵） | 方案 B（FastMCP.mount 單進程） | 方案 C（多進程 + 登錄表） |
| --- | --- | --- | --- |
| 是否解決「工具清單依工作區縮減」原始訴求 | ❌ 不解決（需疊加現有 profile 機制） | ✅ 解決 | ✅ 解決 |
| 跨工作區 session 即時可見性 | 保留 | 保留 | 犧牲（降級為登錄表中繼資料） |
| 作業系統層級故障/安全隔離 | 無 | 無 | 有 |
| `fastmcp` 版本相依性風險 | 無 | 中（依賴 `mount()` 行為穩定性 + alias 疊加未測試） | 無 |
| 新增程式碼量 | 最低 | 中高 | 高 |
| 工量估計 | 約 1.5~2 人日 | 約 6.5~8.5 人日 | 約 6.5~8 人日 |
| 現有測試相容性 | 高（補參數即可） | 中（alias+mount 疊加需新測項） | 中（需新建跨進程整合測試） |
| 使用體驗（跨產品切換） | 不受影響 | 不受影響 | 明顯變複雜 |
| 對標官方「獨立 MCP Server 生態」 | 不滿足 | 不滿足（仍單一部署單元） | 滿足 |

---

## 六、工程建議（最終決策權在使用者）

若 Phase 2 的真正目的是「降低單次會話 Context 占用、依工作區限制工具可見範圍」而非「對外提供作業系統層級獨立部署的 MCP Server 生態」，方案 B 在同等達成「工具清單隔離」目標的前提下，不犧牲現有跨產品 session 共享能力，改動雖多於方案 A 但機械可控、可逐產品分批驗證；方案 A 單獨使用無法滿足計畫文件明示的工具數量縮減訴求，若要用方案 A 達成目的，實質是「方案 A + 現有 ANSYS_MCP_PROFILE」的組合而非方案 A 單獨成立。方案 C 是唯一能滿足「真正獨立進程」字面需求的路徑，但代價是跨工作區即時協作能力倒退，且工量與方案 B 相近——若這個犧牲不是當前的硬性需求，方案 C 的額外複雜度缺乏對應的收益。

**最終決策權在使用者**：三方案的技術事實與工量已盡量基於現有程式碼與本機實測的 `mount()` 行為陳述，但「是否需要作業系統層級隔離」「是否接受跨工作區協作能力降級」屬於產品方向判斷，不在本報告代為決定的範圍。

## 七、決策前仍待確認的事項

1. 方案 A 提到的「FastMCP 工具呼叫時能否取得呼叫者所屬 workspace」目前無法由程式碼內部查證得知，需要查閱 MCP 協定規格或 FastMCP context 傳遞機制的進一步實測，三方案中只有這一點若選定方案 A 會成為前置阻塞項。
2. 方案 B 的 `aliased_tool` 與 `mount()` 疊加行為、方案 C 的登錄表並行寫入競態，皆為全新組合，目前均無實測或既有測試覆蓋，無論選哪個方案都需要在實作前先建立最小 PoC 驗證，而非直接大範圍改動。
3. **已查證**：`pyproject.toml` 第 12 行僅宣告 `"fastmcp"`，**未釘選任何版本區間**。這代表環境重新安裝依賴時可能取得與本機實測不同的 `fastmcp` 版本，本報告對 `mount()` 行為的所有結論僅對當前已安裝的 `3.4.5` 成立。若推進方案 B，建議先補上版本釘選（如 `fastmcp==3.4.5` 或至少 `>=3.4.5,<3.5`）以避免未來環境重建時行為漂移。

---

## 八、審查段（opus-5）獨立實測補充——規劃段三方案之外的關鍵發現

> 本節為 workflow 審查段以 `fastmcp==3.4.5` 親自 PoC 實測後補入，推翻規劃段兩項前提並新增方案 D。決策前務必優先閱讀本節。

### 8.1 規劃段根因定位錯誤（已實測否證）

規劃段假設「工具過多源於產品模組全載入」。實測各 profile 工具數：

```
profile=geometry  -> TOTAL 72  MECH 42  GEO 13
profile=fluent    -> TOTAL 78  MECH 42  GEO  0
profile=optislang -> TOTAL 64  MECH 42  GEO  0
profile=all 143 / mechanical 61
```

真因：`__main__.py` 無條件 import `tools/intent_tools.py` → `from ansys_unified_mcp.workflows import ...` → **連帶載入 `products/mechanical/tools.py`**，使 42 個 Mechanical 工具在**每個** profile 都出現。現有 profile 閘門對 Mechanical 完全失效。

**最高槓桿修正**：切斷 `intent_tools → workflows → mechanical.tools` 的 transitive import，即可讓 geometry profile 由 72 降至 30（數小時工量 vs 方案 B 的 6.5~8.5 人日）。這是任何工具縮減方案的前置。

連帶推翻方案 B 賣點：`mechanical` profile 的 61 個工具中 59 個來自無條件載入的核心，**拆產品子伺服器到不了「10~15 工具」的宣稱目標**。

### 8.2 方案 A「前置阻塞項」不成立（規劃段查證不足）

規劃段第七節稱方案 A 的 workspace 身分識別「無法由程式碼內部查證得知」。實為查證不足：FastMCP 的 `Context` 已提供 `session_id`、`client_id`、`list_roots()`（MCP roots 正是客戶端宣告工作區目錄的標準機制），皆存在於已安裝套件。**方案 A 無前置阻塞項。**

### 8.3 方案 D（規劃段遺漏，審查段實測可行，成本低一個量級）

FastMCP 3.4.5 內建 **per-session 工具可見性** API：`ctx.disable_components / enable_components / reset_visibility`，附 `ToolListChangedNotification`。單一全域實例即可做到真隔離（實測：S1 工具 5→3、S2 仍 5、S1 recheck 維持 3，互不干擾）。

搭配 `on_list_tools` middleware + client roots 實測達成零操作隔離：

```
roots=.../mechanical -> ['mechanical_connect','mechanical_run_script']
roots=.../geometry   -> ['geometry_launch']
無 roots             -> 全部（優雅降級）
```

**不動 `@mcp.tool()` 註冊目標、不動 SessionRegistry、無子伺服器、無多進程。** 這是「工具清單隔離」的正解。

### 8.4 方案 B 新增已知缺陷（審查段重現，非風險而是確定缺陷）

`namespace` 掛載破壞別名執行期解析：`ALIAS_REGISTRY` 存裸名、`mount` 後實際工具名帶 namespace 前綴，`_wrapped_call_tool` 解析後拋 `NotFoundError: Unknown tool`。方案 B 若採用須限定 `namespace=None`。

### 8.5 審查段獨立評分與建議路徑

| 方案 | 可行性 | 複雜度(低者佳) | 契合度 | 定位 |
| --- | --- | --- | --- | --- |
| A | 9 | 9（1.5~2 人日） | 9 | session 鍵隔離正解，但不負責工具縮減 |
| B | 6 | 3（6.5~8.5 人日） | 5 | 到不了 10~15、namespace 破壞別名、與 monkey-patch 衝突，不建議 |
| C | 8 | 2（6.5~8 人日） | 4 | 僅當「作業系統級隔離」為硬需求才選 |
| **D** | **9** | **8** | **9** | **工具可見性隔離正解** |

**建議路徑**：
1. 先修 `intent_tools → workflows → mechanical.tools` transitive import（最高槓桿，數小時）。
2. **方案 D（工具可見性）+ 方案 A（session 鍵隔離）互補組合**，合計遠低於 B/C 單獨成本。
3. 僅在確認需要作業系統級隔離時才上方案 C。
