# Changelog

All notable changes to the **ANSYS Unified MCP Server** project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.0.0] - 2026-11-10

### 🚀 Added
- **Multi-Version ANSYS Detection & Dynamic Switching**:
  - `discover_installed_versions()` in `config.py` scans 5 sources (environment variables `AWP_ROOT*`, registry, install parents, standard disk locations) across v202 to v261+.
  - `set_active_version(version)` function and MCP tool `ans_set_active_version(version)` to dynamically switch active ANSYS releases at runtime without restarting the MCP server.
  - `ans_list_installed_versions()` MCP tool to list all detected releases and component executables on the host.
- **Cross-Process Shared Registry**:
  - `resolve_shared_registry_dir()` in `core/paths.py` unifying IPC queue to `%LOCALAPPDATA%\ansys-unified-mcp\queue\registry`, solving the registration disconnect when Mechanical/Workbench is launched from the Windows Start menu.
- **Resident Core Diagnostics**:
  - Registered `check_ansys_installation`, `ans_list_installed_versions`, and `ans_set_active_version` as common tools in `visibility.py`, keeping them accessible across all domain profiles.
- **BDD & Canary Test Guardrails**:
  - Added Rule M01, M02, and M03 to `docs/testing/BUSINESS_RULES.md`.
  - Added automated test suite `tests/unit/test_multi_version_and_readiness.py` covering multi-version switching, ASD-STE100 instruction constraints, and clean environment rules.
- **One-Click Setup Profile Parameter**:
  - Added `-InstallProfile standard/all/minimal` and `-AnsysVersion` parameters to `scripts/maintenance/setup.ps1`.
  - Added automatic `.env` creation, ACT extension deployment, and end-of-setup Doctor self-test.
  - Added portable client config template `mcp_config.example.json`.

### ⚡ Changed
- **ASD-STE100 Server Instructions**:
  - Rewrote FastMCP `INSTRUCTIONS` in `src/ansys_unified_mcp/shared.py` according to ASD-STE100 strict rules (active voice, sentences <= 20 words, zero semicolons, explicit modality).
- **PyAnsys Launcher Version Binding**:
  - Updated `MechanicalController.launch()` and `FluentController.launch()` to strictly bind to the active version's executable, preventing PyAnsys from defaulting to the highest installed release when multiple versions are present.
- **Python Compatibility**:
  - Relaxed Python requirement in `pyproject.toml` from `>=3.12` to `>=3.10` to align with official PyAnsys support (3.10 ~ 3.13) and deployment documentation.
- **ISO 24495-1 Documentation Overhaul**:
  - Completely restructured `README.md`, `DEPLOYMENT_SOP.md`, `MCP_TOOL_SCOPING_GUIDE.md`, and `.env.example` using ISO 24495-1 plain language principles (conclusion first, action-oriented instructions, updated tool counts).

### 🔒 Security & Privacy
- **Local Path Sanitization**:
  - Removed all hardcoded absolute local paths (`F:/Ming_python/...`) across 38 tracked files in `docs/api_inventory/`, `docs/knowledge_dictionary/`, and skill documentation.
- **ACT Extension Compatibility**:
  - Normalized `WorkbenchMCP.xml` version attribute to `version="1" minorversion="0"` for cross-release compatibility.
