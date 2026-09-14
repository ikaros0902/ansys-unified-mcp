# ANSYS Unified MCP Documentation Index

Welcome to the ANSYS Unified MCP Server documentation and asset index.

## Presentations & Architecture Proposals

- [ANSYS MCP 五大領域全面評估與優化計畫書](ANSYS_MCP_EVALUATION_AND_OPTIMIZATION_PLAN.md): 深度對標 PyAnsys 官方 Tutorial 與各大教學網站之優化里程碑計畫書。
- [ANSYS Unified MCP 架構與規格評估白皮書](ANSYS_UNIFIED_MCP_ARCHITECTURE_AND_SPECIFICATION_REPORT.md): 涵蓋結構、幾何、熱傳/Icepak、PyPrimeMesh 與電子封裝五大領域架構評估。
- [其他 Session 完整盤點與全流程標準化優化實施計畫](ANSYS_MCP_SESSION_OPTIMIZATION_PLAN.md): 衝擊分析管線 Session 05~08 補齊、端到端全閉環與全庫硬編碼路徑解耦實施計畫。
- [ANSYS MCP 完整交付成果與里程碑總結](ANSYS_MCP_DELIVERY_WALKTHROUGH.md): 專案與全域設定庫雙向同步與工程交付完整紀錄。
- [Agentic AI Development Proposal Presentation](presentations/slides_detailed.md) (`docs/presentations/slides_detailed.md`): Detailed slide-by-slide inspection and narrative proposal covering CAE automation pain points, MCP assistant engineer workflows, and POC roadmaps.

## Examples & Tutorials

- [Shock Analysis (35G LS-DYNA Pipeline)](../examples/shock_analysis/README.md): Automated 35G 6-direction half-sine shock wave generation, material matching, contact/joint setup, mesh controls, and input deck export.
- [Geometry Cleanup (SpaceClaim & PyAnsys Geometry)](../examples/geometry_cleanup/README.md): Automated defeaturing, screw fastener deletion, and zero-thickness/sliver body removal.

## Core Architectural Modules

- `src/ansys_unified_mcp/connection_manager.py`: Dynamic gRPC port discovery and instance detection.
- `src/ansys_unified_mcp/jobs/`: Simulation sandbox management and artifact lifecycles.
- `src/ansys_unified_mcp/gatekeeper/`: Pre-flight physical checks and safety validation.
- `src/ansys_unified_mcp/core/sentinel/`: Real-time async solver watchdog and divergence circuit breaker.
