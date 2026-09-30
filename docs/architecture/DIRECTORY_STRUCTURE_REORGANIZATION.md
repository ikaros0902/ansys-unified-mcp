# ANSYS Unified MCP 目錄樹架構收斂與精簡規範

**模組路徑**：`F:\Ming_python\ansys-unified-mcp`  
**更新日期**：2026-09-30  
**版本**：2.1  

---

## 一、 目錄混亂與重複性根因排查

針對使用者 Windows 檔案總管截圖中多達 24 個資料夾的混亂狀態，經盤查主要由以下四類原因造成：

1. **廢棄與歷史空目錄**：
   - `cad_output/`：早先幾何匯出測試留下的空目錄（0 檔案），現已由 `jobs/` 沙盒取代。
   - `commands/`：早先檔案隊列測試留下的空目錄（0 檔案），現已統一收納於 `workbench_queue/commands/`。
   - `runs/`：歷史執行輸出目錄（0 檔案），現已由 `jobs/` 取代。
2. **多代理（Multi-Agent）執行歷史殘留**：
   - `.agents/`：歷史 Swarm 代理運行留下的暫存區（含 257 個歷史日誌、worker/challenger 暫存），嚴重干擾檔案總管視覺。
3. **命名大小寫與職責重疊混淆**：
   - `SKILLs` 與 `skills`：Windows NTFS 大小寫不敏感導致顯示為全大寫，與 Unix/Git 追蹤規範（小寫 `skills`）脫節。
   - `agents/` 與 `.agents/`：兩個同名資料夾並存（一個為規範文件、一個為歷史暫存），造成概念嚴重混淆。
   - `scripts/` 與 `skills/*/scripts/`：`scripts/` 下殘留了 7 月份的臨時 `.wbjn` 腳本與空的 `pcb_warpage_analysis` 快取目錄。
4. **孤立暫存垃圾**：
   - `debug.log`、`grpc_status.txt`、根目錄 `__pycache__/`。

---

## 二、 精簡與清理行動成果

| 項目類別 | 原始路徑 / 檔案 | 處置方式 | 說明 |
| :--- | :--- | :---: | :--- |
| **廢棄空目錄** | `cad_output/`, `commands/`, `runs/` | **徹底移除** | 0 檔案無代碼引用，清除冗餘 |
| **歷史 Agent 暫存** | `.agents/` (257 檔案) | **規格歸檔並清理** | 重要 `PROJECT.md` 轉移至 `docs/architecture/historical_specs/`，清除殘留歷史目錄 |
| **暫存腳本與快取** | `scripts/script_*.wbjn`, `scripts/pcb_warpage_analysis/` | **徹底移除** | 歷史殘留測試腳本與 pyc 快取移除 |
| **根目錄孤立檔案** | `debug.log`, `grpc_status.txt`, `__pycache__/` | **徹底移除** | 清除臨時日誌與快取 |
| **規範化目錄命名** | `SKILLs/` $\rightarrow$ `skills/` | **大小寫規範化** | 與 Git 遠端路徑及跨平台標準統一為小寫 |

---

## 三、 重組後之 5 大架構分層目錄樹（收斂至 11 個核心目錄）

```text
F:\Ming_python\ansys-unified-mcp\
│
├── 📂 [1. 核心原始碼層 Core Source]
│   └── src/ansys_unified_mcp/   # FastMCP 伺服器、產品控制器 (products)、求解驅動 (drivers)、連線管理 (bridges)
│
├── 📂 [2. AI 代理能力與規範層 Agent Capabilities]
│   ├── agents/                  # 代理行為指引 (steering) 與系統核心架構情境 (contexts)
│   └── skills/                  # 18 大 ANSYS 物理場領域工程技能包 (Mechanical, Fluent, LS-DYNA, PCB 等)
│
├── 📂 [3. 測試與驗證工程層 Test Suite]
│   └── tests/                   # 單元測試 (unit)、整合測試 (integration)、契約測試 (contract)
│
├── 📂 [4. 範例與技術文檔層 Examples & Documentation]
│   ├── examples/                # 官方可執行完整工況示範 (幾何清理、PCB 熱翹曲、衝擊響應)
│   └── docs/                    # 架構規格手冊、測試指導原則、修復紀錄與歷史規格
│
└── 📂 [5. 運行佇列與系統維護層 Runtime Queue & Tooling]
    ├── workbench_queue/         # Workbench 檔案隊列 IPC 核心通道 (registry, commands, results)
    ├── jobs/                    # 模擬作業沙盒佇列 (結構化 inputs/workspace/artifacts)
    ├── logs/                    # 系統執行稽核與錯誤追蹤日誌 (保留結構)
    ├── deploy/                  # 系統環境佈署與依賴配置腳本
    └── scripts/                 # 開發者維護工具 (環境預檢、技能雙向同步、合規稽核)
```

---

## 四、 根目錄檔案精簡原則

根目錄僅保留標準的工程設定檔與入口：
- `.gitignore`：版本控制排除名單
- `.env` / `.env.example`：環境變數設定
- `pyproject.toml` / `uv.lock`：Python 專案依賴與工具設定
- `README.md` / `ARCHITECTURE.md` / `AGENTS.md`：專案自述與全域核心規範
- `mcp_server.py`：單一入口啟動腳本
