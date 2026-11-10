# ANSYS Unified MCP Server (v3.0)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Standard-purple.svg)](https://modelcontextprotocol.io/)

本專案是專為 AI 程式助理（如 Antigravity, Claude Desktop, Cursor, Windsurf 等）設計的模型上下文協議（Model Context Protocol, MCP）伺服器。
安裝後，AI 能直接操作您電腦上的 ANSYS 進行幾何建模、結構力學、流體流動、電磁場、熱分析與多目標最佳化。

---

## 🎯 核心功能與特色

- **多版本 ANSYS 自動偵測與執行期動態切換**：相容 ANSYS 2020 R2 (v202) 至 2025 R2 (v252) 及更高版本。單機安裝多個版本時，AI 可在同一對話中動態切換目標版本。
- **雙軌架構（Dual-Track Architecture）**：
  - **Track 1（商業求解器）**：本機具備授權時，由 PyAnsys 或 ACT 外掛進行完整模擬與後處理。
  - **Track 2（數值基準引擎）**：無特定求解器授權或未安裝該模組時，系統自動啟動內建物理公式與數值積分引擎，以完全同構的 JSON 信封回傳物理指標，杜絕 AI 呼叫崩潰。
- **背景自動偵測（Auto-Connect）**：無需手動輸入通訊埠。只要開啟 Mechanical、Workbench 或 SpaceClaim 視窗，MCP 會自動辨識進程 PID 並完成掛載。
- **動態領域工具收斂（Dynamic Tool Routing）**：支援 `ANSYS_MCP_PROFILE` 與 `ans_session_set_workspace`，可將 216 個工具依需求收斂為單一學科，大幅降低 AI 的 Token 消耗。

---

## 🚀 三步快速安裝 (Quickstart)

> 📖 **詳細安裝與疑難排解**：請參閱 [標準部署手冊 (DEPLOYMENT_SOP.md)](docs/deployment/DEPLOYMENT_SOP.md)。

### 步驟 1：下載專案代碼
在 PowerShell 中執行：
```powershell
git clone https://github.com/ikaros0902/ansys-unified-mcp.git
cd ansys-unified-mcp
```

### 步驟 2：執行一鍵部署腳本
以一般使用者（或系統管理員）身分執行：
```powershell
powershell -ExecutionPolicy Bypass -File scripts\maintenance\setup.ps1
```
> **腳本自動完成的項目**：
> 1. 建立 `.venv` 獨立虛擬環境並安裝核心 PyAnsys 套件。
> 2. 自動掃描本機已安裝的所有 ANSYS 版本（v202 至 v261）。
> 3. 自動設定 `.env` 環境檔與 `%LOCALAPPDATA%\ansys-unified-mcp` 跨進程佇列。
> 4. 自動向各版本 `%APPDATA%` 部署 Workbench/Mechanical ACT 外掛。
> 5. 自動產生連線設定檔 `mcp_config.json` 並執行環境健康檢查。

### 步驟 3：掛載至您的 AI 客戶端
安裝完成後，複製自動產生的 `mcp_config.json` 內容至您的 AI 設定檔：
- **Claude Desktop**：`%APPDATA%\Claude\claude_desktop_config.json`
- **Antigravity (Google AGY)**：`%USERPROFILE%\.gemini\config\mcp_config.json`
- **Cursor**：設定中的 `Features` -> `MCP Servers`

重新啟動 AI 客戶端即可開始對話！

---

## 📊 18 大物理領域與求解器支援矩陣

| 領域學科 | 主要驅動方式 | Track 1 原生求解器 | Track 2 數值基準引擎演算法 |
| :--- | :--- | :--- | :--- |
| **結構力學 (Structural)** | gRPC / Subprocess | Mechanical, LS-DYNA, MAPDL, DPF | 梁殼彈塑性解析解、模態振型正交展開 |
| **流體力學 (Fluids)** | PyFluent gRPC | Fluent, CFX | 0D/1D 管道壓降、熱對流經驗公式 |
| **幾何建模 (Geometry)** | PyAnsys Geometry gRPC | SpaceClaim, Discovery | 幾何拓撲體積、投影表面積計算 |
| **工作台流程 (Workbench)** | File IPC / Socket Timer | Workbench (RunWB2) | 專案樹節點依賴關係拓撲排序 |
| **多目標最佳化 (Optimization)** | 原生 Python API | optiSLang | MOP (最佳預測元模型)、多項式回歸 |
| **高頻電磁 (HFSS)** | PyAEDT / Script Runner | HFSS | 微帶天線腔體模型、回波損耗計算 |
| **低頻電磁 (Maxwell)** | PyAEDT / Script Runner | Maxwell | 磁路歐姆定律、氣隙虛功吸力計算 |
| **幾何與波導光學 (Optics)** | Direct API / COM | Speos, Zemax, Lumerical | ABCD 近軸光線追跡、波導特徵方程求解 |
| **散熱分析 (Thermal)** | Mechanical / Icepak | Mechanical Thermal, Icepak | 穩態/暫態多層熱傳導與熱阻網絡模型 |
| **離散顆粒與剛體 (Multibody)**| Rocky / Motion API | Rocky DEM, Motion | Hertz-Mindlin 彈簧阻尼接觸力學積分 |
| **材料與可靠度 (Materials)** | Granta / Sherlock API | Granta MI, Sherlock | 溫度退化材料本構、焊點熱疲勞壽命 |
| **聲學與心理聲學 (Sound)** | Direct Algorithm | Ansys Sound | ISO 532-1 Zwicker 心理聲學響度計算 |
| **海洋水動力學 (Aqwa)** | Hydrodynamic Solver | Aqwa | 水線剛度矩陣、浮體垂盪衰減振盪 |
| **化學反應動力學 (Chemkin)** | Kinetics Solver | Chemkin-Pro | 0D 等溫反應器 Arrhenius 速率積分 |
| **電機電磁設計 (Motor-CAD)** | ActiveX / COM | Motor-CAD | PMSM 反電動勢常數與 dq 軸銅損效率 |

---

## 👥 多版本並存與實例動態管理

### 1. 多版本切換
若您的電腦同時安裝了多個版本的 ANSYS（例如同時裝有 2024 R2 與 2025 R1）：
- **靜態指定**：可在 `.env` 檔案中直接設定 `ANSYS_VERSION=242`。
- **動態切換**：在與 AI 對話中，直接輸入：
  > 「請幫我將 ANSYS 目標版本切換至 242」
  AI 會自動呼叫 `ans_set_active_version("242")` 工具，即時重新綁定所有求解器執行路徑。

### 2. 多視窗動態掛載
當您在同一台電腦開啟多個不同專案的 Mechanical 或 SpaceClaim 視窗時：
- 系統會自動為各視窗分配專屬 gRPC 通訊埠（Mechanical: 10000+；SpaceClaim: 50051+）。
- AI 在連線前會自動列出所有正在運行的實例 PID、視窗標題與埠號，並主動詢問您要連線哪一個視窗。

---

## 🛠️ 常見問題排查 (FAQ)

### Q1: 執行 `setup.ps1` 提示腳本執行受阻？
**原因**：Windows 預設策略限制 PowerShell 指令碼。  
**解法**：在 PowerShell 執行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q2: 呼叫時出現 `ansys-mechanical-core not installed`？
**原因**：安裝時使用了 `--minimal` 模式或未安裝選用套件。  
**解法**：手動補裝核心互動套件：
```powershell
.\.venv\Scripts\pip.exe install -e ".[standard]"
```

### Q3: 啟動 SpaceClaim 時 AI 連不上幾何工具？
**原因**：SpaceClaim 外掛清單尚未載入或連接埠未開放。  
**解法**：
1. 確認檔案是否存在：`C:\ProgramData\SpaceClaim\AddIns\ApiServerAddIn.Manifest.xml`。
2. 啟動 SpaceClaim，執行 `netstat -ano | findstr 50051` 確認通訊埠處於 `LISTENING` 狀態。

---

## 📚 相關文件與架構導覽

- [安裝與部署標準手冊 (DEPLOYMENT_SOP.md)](docs/deployment/DEPLOYMENT_SOP.md)：完整環境需求、安裝步驟與驗證流程。
- [MCP 工具範圍與 Profile 收斂指南 (MCP_TOOL_SCOPING_GUIDE.md)](docs/deployment/MCP_TOOL_SCOPING_GUIDE.md)：如何依工作流調整工具暴露範圍。
- [系統架構與分層職責 (ARCHITECTURE.md)](docs/architecture/ARCHITECTURE.md)：控制器、驅動層、連線管理器與通訊協議規範。
- [業務與物理規則規格書 (BUSINESS_RULES.md)](docs/testing/BUSINESS_RULES.md)：BDD 測試邊界與金絲雀驗收規則。
