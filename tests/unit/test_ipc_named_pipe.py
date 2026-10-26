# Strictly ASCII English Comments
"""Unit tests for IPC Named Pipe control plane and JSON-RPC transport."""

from __future__ import annotations

import time
import numpy as np
import pytest

from ansys_unified_mcp.core.ipc.named_pipe_transport import (
    NamedPipeClient,
    NamedPipeServer,
    decode_jsonrpc_message,
    encode_jsonrpc_message,
    get_ipc_endpoint,
)
from ansys_unified_mcp.core.ipc.shared_memory_buffer import cleanup_all_shm


@pytest.fixture(autouse=True)
def _cleanup_fixture():
    yield
    cleanup_all_shm()


def test_endpoint_resolution():
    """Verify IPC endpoint resolution produces valid platform paths."""
    addr, family = get_ipc_endpoint("structural")
    if pytest.importorskip("sys").platform == "win32":
        assert addr.startswith(r"\\.\pipe\ansys_mcp_structural")
        assert family == "AF_PIPE"
    else:
        assert addr.endswith("ansys_mcp_structural.sock")
        assert family == "AF_UNIX"


def test_encode_decode_small_message():
    """Verify encoding and decoding a standard JSON-RPC 2.0 message."""
    req = {
        "jsonrpc": "2.0",
        "method": "ping",
        "params": {"foo": "bar"},
        "id": 101,
    }
    raw, shm_list = encode_jsonrpc_message(req)
    assert len(shm_list) == 0  # No overflow needed for small message

    decoded = decode_jsonrpc_message(raw)
    assert decoded["jsonrpc"] == "2.0"
    assert decoded["method"] == "ping"
    assert decoded["params"]["foo"] == "bar"
    assert decoded["id"] == 101


def test_encode_decode_large_numpy_auto_sink():
    """Verify large NumPy arrays are automatically diverted to SharedMemory."""
    # 20,000 float64 elements = 160,000 bytes (> 64 KB threshold)
    large_arr = np.linspace(0.0, 500.0, 20000, dtype=np.float64)
    req = {
        "jsonrpc": "2.0",
        "method": "set_field",
        "params": {"field_data": large_arr},
        "id": 202,
    }
    raw, shm_list = encode_jsonrpc_message(req)
    assert len(shm_list) > 0  # Array was diverted to SHM

    # Decode and verify automatic hydration back into ndarray
    decoded = decode_jsonrpc_message(raw, auto_hydrate=True)
    restored_arr = decoded["params"]["field_data"]
    assert isinstance(restored_arr, np.ndarray)
    assert np.array_equal(large_arr, restored_arr)


def test_server_client_roundtrip():
    """Verify live client-server JSON-RPC ping, custom call, and error handling."""
    domain = "test_roundtrip"
    server = NamedPipeServer(domain)

    # Register handlers
    server.register_handler("multiply", lambda x, y: x * y)
    server.register_handler("failing_op", lambda: (_ for _ in ()).throw(ValueError("Intentional error")))
    server.start()

    try:
        client = NamedPipeClient(domain)
        # Test built-in ping
        assert client.ping(timeout=3.0) is True

        # Test custom RPC method
        result = client.call("multiply", {"x": 6, "y": 7})
        assert result == 42

        # Test error handling
        with pytest.raises(RuntimeError, match="Intentional error"):
            client.call("failing_op")

        # Test non-existent method
        with pytest.raises(RuntimeError, match="Method 'unknown_method' not found"):
            client.call("unknown_method")

    finally:
        server.stop()


def test_server_client_large_array_transfer():
    """Verify transferring large multi-variable array over live pipe connection."""
    domain = "test_large_xfer"
    server = NamedPipeServer(domain)

    # Returns 100,000 float64 elements = 800 KB
    server.register_handler("generate_disp", lambda count: np.arange(count, dtype=np.float64))
    server.start()

    try:
        client = NamedPipeClient(domain)
        arr = client.call("generate_disp", {"count": 100000})

        assert isinstance(arr, np.ndarray)
        assert len(arr) == 100000
        assert arr[-1] == 99999.0
    finally:
        server.stop()
