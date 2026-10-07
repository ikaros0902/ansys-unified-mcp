# MCP 工具收斂指引：Profile 與 Workspace

本文說明如何控制 AI 單次 session 面對的 MCP 工具數量。全量工具約 155 個（`profile=all`），
透過兩層機制收斂實際曝露：**啟動期 profile 路由** 與 **執行期 workspace 可見性**。

---

## 一、兩層收斂機制

| 層級 | 機制 | 作用時機 | 效果 |
| --- | --- | --- | --- |
| 啟動期 | `ANSYS_MCP_PROFILE` 環境變數 | server 啟動時決定 import 哪些 `products/*/tools.py` | 進程級，一個進程一個 profile |
| 執行期 | `ans_session_set_workspace(products=[...])` | 連線後動態呼叫 | per-session，不重啟、不斷線、不影響他人 |

合法 profile 值：`all` / `mechanical`（`structural`）/ `geometry`（`spaceclaim`）/
`fluent`（`cfd`）/ `workbench`（`wb`）/ `optislang` / `dyna`（`lsdyna`）。
mechanical profile 會連帶載入 dpf。

合法 workspace products：`mechanical` / `fluent` / `geometry` / `workbench` /
`optislang` / `dpf` / `workflow`。跨域通用工具（文件檢索、session 管理、作業監看）恆可見，不受收斂影響。

---

## 二、目前設定：profile=all + 執行期 workspace 收斂

`mcp_config.json` 設 `ANSYS_MCP_PROFILE=all`，單一進程載入全部產品、session 跨域共享。
適用於需要跨產品串接狀態的工作流（如幾何→結構→最佳化迴圈），再靠 workspace 收斂單次 session 的可見工具。

> 選此而非「多 server 分 profile」的理由：跨產品最佳化迴圈（optiSLang 驅動 geometry/mechanical
> 重算）需要三個產品的連線狀態在同一進程內共享，多進程隔離會切斷此共享。

---

## 三、最佳化流程的 workspace 收斂範例

以「SpaceClaim 調幾何 → Mechanical 調環境 → optiSLang 最佳化」為例：

```python
# 階段一：幾何參數化（只看 geometry ~20 工具）
ans_session_set_workspace(products=["geometry"])
# 用 execute_spaceclaim_script_live 迭代幾何腳本（改腳本不需重啟 server）

# 階段二：環境/邊界設定（mechanical + 結果提取）
ans_session_set_workspace(products=["mechanical", "dpf"])
# 用 mechanical_run_script 驗證 SOP 腳本

# 階段三：最佳化迴圈（跨三域 + 高階 workflow 工具）
ans_session_set_workspace(products=["geometry", "mechanical", "optislang", "workflow"])
# optiSLang 可跨域驅動 geometry/mechanical 重算，底層 session 全共享

# 清除限制，回到全集 155
ans_session_set_workspace(products=[])
```

---

## 四、重啟需求對照

| 改動內容 | 需要重啟 server？ |
| --- | --- |
| ACT / journal 腳本字串（透過 `*_run_script` / `*_script_live` 送入 ANSYS） | 否。改腳本=改參數，再呼叫一次即可 |
| MCP 工具的 Python code（新增/刪除工具、改簽名、改邏輯、改 docstring） | 是。import-time 載入，須重啟進程 |
| `.env` / `mcp_config.json` / `ANSYS_MCP_PROFILE` | 是。啟動期讀取 |
| 切換 workspace（`ans_session_set_workspace`） | 否。執行期行為，不斷 ANSYS 連線 |

> close-loop 腳本驗證（skill SOP 的腳本在固化成專屬工具前，用通用 runner 當試驗台反覆驗證）
> 屬「腳本字串」範疇，零重啟。只有把穩定腳本固化成新 MCP 工具那一刻才重啟一次。
> 開發階段若需頻繁重啟，可在終端直接跑 `python -m ansys_unified_mcp`（Ctrl+C 重跑數秒），
> 不必重啟整個 AI 客戶端。

> 重啟 server 會清掉 SessionRegistry 的 ANSYS 連線（gRPC session），但 ANSYS 軟體視窗不受影響，
> 重啟後重新 connect 即可。
