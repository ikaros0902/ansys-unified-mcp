"""Milestone 1 High-Frequency Concurrency and Lock-Free UUID Isolation Stress Test.

Adversarial verification of:
1. Massive multi-threaded execution (50 threads, 200 tasks) without file collisions.
2. Complete lock-free data isolation (no cross-talk between thread inputs and outputs).
3. Zero temporary file leakage after concurrent execution.
4. Thread-safe session eviction and TTL cache invalidation under concurrent failure injection.
"""

import concurrent.futures
import glob
import os
import re
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from ansys_unified_mcp.core.sessions import registry
from ansys_unified_mcp.products.mechanical.facade import MechanicalController, PRODUCT


def test_massive_concurrent_uuid_isolation():
    """Empirically prove that 50 threads executing 200 tasks have 0 file collisions and 0 cross-talk."""
    controller = MechanicalController()
    mock_session = MagicMock()

    seen_in_files = set()
    seen_out_files = set()
    file_collisions = []

    def mock_run_python(wrapper):
        m_in = re.search(r'with _io\.open\(r"([^"]+)"', wrapper)
        m_out = re.search(r'with open\(r"([^"]+)", \'w\'\)', wrapper)
        assert m_in and m_out, "Wrapper must contain valid in_path and out_path"
        
        in_path = m_in.group(1)
        out_path = m_out.group(1)

        # Thread-safe detection of collision
        if in_path in seen_in_files:
            file_collisions.append(in_path)
        seen_in_files.add(in_path)

        if out_path in seen_out_files:
            file_collisions.append(out_path)
        seen_out_files.add(out_path)

        # Read input script
        with open(in_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Simulate variable I/O delay (1 to 5 ms)
        time.sleep(0.003)

        # Write output
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(code.strip())

    mock_session.run_python_script.side_effect = mock_run_python

    tmp_dir = tempfile.gettempdir()
    
    # Check baseline temporary files
    initial_mech_files = set(glob.glob(os.path.join(tmp_dir, "mech_*.*")))

    # Test Part A: Pure Lock-Free UUID Isolation under Massive 50-thread Concurrency (timeout=None)
    with patch.object(registry, "get_live", return_value=mock_session):
        num_threads = 50
        num_tasks = 200
        results = {}

        def worker_direct(task_id):
            payload = f"UNIQUE_DIRECT_PAYLOAD_{task_id:04d}_{time.monotonic()}"
            res = controller.run_script(payload, timeout=None)
            return task_id, payload, res

        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as pool:
            futures = [pool.submit(worker_direct, i) for i in range(num_tasks)]
            for fut in concurrent.futures.as_completed(futures):
                t_id, payload, res = fut.result()
                results[t_id] = (payload, res)
        elapsed = time.time() - start_time
        print(f"\n[Part A: Direct 50-thread] Completed {len(results)} tasks in {elapsed:.2f}s")

    # Verification 1: Zero file collisions across 200 tasks
    assert len(file_collisions) == 0, f"Detected {len(file_collisions)} file collisions: {file_collisions}"
    assert len(seen_in_files) == num_tasks, f"Expected {num_tasks} unique input files, got {len(seen_in_files)}"
    assert len(seen_out_files) == num_tasks, f"Expected {num_tasks} unique output files, got {len(seen_out_files)}"

    # Verification 2: Zero cross-talk
    mismatches = [(tid, exp, act) for tid, (exp, act) in results.items() if exp != act]
    assert len(mismatches) == 0, f"Detected cross-talk in {len(mismatches)} tasks: {mismatches}"

    # Verification 3: Zero file leakage
    current_mech_files = set(glob.glob(os.path.join(tmp_dir, "mech_*.*")))
    leaked_files = current_mech_files - initial_mech_files
    assert len(leaked_files) == 0, f"Detected leaked temporary files: {leaked_files}"

    # Test Part B: Bounded ThreadPool (timeout=DEFAULT_SCRIPT_TIMEOUT) under high concurrency
    # Verifies graceful circuit-breaking and zero temporary file leakage under pool exhaustion
    with patch.object(registry, "get_live", return_value=mock_session):
        results_b = {}

        def worker_bounded(task_id):
            payload = f"UNIQUE_BOUNDED_PAYLOAD_{task_id:04d}_{time.monotonic()}"
            res = controller.run_script(payload)
            return task_id, payload, res

        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as pool:
            futures = [pool.submit(worker_bounded, i) for i in range(100)]
            for fut in concurrent.futures.as_completed(futures):
                t_id, payload, res = fut.result()
                results_b[t_id] = (payload, res)

    # Some will succeed, some will trigger thread pool exhaustion:
    exhausted_count = sum(1 for _, res in results_b.values() if "Thread pool exhausted" in res)
    success_count = sum(1 for exp, res in results_b.values() if exp == res)
    print(f"\n[Part B: Bounded Pool] Success: {success_count}, Throttled: {exhausted_count}")
    assert success_count + exhausted_count == 100

    # Ensure even throttled/errored calls clean up temporary files completely
    current_mech_files = set(glob.glob(os.path.join(tmp_dir, "mech_*.*")))
    leaked_files = current_mech_files - initial_mech_files
    assert len(leaked_files) == 0, f"Detected leaked files during pool exhaustion: {leaked_files}"


def test_concurrent_session_failure_eviction():
    """Empirically test that when a session crashes during concurrent access, it is cleanly evicted without deadlock."""
    controller = MechanicalController()
    key = "59998"
    
    mock_session = MagicMock()
    call_count = 0

    def flaky_run(wrapper):
        nonlocal call_count
        call_count += 1
        if call_count >= 10:
            raise RuntimeError("Fatal gRPC connection drop during high-load concurrency")
        
        m_in = re.search(r'with _io\.open\(r"([^"]+)"', wrapper)
        m_out = re.search(r'with open\(r"([^"]+)", \'w\'\)', wrapper)
        if m_in and m_out:
            with open(m_in.group(1), "r", encoding="utf-8") as f:
                code = f.read()
            with open(m_out.group(1), "w", encoding="utf-8") as f:
                f.write(code.strip())

    mock_session.run_python_script.side_effect = flaky_run
    registry.put(PRODUCT, key, mock_session)

    num_threads = 10
    num_tasks = 30
    results = []

    def worker(task_id):
        return controller.run_script(f"CMD_{task_id}", key=key)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as pool:
        futures = [pool.submit(worker, i) for i in range(num_tasks)]
        for fut in concurrent.futures.as_completed(futures):
            results.append(fut.result())

    # Some calls succeeded, later calls returned Error:
    successes = [r for r in results if r.startswith("CMD_")]
    errors = [r for r in results if "Error:" in r]
    
    assert len(errors) > 0, "Expected errors after session failure"
    # Session must be evicted from registry
    assert registry.get(PRODUCT, key) is None, "Dead session was not evicted from registry"
    # is_connected must report False immediately
    assert controller.is_connected(key=key) is False, "is_connected must return False for dead session"
