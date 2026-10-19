# -*- coding: utf-8 -*-
"""DPFController 單元測試。

涵蓋：
- 檔案不存在時優雅報錯（extract_structural_results / get_model_summary）
- 沙盒複製防檔案鎖邏輯（copy_to_sandbox=True 時來源檔不被開啟）
- Mock DPF Model 解析流程
- 真實 Model 解析例外的容錯（優雅回傳而非拋出）
- MCP tool 層調用
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ansys_unified_mcp.products.dpf import DPFController, controller as dpf_controller


# ---------------------------------------------------------------------------
# 檔案不存在 → 優雅報錯
# ---------------------------------------------------------------------------

def test_extract_structural_results_file_not_found(tmp_path):
    missing = tmp_path / "does_not_exist.rst"
    result = dpf_controller.extract_structural_results(missing)
    assert result["ok"] is False
    assert "RST file not found" in result["error"]
    assert str(missing) in result["error"]


def test_get_model_summary_file_not_found(tmp_path):
    missing = tmp_path / "does_not_exist.rst"
    result = dpf_controller.get_model_summary(missing)
    assert result["ok"] is False
    assert "RST file not found" in result["error"]


# ---------------------------------------------------------------------------
# ansys-dpf-core 未安裝 → 優雅報錯（模擬 ImportError）
# ---------------------------------------------------------------------------

def test_extract_structural_results_import_error(tmp_path):
    rst = tmp_path / "model.rst"
    rst.write_bytes(b"fake rst content")

    ctrl = DPFController()
    with patch.dict(sys.modules, {"ansys.dpf.core": None, "ansys.dpf": None, "ansys": None}):
        result = ctrl.extract_structural_results(rst, copy_to_sandbox=False)
    assert result["ok"] is False
    assert "ansys-dpf-core not installed" in result["error"]


# ---------------------------------------------------------------------------
# 沙盒複製防檔案鎖邏輯
# ---------------------------------------------------------------------------

def test_sandbox_copy_creates_independent_file_and_cleans_up(tmp_path):
    """copy_to_sandbox=True 時，應複製到暫存目錄讀取，且事後清理副本。"""
    rst = tmp_path / "model.rst"
    rst.write_bytes(b"fake rst content")

    ctrl = DPFController()
    read_path, sandbox_path = ctrl._resolve_read_path(rst, copy_to_sandbox=True, output_dir=None)

    assert sandbox_path is not None
    assert read_path != rst
    assert read_path.exists()
    assert read_path.read_bytes() == rst.read_bytes()

    ctrl._cleanup_sandbox_copy(sandbox_path)
    assert not read_path.exists()
    # 原始檔完全不受影響
    assert rst.exists()


def test_no_sandbox_copy_reads_source_directly(tmp_path):
    """copy_to_sandbox=False 時，直接使用來源路徑，不建立副本。"""
    rst = tmp_path / "model.rst"
    rst.write_bytes(b"fake rst content")

    ctrl = DPFController()
    read_path, sandbox_path = ctrl._resolve_read_path(rst, copy_to_sandbox=False, output_dir=None)

    assert sandbox_path is None
    assert read_path == rst


def test_sandbox_copy_with_custom_output_dir(tmp_path):
    rst = tmp_path / "model.rst"
    rst.write_bytes(b"fake rst content")
    output_dir = tmp_path / "custom_sandbox"

    ctrl = DPFController()
    read_path, sandbox_path = ctrl._resolve_read_path(rst, copy_to_sandbox=True, output_dir=output_dir)

    assert read_path.parent.parent == output_dir
    assert read_path.exists()
    assert sandbox_path == read_path


# ---------------------------------------------------------------------------
# Mock DPF Model 解析流程
# ---------------------------------------------------------------------------

def _build_fake_dpf_module():
    """重用禁止全場下載的 DPF fake。"""
    from tests.unit.test_dpf_summary import build_fake

    fake, model = build_fake()
    return fake, model


def test_extract_structural_results_success_with_mock_model(tmp_path):
    rst = tmp_path / "model.rst"
    rst.write_bytes(b"fake rst content")

    fake_dpf, _ = _build_fake_dpf_module()

    ctrl = DPFController()
    with patch.dict(sys.modules, {"ansys.dpf.core": fake_dpf}):
        result = ctrl.extract_structural_results(rst, copy_to_sandbox=False)

    assert result["ok"] is True
    assert result["metrics"]["num_nodes"] == 120
    assert result["metrics"]["num_elements"] == 40
    assert result["metrics"]["max_deformation"] == pytest.approx(1.2)
    assert result["metrics"]["max_equivalent_stress"] == pytest.approx(25.5)
    assert result["time_freq_sets"] == [0.0, 0.1, 0.2]


def test_get_model_summary_success_with_mock_model(tmp_path):
    rst = tmp_path / "model.rst"
    rst.write_bytes(b"fake rst content")

    fake_dpf, _ = _build_fake_dpf_module()

    ctrl = DPFController()
    with patch.dict(sys.modules, {"ansys.dpf.core": fake_dpf}):
        result = ctrl.get_model_summary(rst)

    assert result["ok"] is True
    assert result["summary"]["num_nodes"] == 120
    assert result["summary"]["num_elements"] == 40
    assert "available_results" in result["summary"]["result_info"]


# ---------------------------------------------------------------------------
# 真實 Model 解析例外容錯
# ---------------------------------------------------------------------------

def test_extract_structural_results_model_parse_exception_is_graceful(tmp_path):
    """Model() 拋出例外時，應優雅回傳 {"ok": False, "error": ...} 而非拋出。"""
    rst = tmp_path / "corrupt.rst"
    rst.write_bytes(b"not a real rst file")

    fake_dpf = types.ModuleType("ansys.dpf.core")
    fake_dpf.Model = MagicMock(side_effect=RuntimeError("Unable to parse RST file: corrupted header"))

    ctrl = DPFController()
    with patch.dict(sys.modules, {"ansys.dpf.core": fake_dpf}):
        result = ctrl.extract_structural_results(rst, copy_to_sandbox=False)

    assert result["ok"] is False
    assert "corrupted header" in result["error"]


def test_extract_structural_results_missing_stress_field_is_tolerated(tmp_path):
    """純熱分析等缺乏應力場之結果檔，抽取失敗應容錯為 None 而非整體失敗。"""
    rst = tmp_path / "thermal.rst"
    rst.write_bytes(b"fake rst content")

    fake_dpf, fake_model = _build_fake_dpf_module()
    fake_model.metadata.result_info.available_results = []

    ctrl = DPFController()
    with patch.dict(sys.modules, {"ansys.dpf.core": fake_dpf}):
        result = ctrl.extract_structural_results(rst, copy_to_sandbox=False)

    assert result["ok"] is True
    assert result["metrics"]["max_deformation"] is None
    assert result["metrics"]["max_equivalent_stress"] is None
    assert result["metrics"]["num_nodes"] == 120


# ---------------------------------------------------------------------------
# MCP tool 層調用
# ---------------------------------------------------------------------------

def test_mcp_tool_dpf_extract_structural_results_returns_json_envelope(tmp_path):
    from ansys_unified_mcp.products.dpf import tools as dpf_tools

    missing = tmp_path / "missing.rst"
    raw = dpf_tools.dpf_extract_structural_results(str(missing))
    payload = raw
    assert payload["ok"] is False
    assert "RST file not found" in payload["error"]


def test_mcp_tool_dpf_get_model_summary_returns_json_envelope(tmp_path):
    from ansys_unified_mcp.products.dpf import tools as dpf_tools

    missing = tmp_path / "missing.rst"
    raw = dpf_tools.dpf_get_model_summary(str(missing))
    payload = raw
    assert payload["ok"] is False
    assert "RST file not found" in payload["error"]


def test_mcp_tool_dpf_extract_structural_results_success(tmp_path):
    from ansys_unified_mcp.products.dpf import tools as dpf_tools

    rst = tmp_path / "model.rst"
    rst.write_bytes(b"fake rst content")
    fake_dpf, _ = _build_fake_dpf_module()

    with patch.dict(sys.modules, {"ansys.dpf.core": fake_dpf}):
        raw = dpf_tools.dpf_extract_structural_results(str(rst), copy_to_sandbox=False)

    payload = raw
    assert payload["ok"] is True
    assert payload["metrics"]["num_nodes"] == 120


@pytest.mark.parametrize("failure", [False, True])
def test_streams_released_and_cleanup_preserves_original_error(tmp_path, failure):
    rst = tmp_path / "source.rst"
    rst.write_bytes(b"source")
    output_dir = tmp_path / "shared"
    output_dir.mkdir()
    preserved = output_dir / "keep.txt"
    preserved.write_text("keep")
    fake, model = _build_fake_dpf_module()
    if failure:
        model.results.stress.side_effect = RuntimeError("original extraction failure")
    model.metadata.release_streams.side_effect = RuntimeError("release failure")
    with patch.dict(sys.modules, {"ansys.dpf.core": fake}):
        result = DPFController().extract_structural_results(rst, output_dir=output_dir)
    model.metadata.release_streams.assert_called_once()
    assert result["ok"] is not failure
    if failure:
        assert result["error"] == "original extraction failure"
    assert preserved.read_text() == "keep"
    assert list(output_dir.iterdir()) == [preserved]
    assert rst.read_bytes() == b"source"


def test_summary_releases_streams(tmp_path):
    rst = tmp_path / "source.rst"
    rst.write_bytes(b"source")
    fake, model = _build_fake_dpf_module()
    model.metadata.release_streams.side_effect = RuntimeError("release failure")
    with patch.dict(sys.modules, {"ansys.dpf.core": fake}):
        result = DPFController().get_model_summary(rst)
    assert result["ok"] is True
    model.metadata.release_streams.assert_called_once()


def test_cleanup_failure_does_not_mask_parse_failure(tmp_path):
    rst = tmp_path / "source.rst"
    rst.write_bytes(b"source")
    fake, model = _build_fake_dpf_module()
    model.results.stress.side_effect = RuntimeError("original extraction failure")
    with patch.dict(sys.modules, {"ansys.dpf.core": fake}), patch(
        "ansys_unified_mcp.products.dpf.facade.shutil.rmtree", side_effect=OSError("locked")
    ):
        result = DPFController().extract_structural_results(rst, output_dir=tmp_path / "sandbox")
    assert result["error"] == "original extraction failure"
    model.metadata.release_streams.assert_called_once()
