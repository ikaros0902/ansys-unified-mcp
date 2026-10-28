---
name: ansys-mcp-foundation
description: Universal foundation and session router for ANSYS Unified MCP. Use when managing sessions, diagnosing connection health, launching Workbench, or querying cross-domain documentation. DO NOT use for domain-specific simulation physics (e.g. CFD, FEA, EM).
---

# ANSYS MCP 通用底座與會話管理主控 (Domain 00)

本技能為 ANSYS 領域路由 核心領域主控路由器，專責解析特定物理需求並將 Agent 零損耗導流至專項 模組技能 專業求解器或子工作流。

## 核心工作流 (Core Workflow)

1. 檢測本機安裝環境與授權連線狀態 (`ans_session_diagnose`, `check_ansys_installation`)
2. 初始化求解器連線會話或啟動 Workbench 橋接 (`ans_session_launch`, `start_workbench_bridge`)
3. 動態檢索官方手冊索引與 API 知識庫 (`search_ansys_docs`, `api_search`, `api_get`)
4. 辨識使用者物理學科邊界並精準分流至 Domain 01-09 領域路由 路由器
5. 驗證跨模組腳本參數合規性與前置條件 (`api_validate_script`)
6. 執行完畢後安全釋放連線與清理會話資源 (`ans_session_disconnect`, `stop_workbench_bridge`)

## 模組技能 專業子技能路由表 (Sub-Skill Router Table)

| 物理任務與工程場景 | 目標學科模組 | 深入研讀之 模組技能 指針 |
|---|---|---|
| 結構力學、隱式/顯式 FEA、跌落衝擊 | Domain 01 | `../ansys-structural-mechanics/SKILL.md` |
| 計算流體力學、空氣動力學、多相流 | Domain 02 | `../ansys-fluids-cfd/SKILL.md` |
| 高頻/低頻電磁場、天線、電機、SI/PI | Domain 03 | `../ansys-electromagnetics/SKILL.md` |
| 光學成像、照明、光子學器件 | Domain 04 | `../ansys-optical-engineering/SKILL.md` |
| 散熱管理、電子散熱、熱傳導、熱翹曲 | Domain 05 | `../ansys-thermal-cooling/SKILL.md` |
| 剛柔多體動力學、機構連桿、離散元顆粒 | Domain 06 | `../ansys-multibody-particles/SKILL.md` |
| 雙向強耦合、流固耦合、系統最佳化、數位孿生 | Domain 07 | `../ansys-systems-coupling/SKILL.md` |
| 材料特性、複合材料鋪層、電子可靠度疲勞 | Domain 08 | `../ansys-materials-reliability/SKILL.md` |
| CAD 前處理、簡化去特徵、網格品質劃分 | Domain 09 | `../ansys-geometry-meshing/SKILL.md` |
| 通用錯誤碼排查與診斷指南 | 通用參考 | `../../mcp-foundation/ansys-error-catalog/SKILL.md` |

## 官方文檔與 APIKB 動態查詢強制令

在生成或修改任何數值模擬腳本之前，**必須**優先透過 MCP 查詢底層確切 API 簽名與參數：
- 使用 `search_ansys_docs(query='...')` 檢索該學科之官方手冊規範
- 使用 `api_search(pattern='...')` 驗證 Python / ACT 符號之完整路徑
- 嚴禁憑空猜測非公開屬性或使用已廢棄之語法

## 關鍵禁止事項 (Critical Don'ts)

- 嚴禁在未檢測連線狀態的前提下直接發送重型腳本命令。
- 嚴禁在通用底座層直接執行具體物理求解器數值計算。
- 嚴禁硬編碼本機通訊通訊埠或外部進程 PID。
