---
name: ansys-cfx
description: ANSYS CFX turbomachinery and rotating machinery solver workflow. Covers setup, CCL scripting, blade gen, multi-stage interfaces, and solver monitoring.
---

# ANSYS-CFX: CFD / Turbomachinery & Rotating Machinery

本技能為 ANSYS Tier-2 專業求解器模組，專責處理 CFD / Turbomachinery & Rotating Machinery 之深度建模、邊界設置與求解後處理。

## 核心工作流 (Core Workflow)

1. 定義渦輪幾何與旋轉座標系（Turbomachinery Domains & Frames）
2. 配置流體物理屬性與湍流模型（SST / k-epsilon / Transition SST）
3. 設定旋轉-靜止交界面（Stage, Frozen Rotor, Transient Rotor-Stator）
4. 透過 CCL (CFX Command Language) 腳本載入網格與邊界條件
5. 提交 CFX-Solver 求解並即時監控殘差收斂度（RMS Residuals < 1e-4）
6. 後處理 CFD-Post 抽取總壓損失、等熵效率與葉片表面壓力分佈

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
