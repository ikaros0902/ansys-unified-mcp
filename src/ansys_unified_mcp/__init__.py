"""ANSYS Unified MCP Server Package."""

__version__ = "2.0.0"

# Note: `config` is intentionally NOT imported here. Importing the instance at
# package level would shadow the `ansys_unified_mcp.config` submodule and force
# eager ANSYS detection on every package import. Import it explicitly where
# needed: `from ansys_unified_mcp.config import config`.

__all__ = ["__version__"]
