"""共用通訊埠探測工具。

從 `bridges/connection_manager.py` 的 `ConnectionManager._is_port_open` 抽出為獨立可重用函式，
供需要「找一個目前空閒的埠」的場景使用（例如 `launch()` 類方法未來若要讓呼叫端指定埠）。

現況澄清（見 docs/reviews/2026-10-02-phase2-3-feasibility-assessment.md 任務 2.3）：
本專案的實際運作模式是「使用者先手動開啟 ANSYS 軟體，MCP Agent 被動掃描偵測」（見根目錄
README.md「自動連線機制」一節），不是「MCP 主動以指定 Port 啟動新 ANSYS 實例」。因此本模組
不提供 CLI `--port`/`--host` 啟動參數（計畫文件原始設想的使用情境在此架構下不成立），僅提供
「尋找空閒埠」這一個函式層級能力，供既有或未來的 `launch()` 方法在需要時呼叫。
"""

from __future__ import annotations

import socket


def is_port_open(port: int, host: str = "127.0.0.1", timeout: float = 0.2) -> bool:
    """測試指定 TCP port 是否已有服務在監聽中。

    與 ConnectionManager._is_port_open 行為一致：任何連線失敗（拒絕、重置、逾時）皆視為未開啟，
    不外溢例外。
    """
    if not isinstance(port, int) or isinstance(port, bool) or not (0 <= port <= 65535):
        return False

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            try:
                s.connect((host, port))
                return True
            except (OSError, OverflowError, TypeError, ValueError):
                return False
    except (OSError, OverflowError, TypeError, ValueError):
        return False


def find_free_port(start_port: int, end_port: int, host: str = "127.0.0.1") -> int | None:
    """在 [start_port, end_port] 範圍內尋找第一個目前無人監聽（即可用）的埠。

    回傳該空閒埠號；範圍內找不到任何空閒埠時回傳 None。

    注意：這是「當前時刻的快照」結果，呼叫端若需要實際綁定該埠啟動服務，
    該埠仍可能在呼叫後、綁定前被其他進程佔用（TOCTOU），需自行處理綁定失敗的重試。
    """
    if start_port > end_port:
        return None
    for port in range(start_port, end_port + 1):
        if not is_port_open(port, host=host):
            return port
    return None
