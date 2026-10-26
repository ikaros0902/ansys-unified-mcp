---
name: ansys-acp-granta
description: ANSYS ACP composite layup/draping & Granta MI material intelligence. Covers ply stackup, Tsai-Wu failure, draping fiber distortion, and material BOM mapping.
---

# ANSYS-ACP-GRANTA: Materials & Composites / ACP Composite Layup & Granta MI Material Intelligence

本技能為 ANSYS Tier-2 專業求解器模組，專責處理 Materials & Composites / ACP Composite Layup & Granta MI Material Intelligence 之深度建模、邊界設置與求解後處理。

## 核心工作流 (Core Workflow)

1. 定義複材鋪層材料（碳纖維、玻璃纖維、環氧樹脂、蜂窩芯材）
2. 在 ANSYS ACP (Pre) 中定義幾何特徵鋪層方向（Rosettes, Look-up Directions）
3. 建立鋪層規則與布料覆蓋模擬（Draping Simulation 預測纖維角度剪切變形）
4. 生成實體複材單元（Solid Elements）或多層殼單元並傳遞至 Mechanical
5. 求解結構強度並在 ACP (Post) 中計算破壞準則（Tsai-Wu, Puck, Hashin Failure）
6. 透過 Granta MI 進行材料生命週期評估（LCA）與企業 BOM 材料智慧核准

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
