"""ANSYS Unified MCP 2.0 - 前置安全閘門核心引擎 (Pre-Flight Gatekeeper Engine).

在模擬作業正式進入求解器前執行硬性物理檢核，
彙整 8 大物理安全規則，未達標強制阻斷並產出結構化自愈處方箋。
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ansys_unified_mcp.gatekeeper.prescription import (
    CheckResult,
    PreFlightGatekeeperError,
    PreFlightPrescriptionReport,
    RuleStatusEnum,
    SeverityEnum,
)
from ansys_unified_mcp.gatekeeper.rules import BaseGateRule
from ansys_unified_mcp.gatekeeper.rules.drop_impact_rules import (
    ContactIntegrityRule,
    CriticalTimeStepRule,
    DropVelocityVectorRule,
)
from ansys_unified_mcp.gatekeeper.rules.thermal_rules import (
    NonZeroSecantCTERule,
    ZeroStressReferenceTemperatureRule,
)
from ansys_unified_mcp.gatekeeper.rules.unit_consistency import UnitConsistencyRule
from ansys_unified_mcp.gatekeeper.rules.vibration_rules import (
    ModalCutoffFrequencyRule,
    ModalEffectiveMassRatioRule,
)


class Gatekeeper:
    """Pre-Flight 物理安全閘門主控引擎。"""

    def __init__(self, rules: Optional[List[BaseGateRule]] = None) -> None:
        if rules is not None:
            self.rules = rules
        else:
            # 註冊標準 8 大硬性物理檢核規則庫
            self.rules = [
                # 隨機振動 / 反應譜規則
                ModalEffectiveMassRatioRule(),      # GATE-VIB-001
                ModalCutoffFrequencyRule(),          # GATE-VIB-002
                # 落摔 / 衝擊規則
                DropVelocityVectorRule(),            # GATE-DRP-001
                CriticalTimeStepRule(),              # GATE-DRP-002
                ContactIntegrityRule(),              # GATE-DRP-003
                # 熱翹曲規則
                NonZeroSecantCTERule(),              # GATE-THM-001
                ZeroStressReferenceTemperatureRule(),# GATE-THM-002
                # 單位制一致性規則 (適用所有工況)
                UnitConsistencyRule(),               # GATE-UNI-001
            ]

    def validate(
        self,
        workflow_type: str,
        context: Dict[str, Any],
        raise_on_blocked: bool = False,
        rules_filter: Optional[List[str]] = None,
    ) -> PreFlightPrescriptionReport:
        """對指定工作流執行物理前置閘門綜合檢驗。

        Args:
            workflow_type: 工作流類型 ('drop_test', 'random_vibration', 'thermal_warpage', etc.)
            context: 包含模型、幾何、邊界條件、材料參數的上下文字典
            raise_on_blocked: 若存在 FATAL 阻斷項目，是否主動拋出 PreFlightGatekeeperError
            rules_filter: 可選，指定僅執行特定 rule_id 清單 (如 ['GATE-VIB-001'])

        Returns:
            PreFlightPrescriptionReport: 結構化處方箋報告實例
        """
        results: List[CheckResult] = []
        blocking_count = 0
        warning_count = 0

        for rule in self.rules:
            # 若有指定過濾清單
            if rules_filter and rule.rule_id not in rules_filter:
                continue

            # 檢核是否適用當前工況
            if not rule.applies_to(workflow_type):
                continue

            # 執行規則檢驗
            res = rule.check(context)
            results.append(res)

            if res.status == RuleStatusEnum.BLOCKED:
                if res.severity == SeverityEnum.FATAL:
                    blocking_count += 1
                elif res.severity == SeverityEnum.WARNING:
                    warning_count += 1
            elif res.status == RuleStatusEnum.WARNING:
                warning_count += 1

        passed = blocking_count == 0
        now_str = datetime.now(timezone.utc).isoformat()

        report = PreFlightPrescriptionReport(
            gatekeeper="pre_flight_sentinel",
            timestamp=now_str,
            passed=passed,
            blocking_issues_count=blocking_count,
            warnings_count=warning_count,
            checks=results,
        )

        if raise_on_blocked and not passed:
            raise PreFlightGatekeeperError(report)

        return report

    # 快捷檢驗介面 (對齊 spec_report.md Features 20~24)
    def check_modal_effective_mass(
        self,
        effective_mass_ratio: Dict[str, float],
        excitation_direction: Optional[str] = None,
        num_modes: int = 12,
    ) -> CheckResult:
        """Feature 20: 強制檢核三向有效模態質量累積佔比 (>= 90%)。"""
        rule = ModalEffectiveMassRatioRule()
        ctx = {
            "effective_mass_ratio": effective_mass_ratio,
            "excitation_direction": excitation_direction,
            "num_modes": num_modes,
        }
        return rule.check(ctx)

    def check_cutoff_frequency(
        self,
        cutoff_frequency_hz: float,
        max_excitation_frequency_hz: float,
    ) -> CheckResult:
        """Feature 21: 檢核模態截斷頻率充裕度 (>= 1.5x 激振上限)。"""
        rule = ModalCutoffFrequencyRule()
        ctx = {
            "cutoff_frequency_hz": cutoff_frequency_hz,
            "max_excitation_frequency_hz": max_excitation_frequency_hz,
        }
        return rule.check(ctx)

    def check_drop_impact_setup(
        self,
        velocity_vector: List[float],
        floor_normal: List[float] = [0.0, 0.0, 1.0],
        estimated_dt_s: Optional[float] = None,
        mass_scaling_dt2ms: float = 0.0,
        has_rigid_wall: bool = True,
        has_contact_pairs: bool = True,
    ) -> PreFlightPrescriptionReport:
        """Feature 22: 綜合檢核落摔初速方向、CFL 時間步長與接觸完整性。"""
        ctx = {
            "velocity_vector": velocity_vector,
            "floor_normal": floor_normal,
            "estimated_dt_s": estimated_dt_s,
            "mass_scaling_dt2ms": mass_scaling_dt2ms,
            "has_rigid_wall": has_rigid_wall,
            "has_contact_pairs": has_contact_pairs,
        }
        return self.validate(workflow_type="drop_test", context=ctx)

    def check_thermal_warpage_setup(
        self,
        secant_cte: Optional[float] = None,
        reference_temperature_c: Optional[float] = None,
        operating_temperature_c: Optional[float] = None,
    ) -> PreFlightPrescriptionReport:
        """Feature 23: 檢核材料溫度相依 CTE 與零應力參考溫度 T_ref。"""
        ctx = {
            "secant_cte": secant_cte,
            "reference_temperature_c": reference_temperature_c,
            "temperature_operating_c": operating_temperature_c,
        }
        return self.validate(workflow_type="thermal_warpage", context=ctx)

    def check_unit_system_consistency(
        self,
        length_unit: str = "mm",
        stress_unit: str = "MPa",
        density_value: Optional[float] = None,
        youngs_modulus_value: Optional[float] = None,
    ) -> CheckResult:
        """Feature 24: 強制檢查長度-質量-時間-應力-密度單位系統一致性。"""
        rule = UnitConsistencyRule()
        ctx = {
            "length_unit": length_unit,
            "stress_unit": stress_unit,
            "density_value": density_value,
            "youngs_modulus_value": youngs_modulus_value,
        }
        return rule.check(ctx)
