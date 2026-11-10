---
name: ansys-thermal-cooling
description: Domain router for thermal management, electronics cooling, conduction, convection, and radiation. Use for temperature distribution, heat sinks, Icepak enclosures, or PCB warpage. DO NOT use for high-frequency RF or optical design.
---

# ANSYS 熱傳導、散熱與電子冷卻主控 (Domain 05)

本技能為 ANSYS 領域路由 核心領域主控路由器，專責解析特定物理需求並將 Agent 零損耗導流至專項 模組技能 專業求解器或子工作流。

## 核心工作流 (Core Workflow)

1. 識別主導熱傳路徑（固體熱傳導、強迫/自然對流換熱、高溫熱輻射）
2. 路由至對應 模組技能 熱分析模組（Thermal Analysis, Icepak, PCB Warpage）
3. 建立電子器件熱幾何模型或熱管、冷板、散熱鰭片幾何拓撲
4. 設定晶片熱耗、發熱功耗（Die Heat Source）與材料導熱係數張量
5. 配置環境邊界條件（環境溫度、表面對流換熱係數 HTC、表面發射率）
6. 執行穩態熱平衡或瞬態升溫/冷卻循環求解
7. 提取最高結溫 (Tj)、封裝熱阻、熱應力分佈與 PCB 熱翹曲位移

## 模組技能 專業子技能路由表 (Sub-Skill Router Table)

| 物理任務與工程場景 | 目標學科模組 | 深入研讀之 模組技能 指針 |
|---|---|---|
| 通用結構熱傳導、熱應力耦合、穩態/瞬態熱平衡 | 模組技能 結構熱傳 | `../../thermal-cooling/ansys-thermal-analysis/SKILL.md` |
| 電子設備系統級熱設計、機箱散熱風道、熱管冷板 (Icepak) | 模組技能 Icepak | `../../thermal-cooling/ansys-icepak/SKILL.md` |
| 封裝基板與 PCB 回流焊熱翹曲模擬 (Warpage) | 模組技能 PCB 翹曲 | `../../materials-reliability/pcb-warpage-analysis/SKILL.md` |

## 官方文檔與 APIKB 動態查詢強制令

在生成或修改任何數值模擬腳本之前，**必須**優先透過 MCP 查詢底層確切 API 簽名與參數：
- 使用 `search_ansys_docs(query='...')` 檢索該學科之官方手冊規範
- 使用 `api_search(query='...', product='pyaedt')` 驗證 Python / ACT 符號之完整路徑
- 嚴禁憑空猜測非公開屬性或使用已廢棄之語法

## 關鍵禁止事項 (Critical Don'ts)

- 嚴禁在密封機箱自然對流熱模擬中忽略重力加速度向量方向。
- 嚴禁在 100°C 以上發熱體高溫熱分析中忽視表面熱輻射換熱機制。
- 嚴禁在未校驗熱阻網路模型（双熱阻模型 Delphi）的前提下簡化高功耗晶片。
