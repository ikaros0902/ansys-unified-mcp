"""Ansys Workbench unified tools.
Consolidates file-IPC bridge, PyWorkbench, and batch launcher tools.
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

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope, aliased_tool
from ansys_unified_mcp.products.workbench import controller
from ansys_unified_mcp.bridges.workbench_batch import (
    detect_workbench_environment,
    get_workbench_job_status,
    launch_mechanical_script,
    launch_workbench_journal,
    list_workbench_jobs,
    read_workbench_job_log,
)
from ansys_unified_mcp.bridges.workbench_filequeue import (
    SERVER_ROOT, MCP_HOME, COMMANDS_DIR, RESULTS_DIR, RUNS_DIR, LOGS_DIR, WORKBENCH_QUEUE_DIR, STATUS_FILE, STOP_FILE, LOG_FILE, BRIDGE_JOURNAL,
    RUNWB2, MECHANICAL, MAPDL, FLUENT, CFX_SOLVE, CFX_PRE,
    WORKBENCH_ANALYSIS_TEMPLATES, WORKBENCH_DEFAULT_PROJECT_NAMES,
    _split_extra_args, _analysis_key, _analysis_candidates, _default_project_name,
    _read_json, _read_json_retry, _get_active_project_path, _write_json, _ensure_dirs,
    _as_path, _json, _run_process, _workbench_command, _read_status,
    _format_bridge_result, _wait_for_log_marker, __version__
)
from ansys_unified_mcp.bridges.transport import send_command as _send_command

@mcp.resource("ansys-workbench://status")
def workbench_status_resource() -> str:
    """Current Ansys Workbench bridge status."""
    import json
    status = _read_status()
    if not status:
        return json.dumps({"connected": False, "detail": "status.json not found", "mcp_home": str(MCP_HOME)}, indent=2, ensure_ascii=False)
    return json.dumps(status, indent=2, ensure_ascii=False)


@mcp.resource("ansys-workbench://installation")
def installation_resource() -> str:
    """Configured Ansys executable paths for this MCP server."""
    import json
    result = check_ansys_installation()
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool()
def check_ansys_installation() -> dict:
    """Check configured Workbench, Mechanical, MAPDL, and bridge paths."""
    data = {
        "version": __version__,
        "runwb2": str(RUNWB2),
        "runwb2_exists": RUNWB2.exists(),
        "mechanical": str(MECHANICAL),
        "mechanical_exists": MECHANICAL.exists(),
        "mapdl": str(MAPDL),
        "mapdl_exists": MAPDL.exists(),
        "fluent": str(FLUENT),
        "fluent_exists": FLUENT.exists(),
        "cfx_solve": str(CFX_SOLVE),
        "cfx_solve_exists": CFX_SOLVE.exists(),
        "cfx_pre": str(CFX_PRE),
        "cfx_pre_exists": CFX_PRE.exists(),
        "bridge_journal": str(BRIDGE_JOURNAL),
        "bridge_journal_exists": BRIDGE_JOURNAL.exists(),
        "mcp_home": str(MCP_HOME),
        "server_root": str(SERVER_ROOT),
    }
    return _envelope(data)


@mcp.tool()
def start_workbench_bridge(batch: bool = True, wait_seconds: int = 20) -> dict:
    """Launch Workbench with the file-IPC bridge journal loaded.

    The bridge journal keeps Workbench alive and polls commands/*.json.
    Use stop_workbench_bridge to stop it.
    """
    if not RUNWB2.exists():
        return _envelope({"ok": False, "error": f"RunWB2 not found: {RUNWB2}"})
    if not BRIDGE_JOURNAL.exists():
        return _envelope({"ok": False, "error": f"Bridge journal not found: {BRIDGE_JOURNAL}"})

    status = _read_status()
    if status.get("status") == "running":
        ping_result = _send_command("ping", timeout=5.0)
        if ping_result.get("success"):
            return _envelope({"ok": True, "already_running": True, "status": status, "ping": ping_result})

    _ensure_dirs()
    try:
        if STOP_FILE.exists():
            STOP_FILE.unlink()
    except Exception:
        pass

    env = os.environ.copy()
    env["ANSYS_WORKBENCH_MCP_HOME"] = str(MCP_HOME)
    # This is the MCP-launched DEDICATED bridge instance: opt in to the blocking
    # polling loop so it stays alive. Interactive Workbench sessions that load the
    # journal without this flag will NOT loop, keeping their console responsive.
    env["ANSYS_MCP_AUTO_LOOP"] = "1"
    proc = subprocess.Popen(
        _workbench_command(BRIDGE_JOURNAL, batch=batch),
        cwd=str(SERVER_ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    deadline = time.time() + max(1, int(wait_seconds))
    ping_result: dict[str, Any] = {}
    while time.time() < deadline:
        status = _read_status()
        if status.get("status") == "running":
            ping_result = _send_command("ping", timeout=5.0)
            if ping_result.get("success"):
                return _envelope({"ok": True, "pid": proc.pid, "status": status, "ping": ping_result})
        time.sleep(0.5)

    return _envelope({"ok": False, "pid": proc.pid, "status": _read_status(), "detail": "Bridge did not answer before timeout"})


@mcp.tool()
def stop_workbench_bridge(timeout_seconds: int = 10) -> dict:
    """Signal the Workbench bridge loop to stop."""
    result = _send_command("stop", timeout=min(float(timeout_seconds), 5.0))
    if not result.get("success"):
        try:
            STOP_FILE.write_text("stop", encoding="utf-8")
        except Exception:
            pass

    deadline = time.time() + max(1, int(timeout_seconds))
    while time.time() < deadline:
        status = _read_status()
        if status.get("status") in {"stopped", "ready"}:
            return _envelope({"ok": True, "status": status, "command_result": result})
        time.sleep(0.25)

    return _envelope({"ok": False, "status": _read_status(), "command_result": result})


@mcp.tool()
def check_workbench_connection() -> dict:
    """Check whether the Workbench bridge journal is running and responding."""
    status = _read_status()
    if not status:
        return "Workbench bridge status not found. Run start_workbench_bridge() or load ansys_workbench_bridge.wbjn in Workbench."

    if status.get("status") != "running":
        return f"Workbench bridge is not running: {_json(status)}"

    result = _send_command("ping", timeout=10.0)
    if result.get("success"):
        data = result.get("data", {})
        version = data.get("version", "?") if isinstance(data, dict) else "?"
        return f"Connected to Ansys Workbench bridge v{version}.\nStatus: {_json(status)}"
    return f"Workbench bridge status exists but ping failed: {_json(result)}"


@mcp.tool()
def execute_workbench_script(script: str, timeout_seconds: int = 60) -> dict:
    """Execute Python/Workbench journal code inside the running Workbench bridge."""
    result = _send_command("execute_script", timeout=float(timeout_seconds), script=script)
    return _envelope(_format_bridge_result(result))


@mcp.tool()
def execute_spaceclaim_script_live(script: str, system_name: str = "", timeout_seconds: int = 120) -> dict:
    """透過已啟動的 Workbench 橋接器，向活躍的 SpaceClaim 視窗發送並執行 SpaceClaim Python 腳本。

    :param script: 要執行的 SpaceClaim Python 腳本內容
    :param system_name: 指定的系統名稱（例如 'SYS'），留空則自動尋找第一個含幾何設計的系統
    """
    wb_script = f"""# encoding: utf-8
import traceback

def run():
    target_system = None
    system_name = {system_name!r}
    
    if system_name:
        for s in GetAllSystems():
            if s.Name == system_name:
                target_system = s
                break
    else:
        for s in GetAllSystems():
            if s.GetContainer(ComponentName="Geometry"):
                target_system = s
                break
                
    if not target_system:
        raise RuntimeError("在專案中找不到具有幾何組件的系統")
        
    geometry = target_system.GetContainer(ComponentName="Geometry")
    geometry.Edit(IsSpaceClaimGeometry=True, Interactive=True)
    geometry.SendCommand(Language="Python", Command={script!r})

try:
    run()
    print("SUCCESS")
except Exception as e:
    print("ERROR: " + str(e))
    print(traceback.format_exc())
"""
    result = _send_command("execute_script", timeout=float(timeout_seconds), script=wb_script)
    return _envelope(_format_bridge_result(result))


@mcp.tool()
def execute_mechanical_script_live(script: str, system_name: str = "", timeout_seconds: int = 120) -> dict:
    """透過已啟動的 Workbench 橋接器，向活躍的 Mechanical 視窗發送並執行 ACT Python 腳本。

    利用暫存檔擷取輸出結果並回傳，提供如同 gRPC 般的完整雙向溝通能力，但完全避開授權連線阻擋。
    :param script: 要執行的 Mechanical ACT Python 腳本內容
    :param system_name: 指定的系統名稱（例如 'SYS'），留空則自動尋找第一個含模型 (Model) 組件的系統
    """
    wb_script = f"""# encoding: utf-8
import traceback
import os
import time

def run():
    target_system = None
    system_name = {system_name!r}
    
    if system_name:
        for s in GetAllSystems():
            if s.Name == system_name:
                target_system = s
                break
    else:
        for s in GetAllSystems():
            if s.GetContainer(ComponentName="Model"):
                target_system = s
                break
                
    if not target_system:
        raise RuntimeError("在專案中找不到具有 Model 組件的系統")
        
    model = target_system.GetContainer(ComponentName="Model")
    model.Edit(Interactive=True)
    
    # 建立輸出結果的暫存路徑
    temp_file = os.path.abspath("mech_out_" + str(time.time()).replace(".", "") + ".txt").replace("\\\\", "/")
    
    # 封裝使用者的程式碼，將輸出寫入暫存檔
    user_script = {script!r}
    wrapped_script = \"\"\"
import sys
import traceback
import io

class OutputCapture:
    def __init__(self):
        self.output = []
    def write(self, s):
        self.output.append(s)
    def flush(self):
        pass

capture = OutputCapture()
original_stdout = sys.stdout
sys.stdout = capture

try:
    exec(user_script)
except Exception as e:
    capture.write("ERROR: " + str(e) + "\\n")
    capture.write(traceback.format_exc())
finally:
    sys.stdout = original_stdout
    with open(r'\"\"\" + temp_file + \"\"\"', 'w') as f:
        f.write("".join(capture.output))
\"\"\"
    
    # 替換 user_script 以正確載入 (IronPython字串處理)
    wrapped_script = wrapped_script.replace("user_script", "'''\\n" + user_script.replace("'''", "\\'\\'\\'") + "\\n'''")
    
    model.SendCommand(Language="Python", Command=wrapped_script)
    
    # 輪詢等待輸出結果
    for _ in range({timeout_seconds} * 2):
        if os.path.exists(temp_file):
            with open(temp_file, 'r') as f:
                print("---MECHANICAL OUTPUT---")
                print(f.read().strip())
                print("-----------------------")
            try:
                os.remove(temp_file)
            except:
                pass
            return
        time.sleep(0.5)
        
    raise RuntimeError("Timed out waiting for Mechanical output in " + str({timeout_seconds}) + " seconds.")

try:
    run()
    print("SUCCESS")
except Exception as e:
    print("ERROR: " + str(e))
    print(traceback.format_exc())
"""
    result = _send_command("execute_script", timeout=float(timeout_seconds), script=wb_script)
    return _envelope(_format_bridge_result(result))



@mcp.tool()
def get_project_info(timeout_seconds: int = 30) -> dict:
    """Get project/system/component information from the running Workbench bridge."""
    result = _send_command("get_project_info", timeout=float(timeout_seconds))
    return _envelope(_format_bridge_result(result))


@mcp.tool()
def open_project(project_file: str, timeout_seconds: int = 120) -> dict:
    """Open a Workbench project in the running Workbench bridge."""
    result = _send_command("open_project", timeout=float(timeout_seconds), project_file=project_file)
    return _envelope(_format_bridge_result(result))


@mcp.tool()
def save_project(project_file: str = "", overwrite: bool = True, timeout_seconds: int = 120) -> dict:
    """Save the current Workbench project through the running bridge."""
    result = _send_command(
        "save_project",
        timeout=float(timeout_seconds),
        project_file=project_file,
        overwrite=overwrite,
    )
    return _envelope(_format_bridge_result(result))


@mcp.tool()
def update_project(timeout_seconds: int = 600) -> dict:
    """Run Workbench Update() in the running bridge."""
    result = _send_command("update_project", timeout=float(timeout_seconds))
    return _envelope(_format_bridge_result(result))


@mcp.tool()
def probe_workbench_analysis_templates_live(timeout_seconds: int = 60) -> dict:
    """Check Workbench template availability for the supported analysis wrappers."""
    result = _send_command(
        "probe_analysis_templates",
        timeout=float(timeout_seconds),
        analysis_templates=WORKBENCH_ANALYSIS_TEMPLATES,
    )
    return _envelope(_format_bridge_result(result))


@mcp.tool()
def create_workbench_analysis_system_live(
    analysis_type: str,
    project_dir: str,
    project_name: str = "",
    geometry_file: str = "",
    refresh_model: bool = False,
    reset_project: bool = True,
    template_name: str = "",
    solver: str = "",
    timeout_seconds: int = 180,
) -> dict:
    """Create a Workbench analysis system in the running bridge.

    Supported analysis_type values include steady_state_thermal,
    transient_thermal, static_structural, transient_structural, modal,
    harmonic_response, response_spectrum, random_vibration, cfx, and fluent.
    template_name/solver can override the built-in mapping.
    """
    try:
        candidates = _analysis_candidates(analysis_type, template_name, solver)
    except ValueError as exc:
        return _envelope({"ok": False, "error": str(exc)})
    result = _send_command(
        "create_analysis_system",
        timeout=float(timeout_seconds),
        analysis_type=_analysis_key(analysis_type),
        project_dir=project_dir,
        project_name=project_name or _default_project_name(analysis_type),
        geometry_file=geometry_file,
        refresh_model=refresh_model,
        reset_project=reset_project,
        template_candidates=candidates,
    )
    return _envelope(_format_bridge_result(result))


@mcp.tool()
def create_steady_state_thermal_system_live(
    project_dir: str,
    project_name: str = "steady_state_thermal",
    geometry_file: str = "",
    refresh_model: bool = False,
    timeout_seconds: int = 180,
) -> dict:
    """Create a Steady-State Thermal system in the running Workbench bridge."""
    result = _send_command(
        "create_steady_state_thermal_system",
        timeout=float(timeout_seconds),
        project_dir=project_dir,
        project_name=project_name,
        geometry_file=geometry_file,
        refresh_model=refresh_model,
    )
    return _envelope(_format_bridge_result(result))


@mcp.tool()
def create_transient_thermal_system_live(
    project_dir: str,
    project_name: str = "transient_thermal",
    geometry_file: str = "",
    refresh_model: bool = False,
    timeout_seconds: int = 180,
) -> dict:
    """Create a Transient Thermal system in the running Workbench bridge."""
    return create_workbench_analysis_system_live(
        "transient_thermal",
        project_dir,
        project_name,
        geometry_file,
        refresh_model,
        True,
        timeout_seconds=timeout_seconds,
    )


@mcp.tool()
def create_static_structural_system_live(
    project_dir: str,
    project_name: str = "static_structural",
    geometry_file: str = "",
    refresh_model: bool = False,
    timeout_seconds: int = 180,
) -> dict:
    """Create a Static Structural system in the running Workbench bridge."""
    return create_workbench_analysis_system_live(
        "static_structural",
        project_dir,
        project_name,
        geometry_file,
        refresh_model,
        True,
        timeout_seconds=timeout_seconds,
    )


@mcp.tool()
def create_transient_structural_system_live(
    project_dir: str,
    project_name: str = "transient_structural",
    geometry_file: str = "",
    refresh_model: bool = False,
    timeout_seconds: int = 180,
) -> dict:
    """Create a Transient Structural dynamics system in the running Workbench bridge."""
    return create_workbench_analysis_system_live(
        "transient_structural",
        project_dir,
        project_name,
        geometry_file,
        refresh_model,
        True,
        timeout_seconds=timeout_seconds,
    )


@mcp.tool()
def create_modal_analysis_system_live(
    project_dir: str,
    project_name: str = "modal_analysis",
    geometry_file: str = "",
    refresh_model: bool = False,
    timeout_seconds: int = 180,
) -> dict:
    """Create a Modal dynamics system in the running Workbench bridge."""
    return create_workbench_analysis_system_live(
        "modal",
        project_dir,
        project_name,
        geometry_file,
        refresh_model,
        True,
        timeout_seconds=timeout_seconds,
    )


@mcp.tool()
def create_harmonic_response_system_live(
    project_dir: str,
    project_name: str = "harmonic_response",
    geometry_file: str = "",
    refresh_model: bool = False,
    timeout_seconds: int = 180,
) -> dict:
    """Create a Harmonic Response dynamics system in the running Workbench bridge."""
    return create_workbench_analysis_system_live(
        "harmonic_response",
        project_dir,
        project_name,
        geometry_file,
        refresh_model,
        True,
        timeout_seconds=timeout_seconds,
    )


@mcp.tool()
def create_response_spectrum_system_live(
    project_dir: str,
    project_name: str = "response_spectrum",
    geometry_file: str = "",
    refresh_model: bool = False,
    timeout_seconds: int = 180,
) -> dict:
    """Create a Response Spectrum dynamics system in the running Workbench bridge."""
    return create_workbench_analysis_system_live(
        "response_spectrum",
        project_dir,
        project_name,
        geometry_file,
        refresh_model,
        True,
        timeout_seconds=timeout_seconds,
    )


@mcp.tool()
def create_random_vibration_system_live(
    project_dir: str,
    project_name: str = "random_vibration",
    geometry_file: str = "",
    refresh_model: bool = False,
    timeout_seconds: int = 180,
) -> dict:
    """Create a Random Vibration dynamics system in the running Workbench bridge."""
    return create_workbench_analysis_system_live(
        "random_vibration",
        project_dir,
        project_name,
        geometry_file,
        refresh_model,
        True,
        timeout_seconds=timeout_seconds,
    )


@mcp.tool()
def create_cfx_flow_system_live(
    project_dir: str,
    project_name: str = "cfx_flow",
    geometry_file: str = "",
    refresh_model: bool = False,
    timeout_seconds: int = 180,
) -> dict:
    """Create a Fluid Flow (CFX) system in the running Workbench bridge."""
    return create_workbench_analysis_system_live(
        "cfx",
        project_dir,
        project_name,
        geometry_file,
        refresh_model,
        True,
        timeout_seconds=timeout_seconds,
    )


@mcp.tool()
def create_fluent_flow_system_live(
    project_dir: str,
    project_name: str = "fluent_flow",
    geometry_file: str = "",
    refresh_model: bool = False,
    timeout_seconds: int = 180,
) -> dict:
    """Try to create a Fluid Flow (Fluent) system in the running Workbench bridge."""
    return create_workbench_analysis_system_live(
        "fluent",
        project_dir,
        project_name,
        geometry_file,
        refresh_model,
        True,
        timeout_seconds=timeout_seconds,
    )


@mcp.tool()
def create_thermal_bar_demo_live(
    project_dir: str = r"D:\ansys-workbench-mcp\runs\thermal_bar_demo_live",
    timeout_seconds: int = 600,
) -> dict:
    """Create and solve a simple thermal bar demo through the running Workbench bridge."""
    result = _send_command("create_thermal_bar_demo", timeout=float(timeout_seconds), project_dir=project_dir)
    return _envelope(_format_bridge_result(result))


@mcp.tool()
def run_workbench_journal(
    journal_path: str,
    workdir: str = "",
    batch: bool = True,
    timeout_seconds: int = 600,
) -> dict:
    """Run an Ansys Workbench journal through RunWB2 as a direct batch job."""
    if not RUNWB2.exists():
        return _envelope({"ok": False, "error": f"RunWB2 not found: {RUNWB2}"})

    journal = _as_path(journal_path)
    if not journal.exists():
        return _envelope({"ok": False, "error": f"Journal not found: {journal}"})

    cwd = _as_path(workdir) if workdir else journal.parent
    cwd.mkdir(parents=True, exist_ok=True)

    try:
        result = _run_process(_workbench_command(journal, batch=batch), cwd, timeout_seconds)
        return _envelope({"ok": result["returncode"] == 0, "journal": str(journal), **result})
    except subprocess.TimeoutExpired:
        return _envelope({"ok": False, "error": f"Timed out after {timeout_seconds}s", "journal": str(journal)})


@mcp.tool()
def create_workbench_analysis_system(
    analysis_type: str,
    project_dir: str,
    project_name: str = "",
    geometry_file: str = "",
    refresh_model: bool = False,
    template_name: str = "",
    solver: str = "",
    timeout_seconds: int = 600,
) -> dict:
    """Create a Workbench analysis system through a direct batch journal.

    This one-shot tool does not require the bridge to be running.
    """
    if not RUNWB2.exists():
        return _envelope({"ok": False, "error": f"RunWB2 not found: {RUNWB2}"})

    try:
        candidates = _analysis_candidates(analysis_type, template_name, solver)
    except ValueError as exc:
        return _envelope({"ok": False, "error": str(exc)})

    if geometry_file:
        geom = _as_path(geometry_file)
        if not geom.exists():
            return _envelope({"ok": False, "error": f"Geometry file not found: {geom}"})
        geometry_file = str(geom)

    analysis_key = _analysis_key(analysis_type)
    final_project_name = project_name or _default_project_name(analysis_key)
    out_dir = _as_path(project_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    project_file = out_dir / f"{final_project_name}.wbpj"
    journal_file = out_dir / f"{final_project_name}_create_{analysis_key}.wbjn"
    log_file = out_dir / f"{final_project_name}_create_{analysis_key}.log"
    marker = "ANSYS_WORKBENCH_MCP_DONE"

    geometry_literal = repr(geometry_file)
    model_fallback_line = "        model = None\n"
    refresh_line = "        model.Refresh()\n" if refresh_model else ""
    journal = f"""# encoding: utf-8
import traceback

log = open({str(log_file)!r}, "w")

def w(message):
    log.write(str(message) + "\\n")
    log.flush()

def resolve_template(candidates):
    errors = []
    for candidate in candidates:
        name = candidate.get("template_name", "")
        solver = candidate.get("solver", "")
        try:
            if solver:
                return GetTemplate(TemplateName=name, Solver=solver), name, solver
            return GetTemplate(TemplateName=name), name, solver
        except Exception as e:
            errors.append(name + "|" + solver + "|" + str(e))
    raise RuntimeError("No matching Workbench template. Tried: " + "; ".join(errors))

try:
    Reset()
    ClearMessages()
    template, used_name, used_solver = resolve_template({json.dumps(candidates, ensure_ascii=False)})
    system = template.CreateSystem()
    if {bool(geometry_file)!r}:
        geometry = system.GetContainer(ComponentName="Geometry")
        geometry.SetFile(FilePath={geometry_literal})
    try:
        model = system.GetContainer(ComponentName="Model")
{refresh_line if refresh_model else model_fallback_line}    except Exception:
        model = None
    Save(FilePath={str(project_file)!r}, Overwrite=True)
    w("Analysis type: " + {analysis_key!r})
    w("Template: " + used_name + " (" + used_solver + ")")
    w("Project saved: " + {str(project_file)!r})
    for message in GetMessages():
        try:
            w("%s: %s" % (message.MessageType, message.Summary))
        except:
            w(str(message))
    w("{marker}")
except Exception:
    w("ERROR")
    w(traceback.format_exc())
    raise
finally:
    log.close()
"""
    journal_file.write_text(journal, encoding="utf-8")

    try:
        process_result = _run_process(_workbench_command(journal_file, batch=True), out_dir, timeout_seconds)
    except subprocess.TimeoutExpired:
        return _envelope({"ok": False, "error": f"Timed out after {timeout_seconds}s", "journal": str(journal_file)})

    marker_seen = _wait_for_log_marker(log_file, marker, min(timeout_seconds, 120))
    log_text = log_file.read_text(encoding="utf-8", errors="replace") if log_file.exists() else ""
    ok = project_file.exists() and marker_seen and "ERROR" not in log_text
    return _envelope(
        {
            "ok": ok,
            "analysis_type": analysis_key,
            "project_file": str(project_file),
            "journal_file": str(journal_file),
            "log_file": str(log_file),
            "marker_seen": marker_seen,
            "process": process_result,
            "log_tail": log_text[-8000:],
        }
    )


@mcp.tool()
def create_steady_state_thermal_system(
    project_dir: str,
    project_name: str = "steady_state_thermal",
    geometry_file: str = "",
    refresh_model: bool = False,
    timeout_seconds: int = 600,
) -> dict:
    """Create a Workbench Steady-State Thermal system using a direct batch journal.

    This one-shot tool does not require the bridge to be running.
    """
    if not RUNWB2.exists():
        return _envelope({"ok": False, "error": f"RunWB2 not found: {RUNWB2}"})

    out_dir = _as_path(project_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    project_file = out_dir / f"{project_name}.wbpj"
    journal_file = out_dir / f"{project_name}_create_steady_thermal.wbjn"
    log_file = out_dir / f"{project_name}_create_steady_thermal.log"

    geom_line = ""
    if geometry_file:
        geom = _as_path(geometry_file)
        if not geom.exists():
            return _envelope({"ok": False, "error": f"Geometry file not found: {geom}"})
        geom_line = (
            "geometry = system.GetContainer(ComponentName='Geometry')\n"
            f"geometry.SetFile(FilePath={str(geom)!r})\n"
        )

    refresh_line = "model.Refresh()\n" if refresh_model else ""
    marker = "ANSYS_WORKBENCH_MCP_DONE"
    journal = f"""# encoding: utf-8
import traceback

log = open({str(log_file)!r}, "w")

def w(message):
    log.write(str(message) + "\\n")
    log.flush()

try:
    Reset()
    ClearMessages()
    template = GetTemplate(TemplateName="Steady-State Thermal", Solver="ANSYS")
    system = template.CreateSystem()
{geom_line}    model = system.GetContainer(ComponentName="Model")
{refresh_line}    Save(FilePath={str(project_file)!r}, Overwrite=True)
    w("Project saved: " + {str(project_file)!r})
    for message in GetMessages():
        try:
            w("%s: %s" % (message.MessageType, message.Summary))
        except:
            w(str(message))
    w("{marker}")
except Exception:
    w("ERROR")
    w(traceback.format_exc())
    raise
finally:
    log.close()
"""
    journal_file.write_text(journal, encoding="utf-8")

    try:
        process_result = _run_process(_workbench_command(journal_file, batch=True), out_dir, timeout_seconds)
    except subprocess.TimeoutExpired:
        return _envelope({"ok": False, "error": f"Timed out after {timeout_seconds}s", "journal": str(journal_file)})

    marker_seen = _wait_for_log_marker(log_file, marker, min(timeout_seconds, 120))
    log_text = log_file.read_text(encoding="utf-8", errors="replace") if log_file.exists() else ""
    ok = project_file.exists() and marker_seen and "ERROR" not in log_text
    return _envelope(
        {
            "ok": ok,
            "project_file": str(project_file),
            "journal_file": str(journal_file),
            "log_file": str(log_file),
            "marker_seen": marker_seen,
            "process": process_result,
            "log_tail": log_text[-8000:],
        }
    )


@mcp.tool()
def run_mapdl_input(
    input_file: str,
    workdir: str = "",
    job_name: str = "ansys_mcp_job",
    timeout_seconds: int = 600,
) -> dict:
    """Run a Mechanical APDL input file with MAPDL."""
    if not MAPDL.exists():
        return _envelope({"ok": False, "error": f"MAPDL not found: {MAPDL}"})

    inp = _as_path(input_file)
    if not inp.exists():
        return _envelope({"ok": False, "error": f"Input file not found: {inp}"})

    cwd = _as_path(workdir) if workdir else inp.parent
    cwd.mkdir(parents=True, exist_ok=True)
    out_file = cwd / f"{job_name}.out"
    args = [str(MAPDL), "-b", "-i", str(inp), "-o", str(out_file), "-j", job_name]

    try:
        result = _run_process(args, cwd, timeout_seconds)
    except subprocess.TimeoutExpired:
        return _envelope({"ok": False, "error": f"Timed out after {timeout_seconds}s", "input_file": str(inp)})

    out_tail = out_file.read_text(encoding="utf-8", errors="replace")[-12000:] if out_file.exists() else ""
    return _envelope(
        {
            "ok": result["returncode"] == 0,
            "input_file": str(inp),
            "out_file": str(out_file),
            "process": result,
            "out_tail": out_tail,
        }
    )


@mcp.tool()
def run_fluent_journal(
    journal_path: str,
    workdir: str = "",
    dimension: str = "3d",
    precision: str = "double",
    processors: int = 1,
    gui: bool = False,
    extra_args: str = "",
    timeout_seconds: int = 3600,
) -> dict:
    """Run an Ansys Fluent journal directly with fluent.exe.

    dimension is 2d or 3d. precision is single or double.
    extra_args is appended to the Fluent command line for advanced cases.
    """
    if not FLUENT.exists():
        return _envelope({"ok": False, "error": f"Fluent not found: {FLUENT}"})

    journal = _as_path(journal_path)
    if not journal.exists():
        return _envelope({"ok": False, "error": f"Journal not found: {journal}"})

    cwd = _as_path(workdir) if workdir else journal.parent
    cwd.mkdir(parents=True, exist_ok=True)

    dim = dimension.strip().lower()
    if dim not in {"2d", "3d"}:
        return _envelope({"ok": False, "error": "dimension must be 2d or 3d"})
    prec = precision.strip().lower()
    if prec in {"double", "dp"}:
        fluent_mode = dim + "dp"
    elif prec in {"single", "sp"}:
        fluent_mode = dim
    else:
        return _envelope({"ok": False, "error": "precision must be single or double"})

    args = [str(FLUENT), fluent_mode]
    if int(processors) > 1:
        args.append(f"-t{int(processors)}")
    if not gui:
        args.append("-g")
    args.extend(["-i", str(journal)])
    args.extend(_split_extra_args(extra_args))

    try:
        result = _run_process(args, cwd, timeout_seconds)
    except subprocess.TimeoutExpired:
        return _envelope({"ok": False, "error": f"Timed out after {timeout_seconds}s", "journal": str(journal)})

    return _envelope(
        {
            "ok": result["returncode"] == 0,
            "journal": str(journal),
            "workdir": str(cwd),
            "command": args,
            "process": result,
        }
    )


@mcp.tool()
def run_cfx_solver(
    definition_file: str,
    workdir: str = "",
    run_name: str = "",
    processors: int = 1,
    double_precision: bool = False,
    extra_args: str = "",
    timeout_seconds: int = 3600,
) -> dict:
    """Run an Ansys CFX solver input file directly with cfx5solve.exe."""
    if not CFX_SOLVE.exists():
        return _envelope({"ok": False, "error": f"CFX solver not found: {CFX_SOLVE}"})

    definition = _as_path(definition_file)
    if not definition.exists():
        return _envelope({"ok": False, "error": f"Definition file not found: {definition}"})

    cwd = _as_path(workdir) if workdir else definition.parent
    cwd.mkdir(parents=True, exist_ok=True)

    args = [str(CFX_SOLVE), "-batch", "-def", str(definition), "-chdir", str(cwd)]
    if run_name:
        args.extend(["-name", run_name])
    if double_precision:
        args.append("-double")
    if int(processors) > 1:
        args.extend(["-par-local", "-partition", str(int(processors))])
    args.extend(_split_extra_args(extra_args))

    try:
        result = _run_process(args, cwd, timeout_seconds)
    except subprocess.TimeoutExpired:
        return _envelope({"ok": False, "error": f"Timed out after {timeout_seconds}s", "definition_file": str(definition)})

    return _envelope(
        {
            "ok": result["returncode"] == 0,
            "definition_file": str(definition),
            "workdir": str(cwd),
            "command": args,
            "process": result,
        }
    )


@mcp.tool()
def create_and_run_thermal_bar_demo(
    project_dir: str = r"D:\ansys-workbench-mcp\runs\thermal_bar_demo",
    timeout_seconds: int = 600,
) -> dict:
    """Create and solve a small steady thermal bar demo through direct Workbench batch."""
    out_dir = _as_path(project_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    inp = out_dir / "thermal_bar.dat"
    result_txt = out_dir / "thermal_nodal_temperatures.txt"
    wbjn = out_dir / "run_thermal_bar.wbjn"
    wbpj = out_dir / "thermal_bar_demo.wbpj"
    log_file = out_dir / "workbench_run.log"
    marker = "ANSYS_WORKBENCH_MCP_DONE"

    apdl = f"""/TITLE,Workbench MCP thermal bar demo
/PREP7
ET,1,SOLID70
MP,KXX,1,45
BLOCK,0,0.1,0,0.02,0,0.02
ESIZE,0.005
VMESH,ALL
FINISH

/SOLU
ANTYPE,STATIC
NSEL,S,LOC,X,0
D,ALL,TEMP,100
NSEL,S,LOC,X,0.1
D,ALL,TEMP,20
ALLSEL,ALL
SOLVE
FINISH

/POST1
SET,LAST
ALLSEL,ALL
/OUTPUT,{str(result_txt.with_suffix('')).replace(chr(92), '/')!r},txt
PRNSOL,TEMP
/OUTPUT
FINISH
"""
    inp.write_text(apdl, encoding="utf-8")

    journal = f"""# encoding: utf-8
import traceback

log = open({str(log_file)!r}, "w")

def w(message):
    log.write(str(message) + "\\n")
    log.flush()

try:
    Reset()
    ClearMessages()
    template = GetTemplate(TemplateName="Mechanical APDL")
    system = template.CreateSystem()
    setup = system.GetContainer(ComponentName="Setup")
    setup.AddInputFile(FilePath={str(inp)!r})
    Save(FilePath={str(wbpj)!r}, Overwrite=True)
    Update()
    Save(FilePath={str(wbpj)!r}, Overwrite=True)
    w("Project saved: " + {str(wbpj)!r})
    w("{marker}")
except Exception:
    w("ERROR")
    w(traceback.format_exc())
    raise
finally:
    log.close()
"""
    wbjn.write_text(journal, encoding="utf-8")

    try:
        process_result = _run_process(_workbench_command(wbjn, batch=True), out_dir, timeout_seconds)
    except subprocess.TimeoutExpired:
        return _envelope({"ok": False, "error": f"Timed out after {timeout_seconds}s", "journal": str(wbjn)})

    marker_seen = _wait_for_log_marker(log_file, marker, min(timeout_seconds, 180))
    log_text = log_file.read_text(encoding="utf-8", errors="replace") if log_file.exists() else ""
    temp_text = result_txt.read_text(encoding="utf-8", errors="replace") if result_txt.exists() else ""
    temps: list[float] = []
    for line in temp_text.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[0].isdigit():
            try:
                temps.append(float(parts[1]))
            except ValueError:
                pass
    ok = result_txt.exists() and marker_seen and "ERROR" not in log_text
    return _envelope(
        {
            "ok": ok,
            "project_file": str(wbpj),
            "input_file": str(inp),
            "journal_file": str(wbjn),
            "log_file": str(log_file),
            "result_file": str(result_txt),
            "node_count": len(temps),
            "min_temperature": min(temps) if temps else None,
            "max_temperature": max(temps) if temps else None,
            "process": process_result,
            "log_tail": log_text[-8000:],
        }
    )


if __name__ == "__main__":
    _ensure_dirs()
    mcp.run(transport='stdio')

@aliased_tool(name="workbench_detect_environment", alias="workbench_detect_tool")
def workbench_detect_tool() -> dict:
    """Detect RunWB2.exe, PyMechanical CLI, ANSYS_ROOT, and job directories."""
    return detect_workbench_environment()


@aliased_tool(name="workbench_run_journal", alias="workbench_run_journal_tool")
def workbench_run_journal_tool(
    journal_path: str,
    cwd: str | None = None,
    batch: bool = True,
    extra_args: list[str] | None = None,
) -> dict:
    """Launch a Workbench journal asynchronously."""
    return launch_workbench_journal(journal_path=journal_path, cwd=cwd, batch=batch, extra_args=extra_args)


@aliased_tool(name="mechanical_run_batch_script", alias="mechanical_run_script_tool")
def mechanical_run_script_tool(
    script_path: str,
    revision: int = 261,
    graphical: bool = False,
    project_file: str | None = None,
    script_args: str | None = None,
) -> dict:
    """Launch ansys-mechanical.exe for a Mechanical Python script (headless batch)."""
    return launch_mechanical_script(
        script_path=script_path,
        revision=revision,
        graphical=graphical,
        project_file=project_file,
        script_args=script_args,
    )


@aliased_tool(name="workbench_get_job_status", alias="workbench_job_status_tool")
def workbench_job_status_tool(job_id: str) -> dict:
    """Return status for a Workbench or Mechanical job launched by this MCP."""
    return get_workbench_job_status(job_id)


@aliased_tool(name="workbench_get_job_log", alias="workbench_job_log_tool")
def workbench_job_log_tool(job_id: str, stream: str = "stdout", tail_chars: int = 12000) -> dict:
    """Read stdout or stderr for a Workbench or Mechanical job."""
    return read_workbench_job_log(job_id=job_id, stream=stream, tail_chars=tail_chars)


@aliased_tool(name="workbench_list_jobs", alias="workbench_list_jobs_tool")
def workbench_list_jobs_tool(limit: int = 20) -> dict:
    """List recent Workbench or Mechanical jobs."""
    return list_workbench_jobs(limit=limit)


@mcp.tool()
def workbench_launch_server(
    show_gui: bool = True,
    version: Optional[str] = None,
    port: int = -1,
    use_insecure_connection: bool = False,
    host: Optional[str] = None,
    server_workdir: Optional[str] = None,
    client_workdir: Optional[str] = None,
) -> dict:
    """Launch a new Ansys Workbench server and connect a PyWorkbench client.

    Official client/server transport (replaces the hand-rolled batch/bridge for
    orchestration). VERIFIED @2026-10-07 against a live server (v261). Note: cold
    launch can take ~3 minutes.
    """
    return controller.launch(
        show_gui=show_gui,
        version=version,
        port=port,
        use_insecure_connection=use_insecure_connection,
        host=host,
        server_workdir=server_workdir,
        client_workdir=client_workdir,
    )


@mcp.tool()
def workbench_connect_server(
    port: int,
    host: Optional[str] = None,
    client_workdir: Optional[str] = None,
    security: str = "mtls",
) -> dict:
    """Connect to an already-running Workbench server via PyWorkbench."""
    return controller.connect(port=port, host=host, client_workdir=client_workdir, security=security)


@mcp.tool()
def workbench_run_script_live(script: str, key: Optional[str] = None, log_level: str = "error") -> dict:
    """Run a Workbench journal (Python) command string via PyWorkbench.

    The script may set ``wb_script_result`` (a string) to return data. Returns
    the journal result. VERIFIED @2026-10-07 (template probe round-trip).
    """
    out = controller.run_script(script, key=key, log_level=log_level)
    if isinstance(out, str) and out.startswith("Error:"):
        return {"ok": False, "error": out[len("Error:"):].strip()}
    return {"ok": True, "output": out}


@mcp.tool()
def workbench_start_mechanical_server(system_name: str, port: int = 0, key: Optional[str] = None) -> dict:
    """Have Workbench start a Mechanical gRPC server for a system's Model cell.

    Returns the gRPC port PyMechanical can connect to (project-schematic handoff).
    """
    return controller.start_mechanical_server(system_name=system_name, port=port, key=key)


@mcp.tool()
def workbench_upload_file(file_paths: list[str], key: Optional[str] = None) -> dict:
    """Upload local files (e.g. geometry) to the Workbench server workdir."""
    return controller.upload_file(*file_paths, key=key)


@mcp.tool()
def workbench_download_archive(archive_name: str, key: Optional[str] = None) -> dict:
    """Download the current Workbench project as an archive from the server."""
    return controller.download_project_archive(archive_name, key=key)


@mcp.tool()
def workbench_disconnect_server(key: Optional[str] = None) -> dict:
    """Drop the PyWorkbench session from the registry (server left running)."""
    return controller.disconnect(key=key)


@mcp.tool()
def workbench_server_status() -> dict:
    """Report PyWorkbench session status (connected sessions and current key)."""
    return controller.status()

