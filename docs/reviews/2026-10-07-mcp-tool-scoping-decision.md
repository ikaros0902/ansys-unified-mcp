# 2026-10-07 MCP 工具收斂評估與決策結論

針對「MCP 工具數量是否需要收斂」的評估結論。對應產出：`docs/deployment/MCP_TOOL_SCOPING_GUIDE.md`（操作指引）
與 `mcp_config.json` 設 `ANSYS_MCP_PROFILE=all`（本機設定，不入版控）。

---

## 一、現況量測

`profile=all` 下註冊工具總數 **155 個**（以 `mcp.list_tools()` 實測）。依產品域粗分：

| 域 | 約數 |
| --- | --- |
| mechanical | 42 |
| workbench | 28 |
| fluent | 22 |
| geometry | 20 |
| 通用（連線/文件/job/session） | 20 |
| optislang / dpf / dyna | 13 |
| workflow | 5 |

---

## 二、根因：不是架構問題，是設定未帶 profile

`mcp_config.json` 的 `env` 原本只設 `PYTHONUTF8`，未設 `ANSYS_MCP_PROFILE`，
而 `__main__.py` 預設值為 `all`，故 AI 客戶端一次面對全部 155 工具。
這是設定問題，零成本可解，非需要重構的架構缺陷。

---

## 三、決策：不做大規模工具合併

評估後判定**不需要**把細顆粒度工具（如 mechanical 的 15 個 `add_*`）合併成參數化大工具：

1. 真正的痛點（context 被無關工具灌爆）已由既有兩層機制解決：啟動期 profile 路由 +
   執行期 workspace 可見性（任務 7 方案 D+A 的成果）。
2. FastMCP 扁平細工具對 AI 友善（工具名自我描述、schema 單純）；合併成參數化大工具
   反而增加單一 schema 複雜度。
3. 合併是高成本重構（動 42 個 mechanical 工具 + 測試改寫），無實測痛點不符 Lazy Senior 原則。

---

## 四、Profile 部署選項對比與選定

| 選項 | 機制 | 跨域狀態共享 | 選定 |
| --- | --- | --- | --- |
| 1 固定單一 profile | 一進程一 profile，換域重啟 | 單域 | 否（跨領域需求排除） |
| 2 多 server 條目 | 每域一進程 | ✗ 進程隔離、SessionRegistry 不共用 | 否 |
| 3 all + workspace 收斂 | 單進程全載，執行期 `ans_session_set_workspace` 收斂 | ✅ 同進程共享 | **是** |

**選 3 的決定性理由**：使用者的目標工作流為「SpaceClaim 調幾何 → Mechanical 調環境 →
optiSLang 最佳化」。optiSLang 最佳化迴圈需驅動 geometry/mechanical 重算並回收結果，
三產品的連線狀態必須在同一進程內共享。選項 2 的多進程會切斷此共享，使最佳化迴圈無法串接。
此結論印證任務 7 當初選 D+A（in-process）而非方案 C（OS 級多進程隔離）的判斷。

---

## 五、附帶澄清：ACT close-loop 開發的重啟需求

skill SOP 腳本在固化成專屬 MCP 工具前，用通用 runner（`*_run_script` / `*_script_live`）
當試驗台反覆驗證——此屬「送腳本字串」範疇，**零重啟**。只有把穩定腳本固化成新 MCP 工具
那一刻才重啟一次。詳見 `docs/deployment/MCP_TOOL_SCOPING_GUIDE.md` 第四節重啟對照表。
