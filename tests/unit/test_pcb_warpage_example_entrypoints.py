from pathlib import Path
import runpy

import pytest


ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "docs" / "examples" / "pcb_warpage"
CANONICAL = ROOT / "agents" / "skills" / "materials-reliability" / "pcb-warpage-analysis" / "scripts"


@pytest.mark.parametrize(
    "name",
    [
        "01_build_pcb_geometry.py",
        "02_calculate_rom_materials.py",
        "run_full_warpage_workflow.py",
    ],
)
def test_example_entrypoint_delegates_to_canonical_skill_script(name, monkeypatch):
    calls = []
    monkeypatch.setattr(runpy, "run_path", lambda path, run_name: calls.append((path, run_name)))
    wrapper = EXAMPLES / name
    namespace = {"__name__": "__main__", "__file__": str(wrapper)}

    exec(compile(wrapper.read_text(encoding="utf-8"), str(wrapper), "exec"), namespace)

    assert calls == [(str(CANONICAL / name), "__main__")]


def test_canonical_workflow_defines_its_script_directory_without_running_workflow(monkeypatch):
    monkeypatch.delenv("PCB_STACKUP_DIR", raising=False)
    namespace = runpy.run_path(
        str(CANONICAL / "run_full_warpage_workflow.py"),
        run_name="pcb_warpage_import_check",
    )

    assert namespace["SCRIPT_DIR"] == str(CANONICAL)
    assert namespace["DEFAULT_FOLDER"] == namespace["SCRIPT_DIR"]
