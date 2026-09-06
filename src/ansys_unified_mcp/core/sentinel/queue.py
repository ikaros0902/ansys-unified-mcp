"""ANSYS Unified MCP 2.0 - 非同步作業排程隊列 (SentinelQueue).

管理模擬作業之非同步生命週期 (QUEUED -> RUNNING -> SOLVED / FAILED / ABORTED)：
- 接收作業提交並立即建立沙盒與返回 job_id，防止 MCP 客戶端逾時 (< 500ms)
- 在背景安全啟動求解器子進程或工作流調用
- 整合 WatchdogDaemon 實時物理守護與熔斷
- 支援狀態輪詢 (get_simulation_status)、串流日誌獲取 (tail_simulation_log) 與優雅終止 (abort_simulation_job)
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import psutil

from ansys_unified_mcp.core.sentinel.circuit_breaker import BreakerVerdict
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

logger = logging.getLogger("ansys-unified-mcp.sentinel.queue")


class ActiveJobRecord:
    """活動作業運行記錄。"""

    def __init__(
        self,
        job_id: str,
        sandbox: JobSandbox,
        workflow_type: str,
        config: Dict[str, Any],
    ) -> None:
        self.job_id = job_id
        self.sandbox = sandbox
        self.workflow_type = workflow_type
        self.config = config
        self.status = JobStatusEnum.QUEUED
        self.process: Optional[subprocess.Popen] = None
        self.thread: Optional[threading.Thread] = None
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.exit_code: Optional[int] = None
        self.abort_reason: Optional[str] = None
        self.error_messages: List[str] = []


class SentinelQueue:
    """非同步作業排程與進程生命週期管理器。"""

    def __init__(
        self,
        job_manager: Optional[JobManager] = None,
        watchdog: Optional[WatchdogDaemon] = None,
    ) -> None:
        self.job_manager = job_manager or JobManager()
        self.watchdog = watchdog or WatchdogDaemon()
        self.watchdog.start()

        self._jobs: Dict[str, ActiveJobRecord] = {}
        self._lock = threading.Lock()

    def submit_simulation_job(
        self,
        workflow_type: str,
        config: Dict[str, Any],
        tag: str = "default",
        solver_cmd: Optional[List[str]] = None,
        runner_fn: Optional[Callable[[JobSandbox, Dict[str, Any]], None]] = None,
        target_duration: float = 1.0,
    ) -> Dict[str, Any]:
        """立即建立作業沙盒並送入非同步執行隊列，500ms 內返回。"""
        try:
            # 1. 建立獨立作業沙盒
            solver_name = config.get("solver", "ANSYS")
            sandbox = self.job_manager.create_job(
                workflow_type=workflow_type,
                tag=tag,
                solver_name=solver_name,
                init_summary=True,
            )
            job_id = sandbox.job_id

            # 2. 將配置直接安全寫入 inputs/ (避免路徑穿越檢查誤判)
            job_config_path = sandbox.inputs_dir / "job_config.json"
            job_config_path.write_text(
                json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8"
            )

            # 3. 註冊活動記錄
            record = ActiveJobRecord(
                job_id=job_id,
                sandbox=sandbox,
                workflow_type=workflow_type,
                config=config,
            )

            with self._lock:
                self._jobs[job_id] = record

            # 4. 註冊 Watchdog 守護
            def on_circuit_breaker(triggered_job_id: str, verdict: BreakerVerdict) -> None:
                self._handle_watchdog_abort(triggered_job_id, verdict)

            self.watchdog.register_job(
                job_id=job_id,
                sandbox=sandbox,
                workflow_type=workflow_type,
                target_duration=target_duration,
                abort_callback=on_circuit_breaker,
            )

            # 5. 非同步背景線程啟動求解
            t = threading.Thread(
                target=self._run_job_async,
                args=(record, solver_cmd, runner_fn),
                name=f"JobRunner-{job_id}",
                daemon=True,
            )
            record.thread = t
            t.start()

            return {
                "ok": True,
                "job_id": job_id,
                "sandbox_dir": str(sandbox.root_dir),
                "status": JobStatusEnum.QUEUED.value,
                "message": f"模擬作業 [{job_id}] 已送入非同步執行隊列。",
            }

        except Exception as e:
            logger.error(f"提交模擬作業失敗: {e}", exc_info=True)
            return {
                "ok": False,
                "error": f"作業提交失敗: {str(e)}",
            }

    def get_simulation_status(self, job_id: str) -> Dict[str, Any]:
        """查詢作業即時狀態、進度百分比、時間步、殘差與物理守護健康度。"""
        # 1. 先從記憶體活動隊列查詢
        with self._lock:
            record = self._jobs.get(job_id)

        if record:
            snapshot = self.watchdog.get_snapshot(job_id)
            elapsed = 0.0
            if record.start_time:
                elapsed = time.time() - record.start_time

            progress = snapshot.get("progress_pct", 0.0)
            if record.status == JobStatusEnum.SOLVED:
                progress = 100.0

            return {
                "ok": True,
                "job_id": job_id,
                "status": record.status.value,
                "progress_pct": progress,
                "current_step": snapshot.get("current_step", "WAITING"),
                "physical_health": snapshot.get("physical_health", {}),
                "elapsed_seconds": round(elapsed, 2),
            }

        # 2. 若不在活動隊列，嘗試自沙盒讀取歷史成果 summary.json
        sandbox = self.job_manager.get_job(job_id)
        if not sandbox:
            return {
                "ok": False,
                "job_id": job_id,
                "status": "NOT_FOUND",
                "error": f"找不到作業 ID: {job_id}",
            }

        summary = sandbox.get_summary()
        if summary:
            return {
                "ok": True,
                "job_id": job_id,
                "status": summary.status.value,
                "progress_pct": 100.0 if summary.status == JobStatusEnum.SOLVED else 0.0,
                "current_step": "FINISHED",
                "physical_health": {
                    "verdict": summary.verdict.value,
                    "circuit_breaker_triggered": summary.execution.circuit_breaker_triggered,
                    "circuit_breaker_reason": summary.execution.circuit_breaker_reason,
                    "failure_reasons": summary.failure_reasons,
                },
                "elapsed_seconds": summary.execution.duration_seconds or 0.0,
            }

        return {
            "ok": True,
            "job_id": job_id,
            "status": "UNKNOWN",
            "progress_pct": 0.0,
            "current_step": "UNKNOWN",
            "physical_health": {},
            "elapsed_seconds": 0.0,
        }

    def tail_simulation_log(
        self,
        job_id: str,
        lines: int = 100,
        log_type: str = "solve_out",
    ) -> Dict[str, Any]:
        """串流獲取即時日誌尾端行數。"""
        sandbox = self.job_manager.get_job(job_id)
        if not sandbox:
            return {
                "ok": False,
                "job_id": job_id,
                "error": f"找不到作業沙盒: {job_id}",
            }

        type_mapping = {
            "solve_out": "solve.out",
            "glstat": "glstat",
            "matter": "matter.out",
            "fluent": "fluent.log",
            "stdout": "stdout.log",
            "stderr": "stderr.log",
            "run": "run.log",
            "solver": "solver.log",
        }

        target_file_name = type_mapping.get(log_type.lower(), log_type)
        workspace = sandbox.workspace_dir
        log_path = (workspace / target_file_name).resolve()

        # 邊界保護：嚴防透過 log_type 穿越超出 workspace_dir
        if not log_path.is_relative_to(workspace.resolve()):
            return {
                "ok": False,
                "job_id": job_id,
                "error": f"安全阻斷：log_type 包含非法路徑穿越字元: {log_type}",
            }

        if not log_path.exists():
            return {
                "ok": True,
                "job_id": job_id,
                "log_type": log_type,
                "lines": [],
                "total_lines": 0,
                "message": f"日誌檔案尚未生成 ({target_file_name})",
            }

        try:
            tail_lines = self._read_tail_lines(log_path, lines=lines)
            return {
                "ok": True,
                "job_id": job_id,
                "log_type": log_type,
                "file_name": log_path.name,
                "lines": tail_lines,
                "total_lines": len(tail_lines),
            }
        except Exception as e:
            return {
                "ok": False,
                "job_id": job_id,
                "error": f"讀取日誌失敗: {str(e)}",
            }

    def abort_simulation_job(
        self,
        job_id: str,
        reason: str = "user_requested",
    ) -> Dict[str, Any]:
        """優雅終止底層求解進程，釋放授權，並將狀態標記為 ABORTED。"""
        with self._lock:
            record = self._jobs.get(job_id)
            if record:
                record.abort_reason = reason
                record.status = JobStatusEnum.ABORTED
                proc_to_kill = record.process
            else:
                proc_to_kill = None

        if not record:
            sandbox = self.job_manager.get_job(job_id)
            if sandbox:
                summary = sandbox.get_summary()
                if summary and summary.status in (JobStatusEnum.RUNNING, JobStatusEnum.QUEUED):
                    summary.status = JobStatusEnum.ABORTED
                    summary.failure_reasons.append(f"作業終止: {reason}")
                    sandbox.save_summary(summary)
            return {
                "ok": True,
                "job_id": job_id,
                "status": JobStatusEnum.ABORTED.value,
                "reason": reason,
                "message": "作業已標記為 ABORTED (不在活動內存中)。",
            }

        # 終止進程樹
        if proc_to_kill:
            self._terminate_process_tree(proc_to_kill)

        # 取消 Watchdog 守護
        self.watchdog.unregister_job(job_id)

        # 更新 summary.json
        try:
            summary = record.sandbox.get_summary()
            if summary:
                summary.status = JobStatusEnum.ABORTED
                summary.execution.finished_at = datetime.now(timezone.utc).isoformat()
                if record.start_time:
                    summary.execution.duration_seconds = round(time.time() - record.start_time, 2)
                summary.failure_reasons.append(f"作業終止: {reason}")
                record.sandbox.save_summary(summary)
        except Exception as e:
            logger.error(f"更新 ABORTED summary.json 失敗: {e}")

        return {
            "ok": True,
            "job_id": job_id,
            "status": JobStatusEnum.ABORTED.value,
            "reason": reason,
        }

    def _run_job_async(
        self,
        record: ActiveJobRecord,
        solver_cmd: Optional[List[str]],
        runner_fn: Optional[Callable[[JobSandbox, Dict[str, Any]], None]],
    ) -> None:
        """非同步作業執行器主迴圈。"""
        with self._lock:
            if record.status == JobStatusEnum.ABORTED:
                logger.info(f"作業 [{record.job_id}] 已在啟動前被取消 (ABORTED)，終止背景執行。")
                return
            record.start_time = time.time()
            record.status = JobStatusEnum.RUNNING

        summary = record.sandbox.get_summary()
        if summary:
            with self._lock:
                if record.status == JobStatusEnum.ABORTED:
                    return
                summary.status = JobStatusEnum.RUNNING
                summary.execution.started_at = datetime.now(timezone.utc).isoformat()
            record.sandbox.save_summary(summary)

        workspace = record.sandbox.workspace_dir
        stdout_log_path = workspace / "stdout.log"
        stderr_log_path = workspace / "stderr.log"

        try:
            with self._lock:
                if record.status == JobStatusEnum.ABORTED:
                    return

            if runner_fn:
                logger.info(f"作業 [{record.job_id}] 透過 Python Runner 函數執行。")
                runner_fn(record.sandbox, record.config)
                record.exit_code = 0
            elif solver_cmd:
                with self._lock:
                    if record.status == JobStatusEnum.ABORTED:
                        return
                logger.info(f"作業 [{record.job_id}] 啟動子進程: {' '.join(solver_cmd)}")
                with open(stdout_log_path, "wb") as out_f, open(stderr_log_path, "wb") as err_f:
                    with self._lock:
                        if record.status == JobStatusEnum.ABORTED:
                            return
                        proc = subprocess.Popen(
                            solver_cmd,
                            cwd=str(workspace),
                            stdout=out_f,
                            stderr=err_f,
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
                        )
                        record.process = proc
                        if summary:
                            summary.execution.pid = proc.pid
                    if summary:
                        record.sandbox.save_summary(summary)

                    proc.wait()
                    record.exit_code = proc.returncode
            else:
                logger.info(f"作業 [{record.job_id}] 以監控模式運行。")
                while True:
                    with self._lock:
                        if record.status != JobStatusEnum.RUNNING:
                            break
                    time.sleep(0.5)

            record.end_time = time.time()

            # 若未被 abort，判定成功或失敗
            with self._lock:
                if record.status == JobStatusEnum.ABORTED:
                    return
                next_status = JobStatusEnum.SOLVED if record.exit_code == 0 else JobStatusEnum.FAILED

            final_summary = record.sandbox.get_summary()
            if final_summary:
                with self._lock:
                    if record.status == JobStatusEnum.ABORTED:
                        return
                    final_summary.status = next_status
                    final_summary.execution.finished_at = datetime.now(timezone.utc).isoformat()
                    final_summary.execution.duration_seconds = round(
                        record.end_time - record.start_time, 2
                    )
                    final_summary.execution.exit_code = record.exit_code
                    if next_status == JobStatusEnum.SOLVED:
                        final_summary.verdict = VerdictEnum.PASS
                    else:
                        final_summary.verdict = VerdictEnum.FAIL
                        final_summary.failure_reasons.append(
                            f"求解進程異常退出 (Exit code: {record.exit_code})"
                        )
                # 確保磁碟 summary.json 原子寫入完畢後，再將隊列記憶體狀態更新為 SOLVED / FAILED
                record.sandbox.save_summary(final_summary)

            with self._lock:
                if record.status != JobStatusEnum.ABORTED:
                    record.status = next_status

        except Exception as e:
            with self._lock:
                if record.status == JobStatusEnum.ABORTED:
                    return
                logger.error(f"作業 [{record.job_id}] 運行崩潰: {e}", exc_info=True)
                record.status = JobStatusEnum.FAILED
                record.error_messages.append(str(e))
            final_summary = record.sandbox.get_summary()
            if final_summary:
                final_summary.status = JobStatusEnum.FAILED
                final_summary.verdict = VerdictEnum.FAIL
                final_summary.failure_reasons.append(f"執行拋出異常: {str(e)}")
                record.sandbox.save_summary(final_summary)

        finally:
            self.watchdog.unregister_job(record.job_id)

    def _handle_watchdog_abort(self, job_id: str, verdict: BreakerVerdict) -> None:
        """處理 Watchdog 早期發散熔斷回呼。"""
        logger.warning(f"Watchdog 觸發熔斷作業: {job_id}, 原因: {verdict.reason}")
        self.abort_simulation_job(
            job_id=job_id,
            reason=f"早期物理發散熔斷 [{verdict.rule_id}]: {verdict.reason}",
        )

    def _terminate_process_tree(self, proc: Optional[subprocess.Popen]) -> None:
        """優雅終止進程樹。"""
        if not proc or proc.poll() is not None:
            return

        try:
            parent = psutil.Process(proc.pid)
            children = parent.children(recursive=True)

            for child in children:
                try:
                    child.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            parent.terminate()

            _, alive = psutil.wait_procs(children + [parent], timeout=2.0)

            for p in alive:
                try:
                    p.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        except Exception as e:
            logger.warning(f"終止進程樹失敗: {e}，改用 proc.kill()")
            try:
                proc.kill()
            except Exception:
                pass

    @staticmethod
    def _read_tail_lines(file_path: Path, lines: int = 100) -> List[str]:
        """安全從檔案末尾讀取指定行數。"""
        if not file_path.exists():
            return []

        try:
            all_lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
            return all_lines[-lines:]
        except Exception:
            return []
