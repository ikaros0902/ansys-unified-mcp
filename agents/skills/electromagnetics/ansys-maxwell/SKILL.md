---
name: ansys-maxwell
description: ANSYS Maxwell low-frequency electromagnetic simulation. Covers 2D/3D magnetostatics, transient motors, eddy currents, core loss, and torque ripple.
---

# ANSYS-MAXWELL: Electromagnetics / Low-Frequency EM, Motors, Actuators & Transformers

本技能為 ANSYS 模組技能 專業求解器模組，專責處理 Electromagnetics / Low-Frequency EM, Motors, Actuators & Transformers 之深度建模、邊界設置與求解後處理。

## 核心工作流 (Core Workflow)

1. 定義 2D 旋轉對稱或 3D 電磁幾何（Rotor, Stator, Coils, Permanent Magnets）
2. 指派鐵心 BH 非線性磁化曲線與永磁體去磁特性（Demagnetization Curves）
3. 設定繞組電流/電壓激勵源（Stranded / Solid Windings, External Circuit）
4. 定義運動邊界（Band Object, Rotation / Translation Motion Setup）
5. 配置瞬態時間步長與網格運動求解器
6. 求解並提取反電動勢（Back-EMF）、轉矩漣波（Torque Ripple）、鐵損與渦流分佈

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
