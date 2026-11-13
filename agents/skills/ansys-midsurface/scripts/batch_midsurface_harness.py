#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Headless Batch Midsurface Harness.

Enables automated, non-interactive execution and testing of the
SpaceClaim Midsurface Agent extraction pipeline on solid bodies.
"""

import argparse
import json
import os
import sys


def write_output(data, output_file):
    try:
        out_dir = os.path.dirname(os.path.abspath(output_file))
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Success! Data written to: %s" % output_file)
    except Exception as ex:
        print("Error writing output file %s: %s" % (output_file, str(ex)), file=sys.stderr)
        sys.exit(1)


def generate_harness_script(target_filter, agent_dir, out_file):
    agent_dir_escaped = agent_dir.replace("\\", "/")
    out_file_escaped = out_file.replace("\\", "/")
    
    code = """
import sys, os, json, time

res = {"targets": [], "summary": {}}
agent_dir = "%s"
out_path = "%s"

for _mod in (
    "ms_usage_log", "ms_config", "ms_geometry", "ms_api", "ms_document",
    "ms_diagnostics", "ms_thickness", "ms_stitch", "ms_engine_offset",
    "ms_engine_native", "ms_audit", "ms_process", "ms_timing"
):
    mod_path = os.path.join(agent_dir, _mod + ".py")
    if os.path.exists(mod_path):
        execfile(mod_path, globals())

ctx, err = build_context(None)
if ctx:
    Matrix_identity_holder[0] = ctx.Matrix.Identity
    all_bodies = list(ms_descendants(ctx.root, ctx.IDesignBody))
    display_names = display_names_for(ctx, all_bodies, all_bodies, lambda b: source_base_name(ctx, b))
    
    filter_str = "%s"
    matched_bodies = []
    for b in all_bodies:
        dname = display_names.get(b, "")
        if "Midsurface" in dname or "MIDSURFACE" in dname or "TEST" in dname:
            continue
        if filter_str and filter_str.lower() not in dname.lower():
            continue
        matched_bodies.append((b, dname))
        
    succeeded = 0
    failed = 0
    skipped = 0
    t0 = time.clock() if hasattr(time, "clock") else time.time()
    
    for b, dname in matched_bodies:
        t_start = time.clock() if hasattr(time, "clock") else time.time()
        ok, msg, stats = process_single_body(ctx, b, dname)
        elapsed = (time.clock() if hasattr(time, "clock") else time.time()) - t_start
        
        status_str = "SUCCESS" if ok else ("SKIP" if "SKIP:" in str(msg) else "FAILED")
        if status_str == "SUCCESS": succeeded += 1
        elif status_str == "SKIP": skipped += 1
        else: failed += 1
        
        entry = {
            "name": dname,
            "status": status_str,
            "message": str(msg),
            "elapsed_seconds": round(elapsed, 2)
        }
        if stats:
            entry["area_ratio"] = stats.get("area_ratio")
            entry["components_count"] = stats.get("bodies")
            entry["thickness_mm"] = stats.get("thickness")
            entry["method"] = stats.get("method")
        res["targets"].append(entry)
        
    tot_time = (time.clock() if hasattr(time, "clock") else time.time()) - t0
    res["summary"] = {
        "total_evaluated": len(matched_bodies),
        "succeeded": succeeded,
        "skipped": skipped,
        "failed": failed,
        "total_elapsed_seconds": round(tot_time, 2)
    }

with open(out_path, "w") as f_out:
    f_out.write(json.dumps(res, indent=2))
""" % (agent_dir_escaped, out_file_escaped, target_filter)
    return code


def main():
    parser = argparse.ArgumentParser(description="Headless Midsurface Batch Test Harness")
    parser.add_argument("--target", default="", help="Sub-string to filter target body names (empty for all)")
    parser.add_argument("--agent-dir", default=r"D:\Ikaros\ACT_Test\1.Release Verison\SC-Midsurface\SC_midsurface_Agent", help="Path to SC_midsurface_Agent modules")
    parser.add_argument("--host", default="127.0.0.1", help="SpaceClaim gRPC host")
    parser.add_argument("--port", type=int, default=50051, help="SpaceClaim gRPC port")
    parser.add_argument("--output", required=True, help="Output JSON report path")
    args = parser.parse_args()

    try:
        from ansys.geometry.core import Modeler
    except ImportError:
        print("Error: ansys-geometry-core required", file=sys.stderr)
        sys.exit(1)

    abs_out = os.path.abspath(args.output)
    script_str = generate_harness_script(args.target, os.path.abspath(args.agent_dir), abs_out)
    temp_script = os.path.join(os.path.dirname(abs_out), "_tmp_harness.py")
    
    with open(temp_script, "w", encoding="utf-8") as f:
        f.write(script_str)
        
    m = None
    try:
        m = Modeler(host=args.host, port=args.port, transport_mode="insecure")
        m.run_script_file(temp_script, import_design=False)
        if os.path.exists(abs_out):
            print("Success! Data written to: %s" % abs_out)
        else:
            print("Harness finished but output file not found: %s" % abs_out, file=sys.stderr)
            sys.exit(1)
    except Exception as ex:
        print("Harness execution failed: %s" % str(ex), file=sys.stderr)
        sys.exit(1)
    finally:
        if m is not None and hasattr(m, "close"):
            try:
                m.close()
            except Exception:
                pass
        if os.path.exists(temp_script):
            os.remove(temp_script)


if __name__ == "__main__":
    main()
