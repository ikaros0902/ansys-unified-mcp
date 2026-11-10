# Strictly ASCII English Comments
"""ANSYS Unified MCP - 能量守恆與交界面連續性前置物理安全閘門 (Energy Conservation Gate).

針對共軛熱傳 (CHT) 與流固耦合 (FSI) 等跨物理場邊界交界面，
實施嚴格熱通量守恆、溫度連續性與力/能量傳遞平衡核驗。
當交界面能量偏差 > 1.5% 或溫度跳躍 > 0.5 K 時，硬性阻斷並拒絕產出偽收斂報告。
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional, Set

from ansys_unified_mcp.core.gatekeeper.prescription import (
    ActionCodeEnum,
    CheckResult,
    PreFlightGatekeeperError,
    PreFlightPrescriptionReport,
    PrescriptionDetail,
    RuleStatusEnum,
    SeverityEnum,
)
from ansys_unified_mcp.core.gatekeeper.rules import BaseGateRule


class EnergyLeakageError(PreFlightGatekeeperError):
    """跨場耦合交界面能量不守恆阻斷例外。

    當共軛熱傳 (CHT) 或流固耦合 (FSI) 固液交界面出現熱通量或功/力不平衡時拋出。
    """

    def __init__(self, report: PreFlightPrescriptionReport) -> None:
        super().__init__(report)
        self.message = (
            "Energy leakage detected across multiphysics interface. "
            "Conservation criteria violated; pseudo-converged report rejected."
        )


class EnergyConservationGate(BaseGateRule):
    """GATE-ENG-001: 跨物理場交界面能量守恆與連續性防護規則。

    核驗指標：
    1. CHT 熱通量偏差：|q_fluid - q_solid| / max(|q_fluid|, 1e-9) <= 1.5%
    2. CHT 交界面溫度連續性：|T_fluid - T_solid| <= 0.5 K
    3. FSI 界面流固作用力平衡：|F_fluid - F_solid| / max(|F_fluid|, 1e-9) <= 1.5%
    4. FSI 界面功率/能量傳遞平衡：|P_fluid - P_solid| / max(|P_fluid|, 1e-9) <= 1.5%
    """

    rule_id = "GATE-ENG-001"
    rule_name = "Interface Energy Conservation & Continuity Guard"
    severity = SeverityEnum.FATAL
    target_workflows: Set[str] = {
        "cht",
        "fsi",
        "multiphysics",
        "system_coupling",
        "thermal_stress",
        "conjugate_heat_transfer",
    }

    # Standard physical tolerance thresholds
    HEAT_FLUX_REL_TOL: float = 0.015  # 1.5% maximum allowable heat flux discrepancy
    TEMP_JUMP_ABS_TOL: float = 0.5  # 0.5 K maximum allowable interface temperature jump
    FORCE_BALANCE_REL_TOL: float = 0.015  # 1.5% maximum allowable force imbalance
    POWER_TRANSFER_REL_TOL: float = 0.015  # 1.5% maximum allowable power transfer imbalance

    def check(self, context: Dict[str, Any]) -> CheckResult:
        """執行跨物理場交界面能量守恆與連續性檢驗。"""
        # 1. Extract interface thermal variables (CHT)
        q_fluid = context.get("q_fluid_wall") or context.get("fluid_heat_flux")
        q_solid = context.get("q_solid_wall") or context.get("solid_heat_flux")
        t_fluid = context.get("t_fluid_interface") or context.get("fluid_interface_temp")
        t_solid = context.get("t_solid_interface") or context.get("solid_interface_temp")

        # 2. Extract interface structural variables (FSI)
        f_fluid = context.get("f_fluid_interface") or context.get("fluid_interface_force")
        f_solid = context.get("f_solid_interface") or context.get("solid_interface_force")
        p_fluid = context.get("power_fluid_interface")
        p_solid = context.get("power_solid_interface")

        observed: Dict[str, Any] = {
            "q_fluid": q_fluid,
            "q_solid": q_solid,
            "t_fluid": t_fluid,
            "t_solid": t_solid,
            "f_fluid": f_fluid,
            "f_solid": f_solid,
            "p_fluid": p_fluid,
            "p_solid": p_solid,
        }

        threshold: Dict[str, Any] = {
            "heat_flux_rel_tol": self.HEAT_FLUX_REL_TOL,
            "temp_jump_abs_tol_K": self.TEMP_JUMP_ABS_TOL,
            "force_balance_rel_tol": self.FORCE_BALANCE_REL_TOL,
            "power_transfer_rel_tol": self.POWER_TRANSFER_REL_TOL,
        }

        violations = []

        # Check CHT heat flux conservation
        if q_fluid is not None and q_solid is not None:
            q_f = float(q_fluid)
            q_s = float(q_solid)
            denom = max(abs(q_f), 1e-9)
            flux_discrepancy = abs(q_f - q_s) / denom
            observed["flux_discrepancy_pct"] = flux_discrepancy * 100.0
            if flux_discrepancy > self.HEAT_FLUX_REL_TOL:
                violations.append(
                    f"交界面熱通量不守恆：偏差 {flux_discrepancy * 100.0:.2f}% "
                    f"超過工程門檻 {self.HEAT_FLUX_REL_TOL * 100.0:.1f}% "
                    f"(q_fluid={q_f:.3f} W/m^2, q_solid={q_s:.3f} W/m^2)"
                )

        # Check CHT interface temperature continuity
        if t_fluid is not None and t_solid is not None:
            t_f = float(t_fluid)
            t_s = float(t_solid)
            temp_jump = abs(t_f - t_s)
            observed["temp_jump_K"] = temp_jump
            if temp_jump > self.TEMP_JUMP_ABS_TOL:
                violations.append(
                    f"交界面溫度連續性破壞：溫度跳躍 {temp_jump:.3f} K "
                    f"超過工程門檻 {self.TEMP_JUMP_ABS_TOL:.1f} K "
                    f"(T_fluid={t_f:.3f} K, T_solid={t_s:.3f} K)"
                )

        # Check FSI force balance
        if f_fluid is not None and f_solid is not None:
            ff = float(f_fluid)
            fs = float(f_solid)
            denom_f = max(abs(ff), 1e-9)
            force_imbalance = abs(ff - fs) / denom_f
            observed["force_imbalance_pct"] = force_imbalance * 100.0
            if force_imbalance > self.FORCE_BALANCE_REL_TOL:
                violations.append(
                    f"FSI 流固界面作用力不平衡：偏差 {force_imbalance * 100.0:.2f}% "
                    f"超過門檻 {self.FORCE_BALANCE_REL_TOL * 100.0:.1f}% "
                    f"(F_fluid={ff:.3f} N, F_solid={fs:.3f} N)"
                )

        # Check FSI power transfer balance
        if p_fluid is not None and p_solid is not None:
            pf = float(p_fluid)
            ps = float(p_solid)
            denom_p = max(abs(pf), 1e-9)
            power_imbalance = abs(pf - ps) / denom_p
            observed["power_imbalance_pct"] = power_imbalance * 100.0
            if power_imbalance > self.POWER_TRANSFER_REL_TOL:
                violations.append(
                    f"FSI 界面能量/功率傳遞不平衡：偏差 {power_imbalance * 100.0:.2f}% "
                    f"超過門檻 {self.POWER_TRANSFER_REL_TOL * 100.0:.1f}% "
                    f"(P_fluid={pf:.3f} W, P_solid={ps:.3f} W)"
                )

        if violations:
            diagnosis_msg = "；".join(violations)
            return CheckResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                status=RuleStatusEnum.BLOCKED,
                severity=self.severity,
                observed_value=observed,
                required_threshold=threshold,
                diagnosis=diagnosis_msg,
                prescription=PrescriptionDetail(
                    action_code=ActionCodeEnum.GENERIC_REMEDIATION.value,
                    suggested_fix=(
                        "交界面能量或通量不守恆，嚴禁採信偽收斂結果。"
                        "建議調整 System Coupling 鬆弛因子 (Under-Relaxation Factor 0.3~0.5)、"
                        "增加耦合迭代步數 (>= 20 sub-iterations)，或加密流固交界面網格以縮小內插誤差。"
                    ),
                    code_snippet=(
                        "# System Coupling / CHT Convergence Tuning\n"
                        "syc.Participant('Fluent').DataTransfer('HeatRate').UnderRelaxationFactor = 0.5\n"
                        "syc.Participant('Mechanical').DataTransfer('Temperature').UnderRelaxationFactor = 0.5\n"
                        "syc.CouplingStep.MaximumIterations = 50"
                    ),
                ),
            )

        return CheckResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            status=RuleStatusEnum.PASSED,
            severity=SeverityEnum.INFO,
            observed_value=observed,
            required_threshold=threshold,
            diagnosis="跨物理場交界面能量守恆與連續性檢驗合格。",
        )

    def validate_interface(
        self,
        context: Dict[str, Any],
        raise_on_leakage: bool = True,
        session_id: Optional[str] = None,
    ) -> PreFlightPrescriptionReport:
        """主動核驗交界面能量守恆狀態。

        若核驗失敗且 raise_on_leakage=True，主動拋出 EnergyLeakageError，
        並可依賴 session_id 同步將 DAMG 狀態機下游標記為 DIRTY / UNSATISFIED。
        """
        result = self.check(context)
        report = PreFlightPrescriptionReport(
            passed=(result.status == RuleStatusEnum.PASSED),
            blocking_issues_count=1 if result.status == RuleStatusEnum.BLOCKED else 0,
            warnings_count=1 if result.status == RuleStatusEnum.WARNING else 0,
            checks=[result],
        )

        if not report.passed:
            # Sync with DAMG state machine if available
            if session_id:
                try:
                    from ansys_unified_mcp.core.damg import DAMGStateMachine
                    sm = DAMGStateMachine.get_instance(session_id)
                    # Invalidate downstream results
                    for node in [
                        "TEMPERATURE_DISTRIBUTION_EXTRACTED",
                        "FLOW_FIELD_RESULTS_EXTRACTED",
                        "STRUCTURAL_SOLUTION_SOLVED",
                        "THERMAL_RESULTS_EXTRACTED",
                    ]:
                        if node in sm.nodes:
                            sm.invalidate_node_and_downstream(node)
                except Exception:
                    pass

            if raise_on_leakage:
                raise EnergyLeakageError(report)

        return report
