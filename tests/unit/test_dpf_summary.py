"""以禁止全場資料下載的 fake 驗證 DPF 摘要資料流。"""

import math
import types
from unittest.mock import MagicMock

import pytest

from ansys_unified_mcp.analytics.postprocessing.dpf_summary import extract_summary


class Field:
    def __init__(self, values, unit, reduced=False):
        self.values = values
        self.unit = unit
        self.location = "Nodal"
        self.elementary_data_count = len(values)
        self._server = None
        self.reduced = reduced

    @property
    def data(self):
        assert self.reduced, "不得下載全場 data"
        return self.values


class Container(list):
    def get_label_space(self, index):
        return {"time": 3}


def build_fake(stress=None, displacement=None, stress_unit="Pa", disp_unit="m"):
    stress = [10.0, 25.5, 15.0] if stress is None else stress
    displacement = [[0.5, 0, 0], [0, 1.2, 0], [0, 0, 0.8]] if displacement is None else displacement
    def output(fc):
        return types.SimpleNamespace(outputs=types.SimpleNamespace(fields_container=lambda: fc))

    def transform(fields_container, fn, **kwargs):
        return output(Container(Field([fn(v) for v in f.values], f.unit) for f in fields_container))

    def equivalent(v):
        if not isinstance(v, (list, tuple)):
            return v
        x, y, z, xy, yz, xz = v
        return math.sqrt(((x-y)**2 + (y-z)**2 + (z-x)**2)/2 + 3*(xy*xy+yz*yz+xz*xz))

    def extrema(field, **kwargs):
        return types.SimpleNamespace(outputs=types.SimpleNamespace(
            field_min=lambda: Field([min(field.values)], field.unit, True),
            field_max=lambda: Field([max(field.values)], field.unit, True)))

    fake = types.ModuleType("ansys.dpf.core")
    fake.operators = types.SimpleNamespace(
        invariant=types.SimpleNamespace(von_mises_eqv_fc=MagicMock(side_effect=lambda **kw: transform(fn=equivalent, **kw))),
        math=types.SimpleNamespace(
            norm_fc=MagicMock(side_effect=lambda **kw: transform(fn=lambda v: math.sqrt(sum(x*x for x in v)), **kw)),
            accumulate=MagicMock(side_effect=lambda fieldA, **kw: types.SimpleNamespace(outputs=types.SimpleNamespace(
                field=lambda: Field([sum(fieldA.values)], fieldA.unit, True))))),
        min_max=types.SimpleNamespace(min_max=MagicMock(side_effect=extrema)),
        logic=types.SimpleNamespace(component_selector_fc=MagicMock(side_effect=lambda component_number, **kw: transform(fn=lambda v: v[component_number], **kw))))
    times = types.SimpleNamespace(data=[0.0, 0.1, 0.2], scoping=types.SimpleNamespace(ids=[1, 2, 3]))
    metadata = types.SimpleNamespace(
        result_info=types.SimpleNamespace(available_results=[types.SimpleNamespace(name=n) for n in ("stress", "displacement")]),
        time_freq_support=types.SimpleNamespace(time_frequencies=times),
        release_streams=MagicMock(),
        meshed_region=types.SimpleNamespace(nodes=types.SimpleNamespace(n_nodes=120), elements=types.SimpleNamespace(n_elements=40)))
    results = types.SimpleNamespace(
        stress=MagicMock(return_value=output(Container([Field(stress, stress_unit)]))),
        displacement=MagicMock(return_value=output(Container([Field(displacement, disp_unit)]))))
    model = types.SimpleNamespace(metadata=metadata, results=results, _server=None)
    fake.Model = MagicMock(return_value=model)
    return fake, model


def test_hydrostatic_tensor_has_zero_von_mises():
    dpf, model = build_fake(stress=[[100, 100, 100, 0, 0, 0]])
    result = extract_summary(model, dpf)
    assert result["stress_von_mises"]["max"] == 0
    assert result["stress_von_mises"]["set_ids"] == [3]
    assert result["stress_von_mises"]["locations"] == ["Nodal"]
    model.results.stress.assert_called_once_with(time_scoping=[3])
    dpf.operators.invariant.von_mises_eqv_fc.assert_called_once()


@pytest.mark.parametrize("su,du,factor_s,factor_d", [("Pa", "m", 1, 1), ("MPa", "mm", 1e6, 1e-3)])
def test_si_conversion_and_summary(su, du, factor_s, factor_d):
    dpf, model = build_fake(stress=[1, 3], displacement=[[-3, 4, 0]], stress_unit=su, disp_unit=du)
    result = extract_summary(model, dpf)
    assert result["stress_von_mises"]["avg"] == 2 * factor_s
    assert result["stress_von_mises"]["max"] == 3 * factor_s
    assert result["displacement"]["total_max"] == 5 * factor_d
    assert result["displacement"]["ux_max"] == 3 * factor_d


@pytest.mark.parametrize("kwargs", [{"stress_unit": "psi"}, {"disp_unit": "inch"}, {"stress_unit": ""}])
def test_unknown_units_fail(kwargs):
    dpf, model = build_fake(**kwargs)
    with pytest.raises(ValueError, match="Unknown DPF unit"):
        extract_summary(model, dpf)


def test_empty_and_missing_are_distinct():
    dpf, model = build_fake(stress=[])
    model.metadata.result_info.available_results = [types.SimpleNamespace(name="stress")]
    result = extract_summary(model, dpf)
    assert result["stress_von_mises"]["status"] == "empty"
    assert result["stress_von_mises"]["max"] is None
    assert result["displacement"]["status"] == "missing"
    assert result["displacement"]["total_max"] is None
    model.results.displacement.assert_not_called()


def test_reader_and_controller_use_identical_summary(tmp_path):
    from ansys_unified_mcp.analytics.postprocessing.dpf_reader import DPFSandboxReader
    from ansys_unified_mcp.products.dpf.facade import DPFController
    from unittest.mock import patch
    from tests.unit.test_dpf_reader import create_mock_summary

    create_mock_summary(tmp_path, "SOLVED")
    rst = tmp_path / "file.rst"
    rst.write_bytes(b"source")
    fake, model = build_fake(stress=[[100, 100, 100, 0, 0, 0]], stress_unit="MPa", disp_unit="mm")
    with patch.dict("sys.modules", {"ansys.dpf.core": fake}):
        reader_result = DPFSandboxReader().read_results(tmp_path)
        controller_result = DPFController().extract_structural_results(rst, copy_to_sandbox=False)
    assert controller_result["ok"] is True
    assert reader_result["stress_von_mises"] == controller_result["results"]["stress_von_mises"]
    assert reader_result["displacement"] == controller_result["results"]["displacement"]
    assert model.metadata.release_streams.call_count == 2
