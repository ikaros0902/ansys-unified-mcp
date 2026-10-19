"""ANSYS Mechanical API 核心門面模組 (Facade).

本模組統籌 Mechanical 的通訊、連線、網格、Scoping、邊界條件與求解操作。
遵循 Clean-Room 重構架構，具體業務邏輯解耦至下列專門子模組：
- session_ops: 會話、連線生命週期與直接腳本執行
- mesh_ops: 網格尺寸、生成、品質統計與 CFL 步長調校
- scoping_ops: 幾何模型資訊、材料查詢指派、具名選擇、實體抑制與質點查詢
- boundary_ops: 固定/摩擦支承、集中力、壓力、位移、遠端位移、重力與彎矩
- solution_ops: 求解、狀態、變形/應力/反力後處理、報告生成、BOM 映射與群組接頭

外部呼叫者 (如 tools.py 與既有測試) 保持 100% 向後相容性。
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from ansys_unified_mcp.products.mechanical.facade import controller, _esc


# ---------------------------------------------------------------------------
# Envelope normalization and error detection helpers
# ---------------------------------------------------------------------------

def _to_bool_ok(val) -> bool:
    """寬鬆布林轉換：支援 bool, int, 字串 'true'/'false'/'1'/'0'。"""
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.strip().lower() not in ("false", "0", "null", "none", "")
    if val is None:
        return False
    return bool(val)


def _normalize_dict_envelope(data: dict) -> dict:
    """標準化字典信封：
    1. 若缺 'ok'，且字典內含 'error'，則預設 ok: False；其餘預設 ok: True。
    2. 強制將 'ok' 其型別轉為嚴格的 bool。
    """
    res = dict(data)
    if "ok" not in res:
        res["ok"] = False if "error" in res else True
    else:
        res["ok"] = _to_bool_ok(res["ok"])
    return res


def _is_error_output(text: str) -> bool:
    """偵測腳本 stdout 是否包含未捕獲的 Python / ACT 例外或致命錯誤。"""
    if not text or not isinstance(text, str):
        return False
    lower = text.lower()
    return any(err in lower for err in [
        "exception:", "traceback", "syntaxerror:",
        "nameerror:", "attributeerror:", "typeerror:", "indexerror:",
        "keyerror:", "system.exception", "ansys.mechanical.core.errors",
        "script error:", "system.nullreferenceexception", "system.invalidoperationexception",
        "502 bad gateway", "500 internal server error"
    ])


def _wrap_raw_output(result: str, default_ok: bool = True) -> dict:
    """安全構造原始腳本輸出的返回信封，偵測例外。"""
    if not result or not result.strip():
        return {
            "ok": False,
            "error": "Script execution returned empty output",
            "raw_output": result,
        }
    is_err = _is_error_output(result)
    payload = {
        "ok": False if is_err else default_ok,
        "raw_output": result,
    }
    if is_err:
        payload["error"] = result.strip()
    return payload


def _parse_mechanical_output(result: str, default_error: str = "Script execution failed") -> dict:
    """安全解析 Mechanical 輸出為 dict 信封：
    - 若 result 為合法字典，標準化信封後返回。
    - 若 result 為非字串型別（例如 list），封裝為 {"ok": True, "data": result}。
    - 若 result 為字串：
      1. 全局致命錯誤預檢（空字串、_is_error_output 為 True 或包含崩潰關鍵字），直接返回 ok: False。
      2. 嘗試整段解析為 JSON（若為 dict 則標準化，若為 list 則封裝）。
      3. 逐行搜尋合法 JSON（處理 ACT 前置除錯日誌或後置輸出）。
      4. 若均無法解析為 JSON，返回 ok: False 預防性報錯。
    """
    if isinstance(result, dict):
        return _normalize_dict_envelope(result)

    if not isinstance(result, str):
        if isinstance(result, list):
            return {"ok": True, "data": result}
        if result is None:
            return {
                "ok": False,
                "error": f"{default_error}: input is None",
                "raw_output": "",
            }
        result = str(result)

    # 1. 致命錯誤與例外前置檢查 (Global Pre-validation)
    if not result or not result.strip():
        return {
            "ok": False,
            "error": f"{default_error}: empty output",
            "raw_output": result,
        }

    fatal_keywords = [
        "script error:", "traceback", "exception:", "syntaxerror:",
        "system.exception", "system.nullreferenceexception",
        "system.invalidoperationexception", "502 bad gateway",
        "500 internal server error", "<html"
    ]
    lower = result.lower()
    if _is_error_output(result) or any(kw in lower for kw in fatal_keywords):
        return {
            "ok": False,
            "error": f"{default_error}: {result[:200]}",
            "raw_output": result,
        }

    # 2. 全篇整段嘗試解析為 JSON
    try:
        data = json.loads(result.strip())
        if isinstance(data, dict):
            return _normalize_dict_envelope(data)
        elif isinstance(data, list):
            return {"ok": True, "data": data}
    except Exception:
        pass

    # 3. 逐行尋找合法 JSON（處理夾雜 ACT 日誌之情境）
    for line in result.splitlines():
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                candidate = json.loads(line)
                if isinstance(candidate, dict):
                    return _normalize_dict_envelope(candidate)
            except Exception:
                pass

    # 4. 若皆無法解析為 JSON，依 M1 防線規範回傳 ok: False
    return {
        "ok": False,
        "error": f"{default_error}: {result[:200]}",
        "raw_output": result,
    }


# 向後相容別名：供舊版測試與模組導入
_safe_json_response = _parse_mechanical_output


# ---------------------------------------------------------------------------
# Connection & Dispatch helpers (Mocking Integration Points)
# ---------------------------------------------------------------------------

def _check_connection() -> dict | None:
    """檢查 Mechanical 連線狀態，若未連線則回傳錯誤字典。"""
    connected = False
    try:
        connected = bool(controller.is_connected())
    except Exception:
        pass
    if not connected:
        return {
            "ok": False,
            "error": "Not connected to Mechanical. Use launch_mechanical or connect_to_mechanical first.",
        }
    return None


def _run(script: str, timeout: Optional[float] = None) -> str:
    """執行 Mechanical 腳本並回傳原始字串。"""
    if timeout:
        old_timeout = getattr(controller, "timeout", None)
        try:
            controller.timeout = timeout
            return controller.run_script(script)
        finally:
            if old_timeout is not None:
                controller.timeout = old_timeout
    return controller.run_script(script)


# ---------------------------------------------------------------------------
# Submodule delegation & Re-exports
# ---------------------------------------------------------------------------

from ansys_unified_mcp.products.mechanical import session_ops
from ansys_unified_mcp.products.mechanical import mesh_ops
from ansys_unified_mcp.products.mechanical import scoping_ops
from ansys_unified_mcp.products.mechanical import boundary_ops
from ansys_unified_mcp.products.mechanical import solution_ops

# Session operations
list_instances = session_ops.list_instances
connect_to_mechanical = session_ops.connect_to_mechanical
launch_mechanical = session_ops.launch_mechanical
disconnect_from_mechanical = session_ops.disconnect_from_mechanical
check_mechanical_connection = session_ops.check_mechanical_connection
run_mechanical_script = session_ops.run_mechanical_script

# Mesh operations
set_mesh_element_size = mesh_ops.set_mesh_element_size
generate_mesh = mesh_ops.generate_mesh
get_mesh_statistics = mesh_ops.get_mesh_statistics
tune_cfl_mesh = mesh_ops.tune_cfl_mesh

# Scoping operations
get_model_info = scoping_ops.get_model_info
list_materials = scoping_ops.list_materials
assign_material = scoping_ops.assign_material
_NS_LOOKUP = scoping_ops._NS_LOOKUP
list_named_selections = scoping_ops.list_named_selections
delete_named_selection = scoping_ops.delete_named_selection
suppress_bodies = scoping_ops.suppress_bodies
list_point_masses = scoping_ops.list_point_masses

# Boundary & Load operations
add_fixed_support = boundary_ops.add_fixed_support
add_force = boundary_ops.add_force
add_pressure = boundary_ops.add_pressure
list_boundary_conditions = boundary_ops.list_boundary_conditions
add_frictionless_support = boundary_ops.add_frictionless_support
add_displacement = boundary_ops.add_displacement
add_remote_displacement = boundary_ops.add_remote_displacement
add_standard_gravity = boundary_ops.add_standard_gravity
add_remote_force = boundary_ops.add_remote_force
add_moment = boundary_ops.add_moment

# Solution & Post-processing operations
solve_analysis = solution_ops.solve_analysis
get_solve_status = solution_ops.get_solve_status
add_total_deformation_all_modes = solution_ops.add_total_deformation_all_modes
add_total_deformation = solution_ops.add_total_deformation
get_modal_frequencies = solution_ops.get_modal_frequencies
generate_report = solution_ops.generate_report
add_equivalent_stress = solution_ops.add_equivalent_stress
add_directional_deformation = solution_ops.add_directional_deformation
add_principal_stress = solution_ops.add_principal_stress
add_stress_tool = solution_ops.add_stress_tool
add_reaction_force = solution_ops.add_reaction_force
_build_pm_script = solution_ops._build_pm_script
_extract_json = solution_ops._extract_json
convert_prefix_to_point_mass = solution_ops.convert_prefix_to_point_mass
convert_part_to_point_mass = solution_ops.convert_part_to_point_mass
get_model_tree_hierarchy = solution_ops.get_model_tree_hierarchy
assign_materials_from_bom = solution_ops.assign_materials_from_bom
create_joints_from_groups = solution_ops.create_joints_from_groups

__all__ = [
    # Session
    "list_instances",
    "connect_to_mechanical",
    "launch_mechanical",
    "disconnect_from_mechanical",
    "check_mechanical_connection",
    "run_mechanical_script",
    # Mesh
    "set_mesh_element_size",
    "generate_mesh",
    "get_mesh_statistics",
    "tune_cfl_mesh",
    # Scoping
    "get_model_info",
    "list_materials",
    "assign_material",
    "list_named_selections",
    "delete_named_selection",
    "suppress_bodies",
    "list_point_masses",
    # Boundary
    "add_fixed_support",
    "add_force",
    "add_pressure",
    "list_boundary_conditions",
    "add_frictionless_support",
    "add_displacement",
    "add_remote_displacement",
    "add_standard_gravity",
    "add_remote_force",
    "add_moment",
    # Solution
    "solve_analysis",
    "get_solve_status",
    "add_total_deformation_all_modes",
    "add_total_deformation",
    "get_modal_frequencies",
    "generate_report",
    "add_equivalent_stress",
    "add_directional_deformation",
    "add_principal_stress",
    "add_stress_tool",
    "add_reaction_force",
    "convert_prefix_to_point_mass",
    "convert_part_to_point_mass",
    "get_model_tree_hierarchy",
    "assign_materials_from_bom",
    "create_joints_from_groups",
]
