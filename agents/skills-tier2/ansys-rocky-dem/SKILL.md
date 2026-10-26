---
name: ansys-rocky-dem
description: ANSYS Rocky discrete element method (DEM) particle solver. Covers polyhedral & custom particle shapes, breakage, abrasive wear, and CFD-DEM coupling.
---

# ANSYS-ROCKY-DEM: Particles & Granular Dynamics / Discrete Element Method (DEM)

本技能為 ANSYS Tier-2 專業求解器模組，專責處理 Particles & Granular Dynamics / Discrete Element Method (DEM) 之深度建模、邊界設置與求解後處理。

## 核心工作流 (Core Workflow)

1. 定義顆粒幾何形狀（真實多面體 Polyhedral, 纖維狀 Fibers, 圓形顆粒）
2. 設定材料物理力學特性（密度、恢復係數、靜動摩擦係數、表面能/黏性模型）
3. 定義邊界幾何運動（輸送帶、滾筒旋轉、振動篩板振幅頻率）
4. 配置顆粒破碎模型（TBR, Ab-T10 Breakage Models）或黏性粉體模型
5. 配置求解器（GPU / Multi-GPU 加速時間步長演進）
6. 評估物料流率、顆粒偏析（Segregation）、壁面磨損深度與 CFD-DEM 曳力

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
