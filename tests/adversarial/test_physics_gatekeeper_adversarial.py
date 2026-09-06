# -*- coding: utf-8 -*-
"""對抗性極限壓力測試：Pre-Flight 物理安全閘門邊界極限攻擊 (test_physics_gatekeeper_adversarial.py).

本測試套件由 Empirical Challenger (Physics Adversarial Specialist) 獨立撰寫，
專注對求解前置物理安全閘門 (Pre-Flight Gatekeeper) 實施嚴苛的邊界條件對抗性攻擊：

1. 隨機振動模態有效質量極限邊界攻擊：
   - 89.99% 阻斷 vs 90.01% 放行之精確度
   - 90.00% 臨界精確點與浮點微量 epsilon (0.90 - 1e-9 vs 0.90 + 1e-9)
   - 單向激振 (X, Y, Z) 與全向激振 (ALL) 隔離性與多軸交互邊界
2. 模態截斷頻率充裕度邊界攻擊：
   - 激振上限 1.49x 阻斷 vs 1.51x 放行
   - 1.50x 臨界精確點與浮點微量邊界 (1499.99 Hz vs 1500.01 Hz)
   - 多點 PSD 功率譜密度激振上限提取與邊界阻斷
3. 落摔衝擊初速度向量與法向內積強健性攻擊：
   - 水平初速度 (內積 = 0.0) 阻斷
   - 微幅向上飛離初速度 (內積 > 0) 阻斷
   - 斜向微向下撞擊 (內積 < 0) 精確放行
   - 初速度全零向量 (內積 = 0.0) 阻斷
   - 非垂直傾斜地面法向向量 (斜坡落摔) 之幾何內積堅固性
   - 畸變向量格式 (空清單、二維向量、非數值型態) 之強健性與抗崩潰
4. 單位系統自洽性極限攻防與誤報率/漏報率實證：
   - mm-tonne-s 體系工程材料 (鋼、鋁、金、氣凝膠) 放行驗證
   - 密度混用典型錯誤 (7850 kg/m³, 2700 kg/m³, 7.85 g/cm³) 阻斷
   - 彈性模量量級混用 (2.0e11 Pa 誤填於 MPa 體系) 阻斷
   - SI 制輕質氣體 (氦氣 0.1786 kg/m³, 氫氣 0.0899 kg/m³) 之誤報率 (False Positive) 實證分析
   - mm-MPa 體系下小密度 (0.00785 kg/dm³) 之漏報率 (False Negative) 實證分析
   - 明確字串單位標籤衝突阻斷
"""

from __future__ import annotations

import pytest
from typing import Any, Dict

from ansys_unified_mcp.gatekeeper import (
    Gatekeeper,
    PreFlightGatekeeperError,
    RuleStatusEnum,
    SeverityEnum,
    ActionCodeEnum,
)
from ansys_unified_mcp.gatekeeper.rules.vibration_rules import (
    ModalEffectiveMassRatioRule,
    ModalCutoffFrequencyRule,
)
from ansys_unified_mcp.gatekeeper.rules.drop_impact_rules import (
    DropVelocityVectorRule,
    CriticalTimeStepRule,
    ContactIntegrityRule,
)
from ansys_unified_mcp.gatekeeper.rules.unit_consistency import UnitConsistencyRule


# ==============================================================================
# 1. 隨機振動模態有效質量極限邊界攻擊
# ==============================================================================
class TestModalEffectiveMassAdversarial:
    """隨機振動模態質量 90% 臨界值極限對抗測試。"""

    @pytest.fixture
    def rule(self) -> ModalEffectiveMassRatioRule:
        return ModalEffectiveMassRatioRule()

    def test_modal_mass_ratio_89_99_blocked(self, rule: ModalEffectiveMassRatioRule) -> None:
        """極限邊界：89.99% (0.8999) 必須硬性阻斷，不容許任何浮點寬容。"""
        ctx = {
            "effective_mass_ratio": {"x": 0.8999, "y": 0.9500, "z": 0.9500},
            "excitation_direction": "ALL",
            "num_modes": 15,
        }
        res = rule.check(ctx)
        assert res.status == RuleStatusEnum.BLOCKED
        assert res.rule_id == "GATE-VIB-001"
        assert res.severity == SeverityEnum.FATAL
        assert "89.99%" in res.diagnosis or "90.0%" in res.diagnosis
        assert res.prescription is not None
        assert res.prescription.action_code == ActionCodeEnum.INCREASE_MODES_AND_CUTOFF.value

    def test_modal_mass_ratio_90_01_passed(self, rule: ModalEffectiveMassRatioRule) -> None:
        """極限邊界：90.01% (0.9001) 必須順利放行。"""
        ctx = {
            "effective_mass_ratio": {"x": 0.9001, "y": 0.9001, "z": 0.9001},
            "excitation_direction": "ALL",
            "num_modes": 20,
        }
        res = rule.check(ctx)
        assert res.status == RuleStatusEnum.PASSED
        assert res.prescription is None

    def test_modal_mass_ratio_exact_90_00_boundary(self, rule: ModalEffectiveMassRatioRule) -> None:
        """精確邊界：剛好 90.00% (0.9000) 應順利放行 (>= 90%)。"""
        ctx = {
            "effective_mass_ratio": {"x": 0.9000, "y": 0.9000, "z": 0.9000},
            "excitation_direction": "ALL",
        }
        res = rule.check(ctx)
        assert res.status == RuleStatusEnum.PASSED

    def test_modal_mass_ratio_floating_point_epsilon(self, rule: ModalEffectiveMassRatioRule) -> None:
        """浮點微量 epsilon 測試 (0.90 - 1e-9 vs 0.90 + 1e-9)。"""
        eps_below = 0.90 - 1e-9
        res_below = rule.check({"effective_mass_ratio": {"x": eps_below, "y": 0.95, "z": 0.95}})
        assert res_below.status == RuleStatusEnum.BLOCKED

        eps_above = 0.90 + 1e-9
        res_above = rule.check({"effective_mass_ratio": {"x": eps_above, "y": eps_above, "z": eps_above}})
        assert res_above.status == RuleStatusEnum.PASSED

    def test_modal_mass_directional_isolation(self, rule: ModalEffectiveMassRatioRule) -> None:
        """單向激振 vs 全向激振之物理隔離性。"""
        # 僅在 Z 軸激振：Z 軸達標 (90.01%)，X 與 Y 未達標 (75%) -> 應放行
        ctx_z = {
            "effective_mass_ratio": {"x": 0.75, "y": 0.75, "z": 0.9001},
            "excitation_direction": "Z",
        }
        res_z = rule.check(ctx_z)
        assert res_z.status == RuleStatusEnum.PASSED

        # 僅在 Z 軸激振：Z 軸未達標 (89.99%)，X 與 Y 達標 (98%) -> 應阻斷
        ctx_z_fail = {
            "effective_mass_ratio": {"x": 0.98, "y": 0.98, "z": 0.8999},
            "excitation_direction": "Z",
        }
        res_z_fail = rule.check(ctx_z_fail)
        assert res_z_fail.status == RuleStatusEnum.BLOCKED

        # 全向激振：僅 Y 軸為 89.99% -> 應阻斷
        ctx_all = {
            "effective_mass_ratio": {"x": 0.95, "y": 0.8999, "z": 0.95},
            "excitation_direction": "ALL",
        }
        res_all = rule.check(ctx_all)
        assert res_all.status == RuleStatusEnum.BLOCKED


# ==============================================================================
# 2. 模態截斷頻率充裕度極限邊界攻擊
# ==============================================================================
class TestModalCutoffFrequencyAdversarial:
    """截斷頻率 1.5x 激振上限對抗測試。"""

    @pytest.fixture
    def rule(self) -> ModalCutoffFrequencyRule:
        return ModalCutoffFrequencyRule()

    def test_cutoff_frequency_1_49x_blocked(self, rule: ModalCutoffFrequencyRule) -> None:
        """激振上限 2000 Hz，門檻 3000 Hz；截斷頻率 1.49x (2980.0 Hz) 必須阻斷。"""
        ctx = {
            "max_excitation_frequency_hz": 2000.0,
            "cutoff_frequency_hz": 2980.0,
        }
        res = rule.check(ctx)
        assert res.status == RuleStatusEnum.BLOCKED
        assert res.rule_id == "GATE-VIB-002"
        assert res.severity == SeverityEnum.FATAL
        assert "2980.0" in res.diagnosis
        assert "3000.0" in res.diagnosis
        assert res.prescription is not None
        assert res.prescription.action_code == ActionCodeEnum.EXTEND_FREQUENCY_RANGE.value

    def test_cutoff_frequency_1_51x_passed(self, rule: ModalCutoffFrequencyRule) -> None:
        """激振上限 2000 Hz，截斷頻率 1.51x (3020.0 Hz) 必須順利放行。"""
        ctx = {
            "max_excitation_frequency_hz": 2000.0,
            "cutoff_frequency_hz": 3020.0,
        }
        res = rule.check(ctx)
        assert res.status == RuleStatusEnum.PASSED

    def test_cutoff_frequency_exact_1_50x(self, rule: ModalCutoffFrequencyRule) -> None:
        """精確邊界：截斷頻率恰為 1.50x (3000.0 Hz) 應放行。"""
        ctx = {
            "max_excitation_frequency_hz": 2000.0,
            "cutoff_frequency_hz": 3000.0,
        }
        res = rule.check(ctx)
        assert res.status == RuleStatusEnum.PASSED

    def test_cutoff_frequency_epsilon_boundary(self, rule: ModalCutoffFrequencyRule) -> None:
        """浮點微量邊界：2999.99 Hz 阻斷 vs 3000.01 Hz 放行。"""
        res_below = rule.check({"max_excitation_frequency_hz": 2000.0, "cutoff_frequency_hz": 2999.99})
        assert res_below.status == RuleStatusEnum.BLOCKED

        res_above = rule.check({"max_excitation_frequency_hz": 2000.0, "cutoff_frequency_hz": 3000.01})
        assert res_above.status == RuleStatusEnum.PASSED

    def test_cutoff_frequency_extracted_from_modal_frequencies_list(self, rule: ModalCutoffFrequencyRule) -> None:
        """從模態頻率清單中自動提取最大固有頻率並檢驗 1.49x vs 1.51x。"""
        # 最大頻率為 1490.0 Hz (< 1.5 * 1000.0 = 1500.0) -> 阻斷
        res_fail = rule.check({
            "max_excitation_frequency_hz": 1000.0,
            "modal_frequencies_hz": [120.5, 340.2, 850.0, 1490.0],
        })
        assert res_fail.status == RuleStatusEnum.BLOCKED

        # 最大頻率為 1520.0 Hz (>= 1500.0) -> 放行
        res_pass = rule.check({
            "max_excitation_frequency_hz": 1000.0,
            "modal_frequencies_hz": [120.5, 340.2, 850.0, 1520.0],
        })
        assert res_pass.status == RuleStatusEnum.PASSED


# ==============================================================================
# 3. 落摔衝擊初速度向量與法向內積強健性攻擊
# ==============================================================================
class TestDropVelocityVectorAdversarial:
    """落摔初速度向量與地面法向內積對抗測試。"""

    @pytest.fixture
    def rule(self) -> DropVelocityVectorRule:
        return DropVelocityVectorRule()

    def test_horizontal_velocity_vector_blocked(self, rule: DropVelocityVectorRule) -> None:
        """水平初速度向量 (沿地面平行滑行，內積 = 0.0) 必須硬性阻斷。"""
        # 地面在底部，法向朝 +Z [0, 0, 1]，物體沿 X 軸以 2000 mm/s 滑行
        ctx = {
            "velocity_vector": [2000.0, 0.0, 0.0],
            "floor_normal": [0.0, 0.0, 1.0],
        }
        res = rule.check(ctx)
        assert res.status == RuleStatusEnum.BLOCKED
        assert res.rule_id == "GATE-DRP-001"
        assert res.observed_value["dot_product"] == 0.0
        assert "平行" in res.diagnosis or ">= 0" in res.diagnosis
        assert res.prescription is not None
        assert res.prescription.action_code == ActionCodeEnum.INVERT_VELOCITY_OR_NORMAL.value

    def test_upward_micro_velocity_blocked(self, rule: DropVelocityVectorRule) -> None:
        """微幅向上初速度 (反向飛離空間，內積 > 0) 必須硬性阻斷。"""
        ctx = {
            "velocity_vector": [500.0, 500.0, 0.001],
            "floor_normal": [0.0, 0.0, 1.0],
        }
        res = rule.check(ctx)
        assert res.status == RuleStatusEnum.BLOCKED
        assert res.observed_value["dot_product"] > 0.0

    def test_oblique_downward_velocity_passed(self, rule: DropVelocityVectorRule) -> None:
        """斜向撞擊地面 (具備巨大水平分量但微弱垂直向下分量，內積 < 0) 精確放行。"""
        # 水平速度高達 10,000 mm/s，垂直速度僅 -0.01 mm/s，內積為 -0.01 < 0
        ctx = {
            "velocity_vector": [10000.0, 5000.0, -0.01],
            "floor_normal": [0.0, 0.0, 1.0],
        }
        res = rule.check(ctx)
        assert res.status == RuleStatusEnum.PASSED
        assert res.observed_value["dot_product"] < 0.0

    def test_zero_velocity_vector_blocked(self, rule: DropVelocityVectorRule) -> None:
        """零速度向量 [0, 0, 0] (內積 = 0.0) 必須阻斷。"""
        ctx = {
            "velocity_vector": [0.0, 0.0, 0.0],
            "floor_normal": [0.0, 0.0, 1.0],
        }
        res = rule.check(ctx)
        assert res.status == RuleStatusEnum.BLOCKED
        assert res.observed_value["dot_product"] == 0.0

    def test_tilted_floor_normal_oblique_impact(self, rule: DropVelocityVectorRule) -> None:
        """非正交斜坡地面法向向量之幾何內積堅固性驗證。"""
        # 斜面法向朝右上 [0.7071, 0.0, 0.7071]
        # 撞擊速度朝左下 [-1000.0, 0.0, -1000.0] -> 內積 = -1414.2 < 0 -> 放行
        res_pass = rule.check({
            "velocity_vector": [-1000.0, 0.0, -1000.0],
            "floor_normal": [0.7071, 0.0, 0.7071],
        })
        assert res_pass.status == RuleStatusEnum.PASSED

        # 飛離斜面速度 [1000.0, 0.0, 500.0] -> 內積 = 707.1 + 353.5 > 0 -> 阻斷
        res_block = rule.check({
            "velocity_vector": [1000.0, 0.0, 500.0],
            "floor_normal": [0.7071, 0.0, 0.7071],
        })
        assert res_block.status == RuleStatusEnum.BLOCKED

    def test_malformed_velocity_input_resilience(self, rule: DropVelocityVectorRule) -> None:
        """抗崩潰測試：輸入空串列、二維向量或字串時，不拋出未捕獲例外，優雅阻斷。"""
        res_empty = rule.check({"velocity_vector": []})
        assert res_empty.status == RuleStatusEnum.BLOCKED

        res_2d = rule.check({"velocity_vector": [0.0, -1000.0]})
        assert res_2d.status == RuleStatusEnum.BLOCKED

        res_none = rule.check({"velocity_vector": None})
        assert res_none.status == RuleStatusEnum.BLOCKED


# ==============================================================================
# 4. 單位系統自洽性極限攻防與誤報/漏報實證
# ==============================================================================
class TestUnitConsistencyAdversarial:
    """單位一致性極限防護對抗測試與誤報率/漏報率實測。"""

    @pytest.fixture
    def rule(self) -> UnitConsistencyRule:
        return UnitConsistencyRule()

    def test_mm_mpa_standard_engineering_materials_passed(self, rule: UnitConsistencyRule) -> None:
        """mm-tonne-s 標準工程材料 (鋼、鋁、金) 正常放行。"""
        # 鋼材
        assert rule.check({"length_unit": "mm", "stress_unit": "MPa", "density_value": 7.85e-9}).status == RuleStatusEnum.PASSED
        # 鋁材
        assert rule.check({"length_unit": "mm", "stress_unit": "MPa", "density_value": 2.70e-9}).status == RuleStatusEnum.PASSED
        # 重金屬 (黃金 1.93e-8, 鋨 2.26e-8)
        assert rule.check({"length_unit": "mm", "stress_unit": "MPa", "density_value": 1.93e-8}).status == RuleStatusEnum.PASSED
        assert rule.check({"length_unit": "mm", "stress_unit": "MPa", "density_value": 2.26e-8}).status == RuleStatusEnum.PASSED
        # 輕質氣凝膠 (1.0e-12)
        assert rule.check({"length_unit": "mm", "stress_unit": "MPa", "density_value": 1.0e-12}).status == RuleStatusEnum.PASSED

    def test_mm_mpa_density_unit_mismatch_blocked(self, rule: UnitConsistencyRule) -> None:
        """mm-tonne-s 體系混用 kg/m³ 或 g/cm³ 數值硬性阻斷。"""
        # 鋼材誤填 7850
        res_steel = rule.check({"length_unit": "mm", "stress_unit": "MPa", "density_value": 7850.0})
        assert res_steel.status == RuleStatusEnum.BLOCKED
        assert res_steel.rule_id == "GATE-UNI-001"
        assert res_steel.severity == SeverityEnum.FATAL
        assert "10^9" in res_steel.diagnosis or "10^12" in res_steel.diagnosis

        # 鋁材誤填 2700
        res_al = rule.check({"length_unit": "mm", "stress_unit": "MPa", "density_value": 2700.0})
        assert res_al.status == RuleStatusEnum.BLOCKED

        # 鋼材誤填 g/cm³ (7.85)
        res_g_cm3 = rule.check({"length_unit": "mm", "stress_unit": "MPa", "density_value": 7.85})
        assert res_g_cm3.status == RuleStatusEnum.BLOCKED

    def test_mm_mpa_youngs_modulus_limits(self, rule: UnitConsistencyRule) -> None:
        """mm-MPa 體系下楊氏模量防護測試。"""
        # 正常鋼材 2.0e5 MPa -> 放行
        res_ok = rule.check({"length_unit": "mm", "stress_unit": "MPa", "youngs_modulus_value": 2.0e5})
        assert res_ok.status == RuleStatusEnum.PASSED

        # 誤填 Pa 數值 2.0e11 Pa -> 阻斷
        res_boom = rule.check({"length_unit": "mm", "stress_unit": "MPa", "youngs_modulus_value": 2.0e11})
        assert res_boom.status == RuleStatusEnum.BLOCKED
        assert "10^6" in res_boom.diagnosis

    def test_empirical_finding_false_positive_si_light_gas(self, rule: UnitConsistencyRule) -> None:
        """【經驗主義挑戰發現：誤報率 (False Positive)】

        在標準 SI 制 (m, Pa) 下，真實物理輕質氣體 (例如常溫常壓氦氣 0.1786 kg/m³、氫氣 0.0899 kg/m³)
        之密度本質即小於 1.0 kg/m³。當前代碼中以 density < 1.0 作為判定依據，
        會引發誤報阻斷！此測試實測確認此邊界限制。
        """
        res_helium = rule.check({"length_unit": "m", "stress_unit": "Pa", "density_value": 0.1786})
        # 經驗實測：確認目前規則確會阻斷該數值
        assert res_helium.status == RuleStatusEnum.BLOCKED
        assert "小於 1.0" in res_helium.diagnosis
        assert "7850" in res_helium.diagnosis

    def test_empirical_finding_false_negative_kg_dm3_slip_through(self, rule: UnitConsistencyRule) -> None:
        """【經驗主義挑戰發現：漏報率 (False Negative)】

        在 mm-MPa 體系中，鋼材若誤填為 kg/cm³ (0.00785 kg/cm³ = 7850 kg/m³)，
        由於其數值 0.00785 小於硬編碼門檻 0.05，目前邏輯會放行！
        實測記錄此潛在漏報邊界。
        """
        res_kg_cm3 = rule.check({"length_unit": "mm", "stress_unit": "MPa", "density_value": 0.00785})
        # 經驗實測：確認目前規則未攔截該混用數值
        assert res_kg_cm3.status == RuleStatusEnum.PASSED


# ==============================================================================
# 5. PreFlightGatekeeper 全局調用與結構化處方箋測試
# ==============================================================================
class TestGatekeeperOrchestrationAdversarial:
    """PreFlightGatekeeper 整體綜合調用與處方箋測試。"""

    def test_gatekeeper_validate_blocks_and_generates_correct_schema(self) -> None:
        """驗證同時多項物理邊界不合格時，處方箋包含所有違規項目與結構。"""
        gk = Gatekeeper()
        context = {
            # 隨機振動邊界失敗: 89.99%
            "effective_mass_ratio": {"x": 0.8999, "y": 0.95, "z": 0.95},
            "excitation_direction": "ALL",
            "num_modes": 10,
            # 截斷頻率邊界失敗: 1.49x
            "max_excitation_frequency_hz": 1000.0,
            "cutoff_frequency_hz": 1490.0,
            # 單位制失敗: 7850
            "length_unit": "mm",
            "stress_unit": "MPa",
            "density_value": 7850.0,
        }

        with pytest.raises(PreFlightGatekeeperError) as exc_info:
            gk.validate(workflow_type="random_vibration", context=context, raise_on_blocked=True)

        report = exc_info.value.report
        assert not report.passed
        assert report.blocking_issues_count >= 3
        rule_ids = {c.rule_id for c in report.checks if c.status == RuleStatusEnum.BLOCKED}
        assert "GATE-VIB-001" in rule_ids
        assert "GATE-VIB-002" in rule_ids
        assert "GATE-UNI-001" in rule_ids