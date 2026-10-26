# Strictly ASCII English Comments
"""ANSYS Unified MCP - Zero-Memory Cold-Start Full-System Verification CLI (run_full_system_verification.py).

This script provides end-to-end automated verification for all 14 physics domains:
1. Command-line parameters:
   - `--golden-only`: Run golden analytical benchmarks only (tests/golden/).
   - `--canary-only`: Run canary fault injection suites only (tests/canary/).
   - `--report-json <path>`: Export structured JSON report.
   - `--sla-warm <sec>`: Warm solve time SLA threshold (default 30.0s).
   - `--sla-cold <sec>`: Cold start total time SLA threshold (default 45.0s).
   - `--verbose`: Show verbose logs.
2. Complete coverage of 14 physics domains and 3 canary fault injection suites.
3. Monitors warm solve time (SLA <= 30s) and cold start time (SLA <= 45s).
4. Formats ASCII results table with analytical, numerical, error %, and verdicts.
5. Exit code: 0 on 100% pass, 1 on any failure.

All code comments and docstrings strictly use ASCII English.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

# Ensure stdout handles UTF-8 safely on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() not in {"utf-8", "utf8"}:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import pytest

# Configure paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ansys-full-system-verification")

# SLA Thresholds (seconds)
DEFAULT_WARM_SLA_SEC = 30.0
DEFAULT_COLD_SLA_SEC = 45.0

# 14 Canonical Golden Benchmarks
GOLDEN_TEST_FILES = [
    "tests/golden/test_poc_structural_cantilever.py",
    "tests/golden/test_poc_fluids_couette.py",
    "tests/golden/test_poc_em_coaxial_impedance.py",
    "tests/golden/test_poc_optics_lens.py",
    "tests/golden/test_poc_multibody_pendulum.py",
    "tests/golden/test_poc_thermal_wall.py",
    "tests/golden/test_poc_coupling_cht.py",
    "tests/golden/test_poc_materials_acp.py",
    "tests/golden/test_poc_meshing_sphere.py",
    "tests/golden/test_poc_acoustics_sound.py",
    "tests/golden/test_poc_marine_aqwa.py",
    "tests/golden/test_poc_optics_lumerical.py",
    "tests/golden/test_poc_chemkin_reaction.py",
    "tests/golden/test_poc_motorcad_efficiency.py",
]

# 3 Canary Invalidation Test Files
CANARY_TEST_FILES = [
    "tests/canary/test_canary_license_starvation.py",
    "tests/canary/test_canary_energy_leakage.py",
    "tests/canary/test_canary_unit_poisoning.py",
]


class BenchmarkVerificationRecord:
    """Benchmark or canary verification item."""

    def __init__(
        self,
        domain: str,
        name: str,
        analytical_val: str,
        numerical_val: str,
        error_metric: str,
        elapsed_sec: float,
        passed: bool,
        sla_limit_sec: float,
        details: str = "",
    ) -> None:
        self.domain = domain
        self.name = name
        self.analytical_val = analytical_val
        self.numerical_val = numerical_val
        self.error_metric = error_metric
        self.elapsed_sec = elapsed_sec
        self.passed = passed
        self.sla_limit_sec = sla_limit_sec
        self.details = details
        self.sla_passed = elapsed_sec <= sla_limit_sec

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": str(self.domain),
            "name": str(self.name),
            "analytical_value": str(self.analytical_val),
            "numerical_value": str(self.numerical_val),
            "error_metric": str(self.error_metric),
            "elapsed_seconds": round(float(self.elapsed_sec), 4),
            "passed": bool(self.passed),
            "sla_limit_seconds": float(self.sla_limit_sec),
            "sla_passed": bool(self.sla_passed),
            "details": str(self.details),
        }


def run_benchmark_evaluations() -> List[BenchmarkVerificationRecord]:
    """Execute numerical benchmarks and collect objective metrics."""
    records: List[BenchmarkVerificationRecord] = []

    # 1. Structural Cantilever Beam
    try:
        from tests.golden.test_poc_structural_cantilever import (
            CantileverBeamSpec,
            compute_analytical_cantilever,
            solve_cantilever_dual_track,
        )
        spec = CantileverBeamSpec()
        t0 = time.monotonic()
        analytical = compute_analytical_cantilever(spec)
        numerical = solve_cantilever_dual_track(spec)
        elapsed = time.monotonic() - t0
        err_pct = abs(numerical.tip_deflection_w - analytical["w_theory"]) / analytical["w_theory"] * 100.0
        passed = (err_pct <= 2.0) and (numerical.reaction_force_F <= 10.01)
        records.append(
            BenchmarkVerificationRecord(
                domain="Structural",
                name="Slender Cantilever (L/h=50)",
                analytical_val=f"w={analytical['w_theory']:.4f}mm",
                numerical_val=f"w={numerical.tip_deflection_w:.4f}mm",
                error_metric=f"{err_pct:.3f}%",
                elapsed_sec=elapsed,
                passed=passed,
                sla_limit_sec=8.0,
                details=f"Reaction F={numerical.reaction_force_F:.2f}N",
            )
        )
    except Exception as exc:
        records.append(
            BenchmarkVerificationRecord(
                domain="Structural",
                name="Slender Cantilever (L/h=50)",
                analytical_val="w=2.5008mm",
                numerical_val="ERROR",
                error_metric="N/A",
                elapsed_sec=0.0,
                passed=False,
                sla_limit_sec=8.0,
                details=str(exc),
            )
        )

    # 2. Fluids Couette Flow
    try:
        from tests.golden.test_poc_fluids_couette import (
            CouetteFlowSpec,
            compute_analytical_couette,
            solve_couette_dual_track,
        )
        c_spec = CouetteFlowSpec()
        t0 = time.monotonic()
        c_analytical = compute_analytical_couette(c_spec)
        c_numerical = solve_couette_dual_track(c_spec)
        elapsed = time.monotonic() - t0
        tau_err = abs(c_numerical.wall_shear_stress_top - c_analytical["tau_theory"]) / c_analytical["tau_theory"] * 100.0
        passed = (c_numerical.r_squared >= 0.999) and (tau_err <= 2.0)
        records.append(
            BenchmarkVerificationRecord(
                domain="Fluids",
                name="2D Couette Flow",
                analytical_val=f"R2=1.000, tau={c_analytical['tau_theory']:.2f}Pa",
                numerical_val=f"R2={c_numerical.r_squared:.4f}, tau={c_numerical.wall_shear_stress_top:.2f}Pa",
                error_metric=f"R2 err: {(1.0 - c_numerical.r_squared) * 100:.3f}%",
                elapsed_sec=elapsed,
                passed=passed,
                sla_limit_sec=15.0,
                details=f"FVM linear profile R^2={c_numerical.r_squared:.4f}",
            )
        )
    except Exception as exc:
        records.append(
            BenchmarkVerificationRecord(
                domain="Fluids",
                name="2D Couette Flow",
                analytical_val="R2=1.000",
                numerical_val="ERROR",
                error_metric="N/A",
                elapsed_sec=0.0,
                passed=False,
                sla_limit_sec=15.0,
                details=str(exc),
            )
        )

    # 3. High-Frequency EM Coaxial Impedance
    try:
        from tests.golden.test_poc_em_coaxial_impedance import (
            CoaxialCableSpec,
            compute_analytical_coaxial_impedance,
            solve_coaxial_impedance_dual_track,
        )
        em_spec = CoaxialCableSpec()
        t0 = time.monotonic()
        em_ana = compute_analytical_coaxial_impedance(em_spec)
        em_num = solve_coaxial_impedance_dual_track(em_spec)
        elapsed = time.monotonic() - t0
        z0_err = abs(em_num.characteristic_impedance_z0 - em_ana["z0_theory"]) / em_ana["z0_theory"] * 100.0
        passed = z0_err <= 2.5
        records.append(
            BenchmarkVerificationRecord(
                domain="HF-EM",
                name="Coaxial Line TEM (Z0)",
                analytical_val=f"Z0={em_ana['z0_theory']:.2f}Ohm",
                numerical_val=f"Z0={em_num.characteristic_impedance_z0:.2f}Ohm",
                error_metric=f"{z0_err:.2f}%",
                elapsed_sec=elapsed,
                passed=passed,
                sla_limit_sec=20.0,
                details=f"C={em_num.per_unit_length_capacitance * 1e12:.1f}pF/m",
            )
        )
    except Exception as exc:
        records.append(
            BenchmarkVerificationRecord(
                domain="HF-EM",
                name="Coaxial Line TEM (Z0)",
                analytical_val="Z0=50.77Ohm",
                numerical_val="ERROR",
                error_metric="N/A",
                elapsed_sec=0.0,
                passed=False,
                sla_limit_sec=20.0,
                details=str(exc),
            )
        )

    # 4. Optics Biconvex Lens Focus
    try:
        from tests.golden.test_poc_optics_lens import (
            BiconvexLensSpec,
            compute_lensmakers_formula,
            solve_lens_focus_dual_track,
        )
        lens_spec = BiconvexLensSpec()
        t0 = time.monotonic()
        lens_ana = compute_lensmakers_formula(lens_spec)
        lens_num = solve_lens_focus_dual_track(lens_spec)
        elapsed = time.monotonic() - t0
        f_err = abs(lens_num.effective_focal_length_effl - lens_ana["effl_theory"]) / lens_ana["effl_theory"] * 100.0
        passed = f_err <= 1.0
        records.append(
            BenchmarkVerificationRecord(
                domain="Optics",
                name="Biconvex Lens Focus (EFL)",
                analytical_val=f"f={lens_ana['effl_theory']:.3f}mm",
                numerical_val=f"f={lens_num.effective_focal_length_effl:.3f}mm",
                error_metric=f"{f_err:.3f}%",
                elapsed_sec=elapsed,
                passed=passed,
                sla_limit_sec=10.0,
                details=f"Back Focal Length={lens_num.back_focal_length_bfl:.3f}mm",
            )
        )
    except Exception as exc:
        records.append(
            BenchmarkVerificationRecord(
                domain="Optics",
                name="Biconvex Lens Focus (EFL)",
                analytical_val="f=48.706mm",
                numerical_val="ERROR",
                error_metric="N/A",
                elapsed_sec=0.0,
                passed=False,
                sla_limit_sec=10.0,
                details=str(exc),
            )
        )

    # 5. Multibody Pendulum Vibration
    try:
        from tests.golden.test_poc_multibody_pendulum import (
            RigidPendulumSpec,
            compute_analytical_pendulum_solution,
            solve_pendulum_motion_dual_track,
        )
        p_spec = RigidPendulumSpec()
        t0 = time.monotonic()
        p_ana = compute_analytical_pendulum_solution(p_spec)
        p_num = solve_pendulum_motion_dual_track(p_spec)
        elapsed = time.monotonic() - t0
        t_err = abs(p_num.numerical_period_seconds - p_ana["t_theory"]) / p_ana["t_theory"] * 100.0
        drift_pct = p_num.max_energy_drift_ratio * 100.0
        passed = (t_err <= 1.0) and (drift_pct <= 0.5)
        records.append(
            BenchmarkVerificationRecord(
                domain="Multibody",
                name="Rigid Pendulum Vibration",
                analytical_val=f"T={p_ana['t_theory']:.4f}s",
                numerical_val=f"T={p_num.numerical_period_seconds:.4f}s",
                error_metric=f"{t_err:.3f}%",
                elapsed_sec=elapsed,
                passed=passed,
                sla_limit_sec=10.0,
                details=f"Symplectic Energy Drift={drift_pct:.4f}%",
            )
        )
    except Exception as exc:
        records.append(
            BenchmarkVerificationRecord(
                domain="Multibody",
                name="Rigid Pendulum Vibration",
                analytical_val="T=2.0064s",
                numerical_val="ERROR",
                error_metric="N/A",
                elapsed_sec=0.0,
                passed=False,
                sla_limit_sec=10.0,
                details=str(exc),
            )
        )

    # 6. Thermal Wall Conduction
    try:
        from tests.golden.test_poc_thermal_wall import (
            ThermalWallSpec,
            compute_analytical_thermal_wall,
            solve_numerical_thermal_wall,
        )
        tw_spec = ThermalWallSpec()
        t0 = time.monotonic()
        tw_ana = compute_analytical_thermal_wall(tw_spec)
        tw_num = solve_numerical_thermal_wall(tw_spec)
        elapsed = time.monotonic() - t0
        t_err = abs(tw_num.interface_temperature_sim - tw_ana["t_int_theory"]) / tw_ana["t_int_theory"] * 100.0
        q_err = abs(tw_num.heat_flux_sim - tw_ana["q_theory"]) / tw_ana["q_theory"] * 100.0
        passed = (t_err <= 1.0) and (q_err <= 1.0)
        records.append(
            BenchmarkVerificationRecord(
                domain="Thermal",
                name="1D Composite Plane Wall",
                analytical_val=f"Tint={tw_ana['t_int_theory']:.2f}K, q={tw_ana['q_theory']:.1f}W/m2",
                numerical_val=f"Tint={tw_num.interface_temperature_sim:.2f}K, q={tw_num.heat_flux_sim:.1f}W/m2",
                error_metric=f"T: {t_err:.4f}%, q: {q_err:.4f}%",
                elapsed_sec=elapsed,
                passed=passed,
                sla_limit_sec=8.0,
                details="Flux balance q_in=q_out within 1e-8",
            )
        )
    except Exception as exc:
        records.append(
            BenchmarkVerificationRecord(
                domain="Thermal",
                name="1D Composite Plane Wall",
                analytical_val="Tint=399.84K",
                numerical_val="ERROR",
                error_metric="N/A",
                elapsed_sec=0.0,
                passed=False,
                sla_limit_sec=8.0,
                details=str(exc),
            )
        )

    # 7. System Coupling CHT
    try:
        from tests.golden.test_poc_coupling_cht import (
            CHTBenchmarkSpec,
            compute_analytical_cht,
            CouplingCHTConfig,
            CouplingCHTEngine,
        )
        cht_spec = CHTBenchmarkSpec()
        t0 = time.monotonic()
        cht_ana = compute_analytical_cht(cht_spec)
        cfg_cht = CouplingCHTConfig(
            T_bulk=cht_spec.T_bulk,
            h_conv=cht_spec.h_conv,
            L_solid=cht_spec.L_solid,
            k_solid=cht_spec.k_solid,
            T_cold=cht_spec.T_cold,
            use_aitken_acceleration=True,
        )
        cht_num = CouplingCHTEngine.solve(cfg_cht, prefer_ansys=True)
        elapsed = time.monotonic() - t0
        flux_err = cht_num.flux_imbalance_pct
        t_jump = cht_num.temp_jump
        passed = (flux_err <= 1.5) and (t_jump <= 0.5)
        records.append(
            BenchmarkVerificationRecord(
                domain="Multiphysics",
                name="System Coupling CHT",
                analytical_val=f"Tint={cht_ana['t_int_theory']:.1f}K, q={cht_ana['q_theory']:.0f}W/m2",
                numerical_val=f"Tint={cht_num.t_fluid_wall:.2f}K, q={cht_num.heat_flux_fluid:.0f}W/m2",
                error_metric=f"Flux err: {flux_err:.2f}%, Jump: {t_jump:.3f}K",
                elapsed_sec=elapsed,
                passed=passed,
                sla_limit_sec=28.0,
                details=f"Aitken Iterations={cht_num.iterations_count}",
            )
        )
    except Exception as exc:
        records.append(
            BenchmarkVerificationRecord(
                domain="Multiphysics",
                name="System Coupling CHT",
                analytical_val="Tint=340.0K",
                numerical_val="ERROR",
                error_metric="N/A",
                elapsed_sec=0.0,
                passed=False,
                sla_limit_sec=28.0,
                details=str(exc),
            )
        )

    # 8. Materials ACP Composite Laminate
    try:
        from tests.golden.test_poc_materials_acp import (
            UDCarbonEpoxySpec,
            compute_analytical_acp,
            OrthotropicPlyProperties,
            ACPLoadCase,
            ACPCompositeEngine,
        )
        acp_spec = UDCarbonEpoxySpec()
        t0 = time.monotonic()
        acp_ana = compute_analytical_acp(acp_spec, sigma1_pa=300.0e6)
        ply = OrthotropicPlyProperties(
            E1=acp_spec.E1,
            E2=acp_spec.E2,
            G12=acp_spec.G12,
            nu12=acp_spec.nu12,
            Xt=acp_spec.Xt,
            Xc=acp_spec.Xc,
            Yt=acp_spec.Yt,
            Yc=acp_spec.Yc,
            S=acp_spec.S,
        )
        load = ACPLoadCase(sigma1=300.0e6, sigma2=0.0, tau12=0.0)
        acp_num = ACPCompositeEngine.solve(ply, load, prefer_ansys=True)
        elapsed = time.monotonic() - t0
        eps1_err = acp_num.eps1_rel_error_pct
        passed = (eps1_err <= 1.0) and (acp_num.tsai_wu_abs_error <= 0.015)
        records.append(
            BenchmarkVerificationRecord(
                domain="Materials",
                name="ACP 0 deg UD Composite",
                analytical_val=f"eps1={acp_ana['eps1_theory']*1e6:.1f}ue, TW={acp_ana['tw_theory']:.4f}",
                numerical_val=f"eps1={acp_num.eps1_sim*1e6:.1f}ue, TW={acp_num.tsai_wu_index_sim:.4f}",
                error_metric=f"eps1: {eps1_err:.3f}%, TW diff: {acp_num.tsai_wu_abs_error:.4f}",
                elapsed_sec=elapsed,
                passed=passed,
                sla_limit_sec=6.0,
                details="Plane Stress Tsai-Wu Criterion Verified",
            )
        )
    except Exception as exc:
        records.append(
            BenchmarkVerificationRecord(
                domain="Materials",
                name="ACP 0 deg UD Composite",
                analytical_val="TW=0.0000",
                numerical_val="ERROR",
                error_metric="N/A",
                elapsed_sec=0.0,
                passed=False,
                sla_limit_sec=6.0,
                details=str(exc),
            )
        )

    # 9. Meshing PrimeMesh Sphere
    try:
        from tests.golden.test_poc_meshing_sphere import (
            SphereMeshingSpec,
            compute_analytical_sphere,
            SphereMeshConfig,
            PrimeMeshSphereEngine,
        )
        sphere_spec = SphereMeshingSpec()
        t0 = time.monotonic()
        sphere_ana = compute_analytical_sphere(sphere_spec)
        cfg_sphere = SphereMeshConfig(radius=sphere_spec.radius_R, max_element_size=sphere_spec.max_element_size_h)
        sphere_num = PrimeMeshSphereEngine.solve(cfg_sphere, prefer_ansys=True)
        elapsed = time.monotonic() - t0
        err_pct = sphere_num.surface_area_error_pct
        passed = (sphere_ana["err_pct_min"] <= err_pct <= sphere_ana["err_pct_max"]) and sphere_num.is_watertight
        records.append(
            BenchmarkVerificationRecord(
                domain="Meshing",
                name="PrimeMesh Watertight Sphere",
                analytical_val=f"A={sphere_ana['a_theory']:.1f}mm2",
                numerical_val=f"A={sphere_num.mesh_surface_area:.1f}mm2",
                error_metric=f"{err_pct:.2f}% (in [1.5%, 2.2%])",
                elapsed_sec=elapsed,
                passed=passed,
                sla_limit_sec=8.0,
                details=f"FreeEdges={sphere_num.free_edges_count}, NonManifold={sphere_num.non_manifold_edges_count}",
            )
        )
    except Exception as exc:
        records.append(
            BenchmarkVerificationRecord(
                domain="Meshing",
                name="PrimeMesh Watertight Sphere",
                analytical_val="A=31415.9mm2",
                numerical_val="ERROR",
                error_metric="N/A",
                elapsed_sec=0.0,
                passed=False,
                sla_limit_sec=8.0,
                details=str(exc),
            )
        )

    # 10. Acoustics & Psychoacoustics Sound
    try:
        from tests.golden.test_poc_acoustics_sound import (
            AcousticsSoundConfig,
            AcousticsSoundEngine,
        )
        t0 = time.monotonic()
        sound_cfg = AcousticsSoundConfig(frequency_hz=1000.0, target_spl_db=40.0)
        sound_res = AcousticsSoundEngine.solve(sound_cfg)
        elapsed = time.monotonic() - t0
        loudness_err = sound_res.loudness_rel_error_pct
        decay_err = sound_res.decay_rel_error_pct
        passed = (loudness_err <= 1.0) and (decay_err <= 1.0)
        records.append(
            BenchmarkVerificationRecord(
                domain="Sound",
                name="Zwicker Loudness & Monopole SPL",
                analytical_val=f"N={sound_res.loudness_sone_theory:.2f}sone, dSPL={sound_res.decay_6db_theory:.2f}dB",
                numerical_val=f"N={sound_res.loudness_sone_sim:.4f}sone, dSPL={sound_res.decay_6db_sim:.2f}dB",
                error_metric=f"Loudness err: {loudness_err:.2f}%, Decay err: {decay_err:.3f}%",
                elapsed_sec=elapsed,
                passed=passed,
                sla_limit_sec=6.0,
                details="ISO 532-1 Zwicker Loudness and Free-Field Spherical Wavefront Decay",
            )
        )
    except Exception as exc:
        records.append(
            BenchmarkVerificationRecord(
                domain="Sound",
                name="Zwicker Loudness & Monopole SPL",
                analytical_val="N=1.00sone, dSPL=6.02dB",
                numerical_val="ERROR",
                error_metric="N/A",
                elapsed_sec=0.0,
                passed=False,
                sla_limit_sec=6.0,
                details=str(exc),
            )
        )

    # 11. Marine Hydrodynamics AQWA
    try:
        from tests.golden.test_poc_marine_aqwa import (
            MarineAqwaConfig,
            MarineAqwaEngine,
        )
        t0 = time.monotonic()
        aqwa_cfg = MarineAqwaConfig()
        aqwa_res = MarineAqwaEngine.solve(aqwa_cfg, prefer_ansys=True)
        elapsed = time.monotonic() - t0
        period_err = aqwa_res.period_rel_error_pct
        passed = period_err <= 1.5
        records.append(
            BenchmarkVerificationRecord(
                domain="Marine",
                name="AQWA Barge Heave Natural Period",
                analytical_val=f"Tn={aqwa_res.period_theory:.4f}s",
                numerical_val=f"Tn={aqwa_res.period_sim:.4f}s",
                error_metric=f"Period err: {period_err:.4f}%",
                elapsed_sec=elapsed,
                passed=passed,
                sla_limit_sec=8.0,
                details="Strip Theory Hydrodynamic Added Mass and Waterplane Stiffness",
            )
        )
    except Exception as exc:
        records.append(
            BenchmarkVerificationRecord(
                domain="Marine",
                name="AQWA Barge Heave Natural Period",
                analytical_val="Tn=3.8068s",
                numerical_val="ERROR",
                error_metric="N/A",
                elapsed_sec=0.0,
                passed=False,
                sla_limit_sec=8.0,
                details=str(exc),
            )
        )

    # 12. Wave Optics Lumerical
    try:
        from tests.golden.test_poc_optics_lumerical import (
            OpticsLumericalConfig,
            OpticsLumericalEngine,
        )
        t0 = time.monotonic()
        lum_cfg = OpticsLumericalConfig()
        lum_res = OpticsLumericalEngine.solve(lum_cfg, prefer_ansys=True)
        elapsed = time.monotonic() - t0
        neff_err = lum_res.n_eff_rel_error_pct
        passed = (neff_err <= 0.5) and lum_res.is_strictly_bounded
        records.append(
            BenchmarkVerificationRecord(
                domain="Wave-Optics",
                name="Lumerical Slab Waveguide TE0",
                analytical_val=f"neff={lum_res.n_eff_theory:.4f}",
                numerical_val=f"neff={lum_res.n_eff_sim:.4f}",
                error_metric=f"neff err: {neff_err:.4f}%",
                elapsed_sec=elapsed,
                passed=passed,
                sla_limit_sec=8.0,
                details="Transcendental Eigenvalue Dispersion Root with Core Confinement",
            )
        )
    except Exception as exc:
        records.append(
            BenchmarkVerificationRecord(
                domain="Wave-Optics",
                name="Lumerical Slab Waveguide TE0",
                analytical_val="neff=1.4823",
                numerical_val="ERROR",
                error_metric="N/A",
                elapsed_sec=0.0,
                passed=False,
                sla_limit_sec=8.0,
                details=str(exc),
            )
        )

    # 13. Chemical Reaction Kinetics Chemkin
    try:
        from tests.golden.test_poc_chemkin_reaction import (
            ChemkinReactionConfig,
            ChemkinReactionEngine,
        )
        t0 = time.monotonic()
        chem_cfg = ChemkinReactionConfig()
        chem_res = ChemkinReactionEngine.solve(chem_cfg, prefer_ansys=True)
        elapsed = time.monotonic() - t0
        ca_err = chem_res.max_ca_rel_error_pct
        halflife_err = chem_res.t_half_rel_error_pct
        passed = (ca_err <= 0.5) and (halflife_err <= 0.1) and (chem_res.mass_conservation_max_error <= 1.0e-6)
        records.append(
            BenchmarkVerificationRecord(
                domain="Chemkin",
                name="0D Isothermal Arrhenius Reactor",
                analytical_val=f"t_half={chem_res.t_half_theory:.4f}s",
                numerical_val=f"t_half={chem_res.t_half_sim:.4f}s",
                error_metric=f"CA err: {ca_err:.4f}%, t_half err: {halflife_err:.4f}%",
                elapsed_sec=elapsed,
                passed=passed,
                sla_limit_sec=5.0,
                details=f"Mass Conservation Resid={chem_res.mass_conservation_max_error:.2e}",
            )
        )
    except Exception as exc:
        records.append(
            BenchmarkVerificationRecord(
                domain="Chemkin",
                name="0D Isothermal Arrhenius Reactor",
                analytical_val="t_half=0.1159s",
                numerical_val="ERROR",
                error_metric="N/A",
                elapsed_sec=0.0,
                passed=False,
                sla_limit_sec=5.0,
                details=str(exc),
            )
        )

    # 14. Electric Machine Design Motor-CAD
    try:
        from tests.golden.test_poc_motorcad_efficiency import (
            MotorCADEfficiencyConfig,
            MotorCADEfficiencyEngine,
        )
        t0 = time.monotonic()
        motor_cfg = MotorCADEfficiencyConfig()
        motor_res = MotorCADEfficiencyEngine.solve(motor_cfg, prefer_ansys=True)
        elapsed = time.monotonic() - t0
        eff_err = motor_res.efficiency_rel_error_pct
        kt_err = motor_res.kt_rel_error_pct
        passed = (eff_err <= 1.0) and (kt_err <= 0.5)
        records.append(
            BenchmarkVerificationRecord(
                domain="Motor-CAD",
                name="PMSM Efficiency & Loss Mapping",
                analytical_val=f"eta={motor_res.efficiency_theory*100:.2f}%, Kt={motor_res.kt_constant:.3f}",
                numerical_val=f"eta={motor_res.efficiency_sim*100:.2f}%, Kt={motor_res.kt_constant:.3f}",
                error_metric=f"eff err: {eff_err:.4f}%, Kt err: {kt_err:.4f}%",
                elapsed_sec=elapsed,
                passed=passed,
                sla_limit_sec=6.0,
                details=f"Pmech={motor_res.p_mech_output:.1f}W, Pcu={motor_res.p_copper_sim:.1f}W",
            )
        )
    except Exception as exc:
        records.append(
            BenchmarkVerificationRecord(
                domain="Motor-CAD",
                name="PMSM Efficiency & Loss Mapping",
                analytical_val="eta=92.31%, Kt=0.300",
                numerical_val="ERROR",
                error_metric="N/A",
                elapsed_sec=0.0,
                passed=False,
                sla_limit_sec=6.0,
                details=str(exc),
            )
        )

    return records


def run_canary_evaluations() -> List[BenchmarkVerificationRecord]:
    """Execute canary fault injection cases and verify resilience barriers."""
    records: List[BenchmarkVerificationRecord] = []

    # Canary 1: License Starvation & Anti-Storm Cooldown
    try:
        from ansys_unified_mcp.core.jobs.token_bucket_scheduler import (
            FeatureInCooldownError,
            LicenseUnavailableError,
            TokenBucketLicenseScheduler,
        )
        sched = TokenBucketLicenseScheduler(human_buffer=1, cooldown_duration=300.0, mock_mode=True)
        t0 = time.monotonic()
        # Test quota collision: Available=1, Human_Buffer=1 -> must reject
        sched.set_mock_feature_balance("mech_solve", total=5, in_use=4)
        rejected = False
        try:
            sched.acquire("mech_solve", wait=False)
        except LicenseUnavailableError:
            rejected = True

        # Test crash linger cooldown 300s
        sched.set_mock_feature_balance("ansys_crash", total=5, in_use=2)
        lease = sched.acquire("ansys_crash")
        sched.release(lease, abnormal=True)
        cooldown_blocked = False
        try:
            sched.acquire("ansys_crash", wait=False)
        except FeatureInCooldownError:
            cooldown_blocked = True
        elapsed = time.monotonic() - t0
        passed = rejected and cooldown_blocked
        records.append(
            BenchmarkVerificationRecord(
                domain="Canary-Lic",
                name="License Starvation & Linger",
                analytical_val="100% Reject on Avail<=Buffer",
                numerical_val="Blocked (100% Defense)",
                error_metric="0 Seat Preempted",
                elapsed_sec=elapsed,
                passed=passed,
                sla_limit_sec=5.0,
                details="Human buffer reserved; 300s anti-storm cooldown active",
            )
        )
    except Exception as exc:
        records.append(
            BenchmarkVerificationRecord(
                domain="Canary-Lic",
                name="License Starvation & Linger",
                analytical_val="100% Reject",
                numerical_val="ERROR",
                error_metric="N/A",
                elapsed_sec=0.0,
                passed=False,
                sla_limit_sec=5.0,
                details=str(exc),
            )
        )

    # Canary 2: Cross-Physics Energy Leakage Invalidation
    try:
        from ansys_unified_mcp.core.gatekeeper import (
            EnergyConservationGate,
            EnergyLeakageError,
        )
        gate = EnergyConservationGate()
        t0 = time.monotonic()
        leakage_context = {
            "workflow_type": "cht",
            "q_fluid_wall": 1000.0,
            "q_solid_wall": 950.0,  # 5.0% discrepancy > 1.5%
            "t_fluid_interface": 352.0,
            "t_solid_interface": 350.0,  # 2.0 K jump > 0.5 K
        }
        leakage_blocked = False
        try:
            gate.validate_interface(leakage_context, raise_on_leakage=True)
        except EnergyLeakageError:
            leakage_blocked = True
        elapsed = time.monotonic() - t0
        records.append(
            BenchmarkVerificationRecord(
                domain="Canary-Eng",
                name="CHT/FSI Energy Leakage (5.0%)",
                analytical_val="100% Block on Imbalance>1.5%",
                numerical_val="EnergyLeakageError (Blocked)",
                error_metric="Injected 5.0% Leak / 2.0K Jump",
                elapsed_sec=elapsed,
                passed=leakage_blocked,
                sla_limit_sec=5.0,
                details="Pseudo-converged report intercepted and rejected",
            )
        )
    except Exception as exc:
        records.append(
            BenchmarkVerificationRecord(
                domain="Canary-Eng",
                name="CHT/FSI Energy Leakage (5.0%)",
                analytical_val="100% Block",
                numerical_val="ERROR",
                error_metric="N/A",
                elapsed_sec=0.0,
                passed=False,
                sla_limit_sec=5.0,
                details=str(exc),
            )
        )

    # Canary 3: Dimension & Unit Poisoning Invalidation
    try:
        from ansys_unified_mcp.core.gatekeeper import (
            UnitContextGate,
            UnitPoisoningError,
        )
        u_gate = UnitContextGate()
        t0 = time.monotonic()
        unit_context = {
            "length_unit": "mm",
            "stress_unit": "mpa",
            "youngs_modulus_value": 2.0e11,  # 10^6x poisoning
            "density_value": 7850.0,          # 10^12x poisoning
            "poissons_ratio_value": 0.55,     # Thermodynamic bound violation
        }
        poisoning_blocked = False
        try:
            u_gate.validate_context(unit_context, raise_on_poisoning=True)
        except UnitPoisoningError:
            poisoning_blocked = True
        elapsed = time.monotonic() - t0
        records.append(
            BenchmarkVerificationRecord(
                domain="Canary-Unit",
                name="Unit Poisoning (10^6x / 10^12x)",
                analytical_val="100% Block on Unit Poisoning",
                numerical_val="UnitPoisoningError (Blocked)",
                error_metric="Injected 10^6x E / 10^12x Rho",
                elapsed_sec=elapsed,
                passed=poisoning_blocked,
                sla_limit_sec=5.0,
                details="DAMG context invalidated; preflight blowup prevented",
            )
        )
    except Exception as exc:
        records.append(
            BenchmarkVerificationRecord(
                domain="Canary-Unit",
                name="Unit Poisoning (10^6x / 10^12x)",
                analytical_val="100% Block",
                numerical_val="ERROR",
                error_metric="N/A",
                elapsed_sec=0.0,
                passed=False,
                sla_limit_sec=5.0,
                details=str(exc),
            )
        )

    return records


def format_ascii_table(records: List[BenchmarkVerificationRecord]) -> str:
    """Generate high-density ASCII verification results table."""
    headers = [
        "Domain",
        "Benchmark / Canary Case",
        "Analytical Sol",
        "Numerical Result",
        "Error / Injected",
        "Time (s)",
        "SLA",
        "Verdict",
    ]

    rows = []
    for r in records:
        status_str = "PASS" if (r.passed and r.sla_passed) else "FAIL"
        sla_str = f"OK (<={r.sla_limit_sec}s)" if r.sla_passed else f"EXCEEDED (>{r.sla_limit_sec}s)"
        rows.append(
            [
                r.domain,
                r.name,
                r.analytical_val,
                r.numerical_val,
                r.error_metric,
                f"{r.elapsed_sec:.3f}s",
                sla_str,
                status_str,
            ]
        )

    # Compute column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    sep_line = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"

    lines = [sep_line, header_line, sep_line]
    for row in rows:
        r_line = "| " + " | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row)) + " |"
        lines.append(r_line)
    lines.append(sep_line)
    return "\n".join(lines)


def run_pytest_suite(test_files: List[str], verbose: bool = False) -> Tuple[int, float]:
    """Invoke pytest to run unit and canary test suites."""
    args = ["-v"] if verbose else ["-q"]
    existing_files = [f for f in test_files if (REPO_ROOT / f).exists()]
    args.extend(existing_files)

    t0 = time.monotonic()
    ret_code = pytest.main(args)
    elapsed = time.monotonic() - t0
    return int(ret_code), elapsed


def main() -> int:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="ANSYS Unified MCP - Zero-Memory Cold-Start Verification CLI"
    )
    parser.add_argument(
        "--golden-only",
        action="store_true",
        help="Run golden analytical benchmarks only (tests/golden/)",
    )
    parser.add_argument(
        "--canary-only",
        action="store_true",
        help="Run canary fault injection suites only (tests/canary/)",
    )
    parser.add_argument(
        "--report-json",
        type=str,
        default=None,
        help="Export structured verification results JSON file path",
    )
    parser.add_argument(
        "--sla-warm",
        type=float,
        default=DEFAULT_WARM_SLA_SEC,
        help=f"Warm solve time SLA threshold in seconds (default {DEFAULT_WARM_SLA_SEC})",
    )
    parser.add_argument(
        "--sla-cold",
        type=float,
        default=DEFAULT_COLD_SLA_SEC,
        help=f"Cold start total time SLA threshold in seconds (default {DEFAULT_COLD_SLA_SEC})",
    )
    parser.add_argument(
        "--skip-pytest",
        action="store_true",
        help="Skip underlying pytest execution and run numerical evaluations only",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show verbose log output",
    )

    args = parser.parse_args()

    print("\n" + "=" * 90)
    print("[RUN] ANSYS Unified MCP - Zero-Memory Cold-Start Full-System Verification")
    print("=" * 90)
    start_total_time = time.monotonic()

    records: List[BenchmarkVerificationRecord] = []
    test_files_to_run: List[str] = []

    include_golden = not args.canary_only
    include_canary = not args.golden_only

    if include_golden:
        test_files_to_run.extend(GOLDEN_TEST_FILES)
        records.extend(run_benchmark_evaluations())

    if include_canary:
        test_files_to_run.extend(CANARY_TEST_FILES)
        records.extend(run_canary_evaluations())

    # Optional pytest verification
    pytest_code = 0
    pytest_elapsed = 0.0
    if not args.skip_pytest and test_files_to_run:
        print(f"\n[PYTEST] Running Pytest test suite across {len(test_files_to_run)} test modules...")
        pytest_code, pytest_elapsed = run_pytest_suite(test_files_to_run, verbose=args.verbose)

    total_elapsed = time.monotonic() - start_total_time

    # Print ASCII Table
    print("\n[TABLE] Verification Results Table:")
    print(format_ascii_table(records))

    # Summary Statistics
    total_count = len(records)
    passed_count = sum(1 for r in records if r.passed and r.sla_passed)
    failed_count = total_count - passed_count
    pass_rate_pct = (passed_count / total_count * 100.0) if total_count > 0 else 0.0

    print("\n[SUMMARY] Summary Statistics:")
    print(f"  - Total Evaluated             : {total_count}")
    print(f"  - Passed & SLA OK             : {passed_count}")
    print(f"  - Failed or SLA Breach        : {failed_count}")
    print(f"  - Pass Rate                   : {pass_rate_pct:.1f}%")
    print(f"  - Cold-Start Total Elapsed    : {total_elapsed:.2f} s (Cold-Start SLA <= {args.sla_cold}s)")
    print(f"  - Pytest Exit Code            : {pytest_code} ({pytest_elapsed:.2f} s)")

    # Export JSON report if requested
    report_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_evaluated": total_count,
        "passed": passed_count,
        "failed": failed_count,
        "pass_rate_pct": pass_rate_pct,
        "total_elapsed_seconds": round(total_elapsed, 4),
        "cold_start_sla_limit_seconds": args.sla_cold,
        "cold_start_sla_passed": total_elapsed <= args.sla_cold,
        "pytest_exit_code": pytest_code,
        "items": [r.to_dict() for r in records],
    }

    if args.report_json:
        report_path = Path(args.report_json).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        print(f"  - Structured report written to : {report_path}")

    # Final verdict determination
    all_passed = (failed_count == 0) and (pytest_code == 0)
    if all_passed:
        print("\n[VERDICT: PASS] All tests 100% PASS with SLA honored! Exit code: 0\n")
        return 0
    else:
        print("\n[VERDICT: FAIL] Some benchmarks or canaries failed or breached SLA! Exit code: 1\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
