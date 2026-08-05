# -*- coding: utf-8 -*-
import runpy

if __name__ == "__main__":
    # 執行實際的 ANSYS MCP 伺服器主程式
    runpy.run_module("ansys_unified_mcp.__main__", run_name="__main__")
