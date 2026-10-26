"""Multi-Body Dynamics (MBD) and Discrete Element Method (DEM) coupling bridge.

Handles 1,000x timescale difference between Motion (dt ~ 1e-3s) and Rocky DEM (dt ~ 1e-6s)
using continuous 2nd-order Hermite posture and quaternion extrapolation, dynamic STL mesh
boundary transformation, and time-averaged collision impulse integration.

All code comments strictly ASCII English.
"""

from __future__ import annotations

import logging
import math
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class HermiteTrajectory(BaseModel):
    """Continuous interpolated kinematic trajectory over DEM substeps."""

    num_substeps: int
    dt_dem: float
    dt_mbd: float
    time_points: list[float]
    positions: list[list[float]]
    velocities: list[list[float]]
    accelerations: list[list[float]]
    quaternions: list[list[float]] = Field(default_factory=list, description="[qw, qx, qy, qz] unit quaternions")
    angular_velocities: list[list[float]] = Field(default_factory=list, description="[wx, wy, wz] rad/s")
    is_continuous: bool = True
    max_step_displacement: float = 0.0


class ParticleContact(BaseModel):
    """Individual particle-to-boundary contact collision."""

    particle_id: int
    contact_point: list[float] = Field(description="[x, y, z] spatial location")
    force: list[float] = Field(description="[Fx, Fy, Fz] contact force in N")
    torque: list[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0], description="[Tx, Ty, Tz] contact torque in N*m")


class SubstepForceResult(BaseModel):
    """Impulse integration and energy conservation results across DEM substeps."""

    num_substeps: int
    total_impulse: list[float] = Field(description="Integrated collision impulse J = integral(F dt) [N*s]")
    total_angular_impulse: list[float] = Field(
        default_factory=lambda: [0.0, 0.0, 0.0],
        description="Integrated angular impulse H = integral(M dt) [N*m*s]",
    )
    time_averaged_force: list[float] = Field(description="Effective force vector returned to MBD F_bar = J / dt_mbd [N]")
    time_averaged_torque: list[float] = Field(
        default_factory=lambda: [0.0, 0.0, 0.0],
        description="Effective torque vector returned to MBD M_bar = H / dt_mbd [N*m]",
    )
    work_done_joules: float = Field(description="Accumulated work W = sum(F_k * v_k * dt) [Joules]")
    kinetic_energy_change: float = Field(description="Kinetic energy variation or macro work delta_Ek [Joules]")
    energy_conservation_error_percent: float = Field(description="Relative discrepancy |W - delta_Ek| / (|W| + eps) * 100")
    energy_conserved: bool = Field(description="True if relative error <= 0.1%")


# -----------------------------------------------------------------------------
# Quaternion Helper Functions
# -----------------------------------------------------------------------------

def _quat_multiply(q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
    """Hamilton product: q1 (x) q2 for quaternions [qw, qx, qy, qz]."""
    w1, x1, y1, z1 = q1[0], q1[1], q1[2], q1[3]
    w2, x2, y2, z2 = q2[0], q2[1], q2[2], q2[3]
    return np.array([
        w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
        w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
        w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
        w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
    ], dtype=np.float64)


def _quat_to_matrix(q: np.ndarray) -> np.ndarray:
    """Convert unit quaternion [qw, qx, qy, qz] to 3x3 rotation matrix."""
    w, x, y, z = q[0], q[1], q[2], q[3]
    return np.array([
        [1.0 - 2.0 * (y * y + z * z), 2.0 * (x * y - w * z), 2.0 * (x * z + w * y)],
        [2.0 * (x * y + w * z), 1.0 - 2.0 * (x * x + z * z), 2.0 * (y * z - w * x)],
        [2.0 * (x * z - w * y), 2.0 * (y * z + w * x), 1.0 - 2.0 * (x * x + y * y)],
    ], dtype=np.float64)


# -----------------------------------------------------------------------------
# MBD-DEM Multi-Timescale Bridge
# -----------------------------------------------------------------------------

class MBDDEMBridge:
    """MBD-DEM cross-timescale bridge for ANSYS Motion and Rocky DEM co-simulation."""

    def __init__(
        self,
        dt_mbd: float = 0.001,  # 1 ms macro step
        dt_dem: float = 1e-06,  # 1 us micro step
    ) -> None:
        self.dt_mbd = dt_mbd
        self.dt_dem = dt_dem
        self.subcycling_ratio = int(round(dt_mbd / dt_dem)) if dt_dem > 0 else 1000

    @staticmethod
    def extrapolate_hermite_posture(
        p0: np.ndarray,
        v0: np.ndarray,
        a0: np.ndarray,
        dt_mbd: float = 0.001,
        num_substeps: int = 1000,
        p1: Optional[np.ndarray] = None,
        v1: Optional[np.ndarray] = None,
        q0: Optional[np.ndarray] = None,
        w0: Optional[np.ndarray] = None,
        alpha0: Optional[np.ndarray] = None,
    ) -> HermiteTrajectory:
        """Extrapolate smooth boundary posture and quaternion across 1,000 DEM substeps.

        Uses 2nd-order Taylor-Hermite kinematic polynomial:
            p(t) = p0 + v0*t + 0.5*a0*t^2
            v(t) = v0 + a0*t
            a(t) = a0
        Or cubic Hermite interpolation if target (p1, v1) is provided.
        Simultaneously performs quaternion orientation extrapolation on unit sphere S^3.
        """
        p0 = np.asarray(p0, dtype=np.float64)
        v0 = np.asarray(v0, dtype=np.float64)
        a0 = np.asarray(a0, dtype=np.float64)

        dt_dem = dt_mbd / float(num_substeps)
        t_steps = np.linspace(0.0, dt_mbd, num_substeps, endpoint=True)

        positions = []
        velocities = []
        accelerations = []
        quaternions = []
        angular_velocities = []

        # Process orientation parameters
        q_init = np.asarray(q0, dtype=np.float64) if q0 is not None else np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)
        q_init = q_init / (np.linalg.norm(q_init) + 1e-15)
        w_init = np.asarray(w0, dtype=np.float64) if w0 is not None else np.zeros(3, dtype=np.float64)
        alpha_init = np.asarray(alpha0, dtype=np.float64) if alpha0 is not None else np.zeros(3, dtype=np.float64)

        if p1 is not None and v1 is not None:
            # Cubic Hermite spline interpolation
            p1 = np.asarray(p1, dtype=np.float64)
            v1 = np.asarray(v1, dtype=np.float64)
            for t in t_steps:
                s = t / dt_mbd
                s2 = s * s
                s3 = s2 * s
                h00 = 2.0 * s3 - 3.0 * s2 + 1.0
                h10 = s3 - 2.0 * s2 + s
                h01 = -2.0 * s3 + 3.0 * s2
                h11 = s3 - s2

                pos = h00 * p0 + h10 * dt_mbd * v0 + h01 * p1 + h11 * dt_mbd * v1
                vel = (
                    (6.0 * s2 - 6.0 * s) * p0 / dt_mbd
                    + (3.0 * s2 - 4.0 * s + 1.0) * v0
                    + (-6.0 * s2 + 6.0 * s) * p1 / dt_mbd
                    + (3.0 * s2 - 2.0 * s) * v1
                )
                acc = (
                    (12.0 * s - 6.0) * p0 / (dt_mbd ** 2)
                    + (6.0 * s - 4.0) * v0 / dt_mbd
                    + (-12.0 * s + 6.0) * p1 / (dt_mbd ** 2)
                    + (6.0 * s - 2.0) * v1 / dt_mbd
                )
                positions.append(pos)
                velocities.append(vel)
                accelerations.append(acc)

                # Smooth orientation extrapolation
                d_theta = w_init * t + 0.5 * alpha_init * (t ** 2)
                ang = np.linalg.norm(d_theta)
                if ang > 1e-12:
                    axis = d_theta / ang
                    half = 0.5 * ang
                    dq = np.array([math.cos(half), axis[0] * math.sin(half), axis[1] * math.sin(half), axis[2] * math.sin(half)])
                else:
                    dq = np.array([1.0, 0.0, 0.0, 0.0])
                q_t = _quat_multiply(dq, q_init)
                q_t /= np.linalg.norm(q_t)
                quaternions.append(q_t.tolist())
                angular_velocities.append((w_init + alpha_init * t).tolist())
        else:
            # 2nd-order Taylor-Hermite extrapolation
            for t in t_steps:
                pos = p0 + v0 * t + 0.5 * a0 * (t ** 2)
                vel = v0 + a0 * t
                acc = a0
                positions.append(pos)
                velocities.append(vel)
                accelerations.append(acc)

                # Smooth orientation extrapolation
                d_theta = w_init * t + 0.5 * alpha_init * (t ** 2)
                ang = np.linalg.norm(d_theta)
                if ang > 1e-12:
                    axis = d_theta / ang
                    half = 0.5 * ang
                    dq = np.array([math.cos(half), axis[0] * math.sin(half), axis[1] * math.sin(half), axis[2] * math.sin(half)])
                else:
                    dq = np.array([1.0, 0.0, 0.0, 0.0])
                q_t = _quat_multiply(dq, q_init)
                q_t /= np.linalg.norm(q_t)
                quaternions.append(q_t.tolist())
                angular_velocities.append((w_init + alpha_init * t).tolist())

        pos_arr = np.array(positions)
        diffs = np.linalg.norm(np.diff(pos_arr, axis=0), axis=1)
        max_step_disp = float(np.max(diffs)) if len(diffs) > 0 else 0.0

        return HermiteTrajectory(
            num_substeps=num_substeps,
            dt_dem=dt_dem,
            dt_mbd=dt_mbd,
            time_points=t_steps.tolist(),
            positions=pos_arr.tolist(),
            velocities=np.array(velocities).tolist(),
            accelerations=np.array(accelerations).tolist(),
            quaternions=quaternions,
            angular_velocities=angular_velocities,
            is_continuous=True,
            max_step_displacement=max_step_disp,
        )

    @staticmethod
    def update_stl_boundary_mesh(
        vertices_initial: np.ndarray,
        position: np.ndarray,
        quaternion: np.ndarray,
        linear_velocity: np.ndarray,
        angular_velocity: np.ndarray,
        center_of_rotation: Optional[np.ndarray] = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Dynamically update STL boundary mesh vertices and surface velocities.

        Prevents geometric steps and non-physical particle penetration in Rocky DEM.

        Args:
            vertices_initial: (K, 3) initial STL vertex coordinates.
            position: (3,) translated position of body reference origin.
            quaternion: (4,) [qw, qx, qy, qz] orientation quaternion.
            linear_velocity: (3,) translational velocity.
            angular_velocity: (3,) rotational velocity.
            center_of_rotation: (3,) reference center of body.

        Returns:
            Tuple of (vertices_current, vertex_velocities) each of shape (K, 3).
        """
        v_init = np.asarray(vertices_initial, dtype=np.float64)
        pos = np.asarray(position, dtype=np.float64)
        quat = np.asarray(quaternion, dtype=np.float64)
        quat /= (np.linalg.norm(quat) + 1e-15)
        v_lin = np.asarray(linear_velocity, dtype=np.float64)
        omega = np.asarray(angular_velocity, dtype=np.float64)

        c_ref = np.asarray(center_of_rotation, dtype=np.float64) if center_of_rotation is not None else np.zeros(3)

        r_mat = _quat_to_matrix(quat)
        rel_pos = v_init - c_ref
        v_curr = pos + (rel_pos @ r_mat.T)

        # Nodal surface velocities: v_node = v_lin + omega x (v_curr - pos)
        r_arms = v_curr - pos
        v_rot = np.cross(omega, r_arms)
        v_nodes = v_lin + v_rot

        return v_curr, v_nodes

    @staticmethod
    def integrate_substep_forces(
        forces: np.ndarray,
        dt_dem: float,
        dt_mbd: float,
        velocities: Optional[np.ndarray] = None,
        positions: Optional[np.ndarray] = None,
        mass: Optional[float] = None,
        initial_velocity: Optional[np.ndarray] = None,
        contact_points: Optional[np.ndarray] = None,
        reference_center: Optional[np.ndarray] = None,
        torques: Optional[np.ndarray] = None,
        angular_velocities: Optional[np.ndarray] = None,
    ) -> SubstepForceResult:
        """Compute time-averaged collision impulse and verify energy conservation across 1,000 substeps.

        Integral formula:
            F_ext(T_{n+1}) = (1 / Delta_T) * integral_{T_n}^{T_{n+1}} sum_k F_k(t) dt
        """
        f = np.asarray(forces, dtype=np.float64)
        num_substeps = len(f)

        # Determine effective integration step (trapezoidal spacing vs Riemann dx)
        if num_substeps > 1 and np.isclose(dt_dem * (num_substeps - 1), dt_mbd, rtol=0.01):
            dt_step = dt_mbd / (num_substeps - 1)
            impulse = np.trapezoid(f, dx=dt_step, axis=0)
        else:
            dt_step = dt_dem
            impulse = np.sum(f * dt_step, axis=0)

        # Time-averaged force F_bar = J / dt_mbd
        time_averaged_force = impulse / dt_mbd

        # Moment / torque integration if points or torques are given
        c_ref = np.asarray(reference_center, dtype=np.float64) if reference_center is not None else np.zeros(3)
        angular_impulse = np.zeros(3, dtype=np.float64)

        if torques is not None:
            t_arr = np.asarray(torques, dtype=np.float64)
            if num_substeps > 1 and np.isclose(dt_dem * (num_substeps - 1), dt_mbd, rtol=0.01):
                angular_impulse += np.trapezoid(t_arr, dx=dt_step, axis=0)
            else:
                angular_impulse += np.sum(t_arr * dt_step, axis=0)

        if contact_points is not None:
            p_arr = np.asarray(contact_points, dtype=np.float64)
            if p_arr.ndim == 2 and p_arr.shape[0] == num_substeps:
                r_arms = p_arr - c_ref
                moments = np.cross(r_arms, f)
                if num_substeps > 1 and np.isclose(dt_dem * (num_substeps - 1), dt_mbd, rtol=0.01):
                    angular_impulse += np.trapezoid(moments, dx=dt_step, axis=0)
                else:
                    angular_impulse += np.sum(moments * dt_step, axis=0)

        time_averaged_torque = angular_impulse / dt_mbd

        # Energy conservation check
        work_done = 0.0
        delta_ek = 0.0
        energy_error = 0.0
        energy_conserved = True

        if velocities is not None:
            v = np.asarray(velocities, dtype=np.float64)
            power_lin = np.sum(f * v, axis=1)
            if num_substeps > 1 and np.isclose(dt_dem * (num_substeps - 1), dt_mbd, rtol=0.01):
                work_done = float(np.trapezoid(power_lin, dx=dt_step))
            else:
                work_done = float(np.sum(power_lin * dt_step))

            if angular_velocities is not None and torques is not None:
                w_arr = np.asarray(angular_velocities, dtype=np.float64)
                power_rot = np.sum(np.asarray(torques, dtype=np.float64) * w_arr, axis=1)
                if num_substeps > 1 and np.isclose(dt_dem * (num_substeps - 1), dt_mbd, rtol=0.01):
                    work_done += float(np.trapezoid(power_rot, dx=dt_step))
                else:
                    work_done += float(np.sum(power_rot * dt_step))

            # Equivalent work transferred to MBD macro step:
            # W_macro = F_bar . Delta_x + M_bar . Delta_theta
            if positions is not None:
                pos_arr = np.asarray(positions, dtype=np.float64)
                delta_x = pos_arr[-1] - pos_arr[0]
            else:
                if num_substeps > 1 and np.isclose(dt_dem * (num_substeps - 1), dt_mbd, rtol=0.01):
                    delta_x = np.trapezoid(v, dx=dt_step, axis=0)
                else:
                    delta_x = np.sum(v * dt_step, axis=0)

            work_mbd = float(np.dot(time_averaged_force, delta_x))
            if angular_velocities is not None:
                w_arr = np.asarray(angular_velocities, dtype=np.float64)
                if num_substeps > 1 and np.isclose(dt_dem * (num_substeps - 1), dt_mbd, rtol=0.01):
                    delta_theta = np.trapezoid(w_arr, dx=dt_step, axis=0)
                else:
                    delta_theta = np.sum(w_arr * dt_step, axis=0)
                work_mbd += float(np.dot(time_averaged_torque, delta_theta))

            delta_ek = work_mbd
            abs_diff = abs(work_done - work_mbd)
            denom = max(abs(work_done), abs(work_mbd), 1e-9)
            energy_error = (abs_diff / denom) * 100.0
            energy_conserved = energy_error <= 0.1  # tolerance <= 0.1%

        elif mass is not None and initial_velocity is not None:
            # Simulate velocity progression under impulse (symplectic midpoint)
            v_curr = np.asarray(initial_velocity, dtype=np.float64).copy()
            work_done = 0.0
            ek_start = 0.5 * mass * np.dot(v_curr, v_curr)

            for k in range(num_substeps):
                fk = f[k]
                v_mid = v_curr + 0.5 * (fk / mass) * dt_step
                work_done += float(np.dot(fk, v_mid) * dt_step)
                v_curr += (fk / mass) * dt_step

            ek_end = 0.5 * mass * np.dot(v_curr, v_curr)
            delta_ek = float(ek_end - ek_start)

            abs_diff = abs(work_done - delta_ek)
            denom = max(abs(work_done), abs(delta_ek), 1e-9)
            energy_error = (abs_diff / denom) * 100.0
            energy_conserved = energy_error <= 0.1

        return SubstepForceResult(
            num_substeps=num_substeps,
            total_impulse=impulse.tolist(),
            total_angular_impulse=angular_impulse.tolist(),
            time_averaged_force=time_averaged_force.tolist(),
            time_averaged_torque=time_averaged_torque.tolist(),
            work_done_joules=work_done,
            kinetic_energy_change=delta_ek,
            energy_conservation_error_percent=energy_error,
            energy_conserved=energy_conserved,
        )

    @classmethod
    def execute_subcycling_step(
        cls,
        p0: np.ndarray,
        v0: np.ndarray,
        a0: np.ndarray,
        substep_forces: np.ndarray,
        dt_mbd: float = 0.001,
        dt_dem: float = 1e-06,
        mass: Optional[float] = None,
        q0: Optional[np.ndarray] = None,
        w0: Optional[np.ndarray] = None,
        alpha0: Optional[np.ndarray] = None,
    ) -> tuple[HermiteTrajectory, SubstepForceResult]:
        """Execute complete MBD-DEM subcycling coupling step."""
        num_substeps = int(round(dt_mbd / dt_dem))
        trajectory = cls.extrapolate_hermite_posture(
            p0=p0,
            v0=v0,
            a0=a0,
            dt_mbd=dt_mbd,
            num_substeps=num_substeps,
            q0=q0,
            w0=w0,
            alpha0=alpha0,
        )
        force_res = cls.integrate_substep_forces(
            forces=substep_forces,
            dt_dem=dt_dem,
            dt_mbd=dt_mbd,
            velocities=np.array(trajectory.velocities),
            positions=np.array(trajectory.positions),
            mass=mass,
        )
        return trajectory, force_res
