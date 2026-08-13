"""ANSYS system configuration.

Detection is non-fatal: if no ANSYS installation is found, a degraded config
(available=False) is returned instead of raising. This keeps the MCP server and
non-ANSYS tools (e.g. documentation search) usable on machines without ANSYS.
"""

import os
import winreg
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict
from dotenv import load_dotenv

# Load project-root .env
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# Default version guess used when nothing else is available.
_DEFAULT_VERSION = "251"
# Sentinel root used in degraded mode so derived exe paths stay Path objects
# (their .exists() will simply be False).
_MISSING_ROOT = Path(r"C:\__ansys_not_found__")


@dataclass
class AnsysConfig:
    version: str
    root_path: Path
    workbench_exe: Path
    mechanical_exe: Path
    fluent_exe: Path
    cfx_solve_exe: Path
    cfx_pre_exe: Path
    mapdl_exe: Path
    lsdyna_exe: Path
    available: bool = True


def _find_ansys_registry() -> Dict[str, str]:
    """Scan the Windows registry for installed ANSYS versions."""
    versions: Dict[str, str] = {}
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\ANSYS, Inc.\ANSYS")
        for i in range(100):
            try:
                ver = winreg.EnumKey(key, i)
                sub_key = winreg.OpenKey(key, ver)
                install_dir, _ = winreg.QueryValueEx(sub_key, "InstallDir")
                versions[ver] = install_dir
            except EnvironmentError:
                break
    except EnvironmentError:
        pass
    return versions


def _child_version_dir(parent: Path, version: str) -> Optional[Path]:
    """Return parent\\v<version> if it exists as a directory, else None."""
    candidate = parent / f"v{version}"
    if candidate.is_dir():
        return candidate
    return None


def _newest_version_dir(parent: Path) -> Optional[Path]:
    """Return the newest vNNN child directory under a parent, or None."""
    ver_dirs = sorted(
        [d for d in parent.iterdir() if d.is_dir() and d.name.startswith("v") and d.name[1:].isdigit()],
        key=lambda d: int(d.name[1:]),
        reverse=True,
    )
    return ver_dirs[0] if ver_dirs else None


def _resolve_root() -> tuple[Optional[Path], str]:
    """Resolve the ANSYS root path and version. Returns (root or None, version).

    Resolution priority:
    1. ANSYS_VERSION selector combined with ANSYS_ROOT (single source of truth).
    2. ANSYS_ROOT pointing directly at a vNNN dir, or its newest vNNN child.
    3. Registry detection (newest installed version).
    4. Standard-location fallback guess.
    """
    ansys_root = os.environ.get("ANSYS_ROOT")
    selected_version = os.environ.get("ANSYS_VERSION", "").strip()

    # --- Priority 1: explicit ANSYS_VERSION selector ---
    if selected_version:
        # 1a. ANSYS_ROOT is a parent containing v<version>.
        if ansys_root and Path(ansys_root).exists():
            root_path = Path(ansys_root)
            name = root_path.name
            # ANSYS_ROOT already points at the matching vNNN dir.
            if name == f"v{selected_version}":
                return root_path, selected_version
            child = _child_version_dir(root_path, selected_version)
            if child:
                return child, selected_version
        # 1b. Try the selected version via registry.
        registry_versions = _find_ansys_registry()
        if selected_version in registry_versions:
            return Path(registry_versions[selected_version]), selected_version
        # 1c. Standard-location guesses for the selected version.
        for base in (ansys_root, r"C:\Program Files\ANSYS Inc", r"D:\ANSYS Inc"):
            if not base:
                continue
            guess = Path(base) / f"v{selected_version}"
            if guess.exists():
                return guess, selected_version
        # Selected version could not be located; fall through to auto-detect but
        # keep the requested version string so callers can see the intent.

    version = selected_version or _DEFAULT_VERSION

    if ansys_root and Path(ansys_root).exists():
        root_path = Path(ansys_root)
        name = root_path.name
        if name.startswith("v") and name[1:].isdigit():
            return root_path, name[1:]
        # ANSYS_ROOT points at a parent (e.g. D:\ANSYS Inc); pick newest vNNN child.
        newest = _newest_version_dir(root_path)
        if newest:
            return newest, newest.name[1:]
        return root_path, version

    # Fall back to registry detection.
    registry_versions = _find_ansys_registry()
    if registry_versions:
        version = max(registry_versions.keys())
        return Path(registry_versions[version]), version

    # Last resort: guess a standard install location.
    fallback = Path(rf"C:\Program Files\ANSYS Inc\v{version}")
    if fallback.exists():
        return fallback, version

    return None, version


def _derive(root_path: Path, version: str, available: bool) -> AnsysConfig:
    """Derive per-module exe paths from a root path (relative to standard layout)."""
    return AnsysConfig(
        version=version,
        root_path=root_path,
        workbench_exe=root_path / "Framework" / "bin" / "Win64" / "RunWB2.exe",
        mechanical_exe=root_path / "aisol" / "bin" / "winx64" / "AnsysWBU.exe",
        fluent_exe=root_path / "fluent" / "ntbin" / "win64" / "fluent.exe",
        cfx_solve_exe=root_path / "CFX" / "bin" / "cfx5solve.exe",
        cfx_pre_exe=root_path / "CFX" / "bin" / "cfx5pre.exe",
        mapdl_exe=root_path / "ansys" / "bin" / "winx64" / "ANSYS.exe",
        lsdyna_exe=root_path / "ansys" / "bin" / "winx64" / "lsdyna.exe",
        available=available,
    )


def get_config() -> AnsysConfig:
    """Get ANSYS system config, deriving per-module paths.

    Never raises: returns a degraded config (available=False) when no ANSYS
    installation can be located.
    """
    root_path, version = _resolve_root()

    if not root_path or not root_path.exists():
        # Degraded, non-fatal config. Exe paths are still Path objects whose
        # .exists() will be False, so callers using str(config.*_exe) are safe.
        return _derive(_MISSING_ROOT, version, available=False)

    # Expose AWP_ROOT<version> for dependent PyAnsys packages.
    os.environ["AWP_ROOT" + version] = str(root_path)
    return _derive(root_path, version, available=True)


config = get_config()
