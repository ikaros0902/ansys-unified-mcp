"""Milestone 1 Empirical Verification: FastMCP Mechanical Alias Symmetry & Call Equivalence Challenge.

This suite is written by the FastMCP Alias Challenger to verify:
1. 39 Mechanical canonical tools registered in FastMCP.
2. 39 Legacy aliases registered with "[DEPRECATED ALIAS for <canonical>]" in description.
3. 100% Parameter schema equivalence between each canonical tool and its alias.
4. 100% Offline execution output equivalence (character-level and JSON AST level).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

import asyncio
import json
import pytest
from unittest.mock import patch

from ansys_unified_mcp.shared import mcp
import ansys_unified_mcp.tools.mechanical as mechanical_mod


def run_async(coro):
    """Run an async coroutine synchronously using standard asyncio."""
    return asyncio.run(coro)


@pytest.fixture(autouse=True)
def _expose_aliases_for_symmetry_check(monkeypatch):
    """R4 工具面剪枝後 alias 預設不暴露；本套件專驗相容模式下的別名對稱性，故顯式開啟。"""
    monkeypatch.delenv("ANSYS_MCP_PRUNE_ALIASES", raising=False)
    monkeypatch.setenv("ANSYS_MCP_EXPOSE_ALIASES", "1")


# Complete list of 39 (canonical_name, legacy_alias, sample_kwargs)
MECHANICAL_39_TOOL_SPECS = [
    ("mechanical_list_instances", "list_instances", {}),
    ("mechanical_connect", "connect_to_mechanical", {"port": 59999}),
    ("mechanical_launch", "launch_mechanical", {"batch": True}),
    ("mechanical_disconnect", "disconnect_from_mechanical", {}),
    ("mechanical_check_connection", "check_mechanical_connection", {}),
    ("mechanical_get_model_info", "get_model_info", {}),
    ("mechanical_list_materials", "list_materials", {}),
    ("mechanical_assign_material", "assign_material", {"body_name": "Body1", "material_name": "Structural Steel"}),
    ("mechanical_set_mesh_element_size", "set_mesh_element_size", {"element_size_mm": 5.0}),
    ("mechanical_generate_mesh", "generate_mesh", {}),
    ("mechanical_get_mesh_statistics", "get_mesh_statistics", {}),
    ("mechanical_add_fixed_support", "add_fixed_support", {"named_selection": "FixedNS", "analysis_index": 0}),
    ("mechanical_add_force", "add_force", {"named_selection": "ForceNS", "fx_n": 0.0, "fy_n": -100.0, "fz_n": 0.0, "analysis_index": 0}),
    ("mechanical_add_pressure", "add_pressure", {"named_selection": "PressNS", "magnitude_pa": 1000.0, "analysis_index": 0}),
    ("mechanical_list_boundary_conditions", "list_boundary_conditions", {"analysis_index": 0}),
    ("mechanical_solve_analysis", "solve_analysis", {"analysis_index": 0}),
    ("mechanical_get_solve_status", "get_solve_status", {"analysis_index": 0}),
    ("mechanical_add_total_deformation_all_modes", "add_total_deformation_all_modes", {"num_modes": 6, "analysis_index": 0}),
    ("mechanical_add_total_deformation", "add_total_deformation", {"mode": 0, "analysis_index": 0}),
    ("mechanical_get_modal_frequencies", "get_modal_frequencies", {"analysis_index": 0}),
    ("mechanical_generate_report", "generate_report", {"output_path": "report.docx", "analysis_index": 0, "fmt": "docx"}),
    ("mechanical_run_script", "run_mechanical_script", {"script": "print('test')"}),
    ("mechanical_list_named_selections", "list_named_selections", {}),
    ("mechanical_delete_named_selection", "delete_named_selection", {"name": "NS1"}),
    ("mechanical_suppress_bodies", "suppress_bodies", {"name_prefix": "Part", "suppress": True}),
    ("mechanical_list_point_masses", "list_point_masses", {}),
    ("mechanical_add_frictionless_support", "add_frictionless_support", {"named_selection": "FricNS", "analysis_index": 0}),
    ("mechanical_add_displacement", "add_displacement", {"named_selection": "DispNS", "x_mm": 0.0, "y_mm": None, "z_mm": None, "analysis_index": 0}),
    ("mechanical_add_remote_displacement", "add_remote_displacement", {"named_selection": "RDispNS", "x_mm": 0.0, "rot_z_deg": 10.0, "analysis_index": 0}),
    ("mechanical_add_standard_gravity", "add_standard_gravity", {"analysis_index": 0, "x_component": 0.0, "y_component": -1.0, "z_component": 0.0}),
    ("mechanical_add_remote_force", "add_remote_force", {"named_selection": "RForceNS", "fx_n": 50.0, "analysis_index": 0}),
    ("mechanical_add_moment", "add_moment", {"named_selection": "MomNS", "mx_nm": 10.0, "analysis_index": 0}),
    ("mechanical_add_equivalent_stress", "add_equivalent_stress", {"named_selection": "", "analysis_index": 0}),
    ("mechanical_add_directional_deformation", "add_directional_deformation", {"axis": "Y", "named_selection": "", "analysis_index": 0}),
    ("mechanical_add_principal_stress", "add_principal_stress", {"which": "max", "analysis_index": 0}),
    ("mechanical_add_stress_tool", "add_stress_tool", {"analysis_index": 0}),
    ("mechanical_add_reaction_force", "add_reaction_force", {"named_selection": "ReactNS", "analysis_index": 0}),
    ("mechanical_convert_prefix_to_point_mass", "convert_prefix_to_point_mass", {"body_name_prefix": "Bolt", "proximity_multiplier": 3.0}),
    ("mechanical_convert_part_to_point_mass", "convert_part_to_point_mass", {"part_name": "PartA", "proximity_multiplier": 3.0}),
]


def test_exact_count_of_mechanical_specs():
    """Verify our specification list contains exactly 39 tools."""
    assert len(MECHANICAL_39_TOOL_SPECS) == 39
    canonicals = [c for c, _, _ in MECHANICAL_39_TOOL_SPECS]
    aliases = [a for _, a, _ in MECHANICAL_39_TOOL_SPECS]
    assert len(set(canonicals)) == 39, "Duplicate canonical name detected in spec!"
    assert len(set(aliases)) == 39, "Duplicate alias detected in spec!"


def test_all_39_canonical_and_aliases_registered():
    """Verify that FastMCP registers all 39 canonicals and all 39 aliases."""
    async def _test():
        tools = await mcp.list_tools()
        tool_map = {t.name: t for t in tools}

        missing_canonicals = []
        missing_aliases = []

        for canonical, alias, _ in MECHANICAL_39_TOOL_SPECS:
            if canonical not in tool_map:
                missing_canonicals.append(canonical)
            if alias not in tool_map:
                missing_aliases.append(alias)

        assert not missing_canonicals, f"Missing canonical tools in FastMCP: {missing_canonicals}"
        assert not missing_aliases, f"Missing alias tools in FastMCP: {missing_aliases}"

    run_async(_test())


def test_alias_deprecation_descriptions():
    """Verify that every alias description starts with [DEPRECATED ALIAS for <canonical>]."""
    async def _test():
        tools = await mcp.list_tools()
        tool_map = {t.name: t for t in tools}

        malformed_descriptions = []

        for canonical, alias, _ in MECHANICAL_39_TOOL_SPECS:
            canonical_tool = tool_map[canonical]
            alias_tool = tool_map[alias]

            expected_prefix = f"[DEPRECATED ALIAS for {canonical}]"
            alias_desc = alias_tool.description or ""
            canon_desc = canonical_tool.description or ""

            if not alias_desc.startswith(expected_prefix):
                malformed_descriptions.append((alias, alias_desc, f"Missing prefix: {expected_prefix}"))

            # Verify remainder of description matches canonical description
            expected_full = f"{expected_prefix} {canon_desc}".strip()
            if alias_desc.strip() != expected_full:
                malformed_descriptions.append((alias, alias_desc, f"Expected full: {expected_full}"))

        assert not malformed_descriptions, f"Aliases with malformed descriptions: {malformed_descriptions}"

    run_async(_test())


def test_parameter_schemas_identical():
    """Verify that parameter schemas (arguments, types, required) are 100% identical."""
    async def _test():
        tools = await mcp.list_tools()
        tool_map = {t.name: t for t in tools}

        schema_mismatches = []

        for canonical, alias, _ in MECHANICAL_39_TOOL_SPECS:
            canon_tool = tool_map[canonical]
            alias_tool = tool_map[alias]

            canon_schema = canon_tool.parameters if hasattr(canon_tool, "parameters") else getattr(canon_tool, "inputSchema", None)
            alias_schema = alias_tool.parameters if hasattr(alias_tool, "parameters") else getattr(alias_tool, "inputSchema", None)

            if canon_schema != alias_schema:
                schema_mismatches.append((canonical, alias, canon_schema, alias_schema))

        assert not schema_mismatches, f"Parameter schema mismatches found: {schema_mismatches}"

    run_async(_test())


def test_offline_call_equivalence_all_39_tools():
    """Empirically invoke both canonical and alias tools via FastMCP in offline mode.
    
    Verify:
    1. Both return successfully from mcp.call_tool without crashing.
    2. The text/result payload contains valid JSON.
    3. The JSON root object contains 'ok': bool.
    4. Canonical and alias outputs are 100% identical in JSON semantics and string content.
    """
    async def _test():
        # Ensure offline mode (controller disconnected)
        assert not mechanical_mod.controller.is_connected(), "Must be tested in offline mode!"

        # Mock controller.launch and controller.connect to avoid hanging network calls while testing call mechanics
        with patch.object(mechanical_mod.controller, "launch", return_value={"ok": False, "error": "Mocked offline launch error"}), \
             patch.object(mechanical_mod.controller, "connect", return_value={"ok": False, "error": "Mocked offline connect error"}):

            comparison_results = []
            inequivalent_tools = []

            for canonical, alias, kwargs in MECHANICAL_39_TOOL_SPECS:
                # 1. Call canonical
                res_canon = await mcp.call_tool(canonical, kwargs)
                # 2. Call alias
                res_alias = await mcp.call_tool(alias, kwargs)

                # Extract raw text from ToolResult
                text_canon = res_canon.content[0].text if res_canon.content else ""
                text_alias = res_alias.content[0].text if res_alias.content else ""

                # Check JSON parseability
                try:
                    data_canon = json.loads(text_canon)
                except Exception as e:
                    pytest.fail(f"Tool {canonical} returned invalid JSON: {text_canon!r}, err: {e}")

                try:
                    data_alias = json.loads(text_alias)
                except Exception as e:
                    pytest.fail(f"Tool {alias} returned invalid JSON: {text_alias!r}, err: {e}")

                # Check JSON envelope: must contain 'ok' key
                assert "ok" in data_canon, f"Tool {canonical} return payload lacks 'ok' field: {data_canon}"
                assert "ok" in data_alias, f"Tool {alias} return payload lacks 'ok' field: {data_alias}"

                # Check equality
                if data_canon != data_alias or text_canon != text_alias:
                    inequivalent_tools.append({
                        "canonical": canonical,
                        "alias": alias,
                        "canon_data": data_canon,
                        "alias_data": data_alias,
                        "text_diff": (text_canon, text_alias),
                    })
                else:
                    comparison_results.append({
                        "canonical": canonical,
                        "alias": alias,
                        "status": "EQUAL",
                        "ok_value": data_canon.get("ok"),
                    })

            assert not inequivalent_tools, f"Inequivalent tool outputs detected: {inequivalent_tools}"
            assert len(comparison_results) == 39, f"Expected 39 verified pairs, got {len(comparison_results)}"

    run_async(_test())
