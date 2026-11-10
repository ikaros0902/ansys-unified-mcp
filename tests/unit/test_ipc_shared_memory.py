# Strictly ASCII English Comments
"""Unit tests for IPC shared memory data plane."""

from __future__ import annotations

import numpy as np
import pytest

from ansys_unified_mcp.core.ipc.shared_memory_buffer import (
    SharedMemoryBuffer,
    cleanup_all_shm,
    cleanup_shm,
    read_numpy_from_shm,
    read_shared_array,
    write_numpy_to_shm,
    write_shared_array,
)


@pytest.fixture(autouse=True)
def _shm_cleanup_fixture():
    """Ensure shared memory segments are cleaned up after each test."""
    yield
    cleanup_all_shm()


def test_write_and_read_1d_array():
    """Verify writing and reading a 1D float64 array via SharedMemory."""
    orig = np.linspace(0.0, 100.0, 1000, dtype=np.float64)
    meta = write_numpy_to_shm(name="test_1d", arr=orig)

    assert meta["shm_name"] == "test_1d"
    assert meta["shape"] == [1000]
    assert meta["dtype"] == "float64"
    assert meta["nbytes"] == 8000
    assert len(meta["sha256"]) == 64

    # Read back zero-copy
    restored = read_numpy_from_shm(meta, verify_hash=True, copy=False)
    assert np.array_equal(orig, restored)
    assert restored.dtype == np.float64
    assert restored.shape == (1000,)


def test_write_auto_name():
    """Verify write_numpy_to_shm auto-generates unique segment name."""
    arr = np.ones((50, 50), dtype=np.int32)
    meta = write_numpy_to_shm(arr)

    assert meta["shm_name"].startswith("ansys_shm_")
    assert meta["shape"] == [50, 50]
    assert meta["dtype"] == "int32"

    restored = read_numpy_from_shm(meta)
    assert np.array_equal(arr, restored)


def test_complex128_s_parameters():
    """Verify multi-port complex S-parameter matrix storage and retrieval."""
    num_ports, num_freqs = 4, 201
    s_params = (
        np.random.randn(num_ports, num_ports, num_freqs)
        + 1j * np.random.randn(num_ports, num_ports, num_freqs)
    ).astype(np.complex128)

    meta = write_numpy_to_shm("test_s_params", s_params)
    assert meta["dtype"] == "complex128"

    restored = read_numpy_from_shm(meta, verify_hash=True)
    assert np.allclose(s_params, restored)


def test_sha256_tamper_detection():
    """Verify SHA-256 hash validation detects corrupted memory."""
    arr = np.arange(100, dtype=np.float64)
    meta = write_numpy_to_shm("test_tamper", arr)

    # Intentionally corrupt the expected SHA hash
    tampered_meta = dict(meta)
    tampered_meta["sha256"] = "0" * 64

    with pytest.raises(ValueError, match="SHA-256 integrity check failed"):
        read_numpy_from_shm(tampered_meta, verify_hash=True)


def test_copy_vs_zero_copy():
    """Verify copy=True returns a detached memory copy."""
    arr = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float64)
    meta = write_numpy_to_shm("test_copy", arr)

    copied = read_numpy_from_shm(meta, copy=True)
    assert np.array_equal(arr, copied)

    # Mutate copied; original in shm should remain unchanged
    copied[0] = 999.0
    view = read_numpy_from_shm(meta, copy=False)
    assert view[0] == 1.0


def test_cleanup_idempotent():
    """Verify cleanup_shm is idempotent and handles non-existent segments safely."""
    cleanup_shm("non_existent_segment_xyz")
    arr = np.zeros(10)
    meta = write_numpy_to_shm("test_clean", arr)
    cleanup_shm("test_clean")
    # Calling again should not raise
    cleanup_shm("test_clean")


def test_empty_array():
    """Verify handling of empty (0-element) arrays."""
    arr = np.empty((0, 3), dtype=np.float32)
    meta = write_numpy_to_shm("test_empty", arr)
    restored = read_numpy_from_shm(meta)
    assert restored.shape == (0, 3)
    assert restored.size == 0


def test_backward_compatible_wrappers():
    """Verify backward compatibility of write_shared_array and read_shared_array."""
    arr = np.array([42, 84], dtype=np.int64)
    shm, meta = write_shared_array(arr, name="test_compat")
    shm2, restored = read_shared_array(meta, copy=False, verify_sha256=True)
    assert np.array_equal(arr, restored)
