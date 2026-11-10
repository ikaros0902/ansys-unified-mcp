#!/usr/bin/env python3
"""ACP Layup Definition CLI Generator."""
import argparse
import json

def main():
    parser = argparse.ArgumentParser(description="Generate Composite Layup Sequence")
    parser.add_argument("--angles", nargs="+", type=float, default=[0, 45, -45, 90, 90, -45, 45, 0], help="Ply angles in degrees")
    parser.add_argument("--thickness-mm", type=float, default=0.125)
    parser.add_argument("--output", default="layup_spec.json")
    args = parser.parse_args()

    plies = []
    for idx, angle in enumerate(args.angles):
        plies.append({
            "ply_id": f"P_{idx+1}",
            "angle": angle,
            "thickness_mm": args.thickness_mm,
            "material": "Carbon_Epoxy_UD"
        })

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"total_plies": len(plies), "stackup": plies}, f, indent=2)
    print(f"Layup spec exported to {args.output}")

if __name__ == "__main__":
    main()
