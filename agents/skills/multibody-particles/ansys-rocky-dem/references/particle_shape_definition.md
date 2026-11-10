# Rocky DEM 多面體顆粒形狀定義優勢

> [!NOTE]
> 本手冊依據官方知識字典 `rocky.md` 與 `rocky` 權威技術規格擴充，提供深度工程指導。

## 1. 原理與設定準則

本模組於高精度數值模擬時，必須遵循以下邊界設定與收斂規範：
- 數值精度與單位一致性：務必先確認全域坐標系統、材料參數庫與求解單位（MKS/SI）。
- 網格劃分策略：實施局部特徵網格加密，並於梯度變化劇烈區域進行自適應細化。
- 監控物理量：除了求解器預設殘差之外，必須定義面通量、力矩或特徵頻率等客觀物理監控器。

## 2. 核心規範與字典精要

# Ansys Rocky 與 PyRocky 知識字典

> 已核範圍以逐來源覆核紀錄與主題清冊為準；部分物理數值、版本相容與腳本行為尚未逐項查證，使用前請回查目標版本原文。

> 本主題深度剖析 Ansys Rocky 離散元模擬 (Discrete Element Method, DEM) 體系與現代化 Python 自動化介面。系統化梳理開源用戶端程式庫 `ansys-rocky-core` (PyRocky 0.6.2) 的遠端 RPC 架構、Pyro Proxy 生命週期與版本邊界；詳細拆解 PrePost Scripting 階層化物件路徑（從 `launch_rocky`、`client.api`、`RAProject`、`RAStudy` 到粒子/幾何/領域/求解器控制）；深入對比 PyRocky 與 Rocky 內嵌 Python Shell 的三大 API 核心差異（`GetTimeSet` 回傳型別、`GetCurve` 不相容改用 `GetNumpyCurve`、UI 互動 Modal Dialog 懸掛阻塞）；嚴格界定教學示範案例預設值與真實 DEM 散體物理驗證的工程邊界；並整合 v261 Solver SDK (C++/CUDA GPU) 自訂接觸模型與網格特徵函數 (Grid Functions) 提取規範。

---

## 領域架構圖 (Rocky DEM & PyRocky Automation Architecture)

```mermaid
flowchart TD
    subgraph PyRockyClient["1. 現代 Python 客戶端 (PyRocky SDK 0.6.2)"]
        LAUNCH["launch_rocky(headless=True, server_port=...)<br/>啟動 Rocky 後台進程並建立連線"]
        CLIENT["RockyClient & client.api<br/>Pyro RPC 遠端代理核心 (Per-Thread Proxy)<br/>自動搜尋 AWP_ROOT261 / ansys-tools-path"]
    end

    subgraph ObjectHierarchy["2. PrePost 階層化物件模型 (PrePost Object Hierarchy)"]
        APP["RockyApiApplication (client.api)<br/>CreateProject() | OpenProject() | SaveProject()"]
        PROJECT["RAProject 專案物件<br/>GetStudy() | GetProjectName()"]
        STUDY["RAStudy 模擬研究核心<br/>GetParticles() | GetGeometries() | GetDomainSettings()<br/>StartSimulation() | StopSimulation() | DeleteResults()"]
        ELEMENTS["離散元實體與邊界 (Entities & Boundaries)<br/>Particle Collection (形狀、粒徑分佈、進料口 Inlet)<br/>Wall & Motion Frame (旋轉、平移、振動運動)<br/>Contacts & Grid Functions (接觸應力、速度、質量流率)"]
    end

    subgraph Solvers["3. 求解運算核心 (DEM Solver Engines)"]
        CPU_SOLVER["Rocky CPU 多核心求解器<br/>多線程接觸搜尋與運動積分"]
        GPU_SOLVER["Rocky 多 GPU / CUDA 加速求解器<br/>數百萬多面體顆粒的高並行接觸力學"]
        SOLVER_SDK["v261 Solver SDK (C++ / CUDA Hooks)<br/>自訂顆粒破碎模型 | 非線性黏附力 | SPH 流體顆粒"]
    end

    subgraph Coupling["4. 多物理場雙向耦合 (Multiphysics Coupling)"]
        FLUENT_COUPLING["Fluent-Rocky 2-Way Coupling<br/>RAFluentTwoWayCoupling (顆粒-流體曳力與傳熱)"]
        MECH_COUPLING["Mechanical 瞬態動力學耦合<br/>表面磨損 (Archard Wear) 與顆粒衝擊載荷"]
    end

    LAUNCH --> CLIENT
    CLIENT --> APP
    APP --> PROJECT
    PROJECT --> STUDY
    STUDY --> ELEMENTS

    STUDY --> CPU_SOLVER
    STUDY --> GPU_SOLVER
    SOLVER_SDK -.-> GPU_SOLVER

    ELEMENTS --> FLUENT_COUPLING
    ELEMENTS --> MECH_COUPLING
```

---

## 主題辭典與核心模組

### 1. PyRocky SDK 與產品版本 (PyRocky SDK Architecture & Version Matrix)

#### 核心概念與辭典定義 (Core Concepts & Glossaries)
- **PyRocky 架構定位**：
  - `ansys-rocky-core` (SDK 0.6.2) 是 Ansys 官方提供的開源 Python 用戶端，允許工程師在標準外部 CPython (3.10~3.12) 環境中透過 RPC (Remote Procedure Call) 協定遠端操控 Rocky 離散元模擬軟體。
  - **通訊核心與執行緒模型**：PyRocky 底層採用 Pyro5 RPC 機制。每個存取 `client.api` 的執行緒會建立專屬的連線 Proxy；當執行緒結束或 Client 物件被記憶體回收時自動釋放連線資源。
- **啟動參數管線 (`launch_rocky`)**：
  - `rocky_exe` / `rocky_version`：可明確指定可執行檔路徑或版本字串；未指定時自動依據環境變數（如 `AWP_ROOT261`）定位本機最新安裝版本。
  - `headless=True`：預設以無介面模式啟動，適合叢集運算與背景批次排程；若設定 `headless=False` 則拉起桌面 GUI 視窗。
  - `server_port`：指定 RPC 監聽連接埠；搭配 `close_existing=True` 可強制關閉該端口上殘留的無效工作階段。
  - `connect_timeout`：連線交握逾時秒數（預設為等待至伺服器就緒）。
- **版本相容性邊界**：
  - SDK 常數宣告 `MINIMUM_ANSYS_VERSION_SUPPORTED = 242`，確認 PyRocky 最低相容版本為 Ansys 2024 R2 (v242)，並完整支援 v251、v252 及 2026 R1 (`v261`)。

#### 手冊章節與規格出處 (Manual & Doc Citations)
- **官方手冊**：*PyRocky User Guide & API Reference (0.6.2)* (**Launcher API**), (**RockyClient Reference**), (**Documentation Index**)
- **Source IDs**：`sources.csv#ansys_a50faf6addc305baac4816cc`, `sources.csv#ansys_1a6a96298fcdc4e3c58f532f`, `ansys_57b182fd93c561ed71dcbc03`, `ansys_bb5f3bd1abb7f4c23e726457`.

---

### 2. PyRocky PrePost Scripting 物件路徑 (PrePost Object Hierarchy & Workflow)

#### 核心概念與辭典定義 (Core Concepts & Glossaries)
- **階層化物件模型結構 (Hierarchy Tree)**：
  - `RockyClient.api` (`RockyApiApplication`)：所有專案層級操作的頂層入口。
  - **專案管理層 (`RAProject`)**：
    - `CreateProject()`：初始化空白專案；
    - `OpenProject(filename)`：載入既有 `.rocky` 專案檔；
    - `SaveProject(filename=None)`：存檔，傳入 `None` 則直接覆寫當前檔案；
    - `CloseProject(check_save_state=False)`：關閉專案，可選擇跳過存檔確認。
  - **研究運算層 (`RAStudy`)**：
    - 透過 `project.GetStudy()` 取得模擬實體控制器。
    - **幾何與顆粒集合**：`study.CreateParticle()` 建立自訂形狀（多面體、圓柱體、球體）與粒徑篩分分佈 (Sieve Size Distribution)；`study.ImportWall(filename)` 匯入 STL/CAD 壁面幾何。
    - **進料與運動**：`study.CreateCircularSurface()` 配合 `study.CreateParticleInlet()` 設定連續進料；透過 `study.GetMotionFrameSource().NewFrame()` 與 `AddRotationMotion()` 指派壁面旋轉或振動。
    - **計算域與求解調度**：`study.GetDomainSettings().SetCoordinateLimitsMaxValues(...)` 劃分計算邊界；`study.SetSimulationDuration(seconds)` 設定模擬時長；`study.StartSimulation()` 啟動求解運算。

#### 手冊章節與規格出處 (Manual & Doc Citations)
- **手冊出處**：*PyRocky User Guide & Basic PrePost Usage* (**RockyApiApplication**), (**RAStudy Reference**)
- **Source IDs**：`sources.csv#ansys_1a6a96298fcdc4e3c58f532f`, `ansys_cea7d8b0356558b526dd3f38`, `ansys_30c34b95ebb62b049ac76220`.

---

### 3. PyRocky 與內建 shell 的 API 差異 (API Divergences & RPC Boundary)

#### 核心概念與辭典定義 (Core Concepts & Glossaries)
- **遠端 RPC vs 原生直譯器執行環境差異**：
  - Rocky 桌面軟體內部內建了嵌入式 Python Shell，可直接存取記憶體中的 C++ 物件指標；而 PyRocky 是透過網路 RPC 呼叫操作遠端物件代理，因此在資料型別與同步機制上存在三大核心差異：
- **三大核心介面差異**：
  1. **`GetTimeSet()` 回傳型別差異**：
     - 在 Rocky 內嵌 Shell 中，`study.GetTimeSet()` 回傳原生的 `TimeSet` 集合物件；
     - 在 PyRocky 客戶端中，`study.GetTimeSet()` 被封裝並回傳**以秒為單位的標準 NumPy 1D 浮點數陣列**，更利於數值運算與 Matplotlib 繪圖。
  2. **`GetCurve()` 不受支援，強制改用 `GetNumpyCurve()`**：
     - 內嵌環境下的 UI 視覺化曲線物件 `KAElementItem.GetCurve()` 無法跨網路序列化傳輸；
     - PyRocky 必須改用 `study.GetParticles().GetNumpyCurve(curve_name, unit="...")`，直接回傳包含時間軸與物理量數值的二元 NumPy 陣列 `(times, values)`。
  3. **非無頭模式下 UI 互動 Modal Dialog 的掛起阻塞風險**：
     - 在非無頭模式 (`headless=False`) 下呼叫 `CloseProject()` 或遇到未處理例外時，桌面 GUI 會彈出「是否儲存變更」的確認對話方塊。由於 PyRocky 無法透過遠端 RPC 模擬點擊該視窗按鈕，Python 腳本將在 `CloseProject()` 呼叫處陷入永久死鎖（Hang）。
     - **工程防禦準則**：無人值守腳本必須設定 `headless=True`，或調用 `CloseProject(check_save_state=False)` 明確略過互動詢問。

#### 手冊章節與規格出處 (Manual & Doc Citations)
- **手冊出處**：*PyRocky User Guide — Differences with Rocky In-App Shell* (**User Guide**)
- **Source IDs**：`sources.csv#ansys_1a6a96298fcdc4e3c58f532f`.

---

### 4. 案例預設值與結果解讀邊界 (Tutorial Presets vs Physics Validation)

#### 核心概念與辭典定義 (Core Concepts & Glossaries)
- **教學示範預設值 (Tutorial Presets)**：
  - 官方教學範例（如 `minimal.py` 單純粒子下落、`particle_wall_interaction_with_motion.py` 旋轉 L 型管）為了讓使用者能在一般個人電腦上於數秒內快速重現計算流程，預設採用極端簡化的數值參數：
    - 單一球體粒子，篩分粒徑高達 $0.1\text{ m}$ (10 公分直徑)；
    - 簡化接觸力學參數（楊氏模數通常設為 $1\times 10^7\text{ Pa}$，遠低於真實鋼材 $2\times 10^{11}\text{ Pa}$）；
    - 粗糙的壁面三角形網格與僅 $2\sim 5\text{ 秒}$ 的模擬時長。
- **物理正確性與結果解讀邊界 (Physical Validation Boundaries)**：
  - **數值教學不等於物理驗收**：教學案例輸出的粒子累積數（如 28 顆）、質量流率及極值速度（$0.5\text{ m/s}$），僅供驗證代碼是否正常跑通，**絕不能直接外推為工業級散體物理行為或篩分設備設計依據**。
  - **時間步長雷利準則 (Rayleigh Time Step Criterion)**：
    - 真實 DEM 模擬中，數值積分時間步長必須小於雷利波在顆粒內傳播時間的臨界上限（$\Delta t \le 0.2 \Delta t_{Rayleigh} = \frac{\pi R}{0.1631 \nu + 0.8766} \sqrt{\frac{\rho}{G}}$）。教學案例常藉由人為降低楊氏模數來放大時間步長（如 $\Delta t = 10^{-3}\text{ s}$）；若直接將真實鋼材高剛度代入同一時間步，求解器將發生嚴重顆粒重疊穿透與數值爆炸。
  - **宏觀散體標定要求 (Bulk Calibration Requirement)**：
    - 真實工程應用中，顆粒間摩擦係數、滾動阻力係數 (Rolling Resistance) 與恢復係數 (COR) 必須透過安息角實驗 (Angle of Repose) 或直剪試驗 (Direct Shear Test) 進行多輪反演標定，方能具備工程可信度。

#### 手冊章節與規格出處 (Manual & Doc Citations)
- **教學手冊出處**：*Simple Particle Simulation Tutorial* (**minimal.html**), *Moving Wall Particle Interaction* (**moving_wall.md**)
- **Source IDs**：`sources.csv#ansys_65546f1b6ce2745e4ba9b6f6`, `sources.csv#ansys_0708440aef97238120ff1a91`.

#### 雙軌介面與 API 特性對照矩陣 (Rocky Interface Comparison Matrix)

| 特性維度 | Rocky In-App Python Shell | PyRocky (`ansys-rocky-core 0.6.2`) |
|---|---|---|
| **直譯器架構** | Rocky 內建 Python 直譯器 | 標準外部 CPython (3.10 ~ 3.12) |
| **通訊與傳輸** | 記憶體內部直接存取 (In-Process) | Pyro5 RPC 網路遠端連線 (Out-of-Process) |
| **`GetTimeSet` 型別** | 原生 `TimeSet` 物件 | NumPy 1D 浮點數陣列（單位：秒） |
| **曲線擷取** | `KAElementItem.GetCurve()` | `study.GetParticles().GetNumpyCurve()` |
| **UI 對話框處理** | 人工點擊 GUI 對話框 | 無法處理彈出對話框；強烈建議 `headless=True` |
| **執行緒模型** | 單主執行緒 | 每個存取 Thread 自動建立獨立 Pyro Proxy |

#### Python 腳本範例：PyRocky 批次模擬與結果萃取 (Python Scripting Example)

```python
import os
import tempfile
import ansys.rocky.core as pyrocky

# 1. Prepare temporary directory and launch Rocky in headless mode
temp_dir = tempfile.mkdtemp(prefix="rocky_sim_")
print(f"Temporary simulation directory: {temp_dir}")

# Launch Rocky backend via Pyro RPC
rocky = pyrocky.launch_rocky(

## 3. 常見陷阱與防呆措施

1. **未定義求解範圍**：求解前未限定掃頻範圍或時間步長，導致求解發散。
2. **材料模型失配**：非線性材料未設定適當的切線模數或溫度相依曲線。
3. **介面通訊失敗**：多物理場耦合未對齊變數傳遞單位，導致數值非物理震盪。
