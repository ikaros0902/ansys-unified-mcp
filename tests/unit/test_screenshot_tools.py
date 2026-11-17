# -*- coding: utf-8 -*-
"""跨模組 Screenshot MCP 工具鏈單元測試。"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image as PILImage

from ansys_unified_mcp.core.screenshot_helper import (
    finalize_screenshot_response,
    resolve_screenshot_path,
)
from ansys_unified_mcp.shared import ALIAS_REGISTRY


def test_resolve_screenshot_path_defaults_and_extension(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ANSYS_UNIFIED_MCP_RUNTIME", str(tmp_path / "rt"))

    default_path = resolve_screenshot_path("", "mech_shot.png")
    assert default_path == (tmp_path / "rt" / "screenshots" / "mech_shot.png").resolve()
    assert default_path.parent.is_dir()

    no_ext = resolve_screenshot_path("custom_view")
    assert no_ext.name == "custom_view.png"

    explicit = resolve_screenshot_path(str(tmp_path / "nested" / "cap.png"))
    assert explicit == (tmp_path / "nested" / "cap.png").resolve()
    assert explicit.parent.is_dir()


def test_finalize_screenshot_response_with_real_png(tmp_path: Path):
    png_path = tmp_path / "sample.png"
    PILImage.new("RGB", (64, 48), (255, 255, 255)).save(png_path)

    res_dict = finalize_screenshot_response(
        {"ok": True, "file_path": str(png_path)},
        return_image=True,
        as_tool_result=False,
    )
    assert res_dict["ok"] is True
    assert res_dict["image_returned"] is True

    res_no_img = finalize_screenshot_response(
        {"ok": True, "file_path": str(png_path)},
        return_image=False,
        as_tool_result=False,
    )
    assert res_no_img["image_returned"] is False

    tool_res = finalize_screenshot_response(
        {"ok": True, "file_path": str(png_path)},
        return_image=True,
        as_tool_result=True,
    )
    assert len(tool_res.content) == 2
    assert tool_res.structured_content["image_returned"] is True


def test_mechanical_screenshot_generates_ascii_export_script(tmp_path: Path):
    from ansys_unified_mcp.products.mechanical import api as mech_api
    from ansys_unified_mcp.products.mechanical.tools import mechanical_screenshot

    out_png = tmp_path / "mech_out.png"
    PILImage.new("RGB", (100, 80), (255, 255, 255)).save(out_png)
    captured: dict[str, str] = {}

    def fake_run(script: str, timeout=None) -> str:
        captured["script"] = script
        return json.dumps(
            {
                "ok": True,
                "product": "mechanical",
                "file_path": str(out_png),
                "view": "front",
                "width": 1280,
                "height": 720,
                "target_activated": "Total Deformation",
                "warnings": [],
            }
        )

    with patch.object(mech_api, "_check_connection", return_value=None), patch.object(
        mech_api, "_run", side_effect=fake_run
    ):
        res = mechanical_screenshot(
            file_path=str(out_png),
            target_name="Total Deformation",
            view="front",
            width=1280,
            height=720,
            return_image=True,
        )

    script = captured["script"]
    assert script.isascii()
    assert "GraphicsImageExportSettings" in script
    assert "Graphics.ExportImage" in script
    assert "SetSpecificViewOrientation" in script
    assert "matched.Activate()" in script
    assert res["ok"] is True
    assert res["target_activated"] == "Total Deformation"
    assert res["image_returned"] is True
    assert ALIAS_REGISTRY.get("screenshot") == "mechanical_screenshot"
    assert ALIAS_REGISTRY.get("capture_mechanical_screenshot") == "mechanical_screenshot"


def test_dyna_screenshot_dry_run_builds_cfile(tmp_path: Path):
    from ansys_unified_mcp.products.dyna.tools import dyna_screenshot

    out_png = tmp_path / "dyna_stress.png"
    res = dyna_screenshot(
        d3plot_path=str(tmp_path / "d3plot"),
        file_path=str(out_png),
        fringe_component=9,
        view="top",
        dry_run=True,
    )
    try:
        assert res["ok"] is True
        assert res["dry_run"] is True
        assert res["product"] == "dyna"
        assert res["file_path"] == str(out_png.resolve())
        assert "print png" in res["cfile_script"]
        assert "fringe 9" in res["cfile_script"]
        assert "top" in res["cfile_script"]
    finally:
        cfile = res.get("cfile")
        if cfile and Path(cfile).is_file():
            Path(cfile).unlink(missing_ok=True)


def test_fluent_screenshot_offline_and_mocked_session(tmp_path: Path):
    from ansys_unified_mcp.products.fluent import call_dispatch as fluent_cd
    from ansys_unified_mcp.products.fluent.tools import fluent_screenshot

    with patch.object(fluent_cd, "_fluent_session", None):
        offline = asyncio.run(fluent_screenshot(file_path=str(tmp_path / "fl.png")))
    assert offline["ok"] is False
    assert "Fluent 未連線" in offline["error"]

    fake_tui = MagicMock()
    fake_session = MagicMock(tui=fake_tui)
    out_png = tmp_path / "fl_ok.png"
    PILImage.new("RGB", (64, 64), (255, 255, 255)).save(out_png)
    with patch.object(fluent_cd, "_fluent_session", fake_session):
        online = asyncio.run(
            fluent_screenshot(file_path=str(out_png), view="iso", width=800, height=600)
        )
    assert online["ok"] is True
    assert online["product"] == "fluent"
    assert online["image_returned"] is True
    executed_cmds = [call.args[0] for call in fake_tui.execute.call_args_list]
    assert any("/display/save-picture" in c for c in executed_cmds)


def test_dpf_screenshot_renders_white_contour_from_extracted_results(tmp_path: Path):
    from ansys_unified_mcp.products.dpf import controller as dpf_ctrl
    from ansys_unified_mcp.products.dpf.tools import dpf_screenshot

    mock_extracted = {
        "ok": True,
        "metrics": {"max_deformation": 0.0012, "max_equivalent_stress": 125e6},
        "results": {
            "stress_von_mises": {"max": 125e6, "min": 1e5, "unit": "Pa"},
            "displacement": {"total_max": 0.0012, "min": 0.0, "unit": "m"},
        },
    }
    out_png = tmp_path / "dpf_stress.png"
    with patch.object(dpf_ctrl, "extract_structural_results", return_value=mock_extracted):
        res = dpf_screenshot(
            rst_path="dummy.rst",
            file_path=str(out_png),
            result_type="stress",
            return_image=True,
        )
    assert res["ok"] is True
    assert res["product"] == "dpf"
    assert res["unit"] == "Pa"
    assert res["image_returned"] is True
    assert out_png.is_file()


def test_ans_capture_screenshot_routing(tmp_path: Path):
    from ansys_unified_mcp.products.mechanical import api as mech_api
    from ansys_unified_mcp.tools.session_manager_tools import ans_capture_screenshot

    out_png = tmp_path / "routed_mech.png"
    with patch.object(mech_api, "_check_connection", return_value=None), patch.object(
        mech_api,
        "_run",
        return_value=json.dumps(
            {"ok": True, "product": "mechanical", "file_path": str(out_png)}
        ),
    ):
        mech_res = asyncio.run(
            ans_capture_screenshot(product="mechanical", file_path=str(out_png))
        )
    assert mech_res["ok"] is True
    assert mech_res["product"] == "mechanical"

    dyna_res = asyncio.run(
        ans_capture_screenshot(
            product="dyna",
            file_path=str(tmp_path / "routed_dyna.png"),
            options={"d3plot_path": str(tmp_path / "d3plot"), "dry_run": True},
        )
    )
    try:
        assert dyna_res["ok"] is True
        assert dyna_res["product"] == "dyna"
    finally:
        cfile = dyna_res.get("cfile")
        if cfile and Path(cfile).is_file():
            Path(cfile).unlink(missing_ok=True)

    missing_dpf = asyncio.run(ans_capture_screenshot(product="dpf"))
    assert missing_dpf["ok"] is False

    invalid = asyncio.run(ans_capture_screenshot(product="unknown_solver"))
    assert invalid["ok"] is False
