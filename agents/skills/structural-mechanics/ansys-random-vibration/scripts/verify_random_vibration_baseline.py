# -*- coding: utf-8 -*-
"""Verification baseline script for Miles equation random vibration."""
import math

def calculate_miles_equation_grms(fn: float, psd_g2_hz: float, q_factor: float) -> float:
    # Miles single-DOF equation: G_rms = sqrt(pi/2 * fn * Q * PSD)
    g_rms = math.sqrt((math.pi / 2.0) * fn * q_factor * psd_g2_hz)
    return g_rms

if __name__ == "__main__":
    g_rms = calculate_miles_equation_grms(100.0, 0.04, 10.0)
    print(f"Calculated 1-sigma Grms: {g_rms:.2f} G")
    assert 7.0 < g_rms < 9.0, "Miles equation expectation mismatch"
    print("Random vibration baseline check PASSED.")
