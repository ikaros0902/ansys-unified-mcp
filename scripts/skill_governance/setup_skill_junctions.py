#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""舊技能連結命令的相容入口，實際工作由 setup_skill_links.py 執行。"""

from __future__ import annotations

import sys


def main() -> int:
    """保留舊的 --verify-only 參數名稱，再轉交給共用連結工具。"""
    sys.argv[1:] = ["--verify" if arg == "--verify-only" else arg for arg in sys.argv[1:]]
    if __package__:
        from .setup_skill_links import main as setup_links
    else:
        from setup_skill_links import main as setup_links
    return setup_links()


if __name__ == "__main__":
    raise SystemExit(main())
