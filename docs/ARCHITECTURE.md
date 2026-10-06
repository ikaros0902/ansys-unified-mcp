# ARCHITECTURE — 分層職責與程式慣例

> 本檔定義 `ansys-unified-mcp` 的**分層職責**與**程式慣例**（命名、回傳信封），是維護與擴充時的準則。
> 專案全貌與心智模型見 `agents/contexts/context.md`；本檔聚焦「怎麼寫才一致」。
> 註：部分現況尚未符合下列慣例（已於各節標出「現況偏差」），這些是漸進收斂的目標，不是要求你一次改完。

## 1. 分層職責

| 層 | 位置 | 該做什麼 | 不該做什麼 |
|---|---|---|---|
| 工具層 | `tools/*.py` | 定義 `@mcp.tool()`；檢查連線、組腳本字串、委派給控制器；包裝回傳信封 | 不放連線/session 的實作細節、不直接管理程序 |
| 產品控制器 | `products/<product>/facade.py` | 每個產品的 connect / launch / run_script / disconnect 邏輯；透過 `SessionRegistry` 管 session | 不定義 `@mcp.tool()`、不做路徑偵測 |
| 驅動 / 橋接 | `drivers/*.py`、`bridges/*.py` | 特定執行機制的實作（如 Fluent 的 PyFluent 驅動、Workbench 的檔案 IPC bridge） | 不定義 `@mcp.tool()` |
| 核心 | `core/sessions.py`、`core/paths.py` | 全域 session 登錄、ANSYS 路徑統一解析 | 不綁定任一產品的業務邏輯 |
| 設定 / 連線 | `config.py`、`connection_manager.py` | ANSYS 安裝偵測、掃 port/進程 | 不做業務邏輯 |
| 文件檢索 | `docs/*.py` | 清洗、分塊、FTS5 索引與查詢 | 與 ANSYS 執行無關，保持獨立 |

**目標形態**：每個產品應為 `products/<product>/` 下 `facade.py`（控制器）+ `tools.py`（工具）+ `driver.py`（執行機制，若需要）**成組出現**，控制器一律用 `SessionRegistry` 管 session。

現況（已收斂）：所有產品皆已採 `products/<product>/` 分層：`geometry`、`mechanical`、`fluent`、`optislang`、`workbench`、`dpf`、`dyna`（本輪新增）。原先散落於 `drivers/sim_impl.py` 的 geometry/fluent `call_tool` 分派實作已拆分歸位至
`products/geometry/call_dispatch.py` 與 `products/fluent/call_dispatch.py`；
`drivers/` 現僅保留與 session/產品無關的共用執行機制殘留
（`lsdyna_driver.py`、`icepak_driver.py`、`base.py`、`contour_helper.py`，
以及部分產品尚未遷移的薄殼轉接 `*_driver.py`）。

目前目錄樹（`src/ansys_unified_mcp/`）：

```
products/
├── geometry/
│   ├── facade.py             # GeometryController（session 管理，走 SessionRegistry）
│   ├── tools.py               # @mcp.tool() 工具層，委派 call_dispatch
│   ├── driver.py               # SpaceClaimDriver（批次 job 驅動，供 workflows/ 用）
│   ├── call_dispatch.py        # geometry_* call_tool 分派與幾何輔助函式（原 sim_impl.py 拆出）
│   ├── batch_executor.py       # 批次聚合多個 geometry 操作
│   └── spaceclaim_scripts/     # SpaceClaim 伺服器端 IronPython 腳本（.ironpy，全英文）
├── mechanical/
│   ├── facade.py / tools.py / driver.py / api.py / plugins/
├── fluent/
│   ├── facade.py              # FluentController
│   ├── tools.py                # @mcp.tool() 工具層，委派 call_dispatch
│   ├── driver.py                # FluentDriver（批次 job 驅動）
│   └── call_dispatch.py         # fluent_* call_tool 分派（原 sim_impl.py 拆出）
├── optislang/
│   ├── facade.py / tools.py / driver.py
├── workbench/
│   ├── facade.py / tools.py / scripts/
├── dpf/
│   ├── facade.py / tools.py
└── dyna/                       # 本輪新增產品
    ├── facade.py / tools.py

drivers/                        # 僅剩與特定產品 session 無關的共用執行機制
├── base.py                     # BaseSolverDriver 抽象基底
├── contour_helper.py           # 白底雲圖產生共用輔助
├── lsdyna_driver.py             # LSDynaDriver（批次 job 驅動）
├── icepak_driver.py             # IcepakDriver（批次 job 驅動）
└── mechanical_driver.py / fluent_driver.py / optislang_driver.py / spaceclaim_driver.py
    （薄殼轉接，實體已搬至對應 products/<product>/driver.py）
```

## 2. 工具命名慣例

**目標規則**：`<product>_<verb>_<object>`，全小寫 snake_case，動詞用祈使式（`connect`/`launch`/`add`/`get`/`list`/`set`/`run`/`disconnect`）。

- product 前綴用固定字彙：`mechanical` / `workbench` / `fluent` / `optislang` / `geometry`(SpaceClaim) / `lsprepost` / `docs`。
- 不加冗餘後綴（如 `_tool`）。
- 診斷類統一 `<product>_check_connection`。

現況偏差（收斂目標，勿一次全改）：

| 產品 | 現況 | 是否符合 |
|---|---|---|
| Fluent（`products/fluent/tools.py`） | `fluent_launch` / `fluent_set_solver`… | ✓ 前綴一致 |
| Geometry/SpaceClaim（`products/geometry/tools.py`） | `geometry_launch` / `geometry_create_block`… | ✓ 前綴一致 |
| Mechanical（`products/mechanical/tools.py`） | `list_instances` / `connect_to_mechanical` / `add_force` / `solve_analysis`… | ✗ 多數**無 product 前綴** |
| Workbench（`products/workbench/tools.py`） | `workbench_run_journal_tool`… | △ 有前綴，但帶冗餘 `_tool` 後綴 |
| optiSLang（`products/optislang/tools.py`） | `connect_optislang` / `optislang_version` / `run_optislang_script`… | ✗ 前綴/後綴**混用** |

> 維護含意：**新增**工具一律照目標規則命名；**既有**工具改名屬對外介面變更（AI client 會看到名稱），需審慎並成批進行，非本輪低風險範圍。

## 3. 回傳信封慣例

**規則**：所有 `@mcp.tool()` 回傳 **dict**（非 JSON 字串），統一用 `shared.as_envelope(...)` 正規化，內容為扁平信封：

- 成功：`{"ok": True, ...其他欄位}`
- 失敗：`{"ok": False, "error": "可讀的錯誤訊息"}`

payload 直接放頂層，**不包一層 `data`**；也不加 `meta` / `elapsed_ms` 等欄位。

**為何回 dict 而非 JSON 字串**：FastMCP 會自行序列化 dict，回字串等於雙重序列化，且迫使呼叫端先 `json.loads` 才能判斷成敗，使 `result["ok"]` 這類客觀驗收斷言無法成立。

標準用法（工具層各檔一律如此匯入，不要再自行定義本地 `_json`）：

```python
from ansys_unified_mcp.shared import mcp, as_envelope as _envelope

@mcp.tool()
def some_tool(...) -> dict:
    return _envelope(controller.do_something(...))
```

`as_envelope` 為容錯正規化：dict 補齊缺少的 `ok` 後原樣回傳；str 優先解析為 JSON 物件，失敗則包成 `{"ok": True, "output": <原字串>}`；`None` → `{"ok": True}`。失敗信封可用 `shared.error_envelope(msg, **extra)` 建立。未連線時各工具開頭呼叫 `_check_connection()`，回傳統一的失敗信封。

**守門機制**：`tests/unit/test_envelope_contract.py` 以 AST 掃描全部工具模組，任一 `@mcp.tool` / `@aliased_tool` / 自製裝飾器工廠（如 `products/fluent/tools.py` 的 `@tool_fluent`、`products/geometry/tools.py` 的 `@tool_geometry`）標註非 dict 即測試失敗。不依賴 `TOOL_REGISTRY`，因為裸 `@mcp.tool` 註冊的工具不會進入該字典。

**例外**：`@mcp.resource` 回傳 `str` 屬正常（resource 本質為文字內容），不受此慣例約束。

## 4. 新增功能檢查清單

新增**一個工具**：
1. 放進對應 `products/<product>/tools.py`。
2. 依第 2 節命名（`<product>_<verb>_<object>`）。
3. 開頭 `_check_connection()`；回傳走第 3 節信封。
4. 底層優先用 script runner 組腳本（見 `agents/contexts/context.md` 第 2 節），避免綁死版本相關高階 API。
5. docstring 要清楚（用途、參數、範例）——這是維護者與 AI 的介面。

新增**一個產品**：
1. `products/<product>/facade.py` 建控制器，session 一律走 `SessionRegistry`。
2. `products/<product>/tools.py` 建工具，委派給控制器。
3. 若需新的執行機制（call_tool 分派、批次 job 驅動），實作放 `products/<product>/driver.py` 或 `call_dispatch.py`；僅與產品無關的共用機制才放 `drivers/` 或 `bridges/`。
4. 在 `__main__.py` import 新的 tools 模組以註冊。
5. 若動到 `core/` 或連線解析，先補冒煙測試（該區目前無測試覆蓋）。

## 5. 相關文件

- `agents/contexts/context.md`：專案定位、四層架構、兩條執行通道、thin script runner 設計理由、已知技術債。
- `README.md`：安裝與啟動（如存在）。
