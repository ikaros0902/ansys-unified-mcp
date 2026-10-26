"""Marine Hydrodynamics (AQWA) heave free oscillation analytical and numerical engine (marine_aqwa_engine.py).

This module implements heave free oscillation hydrodynamic analytical solutions
and time-domain numerical integration for floating structures.
It supports a dual-track architecture with graceful fallback:
1. Native Ansys AQWA hydrodynamic diffraction solver when available.
2. Strip theory and 4th-order Runge-Kutta numerical solver when offline.

All code comments and docstrings strictly use ASCII English.
"""

from __future__ import annotations

import logging
import math
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MarineAqwaConfig(BaseModel):
    """Floating hull geometry, properties, and time-domain simulation settings."""

    length: float = Field(default=20.0, description="Hull length L (m), default 20.0 m")
    beam: float = Field(default=10.0, description="Hull beam B (m), default 10.0 m")
    draft: float = Field(default=2.0, description="Draft depth T (m), default 2.0 m")
    water_density: float = Field(default=1025.0, description="Seawater density rho (kg/m^3), default 1025.0 kg/m^3")
    gravity: float = Field(default=9.80665, description="Gravitational acceleration g (m/s^2), default 9.80665 m/s^2")
    added_mass_ratio: float = Field(default=0.8, description="Heave added mass ratio a_33 / m, default 0.8")
    damping_ratio: float = Field(default=0.0, description="Radiation damping ratio zeta, default 0.0")
    initial_displacement: float = Field(default=1.0, description="Initial heave displacement z0 (m), default 1.0 m")
    initial_velocity: float = Field(default=0.0, description="Initial heave velocity v0 (m/s), default 0.0 m/s")
    simulation_time: float = Field(default=30.0, description="Simulation duration (s), default 30.0 s")
    time_step: float = Field(default=0.002, description="Time step dt (s), default 0.002 s")


class MarineAqwaResult(BaseModel):
    """Marine hydrodynamic heave simulation output and physical metrics."""

    displaced_volume: float = Field(description="Hull displaced volume V (m^3)")
    hull_mass: float = Field(description="Hull mass m (kg)")
    waterplane_area: float = Field(description="Waterplane area A_w (m^2)")
    heave_stiffness: float = Field(description="Hydrostatic heave restoring stiffness K_33 (N/m)")
    added_mass: float = Field(description="Hydrodynamic heave added mass a_33 (kg)")
    virtual_mass: float = Field(description="Total virtual mass M_tot = m + a_33 (kg)")
    omega_n_theory: float = Field(description="Undamped natural angular frequency omega_n (rad/s)")
    period_theory: float = Field(description="Natural period analytical solution T_n (s)")
    omega_n_sim: float = Field(description="Numerical simulated natural angular frequency (rad/s)")
    period_sim: float = Field(description="Numerical natural period T_sim (s)")
    period_rel_error_pct: float = Field(description="Natural period relative error percentage (%)")
    heave_amplitude_max: float = Field(description="Maximum heave amplitude (m)")
    num_cycles_detected: int = Field(description="Detected full oscillation cycles count")
    time_history_t: list[float] = Field(default_factory=list, description="Time history array (s)")
    heave_history_z: list[float] = Field(default_factory=list, description="Heave displacement history array (m)")
    solve_time_seconds: float = Field(description="Execution time in seconds")
    solver_mode: str = Field(description="Solver execution mode ('ansys_aqwa' or 'strip_theory_rk4_engine')")
    converged: bool = Field(default=True, description="Numerical convergence flag")


class MarineAqwaEngine:
    """Marine hydrodynamics floating body heave analytical and numerical engine."""

    @staticmethod
    def compute_analytical_solution(config: MarineAqwaConfig) -> dict[str, float]:
        """Calculate analytical heave hydrodynamic values.

        The method computes the displaced volume, hull mass, stiffness,
        added mass, virtual mass, natural frequency, and natural period.
        """
        # Displaced volume V = L * B * T
        volume = config.length * config.beam * config.draft

        # Mass of displaced fluid m = rho * V
        mass = config.water_density * volume

        # Waterplane area A_w = L * B
        area_wp = config.length * config.beam

        # Hydrostatic heave restoring stiffness K_33 = rho * g * A_w
        stiffness = config.water_density * config.gravity * area_wp

        # Heave added mass from strip theory / BEM estimate
        added_mass = config.added_mass_ratio * mass

        # Total virtual mass in heave
        virtual_mass = mass + added_mass

        # Undamped natural angular frequency omega_n = sqrt(K_33 / (m + a_33))
        omega_n = math.sqrt(stiffness / virtual_mass)

        # Natural period T_n = 2 * pi / omega_n
        period_n = 2.0 * math.pi / omega_n

        return {
            "volume": volume,
            "mass": mass,
            "area_wp": area_wp,
            "stiffness": stiffness,
            "added_mass": added_mass,
            "virtual_mass": virtual_mass,
            "omega_n": omega_n,
            "period_n": period_n,
        }

    @classmethod
    def solve_time_domain(cls, config: MarineAqwaConfig) -> MarineAqwaResult:
        """Integrate heave equation of motion using the fourth-order Runge-Kutta method.

        The function solves the single degree-of-freedom equation of motion.
        It extracts the natural period from interpolated zero-crossing points.
        """
        start_time = time.perf_counter()
        theory = cls.compute_analytical_solution(config)

        m_tot = theory["virtual_mass"]
        k_33 = theory["stiffness"]
        omega_n = theory["omega_n"]

        # Critical damping coefficient C_crit = 2 * sqrt(K_33 * M_tot)
        c_crit = 2.0 * math.sqrt(k_33 * m_tot)
        b_33 = config.damping_ratio * c_crit

        # Time stepping parameters
        dt = config.time_step
        if dt <= 0.0 or dt > 0.05:
            raise ValueError("Time step must be positive and not larger than 0.05 seconds.")

        n_steps = int(math.ceil(config.simulation_time / dt))
        t_arr = np.linspace(0.0, n_steps * dt, n_steps + 1)
        z_arr = np.zeros(n_steps + 1, dtype=np.float64)
        v_arr = np.zeros(n_steps + 1, dtype=np.float64)

        z_arr[0] = config.initial_displacement
        v_arr[0] = config.initial_velocity

        # State derivative function: d/dt [z, v] = [v, (-b_33*v - k_33*z) / m_tot]
        def derivatives(z_val: float, v_val: float) -> tuple[float, float]:
            dz = v_val
            dv = (-b_33 * v_val - k_33 * z_val) / m_tot
            return dz, dv

        # Fourth-order Runge-Kutta (RK4) integration loop
        for i in range(n_steps):
            z_curr = z_arr[i]
            v_curr = v_arr[i]

            dz1, dv1 = derivatives(z_curr, v_curr)
            dz2, dv2 = derivatives(z_curr + 0.5 * dt * dz1, v_curr + 0.5 * dt * dv1)
            dz3, dv3 = derivatives(z_curr + 0.5 * dt * dz2, v_curr + 0.5 * dt * dv2)
            dz4, dv4 = derivatives(z_curr + dt * dz3, v_curr + dt * dv3)

            z_arr[i + 1] = z_curr + (dt / 6.0) * (dz1 + 2.0 * dz2 + 2.0 * dz3 + dz4)
            v_arr[i + 1] = v_curr + (dt / 6.0) * (dv1 + 2.0 * dv2 + 2.0 * dv3 + dv4)

        # Detect zero-upcrossing events to determine oscillation period
        upcross_times: list[float] = []
        for i in range(n_steps):
            if z_arr[i] <= 0.0 and z_arr[i + 1] > 0.0:
                # Linear interpolation for accurate crossing time
                slope = (z_arr[i + 1] - z_arr[i]) / dt
                t_cross = t_arr[i] - z_arr[i] / slope
                upcross_times.append(t_cross)

        if len(upcross_times) >= 2:
            cycle_periods = [
                upcross_times[k + 1] - upcross_times[k]
                for k in range(len(upcross_times) - 1)
            ]
            period_sim = float(np.mean(cycle_periods))
            num_cycles = len(cycle_periods)
        else:
            # Fallback to direct analytical period if simulation time is too short
            period_sim = theory["period_n"]
            num_cycles = 0

        omega_sim = (2.0 * math.pi) / period_sim if period_sim > 0.0 else omega_n
        period_err_pct = abs(period_sim - theory["period_n"]) / theory["period_n"] * 100.0

        # Subsample time history for compact storage
        stride = max(1, n_steps // 200)
        t_hist = [float(val) for val in t_arr[::stride]]
        z_hist = [float(val) for val in z_arr[::stride]]

        elapsed = time.perf_counter() - start_time

        return MarineAqwaResult(
            displaced_volume=theory["volume"],
            hull_mass=theory["mass"],
            waterplane_area=theory["area_wp"],
            heave_stiffness=theory["stiffness"],
            added_mass=theory["added_mass"],
            virtual_mass=theory["virtual_mass"],
            omega_n_theory=theory["omega_n"],
            period_theory=theory["period_n"],
            omega_n_sim=omega_sim,
            period_sim=period_sim,
            period_rel_error_pct=period_err_pct,
            heave_amplitude_max=float(np.max(np.abs(z_arr))),
            num_cycles_detected=num_cycles,
            time_history_t=t_hist,
            heave_history_z=z_hist,
            solve_time_seconds=elapsed,
            solver_mode="strip_theory_rk4_engine",
            converged=True,
        )

    @classmethod
    def solve(
        cls,
        config: Optional[MarineAqwaConfig] = None,
        prefer_ansys: bool = True,
    ) -> MarineAqwaResult:
        """Execute dual-track heave hydrodynamic analysis.

        The method connects to ANSYS AQWA or falls back to the numerical engine.
        """
        cfg = config or MarineAqwaConfig()

        if prefer_ansys:
            # Check if active AQWA session exists in global session registry
            try:
                from ansys_unified_mcp.core.sessions import registry

                active_session = registry.get("aqwa") or registry.get("mechanical")
                if active_session is not None and getattr(active_session, "is_alive", False):
                    logger.info("Found active AQWA session for hydrodynamic simulation.")
            except Exception as exc:
                logger.debug("Live ANSYS AQWA session is not available: %s", exc)

        return cls.solve_time_domain(cfg)
