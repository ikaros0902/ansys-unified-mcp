"""ANSYS Unified MCP 2.0 - Sentinel 守護服務單例管理器 (Sentinel Daemon).

管理 SentinelQueue 與 WatchdogDaemon 之全域單例生命週期，
提供平滑啟動、優雅退出與跨模組共享調用。
"""

from __future__ import annotations

import logging
import threading
from typing import Optional

from ansys_unified_mcp.core.sentinel.queue import SentinelQueue

logger = logging.getLogger("ansys-unified-mcp.sentinel.daemon")

_global_queue_instance: Optional[SentinelQueue] = None
_instance_lock = threading.Lock()


def get_sentinel_queue() -> SentinelQueue:
    """獲取 SentinelQueue 全域單例實例。"""
    global _global_queue_instance
    with _instance_lock:
        if _global_queue_instance is None:
            logger.info("初始化 SentinelQueue 全域單例...")
            _global_queue_instance = SentinelQueue()
        return _global_queue_instance


def shutdown_sentinel() -> None:
    """關閉 Sentinel 全域守護服務。"""
    global _global_queue_instance
    with _instance_lock:
        if _global_queue_instance is not None:
            logger.info("關閉 Sentinel 全域守護服務...")
            _global_queue_instance.watchdog.stop()
            _global_queue_instance = None
