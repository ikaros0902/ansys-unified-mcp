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

from ansys_unified_mcp.products.geometry import call_dispatch as sim_impl


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


def test_get_bounding_box_single_body():
    """驗證查詢單一實體包圍盒與尺寸資訊。"""
    design = _fake_design(bodies=[("DIMM1", "b-1")])
    with patch.object(sim_impl, "_modeler", object()), \
         patch.object(sim_impl, "_geom_get_design", return_value=design), \
         patch("ansys_unified_mcp.products.geometry.call_dispatch._bbox_m", return_value=((0.0, 0.01, 0.0), (0.1, 0.05, 0.02))):
        text = _call("geometry_get_bounding_box", {"body_name": "DIMM1"})

    assert "實體 'DIMM1' 包圍盒與尺寸資訊" in text
    assert "尺寸 (mm): X=100.0, Y=40.0, Z=20.0" in text
    assert "最小座標 min (mm): [0.0, 10.0, 0.0]" in text
    assert "最大座標 max (mm): [100.0, 50.0, 20.0]" in text


def test_get_bounding_box_not_found():
    """查詢不存在的實體名稱時，應回傳提示與可用實體清單。"""
    design = _fake_design(bodies=[("DIMM1", "b-1")])
    with patch.object(sim_impl, "_modeler", object()), \
         patch.object(sim_impl, "_geom_get_design", return_value=design):
        text = _call("geometry_get_bounding_box", {"body_name": "NonExistent"})

    assert "找不到名為 'NonExistent' 的實體" in text
    assert "DIMM1" in text


def test_get_bounding_box_all_bodies():
    """未指定 body_name 時，應列出所有實體的包圍盒。"""
    design = _fake_design(bodies=[("DIMM1", "b-1"), ("Socket1", "b-2")])
    with patch.object(sim_impl, "_modeler", object()), \
         patch.object(sim_impl, "_geom_get_design", return_value=design), \
         patch("ansys_unified_mcp.products.geometry.call_dispatch._bbox_m", return_value=((0.0, 0.0, 0.0), (0.1, 0.01, 0.02))):
        text = _call("geometry_get_bounding_box", {})

    assert "當前設計共有 2 個實體 (Body) 之包圍盒清單" in text
    assert "DIMM1" in text
    assert "Socket1" in text


def test_run_script_grpc():
    """驗證透過 gRPC 執行幾何腳本之分派邏輯。"""
    with patch.object(sim_impl, "_modeler", object()), \
         patch("ansys_unified_mcp.products.geometry.controller.run_script", return_value={"ok": True, "values": {"ans": "42"}}):
        text = _call("geometry_run_script", {"script_content": "result = {'ans': '42'}"})

    assert "腳本已成功透過 PyAnsys Geometry gRPC 在 SpaceClaim 執行完成" in text
    assert "result" in text
    assert "42" in text


def test_simplify_ram_without_motherboard():
    """驗證無主機板模式下，自動以 socket 底面為基準定位。"""
    ram_body = SimpleNamespace(name="DIMM_1")
    sock_body = SimpleNamespace(name="SOCKET_1")
    design = SimpleNamespace(add_component=lambda name: None)

    with patch.object(sim_impl, "_modeler", object()), \
         patch.object(sim_impl, "_geom_get_design", return_value=design), \
         patch("ansys_unified_mcp.products.geometry.simplify_ram._find_bodies_by_name", side_effect=lambda name: [ram_body] if name == "DIMM_1" else [sock_body]), \
         patch("ansys_unified_mcp.products.geometry.simplify_ram._bbox_m", return_value=((0.0, 0.005, 0.0), (0.1, 0.015, 0.02))), \
         patch("ansys_unified_mcp.products.geometry.simplify_ram._build_ram_block", return_value={
             "shape": "convex",
             "base_size_mm": [100, 10, 20],
             "top_size_mm": [90, 30, 10],
             "block_min_mm": [0, 5, 0],
             "block_max_mm": [100, 45, 20],
             "block_size_mm": [100, 40, 20],
             "named_selection": "ram_bottom",
             "named_selection_created": True,
         }), \
         patch("ansys_unified_mcp.products.geometry.simplify_ram._suppress_hide_sources", return_value=(True, "")):
        text = _call("geometry_simplify_ram", {"ram": "DIMM_1", "socket": "SOCKET_1"})

    assert "✓ RAM 簡化完成" in text
    assert "無主機板模式" in text
    assert "Socket 底面" in text


