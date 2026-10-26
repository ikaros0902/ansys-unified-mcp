# Strictly ASCII English Comments
"""Chemkin 0D reaction kinetics golden benchmark test suite.

Validates chemical kinetics:
1. 0D isothermal homogeneous batch reactor first-order irreversible reaction A -> B.
2. Arrhenius rate constant k = A0 * exp(-Ea / (R * T)).
3. Analytical solutions CA(t) = CA0 * exp(-k * t) and half-life t_half = ln(2) / k.
4. Acceptance criteria:
   - Concentration relative error <= 0.5%
   - Half-life relative error <= 0.1%
   - Mass conservation error <= 1e-6 mol/m^3
   - Execution time <= 5.0 seconds
"""

from __future__ import annotations

import logging
import math
import time
from typing import Any, Dict

import pytest

from ansys_unified_mcp.benchmarks.chemkin_reaction_engine import (
    ChemkinReactionConfig,
    ChemkinReactionEngine,
    ChemkinReactionResult,
)

logger = logging.getLogger(__name__)


class TestPOCChemkinReactionBenchmark:
    """Chemkin 0D reaction kinetics golden benchmark suite."""

    def test_analytical_arrhenius_and_halflife_exactness(self) -> None:
        """Verify Arrhenius rate constant and half-life analytical accuracy."""
        ea = 50000.0
        r_const = 8.314462
        temp = 500.0

        # Case 1: Standard A0 = 1.0e6 1/s
        a0_std = 1.0e6
        k_std = a0_std * math.exp(-ea / (r_const * temp))
        t_half_std = math.log(2.0) / k_std
        assert abs(k_std - 5.9791245) < 1e-4, f"A0=1e6 rate constant mismatch: {k_std}"
        assert abs(t_half_std - 0.1159275) < 1e-5, f"A0=1e6 half-life mismatch: {t_half_std}"

        # Case 2: Nominal A0 = 1.0e5 1/s
        a0_nom = 1.0e5
        k_nom = a0_nom * math.exp(-ea / (r_const * temp))
        t_half_nom = math.log(2.0) / k_nom
        assert abs(k_nom - 0.59791245) < 1e-4, f"A0=1e5 rate constant mismatch: {k_nom}"
        assert abs(t_half_nom - 1.1592757) < 1e-4, f"A0=1e5 half-life mismatch: {t_half_nom}"

        # Verify engine helper on both configurations
        cfg_std = ChemkinReactionConfig(A0=a0_std, Ea=ea, R=r_const, temperature=temp)
        res_std = ChemkinReactionEngine.compute_analytical_solution(cfg_std)
        assert abs(res_std["rate_constant_k"] - k_std) < 1e-12
        assert abs(res_std["t_half_theory"] - t_half_std) < 1e-12

        cfg_nom = ChemkinReactionConfig(A0=a0_nom, Ea=ea, R=r_const, temperature=temp)
        res_nom = ChemkinReactionEngine.compute_analytical_solution(cfg_nom)
        assert abs(res_nom["rate_constant_k"] - k_nom) < 1e-12
        assert abs(res_nom["t_half_theory"] - t_half_nom) < 1e-12

    def test_numerical_rk4_accuracy_and_performance(self) -> None:
        """Verify RK4 numerical solver accuracy and execution performance."""
        config = ChemkinReactionConfig(
            A0=1.0e6,
            Ea=50000.0,
            R=8.314462,
            temperature=500.0,
            ca0=1.0,
            cb0=0.0,
            t_end=5.0,
            dt=0.005,
        )

        start = time.perf_counter()
        result = ChemkinReactionEngine.solve_rk4(config)
        elapsed = time.perf_counter() - start

        logger.info(
            "Chemkin solve complete: k=%.6f 1/s, t_half_sim=%.6f s, CA_err=%.4f%%, CB_err=%.4f%%, time=%.4f s",
            result.rate_constant_k,
            result.t_half_sim,
            result.max_ca_rel_error_pct,
            result.max_cb_rel_error_pct,
            result.solve_time_seconds,
        )

        # 1. Concentration relative error <= 0.5%
        assert result.max_ca_rel_error_pct <= 0.5, (
            f"CA error exceeds 0.5%: {result.max_ca_rel_error_pct:.6f}%"
        )
        assert result.max_cb_rel_error_pct <= 0.5, (
            f"CB error exceeds 0.5%: {result.max_cb_rel_error_pct:.6f}%"
        )

        # 2. Half-life relative error <= 0.1%
        assert result.t_half_rel_error_pct <= 0.1, (
            f"Half-life error exceeds 0.1%: {result.t_half_rel_error_pct:.6f}%"
        )

        # 3. Mass conservation error <= 1e-6 mol/m^3
        assert result.mass_conservation_max_error <= 1e-6, (
            f"Mass conservation error exceeds 1e-6: {result.mass_conservation_max_error:.2e}"
        )

        # 4. Solve time <= 5.0 seconds
        assert result.solve_time_seconds <= 5.0, (
            f"Solve time exceeds 5.0 s: {result.solve_time_seconds:.4f} s"
        )
        assert elapsed <= 5.0

        # 5. Convergence flag
        assert result.converged is True

    def test_nominal_operating_point_half_life(self) -> None:
        """Verify nominal operating point numerical accuracy."""
        config = ChemkinReactionConfig(
            A0=1.0e5,
            Ea=50000.0,
            R=8.314462,
            temperature=500.0,
            ca0=1.0,
            cb0=0.0,
            t_end=5.0,
            dt=0.005,
        )

        result = ChemkinReactionEngine.solve_rk4(config)

        assert abs(result.rate_constant_k - 0.59791245) < 1e-4
        assert abs(result.t_half_theory - 1.1592757) < 1e-4
        assert abs(result.t_half_sim - 1.1592757) < 1e-3

        assert result.max_ca_rel_error_pct <= 0.5
        assert result.max_cb_rel_error_pct <= 0.5
        assert result.t_half_rel_error_pct <= 0.1
        assert result.solve_time_seconds <= 5.0

    def test_engine_dual_track_and_package_integration(self) -> None:
        """Verify ChemkinReactionEngine.solve() dual-track dispatch and integration."""
        config = ChemkinReactionConfig()
        result = ChemkinReactionEngine.solve(config, prefer_ansys=True)

        assert isinstance(result, ChemkinReactionResult)
        assert result.converged is True
        assert len(result.time_points) > 10
        assert len(result.ca_sim_profile) == len(result.time_points)
        assert len(result.cb_sim_profile) == len(result.time_points)

        k = result.rate_constant_k
        expected_final_ca = 1.0 * math.exp(-k * 5.0)
        assert abs(result.ca_sim_profile[-1] - expected_final_ca) < 1e-3

    def test_time_step_refinement_monotonicity(self) -> None:
        """Verify monotonic convergence as time step dt is refined."""
        dt_coarse = 0.05
        dt_medium = 0.01
        dt_fine = 0.002

        res_coarse = ChemkinReactionEngine.solve_rk4(
            ChemkinReactionConfig(dt=dt_coarse, t_end=3.0)
        )
        res_medium = ChemkinReactionEngine.solve_rk4(
            ChemkinReactionConfig(dt=dt_medium, t_end=3.0)
        )
        res_fine = ChemkinReactionEngine.solve_rk4(
            ChemkinReactionConfig(dt=dt_fine, t_end=3.0)
        )

        assert res_medium.max_ca_rel_error_pct <= res_coarse.max_ca_rel_error_pct
        assert res_fine.max_ca_rel_error_pct <= res_medium.max_ca_rel_error_pct
        assert res_fine.t_half_rel_error_pct <= res_coarse.t_half_rel_error_pct

    def test_input_validation_boundary_conditions(self) -> None:
        """Verify input boundary conditions and exception handling."""
        with pytest.raises(ValueError, match="Temperature"):
            ChemkinReactionEngine.compute_rate_constant(1.0e6, 50000.0, 8.314462, 0.0)

        with pytest.raises(ValueError, match="Time step"):
            ChemkinReactionEngine.solve_rk4(ChemkinReactionConfig(dt=-0.01))

        with pytest.raises(ValueError, match="End time"):
            ChemkinReactionEngine.solve_rk4(ChemkinReactionConfig(t_end=-1.0))
