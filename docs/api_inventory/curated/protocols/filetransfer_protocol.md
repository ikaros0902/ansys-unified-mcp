# filetransfer_protocol protocol dictionary

- APIKB source key: `filetransfer_protocol`
- Package: `ansys-api-tools-filetransfer 0.2.0`
- Interface: filetransfer gRPC protocol schema
- Snapshot: [`filetransfer_protocol_api.json`](../../filetransfer_protocol_api.json)
- Snapshot SHA-256: `e4bd4b9b709529cafce1a34fc80ba7b5d42442b6995061c38a475447fdaeeb01`

> This page describes the captured protobuf schema. It does not confirm product support, host compatibility, or runtime behavior.
> This snapshot records enum type names on fields. It does not list enum members.

## Services and RPC methods

### `ansys.api.tools.filetransfer.v1.file_transfer_service_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `FileTransferService` | `DownloadFile` | `(ansys.api.tools.filetransfer.v1.DownloadFileRequest) -> ansys.api.tools.filetransfer.v1.DownloadFileResponse [client_streaming=True, server_streaming=True]` |
| `FileTransferService` | `UploadFile` | `(ansys.api.tools.filetransfer.v1.UploadFileRequest) -> ansys.api.tools.filetransfer.v1.UploadFileResponse [client_streaming=True, server_streaming=True]` |

## Messages and fields

### `ansys.api.tools.filetransfer.v1.file_transfer_service_pb2`

| Message | Fields |
| --- | --- |
| `DownloadFileRequest` | `progress: ansys.api.tools.filetransfer.v1.ProgressRequest` (Protobuf field number 1; repeated=False)<br>`initialize: ansys.api.tools.filetransfer.v1.DownloadFileRequest.Initialize` (Protobuf field number 2; repeated=False)<br>`receive_data: ansys.api.tools.filetransfer.v1.DownloadFileRequest.ReceiveData` (Protobuf field number 3; repeated=False)<br>`finalize: ansys.api.tools.filetransfer.v1.DownloadFileRequest.Finalize` (Protobuf field number 4; repeated=False) |
| `DownloadFileResponse` | `progress: ansys.api.tools.filetransfer.v1.ProgressResponse` (Protobuf field number 1; repeated=False)<br>`file_info: ansys.api.tools.filetransfer.v1.FileInfo` (Protobuf field number 2; repeated=False)<br>`file_data: ansys.api.tools.filetransfer.v1.FileChunk` (Protobuf field number 3; repeated=False) |
| `FileChunk` | `offset: int64` (Protobuf field number 1; repeated=False)<br>`data: bytes` (Protobuf field number 2; repeated=False) |
| `FileInfo` | `name: string` (Protobuf field number 1; repeated=False)<br>`size: int64` (Protobuf field number 2; repeated=False)<br>`sha1: ansys.api.tools.filetransfer.v1.SHA1` (Protobuf field number 3; repeated=False) |
| `ProgressRequest` | `interrupt: bool` (Protobuf field number 1; repeated=False) |
| `ProgressResponse` | `state: int32` (Protobuf field number 1; repeated=False) |
| `SHA1` | `hex_digest: string` (Protobuf field number 1; repeated=False) |
| `UploadFileRequest` | `progress: ansys.api.tools.filetransfer.v1.ProgressRequest` (Protobuf field number 1; repeated=False)<br>`initialize: ansys.api.tools.filetransfer.v1.UploadFileRequest.Initialize` (Protobuf field number 2; repeated=False)<br>`send_data: ansys.api.tools.filetransfer.v1.UploadFileRequest.SendData` (Protobuf field number 3; repeated=False)<br>`finalize: ansys.api.tools.filetransfer.v1.UploadFileRequest.Finalize` (Protobuf field number 4; repeated=False) |
| `UploadFileResponse` | `progress: ansys.api.tools.filetransfer.v1.ProgressResponse` (Protobuf field number 1; repeated=False) |

## Snapshot counts

- RPC methods: 2
- Protocol messages: 9
- Message fields: 20
