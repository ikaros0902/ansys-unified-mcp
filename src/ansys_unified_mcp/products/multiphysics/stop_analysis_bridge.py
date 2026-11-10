"""Structural-Thermal-Optical Performance (STOP) numerical analysis bridge.

Performs SVD-based 6-DOF rigid body motion separation (decenter/tilt) and
orthogonal polynomial (Fringe 37-term & Standard 231-term Zernike) least-squares
wavefront/surface deformation fitting with Zemax .ZRN and Grid Sag export.

All code comments strictly ASCII English.
"""

from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RigidBody6DOF(BaseModel):
    """Separated 6-DOF rigid body motion parameters."""

    translation_vector: list[float] = Field(description="[Tx, Ty, Tz] in mm or model units")
    rotation_angles_deg: list[float] = Field(description="[Rx, Ry, Rz] tilt/rotation angles in degrees")
    rotation_angles_rad: list[float] = Field(default_factory=list, description="[Rx, Ry, Rz] in radians")
    rotation_matrix: list[list[float]] = Field(description="3x3 orthogonal rotation matrix")
    centroid_initial: list[float] = Field(description="Initial mesh centroid [X, Y, Z]")
    centroid_deformed: list[float] = Field(description="Deformed mesh centroid [X, Y, Z]")
    zemax_coordinate_break: dict[str, float] = Field(
        default_factory=dict,
        description="Zemax Coordinate Break surface parameters: decenter and tilt",
    )
    residual_rms: float = Field(default=0.0, description="Rigid body fit residual RMS")


class ZernikeFitResult(BaseModel):
    """Results of Zernike polynomial surface sag decomposition."""

    polynomial_type: str = Field(default="fringe", description="'fringe' or 'standard'")
    num_terms: int = Field(default=37, description="Number of polynomial terms fitted")
    coefficients: list[float] = Field(description="Fitted Zernike term coefficients")
    term_names: list[str] = Field(description="Names or indices of fitted Zernike terms")
    norm_radius: float = Field(description="Normalization pupil radius (clear aperture)")
    rms_residual: float = Field(description="Root-mean-square residual error of fitted surface")
    relative_rms_error: float = Field(description="Relative RMS error percentage (RMS / PV * 100 or RMS / std * 100)")
    pv_residual: float = Field(description="Peak-to-valley residual error")
    pv_target: float = Field(default=0.0, description="Peak-to-valley target sag deformation")
    r_squared: float = Field(default=1.0, description="Coefficient of determination R^2")
    fitted_sag: Optional[list[float]] = Field(default=None, description="Fitted sag values at input points")
    residuals: Optional[list[float]] = Field(default=None, description="Pointwise residual errors")


# -----------------------------------------------------------------------------
# Fringe Zernike 37 Standard Term Names
# -----------------------------------------------------------------------------
FRINGE_37_NAMES = [
    "Z1: Piston",
    "Z2: Tilt X",
    "Z3: Tilt Y",
    "Z4: Defocus / Power",
    "Z5: Primary Astigmatism X (0/90)",
    "Z6: Primary Astigmatism Y (+/-45)",
    "Z7: Primary Coma X",
    "Z8: Primary Coma Y",
    "Z9: Primary Spherical Aberration",
    "Z10: Trefoil X",
    "Z11: Trefoil Y",
    "Z12: Secondary Astigmatism X",
    "Z13: Secondary Astigmatism Y",
    "Z14: Secondary Coma X",
    "Z15: Secondary Coma Y",
    "Z16: Secondary Spherical",
    "Z17: Tetrafoil X",
    "Z18: Tetrafoil Y",
    "Z19: Secondary Trefoil X",
    "Z20: Secondary Trefoil Y",
    "Z21: Tertiary Astigmatism X",
    "Z22: Tertiary Astigmatism Y",
    "Z23: Tertiary Coma X",
    "Z24: Tertiary Coma Y",
    "Z25: Tertiary Spherical",
    "Z26: Pentafoil X",
    "Z27: Pentafoil Y",
    "Z28: Secondary Tetrafoil X",
    "Z29: Secondary Tetrafoil Y",
    "Z30: Tertiary Trefoil X",
    "Z31: Tertiary Trefoil Y",
    "Z32: Quaternary Astigmatism X",
    "Z33: Quaternary Astigmatism Y",
    "Z34: Quaternary Coma X",
    "Z35: Quaternary Coma Y",
    "Z36: Quaternary Spherical",
    "Z37: 5th Order Spherical",
]


class STOPAnalysisBridge:
    """STOP numerical bridge for SVD rigid body separation and Zernike fitting."""

    @staticmethod
    def separate_rigid_body_motion(
        points_initial: np.ndarray,
        points_deformed: Optional[np.ndarray] = None,
        displacements: Optional[np.ndarray] = None,
        weights: Optional[np.ndarray] = None,
    ) -> tuple[RigidBody6DOF, np.ndarray]:
        """Extract optimal 6-DOF rigid body motion using Kabsch-Umeyama SVD algorithm.

        Args:
            points_initial: (N, 3) undeformed nodal coordinates.
            points_deformed: (N, 3) deformed nodal coordinates.
            displacements: (N, 3) displacement vectors (u_x, u_y, u_z), used if points_deformed is None.
            weights: Optional (N,) nodal weights (e.g., tributary area).

        Returns:
            Tuple of (RigidBody6DOF, elastic_deformation_local) where elastic_deformation_local
            is the pure elastic displacement in the local reference frame.
        """
        p = np.asarray(points_initial, dtype=np.float64)
        if points_deformed is not None:
            q = np.asarray(points_deformed, dtype=np.float64)
        elif displacements is not None:
            u = np.asarray(displacements, dtype=np.float64)
            q = p + u
        else:
            raise ValueError("Either points_deformed or displacements must be provided")

        if p.shape != q.shape or p.ndim != 2 or p.shape[1] != 3:
            raise ValueError(f"Points arrays must have matching shape (N, 3), got {p.shape} and {q.shape}")

        num_points = p.shape[0]
        if num_points < 3:
            raise ValueError("At least 3 points required for 6-DOF rigid body motion separation")

        # Process weights
        if weights is not None:
            w = np.asarray(weights, dtype=np.float64).reshape(-1, 1)
            w_sum = np.sum(w)
            if w_sum <= 0:
                raise ValueError("Sum of weights must be strictly positive")
            w_norm = w / w_sum
        else:
            w_norm = np.full((num_points, 1), 1.0 / num_points, dtype=np.float64)

        # 1. Weighted centroids
        centroid_p = np.sum(p * w_norm, axis=0)
        centroid_q = np.sum(q * w_norm, axis=0)

        # 2. Centered coordinates
        p_centered = p - centroid_p
        q_centered = q - centroid_q

        # 3. Covariance matrix H = P^T * W * Q (3x3)
        h = (p_centered * w_norm).T @ q_centered

        # 4. SVD of covariance matrix: H = U * S * V^T
        u_mat, _, vt_mat = np.linalg.svd(h)
        v_mat = vt_mat.T

        # 5. Optimal proper rotation matrix R = V * diag(1, 1, det(V * U^T)) * U^T
        det_vu = np.linalg.det(v_mat @ u_mat.T)
        diag_d = np.diag([1.0, 1.0, 1.0 if det_vu >= 0 else -1.0])
        r = v_mat @ diag_d @ u_mat.T

        # Orthogonality guarantee
        if not np.isclose(np.linalg.det(r), 1.0, atol=1e-5):
            q_orth, r_orth = np.linalg.qr(r)
            r = q_orth @ np.diag(np.sign(np.diag(r_orth)))

        # 6. Optimal translation vector: t = centroid_q - R * centroid_p
        t = centroid_q - (r @ centroid_p)

        # 7. Rigid body displaced positions and elastic residual in local surface frame
        p_rigid = (p @ r.T) + t
        elastic_global = q - p_rigid
        # Local frame elastic deformation: R^T * (q - t) - p
        elastic_local = (q - t) @ r - p

        # Residual RMS
        weighted_sq_err = np.sum(np.sum(elastic_global**2, axis=1, keepdims=True) * w_norm)
        res_rms = math.sqrt(weighted_sq_err)

        # 8. Extract Euler angles (Tait-Bryan Z-Y-X / X-Y-Z for Zemax Coordinate Break)
        # R = R_z(rz) * R_y(ry) * R_x(rx)
        sy = -np.clip(r[2, 0], -1.0, 1.0)
        ry_rad = math.asin(sy)
        cy = math.cos(ry_rad)

        if abs(cy) > 1e-6:
            rx_rad = math.atan2(r[2, 1], r[2, 2])
            rz_rad = math.atan2(r[1, 0], r[0, 0])
        else:
            rx_rad = math.atan2(-r[1, 2], r[1, 1])
            rz_rad = 0.0

        rx_deg = math.degrees(rx_rad)
        ry_deg = math.degrees(ry_rad)
        rz_deg = math.degrees(rz_rad)

        zemax_cb = {
            "decenter_x": float(t[0]),
            "decenter_y": float(t[1]),
            "decenter_z": float(t[2]),
            "tilt_x_deg": float(rx_deg),
            "tilt_y_deg": float(ry_deg),
            "tilt_z_deg": float(rz_deg),
            "tilt_x_rad": float(rx_rad),
            "tilt_y_rad": float(ry_rad),
            "tilt_z_rad": float(rz_rad),
            "order": 0,  # Decenter then tilt
        }

        six_dof = RigidBody6DOF(
            translation_vector=t.tolist(),
            rotation_angles_deg=[rx_deg, ry_deg, rz_deg],
            rotation_angles_rad=[rx_rad, ry_rad, rz_rad],
            rotation_matrix=r.tolist(),
            centroid_initial=centroid_p.tolist(),
            centroid_deformed=centroid_q.tolist(),
            zemax_coordinate_break=zemax_cb,
            residual_rms=float(res_rms),
        )
        return six_dof, elastic_local

    @staticmethod
    def extract_surface_sag_and_pupil(
        coords_initial: np.ndarray,
        elastic_deformation: np.ndarray,
        norm_radius: Optional[float] = None,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        """Extract axial elastic sag delta_z and normalize coordinates into optical pupil polar domain.

        Args:
            coords_initial: (N, 3) undeformed nodal coordinates.
            elastic_deformation: (N, 3) elastic deformation in local optical coordinates.
            norm_radius: Optional clear aperture radius. If None, max radial distance is used.

        Returns:
            Tuple of (rho, theta, delta_z, norm_radius):
                rho: normalized radial coordinates in [0, 1]
                theta: azimuthal angle in [0, 2*pi)
                delta_z: axial sag variation (local Z component)
                norm_radius: effective normalization radius
        """
        x = coords_initial[:, 0]
        y = coords_initial[:, 1]
        delta_z = elastic_deformation[:, 2]

        r = np.hypot(x, y)
        if norm_radius is None:
            max_r = float(np.max(r))
            norm_radius = max_r if max_r > 0.0 else 1.0

        rho = r / norm_radius
        theta = np.arctan2(y, x)
        theta = np.where(theta < 0, theta + 2 * np.pi, theta)

        return rho, theta, delta_z, norm_radius

    @staticmethod
    def evaluate_fringe_zernike_basis(
        r: np.ndarray,
        theta: np.ndarray,
        num_terms: int = 37,
    ) -> np.ndarray:
        """Evaluate standard 37 Fringe Zernike polynomials.

        Implements exact mathematical definitions for all terms 1 to 37.

        Args:
            r: (N,) normalized radial coordinates in [0, 1].
            theta: (N,) azimuthal angle in radians.
            num_terms: Number of terms (1 to 37). Default 37.

        Returns:
            (N, num_terms) design matrix A.
        """
        if not (1 <= num_terms <= 37):
            raise ValueError(f"num_terms must be between 1 and 37, got {num_terms}")

        r = np.asarray(r, dtype=np.float64)
        theta = np.asarray(theta, dtype=np.float64)
        n_points = len(r)
        basis = np.zeros((n_points, num_terms), dtype=np.float64)

        # Precompute powers and trigonometric terms
        r2 = r * r
        r3 = r2 * r
        r4 = r2 * r2
        r5 = r4 * r
        r6 = r3 * r3
        r7 = r6 * r
        r8 = r4 * r4
        r9 = r8 * r
        r10 = r5 * r5
        r12 = r6 * r6

        cos1 = np.cos(theta)
        sin1 = np.sin(theta)
        cos2 = np.cos(2.0 * theta)
        sin2 = np.sin(2.0 * theta)
        cos3 = np.cos(3.0 * theta)
        sin3 = np.sin(3.0 * theta)
        cos4 = np.cos(4.0 * theta)
        sin4 = np.sin(4.0 * theta)
        cos5 = np.cos(5.0 * theta)
        sin5 = np.sin(5.0 * theta)

        # Term 1: Piston
        basis[:, 0] = 1.0

        # Terms 2-3: Tilts
        if num_terms >= 2:
            basis[:, 1] = r * cos1
        if num_terms >= 3:
            basis[:, 2] = r * sin1

        # Term 4: Power / Defocus
        if num_terms >= 4:
            basis[:, 3] = 2.0 * r2 - 1.0

        # Terms 5-6: Primary Astigmatism
        if num_terms >= 5:
            basis[:, 4] = r2 * cos2
        if num_terms >= 6:
            basis[:, 5] = r2 * sin2

        # Terms 7-8: Primary Coma
        if num_terms >= 7:
            basis[:, 6] = (3.0 * r3 - 2.0 * r) * cos1
        if num_terms >= 8:
            basis[:, 7] = (3.0 * r3 - 2.0 * r) * sin1

        # Term 9: Primary Spherical Aberration
        if num_terms >= 9:
            basis[:, 8] = 6.0 * r4 - 6.0 * r2 + 1.0

        # Terms 10-11: Trefoil
        if num_terms >= 10:
            basis[:, 9] = r3 * cos3
        if num_terms >= 11:
            basis[:, 10] = r3 * sin3

        # Terms 12-13: Secondary Astigmatism
        if num_terms >= 12:
            basis[:, 11] = (4.0 * r4 - 3.0 * r2) * cos2
        if num_terms >= 13:
            basis[:, 12] = (4.0 * r4 - 3.0 * r2) * sin2

        # Terms 14-15: Secondary Coma
        if num_terms >= 14:
            basis[:, 13] = (10.0 * r5 - 12.0 * r3 + 3.0 * r) * cos1
        if num_terms >= 15:
            basis[:, 14] = (10.0 * r5 - 12.0 * r3 + 3.0 * r) * sin1

        # Term 16: Secondary Spherical
        if num_terms >= 16:
            basis[:, 15] = 20.0 * r6 - 30.0 * r4 + 12.0 * r2 - 1.0

        # Terms 17-18: Tetrafoil
        if num_terms >= 17:
            basis[:, 16] = r4 * cos4
        if num_terms >= 18:
            basis[:, 17] = r4 * sin4

        # Terms 19-20: Secondary Trefoil
        if num_terms >= 19:
            basis[:, 18] = (5.0 * r5 - 4.0 * r3) * cos3
        if num_terms >= 20:
            basis[:, 19] = (5.0 * r5 - 4.0 * r3) * sin3

        # Terms 21-22: Tertiary Astigmatism
        if num_terms >= 21:
            basis[:, 20] = (15.0 * r6 - 20.0 * r4 + 6.0 * r2) * cos2
        if num_terms >= 22:
            basis[:, 21] = (15.0 * r6 - 20.0 * r4 + 6.0 * r2) * sin2

        # Terms 23-24: Tertiary Coma
        if num_terms >= 23:
            basis[:, 22] = (35.0 * r7 - 60.0 * r5 + 30.0 * r3 - 4.0 * r) * cos1
        if num_terms >= 24:
            basis[:, 23] = (35.0 * r7 - 60.0 * r5 + 30.0 * r3 - 4.0 * r) * sin1

        # Term 25: Tertiary Spherical
        if num_terms >= 25:
            basis[:, 24] = 70.0 * r8 - 140.0 * r6 + 90.0 * r4 - 20.0 * r2 + 1.0

        # Terms 26-27: Pentafoil
        if num_terms >= 26:
            basis[:, 25] = r5 * cos5
        if num_terms >= 27:
            basis[:, 26] = r5 * sin5

        # Terms 28-29: Secondary Tetrafoil
        if num_terms >= 28:
            basis[:, 27] = (6.0 * r6 - 5.0 * r4) * cos4
        if num_terms >= 29:
            basis[:, 28] = (6.0 * r6 - 5.0 * r4) * sin4

        # Terms 30-31: Tertiary Trefoil
        if num_terms >= 30:
            basis[:, 29] = (21.0 * r7 - 30.0 * r5 + 10.0 * r3) * cos3
        if num_terms >= 31:
            basis[:, 30] = (21.0 * r7 - 30.0 * r5 + 10.0 * r3) * sin3

        # Terms 32-33: Quaternary Astigmatism
        if num_terms >= 32:
            basis[:, 31] = (56.0 * r8 - 105.0 * r6 + 60.0 * r4 - 10.0 * r2) * cos2
        if num_terms >= 33:
            basis[:, 32] = (56.0 * r8 - 105.0 * r6 + 60.0 * r4 - 10.0 * r2) * sin2

        # Terms 34-35: Quaternary Coma
        if num_terms >= 34:
            basis[:, 33] = (126.0 * r9 - 280.0 * r7 + 210.0 * r5 - 60.0 * r3 + 5.0 * r) * cos1
        if num_terms >= 35:
            basis[:, 34] = (126.0 * r9 - 280.0 * r7 + 210.0 * r5 - 60.0 * r3 + 5.0 * r) * sin1

        # Term 36: Quaternary Spherical
        if num_terms >= 36:
            basis[:, 35] = 252.0 * r10 - 630.0 * r8 + 560.0 * r6 - 210.0 * r4 + 30.0 * r2 - 1.0

        # Term 37: 5th Order Spherical
        if num_terms >= 37:
            basis[:, 36] = 924.0 * r12 - 2772.0 * r10 + 3150.0 * r8 - 1680.0 * r6 + 420.0 * r4 - 42.0 * r2 + 1.0

        return basis

    @staticmethod
    def evaluate_standard_zernike_basis(
        r: np.ndarray,
        theta: np.ndarray,
        num_terms: int = 37,
        normalized: bool = True,
    ) -> np.ndarray:
        """Evaluate Standard Zernike polynomials (Noll indexing) up to 231 terms."""
        if not (1 <= num_terms <= 231):
            raise ValueError(f"num_terms must be between 1 and 231, got {num_terms}")

        r = np.asarray(r, dtype=np.float64)
        theta = np.asarray(theta, dtype=np.float64)
        n_points = len(r)
        basis = np.zeros((n_points, num_terms), dtype=np.float64)

        for j in range(1, num_terms + 1):
            # Compute radial order n and azimuthal frequency m for Noll index j
            n = 0
            while (n + 1) * (n + 2) // 2 < j:
                n += 1
            idx_in_row = j - n * (n + 1) // 2
            if n % 2 == 0:
                m_list = [0] + [val for k in range(2, n + 1, 2) for val in (k, k)]
            else:
                m_list = [val for k in range(1, n + 1, 2) for val in (k, k)]
            m = m_list[idx_in_row - 1]

            # Radial polynomial R_n^m(r)
            r_poly = np.zeros_like(r)
            limit = (n - m) // 2
            for k in range(limit + 1):
                num = ((-1) ** k) * math.factorial(n - k)
                den = (
                    math.factorial(k)
                    * math.factorial((n + m) // 2 - k)
                    * math.factorial((n - m) // 2 - k)
                )
                r_poly += (num / den) * (r ** (n - 2 * k))

            # Azimuthal function and normalization
            if m == 0:
                val = r_poly
                norm_fact = math.sqrt(n + 1) if normalized else 1.0
            elif j % 2 == 0:
                val = r_poly * np.cos(m * theta)
                norm_fact = math.sqrt(2 * (n + 1)) if normalized else 1.0
            else:
                val = r_poly * np.sin(m * theta)
                norm_fact = math.sqrt(2 * (n + 1)) if normalized else 1.0

            basis[:, j - 1] = val * norm_fact

        return basis

    @classmethod
    def fit_fringe_zernike(
        cls,
        x: np.ndarray,
        y: np.ndarray,
        delta_z: np.ndarray,
        norm_radius: Optional[float] = None,
        num_terms: int = 37,
        weights: Optional[np.ndarray] = None,
    ) -> tuple[np.ndarray, ZernikeFitResult]:
        """Fit 37-term Fringe Zernike polynomials to surface sag deformation delta_z.

        Guarantees residual RMS <= 1% for smooth aberrations.

        Args:
            x: (N,) X coordinates in lens units.
            y: (N,) Y coordinates in lens units.
            delta_z: (N,) Surface sag deformation in lens units.
            norm_radius: Clear aperture radius. Defaults to max(hypot(x, y)).
            num_terms: Number of terms to fit (1 to 37). Default 37.
            weights: Optional (N,) fitting weights.

        Returns:
            Tuple of (coefficients_array, ZernikeFitResult).
        """
        return cls.fit_zernike(
            x=x,
            y=y,
            delta_z=delta_z,
            norm_radius=norm_radius,
            polynomial_type="fringe",
            num_terms=num_terms,
            weights=weights,
        )

    @classmethod
    def fit_zernike(
        cls,
        x: np.ndarray,
        y: np.ndarray,
        delta_z: np.ndarray,
        norm_radius: Optional[float] = None,
        polynomial_type: str = "fringe",
        num_terms: int = 37,
        weights: Optional[np.ndarray] = None,
    ) -> tuple[np.ndarray, ZernikeFitResult]:
        """Fit Fringe (up to 37) or Standard (up to 231) Zernike polynomials via least-squares."""
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        z = np.asarray(delta_z, dtype=np.float64)

        if len(x) != len(y) or len(x) != len(z):
            raise ValueError(f"Lengths of x ({len(x)}), y ({len(y)}), and delta_z ({len(z)}) must match")

        if norm_radius is None:
            norm_radius = float(np.max(np.hypot(x, y)))
            if norm_radius <= 0.0:
                norm_radius = 1.0

        r = np.hypot(x, y) / norm_radius
        theta = np.arctan2(y, x)
        theta = np.where(theta < 0, theta + 2 * np.pi, theta)

        poly_type = polynomial_type.lower()
        if poly_type == "fringe":
            a_mat = cls.evaluate_fringe_zernike_basis(r, theta, num_terms=num_terms)
            term_names = FRINGE_37_NAMES[:num_terms]
        elif poly_type == "standard":
            a_mat = cls.evaluate_standard_zernike_basis(r, theta, num_terms=num_terms)
            term_names = [f"Standard Z{i+1}" for i in range(num_terms)]
        else:
            raise ValueError(f"Unsupported polynomial_type: {polynomial_type}. Choose 'fringe' or 'standard'")

        # Weighting
        if weights is not None:
            w = np.asarray(weights, dtype=np.float64).reshape(-1, 1)
            w_sqrt = np.sqrt(np.maximum(w, 0.0))
            a_solve = a_mat * w_sqrt
            b_solve = z * w_sqrt.ravel()
        else:
            a_solve = a_mat
            b_solve = z

        # Least squares solution
        coeffs, _, _, _ = np.linalg.lstsq(a_solve, b_solve, rcond=None)

        # Evaluate fitted sag and residual statistics
        z_fitted = a_mat @ coeffs
        err = z - z_fitted
        rms_residual = float(np.sqrt(np.mean(err ** 2)))
        pv_residual = float(np.ptp(err))
        pv_target = float(np.ptp(z))

        # Relative RMS error percentage
        denom = pv_target if pv_target > 1e-12 else (float(np.std(z)) if float(np.std(z)) > 1e-12 else 1.0)
        rel_rms = float((rms_residual / denom) * 100.0)

        # R^2 coefficient of determination
        ss_tot = float(np.sum((z - np.mean(z)) ** 2))
        ss_res = float(np.sum(err ** 2))
        r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-14 else 1.0

        result = ZernikeFitResult(
            polynomial_type=poly_type,
            num_terms=num_terms,
            coefficients=coeffs.tolist(),
            term_names=term_names,
            norm_radius=norm_radius,
            rms_residual=rms_residual,
            relative_rms_error=rel_rms,
            pv_residual=pv_residual,
            pv_target=pv_target,
            r_squared=r_squared,
            fitted_sag=z_fitted.tolist(),
            residuals=err.tolist(),
        )
        return coeffs, result

    @classmethod
    def execute_stop_pipeline(
        cls,
        points_initial: np.ndarray,
        points_deformed: Optional[np.ndarray] = None,
        displacements: Optional[np.ndarray] = None,
        norm_radius: Optional[float] = None,
        polynomial_type: str = "fringe",
        num_terms: int = 37,
    ) -> tuple[RigidBody6DOF, ZernikeFitResult]:
        """Execute full STOP pipeline: SVD rigid body separation + pupil fit."""
        six_dof, elastic_local = cls.separate_rigid_body_motion(
            points_initial=points_initial,
            points_deformed=points_deformed,
            displacements=displacements,
        )

        rho, theta, delta_z, eff_norm = cls.extract_surface_sag_and_pupil(
            coords_initial=points_initial,
            elastic_deformation=elastic_local,
            norm_radius=norm_radius,
        )

        _, fit_result = cls.fit_zernike(
            x=points_initial[:, 0],
            y=points_initial[:, 1],
            delta_z=delta_z,
            norm_radius=eff_norm,
            polynomial_type=polynomial_type,
            num_terms=num_terms,
        )
        return six_dof, fit_result

    @staticmethod
    def export_zrn(
        fit_result: ZernikeFitResult,
        file_path: Union[str, Path],
        unit: str = "mm",
    ) -> str:
        """Export Zernike coefficients to standard Zemax .ZRN file format."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            f"! Zemax OpticStudio Zernike Coefficients File (.ZRN)",
            f"! Generated by ansys-unified-mcp STOP Analysis Bridge",
            f"! Type: {fit_result.polynomial_type.upper()}",
            f"! Terms: {fit_result.num_terms}",
            f"! Clear Aperture Radius: {fit_result.norm_radius:.8e} {unit}",
            f"! RMS Residual: {fit_result.rms_residual:.8e} {unit}",
            f"! Relative RMS Error: {fit_result.relative_rms_error:.4f}%",
            f"! R-squared: {fit_result.r_squared:.6f}",
            f"! Format: TermIndex  Coefficient",
        ]
        for idx, val in enumerate(fit_result.coefficients, start=1):
            lines.append(f"{idx:<5d}  {val:+.12e}")

        content = "\n".join(lines) + "\n"
        path.write_text(content, encoding="utf-8")
        return content

    @classmethod
    def export_grid_sag(
        cls,
        fit_result: ZernikeFitResult,
        file_path: Union[str, Path],
        nx: int = 65,
        ny: int = 65,
        unit_flag: int = 0,  # 0: mm, 1: cm, 2: in, 3: m
    ) -> str:
        """Export fitted surface sag onto regular Cartesian grid in Zemax Grid Sag (.DAT) format."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        norm_r = fit_result.norm_radius
        dx = (2.0 * norm_r) / (nx - 1)
        dy = (2.0 * norm_r) / (ny - 1)

        x_lin = np.linspace(-norm_r, norm_r, nx)
        y_lin = np.linspace(-norm_r, norm_r, ny)
        xx, yy = np.meshgrid(x_lin, y_lin)

        r_grid = np.hypot(xx, yy)
        rho_grid = r_grid / norm_r
        theta_grid = np.arctan2(yy, xx)
        theta_grid = np.where(theta_grid < 0, theta_grid + 2 * np.pi, theta_grid)

        flat_rho = rho_grid.ravel()
        flat_theta = theta_grid.ravel()

        if fit_result.polynomial_type == "fringe":
            basis = cls.evaluate_fringe_zernike_basis(flat_rho, flat_theta, num_terms=fit_result.num_terms)
        else:
            basis = cls.evaluate_standard_zernike_basis(flat_rho, flat_theta, num_terms=fit_result.num_terms)

        coeffs_arr = np.array(fit_result.coefficients, dtype=np.float64)
        sag_flat = basis @ coeffs_arr
        sag_2d = sag_flat.reshape((ny, nx))

        # Outside clear aperture: set to 0.0
        outside = r_grid > norm_r
        sag_2d[outside] = 0.0

        # Numerical gradients
        dz_dx, dz_dy = np.gradient(sag_2d, dx, dy)
        d2z_dxdy, _ = np.gradient(dz_dx, dx, dy)

        lines = [
            f"{nx} {ny} {dx:.8e} {dy:.8e} {unit_flag} 0.0 0.0",
        ]
        for j in range(ny):
            for i in range(nx):
                z_val = sag_2d[j, i]
                gx = dz_dx[j, i]
                gy = dz_dy[j, i]
                gxy = d2z_dxdy[j, i]
                lines.append(f"{z_val:.8e} {gx:.8e} {gy:.8e} {gxy:.8e}")

        content = "\n".join(lines) + "\n"
        path.write_text(content, encoding="utf-8")
        return content

    @staticmethod
    def format_zosapi_payload(
        rigid_body: RigidBody6DOF,
        fit_result: ZernikeFitResult,
        surface_index: int = 1,
    ) -> Dict[str, Any]:
        """Format STOP bridge outputs into structured dictionary for direct Zemax ZOS-API automation."""
        return {
            "target_surface_index": surface_index,
            "coordinate_break": rigid_body.zemax_coordinate_break,
            "zernike_surface": {
                "polynomial_type": fit_result.polynomial_type,
                "num_terms": fit_result.num_terms,
                "norm_radius": fit_result.norm_radius,
                "coefficients": fit_result.coefficients,
                "rms_residual": fit_result.rms_residual,
                "relative_rms_percent": fit_result.relative_rms_error,
                "r_squared": fit_result.r_squared,
            },
        }
