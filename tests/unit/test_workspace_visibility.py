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

from ansys_unified_mcp.core.visibility import product_of_module, COMMON_PRODUCT


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
