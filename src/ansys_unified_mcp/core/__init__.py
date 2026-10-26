"""Core infrastructure: unified ANSYS path resolution, session registry, jobs, gatekeeper, permission gate, and data sanitizer."""

from __future__ import annotations

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

