#!/usr/bin/env python3
"""PyAEDT HFSS Project Configuration Tool."""
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Configure HFSS Setup via PyAEDT")
    parser.add_argument("--project", required=True, help="AEDT Project name")
    parser.add_argument("--freq-ghz", type=float, default=2.4, help="Solution frequency in GHz")
    parser.add_argument("--max-passes", type=int, default=15, help="Maximum adaptive passes")
    parser.add_argument("--output", default="hfss_config.json", help="Path to output summary")
    args = parser.parse_args()

    summary = {
        "project": args.project,
        "frequency_ghz": args.freq_ghz,
        "max_passes": args.max_passes,
        "delta_s": 0.02
    }
    Path(args.output).write_text(str(summary), encoding="utf-8")
    print(f"HFSS setup saved to {args.output}")

if __name__ == "__main__":
    main()
