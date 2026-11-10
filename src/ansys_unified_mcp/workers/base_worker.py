# Strictly ASCII English Comments
"""BaseWorker: Common daemon worker base for cross-virtual-environment domain workers.

Listens to the control plane via NamedPipeServer, handles JSON-RPC 2.0 requests,
routes commands to registered operations or product facades, and coordinates with
SharedMemoryBuffer for high-speed zero-copy numerical data transfer.
"""

from __future__ import annotations

import argparse
import logging
import os
import signal
import sys
import time
from typing import Any, Callable, Dict, Optional

from ansys_unified_mcp.core.ipc.named_pipe_transport import NamedPipeServer
from ansys_unified_mcp.core.ipc.shared_memory_buffer import cleanup_all_shm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
)
logger = logging.getLogger(__name__)


class BaseWorker:
    """Base class for all domain-specific daemon workers."""

    def __init__(self, domain: str) -> None:
        self.domain = domain
        self.server = NamedPipeServer(domain)
        self.operations: Dict[str, Callable[..., Any]] = {}
        self._setup_default_operations()

    def _setup_default_operations(self) -> None:
        """Register default core operations."""
        self.register_operation("get_worker_info", self._op_worker_info)
        self.register_operation("echo", lambda **kwargs: kwargs)

    def _op_worker_info(self, **kwargs: Any) -> Dict[str, Any]:
        """Return worker runtime metadata."""
        return {
            "domain": self.domain,
            "pid": os.getpid(),
            "python_version": sys.version,
            "executable": sys.executable,
            "operations": list(self.operations.keys()),
            "start_time": time.time(),
        }

    def register_operation(self, name: str, handler: Callable[..., Any]) -> None:
        """Register a domain-specific operation callable."""
        self.operations[name] = handler
        self.server.register_handler(name, handler)

    def run(self) -> None:
        """Run the worker loop synchronously until shutdown."""
        logger.info("Initializing %s worker (PID: %d)...", self.domain, os.getpid())

        # Setup OS signal handlers for graceful termination
        def _signal_handler(signum: int, frame: Any) -> None:
            logger.info("Signal %d received in worker %s, stopping...", signum, self.domain)
            self.stop()

        signal.signal(signal.SIGINT, _signal_handler)
        signal.signal(signal.SIGTERM, _signal_handler)

        try:
            self.server.serve_forever()
        finally:
            logger.info("Cleaning up shared memory for worker %s...", self.domain)
            cleanup_all_shm()
            logger.info("Worker %s shut down successfully.", self.domain)

    def start(self) -> None:
        """Start the worker in a background daemon thread (for testing)."""
        self.server.start()

    def stop(self) -> None:
        """Signal the worker server to stop."""
        self.server.stop()


def standard_worker_main(worker_class: type[BaseWorker], domain: str) -> None:
    """Standard CLI entry point parser for domain worker scripts."""
    parser = argparse.ArgumentParser(description=f"ANSYS {domain.title()} Domain Worker")
    parser.add_argument("--domain", default=domain, help="Worker domain name override")
    args = parser.parse_args()

    worker = worker_class(domain=args.domain)
    worker.run()
