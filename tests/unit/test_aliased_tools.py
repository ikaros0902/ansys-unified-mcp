"""Tests for aliased_tool registration and mechanical composite workflows."""

import asyncio
import json
import pytest
from ansys_unified_mcp.shared import mcp, aliased_tool
import ansys_unified_mcp.tools.mechanical
import ansys_unified_mcp.tools.mechanical_workflows
import ansys_unified_mcp.tools.workbench
import ansys_unified_mcp.tools.optislang
import ansys_unified_mcp.tools.intent_tools


@pytest.fixture(autouse=True)
def _expose_aliases_for_testing(monkeypatch):
    """Ensure aliases are exposed for legacy alias compatibility verification."""
    monkeypatch.setenv("ANSYS_MCP_EXPOSE_ALIASES", "1")


def test_aliased_tools_registered():
    """Verify that both canonical names and legacy aliases are registered in FastMCP."""
    async def _check():
        tools = await mcp.list_tools()
        tool_map = {t.name: t for t in tools}

        # Mechanical checks
        assert "mechanical_add_force" in tool_map
        assert "add_force" in tool_map
        assert "mechanical_connect" in tool_map
        assert "connect_to_mechanical" in tool_map
        assert "mechanical_solve_analysis" in tool_map
        assert "solve_analysis" in tool_map

        # Composite workflow checks
        assert "mechanical_setup_and_solve_static_structural" in tool_map
        assert "setup_and_solve_static_structural" in tool_map
        assert "mechanical_setup_and_solve_modal" in tool_map
        assert "setup_and_solve_modal" in tool_map
        assert "mechanical_diagnose_model_health" in tool_map
        assert "diagnose_model_health" in tool_map

        # Workbench checks
        assert "workbench_run_journal" in tool_map
        assert "workbench_run_journal_tool" in tool_map
        assert "mechanical_run_batch_script" in tool_map
        assert "mechanical_run_script_tool" in tool_map

        # OptiSLang checks
        assert "optislang_connect" in tool_map
        assert "connect_optislang" in tool_map

        # Intent workflow checks
        assert "workflow_run_drop_test" in tool_map
        assert "run_drop_test" in tool_map

    asyncio.run(_check())


def test_composite_workflow_graceful_failure_when_disconnected():
    """Verify composite workflows return graceful error envelope when not connected."""
    # Test setup and solve when disconnected
    result_str = ansys_unified_mcp.tools.mechanical_workflows.setup_and_solve_static_structural(
        body_name="Solid",
        material_name="Structural Steel",
        fixed_support_ns="Fixed",
        load_ns="Load",
        force_magnitude_n=100.0,
    )
    data = json.loads(result_str)
    assert data["ok"] is False
    assert "尚未連線" in data["error"] or "Not connected" in data["error"]

    # Test modal when disconnected
    result_modal = ansys_unified_mcp.tools.mechanical_workflows.setup_and_solve_modal(
        fixed_support_ns="Fixed",
        num_modes=6,
    )
    modal_data = json.loads(result_modal)
    assert modal_data["ok"] is False

    # Test diagnose when disconnected
    result_diag = ansys_unified_mcp.tools.mechanical_workflows.diagnose_model_health()
    diag_data = json.loads(result_diag)
    assert diag_data["ok"] is False


def test_mechanical_envelope_fixes():
    """Verify check_mechanical_connection has ok field and _wrap_raw_output detects errors."""
    from ansys_unified_mcp.tools.mechanical import (
        check_mechanical_connection,
        _wrap_raw_output,
        _is_error_output,
    )

    # 1. check_mechanical_connection must contain 'ok': False when disconnected
    res = json.loads(check_mechanical_connection())
    assert "ok" in res
    assert res["ok"] is False
    assert res["connected"] is False

    # 2. _is_error_output correctly flags exceptions
    assert _is_error_output("Traceback (most recent call last):\n  File 'x', line 1\nSyntaxError: invalid syntax") is True
    assert _is_error_output("System.Exception: Object reference not set to an instance of an object") is True
    assert _is_error_output("Normal output: Solved successfully in 12 iterations") is False

    # 3. _wrap_raw_output flips ok to False if error detected
    err_envelope = _wrap_raw_output("TypeError: unsupported operand type(s)")
    assert err_envelope["ok"] is False
    assert "error" in err_envelope

    ok_envelope = _wrap_raw_output("Normal status")
    assert ok_envelope["ok"] is True


def test_alias_pruning_via_env_var(monkeypatch):
    """Verify that setting ANSYS_MCP_PRUNE_ALIASES=1 skips registering deprecated aliases."""
    import os
    from fastmcp import FastMCP
    from ansys_unified_mcp.shared import aliased_tool

    test_mcp = FastMCP("test-prune")
    monkeypatch.setenv("ANSYS_MCP_PRUNE_ALIASES", "1")

    # Patch global mcp in shared temporarily
    monkeypatch.setattr("ansys_unified_mcp.shared.mcp", test_mcp)

    @aliased_tool(name="canonical_tool", alias="legacy_alias")
    def sample_func():
        return "ok"

    tools = asyncio.run(test_mcp.list_tools())
    tool_names = [t.name for t in tools]
    assert "canonical_tool" in tool_names
    assert "legacy_alias" not in tool_names


