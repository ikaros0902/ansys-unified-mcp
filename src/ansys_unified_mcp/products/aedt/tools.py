# -*- coding: utf-8 -*-
"""ANSYS Electronics Desktop (AEDT) MCP 工具層：暴露 HFSS, Maxwell, Q3D 電磁分析工具。"""

from __future__ import annotations

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.products.aedt.driver import AEDTDriver


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def aedt_check_connection() -> dict:
    """檢查本機 ANSYS Electronics Desktop (AEDT: HFSS / Maxwell / Q3D) 安裝與執行環境可用性。"""
    driver = AEDTDriver()
    valid, message = driver.validate_prerequisites()
    return _envelope({
        "available": valid,
        "solver_bin": driver.solver_bin,
        "message": message,
    })


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def aedt_solve_hfss(
    antenna_length_mm: float = 30.0,
    antenna_width_mm: float = 40.0,
    substrate_h_mm: float = 1.6,
    er: float = 4.4,
    f_start_ghz: float = 2.0,
    f_stop_ghz: float = 3.0,
    dry_run: bool = False,
) -> dict:
    """調度 ANSYS HFSS 求解微帶貼片天線諧振頻率、S11 回波損耗與 -10dB 頻寬。

    Args:
        antenna_length_mm: 貼片長度 L (mm)。
        antenna_width_mm: 貼片寬度 W (mm)。
        substrate_h_mm: 介質基板厚度 h (mm)。
        er: 基板相對介電常數 epsilon_r (預設 FR4 4.4)。
        f_start_ghz: 頻率掃描起始 (GHz)。
        f_stop_ghz: 頻率掃描終止 (GHz)。
        dry_run: 若為 True 則僅驗證幾何與頻率範圍，不執行求解。
    """
    if dry_run:
        return _envelope({
            "ok": True,
            "dry_run": True,
            "parameters": {
                "L": antenna_length_mm,
                "W": antenna_width_mm,
                "h": substrate_h_mm,
                "er": er,
                "f_range": [f_start_ghz, f_stop_ghz],
            },
        })

    driver = AEDTDriver()
    result = driver.solve_hfss_patch(
        length_mm=antenna_length_mm,
        width_mm=antenna_width_mm,
        substrate_h_mm=substrate_h_mm,
        er=er,
        f_start_ghz=f_start_ghz,
        f_stop_ghz=f_stop_ghz,
    )
    result = driver.with_backend_metadata(result)
    return _envelope({"ok": True, **result})


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def aedt_solve_maxwell(
    current_a: float = 5.0,
    turns: int = 200,
    air_gap_mm: float = 1.5,
    core_area_cm2: float = 4.0,
    core_ur: float = 2000.0,
    dry_run: bool = False,
) -> dict:
    """調度 ANSYS Maxwell 求解低頻電磁鐵磁動勢、磁通量、磁感應強度與電磁吸力。

    Args:
        current_a: 線圈激磁電流 (Amperes)。
        turns: 線圈匝數。
        air_gap_mm: 氣隙長度 (mm)。
        core_area_cm2: 鐵芯截面積 (cm^2)。
        core_ur: 鐵芯相對導磁率 mu_r。
        dry_run: 若為 True 則僅驗證參數。
    """
    if dry_run:
        return _envelope({
            "ok": True,
            "dry_run": True,
            "mmf_estimate": current_a * turns,
        })

    driver = AEDTDriver()
    result = driver.solve_maxwell_magnetic_circuit(
        current_a=current_a,
        turns=turns,
        air_gap_mm=air_gap_mm,
        core_area_cm2=core_area_cm2,
        core_ur=core_ur,
    )
    result = driver.with_backend_metadata(result)
    return _envelope({"ok": True, **result})


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def aedt_extract_rlcg(
    trace_width_um: float = 200.0,
    trace_thickness_um: float = 35.0,
    dielectric_height_um: float = 150.0,
    er: float = 4.4,
    length_mm: float = 25.0,
    dry_run: bool = False,
) -> dict:
    """調度 ANSYS Q3D Extractor 提取微帶傳輸線之 RLCG 寄生參數與特徵阻抗 Z0。

    Args:
        trace_width_um: 走線寬度 (um)。
        trace_thickness_um: 走線銅厚 (um, 如 1oz 銅約 35um)。
        dielectric_height_um: 介質層厚度 (um)。
        er: 介質介電常數。
        length_mm: 走線總長度 (mm)。
        dry_run: 僅回傳幾何配置。
    """
    if dry_run:
        return _envelope({"ok": True, "dry_run": True, "trace_w_h_ratio": trace_width_um / dielectric_height_um})

    driver = AEDTDriver()
    result = driver.extract_q3d_rlcg(
        trace_width_um=trace_width_um,
        trace_thickness_um=trace_thickness_um,
        dielectric_height_um=dielectric_height_um,
        er=er,
        length_mm=length_mm,
    )
    result = driver.with_backend_metadata(result)
    return _envelope({"ok": True, **result})
