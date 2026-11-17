# -*- coding: utf-8 -*-
"""ANSYS Sherlock MCP 工具層：暴露電子產品可靠度物理 (PoF)、焊點熱疲勞與振動壽命分析工具。"""

from __future__ import annotations

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.products.sherlock.driver import SherlockDriver


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def sherlock_check_connection() -> dict:
    """檢查本機 ANSYS Sherlock 電子可靠度分析環境可用性。"""
    driver = SherlockDriver()
    valid, message = driver.validate_prerequisites()
    return _envelope({
        "available": valid,
        "solver_bin": driver.solver_bin,
        "message": message,
    })


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def sherlock_run_thermal_fatigue_life(
    delta_t_c: float = 80.0,
    t_mean_c: float = 40.0,
    package_diagonal_mm: float = 25.0,
    solder_joint_height_mm: float = 0.25,
    delta_cte_ppm: float = 12.0,
    dwell_time_minutes: float = 15.0,
    dry_run: bool = False,
) -> dict:
    """調度 ANSYS Sherlock 評估 BGA 焊點在溫度循環工況下的熱疲勞壽命 (Engelmaier-Wild PoF 模型)。

    Args:
        delta_t_c: 溫度循環溫差 Delta-T (攝氏度 C，如 -40C 至 125C 則傳 165)。
        t_mean_c: 平均環境溫度 (攝氏度 C)。
        package_diagonal_mm: 晶片封裝對角線尺寸 (mm)。
        solder_joint_height_mm: 焊球/焊柱間隙高度 (mm, 預設 0.25mm)。
        delta_cte_ppm: 晶片與 PCB 之熱膨脹係數差 Delta-CTE (ppm/C)。
        dwell_time_minutes: 高溫持溫時間 (分鐘)。
        dry_run: 僅驗證參數。
    """
    if dry_run:
        return _envelope({"ok": True, "dry_run": True, "package": package_diagonal_mm})

    driver = SherlockDriver()
    result = driver.calculate_solder_thermal_fatigue(
        delta_t_c=delta_t_c,
        t_mean_c=t_mean_c,
        package_diagonal_mm=package_diagonal_mm,
        solder_joint_height_mm=solder_joint_height_mm,
        delta_cte_ppm=delta_cte_ppm,
        dwell_time_minutes=dwell_time_minutes,
    )
    result = driver.with_backend_metadata(result)
    return _envelope({"ok": True, **result})


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def sherlock_run_vibration_life(
    g_rms: float = 5.0,
    pcb_natural_freq_hz: float = 120.0,
    transmissibility_q: float = 10.0,
    lead_wire_diameter_mm: float = 0.5,
    dry_run: bool = False,
) -> dict:
    """調度 ANSYS Sherlock 評估隨機振動下 PCB 元件引腳疲勞壽命 (Steinberg 3-Band 模型)。

    Args:
        g_rms: 隨機振動輸入均方根加速度 (G_rms)。
        pcb_natural_freq_hz: PCB 板一階固有振動頻率 (Hz)。
        transmissibility_q: 諧振傳遞放大倍數 Q (通常 10 ~ 20)。
        lead_wire_diameter_mm: 元件引腳直徑 (mm)。
        dry_run: 僅驗證參數。
    """
    if dry_run:
        return _envelope({"ok": True, "dry_run": True, "g_rms": g_rms})

    driver = SherlockDriver()
    result = driver.calculate_vibration_fatigue(
        g_rms=g_rms,
        pcb_natural_freq_hz=pcb_natural_freq_hz,
        transmissibility_q=transmissibility_q,
        lead_wire_diameter_mm=lead_wire_diameter_mm,
    )
    result = driver.with_backend_metadata(result)
    return _envelope({"ok": True, **result})
