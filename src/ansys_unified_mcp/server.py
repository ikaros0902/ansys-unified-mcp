# -*- coding: utf-8 -*-
"""FastMCP Main Server Entrypoint Alias.

Provides standard server aliases for FastMCP CLI and external runners:
- fastmcp run ansys_unified_mcp.server:mcp
- python -m ansys_unified_mcp.server

All comments and docstrings in this module strictly use ASCII English.
"""

from __future__ import annotations

# Trigger entrypoint initialization and tool registration
import ansys_unified_mcp.__main__ as _entrypoint
from ansys_unified_mcp.shared import mcp

# Main execution callable alias
main = _entrypoint.main

__all__ = ["mcp", "main"]

if __name__ == "__main__":
    main()
