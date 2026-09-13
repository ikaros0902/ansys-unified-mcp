"""Verification of Dynamic Tool Routing profiles for Mechanical tools."""
import sys
import os
import subprocess
import pytest
from pathlib import Path

python_exe = sys.executable
repo_root = Path(__file__).resolve().parent.parent.parent

check_script = """
import os
import asyncio
import json
from ansys_unified_mcp.shared import mcp

profile = os.environ.get("ANSYS_MCP_PROFILE", "all")

# Import entry point dynamically
import ansys_unified_mcp.__main__

async def verify():
    tools = await mcp.list_tools()
    tool_names = set(t.name for t in tools)
    
    # 39 Mechanical canonical names
    canonical_mech = [
        "mechanical_list_instances", "mechanical_connect", "mechanical_launch", "mechanical_disconnect",
        "mechanical_check_connection", "mechanical_get_model_info", "mechanical_list_materials",
        "mechanical_assign_material", "mechanical_set_mesh_element_size", "mechanical_generate_mesh",
        "mechanical_get_mesh_statistics", "mechanical_add_fixed_support", "mechanical_add_force",
        "mechanical_add_pressure", "mechanical_list_boundary_conditions", "mechanical_solve_analysis",
        "mechanical_get_solve_status", "mechanical_add_total_deformation_all_modes",
        "mechanical_add_total_deformation", "mechanical_get_modal_frequencies",
        "mechanical_generate_report", "mechanical_run_script", "mechanical_list_named_selections",
        "mechanical_delete_named_selection", "mechanical_suppress_bodies", "mechanical_list_point_masses",
        "mechanical_add_frictionless_support", "mechanical_add_displacement",
        "mechanical_add_remote_displacement", "mechanical_add_standard_gravity",
        "mechanical_add_remote_force", "mechanical_add_moment", "mechanical_add_equivalent_stress",
        "mechanical_add_directional_deformation", "mechanical_add_principal_stress",
        "mechanical_add_stress_tool", "mechanical_add_reaction_force",
        "mechanical_convert_prefix_to_point_mass", "mechanical_convert_part_to_point_mass"
    ]
    
    legacy_aliases = [
        "list_instances", "connect_to_mechanical", "launch_mechanical", "disconnect_from_mechanical",
        "check_mechanical_connection", "get_model_info", "list_materials",
        "assign_material", "set_mesh_element_size", "generate_mesh",
        "get_mesh_statistics", "add_fixed_support", "add_force",
        "add_pressure", "list_boundary_conditions", "solve_analysis",
        "get_solve_status", "add_total_deformation_all_modes",
        "add_total_deformation", "get_modal_frequencies",
        "generate_report", "run_mechanical_script", "list_named_selections",
        "delete_named_selection", "suppress_bodies", "list_point_masses",
        "add_frictionless_support", "add_displacement",
        "add_remote_displacement", "add_standard_gravity",
        "add_remote_force", "add_moment", "add_equivalent_stress",
        "add_directional_deformation", "add_principal_stress",
        "add_stress_tool", "add_reaction_force",
        "convert_prefix_to_point_mass", "convert_part_to_point_mass"
    ]
    
    missing_c = [c for c in canonical_mech if c not in tool_names]
    missing_a = [a for a in legacy_aliases if a not in tool_names]
    
    print(f"Profile: {profile}")
    print(f"Total registered tools: {len(tool_names)}")
    print(f"Missing canonical mechanical tools: {missing_c}")
    print(f"Missing legacy alias tools: {missing_a}")
    
    if not missing_c and not missing_a:
        print(f"STATUS: SUCCESS ({len(canonical_mech)} canonical + {len(legacy_aliases)} aliases present)")
    else:
        print("STATUS: FAILED")

asyncio.run(verify())
"""

@pytest.mark.parametrize("profile_val", ["mechanical", "all"])
def test_profile_routing(profile_val):
    env = os.environ.copy()
    env["ANSYS_MCP_PROFILE"] = profile_val
    env["PYTHONPATH"] = str(repo_root / "src")
    res = subprocess.run(
        [python_exe, "-c", check_script],
        cwd=str(repo_root),
        env=env,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert "STATUS: SUCCESS" in res.stdout
