"""ANSYS Unified MCP 2.0 - 熱翹曲前置物理安全閘門 (Thermal Warpage Rules).

包含：
- GATE-THM-001: 溫度相依 CTE 割線熱膨脹係數非零檢核
- GATE-THM-002: 零應力參考溫度 T_ref 賦予完整性檢核 ([-50, 400] °C)
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Set

from ansys_unified_mcp.gatekeeper.prescription import (
    ActionCodeEnum,
    CheckResult,
    PrescriptionDetail,
    RuleStatusEnum,
    SeverityEnum,
)
from ansys_unified_mcp.gatekeeper.rules import BaseGateRule


class NonZeroSecantCTERule(BaseGateRule):
    """GATE-THM-001: 材料熱膨脹係數非零檢核規則。

    在熱翹曲 (Thermal Warpage) 分析中，參與結構變形的材料必須具備非零割線熱膨脹係數 (Secant CTE > 0)。
    若 CTE 為零或未定義，熱應變 epsilon_th = alpha * Delta_T 將恆等於零，熱翹曲預測徹底失真。
    """

    rule_id = "GATE-THM-001"
    rule_name = "Non-Zero Secant CTE Guard"
    severity = SeverityEnum.FATAL
    target_workflows: Set[str] = {"thermal_warpage", "thermal_stress", "pcb_warpage"}

    MIN_REASONABLE_CTE: float = 1.0e-7  # 1/C
    MAX_REASONABLE_CTE: float = 1.0e-3  # 1/C

    def check(self, context: Dict[str, Any]) -> CheckResult:
        cte_val = context.get("secant_cte", context.get("cte_value", context.get("alpha_cte")))
        materials_cte = context.get("materials_cte")

        observed: Dict[str, Any] = {
            "secant_cte": cte_val,
            "materials_cte": materials_cte,
        }
        threshold: Dict[str, Any] = {
            "min_cte": self.MIN_REASONABLE_CTE,
            "max_cte": self.MAX_REASONABLE_CTE,
        }

        # 檢核單一 CTE 或材料清單
        if cte_val is None and not materials_cte:
            return CheckResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                status=RuleStatusEnum.BLOCKED,
                severity=self.severity,
                observed_value=observed,
                required_threshold=threshold,
                diagnosis="未提供材料熱膨脹係數 (Secant CTE) 數據，熱應變計算無法開展。",
                prescription=PrescriptionDetail(
                    action_code=ActionCodeEnum.ASSIGN_TEMPERATURE_DEPENDENT_CTE.value,
                    suggested_fix="請在材料模型中定義割線熱膨脹係數 CTE (如銅材 ~17 ppm/°C, 樹脂 ~50 ppm/°C)。",
                    code_snippet=(
                        "mat = Model.Materials.Add('Copper')\n"
                        "cte = mat.CreateProperty('Thermal Expansion')\n"
                        "cte.SetData(Variables=['Temperature'], Values=[Quantity(25, 'C')], PropertyData=[Quantity(1.7e-5, '1/C')])"
                    ),
                ),
            )

        # 檢查標量 CTE
        if cte_val is not None:
            c_float = float(cte_val)
            if c_float <= 0.0 or c_float < self.MIN_REASONABLE_CTE:
                return CheckResult(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    status=RuleStatusEnum.BLOCKED,
                    severity=self.severity,
                    observed_value=observed,
                    required_threshold=threshold,
                    diagnosis=(
                        f"割線熱膨脹係數數值為 {c_float:.2e} 1/C (<= 0 或低於合理工程門檻 {self.MIN_REASONABLE_CTE:.1e})。"
                        "熱應變公式 Delta_epsilon = alpha * (T - T_ref) 將輸出 0，翹曲分析將完全失去物理意義！"
                    ),
                    prescription=PrescriptionDetail(
                        action_code=ActionCodeEnum.ASSIGN_TEMPERATURE_DEPENDENT_CTE.value,
                        suggested_fix="請為實體材料指派正值且符合工程實際之熱膨脹係數。",
                        code_snippet=(
                            "# 指派標準銅箔與基板 CTE\n"
                            "mat_property.ThermalExpansion = 1.7e-5  # 1/C (17 ppm/C)"
                        ),
                    ),
                )

        # 檢查材料字典中是否有 <= 0
        if materials_cte and isinstance(materials_cte, dict):
            invalid_mats = {m: c for m, c in materials_cte.items() if float(c) <= 0.0}
            if invalid_mats:
                return CheckResult(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    status=RuleStatusEnum.BLOCKED,
                    severity=self.severity,
                    observed_value=observed,
                    required_threshold=threshold,
                    diagnosis=f"材料庫中存在 CTE <= 0 之無效定義: {invalid_mats}，將導致複合疊構應變錯誤！",
                    prescription=PrescriptionDetail(
                        action_code=ActionCodeEnum.ASSIGN_TEMPERATURE_DEPENDENT_CTE.value,
                        suggested_fix="修正上述材料之熱膨脹係數，確保各層材料之熱失配 (CTE Mismatch) 能真實反映。",
                        code_snippet="material.ThermalExpansion = 1.5e-5",
                    ),
                )

        return CheckResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            status=RuleStatusEnum.PASSED,
            severity=SeverityEnum.INFO,
            observed_value=observed,
            required_threshold=threshold,
            diagnosis="熱膨脹係數定義非零且處於合理物理工程區間，熱翹曲驅動項合格。",
            prescription=None,
        )


class ZeroStressReferenceTemperatureRule(BaseGateRule):
    """GATE-THM-002: 零應力參考溫度 T_ref 完整性檢核規則。

    熱應力與熱翹曲之基本本構方程式為: sigma = E * (epsilon - alpha * (T - T_ref))。
    若未明確指定參考溫度 T_ref，求解器可能使用未定義之 0 K 或 0 °C 預設值，
    引發與工作溫度溫差失真高達數百度之致命錯誤。
    """

    rule_id = "GATE-THM-002"
    rule_name = "Zero-Stress Reference Temperature Guard"
    severity = SeverityEnum.FATAL
    target_workflows: Set[str] = {"thermal_warpage", "thermal_stress", "pcb_warpage"}

    MIN_T_REF: float = -50.0  # °C
    MAX_T_REF: float = 400.0  # °C

    def check(self, context: Dict[str, Any]) -> CheckResult:
        t_ref = context.get("reference_temperature_c")
        if t_ref is None:
            t_ref = context.get("temperature_ref_c", context.get("t_ref"))

        observed: Dict[str, Any] = {
            "reference_temperature_c": t_ref,
            "operating_temperature_c": context.get("temperature_operating_c"),
        }
        threshold: Dict[str, Any] = {
            "min_allowed_t_ref_c": self.MIN_T_REF,
            "max_allowed_t_ref_c": self.MAX_T_REF,
            "required": True,
        }

        if t_ref is None:
            return CheckResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                status=RuleStatusEnum.BLOCKED,
                severity=self.severity,
                observed_value=observed,
                required_threshold=threshold,
                diagnosis="未指定零應力參考溫度 T_ref，熱變形公式溫差 Delta_T = (T - T_ref) 無法計算！",
                prescription=PrescriptionDetail(
                    action_code=ActionCodeEnum.SPECIFY_REFERENCE_TEMPERATURE.value,
                    suggested_fix="請明確指定零應力參考溫度 (如固化溫度 260 °C、熱壓成型溫度或常溫 22 °C/25 °C)。",
                    code_snippet=(
                        "structural_env = Model.Analyses[0].Environment\n"
                        "structural_env.ReferenceTemperature = Quantity(22.0, 'C')"
                    ),
                ),
            )

        t_ref_float = float(t_ref)
        if t_ref_float < self.MIN_T_REF or t_ref_float > self.MAX_T_REF:
            return CheckResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                status=RuleStatusEnum.BLOCKED,
                severity=self.severity,
                observed_value=observed,
                required_threshold=threshold,
                diagnosis=(
                    f"零應力參考溫度設定為 {t_ref_float} °C，超出合理工程實體範圍 "
                    f"[{self.MIN_T_REF}, {self.MAX_T_REF}] °C，疑似單位誤填 (如開氏度 K) 或數值錯誤！"
                ),
                prescription=PrescriptionDetail(
                    action_code=ActionCodeEnum.SPECIFY_REFERENCE_TEMPERATURE.value,
                    suggested_fix="請修正參考溫度至攝氏工程範圍 [-50, 400] °C。",
                    code_snippet="reference_temperature_c = 22.0  # 攝氏室溫基準",
                ),
            )

        return CheckResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            status=RuleStatusEnum.PASSED,
            severity=SeverityEnum.INFO,
            observed_value=observed,
            required_threshold=threshold,
            diagnosis="已明確指定物理合理區間之零應力參考溫度 T_ref，熱翹曲溫度基準合格。",
            prescription=None,
        )
