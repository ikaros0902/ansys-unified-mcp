"""ANSYS Mechanical 邊界條件與負載管理模組 (Boundary & Load Operations).

提供固定支承、摩擦支承、位移、遠端位移、重力、集中力、壓力與彎矩等邊界條件之施加與查詢。
依循 Clean-Room 架構，所有操作均向 api._check_connection 與 api._run 委派，
內嵌 IronPython 腳本遵循全 ASCII 規範。
"""

from __future__ import annotations

import json
from typing import Optional

from ansys_unified_mcp.products.mechanical import api


def add_fixed_support(named_selection: str, analysis_index: int = 0) -> dict:
    """為指定具名選擇 (Named Selection) 施加固定支承 (Fixed Support)。"""
    err = api._check_connection()
    if err:
        return err
    safe_ns = api._esc(named_selection)
    script = (
        "import json\n"
        '_NS_NAME = "' + safe_ns + '"\n' + api._NS_LOOKUP + "if _ns is None:\n"
        '    print(json.dumps({"ok": False, "error": "Named selection not found"}))\n'
        "else:\n"
        "    _analysis = ExtAPI.DataModel.Project.Model.Analyses[" + str(analysis_index) + "]\n"
        "    _bc = _analysis.AddFixedSupport()\n"
        "    _bc.Location = _ns\n"
        '    print(json.dumps({"ok": True, "message": "Fixed Support added"}))\n'
    )
    result = api._run(script)
    try:
        return json.loads(result)
    except Exception:
        return api._parse_mechanical_output(result)


def add_force(
    named_selection: str,
    fx_n: float = 0.0,
    fy_n: float = 0.0,
    fz_n: float = 0.0,
    analysis_index: int = 0,
) -> dict:
    """為指定具名選擇施加三維分量集中力 (Force, 單位: N)。"""
    err = api._check_connection()
    if err:
        return err
    safe_ns = api._esc(named_selection)
    script = (
        "import json\n"
        '_NS_NAME = "' + safe_ns + '"\n' + api._NS_LOOKUP + "if _ns is None:\n"
        '    print(json.dumps({"ok": False, "error": "Named selection not found"}))\n'
        "else:\n"
        "    _analysis = ExtAPI.DataModel.Project.Model.Analyses[" + str(analysis_index) + "]\n"
        "    _bc = _analysis.AddForce()\n"
        "    _bc.Location = _ns\n"
        "    _bc.DefineBy = LoadDefineBy.Components\n"
        "    _bc.XComponent.Output.SetDiscreteValue(0, Quantity(" + str(fx_n) + ', "N"))\n'
        "    _bc.YComponent.Output.SetDiscreteValue(0, Quantity(" + str(fy_n) + ', "N"))\n'
        "    _bc.ZComponent.Output.SetDiscreteValue(0, Quantity(" + str(fz_n) + ', "N"))\n'
        '    print(json.dumps({"ok": True, "message": "Force added"}))\n'
    )
    result = api._run(script)
    try:
        return json.loads(result)
    except Exception:
        return api._parse_mechanical_output(result)


def add_pressure(named_selection: str, magnitude_pa: float, analysis_index: int = 0) -> dict:
    """為指定具名選擇施加均勻表面壓力 (Pressure, 單位: Pa)。"""
    err = api._check_connection()
    if err:
        return err
    safe_ns = api._esc(named_selection)
    script = (
        "import json\n"
        '_NS_NAME = "' + safe_ns + '"\n' + api._NS_LOOKUP + "if _ns is None:\n"
        '    print(json.dumps({"ok": False, "error": "Named selection not found"}))\n'
        "else:\n"
        "    _analysis = ExtAPI.DataModel.Project.Model.Analyses[" + str(analysis_index) + "]\n"
        "    _bc = _analysis.AddPressure()\n"
        "    _bc.Location = _ns\n"
        "    _bc.Magnitude.Output.SetDiscreteValue(0, Quantity(" + str(magnitude_pa) + ', "Pa"))\n'
        '    print(json.dumps({"ok": True, "message": "Pressure added"}))\n'
    )
    result = api._run(script)
    try:
        return json.loads(result)
    except Exception:
        return api._parse_mechanical_output(result)


def list_boundary_conditions(analysis_index: int = 0) -> dict:
    """列出指定分析系統中所有已定義的邊界條件與負載物件。"""
    err = api._check_connection()
    if err:
        return err
    script = (
        "import json\n"
        "analysis = ExtAPI.DataModel.Project.Model.Analyses[" + str(analysis_index) + "]\n"
        'bcs = [{"name": str(c.Name), "type": str(c.GetType().Name)} for c in analysis.Children]\n'
        'print(json.dumps({"boundary_conditions": bcs}))\n'
    )
    result = api._run(script)
    try:
        return {"ok": True, **json.loads(result)}
    except Exception:
        return api._parse_mechanical_output(result)


def add_frictionless_support(named_selection: str, analysis_index: int = 0) -> dict:
    """為指定具名選擇施加無摩擦支承 (Frictionless Support)。"""
    err = api._check_connection()
    if err:
        return err
    result = api._run(
        "import json\n"
        '_NS_NAME = "' + api._esc(named_selection) + '"\n' + api._NS_LOOKUP + "if _ns is None:\n"
        '    print(json.dumps({"ok": False, "error": "Named selection not found"}))\n'
        "else:\n"
        "    _bc = ExtAPI.DataModel.Project.Model.Analyses["
        + str(analysis_index)
        + "].AddFrictionlessSupport()\n"
        "    _bc.Location = _ns\n"
        '    print(json.dumps({"ok": True, "message": "Frictionless Support added"}))\n'
    )
    try:
        return json.loads(result)
    except Exception:
        return api._parse_mechanical_output(result)


def add_displacement(
    named_selection: str,
    x_mm: float | None = None,
    y_mm: float | None = None,
    z_mm: float | None = None,
    analysis_index: int = 0,
) -> dict:
    """為指定具名選擇施加位移約束 (Displacement, 單位: mm, None 代表自由度不約束)。"""
    err = api._check_connection()
    if err:
        return err

    def comp_line(comp, val):
        if val is None:
            return ""
        return (
            "    _bc."
            + comp
            + "Component.Output.SetDiscreteValue(0, Quantity("
            + str(val / 1000.0)
            + ', "m"))\n'
        )

    result = api._run(
        "import json\n"
        '_NS_NAME = "' + api._esc(named_selection) + '"\n' + api._NS_LOOKUP + "if _ns is None:\n"
        '    print(json.dumps({"ok": False, "error": "Named selection not found"}))\n'
        "else:\n"
        "    _bc = ExtAPI.DataModel.Project.Model.Analyses["
        + str(analysis_index)
        + "].AddDisplacement()\n"
        "    _bc.Location = _ns\n"
        "    _bc.DefineBy = LoadDefineBy.Components\n"
        + comp_line("X", x_mm)
        + comp_line("Y", y_mm)
        + comp_line("Z", z_mm)
        + '    print(json.dumps({"ok": True, "message": "Displacement added"}))\n'
    )
    try:
        return json.loads(result)
    except Exception:
        return api._parse_mechanical_output(result)


def add_remote_displacement(
    named_selection: str,
    x_mm: float | None = None,
    y_mm: float | None = None,
    z_mm: float | None = None,
    rot_x_deg: float | None = None,
    rot_y_deg: float | None = None,
    rot_z_deg: float | None = None,
    analysis_index: int = 0,
) -> dict:
    """為指定具名選擇施加遠端位移與旋轉角約束 (Remote Displacement)。"""
    err = api._check_connection()
    if err:
        return err

    def trans_line(comp, val):
        if val is None:
            return ""
        return (
            "    _bc."
            + comp
            + "Component.Output.SetDiscreteValue(0, Quantity("
            + str(val / 1000.0)
            + ', "m"))\n'
        )

    def rot_line(comp, val):
        if val is None:
            return ""
        return (
            "    _bc."
            + comp
            + "Rotation.Output.SetDiscreteValue(0, Quantity("
            + str(val)
            + ', "deg"))\n'
        )

    result = api._run(
        "import json\n"
        '_NS_NAME = "' + api._esc(named_selection) + '"\n' + api._NS_LOOKUP + "if _ns is None:\n"
        '    print(json.dumps({"ok": False, "error": "Named selection not found"}))\n'
        "else:\n"
        "    _bc = ExtAPI.DataModel.Project.Model.Analyses["
        + str(analysis_index)
        + "].AddRemoteDisplacement()\n"
        "    _bc.Location = _ns\n"
        + trans_line("X", x_mm)
        + trans_line("Y", y_mm)
        + trans_line("Z", z_mm)
        + rot_line("X", rot_x_deg)
        + rot_line("Y", rot_y_deg)
        + rot_line("Z", rot_z_deg)
        + '    print(json.dumps({"ok": True, "message": "Remote Displacement added"}))\n'
    )
    try:
        return json.loads(result)
    except Exception:
        return api._parse_mechanical_output(result)


def add_standard_gravity(
    analysis_index: int = 0,
    x_component: float = 0.0,
    y_component: float = -1.0,
    z_component: float = 0.0,
) -> dict:
    """為分析系統施加標準地球重力 (Standard Earth Gravity, 預設方向 -Y 向量)。"""
    err = api._check_connection()
    if err:
        return err
    result = api._run(
        "import json\n"
        "_grav = ExtAPI.DataModel.Project.Model.Analyses["
        + str(analysis_index)
        + "].AddStandardEarthGravity()\n"
        "_grav.DefineBy = LoadDefineBy.Components\n"
        "_grav.XComponent.Output.SetDiscreteValue(0, Quantity("
        + str(x_component * 9.80665)
        + ', "m s^-2"))\n'
        "_grav.YComponent.Output.SetDiscreteValue(0, Quantity("
        + str(y_component * 9.80665)
        + ', "m s^-2"))\n'
        "_grav.ZComponent.Output.SetDiscreteValue(0, Quantity("
        + str(z_component * 9.80665)
        + ', "m s^-2"))\n'
        'print(json.dumps({"ok": True, "message": "Standard Earth Gravity added"}))\n'
    )
    try:
        return json.loads(result)
    except Exception:
        return api._parse_mechanical_output(result)


def add_remote_force(
    named_selection: str,
    fx_n: float = 0.0,
    fy_n: float = 0.0,
    fz_n: float = 0.0,
    analysis_index: int = 0,
) -> dict:
    """為指定具名選擇施加遠端集中力 (Remote Force, 單位: N)。"""
    err = api._check_connection()
    if err:
        return err
    result = api._run(
        "import json\n"
        '_NS_NAME = "' + api._esc(named_selection) + '"\n' + api._NS_LOOKUP + "if _ns is None:\n"
        '    print(json.dumps({"ok": False, "error": "Named selection not found"}))\n'
        "else:\n"
        "    _bc = ExtAPI.DataModel.Project.Model.Analyses["
        + str(analysis_index)
        + "].AddRemoteForce()\n"
        "    _bc.Location = _ns\n"
        "    _bc.DefineBy = LoadDefineBy.Components\n"
        "    _bc.XComponent.Output.SetDiscreteValue(0, Quantity(" + str(fx_n) + ', "N"))\n'
        "    _bc.YComponent.Output.SetDiscreteValue(0, Quantity(" + str(fy_n) + ', "N"))\n'
        "    _bc.ZComponent.Output.SetDiscreteValue(0, Quantity(" + str(fz_n) + ', "N"))\n'
        '    print(json.dumps({"ok": True, "message": "Remote Force added"}))\n'
    )
    try:
        return json.loads(result)
    except Exception:
        return api._parse_mechanical_output(result)


def add_moment(
    named_selection: str,
    mx_nm: float = 0.0,
    my_nm: float = 0.0,
    mz_nm: float = 0.0,
    analysis_index: int = 0,
) -> dict:
    """為指定具名選擇施加三維分量彎矩 (Moment, 單位: N·m)。"""
    err = api._check_connection()
    if err:
        return err
    result = api._run(
        "import json\n"
        '_NS_NAME = "' + api._esc(named_selection) + '"\n' + api._NS_LOOKUP + "if _ns is None:\n"
        '    print(json.dumps({"ok": False, "error": "Named selection not found"}))\n'
        "else:\n"
        "    _bc = ExtAPI.DataModel.Project.Model.Analyses["
        + str(analysis_index)
        + "].AddMoment()\n"
        "    _bc.Location = _ns\n"
        "    _bc.DefineBy = LoadDefineBy.Components\n"
        "    _bc.XComponent.Output.SetDiscreteValue(0, Quantity(" + str(mx_nm) + ', "N m"))\n'
        "    _bc.YComponent.Output.SetDiscreteValue(0, Quantity(" + str(my_nm) + ', "N m"))\n'
        "    _bc.ZComponent.Output.SetDiscreteValue(0, Quantity(" + str(mz_nm) + ', "N m"))\n'
        '    print(json.dumps({"ok": True, "message": "Moment added"}))\n'
    )
    try:
        return json.loads(result)
    except Exception:
        return api._parse_mechanical_output(result)
