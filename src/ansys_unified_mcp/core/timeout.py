"""Shared timeout wrapper for blocking calls into external ANSYS sessions.

Some product controllers (Mechanical, optiSLang, Workbench) call directly into
PyAnsys client objects whose underlying gRPC/IPC calls have no built-in
timeout. If the target application hangs (e.g. blocked by a modal dialog, a
deadlocked CAD operation, or a lost network peer), the call blocks the
calling thread indefinitely and the MCP tool invocation never returns to the
client.

This module is a best-effort mitigation: run the blocking call in a worker
thread and give up waiting after ``timeout`` seconds, raising
``BlockingCallTimeout`` so the caller can surface a prompt error instead of
hanging forever. This does NOT cancel the underlying call — Python has no
safe way to force-kill a thread — so the worker keeps running in the
background until the call itself returns or errors. The guarantee is only
that the *caller* (the MCP tool response) gets control back promptly; it is
not true cancellation.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as _FutureTimeoutError
from typing import Callable, TypeVar
import threading
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")

# One shared, bounded pool for the whole process.
_MAX_WORKERS = 8
_pending_count = 0
_pending_lock = threading.Lock()

_executor = ThreadPoolExecutor(max_workers=_MAX_WORKERS, thread_name_prefix="ansys-blocking-call")

def pool_status() -> dict:
    """Return thread pool status for diagnostics."""
    with _pending_lock:
        return {
            "max_workers": _MAX_WORKERS,
            "pending": _pending_count,
            "available": _MAX_WORKERS - _pending_count,
        }

class BlockingCallTimeout(Exception):
    """Raised when a call wrapped by ``run_with_timeout`` exceeds its budget."""


def run_with_timeout(fn: Callable[..., T], *args, timeout: float, **kwargs) -> T:
    """Run ``fn(*args, **kwargs)`` in a worker thread, bounded by ``timeout`` seconds.

    Returns whatever ``fn`` returns on success. Raises ``BlockingCallTimeout``
    if the call has not completed within ``timeout`` seconds. Any exception
    raised by ``fn`` itself propagates unchanged (it is not swallowed or
    wrapped) so existing error-handling in callers keeps working.
    """
    global _pending_count
    with _pending_lock:
        if _pending_count >= _MAX_WORKERS:
            raise BlockingCallTimeout(
                f"Thread pool exhausted ({_pending_count}/{_MAX_WORKERS} workers busy). "
                "Some ANSYS sessions may be unresponsive."
            )
        _pending_count += 1
        
    future = _executor.submit(fn, *args, **kwargs)
    try:
        return future.result(timeout=timeout)
    except _FutureTimeoutError as exc:
        logger.warning("Timeout after %.1fs; worker thread still running in background.", timeout)
        raise BlockingCallTimeout(
            f"Operation exceeded {timeout}s timeout; the ANSYS application may be unresponsive."
        ) from exc
    finally:
        with _pending_lock:
            _pending_count = max(0, _pending_count - 1)
