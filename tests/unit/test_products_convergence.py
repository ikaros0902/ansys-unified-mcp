"""Unit tests for Phase 2 controller convergence (Fluent & Geometry)."""

import pytest
from ansys_unified_mcp.core.sessions import registry
from ansys_unified_mcp.products.fluent import controller as fluent_controller, PRODUCT as FLUENT_PRODUCT
from ansys_unified_mcp.products.geometry import controller as geometry_controller, PRODUCT as GEOM_PRODUCT


class FakeFluentSession:
    def __init__(self, version="24.2.0"):
        self.version = version
        self.exited = False

    def get_fluent_version(self):
        return self.version

    def exit(self):
        self.exited = True


class FakeModeler:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_fluent_controller_lifecycle():
    fake = FakeFluentSession()
    assert fluent_controller.is_connected() is False

    # Simulate session registration
    registry.put(FLUENT_PRODUCT, "default", fake)
    assert fluent_controller.is_connected() is True
    status = fluent_controller.status()
    assert status["ok"] is True
    assert status["connected"] is True

    # Exit session
    res = fluent_controller.exit()
    assert res["ok"] is True
    assert fake.exited is True
    assert fluent_controller.is_connected() is False


def test_geometry_controller_lifecycle():
    fake = FakeModeler()
    assert geometry_controller.is_connected() is False

    # Simulate session registration
    registry.put(GEOM_PRODUCT, "default", fake)
    assert geometry_controller.is_connected() is True
    status = geometry_controller.status()
    assert status["ok"] is True
    assert status["connected"] is True

    # Close session
    res = geometry_controller.close()
    assert res["ok"] is True
    assert fake.closed is True
    assert geometry_controller.is_connected() is False
