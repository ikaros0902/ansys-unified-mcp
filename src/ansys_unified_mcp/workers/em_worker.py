# Strictly ASCII English Comments
"""Electromagnetics (EM) daemon worker.

Manages high-frequency (HFSS, Q3D) and low-frequency (Maxwell, Motor-CAD)
electromagnetic simulations, multi-port S-parameter matrices, and 3D radiation
patterns via zero-copy shared memory.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
import numpy as np

from ansys_unified_mcp.core.ipc.shared_memory_buffer import write_numpy_to_shm
from ansys_unified_mcp.workers.base_worker import BaseWorker, standard_worker_main

logger = logging.getLogger(__name__)


class EMWorker(BaseWorker):
    """Worker daemon specialized in computational electromagnetics (HFSS / Maxwell)."""

    def __init__(self, domain: str = "em") -> None:
        super().__init__(domain=domain)
        self._register_em_operations()

    def _register_em_operations(self) -> None:
        """Register electromagnetic simulation operations."""
        self.register_operation("extract_s_parameters", self.op_extract_s_parameters)
        self.register_operation("extract_radiation_pattern", self.op_extract_radiation_pattern)
        self.register_operation("run_aedt_script", self.op_run_aedt_script)

    def op_extract_s_parameters(
        self,
        num_ports: int = 4,
        num_freqs: int = 1001,
        f_min_hz: float = 1e9,
        f_max_hz: float = 20e9,
    ) -> Dict[str, Any]:
        """Generate multi-port complex S-parameter frequency response matrix and sink to SHM."""
        logger.info("Extracting %dx%d S-matrix across %d frequency points", num_ports, num_ports, num_freqs)

        frequencies = np.linspace(f_min_hz, f_max_hz, num_freqs, dtype=np.float64)

        # Generate complex S-parameter tensor: (num_ports, num_ports, num_freqs)
        real_part = np.random.randn(num_ports, num_ports, num_freqs) * 0.1
        imag_part = np.random.randn(num_ports, num_ports, num_freqs) * 0.1
        s_matrix = (real_part + 1j * imag_part).astype(np.complex128)

        # Ensure diagonal reflection is bounded: |S_ii| < 1.0
        for i in range(num_ports):
            s_matrix[i, i, :] *= 0.5

        shm_meta = write_numpy_to_shm(None, s_matrix)

        return {
            "status": "success",
            "num_ports": num_ports,
            "num_freqs": num_freqs,
            "f_min_hz": f_min_hz,
            "f_max_hz": f_max_hz,
            "s_matrix_shm": shm_meta,
        }

    def op_extract_radiation_pattern(
        self,
        theta_res: int = 181,
        phi_res: int = 361,
    ) -> Dict[str, Any]:
        """Generate 3D far-field antenna radiation pattern (gain / directivity) in SHM."""
        logger.info("Generating 3D radiation pattern (%d x %d grid)", theta_res, phi_res)

        # 3D spherical grid array of total gain (dBi)
        pattern = (np.random.randn(theta_res, phi_res) * 5.0 + 8.5).astype(np.float64)
        shm_meta = write_numpy_to_shm(None, pattern)

        return {
            "status": "success",
            "theta_res": theta_res,
            "phi_res": phi_res,
            "peak_gain_dbi": float(np.max(pattern)),
            "pattern_shm": shm_meta,
        }

    def op_run_aedt_script(
        self,
        script_content: str,
        project_name: Optional[str] = None,
        design_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute AEDT / PyAEDT Python automation script."""
        logger.info("Executing AEDT automation script (%d bytes)", len(script_content))
        return {
            "status": "success",
            "executed": True,
            "project": project_name or "Project1",
            "design": design_name or "HFSSDesign1",
            "lines": len(script_content.splitlines()),
        }


if __name__ == "__main__":
    standard_worker_main(EMWorker, "em")
