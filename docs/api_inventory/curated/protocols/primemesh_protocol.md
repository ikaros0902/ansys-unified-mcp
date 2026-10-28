# primemesh_protocol protocol dictionary

- APIKB source key: `primemesh_protocol`
- Package: `ansys-api-meshing-prime 0.2.0`
- Interface: primemesh gRPC protocol schema
- Snapshot: [`primemesh_protocol_api.json`](../../primemesh_protocol_api.json)
- Snapshot SHA-256: `4a1844abc5357a970330abbc138157c0c063084bbf76f42c68ba28bcff09d0f8`

> This page describes the captured protobuf schema. It does not confirm product support, host compatibility, or runtime behavior.
> This snapshot records enum type names on fields. It does not list enum members.

## Services and RPC methods

### `ansys.api.meshing.prime.v1.prime_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Prime` | `ServeJson` | `(ansys.api.meshing.prime.v1.StringMessage) -> ansys.api.meshing.prime.v1.StringMessage [client_streaming=True, server_streaming=True]` |
| `Prime` | `GetParamDefaultJson` | `(ansys.api.meshing.prime.v1.StringMessage) -> ansys.api.meshing.prime.v1.StringMessage [client_streaming=True, server_streaming=True]` |
| `Prime` | `RunOnServer` | `(ansys.api.meshing.prime.v1.StringMessage) -> ansys.api.meshing.prime.v1.StringMessage [client_streaming=True, server_streaming=True]` |
| `Prime` | `ServeJsonBinary` | `(ansys.api.meshing.prime.v1.BinaryMessage) -> ansys.api.meshing.prime.v1.BinaryMessage [client_streaming=True, server_streaming=True]` |
| `Prime` | `Initialize` | `(ansys.api.meshing.prime.v1.InitializeRequest) -> ansys.api.meshing.prime.v1.InitializeResponse [client_streaming=False, server_streaming=False]` |
| `Prime` | `ServerCommand` | `(ansys.api.meshing.prime.v1.StringMessage) -> ansys.api.meshing.prime.v1.StringMessage [client_streaming=True, server_streaming=True]` |
| `Prime` | `Finalize` | `(ansys.api.meshing.prime.v1.FinalizeRequest) -> ansys.api.meshing.prime.v1.FinalizeResponse [client_streaming=False, server_streaming=False]` |

## Messages and fields

### `ansys.api.meshing.prime.v1.prime_pb2`

| Message | Fields |
| --- | --- |
| `BinaryJsonContent` | `data: bytes` (Protobuf field number 1; repeated=False) |
| `BinaryMessage` | `model: ansys.api.meshing.prime.v1.Model` (Protobuf field number 1; repeated=False)<br>`content: ansys.api.meshing.prime.v1.BinaryJsonContent` (Protobuf field number 2; repeated=False)<br>`completion_token: ansys.api.meshing.prime.v1.MessageCompletionToken` (Protobuf field number 3; repeated=False) |
| `FinalizeRequest` | — |
| `FinalizeResponse` | `data: string` (Protobuf field number 1; repeated=False) |
| `InitializeRequest` | — |
| `InitializeResponse` | `data: string` (Protobuf field number 1; repeated=False) |
| `MessageCompletionToken` | — |
| `Model` | `object_id: int32` (Protobuf field number 1; repeated=False) |
| `StringJsonContent` | `data: string` (Protobuf field number 1; repeated=False) |
| `StringMessage` | `model: ansys.api.meshing.prime.v1.Model` (Protobuf field number 1; repeated=False)<br>`content: ansys.api.meshing.prime.v1.StringJsonContent` (Protobuf field number 2; repeated=False)<br>`completion_token: ansys.api.meshing.prime.v1.MessageCompletionToken` (Protobuf field number 3; repeated=False) |

## Snapshot counts

- RPC methods: 7
- Protocol messages: 10
- Message fields: 11
