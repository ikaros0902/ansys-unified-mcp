#!/usr/bin/env python
"""Run the installed SpaceClaim midsurface agent and checkpoint each result."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def _resolve_default_agent_dir() -> str:
    env_dir = os.environ.get("ANSYS_MIDSURFACE_AGENT_DIR", "").strip()
    if env_dir:
        return env_dir
    sibling = (
        Path(__file__).resolve().parents[5]
        / "ACT_Test"
        / "1.Release Verison"
        / "SC-Midsurface"
        / "SC_midsurface_Agent"
    )
    return str(sibling)


_DEFAULT_AGENT_DIR = _resolve_default_agent_dir()

# 內嵌程式會由 SpaceClaim 的 IronPython 2.7 執行。
_EMBEDDED = r'''
import hashlib as _h_hashlib
import io as _h_io
import json as _h_json
import os as _h_os
import re as _h_re
import time as _h_time
from collections import Counter as _h_counter

_h_cfg = _h_json.loads(__HARNESS_CONFIG__)
_h_views = ("front", "back", "left", "right", "top", "bottom")
_h_diagnostic_fields = (
    "coverage_pct", "unresolved_faces", "unresolved_area_mm2", "unresolved_fraction",
    "audit_missing_faces", "audit_missing_area_mm2", "audit_missing_fraction",
    "ratio_ok", "body_count_ok", "skin_ok", "audit_ok", "bbox_within_source",
    "dropped_fraction", "thickness_assigned",
)
_h_columns = (
    "run_id", "run_started_at_utc", "started_at_utc", "finished_at_utc",
    "host", "port", "agent_dir", "case_number", "name", "occurrence_path",
    "occurrence_id", "occurrence_id_status", "occurrence_path_status",
    "status", "message", "error_stage", "failure_reason", "method", "thickness_mm",
    "area_ratio", "components_count", "metrics_source",
) + _h_diagnostic_fields + (
    "elapsed_seconds", "case_dir",
    "agent_log_status", "agent_log_path", "agent_log_source", "agent_log_error",
    "temp_log_status", "temp_log_source", "temp_log_path", "temp_log_error",
    "capture_status", "screenshot_manifest", "capture_error",
)
try:
    _h_text = unicode
except NameError:
    _h_text = str


def _h_utc():
    return _h_time.strftime("%Y-%m-%dT%H:%M:%SZ", _h_time.gmtime())


def _h_utf8(value):
    try:
        return _h_text(value)
    except UnicodeError:
        return value.decode("utf-8", "replace")


def _h_write(path, content, mode="w"):
    with _h_io.open(path, mode, encoding="utf-8", newline="") as stream:
        stream.write(_h_utf8(content))
        stream.flush()


def _h_json_snapshot(path, payload):
    tmp = path + "." + _h_cfg["run_id"] + ".tmp"
    _h_write(tmp, _h_json.dumps(payload, indent=2, ensure_ascii=True) + "\n")
    if hasattr(_h_os, "replace"):
        _h_os.replace(tmp, path)
    else:
        from System.IO import File
        if File.Exists(path):
            File.Replace(tmp, path, None)
        else:
            File.Move(tmp, path)


def _h_csv_line(values):
    return ",".join(
        '"' + _h_utf8(value if value is not None else "").replace('"', '""') + '"'
        for value in values
    ) + "\r\n"


def _h_attr(obj, key):
    try:
        return getattr(obj, key, None)
    except Exception:
        return None


def _h_identity(body):
    names = []
    seen = []
    node = body
    while node is not None and len(seen) < 64:
        if any(node == previous for previous in seen):
            break
        seen.append(node)
        name = _h_attr(node, "Name") or _h_attr(_h_attr(node, "Master"), "Name")
        if name:
            names.append(_h_utf8(name))
        node = _h_attr(node, "Parent")
    moniker = _h_attr(body, "Moniker")
    return list(reversed(names)), (_h_utf8(moniker).strip() or None) if moniker is not None else None


def _h_identity_status(value, counts):
    if not value:
        return "unavailable"
    return "observed_unique" if counts[value] == 1 else "ambiguous"


def _h_read_log(path):
    try:
        with open(path, "rb") as stream:
            return stream.read()
    except (IOError, OSError):
        return None


def _h_log_signature(path, data):
    if data is None:
        return None
    try:
        return (_h_os.stat(path).st_mtime, _h_hashlib.sha256(data).hexdigest())
    except (IOError, OSError):
        return None


def _h_archive_log(entry, temp_log, before, timing_error):
    entry["temp_log_source"] = temp_log
    entry["temp_log_status"] = "ABSENT_OR_UNREADABLE"
    entry["temp_log_path"] = None
    try:
        data = _h_read_log(temp_log)
        after = _h_log_signature(temp_log, data)
        if after is not None:
            entry["temp_log_status"] = "UNCHANGED"
            if after != before:
                path = _h_os.path.join(entry["case_dir"], "unverified_SC_midsurface_Agent_last_run.txt")
                with open(path, "wb") as stream:
                    stream.write(data)
                    stream.flush()
                entry.update({
                    "temp_log_status": "UNVERIFIED_TEMP", "temp_log_path": path,
                    "temp_log_observed_at_utc": _h_utc(), "temp_log_mtime": after[0],
                    "temp_log_sha256": after[1],
                })
    except Exception as error:
        entry["temp_log_status"] = "ERROR"
        entry["temp_log_error"] = _h_utf8(error)

    entry["agent_log_source"] = "harness process_single_body result"
    path = _h_os.path.join(entry["case_dir"], "harness_case.txt")
    try:
        report = ""
        if not timing_error:
            try:
                report = ms_timing_report() or ""
            except Exception as error:
                timing_error = _h_utf8(error)
        _h_write(
            path,
            "Source: harness process_single_body result and available agent phase timing.\n"
            + "Run: " + entry["run_id"] + "\n"
            + "Finished: " + entry["finished_at_utc"] + "\n"
            + "Name: " + entry["name"] + "\n"
            + entry["status"] + ": " + entry["message"] + "\n"
            + ("Timing unavailable: " + (timing_error or "no timing data") + "\n" if not report else report),
        )
        entry["agent_log_status"] = "HARNESS_TIMING" if report else "HARNESS_RESULT"
        entry["agent_log_path"] = path
    except Exception as error:
        entry["agent_log_status"] = "ERROR"
        entry["agent_log_error"] = _h_utf8(error)


def _h_screenshots(entry):
    shots = _h_os.path.join(entry["case_dir"], "screenshots")
    _h_os.makedirs(shots)
    manifest = _h_os.path.join(shots, "manifest.json")
    entry["screenshot_manifest"] = manifest
    entry["capture_status"] = "pending"
    entry["screenshots"] = [
        {"view": view, "path": _h_os.path.join(shots, view + ".png"), "capture_status": "pending"}
        for view in _h_views
    ]
    _h_json_snapshot(manifest, {
        "run_id": entry["run_id"],
        "case_number": entry["case_number"],
        "status": entry["status"],
        "capture_status": "pending",
        "source_occurrence_id": entry["occurrence_id"],
        "source_occurrence_path": entry["occurrence_path"],
        "source_occurrence_id_status": entry["occurrence_id_status"],
        "source_occurrence_path_status": entry["occurrence_path_status"],
        "source_display_name": entry["name"],
        "expected_result_name": "FAIL_" + entry["name"] if entry["status"] == "INCOMPLETE" else None,
        "instructions": "Verify the live source and result before exporting. Reported IDs and paths only reflect the initial traversal.",
        "views": entry["screenshots"],
    })


def _h_case(ctx, body, name, path, moniker, i, id_status, path_status):
    entry = dict((key, _h_cfg[key]) for key in ("run_id", "run_started_at_utc", "host", "port", "agent_dir"))
    entry.update({
        "case_number": i, "name": name, "occurrence_path": path, "occurrence_id": moniker,
        "occurrence_id_status": id_status, "occurrence_path_status": path_status,
        "case_dir": _h_os.path.join(_h_cfg["run_dir"], "cases", "%04d" % i),
        "agent_log_path": None, "capture_status": "not_requested", "screenshot_manifest": None,
    })
    _h_os.makedirs(entry["case_dir"])
    temp_log = _h_os.path.join(
        _h_os.environ.get("TEMP") or _h_os.path.expanduser("~"),
        "SC_midsurface_Agent_last_run.txt",
    )
    before = _h_log_signature(temp_log, _h_read_log(temp_log))
    timing_error = None
    try:
        ms_timing_begin_run()
    except Exception as error:
        timing_error = _h_utf8(error)

    entry["started_at_utc"] = _h_utc()
    clock = getattr(_h_time, "perf_counter", getattr(_h_time, "clock", _h_time.time))
    t0 = clock()
    try:
        ok, message, stats = process_single_body(ctx, body, name)
    except Exception as error:
        ok, message, stats = False, _h_text(type(error).__name__) + ": " + _h_utf8(error), None
    entry["finished_at_utc"] = _h_utc()
    entry["elapsed_seconds"] = round(clock() - t0, 3)

    msg = _h_utf8(message)
    status = "SUCCESS" if ok else "FAIL"
    if not ok and msg.startswith(("SKIP:", "INCOMPLETE:")):
        status = msg.split(":", 1)[0]
    stage = "post_build_integrity_gate" if status == "INCOMPLETE" else None
    if status == "SKIP":
        skip_detail = msg[len("SKIP:"):].lstrip()
        part_prefix = "Part [%s] " % name
        if skip_detail.startswith(part_prefix):
            skip_detail = skip_detail[len(part_prefix):]
        stage = "unknown_skip_stage"
        for reason, reason_stage in (
            ("fewer than 2 faces", "face_count_precondition"),
            ("no valid primary opposing face pair", "primary_face_pair_detection"),
            ("did not pass sheet metal verification", "sheet_metal_verification"),
        ):
            if skip_detail.startswith((reason, "has " + reason)):
                stage = reason_stage
                break
    entry.update({
        "status": status, "message": msg, "method": None, "thickness_mm": None,
        "area_ratio": None, "components_count": None, "error_stage": stage,
        "failure_reason": msg if not ok else None, "metrics_source": None,
    })
    entry.update((field, None) for field in _h_diagnostic_fields)
    if stats:
        entry.update({
            "method": stats.get("method"), "thickness_mm": stats.get("thickness"),
            "area_ratio": stats.get("area_ratio"), "components_count": stats.get("bodies"),
            "agent_stats": stats, "metrics_source": "agent_stats",
        })
        entry.update((field, stats.get(field)) for field in _h_diagnostic_fields)
    elif status == "INCOMPLETE":
        # Older release agents return no stats on this path. Keep only explicit message values.
        method = _h_re.search(r", method: ([^,]+), Coverage:", msg)
        ratio = _h_re.search(r"area ratio ([0-9.]+) not in", msg)
        count = _h_re.search(r"(\d+) bodies survived stitching", msg)
        entry.update({
            "method": method.group(1) if method else None,
            "area_ratio": float(ratio.group(1)) if ratio else None,
            "components_count": int(count.group(1)) if count else None,
            "metrics_source": "agent_message",
        })

    _h_archive_log(entry, temp_log, before, timing_error)
    if status in ("FAIL", "INCOMPLETE"):
        try:
            _h_screenshots(entry)
        except Exception as error:
            entry["capture_status"] = "manifest_error"
            entry["capture_error"] = _h_utf8(error)
    return entry


def _h_run():
    cfg = _h_cfg
    report = dict(cfg)
    summary = {
        "total_matched": 0, "total_evaluated": 0, "succeeded": 0,
        "failed": 0, "incomplete": 0, "skipped": 0, "total_elapsed_seconds": 0.0,
    }
    report.update({"targets": [], "summary": summary, "run_status": "RUNNING"})
    t0 = _h_time.time()
    ctx = None
    _h_write(cfg["jsonl_path"], "")
    _h_write(cfg["csv_path"], _h_csv_line(_h_columns))
    _h_json_snapshot(cfg["report_path"], report)
    try:
        for module in (
            "ms_usage_log", "ms_config", "ms_geometry", "ms_api", "ms_document",
            "ms_diagnostics", "ms_thickness", "ms_stitch", "ms_engine_offset",
            "ms_engine_native", "ms_audit", "ms_process", "ms_timing"
        ):
            module_path = _h_os.path.join(cfg["agent_dir"], module + ".py")
            if _h_os.path.isfile(module_path):
                execfile(module_path, globals())
        timing_install = globals().get("ms_timing_install")
        if timing_install:
            timing_install()
        ctx, error = build_context(None)
        if error or not ctx:
            raise RuntimeError(error or "The agent returned no SpaceClaim context")
        if cfg["keep_source_visible"]:
            ctx.hide_source_bodies = False
        report["resolved_parameters"] = _h_attr(ctx, "param_summary")
        Matrix_identity_holder[0] = ctx.Matrix.Identity
        bodies = list(ms_descendants(ctx.root, ctx.IDesignBody))
        display_names = display_names_for(ctx, bodies, bodies, lambda body: source_base_name(ctx, body))
        matched = []
        identities = [(body, _h_identity(body)) for body in bodies]
        id_counts = _h_counter(moniker for body, (path, moniker) in identities)
        path_counts = _h_counter(tuple(path) for body, (path, moniker) in identities)
        for body, (path, moniker) in identities:
            name = _h_utf8(display_names.get(body, ""))
            if "_MIDSURFACE" in name.upper() or any(
                item.upper().startswith("MIDSURFACE - ") for item in path
            ):
                continue
            if cfg["target"].lower() not in name.lower():
                continue
            matched.append((body, name, path, moniker))
        summary["total_matched"] = len(matched)
        _h_json_snapshot(cfg["report_path"], report)

        counters = {"SUCCESS": "succeeded", "FAIL": "failed", "INCOMPLETE": "incomplete", "SKIP": "skipped"}
        for i, (body, name, path, moniker) in enumerate(matched, 1):
            entry = _h_case(
                ctx, body, name, path, moniker, i,
                _h_identity_status(moniker, id_counts), _h_identity_status(tuple(path), path_counts),
            )
            report["targets"].append(entry)
            summary["total_evaluated"] += 1
            summary[counters[entry["status"]]] += 1
            summary["total_elapsed_seconds"] = round(_h_time.time() - t0, 3)
            _h_json_snapshot(_h_os.path.join(entry["case_dir"], "result.json"), entry)
            _h_write(cfg["jsonl_path"], _h_json.dumps(entry, ensure_ascii=True) + "\n", "a")
            _h_write(cfg["csv_path"], _h_csv_line(
                _h_json.dumps(entry[key], ensure_ascii=False) if key == "occurrence_path" else entry.get(key)
                for key in _h_columns
            ), "a")
            if _h_attr(body, "IsDeleted") or "source body was deleted during processing" in entry["message"]:
                report["run_status"] = "ABORTED"
                report["error"] = "Source occurrence was deleted; no more cases were processed."
                break
            _h_json_snapshot(cfg["report_path"], report)
        else:
            report["run_status"] = "COMPLETED"
    except Exception as error:
        report["run_status"] = "ABORTED"
        report["error"] = _h_utf8(error)
    finally:
        if ctx and globals().get("restore_active_component"):
            try:
                restore_active_component(ctx)
            except Exception as error:
                report["restore_error"] = _h_utf8(error)
        summary["total_elapsed_seconds"] = round(_h_time.time() - t0, 3)
        report["finished_at_utc"] = _h_utc()
        _h_json_snapshot(cfg["report_path"], report)


_h_run()
'''


def generate_harness_script(target_filter, agent_dir, out_file, **options):
    stamp = datetime.now(timezone.utc)
    run_id = options.get("run_id") or _new_run_id(stamp)
    report_path = Path(out_file).resolve()
    cfg = {
        "run_id": run_id,
        "run_started_at_utc": stamp.isoformat(timespec="seconds"),
        "target": target_filter,
        "agent_dir": str(Path(agent_dir).resolve()),
        "host": "127.0.0.1",
        "port": 50051,
        "keep_source_visible": False,
        "run_dir": str(report_path.parent / (report_path.stem + "-" + run_id)),
        "report_path": str(report_path),
        "jsonl_path": str(report_path.with_suffix(".jsonl")),
        "csv_path": str(report_path.with_suffix(".csv")),
    }
    cfg.update(options)
    return _EMBEDDED.replace("__HARNESS_CONFIG__", repr(json.dumps(cfg, ensure_ascii=True)), 1)


def _new_run_id(stamp):
    return stamp.strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:12]


def main():
    parser = argparse.ArgumentParser(description="Headless Midsurface Batch Test Harness")
    parser.add_argument("--target", default="", help="Substring to filter target body names (empty for all)")
    parser.add_argument("--agent-dir", default=_DEFAULT_AGENT_DIR, help="Path to SC_midsurface_Agent modules")
    parser.add_argument("--host", default="127.0.0.1", help="SpaceClaim gRPC host")
    parser.add_argument("--port", type=int, default=50051, help="SpaceClaim gRPC port")
    parser.add_argument("--output", required=True, help="Run directory or legacy output JSON report path")
    parser.add_argument("--keep-source-visible", action="store_true", help="Leave successful source bodies visible")
    args = parser.parse_args()

    try:
        from ansys.geometry.core import Modeler
    except ImportError:
        print("Error: ansys-geometry-core required", file=sys.stderr)
        return 1

    out = Path(args.output).absolute()
    legacy = out.suffix.lower() == ".json" and not out.is_dir()
    run_id = _new_run_id(datetime.now(timezone.utc))
    run_dir = out.parent / (out.stem + "-" + run_id) if legacy else out
    report_path = run_dir / ("report.json" if not legacy else out.name)
    temp_script = run_dir / "_tmp_harness.py"
    modeler = None
    script_created = False
    try:
        if legacy and (out.exists() or out.is_symlink()):
            raise FileExistsError("Output JSON already exists: %s" % out)
        if run_dir.exists() and (not run_dir.is_dir() or any(run_dir.iterdir())):
            raise ValueError("Output run directory must be empty: %s" % run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
        script = generate_harness_script(
            args.target, args.agent_dir, report_path, run_dir=str(run_dir), run_id=run_id,
            host=args.host, port=args.port, keep_source_visible=args.keep_source_visible,
        )
        with temp_script.open("x", encoding="ascii") as stream:
            script_created = True
            stream.write(script)
        modeler = Modeler(host=args.host, port=args.port, transport_mode="insecure")
        modeler.run_script_file(str(temp_script), import_design=False)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("run_id") != run_id or report.get("run_status") != "COMPLETED":
            raise RuntimeError(report.get("error") or "Harness did not finish the expected run")
        if legacy:
            with out.open("xb") as stream:
                stream.write(report_path.read_bytes())
        print("Batch report: %s" % report_path)
        return 0
    except Exception as error:
        print("Harness execution failed: %s; run directory: %s" % (error, run_dir), file=sys.stderr)
        return 1
    finally:
        if modeler is not None and hasattr(modeler, "close"):
            try:
                modeler.close(close_design=False)
            except Exception:
                pass
        if script_created:
            temp_script.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
