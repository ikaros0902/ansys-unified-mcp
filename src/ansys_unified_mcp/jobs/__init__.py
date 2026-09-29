"""Backward-compatibility shim for ansys_unified_mcp.jobs -> ansys_unified_mcp.core.jobs."""
from ansys_unified_mcp.core.jobs import *
from ansys_unified_mcp.core.jobs.manager import JobManager
from ansys_unified_mcp.core.jobs.models import (
    ExecutionMetadata,
    JobStatusEnum,
    PhysicalMetrics,
    SimulationSummary,
    VerdictEnum,
)
from ansys_unified_mcp.core.jobs.sandbox import JobSandbox

__all__ = [
    "ExecutionMetadata",
    "JobStatusEnum",
    "PhysicalMetrics",
    "SimulationSummary",
    "VerdictEnum",
    "JobSandbox",
    "JobManager",
]
