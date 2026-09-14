# ANSYS Unified MCP Documentation Index

Welcome to the ANSYS Unified MCP Server documentation and asset index.

## Presentations & Architecture Proposals

- [Agentic AI Development Proposal Presentation](presentations/slides_detailed.md) (`docs/presentations/slides_detailed.md`): Detailed slide-by-slide inspection and narrative proposal covering CAE automation pain points, MCP assistant engineer workflows, and POC roadmaps.

## Examples & Tutorials

- [Shock Analysis (35G LS-DYNA Pipeline)](../examples/shock_analysis/README.md): Automated 35G 6-direction half-sine shock wave generation, material matching, contact/joint setup, mesh controls, and input deck export.
- [Geometry Cleanup (SpaceClaim & PyAnsys Geometry)](../examples/geometry_cleanup/README.md): Automated defeaturing, screw fastener deletion, and zero-thickness/sliver body removal.

## Core Architectural Modules

- `src/ansys_unified_mcp/connection_manager.py`: Dynamic gRPC port discovery and instance detection.
- `src/ansys_unified_mcp/jobs/`: Simulation sandbox management and artifact lifecycles.
- `src/ansys_unified_mcp/gatekeeper/`: Pre-flight physical checks and safety validation.
- `src/ansys_unified_mcp/core/sentinel/`: Real-time async solver watchdog and divergence circuit breaker.
