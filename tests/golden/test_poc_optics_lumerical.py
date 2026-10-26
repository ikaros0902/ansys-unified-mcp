# Strictly ASCII English Comments
"""Wave Optics (Lumerical FDTD/MODE) slab waveguide golden benchmark suite.

Validates integrated optics and wave propagation:
1. Symmetric 3-layer dielectric slab waveguide fundamental TE0 eigenvalue equation:
   u * tan(u) = w, where u^2 + w^2 = V^2.
2. Core index n1 = 1.50, Cladding index n2 = 1.45, Core half-thickness a = 1.0 um.
3. Free space wavelength lambda0 = 1.55 um, k0 = 2*pi/lambda0 = 4,053,668 rad/m.
4. Normalized frequency V = 1.55684 (< pi/2, single-mode guidance).
5. Effective index n_eff = beta / k0 = 1.4823.
6. Acceptance criteria:
   - Root finding and 1D-FDM n_eff relative error <= 0.5%
   - Strict physical bound n2 < n_eff < n1
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
from scipy.optimize import brentq

from ansys_unified_mcp.benchmarks.optics_lumerical_engine import (
    OpticsLumericalConfig,
    OpticsLumericalEngine,
    OpticsLumericalResult,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DielectricSlabSpec:
    """Symmetric slab waveguide optical specifications."""

    n1: float = 1.50
    n2: float = 1.45
    a: float = 1.0e-6
    wavelength: float = 1.55e-6


def compute_analytical_lumerical_baseline(spec: DielectricSlabSpec) -> Dict[str, float]:
    """Calculate theoretical slab waveguide TE0 parameters and reference root."""
    k0 = (2.0 * math.pi) / spec.wavelength
    v_num = k0 * spec.a * math.sqrt((spec.n1 ** 2) - (spec.n2 ** 2))

    def objective(u: float) -> float:
        w = math.sqrt((v_num ** 2) - (u ** 2))
        return (u * math.tan(u)) - w

    u_root = float(brentq(objective, 1e-7, min(v_num - 1e-8, (0.5 * math.pi) - 1e-8)))
    w_root = math.sqrt((v_num ** 2) - (u_root ** 2))
    beta = math.sqrt(((k0 * spec.n1) ** 2) - ((u_root / spec.a) ** 2))
    n_eff = beta / k0

    return {
        "k0": k0,
        "v_num": v_num,
        "u_root": u_root,
        "w_root": w_root,
        "beta": beta,
        "n_eff": n_eff,
    }


class TestPOCOpticsLumericalBenchmark:
    """Wave optics Lumerical slab waveguide golden benchmark test suite."""

    def test_analytical_dielectric_slab_waveguide_baseline(self) -> None:
        """Verify wavenumber, V-number, transcendental eigenvalue root, and n_eff."""
        spec = DielectricSlabSpec()
        theory = compute_analytical_lumerical_baseline(spec)

        # 1. Verification of free space wavenumber k0
        assert math.isclose(theory["k0"], (2.0 * math.pi) / 1.55e-6, rel_tol=1e-9)
        assert 4053660.0 <= theory["k0"] <= 4053680.0

        # 2. Verification of normalized frequency V
        assert math.isclose(theory["v_num"], 1.5568407, rel_tol=1e-5)
        assert theory["v_num"] < (0.5 * math.pi)

        # 3. Verification of transverse eigenvalue roots u and w
        u_val = theory["u_root"]
        w_val = theory["w_root"]
        assert 0.925 <= u_val <= 0.935
        assert 1.240 <= w_val <= 1.255
        assert math.isclose((u_val ** 2) + (w_val ** 2), theory["v_num"] ** 2, rel_tol=1e-12)
        assert math.isclose(u_val * math.tan(u_val), w_val, rel_tol=1e-10)

        # 4. Verification of effective refractive index n_eff
        n_eff = theory["n_eff"]
        assert 1.480 <= n_eff <= 1.485
        assert math.isclose(n_eff, 1.4823389, rel_tol=1e-5)

        # 5. Strict bounding verification: n2 < n_eff < n1
        assert spec.n2 < n_eff < spec.n1

    def test_numerical_slab_eigenvalue_accuracy_and_timing(self) -> None:
        """Verify numerical effective index relative error <= 0.5% and timing SLA."""
        cfg = OpticsLumericalConfig(
            core_index=1.50,
            cladding_index=1.45,
            core_half_thickness=1.0e-6,
            wavelength=1.55e-6,
            num_grid_points=1601,
        )

        t_start = time.perf_counter()
        res: OpticsLumericalResult = OpticsLumericalEngine.solve(cfg)
        elapsed = time.perf_counter() - t_start

        # Relative error of n_eff <= 0.5%
        assert res.n_eff_rel_error_pct <= 0.5, (
            f"n_eff relative error {res.n_eff_rel_error_pct:.6f}% exceeds 0.5% limit"
        )

        # 1D-FDM mode solver relative error <= 0.5%
        assert res.fdm_rel_error_pct <= 0.5, (
            f"FDM relative error {res.fdm_rel_error_pct:.6f}% exceeds 0.5% limit"
        )

        # Execution time <= 8.0 seconds
        assert elapsed <= 8.0, f"Solver elapsed time {elapsed:.4f}s exceeds 8.0s limit"
        assert res.solve_time_seconds <= 8.0

        # Strict physical bounds n2 < n_eff < n1
        assert res.is_strictly_bounded is True
        assert cfg.cladding_index < res.n_eff_sim < cfg.core_index
        assert cfg.cladding_index < res.n_eff_fdm < cfg.core_index

        # Transcendental root residual tolerance
        assert res.transcendental_residual <= 1e-9
        assert res.is_single_mode is True
        assert res.converged is True

    def test_weakly_guiding_and_confinement_factor(self) -> None:
        """Verify weakly guiding index contrast Delta and core optical confinement."""
        cfg = OpticsLumericalConfig(
            core_index=1.50,
            cladding_index=1.45,
            core_half_thickness=1.0e-6,
            wavelength=1.55e-6,
        )
        res = OpticsLumericalEngine.solve(cfg)

        delta = ((cfg.core_index ** 2) - (cfg.cladding_index ** 2)) / (2.0 * (cfg.core_index ** 2))
        assert math.isclose(delta, 0.0327777, rel_tol=1e-4)

        assert 0.80 <= res.core_confinement_factor <= 0.88
        assert math.isclose(res.core_confinement_factor, 0.84117, rel_tol=1e-3)

    def test_optics_lumerical_dual_track_resilience(self) -> None:
        """Verify dual-track fallback to FDM and transcendental engine when offline."""
        cfg = OpticsLumericalConfig()
        res = OpticsLumericalEngine.solve(cfg, prefer_ansys=True)

        assert res.solver_mode in ["ansys_lumerical", "transcendental_fdm_engine"]
        assert res.converged is True
        assert res.n_eff_rel_error_pct <= 0.5
        assert cfg.cladding_index < res.n_eff_sim < cfg.core_index
