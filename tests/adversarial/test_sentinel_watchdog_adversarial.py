# -*- coding: utf-8 -*-
"""對抗性極限壓力測試：Sentinel Watchdog 與 CircuitBreaker 實時發散熔斷攻擊 (test_sentinel_watchdog_adversarial.py).

本測試套件由 Empirical Challenger (Physics Adversarial Specialist) 獨立撰寫，
專注對實時物理守護進程 (Watchdog) 與發散熔斷器 (CircuitBreaker) 實施嚴酷的實時日誌發散攻擊：

1. 沙漏能去抖動容錯 vs 超標立即熔斷攻防：
   - 4.9% 沙漏能長週期波動 (4.80% ~ 4.99% 連續 100 步) 去抖動機制不誤熔斷 (False Positive = 0)
   - 5.1% 沙漏能超標時連續 3 次精準觸發熔斷 (CB-DYNA-003)
   - 沙漏能超標後回落容錯恢復機制 (不發生錯誤累加殘留)
   - 15.1% 沙漏能極度超標單次立即熔斷 (無需等待去抖動次數)
2. 數值崩潰 (NaN / Inf / #IND / #QNAN) 注入攻擊：
   - LS-DYNA 能量出現 NaN / Inf 時即刻熔斷 (CB-DYNA-001)
   - Mechanical solve.out 殘差出現 NaN / Inf 時即刻熔斷 (CB-MECH-001)
   - Fluent fluent.log 殘差出現 NaN / #IND / #QNAN 時即刻熔斷 (CB-CFD-001)
3. 負滑移能 (Negative Sliding Energy) 穿透鎖死攻擊：
   - 滑移能為顯著負值且佔總能 15% (>10%) 時精確熔斷 (CB-DYNA-004)
   - 注入高達 -10^9 J 之極端負滑移能數值攻擊
   - 微小負滑移能 (2% < 10%) 正常容忍不誤熔斷
4. 殘差暴衝與單元畸變攻擊：
   - Mechanical 殘差暴增至 1.5e12 (>1e10) 觸發 CB-MECH-002
   - Mechanical 單元嚴重畸變 (Negative Jacobian) 伴隨未收斂殘差觸發 CB-MECH-003
   - Fluent 殘差單步暴衝至 2.5e8 (>1e8) 觸發 CB-CFD-003
5. 惡意日誌亂碼、行截斷與抗崩潰防禦 (Crash Resilience)：
   - 注入 NULL 位元組 (\x00)、非 ASCII 亂碼、損壞編碼
   - 注入截斷行 (不完整鍵值對、缺少浮點數)
   - 注入超大單行 (50,000 字元長度)
   - 驗證所有求解器解析器與 Watchdog 絕不拋出未捕獲例外，確保系統抗崩潰穩定性
6. WatchdogDaemon 實時端到端熔斷與沙盒狀態聯動：
   - 實時後台監控線程、動態日誌寫入、自動調用 abort_callback
   - 沙盒 summary.json 自動標記 ABORTED、寫入建議處方
"""

from __future__ import annotations

import math
import os
import time
from pathlib import Path
from typing import Any, Dict, List
import pytest

from ansys_unified_mcp.core.sentinel.circuit_breaker import (
    BreakerVerdict,
    CircuitBreaker,
)
from ansys_unified_mcp.core.sentinel.parsers import (
    FluentResidualParser,
    LSDynaGlstatParser,
    MechanicalMAPDLParser,
)
from ansys_unified_mcp.core.sentinel.watchdog import WatchdogDaemon
from ansys_unified_mcp.jobs.manager import JobManager
from ansys_unified_mcp.jobs.models import JobStatusEnum, VerdictEnum


# ==============================================================================
# 1. 沙漏能去抖動容錯 vs 超標熔斷攻防
# ==============================================================================
class TestHourglassDebounceAdversarial:
    """沙漏能 4.9% 波動去抖動 vs 5.1% 超標熔斷對抗測試。"""

    def test_hourglass_fluctuation_4_9_no_false_trip(self) -> None:
        """4.9% 沙漏能長週期波動 (連續 100 步)，驗證去抖動機制絕不誤熔斷。"""
        cb = CircuitBreaker(hourglass_threshold_pct=5.0, debounce_count=3)

        for step in range(100):
            # 讓沙漏比率在 4.80% ~ 4.98% 之間波動
            ratio = 4.80 + (step % 10) * 0.02
            hg_energy = ratio * 10.0  # 總能 1000J
            verdict = cb.evaluate_lsdyna(
                hourglass_energy=hg_energy,
                internal_energy=800.0,
                total_energy=1000.0,
                sliding_energy=5.0,
                added_mass_pct=0.1,
                current_time=step * 0.0001,
            )
            assert not verdict.triggered, f"在步長 {step} (比率 {ratio:.2f}%) 發生誤熔斷！"
            assert verdict.rule_id is None

    def test_hourglass_exceeded_5_1_debounced_trip(self) -> None:
        """5.1% 沙漏能超標 (門檻 5.0%)，在 debounce_count=3 下連續第 3 次精準熔斷。"""
        cb = CircuitBreaker(hourglass_threshold_pct=5.0, debounce_count=3)
        hg_energy = 51.0  # 51J / 1000J = 5.1%

        # 第 1 次超標：容忍期，不熔斷
        v1 = cb.evaluate_lsdyna(hg_energy, 800.0, 1000.0, 0.0, 0.1)
        assert not v1.triggered
        assert cb._hourglass_over_count == 1

        # 第 2 次超標：容忍期，不熔斷
        v2 = cb.evaluate_lsdyna(hg_energy, 800.0, 1000.0, 0.0, 0.1)
        assert not v2.triggered
        assert cb._hourglass_over_count == 2

        # 第 3 次超標：精準觸發熔斷
        v3 = cb.evaluate_lsdyna(hg_energy, 800.0, 1000.0, 0.0, 0.1)
        assert v3.triggered
        assert v3.rule_id == "CB-DYNA-003"
        assert "5.10%" in v3.reason or "5.1%" in v3.reason
        assert "連續 3 次" in v3.reason
        assert "UPGRADE_HOURGLASS_CONTROL" in (v3.action_code or "")

    def test_hourglass_recovery_resets_debounce_count(self) -> None:
        """沙漏能短暫超標後回落，去抖動計數應動態扣減，防累積殘留。"""
        cb = CircuitBreaker(hourglass_threshold_pct=5.0, debounce_count=3)

        # 2 次超標 (5.2%)
        cb.evaluate_lsdyna(52.0, 800.0, 1000.0, 0.0, 0.1)
        cb.evaluate_lsdyna(52.0, 800.0, 1000.0, 0.0, 0.1)
        assert cb._hourglass_over_count == 2

        # 回落至安全值 (4.0%) 連續 2 次
        cb.evaluate_lsdyna(40.0, 800.0, 1000.0, 0.0, 0.1)
        assert cb._hourglass_over_count == 1
        cb.evaluate_lsdyna(40.0, 800.0, 1000.0, 0.0, 0.1)
        assert cb._hourglass_over_count == 0

        # 再次單次超標 (5.2%)：此時計數器應重新從 1 起算，不觸發熔斷
        v_again = cb.evaluate_lsdyna(52.0, 800.0, 1000.0, 0.0, 0.1)
        assert not v_again.triggered
        assert cb._hourglass_over_count == 1

    def test_hourglass_extreme_instant_breaker(self) -> None:
        """沙漏能超過 15% 極度失控時，無需等待去抖動次數，第 1 次立即熔斷。"""
        cb = CircuitBreaker(hourglass_threshold_pct=5.0, debounce_count=5)
        # 160J / 1000J = 16.0% > 15.0%
        v = cb.evaluate_lsdyna(160.0, 800.0, 1000.0, 0.0, 0.1)
        assert v.triggered
        assert v.rule_id == "CB-DYNA-003"


# ==============================================================================
# 2. 數值崩潰 (NaN / Inf) 與負滑移能巨大數值攻擊
# ==============================================================================
class TestNumericalExplosionAndNegativeSlidingAdversarial:
    """NaN/Inf 數值注入與負滑移能穿透攻擊測試。"""

    @pytest.fixture
    def cb(self) -> CircuitBreaker:
        return CircuitBreaker()

    def test_lsdyna_nan_inf_all_fields_attack(self, cb: CircuitBreaker) -> None:
        """LS-DYNA 能量數值出現各類 NaN/Inf 時即刻熔斷 (CB-DYNA-001)。"""
        # 沙漏能為 NaN
        assert cb.evaluate_lsdyna(float("nan"), 800.0, 1000.0).rule_id == "CB-DYNA-001"
        # 內能為 Inf
        assert cb.evaluate_lsdyna(10.0, float("inf"), 1000.0).rule_id == "CB-DYNA-001"
        # 總能為 -Inf
        assert cb.evaluate_lsdyna(10.0, 800.0, float("-inf")).rule_id == "CB-DYNA-001"
        # 標記 has_nan_inf = True
        assert cb.evaluate_lsdyna(10.0, 800.0, 1000.0, has_nan_inf=True).rule_id == "CB-DYNA-001"

    def test_lsdyna_negative_sliding_energy_large_value_attack(self, cb: CircuitBreaker) -> None:
        """負滑移能巨大數值注入攻擊 (CB-DYNA-004)。"""
        # 正常微小負值容忍 (2% 總能) -> 不熔斷
        v_ok = cb.evaluate_lsdyna(10.0, 800.0, 1000.0, sliding_energy=-20.0)
        assert not v_ok.triggered

        # 超標負值 (15% 總能) -> 熔斷
        v_fail = cb.evaluate_lsdyna(10.0, 800.0, 1000.0, sliding_energy=-150.0)
        assert v_fail.triggered
        assert v_fail.rule_id == "CB-DYNA-004"
        assert "滑移能" in v_fail.reason

        # 巨大負值攻擊 (-1.0e9 J) -> 熔斷
        v_huge = cb.evaluate_lsdyna(10.0, 800.0, 1000.0, sliding_energy=-1.0e9)
        assert v_huge.triggered
        assert v_huge.rule_id == "CB-DYNA-004"

    def test_mechanical_residual_nan_and_explosion_attack(self, cb: CircuitBreaker) -> None:
        """Mechanical 力平衡殘差 NaN 與暴衝數值 (1.5e12) 攻擊。"""
        # NaN 殘差
        v_nan = cb.evaluate_mechanical(force_residual=float("nan"), criterion=0.05)
        assert v_nan.triggered
        assert v_nan.rule_id == "CB-MECH-001"

        # 殘差暴衝至 1.5e12 > 1e10 (CB-MECH-002)
        v_exp = cb.evaluate_mechanical(force_residual=1.5e12, criterion=0.05)
        assert v_exp.triggered
        assert v_exp.rule_id == "CB-MECH-002"
        assert "1.50e+12" in v_exp.reason

        # 畸變伴隨殘差發散 (CB-MECH-003)
        v_dist = cb.evaluate_mechanical(force_residual=500.0, criterion=0.05, has_distortion=True)
        assert v_dist.triggered
        assert v_dist.rule_id == "CB-MECH-003"

    def test_fluent_residual_nan_and_spike_attack(self, cb: CircuitBreaker) -> None:
        """Fluent 殘差 NaN、發散標記與暴衝數值 (2.5e8) 攻擊。"""
        # NaN 殘差 (CB-CFD-001)
        v_nan = cb.evaluate_fluent(residuals={"continuity": 0.1}, has_nan_inf=True)
        assert v_nan.triggered
        assert v_nan.rule_id == "CB-CFD-001"

        # 指數發散標記 (CB-CFD-002)
        v_div = cb.evaluate_fluent(residuals={"continuity": 100.0}, is_diverged=True)
        assert v_div.triggered
        assert v_div.rule_id == "CB-CFD-002"

        # 單方程殘差 > 1e8 暴衝 (CB-CFD-003)
        v_spike = cb.evaluate_fluent(residuals={"continuity": 2.5e8, "x_velocity": 0.01})
        assert v_spike.triggered
        assert v_spike.rule_id == "CB-CFD-003"
        assert "2.50e+08" in v_spike.reason


# ==============================================================================
# 3. 日誌解析器抗亂碼、行截斷與惡意字元防禦 (Crash Resilience)
# ==============================================================================
class TestLogParsersCrashResilienceAdversarial:
    """日誌解析器面對亂碼、截斷與損壞內容之抗崩潰測試。"""

    def test_lsdyna_parser_corrupted_log_stream_survives(self) -> None:
        """LS-DYNA 解析器解析包含 NULL 位元組、截斷行、巨大超長行與 NaN 時不崩潰。"""
        parser = LSDynaGlstatParser(target_duration_s=0.005)

        corrupted_stream = (
            "time = 1.00000E-04  dt = 1.00000E-07\n"
            "kinetic energy = 1.00000E+02\n"
            "internal energy = NaN\n"  # 注入 NaN
            "hourglass energy = 5.00000E+00\n"
            "total energy = Inf\n"  # 注入 Inf
            "sliding energy = -2.50000E+02\n"
            "added mass = 1.0E-03 (ratio = 6.50 %)\n"
            # 截斷行
            "time = 2.00000E-04  dt = \n"
            "kinetic energy = \n"
            # 超長行 (50,000 字元)
            + ("X" * 50000) + "\n"
            # 控制字元與亂碼
            + "\x00\x01\x02\xff\xfe random binary junk !@#$%^&*()_+\n"
        )

        res = parser.parse_chunk(corrupted_stream)
        assert res.has_nan_inf is True
        assert res.sliding_energy == -250.0
        assert res.added_mass_pct == 6.50
        assert res.current_time == 1.00000e-4

    def test_mechanical_parser_corrupted_log_stream_survives(self) -> None:
        """MechanicalMAPDLParser 解析包含截斷行、畸變警告與 NaN 殘差時不崩潰。"""
        parser = MechanicalMAPDLParser(target_end_time=1.0)

        corrupted_stream = (
            "INCREMENT 1 SUBSTEP 1 TIME= 0.1000\n"
            "CUMULATIVE ITERATION = 5\n"
            "FORCE CONVERGENCE VALUE = NaN  CRITERION = 0.05\n"  # 注入 NaN
            "Element 99999 has become highly distorted\n"
            # 截斷行
            "INCREMENT 1 SUBSTEP 2 TIME= \n"
            "FORCE CONVERGENCE VALUE = \n"
            # 亂碼與超長行
            + ("M" * 20000) + "\n"
            + "\x00\x00\xff\xfe corrupt bytes\n"
            "FORCE CONVERGENCE VALUE = 1.50000E+12  CRITERION = 0.05\n"
        )

        res = parser.parse_chunk(corrupted_stream)
        assert res.has_nan_inf is True
        assert res.has_distortion is True
        assert res.force_convergence_value == 1.5e12

    def test_fluent_parser_corrupted_log_stream_survives(self) -> None:
        """FluentResidualParser 解析包含 #IND、#QNAN、截斷行時不崩潰。"""
        parser = FluentResidualParser(target_iterations=500)

        corrupted_stream = (
            "iter continuity x-velocity y-velocity energy\n"
            "1    1.0000e+00  1.0000e-01  1.0000e-01  1.0000e-02\n"
            "2    NaN         #IND         #QNAN       1.0000e-02\n"  # 注入 Windows 浮點異常記號
            "reversed flow in 32 faces\n"
            # 截斷行
            "3    \n"
            # 亂碼
            + "\x00\xff\xfe junk line\n"
            "4    2.5000e+08  1.0000e-01  1.0000e-01  1.0000e-02\n"
        )

        res = parser.parse_chunk(corrupted_stream)
        assert res.has_nan_inf is True
        assert res.reversed_flow_faces == 32
        assert res.residuals.get("continuity") == 2.5e8


# ==============================================================================
# 4. WatchdogDaemon 實時端到端熔斷與沙盒狀態聯動
# ==============================================================================
class TestWatchdogLiveAbortAdversarial:
    """WatchdogDaemon 在真實沙盒與串流日誌發散攻擊下的處置閉環。"""

    def test_watchdog_live_abort_under_severe_divergence_attack(self, tmp_path: Path) -> None:
        """在沙盒中串流寫入沙漏超標與負滑移能日誌，驗證 Watchdog 即時熔斷並標記 summary.json。"""
        jobs_dir = tmp_path / "jobs"
        mgr = JobManager(base_jobs_dir=jobs_dir)
        sandbox = mgr.create_job("drop_test", tag="live_attack")

        aborted_records: List[Dict[str, Any]] = []

        def on_abort(jid: str, verdict: BreakerVerdict) -> None:
            aborted_records.append({"job_id": jid, "rule_id": verdict.rule_id, "reason": verdict.reason})

        wd = WatchdogDaemon(poll_interval_seconds=0.05)
        wd.start()

        try:
            wd.register_job(
                job_id=sandbox.job_id,
                sandbox=sandbox,
                workflow_type="lsdyna",
                target_duration=0.005,
                abort_callback=on_abort,
            )

            # 配置熔斷去抖動為 1 次以配合單次實測
            ctx = wd._jobs[sandbox.job_id]
            ctx.circuit_breaker.debounce_count = 1

            # 串流寫入極端日誌至 glstat
            glstat_file = sandbox.workspace_dir / "glstat"
            extreme_log = (
                "time = 1.00000E-04  dt = 1.00000E-07\n"
                "kinetic energy = 5.00000E+02\n"
                "internal energy = 5.00000E+02\n"
                "hourglass energy = 1.00000E+01\n"
                "total energy = 1.00000E+03\n"
                "sliding energy = -4.00000E+02\n"  # 負滑移能 40% > 10%
                "added mass = 0.0000E+00 (ratio = 0.00 %)\n"
                + ("#" * 8000) + "\n"
                + "\x00\xff\xfe corrupt bytes\n"
            )
            glstat_file.write_text(extreme_log, encoding="utf-8", errors="replace")

            # 等待守護線程輪詢檢驗 (0.05s * 6 = 0.3s)
            time.sleep(0.25)

            # 驗證 abort_callback 已被觸發
            assert len(aborted_records) == 1
            assert aborted_records[0]["job_id"] == sandbox.job_id
            assert aborted_records[0]["rule_id"] == "CB-DYNA-004"

            # 驗證沙盒 summary.json 已被寫入 ABORTED
            summary = sandbox.get_summary()
            assert summary is not None
            assert summary.status == JobStatusEnum.ABORTED
            assert summary.execution.circuit_breaker_triggered is True
            assert "CB-DYNA-004" in (summary.execution.circuit_breaker_reason or "")

            # 驗證快照查詢呈現熔斷
            snap = wd.get_snapshot(sandbox.job_id)
            assert snap["monitored"] is True
            assert snap["physical_health"].get("circuit_breaker_triggered") is True

        finally:
            wd.stop()