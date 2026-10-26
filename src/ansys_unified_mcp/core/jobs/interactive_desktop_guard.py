"""Windows Interactive Desktop and Session 0 isolation guard.

Prevents GUI-dependent solver crashes in Windows Session 0 service contexts
and injects deterministic silent headless batch flags and environment variables.
Provides clear configuration guidance on session isolation remediation.
"""

from __future__ import annotations

import csv
import io
import logging
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


class DesktopGuardError(RuntimeError):
    """Base exception for interactive desktop guard failures."""
    pass


class SessionZeroExecutionError(DesktopGuardError):
    """Raised when a GUI/OpenGL dependent solver is attempted in Windows Session 0."""

    def __init__(
        self,
        message: Optional[str] = None,
        binary_name: str = "",
        session_id: int = 0,
        guidance: str = "",
    ) -> None:
        self.binary_name = binary_name
        self.session_id = session_id
        self.guidance = guidance
        if message is None:
            message = (
                f"[CRITICAL INTERCEPTION] Execution of GUI-dependent binary '{binary_name}' "
                f"is blocked in Windows Session {session_id}!\n\n{guidance}"
            )
        super().__init__(message)


# Backward compatibility alias
SessionZeroBlockedError = SessionZeroExecutionError


class InteractiveDesktopGuard:
    """Guard against non-interactive Session 0 executions and manager for silent solver flags."""

    # Set of binaries known to depend on an interactive Windows desktop session
    GUI_DEPENDENT_BINARIES: Set[str] = {
        "ansysedt.exe",
        "runwb2.exe",
        "opticstudio.exe",
        "spaceclaim.exe",
        "mechanical.exe",
        "ansyswbu.exe",
    }

    # Headless silent flags required for headless command dispatch
    DEFAULT_HEADLESS_FLAGS: List[str] = [
        "-ng",
        "-BatchSolve",
        "-Distributed",
    ]

    # Mandatory environment variables to suppress blocking message boxes and nodelock checks
    MANDATORY_ENV_VARS: Dict[str, str] = {
        "ANSYSEM_DONT_SHOW_MESSAGEBOX": "1",
        "ANS_DISABLE_NODELOCK_CHECK": "1",
        "ANSYS_BATCH": "1",
        "ANS_NODIAG": "1",
    }

    def __init__(
        self,
        monitored_binaries: Optional[Set[str]] = None,
        custom_headless_flags: Optional[List[str]] = None,
        custom_env_vars: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialize InteractiveDesktopGuard with configurable binaries and flags."""
        if monitored_binaries is not None:
            self.monitored_binaries = {b.lower() for b in monitored_binaries}
        else:
            self.monitored_binaries = set(self.GUI_DEPENDENT_BINARIES)

        self.headless_flags = list(custom_headless_flags or self.DEFAULT_HEADLESS_FLAGS)
        self.env_vars = dict(self.MANDATORY_ENV_VARS)
        if custom_env_vars:
            self.env_vars.update(custom_env_vars)

    # -------------------------------------------------------------------------
    # Windows Session ID Detection
    # -------------------------------------------------------------------------

    @classmethod
    def get_current_session_id(cls) -> int:
        """Query Windows Terminal Services Session ID for the current process.

        Priority order:
        1. Environment variable override: ANSYS_DESKTOP_GUARD_SESSION_ID or ANSYS_MOCK_SESSION_ID.
        2. Windows native ctypes kernel32 API: ProcessIdToSessionId.
        3. PyWin32 win32ts module (if installed).
        4. tasklist /FO CSV CLI fallback.
        5. Default to 1 (interactive desktop).
        """
        for env_key in ("ANSYS_DESKTOP_GUARD_SESSION_ID", "ANSYS_MOCK_SESSION_ID"):
            env_val = os.getenv(env_key)
            if env_val is not None:
                try:
                    return int(env_val.strip())
                except ValueError:
                    logger.debug("Failed parsing %s: %s", env_key, env_val)

        if sys.platform == "win32":
            # 2. ctypes kernel32 API
            try:
                import ctypes
                from ctypes import wintypes
                kernel32 = ctypes.windll.kernel32
                session_id = wintypes.DWORD()
                pid = kernel32.GetCurrentProcessId()
                if kernel32.ProcessIdToSessionId(pid, ctypes.byref(session_id)):
                    return int(session_id.value)
            except Exception as exc:
                logger.debug("ctypes ProcessIdToSessionId failed: %s", exc)

            # 3. win32ts fallback
            try:
                import win32ts  # type: ignore
                return int(win32ts.ProcessIdToSessionId(os.getpid()))
            except Exception:
                pass

            # 4. tasklist CLI fallback
            try:
                res = subprocess.run(
                    ["tasklist", "/FO", "CSV", "/FI", f"PID eq {os.getpid()}"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                if res.returncode == 0 and res.stdout:
                    reader = csv.reader(io.StringIO(res.stdout.strip()))
                    rows = list(reader)
                    if len(rows) >= 2:
                        header = [h.strip().lower() for h in rows[0]]
                        data = rows[1]
                        session_idx = -1
                        for idx, col in enumerate(header):
                            if "session" in col and ("#" in col or "num" in col):
                                session_idx = idx
                                break
                        if session_idx == -1 and len(data) >= 4:
                            # Standard tasklist column 3 is Session#
                            session_idx = 3
                        if session_idx != -1 and session_idx < len(data):
                            val = data[session_idx].strip()
                            if val.isdigit():
                                return int(val)
            except Exception as exc:
                logger.debug("tasklist session detection failed: %s", exc)

        return 1

    @classmethod
    def is_session_zero(cls, session_id: Optional[int] = None) -> bool:
        """Return True if running inside Windows Session 0."""
        sid = cls.get_current_session_id() if session_id is None else session_id
        return sid == 0

    # -------------------------------------------------------------------------
    # Classification & Session Validation
    # -------------------------------------------------------------------------

    def extract_binary_name(self, command_or_binary: Union[str, Path, List[str]]) -> str:
        """Extract the base executable filename from a path, string, or command list."""
        if isinstance(command_or_binary, (list, tuple)):
            if not command_or_binary:
                return ""
            raw_binary = str(command_or_binary[0])
        elif isinstance(command_or_binary, Path):
            return command_or_binary.name.lower()
        else:
            raw_str = str(command_or_binary).strip()
            # If it directly specifies an executable or path without flag arguments
            if raw_str.lower().endswith(".exe") or ("\\" in raw_str and " -" not in raw_str and " /" not in raw_str):
                raw_binary = raw_str
            elif " " in raw_str and not Path(raw_str).is_file():
                try:
                    tokens = shlex.split(raw_str, posix=(sys.platform != "win32"))
                    raw_binary = tokens[0] if tokens else ""
                except ValueError:
                    raw_binary = raw_str.split()[0] if raw_str.split() else ""
            else:
                raw_binary = raw_str

        raw_binary = raw_binary.strip("\"'")
        return Path(raw_binary).name.lower()

    def is_gui_binary(self, command_or_binary: Union[str, Path, List[str]]) -> bool:
        """Return True if the target binary is identified as GUI-dependent."""
        bname = self.extract_binary_name(command_or_binary)
        return bname in self.monitored_binaries

    def get_session_zero_guidance(self, binary_name: str) -> str:
        """Generate structured configuration guidance when execution is blocked in Session 0."""
        return (
            f"=== Windows Session 0 Execution Blocked for {binary_name} ===\n"
            f"Root Cause:\n"
            f"  Binary '{binary_name}' requires an interactive Windows GUI desktop window manager.\n"
            f"  Windows Session 0 is reserved strictly for non-interactive system services (Session 0 Isolation).\n"
            f"  Running GUI-dependent ANSYS applications in Session 0 causes silent crashes, frozen\n"
            f"  modal message boxes, missing graphics context, or NTSTATUS 0xC0000142 termination.\n\n"
            f"Remediation & Configuration Steps:\n"
            f"  1. Interactive Logon Session:\n"
            f"     Run the agent or MCP server in an active user logon session (Session 1 or higher).\n"
            f"  2. Windows Task Scheduler Configuration:\n"
            f"     If launching via Task Scheduler, configure the task with:\n"
            f"       - 'Run only when user is logged on' checked.\n"
            f"       - 'Run with highest privileges' checked.\n"
            f"  3. OpenSSH / Remote Agent Configuration:\n"
            f"     When using remote execution services, do not spawn GUI processes directly from Session 0.\n"
            f"     Dispatch workloads via interactive agent workers or headless solver APIs.\n"
            f"  4. Headless Silent Flags:\n"
            f"     Ensure proper silent flags (-ng -BatchSolve -Distributed) are supplied when batch solve is intended."
        )

    def validate_session(
        self,
        command_or_binary: Union[str, Path, List[str]],
        session_id: Optional[int] = None,
    ) -> None:
        """Validate whether the binary can safely execute in the target session.

        Raises:
            SessionZeroExecutionError: If a GUI-dependent binary is dispatched in Session 0.
        """
        binary_name = self.extract_binary_name(command_or_binary)
        if not self.is_gui_binary(command_or_binary):
            return

        sid = self.get_current_session_id() if session_id is None else session_id
        if sid == 0:
            guidance = self.get_session_zero_guidance(binary_name)
            logger.critical(
                "Blocked dispatch of GUI-dependent binary '%s' in Windows Session 0.",
                binary_name,
            )
            raise SessionZeroExecutionError(
                message=None,
                binary_name=binary_name,
                session_id=0,
                guidance=guidance,
            )

    @classmethod
    def assert_not_session_zero(cls, requires_gui: bool = True, solver_name: str = "") -> None:
        """Enforce that GUI-dependent CAE solvers are never executed in Session 0."""
        if requires_gui and cls.is_session_zero():
            guard = cls()
            guidance = guard.get_session_zero_guidance(solver_name or "solver")
            raise SessionZeroExecutionError(
                message=(
                    f"Execution of GUI/OpenGL dependent solver '{solver_name}' is blocked in Windows Session 0! "
                    "Session 0 lacks an interactive desktop display and GPU hardware rasterizer. "
                    "Please configure an interactive service runner or launch in headless batch mode."
                ),
                binary_name=solver_name,
                session_id=0,
                guidance=guidance,
            )

    # -------------------------------------------------------------------------
    # Headless Silent Flags & Environment Injection
    # -------------------------------------------------------------------------

    def inject_headless_flags(
        self,
        command: List[str],
        binary_name: Optional[str] = None,
    ) -> List[str]:
        """Automatically inject headless silent flags (-ng -BatchSolve -Distributed).

        Preserves existing arguments and ensures no duplicated flags are added.
        """
        if not command:
            return list(command)

        bname = (binary_name or self.extract_binary_name(command)).lower()
        new_command = list(command)

        if bname in self.monitored_binaries or any(k in bname for k in ("ansysedt", "runwb2", "spaceclaim", "opticstudio")):
            existing_flags_lower = {arg.lower() for arg in command[1:]}
            flags_to_insert = [
                flag for flag in self.headless_flags
                if flag.lower() not in existing_flags_lower
            ]
            if flags_to_insert:
                new_command = [command[0]] + flags_to_insert + list(command[1:])
                logger.debug("Injected headless flags %s into command for %s", flags_to_insert, bname)

        return new_command

    def inject_environment(
        self,
        env: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Inject mandatory environment variables to suppress dialogs and nodelock checks."""
        prepared_env = dict(os.environ if env is None else env)
        for key, value in self.env_vars.items():
            prepared_env[key] = str(value)
        return prepared_env

    @staticmethod
    def inject_silent_flags(
        solver: str,
        command_args: List[str],
        env: Optional[Dict[str, str]] = None,
    ) -> Tuple[List[str], Dict[str, str]]:
        """Inject headless batch flags and silence messagebox popups for specific solvers."""
        args = list(command_args)
        modified_env = dict(env if env is not None else os.environ)

        # Universal silent flags
        modified_env["ANSYS_BATCH"] = "1"
        modified_env["ANS_NODIAG"] = "1"
        modified_env["ANS_DISABLE_NODELOCK_CHECK"] = "1"

        solver_lower = solver.lower()

        # Electronics Desktop (HFSS, Maxwell, Q3D, AEDT)
        if any(term in solver_lower for term in ("aedt", "hfss", "maxwell", "ansysedt")):
            modified_env["ANSYSEM_DONT_SHOW_MESSAGEBOX"] = "1"
            modified_env["ANSYSEM_NO_MESSAGE_BOX"] = "1"
            if "-ng" not in args:
                args.append("-ng")
            if "-BatchSolve" not in args and "-BatchExtract" not in args:
                args.append("-BatchSolve")
            if "-Distributed" not in args:
                args.append("-Distributed")

        # Mechanical / APDL
        elif any(term in solver_lower for term in ("mechanical", "ansyswbu", "mapdl")):
            modified_env["ANSYS_NO_GUI"] = "1"
            if "-b" not in args and "-Batch" not in args:
                args.append("-Batch")

        # Fluent CFD
        elif "fluent" in solver_lower:
            modified_env["FLUENT_BATCH"] = "1"
            if "-g" not in args:
                args.append("-g")

        return args, modified_env

    def prepare_command(
        self,
        command: Union[str, List[str]],
        env: Optional[Dict[str, str]] = None,
        check_session: bool = True,
        session_id: Optional[int] = None,
    ) -> Tuple[List[str], Dict[str, str]]:
        """Validate session safety and prepare command tokens and environment dictionary."""
        if isinstance(command, str):
            cmd_list = shlex.split(command, posix=(sys.platform != "win32"))
        else:
            cmd_list = [str(x) for x in command]

        if not cmd_list:
            raise ValueError("Command cannot be empty")

        if check_session:
            self.validate_session(cmd_list, session_id=session_id)

        prepared_cmd = self.inject_headless_flags(cmd_list)
        prepared_env = self.inject_environment(env)

        return prepared_cmd, prepared_env

    def execute_guarded(
        self,
        command: Union[str, List[str]],
        env: Optional[Dict[str, str]] = None,
        check_session: bool = True,
        session_id: Optional[int] = None,
        **subprocess_kwargs: Any,
    ) -> subprocess.CompletedProcess:
        """Prepare and safely execute a process with session checks and headless flags applied."""
        prepared_cmd, prepared_env = self.prepare_command(
            command=command,
            env=env,
            check_session=check_session,
            session_id=session_id,
        )
        return subprocess.run(prepared_cmd, env=prepared_env, **subprocess_kwargs)
