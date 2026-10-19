# -*- coding: utf-8 -*-
"""Deprecated compatibility wrapper for visibility components.

WorkspaceVisibilityMiddleware and related helpers have been moved to
ansys_unified_mcp.tools.visibility to decouple the core module from FastMCP.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "ansys_unified_mcp.core.visibility is deprecated and will be removed in a future release. "
    "Please import from ansys_unified_mcp.tools.visibility instead.",
    DeprecationWarning,
    stacklevel=2,
)

from ansys_unified_mcp.tools.visibility import (
    COMMON_PRODUCT,
    WorkspaceVisibilityMiddleware,
    product_of_module,
)

__all__ = [
    "COMMON_PRODUCT",
    "WorkspaceVisibilityMiddleware",
    "product_of_module",
]
