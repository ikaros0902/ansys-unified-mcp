---
name: ansys-motorcad
description: ANSYS Motor-CAD motor design suite. Covers electromagnetic (EMag), thermal (Lab), and mechanical stress sizing across drive duty cycles.
---

# ANSYS-MOTORCAD: Electromagnetics & Multiphysics / Motor Multiphysics Fast Sizing

本技能為 ANSYS 模組技能 專業求解器模組，專責處理 Electromagnetics & Multiphysics / Motor Multiphysics Fast Sizing 之深度建模、邊界設置與求解後處理。

## 核心工作流 (Core Workflow)

1. 定義電機幾何拓撲（Slot/Pole 槽極匹配、轉子磁鋼排布 V-shape, Interior PM）
2. 快速解析求解電磁特性（Torque-Speed Efficiency Map, Cogging Torque）
3. 建立等效熱路阻抗網路（Lumped Parameter Thermal Network, LPTN）
4. 計算水冷套、油冷或自然風冷散熱通道對繞組溫升之影響
5. 評估轉子高速離心力應力與護套厚度（Mechanical Stress & Rotor Containment）
6. 導出至 Maxwell / Fluent / optiSLang 進行深度多物理高精度驗證

## 參考手冊導讀 (Reference Router)

| 關鍵需求 / 主題 | 推薦深入研讀之參考文件 |
|---|---|
| 核心物理設定與邊界條件 | [`references/`](references/) |
| 自動化腳本模板與 CLI 調用 | [`scripts/`](scripts/) |

## 官方文檔與 API 動態查詢強制令

在生成或修改任何程式碼之前，**必須**優先透過 MCP 查詢底層確切 API 簽名與參數：
- 使用 `search_ansys_docs(query='...')` 檢索官方手冊規範
- 使用 `api_search(query='...', product='motorcad')` 驗證 PyAnsys / IronPython 符號完整路徑
- 嚴禁憑空猜測非公開屬性或廢棄語法

## 關鍵禁止事項 (Critical Don'ts)

- 嚴禁在未驗證單位制（SI, CGS, N-mm-s）的前提下載入材料或邊界數值。
- 嚴禁硬編碼本地絕對路徑或使用未受管理的外部進程呼叫。
- 嚴禁跳過求解收斂性檢查而直接採信未收斂之數值結果。
