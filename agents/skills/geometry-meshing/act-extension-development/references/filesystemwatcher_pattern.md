# FileSystemWatcher 非同步事件架構 (filesystemwatcher_pattern.md)

本手冊說明如何使用 .NET `System.IO.FileSystemWatcher` 替代傳統 `while True: time.sleep()` 輪詢，實現 0% CPU 佔用的非阻塞檔案 IPC 通訊。

---

## 1. 核心實作模式

```python
from System.IO import FileSystemWatcher, NotifyFilters
import threading

watcher = FileSystemWatcher()
watcher.Path = commands_dir
watcher.Filter = "*.json"
watcher.NotifyFilter = NotifyFilters.FileName | NotifyFilters.LastWrite
watcher.Created += on_file_changed
watcher.Changed += on_file_changed
watcher.EnableRaisingEvents = True
```

---

## 2. WPF Dispatcher 安全跨執行緒呼叫

`FileSystemWatcher` 事件在 .NET ThreadPool 執行緒觸發，若需操作 UI 或 ExtAPI，必須透過 WPF Dispatcher 切換回主執行緒：

```python
from System.Windows import Application as WpfApp

app = WpfApp.Current
if app is not None and app.Dispatcher is not None:
    app.Dispatcher.Invoke(Action(_action))
```

---

## 3. 去重加鎖防護 (Anti-duplicate Trigger)

防止作業系統觸發多次檔案變更事件：

```python
_processed_lock = threading.Lock()
_processed_ids = set()

with _processed_lock:
    if cmd_id in _processed_ids:
        return
    _processed_ids.add(cmd_id)
```
