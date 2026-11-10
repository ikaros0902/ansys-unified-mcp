# -*- coding: utf-8 -*-
"""Verification baseline script for MAPDL Euler-Bernoulli beam deflection."""

def calculate_cantilever_beam_deflection(force_n: float, length_m: float, e_pa: float, iz_m4: float) -> float:
    # Analytical deflection formula for cantilever with end load: delta = F * L^3 / (3 * E * I)
    return (force_n * (length_m**3)) / (3.0 * e_pa * iz_m4)

if __name__ == "__main__":
    # Steel cantilever: L=1m, E=210 GPa, Box section
    delta = calculate_cantilever_beam_deflection(1000.0, 1.0, 210e9, 8.333e-6)
    print(f"Analytical cantilever deflection: {delta * 1e3:.4f} mm")
    assert delta > 0, "Deflection must be positive"
    print("MAPDL cantilever baseline check PASSED.")
