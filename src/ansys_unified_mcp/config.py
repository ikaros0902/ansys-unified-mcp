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
    spaceclaim_exe: Path
    available: bool = True


def _find_ansys_registry() -> Dict[str, str]:
    """Scan the Windows registry for installed ANSYS versions."""
    versions: Dict[str, str] = {}
    # Check HKLM:\SOFTWARE\ANSYS, Inc.\ANSYS\<ver>
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

    # Check HKLM:\SOFTWARE\ANSYS, Inc.\v<ver>
    try:
        parent_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\ANSYS, Inc.")
        for i in range(100):
            try:
                sub_name = winreg.EnumKey(parent_key, i)
                if sub_name.startswith("v") and sub_name[1:].isdigit():
                    v_key = winreg.OpenKey(parent_key, sub_name)
                    try:
                        inst_dir, _ = winreg.QueryValueEx(v_key, "InstallDir")
                        versions.setdefault(sub_name[1:], inst_dir)
                    except EnvironmentError:
                        pass
            except EnvironmentError:
                break
    except EnvironmentError:
        pass

    return versions


def discover_installed_versions() -> Dict[str, Path]:
    """掃描本機所有已安裝之 ANSYS 版本並回傳版本號對應路徑字典 (e.g. {'251': Path('...'), '242': Path('...')})。

    掃描順序：
    1. AWP_ROOT* 系統與行程環境變數
    2. Windows Registry (HKLM:\\SOFTWARE\\ANSYS, Inc.\\ANSYS 與 v*)
    3. ANSYS_ROOT 目錄下所有 v* 子資料夾
    4. 標準安裝目錄 (C:\\Program Files\\ANSYS Inc, D:\\ANSYS Inc, E:\\ANSYS Inc 等)
    """
    discovered: Dict[str, Path] = {}

    # 1. 檢查 AWP_ROOT* 環境變數
    for k, v in os.environ.items():
        if k.upper().startswith("AWP_ROOT") and v:
            ver = k[8:].strip()
            p = Path(v)
            if ver.isdigit() and p.is_dir():
                discovered[ver] = p

    # 2. 檢查 Windows 登錄檔
    reg_vers = _find_ansys_registry()
    for ver, inst_dir in reg_vers.items():
        p = Path(inst_dir)
        if p.is_dir():
            discovered.setdefault(ver, p)

    # 3. 檢查 ANSYS_ROOT 及其父子目錄
    ansys_root_env = os.environ.get("ANSYS_ROOT")
    scan_bases = []
    if ansys_root_env:
        ar_path = Path(ansys_root_env)
        if ar_path.is_dir():
            if ar_path.name.startswith("v") and ar_path.name[1:].isdigit():
                discovered.setdefault(ar_path.name[1:], ar_path)
            scan_bases.append(ar_path)
            scan_bases.append(ar_path.parent)

    # 4. 標準磁碟機目錄
    for drive in ("C:", "D:", "E:"):
        scan_bases.append(Path(rf"{drive}\Program Files\ANSYS Inc"))
        scan_bases.append(Path(rf"{drive}\ANSYS Inc"))

    for base in scan_bases:
        if not base.is_dir():
            continue
        try:
            for child in base.iterdir():
                if child.is_dir() and child.name.startswith("v") and child.name[1:].isdigit():
                    ver_num = child.name[1:]
                    discovered.setdefault(ver_num, child)
        except (PermissionError, OSError):
            continue

    return discovered


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


def _override_or(env_key: str, default_path: Path) -> Path:
    val = os.environ.get(env_key)
    return Path(val) if val else default_path


def _derive(root_path: Path, version: str, available: bool) -> AnsysConfig:
    """Derive per-module exe paths from a root path (relative to standard layout), allowing env overrides."""
    return AnsysConfig(
        version=version,
        root_path=root_path,
        workbench_exe=_override_or("ANSYS_RUNWB2", root_path / "Framework" / "bin" / "Win64" / "RunWB2.exe"),
        mechanical_exe=_override_or("ANSYS_MECHANICAL", root_path / "aisol" / "bin" / "winx64" / "AnsysWBU.exe"),
        fluent_exe=_override_or("ANSYS_FLUENT", root_path / "fluent" / "ntbin" / "win64" / "fluent.exe"),
        cfx_solve_exe=_override_or("ANSYS_CFX_SOLVE", root_path / "CFX" / "bin" / "cfx5solve.exe"),
        cfx_pre_exe=_override_or("ANSYS_CFX_PRE", root_path / "CFX" / "bin" / "cfx5pre.exe"),
        mapdl_exe=_override_or("ANSYS_MAPDL", root_path / "ansys" / "bin" / "winx64" / "ANSYS.exe"),
        lsdyna_exe=_override_or("ANSYS_LSDYNA", root_path / "ansys" / "bin" / "winx64" / "lsdyna.exe"),
        spaceclaim_exe=_override_or("ANSYS_SPACECLAIM_EXE", root_path / "scdm" / "SpaceClaim.exe"),
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


def set_active_version(version: str) -> AnsysConfig:
    """動態切換作用中之 ANSYS 版本並原地更新全域 config 實例。

    參數:
        version: 目標版本號（例如 "242"、"251"、"252" 等）。

    回傳:
        更新後的 AnsysConfig 實例。
    """
    ver = str(version).strip().lstrip("v")
    os.environ["ANSYS_VERSION"] = ver

    discovered = discover_installed_versions()
    if ver in discovered:
        target_root = discovered[ver]
        os.environ[f"AWP_ROOT{ver}"] = str(target_root)
        os.environ["ANSYS_ROOT"] = str(target_root.parent)

    new_cfg = get_config()
    for field in (
        "version",
        "root_path",
        "workbench_exe",
        "mechanical_exe",
        "fluent_exe",
        "cfx_solve_exe",
        "cfx_pre_exe",
        "mapdl_exe",
        "lsdyna_exe",
        "spaceclaim_exe",
        "available",
    ):
        setattr(config, field, getattr(new_cfg, field))

    return config
