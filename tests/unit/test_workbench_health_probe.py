"""Unit tests for WorkbenchController health probe, TTL cache, and timeout eviction.

Tests:
1. Normal healthy session probe succeeds and respects _PROBE_TTL cache.
2. Dead session probe fails -> is_connected() returns False and session is evicted from registry.
3. BlockingCallTimeout in run_script drops the poisoned session from registry and clears cache.
4. Subsequent calls after timeout do not reuse the poisoned session.
5. BlockingCallTimeout in run_script_file drops the poisoned session from registry.
6. Script guard integration in run_script and run_script_file.
7. Multi-instance probe isolation (evicting one session does not drop another).
"""

from __future__ import annotations

import os
import time
from unittest.mock import patch

import pytest

from ansys_unified_mcp.core.sessions import registry
from ansys_unified_mcp.products.workbench import WorkbenchController, PRODUCT, _PROBE_CACHE, _PROBE_TTL


class FakeWorkbenchClient:
    """Mock PyWorkbench WorkbenchClient for unit testing health probes and timeouts."""

    def __init__(self, port=None, server_version="2026 R1", sleep_seconds: float = 0.0):
        self._port = port
        self.server_version = server_version
        self.sleep_seconds = sleep_seconds
        self.run_script_string_calls: list[tuple[str, str]] = []
        self.run_script_file_calls: list[tuple[str, str]] = []

    def run_script_string(self, script: str, log_level: str = "error") -> str:
        self.run_script_string_calls.append((script, log_level))
        if self.sleep_seconds and script != "pass":
            time.sleep(self.sleep_seconds)
        return f"result:{script}"

    def run_script_file(self, script_file_name: str, log_level: str = "error") -> str:
        self.run_script_file_calls.append((script_file_name, log_level))
        if self.sleep_seconds:
            time.sleep(self.sleep_seconds)
        return f"fileresult:{script_file_name}"


@pytest.fixture
def controller():
    """Provides a clean WorkbenchController and resets registry & probe cache."""
    for key in list(registry.keys(PRODUCT)):
        registry.drop(PRODUCT, key)
    WorkbenchController._PROBE_CACHE.clear()
    ctrl = WorkbenchController()
    yield ctrl
    for key in list(registry.keys(PRODUCT)):
        registry.drop(PRODUCT, key)
    WorkbenchController._PROBE_CACHE.clear()


def test_healthy_session_probe_and_ttl_cache(controller):
    """Test that a healthy session succeeds probe and caches result within TTL window."""
    fake = FakeWorkbenchClient(port=5000)
    registry.put(PRODUCT, "5000", fake)

    # First call must invoke run_script_string("pass")
    assert controller.is_connected("5000") is True
    assert fake.run_script_string_calls == [("pass", "error")]
    client_key = str(id(fake))
    assert client_key in WorkbenchController._PROBE_CACHE

    # Immediate second and third calls must hit probe cache
    assert controller.is_connected("5000") is True
    assert controller._client("5000") is fake
    assert len(fake.run_script_string_calls) == 1

    # Fast-forward time past _PROBE_TTL (10s)
    with patch("time.monotonic", return_value=time.monotonic() + 15.0):
        assert controller.is_connected("5000") is True
        assert len(fake.run_script_string_calls) == 2
        assert fake.run_script_string_calls[1] == ("pass", "error")


def test_dead_session_probe_drops_and_is_connected_false(controller):
    """Test that a dead session probe failure results in session eviction and is_connected == False."""
    class _DeadClient(FakeWorkbenchClient):
        def run_script_string(self, script: str, log_level: str = "error") -> str:
            raise ConnectionResetError("gRPC connection closed by remote peer")

    dead = _DeadClient(port=5001)
    registry.put(PRODUCT, "5001", dead)

    # is_connected checks _client() with probe -> probe fails -> evicts session
    assert controller.is_connected("5001") is False
    assert registry.get(PRODUCT, "5001") is None
    assert controller._client("5001") is None
    assert str(id(dead)) not in WorkbenchController._PROBE_CACHE


def test_blocking_call_timeout_in_run_script_drops_poisoned_session(controller):
    """Test that BlockingCallTimeout in run_script evicts poisoned session from registry and cache."""
    slow_client = FakeWorkbenchClient(port=5002, sleep_seconds=0.5)
    registry.put(PRODUCT, "5002", slow_client)

    started = time.monotonic()
    out = controller.run_script("do_expensive_work()", key="5002", timeout=0.05)
    elapsed = time.monotonic() - started

    assert out.startswith("Error:")
    assert "timeout" in out.lower()
    assert "evicted from registry" in out
    assert elapsed < 0.5

    # Poisoned session must be gone from registry
    assert registry.get(PRODUCT, "5002") is None
    assert controller.is_connected("5002") is False
    assert str(id(slow_client)) not in WorkbenchController._PROBE_CACHE


def test_subsequent_calls_do_not_reuse_poisoned_session(controller):
    """Test that after a timeout eviction, subsequent calls do not reuse the poisoned session."""
    slow_client = FakeWorkbenchClient(port=5003, sleep_seconds=0.5)
    registry.put(PRODUCT, "5003", slow_client)

    # Trigger timeout
    out = controller.run_script("hang()", key="5003", timeout=0.05)
    assert "evicted from registry" in out

    # Clear recorded calls on fake
    slow_client.run_script_string_calls.clear()

    # Second call must immediately return Not connected without blocking or hitting slow_client
    out2 = controller.run_script("healthy_script()", key="5003")
    assert out2 == "Error: Not connected to Workbench."
    assert len(slow_client.run_script_string_calls) == 0


def test_blocking_call_timeout_in_run_script_file_drops_poisoned_session(controller):
    """Test that BlockingCallTimeout in run_script_file evicts poisoned session from registry."""
    class _SlowFileClient(FakeWorkbenchClient):
        def run_script_file(self, script_file_name: str, log_level: str = "error") -> str:
            time.sleep(0.5)
            return f"fileresult:{script_file_name}"

    slow_client = _SlowFileClient(port=5004)
    registry.put(PRODUCT, "5004", slow_client)

    started = time.monotonic()
    out = controller.run_script_file("slow.wbjn", key="5004", timeout=0.05)
    elapsed = time.monotonic() - started

    assert out.startswith("Error:")
    assert "timeout" in out.lower()
    assert "evicted from registry" in out
    assert elapsed < 0.5
    assert registry.get(PRODUCT, "5004") is None
    assert controller.is_connected("5004") is False


def test_check_script_guard_blocks_malicious_script(controller, monkeypatch):
    """Test that run_script and run_script_file invoke check_script guard."""
    monkeypatch.setattr("ansys_unified_mcp.core.script_guard._MODE", "strict")

    fake = FakeWorkbenchClient(port=5005)
    registry.put(PRODUCT, "5005", fake)

    # Malicious script with dangerous import
    malicious_script = "import subprocess\nsubprocess.call(['calc'])"
    out = controller.run_script(malicious_script, key="5005")

    assert out.startswith("Error: Script blocked by security guard:")
    assert "subprocess" in out
    # Client should not have executed the malicious script
    assert ("subprocess.call(['calc'])", "error") not in fake.run_script_string_calls


def test_multi_instance_probe_isolation(controller):
    """Test that dropping a poisoned session on one port leaves sessions on other ports intact."""
    healthy_client = FakeWorkbenchClient(port=6001)
    slow_client = FakeWorkbenchClient(port=6002, sleep_seconds=0.5)

    registry.put(PRODUCT, "6001", healthy_client)
    registry.put(PRODUCT, "6002", slow_client)

    # Evict 6002 via timeout
    out = controller.run_script("hang()", key="6002", timeout=0.05)
    assert "evicted from registry" in out

    # 6002 must be evicted
    assert registry.get(PRODUCT, "6002") is None
    assert controller.is_connected("6002") is False

    # 6001 must remain live and functional
    assert registry.get(PRODUCT, "6001") is healthy_client
    assert controller.is_connected("6001") is True
    res = controller.run_script("wb_script_result = 99", key="6001")
    assert res == "result:wb_script_result = 99"


def test_check_script_guard_blocks_malicious_script_file(controller, monkeypatch, tmp_path):
    """Test that run_script_file inspects file contents with script guard."""
    monkeypatch.setattr("ansys_unified_mcp.core.script_guard._MODE", "strict")

    fake = FakeWorkbenchClient(port=5006)
    registry.put(PRODUCT, "5006", fake)

    bad_file = tmp_path / "bad_journal.wbjn"
    bad_file.write_text("import shutil\nshutil.rmtree('/tmp')", encoding="utf-8")

    out = controller.run_script_file(str(bad_file), key="5006")
    assert out.startswith("Error: Script blocked by security guard:")
    assert "shutil" in out
    assert len(fake.run_script_file_calls) == 0
