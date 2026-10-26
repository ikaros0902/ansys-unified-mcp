"""Unit tests for Stage 4 Multiphysics Bridges (STOP & MBD-DEM).

Verifies:
1. STOPAnalysisBridge:
   - SVD 6-DOF rigid body motion separation (Kabsch algorithm).
   - Surface sag residual extraction and pupil normalization (rho in [0, 1], theta in [0, 2*pi)).
   - 37-term Fringe Zernike least-squares polynomial fitting with RMS <= 1%.
   - Standard Zernike (Noll indexing) basis evaluation and fitting.
   - Zemax .ZRN and Grid Sag (.DAT) file export and ZOS-API payload formatting.
2. MBDDEMBridge:
   - Timescale mismatch handling (1,000 substeps).
   - Hermite posture extrapolation (2nd-order Taylor and cubic Hermite spline).
   - Quaternion attitude smooth extrapolation on S^3 unit sphere.
   - Dynamic STL mesh vertex position and velocity transformation.
   - Conservative contact force and moment time integration with energy conservation <= 0.1%.
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import numpy as np
import pytest

from ansys_unified_mcp.products.multiphysics.stop_analysis_bridge import (
    RigidBody6DOF,
    STOPAnalysisBridge,
    ZernikeFitResult,
    FRINGE_37_NAMES,
)
from ansys_unified_mcp.products.multiphysics.mbd_dem_bridge import (
    HermiteTrajectory,
    MBDDEMBridge,
    ParticleContact,
    SubstepForceResult,
)


# =============================================================================
# STOP Analysis Numerical Bridge Tests
# =============================================================================

class TestSTOPAnalysisBridge:
    """Test suite for STOP numerical bridge."""

    @pytest.fixture
    def circular_optical_surface(self):
        """Generate synthetic optical mirror surface nodes."""
        np.random.seed(42)
        n_radii = 25
        n_angles = 40
        radii = np.linspace(0.5, 50.0, n_radii)
        angles = np.linspace(0.0, 2.0 * np.pi, n_angles, endpoint=False)

        r_grid, theta_grid = np.meshgrid(radii, angles)
        r_flat = r_grid.ravel()
        theta_flat = theta_grid.ravel()

        x = r_flat * np.cos(theta_flat)
        y = r_flat * np.sin(theta_flat)
        # Nominal parabolic sag: z = r^2 / (2 * R_curv), R_curv = 500 mm
        z = (r_flat ** 2) / 1000.0
        coords_initial = np.column_stack([x, y, z])
        return coords_initial, 50.0

    def test_svd_rigid_body_separation_exact(self, circular_optical_surface):
        """Test exact recovery of known 6-DOF translation and rotation via SVD."""
        coords_init, norm_r = circular_optical_surface

        # Known rigid body motion:
        # Translation: [3.5, -2.1, 8.4] mm
        # Rotation: Rx = 1.8 deg, Ry = -0.9 deg, Rz = 2.4 deg
        t_known = np.array([3.5, -2.1, 8.4])
        rx_rad = math.radians(1.8)
        ry_rad = math.radians(-0.9)
        rz_rad = math.radians(2.4)

        # Build rotation matrix: R = Rz * Ry * Rx
        cx, sx = math.cos(rx_rad), math.sin(rx_rad)
        cy, sy = math.cos(ry_rad), math.sin(ry_rad)
        cz, sz = math.cos(rz_rad), math.sin(rz_rad)

        rx_mat = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
        ry_mat = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
        rz_mat = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
        r_known = rz_mat @ ry_mat @ rx_mat

        # Apply pure rigid body transformation
        coords_deformed = (coords_init @ r_known.T) + t_known

        six_dof, elastic_local = STOPAnalysisBridge.separate_rigid_body_motion(
            points_initial=coords_init,
            points_deformed=coords_deformed,
        )

        assert isinstance(six_dof, RigidBody6DOF)
        # Verify translation recovery (< 1e-6 mm)
        assert np.allclose(six_dof.translation_vector, t_known, atol=1e-6)

        # Verify rotation angle recovery (< 1e-4 deg)
        assert np.isclose(six_dof.rotation_angles_deg[0], 1.8, atol=1e-4)
        assert np.isclose(six_dof.rotation_angles_deg[1], -0.9, atol=1e-4)
        assert np.isclose(six_dof.rotation_angles_deg[2], 2.4, atol=1e-4)

        # Verify pure rigid motion has near-zero elastic deformation (< 1e-8)
        assert np.allclose(elastic_local, 0.0, atol=1e-8)
        assert six_dof.residual_rms < 1e-8

        # Check Zemax Coordinate Break parameters
        cb = six_dof.zemax_coordinate_break
        assert "decenter_x" in cb and np.isclose(cb["decenter_x"], 3.5, atol=1e-6)
        assert "tilt_x_deg" in cb and np.isclose(cb["tilt_x_deg"], 1.8, atol=1e-4)

    def test_pupil_normalization_and_sag_extraction(self, circular_optical_surface):
        """Test conversion of local Cartesian coordinates to normalized pupil polar coordinates."""
        coords_init, norm_r = circular_optical_surface
        n_pts = len(coords_init)

        # Synthetic elastic deformation in local frame
        elastic_local = np.zeros((n_pts, 3))
        r = np.hypot(coords_init[:, 0], coords_init[:, 1])
        # Add primary spherical aberration sag
        rho_true = r / norm_r
        elastic_local[:, 2] = 0.02 * (6.0 * (rho_true ** 4) - 6.0 * (rho_true ** 2) + 1.0)

        rho, theta, delta_z, eff_norm = STOPAnalysisBridge.extract_surface_sag_and_pupil(
            coords_initial=coords_init,
            elastic_deformation=elastic_local,
            norm_radius=norm_r,
        )

        assert np.all(rho >= 0.0)
        assert np.all(rho <= 1.0 + 1e-6)
        assert np.all(theta >= 0.0)
        assert np.all(theta < 2.0 * np.pi + 1e-6)
        assert np.isclose(eff_norm, norm_r)
        assert np.allclose(delta_z, elastic_local[:, 2])

    def test_fringe_zernike_fit_accuracy_rms_less_than_1_percent(self, circular_optical_surface):
        """Test that 37 Fringe Zernike fitting achieves residual RMS <= 1% on optical aberrations."""
        coords_init, norm_r = circular_optical_surface
        x = coords_init[:, 0]
        y = coords_init[:, 1]
        r = np.hypot(x, y) / norm_r
        theta = np.arctan2(y, x)

        # Synthetic complex optical aberration:
        # Z4 (defocus) + Z5 (astigmatism) + Z7 (coma) + Z9 (spherical) + Z16 (secondary spherical)
        c4, c5, c7, c9, c16 = 0.015, -0.008, 0.006, -0.012, 0.003
        target_sag = (
            c4 * (2.0 * r**2 - 1.0)
            + c5 * (r**2 * np.cos(2.0 * theta))
            + c7 * ((3.0 * r**3 - 2.0 * r) * np.cos(theta))
            + c9 * (6.0 * r**4 - 6.0 * r**2 + 1.0)
            + c16 * (20.0 * r**6 - 30.0 * r**4 + 12.0 * r**2 - 1.0)
        )

        coeffs, fit_result = STOPAnalysisBridge.fit_fringe_zernike(
            x=x,
            y=y,
            delta_z=target_sag,
            norm_radius=norm_r,
            num_terms=37,
        )

        assert isinstance(fit_result, ZernikeFitResult)
        assert len(coeffs) == 37
        assert len(fit_result.term_names) == 37

        # Coefficients recovery verification
        assert np.isclose(coeffs[3], c4, atol=1e-8)   # Z4
        assert np.isclose(coeffs[4], c5, atol=1e-8)   # Z5
        assert np.isclose(coeffs[6], c7, atol=1e-8)   # Z7
        assert np.isclose(coeffs[8], c9, atol=1e-8)   # Z9
        assert np.isclose(coeffs[15], c16, atol=1e-8) # Z16

        # Critical verification condition: RMS residual <= 1%
        assert fit_result.relative_rms_error <= 1.0, f"RMS exceeded 1%: {fit_result.relative_rms_error}%"
        assert fit_result.r_squared >= 0.9999

    def test_standard_zernike_fit_noll_indexing(self, circular_optical_surface):
        """Test Standard Zernike polynomial evaluation up to 231 terms."""
        coords_init, norm_r = circular_optical_surface
        x = coords_init[:, 0]
        y = coords_init[:, 1]
        r = np.hypot(x, y) / norm_r
        theta = np.arctan2(y, x)

        # Standard Zernike fitting with 45 terms
        target_sag = 0.01 * (r ** 2) * np.cos(2 * theta)
        coeffs, fit_result = STOPAnalysisBridge.fit_zernike(
            x=x,
            y=y,
            delta_z=target_sag,
            norm_radius=norm_r,
            polynomial_type="standard",
            num_terms=45,
        )

        assert fit_result.polynomial_type == "standard"
        assert len(coeffs) == 45
        assert fit_result.relative_rms_error <= 1.0

    def test_export_zrn_file_generation(self, circular_optical_surface):
        """Test export to standard Zemax .ZRN coefficient format."""
        coords_init, norm_r = circular_optical_surface
        x = coords_init[:, 0]
        y = coords_init[:, 1]
        delta_z = 0.005 * (x**2 + y**2) / (norm_r**2)

        _, fit_result = STOPAnalysisBridge.fit_fringe_zernike(x=x, y=y, delta_z=delta_z, norm_radius=norm_r)

        with tempfile.TemporaryDirectory() as tmp_dir:
            zrn_path = Path(tmp_dir) / "surface_test.ZRN"
            content = STOPAnalysisBridge.export_zrn(fit_result, zrn_path, unit="mm")

            assert zrn_path.exists()
            assert "Zemax OpticStudio Zernike Coefficients File" in content
            assert f"Clear Aperture Radius: {norm_r:.8e} mm" in content
            lines = [ln for ln in content.splitlines() if not ln.startswith("!")]
            assert len(lines) == 37  # 37 coefficients lines

    def test_export_grid_sag_dat_format(self, circular_optical_surface):
        """Test export to Zemax Grid Sag (.DAT) format."""
        coords_init, norm_r = circular_optical_surface
        x = coords_init[:, 0]
        y = coords_init[:, 1]
        delta_z = 0.002 * (x / norm_r)

        _, fit_result = STOPAnalysisBridge.fit_fringe_zernike(x=x, y=y, delta_z=delta_z, norm_radius=norm_r)

        with tempfile.TemporaryDirectory() as tmp_dir:
            dat_path = Path(tmp_dir) / "grid_sag_test.DAT"
            content = STOPAnalysisBridge.export_grid_sag(fit_result, dat_path, nx=33, ny=33, unit_flag=0)

            assert dat_path.exists()
            header_line = content.splitlines()[0]
            tokens = header_line.split()
            assert tokens[0] == "33" and tokens[1] == "33"
            # 33x33 = 1089 grid points + 1 header line = 1090 lines
            assert len(content.splitlines()) == 1090

    def test_format_zosapi_payload(self, circular_optical_surface):
        """Test structured dictionary generation for Zemax ZOS-API injection."""
        coords_init, norm_r = circular_optical_surface
        t_vec = np.array([1.0, 2.0, 3.0])
        coords_def = coords_init + t_vec

        six_dof, fit_result = STOPAnalysisBridge.execute_stop_pipeline(
            points_initial=coords_init,
            points_deformed=coords_def,
            norm_radius=norm_r,
        )

        payload = STOPAnalysisBridge.format_zosapi_payload(six_dof, fit_result, surface_index=3)
        assert payload["target_surface_index"] == 3
        assert np.isclose(payload["coordinate_break"]["decenter_x"], 1.0, atol=1e-8)
        assert np.isclose(payload["coordinate_break"]["decenter_y"], 2.0, atol=1e-8)
        assert payload["zernike_surface"]["num_terms"] == 37
        assert len(payload["zernike_surface"]["coefficients"]) == 37


# =============================================================================
# MBD-DEM Multi-Timescale Bridge Tests
# =============================================================================

class TestMBDDEMBridge:
    """Test suite for MBD-DEM cross-timescale bridge."""

    def test_hermite_kinematic_extrapolation_1000_substeps(self):
        """Test 2nd-order Taylor-Hermite posture extrapolation across 1,000 substeps."""
        p0 = np.array([0.0, 1.0, 2.0])
        v0 = np.array([10.0, 0.0, -5.0])
        a0 = np.array([0.0, -9.81, 2.0])
        dt_mbd = 0.001  # 1 ms
        num_substeps = 1000

        traj = MBDDEMBridge.extrapolate_hermite_posture(
            p0=p0,
            v0=v0,
            a0=a0,
            dt_mbd=dt_mbd,
            num_substeps=num_substeps,
        )

        assert isinstance(traj, HermiteTrajectory)
        assert traj.num_substeps == 1000
        assert len(traj.positions) == 1000
        assert traj.dt_dem == pytest.approx(1e-6, rel=1e-6)

        # Check endpoint accuracy
        p_expected = p0 + v0 * dt_mbd + 0.5 * a0 * (dt_mbd ** 2)
        v_expected = v0 + a0 * dt_mbd

        assert np.allclose(traj.positions[-1], p_expected, atol=1e-8)
        assert np.allclose(traj.velocities[-1], v_expected, atol=1e-8)
        assert traj.is_continuous
        # Maximum step displacement should be tiny (~ 1e-5 m), preventing geometric step
        assert traj.max_step_displacement < 2e-5

    def test_quaternion_smooth_extrapolation(self):
        """Test smooth unit quaternion attitude extrapolation on S^3."""
        p0 = np.zeros(3)
        v0 = np.zeros(3)
        a0 = np.zeros(3)
        q0 = np.array([1.0, 0.0, 0.0, 0.0])  # Identity orientation
        w0 = np.array([0.0, 0.0, 100.0])    # 100 rad/s rotation around Z
        alpha0 = np.array([0.0, 0.0, 0.0])

        traj = MBDDEMBridge.extrapolate_hermite_posture(
            p0=p0,
            v0=v0,
            a0=a0,
            dt_mbd=0.001,
            num_substeps=1000,
            q0=q0,
            w0=w0,
            alpha0=alpha0,
        )

        quats = np.array(traj.quaternions)
        # All quaternions must remain strictly normalized on unit sphere S^3
        norms = np.linalg.norm(quats, axis=1)
        assert np.allclose(norms, 1.0, atol=1e-12)

        # Expected angle at t = 1 ms: theta = 100 * 0.001 = 0.1 rad
        # q = [cos(0.05), 0, 0, sin(0.05)]
        expected_q = np.array([math.cos(0.05), 0.0, 0.0, math.sin(0.05)])
        assert np.allclose(traj.quaternions[-1], expected_q, atol=1e-6)

    def test_dynamic_stl_mesh_vertex_update(self):
        """Test dynamic boundary STL mesh transformation preventing particle penetration."""
        # Simple triangle STL mesh
        vertices_init = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ])
        pos = np.array([5.0, 2.0, -1.0])
        # 90-degree rotation around Z
        q_90z = np.array([math.cos(math.pi / 4.0), 0.0, 0.0, math.sin(math.pi / 4.0)])
        v_lin = np.array([1.0, 0.0, 0.0])
        omega = np.array([0.0, 0.0, 10.0])

        v_curr, v_nodes = MBDDEMBridge.update_stl_boundary_mesh(
            vertices_initial=vertices_init,
            position=pos,
            quaternion=q_90z,
            linear_velocity=v_lin,
            angular_velocity=omega,
        )

        assert v_curr.shape == (3, 3)
        assert v_nodes.shape == (3, 3)
        # First vertex at origin should translate to pos
        assert np.allclose(v_curr[0], pos, atol=1e-8)
        # Linear velocity of first vertex
        assert np.allclose(v_nodes[0], v_lin, atol=1e-8)

    def test_conservative_contact_force_integration_and_energy_conservation(self):
        """Test time-averaged force integration and strict energy conservation <= 0.1%."""
        dt_mbd = 0.001  # 1 ms
        num_substeps = 1000
        dt_dem = dt_mbd / num_substeps  # 1 us

        # Simulate 1,000 DEM substeps of particle collision force pulse: F(t) = F_max * sin(pi * t / dt_mbd)
        t_arr = np.linspace(0.0, dt_mbd, num_substeps)
        f_max = 500.0  # 500 N peak collision force along X
        forces = np.zeros((num_substeps, 3))
        forces[:, 0] = f_max * np.sin(np.pi * t_arr / dt_mbd)

        # Boundary kinematics: body of mass 2.0 kg moving at v0 = 5.0 m/s
        mass = 2.0
        v0 = np.array([5.0, 0.0, 0.0])
        p0 = np.array([0.0, 0.0, 0.0])
        a0 = np.array([0.0, 0.0, 0.0])

        traj = MBDDEMBridge.extrapolate_hermite_posture(
            p0=p0, v0=v0, a0=a0, dt_mbd=dt_mbd, num_substeps=num_substeps
        )

        force_res = MBDDEMBridge.integrate_substep_forces(
            forces=forces,
            dt_dem=dt_dem,
            dt_mbd=dt_mbd,
            mass=mass,
            initial_velocity=v0,
        )

        assert isinstance(force_res, SubstepForceResult)
        assert force_res.num_substeps == 1000

        # Theoretical impulse: integral(500 * sin(pi*t/dt_mbd)) dt = 500 * (2*dt_mbd / pi)
        expected_impulse_x = f_max * (2.0 * dt_mbd / np.pi)
        assert np.isclose(force_res.total_impulse[0], expected_impulse_x, rtol=1e-3)

        # Time averaged force: F_bar = J / dt_mbd = 500 * 2 / pi ~ 318.31 N
        expected_f_bar = expected_impulse_x / dt_mbd
        assert np.isclose(force_res.time_averaged_force[0], expected_f_bar, rtol=1e-3)

        # Energy conservation condition: error <= 0.1%
        assert force_res.energy_conserved, f"Energy not conserved: {force_res.energy_conservation_error_percent}%"
        assert force_res.energy_conservation_error_percent <= 0.1

    def test_complete_subcycling_pipeline(self):
        """Test end-to-end execute_subcycling_step pipeline."""
        p0 = np.array([0.1, -0.2, 0.5])
        v0 = np.array([2.0, 1.0, 0.0])
        a0 = np.array([0.0, 0.0, -9.81])
        substep_forces = np.ones((1000, 3)) * 10.0  # Constant 10 N force

        traj, force_res = MBDDEMBridge.execute_subcycling_step(
            p0=p0,
            v0=v0,
            a0=a0,
            substep_forces=substep_forces,
            dt_mbd=0.001,
            dt_dem=1e-6,
            mass=5.0,
        )

        assert traj.num_substeps == 1000
        assert force_res.energy_conserved
        assert np.allclose(force_res.time_averaged_force, [10.0, 10.0, 10.0], rtol=1e-3)
