# PyAnsys 對應、MCP 現況與後續規劃

> 本檔記錄：①PyAnsys 安裝現況（`.venv` 與全域 3.14）②圖片中 Workbench/授權模組 ↔ 官方 pyansys 套件 ↔ 官方 MCP ↔ 是否已安裝 的對照 ③專案後續規劃 roadmap ④如何驗證 PyWorkbench 連線。
> 來源：pyansys metapackage README（https://github.com/ansys/pyansys）。與 `context.md`（心智模型）、`ARCHITECTURE.md`（程式慣例）並列。

## 1. 安裝現況（兩個環境）

> 重點：MCP server 跑在專案 `.venv`，**只有 `.venv` 內的套件對 MCP 可見**；全域 Python 3.14 供你一般 scripting，MCP 不使用。

### 1a. `.venv`（MCP runtime）
- `pyansys` metapackage：未安裝（採個別安裝）。
- 已安裝核心庫：
  - `ansys-mechanical-core` 0.13.0（PyMechanical）
  - `ansys-geometry-core` 0.16.3（PyAnsys Geometry）
  - `ansys-fluent-core` 0.40.2（PyFluent）
  - `ansys-optislang-core` 1.5.0（PyOptislang）
  - **`ansys-workbench-core` 0.14.0（PyWorkbench）— 新增，供 MCP 用** ✅
  - 輔助：`ansys-pythonnet`（embedded 必需）、`ansys-tools-common`、`ansys-units`、各 `ansys-api-*`
- `.venv` 尚未裝：`ansys-dyna-core`、`ansys-sherlock-core`、PyGranta、`ansys-mapdl-core`、`ansys-dpf-core`、`ansys-meshing-prime`、PyAEDT（Phase 2 再視需要加）。

### 1b. 全域（`C:\Python314`，user site）
- **`pyansys` 2026.1.3 完整堆疊已安裝** ✅：含 `ansys-workbench-core` 0.14.0、`ansys-dyna-core` 0.12.1、`ansys-sherlock-core` 1.0.2、`pygranta` 2026.1.1、`ansys-mapdl-core`、`ansys-dpf-core`、`ansys-meshing-prime`、`pyaedt` 等約 40 庫。
- 供全域 Python 3.14 一般 scripting；**MCP 不使用全域**。

### 官方 MCP
- 皆未安裝（`ansys-common-mcp`、`ansys-mapdl-mcp`、PyMechanical/PyFluent/PyCFX/PyAEDT/PyLumerical MCP）。

> 官方目前有 MCP 的 6 個產品：Mechanical、MAPDL、Fluent、CFX、AEDT、Lumerical。

## 2. 模組 ↔ 套件 ↔ 官方 MCP ↔ 安裝

圖例：✅ 有／已裝　❌ 無／未裝　⚠️ 部分

### A. Workbench — Analysis Systems

| 分析系統 | pyansys 套件 | 官方 MCP? | 已安裝? |
|---|---|---|---|
| Static/Transient Structural、Steady/Transient Thermal、Modal、Harmonic Response、Random Vibration、Response Spectrum、Rigid Dynamics、Buckling、Electric、Coupled Field、Structural Optimization、Substructure、Acoustics、Explicit Dynamics(設定) | PyMechanical | ✅ PyMechanical MCP | ✅ |
| Fluid Flow (Fluent / Fluent Meshing / Materials Processing) | PyFluent | ✅ PyFluent MCP | ✅ |
| Fluid Flow (CFX) | PyCFX | ✅ PyCFX MCP | ❌ |
| Turbomachinery Fluid Flow | PyFluent/PyCFX + PyTurboGrid | ⚠️ 部分 | ⚠️（Fluent 已裝） |
| LS-DYNA / Acoustics / Restart | PyDYNA | ❌ | ❌ |
| Speos | PySpeos | ❌ | ❌ |
| Polyflow | ❌ 無套件 | ❌ | ❌ |
| Hydrodynamic (Aqwa) | ❌ 無套件 | ❌ | ❌ |

### B. Workbench — Component Systems

| 元件系統 | pyansys 套件 | 官方 MCP? | 已安裝? |
|---|---|---|---|
| Mechanical Model | PyMechanical | ✅ PyMechanical MCP | ✅ |
| Mechanical APDL | PyMAPDL | ✅ PyMAPDL MCP | ❌ |
| Fluent（各版本） | PyFluent | ✅ PyFluent MCP | ✅ |
| CFX、CFX (Beta) | PyCFX | ✅ PyCFX MCP | ❌ |
| Icepak | PyAEDT | ✅ PyAEDT MCP | ❌ |
| Geometry、Discovery | PyAnsys Geometry | ❌ | ✅ |
| Mesh | PyPrimeMesh | ❌ | ❌ |
| ACP (Pre/Post) | PyACP | ❌ | ❌ |
| Chemkin | PyChemkin | ❌ | ❌ |
| Granta MI | PyGranta | ❌ | ❌ |
| Sherlock (Pre/Post) | PySherlock | ❌ | ❌ |
| System Coupling | PySystemCoupling | ❌ | ❌ |
| TurboGrid | PyTurboGrid | ❌ | ❌ |
| Results（CFD-Post 類） | PyDPF + PyEnSight | ❌ | ❌ |
| Engineering Data | PyMechanical(指派) / PyGranta(庫) / PyMaterials Manager | ❌ | ⚠️（Mechanical 已裝） |
| Autodyn、BladeBuilder、ICEM CFD、Forte、Polyflow、Material Designer、Injection Molding、External Data/Model、Granta Selector、MS Excel | ❌ 無套件 | ❌ | ❌ |

### C. Workbench — Custom Systems

| Custom System | pyansys 套件 | 官方 MCP? | 已安裝? |
|---|---|---|---|
| AM DED / AM LPBF (Inherent Strain / Thermal-Structural) | PyAdditive + PyMechanical | ⚠️ 部分 | ⚠️（Mechanical 已裝，Additive 未裝） |
| FSI: Fluid Flow (CFX/FLUENT) → Static Structural | PySystemCoupling + PyFluent/PyCFX + PyMechanical | ⚠️ 部分 | ⚠️（Fluent/Mechanical 已裝，SystemCoupling 未裝） |
| Pre-Stress Modal、Random Vibration、Response Spectrum、Thermal-Stress | PyMechanical | ✅ PyMechanical MCP | ✅ |

### D. Workbench — Design Exploration

| 項目 | pyansys 套件 | 官方 MCP? | 已安裝? |
|---|---|---|---|
| Direct Optimization、Parameters Correlation、Response Surface (Optimization) | PyOptislang / PyWorkbench | ❌ | ⚠️（optiSLang 已裝，Workbench 未裝） |
| 3D ROM | PyTwin（鬆散對應） | ❌ | ❌ |

### E. Ansys Module for license statistics

| 授權模組 | pyansys 套件 | 官方 MCP? | 已安裝? |
|---|---|---|---|
| Mechanical | PyMechanical | ✅ PyMechanical MCP | ✅ |
| CFD（Fluent/CFX） | PyFluent / PyCFX | ✅ PyFluent/PyCFX MCP | ⚠️（Fluent 已裝） |
| HFSS、Maxwell、ICEPAK、Electronics | PyAEDT | ✅ PyAEDT MCP | ❌ |
| SiWave | PyEDB / PyAEDT | ✅ PyAEDT MCP | ❌ |
| Lumerical | PyLumerical | ✅ PyLumerical MCP | ❌ |
| LSDyna | PyDYNA | ❌ | ❌ |
| Optislang | PyOptislang | ❌ | ✅ |
| Sherlock | PySherlock | ❌ | ❌ |
| Granta | PyGranta | ❌ | ❌ |
| Discovery | PyAnsys Geometry | ❌ | ✅ |
| Speos | PySpeos | ❌ | ❌ |
| Designexplorer | PyOptislang / PyWorkbench | ❌ | ⚠️ |
| Aqwa、Autodyn、nCode、Material Designer、Zemax | ❌ 無套件 | ❌ | ❌ |

## 3. 關鍵決策紀錄

1. **庫層一律用官方 pyansys**：凡官方有庫的（Mechanical/Geometry/Fluent/optiSLang/LS-DYNA/Sherlock/Granta/Workbench…），不自行手刻。
2. **Workbench 手刻 bridge 降為 legacy，改用 PyWorkbench**：手刻 batch journal（`RunWB2 -B`）在收尾閃退（`0xC000013A`）、file-IPC bridge 曾 ping 逾時；PyWorkbench 走 client/server，對症「斷線/閃退」。
3. **穩定度排序（不斷線）**：PyMechanical embedded（無 socket，最穩）＞ PyMechanical/PyFluent remote gRPC（行程隔離、可見 GUI）＞ 手刻 file-IPC bridge ＞ batch journal（最不穩）。
4. **MCP 層自建於 `ansys-common-mcp` 官方框架**：繼承其 persistent Python session 與生命週期管理（對症穩定性），並可整合官方 PyMechanical/PyFluent MCP。unified MCP 的價值在跨產品編排 + workflow skills。
5. **Thermal / Model / Random Vibration / Response Spectrum 不是獨立庫**：皆為 Mechanical 分析類型，用 PyMechanical 操作即可。

## 4. 後續規劃 Roadmap

### Phase 0 — 決策與備份（✅ 完成）
- ✅ 重構已備份到分支 `refactor/unified-arch`（commit `b00c433`），併入遠端 `941314b`（merge `6b6d9d0`）。
- ✅ 對應盤點與決策紀錄（本檔），commit `64a1da2`。

### Phase 1 — 穩定化 Workbench 層（對症斷線/閃退）（🔧 進行中）
- ✅ 安裝 `ansys-workbench-core` 0.14.0 到 `.venv`（供 MCP）；全域另裝完整 `pyansys` 2026.1.3。
- ✅ 新增 PyWorkbench 通道（**附 fallback、標記 UNVERIFIED**）：
  - `products/workbench.py`：`WorkbenchController`（`connect`/`launch`/`run_script`/`run_script_file`/`start_mechanical_server`/`upload_file`/`download_project_archive`/`disconnect`/`status`，走 `SessionRegistry`）。
  - `tools/workbench_pyworkbench.py`：8 個 additive 工具（`workbench_launch_server`/`connect_server`/`run_script_live`/`start_mechanical_server`/`upload_file`/`download_archive`/`disconnect_server`/`server_status`）。
  - `__main__.py` 註冊新模組；舊 file-IPC bridge 與 batch launcher **保留為 fallback，未動**。
- ⏳ **待驗證**（見第 5 節）：實機確認 PyWorkbench 連得上、穩定不斷線。驗證前程式碼維持 UNVERIFIED 標記。
- ⏳ 驗證通過後才做：移除舊 file-IPC bridge、改寫既有 31 個 bridge 工具；無悔清理（`bridges/workbench_bridge.py`→`job_launcher.py` 改名、清 `tools/` 殘留執行期資料、佔位檔歸位）。
  （原「核心+清理」#2/#3 深修手刻 bridge 不再單獨做，隨 PyWorkbench 落地一併處理。）

### Phase 2 — 補齊產品庫與分層對稱
- 安裝缺的官方庫：`ansys-dyna-core`(LS-DYNA)、`ansys-sherlock-core`(Sherlock)、PyGranta(Granta/材料)，視需要 `ansys-dpf-core`(後處理)、`ansys-meshing-prime`(Mesh)。
- 分層收斂（對齊 `ARCHITECTURE.md` 目標形態，`tools/<product>.py` + `products/<product>.py` 成對）：
  - Fluent：`drivers/sim_impl.py` → `products/fluent.py`
  - SpaceClaim(geometry)：從 `tools/sim_tools.py` 拆出 → `products/geometry.py`
  - 新增 `products/dyna.py`、`products/sherlock.py`、`products/granta.py` + 對應 tools。

### Phase 3 — 對齊官方 MCP 框架 + workflow skills
- 評估將 unified MCP 建於 `ansys-common-mcp`（或整合官方 PyMechanical/PyFluent MCP 為子能力）。
- 把常用多步流程寫成 workflow skills（每個附客觀驗證條件）：
  - 幾何 → Engineering Data(材料) → 網格 → 邊界 → 求解 → 後處理
  - Modal → Random Vibration / Response Spectrum（連結相依分析）
  - Thermal-Stress、FSI(Fluent/CFX → Static Structural) 耦合
  - LS-DYNA 顯式流程、Sherlock 可靠度交接、optiSLang 參數化

### Phase 4 — 驗證與文件
- 補 `core/`、連線層的冒煙測試（目前無覆蓋）。
- 擴充 docs 索引到全五產品（Fluent / SpaceClaim / LS-DYNA 待補）。
- 每個 workflow skill 附驗證條件與範例。

## 5. 如何驗證 PyWorkbench 連線（UNVERIFIED → 驗證）

> PyWorkbench 通道目前標記 **UNVERIFIED**——程式碼寫好但尚未實機連線。以下是驗證方式與「連上 vs 沒連上」判讀。**這些步驟會啟動 Workbench server（屬連線動作）**，由你決定何時執行。

### 5.1 前置檢查
- `.venv` 有 PyWorkbench：`.venv\Scripts\python.exe -m pip show ansys-workbench-core`（應為 0.14.0）。
- 本機已安裝且可授權 Ansys Workbench（PyWorkbench 需在有 WB 的機器啟動 server）。

### 5.2 方式 A：直接用 PyWorkbench（.venv）
無副作用冒煙測試（只探測 template，不建系統、不求解）：

```python
from ansys.workbench.core import launch_workbench
wb = launch_workbench(show_gui=True)          # 啟動 WB server + client（連線動作）
print("server_version:", wb.server_version)   # 有版本字串 = 連上了
print(wb.run_script_string(
    "import json\n"
    "tpl = GetTemplate(TemplateName='Static Structural', Solver='ANSYS')\n"
    "wb_script_result = json.dumps({'template': str(tpl)})"))
wb.exit()                                     # 關閉 server（PyWorkbench 慣例）
```

### 5.3 方式 B：透過本專案的 MCP 工具
1. `workbench_launch_server`（或對已開的 server 用 `workbench_connect_server(port=...)`）→ 回 `{"ok": true, "key": ..., "server_version": ...}` 即連上。
2. `workbench_server_status` → `{"connected": true, "sessions": [...], "current": ...}`。
3. `workbench_run_script_live(script="import json\nwb_script_result=json.dumps({'ping':1})")` → 回 `{"ok": true, "output": ...}`。
4. `workbench_disconnect_server` 結束（只離線，不關 server）。

### 5.4 連上 vs 沒連上 判讀
| 現象 | 判讀 |
|---|---|
| `server_version` 有值 / 工具回 `ok:true` 且含 `server_version` | ✅ 已連上 |
| `run_script_string` 能回傳 `wb_script_result` 內容 | ✅ 雙向通道正常 |
| 連續下多個 journal 全程不閃退 | ✅ 穩定（勝過手刻 batch 的 `0xC000013A`） |
| `ok:false`，error 提及連線/逾時/找不到 WB | ❌ 未連上（查 WB 安裝、授權、port） |
| `Error: Not connected to Workbench.` | 尚未 launch/connect，先做 5.2/5.3 第 1 步 |

### 5.5 驗證通過後
- 移除 `products/workbench.py`、`tools/workbench_pyworkbench.py` 的 `STATUS: UNVERIFIED` 註記（改為「已驗證 @日期」）。
- 才進 Phase 1 收尾：移除舊 file-IPC bridge、改寫既有 bridge 工具、無悔清理。

## 6. 相關文件
- `context.md`：專案定位、四層架構、兩條執行通道、技術債。
- `ARCHITECTURE.md`：分層職責、命名慣例、回傳信封。
