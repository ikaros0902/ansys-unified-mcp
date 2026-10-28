# Workbench Python SDK 快照（0.14.0）

## 來源與範圍

- Distribution：`ansys-workbench-core 0.14.0`，來源為本機 repo `.venv`。
- 模組：`ansys.workbench.core.public_api`。
- 本頁記錄該模組匯出的四個 callable 的 Python 反射簽名。
- 本頁不是完整 SDK API 快照。沒有列出類別方法、其他子模組、型別註記或文件正文。
- 此 SDK 版本不等於 ANSYS Workbench 產品 release。未啟動 Workbench，也未驗證連線或執行行為。
- 公開支援狀態未分類。安裝套件匯出名稱不代表 Ansys 對外支援承諾。

## Callable

| 名稱 | 0.14.0 反射簽名 |
| --- | --- |
| `connect_workbench` | `(port, client_workdir=None, host=None, security='mtls')` |
| `launch_workbench` | `(show_gui=True, version=None, client_workdir=None, server_workdir=None, port=-1, use_insecure_connection=False, host=None, username=None, password=None)` |
| `ClientWrapper` | `(port, client_workdir=None, host=None, security='mtls')` |
| `LaunchWorkbench` | `(show_gui=True, version=None, client_workdir=None, server_workdir=None, port=-1, use_insecure_connection=False, host=None, username=None, password=None)` |
| `Launcher` | `()` |
| `WorkbenchClient` | `(local_workdir, server_host, server_port, server_security)` |

以上名稱來自 `ansys.workbench.core.public_api` 的匯出。反射簽名尚未逐一對照該 SDK 版本的官方文件。

## 可追溯性

本快照由本機安裝套件的 `public_api.py` 與 package `__init__.py` 反射讀取。快照已登錄 APIKB，來源鍵為 `workbench`。重建工具為 `scripts/api_extraction/extract_workbench_api.py`。輸出保存套件原始檔雜湊與反射範圍。Workbench gRPC 傳輸協定另見[協定字典](./protocol_0_4_0.md)，不可與 Python SDK 簽名混為一談。
