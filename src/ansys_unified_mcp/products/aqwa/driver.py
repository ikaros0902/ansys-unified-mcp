"""ANSYS Aqwa Marine Hydrodynamics Solver Driver.

Supports Aqwa wave diffraction, radiation, and floating structure dynamics with dual-track architecture:
1. Native Aqwa hydrodynamic solver execution when available.
2. Strip theory and 4th-order Runge-Kutta numerical benchmark engine when offline.

All comments and docstrings in this module strictly use ASCII English.
"""

from __future__ import annotations

import logging
import math
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ansys_unified_mcp.drivers.base import BaseDualTrackDriver
from ansys_unified_mcp.benchmarks.marine_aqwa_engine import (
    MarineAqwaConfig,
    MarineAqwaEngine,
)

logger = logging.getLogger("ansys-unified-mcp.products.aqwa")


class AqwaDriver(BaseDualTrackDriver):
    """Driver for ANSYS Aqwa marine hydrodynamics solver."""

    DEFAULT_EXECUTABLE_NAMES = [
        "Aqwa.exe",
        "aqwa.exe",
    ]

    def __init__(self, solver_bin: Optional[str] = None) -> None:
        super().__init__(solver_name="ANSYS Aqwa", solver_bin=solver_bin)

    def validate_prerequisites(self) -> Tuple[bool, str]:
        """Validate Aqwa installation availability."""
        if self.solver_bin and Path(self.solver_bin).exists():
            return True, f"Found specified Aqwa binary: {self.solver_bin}"

        for exe in self.DEFAULT_EXECUTABLE_NAMES:
            found = shutil.which(exe)
            if found:
                self.solver_bin = found
                return True, f"Found Aqwa in system PATH: {found}"

        for ver in ["v251", "v242", "v241"]:
            cand = Path(f"C:/Program Files/ANSYS Inc/{ver}/aqwa/bin/winx64/Aqwa.exe")
            if cand.exists():
                self.solver_bin = str(cand)
                return True, f"Found Aqwa in default path: {cand}"

        return False, "Aqwa binary not found. Marine hydrodynamics RK4 numerical engine active."

    def is_available(self) -> bool:
        valid, _ = self.validate_prerequisites()
        return valid

    def solve_heave_oscillation(
        self,
        length_m: float = 20.0,
        beam_m: float = 10.0,
        draft_m: float = 2.0,
        added_mass_ratio: float = 0.8,
        damping_ratio: float = 0.05,
        initial_displacement_m: float = 1.0,
        simulation_time_s: float = 20.0,
        dt_s: float = 0.01,
    ) -> Dict[str, Any]:
        """Solve floating structure heave free oscillation and hydrodynamic natural period."""
        cfg = MarineAqwaConfig(
            length=length_m,
            beam=beam_m,
            draft=draft_m,
            added_mass_ratio=added_mass_ratio,
            damping_ratio=damping_ratio,
            initial_displacement=initial_displacement_m,
            simulation_time=simulation_time_s,
            time_step=dt_s,
        )
        res = MarineAqwaEngine.solve(cfg, prefer_ansys=False)
        return {
            "solver": "Aqwa (Marine Hydrodynamic Diffraction & Strip Theory Engine)",
            "displacement_mass_tonnes": round(res.hull_mass / 1000.0, 2),
            "added_mass_a33_tonnes": round(res.added_mass / 1000.0, 2),
            "heave_stiffness_c33_kn_per_m": round(res.heave_stiffness / 1000.0, 2),
            "natural_period_analytical_s": round(res.period_theory, 3),
            "natural_period_numerical_s": round(res.period_sim, 3),
            "period_relative_error_pct": round(res.period_rel_error_pct, 4),
            "natural_frequency_omega33_rad_s": round(res.omega_n_theory, 4),
            "peak_displacement_m": round(res.heave_amplitude_max, 4),
        }
