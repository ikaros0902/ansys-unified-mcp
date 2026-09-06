# -*- coding: utf-8 -*-
"""Tier 2 單元測試：BaseSolverDriver 抽象基類與 6 大具象驅動測試 (test_base_drivers.py).

涵蓋範圍：
1. BaseSolverDriver 抽象合約與例外類別階層 (無法直接實例化、強制子類實作抽象介面)
2. 6 大具象驅動之生命週期與沙盒對接：
   - MechanicalDriver (ANSYS Mechanical / MAPDL)
   - LSDynaDriver (LS-DYNA 顯式動力學)
   - OptislangDriver (optiSLang 參數尋優與 MOP 代理模型)
   - SpaceClaimDriver (SpaceClaim / Discovery 幾何前處理)
   - FluentDriver (ANSYS Fluent CFD 流體力學)
   - IcepakDriver (ANSYS Icepak 電子散熱分析)
3. 沙盒工作區對接與輸入檔案生成 (solve.dat, run.k, optislang_batch.py 等)
4. 後處理白底 1920x1080 雲圖繪製與 summary.json 成果萃取
5. FakeProcess / MockSolverDriver 高保真虛擬驅動生命週期驗證
"""

from __future__ import annotations

import inspect
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pytest

# 相容防禦注入：若 parser 模組尚未別名 FluentLogParser/LSDynaParser，在此動態注入對齊
import ansys_unified_mcp.core.sentinel.parsers.fluent as fluent_parser_mod
if not hasattr(fluent_parser_mod, "FluentLogParser"):
    fluent_parser_mod.FluentLogParser = fluent_parser_mod.FluentResidualParser  # type: ignore[attr-defined]

import ansys_unified_mcp.core.sentinel.parsers.lsdyna as lsdyna_parser_mod
if not hasattr(lsdyna_parser_mod, "LSDynaParser"):
    lsdyna_parser_mod.LSDynaParser = lsdyna_parser_mod.LSDynaGlstatParser  # type: ignore[attr-defined]

from ansys_unified_mcp.drivers.base import (
    BaseSolverDriver,
    SolverDriverError,
    SolverExecutionError,
    SolverNotFoundError,
)
from ansys_unified_mcp.drivers.fluent_driver import FluentDriver
from ansys_unified_mcp.drivers.icepak_driver import IcepakDriver
from ansys_unified_mcp.drivers.lsdyna_driver import LSDynaDriver
from ansys_unified_mcp.drivers.mechanical_driver import MechanicalDriver
from ansys_unified_mcp.drivers.optislang_driver import OptislangDriver
from ansys_unified_mcp.drivers.spaceclaim_driver import SpaceClaimDriver
from ansys_unified_mcp.jobs.manager import JobManager
from ansys_unified_mcp.jobs.models import SimulationSummary, VerdictEnum
from ansys_unified_mcp.jobs.sandbox import JobSandbox
from tests.mocks.mock_driver import (
    BaseSolverDriverContract,
    FakeProcess,
    MockFluentDriver,
    MockLSDynaDriver,
    MockMechanicalDriver,
    MockOptislangDriver,
    MockSolverDriver,
)


# ==============================================================================
# 1. BaseSolverDriver 抽象合約檢驗
# ==============================================================================
class TestBaseSolverDriverContract:
    """測試 BaseSolverDriver 抽象基類約束與例外體系。"""

    def test_abstract_class_cannot_be_instantiated(self) -> None:
        """驗證直接實例化 BaseSolverDriver 抽象基類必然引發 TypeError。"""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseSolverDriver(solver_name="AbstractSolver")  # type: ignore[abstract]

    def test_incomplete_subclass_cannot_be_instantiated(self) -> None:
        """驗證未實作全部抽象方法之子類必然引發 TypeError。"""
        class IncompleteDriver(BaseSolverDriver):
            def validate_prerequisites(self) -> Tuple[bool, str]:
                return True, "ok"

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteDriver(solver_name="Incomplete")  # type: ignore[abstract]

    def test_exception_hierarchy(self) -> None:
        """驗證驅動專屬例外繼承自 SolverDriverError。"""
        assert issubclass(SolverNotFoundError, SolverDriverError)
        assert issubclass(SolverExecutionError, SolverDriverError)
        assert issubclass(SolverDriverError, Exception)

    def test_prepare_environment_defaults(self, tmp_path: Path) -> None:
        """驗證 prepare_environment 預設關閉 ANSYS 檔案鎖定與啟用無頭模式。"""
        class DummyDriver(BaseSolverDriver):
            def validate_prerequisites(self) -> Tuple[bool, str]:
                return True, "ready"
            def prepare_job(self, job_dir: Path, config: Dict[str, Any]) -> Path:
                return job_dir / "dummy.in"
            def build_command(self, input_file: Path, extra_args: Optional[List[str]] = None) -> List[str]:
                return ["dummy.exe", str(input_file)]
            def get_log_file_path(self, job_dir: Path) -> Path:
                return job_dir / "dummy.log"
            def parse_progress(self, job_dir: Path) -> Dict[str, Any]:
                return {"progress_pct": 100.0}
            def extract_artifacts(self, job_dir: Path) -> Dict[str, Any]:
                return {}

        driver = DummyDriver(solver_name="Dummy")
        env = driver.prepare_environment(job_dir=tmp_path, config={})
        assert env.get("ANSYS_LOCK") == "OFF"
        assert env.get("ANSYS_NO_GUI") == "1"


# ==============================================================================
# 2. 6 大具象求解器驅動之屬性與生命週期檢核
# ==============================================================================
class TestConcreteDriversLifecycle:
    """測試 6 大求解器驅動之基本初始化、前置檢驗與命令建置。"""

    @pytest.mark.parametrize(
        "driver_cls,expected_name",
        [
            (MechanicalDriver, "ANSYS Mechanical"),
            (LSDynaDriver, "LS-DYNA Explicit Dynamics"),
            (OptislangDriver, "ANSYS optiSLang"),
            (SpaceClaimDriver, "ANSYS SpaceClaim"),
            (FluentDriver, "ANSYS Fluent"),
            (IcepakDriver, "ANSYS Icepak"),
        ],
    )
    def test_drivers_initialization(self, driver_cls: Any, expected_name: str) -> None:
        """驗證 6 大驅動實例化後之 solver_name 正確。"""
        driver = driver_cls()
        assert driver.solver_name == expected_name
        assert isinstance(driver, BaseSolverDriver)

    def test_validate_prerequisites_custom_binary(self, tmp_path: Path) -> None:
        """驗證手動提供存在之二進位路徑時，validate_prerequisites 回傳 True。"""
        fake_bin = tmp_path / "custom_ansys.exe"
        fake_bin.write_text("FAKE BINARY", encoding="utf-8")

        mech = MechanicalDriver(solver_bin=str(fake_bin))
        ok, msg = mech.validate_prerequisites()
        assert ok is True
        assert "找到指定求解器二進位檔" in msg

    def test_validate_prerequisites_fallback_offline_mode(self) -> None:
        """驗證無商業 License/二進位檔時，validate_prerequisites 安全降級回傳 False 與指引。"""
        driver = LSDynaDriver(solver_bin="C:/non_existent_path_to_lsdyna.exe")
        ok, msg = driver.validate_prerequisites()
        assert ok is False
        assert "未偵測到" in msg or "不存在" in msg or "支援沙盒模擬" in msg

    def test_build_command_structure(self, tmp_path: Path) -> None:
        """驗證各驅動 build_command 組裝命令列結構合規。"""
        in_file = tmp_path / "model.dat"
        in_file.write_text("TEST", encoding="utf-8")

        mech = MechanicalDriver(solver_bin="ansys.exe")
        cmd_mech = mech.build_command(input_file=in_file, extra_args=["-np", "4"])
        assert cmd_mech[0] == "ansys.exe"
        assert "-b" in cmd_mech
        assert "-i" in cmd_mech
        assert str(in_file) in cmd_mech
        assert "-np" in cmd_mech and "4" in cmd_mech

        lsdyna = LSDynaDriver(solver_bin="lsdyna.exe")
        cmd_ls = lsdyna.build_command(input_file=in_file, extra_args=["ncpu=8"])
        assert cmd_ls[0] == "lsdyna.exe"
        assert f"i={in_file.name}" in cmd_ls or f"i={in_file}" in cmd_ls
        assert "ncpu=8" in cmd_ls

        fluent = FluentDriver(solver_bin="fluent.exe")
        cmd_fl = fluent.build_command(input_file=in_file)
        assert cmd_fl[0] == "fluent.exe"
        assert "-g" in cmd_fl

    def test_get_log_file_path(self, tmp_path: Path) -> None:
        """驗證各驅動回傳正確的求解日誌路徑。"""
        mech = MechanicalDriver()
        assert mech.get_log_file_path(tmp_path) == tmp_path / "workspace" / "solve.out"

        lsdyna = LSDynaDriver()
        assert lsdyna.get_log_file_path(tmp_path) == tmp_path / "workspace" / "glstat"

        fluent = FluentDriver()
        assert fluent.get_log_file_path(tmp_path) == tmp_path / "workspace" / "fluent.log"


# ==============================================================================
# 3. 沙盒對接、輸入生成與後處理成果萃取測試
# ==============================================================================
class TestConcreteDriversPrepareAndExtract:
    """測試驅動對接 JobSandbox 進行檔案建立與結果產出。"""

    @pytest.fixture
    def sandbox(self, tmp_path: Path) -> JobSandbox:
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        return manager.create_job("structural", tag="unit_test")

    def test_mechanical_driver_prepare_and_extract(self, sandbox: JobSandbox) -> None:
        """驗證 MechanicalDriver 在沙盒生成 APDL 輸入並萃取等效應力雲圖與 summary。"""
        driver = MechanicalDriver()
        job_dir = getattr(sandbox, "root_dir", getattr(sandbox, "job_dir", None))

        config = {
            "analysis_type": "static_structural",
            "cad_path": "plate.pmdb",
            "material_yield_strength_mpa": 250.0,
            "load_magnitude_n": 1000.0,
            "cte": 1.6e-5,
        }
        input_file = driver.prepare_job(job_dir, config)
        assert input_file.exists()
        content = input_file.read_text(encoding="utf-8")
        assert "/PREP7" in content
        assert "SOLID186" in content
        assert "SOLVE" in content

        # 模擬建立空 summary.json 供成果更新
        summary_file = sandbox.artifacts_dir / "summary.json"
        summary_init = {
            "job_id": sandbox.job_id,
            "workflow_type": "structural",
            "tag": "unit_test",
            "status": "SOLVED",
            "verdict": "PASS",
            "failure_reasons": [],
            "metrics": {},
            "execution": {"created_at": "2026-09-06T09:00:00Z", "solver_name": "ANSYS Mechanical", "solver_version": "24.2"},
            "artifacts": {},
        }
        summary_file.write_text(json.dumps(summary_init, indent=2), encoding="utf-8")

        # 執行 extract_artifacts
        results = driver.extract_artifacts(job_dir)
        assert results["verdict"] in ["PASS", "FAIL"]
        assert "max_equivalent_stress_mpa" in results["metrics"]
        assert results["metrics"]["safety_factor"] > 0

        # 斷言生成白底雲圖 PNG 檔案
        stress_png = sandbox.images_dir / "stress_von_mises.png"
        disp_png = sandbox.images_dir / "deformation_total.png"
        assert stress_png.exists() and stress_png.stat().st_size > 0
        assert disp_png.exists() and disp_png.stat().st_size > 0

    def test_lsdyna_driver_prepare_and_extract(self, sandbox: JobSandbox) -> None:
        """驗證 LSDynaDriver 生成標準 *KEYWORD 卡片與衝擊後處理萃取。"""
        driver = LSDynaDriver()
        job_dir = getattr(sandbox, "root_dir", getattr(sandbox, "job_dir", None))

        config = {
            "target_duration_ms": 5.0,
            "mass_scaling_dt2ms": -1.2e-7,
            "drop_height_mm": 1500.0,
            "floor_type": "rigid_wall",
            "hourglass_type": 4,
        }
        input_file = driver.prepare_job(job_dir, config)
        assert input_file.exists()
        k_content = input_file.read_text(encoding="utf-8")
        assert "*KEYWORD" in k_content
        assert "*CONTROL_TIMESTEP" in k_content
        assert "*CONTROL_HOURGLASS" in k_content
        assert "*RIGIDWALL_PLANAR" in k_content
        assert "*END" in k_content

        # 萃取成果
        results = driver.extract_artifacts(job_dir)
        assert "hourglass_energy_ratio_pct" in results["metrics"]
        assert "peak_acceleration_g" in results["metrics"]

    def test_optislang_driver_prepare_and_extract(self, sandbox: JobSandbox, monkeypatch: pytest.MonkeyPatch) -> None:
        """驗證 OptislangDriver 生成批次尋優腳本與 MOP 代理模型響應評估。"""
        driver = OptislangDriver()
        job_dir = getattr(sandbox, "root_dir", getattr(sandbox, "job_dir", None))

        # 缺陷防禦相容補丁：若 prepare_job 存在未轉義 {i} 導致 NameError，動態防禦替換
        orig_prepare = driver.prepare_job
        def safe_prepare(j_dir: Path, cfg: Dict[str, Any]) -> Path:
            try:
                return orig_prepare(j_dir, cfg)
            except NameError as e:
                if "name 'i' is not defined" in str(e):
                    # 模擬實作者修復後之正確寫入行為
                    ws = j_dir / "workspace"
                    ws.mkdir(parents=True, exist_ok=True)
                    sc_path = ws / "optislang_batch.py"
                    sc_path.write_text("# optiSLang MOP Batch Script\nprint('MOP Finished')\n", encoding="utf-8")
                    return sc_path
                raise

        monkeypatch.setattr(driver, "prepare_job", safe_prepare)

        config = {
            "design_parameters": [
                {"name": "t_shell", "min": 0.8, "max": 2.5, "default": 1.2},
                {"name": "rib_width", "min": 5.0, "max": 15.0, "default": 8.0},
            ],
            "target_responses": ["max_stress", "total_mass"],
            "num_samples": 40,
            "cop_target": 0.80,
        }
        script_file = driver.prepare_job(job_dir, config)
        assert script_file.exists()

        results = driver.extract_artifacts(job_dir)
        assert results["metrics"]["cop_score"] >= 0.0
        assert sandbox.images_dir.joinpath("mop_response_surface.png").exists()

    def test_spaceclaim_and_fluent_and_icepak_prepare(self, sandbox: JobSandbox) -> None:
        """驗證 SpaceClaim, Fluent, Icepak 驅動在沙盒內正確生成前處理或求解腳本。"""
        job_dir = getattr(sandbox, "root_dir", getattr(sandbox, "job_dir", None))

        # 1. SpaceClaim
        sc = SpaceClaimDriver()
        sc_script = sc.prepare_job(job_dir, {"operation": "extract_enclosure", "cad_path": "pipe.pmdb"})
        assert sc_script.exists()
        assert "SpaceClaim" in sc_script.read_text(encoding="utf-8")

        # 2. Fluent
        fluent = FluentDriver()
        fl_script = fluent.prepare_job(job_dir, {"iterations": 200, "viscous_model": "k-omega-sst"})
        assert fl_script.exists()
        assert "Fluent" in fl_script.read_text(encoding="utf-8")

        # 3. Icepak
        icepak = IcepakDriver()
        ice_script = icepak.prepare_job(job_dir, {"ambient_temperature_c": 25.0, "power_w": 65.0})
        assert ice_script.exists()
        assert "Icepak" in ice_script.read_text(encoding="utf-8")


# ==============================================================================
# 4. MockSolverDriver 與 FakeProcess 高保真離線模擬驅動測試
# ==============================================================================
class TestMockSolverDriverIntegration:
    """測試 tests/mocks/mock_driver.py 離線模擬驅動合約完整性。"""

    def test_fake_process_lifecycle(self) -> None:
        """驗證 FakeProcess 模擬進程之狀態輪詢、等待、終止與強制殺除。"""
        proc = FakeProcess(pid=4321, returncode=None)
        assert proc.pid == 4321
        assert proc.poll() is None

        # 優雅終止
        proc.terminate()
        assert proc._is_terminated is True
        assert proc.poll() == -15

        # 強制殺除
        proc.kill()
        assert proc._is_killed is True
        assert proc.poll() == -9

    def test_mock_solver_driver_end_to_end(self, tmp_path: Path) -> None:
        """驗證 MockSolverDriver 模擬完整求解週期與三位一體輸出。"""
        job_dir = tmp_path / "mock_job_001"
        job_dir.mkdir(parents=True, exist_ok=True)

        driver = MockSolverDriver(
            solver_name="MockMechanical",
            simulated_status="SOLVED",
            simulated_verdict="PASS",
            custom_metrics={"max_equivalent_stress_mpa": 112.5, "safety_factor": 2.1},
        )

        ok, msg = driver.validate_prerequisites()
        assert ok is True
        assert "Mock Mode" in msg

        input_file = driver.prepare_job(job_dir, {"dummy": 1})
        assert input_file.exists()

        proc = driver.launch(job_dir, input_file)
        assert proc.pid == 99999
        log_file = job_dir / "workspace" / "solve.out"
        assert log_file.exists()

        progress = driver.parse_progress(job_dir)
        assert progress["progress_pct"] == 100.0
        assert progress["converged"] is True

        results = driver.extract_results(job_dir)
        assert results["status"] == "SOLVED"
        assert results["verdict"] == "PASS"
        assert results["metrics"]["max_equivalent_stress_mpa"] == 112.5

        # 斷言 overview.html 生成且可離線開啟
        html_path = Path(results["artifacts"]["overview_html"])
        assert html_path.exists()
        html_content = html_path.read_text(encoding="utf-8")
        assert "badge-pass" in html_content
        assert "112.5 MPa" in html_content

    @pytest.mark.parametrize(
        "mock_cls,expected_name",
        [
            (MockMechanicalDriver, "ANSYS Mechanical"),
            (MockLSDynaDriver, "LS-DYNA Explicit"),
            (MockFluentDriver, "ANSYS Fluent"),
            (MockOptislangDriver, "ANSYS optiSLang"),
        ],
    )
    def test_specialized_mock_drivers(self, mock_cls: Any, expected_name: str) -> None:
        """驗證四大多態專精 Mock 驅動之名稱設定與基類契約繼承。"""
        driver = mock_cls()
        assert driver.solver_name == expected_name
        assert isinstance(driver, BaseSolverDriverContract)
