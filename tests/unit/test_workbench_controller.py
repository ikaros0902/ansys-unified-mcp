"""Smoke tests for the Workbench controller (products/workbench.py).

Guards the SessionRegistry-based session lifecycle, the three-way key
resolution in launch(), and the run_script()/run_script_file() timeout
wrapper (core/timeout.py). ``ansys-workbench-core`` is not required: the
``from ansys.workbench.core import ...`` statements are intercepted via a
patched ``builtins.__import__`` so a fake module is returned instead.
"""

from __future__ import annotations

import builtins
import time

import pytest

from ansys_unified_mcp.core.sessions import registry
from ansys_unified_mcp.products.workbench import WorkbenchController, PRODUCT


class FakeWorkbenchClient:
    """Stand-in for a PyWorkbench ``WorkbenchClient``."""

    def __init__(self, port=None, server_version="2026 R1", sleep_seconds: float = 0.0):
        self._port = port
        self.server_version = server_version
        self.sleep_seconds = sleep_seconds
        self.run_script_string_calls: list[tuple[str, str]] = []
        self.uploaded: tuple[str, ...] = ()

    def run_script_string(self, script, log_level="error"):
        self.run_script_string_calls.append((script, log_level))
        if self.sleep_seconds and script != "pass":
            time.sleep(self.sleep_seconds)
        return f"result:{script}"

    def run_script_file(self, script_file_name, log_level="error"):
        return f"fileresult:{script_file_name}"

    def upload_file(self, *file_list):
        self.uploaded = file_list

    def download_project_archive(self, archive_name):
        return f"/tmp/{archive_name}"

    def start_mechanical_server(self, system_name, port=0):
        return 10001


class _FakeWorkbenchCoreModule:
    """Minimal stand-in for the ``ansys.workbench.core`` module."""

    def __init__(self, launch_workbench=None, connect_workbench=None):
        if launch_workbench is not None:
            self.launch_workbench = launch_workbench
        if connect_workbench is not None:
            self.connect_workbench = connect_workbench


@pytest.fixture
def controller():
    for key in list(registry.keys(PRODUCT)):
        registry.drop(PRODUCT, key)
    WorkbenchController._PROBE_CACHE.clear()
    yield WorkbenchController()
    for key in list(registry.keys(PRODUCT)):
        registry.drop(PRODUCT, key)
    WorkbenchController._PROBE_CACHE.clear()


@pytest.fixture
def fake_workbench_core(monkeypatch):
    """Intercepts ``from ansys.workbench.core import ...`` without the real package."""
    state: dict = {}
    real_import = builtins.__import__

    def _fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "ansys.workbench.core" and fromlist:
            return state["module"]
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _fake_import)

    def _set(module: _FakeWorkbenchCoreModule) -> None:
        state["module"] = module

    return _set


def test_not_connected_paths(controller):
    assert controller.is_connected() is False
    assert controller.status() == {"connected": False, "sessions": [], "current": None}

    assert controller.run_script("print(1)") == "Error: Not connected to Workbench."
    assert controller.run_script_file("probe.wbjn") == "Error: Not connected to Workbench."
    assert controller.upload_file("a.step") == {"ok": False, "error": "Not connected to Workbench."}
    assert controller.download_project_archive("proj.wbpz") == {
        "ok": False,
        "error": "Not connected to Workbench.",
    }
    assert controller.start_mechanical_server("SYS") == {"ok": False, "error": "Not connected to Workbench."}
    assert controller.disconnect() == {"ok": True, "note": "No such session."}


@pytest.mark.parametrize(
    "client_port,launch_port_arg,expected_key",
    [
        (54321, -1, "54321"),  # resolved_port from client wins
        (None, 9000, "9000"),  # no resolved_port, falls back to explicit port arg
        (None, -1, "launched"),  # neither available -> sentinel
    ],
)
def test_launch_key_resolution(controller, fake_workbench_core, client_port, launch_port_arg, expected_key):
    fake_client = FakeWorkbenchClient(port=client_port)
    fake_workbench_core(_FakeWorkbenchCoreModule(launch_workbench=lambda **kwargs: fake_client))

    result = controller.launch(port=launch_port_arg)

    assert result["ok"] is True
    assert result["key"] == expected_key
    assert registry.get(PRODUCT, expected_key) is fake_client


def test_connect_reuses_existing_session(controller):
    existing = FakeWorkbenchClient(port=5000)
    registry.put(PRODUCT, "5000", existing)

    result = controller.connect(port=5000)
    assert result == {"ok": True, "port": 5000, "key": "5000", "note": "Reused existing session."}


def test_connect_success_registers_session(controller, fake_workbench_core):
    fake_client = FakeWorkbenchClient(port=5001)
    fake_workbench_core(_FakeWorkbenchCoreModule(connect_workbench=lambda **kwargs: fake_client))

    result = controller.connect(port=5001)
    assert result["ok"] is True
    assert result["key"] == "5001"
    assert registry.get(PRODUCT, "5001") is fake_client


def test_run_script_success_via_registry(controller):
    fake = FakeWorkbenchClient()
    registry.put(PRODUCT, "launched", fake)

    out = controller.run_script("wb_script_result = 42", key="launched")
    assert out == "result:wb_script_result = 42"
    assert ("wb_script_result = 42", "error") in fake.run_script_string_calls


def test_run_script_timeout_evicts_session_from_registry(controller):
    fake = FakeWorkbenchClient(sleep_seconds=0.5)
    registry.put(PRODUCT, "launched", fake)

    started = time.monotonic()
    out = controller.run_script("slow_script()", key="launched", timeout=0.05)
    elapsed = time.monotonic() - started

    assert out.startswith("Error:")
    assert "timeout" in out.lower()
    assert "evicted from registry" in out
    assert elapsed < 0.5
    # The stale session must be dropped so a subsequent call reports "not connected"
    # instead of reusing a session bound to a hung worker thread.
    assert registry.get(PRODUCT, "launched") is None
    assert controller.is_connected(key="launched") is False


def test_run_script_file_timeout_evicts_session_from_registry(controller):
    class _SlowFileClient(FakeWorkbenchClient):
        def run_script_file(self, script_file_name, log_level="error"):
            time.sleep(0.5)
            return f"fileresult:{script_file_name}"

    fake = _SlowFileClient()
    registry.put(PRODUCT, "launched", fake)

    started = time.monotonic()
    out = controller.run_script_file("slow.wbjn", key="launched", timeout=0.05)
    elapsed = time.monotonic() - started

    assert out.startswith("Error:")
    assert "timeout" in out.lower()
    assert "evicted from registry" in out
    assert elapsed < 0.5
    assert registry.get(PRODUCT, "launched") is None


def test_probe_session_reports_dead_client_and_evicts_it(controller):
    """A client whose run_script_string() always raises must be treated as dead."""

    class _DeadClient(FakeWorkbenchClient):
        def run_script_string(self, script, log_level="error"):
            raise ConnectionError("simulated: peer closed the connection")

    fake = _DeadClient()
    registry.put(PRODUCT, "launched", fake)

    # _client() (used by run_script/run_script_file/etc.) goes through
    # registry.get_live() with the probe, so a dead client must not be handed
    # back to a caller, and must be evicted from the registry as a side effect.
    assert controller._client(key="launched") is None
    assert registry.get(PRODUCT, "launched") is None


def test_probe_session_caches_healthy_result_within_ttl(controller):
    """A repeated probe within the TTL window must not re-invoke run_script_string."""
    fake = FakeWorkbenchClient()

    assert controller._probe_session(fake) is True
    assert controller._probe_session(fake) is True
    assert fake.run_script_string_calls == [("pass", "error")]


def test_run_script_reports_not_connected_when_probe_fails(controller):
    """run_script() must route through the same dead-session detection as _client()."""

    class _DeadClient(FakeWorkbenchClient):
        def run_script_string(self, script, log_level="error"):
            raise ConnectionError("simulated: peer closed the connection")

    fake = _DeadClient()
    registry.put(PRODUCT, "launched", fake)

    assert controller.run_script("print(1)", key="launched") == "Error: Not connected to Workbench."
    assert registry.get(PRODUCT, "launched") is None


def test_run_script_file_success(controller):
    fake = FakeWorkbenchClient()
    registry.put(PRODUCT, "launched", fake)

    out = controller.run_script_file("probe.wbjn", key="launched")
    assert out == "fileresult:probe.wbjn"


def test_upload_and_download_and_start_mechanical_server(controller):
    fake = FakeWorkbenchClient()
    registry.put(PRODUCT, "launched", fake)

    assert controller.upload_file("a.step", "b.step", key="launched") == {
        "ok": True,
        "uploaded": ["a.step", "b.step"],
    }
    assert fake.uploaded == ("a.step", "b.step")

    assert controller.download_project_archive("proj.wbpz", key="launched") == {
        "ok": True,
        "archive": "/tmp/proj.wbpz",
    }

    assert controller.start_mechanical_server("SYS", key="launched") == {
        "ok": True,
        "system_name": "SYS",
        "grpc_port": 10001,
    }


def test_disconnect_drops_session(controller):
    fake = FakeWorkbenchClient()
    registry.put(PRODUCT, "launched", fake)

    result = controller.disconnect(key="launched")
    assert result == {"ok": True, "message": "Disconnected (Workbench server left running)."}
    assert controller.is_connected(key="launched") is False


def test_launch_without_package_reports_clean_error(controller, monkeypatch):
    real_import = builtins.__import__

    def _blocked_import(name, *args, **kwargs):
        if name == "ansys.workbench.core":
            raise ImportError("simulated: ansys-workbench-core not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked_import)

    result = controller.launch()
    assert result == {"ok": False, "error": "ansys-workbench-core not installed."}


def test_run_script_reports_busy_when_session_locked(controller):
    """run_script() 必須在 record.lock 已被另一方持有時回報 busy，不等待不卡死。

    驗證 acquire_live() 補齊的序列化保護確實生效：模擬另一執行緒持鎖中
    （直接對 registry 的 record 搶鎖，模擬真實並發場景），本次呼叫必須
    立即回報 "Error: Workbench session is busy."，而不是阻塞等待或誤判
    為「探活失敗 (not connected)」。
    """
    fake = FakeWorkbenchClient()
    registry.put(PRODUCT, "launched", fake)

    held_record = registry.record(PRODUCT, "launched")
    assert held_record.lock.acquire(blocking=False) is True  # 模擬另一執行緒持鎖中
    try:
        out = controller.run_script("print(1)", key="launched")
        assert out == "Error: Workbench session is busy."
        # busy 不代表 session 被驅逐：session 本身仍應留在 registry。
        assert registry.get(PRODUCT, "launched") is fake
    finally:
        held_record.lock.release()

    # 鎖釋放後，後續呼叫必須恢復正常執行（證明 busy 路徑沒有洩漏任何狀態）。
    out2 = controller.run_script("wb_script_result = 1", key="launched")
    assert out2 == "result:wb_script_result = 1"


def test_run_script_file_reports_busy_when_session_locked(controller):
    """run_script_file() 同樣受 acquire_live() 保護，busy 時立即回報不卡死。"""
    fake = FakeWorkbenchClient()
    registry.put(PRODUCT, "launched", fake)

    held_record = registry.record(PRODUCT, "launched")
    assert held_record.lock.acquire(blocking=False) is True
    try:
        out = controller.run_script_file("probe.wbjn", key="launched")
        assert out == "Error: Workbench session is busy."
    finally:
        held_record.lock.release()
