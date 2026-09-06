"""ANSYS Unified MCP 2.0 - 落摔衝擊前置物理安全閘門 (Drop Impact Rules).

包含：
- GATE-DRP-001: 初速度向量方向性檢核 (指向剛性地面 v . n < 0)
- GATE-DRP-002: CFL 臨界時間步長與質量縮放檢核 (dt >= 1e-7 或啟用合理負值 dt2ms)
- GATE-DRP-003: 剛體/面面接觸定義完整性檢核 (具備剛性地面或接觸對)
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Set

from ansys_unified_mcp.gatekeeper.prescription import (
    ActionCodeEnum,
    CheckResult,
    PrescriptionDetail,
    RuleStatusEnum,
    SeverityEnum,
)
from ansys_unified_mcp.gatekeeper.rules import BaseGateRule


class DropVelocityVectorRule(BaseGateRule):
    """GATE-DRP-001: 落摔初速度向量方向性檢核規則。

    初速度向量與地面法向之內積必須嚴格為負值 (v . n < 0)，
    確保物體朝向剛性地面撞擊，防止方向相反導致物體反向飛離空間。
    """

    rule_id = "GATE-DRP-001"
    rule_name = "Drop Impact Velocity Direction Guard"
    severity = SeverityEnum.FATAL
    target_workflows: Set[str] = {"drop_test", "shock_analysis", "explicit_dynamics"}

    def check(self, context: Dict[str, Any]) -> CheckResult:
        # 獲取初速度向量
        velocity = context.get("velocity_vector") or context.get("initial_velocity")
        floor_normal = context.get("floor_normal", [0.0, 0.0, 1.0])

        # 若僅提供標量速度與方向
        if velocity is None:
            speed_val = context.get("impact_velocity_mps") or context.get("impact_velocity_mms")
            direction_vec = context.get("gravity_direction", [0.0, 0.0, -1.0])
            if speed_val is not None:
                velocity = [float(speed_val) * float(d) for d in direction_vec]

        observed: Dict[str, Any] = {
            "velocity_vector": velocity,
            "floor_normal": floor_normal,
        }

        if velocity is None or not isinstance(velocity, (list, tuple)) or len(velocity) < 3:
            return CheckResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                status=RuleStatusEnum.BLOCKED,
                severity=self.severity,
                observed_value=observed,
                required_threshold={"dot_product": "< 0.0"},
                diagnosis="未提供有效之初速度向量 (velocity_vector) 或衝擊速度參數。",
                prescription=PrescriptionDetail(
                    action_code=ActionCodeEnum.INVERT_VELOCITY_OR_NORMAL.value,
                    suggested_fix="請明確指定待測物體之初速度向量 [vx, vy, vz]，數值須朝向剛性地面。",
                    code_snippet=(
                        "*INITIAL_VELOCITY_GENERATION\n"
                        "$#    ID     STYPE      VX      VY      VZ\n"
                        "       1         0     0.0     0.0 -4429.0"
                    ),
                ),
            )

        # 計算內積: v . n
        dot_product = sum(float(v) * float(n) for v, n in zip(velocity[:3], floor_normal[:3]))
        observed["dot_product"] = dot_product

        # 若內積 >= 0，速度方向背離地面或平行於地面
        if dot_product >= 0.0:
            return CheckResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                status=RuleStatusEnum.BLOCKED,
                severity=self.severity,
                observed_value=observed,
                required_threshold={"dot_product": "< 0.0"},
                diagnosis=(
                    f"初速度向量 {velocity} 與地面法向量 {floor_normal} 內積為 {dot_product:.2f} (>= 0)。"
                    "物體運動方向正遠離剛性地面或與地面平行，無法觸發實體碰撞！"
                ),
                prescription=PrescriptionDetail(
                    action_code=ActionCodeEnum.INVERT_VELOCITY_OR_NORMAL.value,
                    suggested_fix=(
                        "請反轉速度向量或將衝擊方向設定為指向地面 "
                        f"(例如若地面在下方，速度 Z 軸應由 {velocity[2]} 調整為 {-abs(float(velocity[2]))})。"
                    ),
                    code_snippet=(
                        "# 修正為朝向地面之衝擊速度\n"
                        f"correct_velocity = [{velocity[0]}, {velocity[1]}, {-abs(float(velocity[2])) if velocity[2] != 0 else -1000.0}]\n"
                        "*INITIAL_VELOCITY_GENERATION\n"
                        f"       1         0   {velocity[0]}   {velocity[1]}  {-abs(float(velocity[2])) if velocity[2] != 0 else -1000.0}"
                    ),
                ),
            )

        return CheckResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            status=RuleStatusEnum.PASSED,
            severity=SeverityEnum.INFO,
            observed_value=observed,
            required_threshold={"dot_product": "< 0.0"},
            diagnosis="初速度向量指向剛性地面，滿足碰撞動力學幾何條件。",
            prescription=None,
        )


class CriticalTimeStepRule(BaseGateRule):
    """GATE-DRP-002: 顯式動力學 CFL 臨界時間步長與質量縮放檢核規則。

    依據 CFL 穩定性判據: dt_crit = L_min / c (其中 c = sqrt(E / rho))。
    若估算之臨界時間步長 < 1.0e-7 秒且未啟用質量縮放 (*CONTROL_TIMESTEP DT2MS=0)，
    求解過程將因步長極小產生數以億計的時間步，導致計算時間失控。
    """

    rule_id = "GATE-DRP-002"
    rule_name = "Critical Timestep & Mass Scaling Guard"
    severity = SeverityEnum.FATAL
    target_workflows: Set[str] = {"drop_test", "explicit_dynamics"}

    CRITICAL_DT_THRESHOLD: float = 1.0e-7  # 秒

    def check(self, context: Dict[str, Any]) -> CheckResult:
        dt2ms = context.get("mass_scaling_dt2ms", context.get("dt2ms", 0.0))
        estimated_dt = context.get("estimated_dt_s")

        min_elem_size = context.get("min_element_size_mm")
        youngs_modulus_mpa = context.get("youngs_modulus_mpa")
        density_tonne_mm3 = context.get("density_tonne_mm3")

        # 若未直接傳入 estimated_dt_s，嘗試由網格與材料計算聲速估算
        if estimated_dt is None and min_elem_size and youngs_modulus_mpa and density_tonne_mm3:
            try:
                # E: MPa = N/mm^2, rho: tonne/mm^3 => c = sqrt(E/rho) mm/s
                e_val = float(youngs_modulus_mpa)
                rho_val = float(density_tonne_mm3)
                if e_val > 0 and rho_val > 0:
                    wave_speed_mm_per_s = math.sqrt(e_val / rho_val)
                    estimated_dt = (float(min_elem_size) / wave_speed_mm_per_s) * 0.9  # CFL 安全因子 0.9
            except Exception:
                pass

        observed: Dict[str, Any] = {
            "estimated_dt_s": estimated_dt,
            "dt2ms": dt2ms,
            "min_element_size_mm": min_elem_size,
        }
        threshold: Dict[str, Any] = {
            "min_dt_without_mass_scaling": self.CRITICAL_DT_THRESHOLD,
            "mass_scaling_recommended_dt2ms": -1.0e-7,
        }

        # 檢驗質量縮放
        # 在 LS-DYNA 中，DT2MS < 0 代表按時間步長進行質量縮放 (傳統常規做法)
        has_mass_scaling = dt2ms is not None and float(dt2ms) < 0.0

        if estimated_dt is not None and float(estimated_dt) < self.CRITICAL_DT_THRESHOLD:
            if not has_mass_scaling:
                return CheckResult(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    status=RuleStatusEnum.BLOCKED,
                    severity=self.severity,
                    observed_value=observed,
                    required_threshold=threshold,
                    diagnosis=(
                        f"CFL 臨界時間步長估算為 {float(estimated_dt):.2e} s "
                        f"(低於 {self.CRITICAL_DT_THRESHOLD:.1e} s 門檻)，且未啟用常規質量縮放 (dt2ms={dt2ms})。"
                        "顯式求解將因微小步長陷入嚴重算力耗盡 (可能需要數十小時或幾天)！"
                    ),
                    prescription=PrescriptionDetail(
                        action_code=ActionCodeEnum.CONFIGURE_MASS_SCALING.value,
                        suggested_fix=(
                            "請在 *CONTROL_TIMESTEP 卡片中設定合理的負值 DT2MS "
                            "(例如 -1.0E-07)，並透過 Watchdog 監控增加質量百分比不超過 5%。"
                        ),
                        code_snippet=(
                            "*CONTROL_TIMESTEP\n"
                            "$$  DTINIT    TSSFAC      ISDO    TSLIMT     DT2MS      LCTM     ERASE   EVERSN\n"
                            "       0.0       0.9         0       0.0 -1.000E-07         0         0        0"
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
            diagnosis="時間步長在安全範圍內或已適當配置質量縮放，顯式動力學求解穩定性合格。",
            prescription=None,
        )


class ContactIntegrityRule(BaseGateRule):
    """GATE-DRP-003: 落摔衝擊接觸與剛體地面完整性檢核規則。

    模型中必須定義至少一組剛性地面 (*RIGIDWALL_PLANAR) 或接觸對 (*CONTACT)，
    防止求解時物體直接穿透地面引發發散崩潰。
    """

    rule_id = "GATE-DRP-003"
    rule_name = "Rigid Wall and Contact Integrity Guard"
    severity = SeverityEnum.FATAL
    target_workflows: Set[str] = {"drop_test", "explicit_dynamics"}

    def check(self, context: Dict[str, Any]) -> CheckResult:
        has_rigid_wall = context.get("has_rigid_wall", False)
        floor_type = context.get("floor_type")
        if floor_type in {"rigid_wall", "rigid_floor", "elastic_floor"}:
            has_rigid_wall = True

        has_contact_pairs = context.get("has_contact_pairs", False)
        contact_cards = context.get("contact_cards")
        if contact_cards and len(contact_cards) > 0:
            has_contact_pairs = True

        observed: Dict[str, Any] = {
            "has_rigid_wall": bool(has_rigid_wall),
            "has_contact_pairs": bool(has_contact_pairs),
            "floor_type": floor_type,
        }
        threshold: Dict[str, Any] = {
            "require_at_least_one_contact_or_wall": True,
        }

        if not has_rigid_wall and not has_contact_pairs:
            return CheckResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                status=RuleStatusEnum.BLOCKED,
                severity=self.severity,
                observed_value=observed,
                required_threshold=threshold,
                diagnosis=(
                    "模型中未定義任何剛性地面 (*RIGIDWALL) 或接觸卡片 (*CONTACT)。"
                    "落摔碰撞時物體將無阻擋穿透空間，引發數值發散並浪費算力！"
                ),
                prescription=PrescriptionDetail(
                    action_code=ActionCodeEnum.DEFINE_RIGIDWALL_OR_CONTACT.value,
                    suggested_fix="請建立平面剛性地面 (*RIGIDWALL_PLANAR) 或配置自動表面接觸卡片。",
                    code_snippet=(
                        "*RIGIDWALL_PLANAR\n"
                        "$#    HEAD\n"
                        "         0         0\n"
                        "$#      XT        YT        ZT        XH        YH        ZH      FRIC\n"
                        "       0.0       0.0       0.0       0.0       0.0       1.0       0.2\n"
                        "*CONTACT_AUTOMATIC_SINGLE_SURFACE\n"
                        "         0         0         0         0         0         0         0         0"
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
            diagnosis="已檢測到剛性地面或接觸對定義，落摔接觸完整性合格。",
            prescription=None,
        )
