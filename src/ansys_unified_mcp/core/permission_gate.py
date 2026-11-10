"""Permission gate and declarative security boundary enforcement.

This module provides path validation, binary inspection control,
command checking, and permission enforcement decorators.
All code comments follow ASD-STE100 and IronPython ASCII safety standards.
"""

from __future__ import annotations

import fnmatch
import functools
import inspect
import logging
import os
import shlex
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union

import yaml

logger = logging.getLogger(__name__)


class SecurityGatePermissionError(PermissionError):
    """Raised when an operation violates security gate permissions."""

    def __init__(self, message: str, category: str, remediation: str) -> None:
        super().__init__(
            f"Permission denied [Category: {category}]. {message} Remediation: {remediation}"
        )
        self.category = category
        self.remediation = remediation


@dataclass(frozen=True)
class AllowedRoot:
    """Represents an authorized path boundary."""

    id: str
    path: Path
    description: str
    allow_read: bool = True
    allow_write: bool = False


class PermissionGate:
    """Enforces declarative permissions and boundary controls.

    Loads security manifest from permissions.yaml and provides
    runtime path, binary, and command safety validations.
    """

    def __init__(self, manifest_path: Optional[Union[str, Path]] = None) -> None:
        # Determine repository root directory
        self.project_root = Path(__file__).resolve().parents[3]

        # Locate manifest configuration file
        if manifest_path:
            self.manifest_path = Path(manifest_path).resolve()
        else:
            env_manifest = os.environ.get("ANSYS_MCP_PERMISSIONS_MANIFEST")
            if env_manifest:
                self.manifest_path = Path(env_manifest).resolve()
            else:
                self.manifest_path = Path(__file__).resolve().parents[1] / "resources" / "manifests" / "permissions.yaml"

        # Initialize collections
        self.categories: Dict[str, Dict[str, Any]] = {}
        self.allowed_roots: List[AllowedRoot] = []
        self.blocked_extensions: Set[str] = set()
        self.restricted_patterns: List[str] = []
        self.disallowed_commands: Set[str] = set()
        self.proprietary_binary_patterns: List[str] = []

        # Resolve system path locations
        self.runtime_dir = self._resolve_runtime_dir()
        self.temp_dir = Path(tempfile.gettempdir()).resolve()
        self.ansys_root = self._resolve_ansys_root()

        # Load manifest configuration
        self._load_manifest()

    def _resolve_runtime_dir(self) -> Path:
        """Resolve writable runtime directory."""
        try:
            from ansys_unified_mcp.core.paths import resolve_runtime_dir

            return resolve_runtime_dir()
        except Exception:
            fallback = self.project_root / ".runtime"
            try:
                fallback.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError):
                pass
            return fallback.resolve()

    def _resolve_ansys_root(self) -> Optional[Path]:
        """Resolve installed ANSYS root directory if present."""
        # Check configuration module
        try:
            from ansys_unified_mcp.config import config

            if getattr(config, "available", False) and config.root_path.exists():
                return config.root_path.resolve()
        except Exception:
            pass

        # Check environment variables
        for key in os.environ:
            if key.upper().startswith("AWP_ROOT") or key.upper() == "ANSYS_ROOT":
                val = os.environ.get(key)
                if val:
                    p = Path(val).resolve()
                    if p.exists():
                        return p

        # Check standard Windows default location
        if os.name == "nt":
            std_dir = Path(r"C:\Program Files\ANSYS Inc")
            if std_dir.exists():
                return std_dir.resolve()

        return None

    def _load_manifest(self) -> None:
        """Load manifest from YAML file or apply safe defaults."""
        data: Dict[str, Any] = {}
        if self.manifest_path.is_file():
            try:
                with open(self.manifest_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
            except Exception as exc:
                logger.warning(
                    "Failed to parse permissions manifest at %s: %s",
                    self.manifest_path,
                    exc,
                )

        # Parse categories
        self.categories = data.get("categories", {})
        if not self.categories:
            self.categories = {
                "open_source": {
                    "tier": 1,
                    "description": "PyAnsys open-source ecosystem packages.",
                },
                "documented_api": {
                    "tier": 2,
                    "description": "Official published API documentation.",
                },
                "observable_runtime": {
                    "tier": 3,
                    "description": "Authorized solver execution and observable runtime.",
                },
                "proprietary_binary": {
                    "tier": 4,
                    "description": "Commercial proprietary binaries and solvers.",
                },
                "restricted": {
                    "tier": 5,
                    "description": "Strictly prohibited operations and resources.",
                },
            }

        # Parse blocked extensions
        paths_cfg = data.get("paths", {})
        ext_list = paths_cfg.get(
            "blocked_extensions",
            [
                ".lic",
                ".key",
                ".pem",
                ".crt",
                ".pfx",
                ".p12",
                ".secret",
                ".token",
                ".pdb",
                ".idb",
                ".i64",
                ".til",
                ".nam",
                ".dmp",
                ".dump",
                ".core",
            ],
        )
        self.blocked_extensions = {
            ext.lower() if ext.startswith(".") else f".{ext.lower()}"
            for ext in ext_list
        }

        # Parse restricted patterns
        self.restricted_patterns = paths_cfg.get(
            "restricted_patterns",
            [
                "*licdebug*",
                "*ansyslmd*",
                "*/.ssh/*",
                "*\\.ssh\\*",
                "*/.aws/*",
                "*\\.aws\\*",
                "C:\\Windows\\System32\\*",
                "C:\\Windows\\SysWOW64\\*",
                "/etc/shadow",
                "/etc/passwd",
            ],
        )

        # Parse disallowed commands
        cmds_cfg = data.get("commands", {})
        raw_disallowed = cmds_cfg.get(
            "disallowed_commands",
            [
                "ghidra",
                "ida",
                "ida64",
                "idat",
                "idat64",
                "x64dbg",
                "x32dbg",
                "windbg",
                "ollydbg",
                "radare2",
                "r2",
                "cutter",
                "gdb",
                "lldb",
                "objdump",
                "readelf",
                "dnspy",
                "ilspy",
                "jadx",
                "strings",
                "pedump",
                "dumpbin",
                "pestudio",
                "hexdump",
                "hxd",
                "hexedit",
                "bpatch",
                "lmutil",
                "lmgrd",
            ],
        )
        self.disallowed_commands = {cmd.lower() for cmd in raw_disallowed}

        # Parse proprietary binary patterns
        self.proprietary_binary_patterns = cmds_cfg.get(
            "proprietary_binary_patterns",
            [
                "*ansys*.exe",
                "*ansys*.dll",
                "*fluent*.exe",
                "*fluent*.dll",
                "*RunWB2*.exe",
                "*SpaceClaim*.exe",
                "*lsdyna*.exe",
                "*cfx5*.exe",
                "*mapdl*.exe",
                "*optislang*.exe",
            ],
        )

        # Build allowed roots
        self._build_allowed_roots(paths_cfg.get("allowed_roots", []))

    def _build_allowed_roots(self, configured_roots: List[Dict[str, Any]]) -> None:
        """Resolve and register allowed directory roots."""
        roots: List[AllowedRoot] = []

        # Always register project root
        roots.append(
            AllowedRoot(
                id="project_root",
                path=self.project_root,
                description="Project workspace directory",
                allow_read=True,
                allow_write=True,
            )
        )

        # Register runtime directory
        if self.runtime_dir:
            roots.append(
                AllowedRoot(
                    id="runtime_dir",
                    path=self.runtime_dir,
                    description="Runtime working directory",
                    allow_read=True,
                    allow_write=True,
                )
            )

        # Register temporary directory
        roots.append(
            AllowedRoot(
                id="temp_dir",
                path=self.temp_dir,
                description="System temporary directory",
                allow_read=True,
                allow_write=True,
            )
        )

        # Register ANSYS install root as read-only if present
        if self.ansys_root and self.ansys_root.exists():
            roots.append(
                AllowedRoot(
                    id="ansys_install_root",
                    path=self.ansys_root,
                    description="Official ANSYS installation root",
                    allow_read=True,
                    allow_write=False,
                )
            )

        # Process any additional configured roots
        for entry in configured_roots:
            raw_path = entry.get("path", "")
            root_id = entry.get("id", "")
            if root_id in {
                "project_root",
                "runtime_dir",
                "temp_dir",
                "ansys_install_root",
            }:
                continue
            resolved_p = self._interpolate_path(raw_path)
            if resolved_p and resolved_p.exists():
                roots.append(
                    AllowedRoot(
                        id=root_id or resolved_p.name,
                        path=resolved_p,
                        description=entry.get("description", ""),
                        allow_read=entry.get("allow_read", True),
                        allow_write=entry.get("allow_write", False),
                    )
                )

        self.allowed_roots = roots

    def _interpolate_path(self, raw: str) -> Optional[Path]:
        """Interpolate path variables like ${PROJECT_ROOT}."""
        if not raw:
            return None
        expanded = raw.replace("${PROJECT_ROOT}", str(self.project_root))
        if self.ansys_root:
            expanded = expanded.replace("${ANSYS_ROOT}", str(self.ansys_root))
        expanded = expanded.replace("${RUNTIME_DIR}", str(self.runtime_dir))
        expanded = expanded.replace("${TEMP_DIR}", str(self.temp_dir))
        try:
            return Path(expanded).resolve()
        except Exception:
            return None

    @staticmethod
    def _is_subpath(target: Path, base: Path) -> bool:
        """Check if target path is inside base path."""
        try:
            target.relative_to(base)
            return True
        except ValueError:
            if os.name == "nt":
                t_str = str(target).lower()
                b_str = str(base).lower()
                if t_str == b_str:
                    return True
                b_prefix = b_str if b_str.endswith(("\\", "/")) else b_str + "\\"
                return t_str.startswith(b_prefix)
            return False

    def check_path(
        self, path: Union[str, Path], access_type: str = "read"
    ) -> Path:
        """Validate path boundaries, extensions, and traversal prevention.

        Uses Path.resolve() to resolve symlinks and path traversal attempts.
        Raises PermissionError if path violates security constraints.
        """
        raw_candidate = Path(path)
        if not raw_candidate.is_absolute():
            resolved = (self.project_root / raw_candidate).resolve()
        else:
            resolved = raw_candidate.resolve()

        # 1. Blocked extensions check
        suffix = resolved.suffix.lower()
        if suffix in self.blocked_extensions:
            raise SecurityGatePermissionError(
                f"Access to file extension '{suffix}' is prohibited for '{resolved.name}'.",
                category="restricted",
                remediation="Remove proprietary license files, private symbol files (.pdb), or cryptographic keys from the request.",
            )

        # 2. Restricted pattern check
        resolved_str = str(resolved)
        resolved_name = resolved.name
        for pattern in self.restricted_patterns:
            if fnmatch.fnmatch(resolved_str, pattern) or fnmatch.fnmatch(
                resolved_name, pattern
            ):
                raise SecurityGatePermissionError(
                    f"Path '{resolved}' matches restricted security pattern '{pattern}'.",
                    category="restricted",
                    remediation="Direct access to license daemons, credential stores, or system directories is prohibited.",
                )

        # Explicitly check sensitive directory components
        parts_lower = {p.lower() for p in resolved.parts}
        if ".ssh" in parts_lower or ".aws" in parts_lower:
            raise SecurityGatePermissionError(
                f"Path '{resolved}' accesses sensitive credential directory.",
                category="restricted",
                remediation="Credentials and SSH keys must not be accessed.",
            )

        # 3. Allowed roots boundary check
        matching_root: Optional[AllowedRoot] = None
        for root in self.allowed_roots:
            if self._is_subpath(resolved, root.path):
                matching_root = root
                break

        if matching_root is None:
            allowed_names = [f"{r.id} ({r.path})" for r in self.allowed_roots]
            raise SecurityGatePermissionError(
                f"Path '{resolved}' is outside authorized directory boundaries.",
                category="restricted",
                remediation=f"Ensure file operations are within authorized boundaries: {', '.join(allowed_names)}.",
            )

        # 4. Check write permissions on boundary
        if access_type.lower() == "write":
            if not matching_root.allow_write:
                raise SecurityGatePermissionError(
                    f"Path '{resolved}' is located in read-only boundary '{matching_root.id}'. Write access is prohibited.",
                    category="restricted",
                    remediation=f"Boundary '{matching_root.id}' ({matching_root.path}) is read-only. Write to project workspace or runtime directory instead.",
                )

        return resolved

    def check_binary_inspection(self, binary_path: Union[str, Path]) -> bool:
        """Validate binary target before inspection or reverse engineering.

        Disassembly, decompilation, and symbol scraping on commercial proprietary
        binaries are strictly forbidden.
        """
        raw_candidate = Path(binary_path)
        if not raw_candidate.is_absolute():
            resolved = (self.project_root / raw_candidate).resolve()
        else:
            resolved = raw_candidate.resolve()

        # Check blocked extensions (e.g. .pdb, .idb)
        suffix = resolved.suffix.lower()
        if suffix in self.blocked_extensions:
            raise SecurityGatePermissionError(
                f"Binary inspection on private symbol or database file '{resolved.name}' is prohibited.",
                category="proprietary_binary",
                remediation="Inspection of proprietary debug symbols (.pdb) and database files is forbidden.",
            )

        # Check if target matches proprietary binary patterns
        name_lower = resolved.name.lower()
        is_proprietary = False
        for pat in self.proprietary_binary_patterns:
            if fnmatch.fnmatch(name_lower, pat.lower()):
                is_proprietary = True
                break

        # Check if target is inside ANSYS install root with binary extension
        if (
            not is_proprietary
            and self.ansys_root
            and self._is_subpath(resolved, self.ansys_root)
        ):
            if suffix in {".exe", ".dll", ".so", ".dylib", ".pyd", ".sys"}:
                is_proprietary = True

        if is_proprietary:
            raise SecurityGatePermissionError(
                f"Binary inspection, disassembly, or decompilation on commercial binary '{resolved.name}' is strictly prohibited.",
                category="proprietary_binary",
                remediation="Use official documented APIs, PyAnsys high-level interfaces, or ACT scripts instead of reverse engineering commercial binaries.",
            )

        return True

    def check_command(self, command: str) -> None:
        """Validate shell or process command against reverse engineering rules."""
        if not command or not command.strip():
            return

        cmd_clean = command.strip()

        # Tokenize command safely
        try:
            if os.name == "nt":
                tokens = shlex.split(cmd_clean, posix=False)
            else:
                tokens = shlex.split(cmd_clean)
        except Exception:
            tokens = cmd_clean.split()

        if not tokens:
            return

        # Extract primary executable name
        primary_exe = Path(tokens[0]).name.lower()
        for ext in (".exe", ".bat", ".cmd", ".sh", ".py"):
            if primary_exe.endswith(ext):
                primary_exe = primary_exe[: -len(ext)]
                break

        # 1. Check if utility targets proprietary solver binaries
        binary_inspection_tools = {
            "strings",
            "pedump",
            "dumpbin",
            "pestudio",
            "hexdump",
        }
        if primary_exe in binary_inspection_tools:
            for arg in tokens[1:]:
                arg_lower = Path(arg).name.lower()
                for pat in self.proprietary_binary_patterns:
                    if fnmatch.fnmatch(arg_lower, pat.lower()):
                        raise SecurityGatePermissionError(
                            f"Command '{primary_exe}' targeting commercial solver binary '{arg}' is prohibited.",
                            category="proprietary_binary",
                            remediation="Commercial binary inspection or disassembly is forbidden. Use official documented APIs or PyAnsys interfaces.",
                        )

        # 2. Check disallowed command list
        if primary_exe in self.disallowed_commands:
            raise SecurityGatePermissionError(
                f"Execution of disallowed reverse engineering command '{tokens[0]}' is blocked.",
                category="restricted",
                remediation="Disassemblers, decompilers, debuggers, and binary analysis utilities are prohibited.",
            )

        # 3. Check for token-level command violation
        for token in tokens:
            token_name = Path(token).name.lower()
            for ext in (".exe", ".bat", ".cmd", ".sh"):
                if token_name.endswith(ext):
                    token_name = token_name[: -len(ext)]
                    break
            if token_name in self.disallowed_commands:
                raise SecurityGatePermissionError(
                    f"Command references prohibited utility '{token}'.",
                    category="restricted",
                    remediation="Disassemblers, debuggers, and binary dump tools are prohibited in command arguments.",
                )

        # 4. Check for DRM or license tampering commands
        for token in tokens:
            lower_tok = token.lower()
            if "lmutil" in lower_tok or "lmgrd" in lower_tok:
                raise SecurityGatePermissionError(
                    f"License management or tampering invocation '{token}' is blocked.",
                    category="restricted",
                    remediation="Direct license server tampering is strictly forbidden.",
                )

    def enforce_permission(self, category: str) -> Callable:
        """Enforce permission decorator bound to this PermissionGate instance."""
        return enforce_permission(category, gate=self)


# Default global gate instance
permission_gate = PermissionGate()


def _validate_call(
    gate: PermissionGate,
    category: str,
    func: Callable,
    args: tuple,
    kwargs: dict,
) -> None:
    """Validate function arguments against specified permission category."""
    # 1. Block restricted category unconditionally
    if category == "restricted":
        raise SecurityGatePermissionError(
            f"Execution of function '{func.__name__}' under 'restricted' permission tier is prohibited.",
            category="restricted",
            remediation="Restricted tier operations cannot be executed. Re-architect logic to use public documented APIs.",
        )

    # 2. Extract bound arguments
    try:
        sig = inspect.signature(func)
        bound = sig.bind_partial(*args, **kwargs)
        arguments = bound.arguments
    except Exception:
        arguments = kwargs.copy()

    # 3. Inspect binary path if proprietary_binary category
    if category == "proprietary_binary":
        for param_name, val in arguments.items():
            if any(k in param_name.lower() for k in ("binary", "exe", "dll")):
                if isinstance(val, (str, Path)):
                    gate.check_binary_inspection(val)

    # 4. Inspect paths across all categories
    for param_name, val in arguments.items():
        name_lower = param_name.lower()
        if any(
            k in name_lower
            for k in ("path", "file", "directory", "dir", "workspace")
        ):
            if isinstance(val, (str, Path)):
                access_type = (
                    "write"
                    if any(w in name_lower for w in ("out", "dest", "write"))
                    else "read"
                )
                gate.check_path(val, access_type=access_type)

    # 5. Inspect commands across all categories
    for param_name, val in arguments.items():
        name_lower = param_name.lower()
        if any(k in name_lower for k in ("command", "cmd")):
            if isinstance(val, str):
                gate.check_command(val)


def enforce_permission(
    category: str, gate: Optional[PermissionGate] = None
) -> Callable:
    """Decorator to enforce security permission categories on functions.

    Supports both synchronous and asynchronous functions.
    """
    target_gate = gate or permission_gate

    def decorator(func: Callable) -> Callable:
        cat_lower = category.lower().strip()

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                _validate_call(target_gate, cat_lower, func, args, kwargs)
                return await func(*args, **kwargs)

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                _validate_call(target_gate, cat_lower, func, args, kwargs)
                return func(*args, **kwargs)

            return sync_wrapper

    return decorator
