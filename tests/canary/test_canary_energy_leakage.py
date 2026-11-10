# Strictly ASCII English Comments
"""跨場耦合能量洩漏破壞性注入 Canary 測試套件 (test_canary_energy_leakage.py).

本模組為 Stage 5 Canary 破壞性容錯注入測試之二：
1. 共軛熱傳 (CHT) 固液交界面熱通量不守恆注入：故意注入 5.0% 偏差 (> 1.5% 門檻)，
   驗證 EnergyConservationGate 100% 拋出 EnergyLeakageError。
2. CHT 界面溫度連續性破壞注入：故意注入 2.0 K 溫度跳躍 (> 0.5 K 門檻)，
   驗證閘門 100% 阻斷並拒絕產出偽收斂報告。
3. 流固耦合 (FSI) 界面力/能量傳遞不平衡注入：故意注入 10.0% 作用力偏差，
   驗證 EnergyLeakageError 阻斷。
4. DAMG 因果狀態機聯動失效傳播：交界面能量洩漏時，狀態機自動將下游節點標記為 DIRTY，
   後續求解觸發 DAMG_PRECONDITION_VIOLATION。
5. 偽收斂報告阻斷：即使求解器收斂殘差達標，只要能量不守恆，嚴禁標註 PASS / COMPLETED。
"""

from __future__ import annotations

import pytest
from typing import Any, Dict

from ansys_unified_mcp.core.gatekeeper import (
    EnergyConservationGate,
    EnergyLeakageError,
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


class TestCanaryEnergyLeakage:
    """Canary 跨場耦合能量洩漏破壞性注入測試套件。"""

    @pytest.fixture
    def gate(self) -> EnergyConservationGate:
        """建立標準能量守恆檢查器實例。"""
        return EnergyConservationGate()

    def test_cht_heat_flux_leakage_injection_5pct_blocked(
        self, gate: EnergyConservationGate
    ) -> None:
        """破壞性注入 1: CHT 界面熱通量偏差 5.0% (> 1.5% 門檻) 注入。

        流體側熱通量 1000 W/m^2，固體側熱通量 950 W/m^2，偏差 5.0%。
        驗證 EnergyConservationGate 100% 阻斷並拋出 EnergyLeakageError。
        """
        poisoned_context = {
            "workflow_type": "cht",
            "q_fluid_wall": 1000.0,
            "q_solid_wall": 950.0,  # 5.0% flux discrepancy > 1.5%
            "t_fluid_interface": 350.0,
            "t_solid_interface": 350.1,  # 0.1 K jump <= 0.5 K (OK)
        }

        # 1. Inspect check result directly
        result = gate.check(poisoned_context)
        assert result.status == RuleStatusEnum.BLOCKED
        assert result.severity == SeverityEnum.FATAL
        assert result.rule_id == "GATE-ENG-001"
        assert "5.00%" in result.diagnosis
        assert "熱通量不守恆" in result.diagnosis

        # 2. validate_interface must raise EnergyLeakageError
        with pytest.raises(EnergyLeakageError) as exc_info:
            gate.validate_interface(poisoned_context, raise_on_leakage=True)

        err: EnergyLeakageError = exc_info.value
        assert not err.report.passed
        assert err.report.blocking_issues_count == 1
        assert "GATE-ENG-001" in str(err)

    def test_cht_temperature_jump_injection_2k_blocked(
        self, gate: EnergyConservationGate
    ) -> None:
        """破壞性注入 2: CHT 界面溫度跳躍 2.0 K (> 0.5 K 門檻) 注入。

        流體側溫度 352.0 K，固體側溫度 350.0 K，界面溫度不連續 2.0 K。
        驗證閘門 100% 阻斷並拋出 EnergyLeakageError。
        """
        poisoned_context = {
            "workflow_type": "cht",
            "q_fluid_wall": 1000.0,
            "q_solid_wall": 1005.0,  # 0.5% flux discrepancy <= 1.5% (OK)
            "t_fluid_interface": 352.0,
            "t_solid_interface": 350.0,  # 2.0 K jump > 0.5 K (VIOLATION)
        }

        result = gate.check(poisoned_context)
        assert result.status == RuleStatusEnum.BLOCKED
        assert result.severity == SeverityEnum.FATAL
        assert "2.000 K" in result.diagnosis
        assert "溫度連續性破壞" in result.diagnosis

        with pytest.raises(EnergyLeakageError) as exc_info:
            gate.validate_interface(poisoned_context, raise_on_leakage=True)

        assert "GATE-ENG-001" in str(exc_info.value)

    def test_fsi_interface_force_imbalance_injection_blocked(
        self, gate: EnergyConservationGate
    ) -> None:
        """破壞性注入 3: FSI 流固界面作用力不平衡 10.0% (> 1.5% 門檻) 注入。

        流體施加力 500 N，結構反作用力 450 N，偏差 10.0%。
        驗證閘門 100% 阻斷。
        """
        poisoned_context = {
            "workflow_type": "fsi",
            "f_fluid_interface": 500.0,
            "f_solid_interface": 450.0,  # 10.0% imbalance > 1.5%
        }

        result = gate.check(poisoned_context)
        assert result.status == RuleStatusEnum.BLOCKED
        assert "10.00%" in result.diagnosis
        assert "流固界面作用力不平衡" in result.diagnosis

        with pytest.raises(EnergyLeakageError):
            gate.validate_interface(poisoned_context, raise_on_leakage=True)

    def test_damg_state_machine_causal_invalidation_and_precondition_violation(
        self, gate: EnergyConservationGate
    ) -> None:
        """破壞性注入 4: 能量洩漏連動 DAMG 狀態機下游無效化與前置阻斷。

        當 CHT 能量洩漏時，狀態機將下游結果節點強制標記為 DIRTY / UNSATISFIED，
        後續工具若企圖在未重新核驗能量平衡下調用，立即觸發 DAMG_PRECONDITION_VIOLATION。
        """
        session_id = "canary_cht_energy_leak_sess"
        DAMGStateMachine.remove_instance(session_id)
        sm = DAMGStateMachine.get_instance(session_id)

        # Satisfy prerequisites up to thermal extraction
        sm.mark_node_satisfied("THERMAL_CONTEXT_INITIALIZED")
        sm.mark_node_satisfied("THERMAL_GEOMETRY_READY")
        sm.mark_node_satisfied("THERMAL_MATERIALS_ASSIGNED")
        sm.mark_node_satisfied("THERMAL_LOADS_BC_APPLIED")
        sm.mark_node_satisfied("THERMAL_MESH_GENERATED")
        sm.mark_node_satisfied("THERMAL_SOLVER_CONFIGURED")
        sm.mark_node_satisfied("THERMAL_SOLUTION_SOLVED")
        sm.mark_node_satisfied("TEMPERATURE_DISTRIBUTION_EXTRACTED")

        assert sm.get_node_status("TEMPERATURE_DISTRIBUTION_EXTRACTED") == NodeStatus.SATISFIED

        # Inject energy leakage and validate with session_id linkage
        poisoned_context = {
            "workflow_type": "cht",
            "q_fluid_wall": 500.0,
            "q_solid_wall": 400.0,  # 20% leakage
            "t_fluid_interface": 300.0,
            "t_solid_interface": 305.0,  # 5.0 K jump
        }

        # Must raise EnergyLeakageError and invalidate downstream node in DAMG
        with pytest.raises(EnergyLeakageError):
            gate.validate_interface(poisoned_context, raise_on_leakage=True, session_id=session_id)

        # Verify downstream node is no longer SATISFIED
        status = sm.get_node_status("TEMPERATURE_DISTRIBUTION_EXTRACTED")
        assert status in {NodeStatus.DIRTY, NodeStatus.UNSATISFIED}

        # Attempt to call a dummy tool decorated with enforce_damg_precondition
        @enforce_damg_precondition(
            required_nodes=["TEMPERATURE_DISTRIBUTION_EXTRACTED"],
            target_node="THERMAL_REPORT_GENERATED",
            session_id=session_id,
            state_machine=sm,
        )
        def generate_thermal_report_tool(session_id: str = session_id) -> Dict[str, Any]:
            return {"status": "SUCCESS", "report": "pseudo_converged_report"}

        # Execution must be intercepted at 0 seconds with DAMG_PRECONDITION_VIOLATION
        response = generate_thermal_report_tool(session_id=session_id)
        assert response["ok"] is False
        assert response["error_code"] == DAMG_ERROR_CODE_PRECONDITION_VIOLATION
        assert "TEMPERATURE_DISTRIBUTION_EXTRACTED" in response["error"]

    def test_pseudo_convergence_report_rejection(
        self, gate: EnergyConservationGate
    ) -> None:
        """破壞性注入 5: 拒絕產出偽收斂報告。

        模擬數值殘差看似收斂 (Residual < 1e-4)，但交界面熱平衡偏差 8.0%。
        驗證報告門禁嚴格阻斷，不容許標記 COMPLETED 或 PASS。
        """
        simulated_report = {
            "status": "COMPLETED",
            "verdict": "PASS",
            "residuals": {"continuity": 1e-5, "energy": 1e-5},
            "interface_data": {
                "q_fluid_wall": 2000.0,
                "q_solid_wall": 1840.0,  # 8.0% discrepancy
                "t_fluid_interface": 360.0,
                "t_solid_interface": 360.2,
            },
        }

        # Audit interface data via gate
        check_res = gate.check(simulated_report["interface_data"])
        assert check_res.status == RuleStatusEnum.BLOCKED

        # Enforce rejection: verdict cannot remain PASS
        if check_res.status == RuleStatusEnum.BLOCKED:
            simulated_report["verdict"] = "REJECTED_ENERGY_LEAKAGE"
            simulated_report["status"] = "FAILED"

        assert simulated_report["verdict"] != "PASS"
        assert simulated_report["status"] == "FAILED"

    def test_compliant_interface_energy_balance_clean_pass(
        self, gate: EnergyConservationGate
    ) -> None:
        """驗證合規交界面順利通過：熱通量偏差 0.4% (< 1.5%)，溫度跳躍 0.1 K (< 0.5 K)。"""
        compliant_context = {
            "workflow_type": "cht",
            "q_fluid_wall": 1000.0,
            "q_solid_wall": 1004.0,  # 0.4% discrepancy <= 1.5%
            "t_fluid_interface": 350.0,
            "t_solid_interface": 350.1,  # 0.1 K jump <= 0.5 K
        }

        res = gate.check(compliant_context)
        assert res.status == RuleStatusEnum.PASSED
        assert res.severity == SeverityEnum.INFO

        report = gate.validate_interface(compliant_context, raise_on_leakage=True)
        assert report.passed is True
        assert report.blocking_issues_count == 0


if __name__ == "__main__":
    pytest.main(["-v", __file__])
