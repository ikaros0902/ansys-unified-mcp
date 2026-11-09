# -*- coding: utf-8 -*-
"""Verification baseline script for Icepak 1D thermal resistance."""

def calculate_junction_temperature(power_w: float, r_jc: float, r_cs: float, r_sa: float, t_ambient: float) -> float:
    # 1D thermal resistance network: T_j = T_amb + P * (R_jc + R_cs + R_sa)
    total_r = r_jc + r_cs + r_sa
    t_junction = t_ambient + power_w * total_r
    return t_junction

if __name__ == "__main__":
    tj = calculate_junction_temperature(50.0, 0.5, 0.2, 0.8, 25.0)
    print(f"Junction temperature: {tj:.1f} C")
    assert abs(tj - 100.0) < 1e-4, "Thermal network mismatch"
    print("Icepak 1D thermal baseline check PASSED.")
