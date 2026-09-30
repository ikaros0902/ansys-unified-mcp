---
name: antigravity-notebooklm
description: 在 AntiGravity 串接 NotebookLM MCP 與 nlm CLI 工具。支援查詢 Google NotebookLM 中的筆記、來源資料與語義問答。
---

# 串接 NotebookLM（AntiGravity 版）

本技能提供透過 `nlm` (NotebookLM MCP CLI) 與 Google NotebookLM 深度整合之指引。

---

## 一、環境與工具配置

### 1. 安裝 CLI 工具
```powershell
uv tool install notebooklm-mcp-cli
nlm --version
```
*(本機已安裝於 `C:\Python311\Scripts\nlm.EXE`)*

### 2. 互動式登入 (Session 認證)
請在一般外部 PowerShell 視窗手動執行以下指令（需跳出 Chrome 登入視窗完成 Google 授權）：
```powershell
$env:PYTHONUTF8 = '1'
nlm config set auth.browser chrome
nlm login --profile default
```

### 3. 驗證連線狀態
```powershell
$env:PYTHONUTF8 = '1'
nlm doctor
nlm list notebooks
```

---

## 二、CLI 核心操作語法

當登入有效時，可直接透過終端命令查詢筆記本：

```powershell
$env:PYTHONUTF8 = '1'

# 1. 檢視筆記本詳情
nlm notebook get <notebook_id>

# 2. 列出筆記本中的所有來源文件
nlm list sources <notebook_id>

# 3. 讀取特定來源內容
nlm content <source_id>

# 4. 對筆記本進行 AI 提問與內容檢索
nlm query <notebook_id> "請摘要此筆記本中關於 ANSYS Mesh 的重點"
```

---

## 三、註冊 AntiGravity MCP Server

```powershell
$env:PYTHONUTF8 = '1'
nlm setup add antigravity
```
*執行後設定將自動寫入 `.agents/mcp_config.json` 或 `~/.gemini/config/mcp_config.json`。*
