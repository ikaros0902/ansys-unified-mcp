"""Mechanical product facade.

Single owner of all Mechanical gRPC sessions. Replaces the three previously
independent Mechanical paths (drivers/sim_impl, tools/mechanical, and the
file-queue/socket bridges), each of which held its own global session.

Transports:
- gRPC (PyMechanical) as the primary bidirectional transport, both
  "connect to an existing instance" and "launch a new headless instance".
- Batch subprocess and Workbench-journal live SendCommand remain available
  via the workbench facade for license-blocked or headless scenarios.

Sessions are stored in the shared SessionRegistry keyed by gRPC port (or the
sentinel "embedded" for an embedded App), enabling multiple concurrent
connections (Requirement: true multi-instance).
"""

from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

from ansys_unified_mcp.core.sessions import registry
from ansys_unified_mcp.core.timeout import BlockingCallTimeout, run_with_timeout

PRODUCT = "mechanical"

# Default budget for a single run_script() call. The underlying gRPC call has
# no native timeout, so this only bounds how long the *caller* waits before
# getting an error back (see core/timeout.py for the caveat on cancellation).
DEFAULT_SCRIPT_TIMEOUT = 60.0


def _esc(s: str) -> str:
    """Escape a user string for safe embedding in an IronPython double-quoted literal."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


class MechanicalController:
    """Owns Mechanical gRPC sessions via the shared SessionRegistry."""

    def _resolve_target_port(self, port: Optional[int], pid: Optional[int]) -> tuple[Optional[int], Optional[str]]:
        """Resolve a gRPC port to connect to. Returns (port, error_message)."""
        if port is not None:
            return int(port), None
        from ansys_unified_mcp.connection_manager import connection_manager

        instances = connection_manager.get_registered_instances()
        mech = [i for i in instances if i.get("app_name") == "AnsysWBU" and "grpc_port" in i]
        if pid is not None:
            match = [i for i in mech if i.get("pid") == pid]
            if not match:
                return None, f"No registered Mechanical instance with PID {pid}."
            return int(match[0]["grpc_port"]), None
        if mech:
            return int(mech[0]["grpc_port"]), None
        scanned = connection_manager.scan_for_mechanical_grpc()
        if scanned is None:
            return None, "No running Mechanical instance registered or detected."
        return scanned, None

    def connect(self, port: Optional[int] = None, pid: Optional[int] = None) -> dict:
        """Connect to an existing Mechanical gRPC server."""
        try:
            import ansys.mechanical.core as mech
        except ImportError:
            return {"ok": False, "error": "ansys-mechanical-core not installed."}

        target_port, err = self._resolve_target_port(port, pid)
        if err:
            return {"ok": False, "error": err}

        key = str(target_port)
        if registry.get(PRODUCT, key) is not None:
            registry.set_current(PRODUCT, key)
            return {"ok": True, "port": target_port, "note": "Reused existing session.", "key": key}

        try:
            session = mech.connect_to_mechanical(port=target_port)
        except Exception as exc:  # noqa: BLE001 - surface any connection failure
            return {"ok": False, "error": str(exc)}

        registry.put(PRODUCT, key, session)
        info = self.run_script(
            "model = ExtAPI.DataModel.Project.Model\n"
            'print("Connected! Analyses: " + str(len(model.Analyses)))\n'
            "for i, a in enumerate(model.Analyses):\n"
            '    print("  [" + str(i) + "] " + str(a.Name) + " (" + str(a.AnalysisType) + ")")\n',
            key=key,
        )
        return {"ok": True, "port": target_port, "key": key, "info": info}

    def launch(self, batch: bool = True) -> dict:
        """Launch a new headless Mechanical instance via PyMechanical."""
        try:
            import ansys.mechanical.core as mech
        except ImportError:
            return {"ok": False, "error": "ansys-mechanical-core not installed."}
        try:
            session = mech.launch_mechanical(
                batch=batch, transport_mode="insecure", start_timeout=120, loglevel="ERROR"
            )
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}

        key = str(getattr(session, "_port", None) or "launched")
        registry.put(PRODUCT, key, session)
        return {"ok": True, "key": key, "version": getattr(session, "version", "unknown")}

    _PROBE_CACHE: dict[str, float] = {}
    _PROBE_TTL = 10.0

    def _probe_session(self, session) -> bool:
        """Lightweight gRPC health check."""
        key = str(id(session))
        now = time.monotonic()
        if key in self._PROBE_CACHE and (now - self._PROBE_CACHE[key]) < self._PROBE_TTL:
            return True
        try:
            session.run_python_script("pass")
            self._PROBE_CACHE[key] = now
            return True
        except Exception:
            self._PROBE_CACHE.pop(key, None)
            return False

    def run_script(self, script: str, key: Optional[str] = None, timeout: float = DEFAULT_SCRIPT_TIMEOUT) -> str:
        """Execute a Python script string in the connected Mechanical session."""
        from ansys_unified_mcp.core.script_guard import check_script
        is_safe, warnings = check_script(script, context="mechanical.run_script")
        if not is_safe:
            return "Error: Script blocked by security guard: " + "; ".join(warnings)
            
        session = registry.get_live(PRODUCT, key, probe_fn=self._probe_session)
        if session is None:
            return "Error: Not connected to Mechanical (session lost or closed)."

        tmp_dir = Path(tempfile.gettempdir())
        out_file = (tmp_dir / f"mech_out_{os.getpid()}.txt").as_posix()
        script_file = (tmp_dir / f"mech_script_{os.getpid()}.py").as_posix()
        try:
            with open(script_file, "w", encoding="utf-8") as fh:
                fh.write(script)

            wrapper = (
                "import sys as _sys\n"
                "class _Cap:\n"
                "    def __init__(self): self.d=[]\n"
                "    def write(self,s): self.d.append(s)\n"
                "    def flush(self): pass\n"
                "_cap=_Cap()\n"
                "_orig=_sys.stdout\n"
                "_sys.stdout=_cap\n"
                "try:\n"
                "    import io as _io\n"
                '    with _io.open(r"' + script_file.replace('"', '\\"') + "\", encoding='utf-8') as _sf: _code=_sf.read()\n"
                "    exec(_code, globals())\n"
                "except Exception as _e:\n"
                "    _cap.d.append('Script error: ' + str(_e) + '\\n')\n"
                "finally:\n"
                "    _sys.stdout=_orig\n"
                '    with open(r"' + out_file.replace('"', '\\"') + "\", 'w') as _f:\n"
                "        _f.write(''.join(_cap.d))\n"
            )
            try:
                run_with_timeout(session.run_python_script, wrapper, timeout=timeout)
            except BlockingCallTimeout as exc:
                return "Error: " + str(exc)

            try:
                with open(out_file, "r", encoding="utf-8") as fh:
                    result = fh.read().strip()
            except OSError:
                result = ""
            return result if result else "(done)"
        except Exception as exc:  # noqa: BLE001
            return "Error: " + str(exc)
        finally:
            for path in (out_file, script_file):
                try:
                    os.remove(path)
                except OSError:
                    pass

    def disconnect(self, key: Optional[str] = None) -> dict:
        """Drop a session from the registry (does not close a launched process)."""
        session = registry.drop(PRODUCT, key)
        if session is None:
            return {"ok": True, "note": "No such session."}
        return {"ok": True, "message": "Disconnected."}

    def is_connected(self, key: Optional[str] = None) -> bool:
        return registry.get_live(PRODUCT, key, probe_fn=self._probe_session) is not None

    def status(self) -> dict:
        keys = registry.keys(PRODUCT)
        return {
            "connected": bool(keys),
            "sessions": keys,
            "current": registry.current_key(PRODUCT),
        }


controller = MechanicalController()
