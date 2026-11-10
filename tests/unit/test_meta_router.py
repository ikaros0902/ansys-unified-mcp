# -*- coding: utf-8 -*-
"""Unit test suite for Meta-Router and Pydantic Flat Validation system.

Verifies:
- Standard and ASD-STE100 response/error envelopes.
- PaginationParams and PaginatedResponse slicing.
- 4-key ToolAnnotations builder and convenience constructors.
- Flat Pydantic validation decorator with sync/async, type coercion, and extra forbid.
- Domain input models schema generation and constraints.
- Dynamic tool discovery via ans_list_domain_tools.
- Dynamic tool execution and envelope wrapping via ans_call_domain_tool.
- FastMCP server alias export in server.py.

All comments and docstrings in this module strictly use ASCII English.
"""

import inspect
import pytest
from pydantic import BaseModel, ConfigDict, Field

from ansys_unified_mcp.schemas.common_envelope import (
    PaginatedResponse,
    PaginationParams,
    create_error_envelope,
    create_response_envelope,
    paginate_list,
)
from ansys_unified_mcp.schemas.domain_inputs import (
    FluentBoundaryConditionInput,
    HFSSAdaptiveMeshInput,
    MechanicalMeshInput,
    OpticsSimulationInput,
)
from ansys_unified_mcp.schemas.tool_annotations import (
    ToolAnnotations,
    create_tool_annotations,
    validate_flat_pydantic,
)
from ansys_unified_mcp.tools.meta_router_tools import (
    ans_call_domain_tool,
    ans_list_domain_tools,
    normalize_domain,
)


class TestCommonEnvelope:
    """Tests for common_envelope module."""

    def test_create_response_envelope_defaults(self):
        env = create_response_envelope(data={"count": 5}, summary="Operation finished.")
        assert env["ok"] is True
        assert env["status"] == "success"
        assert env["summary"] == "Operation finished."
        assert env["data"] == {"count": 5}
        assert env["execution_time_ms"] == 0.0
        assert "file_path" not in env
        assert "sha256" not in env

    def test_create_response_envelope_full_metadata(self):
        env = create_response_envelope(
            data="payload",
            summary="File saved.",
            file_path="/tmp/test.txt",
            sha256="abc123hash",
            execution_time_ms=12.5,
            extra_tag="benchmark",
        )
        assert env["ok"] is True
        assert env["status"] == "success"
        assert env["file_path"] == "/tmp/test.txt"
        assert env["sha256"] == "abc123hash"
        assert env["execution_time_ms"] == 12.5
        assert env["extra_tag"] == "benchmark"

    def test_create_error_envelope(self):
        env = create_error_envelope(
            status="error",
            error_code="SOLVER_TIMEOUT",
            message="Mechanical solver did not respond within 60 seconds.",
            recovery_action="Increase timeout parameter and verify solver license.",
            solver_pid=1234,
        )
        assert env["ok"] is False
        assert env["status"] == "error"
        assert env["error_code"] == "SOLVER_TIMEOUT"
        assert env["message"] == "Mechanical solver did not respond within 60 seconds."
        assert env["error"] == env["message"]
        assert env["recovery_action"] == "Increase timeout parameter and verify solver license."
        assert env["suggested_actions"] == ["Increase timeout parameter and verify solver license."]
        assert env["solver_pid"] == 1234

    def test_pagination_params_validation(self):
        params = PaginationParams(limit=50, offset=10)
        assert params.limit == 50
        assert params.offset == 10

        # Boundary checks
        with pytest.raises(Exception):
            PaginationParams(limit=0)  # ge=1

        with pytest.raises(Exception):
            PaginationParams(limit=10, invalid_field=99)  # extra='forbid'

    def test_paginate_list_helper(self):
        items = list(range(100))
        resp = paginate_list(items, limit=15, offset=30)
        assert isinstance(resp, PaginatedResponse)
        assert resp.total == 100
        assert resp.limit == 15
        assert resp.offset == 30
        assert resp.has_more is True
        assert resp.items == list(range(30, 45))

        # Edge case: end of list
        last_resp = paginate_list(items, limit=20, offset=90)
        assert last_resp.has_more is False
        assert len(last_resp.items) == 10


class TestToolAnnotations:
    """Tests for ToolAnnotations and validation decorator."""

    def test_tool_annotations_create(self):
        ann = ToolAnnotations.create(read_only=True, destructive=False, idempotent=True, open_world=False)
        d = ann.to_dict()
        assert d == {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        }

    def test_tool_annotations_factories(self):
        ro = ToolAnnotations.read_only().to_dict()
        assert ro["readOnlyHint"] is True
        assert ro["destructiveHint"] is False

        mut = ToolAnnotations.mutation(destructive=True).to_dict()
        assert mut["readOnlyHint"] is False
        assert mut["destructiveHint"] is True

        ext = ToolAnnotations.external().to_dict()
        assert ext["openWorldHint"] is True

    def test_create_tool_annotations_helper(self):
        d = create_tool_annotations(read_only=True, idempotent=True)
        assert d["readOnlyHint"] is True
        assert d["idempotentHint"] is True
        assert d["destructiveHint"] is False
        assert d["openWorldHint"] is False

    def test_validate_flat_pydantic_sync(self):
        class SampleInput(BaseModel):
            model_config = ConfigDict(extra="forbid")
            value: int = Field(..., ge=0)
            tag: str = Field(default="primary")

        @validate_flat_pydantic(SampleInput)
        def process_item(value: int, tag: str = "primary") -> dict:
            return {"ok": True, "result": f"{tag}:{value}"}

        # Check signature remains flat
        sig = inspect.signature(process_item)
        assert "value" in sig.parameters
        assert "tag" in sig.parameters

        # Valid call with type coercion
        res = process_item(value="42", tag="custom")
        assert res["ok"] is True
        assert res["result"] == "custom:42"

        # Default filling
        res_default = process_item(value=10)
        assert res_default["ok"] is True
        assert res_default["result"] == "primary:10"

        # Extra forbidden parameter rejection
        res_extra = process_item(value=10, unknown_arg=99)
        assert res_extra["ok"] is False
        assert res_extra["error_code"] == "VALIDATION_ERROR"
        assert "unknown_arg" in res_extra["message"]

        # Type violation rejection
        res_type = process_item(value="not_an_int")
        assert res_type["ok"] is False
        assert res_type["error_code"] == "VALIDATION_ERROR"

    @pytest.mark.anyio
    async def test_validate_flat_pydantic_async(self):
        class AsyncInput(BaseModel):
            model_config = ConfigDict(extra="forbid")
            multiplier: float = Field(default=2.0)

        @validate_flat_pydantic(AsyncInput)
        async def compute_async(multiplier: float = 2.0) -> dict:
            return {"ok": True, "scaled": multiplier * 10}

        res = await compute_async(multiplier=3.5)
        assert res["ok"] is True
        assert res["scaled"] == 35.0

        res_err = await compute_async(multiplier="invalid")
        assert res_err["ok"] is False
        assert res_err["error_code"] == "VALIDATION_ERROR"


class TestDomainInputs:
    """Tests for physics domain input models."""

    def test_hfss_adaptive_mesh_input(self):
        inp = HFSSAdaptiveMeshInput(freq_ghz=10.0, max_delta_s=0.01)
        assert inp.freq_ghz == 10.0
        assert inp.max_delta_s == 0.01
        assert inp.max_passes == 20  # default

        # extra forbid
        with pytest.raises(Exception):
            HFSSAdaptiveMeshInput(freq_ghz=10.0, bogus="extra")

    def test_fluent_boundary_condition_input(self):
        inp = FluentBoundaryConditionInput(zone_name="inlet_1", velocity_magnitude=5.0)
        assert inp.zone_name == "inlet_1"
        assert inp.velocity_magnitude == 5.0
        assert inp.bc_type == "velocity-inlet"

        schema = FluentBoundaryConditionInput.model_json_schema()
        assert schema["type"] == "object"
        assert "zone_name" in schema["properties"]

    def test_mechanical_mesh_input(self):
        inp = MechanicalMeshInput(element_size=0.005)
        assert inp.element_size == 0.005
        assert inp.growth_rate == 1.2


class TestMetaRouterTools:
    """Tests for ans_list_domain_tools and ans_call_domain_tool."""

    def test_normalize_domain(self):
        assert normalize_domain("  CFD  ") == "fluids"
        assert normalize_domain("Mechanical") == "structural"
        assert normalize_domain("hfss") == "electromagnetics"
        assert normalize_domain("cad") == "geometry"
        assert normalize_domain("heat") == "thermal"

    @pytest.mark.anyio
    async def test_list_domain_tools_fluids(self):
        res = await ans_list_domain_tools(domain="fluids")
        assert res["ok"] is True
        assert res["status"] == "success"
        data = res["data"]
        assert data["domain"] == "fluids"
        assert data["tool_count"] >= 10
        tool_names = [t["name"] for t in data["tools"]]
        assert "fluent_read_case" in tool_names

        # Verify tool structure
        sample_tool = next(t for t in data["tools"] if t["name"] == "fluent_read_case")
        assert "annotations" in sample_tool
        assert "parameters" in sample_tool
        assert "readOnlyHint" in sample_tool["annotations"]

    @pytest.mark.anyio
    async def test_list_domain_tools_electromagnetics(self):
        res = await ans_list_domain_tools(domain="electromagnetics")
        assert res["ok"] is True
        data = res["data"]
        assert data["domain"] == "electromagnetics"
        assert data["tool_count"] >= 2
        tool_names = [t["name"] for t in data["tools"]]
        assert "hfss_setup_adaptive_mesh" in tool_names
        assert "maxwell_setup_solver" in tool_names

    @pytest.mark.anyio
    async def test_call_domain_tool_staging(self):
        res = await ans_call_domain_tool(
            domain="electromagnetics",
            tool_name="hfss_setup_adaptive_mesh",
            arguments={"freq_ghz": 5.8},
        )
        assert res["ok"] is True
        assert res["status"] == "success"
        assert res["data"]["parameters"]["freq_ghz"] == 5.8
        assert res["data"]["parameters"]["max_passes"] == 20

    @pytest.mark.anyio
    async def test_call_domain_tool_staging_validation_failure(self):
        res = await ans_call_domain_tool(
            domain="electromagnetics",
            tool_name="hfss_setup_adaptive_mesh",
            arguments={"freq_ghz": 5.8, "extra_illegal_field": 123},
        )
        assert res["ok"] is False
        assert res["error_code"] == "VALIDATION_ERROR"
        assert "extra_illegal_field" in res["message"]

    @pytest.mark.anyio
    async def test_call_domain_tool_live_mechanical_instances(self):
        res = await ans_call_domain_tool(
            domain="structural",
            tool_name="mechanical_list_instances",
            arguments={},
        )
        assert res["ok"] is True
        assert res["status"] == "success"
        assert "instances" in res["data"]
        assert res["execution_time_ms"] >= 0.0

    @pytest.mark.anyio
    async def test_call_domain_tool_not_found(self):
        res = await ans_call_domain_tool(
            domain="fluids",
            tool_name="completely_non_existent_solver_tool",
            arguments={},
        )
        assert res["ok"] is False
        assert res["error_code"] == "TOOL_NOT_FOUND"
        assert "recovery_action" in res

    @pytest.mark.anyio
    async def test_call_domain_tool_argument_type_mismatch(self):
        res = await ans_call_domain_tool(
            domain="structural",
            tool_name="mechanical_connect",
            arguments={"port": "not_an_integer_port"},
        )
        assert res["ok"] is False
        assert res["error_code"] in ("INVALID_ARGUMENTS", "VALIDATION_ERROR", "TOOL_EXECUTION_EXCEPTION")


class TestServerAliasExport:
    """Tests for server.py entrypoint export."""

    def test_server_exports_mcp_and_main(self):
        from ansys_unified_mcp.server import mcp, main
        assert mcp is not None
        assert mcp.name == "ansys-unified-mcp"
        assert callable(main)
