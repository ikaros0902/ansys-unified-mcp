# -*- coding: utf-8 -*-
"""
FileSystemWatcher 非同步事件監聽模組 (IronPython / .NET)
使用 System.IO.FileSystemWatcher 實現 0% CPU 佔用非同步事件監聽，
並透過 WPF Dispatcher 安全跨執行緒呼叫 ANSYS ExtAPI / Mechanical 主執行緒。
"""
import os
import threading
try:
    import clr
    clr.AddReference("System")
    clr.AddReference("PresentationFramework")
    from System.IO import FileSystemWatcher, NotifyFilters
    from System.Windows import Application as WpfApp
    from System import Action
except Exception as e:
    print("注意: 僅在 .NET / IronPython 環境下完全載入 ({}".format(e))

class SafeFileSystemListener(object):
    def __init__(self, watch_dir, filter_pattern="*.json"):
        self.watch_dir = watch_dir
        self.filter_pattern = filter_pattern
        self.watcher = None
        self._processed_lock = threading.Lock()
        self._processed_ids = set()

    def start(self, callback_fn):
        """啟動非同步檔案監聽"""
        if not os.path.exists(self.watch_dir):
            os.makedirs(self.watch_dir)
            
        self.watcher = FileSystemWatcher()
        self.watcher.Path = self.watch_dir
        self.watcher.Filter = self.filter_pattern
        self.watcher.NotifyFilter = NotifyFilters.FileName | NotifyFilters.LastWrite
        
        def _on_event(sender, args):
            file_path = args.FullPath
            # 防重複觸發與鎖護
            with self._processed_lock:
                if file_path in self._processed_ids:
                    return
                self._processed_ids.add(file_path)
            
            # WPF Dispatcher 安全回到 UI / ExtAPI 主執行緒
            try:
                app = WpfApp.Current
                if app is not None and app.Dispatcher is not None:
                    app.Dispatcher.Invoke(Action(lambda: callback_fn(file_path)))
                else:
                    callback_fn(file_path)
            except Exception as ex:
                print("Dispatcher 執行異常: {}".format(ex))

        self.watcher.Created += _on_event
        self.watcher.Changed += _on_event
        self.watcher.EnableRaisingEvents = True
        print("FileSystemWatcher 已啟動，監控目錄: {}".format(self.watch_dir))

    def stop(self):
        if self.watcher is not None:
            self.watcher.EnableRaisingEvents = False
            self.watcher.Dispose()
            print("FileSystemWatcher 已停止。")

if __name__ == "__main__":
    print("FileSystemWatcher 安全非同步範例模組。")
