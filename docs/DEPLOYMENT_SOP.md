# ANSYS Unified MCP Server 安裝與部署標準作業手冊 (Deployment SOP)

本手冊專為需要將 **ANSYS Unified MCP Server** 部署至其他工程師電腦、測試機或伺服器環境之人員編寫。遵照本作業程序，可確保在全新的 Windows 環境中順利完成安裝、環境配置、外掛部署與 AI 客戶端連線。

---

## 一、 部署先決條件 (Prerequisites)

在開始安裝前，請確認目標電腦已具備以下環境與權限：

| 項目 | 最低規格需求 | 備註說明 |
| :--- | :--- | :--- |
| **作業系統** | Windows 10 / 11 64-bit 或 Windows Server | 結構/幾何核心需調用 Windows 本機求解器介面。 |
| **Python** | **Python 3.10 ~ 3.12 (64-bit)** | 安裝時**務必勾選**「Add Python to PATH」。 |
| **ANSYS 軟體** | **ANSYS 2024 R1 (v241) ~ 2025 R1 (v251)** | 支援 Workbench, Mechanical, Fluent, SpaceClaim, optiSLang。 |
| **授權 (License)** | 具備對應 ANSYS 求解器有效 License | 需確認本機能正常開啟 ANSYS GUI。 |
| **版本控管** | Git for Windows | 用於拉取與同步倉庫代碼。 |
| **AI 客戶端** | 支援 MCP 的工具 | 如 Antigravity, Claude Desktop, Cursor, Windsurf, VSCode 等。 |

---

## 二、 標準安裝與部署步驟 (Step-by-Step)

### 步驟 1：取得專案代碼
開啟 **PowerShell** 或 **命令提示字元 (CMD)**，切換至目標工作目錄（例如 `D:\Projects` 或 `F:\Ming_python`）：
```powershell
git clone https://github.com/ikaros0902/ansys-unified-mcp.git
cd ansys-unified-mcp
```

---

### 步驟 2：建立獨立虛擬環境並安裝相依套件
為避免干擾全域 Python 環境，必須使用獨立的 `.venv`：

```powershell
# 1. 建立虛擬環境
python -m venv .venv

# 2. 啟用虛擬環境
.\.venv\Scripts\Activate.ps1

# 3. 升級基礎打包工具
python -m pip install --upgrade pip setuptools wheel

# 4. 安裝專案核心與 PyAnsys 官方套件
pip install fastmcp ansys-mechanical-core ansys-fluent-core ansys-geometry-core ansys-optislang-core python-dotenv pydantic rich psutil

# 5. 以可編輯模式安裝本專案（使模組直接支援全域 import）
pip install -e .
```

---

### 步驟 3：配置環境變數檔案 (`.env`)
專案已內建智慧路徑解析器，**不需要每一支 exe 都手動硬編碼**，只需指定版本與安裝目錄：

1. 複製設定檔範本：
   ```powershell
   Copy-Item .env.example .env
   ```
2. 開啟並編輯 `.env`，確認以下設定符合該電腦的安裝狀況：
   ```ini
   # ===== 填入目標電腦的 ANSYS 版本代號 =====
   # 例如：2025 R1 填 251；2024 R2 填 242；2024 R1 填 241
   ANSYS_VERSION=251

   # ANSYS 安裝父目錄（其下包含 v251、v242 等資料夾）
   ANSYS_ROOT=C:\Program Files\ANSYS Inc

   # 專案根目錄（填入本機 ansys-unified-mcp 所在的絕對路徑）
   WORKBENCH_MCP_ROOT=C:\path\to\ansys-unified-mcp
   WORKBENCH_MCP_QUEUE_ROOT=C:\path\to\ansys-unified-mcp\workbench_queue
   WORKBENCH_MCP_HOST=127.0.0.1
   WORKBENCH_MCP_PORT=9885
   ```
   > 💡 **自動推導機制**：系統會自動根據 `ANSYS_ROOT` 與 `ANSYS_VERSION` 自動算出 `RunWB2.exe`、`AnsysWBU.exe`、`fluent.exe`、`ANSYS.exe` (MAPDL) 等路徑。

---

### 步驟 4：執行一鍵部署腳本 (`setup.ps1`)
本步驟為最核心關鍵，會自動向 Windows 註冊 **Workbench ACT 外掛** 與 **SpaceClaim 自動 gRPC 擴充**。

以 **系統管理員身分 (Administrator)** 開啟 PowerShell 並執行：
```powershell
# 放行 PowerShell 執行權限
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# 執行自動化配置
.\setup.ps1
```

此腳本會自動完成：
1. **掃描本機登錄檔**：自動比對抓取電腦中所有已安裝的 ANSYS 版本。
2. **安裝 Workbench ACT 外掛**：將 `workbench_plugin` 自動複製至 `%APPDATA%\Ansys\v<版本>\ACT\extensions\WorkbenchMCP`。
3. **註冊 SpaceClaim 常駐 gRPC 服務**：在 `%ProgramData%\SpaceClaim\AddIns\ApiServerAddIn.Manifest.xml` 建立清單，**讓使用者日後每次開啟 SpaceClaim 時，背景自動啟動 50051 埠 gRPC 服務**，AI 可隨時連線。

---

### 步驟 5：將 MCP 掛載進 AI 客戶端 (Client 配置)

根據使用者慣用的 AI 軟體，將以下 JSON 填入其設定檔中：

#### 方案 A：Claude Desktop 客戶端
開啟設定檔：`%APPDATA%\Claude\claude_desktop_config.json`
```json
{
  "mcpServers": {
    "ansys-unified-mcp": {
      "command": "C:\\path\\to\\ansys-unified-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\path\\to\\ansys-unified-mcp\\mcp_server.py"
      ],
      "cwd": "C:\\path\\to\\ansys-unified-mcp",
      "env": {
        "PYTHONUTF8": "1",
        "ANSYS_MCP_PROFILE": "all"
      }
    }
  }
}
```
*(請將 `C:\\path\\to\\ansys-unified-mcp` 替換為實際目錄，反斜線需寫為雙反斜線 `\\`)*

#### 方案 B：Antigravity / Cursor / Windsurf
直接在專案或全域的 `mcp_config.json` 加入：
```json
{
  "mcpServers": {
    "ansys-unified-mcp": {
      "command": "C:/path/to/ansys-unified-mcp/.venv/Scripts/python.exe",
      "args": ["C:/path/to/ansys-unified-mcp/mcp_server.py"],
      "cwd": "C:/path/to/ansys-unified-mcp",
      "env": {
        "PYTHONUTF8": "1"
      }
    }
  }
}
```
> 💡 **進階特性**：`mcp_server.py` 已內建自動加入 `src` 目錄與 stderr 隔離日誌，是最穩健的啟動入口。

---

## 三、 三重驗證程序 (確保 100% 成功運作)

安裝完成後，依序執行以下 3 關驗證：

### 關卡 1：套件與 174 項工具載入驗證 (語法級)
在命令列執行此單行指令：
```powershell
.\.venv\Scripts\python.exe -c "import sys, asyncio; sys.path.insert(0, 'src'); import ansys_unified_mcp.__main__; from ansys_unified_mcp.shared import mcp; tools = asyncio.run(mcp.list_tools()); print(f'載入成功！共註冊 {len(tools)} 個工具。')"
```
* **預期結果**：輸出 `載入成功！共註冊 174 個工具。`。

---

### 關卡 2：ANSYS 本機安裝與求解器偵測驗證 (環境級)
執行以下指令，測試是否正確讀取本機求解器：
```powershell
.\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'src'); from ansys_unified_mcp.config import get_config; cfg = get_config(); print('版本:', cfg.version); print('Workbench:', cfg.workbench_exe.exists()); print('Mechanical:', cfg.mechanical_exe.exists()); print('Fluent:', cfg.fluent_exe.exists()); print('狀態:', cfg.available)"
```
* **預期結果**：
  * `Workbench: True`
  * `Mechanical: True`
  * `Fluent: True`
  * `狀態: True`

---

### 關卡 3：AI 實戰對話驗證 (業務級)
重新啟動您的 AI 客戶端（Claude Desktop、Cursor 或 Antigravity），開啟新對話並輸入：
> **「請幫我執行 check_ansys_installation 工具，檢查當前 ANSYS 環境。」**

* **預期結果**：
  AI 能成功觸發該工具，並列出檢測到的本機 ANSYS 版本、各求解器執行檔完整路徑與可用狀態。

---

## 四、 常見問題排障手冊 (Troubleshooting)

### Q1: 執行 `setup.ps1` 報錯「因為這個系統上已停用指令碼執行」？
* **原因**：Windows 預設封鎖 PowerShell 指令碼。
* **解法**：在 PowerShell 執行：
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### Q2: AI 客戶端連線出現亂碼或 JSON-RPC 解析錯誤？
* **原因**：Windows 繁體中文環境預設為 CP950 編碼。
* **解法**：確認 MCP 設定檔的 `env` 區塊已設定 `"PYTHONUTF8": "1"`。

### Q3: 啟動 SpaceClaim 時 AI 連不上幾何工具？
* **原因**：SpaceClaim 外掛清單未讀取或埠號未開放。
* **解法**：
  1. 檢查檔案是否存在：`C:\ProgramData\SpaceClaim\AddIns\ApiServerAddIn.Manifest.xml`。
  2. 開啟 SpaceClaim，確認工作管理員中是否有 `SpaceClaim.exe` 正在執行。
  3. 執行指令 `netstat -ano | findstr 50051` 確認埠號 50051 是否處於 `LISTENING` 狀態。

### Q4: 電腦記憶體有限，只想用結構或流體，不想一次載入 174 個工具？
* **解法**：支援**動態路由 (Dynamic Routing)**。在 MCP 的 `env` 中設定 `ANSYS_MCP_PROFILE`：
  - `mechanical`：僅載入力學與結構分析工具。
  - `fluent`：僅載入流體力學與 CHT 工具。
  - `geometry`：僅載入幾何建模工具。
  - `workbench`：僅載入工作台流程調度工具。
  - `all`：載入完整全套工具（預設）。