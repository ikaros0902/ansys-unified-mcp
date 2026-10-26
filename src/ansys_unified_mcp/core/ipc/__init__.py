# Strictly ASCII English Comments
"""Cross-virtual-environment IPC: SharedMemory data plane and NamedPipe control plane."""

from __future__ import annotations

from ansys_unified_mcp.core.ipc.named_pipe_transport import (
    IPCClient,
    IPCServer,
    NamedPipeClient,
    NamedPipeMessage,
    NamedPipeServer,
    NamedPipeTransport,
    OVERFLOW_THRESHOLD_BYTES,
    decode_jsonrpc_message,
    encode_jsonrpc_message,
    get_ipc_endpoint,
)
from ansys_unified_mcp.core.ipc.shared_memory_buffer import (
    SharedMemoryBuffer,
    SharedMemoryBufferError,
    SharedMemoryMetadata,
    cleanup_all_shm,
    cleanup_shm,
    read_numpy_from_shm,
    read_shared_array,
    write_numpy_to_shm,
    write_shared_array,
)
from ansys_unified_mcp.core.ipc.venv_supervisor import (
    DOMAIN_CONFIGS,
    VenvSupervisor,
    WorkerProcess,
    supervisor,
)

__all__ = [
    "SharedMemoryBuffer",
    "SharedMemoryBufferError",
    "SharedMemoryMetadata",
    "write_numpy_to_shm",
    "read_numpy_from_shm",
    "write_shared_array",
    "read_shared_array",
    "cleanup_shm",
    "cleanup_all_shm",
    "get_ipc_endpoint",
    "NamedPipeServer",
    "NamedPipeClient",
    "IPCServer",
    "IPCClient",
    "NamedPipeMessage",
    "NamedPipeTransport",
    "OVERFLOW_THRESHOLD_BYTES",
    "encode_jsonrpc_message",
    "decode_jsonrpc_message",
    "VenvSupervisor",
    "WorkerProcess",
    "supervisor",
    "DOMAIN_CONFIGS",
]
