# ANSYS Unified MCP Server

這個專案將多個 ANSYS 相關的 MCP (Model Context Protocol) 伺服器整合為單一的集中化伺服器，大幅降低系統資源消耗並統一管理。
此伺服器提供了 127 個自動化工具，涵蓋了 ANSYS Workbench、Mechanical、Fluent 以及 SpaceClaim / Geometry。

## 🚀 核心功能

* **單一處理程序 (Single Process)**：將原本分散的四個 Python 行程整合為單一進程，節省 CPU/記憶體開銷。
* **Workbench 整合**：支援 Workbench 專案管理、日誌讀取與任務控制。
* **Mechanical 整合**：透過 ACT 擴充套件，實現與 Mechanical 雙向通訊、材料賦予、邊界條件設定與求解控制。
* **Fluent 與 Geometry 整合**：透過 PyAnsys (PyFluent, PyGeometry)，自動化執行流體計算與 SpaceClaim 3D CAD 幾何繪製。
* **100% 相容**：無縫支援 Claude / AI 代理人操作的所有原有工具。

## 📦 系統需求

* **作業系統**：Windows
* **Python**：Python 3.10 或以上版本 (建議使用虛擬環境)
* **ANSYS 版本**：預設為 **ANSYS 2025 R1 (v251)**。如果您使用的是其他版本，請於 `.env` 中調整相應路徑。

## ⚙️ 安裝與設定

### 1. 安裝 Python 依賴套件

請在專案目錄下建立並啟動虛擬環境，接著安裝相依套件：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. 設定環境變數

請複製一份 `.env.example` 並命名為 `.env`，根據您的本機 ANSYS 安裝路徑修改：

```powershell
cp .env.example .env
```
確保 `.env` 中的路徑正確指向您的 ANSYS 安裝位置。

### 3. 部署 Mechanical ACT 外掛程式

為了讓伺服器能與 ANSYS Mechanical 進行雙向溝通，必須部署 ACT 擴充套件：

1. 將專案中的 `workbench_plugin/WorkbenchMCP` 資料夾，複製到您的 `%APPDATA%\Ansys\v251\ACT\extensions\` 目錄下。
2. 啟動 ANSYS Mechanical，在擴充套件管理器中啟用 `WorkbenchMCP`。
3. 若要啟動自動排程通訊，請點選 UI 介面上的 **"Socket Timer Start"** 按鈕。

## 🎮 啟動伺服器 (供 MCP 客戶端使用)

這個伺服器是為 Claude / Cursor / Antigravity 等 MCP 客戶端設計的。請在您的 MCP 設定檔（例如 `mcp_config.json` 或 `claude_desktop_config.json`）中加入以下設定：

```json
{
  "mcpServers": {
    "ansys-unified-mcp": {
      "command": "您的路徑\\ansys-unified-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "您的路徑\\ansys-unified-mcp\\mcp_server.py"
      ],
      "cwd": "您的路徑\\ansys-unified-mcp"
    }
  }
}
```

## ⚠️ 注意事項

1. **SpaceClaim 啟動時間**：當呼叫 `geometry_launch` 工具時，SpaceClaim 的啟動通常需要 **30 ~ 50 秒**。在此期間請耐心等待工具執行完成，**請勿中止**，以免造成連線遺失或殭屍行程。
2. **快取與重啟**：如果您修改了 `workbench_plugin` 中的 Python 腳本，必須重新啟動 ANSYS Mechanical 才能載入最新版本的腳本。
