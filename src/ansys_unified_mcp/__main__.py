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
# 可選值:
# - 'all' (預設全套規範工具，適配 Antigravity 原生 Lazy MCP 索引)
# - 'core_cae' (僅預載主力實機 CAE 模組，非主力/基準模組可透過 ans_call_domain_tool 按需載入)
# - 'core' (極簡核心與 Meta-Router 工具，適配 Kiro CLI / Claude Desktop 零延遲連線)
# - 單一領域: 'geometry', 'mechanical', 'fluent', 'workbench' 等
profile = os.environ.get("ANSYS_MCP_PROFILE", "all").strip().lower()
logger.info(f"Dynamic Tool Routing active. Profile: '{profile}'")

# 核心通用診斷、文件、非同步守護與高階意圖工況工具（一律載入）
import ansys_unified_mcp.tools.connection_tools
import ansys_unified_mcp.tools.docs_tools
import ansys_unified_mcp.tools.apikb_tools
import ansys_unified_mcp.tools.sentinel_tools
import ansys_unified_mcp.tools.intent_tools
import ansys_unified_mcp.tools.session_manager_tools
import ansys_unified_mcp.tools.meta_router_tools
import ansys_unified_mcp.tools.sound_tools

if profile in ("all", "full", "core_cae", "workbench", "wb"):
    import ansys_unified_mcp.products.workbench.tools

if profile in ("all", "full", "core_cae", "mechanical", "structural"):
    import ansys_unified_mcp.products.mechanical.tools

if profile in ("all", "full", "core_cae", "mechanical", "structural", "dpf"):
    import ansys_unified_mcp.products.dpf.tools

if profile in ("all", "full", "core_cae", "optislang"):
    import ansys_unified_mcp.products.optislang.tools

if profile in ("all", "full", "core_cae", "fluent", "cfd"):
    import ansys_unified_mcp.products.fluent.tools

if profile in ("all", "full", "core_cae", "geometry", "spaceclaim"):
    import ansys_unified_mcp.products.geometry.tools

if profile in ("all", "full", "core_cae", "dyna", "lsdyna"):
    import ansys_unified_mcp.products.dyna.tools

if profile in ('all', 'full', 'icepak', 'thermal'):
    import ansys_unified_mcp.products.icepak.tools

if profile in ('all', 'full', 'core_cae', 'mapdl', 'apdl'):
    import ansys_unified_mcp.products.mapdl.tools

if profile in ('all', 'full', 'aedt', 'em', 'hfss', 'maxwell'):
    import ansys_unified_mcp.products.aedt.tools

if profile in ('all', 'full', 'optics', 'lumerical', 'zemax', 'speos'):
    import ansys_unified_mcp.products.optics.tools

if profile in ('all', 'full', 'systems', 'coupling', 'twin'):
    import ansys_unified_mcp.products.systems.tools

if profile in ('all', 'full', 'rocky', 'dem'):
    import ansys_unified_mcp.products.rocky.tools

if profile in ('all', 'full', 'granta', 'materials'):
    import ansys_unified_mcp.products.granta.tools

if profile in ('all', 'full', 'sherlock', 'reliability'):
    import ansys_unified_mcp.products.sherlock.tools

if profile in ('all', 'full', 'motorcad', 'motor'):
    import ansys_unified_mcp.products.motorcad.tools

if profile in ('all', 'full', 'aqwa', 'marine'):
    import ansys_unified_mcp.products.aqwa.tools

if profile in ('all', 'full', 'chemkin', 'reaction'):
    import ansys_unified_mcp.products.chemkin.tools

# Import the auto connection manager (it runs its initialization upon import if needed)
from ansys_unified_mcp.bridges.connection_manager import connection_manager


def main():
    from ansys_unified_mcp.core.stdout_guard import install_stdio_stdout_guard

    install_stdio_stdout_guard()
    logger.info("Starting Unified ANSYS MCP Server v2.0...")
    mcp.run(transport='stdio', show_banner=False)


if __name__ == "__main__":
    main()
