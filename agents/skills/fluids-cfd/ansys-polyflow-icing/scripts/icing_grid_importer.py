#!/usr/bin/env python3
"""Polyflow / FENSAP-ICE Grid and Property Setup CLI Tool."""
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Configure Polyflow/Icing run parameters")
    parser.add_argument("--mesh", required=True, help="Input mesh path")
    parser.add_argument("--material-model", choices=["power_law", "carreau", "ptt"], default="carreau")
    parser.add_argument("--output", required=True, help="Output setup script path")
    args = parser.parse_args()

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(f"# Auto-generated configuration for {args.material_model}\n")
        f.write(f"MESH_PATH = '{args.mesh}'\n")
    print(f"Setup written to {args.output}")

if __name__ == "__main__":
    main()
