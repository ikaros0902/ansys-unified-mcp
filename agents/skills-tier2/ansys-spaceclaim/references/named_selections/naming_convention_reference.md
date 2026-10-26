# 完整命名字典 (Naming Convention Reference)

本手冊逐條列出所有已確認存在於既有腳本中的命名規則，每條附來源腳本與用途。嚴禁收錄未經來源腳本確認的命名慣例。

---

## 一、Bonded Contact：`Connect Topology` 前綴

| 項目 | 內容 |
| :--- | :--- |
| 命名模式 | `Connect Topology` 開頭（SpaceClaim Share Topology / Connect 功能的系統預設命名，非自訂字串） |
| 判定條件 | `i.Name[0:len("Connect Topology")] == "Connect Topology"` 且 `len(i.Location.Ids) == 2` |
| 中文語系陷阱與轉譯 | 中文版 SpaceClaim 之 `ShareTopologyNamedSelection` 預設生成「連接拓撲1/2/3」，**下游 Mechanical ACT 會因全英文比對而漏讀**！產出端腳本必須於生成後自動將「連接拓撲*」重命名為全英文 ASCII `Connect Topology <N>`。 |
| 雙軌輔助命名 (可選) | 若需支援手動 Scoping 或依零件區分接觸面，可額外產出本體層級集合：`NS_Contact_<BodyName>`（如 `NS_Contact_Slot`、`NS_Contact_DIMM`），收納該零件上所有參與接觸的面（面數 $\ge 1$）。注意：本體層級集合**不可**冠上 `Connect Topology` 前綴，以維持 2-face 契約乾淨。 |
| 來源腳本 | `D:\Ikaros\ACT_Test\MECH_Joint_Creation.py`（`findText = "Connect Topology"`）；整合版 `agents/skills/ansys-mechanical/scripts/bonded_contact_creator.py`；`20230925_SC_Boned` |
| 下游用途 | 批次建立 `Bonded` ContactRegion：`SourceLocation` 取 `pair_check[0]`，`TargetLocation` 取 `pair_check[1]` |
| 群組歸納 | 所有由此規則建立的 Contact 會被收納進 `_Bonded_by_script` ConnectionGroup（若不存在則自動建立） |
| 去重機制 | 建立前檢查 `connections_bonded_grp.Children` 現有名稱清單 `bondedList`，避免重複建立同名 Contact |
| 參數設定 | `PinballRegion = ContactPinballType.Radius`，`PinballRadius = pinBallRadius * 2 [mm]`，`BondedMaximumOffset` 同值，`ShellThicknessEffect = False` |

---

## 二、螺絲孔配對群組：`Scr_RM_grp` 系列

| 項目 | 內容 |
| :--- | :--- |
| 基礎前綴 | `RM_grp_name_create` 參數值（ACT wizard 預設常用 `Scr_RM_grp`），實際字串由 UI 屬性注入，非寫死常數 |
| 編號規則 | `GetGroupNameANDIndex()` 以 `<prefix>_<index>` 形式遞增編號，索引從 `Index_RM_start` 起算，遇重名自動 +1 直到唯一 |
| 距離分級後綴（可選） | `_Near`（`<= Distance_Level1`）/ `_Medium`（`<= Distance_Level2`）/ `_Far`（其餘），僅在 `Enable_Distance_Grouping=True` 時附加，由 `GetDistanceSuffix()` 產生 |
| 來源腳本 | `D:\Ikaros\ACT_Test\SC_RM\SC_RM_grp_creation\SC_RM_grp_creation.py`；整合版 `agents/skills/ansys-spaceclaim-modeling/scripts/rm_hole_group_hierarchical.ironpy` |
| 全域匯總標記 | `Scr_RMgrp_ALL`（固定字串，不含 index）：收納所有符合 `RM_grp_name_create` 規則的邊元素總和，供快速全選；**所有迴圈必須明確排除此名稱**（`if grp_name == 'Scr_RMgrp_ALL': continue`） |
| 配對演算法輸入 | 孔邊 (circle edge) 或任意邊 (`mode=0`/`mode=1`)，依距離、軸線平行度、法向夾角等門檻（`Holes_axis_dist_max`, `Deg_max_circles`）判定是否互為配對 |
| 階層策略標記（非命名，為內部統計） | `Pairing_Strategy` 控制「Ignore Component」vs「Within Component」比對範圍，影響配對結果但不寫入命名字串本身 |

### 2.1 圓孔分類輔助群組（`mode=0` 專用，非配對群組）

| 命名 | 內容 | 來源 |
| :--- | :--- | :--- |
| `<grp_name_create>_FullCircles` | 完整圓周邊（`length > 2*pi*r`，即非斷裂整圓） | `rm_hole_group_hierarchical.ironpy` 之 `grp_name_FullCircle_edges` |
| `<grp_name_create>_HalfCircles` | 半圓/斷裂圓弧邊（`length < 2*pi*r*0.51` 且 `> 2*pi*r*0.49`） | 同上 `grp_name_HalfCircle_edges` |

此二群組是候選孔洞的分類輸出，**不是** Mobile/Reference 連接配對的輸入，不應被 Joint 建立腳本誤讀取。

---

## 三、運動副與遠端點：`_Mobile` / `_Reference` 後綴

| 項目 | 內容 |
| :--- | :--- |
| 命名模式 | `<RMP_Name_Prefix><base_name>_Mobile` 與 `<RMP_Name_Prefix><base_name>_Reference` 成對出現 |
| 參數來源 | `RMP_Name_Prefix`（ACT 屬性，無固定預設字串，依工程命名慣例注入，常見如 `RMP_` 或 `Scr_RM_grp` 本身） |
| 後綴可覆寫 | `Mobile_suffix` / `Reference_suffix`（預設 `"_Mobile"` / `"_Reference"`，`MECH_Joint_Creation.py` 允許透過 `step.Properties` 覆寫；`rm_joint_creator.py` 固定寫死不可覆寫） |
| 來源腳本 | `D:\Ikaros\ACT_Test\MECH_Joint_Creation.py`；`agents/skills/ansys-mechanical/scripts/rm_joint_creator.py`（固定前綴 `RM_Name_Prefix = "Scr_RM_grp"`，僅建立 Revolute） |
| 配對邏輯 | 以 `body_entities_map` 依 `entity.Bodies[0].Id` 分組，**必須恰好 2 個不同 Body** 才建立 Joint；否則記錄為 Skip |
| Joint 類型對應 | `ConnectionMethod` 屬性值對應 `JointType.Fixed` / `Revolute` / `Cylindrical`；`rm_joint_creator.py` 僅支援 Revolute（無 `ConnectionMethod` 分支） |
| 衍生命名（Promote 後） | `<joint_name> - Reference Remote Point` / `<joint_name> - Mobile Remote Point`（系統自動產生，`" - "` 為空格減號空格），刪除 Joint 時 `MECH_Joint_Creation.py` 會連動以 `ExtAPI.DataModel.GetObjectsByName()` 查找並刪除 |

---

## 四、單一遠端點：無 Mobile/Reference 後綴

| 項目 | 內容 |
| :--- | :--- |
| 命名模式 | `<RMP_Name_Prefix><name>`，不含 `_Mobile` / `_Reference` 後綴，且不等於 `Scr_RMgrp_ALL` |
| 觸發條件 | `step.Properties['ConnectionMethod'].Value == 'Remote Point'` 分支 |
| 來源腳本 | `D:\Ikaros\ACT_Test\MECH_Joint_Creation.py` |
| 過濾規則 | `ns.Entities.Count <= 1` 時跳過；單一實體且 `Bodies[0].Volume != 0`（代表只涵蓋單一實心零件、非跨零件介面）亦跳過 |
| 建立屬性 | `ScopingMethod = GeometryDefineByType.Component`，`Behavior = LoadBehavior.Rigid`，6 DOF（XComponent~RotationZ）全部設為 `ActiveOrInactive.Active` |

---

## 五、交叉引用但非本技能定義

以下命名/標籤規則屬於其他技能的產出範圍，本技能僅在總表中提及以避免消費端誤判，**不在此重複展開建立邏輯**：

| 命名 | 定義技能 |
| :--- | :--- |
| `[Mat] Unassigned_Bodies` | `ansys-material-assignment` |
| `Midsurface-` 前綴（實體命名清洗規則） | `ansys-material-assignment`（引用於 BOM 名稱清洗）、`ansys-spaceclaim-midsurface`（產出端） |
