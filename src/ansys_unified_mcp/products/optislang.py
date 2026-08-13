"""optiSLang product facade.

Single owner of the optiSLang session, stored in the shared SessionRegistry
(product "optislang", key "default"). This replaces the former module-global
``_osl`` in tools/optislang.py so optiSLang follows the same session lifecycle
as Mechanical (see products/mechanical.py) and no longer keeps a separate
global. The single-key layout preserves today's single-connection behavior
while leaving room to grow to multiple concurrent projects.

Design: the optiSLang native ``run_python_script`` API is the primary
primitive (thin generic script runner); high-level APIs vary across releases
and are deliberately avoided. The ``Optislang`` import is lazy (inside
``connect``) so the module imports cleanly without ansys-optislang-core.
"""

from __future__ import annotations

import os

from ansys_unified_mcp.core.sessions import registry
from ansys_unified_mcp.core.timeout import BlockingCallTimeout, run_with_timeout

PRODUCT = "optislang"
KEY = "default"

# Default budget for a single run_script() call (see core/timeout.py caveat).
DEFAULT_SCRIPT_TIMEOUT = 60.0


class OptislangController:
    """Owns the optiSLang session via the shared SessionRegistry."""

    def _session(self):
        return registry.get(PRODUCT, KEY)

    def is_connected(self) -> bool:
        return self._session() is not None

    def version_string(self) -> str:
        """Cross-version version string: prefer attribute, fall back to method."""
        osl = self._session()
        if osl is None:
            return "unknown"
        for attr in ("osl_version_string", "get_osl_version_string"):
            obj = getattr(osl, attr, None)
            if obj is None:
                continue
            try:
                return str(obj() if callable(obj) else obj)
            except Exception:  # noqa: BLE001 - tolerate cross-version API differences
                continue
        return "unknown"

    def connect(self, project_path: str = "", ini_timeout: float = 60.0) -> dict:
        """Launch and connect to optiSLang. Reuses an existing session if present."""
        if self.is_connected():
            return {"ok": True, "note": "已有連線，若要重連請先 disconnect_optislang。"}
        try:
            from ansys.optislang.core import Optislang
        except ImportError as exc:
            return {"ok": False, "error": f"未安裝 ansys-optislang-core：{exc}"}

        kwargs: dict[str, object] = {"ini_timeout": ini_timeout}
        if project_path:
            if not os.path.isfile(project_path):
                return {"ok": False, "error": f"專案檔不存在：{project_path}"}
            kwargs["project_path"] = project_path
        try:
            osl = Optislang(**kwargs)
        except Exception as exc:  # noqa: BLE001 - surface any connection failure
            return {"ok": False, "error": f"連線失敗：{exc}"}

        registry.put(PRODUCT, KEY, osl)
        return {"ok": True, "version": self.version_string(), "project": project_path or "(new)"}

    def run_script(self, script: str, timeout: float = DEFAULT_SCRIPT_TIMEOUT) -> dict:
        """Run an optiSLang native Python script string in the connected server.

        Bounded by ``timeout`` seconds via a worker thread (see
        core/timeout.py) since the underlying call has no native timeout.
        """
        osl = self._session()
        if osl is None:
            return {"ok": False, "error": "尚未連線 optiSLang，請先呼叫 connect_optislang。"}
        if not script or not script.strip():
            return {"ok": False, "error": "script 不得為空。"}
        try:
            # run_python_script may return str or (success, output); stringify uniformly.
            result = run_with_timeout(osl.run_python_script, script, timeout=timeout)
            return {"ok": True, "output": str(result)}
        except BlockingCallTimeout as exc:
            return {"ok": False, "error": str(exc)}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": f"腳本執行失敗：{exc}"}

    def start_project(self) -> dict:
        """Run (solve) the current optiSLang project, blocking until complete."""
        osl = self._session()
        if osl is None:
            return {"ok": False, "error": "尚未連線 optiSLang，請先呼叫 connect_optislang。"}
        try:
            osl.start()
            return {"ok": True, "note": "專案執行完成。"}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": f"執行失敗：{exc}"}

    def disconnect(self, shutdown: bool = True) -> dict:
        """Drop the session from the registry, optionally disposing the process."""
        osl = registry.drop(PRODUCT, KEY)
        if osl is None:
            return {"ok": True, "note": "本來就未連線。"}
        try:
            if shutdown:
                osl.dispose()
            return {"ok": True}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": f"關閉時發生例外（已強制清除連線）：{exc}"}

    def status(self) -> dict:
        return {"connected": self.is_connected()}


controller = OptislangController()
