---
name: ansys-electromagnetics
description: Domain router for high/low frequency electromagnetics, RF, antennas, electric machines, and signal integrity. Use for S-parameters, antennas, motors, transformers, SI/PI, or EM fields. DO NOT use for structural or pure fluid mechanics.
---

# ANSYS 電磁場、高頻 RF 與電機主控 (Domain 03)

本技能為 ANSYS 領域路由 核心領域主控路由器，專責解析特定物理需求並將 Agent 零損耗導流至專項 模組技能 專業求解器或子工作流。

## 核心工作流 (Core Workflow)

1. 判定電磁波頻率尺度與應用場景（高頻 RF、低頻機電、封裝 SI/PI）
2. 路由至對應 模組技能 專項電磁技能（HFSS, Maxwell, Q3D/SIwave, Motor-CAD）
3. 建立 3D 電磁結構、線圈繞組幾何或 ECAD 疊層佈局
4. 指派材料介電係數、損耗角正切、磁導率與非線性 BH 曲線
5. 設定激勵端口（Wave Port, Lumped Port, 繞組電流）與吸收輻射邊界 (PML)
6. 配置頻域/時域求解器與自適應網格剖分頻率（Adaptive Solution Pass）
7. 求解並導出 S 參數矩陣、天線方向圖增益、電機轉矩脈動或 RLCG 寄生參數

## 模組技能 專業子技能路由表 (Sub-Skill Router Table)

| 物理任務與工程場景 | 目標學科模組 | 深入研讀之 模組技能 指針 |
|---|---|---|
| 高頻全波電磁場、天線、微波器件、雷達 RCS、S 參數 | 模組技能 HFSS | `../../electromagnetics/ansys-hfss/SKILL.md` |
| 低頻電磁場、永磁/感應電機、變壓器、電磁鐵、渦流損耗 | 模組技能 Maxwell | `../../electromagnetics/ansys-maxwell/SKILL.md` |
| PCB/IC 封裝寄生參數提取 (RLCG)、信號與電源完整性 (SI/PI) | 模組技能 Q3D/SIwave | `../../electromagnetics/ansys-q3d-siwave/SKILL.md` |
| 電機多物理快速概念設計、效率雲圖速算與熱路評估 | 模組技能 Motor-CAD | `../../electromagnetics/ansys-motorcad/SKILL.md` |

## 官方文檔與 APIKB 動態查詢強制令

在生成或修改任何數值模擬腳本之前，**必須**優先透過 MCP 查詢底層確切 API 簽名與參數：
- 使用 `search_ansys_docs(query='...')` 檢索該學科之官方手冊規範
- 使用 `api_search(pattern='...')` 驗證 Python / ACT 符號之完整路徑
- 嚴禁憑空猜測非公開屬性或使用已廢棄之語法

## 關鍵禁止事項 (Critical Don'ts)

- 嚴禁 Wave Port 橫截面尺寸小於傳輸線導波模態分佈區域（避免切斷邊界場）。
- 嚴禁在 10 GHz 以上高頻損耗評估中忽略導體表面粗糙度（Huray 模型）。
- 嚴禁在低頻瞬態電機運動設定中將 Band 物件與靜止幾何發生面相交。
