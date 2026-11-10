"""Unit tests for declarative security permission gate and enforcement."""

from __future__ import annotations

import os
from pathlib import Path
import pytest

from ansys_unified_mcp.core.permission_gate import (
    AllowedRoot,
    PermissionGate,
    SecurityGatePermissionError,
    enforce_permission,
    permission_gate,
)


@pytest.fixture
def gate() -> PermissionGate:
    """Fixture providing standard PermissionGate instance."""
    return PermissionGate()


# ------------------------------------------------------------------------------
# 1. Manifest Loading & Configuration Tests
# ------------------------------------------------------------------------------

def test_manifest_categories_loaded(gate: PermissionGate) -> None:
    """Verify that all five permission tiers are correctly registered."""
    categories = gate.categories
    expected_categories = [
        "open_source",
        "documented_api",
        "observable_runtime",
        "proprietary_binary",
        "restricted",
    ]
    for cat in expected_categories:
        assert cat in categories, f"Category '{cat}' missing from manifest"
        assert "tier" in categories[cat]
        assert "description" in categories[cat]

    assert categories["open_source"]["tier"] == 1
    assert categories["documented_api"]["tier"] == 2
    assert categories["observable_runtime"]["tier"] == 3
    assert categories["proprietary_binary"]["tier"] == 4
    assert categories["restricted"]["tier"] == 5


def test_manifest_blocked_extensions(gate: PermissionGate) -> None:
    """Verify blocked extensions include licenses, keys, and private symbols."""
    for ext in (".lic", ".key", ".pdb", ".idb", ".pem", ".pfx", ".dmp"):
        assert ext in gate.blocked_extensions


def test_manifest_disallowed_commands(gate: PermissionGate) -> None:
    """Verify reverse engineering and tampering tools are in disallowed list."""
    for cmd in ("ghidra", "ida64", "x64dbg", "windbg", "strings", "lmutil"):
        assert cmd in gate.disallowed_commands


# ------------------------------------------------------------------------------
# 2. Path Validation & Boundary Checking Tests
# ------------------------------------------------------------------------------

def test_check_path_valid_project_file(gate: PermissionGate) -> None:
    """Valid path inside project root must pass successfully."""
    project_file = gate.project_root / "pyproject.toml"
    resolved = gate.check_path(project_file, access_type="read")
    assert resolved == project_file.resolve()


def test_check_path_relative_project_file(gate: PermissionGate) -> None:
    """Relative path inside project root must resolve and pass."""
    resolved = gate.check_path("pyproject.toml", access_type="read")
    assert resolved.name == "pyproject.toml"
    assert resolved.is_file()


def test_check_path_blocked_extension(gate: PermissionGate) -> None:
    """Files with blocked extensions (.lic, .key, .pdb) must raise PermissionError."""
    with pytest.raises(PermissionError) as exc_info:
        gate.check_path("license.lic", access_type="read")
    assert "extension '.lic' is prohibited" in str(exc_info.value)
    assert "[Category: restricted]" in str(exc_info.value)

    with pytest.raises(PermissionError) as exc_info:
        gate.check_path("private.key", access_type="read")
    assert "extension '.key' is prohibited" in str(exc_info.value)

    with pytest.raises(PermissionError) as exc_info:
        gate.check_path("symbols.pdb", access_type="read")
    assert "extension '.pdb' is prohibited" in str(exc_info.value)


def test_check_path_restricted_pattern(gate: PermissionGate) -> None:
    """Files matching restricted patterns must be rejected."""
    with pytest.raises(PermissionError) as exc_info:
        gate.check_path("debug/licdebug.log", access_type="read")
    assert "matches restricted security pattern" in str(exc_info.value)

    with pytest.raises(PermissionError) as exc_info:
        gate.check_path(".ssh/id_rsa", access_type="read")
    assert "credential" in str(exc_info.value).lower() or "restricted" in str(exc_info.value).lower()


def test_check_path_traversal_escape(gate: PermissionGate) -> None:
    """Path traversal attempting to escape project root must be blocked."""
    with pytest.raises(PermissionError) as exc_info:
        gate.check_path("../../../../../Windows/System32/cmd.exe", access_type="read")
    assert "outside authorized directory boundaries" in str(exc_info.value) or "restricted" in str(exc_info.value)


def test_check_path_write_to_read_only_root() -> None:
    """Writing to read-only roots (like ANSYS install dir) must raise PermissionError."""
    custom_gate = PermissionGate()
    # Configure a mock read-only root
    read_only_dir = custom_gate.project_root / "src" / "ansys_unified_mcp" / "resources" / "manifests"
    custom_gate.allowed_roots = [
        AllowedRoot(
            id="read_only_manifests",
            path=read_only_dir.resolve(),
            description="Read-only test directory",
            allow_read=True,
            allow_write=False,
        )
    ]

    target = read_only_dir / "test_write.txt"
    # Reading should succeed
    resolved = custom_gate.check_path(target, access_type="read")
    assert resolved == target.resolve()

    # Writing must fail with PermissionError
    with pytest.raises(PermissionError) as exc_info:
        custom_gate.check_path(target, access_type="write")
    assert "read-only boundary" in str(exc_info.value)


# ------------------------------------------------------------------------------
# 3. Binary Inspection Checking Tests
# ------------------------------------------------------------------------------

def test_check_binary_inspection_commercial_solvers(gate: PermissionGate) -> None:
    """Inspection of proprietary solver binaries must raise PermissionError."""
    solvers = [
        "ansys.exe",
        "fluent.exe",
        "RunWB2.exe",
        "SpaceClaim.exe",
        "lsdyna.exe",
        "cfx5.exe",
        "optislang.exe",
    ]
    for solver in solvers:
        with pytest.raises(PermissionError) as exc_info:
            gate.check_binary_inspection(solver)
        assert "[Category: proprietary_binary]" in str(exc_info.value)
        assert "commercial binary" in str(exc_info.value).lower()


def test_check_binary_inspection_symbol_pdb(gate: PermissionGate) -> None:
    """Inspection of private debug symbol file must raise PermissionError."""
    with pytest.raises(PermissionError) as exc_info:
        gate.check_binary_inspection("solver.pdb")
    assert "[Category: proprietary_binary]" in str(exc_info.value)
    assert "symbol" in str(exc_info.value).lower()


def test_check_binary_inspection_open_source_allowed(gate: PermissionGate) -> None:
    """Inspection of open-source scripts or safe targets must return True."""
    assert gate.check_binary_inspection("test_script.py") is True
    assert gate.check_binary_inspection("user_model.step") is True


# ------------------------------------------------------------------------------
# 4. Command Interception Tests
# ------------------------------------------------------------------------------

def test_check_command_disallowed_executables(gate: PermissionGate) -> None:
    """Disallowed reverse engineering utilities must be blocked."""
    prohibited_cmds = [
        "ghidra",
        "ghidra.bat -project /tmp",
        "ida64.exe -A solver.exe",
        "x64dbg.exe",
        "r2 -d ansys.exe",
        "windbg -p 1234",
    ]
    for cmd in prohibited_cmds:
        with pytest.raises(PermissionError) as exc_info:
            gate.check_command(cmd)
        assert "[Category: restricted]" in str(exc_info.value)


def test_check_command_strings_targeting_proprietary_binary(gate: PermissionGate) -> None:
    """Using strings on proprietary solver binaries must be blocked."""
    with pytest.raises(PermissionError) as exc_info:
        gate.check_command("strings ansys.exe")
    assert "[Category: proprietary_binary]" in str(exc_info.value)


def test_check_command_license_tampering(gate: PermissionGate) -> None:
    """License management and tampering commands must be blocked."""
    with pytest.raises(PermissionError) as exc_info:
        gate.check_command("lmutil lmstat -a")
    assert "[Category: restricted]" in str(exc_info.value)


def test_check_command_safe_execution(gate: PermissionGate) -> None:
    """Normal build and test commands must pass without raising."""
    gate.check_command("python -m pytest tests/unit")
    gate.check_command("uv run pytest")
    gate.check_command("git status")


# ------------------------------------------------------------------------------
# 5. Permission Enforcement Decorator Tests
# ------------------------------------------------------------------------------

def test_decorator_restricted_category_blocked() -> None:
    """Functions decorated with 'restricted' must unconditionally raise PermissionError."""
    @enforce_permission("restricted")
    def crack_drm() -> str:
        return "unreachable"

    with pytest.raises(PermissionError) as exc_info:
        crack_drm()
    assert "[Category: restricted]" in str(exc_info.value)


def test_decorator_path_validation() -> None:
    """Decorator must validate path arguments for security violations."""
    @enforce_permission("open_source")
    def process_file(path: str) -> str:
        return f"Processed {path}"

    # Valid project file
    result = process_file("pyproject.toml")
    assert result == "Processed pyproject.toml"

    # Blocked extension
    with pytest.raises(PermissionError):
        process_file("secret.lic")


def test_decorator_command_validation() -> None:
    """Decorator must validate command arguments for security violations."""
    @enforce_permission("observable_runtime")
    def run_worker(command: str) -> str:
        return f"Ran {command}"

    # Valid command
    result = run_worker("python run.py")
    assert result == "Ran python run.py"

    # Blocked command
    with pytest.raises(PermissionError):
        run_worker("ghidra run.exe")


def test_decorator_proprietary_binary_validation() -> None:
    """Decorator under proprietary_binary category must check binary targets."""
    @enforce_permission("proprietary_binary")
    def analyze_binary(binary_path: str) -> str:
        return f"Inspected {binary_path}"

    with pytest.raises(PermissionError):
        analyze_binary("ansys.exe")

    # Safe file
    assert analyze_binary("myscript.py") == "Inspected myscript.py"


@pytest.mark.anyio
async def test_decorator_async_function() -> None:
    """Decorator must support asynchronous functions."""
    @enforce_permission("observable_runtime")
    async def async_worker(path: str) -> str:
        return f"Async {path}"

    result = await async_worker("pyproject.toml")
    assert result == "Async pyproject.toml"

    with pytest.raises(PermissionError):
        await async_worker("secret.key")
