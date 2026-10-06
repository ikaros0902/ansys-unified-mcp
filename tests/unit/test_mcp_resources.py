"""Unit tests for MCP Resources (任務 3.3, docs/reviews/2026-10-02-phase2-3-feasibility-assessment.md).

涵蓋 ansys://mechanical/model-tree、ansys://mechanical/materials、
ansys://geometry/model-tree、ansys://geometry/named-selections。
"""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, patch

from ansys_unified_mcp.products.mechanical.tools import (
    mechanical_materials_resource,
    mechanical_model_tree_resource,
)


def run_async(coro):
    return asyncio.run(coro)


def test_mechanical_model_tree_resource_not_connected():
    """未連線時應回傳標準失敗信封，不拋出例外。"""
    with patch("ansys_unified_mcp.products.mechanical.tools.controller") as mock_controller:
        mock_controller.is_connected.return_value = False
        result = json.loads(mechanical_model_tree_resource())

    assert result["ok"] is False
    assert "尚未連線" in result["error"]


def test_mechanical_model_tree_resource_success():
    """已連線且腳本回傳合法 JSON 時，應解析並包成 model_tree 欄位。"""
    fake_model_info = {
        "bodies": [{"name": "Block1", "material": "Steel"}],
        "named_selections": ["NS_Fixed"],
        "analyses": [{"name": "Static Structural", "type": "StaticStructural"}],
    }
    with patch("ansys_unified_mcp.products.mechanical.tools.controller") as mock_controller:
        mock_controller.is_connected.return_value = True
        mock_controller.run_script.return_value = json.dumps(fake_model_info)
        result = json.loads(mechanical_model_tree_resource())

    assert result["ok"] is True
    assert result["model_tree"] == fake_model_info


def test_mechanical_model_tree_resource_parse_failure():
    """腳本回傳非 JSON（如 ACT 錯誤訊息）時，應回傳失敗信封並保留原始輸出供排查。"""
    with patch("ansys_unified_mcp.products.mechanical.tools.controller") as mock_controller:
        mock_controller.is_connected.return_value = True
        mock_controller.run_script.return_value = "Error: Script execution failed"
        result = json.loads(mechanical_model_tree_resource())

    assert result["ok"] is False
    assert result["raw"] == "Error: Script execution failed"


def test_mechanical_materials_resource_not_connected():
    """未連線時應回傳標準失敗信封。"""
    with patch("ansys_unified_mcp.products.mechanical.tools.controller") as mock_controller:
        mock_controller.is_connected.return_value = False
        result = json.loads(mechanical_materials_resource())

    assert result["ok"] is False
    assert "尚未連線" in result["error"]


def test_mechanical_materials_resource_success():
    """已連線且腳本回傳合法 JSON 時，應解析並展開材料清單欄位。"""
    with patch("ansys_unified_mcp.products.mechanical.tools.controller") as mock_controller:
        mock_controller.is_connected.return_value = True
        mock_controller.run_script.return_value = json.dumps({"materials": ["Structural Steel", "Aluminum"]})
        result = json.loads(mechanical_materials_resource())

    assert result["ok"] is True
    assert result["materials"] == ["Structural Steel", "Aluminum"]


def test_geometry_model_tree_resource_delegates_to_list_bodies():
    """geometry model-tree resource 應委派至既有 geometry_list_bodies 的 sim_impl.call_tool 邏輯。"""
    from ansys_unified_mcp.products.geometry.tools import geometry_model_tree_resource

    fake_content = type("FakeContent", (), {"text": '{"ok": true, "bodies": ["Block1"]}'})()
    with patch(
        "ansys_unified_mcp.products.geometry.tools.sim_impl.call_tool",
        new=AsyncMock(return_value=[fake_content]),
    ) as mock_call_tool:
        result = run_async(geometry_model_tree_resource())

    mock_call_tool.assert_called_once_with("geometry_list_bodies", {})
    assert result == '{"ok": true, "bodies": ["Block1"]}'


def test_geometry_named_selections_resource_delegates_to_list_named_selections():
    """geometry named-selections resource 應委派至既有 geometry_list_named_selections 的 sim_impl.call_tool 邏輯。"""
    from ansys_unified_mcp.products.geometry.tools import geometry_named_selections_resource

    fake_content = type("FakeContent", (), {"text": '{"ok": true, "named_selections": ["NS_Fixed"]}'})()
    with patch(
        "ansys_unified_mcp.products.geometry.tools.sim_impl.call_tool",
        new=AsyncMock(return_value=[fake_content]),
    ) as mock_call_tool:
        result = run_async(geometry_named_selections_resource())

    mock_call_tool.assert_called_once_with("geometry_list_named_selections", {})
    assert result == '{"ok": true, "named_selections": ["NS_Fixed"]}'
