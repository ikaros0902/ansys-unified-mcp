# Strictly ASCII English Comments
"""ANSYS Sound and Computational Acoustics golden benchmark verification suite.

Validates acoustics and psychoacoustics:
1. 1 kHz 40 dB pure tone ISO 532-1 Zwicker loudness error <= 1.0% (theory 1.0000 sone, 40 phon).
2. Free-field monopole spherical acoustic wave decay between 1.0 m and 2.0 m <= 0.1 dB (theory 6.02 dB).
3. 1 kHz A-weighting gain accuracy per IEC 61672-1:2013 <= 0.05 dB (gain is 0.0 dB at 1 kHz).
4. Solver execution timing SLA <= 6.0 seconds.
5. FastMCP acoustics tool suite execution and flat envelope formatting.

All comments and docstrings in this file strictly use ASCII English.
"""

from __future__ import annotations

import logging
import math
import time
from typing import Any, Dict

import numpy as np
import pytest

from ansys_unified_mcp.benchmarks.sound_acoustics_engine import (
    C_0_AIR,
    DIN45692SharpnessEngine,
    MonopoleAcousticsEngine,
    P_REF_AIR,
    RHO_0_AIR,
    SoundPressureLevelEngine,
    ZwickerLoudnessEngine,
    AcousticsSoundConfig,
    AcousticsSoundEngine,
    AcousticsSoundResult,
)
from ansys_unified_mcp.tools.sound_tools import (
    sound_calculate_sound_pressure_level,
    sound_calculate_zwicker_loudness,
    sound_calculate_sharpness,
)

logger = logging.getLogger(__name__)


class TestPOCAcousticsSoundBenchmark:
    """Computational acoustics and ANSYS Sound psychoacoustics golden test suite."""

    def test_1_zwicker_loudness_1khz_40db(self) -> None:
        """Test 1: Verify 1 kHz 40 dB pure tone Zwicker loudness error <= 1.0% (theory 1.0000 sone)."""
        # 1. Direct parametric pure tone analytical computation
        res_pure = ZwickerLoudnessEngine.compute_pure_tone_loudness(
            frequency=1000.0,
            spl_db=40.0,
            field_type="free",
        )

        loudness_theory = 1.0000  # 1.000 sone
        phon_theory = 40.0000  # 40 phon

        rel_err_pure_pct = abs(res_pure.loudness_sone - loudness_theory) / loudness_theory * 100.0
        assert rel_err_pure_pct <= 1.0, (
            f"Zwicker pure tone loudness error {rel_err_pure_pct:.4f}% exceeds 1.0% limit (val: {res_pure.loudness_sone} sone)"
        )
        assert math.isclose(res_pure.loudness_sone, loudness_theory, abs_tol=1e-3)
        assert math.isclose(res_pure.loudness_level_phon, phon_theory, abs_tol=1e-3)

        # 2. Synthetic 1 kHz sine wave time-domain signal (40 dB SPL)
        fs = 48000.0
        duration = 0.5
        num_samples = int(fs * duration)
        t = np.linspace(0.0, duration, num_samples, endpoint=False)

        # p_rms = p_ref * 10^(40/20) = 2.0e-5 * 100 = 0.002 Pa
        # p(t) = sqrt(2) * p_rms * sin(2 * pi * 1000 * t)
        p_rms_target = P_REF_AIR * (10.0 ** (40.0 / 20.0))
        amplitude = math.sqrt(2.0) * p_rms_target
        signal_sine = amplitude * np.sin(2.0 * np.pi * 1000.0 * t)

        res_signal = ZwickerLoudnessEngine.compute_signal_loudness(
            signal_data=signal_sine,
            fs=fs,
            field_type="free",
        )

        rel_err_sig_pct = abs(res_signal.loudness_sone - loudness_theory) / loudness_theory * 100.0
        assert rel_err_sig_pct <= 1.0, (
            f"Time domain signal Zwicker error {rel_err_sig_pct:.4f}% exceeds 1.0% limit (val: {res_signal.loudness_sone} sone)"
        )
        assert math.isclose(res_signal.loudness_sone, loudness_theory, abs_tol=1e-3)

    def test_2_monopole_free_field_attenuation(self) -> None:
        """Test 2: Verify free-field monopole attenuation error <= 0.1 dB between 1.0 m and 2.0 m (theory 6.02 dB)."""
        r1 = 1.0
        r2 = 2.0
        freq = 1000.0
        q_source = 1.0e-4

        expected_decay_db = 20.0 * math.log10(r2 / r1)

        analysis = MonopoleAcousticsEngine.analyze_monopole(
            r1=r1,
            r2=r2,
            frequency=freq,
            q_source=q_source,
            rho0=RHO_0_AIR,
            c0=C_0_AIR,
            p_ref=P_REF_AIR,
        )

        actual_decay_db = analysis["decay_actual_db"]
        decay_error_db = abs(actual_decay_db - expected_decay_db)

        assert decay_error_db <= 0.1, (
            f"Monopole spherical decay error {decay_error_db:.6f} dB exceeds 0.1 dB limit "
            f"(sim: {actual_decay_db:.4f} dB, theory: {expected_decay_db:.4f} dB)"
        )
        assert math.isclose(actual_decay_db, 6.0206, abs_tol=0.01)

        pressure_ratio = analysis["pressure_r2"] / analysis["pressure_r1"]
        assert math.isclose(pressure_ratio, 0.5, rel_tol=1e-9)

    def test_3_a_weighting_filter_gain_1khz(self) -> None:
        """Test 3: Verify 1 kHz pure tone A-weighting gain <= 0.05 dB deviation (gain is 0.0 dB at 1 kHz)."""
        fs = 48000.0
        duration = 1.0
        num_samples = int(fs * duration)
        t = np.linspace(0.0, duration, num_samples, endpoint=False)

        raw_signal = np.sin(2.0 * np.pi * 1000.0 * t)

        filtered_a = SoundPressureLevelEngine.apply_weighting(
            signal_data=raw_signal,
            weighting="A",
            fs=fs,
        )

        rms_in = SoundPressureLevelEngine.compute_rms(raw_signal)
        rms_out_a = SoundPressureLevelEngine.compute_rms(filtered_a)

        gain_db_a = 20.0 * math.log10(rms_out_a / rms_in)
        gain_error_a = abs(gain_db_a - 0.0)

        assert gain_error_a <= 0.05, (
            f"1 kHz A-weighting gain error {gain_error_a:.6f} dB exceeds 0.05 dB limit (gain: {gain_db_a:.6f} dB)"
        )

        filtered_c = SoundPressureLevelEngine.apply_weighting(
            signal_data=raw_signal,
            weighting="C",
            fs=fs,
        )
        rms_out_c = SoundPressureLevelEngine.compute_rms(filtered_c)
        gain_db_c = 20.0 * math.log10(rms_out_c / rms_in)
        gain_error_c = abs(gain_db_c - 0.0)

        assert gain_error_c <= 0.05, (
            f"1 kHz C-weighting gain error {gain_error_c:.6f} dB exceeds 0.05 dB limit (gain: {gain_db_c:.6f} dB)"
        )

    def test_4_execution_time_sla(self) -> None:
        """Test 4: Solver execution time verification (SLA <= 6.0 s)."""
        fs = 48000.0
        duration = 2.0
        num_samples = int(fs * duration)
        t = np.linspace(0.0, duration, num_samples, endpoint=False)

        composite_signal = (
            0.01 * np.sin(2.0 * np.pi * 100.0 * t)
            + 0.02 * np.sin(2.0 * np.pi * 1000.0 * t)
            + 0.005 * np.sin(2.0 * np.pi * 4000.0 * t)
        )

        start_time = time.perf_counter()

        spl_res = SoundPressureLevelEngine.analyze_signal(composite_signal, fs=fs)
        loudness_res = ZwickerLoudnessEngine.compute_signal_loudness(composite_signal, fs=fs)
        sharpness_res = DIN45692SharpnessEngine.compute_sharpness(
            specific_loudness=loudness_res.specific_loudness,
            bark_bands=loudness_res.bark_bands,
            total_loudness=loudness_res.loudness_sone,
        )
        monopole_res = MonopoleAcousticsEngine.analyze_monopole(
            r1=1.0,
            r2=2.0,
            frequency=1000.0,
            q_source=1.0e-4,
        )

        elapsed = time.perf_counter() - start_time

        assert spl_res.p_rms > 0.0
        assert loudness_res.loudness_sone > 0.0
        assert sharpness_res.sharpness_acum > 0.0
        assert monopole_res["decay_actual_db"] > 6.0

        assert elapsed <= 6.0, f"Execution time {elapsed:.4f}s exceeds 6.0s SLA"

    def test_5_mcp_tools_sound_calculation(self) -> None:
        """Test 5: FastMCP acoustics tools execution and envelope verification."""
        fs = 48000.0
        duration = 0.25
        t = np.linspace(0.0, duration, int(fs * duration), endpoint=False)
        p_rms_target = P_REF_AIR * (10.0 ** (40.0 / 20.0))
        signal_list = (math.sqrt(2.0) * p_rms_target * np.sin(2.0 * np.pi * 1000.0 * t)).tolist()

        spl_env = sound_calculate_sound_pressure_level(
            signal=signal_list,
            sampling_rate=fs,
        )
        assert spl_env.get("ok") is True, f"SPL tool failed: {spl_env}"
        assert math.isclose(spl_env["spl_db"], 40.0, abs_tol=0.2)
        assert math.isclose(spl_env["spl_dba"], 40.0, abs_tol=0.2)

        loud_env_pure = sound_calculate_zwicker_loudness(
            frequency=1000.0,
            spl_db=40.0,
            field_type="free",
        )
        assert loud_env_pure.get("ok") is True, f"Zwicker pure tone tool failed: {loud_env_pure}"
        assert math.isclose(loud_env_pure["loudness_sone"], 1.0000, abs_tol=1e-3)
        assert math.isclose(loud_env_pure["loudness_level_phon"], 40.0, abs_tol=1e-3)

        loud_env_sig = sound_calculate_zwicker_loudness(
            signal=signal_list,
            sampling_rate=fs,
            field_type="free",
        )
        assert loud_env_sig.get("ok") is True, f"Zwicker signal tool failed: {loud_env_sig}"
        assert math.isclose(loud_env_sig["loudness_sone"], 1.0000, abs_tol=1e-2)

        sharp_env = sound_calculate_sharpness(
            frequency=1000.0,
            spl_db=40.0,
            field_type="free",
        )
        assert sharp_env.get("ok") is True, f"Sharpness tool failed: {sharp_env}"
        assert sharp_env["sharpness_acum"] > 0.0

    def test_analytical_zwicker_and_monopole_baseline(self) -> None:
        """Verify ISO 532-1 Zwicker baseline and monopole 6dB decay analytical solutions."""
        cfg = AcousticsSoundConfig(
            frequency_hz=1000.0,
            spl_db_at_r1=40.0,
            r1_distance_m=1.0,
            r2_distance_m=2.0,
        )
        theory = AcousticsSoundEngine.compute_analytical_solution(cfg)

        assert math.isclose(theory["loudness_sone_theory"], 1.0, abs_tol=1e-9)
        assert math.isclose(theory["phon_theory"], 40.0, abs_tol=1e-9)

        expected_decay = 20.0 * math.log10(2.0)
        assert math.isclose(theory["decay_6db_theory"], expected_decay, rel_tol=1e-9)
        assert abs(theory["decay_6db_theory"] - 6.0206) < 1e-4

        expected_spl_r2 = 40.0 - expected_decay
        assert math.isclose(theory["spl_r2_theory"], expected_spl_r2, rel_tol=1e-9)

    def test_numerical_helmholtz_and_zwicker_accuracy_and_timing(self) -> None:
        """Verify numerical Helmholtz and Zwicker accuracy and timing SLA."""
        cfg = AcousticsSoundConfig(
            frequency_hz=1000.0,
            spl_db_at_r1=40.0,
            r1_distance_m=1.0,
            r2_distance_m=2.0,
            radial_grid_points=500,
        )

        t_start = time.perf_counter()
        res: AcousticsSoundResult = AcousticsSoundEngine.solve(cfg)
        elapsed = time.perf_counter() - t_start

        assert res.loudness_rel_error_pct <= 0.1
        assert math.isclose(res.loudness_sone_sim, 1.0000, abs_tol=1e-3)
        assert res.decay_rel_error_pct <= 0.1
        assert abs(res.decay_6db_sim - 6.0206) < 0.01
        assert res.converged is True
        assert elapsed <= 5.0
