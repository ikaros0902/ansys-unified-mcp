---
name: ansys-systems-coupling
description: Domain router for multiphysics co-simulation, system coupling (SyC), digital twins, and design optimization. Use for 2-way FSI, optiSLang MOP, ROM, or SCADE. DO NOT use for single-physics components.
---

# ANSYS 系統耦合、多物理與最佳化主控 (Domain 07)

本技能為 ANSYS Tier-1 核心領域主控路由器，專責解析特定物理需求並將 Agent 零損耗導流至專項 Tier-2 專業求解器或子工作流。

## 核心工作流 (Core Workflow)

1. 辨別跨物理場協同型態（流固耦合 FSI、共軛熱 CHT、多學科最佳化、數位孿生）
2. 路由至對應 Tier-2 專項模組（System Coupling, optiSLang, Twin-SCADE）
3. 在各參與求解器中配置交界面（Interface Boundaries）並建立資料映射配對
4. 配置時間步同步機制與非線性隱式迭代亞鬆弛參數 (IQN-ILS)
5. 建構高維參數採樣矩陣 (DoE) 或提煉 3D 場降階模型 (ROM / MOP)
6. 執行多物理聯算並監控交界面資料守恆性與系統收斂準則
7. 輸出跨場動態交互雲圖、全域敏感度帕累托解集或邊緣部署 FMU

## Tier-2 專業子技能路由表 (Sub-Skill Router Table)

| 物理任務與工程場景 | 目標學科模組 | 深入研讀之 Tier-2 指針 |
|---|---|---|
| 流固雙向強耦合 (FSI)、共軛熱傳 (CHT)、雙向跨求解器協同 | Tier-2 SyC | `agents/skills-tier2/ansys-system-coupling/SKILL.md` |
| 多學科設計最佳化 (MDO)、敏感度分析、最佳預測元模型 (MOP) | Tier-2 optiSLang | `agents/skills-tier2/ansys-optislang/SKILL.md` |
| 數位孿生 (Twin Builder)、降階模型 (ROM)、嵌入式安全軟體 (SCADE) | Tier-2 Twin/SCADE | `agents/skills-tier2/ansys-twin-scade/SKILL.md` |

## 官方文檔與 APIKB 動態查詢強制令

在生成或修改任何數值模擬腳本之前，**必須**優先透過 MCP 查詢底層確切 API 簽名與參數：
- 使用 `search_ansys_docs(query='...')` 檢索該學科之官方手冊規範
- 使用 `api_search(pattern='...')` 驗證 Python / ACT 符號之完整路徑
- 嚴禁憑空猜測非公開屬性或使用已廢棄之語法

## 關鍵禁止事項 (Critical Don'ts)

- 嚴禁在輕質彈性結構與水體耦合中採用顯式鬆弛迭代（附加質量效應必致發散）。
- 嚴禁在未通過交叉驗證（Coefficient of Prognosis, CoP < 80%）的 MOP 上進行最佳化尋優。
- 嚴禁非共形網格交界面在力與熱流傳遞時忽略守恆積分檢查。
