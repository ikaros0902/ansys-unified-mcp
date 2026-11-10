# platform_instance_management_protocol protocol dictionary

- APIKB source key: `platform_instance_management_protocol`
- Package: `ansys-api-platform-instancemanagement 1.2.0`
- Interface: platform_instance_management gRPC protocol schema
- Snapshot: [`platform_instance_management_protocol_api.json`](../../platform_instance_management_protocol_api.json)
- Snapshot SHA-256: `3c60e55a03acc8667b8a606f57b33b2d18d4d914065eab52437a04848efd066f`

> This page describes the captured protobuf schema. It does not confirm product support, host compatibility, or runtime behavior.
> This snapshot records enum type names on fields. It does not list enum members.

## Services and RPC methods

### `ansys.api.platform.instancemanagement.v1.product_instance_manager_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `ProductInstanceManager` | `CreateInstance` | `(ansys.api.platform.instancemanagement.v1.CreateInstanceRequest) -> ansys.api.platform.instancemanagement.v1.Instance [client_streaming=False, server_streaming=False]` |
| `ProductInstanceManager` | `DeleteInstance` | `(ansys.api.platform.instancemanagement.v1.DeleteInstanceRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `ProductInstanceManager` | `ListInstances` | `(ansys.api.platform.instancemanagement.v1.ListInstancesRequest) -> ansys.api.platform.instancemanagement.v1.ListInstancesResponse [client_streaming=False, server_streaming=False]` |
| `ProductInstanceManager` | `GetInstance` | `(ansys.api.platform.instancemanagement.v1.GetInstanceRequest) -> ansys.api.platform.instancemanagement.v1.Instance [client_streaming=False, server_streaming=False]` |
| `ProductInstanceManager` | `ListDefinitions` | `(ansys.api.platform.instancemanagement.v1.ListDefinitionsRequest) -> ansys.api.platform.instancemanagement.v1.ListDefinitionsResponse [client_streaming=False, server_streaming=False]` |
| `ProductInstanceManager` | `GetDefinition` | `(ansys.api.platform.instancemanagement.v1.GetDefinitionRequest) -> ansys.api.platform.instancemanagement.v1.Definition [client_streaming=False, server_streaming=False]` |

## Messages and fields

### `ansys.api.platform.instancemanagement.v1.product_instance_manager_pb2`

| Message | Fields |
| --- | --- |
| `CreateInstanceRequest` | `instance: ansys.api.platform.instancemanagement.v1.Instance` (Protobuf field number 1; repeated=False)<br>`security_settings: ansys.api.platform.instancemanagement.v1.InstanceSecuritySettings` (Protobuf field number 2; repeated=False) |
| `Definition` | `name: string` (Protobuf field number 1; repeated=False)<br>`product_name: string` (Protobuf field number 2; repeated=False)<br>`product_version: string` (Protobuf field number 3; repeated=False)<br>`available_service_names: string` (Protobuf field number 4; repeated=True) |
| `DeleteInstanceRequest` | `name: string` (Protobuf field number 1; repeated=False) |
| `GetDefinitionRequest` | `name: string` (Protobuf field number 1; repeated=False) |
| `GetInstanceRequest` | `name: string` (Protobuf field number 1; repeated=False) |
| `Instance` | `name: string` (Protobuf field number 1; repeated=False)<br>`definition_name: string` (Protobuf field number 2; repeated=False)<br>`ready: bool` (Protobuf field number 3; repeated=False)<br>`status_message: string` (Protobuf field number 4; repeated=False)<br>`services: ansys.api.platform.instancemanagement.v1.Instance.ServicesEntry` (Protobuf field number 5; repeated=True) |
| `InstanceSecuritySettings` | `insecure: google.protobuf.Empty` (Protobuf field number 1; repeated=False)<br>`mtls: ansys.api.platform.instancemanagement.v1.MtlsSettings` (Protobuf field number 2; repeated=False)<br>`wnua: google.protobuf.Empty` (Protobuf field number 3; repeated=False)<br>`uds: ansys.api.platform.instancemanagement.v1.UdsSettings` (Protobuf field number 4; repeated=False) |
| `ListDefinitionsRequest` | `page_size: int32` (Protobuf field number 1; repeated=False)<br>`page_token: string` (Protobuf field number 2; repeated=False)<br>`product_name: string` (Protobuf field number 3; repeated=False)<br>`product_version: string` (Protobuf field number 4; repeated=False) |
| `ListDefinitionsResponse` | `definitions: ansys.api.platform.instancemanagement.v1.Definition` (Protobuf field number 1; repeated=True)<br>`next_page_token: string` (Protobuf field number 2; repeated=False) |
| `ListInstancesRequest` | `page_size: int32` (Protobuf field number 1; repeated=False)<br>`page_token: string` (Protobuf field number 2; repeated=False) |
| `ListInstancesResponse` | `instances: ansys.api.platform.instancemanagement.v1.Instance` (Protobuf field number 1; repeated=True)<br>`next_page_token: string` (Protobuf field number 2; repeated=False) |
| `MtlsCertificatePaths` | `server_key_path: string` (Protobuf field number 1; repeated=False)<br>`server_certificate_path: string` (Protobuf field number 2; repeated=False)<br>`ca_certificate_path: string` (Protobuf field number 3; repeated=False)<br>`client_key_path: string` (Protobuf field number 4; repeated=False)<br>`client_certificate_path: string` (Protobuf field number 5; repeated=False) |
| `MtlsClientInfo` | `ca_certificate_path: string` (Protobuf field number 1; repeated=False)<br>`client_certificate_path: string` (Protobuf field number 2; repeated=False)<br>`client_key_path: string` (Protobuf field number 3; repeated=False) |
| `MtlsSettings` | `certificates_directory: string` (Protobuf field number 1; repeated=False)<br>`certificate_paths: ansys.api.platform.instancemanagement.v1.MtlsCertificatePaths` (Protobuf field number 2; repeated=False) |
| `Service` | `uri: string` (Protobuf field number 1; repeated=False)<br>`headers: ansys.api.platform.instancemanagement.v1.Service.HeadersEntry` (Protobuf field number 2; repeated=True)<br>`security: ansys.api.platform.instancemanagement.v1.ServiceSecurityInfo` (Protobuf field number 3; repeated=False) |
| `ServiceSecurityInfo` | `insecure: google.protobuf.Empty` (Protobuf field number 1; repeated=False)<br>`mtls: ansys.api.platform.instancemanagement.v1.MtlsClientInfo` (Protobuf field number 2; repeated=False)<br>`wnua: google.protobuf.Empty` (Protobuf field number 3; repeated=False)<br>`uds: google.protobuf.Empty` (Protobuf field number 4; repeated=False) |
| `UdsSettings` | `socket_path: string` (Protobuf field number 1; repeated=False)<br>`socket_directory: string` (Protobuf field number 2; repeated=False)<br>`socket_identifier: string` (Protobuf field number 3; repeated=False) |

## Snapshot counts

- RPC methods: 6
- Protocol messages: 17
- Message fields: 48
