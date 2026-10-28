# dbu_protocol protocol dictionary

- APIKB source key: `dbu_protocol`
- Package: `ansys-api-dbu 0.3.29`
- Interface: dbu gRPC protocol schema
- Snapshot: [`dbu_protocol_api.json`](../../dbu_protocol_api.json)
- Snapshot SHA-256: `251f5ede4e2c219f0f20df40986aa955ec52466bd63bdfb5e5586158620203f1`

> This page describes the captured protobuf schema. It does not confirm product support, host compatibility, or runtime behavior.
> This snapshot records enum type names on fields. It does not list enum members.

## Services and RPC methods

### `ansys.api.dbu.v0.admin_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Admin` | `GetLogs` | `(ansys.api.dbu.v0.admin.LogsRequest) -> ansys.api.dbu.v0.admin.LogsResponse [client_streaming=False, server_streaming=True]` |
| `Admin` | `Health` | `(google.protobuf.Empty) -> ansys.api.dbu.v0.admin.HealthResponse [client_streaming=False, server_streaming=False]` |
| `Admin` | `Shutdown` | `(google.protobuf.Empty) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Admin` | `StatusInfo` | `(google.protobuf.Empty) -> ansys.api.dbu.v0.admin.StatusInfoResponse [client_streaming=False, server_streaming=False]` |
| `Admin` | `SetApplicationTitle` | `(ansys.api.dbu.v0.admin.SetApplicationTitleRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Admin` | `CloseApplication` | `(google.protobuf.Empty) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Admin` | `GetBackend` | `(google.protobuf.Empty) -> ansys.api.dbu.v0.admin.GetBackendResponse [client_streaming=False, server_streaming=False]` |
| `Admin` | `ApplicationStarted` | `(google.protobuf.Empty) -> ansys.api.dbu.v0.admin.ApplicationStartedResponse [client_streaming=False, server_streaming=False]` |
| `Admin` | `SetMonikersCompressionMethod` | `(ansys.api.dbu.v0.admin.MonikerCompressionMethodMessage) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Admin` | `GetMonikersCompressionMethod` | `(google.protobuf.Empty) -> ansys.api.dbu.v0.admin.MonikerCompressionMethodMessage [client_streaming=False, server_streaming=False]` |

### `ansys.api.dbu.v0.dbuapi_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `DbuApi` | `SetVersion` | `(ansys.api.dbu.v0.dbuapi.SetVersionRequest) -> ansys.api.dbu.v0.dbuapi.SetVersionResponse [client_streaming=False, server_streaming=False]` |
| `DbuApi` | `GetVersion` | `(google.protobuf.Empty) -> ansys.api.dbu.v0.dbuapi.GetVersionResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.dbu.v0.dbuapplication_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `DbuApplication` | `RunScriptFile` | `(ansys.api.dbu.v0.dbuapplication.RunScriptFileRequest) -> ansys.api.dbu.v0.dbuapplication.RunScriptFileResponse [client_streaming=False, server_streaming=False]` |
| `DbuApplication` | `RunNotTrackedScriptFile` | `(ansys.api.dbu.v0.dbuapplication.RunScriptFileRequest) -> ansys.api.dbu.v0.dbuapplication.RunScriptFileResponse [client_streaming=False, server_streaming=False]` |
| `DbuApplication` | `RunScript` | `(ansys.api.dbu.v0.dbuapplication.RunScriptRequest) -> ansys.api.dbu.v0.dbuapplication.RunScriptResponse [client_streaming=False, server_streaming=False]` |
| `DbuApplication` | `RunCommand` | `(ansys.api.dbu.v0.dbuapplication.RunCommandRequest) -> ansys.api.dbu.v0.dbuapplication.RunCommandResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.dbu.v0.designs_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Designs` | `Get` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.dbu.v0.Design [client_streaming=False, server_streaming=False]` |
| `Designs` | `GetAll` | `(google.protobuf.Empty) -> ansys.api.dbu.v0.designs.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `Designs` | `GetActive` | `(google.protobuf.Empty) -> ansys.api.dbu.v0.Design [client_streaming=False, server_streaming=False]` |
| `Designs` | `PutActive` | `(ansys.api.dbu.v0.EntityIdentifier) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Designs` | `Open` | `(ansys.api.dbu.v0.designs.OpenRequest) -> ansys.api.dbu.v0.EntityIdentifier [client_streaming=False, server_streaming=False]` |
| `Designs` | `New` | `(ansys.api.dbu.v0.designs.NewRequest) -> ansys.api.dbu.v0.Design [client_streaming=False, server_streaming=False]` |
| `Designs` | `Close` | `(ansys.api.dbu.v0.EntityIdentifier) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Designs` | `Save` | `(ansys.api.dbu.v0.EntityIdentifier) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Designs` | `SaveAs` | `(ansys.api.dbu.v0.designs.SaveAsRequest) -> ansys.api.dbu.v0.EntityIdentifier [client_streaming=False, server_streaming=False]` |
| `Designs` | `Insert` | `(ansys.api.dbu.v0.designs.InsertRequest) -> ansys.api.dbu.v0.EntityIdentifier [client_streaming=False, server_streaming=False]` |
| `Designs` | `GetAsJson` | `(ansys.api.dbu.v0.designs.GetAsJsonRequest) -> ansys.api.dbu.v0.designs.GetAsJsonResponse [client_streaming=False, server_streaming=False]` |
| `Designs` | `CopyReferencedDocuments` | `(ansys.api.dbu.v0.designs.CopyReferencedDocumentsRequest) -> ansys.api.dbu.v0.RequestResult [client_streaming=False, server_streaming=False]` |
| `Designs` | `SaveWithoutResults` | `(google.protobuf.Empty) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Designs` | `OpenCloudFileFromUrl` | `(ansys.api.dbu.v0.designs.OpenCloudFileFromUrlRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Designs` | `SaveCloudFile` | `(google.protobuf.Empty) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Designs` | `DownloadExportFile` | `(ansys.api.dbu.v0.designs.DownloadExportFileRequest) -> ansys.api.dbu.v0.designs.DownloadExportFileResponse [client_streaming=False, server_streaming=False]` |
| `Designs` | `StreamDownloadExportFile` | `(ansys.api.dbu.v0.designs.DownloadExportFileRequest) -> ansys.api.dbu.v0.designs.DownloadExportFileResponse [client_streaming=False, server_streaming=True]` |
| `Designs` | `StreamDesignTessellation` | `(ansys.api.dbu.v0.designs.DesignTessellationRequest) -> ansys.api.dbu.v0.designs.DesignTessellationResponse [client_streaming=False, server_streaming=True]` |

### `ansys.api.dbu.v0.drivingdimensions_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `DrivingDimensions` | `Get` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.dbu.v0.DrivingDimension [client_streaming=False, server_streaming=False]` |
| `DrivingDimensions` | `GetAll` | `(ansys.api.dbu.v0.drivingdimensions.GetAllRequest) -> ansys.api.dbu.v0.drivingdimensions.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `DrivingDimensions` | `Update` | `(ansys.api.dbu.v0.drivingdimensions.UpdateRequest) -> ansys.api.dbu.v0.DrivingDimension [client_streaming=False, server_streaming=False]` |
| `DrivingDimensions` | `UpdateParameter` | `(ansys.api.dbu.v0.drivingdimensions.UpdateRequest) -> ansys.api.dbu.v0.drivingdimensions.UpdateResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.dbu.v0.sessionmanager_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `SessionManager` | `Start` | `(ansys.api.dbu.v0.sessionmanager.StartRequest) -> ansys.api.dbu.v0.sessionmanager.StartResponse [client_streaming=False, server_streaming=False]` |
| `SessionManager` | `Stop` | `(ansys.api.dbu.v0.Session) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |

### `ansys.api.dbu.v0.windows_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Windows` | `GetImage` | `(ansys.api.dbu.v0.windows.GetImageRequest) -> ansys.api.dbu.v0.StreamPackage [client_streaming=False, server_streaming=True]` |
| `Windows` | `SetView` | `(ansys.api.dbu.v0.windows.SetViewRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |

## Messages and fields

### `ansys.api.dbu.v0.admin_pb2`

| Message | Fields |
| --- | --- |
| `ApplicationStartedResponse` | `is_startup_complete: bool` (Protobuf field number 1; repeated=False) |
| `GetBackendResponse` | `type: ansys.api.dbu.v0.admin.BackendType` (Protobuf field number 1; repeated=False)<br>`version: ansys.api.dbu.v0.VersionIdentifier` (Protobuf field number 2; repeated=False)<br>`backend_version_info: string` (Protobuf field number 3; repeated=False)<br>`additional_build_info: ansys.api.dbu.v0.admin.GetBackendResponse.AdditionalBuildInfoEntry` (Protobuf field number 4; repeated=True) |
| `HealthResponse` | `message: string` (Protobuf field number 1; repeated=False) |
| `LogsRequest` | `target: ansys.api.dbu.v0.admin.LogsTarget` (Protobuf field number 1; repeated=False)<br>`null_path: google.protobuf.NullValue` (Protobuf field number 2; repeated=False)<br>`target_path: string` (Protobuf field number 3; repeated=False)<br>`period_type: ansys.api.dbu.v0.admin.PeriodType` (Protobuf field number 4; repeated=False)<br>`null_period: google.protobuf.NullValue` (Protobuf field number 5; repeated=False)<br>`logs_period: google.protobuf.Timestamp` (Protobuf field number 6; repeated=False) |
| `LogsResponse` | `relative_path: string` (Protobuf field number 1; repeated=False)<br>`log_name: string` (Protobuf field number 2; repeated=False)<br>`log_chunk: bytes` (Protobuf field number 3; repeated=False) |
| `MonikerCompressionMethodMessage` | `method: ansys.api.dbu.v0.MonikerCompressionMethod` (Protobuf field number 1; repeated=False) |
| `SetApplicationTitleRequest` | `title: string` (Protobuf field number 1; repeated=False) |
| `StatusInfoResponse` | `touch_time: string` (Protobuf field number 1; repeated=False)<br>`application_version: string` (Protobuf field number 2; repeated=False)<br>`embedded_api_version: string` (Protobuf field number 3; repeated=False) |

### `ansys.api.dbu.v0.dbuapi_pb2`

| Message | Fields |
| --- | --- |
| `GetVersionResponse` | `version: ansys.api.dbu.v0.dbuapi.ApiVersion` (Protobuf field number 1; repeated=False) |
| `SetVersionRequest` | `version: ansys.api.dbu.v0.dbuapi.ApiVersion` (Protobuf field number 1; repeated=False) |
| `SetVersionResponse` | `result: string` (Protobuf field number 1; repeated=False) |

### `ansys.api.dbu.v0.dbuapplication_pb2`

| Message | Fields |
| --- | --- |
| `RunCommandRequest` | `command: string` (Protobuf field number 1; repeated=False)<br>`data: string` (Protobuf field number 2; repeated=False) |
| `RunCommandResponse` | `data: string` (Protobuf field number 1; repeated=False) |
| `RunScriptFileRequest` | `script_path: string` (Protobuf field number 1; repeated=False)<br>`script_args: ansys.api.dbu.v0.dbuapplication.RunScriptFileRequest.ScriptArgsEntry` (Protobuf field number 2; repeated=True)<br>`api_version: int32` (Protobuf field number 3; repeated=False)<br>`script_type: ansys.api.dbu.v0.dbuapplication.RunScriptType` (Protobuf field number 4; repeated=False) |
| `RunScriptFileResponse` | `success: bool` (Protobuf field number 1; repeated=False)<br>`message: string` (Protobuf field number 2; repeated=False)<br>`values: ansys.api.dbu.v0.dbuapplication.RunScriptFileResponse.ValuesEntry` (Protobuf field number 3; repeated=True) |
| `RunScriptRequest` | `script: string` (Protobuf field number 1; repeated=False)<br>`api_version: int32` (Protobuf field number 2; repeated=False) |
| `RunScriptResponse` | `script_result: bool` (Protobuf field number 1; repeated=False) |

### `ansys.api.dbu.v0.dbumodels_pb2`

| Message | Fields |
| --- | --- |
| `Design` | `id: string` (Protobuf field number 1; repeated=False)<br>`is_complete: bool` (Protobuf field number 2; repeated=False)<br>`is_locked: bool` (Protobuf field number 3; repeated=False)<br>`is_modified: bool` (Protobuf field number 4; repeated=False)<br>`is_removed: bool` (Protobuf field number 5; repeated=False)<br>`main_part: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 6; repeated=False)<br>`main_part_displays_file_name: bool` (Protobuf field number 7; repeated=False)<br>`path: string` (Protobuf field number 10; repeated=False)<br>`name: string` (Protobuf field number 11; repeated=False) |
| `DrivingDimension` | `id: string` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`dimension_type: ansys.api.dbu.v0.DimensionType` (Protobuf field number 3; repeated=False)<br>`dimension_value: double` (Protobuf field number 4; repeated=False) |
| `EdgeTessellation` | `vertices: ansys.api.dbu.v0.Point` (Protobuf field number 1; repeated=True) |
| `EntityIdentifier` | `id: string` (Protobuf field number 1; repeated=False) |
| `ImportOptionDefinition` | `bool_option: bool` (Protobuf field number 1; repeated=False)<br>`string_option: string` (Protobuf field number 2; repeated=False) |
| `PhysicsEntityIdentifier` | `guid_as_string: string` (Protobuf field number 1; repeated=False) |
| `Point` | `x: double` (Protobuf field number 1; repeated=False)<br>`y: double` (Protobuf field number 2; repeated=False)<br>`z: double` (Protobuf field number 3; repeated=False) |
| `RequestResult` | `success: bool` (Protobuf field number 1; repeated=False)<br>`error_message: string` (Protobuf field number 2; repeated=False)<br>`internal_error: string` (Protobuf field number 3; repeated=False) |
| `Tessellation` | `vertices: double` (Protobuf field number 1; repeated=True)<br>`faces: int32` (Protobuf field number 2; repeated=True)<br>`facecolor: int32` (Protobuf field number 3; repeated=False) |
| `TessellationOptions` | `surface_deviation: double` (Protobuf field number 1; repeated=False)<br>`angle_deviation: double` (Protobuf field number 2; repeated=False)<br>`maximum_aspect_ratio: double` (Protobuf field number 3; repeated=False)<br>`maximum_edge_length: double` (Protobuf field number 4; repeated=False)<br>`watertight: bool` (Protobuf field number 5; repeated=False)<br>`curve_deviation: double` (Protobuf field number 6; repeated=False) |
| `VersionIdentifier` | `major_release: int32` (Protobuf field number 1; repeated=False)<br>`minor_release: int32` (Protobuf field number 2; repeated=False)<br>`service_pack: int32` (Protobuf field number 3; repeated=False)<br>`build_number: int32` (Protobuf field number 4; repeated=False) |

### `ansys.api.dbu.v0.dbuwebmodels_pb2`

| Message | Fields |
| --- | --- |
| `ObjectIdentifier` | `id: string` (Protobuf field number 1; repeated=False) |
| `Session` | `id: ansys.api.dbu.v0.ObjectIdentifier` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`status: ansys.api.dbu.v0.SessionStatus` (Protobuf field number 3; repeated=False)<br>`idle_time: google.protobuf.Timestamp` (Protobuf field number 4; repeated=False)<br>`address: string` (Protobuf field number 5; repeated=False)<br>`port: int32` (Protobuf field number 6; repeated=False) |
| `SessionHost` | `id: ansys.api.dbu.v0.ObjectIdentifier` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`status: ansys.api.dbu.v0.SessionHostStatus` (Protobuf field number 3; repeated=False)<br>`idle_time: google.protobuf.Timestamp` (Protobuf field number 4; repeated=False)<br>`address: string` (Protobuf field number 5; repeated=False)<br>`port: int32` (Protobuf field number 6; repeated=False) |
| `User` | `id: ansys.api.dbu.v0.ObjectIdentifier` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`uri: string` (Protobuf field number 3; repeated=False) |

### `ansys.api.dbu.v0.designs_pb2`

| Message | Fields |
| --- | --- |
| `CopyReferencedDocumentsRequest` | `document_id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`output_path: string` (Protobuf field number 2; repeated=False) |
| `DesignTessellationRequest` | `options: ansys.api.dbu.v0.TessellationOptions` (Protobuf field number 1; repeated=False)<br>`include_faces: bool` (Protobuf field number 2; repeated=False)<br>`include_edges: bool` (Protobuf field number 3; repeated=False) |
| `DesignTessellationResponse` | `body_tessellation: ansys.api.dbu.v0.designs.DesignTessellationResponse.BodyTessellationEntry` (Protobuf field number 1; repeated=True) |
| `DesignTessellationResponseData` | `face_tessellation: ansys.api.dbu.v0.designs.DesignTessellationResponseData.FaceTessellationEntry` (Protobuf field number 1; repeated=True)<br>`edge_tessellation: ansys.api.dbu.v0.designs.DesignTessellationResponseData.EdgeTessellationEntry` (Protobuf field number 2; repeated=True) |
| `DownloadExportFileRequest` | `format: ansys.api.dbu.v0.PartExportFormat` (Protobuf field number 1; repeated=False)<br>`write_body_facets: bool` (Protobuf field number 2; repeated=False) |
| `DownloadExportFileResponse` | `data: bytes` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `designs: ansys.api.dbu.v0.Design` (Protobuf field number 1; repeated=True) |
| `GetAsJsonRequest` | `id: string` (Protobuf field number 1; repeated=False) |
| `GetAsJsonResponse` | `json: string` (Protobuf field number 1; repeated=False) |
| `InsertRequest` | `filepath: string` (Protobuf field number 1; repeated=False)<br>`import_named_selections: bool` (Protobuf field number 2; repeated=False) |
| `NewRequest` | `name: string` (Protobuf field number 1; repeated=False) |
| `OpenCloudFileFromUrlRequest` | `url_filepath: string` (Protobuf field number 1; repeated=False) |
| `OpenRequest` | `filepath: string` (Protobuf field number 1; repeated=False)<br>`import_options: ansys.api.dbu.v0.designs.OpenRequest.ImportOptionsEntry` (Protobuf field number 2; repeated=True)<br>`import_options_definitions: ansys.api.dbu.v0.designs.OpenRequest.ImportOptionsDefinitionsEntry` (Protobuf field number 3; repeated=True) |
| `SaveAsRequest` | `filepath: string` (Protobuf field number 1; repeated=False)<br>`write_body_facets: bool` (Protobuf field number 2; repeated=False) |

### `ansys.api.dbu.v0.drivingdimensions_pb2`

| Message | Fields |
| --- | --- |
| `GetAllRequest` | `parent: string` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `driving_dimensions: ansys.api.dbu.v0.DrivingDimension` (Protobuf field number 1; repeated=True) |
| `UpdateRequest` | `driving_dimension: ansys.api.dbu.v0.DrivingDimension` (Protobuf field number 1; repeated=False) |
| `UpdateResponse` | `status: ansys.api.dbu.v0.drivingdimensions.UpdateStatus` (Protobuf field number 1; repeated=False) |

### `ansys.api.dbu.v0.sessionmanager_pb2`

| Message | Fields |
| --- | --- |
| `StartRequest` | `user: ansys.api.dbu.v0.User` (Protobuf field number 1; repeated=False)<br>`opening_document: string` (Protobuf field number 2; repeated=False) |
| `StartResponse` | `host: ansys.api.dbu.v0.SessionHost` (Protobuf field number 1; repeated=False)<br>`session_object: ansys.api.dbu.v0.Session` (Protobuf field number 2; repeated=False) |

### `ansys.api.dbu.v0.streaming_pb2`

| Message | Fields |
| --- | --- |
| `StreamPackage` | `content_type: string` (Protobuf field number 1; repeated=False)<br>`count: int32` (Protobuf field number 2; repeated=False)<br>`index: int32` (Protobuf field number 3; repeated=False)<br>`total_size: int32` (Protobuf field number 4; repeated=False)<br>`package_size: int32` (Protobuf field number 5; repeated=False)<br>`data: bytes` (Protobuf field number 6; repeated=False) |

### `ansys.api.dbu.v0.windows_pb2`

| Message | Fields |
| --- | --- |
| `GetImageRequest` | `format: ansys.api.dbu.v0.ImageFormat` (Protobuf field number 1; repeated=False) |
| `SetViewRequest` | `view: ansys.api.dbu.v0.WindowView` (Protobuf field number 1; repeated=False) |

## Snapshot counts

- RPC methods: 42
- Protocol messages: 55
- Message fields: 128
