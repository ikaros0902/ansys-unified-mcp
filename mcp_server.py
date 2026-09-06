# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path

# 自動將專案 src 目錄加入 sys.path，保證無論以何種方式啟動均能載入 ansys_unified_mcp
src_dir = Path(__file__).resolve().parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import runpy

if __name__ == "__main__":
    # 執行實際的 ANSYS MCP 伺服器主程式
    runpy.run_module("ansys_unified_mcp.__main__", run_name="__main__")
