# Strictly ASCII English Comments
"""Optics and photonics daemon worker.

Manages Speos, Zemax OpticStudio, and Lumerical optical simulations,
spectral irradiance data cubes, and photometric illuminance point clouds via shared memory.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
import numpy as np

from ansys_unified_mcp.core.ipc.shared_memory_buffer import write_numpy_to_shm
from ansys_unified_mcp.workers.base_worker import BaseWorker, standard_worker_main

logger = logging.getLogger(__name__)


class OpticsWorker(BaseWorker):
    """Worker daemon specialized in optical engineering (Speos / Zemax OpticStudio)."""

    def __init__(self, domain: str = "optics") -> None:
        super().__init__(domain=domain)
        self._register_optics_operations()

    def _register_optics_operations(self) -> None:
        """Register optical simulation operations."""
        self.register_operation("extract_spectral_irradiance", self.op_extract_spectral_irradiance)
        self.register_operation("extract_illuminance_map", self.op_extract_illuminance_map)
        self.register_operation("run_ray_trace", self.op_run_ray_trace)

    def op_extract_spectral_irradiance(
        self,
        wavelengths: int = 61,
        x_res: int = 128,
        y_res: int = 128,
        lambda_min_nm: float = 380.0,
        lambda_max_nm: float = 780.0,
    ) -> Dict[str, Any]:
        """Generate spectral irradiance data cube (W/m^2/nm) and sink to SHM."""
        logger.info("Extracting spectral irradiance cube: %d bands, %dx%d resolution", wavelengths, x_res, y_res)

        # 3D array: (wavelengths, x_res, y_res)
        cube = np.random.uniform(0.01, 120.0, size=(wavelengths, x_res, y_res)).astype(np.float32)
        shm_meta = write_numpy_to_shm(None, cube)

        return {
            "status": "success",
            "wavelength_bands": wavelengths,
            "lambda_min_nm": lambda_min_nm,
            "lambda_max_nm": lambda_max_nm,
            "resolution": [x_res, y_res],
            "total_pixels": x_res * y_res,
            "cube_shm": shm_meta,
        }

    def op_extract_illuminance_map(
        self,
        width: int = 256,
        height: int = 256,
    ) -> Dict[str, Any]:
        """Generate photometric illuminance map (lux) in SHM."""
        logger.info("Generating photometric illuminance map (%dx%d)", width, height)

        lux_map = (np.random.gamma(shape=2.0, scale=500.0, size=(height, width))).astype(np.float64)
        shm_meta = write_numpy_to_shm(None, lux_map)

        return {
            "status": "success",
            "dimensions": [width, height],
            "max_illuminance_lux": float(np.max(lux_map)),
            "average_illuminance_lux": float(np.mean(lux_map)),
            "map_shm": shm_meta,
        }

    def op_run_ray_trace(
        self,
        num_rays: int = 1000000,
        source_type: str = "collimated",
    ) -> Dict[str, Any]:
        """Simulate optical ray trace calculation."""
        logger.info("Running ray trace with %d rays (source: %s)", num_rays, source_type)
        return {
            "status": "success",
            "rays_traced": num_rays,
            "source_type": source_type,
            "efficiency": 0.894,
            "absorbed_fraction": 0.082,
            "lost_rays_fraction": 0.024,
        }


if __name__ == "__main__":
    standard_worker_main(OpticsWorker, "optics")
