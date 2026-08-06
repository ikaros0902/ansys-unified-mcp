"""Unified ANSYS path resolution.

Single source of truth for locating ANSYS executables and the PyMechanical CLI,
merging what was previously duplicated across config.py, bridges/workbench_bridge.py
and tools/connection_doctor.py.

Resolution order for each executable:
1. Explicit environment variable override (e.g. ANSYS_RUNWB2).
2. Standard-layout path derived from the detected ANSYS root (config).
3. AWP_ROOT* environment roots, searched recursively as a fallback.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from ansys_unified_mcp.config import config


def _env_path(*keys: str) -> Optional[Path]:
    """Return the first existing path among the given environment variables."""
    for key in keys:
        value = os.environ.get(key)
        if value and Path(value).exists():
            return Path(value)
    return None


def _search_awp_roots(name: str) -> Optional[Path]:
    """Search AWP_ROOT* roots recursively for an executable by name."""
    for key, value in os.environ.items():
        if not key.upper().startswith("AWP_ROOT"):
            continue
        root = Path(value)
        if not root.exists():
            continue
        try:
            matches = sorted(root.rglob(name), key=lambda p: p.stat().st_mtime, reverse=True)
        except OSError:
            continue
        if matches:
            return matches[0]
    return None


def find_runwb2() -> Optional[Path]:
    """Locate RunWB2.exe (Workbench launcher)."""
    explicit = _env_path("ANSYS_RUNWB2", "ANSYS_WB_EXE", "RUNWB2_EXE")
    if explicit:
        return explicit
    if config.available and config.workbench_exe.exists():
        return config.workbench_exe
    return _search_awp_roots("RunWB2.exe") or _search_awp_roots("runwb2.exe")


def find_mechanical_exe() -> Optional[Path]:
    """Locate AnsysWBU.exe (Mechanical editor executable)."""
    explicit = _env_path("ANSYS_MECHANICAL")
    if explicit:
        return explicit
    if config.available and config.mechanical_exe.exists():
        return config.mechanical_exe
    return _search_awp_roots("AnsysWBU.exe")


def find_fluent_exe() -> Optional[Path]:
    explicit = _env_path("ANSYS_FLUENT")
    if explicit:
        return explicit
    if config.available and config.fluent_exe.exists():
        return config.fluent_exe
    return _search_awp_roots("fluent.exe")


def find_mapdl_exe() -> Optional[Path]:
    explicit = _env_path("ANSYS_MAPDL")
    if explicit:
        return explicit
    if config.available and config.mapdl_exe.exists():
        return config.mapdl_exe
    return _search_awp_roots("ANSYS.exe")


def find_cfx_solve_exe() -> Optional[Path]:
    explicit = _env_path("ANSYS_CFX_SOLVE")
    if explicit:
        return explicit
    if config.available and config.cfx_solve_exe.exists():
        return config.cfx_solve_exe
    return _search_awp_roots("cfx5solve.exe")


def find_mechanical_cli() -> Optional[Path]:
    """Locate the ansys-mechanical CLI installed in this MCP virtual environment."""
    explicit = _env_path("ANSYS_MECHANICAL_CLI")
    if explicit:
        return explicit
    # Repo root = parents[3] of this file: core/ -> ansys_unified_mcp/ -> src/ -> repo
    repo_root = Path(__file__).resolve().parents[3]
    cli = repo_root / ".venv" / "Scripts" / "ansys-mechanical.exe"
    if cli.exists():
        return cli
    return None


def default_revision() -> int:
    """Return the ANSYS revision number (e.g. 261) from the detected version."""
    try:
        return int(config.version)
    except (TypeError, ValueError):
        return 261


def environment_summary() -> dict:
    """Structured summary of resolved ANSYS paths for diagnostics."""
    def s(p: Optional[Path]) -> Optional[str]:
        return str(p) if p else None

    runwb2 = find_runwb2()
    mech_exe = find_mechanical_exe()
    mech_cli = find_mechanical_cli()
    fluent = find_fluent_exe()
    return {
        "ansys_available": config.available,
        "ansys_root": s(config.root_path) if config.available else None,
        "version": config.version,
        "runwb2": s(runwb2),
        "runwb2_available": runwb2 is not None,
        "mechanical_exe": s(mech_exe),
        "mechanical_exe_available": mech_exe is not None,
        "mechanical_cli": s(mech_cli),
        "mechanical_cli_available": mech_cli is not None,
        "fluent_exe": s(fluent),
        "fluent_exe_available": fluent is not None,
    }
