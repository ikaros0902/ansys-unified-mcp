---
name: ansys-q3d-siwave
description: ANSYS Q3D Extractor & SIwave simulation for PCB/IC packaging. Covers RLCG parasitic extraction, S-parameter touchstone models, impedance & voltage drop.
---

# ANSYS-Q3D-SIWAVE: Electromagnetics / Signal & Power Integrity, Parasitic Extraction

本技能為 ANSYS 模組技能 專業求解器模組，專責處理 Electromagnetics / Signal & Power Integrity, Parasitic Extraction 之深度建模、邊界設置與求解後處理。

## 核心工作流 (Core Workflow)

1. 導入 ECAD 幾何（ODB++, IPC-2581, GDSII 或 BRD 檔）
2. 定義 PCB 疊層材料特性（Dielectric Constant Dk, Loss Tangent Df）
3. 指派信號線、電源網（Power Net）與接地網（Ground Net）分類
4. 在 Q3D 中提取導線寄生參數（Partial Inductance & Capacitance Matrix）
5. 在 SIwave 中執行直流電壓降（DC IR Drop）與電流密度評估
6. 導出 Touchstone S 參數模型供高速時域模擬（SPICE / IBIS-AMI）使用

## 參考手冊導讀 (Reference Router)

| 關鍵需求 / 主題 | 推薦深入研讀之參考文件 |
|---|---|
| 核心物理設定與邊界條件 | [`references/`](references/) |
| 自動化腳本模板與 CLI 調用 | [`scripts/`](scripts/) |

## 官方文檔與 API 動態查詢強制令

在生成或修改任何程式碼之前，**必須**優先透過 MCP 查詢底層確切 API 簽名與參數：
- 使用 `search_ansys_docs(query='...')` 檢索官方手冊規範
- 使用 `api_search(query='...', product='pyaedt')` 驗證 PyAnsys / IronPython 符號完整路徑
- 嚴禁憑空猜測非公開屬性或廢棄語法

## 關鍵禁止事項 (Critical Don'ts)

- 嚴禁在未驗證單位制（SI, CGS, N-mm-s）的前提下載入材料或邊界數值。
- 嚴禁硬編碼本地絕對路徑或使用未受管理的外部進程呼叫。
- 嚴禁跳過求解收斂性檢查而直接採信未收斂之數值結果。
