# Strictly ASCII English Comments
"""Marine Hydrodynamics floating heave oscillation golden benchmark suite.

Validates marine hydrodynamics:
1. Floating barge heave free oscillation hydrodynamic analytical solutions.
2. Barge geometry: Length L = 20.0 m, Beam B = 10.0 m, Draft T = 2.0 m.
3. Seawater density rho = 1025.0 kg/m^3, gravity g = 9.80665 m/s^2.
4. Volume V = 400.0 m^3, Hull mass m = 410,000.0 kg.
5. Waterplane area A_w = 200.0 m^2, Stiffness K_33 = 2,010,363.25 N/m.
6. Heave added mass a_33 = 0.8 * m = 328,000.0 kg, Virtual mass M_tot = 738,000.0 kg.
7. Natural frequency omega_n = sqrt(K_33 / M_tot) = 1.6505 rad/s, Period T_n = 3.8069 s.
8. Acceptance criteria:
   - Numerical natural period relative error <= 1.5%
   - Execution time <= 8.0 seconds

All comments and docstrings in this file strictly use ASCII English.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
import math
import time
from typing import Any, Dict, Optional

import pytest

from ansys_unified_mcp.benchmarks.marine_aqwa_engine import (
    MarineAqwaConfig,
    MarineAqwaEngine,
    MarineAqwaResult,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MarineBargeSpec:
    """Floating barge geometry and hydrodynamic properties."""

    length: float = 20.0
    beam: float = 10.0
    draft: float = 2.0
    water_density: float = 1025.0
    gravity: float = 9.80665
    added_mass_ratio: float = 0.8


def compute_analytical_aqwa_baseline(spec: MarineBargeSpec) -> Dict[str, float]:
    """Calculate theoretical analytical solution for floating heave oscillation."""
    vol = spec.length * spec.beam * spec.draft
    mass = spec.water_density * vol
    area_wp = spec.length * spec.beam
    stiffness = spec.water_density * spec.gravity * area_wp
    a_33 = spec.added_mass_ratio * mass
    m_tot = mass + a_33
    omega_n = math.sqrt(stiffness / m_tot)
    period_n = 2.0 * math.pi / omega_n

    return {
        "volume": vol,
        "mass": mass,
        "area_wp": area_wp,
        "stiffness": stiffness,
        "added_mass": a_33,
        "virtual_mass": m_tot,
        "omega_n": omega_n,
        "period_n": period_n,
    }


class TestPOCMarineAqwaBenchmark:
    """Marine hydrodynamics AQWA heave benchmark verification suite."""

    def test_analytical_heave_hydrodynamics_baseline(self) -> None:
        """Verify displaced volume, stiffness, added mass, and natural period."""
        spec = MarineBargeSpec()
        theory = compute_analytical_aqwa_baseline(spec)

        # 1. Volume and mass
        assert math.isclose(theory["volume"], 400.0, rel_tol=1e-9)
        assert math.isclose(theory["mass"], 410000.0, rel_tol=1e-9)

        # 2. Waterplane area and stiffness
        assert math.isclose(theory["area_wp"], 200.0, rel_tol=1e-9)
        assert math.isclose(theory["stiffness"], 2010363.25, rel_tol=1e-7)

        # 3. Added mass and virtual mass
        assert math.isclose(theory["added_mass"], 328000.0, rel_tol=1e-9)
        assert math.isclose(theory["virtual_mass"], 738000.0, rel_tol=1e-9)

        # 4. Natural frequency and period
        assert math.isclose(theory["omega_n"], 1.6504755, rel_tol=1e-4)
        assert math.isclose(theory["period_n"], 3.806894, rel_tol=1e-4)
        assert 1.650 <= theory["omega_n"] <= 1.651
        assert 3.805 <= theory["period_n"] <= 3.808

    def test_numerical_heave_oscillation_solve_accuracy_and_timing(self) -> None:
        """Verify numerical natural period error <= 1.5% and solve time <= 8.0 s."""
        cfg = MarineAqwaConfig(
            length=20.0,
            beam=10.0,
            draft=2.0,
            water_density=1025.0,
            gravity=9.80665,
            added_mass_ratio=0.8,
            damping_ratio=0.0,
            simulation_time=30.0,
            time_step=0.002,
        )

        t_start = time.perf_counter()
        res: MarineAqwaResult = MarineAqwaEngine.solve(cfg)
        elapsed = time.perf_counter() - t_start

        # Objective criterion: Relative error <= 1.5%
        assert res.period_rel_error_pct <= 1.5, (
            f"Heave period relative error {res.period_rel_error_pct:.4f}% exceeds 1.5% limit"
        )

        # Objective criterion: Execution time <= 8.0 seconds
        assert elapsed <= 8.0, f"Solver elapsed time {elapsed:.4f}s exceeds 8.0s limit"
        assert res.solve_time_seconds <= 8.0

        # Solution quality assertions
        assert res.converged is True
        assert res.num_cycles_detected >= 5
        assert math.isclose(res.period_sim, res.period_theory, rel_tol=0.015)
        assert math.isclose(res.heave_stiffness, 2010363.25, rel_tol=1e-6)

    def test_damped_heave_decay_and_frequency_shift(self) -> None:
        """Verify damped oscillation frequency shift and amplitude decay."""
        zeta = 0.05
        cfg = MarineAqwaConfig(
            length=20.0,
            beam=10.0,
            draft=2.0,
            water_density=1025.0,
            gravity=9.80665,
            added_mass_ratio=0.8,
            damping_ratio=zeta,
            simulation_time=30.0,
            time_step=0.002,
        )

        res = MarineAqwaEngine.solve(cfg)

        omega_d_theory = res.omega_n_theory * math.sqrt(1.0 - (zeta ** 2))
        period_d_theory = 2.0 * math.pi / omega_d_theory

        rel_error = abs(res.period_sim - period_d_theory) / period_d_theory * 100.0
        assert rel_error <= 1.5, f"Damped period relative error {rel_error:.4f}% exceeds 1.5%"
        assert math.isclose(res.heave_amplitude_max, 1.0, rel_tol=1e-3)

    def test_marine_aqwa_dual_track_resilience(self) -> None:
        """Verify dual-track graceful fallback when native AQWA is offline."""
        cfg = MarineAqwaConfig()
        res = MarineAqwaEngine.solve(cfg, prefer_ansys=True)

        assert res.solver_mode in ["ansys_aqwa", "strip_theory_rk4_engine"]
        assert res.converged is True
        assert res.period_rel_error_pct <= 1.5
        assert res.virtual_mass == 738000.0
