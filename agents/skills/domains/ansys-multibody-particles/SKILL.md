---
name: ansys-multibody-particles
description: Domain router for multibody dynamics (MBD) and granular discrete element method (DEM). Use for kinematic linkages, gear trains, bushings, and particle flow or wear. DO NOT use for pure static stress or optics.
---

# ANSYS 多體動力學與顆粒離散元主控 (Domain 06)

本技能為 ANSYS 領域路由 核心領域主控路由器，專責解析特定物理需求並將 Agent 零損耗導流至專項 模組技能 專業求解器或子工作流。

## 核心工作流 (Core Workflow)

1. 區分機構系統運動（剛柔多體動力學 MBD）與散料顆粒流動（離散元 DEM）
2. 路由並載入對應 模組技能 專業求解器技能（Motion, Rocky DEM）
3. 建立多體鉸鏈約束（轉動副、移動副、襯套剛度）或非球形顆粒幾何形貌
4. 設定接觸力模型（非線性恢復力、摩擦阻尼、黏彈性顆粒碰撞模型）
5. 配置機構運動驅動曲線或顆粒進料流率邊界
6. 設定時間步長進行動態積分演進（DEM 需滿足 Rayleigh 時間步長限制）
7. 提取機構鉸鏈動態反力、柔性體動應力歷程或料斗壁面磨損分佈

## 模組技能 專業子技能路由表 (Sub-Skill Router Table)

| 物理任務與工程場景 | 目標學科模組 | 深入研讀之 模組技能 指針 |
|---|---|---|
| 剛體/柔性體多體動力學、機構運動學、齒輪鏈條傳動 (Motion) | 模組技能 Motion | `../../multibody-particles/ansys-motion/SKILL.md` |
| 散料顆粒流動、真實多面體顆粒、物料磨損破碎、CFD-DEM 耦合 | 模組技能 Rocky DEM | `../../multibody-particles/ansys-rocky-dem/SKILL.md` |

## 官方文檔與 APIKB 動態查詢強制令

在生成或修改任何數值模擬腳本之前，**必須**優先透過 MCP 查詢底層確切 API 簽名與參數：
- 使用 `search_ansys_docs(query='...')` 檢索該學科之官方手冊規範
- 使用 `api_search(query='...', product='motion')` 驗證 Python / ACT 符號之完整路徑
- 嚴禁憑空猜測非公開屬性或使用已廢棄之語法

## 關鍵禁止事項 (Critical Don'ts)

- 嚴禁機構運動學約束過度或存在冗餘奇異副導致方程無解。
- 嚴禁 DEM 時間步長設定大於臨界 Rayleigh 步長之 20%（引發顆粒碰撞能量發散爆炸）。
- 嚴禁在忽略顆粒真實形貌互鎖效應的情況下以球形顆粒模擬高角碎石。
