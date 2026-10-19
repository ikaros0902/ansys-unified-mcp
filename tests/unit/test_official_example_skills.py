"""離線驗證官方範例路由與 Fluent 授權／階段邊界。"""
import builtins
import importlib.util
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

import pytest


ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "agents" / "skills"
SCRIPT = SKILLS / "ansys-fluent/scripts/run_mixing_elbow_e2e.py"
OFFICIAL_SKILLS = (
    "ansys-mechanical", "pymechanical-operations", "ansys-fluent",
    "ansys-geometry-modeling", "ansys-named-selection-rm-contact",
    "ansys-submodeling-dpf", "ansys-lsdyna", "ansys-optislang",
)


def load_script():
    spec = importlib.util.spec_from_file_location("mixing_elbow_example", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_import_does_not_load_product_or_create_files(monkeypatch, tmp_path):
    original = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name.startswith("ansys"):
            raise AssertionError("Import must not load an ANSYS product")
        return original(name, *args, **kwargs)

    work_dir = tmp_path / "scratch"
    work_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(work_dir)
    monkeypatch.setattr(builtins, "__import__", guarded_import)
    load_script()
    assert list(work_dir.iterdir()) == []


@pytest.mark.parametrize("skill", OFFICIAL_SKILLS)
def test_official_reference_is_reachable_and_nonempty(skill):
    reference = SKILLS / skill / "references/official_examples.md"
    assert reference.is_file() and reference.stat().st_size > 0
    assert "(references/official_examples.md)" in (SKILLS / skill / "SKILL.md").read_text(
        encoding="utf-8")


@pytest.fixture
def fake_fluent(monkeypatch):
    import sys

    module = ModuleType("ansys.fluent.core")
    module.examples = MagicMock()
    module.launch_fluent = MagicMock()
    monkeypatch.setitem(sys.modules, "ansys.fluent.core", module)
    # Python imports the parent package before resolving the substituted leaf.
    import ansys.fluent
    monkeypatch.setattr(ansys.fluent, "core", module, raising=False)
    return module


@pytest.mark.parametrize("kwargs", [
    {}, {"allow_launch": True},
    {"allow_launch": True, "allow_model_changes": True, "phase": "solve"},
])
def test_missing_authorization_has_no_side_effects(fake_fluent, tmp_path, kwargs):
    target_dir = tmp_path / "target"
    with pytest.raises(PermissionError):
        load_script().run_mixing_elbow_simulation(output_dir=target_dir / "output", **kwargs)
    fake_fluent.launch_fluent.assert_not_called()
    fake_fluent.examples.download_file.assert_not_called()
    assert not target_dir.exists() or list(target_dir.iterdir()) == []


@pytest.mark.parametrize("version", [251, 252, 261])
def test_prepare_writes_mesh_without_solver_calls(fake_fluent, tmp_path, version):
    geometry = tmp_path / "input.pmdb"
    geometry.write_bytes(b"geometry")
    session = fake_fluent.launch_fluent.return_value
    session.tui.file.write_mesh.side_effect = lambda path: Path(path).write_bytes(b"mesh")
    outputs = load_script().run_mixing_elbow_simulation(
        output_dir=tmp_path / "output", geometry_file=geometry, product_version=version,
        allow_launch=True, allow_model_changes=True)
    assert Path(outputs[0]).read_bytes() == b"mesh"
    session.settings.solution.initialization.hybrid_initialize.assert_not_called()
    session.settings.solution.run_calculation.iterate.assert_not_called()
    session.switch_to_solver.assert_not_called()
    session.exit.assert_called_once()
    if version == 261:
        session.watertight.assert_called_once_with(legacy=False)
        session.watertight.return_value.create_volume_mesh_wtm.assert_called_once_with()
        session.workflow.InitializeWorkflow.assert_not_called()
    else:
        session.watertight.assert_not_called()
        session.workflow.InitializeWorkflow.assert_called_once_with(
            WorkflowType="Watertight Geometry")
        session.workflow.TaskObject.__getitem__.assert_any_call("Generate the Volume Mesh")
    assert fake_fluent.launch_fluent.call_args.kwargs["product_version"] == version
    assert fake_fluent.launch_fluent.call_args.kwargs["ui_mode"] == "no_gui"


def test_solve_needs_case_and_preserves_existing_results(fake_fluent, tmp_path):
    script = load_script()
    kwargs = dict(phase="solve", allow_launch=True, allow_model_changes=True, allow_solve=True)
    with pytest.raises(ValueError, match="configured case"):
        script.run_mixing_elbow_simulation(output_dir=tmp_path, **kwargs)
    case = tmp_path / "input.cas.h5"
    case.write_bytes(b"configured")
    result = tmp_path / "mixing_elbow_solution.cas.h5"
    result.write_bytes(b"existing")
    with pytest.raises(FileExistsError):
        script.run_mixing_elbow_simulation(output_dir=tmp_path, case_file=case, **kwargs)
    assert result.read_bytes() == b"existing"
    fake_fluent.launch_fluent.assert_not_called()


def test_solve_runs_only_explicit_case_and_checks_both_outputs(fake_fluent, tmp_path):
    case = tmp_path / "input.cas.h5"
    case.write_bytes(b"configured")
    session = fake_fluent.launch_fluent.return_value

    def write_results(**kwargs):
        path = Path(kwargs["file_name"])
        path.write_bytes(b"case")
        path.with_name("mixing_elbow_solution.dat.h5").write_bytes(b"data")

    session.settings.file.write.side_effect = write_results
    outputs = load_script().run_mixing_elbow_simulation(
        output_dir=tmp_path / "output", phase="solve", case_file=case, iter_count=7,
        allow_launch=True, allow_model_changes=True, allow_solve=True)
    assert len(outputs) == 2 and all(Path(path).stat().st_size for path in outputs)
    session.settings.file.read.assert_called_once_with(file_type="case", file_name=str(case))
    session.settings.solution.run_calculation.iterate.assert_called_once_with(iter_count=7)
    fake_fluent.examples.download_file.assert_not_called()
    session.exit.assert_called_once()


def test_missing_output_fails_and_closes_session(fake_fluent, tmp_path):
    geometry = tmp_path / "input.pmdb"
    geometry.write_bytes(b"geometry")
    with pytest.raises(RuntimeError, match="nonempty output"):
        load_script().run_mixing_elbow_simulation(
            output_dir=tmp_path / "output", geometry_file=geometry,
            allow_launch=True, allow_model_changes=True)
    fake_fluent.launch_fluent.return_value.exit.assert_called_once()
