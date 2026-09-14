---
name: shock-session-connection-rm
description: 遠端點 (Remote Point)、遠端質量 (Remote Mass) 配置會話，包含過度約束防呆 (Error 20110)、空 NS 過濾、Deformable 設定與飛出零件拓撲預檢。
---

# Session 04: 連線、遠端質量配置與拓撲防呆預檢 (Connection, Remote Mass & Topology Pre-Checks)

## 1. 目標 (Objective)
在 LS-DYNA 衝擊分析模型中，精確建立螺絲緊固點的 MPC 遠端點（Remote Points）與等效配重（Remote Mass），並透過拓撲預檢機制防止：
1. **過度約束 (Over-Constraining / LS-DYNA Error 20110)**：避免剛性遠端點過度鎖死鈑金自由度導致奇異性或多重剛體約束錯誤。
2. **空集合報錯 (Empty Named Selection Errors)**：自動過濾 CAD 無效特徵或包含 0 實體的空 NS。
3. **未約束飛出零件 (Unconstrained Flying Bodies)**：在求解前確保全機每個零件均具備接觸、關節或邊界約束。

---

## 2. 核心防呆機制與建立演算法 (Core Pre-Check & Creation Algorithms)

```mermaid
flowchart TD
    A[掃描全機 Named Selections] --> B{實體數量檢查 Entities.Count > 0?}
    B -- 否 (0 實體) --> C[自動過濾跳過 避免錯誤]
    B -- 是 --> D{判斷目標類型}
    D -- 螺絲孔 / 鈑金介面 --> E[建立 Remote Point]
    E --> F[設定 Behavior = Deformable 防呆 Error 20110]
    D -- 模組等效配重 --> G[建立 Point Mass (Remote Mass)]
    G --> H[指定質量數值與轉動慣量]
    D --> I[全機零件拓撲連線檢查]
    I --> J{連線數 == 0?}
    J -- 是 --> K[發出 CRITICAL ALERT 飛出警示]
    J -- 否 --> L[拓撲檢查通過 進入求解準備]
```

---

## 3. 連線演算法與參考手冊 (Progressive Disclosure)

- **過度約束防呆與 Error 20110 消除**：螺絲 MPC 遠端點強制指派 `Behavior = LoadBehavior.Deformable`，避免共用節點引發多重剛體崩潰。
- **空集合自動過濾**：跳過 `Entities.Count == 0` 之空 NS，杜絕 Scoping 例外。
- **MPC 與集中質量區分**：Remote Point 傳遞 6-DOF 位移與反力；Point Mass 模擬模組配重。
- **飛出零件拓撲檢查 (`verify_body_topology`)**：求解前驗證所有作用中 Body 具備幾何實體與有效約束。

> 完整遠端點建立腳本、Error 20110 防呆機制與拓撲檢查代碼，詳見專門手冊：
> - [`reference/remote_point_algorithms.md`](reference/remote_point_algorithms.md)

---

## 4. 小批次驗證章節 (Dedicated Verification Section)

本會話提供小型單元測試腳本，驗證 5 個樣本 RM Named Selection 的空集合過濾、Deformable 行為指派以及 5 個樣本零件的拓撲健全度。

### 4.1 驗證步驟
1. 透過 PyMechanical gRPC 連線至 Port 10000。
2. 掃描所有 Named Selections，統計並過濾實體數為 0 的空集合。
3. 選取 5 個候選 RM/螺絲孔 Named Selections。
4. 建立 5 個 Remote Points 並斷言其 `Behavior == Deformable`。
5. 對 5 個樣本 Body 執行拓撲幾何有效性檢查。
6. 安全刪除 5 個測試 Remote Points，確保模型無殘留垃圾物件。

### 4.2 獨立測試腳本執行方式
執行以下獨立測試腳本：
```powershell
python d:/Ikaros/ANSYS-unified-MCP/SKILLs/shock-analysis-workflow/scripts/test_session_04.py
```

### 4.3 驗證評估指標 (Verification Metrics)
- **樣本 RM Named Selections**: 5 (Entities > 0)
- **空白 Named Selections 自動過濾**: PASS
- **Remote Point Deformable 行為設定**: 100% (5 / 5)
- **LS-DYNA Error 20110 防護機制**: ACTIVE
- **拓撲有效性檢核**: PASS (5 / 5)
- **模型無污染狀態 (Pristine State)**: 100% 乾淨（0 殘留測試 Remote Points）

---

## 5. 相關參考手冊 (Related References)

| 手冊名稱 | 內容摘要 |
| :--- | :--- |
| [`reference/remote_point_algorithms.md`](reference/remote_point_algorithms.md) | 螺絲 Deformable 遠端點建立、MPC 與 Point Mass 區分及飛出零件拓撲檢查 |
