# -*- coding: utf-8 -*-
"""ANSYS Rocky DEM MCP 工具層：暴露離散元顆粒模擬工具。"""

from __future__ import annotations

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.products.rocky.driver import RockyDriver


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def rocky_check_connection() -> dict:
    """檢查本機 ANSYS Rocky DEM 求解器與環境狀態。"""
    driver = RockyDriver()
    valid, message = driver.validate_prerequisites()
    return _envelope({
        "available": valid,
        "solver_bin": driver.solver_bin,
        "message": message,
    })


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def rocky_solve(
    particle_radius_mm: float = 5.0,
    density_kg_m3: float = 2500.0,
    restitution_coeff: float = 0.5,
    num_particles: int = 250,
    drop_height_m: float = 0.5,
    sim_time_s: float = 1.0,
    dt_s: float = 0.001,
    dry_run: bool = False,
) -> dict:
    """調度 ANSYS Rocky DEM 求解離散顆粒自由落體、衝擊碰撞與沉降能量耗散。

    Args:
        particle_radius_mm: 顆粒平均半徑 (mm)。
        density_kg_m3: 顆粒材料密度 (kg/m^3, 預設 2500 kg/m^3 碎石/玻璃)。
        restitution_coeff: 法向恢復係數 e (0 < e < 1.0)。
        num_particles: 顆粒總數。
        drop_height_m: 初始落料高度 (m)。
        sim_time_s: 總模擬時長 (s)。
        dt_s: 時間步長 (s)。
        dry_run: 僅驗證參數。
    """
    if dry_run:
        return _envelope({"ok": True, "dry_run": True, "estimated_steps": int(sim_time_s / dt_s)})

    driver = RockyDriver()
    result = driver.solve_dem_particle_deposition(
        particle_radius_mm=particle_radius_mm,
        density_kg_m3=density_kg_m3,
        restitution_coeff=restitution_coeff,
        num_particles=num_particles,
        drop_height_m=drop_height_m,
        sim_time_s=sim_time_s,
        dt_s=dt_s,
    )
    result = driver.with_backend_metadata(result)
    return _envelope({"ok": True, **result})
