"""Milestone 1 Empirical Stress Test: Concurrency and Reconnection.

Adversarial Verification Suite for:
1. High-frequency concurrent calls to MechanicalController.run_script (race conditions, file collisions).
2. Session error injection and reconnection behavior when session drops.
"""

import concurrent.futures
import time
from unittest.mock import MagicMock, patch

import pytest
from ansys_unified_mcp.core.sessions import registry
from ansys_unified_mcp.products.mechanical.facade import MechanicalController, PRODUCT


def test_concurrent_run_script_file_collision():
    """Empirically test whether concurrent run_script calls collide on the same temporary files."""
    controller = MechanicalController()
    mock_session = MagicMock()

    # Simulate realistic execution where session reads script_file and writes out_file
    def fake_run_python_script(wrapper):
        # Extract script_file path from wrapper
        # The wrapper reads from script_file and writes to out_file
        # We simulate gRPC / IronPython execution delay of 20ms
        import re
        import os
        m_in = re.search(r'with _io\.open\(r"([^"]+)"', wrapper)
        m_out = re.search(r'with open\(r"([^"]+)", \'w\'\)', wrapper)
        if m_in and m_out:
            in_path = m_in.group(1)
            out_path = m_out.group(1)
            with open(in_path, "r", encoding="utf-8") as f:
                code = f.read()
            time.sleep(0.02)
            with open(out_path, "w", encoding="utf-8") as f:
                # If script was "print('ID_X')", write "ID_X"
                f.write(code.strip())

    mock_session.run_python_script.side_effect = fake_run_python_script

    with patch.object(registry, "get_live", return_value=mock_session):
        num_workers = 5
        results = {}

        def worker_task(task_id):
            expected = f"OUTPUT_FROM_TASK_{task_id}"
            script = expected
            res = controller.run_script(script)
            return task_id, expected, res

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker_task, i) for i in range(num_workers)]
            for fut in concurrent.futures.as_completed(futures):
                t_id, expected, res = fut.result()
                results[t_id] = (expected, res)

        print("\nConcurrent run_script results:")
        mismatches = []
        for t_id, (expected, res) in results.items():
            print(f"Task {t_id}: expected={expected!r}, actual={res!r}")
            if expected != res:
                mismatches.append((t_id, expected, res))

        assert len(mismatches) == 0, f"Concurrent run_script suffered from cross-talk/file collision! Mismatches: {mismatches}"


def test_reconnect_when_session_dead():
    """Empirically test whether connect() properly detects a dead session and reconnects."""
    controller = MechanicalController()
    key = "59999"

    # Put a dead mock session into registry
    dead_session = MagicMock()
    # Dead session raises on any gRPC call
    dead_session.run_python_script.side_effect = RuntimeError("gRPC connection broken")
    registry.put(PRODUCT, key, dead_session)

    # Now attempt to connect() to the same port
    mock_mech_module = MagicMock()
    fresh_session = MagicMock()
    fresh_session.run_python_script.return_value = "Connected! Analyses: 1"
    mock_mech_module.connect_to_mechanical.return_value = fresh_session

    import types
    ansys_pkg = types.ModuleType("ansys")
    mech_pkg = types.ModuleType("ansys.mechanical")
    mech_core_pkg = mock_mech_module
    ansys_pkg.mechanical = mech_pkg
    mech_pkg.core = mech_core_pkg

    with patch.dict("sys.modules", {
        "ansys": ansys_pkg,
        "ansys.mechanical": mech_pkg,
        "ansys.mechanical.core": mock_mech_module,
    }), patch.object(controller, "run_script", return_value="Connected OK"):
        res = controller.connect(port=59999)

        print(f"\nConnect result with dead session in registry: {res}")
        # If connect reused the dead session instead of establishing a fresh connection:
        if res.get("note") == "Reused existing session.":
            pytest.fail("VULNERABILITY CONFIRMED: connect() blindly reused a dead session from registry without checking liveness!")


def test_session_exception_does_not_evict_dead_session():
    """Empirically test whether run_script cleans up the session registry when gRPC raises connection errors."""
    controller = MechanicalController()
    key = "59999"

    mock_session = MagicMock()
    mock_session.run_python_script.side_effect = RuntimeError("gRPC connection reset by peer")
    registry.put(PRODUCT, key, mock_session)

    # Calling run_script raises internally, returns error string
    res = controller.run_script("print(1)", key=key)
    print(f"\nrun_script returned: {res}")

    # Check whether dead session was dropped from registry
    cached_session = registry.get(PRODUCT, key)
    print(f"Session in registry after fatal gRPC error: {cached_session}")
    if cached_session is not None:
        pytest.fail("VULNERABILITY CONFIRMED: Fatal gRPC error during run_script did NOT evict the dead session from registry!")


def test_session_dies_during_run_script_not_evicted_due_to_ttl_cache():
    """Empirically test whether a session that fails during script execution is evicted or kept alive by TTL cache."""
    controller = MechanicalController()
    key = "59999"

    mock_session = MagicMock()
    # First call ('pass' during probe) succeeds
    # Second call (wrapper during run_script) crashes with connection broken
    def script_side_effect(code):
        if code == "pass":
            return "ok"
        raise RuntimeError("gRPC connection broken during execution")

    mock_session.run_python_script.side_effect = script_side_effect
    registry.put(PRODUCT, key, mock_session)

    # First probe passes and caches TTL for 10s
    res = controller.run_script("print(1)", key=key)
    print(f"\nFirst run_script result: {res}")
    assert "Error:" in res

    # 驗證死 Session 是否已正確自 registry 驅逐
    cached_session = registry.get(PRODUCT, key)
    print(f"Session still in registry: {cached_session}")
    assert cached_session is None, f"Dead session was NOT evicted from registry: {cached_session}"

    # 驗證 is_connected() 立即回傳 False，不再因 TTL 快取而產生假陽性
    is_conn = controller.is_connected(key=key)
    print(f"is_connected() reported: {is_conn}")
    assert is_conn is False, "is_connected() falsely reported True for a dead session due to stale TTL cache!"


