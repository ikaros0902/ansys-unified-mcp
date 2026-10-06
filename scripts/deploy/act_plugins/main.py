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
    # This path-resolution logic duplicates core/paths.py, but the IronPython
    # runtime cannot import that module, so it is re-implemented here.
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
    env_dir = os.environ.get("ANSYS_WORKBENCH_QUEUE_DIR")
    if env_dir:
        return env_dir
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
        # 1. First try an active connect(): success means a server is already
        #    listening on this port (occupied).
        occupied = False
        try:
            s_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_test.settimeout(0.2)
            s_test.connect(('127.0.0.1', port))
            s_test.close()
            occupied = True
        except Exception:
            pass

        if occupied:
            continue

        # 2. Connect failed, so verify the port is truly free by binding to
        #    0.0.0.0 (no SO_REUSEADDR, to avoid a false-positive bind).
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(('0.0.0.0', port))
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
    """Load and start the FileSystemWatcher-based asynchronous listener."""
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


def _start_spaceclaim_port_watcher():
    """Background daemon thread that keeps Workbench's API_PORT environment
    variable pointed at the latest free port.

    When the user opens multiple SpaceClaim systems in sequence from within
    Workbench (System A, System B, ...), each new SpaceClaim process inherits
    the parent (Workbench) process's environment at launch time. Keeping
    API_PORT continuously updated means each successive SpaceClaim instance
    automatically binds to the next free port (50051 -> 50052 -> 50053 ...)
    without any manual intervention.
    """
    sentinel = "_WORKBENCH_MCP_SC_WATCHER_STARTED"
    if getattr(_builtins, sentinel, False):
        return
    setattr(_builtins, sentinel, True)

    import threading
    def _loop():
        last_port = None
        while True:
            try:
                port = find_free_port(50051)
                if port != last_port:
                    import System
                    System.Environment.SetEnvironmentVariable("API_PORT", str(port))
                    _debug_log("SpaceClaim dynamic watcher set API_PORT to %d" % port)
                    last_port = port
            except Exception as e:
                _debug_log("Watcher loop error: " + str(e))
            time.sleep(1.0)

    t = threading.Thread(target=_loop)
    t.daemon = True
    t.start()
    _log("Started background SpaceClaim dynamic port watcher.")


def on_project_init(context=None):
    """Callback invoked when the Workbench Project Schematic loads."""
    _log("Workbench Project Schematic oninit callback triggered.")
    try:
        if context and hasattr(context, "ExtAPI"):
            setattr(_builtins, "ExtAPI", context.ExtAPI)
        elif "ExtAPI" in globals():
            setattr(_builtins, "ExtAPI", globals()["ExtAPI"])
    except Exception:
        pass
    _start_spaceclaim_port_watcher()
    _register_instance()
    init_listener()


_debug_log("main.py imported from " + __file__)
_register_instance()
_auto_start_grpc_server()
init_listener()
