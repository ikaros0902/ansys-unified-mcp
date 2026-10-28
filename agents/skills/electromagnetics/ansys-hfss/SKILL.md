---
name: ansys-hfss
description: ANSYS HFSS high-frequency full-wave EM simulation. Covers S-parameters, microstrip & array antennas, radar cross section (RCS), and radiated emissions.
---

# ANSYS-HFSS: Electromagnetics / High-Frequency EM, Antennas, Radar & RF Systems

本技能為 ANSYS 模組技能 專業求解器模組，專責處理 Electromagnetics / High-Frequency EM, Antennas, Radar & RF Systems 之深度建模、邊界設置與求解後處理。

## 核心工作流 (Core Workflow)

1. 建立 3D 電磁結構幾何與封裝基板堆疊（3D Layout / Substrate Stackup）
2. 指派材料介電係數、損耗角正切與導體表面粗糙度（Huray / Hammerstad）
3. 定義激勵端口（Wave Port, Lumped Port）與輻射吸收邊界（PML / Radiation Boundary）
4. 設定適應性網格剖分頻率（Adaptive Meshing Solution Frequency & Delta S）
5. 配置頻率掃描（Interpolating, Fast, Discrete Frequency Sweep）
6. 求解並提取 S/Y/Z 參數、增益輻射場型（Far-field 3D Radiation Pattern）與 RCS

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
