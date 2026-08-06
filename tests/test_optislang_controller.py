"""Smoke tests for the optiSLang controller (products/optislang.py).

Guards the refactor that moved optiSLang's session from a module-global into
the shared SessionRegistry. A fake session is injected directly into the
registry so these tests run without ansys-optislang-core or a live optiSLang.
"""

import pytest

from ansys_unified_mcp.core.sessions import registry
from ansys_unified_mcp.products.optislang import OptislangController, PRODUCT, KEY


class FakeOsl:
    """Minimal stand-in for an ansys.optislang.core.Optislang session."""

    def __init__(self):
        self.osl_version_string = "2026 R1"  # attribute form (not callable)
        self.started = False
        self.disposed = False

    def run_python_script(self, script):
        return f"ran:{script}"

    def start(self):
        self.started = True

    def dispose(self):
        self.disposed = True


@pytest.fixture
def controller():
    registry.drop(PRODUCT, KEY)  # ensure clean shared-singleton state
    yield OptislangController()
    registry.drop(PRODUCT, KEY)  # cleanup so tests do not contaminate each other


def test_not_connected_paths(controller):
    assert controller.is_connected() is False
    assert controller.status() == {"connected": False}
    assert controller.version_string() == "unknown"

    r = controller.run_script("print(1)")
    assert r["ok"] is False and "尚未連線" in r["error"]

    r = controller.start_project()
    assert r["ok"] is False and "尚未連線" in r["error"]

    r = controller.disconnect()  # no-op when nothing is connected
    assert r["ok"] is True and "本來就未連線" in r["note"]


def test_connected_via_registry(controller):
    fake = FakeOsl()
    registry.put(PRODUCT, KEY, fake)

    assert controller.is_connected() is True
    assert controller.status() == {"connected": True}
    assert controller.version_string() == "2026 R1"

    r = controller.run_script("do()")
    assert r["ok"] is True and r["output"] == "ran:do()"

    r = controller.run_script("   ")  # empty/whitespace rejected
    assert r["ok"] is False and "script 不得為空" in r["error"]

    r = controller.start_project()
    assert r["ok"] is True and fake.started is True


def test_disconnect_disposes_and_drops(controller):
    fake = FakeOsl()
    registry.put(PRODUCT, KEY, fake)

    r = controller.disconnect(shutdown=True)
    assert r["ok"] is True
    assert fake.disposed is True
    assert controller.is_connected() is False
    assert registry.get(PRODUCT, KEY) is None


def test_run_script_surfaces_exception(controller):
    class Boom:
        def run_python_script(self, script):
            raise RuntimeError("boom")

    registry.put(PRODUCT, KEY, Boom())
    r = controller.run_script("x")
    assert r["ok"] is False and "腳本執行失敗" in r["error"]
