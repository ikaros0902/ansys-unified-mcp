# -*- coding: utf-8 -*-
"""Unit tests for TokenBucketLicenseScheduler and InteractiveDesktopGuard."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Dict
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
from ansys_unified_mcp.core.jobs.interactive_desktop_guard import (
    InteractiveDesktopGuard,
    SessionZeroExecutionError,
)


# =============================================================================
# Token Bucket License Scheduler Tests
# =============================================================================

class TestTokenBucketLicenseScheduler:
    """Test suite for pre-flight feature-level token bucket license scheduler."""

    @pytest.fixture
    def mock_scheduler(self) -> TokenBucketLicenseScheduler:
        """Create a scheduler in mock mode with human_buffer=1."""
        scheduler = TokenBucketLicenseScheduler(
            human_buffer=1,
            cooldown_duration=300.0,
            mock_mode=True,
        )
        scheduler.reset_mock_state()
        return scheduler

    def test_lmutil_output_parser_standard(self) -> None:
        """Verify regex parsing of standard FlexNet lmutil lmstat output."""
        sample_output = """
        lmutil - Copyright (c) 1989-2023 Flexera Software LLC. All Rights Reserved.
        Flexible License Manager status on Mon 10/26/2026 12:00

        Users of spaceclaim:  (Total of 5 licenses issued;  Total of 2 licenses in use)

          "spaceclaim" v2024.0, vendor: ansyslmd, expiry: 31-dec-2026
          floating license
            user1 WORKSTATION (v2024.0) (licserver/1055 101), start Mon 10/26 10:00
            user2 WORKSTATION (v2024.0) (licserver/1055 102), start Mon 10/26 11:30
        """
        bal = TokenBucketLicenseScheduler._parse_lmutil_output("spaceclaim", sample_output)
        assert bal is not None
        assert bal.feature == "spaceclaim"
        assert bal.total == 5
        assert bal.in_use == 2
        assert bal.available == 3

    def test_lmutil_output_parser_generic_fallback(self) -> None:
        """Verify fallback parsing when format differs slightly."""
        sample_output = "Status report: 10 licenses issued and 4 licenses in use for feature test_feat."
        bal = TokenBucketLicenseScheduler._parse_lmutil_output("test_feat", sample_output)
        assert bal is not None
        assert bal.total == 10
        assert bal.in_use == 4
        assert bal.available == 6

    def test_human_reserve_buffer_single_token_remaining_blocked(
        self, mock_scheduler: TokenBucketLicenseScheduler
    ) -> None:
        """Verify rule: Allowed = (Available - Active_Agent) > Human_Buffer.

        If company has only 1 license available and Human_Buffer=1,
        (1 - 0) = 1 is NOT > 1, so the task is suspended / blocked to protect humans.
        """
        mock_scheduler.set_mock_feature_balance("spaceclaim", total=5, in_use=4)
        # Available = 1, Active Agent = 0

        check = mock_scheduler.check_availability("spaceclaim")
        assert check.allowed is False
        assert len(check.blocking_reasons) > 0
        assert "Human engineer priority policy reserves at least 1 token" in check.blocking_reasons[0]

        # Acquire without wait should raise LicenseUnavailableError
        with pytest.raises(LicenseUnavailableError) as exc_info:
            mock_scheduler.acquire("spaceclaim", wait=False)
        assert "Human engineer priority policy" in str(exc_info.value)

    def test_human_reserve_buffer_two_tokens_allows_one_agent_then_blocks_second(
        self, mock_scheduler: TokenBucketLicenseScheduler
    ) -> None:
        """Verify that when 2 tokens are available, first agent succeeds and second is blocked."""
        mock_scheduler.set_mock_feature_balance("spaceclaim", total=5, in_use=3)
        # Available = 2, Active Agent = 0 -> (2 - 0) > 1 -> Allowed!

        lease1 = mock_scheduler.acquire("spaceclaim", job_id="job_001")
        assert lease1 is not None
        assert mock_scheduler.get_active_agent_tasks("spaceclaim") == 1

        # Now Available = 2, Active Agent = 1 -> (2 - 1) = 1 is NOT > 1 -> Next blocked!
        check2 = mock_scheduler.check_availability("spaceclaim")
        assert check2.allowed is False

        with pytest.raises(LicenseUnavailableError):
            mock_scheduler.acquire("spaceclaim", wait=False)

        # Release first lease -> Active Agent returns to 0 -> Second agent can now acquire
        mock_scheduler.release(lease1)
        assert mock_scheduler.get_active_agent_tasks("spaceclaim") == 0

        lease2 = mock_scheduler.acquire("spaceclaim", job_id="job_002")
        assert lease2 is not None
        mock_scheduler.release(lease2)

    def test_atomic_multi_feature_checkout_speos_success(
        self, mock_scheduler: TokenBucketLicenseScheduler
    ) -> None:
        """Verify atomic multi-feature checkout for Speos (spaceclaim + speos_optic)."""
        mock_scheduler.set_mock_feature_balance("spaceclaim", total=5, in_use=2)  # Avail: 3
        mock_scheduler.set_mock_feature_balance("speos_optic", total=3, in_use=1)  # Avail: 2
        mock_scheduler.set_mock_sentinel_status("127.0.0.1", 1947, True)

        lease = mock_scheduler.acquire(mock_scheduler.SPEOS_FEATURES, job_id="speos_job")
        assert lease is not None
        assert mock_scheduler.get_active_agent_tasks("spaceclaim") == 1
        assert mock_scheduler.get_active_agent_tasks("speos_optic") == 1

        mock_scheduler.release(lease)
        assert mock_scheduler.get_active_agent_tasks("spaceclaim") == 0
        assert mock_scheduler.get_active_agent_tasks("speos_optic") == 0

    def test_atomic_multi_feature_checkout_rollback_when_one_feature_fails(
        self, mock_scheduler: TokenBucketLicenseScheduler
    ) -> None:
        """Verify all-or-nothing two-phase rollback: if Rocky prepost is OK but GPU token is short."""
        mock_scheduler.set_mock_feature_balance("rocky_prepost", total=4, in_use=1)  # Avail: 3 (OK)
        mock_scheduler.set_mock_feature_balance("gpu_token", total=2, in_use=1)      # Avail: 1 (Blocked by buffer!)

        with pytest.raises(LicenseUnavailableError) as exc_info:
            mock_scheduler.acquire(mock_scheduler.ROCKY_FEATURES, job_id="rocky_job", wait=False)

        assert "gpu_token" in str(exc_info.value)
        # Crucial check: rocky_prepost MUST NOT be checked out; active tasks remain 0
        assert mock_scheduler.get_active_agent_tasks("rocky_prepost") == 0
        assert mock_scheduler.get_active_agent_tasks("gpu_token") == 0
        assert len(mock_scheduler.get_active_leases()) == 0

    def test_sentinel_ldk_hasp_port_1947_probe_failure_blocks_optical(
        self, mock_scheduler: TokenBucketLicenseScheduler
    ) -> None:
        """Verify optical module (speos_optic) fails if Sentinel Port 1947 is unreachable."""
        mock_scheduler.set_mock_feature_balance("spaceclaim", total=5, in_use=1)
        mock_scheduler.set_mock_feature_balance("speos_optic", total=5, in_use=1)
        # Simulate Sentinel Port 1947 down
        mock_scheduler.set_mock_sentinel_status("127.0.0.1", 1947, False)

        check = mock_scheduler.check_availability("speos_optic")
        assert check.allowed is False
        assert any("Sentinel LDK HASP Port 1947 unreachable" in r for r in check.blocking_reasons)

        with pytest.raises(LicenseUnavailableError) as exc_info:
            mock_scheduler.acquire("speos_optic", wait=False)
        assert "Port 1947 unreachable" in str(exc_info.value)

    def test_license_linger_anti_storm_cooldown_on_abnormal_termination(
        self, mock_scheduler: TokenBucketLicenseScheduler
    ) -> None:
        """Verify abnormal termination triggers 300s cooldown blacklist preventing storm."""
        mock_scheduler.set_mock_feature_balance("ansys_mech", total=10, in_use=2)

        lease = mock_scheduler.acquire("ansys_mech", job_id="crash_job")
        # Abnormally terminate
        mock_scheduler.release(lease, abnormal=True)

        assert mock_scheduler.is_in_cooldown("ansys_mech") is True
        rem = mock_scheduler.get_cooldown_remaining("ansys_mech")
        assert 295.0 <= rem <= 300.0

        # Immediate re-checkout should fail with FeatureInCooldownError
        with pytest.raises(FeatureInCooldownError) as exc_info:
            mock_scheduler.acquire("ansys_mech", wait=False)
        assert "anti-storm cooldown" in str(exc_info.value)

        # Clear cooldown -> should work again
        mock_scheduler.clear_cooldown("ansys_mech")
        assert mock_scheduler.is_in_cooldown("ansys_mech") is False
        lease2 = mock_scheduler.acquire("ansys_mech", job_id="retry_job")
        mock_scheduler.release(lease2, abnormal=False)

    def test_lease_context_manager_abnormal_exception_handling(
        self, mock_scheduler: TokenBucketLicenseScheduler
    ) -> None:
        """Verify lease_context automatically marks abnormal on unhandled exceptions."""
        mock_scheduler.set_mock_feature_balance("spaceclaim", total=5, in_use=1)

        with pytest.raises(RuntimeError):
            with mock_scheduler.lease_context("spaceclaim", job_id="context_fail"):
                assert mock_scheduler.get_active_agent_tasks("spaceclaim") == 1
                raise RuntimeError("Simulation core dumped!")

        # Tokens released
        assert mock_scheduler.get_active_agent_tasks("spaceclaim") == 0
        # Cooldown activated
        assert mock_scheduler.is_in_cooldown("spaceclaim") is True

    def test_acquire_wait_timeout(
        self, mock_scheduler: TokenBucketLicenseScheduler
    ) -> None:
        """Verify acquire with wait=True raises LicenseAcquisitionTimeoutError when time runs out."""
        mock_scheduler.set_mock_feature_balance("sparse_token", total=1, in_use=1)

        start = time.time()
        with pytest.raises(LicenseAcquisitionTimeoutError):
            mock_scheduler.acquire("sparse_token", wait=True, timeout=0.3, poll_interval=0.1)
        elapsed = time.time() - start
        assert elapsed >= 0.25


# =============================================================================
# Interactive Desktop Guard Tests
# =============================================================================

class TestInteractiveDesktopGuard:
    """Test suite for Windows Interactive Desktop Guard and Session 0 isolation."""

    @pytest.fixture
    def guard(self) -> InteractiveDesktopGuard:
        """Create standard guard instance."""
        return InteractiveDesktopGuard()

    def test_binary_classification(self, guard: InteractiveDesktopGuard) -> None:
        """Verify identification of GUI-dependent binaries."""
        assert guard.is_gui_binary(r"C:\Program Files\AnsysEM\v242\Win64\ansysedt.exe") is True
        assert guard.is_gui_binary("RunWB2.exe") is True
        assert guard.is_gui_binary("OpticStudio.exe") is True
        assert guard.is_gui_binary("SpaceClaim.exe") is True
        assert guard.is_gui_binary("mechanical.exe") is True

        # Non-GUI binaries should return False
        assert guard.is_gui_binary("python.exe") is False
        assert guard.is_gui_binary("ansys-solver.exe") is False
        assert guard.is_gui_binary("lmutil.exe") is False

    def test_session_zero_interception_for_gui_binary(self, guard: InteractiveDesktopGuard) -> None:
        """Verify GUI binaries are strictly blocked when executed in Session 0."""
        # Test ansysedt.exe in Session 0
        with pytest.raises(SessionZeroExecutionError) as exc_info:
            guard.validate_session("ansysedt.exe", session_id=0)

        err = exc_info.value
        assert err.session_id == 0
        assert "ansysedt.exe" in err.binary_name
        assert "Windows Session 0 is reserved strictly for non-interactive system services" in str(err)
        assert "Remediation & Configuration Steps" in str(err)
        assert "Run only when user is logged on" in str(err)

    def test_session_nonzero_allows_gui_binary(self, guard: InteractiveDesktopGuard) -> None:
        """Verify GUI binaries are permitted in interactive user logon sessions (Session 1+)."""
        # Session 1 (Standard interactive desktop)
        guard.validate_session("ansysedt.exe", session_id=1)
        guard.validate_session("RunWB2.exe", session_id=2)

    def test_non_gui_binary_allowed_in_session_zero(self, guard: InteractiveDesktopGuard) -> None:
        """Verify non-GUI CLI binaries are not blocked in Session 0."""
        guard.validate_session("python.exe", session_id=0)
        guard.validate_session("lmutil.exe", session_id=0)

    def test_headless_flags_injection_ansysedt(self, guard: InteractiveDesktopGuard) -> None:
        """Verify automatic injection of -ng -BatchSolve -Distributed for ansysedt.exe."""
        raw_cmd = ["C:\\Ansys\\ansysedt.exe", "-script", "solve.py"]
        injected = guard.inject_headless_flags(raw_cmd)

        assert injected[0] == "C:\\Ansys\\ansysedt.exe"
        assert "-ng" in injected
        assert "-BatchSolve" in injected
        assert "-Distributed" in injected
        assert injected[-2:] == ["-script", "solve.py"]

    def test_headless_flags_injection_does_not_duplicate(self, guard: InteractiveDesktopGuard) -> None:
        """Verify headless flags are not duplicated if already present in command."""
        raw_cmd = ["ansysedt.exe", "-ng", "-run", "task.py"]
        injected = guard.inject_headless_flags(raw_cmd)

        # Count occurrences of -ng
        assert sum(1 for x in injected if x.lower() == "-ng") == 1
        assert "-BatchSolve" in injected
        assert "-Distributed" in injected

    def test_mandatory_environment_variable_injection(self, guard: InteractiveDesktopGuard) -> None:
        """Verify injection of ANSYSEM_DONT_SHOW_MESSAGEBOX and ANS_DISABLE_NODELOCK_CHECK."""
        base_env = {"USER": "testuser", "PATH": "C:\\Windows"}
        prepared_env = guard.inject_environment(base_env)

        assert prepared_env["ANSYSEM_DONT_SHOW_MESSAGEBOX"] == "1"
        assert prepared_env["ANS_DISABLE_NODELOCK_CHECK"] == "1"
        assert prepared_env["USER"] == "testuser"

    def test_prepare_command_pipeline(self, guard: InteractiveDesktopGuard) -> None:
        """Verify end-to-end prepare_command performs session check and injects flags and env."""
        cmd, env = guard.prepare_command(
            command="ansysedt.exe -script test.py",
            check_session=True,
            session_id=1,  # Interactive session
        )
        assert cmd[0] == "ansysedt.exe"
        assert "-ng" in cmd
        assert "-BatchSolve" in cmd
        assert "-Distributed" in cmd
        assert env["ANSYSEM_DONT_SHOW_MESSAGEBOX"] == "1"
        assert env["ANS_DISABLE_NODELOCK_CHECK"] == "1"

    def test_prepare_command_blocks_session_zero(self, guard: InteractiveDesktopGuard) -> None:
        """Verify prepare_command raises SessionZeroExecutionError when session_id is 0."""
        with pytest.raises(SessionZeroExecutionError):
            guard.prepare_command(
                command="ansysedt.exe -script test.py",
                check_session=True,
                session_id=0,
            )

    def test_get_current_session_id_env_override(self) -> None:
        """Verify ANSYS_DESKTOP_GUARD_SESSION_ID environment variable override."""
        with patch.dict(os.environ, {"ANSYS_DESKTOP_GUARD_SESSION_ID": "42"}):
            sid = InteractiveDesktopGuard.get_current_session_id()
            assert sid == 42
