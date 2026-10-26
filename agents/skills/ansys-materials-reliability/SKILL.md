---
name: ansys-materials-reliability
description: Domain router for material intelligence, composite structures, and electronics reliability. Use for Granta MI properties, ACP composite layup, or Sherlock solder fatigue. DO NOT use for fluid aerodynamics.
---

# ANSYS 材料智慧、複合材料與可靠度主控 (Domain 08)

本技能為 ANSYS Tier-1 核心領域主控路由器，專責解析特定物理需求並將 Agent 零損耗導流至專項 Tier-2 專業求解器或子工作流。

## 核心工作流 (Core Workflow)

1. 辨析材料體系與可靠度評估目標（複材層合板強度、電子封裝焊點疲勞、材料法規庫）
2. 路由至對應 Tier-2 專業技能（ACP, Sherlock, Granta）
3. 檢索受控材料庫特性數據（正交各向異性剛度、溫變曲線、應變-壽命 S-N 曲線）
4. 建立微觀結構鋪層（Ply Stackup, Rosettes）或電子電路板裝配拓撲
5. 施加極限載荷或熱-震動環境輪廓譜（Thermal Cycling, Random Vibration）
6. 求解並計算各向異性失效因子（Tsai-Wu, Puck）或焊點潛變疲勞累積損傷
7. 輸出複合材料漸進損傷報告、電子可靠度 MTBF 壽命預測曲線與材料合規清單

## Tier-2 專業子技能路由表 (Sub-Skill Router Table)

| 物理任務與工程場景 | 目標學科模組 | 深入研讀之 Tier-2 指針 |
|---|---|---|
| 複合材料預處理與後處理、纖維鋪層、布料包覆模擬 (Draping) | Tier-2 ACP | `agents/skills-tier2/ansys-acp-granta/SKILL.md` |
| 電子封裝物理可靠度、焊點熱疲勞壽命、PCB 振動疲勞 (Sherlock) | Tier-2 Sherlock | `agents/skills-tier2/ansys-sherlock/SKILL.md` |

## 官方文檔與 APIKB 動態查詢強制令

在生成或修改任何數值模擬腳本之前，**必須**優先透過 MCP 查詢底層確切 API 簽名與參數：
- 使用 `search_ansys_docs(query='...')` 檢索該學科之官方手冊規範
- 使用 `api_search(pattern='...')` 驗證 Python / ACT 符號之完整路徑
- 嚴禁憑空猜測非公開屬性或使用已廢棄之語法

## 關鍵禁止事項 (Critical Don'ts)

- 嚴禁將等向性材料的 Von-Mises 屈服準則錯誤套用於各向異性複合材料鋪層。
- 嚴禁在電子焊點熱循環分析中忽略焊料的非線性黏塑性潛變（Creep Anand 模型）。
- 嚴禁在未校驗纖維剪切滑移角的前提下假定大曲率曲面纖維方向不變。
