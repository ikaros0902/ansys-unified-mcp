# Strictly ASCII English Comments
"""Workers package for domain-specific daemon execution.

Provides isolated domain workers communicating via dual-track IPC:
- structural_worker: Structural mechanics (Mechanical, MAPDL, LS-DYNA)
- fluids_worker: Fluid dynamics (Fluent, CFX)
- em_worker: Electromagnetics (HFSS, Maxwell, AEDT)
- optics_worker: Optics and photonics (Speos, Zemax OpticStudio)
- multibody_particles_worker: Multibody dynamics and discrete particles (Rocky DEM, Motion)
"""

from __future__ import annotations

from ansys_unified_mcp.workers.base_worker import BaseWorker
from ansys_unified_mcp.workers.em_worker import EMWorker
from ansys_unified_mcp.workers.fluids_worker import FluidsWorker
from ansys_unified_mcp.workers.multibody_particles_worker import MultibodyParticlesWorker
from ansys_unified_mcp.workers.optics_worker import OpticsWorker
from ansys_unified_mcp.workers.structural_worker import StructuralWorker

__all__ = [
    "BaseWorker",
    "StructuralWorker",
    "FluidsWorker",
    "EMWorker",
    "OpticsWorker",
    "MultibodyParticlesWorker",
]
