#!/usr/bin/env python3
"""Rocky DEM Particle Setup CLI."""
import argparse
import json

def main():
    parser = argparse.ArgumentParser(description="Configure Rocky DEM Particle Injection")
    parser.add_argument("--shape", choices=["polyhedron", "sphere", "fiber"], default="polyhedron")
    parser.add_argument("--mass-flow-rate", type=float, default=10.0, help="kg/s")
    parser.add_argument("--output", default="particle_setup.json")
    args = parser.parse_args()

    cfg = {
        "particle_shape": args.shape,
        "mass_flow_rate_kg_s": args.mass_flow_rate,
        "breakage_enabled": False
    }
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    print(f"Rocky config saved to {args.output}")

if __name__ == "__main__":
    main()
