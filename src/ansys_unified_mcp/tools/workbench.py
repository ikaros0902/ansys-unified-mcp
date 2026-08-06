"""Workbench / Mechanical batch job tools.

Async job launcher for headless one-shot runs (RunWB2 -R journal and
ansys-mechanical.exe -i script), with job status/log tracking. This is the
"batch subprocess" transport (needs no ACT plugin and no pre-running instance).

The file-queue and socket-timer bridges were removed during the architecture
refactor: they required an in-Mechanical plugin, duplicated the gRPC and
Workbench-journal transports, and carried a cross-process env-coupling bug.
Live in-application execution is provided by the Workbench-journal bridge in
tools/workbench_bridge.py (execute_mechanical_script_live / execute_spaceclaim_script_live).
"""

from __future__ import annotations

from ansys_unified_mcp.bridges.workbench_bridge import (
    detect_workbench_environment,
    get_workbench_job_status,
    launch_mechanical_script,
    launch_workbench_journal,
    list_workbench_jobs,
    read_workbench_job_log,
)
from ansys_unified_mcp.shared import mcp


@mcp.tool()
def workbench_detect_tool() -> dict:
    """Detect RunWB2.exe, PyMechanical CLI, ANSYS_ROOT, and job directories."""
    return detect_workbench_environment()


@mcp.tool()
def workbench_run_journal_tool(
    journal_path: str,
    cwd: str | None = None,
    batch: bool = True,
    extra_args: list[str] | None = None,
) -> dict:
    """Launch a Workbench journal asynchronously."""
    return launch_workbench_journal(journal_path=journal_path, cwd=cwd, batch=batch, extra_args=extra_args)


@mcp.tool()
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


@mcp.tool()
def workbench_job_status_tool(job_id: str) -> dict:
    """Return status for a Workbench or Mechanical job launched by this MCP."""
    return get_workbench_job_status(job_id)


@mcp.tool()
def workbench_job_log_tool(job_id: str, stream: str = "stdout", tail_chars: int = 12000) -> dict:
    """Read stdout or stderr for a Workbench or Mechanical job."""
    return read_workbench_job_log(job_id=job_id, stream=stream, tail_chars=tail_chars)


@mcp.tool()
def workbench_list_jobs_tool(limit: int = 20) -> dict:
    """List recent Workbench or Mechanical jobs."""
    return list_workbench_jobs(limit=limit)
