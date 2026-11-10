"""Multiphysics bridges: STOP (structural-thermal-optical) and MBD-DEM coupling."""

from __future__ import annotations

from ansys_unified_mcp.products.multiphysics.mbd_dem_bridge import (
    HermiteTrajectory,
    MBDDEMBridge,
    ParticleContact,
    SubstepForceResult,
)
from ansys_unified_mcp.products.multiphysics.stop_analysis_bridge import (
    RigidBody6DOF,
    STOPAnalysisBridge,
    ZernikeFitResult,
)

__all__ = [
    "STOPAnalysisBridge",
    "RigidBody6DOF",
    "ZernikeFitResult",
    "MBDDEMBridge",
    "HermiteTrajectory",
    "SubstepForceResult",
    "ParticleContact",
]
