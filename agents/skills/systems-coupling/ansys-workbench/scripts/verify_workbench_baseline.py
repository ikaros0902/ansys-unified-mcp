# -*- coding: utf-8 -*-
"""Verification baseline script for Workbench design point table parser."""
import csv
import io

def parse_design_point_table(csv_text: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    return list(reader)

if __name__ == "__main__":
    sample = "Name,P1_Length,P2_Force,P3_Stress\nDP 0,100,500,24.5\nDP 1,120,600,31.2"
    points = parse_design_point_table(sample)
    assert len(points) == 2
    assert points[0]["Name"] == "DP 0"
    print("Workbench design point baseline check PASSED.")
