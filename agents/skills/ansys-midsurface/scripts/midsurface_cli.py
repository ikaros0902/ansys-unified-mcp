#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ANSYS Midsurface Engineering CLI Utility.

Follows the standard Agent Skill CLI pattern with subcommands:
- verify-sheet-metal: Evaluates whether a given geometry passes the Aspect Ratio Guard (span/thickness >= 2.0).
- audit: Audits an extracted midsurface body in SpaceClaim for topological continuity, countersink holes, and absence of 14.14mm chamfers.
"""

import argparse
import json
import os
import sys


def write_output(data, output_file):
    """Writes data to a JSON file."""
    try:
        out_dir = os.path.dirname(os.path.abspath(output_file))
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Success! Data written to: %s" % output_file)
    except Exception as ex:
        print("Error writing to file %s: %s" % (output_file, str(ex)), file=sys.stderr)
        sys.exit(1)


def cmd_verify_sheet_metal(args):
    """Evaluates the Aspect Ratio Guard and sheet metal criteria."""
    thickness_mm = args.thickness
    span_mm = args.span
    area_mm2 = args.area if args.area is not None else (span_mm * span_mm if span_mm else None)
    
    if area_mm2 is None and span_mm is None:
        print("Error: Must provide either --span or --area", file=sys.stderr)
        sys.exit(1)
        
    char_span_mm = span_mm if span_mm is not None else (area_mm2 ** 0.5)
    aspect_ratio = char_span_mm / thickness_mm if thickness_mm > 0 else 0.0
    min_aspect_ratio = args.min_ratio
    
    is_sheet = (aspect_ratio >= min_aspect_ratio) and (thickness_mm <= args.max_thickness)
    
    data = {
        "thickness_mm": thickness_mm,
        "characteristic_span_mm": round(char_span_mm, 3),
        "aspect_ratio": round(aspect_ratio, 3),
        "min_required_aspect_ratio": min_aspect_ratio,
        "max_allowed_thickness_mm": args.max_thickness,
        "is_sheet_metal": is_sheet,
        "classification": "Sheet Metal" if is_sheet else "Solid Bulk Block",
        "rationale": (
            "Passed Aspect Ratio Guard (span/t >= %.1f)" % min_aspect_ratio
            if is_sheet else
            "Failed Aspect Ratio Guard: span/t (%.2f) < %.1f. Equidimensional geometry violates thin-walled shell assumptions and must be modeled with solid elements." % (aspect_ratio, min_aspect_ratio)
        )
    }
    write_output(data, args.output)


def cmd_audit(args):
    """Audits extracted midsurface in live SpaceClaim session."""
    try:
        from ansys.geometry.core import Modeler
    except ImportError:
        print("Error: ansys-geometry-core is required for live audit.", file=sys.stderr)
        sys.exit(1)

    abs_out = os.path.abspath(args.output).replace("\\", "/")
    
    script_lines = [
        "import json, sys, os",
        "res = {}",
        "out_path = '%s'" % abs_out,
        "try:",
        "    all_bodies = list(GetRootPart().GetAllBodies())",
        "    target_mid = None",
        "    target_name = '%s'" % (args.body_name or ""),
        "    for b in all_bodies:",
        "        if target_name and target_name in b.Name:",
        "            target_mid = b",
        "            break",
        "        elif not target_name and ('Midsurface' in b.Name or 'MIDSURFACE' in b.Name):",
        "            target_mid = b",
        "            break",
        "    if not target_mid:",
        "        res = {'found': False, 'error': 'No midsurface body matching: ' + target_name}",
        "    else:",
        "        faces = list(target_mid.Faces)",
        "        edges = list(target_mid.Edges)",
        "        f_idx = {faces[i]: i for i in range(len(faces))}",
        "        adj = [set() for _ in range(len(faces))]",
        "        for e in edges:",
        "            ef = [f_idx[f] for f in e.Faces if f in f_idx]",
        "            for i in range(len(ef)):",
        "                for j in range(i + 1, len(ef)):",
        "                    adj[ef[i]].add(ef[j])",
        "                    adj[ef[j]].add(ef[i])",
        "        comps = []",
        "        vis = set()",
        "        for i in range(len(faces)):",
        "            if i in vis: continue",
        "            c = []",
        "            q = [i]",
        "            vis.add(i)",
        "            while q:",
        "                curr = q.pop(0)",
        "                c.append(curr)",
        "                for nb in adj[curr]:",
        "                    if nb not in vis:",
        "                        vis.add(nb)",
        "                        q.append(nb)",
        "            comps.append(c)",
        "        holes = []",
        "        has_1414 = False",
        "        for f in faces:",
        "            for e in f.Edges:",
        "                l = round(e.Shape.Length * 1000.0, 2)",
        "                if 14.0 < l < 14.2:",
        "                    has_1414 = True",
        "                if e.Shape.Geometry.__class__.__name__ == 'Circle':",
        "                    holes.append(round(e.Shape.Geometry.Radius * 1000.0, 2))",
        "        res = {",
        "            'found': True,",
        "            'body_name': target_mid.Name,",
        "            'faces_count': len(faces),",
        "            'edges_count': len(edges),",
        "            'components_count': len(comps),",
        "            'is_single_connected_body': len(comps) == 1,",
        "            'has_1414_chamfer': has_1414,",
        "            'hole_radii_mm': sorted(list(set(holes))),",
        "            'total_area_mm2': round(sum(f.Shape.Area * 1e6 for f in faces), 2)",
        "        }",
        "except Exception as ex:",
        "    res = {'error': str(ex)}",
        "with open(out_path, 'w') as f_out:",
        "    f_out.write(json.dumps(res, indent=2))"
    ]
    audit_script = "\n".join(script_lines)

    temp_script = os.path.join(os.path.dirname(os.path.abspath(args.output)), "_tmp_audit.py")
    with open(temp_script, "w", encoding="utf-8") as f:
        f.write(audit_script)
        
    m = None
    try:
        m = Modeler(host=args.host, port=args.port, transport_mode="insecure")
        m.run_script_file(temp_script, import_design=False)
        if os.path.exists(args.output):
            print("Success! Data written to: %s" % args.output)
        else:
            print("Audit completed but output file was not found: %s" % args.output, file=sys.stderr)
            sys.exit(1)
    except Exception as ex:
        print("Audit execution failed: %s" % str(ex), file=sys.stderr)
        sys.exit(1)
    finally:
        if m is not None and hasattr(m, "close"):
            try:
                m.close()
            except Exception:
                pass
        if os.path.exists(temp_script):
            os.remove(temp_script)


def main():
    parser = argparse.ArgumentParser(description="ANSYS Midsurface Engineering CLI Utility")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Subcommand: verify-sheet-metal
    p_vsm = subparsers.add_parser("verify-sheet-metal", help="Check if dimensions satisfy the Aspect Ratio Guard")
    p_vsm.add_argument("--thickness", type=float, required=True, help="Sheet thickness in mm")
    p_vsm.add_argument("--span", type=float, default=None, help="Characteristic surface span in mm")
    p_vsm.add_argument("--area", type=float, default=None, help="Surface area in mm^2")
    p_vsm.add_argument("--min-ratio", type=float, default=2.0, help="Minimum aspect ratio threshold (default 2.0)")
    p_vsm.add_argument("--max-thickness", type=float, default=3.0, help="Maximum allowed sheet thickness in mm")
    p_vsm.add_argument("--output", required=True, help="Output JSON file path")
    
    # Subcommand: audit
    p_audit = subparsers.add_parser("audit", help="Audit an extracted midsurface body in SpaceClaim")
    p_audit.add_argument("--body-name", default="", help="Sub-string of midsurface body name")
    p_audit.add_argument("--host", default="127.0.0.1", help="SpaceClaim gRPC host")
    p_audit.add_argument("--port", type=int, default=50051, help="SpaceClaim gRPC port")
    p_audit.add_argument("--output", required=True, help="Output JSON file path")
    
    args = parser.parse_args()
    if args.command == "verify-sheet-metal":
        cmd_verify_sheet_metal(args)
    elif args.command == "audit":
        cmd_audit(args)
    else:
        print("Unknown command: %s" % args.command, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
