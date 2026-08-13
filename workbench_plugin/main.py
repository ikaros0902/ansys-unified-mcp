# encoding: utf-8
"""ACT entry point for Workbench MCP (slim).

On load inside Mechanical (AnsysWBU), this plugin:
- auto-starts the Mechanical gRPC server on a free port (10000+), and
- registers the instance (pid, app name, gRPC port) into the MCP registry dir,

so the MCP server can discover and connect to a running Mechanical via
PyMechanical. The previous file-queue and socket-timer transports were removed
during the architecture refactor (superseded by gRPC + the Workbench-journal
bridge).

Set WORKBENCH_MCP_QUEUE_ROOT (or WORKBENCH_MCP_ROOT) so the registry lands in
the same folder the MCP server reads. If neither is set, the registry defaults
to a folder next to this plugin.
"""

from __future__ import print_function

import os
import time

try:
    import __builtin__ as _builtins
except Exception:
    import builtins as _builtins


_PLUGIN_DIR = os.path.abspath(os.path.dirname(__file__))
def _resolve_queue_root():
    env_queue = os.environ.get("WORKBENCH_MCP_QUEUE_ROOT")
    if env_queue:
        return env_queue
    env_root = os.environ.get("WORKBENCH_MCP_ROOT")
    if env_root:
        return os.path.join(env_root, "workbench_queue")
    cur = _PLUGIN_DIR
    for _ in range(5):
        if os.path.exists(os.path.join(cur, "pyproject.toml")):
            return os.path.join(cur, "workbench_queue")
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    fallback = r"D:\Ikaros\ANSYS-unified-MCP\workbench_queue"
    if os.path.exists(r"D:\Ikaros\ANSYS-unified-MCP"):
        return fallback
    return os.path.join(_PLUGIN_DIR, "workbench_queue")

_QUEUE_ROOT = _resolve_queue_root()
_PROJECT_ROOT = os.path.dirname(_QUEUE_ROOT)
_DEBUG_LOG_FILE = os.path.join(_QUEUE_ROOT, "act_main_debug.log")


def _mkdirs(path):
    if not path or os.path.isdir(path):
        return
    parent = os.path.dirname(path)
    if parent and parent != path and not os.path.isdir(parent):
        _mkdirs(parent)
    if not os.path.isdir(path):
        os.mkdir(path)


def _debug_log(message):
    try:
        _mkdirs(os.path.dirname(_DEBUG_LOG_FILE))
        with open(_DEBUG_LOG_FILE, "a") as fp:
            fp.write("%s [WorkbenchMCP main.py] %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), str(message)))
    except Exception:
        pass


def _log(message):
    _debug_log(message)
    try:
        ExtAPI.Log.WriteMessage("[WorkbenchMCP] " + str(message))
    except Exception:
        print("[WorkbenchMCP] " + str(message))


def find_free_port(start_port, max_attempts=100):
    import socket
    for port in range(start_port, start_port + max_attempts):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(('127.0.0.1', port))
            s.close()
            return port
        except socket.error:
            continue
    raise RuntimeError("No free port found in range %d-%d" % (start_port, start_port + max_attempts))


def _register_instance(grpc_port=None):
    try:
        import System

        pid = os.getpid()
        proc = System.Diagnostics.Process.GetCurrentProcess()
        proc_name = proc.ProcessName
        title = proc.MainWindowTitle or proc_name

        registry_dir = os.path.join(_QUEUE_ROOT, "registry")
        if not os.path.isdir(registry_dir):
            try:
                os.makedirs(registry_dir)
            except Exception:
                pass

        reg_file = os.path.join(registry_dir, "%d.json" % pid)

        data = {}
        try:
            import json
            if os.path.isfile(reg_file):
                with open(reg_file, "r") as fp:
                    data = json.load(fp)
        except Exception:
            pass

        data["pid"] = pid
        data["app_name"] = proc_name
        data["app_title"] = title
        if grpc_port is not None:
            data["grpc_port"] = grpc_port
        data["last_seen"] = time.time()

        try:
            if "AnsysFWW" in proc_name:
                data["project_path"] = GetActiveProject().FilePath
        except Exception:
            pass

        try:
            import json
            with open(reg_file, "w") as fp:
                json.dump(data, fp)
        except Exception:
            serialized = "{"
            serialized += '"pid": %d, ' % data["pid"]
            serialized += '"app_name": "%s", ' % data["app_name"].replace('\\', '\\\\').replace('"', '\\"')
            serialized += '"app_title": "%s", ' % data["app_title"].replace('\\', '\\\\').replace('"', '\\"')
            if "grpc_port" in data:
                serialized += '"grpc_port": %d, ' % data["grpc_port"]
            if "project_path" in data:
                serialized += '"project_path": "%s", ' % data["project_path"].replace('\\', '\\\\').replace('"', '\\"')
            serialized += '"last_seen": %f' % data["last_seen"]
            serialized += "}"
            with open(reg_file, "w") as fp:
                fp.write(serialized)

        _log("Registered: PID=%d (%s) with grpc_port=%s" % (pid, proc_name, str(grpc_port)))
    except Exception as exc:
        _log("Failed to register app: " + str(exc))


def _auto_start_grpc_server():
    """Auto-start the Mechanical gRPC server for external PyMechanical (MCP) clients."""
    sentinel = "_WORKBENCH_MCP_GRPC_STARTED"
    if getattr(_builtins, sentinel, False):
        return
    setattr(_builtins, sentinel, True)

    import System
    proc_name = System.Diagnostics.Process.GetCurrentProcess().ProcessName
    if "AnsysWBU" not in proc_name:
        return

    try:
        grpc_port = find_free_port(10000)
        if hasattr(ExtAPI, "Application") and hasattr(ExtAPI.Application, "StartGrpcServer"):
            ExtAPI.Application.StartGrpcServer(grpc_port)
            _log("Auto-started Mechanical gRPC Server on port %d via ExtAPI.Application" % grpc_port)
            _register_instance(grpc_port=grpc_port)
            return

        import Ansys.ACT.Mechanical
        Ansys.ACT.Mechanical.MechanicalAPI.Instance.ApplicationAPI.StartGrpcServer(grpc_port)
        _log("Auto-started Mechanical gRPC Server on port %d via MechanicalAPI" % grpc_port)
        _register_instance(grpc_port=grpc_port)
    except Exception as exc:
        _log("Failed to auto-start gRPC Server: " + str(exc))


def show_mcp_info(analysis=None):
    _log("MCP project root: " + _PROJECT_ROOT)
    _log("MCP registry root: " + _QUEUE_ROOT)
    _log("The MCP server connects to this Mechanical via the auto-started gRPC port (see registry).")


def init_listener():
    """載入並啟動 FileSystemWatcher 非同步監聽器"""
    try:
        import wb_event_listener
        try:
            reload(wb_event_listener)
        except Exception:
            pass
        wb_event_listener.start_listener(_QUEUE_ROOT)
        _log("Initialized wb_event_listener FileSystemWatcher on " + _QUEUE_ROOT)
    except Exception as exc:
        _log("Failed to initialize wb_event_listener: " + str(exc))


def on_project_init(context=None):
    """Workbench Project Schematic 載入時的回呼函式"""
    _log("Workbench Project Schematic oninit callback triggered.")
    try:
        if context and hasattr(context, "ExtAPI"):
            setattr(_builtins, "ExtAPI", context.ExtAPI)
        elif "ExtAPI" in globals():
            setattr(_builtins, "ExtAPI", globals()["ExtAPI"])
    except Exception:
        pass
    _register_instance()
    init_listener()


_debug_log("main.py imported from " + __file__)
_register_instance()
_auto_start_grpc_server()
init_listener()
