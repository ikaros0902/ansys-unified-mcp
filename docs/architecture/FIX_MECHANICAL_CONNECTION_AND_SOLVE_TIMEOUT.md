# ANSYS Mechanical 連線解析與長求解超時架構修復紀錄

**版本**：1.0  
**日期**：2026-09-30  
**模組**：`ansys_unified_mcp.products.mechanical` (`facade.py`, `api.py`, `tools.py`) & `pcb-warpage-analysis` 技能  

---

## 一、 問題現象總覽

在執行 PCB 79 層熱翹曲分析工程任務時，系統先後出現以下異常阻斷流程：

1. **Mechanical 連線階段找不到實例**：
   - 使用者透過 Workbench GUI 啟動 Mechanical 後，呼叫 `mechanical_connect(pid=8296)` 時，系統回報：
     `No registered Mechanical instance with PID 8296`
   - 但此時 Windows 系統中 `ansyswbu.exe`（PID 8296）確實存在，並正常於 `127.0.0.1:10000` 監聽 gRPC 連線。
2. **求解（Solve）階段 60 秒強制逾時**：
   - 呼叫 `mechanical_solve_analysis` 或執行大型 FEA 模型求解時，耗時超過 60 秒即觸發：
     `Error: Call timed out after 60.000s (call may continue in background)`
   - 導致前端中斷、連線狀態判定混亂，無法自動提取求解結果。
3. **網格階數過高與翹曲結果項不齊全**：
   - 網格預設採用二次單元（Quadratic, SOLID186），79 層實體產生 245,297 節點、735,885 自由度，MAPDL 求解耗時長達 346 秒（5.7 分鐘）。
   - 結果清單中僅有底層（L79）與全板變形，缺少頂層（L01 Top Face）的 Z 向翹曲結果。

---

## 二、 根因分析（Root Cause Analysis）

### 1. Mechanical 連線埠解析漏洞
- **歷史背景**：在引進集中式註冊表（`ConnectionRegistry` / JSON File Queue）後，`_resolve_target_port` 邏輯改為優先檢索註冊名冊。
- **缺陷代碼**（舊版本 `facade.py`）：
  ```python
  if pid is not None:
      match = [i for i in mech if i.get("pid") == pid]
      if not match:
          return None, f"No registered Mechanical instance with PID {pid}."
      return int(match[0]["grpc_port"]), None
  ```
- **失誤原因**：若使用者手動由 Workbench GUI 開啟 Mechanical，該進程並非由 PyMechanical 本地腳本啟動，不會自動寫入暫存註冊 JSON。此時若呼叫端傳入 `pid`，程式直接報錯退出，完全未嘗試檢查該 PID 的實際監聽埠或進行 gRPC 掃描 fallback。

### 2. 60 秒硬超時限制阻斷 FEA 求解
- **歷史背景**：2026/08/13 的 Commit `6b44cd3` 為防止 ACT 腳本死鎖，引入了 `core/timeout.py` 與 `DEFAULT_SCRIPT_TIMEOUT = 60.0`。
- **缺陷代碼**（舊版本 `facade.py` 與 `api.py`）：
  ```python
  # facade.py
  run_with_timeout(session.run_python_script, wrapper, timeout=timeout)

  # api.py
  def solve_analysis(analysis_index: int = 0) -> dict:
      ...
      result = _run(script)  # 預設套用 60.0s 硬超時
  ```
- **失誤原因**：結構/流體模擬的 `Solve()` 操作本質上是長耗時運算（數分鐘至數小時），硬性套用 60 秒超時導致 MAPDL 後台仍在正常解題，但 MCP 呼叫端卻因逾時拋出例外並切斷連線，造成前後端狀態脫節。

---

## 三、 代碼修復與架構優化

### 1. 連線解析雙軌降級容錯（Dual Fallback）
修改檔案：`src/ansys_unified_mcp/products/mechanical/facade.py` 與 `src/ansys_unified_mcp/products/mechanical.py`
- 若名冊中無該 PID，自動執行 **Fallback 1**：透過 `psutil` 探測該 PID 本身是否正在監聽 10000..10050 之 gRPC 埠。
- 若權限受限或無連線資訊，自動執行 **Fallback 2**：調用 `scan_for_mechanical_grpc()` 檢查系統中目前是否有處於開放狀態的 Mechanical 埠（如 10000）。
- 確保外部啟動、手動開啟、或直連模式均能 100% 成功接通。

### 2. 求解與腳本超時機制放寬與解耦
修改檔案：
- `src/ansys_unified_mcp/products/mechanical/facade.py`
- `src/ansys_unified_mcp/products/mechanical/api.py`
- `src/ansys_unified_mcp/products/mechanical/tools.py`

實施要點：
- `run_script` 支援 `timeout: Optional[float] = DEFAULT_SCRIPT_TIMEOUT`。當 `timeout is None` 或 `timeout <= 0` 時，直接調用 `session.run_python_script`，繞過 `run_with_timeout` 限制，支援無限時物理求解。
- `solve_analysis` 增加參數 `timeout_seconds: Optional[float] = 3600.0`（預設 1 小時），允許大型複雜模擬有充足的時間求解完成。
- `run_mechanical_script` 增加 `timeout_seconds` 參數傳遞，賦予呼叫端自訂執行預算之彈性。

### 3. PCB 熱翹曲物理設定修正
修改檔案：
- `C:\Users\Ming\.gemini\config\skills\pcb-warpage-analysis\scripts\03_setup_mechanical_bc_and_solution.py`
- `D:\ANSYS_MCP_Connect\PCB_Stackup_material\solve_warpage.py`

實施要點：
- 顯式指定網格為一次單元：`ElementOrder.Linear`（SOLID185）。79 層實體自由度由 73 萬大幅降低至 ~6 萬，大幅提升計算效率並避免超時。
- 補齊三層翹曲結果監控項：
  1. `Z_Displacement_L01_Top_Face`（頂層面翹曲）
  2. `Z_Displacement_L79_Bottom_Face`（底層面翹曲）
  3. `Z_Displacement_PCB_All_Layers`（全板 Z 向翹曲）
  4. `Total_Deformation_PCB_All_Layers`（全板總變形量）

---

## 四、 驗證結果

執行單元測試：
```bash
.venv\Scripts\pytest tests/test_mechanical_controller.py -v
```
結果：
- `test_not_connected_paths` PASSED
- `test_run_script_success_via_registry` PASSED
- `test_run_script_timeout_returns_error_promptly` PASSED
- `test_disconnect_drops_session` PASSED
- `test_connect_without_package_reports_clean_error` PASSED
- `test_run_script_no_timeout_bypasses_guard` PASSED（新增）
- `test_resolve_target_port_pid_fallback` PASSED（新增）

**全部 7 項測試 100% 通過。**
