# Strictly ASCII English Comments
"""VenvSupervisor: Cross-virtual-environment worker lifecycle and process supervisor.

Manages isolated domain worker daemons (.venv-structural, .venv-fluids, .venv-aedt, .venv-optics,
.venv-multibody) with:
- Sub-venv discovery and automatic graceful fallback to current Python interpreter.
- Pre-warmed Worker Daemon Pool lifecycle management.
- Health-probe heartbeat monitoring (ping).
- Crash detection and self-healing auto-restart mechanism.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from ansys_unified_mcp.core.ipc.named_pipe_transport import NamedPipeClient

logger = logging.getLogger(__name__)

# Standard domain configurations mapping to worker modules and candidate venv names
DOMAIN_CONFIGS: Dict[str, Dict[str, Any]] = {
    "structural": {
        "module": "ansys_unified_mcp.workers.structural_worker",
        "candidates": [".venv-structural", ".venv_structural", "venvs/structural"],
        "env_var": "ANSYS_VENV_STRUCTURAL",
    },
    "fluids": {
        "module": "ansys_unified_mcp.workers.fluids_worker",
        "candidates": [".venv-fluids", ".venv_fluids", "venvs/fluids"],
        "env_var": "ANSYS_VENV_FLUIDS",
    },
    "em": {
        "module": "ansys_unified_mcp.workers.em_worker",
        "candidates": [".venv-em", ".venv-aedt", ".venv_em", ".venv_aedt", "venvs/em", "venvs/aedt"],
        "env_var": "ANSYS_VENV_EM",
    },
    "optics": {
        "module": "ansys_unified_mcp.workers.optics_worker",
        "candidates": [".venv-optics", ".venv_optics", "venvs/optics"],
        "env_var": "ANSYS_VENV_OPTICS",
    },
    "multibody": {
        "module": "ansys_unified_mcp.workers.multibody_particles_worker",
        "candidates": [".venv-multibody", ".venv-particles", ".venv_multibody", "venvs/multibody"],
        "env_var": "ANSYS_VENV_MULTIBODY",
    },
}


@dataclass
class WorkerProcess:
    """Represents a domain worker process and its supervisor state."""

    domain: str
    python_path: Path
    worker_module: str
    is_isolated: bool
    process: Optional[subprocess.Popen] = None
    start_time: float = 0.0
    restarts: int = 0
    status: str = "stopped"  # "stopped", "running", "crashed", "restarting"
    client: Optional[NamedPipeClient] = None
    last_ping_time: float = 0.0


class VenvSupervisor:
    """Supervisor for managing cross-virtual-environment worker daemons."""

    def __init__(self, repo_root: Optional[Path] = None) -> None:
        if repo_root is not None:
            self.repo_root = repo_root.resolve()
        else:
            # Anchor to repo root: src/ansys_unified_mcp/core/ipc -> parents[3]
            self.repo_root = Path(__file__).resolve().parents[3]

        self.src_dir = self.repo_root / "src"
        self._workers: Dict[str, WorkerProcess] = {}
        self._init_domain_entries()

    def _init_domain_entries(self) -> None:
        """Initialize worker state tracking for all registered domains."""
        for domain, cfg in DOMAIN_CONFIGS.items():
            python_path, is_isolated = self.resolve_interpreter(domain)
            self._workers[domain] = WorkerProcess(
                domain=domain,
                python_path=python_path,
                worker_module=cfg["module"],
                is_isolated=is_isolated,
                client=NamedPipeClient(domain),
            )

    def resolve_interpreter(self, domain: str) -> Tuple[Path, bool]:
        """Resolve python executable for domain, falling back to current interpreter."""
        cfg = DOMAIN_CONFIGS.get(domain)
        if not cfg:
            return Path(sys.executable), False

        # 1. Check explicit environment variable override
        env_val = os.environ.get(cfg["env_var"])
        if env_val:
            candidate = Path(env_val)
            if candidate.is_file():
                return candidate, True
            elif candidate.is_dir():
                exe = candidate / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
                if exe.exists():
                    return exe, True

        # 2. Check candidate sub-venv directories in repo root
        for rel_dir in cfg["candidates"]:
            venv_path = self.repo_root / rel_dir
            if venv_path.is_dir():
                exe = venv_path / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
                if exe.is_file() and os.access(exe, os.X_OK):
                    return exe, True

        # 3. Graceful fallback to current Python interpreter
        current_py = Path(sys.executable)
        logger.info(
            "Sub-venv for domain '%s' not configured. Gracefully falling back to current interpreter: %s",
            domain,
            current_py,
        )
        return current_py, False

    def is_running(self, domain: str) -> bool:
        """Check if worker process is currently running and active."""
        worker = self._workers.get(domain)
        if not worker or worker.process is None:
            return False
        return worker.process.poll() is None

    def ping(self, domain: str, timeout: float = 2.0) -> bool:
        """Send a ping probe to verify worker responsiveness."""
        worker = self._workers.get(domain)
        if not worker or not self.is_running(domain):
            return False

        if worker.client is None:
            worker.client = NamedPipeClient(domain)

        try:
            ok = worker.client.ping(timeout=timeout)
            if ok:
                worker.last_ping_time = time.time()
                worker.status = "running"
            return ok
        except Exception:
            return False

    def start_worker(
        self,
        domain: str,
        wait_healthy: bool = True,
        timeout: float = 10.0,
    ) -> bool:
        """Start domain worker process and optionally wait for healthy ping probe."""
        worker = self._workers.get(domain)
        if not worker:
            raise ValueError(f"Unknown worker domain: {domain}")

        # If already running and responsive, return immediately
        if self.is_running(domain) and self.ping(domain, timeout=1.0):
            return True

        # Clean up any stale process handles
        if worker.process is not None and worker.process.poll() is None:
            try:
                worker.process.terminate()
                worker.process.wait(timeout=2.0)
            except Exception:
                try:
                    worker.process.kill()
                except Exception:
                    pass

        # Prepare execution environment
        env = os.environ.copy()
        pythonpath_parts = [str(self.src_dir)]
        if "PYTHONPATH" in env:
            pythonpath_parts.append(env["PYTHONPATH"])
        env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)
        env["PYTHONUNBUFFERED"] = "1"
        env["ANSYS_WORKER_DOMAIN"] = domain

        cmd = [str(worker.python_path), "-m", worker.worker_module]
        logger.info("Spawning %s worker: %s", domain, " ".join(cmd))

        worker.status = "starting"
        try:
            worker.process = subprocess.Popen(
                cmd,
                env=env,
                cwd=str(self.repo_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            worker.start_time = time.time()
        except Exception as err:
            logger.error("Failed to spawn worker for domain '%s': %s", domain, err)
            worker.status = "crashed"
            return False

        if not wait_healthy:
            worker.status = "running"
            return True

        # Wait for health probe with backoff
        deadline = time.time() + timeout
        while time.time() < deadline:
            # Check if process died during startup
            retcode = worker.process.poll()
            if retcode is not None:
                worker.status = "crashed"
                stderr_text = ""
                try:
                    if worker.process.stderr:
                        stderr_text = worker.process.stderr.read().decode("utf-8", errors="replace")
                except Exception:
                    pass
                logger.error(
                    "Worker '%s' terminated prematurely with exit code %s: %s",
                    domain,
                    retcode,
                    stderr_text,
                )
                return False

            if self.ping(domain, timeout=0.5):
                worker.status = "running"
                logger.info("Worker '%s' is up and healthy (PID: %d)", domain, worker.process.pid)
                return True

            time.sleep(0.1)

        logger.warning("Worker '%s' did not pass health check within %.1fs timeout", domain, timeout)
        return False

    def stop_worker(self, domain: str, timeout: float = 5.0) -> bool:
        """Gracefully stop a domain worker via RPC shutdown and terminate if needed."""
        worker = self._workers.get(domain)
        if not worker or worker.process is None:
            return True

        # 1. Attempt graceful RPC shutdown
        try:
            if worker.client:
                worker.client.call("shutdown", timeout=1.0)
        except Exception:
            pass

        # 2. Wait for process exit
        try:
            worker.process.wait(timeout=timeout)
            worker.status = "stopped"
            return True
        except subprocess.TimeoutExpired:
            pass

        # 3. Force terminate and kill if unresponsive
        try:
            worker.process.terminate()
            worker.process.wait(timeout=2.0)
        except Exception:
            try:
                worker.process.kill()
            except Exception:
                pass

        worker.status = "stopped"
        return True

    def restart_worker(self, domain: str, timeout: float = 10.0) -> bool:
        """Restart a domain worker process."""
        worker = self._workers.get(domain)
        if not worker:
            raise ValueError(f"Unknown domain: {domain}")

        logger.warning("Restarting worker for domain '%s'", domain)
        worker.status = "restarting"
        self.stop_worker(domain, timeout=2.0)
        worker.restarts += 1
        return self.start_worker(domain, wait_healthy=True, timeout=timeout)

    def ensure_worker(self, domain: str) -> WorkerProcess:
        """Ensure worker is alive; restart automatically if crashed (self-healing)."""
        worker = self._workers.get(domain)
        if not worker:
            raise ValueError(f"Domain '{domain}' is not registered")

        if not self.is_running(domain):
            # If the worker had run before, this is an unexpected crash recovery
            if worker.start_time > 0.0 or worker.process is not None:
                worker.restarts += 1
                logger.warning("Worker '%s' died unexpectedly. Self-healing restart #%d...", domain, worker.restarts)
            else:
                logger.info("Worker '%s' is not running. Performing initial start...", domain)
            self.start_worker(domain, wait_healthy=True)
        elif not self.ping(domain, timeout=1.0):
            logger.warning("Worker '%s' is unresponsive. Performing self-healing restart...", domain)
            self.restart_worker(domain)

        return worker

    def send_request(
        self,
        domain: str,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
    ) -> Any:
        """Send RPC request to domain worker with automatic self-healing crash recovery."""
        self.ensure_worker(domain)
        worker = self._workers[domain]
        if worker.client is None:
            worker.client = NamedPipeClient(domain)

        try:
            return worker.client.call(method, params, timeout=timeout)
        except (ConnectionError, TimeoutError) as err:
            logger.warning("Request failed (%s). Triggering self-healing restart...", err)
            self.restart_worker(domain)
            # Retry once after self-healing restart
            return worker.client.call(method, params, timeout=timeout)

    def prewarm_all(
        self,
        domains: Optional[List[str]] = None,
        timeout: float = 10.0,
    ) -> Dict[str, bool]:
        """Pre-warm all or specified domain worker daemons into a hot standby pool."""
        target_domains = domains or list(DOMAIN_CONFIGS.keys())
        results: Dict[str, bool] = {}
        for d in target_domains:
            ok = self.start_worker(d, wait_healthy=True, timeout=timeout)
            results[d] = ok
        return results

    def stop_all(self, timeout: float = 5.0) -> None:
        """Gracefully stop all worker daemons in the supervisor pool."""
        for domain in list(self._workers.keys()):
            self.stop_worker(domain, timeout=timeout)

    def get_status(self) -> Dict[str, Any]:
        """Return comprehensive status of all managed worker daemons."""
        status_dict: Dict[str, Any] = {}
        for domain, worker in self._workers.items():
            pid = worker.process.pid if (worker.process and worker.process.poll() is None) else None
            status_dict[domain] = {
                "domain": domain,
                "status": worker.status if pid else "stopped",
                "pid": pid,
                "is_isolated": worker.is_isolated,
                "python_path": str(worker.python_path),
                "restarts": worker.restarts,
                "uptime": (time.time() - worker.start_time) if pid else 0.0,
                "last_ping": worker.last_ping_time,
            }
        return status_dict


# Global supervisor instance
supervisor = VenvSupervisor()
