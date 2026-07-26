from __future__ import annotations

import json
import os
import socket
from typing import Any


DEFAULT_HOST = os.environ.get("WORKBENCH_MCP_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.environ.get("WORKBENCH_MCP_PORT", "9885"))


def _get_active_socket_port(app_name: str = "AnsysFWW") -> int:
    try:
        reg_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "workbench_queue", "registry")
        )
        if os.path.exists(reg_dir):
            for name in os.listdir(reg_dir):
                if name.endswith(".json"):
                    with open(os.path.join(reg_dir, name), "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                        if data.get("app_name") == app_name and "socket_timer_port" in data:
                            return int(data["socket_timer_port"])
    except Exception:
        pass
    return DEFAULT_PORT


def _request(payload: dict[str, Any], timeout: float = 10.0, port: int | None = None) -> dict[str, Any]:
    data = (json.dumps(payload, ensure_ascii=False) + "\0").encode("utf-8")
    received = b""
    
    target_port = port
    if target_port is None:
        target_port = _get_active_socket_port("AnsysFWW")
        if target_port == DEFAULT_PORT:
            target_port = _get_active_socket_port("AnsysWBU")
            
    try:
        with socket.create_connection((DEFAULT_HOST, target_port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            sock.sendall(data)
            while b"\0" not in received:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                received += chunk
        if not received:
            return {"ok": False, "connected": True, "error": "No response from Workbench MCP socket timer"}
        return {
            "ok": True,
            "connected": True,
            "host": DEFAULT_HOST,
            "port": target_port,
            "response": json.loads(received.split(b"\0", 1)[0].decode("utf-8", errors="replace")),
        }
    except Exception as exc:
        return {
            "ok": False,
            "connected": False,
            "host": DEFAULT_HOST,
            "port": target_port,
            "error": str(exc),
            "hint": "Open Mechanical and start Workbench MCP > Socket Timer Start, or enable plugin auto-start.",
        }


def socket_timer_ping(timeout: float = 10.0) -> dict[str, Any]:
    return _request({"action": "ping"}, timeout=timeout)


def socket_timer_state(timeout: float = 10.0) -> dict[str, Any]:
    return _request({"action": "state"}, timeout=timeout)


def socket_timer_execute_python(code: str, timeout: float = 60.0) -> dict[str, Any]:
    return _request({"action": "execute_python", "code": code}, timeout=timeout)


def socket_timer_stop(timeout: float = 10.0) -> dict[str, Any]:
    return _request({"action": "stop"}, timeout=timeout)
