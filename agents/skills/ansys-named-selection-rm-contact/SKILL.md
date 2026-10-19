---
name: ansys-named-selection-rm-contact
description: SpaceClaim 幾何端產出的 Named Selection 命名慣例與 Mechanical/thermal/LS-DYNA 消費端 ACT 行為橋接手冊。顯性化既有腳本中隱藏的前綴、後綴與分隔符號規則，涵蓋 Connect Topology bonded 接觸、Scr_RM_grp 螺絲孔配對群組、Mobile/Reference 運動副後綴與遠端點命名，供 server/機構衝擊分析、wireline、payment 等多產品線跨工具鏈共用判讀。
license: Proprietary
compatibility: ANSYS SpaceClaim 2023 R1 以上 (建立端 IronPython 2.7)；ANSYS Mechanical 2023R1+ ACT 或 PyMechanical gRPC (消費端)。
---

# Named Selection 命名慣例橋接手冊 (SpaceClaim → Mechanical/thermal/LS-DYNA)

本技能不建立新的連接邏輯，而是將分散在 `bonded_contact_creator.py`、`rm_joint_creator.py`、`rm_hole_group_hierarchical.ironpy`（SC_RM_grp_creation 引擎）等腳本中**隱性**的命名約定，整理成**顯性**的規則總表，作為 SpaceClaim 產出端與 Mechanical/thermal/LS-DYNA 消費端之間的契約文件。

---

## 一、命名規則總覽 (Naming Convention Overview)

| 命名模式 | 分隔符號 | 來源腳本 | 下游消費端行為 |
|---|---|---|---|
| `Connect Topology*`（前綴，恰好 2 個幾何實體） | 無固定分隔，前綴比對 | `bonded_contact_creator.py` / `Mech_bonded.py` | 建立 `Bonded` Contact Region，`SourceLocation`/`TargetLocation` 取 `Location.Ids[0]`/`[1]` |
| `Scr_RM_grp_<N>` / 可選距離後綴 `_Near` `_Medium` `_Far` | `_` 底線分隔 index | `rm_hole_group_hierarchical.ironpy`（SC_RM_grp_creation 引擎） | 作為螺絲孔配對候選群組，交給下游建立 Remote Point 或 Joint |
| `Scr_RMgrp_ALL` | 固定全域匯總名，**不可**被當作一般 RM 群組處理 | `rm_hole_group_hierarchical.ironpy` | 消費端必須明確排除（`!= 'Scr_RMgrp_ALL'`），否則重複處理全部孔邊造成誤判 |
| `<RMP_Name_Prefix><base>_Mobile` / `<RMP_Name_Prefix><base>_Reference` | `_Mobile` / `_Reference` 固定後綴 | `rm_joint_creator.py` / `MECH_RM_Joint_Creation.py` | 依 `base` 配對，建立 `BodyToBody` Joint（Fixed/Revolute/Cylindrical），Mobile→`MobileLocation`，Reference→`ReferenceLocation` |
| `<RMP_Name_Prefix><name>`（無 Mobile/Reference 後綴，單一 NS） | 無固定分隔 | `rm_joint_creator.py`（`ConnectionMethod='RemotePoint'` 分支） | 建立單一 `RemotePoint`，`Behavior=Rigid`，6 DOF 全啟用 |
| `<joint_name> - Reference Remote Point` / `<joint_name> - Mobile Remote Point` | `" - "` 空格減號空格 | `rm_joint_creator.py` 刪除邏輯 | Joint 被 `PromoteToRemotePoint()` 後系統自動產生的衍生 Remote Point 名稱，刪除 Joint 時必須連動刪除這兩個衍生物件 |
| `_FullCircles` / `_HalfCircles`（接在 `grp_name_create` 之後） | `_` 底線後綴 | `rm_hole_group_hierarchical.ironpy` | 分流圓孔邊 (`FullCircles`) 與半圓/斷裂圓弧邊 (`HalfCircles`)，供孔徑分類網格劃分參考，非直接連接建立輸入 |
| `[Mat] Unassigned_Bodies` | 方括號分類標籤前綴 | `ansys-material-assignment` 技能（交叉引用，非本技能產出） | 本技能命名規則與材料指派標籤**互不衝突**，可共存於同一模型 |

完整命名字典（每條規則附來源行號與用途）見 [`references/naming_convention_reference.md`](references/naming_convention_reference.md)。

---

## 二、跨下游解讀差異（static / thermal / LS-DYNA）

同一組命名在三種分析類型下的解讀存在關鍵差異（例如 `Behavior` 預設值、Pinball 半徑單位意義、Joint 的 UnderDefined 處置），完整比較表見 [`references/cross_product_consumption_matrix.md`](references/cross_product_consumption_matrix.md)。核心原則：
1. **static/thermal**：Remote Point 的 `Behavior` 依工況可選 `Rigid` 或 `Deformable`；thermal 額外需確認是否影響虛假熱傳導路徑。
2. **LS-DYNA 顯式**：螺絲孔類多點共用遠端點**必須**強制 `Deformable`，否則觸發 `Error 20110`（詳見 `ansys-mechanical-connections` 技能）。
3. **命名規則本身不隨分析類型改變**——改變的只是下游消費端如何設定建立出來物件的屬性。

---

## 三、驗證入口

執行 [`scripts/validate_ns_naming_convention.ironpy`](scripts/validate_ns_naming_convention.ironpy)：掃描模型全部 Named Selection，依本手冊規則逐一比對，產出合規/不合規清單（含不合規原因，如「`_Mobile` 存在但找不到對應 `_Reference`」、「`Connect Topology*` 命名但實體數不等於 2」）。

---

## 四、絕不能做清單 (Don'ts)

> [!CAUTION]
> 1. **嚴禁將 `Scr_RMgrp_ALL` 當作一般 RM 群組納入配對或建立邏輯**：此名稱為 SC_RM_grp_creation 引擎的全域匯總標記，所有消費端腳本（`rm_joint_creator.py`、`MECH_RM_Joint_Creation.py`）皆明確排除，新腳本必須延續此排除規則。
> 2. **嚴禁假設 `_Mobile` 與 `_Reference` 一定成對出現**：SpaceClaim 端若只建立了其中一側（例如幾何缺失或人工誤刪），消費端必須能偵測並跳過（記錄為不合規），不可盲目假設配對完整直接建立 Joint 導致 Scoping 例外。
> 3. **嚴禁對 `Connect Topology*` 命名但實體數不等於 2 的 NS 建立 Bonded Contact**：`bonded_contact_creator.py` 原始邏輯僅接受 `len(pair_check) == 2`，超過或少於 2 個實體屬命名誤用，必須攔截並回報，不可強行指派造成錯誤的 Source/Target。
> 4. **嚴禁跨技能重複定義相同命名規則**：接觸類型列舉、Pinball 公式等已於 `ansys-mechanical-connections` / `ansys-mechanical` 定義者，本技能僅引用不重複展開；本技能專注於「命名規則本身」而非「建立邏輯細節」。
> 5. **嚴禁憑記憶臆測未在來源腳本出現過的命名後綴**：若需要新增命名規則（如假設性的 `_Thermal` 後綴），必須先確認是否已有腳本實作，若無則在 references 中標註「待來源腳本查證，目前僅為提案」，不可當作既有規範收錄。

## 官方範例路由

需重現官方輸入與輸出驗收時，讀取 [references/official_examples.md](references/official_examples.md)；依該文件分開檢查啟動、模型修改與求解授權。

## 內嵌腳本來源

執行 material_assignment_engine、rm_joint_creator、defeature、imprint_contacts、midsurface 或 rm_group 前，讀取 [宿主腳本唯一來源](../ansys-geometry-modeling/references/embedded_scripts.md)。products 為唯一來源，技能內歷史副本不作執行入口；由 CPython／MCP 讀原文送宿主。
