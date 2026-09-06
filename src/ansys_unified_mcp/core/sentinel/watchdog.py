"""ANSYS Unified MCP 2.0 - 實時物理守護線程 (WatchdogDaemon).

在背景線程中定時輪詢監控各活動沙盒工作目錄日誌：
- 串流解析求解日誌 (solve.out, glstat, matter.out, fluent.log, stdout.log)
- 即時換算進度百分比 (progress_pct)、時間步與收斂殘差
- 評估 CircuitBreaker 早期發散熔斷
- 觸發熔斷時主動調用進程中斷與更新沙盒成果
"""

from __future__ import annotations

import logging
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ansys_unified_mcp.core.sentinel.circuit_breaker import (
    BreakerVerdict,
    CircuitBreaker,
)
from ansys_unified_mcp.core.sentinel.parsers import (
    FluentResidualParser,
    LSDynaGlstatParser,
    MechanicalMAPDLParser,
    create_solver_parser,
)
from ansys_unified_mcp.jobs.models import (
    JobStatusEnum,
    SimulationSummary,
    VerdictEnum,
)
from ansys_unified_mcp.jobs.sandbox import JobSandbox

logger = logging.getLogger("ansys-unified-mcp.sentinel.watchdog")


@dataclass
class JobWatchContext:
    """單一作業守護上下文。"""

    job_id: str
    sandbox: JobSandbox
    workflow_type: str
    target_duration: float = 1.0
    parser: Any = None
    circuit_breaker: CircuitBreaker = field(default_factory=CircuitBreaker)
    file_offsets: Dict[str, int] = field(default_factory=dict)
    last_verdict: Optional[BreakerVerdict] = None
    abort_callback: Optional[Callable[[str, BreakerVerdict], None]] = None
    is_active: bool = True
    start_time: float = field(default_factory=time.time)


class WatchdogDaemon:
    """實時物理守護後台線程管理器。"""

    def __init__(self, poll_interval_seconds: float = 0.5) -> None:
        """初始化守護線程管理器。

        Args:
            poll_interval_seconds: 日誌掃描輪詢週期 (秒)
        """
        self.poll_interval = poll_interval_seconds
        self._jobs: Dict[str, JobWatchContext] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """啟動後台守護線程。"""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._thread = threading.Thread(
                target=self._monitor_loop,
                name="SentinelWatchdogDaemon",
                daemon=True,
            )
            self._thread.start()
            logger.info("WatchdogDaemon 背景物理守護線程已啟動。")

    def stop(self) -> None:
        """停止後台守護線程。"""
        with self._lock:
            self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
            logger.info("WatchdogDaemon 背景物理守護線程已停止。")

    def register_job(
        self,
        job_id: str,
        sandbox: JobSandbox,
        workflow_type: str,
        target_duration: float = 1.0,
        abort_callback: Optional[Callable[[str, BreakerVerdict], None]] = None,
    ) -> None:
        """註冊新作業進入守護清單。"""
        with self._lock:
            parser = create_solver_parser(workflow_type, target_value=target_duration)
            ctx = JobWatchContext(
                job_id=job_id,
                sandbox=sandbox,
                workflow_type=workflow_type,
                target_duration=target_duration,
                parser=parser,
                abort_callback=abort_callback,
            )
            self._jobs[job_id] = ctx
            logger.info(f"作業 [{job_id}] (工作流: {workflow_type}) 已註冊至 Watchdog 監控。")

    def unregister_job(self, job_id: str) -> None:
        """取消作業守護監控。"""
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].is_active = False
                del self._jobs[job_id]
                logger.info(f"作業 [{job_id}] 已自 Watchdog 監控移除。")

    def get_snapshot(self, job_id: str) -> Dict[str, Any]:
        """獲取指定作業之實時守護健康與進度快照。"""
        with self._lock:
            ctx = self._jobs.get(job_id)
            if not ctx:
                return {
                    "job_id": job_id,
                    "monitored": False,
                    "progress_pct": 0.0,
                    "current_step": "UNKNOWN",
                    "physical_health": {"status": "NOT_MONITORED"},
                    "elapsed_seconds": 0.0,
                }

            elapsed = time.time() - ctx.start_time
            parser = ctx.parser
            progress_pct = 0.0
            current_step = "RUNNING"
            health_info: Dict[str, Any] = {"healthy": True}

            if isinstance(parser, MechanicalMAPDLParser):
                res = parser.result
                progress_pct = res.progress_pct
                current_step = f"Step {res.current_load_step} Substep {res.current_substep} (t={res.current_time:.4e}s)"
                health_info = {
                    "force_residual": res.force_convergence_value,
                    "criterion": res.force_criterion,
                    "distortion": res.has_distortion,
                    "nan_inf": res.has_nan_inf,
                    "converged": res.is_converged,
                }
            elif isinstance(parser, LSDynaGlstatParser):
                res = parser.result
                progress_pct = res.progress_pct
                current_step = f"t={res.current_time:.6e}s (dt={res.current_dt:.2e}s)"
                health_info = {
                    "hourglass_ratio_pct": res.hourglass_ratio_pct,
                    "hourglass_total_ratio_pct": res.hourglass_total_ratio_pct,
                    "mass_scaling_added_pct": res.added_mass_pct,
                    "sliding_energy": res.sliding_energy,
                    "nan_inf": res.has_nan_inf,
                    "completed": res.is_completed,
                }
            elif isinstance(parser, FluentResidualParser):
                res = parser.result
                progress_pct = res.progress_pct
                current_step = f"Iteration {res.current_iteration}"
                health_info = {
                    "residuals": dict(res.residuals),
                    "reversed_flow_faces": res.reversed_flow_faces,
                    "nan_inf": res.has_nan_inf,
                    "converged": res.is_converged,
                }

            if ctx.last_verdict and ctx.last_verdict.triggered:
                health_info["circuit_breaker_triggered"] = True
                health_info["circuit_breaker_reason"] = ctx.last_verdict.reason
                health_info["rule_id"] = ctx.last_verdict.rule_id

            return {
                "job_id": job_id,
                "monitored": True,
                "progress_pct": progress_pct,
                "current_step": current_step,
                "physical_health": health_info,
                "elapsed_seconds": round(elapsed, 2),
            }

    def _monitor_loop(self) -> None:
        """後台輪詢迴圈。"""
        while self._running:
            try:
                active_contexts: List[JobWatchContext] = []
                with self._lock:
                    active_contexts = [ctx for ctx in self._jobs.values() if ctx.is_active]

                for ctx in active_contexts:
                    self._check_job_logs(ctx)

            except Exception as e:
                logger.error(f"WatchdogDaemon 輪詢發生未預期異常: {e}", exc_info=True)

            time.sleep(self.poll_interval)

    def _check_job_logs(self, ctx: JobWatchContext) -> None:
        """掃描並讀取沙盒 workspace/ 內之最新日誌。"""
        workspace = ctx.sandbox.workspace_dir
        if not workspace.exists():
            return

        # 候選日誌清單
        candidate_logs = [
            "solve.out",
            "glstat",
            "matter.out",
            "matsum",
            "d3hsp",
            "fluent.log",
            "run.log",
            "stdout.log",
            "solver.log",
        ]

        found_any = False
        for log_name in candidate_logs:
            log_path = workspace / log_name
            if not log_path.exists() or not log_path.is_file():
                continue

            found_any = True
            self._process_single_log(ctx, log_path)

        # 若未發現標準命名檔案，搜尋 workspace 下所有 .out, .log 檔案
        if not found_any:
            try:
                for file_p in workspace.glob("*.log"):
                    self._process_single_log(ctx, file_p)
                for file_p in workspace.glob("*.out"):
                    self._process_single_log(ctx, file_p)
            except Exception:
                pass

    def _process_single_log(self, ctx: JobWatchContext, log_path: Path) -> None:
        """增量讀取單一檔案並交給 Parser 與 CircuitBreaker 檢驗。"""
        try:
            file_key = str(log_path.name)
            last_offset = ctx.file_offsets.get(file_key, 0)
            file_size = log_path.stat().st_size

            if file_size <= last_offset:
                return

            # 增量讀取新寫入內容 (安全分塊限制，防止單次暴增 OOM)
            bytes_to_read = min(file_size - last_offset, 2 * 1024 * 1024)  # 最大 2MB
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(last_offset)
                new_chunk = f.read(bytes_to_read)
                ctx.file_offsets[file_key] = f.tell()

            if not new_chunk:
                return

            # 1. 提交至解析器
            parser = ctx.parser
            if parser is None:
                return

            parse_res = parser.parse_chunk(new_chunk)

            # 2. 提交至熔斷器評估
            verdict = BreakerVerdict(triggered=False)
            if isinstance(parser, LSDynaGlstatParser):
                verdict = ctx.circuit_breaker.evaluate_lsdyna(
                    hourglass_energy=parse_res.hourglass_energy,
                    internal_energy=parse_res.internal_energy,
                    total_energy=parse_res.total_energy,
                    sliding_energy=parse_res.sliding_energy,
                    added_mass_pct=parse_res.added_mass_pct,
                    has_nan_inf=parse_res.has_nan_inf,
                    current_time=parse_res.current_time,
                )
            elif isinstance(parser, MechanicalMAPDLParser):
                verdict = ctx.circuit_breaker.evaluate_mechanical(
                    force_residual=parse_res.force_convergence_value,
                    criterion=parse_res.force_criterion,
                    has_distortion=parse_res.has_distortion,
                    has_nan_inf=parse_res.has_nan_inf,
                    substep=parse_res.current_substep,
                )
            elif isinstance(parser, FluentResidualParser):
                verdict = ctx.circuit_breaker.evaluate_fluent(
                    residuals=parse_res.residuals,
                    has_nan_inf=parse_res.has_nan_inf,
                    is_diverged=parse_res.is_diverged,
                    reversed_flow_faces=parse_res.reversed_flow_faces,
                    iteration=parse_res.current_iteration,
                )

            # 3. 若熔斷觸發，處置
            if verdict.triggered:
                ctx.last_verdict = verdict
                logger.warning(
                    f"作業 [{ctx.job_id}] 觸發早期物理發散熔斷！規則: {verdict.rule_id}, 原因: {verdict.reason}"
                )
                # 更新沙盒 summary.json
                self._record_abort_in_summary(ctx, verdict)

                # 呼叫終止回呼
                if ctx.abort_callback:
                    try:
                        ctx.abort_callback(ctx.job_id, verdict)
                    except Exception as e:
                        logger.error(f"調用作業中斷回呼失敗: {e}", exc_info=True)

                ctx.is_active = False

        except Exception as e:
            logger.debug(f"讀取解析日誌 [{log_path.name}] 異常: {e}")

    def _record_abort_in_summary(self, ctx: JobWatchContext, verdict: BreakerVerdict) -> None:
        """在沙盒 summary.json 記錄熔斷原因與狀態。"""
        try:
            summary = ctx.sandbox.get_summary()
            if summary:
                summary.status = JobStatusEnum.ABORTED
                summary.verdict = VerdictEnum.FAIL
                summary.execution.circuit_breaker_triggered = True
                summary.execution.circuit_breaker_reason = (
                    f"[{verdict.rule_id}] {verdict.reason} | 建議處方: {verdict.suggested_fix}"
                )
                if verdict.reason not in summary.failure_reasons:
                    summary.failure_reasons.append(verdict.reason)
                ctx.sandbox.save_summary(summary)
        except Exception as e:
            logger.error(f"寫入熔斷資訊至 summary.json 失敗: {e}")
