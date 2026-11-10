# Strictly ASCII English Comments
"""Unit tests for domain daemon workers and VenvSupervisor."""

from __future__ import annotations

import sys
import numpy as np
import pytest

from ansys_unified_mcp.core.ipc.named_pipe_transport import NamedPipeClient
from ansys_unified_mcp.core.ipc.shared_memory_buffer import cleanup_all_shm, read_numpy_from_shm
from ansys_unified_mcp.core.ipc.venv_supervisor import VenvSupervisor
from ansys_unified_mcp.workers.em_worker import EMWorker
from ansys_unified_mcp.workers.fluids_worker import FluidsWorker
from ansys_unified_mcp.workers.multibody_particles_worker import MultibodyParticlesWorker
from ansys_unified_mcp.workers.optics_worker import OpticsWorker
from ansys_unified_mcp.workers.structural_worker import StructuralWorker


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    cleanup_all_shm()


def test_structural_worker_operations():
    """Verify StructuralWorker operations and field result SHM extraction."""
    worker = StructuralWorker(domain="test_structural")
    worker.start()

    try:
        client = NamedPipeClient(domain="test_structural")
        assert client.ping(timeout=3.0) is True

        # Test field extraction
        resp = client.call("extract_field_results", {"num_nodes": 1000, "field_type": "displacement"})
        assert resp["status"] == "success"
        assert resp["num_nodes"] == 1000
        shm_meta = resp["shm_ref"]
        arr = read_numpy_from_shm(shm_meta)
        assert arr.shape == (1000, 3)
        assert arr.dtype == np.float64

        # Test Taylor bar benchmark
        taylor_resp = client.call("solve_taylor_bar", {"length": 30.0, "radius": 3.0})
        assert taylor_resp["benchmark"] == "taylor_bar"
        strain_arr = read_numpy_from_shm(taylor_resp["plastic_strain_shm"])
        assert len(strain_arr) == 10000

        # Test keyword deck creation
        deck_resp = client.call("create_keyword_deck", {"endtim": 0.005})
        assert deck_resp["length"] > 0
    finally:
        worker.stop()


def test_fluids_worker_operations():
    """Verify FluidsWorker flow field extraction and mesh quality analysis."""
    worker = FluidsWorker(domain="test_fluids")
    worker.start()

    try:
        client = NamedPipeClient(domain="test_fluids")
        assert client.ping(timeout=3.0) is True

        # Test 3D CFD flow field extraction
        resp = client.call("extract_flow_field", {"nx": 10, "ny": 10, "nz": 10})
        assert resp["status"] == "success"
        field_cube = read_numpy_from_shm(resp["shm_ref"])
        assert field_cube.shape == (5, 10, 10, 10)

        # Test mesh quality check
        mesh_resp = client.call("check_mesh_quality", {"cell_count": 5000})
        assert mesh_resp["status"] == "success"
        quality_arr = read_numpy_from_shm(mesh_resp["quality_array_shm"])
        assert len(quality_arr) == 5000
    finally:
        worker.stop()


def test_em_worker_operations():
    """Verify EMWorker S-parameter complex matrix extraction."""
    worker = EMWorker(domain="test_em")
    worker.start()

    try:
        client = NamedPipeClient(domain="test_em")
        assert client.ping(timeout=3.0) is True

        # Test multi-port complex S-matrix extraction
        resp = client.call("extract_s_parameters", {"num_ports": 2, "num_freqs": 51})
        assert resp["status"] == "success"
        s_matrix = read_numpy_from_shm(resp["s_matrix_shm"])
        assert s_matrix.shape == (2, 2, 51)
        assert s_matrix.dtype == np.complex128

        # Test radiation pattern
        rad_resp = client.call("extract_radiation_pattern", {"theta_res": 37, "phi_res": 73})
        pat = read_numpy_from_shm(rad_resp["pattern_shm"])
        assert pat.shape == (37, 73)
    finally:
        worker.stop()


def test_optics_worker_operations():
    """Verify OpticsWorker spectral irradiance cube and ray trace."""
    worker = OpticsWorker(domain="test_optics")
    worker.start()

    try:
        client = NamedPipeClient(domain="test_optics")
        assert client.ping(timeout=3.0) is True

        # Test spectral irradiance cube
        resp = client.call("extract_spectral_irradiance", {"wavelengths": 21, "x_res": 32, "y_res": 32})
        assert resp["status"] == "success"
        cube = read_numpy_from_shm(resp["cube_shm"])
        assert cube.shape == (21, 32, 32)
        assert cube.dtype == np.float32

        # Test illuminance map
        ill_resp = client.call("extract_illuminance_map", {"width": 64, "height": 64})
        lux = read_numpy_from_shm(ill_resp["map_shm"])
        assert lux.shape == (64, 64)
    finally:
        worker.stop()


def test_multibody_particles_worker_operations():
    """Verify MultibodyParticlesWorker DEM particle trajectory point clouds."""
    worker = MultibodyParticlesWorker(domain="test_multibody")
    worker.start()

    try:
        client = NamedPipeClient(domain="test_multibody")
        assert client.ping(timeout=3.0) is True

        # Test particle trajectories point cloud
        resp = client.call("extract_particle_trajectories", {"num_particles": 1000, "num_steps": 5})
        assert resp["status"] == "success"
        traj = read_numpy_from_shm(resp["trajectories_shm"])
        assert traj.shape == (1000, 5, 6)

        # Test contact forces
        cf_resp = client.call("extract_contact_forces", {"num_contacts": 500})
        forces = read_numpy_from_shm(cf_resp["contact_forces_shm"])
        assert forces.shape == (500, 3)
    finally:
        worker.stop()


def test_venv_supervisor_fallback_and_status():
    """Verify VenvSupervisor resolves python interpreters and gracefully falls back."""
    supervisor = VenvSupervisor()
    status = supervisor.get_status()

    # All 5 standard domains should be registered
    assert "structural" in status
    assert "fluids" in status
    assert "em" in status
    assert "optics" in status
    assert "multibody" in status

    # Verify fallback to current interpreter when sub-venvs do not exist
    py_path, is_isolated = supervisor.resolve_interpreter("structural")
    assert py_path.exists()
    assert str(py_path).lower() == sys.executable.lower() or py_path.name.lower().startswith("python")


def test_venv_supervisor_e2e_spawn_and_recover():
    """Verify end-to-end supervisor worker spawning, IPC call, crash recovery, and shutdown."""
    supervisor = VenvSupervisor()
    domain = "structural"
    try:
        # Start worker as external subprocess
        started = supervisor.start_worker(domain, wait_healthy=True, timeout=10.0)
        assert started is True
        assert supervisor.is_running(domain) is True
        assert supervisor.ping(domain, timeout=3.0) is True

        # Send request through supervisor with SHM data extraction
        resp = supervisor.send_request(domain, "extract_field_results", {"num_nodes": 500, "field_type": "stress"})
        assert resp["status"] == "success"
        arr = read_numpy_from_shm(resp["shm_ref"])
        assert arr.shape == (500, 6)

        # Simulate unexpected crash: kill worker process directly
        worker = supervisor._workers[domain]
        assert worker.process is not None
        worker.process.kill()
        worker.process.wait(timeout=3.0)
        assert supervisor.is_running(domain) is False

        # Self-healing request: should auto-restart the killed worker and succeed
        recovered_resp = supervisor.send_request(domain, "ping")
        assert recovered_resp["status"] == "pong"
        assert supervisor.is_running(domain) is True
        assert worker.restarts >= 1

    finally:
        supervisor.stop_worker(domain)

