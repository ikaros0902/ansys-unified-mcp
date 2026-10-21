"""Geometry product facade.

Single owner of all Geometry (PyAnsys Geometry / SpaceClaim) sessions via SessionRegistry.
Transports:
- ansys-geometry-core (PyAnsys Geometry) gRPC.
Sessions are stored in the shared SessionRegistry keyed by gRPC port or 'default'.
"""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path
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
        transport_mode: Optional[str] = None,
        connect_timeout: int = 15,
    ) -> dict:
        """Launch or connect to SpaceClaim/Discovery via PyAnsys Geometry."""
        key = str(port) if port else DEFAULT_KEY
        if self._modeler(key) is not None:
            registry.set_current(PRODUCT, key)
            return {"ok": True, "key": key, "port": port, "pid": self._find_pid(port), "note": "Reused existing Geometry session."}

        try:
            from ansys.geometry.core import Modeler
        except ImportError:
            return {"ok": False, "error": "ansys-geometry-core not installed."}

        try:
            options = {"host": host, "timeout": connect_timeout}
            if port is not None:
                if not 1 <= int(port) <= 65535:
                    raise ValueError("port must be between 1 and 65535")
                options["port"] = int(port)
            options["transport_mode"] = transport_mode or "insecure"
            modeler = Modeler(**options)
            registry.put(PRODUCT, key, modeler)
            return {"ok": True, "key": key, "port": port, "pid": self._find_pid(port), "message": "Connected to Geometry Modeler."}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def _find_pid(self, port: Optional[int]) -> Optional[int]:
        """以埠號反查監聽進程 PID，供回傳信封顯示（Port 可視化，杜絕黑盒子）。"""
        if port is None:
            return None
        from ansys_unified_mcp.bridges.connection_manager import connection_manager
        return connection_manager.find_pid_by_port(int(port))

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
        return registry.close(PRODUCT, "close", key)

    def disconnect(self, key: Optional[str] = None) -> dict:
        registry.drop(PRODUCT, key)
        return {"ok": True, "message": "Disconnected."}

    def run_script(
        self,
        script_content: str = "",
        script_path: str = "",
        script_args: Optional[dict[str, str]] = None,
        import_design: bool = True,
        api_version: Optional[int | str] = None,
        key: Optional[str] = None,
    ) -> dict:
        """透過當前已連線的 Geometry (PyAnsys Geometry) gRPC Session 執行腳本。

        直接在當前作用中的 SpaceClaim / Discovery 視窗執行 Python / Discovery 腳本，
        不另開無頭進程。
        """
        modeler = self._modeler(key)
        if modeler is None:
            return {"ok": False, "error": "Geometry Modeler 未連線，請先執行 geometry_launch。"}

        temp_created = False
        actual_path = None
        if script_content:
            tf = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
            tf.write(script_content)
            tf.close()
            actual_path = tf.name
            temp_created = True
        elif script_path:
            actual_path = script_path

        if not actual_path:
            return {"ok": False, "error": "必須指定 script_content 或 script_path。"}

        try:
            res_values, design = modeler.run_script_file(
                file_path=actual_path,
                script_args=script_args,
                import_design=import_design,
                api_version=api_version,
            )
            return {
                "ok": True,
                "values": res_values,
                "message": "腳本已成功透過 PyAnsys Geometry gRPC 在 SpaceClaim 執行完成。",
            }
        except Exception as exc:
            return {"ok": False, "error": f"gRPC 腳本執行失敗: {exc}"}
        finally:
            if temp_created and actual_path:
                try:
                    os.remove(actual_path)
                except OSError:
                    pass


    @staticmethod
    def find_spaceclaim_exe() -> Optional[Path]:
        """自動偵測本機 SpaceClaim.exe 執行檔。"""
        import os
        from pathlib import Path

        # 1. 明確環境變數優先
        override = os.environ.get("ANSYS_SPACECLAIM_EXE")
        if override and Path(override).is_file():
            return Path(override)

        # 2. 透過系統全域設定解析
        try:
            from ansys_unified_mcp.config import config
            if hasattr(config, "spaceclaim_exe") and config.spaceclaim_exe.is_file():
                return config.spaceclaim_exe
        except Exception:
            pass

        # 3. 掃描 AWP_ROOT 環境變數
        for env_var in sorted([k for k in os.environ if k.startswith("AWP_ROOT")], reverse=True):
            cand = Path(os.environ[env_var]) / "scdm" / "SpaceClaim.exe"
            if cand.is_file():
                return cand

        # 4. 常見磁碟機與安裝路徑掃描 (包含 D: 與最新 v261)
        for drive in ["D:", "C:", "E:"]:
            for ver in ["v261", "v252", "v251", "v242", "v241", "v232"]:
                for base in [f"{drive}/ANSYS Inc/{ver}", f"{drive}/Program Files/ANSYS Inc/{ver}"]:
                    cand = Path(base) / "scdm" / "SpaceClaim.exe"
                    if cand.is_file():
                        return cand
        return None

    def run_spaceclaim_headless(
        self,
        script_content: str = "",
        script_path: str = "",
        working_dir: str = "",
        dry_run: bool = False,
        timeout: float = 120.0,
    ) -> dict:
        """以無頭 (Headless) 批次模式啟動 SpaceClaim.exe 執行自動化 IronPython 腳本。"""
        import subprocess
        import tempfile
        from pathlib import Path

        scdm_exe = self.find_spaceclaim_exe()
        if not dry_run and scdm_exe is None:
            return {"ok": False, "error": "未偵測到本機 SpaceClaim.exe 執行檔。"}

        actual_script = None
        temp_created = False
        if script_content:
            tf = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
            tf.write(script_content)
            tf.close()
            actual_script = tf.name
            temp_created = True
        elif script_path:
            actual_script = script_path

        if not actual_script and not dry_run:
            return {"ok": False, "error": "必須指定 script_content 或 script_path。"}

        cmd = [
            str(scdm_exe) if scdm_exe else "SpaceClaim.exe",
            f"/RunScript={actual_script or 'script.py'}",
            "/Headless=True",
            "/Splash=False",
            "/ExitAfter=True",
        ]

        if dry_run:
            if temp_created and actual_script:
                try:
                    os.remove(actual_script)
                except OSError:
                    pass
            return {
                "ok": True,
                "dry_run": True,
                "command": cmd,
                "executable": str(scdm_exe) if scdm_exe else "SpaceClaim.exe",
                "script": actual_script,
            }

        work_dir = Path(working_dir) if working_dir else Path.cwd()
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "ok": proc.returncode == 0,
                "return_code": proc.returncode,
                "stdout": proc.stdout[-2000:] if proc.stdout else "",
                "stderr": proc.stderr[-2000:] if proc.stderr else "",
                "script": actual_script,
                "command": cmd,
            }
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": f"SpaceClaim 腳本執行超時 ({timeout} 秒)"}
        except Exception as exc:
            return {"ok": False, "error": f"執行 SpaceClaim 失敗: {exc}"}
        finally:
            if temp_created and actual_script:
                try:
                    os.remove(actual_script)
                except OSError:
                    pass


controller = GeometryController()

