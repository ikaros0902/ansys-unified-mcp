"""ANSYS Unified MCP 2.0 - 單位制一致性前置物理安全閘門 (Unit Consistency Rules).

包含：
- GATE-UNI-001: 長度-質量-時間-應力-密度單位體系嚴格校驗
  防止 MPa 與 kg/m³ 混用造成 10^6~10^9 級別加速度/應力暴衝。
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


class UnitConsistencyRule(BaseGateRule):
    """GATE-UNI-001: 單位系統自洽性防護規則。

    在有限元分析 (FEA) 與計算流體力學 (CFD) 中，單位系統必須嚴格自洽：
    - mm-tonne-s (結構 FEA 標準): 長度 mm, 質量 tonne (10^3 kg), 時間 s, 應力/模量 MPa, 密度 tonne/mm³ (鋼材 ~7.85e-9)
    - SI / MKS: 長度 m, 質量 kg, 時間 s, 應力/模量 Pa, 密度 kg/m³ (鋼材 ~7850)
    - mm-kg-ms (顯式動力學常用): 長度 mm, 質量 kg, 時間 ms (10^-3 s), 應力 GPa, 密度 kg/mm³ (鋼材 ~7.85e-6)

    若長度採用 mm、應力採用 MPa，但材料密度誤設為 kg/m³ (如 7850 kg/m³)，
    換算慣性項時質量將暴增 10^9 倍，引發求解器爆散崩潰或假性應力暴衝。
    """

    rule_id = "GATE-UNI-001"
    rule_name = "Unit System Consistency Guard"
    severity = SeverityEnum.FATAL
    target_workflows: Set[str] = set()  # 空集合代表適用所有工作流

    def check(self, context: Dict[str, Any]) -> CheckResult:
        length_unit = str(context.get("length_unit", "mm")).strip().lower()
        stress_unit = str(context.get("stress_unit", "mpa")).strip().lower()
        density_val = context.get("density_value", context.get("density"))
        density_unit = context.get("density_unit")
        youngs_modulus = context.get("youngs_modulus_value", context.get("youngs_modulus_mpa"))

        observed: Dict[str, Any] = {
            "length_unit": length_unit,
            "stress_unit": stress_unit,
            "density_value": density_val,
            "density_unit": density_unit,
            "youngs_modulus": youngs_modulus,
        }
        threshold: Dict[str, Any] = {
            "supported_systems": ["mm-tonne-s-MPa", "m-kg-s-Pa", "mm-kg-ms-GPa"],
            "consistency_required": True,
        }

        # 檢驗 1: mm-tonne-s 體系下的密度數值範圍
        # 在長度為 mm 且應力為 MPa 時，工程結構材料密度 (如鋼、鋁、銅、樹脂) 在 tonne/mm³ 範圍約 1e-10 ~ 1e-7
        # 若使用者填入密度 > 0.05 (例如 7850, 2700, 1.2, 1000)，必定是誤填了 kg/m³ 或 g/cm³！
        if length_unit in {"mm", "millimeter"} and stress_unit in {"mpa", "n/mm2"}:
            if density_val is not None:
                d_float = float(density_val)
                if d_float > 0.05:
                    suggested_density = d_float * 1.0e-12 if d_float > 100 else d_float * 1.0e-9
                    return CheckResult(
                        rule_id=self.rule_id,
                        rule_name=self.rule_name,
                        status=RuleStatusEnum.BLOCKED,
                        severity=self.severity,
                        observed_value=observed,
                        required_threshold=threshold,
                        diagnosis=(
                            f"單位系統發生致命衝突：當前長度單位為 {length_unit} (對應 MPa 應力體系)，"
                            f"但材料密度數值為 {d_float} (明顯混用 kg/m³ 或 g/cm³)。"
                            f"在 mm-tonne-s 體系中，鋼材密度應為 ~7.85e-9 tonne/mm³。"
                            f"當前輸入會使模型等效質量暴增 10^9 ~ 10^12 倍，造成重大慣性發散！"
                        ),
                        prescription=PrescriptionDetail(
                            action_code=ActionCodeEnum.CONVERT_TO_CONSISTENT_UNIT_SYSTEM.value,
                            suggested_fix=(
                                f"請將密度數值轉換為 tonne/mm³ 單位制。"
                                f"若原數值為 kg/m³，請乘以 1e-12 (換算後約 {suggested_density:.2e} tonne/mm³)。"
                            ),
                            code_snippet=(
                                f"# 將 kg/m³ 轉換為 tonne/mm³\n"
                                f"input_density_kg_m3 = {d_float}\n"
                                f"density_tonne_mm3 = input_density_kg_m3 * 1.0e-12  # => {suggested_density:.2e}\n"
                                "material.SetPropertyData('Density', density_tonne_mm3)"
                            ),
                        ),
                    )

            # 檢驗彈性模量：在 MPa 單位下，鋼材 ~2.0e5 MPa。若填入 2.0e11，顯然是 Pa
            if youngs_modulus is not None:
                e_float = float(youngs_modulus)
                if e_float > 1.0e7:
                    suggested_e = e_float * 1.0e-6
                    return CheckResult(
                        rule_id=self.rule_id,
                        rule_name=self.rule_name,
                        status=RuleStatusEnum.BLOCKED,
                        severity=self.severity,
                        observed_value=observed,
                        required_threshold=threshold,
                        diagnosis=(
                            f"彈性模量數值為 {e_float:.2e}，在 MPa 單位制下過度龐大 (可能誤填為 Pa 單位)。"
                            f"鋼材標準楊氏模量約為 200,000 MPa (2.0e5)，當前數值將使剛度虛增 10^6 倍！"
                        ),
                        prescription=PrescriptionDetail(
                            action_code=ActionCodeEnum.CONVERT_TO_CONSISTENT_UNIT_SYSTEM.value,
                            suggested_fix="請將彈性模量單位由 Pa 換算為 MPa (除以 1e6)。",
                            code_snippet=f"youngs_modulus_mpa = {suggested_e:.1f}  # 換算為 MPa",
                        ),
                    )

        # 檢驗 2: SI (m-kg-s) 體系下的密度數值
        if length_unit in {"m", "meter"} and stress_unit in {"pa", "n/m2"}:
            if density_val is not None:
                d_float = float(density_val)
                if d_float < 1.0:
                    return CheckResult(
                        rule_id=self.rule_id,
                        rule_name=self.rule_name,
                        status=RuleStatusEnum.BLOCKED,
                        severity=self.severity,
                        observed_value=observed,
                        required_threshold=threshold,
                        diagnosis=(
                            f"當前長度單位為公尺 (m) / 應力單位為 Pa (標準 SI 制)，"
                            f"但密度數值為 {d_float} (小於 1.0，疑似誤填 tonne/mm³ 或 g/cm³)。"
                            "在 SI 制下鋼材密度應為 ~7850 kg/m³。"
                        ),
                        prescription=PrescriptionDetail(
                            action_code=ActionCodeEnum.CONVERT_TO_CONSISTENT_UNIT_SYSTEM.value,
                            suggested_fix="請將密度轉換為標準 kg/m³ (例如鋼材 7850 kg/m³)。",
                            code_snippet="density_kg_m3 = 7850.0  # SI 制標準密度",
                        ),
                    )

        # 檢驗 3: 明確字串單位標記衝突
        if density_unit:
            d_unit_str = str(density_unit).strip().lower()
            if length_unit in {"mm", "millimeter"} and d_unit_str in {"kg/m3", "kg/m^3"}:
                return CheckResult(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    status=RuleStatusEnum.BLOCKED,
                    severity=self.severity,
                    observed_value=observed,
                    required_threshold=threshold,
                    diagnosis=f"幾何長度單位為 {length_unit}，但明確指定之密度單位為 {density_unit}，單位制不相容！",
                    prescription=PrescriptionDetail(
                        action_code=ActionCodeEnum.CONVERT_TO_CONSISTENT_UNIT_SYSTEM.value,
                        suggested_fix="將密度單位改設為 tonne/mm³ 或將幾何尺度縮放至公尺 m。",
                        code_snippet="material.Density.Unit = 'tonne/mm^3'",
                    ),
                )

        return CheckResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            status=RuleStatusEnum.PASSED,
            severity=SeverityEnum.INFO,
            observed_value=observed,
            required_threshold=threshold,
            diagnosis="長度-質量-時間-應力-密度單位制自洽，無跨量級暴衝風險。",
            prescription=None,
        )
