# Strictly ASCII English Comments
"""物理量綱與單位混淆毒化 Canary 破壞性注入測試套件 (test_canary_unit_poisoning.py).

本模組為 Stage 5 Canary 破壞性容錯注入測試之三：
1. 幾何尺寸量綱混淆毒化：故意將長度單位由 mm 混淆為 m (特徵尺寸放大 1000 倍)，
   驗證 UnitContextGate 100% 拋出 UnitPoisoningError。
2. 材料楊氏彈性模量量綱混淆毒化：故意在 MPa 體系填入 Pa 數值 (2.0e11 虛增 10^6 倍剛度)，
   或在 Pa 體系填入 MPa 數值 (2.0e5 剛度縮小 10^6 倍引發奇異矩陣)，100% 阻斷。
3. 材料密度單位混淆毒化：在 mm-tonne-s 體系誤填 7850 kg/m^3 (質量虛增 10^12 倍引發慣性發散)，
   100% 阻斷。
4. 泊松比非物理熱力學邊界毒化：故意注入 nu >= 0.5 或 nu <= 0.0，100% 阻斷。
5. 連動 DAMG 狀態機預檢：幾何/材料預檢一旦遭受量綱毒化，狀態機下游節點全面標記為 DIRTY，
   後續求解工具調用 0 秒阻斷並回傳 DAMG_PRECONDITION_VIOLATION。
"""

from __future__ import annotations

import pytest
from typing import Any, Dict

from ansys_unified_mcp.core.gatekeeper import (
    UnitContextGate,
    UnitPoisoningError,
    PreFlightPrescriptionReport,
    RuleStatusEnum,
    SeverityEnum,
)
from ansys_unified_mcp.core.damg import (
    DAMGStateMachine,
    NodeStatus,
    enforce_damg_precondition,
    DAMG_ERROR_CODE_PRECONDITION_VIOLATION,
)


class TestCanaryUnitPoisoning:
    """Canary 物理量綱/單位混淆毒化破壞性注入測試套件。"""

    @pytest.fixture
    def gate(self) -> UnitContextGate:
        """建立標準單位上下文安全閘門實例。"""
        return UnitContextGate()

    def test_geometry_length_scale_poisoning_1000x_blocked(
        self, gate: UnitContextGate
    ) -> None:
        """破壞性注入 1: 幾何尺度 mm 與 m 混淆 (特徵尺寸放大 1000 倍) 毒化注入。

        在 electronics / chassis 工況下，模型外殼標稱 500 mm，
        但單位誤設為 m (特徵長度 500.0 m，相當於五百公尺的航母級機箱)。
        驗證 UnitContextGate 100% 阻斷並拋出 UnitPoisoningError。
        """
        poisoned_context = {
            "length_unit": "m",
            "stress_unit": "pa",
            "characteristic_length": 500.0,  # 500 meters!
            "expected_domain": "electronics",
        }

        result = gate.check(poisoned_context)
        assert result.status == RuleStatusEnum.BLOCKED
        assert result.severity == SeverityEnum.FATAL
        assert result.rule_id == "GATE-UNI-002"
        assert "放大 1000 倍" in result.diagnosis

        with pytest.raises(UnitPoisoningError) as exc_info:
            gate.validate_context(poisoned_context, raise_on_poisoning=True)

        err: UnitPoisoningError = exc_info.value
        assert not err.report.passed
        assert "GATE-UNI-002" in str(err)

    def test_youngs_modulus_poisoning_pa_in_mpa_system_10e6x_blocked(
        self, gate: UnitContextGate
    ) -> None:
        """破壞性注入 2: 楊氏彈性模量誤填 Pa 數值 (2.0e11 在 MPa 體系下虛增 10^6 倍剛度)。

        鋼材在 MPa 體系標準值為 200,000 MPa (2.0e5)。
        若填入 2.0e11，結構剛度矩陣剛度暴增 10^6 倍，位移縮小 10^6 倍失去物理真實度。
        驗證閘門 100% 阻斷並拋出 UnitPoisoningError。
        """
        poisoned_context = {
            "length_unit": "mm",
            "stress_unit": "mpa",
            "youngs_modulus_value": 2.0e11,  # Pa input in MPa system!
            "poissons_ratio_value": 0.3,
        }

        result = gate.check(poisoned_context)
        assert result.status == RuleStatusEnum.BLOCKED
        assert result.severity == SeverityEnum.FATAL
        assert "10^6 倍" in result.diagnosis
        assert "Pa 單位制" in result.diagnosis

        with pytest.raises(UnitPoisoningError):
            gate.validate_context(poisoned_context, raise_on_poisoning=True)

    def test_youngs_modulus_poisoning_mpa_in_pa_system_underflow_blocked(
        self, gate: UnitContextGate
    ) -> None:
        """破壞性注入 3: 楊氏彈性模量誤填 MPa 數值於 SI Pa 體系 (剛度縮小 10^6 倍)。

        在標準 SI (m, Pa) 體系下填入 2.0e5 (過小，如同液體或極度軟質凝膠)。
        驗證閘門 100% 阻斷。
        """
        poisoned_context = {
            "length_unit": "m",
            "stress_unit": "pa",
            "youngs_modulus_value": 2.0e5,  # MPa input in Pa system!
            "poissons_ratio_value": 0.3,
        }

        result = gate.check(poisoned_context)
        assert result.status == RuleStatusEnum.BLOCKED
        assert "縮小 10^6 倍" in result.diagnosis

        with pytest.raises(UnitPoisoningError):
            gate.validate_context(poisoned_context, raise_on_poisoning=True)

    def test_density_poisoning_kg_m3_in_tonne_mm3_system_10e12x_blocked(
        self, gate: UnitContextGate
    ) -> None:
        """破壞性注入 4: 材料密度在 mm-tonne-s 體系誤填 7850 (虛增 10^12 倍質量)。

        在 mm-tonne-s 體系中鋼材應為 7.85e-9 tonne/mm^3。
        若誤填 7850 kg/m^3，等效質量暴增 10^12 倍，動力學求解時間步 CFL 縮小 10^6 倍直接發散。
        驗證閘門 100% 阻斷。
        """
        poisoned_context = {
            "length_unit": "mm",
            "stress_unit": "mpa",
            "density_value": 7850.0,  # kg/m^3 in tonne/mm^3 system!
        }

        result = gate.check(poisoned_context)
        assert result.status == RuleStatusEnum.BLOCKED
        assert "10^9~10^12 倍" in result.diagnosis

        with pytest.raises(UnitPoisoningError):
            gate.validate_context(poisoned_context, raise_on_poisoning=True)

    def test_poisson_ratio_thermodynamic_bounds_violation_blocked(
        self, gate: UnitContextGate
    ) -> None:
        """破壞性注入 5: 泊松比非物理熱力學邊界毒化注入 (nu >= 0.5 或 nu <= 0.0)。

        泊松比 nu >= 0.5 違背連續介質力學上界，剪切模量 G = E / (2*(1+nu)) 失去正定性。
        驗證閘門 100% 阻斷。
        """
        # Test upper bound violation: nu = 0.55
        res_upper = gate.check({"poissons_ratio_value": 0.55})
        assert res_upper.status == RuleStatusEnum.BLOCKED
        assert "正定邊界" in res_upper.diagnosis

        # Test lower bound violation: nu = -0.05
        res_lower = gate.check({"poissons_ratio_value": -0.05})
        assert res_lower.status == RuleStatusEnum.BLOCKED
        assert "正定邊界" in res_lower.diagnosis

        with pytest.raises(UnitPoisoningError):
            gate.validate_context({"poissons_ratio_value": 0.52}, raise_on_poisoning=True)

    def test_damg_state_machine_unit_context_invalidation_and_precondition_rejection(
        self, gate: UnitContextGate
    ) -> None:
        """破壞性注入 6: 單位毒化連動 DAMG 狀態機預檢與 0 秒攔截。

        在幾何與材料預檢階段注入單位混淆毒化，狀態機將幾何與材料節點全面無效化，
        後續結構網格與求解步驟因前置條件缺失被 100% 拒絕。
        """
        session_id = "canary_unit_poison_sess"
        DAMGStateMachine.remove_instance(session_id)
        sm = DAMGStateMachine.get_instance(session_id)

        # Satisfy structural context, geometry and materials initially
        sm.mark_node_satisfied("STRUCTURAL_CONTEXT_INITIALIZED")
        sm.mark_node_satisfied("STRUCTURAL_GEOMETRY_READY")
        sm.mark_node_satisfied("STRUCTURAL_MATERIALS_ASSIGNED")

        assert sm.get_node_status("STRUCTURAL_MATERIALS_ASSIGNED") == NodeStatus.SATISFIED

        # Inject unit poisoning in materials stage
        poisoned_context = {
            "length_unit": "mm",
            "stress_unit": "mpa",
            "youngs_modulus_value": 2.1e11,  # 10^6x poisoning
            "density_value": 7800.0,          # 10^12x poisoning
        }

        # Validate with session_id linkage
        with pytest.raises(UnitPoisoningError):
            gate.validate_context(poisoned_context, raise_on_poisoning=True, session_id=session_id)

        # Verify materials and geometry nodes are invalidated
        mat_status = sm.get_node_status("STRUCTURAL_MATERIALS_ASSIGNED")
        assert mat_status in {NodeStatus.DIRTY, NodeStatus.UNSATISFIED}

        # Attempt to call a dummy solve tool requiring STRUCTURAL_MATERIALS_ASSIGNED
        @enforce_damg_precondition(
            required_nodes=["STRUCTURAL_MATERIALS_ASSIGNED"],
            target_node="STRUCTURAL_SOLUTION_SOLVED",
            session_id=session_id,
            state_machine=sm,
        )
        def run_structural_solver_tool(session_id: str = session_id) -> Dict[str, Any]:
            return {"status": "SUCCESS", "message": "Solved with poisoned units"}

        response = run_structural_solver_tool(session_id=session_id)
        assert response["ok"] is False
        assert response["error_code"] == DAMG_ERROR_CODE_PRECONDITION_VIOLATION
        assert "STRUCTURAL_MATERIALS_ASSIGNED" in response["error"]

    def test_compliant_units_context_clean_pass(
        self, gate: UnitContextGate
    ) -> None:
        """驗證兩大標準自洽單位體系順利放行：mm-tonne-s-MPa 與 m-kg-s-Pa。"""
        # 1. mm-tonne-s-MPa standard engineering system
        ctx_mm = {
            "length_unit": "mm",
            "stress_unit": "mpa",
            "youngs_modulus_value": 2.0e5,  # 200,000 MPa (Steel)
            "density_value": 7.85e-9,        # 7.85e-9 tonne/mm^3
            "poissons_ratio_value": 0.3,
            "characteristic_length": 300.0,
        }
        res_mm = gate.check(ctx_mm)
        assert res_mm.status == RuleStatusEnum.PASSED
        report_mm = gate.validate_context(ctx_mm, raise_on_poisoning=True)
        assert report_mm.passed is True

        # 2. m-kg-s-Pa standard SI system
        ctx_si = {
            "length_unit": "m",
            "stress_unit": "pa",
            "youngs_modulus_value": 2.0e11,  # 2.0e11 Pa (Steel)
            "density_value": 7850.0,         # 7850 kg/m^3
            "poissons_ratio_value": 0.3,
            "characteristic_length": 0.3,
        }
        res_si = gate.check(ctx_si)
        assert res_si.status == RuleStatusEnum.PASSED
        report_si = gate.validate_context(ctx_si, raise_on_poisoning=True)
        assert report_si.passed is True


if __name__ == "__main__":
    pytest.main(["-v", __file__])
