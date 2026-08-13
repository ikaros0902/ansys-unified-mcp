"""Workbench tools via PyWorkbench (ansys-workbench-core).

Official client/server transport for Ansys Workbench, exposed as additive MCP
tools that delegate to ``products/workbench.py`` (WorkbenchController).

These tools are ADDITIVE: the legacy file-IPC bridge tools in
``tools/workbench_bridge.py`` (start_workbench_bridge / execute_workbench_script
/ check_workbench_connection ...) and the batch job launcher in
``tools/workbench.py`` remain untouched as fallback.

STATUS: UNVERIFIED (Phase 1, option B). This path has not been validated against
a live Workbench server. Verify with a connection smoke test before relying on
it in place of the legacy bridge.
"""

from __future__ import annotations

from typing import Optional

from ansys_unified_mcp.products.workbench import controller
from ansys_unified_mcp.shared import mcp


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
    orchestration). UNVERIFIED: not yet validated against a live server.
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
    the journal result. UNVERIFIED path.
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
