#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unified ANSYS MCP Server - entry point."""

import sys
import logging
from dotenv import load_dotenv

# Configure logging to go to stderr to avoid corrupting stdout JSON-RPC
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("ansys-unified-mcp")

# Load environment variables
load_dotenv()

# Import the shared FastMCP instance
from ansys_unified_mcp.shared import mcp
import os

# Dynamic Tool Routing: 根據 ANSYS_MCP_PROFILE 決定載入的工具模組
# 可選值: 'geometry' (幾何建模), 'mechanical' (結構分析), 'fluent' (流體), 'workbench' (工作台流程), 'all' (全套工具)
profile = os.environ.get("ANSYS_MCP_PROFILE", "all").strip().lower()
logger.info(f"Dynamic Tool Routing active. Profile: '{profile}'")

# 核心通用診斷、文件、非同步守護與高階意圖工況工具（一律載入）
import ansys_unified_mcp.tools.connection_tools
import ansys_unified_mcp.tools.docs_tools
import ansys_unified_mcp.tools.sentinel_tools
import ansys_unified_mcp.tools.intent_tools

if profile in ("all", "full", "workbench", "wb"):
    import ansys_unified_mcp.products.workbench.tools

if profile in ("all", "full", "mechanical", "structural"):
    import ansys_unified_mcp.products.mechanical.tools

if profile in ("all", "full", "mechanical", "structural", "dpf"):
    import ansys_unified_mcp.products.dpf.tools

if profile in ("all", "full", "optislang"):
    import ansys_unified_mcp.products.optislang.tools

if profile in ("all", "full", "fluent", "cfd"):
    import ansys_unified_mcp.products.fluent.tools

if profile in ("all", "full", "geometry", "spaceclaim"):
    import ansys_unified_mcp.products.geometry.tools

# Import the auto connection manager (it runs its initialization upon import if needed)
from ansys_unified_mcp.bridges.connection_manager import connection_manager

def main():
    logger.info("Starting Unified ANSYS MCP Server v2.0...")
    mcp.run(transport='stdio', show_banner=False)

if __name__ == "__main__":
    main()
