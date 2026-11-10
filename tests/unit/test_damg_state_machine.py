"""Unit tests for Directed Acyclic Multiphysics Graph (DAMG) state machine and decorators."""

from __future__ import annotations

import asyncio
from pathlib import Path
import pytest

from ansys_unified_mcp.core.damg import (
    DAMG_ERROR_CODE_PRECONDITION_VIOLATION,
    DAMGStateMachine,
    NodeDefinition,
    NodeState,
    NodeStatus,
    enforce_damg_precondition,
    invalidate_damg_on_change,
)


@pytest.fixture(autouse=True)
def clean_state_machines() -> None:
    """Ensure clean state machine registry before each test run."""
    DAMGStateMachine.clear_all_instances()
    yield
    DAMGStateMachine.clear_all_instances()


@pytest.fixture
def sm() -> DAMGStateMachine:
    """Fixture providing clean default state machine."""
    return DAMGStateMachine.get_instance("test_default")


# ------------------------------------------------------------------------------
# 1. Manifest Loading & 9 Physics Disciplines Validation
# ------------------------------------------------------------------------------

def test_manifest_loads_nine_disciplines(sm: DAMGStateMachine) -> None:
    """Verify all 9 physics disciplines are correctly loaded."""
    expected_disciplines = {
        "structural_mechanics",
        "fluid_dynamics",
        "high_frequency_electromagnetics",
        "low_frequency_electromagnetics",
        "thermal_analysis",
        "explicit_dynamics",
        "electronics_cooling",
        "optics_photonics",
        "system_optimization",
    }
    loaded_disciplines = {node.discipline for node in sm.nodes.values()}
    assert expected_disciplines.issubset(loaded_disciplines)


def test_levels_zero_to_seven_represented(sm: DAMGStateMachine) -> None:
    """Verify nodes span from Level 0 (Context) through Level 7 (Observables)."""
    levels_present = {node.level for node in sm.nodes.values()}
    for lvl in range(8):
        assert lvl in levels_present, f"Level {lvl} missing from node definitions"


def test_fluent_cfd_core_mesh_dependencies(sm: DAMGStateMachine) -> None:
    """Verify Fluent CORE_MESH_GENERATED strictly requires BOUNDARY_ZONES_DECLARED and WATERTIGHT_GEOMETRY_READY."""
    core_mesh_node = sm.get_node_definition("CORE_MESH_GENERATED")
    assert core_mesh_node is not None
    assert "BOUNDARY_ZONES_DECLARED" in core_mesh_node.prerequisites
    assert "WATERTIGHT_GEOMETRY_READY" in core_mesh_node.prerequisites
    assert core_mesh_node.level == 4


def test_hfss_frequency_sweep_dependencies(sm: DAMGStateMachine) -> None:
    """Verify HFSS FREQUENCY_SWEEP_EXECUTED strictly requires ADAPTIVE_MESH_CONVERGED."""
    sweep_node = sm.get_node_definition("FREQUENCY_SWEEP_EXECUTED")
    assert sweep_node is not None
    assert "ADAPTIVE_MESH_CONVERGED" in sweep_node.prerequisites
    assert sweep_node.level == 6


def test_multiphysics_couplings_registered(sm: DAMGStateMachine) -> None:
    """Verify cross-discipline multiphysics couplings are loaded."""
    assert len(sm.couplings) >= 3
    assert "thermal_stress" in sm.couplings
    coupling = sm.couplings["thermal_stress"]
    assert coupling["source_node"] == "TEMPERATURE_DISTRIBUTION_EXTRACTED"
    assert coupling["target_node"] == "STRUCTURAL_SOLVER_CONFIGURED"


# ------------------------------------------------------------------------------
# 2. State Machine Core Methods Tests
# ------------------------------------------------------------------------------

def test_initial_node_states_are_unsatisfied(sm: DAMGStateMachine) -> None:
    """Verify initial state of all nodes is UNSATISFIED."""
    assert not sm.is_node_satisfied("STRUCTURAL_GEOMETRY_READY")
    assert sm.get_node_status("STRUCTURAL_GEOMETRY_READY") == NodeStatus.UNSATISFIED


def test_mark_node_satisfied(sm: DAMGStateMachine) -> None:
    """Verify marking node as satisfied updates status and timestamp."""
    sm.mark_node_satisfied("STRUCTURAL_CONTEXT_INITIALIZED", metadata={"source": "test"})
    assert sm.is_node_satisfied("STRUCTURAL_CONTEXT_INITIALIZED")
    assert sm.get_node_status("STRUCTURAL_CONTEXT_INITIALIZED") == NodeStatus.SATISFIED


def test_check_prerequisites_missing(sm: DAMGStateMachine) -> None:
    """Verify check_prerequisites returns missing nodes."""
    missing = sm.check_prerequisites([
        "STRUCTURAL_CONTEXT_INITIALIZED",
        "STRUCTURAL_GEOMETRY_READY",
    ])
    assert "STRUCTURAL_CONTEXT_INITIALIZED" in missing
    assert "STRUCTURAL_GEOMETRY_READY" in missing

    # Satisfy one node
    sm.mark_node_satisfied("STRUCTURAL_CONTEXT_INITIALIZED")
    missing_after = sm.check_prerequisites([
        "STRUCTURAL_CONTEXT_INITIALIZED",
        "STRUCTURAL_GEOMETRY_READY",
    ])
    assert missing_after == ["STRUCTURAL_GEOMETRY_READY"]


def test_check_prerequisites_all_satisfied(sm: DAMGStateMachine) -> None:
    """Verify check_prerequisites returns empty list when all satisfied."""
    sm.mark_node_satisfied("WATERTIGHT_GEOMETRY_READY")
    sm.mark_node_satisfied("BOUNDARY_ZONES_DECLARED")
    sm.mark_node_satisfied("SURFACE_MESH_GENERATED")

    missing = sm.check_prerequisites([
        "WATERTIGHT_GEOMETRY_READY",
        "BOUNDARY_ZONES_DECLARED",
        "SURFACE_MESH_GENERATED",
    ])
    assert missing == []


# ------------------------------------------------------------------------------
# 3. BFS Dirty Invalidation Cascades Tests
# ------------------------------------------------------------------------------

def test_dirty_invalidation_cascades_downstream(sm: DAMGStateMachine) -> None:
    """Verify BFS cascades DIRTY status down the DAG from geometry to observables."""
    # Satisfy structural chain
    chain = [
        "STRUCTURAL_CONTEXT_INITIALIZED",
        "STRUCTURAL_GEOMETRY_READY",
        "STRUCTURAL_MATERIALS_ASSIGNED",
        "STRUCTURAL_BOUNDARIES_APPLIED",
        "STRUCTURAL_MESH_GENERATED",
        "STRUCTURAL_SOLVER_CONFIGURED",
        "STRUCTURAL_SOLUTION_SOLVED",
        "STRUCTURAL_RESULTS_EXTRACTED",
    ]
    for node in chain:
        sm.mark_node_satisfied(node)
        assert sm.is_node_satisfied(node)

    # Invalidate upstream geometry
    invalidated = sm.invalidate_node_and_downstream("STRUCTURAL_GEOMETRY_READY")

    # Upstream context must remain SATISFIED
    assert sm.is_node_satisfied("STRUCTURAL_CONTEXT_INITIALIZED")
    assert sm.get_node_status("STRUCTURAL_CONTEXT_INITIALIZED") == NodeStatus.SATISFIED

    # Target node and all downstream nodes must be DIRTY
    assert sm.get_node_status("STRUCTURAL_GEOMETRY_READY") == NodeStatus.DIRTY
    assert not sm.is_node_satisfied("STRUCTURAL_GEOMETRY_READY")

    assert sm.get_node_status("STRUCTURAL_MESH_GENERATED") == NodeStatus.DIRTY
    assert sm.get_node_status("STRUCTURAL_SOLVER_CONFIGURED") == NodeStatus.DIRTY
    assert sm.get_node_status("STRUCTURAL_SOLUTION_SOLVED") == NodeStatus.DIRTY
    assert sm.get_node_status("STRUCTURAL_RESULTS_EXTRACTED") == NodeStatus.DIRTY

    # Check prerequisites must report DIRTY node
    missing = sm.check_prerequisites(["STRUCTURAL_MESH_GENERATED"])
    assert "STRUCTURAL_MESH_GENERATED" in missing


def test_fluent_cfd_dirty_cascade(sm: DAMGStateMachine) -> None:
    """Verify Fluent CFD dirty invalidation from geometry change cascades to core mesh and solver."""
    sm.mark_node_satisfied("FLUENT_CONTEXT_INITIALIZED")
    sm.mark_node_satisfied("WATERTIGHT_GEOMETRY_READY")
    sm.mark_node_satisfied("BOUNDARY_ZONES_DECLARED")
    sm.mark_node_satisfied("SURFACE_MESH_GENERATED")
    sm.mark_node_satisfied("CORE_MESH_GENERATED")
    sm.mark_node_satisfied("SOLVER_ITERATIONS_CONVERGED")

    # Geometry modification occurs
    invalidated = sm.invalidate_node_and_downstream("WATERTIGHT_GEOMETRY_READY")

    assert "CORE_MESH_GENERATED" in invalidated
    assert "SOLVER_ITERATIONS_CONVERGED" in invalidated
    assert sm.get_node_status("CORE_MESH_GENERATED") == NodeStatus.DIRTY
    assert sm.get_node_status("SOLVER_ITERATIONS_CONVERGED") == NodeStatus.DIRTY


def test_reset_state(sm: DAMGStateMachine) -> None:
    """Verify reset_state clears all satisfied nodes."""
    sm.mark_node_satisfied("STRUCTURAL_CONTEXT_INITIALIZED")
    sm.mark_node_satisfied("STRUCTURAL_GEOMETRY_READY")
    assert sm.is_node_satisfied("STRUCTURAL_CONTEXT_INITIALIZED")

    sm.reset_state()
    assert not sm.is_node_satisfied("STRUCTURAL_CONTEXT_INITIALIZED")
    assert not sm.is_node_satisfied("STRUCTURAL_GEOMETRY_READY")
    assert sm.get_node_status("STRUCTURAL_CONTEXT_INITIALIZED") == NodeStatus.UNSATISFIED


# ------------------------------------------------------------------------------
# 4. Multi-Project / Session Isolation Tests
# ------------------------------------------------------------------------------

def test_session_isolation() -> None:
    """Verify state changes in session A do not contaminate session B."""
    sm_a = DAMGStateMachine.get_instance("session_A")
    sm_b = DAMGStateMachine.get_instance("session_B")

    sm_a.mark_node_satisfied("WATERTIGHT_GEOMETRY_READY")

    assert sm_a.is_node_satisfied("WATERTIGHT_GEOMETRY_READY")
    assert not sm_b.is_node_satisfied("WATERTIGHT_GEOMETRY_READY")

    sm_b.mark_node_satisfied("STRUCTURAL_GEOMETRY_READY")
    assert sm_b.is_node_satisfied("STRUCTURAL_GEOMETRY_READY")
    assert not sm_a.is_node_satisfied("STRUCTURAL_GEOMETRY_READY")


# ------------------------------------------------------------------------------
# 5. Precondition Enforcement Decorator Tests
# ------------------------------------------------------------------------------

def test_precondition_decorator_blocks_when_unsatisfied(sm: DAMGStateMachine) -> None:
    """Verify decorator intercepts call in 0s and returns ASD-STE100 error envelope."""
    call_tracker = {"executed": False}

    @enforce_damg_precondition(
        required_nodes=["WATERTIGHT_GEOMETRY_READY", "BOUNDARY_ZONES_DECLARED"],
        target_node="CORE_MESH_GENERATED",
        state_machine=sm,
    )
    def generate_mesh(element_size: float = 1.0) -> dict:
        call_tracker["executed"] = True
        return {"ok": True, "cells": 50000}

    # Execute tool with missing prerequisites
    result = generate_mesh(element_size=2.5)

    assert not call_tracker["executed"], "Function should have been intercepted before execution"
    assert result["ok"] is False
    assert result["error_code"] == DAMG_ERROR_CODE_PRECONDITION_VIOLATION
    assert result["target_node"] == "CORE_MESH_GENERATED"
    assert "WATERTIGHT_GEOMETRY_READY" in result["missing_prerequisites"]
    assert "BOUNDARY_ZONES_DECLARED" in result["missing_prerequisites"]
    assert len(result["suggested_actions"]) >= 2
    assert "remediation" in result


def test_precondition_decorator_allows_when_satisfied(sm: DAMGStateMachine) -> None:
    """Verify decorator allows execution and marks target node satisfied."""
    call_tracker = {"executed": False}

    sm.mark_node_satisfied("WATERTIGHT_GEOMETRY_READY")
    sm.mark_node_satisfied("BOUNDARY_ZONES_DECLARED")

    @enforce_damg_precondition(
        required_nodes=["WATERTIGHT_GEOMETRY_READY", "BOUNDARY_ZONES_DECLARED"],
        target_node="CORE_MESH_GENERATED",
        state_machine=sm,
    )
    def generate_mesh(element_size: float = 1.0) -> dict:
        call_tracker["executed"] = True
        return {"ok": True, "cells": 75000}

    result = generate_mesh(element_size=1.5)

    assert call_tracker["executed"] is True
    assert result["ok"] is True
    assert result["cells"] == 75000
    assert sm.is_node_satisfied("CORE_MESH_GENERATED")


def test_precondition_decorator_blocks_when_dirty(sm: DAMGStateMachine) -> None:
    """Verify decorator blocks execution if prerequisite was previously satisfied but is now DIRTY."""
    sm.mark_node_satisfied("WATERTIGHT_GEOMETRY_READY")
    sm.mark_node_satisfied("BOUNDARY_ZONES_DECLARED")

    @enforce_damg_precondition(
        required_nodes=["WATERTIGHT_GEOMETRY_READY", "BOUNDARY_ZONES_DECLARED"],
        target_node="CORE_MESH_GENERATED",
        state_machine=sm,
    )
    def generate_mesh() -> dict:
        return {"ok": True}

    # CAD change invalidates watertight geometry and downstream boundary zones
    sm.invalidate_node_and_downstream("WATERTIGHT_GEOMETRY_READY")
    assert sm.get_node_status("WATERTIGHT_GEOMETRY_READY") == NodeStatus.DIRTY

    # Execution should be blocked
    res = generate_mesh()
    assert res["ok"] is False
    assert res["error_code"] == DAMG_ERROR_CODE_PRECONDITION_VIOLATION


def test_precondition_decorator_async_function(sm: DAMGStateMachine) -> None:
    """Verify decorator functions correctly with asynchronous tools."""
    sm.mark_node_satisfied("ADAPTIVE_MESH_CONVERGED")
    sm.mark_node_satisfied("FREQUENCY_SWEEP_CONFIGURED")

    @enforce_damg_precondition(
        required_nodes=["ADAPTIVE_MESH_CONVERGED", "FREQUENCY_SWEEP_CONFIGURED"],
        target_node="FREQUENCY_SWEEP_EXECUTED",
        state_machine=sm,
    )
    async def async_solve_sweep(f_start_ghz: float, f_stop_ghz: float) -> dict:
        await asyncio.sleep(0.001)
        return {"ok": True, "s_params": [0.05, 0.02]}

    res = asyncio.run(async_solve_sweep(1.0, 10.0))
    assert res["ok"] is True
    assert sm.is_node_satisfied("FREQUENCY_SWEEP_EXECUTED")



def test_precondition_does_not_mark_satisfied_on_error(sm: DAMGStateMachine) -> None:
    """Verify target node is NOT marked satisfied if wrapped function returns error."""
    sm.mark_node_satisfied("STRUCTURAL_SOLVER_CONFIGURED")

    @enforce_damg_precondition(
        required_nodes=["STRUCTURAL_SOLVER_CONFIGURED"],
        target_node="STRUCTURAL_SOLUTION_SOLVED",
        state_machine=sm,
    )
    def solve_diverges() -> dict:
        return {"ok": False, "error": "Newton-Raphson residual divergence."}

    res = solve_diverges()
    assert res["ok"] is False
    assert not sm.is_node_satisfied("STRUCTURAL_SOLUTION_SOLVED")


def test_invalidation_decorator_cascades_on_success(sm: DAMGStateMachine) -> None:
    """Verify invalidate_damg_on_change decorator triggers BFS invalidation upon completion."""
    sm.mark_node_satisfied("STRUCTURAL_GEOMETRY_READY")
    sm.mark_node_satisfied("STRUCTURAL_MESH_GENERATED")
    sm.mark_node_satisfied("STRUCTURAL_SOLUTION_SOLVED")

    @invalidate_damg_on_change(
        dirty_nodes=["STRUCTURAL_GEOMETRY_READY"],
        state_machine=sm,
    )
    def modify_cad_dimension(fillet_radius: float) -> dict:
        return {"ok": True, "modified_features": 2}

    res = modify_cad_dimension(2.5)
    assert res["ok"] is True

    # Geometry and downstream mesh/solve must now be DIRTY
    assert sm.get_node_status("STRUCTURAL_GEOMETRY_READY") == NodeStatus.DIRTY
    assert sm.get_node_status("STRUCTURAL_MESH_GENERATED") == NodeStatus.DIRTY
    assert sm.get_node_status("STRUCTURAL_SOLUTION_SOLVED") == NodeStatus.DIRTY
