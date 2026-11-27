---
name: pcb-warpage-analysis
description: "PCB多層疊構熱翹曲（Thermal Warpage）統一自動化技能，涵蓋無ODB++整層ROM（Track 1）與有ODB++逐元素Trace Mapping及BGA-shadow Leveling（Track 2）。支援純本機與ANSYS MCP雙環境，強制前置Intake Gate分流、Z軸位移（Uz）後處理、3-2-1靜定支撐與T_REF一致性檢核。觸發關鍵字：PCB熱翹曲, PCB疊構, ODB++, ROM材料計算, Trace Mapping, 3-2-1支承, Leveling。"
---

# PCB Multi-Layer Thermal Warpage Analysis Skill

本技能整合 **Track 1（無 ODB++ 整層均質化 ROM）** 與 **Track 2（有 ODB++ 逐元素 Trace Mapping 與 BGA-shadow Leveling）** 兩條 PCB 熱翹曲分析路線，支援純本機與 `ansys-unified-mcp` 雙環境。

---

## 1. Pre-Action Intake Gate（強制前置分流）

啟動任何腳本或 MCP 工具前，Agent 必須依序確認以下三問並寫入倉庫外 `PROJECT_DIR/project_log.md`：

1. **是否有 ODB++？**
   - **無** → 進入 `Track 1`（FEM 求解標註 `RESULT SOURCE: FEM-ROM`；僅做解析估算標註 `RESULT SOURCE: ESTIMATED`）。
   - **有** → 進入第 2 問。
2. **Track 2 五項輸入是否齊全？**（ODB++ `.tgz`、廠商疊構表、Design 材料表、2D `.stp`、外部材料庫 XML 路徑）
   - **齊全** → 進入 `Track 2`（標註 `RESULT SOURCE: FEM-TraceMapping`），建立專案 JSON 時設定 `output.root = "runs/track2_odb"`（不改上游範本）。
   - **缺任一項** → 立即停止並要求補齊；僅當工程師明確指示「改以高階估算進行」時，方可降級至 `Track 1` 並於 `project_log.md` 記錄原因。
3. **三段式 MCP 偵測與降級**：
   - (a) 會話工具清單含 `ans_session_status` 與 `mechanical_*`；(b) `ans_session_status(product="mechanical")` 可用；(c) `mechanical_list_instances` / `mechanical_connect` 附著並經工程師確認專案路徑或實例身分。
   - 三段皆成功 → **MCP 模式**；任一步失敗 → **純本機模式**（全流程於本機與 GUI 檢查點完成）。

---

## 2. 雙軌執行路由表 (Track Router)

| 軌道 | 適用情境 | 輸出目錄（於倉庫外 `PROJECT_DIR`） | 核心入口與必讀規範 |
| :--- | :--- | :--- | :--- |
| **Track 1** | 僅有疊構表與各層鋪銅率，無 ODB++ | `runs/track1_rom/` | `./scripts/run_full_warpage_workflow.py`（依序呼叫 `01_build_pcb_geometry.py`、`02_calculate_rom_materials.py`、`03_setup_mechanical_bc_and_solution.py`）；僅需解析估算可呼叫 `workflow_run_thermal_warpage`（`ESTIMATED`） |
| **Track 2** | 具備 ODB++ `.tgz` 與五項完整輸入 | `runs/track2_odb/` | [`./references/odb_workflow/TRACK2_SKILL.md`](./references/odb_workflow/TRACK2_SKILL.md)、[`./references/odb_workflow/README.md`](./references/odb_workflow/README.md)、[`./references/odb_workflow/mcp_hybrid_checkpoint.md`](./references/odb_workflow/mcp_hybrid_checkpoint.md) |
| **共用 Leveling** | Track 1 / Track 2 匯出 Z 位移與 `ds.dat` 後之最小平方平面擬合 | 依所屬軌道輸出 | `./scripts/level_wrapper.py` CLI（BGA 區域標註 `BGA-Shadow Leveled`；全板節點標註 `Full-Board Leveled`） |

---

## 3. 核心物理與後處理規範 (Mandatory Guardrails)

1. **嚴格聚焦 Z 軸位移 ($U_z$)**：熱翹曲分析禁用 `Total Deformation`（混入 $U_x, U_y$），必監視 `Z_Displacement_PCB_All_Layers`、`Z_Displacement_L01_Top_Face` 與 `Z_Displacement_L79_Bottom_Face`。
2. **3-2-1 靜定支撐**：於三個不共線頂點分別限制 3、2、1 個自由度（共 6 DOF），消除剛體運動且不產生人為熱拘束應力。
3. **相機構圖標準**：禁止未校正視角遮擋圖例。
   - **視角 A（2D 俯視）**：`cam.SetSpecificViewOrientation(ViewOrientationType.Front)` + `cam.SetFit()` + `cam.Zoom(0.85)`。
   - **視角 B（3D 等角）**：由 Front 旋轉 `cam.Rotate(-28, CameraAxisType.ScreenX)` 與 `cam.Rotate(-25, CameraAxisType.ScreenY)`，搭配 `cam.SetFit()` + `cam.Zoom(0.82)`。
4. **人類決策零猜測與 `T_REF` 核對**：不得自行猜測厚度欄位、N+M FR4、Resin Content、BGA footprint、支撐點、溫度與單位；Track 2 求解前必核對 `T_REF` 三處一致（詳見 [`mcp_hybrid_checkpoint.md`](./references/odb_workflow/mcp_hybrid_checkpoint.md)）。

---

## 4. 模板、材料與參考文件

- **ROM APDL 骨架**：[`assets/apdl_rom_materials_template.mac`](assets/apdl_rom_materials_template.mac)（對應 `02_calculate_rom_materials.py` 之 MP/MPTEMP/MPDATA 順序規則）。
- **膠材黏彈性選型**：若 underfill、mold compound 需考量應力鬆弛或時溫等效黏彈性，見 [`ansys-mechanical/references/hyperelastic_viscoelastic_materials.md`](../../structural-mechanics/ansys-mechanical/references/hyperelastic_viscoelastic_materials.md)。
- **可靠度標準**：IPC-9701A 熱循環條件、無鉛焊點 Weibull 判定與界面裂解判準見 [`references/ipc_jedec_reliability_standards.md`](references/ipc_jedec_reliability_standards.md)。
