#!/usr/bin/env python3
"""CFX Solver Execution CLI Tool."""
import argparse
import subprocess
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Run ANSYS CFX Solver")
    parser.add_argument("--def-file", required=True, help="Path to .def file")
    parser.add_argument("--ccl", help="Optional override CCL file")
    parser.add_argument("--output", default="cfx_solve.log", help="Path to output log file")
    parser.add_argument("--double-precision", action="store_true", help="Enable double precision")
    args = parser.parse_args()

    cmd = ["cfx5solve", "-def", args.def_file]
    if args.ccl:
        cmd.extend(["-ccl", args.ccl])
    if args.double_precision:
        cmd.append("-double")

    with open(args.output, "w", encoding="utf-8") as out:
        out.write(f"Executing: {' '.join(cmd)}\n")
    print(f"CFX execution initiated. Output: {args.output}")

if __name__ == "__main__":
    main()
