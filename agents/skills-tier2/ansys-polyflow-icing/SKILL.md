---
name: ansys-polyflow-icing
description: ANSYS Polyflow polymer processing & FENSAP-ICE aircraft icing simulation. Covers viscoelastic fluids, die swell, droplet impingement, and ice accretion.
---

# ANSYS-POLYFLOW-ICING: CFD / Polymer Extrusion, Blow Molding & In-Flight Icing (FENSAP-ICE)

本技能為 ANSYS Tier-2 專業求解器模組，專責處理 CFD / Polymer Extrusion, Blow Molding & In-Flight Icing (FENSAP-ICE) 之深度建模、邊界設置與求解後處理。

## 核心工作流 (Core Workflow)

1. 定義非牛頓黏性與黏彈性流體本構方程（Bird-Carreau, Cross, Phan-Thien-Tanner）
2. 幾何模頭與自由表面網格自動重劃（Adaptive Remeshing for Free Surfaces）
3. 模頭擠出脹大（Die Swell）與中空吹塑壁厚預測求解
4. 在 FENSAP-ICE 中配置大氣結冰條件（LWC, MVD, Static Temperature）
5. 水滴軌跡與撞擊極限計算（Droplet Impingement Limits）
6. 表面結冰累積形狀預測（Rime / Glaze Ice Accretion）

## 參考手冊導讀 (Reference Router)

| 關鍵需求 / 主題 | 推薦深入研讀之參考文件 |
|---|---|
| 核心物理設定與邊界條件 | [`references/`](references/) |
| 自動化腳本模板與 CLI 調用 | [`scripts/`](scripts/) |

## 官方文檔與 API 動態查詢強制令

在生成或修改任何程式碼之前，**必須**優先透過 MCP 查詢底層確切 API 簽名與參數：
- 使用 `search_ansys_docs(query='...')` 檢索官方手冊規範
- 使用 `api_search(pattern='...')` 驗證 PyAnsys / IronPython 符號完整路徑
- 嚴禁憑空猜測非公開屬性或廢棄語法

## 關鍵禁止事項 (Critical Don'ts)

- 嚴禁在未驗證單位制（SI, CGS, N-mm-s）的前提下載入材料或邊界數值。
- 嚴禁硬編碼本地絕對路徑或使用未受管理的外部進程呼叫。
- 嚴禁跳過求解收斂性檢查而直接採信未收斂之數值結果。
