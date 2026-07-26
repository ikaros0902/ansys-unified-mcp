# ANSYS Unified MCP Server v2.0

這是一個專為 AI Agent (Claude, Cursor 等) 設計的模型上下文協議 (Model Context Protocol, MCP) 伺服器，能夠讓 AI 直接連線並操控您本機的 ANSYS 軟體系列。

## 支援的 ANSYS 模組

- **Workbench** (透過 File IPC 驅動)
- **Mechanical** (透過 gRPC 驅動，ACT 外掛自動啟動)
- **SpaceClaim** (透過 gRPC 驅動)
- **Fluent** (透過 gRPC 驅動)
- **OptiSLang** (透過原生 Python API 驅動)
- **LS-DYNA** (即將支援)
- **MAPDL** (即將支援)

---

## 🚀 快速安裝 (針對一般使用者 / 同事)

您不再需要手動設定 Python 環境或尋找 ANSYS 安裝路徑！我們提供了一鍵安裝腳本。

1. **下載本專案** (或 `git clone`) 到您的電腦上。
2. 在專案資料夾上點擊右鍵，選擇 **「使用 PowerShell 執行 (Run with PowerShell)」**，或是打開 PowerShell 並輸入：
   ```powershell
   .\setup.ps1
   ```
3. 腳本會自動完成以下工作：
   - 建立 Python 虛擬環境 (`.venv`)
   - 安裝所有必要的相依套件 (PyAnsys 等)
   - 自動偵測您安裝的 ANSYS 版本
   - 自動安裝 WorkbenchMCP (ACT 外掛) 到您的 `%APPDATA%`
   - 生成專屬的 `mcp_config.json` 供 AI 客戶端使用

### 將 MCP Server 加入 Claude / Cursor

安裝完成後，開啟專案目錄下的 `mcp_config.json`，將裡面的內容複製到您的 Claude Desktop 設定檔 (通常在 `%APPDATA%\Claude\claude_desktop_config.json`) 中，然後重啟 Claude 即可。

---

## ⚡ 自動連線機制 (Auto-Connect)

v2.0 導入了全新的「自動連線管理器」。

您**不需要**在指令列打指令來啟動伺服器或設定 Port。您只要像平常一樣開啟您的 ANSYS 軟體：
1. **Workbench**：直接開啟，背景會自動輪詢。
2. **Mechanical**：從 Workbench 開啟，或是單獨開啟。內建的 ACT 外掛會在背景自動啟動 gRPC Server (Port 10000+)。
3. **SpaceClaim / Fluent**：同理，只要開啟，MCP Agent 就能掃描並連上。

MCP Agent 在啟動時會自動偵測正在執行的這些視窗並接管控制。

---

## 開發者資訊 (Project Structure)

本專案已重構為標準 Python 套件：
- `pyproject.toml`: 專案設定與相依性。
- `src/ansys_unified_mcp/`: 核心原始碼目錄。
  - `config.py`: 自動偵測與推導 ANSYS 系統路徑。
  - `connection_manager.py`: 自動探測背景運作中的 ANSYS 進程與 Port。
  - `server.py` / `__main__.py`: MCP 伺服器主程式。
  - `tools/`: 各模組的 MCP 註冊工具 (Mechanical, Fluent, OptiSLang 等)。
  - `drivers/`: 底層呼叫模組。
  - `bridges/`: File IPC 等橋接工具。
- `workbench_plugin/`: 將安裝至 ANSYS 的 ACT 外掛原始碼。

## 疑難排解

- 若安裝腳本執行時出現「執行原則 (Execution Policy)」錯誤，請先在 PowerShell 輸入 `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`。
- 若連線失敗時，請確認防火牆沒有阻擋 10000~10010 (Mechanical) 與 50051 (SpaceClaim) 的本機 (localhost) 網路通訊。

---

## 👥 多實例動態埠與引導規則

為了支援在同一台電腦上同時開啟多個不同的 ANSYS 視窗（例如：同時開啟 Workbench、Mechanical、SpaceClaim 等多專案情境），v2.0 導入了動態埠與實例註冊表：
1. **動態分配通訊埠**：各視窗啟動時會自動尋找可用的埠號綁定通訊（Socket 埠自 9885 起；gRPC 埠自 10000 起），避免互相佔用衝突。
2. **自動註冊**：啟動後會自動在 `workbench_queue/registry/` 目錄中以 PID 命名寫入資訊檔（包含 PID、進程名稱、視窗標題與分配到的埠號）。當視窗關閉時，MCP 伺服器會自動清理過期實例。
3. **主動詢問引導**：當 AI 客戶端收到「連線 ANSYS」指令且環境中有多個實例或模組時，**AI 必須先主動以多選單或問答方式詢問使用者要連接哪一個模組**，不可擅自盲目猜測連線。
