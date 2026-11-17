# -*- coding: utf-8 -*-
"""ANSYS Aqwa MCP 工具層：暴露海洋水動力學、浮體垂盪振盪與水動力附加質量分析工具。"""

from __future__ import annotations

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.products.aqwa.driver import AqwaDriver


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def aqwa_check_connection() -> dict:
    """檢查本機 ANSYS Aqwa 海洋流體水動力學求解器可用性。"""
    driver = AqwaDriver()
    valid, message = driver.validate_prerequisites()
    return _envelope({
        "available": valid,
        "solver_bin": driver.solver_bin,
        "message": message,
    })


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def aqwa_solve_heave_oscillation(
    length_m: float = 20.0,
    beam_m: float = 10.0,
    draft_m: float = 2.0,
    added_mass_ratio: float = 0.8,
    damping_ratio: float = 0.05,
    initial_displacement_m: float = 1.0,
    simulation_time_s: float = 20.0,
    dry_run: bool = False,
) -> dict:
    """調度 ANSYS Aqwa 求解駁船/浮式結構物垂盪自由衰減振盪、附加質量與固有週期。

    Args:
        length_m: 浮體水線長度 L (m, 預設 20.0m)。
        beam_m: 浮體水線寬度 B (m, 預設 10.0m)。
        draft_m: 吃水深度 T (m, 預設 2.0m)。
        added_mass_ratio: 垂盪水動力附加質量比 a_33 / m (通常 0.7 ~ 1.0)。
        damping_ratio: 水動力輻射阻尼比 zeta。
        initial_displacement_m: 初始垂盪擾動位移 (m)。
        simulation_time_s: 時域動態模擬時長 (s)。
        dry_run: 僅驗證浮體幾何參數。
    """
    if dry_run:
        return _envelope({"ok": True, "dry_run": True, "displaced_volume_m3": length_m * beam_m * draft_m})

    driver = AqwaDriver()
    result = driver.solve_heave_oscillation(
        length_m=length_m,
        beam_m=beam_m,
        draft_m=draft_m,
        added_mass_ratio=added_mass_ratio,
        damping_ratio=damping_ratio,
        initial_displacement_m=initial_displacement_m,
        simulation_time_s=simulation_time_s,
    )
    result = driver.with_backend_metadata(result)
    return _envelope({"ok": True, **result})
