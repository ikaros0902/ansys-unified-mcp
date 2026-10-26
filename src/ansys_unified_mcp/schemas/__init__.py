# -*- coding: utf-8 -*-
"""Pydantic schemas and structured envelope validation package.

Provides unified response envelopes, ASD-STE100 error envelopes,
4-key tool annotations, and flat Pydantic parameter validation decorators.
All comments and docstrings in this module strictly use ASCII English.
"""

from ansys_unified_mcp.schemas.common_envelope import (
    PaginatedResponse,
    PaginationParams,
    create_error_envelope,
    create_response_envelope,
    paginate_list,
)
from ansys_unified_mcp.schemas.domain_inputs import (
    FluentBoundaryConditionInput,
    FluentSolverSettingsInput,
    GeometryCreateBlockInput,
    GeometryCreateCylinderInput,
    HFSSAdaptiveMeshInput,
    LSDynaDropTestInput,
    MaterialAssignmentInput,
    MaxwellSetupInput,
    MechanicalBoundaryConditionInput,
    MechanicalMeshInput,
    MultibodyJointInput,
    OpticsSimulationInput,
    OptislangMOPInput,
    StaticStructuralSolveInput,
    SteadyThermalSolveInput,
)
from ansys_unified_mcp.schemas.tool_annotations import (
    ToolAnnotations,
    create_tool_annotations,
    validate_flat_pydantic,
)

__all__ = [
    # Envelopes and Pagination
    "create_response_envelope",
    "create_error_envelope",
    "PaginationParams",
    "PaginatedResponse",
    "paginate_list",
    # Tool Annotations & Decorators
    "ToolAnnotations",
    "create_tool_annotations",
    "validate_flat_pydantic",
    # Domain Input Models
    "HFSSAdaptiveMeshInput",
    "MaxwellSetupInput",
    "FluentBoundaryConditionInput",
    "FluentSolverSettingsInput",
    "MechanicalMeshInput",
    "MechanicalBoundaryConditionInput",
    "StaticStructuralSolveInput",
    "SteadyThermalSolveInput",
    "GeometryCreateBlockInput",
    "GeometryCreateCylinderInput",
    "LSDynaDropTestInput",
    "MultibodyJointInput",
    "MaterialAssignmentInput",
    "OptislangMOPInput",
    "OpticsSimulationInput",
]
