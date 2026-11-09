# -*- coding: utf-8 -*-
"""ANSYS Motor-CAD MCP 工具層：暴露永磁同步馬達 (PMSM) 反電動勢、銅損與電磁效率計算工具。"""

from __future__ import annotations

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.products.motorcad.driver import MotorCADDriver


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def motorcad_check_connection() -> dict:
    """檢查本機 ANSYS Motor-CAD 電機設計軟體安裝與可用性。"""
    driver = MotorCADDriver()
    valid, message = driver.validate_prerequisites()
    return _envelope({
        "available": valid,
        "solver_bin": driver.solver_bin,
        "message": message,
    })


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def motorcad_solve_efficiency_point(
    pole_pairs: int = 4,
    flux_linkage_wb: float = 0.05,
    stator_resistance_ohm: float = 0.10,
    omega_m_rad_s: float = 300.0,
    torque_target_nm: float = 15.0,
    dry_run: bool = False,
) -> dict:
    """調度 ANSYS Motor-CAD 求解永磁同步馬達 (PMSM) 在特定轉速與轉矩工況點下的銅損與電磁效率。

    Args:
        pole_pairs: 極對數 p (預設 4)。
        flux_linkage_wb: 永磁體等效磁鏈 psi_m (Webers, 預設 0.05 Wb)。
        stator_resistance_ohm: 定子單相電阻 Rs (Ohms, 預設 0.10 Ohm)。
        omega_m_rad_s: 機械角速度 (rad/s, 300 rad/s 約 2865 RPM)。
        torque_target_nm: 目標電磁轉矩 Tem (N*m, 預設 15.0 N*m)。
        dry_run: 僅驗證電機幾何與工況。
    """
    if dry_run:
        return _envelope({"ok": True, "dry_run": True, "target_power_w": omega_m_rad_s * torque_target_nm})

    driver = MotorCADDriver()
    result = driver.solve_operating_point(
        pole_pairs=pole_pairs,
        flux_linkage_wb=flux_linkage_wb,
        stator_resistance_ohm=stator_resistance_ohm,
        omega_m_rad_s=omega_m_rad_s,
        torque_target_nm=torque_target_nm,
    )
    return _envelope({"ok": True, **result})
