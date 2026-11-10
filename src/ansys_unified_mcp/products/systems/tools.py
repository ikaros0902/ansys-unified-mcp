# -*- coding: utf-8 -*-
"""ANSYS Systems & Digital Twin MCP 工具層：暴露 System Coupling 與 TwinAI 工具。"""

from __future__ import annotations

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.products.systems.driver import SystemsDriver


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def systems_check_connection() -> dict:
    """檢查本機 ANSYS System Coupling 與 TwinAI 數位孿生求解環境可用性。"""
    driver = SystemsDriver()
    valid, message = driver.validate_prerequisites()
    return _envelope({
        "available": valid,
        "solver_bin": driver.solver_bin,
        "message": message,
    })


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def systems_solve_coupling_cht(
    t_bulk_k: float = 500.0,
    h_conv_w_m2k: float = 250.0,
    l_solid_m: float = 0.02,
    k_solid_w_mk: float = 20.0,
    t_cold_k: float = 300.0,
    use_aitken: bool = True,
    dry_run: bool = False,
) -> dict:
    """調度 ANSYS System Coupling 執行流固共軛熱傳 (CHT) 雙向聯合迭代求解。

    Args:
        t_bulk_k: 流體主流參考溫度 (Kelvin, 預設 500K)。
        h_conv_w_m2k: 對流換熱係數 h (W/(m^2*K))。
        l_solid_m: 固體壁面厚度 (m, 預設 0.02m / 20mm)。
        k_solid_w_mk: 固體導熱係數 k (W/(m*K))。
        t_cold_k: 固體外側冷卻溫度 (Kelvin, 預設 300K)。
        use_aitken: 是否啟用 Aitken 動態自適應鬆弛加速 (預設 True)。
        dry_run: 僅驗證工況參數。
    """
    if dry_run:
        return _envelope({"ok": True, "dry_run": True, "delta_t": t_bulk_k - t_cold_k})

    driver = SystemsDriver()
    result = driver.solve_coupling_cht(
        t_bulk_k=t_bulk_k,
        h_conv_w_m2k=h_conv_w_m2k,
        l_solid_m=l_solid_m,
        k_solid_w_mk=k_solid_w_mk,
        t_cold_k=t_cold_k,
        use_aitken=use_aitken,
    )
    return _envelope({"ok": True, **result})


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def systems_run_twin_rom(
    time_steps: int = 50,
    dt_s: float = 0.1,
    input_magnitude: float = 1.0,
    damping_ratio: float = 0.15,
    natural_frequency_rad_s: float = 5.0,
    dry_run: bool = False,
) -> dict:
    """調度 ANSYS TwinAI 執行 1D 狀態空間降階模型 (ROM) 數位孿生動態響應模擬。

    Args:
        time_steps: 模擬時間步數。
        dt_s: 時間步長 (seconds)。
        input_magnitude: 階躍輸入激勵幅值。
        damping_ratio: 阻尼比 zeta。
        natural_frequency_rad_s: 自然圓頻率 omega_n (rad/s)。
        dry_run: 僅驗證參數。
    """
    if dry_run:
        return _envelope({"ok": True, "dry_run": True, "total_time": time_steps * dt_s})

    driver = SystemsDriver()
    result = driver.run_twin_rom(
        time_steps=time_steps,
        dt_s=dt_s,
        input_magnitude=input_magnitude,
        damping_ratio=damping_ratio,
        natural_frequency_rad_s=natural_frequency_rad_s,
    )
    return _envelope({"ok": True, **result})
