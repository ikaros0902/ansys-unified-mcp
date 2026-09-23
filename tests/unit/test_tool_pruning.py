# -*- coding: utf-8 -*-
"""Unit tests for tool surface pruning (R4).

Verifies:
1. When EXPOSE_ALIASES is False (default), exactly 0 '[DEPRECATED ALIAS for ...]' tools
   are registered/exposed in FastMCP.
2. Canonical primitives (~18 core primitives) are present and callable.
3. General passthroughs (mechanical_run_script, workbench_run_script_live / execute_workbench_script)
   are preserved.
4. Pre-flight security/gatekeeper physical guards on workflows are preserved.
5. Internal alias lookup dictionary resolves aliases to canonical implementations.
"""

from __future__ import annotations

import asyncio
import json
import os
import pytest
from unittest.mock import patch, MagicMock

from ansys_unified_mcp.shared import (
    mcp,
    aliased_tool,
    EXPOSE_ALIASES,
    should_expose_aliases,
    ALIAS_REGISTRY,
    CANONICAL_TO_ALIASES,
    get_canonical_name,
    get_tool_function,
)

# Ensure relevant tool modules are imported
import ansys_unified_mcp.tools.sentinel_tools
import ansys_unified_mcp.tools.intent_tools
import ansys_unified_mcp.tools.mechanical
import ansys_unified_mcp.tools.optislang
import ansys_unified_mcp.tools.workbench_filebridge


def run_async(coro):
    return asyncio.run(coro)


class TestToolSurfacePruning:
    """Tests verifying MCP tool pruning behavior and canonical exposure."""

    def test_default_pruning_zero_deprecated_aliases(self, monkeypatch):
        """Verify that when EXPOSE_ALIASES is False (default), 0 deprecated alias tools are exposed."""
        monkeypatch.delenv("ANSYS_MCP_EXPOSE_ALIASES", raising=False)
        monkeypatch.delenv("ANSYS_MCP_PRUNE_ALIASES", raising=False)

        async def _verify():
            tools = await mcp.list_tools()
            tool_names = {t.name for t in tools}

            # 1. 斷言任何工具的說明中均不含 [DEPRECATED ALIAS for ...]
            deprecated_tools = [
                t.name for t in tools
                if t.description and "[DEPRECATED ALIAS for" in t.description
            ]
            assert len(deprecated_tools) == 0, f"Found deprecated alias tools exposed: {deprecated_tools}"

            # 2. 斷言已知的舊別名絕對不包含在 FastMCP 工具名稱清單中
            legacy_aliases_to_check = [
                "add_force",
                "connect_to_mechanical",
                "launch_mechanical",
                "disconnect_from_mechanical",
                "solve_analysis",
                "run_drop_test",
                "run_shock_analysis",
                "run_random_vibration",
                "run_thermal_warpage",
                "train_surrogate_model",
                "connect_optislang",
                "run_optislang_script",
                "setup_and_solve_static_structural",
                "setup_and_solve_modal",
                "diagnose_model_health",
            ]
            leaked_aliases = [alias for alias in legacy_aliases_to_check if alias in tool_names]
            assert len(leaked_aliases) == 0, f"Leaked legacy aliases in FastMCP tool list: {leaked_aliases}"

        run_async(_verify())

    def test_canonical_primitives_present(self):
        """Verify the ~18 canonical primitives are present in FastMCP list_tools."""
        async def _verify():
            tools = await mcp.list_tools()
            tool_names = {t.name for t in tools}

            # Sentinel (4)
            sentinel_primitives = [
                "submit_simulation_job",
                "get_simulation_status",
                "tail_simulation_log",
                "abort_simulation_job",
            ]
            for name in sentinel_primitives:
                assert name in tool_names, f"Sentinel primitive '{name}' missing from FastMCP tools"

            # Intent Workflows (5)
            intent_primitives = [
                "workflow_run_drop_test",
                "workflow_run_shock_analysis",
                "workflow_run_random_vibration",
                "workflow_run_thermal_warpage",
                "workflow_train_surrogate_model",
            ]
            for name in intent_primitives:
                assert name in tool_names, f"Intent workflow primitive '{name}' missing from FastMCP tools"

            # Mechanical passthroughs (4)
            mechanical_primitives = [
                "mechanical_connect",
                "mechanical_launch",
                "mechanical_run_script",
                "mechanical_disconnect",
            ]
            for name in mechanical_primitives:
                assert name in tool_names, f"Mechanical primitive '{name}' missing from FastMCP tools"

            # Workbench passthrough
            # Support execute_workbench_script or workbench_run_script_live
            wb_found = ("execute_workbench_script" in tool_names or "workbench_run_script_live" in tool_names)
            assert wb_found, "Workbench script passthrough primitive missing from FastMCP tools"

            # optiSLang passthroughs (2)
            optislang_primitives = [
                "optislang_connect",
                "optislang_run_script",
            ]
            for name in optislang_primitives:
                assert name in tool_names, f"optiSLang primitive '{name}' missing from FastMCP tools"

        run_async(_verify())

    def test_canonical_primitives_callable(self):
        """Verify that canonical primitives are callable via mcp.call_tool and return standard envelopes."""
        async def _verify():
            # 1. Sentinel status query for a non-existent dummy job
            res = await mcp.call_tool("get_simulation_status", {"job_id": "nonexistent_job_12345"})
            assert res.content, "Sentinel get_simulation_status returned empty content"
            raw_data = json.loads(res.content[0].text) if isinstance(res.content[0].text, str) else res.content[0].text
            assert "status" in raw_data or "ok" in raw_data

            # 2. Mechanical passthrough (offline mode)
            res_mech = await mcp.call_tool("mechanical_run_script", {"script": "print('hello')"})
            assert res_mech.content, "mechanical_run_script returned empty content"
            mech_data = json.loads(res_mech.content[0].text)
            assert "ok" in mech_data
            assert mech_data["ok"] is False  # Offline mode

            # 3. optiSLang passthrough (offline mode)
            res_opti = await mcp.call_tool("optislang_run_script", {"script": "a = 1"})
            assert res_opti.content, "optislang_run_script returned empty content"
            opti_data = json.loads(res_opti.content[0].text)
            assert "ok" in opti_data
            assert opti_data["ok"] is False  # Offline mode

        run_async(_verify())

    def test_runtime_alias_lookup_and_resolution(self):
        """Verify internal alias lookup dictionary and that mcp.call_tool resolves aliases to canonicals."""
        # 1. ALIAS_REGISTRY 字典映射驗證
        assert ALIAS_REGISTRY.get("run_drop_test") == "workflow_run_drop_test"
        assert ALIAS_REGISTRY.get("connect_to_mechanical") == "mechanical_connect"
        assert ALIAS_REGISTRY.get("connect_optislang") == "optislang_connect"
        assert ALIAS_REGISTRY.get("add_force") == "mechanical_add_force"

        # 2. get_canonical_name 驗證
        assert get_canonical_name("run_drop_test") == "workflow_run_drop_test"
        assert get_canonical_name("workflow_run_drop_test") == "workflow_run_drop_test"
        assert get_canonical_name("unknown_tool") == "unknown_tool"

        # 3. 運行時調用未暴露別名時，mcp.call_tool 自動解析至 canonical 實作
        async def _test_call():
            res_alias = await mcp.call_tool("run_mechanical_script", {"script": "print('test')"})
            res_canon = await mcp.call_tool("mechanical_run_script", {"script": "print('test')"})
            data_alias = json.loads(res_alias.content[0].text)
            data_canon = json.loads(res_canon.content[0].text)
            assert data_alias["ok"] == data_canon["ok"]

        run_async(_test_call())

    def test_expose_aliases_environment_toggle(self, monkeypatch):
        """Verify that setting ANSYS_MCP_EXPOSE_ALIASES=1 exposes aliases with proper deprecation prefix."""
        monkeypatch.setenv("ANSYS_MCP_EXPOSE_ALIASES", "1")
        assert should_expose_aliases() is True

        async def _verify():
            tools = await mcp.list_tools()
            tool_map = {t.name: t for t in tools}

            # 檢查別名存在
            assert "run_drop_test" in tool_map
            assert "connect_to_mechanical" in tool_map
            assert "add_force" in tool_map

            # 檢查別名包含棄用前綴
            alias_tool = tool_map["run_drop_test"]
            assert alias_tool.description.startswith("[DEPRECATED ALIAS for workflow_run_drop_test]")

        run_async(_verify())

    def test_preflight_gatekeeper_guards_preserved(self):
        """Verify pre-flight physical guards (Gatekeeper) on workflows remain strictly enforced."""
        from ansys_unified_mcp.workflows.drop_test import run_drop_test

        # 傳入違反物理邊界的組態（初速向量反向朝 +Z，遠離位於下方的地面）
        res = run_drop_test(
            cad_path="test_model.pmdb",
            gravity_direction=[0.0, 0.0, 1.0],  # 違反 GATE-DRP-001: 初速度必須指向地面
        )
        assert res["ok"] is False
        assert res.get("blocked") is True
        assert "prescription_report" in res
