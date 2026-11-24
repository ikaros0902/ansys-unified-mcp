# -*- coding: utf-8 -*-
"""MAPDL Facade/Tools 安全契約與 BaseDualTrackDriver 進度解析契約測試。"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pytest

from ansys_unified_mcp.drivers.base import BaseDualTrackDriver
from ansys_unified_mcp.products.mapdl import tools as mapdl_tools
from ansys_unified_mcp.products.mapdl.facade import (
    MapdlController,
    controller as mapdl_controller,
    sanitize_job_name,
)


class _DummyDualTrackDriver(BaseDualTrackDriver):
    """供測試 BaseDualTrackDriver.parse_progress 行為之最小具象子類。"""

    def __init__(self) -> None:
        super().__init__(solver_name="DummyDualTrack")

    def validate_prerequisites(self) -> Tuple[bool, str]:
        return True, "ready"


# ==============================================================================
# 1. MAPDL 工作名稱消毒、路徑穿越防護與 dry_run 委派契約
# ==============================================================================


@pytest.mark.parametrize(
    "valid_name",
    [
        "ansys_job",
        "ansys_inline",
        "BeamModel-01.v2",
        "JOB_123",
    ],
)
def test_sanitize_job_name_accepts_safe_names(valid_name: str) -> None:
    """合法的工作名稱應原樣回傳。"""
    assert sanitize_job_name(valid_name) == valid_name


@pytest.mark.parametrize(
    "invalid_name",
    [
        "",
        ".",
        "..",
        "../evil",
        "..\\evil",
        "foo..bar",
        "a/b",
        "a\\b",
        "/tmp/x",
        "C:\\temp\\x",
        "job name",
        "job;rm",
        "job\n",
    ],
)
def test_sanitize_job_name_rejects_traversal_and_illegal_chars(invalid_name: str) -> None:
    """路徑穿越、斜線、空白、絕對路徑與非法字元必須拋出 ValueError。"""
    with pytest.raises(ValueError, match="非法的工作名稱"):
        sanitize_job_name(invalid_name)


@pytest.mark.parametrize("bad_job_name", ["../evil", "a/b", "C:\\temp\\x", ""])
def test_mapdl_controller_and_tool_block_path_traversal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    bad_job_name: str,
) -> None:
    """MapdlController 與 mapdl_run_apdl 皆須於入口阻擋非法 job_name，且不得建立檔案。"""
    called = False

    def _forbid_subprocess(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("非法 job_name 不得進入 subprocess.run")

    monkeypatch.setattr("ansys_unified_mcp.products.mapdl.facade.subprocess.run", _forbid_subprocess)

    # 1. Controller.run_apdl 直接阻擋
    ctrl = MapdlController()
    res_ctrl_apdl = ctrl.run_apdl(
        apdl_commands="/PREP7\nFINISH\n",
        job_name=bad_job_name,
        working_dir=str(tmp_path),
        dry_run=True,
    )
    assert res_ctrl_apdl["ok"] is False
    assert "非法的工作名稱" in res_ctrl_apdl["error"]

    # 2. Controller.solve_input 直接阻擋（即使先檢核入口也不依賴檔案存在）
    inp_file = tmp_path / "valid.inp"
    inp_file.write_text("/PREP7\n", encoding="utf-8")
    res_ctrl_solve = ctrl.solve_input(
        input_path=str(inp_file),
        job_name=bad_job_name,
        working_dir=str(tmp_path),
        dry_run=True,
    )
    assert res_ctrl_solve["ok"] is False
    assert "非法的工作名稱" in res_ctrl_solve["error"]

    # 3. MCP tool mapdl_run_apdl 阻擋並維持扁平失敗信封
    res_tool = mapdl_tools.mapdl_run_apdl(
        apdl_commands="/PREP7\nFINISH\n",
        job_name=bad_job_name,
        working_dir=str(tmp_path),
        dry_run=True,
    )
    assert res_tool["ok"] is False
    assert "非法的工作名稱" in res_tool["error"]
    assert list(tmp_path.glob("*.inp")) == [inp_file]
    assert called is False


def test_mapdl_run_apdl_dry_run_delegates_to_controller(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """合法 job_name 的 mapdl_run_apdl(dry_run=True) 應委派至 controller 且正確生成命令與輸入檔。"""
    fake_exe = tmp_path / "ANSYS.exe"
    fake_exe.write_text("mock", encoding="utf-8")
    monkeypatch.setattr("ansys_unified_mcp.products.mapdl.facade.config.mapdl_exe", fake_exe)

    res = mapdl_tools.mapdl_run_apdl(
        apdl_commands="/PREP7\nBLOCK,0,1,0,1,0,1\nFINISH\n",
        job_name="cantilever_01",
        working_dir=str(tmp_path),
        dry_run=True,
        timeout=90.0,
    )

    expected_inp = tmp_path.resolve() / "cantilever_01.inp"
    expected_out = tmp_path.resolve() / "cantilever_01.out"
    assert res["ok"] is True
    assert res["dry_run"] is True
    assert res["working_dir"] == str(tmp_path.resolve())
    assert res["output_log"] == str(expected_out)
    assert expected_inp.is_file()
    assert "BLOCK,0,1,0,1,0,1" in expected_inp.read_text(encoding="utf-8")
    assert res["command"] == [
        str(fake_exe),
        "-b",
        "-i",
        str(expected_inp),
        "-o",
        str(expected_out),
        "-j",
        "cantilever_01",
        "-np",
        "4",
    ]


def test_mapdl_solve_input_dry_run_and_missing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """mapdl_solve_input 應在缺檔時回傳 ok=False，合法 dry_run 時正確委派 controller。"""
    missing_res = mapdl_tools.mapdl_solve_input(
        input_path=str(tmp_path / "does_not_exist.inp"),
        job_name="valid_job",
        dry_run=True,
    )
    assert missing_res["ok"] is False
    assert "找不到輸入檔" in missing_res["error"]

    inp_file = tmp_path / "beam.inp"
    inp_file.write_text("/PREP7\nFINISH\n", encoding="utf-8")
    fake_exe = tmp_path / "ANSYS.exe"
    fake_exe.write_text("mock", encoding="utf-8")
    monkeypatch.setattr("ansys_unified_mcp.products.mapdl.facade.config.mapdl_exe", fake_exe)

    ok_res = mapdl_tools.mapdl_solve_input(
        input_path=str(inp_file),
        job_name="beam_01",
        np=2,
        working_dir=str(tmp_path),
        dry_run=True,
    )
    assert ok_res["ok"] is True
    assert ok_res["dry_run"] is True
    assert ok_res["command"][-2:] == ["-np", "2"]


def test_mapdl_check_connection_delegates_to_controller(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """mapdl_check_connection 應委派 controller.check_connection 並回傳標準扁平信封。"""
    fake_dir = tmp_path / "v251"
    fake_dir.mkdir(parents=True, exist_ok=True)
    fake_exe = fake_dir / "ANSYS.exe"
    fake_exe.write_text("mock", encoding="utf-8")
    monkeypatch.setattr("ansys_unified_mcp.products.mapdl.facade.config.mapdl_exe", fake_exe)

    direct = mapdl_controller.check_connection()
    via_tool = mapdl_tools.mapdl_check_connection()

    assert direct["ok"] is True
    assert direct["available"] is True
    assert direct["version"] == "v251"
    assert via_tool == direct


# ==============================================================================
# 2. BaseDualTrackDriver.parse_progress 五種狀態契約測試
# ==============================================================================


def test_base_dual_track_driver_parse_progress_missing_log(tmp_path: Path) -> None:
    """狀態 1：日誌檔不存在 -> QUEUED, 0.0%, is_converged=False。"""
    driver = _DummyDualTrackDriver()
    progress = driver.parse_progress(tmp_path)
    assert progress == {
        "progress_pct": 0.0,
        "current_step": "QUEUED",
        "is_converged": False,
    }


def test_base_dual_track_driver_parse_progress_empty_log(tmp_path: Path) -> None:
    """狀態 2：日誌檔存在但內容為空/純空白 -> RUNNING, 0.0%, is_converged=False。"""
    driver = _DummyDualTrackDriver()
    log_file = driver.get_log_file_path(tmp_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text("   \n\t  \n", encoding="utf-8")

    progress = driver.parse_progress(tmp_path)
    assert progress == {
        "progress_pct": 0.0,
        "current_step": "RUNNING",
        "is_converged": False,
    }


def test_base_dual_track_driver_parse_progress_running_log(tmp_path: Path) -> None:
    """狀態 3：日誌已有輸出但無完成或失敗標記 -> RUNNING, 50.0%, is_converged=False。"""
    driver = _DummyDualTrackDriver()
    log_file = driver.get_log_file_path(tmp_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text("Iteration 12: residual = 1.25e-03\n", encoding="utf-8")

    progress = driver.parse_progress(tmp_path)
    assert progress == {
        "progress_pct": 50.0,
        "current_step": "RUNNING",
        "is_converged": False,
    }


@pytest.mark.parametrize(
    "log_text",
    [
        "ERROR: license checkout failed",
        "Unhandled Exception in solver kernel",
        "Mesh generation FAILED due to bad topology",
        "FATAL: singular stiffness matrix",
        "Solution DIVERGED at substep 4",
        "Job ABORTED by watchdog\nCompleted cleanup",
    ],
)
def test_base_dual_track_driver_parse_progress_failed_log(tmp_path: Path, log_text: str) -> None:
    """狀態 4：日誌包含失敗關鍵字 -> FAILED, 100.0%, is_converged=False（優先於完成關鍵字）。"""
    driver = _DummyDualTrackDriver()
    log_file = driver.get_log_file_path(tmp_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text(log_text, encoding="utf-8")

    progress = driver.parse_progress(tmp_path)
    assert progress == {
        "progress_pct": 100.0,
        "current_step": "FAILED",
        "is_converged": False,
    }


@pytest.mark.parametrize(
    "log_text",
    [
        "Time step 10 CONVERGED within tolerance.",
        "Analysis Completed.",
        "Normal termination of solver.",
        "***** SOLUTION IS DONE *****",
        "FINISH\nPostprocessing ready.",
        "Run status: SUCCESS",
    ],
)
def test_base_dual_track_driver_parse_progress_completed_log(tmp_path: Path, log_text: str) -> None:
    """狀態 5：日誌包含收斂/完成關鍵字且無失敗標記 -> COMPLETED, 100.0%, is_converged=True。"""
    driver = _DummyDualTrackDriver()
    log_file = driver.get_log_file_path(tmp_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text(log_text, encoding="utf-8")

    progress = driver.parse_progress(tmp_path)
    assert progress == {
        "progress_pct": 100.0,
        "current_step": "COMPLETED",
        "is_converged": True,
    }
