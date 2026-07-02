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

# Import the shared FastMCP instance and register all tools
from src.shared import mcp
import src

def main():
    logger.info("Starting Unified ANSYS MCP Server...")
    # Run with stdio transport to ensure no standard output corruption
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
