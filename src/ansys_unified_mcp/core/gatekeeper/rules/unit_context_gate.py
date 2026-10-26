# Strictly ASCII English Comments
"""ANSYS Unified MCP - 物理量綱與單位毒化前置防護閘門 (Unit Context Gate).

針對幾何尺寸 (CAD/Mesh Bounding Box)、材料彈性模量、密度與導熱率等核心物理量綱，
偵測單位混淆 (mm vs m 放大 1000 倍、MPa vs Pa 放大 10^6 倍、kg/m^3 vs tonne/mm^3 放大 10^12 倍)。
一旦偵測到量綱毒化，100% 阻斷並拋出 UnitPoisoningError，連動 DAMG 狀態機拒絕推進。
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


class UnitPoisoningError(PreFlightGatekeeperError):
    """物理量綱/單位混淆毒化阻斷例外。

    當模型中出現毫米/公尺混淆 (1000x)、帕斯卡/兆帕混淆 (10^6x) 或密度單位衝突時拋出。
    """

    def __init__(self, report: PreFlightPrescriptionReport) -> None:
        super().__init__(report)
        self.message = (
            "Physical unit poisoning detected. "
            "Dimensional mismatch would cause numerical blowup or non-physical results."
        )


class UnitContextGate(BaseGateRule):
    """GATE-UNI-002: 物理量綱與幾何/材料單位毒化防護規則。

    核驗指標：
    1. 幾何長度尺度毒化：mm 與 m 混淆 (特徵尺寸放大 1000 倍或縮小 1000 倍)
    2. 楊氏彈性模量毒化：MPa 與 Pa 混淆 (鋼材 2.0e11 誤填入 MPa 體系，或 2.0e5 誤填入 Pa 體系)
    3. 材料密度毒化：kg/m^3 與 tonne/mm^3 混淆 (鋼材 7850 誤填入 mm 體系)
    4. 泊松比熱力學正定性：nu <= 0.0 或 nu >= 0.5 違背連續介質力學上界
    """

    rule_id = "GATE-UNI-002"
    rule_name = "Physical Dimension & Unit Poisoning Guard"
    severity = SeverityEnum.FATAL
    target_workflows: Set[str] = set()  # Empty set applies to all workflows

    # Physical standard bounds
    MAX_MPA_YOUNGS_MODULUS: float = 1.0e7  # 10,000,000 MPa (diamond is ~1.2e6 MPa)
    MIN_PA_YOUNGS_MODULUS: float = 1.0e6  # Structural solids in Pa are > 1e6 Pa
    MAX_TONNE_MM3_DENSITY: float = 0.05  # Gold/Osmium is ~2.26e-8 tonne/mm^3; > 0.05 is kg/m^3
    MIN_KG_M3_DENSITY: float = 0.5  # Solid/liquid densities in SI are >= 0.5 kg/m^3

    def check(self, context: Dict[str, Any]) -> CheckResult:
        """執行幾何與材料物理量綱毒化檢驗。"""
        length_unit = str(context.get("length_unit", "mm")).strip().lower()
        stress_unit = str(context.get("stress_unit", "mpa")).strip().lower()
        density_val = context.get("density_value", context.get("density"))
        youngs_modulus = context.get("youngs_modulus_value", context.get("youngs_modulus_mpa", context.get("youngs_modulus")))
        poissons_ratio = context.get("poissons_ratio_value", context.get("poissons_ratio", context.get("nu")))
        char_length = context.get("characteristic_length", context.get("bounding_box_diagonal", context.get("length_scale")))

        observed: Dict[str, Any] = {
            "length_unit": length_unit,
            "stress_unit": stress_unit,
            "density_value": density_val,
            "youngs_modulus": youngs_modulus,
            "poissons_ratio": poissons_ratio,
            "characteristic_length": char_length,
        }

        threshold: Dict[str, Any] = {
            "max_mpa_youngs_modulus": self.MAX_MPA_YOUNGS_MODULUS,
            "max_tonne_mm3_density": self.MAX_TONNE_MM3_DENSITY,
            "poisson_valid_range": "0.0 < nu < 0.5",
        }

        violations = []
        suggested_fixes = []
        code_snippets = []

        # 1. Check Poisson's ratio thermodynamic bounds
        if poissons_ratio is not None:
            nu_f = float(poissons_ratio)
            if nu_f <= 0.0 or nu_f >= 0.5:
                violations.append(
                    f"泊松比 nu={nu_f} 超出熱力學正定邊界 (0.0 < nu < 0.5)，會導致剪切模量 G 或體積模量 K 計算發散"
                )
                suggested_fixes.append("請將泊松比修正至工程合理區間 (金屬 ~0.3，橡膠 ~0.49)。")
                code_snippets.append("material.poissons_ratio = 0.3")

        # 2. Check length unit poisoning (e.g. mm vs m confusion)
        if char_length is not None:
            L_val = float(char_length)
            # If length unit is 'm', but user supplied mm magnitude (e.g. 500.0 m for a small bracket or PCB)
            if length_unit in {"m", "meter"} and L_val > 100.0 and context.get("expected_domain") in {"electronics", "chassis", "bracket", "lens"}:
                violations.append(
                    f"長度單位混淆毒化：長度單位為 {length_unit} 但特徵尺寸為 {L_val:.1f} m (放大 1000 倍，疑將 mm 當作 m)"
                )
                suggested_fixes.append("請將幾何尺寸除以 1000 轉換為公尺，或將長度單位切換為 mm。")
                code_snippets.append(f"length_m = {L_val * 1e-3:.3f}")
            # If length unit is 'mm', but user supplied m magnitude (e.g. 0.05 mm for a 50mm part)
            elif length_unit in {"mm", "millimeter"} and 0.0 < L_val < 0.01 and context.get("expected_domain") in {"structural", "automotive", "beam"}:
                violations.append(
                    f"長度單位混淆毒化：長度單位為 {length_unit} 但特徵尺寸為 {L_val:.4f} mm (縮小 1000 倍，疑將 m 當作 mm)"
                )
                suggested_fixes.append("請將幾何尺寸乘以 1000 轉換為毫米。")
                code_snippets.append(f"length_mm = {L_val * 1e3:.1f}")

        # 3. Check Young's modulus unit poisoning
        if youngs_modulus is not None:
            E_val = float(youngs_modulus)
            # In MPa system, standard steel is 2.0e5 MPa. 2.0e11 is in Pa (10^6 times larger!)
            if (stress_unit in {"mpa", "n/mm2"} or length_unit in {"mm", "millimeter"}) and E_val > self.MAX_MPA_YOUNGS_MODULUS:
                violations.append(
                    f"楊氏彈性模量單位混淆毒化：模量數值為 {E_val:.2e}，在 MPa 單位制下暴增 10^6 倍 (誤填入 Pa 單位制)"
                )
                suggested_fixes.append("請將彈性模量除以 1e6 換算為 MPa (例如鋼材 2.0e5 MPa)。")
                code_snippets.append(f"youngs_modulus_mpa = {E_val * 1e-6:.1f}")
            # In Pa system, 2.0e5 is in MPa (10^6 times smaller!)
            elif (stress_unit in {"pa", "n/m2"} or length_unit in {"m", "meter"}) and 0.0 < E_val < self.MIN_PA_YOUNGS_MODULUS:
                violations.append(
                    f"楊氏彈性模量單位混淆毒化：模量數值為 {E_val:.2e}，在 Pa 單位制下縮小 10^6 倍 (誤填入 MPa 單位制)"
                )
                suggested_fixes.append("請將彈性模量乘以 1e6 換算為 Pa (例如鋼材 2.0e11 Pa)。")
                code_snippets.append(f"youngs_modulus_pa = {E_val * 1e6:.2e}")

        # 4. Check density unit poisoning
        if density_val is not None:
            rho_val = float(density_val)
            # In mm-tonne-s system, steel is 7.85e-9 tonne/mm^3. If 7850 is entered, it is 10^12 times larger!
            if (length_unit in {"mm", "millimeter"} or stress_unit in {"mpa", "n/mm2"}) and rho_val > self.MAX_TONNE_MM3_DENSITY:
                violations.append(
                    f"材料密度單位混淆毒化：密度數值為 {rho_val:.2f}，在 mm-tonne-s 體系下暴增 10^9~10^12 倍 (誤填入 kg/m^3)"
                )
                suggested_fixes.append("請將密度乘以 1e-12 換算為 tonne/mm^3 (例如鋼材 7.85e-9 tonne/mm^3)。")
                code_snippets.append(f"density_tonne_mm3 = {rho_val * 1e-12:.2e}")
            # In SI m-kg-s system, steel is 7850 kg/m^3. If 7.85e-9 is entered, it is 10^12 times smaller!
            elif (length_unit in {"m", "meter"} or stress_unit in {"pa", "n/m2"}) and 0.0 < rho_val < self.MIN_KG_M3_DENSITY:
                violations.append(
                    f"材料密度單位混淆毒化：密度數值為 {rho_val:.2e}，在 SI m-kg-s 體系下縮小 10^12 倍 (誤填入 tonne/mm^3)"
                )
                suggested_fixes.append("請將密度乘以 1e12 換算為 kg/m^3 (例如鋼材 7850 kg/m^3)。")
                code_snippets.append(f"density_kg_m3 = {rho_val * 1e12:.1f}")

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
                    action_code=ActionCodeEnum.CONVERT_TO_CONSISTENT_UNIT_SYSTEM.value,
                    suggested_fix="；".join(suggested_fixes) if suggested_fixes else "請校準物理量綱單位制。",
                    code_snippet="\n".join(code_snippets) if code_snippets else "# 校準量綱\npass",
                ),
            )

        return CheckResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            status=RuleStatusEnum.PASSED,
            severity=SeverityEnum.INFO,
            observed_value=observed,
            required_threshold=threshold,
            diagnosis="物理量綱與幾何/材料單位檢核合格，無單位毒化。",
        )

    def validate_context(
        self,
        context: Dict[str, Any],
        raise_on_poisoning: bool = True,
        session_id: Optional[str] = None,
    ) -> PreFlightPrescriptionReport:
        """主動核驗量綱與單位狀態。

        若核驗失敗且 raise_on_poisoning=True，主動拋出 UnitPoisoningError，
        並可依賴 session_id 同步將 DAMG 狀態機節點標記為 DIRTY / UNSATISFIED。
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
                    for node in [
                        "STRUCTURAL_CONTEXT_INITIALIZED",
                        "STRUCTURAL_GEOMETRY_READY",
                        "STRUCTURAL_MATERIALS_ASSIGNED",
                        "THERMAL_CONTEXT_INITIALIZED",
                        "FLUID_CONTEXT_INITIALIZED",
                    ]:
                        if node in sm.nodes:
                            sm.invalidate_node_and_downstream(node)
                except Exception:
                    pass

            if raise_on_poisoning:
                raise UnitPoisoningError(report)

        return report
