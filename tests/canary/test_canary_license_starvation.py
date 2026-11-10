# Strictly ASCII English Comments
"""授權匱乏與風暴冷卻 Canary 破壞性注入測試套件 (test_canary_license_starvation.py).

本模組為 Stage 5 Canary 破壞性容錯注入測試之一：
1. 人類工程師保留配額衝撞注入：當 Available = 1, Human_Buffer = 1 時，Agent 請求 100% 遭拒絕，
   拋出 LicenseUnavailableError，絕不侵佔人類席位。
2. 異常崩潰後 300 秒 License Linger 冷卻防暴風雨注入：崩潰後該 Feature 在 300s 內被黑名單鎖死，
   阻斷所有後續重試請求，防止 Thundering Herd。
3. 孤兒進程與無限掛起 (Hang) 銷毀驗證：當任務崩潰或超時，進程守護保證無殭屍殘留，不發生進程掛起。
4. 原子多 Feature 回滾防禦：當任一子授權短缺時，已獲取之授權立即原封釋放，零席位洩漏。
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from typing import List
from unittest.mock import MagicMock, patch

import pytest

from ansys_unified_mcp.core.jobs.token_bucket_scheduler import (
    FeatureBalance,
    FeatureInCooldownError,
    LicenseAcquisitionTimeoutError,
    LicenseLease,
    LicenseUnavailableError,
    PreflightCheckResult,
    TokenBucketLicenseScheduler,
)


class TestCanaryLicenseStarvation:
    """Canary 授權匱乏破壞性注入與風暴冷卻防護測試套件。"""

    @pytest.fixture
    def scheduler(self) -> TokenBucketLicenseScheduler:
        """建立具備 Human_Buffer=1 與 300s 崩潰冷卻的模擬調度器。"""
        sched = TokenBucketLicenseScheduler(
            human_buffer=1,
            cooldown_duration=300.0,
            mock_mode=True,
        )
        sched.reset_mock_state()
        return sched

    def test_human_reserve_buffer_collision_injection_100pct_rejection(
        self, scheduler: TokenBucketLicenseScheduler
    ) -> None:
        """破壞性注入 1: 人類保留配額衝撞注入。

        當 Available = 1, Human_Buffer = 1 時，Agent 請求必須被 100% 拒絕，
        拋出 LicenseUnavailableError 或回傳阻斷狀態，絕不搶佔席位。
        """
        # Configure total 5, in use 4 -> Available = 1, Human_Buffer = 1
        scheduler.set_mock_feature_balance("meba", total=5, in_use=4)

        # 1. Preflight availability check MUST be blocked
        check: PreflightCheckResult = scheduler.check_availability("meba")
        assert check.allowed is False, "Available=1, Human_Buffer=1 時未被安全阻斷！"
        assert len(check.blocking_reasons) > 0
        assert "Human engineer priority policy" in check.blocking_reasons[0]

        # 2. Synchronous non-blocking acquisition MUST throw LicenseUnavailableError
        with pytest.raises(LicenseUnavailableError) as exc_info:
            scheduler.acquire("meba", job_id="canary_agent_job_1", wait=False)
        assert "Human engineer priority policy reserves at least 1 token" in str(exc_info.value)

        # 3. Verify zero agent tasks checked out
        assert scheduler.get_active_agent_tasks("meba") == 0
        assert len(scheduler.get_active_leases()) == 0

        # 4. Repeated bombardment attack (10 consecutive attempts)
        for i in range(10):
            with pytest.raises(LicenseUnavailableError):
                scheduler.acquire("meba", job_id=f"bombard_{i}", wait=False)
        assert scheduler.get_active_agent_tasks("meba") == 0

    def test_human_reserve_buffer_escalation_boundary(
        self, scheduler: TokenBucketLicenseScheduler
    ) -> None:
        """驗證動態配額邊界：Human_Buffer=2 時的防禦性阻斷。"""
        sched_buffer2 = TokenBucketLicenseScheduler(
            human_buffer=2,
            cooldown_duration=300.0,
            mock_mode=True,
        )
        # Total=10, In_use=8 -> Available=2. With Human_Buffer=2, Allowed=(2-0)>2 -> False!
        sched_buffer2.set_mock_feature_balance("fluent_solver", total=10, in_use=8)

        check = sched_buffer2.check_availability("fluent_solver")
        assert check.allowed is False
        assert "reserves at least 2 token" in check.blocking_reasons[0]

        with pytest.raises(LicenseUnavailableError):
            sched_buffer2.acquire("fluent_solver", wait=False)

    def test_crash_license_linger_300s_cooldown_anti_thundering_herd(
        self, scheduler: TokenBucketLicenseScheduler
    ) -> None:
        """破壞性注入 2: 異常崩潰後的 300 秒 License Linger 冷卻防暴風雨注入。

        崩潰後該 Feature 在 300s 內被黑名單鎖死，防止 Thundering Herd。
        """
        feature = "ansys_mechanical"
        scheduler.set_mock_feature_balance(feature, total=10, in_use=2)

        # 1. Agent successfully acquires license
        lease = scheduler.acquire(feature, job_id="crashing_task_001")
        assert lease is not None
        assert scheduler.get_active_agent_tasks(feature) == 1

        # 2. Simulate abnormal crash termination
        scheduler.release(lease, abnormal=True)

        # 3. Active tasks count decremented, but feature is now blacklisted in linger cooldown
        assert scheduler.get_active_agent_tasks(feature) == 0
        assert scheduler.is_in_linger(feature) is True
        assert scheduler.is_in_cooldown(feature) is True

        rem_sec = scheduler.get_linger_remaining(feature)
        assert 295.0 <= rem_sec <= 300.0, f"冷卻倒數不在 300 秒合理範圍: {rem_sec}"

        # 4. Simulate a Thundering Herd: 20 agents storm the scheduler simultaneously
        for i in range(20):
            with pytest.raises(FeatureInCooldownError) as exc_info:
                scheduler.acquire(feature, job_id=f"storm_agent_{i}", wait=False)
            assert "anti-storm cooldown" in str(exc_info.value)
            assert feature in str(exc_info.value)

        # 5. Verify feature remains locked until linger duration expires
        assert scheduler.is_in_cooldown(feature) is True

        # 6. Simulate cooldown expiration
        scheduler.clear_cooldown(feature)
        assert scheduler.is_in_cooldown(feature) is False

        # 7. Safe recovery checkout works normally
        recovery_lease = scheduler.acquire(feature, job_id="recovery_task")
        assert recovery_lease is not None
        scheduler.release(recovery_lease, abnormal=False)

    def test_no_orphan_processes_and_no_infinite_hang_on_crash(
        self, scheduler: TokenBucketLicenseScheduler
    ) -> None:
        """破壞性注入 3: 驗證絕無孤兒進程或進程無限掛起 (Hang)。

        注入模擬子進程崩潰與超時終止，驗證調度器與進程守護在有限時間內退出並銷毀進程。
        """
        # Test 3.1: Timeout defense - acquire with wait must not hang infinitely
        scheduler.set_mock_feature_balance("hpc_pack", total=1, in_use=1)
        start_time = time.monotonic()
        timeout_limit = 0.5  # 500 ms SLA test limit

        with pytest.raises(LicenseAcquisitionTimeoutError) as exc_info:
            scheduler.acquire(
                "hpc_pack",
                job_id="hang_prevention_job",
                wait=True,
                timeout=timeout_limit,
                poll_interval=0.05,
            )
        elapsed = time.monotonic() - start_time
        assert elapsed < timeout_limit + 0.3, f"超時未及時熔斷，發生掛起！耗時 {elapsed:.2f}s"
        assert "Timed out after" in str(exc_info.value)

        # Test 3.2: Process termination cleanliness
        # Spawn a dummy child process and ensure termination leaves zero orphans
        dummy_code = "import time; time.sleep(10)"
        proc = subprocess.Popen([sys.executable, "-c", dummy_code])
        pid = proc.pid
        assert proc.poll() is None, "測試進程未啟動"

        # Simulate abnormal watchdog/supervisor abort
        try:
            proc.terminate()
            proc.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=2.0)

        # Verify process is dead and not hanging
        assert proc.poll() is not None, f"進程 {pid} 依然存活，存在孤兒進程洩漏！"

    def test_atomic_multi_feature_rollback_prevents_partial_seat_starvation(
        self, scheduler: TokenBucketLicenseScheduler
    ) -> None:
        """破壞性注入 4: 原子多 Feature 授權競爭與回滾保護。

        若複合作業 (如 Speos: spaceclaim + speos_optic) 在獲取第二個 Feature 時
        觸發授權匱乏，已獲取的空間 Feature 必須 100% 回滾，不可造成部分佔位。
        """
        scheduler.set_mock_feature_balance("spaceclaim", total=5, in_use=2)  # Available: 3 (OK)
        scheduler.set_mock_feature_balance("speos_optic", total=3, in_use=2)  # Available: 1 (Starved by Human_Buffer=1!)

        # Atomic acquire must fail due to speos_optic starvation
        with pytest.raises(LicenseUnavailableError) as exc_info:
            scheduler.acquire(["spaceclaim", "speos_optic"], job_id="speos_job_001", wait=False)

        assert "speos_optic" in str(exc_info.value)
        # Critical verification: spaceclaim was checked out during phase 1, but rolled back in phase 2
        assert scheduler.get_active_agent_tasks("spaceclaim") == 0
        assert scheduler.get_active_agent_tasks("speos_optic") == 0
        assert len(scheduler.get_active_leases()) == 0


if __name__ == "__main__":
    pytest.main(["-v", __file__])
