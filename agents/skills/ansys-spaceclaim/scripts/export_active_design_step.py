import argparse
import json
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Export the active SpaceClaim design to STEP")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", required=True, type=int)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--connect-timeout", default=60, type=int)
    parser.add_argument("--max-message-mib", type=int)
    args = parser.parse_args()

    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    if args.connect_timeout <= 0:
        parser.error("--connect-timeout must be positive")
    if args.max_message_mib is not None and not 1 <= args.max_message_mib <= 1024:
        parser.error("--max-message-mib must be between 1 and 1024")
    if not os.path.isdir(args.output_dir):
        parser.error("--output-dir must be an existing directory")

    if args.max_message_mib is not None:
        os.environ["PYGEOMETRY_MAX_MESSAGE_LENGTH"] = str(args.max_message_mib * 1024 * 1024)

    try:
        from ansys.geometry.core import Modeler

        modeler = Modeler(
            host=args.host,
            port=args.port,
            transport_mode="insecure",
            timeout=args.connect_timeout,
        )
        design = modeler.read_existing_design()
        if design is None or not design.is_active:
            raise RuntimeError("no active design was returned by the connected service")
        output_dir = Path(args.output_dir).resolve()
        design_name = str(design.name)
        if not design_name or design_name in (".", "..") or "/" in design_name or "\\" in design_name:
            raise RuntimeError("design name cannot be used as a STEP filename")
        expected_path = (output_dir / (design_name + ".stp")).resolve()
        if expected_path.parent != output_dir:
            raise RuntimeError("derived STEP path escapes the requested output directory")
        if expected_path.exists():
            raise RuntimeError("refusing to overwrite existing file: " + str(expected_path))

        output_path = design.export_to_step(str(output_dir))
        if Path(output_path).resolve() != expected_path:
            raise RuntimeError("exported STEP path does not match the expected output path")
        if not os.path.isfile(output_path) or os.path.getsize(output_path) <= 0:
            raise RuntimeError("STEP export did not produce a non-empty file")
        print(json.dumps({
            "design": design.name,
            "output_path": str(output_path),
            "output_bytes": os.path.getsize(output_path),
        }, ensure_ascii=False))
        return 0
    except Exception as error:
        print("STEP export failed: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
