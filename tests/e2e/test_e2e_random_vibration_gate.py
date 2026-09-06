# -*- coding: utf-8 -*-
"""Tier 3 合成端到端場景驗收測試 (一)：隨機振動模態質量不足物理閘門硬性阻斷

驗收場景規格 (對齊 TEST_INFRA.md Section 5.1 與 ORIGINAL_REQUEST.md)：
1. 工況類型：Random Vibration (PSD 分析)
2. 觸發條件：
   - 模態分析提取 10 階，有效模態質量比 X=82.4%, Y=85.1%, Z=79.3% (任一向或全部 < 90%)
   - 或截斷頻率 1850 Hz < 1.5 * 2000 Hz = 3000 Hz
3. 預期行為：
   - Pre-Flight Gatekeeper 立即觸發硬性物理攔截，拒絕建立 PSD 求解任務
   - 拋出 PreFlightGatekeeperError 例外，嚴格禁止送算
   - 產出結構化自愈處方箋 JSON，包含：
     * 規則代碼：GATE-VIB-001 (或 PHYS-001-MASS-DEFICIENT)
     * 嚴重度：FATAL
     * 診斷訊息：指明 X/Y/Z 質量不足與未達 90% 門檻
     * 具體修復建議與代碼片段：建議增加模態提取階數 (至 35~60 階)
4. 對比驗證：合規輸入 (>= 90%) 順利放行 (Happy Path)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
import pytest

# 相容防禦注入
import ansys_unified_mcp.core.sentinel.parsers.fluent as fluent_parser_mod
if not hasattr(fluent_parser_mod, "FluentLogParser"):
    fluent_parser_mod.FluentLogParser = fluent_parser_mod.FluentResidualParser  # type: ignore[attr-defined]

import ansys_unified_mcp.core.sentinel.parsers.lsdyna as lsdyna_parser_mod
if not hasattr(lsdyna_parser_mod, "LSDynaParser"):
    lsdyna_parser_mod.LSDynaParser = lsdyna_parser_mod.LSDynaGlstatParser  # type: ignore[attr-defined]

from ansys_unified_mcp.gatekeeper import (
    ActionCodeEnum,
    Gatekeeper,
    PreFlightGatekeeperError,
    PreFlightPrescriptionReport,
    RuleStatusEnum,
    SeverityEnum,
)
from ansys_unified_mcp.workflows.random_vibration import run_random_vibration


class TestE2ERandomVibrationGatekeeper:
    """三大端到端驗收場景一：隨機振動物理安全閘門阻斷與處方箋閉環。"""

    def test_random_vibration_mass_deficient_hard_blocking(self) -> None:
        """場景 1.1：有效模態質量不足 90% (80% / 79.3%) 立即引發 PreFlightGatekeeperError 硬性阻斷。"""
        gatekeeper = Gatekeeper()

        # 模擬 10 階模態提取結果：X=82.4%, Y=85.1%, Z=79.3% (< 90%)
        mass_ratios = {"x": 0.824, "y": 0.851, "z": 0.793}
        context = {
            "effective_mass_ratio": mass_ratios,
            "excitation_direction": "ALL",
            "num_modes": 10,
            "cutoff_frequency_hz": 1850.0,
            "max_excitation_frequency_hz": 2000.0,  # 要求 cutoff >= 3000 Hz
        }

        # 斷言 validate 傳入 raise_on_blocked=True 時硬性拋出 PreFlightGatekeeperError
        with pytest.raises(PreFlightGatekeeperError) as exc_info:
            gatekeeper.validate(
                workflow_type="random_vibration",
                context=context,
                raise_on_blocked=True,
            )

        err: PreFlightGatekeeperError = exc_info.value
        report = err.report

        # 1. 驗證報告整體狀態
        assert report.passed is False
        assert report.blocking_issues_count >= 1

        # 2. 驗證結構化自愈處方箋 JSON Schema
        report_dict = report.to_dict()
        assert "gatekeeper" in report_dict
        assert "timestamp" in report_dict
        assert "checks" in report_dict

        # 3. 驗證有效模態質量阻斷項 (GATE-VIB-001 或 PHYS-001-MASS-DEFICIENT)
        mass_checks = [
            c for c in report.checks
            if c.rule_id in ("GATE-VIB-001", "PHYS-001-MASS-DEFICIENT")
        ]
        assert len(mass_checks) == 1, "必須包含模態有效質量阻斷規則項"
        mass_check = mass_checks[0]

        assert mass_check.status == RuleStatusEnum.BLOCKED
        assert mass_check.severity == SeverityEnum.FATAL
        assert "90.0%" in mass_check.diagnosis or "未達" in mass_check.diagnosis
        assert "82.4%" in mass_check.diagnosis or "79.3%" in mass_check.diagnosis

        # 4. 驗證自愈處方箋內容
        assert mass_check.prescription is not None
        assert mass_check.prescription.action_code == ActionCodeEnum.INCREASE_MODES_AND_CUTOFF.value
        assert "NumberOfModes" in mass_check.prescription.code_snippet
        assert "30" in mass_check.prescription.code_snippet or "35" in mass_check.prescription.code_snippet

    def test_random_vibration_workflow_interception(self) -> None:
        """場景 1.2：透過 run_random_vibration 工作流進入點調用時，阻斷未達標工況並回傳處方箋。"""
        psd_table = [(20.0, 0.01), (100.0, 0.05), (1000.0, 0.05), (2000.0, 0.01)]

        result = run_random_vibration(
            cad_path="bracket.pmdb",
            psd_table=psd_table,
            direction="Z",
            num_modes=10,
            effective_mass_ratio={"X": 0.80, "Y": 0.82, "Z": 0.78},  # 均低於 90%
            cutoff_frequency_hz=1800.0,
            tag="e2e_gate_check",
        )

        assert result["ok"] is False
        assert result["blocked"] is True
        assert "物理前置安全閘門檢核未通過" in result["message"]

        # 驗證傳回之自愈處方箋
        prescription_data = result["prescription_report"]
        assert prescription_data["passed"] is False
        assert prescription_data["blocking_issues_count"] >= 1

        # 斷言 JSON 可直接序列化與持久化
        json_str = json.dumps(prescription_data, ensure_ascii=False, indent=2)
        assert "GATE-VIB-001" in json_str or "PHYS-001" in json_str

    def test_random_vibration_compliant_happy_path(self) -> None:
        """場景 1.3：合規輸入 (三向有效質量 >= 90% 且截斷頻率充裕) 前置安全閘門順利放行。"""
        gatekeeper = Gatekeeper()

        # 三向累積質量達到 93.5%, 92.0%, 95.1% (均 >= 90%)
        # 激振上限 2000 Hz，截斷頻率 3200 Hz (>= 1.5 * 2000 = 3000 Hz)
        context = {
            "effective_mass_ratio": {"X": 0.935, "Y": 0.920, "Z": 0.951},
            "excitation_direction": "Z",
            "num_modes": 50,
            "cutoff_frequency_hz": 3200.0,
            "max_excitation_frequency_hz": 2000.0,
            "length_unit": "mm",
            "mass_unit": "kg",
            "time_unit": "s",
            "stress_unit": "Pa",
            "youngs_modulus_pa": 2.0e11,
            "density_kg_m3": 7850.0,
        }

        report = gatekeeper.validate(
            workflow_type="random_vibration",
            context=context,
            raise_on_blocked=True,
        )

        assert report.passed is True
        assert report.blocking_issues_count == 0
        vib_check = [c for c in report.checks if c.rule_id == "GATE-VIB-001"][0]
        assert vib_check.status == RuleStatusEnum.PASSED
