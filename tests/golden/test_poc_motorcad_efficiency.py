# Strictly ASCII English Comments
"""Motor-CAD PMSM back-EMF, torque constant, and copper loss efficiency golden benchmark suite.

Validates permanent magnet synchronous motor efficiency:
1. Pole pairs p = 4, flux linkage psi_m = 0.05 Wb, stator resistance Rs = 0.10 Ohm.
2. Back-EMF constant Ke = sqrt(3) * p * psi_m = 0.34641 V/(rad/s).
3. Torque constant Kt = 1.5 * p * psi_m = 0.30000 N*m/A.
4. Rated operating point: omega_m = 300.0 rad/s (approx 2865 RPM), Tem = 15.0 N*m.
5. Copper loss P_cu = 3 * (Irms^2) * Rs = 375.0 W.
6. Mechanical power P_mech = 4500.0 W, electrical power P_elec = 4875.0 W.
7. Ideal efficiency eta = 4500 / 4875 = 0.923077 (92.31%).
8. Acceptance criteria:
   - Torque constant error <= 0.5%
   - Copper loss error <= 0.5%
   - Efficiency relative error <= 1.0%
   - Execution time <= 6.0 seconds

All comments and docstrings in this file strictly use ASCII English.
"""

from __future__ import annotations

import logging
import math
import time
from typing import Any, Dict

import pytest

from ansys_unified_mcp.benchmarks.motorcad_efficiency_engine import (
    MotorCADEfficiencyConfig,
    MotorCADEfficiencyEngine,
    MotorCADEfficiencyResult,
)

logger = logging.getLogger(__name__)


class TestPOCMotorCADEfficiencyBenchmark:
    """Motor-CAD PMSM efficiency and loss golden benchmark test suite."""

    def test_analytical_constants_and_efficiency_exactness(self) -> None:
        """Verify PMSM back-EMF, torque constant, copper loss, and efficiency exactness."""
        p = 4
        psi_m = 0.05
        rs = 0.10
        omega_m = 300.0
        target_torque = 15.0

        # 1. Back-EMF constant Ke: sqrt(3) * p * psi_m
        ke_expected = math.sqrt(3.0) * p * psi_m
        assert abs(ke_expected - 0.3464101615) < 1e-6, f"Ke constant deviation: {ke_expected}"

        # 2. Torque constant Kt: 1.5 * p * psi_m
        kt_expected = 1.5 * p * psi_m
        assert abs(kt_expected - 0.300000) < 1e-6, f"Kt constant deviation: {kt_expected}"

        # 3. Peak q-axis current: Iq = Tem / Kt = 15 / 0.3 = 50 A
        iq_expected = target_torque / kt_expected
        assert abs(iq_expected - 50.0) < 1e-6, f"Iq current deviation: {iq_expected}"

        # 4. Phase RMS current: Irms = Iq / sqrt(2)
        i_rms_expected = iq_expected / math.sqrt(2.0)
        assert abs(i_rms_expected - 35.355339) < 1e-4, f"Irms current deviation: {i_rms_expected}"

        # 5. Copper loss: 3 * (Irms^2) * Rs = 3 * 1250 * 0.1 = 375 W
        p_cu_expected = 3.0 * (i_rms_expected ** 2) * rs
        assert abs(p_cu_expected - 375.0) < 1e-5, f"Copper loss deviation: {p_cu_expected}"

        # 6. Mechanical power: Tem * omega_m = 15 * 300 = 4500 W
        p_mech_expected = target_torque * omega_m
        assert abs(p_mech_expected - 4500.0) < 1e-6, f"Mechanical power deviation: {p_mech_expected}"

        # 7. Total electrical power: 4500 + 375 = 4875 W
        p_elec_expected = p_mech_expected + p_cu_expected
        assert abs(p_elec_expected - 4875.0) < 1e-5, f"Input electrical power deviation: {p_elec_expected}"

        # 8. Ideal electromagnetic efficiency: 4500 / 4875 = 12 / 13 approx 0.9230769
        eta_expected = p_mech_expected / p_elec_expected
        assert abs(eta_expected - 0.92307692) < 1e-6, f"Theoretical efficiency deviation: {eta_expected}"

        config = MotorCADEfficiencyConfig(
            pole_pairs=p,
            flux_linkage=psi_m,
            stator_resistance=rs,
            omega_m=omega_m,
            torque_target=target_torque,
        )
        analytical = MotorCADEfficiencyEngine.compute_analytical_solution(config)
        assert abs(analytical["ke_constant"] - ke_expected) < 1e-12
        assert abs(analytical["kt_constant"] - kt_expected) < 1e-12
        assert abs(analytical["p_copper"] - 375.0) < 1e-12
        assert abs(analytical["p_mech"] - 4500.0) < 1e-12
        assert abs(analytical["efficiency"] - eta_expected) < 1e-12

    def test_numerical_simulation_accuracy_and_performance(self) -> None:
        """Verify time-domain numerical integration accuracy and timing SLA."""
        config = MotorCADEfficiencyConfig(
            pole_pairs=4,
            flux_linkage=0.05,
            stator_resistance=0.10,
            omega_m=300.0,
            torque_target=15.0,
            num_time_samples=360,
        )

        start = time.perf_counter()
        result = MotorCADEfficiencyEngine.solve_numerical(config)
        elapsed = time.perf_counter() - start

        logger.info(
            "Motor-CAD solve complete: Ke=%.5f, Kt=%.4f, P_cu=%.2f W, P_mech=%.2f W, eta=%.4f, time=%.4f s",
            result.ke_constant,
            result.kt_constant,
            result.p_copper_sim,
            result.p_mech_output,
            result.efficiency_sim,
            result.solve_time_seconds,
        )

        # 1. Torque constant error <= 0.5%
        assert result.kt_rel_error_pct <= 0.5, (
            f"Torque constant error exceeds 0.5%: {result.kt_rel_error_pct:.4f}%"
        )

        # 2. Copper loss error <= 0.5%
        assert result.p_copper_rel_error_pct <= 0.5, (
            f"Copper loss error exceeds 0.5%: {result.p_copper_rel_error_pct:.4f}%"
        )
        assert abs(result.p_copper_sim - 375.0) < 1e-4

        # 3. Efficiency relative error <= 1.0%
        assert result.efficiency_rel_error_pct <= 1.0, (
            f"Efficiency relative error exceeds 1.0%: {result.efficiency_rel_error_pct:.4f}%"
        )
        assert abs(result.efficiency_sim - 0.9230769) < 1e-4

        # 4. Torque tracking error <= 0.5%
        assert result.torque_rel_error_pct <= 0.5, (
            f"Torque tracking error exceeds 0.5%: {result.torque_rel_error_pct:.4f}%"
        )

        # 5. Solve time <= 6.0 seconds
        assert result.solve_time_seconds <= 6.0, (
            f"Solve time exceeds 6.0 s: {result.solve_time_seconds:.4f} s"
        )
        assert elapsed <= 6.0

        # 6. Numerical convergence
        assert result.converged is True

    def test_efficiency_map_multi_point_sweep(self) -> None:
        """Verify operating map multi-point sweep functionality."""
        speeds = [100.0, 200.0, 300.0, 400.0]
        torques = [5.0, 10.0, 15.0, 20.0]

        base_config = MotorCADEfficiencyConfig(
            pole_pairs=4,
            flux_linkage=0.05,
            stator_resistance=0.10,
        )

        start = time.perf_counter()
        map_results = MotorCADEfficiencyEngine.solve_efficiency_map(
            speed_range=speeds,
            torque_range=torques,
            base_config=base_config,
        )
        sweep_elapsed = time.perf_counter() - start

        assert len(map_results) == len(speeds) * len(torques)
        assert sweep_elapsed <= 6.0, f"Multi-point sweep timeout: {sweep_elapsed:.2f} s"

        t15_results = [r for r in map_results if abs(r.torque_sim - 15.0) < 0.1]
        for i in range(len(t15_results) - 1):
            assert t15_results[i + 1].efficiency_sim > t15_results[i].efficiency_sim

    def test_engine_dual_track_and_package_integration(self) -> None:
        """Verify MotorCADEfficiencyEngine.solve() dual-track dispatch and integration."""
        config = MotorCADEfficiencyConfig()
        result = MotorCADEfficiencyEngine.solve(config, prefer_ansys=True)

        assert isinstance(result, MotorCADEfficiencyResult)
        assert result.converged is True
        assert abs(result.ke_constant - 0.34641016) < 1e-4
        assert abs(result.kt_constant - 0.30000) < 1e-4
        assert abs(result.efficiency_sim - 0.9230769) < 1e-4

    def test_input_validation_boundary_conditions(self) -> None:
        """Verify motor parameter boundary validation and exception defense."""
        with pytest.raises(ValueError, match="Pole pairs"):
            MotorCADEfficiencyEngine.compute_kt_constant(0, 0.05)

        with pytest.raises(ValueError, match="flux linkage"):
            MotorCADEfficiencyEngine.compute_ke_constant(4, -0.01)

        with pytest.raises(ValueError, match="Stator resistance"):
            MotorCADEfficiencyEngine.compute_analytical_solution(
                MotorCADEfficiencyConfig(stator_resistance=-0.1)
            )

        with pytest.raises(ValueError, match="angular velocity"):
            MotorCADEfficiencyEngine.compute_analytical_solution(
                MotorCADEfficiencyConfig(omega_m=-100.0)
            )
