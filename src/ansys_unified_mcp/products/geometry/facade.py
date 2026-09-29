"""Geometry product facade.

Single owner of all Geometry (PyAnsys Geometry / SpaceClaim) sessions via SessionRegistry.
Transports:
- ansys-geometry-core (PyAnsys Geometry) gRPC.
Sessions are stored in the shared SessionRegistry keyed by gRPC port or 'default'.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from ansys_unified_mcp.core.sessions import registry

PRODUCT = "geometry"
DEFAULT_KEY = "default"
logger = logging.getLogger("ansys-unified-mcp.geometry")


class GeometryController:
    """Owns Geometry (PyAnsys Geometry Modeler) sessions via the shared SessionRegistry."""

    def _modeler(self, key: Optional[str] = None):
        return registry.get(PRODUCT, key)

    def is_connected(self, key: Optional[str] = None) -> bool:
        return self._modeler(key) is not None

    def launch(
        self,
        port: Optional[int] = None,
        host: str = "localhost",
        transport_mode: str = "wnua",
        connect_timeout: int = 15,
    ) -> dict:
        """Launch or connect to SpaceClaim/Discovery via PyAnsys Geometry."""
        key = str(port) if port else DEFAULT_KEY
        if self._modeler(key) is not None:
            registry.set_current(PRODUCT, key)
            return {"ok": True, "key": key, "note": "Reused existing Geometry session."}

        try:
            from ansys.geometry.core import Modeler
        except ImportError:
            return {"ok": False, "error": "ansys-geometry-core not installed."}

        try:
            if port:
                modeler = Modeler(host=host, port=port, transport_mode=transport_mode, timeout=connect_timeout)
            else:
                modeler = Modeler(transport_mode=transport_mode, timeout=connect_timeout)
            registry.put(PRODUCT, key, modeler)
            return {"ok": True, "key": key, "message": "Connected to Geometry Modeler."}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def status(self, key: Optional[str] = None) -> dict:
        modeler = self._modeler(key)
        if modeler is None:
            return {"ok": False, "connected": False, "error": "No active Geometry modeler session."}
        return {
            "ok": True,
            "connected": True,
            "current_key": registry.current_key(PRODUCT),
            "keys": registry.keys(PRODUCT),
        }

    def close(self, key: Optional[str] = None) -> dict:
        modeler = self._modeler(key)
        if modeler is None:
            return {"ok": True, "note": "No active session to close."}
        try:
            if hasattr(modeler, "close"):
                modeler.close()
        except Exception as exc:
            logger.warning(f"Error while closing Geometry session: {exc}")
        finally:
            registry.drop(PRODUCT, key)
        return {"ok": True, "message": "Geometry session closed."}


controller = GeometryController()
