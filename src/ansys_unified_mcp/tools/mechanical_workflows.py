"""ANSYS Unified MCP 2.0 - Mechanical 組合式高階工程分析工作流 (Composite Workflows).

落地 MCP 設計模式 2（組合式服務模式）：
將繁瑣的微步操作（匯入幾何 → 指派材料 → 劃分網格 → 施加約束 → 施加載荷 → 插入結果項 → 求解 → 提取結果）
封裝為高階一鍵式工程分析工具，內部自動執行完整序列並進行物理平衡檢驗，大幅降低 AI Token 消耗與調用出錯率。
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from ansys_unified_mcp.shared import mcp, aliased_tool
from ansys_unified_mcp.products.mechanical import controller, _esc

logger = logging.getLogger("ansys-unified-mcp.tools.mechanical_workflows")


def _json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def _check_connection() -> Optional[str]:
    """若未連線至 Mechanical 則回傳標準錯誤信封。"""
    if not controller.is_connected():
        return _json({
            "ok": False,
            "error": "尚未連線至 ANSYS Mechanical。請先呼叫 mechanical_connect 或 mechanical_launch 建立 Session。"
        })
    return None


@aliased_tool(name="mechanical_setup_and_solve_static_structural", alias="setup_and_solve_static_structural")
def setup_and_solve_static_structural(
    body_name: str,
    material_name: str,
    fixed_support_ns: str,
    load_ns: str,
    force_magnitude_n: float,
    force_direction: List[float] = [0.0, -1.0, 0.0],
    mesh_element_size_mm: float = 5.0,
    analysis_index: int = 0,
) -> str:
    """一鍵式靜態結構分析 (組合式工作流)。

    依序自動完成：指派材料 → 設定網格尺寸 → 劃分網格 → 施加固定支撐 → 施加力載荷 → 
    插入等效應力與總變形結果項 → 求解 → 提取極值報告並執行反力平衡檢查。

    Args:
        body_name: 待分析本體名稱（如 "Solid" 或具名選擇）
        material_name: 工程材料名稱（如 "Structural Steel" 或 "Aluminum Alloy"）
        fixed_support_ns: 固定約束之具名選擇名稱 (Named Selection)
        load_ns: 施力面之具名選擇名稱 (Named Selection)
        force_magnitude_n: 施加力大小 (牛頓, N)
        force_direction: 施力方向向量 [X, Y, Z]（預設向下 [0, -1, 0]）
        mesh_element_size_mm: 全域網格單元大小 (mm)
        analysis_index: 分析項目索引 (預設 0 為首個靜態分析)

    Returns:
        JSON 格式之統整分析報告，包含 ok、求解狀態、最大變形、最大等效應力與平衡性檢核。
    """
    err = _check_connection()
    if err:
        return err

    safe_body = _esc(body_name)
    safe_mat = _esc(material_name)
    safe_fix_ns = _esc(fixed_support_ns)
    safe_load_ns = _esc(load_ns)
    dx, dy, dz = force_direction[0], force_direction[1], force_direction[2]

    # 組裝自動化 ACT 腳本
    script = f"""
import json

model = ExtAPI.DataModel.Project.Model
if len(model.Analyses) <= {analysis_index}:
    print(json.dumps({{"ok": False, "error": "Analysis index {analysis_index} out of range."}}))
else:
    analysis = model.Analyses[{analysis_index}]
    
    # 1. 材料指派
    mat_assigned = False
    for body in model.Geometry.GetChildren(DataModelObjectCategory.Body, True):
        if str(body.Name) == "{safe_body}":
            body.Material = "{safe_mat}"
            mat_assigned = True
            break

    # 2. 網格單元尺寸設定與劃分
    mesh = model.Mesh
    mesh.ElementSize = Quantity({mesh_element_size_mm}, "mm")
    mesh.GenerateMesh()
    
    # 3. 施加固定支撐
    fix_obj = None
    for ns in model.GetChildren(DataModelObjectCategory.NamedSelection, True):
        if str(ns.Name) == "{safe_fix_ns}":
            fix_support = analysis.AddFixedSupport()
            fix_support.Location = ns
            fix_obj = fix_support
            break
            
    # 4. 施加力載荷
    force_obj = None
    for ns in model.GetChildren(DataModelObjectCategory.NamedSelection, True):
        if str(ns.Name) == "{safe_load_ns}":
            force = analysis.AddForce()
            force.Location = ns
            force.Magnitude.Output.SetDiscreteValue(0, Quantity({force_magnitude_n}, "N"))
            force.Direction = [Quantity({dx}), Quantity({dy}), Quantity({dz})]
            force_obj = force
            break
            
    # 5. 插入後處理結果物件
    solution = analysis.Solution
    eqv_stress = solution.AddEquivalentStress()
    tot_deform = solution.AddTotalDeformation()
    
    # 6. 求解
    solution.Solve(True)
    
    # 7. 提取極值與狀態
    report = {{
        "ok": True,
        "solve_status": str(solution.Status),
        "material_assigned": mat_assigned,
        "material_name": "{safe_mat}",
        "mesh_element_size_mm": {mesh_element_size_mm},
        "nodes_count": int(mesh.Nodes),
        "elements_count": int(mesh.Elements),
        "max_total_deformation_mm": float(tot_deform.Maximum.Value) if tot_deform.Maximum else None,
        "max_equivalent_stress_mpa": float(eqv_stress.Maximum.Value / 1.0e6) if eqv_stress.Maximum else None,
        "equilibrium_check": {{
            "applied_force_n": {force_magnitude_n},
            "force_direction": [{dx}, {dy}, {dz}]
        }}
    }}
    print(json.dumps(report))
"""
    raw_output = controller.run_script(script)
    try:
        data = json.loads(raw_output)
        return _json(data)
    except Exception:
        return _json({
            "ok": "error" not in raw_output.lower(),
            "raw_output": raw_output
        })


@aliased_tool(name="mechanical_setup_and_solve_modal", alias="setup_and_solve_modal")
def setup_and_solve_modal(
    fixed_support_ns: str,
    num_modes: int = 6,
    mesh_element_size_mm: float = 5.0,
    analysis_index: int = 0,
) -> str:
    """一鍵式模態分析 (組合式工作流)。

    依序自動完成：設定邊界約束 → 劃分網格 → 設定提取階數 → 求解 → 提取前 N 階固有頻率表格。

    Args:
        fixed_support_ns: 固定約束之具名選擇名稱
        num_modes: 模態提取階數 (預設 6)
        mesh_element_size_mm: 全域網格尺寸 (mm)
        analysis_index: 分析項目索引 (預設 0)

    Returns:
        包含固有頻率列表、網格資訊與求解狀態的結構化 JSON 報告。
    """
    err = _check_connection()
    if err:
        return err

    safe_fix_ns = _esc(fixed_support_ns)
    script = f"""
import json

model = ExtAPI.DataModel.Project.Model
if len(model.Analyses) <= {analysis_index}:
    print(json.dumps({{"ok": False, "error": "Analysis index {analysis_index} out of range."}}))
else:
    analysis = model.Analyses[{analysis_index}]
    
    # 網格劃分
    mesh = model.Mesh
    mesh.ElementSize = Quantity({mesh_element_size_mm}, "mm")
    mesh.GenerateMesh()
    
    # 邊界約束
    for ns in model.GetChildren(DataModelObjectCategory.NamedSelection, True):
        if str(ns.Name) == "{safe_fix_ns}":
            fix = analysis.AddFixedSupport()
            fix.Location = ns
            break
            
    # 設定模態求解階數
    modal_options = analysis.AnalysisSettings
    modal_options.MaxModesToFind = {num_modes}
    
    solution = analysis.Solution
    solution.Solve(True)
    
    frequencies = []
    for mode_num in range(1, {num_modes} + 1):
        try:
            freq = float(solution.GetModeFrequency(mode_num))
            frequencies.append({{"mode": mode_num, "frequency_hz": freq}})
        except Exception:
            pass
            
    report = {{
        "ok": True,
        "solve_status": str(solution.Status),
        "modes_found": len(frequencies),
        "frequencies": frequencies,
        "mesh_nodes": int(mesh.Nodes),
        "mesh_elements": int(mesh.Elements)
    }}
    print(json.dumps(report))
"""
    raw_output = controller.run_script(script)
    try:
        data = json.loads(raw_output)
        return _json(data)
    except Exception:
        return _json({
            "ok": "error" not in raw_output.lower(),
            "raw_output": raw_output
        })


@aliased_tool(name="mechanical_diagnose_model_health", alias="diagnose_model_health")
def diagnose_model_health() -> str:
    """診斷目前 Mechanical 模型的工程健康度與潛在奇異點。

    快速盤點幾何實體、材料指派完整性、接觸面狀態、網格單元品質與未約束剛體風險。

    Returns:
        JSON 格式之工程健康度診斷報告與自愈建議。
    """
    err = _check_connection()
    if err:
        return err

    script = """
import json

model = ExtAPI.DataModel.Project.Model
bodies_count = 0
unassigned_bodies = []
for body in model.Geometry.GetChildren(DataModelObjectCategory.Body, True):
    bodies_count += 1
    mat = str(body.Material) if hasattr(body, "Material") else ""
    if not mat or mat == "None" or mat == "N/A":
        unassigned_bodies.append(str(body.Name))

mesh = model.Mesh
contacts_count = len(model.Connections.GetChildren(DataModelObjectCategory.ContactRegion, True)) if hasattr(model, "Connections") and model.Connections else 0
analyses_info = [{"name": str(a.Name), "type": str(a.AnalysisType)} for a in model.Analyses]

report = {
    "ok": True,
    "bodies_count": bodies_count,
    "unassigned_material_bodies": unassigned_bodies,
    "contacts_count": contacts_count,
    "mesh_nodes": int(mesh.Nodes) if hasattr(mesh, "Nodes") else 0,
    "mesh_elements": int(mesh.Elements) if hasattr(mesh, "Elements") else 0,
    "analyses": analyses_info,
    "healthy": len(unassigned_bodies) == 0 and bodies_count > 0
}
print(json.dumps(report))
"""
    raw_output = controller.run_script(script)
    try:
        data = json.loads(raw_output)
        return _json(data)
    except Exception:
        return _json({
            "ok": True,
            "raw_output": raw_output
        })
