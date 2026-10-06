# ANSYS Unified MCP — 必要安裝與快速啟動 SOP 手冊

本手冊為本專案的核心標準作業程序（SOP），只需 3 個步驟即可完成安裝與 AI 連線。

---

## 📋 步驟 1：一鍵環境安裝與 ACT 外掛部署

開啟 **PowerShell**（以系統管理員身分或一般使用者皆可），進入本專案目錄執行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\maintenance\setup.ps1
```

> **本腳本會自動完成以下所有工作**：
> 1. 自動建立 Python 虛擬環境（`.venv`）並安裝所有 PyAnsys 與 FastMCP 相依套件。
> 2. 自動偵測本機安裝之 ANSYS 版本（支援 2024 R1、2024 R2、2025 R1 等）。
> 3. 自動佈署 `WorkbenchMCP` ACT 外掛至本機 `%APPDATA%\Ansys\v<版本>\ACT\extensions`。
> 4. 自動生成連線設定範本。

---

## 🔌 步驟 2：AI 代理連線設定 (MCP Client Setup)

將以下設定加入您的 AI 代理設定檔中：

### 1. Claude Desktop 設定
檔案位置：`%APPDATA%\Claude\claude_desktop_config.json`
```json
{
  "mcpServers": {
    "ansys-unified-mcp": {
      "command": "F:\\Ming_python\\ansys-unified-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "-m",
        "ansys_unified_mcp.__main__"
      ],
      "env": {
        "PYTHONUTF8": "1"
      }
    }
  }
}
```

### 2. Antigravity / Cursor 設定
在全域 MCP 設定檔（例如 `mcp_config.json`）中直接指向本機虛擬環境的 Python 執行檔即可。

---

## ⚡ 步驟 3：日常模擬作業流程（自動連線）

您**完全不需要手動啟動伺服器或設定 Port**：

1. **開啟 ANSYS**：如常打開 Workbench 專案（`.wbpj`）或 Mechanical。
2. **自動連線**：內建的 ACT 外掛會在後台自動啟動 gRPC 連線埠（Port 10000+）。
3. **AI 驅動**：直接向 AI 提出模擬需求（如「匯入疊構建立幾何」、「施加 3-2-1 支承與熱載荷求解熱翹曲」），AI 將自動連線並推進分析！

---

## 🔍 故障排查與驗證 (Verification)

若需驗證本機環境是否正常，可於 PowerShell 執行：
```powershell
.venv\Scripts\python scripts\preflight_env_check.py
```
若需執行單元測試驗證：
```powershell
.venv\Scripts\pytest tests\test_mechanical_controller.py -v
```
