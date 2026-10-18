"""Unit test guarding Rule 1: Strictly ASCII/English for all embedded ANSYS scripts.

Ensures that all embedded IronPython, APDL, and Workbench journal script templates
in products/mechanical contain only ASCII characters (ord(c) < 128) to prevent
interpreter encoding crashes.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path
import re
import pytest

from ansys_unified_mcp.products.mechanical import driver, facade, tools, session_ops, mesh_ops, scoping_ops, boundary_ops, solution_ops


def test_driver_wbjn_template_is_pure_ascii():
    """Verify that driver.py's prepare_job produces strictly ASCII script content."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        d = driver.MechanicalDriver(mode="workbench")
        job_dir = Path(tmpdir)
        script_path = d.prepare_job(job_dir, {"analysis_type": "static_structural"})
        assert script_path.exists()
        content = script_path.read_text(encoding="utf-8")
        non_ascii = [(i + 1, c, ord(c)) for i, c in enumerate(content) if ord(c) >= 128]
        assert not non_ascii, f"Found non-ASCII characters in generated .wbjn: {non_ascii}"


def test_driver_apdl_template_is_pure_ascii():
    """Verify that driver.py's MAPDL solve.dat is strictly ASCII."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        d = driver.MechanicalDriver(mode="mapdl")
        job_dir = Path(tmpdir)
        script_path = d.prepare_job(job_dir, {"analysis_type": "static_structural"})
        assert script_path.exists()
        content = script_path.read_text(encoding="utf-8")
        non_ascii = [(i + 1, c, ord(c)) for i, c in enumerate(content) if ord(c) >= 128]
        assert not non_ascii, f"Found non-ASCII characters in generated solve.dat: {non_ascii}"


def test_facade_embedded_scripts_are_pure_ascii():
    """Verify that facade.py embedded probe scripts are strictly ASCII."""
    src = inspect.getsource(facade)
    for match in re.finditer(r'run_script\(\s*(["\'])(.*?)\1', src, re.DOTALL):
        snippet = match.group(2)
        non_ascii = [c for c in snippet if ord(c) >= 128]
        assert not non_ascii, f"Found non-ASCII in facade run_script snippet: {non_ascii}"


def test_tools_embedded_scripts_are_pure_ascii():
    """Verify that all embedded IronPython scripts in tools.py are strictly ASCII."""
    src_file = Path(tools.__file__)
    tree = ast.parse(src_file.read_text(encoding="utf-8"))

    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            for part in node.values:
                if isinstance(part, ast.Constant) and isinstance(part.value, str):
                    for line in part.value.splitlines():
                        if "#" in line and any(ord(c) > 127 for c in line):
                            violations.append((node.lineno, line.strip()))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if "import " in node.value or "ExtAPI" in node.value:
                for line in node.value.splitlines():
                    if "#" in line and any(ord(c) > 127 for c in line):
                        violations.append((node.lineno, line.strip()))

    assert not violations, f"Found non-ASCII comments in tools.py scripts: {violations}"


@pytest.mark.parametrize(
    "mod",
    [session_ops, mesh_ops, scoping_ops, boundary_ops, solution_ops],
)
def test_mechanical_submodules_scripts_are_pure_ascii(mod):
    """Verify that all decomposed submodules in products/mechanical have strictly ASCII embedded scripts."""
    src_file = Path(mod.__file__)
    tree = ast.parse(src_file.read_text(encoding="utf-8"))

    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if "import " in node.value or "ExtAPI" in node.value:
                for line in node.value.splitlines():
                    if "#" in line and any(ord(c) > 127 for c in line):
                        violations.append((node.lineno, line.strip()))

    assert not violations, f"Found non-ASCII comments in {mod.__name__} scripts: {violations}"
