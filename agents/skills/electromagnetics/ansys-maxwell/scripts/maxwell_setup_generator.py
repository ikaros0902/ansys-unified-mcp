#!/usr/bin/env python3
"""Maxwell 2D/3D Motor Setup CLI Tool."""
import argparse
import json

def main():
    parser = argparse.ArgumentParser(description="Generate Maxwell setup parameters")
    parser.add_argument("--motor-type", choices=["bldc", "pmsm", "im"], default="pmsm")
    parser.add_argument("--rpm", type=float, default=3000.0)
    parser.add_argument("--output", default="maxwell_setup.json")
    args = parser.parse_args()

    config = {
        "motor_type": args.motor_type,
        "speed_rpm": args.rpm,
        "time_step_sec": (60.0 / args.rpm) / 360.0,
        "stop_time_sec": (60.0 / args.rpm) * 2.0
    }
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print(f"Maxwell setup exported to {args.output}")

if __name__ == "__main__":
    main()
