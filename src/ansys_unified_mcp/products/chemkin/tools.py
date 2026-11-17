# -*- coding: utf-8 -*-
"""ANSYS Chemkin MCP 工具層：暴露化學反應動力學、阿瑞尼斯速率常數與等溫反應槽模擬工具。"""

from __future__ import annotations

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.products.chemkin.driver import ChemkinDriver


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def chemkin_check_connection() -> dict:
    """檢查本機 ANSYS Chemkin 化學反應動力學求解器可用性。"""
    driver = ChemkinDriver()
    valid, message = driver.validate_prerequisites()
    return _envelope({
        "available": valid,
        "solver_bin": driver.solver_bin,
        "message": message,
    })


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def chemkin_solve_0d_reactor(
    temperature_k: float = 500.0,
    a0_pre_exponential: float = 1.0e6,
    ea_activation_energy_j_mol: float = 50000.0,
    initial_ca_mol_m3: float = 1.0,
    t_end_s: float = 5.0,
    dry_run: bool = False,
) -> dict:
    """調度 ANSYS Chemkin 求解零維等溫反應槽反應動力學 (A -> B)、阿瑞尼斯速率常數與反應半衰期。

    Args:
        temperature_k: 反應槽溫度 (Kelvin, 預設 500.0 K)。
        a0_pre_exponential: 指前因子 A0 (1/s, 預設 1.0e6)。
        ea_activation_energy_j_mol: 活化能 Ea (J/mol, 預設 50000.0 J/mol)。
        initial_ca_mol_m3: 反應物 A 初始濃度 (mol/m^3)。
        t_end_s: 反應模擬時長 (s)。
        dry_run: 僅驗證參數。
    """
    if dry_run:
        return _envelope({"ok": True, "dry_run": True, "temp_k": temperature_k})

    driver = ChemkinDriver()
    result = driver.solve_batch_reactor(
        temperature_k=temperature_k,
        a0_pre_exponential=a0_pre_exponential,
        ea_activation_energy_j_mol=ea_activation_energy_j_mol,
        initial_ca_mol_m3=initial_ca_mol_m3,
        t_end_s=t_end_s,
    )
    result = driver.with_backend_metadata(result)
    return _envelope({"ok": True, **result})
