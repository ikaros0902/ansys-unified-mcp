# Mechanical 模組行為與架構規範說明書 (SPEC_MECHANICAL.md)

本文件依據 REA $\times$ Jev 潔淨室規範，自既有代碼與 API 知識庫提煉出 [`products/mechanical/`](file:///F:/Ming_python/ansys-unified-mcp/src/ansys_unified_mcp/products/mechanical/) 的完整行為合約。每條規則皆附帶客觀證據錨點。

---

## 一、核心基礎設施與錯誤解析合約 (Core Infrastructure & Parsing Contract)

### Rule INF-01: 布林值與信封標準化 (Envelope Normalization)
- **行為定義 (Given-When-Then)**:
  - *Given*: 任何來自求解器或內部封裝的回傳字典。
  - *When*: 呼叫 `_normalize_dict_envelope(data)`。
  - *Then*:
    1. 若未含 `'ok'` 鍵且內含 `'error'` 鍵，則補設 `ok: False`；其餘預設 `ok: True`。
    2. 強制將 `'ok'` 鍵轉換為標準 Python `bool` 型別（禁止字串 `"false"` 誤判為 True）。
- **[Evidence: src/ansys_unified_mcp/products/mechanical/api.py:10-31]**

### Rule INF-02: 全域優先致命錯誤偵測 (Fatal Exception Detection)
- **行為定義**:
  - *Given*: Mechanical IronPython 腳本之 stdout 輸出字串。
  - *When*: 輸出包含以下任一異常標識：
    `"exception:"`, `"traceback"`, `"syntaxerror:"`, `"nameerror:"`, `"attributeerror:"`, `"typeerror:"`, `"indexerror:"`, `"keyerror:"`, `"system.exception"`, `"ansys.mechanical.core.errors"`, `"script error:"`, `"system.nullreferenceexception"`, `"system.invalidoperationexception"`, `"502 bad gateway"`, `"500 internal server error"`。
  - *Then*: 即使輸出末行碰巧包含合法 JSON，`_parse_mechanical_output` **絕不能判定成功**，必須直接回傳 `ok: False`，並將錯誤訊息保留於 `error` 欄位。
- **[Evidence: src/ansys_unified_mcp/products/mechanical/api.py:38-49, 70-143]**

### Rule INF-03: 連線探針與死連線自癒 (Connection Probe & Self-Healing)
- **行為定義**:
  - *Given*: `SessionRegistry` 中既有的 Mechanical gRPC session。
  - *When*: 呼叫 `connect()` 嘗試重用連線。
  - *Then*:
    1. 必須以快速輕量探針（`1+1` 或 `ExtAPI.DataModel` 存活檢查）驗證連線。
    2. 若探針逾時或連線中斷，必須自動自快取與註冊表驅逐（`registry.drop`），並嘗試重新連線或向使用者回報明確斷線原因。
- **[Evidence: src/ansys_unified_mcp/products/mechanical/facade.py:98-104]**

### Rule INF-04: 內嵌腳本全英文原則 (Strict ASCII Embedded Scripts)
- **行為定義**:
  - *Given*: 任何傳遞給 Mechanical IronPython 2.7 或 MAPDL 之腳本字串。
  - *When*: 腳本生成或組裝。
  - *Then*: 腳本內部字串與註解必須為純 ASCII（`ord(c) < 128`），嚴禁包含非 ASCII 字元（如繁體/簡體中文），以避免 IronPython 解譯器 ANSI 編碼損毀。
- **[Evidence: 全域核心規則 00-behavior.md 第一條]**

---

## 二、領域子模組拆分與責任劃分 (Domain Decomposition Spec)

為消除 1,666 行之 God Module [`api.py`](file:///F:/Ming_python/ansys-unified-mcp/src/ansys_unified_mcp/products/mechanical/api.py)，將其解耦為 5 大單一責任領域模組，並統一使用 `@mechanical_op` 裝飾器消除 39 處重複的連線檢查與例外捕獲樣板：

### 1. `session_ops.py`（連線與生命週期）
- 涵蓋函式：`list_instances`, `connect_to_mechanical`, `launch_mechanical`, `disconnect_from_mechanical`, `check_mechanical_connection`, `run_mechanical_script`
- **[Evidence: api.py:165-210, 686-698]**

### 2. `scoping_ops.py`（模型資訊、材料與具名選擇）
- 涵蓋函式：
  - `get_model_info` [Evidence: api.py:213-233]
  - `list_materials`, `assign_material` [Evidence: api.py:236-278]
  - `list_named_selections`, `delete_named_selection` [Evidence: api.py:717-755]
  - `suppress_bodies` [Evidence: api.py:763-783]
  - `list_point_masses` [Evidence: api.py:786-814]

### 3. `mesh_ops.py`（網格劃分與 CFL 調優）
- 涵蓋函式：
  - `set_mesh_element_size`, `generate_mesh`, `get_mesh_statistics` [Evidence: api.py:281-337]
  - `tune_cfl_mesh` [Evidence: api.py:1618-1662]

### 4. `boundary_ops.py`（負載與邊界條件）
- 涵蓋函式：
  - `add_fixed_support`, `add_frictionless_support` [Evidence: api.py:340-360, 822-841]
  - `add_force`, `add_pressure` [Evidence: api.py:363-417]
  - `add_displacement`, `add_remote_displacement` [Evidence: api.py:844-947]
  - `add_standard_gravity`, `add_remote_force`, `add_moment` [Evidence: api.py:950-1045]
  - `list_boundary_conditions` [Evidence: api.py:420-435]

### 5. `solution_ops.py`（求解控制與後處理結果）
- 涵蓋函式：
  - `solve_analysis`, `get_solve_status` [Evidence: api.py:438-476]
  - `add_total_deformation_all_modes`, `add_total_deformation`, `get_modal_frequencies` [Evidence: api.py:479-545]
  - `add_equivalent_stress`, `add_directional_deformation`, `add_principal_stress`, `add_stress_tool`, `add_reaction_force` [Evidence: api.py:1053-1185]
  - `generate_report` [Evidence: api.py:548-683]
  - 高階組裝特徵：`convert_prefix_to_point_mass`, `convert_part_to_point_mass`, `get_model_tree_hierarchy`, `assign_materials_from_bom`, `create_joints_from_groups` [Evidence: api.py:1380-1615]

---

## 三、三層驗證與 3-Broken 金絲雀驗收規格

1. **Broken-1 (ASCII / API 符號驗證)**：
   - 注入非 ASCII 註解或無效 `ExtAPI` 方法，靜態檢查器與 `api_validate_script` 必須回報失敗。
2. **Broken-2 (例外吞沒驗證)**：
   - 模擬混合輸出，若 `_parse_mechanical_output` 失去預檢能力，對抗測試必須翻紅。
3. **Broken-3 (方向性物理量與單位縮放驗證)**：
   - 反轉載荷方向，必須檢驗帶正負號的方向變形 (`directional_deformation_z`) 與支承反力 (`reaction_force_z`)，`compare.py` 必須回報 `differs` (Exit Code 1)。
