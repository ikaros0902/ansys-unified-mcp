from unittest.mock import patch
import pytest

from ansys_unified_mcp.products.mechanical.tools import (
    mechanical_assign_materials_from_bom,
    mechanical_create_joints_from_groups,
    mechanical_tune_cfl_mesh,
)
from ansys_unified_mcp.products.dyna.tools import (
    lsdyna_setup_shock_analysis,
    lsdyna_setup_drop_test,
)
from ansys_unified_mcp.products.geometry.tools import (
    geometry_defeature_features,
    geometry_create_bga_array,
    geometry_imprint_contacts,
)


def test_lsdyna_setup_shock_analysis(tmp_path):
    out_k = str(tmp_path / "test_shock.k")
    result = lsdyna_setup_shock_analysis(
        pulse_type="half_sine",
        peak_g=30.0,
        duration_ms=11.0,
        direction="Z",
        output_k_path=out_k,
    )
    assert result["ok"] is True
    assert result["peak_g"] == 30.0
    assert result["duration_ms"] == 11.0
    assert "*KEYWORD" in result["deck_text"]
    assert "*DEFINE_CURVE_TITLE" in result["deck_text"]
    assert tmp_path.joinpath("test_shock.k").is_file()


def test_lsdyna_setup_drop_test(tmp_path):
    out_k = str(tmp_path / "test_drop.k")
    result = lsdyna_setup_drop_test(
        drop_height_mm=500.0,
        impact_surface="rigid_floor",
        output_k_path=out_k,
    )
    assert result["ok"] is True
    assert result["drop_height_mm"] == 500.0
    assert result["impact_velocity_mm_s"] > 0
    assert "*INITIAL_VELOCITY_GENERATION" in result["deck_text"]
    assert "*RIGIDWALL_PLANAR" in result["deck_text"]
    assert tmp_path.joinpath("test_drop.k").is_file()


def test_mechanical_assign_materials_from_bom_mocked():
    with patch("ansys_unified_mcp.products.mechanical.api._check_connection", return_value=None), \
         patch("ansys_unified_mcp.products.mechanical.api._run", return_value='{"ok": true, "assigned_count": 2, "assigned": [{"body": "B1", "material": "Copper"}], "unmatched": []}'):
        result = mechanical_assign_materials_from_bom(
            bom_items=[{"body_name": "B1", "material_name": "Copper"}]
        )
        assert result["ok"] is True
        assert result["assigned_count"] == 2


def test_mechanical_create_joints_from_groups_mocked():
    with patch("ansys_unified_mcp.products.mechanical.api._check_connection", return_value=None), \
         patch("ansys_unified_mcp.products.mechanical.api._run", return_value='{"ok": true, "created_count": 4, "created_joints": ["AutoJoint_1", "AutoJoint_2"], "scanned_groups": 4}'):
        result = mechanical_create_joints_from_groups(connection_type="Fixed", group_prefix="Joint_")
        assert result["ok"] is True
        assert result["created_count"] == 4


def test_mechanical_tune_cfl_mesh_mocked():
    with patch("ansys_unified_mcp.products.mechanical.api._check_connection", return_value=None), \
         patch("ansys_unified_mcp.products.mechanical.api._run", return_value='{"ok": true, "cfl_diagnostic": {"target_timestep_sec": 1e-7}}'):
        result = mechanical_tune_cfl_mesh(target_timestep=1e-7)
        assert result["ok"] is True
        assert result["cfl_diagnostic"]["target_timestep_sec"] == 1e-7


@pytest.mark.anyio
async def test_geometry_tools_unconnected_graceful_fail():
    # When geometry controller is not connected, tools should return structured error envelope
    res1 = await geometry_defeature_features(feature_types=["rounds", "chamfers"])
    assert "ok" in res1
    res2 = await geometry_create_bga_array(rows=10, cols=10, pitch_x=1.0, pitch_y=1.0, ball_radius=0.25)
    assert "ok" in res2
    res3 = await geometry_imprint_contacts(body1_name="Chip", body2_name="PCB")
    assert "ok" in res3

