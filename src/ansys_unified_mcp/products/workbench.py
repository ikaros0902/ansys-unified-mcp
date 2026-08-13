"""Workbench product facade (PyWorkbench / ansys-workbench-core).

Official client/server transport for Ansys Workbench. Intended to supersede the
hand-rolled file-IPC bridge (``tools/workbench_bridge.py``) and the batch-journal
job launcher (``tools/workbench.py``) for real Workbench project orchestration:
create/link systems, drive Engineering Data / Geometry / Model cells, and hand a
cell off to a solver-specific PyAnsys server (Mechanical / Fluent / Sherlock).

Core primitive (aligns with the project's thin script-runner design):
``run_script(script)`` sends a Workbench journal (Python) command string to the
server via ``WorkbenchClient.run_script_string`` and returns the journal's
``wb_script_result`` value.

Sessions live in the shared ``SessionRegistry``, keyed by port (or ``"launched"``),
consistent with ``MechanicalController``.

STATUS: UNVERIFIED (Phase 1, option B). Written per the migration plan but NOT
yet validated against a live Workbench server (no connection/launch was run, per
user instruction). The legacy file-IPC bridge and batch job launcher remain in
place as fallback. Verify with a connection smoke test (launch/connect + a
side-effect-free journal such as a template probe) before deprecating the legacy
path.
"""

from __future__ import annotations

from typing import Optional

from ansys_unified_mcp.core.sessions import registry
from ansys_unified_mcp.core.timeout import BlockingCallTimeout, run_with_timeout

PRODUCT = "workbench"

# Default budget for a single run_script()/run_script_file() call (see
# core/timeout.py caveat: this bounds the caller's wait, not the server call).
DEFAULT_SCRIPT_TIMEOUT = 60.0


class WorkbenchController:
    """Owns Workbench (PyWorkbench) client sessions via the shared SessionRegistry."""

    def _client(self, key: Optional[str] = None):
        return registry.get(PRODUCT, key)

    def launch(
        self,
        show_gui: bool = True,
        version: Optional[str] = None,
        port: int = -1,
        use_insecure_connection: bool = False,
        host: Optional[str] = None,
        server_workdir: Optional[str] = None,
        client_workdir: Optional[str] = None,
    ) -> dict:
        """Launch a new Workbench server and connect a client (PyWorkbench)."""
        try:
            from ansys.workbench.core import launch_workbench
        except ImportError:
            return {"ok": False, "error": "ansys-workbench-core not installed."}
        try:
            client = launch_workbench(
                show_gui=show_gui,
                version=version,
                client_workdir=client_workdir,
                server_workdir=server_workdir,
                port=port,
                use_insecure_connection=use_insecure_connection,
                host=host,
            )
        except Exception as exc:  # noqa: BLE001 - surface any launch failure
            return {"ok": False, "error": str(exc)}

        resolved_port = getattr(client, "_port", None)
        if resolved_port:
            key = str(resolved_port)
        elif port and port > 0:
            key = str(port)
        else:
            key = "launched"
        registry.put(PRODUCT, key, client)
        return {"ok": True, "key": key, "server_version": getattr(client, "server_version", "unknown")}

    def connect(
        self,
        port: int,
        host: Optional[str] = None,
        client_workdir: Optional[str] = None,
        security: str = "mtls",
    ) -> dict:
        """Connect to an existing Workbench server (PyWorkbench)."""
        try:
            from ansys.workbench.core import connect_workbench
        except ImportError:
            return {"ok": False, "error": "ansys-workbench-core not installed."}

        key = str(port)
        if registry.get(PRODUCT, key) is not None:
            registry.set_current(PRODUCT, key)
            return {"ok": True, "port": port, "key": key, "note": "Reused existing session."}
        try:
            client = connect_workbench(
                port=port, client_workdir=client_workdir, host=host, security=security
            )
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}

        registry.put(PRODUCT, key, client)
        return {"ok": True, "port": port, "key": key, "server_version": getattr(client, "server_version", "unknown")}

    def run_script(
        self,
        script: str,
        key: Optional[str] = None,
        log_level: str = "error",
        timeout: float = DEFAULT_SCRIPT_TIMEOUT,
    ) -> str:
        """Send a Workbench journal (Python) command string to the server.

        Returns the journal's ``wb_script_result`` value when the script sets it,
        otherwise a status string. Bounded by ``timeout`` seconds via a worker
        thread (see core/timeout.py) since the underlying call has no native
        timeout.
        """
        client = self._client(key)
        if client is None:
            return "Error: Not connected to Workbench."
        try:
            result = run_with_timeout(
                client.run_script_string, script, log_level=log_level, timeout=timeout
            )
        except BlockingCallTimeout as exc:
            return "Error: " + str(exc)
        except Exception as exc:  # noqa: BLE001
            return "Error: " + str(exc)
        return str(result) if result is not None else "(done)"

    def run_script_file(
        self,
        script_file_name: str,
        key: Optional[str] = None,
        log_level: str = "error",
        timeout: float = DEFAULT_SCRIPT_TIMEOUT,
    ) -> str:
        """Run a Workbench journal file already present on the server.

        Bounded by ``timeout`` seconds via a worker thread (see core/timeout.py).
        """
        client = self._client(key)
        if client is None:
            return "Error: Not connected to Workbench."
        try:
            result = run_with_timeout(
                client.run_script_file, script_file_name, log_level=log_level, timeout=timeout
            )
        except BlockingCallTimeout as exc:
            return "Error: " + str(exc)
        except Exception as exc:  # noqa: BLE001
            return "Error: " + str(exc)
        return str(result) if result is not None else "(done)"

    def start_mechanical_server(self, system_name: str, port: int = 0, key: Optional[str] = None) -> dict:
        """Ask Workbench to start a Mechanical gRPC server for a system's Model cell.

        Returns the gRPC port that PyMechanical can then connect to. This is the
        orchestration handoff: Workbench owns the project schematic, PyMechanical
        drives the Mechanical session on the cell.
        """
        client = self._client(key)
        if client is None:
            return {"ok": False, "error": "Not connected to Workbench."}
        try:
            grpc_port = client.start_mechanical_server(system_name=system_name, port=port)
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}
        return {"ok": True, "system_name": system_name, "grpc_port": grpc_port}

    def upload_file(self, *file_list: str, key: Optional[str] = None) -> dict:
        """Upload local files to the Workbench server working directory."""
        client = self._client(key)
        if client is None:
            return {"ok": False, "error": "Not connected to Workbench."}
        try:
            client.upload_file(*file_list)
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}
        return {"ok": True, "uploaded": list(file_list)}

    def download_project_archive(self, archive_name: str, key: Optional[str] = None) -> dict:
        """Download the current Workbench project as an archive from the server."""
        client = self._client(key)
        if client is None:
            return {"ok": False, "error": "Not connected to Workbench."}
        try:
            path = client.download_project_archive(archive_name)
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}
        return {"ok": True, "archive": str(path)}

    def disconnect(self, key: Optional[str] = None) -> dict:
        """Drop a session from the registry (does not shut the server down)."""
        client = registry.drop(PRODUCT, key)
        if client is None:
            return {"ok": True, "note": "No such session."}
        return {"ok": True, "message": "Disconnected (Workbench server left running)."}

    def is_connected(self, key: Optional[str] = None) -> bool:
        return registry.get(PRODUCT, key) is not None

    def status(self) -> dict:
        keys = registry.keys(PRODUCT)
        return {
            "connected": bool(keys),
            "sessions": keys,
            "current": registry.current_key(PRODUCT),
        }


controller = WorkbenchController()
