# mechanical_protocol protocol dictionary

- APIKB source key: `mechanical_protocol`
- Package: `ansys-api-mechanical 0.1.4`
- Interface: mechanical gRPC protocol schema
- Snapshot: [`mechanical_protocol_api.json`](../../mechanical_protocol_api.json)
- Snapshot SHA-256: `a664f0066e5540369e8f0933dabec63b27d2621d955bc9cff57dc33bd5886482`

> This page describes the captured protobuf schema. It does not confirm product support, host compatibility, or runtime behavior.
> This snapshot records enum type names on fields. It does not list enum members.

## Services and RPC methods

### `ansys.api.mechanical.v0.mechanical_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `MechanicalService` | `RunJScript` | `(ansys.api.mechanical.scripting.v1.RunScriptRequest) -> ansys.api.mechanical.scripting.v1.RunScriptResponse [client_streaming=False, server_streaming=True]` |
| `MechanicalService` | `RunPythonScript` | `(ansys.api.mechanical.scripting.v1.RunScriptRequest) -> ansys.api.mechanical.scripting.v1.RunScriptResponse [client_streaming=False, server_streaming=True]` |
| `MechanicalService` | `Shutdown` | `(ansys.api.mechanical.scripting.v1.ShutdownRequest) -> ansys.api.mechanical.scripting.v1.ShutdownResponse [client_streaming=False, server_streaming=False]` |
| `MechanicalService` | `UploadFile` | `(ansys.api.mechanical.scripting.v1.FileUploadRequest) -> ansys.api.mechanical.scripting.v1.FileUploadResponse [client_streaming=True, server_streaming=False]` |
| `MechanicalService` | `DownloadFile` | `(ansys.api.mechanical.scripting.v1.FileDownloadRequest) -> ansys.api.mechanical.scripting.v1.FileDownloadResponse [client_streaming=False, server_streaming=True]` |

## Messages and fields

### `ansys.api.mechanical.v0.mechanical_pb2`

| Message | Fields |
| --- | --- |
| `Chunk` | `payload: bytes` (Protobuf field number 1; repeated=False)<br>`size: int64` (Protobuf field number 2; repeated=False) |
| `FileDownloadRequest` | `file_path: string` (Protobuf field number 1; repeated=False)<br>`chunk_size: int64` (Protobuf field number 2; repeated=False) |
| `FileDownloadResponse` | `chunk: ansys.api.mechanical.scripting.v1.Chunk` (Protobuf field number 1; repeated=False)<br>`file_size: int64` (Protobuf field number 2; repeated=False) |
| `FileUploadRequest` | `file_name: string` (Protobuf field number 1; repeated=False)<br>`file_location: string` (Protobuf field number 2; repeated=False)<br>`chunk: ansys.api.mechanical.scripting.v1.Chunk` (Protobuf field number 3; repeated=False) |
| `FileUploadResponse` | `is_ok: bool` (Protobuf field number 1; repeated=False) |
| `RunScriptRequest` | `script_code: string` (Protobuf field number 1; repeated=False)<br>`enable_logging: bool` (Protobuf field number 2; repeated=False)<br>`logger_severity: ansys.api.mechanical.scripting.v1.LoggerSeverity` (Protobuf field number 3; repeated=False)<br>`progress_interval: int32` (Protobuf field number 4; repeated=False)<br>`python_behavior: int32` (Protobuf field number 5; repeated=False) |
| `RunScriptResponse` | `script_result: string` (Protobuf field number 1; repeated=False)<br>`log_info: string` (Protobuf field number 2; repeated=False) |
| `ShutdownRequest` | `force_exit: bool` (Protobuf field number 1; repeated=False) |
| `ShutdownResponse` | — |

## Snapshot counts

- RPC methods: 5
- Protocol messages: 9
- Message fields: 18
