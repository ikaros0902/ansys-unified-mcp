"""Stage 4 Unit Tests: Cross-Virtual-Environment IPC and License Scheduler.

Validates:
1. 50 MB NumPy float array zero-copy SharedMemory transfer with <50 ms latency and bit-exactness.
2. Resource cleanup and unlink safety.
3. Named pipe signaling (Echo/Ping) with automatic 64 KB overflow diversion.
4. Token bucket scheduler with Human_Buffer=1 gate and Speos/Rocky multi-feature atomic reservation.
5. 300-second license lingering cooldown on abnormal termination.
6. Windows Interactive Desktop Guard Session 0 blockage and silent flag injection.
"""

from __future__ import annotations

import os
import time
import numpy as np
import pytest

from ansys_unified_mcp.core.ipc.shared_memory_buffer import (
    SharedMemoryBuffer,
    SharedMemoryMetadata,
    cleanup_shm,
    read_shared_array,
    write_shared_array,
)
from ansys_unified_mcp.core.ipc.named_pipe_transport import (
    OVERFLOW_THRESHOLD_BYTES,
    NamedPipeMessage,
    NamedPipeTransport,
)
from ansys_unified_mcp.core.jobs.token_bucket_scheduler import (
    FeatureBalance,
    LicenseLease,
    PreflightCheckResult,
    TokenBucketLicenseScheduler,
    TokenBucketScheduler,
)
from ansys_unified_mcp.core.jobs.interactive_desktop_guard import (
    DesktopGuardError,
    InteractiveDesktopGuard,
    SessionZeroBlockedError,
    SessionZeroExecutionError,
)


# ==============================================================================
# 1. SharedMemoryBuffer Tests (50 MB Zero-Copy Transfer Benchmark)
# ==============================================================================

def test_shared_memory_50mb_transfer_speed_and_exactness():
    """Verify 50 MB NumPy float64 array transfers in <50 ms with bit-level exactness."""
    # 50 MB float64 array: 50 * 1024 * 1024 / 8 = 6,553,600 elements
    num_elements = 6_553_600
    expected_bytes = num_elements * 8

    # Generate test array
    np.random.seed(42)
    original_arr = np.random.randn(num_elements).astype(np.float64)
    assert original_arr.nbytes == expected_bytes

    shm_write_handle = None
    shm_read_handle = None
    try:
        t_start = time.perf_counter()

        # Step 1: Write to SharedMemory (Zero-copy IPC buffer allocation & copy)
        shm_write_handle, meta = write_shared_array(original_arr, name="ansys_bench_50mb", compute_sha256=False)

        # Step 2: Read from SharedMemory (Zero-copy ndarray buffer view)
        shm_read_handle, reconstructed_arr = read_shared_array(meta, copy=False, verify_sha256=False)

        t_elapsed_ms = (time.perf_counter() - t_start) * 1000.0

        # Verification 1: Bit-level exactness
        assert np.array_equal(original_arr, reconstructed_arr), "Arrays are not bit-exact!"
        assert original_arr.shape == reconstructed_arr.shape
        assert original_arr.dtype == reconstructed_arr.dtype

        # Verification 2: True zero-copy memoryview
        assert reconstructed_arr.base is not None, "Array is not a zero-copy buffer view!"

        # Verification 3: Performance SLA < 50 ms
        print(f"\n[PERF] 50 MB Zero-Copy Transfer Latency: {t_elapsed_ms:.2f} ms (SLA < 50 ms)")
        assert t_elapsed_ms < 50.0, f"Transfer took {t_elapsed_ms:.2f} ms, exceeding 50 ms SLA!"

    finally:
        # Step 3: Resource cleanup
        if shm_write_handle is not None:
            cleanup_shm(shm_write_handle)
        if shm_read_handle is not None:
            cleanup_shm(shm_read_handle)
        SharedMemoryBuffer.cleanup_all()


def test_shared_memory_sha256_integrity_verification():
    """Verify SHA-256 fingerprint generation and tamper detection."""
    arr = np.linspace(1.0, 1000.0, 50000, dtype=np.float64)
    shm, meta = write_shared_array(arr, name="ansys_sha_verify", compute_sha256=True)
    assert len(meta.sha256) == 64

    # Valid read with integrity check
    _, arr_read = read_shared_array(meta, copy=False, verify_sha256=True)
    assert np.array_equal(arr, arr_read)

    # Tampered metadata should trigger ValueError
    meta_corrupted = meta.model_copy(update={"sha256": "0" * 64})
    with pytest.raises(ValueError, match="SHA-256 integrity check failed"):
        read_shared_array(meta_corrupted, copy=False, verify_sha256=True)

    cleanup_shm(shm)


def test_shared_memory_cleanup_and_leak_prevention():
    """Verify segments can be safely unlinked and cleaned up without leak."""
    test_arr = np.arange(1000, dtype=np.int32)
    shm, meta = write_shared_array(test_arr, name="ansys_leak_test")

    # Read back
    _, arr_read = read_shared_array(meta, copy=True)
    assert np.array_equal(test_arr, arr_read)

    # Cleanup
    cleanup_shm(meta.name)
    SharedMemoryBuffer.cleanup_all()


# ==============================================================================
# 2. Named Pipe Transport Tests (Signaling & 64 KB Automatic Overflow)
# ==============================================================================

def test_named_pipe_ping_and_echo_signaling():
    """Verify control-plane ping/pong and echo signaling round-trips."""
    transport = NamedPipeTransport()

    # Ping test
    resp_ping, _ = transport.send_and_receive_echo(payload="ping_test_payload", msg_type="ping")
    assert resp_ping.msg_type == "pong"
    assert resp_ping.payload == "ping_test_payload"
    assert not resp_ping.is_overflow

    # Echo test with structured dict
    request_data = {"tool": "mechanical_solve", "mesh_size_mm": 2.5, "unit_system": "Metric"}
    resp_echo, _ = transport.send_and_receive_echo(payload=request_data, msg_type="echo")
    assert resp_echo.msg_type == "echo_response"
    assert resp_echo.payload == request_data
    assert not resp_echo.is_overflow


def test_named_pipe_large_payload_automatic_overflow():
    """Verify payloads exceeding 64 KB automatically overflow to SharedMemory."""
    transport = NamedPipeTransport(threshold_bytes=OVERFLOW_THRESHOLD_BYTES)

    # Create 128 KB array (exceeds 64 KB threshold)
    large_arr = np.linspace(0.0, 100.0, 16384, dtype=np.float64)  # 16384 * 8 = 131,072 bytes (128 KB)
    assert large_arr.nbytes > OVERFLOW_THRESHOLD_BYTES

    resp, shm_handle = transport.send_and_receive_echo(payload=large_arr, msg_type="echo")

    try:
        # Message must be marked as overflow
        assert resp.is_overflow is True
        assert resp.shm_metadata is not None
        assert resp.shm_metadata.size_bytes == large_arr.nbytes

        # Reconstructed payload must equal original array
        assert isinstance(resp.payload, np.ndarray)
        assert np.array_equal(resp.payload, large_arr)
    finally:
        if shm_handle is not None:
            cleanup_shm(shm_handle)
        SharedMemoryBuffer.cleanup_all()


# ==============================================================================
# 3. Token Bucket License Scheduler Tests
# ==============================================================================

def test_scheduler_human_buffer_gate():
    """Verify Human_Buffer = 1 gate strictly prevents agent checkout when tokens <= 1."""
    # Inventory: 2 mechanical tokens
    scheduler = TokenBucketLicenseScheduler(inventory={"meba": 2}, human_buffer=1)

    # 1. First checkout of 1 token should succeed (2 - 1 = 1 remaining, equals human_buffer)
    assert scheduler.acquire("task_1", {"meba": 1}) is True
    assert scheduler.get_available_tokens("meba") == 1

    # 2. Second checkout of 1 token should be DENIED because remaining would be 0 < human_buffer
    can_acquire, reason = scheduler.can_acquire({"meba": 1})
    assert can_acquire is False
    assert "Human buffer violation" in reason or "Insufficient tokens" in reason
    assert scheduler.acquire("task_2", {"meba": 1}) is False

    # 3. Release task 1 restores availability
    scheduler.release("task_1", normal_exit=True)
    assert scheduler.get_available_tokens("meba") == 2

    # Now task 2 can acquire
    assert scheduler.acquire("task_2", {"meba": 1}) is True
    scheduler.release("task_2", normal_exit=True)


def test_scheduler_speos_and_rocky_atomic_multi_feature():
    """Verify atomic multi-feature checkout (Speos+HPC and Rocky+GPU)."""
    inventory = {
        "speos_optic": 1,
        "ans_d_hpc": 4,
        "rocky_solver_gpu": 1,
    }
    scheduler = TokenBucketLicenseScheduler(inventory=inventory, human_buffer=1)

    # Case A: Request Speos with 8 HPC cores (only 4 available)
    # Must fail atomically: neither speos_optic nor ans_d_hpc should be allocated!
    can_do, _ = scheduler.can_acquire({"speos_optic": 1, "ans_d_hpc": 8})
    assert can_do is False
    assert scheduler.acquire("task_speos_fail", {"speos_optic": 1, "ans_d_hpc": 8}) is False
    assert scheduler.get_available_tokens("speos_optic") == 1
    assert scheduler.get_available_tokens("ans_d_hpc") == 4

    # Case B: Rocky multi-feature check
    # rocky_solver_gpu available is 1, human_buffer is 1 -> available <= human_buffer, blocked
    can_do_rocky, reason = scheduler.can_acquire({"rocky_solver_gpu": 1})
    assert can_do_rocky is False
    assert "Human buffer violation" in reason

    # Expand Rocky inventory to 2
    scheduler.set_inventory("rocky_solver_gpu", 2)
    assert scheduler.acquire("task_rocky_ok", {"rocky_solver_gpu": 1}) is True
    assert scheduler.get_available_tokens("rocky_solver_gpu") == 1
    scheduler.release("task_rocky_ok", normal_exit=True)


def test_scheduler_abnormal_exit_300s_license_linger():
    """Verify 300-second license lingering cooldown on abnormal task exit."""
    scheduler = TokenBucketLicenseScheduler(
        inventory={"fluent_solve": 4},
        human_buffer=1,
        linger_duration=300.0,
    )

    t0 = 1000.0
    # Acquire token
    assert scheduler.acquire("task_cfd_crash", {"fluent_solve": 1}, current_time=t0) is True

    # Abnormal task crash at t0 + 10s
    scheduler.release("task_cfd_crash", normal_exit=False, current_time=t0 + 10.0)

    # At t0 + 50s (within 300s window), feature must be in linger cooldown
    assert scheduler.is_in_linger("fluent_solve", current_time=t0 + 50.0) is True
    can_do, reason = scheduler.can_acquire({"fluent_solve": 1}, current_time=t0 + 50.0)
    assert can_do is False
    assert "linger cooldown" in reason

    # At t0 + 315s (after 300s window), cooldown expires
    assert scheduler.is_in_linger("fluent_solve", current_time=t0 + 315.0) is False
    can_do_after, _ = scheduler.can_acquire({"fluent_solve": 1}, current_time=t0 + 315.0)
    assert can_do_after is True


# ==============================================================================
# 4. Interactive Desktop Guard Tests (Session 0 & Silent Flags)
# ==============================================================================

def test_interactive_desktop_guard_session_zero_blockage():
    """Verify Session 0 blocks GUI solvers and allows headless solvers."""
    guard = InteractiveDesktopGuard

    # Simulate Windows Session 0
    os.environ["ANSYS_MOCK_SESSION_ID"] = "0"
    try:
        assert guard.is_session_zero() is True

        # GUI-dependent solver must raise SessionZeroExecutionError
        with pytest.raises(SessionZeroExecutionError) as exc_info:
            guard.assert_not_session_zero(requires_gui=True, solver_name="ansysedt.exe")
        assert "blocked in Windows Session 0" in str(exc_info.value)

        # Headless solver execution is allowed in Session 0
        guard.assert_not_session_zero(requires_gui=False, solver_name="pyfluent_batch")

    finally:
        # Restore mock session id to interactive session 1
        os.environ["ANSYS_MOCK_SESSION_ID"] = "1"
        assert guard.is_session_zero() is False
        guard.assert_not_session_zero(requires_gui=True, solver_name="ansysedt.exe")


def test_interactive_desktop_guard_silent_flags_injection():
    """Verify silent flags and popup-suppressing environment variables are injected."""
    guard = InteractiveDesktopGuard

    # 1. Electronics Desktop (HFSS)
    args_hfss, env_hfss = guard.inject_silent_flags("ansysedt.exe", ["-run_script", "sim.py"])
    assert "-ng" in args_hfss
    assert "-BatchSolve" in args_hfss
    assert env_hfss["ANSYSEM_DONT_SHOW_MESSAGEBOX"] == "1"
    assert env_hfss["ANS_NODIAG"] == "1"

    # 2. Mechanical
    args_mech, env_mech = guard.inject_silent_flags("AnsysWBU.exe", ["-script", "solve.py"])
    assert "-Batch" in args_mech
    assert env_mech["ANSYS_NO_GUI"] == "1"

    # 3. Fluent
    args_fluent, env_fluent = guard.inject_silent_flags("fluent.exe", ["3ddp"])
    assert "-g" in args_fluent
    assert env_fluent["FLUENT_BATCH"] == "1"
