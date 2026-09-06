# -*- coding: utf-8 -*-
"""Tier 2 單元測試：5 大高階工況工作流與 Intent Tools 測試 (test_intent_workflows.py).

覆蓋 R3 與 R4 核心驗證矩陣：
1. run_drop_test (落摔衝擊):
   - Gatekeeper 前置物理檢核攔截 (初速向量反向阻斷)
   - 正常初速換算、卡片生成與沙盒排程
2. run_shock_analysis (衝擊響應):
   - 單位制檢核、半正弦波與梯形波計算
3. run_random_vibration (隨機振動):
   - Gatekeeper 嚴格物理阻斷 (三向有效模態質量 < 90% 強制攔截)
   - 模態截斷頻率充裕度檢核 (< 1.5x 激振上限攔截)
   - 達標時建立 Modal -> Random Vibration 原生單元鏈結
4. run_thermal_warpage (熱翹曲):
   - Gatekeeper 檢核 (CTE=0 或參考溫度異常強制阻斷)
   - 達標時建立熱-結構單元直通與 3-2-1 靜定無拘束支承
5. train_surrogate_model (代理模型):
   - 參數邊界檢驗 (min >= max 阻斷)
   - 取樣數不足檢驗 (< 10 阻斷)
   - 達標時建立 optiSLang 參數直通與 MOP 評估
6. tools/intent_tools.py (MCP Tools 註冊與介面合約):
   - 驗證 5 大工具簽名與可調用性
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict
import pytest

from ansys_unified_mcp.tools import intent_tools
from ansys_unified_mcp.workflows import (
    run_drop_test,
    run_random_vibration,
    run_shock_analysis,
    run_thermal_warpage,
    train_surrogate_model,
)


class TestDropTestWorkflow:
    """測試落摔衝擊工作流 (run_drop_test)。"""

    def test_drop_test_normal_submission(self, tmp_path: Path) -> None:
        """驗證合規參數正常通過前置閘門並成功提交作業。"""
        res = run_drop_test(
            cad_path=str(tmp_path / "model.step"),
            drop_height_mm=1000.0,
            gravity_direction=[0.0, 0.0, -1.0],
            floor_type="rigid_wall",
            tag="test_drop_pass",
        )

        assert res.get("ok") is True
        assert "job_id" in res
        assert res.get("status") == "QUEUED"
        assert "sandbox_dir" in res

    def test_drop_test_gatekeeper_blocks_reverse_velocity(self, tmp_path: Path) -> None:
        """驗證初速度向量朝上 (+Z 反向飛離剛性地面) 時被 Gatekeeper 致命阻斷。"""
        res = run_drop_test(
            cad_path=str(tmp_path / "model.step"),
            drop_height_mm=1000.0,
            gravity_direction=[0.0, 0.0, 1.0],  # 反向朝上
            floor_type="rigid_wall",
            tag="test_drop_blocked",
        )

        assert res.get("ok") is False
        assert res.get("blocked") is True
        assert "prescription_report" in res
        report = res["prescription_report"]
        assert report["passed"] is False
        assert report["blocking_issues_count"] >= 1
        # 確認包含初速向量阻斷項
        rules_checked = [c["rule_id"] for c in report["checks"]]
        assert "GATE-DRP-001" in rules_checked


class TestShockAnalysisWorkflow:
    """測試衝擊響應分析工作流 (run_shock_analysis)。"""

    def test_shock_analysis_half_sine_submission(self, tmp_path: Path) -> None:
        """驗證半正弦波衝擊響應工作流正常提交。"""
        res = run_shock_analysis(
            cad_path=str(tmp_path / "bracket.pmdb"),
            pulse_shape="half_sine",
            peak_acceleration_g=50.0,
            pulse_duration_ms=11.0,
            direction="Z",
            analysis_method="transient_dynamics",
            tag="test_shock_half_sine",
        )

        assert res.get("ok") is True
        assert "job_id" in res
        assert res.get("status") == "QUEUED"

    def test_shock_analysis_response_spectrum(self, tmp_path: Path) -> None:
        """驗證反應譜衝擊工作流正常提交。"""
        res = run_shock_analysis(
            cad_path=str(tmp_path / "bracket.pmdb"),
            pulse_shape="trapezoidal",
            peak_acceleration_g=30.0,
            pulse_duration_ms=8.0,
            analysis_method="response_spectrum",
            tag="test_shock_spectrum",
        )

        assert res.get("ok") is True
        assert "job_id" in res


class TestRandomVibrationWorkflow:
    """測試隨機振動分析工作流 (run_random_vibration)。"""

    def test_random_vib_gatekeeper_blocks_low_effective_mass(self, tmp_path: Path) -> None:
        """驗證三向累積有效模態質量比未達 90% (如 78%) 時被 Gatekeeper 強制阻斷並回傳處方箋。"""
        res = run_random_vibration(
            cad_path=str(tmp_path / "pcb.pmdb"),
            psd_table=[(20.0, 0.04), (1000.0, 0.04), (2000.0, 0.01)],
            direction="Z",
            effective_mass_ratio={"X": 0.78, "Y": 0.82, "Z": 0.80},  # 全部 < 0.90
            cutoff_frequency_hz=3500.0,
            tag="test_vib_low_mass",
        )

        assert res.get("ok") is False
        assert res.get("blocked") is True
        assert "prescription_report" in res
        report = res["prescription_report"]
        assert report["passed"] is False
        rules_checked = [c["rule_id"] for c in report["checks"]]
        assert "GATE-VIB-001" in rules_checked

    def test_random_vib_gatekeeper_blocks_insufficient_cutoff(self, tmp_path: Path) -> None:
        """驗證截斷頻率未達 1.5x 激振上限 (2000Hz 上限而截斷頻率僅 2200Hz) 時被阻斷。"""
        res = run_random_vibration(
            cad_path=str(tmp_path / "pcb.pmdb"),
            psd_table=[(20.0, 0.04), (2000.0, 0.04)],
            direction="Z",
            effective_mass_ratio={"X": 0.92, "Y": 0.93, "Z": 0.95},
            cutoff_frequency_hz=2200.0,  # 2200 < 1.5 * 2000 = 3000
            tag="test_vib_low_cutoff",
        )

        assert res.get("ok") is False
        assert res.get("blocked") is True
        report = res["prescription_report"]
        rules_checked = [c["rule_id"] for c in report["checks"]]
        assert "GATE-VIB-002" in rules_checked

    def test_random_vib_normal_submission(self, tmp_path: Path) -> None:
        """驗證指標達標時正常提交並建立 Modal -> Random Vibration 單元鏈結。"""
        res = run_random_vibration(
            cad_path=str(tmp_path / "pcb.pmdb"),
            psd_table=[(20.0, 0.04), (1000.0, 0.04), (2000.0, 0.01)],
            direction="Z",
            effective_mass_ratio={"X": 0.92, "Y": 0.91, "Z": 0.94},
            cutoff_frequency_hz=3500.0,
            tag="test_vib_pass",
        )

        assert res.get("ok") is True
        assert "job_id" in res
        assert res.get("status") == "QUEUED"


class TestThermalWarpageWorkflow:
    """測試熱翹曲分析工作流 (run_thermal_warpage)。"""

    def test_thermal_warpage_gatekeeper_blocks_zero_cte(self, tmp_path: Path) -> None:
        """驗證材料熱膨脹係數 CTE <= 0 時被 Gatekeeper 強制阻斷。"""
        res = run_thermal_warpage(
            cad_or_stackup_file=str(tmp_path / "package.step"),
            temperature_ref_c=22.0,
            temperature_operating_c=125.0,
            secant_cte=0.0,  # CTE 為零
            tag="test_warpage_zero_cte",
        )

        assert res.get("ok") is False
        assert res.get("blocked") is True
        report = res["prescription_report"]
        rules_checked = [c["rule_id"] for c in report["checks"]]
        assert "GATE-THM-001" in rules_checked

    def test_thermal_warpage_gatekeeper_blocks_invalid_tref(self, tmp_path: Path) -> None:
        """驗證參考溫度異常 (如 -100 °C 脫離合理工程範圍) 時被阻斷。"""
        res = run_thermal_warpage(
            cad_or_stackup_file=str(tmp_path / "package.step"),
            temperature_ref_c=-100.0,  # 脫離 [-50, 400]
            temperature_operating_c=125.0,
            secant_cte=1.6e-5,
            tag="test_warpage_bad_tref",
        )

        assert res.get("ok") is False
        assert res.get("blocked") is True
        report = res["prescription_report"]
        rules_checked = [c["rule_id"] for c in report["checks"]]
        assert "GATE-THM-002" in rules_checked

    def test_thermal_warpage_normal_submission(self, tmp_path: Path) -> None:
        """驗證合規參數建立熱-結構單元直通並成功送算。"""
        res = run_thermal_warpage(
            cad_or_stackup_file=str(tmp_path / "package.step"),
            temperature_ref_c=22.0,
            temperature_operating_c=125.0,
            secant_cte=1.6e-5,
            support_type="3-2-1",
            tag="test_warpage_pass",
        )

        assert res.get("ok") is True
        assert "job_id" in res
        assert res.get("status") == "QUEUED"


class TestSurrogateModelWorkflow:
    """測試 optiSLang 代理模型工作流 (train_surrogate_model)。"""

    def test_surrogate_blocks_invalid_bounds(self) -> None:
        """驗證參數下限大於上限時被阻斷。"""
        res = train_surrogate_model(
            design_parameters=[{"name": "t", "min": 5.0, "max": 2.0}],  # min > max
            target_responses=["max_stress"],
            num_samples=50,
            tag="test_surrogate_bad_bounds",
        )

        assert res.get("ok") is False
        assert res.get("blocked") is True
        assert "errors" in res

    def test_surrogate_blocks_insufficient_samples(self) -> None:
        """驗證樣本數過少 (<10) 時被阻斷。"""
        res = train_surrogate_model(
            design_parameters=[{"name": "t", "min": 1.0, "max": 3.0}],
            target_responses=["max_stress"],
            num_samples=5,  # 5 < 10
            tag="test_surrogate_few_samples",
        )

        assert res.get("ok") is False
        assert res.get("blocked") is True
        assert "errors" in res

    def test_surrogate_normal_submission(self) -> None:
        """驗證合規參數建立參數集直通並排程。"""
        res = train_surrogate_model(
            design_parameters=[{"name": "t", "min": 1.0, "max": 3.0}],
            target_responses=["max_stress", "max_deformation"],
            num_samples=50,
            sampling_method="LHS",
            cop_target=0.80,
            tag="test_surrogate_pass",
        )

        assert res.get("ok") is True
        assert "job_id" in res
        assert res.get("status") == "QUEUED"


class TestIntentToolsMCPRegistration:
    """測試 intent_tools.py 導出的 MCP 工具註冊合約。"""

    def test_tools_are_callable(self, tmp_path: Path) -> None:
        """驗證 5 大 MCP 意圖工具具備 callable 特性並能直接執行。"""
        assert callable(intent_tools.run_drop_test)
        assert callable(intent_tools.run_shock_analysis)
        assert callable(intent_tools.run_random_vibration)
        assert callable(intent_tools.run_thermal_warpage)
        assert callable(intent_tools.train_surrogate_model)

        # 簡單調用測試
        res = intent_tools.run_drop_test(
            cad_path=str(tmp_path / "test.step"),
            drop_height_mm=500.0,
            tag="mcp_test_drop",
        )
        assert res.get("ok") is True