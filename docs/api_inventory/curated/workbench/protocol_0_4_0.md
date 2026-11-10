# Workbench gRPC 協定字典（ansys-api-workbench 0.4.0）

## 範圍與證據

此頁整理本機 `ansys-api-workbench 0.4.0` protobuf descriptor 中的 `WorkbenchService`。它描述 RPC 傳輸協定，不等同 `ansys-workbench-core` Python client API、Workbench scripting API 或支援承諾。

機器快照為 [workbench_protocol_api.json](../../workbench_protocol_api.json)。APIKB 來源鍵為 `workbench_protocol`。檔案 SHA-256、協定版本與欄位定義見快照。未連線 Workbench，未執行 RPC，也未確認伺服器版本相容性。

## RPC

| 方法 | Request → Response | 串流方向 |
| --- | --- | --- |
| `RunScript` | `RunScriptRequest` → `RunScriptResponse` | 單一 request，伺服器串流 response |
| `UploadFile` | `UploadFileRequest` → `UploadFileResponse` | client 串流 request，單一 response |
| `DownloadFile` | `DownloadFileRequest` → `DownloadFileResponse` | 單一 request，伺服器串流 response |

## 訊息欄位

| 訊息 | 欄位與型別 |
| --- | --- |
| `RunScriptRequest` | `content: string`, `log_level: LogLevel` |
| `RunScriptResponse` | `result: RunScriptResult`, `log: RunScriptLog` |
| `RunScriptResult` | `error: string`, `result: string` |
| `RunScriptLog` | `messages: repeated LogEntry` |
| `LogEntry` | `level: LogLevel`, `message: string` |
| `UploadFileRequest` | `file_name: string`, `file_content: bytes` |
| `UploadFileResponse` | `error: string`, `file_name: string` |
| `DownloadFileRequest` | `file_name: string` |
| `DownloadFileResponse` | `error: string`, `file_content: bytes`, `file_info: DownloadFileInfo` |
| `DownloadFileInfo` | `is_archive: bool`, `file_size: uint64` |

`LogLevel` 是協定列舉。此頁不推論錯誤處理、檔案路徑限制、執行權限或 API 安全語意。請查閱與伺服器相同版本的官方文件後再使用。
