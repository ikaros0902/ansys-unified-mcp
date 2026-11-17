# -*- coding: utf-8 -*-
"""Per-session 工具可見性 (方案 D) 整合測試。

驗證單一 all-profile FastMCP server 下：
- session 設定 product 偏好後，list_tools 收斂為該 product 子集 + 通用工具。
- 不同 session 互不干擾 (隔離)。
- 別名解析鏈不受影響。
- product 分類純函式的邊界行為。
"""

import asyncio

import pytest

from ansys_unified_mcp.tools.visibility import product_of_module, COMMON_PRODUCT


# ---- product 分類純函式 (無需 server) ----

def test_product_of_module_products():
    assert product_of_module("ansys_unified_mcp.products.mechanical.tools") == "mechanical"
    assert product_of_module("ansys_unified_mcp.products.geometry.tools") == "geometry"
    assert product_of_module("ansys_unified_mcp.products.fluent.tools") == "fluent"
    assert product_of_module("ansys_unified_mcp.products.workbench.tools") == "workbench"


def test_product_of_module_common_and_workflow():
    assert product_of_module("ansys_unified_mcp.tools.docs_tools") == COMMON_PRODUCT
    assert product_of_module("ansys_unified_mcp.tools.sentinel_tools") == COMMON_PRODUCT
    assert product_of_module("ansys_unified_mcp.tools.session_manager_tools") == COMMON_PRODUCT
    assert product_of_module("ansys_unified_mcp.tools.intent_tools") == "workflow"


def test_product_of_module_unknown_is_common():
    # 未知來源從寬歸類為通用 (避免誤隱藏)
    assert product_of_module("some.random.module") == COMMON_PRODUCT
    assert product_of_module("") == COMMON_PRODUCT


# ---- per-session 可見性 (需 in-memory Client 模擬真實 session) ----

def _run(coro):
    return asyncio.run(coro)


def test_per_session_visibility_and_isolation():
    """設定 geometry 偏好後工具收斂且不含 mechanical；另一 session 不受影響。"""
    import ansys_unified_mcp.__main__  # noqa: F401  確保所有工具已註冊
    from ansys_unified_mcp.shared import mcp
    from fastmcp import Client

    async def scenario():
        async with Client(mcp) as c:
            before = {t.name for t in await c.list_tools()}
            await c.call_tool("ans_session_set_workspace", {"products": ["geometry"]})
            after = {t.name for t in await c.list_tools()}
        # 另一全新 session 不設偏好，應維持全集 (隔離驗證)
        async with Client(mcp) as c2:
            full = {t.name for t in await c2.list_tools()}
        return before, after, full

    before, after, full = _run(scenario())

    # 設定後嚴格收斂 (子集)
    assert after < before, "設定偏好後工具集應為設定前的真子集"
    # geometry 工具保留 (以來源判定，geometry 模組的代表工具)
    assert any("geometry" in n or n in ("create_sketch", "rebuild_model") for n in after)
    # mechanical 工具被隱藏
    assert not any(n.startswith("mechanical_") for n in after)
    # 通用 session 管理工具恆可見
    assert "ans_session_status" in after
    assert "ans_session_set_workspace" in after
    # session 隔離：第二個 session 未設偏好，看到全集
    assert full == before


def test_set_workspace_rejects_invalid_product():
    """非法 product 名稱回 ok=False，不改動可見性。"""
    import ansys_unified_mcp.__main__  # noqa: F401
    from ansys_unified_mcp.shared import mcp
    from fastmcp import Client

    async def scenario():
        async with Client(mcp) as c:
            res = await c.call_tool("ans_session_set_workspace", {"products": ["not_a_product"]})
            return res.data

    data = _run(scenario())
    assert data["ok"] is False
    assert "非法" in data["error"]


def test_set_workspace_empty_clears_restriction():
    """空清單清除限制，回到全集。"""
    import ansys_unified_mcp.__main__  # noqa: F401
    from ansys_unified_mcp.shared import mcp
    from fastmcp import Client

    async def scenario():
        async with Client(mcp) as c:
            full = {t.name for t in await c.list_tools()}
            await c.call_tool("ans_session_set_workspace", {"products": ["geometry"]})
            restricted = {t.name for t in await c.list_tools()}
            await c.call_tool("ans_session_set_workspace", {"products": []})
            cleared = {t.name for t in await c.list_tools()}
        return full, restricted, cleared

    full, restricted, cleared = _run(scenario())
    assert restricted < full
    assert cleared == full


def test_product_of_module_sound_and_apikb():
    """sound_tools 應歸為 sound 域，apikb_tools 應歸為 common 域。"""
    assert product_of_module("ansys_unified_mcp.tools.sound_tools") == "sound"
    assert product_of_module("ansys_unified_mcp.tools.apikb_tools") == COMMON_PRODUCT


def test_set_workspace_core_and_all_products():
    """core 模式僅保留通用核心工具；dyna 與 sound 亦可合法設定並過濾。"""
    import ansys_unified_mcp.__main__  # noqa: F401
    from ansys_unified_mcp.shared import mcp
    from fastmcp import Client

    async def scenario():
        async with Client(mcp) as c:
            res_core = await c.call_tool("ans_session_set_workspace", {"products": ["core"]})
            core_tools = {t.name for t in await c.list_tools()}
            res_ds = await c.call_tool("ans_session_set_workspace", {"products": ["dyna", "sound"]})
            ds_tools = {t.name for t in await c.list_tools()}
        return res_core.data, core_tools, res_ds.data, ds_tools

    res_core, core_tools, res_ds, ds_tools = _run(scenario())

    assert res_core["ok"] is True
    assert "ans_session_status" in core_tools
    assert "api_search" in core_tools
    assert not any(n.startswith("mechanical_") for n in core_tools)
    assert not any(n.startswith("geometry_") for n in core_tools)
    assert not any(n.startswith("sound_") for n in core_tools)

    assert res_ds["ok"] is True
    assert "dyna_solve" in ds_tools
    assert "sound_calculate_zwicker_loudness" in ds_tools
    assert not any(n.startswith("mechanical_") for n in ds_tools)


def test_visibility_cache_refreshes_on_dynamic_registration():
    """TOOL_REGISTRY 新增工具後，_ensure_map() 應自動偵測並重建映射。"""
    from ansys_unified_mcp.shared import TOOL_REGISTRY, mcp
    from ansys_unified_mcp.tools.visibility import WorkspaceVisibilityMiddleware

    mw = WorkspaceVisibilityMiddleware(mcp, "ansys_visible_products")
    initial_map = mw._ensure_map()
    dummy_name = "_test_dynamic_dyna_tool_temp"

    def _dummy_fn():
        return None

    _dummy_fn.__module__ = "ansys_unified_mcp.products.dyna.tools"
    assert dummy_name not in initial_map
    try:
        TOOL_REGISTRY[dummy_name] = _dummy_fn
        refreshed_map = mw._ensure_map()
        assert refreshed_map.get(dummy_name) == "dyna"
    finally:
        TOOL_REGISTRY.pop(dummy_name, None)


def test_dual_track_tools_include_backend_metadata():
    """Dual-track 基準工具回傳必須包含 execution_mode 與 backend_notice。"""
    from ansys_unified_mcp.products.aedt.tools import aedt_solve_hfss
    from ansys_unified_mcp.tools.sound_tools import sound_calculate_zwicker_loudness

    hfss_res = aedt_solve_hfss()
    sound_res = sound_calculate_zwicker_loudness(frequency=1000.0, spl_db=40.0)

    assert hfss_res["ok"] is True
    assert hfss_res["execution_mode"] == "benchmark_fallback"
    assert "backend_notice" in hfss_res

    assert sound_res["ok"] is True
    assert sound_res["execution_mode"] == "benchmark_fallback"
    assert "backend_notice" in sound_res

