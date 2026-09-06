# -*- coding: utf-8 -*-
"""對抗性壓力測試套件 (Adversarial Stress & Security Test Suite)

由 E2E & Stress Challenger 獨立撰寫，專注於挖掘系統級漏洞與邊界失效模式：
1. 沙盒安全性與高併發干擾：
   - 10 與 20 併發相同 workflow_type 與 tag 之目錄碰撞防護檢驗
   - 深入多維道路徑穿越 (Path Traversal) 滲透攻擊測試：
     * JobManager.create_job 標識符穿越
     * JobSandbox.write_workspace_file 前綴繞過注入
     * JobSandbox.protect_read_only 目標檔名逃逸覆寫
     * SentinelQueue.tail_simulation_log 外部任意檔案讀取洩漏
2. 非同步狀態機與 Abort 韌性：
   - 在 QUEUED 排隊延遲狀態下主動 Abort 之後續執行阻斷與狀態一致性檢驗
   - 在 RUNNING 狀態下中止深層子進程樹，驗證 OS 進程表中 0 孤兒進程殘留
3. 報告 100% 離線自包含性：
   - 模擬純內網/涉密斷網環境 (Air-gapped Socket Interception)
   - 檢驗 overview.html 零外部 CDN/HTTP 資源引用，驗證 SVG 向量圖形與 Base64 雲圖內嵌
"""

from __future__ import annotations

import base64
import os
import re
import socket
import stat
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import psutil
import pytest

from ansys_unified_mcp.core.sentinel.queue import ActiveJobRecord, SentinelQueue
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
from ansys_unified_mcp.reporting.generator import ReportGenerator


# ==============================================================================
# 第一組：沙盒安全性與高併發干擾對抗測試
# ==============================================================================
class TestSandboxConcurrencyAndSecurityAdversarial:
    """沙盒併發碰撞與檔案路徑安全對抗測試。"""

    def test_concurrent_job_creation_collision_resistance(self, tmp_path: Path) -> None:
        """檢驗同時併發 10 個以上相同 workflow_type 與 tag 時，時間戳與短 UUID 之防碰撞能力。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        concurrency_count = 10
        barrier = threading.Barrier(concurrency_count)

        def concurrent_create(idx: int) -> JobSandbox:
            barrier.wait()  # 同步瞬間觸發
            return manager.create_job(workflow_type="drop_test", tag="heavy_load")

        with ThreadPoolExecutor(max_workers=concurrency_count) as pool:
            sandboxes = list(pool.map(concurrent_create, range(concurrency_count)))

        job_ids = [s.job_id for s in sandboxes]

        # 1. 斷言所有生成的 job_id 100% 唯一，無任何 ID 碰撞
        assert len(set(job_ids)) == concurrency_count, (
            f"檢測到 job_id 重複碰撞！生成數: {concurrency_count}, 唯一數: {len(set(job_ids))}"
        )

        # 2. 斷言實體磁碟目錄彼此隔離獨立
        disk_dirs = [p for p in (tmp_path / "jobs").iterdir() if p.is_dir()]
        assert len(disk_dirs) == concurrency_count, "磁碟實體目錄發生覆蓋碰撞"

        # 3. 斷言所有沙盒 summary.json 均可獨立讀取且內容合法
        for sb in sandboxes:
            summary = sb.get_summary()
            assert summary is not None, f"沙盒 [{sb.job_id}] 的 summary.json 未正常生成"
            assert summary.job_id == sb.job_id
            assert summary.workflow_type == "drop_test"

        # 4. 斷言 JobManager.list_jobs 正確枚舉所有沙盒
        listed = manager.list_jobs()
        assert len(listed) == concurrency_count

    def test_path_traversal_in_job_manager_identifier(self, tmp_path: Path) -> None:
        """檢驗 JobManager 針對 workflow_type、tag 與 job_id 之路徑穿越防護。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")

        # 1. 拒絕 tag 穿越
        with pytest.raises(ValueError, match="path traversal detected"):
            manager.create_job("drop_test", tag="../../escaped_tag")

        with pytest.raises(ValueError, match="path traversal detected"):
            manager.create_job("drop_test", tag="..\\..\\windows_escaped")

        # 2. 拒絕 workflow_type 穿越
        with pytest.raises(ValueError, match="path traversal detected"):
            manager.create_job("../../../evil_workflow", tag="normal")

        # 3. 拒絕 get_job 與 delete_job 穿越
        with pytest.raises(ValueError, match="path traversal detected"):
            manager.get_job("../../../target_job")

        with pytest.raises(ValueError, match="path traversal detected"):
            manager.delete_job("..\\..\\target_job")

    def test_path_traversal_write_workspace_file_prefix_bypass(self, tmp_path: Path) -> None:
        """【漏洞檢驗】檢驗 write_workspace_file 是否存在字串前綴繞過漏洞。

        若使用 str(target).startswith(str(self.workspace_dir))，
        注入 '../workspace_evil/hack.txt' 將因前綴比對為真而成功逃逸至 workspace 同級目錄！
        預期安全行為：必須拋出 ValueError 阻斷逃逸。
        """
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        sandbox = manager.create_job("modal", tag="security_probe")

        # 嘗試利用同前綴目錄名進行路徑逃逸
        evil_rel_path = "../workspace_evil/malicious_payload.py"
        with pytest.raises(ValueError, match="超出 workspace 目錄範疇"):
            sandbox.write_workspace_file(evil_rel_path, "import os; os.system('calc')")

    def test_path_traversal_protect_read_only_destination(self, tmp_path: Path) -> None:
        """【漏洞檢驗】檢驗 protect_read_only 是否檢查 target_name 路徑穿越。

        若直接 destination = self.inputs_dir / target_name，傳入 '../../escaped.txt'
        將任意寫入沙盒外部檔案並將其鎖死為唯讀！
        預期安全行為：必須阻斷目標檔名中之路徑穿越並拋出異常。
        """
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        sandbox = manager.create_job("thermal", tag="protect_probe")

        # 建立合法來源檔案
        source_file = tmp_path / "valid_model.pmdb"
        source_file.write_bytes(b"CAD_MODEL_DATA_BYTES")

        # 惡意目標名稱嘗試逃逸至沙盒外部
        malicious_target = "../../escaped_system_file.bin"

        with pytest.raises((ValueError, PermissionError), match=r"(path traversal|超出|Invalid)"):
            dest = sandbox.protect_read_only(source_file, target_name=malicious_target)
            # 若未拋出異常，進一步核驗是否逃逸出 inputs 目錄
            assert dest.resolve().is_relative_to(sandbox.inputs_dir), (
                f"安全失效：protect_read_only 成功將檔案寫入 inputs 外: {dest.resolve()}"
            )

    def test_path_traversal_tail_simulation_log(self, tmp_path: Path) -> None:
        """【漏洞檢驗】檢驗 tail_simulation_log 是否存在任意檔案讀取漏洞。

        若 log_type 直接作為檔名拼接到 workspace，傳入 '../../../secret.txt'
        將洩漏沙盒外之機敏檔案！
        預期安全行為：禁止傳入包含路徑穿越字元之 log_type。
        """
        secret_file = tmp_path / "top_secret.txt"
        secret_file.write_text("CONFIDENTIAL_SYSTEM_PASSWORD", encoding="utf-8")

        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        watchdog = WatchdogDaemon(poll_interval_seconds=0.1)
        queue = SentinelQueue(job_manager=manager, watchdog=watchdog)

        try:
            sandbox = manager.create_job("fluent", tag="log_probe")
            # 嘗試向上三層讀取 secret_file
            res = queue.tail_simulation_log(sandbox.job_id, log_type="../../../top_secret.txt")
            leaked_lines = res.get("lines", [])
            assert "CONFIDENTIAL_SYSTEM_PASSWORD" not in str(leaked_lines), (
                "安全失效：tail_simulation_log 透過路徑穿越成功讀取沙盒外機敏檔案！"
            )
        finally:
            watchdog.stop()


# ==============================================================================
# 第二組：非同步狀態機與 Abort 韌性及進程清理對抗測試
# ==============================================================================
class TestAsyncStateMachineAndAbortResilience:
    """狀態機競態條件與進程樹清理測試。"""

    def test_abort_queued_job_race_condition(self, tmp_path: Path) -> None:
        """【狀態機缺陷檢驗】檢驗在 QUEUED 狀態下 Abort 作業，背景執行緒是否阻斷執行。

        場景：使用者提交長作業後立即取消（或排隊中取消）。
        若 _run_job_async 未檢查 record.status == ABORTED，將無條件覆蓋為 RUNNING，
        啟動子進程並最終標記為 SOLVED，造成被取消的作業仍然被完整執行！
        預期安全行為：
        1. 背景執行器發現已 ABORTED 時應立即返回，不得啟動子進程。
        2. 狀態必須維持 ABORTED，不得被覆蓋為 RUNNING 或 SOLVED。
        3. 磁碟 summary.json 必須保持 ABORTED。
        """
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        watchdog = WatchdogDaemon(poll_interval_seconds=0.05)
        queue = SentinelQueue(job_manager=manager, watchdog=watchdog)

        # 模擬排隊延遲：建立一個尚在 QUEUED 狀態的作業記錄
        sandbox = manager.create_job("drop_test", tag="queued_abort")
        record = ActiveJobRecord(
            job_id=sandbox.job_id,
            sandbox=sandbox,
            workflow_type="drop_test",
            config={},
        )
        record.status = JobStatusEnum.QUEUED
        with queue._lock:
            queue._jobs[sandbox.job_id] = record

        try:
            # 1. 使用者在 QUEUED 狀態執行 abort
            abort_res = queue.abort_simulation_job(sandbox.job_id, reason="使用者於排隊中主動取消")
            assert abort_res["ok"]
            assert abort_res["status"] == "ABORTED"

            # 2. 模擬背景排程線程隨後啟動 _run_job_async
            marker_file = sandbox.workspace_dir / "executed.marker"
            solver_cmd = [
                "python",
                "-c",
                f"from pathlib import Path; Path(r'{marker_file}').write_text('RAN'); import time; time.sleep(0.5)",
            ]

            # 執行背景迴圈
            queue._run_job_async(record, solver_cmd=solver_cmd, runner_fn=None)

            # 3. 核心斷言：已中斷的作業絕不可執行求解指令！
            assert not marker_file.exists(), "重大缺陷：已在 QUEUED 狀態取消的作業，子進程仍被啟動並執行！"

            # 4. 斷言狀態未被覆蓋為 SOLVED
            assert record.status == JobStatusEnum.ABORTED, (
                f"重大缺陷：已取消作業狀態被背景線程覆蓋為: {record.status}"
            )

            # 5. 斷言磁碟 summary.json 保持 ABORTED
            disk_summary = sandbox.get_summary()
            assert disk_summary is not None
            assert disk_summary.status == JobStatusEnum.ABORTED, (
                f"重大缺陷：磁碟 summary.json 被覆蓋為: {disk_summary.status}"
            )

        finally:
            watchdog.stop()

    def test_abort_running_process_tree_cleanup_no_orphans(self, tmp_path: Path) -> None:
        """檢驗在 RUNNING 狀態下中止深層子進程樹，確保 OS 中 0 孤兒進程殘留。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        watchdog = WatchdogDaemon(poll_interval_seconds=0.05)
        queue = SentinelQueue(job_manager=manager, watchdog=watchdog)

        try:
            # 啟動父進程，並由父進程繁衍一個長睡眠子進程
            solver_cmd = [
                "python",
                "-c",
                "import subprocess, time; p = subprocess.Popen(['python', '-c', 'import time; time.sleep(40)']); time.sleep(40)",
            ]
            resp = queue.submit_simulation_job(
                workflow_type="explicit_dynamics",
                config={},
                tag="orphan_test",
                solver_cmd=solver_cmd,
            )
            assert resp["ok"]
            job_id = resp["job_id"]

            # 等待進程樹在作業系統中繁衍完成
            time.sleep(1.2)

            record = queue._jobs.get(job_id)
            assert record is not None
            assert record.process is not None
            parent_pid = record.process.pid
            assert psutil.pid_exists(parent_pid), "父進程未正常啟動"

            # 檢索子進程樹 PID 列表
            parent_proc = psutil.Process(parent_pid)
            children_pids = [c.pid for c in parent_proc.children(recursive=True)]
            assert len(children_pids) >= 1, "未偵測到繁衍之子進程"

            # 執行優雅終止
            abort_res = queue.abort_simulation_job(job_id, reason="測試進程樹終止清理")
            assert abort_res["ok"]
            assert abort_res["status"] == "ABORTED"

            # 給予進程樹退出緩衝時間
            time.sleep(1.5)

            # 斷言父進程已終止
            assert not psutil.pid_exists(parent_pid), f"父進程 [{parent_pid}] 仍殘留未被終止"

            # 斷言所有子進程（孤兒進程）100% 被徹底終止
            orphans = [pid for pid in children_pids if psutil.pid_exists(pid)]
            # 若有殘留，緊急清理防止污染測試環境
            for pid in orphans:
                try:
                    psutil.Process(pid).kill()
                except Exception:
                    pass

            assert len(orphans) == 0, f"重大缺陷：進程樹清理殘留孤兒進程: {orphans}"

        finally:
            watchdog.stop()


# ==============================================================================
# 第三組：報告 100% 離線自包含性暴力檢驗
# ==============================================================================
class TestReportOfflineSelfContainmentAdversarial:
    """報告零外部 CDN/HTTP 依賴與斷網環境渲染暴力檢驗。"""

    def test_air_gapped_offline_zero_external_resources(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """檢驗在模擬完全涉密斷網環境 (Air-gapped) 下，overview.html 無任何外部依賴且完全自包含。"""
        # 1. 攔截所有 socket 連線，模擬實體斷網環境
        def mock_blocked_connect(*args, **kwargs):
            raise OSError("Air-gapped network: all external connections blocked")

        monkeypatch.setattr(socket.socket, "connect", mock_blocked_connect)

        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        sandbox = manager.create_job("drop_test", tag="airgap_test")

        # 寫入測試雲圖
        dummy_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        (sandbox.images_dir / "von_mises_stress.png").write_bytes(dummy_png)
        (sandbox.images_dir / "total_deformation.png").write_bytes(dummy_png)

        # 準備多樣性圖表數據
        chart_data = {
            "convergence": {
                "iterations": [1, 2, 3, 4, 5],
                "residuals": [1.0, 0.2, 0.05, 0.003, 1e-5],
                "criteria": [1e-4, 1e-4, 1e-4, 1e-4, 1e-4],
            },
            "drop": {
                "time_ms": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
                "acceleration_g": [0.0, 25.0, 85.0, 150.0, 60.0, 10.0, 0.0],
            },
            "psd": {
                "frequencies": [10.0, 50.0, 100.0, 200.0, 500.0, 1000.0],
                "response_g2_hz": [0.001, 0.02, 0.15, 0.08, 0.005, 0.0002],
            },
            "energy": {
                "time_s": [0.0, 0.001, 0.002, 0.003],
                "kinetic_e": [100.0, 70.0, 30.0, 5.0],
                "internal_e": [0.0, 28.0, 65.0, 88.0],
                "hourglass_e": [0.0, 1.2, 2.8, 3.5],
                "total_e": [100.0, 99.2, 97.8, 96.5],
            },
            "mop": {
                "x_grid": [1.0, 2.0, 3.0],
                "y_grid": [10.0, 20.0, 30.0],
                "z_matrix": [[10.0, 20.0, 30.0], [20.0, 40.0, 60.0], [30.0, 60.0, 90.0]],
                "cop_score": 0.92,
            },
        }

        gen = ReportGenerator()
        html_path = gen.build_overview_html(sandbox, chart_data=chart_data, embed_images_base64=True)
        assert html_path.exists(), "overview.html 生成失敗"

        html_text = html_path.read_text(encoding="utf-8")

        # 2. 檢驗完全無外部 URL (除了標準 SVG 命名空間 xmlns="http://www.w3.org/2000/svg")
        all_urls = re.findall(r"https?://[^\s\"'<>]+", html_text)
        external_urls = [u for u in all_urls if u != "http://www.w3.org/2000/svg"]
        assert len(external_urls) == 0, f"重大缺陷：報告包含外部 CDN/HTTP 外鏈資源: {external_urls}"

        # 3. 檢驗無外部 <link rel="stylesheet"> 或 <script src="...">
        assert not re.search(r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']http', html_text, re.I), "包含外部 CSS 外鏈"
        assert not re.search(r'<script[^>]+src=["\']http', html_text, re.I), "包含外部 JS 外鏈"

        # 4. 檢驗雲圖 100% 透過 Base64 Data URI 內嵌
        assert "data:image/png;base64," in html_text, "雲圖未以 Base64 內嵌"
        assert 'von_mises_stress.png' not in html_text or 'data:image/png;base64,' in html_text

        # 5. 檢驗 SVG 向量圖形標籤完整性
        svg_tags = re.findall(r"<svg[\s\S]*?</svg>", html_text)
        assert len(svg_tags) >= 5, f"預期渲染 5 個 SVG 物理曲線，實際渲染: {len(svg_tags)}"
        for svg in svg_tags:
            assert "viewBox=" in svg
            assert "xmlns=" in svg

    def test_charts_robustness_with_scalar_criteria(self, tmp_path: Path) -> None:
        """【健壯性檢驗】當收斂指標 criteria 為純量 float 時，報告生成器不得崩潰。

        使用者傳入 criteria: 1e-4 時，不可引發 TypeError: 'float' object is not iterable。
        """
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        sandbox = manager.create_job("mechanical", tag="scalar_crit_probe")

        chart_data = {
            "convergence": {
                "iterations": [1, 2, 3],
                "residuals": [0.5, 0.05, 0.001],
                "criteria": 1e-4,  # 純量 float
            }
        }

        gen = ReportGenerator()
        # 預期安全行為：支援純量 float 或自動包裝為 list，不拋出 TypeError
        try:
            html_path = gen.build_overview_html(sandbox, chart_data=chart_data)
            assert html_path.exists()
        except TypeError as e:
            pytest.fail(f"健壯性缺陷：傳入純量 criteria 導致崩潰: {e}")
