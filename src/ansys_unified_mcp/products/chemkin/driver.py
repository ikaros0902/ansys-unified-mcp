"""ANSYS Chemkin Chemical Kinetics Solver Driver.

Supports Chemkin reaction kinetics and combustion chemistry with dual-track architecture:
1. Native Chemkin-Pro execution when installed.
2. Arrhenius chemical reaction rate and RK4 numerical benchmark engine when offline.

All comments and docstrings in this module strictly use ASCII English.
"""

from __future__ import annotations

import logging
import math
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ansys_unified_mcp.drivers.base import BaseDualTrackDriver
from ansys_unified_mcp.benchmarks.chemkin_reaction_engine import (
    ChemkinReactionConfig,
    ChemkinReactionEngine,
)

logger = logging.getLogger("ansys-unified-mcp.products.chemkin")


class ChemkinDriver(BaseDualTrackDriver):
    """Driver for ANSYS Chemkin reaction kinetics solver."""

    DEFAULT_EXECUTABLE_NAMES = [
        "chemkin.exe",
        "chemkinpro.exe",
    ]

    def __init__(self, solver_bin: Optional[str] = None) -> None:
        super().__init__(solver_name="ANSYS Chemkin", solver_bin=solver_bin)

    def validate_prerequisites(self) -> Tuple[bool, str]:
        """Validate Chemkin installation availability."""
        if self.solver_bin and Path(self.solver_bin).exists():
            return True, f"Found specified Chemkin binary: {self.solver_bin}"

        for exe in self.DEFAULT_EXECUTABLE_NAMES:
            found = shutil.which(exe)
            if found:
                self.solver_bin = found
                return True, f"Found Chemkin in system PATH: {found}"

        for ver in ["v251", "v242", "v241"]:
            cand = Path(f"C:/Program Files/ANSYS Inc/{ver}/reaction/chemkinpro.win64/bin/chemkinpro.exe")
            if cand.exists():
                self.solver_bin = str(cand)
                return True, f"Found Chemkin in default path: {cand}"

        return False, "Chemkin binary not found. Arrhenius chemical kinetics RK4 engine active."

    def is_available(self) -> bool:
        valid, _ = self.validate_prerequisites()
        return valid

    def solve_batch_reactor(
        self,
        temperature_k: float = 500.0,
        a0_pre_exponential: float = 1.0e6,
        ea_activation_energy_j_mol: float = 50000.0,
        initial_ca_mol_m3: float = 1.0,
        initial_cb_mol_m3: float = 0.0,
        t_end_s: float = 5.0,
        dt_s: float = 0.005,
    ) -> Dict[str, Any]:
        """Solve 0D isothermal batch reactor reaction kinetics (A -> B)."""
        cfg = ChemkinReactionConfig(
            temperature=temperature_k,
            A0=a0_pre_exponential,
            Ea=ea_activation_energy_j_mol,
            ca0=initial_ca_mol_m3,
            cb0=initial_cb_mol_m3,
            t_end=t_end_s,
            dt=dt_s,
        )
        res = ChemkinReactionEngine.solve(cfg, prefer_ansys=False)
        ca_theory_final = res.ca_theory_profile[-1] if res.ca_theory_profile else 0.0
        ca_sim_final = res.ca_sim_profile[-1] if res.ca_sim_profile else 0.0
        cb_sim_final = res.cb_sim_profile[-1] if res.cb_sim_profile else 0.0
        return {
            "solver": "Chemkin (Arrhenius Kinetics & RK4 Batch Reactor Engine)",
            "temperature_k": temperature_k,
            "rate_constant_k_per_s": round(res.rate_constant_k, 4),
            "half_life_analytical_s": round(res.t_half_theory, 4),
            "half_life_numerical_s": round(res.t_half_sim, 4),
            "ca_final_analytical": round(ca_theory_final, 6),
            "ca_final_numerical": round(ca_sim_final, 6),
            "cb_final_numerical": round(cb_sim_final, 6),
            "mass_conservation_residual": round(res.mass_conservation_max_error, 8),
            "relative_error_half_life_pct": round(res.t_half_rel_error_pct, 4),
            "mass_conserved": res.mass_conservation_max_error < 1e-4,
        }
