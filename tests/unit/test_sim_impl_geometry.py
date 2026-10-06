"""Driver 層單元測試：sim_impl.call_tool 的 geometry 列舉分支。

對應審查段待分類事項（docs/reviews/2026-10-02-phase2-3-feasibility-assessment.md，任務 3.3）：
resource 與 tool wrapper 層已有測試，但最底層 driver 分支
(`elif name == "geometry_list_named_selections"` / `"geometry_list_bodies"`)
原本僅靠 API 簽名靜態驗證，缺乏執行覆蓋。此處補齊，mock `_geom_get_design`
回傳假設計物件，驗證 driver 分支的格式化輸出與邊界（空清單、未連線）。
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import patch

from ansys_unified_mcp.drivers import sim_impl


def run_async(coro):
    return asyncio.run(coro)


def _call(name, arguments=None):
    """呼叫 driver dispatcher 並取出單一 TextContent 的純文字。"""
    res = run_async(sim_impl.call_tool(name, arguments or {}))
    assert len(res) == 1
    return res[0].text


def _fake_design(bodies=(), named_selections=()):
    """建立假設計物件：bodies / named_selections 皆為具 .name/.id 的物件清單。"""
    return SimpleNamespace(
        bodies=[SimpleNamespace(name=n, id=i) for n, i in bodies],
        named_selections=[SimpleNamespace(name=n, id=i) for n, i in named_selections],
    )


def test_list_named_selections_formats_entries():
    """已連線且有具名選擇時，應逐筆列出 name 與 id。"""
    design = _fake_design(named_selections=[("NS_Fixed", "ns-1"), ("NS_Load", "ns-2")])
    with patch.object(sim_impl, "_modeler", object()), \
         patch.object(sim_impl, "_geom_get_design", return_value=design):
        text = _call("geometry_list_named_selections")

    assert "具名選擇 (2)" in text
    assert "NS_Fixed (id=ns-1)" in text
    assert "NS_Load (id=ns-2)" in text


def test_list_named_selections_empty():
    """已連線但無具名選擇時，應回傳明確空清單訊息。"""
    design = _fake_design(named_selections=[])
    with patch.object(sim_impl, "_modeler", object()), \
         patch.object(sim_impl, "_geom_get_design", return_value=design):
        text = _call("geometry_list_named_selections")

    assert text == "當前設計無具名選擇"


def test_list_named_selections_not_connected():
    """未連線（_modeler is None）時，應提示先執行 geometry_launch，不觸碰設計。"""
    with patch.object(sim_impl, "_modeler", None):
        text = _call("geometry_list_named_selections")

    assert "未連線" in text
    assert "geometry_launch" in text


def test_list_bodies_formats_entries():
    """對稱覆蓋 geometry_list_bodies 分支，確保兩條列舉邏輯行為一致。"""
    design = _fake_design(bodies=[("Block1", "b-1")])
    with patch.object(sim_impl, "_modeler", object()), \
         patch.object(sim_impl, "_geom_get_design", return_value=design):
        text = _call("geometry_list_bodies")

    assert "幾何體 (1)" in text
    assert "Block1 (id=b-1)" in text
