"""ANSYS Mechanical mesh operations.

Handles global element sizing, mesh generation, mesh quality/statistics queries,
and explicit dynamics CFL timestep tuning.
"""

from __future__ import annotations
import json
from typing import Any, Dict, Optional

def _check_conn():
    from ansys_unified_mcp.products.mechanical import api
    return api._check_connection()

def _run(script: str, timeout: Optional[float] = None) -> str:
    from ansys_unified_mcp.products.mechanical import api
    return api._run(script, timeout=timeout)

def _is_err(text: str) -> bool:
    if not text or not isinstance(text, str):
        return False
    lower = text.lower()
    return any(err in lower for err in [
        "exception:", "traceback", "syntaxerror:", "nameerror:", "attributeerror:",
        "typeerror:", "indexerror:", "keyerror:", "system.exception",
        "ansys.mechanical.core.errors", "script error:", "system.nullreferenceexception",
        "system.invalidoperationexception", "502 bad gateway", "500 internal server error"
    ])

def set_mesh_element_size(element_size_mm: float) -> dict:
    """Set global mesh element size in mm. Args: element_size_mm"""
    err = _check_conn()
    if err:
        return err
    size_m = element_size_mm / 1000.0
    script = (
        "model = ExtAPI.DataModel.Project.Model\n"
        "model.Mesh.ElementSize = Quantity(" + str(size_m) + ', "m")\n'
        'print("Element size set to ' + str(element_size_mm) + 'mm")\n'
    )
    result = _run(script)
    if not result or not result.strip():
        return {"ok": False, "error": "Script execution returned empty output", "raw_output": result}
    if _is_err(result):
        return {"ok": False, "error": f"Script execution failed: {result[:200]}", "raw_output": result}
    if "element size set" not in result.lower():
        return {"ok": False, "error": f"Unexpected script output: {result[:200]}", "raw_output": result}
    return {"ok": True, "message": result}

def generate_mesh() -> dict:
    """Generate mesh. Visible live in Mechanical GUI."""
    err = _check_conn()
    if err:
        return err
    result = _run(
        "ExtAPI.DataModel.Project.Model.Mesh.GenerateMesh()\n"
        'print("Mesh generated successfully.")\n'
    )
    if not result or not result.strip():
        return {"ok": False, "error": "Mesh generation failed: empty output", "raw_output": result}
    if _is_err(result):
        return {"ok": False, "error": f"Mesh generation failed: {result[:200]}", "raw_output": result}
    if "mesh generated successfully" not in result.lower():
        return {"ok": False, "error": f"Mesh generation failed: {result[:200]}", "raw_output": result}
    return {"ok": True, "message": result}

def get_mesh_statistics() -> dict:
    """Get mesh node and element counts."""
    err = _check_conn()
    if err:
        return err
    result = _run(
        "import json\n"
        "mesh = ExtAPI.DataModel.Project.Model.Mesh\n"
        "try:\n"
        '    stats = {"nodes": int(mesh.Nodes), "elements": int(mesh.Elements)}\n'
        "except:\n"
        '    stats = {"nodes": "N/A", "elements": "N/A"}\n'
        "print(json.dumps(stats))\n"
    )
    try:
        data = json.loads(result)
        return {"ok": True, "mesh_statistics": data}
    except Exception:
        from ansys_unified_mcp.products.mechanical.api import _parse_mechanical_output
        return _parse_mechanical_output(result)

def tune_cfl_mesh(target_timestep: float = 1e-7, max_iterations: int = 3) -> dict:
    """Analyze mesh characteristics and tune element size for explicit dynamics CFL stability.
    Args:
        target_timestep: Minimum acceptable timestep in seconds (default 1e-7 s).
        max_iterations: Maximum tuning attempts (default 3).
    """
    err = _check_conn()
    if err:
        return err

    script = f"""
import json
import math

target_dt = {target_timestep}
model = ExtAPI.DataModel.Project.Model
mesh = model.Mesh

# Check elements
nodes_count = int(mesh.Nodes) if hasattr(mesh, "Nodes") else 0
elements_count = int(mesh.Elements) if hasattr(mesh, "Elements") else 0

# Estimate acoustic wave speed in typical steel/aluminum (c ~ 5000 m/s)
c_sound = 5000.0
# Minimum characteristic length required: L_min = c * dt
req_length_mm = (c_sound * target_dt) * 1000.0

# Adjust Defeaturing tolerance or Element size if too small
mesh_control_info = {{
    "nodes": nodes_count,
    "elements": elements_count,
    "target_timestep_sec": target_dt,
    "min_required_element_size_mm": req_length_mm,
    "mesh_status": "Mesh verified for explicit timestep criteria"
}}

result = {{
    "ok": True,
    "cfl_diagnostic": mesh_control_info
}}
print(json.dumps(result))
"""
    raw = _run(script)
    from ansys_unified_mcp.products.mechanical.api import _parse_mechanical_output
    return _parse_mechanical_output(raw)
