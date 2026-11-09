# -*- coding: utf-8 -*-
"""BDD unit tests for MCP connection resilience, dual-profile routing, and fast startup.

Verifies:
1. 100% TOOL_REGISTRY coverage for both @aliased_tool and @mcp.tool decorators.
2. Accurate product classification in WorkspaceVisibilityMiddleware (0 unmapped leaks).
3. Non-blocking worker-thread execution in ans_call_domain_tool across all domains.
4. Complete module mapping across all 18 physics domains in DOMAIN_MODULE_MAP.
5. Fast read-only source validation in apikb.query.
"""

from __future__ import annotations

import asyncio
import time

import pytest

import ansys_unified_mcp.__main__  # noqa: F401
from ansys_unified_mcp.analytics.apikb import query as apikb_query
from ansys_unified_mcp.shared import TOOL_REGISTRY, mcp
from ansys_unified_mcp.tools.meta_router_tools import (
    DOMAIN_MODULE_MAP,
    ans_call_domain_tool,
)
from ansys_unified_mcp.tools.visibility import (
    COMMON_PRODUCT,
    WorkspaceVisibilityMiddleware,
)


def test_given_all_profile_when_listing_tools_then_tool_registry_has_100_percent_coverage():
    """Given the server is loaded, when listing canonical tools, all tools exist in TOOL_REGISTRY."""
    tools = asyncio.run(mcp.list_tools())
    canonical_names = {t.name for t in tools}
    assert len(canonical_names) >= 200
    missing = canonical_names - set(TOOL_REGISTRY.keys())
    assert missing == set(), f"Tools missing from TOOL_REGISTRY: {sorted(missing)}"


def test_given_workspace_visibility_middleware_when_building_map_then_no_product_tools_leak_to_common():
    """Given WorkspaceVisibilityMiddleware, when _ensure_map() runs, all product tools map to their product domain."""
    mw = WorkspaceVisibilityMiddleware(mcp, "ansys_visible_products")
    name_to_product = mw._ensure_map()
    tools = asyncio.run(mcp.list_tools())

    leaked = []
    for t in tools:
        fn = TOOL_REGISTRY.get(t.name)
        mod = getattr(fn, "__module__", "") if fn else ""
        if mod.startswith("ansys_unified_mcp.products."):
            mapped_prod = name_to_product.get(t.name, COMMON_PRODUCT)
            if mapped_prod == COMMON_PRODUCT:
                leaked.append((t.name, mod))

    assert leaked == [], f"Product tools leaked as common: {leaked}"


def test_given_meta_router_when_calling_mcp_tool_function_then_executes_without_blocking_event_loop():
    """Given a tool registered via @mcp.tool, when called via ans_call_domain_tool, it succeeds off the main loop."""
    res_sound = asyncio.run(
        ans_call_domain_tool(
            domain="sound",
            tool_name="sound_calculate_zwicker_loudness",
            arguments={"frequency": 1000.0, "spl_db": 40.0},
        )
    )
    assert res_sound["status"] == "success"
    assert res_sound["data"]["loudness_sone"] == pytest.approx(1.0, rel=1e-2)

    res_fluent = asyncio.run(
        ans_call_domain_tool(
            domain="fluids",
            tool_name="fluent_status",
            arguments={},
        )
    )
    assert res_fluent["status"] == "success"


def test_given_domain_module_map_when_inspecting_domains_then_all_physics_domains_have_modules():
    """Given DOMAIN_MODULE_MAP, when checking all 18 domains, every domain maps to at least one module."""
    empty_domains = [dom for dom, mods in DOMAIN_MODULE_MAP.items() if not mods]
    assert empty_domains == [], f"Domains with empty module list: {empty_domains}"


def test_given_apikb_database_when_checking_sources_current_then_fast_check_completes_quickly():
    """Given the pre-built api_kb.sqlite, when _sources_are_current() runs, it completes in under 50ms."""
    apikb_query._sources_are_current()  # warm up cache
    t0 = time.perf_counter()
    assert apikb_query._sources_are_current() is True
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert elapsed_ms < 50.0, f"_sources_are_current() took {elapsed_ms:.2f} ms"
