"""Directed Acyclic Multiphysics Graph (DAMG) causal state machine and precondition interceptor."""

from __future__ import annotations

from ansys_unified_mcp.core.damg.damg_decorators import (
    DAMG_ERROR_CODE_PRECONDITION_VIOLATION,
    build_precondition_violation_envelope,
    enforce_damg_precondition,
    invalidate_damg_on_change,
)
from ansys_unified_mcp.core.damg.damg_state_machine import (
    DAMGStateMachine,
    NodeDefinition,
    NodeState,
    NodeStatus,
)

__all__ = [
    "DAMGStateMachine",
    "NodeStatus",
    "NodeDefinition",
    "NodeState",
    "DAMG_ERROR_CODE_PRECONDITION_VIOLATION",
    "enforce_damg_precondition",
    "invalidate_damg_on_change",
    "build_precondition_violation_envelope",
]
