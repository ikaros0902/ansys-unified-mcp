# Project: ANSYS Unified MCP Phase 1 核心架構改造

## Architecture
ANSYS Unified MCP 是基於 FastMCP 協定的全功能模擬控制伺服器，將各類 ANSYS CAE 模組（Mechanical、Workbench、OptiSLang、Fluent 等）封裝為標準 MCP 工具。
Phase 1 聚焦於核心工具架構改造：
1. **命名規範化與雙軌 Alias 層**：
   - 透過 `src/ansys_unified_mcp/shared.py` 中的 `@aliased_tool` 裝飾器，讓所有工具對外以新標準名稱 `<product>_<verb>_<object>` 提供服務，同時保留舊別名並標記 `[DEPRECATED ALIAS for ...]`。
   - 兩者在 FastMCP 內部綁定同一函式指標，可同時於 `tools/list` 查詢並於 `tools/call` 調用。
2. **統一 JSON 信封層**：
   - 所有工具回傳值一律標準化為 `{"ok": bool, ...}` JSON 結構。
   - 解決歷史程式碼中缺乏 `ok` 鍵（如 `check_mechanical_connection`）與 22 處假陽性黑洞（`except Exception: return _json({"ok": True, "raw_output": result})`）。
3. **高階組合式工程工作流 (Composite Workflows)**：
   - `src/ansys_unified_mcp/tools/mechanical_workflows.py` 封裝一鍵式操作（靜態結構分析、模態分析、模型健康度診斷），內部自動協調幾何、邊界、網格、求解與結果後處理，並具備嚴格的參數校驗與未連線降級保護。
4. **自動化等效性測試與回歸驗證**：
   - 建立全自動化測試套件 `test_aliased_tools.py`，100% 覆蓋所有別名與規範名稱的註冊對稱性、Schema 一致性與調用結果等價性。

---

## Feature Inventory
所有來自原始需求與 Survey 探查之必要功能項目：

| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Mechanical 39 工具雙軌註冊 | 確保 `mechanical.py` 中 39 個工具全數以標準名稱與舊別名雙軌註冊於 FastMCP | M1 | AC1 |
| 2 | check_mechanical_connection 信封修復 | 補齊遺失的 `"ok"` 鍵，連線回傳 `{"ok": True, "connected": True, ...}`，未連線回傳 `{"ok": False, "connected": False}` | M1 | Survey E2 |
| 3 | 根除 22 處假陽性回傳漏洞 | 替換 `except Exception: return _json({"ok": True, ...})`，引入 `_safe_json_response` 確保腳本錯誤時回傳 `{"ok": False, "error": str}` | M1 | AC1 / Survey E2 |
| 4 | 組合式靜態分析工作流 | `mechanical_setup_and_solve_static_structural`（支援 `mechanical_setup_and_solve` 等別名），完成幾何、邊界、網格、求解到結果萃取 | M2 | AC2 / R2 |
| 5 | 組合式模態分析工作流 | `mechanical_setup_and_solve_modal`（支援 `mechanical_modal_analysis` 等別名），完成模態求解、提取前 N 階固有頻率與振型 | M2 | AC2 / R2 |
| 6 | 組合式模型健康診斷工具 | `mechanical_diagnose_model_health`，檢查幾何實體、網格品質、邊界條件完整度 | M2 | R2 |
| 7 | 高階工作流參數校驗與離線防護 | 在 Python 端完成網格尺寸、力負載方向等邊界檢查，未連線時回傳標準錯誤信封 | M2 | AC2 |
| 8 | aliased_tool 統一信封保證攔截器 | 在 `shared.py` 的裝飾器層注入 `_normalize_envelope`，無死角保證所有工具輸出皆符合 JSON 信封 | M3 | Survey E1 |
| 9 | 測試環境路徑修復 (conftest.py) | 解決 `tests` 根目錄模組解析與 `pytest -o pythonpath` 基準線健全度 | M3 | Survey E3 |
| 10 | 雙軌別名 100% 等效性測試套件 | `tests/unit/test_aliased_tools.py` 實裝註冊對稱性、Schema 一致性、離線調用輸出等價性自動化測試 | M4 | AC3 |
| 11 | 全域 pytest 零回歸檢驗 | 執行全套單元測試與端到端測試，確保通過率維持在 99.47% 以上（除已知環境缺包外無任何代碼邏輯錯誤） | M4 | AC3 |
| 12 | 獨立誠信審計與專案竣工驗收 | 執行 Forensic Auditor 二元獨立審計，生成整體交付驗證報告 | M5 | AC1-AC3 |

---

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Mechanical 工具信封修復與安全響應重構 | 修復 `check_mechanical_connection`、根除 22 處假陽性黑洞、實作 `_safe_json_response` | none | DONE |
| M2 | Mechanical Workflows 組合式工具完善 | 實裝 `mechanical_workflows.py`、擴充高階分析別名、加入參數邊界校驗與未連線防護 | M1 | DONE |
| M3 | 工具裝飾器信封保證層與測試環境補強 | 在 `shared.py` 實作 `@aliased_tool` 信封保證攔截器，補齊路徑與 SessionRegistry 健全性 | M1, M2 | DONE |
| M4 | 雙軌別名 100% 等效性測試與回歸驗證 | `tests/unit/test_aliased_tools.py` 達成 100% 別名覆蓋，全域 246 項測試零失敗 | M3 | DONE |
| M5 | 獨立誠信審計、全域復核與竣工驗收 | 全產品線別名等價、行為安全規範重構與 18 項 Skill 漸進式瘦身全數通過驗收 | M4 | DONE |

---

## Interface Contracts
### 1. `_safe_json_response(result: Any, default_error: str = "Script execution failed") -> str`
- 輸入：`result`（可為已解析的 dict、JSON 字串、或是 IronPython 拋出的錯誤字串）
- 輸出：合法 JSON 字串。若內容表示失敗或包含非 JSON 錯誤輸出，保證輸出：
  ```json
  {"ok": false, "error": "<詳細錯誤原因>", "raw_output": "<原始輸出>"}
  ```
- 若內容為成功字典，保證輸出包含 `"ok": true`：
  ```json
  {"ok": true, ...}
  ```

### 2. `aliased_tool` 信封防護裝飾器契約
- 無論底層函式回傳字串或 dict，經由 FastMCP 調用後保證回傳型態為合法 JSON，且根物件必定包含 `"ok": bool`。

### 3. 高階工作流簽名契約
- `mechanical_setup_and_solve(mesh_size: float = 0.01, force_y: float = -1000.0, ...)`
  - 參數驗證：`mesh_size > 0`，否則直接回傳 `{"ok": false, "error": "mesh_size must be positive"}`。
  - 離線防護：未連線時回傳 `{"ok": false, "error": "Not connected to Mechanical. Call connect_to_mechanical first."}`。

---

## Code Layout
- `src/ansys_unified_mcp/shared.py`: FastMCP 實例、`aliased_tool` 裝飾器與信封正規化
- `src/ansys_unified_mcp/tools/mechanical.py`: Mechanical 39 個工具與 `_safe_json_response` 實作
- `src/ansys_unified_mcp/tools/mechanical_workflows.py`: 高階組合式工程分析工具
- `src/ansys_unified_mcp/__main__.py`: 進入點與模組動態載入分流
- `tests/conftest.py`: pytest 路徑與共用 fixtures
- `tests/unit/test_aliased_tools.py`: 雙軌別名等效性與信封自動化測試套件
