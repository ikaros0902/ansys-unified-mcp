# -*- coding: utf-8 -*-
"""Verification baseline script for Discovery geometry bounding box check."""

def calculate_box_volume(xmin: float, xmax: float, ymin: float, ymax: float, zmin: float, zmax: float) -> float:
    dx = max(0.0, xmax - xmin)
    dy = max(0.0, ymax - ymin)
    dz = max(0.0, zmax - zmin)
    return dx * dy * dz

if __name__ == "__main__":
    v = calculate_box_volume(0, 10, 0, 20, 0, 5)
    assert abs(v - 1000.0) < 1e-6
    print("Discovery geometry volume check PASSED.")
