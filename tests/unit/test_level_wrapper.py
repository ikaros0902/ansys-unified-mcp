# -*- coding: utf-8 -*-
"""測試 `level_wrapper.py` 與 `LayerBuilder_pyansys.py --check` 之契約行為。"""

from __future__ import annotations

import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_SCRIPTS = (
    REPO_ROOT / "agents" / "skills" / "materials-reliability" / "pcb-warpage-analysis" / "scripts"
)
LEVEL_WRAPPER_PATH = SKILL_SCRIPTS / "level_wrapper.py"
LAYERBUILDER_PATH = SKILL_SCRIPTS / "odb_workflow" / "1_Scripts" / "LayerBuilder_pyansys.py"
UPSTREAM_LEVELING_PATH = SKILL_SCRIPTS / "odb_workflow" / "1_Scripts" / "level_bga_shadow.py"


def _load_level_wrapper():
    """動態載入 `level_wrapper.py`，確保每次匯入不依賴 ansys_unified_mcp 套件。"""
    spec = importlib.util.spec_from_file_location("pcb_level_wrapper", LEVEL_WRAPPER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_upstream_input_error():
    """取得上游 `level_bga_shadow.InputError` 類別以精準斷言例外型別。"""
    existing = sys.modules.get("level_bga_shadow")
    if existing is not None and Path(existing.__file__).resolve() == UPSTREAM_LEVELING_PATH.resolve():
        return existing.InputError
    spec = importlib.util.spec_from_file_location("level_bga_shadow", UPSTREAM_LEVELING_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["level_bga_shadow"] = module
    spec.loader.exec_module(module)
    return module.InputError


def _synthetic_grid(nx: int = 9, ny: int = 7, pitch: float = 5.0, x0: float = 100.0, y0: float = 200.0):
    xs, ys = np.meshgrid(np.arange(nx) * pitch + x0, np.arange(ny) * pitch + y0)
    return xs.ravel(), ys.ravel()


def _write_leveling_files(
    tmp_path: Path,
    nodes: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    uz: np.ndarray,
    *,
    header: str = "Directional Deformation (mm)",
    units_line: str = "/units,MPA",
    consistent_line: str = "/com,--- Data in consistent NMM units. See Solving Units",
) -> tuple[Path, Path]:
    res_path = tmp_path / "bga_disp.txt"
    res_lines = [f"Node Number\t{header}"] + [
        f"{int(n)}\t{val:.9g}" for n, val in zip(nodes, uz)
    ]
    res_path.write_text("\n".join(res_lines) + "\n", encoding="utf-8")

    dat_path = tmp_path / "ds.dat"
    dat_lines = [
        consistent_line,
        units_line,
        f"nblock,3,,{len(nodes)}",
        "(1i9,3e20.9e3)",
    ]
    for n, xi, yi in zip(nodes, x, y):
        dat_lines.append(f"{int(n):9d}{xi:20.9E}{yi:20.9E}{0.0:20.9E}")
    dat_lines.extend(["-1", "et,1,185"])
    dat_path.write_text("\n".join(dat_lines) + "\n", encoding="latin-1")
    return res_path, dat_path


@pytest.mark.parametrize("cli_args", [["--help"], []])
def test_level_wrapper_cli_help_and_no_args_exit_zero(cli_args):
    """驗證 `level_wrapper.py --help` 與無參數執行皆回傳 Exit Code 0 並輸出 usage。"""
    proc = subprocess.run(
        [sys.executable, str(LEVEL_WRAPPER_PATH), *cli_args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert proc.returncode == 0
    assert "usage:" in proc.stdout.lower()


def test_level_wrapper_help_does_not_import_numpy():
    """驗證處理 `--help` 與無參數 usage 分支前不匯入 `numpy`。"""
    probe = "\n".join(
        [
            "import importlib.util, sys",
            "sys.modules['numpy'] = None",
            f"spec = importlib.util.spec_from_file_location('lw', r'{LEVEL_WRAPPER_PATH}')",
            "mod = importlib.util.module_from_spec(spec)",
            "spec.loader.exec_module(mod)",
            "assert mod.main([]) == 0",
            "try:",
            "    mod.main(['--help'])",
            "except SystemExit as exc:",
            "    assert exc.code == 0",
        ]
    )
    proc = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert proc.returncode == 0, proc.stderr


def test_compute_leveled_warpage_removes_tilt_and_handles_flip_z():
    """以已知傾斜平面疊加已知對稱碗狀翹曲驗證 warpage_um、tilt_deg、shape 與 flip_z。"""
    lw = _load_level_wrapper()
    x, y = _synthetic_grid()
    xc, yc = x.mean(), y.mean()
    hx = x.max() - xc
    hy = y.max() - yc

    # 中心低、邊緣高（0 ~ 0.008 mm = 8.0 um）的對稱翹曲，疊加已知平面傾斜
    bowl_mm = 0.004 * (((x - xc) / hx) ** 2 + ((y - yc) / hy) ** 2)
    slope_a, slope_b = 0.002, -0.001
    uz_mm = bowl_mm + slope_a * x + slope_b * y + 1.5

    res = lw.compute_leveled_warpage(x, y, uz_mm, method="OLS", mode="detrend", flip_z=False)

    assert set(res.keys()) == {
        "warpage_um",
        "warpage_mil",
        "shape",
        "tilt_deg",
        "z_leveled_mm",
        "warnings",
    }
    expected_tilt_deg = math.degrees(math.atan(math.hypot(slope_a, slope_b)))
    assert res["warpage_um"] == pytest.approx(8.0, abs=1e-3)
    assert res["warpage_mil"] == pytest.approx(8.0 / 25.4, abs=1e-4)
    assert res["tilt_deg"] == pytest.approx(expected_tilt_deg, rel=1e-6)
    assert res["shape"] == "Smile"
    assert isinstance(res["z_leveled_mm"], np.ndarray)
    assert res["z_leveled_mm"].shape == x.shape
    assert res["warnings"] == []

    # 翻轉 Z 軸方向：形態應反轉為 Cry，翹曲量與傾角大小保持不變
    res_flipped = lw.compute_leveled_warpage(x, y, uz_mm, method="OLS", mode="detrend", flip_z=True)
    assert res_flipped["shape"] == "Cry"
    assert res_flipped["warpage_um"] == pytest.approx(res["warpage_um"], abs=1e-9)
    assert res_flipped["warpage_mil"] == pytest.approx(res["warpage_mil"], abs=1e-9)
    assert res_flipped["tilt_deg"] == pytest.approx(res["tilt_deg"], rel=1e-9)
    assert np.allclose(res_flipped["z_leveled_mm"], -res["z_leveled_mm"], atol=1e-12)


def test_compute_leveled_warpage_undetermined_and_small_node_warning():
    """驗證極值等距（Undetermined）情境與 3 <= N < 9 警告訊息。"""
    lw = _load_level_wrapper()

    # 7x7 正方形對稱網格上的傾斜馬鞍面：最大與最小值分別位於四角且距中心等距 -> Undetermined
    x_sq, y_sq = _synthetic_grid(nx=7, ny=7, pitch=5.0, x0=0.0, y0=0.0)
    xc, yc = x_sq.mean(), y_sq.mean()
    saddle_mm = 0.004 * ((x_sq - xc) / 15.0) * ((y_sq - yc) / 15.0)
    uz_saddle = saddle_mm + 0.0015 * x_sq - 0.0008 * y_sq + 0.25
    saddle_res = lw.compute_leveled_warpage(x_sq, y_sq, uz_saddle)
    assert saddle_res["warpage_um"] == pytest.approx(8.0, abs=1e-6)
    assert saddle_res["shape"] == "Undetermined"
    assert saddle_res["warnings"] == []

    # 5 個不共線節點（3 <= N < 9）-> 允許計算但必含警告
    x_small = [0.0, 10.0, 10.0, 0.0, 5.0]
    y_small = [0.0, 0.0, 10.0, 10.0, 5.0]
    uz_small = [0.002, 0.002, 0.002, 0.002, 0.0]
    small_res = lw.compute_leveled_warpage(x_small, y_small, uz_small)
    assert small_res["shape"] == "Smile"
    assert small_res["warpage_um"] == pytest.approx(2.0, abs=1e-6)
    assert len(small_res["warnings"]) == 1
    assert "MIN_NODES=9" in small_res["warnings"][0]


def test_compute_leveled_warpage_invalid_inputs_raise_upstream_input_error():
    """驗證節點數 < 3、長度不一致、共線點與非有限值均拋出上游 InputError。"""
    lw = _load_level_wrapper()
    upstream_input_error = _load_upstream_input_error()

    # 空陣列與 N < 3
    for x_bad, y_bad, z_bad in [
        ([], [], []),
        ([1.0], [2.0], [0.1]),
        ([0.0, 1.0], [0.0, 1.0], [0.1, 0.2]),
        ([0.0, 1.0, 2.0], [0.0, 1.0], [0.1, 0.2, 0.3]),
    ]:
        with pytest.raises(upstream_input_error):
            lw.compute_leveled_warpage(x_bad, y_bad, z_bad)

    # 共線點集（含大座標偏移共線）
    with pytest.raises(upstream_input_error):
        lw.compute_leveled_warpage(
            [100.0, 101.0, 102.0, 103.0],
            [200.0, 202.0, 204.0, 206.0],
            [0.01, 0.02, 0.03, 0.04],
        )

    # 重複相同點（秩 = 1 < 3）
    with pytest.raises(upstream_input_error):
        lw.compute_leveled_warpage([5.0, 5.0, 5.0], [6.0, 6.0, 6.0], [0.1, 0.2, 0.3])

    # NaN 輸入
    with pytest.raises(upstream_input_error):
        lw.compute_leveled_warpage(
            [0.0, 10.0, 0.0, 10.0],
            [0.0, 0.0, 10.0, 10.0],
            [0.0, float("nan"), 0.01, 0.02],
        )


def test_level_wrapper_cli_unit_validation_and_direct_execution(tmp_path):
    """驗證 CLI 直接模式之單位錯誤攔截（Exit Code 3）與正常輸出（Exit Code 0）。"""
    x, y = _synthetic_grid()
    uz = 0.004 * (((x - x.mean()) / 20.0) ** 2 + ((y - y.mean()) / 15.0) ** 2)
    nodes = np.arange(1, len(x) + 1)

    res_ok, dat_ok = _write_leveling_files(tmp_path, nodes, x, y, uz)
    proc_ok = subprocess.run(
        [
            sys.executable,
            str(LEVEL_WRAPPER_PATH),
            "--result",
            str(res_ok),
            "--dat",
            str(dat_ok),
            "--z-unit",
            "mm",
            "--xy-unit",
            "mm",
            "--scope",
            "bga-shadow",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert proc_ok.returncode == 0, proc_ok.stdout + proc_ok.stderr
    assert "BGA-Shadow Leveled" in proc_ok.stdout

    # 檔頭單位與 --z-unit 不符 -> 必須回傳 Exit Code 3
    proc_mismatch = subprocess.run(
        [
            sys.executable,
            str(LEVEL_WRAPPER_PATH),
            "--result",
            str(res_ok),
            "--dat",
            str(dat_ok),
            "--z-unit",
            "m",
            "--xy-unit",
            "mm",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert proc_mismatch.returncode == 3

    # 檔頭缺少單位 -> 必須回傳 Exit Code 3
    res_no_unit, dat_no_unit = _write_leveling_files(tmp_path, nodes, x, y, uz, header="UZ")
    proc_missing_unit = subprocess.run(
        [
            sys.executable,
            str(LEVEL_WRAPPER_PATH),
            "--result",
            str(res_no_unit),
            "--dat",
            str(dat_no_unit),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert proc_missing_unit.returncode == 3


def test_layerbuilder_check_passes_with_synthetic_inputs(tmp_path):
    """以合成疊構 CSV、空白 .stp 與專案 JSON 驗證 `LayerBuilder_pyansys.py --check` 通過。"""
    csv_path = tmp_path / "stackup.csv"
    csv_path.write_text(
        "Layer Name,Thickness um,Copper Ratio\n"
        "Layer_1_EM892K2,35.0,0.296\n"
        "Layer_2_EM892K2,100.0,0.0\n"
        "Layer_3_EM892K2,35.0,0.85\n",
        encoding="utf-8",
    )

    step_path = tmp_path / "board_2d.stp"
    step_path.write_text("", encoding="utf-8")

    cfg_path = tmp_path / "project.json"
    cfg_path.write_text(
        json.dumps(
            {
                "project": {"name": "SYNTH", "vendor": "TEST"},
                "layerbuilder": {
                    "stackup_csv": str(csv_path),
                    "step_file": str(step_path),
                    "output_scdocx": str(tmp_path / "out" / "SYNTH_TEST_Stackup.scdocx"),
                },
            }
        ),
        encoding="utf-8",
    )

    proc = subprocess.run(
        [sys.executable, str(LAYERBUILDER_PATH), str(cfg_path), "--check"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "CHECK OK" in proc.stdout
