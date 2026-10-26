"""ANSYS Unified MCP Benchmarks Package (Stage 5).

Provides high-speed analytical solutions, numerical engines, and golden verification
benchmarks for multi-domain physical simulation:
1. Thermal Wall: 1D Composite Two-Layer Conduction
2. Coupling CHT: Conjugate Heat Transfer via Partitioned Dirichlet-Neumann Iteration
3. Materials ACP: Orthotropic Composite Laminate & Tsai-Wu Failure Theory
4. Meshing Sphere: PrimeMesh Watertight Polyhedral Surface Discretization

All code comments strictly ASCII English.
"""

from __future__ import annotations

from ansys_unified_mcp.benchmarks.thermal_wall_engine import (
    ThermalWallConfig,
    ThermalWallEngine,
    ThermalWallResult,
)
from ansys_unified_mcp.benchmarks.coupling_cht_engine import (
    CouplingCHTConfig,
    CouplingCHTEngine,
    CouplingCHTResult,
)
from ansys_unified_mcp.benchmarks.materials_acp_engine import (
    ACPAnalysisResult,
    ACPCompositeEngine,
    ACPLoadCase,
    OrthotropicPlyProperties,
)
from ansys_unified_mcp.benchmarks.meshing_sphere_engine import (
    PrimeMeshSphereEngine,
    SphereMeshConfig,
    SphereMeshResult,
)

__all__ = [
    "ThermalWallConfig",
    "ThermalWallResult",
    "ThermalWallEngine",
    "CouplingCHTConfig",
    "CouplingCHTResult",
    "CouplingCHTEngine",
    "OrthotropicPlyProperties",
    "ACPLoadCase",
    "ACPAnalysisResult",
    "ACPCompositeEngine",
    "SphereMeshConfig",
    "SphereMeshResult",
    "PrimeMeshSphereEngine",
]
