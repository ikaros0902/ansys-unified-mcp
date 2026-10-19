# -*- coding: utf-8 -*-
# [!IMPORTANT] 此檔案為向後相容過渡入口，請勿刪除。
# 新部署請推薦使用模組入口 `python -m ansys_unified_mcp` 或 CLI `ansys-unified-mcp`。
import os
import sys
import warnings
from pathlib import Path

warnings.warn(
    "Direct execution of mcp_server.py is deprecated and will be removed in a future release. "
    "Please run as a module: `python -m ansys_unified_mcp` or use the installed CLI `ansys-unified-mcp`.",
    DeprecationWarning,
    stacklevel=2,
)

# 自動將專案 src 目錄加入 sys.path，保證無論以何種方式啟動均能載入 ansys_unified_mcp
src_dir = Path(__file__).resolve().parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import runpy

if __name__ == "__main__":
    # 執行實際的 ANSYS MCP 伺服器主程式
    runpy.run_module("ansys_unified_mcp.__main__", run_name="__main__")
