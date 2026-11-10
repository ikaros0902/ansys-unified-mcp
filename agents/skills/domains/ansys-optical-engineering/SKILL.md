---
name: ansys-optical-engineering
description: Domain router for optical design, illumination, imaging systems, and photonic devices. Use for Speos light simulation, Zemax lens design, or Lumerical photonics. DO NOT use for structural FEA or general CFD.
---

# ANSYS 光學工程、照明與光子學主控 (Domain 04)

本技能為 ANSYS 領域路由 核心領域主控路由器，專責解析特定物理需求並將 Agent 零損耗導流至專項 模組技能 專業求解器或子工作流。

## 核心工作流 (Core Workflow)

1. 辨別光學物理體系（幾何成像光學、非成像照明工程、波動/奈米光子學）
2. 路由並載入對應 模組技能 光學專業技能（Speos, Zemax, Lumerical）
3. 設定光學光譜範圍（UV, 可見光, NIR, 遠紅外）與光源發光特性
4. 指派光學材料屬性（折射率色散公式 Sellmeier, 表面 BSDF 散射特性）
5. 配置感測器與評估指標（照度計 Lux, 輝度計 cd/m2, MTF, 畸變率, FDTD Monitor）
6. 執行非連續光線追跡（Monte Carlo Ray Tracing）或波動麥克斯韋方程求解
7. 後處理光學均勻性、人眼視覺感知圖、波前像差或光子傳輸光譜

## 模組技能 專業子技能路由表 (Sub-Skill Router Table)

| 物理任務與工程場景 | 目標學科模組 | 深入研讀之 模組技能 指針 |
|---|---|---|
| 系統級照明設計、車燈、人眼視覺感知 (HUD)、照度/輝度 | 模組技能 Speos | `../../optical-engineering/ansys-speos/SKILL.md` |
| 光學鏡頭設計、序列/非序列光線追跡、成像品質 MTF、容差分析 | 模組技能 Zemax | `../../optical-engineering/ansys-zemax/SKILL.md` |
| 微納光子學器件、FDTD、光纖波導、光電整合、光子積體電路 | 模組技能 Lumerical | `../../optical-engineering/ansys-lumerical/SKILL.md` |

## 官方文檔與 APIKB 動態查詢強制令

在生成或修改任何數值模擬腳本之前，**必須**優先透過 MCP 查詢底層確切 API 簽名與參數：
- 使用 `search_ansys_docs(query='...')` 檢索該學科之官方手冊規範
- 使用 `api_search(query='...', product='speos')` 驗證 Python / ACT 符號之完整路徑
- 嚴禁憑空猜測非公開屬性或使用已廢棄之語法

## 關鍵禁止事項 (Critical Don'ts)

- 嚴禁在特徵尺寸接近波長的奈米微結構中使用幾何光學射線追跡（必須使用 FDTD）。
- 嚴禁在未指定色散模型的情況下載入寬光譜光源進行色差評估。
- 嚴禁將未達蒙地卡羅收斂的光線數（光子噪聲過大）直接用於量化輝度驗收。
