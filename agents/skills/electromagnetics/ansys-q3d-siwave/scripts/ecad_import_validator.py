#!/usr/bin/env python3
"""ECAD File Pre-check CLI for Q3D / SIwave."""
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Validate ECAD stackup file for Q3D/SIwave")
    parser.add_argument("--ecad-file", required=True, help="Path to ECAD file")
    parser.add_argument("--output", default="ecad_report.txt", help="Validation report")
    args = parser.parse_args()

    p = Path(args.ecad_file)
    valid = p.exists() and p.suffix.lower() in [".brd", ".xml", ".ipc", ".tgz"]
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(f"File: {p.name}\nExists: {p.exists()}\nValid Format: {valid}\n")
    print(f"Report written to {args.output}")

if __name__ == "__main__":
    main()
