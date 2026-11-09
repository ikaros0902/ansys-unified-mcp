"""ANSYS Sherlock Electronics Reliability Solver Driver.

Supports Sherlock Physics of Failure (PoF) life prediction with dual-track architecture:
1. Native Sherlock desktop batch and PySherlock gRPC execution when installed.
2. Engelmaier solder fatigue and Steinberg 3-band random vibration models when offline.

All comments and docstrings in this module strictly use ASCII English.
"""

from __future__ import annotations

import logging
import math
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ansys_unified_mcp.drivers.base import BaseDualTrackDriver

logger = logging.getLogger("ansys-unified-mcp.products.sherlock")


class SherlockDriver(BaseDualTrackDriver):
    """Driver for ANSYS Sherlock electronics reliability analysis."""

    DEFAULT_EXECUTABLE_NAMES = [
        "Sherlock.exe",
        "sherlock.exe",
    ]

    def __init__(self, solver_bin: Optional[str] = None) -> None:
        super().__init__(solver_name="ANSYS Sherlock", solver_bin=solver_bin)

    def validate_prerequisites(self) -> Tuple[bool, str]:
        """Validate Sherlock installation availability."""
        if self.solver_bin and Path(self.solver_bin).exists():
            return True, f"Found specified Sherlock binary: {self.solver_bin}"

        for exe in self.DEFAULT_EXECUTABLE_NAMES:
            found = shutil.which(exe)
            if found:
                self.solver_bin = found
                return True, f"Found Sherlock in system PATH: {found}"

        for ver in ["v251", "v242", "v241"]:
            cand = Path(f"C:/Program Files/ANSYS Inc/{ver}/sherlock/bin/Sherlock.exe")
            if cand.exists():
                self.solver_bin = str(cand)
                return True, f"Found Sherlock in default path: {cand}"

        return False, "Sherlock binary not found. PoF reliability physics engine active."

    def is_available(self) -> bool:
        valid, _ = self.validate_prerequisites()
        return valid

    def calculate_solder_thermal_fatigue(
        self,
        delta_t_c: float = 80.0,
        t_mean_c: float = 40.0,
        package_diagonal_mm: float = 25.0,
        solder_joint_height_mm: float = 0.25,
        delta_cte_ppm: float = 12.0,
        dwell_time_minutes: float = 15.0,
    ) -> Dict[str, Any]:
        """Calculate BGA solder joint thermal cycling fatigue life (Engelmaier-Wild model)."""
        ld = (package_diagonal_mm / 2.0) * 1e-3
        h = solder_joint_height_mm * 1e-3
        delta_alpha = delta_cte_ppm * 1e-6
        delta_t = max(delta_t_c, 1.0)
        td = max(dwell_time_minutes, 1.0)

        # Cyclic shear strain range delta gamma = (Ld * delta_alpha * delta_T) / (2 * h)
        delta_gamma = (ld * delta_alpha * delta_t) / (2.0 * h)

        # Fatigue ductility exponent c (Engelmaier empirical correlation for SAC / SnPb)
        c_exp = -0.442 - 6e-4 * t_mean_c + 1.74e-2 * math.log(1.0 + 360.0 / td)

        # Fatigue ductility coefficient epsilon_f_prime
        eps_f = 0.325

        # Number of cycles to 50% failure: N_f = 0.5 * (delta_gamma / (2 * eps_f))^(1 / c_exp)
        if delta_gamma > 1e-6 and abs(c_exp) > 1e-4:
            n_f_50 = 0.5 * ((delta_gamma / (2.0 * eps_f)) ** (1.0 / c_exp))
        else:
            n_f_50 = 1e6

        # Characteristic Weibull 63.2% life N_63 = N_50 / (ln(2))^(1/beta), beta ~ 2.6
        beta = 2.6
        n_63 = n_f_50 / (math.log(2.0) ** (1.0 / beta))
        # 1% early failure life
        n_01 = n_63 * ((-math.log(0.99)) ** (1.0 / beta))

        return {
            "solver": "Sherlock (Engelmaier Solder Thermal Fatigue PoF Engine)",
            "cyclic_shear_strain_range": round(delta_gamma, 5),
            "fatigue_ductility_exponent": round(c_exp, 4),
            "median_cycles_to_failure_n50": int(n_f_50),
            "characteristic_life_weibull_n63": int(n_63),
            "early_failure_1pct_cycles": int(n_01),
            "weibull_slope_beta": beta,
            "pass_automotive_1000_cycles": n_01 >= 1000,
        }

    def calculate_vibration_fatigue(
        self,
        g_rms: float = 5.0,
        pcb_natural_freq_hz: float = 120.0,
        transmissibility_q: float = 10.0,
        lead_wire_diameter_mm: float = 0.5,
    ) -> Dict[str, Any]:
        """Calculate random vibration component lead fatigue life (Steinberg 3-band model)."""
        fn = max(pcb_natural_freq_hz, 1.0)
        q = max(transmissibility_q, 1.0)

        # 3-sigma maximum dynamic displacement Z_3sigma (mm) = (9.8 * g_rms * sqrt(Q)) / (4 * pi^2 * fn^2) * 1000 * 3
        z_rms_mm = (9.80665 * g_rms * math.sqrt(math.pi / 2.0 * q)) / (4.0 * (math.pi**2) * (fn**2)) * 1000.0
        z_3sigma_mm = 3.0 * z_rms_mm

        # Component lead stress amplitude estimation based on Steinberg lead deflection
        lead_d_m = lead_wire_diameter_mm * 1e-3
        lead_len_m = 0.003  # 3 mm typical lead span
        # Lead compliance factor: gull-wing/J-lead geometry absorbs ~99.2% of displacement
        z_rel_m = (z_3sigma_mm * 1e-3) * 0.008
        e_copper_pa = 1.1e11  # Copper elastic modulus 110 GPa
        stress_3sigma_mpa = (3.0 * e_copper_pa * (lead_d_m / 2.0) * z_rel_m) / (lead_len_m**2) * 1e-6
        stress_3sigma_mpa = max(stress_3sigma_mpa, 5.0)

        # Miner's cumulative damage D per hour (1-sigma 68.3%, 2-sigma 27.1%, 3-sigma 4.33%)
        cycles_per_hour = fn * 3600.0
        # Basquin S-N curve: N * S^b = C, with b ~ 6.4 for copper leads
        b_exp = 6.4
        c_const = 1e18
        n1 = c_const / max((stress_3sigma_mpa / 3.0)**b_exp, 1.0)
        n2 = c_const / max((stress_3sigma_mpa * 2.0 / 3.0)**b_exp, 1.0)
        n3 = c_const / max(stress_3sigma_mpa**b_exp, 1.0)

        damage_per_hour = cycles_per_hour * (0.683 / n1 + 0.271 / n2 + 0.0433 / n3)
        time_to_failure_hours = round(1.0 / max(damage_per_hour, 1e-12), 2)

        return {
            "solver": "Sherlock (Steinberg 3-Band Random Vibration PoF Engine)",
            "pcb_natural_freq_hz": fn,
            "transmissibility_q": q,
            "pcb_z_rms_disp_mm": round(z_rms_mm, 4),
            "pcb_z_3sigma_disp_mm": round(z_3sigma_mm, 4),
            "peak_lead_stress_3sigma_mpa": round(stress_3sigma_mpa, 2),
            "vibration_life_hours": min(time_to_failure_hours, 100000.0),
            "pass_mil_std_810_20_hours": time_to_failure_hours >= 20.0,
        }
