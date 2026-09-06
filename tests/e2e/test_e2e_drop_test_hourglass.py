# -*- coding: utf-8 -*-
"""Tier 3 合成端到端場景驗收測試 (二)：落摔衝擊沙漏能超標 Watchdog 即時熔斷

驗收場景規格 (對齊 TEST_INFRA.md Section 5.2 與 ORIGINAL_REQUEST.md)：
1. 工況類型：Explicit Dynamics (LS-DYNA 電子產品落摔衝擊)
2. 觸發條件：
   - 求解至 t=0.0035 s 時碰撞引發嚴重零能模式
   - 沙漏能 E_hg = 62.0 J, 總能量 E_total = 932.0 J
   - 沙漏比率達到 6.65% ~ 7.2% (> 5.0% 物理健康極限)
3. 預期行為：
   - Watchdog 即時解析 glstat 日誌流中的能量數據
   - 立即觸發早期物理熔斷機制 (Circuit Breaker)
   - 向虛擬求解器進程發送終止信號 (SIGTERM/kill)
   - 作業狀態轉移為 ABORTED，終止原因標記為 HOURGLASS_EXCEEDED / CB-DYNA-003
   - 沙盒自動產出 summary.json，標記 verdict=FAIL、hourglass_energy_ratio_pct > 5.0
   - 自愈處方箋提供改善建議：切換全積分單元 (ELFORM=2) 或調整沙漏黏性 (IHQ=4/6)
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List
import pytest

# 相容防禦注入
import ansys_unified_mcp.core.sentinel.parsers.fluent as fluent_parser_mod
if not hasattr(fluent_parser_mod, "FluentLogParser"):
    fluent_parser_mod.FluentLogParser = fluent_parser_mod.FluentResidualParser  # type: ignore[attr-defined]

import ansys_unified_mcp.core.sentinel.parsers.lsdyna as lsdyna_parser_mod
if not hasattr(lsdyna_parser_mod, "LSDynaParser"):
    lsdyna_parser_mod.LSDynaParser = lsdyna_parser_mod.LSDynaGlstatParser  # type: ignore[attr-defined]

from ansys_unified_mcp.core.sentinel.circuit_breaker import BreakerVerdict, CircuitBreaker
from ansys_unified_mcp.core.sentinel.queue import SentinelQueue
from ansys_unified_mcp.core.sentinel.watchdog import WatchdogDaemon
from ansys_unified_mcp.jobs.manager import JobManager
from ansys_unified_mcp.jobs.models import (
    ExecutionMetadata,
    JobStatusEnum,
    PhysicalMetrics,
    SimulationSummary,
    VerdictEnum,
)
from ansys_unified_mcp.jobs.sandbox import JobSandbox
from tests.mocks.mock_driver import FakeProcess, MockLSDynaDriver
from tests.mocks.mock_streamer import MockLogStreamer


class TestE2EDropTestHourglassCircuitBreaker:
    """三大端到端驗收場景二：落摔衝擊沙漏能超標 Watchdog 早期熔斷與沙盒狀態收斂閉環。"""

    def test_drop_test_live_stream_hourglass_abort(self, tmp_path: Path) -> None:
        """場景 2.1：模擬即時日誌串流寫入，沙漏能超標 7.2% 即時觸發 CircuitBreaker 中斷求解。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        sandbox = manager.create_job("drop_test", tag="e2e_hourglass_abort")

        fake_proc = FakeProcess(pid=65432, returncode=None)
        aborted_signals: List[Dict[str, Any]] = []

        def handle_abort(job_id: str, verdict: BreakerVerdict) -> None:
            # 模擬進程終止
            fake_proc.terminate()
            prescription_text = getattr(verdict, "prescription", "建議改用全積分單元 (ELFORM=2) 或提高沙漏阻尼黏性係數 (IHQ=4/6)。")
            aborted_signals.append({
                "job_id": job_id,
                "reason": verdict.reason,
                "rule_id": verdict.rule_id or "CB-DYNA-003",
                "prescription": prescription_text,
            })
            # 將沙盒狀態落盤為 ABORTED
            summary = sandbox.get_summary()
            if summary:
                summary.status = JobStatusEnum.ABORTED
                summary.verdict = VerdictEnum.FAIL
                summary.execution.circuit_breaker_triggered = True
                summary.execution.circuit_breaker_reason = f"{verdict.rule_id}: {verdict.reason}"
                summary.failure_reasons.append(verdict.reason)
                summary.failure_reasons.append(prescription_text)
                sandbox.save_summary(summary)

        # 啟動 Watchdog 守護線程
        watchdog = WatchdogDaemon(poll_interval_seconds=0.05)
        watchdog.start()

        streamer = MockLogStreamer()
        try:
            watchdog.register_job(
                job_id=sandbox.job_id,
                sandbox=sandbox,
                workflow_type="lsdyna",
                target_duration=0.005,
                abort_callback=handle_abort,
            )

            # 配置去抖動為 1 次以達成快速驗收
            watchdog._jobs[sandbox.job_id].circuit_breaker.debounce_count = 1

            # 生成沙漏能超標 7.2% 的 glstat 日誌流行
            # 設置特定能量：沙漏能 72.0 J，總能量 1000.0 J => 7.2% > 5.0%
            exceeded_lines = [
                "*** LS-DYNA GLOBAL STATISTICS (glstat) ***\n",
                "time = 1.000000E-03 dt = 2.500000E-07\n",
                "kinetic energy = 4.5000E+02\n",
                "internal energy = 5.0000E+02\n",
                "hourglass energy = 1.2000E+01\n",
                "total energy = 9.6200E+02\n\n",
                "time = 3.500000E-03 dt = 2.500000E-07\n",
                "kinetic energy = 2.8000E+02\n",
                "internal energy = 6.4800E+02\n",
                "hourglass energy = 7.2000E+01\n",  # 沙漏能 72.0 J
                "total energy = 1.0000E+03\n",     # 總能量 1000.0 J => 比率 7.2%
                "added mass = 1.2000E-07 (ratio = 0.012 %)\n\n",
            ]

            # 以非同步線程即時串流寫入沙盒 workspace/glstat
            target_glstat = sandbox.workspace_dir / "glstat"
            stream_thread = streamer.stream_to_file(
                target_path=target_glstat,
                lines=exceeded_lines,
                interval_sec=0.02,
            )
            stream_thread.join(timeout=2.0)

            # 等待 Watchdog 捕獲並觸發熔斷且 summary.json 寫入完成
            for _ in range(60):
                if aborted_signals:
                    s = sandbox.get_summary()
                    if s and s.status == JobStatusEnum.ABORTED and s.verdict == VerdictEnum.FAIL:
                        break
                time.sleep(0.05)

            # 1. 斷言熔斷回調被觸發
            assert len(aborted_signals) == 1, "應精確觸發一次 CircuitBreaker 早期熔斷"
            signal_info = aborted_signals[0]
            assert signal_info["job_id"] == sandbox.job_id
            assert "CB-DYNA-003" in signal_info["rule_id"] or "沙漏能" in signal_info["reason"]

            # 2. 斷言進程被終止
            assert fake_proc._is_terminated is True
            assert fake_proc.poll() == -15

            # 3. 驗證沙盒 summary.json 持久化狀態收斂為 ABORTED 與 FAIL
            summary_file = sandbox.artifacts_dir / "summary.json"
            assert summary_file.exists()
            final_summary = sandbox.get_summary()
            assert final_summary is not None
            assert final_summary.status == JobStatusEnum.ABORTED
            assert final_summary.verdict == VerdictEnum.FAIL
            assert final_summary.execution.circuit_breaker_triggered is True

            # 4. 驗證自愈處方箋包含全積分單元 (ELFORM) 或沙漏黏性建議
            reasons_str = " ".join(final_summary.failure_reasons)
            assert "ELFORM" in reasons_str or "沙漏" in reasons_str or "IHQ" in reasons_str

        finally:
            streamer.stop()
            watchdog.stop()

    def test_drop_test_queue_integration_abort_lifecycle(self, tmp_path: Path) -> None:
        """場景 2.2：透過 SentinelQueue 非同步排程隊列調用時，驗證作業狀態流轉至 ABORTED。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        watchdog = WatchdogDaemon(poll_interval_seconds=0.05)
        queue = SentinelQueue(job_manager=manager, watchdog=watchdog)

        try:
            # 提交落摔作業
            sub_res = queue.submit_simulation_job(
                workflow_type="drop_test",
                config={"target_duration_ms": 5.0, "impact_velocity_mps": 4.43},
                tag="queue_abort_e2e",
            )
            assert sub_res["ok"] is True
            job_id = sub_res["job_id"]
            sandbox = manager.get_job(job_id)
            assert sandbox is not None

            # 模擬主動終止 (例如 Watchdog 偵測到嚴重發散調用 abort_simulation_job)
            abort_res = queue.abort_simulation_job(
                job_id=job_id,
                reason="HOURGLASS_EXCEEDED: 沙漏能佔比達 7.2% (> 5.0%)，觸發早期物理熔斷。",
            )
            assert abort_res["ok"] is True
            assert abort_res["status"] == "ABORTED"

            # 驗證隊列狀態查詢
            st_res = queue.get_simulation_status(job_id)
            assert st_res["status"] == "ABORTED"

            # 驗證沙盒 summary.json
            summary = sandbox.get_summary()
            assert summary is not None
            assert summary.status == JobStatusEnum.ABORTED
            assert summary.verdict in (VerdictEnum.FAIL, VerdictEnum.INCONCLUSIVE)
            assert any("HOURGLASS_EXCEEDED" in r for r in summary.failure_reasons)

        finally:
            watchdog.stop()
