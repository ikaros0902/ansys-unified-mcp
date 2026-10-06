# -*- coding: utf-8 -*-
"""sim_impl._run_geom_long（長時間 geometry 工作的執行緒化、逾時與進度）單元測試。不需 SpaceClaim。"""
import asyncio
import time

import pytest

from ansys_unified_mcp.products.geometry import call_dispatch as S


def test_progress_is_forwarded_and_result_returned():
    msgs = []

    def job(progress):
        progress("階段一")
        progress("階段二")
        return "完成"

    out = asyncio.run(S._run_geom_long(job, timeout_s=10, notify=msgs.append))
    assert out.startswith("完成")
    assert [m.split("] ", 1)[1] for m in msgs] == ["階段一", "階段二"]


def test_timeout_raises_at_next_stage_boundary():
    cleaned = []

    def job(progress):
        progress("開始")
        time.sleep(0.3)
        try:
            progress("下一階段")
        except TimeoutError:
            cleaned.append(True)  # 模擬既有例外流程清除暫存幾何
            raise
        return "不應到達"

    with pytest.raises(TimeoutError, match="下一階段"):
        asyncio.run(S._run_geom_long(job, timeout_s=0.1))
    assert cleaned == [True]
    assert not S._GEOM_LONG_LOCK.locked()


def test_hard_timeout_returns_early_and_rejects_concurrent_jobs(monkeypatch):
    monkeypatch.setattr(S, "_GEOM_LONG_GRACE_S", 0.1)

    def stuck(progress):
        progress("布林運算")
        time.sleep(0.6)  # 模擬卡在單一 SpaceClaim 呼叫
        progress("之後")

    async def scenario():
        first = await S._run_geom_long(stuck, timeout_s=0.1)
        second = await S._run_geom_long(lambda p: "x", timeout_s=5)
        await asyncio.sleep(0.8)  # 背景工作於下一階段邊界中止並釋放鎖
        third = await S._run_geom_long(lambda p: "ok", timeout_s=5)
        return first, second, third

    first, second, third = asyncio.run(scenario())
    assert "逾時" in first
    assert "另一個長時間" in second
    assert third.startswith("ok")
