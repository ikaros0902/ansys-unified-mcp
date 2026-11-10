"""ANSYS Unified MCP 2.0 - 模擬作業生命週期與沙盒管理套件 (Jobs Package)."""

from ansys_unified_mcp.core.jobs.models import (
    ExecutionMetadata,
    JobStatusEnum,
    PhysicalMetrics,
    SimulationSummary,
    VerdictEnum,
)
from ansys_unified_mcp.core.jobs.sandbox import JobSandbox
from ansys_unified_mcp.core.jobs.manager import JobManager
from ansys_unified_mcp.core.jobs.token_bucket_scheduler import (
    TokenBucketLicenseScheduler,
    LicenseLease,
    FeatureBalance,
    PreflightCheckResult,
    LicenseSchedulerError,
    LicenseUnavailableError,
    LicenseAcquisitionTimeoutError,
    FeatureInCooldownError,
    SentinelServiceUnavailableError,
)
from ansys_unified_mcp.core.jobs.interactive_desktop_guard import (
    InteractiveDesktopGuard,
    DesktopGuardError,
    SessionZeroExecutionError,
)

__all__ = [
    "ExecutionMetadata",
    "JobStatusEnum",
    "PhysicalMetrics",
    "SimulationSummary",
    "VerdictEnum",
    "JobSandbox",
    "JobManager",
    "TokenBucketLicenseScheduler",
    "LicenseLease",
    "FeatureBalance",
    "PreflightCheckResult",
    "LicenseSchedulerError",
    "LicenseUnavailableError",
    "LicenseAcquisitionTimeoutError",
    "FeatureInCooldownError",
    "SentinelServiceUnavailableError",
    "InteractiveDesktopGuard",
    "DesktopGuardError",
    "SessionZeroExecutionError",
]
