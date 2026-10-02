"""Unit tests for ansys_unified_mcp.connection.session_manager.AnsSessionManager.

純測試委派邏輯是否正確路由至對應產品的 controller，不測試各 controller 內部連線細節
（那些已由 tests/test_mechanical_controller.py、tests/test_optislang_controller.py 等覆蓋）。
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ansys_unified_mcp.connection.session_manager import AnsSessionManager


@pytest.fixture
def manager():
    return AnsSessionManager()


def test_connect_dispatches_to_mechanical_controller(manager):
    """connect(product='mechanical', ...) 應委派至 MechanicalController.connect，並透傳參數。"""
    mock_controller = MagicMock()
    mock_controller.connect.return_value = {"ok": True, "port": 10000, "pid": 123}
    with patch("ansys_unified_mcp.products.mechanical.facade.controller", mock_controller):
        result = manager.connect("mechanical", port=10000, pid=456)

    mock_controller.connect.assert_called_once_with(port=10000, pid=456)
    assert result == {"ok": True, "port": 10000, "pid": 123}


def test_connect_dispatches_to_optislang_controller(manager):
    """connect(product='optislang', ...) 應委派至 OptislangController.connect。"""
    mock_controller = MagicMock()
    mock_controller.connect.return_value = {"ok": True, "version": "2026 R1"}
    with patch("ansys_unified_mcp.products.optislang.facade.controller", mock_controller):
        result = manager.connect("optislang", project_path="my_project.opf")

    mock_controller.connect.assert_called_once_with(project_path="my_project.opf")
    assert result == {"ok": True, "version": "2026 R1"}


def test_connect_geometry_and_fluent_dispatch_to_launch(manager):
    """geometry/fluent 無獨立 connect，connect() 應委派至對應 controller 的 launch()。"""
    mock_geo = MagicMock()
    mock_geo.launch.return_value = {"ok": True, "port": 50051, "pid": 789}
    with patch("ansys_unified_mcp.products.geometry.facade.controller", mock_geo):
        result = manager.connect("geometry", port=50051)
    mock_geo.launch.assert_called_once_with(port=50051)
    assert result == {"ok": True, "port": 50051, "pid": 789}

    mock_fluent = MagicMock()
    mock_fluent.launch.return_value = {"ok": True, "port": 50052}
    with patch("ansys_unified_mcp.products.fluent.facade.controller", mock_fluent):
        result = manager.connect("fluent", port=50052)
    mock_fluent.launch.assert_called_once_with(port=50052)
    assert result == {"ok": True, "port": 50052}


def test_launch_dispatches_to_mechanical_controller(manager):
    """launch(product='mechanical', ...) 應委派至 MechanicalController.launch。"""
    mock_controller = MagicMock()
    mock_controller.launch.return_value = {"ok": True, "key": "launched"}
    with patch("ansys_unified_mcp.products.mechanical.facade.controller", mock_controller):
        result = manager.launch("mechanical", batch=True)

    mock_controller.launch.assert_called_once_with(batch=True)
    assert result == {"ok": True, "key": "launched"}


def test_launch_optislang_dispatches_to_connect(manager):
    """optiSLang 無獨立 launch，launch() 應委派至其 connect()（進程啟動與連線同一步）。"""
    mock_controller = MagicMock()
    mock_controller.connect.return_value = {"ok": True, "version": "2026 R1"}
    with patch("ansys_unified_mcp.products.optislang.facade.controller", mock_controller):
        result = manager.launch("optislang", project_path="")

    mock_controller.connect.assert_called_once_with(project_path="")
    assert result == {"ok": True, "version": "2026 R1"}


def test_status_dispatches_per_product(manager):
    """status() 應依 product 委派至對應 controller 的 status()。"""
    mock_controller = MagicMock()
    mock_controller.status.return_value = {"connected": True}
    with patch("ansys_unified_mcp.products.optislang.facade.controller", mock_controller):
        result = manager.status("optislang")
    mock_controller.status.assert_called_once_with()
    assert result == {"connected": True}


def test_disconnect_dispatches_to_correct_method_name_per_product(manager):
    """disconnect() 需對應各產品不同的中斷連線方法名稱（disconnect/close/exit）。"""
    mock_geo = MagicMock()
    mock_geo.close.return_value = {"ok": True, "message": "Geometry session closed."}
    with patch("ansys_unified_mcp.products.geometry.facade.controller", mock_geo):
        result = manager.disconnect("geometry")
    mock_geo.close.assert_called_once_with()
    assert result == {"ok": True, "message": "Geometry session closed."}

    mock_fluent = MagicMock()
    mock_fluent.exit.return_value = {"ok": True, "message": "Fluent session terminated."}
    with patch("ansys_unified_mcp.products.fluent.facade.controller", mock_fluent):
        result = manager.disconnect("fluent")
    mock_fluent.exit.assert_called_once_with()
    assert result == {"ok": True, "message": "Fluent session terminated."}


def test_unsupported_product_returns_error_envelope(manager):
    """未知產品名稱應回傳標準失敗信封，而非拋出例外或 KeyError。"""
    for method in (manager.connect, manager.launch, manager.status, manager.disconnect):
        result = method("unknown_product")
        assert result["ok"] is False
        assert "不支援" in result["error"]
