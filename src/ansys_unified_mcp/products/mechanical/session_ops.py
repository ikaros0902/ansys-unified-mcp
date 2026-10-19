"""ANSYS Mechanical session and connection operations.

Guards Mechanical lifecycle: instance listing, connection, launch, disconnection,
connection status probing, and raw ACT script execution.
"""

from __future__ import annotations
from typing import Optional

from ansys_unified_mcp.products.mechanical.facade import controller

def _check_conn():
    """Return error payload if not connected."""
    from ansys_unified_mcp.products.mechanical import api
    return api._check_connection()

def list_instances() -> dict:
    """List all running and registered ANSYS instances (Mechanical, Workbench, etc.) and their ports."""
    from ansys_unified_mcp.bridges.connection_manager import connection_manager
    try:
        instances = connection_manager.get_registered_instances()
        return {"ok": True, "instances": instances}
    except Exception as e:
        return {"ok": False, "error": f"Failed to list instances: {e}"}

def connect_to_mechanical(port: Optional[int] = None, pid: Optional[int] = None) -> dict:
    """Connect to ANSYS Mechanical via gRPC.
    Args:
        port: gRPC connection port. If omitted, connects to the first running instance.
        pid: gRPC connection PID. Connects to the Mechanical instance with this PID.
    """
    return controller.connect(port=port, pid=pid)

def launch_mechanical(batch: bool = True) -> dict:
    """Launch a new headless Mechanical instance via PyMechanical.
    Args:
        batch: Launch in batch (headless) mode. Set False for a visible session.
    """
    return controller.launch(batch=batch)

def disconnect_from_mechanical() -> dict:
    """Disconnect the current Mechanical session."""
    err = _check_conn()
    if err:
        return err
    return controller.disconnect()

def check_mechanical_connection() -> dict:
    """Check connection status (lists all bound Mechanical sessions)."""
    status = controller.status()
    if not status.get("connected"):
        return {"ok": False, "connected": False}
    info = controller.run_script(
        "model = ExtAPI.DataModel.Project.Model\n"
        "for i, a in enumerate(model.Analyses):\n"
        '    print("[" + str(i) + "] " + str(a.Name) + " (" + str(a.AnalysisType) + ")")\n'
    )
    return {"ok": True, "connected": True, **status, "info": info}

def run_mechanical_script(script: str, timeout_seconds: Optional[float] = None) -> dict:
    """Run custom Python script inside Mechanical ACT API."""
    err = _check_conn()
    if err:
        return err
    result = controller.run_script(script, timeout=timeout_seconds)
    if not result or not result.strip():
        return {"ok": False, "error": "Script execution returned empty output", "output": result}

    lower = result.lower()
    fatal_keywords = [
        "exception:", "traceback", "syntaxerror:", "nameerror:", "attributeerror:",
        "typeerror:", "indexerror:", "keyerror:", "system.exception",
        "ansys.mechanical.core.errors", "script error:", "system.nullreferenceexception",
        "system.invalidoperationexception", "502 bad gateway", "500 internal server error", "<html"
    ]
    if any(kw in lower for kw in fatal_keywords):
        return {"ok": False, "error": f"Script execution failed: {result[:200]}", "output": result}

    return {"ok": True, "output": result}
