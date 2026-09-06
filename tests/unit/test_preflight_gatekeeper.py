# -*- coding: utf-8 -*-
"""Tier 2 單元測試：求解前置安全閘門 (Gatekeeper) 與自愈處方箋測試

覆蓋 R4 規範核心 8 大硬性物理阻斷與結構化自愈處方箋 JSON 輸出：
1. GATE-VIB-001: 隨機振動/反應譜有效模態質量累積佔比 (< 90% 阻斷)
2. GATE-VIB-002: 模態截斷頻率充裕度 (< 1.5x 激振上限阻斷)
3. GATE-DRP-001: 落摔初速度向量方向反向阻斷 (v · n >= 0 反向飛離阻斷)
4. GATE-DRP-002: 臨界時間步長與質量縮放阻斷 (dt < 1e-9 且未設 dt2ms 阻斷)
5. GATE-DRP-003: 落摔剛體/接觸完整性阻斷 (無剛性地面/接觸阻斷)
6. GATE-THM-001: 熱翹曲材料熱膨脹係數非零阻斷 (CTE <= 0 阻斷)
7. GATE-THM-002: 熱翹曲零應力參考溫度 T_ref 缺失阻斷 (T_ref 未設定阻斷)
8. GATE-UNI-001: 單位制一致性防護 (MPa 與 kg/m³ 混用阻斷)
9. 結構化自愈處方箋 JSON Schema 格式與 PreFlightGatekeeperError 例外驗證
10. 全物理合規正常放行 (Happy Path)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import pytest

from ansys_unified_mcp.gatekeeper import (
    Gatekeeper,
    PreFlightGatekeeperError,
    PreFlightPrescriptionReport,
    CheckResult,
    RuleStatusEnum,
    SeverityEnum,
    ActionCodeEnum,
    ModalEffectiveMassRatioRule,
    ModalCutoffFrequencyRule,
    DropVelocityVectorRule,
    CriticalTimeStepRule,
    ContactIntegrityRule,
    NonZeroSecantCTERule,
    ZeroStressReferenceTemperatureRule,
    UnitConsistencyRule,
)

# 別名相容規範定義
PreFlightGatekeeper = Gatekeeper


class TestPreFlightGatekeeperRules:
    """測試 8 大硬性物理阻斷規則之個別檢核邏輯。"""

    @pytest.fixture
    def gatekeeper(self) -> Gatekeeper:
        return Gatekeeper()

    def test_modal_effective_mass_ratio_blocking(self, gatekeeper: Gatekeeper) -> None:
        """1. GATE-VIB-001: 隨機振動模態質量 < 90% 觸發阻斷並產出自愈處方。"""
        # X=82.4%, Y=85.1%, Z=79.3% (三向皆低於 90%)
        result = gatekeeper.check_modal_effective_mass(
            effective_mass_ratio={"x": 0.824, "y": 0.851, "z": 0.793},
            excitation_direction="ALL",
            num_modes=10,
        )
        assert result.status == RuleStatusEnum.BLOCKED
        assert result.rule_id == "GATE-VIB-001"
        assert result.severity == SeverityEnum.FATAL
        assert result.prescription is not None
        assert result.prescription.action_code == ActionCodeEnum.INCREASE_MODES_AND_CUTOFF.value
        assert "90.0%" in result.diagnosis

    def test_modal_cutoff_frequency_blocking(self, gatekeeper: Gatekeeper) -> None:
        """2. GATE-VIB-002: 截斷頻率充裕度不足觸發阻斷。"""
        # 激振上限 2000 Hz，要求截斷頻率 >= 3000 Hz，實際僅 2500 Hz
        result = gatekeeper.check_cutoff_frequency(
            cutoff_frequency_hz=2500.0,
            max_excitation_frequency_hz=2000.0,
        )
        assert result.status == RuleStatusEnum.BLOCKED
        assert result.rule_id == "GATE-VIB-002"
        assert result.severity == SeverityEnum.FATAL
        threshold_val = result.required_threshold.get("required_min_cutoff_hz", result.required_threshold.get("required_cutoff_hz"))
        assert threshold_val == pytest.approx(3000.0)
        assert result.prescription is not None
        assert result.prescription.action_code == ActionCodeEnum.EXTEND_FREQUENCY_RANGE.value

    def test_drop_velocity_vector_inverted_blocking(self, gatekeeper: Gatekeeper) -> None:
        """3. GATE-DRP-001: 落摔初速度向量反向飛離觸發阻斷。"""
        rule = DropVelocityVectorRule()
        # 地面法向向 +Z [0, 0, 1]，初速誤設為向上 [0, 0, 9800] (點積 > 0)
        result = rule.check({
            "velocity_vector": [0.0, 0.0, 9800.0],
            "floor_normal": [0.0, 0.0, 1.0],
        })
        assert result.status == RuleStatusEnum.BLOCKED
        assert result.rule_id == "GATE-DRP-001"
        assert result.severity == SeverityEnum.FATAL
        assert result.observed_value["dot_product"] > 0.0
        assert result.prescription is not None
        assert result.prescription.action_code == ActionCodeEnum.INVERT_VELOCITY_OR_NORMAL.value

    def test_critical_timestep_and_mass_scaling_blocking(self, gatekeeper: Gatekeeper) -> None:
        """4. GATE-DRP-002: 步長過小且未設質量縮放觸發阻斷。"""
        rule = CriticalTimeStepRule()
        result = rule.check({
            "estimated_dt_s": 5.0e-10,
            "mass_scaling_dt2ms": 0.0,
        })
        assert result.status == RuleStatusEnum.BLOCKED
        assert result.rule_id == "GATE-DRP-002"
        assert result.severity == SeverityEnum.FATAL
        assert result.prescription is not None
        assert result.prescription.action_code == ActionCodeEnum.CONFIGURE_MASS_SCALING.value

    def test_contact_definition_missing_blocking(self, gatekeeper: Gatekeeper) -> None:
        """5. GATE-DRP-003: 接觸對/剛性牆缺失觸發穿透阻斷。"""
        rule = ContactIntegrityRule()
        result = rule.check({
            "has_rigid_wall": False,
            "has_contact_pairs": False,
        })
        assert result.status == RuleStatusEnum.BLOCKED
        assert result.rule_id == "GATE-DRP-003"
        assert result.severity == SeverityEnum.FATAL
        assert "穿透" in result.diagnosis
        assert result.prescription is not None
        assert result.prescription.action_code == ActionCodeEnum.DEFINE_RIGIDWALL_OR_CONTACT.value

    def test_thermal_cte_missing_or_zero_blocking(self, gatekeeper: Gatekeeper) -> None:
        """6. GATE-THM-001: 熱膨脹係數為 0 或缺失觸發阻斷。"""
        rule = NonZeroSecantCTERule()
        result = rule.check({"secant_cte": 0.0})
        assert result.status == RuleStatusEnum.BLOCKED
        assert result.rule_id == "GATE-THM-001"
        assert result.severity == SeverityEnum.FATAL
        assert result.prescription is not None
        assert result.prescription.action_code == ActionCodeEnum.ASSIGN_TEMPERATURE_DEPENDENT_CTE.value

    def test_reference_temperature_missing_blocking(self, gatekeeper: Gatekeeper) -> None:
        """7. GATE-THM-002: 零應力參考溫度 T_ref 缺失觸發阻斷。"""
        rule = ZeroStressReferenceTemperatureRule()
        result = rule.check({"reference_temperature_c": None})
        assert result.status == RuleStatusEnum.BLOCKED
        assert result.rule_id == "GATE-THM-002"
        assert result.severity == SeverityEnum.FATAL
        assert result.prescription is not None
        assert result.prescription.action_code == ActionCodeEnum.SPECIFY_REFERENCE_TEMPERATURE.value

    def test_unit_system_consistency_conflict_blocking(self, gatekeeper: Gatekeeper) -> None:
        """8. GATE-UNI-001: 單位制混用 (mm-MPa 搭配 7850 kg/m³) 觸發阻斷。"""
        result = gatekeeper.check_unit_system_consistency(
            length_unit="mm",
            stress_unit="MPa",
            density_value=7850.0,
        )
        assert result.status == RuleStatusEnum.BLOCKED
        assert result.rule_id == "GATE-UNI-001"
        assert result.severity == SeverityEnum.FATAL
        assert "10^6" in result.diagnosis or "10^12" in result.diagnosis
        assert result.prescription is not None
        assert result.prescription.action_code == ActionCodeEnum.CONVERT_TO_CONSISTENT_UNIT_SYSTEM.value


class TestPreFlightPrescriptionReport:
    """測試自愈處方箋結構化 JSON 生成與綜合裁決。"""

    def test_blocking_raises_exception_with_structured_prescription(self) -> None:
        """驗證存在阻斷項目且 raise_on_blocked=True 時，拋出 PreFlightGatekeeperError 且包含完整報告。"""
        gatekeeper = Gatekeeper()

        # 在隨機振動中傳入不足的模態質量比
        context = {
            "effective_mass_ratio": {"x": 0.75, "y": 0.82, "z": 0.68},
            "excitation_direction": "ALL",
            "num_modes": 12,
            "cutoff_frequency_hz": 3500.0,
            "max_excitation_frequency_hz": 2000.0,
            "length_unit": "mm",
            "stress_unit": "MPa",
            "density_value": 7.85e-9,
        }

        with pytest.raises(PreFlightGatekeeperError) as exc_info:
            gatekeeper.validate(
                workflow_type="random_vibration",
                context=context,
                raise_on_blocked=True,
            )

        report = exc_info.value.report
        assert report.passed is False
        assert report.blocking_issues_count >= 1

        # 斷言可正確導出為標準 JSON
        json_str = report.to_json()
        data = json.loads(json_str)
        assert data["passed"] is False
        assert "checks" in data
        assert any(c["rule_id"] == "GATE-VIB-001" for c in data["checks"])

    def test_all_checks_passed_happy_path(self) -> None:
        """驗證全部物理標準皆達標時，順利放行 (passed=True)。"""
        gatekeeper = Gatekeeper()

        context = {
            "effective_mass_ratio": {"x": 0.94, "y": 0.92, "z": 0.91},
            "excitation_direction": "ALL",
            "num_modes": 35,
            "cutoff_frequency_hz": 3500.0,
            "max_excitation_frequency_hz": 2000.0,
            "length_unit": "mm",
            "stress_unit": "MPa",
            "density_value": 7.85e-9,
        }

        report = gatekeeper.validate(
            workflow_type="random_vibration",
            context=context,
            raise_on_blocked=False,
        )

        assert report.passed is True
        assert report.blocking_issues_count == 0
        assert len(report.checks) >= 2
