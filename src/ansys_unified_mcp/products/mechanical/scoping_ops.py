"""ANSYS Mechanical scoping, materials, named selections, and body management.

Decomposes scoping and geometry management operations:
- Model info
- Material listing & assignment
- Named selections (listing, deletion)
- Body suppression
- Point mass queries
"""

from __future__ import annotations
import json
from typing import Any, Dict, Optional

from ansys_unified_mcp.products.mechanical.facade import _esc

_NS_LOOKUP = (
    "_ns = None\n"
    "for _item in ExtAPI.DataModel.Project.Model.GetChildren(DataModelObjectCategory.NamedSelection, True):\n"
    "    if str(_item.Name) == _NS_NAME:\n"
    "        _ns = _item\n"
    "        break\n"
)

def _check_conn():
    from ansys_unified_mcp.products.mechanical import api
    return api._check_connection()

def _run(script: str, timeout: Optional[float] = None) -> str:
    from ansys_unified_mcp.products.mechanical import api
    return api._run(script, timeout=timeout)

def _parse(result: str, default_error: str = "Script execution failed") -> dict:
    from ansys_unified_mcp.products.mechanical import api
    return api._parse_mechanical_output(result, default_error=default_error)

def _is_err(text: str) -> bool:
    from ansys_unified_mcp.products.mechanical import api
    return api._is_error_output(text)

def get_model_info() -> dict:
    """Get model info: bodies, named selections, analyses."""
    err = _check_conn()
    if err:
        return err
    result = _run(
        "import json\n"
        "model = ExtAPI.DataModel.Project.Model\n"
        "info = {}\n"
        "bodies = []\n"
        "for body in model.Geometry.GetChildren(DataModelObjectCategory.Body, True):\n"
        '    bodies.append({"name": str(body.Name), "material": str(body.Material) if hasattr(body, "Material") else "N/A"})\n'
        'info["bodies"] = bodies\n'
        'info["named_selections"] = [str(ns.Name) for ns in model.GetChildren(DataModelObjectCategory.NamedSelection, True)]\n'
        'info["analyses"] = [{"name": str(a.Name), "type": str(a.AnalysisType)} for a in model.Analyses]\n'
        "print(json.dumps(info))\n"
    )
    try:
        return {"ok": True, "model_info": json.loads(result)}
    except Exception:
        return _parse(result)

def list_materials() -> dict:
    """List all materials in Engineering Data."""
    err = _check_conn()
    if err:
        return err
    result = _run(
        "import json\n"
        "model = ExtAPI.DataModel.Project.Model\n"
        "materials = [str(m.Name) for m in model.Materials.Children]\n"
        'print(json.dumps({"materials": materials}))\n'
    )
    try:
        return {"ok": True, **json.loads(result)}
    except Exception:
        return _parse(result)

def assign_material(body_name: str, material_name: str) -> dict:
    """Assign material to a body. Args: body_name, material_name"""
    err = _check_conn()
    if err:
        return err
    safe_body = _esc(body_name)
    safe_mat = _esc(material_name)
    script = (
        "model = ExtAPI.DataModel.Project.Model\n"
        "assigned = False\n"
        "for body in model.Geometry.GetChildren(DataModelObjectCategory.Body, True):\n"
        '    if str(body.Name) == "' + safe_body + '":\n'
        '        body.Material = "' + safe_mat + '"\n'
        "        assigned = True\n"
        "        break\n"
        'print("Assigned" if assigned else "Body not found: ' + safe_body + '")\n'
    )
    result = _run(script)
    if not result or not result.strip():
        return {"ok": False, "error": "Script execution returned empty output", "message": result}
    if _is_err(result) or "not found" in result.lower():
        err_msg = result.strip() if _is_err(result) else f"Body not found: {body_name}"
        return {"ok": False, "error": err_msg, "message": result}
    if "assigned" not in result.lower():
        return {"ok": False, "error": f"Unexpected script output: {result[:200]}", "message": result}
    return {"ok": True, "message": result}

def list_named_selections() -> dict:
    """List all named selections with face/body counts."""
    err = _check_conn()
    if err:
        return err
    result = _run(
        "import json\n"
        "out = []\n"
        "for ns in ExtAPI.DataModel.Project.Model.GetChildren(DataModelObjectCategory.NamedSelection, True):\n"
        "    try:\n"
        "        cnt = len(ns.Location.Ids) if ns.Location else 0\n"
        "    except: cnt = 0\n"
        '    out.append({"name": str(ns.Name), "entity_count": cnt})\n'
        'print(json.dumps({"named_selections": out}))\n'
    )
    try:
        return {"ok": True, **json.loads(result)}
    except Exception:
        return _parse(result)

def delete_named_selection(name: str) -> dict:
    """Delete a named selection by name. Args: name"""
    err = _check_conn()
    if err:
        return err
    safe_name = _esc(name)
    result = _run(
        "import json\n"
        '_NS_NAME = "' + safe_name + '"\n' + _NS_LOOKUP + "if _ns is None:\n"
        '    print(json.dumps({"ok": False, "error": "Not found: ' + safe_name + '"}))\n'
        "else:\n"
        "    _ns.Delete()\n"
        '    print(json.dumps({"ok": True, "deleted": "' + safe_name + '"}))\n'
    )
    try:
        return json.loads(result)
    except Exception:
        return _parse(result)

def suppress_bodies(name_prefix: str = "", suppress: bool = True) -> dict:
    """Suppress or unsuppress bodies by name prefix (empty = all bodies)."""
    err = _check_conn()
    if err:
        return err
    action = "True" if suppress else "False"
    result = _run(
        "import json\n"
        '_PREFIX = "' + _esc(name_prefix) + '"\n'
        "_changed = []\n"
        "for _b in ExtAPI.DataModel.Project.Model.Geometry.GetChildren(DataModelObjectCategory.Body, True):\n"
        '    if _PREFIX == "" or str(_b.Name).startswith(_PREFIX):\n'
        "        _b.Suppressed = " + action + "\n"
        "        _changed.append(str(_b.Name))\n"
        'print(json.dumps({"ok": True, "affected": len(_changed), "bodies": _changed[:20]}))\n'
    )
    try:
        return json.loads(result)
    except Exception:
        return _parse(result)

def list_point_masses() -> dict:
    """List all Point Masses with CG, mass, pinball and scoped named selection."""
    err = _check_conn()
    if err:
        return err
    result = _run(
        "import json\n"
        "def _qm(q):\n"
        '    p=str(q).replace("[","").replace("]","").split(); v=float(p[0])\n'
        '    u=p[1] if len(p)>1 else "m"\n'
        '    if u=="mm": v/=1000.0\n'
        '    elif u=="cm": v/=100.0\n'
        "    return v\n"
        "out=[]\n"
        "for pm in ExtAPI.DataModel.Project.Model.Geometry.GetChildren(DataModelObjectCategory.PointMass, True):\n"
        "    try:\n"
        '        ns_name = str(pm.Location.Name) if pm.Location else "None"\n'
        '    except: ns_name = "None"\n'
        '    out.append({"name": str(pm.Name),\n'
        '        "mass_kg": round(_qm(pm.Mass),6),\n'
        '        "cg_mm": [round(_qm(pm.XCoordinate)*1000,1), round(_qm(pm.YCoordinate)*1000,1), round(_qm(pm.ZCoordinate)*1000,1)],\n'
        '        "pinball": str(pm.PinballRegion),\n'
        '        "named_selection": ns_name})\n'
        'print(json.dumps({"point_masses": out, "count": len(out)}))\n'
    )
    try:
        return {"ok": True, **json.loads(result)}
    except Exception:
        return _parse(result)
