# -*- coding: utf-8 -*-
"""Empirical Challenger Test Suite for ANSYS Icepak Driver.

This suite is authored by Challenger M1-1 (teamwork_preview_challenger) to
adversarially stress-test and empirically challenge the Icepak driver:
1. Physical temperature variation across varying ambient temperatures & chip powers (synthetic mode).
2. Verification that temperatures are strictly dynamic/physical and never hardcoded to 85.4.
3. Strict requirement of SolverDriverError when allow_synthetic=False and icepak.exe is absent.
4. Repo-wide verification that no 85.4 hardcoded fake temperatures remain.
5. End-to-end execution of synthetic batch script and artifact extraction.
6. Edge case mining: zero power, extreme high power (FAIL verdict check), negative ambient.
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest

from ansys_unified_mcp.drivers.base import SolverDriverError
from ansys_unified_mcp.drivers.icepak_driver import IcepakDriver
from ansys_unified_mcp.jobs.models import (
    ExecutionMetadata,
    PhysicalMetrics,
    SimulationSummary,
    VerdictEnum,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_ROOT = REPO_ROOT / "src"


class TestRepoWideHardcodedTemperatureScan:
    """Scan all Python source files in the repository to ensure no hardcoded 85.4 fake temperatures exist."""

    def test_no_85_4_in_src_py_files(self) -> None:
        """Scan all .py files in src/ to ensure '85.4' is completely absent."""
        found: List[str] = []
        for py_path in SRC_ROOT.rglob("*.py"):
            text = py_path.read_text(encoding="utf-8", errors="ignore")
            if "85.4" in text:
                found.append(str(py_path.relative_to(REPO_ROOT)))

        assert not found, f"Found forbidden hardcoded '85.4' in source files: {found}"

    def test_icepak_driver_source_contains_no_85_4(self) -> None:
        """Ensure icepak_driver.py source has 0 occurrences of '85.4'."""
        driver_path = SRC_ROOT / "ansys_unified_mcp" / "drivers" / "icepak_driver.py"
        assert driver_path.exists()
        text = driver_path.read_text(encoding="utf-8")
        assert "85.4" not in text, "icepak_driver.py must not contain '85.4' anywhere"


class TestIcepakDriverStrictRefusal:
    """Stress-test strict refusal behavior when real icepak.exe is absent and allow_synthetic=False."""

    @pytest.fixture
    def mock_unavailable_driver(self) -> IcepakDriver:
        """Create an IcepakDriver forced to report unavailable."""
        driver = IcepakDriver(solver_bin=None)
        driver.is_available = lambda: False  # type: ignore[assignment]
        return driver

    def test_prepare_job_strictly_raises_without_allow_synthetic(
        self, tmp_path: Path, mock_unavailable_driver: IcepakDriver
    ) -> None:
        """Default config without allow_synthetic must raise SolverDriverError."""
        job_dir = tmp_path / "job_refuse_default"
        with pytest.raises(SolverDriverError) as exc_info:
            mock_unavailable_driver.prepare_job(job_dir, {"ambient_temperature_c": 25.0, "chip_power_w": 50.0})
        assert "allow_synthetic=True" in str(exc_info.value)
        assert not (job_dir / "workspace" / "icepak_batch.py").exists()

    def test_prepare_job_strictly_raises_with_explicit_false(
        self, tmp_path: Path, mock_unavailable_driver: IcepakDriver
    ) -> None:
        """Explicit allow_synthetic=False must raise SolverDriverError."""
        job_dir = tmp_path / "job_refuse_false"
        with pytest.raises(SolverDriverError) as exc_info:
            mock_unavailable_driver.prepare_job(
                job_dir,
                {"ambient_temperature_c": 30.0, "chip_power_w": 40.0, "allow_synthetic": False},
            )
        assert "allow_synthetic=True" in str(exc_info.value)
        assert not (job_dir / "workspace" / "icepak_batch.py").exists()

    @pytest.mark.parametrize("falsy_val", [None, 0, "", [], {}])
    def test_prepare_job_strictly_raises_with_falsy_values(
        self, tmp_path: Path, mock_unavailable_driver: IcepakDriver, falsy_val: Any
    ) -> None:
        """Falsy values of allow_synthetic must not grant synthetic execution."""
        job_dir = tmp_path / f"job_refuse_falsy_{type(falsy_val).__name__}"
        with pytest.raises(SolverDriverError):
            mock_unavailable_driver.prepare_job(
                job_dir,
                {"ambient_temperature_c": 25.0, "chip_power_w": 45.0, "allow_synthetic": falsy_val},
            )

    def test_build_command_rejects_unmarked_script(
        self, tmp_path: Path, mock_unavailable_driver: IcepakDriver
    ) -> None:
        """build_command must refuse to run a non-synthetic script via python when real solver is absent."""
        unmarked_script = tmp_path / "custom_script.py"
        unmarked_script.write_text("print('hello')", encoding="utf-8")
        with pytest.raises(SolverDriverError) as exc_info:
            mock_unavailable_driver.build_command(unmarked_script)
        assert "拒絕以 Python 解譯器直接執行" in str(exc_info.value)

    def test_build_command_allows_synthetic_script_with_extra_args(
        self, tmp_path: Path, mock_unavailable_driver: IcepakDriver
    ) -> None:
        """build_command should append extra_args when executing synthetic scripts."""
        script = tmp_path / "synthetic_script.py"
        script.write_text("# WARNING: SYNTHETIC TEST DATA\nprint('run')", encoding="utf-8")
        cmd = mock_unavailable_driver.build_command(script, extra_args=["--foo", "bar"])
        assert cmd == [sys.executable, str(script), "--foo", "bar"]


class TestIcepakDriverSyntheticPhysicalVariation:
    """Empirically test physical temperature variation and absence of hardcoded values."""

    @pytest.fixture
    def mock_driver(self) -> IcepakDriver:
        driver = IcepakDriver(solver_bin=None)
        driver.is_available = lambda: False  # type: ignore[assignment]
        return driver

    @pytest.mark.parametrize(
        "ambient_c, power_w",
        [
            (-40.0, 10.0),    # Sub-zero industrial testing
            (0.0, 20.0),
            (25.0, 0.0),      # Zero power edge case
            (25.0, 15.0),
            (25.0, 45.0),     # Baseline standard case
            (25.0, 80.0),
            (40.0, 30.0),
            (50.0, 50.0),
            (60.0, 120.0),    # High temp & high power (triggers FAIL verdict)
        ],
    )
    def test_parametric_physical_variation_and_execution(
        self, tmp_path: Path, mock_driver: IcepakDriver, ambient_c: float, power_w: float
    ) -> None:
        """Empirically execute synthetic simulation across various ambient temps & powers.

        Verifies:
        1. Generated batch script contains NO '85.4'.
        2. Execution runs to completion (exit code 0).
        3. Parsed log progress reaches 100% and converged.
        4. Node temperatures in CSV follow physical decay and are never 85.4.
        5. Peak temperature strictly equals round(ambient_c + power_w * 1.55, 1).
        6. Summary metadata properly records is_synthetic=True and mock_reason.
        """
        job_dir = tmp_path / f"job_amb{ambient_c}_pwr{power_w}"
        job_dir.mkdir(parents=True, exist_ok=True)
        inputs_dir = job_dir / "inputs"
        inputs_dir.mkdir(parents=True, exist_ok=True)
        config = {
            "ambient_temperature_c": ambient_c,
            "chip_power_w": power_w,
            "allow_synthetic": True,
        }
        (inputs_dir / "job_config.json").write_text(json.dumps(config), encoding="utf-8")

        # 1. Prepare job
        script_path = mock_driver.prepare_job(job_dir, config)
        assert script_path.exists()
        script_text = script_path.read_text(encoding="utf-8")
        assert "85.4" not in script_text, f"Batch script contains 85.4 for amb={ambient_c}, pwr={power_w}"

        # 2. Build command and actually run it via subprocess
        cmd = mock_driver.build_command(script_path)
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(job_dir / "workspace"))
        assert proc.returncode == 0, f"Synthetic script failed with stderr: {proc.stderr}"

        # 3. Parse progress from generated log
        progress = mock_driver.parse_progress(job_dir)
        assert progress["is_converged"] is True
        assert progress["progress_pct"] == 100.0
        expected_log_max_t = round(ambient_c + (power_w * 1.6), 2)
        assert abs(progress["max_temperature_c"] - expected_log_max_t) < 0.1

        # 4. Extract artifacts and inspect CSV data
        artifacts = mock_driver.extract_artifacts(job_dir)
        assert artifacts["is_synthetic"] is True
        assert artifacts["mock_reason"] == "NO_ICEPAK_SOLVER_DETECTED"

        expected_max_t = round(ambient_c + power_w * 1.55, 1)
        assert abs(artifacts["max_temperature_c"] - expected_max_t) < 1e-4

        csv_path = job_dir / "workspace" / "temperature_field.csv"
        assert csv_path.exists()
        csv_content = csv_path.read_text(encoding="utf-8")
        assert "85.4" not in csv_content, f"Generated CSV contains 85.4 for amb={ambient_c}, pwr={power_w}!"

        # Read CSV rows and analyze temperature distribution
        rows = [r for r in csv_content.splitlines() if not r.startswith("#") and r.strip()]
        reader = list(csv.DictReader(rows))
        assert len(reader) == 100, f"Expected 100 nodes, got {len(reader)}"

        temps = [float(r["Temperature_C"]) for r in reader]
        assert all(t != 85.4 for t in temps), "A node temperature was exactly 85.4!"

        # Physical consistency checks:
        if power_w > 0:
            # All nodes must be >= ambient temperature
            assert all(t >= ambient_c for t in temps), "Thermal law violation: node colder than ambient!"
            # Nodal peak: grid center at (0.0225, 0.0225) falls between nodes at 0.020 and 0.025,
            # so max discrete node temperature is ambient + delta_t_max * (80/81).
            expected_node_max = round(ambient_c + power_w * 1.55 * (80.0 / 81.0), 2)
            assert abs(max(temps) - expected_node_max) <= 0.02
            # Center nodes must be hotter than corner nodes
            corner_temp = temps[0]  # node 1 at (0.0, 0.0)
            assert corner_temp < max(temps), "Center should be hotter than corners"
        else:
            # Zero power: all nodes must exactly equal ambient temperature
            assert all(t == ambient_c for t in temps), "Zero power must yield isothermal ambient field"

        # Check verdict threshold (105.0 C)
        if expected_max_t < 105.0:
            assert artifacts["verdict"] == VerdictEnum.PASS.value
        else:
            assert artifacts["verdict"] == VerdictEnum.FAIL.value

    def test_monotonicity_across_power_and_ambient(
        self, tmp_path: Path, mock_driver: IcepakDriver
    ) -> None:
        """Verify that temperature strictly monotonically increases with power and ambient."""
        ambient = 25.0
        powers = [10.0, 30.0, 50.0, 70.0]
        max_temps_power: List[float] = []

        for p in powers:
            job_dir = tmp_path / f"job_mono_p_{p}"
            job_dir.mkdir(parents=True, exist_ok=True)
            inputs_dir = job_dir / "inputs"
            inputs_dir.mkdir(parents=True, exist_ok=True)
            cfg = {"ambient_temperature_c": ambient, "chip_power_w": p, "allow_synthetic": True}
            (inputs_dir / "job_config.json").write_text(json.dumps(cfg), encoding="utf-8")
            mock_driver.prepare_job(job_dir, cfg)
            res = mock_driver.extract_artifacts(job_dir)
            max_temps_power.append(res["max_temperature_c"])

        # Strictly increasing with power
        for i in range(len(max_temps_power) - 1):
            assert max_temps_power[i + 1] > max_temps_power[i], (
                f"Power monotonicity violated: {max_temps_power[i]} >= {max_temps_power[i + 1]}"
            )

        # Strictly increasing with ambient
        power = 40.0
        ambients = [15.0, 25.0, 35.0, 45.0]
        max_temps_amb: List[float] = []

        for a in ambients:
            job_dir = tmp_path / f"job_mono_a_{a}"
            job_dir.mkdir(parents=True, exist_ok=True)
            inputs_dir = job_dir / "inputs"
            inputs_dir.mkdir(parents=True, exist_ok=True)
            cfg = {"ambient_temperature_c": a, "chip_power_w": power, "allow_synthetic": True}
            (inputs_dir / "job_config.json").write_text(json.dumps(cfg), encoding="utf-8")
            mock_driver.prepare_job(job_dir, cfg)
            res = mock_driver.extract_artifacts(job_dir)
            max_temps_amb.append(res["max_temperature_c"])

        for i in range(len(max_temps_amb) - 1):
            assert max_temps_amb[i + 1] > max_temps_amb[i], (
                f"Ambient monotonicity violated: {max_temps_amb[i]} >= {max_temps_amb[i + 1]}"
            )

    def test_summary_json_lifecycle_in_synthetic_mode(
        self, tmp_path: Path, mock_driver: IcepakDriver
    ) -> None:
        """Verify that existing summary.json is correctly updated with execution metadata."""
        job_dir = tmp_path / "job_summary_test"
        job_dir.mkdir(parents=True, exist_ok=True)
        artifacts_dir = job_dir / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        inputs_dir = job_dir / "inputs"
        inputs_dir.mkdir(parents=True, exist_ok=True)

        config = {"ambient_temperature_c": 25.0, "chip_power_w": 50.0, "allow_synthetic": True}
        (inputs_dir / "job_config.json").write_text(json.dumps(config), encoding="utf-8")

        # Create a pre-existing summary.json
        init_summary = SimulationSummary(
            job_id="test_icepak_job",
            workflow_type="thermal_analysis",
            execution=ExecutionMetadata(
                created_at="2026-09-23T05:00:00Z",
                solver_name="ANSYS Icepak",
                is_synthetic=False,
                mock_reason=None,
            ),
        )
        summary_file = artifacts_dir / "summary.json"
        summary_file.write_text(init_summary.model_dump_json(), encoding="utf-8")

        mock_driver.prepare_job(job_dir, config)
        res = mock_driver.extract_artifacts(job_dir)

        # Inspect updated summary.json
        updated = SimulationSummary.model_validate_json(summary_file.read_text(encoding="utf-8"))
        assert updated.execution.is_synthetic is True
        assert updated.execution.mock_reason == "NO_ICEPAK_SOLVER_DETECTED"
        assert updated.verdict == VerdictEnum.PASS
        assert "temperature_contour" in updated.artifacts
        assert "temperature_field_csv" in updated.artifacts

    def test_overheating_verdict_failure(
        self, tmp_path: Path, mock_driver: IcepakDriver
    ) -> None:
        """Verify that junction temperature exceeding 105 C marks FAIL and records reason."""
        job_dir = tmp_path / "job_overheating"
        job_dir.mkdir(parents=True, exist_ok=True)
        inputs_dir = job_dir / "inputs"
        inputs_dir.mkdir(parents=True, exist_ok=True)
        artifacts_dir = job_dir / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        # Ambient 50 C, Power 80 W -> max_temp_c = 50 + 80*1.55 = 174.0 C (> 105.0)
        config = {"ambient_temperature_c": 50.0, "chip_power_w": 80.0, "allow_synthetic": True}
        (inputs_dir / "job_config.json").write_text(json.dumps(config), encoding="utf-8")

        init_summary = SimulationSummary(
            job_id="test_overheat_job",
            workflow_type="thermal_analysis",
            execution=ExecutionMetadata(
                created_at="2026-09-23T05:00:00Z",
                solver_name="ANSYS Icepak",
            ),
        )
        (artifacts_dir / "summary.json").write_text(init_summary.model_dump_json(), encoding="utf-8")

        mock_driver.prepare_job(job_dir, config)
        res = mock_driver.extract_artifacts(job_dir)

        assert res["verdict"] == VerdictEnum.FAIL.value
        assert res["max_temperature_c"] == 174.0

        updated_summary = SimulationSummary.model_validate_json(
            (artifacts_dir / "summary.json").read_text(encoding="utf-8")
        )
        assert updated_summary.verdict == VerdictEnum.FAIL
        assert any("晶片最高結溫超標" in r for r in updated_summary.failure_reasons)
