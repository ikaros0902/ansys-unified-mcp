#!/usr/bin/env python3
"""ANSYS Motion Joint and Topology Definition CLI."""
import argparse
import json

def main():
    parser = argparse.ArgumentParser(description="Define Motion joints")
    parser.add_argument("--joint-type", choices=["revolute", "translational", "spherical", "fixed"], default="revolute")
    parser.add_argument("--body-a", required=True)
    parser.add_argument("--body-b", required=True)
    parser.add_argument("--output", default="motion_joint.json")
    args = parser.parse_args()

    joint_spec = {
        "type": args.joint_type,
        "base_body": args.body_a,
        "action_body": args.body_b,
        "friction_model": "None"
    }
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(joint_spec, f, indent=2)
    print(f"Motion joint spec created at {args.output}")

if __name__ == "__main__":
    main()
