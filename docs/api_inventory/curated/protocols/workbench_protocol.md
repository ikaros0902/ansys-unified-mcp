# workbench_protocol protocol dictionary

- APIKB source key: `workbench_protocol`
- Package: `ansys-api-workbench 0.4.0`
- Interface: Workbench gRPC protocol schema
- Snapshot: [`workbench_protocol_api.json`](../../workbench_protocol_api.json)
- Snapshot SHA-256: `c54ebe9456614a7669faa48ea1432aad8523e17c0e2c90c1fd839cfd276f41ae`

> This page describes the captured protobuf schema. It does not confirm product support, host compatibility, or runtime behavior.
> This snapshot records enum type names on fields. It does not list enum members.

## Services and RPC methods

### `ansys.api.workbench.v0.workbench_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `WorkbenchService` | `RunScript` | `(ansys.api.workbench.v0.RunScriptRequest) -> ansys.api.workbench.v0.RunScriptResponse [client_streaming=False, server_streaming=True]` |
| `WorkbenchService` | `UploadFile` | `(ansys.api.workbench.v0.UploadFileRequest) -> ansys.api.workbench.v0.UploadFileResponse [client_streaming=True, server_streaming=False]` |
| `WorkbenchService` | `DownloadFile` | `(ansys.api.workbench.v0.DownloadFileRequest) -> ansys.api.workbench.v0.DownloadFileResponse [client_streaming=False, server_streaming=True]` |

## Messages and fields

### `ansys.api.workbench.v0.workbench_pb2`

| Message | Fields |
| --- | --- |
| `DownloadFileInfo` | `is_archive: bool` (Protobuf field number 1; repeated=False)<br>`file_size: uint64` (Protobuf field number 2; repeated=False) |
| `DownloadFileRequest` | `file_name: string` (Protobuf field number 1; repeated=False) |
| `DownloadFileResponse` | `error: string` (Protobuf field number 1; repeated=False)<br>`file_content: bytes` (Protobuf field number 2; repeated=False)<br>`file_info: ansys.api.workbench.v0.DownloadFileInfo` (Protobuf field number 3; repeated=False) |
| `LogEntry` | `level: ansys.api.workbench.v0.LogLevel` (Protobuf field number 1; repeated=False)<br>`message: string` (Protobuf field number 2; repeated=False) |
| `RunScriptLog` | `messages: ansys.api.workbench.v0.LogEntry` (Protobuf field number 1; repeated=True) |
| `RunScriptRequest` | `content: string` (Protobuf field number 1; repeated=False)<br>`log_level: ansys.api.workbench.v0.LogLevel` (Protobuf field number 2; repeated=False) |
| `RunScriptResponse` | `result: ansys.api.workbench.v0.RunScriptResult` (Protobuf field number 1; repeated=False)<br>`log: ansys.api.workbench.v0.RunScriptLog` (Protobuf field number 2; repeated=False) |
| `RunScriptResult` | `error: string` (Protobuf field number 1; repeated=False)<br>`result: string` (Protobuf field number 2; repeated=False) |
| `UploadFileRequest` | `file_name: string` (Protobuf field number 1; repeated=False)<br>`file_content: bytes` (Protobuf field number 2; repeated=False) |
| `UploadFileResponse` | `error: string` (Protobuf field number 1; repeated=False)<br>`file_name: string` (Protobuf field number 2; repeated=False) |

## Snapshot counts

- RPC methods: 3
- Protocol messages: 10
- Message fields: 19
