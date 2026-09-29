from __future__ import annotations
from ansys_unified_mcp.shared import mcp, aliased_tool, as_envelope
from ansys_unified_mcp.products import mechanical_api


@aliased_tool(name="mechanical_list_instances", alias="list_instances")
def list_instances() -> dict:
    """List all running and registered ANSYS instances (Mechanical, Workbench, etc.) and their ports."""
    return as_envelope(mechanical_api.list_instances())


@aliased_tool(name="mechanical_connect", alias="connect_to_mechanical")
def connect_to_mechanical(port: int = None, pid: int = None) -> dict:
    """Connect to ANSYS Mechanical via gRPC.
    Args:
    port: gRPC connection port. If omitted, connects to the first running instance.
    pid: gRPC connection PID. Connects to the Mechanical instance with this PID.
    """
    return as_envelope(mechanical_api.connect_to_mechanical(port=port, pid=pid))


@aliased_tool(name="mechanical_launch", alias="launch_mechanical")
def launch_mechanical(batch: bool = True) -> dict:
    """Launch a new headless Mechanical instance via PyMechanical (no pre-running instance needed).
    Args:
    batch: Launch in batch (headless) mode. Set False for a visible session.
    """
    return as_envelope(mechanical_api.launch_mechanical(batch=batch))


@aliased_tool(name="mechanical_disconnect", alias="disconnect_from_mechanical")
def disconnect_from_mechanical() -> dict:
    """Disconnect the current Mechanical session."""
    return as_envelope(mechanical_api.disconnect_from_mechanical())


@aliased_tool(name="mechanical_check_connection", alias="check_mechanical_connection")
def check_mechanical_connection() -> dict:
    """Check connection status (lists all bound Mechanical sessions)."""
    return as_envelope(mechanical_api.check_mechanical_connection())


@aliased_tool(name="mechanical_get_model_info", alias="get_model_info")
def get_model_info() -> dict:
    """Get model info: bodies, named selections, analyses."""
    return as_envelope(mechanical_api.get_model_info())


@aliased_tool(name="mechanical_list_materials", alias="list_materials")
def list_materials() -> dict:
    """List all materials in Engineering Data."""
    return as_envelope(mechanical_api.list_materials())


@aliased_tool(name="mechanical_assign_material", alias="assign_material")
def assign_material(body_name: str, material_name: str) -> dict:
    """Assign material to a body. Args: body_name, material_name"""
    return as_envelope(mechanical_api.assign_material(body_name=body_name, material_name=material_name))


@aliased_tool(name="mechanical_set_mesh_element_size", alias="set_mesh_element_size")
def set_mesh_element_size(element_size_mm: float) -> dict:
    """Set global mesh element size in mm. Args: element_size_mm"""
    return as_envelope(mechanical_api.set_mesh_element_size(element_size_mm=element_size_mm))


@aliased_tool(name="mechanical_generate_mesh", alias="generate_mesh")
def generate_mesh() -> dict:
    """Generate mesh. Visible live in Mechanical GUI."""
    return as_envelope(mechanical_api.generate_mesh())


@aliased_tool(name="mechanical_get_mesh_statistics", alias="get_mesh_statistics")
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
def solve_analysis(analysis_index: int = 0) -> dict:
    """Solve the analysis. Progress visible in GUI. Args: analysis_index"""
    return as_envelope(mechanical_api.solve_analysis(analysis_index=analysis_index))


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
def run_mechanical_script(script: str) -> dict:
    """Run custom Python script inside Mechanical ACT API. Args: script"""
    return as_envelope(mechanical_api.run_mechanical_script(script=script))


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



