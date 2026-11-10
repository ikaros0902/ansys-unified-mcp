# -*- coding: utf-8 -*-
"""ANSYS Optics & Photonics MCP 工具層：暴露 Lumerical, Zemax, Speos 光學工具。"""

from __future__ import annotations

from typing import List
from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.products.optics.driver import OpticsDriver


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def optics_check_connection() -> dict:
    """檢查本機 ANSYS 光學家族 (Lumerical / Zemax OpticStudio / Speos) 求解器可用性。"""
    driver = OpticsDriver()
    valid, message = driver.validate_prerequisites()
    return _envelope({
        "available": valid,
        "solver_bin": driver.solver_bin,
        "message": message,
    })


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def optics_solve_lumerical_waveguide(
    core_index: float = 1.50,
    cladding_index: float = 1.45,
    core_half_thickness_um: float = 1.0,
    wavelength_um: float = 1.55,
    dry_run: bool = False,
) -> dict:
    """調度 ANSYS Lumerical 求解光波導 TE0 基模特徵值、有效折射率與光場限制因子。

    Args:
        core_index: 芯層折射率 n1 (預設 1.50)。
        cladding_index: 包層折射率 n2 (預設 1.45)。
        core_half_thickness_um: 波導芯層半厚度 a (um)。
        wavelength_um: 自由空間光波長 lambda0 (um, 預設 1.55um 通訊波段)。
        dry_run: 若為 True 則僅驗證光學參數。
    """
    if dry_run:
        return _envelope({"ok": True, "dry_run": True, "na": (core_index**2 - cladding_index**2)**0.5})

    driver = OpticsDriver()
    result = driver.solve_lumerical_waveguide(
        core_index=core_index,
        cladding_index=cladding_index,
        core_half_thickness_um=core_half_thickness_um,
        wavelength_um=wavelength_um,
    )
    return _envelope({"ok": True, **result})


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def optics_trace_zemax_lens(
    radii_mm: List[float] = [50.0, -50.0],
    thicknesses_mm: List[float] = [5.0],
    refractive_indices: List[float] = [1.0, 1.5168, 1.0],
    beam_radius_mm: float = 5.0,
    dry_run: bool = False,
) -> dict:
    """調度 ANSYS Zemax OpticStudio 執行 ABCD 矩陣近軸射線追蹤，求解系統有效焦距 (EFL)。

    Args:
        radii_mm: 各光學透鏡表面曲率半徑列表 (mm, 平面傳 0.0)。
        thicknesses_mm: 透鏡介質中心厚度列表 (mm)。
        refractive_indices: 包含物方、各透鏡材料與像方的折射率列表 (長度 = 曲率半徑數 + 1)。
        beam_radius_mm: 入射邊緣光線半徑 (mm)。
        dry_run: 若為 True 則僅驗證曲率。
    """
    if dry_run:
        return _envelope({"ok": True, "dry_run": True, "surface_count": len(radii_mm)})

    driver = OpticsDriver()
    result = driver.trace_zemax_paraxial(
        radii_mm=radii_mm,
        thicknesses_mm=thicknesses_mm,
        indices=refractive_indices,
        beam_radius_mm=beam_radius_mm,
    )
    return _envelope({"ok": True, **result})


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def optics_evaluate_speos_photometry(
    luminous_flux_lumen: float = 1200.0,
    distance_m: float = 2.5,
    beam_angle_deg: float = 60.0,
    dry_run: bool = False,
) -> dict:
    """調度 ANSYS Speos 評估光源光通量、發光強度 (cd) 與目標平面照度 (lux)。

    Args:
        luminous_flux_lumen: 光源總光通量 (流明 lm)。
        distance_m: 投射距離 (公尺 m)。
        beam_angle_deg: 光束角 (全角 degrees)。
        dry_run: 僅驗證參數。
    """
    if dry_run:
        return _envelope({"ok": True, "dry_run": True, "flux": luminous_flux_lumen})

    driver = OpticsDriver()
    result = driver.evaluate_speos_photometry(
        luminous_flux_lumen=luminous_flux_lumen,
        distance_m=distance_m,
        beam_angle_deg=beam_angle_deg,
    )
    return _envelope({"ok": True, **result})
