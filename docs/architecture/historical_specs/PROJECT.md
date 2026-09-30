# Project: ANSYS Unified MCP 2.0 全域架構重塑

## Architecture
- **核心架構願景**：
  以林明志專家教學的系統級架構為標竿，建立「模擬作業生命週期與沙盒目錄隔離、非同步求解作業排程、實時物理守護與早期熔斷、Workbench 原生拓撲單元直通、求解前置物理安全閘門與自愈處方箋、自包含互動式 HTML 儀表板」之六大核心架構閉環。
- **架構分層原則**：
  1. **Job 沙盒隔離層 (`jobs/`)**：每次模擬產生 `jobs/{timestamp}_{analysis_type}_{tag}/`，原始資產絕對唯讀，產生 `summary.json`、白底雲圖 PNG、`overview.html` 三位一體標準產物。
  2. **非同步守護層 (`core/sentinel/`)**：提供非阻塞式排程介面 (`submit_simulation_job`, `get_simulation_status`, `tail_simulation_log`, `abort_simulation_job`)，後台守護線程 Watchdog 實時正則解析求解日誌，偵測沙漏能 > 5%、質量縮放失控、殘差 NaN/Inf 時早期熔斷。
  3. **驅動與拓撲層 (`drivers/` & `workflows/`)**：以 `BaseSolverDriver` 統一 Mechanical, LSDyna, Optislang, SpaceClaim, Fluent, Icepak 抽象；`workbench_links.py` 透過 RunWB2 原生 Journal 生成原生單元鏈結；頂層封裝 5 大高階工況 Intent Workflows (`run_drop_test`, `run_shock_analysis`, `run_random_vibration`, `run_thermal_warpage`, `train_surrogate_model`)。
  4. **前置安全閘門層 (`gatekeeper/`)**：硬性物理阻斷檢核（振動有效質量 >= 90%、截斷頻率 1.5x、落摔初速方向/接觸/時間步、熱翹曲 CTE/$T_{ref}$、單位制一致性），阻斷時回傳標準 JSON 自愈處方箋。
  5. **報告合成層 (`reporting/`)**：合成免伺服器、零外網 CDN、純原生 SVG/Canvas 渲染之自包含互動式 `overview.html` 儀表板、KPI 指標卡與 Markdown 對話摘要。
  6. **端到端測試軌道 (`tests/`)**：4-Tier 測試覆蓋矩陣，支援 100% 免商業 License 離線 Mock 驗證，並涵蓋 3 大典型驗收場景。

---

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1.1 | JobManager 沙盒管理 | 在 `jobs/{timestamp}_{analysis_type}_{tag}/` 建立獨立結構（`inputs/`, `workspace/`, `artifacts/`）與狀態追蹤 | M1 | R1, Survey |
| F1.2 | 原始資產唯讀保護 | 原始 CAD 模型（PMDB/STEP/SCDOC）、材料庫 XML、基礎模板設置唯讀屬性，禁止求解污染 | M1 | R1, Survey |
| F1.3 | 標準交付物矩陣 | 規範 `summary.json` Schema、1920x1080 白底雲圖規格與沙盒生命週期收斂機制 | M1 | R1, Survey |
| F2.1 | 非同步排程 MCP 工具 | 實裝 `submit_simulation_job`, `get_simulation_status`, `tail_simulation_log`, `abort_simulation_job` 與五態狀態機 | M2 | R2, Survey |
| F2.2 | 實時日誌 Watchdog | 後台守護線程解析 `solve.out`, `glstat`, `fluent.log`, `matter.out`，即時換算進度百分比、時間步與殘差 | M2 | R2, Survey |
| F2.3 | 早期發散物理熔斷 | 沙漏能比例 > 5%、質量縮放 > 5%、殘差 NaN/Inf 或負滑移能時主動中止求解，節省算力 | M2 | R2, Survey |
| F3.1 | BaseSolverDriver 抽象 | 建立統一求解器驅動抽象基類，標準化 setup, solve, monitor, extract_results 介面 | M3 | R3, Survey |
| F3.2 | 求解器驅動具象化 | 實裝/重構 MechanicalDriver, LSDynaDriver, OptislangDriver, SpaceClaimDriver, FluentDriver, IcepakDriver | M3 | R3, Survey |
| F3.3 | Workbench 原生單元鏈結 | 實裝 `workbench_links.py`，透過 RunWB2 原生 Journal 生成熱-結構、模態-振動、參數-optiSLang TransferData 鏈結 | M3 | R3, Survey |
| F3.4 | 5 大高階工況工作流 | 實裝 `run_drop_test`, `run_shock_analysis`, `run_random_vibration`, `run_thermal_warpage`, `train_surrogate_model` | M3 | R3, Survey |
| F4.1 | 物理前置硬性阻斷矩陣 | 實裝振動有效質量 >= 90%、落摔初速度方向/CFL 時間步、熱翹曲 CTE/$T_{ref}$、長度-質量-時間單位制嚴格校驗 | M4 | R4, Survey |
| F4.2 | 結構化 JSON 自愈處方箋 | 阻斷時回傳標準錯誤碼（如 `PHYS-001-MASS-DEFICIENT`）與具體修復處方引導，未達標嚴禁送算 | M4 | R4, Survey |
| F5.1 | 報告合成器 | 自動掃描沙盒產物與 `summary.json`，合成自包含單一檔案 `overview.html` | M5 | R5, Survey |
| F5.2 | 免外網純原生 SVG/Canvas 渲染 | 輕量化渲染 PSD 頻響曲線、落摔衝擊歷程、optiSLang 響應面雲圖與 KPI 卡片 | M5 | R5, Survey |
| F5.3 | 對話引用 Markdown 摘要 | 自動提取關鍵指標生成精簡 Markdown 片段供 AI 於對話中直接回覆使用者 | M5 | R5, Survey |
| F-E2E.1 | 測試架構與高保真 Mocking | 建立 `TEST_INFRA.md` 與 `MockLogStreamer`，達成 100% 免商業 License 離線測試 | E2E | Criteria, Survey |
| F-E2E.2 | 4-Tier 測試套件與三大場景 | 實裝 Tier 1~4 測試（含隨機振動阻斷處方箋、落摔沙漏超標熔斷、熱翹曲 Cell Link 成功閉環三大端到端場景） | E2E | Criteria, Survey |

---

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Job 沙盒生命週期與成果矩陣 | F1.1, F1.2, F1.3 | none | DONE |
| M4 | 求解前置安全閘門與自愈處方箋 | F4.1, F4.2 | none | DONE |
| M2 | 非同步排程與實時物理守護 | F2.1, F2.2, F2.3 | M1 | DONE |
| M5 | 自包含互動式 HTML 儀表板與報告合成器 | F5.1, F5.2, F5.3 | M1 | DONE |
| M3 | 統一驅動層、Workbench 單元鏈結與 5 大高階工況 | F3.1, F3.2, F3.3, F3.4 | M1, M2, M4, M5 | IN_PROGRESS |
| E2E | 端到端測試套件與三大典型場景驗證 | F-E2E.1, F-E2E.2 | M1, M2, M3, M4, M5 | IN_PROGRESS |

---

## Interface Contracts

### 1. JobManager 介面合約 (`src/ansys_unified_mcp/jobs/`)
```python
class JobSandbox:
    job_id: str
    sandbox_dir: Path        # jobs/{timestamp}_{analysis_type}_{tag}/
    inputs_dir: Path         # 唯讀輸入資源放置處
    workspace_dir: Path      # 求解器工作目錄
    artifacts_dir: Path      # 產出物收集處
    
    def protect_read_only(self, path: Path) -> None: ...
    def write_summary(self, summary: SimulationSummary) -> Path: ...
```

### 2. Async Sentinel & Watchdog 介面合約 (`src/ansys_unified_mcp/core/sentinel/`)
```python
class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SOLVED = "SOLVED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"

class SentinelQueue:
    def submit_job(self, workflow_type: str, config: dict) -> JobSubmissionResult: ...
    def get_status(self, job_id: str) -> JobStatusResponse: ...
    def tail_log(self, job_id: str, lines: int = 50) -> LogTailResponse: ...
    def abort_job(self, job_id: str) -> AbortResult: ...

class WatchdogDaemon:
    def register_job(self, job_id: str, log_path: Path, solver_type: str) -> None: ...
    def check_divergence(self, metrics: LogMetrics) -> DivergenceVerdict: ...
```

### 3. Pre-Flight Gatekeeper 介面合約 (`src/ansys_unified_mcp/gatekeeper/`)
```python
class GatekeeperVerdict:
    passed: bool
    violations: list[GateViolation]
    prescription: Optional[PrescriptionReport]

class PreFlightGatekeeper:
    def verify(self, workflow_type: str, params: dict) -> GatekeeperVerdict: ...
```

### 4. BaseSolverDriver 抽象基類合約 (`src/ansys_unified_mcp/drivers/`)
```python
class BaseSolverDriver(ABC):
    @abstractmethod
    def prepare_environment(self, sandbox: JobSandbox, config: dict) -> None: ...
    
    @abstractmethod
    def run_solver(self, sandbox: JobSandbox, is_async: bool = True) -> Any: ...
    
    @abstractmethod
    def get_log_file_path(self, sandbox: JobSandbox) -> Path: ...
    
    @abstractmethod
    def extract_artifacts(self, sandbox: JobSandbox) -> SimulationSummary: ...
```

### 5. ReportGenerator 介面合約 (`src/ansys_unified_mcp/reporting/`)
```python
class ReportGenerator:
    def generate_html_dashboard(self, sandbox: JobSandbox, summary: SimulationSummary) -> Path: ...
    def generate_dialog_summary(self, summary: SimulationSummary) -> str: ...
```

---

## Code Layout
```text
src/ansys_unified_mcp/
├── __init__.py
├── __main__.py
├── server.py
├── config.py
├── jobs/                         # R1: 模擬作業生命週期與沙盒管理器
│   ├── __init__.py
│   ├── manager.py
│   ├── sandbox.py
│   └── models.py
├── core/
│   ├── timeout.py
│   └── sentinel/                 # R2: 非同步作業排程與 Watchdog 守護進程
│       ├── __init__.py
│       ├── daemon.py
│       ├── queue.py
│       ├── watchdog.py
│       ├── circuit_breaker.py
│       └── parsers/
│           ├── __init__.py
│           ├── mechanical.py
│           ├── lsdyna.py
│           └── fluent.py
├── drivers/                      # R3: 統一求解器驅動層
│   ├── __init__.py
│   ├── base.py
│   ├── mechanical_driver.py
│   ├── lsdyna_driver.py
│   ├── optislang_driver.py
│   ├── spaceclaim_driver.py
│   ├── fluent_driver.py
│   └── icepak_driver.py
├── workflows/                    # R3: 高階工況工作流與 Workbench 單元鏈結
│   ├── __init__.py
│   ├── workbench_links.py
│   ├── drop_test.py
│   ├── shock_analysis.py
│   ├── random_vibration.py
│   ├── thermal_warpage.py
│   └── surrogate_model.py
├── gatekeeper/                   # R4: 求解前置安全閘門與自愈處方箋
│   ├── __init__.py
│   ├── gatekeeper.py
│   ├── prescription.py
│   └── rules/
│       ├── __init__.py
│       ├── vibration_rules.py
│       ├── drop_impact_rules.py
│       ├── thermal_rules.py
│       └── unit_consistency.py
├── reporting/                    # R5: 自包含 HTML 儀表板與報告合成器
│   ├── __init__.py
│   ├── generator.py
│   ├── charts.py
│   └── templates/
│       └── overview.html
└── tools/                        # MCP 系統工具註冊
    ├── __init__.py
    ├── sentinel_tools.py         # submit/status/tail/abort
    ├── intent_tools.py           # 5 大高階工況進入點
    ├── ... (既有工具保持向後相容)

tests/
├── conftest.py
├── unit/                         # Tier 2: 離線單元測試
│   ├── test_job_sandbox.py
│   ├── test_sentinel_watchdog.py
│   ├── test_base_drivers.py
│   ├── test_workbench_links.py
│   ├── test_preflight_gatekeeper.py
│   └── test_report_generator.py
└── e2e/                          # Tier 3: 三大高保真合成端到端場景
    ├── test_e2e_random_vibration_gate.py
    ├── test_e2e_drop_test_hourglass.py
    └── test_e2e_thermal_warpage_cell_link.py
```
