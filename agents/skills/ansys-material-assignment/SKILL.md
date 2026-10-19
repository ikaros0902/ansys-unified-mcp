---
name: ansys-material-assignment
description: ANSYS Mechanical 自動材料指派主控手冊。支援讀取 BOM Excel 清單、零件名稱正則關鍵字匹配、材料樹目錄建立與未賦予零件自動追蹤。
Use when:
  - 裝配體零件數量龐大，手動指派材料耗時且易遺漏，需從 BOM Excel 清單自動批次匹配材料。
  - 需透過零件命名規則與材料庫正則關鍵字（如 AL, STEEL, COPPER, FR4, RUBBER 等）自動指派材料。
  - 需過濾既有自訂材料（避免覆蓋已設定之特殊非線性材料）或跳過已抑制幾何。
  - 需在 Mechanical 自動生成 `[Mat] Unassigned_Bodies` 命名選擇群組以利人工覆核。
  - 觸發關鍵字 (繁中/En): ansys-material-assignment, 材料指派, BOM材料匹配, 自動賦予材料, Material Assignment, Assign Material from BOM.
phase_gate:
  requires: []
  produces: []
---

# ANSYS Mechanical 自動材料指派 (Material Assignment) 手冊

本技能規範基於 Excel BOM 表與零件名稱正則規則，在 ANSYS Mechanical 結構/熱分析環境中實現 100% 無遺漏的自動化材料賦予與品質前檢。

---

## 一、核心操作進入點 (Entry Points)

- **MCP 工具調用**：
  ```python
  await mechanical_assign_materials_from_bom(
      bom_file_path="D:/Project/BOM.xlsx",   # BOM Excel 檔案路徑
      overwrite_existing=False,             # 是否覆蓋非預設之既有材料 (預設保留)
      group_folders=True                    # 是否依材料建立樹狀資料夾收納
  )
  ```
- **ACT 腳本路徑**：
  `scripts/material_assignment_engine.py`

---

## 二、材料自動指派標準流程 (Standard SOP)

```mermaid
flowchart TD
    S1[1. BOM 表格與工程材料庫讀取<br/>解析 Excel 欄位與 Engineering Data 材料庫清單] --> S2[2. 幾何候選快照<br/>快照全模型 Bodies，過濾 Suppressed 零件與既有特殊材料]
    S2 --> S3[3. BOM 精確名稱與料號匹配<br/>清洗 CAD 零件名稱並與 DWG/JPN 料號對應]
    S3 --> S4[4. 內建關鍵字正則後備匹配<br/>若 BOM 未命中，以名稱關鍵字比對材料別名]
    S4 --> S5[5. 材料指派與目錄建立<br/>指派 Material 並建立分類資料夾，未命中者建立 [Mat] Unassigned_Bodies 群組]
```

### 1. 欄位自動探測機制
引擎自動掃描 Excel 前 10 行，辨識以下關鍵欄位：
- **料號欄**：`PART NUMBER`, `JPN`, `DWG`, `FILE NAME`, `ITEM`
- **品名欄**：`DESCRIPTION`, `DESC`, `COMMON NAME`
- **材料欄**：`MATERIAL`

### 2. 名稱清洗（CAD Cleaning）
自動剔除 SpaceClaim/Creo/SolidWorks 生成之冗餘後綴：
- 剔除 `Midsurface-` 前綴
- 剔除 `(Solid)`, `[Sheet]`, `[Body]` 標籤
- 剔除 `.prt.1`, `.asm.2` 等版本號

### 3. 未賦予零件防漏機制
未能命中的零件將被自動歸入 `[Mat] Unassigned_Bodies` 命名選擇，並在 3D 視圖中保持顯示，其餘已指派零件臨時隱藏，工程師可於 10 秒內完成視覺前檢。

---

## 三、工程參數對照 (Parameter Reference)

| 參數名稱 | 預設值 | 說明 |
| :--- | :--- | :--- |
| `bom_file_path` | `""` | Excel 檔案絕對路徑（若為空則僅跑關鍵字規則） |
| `overwrite_existing`| `False` | 是否覆蓋非預設（非 Structural Steel）之材料 |
| `group_folders` | `True` | 是否在幾何樹中按材料名稱建立資料夾歸納 |

詳細規則清單請參閱 [`references/bom_schema_guide.md`](references/bom_schema_guide.md)。

---

## 四、工程禁忌與注意事項 (Don'ts)

- **嚴禁暴力覆蓋既有非線性材料**：`overwrite_existing` 預設必須為 `False`，防止覆蓋已定義塑性硬化或超彈性參數的特殊零件。
- **嚴禁解譯已抑制零件**：已抑制幾何應跳過，避免在 Engineering Data 中引發無效材料引用。

## 內嵌腳本來源

執行 material_assignment_engine、rm_joint_creator、defeature、imprint_contacts、midsurface 或 rm_group 前，讀取 [宿主腳本唯一來源](../ansys-geometry-modeling/references/embedded_scripts.md)。products 為唯一來源，技能內歷史副本不作執行入口；由 CPython／MCP 讀原文送宿主。
