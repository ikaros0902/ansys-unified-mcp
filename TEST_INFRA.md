# ANSYS Unified MCP 2.0 測試基礎設施規範 (TEST_INFRA.md)

本文件定義 ANSYS Unified MCP 2.0 之 4-Tier 漸進式測試防線架構、自動化執行命令、質量覆蓋門檻、Mocking 設施以及三大合成端到端場景驗收規格。

---

## 一、 4-Tier 漸進式測試分層架構 (Test Matrix)

為兼顧「極速反饋」、「高保真物理斷言」與「免商業 License 依賴」，本專案建立 4-Tier 測試架構：

```
+-----------------------------------------------------------------------------------+
| Tier 4: Live Hardware/License E2E (可選/現場, 需真機 ANSYS 2026 R1 + License)     |
+-----------------------------------------------------------------------------------+
| Tier 3: Synthetic E2E Scenarios (合成端到端, 跨工作流模擬, overview.html 閉環)    |
+-----------------------------------------------------------------------------------+
| Tier 2: Component Unit & Contract Tests (離線單元測試, 100% Mock 隔離, 毫秒級執行) |
+-----------------------------------------------------------------------------------+
| Tier 1: Static Analysis & Lint Gate (py_compile + ruff check, 語法與型別 0 錯誤)  |
+-----------------------------------------------------------------------------------+
```

### 1.1 測試層級詳細定義

| 層級 (Tier) | 名稱 | 覆蓋範疇與目標 | 依賴需求 | 執行時間 | 觸發時機 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | **靜態語法與代碼品質閘門** | 語法完整性、未定義變數、重大語法與匯入循環檢測。 | 無 (零外部相依) | < 2 秒 | 每次代碼變更、Git Pre-commit |
| **Tier 2** | **核心元件單元與契約測試** | `JobManager` 沙盒生命週期、`PreFlightGatekeeper` 物理安全阻斷、`WatchdogSentinel` 正則解析、`WorkbenchLinks` 腳本生成、`SummaryJson` Schema 校驗。 | 無 (內建高保真 Mock 物件) | < 5 秒 | 本地日常開發、PR 合併標準 |
| **Tier 3** | **合成端到端場景測試** | 三大驗收工況（隨機振動模態質量阻斷、落摔衝擊沙漏能熔斷、熱翹曲 Cell Link 串接與儀表板合成）、非同步作業狀態機流轉。 | 無 (依賴合成日誌流與虛擬求解器) | < 8 秒 | 每日構建、版本發布驗收 |
| **Tier 4** | **實體求解器驗收測試** | 真實調用 PyMechanical, PyFluent, PyWorkbench 連線執行實際 FEA/CFD 計算。 | 需本機安裝 ANSYS 2026 R1 與可用 License | 2 ~ 30 分鐘 | 現場部署驗收 (無 License 自動 Skip) |

---

## 二、 標準驗證指令集 (Execution Commands)

### 2.1 環境設置與前置
本專案支援使用 Python 3.14 環境，透過環境變數 `PYTHONPATH` 指向 `src` 目錄：
```powershell
$env:PYTHONPATH="F:\Ming_python\ansys-unified-mcp\src"
```

### 2.2 Tier 1: 靜態語法與風格檢查
```powershell
# 1. 語法編譯檢查 (必須全數編譯通過，Exit Code 0)
& "F:\Ming_python\ansys-unified-mcp\.venv\Scripts\python.exe" -m py_compile (Get-ChildItem -Path "src", "tests" -Filter "*.py" -Recurse | Select-Object -ExpandProperty FullName)

# 2. Ruff 代碼品質檢查 (針對重大錯誤)
uvx ruff check src/ tests/ --select E9,F63,F7,F82
```

### 2.3 Tier 2: 離線單元測試
```powershell
$env:PYTHONPATH="F:\Ming_python\ansys-unified-mcp\src"
C:\Python314\python.exe -m pytest tests/unit/ -v
```

針對核心模組單獨執行：
```powershell
# 僅測試作業沙盒
C:\Python314\python.exe -m pytest tests/unit/test_job_sandbox.py -v

# 僅測試物理安全閘門
C:\Python314\python.exe -m pytest tests/unit/test_preflight_gatekeeper.py -v
```

### 2.4 Tier 3: 合成端到端場景測試
```powershell
$env:PYTHONPATH="F:\Ming_python\ansys-unified-mcp\src"
C:\Python314\python.exe -m pytest tests/e2e/ -v
```

### 2.5 全套自動化回歸一鍵執行
```powershell
$env:PYTHONPATH="F:\Ming_python\ansys-unified-mcp\src"
C:\Python314\python.exe -m pytest tests/ -v --durations=10
```

---

## 三、 測試覆蓋標準與品質門檻 (Quality Gates)

所有提交或合併至主線之代碼，必須嚴格滿足以下量化標準：

1. **通過率 (Pass Rate)**：Tier 1 ~ Tier 3 測試通過率必須為 **100%**，不允許任何無故失敗。
2. **零 Commercial License 依賴**：Tier 1 ~ Tier 3 測試套件**絕對禁止**嘗試建立真實 gRPC/TCP 連線或呼叫未授權的商業 ANSYS 二進位檔。
3. **隔離性 (Isolation)**：
   - 每個測試用例必須獨立建立與清除臨時資料夾，不得依賴測試執行順序。
   - 所有在測試過程中建立的 `jobs/` 沙盒必須建立於暫存路徑（如 `pytest` 之 `tmp_path`），測試結束後自動清理，保持工作區整潔。
4. **時延限制 (Execution Time Limit)**：
   - Tier 1: 總執行時間 $\le 2.0\text{ s}$。
   - Tier 2: 單元測試全套 $\le 5.0\text{ s}$（單個用例 $\le 200\text{ ms}$）。
   - Tier 3: 合成端到端全套 $\le 10.0\text{ s}$。
5. **誠信原則 (Test Integrity)**：
   - 禁止撰寫「恆真」虛晃測試（Facade Tests）。
   - 斷言必須基於客觀規格數值（如物理閾值、Schema 欄位、正則匹配群組），嚴禁單純 `assert True`。

---

## 四、 高保真 Mock 基礎設施規範 (Mocking Infrastructure)

為在離線環境下精確模擬複雜的求解器行為，測試基礎設施位於 `tests/mocks/`：

### 4.1 `mock_streamer.py` (MockLogStreamer)
- **職責**：模擬求解器日誌的即時非同步串流寫入，提供 Watchdog 線程即時解析驗證。
- **支援日誌格式**：
  1. **ANSYS Mechanical `solve.out`**：支援平穩收斂迭代（INCREMENT, SUBSTEP, FORCE CONVERGENCE VALUE < CRITERION）與非線性發散（Substep not converged / NaN / Inf）。
  2. **LS-DYNA `glstat`**：支援健康能量守恆模式（沙漏能比率 1.0%~2.0%）與能量發散/沙漏超標模式（沙漏能佔比迅速飆升至 6.8% > 5.0%）。
  3. **ANSYS Fluent `fluent.log`**：支援連續性/速度/k-omega 殘差正常收斂與殘差暴增/逆流（reversed flow）警告。
- **運作機制**：支援後台守護線程定時 yield 寫入，提供 `start_streaming(interval_sec)` 與 `stop()` 控制介面。

### 4.2 `mock_driver.py` (MockSolverDriver)
- **職責**：實作 `BaseSolverDriver` 介面，供離線測試調用，模擬求解器完整生命週期。
- **支援特性**：
  - `validate_prerequisites()`：離線回傳成功，模擬環境就緒。
  - `prepare_job(job_dir, config)`：在沙盒 `workspace/` 中自動建立仿真輸入腳本（`.wbjn` / `.k` / `.py`）。
  - `launch(job_dir, input_file)`：啟動虛擬子進程或虛擬線程，模擬求解進度。
  - `parse_progress(job_dir)`：從沙盒日誌讀取並換算進度百分比與殘差。
  - `abort(proc)`：優雅終止虛擬進程，支援 SIGTERM 模擬。
  - `extract_results(job_dir)`：合成高保真 `summary.json`、白底雲圖 PNG 與 `overview.html`。

---

## 五、 三大端到端驗收場景規格 (3 Synthetic E2E Scenarios)

### 5.1 場景一：隨機振動模態質量不足 (<90%) 觸發 Pre-flight 阻斷並輸出處方箋
- **工況類型**：Random Vibration (PSD 分析)。
- **觸發條件**：前置模態分析提取 10 階，有效模態質量比 $X=82.4\%, Y=85.1\%, Z=79.3\%$（任一向 $< 90\%$），且截斷頻率 $1850\text{ Hz} < 1.5 \times 2000\text{ Hz} = 3000\text{ Hz}$。
- **預期行為**：
  1. `PreFlightGatekeeper` 立即攔截，強制拒絕建立 PSD 求解任務。
  2. 作業狀態保持為 `REJECTED` 或引發 `PreFlightGatekeeperError`。
  3. 產出結構化自愈處方箋 JSON：
     - 規則代碼：`GATE-VIB-001` (或 `PHYS-001-MASS-DEFICIENT`)。
     - 嚴重度：`FATAL` / `BLOCKING`。
     - 診斷：指出 X/Y/Z 累積質量不足與截斷頻率缺口。
     - 具體修復建議：建議階數提高至 35~60 階以上，或設定截斷頻率 $\ge 3000\text{ Hz}$。

### 5.2 場景二：落摔衝擊沙漏能超標 (>5%) 觸發 Watchdog 早期熔斷中斷求解
- **工況類型**：Explicit Dynamics (LS-DYNA 落摔衝擊)。
- **觸發條件**：求解至 $t=0.0035\text{ s}$ 時，碰撞引發嚴重零能模式，沙漏能 $E_{\text{hg}} = 62.0\text{ J}$，總能量 $E_{\text{total}} = 932.0\text{ J}$，沙漏比率達 $6.65\% > 5.0\%$。
- **預期行為**：
  1. `WatchdogSentinel` 即時匹配到 `glstat` 日誌中的能量數據。
  2. 立即觸發早期熔斷機制（Circuit Breaker），向求解器進程發送終止信號。
  3. 作業狀態轉移為 `ABORTED`，終止原因標記為 `HOURGLASS_EXCEEDED`。
  4. 沙盒生成 `summary.json` 標記 `verdict: FAIL`、`hourglass_ratio: 0.0665`。
  5. 自愈處方箋建議：切換為全積分單元 (`ELFORM=2`) 或調整沙漏阻尼黏性係數 (`IHQ=4/6`)。

### 5.3 場景三：熱翹曲工作流 Cell Link 成功串接並輸出 overview.html 與 summary.json
- **工況類型**：Steady-State Thermal -> Static Structural 熱-結構單向序列耦合翹曲分析。
- **觸發條件**：回流焊冷卻工況 ($260^\circ\text{C} \to 25^\circ\text{C}$)，無應力參考溫度 $T_{\text{ref}} = 260^\circ\text{C}$，3-2-1 靜定支承。
- **預期行為**：
  1. `WorkbenchCellLinkEngine` 生成原生 `.wbjn` 腳本，包含 `Solution` 至 `Setup` 的 `TransferData` 原生單元鏈結。
  2. 求解完成後提取最大等效應力 $\sigma_{\max} = 94.2\text{ MPa} < 180\text{ MPa}$，Z 軸翹曲 $U_z = 0.128\text{ mm} \le 0.150\text{ mm}$。
  3. 三位一體標準產出完整生成：
     - `artifacts/summary.json`：符合 Pydantic 模型，`verdict: PASS`。
     - `artifacts/overview.html`：免外網連線、零 CDN 依賴，包含綠色 PASS 徽章、內嵌 SVG 圖表與雲圖預覽。
     - `artifacts/images/`：包含白底高解析度等效應力雲圖與翹曲雲圖 PNG。
