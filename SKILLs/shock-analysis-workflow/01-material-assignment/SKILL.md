---
name: shock-session-material-assignment
description: 自動化材料指派會話（Material Assignment Session），整合 ACT 關鍵字比對引擎、BOM 查表、SMT 元件正則匹配與小批次驗證機制。
---

# Session 01: 材料自動指派與驗證 (Material Assignment & Verification)

## 1. 目標 (Objective)
在 ANSYS Mechanical LS-DYNA 衝擊分析專案中，依據 CAD 幾何名稱、零件階層與 BOM 表，自動且精確地為全機所有 Body（實體與鈑金面）指派對應的物理材料模型（如 `*MAT_024 Piecewise Linear Plasticity` 彈塑性材料或線性彈性材料），並自動標記與隔離未匹配的孤兒物件。

---

## 2. ACT 比對引擎架構 (ACT Matching Engine Architecture)

本會話完整整合了 ACT 擴充套件 `MECH_Material_Assignment.py` 的核心匹配演算法，提供四級優先順序的比對階梯（Matching Hierarchy）：

```mermaid
flowchart TD
    A[CAD Body / Part 名稱] --> B[字串清理 clean_name_string]
    B --> C{優先級 1: BOM Lookup}
    C -- 命中 --> Z[指派材料 & 紀錄來源]
    C -- 未命中 --> D{優先級 2: 直接材料關鍵字}
    D -- 命中 --> Z
    D -- 未命中 --> E{優先級 3: 結構功能關鍵字}
    E -- 命中 --> Z
    E -- 未命中 --> F{優先級 4: SMT 元件正則表達式}
    F -- 命中 --> Z
    F -- 未命中 --> G[加入未指派清單]
    G --> H[建立 [Mat] Unassigned_Bodies NS]
```

---

## 3. 核心比對邏輯與參考手冊 (Progressive Disclosure)

- **CAD 名稱清理演算法 (`clean_name_string`)**：自動剔除 (Solid)、(Surface)、.prt.1 等 CAD 命名雜訊。
- **多階關鍵字比對字典 (`match_keyword_rules`)**：依序比對 SGCC、AL6061、SUS301、FR4、PC+ABS 及 SMT 正則。
- **孤兒物件管理 (`[Mat] Unassigned_Bodies`)**：未匹配物件自動群組建立 Named Selection，加速人工審查。
- **LS-DYNA `*MAT_024` 關鍵字卡片**：注入應變率相依 Cowper-Symonds 參數（C=40.0, P=5.0）。

> 完整演算法程式碼與 LS-DYNA 卡片定義，詳見專門手冊：
> - [`reference/material_mapping.md`](reference/material_mapping.md)

---

## 4. 小批次驗證章節 (Dedicated Verification Section)

為確保自動化指令之穩定性，禁止直接進行長時間求解。本工作流程採用 **10 個樣本 Body** 的小批次驗證機制。

### 4.1 驗證步驟
1. 透過 PyMechanical gRPC 連線至 Port 10000。
2. 隨機或循序選取 10 個幾何 Body（包含螺絲、鈑金 Surface、固定座 Solid）。
3. 執行字串清理與材料關鍵字匹配。
4. 驗證材料指派正確性及 `[Mat] Unassigned_Bodies` 建立狀態。
5. 輸出測試覆蓋率與詳細日誌。

### 4.2 獨立測試腳本執行方式
執行以下獨立測試腳本：
```powershell
python d:/Ikaros/ANSYS-unified-MCP/SKILLs/shock-analysis-workflow/scripts/test_session_01.py
```

### 4.3 驗證評估指標 (Verification Metrics)
- **樣本數量 (Sample Size)**: 10 Bodies
- **匹配成功率 (Coverage Rate)**: $\ge 90\%$
- **孤兒物件標記 (Orphan Tracking)**: 未匹配物件 100% 進入 `[Mat] Unassigned_Bodies`
- **模型無污染 (Cleanliness)**: 驗證完成後無殘留垃圾變數。

---

## 5. 相關參考手冊 (Related References)

| 手冊名稱 | 內容摘要 |
| :--- | :--- |
| [`reference/material_mapping.md`](reference/material_mapping.md) | 清理正規化、關鍵字比對表、孤兒 NS 建立與 *MAT_024 卡片 |
