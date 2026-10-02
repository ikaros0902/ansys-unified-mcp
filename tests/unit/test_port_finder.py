"""Unit tests for ansys_unified_mcp.connection.port_finder."""

from __future__ import annotations

import socket

from ansys_unified_mcp.connection.port_finder import find_free_port, is_port_open


def test_find_free_port_skips_occupied_port():
    """埠已被占用時，應找到下一個空閒埠（不回傳被占用的那個）。"""
    # 綁定一個暫時的 TCP 伺服器以占用某個埠
    occupied_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        occupied_sock.bind(("127.0.0.1", 0))
        occupied_sock.listen(1)
        occupied_port = occupied_sock.getsockname()[1]

        # 範圍涵蓋被占用的埠與其後一個埠
        found = find_free_port(occupied_port, occupied_port + 50, host="127.0.0.1")

        assert found is not None
        assert found != occupied_port, "不應回傳已被占用的埠"
        assert not is_port_open(found, host="127.0.0.1"), "回傳的埠必須確實空閒"
    finally:
        occupied_sock.close()


def test_find_free_port_returns_none_when_range_exhausted():
    """範圍內所有埠皆被占用（或範圍為空）時，應回傳 None 而非拋出例外。"""
    # start > end 視為空範圍，必定無解
    assert find_free_port(60000, 59999) is None


def test_is_port_open_rejects_invalid_port_values():
    """非法埠值（超出範圍、非整數、布林值）一律視為未開啟，不拋出例外。"""
    assert is_port_open(-1) is False
    assert is_port_open(70000) is False
    assert is_port_open(True) is False  # bool 是 int 子類別，須明確排除
    assert is_port_open("10000") is False  # type: ignore[arg-type]
