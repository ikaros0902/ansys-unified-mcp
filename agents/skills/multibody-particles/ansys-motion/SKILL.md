---
name: ansys-motion
description: ANSYS Motion multibody dynamics solver. Covers rigid/flexible bodies, gear trains, bushings, complex joints, contact dynamics, and modal stress recovery.
---

# ANSYS-MOTION: Multibody Dynamics / Rigid & Flexible Multibody Dynamics (MBD)

本技能為 ANSYS 模組技能 專業求解器模組，專責處理 Multibody Dynamics / Rigid & Flexible Multibody Dynamics (MBD) 之深度建模、邊界設置與求解後處理。

## 核心工作流 (Core Workflow)

1. 定義剛體與柔性體多體系統幾何拓撲（Subsystem Architecture）
2. 配置機構運動副與鉸鏈（Revolute, Prismatic, Spherical Joints, Bushings）
3. 定義非線性接觸對與齒輪嚙合接觸（Surface-to-Surface Contact & Gear Mesh）
4. 建立柔性體模型（Modal Superposition 或 Full Flexible Body）
5. 設定驅動運動或載荷工況（Kinematic Drivers & Force Actuators）
6. 求解運動響應並提取鉸鏈反力、振動位移與動態應力歷程

## 參考手冊導讀 (Reference Router)

| 關鍵需求 / 主題 | 推薦深入研讀之參考文件 |
|---|---|
| 核心物理設定與邊界條件 | [`references/`](references/) |
| 自動化腳本模板與 CLI 調用 | [`scripts/`](scripts/) |

## 官方文檔與 API 動態查詢強制令

在生成或修改任何程式碼之前，**必須**優先透過 MCP 查詢底層確切 API 簽名與參數：
- 使用 `search_ansys_docs(query='...')` 檢索官方手冊規範
- 使用 `api_search(query='...', product='motion')` 驗證 PyAnsys / IronPython 符號完整路徑
- 嚴禁憑空猜測非公開屬性或廢棄語法

## 關鍵禁止事項 (Critical Don'ts)

- 嚴禁在未驗證單位制（SI, CGS, N-mm-s）的前提下載入材料或邊界數值。
- 嚴禁硬編碼本地絕對路徑或使用未受管理的外部進程呼叫。
- 嚴禁跳過求解收斂性檢查而直接採信未收斂之數值結果。
