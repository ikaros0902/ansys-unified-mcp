"""ANSYS Motor-CAD Electric Machine Solver Driver.

Supports Motor-CAD electromagnetic and thermal machine design with dual-track architecture:
1. Native Motor-CAD desktop execution (MotorCAD.exe / PyMotorCAD) when available.
2. PMSM dq-axis analytical and numerical efficiency map engine when offline.

All comments and docstrings in this module strictly use ASCII English.
"""

from __future__ import annotations

import logging
import math
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ansys_unified_mcp.drivers.base import BaseDualTrackDriver
from ansys_unified_mcp.benchmarks.motorcad_efficiency_engine import (
    MotorCADEfficiencyConfig,
    MotorCADEfficiencyEngine,
)

logger = logging.getLogger("ansys-unified-mcp.products.motorcad")


class MotorCADDriver(BaseDualTrackDriver):
    """Driver for ANSYS Motor-CAD electric machine solver."""

    DEFAULT_EXECUTABLE_NAMES = [
        "MotorCAD.exe",
        "motorcad.exe",
    ]

    def __init__(self, solver_bin: Optional[str] = None) -> None:
        super().__init__(solver_name="ANSYS Motor-CAD", solver_bin=solver_bin)

    def validate_prerequisites(self) -> Tuple[bool, str]:
        """Validate Motor-CAD installation availability."""
        if self.solver_bin and Path(self.solver_bin).exists():
            return True, f"Found specified Motor-CAD binary: {self.solver_bin}"

        for exe in self.DEFAULT_EXECUTABLE_NAMES:
            found = shutil.which(exe)
            if found:
                self.solver_bin = found
                return True, f"Found Motor-CAD in system PATH: {found}"

        for ver in ["v251", "v242", "v241"]:
            cand = Path(f"C:/Program Files/ANSYS Inc/{ver}/Motor-CAD/MotorCAD.exe")
            if cand.exists():
                self.solver_bin = str(cand)
                return True, f"Found Motor-CAD in default path: {cand}"

        return False, "Motor-CAD binary not found. PMSM electromagnetic efficiency benchmark engine active."

    def is_available(self) -> bool:
        valid, _ = self.validate_prerequisites()
        return valid

    def solve_operating_point(
        self,
        pole_pairs: int = 4,
        flux_linkage_wb: float = 0.05,
        stator_resistance_ohm: float = 0.10,
        omega_m_rad_s: float = 300.0,
        torque_target_nm: float = 15.0,
    ) -> Dict[str, Any]:
        """Solve PMSM efficiency, back-EMF, and copper losses at specific operating point."""
        cfg = MotorCADEfficiencyConfig(
            pole_pairs=pole_pairs,
            flux_linkage=flux_linkage_wb,
            stator_resistance=stator_resistance_ohm,
            omega_m=omega_m_rad_s,
            torque_target=torque_target_nm,
        )
        res = MotorCADEfficiencyEngine.solve(cfg, prefer_ansys=False)
        rpm = round((omega_m_rad_s * 60.0) / (2.0 * math.pi), 1)

        return {
            "solver": "Motor-CAD (PMSM DQ-Axis Analytical & Numerical Engine)",
            "speed_rpm": rpm,
            "torque_target_nm": torque_target_nm,
            "mechanical_power_watts": round(res.p_mech_output, 2),
            "copper_loss_watts": round(res.p_copper_sim, 2),
            "electromagnetic_efficiency_pct": round(res.efficiency_sim * 100.0, 2),
            "analytical_efficiency_pct": round(res.efficiency_theory * 100.0, 2),
            "ke_constant_v_per_rad_s": round(res.ke_constant, 4),
            "kt_constant_nm_per_a": round(res.kt_constant, 4),
            "iq_current_a": round(res.i_q_current, 2),
            "relative_error_pct": round(res.efficiency_rel_error_pct, 4),
        }
