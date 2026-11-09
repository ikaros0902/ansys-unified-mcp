# -*- coding: utf-8 -*-
"""Verification baseline script for Zemax thin lens paraxial optics."""

def paraxial_matrix_transfer(focal_length: float, distance_in: float, distance_out: float) -> tuple[float, float]:
    # ABCD ray transfer matrix: Ray translation + Thin Lens + Ray translation
    # Ray vector [y, u]^T where y is height and u is ray angle
    y0 = 1.0  # 1 mm off-axis
    u0 = 0.0  # parallel incident ray
    # Translation to lens
    y1 = y0 + distance_in * u0
    u1 = u0
    # Refraction at thin lens: u2 = -y1/f + u1
    y2 = y1
    u2 = -y1 / focal_length + u1
    # Translation to image plane
    y3 = y2 + distance_out * u2
    u3 = u2
    return y3, u3

if __name__ == "__main__":
    y_focus, _ = paraxial_matrix_transfer(100.0, 50.0, 100.0)
    print(f"Ray height at focal plane: {y_focus:.4f}")
    assert abs(y_focus) < 1e-6, "Paraxial focus mismatch"
    print("Zemax paraxial baseline check PASSED.")
