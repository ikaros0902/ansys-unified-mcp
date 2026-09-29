from __future__ import annotations
import logging
from typing import Any

from ansys_unified_mcp.bridges import workbench_socket
from ansys_unified_mcp.bridges import workbench_filequeue

logger = logging.getLogger(__name__)

def send_command(action: str, timeout: float = 30.0, transport: str = "auto", **kwargs: Any) -> dict[str, Any]:
    """
    Route commands to Mechanical/Workbench via the specified transport layer.
    
    Args:
        action: The command action string.
        timeout: Timeout in seconds.
        transport: 'auto' (try socket, fallback queue), 'socket', or 'queue'.
        **kwargs: Additional payload arguments.
        
    Returns:
        dict: Standardized response envelope (with 'ok' flag).
    """
    req = {"action": action}
    req.update(kwargs)
    
    if transport in ("auto", "socket"):
        # Try socket first
        try:
            resp = workbench_socket.send_request(req, timeout=timeout)
            
            # If socket succeeds, or user forced socket, format and return
            if resp and resp.get("status") != "error":
                if "status" in resp:
                    resp["ok"] = (resp["status"] == "success")
                return resp
            
            # If forced socket but failed, return the error
            if transport == "socket":
                if "status" in resp:
                    resp["ok"] = False
                return resp
                
            # If 'auto' and socket failed (e.g. refused connection), log and fallback
            logger.debug(f"Socket transport failed, falling back to file queue. Reason: {resp.get('message')}")
            
        except Exception as e:
            if transport == "socket":
                return {"ok": False, "error": str(e)}
            logger.debug(f"Socket exception, falling back to file queue. Error: {str(e)}")
            
    # Fallback or explicit 'queue' transport
    return workbench_filequeue._send_command(action, timeout=timeout, **kwargs)
