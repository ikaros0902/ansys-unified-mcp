"""Fluent product facade.

Single owner of all Fluent gRPC sessions via the shared SessionRegistry.
Transports:
- ansys-fluent-core (PyFluent) gRPC.
Sessions are stored in the shared SessionRegistry keyed by gRPC port or 'default'.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from ansys_unified_mcp.core.sessions import registry

PRODUCT = "fluent"
DEFAULT_KEY = "default"
logger = logging.getLogger("ansys-unified-mcp.fluent")


class FluentController:
    """Owns Fluent (PyFluent) sessions via the shared SessionRegistry."""

    def _session(self, key: Optional[str] = None):
        return registry.get(PRODUCT, key)

    def is_connected(self, key: Optional[str] = None) -> bool:
        return self._session(key) is not None

    def launch(
        self,
        processors: int = 4,
        cwd: Optional[str] = None,
        port: Optional[int] = None,
        ip: str = "127.0.0.1",
        password: Optional[str] = None,
        connect_timeout: int = 30,
    ) -> dict:
        """Launch a new Fluent solver instance or connect to an existing instance."""
        key = str(port) if port else DEFAULT_KEY
        if self._session(key) is not None:
            registry.set_current(PRODUCT, key)
            return {"ok": True, "key": key, "note": "Reused existing Fluent session."}

        try:
            import ansys.fluent.core as pyfluent
        except ImportError:
            return {"ok": False, "error": "ansys-fluent-core not installed."}

        try:
            if port:
                session = pyfluent.connect_to_fluent(
                    ip=ip, port=port, password=password, timeout=connect_timeout
                )
            else:
                session = pyfluent.launch_fluent(
                    precision="double",
                    processor_count=processors,
                    start_rootdir=cwd,
                    timeout=connect_timeout,
                )
            registry.put(PRODUCT, key, session)
            return {"ok": True, "key": key, "message": f"Fluent session launched/connected on port {port or 'default'}."}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def status(self, key: Optional[str] = None) -> dict:
        session = self._session(key)
        if session is None:
            return {"ok": False, "connected": False, "error": "No active Fluent session."}
        return {
            "ok": True,
            "connected": True,
            "current_key": registry.current_key(PRODUCT),
            "keys": registry.keys(PRODUCT),
        }

    def exit(self, key: Optional[str] = None) -> dict:
        session = self._session(key)
        if session is None:
            return {"ok": True, "note": "No active session to exit."}
        try:
            session.exit()
        except Exception as exc:
            logger.warning(f"Error while exiting Fluent session: {exc}")
        finally:
            registry.drop(PRODUCT, key)
        return {"ok": True, "message": "Fluent session terminated."}


controller = FluentController()
