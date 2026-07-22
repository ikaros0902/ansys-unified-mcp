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
import ansys_unified_mcp.tools.workbench
import ansys_unified_mcp.tools.workbench_bridge
import ansys_unified_mcp.tools.mechanical
import ansys_unified_mcp.tools.sim_tools
import ansys_unified_mcp.tools.optislang
import ansys_unified_mcp.tools.connection_doctor

# Import the auto connection manager (it runs its initialization upon import if needed)
from ansys_unified_mcp.connection_manager import connection_manager

def main():
    logger.info("Starting Unified ANSYS MCP Server v2.0...")
    
    # 嘗試預先探測正在運作的 ANSYS 模組
    fluent_port = connection_manager.attach_to_fluent()
    if fluent_port:
        logger.info(f"Auto-detected Fluent on port {fluent_port}")
        
    mech_port = connection_manager.scan_for_mechanical_grpc()
    if mech_port:
        logger.info(f"Auto-detected Mechanical on port {mech_port}")

    sc_port = connection_manager.scan_for_spaceclaim_grpc()
    if sc_port:
        logger.info(f"Auto-detected SpaceClaim on port {sc_port}")
        
    wb_running = connection_manager.attach_to_workbench()
    if wb_running:
        logger.info("Auto-detected Workbench background process")

    # Run with stdio transport to ensure no standard output corruption
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
