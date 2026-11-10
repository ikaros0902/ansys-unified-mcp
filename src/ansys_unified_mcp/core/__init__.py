"""Core infrastructure: unified ANSYS path resolution, session registry, jobs, gatekeeper, permission gate, data sanitizer, and DAMG causal state machine."""

from __future__ import annotations

from ansys_unified_mcp.core.damg import (
    DAMG_ERROR_CODE_PRECONDITION_VIOLATION,
    DAMGStateMachine,
    NodeDefinition,
    NodeState,
    NodeStatus,
    enforce_damg_precondition,
    invalidate_damg_on_change,
)
from ansys_unified_mcp.core.data_sanitizer import (
    DataSanitizer,
    sanitize_material_properties,
    sanitize_optical_parameters,
    sanitize_bom_and_metadata,
    sanitize_text,
    sanitize_evidence_payload,
)
from ansys_unified_mcp.core.permission_gate import (
    AllowedRoot,
    PermissionGate,
    SecurityGatePermissionError,
    enforce_permission,
    permission_gate,
)

__all__ = [
    "DAMGStateMachine",
    "NodeStatus",
    "NodeDefinition",
    "NodeState",
    "DAMG_ERROR_CODE_PRECONDITION_VIOLATION",
    "enforce_damg_precondition",
    "invalidate_damg_on_change",
    "DataSanitizer",
    "sanitize_material_properties",
    "sanitize_optical_parameters",
    "sanitize_bom_and_metadata",
    "sanitize_text",
    "sanitize_evidence_payload",
    "AllowedRoot",
    "PermissionGate",
    "SecurityGatePermissionError",
    "enforce_permission",
    "permission_gate",
]


