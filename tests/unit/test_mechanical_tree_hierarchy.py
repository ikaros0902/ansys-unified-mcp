# -*- coding: utf-8 -*-
"""Mechanical DataModel Tree 查詢單元測試。"""

import json
from unittest.mock import patch, MagicMock

import pytest
from ansys_unified_mcp.products.mechanical.api import get_model_tree_hierarchy
from ansys_unified_mcp.products.mechanical.tools import mechanical_get_tree_hierarchy


def test_mechanical_tree_disconnected():
    """驗證在未連線 Mechanical 時回傳標準連線錯誤。"""
    with patch("ansys_unified_mcp.products.mechanical.api._check_connection", return_value={"ok": False, "error": "Not connected"}):
        res = get_model_tree_hierarchy()
        assert res["ok"] is False
        assert "Not connected" in res["error"]


def test_mechanical_tree_success():
    """驗證連線狀態下正確回傳並解析樹狀結構 JSON。"""
    mock_tree = {
        "ok": True,
        "tree": {
            "name": "Model",
            "category": "Model",
            "state": "FullyDefined",
            "suppressed": False,
            "children": [
                {
                    "name": "Geometry",
                    "category": "Geometry",
                    "state": "FullyDefined",
                    "suppressed": False,
                    "children": []
                }
            ]
        }
    }
    with patch("ansys_unified_mcp.products.mechanical.api._check_connection", return_value=None), \
         patch("ansys_unified_mcp.products.mechanical.api._run", return_value=json.dumps(mock_tree)):
        res = get_model_tree_hierarchy(max_depth=3)
        assert res["ok"] is True
        assert res["tree"]["name"] == "Model"
        assert len(res["tree"]["children"]) == 1


def test_mechanical_tree_tool_envelope():
    """驗證 MCP 工具層 mechanical_get_tree_hierarchy 信封封裝。"""
    mock_tree = {
        "ok": True,
        "tree": {"name": "Model", "children": []}
    }
    with patch("ansys_unified_mcp.products.mechanical.api._check_connection", return_value=None), \
         patch("ansys_unified_mcp.products.mechanical.api._run", return_value=json.dumps(mock_tree)):
        envelope = mechanical_get_tree_hierarchy(max_depth=2)
        assert envelope["ok"] is True
        assert envelope["tree"]["name"] == "Model"
