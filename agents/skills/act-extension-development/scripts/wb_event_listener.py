# -*- coding: utf-8 -*-
"""
ACT Async FileSystemWatcher Event Listener for ANSYS Workbench / Mechanical.
"""
import os
import threading
from System.IO import FileSystemWatcher, NotifyFilters
from System.Windows import Application as WpfApp
from System import Action

class ACTAsyncEventListener(object):
    def __init__(self, watch_dir):
        self.watch_dir = watch_dir
        self.watcher = None
        self._processed_ids = set()
        self._lock = threading.Lock()
        
    def start_listening(self):
        if not os.path.exists(self.watch_dir):
            os.makedirs(self.watch_dir)
            
        self.watcher = FileSystemWatcher()
        self.watcher.Path = self.watch_dir
        self.watcher.Filter = "*.json"
        self.watcher.NotifyFilter = NotifyFilters.FileName | NotifyFilters.LastWrite
        self.watcher.Created += self._on_file_event
        self.watcher.Changed += self._on_file_event
        self.watcher.EnableRaisingEvents = True
        print("FileSystemWatcher 已啟動，監聽目錄: {}".format(self.watch_dir))

    def _on_file_event(self, sender, args):
        filepath = args.FullPath
        with self._lock:
            if filepath in self._processed_ids:
                return
            self._processed_ids.add(filepath)
            
        # WPF Dispatcher 安全跨執行緒呼叫
        app = WpfApp.Current
        if app is not None and app.Dispatcher is not None:
            app.Dispatcher.Invoke(Action(lambda: self.process_command(filepath)))
        else:
            self.process_command(filepath)

    def process_command(self, filepath):
        print("處理 ACT 命令檔案: {}".format(filepath))

if __name__ == "__main__":
    listener = ACTAsyncEventListener("C:/tmp/act_commands")
    listener.start_listening()
