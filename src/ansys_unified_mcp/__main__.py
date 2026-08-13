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

# Import tools so they are registered with the MCP instance
import ansys_unified_mcp.tools.workbench_bridge
import os

# PyWorkbench 通道尚未驗證，預設不載入。
# 設定 ANSYS_MCP_ENABLE_PYWORKBENCH=1 啟用。
if os.environ.get("ANSYS_MCP_ENABLE_PYWORKBENCH", "").strip() == "1":
    import ansys_unified_mcp.tools.workbench_pyworkbench  # PyWorkbench (official client/server); UNVERIFIED, additive alongside the legacy bridge
    logger.info("PyWorkbench tools enabled (UNVERIFIED).")

import ansys_unified_mcp.tools.mechanical
import ansys_unified_mcp.tools.sim_tools
import ansys_unified_mcp.tools.optislang
import ansys_unified_mcp.tools.connection_doctor
import ansys_unified_mcp.tools.docs_tools

# Import the auto connection manager (it runs its initialization upon import if needed)
from ansys_unified_mcp.connection_manager import connection_manager

def main():
    logger.info("Starting Unified ANSYS MCP Server v2.0...")
    
    # 立即啟動 MCP server，不阻塞於連接偵測
    # 背景連接掃描改為工具內懶加載，避免啟動延遲
    # 
    # 若需保留預掃描邏輯，改為異步背景線程：
    # import threading
    # def bg_scan():
    #     fluent_port = connection_manager.attach_to_fluent()
    #     if fluent_port:
    #         logger.info(f"Auto-detected Fluent on port {fluent_port}")
    #     ... (其他掃描)
    # threading.Thread(target=bg_scan, daemon=True).start()
    
    # Run with stdio transport to ensure no standard output corruption
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
