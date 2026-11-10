---
name: ansys-twin-scade
description: ANSYS Twin Builder digital twin ROM & SCADE safety-critical software. Covers reduced-order modeling, Modelica, V-model embedded control, and edge deployment.
---

# ANSYS-TWIN-SCADE: Systems & Digital Twin / Twin Builder ROM & SCADE Embedded Software

本技能為 ANSYS 模組技能 專業求解器模組，專責處理 Systems & Digital Twin / Twin Builder ROM & SCADE Embedded Software 之深度建模、邊界設置與求解後處理。

## 核心工作流 (Core Workflow)

1. 從 3D 物理場模擬（Mechanical/Fluent）中提煉降階模型（SVD, Dynamic ROM Builder）
2. 在 Twin Builder 中組裝 1D-0D 多領域系統電路（Modelica / VHDL-AMS）
3. 在 SCADE Suite 中以模型化設計（MBD）開發安全關鍵控制邏輯（C99 合規）
4. 執行軟體在環（SiL）與硬體在環（HiL）閉環協同模擬
5. 驗證嚴格符合 DO-178C / ISO 26262 功能安全軟體代碼生成
6. 將數位孿生模型導出為 FMI/FMU 或 Twin Deployer 邊緣端部署包

## 參考手冊導讀 (Reference Router)

| 關鍵需求 / 主題 | 推薦深入研讀之參考文件 |
|---|---|
| 核心物理設定與邊界條件 | [`references/`](references/) |
| 自動化腳本模板與 CLI 調用 | [`scripts/`](scripts/) |

## 官方文檔與 API 動態查詢強制令

在生成或修改任何程式碼之前，**必須**優先透過 MCP 查詢底層確切 API 簽名與參數：
- 使用 `search_ansys_docs(query='...')` 檢索官方手冊規範
- 使用 `api_search(query='...', product='scade_one')` 驗證 PyAnsys / IronPython 符號完整路徑
- 嚴禁憑空猜測非公開屬性或廢棄語法

## 關鍵禁止事項 (Critical Don'ts)

- 嚴禁在未驗證單位制（SI, CGS, N-mm-s）的前提下載入材料或邊界數值。
- 嚴禁硬編碼本地絕對路徑或使用未受管理的外部進程呼叫。
- 嚴禁跳過求解收斂性檢查而直接採信未收斂之數值結果。
