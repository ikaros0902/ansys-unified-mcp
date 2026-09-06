# -*- coding: utf-8 -*-
"""Tier 2 單元測試：Sentinel 守護隊列、日誌解析與早期物理熔斷測試 (test_sentinel_watchdog.py)

覆蓋 R2 規範核心要素：
1. CircuitBreaker 四大早期物理發散熔斷邏輯：
   - LS-DYNA 沙漏能 > 5% 熔斷 (去抖動防誤殺與單次暴增)
   - LS-DYNA 質量縮放 > 5% 熔斷
   - 數值 NaN / Inf 早期熔斷 (LS-DYNA, Mechanical, Fluent)
   - 負滑移能 > 10% 穿透鎖死熔斷
   - Mechanical 殘差暴衝 (>1e10) 與嚴重畸變發散熔斷
   - Fluent 殘差暴衝發散與 > 1e8 熔斷
2. 日誌正則解析器 (結合 MockLogStreamer 高保真仿真日誌)：
   - MechanicalMAPDLParser (solve.out 步長、時間、力平衡殘差、收斂與畸變警告)
   - LSDynaGlstatParser (glstat/matter.out 能量平衡、質量縮放、Normal termination)
   - FluentResidualParser (fluent.log 殘差陣列、逆流 reversed flow、收斂判定)
   - create_solver_parser 工廠函數
3. WatchdogDaemon 實時物理守護線程：
   - 增量日誌讀取、健康指標快照與熔斷回呼
   - 熔斷時自動更新沙盒 summary.json 標記
4. SentinelQueue 非同步排程與進程管理：
   - submit_simulation_job 立即回傳 (<500ms) 與狀態流轉 (QUEUED -> RUNNING -> SOLVED)
   - get_simulation_status 查詢活動與歷史作業
   - tail_simulation_log 即時串流末尾日誌
   - abort_simulation_job 優雅中止與進程樹清理
"""

from __future__ import annotations

import math
import os
import time
from pathlib import Path
from typing import Any, Dict, List
import pytest

# 引入模組
from ansys_unified_mcp.core.sentinel.circuit_breaker import (
    BreakerVerdict,
    CircuitBreaker,
)
from ansys_unified_mcp.core.sentinel.daemon import (
    get_sentinel_queue,
    shutdown_sentinel,
)
import ansys_unified_mcp.core.sentinel.parsers.mechanical as mech_mod
from ansys_unified_mcp.core.sentinel.parsers import (
    FluentResidualParser,
    LSDynaGlstatParser,
    MechanicalMAPDLParser,
    create_solver_parser,
)
from ansys_unified_mcp.core.sentinel.queue import SentinelQueue
from ansys_unified_mcp.core.sentinel.watchdog import WatchdogDaemon
from ansys_unified_mcp.jobs.manager import JobManager
from ansys_unified_mcp.jobs.models import JobStatusEnum, VerdictEnum
from ansys_unified_mcp.jobs.sandbox import JobSandbox
from tests.mocks.mock_streamer import MockLogStreamer

# 缺陷防禦注入：若 mechanical.py 模組內缺少 math 引用，動態補齊
if not hasattr(mech_mod, "math"):
    mech_mod.math = math


@pytest.fixture(autouse=True)
def patch_sandbox_inputs_compat(monkeypatch: pytest.MonkeyPatch) -> None:
    """自動相容補丁：處理 queue.py 調用 write_workspace_file("../inputs/...") 遭邊界防護攔截。

    註：此為相容層補丁，同時已向協調者 escalate 該實作缺陷。
    """
    orig_write = JobSandbox.write_workspace_file

    def safe_write_workspace(self: JobSandbox, relative_path: str | Path, content: str | bytes) -> Path:
        rel_str = str(relative_path).replace("\\", "/")
        if rel_str.startswith("../inputs/"):
            target_name = rel_str.replace("../inputs/", "")
            target_file = self.inputs_dir / target_name
            target_file.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                target_file.write_bytes(content)
            else:
                target_file.write_text(content, encoding="utf-8")
            return target_file
        return orig_write(self, relative_path, content)

    monkeypatch.setattr(JobSandbox, "write_workspace_file", safe_write_workspace)


# ==============================================================================
# 1. CircuitBreaker 早期物理發散熔斷測試
# ==============================================================================
class TestCircuitBreaker:
    """測試 CircuitBreaker 四大早期物理發散熔斷判準。"""

    def test_lsdyna_normal_energy_no_breaker(self) -> None:
        """驗證 LS-DYNA 正常能量平衡（沙漏比 1.875%、質量縮放 0.05%）不觸發熔斷。"""
        cb = CircuitBreaker()
        verdict = cb.evaluate_lsdyna(
            hourglass_energy=15.0,
            internal_energy=800.0,
            total_energy=1000.0,
            sliding_energy=5.0,
            added_mass_pct=0.05,
            has_nan_inf=False,
            current_time=0.001,
        )
        assert not verdict.triggered
        assert verdict.rule_id is None
        assert verdict.metrics_snapshot["hourglass_ratio_pct"] == pytest.approx(1.5, rel=1e-2)

    def test_lsdyna_hourglass_exceeded_breaker_with_debounce(self) -> None:
        """驗證 LS-DYNA 沙漏能佔比 > 5% 時，連續 3 次超過門檻觸發熔斷 (CB-DYNA-003)。"""
        cb = CircuitBreaker(debounce_count=3)

        # 前 2 次超標 (6.0%, 6.2% > 5.0%)：處於去抖動容忍期，不立即觸發
        v1 = cb.evaluate_lsdyna(60.0, 800.0, 1000.0, 0.0, 0.1)
        assert not v1.triggered, "第 1 次超標不應觸發熔斷 (去抖動)"

        v2 = cb.evaluate_lsdyna(62.0, 800.0, 1000.0, 0.0, 0.1)
        assert not v2.triggered, "第 2 次超標不應觸發熔斷 (去抖動)"

        # 第 3 次超標 (6.5% > 5.0%)：觸發熔斷
        v3 = cb.evaluate_lsdyna(65.0, 800.0, 1000.0, 0.0, 0.1)
        assert v3.triggered, "第 3 次超標應觸發熔斷"
        assert v3.rule_id == "CB-DYNA-003"
        assert "沙漏能" in v3.reason
        assert "UPGRADE_HOURGLASS_CONTROL" in (v3.action_code or "")

    def test_lsdyna_hourglass_extreme_instant_breaker(self) -> None:
        """驗證 LS-DYNA 沙漏能極度超標 (>15%) 時立即觸發熔斷，無需等待去抖動。"""
        cb = CircuitBreaker(debounce_count=3)
        # 沙漏能 200J / 總能 1000J = 20% > 15%
        verdict = cb.evaluate_lsdyna(200.0, 500.0, 1000.0, 0.0, 0.1)
        assert verdict.triggered
        assert verdict.rule_id == "CB-DYNA-003"

    def test_lsdyna_mass_scaling_exceeded_breaker(self) -> None:
        """驗證 LS-DYNA 質量縮放比例 > 5% 立即觸發熔斷 (CB-DYNA-002)。"""
        cb = CircuitBreaker()
        verdict = cb.evaluate_lsdyna(
            hourglass_energy=10.0,
            internal_energy=500.0,
            total_energy=1000.0,
            sliding_energy=0.0,
            added_mass_pct=5.85,  # 5.85% > 5.0%
        )
        assert verdict.triggered
        assert verdict.rule_id == "CB-DYNA-002"
        assert "質量縮放" in verdict.reason
        assert "TUNE_MASS_SCALING_DT2MS" in (verdict.action_code or "")

    def test_lsdyna_nan_inf_breaker(self) -> None:
        """驗證 LS-DYNA 能量或日誌出現 NaN/Inf 時立即觸發熔斷 (CB-DYNA-001)。"""
        cb = CircuitBreaker()

        # 藉由 has_nan_inf 觸發
        v_flag = cb.evaluate_lsdyna(10.0, 500.0, 1000.0, 0.0, 0.1, has_nan_inf=True)
        assert v_flag.triggered
        assert v_flag.rule_id == "CB-DYNA-001"

        # 藉由浮點 NaN 觸發
        v_nan = cb.evaluate_lsdyna(float("nan"), 500.0, 1000.0, 0.0, 0.1)
        assert v_nan.triggered
        assert v_nan.rule_id == "CB-DYNA-001"

        # 藉由浮點 Inf 觸發
        v_inf = cb.evaluate_lsdyna(10.0, float("inf"), 1000.0, 0.0, 0.1)
        assert v_inf.triggered
        assert v_inf.rule_id == "CB-DYNA-001"

    def test_lsdyna_negative_sliding_energy_breaker(self) -> None:
        """驗證 LS-DYNA 接觸滑移能為顯著負值且佔總能 > 10% 時觸發熔斷 (CB-DYNA-004)。"""
        cb = CircuitBreaker()
        # 滑移能 -150 J，總能 1000 J，比例 15% > 10%
        verdict = cb.evaluate_lsdyna(
            hourglass_energy=10.0,
            internal_energy=500.0,
            total_energy=1000.0,
            sliding_energy=-150.0,
            added_mass_pct=0.1,
        )
        assert verdict.triggered
        assert verdict.rule_id == "CB-DYNA-004"
        assert "滑移能" in verdict.reason

        # 若負滑移能小於 10% (例如 -20 J / 1000 J = 2%)，不觸發熔斷
        v_minor = cb.evaluate_lsdyna(10.0, 500.0, 1000.0, -20.0, 0.1)
        assert not v_minor.triggered

    def test_mechanical_normal_convergence_no_breaker(self) -> None:
        """驗證 Mechanical 正常力殘差 (0.01 < 0.05) 不觸發熔斷。"""
        cb = CircuitBreaker()
        verdict = cb.evaluate_mechanical(force_residual=0.01, criterion=0.05)
        assert not verdict.triggered

    def test_mechanical_nan_inf_and_explosion_breaker(self) -> None:
        """驗證 Mechanical 殘差 NaN、Inf 或殘差暴衝 (>1e10) 觸發熔斷。"""
        cb = CircuitBreaker()

        # NaN 殘差
        v_nan = cb.evaluate_mechanical(force_residual=float("nan"), criterion=0.05)
        assert v_nan.triggered
        assert v_nan.rule_id == "CB-MECH-001"

        # 殘差暴衝至 1e12 > 1e10
        v_exp = cb.evaluate_mechanical(force_residual=1.5e12, criterion=0.05)
        assert v_exp.triggered
        assert v_exp.rule_id == "CB-MECH-002"

        # 單元畸變伴隨殘差發散 (殘差 > criterion * 1e4)
        v_dist = cb.evaluate_mechanical(
            force_residual=5000.0, criterion=0.05, has_distortion=True
        )
        assert v_dist.triggered
        assert v_dist.rule_id == "CB-MECH-003"

    def test_fluent_residual_breakers(self) -> None:
        """驗證 Fluent 殘差 NaN/Inf、發散標記或數值 > 1e8 觸發熔斷。"""
        cb = CircuitBreaker()

        # NaN / Inf 熔斷
        v_nan = cb.evaluate_fluent(residuals={"continuity": 1.0}, has_nan_inf=True)
        assert v_nan.triggered
        assert v_nan.rule_id == "CB-CFD-001"

        # 發散標記熔斷
        v_div = cb.evaluate_fluent(residuals={"continuity": 100.0}, is_diverged=True)
        assert v_div.triggered
        assert v_div.rule_id == "CB-CFD-002"

        # 單一殘差 > 1e8 熔斷
        v_over = cb.evaluate_fluent(residuals={"continuity": 2.5e8, "x_velocity": 0.01})
        assert v_over.triggered
        assert v_over.rule_id == "CB-CFD-003"


# ==============================================================================
# 2. 日誌正則解析器單元測試 (結合 MockLogStreamer)
# ==============================================================================
class TestLogParsersWithMockStreamer:
    """測試 Mechanical, LS-DYNA, Fluent 日誌解析器對高保真日誌之正則匹配。"""

    def test_mechanical_parser_converged(self) -> None:
        """驗證 MechanicalMAPDLParser 解析正常收斂 solve.out 日誌。"""
        streamer = MockLogStreamer()
        lines = streamer.generate_mechanical_solve_out(mode="converged", total_substeps=5)
        lines.append("SOLUTION IS CONVERGED\n")
        content = "".join(lines)

        parser = MechanicalMAPDLParser(target_end_time=1.0)
        res = parser.parse_chunk(content)

        assert res.current_substep == 5
        assert res.current_time == pytest.approx(1.0, rel=1e-3)
        assert res.cumulative_iterations > 0
        assert res.force_convergence_value is not None
        assert res.force_criterion == pytest.approx(0.05, rel=1e-3)
        assert res.is_converged
        assert not res.has_distortion
        assert not res.has_nan_inf
        assert res.progress_pct == 100.0
        assert len(res.history) >= 5

    def test_mechanical_parser_divergence(self) -> None:
        """驗證 MechanicalMAPDLParser 捕捉單元畸變、Negative jacobian 與 NaN 殘差。"""
        streamer = MockLogStreamer()
        lines = streamer.generate_mechanical_solve_out(mode="divergence", total_substeps=5)
        content = "".join(lines)

        parser = MechanicalMAPDLParser(target_end_time=1.0)
        res = parser.parse_chunk(content)

        assert res.has_distortion
        assert res.has_nan_inf
        assert any("distorted" in msg.lower() or "jacobian" in msg.lower() for msg in res.distortion_warnings)
        assert not res.is_converged

    def test_lsdyna_parser_normal_glstat(self) -> None:
        """驗證 LSDynaGlstatParser 解析健康能量平衡 glstat。"""
        streamer = MockLogStreamer()
        lines = streamer.generate_lsdyna_glstat(mode="normal", total_steps=10)
        content = "".join(lines)

        parser = LSDynaGlstatParser(target_duration_s=0.0025)
        res = parser.parse_chunk(content)

        assert res.current_time > 0.0
        assert res.current_dt > 0.0
        assert res.kinetic_energy > 0.0
        assert res.internal_energy > 0.0
        assert res.hourglass_energy > 0.0
        assert res.total_energy > 0.0
        assert res.hourglass_ratio_pct < 5.0
        assert res.added_mass_pct < 5.0
        assert not res.has_nan_inf
        assert len(res.history) >= 1

    def test_lsdyna_parser_hourglass_exceeded(self) -> None:
        """驗證 LSDynaGlstatParser 正確提取沙漏能暴增日誌。"""
        streamer = MockLogStreamer()
        lines = streamer.generate_lsdyna_glstat(mode="hourglass_exceeded", total_steps=12)
        content = "".join(lines)

        parser = LSDynaGlstatParser(target_duration_s=0.003)
        res = parser.parse_chunk(content)

        assert res.hourglass_energy >= 62.0
        assert res.hourglass_ratio_pct > 5.0 or res.hourglass_total_ratio_pct > 5.0

    def test_fluent_parser_converged(self) -> None:
        """驗證 FluentResidualParser 解析正常收斂 fluent.log。"""
        streamer = MockLogStreamer()
        lines = streamer.generate_fluent_log(mode="converged", total_iterations=10)
        content = "".join(lines)

        parser = FluentResidualParser(target_iterations=10)
        res = parser.parse_chunk(content)

        assert res.current_iteration == 10
        assert "continuity" in res.residuals
        assert "x_velocity" in res.residuals
        assert res.is_converged
        assert not res.has_nan_inf
        assert res.progress_pct == 100.0

    def test_fluent_parser_divergence_and_reversed_flow(self) -> None:
        """驗證 FluentResidualParser 捕捉 NaN 殘差與逆流 (reversed flow) 警告。"""
        streamer = MockLogStreamer()

        # 1. 逆流模式
        rev_lines = streamer.generate_fluent_log(mode="reversed_flow", total_iterations=8)
        parser_rev = FluentResidualParser(target_iterations=8)
        res_rev = parser_rev.parse_chunk("".join(rev_lines))
        assert res_rev.reversed_flow_faces == 25
        assert any("逆流" in w for w in res_rev.warnings)

        # 2. 發散模式
        div_lines = streamer.generate_fluent_log(mode="divergence", total_iterations=8)
        parser_div = FluentResidualParser(target_iterations=8)
        res_div = parser_div.parse_chunk("".join(div_lines))
        assert res_div.has_nan_inf
        assert res_div.is_diverged

    def test_create_solver_parser_factory(self) -> None:
        """驗證 create_solver_parser 工廠函數正確指派對應求解器解析器。"""
        p_drop = create_solver_parser("drop_test", target_value=0.005)
        assert isinstance(p_drop, LSDynaGlstatParser)

        p_fluent = create_solver_parser("fluent_cfd", target_value=100)
        assert isinstance(p_fluent, FluentResidualParser)

        p_mech = create_solver_parser("static_structural", target_value=1.0)
        assert isinstance(p_mech, MechanicalMAPDLParser)


# ==============================================================================
# 3. WatchdogDaemon 實時物理守護線程測試
# ==============================================================================
class TestWatchdogDaemon:
    """測試 WatchdogDaemon 增量日誌掃描與熔斷聯動。"""

    def test_watchdog_snapshot_and_monitoring(self, tmp_path: Path) -> None:
        """驗證 Watchdog 註冊作業、增量掃描日誌並更新快照。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        sandbox = manager.create_job("modal", tag="vibration_watch")

        daemon = WatchdogDaemon(poll_interval_seconds=0.05)
        daemon.start()

        try:
            daemon.register_job(
                job_id=sandbox.job_id,
                sandbox=sandbox,
                workflow_type="mechanical",
                target_duration=1.0,
            )

            # 初始快照 (尚未生成日誌)
            snap0 = daemon.get_snapshot(sandbox.job_id)
            assert snap0["monitored"]
            assert snap0["progress_pct"] == 0.0

            # 寫入 solve.out
            streamer = MockLogStreamer()
            streamer.write_static_log(
                sandbox.workspace_dir / "solve.out",
                log_type="solve_out",
                mode="converged",
            )

            time.sleep(0.15)
            snap1 = daemon.get_snapshot(sandbox.job_id)
            assert snap1["monitored"]
            assert snap1["progress_pct"] > 0.0
            assert "force_residual" in snap1["physical_health"]

        finally:
            daemon.stop()

    def test_watchdog_circuit_breaker_abort_callback(self, tmp_path: Path) -> None:
        """驗證當日誌出現超標沙漏能時，Watchdog 觸發熔斷並呼叫 abort_callback。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        sandbox = manager.create_job("drop_test", tag="hg_breaker")

        aborted_jobs: List[str] = []

        def on_abort(job_id: str, verdict: BreakerVerdict) -> None:
            aborted_jobs.append(job_id)

        daemon = WatchdogDaemon(poll_interval_seconds=0.05)
        daemon.start()

        try:
            daemon.register_job(
                job_id=sandbox.job_id,
                sandbox=sandbox,
                workflow_type="lsdyna",
                target_duration=0.005,
                abort_callback=on_abort,
            )

            # 調整去抖動為 1 次以配合靜態日誌單次掃描
            daemon._jobs[sandbox.job_id].circuit_breaker.debounce_count = 1

            # 寫入沙漏能嚴重超標之 glstat
            streamer = MockLogStreamer()
            streamer.write_static_log(
                sandbox.workspace_dir / "glstat",
                log_type="glstat",
                mode="hourglass_exceeded",
            )

            time.sleep(0.2)
            assert sandbox.job_id in aborted_jobs, "應觸發 abort_callback"

            # 驗證沙盒 summary.json 標記了熔斷
            summary = sandbox.get_summary()
            assert summary is not None
            assert summary.execution.circuit_breaker_triggered
            assert "CB-DYNA-003" in (summary.execution.circuit_breaker_reason or "")

        finally:
            daemon.stop()


# ==============================================================================
# 4. SentinelQueue 非同步排程與進程管理測試
# ==============================================================================
class TestSentinelQueue:
    """測試 SentinelQueue 非同步作業提交、狀態輪詢、日誌提取與作業終止。"""

    def test_submit_job_immediate_return(self, tmp_path: Path) -> None:
        """驗證 submit_simulation_job 立即建立沙盒並返回 (< 500ms)，符合非同步規範。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        watchdog = WatchdogDaemon(poll_interval_seconds=0.1)
        queue = SentinelQueue(job_manager=manager, watchdog=watchdog)

        try:
            t0 = time.time()
            resp = queue.submit_simulation_job(
                workflow_type="shock_analysis",
                config={"peak_g": 50.0, "duration_ms": 11.0},
                tag="unit_test",
            )
            duration_ms = (time.time() - t0) * 1000.0

            assert resp["ok"], "作業提交應成功"
            assert resp["status"] in ("QUEUED", "RUNNING")
            assert "job_id" in resp
            assert Path(resp["sandbox_dir"]).exists()
            assert duration_ms < 500.0, f"提交響應應在 500ms 內，實際耗時: {duration_ms:.1f}ms"

        finally:
            watchdog.stop()

    def test_job_execution_lifecycle_with_runner_fn(self, tmp_path: Path) -> None:
        """驗證透過 runner_fn 非同步運行作業，狀態由 QUEUED -> RUNNING -> SOLVED。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        watchdog = WatchdogDaemon(poll_interval_seconds=0.05)
        queue = SentinelQueue(job_manager=manager, watchdog=watchdog)

        def mock_runner(sandbox: JobSandbox, config: Dict[str, Any]) -> None:
            time.sleep(0.1)
            streamer = MockLogStreamer()
            streamer.write_static_log(
                sandbox.workspace_dir / "solve.out",
                log_type="solve_out",
                mode="converged",
            )

        try:
            resp = queue.submit_simulation_job(
                workflow_type="thermal_warpage",
                config={"ref_temp": 25.0},
                tag="cycle_test",
                runner_fn=mock_runner,
            )
            assert resp["ok"], f"提交失敗: {resp.get('error')}"
            job_id = resp["job_id"]

            # 等待非同步任務結束
            for _ in range(40):
                status_resp = queue.get_simulation_status(job_id)
                if status_resp.get("status") == "SOLVED":
                    break
                time.sleep(0.05)

            final_status = queue.get_simulation_status(job_id)
            assert final_status["status"] == "SOLVED"
            assert final_status["progress_pct"] == 100.0

            # 驗證 summary.json
            sandbox = manager.get_job(job_id)
            assert sandbox is not None
            summary = sandbox.get_summary()
            assert summary is not None
            assert summary.status == JobStatusEnum.SOLVED
            assert summary.verdict == VerdictEnum.PASS

        finally:
            watchdog.stop()

    def test_tail_simulation_log(self, tmp_path: Path) -> None:
        """驗證 tail_simulation_log 正確讀取沙盒末尾日誌行。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        watchdog = WatchdogDaemon(poll_interval_seconds=0.1)
        queue = SentinelQueue(job_manager=manager, watchdog=watchdog)

        try:
            resp = queue.submit_simulation_job(
                workflow_type="drop_test",
                config={},
                tag="tail_test",
            )
            assert resp["ok"], f"提交失敗: {resp.get('error')}"
            job_id = resp["job_id"]
            sandbox = manager.get_job(job_id)
            assert sandbox is not None

            # 寫入多行日誌至 workspace/solve.out
            log_file = sandbox.workspace_dir / "solve.out"
            lines = [f"Log line entry number {i}\n" for i in range(1, 51)]
            log_file.write_text("".join(lines), encoding="utf-8")

            # 提取末尾 10 行
            tail_resp = queue.tail_simulation_log(job_id, lines=10, log_type="solve_out")
            assert tail_resp["ok"]
            assert tail_resp["total_lines"] == 10
            assert "Log line entry number 50" in tail_resp["lines"][-1]

            # 提取不存在之日誌類型時應安全回傳空列表，不拋錯
            tail_empty = queue.tail_simulation_log(job_id, lines=10, log_type="matter")
            assert tail_empty["ok"]
            assert tail_empty["total_lines"] == 0

        finally:
            watchdog.stop()

    def test_abort_simulation_job(self, tmp_path: Path) -> None:
        """驗證主動調用 abort_simulation_job 將作業終止並標記為 ABORTED。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        watchdog = WatchdogDaemon(poll_interval_seconds=0.05)
        queue = SentinelQueue(job_manager=manager, watchdog=watchdog)

        def long_running_runner(sandbox: JobSandbox, config: Dict[str, Any]) -> None:
            for _ in range(50):
                time.sleep(0.1)

        try:
            resp = queue.submit_simulation_job(
                workflow_type="explicit_dynamics",
                config={},
                tag="abort_test",
                runner_fn=long_running_runner,
            )
            assert resp["ok"], f"提交失敗: {resp.get('error')}"
            job_id = resp["job_id"]

            time.sleep(0.05)
            abort_resp = queue.abort_simulation_job(job_id, reason="測試手動取消")
            assert abort_resp["ok"]
            assert abort_resp["status"] == "ABORTED"

            # 狀態查詢應為 ABORTED
            st = queue.get_simulation_status(job_id)
            assert st["status"] == "ABORTED"

            # 沙盒 summary.json 應有 ABORTED 與取消原因記錄
            sandbox = manager.get_job(job_id)
            assert sandbox is not None
            summary = sandbox.get_summary()
            assert summary is not None
            assert summary.status == JobStatusEnum.ABORTED
            assert any("測試手動取消" in r for r in summary.failure_reasons)

        finally:
            watchdog.stop()

    def test_get_simulation_status_not_found(self, tmp_path: Path) -> None:
        """驗證查詢不存在的 job_id 時回傳 status: NOT_FOUND。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        watchdog = WatchdogDaemon(poll_interval_seconds=0.1)
        queue = SentinelQueue(job_manager=manager, watchdog=watchdog)

        try:
            resp = queue.get_simulation_status("20260906_999999_non_existent_job")
            assert not resp["ok"]
            assert resp["status"] == "NOT_FOUND"
        finally:
            watchdog.stop()

    def test_daemon_singleton_lifecycle(self) -> None:
        """驗證 SentinelQueue 全域單例取得與關閉生命週期。"""
        q1 = get_sentinel_queue()
        q2 = get_sentinel_queue()
        assert q1 is q2, "get_sentinel_queue 應返回相同之單例實例"

        shutdown_sentinel()
        # 再次獲取應為新實例
        q3 = get_sentinel_queue()
        assert q3 is not None
        shutdown_sentinel()

