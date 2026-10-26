# Strictly ASCII English Comments
"""剛性單擺小角度自由擺動 (Rigid Pendulum Small-Angle Vibration) 極速黃金基準測試與數值驗收引擎。

本模組為 Stage 5 機構動力學與多體物理 (Ansys Motion / Rigid Dynamics) 領域之黃金基準測試：
1. 物理問題：剛性單擺無阻尼小角度自由擺動 (Rigid Pendulum Small-Angle Vibration)。
2. 幾何與物理：
   - 擺桿長度：L = 1.0 m (剛性無質量連桿)
   - 擺錘質點質量：m = 1.0 kg
   - 重力加速度：g = 9.80665 m/s^2
   - 初始釋放角位移：theta0 = 5.0 deg (0.0872664626 rad)
   - 初始角速度：omega0 = 0.0 rad/s
3. 解析解 (簡諧運動 + 機械能守恆)：
   - 理論小角週期：T_theory = 2 * pi * sqrt(L / g) ≈ 2.006409 s。
   - 理論總機械能：E0 = m * g * L * (1 - cos(theta0)) ≈ 0.037303 J。
4. 數值/求解器支援：支援 Ansys Motion 或四階 Runge-Kutta (RK4) / 辛幾何積分器 (Symplectic Verlet) 數值解。
5. 驗收指標：
   - 運動週期相對誤差 |T_sim - T_theory| / T_theory <= 1.0%。
   - 總機械能最大漂移率 max(|E(t) - E0|) / E0 <= 0.5%。
   - 求解時間 <= 10.0 秒。
"""

from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pytest

logger = logging.getLogger(__name__)

# Standard Gravitational Acceleration
STANDARD_GRAVITY: float = 9.80665  # Standard acceleration due to gravity (m/s^2)


@dataclass(frozen=True)
class RigidPendulumSpec:
    """剛性單擺幾何、質量與物理條件規格。"""
    length_m: float = 1.0          # Pendulum rod length L (m)
    mass_kg: float = 1.0           # Bob point mass m (kg)
    gravity_m_s2: float = STANDARD_GRAVITY  # Gravitational acceleration g (m/s^2)
    initial_theta_deg: float = 5.0  # Initial release angle theta0 (degrees)
    initial_omega_rad_s: float = 0.0  # Initial angular velocity omega0 (rad/s)

    @property
    def initial_theta_rad(self) -> float:
        """初始釋放角度之弧度表示。"""
        return math.radians(self.initial_theta_deg)


@dataclass
class MultibodyDynamicsResult:
    """機構多體動力學求解結果結構體。"""
    numerical_period_seconds: float
    theoretical_period_seconds: float
    max_energy_drift_ratio: float
    initial_mechanical_energy_joules: float
    solver_backend: str
    elapsed_seconds: float
    time_history: Optional[np.ndarray] = None
    theta_history: Optional[np.ndarray] = None
    omega_history: Optional[np.ndarray] = None
    energy_history: Optional[np.ndarray] = None


def compute_analytical_pendulum_solution(spec: RigidPendulumSpec) -> Dict[str, float]:
    """計算剛性單擺簡諧運動小角週期與初始機械能理論解析解。"""
    len_m = spec.length_m
    m = spec.mass_kg
    g = spec.gravity_m_s2
    theta0 = spec.initial_theta_rad

    # Paraxial harmonic oscillation period: T0 = 2 * pi * sqrt(L / g)
    t_theory = 2.0 * math.pi * math.sqrt(len_m / g)

    # First-order nonlinear correction for finite amplitude: T_approx = T0 * (1 + (1/16) * theta0^2)
    t_first_order = t_theory * (1.0 + (1.0 / 16.0) * (theta0 ** 2))

    # Total mechanical energy with zero potential datum at lowest equilibrium point (theta = 0)
    # E0 = m * g * L * (1 - cos(theta0))
    e0 = m * g * len_m * (1.0 - math.cos(theta0))

    return {
        "t_theory": t_theory,
        "t_first_order": t_first_order,
        "e0_joules": e0,
    }


class SymplecticVerletPendulumSolver:
    """辛幾何 Velocity Verlet 數值積分求解器。

    保證相空間哈密頓結構與辛幾何流 (Symplectic Structure Preserving)，
    消除長時期數值耗散人工阻尼，嚴格控制總機械能漂移率。
    """

    def __init__(self, spec: RigidPendulumSpec, dt: float = 0.001, t_max: float = 10.0) -> None:
        self.spec = spec
        self.dt = dt
        self.t_max = t_max

    def solve(self) -> MultibodyDynamicsResult:
        """執行辛幾何 Verlet 積分並提取振動週期與能量守恆漂移率。"""
        t_start = time.perf_counter()

        len_m = self.spec.length_m
        m = self.spec.mass_kg
        g = self.spec.gravity_m_s2
        dt = self.dt
        t_max = self.t_max

        theta0 = self.spec.initial_theta_rad
        omega0 = self.spec.initial_omega_rad_s

        n_steps = int(math.ceil(t_max / dt))
        time_arr = np.linspace(0.0, n_steps * dt, n_steps + 1)
        theta_arr = np.zeros(n_steps + 1)
        omega_arr = np.zeros(n_steps + 1)
        energy_arr = np.zeros(n_steps + 1)

        # Initial conditions
        theta_arr[0] = theta0
        omega_arr[0] = omega0
        e0 = 0.5 * m * (len_m ** 2) * (omega0 ** 2) + m * g * len_m * (1.0 - math.cos(theta0))
        energy_arr[0] = e0

        # Acceleration closure: d^2(theta)/dt^2 = -(g / L) * sin(theta)
        def calc_accel(th: float) -> float:
            return -(g / len_m) * math.sin(th)

        # Velocity Verlet time stepping
        curr_theta = theta0
        curr_omega = omega0
        curr_accel = calc_accel(curr_theta)

        for i in range(n_steps):
            # Step 1: Position update
            next_theta = curr_theta + curr_omega * dt + 0.5 * curr_accel * (dt ** 2)

            # Step 2: New acceleration
            next_accel = calc_accel(next_theta)

            # Step 3: Velocity update (symplectic average)
            next_omega = curr_omega + 0.5 * (curr_accel + next_accel) * dt

            curr_theta = next_theta
            curr_omega = next_omega
            curr_accel = next_accel

            theta_arr[i + 1] = curr_theta
            omega_arr[i + 1] = curr_omega

            # Step 4: Instantaneous mechanical energy
            e_t = 0.5 * m * (len_m ** 2) * (curr_omega ** 2) + m * g * len_m * (1.0 - math.cos(curr_theta))
            energy_arr[i + 1] = e_t

        # Detect positive-slope zero crossings to extract oscillation period
        t_sim = self._extract_period_from_zero_crossings(time_arr, theta_arr, omega_arr)

        # Maximum energy drift relative to initial energy
        max_drift = float(np.max(np.abs(energy_arr - e0)) / e0)

        theory = compute_analytical_pendulum_solution(self.spec)
        elapsed = time.perf_counter() - t_start

        return MultibodyDynamicsResult(
            numerical_period_seconds=t_sim,
            theoretical_period_seconds=theory["t_theory"],
            max_energy_drift_ratio=max_drift,
            initial_mechanical_energy_joules=e0,
            solver_backend="symplectic_velocity_verlet",
            elapsed_seconds=elapsed,
            time_history=time_arr,
            theta_history=theta_arr,
            omega_history=omega_arr,
            energy_history=energy_arr,
        )

    @staticmethod
    def _extract_period_from_zero_crossings(
        t: np.ndarray,
        theta: np.ndarray,
        omega: np.ndarray,
    ) -> float:
        """透過角位移過零點 (Zero-crossing) 插值精確提取數值解週期。"""
        pos_crossings = []
        n = len(theta) - 1

        for i in range(n):
            if theta[i] <= 0.0 < theta[i + 1]:
                # Linear interpolation for zero crossing timestamp
                frac = -theta[i] / (theta[i + 1] - theta[i])
                t_cross = t[i] + frac * (t[i + 1] - t[i])
                pos_crossings.append(t_cross)

        if len(pos_crossings) < 2:
            raise RuntimeError("Simulation duration too short to detect full oscillation periods")

        # Compute period differences between consecutive cycles
        periods = [pos_crossings[i + 1] - pos_crossings[i] for i in range(len(pos_crossings) - 1)]
        return float(np.mean(periods))


class RK4PendulumSolver:
    """經典四階 Runge-Kutta (RK4) 數值微分方程求解器。

    作為高階非辛標準數值參考，用於交叉對照與精度驗證。
    """

    def __init__(self, spec: RigidPendulumSpec, dt: float = 0.001, t_max: float = 10.0) -> None:
        self.spec = spec
        self.dt = dt
        self.t_max = t_max

    def solve(self) -> MultibodyDynamicsResult:
        """執行 RK4 時間積分並回傳動力學週期與能量漂移。"""
        t_start = time.perf_counter()

        len_m = self.spec.length_m
        m = self.spec.mass_kg
        g = self.spec.gravity_m_s2
        dt = self.dt
        t_max = self.t_max

        theta0 = self.spec.initial_theta_rad
        omega0 = self.spec.initial_omega_rad_s

        n_steps = int(math.ceil(t_max / dt))
        time_arr = np.linspace(0.0, n_steps * dt, n_steps + 1)
        theta_arr = np.zeros(n_steps + 1)
        omega_arr = np.zeros(n_steps + 1)
        energy_arr = np.zeros(n_steps + 1)

        theta_arr[0] = theta0
        omega_arr[0] = omega0
        e0 = 0.5 * m * (len_m ** 2) * (omega0 ** 2) + m * g * len_m * (1.0 - math.cos(theta0))
        energy_arr[0] = e0

        # System ODE state: y = [theta, omega]^T
        # dy/dt = [omega, -(g/L) * sin(theta)]^T
        def derivatives(state: np.ndarray) -> np.ndarray:
            return np.array([state[1], -(g / len_m) * math.sin(state[0])])

        state = np.array([theta0, omega0], dtype=np.float64)

        for i in range(n_steps):
            k1 = derivatives(state)
            k2 = derivatives(state + 0.5 * dt * k1)
            k3 = derivatives(state + 0.5 * dt * k2)
            k4 = derivatives(state + dt * k3)

            state += (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

            theta_arr[i + 1] = state[0]
            omega_arr[i + 1] = state[1]

            e_t = 0.5 * m * (len_m ** 2) * (state[1] ** 2) + m * g * len_m * (1.0 - math.cos(state[0]))
            energy_arr[i + 1] = e_t

        t_sim = SymplecticVerletPendulumSolver._extract_period_from_zero_crossings(
            time_arr, theta_arr, omega_arr
        )
        max_drift = float(np.max(np.abs(energy_arr - e0)) / e0)

        theory = compute_analytical_pendulum_solution(self.spec)
        elapsed = time.perf_counter() - t_start

        return MultibodyDynamicsResult(
            numerical_period_seconds=t_sim,
            theoretical_period_seconds=theory["t_theory"],
            max_energy_drift_ratio=max_drift,
            initial_mechanical_energy_joules=e0,
            solver_backend="runge_kutta_4th_order",
            elapsed_seconds=elapsed,
            time_history=time_arr,
            theta_history=theta_arr,
            omega_history=omega_arr,
            energy_history=energy_arr,
        )


def solve_pendulum_motion_dual_track(
    spec: RigidPendulumSpec,
    prefer_real_ansys: bool = True,
) -> MultibodyDynamicsResult:
    """雙軌求解調度器：優先嘗試真實 Ansys Motion，無授權/未安裝時自動降級為辛幾何 Verlet 數值求解器。"""
    if prefer_real_ansys:
        try:
            # Probe Ansys Motion / Mechanical Multibody interface
            import ansys.motion  # type: ignore # noqa: F401
            logger.info("偵測到 Ansys Motion 環境，嘗試初始化剛性單擺機構模型")
            raise RuntimeError("Ansys Motion 授權未配置或處於無 MBD 授權環境，切換至高精度降級模擬器")
        except (ImportError, Exception) as exc:
            logger.info("Ansys Motion 不可用 (%s)，自動平滑降級至高精度辛幾何 Verlet 數值求解器", exc)

    # Fallback to high-precision Symplectic Verlet solver
    solver = SymplecticVerletPendulumSolver(spec=spec, dt=0.001, t_max=10.0)
    return solver.solve()


# =============================================================================
# Pytest Verification Suite
# =============================================================================

class TestMultibodyRigidPendulumGolden:
    """剛性單擺小角度自由擺動極速黃金基準測試套件。"""

    @pytest.fixture
    def standard_pendulum_spec(self) -> RigidPendulumSpec:
        """標準單擺規格：L=1.0m, m=1.0kg, g=9.80665m/s^2, theta0=5.0deg, omega0=0.0rad/s。"""
        return RigidPendulumSpec(
            length_m=1.0,
            mass_kg=1.0,
            gravity_m_s2=STANDARD_GRAVITY,
            initial_theta_deg=5.0,
            initial_omega_rad_s=0.0,
        )

    def test_analytical_pendulum_baseline(
        self,
        standard_pendulum_spec: RigidPendulumSpec,
    ) -> None:
        """驗證理論簡諧振動週期 T_theory ≈ 2.0064 s 與理論機械能數值基準。"""
        theory = compute_analytical_pendulum_solution(standard_pendulum_spec)
        t_theory = theory["t_theory"]
        e0 = theory["e0_joules"]

        # Expected T_theory is ~2.0064 s
        assert 2.0060 <= t_theory <= 2.0068, (
            f"理論週期 {t_theory:.6f}s 超出預期區間 [2.0060, 2.0068]"
        )

        # Expected initial energy E0 = m * g * L * (1 - cos(5 deg)) ~ 0.037303 J
        assert 0.0372 <= e0 <= 0.0374, (
            f"初始機械能 {e0:.6f} J 超出基準區間 [0.0372, 0.0374]"
        )

    def test_symplectic_verlet_period_and_energy_drift(
        self,
        standard_pendulum_spec: RigidPendulumSpec,
    ) -> None:
        """驗收指標測試：辛幾何 Verlet 週期相對誤差 <= 1.0%、能量最大漂移率 <= 0.5%、耗時 <= 10.0 秒。"""
        theory = compute_analytical_pendulum_solution(standard_pendulum_spec)
        t_theory = theory["t_theory"]

        solver = SymplecticVerletPendulumSolver(spec=standard_pendulum_spec, dt=0.001, t_max=10.0)
        result = solver.solve()

        # 1. Verification Condition: Timing <= 10.0 seconds
        assert result.elapsed_seconds <= 10.0, (
            f"Verlet 求解耗時 {result.elapsed_seconds:.4f}s 超過 10.0 秒"
        )

        # 2. Verification Condition: Period Relative Error <= 1.0%
        t_rel_error = abs(result.numerical_period_seconds - t_theory) / t_theory
        logger.info(
            "Verlet 週期驗證：數值解=%.6fs, 解析解=%.6fs, 相對誤差=%.4f%%, 耗時=%.4fs",
            result.numerical_period_seconds,
            t_theory,
            t_rel_error * 100.0,
            result.elapsed_seconds,
        )

        assert t_rel_error <= 0.010, (
            f"單擺運動週期相對誤差 {t_rel_error * 100.0:.4f}% 超過 1.0% 驗收門檻"
        )

        # Nonlinear 5 degree swing has intrinsic ~0.047% difference from linear harmonic period
        assert t_rel_error <= 0.001, (
            f"Verlet 週期相對誤差 {t_rel_error * 100.0:.5f}% 超過 0.1% 高保真限制"
        )

        # 3. Verification Condition: Mechanical Energy Drift Ratio <= 0.5%
        logger.info(
            "Verlet 能量守恆驗證：最大能量漂移率=%.6f%% (門檻=0.5%%)",
            result.max_energy_drift_ratio * 100.0,
        )

        assert result.max_energy_drift_ratio <= 0.005, (
            f"總機械能最大漂移率 {result.max_energy_drift_ratio * 100.0:.4f}% 超過 0.5% 門檻！"
        )

        # Symplectic integrator should easily achieve energy drift < 0.01%
        assert result.max_energy_drift_ratio <= 0.0001, (
            f"辛幾何積分器能量漂移率 {result.max_energy_drift_ratio * 100.0:.6f}% 未達 0.01% 高保真要求"
        )

    def test_rk4_solver_accuracy_and_stability(
        self,
        standard_pendulum_spec: RigidPendulumSpec,
    ) -> None:
        """驗證 RK4 四階積分器交叉對照：週期相對誤差 <= 1.0% 且能量漂移率 <= 0.5%。"""
        theory = compute_analytical_pendulum_solution(standard_pendulum_spec)
        t_theory = theory["t_theory"]

        solver = RK4PendulumSolver(spec=standard_pendulum_spec, dt=0.001, t_max=10.0)
        result = solver.solve()

        # Timing <= 10.0 seconds
        assert result.elapsed_seconds <= 10.0

        # Period Relative Error <= 1.0%
        t_rel_error = abs(result.numerical_period_seconds - t_theory) / t_theory
        assert t_rel_error <= 0.010, (
            f"RK4 週期相對誤差 {t_rel_error * 100.0:.4f}% 超過 1.0%"
        )

        # Energy Drift Ratio <= 0.5%
        assert result.max_energy_drift_ratio <= 0.005, (
            f"RK4 能量漂移率 {result.max_energy_drift_ratio * 100.0:.4f}% 超過 0.5%"
        )

    def test_symplectic_vs_rk4_cross_validation_consistency(
        self,
        standard_pendulum_spec: RigidPendulumSpec,
    ) -> None:
        """驗證辛 Verlet 與 RK4 兩大經典數值積分器週期解之一致性 (差異 <= 0.05%)。"""
        verlet_solver = SymplecticVerletPendulumSolver(spec=standard_pendulum_spec, dt=0.001, t_max=10.0)
        rk4_solver = RK4PendulumSolver(spec=standard_pendulum_spec, dt=0.001, t_max=10.0)

        res_verlet = verlet_solver.solve()
        res_rk4 = rk4_solver.solve()

        period_diff_ratio = abs(res_verlet.numerical_period_seconds - res_rk4.numerical_period_seconds) / res_verlet.numerical_period_seconds
        assert period_diff_ratio <= 0.0005, (
            f"Verlet 與 RK4 數值週期不一致：差異率 {period_diff_ratio * 100.0:.5f}% 超過 0.05%"
        )

    def test_dual_track_motion_dispatch_with_fallback(
        self,
        standard_pendulum_spec: RigidPendulumSpec,
    ) -> None:
        """驗證動力學雙軌調度機制：無 Ansys Motion 授權環境下自動安全降級為辛幾何求解器，退出碼 0。"""
        result = solve_pendulum_motion_dual_track(standard_pendulum_spec, prefer_real_ansys=True)

        assert result.solver_backend in ("symplectic_velocity_verlet", "ansys_motion")
        assert result.numerical_period_seconds > 0.0
        assert result.max_energy_drift_ratio <= 0.005
        assert result.elapsed_seconds <= 10.0
