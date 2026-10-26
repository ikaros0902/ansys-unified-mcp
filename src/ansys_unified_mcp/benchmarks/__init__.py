"""ANSYS Unified MCP Benchmarks Package (Stage 5 & Extensions).

Provides high-speed analytical solutions, numerical engines, and golden verification
benchmarks for multi-domain physical simulation:
1. Thermal Wall: 1D Composite Two-Layer Conduction
2. Coupling CHT: Conjugate Heat Transfer via Partitioned Dirichlet-Neumann Iteration
3. Materials ACP: Orthotropic Composite Laminate & Tsai-Wu Failure Theory
4. Meshing Sphere: PrimeMesh Watertight Polyhedral Surface Discretization
5. Chemkin Reaction: 0D Isothermal Homogeneous Reactor Kinetics (A -> B)
6. Motor-CAD Efficiency: PMSM Back-EMF, Torque Constant & Copper Loss Efficiency
7. Marine AQWA: Floating Body Heave Free Oscillation Hydrodynamics
8. Optics Lumerical: Symmetric Dielectric Slab Waveguide TE0 Mode Root Finding

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
from ansys_unified_mcp.benchmarks.chemkin_reaction_engine import (
    ChemkinReactionConfig,
    ChemkinReactionEngine,
    ChemkinReactionResult,
)
from ansys_unified_mcp.benchmarks.motorcad_efficiency_engine import (
    MotorCADEfficiencyConfig,
    MotorCADEfficiencyEngine,
    MotorCADEfficiencyResult,
)
from ansys_unified_mcp.benchmarks.marine_aqwa_engine import (
    MarineAqwaConfig,
    MarineAqwaEngine,
    MarineAqwaResult,
)
from ansys_unified_mcp.benchmarks.optics_lumerical_engine import (
    OpticsLumericalConfig,
    OpticsLumericalEngine,
    OpticsLumericalResult,
)
from ansys_unified_mcp.benchmarks.acoustics_sound_engine import (
    AcousticsSoundConfig,
    AcousticsSoundEngine,
    AcousticsSoundResult,
)
from ansys_unified_mcp.benchmarks.sound_acoustics_engine import (
    DIN45692SharpnessEngine,
    MonopoleAcousticsEngine,
    MonopoleResult,
    P_REF_AIR,
    RHO_0_AIR,
    C_0_AIR,
    SPLResult,
    SharpnessResult,
    SoundPressureLevelEngine,
    ZwickerLoudnessEngine,
    ZwickerLoudnessResult,
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
    "ChemkinReactionConfig",
    "ChemkinReactionResult",
    "ChemkinReactionEngine",
    "MotorCADEfficiencyConfig",
    "MotorCADEfficiencyResult",
    "MotorCADEfficiencyEngine",
    "MarineAqwaConfig",
    "MarineAqwaResult",
    "MarineAqwaEngine",
    "OpticsLumericalConfig",
    "OpticsLumericalResult",
    "OpticsLumericalEngine",
    "AcousticsSoundConfig",
    "AcousticsSoundResult",
    "AcousticsSoundEngine",
    "P_REF_AIR",
    "RHO_0_AIR",
    "C_0_AIR",
    "SPLResult",
    "MonopoleResult",
    "ZwickerLoudnessResult",
    "SharpnessResult",
    "SoundPressureLevelEngine",
    "MonopoleAcousticsEngine",
    "ZwickerLoudnessEngine",
    "DIN45692SharpnessEngine",
]
