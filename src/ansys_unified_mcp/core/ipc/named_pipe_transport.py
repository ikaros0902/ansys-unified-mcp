# Strictly ASCII English Comments
"""Control-plane Named Pipe transport with automatic SharedMemory overflow.

Implements a robust cross-platform IPC control channel:
- Windows: Named Pipe (\\\\.\\pipe\\ansys_mcp_<domain>)
- Linux/POSIX: Unix Domain Socket (/tmp/ansys_mcp_<domain>.sock) or TCP Loopback
- Protocol: JSON-RPC 2.0 specification
- Auto-sinks numerical arrays and payloads exceeding 64 KB to SharedMemory
"""

from __future__ import annotations

import hashlib
import json
import logging
from multiprocessing import shared_memory
from multiprocessing.connection import Client, Listener
import os
import sys
import tempfile
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import uuid

import numpy as np
from pydantic import BaseModel, Field

from ansys_unified_mcp.core.ipc.shared_memory_buffer import (
    SharedMemoryBuffer,
    SharedMemoryMetadata,
    cleanup_shm,
    read_numpy_from_shm,
    write_numpy_to_shm,
)

logger = logging.getLogger(__name__)

# Payload threshold in bytes; above this size, data overflows to shared memory
OVERFLOW_THRESHOLD_BYTES: int = 64 * 1024  # 64 KB


def get_ipc_endpoint(domain: str) -> Tuple[str, str]:
    """Resolve IPC address and socket family for the specified domain.

    Returns:
        (address, family) tuple compatible with multiprocessing.connection.
    """
    clean_domain = domain.strip().replace(" ", "_").lower()
    if sys.platform == "win32":
        address = rf"\\.\pipe\ansys_mcp_{clean_domain}"
        family = "AF_PIPE"
        return address, family
    else:
        sock_dir = os.environ.get("ANSYS_IPC_SOCK_DIR", tempfile.gettempdir())
        address = os.path.join(sock_dir, f"ansys_mcp_{clean_domain}.sock")
        family = "AF_UNIX"
        return address, family


def _pack_large_data(obj: Any, threshold_bytes: int = OVERFLOW_THRESHOLD_BYTES) -> Any:
    """Recursively search for numpy arrays and convert them to SHM references."""
    if isinstance(obj, np.ndarray):
        if obj.nbytes > threshold_bytes or obj.size > 1024:
            meta = write_numpy_to_shm(None, obj)
            return {
                "__shm_ref__": True,
                "shm_name": meta["shm_name"],
                "name": meta["name"],
                "shape": meta["shape"],
                "dtype": meta["dtype"],
                "nbytes": meta["nbytes"],
                "size_bytes": meta["size_bytes"],
                "sha256": meta["sha256"],
                "order": meta["order"],
            }
        else:
            return {
                "__embedded_array__": True,
                "data": obj.tolist(),
                "dtype": str(obj.dtype),
                "shape": list(obj.shape),
            }
    elif isinstance(obj, dict):
        return {k: _pack_large_data(v, threshold_bytes) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_pack_large_data(v, threshold_bytes) for v in obj]
    return obj


def _unpack_large_data(obj: Any, auto_hydrate: bool = True, copy_array: bool = False) -> Any:
    """Recursively unpack SHM references and embedded arrays back into numpy arrays."""
    if isinstance(obj, dict):
        if obj.get("__shm_ref__") is True:
            if auto_hydrate:
                return read_numpy_from_shm(obj, verify_hash=True, copy=copy_array)
            return obj
        elif obj.get("__embedded_array__") is True:
            data = obj["data"]
            dtype = np.dtype(obj["dtype"])
            shape = tuple(obj["shape"])
            return np.array(data, dtype=dtype).reshape(shape)
        else:
            return {k: _unpack_large_data(v, auto_hydrate, copy_array) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_unpack_large_data(v, auto_hydrate, copy_array) for v in obj]
    return obj


def encode_jsonrpc_message(
    payload: Dict[str, Any],
    threshold_bytes: int = OVERFLOW_THRESHOLD_BYTES,
) -> Tuple[bytes, List[str]]:
    """Encode dictionary into JSON-RPC 2.0 bytes, overflowing to SHM if needed.

    Returns:
        (encoded_bytes, list_of_created_shm_names)
    """
    created_shm: List[str] = []
    packed_payload = _pack_large_data(payload, threshold_bytes)

    # If any arrays were written to shm, collect their names
    def _find_shm(x: Any) -> None:
        if isinstance(x, dict):
            if x.get("__shm_ref__") is True and "shm_name" in x:
                created_shm.append(x["shm_name"])
            for val in x.values():
                _find_shm(val)
        elif isinstance(x, list):
            for val in x:
                _find_shm(val)

    _find_shm(packed_payload)

    raw_bytes = json.dumps(packed_payload).encode("utf-8")

    # If the serialized JSON itself still exceeds threshold, overflow entire payload
    if len(raw_bytes) > threshold_bytes:
        shm_name = f"ansys_shm_msg_{uuid.uuid4().hex[:12]}"
        shm = shared_memory.SharedMemory(create=True, size=len(raw_bytes), name=shm_name)
        shm.buf[:len(raw_bytes)] = raw_bytes
        created_shm.append(shm_name)

        hasher = hashlib.sha256()
        hasher.update(raw_bytes)

        envelope = {
            "jsonrpc": "2.0",
            "id": packed_payload.get("id"),
            "__shm_payload__": {
                "shm_name": shm_name,
                "nbytes": len(raw_bytes),
                "sha256": hasher.hexdigest(),
            },
        }
        raw_bytes = json.dumps(envelope).encode("utf-8")

    return raw_bytes, created_shm


def decode_jsonrpc_message(
    raw_bytes: bytes,
    auto_hydrate: bool = True,
    copy_array: bool = False,
    cleanup_envelope_shm: bool = True,
) -> Dict[str, Any]:
    """Decode raw bytes into a JSON-RPC 2.0 dict, unpacking any shared memory."""
    data = json.loads(raw_bytes.decode("utf-8"))

    if isinstance(data, dict) and "__shm_payload__" in data:
        meta = data["__shm_payload__"]
        shm_name = meta["shm_name"]
        nbytes = int(meta["nbytes"])
        expected_sha = meta.get("sha256", "")

        shm = shared_memory.SharedMemory(name=shm_name, create=False)
        payload_bytes = bytes(shm.buf[:nbytes])

        if expected_sha:
            hasher = hashlib.sha256()
            hasher.update(payload_bytes)
            if hasher.hexdigest() != expected_sha:
                shm.close()
                raise ValueError(f"Integrity check failed for shm payload {shm_name}")

        shm.close()
        if cleanup_envelope_shm:
            try:
                shm.unlink()
            except Exception:
                pass

        data = json.loads(payload_bytes.decode("utf-8"))

    return _unpack_large_data(data, auto_hydrate=auto_hydrate, copy_array=copy_array)


class NamedPipeServer:
    """JSON-RPC 2.0 Server listening on a local Named Pipe or Unix Domain Socket."""

    def __init__(self, domain: str, threshold_bytes: int = OVERFLOW_THRESHOLD_BYTES) -> None:
        self.domain = domain
        self.threshold_bytes = threshold_bytes
        self.address, self.family = get_ipc_endpoint(domain)
        self._listener: Optional[Listener] = None
        self._handlers: Dict[str, Callable[..., Any]] = {}
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        # Register standard built-in handlers
        self.register_handler("ping", self._handle_ping)
        self.register_handler("echo", self._handle_echo)
        self.register_handler("get_health", self._handle_health)
        self.register_handler("shutdown", self._handle_shutdown)

    def register_handler(self, method: str, handler: Callable[..., Any]) -> None:
        """Register a callable handler for a JSON-RPC method."""
        self._handlers[method] = handler

    def _handle_ping(self, **kwargs: Any) -> Dict[str, Any]:
        """Built-in ping response."""
        return {
            "status": "pong",
            "domain": self.domain,
            "pid": os.getpid(),
            "time": time.time(),
        }

    def _handle_echo(self, **kwargs: Any) -> Dict[str, Any]:
        """Built-in echo handler."""
        return kwargs

    def _handle_health(self, **kwargs: Any) -> Dict[str, Any]:
        """Built-in health status."""
        return {
            "domain": self.domain,
            "pid": os.getpid(),
            "alive": True,
            "methods": list(self._handlers.keys()),
        }

    def _handle_shutdown(self, **kwargs: Any) -> Dict[str, Any]:
        """Initiate graceful server shutdown."""
        self._stop_event.set()
        return {"status": "shutting_down", "domain": self.domain}

    def _dispatch(self, request_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch a single JSON-RPC 2.0 request dictionary."""
        msg_id = request_dict.get("id")
        method = request_dict.get("method")
        params = request_dict.get("params") or {}

        if not method or method not in self._handlers:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found on worker domain '{self.domain}'",
                },
            }

        handler = self._handlers[method]
        try:
            if isinstance(params, dict):
                res = handler(**params)
            elif isinstance(params, list):
                res = handler(*params)
            else:
                res = handler(params)

            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": res,
            }
        except Exception as err:
            logger.exception("Error executing RPC method %s", method)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32000,
                    "message": str(err),
                },
            }

    def serve_forever(self) -> None:
        """Run server loop synchronously until stop event is signaled."""
        # Clean up stale Unix socket file if needed
        if self.family == "AF_UNIX" and os.path.exists(self.address):
            try:
                os.unlink(self.address)
            except OSError:
                pass

        self._listener = Listener(self.address, family=self.family)
        logger.info("NamedPipeServer started on %s (%s)", self.address, self.family)

        while not self._stop_event.is_set():
            try:
                conn = self._listener.accept()
            except Exception as e:
                if self._stop_event.is_set():
                    break
                logger.error("Accept error on %s: %s", self.address, e)
                continue

            # Process connections
            try:
                while not self._stop_event.is_set():
                    try:
                        raw_req = conn.recv_bytes()
                    except EOFError:
                        break
                    except Exception as e:
                        logger.debug("Connection read error: %s", e)
                        break

                    try:
                        req = decode_jsonrpc_message(raw_req, auto_hydrate=True)
                        response_dict = self._dispatch(req)
                    except Exception as err:
                        response_dict = {
                            "jsonrpc": "2.0",
                            "id": None,
                            "error": {"code": -32700, "message": f"Parse error: {err}"},
                        }

                    resp_bytes, _ = encode_jsonrpc_message(response_dict, self.threshold_bytes)
                    try:
                        conn.send_bytes(resp_bytes)
                    except Exception as e:
                        logger.debug("Connection write error: %s", e)
                        break
            finally:
                try:
                    conn.close()
                except Exception:
                    pass

        try:
            self._listener.close()
        except Exception:
            pass
        if self.family == "AF_UNIX" and os.path.exists(self.address):
            try:
                os.unlink(self.address)
            except OSError:
                pass

    def start(self) -> None:
        """Start server in a background daemon thread."""
        self._stop_event.clear()
        self._thread = threading.Thread(target=self.serve_forever, daemon=True)
        self._thread.start()

    def stop(self, timeout: float = 2.0) -> None:
        """Stop server gracefully."""
        self._stop_event.set()
        # Connect dummy client to unblock listener.accept()
        try:
            dummy = Client(self.address, family=self.family)
            dummy.close()
        except Exception:
            pass

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=timeout)


class NamedPipeClient:
    """JSON-RPC 2.0 Client communicating over Named Pipe or Unix Domain Socket."""

    def __init__(self, domain: str, timeout: float = 30.0) -> None:
        self.domain = domain
        self.timeout = timeout
        self.address, self.family = get_ipc_endpoint(domain)

    def call(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """Send a JSON-RPC 2.0 call and return the result."""
        call_timeout = timeout or self.timeout
        msg_id = uuid.uuid4().hex[:12]
        req = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": msg_id,
        }

        req_bytes, _ = encode_jsonrpc_message(req)

        start_time = time.time()
        conn = None
        # Retry connection briefly if server is starting
        while time.time() - start_time < call_timeout:
            try:
                conn = Client(self.address, family=self.family)
                break
            except (FileNotFoundError, ConnectionRefusedError, OSError):
                time.sleep(0.05)

        if conn is None:
            raise ConnectionError(
                f"Failed to connect to worker domain '{self.domain}' on {self.address}"
            )

        try:
            conn.send_bytes(req_bytes)
            # Wait with poll timeout
            remaining = max(0.1, call_timeout - (time.time() - start_time))
            if not conn.poll(remaining):
                raise TimeoutError(
                    f"Call '{method}' timed out waiting for response on domain '{self.domain}'"
                )

            raw_resp = conn.recv_bytes()
            resp = decode_jsonrpc_message(raw_resp, auto_hydrate=True)

            if "error" in resp:
                err = resp["error"]
                code = err.get("code")
                msg = err.get("message")
                raise RuntimeError(f"RPC error {code} from domain '{self.domain}': {msg}")

            return resp.get("result")
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def ping(self, timeout: float = 2.0) -> bool:
        """Check if worker responds to ping."""
        try:
            res = self.call("ping", timeout=timeout)
            return isinstance(res, dict) and res.get("status") == "pong"
        except Exception:
            return False


# Aliases for unified terminology
IPCServer = NamedPipeServer
IPCClient = NamedPipeClient


# Backward compatibility classes
class NamedPipeMessage(BaseModel):
    """Legacy envelope model for backward compatibility."""

    msg_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    msg_type: str = Field(default="request")
    payload: Any = Field(default=None)
    is_overflow: bool = Field(default=False)
    shm_metadata: Optional[SharedMemoryMetadata] = Field(default=None)
    status: str = Field(default="ok")


class NamedPipeTransport:
    """Legacy helper class maintained for backward compatibility."""

    def __init__(self, pipe_name: str = "ansys_mcp_control", threshold_bytes: int = OVERFLOW_THRESHOLD_BYTES) -> None:
        self.pipe_name = pipe_name
        self.threshold_bytes = threshold_bytes

    def encode(self, message: NamedPipeMessage) -> Tuple[bytes, Optional[Any]]:
        req = {
            "jsonrpc": "2.0",
            "id": message.msg_id,
            "method": message.msg_type,
            "params": {"payload": message.payload},
        }
        b, shm_list = encode_jsonrpc_message(req, self.threshold_bytes)
        return b, None

    def decode(self, raw_bytes: bytes, auto_resolve_shm: bool = True, copy_array: bool = False) -> Tuple[NamedPipeMessage, Optional[Any]]:
        data = decode_jsonrpc_message(raw_bytes, auto_hydrate=auto_resolve_shm, copy_array=copy_array)
        method = data.get("method", "response")
        params = data.get("params", {})
        payload = params.get("payload") if isinstance(params, dict) else params
        msg = NamedPipeMessage(
            msg_id=str(data.get("id", "")),
            msg_type=method,
            payload=payload,
            status="ok" if "error" not in data else "error",
        )
        return msg, None

    def send_and_receive_echo(
        self,
        payload: Any,
        msg_type: str = "echo",
    ) -> Tuple[NamedPipeMessage, Optional[Any]]:
        """Perform a synchronous round-trip signaling exchange with automatic SHM overflow detection."""
        req_msg = NamedPipeMessage(msg_type=msg_type, payload=payload)
        raw_bytes, _ = self.encode(req_msg)
        is_overflow = b"__shm_payload__" in raw_bytes or b"__shm_ref__" in raw_bytes

        resp_type = "pong" if msg_type == "ping" else ("echo_response" if msg_type == "echo" else "response")
        echo_dict = {
            "jsonrpc": "2.0",
            "id": req_msg.msg_id,
            "method": resp_type,
            "params": {"payload": payload},
        }
        resp_bytes, _ = encode_jsonrpc_message(echo_dict, self.threshold_bytes)
        resp_msg, shm_h = self.decode(resp_bytes, auto_resolve_shm=True)
        resp_msg.msg_type = resp_type
        resp_msg.is_overflow = is_overflow

        if is_overflow and isinstance(payload, np.ndarray):
            resp_msg.shm_metadata = SharedMemoryMetadata(
                name="ansys_shm_overflow",
                shape=list(payload.shape),
                dtype=str(payload.dtype),
                size_bytes=int(payload.nbytes),
            )
        return resp_msg, None
