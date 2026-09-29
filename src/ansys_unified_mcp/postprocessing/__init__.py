"""Backward-compatibility shim for ansys_unified_mcp.postprocessing -> ansys_unified_mcp.analytics.postprocessing."""
from ansys_unified_mcp.analytics.postprocessing import *
from ansys_unified_mcp.analytics.postprocessing.base import (
    BaseResultReader,
    JobNotReadyError,
    PostprocessingError,
    TERMINAL_STATES,
)
from ansys_unified_mcp.analytics.postprocessing.dpf_reader import DPFSandboxReader
from ansys_unified_mcp.analytics.postprocessing.explicit_reader import LSDynaExplicitReader
from ansys_unified_mcp.analytics.postprocessing.router import PostprocessingRouter
