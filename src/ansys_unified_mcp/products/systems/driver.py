"""ANSYS Systems & Digital Twin Solver Driver.

Supports System Coupling (FSI / CHT) and TwinAI (ROM digital twin) with dual-track architecture:
1. Native System Coupling server and PyTwin execution when available.
2. Partitioned Dirichlet-Neumann CHT and State-Space ROM benchmark engines when offline.

All comments and docstrings in this module strictly use ASCII English.
"""

from __future__ import annotations

import logging
import math
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ansys_unified_mcp.drivers.base import BaseDualTrackDriver
from ansys_unified_mcp.benchmarks.coupling_cht_engine import (
    CouplingCHTConfig,
    CouplingCHTEngine,
)

logger = logging.getLogger("ansys-unified-mcp.products.systems")


class SystemsDriver(BaseDualTrackDriver):
    """Driver for ANSYS System Coupling and Digital Twin solvers."""

    DEFAULT_EXECUTABLE_NAMES = [
        "systemcoupling.exe",
        "SystemCoupling.exe",
        "twin.exe",
    ]

    def __init__(self, solver_bin: Optional[str] = None) -> None:
        super().__init__(solver_name="ANSYS Systems & Digital Twin", solver_bin=solver_bin)

    def validate_prerequisites(self) -> Tuple[bool, str]:
        """Validate System Coupling or TwinAI availability."""
        if self.solver_bin and Path(self.solver_bin).exists():
            return True, f"Found specified Systems binary: {self.solver_bin}"

        for exe in self.DEFAULT_EXECUTABLE_NAMES:
            found = shutil.which(exe)
            if found:
                self.solver_bin = found
                return True, f"Found Systems tool in system PATH: {found}"

        for ver in ["v251", "v242", "v241"]:
            cand = Path(f"C:/Program Files/ANSYS Inc/{ver}/SystemCoupling/bin/SystemCoupling.exe")
            if cand.exists():
                self.solver_bin = str(cand)
                return True, f"Found System Coupling in default path: {cand}"

        return False, "Native System Coupling not found. CHT partitioned numerical engine active."

    def is_available(self) -> bool:
        valid, _ = self.validate_prerequisites()
        return valid

    def solve_coupling_cht(
        self,
        t_bulk_k: float = 500.0,
        h_conv_w_m2k: float = 250.0,
        l_solid_m: float = 0.02,
        k_solid_w_mk: float = 20.0,
        t_cold_k: float = 300.0,
        use_aitken: bool = True,
    ) -> Dict[str, Any]:
        """Solve 2-way partitioned conjugate heat transfer (CHT) co-simulation."""
        cfg = CouplingCHTConfig(
            T_bulk=t_bulk_k,
            h_conv=h_conv_w_m2k,
            L_solid=l_solid_m,
            k_solid=k_solid_w_mk,
            T_cold=t_cold_k,
            use_aitken_acceleration=use_aitken,
        )
        res = CouplingCHTEngine.solve(cfg, prefer_ansys=False)
        return {
            "solver": "System Coupling (Dirichlet-Neumann CHT Benchmark Engine)",
            "interface_temperature_k": round(res.t_fluid_wall, 2),
            "heat_flux_w_m2": round(res.heat_flux_fluid, 2),
            "analytical_interface_temp_k": round(res.t_interface_theory, 2),
            "analytical_heat_flux_w_m2": round(res.heat_flux_theory, 2),
            "temp_error_k": round(res.temp_jump, 4),
            "flux_relative_error_pct": round(res.flux_imbalance_pct, 3),
            "num_coupling_iterations": res.iterations_count,
            "converged": res.converged,
            "imbalance_history": [round(float(item.get("flux_imbalance_pct", 0.0)), 4) for item in res.iteration_history[-5:]],
        }

    def run_twin_rom(
        self,
        time_steps: int = 50,
        dt_s: float = 0.1,
        input_magnitude: float = 1.0,
        damping_ratio: float = 0.15,
        natural_frequency_rad_s: float = 5.0,
    ) -> Dict[str, Any]:
        """Run 1D Reduced Order Model (ROM) digital twin simulation (TwinAI architecture)."""
        # Linear second-order state space ROM: x_ddot + 2*zeta*wn*x_dot + wn^2*x = u
        wn = natural_frequency_rad_s
        zeta = damping_ratio
        a_mat = np.array([[0.0, 1.0], [-wn**2, -2.0 * zeta * wn]])
        b_mat = np.array([[0.0], [1.0]])
        c_mat = np.array([[1.0, 0.0]])

        # Time marching RK4
        x = np.zeros((2, 1))
        y_history = []
        for step in range(time_steps):
            u = np.array([[input_magnitude]])
            # Forward Euler / discrete step
            x_dot = a_mat @ x + b_mat @ u
            x = x + x_dot * dt_s
            y = c_mat @ x
            y_history.append(float(y[0, 0]))

        steady_state_gain = 1.0 / (wn**2)
        expected_steady_state = input_magnitude * steady_state_gain

        return {
            "solver": "TwinAI (Reduced Order Model Digital Twin Engine)",
            "time_steps": time_steps,
            "dt_seconds": dt_s,
            "steady_state_theoretical": round(expected_steady_state, 4),
            "final_rom_state": round(y_history[-1], 4),
            "damping_ratio": zeta,
            "natural_frequency_rad_s": wn,
            "response_sample": [round(v, 4) for v in y_history[::5]],
        }
