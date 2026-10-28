---
name: ansys-structural-mechanics
description: Domain router for structural mechanics, implicit/explicit FEA, modal, shock & random vibration. Use when analyzing stress, deformation, impact, crash, or vibration. DO NOT use for pure CFD, optical, or low-frequency EM.
---

# ANSYS 結構力學與動力學主控 (Domain 01)

本技能為 ANSYS 領域路由 核心領域主控路由器，專責解析特定物理需求並將 Agent 零損耗導流至專項 模組技能 專業求解器或子工作流。

## 核心工作流 (Core Workflow)

1. 辨識結構分析型態（靜態力學、模態分析、隨機振動、顯式衝擊）
2. 路由並載入對應 模組技能 專業求解器技能或工作流手冊
3. 驗證材料力學特性（彈性模量、泊松比、屈服強度、非線性應力-應變）
4. 設定邊界條件（固定支撐、位移約束、載荷、接觸對與螺栓預緊力）
5. 配置求解器數值控制（自動時間步進、收斂容差、大變形效應）
6. 執行求解並監控力與位移殘差收斂曲線（顯式分析檢查能量平衡）
7. 提取等效應力 (Von-Mises)、主應變、變形雲圖並判定結構安全裕度

## 模組技能 專業子技能路由表 (Sub-Skill Router Table)

| 物理任務與工程場景 | 目標學科模組 | 深入研讀之 模組技能 指針 |
|---|---|---|
| 線性/非線性靜態結構分析、模態頻率 | 模組技能 Mechanical | `../../structural-mechanics/ansys-mechanical/SKILL.md` |
| 顯式衝擊、碰撞、跌落模擬 (Explicit FEA) | 模組技能 LS-DYNA | `../../structural-mechanics/ansys-lsdyna/SKILL.md` |
| 8 步標準跌落衝擊工程作業流程 (SOP) | 模組技能 衝擊工作流 | `../../structural-mechanics/shock-analysis-workflow/SKILL.md` |
| 隨機振動 (PSD)、響應譜、疲勞壽命評估 | 模組技能 振動分析 | `../../structural-mechanics/ansys-random-vibration/SKILL.md` |
| LS-DYNA 前處理關鍵字與 LS-PrePost 腳本 | 模組技能 LS-PrePost | `../../structural-mechanics/ansys-ls-prepost/SKILL.md` |
| DPF 資料處理框架與子模型 (Submodeling) 應力提取 | 模組技能 DPF | `../../structural-mechanics/ansys-submodeling-dpf/SKILL.md` |
| PyMechanical 高階 gRPC 自動化底層操作 | 模組技能 PyMech | `../../structural-mechanics/pymechanical-operations/SKILL.md` |

## 官方文檔與 APIKB 動態查詢強制令

在生成或修改任何數值模擬腳本之前，**必須**優先透過 MCP 查詢底層確切 API 簽名與參數：
- 使用 `search_ansys_docs(query='...')` 檢索該學科之官方手冊規範
- 使用 `api_search(pattern='...')` 驗證 Python / ACT 符號之完整路徑
- 嚴禁憑空猜測非公開屬性或使用已廢棄之語法

## 關鍵禁止事項 (Critical Don'ts)

- 嚴禁在顯式衝擊求解中忽略沙漏能（Hourglass Energy 超過總能量 5% 即為無效模擬）。
- 嚴禁在未約束剛體位移或未設定弱彈簧的情況下求解靜態奇異結構。
- 嚴禁在非線性大變形分析中關閉 Large Deflection 開關。
