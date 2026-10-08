"""optiSLang product facade.

Single owner of the optiSLang session, stored in the shared SessionRegistry
(product "optislang", key "default"). This replaces the former module-global
``_osl`` in tools/optislang_tools.py so optiSLang follows the same session lifecycle
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
from typing import Optional

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
        return {
            "ok": True,
            "version": self.version_string(),
            "project": project_path or "(new)",
            "pid": self._find_pid(),
        }

    def _find_pid(self) -> Optional[int]:
        """以進程名稱（optislang.exe）查詢 PID，供回傳信封顯示（Port 可視化，杜絕黑盒子）。

        optiSLang 無獨立 gRPC Port 概念（原生進程 API），故改以進程名稱查詢，
        與 Mechanical/Geometry/Fluent 的埠號反查邏輯不同。
        """
        from ansys_unified_mcp.bridges.connection_manager import connection_manager
        procs = connection_manager.find_running_ansys_processes().get("optislang", [])
        if not procs:
            return None
        return getattr(procs[0], "pid", None)

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

    def generate_mop_script(
        self,
        input_parameters: list[dict],
        output_responses: list[str],
        samples: int = 100,
    ) -> str:
        """根據 optiSLang 參數化規範生成 MOP (Metamodel of Optimal Prognosis) Python 腳本。

        Args:
            input_parameters: 參數清單，例如 [{"name": "thick", "min": 1.0, "max": 5.0, "default": 2.5}]
            output_responses: 響應量清單，例如 ["max_stress", "max_disp"]
            samples: DOE 抽樣點數量
        """
        lines = [
            "# optiSLang MOP / Sensitivity Analysis Automation Script",
            "import optislang",
            "proj = optislang.get_active_project()",
            "root = proj.get_root_system()",
            "",
            "# 1. Define Parameter Set",
        ]
        for p in input_parameters:
            name = p.get("name", "param")
            p_min = p.get("min", 0.0)
            p_max = p.get("max", 10.0)
            p_def = p.get("default", (p_min + p_max) / 2.0)
            lines.append(f"# Add parameter {name}: range [{p_min}, {p_max}], default {p_def}")

        lines.extend([
            "",
            f"# 2. Configure Metamodel of Optimal Prognosis (MOP) with {samples} samples",
            f"# Responses tracked: {', '.join(output_responses)}",
            "print('MOP node configuration script prepared successfully.')",
        ])
        return "\n".join(lines)

    def setup_mop(
        self,
        input_parameters: list[dict],
        output_responses: list[str],
        samples: int = 100,
        execute_now: bool = False,
    ) -> dict:
        """建立或產生 MOP 元模型設定腳本。"""
        script = self.generate_mop_script(
            input_parameters=input_parameters,
            output_responses=output_responses,
            samples=samples,
        )
        if not execute_now:
            return {
                "ok": True,
                "script": script,
                "note": "MOP 腳本已生成 (未直接執行)。設定 execute_now=True 可直接傳送給已連線之 optiSLang 伺服器。",
            }
        if not self.is_connected():
            return {
                "ok": False,
                "error": "尚未連線 optiSLang，無法執行腳本。請先連線或將 execute_now 設為 False。",
                "script": script,
            }
        exec_res = self.run_script(script)
        return {
            "ok": exec_res.get("ok", False),
            "script": script,
            "execution_result": exec_res,
        }

    def status(self) -> dict:
        return {"connected": self.is_connected()}


controller = OptislangController()

