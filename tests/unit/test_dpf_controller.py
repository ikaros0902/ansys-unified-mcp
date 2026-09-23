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

    assert read_path.parent == output_dir
    assert read_path.exists()
    assert sandbox_path == read_path


# ---------------------------------------------------------------------------
# Mock DPF Model 解析流程
# ---------------------------------------------------------------------------

def _build_fake_dpf_module():
    """建立一個假的 ansys.dpf.core 模組，模擬 Model 解析成功路徑。"""
    fake_dpf = types.ModuleType("ansys.dpf.core")

    fake_mesh = MagicMock()
    fake_mesh.nodes.n_nodes = 120
    fake_mesh.elements.n_elements = 40

    fake_metadata = MagicMock()
    fake_metadata.meshed_region = fake_mesh

    fake_time_freqs = MagicMock()
    fake_time_freqs.data = [0.0, 0.1, 0.2]
    fake_tfs = MagicMock()
    fake_tfs.time_frequencies = fake_time_freqs
    fake_metadata.time_freq_support = fake_tfs
    fake_metadata.result_info = "Static Structural Result"

    fake_disp_field = MagicMock()
    fake_norm_field = MagicMock()
    fake_norm_field.data = [0.5, 1.2, 0.8]

    fake_disp_fields_container = MagicMock()
    fake_disp_fields_container.__getitem__ = lambda self, idx: fake_disp_field
    fake_disp_op = MagicMock()
    fake_disp_op.outputs.fields_container.return_value = fake_disp_fields_container

    fake_eqv_field = MagicMock()
    fake_eqv_field.data = [10.0, 25.5, 15.0]

    fake_stress_op = MagicMock()

    fake_results = MagicMock()
    fake_results.displacement.return_value = fake_disp_op
    fake_results.stress.return_value = fake_stress_op

    fake_model = MagicMock()
    fake_model.metadata = fake_metadata
    fake_model.results = fake_results

    fake_dpf.Model = MagicMock(return_value=fake_model)
    fake_dpf.locations = types.SimpleNamespace(nodal="Nodal")

    fake_norm_op_result = MagicMock()
    fake_norm_op_result.eval.return_value = fake_norm_field

    fake_eqv_op_result = MagicMock()
    fake_eqv_op_result.eval.return_value = [fake_eqv_field]

    fake_math = types.SimpleNamespace(norm=MagicMock(return_value=fake_norm_op_result))
    fake_invariant = types.SimpleNamespace(von_mises_eqv_fc=MagicMock(return_value=fake_eqv_op_result))
    fake_dpf.operators = types.SimpleNamespace(math=fake_math, invariant=fake_invariant)

    return fake_dpf, fake_model


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
    assert "Static Structural" in result["summary"]["result_info"]


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
    fake_model.results.stress.side_effect = RuntimeError("No stress result available")
    fake_model.results.displacement.side_effect = RuntimeError("No displacement result available")

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
    from ansys_unified_mcp.tools import dpf_tools

    missing = tmp_path / "missing.rst"
    raw = dpf_tools.dpf_extract_structural_results(str(missing))
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert "RST file not found" in payload["error"]


def test_mcp_tool_dpf_get_model_summary_returns_json_envelope(tmp_path):
    from ansys_unified_mcp.tools import dpf_tools

    missing = tmp_path / "missing.rst"
    raw = dpf_tools.dpf_get_model_summary(str(missing))
    payload = json.loads(raw)
    assert payload["ok"] is False
    assert "RST file not found" in payload["error"]


def test_mcp_tool_dpf_extract_structural_results_success(tmp_path):
    from ansys_unified_mcp.tools import dpf_tools

    rst = tmp_path / "model.rst"
    rst.write_bytes(b"fake rst content")
    fake_dpf, _ = _build_fake_dpf_module()

    with patch.dict(sys.modules, {"ansys.dpf.core": fake_dpf}):
        raw = dpf_tools.dpf_extract_structural_results(str(rst), copy_to_sandbox=False)

    payload = json.loads(raw)
    assert payload["ok"] is True
    assert payload["metrics"]["num_nodes"] == 120
