# -*- coding: utf-8 -*-
"""Verification baseline script for Chemkin Arrhenius reaction rate."""
import math

def calculate_arrhenius_rate(a_factor: float, b_temp_exponent: float, ea_cal_mole: float, temp_k: float) -> float:
    # Arrhenius equation: k = A * T^b * exp(-Ea / (R * T))
    r_gas = 1.9872  # cal / (mol * K)
    k = a_factor * (temp_k ** b_temp_exponent) * math.exp(-ea_cal_mole / (r_gas * temp_k))
    return k

if __name__ == "__main__":
    rate = calculate_arrhenius_rate(1.0e13, 0.0, 30000.0, 1500.0)
    print(f"Arrhenius reaction rate constant: {rate:.4e}")
    assert rate > 0, "Reaction rate must be strictly positive"
    print("Chemkin Arrhenius baseline check PASSED.")
