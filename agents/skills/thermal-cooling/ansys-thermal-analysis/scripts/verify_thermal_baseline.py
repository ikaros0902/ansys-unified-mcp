# -*- coding: utf-8 -*-
"""Verification baseline script for 1D Fourier thermal conduction."""

def calculate_conduction_heat_flux(k: float, t_hot: float, t_cold: float, length: float) -> float:
    # Fourier Law: q = k * (T_hot - T_cold) / L
    if length <= 0:
        raise ValueError("Length must be positive.")
    return k * (t_hot - t_cold) / length

if __name__ == "__main__":
    flux = calculate_conduction_heat_flux(200.0, 100.0, 20.0, 0.1)
    print(f"Heat flux: {flux:.1f} W/m2")
    assert abs(flux - 160000.0) < 1e-4, "Fourier conduction mismatch"
    print("Thermal conduction baseline check PASSED.")
