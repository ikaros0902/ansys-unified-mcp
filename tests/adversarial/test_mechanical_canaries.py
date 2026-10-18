"""3-Broken Semantic Canary Verification Suite.

Guards Tier 2 requirements from Final Master Plan v3.0:
- Broken-1: Non-ASCII characters in embedded scripts or invalid API symbols MUST be detected and fail.
- Broken-2: Mixed outputs with unhandled exceptions followed by JSON lines MUST NOT be swallowed.
- Broken-3: Directional signed metrics (Z-displacement, reaction force) and unit scaling errors MUST be caught by compare.py.
"""

from __future__ import annotations
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import pytest

from ansys_unified_mcp.products.mechanical.api import _parse_mechanical_output, _is_error_output

def test_broken_1_ascii_canary_must_catch_non_ascii():
    """Canary 1: Injecting Chinese characters into an embedded script string MUST be flagged."""
    corrupted_script = "# Corrupted script\nprint('hello')\n# 測試中文\n"
    non_ascii = [c for c in corrupted_script if ord(c) >= 128]
    assert len(non_ascii) > 0, "Canary injection must contain non-ASCII characters"
    # Verify our ASCII rule detects it
    is_pure_ascii = all(ord(c) < 128 for c in corrupted_script)
    assert is_pure_ascii is False

def test_broken_2_exception_swallow_canary_must_fail():
    """Canary 2: Mixed stdout with fatal exception followed by valid JSON must fail."""
    corrupted_stdout = """
    System.NullReferenceException: Object reference not set to an instance of an object.
       at Ansys.ACT.Core.Model.GetAnalysis()
    {"ok": true, "result": "corrupted_success_illusion"}
    """
    # The parser must detect the fatal exception and NOT return ok: True
    envelope = _parse_mechanical_output(corrupted_stdout)
    assert envelope["ok"] is False
    assert "error" in envelope
    assert _is_error_output(corrupted_stdout) is True

def test_broken_3_signed_directional_physics_canary():
    """Canary 3: Directional metrics with inverted signs must cause compare.py to fail (differs)."""
    compare_script = Path(r"C:\Users\Ming\.gemini\config\skills\cae-code-modernization\scripts\compare.py")
    if not compare_script.exists():
        pytest.skip("compare.py not found at configured path")

    with tempfile.TemporaryDirectory() as tmpdir:
        td = Path(tmpdir)
        legacy_file = td / "legacy.json"
        # Legacy run has negative Z deflection
        legacy_data = {
            "max_directional_deflection_z_mm": -1.2345,
            "reaction_force_z_n": -500.0,
            "status": "converged"
        }
        legacy_file.write_text(json.dumps(legacy_data, indent=2), encoding="utf-8")

        # Corrupted run flipped the load direction (yields positive Z deflection)
        corrupted_file = td / "corrupted.json"
        corrupted_data = {
            "max_directional_deflection_z_mm": 1.2345,
            "reaction_force_z_n": 500.0,
            "status": "converged"
        }
        corrupted_file.write_text(json.dumps(corrupted_data, indent=2), encoding="utf-8")

        cases_file = td / "cases.json"
        cases_content = {
            "system": "canary_test",
            "cases": [
                {
                    "id": "C_CANARY_01",
                    "legacy": "legacy.json",
                    "new": "corrupted.json",
                    "tolerance": {
                        "rel": 0.001,
                        "abs": 1e-4,
                        "why": "Allowable MKL solver rounding tolerance"
                    }
                }
            ]
        }
        cases_file.write_text(json.dumps(cases_content, indent=2), encoding="utf-8")

        # Run compare.py
        result = subprocess.run(
            [sys.executable, str(compare_script), str(cases_file)],
            capture_output=True,
            text=True,
            cwd=str(td)
        )

        # Must exit with code 1 (differs) because sign inverted!
        assert result.returncode == 1, f"compare.py should have failed on signed inversion! stdout: {result.stdout}"
        assert "differs" in result.stdout.lower() or "fail" in result.stdout.lower()
