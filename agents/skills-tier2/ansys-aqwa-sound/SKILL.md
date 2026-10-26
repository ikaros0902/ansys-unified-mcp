---
name: ansys-aqwa-sound
description: ANSYS AQWA marine hydrodynamic diffraction/radiation & Ansys Sound psychoacoustics. Covers wave loads, mooring, RAO, sound quality, and psychoacoustic metrics.
---

# ANSYS-AQWA-SOUND: Hydrodynamics & Acoustics / Marine AQWA & Ansys Sound Psychoacoustics

本技能為 ANSYS Tier-2 專業求解器模組，專責處理 Hydrodynamics & Acoustics / Marine AQWA & Ansys Sound Psychoacoustics 之深度建模、邊界設置與求解後處理。

## 核心工作流 (Core Workflow)

1. 定義浮體水動力學幾何與壓載條件（Ballast & Center of Gravity CG）
2. 在 AQWA 中計算波浪繞射/輻射力與幅值響應算子（RAO, Response Amplitude Operators）
3. 配置系泊纜繩（Mooring Lines, Tethers）與二階波漂移力
4. 在 Mechanical / Fluent 中計算振動發聲源與聲壓分佈
5. 導入聲壓信號至 Ansys Sound 進行時頻濾波與階次分析（Order Tracking）
6. 計算心理聲學客觀指標（響度 Loudness, 尖銳度 Sharpness, 粗糙度 Roughness）

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
