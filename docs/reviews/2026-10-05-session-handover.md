# 2026-10-05 工作交接記錄（供次日新 session 接續）

**基線起點**：commit `b6dedd1`
**本日最終**：commit `cf0489a`（三邊同步：本機 / GitHub `ansys-unified-mcp` / GitLab `ansys-mcp`）
**驗收標準**：基線非全綠（pytest 既有 1 failed、ruff 78 errors），全程以「不惡化既有紅燈」為準，非「全綠」。

---

## 一、今日完成的任務（8 項任務中 7 項完成並推送）

| # | 任務 | commit | 狀態 |
| --- | --- | --- | --- |
| 0 | 補完 geometry/named-selections MCP resource + driver 測試 | `5b43dd3` | ✅ |
| 1 | 刪除 products/ 下 4 個被同名套件遮蔽的扁平死碼檔 | `0fcb7b9` | ✅ |
| 2 | 刪除失效的 src/__init__.py 殘骸 | `d8cd691` | ✅ |
| 3 | 5 個測試檔斷言從 tools/ 三檔遷移到 products/*/tools.py 正本 | `1e97a3a` | ✅ |
| 4 | 刪除 tools/ 三檔（mechanical_tools/workbench_tools/mechanical_workflow_tools） | `1e97a3a` | ✅ |
| 5 | 接線 AnsSessionManager 為 4 個 ans_session_* MCP 工具 | `6812b1a` | ✅ |
| 6 | 修補 test_envelope_contract 守門缺陷（掃描範圍擴及 products 正本） | `1e97a3a` | ✅ |
| 8 | SpaceClaim 幾何批次執行器 batch_executor + 整合測試（真實環境驗收） | `cf0489a` | ✅ |
| 7 | 多工作區 session 隔離 | — | ⏸ 待使用者決策（見第四節） |

**當前測試基線**：`1 failed / 543 passed / 2 deselected / 5 xfailed / 1 xpassed`
唯一紅燈 `test_tool_count_136_ast_verification`（AST 工具計數 143≠138），既有債、非今日引入，所有任務均確認不觸發新 failure。

---

## 二、架構現況（清理後）

活架構路徑（四層單向依賴，清理後乾淨）：
```
__main__.py → shared.mcp（單一 FastMCP 實例）
  → profile 動態載入 products/<name>/tools.py（薄包裝 @mcp.tool / @mcp.resource）
  → products/<name>/facade.py（持有 session 的 controller）
  → drivers/sim_impl.py（Fluent/Geometry gRPC 實作）+ core/sessions.py（SessionRegistry 多實例）
  → bridges/connection_manager.py（進程/埠探測）
```

今日清理成果：
- products/ 下新舊並存的死碼（4 個扁平 .py）已刪
- tools/ 下 3 個重複死碼已刪，測試斷言遷移至 products 正本
- src/__init__.py 語意污染殘骸已刪
- AnsSessionManager 從「建好零引用」接線為實際生效的 4 個 MCP 工具
- 信封門禁（test_envelope_contract）掃描範圍從只掃 tools/ 擴到涵蓋 products 正本 126 工具

新增能力：
- 4 個 MCP Resources：ansys://mechanical/model-tree、materials、geometry/model-tree、named-selections（全到位）
- 4 個 ans_session_* 統一跨產品 session 工具
- geometry 批次執行器 execute_batch（已真實環境驗收，但尚無 @mcp.tool 入口，見第三節待決）

---

## 三、兩個待使用者決策的收尾點

### 3.1 batch_executor 工具層入口（任務 8 衍生）
`products/geometry/batch_executor.py` 的 `execute_batch` 已實作並通過真實 SpaceClaim 驗收，但**尚未掛 @mcp.tool**，AI agent 目前無法直接呼叫。掛工具會讓 AST 工具計數 +1，牽涉既有紅燈 `test_tool_count_136_ast_verification`（已 143≠138）是否同步更新為正確值。
**待決**：是否掛工具入口 + 是否順手修正該紅燈的期望值。

### 3.2 既有紅燈 test_tool_count_136_ast_verification
期望值硬編碼 138，實際 143。此為硬編碼守門測試，每次新增工具都會製造假紅燈，掩蓋真實回歸訊號。
**建議**：改為動態比對或更新期望值為 143，獨立成一次提交。

---

## 四、任務 7：多工作區 session 隔離——方案對比與建議（待拍板）

完整方案見 `docs/reviews/2026-10-05-workspace-session-isolation-options.md`（第八節為審查段實測補充，務必優先讀）。摘要：

| 方案 | 機制 | 可行性/複雜度/契合 | 工量 |
| --- | --- | --- | --- |
| A 輕量 | SessionRegistry 鍵加 workspace 維度 | 9/9/9 | 1.5~2 人日 |
| B 重 | FastMCP.mount() 每工作區掛子 server | 6/3/5 | 6.5~8.5 人日 |
| C 折衷 | 多進程 + 檔案系統登錄表 | 8/2/4 | 6.5~8 人日 |
| **D（審查段發現）** | fastmcp per-session 工具可見性 + roots middleware | 9/8/9 | 低一個量級 |

**審查段（opus-5）實測結論**（推翻規劃段）：
1. 工具過多的真因是 `intent_tools → workflows → mechanical.tools` 的 transitive import 讓 42 個 Mechanical 工具在每個 profile 都載入，**先修這個是最高槓桿**（數小時，geometry profile 72→30）。
2. 方案 B 的 `mount` namespace 會破壞 ALIAS_REGISTRY 別名解析，且到不了「10~15 工具」目標。
3. 方案 D 用 fastmcp 內建 per-session 可見性，不動註冊目標、不動 SessionRegistry、無多進程，實測可行。

**審查段建議路徑**：先修 transitive import → 方案 D（工具可見性）+ 方案 A（session 鍵隔離）互補 → 僅在需要 OS 級隔離才上 C。

**最終決策權在使用者**：是否需要「作業系統層級隔離」是產品方向判斷。若只是要降低 context 占用，D+A 組合成本遠低於 B/C。

---

## 五、明日接續的建議起點

1. 使用者先針對第三節兩個待決點與第四節方案 7 給出決策。
2. 若採審查段建議：先做「切斷 intent_tools transitive import」PoC（最高槓桿、數小時可驗），再評估 D+A。
3. 推進任務 7 前補 pyproject.toml 的 fastmcp 版本釘選（目前未釘選，mount/可見性行為僅對 3.4.5 保證）。

---

## 六、環境與操作註記

- 專案根 `D:\Ikaros\ANSYS-unified-MCP`，Python 3.14 於 `.venv`，pytest 全量約 2.5~3.5 分鐘。
- 整合測試需真實 SpaceClaim（gRPC 50051），預設被 `addopts = "-m 'not integration'"` 排除，加 `-m integration` 才跑。
- 兩個遠端：`origin`（push 設雙 URL：GitHub + GitLab）。push 後以 `git ls-remote` 比對三邊 SHA 確認同步。
