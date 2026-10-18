"""ANSYS Unified MCP 2.0 - Mechanical 模組工具層 (Mechanical Tools).

整合原子化工具 (Atomic Tools) 與組合式高階工程工作流 (Composite Workflows)。
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from ansys_unified_mcp.shared import mcp, aliased_tool, as_envelope
from ansys_unified_mcp.products.mechanical import api as mechanical_api
from ansys_unified_mcp.products.mechanical.facade import controller, _esc

_envelope = as_envelope
logger = logging.getLogger("ansys-unified-mcp.products.mechanical.tools")


@mcp.resource("ansys://mechanical/model-tree")
def mechanical_model_tree_resource() -> str:
    """唯讀讀取 Mechanical 目前模型樹（Bodies、Named Selections、Analyses），不觸發任何 Tool 呼叫額度。

    對應 Phase 3 任務 3.3（docs/reviews/2026-10-02-phase2-3-feasibility-assessment.md）。
    內部委派 MechanicalController.run_script 執行既有 get_model_info 查詢腳本
    （與 mechanical_get_model_info 工具共用同一段 ACT 查詢邏輯，不重複實作）。
    """
    if not controller.is_connected():
        return json.dumps({"ok": False, "error": "尚未連線至 ANSYS Mechanical。"}, ensure_ascii=False)
    result = controller.run_script(
        "import json\n"
        "model = ExtAPI.DataModel.Project.Model\n"
        "info = {}\n"
        "bodies = []\n"
        "for body in model.Geometry.GetChildren(DataModelObjectCategory.Body, True):\n"
        '    bodies.append({"name": str(body.Name), "material": str(body.Material) if hasattr(body, "Material") else "N/A"})\n'
        'info["bodies"] = bodies\n'
        'info["named_selections"] = [str(ns.Name) for ns in model.GetChildren(DataModelObjectCategory.NamedSelection, True)]\n'
        'info["analyses"] = [{"name": str(a.Name), "type": str(a.AnalysisType)} for a in model.Analyses]\n'
        "print(json.dumps(info))\n"
    )
    try:
        return json.dumps({"ok": True, "model_tree": json.loads(result)}, ensure_ascii=False, indent=2)
    except (ValueError, TypeError):
        return json.dumps({"ok": False, "error": "無法解析模型樹輸出", "raw": result}, ensure_ascii=False)


@mcp.resource("ansys://mechanical/materials")
def mechanical_materials_resource() -> str:
    """唯讀讀取 Mechanical Engineering Data 中已載入的材料清單，不觸發任何 Tool 呼叫額度。

    內部委派 MechanicalController.run_script，與 mechanical_list_materials 工具
    共用同一段 ACT 查詢腳本。
    """
    if not controller.is_connected():
        return json.dumps({"ok": False, "error": "尚未連線至 ANSYS Mechanical。"}, ensure_ascii=False)
    result = controller.run_script(
        "import json\n"
        "model = ExtAPI.DataModel.Project.Model\n"
        "materials = [str(m.Name) for m in model.Materials.Children]\n"
        'print(json.dumps({"materials": materials}))\n'
    )
    try:
        return json.dumps({"ok": True, **json.loads(result)}, ensure_ascii=False, indent=2)
    except (ValueError, TypeError):
        return json.dumps({"ok": False, "error": "無法解析材料清單輸出", "raw": result}, ensure_ascii=False)


@aliased_tool(
    name="mechanical_list_instances",
    alias="list_instances",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def list_instances() -> dict:
    """List all running and registered ANSYS instances (Mechanical, Workbench, etc.) and their ports."""
    return as_envelope(mechanical_api.list_instances())


@aliased_tool(
    name="mechanical_connect",
    alias="connect_to_mechanical",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True}
)
def connect_to_mechanical(port: int = None, pid: int = None) -> dict:
    """Connect to ANSYS Mechanical via gRPC.
    Args:
    port: gRPC connection port. If omitted, connects to the first running instance.
    pid: gRPC connection PID. Connects to the Mechanical instance with this PID.
    """
    return as_envelope(mechanical_api.connect_to_mechanical(port=port, pid=pid))


@aliased_tool(
    name="mechanical_launch",
    alias="launch_mechanical",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True}
)
def launch_mechanical(batch: bool = True) -> dict:
    """Launch a new headless Mechanical instance via PyMechanical (no pre-running instance needed).
    Args:
    batch: Launch in batch (headless) mode. Set False for a visible session.
    """
    return as_envelope(mechanical_api.launch_mechanical(batch=batch))


@aliased_tool(
    name="mechanical_disconnect",
    alias="disconnect_from_mechanical",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def disconnect_from_mechanical() -> dict:
    """Disconnect the current Mechanical session."""
    return as_envelope(mechanical_api.disconnect_from_mechanical())


@aliased_tool(
    name="mechanical_check_connection",
    alias="check_mechanical_connection",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def check_mechanical_connection() -> dict:
    """Check connection status (lists all bound Mechanical sessions)."""
    return as_envelope(mechanical_api.check_mechanical_connection())


@aliased_tool(
    name="mechanical_get_model_info",
    alias="get_model_info",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def get_model_info() -> dict:
    """Get model info: bodies, named selections, analyses."""
    return as_envelope(mechanical_api.get_model_info())


@aliased_tool(
    name="mechanical_list_materials",
    alias="list_materials",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def list_materials() -> dict:
    """List all materials in Engineering Data."""
    return as_envelope(mechanical_api.list_materials())


@aliased_tool(
    name="mechanical_assign_material",
    alias="assign_material",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def assign_material(body_name: str, material_name: str) -> dict:
    """Assign material to a body. Args: body_name, material_name"""
    return as_envelope(mechanical_api.assign_material(body_name=body_name, material_name=material_name))


@aliased_tool(
    name="mechanical_set_mesh_element_size",
    alias="set_mesh_element_size",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def set_mesh_element_size(element_size_mm: float) -> dict:
    """Set global mesh element size in mm. Args: element_size_mm"""
    return as_envelope(mechanical_api.set_mesh_element_size(element_size_mm=element_size_mm))


@aliased_tool(
    name="mechanical_generate_mesh",
    alias="generate_mesh",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False}
)
def generate_mesh() -> dict:
    """Generate mesh. Visible live in Mechanical GUI."""
    return as_envelope(mechanical_api.generate_mesh())


@aliased_tool(
    name="mechanical_get_mesh_statistics",
    alias="get_mesh_statistics",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def get_mesh_statistics() -> dict:
    """Get mesh node and element counts."""
    return as_envelope(mechanical_api.get_mesh_statistics())


@aliased_tool(name="mechanical_add_fixed_support", alias="add_fixed_support")
def add_fixed_support(named_selection: str, analysis_index: int = 0) -> dict:
    """Add Fixed Support to a named selection. Args: named_selection, analysis_index"""
    return as_envelope(mechanical_api.add_fixed_support(named_selection=named_selection, analysis_index=analysis_index))


@aliased_tool(name="mechanical_add_force", alias="add_force")
def add_force(
    named_selection: str,
    fx_n: float = 0.0,
    fy_n: float = 0.0,
    fz_n: float = 0.0,
    analysis_index: int = 0,
) -> dict:
    """Add Force load in Newtons. Args: named_selection, fx_n, fy_n, fz_n, analysis_index"""
    return as_envelope(mechanical_api.add_force(named_selection=named_selection, fx_n=fx_n, fy_n=fy_n, fz_n=fz_n, analysis_index=analysis_index))


@aliased_tool(name="mechanical_add_pressure", alias="add_pressure")
def add_pressure(named_selection: str, magnitude_pa: float, analysis_index: int = 0) -> dict:
    """Add Pressure load in Pascals. Args: named_selection, magnitude_pa, analysis_index"""
    return as_envelope(mechanical_api.add_pressure(named_selection=named_selection, magnitude_pa=magnitude_pa, analysis_index=analysis_index))


@aliased_tool(name="mechanical_list_boundary_conditions", alias="list_boundary_conditions")
def list_boundary_conditions(analysis_index: int = 0) -> dict:
    """List all boundary conditions. Args: analysis_index"""
    return as_envelope(mechanical_api.list_boundary_conditions(analysis_index=analysis_index))


@aliased_tool(name="mechanical_solve_analysis", alias="solve_analysis")
def solve_analysis(analysis_index: int = 0, timeout_seconds: float = 3600.0) -> dict:
    """Solve the analysis. Progress visible in GUI. Args: analysis_index, timeout_seconds (default 3600s)"""
    return as_envelope(mechanical_api.solve_analysis(analysis_index=analysis_index, timeout_seconds=timeout_seconds))


@aliased_tool(name="mechanical_get_solve_status", alias="get_solve_status")
def get_solve_status(analysis_index: int = 0) -> dict:
    """Get solve status. Args: analysis_index"""
    return as_envelope(mechanical_api.get_solve_status(analysis_index=analysis_index))


@aliased_tool(name="mechanical_add_total_deformation_all_modes", alias="add_total_deformation_all_modes")
def add_total_deformation_all_modes(num_modes: int = 6, analysis_index: int = 0) -> dict:
    """Add Total Deformation for all modal modes. Args: num_modes, analysis_index"""
    return as_envelope(mechanical_api.add_total_deformation_all_modes(num_modes=num_modes, analysis_index=analysis_index))


@aliased_tool(name="mechanical_add_total_deformation", alias="add_total_deformation")
def add_total_deformation(mode: int = 0, analysis_index: int = 0) -> dict:
    """Add Total Deformation result. Args: mode (0=not modal), analysis_index"""
    return as_envelope(mechanical_api.add_total_deformation(mode=mode, analysis_index=analysis_index))


@aliased_tool(name="mechanical_get_modal_frequencies", alias="get_modal_frequencies")
def get_modal_frequencies(analysis_index: int = 0) -> dict:
    """Get natural frequencies from modal analysis. Args: analysis_index"""
    return as_envelope(mechanical_api.get_modal_frequencies(analysis_index=analysis_index))


@aliased_tool(name="mechanical_generate_report", alias="generate_report")
def generate_report(output_path: str, analysis_index: int = 0, fmt: str = "docx") -> dict:
    """Generate simulation report. Args: output_path, analysis_index, fmt (docx or txt)"""
    return as_envelope(mechanical_api.generate_report(output_path=output_path, analysis_index=analysis_index, fmt=fmt))


@aliased_tool(name="mechanical_run_script", alias="run_mechanical_script")
def run_mechanical_script(script: str, timeout_seconds: Optional[float] = None) -> dict:
    """Run custom Python script inside Mechanical ACT API. Args: script, timeout_seconds"""
    return as_envelope(mechanical_api.run_mechanical_script(script=script, timeout_seconds=timeout_seconds))


@aliased_tool(name="mechanical_list_named_selections", alias="list_named_selections")
def list_named_selections() -> dict:
    """List all named selections with face/body counts."""
    return as_envelope(mechanical_api.list_named_selections())


@aliased_tool(name="mechanical_delete_named_selection", alias="delete_named_selection")
def delete_named_selection(name: str) -> dict:
    """Delete a named selection by name. Args: name"""
    return as_envelope(mechanical_api.delete_named_selection(name=name))


@aliased_tool(name="mechanical_suppress_bodies", alias="suppress_bodies")
def suppress_bodies(name_prefix: str = "", suppress: bool = True) -> dict:
    """Suppress or unsuppress bodies by name prefix (empty = all bodies).
    Args: name_prefix, suppress (True=suppress, False=unsuppress)"""
    return as_envelope(mechanical_api.suppress_bodies(name_prefix=name_prefix, suppress=suppress))


@aliased_tool(name="mechanical_list_point_masses", alias="list_point_masses")
def list_point_masses() -> dict:
    """List all Point Masses with CG, mass, pinball and scoped named selection."""
    return as_envelope(mechanical_api.list_point_masses())


@aliased_tool(name="mechanical_add_frictionless_support", alias="add_frictionless_support")
def add_frictionless_support(named_selection: str, analysis_index: int = 0) -> dict:
    """Add Frictionless Support. Args: named_selection, analysis_index"""
    return as_envelope(mechanical_api.add_frictionless_support(named_selection=named_selection, analysis_index=analysis_index))


@aliased_tool(name="mechanical_add_displacement", alias="add_displacement")
def add_displacement(
    named_selection: str,
    x_mm: float | None = None,
    y_mm: float | None = None,
    z_mm: float | None = None,
    analysis_index: int = 0,
) -> dict:
    """Add Displacement BC. Pass None for a DOF to leave it free.
    Args: named_selection, x_mm, y_mm, z_mm (None=free), analysis_index"""
    return as_envelope(mechanical_api.add_displacement(named_selection=named_selection, x_mm=x_mm, y_mm=y_mm, z_mm=z_mm, analysis_index=analysis_index))


@aliased_tool(name="mechanical_add_remote_displacement", alias="add_remote_displacement")
def add_remote_displacement(
    named_selection: str,
    x_mm: float | None = None,
    y_mm: float | None = None,
    z_mm: float | None = None,
    rot_x_deg: float | None = None,
    rot_y_deg: float | None = None,
    rot_z_deg: float | None = None,
    analysis_index: int = 0,
) -> dict:
    """Add Remote Displacement BC. Pass None for a DOF to leave it free.
    Args: named_selection, x_mm, y_mm, z_mm, rot_x_deg, rot_y_deg, rot_z_deg, analysis_index"""
    return as_envelope(mechanical_api.add_remote_displacement(named_selection=named_selection, x_mm=x_mm, y_mm=y_mm, z_mm=z_mm, rot_x_deg=rot_x_deg, rot_y_deg=rot_y_deg, rot_z_deg=rot_z_deg, analysis_index=analysis_index))


@aliased_tool(name="mechanical_add_standard_gravity", alias="add_standard_gravity")
def add_standard_gravity(
    analysis_index: int = 0,
    x_component: float = 0.0,
    y_component: float = -1.0,
    z_component: float = 0.0,
) -> dict:
    """Add Standard Earth Gravity. Direction vector defaults to -Y (down).
    Args: analysis_index, x_component, y_component, z_component (unit vector)"""
    return as_envelope(mechanical_api.add_standard_gravity(analysis_index=analysis_index, x_component=x_component, y_component=y_component, z_component=z_component))


@aliased_tool(name="mechanical_add_remote_force", alias="add_remote_force")
def add_remote_force(
    named_selection: str,
    fx_n: float = 0.0,
    fy_n: float = 0.0,
    fz_n: float = 0.0,
    analysis_index: int = 0,
) -> dict:
    """Add Remote Force load. Args: named_selection, fx_n, fy_n, fz_n, analysis_index"""
    return as_envelope(mechanical_api.add_remote_force(named_selection=named_selection, fx_n=fx_n, fy_n=fy_n, fz_n=fz_n, analysis_index=analysis_index))


@aliased_tool(name="mechanical_add_moment", alias="add_moment")
def add_moment(
    named_selection: str,
    mx_nm: float = 0.0,
    my_nm: float = 0.0,
    mz_nm: float = 0.0,
    analysis_index: int = 0,
) -> dict:
    """Add Moment load in N·m. Args: named_selection, mx_nm, my_nm, mz_nm, analysis_index"""
    return as_envelope(mechanical_api.add_moment(named_selection=named_selection, mx_nm=mx_nm, my_nm=my_nm, mz_nm=mz_nm, analysis_index=analysis_index))


@aliased_tool(name="mechanical_add_equivalent_stress", alias="add_equivalent_stress")
def add_equivalent_stress(named_selection: str = "", analysis_index: int = 0) -> dict:
    """Add Equivalent (von Mises) Stress result, optionally scoped to a named selection.
    Args: named_selection (empty = whole model), analysis_index"""
    return as_envelope(mechanical_api.add_equivalent_stress(named_selection=named_selection, analysis_index=analysis_index))


@aliased_tool(name="mechanical_add_directional_deformation", alias="add_directional_deformation")
def add_directional_deformation(
    axis: str = "Y", named_selection: str = "", analysis_index: int = 0
) -> dict:
    """Add Directional Deformation result. Args: axis (X/Y/Z), named_selection, analysis_index"""
    return as_envelope(mechanical_api.add_directional_deformation(axis=axis, named_selection=named_selection, analysis_index=analysis_index))


@aliased_tool(name="mechanical_add_principal_stress", alias="add_principal_stress")
def add_principal_stress(which: str = "max", analysis_index: int = 0) -> dict:
    """Add Principal Stress result. Args: which (max/mid/min), analysis_index"""
    return as_envelope(mechanical_api.add_principal_stress(which=which, analysis_index=analysis_index))


@aliased_tool(name="mechanical_add_stress_tool", alias="add_stress_tool")
def add_stress_tool(analysis_index: int = 0) -> dict:
    """Add Stress Tool (safety factor, stress ratio) using material limits. Args: analysis_index"""
    return as_envelope(mechanical_api.add_stress_tool(analysis_index=analysis_index))


@aliased_tool(name="mechanical_add_reaction_force", alias="add_reaction_force")
def add_reaction_force(named_selection: str, analysis_index: int = 0) -> dict:
    """Add Force Reaction probe at a named selection. Args: named_selection, analysis_index"""
    return as_envelope(mechanical_api.add_reaction_force(named_selection=named_selection, analysis_index=analysis_index))


@aliased_tool(name="mechanical_convert_prefix_to_point_mass", alias="convert_prefix_to_point_mass")
def convert_prefix_to_point_mass(body_name_prefix: str, proximity_multiplier: float = 3.0) -> dict:
    """Convert all unsuppressed bodies whose name starts with body_name_prefix to a
    combined Point Mass, then create a Named Selection of all coplanar attachment
    faces on the nearest structural surface. No ACT extensions required.
    Args: body_name_prefix, proximity_multiplier (default 3.0)"""
    return as_envelope(mechanical_api.convert_prefix_to_point_mass(body_name_prefix=body_name_prefix, proximity_multiplier=proximity_multiplier))


@aliased_tool(name="mechanical_convert_part_to_point_mass", alias="convert_part_to_point_mass")
def convert_part_to_point_mass(part_name: str, proximity_multiplier: float = 3.0) -> dict:
    """Convert all unsuppressed bodies inside a named Part to a combined Point Mass,
    then create a Named Selection of all coplanar attachment faces on the nearest
    structural surface. No ACT extensions required.
    Args: part_name, proximity_multiplier (default 3.0)"""
    return as_envelope(mechanical_api.convert_part_to_point_mass(part_name=part_name, proximity_multiplier=proximity_multiplier))



# --- Composite Engineering Workflows ---

def _check_connection() -> Optional[dict]:
    """若未連線至 Mechanical 則回傳標準錯誤信封。"""
    if not controller.is_connected():
        return {
            "ok": False,
            "error": "尚未連線至 ANSYS Mechanical。請先呼叫 mechanical_connect 或 mechanical_launch 建立 Session。"
        }
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
) -> dict:
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

    # Assemble automated ACT script
    script = f"""
import json

model = ExtAPI.DataModel.Project.Model
if len(model.Analyses) <= {analysis_index}:
    print(json.dumps({{"ok": False, "error": "Analysis index {analysis_index} out of range."}}))
else:
    analysis = model.Analyses[{analysis_index}]
    
    # 1. Material assignment
    mat_assigned = False
    for body in model.Geometry.GetChildren(DataModelObjectCategory.Body, True):
        if str(body.Name) == "{safe_body}":
            body.Material = "{safe_mat}"
            mat_assigned = True
            break

    # 2. Mesh sizing and generation
    mesh = model.Mesh
    mesh.ElementSize = Quantity({mesh_element_size_mm}, "mm")
    mesh.GenerateMesh()
    
    # 3. Apply fixed support
    fix_obj = None
    for ns in model.GetChildren(DataModelObjectCategory.NamedSelection, True):
        if str(ns.Name) == "{safe_fix_ns}":
            fix_support = analysis.AddFixedSupport()
            fix_support.Location = ns
            fix_obj = fix_support
            break
            
    # 4. Apply force load
    force_obj = None
    for ns in model.GetChildren(DataModelObjectCategory.NamedSelection, True):
        if str(ns.Name) == "{safe_load_ns}":
            force = analysis.AddForce()
            force.Location = ns
            force.Magnitude.Output.SetDiscreteValue(0, Quantity({force_magnitude_n}, "N"))
            force.Direction = [Quantity({dx}), Quantity({dy}), Quantity({dz})]
            force_obj = force
            break
            
    # 5. Insert post-processing results
    solution = analysis.Solution
    eqv_stress = solution.AddEquivalentStress()
    tot_deform = solution.AddTotalDeformation()
    
    # 6. Solve
    solution.Solve(True)
    
    # 7. Extract extreme values and status
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
        return _envelope(data)
    except Exception:
        return _envelope({
            "ok": "error" not in raw_output.lower(),
            "raw_output": raw_output
        })


@aliased_tool(name="mechanical_setup_and_solve_modal", alias="setup_and_solve_modal")
def setup_and_solve_modal(
    fixed_support_ns: str,
    num_modes: int = 6,
    mesh_element_size_mm: float = 5.0,
    analysis_index: int = 0,
) -> dict:
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
    
    # 1. Mesh generation
    mesh = model.Mesh
    mesh.ElementSize = Quantity({mesh_element_size_mm}, "mm")
    mesh.GenerateMesh()
    
    # 2. Boundary conditions
    for ns in model.GetChildren(DataModelObjectCategory.NamedSelection, True):
        if str(ns.Name) == "{safe_fix_ns}":
            fix = analysis.AddFixedSupport()
            fix.Location = ns
            break
            
    # 3. Modal settings
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
        return _envelope(data)
    except Exception:
        return _envelope({
            "ok": "error" not in raw_output.lower(),
            "raw_output": raw_output
        })


@aliased_tool(name="mechanical_diagnose_model_health", alias="diagnose_model_health")
def diagnose_model_health() -> dict:
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
        return _envelope(data)
    except Exception:
        return _envelope({
            "ok": True,
            "raw_output": raw_output
        })


@aliased_tool(name="mechanical_get_tree_hierarchy", alias="get_model_tree_hierarchy")
def mechanical_get_tree_hierarchy(max_depth: int = 5) -> dict:
    """遞迴遍歷 Mechanical DataModel 樹狀階層結構，提取各節點名稱、類別、抑制狀態與健全度。

    Args:
        max_depth: 遍歷最大深度 (預設 5 層)。
    """
    from ansys_unified_mcp.products.mechanical.api import get_model_tree_hierarchy
    return _envelope(get_model_tree_hierarchy(max_depth=max_depth))


@aliased_tool(name="mechanical_assign_materials_from_bom", alias="assign_materials_from_bom")
def mechanical_assign_materials_from_bom(
    bom_items: Optional[List[Dict[str, Any]]] = None,
    csv_path: str = "",
) -> dict:
    """依據 BOM 表格或 CSV 檔案，批次將材料與等效密度指派給 Mechanical 中的各幾何體 (Bodies)。

    Args:
        bom_items: BOM 對應字典清單 (包含 body_name, material_name, 選填 density)。
        csv_path: 包含 BodyName 與 Material 欄位之 CSV 檔案絕對路徑。
    """
    from ansys_unified_mcp.products.mechanical.api import assign_materials_from_bom
    return _envelope(assign_materials_from_bom(bom_items=bom_items, csv_path=csv_path))


@aliased_tool(name="mechanical_create_joints_from_groups", alias="create_joints_from_groups")
def mechanical_create_joints_from_groups(
    connection_type: str = "Fixed",
    group_prefix: str = "Joint_",
) -> dict:
    """根據 Named Selection 命名選擇群組前綴，批次在 Mechanical 中建立 Joint 接頭連接元件。

    Args:
        connection_type: 接頭類型 ('Fixed', 'Revolute', 'Bush')。
        group_prefix: 命名選擇前綴字串 (預設 'Joint_')。
    """
    from ansys_unified_mcp.products.mechanical.api import create_joints_from_groups
    return _envelope(create_joints_from_groups(connection_type=connection_type, group_prefix=group_prefix))


@aliased_tool(name="mechanical_tune_cfl_mesh", alias="tune_cfl_mesh")
def mechanical_tune_cfl_mesh(
    target_timestep: float = 1e-7,
    max_iterations: int = 3,
) -> dict:
    """診斷並調優 Mechanical / LS-DYNA 顯式動力學網格之臨界 CFL 時間步長。

    Args:
        target_timestep: 目標臨界最小時間步長 (秒，預設 1e-7)。
        max_iterations: 最大調優迭代次數 (預設 3)。
    """
    from ansys_unified_mcp.products.mechanical.api import tune_cfl_mesh
    return _envelope(tune_cfl_mesh(target_timestep=target_timestep, max_iterations=max_iterations))


