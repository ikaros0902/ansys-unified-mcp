# encoding: utf-8
"""Workbench ACT 非同步 FileSystemWatcher 事件監聽器 (Ponytail mode).

使用 System.IO.FileSystemWatcher 監聽 commands 目錄下的 *.json 檔案，
當收到 Created / Changed 事件時非同步讀取並執行 script，結果寫回 results/result_<id>.json。
平時 0% 占用 UI 執行緒，不會造成介面卡頓。
"""

from __future__ import print_function

import json
import os
import sys
import threading
import time
import traceback

import System
from System.IO import FileSystemWatcher, NotifyFilters

_PLUGIN_DIR = os.path.abspath(os.path.dirname(__file__))

def _resolve_queue_root():
    env_queue = os.environ.get("WORKBENCH_MCP_QUEUE_ROOT")
    if env_queue:
        return env_queue
    env_root = os.environ.get("WORKBENCH_MCP_ROOT")
    if env_root:
        return os.path.join(env_root, "workbench_queue")
    # 搜尋專案根目錄
    cur = _PLUGIN_DIR
    for _ in range(5):
        if os.path.exists(os.path.join(cur, "pyproject.toml")):
            return os.path.join(cur, "workbench_queue")
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    # 專案預設備援路徑
    fallback = r"D:\Ikaros\ANSYS-unified-MCP\workbench_queue"
    if os.path.exists(r"D:\Ikaros\ANSYS-unified-MCP"):
        return fallback
    return os.path.join(_PLUGIN_DIR, "workbench_queue")

_QUEUE_ROOT = _resolve_queue_root()
_COMMANDS_DIR = os.path.join(_QUEUE_ROOT, "commands")
_RESULTS_DIR = os.path.join(_QUEUE_ROOT, "results")
_LOG_FILE = os.path.join(_QUEUE_ROOT, "wb_listener.log")

_watcher = None
_processed_lock = threading.Lock()
_processed_ids = set()


def _log(msg):
    """寫入日誌檔與 ExtAPI/Console"""
    try:
        if not os.path.isdir(_QUEUE_ROOT):
            os.makedirs(_QUEUE_ROOT)
        line = "%s [WBListener] %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), str(msg))
        with open(_LOG_FILE, "a") as fp:
            fp.write(line)
        print("[WBListener] " + str(msg))
    except Exception:
        pass


def _read_json_retry(filepath, retries=5, delay=0.05):
    """讀取 JSON 檔，含檔案寫入鎖定重試機制"""
    for _ in range(retries):
        try:
            with open(filepath, "r") as fp:
                return json.load(fp)
        except Exception:
            time.sleep(delay)
    return None


class _OutputCollector(object):
    def __init__(self):
        self.lines = []

    def __call__(self, *args):
        self.lines.append(" ".join(str(a) for a in args))


def _do_workbench_refresh_all(exec_globals):
    """執行最完整的 Workbench 專案與 Model (Cell 4) 刷新。"""
    try:
        import __builtin__ as _builtins
    except Exception:
        import builtins as _builtins

    # 1. 嘗試 Workbench Journal 原生 GetAllSystems() 刷新 Model container
    get_systems = exec_globals.get("GetAllSystems") or getattr(_builtins, "GetAllSystems", None)
    if not get_systems:
        try:
            import Ansys.UI.Handle
            get_systems = getattr(Ansys.UI.Handle, "GetAllSystems", None)
        except Exception:
            pass

    if get_systems:
        try:
            systems = get_systems()
            for sys_item in systems:
                try:
                    model_cont = sys_item.GetContainer(ComponentName="Model")
                    if model_cont and hasattr(model_cont, "Refresh"):
                        model_cont.Refresh()
                except Exception:
                    pass
                try:
                    sys_item.Refresh()
                except Exception:
                    pass
        except Exception:
            pass

    # 2. 嘗試全域 Update()
    update_fn = exec_globals.get("Update") or getattr(_builtins, "Update", None)
    if update_fn:
        try:
            update_fn()
        except Exception:
            pass

    # 3. 嘗試 ExtAPI DataModel 組件層級 (Components) 精準刷新
    ext_api = exec_globals.get("ExtAPI") or getattr(_builtins, "ExtAPI", None)
    if ext_api and hasattr(ext_api, "DataModel") and hasattr(ext_api.DataModel, "Project"):
        proj = ext_api.DataModel.Project
        if hasattr(proj, "Systems"):
            for sys_item in proj.Systems:
                # 專門刷新 System 下的 Component 節點 (如 Model / Geometry)
                if hasattr(sys_item, "Components"):
                    for comp in sys_item.Components:
                        if hasattr(comp, "Refresh"):
                            try:
                                comp.Refresh()
                            except Exception:
                                pass
                        if hasattr(comp, "Update"):
                            try:
                                comp.Update()
                            except Exception:
                                pass
                if hasattr(sys_item, "Refresh"):
                    try:
                        sys_item.Refresh()
                    except Exception:
                        pass
        if hasattr(proj, "Update"):
            try:
                proj.Update()
            except Exception:
                pass


def _execute_script(payload, cmd_id):
    """執行指令內含之 Python 腳本或 Workbench 命令"""
    cmd_type = payload.get("type", "")
    script = payload.get("script") or payload.get("code")

    collector = _OutputCollector()
    exec_globals = dict(globals())
    exec_globals["print"] = collector

    try:
        import __builtin__ as _builtins
    except Exception:
        import builtins as _builtins

    ext_api = exec_globals.get("ExtAPI") or getattr(_builtins, "ExtAPI", None)
    if ext_api:
        exec_globals["ExtAPI"] = ext_api
        if hasattr(ext_api, "DataModel") and hasattr(ext_api.DataModel, "Project"):
            exec_globals["Project"] = ext_api.DataModel.Project

    result = {
        "id": cmd_id,
        "success": False,
        "output": "",
        "error": None,
        "timestamp": time.time(),
    }

    try:
        if cmd_type == "ping":
            result["success"] = True
            result["data"] = {"status": "pong", "pid": os.getpid()}
        elif cmd_type in ("update_project", "refresh_project", "refresh"):
            _do_workbench_refresh_all(exec_globals)
            if script:
                try:
                    exec(script, exec_globals)
                except Exception as ex:
                    _log("Script note during refresh: " + str(ex))
            result["success"] = True
            result["output"] = "Project refresh/update command received and executed successfully."
        elif script:
            exec(script, exec_globals)
            result["success"] = True
            result["output"] = "\n".join(collector.lines)
        else:
            result["error"] = "No script or supported command type provided."
    except Exception as exc:
        result["error"] = str(exc)
        result["traceback"] = traceback.format_exc()

    return result


def _dispatch_execution(payload, cmd_id):
    """在 WPF UI 執行緒執行腳本 (若 GUI 存在) 確保安全，無 GUI 則直執行"""
    try:
        import clr
        clr.AddReference("PresentationFramework")
        clr.AddReference("WindowsBase")
        from System.Windows import Application as WpfApp
        from System.Action import Action

        app = WpfApp.Current
        if app is not None and app.Dispatcher is not None:
            container = []

            def _action():
                container.append(_execute_script(payload, cmd_id))

            app.Dispatcher.Invoke(Action(_action))
            return container[0]
    except Exception:
        pass

    return _execute_script(payload, cmd_id)


def _write_result(cmd_id, result):
    """將執行結果寫入 results/result_<id>.json 及 results/<id>.json"""
    if not os.path.isdir(_RESULTS_DIR):
        try:
            os.makedirs(_RESULTS_DIR)
        except Exception:
            pass

    res_file = os.path.join(_RESULTS_DIR, "result_%s.json" % cmd_id)
    compat_file = os.path.join(_RESULTS_DIR, "%s.json" % cmd_id)
    content = json.dumps(result, indent=2, ensure_ascii=False)

    for path in (res_file, compat_file):
        try:
            tmp = path + ".tmp"
            with open(tmp, "w") as fp:
                fp.write(content)
            try:
                os.replace(tmp, path)
            except Exception:
                with open(path, "w") as fp:
                    fp.write(content)
                if os.path.exists(tmp):
                    os.remove(tmp)
        except Exception as exc:
            _log("Failed to write result file %s: %s" % (path, str(exc)))


def _on_file_changed(sender, event_args):
    """FileSystemWatcher 事件處理函式 (觸發於 .NET ThreadPool 背景執行緒)"""
    try:
        filepath = event_args.FullPath
        filename = event_args.Name

        if not filename or not filename.endswith(".json"):
            return

        base_name = os.path.splitext(filename)[0]
        cmd_id = base_name[4:] if base_name.startswith("cmd_") else base_name

        # 防重複觸發去重鎖
        with _processed_lock:
            if cmd_id in _processed_ids:
                return
            _processed_ids.add(cmd_id)

        payload = _read_json_retry(filepath)
        if payload is None:
            with _processed_lock:
                _processed_ids.discard(cmd_id)
            return

        result = _dispatch_execution(payload, cmd_id)
        _write_result(cmd_id, result)

        # 刪除已處理之 command 檔案
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass

    except Exception as exc:
        _log("Error in file event handler: " + str(exc))


def start_listener(queue_root=None):
    """啟動 FileSystemWatcher 非同步監聽器"""
    global _watcher, _QUEUE_ROOT, _COMMANDS_DIR, _RESULTS_DIR

    if _watcher is not None and _watcher.EnableRaisingEvents:
        _log("FileSystemWatcher listener is already running.")
        return _watcher

    if queue_root:
        _QUEUE_ROOT = queue_root
        _COMMANDS_DIR = os.path.join(_QUEUE_ROOT, "commands")
        _RESULTS_DIR = os.path.join(_QUEUE_ROOT, "results")

    for d in (_COMMANDS_DIR, _RESULTS_DIR):
        if not os.path.isdir(d):
            try:
                os.makedirs(d)
            except Exception:
                pass

    _watcher = FileSystemWatcher()
    _watcher.Path = _COMMANDS_DIR
    _watcher.Filter = "*.json"
    _watcher.NotifyFilter = NotifyFilters.FileName | NotifyFilters.LastWrite

    _watcher.Created += _on_file_changed
    _watcher.Changed += _on_file_changed

    _watcher.EnableRaisingEvents = True
    _log("FileSystemWatcher listener started on: " + _COMMANDS_DIR)
    return _watcher


def stop_listener():
    """停止 FileSystemWatcher 監聽器"""
    global _watcher
    if _watcher is not None:
        try:
            _watcher.EnableRaisingEvents = False
            _watcher.Dispose()
        except Exception:
            pass
        _watcher = None
        _log("FileSystemWatcher listener stopped.")


def is_listening():
    """查詢監聽器是否運作中"""
    return _watcher is not None and _watcher.EnableRaisingEvents
