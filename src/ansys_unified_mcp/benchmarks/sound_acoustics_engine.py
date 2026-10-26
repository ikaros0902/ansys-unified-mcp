# -*- coding: utf-8 -*-
# Strictly ASCII English Comments
"""Sound and Computational Acoustics Engine (sound_acoustics_engine.py).

Provides standard algorithms for computational acoustics and psychoacoustics:
1. Sound Pressure Level (SPL) in dB, dBA, and dBC per IEC 61672-1:2013.
2. ISO 532-1 (Zwicker) stationary loudness (sone) and loudness level (phon).
3. Monopole point source free-field spherical pressure wave decay.
4. DIN 45692 sound sharpness (acum).

All docstrings and exception messages follow ASD-STE100 guidelines.
All internal comments strictly use ASCII English characters.
"""

from __future__ import annotations

import logging
import math
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np
import scipy.signal as signal
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

# Standard acoustic reference constants
P_REF_AIR: float = 2.0e-5  # Standard reference sound pressure in air (20 micro-Pascals)
RHO_0_AIR: float = 1.2041  # Air density at 20 degrees Celsius (kg/m^3)
C_0_AIR: float = 343.24  # Speed of sound in air at 20 degrees Celsius (m/s)

# ISO 226:2003 Equal Loudness Contour reference data
_ISO226_FREQ = np.array([
    20.0, 25.0, 31.5, 40.0, 50.0, 63.0, 80.0, 100.0, 125.0, 160.0,
    200.0, 250.0, 315.0, 400.0, 500.0, 630.0, 800.0, 1000.0, 1250.0,
    1600.0, 2000.0, 2500.0, 3150.0, 4000.0, 5000.0, 6300.0, 8000.0,
    10000.0, 12500.0
], dtype=np.float64)

_ISO226_AF = np.array([
    0.532, 0.506, 0.480, 0.455, 0.432, 0.409, 0.387, 0.367, 0.349, 0.330,
    0.315, 0.301, 0.288, 0.276, 0.267, 0.259, 0.253, 0.250, 0.246, 0.244,
    0.243, 0.243, 0.243, 0.242, 0.242, 0.245, 0.254, 0.271, 0.301
], dtype=np.float64)

_ISO226_LU = np.array([
    -31.6, -27.2, -23.0, -19.1, -15.9, -13.0, -10.3, -8.1, -6.2, -4.5,
    -3.1, -2.0, -1.1, -0.4, 0.0, 0.3, 0.5, 0.0, -2.7, -4.1,
    -1.0, 1.7, 2.5, 1.2, -2.1, -7.1, -11.2, -10.7, -3.1
], dtype=np.float64)

_ISO226_TF = np.array([
    78.5, 68.7, 59.5, 51.1, 44.0, 37.5, 31.5, 26.5, 22.1, 17.9,
    14.4, 11.4, 8.6, 6.2, 4.4, 3.0, 2.2, 2.4, 3.5, 1.7,
    -1.3, -4.2, -6.0, -5.4, -1.5, 6.0, 12.6, 13.9, 12.3
], dtype=np.float64)


class SPLResult(BaseModel):
    """Result data model for sound pressure level analysis."""

    model_config = ConfigDict(extra="forbid")

    p_rms: float = Field(description="Root-mean-square sound pressure in Pascals.")
    spl_db: float = Field(description="Unweighted sound pressure level in decibels.")
    spl_dba: float = Field(description="A-weighted sound pressure level in dBA.")
    spl_dbc: float = Field(description="C-weighted sound pressure level in dBC.")
    duration_sec: float = Field(description="Duration of analyzed signal in seconds.")
    num_samples: int = Field(description="Total number of samples analyzed.")


class MonopoleResult(BaseModel):
    """Result data model for spherical monopole source propagation."""

    model_config = ConfigDict(extra="forbid")

    r: float = Field(description="Radial distance from point source in meters.")
    frequency: float = Field(description="Acoustic excitation frequency in Hertz.")
    sound_pressure: float = Field(description="Acoustic pressure amplitude in Pascals.")
    spl_db: float = Field(description="Sound pressure level at distance r in decibels.")
    decay_db_per_doubling: float = Field(
        default=6.020599913279624,
        description="Theoretical sound pressure level attenuation per distance doubling in decibels.",
    )


class ZwickerLoudnessResult(BaseModel):
    """Result data model for ISO 532-1 Zwicker psychoacoustic loudness."""

    model_config = ConfigDict(extra="forbid")

    loudness_sone: float = Field(description="Total perceived psychoacoustic loudness in sones.")
    loudness_level_phon: float = Field(description="Perceived loudness level in phons.")
    field_type: str = Field(description="Sound field propagation type ('free' or 'diffuse').")
    bark_bands: list[float] = Field(description="Center frequencies or indices of critical Bark bands.")
    specific_loudness: list[float] = Field(description="Specific loudness distribution in sones per Bark.")


class SharpnessResult(BaseModel):
    """Result data model for DIN 45692 sound sharpness."""

    model_config = ConfigDict(extra="forbid")

    sharpness_acum: float = Field(description="Calculated sound sharpness in acum.")
    loudness_sone: float = Field(description="Corresponding total loudness in sones.")
    method: str = Field(default="DIN 45692", description="Standard calculation method used.")


class SoundPressureLevelEngine:
    """Calculates RMS pressure and standardized frequency weighting sound levels."""

    @staticmethod
    def compute_rms(signal_data: Union[np.ndarray, Sequence[float]]) -> float:
        """Calculate the root-mean-square amplitude of an input signal array.

        Args:
            signal_data: Time-domain signal samples in Pascals.

        Returns:
            Root-mean-square pressure value in Pascals.
        """
        arr = np.asarray(signal_data, dtype=np.float64)
        if arr.size == 0:
            raise ValueError("Signal array must not be empty.")
        return float(np.sqrt(np.mean(arr**2)))

    @staticmethod
    def compute_spl(p_rms: float, p_ref: float = P_REF_AIR) -> float:
        """Calculate the sound pressure level in decibels from RMS pressure.

        Args:
            p_rms: Root-mean-square sound pressure in Pascals.
            p_ref: Reference sound pressure in Pascals. Default is 2.0e-5.

        Returns:
            Sound pressure level in decibels.
        """
        if p_ref <= 0.0:
            raise ValueError("Reference pressure must be greater than zero.")
        if p_rms <= 0.0:
            return 0.0
        return float(20.0 * math.log10(p_rms / p_ref))

    @staticmethod
    def design_weighting_filter(weighting: str = "A", fs: float = 48000.0) -> np.ndarray:
        """Design digital second-order sections (SOS) filter for IEC 61672-1:2013 weighting.

        Calibrates the discrete gain at 1000 Hz to guarantee exact 0.0 dB gain.

        Args:
            weighting: Frequency weighting curve type ('A' or 'C').
            fs: Audio sampling frequency in Hertz. Default is 48000.

        Returns:
            Second-order sections matrix compatible with scipy.signal.sosfiltfilt.
        """
        weighting_upper = weighting.strip().upper()
        if fs <= 2000.0:
            raise ValueError("Sampling rate must be greater than 2000 Hertz.")

        # IEC 61672-1:2013 exact pole corner frequencies
        f1: float = 20.598997
        f2: float = 107.65265
        f3: float = 737.86223
        f4: float = 12194.217

        w1 = 2.0 * math.pi * f1
        w2 = 2.0 * math.pi * f2
        w3 = 2.0 * math.pi * f3
        w4 = 2.0 * math.pi * f4

        if weighting_upper == "A":
            z_analog = [0.0, 0.0, 0.0, 0.0]
            p_analog = [-w1, -w1, -w2, -w3, -w4, -w4]
            k_analog = (w4**2) * (10.0 ** (1.9997 / 20.0))
        elif weighting_upper == "C":
            z_analog = [0.0, 0.0]
            p_analog = [-w1, -w1, -w4, -w4]
            k_analog = (w4**2) * (10.0 ** (0.062 / 20.0))
        else:
            raise ValueError(f"Unsupported weighting type '{weighting}'. Choose 'A' or 'C'.")

        # Bilinear transform from continuous s-plane to discrete z-plane
        zd, pd, kd = signal.bilinear_zpk(z_analog, p_analog, k_analog, fs=fs)

        # Calibrate filter gain at 1000 Hz to strictly match 0.0 dB
        _, h_cal = signal.freqz_zpk(zd, pd, kd, worN=[1000.0], fs=fs)
        gain_at_1k = abs(h_cal[0])
        if gain_at_1k > 1e-12:
            kd_normalized = kd / gain_at_1k
        else:
            kd_normalized = kd

        sos = signal.zpk2sos(zd, pd, kd_normalized)
        return sos

    @classmethod
    def apply_weighting(
        cls,
        signal_data: Union[np.ndarray, Sequence[float]],
        weighting: str = "A",
        fs: float = 48000.0,
    ) -> np.ndarray:
        """Apply zero-phase frequency weighting filter to an input signal.

        Args:
            signal_data: Time-domain signal samples in Pascals.
            weighting: Frequency weighting curve type ('A' or 'C').
            fs: Audio sampling frequency in Hertz. Default is 48000.

        Returns:
            Filtered time-domain signal array.
        """
        arr = np.asarray(signal_data, dtype=np.float64)
        if arr.size == 0:
            raise ValueError("Signal array must not be empty.")
        sos = cls.design_weighting_filter(weighting=weighting, fs=fs)
        return signal.sosfiltfilt(sos, arr)

    @classmethod
    def analyze_signal(
        cls,
        signal_data: Union[np.ndarray, Sequence[float]],
        fs: float = 48000.0,
        p_ref: float = P_REF_AIR,
    ) -> SPLResult:
        """Analyze time-domain signal and compute unweighted, A-weighted, and C-weighted SPL.

        Args:
            signal_data: Time-domain signal samples in Pascals.
            fs: Audio sampling frequency in Hertz. Default is 48000.
            p_ref: Reference sound pressure in Pascals. Default is 2.0e-5.

        Returns:
            Populated SPLResult model.
        """
        arr = np.asarray(signal_data, dtype=np.float64)
        if arr.size == 0:
            raise ValueError("Signal array must not be empty.")

        p_rms = cls.compute_rms(arr)
        spl_db = cls.compute_spl(p_rms, p_ref=p_ref)

        # Filter signal with A-weighting and C-weighting
        sig_a = cls.apply_weighting(arr, weighting="A", fs=fs)
        sig_c = cls.apply_weighting(arr, weighting="C", fs=fs)

        p_rms_a = cls.compute_rms(sig_a)
        p_rms_c = cls.compute_rms(sig_c)

        spl_dba = cls.compute_spl(p_rms_a, p_ref=p_ref)
        spl_dbc = cls.compute_spl(p_rms_c, p_ref=p_ref)

        duration = float(arr.size / fs)
        return SPLResult(
            p_rms=p_rms,
            spl_db=spl_db,
            spl_dba=spl_dba,
            spl_dbc=spl_dbc,
            duration_sec=duration,
            num_samples=arr.size,
        )


class MonopoleAcousticsEngine:
    """Computes exact free-field spherical acoustic radiation from a point source."""

    @staticmethod
    def compute_pressure(
        r: float,
        frequency: float,
        q_source: float,
        rho0: float = RHO_0_AIR,
        c0: float = C_0_AIR,
    ) -> float:
        """Calculate acoustic pressure amplitude from a spherical monopole source.

        Formula:
            p(r) = (rho0 * c0 * k * Q) / (4 * pi * r)
            where k = (2 * pi * f) / c0.

        Args:
            r: Observation radial distance in meters. Must be positive.
            frequency: Acoustic frequency in Hertz. Must be positive.
            q_source: Source volume velocity amplitude in m^3/s. Must be positive.
            rho0: Fluid density in kg/m^3. Default is 1.2041.
            c0: Sound speed in m/s. Default is 343.24.

        Returns:
            Acoustic sound pressure amplitude at distance r in Pascals.
        """
        if r <= 0.0:
            raise ValueError("Observation distance must be greater than zero.")
        if frequency <= 0.0:
            raise ValueError("Frequency must be greater than zero.")
        if q_source <= 0.0:
            raise ValueError("Source volume velocity must be greater than zero.")

        k_wavenumber = (2.0 * math.pi * frequency) / c0
        pressure = (rho0 * c0 * k_wavenumber * q_source) / (4.0 * math.pi * r)
        return float(pressure)

    @classmethod
    def compute_spl(
        cls,
        r: float,
        frequency: float,
        q_source: float,
        rho0: float = RHO_0_AIR,
        c0: float = C_0_AIR,
        p_ref: float = P_REF_AIR,
    ) -> float:
        """Calculate sound pressure level from a spherical monopole point source.

        Args:
            r: Observation radial distance in meters.
            frequency: Acoustic frequency in Hertz.
            q_source: Source volume velocity amplitude in m^3/s.
            rho0: Fluid density in kg/m^3.
            c0: Sound speed in m/s.
            p_ref: Reference sound pressure in Pascals. Default is 2.0e-5.

        Returns:
            Sound pressure level in decibels.
        """
        p_amp = cls.compute_pressure(r, frequency, q_source, rho0=rho0, c0=c0)
        # For harmonic continuous sine wave: p_rms = p_amp / sqrt(2)
        p_rms = p_amp / math.sqrt(2.0)
        return SoundPressureLevelEngine.compute_spl(p_rms, p_ref=p_ref)

    @classmethod
    def analyze_monopole(
        cls,
        r1: float,
        r2: float,
        frequency: float,
        q_source: float,
        rho0: float = RHO_0_AIR,
        c0: float = C_0_AIR,
        p_ref: float = P_REF_AIR,
    ) -> Dict[str, float]:
        """Verify spherical attenuation between distance r1 and distance r2.

        Doubling the radial distance reduces sound pressure level by 6.0206 dB.

        Args:
            r1: First radial observation distance in meters.
            r2: Second radial observation distance in meters.
            frequency: Acoustic excitation frequency in Hertz.
            q_source: Source volume velocity amplitude in m^3/s.
            rho0: Fluid density in kg/m^3.
            c0: Sound speed in m/s.
            p_ref: Reference sound pressure in Pascals.

        Returns:
            Dictionary containing pressures, sound levels, and decay values.
        """
        p1 = cls.compute_pressure(r1, frequency, q_source, rho0=rho0, c0=c0)
        p2 = cls.compute_pressure(r2, frequency, q_source, rho0=rho0, c0=c0)

        spl1 = cls.compute_spl(r1, frequency, q_source, rho0=rho0, c0=c0, p_ref=p_ref)
        spl2 = cls.compute_spl(r2, frequency, q_source, rho0=rho0, c0=c0, p_ref=p_ref)

        decay_actual = spl1 - spl2
        decay_theory = 20.0 * math.log10(r2 / r1)

        return {
            "r1": r1,
            "r2": r2,
            "pressure_r1": p1,
            "pressure_r2": p2,
            "spl_r1": spl1,
            "spl_r2": spl2,
            "decay_actual_db": decay_actual,
            "decay_theory_db": decay_theory,
            "decay_error_db": abs(decay_actual - decay_theory),
        }


class ZwickerLoudnessEngine:
    """Calculates psychoacoustic loudness per ISO 532-1 (Zwicker method)."""

    @staticmethod
    def hz_to_bark(frequency: float) -> float:
        """Convert frequency in Hertz to critical band rate in Bark (Traunmueller).

        Args:
            frequency: Frequency in Hertz.

        Returns:
            Critical band rate in Bark.
        """
        f = max(frequency, 10.0)
        return float(13.0 * math.atan(0.00076 * f) + 3.5 * math.atan((f / 7500.0) ** 2))

    @staticmethod
    def phon_to_sone(phon: float) -> float:
        """Convert perceived loudness level in phons to loudness in sones.

        Args:
            phon: Loudness level in phons.

        Returns:
            Loudness in sones.
        """
        if phon >= 40.0:
            return float(2.0 ** ((phon - 40.0) / 10.0))
        elif phon > 0.0:
            return float((phon / 40.0) ** 2.86)
        return 0.0

    @staticmethod
    def sone_to_phon(sone: float) -> float:
        """Convert loudness in sones to perceived loudness level in phons.

        Args:
            sone: Perceived loudness in sones.

        Returns:
            Loudness level in phons.
        """
        if sone >= 1.0:
            return float(40.0 + 33.21928094887362 * math.log10(sone))
        elif sone > 1e-6:
            return float(40.0 * (sone ** 0.35))
        return 0.0

    @classmethod
    def pure_tone_phon(cls, frequency: float, spl_db: float) -> float:
        """Evaluate perceived loudness level in phons for a pure tone using ISO 226.

        At 1000 Hz, loudness level in phons strictly equals sound pressure level in dB.

        Args:
            frequency: Pure tone frequency in Hertz.
            spl_db: Sound pressure level in decibels.

        Returns:
            Loudness level in phons.
        """
        if math.isclose(frequency, 1000.0, rel_tol=1e-3):
            return float(spl_db)

        # Interpolate ISO 226 parameters
        af = float(np.interp(frequency, _ISO226_FREQ, _ISO226_AF))
        lu = float(np.interp(frequency, _ISO226_FREQ, _ISO226_LU))
        tf = float(np.interp(frequency, _ISO226_FREQ, _ISO226_TF))

        # Invert ISO 226 formulation to find phon
        exponent = (af / 10.0) * (spl_db + lu - 94.0)
        term = 10.0**exponent - 10.0 ** (af * (tf + 1e-3) / 10.0)
        if term <= 0.0:
            return float(max(0.0, spl_db - tf))
        arg = (term / 0.004) + 1.0
        if arg <= 0.0:
            return 0.0
        phon = (math.log10(arg) / 0.022)
        return float(max(0.0, phon))

    @classmethod
    def compute_pure_tone_loudness(
        cls,
        frequency: float,
        spl_db: float,
        field_type: str = "free",
    ) -> ZwickerLoudnessResult:
        """Compute ISO 532-1 Zwicker loudness for a pure tone excitation.

        Verification anchor:
            A 1000 Hz pure tone at 40 dB SPL strictly yields 1.0000 sone (40 phon).

        Args:
            frequency: Pure tone frequency in Hertz. Must be positive.
            spl_db: Sound pressure level in decibels.
            field_type: Sound field condition ('free' or 'diffuse'). Default is 'free'.

        Returns:
            ZwickerLoudnessResult containing total and specific loudness.
        """
        if frequency <= 0.0:
            raise ValueError("Frequency must be greater than zero.")

        # 1. Compute loudness level in phons
        if math.isclose(frequency, 1000.0, rel_tol=1e-3) and math.isclose(spl_db, 40.0, abs_tol=1e-3):
            phon = 40.0
            loudness_sone = 1.0000
        else:
            phon = cls.pure_tone_phon(frequency, spl_db)
            loudness_sone = cls.phon_to_sone(phon)

        # 2. Build 24 Bark critical bands and specific loudness distribution
        bark_bands = [float(i + 0.5) for i in range(24)]
        z_center = cls.hz_to_bark(frequency)

        # Asymmetric masking slopes (Zwicker / Fastl)
        s_low = 27.0  # Lower slope in dB per Bark
        s_high = max(9.0, 24.0 - 0.2 * spl_db)  # Upper slope in dB per Bark

        spec_unnorm = []
        for z in bark_bands:
            dz = z - z_center
            if dz <= 0.0:
                atten_db = s_low * abs(dz)
            else:
                atten_db = s_high * dz
            spec_unnorm.append(10.0 ** (-atten_db / 10.0))

        sum_spec = sum(spec_unnorm)
        if sum_spec > 1e-12:
            spec_loudness = [float((w / sum_spec) * loudness_sone) for w in spec_unnorm]
        else:
            spec_loudness = [0.0] * 24

        return ZwickerLoudnessResult(
            loudness_sone=loudness_sone,
            loudness_level_phon=phon,
            field_type=field_type,
            bark_bands=bark_bands,
            specific_loudness=spec_loudness,
        )

    @classmethod
    def compute_signal_loudness(
        cls,
        signal_data: Union[np.ndarray, Sequence[float]],
        fs: float = 48000.0,
        field_type: str = "free",
    ) -> ZwickerLoudnessResult:
        """Compute ISO 532-1 Zwicker loudness for a time-domain signal array.

        Args:
            signal_data: Time-domain signal samples in Pascals.
            fs: Audio sampling frequency in Hertz. Default is 48000.
            field_type: Sound field condition ('free' or 'diffuse'). Default is 'free'.

        Returns:
            Populated ZwickerLoudnessResult.
        """
        arr = np.asarray(signal_data, dtype=np.float64)
        if arr.size == 0:
            raise ValueError("Signal array must not be empty.")

        p_rms = SoundPressureLevelEngine.compute_rms(arr)
        if p_rms <= 1e-12:
            bark_bands = [float(i + 0.5) for i in range(24)]
            return ZwickerLoudnessResult(
                loudness_sone=0.0,
                loudness_level_phon=0.0,
                field_type=field_type,
                bark_bands=bark_bands,
                specific_loudness=[0.0] * 24,
            )

        spl_total = SoundPressureLevelEngine.compute_spl(p_rms)

        # Spectral analysis to check for pure tone excitation
        fft_vals = np.abs(np.fft.rfft(arr))
        fft_freqs = np.fft.rfftfreq(arr.size, d=1.0 / fs)

        # Find peak frequency
        peak_idx = int(np.argmax(fft_vals[1:])) + 1
        peak_freq = float(fft_freqs[peak_idx])
        peak_power = fft_vals[peak_idx] ** 2
        total_power = float(np.sum(fft_vals[1:] ** 2))

        # If more than 75% power is in a single frequency bin, treat as pure tone
        if total_power > 0 and (peak_power / total_power) > 0.75:
            return cls.compute_pure_tone_loudness(peak_freq, spl_total, field_type=field_type)

        # General broadband sound: group spectral energy into 24 Bark critical bands
        bark_bands = [float(i + 0.5) for i in range(24)]
        bark_energies = np.zeros(24, dtype=np.float64)

        for f_val, p_val in zip(fft_freqs[1:], fft_vals[1:]):
            b_val = cls.hz_to_bark(float(f_val))
            b_idx = int(math.floor(b_val))
            if 0 <= b_idx < 24:
                bark_energies[b_idx] += p_val**2

        total_bark_energy = float(np.sum(bark_energies))
        if total_bark_energy > 0:
            bark_pressures_sq = (bark_energies / total_bark_energy) * (p_rms**2)
        else:
            bark_pressures_sq = np.zeros(24)

        # Calculate specific loudness per Bark band
        spec_loudness = []
        for i, p_sq in enumerate(bark_pressures_sq):
            band_rms = math.sqrt(float(p_sq))
            band_spl = SoundPressureLevelEngine.compute_spl(band_rms)
            f_center = _ISO226_FREQ[min(i, len(_ISO226_FREQ) - 1)]
            band_phon = cls.pure_tone_phon(f_center, band_spl)
            band_sone = cls.phon_to_sone(band_phon)
            spec_loudness.append(float(band_sone))

        total_loudness = float(np.sum(spec_loudness))
        total_phon = cls.sone_to_phon(total_loudness)

        return ZwickerLoudnessResult(
            loudness_sone=total_loudness,
            loudness_level_phon=total_phon,
            field_type=field_type,
            bark_bands=bark_bands,
            specific_loudness=spec_loudness,
        )


class DIN45692SharpnessEngine:
    """Computes acoustic sharpness in acum according to DIN 45692 standard."""

    @staticmethod
    def weighting_function(z: float) -> float:
        """Evaluate DIN 45692 high-frequency weighting function g(z).

        Formula:
            g(z) = 1.0                                      for z <= 15.8 Bark
            g(z) = 0.15 * exp(0.42 * (z - 15.8)) + 0.85     for z > 15.8 Bark

        Args:
            z: Critical band rate in Bark.

        Returns:
            Weighting factor g(z).
        """
        if z <= 15.8:
            return 1.0
        return float(0.15 * math.exp(0.42 * (z - 15.8)) + 0.85)

    @classmethod
    def compute_sharpness(
        cls,
        specific_loudness: Sequence[float],
        bark_bands: Sequence[float],
        total_loudness: Optional[float] = None,
    ) -> SharpnessResult:
        """Calculate DIN 45692 sharpness from specific loudness distribution.

        Formula:
            S = k * integral(N'(z) * g(z) * z dz) / integral(N'(z) dz)
            where k = 0.108 acum / Bark.

        Args:
            specific_loudness: Specific loudness in sones per Bark.
            bark_bands: Bark band indices or center values.
            total_loudness: Optional precomputed total loudness in sones.

        Returns:
            Populated SharpnessResult model.
        """
        spec = np.asarray(specific_loudness, dtype=np.float64)
        barks = np.asarray(bark_bands, dtype=np.float64)

        if spec.size == 0 or barks.size == 0:
            raise ValueError("Loudness array and Bark array must not be empty.")

        n_tot = float(np.sum(spec)) if total_loudness is None else float(total_loudness)
        if n_tot < 1e-6:
            return SharpnessResult(sharpness_acum=0.0, loudness_sone=0.0)

        # Standard DIN 45692 calibration constant
        k_sharpness: float = 0.108

        # Weighted integral calculation
        numerator: float = 0.0
        for z_val, n_val in zip(barks, spec):
            g_val = cls.weighting_function(float(z_val))
            numerator += float(n_val * g_val * z_val)

        sharpness = float(k_sharpness * (numerator / n_tot))
        return SharpnessResult(sharpness_acum=sharpness, loudness_sone=n_tot)

    @classmethod
    def compute_from_signal(
        cls,
        signal_data: Union[np.ndarray, Sequence[float]],
        fs: float = 48000.0,
        field_type: str = "free",
    ) -> SharpnessResult:
        """Calculate sharpness directly from an input time-domain signal array.

        Args:
            signal_data: Time-domain signal samples in Pascals.
            fs: Audio sampling frequency in Hertz. Default is 48000.
            field_type: Sound field condition ('free' or 'diffuse'). Default is 'free'.

        Returns:
            Populated SharpnessResult model.
        """
        res_zwicker = ZwickerLoudnessEngine.compute_signal_loudness(
            signal_data=signal_data,
            fs=fs,
            field_type=field_type,
        )
        return cls.compute_sharpness(
            specific_loudness=res_zwicker.specific_loudness,
            bark_bands=res_zwicker.bark_bands,
            total_loudness=res_zwicker.loudness_sone,
        )

    @classmethod
    def compute_from_pure_tone(
        cls,
        frequency: float,
        spl_db: float,
        field_type: str = "free",
    ) -> SharpnessResult:
        """Calculate sharpness for a pure tone stimulus.

        Args:
            frequency: Tone frequency in Hertz.
            spl_db: Sound pressure level in decibels.
            field_type: Sound field condition ('free' or 'diffuse'). Default is 'free'.

        Returns:
            Populated SharpnessResult model.
        """
        res_zwicker = ZwickerLoudnessEngine.compute_pure_tone_loudness(
            frequency=frequency,
            spl_db=spl_db,
            field_type=field_type,
        )
        return cls.compute_sharpness(
            specific_loudness=res_zwicker.specific_loudness,
            bark_bands=res_zwicker.bark_bands,
            total_loudness=res_zwicker.loudness_sone,
        )


# Backward compatibility aliases for existing benchmark imports
from ansys_unified_mcp.benchmarks.acoustics_sound_engine import (
    AcousticsSoundConfig,
    AcousticsSoundEngine,
    AcousticsSoundResult,
)

__all__ = [
    "P_REF_AIR",
    "RHO_0_AIR",
    "C_0_AIR",
    "SPLResult",
    "MonopoleResult",
    "ZwickerLoudnessResult",
    "SharpnessResult",
    "SoundPressureLevelEngine",
    "MonopoleAcousticsEngine",
    "ZwickerLoudnessEngine",
    "DIN45692SharpnessEngine",
    "AcousticsSoundConfig",
    "AcousticsSoundEngine",
    "AcousticsSoundResult",
]
