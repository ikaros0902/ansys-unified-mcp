---
name: ansys-system-coupling
description: ANSYS System Coupling (SyC) co-simulation. Coordinates 2-way Fluid-Structure Interaction (FSI), Conjugate Heat Transfer (CHT), and Electro-Thermal coupling.
---

# ANSYS-SYSTEM-COUPLING: Systems & Multiphysics / 2-Way Multi-Field System Coupling (SyC)

本技能為 ANSYS 模組技能 專業求解器模組，專責處理 Systems & Multiphysics / 2-Way Multi-Field System Coupling (SyC) 之深度建模、邊界設置與求解後處理。

## 核心工作流 (Core Workflow)

1. 定義參與耦合之單物理求解器模組（Fluent, CFX, Mechanical, MAPDL）
2. 在各參與求解器中配置耦合交界面（Fluid-Solid Interface Boundaries）
3. 建立 System Coupling 伺服器並建立交界面配對（Data Transfer Pairs）
4. 指定雙向傳遞物理量（Displacement, Force, Heat Rate, Temperature）
5. 設定時間步進階協同算法（Implicit Fixed-Point Iterations, Under-Relaxation）
6. 執行聯合求解並監控界面資料守恆性與收斂殘差

## 參考手冊導讀 (Reference Router)

| 關鍵需求 / 主題 | 推薦深入研讀之參考文件 |
|---|---|
| 核心物理設定與邊界條件 | [`references/`](references/) |
| 自動化腳本模板與 CLI 調用 | [`scripts/`](scripts/) |

## 官方文檔與 API 動態查詢強制令

在生成或修改任何程式碼之前，**必須**優先透過 MCP 查詢底層確切 API 簽名與參數：
- 使用 `search_ansys_docs(query='...')` 檢索官方手冊規範
- 使用 `api_search(query='...', product='system_coupling')` 驗證 PyAnsys / IronPython 符號完整路徑
- 嚴禁憑空猜測非公開屬性或廢棄語法

## 關鍵禁止事項 (Critical Don'ts)

- 嚴禁在未驗證單位制（SI, CGS, N-mm-s）的前提下載入材料或邊界數值。
- 嚴禁硬編碼本地絕對路徑或使用未受管理的外部進程呼叫。
- 嚴禁跳過求解收斂性檢查而直接採信未收斂之數值結果。
