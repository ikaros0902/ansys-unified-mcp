"""Smoke tests for the Mechanical controller (products/mechanical.py).

Guards the SessionRegistry-based session lifecycle and the run_script()
timeout wrapper (core/timeout.py). A fake session is injected directly into
the registry so these tests run without ansys-mechanical-core or a live
Mechanical instance.

The fake session's ``run_python_script`` actually executes the wrapper script
with the real Python ``exec`` (the wrapper controller.run_script() builds is
plain CPython-compatible code — it only uses sys.stdout capture, io.open, and
exec — so this exercises the real temp-file round trip without needing
IronPython or a live Mechanical process).
"""

from __future__ import annotations

import time

import pytest

from ansys_unified_mcp.core.sessions import registry
from ansys_unified_mcp.products.mechanical import MechanicalController, PRODUCT


class FakeMechanicalSession:
    """Stand-in for a PyMechanical session bound via mech.connect_to_mechanical()."""

    def __init__(self, sleep_seconds: float = 0.0):
        self.version = "2026 R1"
        self.sleep_seconds = sleep_seconds
        self.scripts_run: list[str] = []

    def run_python_script(self, script: str):
        self.scripts_run.append(script)
        if self.sleep_seconds and script != "pass":
            time.sleep(self.sleep_seconds)
        # The wrapper is plain-Python compatible; actually executing it
        # reproduces what a real Mechanical/IronPython host would do (write
        # captured stdout to the temp out_file).
        exec(script, {})  # noqa: S102 - trusted, test-only fixture script


@pytest.fixture
def controller():
    for key in list(registry.keys(PRODUCT)):
        registry.drop(PRODUCT, key)
    yield MechanicalController()
    for key in list(registry.keys(PRODUCT)):
        registry.drop(PRODUCT, key)


def test_not_connected_paths(controller):
    assert controller.is_connected() is False
    assert controller.status() == {"connected": False, "sessions": [], "current": None}

    result = controller.run_script("print(1)")
    assert result == "Error: Not connected to Mechanical (session lost or closed)."

    result = controller.disconnect()
    assert result == {"ok": True, "note": "No such session."}


def test_run_script_success_via_registry(controller):
    fake = FakeMechanicalSession()
    registry.put(PRODUCT, "10000", fake)

    assert controller.is_connected() is True
    assert controller.status()["sessions"] == ["10000"]

    out = controller.run_script('print("hello from mechanical")', key="10000")
    assert out == "hello from mechanical"
    assert len(fake.scripts_run) == 2  # 1 probe + 1 actual script


def test_run_script_timeout_returns_error_promptly(controller):
    """A hung underlying call must not block the caller past the timeout budget."""
    fake = FakeMechanicalSession(sleep_seconds=0.3)
    registry.put(PRODUCT, "10000", fake)

    started = time.monotonic()
    out = controller.run_script("print('slow')", key="10000", timeout=0.05)
    elapsed = time.monotonic() - started

    assert out.startswith("Error:")
    assert "timeout" in out.lower()
    # The caller must get control back close to the timeout budget, not after
    # the full 0.3s the underlying call actually takes.
    assert elapsed < 0.3


def test_disconnect_drops_session(controller):
    fake = FakeMechanicalSession()
    registry.put(PRODUCT, "10000", fake)

    result = controller.disconnect(key="10000")
    assert result == {"ok": True, "message": "Disconnected."}
    assert controller.is_connected(key="10000") is False


def test_connect_without_package_reports_clean_error(controller, monkeypatch):
    """When ansys-mechanical-core is not importable, connect() must not raise."""
    import builtins

    real_import = builtins.__import__

    def _blocked_import(name, *args, **kwargs):
        if name == "ansys.mechanical.core":
            raise ImportError("simulated: ansys-mechanical-core not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked_import)

    result = controller.connect(port=10000)
    assert result == {"ok": False, "error": "ansys-mechanical-core not installed."}
