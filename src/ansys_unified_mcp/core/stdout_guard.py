# -*- coding: utf-8 -*-
# Strictly ASCII English Comments
"""Operating system file descriptor guard for MCP stdio transport.

Isolates the MCP JSON-RPC output stream from accidental writes to stdout.
Duplicates file descriptor 1 for the FastMCP stdio server and redirects
standard file descriptor 1 and sys.stdout to stderr.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import io
import logging
import os
import sys
from typing import Any

import anyio

logger = logging.getLogger("ansys-unified-mcp.stdout_guard")

_GUARD_INSTALLED: bool = False
_DEDICATED_STDOUT_FD: int | None = None


def install_stdio_stdout_guard() -> bool:
    """Install OS-level file descriptor isolation for MCP stdio transport.

    Duplicates OS file descriptor 1 for JSON-RPC framing, then redirects
    file descriptor 1 and sys.stdout to stderr. This prevents C extensions,
    .NET CLR assemblies, or Python print statements from corrupting the
    MCP JSON-RPC stream.

    Returns:
        True if the guard is active, or False if installation was skipped.
    """
    global _GUARD_INSTALLED, _DEDICATED_STDOUT_FD

    if _GUARD_INSTALLED:
        return True

    try:
        import mcp.server.stdio as mcp_stdio
    except Exception as exc:
        logger.warning(f"Skipped stdout guard installation: {exc}")
        return False

    try:
        dup_fd = os.dup(1)
        os.dup2(2, 1)
        sys.stdout = sys.stderr
    except Exception as exc:
        logger.warning(f"Failed to duplicate stdout file descriptor: {exc}")
        return False

    _DEDICATED_STDOUT_FD = dup_fd
    orig_stdio_server = mcp_stdio.stdio_server

    @asynccontextmanager
    async def _guarded_stdio_server(
        stdin: Any = None,
        stdout: Any = None,
    ):
        if stdout is None and _DEDICATED_STDOUT_FD is not None:
            raw_file = os.fdopen(_DEDICATED_STDOUT_FD, "wb", closefd=False)
            text_stream = io.TextIOWrapper(
                raw_file,
                encoding="utf-8",
                write_through=True,
            )
            stdout = anyio.wrap_file(text_stream)
        async with orig_stdio_server(stdin=stdin, stdout=stdout) as streams:
            yield streams

    mcp_stdio.stdio_server = _guarded_stdio_server
    _GUARD_INSTALLED = True
    logger.info("Installed OS file descriptor guard for MCP stdio transport.")
    return True
