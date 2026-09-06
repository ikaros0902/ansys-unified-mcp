"""ANSYS Unified MCP 2.0 - Sentinel 系統級非同步排程與守護工具 (Sentinel MCP Tools).

定義並註冊 4 個核心 MCP 系統工具：
- submit_simulation_job: 立即提交作業建立沙盒並非同步送算 (<500ms 返回)
- get_simulation_status: 輪詢作業狀態、進度百分比、時間步、殘差與物理守護健康度
- tail_simulation_log: 串流提取最新日誌尾端行數
- abort_simulation_job: 優雅終止求解進程並記錄原因
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from ansys_unified_mcp.core.sentinel.daemon import get_sentinel_queue

logger = logging.getLogger("ansys-unified-mcp.tools.sentinel")

# 防禦性相容導入 FastMCP
try:
    from ansys_unified_mcp.shared import mcp
except Exception:
    try:
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("ansys-unified-mcp")
    except Exception:
        class _FallbackMCP:
            def tool(self, *args, **kwargs):
                def decorator(fn):
                    return fn
                return decorator
        mcp = _FallbackMCP()


@mcp.tool()
def submit_simulation_job(workflow_type: str, config: dict) -> dict:
    """立即建立作業沙盒並送入非同步執行隊列，500ms 內返回，防止 MCP 客戶端逾時。

    Args:
        workflow_type: 工作流類型 ('drop_test', 'shock_analysis', 'random_vibration',
                                    'thermal_warpage', 'train_surrogate_model',
                                    'workbench_journal', 'mechanical_script')
        config: 工作流配置字典 (包含幾何、材料、載荷、邊界條件等參數)

    Returns:
        {'ok': True, 'job_id': str, 'sandbox_dir': str, 'status': 'QUEUED'}
    """
    logger.info(f"收到 submit_simulation_job 請求: workflow_type={workflow_type}")
    queue = get_sentinel_queue()
    tag = config.get("tag", "default")
    return queue.submit_simulation_job(
        workflow_type=workflow_type,
        config=config,
        tag=tag,
    )


@mcp.tool()
def get_simulation_status(job_id: str) -> dict:
    """獲取作業即時狀態、進度百分比、時間步、殘差與物理守護健康度。

    Args:
        job_id: 模擬作業唯一標識符

    Returns:
        {'ok': True, 'job_id': str, 'status': str, 'progress_pct': float,
         'current_step': str, 'physical_health': dict, 'elapsed_seconds': float}
    """
    queue = get_sentinel_queue()
    return queue.get_simulation_status(job_id=job_id)


@mcp.tool()
def tail_simulation_log(job_id: str, lines: int = 100, log_type: str = "solve_out") -> dict:
    """串流獲取作業求解即時日誌 (solve.out, glstat, matter.out, fluent.log, stdout.log)。

    Args:
        job_id: 模擬作業唯一標識符
        lines: 提取尾端行數 (預設 100)
        log_type: 日誌類型 ('solve_out', 'glstat', 'matter', 'fluent', 'stdout', 'stderr')

    Returns:
        {'ok': True, 'job_id': str, 'log_type': str, 'lines': list[str], 'total_lines': int}
    """
    queue = get_sentinel_queue()
    return queue.tail_simulation_log(job_id=job_id, lines=lines, log_type=log_type)


@mcp.tool()
def abort_simulation_job(job_id: str, reason: str = "user_requested") -> dict:
    """優雅中斷求解器進程，釋放授權，並將作業狀態置為 ABORTED。

    Args:
        job_id: 模擬作業唯一標識符
        reason: 中斷原因 ('user_requested' 或自訂理由)

    Returns:
        {'ok': True, 'job_id': str, 'status': 'ABORTED', 'reason': str}
    """
    logger.info(f"收到 abort_simulation_job 請求: job_id={job_id}, reason={reason}")
    queue = get_sentinel_queue()
    return queue.abort_simulation_job(job_id=job_id, reason=reason)
