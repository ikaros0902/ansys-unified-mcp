"""ANSYS Unified MCP 2.0 - DPF 後處理與顯式日誌讀取器單元測試套件 (test_dpf_reader.py).

涵蓋 7 大驗證場景：
- Test 1: 非終態 (QUEUED, RUNNING) 阻斷拋出 JobNotReadyError
- Test 2: 終態 (SOLVED) 複製 .rst 至 .dpf_cache/isolated_result.rst 並提取場結果
- Test 3: release_streams() 於 finally 區塊中嚴格調用釋放檔案鎖
- Test 4: 離線/無伺服器環境且 allow_synthetic=False 嚴格拋出 PostprocessingError
- Test 5: 離線環境且 allow_synthetic=True 回傳 is_synthetic: True 與 mock_reason: "NO_DPF_SERVER_DETECTED"
- Test 6: LSDynaExplicitReader 精確解析 glstat 能量平衡、matter.out 質量縮放與沙漏能佔比 (< 5%)
- Test 7: PostprocessingRouter 依據隱式 (DPF) 與顯式 (LS-DYNA) 工況類型精確分發
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import numpy as np
import pytest

from ansys_unified_mcp.postprocessing import (
    BaseResultReader,
    DPFSandboxReader,
    JobNotReadyError,
    LSDynaExplicitReader,
    PostprocessingError,
    PostprocessingRouter,
    TERMINAL_STATES,
)


# ==============================================================================
# 輔助工具函式
# ==============================================================================
def create_mock_summary(job_dir: Path, status: str, workflow_type: str = "static_structural") -> Path:
    """建立測試用之 summary.json 檔案。"""
    summary_path = job_dir / "summary.json"
    data = {
        "job_id": "test-job-001",
        "workflow_type": workflow_type,
        "status": status,
        "verdict": "PASS" if status == "SOLVED" else "INCONCLUSIVE",
    }
    summary_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return summary_path


def create_dummy_rst(job_dir: Path, filename: str = "file.rst", content: bytes = b"ANSYS_RST_BINARY_DATA_DUMMY") -> Path:
    """建立測試用之假 .rst 檔案。"""
    rst_path = job_dir / filename
    rst_path.write_bytes(content)
    return rst_path


# ==============================================================================
# Test 1: 非終態阻斷檢驗
# ==============================================================================
def test_1_non_terminal_state_raises_job_not_ready_error(tmp_path: Path) -> None:
    """驗證作業處於非終態 (RUNNING, QUEUED 或未標記) 時，嚴格拋出 JobNotReadyError。"""
    reader = DPFSandboxReader()
    job_dir = tmp_path / "job_running"
    job_dir.mkdir()

    # 1. 處於 RUNNING 狀態
    create_mock_summary(job_dir, "RUNNING")
    create_dummy_rst(job_dir)
    with pytest.raises(JobNotReadyError) as exc_info:
        reader.read_results(job_dir)
    assert "RUNNING" in str(exc_info.value)
    assert "尚未處於終態" in str(exc_info.value)

    # 2. 處於 QUEUED 狀態
    create_mock_summary(job_dir, "QUEUED")
    with pytest.raises(JobNotReadyError):
        reader.read_results(job_dir)

    # 3. 透過 kwargs 明確指定 non-terminal job_status
    with pytest.raises(JobNotReadyError):
        reader.read_results(job_dir, job_status="INITIALIZING")

    # 4. 無任何 summary.json 與 job_status
    empty_dir = tmp_path / "empty_job"
    empty_dir.mkdir()
    with pytest.raises(JobNotReadyError):
        reader.read_results(empty_dir)

    # 5. LS-DYNA Explicit Reader 亦同步遵守終態閘門
    explicit_reader = LSDynaExplicitReader()
    with pytest.raises(JobNotReadyError):
        explicit_reader.read_results(job_dir)


# ==============================================================================
# Test 2: 終態沙盒副本隔離與場數據提取
# ==============================================================================
def test_2_terminal_state_copies_rst_to_cache_and_extracts_fields(tmp_path: Path) -> None:
    """驗證終態 (SOLVED) 作業將 .rst 複製至 .dpf_cache/isolated_result.rst 並正確提取等效應力與位移。"""
    reader = DPFSandboxReader()
    job_dir = tmp_path / "job_solved"
    job_dir.mkdir()
    create_mock_summary(job_dir, "SOLVED")
    dummy_bytes = b"BINARY_SOLVE_RST_PAYLOAD_123456"
    create_dummy_rst(job_dir, "file.rst", dummy_bytes)

    # 構造模擬 DPF Model 與欄位結果
    mock_model = MagicMock()

    # 模擬等效應力欄位
    mock_stress_field = MagicMock()
    mock_stress_field.data = np.array([120.5, 245.8, 80.2], dtype=float)
    mock_stress_op = MagicMock()
    mock_stress_op.eval.return_value = [mock_stress_field]
    mock_model.results.stress_von_mises.return_value = mock_stress_op

    # 模擬位移場 (N, 3) 陣列
    mock_disp_field = MagicMock()
    mock_disp_field.data = np.array([
        [0.10, 0.20, 0.30],
        [0.15, 0.25, 0.40],
    ], dtype=float)
    mock_disp_op = MagicMock()
    mock_disp_op.eval.return_value = [mock_disp_field]
    mock_model.results.displacement.return_value = mock_disp_op

    # 模擬模態特徵頻率
    mock_tfs = MagicMock()
    mock_tfs.frequencies.data = [45.2, 112.8, 230.5]
    mock_tfs.get_cumulative_mass_fractions.return_value = {"x": 0.88, "y": 0.91, "z": 0.93}
    mock_model.metadata.time_freq_support = mock_tfs

    with patch("ansys.dpf.core.Model", return_value=mock_model):
        results = reader.read_results(job_dir, allow_synthetic=False)

    # 1. 斷言沙盒隔離副本確實產生且內容無損
    cache_rst = job_dir / ".dpf_cache" / "isolated_result.rst"
    assert cache_rst.is_file(), "必須生成 .dpf_cache/isolated_result.rst 副本"
    assert cache_rst.read_bytes() == dummy_bytes, "隔離副本內容必須與原始主檔案完全吻合"

    # 2. 斷言非合成指標
    assert results["is_synthetic"] is False
    assert results["rst_path"] == str(cache_rst)

    # 3. 斷言應力數值提取
    stress = results["stress_von_mises"]
    assert stress["max"] == pytest.approx(245.8)
    assert stress["min"] == pytest.approx(80.2)
    assert stress["avg"] == pytest.approx(np.mean([120.5, 245.8, 80.2]))
    assert stress["unit"] == "Pa"

    # 4. 斷言位移數值提取
    disp = results["displacement"]
    expected_norm_1 = np.linalg.norm([0.10, 0.20, 0.30])
    expected_norm_2 = np.linalg.norm([0.15, 0.25, 0.40])
    assert disp["total_max"] == pytest.approx(max(expected_norm_1, expected_norm_2))
    assert disp["ux_max"] == pytest.approx(0.15)
    assert disp["uy_max"] == pytest.approx(0.25)
    assert disp["uz_max"] == pytest.approx(0.40)

    # 5. 斷言模態頻率與質量佔比提取
    modal = results["modal"]
    assert modal["frequencies"] == [45.2, 112.8, 230.5]
    assert modal["effective_mass_ratio"]["x"] == 0.88


# ==============================================================================
# Test 3: release_streams() 於 finally 區塊調用驗證
# ==============================================================================
def test_3_release_streams_called_in_finally_block(tmp_path: Path) -> None:
    """驗證無論提取成功或中途發生例外，release_streams() 皆必被調用以釋放檔案鎖。"""
    reader = DPFSandboxReader()
    job_dir = tmp_path / "job_stream"
    job_dir.mkdir()
    create_mock_summary(job_dir, "SOLVED")
    create_dummy_rst(job_dir)

    mock_model = MagicMock()
    mock_model.metadata.release_streams = MagicMock()

    # 正常執行情境
    with patch("ansys.dpf.core.Model", return_value=mock_model):
        reader.read_results(job_dir, allow_synthetic=False)
    assert mock_model.metadata.release_streams.call_count == 1

    # 異常中斷情境：模擬提取過程中爆出例外
    mock_model.metadata.release_streams.reset_mock()
    mock_model.results.stress_von_mises.side_effect = RuntimeError("二進位資料損毀")

    with patch("ansys.dpf.core.Model", return_value=mock_model):
        with pytest.raises(PostprocessingError):
            reader.read_results(job_dir, allow_synthetic=False)

    # 斷言即使拋出例外，finally 依舊成功執行 release_streams()
    assert mock_model.metadata.release_streams.call_count == 1


# ==============================================================================
# Test 4: 離線且 allow_synthetic=False 拋出 PostprocessingError
# ==============================================================================
def test_4_offline_dpf_raises_postprocessing_error_when_synthetic_disabled(tmp_path: Path) -> None:
    """驗證在無 DPF 授權/伺服器環境下，若 allow_synthetic=False 則嚴格拋出例外，拒絕偽造數據。"""
    reader = DPFSandboxReader()
    job_dir = tmp_path / "job_offline"
    job_dir.mkdir()
    create_mock_summary(job_dir, "SOLVED")
    create_dummy_rst(job_dir)

    # 模擬 DPF 伺服器連線失敗或授權不足
    server_error = RuntimeError("DPFServerException: Cannot connect to DPF server on port 50052")
    with patch("ansys.dpf.core.Model", side_effect=server_error):
        with pytest.raises(PostprocessingError) as exc_info:
            reader.read_results(job_dir, allow_synthetic=False)
        assert "DPF 讀取結果失敗" in str(exc_info.value)


# ==============================================================================
# Test 5: 離線且 allow_synthetic=True 回傳標準合成指標
# ==============================================================================
def test_5_offline_dpf_returns_synthetic_indicators_when_allowed(tmp_path: Path) -> None:
    """驗證在無 DPF 伺服器環境下，若 allow_synthetic=True 則回傳明確標記之合成指標。"""
    reader = DPFSandboxReader()
    job_dir = tmp_path / "job_synthetic"
    job_dir.mkdir()
    create_mock_summary(job_dir, "SOLVED")
    create_dummy_rst(job_dir)

    server_error = RuntimeError("DPFServerException: License server unavailable")
    with patch("ansys.dpf.core.Model", side_effect=server_error):
        res = reader.read_results(job_dir, allow_synthetic=True)

    assert res["is_synthetic"] is True
    assert res["mock_reason"] == "NO_DPF_SERVER_DETECTED"
    assert "stress_von_mises" in res
    assert res["stress_von_mises"]["max"] > 0
    assert "displacement" in res
    assert res["displacement"]["total_max"] > 0
    assert "modal" in res
    assert len(res["modal"]["frequencies"]) > 0


# ==============================================================================
# Test 6: LS-DYNA Explicit Reader 解析 glstat 能量平衡與沙漏能佔比
# ==============================================================================
def test_6_explicit_reader_parses_glstat_and_hourglass_ratio(tmp_path: Path) -> None:
    """驗證 LSDynaExplicitReader 正確解析 glstat 能量平衡、matter.out 質量縮放並計算沙漏能佔比 (< 5%)。"""
    reader = LSDynaExplicitReader()
    job_dir = tmp_path / "job_lsdyna"
    job_dir.mkdir()
    create_mock_summary(job_dir, "SOLVED", workflow_type="drop_test")

    # 模擬 d3plot 檔案
    (job_dir / "d3plot").write_bytes(b"D3PLOT_HEADER")

    # 模擬標準 glstat 內容（沙漏能 25 J / 內能 1000 J = 2.5% < 5%）
    glstat_content = """
    *** GLSTAT ENERGY SUMMARY ***
    time = 2.5000E-03  dt = 1.2500E-06
    kinetic energy = 4.5000E+02
    internal energy = 1.0000E+03
    hourglass energy = 2.5000E+01
    total energy = 1.4750E+03
    sliding interface energy = 0.0000E+00
    added mass = 1.5000E-06 (ratio = 0.085 %)
    """
    (job_dir / "glstat").write_text(glstat_content, encoding="utf-8")

    # 模擬 matter.out 質量縮放
    matter_content = "added mass percentage = 0.125\n"
    (job_dir / "matter.out").write_text(matter_content, encoding="utf-8")

    res = reader.read_results(job_dir, allow_synthetic=False)

    assert res["is_synthetic"] is False
    assert res["d3plot_exists"] is True
    assert res["kinetic_energy"] == pytest.approx(450.0)
    assert res["internal_energy"] == pytest.approx(1000.0)
    assert res["hourglass_energy"] == pytest.approx(25.0)
    assert res["total_energy"] == pytest.approx(1475.0)

    # 檢驗沙漏能佔比: 25 / 1000 = 0.025 (2.5%)
    assert res["hourglass_ratio"] == pytest.approx(0.025)
    assert res["hourglass_ratio_pct"] == pytest.approx(2.5)
    assert res["hourglass_ratio"] < 0.05, "沙漏能比例必須小於 5% 門檻"
    assert res["hourglass_acceptable"] is True

    # 檢驗能量平衡與質量縮放
    assert res["energy_balance"] == pytest.approx((450.0 + 1000.0 + 25.0) / 1475.0)
    assert res["mass_scaling_added_pct"] == pytest.approx(0.125)

    # 測試沙漏能超標 (例如 80 J / 1000 J = 8.0% > 5%)
    bad_glstat = """
    time = 2.5000E-03  dt = 1.2500E-06
    kinetic energy = 4.5000E+02
    internal energy = 1.0000E+03
    hourglass energy = 8.0000E+01
    total energy = 1.5300E+03
    """
    (job_dir / "glstat").write_text(bad_glstat, encoding="utf-8")
    res_bad = reader.read_results(job_dir, allow_synthetic=False)
    assert res_bad["hourglass_ratio"] == pytest.approx(0.08)
    assert res_bad["hourglass_acceptable"] is False

    # 若開啟嚴格物理健康門禁 assert_healthy=True，超標應報錯
    with pytest.raises(PostprocessingError) as exc_info:
        reader.read_results(job_dir, assert_healthy=True)
    assert "超出 5% 安全門檻" in str(exc_info.value)


# ==============================================================================
# Test 7: PostprocessingRouter 分發路由檢驗
# ==============================================================================
def test_7_router_correctly_dispatches_implicit_vs_explicit() -> None:
    """驗證 PostprocessingRouter 正確將各工況類型派發至 DPFSandboxReader 或 LSDynaExplicitReader。"""
    router = PostprocessingRouter()

    # 隱式結構、模態、振動與熱翹曲 -> DPFSandboxReader
    implicit_cases = [
        "static_structural",
        "transient_structural",
        "modal",
        "modal_analysis",
        "random_vibration",
        "thermal_warpage",
        "steady_state_thermal",
        "transient_thermal",
        "implicit",
    ]
    for case in implicit_cases:
        reader = router.get_reader(case)
        assert isinstance(reader, DPFSandboxReader), f"工況 '{case}' 應路由至 DPFSandboxReader"

    # 顯式動力學落摔與衝擊 -> LSDynaExplicitReader
    explicit_cases = [
        "drop_test",
        "shock_analysis",
        "shock",
        "lsdyna",
        "lsdyna_explicit",
        "explicit",
        "explicit_dynamics",
    ]
    for case in explicit_cases:
        reader = router.get_reader(case)
        assert isinstance(reader, LSDynaExplicitReader), f"工況 '{case}' 應路由至 LSDynaExplicitReader"
