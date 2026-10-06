#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP bridge for Ansys Workbench automation.

The server supports two modes:

1. File-IPC bridge mode, similar to Abaqus MCP:
   mcp_server.py writes command JSON files and ansys_workbench_bridge.wbjn
   runs inside Workbench to execute them.
2. Direct batch mode:
   mcp_server.py invokes RunWB2/MAPDL directly for one-shot jobs.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any, Optional

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.config import config

__version__ = "0.2.0"

SERVER_ROOT = Path(__file__).resolve().parent
DEFAULT_MCP_HOME = SERVER_ROOT
MCP_HOME = Path(os.environ.get("ANSYS_WORKBENCH_MCP_HOME", DEFAULT_MCP_HOME)).expanduser().resolve()

COMMANDS_DIR = MCP_HOME / "commands"
RESULTS_DIR = MCP_HOME / "results"
SCRIPTS_DIR = MCP_HOME / "scripts"
RUNS_DIR = MCP_HOME / "runs"
LOGS_DIR = MCP_HOME / ".runtime" / "logs"
WORKBENCH_QUEUE_DIR = MCP_HOME / ".runtime" / "queue"
STATUS_FILE = MCP_HOME / "status.json"
STOP_FILE = MCP_HOME / "stop.flag"
LOG_FILE = MCP_HOME / "mcp.log"
_NEW_BRIDGE = SERVER_ROOT.parent / "products" / "workbench" / "scripts" / "ansys_workbench_bridge.wbjn"
_OLD_BRIDGE = SERVER_ROOT.parent / "scripts" / "ansys_workbench_bridge.wbjn"
BRIDGE_JOURNAL = _NEW_BRIDGE if _NEW_BRIDGE.exists() else _OLD_BRIDGE

DEFAULT_RUNWB2 = str(config.workbench_exe)
DEFAULT_MECHANICAL = str(config.mechanical_exe)
DEFAULT_MAPDL = str(config.mapdl_exe)
DEFAULT_FLUENT = str(config.fluent_exe)
DEFAULT_CFX_SOLVE = str(config.cfx_solve_exe)
DEFAULT_CFX_PRE = str(config.cfx_pre_exe)

RUNWB2 = Path(os.environ.get("ANSYS_RUNWB2", DEFAULT_RUNWB2))
MECHANICAL = Path(os.environ.get("ANSYS_MECHANICAL", DEFAULT_MECHANICAL))
MAPDL = Path(os.environ.get("ANSYS_MAPDL", DEFAULT_MAPDL))
FLUENT = Path(os.environ.get("ANSYS_FLUENT", DEFAULT_FLUENT))
CFX_SOLVE = Path(os.environ.get("ANSYS_CFX_SOLVE", DEFAULT_CFX_SOLVE))
CFX_PRE = Path(os.environ.get("ANSYS_CFX_PRE", DEFAULT_CFX_PRE))

DEFAULT_TIMEOUT = 30.0

WORKBENCH_ANALYSIS_TEMPLATES: dict[str, list[dict[str, str]]] = {
    "steady_state_thermal": [{"template_name": "Steady-State Thermal", "solver": "ANSYS"}],
    "transient_thermal": [{"template_name": "Transient Thermal", "solver": "ANSYS"}],
    "static_structural": [{"template_name": "Static Structural", "solver": "ANSYS"}],
    "transient_structural": [{"template_name": "Transient Structural", "solver": "ANSYS"}],
    "modal": [{"template_name": "Modal", "solver": "ANSYS"}],
    "harmonic_response": [{"template_name": "Harmonic Response", "solver": "ANSYS"}],
    "response_spectrum": [{"template_name": "Response Spectrum", "solver": "ANSYS"}],
    "random_vibration": [{"template_name": "Random Vibration", "solver": "ANSYS"}],
    "cfx": [{"template_name": "Fluid Flow (CFX)", "solver": ""}, {"template_name": "CFX", "solver": ""}],
    "fluent": [{"template_name": "Fluid Flow (Fluent)", "solver": ""}, {"template_name": "Fluent", "solver": ""}],
}

WORKBENCH_DEFAULT_PROJECT_NAMES: dict[str, str] = {
    "steady_state_thermal": "steady_state_thermal",
    "transient_thermal": "transient_thermal",
    "static_structural": "static_structural",
    "transient_structural": "transient_structural",
    "modal": "modal_analysis",
    "harmonic_response": "harmonic_response",
    "response_spectrum": "response_spectrum",
    "random_vibration": "random_vibration",
    "cfx": "cfx_flow",
    "fluent": "fluent_flow",
}


def _split_extra_args(extra_args: str) -> list[str]:
    if not extra_args.strip():
        return []
    return shlex.split(extra_args, posix=False)


def _analysis_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _analysis_candidates(analysis_type: str, template_name: str = "", solver: str = "") -> list[dict[str, str]]:
    if template_name:
        return [{"template_name": template_name, "solver": solver}]
    key = _analysis_key(analysis_type)
    candidates = WORKBENCH_ANALYSIS_TEMPLATES.get(key)
    if not candidates:
        supported = ", ".join(sorted(WORKBENCH_ANALYSIS_TEMPLATES))
        raise ValueError(f"Unsupported analysis_type {analysis_type!r}. Supported values: {supported}")
    return candidates


def _default_project_name(analysis_type: str, fallback: str = "workbench_analysis") -> str:
    return WORKBENCH_DEFAULT_PROJECT_NAMES.get(_analysis_key(analysis_type), fallback)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _read_json_retry(path: Path, retries: int = 5, delay: float = 0.05) -> dict[str, Any]:
    """Read JSON file with retry, to prevent reading half-written IPC files."""
    for _ in range(retries):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            time.sleep(delay)
    return {}


def _get_active_project_path() -> Optional[Path]:
    return None


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def _ensure_dirs() -> None:
    for d in (COMMANDS_DIR, RESULTS_DIR, LOGS_DIR, WORKBENCH_QUEUE_DIR):
        d.mkdir(parents=True, exist_ok=True)


def _as_path(p: str | Path) -> Path:
    return Path(p).resolve() if not isinstance(p, Path) else p


def _json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


def _run_process(args: list[str], cwd: Path, timeout_seconds: int) -> dict[str, Any]:
    started = time.time()
    proc = subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        check=False,
    )
    return {
        "returncode": proc.returncode,
        "elapsed_seconds": round(time.time() - started, 3),
        "stdout": proc.stdout[-12000:],
        "stderr": proc.stderr[-12000:],
    }


def _workbench_command(journal_path: Path, batch: bool) -> list[str]:
    args = [str(RUNWB2)]
    if batch:
        args.append("-B")
    else:
        # "-B" 缺席不會自動變成「顯示 GUI」；RunWB2 在完全沒指定模式時預設
        # 不建立主視窗。必須明確加 "-I"（互動模式）才會真的跳出視窗，
        # 對應官方 PyWorkbench launcher 的 show_gui=True 行為。
        args.append("-I")
    args.extend(["-R", str(journal_path)])
    return args


def _read_status() -> dict[str, Any]:
    return _read_json(STATUS_FILE)


def _send_command(cmd_type: str, timeout: float = DEFAULT_TIMEOUT, **kwargs: Any) -> dict[str, Any]:
    _ensure_dirs()
    cmd_id = uuid.uuid4().hex[:8]
    command = {"id": cmd_id, "type": cmd_type, "timestamp": time.time(), **kwargs}
    cmd_path = COMMANDS_DIR / f"cmd_{cmd_id}.json"
    result_path = RESULTS_DIR / f"{cmd_id}.json"

    _write_json(cmd_path, command)
    deadline = time.time() + float(timeout)
    while time.time() < deadline:
        if result_path.exists():
            result = _read_json_retry(result_path)
            if not result:
                continue
            try:
                result_path.unlink()
            except Exception:
                pass
            return result
        time.sleep(0.05)

    try:
        cmd_path.unlink()
    except Exception:
        pass
    return {"success": False, "error": f"Timeout: no response from Workbench bridge in {timeout}s"}


def _format_bridge_result(result: dict[str, Any]) -> str:
    """將 bridge 回傳的 dict 格式化為字串（本函式回傳 str 供後續再包 _envelope）"""
    if result.get("success"):
        data = result.get("data")
        output = result.get("output", "")
        if data is not None:
            import json
            return json.dumps(data if isinstance(data, dict) else {"data": data, "output": output}, indent=2, ensure_ascii=False)
        return output if output else "(Command executed successfully, no output)"
    error = result.get("error", "Unknown error")
    tb = result.get("traceback", "")
    if error == "Unknown error" and not tb:
        import json
        return f"Error: {error}\nRaw result: {json.dumps(result, indent=2, ensure_ascii=False)}"
    return f"Error: {error}\n{tb}".strip()


def _wait_for_log_marker(log_path: Path, marker: str, timeout_seconds: int) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if log_path.exists():
            try:
                if marker in log_path.read_text(encoding="utf-8", errors="replace"):
                    return True
            except OSError:
                pass
        time.sleep(0.5)
    return False


