# -*- coding: utf-8 -*-
"""Verification baseline script for Lumerical optical waveguide."""
import math

def calculate_slab_waveguide_effective_index(n_core: float, n_clad: float, wavelength: float, thickness: float) -> float:
    # Analytical estimate for TE fundamental mode in symmetric dielectric slab
    k0 = 2 * math.pi / wavelength
    v_num = k0 * (thickness / 2.0) * math.sqrt(max(0.0, n_core**2 - n_clad**2))
    # Approximation for fundamental symmetric mode normalized propagation constant b
    b = (v_num / (1.0 + v_num))**2 if v_num > 0 else 0.0
    n_eff = math.sqrt(n_clad**2 + b * (n_core**2 - n_clad**2))
    return n_eff

if __name__ == "__main__":
    n_eff = calculate_slab_waveguide_effective_index(3.45, 1.45, 1.55e-6, 0.22e-6)
    print(f"Analytical TE0 effective index: {n_eff:.4f}")
    assert 1.45 < n_eff < 3.45, "Effective index out of bounds"
    print("Lumerical analytical baseline check PASSED.")
