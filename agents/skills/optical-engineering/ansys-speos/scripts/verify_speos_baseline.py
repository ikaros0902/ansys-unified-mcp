# -*- coding: utf-8 -*-
"""Verification baseline script for Speos photometric illumination."""
import math

def calculate_inverse_square_illuminance(intensity_cd: float, distance_m: float, angle_rad: float = 0.0) -> float:
    # Point source inverse-square law with Lambertian cosine factor
    if distance_m <= 0:
        raise ValueError("Distance must be positive.")
    return (intensity_cd / (distance_m**2)) * math.cos(angle_rad)

if __name__ == "__main__":
    ev = calculate_inverse_square_illuminance(100.0, 2.0, 0.0)
    print(f"Calculated illuminance: {ev:.2f} lux")
    assert abs(ev - 25.0) < 1e-4, "Inverse square law mismatch"
    print("Speos photometric baseline check PASSED.")
