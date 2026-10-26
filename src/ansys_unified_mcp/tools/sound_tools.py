# -*- coding: utf-8 -*-
# Strictly ASCII English Comments
"""Acoustic and Sound Analysis MCP Tools (sound_tools.py).

Provides MCP tools for computational acoustics and psychoacoustics:
1. sound_calculate_sound_pressure_level: Root-mean-square pressure and SPL (dB, dBA, dBC).
2. sound_calculate_zwicker_loudness: ISO 532-1 Zwicker psychoacoustic loudness (sone, phon).
3. sound_calculate_sharpness: DIN 45692 sound sharpness (acum).

All docstrings and exception messages follow ASD-STE100 guidelines.
All internal comments strictly use ASCII English characters.
"""

from __future__ import annotations

import logging
from typing import Annotated, Optional

from pydantic import Field

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.schemas.tool_annotations import create_tool_annotations
from ansys_unified_mcp.benchmarks.sound_acoustics_engine import (
    DIN45692SharpnessEngine,
    P_REF_AIR,
    SoundPressureLevelEngine,
    ZwickerLoudnessEngine,
)

logger = logging.getLogger("ansys-unified-mcp.sound_tools")

# Standard 4-key tool annotations for read-only idempotent acoustics operations
_READ_ONLY_ANNOTATIONS = create_tool_annotations(
    read_only=True,
    destructive=False,
    idempotent=True,
    open_world=False,
)


@mcp.tool(annotations=_READ_ONLY_ANNOTATIONS)
def sound_calculate_sound_pressure_level(
    signal: Annotated[
        list[float],
        Field(description="Time-domain acoustic pressure samples in Pascals."),
    ],
    sampling_rate: Annotated[
        float,
        Field(default=48000.0, ge=1000.0, description="Sampling rate of the audio signal in Hertz."),
    ] = 48000.0,
    p_ref: Annotated[
        float,
        Field(default=P_REF_AIR, gt=0.0, description="Reference sound pressure in Pascals."),
    ] = P_REF_AIR,
) -> dict:
    """Calculate sound pressure level from a time-domain acoustic signal.

    This tool calculates root-mean-square pressure and decibel levels.
    It returns unweighted decibels, A-weighted decibels, and C-weighted decibels.

    Args:
        signal: Time-domain acoustic pressure samples in Pascals.
        sampling_rate: Sampling rate of the audio signal in Hertz. Default is 48000.
        p_ref: Reference sound pressure in Pascals. Default is 2.0e-5.

    Returns:
        Standard envelope dictionary with RMS pressure and sound levels.
    """
    if not signal:
        return _envelope({"error": "Signal array must not be empty."})

    try:
        res = SoundPressureLevelEngine.analyze_signal(
            signal_data=signal,
            fs=sampling_rate,
            p_ref=p_ref,
        )
        return _envelope({
            "p_rms": res.p_rms,
            "spl_db": res.spl_db,
            "spl_dba": res.spl_dba,
            "spl_dbc": res.spl_dbc,
            "duration_sec": res.duration_sec,
            "num_samples": res.num_samples,
        })
    except Exception as exc:
        logger.error(f"Error calculating sound pressure level: {exc}")
        return _envelope({"error": f"Failed to calculate sound pressure level: {str(exc)}"})


@mcp.tool(annotations=_READ_ONLY_ANNOTATIONS)
def sound_calculate_zwicker_loudness(
    frequency: Annotated[
        Optional[float],
        Field(default=None, gt=0.0, description="Optional pure tone frequency in Hertz."),
    ] = None,
    spl_db: Annotated[
        Optional[float],
        Field(default=None, description="Optional sound pressure level in decibels."),
    ] = None,
    signal: Annotated[
        Optional[list[float]],
        Field(default=None, description="Optional time-domain acoustic pressure samples in Pascals."),
    ] = None,
    sampling_rate: Annotated[
        float,
        Field(default=48000.0, ge=1000.0, description="Sampling rate of the audio signal in Hertz."),
    ] = 48000.0,
    field_type: Annotated[
        str,
        Field(default="free", description="Sound field type: 'free' or 'diffuse'."),
    ] = "free",
) -> dict:
    """Calculate ISO 532-1 Zwicker psychoacoustic loudness in sones and phons.

    This tool evaluates loudness for pure tones or time-domain signals.
    A 1000 Hertz tone at 40 decibels strictly yields 1.0 sone (40 phon).

    Args:
        frequency: Optional pure tone frequency in Hertz.
        spl_db: Optional sound pressure level in decibels.
        signal: Optional time-domain acoustic pressure samples in Pascals.
        sampling_rate: Audio sampling frequency in Hertz. Default is 48000.
        field_type: Sound field propagation type. Default is 'free'.

    Returns:
        Standard envelope dictionary with loudness in sones and phons.
    """
    field_norm = field_type.strip().lower()
    if field_norm not in ("free", "diffuse"):
        return _envelope({"error": "Field type must be 'free' or 'diffuse'."})

    try:
        if frequency is not None:
            if spl_db is None:
                return _envelope({"error": "Provide spl_db when frequency is specified."})
            res = ZwickerLoudnessEngine.compute_pure_tone_loudness(
                frequency=frequency,
                spl_db=spl_db,
                field_type=field_norm,
            )
        elif signal is not None:
            if not signal:
                return _envelope({"error": "Signal array must not be empty."})
            res = ZwickerLoudnessEngine.compute_signal_loudness(
                signal_data=signal,
                fs=sampling_rate,
                field_type=field_norm,
            )
        else:
            return _envelope({"error": "Provide either frequency and spl_db or a time-domain signal."})

        return _envelope({
            "loudness_sone": res.loudness_sone,
            "loudness_level_phon": res.loudness_level_phon,
            "field_type": res.field_type,
            "specific_loudness": res.specific_loudness,
            "bark_bands": res.bark_bands,
        })
    except Exception as exc:
        logger.error(f"Error calculating Zwicker loudness: {exc}")
        return _envelope({"error": f"Failed to calculate Zwicker loudness: {str(exc)}"})


@mcp.tool(annotations=_READ_ONLY_ANNOTATIONS)
def sound_calculate_sharpness(
    frequency: Annotated[
        Optional[float],
        Field(default=None, gt=0.0, description="Optional pure tone frequency in Hertz."),
    ] = None,
    spl_db: Annotated[
        Optional[float],
        Field(default=None, description="Optional sound pressure level in decibels."),
    ] = None,
    signal: Annotated[
        Optional[list[float]],
        Field(default=None, description="Optional time-domain acoustic pressure samples in Pascals."),
    ] = None,
    sampling_rate: Annotated[
        float,
        Field(default=48000.0, ge=1000.0, description="Sampling rate of the audio signal in Hertz."),
    ] = 48000.0,
    field_type: Annotated[
        str,
        Field(default="free", description="Sound field type: 'free' or 'diffuse'."),
    ] = "free",
) -> dict:
    """Calculate DIN 45692 acoustic sharpness in acum.

    This tool evaluates perceived sharpness for pure tones or signals.
    It weights high frequencies above 15.8 Bark to measure spectral sharpness.

    Args:
        frequency: Optional pure tone frequency in Hertz.
        spl_db: Optional sound pressure level in decibels.
        signal: Optional time-domain acoustic pressure samples in Pascals.
        sampling_rate: Audio sampling frequency in Hertz. Default is 48000.
        field_type: Sound field propagation type. Default is 'free'.

    Returns:
        Standard envelope dictionary with sharpness in acum and loudness in sones.
    """
    field_norm = field_type.strip().lower()
    if field_norm not in ("free", "diffuse"):
        return _envelope({"error": "Field type must be 'free' or 'diffuse'."})

    try:
        if frequency is not None:
            if spl_db is None:
                return _envelope({"error": "Provide spl_db when frequency is specified."})
            res = DIN45692SharpnessEngine.compute_from_pure_tone(
                frequency=frequency,
                spl_db=spl_db,
                field_type=field_norm,
            )
        elif signal is not None:
            if not signal:
                return _envelope({"error": "Signal array must not be empty."})
            res = DIN45692SharpnessEngine.compute_from_signal(
                signal_data=signal,
                fs=sampling_rate,
                field_type=field_norm,
            )
        else:
            return _envelope({"error": "Provide either frequency and spl_db or a time-domain signal."})

        return _envelope({
            "sharpness_acum": res.sharpness_acum,
            "loudness_sone": res.loudness_sone,
            "method": res.method,
        })
    except Exception as exc:
        logger.error(f"Error calculating sound sharpness: {exc}")
        return _envelope({"error": f"Failed to calculate sound sharpness: {str(exc)}"})


__all__ = [
    "sound_calculate_sound_pressure_level",
    "sound_calculate_zwicker_loudness",
    "sound_calculate_sharpness",
]
