"""Stage 4 Unit Tests: Multiphysics Bridges (STOP & MBD-DEM).

Validates:
1. STOP Analysis Bridge:
   - SVD Kabsch-Umeyama algorithm 100% separating 6-DOF rigid body motion (translation + rotation).
   - Zernike orthogonal polynomial least-squares fit with residual RMS <= 1.0% on known spherical/coma aberrations.
2. MBD-DEM Coupling Bridge:
   - 2nd-order Hermite posture extrapolation continuity and smoothness across 1,000 substeps.
   - 1,000-substep collision impulse time-averaged integration accuracy and energy conservation (<0.1% discrepancy).
"""

from __future__ import annotations

import math
import numpy as np
import pytest

from ansys_unified_mcp.products.multiphysics.stop_analysis_bridge import (
    RigidBody6DOF,
    STOPAnalysisBridge,
    ZernikeFitResult,
)
from ansys_unified_mcp.products.multiphysics.mbd_dem_bridge import (
    HermiteTrajectory,
    MBDDEMBridge,
    SubstepForceResult,
)


# ==============================================================================
# 1. STOP Analysis Bridge Tests (SVD 6-DOF & Zernike Fit)
# ==============================================================================

def test_stop_bridge_svd_rigid_body_separation():
    """Verify SVD separates 6-DOF rigid translation and rotation with numerical exactness."""
    # Generate 500 surface points on a concave mirror
    np.random.seed(123)
    n_points = 500
    r_pts = 50.0 * np.sqrt(np.random.uniform(0.0, 1.0, n_points))
    theta_pts = np.random.uniform(0.0, 2.0 * np.pi, n_points)
    x = r_pts * np.cos(theta_pts)
    y = r_pts * np.sin(theta_pts)
    # Parabolic sagittal depth z = (x^2 + y^2) / (2 * R_curv)
    z = (x ** 2 + y ** 2) / (2.0 * 200.0)
    p_initial = np.column_stack([x, y, z])

    # Inject known 6-DOF rigid body motion:
    # Known translation: [1.50, -2.25, 3.10] mm
    t_known = np.array([1.50, -2.25, 3.10], dtype=np.float64)

    # Known rotations: Rx = 0.5 deg, Ry = -0.3 deg, Rz = 0.8 deg
    rx_rad = math.radians(0.5)
    ry_rad = math.radians(-0.3)
    rz_rad = math.radians(0.8)

    rx_mat = np.array([
        [1.0, 0.0, 0.0],
        [0.0, math.cos(rx_rad), -math.sin(rx_rad)],
        [0.0, math.sin(rx_rad), math.cos(rx_rad)],
    ])
    ry_mat = np.array([
        [math.cos(ry_rad), 0.0, math.sin(ry_rad)],
        [0.0, 1.0, 0.0],
        [-math.sin(ry_rad), 0.0, math.cos(ry_rad)],
    ])
    rz_mat = np.array([
        [math.cos(rz_rad), -math.sin(rz_rad), 0.0],
        [math.sin(rz_rad), math.cos(rz_rad), 0.0],
        [0.0, 0.0, 1.0],
    ])
    r_known = rz_mat @ ry_mat @ rx_mat

    # Apply rigid transformation
    p_deformed = (p_initial @ r_known.T) + t_known

    # Execute SVD separation
    six_dof, elastic_def = STOPAnalysisBridge.separate_rigid_body_motion(p_initial, p_deformed)

    # Verification 1: Translation recovery accuracy (discrepancy < 1e-10 mm)
    t_recovered = np.array(six_dof.translation_vector)
    t_error = np.linalg.norm(t_recovered - t_known)
    assert t_error < 1e-10, f"Translation recovery error {t_error} exceeds 1e-10 mm"

    # Verification 2: Rotation angles recovery (discrepancy < 1e-6 degrees)
    angles_recovered = np.array(six_dof.rotation_angles_deg)
    angles_known = np.array([0.5, -0.3, 0.8])
    angle_error = np.linalg.norm(angles_recovered - angles_known)
    assert angle_error < 1e-6, f"Rotation angle recovery error {angle_error} exceeds 1e-6 deg"

    # Verification 3: Pure elastic deformation after subtracting rigid motion is zero
    max_elastic = float(np.max(np.linalg.norm(elastic_def, axis=1)))
    assert max_elastic < 1e-10, f"Spurious elastic deformation {max_elastic} detected in rigid motion!"


def test_stop_bridge_zernike_fitting_spherical_and_coma():
    """Verify Zernike least-squares fit reconstructs spherical and coma aberrations with RMS <= 1.0%."""
    np.random.seed(456)
    n_points = 800
    norm_radius = 50.0

    # Points on circular aperture
    r_norm = np.sqrt(np.random.uniform(0.01, 1.0, n_points))
    theta = np.random.uniform(0.0, 2.0 * np.pi, n_points)
    x = r_norm * norm_radius * np.cos(theta)
    y = r_norm * norm_radius * np.sin(theta)

    # Case A: Known Primary Spherical Aberration (Fringe Z9 = 6*r^4 - 6*r^2 + 1)
    amplitude_sph = 0.005  # 5 micrometers
    delta_z_sph = amplitude_sph * (6.0 * (r_norm ** 4) - 6.0 * (r_norm ** 2) + 1.0)

    coeffs_sph, result_sph = STOPAnalysisBridge.fit_fringe_zernike(
        x, y, delta_z_sph, norm_radius=norm_radius, num_terms=16
    )

    # Verification: Z9 term is index 8 (0-based)
    assert abs(coeffs_sph[8] - amplitude_sph) < 1e-6, f"Z9 coefficient {coeffs_sph[8]} != {amplitude_sph}"
    assert result_sph.relative_rms_error <= 1.0, f"Spherical fit relative RMS {result_sph.relative_rms_error}% > 1.0%"
    assert result_sph.rms_residual < 1e-7

    # Case B: Known Coma Aberration (Fringe Z7 = (3*r^3 - 2*r)*cos(theta))
    amplitude_coma = 0.003  # 3 micrometers
    delta_z_coma = amplitude_coma * (3.0 * (r_norm ** 3) - 2.0 * r_norm) * np.cos(theta)

    coeffs_coma, result_coma = STOPAnalysisBridge.fit_fringe_zernike(
        x, y, delta_z_coma, norm_radius=norm_radius, num_terms=16
    )

    # Z7 term is index 6
    assert abs(coeffs_coma[6] - amplitude_coma) < 1e-6, f"Z7 coefficient {coeffs_coma[6]} != {amplitude_coma}"
    assert result_coma.relative_rms_error <= 1.0, f"Coma fit relative RMS {result_coma.relative_rms_error}% > 1.0%"
    assert result_coma.rms_residual < 1e-7


# ==============================================================================
# 2. MBD-DEM Coupling Bridge Tests (Hermite Posture & Impulse Integration)
# ==============================================================================

def test_mbd_dem_hermite_extrapolation_smoothness():
    """Verify 2nd-order Hermite posture extrapolation across 1,000 substeps is smooth and continuous."""
    p0 = np.array([0.1, 0.2, 0.5])
    v0 = np.array([1.5, -0.8, 2.0])
    a0 = np.array([0.0, -9.81, 0.0])
    dt_mbd = 0.001  # 1 millisecond
    num_substeps = 1000  # 1,000 micro-substeps (dt_dem = 1e-6 s)

    traj = MBDDEMBridge.extrapolate_hermite_posture(
        p0=p0, v0=v0, a0=a0, dt_mbd=dt_mbd, num_substeps=num_substeps
    )

    assert traj.num_substeps == 1000
    assert abs(traj.dt_dem - 1e-6) < 1e-12
    assert traj.is_continuous is True

    # Check maximum step-to-step displacement (must be tiny ~ 1e-6 * |v| < 1e-5 m)
    assert traj.max_step_displacement < 1e-5, f"Step displacement {traj.max_step_displacement} is discontinuous!"

    # Verify endpoint matches analytical Taylor expansion
    p_expected_end = p0 + v0 * dt_mbd + 0.5 * a0 * (dt_mbd ** 2)
    p_actual_end = np.array(traj.positions[-1])
    assert np.allclose(p_actual_end, p_expected_end, atol=1e-10)

    # Verify velocities match
    v_expected_end = v0 + a0 * dt_mbd
    v_actual_end = np.array(traj.velocities[-1])
    assert np.allclose(v_actual_end, v_expected_end, atol=1e-10)


def test_mbd_dem_1000_substep_impulse_and_energy_conservation():
    """Verify 1,000-substep collision force integration accuracy and energy conservation (<0.1%)."""
    num_substeps = 1000
    dt_mbd = 0.001  # 1 ms
    dt_dem = dt_mbd / num_substeps  # 1 microsecond

    # Simulate half-sine collision pulse: F(t) = F_max * sin(pi * t / dt_mbd) along Z
    t_vals = np.linspace(0.0, dt_mbd, num_substeps)
    f_max = 5000.0  # 5000 N peak collision force
    f_z = f_max * np.sin(np.pi * t_vals / dt_mbd)
    forces = np.column_stack([np.zeros(num_substeps), np.zeros(num_substeps), f_z])

    # Mass = 2.0 kg, initial velocity = [0, 0, -2.0] m/s
    mass = 2.0
    v_init = np.array([0.0, 0.0, -2.0], dtype=np.float64)

    # Theoretical impulse of half-sine: J_theory = 2 * F_max * dt_mbd / pi
    j_theory_z = 2.0 * f_max * dt_mbd / np.pi  # ~ 3.183 N*s

    result = MBDDEMBridge.integrate_substep_forces(
        forces=forces,
        dt_dem=dt_dem,
        dt_mbd=dt_mbd,
        mass=mass,
        initial_velocity=v_init,
    )

    # Verification 1: Impulse integration accuracy
    j_integrated_z = result.total_impulse[2]
    rel_impulse_err = abs(j_integrated_z - j_theory_z) / j_theory_z
    assert rel_impulse_err < 0.002, f"Impulse error {rel_impulse_err * 100}% exceeds 0.2%"

    # Verification 2: Time-averaged force returned to MBD
    f_bar_z = result.time_averaged_force[2]
    expected_f_bar = j_theory_z / dt_mbd
    assert abs(f_bar_z - expected_f_bar) / expected_f_bar < 0.002

    # Verification 3: Energy conservation (Work done W == delta_Ek within 0.1%)
    assert result.energy_conserved is True
    assert result.energy_conservation_error_percent <= 0.1, (
        f"Energy error {result.energy_conservation_error_percent}% exceeds 0.1% tolerance!"
    )
    print(f"\n[PHYSICS] MBD-DEM Energy Conservation Discrepancy: {result.energy_conservation_error_percent:.4f}% (SLA <= 0.1%)")
