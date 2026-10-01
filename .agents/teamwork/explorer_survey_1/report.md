# R1 代碼重複與引用狀況調研報告 (Codebase Deduplication Survey)

**調研代理**：`explorer_survey_1` (teamwork_preview_explorer)  
**日期時間**：2026-10-01  
**目標任務**：針對 `ORIGINAL_REQUEST.md` 之 R1 需求（消除代碼重複與技術債），全面探查 `src/ansys_unified_mcp/products/mechanical.py` 與 `src/ansys_unified_mcp/products/mechanical/facade.py`，檢索全專案所有依賴引用，評估刪除舊版檔案與切換至 `facade` 的可行性、風險與改動步驟。

---

## 一、`mechanical.py` 與 `mechanical/facade.py` 內容與結構比對分析

### 1. 物理比對與字元一致性檢驗
經執行 Python `filecmp.cmp(..., shallow=False)` 進行深度二進位比對，結果顯示：
- `src/ansys_unified_mcp/products/mechanical.py`（長度：229 行，大小：9,972 Bytes）
- `src/ansys_unified_mcp/products/mechanical/facade.py`（長度：229 行，大小：9,972 Bytes）
- **二進位一致性**：`Identical: True`（兩者內容 100% 逐行完全相同）。

### 2. 結構與公開介面盤點
兩檔案均實作並導出完全相同的類別與符號：
1. `PRODUCT = "mechanical"`
2. `DEFAULT_SCRIPT_TIMEOUT = 60.0`
3. 輔助函數：`_esc(s: str) -> str`（轉義 IronPython 字串）
4. 核心類別：`MechanicalController`
   - `_resolve_target_port(port, pid)`：解析連線目標 gRPC 埠號（支援 ConnectionManager、PID 監聽埠檢測與掃描 fallback）
   - `connect(port, pid)`：透過 PyMechanical (`ansys.mechanical.core`) 連線既有 Mechanical 實例
   - `launch(batch)`：無頭或有介面啟動 Mechanical 實例
   - `_probe_session(session)`：Session 存活心跳探測（具 10 秒緩存）
   - `run_script(script, key, timeout)`：帶安全守衛 (`check_script`) 與超時保護 (`run_with_timeout`) 的腳本執行包裝器
   - `disconnect(key)`：自 SessionRegistry 移除 Session
   - `is_connected(key)`：連線狀態探測
   - `status()`：取得連線狀態與 Session 列表
5. 全域單例：`controller = MechanicalController()`

### 3. 同目錄下其他垂直切片模組
在 `src/ansys_unified_mcp/products/mechanical/` 套件目錄內，已具備完整垂直切片架構：
- `facade.py`：Session 管理與通訊協定（Controller）
- `api.py`：60KB 規模之高階分析業務 API（材料、網格、邊界條件、求解、結果提取之 ACT 腳本生成）
- `driver.py`：標準求解器驅動層（繼承 BaseDriver，實現狀態機與作業生命週期）
- `tools.py`：FastMCP 工具層（定義 39 個 `@mcp.tool` 供 AI 調用）
- `__init__.py`：將上述模組聚合并對外 re-export
- `plugins/`：ACT 插件相關設定與腳本

### 4. 關鍵結論
**刪除舊版 `src/ansys_unified_mcp/products/mechanical.py` 前，100% 確認無任何獨特邏輯或介面尚未被 `facade.py` 涵蓋。**
舊版檔案純屬歷史重構未清理的冗餘複本（Dead Duplicate Code）。

---

## 二、Python 運行時解析與幽靈遮蔽現象 (Shadowing)

在目前的專案結構下：
- `src/ansys_unified_mcp/products/mechanical.py`
- `src/ansys_unified_mcp/products/mechanical/__init__.py`

兩者並存於 `src/ansys_unified_mcp/products/`。
經實測 Python 模組導入解析：
```python
import ansys_unified_mcp.products.mechanical as m
print(m.__file__)
# 輸出：.../src/ansys_unified_mcp/products/mechanical/__init__.py
```
**分析**：
1. Python 在解析 `ansys_unified_mcp.products.mechanical` 時，套件目錄優先，導致舊版 `mechanical.py` 在執行期早已被 `mechanical/__init__.py` 遮蔽（Shadowed），根本不會被直接載入！
2. 然而，`mechanical/__init__.py` 內部第 16 行：
   ```python
   from ansys_unified_mcp.products.mechanical import tools as _tools
   ```
   會導致任何只是想匯入 `MechanicalController` 的模組或測試，在載入 `mechanical` package 時被動執行 `tools.py`，連帶拉入整個 MCP 運行時依賴（FastMCP、pydantic 等）。
3. 若將依賴精確重定向至 `ansys_unified_mcp.products.mechanical.facade`，將直接跳過不必要的 tools 載入，大幅降低耦合。

---

## 三、全專案依賴與引用清單 (Impacted References)

經全庫掃描（包含原始碼、測試、範例、技能腳本與技術文件），引用分佈如下：

### 類別 A：核心原始碼層（需更新 import）
1. `src/ansys_unified_mcp/tools/mechanical_workflow_tools.py`
   - **第 15 行**：`from ansys_unified_mcp.products.mechanical import controller, _esc`
   - **處置**：改為 `from ansys_unified_mcp.products.mechanical.facade import controller, _esc`

### 類別 B：測試套件層（需更新 import 與 mock 對象）
1. `tests/test_mechanical_controller.py`
   - **第 22 行**：`from ansys_unified_mcp.products.mechanical import MechanicalController, PRODUCT`
   - **處置**：改為 `from ansys_unified_mcp.products.mechanical.facade import MechanicalController, PRODUCT`
2. `tests/adversarial/test_final_stress_harness.py`
   - **第 23 行**：`import ansys_unified_mcp.products.mechanical as mechanical_mod`
   - **第 82-84, 117-119, 300-302 行**：`patch.object(mechanical_mod.controller, ...)`
   - **處置**：改為 `import ansys_unified_mcp.products.mechanical.facade as mechanical_mod`
3. `tests/adversarial/test_m1_envelope_stress_challenge.py`
   - **第 27 行**：`import ansys_unified_mcp.products.mechanical as mechanical_mod`
   - **第 397-401, 413, 440, 475 行**：`patch.object(mechanical_mod.controller, ...)`
   - **處置**：改為 `import ansys_unified_mcp.products.mechanical.facade as mechanical_mod`
4. `tests/adversarial/test_m1_alias_challenge.py`
   - **第 20 行**：`import ansys_unified_mcp.products.mechanical as mechanical_mod`
   - **第 172, 175-176 行**：`patch.object(mechanical_mod.controller, ...)`
   - **處置**：改為 `import ansys_unified_mcp.products.mechanical.facade as mechanical_mod`

### 類別 C：範例與技能測試腳本（需更新 import）
1. `examples/shock_analysis/audit_rm_deep.py` (第 6 行)
2. `examples/shock_analysis/execute_full_shock_act_pipeline.py` (第 7 行)
3. `examples/shock_analysis/run_shock_35g_pipeline.py` (第 7 行)
4. `skills/shock-analysis-workflow/scripts/test_session_01.py` (第 17 行)
5. `skills/shock-analysis-workflow/scripts/test_session_02.py` (第 18 行)
6. `skills/shock-analysis-workflow/scripts/test_session_03.py` (第 18 行)
7. `skills/shock-analysis-workflow/scripts/test_session_04.py` (第 18 行)
8. `skills/shock-analysis-workflow/scripts/test_session_05.py` (第 18 行)
9. `skills/shock-analysis-workflow/scripts/test_session_06.py` (第 17 行)
10. `skills/shock-analysis-workflow/scripts/test_session_07.py` (第 15 行)
11. `skills/shock-analysis-workflow/scripts/test_session_08.py` (第 16 行)
   - **處置**：以上 11 處均將 `from ansys_unified_mcp.products.mechanical import MechanicalController` 更新為 `from ansys_unified_mcp.products.mechanical.facade import MechanicalController`。

### 類別 D：已經合規或屬於聚合層（無需改動）
1. `src/ansys_unified_mcp/products/mechanical/api.py` (第 8 行)：已經是 `from ansys_unified_mcp.products.mechanical.facade import controller, _esc`。
2. `src/ansys_unified_mcp/products/mechanical/tools.py` (第 14 行)：已經是 `from ansys_unified_mcp.products.mechanical.facade import controller, _esc`。
3. `src/ansys_unified_mcp/products/mechanical/__init__.py` (第 9-14 行)：身為聚合包，負責 re-export `facade` 符號以維持外部相容性，保留現狀。
4. `src/ansys_unified_mcp/__main__.py` (第 39 行)：載入的是 `ansys_unified_mcp.products.mechanical.tools`，合規。
5. `src/ansys_unified_mcp/drivers/mechanical_driver.py` (第 3 行)：引用 `driver as _driver`，合規。
6. `src/ansys_unified_mcp/products/mechanical_api.py` (第 3 行)：向後相容 shim，引用 `api as _api`，合規。

### 類別 E：文件與註解提示（建議同步修正）
1. `src/ansys_unified_mcp/drivers/sim_impl.py` (第 347, 554 行)：註解提及 `products/mechanical.py`
2. `src/ansys_unified_mcp/products/optislang/facade.py` (第 6 行)：註解提及 `products/mechanical.py`
3. `tests/test_mechanical_controller.py` (第 1 行)：docstring 提及 `(products/mechanical.py)`
4. `tests/test_sessions.py` (第 3 行)：docstring 提及 `products/mechanical.py`
5. `tests/adversarial/test_chapter2_adversarial_verification.py` (第 85 行)：註解提及 `products/mechanical.py`
6. `docs/architecture/FIX_MECHANICAL_CONNECTION_AND_SOLVE_TIMEOUT.md` (第 60 行)：雙軌修改歷史紀錄

---

## 四、改動實施步驟與風險評估矩陣

### 1. 具體改動步驟 (Step-by-Step Execution Plan)

#### 步驟 1：實體刪除舊版檔案
- 移除 `src/ansys_unified_mcp/products/mechanical.py`。
- 驗證：檢查檔案系統，確認 `src/ansys_unified_mcp/products/mechanical.py` 已不復存在。

#### 步驟 2：核心源碼與測試重定向
- 修改 `src/ansys_unified_mcp/tools/mechanical_workflow_tools.py`。
- 修改 `tests/test_mechanical_controller.py`。
- 修改 `tests/adversarial/test_final_stress_harness.py`、`test_m1_envelope_stress_challenge.py`、`test_m1_alias_challenge.py`。

#### 步驟 3：範例與技能測試腳本更新
- 批次更新 `examples/shock_analysis/` 下 3 個腳本。
- 批次更新 `skills/shock-analysis-workflow/scripts/` 下 8 個腳本。

#### 步驟 4：註解與文件路徑校正
- 修正 `sim_impl.py`、`optislang/facade.py`、`test_sessions.py` 等處之註解文字。

#### 步驟 5：測試套件全面回歸
- 執行 `pytest tests/test_mechanical_controller.py`。
- 執行對抗測試與單元測試。

---

### 2. 風險評估與防護對策

| 風險項目 | 風險等級 | 影響說明 | 防護與緩解對策 |
|---|---|---|---|
| **遺漏獨特邏輯** | **極低 (Zero)** | 誤刪未同步的功能 | 已由二進位比較證實兩檔案 100% 相同，零邏輯遺失。 |
| **Mock / Patch 標的失效** | **低** | 測試中使用 `patch.object(mechanical_mod.controller)` 若 module 替換不完整可能導致 mock 脫靶 | `facade.py` 中 `controller` 是唯一的單例實例，將測試 import 導向 `mechanical.facade as mechanical_mod` 可使 patch 直接穿透至來源。 |
| **外部用戶向後相容性** | **極低** | 外部調用若仍寫 `from ansys_unified_mcp.products.mechanical import MechanicalController` | `mechanical/__init__.py` 依然保留 re-export，對外公開 API 介面絲毫不受影響。 |
| **模組載入歧義消除** | **正向收益** | 徹底解決 package 目錄與 .py 單檔同名遮蔽的潛在隱患 | 刪除單檔後，Python 匯入路徑清晰單一，杜絕 packaging 部署時的快取混淆。 |

---

## 五、總結

`src/ansys_unified_mcp/products/mechanical.py` 的刪除條件完全成熟，無任何邏輯或功能風險。受影響的引用範圍明確（主要為 5 處代碼/測試與 11 處輔助腳本）。實施後將徹底消除雙軌維護技術債，達成 R1 驗收判準。
