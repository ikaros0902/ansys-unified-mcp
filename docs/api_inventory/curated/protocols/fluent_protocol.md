# fluent_protocol protocol dictionary

- APIKB source key: `fluent_protocol`
- Package: `ansys-api-fluent 0.6.0`
- Interface: fluent gRPC protocol schema
- Snapshot: [`fluent_protocol_api.json`](../../fluent_protocol_api.json)
- Snapshot SHA-256: `f20ee08937bd3a83f1441f7b43b5949a52a8acd9d1409ea8a37008e4b9c9bad0`

> This page describes the captured protobuf schema. It does not confirm product support, host compatibility, or runtime behavior.
> This snapshot records enum type names on fields. It does not list enum members.

## Services and RPC methods

### `ansys.api.fluent.v0.Connection_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Connection` | `Connect` | `(ansys.api.fluent.v0.ConnectRequest) -> ansys.api.fluent.v0.ConnectResponse [client_streaming=False, server_streaming=True]` |

### `ansys.api.fluent.v0.app_utilities_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `AppUtilities` | `GetProductVersion` | `(ansys.api.fluent.v0.app_utilities.GetProductVersionRequest) -> ansys.api.fluent.v0.app_utilities.GetProductVersionResponse [client_streaming=False, server_streaming=False]` |
| `AppUtilities` | `GetBuildInfo` | `(ansys.api.fluent.v0.app_utilities.GetBuildInfoRequest) -> ansys.api.fluent.v0.app_utilities.GetBuildInfoResponse [client_streaming=False, server_streaming=False]` |
| `AppUtilities` | `GetControllerProcessInfo` | `(ansys.api.fluent.v0.app_utilities.GetControllerProcessInfoRequest) -> ansys.api.fluent.v0.app_utilities.GetControllerProcessInfoResponse [client_streaming=False, server_streaming=False]` |
| `AppUtilities` | `GetSolverProcessInfo` | `(ansys.api.fluent.v0.app_utilities.GetSolverProcessInfoRequest) -> ansys.api.fluent.v0.app_utilities.GetSolverProcessInfoResponse [client_streaming=False, server_streaming=False]` |
| `AppUtilities` | `GetAppMode` | `(ansys.api.fluent.v0.app_utilities.GetAppModeRequest) -> ansys.api.fluent.v0.app_utilities.GetAppModeResponse [client_streaming=False, server_streaming=False]` |
| `AppUtilities` | `StartPythonJournal` | `(ansys.api.fluent.v0.app_utilities.StartPythonJournalRequest) -> ansys.api.fluent.v0.app_utilities.StartPythonJournalResponse [client_streaming=False, server_streaming=False]` |
| `AppUtilities` | `StopPythonJournal` | `(ansys.api.fluent.v0.app_utilities.StopPythonJournalRequest) -> ansys.api.fluent.v0.app_utilities.StopPythonJournalResponse [client_streaming=False, server_streaming=False]` |
| `AppUtilities` | `IsBetaEnabled` | `(ansys.api.fluent.v0.app_utilities.IsBetaEnabledRequest) -> ansys.api.fluent.v0.app_utilities.IsBetaEnabledResponse [client_streaming=False, server_streaming=False]` |
| `AppUtilities` | `EnableBeta` | `(ansys.api.fluent.v0.app_utilities.EnableBetaRequest) -> ansys.api.fluent.v0.app_utilities.EnableBetaResponse [client_streaming=False, server_streaming=False]` |
| `AppUtilities` | `IsWildcard` | `(ansys.api.fluent.v0.app_utilities.IsWildcardRequest) -> ansys.api.fluent.v0.app_utilities.IsWildcardResponse [client_streaming=False, server_streaming=False]` |
| `AppUtilities` | `IsSolutionDataAvailable` | `(ansys.api.fluent.v0.app_utilities.IsSolutionDataAvailableRequest) -> ansys.api.fluent.v0.app_utilities.IsSolutionDataAvailableResponse [client_streaming=False, server_streaming=False]` |
| `AppUtilities` | `RegisterPauseOnSolutionEvents` | `(ansys.api.fluent.v0.app_utilities.RegisterPauseOnSolutionEventsRequest) -> ansys.api.fluent.v0.app_utilities.RegisterPauseOnSolutionEventsResponse [client_streaming=False, server_streaming=False]` |
| `AppUtilities` | `ResumeOnSolutionEvent` | `(ansys.api.fluent.v0.app_utilities.ResumeOnSolutionEventRequest) -> ansys.api.fluent.v0.app_utilities.ResumeOnSolutionEventResponse [client_streaming=False, server_streaming=False]` |
| `AppUtilities` | `UnregisterPauseOnSolutionEvents` | `(ansys.api.fluent.v0.app_utilities.UnregisterPauseOnSolutionEventsRequest) -> ansys.api.fluent.v0.app_utilities.UnregisterPauseOnSolutionEventsResponse [client_streaming=False, server_streaming=False]` |
| `AppUtilities` | `Exit` | `(ansys.api.fluent.v0.app_utilities.ExitRequest) -> ansys.api.fluent.v0.app_utilities.ExitResponse [client_streaming=False, server_streaming=False]` |
| `AppUtilities` | `SetWorkingDirectory` | `(ansys.api.fluent.v0.app_utilities.SetWorkingDirectoryRequest) -> ansys.api.fluent.v0.app_utilities.SetWorkingDirectoryResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.fluent.v0.batch_ops_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `BatchOps` | `Execute` | `(ansys.api.fluent.v0.ExecuteRequest) -> ansys.api.fluent.v0.ExecuteResponse [client_streaming=True, server_streaming=True]` |

### `ansys.api.fluent.v0.datamodel_se_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `DataModel` | `BeginStreaming` | `(grpcRemoting.DataModelRequest) -> grpcRemoting.DataModelResponse [client_streaming=False, server_streaming=True]` |
| `DataModel` | `initDatamodel` | `(grpcRemoting.InitDatamodelRequest) -> grpcRemoting.InitDatamodelResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `getState` | `(grpcRemoting.GetStateRequest) -> grpcRemoting.GetStateResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `setState` | `(grpcRemoting.SetStateRequest) -> grpcRemoting.SetStateResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `updateDict` | `(grpcRemoting.UpdateDictRequest) -> grpcRemoting.UpdateDictResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `deleteObject` | `(grpcRemoting.DeleteObjectRequest) -> grpcRemoting.DeleteObjectResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `getAttributeValue` | `(grpcRemoting.GetAttributeValueRequest) -> grpcRemoting.GetAttributeValueResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `executeCommand` | `(grpcRemoting.ExecuteCommandRequest) -> grpcRemoting.ExecuteCommandResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `executeQuery` | `(grpcRemoting.ExecuteQueryRequest) -> grpcRemoting.ExecuteQueryResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `createCommandArguments` | `(grpcRemoting.CreateCommandArgumentsRequest) -> grpcRemoting.CreateCommandArgumentsResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `deleteCommandArguments` | `(grpcRemoting.DeleteCommandArgumentsRequest) -> grpcRemoting.DeleteCommandArgumentsResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `getSpecs` | `(grpcRemoting.GetSpecsRequest) -> grpcRemoting.GetSpecsResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `getStaticInfo` | `(grpcRemoting.GetStaticInfoRequest) -> grpcRemoting.GetStaticInfoResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `rename` | `(grpcRemoting.RenameRequest) -> grpcRemoting.RenameResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `fixState` | `(grpcRemoting.FixStateRequest) -> grpcRemoting.FixStateResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `getObjectNames` | `(grpcRemoting.GetObjectNamesRequest) -> grpcRemoting.GetObjectNamesResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `deleteChildObjects` | `(grpcRemoting.DeleteChildObjectsRequest) -> grpcRemoting.DeleteChildObjectsResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `subscribeEvents` | `(grpcRemoting.SubscribeEventsRequest) -> grpcRemoting.SubscribeEventsResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `unsubscribeEvents` | `(grpcRemoting.UnsubscribeEventsRequest) -> grpcRemoting.UnsubscribeEventsResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `BeginEventStreaming` | `(grpcRemoting.EventRequest) -> grpcRemoting.EventResponse [client_streaming=False, server_streaming=True]` |

### `ansys.api.fluent.v0.datamodel_tui_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `DataModel` | `NotifyChanges` | `(ansys.api.fluent.v0.NotifyChangesRequest) -> ansys.api.fluent.v0.NotifyChangesResponse [client_streaming=False, server_streaming=True]` |
| `DataModel` | `GetAttributeValue` | `(ansys.api.fluent.v0.GetAttributeValueRequest) -> ansys.api.fluent.v0.GetAttributeValueResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `GetState` | `(ansys.api.fluent.v0.GetStateRequest) -> ansys.api.fluent.v0.GetStateResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `SetState` | `(ansys.api.fluent.v0.SetStateRequest) -> ansys.api.fluent.v0.SetStateResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `ExecuteCommand` | `(ansys.api.fluent.v0.ExecuteCommandRequest) -> ansys.api.fluent.v0.ExecuteCommandResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `ExecuteQuery` | `(ansys.api.fluent.v0.ExecuteQueryRequest) -> ansys.api.fluent.v0.ExecuteQueryResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `CompositeGet` | `(ansys.api.fluent.v0.CompositeGetRequest) -> ansys.api.fluent.v0.CompositeGetResponse [client_streaming=False, server_streaming=False]` |
| `DataModel` | `GetStaticInfo` | `(ansys.api.fluent.v0.GetStaticInfoRequest) -> ansys.api.fluent.v0.GetStaticInfoResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.fluent.v0.events_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Events` | `BeginStreaming` | `(grpcRemoting.BeginStreamingRequest) -> grpcRemoting.BeginStreamingResponse [client_streaming=False, server_streaming=True]` |

### `ansys.api.fluent.v0.field_data_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `FieldData` | `BeginFieldsStreaming` | `(grpcRemoting.BeginFieldsStreamingRequest) -> grpcRemoting.BeginFieldsStreamingResponse [client_streaming=False, server_streaming=True]` |
| `FieldData` | `GetFields` | `(grpcRemoting.GetFieldsRequest) -> grpcRemoting.GetFieldsResponse [client_streaming=False, server_streaming=True]` |
| `FieldData` | `GetRange` | `(grpcRemoting.GetRangeRequest) -> grpcRemoting.GetRangeResponse [client_streaming=False, server_streaming=False]` |
| `FieldData` | `GetSurfacesInfo` | `(grpcRemoting.GetSurfacesInfoRequest) -> grpcRemoting.GetSurfacesInfoResponse [client_streaming=False, server_streaming=False]` |
| `FieldData` | `GetVectorFieldsInfo` | `(grpcRemoting.GetVectorFieldsInfoRequest) -> grpcRemoting.GetVectorFieldsInfoResponse [client_streaming=False, server_streaming=False]` |
| `FieldData` | `GetFieldsInfo` | `(grpcRemoting.GetFieldsInfoRequest) -> grpcRemoting.GetFieldsInfoResponse [client_streaming=False, server_streaming=False]` |
| `FieldData` | `GetSurfaces` | `(grpcRemoting.GetSurfacesRequest) -> grpcRemoting.GetSurfacesResponse [client_streaming=False, server_streaming=True]` |
| `FieldData` | `GetScalarField` | `(grpcRemoting.GetScalarFieldRequest) -> grpcRemoting.GetScalarFieldResponse [client_streaming=False, server_streaming=True]` |
| `FieldData` | `GetVectorField` | `(grpcRemoting.GetVectorFieldRequest) -> grpcRemoting.GetVectorFieldResponse [client_streaming=False, server_streaming=True]` |
| `FieldData` | `GetPathlinesField` | `(grpcRemoting.GetPathlinesFieldRequest) -> grpcRemoting.GetPathlinesFieldResponse [client_streaming=False, server_streaming=True]` |
| `FieldData` | `GetParticleTracksField` | `(grpcRemoting.GetParticleTracksFieldRequest) -> grpcRemoting.GetParticleTracksFieldResponse [client_streaming=False, server_streaming=True]` |
| `FieldData` | `IsBoundaryValuesOn` | `(grpcRemoting.IsBoundaryValuesOnRequest) -> grpcRemoting.IsBoundaryValuesOnResponse [client_streaming=False, server_streaming=False]` |
| `FieldData` | `GetSolverMeshNodesDouble` | `(grpcRemoting.GetSolverMeshNodesRequest) -> grpcRemoting.GetSolverMeshNodesDoubleResponse [client_streaming=False, server_streaming=True]` |
| `FieldData` | `GetSolverMeshNodesFloat` | `(grpcRemoting.GetSolverMeshNodesRequest) -> grpcRemoting.GetSolverMeshNodesFloatResponse [client_streaming=False, server_streaming=True]` |
| `FieldData` | `GetSolverMeshElements` | `(grpcRemoting.GetSolverMeshElementsRequest) -> grpcRemoting.GetSolverMeshElementsResponse [client_streaming=False, server_streaming=True]` |

### `ansys.api.fluent.v0.health_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Health` | `Check` | `(grpc.health.v1.HealthCheckRequest) -> grpc.health.v1.HealthCheckResponse [client_streaming=False, server_streaming=False]` |
| `Health` | `Watch` | `(grpc.health.v1.HealthCheckRequest) -> grpc.health.v1.HealthCheckResponse [client_streaming=False, server_streaming=True]` |

### `ansys.api.fluent.v0.meshing_queries_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `MeshingQueries` | `GetFaceZoneAtLocation` | `(ansys.api.fluent.v0.GetFaceZoneAtLocationRequest) -> ansys.api.fluent.v0.GetFaceZoneAtLocationResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetCellZoneAtLocation` | `(ansys.api.fluent.v0.GetCellZoneAtLocationRequest) -> ansys.api.fluent.v0.GetCellZoneAtLocationResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetZonesOfType` | `(ansys.api.fluent.v0.GetZonesOfTypeRequest) -> ansys.api.fluent.v0.GetZonesOfTypeResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetZonesOfGroup` | `(ansys.api.fluent.v0.GetZonesOfGroupRequest) -> ansys.api.fluent.v0.GetZonesOfGroupResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetFaceZonesOfFilter` | `(ansys.api.fluent.v0.GetFaceZonesOfFilterRequest) -> ansys.api.fluent.v0.GetFaceZonesOfFilterResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetCellZonesOfFilter` | `(ansys.api.fluent.v0.GetCellZonesOfFilterRequest) -> ansys.api.fluent.v0.GetCellZonesOfFilterResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetEdgeZonesOfFilter` | `(ansys.api.fluent.v0.GetEdgeZonesOfFilterRequest) -> ansys.api.fluent.v0.GetEdgeZonesOfFilterResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetNodeZonesOfFilter` | `(ansys.api.fluent.v0.GetNodeZonesOfFilterRequest) -> ansys.api.fluent.v0.GetNodeZonesOfFilterResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetObjectsOfType` | `(ansys.api.fluent.v0.GetObjectsOfTypeRequest) -> ansys.api.fluent.v0.GetObjectsOfTypeResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetFaceZoneIdListOfObject` | `(ansys.api.fluent.v0.GetFaceZoneIdListOfObjectRequest) -> ansys.api.fluent.v0.GetFaceZoneIdListOfObjectResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetEdgeZoneIdListOfObject` | `(ansys.api.fluent.v0.GetEdgeZoneIdListOfObjectRequest) -> ansys.api.fluent.v0.GetEdgeZoneIdListOfObjectResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetCellZoneIdListOfObject` | `(ansys.api.fluent.v0.GetCellZoneIdListOfObjectRequest) -> ansys.api.fluent.v0.GetCellZoneIdListOfObjectResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetFaceZonesSharedByRegionsOfType` | `(ansys.api.fluent.v0.GetFaceZonesSharedByRegionsOfTypeRequest) -> ansys.api.fluent.v0.GetFaceZonesSharedByRegionsOfTypeResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetFaceZonesOfRegions` | `(ansys.api.fluent.v0.GetFaceZonesOfRegionsRequest) -> ansys.api.fluent.v0.GetFaceZonesOfRegionsResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetFaceZonesOfLabels` | `(ansys.api.fluent.v0.GetFaceZonesOfLabelsRequest) -> ansys.api.fluent.v0.GetFaceZonesOfLabelsResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetFaceZoneIdListOfLabels` | `(ansys.api.fluent.v0.GetFaceZoneIdListOfLabelsRequest) -> ansys.api.fluent.v0.GetFaceZoneIdListOfLabelsResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetFaceZonesOfObjects` | `(ansys.api.fluent.v0.GetFaceZonesOfObjectsRequest) -> ansys.api.fluent.v0.GetFaceZonesOfObjectsResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetEdgeZonesOfObjects` | `(ansys.api.fluent.v0.GetEdgeZonesOfObjectsRequest) -> ansys.api.fluent.v0.GetEdgeZonesOfObjectsResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetFaceZoneIdListOfRegions` | `(ansys.api.fluent.v0.GetFaceZoneIdListOfRegionsRequest) -> ansys.api.fluent.v0.GetFaceZoneIdListOfRegionsResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetPrismCellZones` | `(ansys.api.fluent.v0.GetPrismCellZonesRequest) -> ansys.api.fluent.v0.GetPrismCellZonesResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetTetCellZones` | `(ansys.api.fluent.v0.GetTetCellZonesRequest) -> ansys.api.fluent.v0.GetTetCellZonesResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetAdjacentCellZones` | `(ansys.api.fluent.v0.GetAdjacentCellZonesRequest) -> ansys.api.fluent.v0.GetAdjacentCellZonesResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetAdjacentFaceZones` | `(ansys.api.fluent.v0.GetAdjacentFaceZonesRequest) -> ansys.api.fluent.v0.GetAdjacentFaceZonesResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetAdjacentInteriorAndBoundaryFaceZones` | `(ansys.api.fluent.v0.GetAdjacentInteriorAndBoundaryFaceZonesRequest) -> ansys.api.fluent.v0.GetAdjacentInteriorAndBoundaryFaceZonesResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetAdjacentZonesByEdgeConnectivity` | `(ansys.api.fluent.v0.GetAdjacentZonesByEdgeConnectivityRequest) -> ansys.api.fluent.v0.GetAdjacentZonesByEdgeConnectivityResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetAdjacentZonesByNodeConnectivity` | `(ansys.api.fluent.v0.GetAdjacentZonesByNodeConnectivityRequest) -> ansys.api.fluent.v0.GetAdjacentZonesByNodeConnectivityResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetSharedBoundaryZones` | `(ansys.api.fluent.v0.GetSharedBoundaryZonesRequest) -> ansys.api.fluent.v0.GetSharedBoundaryZonesResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetInteriorZonesConnectedToCellZones` | `(ansys.api.fluent.v0.GetInteriorZonesConnectedToCellZonesRequest) -> ansys.api.fluent.v0.GetInteriorZonesConnectedToCellZonesResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetFaceZonesWithZoneSpecificPrismsApplied` | `(ansys.api.fluent.v0.Empty) -> ansys.api.fluent.v0.GetFaceZonesWithZoneSpecificPrismsAppliedResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetFaceZonesOfPrismControls` | `(ansys.api.fluent.v0.GetFaceZonesOfPrismControlsRequest) -> ansys.api.fluent.v0.GetFaceZonesOfPrismControlsResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetBaffles` | `(ansys.api.fluent.v0.GetBafflesRequest) -> ansys.api.fluent.v0.GetBafflesResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetEmbeddedBaffles` | `(ansys.api.fluent.v0.Empty) -> ansys.api.fluent.v0.GetEmbeddedBafflesResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetWrappedZones` | `(ansys.api.fluent.v0.Empty) -> ansys.api.fluent.v0.GetWrappedZonesResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetUnreferencedEdgeZones` | `(ansys.api.fluent.v0.Empty) -> ansys.api.fluent.v0.GetUnreferencedEdgeZonesResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetUnreferencedFaceZones` | `(ansys.api.fluent.v0.Empty) -> ansys.api.fluent.v0.GetUnreferencedFaceZonesResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetUnreferencedCellZones` | `(ansys.api.fluent.v0.Empty) -> ansys.api.fluent.v0.GetUnreferencedCellZonesResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetUnreferencedEdgeZonesOfFilter` | `(ansys.api.fluent.v0.GetUnreferencedEdgeZonesOfFilterRequest) -> ansys.api.fluent.v0.GetUnreferencedEdgeZonesOfFilterResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetUnreferencedFaceZonesOfFilter` | `(ansys.api.fluent.v0.GetUnreferencedFaceZonesOfFilterRequest) -> ansys.api.fluent.v0.GetUnreferencedFaceZonesOfFilterResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetUnreferencedCellZonesOfFilter` | `(ansys.api.fluent.v0.GetUnreferencedCellZonesOfFilterRequest) -> ansys.api.fluent.v0.GetUnreferencedCellZonesOfFilterResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetUnreferencedEdgeZoneIdListOfPattern` | `(ansys.api.fluent.v0.GetUnreferencedEdgeZoneIdListOfPatternRequest) -> ansys.api.fluent.v0.GetUnreferencedEdgeZoneIdListOfPatternResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetUnreferencedFaceZoneIdListOfPattern` | `(ansys.api.fluent.v0.GetUnreferencedFaceZoneIdListOfPatternRequest) -> ansys.api.fluent.v0.GetUnreferencedFaceZoneIdListOfPatternResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetUnreferencedCellZoneIdListOfPattern` | `(ansys.api.fluent.v0.GetUnreferencedCellZoneIdListOfPatternRequest) -> ansys.api.fluent.v0.GetUnreferencedCellZoneIdListOfPatternResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetMaxsizeCellZoneByVolume` | `(ansys.api.fluent.v0.GetMaxsizeCellZoneByVolumeRequest) -> ansys.api.fluent.v0.GetMaxsizeCellZoneByVolumeResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetMaxsizeCellZoneByCount` | `(ansys.api.fluent.v0.GetMaxsizeCellZoneByCountRequest) -> ansys.api.fluent.v0.GetMaxsizeCellZoneByCountResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetMinsizeFaceZoneByArea` | `(ansys.api.fluent.v0.GetMinsizeFaceZoneByAreaRequest) -> ansys.api.fluent.v0.GetMinsizeFaceZoneByAreaResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetMinsizeFaceZoneByCount` | `(ansys.api.fluent.v0.GetMinsizeFaceZoneByCountRequest) -> ansys.api.fluent.v0.GetMinsizeFaceZoneByCountResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetFaceZoneListByMaximumEntityCount` | `(ansys.api.fluent.v0.GetFaceZoneListByMaximumEntityCountRequest) -> ansys.api.fluent.v0.GetFaceZoneListByMaximumEntityCountResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetEdgeZoneListByMaximumEntityCount` | `(ansys.api.fluent.v0.GetEdgeZoneListByMaximumEntityCountRequest) -> ansys.api.fluent.v0.GetEdgeZoneListByMaximumEntityCountResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetCellZoneListByMaximumEntityCount` | `(ansys.api.fluent.v0.GetCellZoneListByMaximumEntityCountRequest) -> ansys.api.fluent.v0.GetCellZoneListByMaximumEntityCountResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetFaceZoneListByMaximumZoneArea` | `(ansys.api.fluent.v0.GetFaceZoneListByMaximumZoneAreaRequest) -> ansys.api.fluent.v0.GetFaceZoneListByMaximumZoneAreaResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetFaceZoneListByMinimumZoneArea` | `(ansys.api.fluent.v0.GetFaceZoneListByMinimumZoneAreaRequest) -> ansys.api.fluent.v0.GetFaceZoneListByMinimumZoneAreaResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetZonesWithFreeFaces` | `(ansys.api.fluent.v0.GetZonesWithFreeFacesRequest) -> ansys.api.fluent.v0.GetZonesWithFreeFacesResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetZonesWithMultiFaces` | `(ansys.api.fluent.v0.GetZonesWithMultiFacesRequest) -> ansys.api.fluent.v0.GetZonesWithMultiFacesResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetOverlappingFaceZones` | `(ansys.api.fluent.v0.GetOverlappingFaceZonesRequest) -> ansys.api.fluent.v0.GetOverlappingFaceZonesResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetZonesWithMarkedFaces` | `(ansys.api.fluent.v0.GetZonesWithMarkedFacesRequest) -> ansys.api.fluent.v0.GetZonesWithMarkedFacesResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetAllObjectNameList` | `(ansys.api.fluent.v0.Empty) -> ansys.api.fluent.v0.GetAllObjectNameListResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetObjectNameListOfType` | `(ansys.api.fluent.v0.GetObjectNameListOfTypeRequest) -> ansys.api.fluent.v0.GetObjectNameListOfTypeResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetObjectsOfFilter` | `(ansys.api.fluent.v0.GetObjectsOfFilterRequest) -> ansys.api.fluent.v0.GetObjectsOfFilterResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetRegionsOfObject` | `(ansys.api.fluent.v0.GetRegionsOfObjectRequest) -> ansys.api.fluent.v0.GetRegionsOfObjectResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetRegionNameListOfObject` | `(ansys.api.fluent.v0.GetRegionNameListOfObjectRequest) -> ansys.api.fluent.v0.GetRegionNameListOfObjectResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `SortRegionsByVolume` | `(ansys.api.fluent.v0.SortRegionsByVolumeRequest) -> ansys.api.fluent.v0.SortRegionsByVolumeResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetRegionVolume` | `(ansys.api.fluent.v0.GetRegionVolumeRequest) -> ansys.api.fluent.v0.GetRegionVolumeResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetRegionsOfFilter` | `(ansys.api.fluent.v0.GetRegionsOfFilterRequest) -> ansys.api.fluent.v0.GetRegionsOfFilterResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetRegionNameListOfPattern` | `(ansys.api.fluent.v0.GetRegionNameListOfPatternRequest) -> ansys.api.fluent.v0.GetRegionNameListOfPatternResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetRegionsOfFaceZones` | `(ansys.api.fluent.v0.GetRegionsOfFaceZonesRequest) -> ansys.api.fluent.v0.GetRegionsOfFaceZonesResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `GetRegionNameListOfFaceZones` | `(ansys.api.fluent.v0.GetRegionNameListOfFaceZonesRequest) -> ansys.api.fluent.v0.GetRegionNameListOfFaceZonesResponse [client_streaming=False, server_streaming=False]` |
| `MeshingQueries` | `FindJoinPairs` | `(ansys.api.fluent.v0.FindJoinPairsRequest) -> ansys.api.fluent.v0.FindJoinPairsResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.fluent.v0.monitor_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Monitor` | `GetMonitors` | `(grpcRemoting.GetMonitorsRequest) -> grpcRemoting.GetMonitorsResponse [client_streaming=False, server_streaming=False]` |
| `Monitor` | `BeginStreaming` | `(grpcRemoting.StreamingRequest) -> grpcRemoting.StreamingResponse [client_streaming=False, server_streaming=True]` |

### `ansys.api.fluent.v0.reduction_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Reduction` | `Area` | `(ansys.api.fluent.v0.AreaRequest) -> ansys.api.fluent.v0.AreaResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `AreaAve` | `(ansys.api.fluent.v0.AreaAveRequest) -> ansys.api.fluent.v0.AreaAveResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `AreaInt` | `(ansys.api.fluent.v0.AreaIntRequest) -> ansys.api.fluent.v0.AreaIntResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `Centroid` | `(ansys.api.fluent.v0.CentroidRequest) -> ansys.api.fluent.v0.CentroidResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `Count` | `(ansys.api.fluent.v0.CountRequest) -> ansys.api.fluent.v0.CountResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `CountIf` | `(ansys.api.fluent.v0.CountIfRequest) -> ansys.api.fluent.v0.CountIfResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `Force` | `(ansys.api.fluent.v0.ForceRequest) -> ansys.api.fluent.v0.ForceResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `MassAve` | `(ansys.api.fluent.v0.MassAveRequest) -> ansys.api.fluent.v0.MassAveResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `MassFlowAve` | `(ansys.api.fluent.v0.MassFlowAveRequest) -> ansys.api.fluent.v0.MassFlowAveResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `MassFlowAveAbs` | `(ansys.api.fluent.v0.MassFlowAveAbsRequest) -> ansys.api.fluent.v0.MassFlowAveAbsResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `MassFlowInt` | `(ansys.api.fluent.v0.MassFlowIntRequest) -> ansys.api.fluent.v0.MassFlowIntResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `MassInt` | `(ansys.api.fluent.v0.MassIntRequest) -> ansys.api.fluent.v0.MassIntResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `Maximum` | `(ansys.api.fluent.v0.MaximumRequest) -> ansys.api.fluent.v0.MaximumResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `Minimum` | `(ansys.api.fluent.v0.MinimumRequest) -> ansys.api.fluent.v0.MinimumResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `PressureForce` | `(ansys.api.fluent.v0.PressureForceRequest) -> ansys.api.fluent.v0.PressureForceResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `ViscousForce` | `(ansys.api.fluent.v0.ViscousForceRequest) -> ansys.api.fluent.v0.ViscousForceResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `Volume` | `(ansys.api.fluent.v0.VolumeRequest) -> ansys.api.fluent.v0.VolumeResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `VolumeAve` | `(ansys.api.fluent.v0.VolumeAveRequest) -> ansys.api.fluent.v0.VolumeAveResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `VolumeInt` | `(ansys.api.fluent.v0.VolumeIntRequest) -> ansys.api.fluent.v0.VolumeIntResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `Moment` | `(ansys.api.fluent.v0.MomentRequest) -> ansys.api.fluent.v0.MomentResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `Sum` | `(ansys.api.fluent.v0.SumRequest) -> ansys.api.fluent.v0.SumResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `SumIf` | `(ansys.api.fluent.v0.SumIfRequest) -> ansys.api.fluent.v0.SumIfResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.fluent.v0.scheme_eval_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `SchemeEval` | `Eval` | `(grpcRemoting.SchemePointer) -> grpcRemoting.SchemePointer [client_streaming=False, server_streaming=False]` |
| `SchemeEval` | `SchemeEval` | `(grpcRemoting.SchemeEvalRequest) -> grpcRemoting.SchemeEvalResponse [client_streaming=False, server_streaming=False]` |
| `SchemeEval` | `Exec` | `(grpcRemoting.ExecRequest) -> grpcRemoting.ExecResponse [client_streaming=False, server_streaming=False]` |
| `SchemeEval` | `StringEval` | `(grpcRemoting.StringEvalRequest) -> grpcRemoting.StringEvalResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.fluent.v0.settings_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Settings` | `GetStaticInfo` | `(ansys.api.fluent.v0.settings.GetStaticInfoRequest) -> ansys.api.fluent.v0.settings.GetStaticInfoResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `GetVar` | `(ansys.api.fluent.v0.settings.GetVarRequest) -> ansys.api.fluent.v0.settings.GetVarResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `SetVar` | `(ansys.api.fluent.v0.settings.SetVarRequest) -> ansys.api.fluent.v0.settings.SetVarResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `Rename` | `(ansys.api.fluent.v0.settings.RenameRequest) -> ansys.api.fluent.v0.settings.RenameResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `Create` | `(ansys.api.fluent.v0.settings.CreateRequest) -> ansys.api.fluent.v0.settings.CreateResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `Delete` | `(ansys.api.fluent.v0.settings.DeleteRequest) -> ansys.api.fluent.v0.settings.DeleteResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `GetObjectNames` | `(ansys.api.fluent.v0.settings.GetObjectNamesRequest) -> ansys.api.fluent.v0.settings.GetObjectNamesResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `GetListSize` | `(ansys.api.fluent.v0.settings.GetListSizeRequest) -> ansys.api.fluent.v0.settings.GetListSizeResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `ResizeListObject` | `(ansys.api.fluent.v0.settings.ResizeListObjectRequest) -> ansys.api.fluent.v0.settings.ResizeListObjectResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `ExecuteCommand` | `(ansys.api.fluent.v0.settings.ExecuteCommandRequest) -> ansys.api.fluent.v0.settings.ExecuteCommandResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `ExecuteQuery` | `(ansys.api.fluent.v0.settings.ExecuteQueryRequest) -> ansys.api.fluent.v0.settings.ExecuteQueryResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `GetAttrs` | `(ansys.api.fluent.v0.settings.GetAttrsRequest) -> ansys.api.fluent.v0.settings.GetAttrsResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.fluent.v0.svar_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `svar` | `GetZonesInfo` | `(grpcRemoting.GetZonesInfoRequest) -> grpcRemoting.GetZonesInfoResponse [client_streaming=False, server_streaming=False]` |
| `svar` | `GetSvarsInfo` | `(grpcRemoting.GetSvarsInfoRequest) -> grpcRemoting.GetSvarsInfoResponse [client_streaming=False, server_streaming=False]` |
| `svar` | `GetSvarData` | `(grpcRemoting.GetSvarDataRequest) -> grpcRemoting.GetSvarDataResponse [client_streaming=False, server_streaming=True]` |
| `svar` | `SetSvarData` | `(grpcRemoting.SetSvarDataRequest) -> grpcRemoting.SetSvarDataResponse [client_streaming=True, server_streaming=False]` |

### `ansys.api.fluent.v0.transcript_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Transcript` | `BeginStreaming` | `(grpcRemoting.TranscriptRequest) -> grpcRemoting.TranscriptResponse [client_streaming=False, server_streaming=True]` |

### `ansys.api.fluent.v1.application_runtime_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `ApplicationRuntime` | `GetProductVersion` | `(ansys.api.fluent.v1.application_runtime.GetProductVersionRequest) -> ansys.api.fluent.v1.application_runtime.GetProductVersionResponse [client_streaming=False, server_streaming=False]` |
| `ApplicationRuntime` | `GetBuildInfo` | `(ansys.api.fluent.v1.application_runtime.GetBuildInfoRequest) -> ansys.api.fluent.v1.application_runtime.GetBuildInfoResponse [client_streaming=False, server_streaming=False]` |
| `ApplicationRuntime` | `GetControllerProcessInfo` | `(ansys.api.fluent.v1.application_runtime.GetControllerProcessInfoRequest) -> ansys.api.fluent.v1.application_runtime.GetControllerProcessInfoResponse [client_streaming=False, server_streaming=False]` |
| `ApplicationRuntime` | `GetSolverProcessInfo` | `(ansys.api.fluent.v1.application_runtime.GetSolverProcessInfoRequest) -> ansys.api.fluent.v1.application_runtime.GetSolverProcessInfoResponse [client_streaming=False, server_streaming=False]` |
| `ApplicationRuntime` | `GetMode` | `(ansys.api.fluent.v1.application_runtime.GetModeRequest) -> ansys.api.fluent.v1.application_runtime.GetModeResponse [client_streaming=False, server_streaming=False]` |
| `ApplicationRuntime` | `GetDimension` | `(ansys.api.fluent.v1.application_runtime.GetDimensionRequest) -> ansys.api.fluent.v1.application_runtime.GetDimensionResponse [client_streaming=False, server_streaming=False]` |
| `ApplicationRuntime` | `GetPrecision` | `(ansys.api.fluent.v1.application_runtime.GetPrecisionRequest) -> ansys.api.fluent.v1.application_runtime.GetPrecisionResponse [client_streaming=False, server_streaming=False]` |
| `ApplicationRuntime` | `GetProcessorCount` | `(ansys.api.fluent.v1.application_runtime.GetProcessorCountRequest) -> ansys.api.fluent.v1.application_runtime.GetProcessorCountResponse [client_streaming=False, server_streaming=False]` |
| `ApplicationRuntime` | `GetUIMode` | `(ansys.api.fluent.v1.application_runtime.GetUIModeRequest) -> ansys.api.fluent.v1.application_runtime.GetUIModeResponse [client_streaming=False, server_streaming=False]` |
| `ApplicationRuntime` | `GetGraphicsDriver` | `(ansys.api.fluent.v1.application_runtime.GetGraphicsDriverRequest) -> ansys.api.fluent.v1.application_runtime.GetGraphicsDriverResponse [client_streaming=False, server_streaming=False]` |
| `ApplicationRuntime` | `GetGPUConfig` | `(ansys.api.fluent.v1.application_runtime.GetGPUConfigRequest) -> ansys.api.fluent.v1.application_runtime.GetGPUConfigResponse [client_streaming=False, server_streaming=False]` |
| `ApplicationRuntime` | `StartPythonJournal` | `(ansys.api.fluent.v1.application_runtime.StartPythonJournalRequest) -> ansys.api.fluent.v1.application_runtime.StartPythonJournalResponse [client_streaming=False, server_streaming=False]` |
| `ApplicationRuntime` | `StopPythonJournal` | `(ansys.api.fluent.v1.application_runtime.StopPythonJournalRequest) -> ansys.api.fluent.v1.application_runtime.StopPythonJournalResponse [client_streaming=False, server_streaming=False]` |
| `ApplicationRuntime` | `IsBetaEnabled` | `(ansys.api.fluent.v1.application_runtime.IsBetaEnabledRequest) -> ansys.api.fluent.v1.application_runtime.IsBetaEnabledResponse [client_streaming=False, server_streaming=False]` |
| `ApplicationRuntime` | `EnableBeta` | `(ansys.api.fluent.v1.application_runtime.EnableBetaRequest) -> ansys.api.fluent.v1.application_runtime.EnableBetaResponse [client_streaming=False, server_streaming=False]` |
| `ApplicationRuntime` | `Exit` | `(ansys.api.fluent.v1.application_runtime.ExitRequest) -> ansys.api.fluent.v1.application_runtime.ExitResponse [client_streaming=False, server_streaming=False]` |
| `ApplicationRuntime` | `SetWorkingDirectory` | `(ansys.api.fluent.v1.application_runtime.SetWorkingDirectoryRequest) -> ansys.api.fluent.v1.application_runtime.SetWorkingDirectoryResponse [client_streaming=False, server_streaming=False]` |
| `ApplicationRuntime` | `SetIdleTimeout` | `(ansys.api.fluent.v1.application_runtime.SetIdleTimeoutRequest) -> ansys.api.fluent.v1.application_runtime.SetIdleTimeoutResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.fluent.v1.connection_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Connection` | `Connect` | `(ansys.api.fluent.v1.connection.ConnectRequest) -> ansys.api.fluent.v1.connection.ConnectResponse [client_streaming=False, server_streaming=True]` |

### `ansys.api.fluent.v1.events_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Events` | `BeginStreaming` | `(ansys.api.fluent.v1.events.BeginStreamingRequest) -> ansys.api.fluent.v1.events.BeginStreamingResponse [client_streaming=False, server_streaming=True]` |
| `Events` | `PauseSolveFor` | `(ansys.api.fluent.v1.events.PauseSolveForRequest) -> ansys.api.fluent.v1.events.PauseSolveForResponse [client_streaming=False, server_streaming=False]` |
| `Events` | `ResumeSolve` | `(ansys.api.fluent.v1.events.ResumeSolveRequest) -> ansys.api.fluent.v1.events.ResumeSolveResponse [client_streaming=False, server_streaming=False]` |
| `Events` | `CancelPauseSolve` | `(ansys.api.fluent.v1.events.CancelPauseSolveRequest) -> ansys.api.fluent.v1.events.CancelPauseSolveResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.fluent.v1.field_data_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `FieldData` | `BeginFieldsStreaming` | `(ansys.api.fluent.v1.field_data.BeginFieldsStreamingRequest) -> ansys.api.fluent.v1.field_data.BeginFieldsStreamingResponse [client_streaming=False, server_streaming=True]` |
| `FieldData` | `GetFields` | `(ansys.api.fluent.v1.field_data.GetFieldsRequest) -> ansys.api.fluent.v1.field_data.GetFieldsResponse [client_streaming=False, server_streaming=True]` |
| `FieldData` | `GetRange` | `(ansys.api.fluent.v1.field_data.GetRangeRequest) -> ansys.api.fluent.v1.field_data.GetRangeResponse [client_streaming=False, server_streaming=False]` |
| `FieldData` | `GetSurfacesInfo` | `(ansys.api.fluent.v1.field_data.GetSurfacesInfoRequest) -> ansys.api.fluent.v1.field_data.GetSurfacesInfoResponse [client_streaming=False, server_streaming=False]` |
| `FieldData` | `GetVectorFieldsInfo` | `(ansys.api.fluent.v1.field_data.GetVectorFieldsInfoRequest) -> ansys.api.fluent.v1.field_data.GetVectorFieldsInfoResponse [client_streaming=False, server_streaming=False]` |
| `FieldData` | `GetFieldsInfo` | `(ansys.api.fluent.v1.field_data.GetFieldsInfoRequest) -> ansys.api.fluent.v1.field_data.GetFieldsInfoResponse [client_streaming=False, server_streaming=False]` |
| `FieldData` | `GetSurfaces` | `(ansys.api.fluent.v1.field_data.GetSurfacesRequest) -> ansys.api.fluent.v1.field_data.GetSurfacesResponse [client_streaming=False, server_streaming=True]` |
| `FieldData` | `GetScalarField` | `(ansys.api.fluent.v1.field_data.GetScalarFieldRequest) -> ansys.api.fluent.v1.field_data.GetScalarFieldResponse [client_streaming=False, server_streaming=True]` |
| `FieldData` | `GetVectorField` | `(ansys.api.fluent.v1.field_data.GetVectorFieldRequest) -> ansys.api.fluent.v1.field_data.GetVectorFieldResponse [client_streaming=False, server_streaming=True]` |
| `FieldData` | `GetPathlinesField` | `(ansys.api.fluent.v1.field_data.GetPathlinesFieldRequest) -> ansys.api.fluent.v1.field_data.GetPathlinesFieldResponse [client_streaming=False, server_streaming=True]` |
| `FieldData` | `GetParticleTracksField` | `(ansys.api.fluent.v1.field_data.GetParticleTracksFieldRequest) -> ansys.api.fluent.v1.field_data.GetParticleTracksFieldResponse [client_streaming=False, server_streaming=True]` |
| `FieldData` | `IsBoundaryValuesEnabled` | `(ansys.api.fluent.v1.field_data.IsBoundaryValuesEnabledRequest) -> ansys.api.fluent.v1.field_data.IsBoundaryValuesEnabledResponse [client_streaming=False, server_streaming=False]` |
| `FieldData` | `GetSolverMeshNodesDouble` | `(ansys.api.fluent.v1.field_data.GetSolverMeshNodesRequest) -> ansys.api.fluent.v1.field_data.GetSolverMeshNodesDoubleResponse [client_streaming=False, server_streaming=True]` |
| `FieldData` | `GetSolverMeshNodesFloat` | `(ansys.api.fluent.v1.field_data.GetSolverMeshNodesRequest) -> ansys.api.fluent.v1.field_data.GetSolverMeshNodesFloatResponse [client_streaming=False, server_streaming=True]` |
| `FieldData` | `GetSolverMeshElements` | `(ansys.api.fluent.v1.field_data.GetSolverMeshElementsRequest) -> ansys.api.fluent.v1.field_data.GetSolverMeshElementsResponse [client_streaming=False, server_streaming=True]` |
| `FieldData` | `IsDataAvailable` | `(ansys.api.fluent.v1.field_data.IsDataAvailableRequest) -> ansys.api.fluent.v1.field_data.IsDataAvailableResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.fluent.v1.health_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Health` | `Check` | `(ansys.api.fluent.v1.health.HealthCheckRequest) -> ansys.api.fluent.v1.health.HealthCheckResponse [client_streaming=False, server_streaming=False]` |
| `Health` | `Watch` | `(ansys.api.fluent.v1.health.HealthCheckRequest) -> ansys.api.fluent.v1.health.HealthCheckResponse [client_streaming=False, server_streaming=True]` |

### `ansys.api.fluent.v1.monitor_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Monitor` | `GetMonitors` | `(ansys.api.fluent.v1.monitor.GetMonitorsRequest) -> ansys.api.fluent.v1.monitor.GetMonitorsResponse [client_streaming=False, server_streaming=False]` |
| `Monitor` | `BeginStreaming` | `(ansys.api.fluent.v1.monitor.StreamingRequest) -> ansys.api.fluent.v1.monitor.StreamingResponse [client_streaming=False, server_streaming=True]` |

### `ansys.api.fluent.v1.object_model_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `ObjectModel` | `StreamStateChanges` | `(ansys.api.fluent.v1.object_model.StreamStateChangesRequest) -> ansys.api.fluent.v1.object_model.StreamStateChangesResponse [client_streaming=False, server_streaming=True]` |
| `ObjectModel` | `GetState` | `(ansys.api.fluent.v1.object_model.GetStateRequest) -> ansys.api.fluent.v1.object_model.GetStateResponse [client_streaming=False, server_streaming=False]` |
| `ObjectModel` | `SetState` | `(ansys.api.fluent.v1.object_model.SetStateRequest) -> ansys.api.fluent.v1.object_model.SetStateResponse [client_streaming=False, server_streaming=False]` |
| `ObjectModel` | `UpdateDict` | `(ansys.api.fluent.v1.object_model.UpdateDictRequest) -> ansys.api.fluent.v1.object_model.UpdateDictResponse [client_streaming=False, server_streaming=False]` |
| `ObjectModel` | `CreateObject` | `(ansys.api.fluent.v1.object_model.CreateObjectRequest) -> ansys.api.fluent.v1.object_model.CreateObjectResponse [client_streaming=False, server_streaming=False]` |
| `ObjectModel` | `DeleteObject` | `(ansys.api.fluent.v1.object_model.DeleteObjectRequest) -> ansys.api.fluent.v1.object_model.DeleteObjectResponse [client_streaming=False, server_streaming=False]` |
| `ObjectModel` | `GetAttributeValue` | `(ansys.api.fluent.v1.object_model.GetAttributeValueRequest) -> ansys.api.fluent.v1.object_model.GetAttributeValueResponse [client_streaming=False, server_streaming=False]` |
| `ObjectModel` | `ExecuteCommand` | `(ansys.api.fluent.v1.object_model.ExecuteCommandRequest) -> ansys.api.fluent.v1.object_model.ExecuteCommandResponse [client_streaming=False, server_streaming=False]` |
| `ObjectModel` | `ExecuteQuery` | `(ansys.api.fluent.v1.object_model.ExecuteQueryRequest) -> ansys.api.fluent.v1.object_model.ExecuteQueryResponse [client_streaming=False, server_streaming=False]` |
| `ObjectModel` | `CreateCommandArguments` | `(ansys.api.fluent.v1.object_model.CreateCommandArgumentsRequest) -> ansys.api.fluent.v1.object_model.CreateCommandArgumentsResponse [client_streaming=False, server_streaming=False]` |
| `ObjectModel` | `DeleteCommandArguments` | `(ansys.api.fluent.v1.object_model.DeleteCommandArgumentsRequest) -> ansys.api.fluent.v1.object_model.DeleteCommandArgumentsResponse [client_streaming=False, server_streaming=False]` |
| `ObjectModel` | `GetSchema` | `(ansys.api.fluent.v1.object_model.GetSchemaRequest) -> ansys.api.fluent.v1.object_model.GetSchemaResponse [client_streaming=False, server_streaming=False]` |
| `ObjectModel` | `Rename` | `(ansys.api.fluent.v1.object_model.RenameRequest) -> ansys.api.fluent.v1.object_model.RenameResponse [client_streaming=False, server_streaming=False]` |
| `ObjectModel` | `FixState` | `(ansys.api.fluent.v1.object_model.FixStateRequest) -> ansys.api.fluent.v1.object_model.FixStateResponse [client_streaming=False, server_streaming=False]` |
| `ObjectModel` | `GetObjectNames` | `(ansys.api.fluent.v1.object_model.GetObjectNamesRequest) -> ansys.api.fluent.v1.object_model.GetObjectNamesResponse [client_streaming=False, server_streaming=False]` |
| `ObjectModel` | `DeleteChildObjects` | `(ansys.api.fluent.v1.object_model.DeleteChildObjectsRequest) -> ansys.api.fluent.v1.object_model.DeleteChildObjectsResponse [client_streaming=False, server_streaming=False]` |
| `ObjectModel` | `SubscribeEvents` | `(ansys.api.fluent.v1.object_model.SubscribeEventsRequest) -> ansys.api.fluent.v1.object_model.SubscribeEventsResponse [client_streaming=False, server_streaming=False]` |
| `ObjectModel` | `UnsubscribeEvents` | `(ansys.api.fluent.v1.object_model.UnsubscribeEventsRequest) -> ansys.api.fluent.v1.object_model.UnsubscribeEventsResponse [client_streaming=False, server_streaming=False]` |
| `ObjectModel` | `StreamEvents` | `(ansys.api.fluent.v1.object_model.StreamEventsRequest) -> ansys.api.fluent.v1.object_model.StreamEventsResponse [client_streaming=False, server_streaming=True]` |

### `ansys.api.fluent.v1.reduction_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Reduction` | `Area` | `(ansys.api.fluent.v1.reduction.AreaRequest) -> ansys.api.fluent.v1.reduction.AreaResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `AreaAve` | `(ansys.api.fluent.v1.reduction.AreaAveRequest) -> ansys.api.fluent.v1.reduction.AreaAveResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `AreaInt` | `(ansys.api.fluent.v1.reduction.AreaIntRequest) -> ansys.api.fluent.v1.reduction.AreaIntResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `Centroid` | `(ansys.api.fluent.v1.reduction.CentroidRequest) -> ansys.api.fluent.v1.reduction.CentroidResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `Count` | `(ansys.api.fluent.v1.reduction.CountRequest) -> ansys.api.fluent.v1.reduction.CountResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `CountIf` | `(ansys.api.fluent.v1.reduction.CountIfRequest) -> ansys.api.fluent.v1.reduction.CountIfResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `Force` | `(ansys.api.fluent.v1.reduction.ForceRequest) -> ansys.api.fluent.v1.reduction.ForceResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `MassAve` | `(ansys.api.fluent.v1.reduction.MassAveRequest) -> ansys.api.fluent.v1.reduction.MassAveResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `MassFlowAve` | `(ansys.api.fluent.v1.reduction.MassFlowAveRequest) -> ansys.api.fluent.v1.reduction.MassFlowAveResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `MassFlowAveAbs` | `(ansys.api.fluent.v1.reduction.MassFlowAveAbsRequest) -> ansys.api.fluent.v1.reduction.MassFlowAveAbsResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `MassFlowInt` | `(ansys.api.fluent.v1.reduction.MassFlowIntRequest) -> ansys.api.fluent.v1.reduction.MassFlowIntResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `MassInt` | `(ansys.api.fluent.v1.reduction.MassIntRequest) -> ansys.api.fluent.v1.reduction.MassIntResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `Maximum` | `(ansys.api.fluent.v1.reduction.MaximumRequest) -> ansys.api.fluent.v1.reduction.MaximumResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `Minimum` | `(ansys.api.fluent.v1.reduction.MinimumRequest) -> ansys.api.fluent.v1.reduction.MinimumResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `PressureForce` | `(ansys.api.fluent.v1.reduction.PressureForceRequest) -> ansys.api.fluent.v1.reduction.PressureForceResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `ViscousForce` | `(ansys.api.fluent.v1.reduction.ViscousForceRequest) -> ansys.api.fluent.v1.reduction.ViscousForceResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `Volume` | `(ansys.api.fluent.v1.reduction.VolumeRequest) -> ansys.api.fluent.v1.reduction.VolumeResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `VolumeAve` | `(ansys.api.fluent.v1.reduction.VolumeAveRequest) -> ansys.api.fluent.v1.reduction.VolumeAveResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `VolumeInt` | `(ansys.api.fluent.v1.reduction.VolumeIntRequest) -> ansys.api.fluent.v1.reduction.VolumeIntResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `Moment` | `(ansys.api.fluent.v1.reduction.MomentRequest) -> ansys.api.fluent.v1.reduction.MomentResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `Sum` | `(ansys.api.fluent.v1.reduction.SumRequest) -> ansys.api.fluent.v1.reduction.SumResponse [client_streaming=False, server_streaming=False]` |
| `Reduction` | `SumIf` | `(ansys.api.fluent.v1.reduction.SumIfRequest) -> ansys.api.fluent.v1.reduction.SumIfResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.fluent.v1.scheme_interpreter_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `SchemeInterpreter` | `Eval` | `(ansys.api.fluent.v1.scheme_pointer.SchemePointer) -> ansys.api.fluent.v1.scheme_pointer.SchemePointer [client_streaming=False, server_streaming=False]` |
| `SchemeInterpreter` | `SchemeEval` | `(ansys.api.fluent.v1.scheme_interpreter.SchemeEvalRequest) -> ansys.api.fluent.v1.scheme_interpreter.SchemeEvalResponse [client_streaming=False, server_streaming=False]` |
| `SchemeInterpreter` | `Exec` | `(ansys.api.fluent.v1.scheme_interpreter.ExecRequest) -> ansys.api.fluent.v1.scheme_interpreter.ExecResponse [client_streaming=False, server_streaming=False]` |
| `SchemeInterpreter` | `StringEval` | `(ansys.api.fluent.v1.scheme_interpreter.StringEvalRequest) -> ansys.api.fluent.v1.scheme_interpreter.StringEvalResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.fluent.v1.settings_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Settings` | `GetSchema` | `(ansys.api.fluent.v1.settings.GetSchemaRequest) -> ansys.api.fluent.v1.settings.GetSchemaResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `GetState` | `(ansys.api.fluent.v1.settings.GetStateRequest) -> ansys.api.fluent.v1.settings.GetStateResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `SetState` | `(ansys.api.fluent.v1.settings.SetStateRequest) -> ansys.api.fluent.v1.settings.SetStateResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `Rename` | `(ansys.api.fluent.v1.settings.RenameRequest) -> ansys.api.fluent.v1.settings.RenameResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `CreateObject` | `(ansys.api.fluent.v1.settings.CreateObjectRequest) -> ansys.api.fluent.v1.settings.CreateObjectResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `DeleteObject` | `(ansys.api.fluent.v1.settings.DeleteObjectRequest) -> ansys.api.fluent.v1.settings.DeleteObjectResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `GetObjectNames` | `(ansys.api.fluent.v1.settings.GetObjectNamesRequest) -> ansys.api.fluent.v1.settings.GetObjectNamesResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `GetListSize` | `(ansys.api.fluent.v1.settings.GetListSizeRequest) -> ansys.api.fluent.v1.settings.GetListSizeResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `ResizeListObject` | `(ansys.api.fluent.v1.settings.ResizeListObjectRequest) -> ansys.api.fluent.v1.settings.ResizeListObjectResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `ExecuteCommand` | `(ansys.api.fluent.v1.settings.ExecuteCommandRequest) -> ansys.api.fluent.v1.settings.ExecuteCommandResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `ExecuteQuery` | `(ansys.api.fluent.v1.settings.ExecuteQueryRequest) -> ansys.api.fluent.v1.settings.ExecuteQueryResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `GetAttrs` | `(ansys.api.fluent.v1.settings.GetAttrsRequest) -> ansys.api.fluent.v1.settings.GetAttrsResponse [client_streaming=False, server_streaming=False]` |
| `Settings` | `IsWildcard` | `(ansys.api.fluent.v1.settings.IsWildcardRequest) -> ansys.api.fluent.v1.settings.IsWildcardResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.fluent.v1.solution_variable_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `SolutionVariable` | `GetZonesInfo` | `(ansys.api.fluent.v1.solution_variable.GetZonesInfoRequest) -> ansys.api.fluent.v1.solution_variable.GetZonesInfoResponse [client_streaming=False, server_streaming=False]` |
| `SolutionVariable` | `GetSolutionVariableInfo` | `(ansys.api.fluent.v1.solution_variable.GetSolutionVariableInfoRequest) -> ansys.api.fluent.v1.solution_variable.GetSolutionVariableInfoResponse [client_streaming=False, server_streaming=False]` |
| `SolutionVariable` | `GetSolutionVariableData` | `(ansys.api.fluent.v1.solution_variable.GetSolutionVariableDataRequest) -> ansys.api.fluent.v1.solution_variable.GetSolutionVariableDataResponse [client_streaming=False, server_streaming=True]` |
| `SolutionVariable` | `SetSolutionVariableData` | `(ansys.api.fluent.v1.solution_variable.SetSolutionVariableDataRequest) -> ansys.api.fluent.v1.solution_variable.SetSolutionVariableDataResponse [client_streaming=True, server_streaming=False]` |

### `ansys.api.fluent.v1.text_interface_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `TextInterface` | `NotifyChanges` | `(ansys.api.fluent.v1.text_interface.NotifyChangesRequest) -> ansys.api.fluent.v1.text_interface.NotifyChangesResponse [client_streaming=False, server_streaming=True]` |
| `TextInterface` | `GetAttributeValue` | `(ansys.api.fluent.v1.text_interface.GetAttributeValueRequest) -> ansys.api.fluent.v1.text_interface.GetAttributeValueResponse [client_streaming=False, server_streaming=False]` |
| `TextInterface` | `GetState` | `(ansys.api.fluent.v1.text_interface.GetStateRequest) -> ansys.api.fluent.v1.text_interface.GetStateResponse [client_streaming=False, server_streaming=False]` |
| `TextInterface` | `SetState` | `(ansys.api.fluent.v1.text_interface.SetStateRequest) -> ansys.api.fluent.v1.text_interface.SetStateResponse [client_streaming=False, server_streaming=False]` |
| `TextInterface` | `ExecuteCommand` | `(ansys.api.fluent.v1.text_interface.ExecuteCommandRequest) -> ansys.api.fluent.v1.text_interface.ExecuteCommandResponse [client_streaming=False, server_streaming=False]` |
| `TextInterface` | `ExecuteQuery` | `(ansys.api.fluent.v1.text_interface.ExecuteQueryRequest) -> ansys.api.fluent.v1.text_interface.ExecuteQueryResponse [client_streaming=False, server_streaming=False]` |
| `TextInterface` | `CompositeGet` | `(ansys.api.fluent.v1.text_interface.CompositeGetRequest) -> ansys.api.fluent.v1.text_interface.CompositeGetResponse [client_streaming=False, server_streaming=False]` |
| `TextInterface` | `GetSchema` | `(ansys.api.fluent.v1.text_interface.GetSchemaRequest) -> ansys.api.fluent.v1.text_interface.GetSchemaResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.fluent.v1.transcript_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Transcript` | `BeginStreaming` | `(ansys.api.fluent.v1.transcript.TranscriptRequest) -> ansys.api.fluent.v1.transcript.TranscriptResponse [client_streaming=False, server_streaming=True]` |

## Messages and fields

### `ansys.api.fluent.v0.Connection_pb2`

| Message | Fields |
| --- | --- |
| `ConnectRequest` | `requesttype: ansys.api.fluent.v0.ConnectRequest.RequestType` (Protobuf field number 1; repeated=False)<br>`password: string` (Protobuf field number 2; repeated=False)<br>`version: string` (Protobuf field number 3; repeated=False) |
| `ConnectResponse` | `errorcode: ansys.api.fluent.v0.ConnectionError` (Protobuf field number 1; repeated=False) |

### `ansys.api.fluent.v0.app_utilities_pb2`

| Message | Fields |
| --- | --- |
| `EnableBetaRequest` | — |
| `EnableBetaResponse` | — |
| `ExitRequest` | — |
| `ExitResponse` | — |
| `GetAppModeRequest` | — |
| `GetAppModeResponse` | `app_mode: ansys.api.fluent.v0.app_utilities.AppMode` (Protobuf field number 1; repeated=False) |
| `GetBuildInfoRequest` | — |
| `GetBuildInfoResponse` | `build_time: string` (Protobuf field number 1; repeated=False)<br>`build_id: int64` (Protobuf field number 2; repeated=False)<br>`vcs_revision: string` (Protobuf field number 3; repeated=False)<br>`vcs_branch: string` (Protobuf field number 4; repeated=False) |
| `GetControllerProcessInfoRequest` | — |
| `GetControllerProcessInfoResponse` | `hostname: string` (Protobuf field number 1; repeated=False)<br>`process_id: int64` (Protobuf field number 2; repeated=False)<br>`working_directory: string` (Protobuf field number 3; repeated=False) |
| `GetProductVersionRequest` | — |
| `GetProductVersionResponse` | `major: int64` (Protobuf field number 1; repeated=False)<br>`minor: int64` (Protobuf field number 2; repeated=False)<br>`patch: int64` (Protobuf field number 3; repeated=False) |
| `GetSolverProcessInfoRequest` | — |
| `GetSolverProcessInfoResponse` | `hostname: string` (Protobuf field number 1; repeated=False)<br>`process_id: int64` (Protobuf field number 2; repeated=False)<br>`working_directory: string` (Protobuf field number 3; repeated=False) |
| `IsBetaEnabledRequest` | — |
| `IsBetaEnabledResponse` | `is_beta_enabled: bool` (Protobuf field number 1; repeated=False) |
| `IsSolutionDataAvailableRequest` | — |
| `IsSolutionDataAvailableResponse` | `is_solution_data_available: bool` (Protobuf field number 1; repeated=False) |
| `IsWildcardRequest` | `input: string` (Protobuf field number 1; repeated=False) |
| `IsWildcardResponse` | `is_wildcard: bool` (Protobuf field number 1; repeated=False) |
| `RegisterPauseOnSolutionEventsRequest` | `solution_event: ansys.api.fluent.v0.app_utilities.SolutionEvent` (Protobuf field number 1; repeated=False) |
| `RegisterPauseOnSolutionEventsResponse` | `registration_id: int64` (Protobuf field number 1; repeated=False) |
| `ResumeOnSolutionEventRequest` | `registration_id: int64` (Protobuf field number 1; repeated=False) |
| `ResumeOnSolutionEventResponse` | — |
| `SetWorkingDirectoryRequest` | `path: string` (Protobuf field number 1; repeated=False) |
| `SetWorkingDirectoryResponse` | — |
| `StartPythonJournalRequest` | `journal_name: string` (Protobuf field number 1; repeated=False) |
| `StartPythonJournalResponse` | `journal_id: string` (Protobuf field number 1; repeated=False) |
| `StopPythonJournalRequest` | `journal_id: string` (Protobuf field number 1; repeated=False) |
| `StopPythonJournalResponse` | `journal_str: string` (Protobuf field number 1; repeated=False) |
| `UnregisterPauseOnSolutionEventsRequest` | `registration_id: int64` (Protobuf field number 1; repeated=False) |
| `UnregisterPauseOnSolutionEventsResponse` | — |

### `ansys.api.fluent.v0.batch_ops_pb2`

| Message | Fields |
| --- | --- |
| `ExecuteRequest` | `package: string` (Protobuf field number 1; repeated=False)<br>`service: string` (Protobuf field number 2; repeated=False)<br>`method: string` (Protobuf field number 3; repeated=False)<br>`request_body: bytes` (Protobuf field number 4; repeated=False) |
| `ExecuteResponse` | `status: ansys.api.fluent.v0.ExecuteStatus` (Protobuf field number 1; repeated=False)<br>`response_body: bytes` (Protobuf field number 2; repeated=False) |

### `ansys.api.fluent.v0.common_api_pb2`

| Message | Fields |
| --- | --- |
| `Point` | `x: double` (Protobuf field number 1; repeated=False)<br>`y: double` (Protobuf field number 2; repeated=False)<br>`z: double` (Protobuf field number 3; repeated=False) |

### `ansys.api.fluent.v0.common_pb2`

| Message | Fields |
| --- | --- |
| `Empty` | — |

### `ansys.api.fluent.v0.datamodel_se_pb2`

| Message | Fields |
| --- | --- |
| `AffectedEventRequest` | `path: string` (Protobuf field number 1; repeated=False)<br>`subtype: string` (Protobuf field number 2; repeated=False) |
| `AffectedEventResponse` | `path: string` (Protobuf field number 1; repeated=False)<br>`subtype: string` (Protobuf field number 2; repeated=False) |
| `AttributeChangedEventRequest` | `path: string` (Protobuf field number 1; repeated=False)<br>`attribute: string` (Protobuf field number 2; repeated=False) |
| `AttributeChangedEventResponse` | `path: string` (Protobuf field number 1; repeated=False)<br>`attribute: string` (Protobuf field number 2; repeated=False)<br>`value: utils.Variant` (Protobuf field number 3; repeated=False) |
| `BoolParameterSpecs` | `common: grpcRemoting.CommonSpecs` (Protobuf field number 1; repeated=False) |
| `ChildNames` | `names: string` (Protobuf field number 1; repeated=True) |
| `CommandArg` | `type: string` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`info: grpcRemoting.StaticInfo` (Protobuf field number 3; repeated=False)<br>`helpstring: string` (Protobuf field number 4; repeated=False)<br>`attrs: grpcRemoting.CommandArg.AttrsEntry` (Protobuf field number 5; repeated=True)<br>`docstring: string` (Protobuf field number 6; repeated=False) |
| `CommandAttributeChangedEventRequest` | `path: string` (Protobuf field number 1; repeated=False)<br>`command: string` (Protobuf field number 2; repeated=False)<br>`attribute: string` (Protobuf field number 3; repeated=False) |
| `CommandAttributeChangedEventResponse` | `path: string` (Protobuf field number 1; repeated=False)<br>`command: string` (Protobuf field number 2; repeated=False)<br>`attribute: string` (Protobuf field number 3; repeated=False)<br>`value: utils.Variant` (Protobuf field number 4; repeated=False) |
| `CommandExecutedEventRequest` | `path: string` (Protobuf field number 1; repeated=False)<br>`command: string` (Protobuf field number 2; repeated=False) |
| `CommandExecutedEventResponse` | `path: string` (Protobuf field number 1; repeated=False)<br>`command: string` (Protobuf field number 2; repeated=False)<br>`args: utils.Variant` (Protobuf field number 3; repeated=False) |
| `CommandInfo` | `returntype: string` (Protobuf field number 1; repeated=False)<br>`args: grpcRemoting.CommandArg` (Protobuf field number 2; repeated=True)<br>`docstring: string` (Protobuf field number 3; repeated=False) |
| `CommandSpecs` | `name: string` (Protobuf field number 1; repeated=False)<br>`isactive: bool` (Protobuf field number 2; repeated=False) |
| `CommonSpecs` | `readonly: bool` (Protobuf field number 1; repeated=False)<br>`default: utils.Variant` (Protobuf field number 2; repeated=False)<br>`displaytext: string` (Protobuf field number 3; repeated=False)<br>`isactive: bool` (Protobuf field number 4; repeated=False)<br>`referencepath: string` (Protobuf field number 5; repeated=False)<br>`hasDeveloperExposureLevel: bool` (Protobuf field number 6; repeated=False)<br>`helpstring: string` (Protobuf field number 7; repeated=False) |
| `CreateCommandArgumentsRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`command: string` (Protobuf field number 3; repeated=False) |
| `CreateCommandArgumentsResponse` | `commandid: string` (Protobuf field number 1; repeated=False) |
| `CreatedEventRequest` | `parentpath: string` (Protobuf field number 1; repeated=False)<br>`childtype: string` (Protobuf field number 2; repeated=False) |
| `CreatedEventResponse` | `parentpath: string` (Protobuf field number 1; repeated=False)<br>`childtype: string` (Protobuf field number 2; repeated=False)<br>`childname: string` (Protobuf field number 3; repeated=False) |
| `DataModelEventRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`createdEventRequest: grpcRemoting.CreatedEventRequest` (Protobuf field number 2; repeated=False)<br>`modifiedEventRequest: grpcRemoting.ModifiedEventRequest` (Protobuf field number 3; repeated=False)<br>`deletedEventRequest: grpcRemoting.DeletedEventRequest` (Protobuf field number 4; repeated=False)<br>`affectedEventRequest: grpcRemoting.AffectedEventRequest` (Protobuf field number 5; repeated=False)<br>`attributeChangedEventRequest: grpcRemoting.AttributeChangedEventRequest` (Protobuf field number 6; repeated=False)<br>`commandAttributeChangedEventRequest: grpcRemoting.CommandAttributeChangedEventRequest` (Protobuf field number 7; repeated=False)<br>`commandExecutedEventRequest: grpcRemoting.CommandExecutedEventRequest` (Protobuf field number 8; repeated=False) |
| `DataModelRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`returnstatechanges: bool` (Protobuf field number 2; repeated=False)<br>`diffstate: grpcRemoting.DiffState` (Protobuf field number 3; repeated=False) |
| `DataModelResponse` | `state: utils.Variant` (Protobuf field number 1; repeated=False)<br>`deletedpaths: string` (Protobuf field number 2; repeated=True)<br>`events: string` (Protobuf field number 3; repeated=True) |
| `DeleteChildObjectsRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`child_names: grpcRemoting.ChildNames` (Protobuf field number 3; repeated=False)<br>`delete_all: bool` (Protobuf field number 4; repeated=False)<br>`wait: bool` (Protobuf field number 5; repeated=False) |
| `DeleteChildObjectsResponse` | `state: utils.Variant` (Protobuf field number 1; repeated=False)<br>`deletedpaths: string` (Protobuf field number 2; repeated=True) |
| `DeleteCommandArgumentsRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`command: string` (Protobuf field number 3; repeated=False)<br>`commandid: string` (Protobuf field number 4; repeated=False) |
| `DeleteCommandArgumentsResponse` | — |
| `DeleteObjectRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`wait: bool` (Protobuf field number 3; repeated=False) |
| `DeleteObjectResponse` | `state: utils.Variant` (Protobuf field number 1; repeated=False)<br>`deletedpaths: string` (Protobuf field number 2; repeated=True) |
| `DeletedEventRequest` | `path: string` (Protobuf field number 1; repeated=False) |
| `DeletedEventResponse` | `path: string` (Protobuf field number 1; repeated=False) |
| `EventRequest` | — |
| `EventResponse` | `tag: string` (Protobuf field number 1; repeated=False)<br>`rules: string` (Protobuf field number 2; repeated=False)<br>`createdEventResponse: grpcRemoting.CreatedEventResponse` (Protobuf field number 3; repeated=False)<br>`modifiedEventResponse: grpcRemoting.ModifiedEventResponse` (Protobuf field number 4; repeated=False)<br>`deletedEventResponse: grpcRemoting.DeletedEventResponse` (Protobuf field number 5; repeated=False)<br>`affectedEventResponse: grpcRemoting.AffectedEventResponse` (Protobuf field number 6; repeated=False)<br>`attributeChangedEventResponse: grpcRemoting.AttributeChangedEventResponse` (Protobuf field number 7; repeated=False)<br>`commandAttributeChangedEventResponse: grpcRemoting.CommandAttributeChangedEventResponse` (Protobuf field number 8; repeated=False)<br>`commandExecutedEventResponse: grpcRemoting.CommandExecutedEventResponse` (Protobuf field number 9; repeated=False) |
| `EventSubscription` | `tag: string` (Protobuf field number 1; repeated=False)<br>`status: grpcRemoting.SubscriptionStatus` (Protobuf field number 2; repeated=False) |
| `ExecuteCommandRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`command: string` (Protobuf field number 3; repeated=False)<br>`wait: bool` (Protobuf field number 4; repeated=False)<br>`args: utils.Variant` (Protobuf field number 5; repeated=False) |
| `ExecuteCommandResponse` | `result: utils.Variant` (Protobuf field number 1; repeated=False)<br>`state: utils.Variant` (Protobuf field number 2; repeated=False)<br>`deletedpaths: string` (Protobuf field number 3; repeated=True) |
| `ExecuteQueryRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`query: string` (Protobuf field number 3; repeated=False)<br>`args: utils.Variant` (Protobuf field number 4; repeated=False) |
| `ExecuteQueryResponse` | `result: utils.Variant` (Protobuf field number 1; repeated=False) |
| `FixStateRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False) |
| `FixStateResponse` | `state: utils.Variant` (Protobuf field number 1; repeated=False)<br>`deletedpaths: string` (Protobuf field number 2; repeated=True) |
| `GetAttributeValueRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`attribute: string` (Protobuf field number 3; repeated=False) |
| `GetAttributeValueResponse` | `result: utils.Variant` (Protobuf field number 1; repeated=False) |
| `GetObjectNamesRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False) |
| `GetObjectNamesResponse` | `names: string` (Protobuf field number 1; repeated=True) |
| `GetSpecsRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`includeChildren: bool` (Protobuf field number 3; repeated=False) |
| `GetSpecsResponse` | `member: grpcRemoting.MemberSpecs` (Protobuf field number 1; repeated=False) |
| `GetStateRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False) |
| `GetStateResponse` | `state: utils.Variant` (Protobuf field number 1; repeated=False) |
| `GetStaticInfoRequest` | `rules: string` (Protobuf field number 1; repeated=False) |
| `GetStaticInfoResponse` | `info: grpcRemoting.StaticInfo` (Protobuf field number 1; repeated=False) |
| `InitDatamodelRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`returnstatechanges: bool` (Protobuf field number 2; repeated=False) |
| `InitDatamodelResponse` | `state: utils.Variant` (Protobuf field number 1; repeated=False)<br>`deletedpaths: string` (Protobuf field number 2; repeated=True) |
| `IntListParameterSpecs` | `common: grpcRemoting.CommonSpecs` (Protobuf field number 1; repeated=False) |
| `IntParameterSpecs` | `common: grpcRemoting.CommonSpecs` (Protobuf field number 1; repeated=False)<br>`lowerbound: int32` (Protobuf field number 2; repeated=False)<br>`upperbound: int32` (Protobuf field number 3; repeated=False) |
| `MemberSpecs` | `name: string` (Protobuf field number 1; repeated=False)<br>`type: string` (Protobuf field number 2; repeated=False)<br>`bool: grpcRemoting.BoolParameterSpecs` (Protobuf field number 3; repeated=False)<br>`int: grpcRemoting.IntParameterSpecs` (Protobuf field number 4; repeated=False)<br>`real: grpcRemoting.RealParameterSpecs` (Protobuf field number 5; repeated=False)<br>`string: grpcRemoting.StringParameterSpecs` (Protobuf field number 6; repeated=False)<br>`intlist: grpcRemoting.IntListParameterSpecs` (Protobuf field number 7; repeated=False)<br>`stringlist: grpcRemoting.StringListParameterSpecs` (Protobuf field number 8; repeated=False)<br>`singleton: grpcRemoting.SingletonSpecs` (Protobuf field number 9; repeated=False)<br>`namedobject: grpcRemoting.NamedObjectSpecs` (Protobuf field number 10; repeated=False)<br>`children: grpcRemoting.MemberSpecs` (Protobuf field number 11; repeated=True) |
| `ModifiedEventRequest` | `path: string` (Protobuf field number 1; repeated=False) |
| `ModifiedEventResponse` | `path: string` (Protobuf field number 1; repeated=False)<br>`value: utils.Variant` (Protobuf field number 2; repeated=False) |
| `NamedObjectSpecs` | `common: grpcRemoting.CommonSpecs` (Protobuf field number 1; repeated=False)<br>`members: string` (Protobuf field number 2; repeated=True)<br>`commands: grpcRemoting.CommandSpecs` (Protobuf field number 3; repeated=True)<br>`creatabletypes: string` (Protobuf field number 4; repeated=True) |
| `RealParameterSpecs` | `common: grpcRemoting.CommonSpecs` (Protobuf field number 1; repeated=False)<br>`lowerbound: double` (Protobuf field number 2; repeated=False)<br>`upperbound: double` (Protobuf field number 3; repeated=False) |
| `RenameRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`new_name: string` (Protobuf field number 3; repeated=False)<br>`wait: bool` (Protobuf field number 4; repeated=False) |
| `RenameResponse` | `state: utils.Variant` (Protobuf field number 1; repeated=False)<br>`deletedpaths: string` (Protobuf field number 2; repeated=True) |
| `SetStateRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`state: utils.Variant` (Protobuf field number 3; repeated=False)<br>`wait: bool` (Protobuf field number 4; repeated=False) |
| `SetStateResponse` | `state: utils.Variant` (Protobuf field number 1; repeated=False)<br>`deletedpaths: string` (Protobuf field number 2; repeated=True) |
| `SingletonSpecs` | `common: grpcRemoting.CommonSpecs` (Protobuf field number 1; repeated=False)<br>`members: string` (Protobuf field number 2; repeated=True)<br>`commands: grpcRemoting.CommandSpecs` (Protobuf field number 3; repeated=True)<br>`creatabletypes: string` (Protobuf field number 4; repeated=True) |
| `StaticInfo` | `namedobjects: grpcRemoting.StaticInfo.NamedobjectsEntry` (Protobuf field number 1; repeated=True)<br>`singletons: grpcRemoting.StaticInfo.SingletonsEntry` (Protobuf field number 2; repeated=True)<br>`parameters: grpcRemoting.StaticInfo.ParametersEntry` (Protobuf field number 3; repeated=True)<br>`commands: grpcRemoting.StaticInfo.CommandsEntry` (Protobuf field number 4; repeated=True)<br>`type: string` (Protobuf field number 5; repeated=False)<br>`commandinfo: grpcRemoting.CommandInfo` (Protobuf field number 6; repeated=False)<br>`queries: grpcRemoting.StaticInfo.QueriesEntry` (Protobuf field number 7; repeated=True)<br>`queryinfo: grpcRemoting.CommandInfo` (Protobuf field number 8; repeated=False)<br>`helpstring: string` (Protobuf field number 9; repeated=False)<br>`attrs: grpcRemoting.StaticInfo.AttrsEntry` (Protobuf field number 10; repeated=True) |
| `StringListParameterSpecs` | `common: grpcRemoting.CommonSpecs` (Protobuf field number 1; repeated=False)<br>`allowedstringlist: string` (Protobuf field number 2; repeated=True) |
| `StringParameterSpecs` | `common: grpcRemoting.CommonSpecs` (Protobuf field number 1; repeated=False)<br>`allowedstringlist: string` (Protobuf field number 2; repeated=True) |
| `SubscribeEventsRequest` | `eventrequest: grpcRemoting.DataModelEventRequest` (Protobuf field number 1; repeated=True) |
| `SubscribeEventsResponse` | `response: grpcRemoting.EventSubscription` (Protobuf field number 1; repeated=True) |
| `UnsubscribeEventsRequest` | `tag: string` (Protobuf field number 1; repeated=True) |
| `UnsubscribeEventsResponse` | `response: grpcRemoting.EventSubscription` (Protobuf field number 1; repeated=True) |
| `UpdateDictRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`dicttomerge: utils.Variant` (Protobuf field number 3; repeated=False)<br>`wait: bool` (Protobuf field number 4; repeated=False)<br>`recursive: bool` (Protobuf field number 5; repeated=False) |
| `UpdateDictResponse` | `state: utils.Variant` (Protobuf field number 1; repeated=False)<br>`deletedpaths: string` (Protobuf field number 2; repeated=True) |

### `ansys.api.fluent.v0.datamodel_tui_pb2`

| Message | Fields |
| --- | --- |
| `CompositeGetRequest` | `getters: ansys.api.fluent.v0.DataModelGetter` (Protobuf field number 1; repeated=True) |
| `CompositeGetResponse` | `response: google.protobuf.Value` (Protobuf field number 1; repeated=False) |
| `DataModelGetter` | `get_attribute_value_request: ansys.api.fluent.v0.GetAttributeValueRequest` (Protobuf field number 1; repeated=False)<br>`get_state_request: ansys.api.fluent.v0.GetStateRequest` (Protobuf field number 2; repeated=False) |
| `ExecuteCommandRequest` | `path: string` (Protobuf field number 1; repeated=False)<br>`command: string` (Protobuf field number 2; repeated=False)<br>`args: google.protobuf.Struct` (Protobuf field number 3; repeated=False) |
| `ExecuteCommandResponse` | `result: google.protobuf.Value` (Protobuf field number 1; repeated=False) |
| `ExecuteQueryRequest` | `path: string` (Protobuf field number 1; repeated=False) |
| `ExecuteQueryResponse` | `result: google.protobuf.Value` (Protobuf field number 1; repeated=False) |
| `GetAttributeValueRequest` | `path: string` (Protobuf field number 1; repeated=False)<br>`attribute: ansys.api.fluent.v0.Attribute` (Protobuf field number 2; repeated=False)<br>`args: google.protobuf.Struct` (Protobuf field number 3; repeated=False) |
| `GetAttributeValueResponse` | `value: google.protobuf.Value` (Protobuf field number 1; repeated=False) |
| `GetStateRequest` | `path: string` (Protobuf field number 1; repeated=False) |
| `GetStateResponse` | `state: google.protobuf.Value` (Protobuf field number 1; repeated=False) |
| `GetStaticInfoRequest` | `path: string` (Protobuf field number 1; repeated=False) |
| `GetStaticInfoResponse` | `info: ansys.api.fluent.v0.StaticInfo` (Protobuf field number 1; repeated=False) |
| `NotifyChangesRequest` | `paths: google.protobuf.Value` (Protobuf field number 1; repeated=False)<br>`args: google.protobuf.Struct` (Protobuf field number 2; repeated=False) |
| `NotifyChangesResponse` | `changed_paths: google.protobuf.Value` (Protobuf field number 1; repeated=False)<br>`state_difference: google.protobuf.Value` (Protobuf field number 2; repeated=False) |
| `SetStateRequest` | `path: string` (Protobuf field number 1; repeated=False)<br>`state: google.protobuf.Value` (Protobuf field number 2; repeated=False) |
| `SetStateResponse` | `state: google.protobuf.Value` (Protobuf field number 1; repeated=False) |
| `StaticInfo` | `menus: ansys.api.fluent.v0.StaticInfo.MenusEntry` (Protobuf field number 1; repeated=True)<br>`commands: ansys.api.fluent.v0.StaticInfo.CommandsEntry` (Protobuf field number 2; repeated=True)<br>`help: string` (Protobuf field number 5; repeated=False) |

### `ansys.api.fluent.v0.events_pb2`

| Message | Fields |
| --- | --- |
| `AboutToInitializeEvent` | — |
| `AboutToReadCaseEvent` | `casefilepath: string` (Protobuf field number 1; repeated=False) |
| `AboutToReadDataEvent` | `datafilepath: string` (Protobuf field number 1; repeated=False) |
| `AutoPauseEvent` | `level: sint32` (Protobuf field number 1; repeated=False)<br>`index: sint64` (Protobuf field number 2; repeated=False) |
| `BeginStreamingRequest` | — |
| `BeginStreamingResponse` | `abouttoreadcaseevent: grpcRemoting.AboutToReadCaseEvent` (Protobuf field number 1; repeated=False)<br>`casereadevent: grpcRemoting.CaseReadEvent` (Protobuf field number 2; repeated=False)<br>`abouttoinitializeevent: grpcRemoting.AboutToInitializeEvent` (Protobuf field number 3; repeated=False)<br>`initializedevent: grpcRemoting.InitializedEvent` (Protobuf field number 4; repeated=False)<br>`abouttoreaddataevent: grpcRemoting.AboutToReadDataEvent` (Protobuf field number 5; repeated=False)<br>`datareadevent: grpcRemoting.DataReadEvent` (Protobuf field number 6; repeated=False)<br>`iterationstartedevent: grpcRemoting.IterationStartedEvent` (Protobuf field number 7; repeated=False)<br>`iterationendedevent: grpcRemoting.IterationEndedEvent` (Protobuf field number 8; repeated=False)<br>`timestepstartedevent: grpcRemoting.TimestepStartedEvent` (Protobuf field number 9; repeated=False)<br>`timestependedevent: grpcRemoting.TimestepEndedEvent` (Protobuf field number 10; repeated=False)<br>`calculationsstartedevent: grpcRemoting.CalculationsStartedEvent` (Protobuf field number 11; repeated=False)<br>`calculationsendedevent: grpcRemoting.CalculationsEndedEvent` (Protobuf field number 12; repeated=False)<br>`reportdefinitionchangedevent: grpcRemoting.ReportDefinitionChangedEvent` (Protobuf field number 13; repeated=False)<br>`plotsetchangedevent: grpcRemoting.PlotSetChangedEvent` (Protobuf field number 14; repeated=False)<br>`residualplotchangedevent: grpcRemoting.ResidualPlotChangedEvent` (Protobuf field number 15; repeated=False)<br>`clearsettingsdoneevent: grpcRemoting.ClearSettingsDoneEvent` (Protobuf field number 16; repeated=False)<br>`autopauseevent: grpcRemoting.AutoPauseEvent` (Protobuf field number 17; repeated=False)<br>`calculationspausedevent: grpcRemoting.CalculationsPausedEvent` (Protobuf field number 18; repeated=False)<br>`calculationsresumedevent: grpcRemoting.CalculationsResumedEvent` (Protobuf field number 19; repeated=False)<br>`progressevent: grpcRemoting.ProgressEvent` (Protobuf field number 20; repeated=False)<br>`errorevent: grpcRemoting.ErrorEvent` (Protobuf field number 21; repeated=False)<br>`commandcompletedevent: grpcRemoting.CommandCompletedEvent` (Protobuf field number 22; repeated=False)<br>`datamodelchangedevent: grpcRemoting.DataModelChangedEvent` (Protobuf field number 23; repeated=False)<br>`solvertimeestimateevent: grpcRemoting.SolverTimeEstimateEvent` (Protobuf field number 24; repeated=False)<br>`executeinclientevent: grpcRemoting.ExecuteInClientEvent` (Protobuf field number 25; repeated=False) |
| `CalculationsEndedEvent` | — |
| `CalculationsPausedEvent` | — |
| `CalculationsResumedEvent` | — |
| `CalculationsStartedEvent` | — |
| `CaseReadEvent` | `casefilepath: string` (Protobuf field number 1; repeated=False) |
| `ClearSettingsDoneEvent` | — |
| `CommandCompletedEvent` | — |
| `DataModelChangedEvent` | `paths: string` (Protobuf field number 1; repeated=True) |
| `DataReadEvent` | `datafilepath: string` (Protobuf field number 1; repeated=False) |
| `ErrorEvent` | `message: string` (Protobuf field number 1; repeated=False)<br>`errorCode: sint32` (Protobuf field number 2; repeated=False) |
| `ExecuteInClientEvent` | `function: string` (Protobuf field number 1; repeated=False)<br>`arguments: grpcRemoting.SchemePointer` (Protobuf field number 2; repeated=True) |
| `InitializedEvent` | — |
| `IterationEndedEvent` | `index: sint64` (Protobuf field number 1; repeated=False) |
| `IterationStartedEvent` | `index: sint64` (Protobuf field number 1; repeated=False) |
| `PlotSetChangedEvent` | `plotsetname: string` (Protobuf field number 1; repeated=False) |
| `ProgressEvent` | `message: string` (Protobuf field number 1; repeated=False)<br>`percentComplete: sint32` (Protobuf field number 2; repeated=False) |
| `ReportDefinitionChangedEvent` | `reportdefinitionname: string` (Protobuf field number 1; repeated=False) |
| `ResidualPlotChangedEvent` | — |
| `SolverTimeEstimateEvent` | `hours: double` (Protobuf field number 1; repeated=False)<br>`minutes: double` (Protobuf field number 2; repeated=False)<br>`seconds: double` (Protobuf field number 3; repeated=False) |
| `TimestepEndedEvent` | `index: sint64` (Protobuf field number 1; repeated=False)<br>`size: double` (Protobuf field number 2; repeated=False) |
| `TimestepStartedEvent` | `index: sint64` (Protobuf field number 1; repeated=False)<br>`size: double` (Protobuf field number 2; repeated=False) |

### `ansys.api.fluent.v0.field_data_pb2`

| Message | Fields |
| --- | --- |
| `ActiveField` | `active: sint64` (Protobuf field number 1; repeated=True) |
| `BeginFieldsStreamingRequest` | `chunkSize: uint32` (Protobuf field number 1; repeated=False)<br>`provideBytesStream: bool` (Protobuf field number 2; repeated=False) |
| `BeginFieldsStreamingResponse` | `bytePayload: bytes` (Protobuf field number 1; repeated=False)<br>`doublePayload: grpcRemoting.DoublePayload` (Protobuf field number 2; repeated=False)<br>`floatPayload: grpcRemoting.FloatPayload` (Protobuf field number 3; repeated=False)<br>`longPayload: grpcRemoting.LongPayload` (Protobuf field number 4; repeated=False)<br>`intPayload: grpcRemoting.IntPayload` (Protobuf field number 5; repeated=False)<br>`payloadInfo: grpcRemoting.PayloadInfo` (Protobuf field number 6; repeated=False) |
| `Coordinate` | `x: double` (Protobuf field number 1; repeated=False)<br>`y: double` (Protobuf field number 2; repeated=False)<br>`z: double` (Protobuf field number 3; repeated=False) |
| `DataStamping` | `datastampingtype: grpcRemoting.DataStampingType` (Protobuf field number 1; repeated=False)<br>`doublevalue: double` (Protobuf field number 2; repeated=False)<br>`intvalue: sint64` (Protobuf field number 3; repeated=False) |
| `DataStampingInfo` | `datastamping: grpcRemoting.DataStamping` (Protobuf field number 1; repeated=True) |
| `DoublePayload` | `payload: double` (Protobuf field number 1; repeated=True) |
| `Element` | `id: uint64` (Protobuf field number 1; repeated=False)<br>`element_type: grpcRemoting.CellElementType` (Protobuf field number 2; repeated=False)<br>`node_ids: uint64` (Protobuf field number 3; repeated=True)<br>`facets: grpcRemoting.Facet` (Protobuf field number 4; repeated=True) |
| `Facet` | `node: sint32` (Protobuf field number 1; repeated=True) |
| `FieldInfo` | `displayName: string` (Protobuf field number 1; repeated=False)<br>`solverName: string` (Protobuf field number 2; repeated=False)<br>`section: string` (Protobuf field number 3; repeated=False)<br>`domain: string` (Protobuf field number 4; repeated=False)<br>`quantity_name: string` (Protobuf field number 5; repeated=False) |
| `FieldRequestInfo` | `surfaceRequest: grpcRemoting.SurfaceRequest` (Protobuf field number 1; repeated=False)<br>`scalarFieldRequest: grpcRemoting.ScalarFieldRequest` (Protobuf field number 2; repeated=False)<br>`vectorFieldRequest: grpcRemoting.VectorFieldRequest` (Protobuf field number 3; repeated=False)<br>`pathlinesFieldRequest: grpcRemoting.PathlinesFieldRequest` (Protobuf field number 4; repeated=False) |
| `FloatPayload` | `payload: float` (Protobuf field number 1; repeated=True) |
| `GetFieldsInfoRequest` | — |
| `GetFieldsInfoResponse` | `fieldInfo: grpcRemoting.FieldInfo` (Protobuf field number 1; repeated=True) |
| `GetFieldsRequest` | `chunkSize: uint32` (Protobuf field number 1; repeated=False)<br>`provideBytesStream: bool` (Protobuf field number 2; repeated=False)<br>`surfaceRequest: grpcRemoting.SurfaceRequest` (Protobuf field number 3; repeated=True)<br>`scalarFieldRequest: grpcRemoting.ScalarFieldRequest` (Protobuf field number 4; repeated=True)<br>`vectorFieldRequest: grpcRemoting.VectorFieldRequest` (Protobuf field number 5; repeated=True)<br>`pathlinesFieldRequest: grpcRemoting.PathlinesFieldRequest` (Protobuf field number 6; repeated=True) |
| `GetFieldsResponse` | `bytePayload: bytes` (Protobuf field number 1; repeated=False)<br>`doublePayload: grpcRemoting.DoublePayload` (Protobuf field number 2; repeated=False)<br>`floatPayload: grpcRemoting.FloatPayload` (Protobuf field number 3; repeated=False)<br>`longPayload: grpcRemoting.LongPayload` (Protobuf field number 4; repeated=False)<br>`intPayload: grpcRemoting.IntPayload` (Protobuf field number 5; repeated=False)<br>`payloadInfo: grpcRemoting.PayloadInfo` (Protobuf field number 6; repeated=False) |
| `GetParticleTracksFieldRequest` | `releaseFrom: string` (Protobuf field number 1; repeated=True)<br>`field1: string` (Protobuf field number 2; repeated=False)<br>`field2: string` (Protobuf field number 3; repeated=False)<br>`field3: string` (Protobuf field number 4; repeated=False)<br>`vectorsOf: string` (Protobuf field number 5; repeated=False)<br>`nodeValue: bool` (Protobuf field number 6; repeated=False)<br>`skip: sint32` (Protobuf field number 7; repeated=False)<br>`singleStreamId: sint32` (Protobuf field number 8; repeated=False)<br>`coarsen: sint32` (Protobuf field number 9; repeated=False)<br>`freeStreamParticles: bool` (Protobuf field number 10; repeated=False)<br>`wallFilmParticles: bool` (Protobuf field number 11; repeated=False)<br>`pdfParticles: bool` (Protobuf field number 12; repeated=False)<br>`filter: grpcRemoting.ParticleTracksFilter` (Protobuf field number 13; repeated=False)<br>`dataStampingInfo: grpcRemoting.DataStampingInfo` (Protobuf field number 14; repeated=False) |
| `GetParticleTracksFieldResponse` | `particleTrackData: grpcRemoting.ParticleTrackData` (Protobuf field number 1; repeated=False) |
| `GetPathlinesFieldRequest` | `releaseFrom: grpcRemoting.SurfaceId` (Protobuf field number 1; repeated=True)<br>`field1: string` (Protobuf field number 2; repeated=False)<br>`field2: string` (Protobuf field number 3; repeated=False)<br>`nodeValue: bool` (Protobuf field number 4; repeated=False)<br>`steps: sint32` (Protobuf field number 5; repeated=False)<br>`stepSize: double` (Protobuf field number 6; repeated=False)<br>`skip: sint32` (Protobuf field number 8; repeated=False)<br>`reverse: bool` (Protobuf field number 9; repeated=False)<br>`accuracyControlOn: bool` (Protobuf field number 10; repeated=False)<br>`tolerance: double` (Protobuf field number 11; repeated=False)<br>`coarsen: sint32` (Protobuf field number 12; repeated=False)<br>`zone: string` (Protobuf field number 13; repeated=False)<br>`velocityDomain: string` (Protobuf field number 14; repeated=False)<br>`dataStampingInfo: grpcRemoting.DataStampingInfo` (Protobuf field number 15; repeated=False)<br>`zones: string` (Protobuf field number 16; repeated=True) |
| `GetPathlinesFieldResponse` | `pathlineData: grpcRemoting.PathlineData` (Protobuf field number 1; repeated=False) |
| `GetRangeRequest` | `fieldName: string` (Protobuf field number 1; repeated=False)<br>`surfaceid: grpcRemoting.SurfaceId` (Protobuf field number 2; repeated=True)<br>`nodeValue: bool` (Protobuf field number 3; repeated=False) |
| `GetRangeResponse` | `minimum: double` (Protobuf field number 1; repeated=False)<br>`maximum: double` (Protobuf field number 2; repeated=False) |
| `GetScalarFieldRequest` | `surfaceid: grpcRemoting.SurfaceId` (Protobuf field number 1; repeated=True)<br>`scalarfield: string` (Protobuf field number 2; repeated=False)<br>`nodevalue: bool` (Protobuf field number 3; repeated=False)<br>`boundaryvalues: bool` (Protobuf field number 7; repeated=False)<br>`datastampinginfo: grpcRemoting.DataStampingInfo` (Protobuf field number 4; repeated=False)<br>`availablesurfaces: grpcRemoting.SurfaceId` (Protobuf field number 5; repeated=True)<br>`availablescalarfield: grpcRemoting.SurfaceId` (Protobuf field number 6; repeated=True) |
| `GetScalarFieldResponse` | `scalarfielddata: grpcRemoting.ScalarFieldData` (Protobuf field number 1; repeated=False) |
| `GetSolverMeshElementsRequest` | `domain_id: uint64` (Protobuf field number 1; repeated=False)<br>`thread_id: uint64` (Protobuf field number 2; repeated=False) |
| `GetSolverMeshElementsResponse` | `elements: grpcRemoting.Element` (Protobuf field number 1; repeated=True) |
| `GetSolverMeshNodesDoubleResponse` | `nodes: grpcRemoting.NodeDouble` (Protobuf field number 1; repeated=True) |
| `GetSolverMeshNodesFloatResponse` | `nodes: grpcRemoting.NodeFloat` (Protobuf field number 1; repeated=True) |
| `GetSolverMeshNodesRequest` | `domain_id: uint64` (Protobuf field number 1; repeated=False)<br>`thread_id: uint64` (Protobuf field number 2; repeated=False) |
| `GetSurfacesInfoRequest` | — |
| `GetSurfacesInfoResponse` | `surfaceInfo: grpcRemoting.SurfaceInfo` (Protobuf field number 1; repeated=True) |
| `GetSurfacesRequest` | `surfaceid: grpcRemoting.SurfaceId` (Protobuf field number 1; repeated=True)<br>`oversetMesh: bool` (Protobuf field number 2; repeated=False)<br>`datastampinginfo: grpcRemoting.DataStampingInfo` (Protobuf field number 3; repeated=False)<br>`availablesurfaces: grpcRemoting.SurfaceId` (Protobuf field number 4; repeated=True) |
| `GetSurfacesResponse` | `surfacedata: grpcRemoting.SurfaceData` (Protobuf field number 1; repeated=False) |
| `GetVectorFieldRequest` | `surfaceid: grpcRemoting.SurfaceId` (Protobuf field number 1; repeated=True)<br>`scalarfield: string` (Protobuf field number 2; repeated=False)<br>`nodevalue: bool` (Protobuf field number 3; repeated=False)<br>`vectorfield: string` (Protobuf field number 4; repeated=False)<br>`datastampinginfo: grpcRemoting.DataStampingInfo` (Protobuf field number 6; repeated=False)<br>`availablesurfaces: grpcRemoting.SurfaceId` (Protobuf field number 7; repeated=True)<br>`availablescalarfield: grpcRemoting.SurfaceId` (Protobuf field number 8; repeated=True)<br>`availablevectorfield: grpcRemoting.SurfaceId` (Protobuf field number 9; repeated=True) |
| `GetVectorFieldResponse` | `vectorfielddata: grpcRemoting.VectorFieldData` (Protobuf field number 1; repeated=False) |
| `GetVectorFieldsInfoRequest` | — |
| `GetVectorFieldsInfoResponse` | `vectorFieldInfo: grpcRemoting.VectorFieldInfo` (Protobuf field number 1; repeated=True) |
| `GlobalRange` | `globalmin: double` (Protobuf field number 1; repeated=False)<br>`globalmax: double` (Protobuf field number 2; repeated=False) |
| `IntPayload` | `payload: sint32` (Protobuf field number 1; repeated=True) |
| `IsBoundaryValuesOnRequest` | — |
| `IsBoundaryValuesOnResponse` | `isboundaryvalueson: bool` (Protobuf field number 1; repeated=False) |
| `LongPayload` | `payload: sint64` (Protobuf field number 1; repeated=True) |
| `NodeDouble` | `id: uint64` (Protobuf field number 1; repeated=False)<br>`x: double` (Protobuf field number 2; repeated=False)<br>`y: double` (Protobuf field number 3; repeated=False)<br>`z: double` (Protobuf field number 4; repeated=False) |
| `NodeFloat` | `id: uint64` (Protobuf field number 1; repeated=False)<br>`x: float` (Protobuf field number 2; repeated=False)<br>`y: float` (Protobuf field number 3; repeated=False)<br>`z: float` (Protobuf field number 4; repeated=False) |
| `ParticleTrackData` | `particleTrackFieldData: grpcRemoting.ParticleTrackFieldData` (Protobuf field number 1; repeated=False)<br>`particleTrackMetaData: grpcRemoting.ParticleTrackMetaData` (Protobuf field number 2; repeated=False) |
| `ParticleTrackFieldData` | `particleId: sint64` (Protobuf field number 1; repeated=False)<br>`particlePosition: grpcRemoting.ScalarField` (Protobuf field number 2; repeated=False)<br>`particleTime: grpcRemoting.ScalarField` (Protobuf field number 3; repeated=False)<br>`field1: grpcRemoting.ScalarField` (Protobuf field number 4; repeated=False)<br>`field2: grpcRemoting.ScalarField` (Protobuf field number 5; repeated=False)<br>`field3: grpcRemoting.ScalarField` (Protobuf field number 6; repeated=False)<br>`particleVelocity: grpcRemoting.VectorField` (Protobuf field number 7; repeated=False)<br>`particleStartTime: double` (Protobuf field number 8; repeated=False)<br>`particleEndTime: double` (Protobuf field number 9; repeated=False) |
| `ParticleTrackMetaData` | `dataStampingInfo: grpcRemoting.DataStampingInfo` (Protobuf field number 1; repeated=False)<br>`lengthUnit: grpcRemoting.UnitInfo` (Protobuf field number 2; repeated=False)<br>`scalarFieldRange: grpcRemoting.GlobalRange` (Protobuf field number 3; repeated=False)<br>`scalarFieldUnit: grpcRemoting.UnitInfo` (Protobuf field number 4; repeated=False)<br>`twistRange: grpcRemoting.GlobalRange` (Protobuf field number 5; repeated=False)<br>`timeUnit: grpcRemoting.UnitInfo` (Protobuf field number 6; repeated=False) |
| `ParticleTracksFilter` | `field: string` (Protobuf field number 1; repeated=False)<br>`filterRange: grpcRemoting.GlobalRange` (Protobuf field number 2; repeated=False)<br>`insideRange: bool` (Protobuf field number 3; repeated=False) |
| `PathlineData` | `pathlineFieldData: grpcRemoting.PathlineFieldData` (Protobuf field number 1; repeated=False)<br>`pathlineMetaData: grpcRemoting.PathlineMetaData` (Protobuf field number 2; repeated=False) |
| `PathlineFieldData` | `particleId: sint64` (Protobuf field number 1; repeated=False)<br>`particlePositions: double` (Protobuf field number 2; repeated=True)<br>`particleTime: double` (Protobuf field number 3; repeated=True)<br>`field1: double` (Protobuf field number 4; repeated=True)<br>`field2: double` (Protobuf field number 5; repeated=True)<br>`beginStep: sint64` (Protobuf field number 6; repeated=False)<br>`endStep: sint64` (Protobuf field number 7; repeated=False) |
| `PathlineMetaData` | `dataStampingInfo: grpcRemoting.DataStampingInfo` (Protobuf field number 1; repeated=False)<br>`lengthUnit: grpcRemoting.UnitInfo` (Protobuf field number 2; repeated=False)<br>`scalarFieldRange: grpcRemoting.GlobalRange` (Protobuf field number 3; repeated=False)<br>`scalarFieldUnit: grpcRemoting.UnitInfo` (Protobuf field number 4; repeated=False)<br>`twistRange: grpcRemoting.GlobalRange` (Protobuf field number 5; repeated=False)<br>`timeUnit: grpcRemoting.UnitInfo` (Protobuf field number 6; repeated=False) |
| `PathlinesFieldRequest` | `surfaceId: uint64` (Protobuf field number 1; repeated=False)<br>`field: string` (Protobuf field number 2; repeated=False)<br>`additionalField: string` (Protobuf field number 3; repeated=False)<br>`provideParticleTimeField: bool` (Protobuf field number 4; repeated=False)<br>`dataLocation: grpcRemoting.DataLocation` (Protobuf field number 5; repeated=False)<br>`steps: sint32` (Protobuf field number 6; repeated=False)<br>`stepSize: double` (Protobuf field number 7; repeated=False)<br>`skip: sint32` (Protobuf field number 8; repeated=False)<br>`reverse: bool` (Protobuf field number 9; repeated=False)<br>`accuracyControlOn: bool` (Protobuf field number 10; repeated=False)<br>`tolerance: double` (Protobuf field number 11; repeated=False)<br>`coarsen: sint32` (Protobuf field number 12; repeated=False)<br>`velocityDomain: string` (Protobuf field number 13; repeated=False)<br>`zones: string` (Protobuf field number 14; repeated=True) |
| `PayloadInfo` | `surfaceId: uint64` (Protobuf field number 1; repeated=False)<br>`fieldName: string` (Protobuf field number 2; repeated=False)<br>`fieldType: grpcRemoting.FieldType` (Protobuf field number 3; repeated=False)<br>`fieldSize: uint64` (Protobuf field number 4; repeated=False)<br>`payloadTag: grpcRemoting.PayloadTag` (Protobuf field number 5; repeated=True)<br>`fieldRequestInfo: grpcRemoting.FieldRequestInfo` (Protobuf field number 6; repeated=False) |
| `ScalarField` | `data: double` (Protobuf field number 1; repeated=True) |
| `ScalarFieldData` | `surfaceid: grpcRemoting.SurfaceId` (Protobuf field number 1; repeated=False)<br>`surfacedata: grpcRemoting.SurfaceData` (Protobuf field number 2; repeated=False)<br>`scalarfield: grpcRemoting.ScalarField` (Protobuf field number 3; repeated=False)<br>`activefield: grpcRemoting.ActiveField` (Protobuf field number 4; repeated=False)<br>`empty_state: grpcRemoting.Empty` (Protobuf field number 5; repeated=False)<br>`scalarfieldmetadata: grpcRemoting.ScalarFieldMetaData` (Protobuf field number 6; repeated=False) |
| `ScalarFieldMetaData` | `datastampinginfo: grpcRemoting.DataStampingInfo` (Protobuf field number 1; repeated=False)<br>`lengthunit: grpcRemoting.UnitInfo` (Protobuf field number 2; repeated=False)<br>`scalarFieldrange: grpcRemoting.GlobalRange` (Protobuf field number 3; repeated=False)<br>`scalarfieldunit: grpcRemoting.UnitInfo` (Protobuf field number 4; repeated=False) |
| `ScalarFieldRequest` | `surfaceId: uint64` (Protobuf field number 1; repeated=False)<br>`scalarFieldName: string` (Protobuf field number 2; repeated=False)<br>`dataLocation: grpcRemoting.DataLocation` (Protobuf field number 3; repeated=False)<br>`provideBoundaryValues: bool` (Protobuf field number 4; repeated=False) |
| `SurfaceData` | `surfaceid: grpcRemoting.SurfaceId` (Protobuf field number 1; repeated=False)<br>`point: grpcRemoting.Coordinate` (Protobuf field number 2; repeated=True)<br>`facet: grpcRemoting.Facet` (Protobuf field number 3; repeated=True)<br>`empty_state: grpcRemoting.Empty` (Protobuf field number 5; repeated=False)<br>`surfacemetadata: grpcRemoting.SurfaceMetaData` (Protobuf field number 6; repeated=False) |
| `SurfaceId` | `id: sint64` (Protobuf field number 1; repeated=False) |
| `SurfaceInfo` | `surfaceId: grpcRemoting.SurfaceId` (Protobuf field number 1; repeated=True)<br>`zoneId: grpcRemoting.SurfaceId` (Protobuf field number 2; repeated=False)<br>`surfaceName: string` (Protobuf field number 3; repeated=False)<br>`zoneType: string` (Protobuf field number 4; repeated=False)<br>`type: string` (Protobuf field number 5; repeated=False) |
| `SurfaceMetaData` | `datastampinginfo: grpcRemoting.DataStampingInfo` (Protobuf field number 1; repeated=False)<br>`lengthunit: grpcRemoting.UnitInfo` (Protobuf field number 2; repeated=False) |
| `SurfaceRequest` | `surfaceId: uint64` (Protobuf field number 1; repeated=False)<br>`oversetMesh: bool` (Protobuf field number 2; repeated=False)<br>`provideVertices: bool` (Protobuf field number 3; repeated=False)<br>`provideFaces: bool` (Protobuf field number 4; repeated=False)<br>`provideFacesCentroid: bool` (Protobuf field number 5; repeated=False)<br>`provideFacesNormal: bool` (Protobuf field number 6; repeated=False) |
| `UnitInfo` | `name: string` (Protobuf field number 1; repeated=False)<br>`unit: string` (Protobuf field number 2; repeated=False)<br>`factor: double` (Protobuf field number 3; repeated=False)<br>`offset: double` (Protobuf field number 4; repeated=False)<br>`label: string` (Protobuf field number 5; repeated=False) |
| `VectorComponents` | `x: double` (Protobuf field number 1; repeated=False)<br>`y: double` (Protobuf field number 2; repeated=False)<br>`z: double` (Protobuf field number 3; repeated=False) |
| `VectorField` | `vectorComponents: grpcRemoting.VectorComponents` (Protobuf field number 1; repeated=True) |
| `VectorFieldData` | `surfaceid: grpcRemoting.SurfaceId` (Protobuf field number 1; repeated=False)<br>`surfacedata: grpcRemoting.SurfaceData` (Protobuf field number 2; repeated=False)<br>`scalarfield: grpcRemoting.ScalarField` (Protobuf field number 3; repeated=False)<br>`activefield: grpcRemoting.ActiveField` (Protobuf field number 4; repeated=False)<br>`empty_state: grpcRemoting.Empty` (Protobuf field number 5; repeated=False)<br>`vectorfieldmetadata: grpcRemoting.VectorFieldMetaData` (Protobuf field number 6; repeated=False)<br>`base: grpcRemoting.VectorField` (Protobuf field number 7; repeated=False)<br>`vector: grpcRemoting.VectorField` (Protobuf field number 8; repeated=False)<br>`normal: grpcRemoting.VectorField` (Protobuf field number 9; repeated=False)<br>`vectorscale: grpcRemoting.VectorScale` (Protobuf field number 10; repeated=False) |
| `VectorFieldInfo` | `displayName: string` (Protobuf field number 1; repeated=False)<br>`xComponent: string` (Protobuf field number 2; repeated=False)<br>`yComponent: string` (Protobuf field number 3; repeated=False)<br>`zComponent: string` (Protobuf field number 4; repeated=False) |
| `VectorFieldMetaData` | `datastampinginfo: grpcRemoting.DataStampingInfo` (Protobuf field number 1; repeated=False)<br>`lengthunit: grpcRemoting.UnitInfo` (Protobuf field number 2; repeated=False)<br>`scalarFieldrange: grpcRemoting.GlobalRange` (Protobuf field number 3; repeated=False)<br>`scalarfieldunit: grpcRemoting.UnitInfo` (Protobuf field number 4; repeated=False) |
| `VectorFieldRequest` | `surfaceId: uint64` (Protobuf field number 1; repeated=False)<br>`vectorFieldName: string` (Protobuf field number 2; repeated=False) |
| `VectorScale` | `data: double` (Protobuf field number 1; repeated=False) |

### `ansys.api.fluent.v0.health_pb2`

| Message | Fields |
| --- | --- |
| `HealthCheckRequest` | `service: string` (Protobuf field number 1; repeated=False) |
| `HealthCheckResponse` | `status: grpc.health.v1.HealthCheckResponse.ServingStatus` (Protobuf field number 1; repeated=False) |

### `ansys.api.fluent.v0.meshing_queries_pb2`

| Message | Fields |
| --- | --- |
| `CustomDoubleAndString` | `volume: double` (Protobuf field number 1; repeated=False)<br>`region: string` (Protobuf field number 2; repeated=False) |
| `Empty` | — |
| `FindJoinPairsRequest` | `face_zone_name_or_pattern: string` (Protobuf field number 1; repeated=False)<br>`face_zone_ids: sint64` (Protobuf field number 2; repeated=True)<br>`face_zone_names: string` (Protobuf field number 3; repeated=True)<br>`join_tolerance: double` (Protobuf field number 4; repeated=False)<br>`absolute_tolerance: bool` (Protobuf field number 5; repeated=False)<br>`join_angle: double` (Protobuf field number 6; repeated=False) |
| `FindJoinPairsResponse` | `pairs: ansys.api.fluent.v0.OverlappingBoundingBox` (Protobuf field number 1; repeated=True) |
| `GetAdjacentCellZonesRequest` | `zone_name_or_pattern: string` (Protobuf field number 1; repeated=False)<br>`face_zone_ids: sint64` (Protobuf field number 2; repeated=True) |
| `GetAdjacentCellZonesResponse` | `adjacent_cell_zones: sint64` (Protobuf field number 1; repeated=True) |
| `GetAdjacentFaceZonesRequest` | `zone_name_or_pattern: string` (Protobuf field number 1; repeated=False)<br>`cell_zone_ids: sint64` (Protobuf field number 2; repeated=True) |
| `GetAdjacentFaceZonesResponse` | `adjacent_boundary_face_zones: sint64` (Protobuf field number 1; repeated=True) |
| `GetAdjacentInteriorAndBoundaryFaceZonesRequest` | `zone_name_or_pattern: string` (Protobuf field number 1; repeated=False)<br>`cell_zone_ids: sint64` (Protobuf field number 2; repeated=True) |
| `GetAdjacentInteriorAndBoundaryFaceZonesResponse` | `adjacent_interior_and_boundary_face_zones: sint64` (Protobuf field number 1; repeated=True) |
| `GetAdjacentZonesByEdgeConnectivityRequest` | `zone_name_or_pattern: string` (Protobuf field number 1; repeated=False)<br>`zone_ids: sint64` (Protobuf field number 2; repeated=True) |
| `GetAdjacentZonesByEdgeConnectivityResponse` | `adjacent_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetAdjacentZonesByNodeConnectivityRequest` | `zone_name_or_pattern: string` (Protobuf field number 1; repeated=False)<br>`zone_ids: sint64` (Protobuf field number 2; repeated=True) |
| `GetAdjacentZonesByNodeConnectivityResponse` | `adjacent_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetAllObjectNameListResponse` | `objects: string` (Protobuf field number 1; repeated=True) |
| `GetBafflesRequest` | `face_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetBafflesResponse` | `baffle_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetCellZoneAtLocationRequest` | `location: ansys.api.fluent.v0.Point` (Protobuf field number 1; repeated=False) |
| `GetCellZoneAtLocationResponse` | `cell_zone_id: sint64` (Protobuf field number 1; repeated=False) |
| `GetCellZoneIdListOfObjectRequest` | `object: string` (Protobuf field number 1; repeated=False) |
| `GetCellZoneIdListOfObjectResponse` | `cell_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetCellZoneListByMaximumEntityCountRequest` | `maximum_entity_count: sint64` (Protobuf field number 1; repeated=False) |
| `GetCellZoneListByMaximumEntityCountResponse` | `cell_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetCellZonesOfFilterRequest` | `filter: string` (Protobuf field number 1; repeated=False) |
| `GetCellZonesOfFilterResponse` | `cell_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetEdgeZoneIdListOfObjectRequest` | `object: string` (Protobuf field number 1; repeated=False) |
| `GetEdgeZoneIdListOfObjectResponse` | `edge_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetEdgeZoneListByMaximumEntityCountRequest` | `maximum_entity_count: sint64` (Protobuf field number 1; repeated=False)<br>`only_boundary: bool` (Protobuf field number 2; repeated=False) |
| `GetEdgeZoneListByMaximumEntityCountResponse` | `edge_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetEdgeZonesOfFilterRequest` | `filter: string` (Protobuf field number 1; repeated=False) |
| `GetEdgeZonesOfFilterResponse` | `edge_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetEdgeZonesOfObjectsRequest` | `object_list: string` (Protobuf field number 1; repeated=True) |
| `GetEdgeZonesOfObjectsResponse` | `edge_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetEmbeddedBafflesResponse` | `embedded_baffles_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetFaceZoneAtLocationRequest` | `location: ansys.api.fluent.v0.Point` (Protobuf field number 1; repeated=False) |
| `GetFaceZoneAtLocationResponse` | `face_zone_id: sint64` (Protobuf field number 1; repeated=False) |
| `GetFaceZoneIdListOfLabelsRequest` | `object: string` (Protobuf field number 1; repeated=False)<br>`labels: string` (Protobuf field number 2; repeated=True) |
| `GetFaceZoneIdListOfLabelsResponse` | `zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetFaceZoneIdListOfObjectRequest` | `object: string` (Protobuf field number 1; repeated=False) |
| `GetFaceZoneIdListOfObjectResponse` | `face_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetFaceZoneIdListOfRegionsRequest` | `object: string` (Protobuf field number 1; repeated=False)<br>`labels: string` (Protobuf field number 2; repeated=True) |
| `GetFaceZoneIdListOfRegionsResponse` | `zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetFaceZoneListByMaximumEntityCountRequest` | `maximum_entity_count: sint64` (Protobuf field number 1; repeated=False)<br>`only_boundary: bool` (Protobuf field number 2; repeated=False) |
| `GetFaceZoneListByMaximumEntityCountResponse` | `face_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetFaceZoneListByMaximumZoneAreaRequest` | `maximum_zone_area: sint64` (Protobuf field number 1; repeated=False) |
| `GetFaceZoneListByMaximumZoneAreaResponse` | `face_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetFaceZoneListByMinimumZoneAreaRequest` | `minimum_zone_area: sint64` (Protobuf field number 1; repeated=False) |
| `GetFaceZoneListByMinimumZoneAreaResponse` | `face_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetFaceZonesOfFilterRequest` | `filter: string` (Protobuf field number 1; repeated=False) |
| `GetFaceZonesOfFilterResponse` | `face_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetFaceZonesOfLabelsRequest` | `object: string` (Protobuf field number 1; repeated=False)<br>`labels: string` (Protobuf field number 2; repeated=True) |
| `GetFaceZonesOfLabelsResponse` | `zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetFaceZonesOfObjectsRequest` | `object_list: string` (Protobuf field number 1; repeated=True) |
| `GetFaceZonesOfObjectsResponse` | `face_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetFaceZonesOfPrismControlsRequest` | `control_name: string` (Protobuf field number 1; repeated=False) |
| `GetFaceZonesOfPrismControlsResponse` | `face_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetFaceZonesOfRegionsRequest` | `object: string` (Protobuf field number 1; repeated=False)<br>`regions: string` (Protobuf field number 2; repeated=True) |
| `GetFaceZonesOfRegionsResponse` | `zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetFaceZonesSharedByRegionsOfTypeRequest` | `mesh_object: string` (Protobuf field number 1; repeated=False)<br>`region_type: string` (Protobuf field number 2; repeated=False) |
| `GetFaceZonesSharedByRegionsOfTypeResponse` | `shared_face_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetFaceZonesWithZoneSpecificPrismsAppliedResponse` | `face_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetInteriorZonesConnectedToCellZonesRequest` | `cell_zone_name_or_pattern: string` (Protobuf field number 1; repeated=False)<br>`face_zone_ids: sint64` (Protobuf field number 2; repeated=True) |
| `GetInteriorZonesConnectedToCellZonesResponse` | `interior_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetMaxsizeCellZoneByCountRequest` | `cell_zone_pattern: string` (Protobuf field number 1; repeated=False)<br>`cell_zone_ids: sint64` (Protobuf field number 2; repeated=True)<br>`cell_zone_names: string` (Protobuf field number 3; repeated=True) |
| `GetMaxsizeCellZoneByCountResponse` | `cell_zone_id: sint64` (Protobuf field number 1; repeated=False) |
| `GetMaxsizeCellZoneByVolumeRequest` | `cell_zone_pattern: string` (Protobuf field number 1; repeated=False)<br>`cell_zone_ids: sint64` (Protobuf field number 2; repeated=True)<br>`cell_zone_names: string` (Protobuf field number 3; repeated=True) |
| `GetMaxsizeCellZoneByVolumeResponse` | `cell_zone_id: sint64` (Protobuf field number 1; repeated=False) |
| `GetMinsizeFaceZoneByAreaRequest` | `face_zone_pattern: string` (Protobuf field number 1; repeated=False)<br>`face_zone_ids: sint64` (Protobuf field number 2; repeated=True)<br>`face_zone_names: string` (Protobuf field number 3; repeated=True) |
| `GetMinsizeFaceZoneByAreaResponse` | `face_zone_id: sint64` (Protobuf field number 1; repeated=False) |
| `GetMinsizeFaceZoneByCountRequest` | `face_zone_pattern: string` (Protobuf field number 1; repeated=False)<br>`face_zone_ids: sint64` (Protobuf field number 2; repeated=True)<br>`face_zone_names: string` (Protobuf field number 3; repeated=True) |
| `GetMinsizeFaceZoneByCountResponse` | `face_zone_id: sint64` (Protobuf field number 1; repeated=False) |
| `GetNodeZonesOfFilterRequest` | `filter: string` (Protobuf field number 1; repeated=False) |
| `GetNodeZonesOfFilterResponse` | `node_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetObjectNameListOfTypeRequest` | `type: string` (Protobuf field number 1; repeated=False) |
| `GetObjectNameListOfTypeResponse` | `objects: string` (Protobuf field number 1; repeated=True) |
| `GetObjectsOfFilterRequest` | `filter: string` (Protobuf field number 1; repeated=False) |
| `GetObjectsOfFilterResponse` | `objects: string` (Protobuf field number 1; repeated=True) |
| `GetObjectsOfTypeRequest` | `type: string` (Protobuf field number 1; repeated=False) |
| `GetObjectsOfTypeResponse` | `objects: string` (Protobuf field number 1; repeated=True) |
| `GetOverlappingFaceZonesRequest` | `face_zone_name_or_pattern: string` (Protobuf field number 1; repeated=False)<br>`area_tolerance: double` (Protobuf field number 2; repeated=False)<br>`distance_tolerance: double` (Protobuf field number 3; repeated=False) |
| `GetOverlappingFaceZonesResponse` | `overlapping_face_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetPrismCellZonesRequest` | `zone_name_or_pattern: string` (Protobuf field number 1; repeated=False)<br>`zones: string` (Protobuf field number 2; repeated=True) |
| `GetPrismCellZonesResponse` | `prism_cell_zones: sint64` (Protobuf field number 1; repeated=True) |
| `GetRegionNameListOfFaceZonesRequest` | `face_zone_name_or_pattern: string` (Protobuf field number 1; repeated=False)<br>`face_zone_ids: sint64` (Protobuf field number 2; repeated=True) |
| `GetRegionNameListOfFaceZonesResponse` | `regions: string` (Protobuf field number 1; repeated=True) |
| `GetRegionNameListOfObjectRequest` | `object: string` (Protobuf field number 1; repeated=False) |
| `GetRegionNameListOfObjectResponse` | `regions: string` (Protobuf field number 1; repeated=True) |
| `GetRegionNameListOfPatternRequest` | `object: string` (Protobuf field number 1; repeated=False)<br>`region_name_or_pattern: string` (Protobuf field number 2; repeated=False) |
| `GetRegionNameListOfPatternResponse` | `regions: string` (Protobuf field number 1; repeated=True) |
| `GetRegionVolumeRequest` | `object_name: string` (Protobuf field number 1; repeated=False)<br>`region_name: string` (Protobuf field number 2; repeated=False) |
| `GetRegionVolumeResponse` | `region_volume: double` (Protobuf field number 1; repeated=False) |
| `GetRegionsOfFaceZonesRequest` | `face_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetRegionsOfFaceZonesResponse` | `regions: string` (Protobuf field number 1; repeated=True) |
| `GetRegionsOfFilterRequest` | `object: string` (Protobuf field number 1; repeated=False)<br>`filter: string` (Protobuf field number 2; repeated=False) |
| `GetRegionsOfFilterResponse` | `regions: string` (Protobuf field number 1; repeated=True) |
| `GetRegionsOfObjectRequest` | `object: string` (Protobuf field number 1; repeated=False) |
| `GetRegionsOfObjectResponse` | `regions: string` (Protobuf field number 1; repeated=True) |
| `GetSharedBoundaryZonesRequest` | `cell_zone_name_or_pattern: string` (Protobuf field number 1; repeated=False)<br>`cell_zone_ids: sint64` (Protobuf field number 2; repeated=True) |
| `GetSharedBoundaryZonesResponse` | `shared_boundary_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetTetCellZonesRequest` | `zone_name_or_pattern: string` (Protobuf field number 1; repeated=False)<br>`zones: string` (Protobuf field number 2; repeated=True) |
| `GetTetCellZonesResponse` | `tet_cell_zones: sint64` (Protobuf field number 1; repeated=True) |
| `GetUnreferencedCellZoneIdListOfPatternRequest` | `pattern: string` (Protobuf field number 1; repeated=False) |
| `GetUnreferencedCellZoneIdListOfPatternResponse` | `unreferenced_cell_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetUnreferencedCellZonesOfFilterRequest` | `filter: string` (Protobuf field number 1; repeated=False) |
| `GetUnreferencedCellZonesOfFilterResponse` | `unreferenced_cell_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetUnreferencedCellZonesResponse` | `unreferenced_cell_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetUnreferencedEdgeZoneIdListOfPatternRequest` | `pattern: string` (Protobuf field number 1; repeated=False) |
| `GetUnreferencedEdgeZoneIdListOfPatternResponse` | `unreferenced_edge_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetUnreferencedEdgeZonesOfFilterRequest` | `filter: string` (Protobuf field number 1; repeated=False) |
| `GetUnreferencedEdgeZonesOfFilterResponse` | `unreferenced_edge_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetUnreferencedEdgeZonesResponse` | `unreferenced_edge_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetUnreferencedFaceZoneIdListOfPatternRequest` | `pattern: string` (Protobuf field number 1; repeated=False) |
| `GetUnreferencedFaceZoneIdListOfPatternResponse` | `unreferenced_face_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetUnreferencedFaceZonesOfFilterRequest` | `filter: string` (Protobuf field number 1; repeated=False) |
| `GetUnreferencedFaceZonesOfFilterResponse` | `unreferenced_face_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetUnreferencedFaceZonesResponse` | `unreferenced_face_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetWrappedZonesResponse` | `wrapped_face_zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetZonesOfGroupRequest` | `group: string` (Protobuf field number 1; repeated=False) |
| `GetZonesOfGroupResponse` | `zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetZonesOfTypeRequest` | `type: string` (Protobuf field number 1; repeated=False) |
| `GetZonesOfTypeResponse` | `zone_ids: sint64` (Protobuf field number 1; repeated=True) |
| `GetZonesWithFreeFacesRequest` | `face_zone_pattern: string` (Protobuf field number 1; repeated=False)<br>`face_zone_ids: sint64` (Protobuf field number 2; repeated=True)<br>`face_zone_names: string` (Protobuf field number 3; repeated=True) |
| `GetZonesWithFreeFacesResponse` | `zones_with_free_faces: sint64` (Protobuf field number 1; repeated=True) |
| `GetZonesWithMarkedFacesRequest` | `face_zone_pattern: string` (Protobuf field number 1; repeated=False)<br>`face_zone_ids: sint64` (Protobuf field number 2; repeated=True)<br>`face_zone_names: string` (Protobuf field number 3; repeated=True) |
| `GetZonesWithMarkedFacesResponse` | `zones_with_marked_faces: sint64` (Protobuf field number 1; repeated=True) |
| `GetZonesWithMultiFacesRequest` | `face_zone_pattern: string` (Protobuf field number 1; repeated=False)<br>`face_zone_ids: sint64` (Protobuf field number 2; repeated=True)<br>`face_zone_names: string` (Protobuf field number 3; repeated=True) |
| `GetZonesWithMultiFacesResponse` | `zones_with_multi_connected_faces: sint64` (Protobuf field number 1; repeated=True) |
| `OverlappingBoundingBox` | `zone_id_1: int64` (Protobuf field number 1; repeated=False)<br>`zone_id_2: int64` (Protobuf field number 2; repeated=False)<br>`bounding_box_min: double` (Protobuf field number 3; repeated=True)<br>`bounding_box_max: double` (Protobuf field number 4; repeated=True) |
| `SortRegionsByVolumeRequest` | `object_name: string` (Protobuf field number 1; repeated=False)<br>`order: string` (Protobuf field number 2; repeated=False) |
| `SortRegionsByVolumeResponse` | `regions: ansys.api.fluent.v0.CustomDoubleAndString` (Protobuf field number 1; repeated=True) |

### `ansys.api.fluent.v0.monitor_pb2`

| Message | Fields |
| --- | --- |
| `GetMonitorsRequest` | — |
| `GetMonitorsResponse` | `monitorset: grpcRemoting.MonitorSet` (Protobuf field number 1; repeated=True) |
| `MonitorData` | `name: string` (Protobuf field number 1; repeated=False)<br>`value: double` (Protobuf field number 2; repeated=False) |
| `MonitorFilter` | `xaxistype: grpcRemoting.XAxisType` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=True)<br>`frequency: sint32` (Protobuf field number 3; repeated=False) |
| `MonitorSet` | `name: string` (Protobuf field number 1; repeated=False)<br>`title: string` (Protobuf field number 2; repeated=False)<br>`xlabel: string` (Protobuf field number 3; repeated=False)<br>`ylabel: string` (Protobuf field number 4; repeated=False)<br>`frequency: sint64` (Protobuf field number 5; repeated=False)<br>`type: grpcRemoting.MonitorType` (Protobuf field number 6; repeated=False)<br>`unitinfo: grpcRemoting.UnitData` (Protobuf field number 7; repeated=False)<br>`axis: grpcRemoting.XAxisType` (Protobuf field number 8; repeated=False)<br>`monitors: string` (Protobuf field number 9; repeated=True) |
| `StreamingRequest` | `filter: grpcRemoting.MonitorFilter` (Protobuf field number 2; repeated=True) |
| `StreamingResponse` | `xaxisdata: grpcRemoting.XAxisData` (Protobuf field number 1; repeated=False)<br>`yaxisvalues: grpcRemoting.MonitorData` (Protobuf field number 2; repeated=True) |
| `UnitData` | `name: string` (Protobuf field number 1; repeated=False)<br>`unit: string` (Protobuf field number 2; repeated=False)<br>`factor: double` (Protobuf field number 3; repeated=False)<br>`offset: double` (Protobuf field number 4; repeated=False) |
| `XAxisData` | `xaxistype: grpcRemoting.XAxisType` (Protobuf field number 1; repeated=False)<br>`xaxisindex: sint64` (Protobuf field number 2; repeated=False) |

### `ansys.api.fluent.v0.reduction_pb2`

| Message | Fields |
| --- | --- |
| `AreaAveRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `AreaAveResponse` | `value: utils.Variant` (Protobuf field number 1; repeated=False) |
| `AreaIntRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `AreaIntResponse` | `value: utils.Variant` (Protobuf field number 1; repeated=False) |
| `AreaRequest` | `locations: string` (Protobuf field number 1; repeated=True) |
| `AreaResponse` | `value: utils.Variant` (Protobuf field number 1; repeated=False) |
| `CentroidRequest` | `locations: string` (Protobuf field number 1; repeated=True) |
| `CentroidResponse` | `value: ansys.api.fluent.v0.Point` (Protobuf field number 1; repeated=False) |
| `CountIfRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `CountIfResponse` | `value: utils.Variant` (Protobuf field number 1; repeated=False) |
| `CountRequest` | `locations: string` (Protobuf field number 1; repeated=True) |
| `CountResponse` | `value: utils.Variant` (Protobuf field number 1; repeated=False) |
| `ForceRequest` | `locations: string` (Protobuf field number 1; repeated=True) |
| `ForceResponse` | `value: ansys.api.fluent.v0.Point` (Protobuf field number 1; repeated=False) |
| `MassAveRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `MassAveResponse` | `value: utils.Variant` (Protobuf field number 1; repeated=False) |
| `MassFlowAveAbsRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `MassFlowAveAbsResponse` | `value: utils.Variant` (Protobuf field number 1; repeated=False) |
| `MassFlowAveRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `MassFlowAveResponse` | `value: utils.Variant` (Protobuf field number 1; repeated=False) |
| `MassFlowIntRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `MassFlowIntResponse` | `value: utils.Variant` (Protobuf field number 1; repeated=False) |
| `MassIntRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `MassIntResponse` | `value: utils.Variant` (Protobuf field number 1; repeated=False) |
| `MaximumRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `MaximumResponse` | `value: utils.Variant` (Protobuf field number 1; repeated=False) |
| `MinimumRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `MinimumResponse` | `value: utils.Variant` (Protobuf field number 1; repeated=False) |
| `MomentRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `MomentResponse` | `value: ansys.api.fluent.v0.Point` (Protobuf field number 1; repeated=False) |
| `PressureForceRequest` | `locations: string` (Protobuf field number 1; repeated=True) |
| `PressureForceResponse` | `value: ansys.api.fluent.v0.Point` (Protobuf field number 1; repeated=False) |
| `SumIfRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`condition: string` (Protobuf field number 2; repeated=False)<br>`locations: string` (Protobuf field number 3; repeated=True)<br>`weight: string` (Protobuf field number 4; repeated=False) |
| `SumIfResponse` | `value: utils.Variant` (Protobuf field number 1; repeated=False) |
| `SumRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`weight: string` (Protobuf field number 3; repeated=False) |
| `SumResponse` | `value: utils.Variant` (Protobuf field number 1; repeated=False) |
| `ViscousForceRequest` | `locations: string` (Protobuf field number 1; repeated=True) |
| `ViscousForceResponse` | `value: ansys.api.fluent.v0.Point` (Protobuf field number 1; repeated=False) |
| `VolumeAveRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `VolumeAveResponse` | `value: utils.Variant` (Protobuf field number 1; repeated=False) |
| `VolumeIntRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `VolumeIntResponse` | `value: utils.Variant` (Protobuf field number 1; repeated=False) |
| `VolumeRequest` | `locations: string` (Protobuf field number 1; repeated=True) |
| `VolumeResponse` | `value: utils.Variant` (Protobuf field number 1; repeated=False) |

### `ansys.api.fluent.v0.scheme_eval_pb2`

| Message | Fields |
| --- | --- |
| `ExecRequest` | `command: string` (Protobuf field number 1; repeated=True)<br>`wait: bool` (Protobuf field number 2; repeated=False)<br>`silent: bool` (Protobuf field number 3; repeated=False) |
| `ExecResponse` | `output: string` (Protobuf field number 1; repeated=False) |
| `SchemeEvalRequest` | `input: grpcRemoting.SchemePointer` (Protobuf field number 1; repeated=False) |
| `SchemeEvalResponse` | `output: grpcRemoting.SchemePointer` (Protobuf field number 1; repeated=False) |
| `StringEvalRequest` | `input: string` (Protobuf field number 1; repeated=False) |
| `StringEvalResponse` | `output: string` (Protobuf field number 1; repeated=False) |

### `ansys.api.fluent.v0.scheme_pointer_pb2`

| Message | Fields |
| --- | --- |
| `SchemePointer` | `empty: grpcRemoting.Empty` (Protobuf field number 1; repeated=False)<br>`sym: string` (Protobuf field number 2; repeated=False)<br>`pair: grpcRemoting.SchemePointer.SchemePair` (Protobuf field number 3; repeated=False)<br>`list: grpcRemoting.SchemePointer.SchemeList` (Protobuf field number 9; repeated=False)<br>`flonum: double` (Protobuf field number 4; repeated=False)<br>`fixednum: sint64` (Protobuf field number 5; repeated=False)<br>`c: string` (Protobuf field number 6; repeated=False)<br>`str: string` (Protobuf field number 7; repeated=False)<br>`b: bool` (Protobuf field number 8; repeated=False) |

### `ansys.api.fluent.v0.settings_pb2`

| Message | Fields |
| --- | --- |
| `AttrInfoMap` | `name: string` (Protobuf field number 1; repeated=False)<br>`value: ansys.api.fluent.v0.settings.GetAttrsResponse` (Protobuf field number 2; repeated=False) |
| `CreateRequest` | `path_info: ansys.api.fluent.v0.settings.PathInfo` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False) |
| `CreateResponse` | — |
| `DeleteRequest` | `path_info: ansys.api.fluent.v0.settings.PathInfo` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False) |
| `DeleteResponse` | — |
| `ExecuteCommandRequest` | `path_info: ansys.api.fluent.v0.settings.PathInfo` (Protobuf field number 1; repeated=False)<br>`command: string` (Protobuf field number 2; repeated=False)<br>`args: ansys.api.fluent.v0.settings.Value` (Protobuf field number 3; repeated=False) |
| `ExecuteCommandResponse` | `reply: ansys.api.fluent.v0.settings.Value` (Protobuf field number 1; repeated=False) |
| `ExecuteQueryRequest` | `path_info: ansys.api.fluent.v0.settings.PathInfo` (Protobuf field number 1; repeated=False)<br>`query: string` (Protobuf field number 2; repeated=False)<br>`args: ansys.api.fluent.v0.settings.Value` (Protobuf field number 3; repeated=False) |
| `ExecuteQueryResponse` | `reply: ansys.api.fluent.v0.settings.Value` (Protobuf field number 1; repeated=False) |
| `GetAttrsRequest` | `path_info: ansys.api.fluent.v0.settings.PathInfo` (Protobuf field number 1; repeated=False)<br>`attrs: string` (Protobuf field number 2; repeated=True)<br>`recursive: bool` (Protobuf field number 3; repeated=False) |
| `GetAttrsResponse` | `values: ansys.api.fluent.v0.settings.Value` (Protobuf field number 1; repeated=False)<br>`group_children: ansys.api.fluent.v0.settings.AttrInfoMap` (Protobuf field number 2; repeated=True) |
| `GetListSizeRequest` | `path_info: ansys.api.fluent.v0.settings.PathInfo` (Protobuf field number 1; repeated=False) |
| `GetListSizeResponse` | `size: int32` (Protobuf field number 1; repeated=False) |
| `GetObjectNamesRequest` | `path_info: ansys.api.fluent.v0.settings.PathInfo` (Protobuf field number 1; repeated=False) |
| `GetObjectNamesResponse` | `names: string` (Protobuf field number 1; repeated=True) |
| `GetStaticInfoRequest` | `root: string` (Protobuf field number 1; repeated=False)<br>`optional_attrs: string` (Protobuf field number 2; repeated=True) |
| `GetStaticInfoResponse` | `info: ansys.api.fluent.v0.settings.StaticInfo` (Protobuf field number 1; repeated=False) |
| `GetVarRequest` | `path_info: ansys.api.fluent.v0.settings.PathInfo` (Protobuf field number 1; repeated=False) |
| `GetVarResponse` | `value: ansys.api.fluent.v0.settings.Value` (Protobuf field number 1; repeated=False) |
| `PathInfo` | `root: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False) |
| `RenameRequest` | `path_info: ansys.api.fluent.v0.settings.PathInfo` (Protobuf field number 1; repeated=False)<br>`old_name: string` (Protobuf field number 2; repeated=False)<br>`new_name: string` (Protobuf field number 3; repeated=False) |
| `RenameResponse` | — |
| `ResizeListObjectRequest` | `path_info: ansys.api.fluent.v0.settings.PathInfo` (Protobuf field number 1; repeated=False)<br>`size: int32` (Protobuf field number 2; repeated=False) |
| `ResizeListObjectResponse` | — |
| `SetVarRequest` | `path_info: ansys.api.fluent.v0.settings.PathInfo` (Protobuf field number 1; repeated=False)<br>`value: ansys.api.fluent.v0.settings.Value` (Protobuf field number 2; repeated=False) |
| `SetVarResponse` | — |
| `StaticInfo` | `type: string` (Protobuf field number 1; repeated=False)<br>`children: ansys.api.fluent.v0.settings.StaticInfoMap` (Protobuf field number 2; repeated=True)<br>`commands: ansys.api.fluent.v0.settings.StaticInfoMap` (Protobuf field number 3; repeated=True)<br>`queries: ansys.api.fluent.v0.settings.StaticInfoMap` (Protobuf field number 11; repeated=True)<br>`arguments: ansys.api.fluent.v0.settings.StaticInfoMap` (Protobuf field number 4; repeated=True)<br>`object_type: ansys.api.fluent.v0.settings.StaticInfo` (Protobuf field number 5; repeated=False)<br>`help: string` (Protobuf field number 6; repeated=False)<br>`has_allowed_values: bool` (Protobuf field number 7; repeated=False)<br>`include_child_named_objects: bool` (Protobuf field number 8; repeated=False)<br>`list_size: int32` (Protobuf field number 9; repeated=False)<br>`user_creatable: bool` (Protobuf field number 10; repeated=False)<br>`attrs: ansys.api.fluent.v0.settings.StaticInfo.AttrsEntry` (Protobuf field number 12; repeated=True) |
| `StaticInfoMap` | `name: string` (Protobuf field number 1; repeated=False)<br>`value: ansys.api.fluent.v0.settings.StaticInfo` (Protobuf field number 2; repeated=False) |
| `Value` | `boolean: bool` (Protobuf field number 2; repeated=False)<br>`integer: int64` (Protobuf field number 3; repeated=False)<br>`real: double` (Protobuf field number 4; repeated=False)<br>`string: string` (Protobuf field number 5; repeated=False)<br>`value_list: ansys.api.fluent.v0.settings.Value.ValueList` (Protobuf field number 10; repeated=False)<br>`value_map: ansys.api.fluent.v0.settings.Value.ValueMap` (Protobuf field number 11; repeated=False) |

### `ansys.api.fluent.v0.svar_pb2`

| Message | Fields |
| --- | --- |
| `DomainInfo` | `name: string` (Protobuf field number 1; repeated=False)<br>`domainId: uint32` (Protobuf field number 2; repeated=False) |
| `GetSvarDataRequest` | `chunkSize: uint32` (Protobuf field number 1; repeated=False)<br>`provideBytesStream: bool` (Protobuf field number 2; repeated=False)<br>`name: string` (Protobuf field number 3; repeated=False)<br>`domainId: uint32` (Protobuf field number 4; repeated=False)<br>`zones: uint64` (Protobuf field number 5; repeated=True) |
| `GetSvarDataResponse` | `payload: grpcRemoting.Payload` (Protobuf field number 1; repeated=False)<br>`payloadInfo: grpcRemoting.Info` (Protobuf field number 2; repeated=False) |
| `GetSvarsInfoRequest` | `domainId: uint32` (Protobuf field number 1; repeated=False)<br>`zoneId: uint64` (Protobuf field number 2; repeated=False) |
| `GetSvarsInfoResponse` | `svarsInfo: grpcRemoting.SvarInfo` (Protobuf field number 1; repeated=True) |
| `GetZonesInfoRequest` | — |
| `GetZonesInfoResponse` | `domainsInfo: grpcRemoting.DomainInfo` (Protobuf field number 1; repeated=True)<br>`zonesInfo: grpcRemoting.ZoneInfo` (Protobuf field number 2; repeated=True) |
| `Info` | `fieldType: grpcRemoting.FieldType` (Protobuf field number 1; repeated=False)<br>`fieldSize: uint64` (Protobuf field number 2; repeated=False)<br>`zone: uint64` (Protobuf field number 3; repeated=False) |
| `PartitionInfo` | `count: uint64` (Protobuf field number 1; repeated=False)<br>`startIndex: uint64` (Protobuf field number 2; repeated=False)<br>`endIndex: uint64` (Protobuf field number 3; repeated=False) |
| `Payload` | `bytePayload: bytes` (Protobuf field number 1; repeated=False)<br>`doublePayload: grpcRemoting.DoublePayload` (Protobuf field number 2; repeated=False)<br>`floatPayload: grpcRemoting.FloatPayload` (Protobuf field number 3; repeated=False)<br>`longPayload: grpcRemoting.LongPayload` (Protobuf field number 4; repeated=False)<br>`intPayload: grpcRemoting.IntPayload` (Protobuf field number 5; repeated=False) |
| `SetSvarDataRequest` | `header: grpcRemoting.SvarHeader` (Protobuf field number 1; repeated=False)<br>`payload: grpcRemoting.Payload` (Protobuf field number 2; repeated=False)<br>`payloadInfo: grpcRemoting.Info` (Protobuf field number 3; repeated=False) |
| `SetSvarDataResponse` | — |
| `SvarHeader` | `name: string` (Protobuf field number 1; repeated=False)<br>`domainId: uint32` (Protobuf field number 2; repeated=False) |
| `SvarInfo` | `name: string` (Protobuf field number 1; repeated=False)<br>`dimension: uint32` (Protobuf field number 2; repeated=False)<br>`fieldType: grpcRemoting.FieldType` (Protobuf field number 3; repeated=False) |
| `ZoneInfo` | `name: string` (Protobuf field number 1; repeated=False)<br>`zoneId: uint64` (Protobuf field number 2; repeated=False)<br>`zoneType: string` (Protobuf field number 3; repeated=False)<br>`threadType: grpcRemoting.ThreadType` (Protobuf field number 4; repeated=False)<br>`partitionsInfo: grpcRemoting.PartitionInfo` (Protobuf field number 5; repeated=True) |

### `ansys.api.fluent.v0.transcript_pb2`

| Message | Fields |
| --- | --- |
| `TranscriptRequest` | — |
| `TranscriptResponse` | `transcript: string` (Protobuf field number 1; repeated=False) |

### `ansys.api.fluent.v0.variant_pb2`

| Message | Fields |
| --- | --- |
| `BoolVector` | `item: bool` (Protobuf field number 1; repeated=True) |
| `DoubleVector` | `item: double` (Protobuf field number 1; repeated=True) |
| `Empty` | — |
| `Int64Vector` | `item: sint64` (Protobuf field number 1; repeated=True) |
| `StringVector` | `item: string` (Protobuf field number 1; repeated=True) |
| `Variant` | `empty_state: utils.Empty` (Protobuf field number 1; repeated=False)<br>`bool_state: bool` (Protobuf field number 2; repeated=False)<br>`int64_state: sint64` (Protobuf field number 3; repeated=False)<br>`double_state: double` (Protobuf field number 5; repeated=False)<br>`string_state: string` (Protobuf field number 6; repeated=False)<br>`bool_vector_state: utils.BoolVector` (Protobuf field number 7; repeated=False)<br>`int64_vector_state: utils.Int64Vector` (Protobuf field number 8; repeated=False)<br>`double_vector_state: utils.DoubleVector` (Protobuf field number 9; repeated=False)<br>`string_vector_state: utils.StringVector` (Protobuf field number 10; repeated=False)<br>`variant_vector_state: utils.VariantVector` (Protobuf field number 11; repeated=False)<br>`variant_map_state: utils.VariantMap` (Protobuf field number 12; repeated=False) |
| `VariantMap` | `item: utils.VariantMap.ItemEntry` (Protobuf field number 1; repeated=True) |
| `VariantVector` | `item: utils.Variant` (Protobuf field number 1; repeated=True) |

### `ansys.api.fluent.v1.application_runtime_pb2`

| Message | Fields |
| --- | --- |
| `EnableBetaRequest` | — |
| `EnableBetaResponse` | — |
| `ExitRequest` | — |
| `ExitResponse` | — |
| `GetBuildInfoRequest` | — |
| `GetBuildInfoResponse` | `build_time: string` (Protobuf field number 1; repeated=False)<br>`build_id: int64` (Protobuf field number 2; repeated=False)<br>`vcs_revision: string` (Protobuf field number 3; repeated=False)<br>`vcs_branch: string` (Protobuf field number 4; repeated=False) |
| `GetControllerProcessInfoRequest` | — |
| `GetControllerProcessInfoResponse` | `hostname: string` (Protobuf field number 1; repeated=False)<br>`process_id: int64` (Protobuf field number 2; repeated=False)<br>`working_directory: string` (Protobuf field number 3; repeated=False) |
| `GetDimensionRequest` | — |
| `GetDimensionResponse` | `dimension: ansys.api.fluent.v1.application_runtime.Dimension` (Protobuf field number 1; repeated=False) |
| `GetGPUConfigRequest` | — |
| `GetGPUConfigResponse` | `auto_allocate: bool` (Protobuf field number 1; repeated=False)<br>`specific_gpu_ids: ansys.api.fluent.v1.application_runtime.GpuIdList` (Protobuf field number 2; repeated=False) |
| `GetGraphicsDriverRequest` | — |
| `GetGraphicsDriverResponse` | `windows_graphics_driver: ansys.api.fluent.v1.application_runtime.WindowsGraphicsDriver` (Protobuf field number 1; repeated=False)<br>`linux_graphics_driver: ansys.api.fluent.v1.application_runtime.LinuxGraphicsDriver` (Protobuf field number 2; repeated=False) |
| `GetModeRequest` | — |
| `GetModeResponse` | `mode: ansys.api.fluent.v1.application_runtime.Mode` (Protobuf field number 1; repeated=False) |
| `GetPrecisionRequest` | — |
| `GetPrecisionResponse` | `precision: ansys.api.fluent.v1.application_runtime.Precision` (Protobuf field number 1; repeated=False) |
| `GetProcessorCountRequest` | — |
| `GetProcessorCountResponse` | `processor_count: uint64` (Protobuf field number 1; repeated=False) |
| `GetProductVersionRequest` | — |
| `GetProductVersionResponse` | `major: int64` (Protobuf field number 1; repeated=False)<br>`minor: int64` (Protobuf field number 2; repeated=False)<br>`patch: int64` (Protobuf field number 3; repeated=False) |
| `GetSolverProcessInfoRequest` | — |
| `GetSolverProcessInfoResponse` | `hostname: string` (Protobuf field number 1; repeated=False)<br>`process_id: int64` (Protobuf field number 2; repeated=False)<br>`working_directory: string` (Protobuf field number 3; repeated=False) |
| `GetUIModeRequest` | — |
| `GetUIModeResponse` | `ui_mode: ansys.api.fluent.v1.application_runtime.UIMode` (Protobuf field number 1; repeated=False) |
| `GpuIdList` | `gpu_ids: uint32` (Protobuf field number 1; repeated=True) |
| `IsBetaEnabledRequest` | — |
| `IsBetaEnabledResponse` | `is_beta_enabled: bool` (Protobuf field number 1; repeated=False) |
| `SetIdleTimeoutRequest` | `timeout: google.protobuf.Duration` (Protobuf field number 1; repeated=False) |
| `SetIdleTimeoutResponse` | — |
| `SetWorkingDirectoryRequest` | `path: string` (Protobuf field number 1; repeated=False) |
| `SetWorkingDirectoryResponse` | — |
| `StartPythonJournalRequest` | `journal_name: string` (Protobuf field number 1; repeated=False) |
| `StartPythonJournalResponse` | `journal_id: string` (Protobuf field number 1; repeated=False) |
| `StopPythonJournalRequest` | `journal_id: string` (Protobuf field number 1; repeated=False) |
| `StopPythonJournalResponse` | `journal_str: string` (Protobuf field number 1; repeated=False) |

### `ansys.api.fluent.v1.connection_pb2`

| Message | Fields |
| --- | --- |
| `ConnectRequest` | `request_type: ansys.api.fluent.v1.connection.ConnectRequest.RequestType` (Protobuf field number 1; repeated=False)<br>`password: string` (Protobuf field number 2; repeated=False)<br>`version: string` (Protobuf field number 3; repeated=False) |
| `ConnectResponse` | `error_code: ansys.api.fluent.v1.connection.ConnectionError` (Protobuf field number 1; repeated=False) |

### `ansys.api.fluent.v1.events_pb2`

| Message | Fields |
| --- | --- |
| `AutoPauseEvent` | `level: sint32` (Protobuf field number 1; repeated=False)<br>`index: sint64` (Protobuf field number 2; repeated=False) |
| `BeginStreamingRequest` | — |
| `BeginStreamingResponse` | `pre_read_case_event: ansys.api.fluent.v1.events.PreReadCaseEvent` (Protobuf field number 1; repeated=False)<br>`case_read_event: ansys.api.fluent.v1.events.CaseReadEvent` (Protobuf field number 2; repeated=False)<br>`pre_initialize_event: ansys.api.fluent.v1.events.PreInitializeEvent` (Protobuf field number 3; repeated=False)<br>`initialized_event: ansys.api.fluent.v1.events.InitializedEvent` (Protobuf field number 4; repeated=False)<br>`pre_read_data_event: ansys.api.fluent.v1.events.PreReadDataEvent` (Protobuf field number 5; repeated=False)<br>`data_read_event: ansys.api.fluent.v1.events.DataReadEvent` (Protobuf field number 6; repeated=False)<br>`iteration_started_event: ansys.api.fluent.v1.events.IterationStartedEvent` (Protobuf field number 7; repeated=False)<br>`iteration_ended_event: ansys.api.fluent.v1.events.IterationEndedEvent` (Protobuf field number 8; repeated=False)<br>`timestep_started_event: ansys.api.fluent.v1.events.TimestepStartedEvent` (Protobuf field number 9; repeated=False)<br>`timestep_ended_event: ansys.api.fluent.v1.events.TimestepEndedEvent` (Protobuf field number 10; repeated=False)<br>`calculations_started_event: ansys.api.fluent.v1.events.CalculationsStartedEvent` (Protobuf field number 11; repeated=False)<br>`calculations_ended_event: ansys.api.fluent.v1.events.CalculationsEndedEvent` (Protobuf field number 12; repeated=False)<br>`report_definition_changed_event: ansys.api.fluent.v1.events.ReportDefinitionChangedEvent` (Protobuf field number 13; repeated=False)<br>`plot_set_changed_event: ansys.api.fluent.v1.events.PlotSetChangedEvent` (Protobuf field number 14; repeated=False)<br>`residual_plot_changed_event: ansys.api.fluent.v1.events.ResidualPlotChangedEvent` (Protobuf field number 15; repeated=False)<br>`clear_settings_done_event: ansys.api.fluent.v1.events.ClearSettingsDoneEvent` (Protobuf field number 16; repeated=False)<br>`auto_pause_event: ansys.api.fluent.v1.events.AutoPauseEvent` (Protobuf field number 17; repeated=False)<br>`calculations_paused_event: ansys.api.fluent.v1.events.CalculationsPausedEvent` (Protobuf field number 18; repeated=False)<br>`calculations_resumed_event: ansys.api.fluent.v1.events.CalculationsResumedEvent` (Protobuf field number 19; repeated=False)<br>`progress_event: ansys.api.fluent.v1.events.ProgressEvent` (Protobuf field number 20; repeated=False)<br>`error_event: ansys.api.fluent.v1.events.ErrorEvent` (Protobuf field number 21; repeated=False)<br>`command_completed_event: ansys.api.fluent.v1.events.CommandCompletedEvent` (Protobuf field number 22; repeated=False)<br>`data_model_changed_event: ansys.api.fluent.v1.events.DataModelChangedEvent` (Protobuf field number 23; repeated=False)<br>`solver_time_estimate_event: ansys.api.fluent.v1.events.SolverTimeEstimateEvent` (Protobuf field number 24; repeated=False)<br>`client_execute_event: ansys.api.fluent.v1.events.ClientExecuteEvent` (Protobuf field number 25; repeated=False) |
| `CalculationsEndedEvent` | — |
| `CalculationsPausedEvent` | — |
| `CalculationsResumedEvent` | — |
| `CalculationsStartedEvent` | — |
| `CancelPauseSolveRequest` | `registration_id: int64` (Protobuf field number 1; repeated=False) |
| `CancelPauseSolveResponse` | — |
| `CaseReadEvent` | `case_file_path: string` (Protobuf field number 1; repeated=False) |
| `ClearSettingsDoneEvent` | — |
| `ClientExecuteEvent` | `function: string` (Protobuf field number 1; repeated=False)<br>`arguments: ansys.api.fluent.v1.scheme_pointer.SchemePointer` (Protobuf field number 2; repeated=True) |
| `CommandCompletedEvent` | — |
| `DataModelChangedEvent` | `paths: string` (Protobuf field number 1; repeated=True) |
| `DataReadEvent` | `data_file_path: string` (Protobuf field number 1; repeated=False) |
| `ErrorEvent` | `message: string` (Protobuf field number 1; repeated=False)<br>`error_code: sint32` (Protobuf field number 2; repeated=False) |
| `InitializedEvent` | — |
| `IterationEndedEvent` | `index: sint64` (Protobuf field number 1; repeated=False) |
| `IterationStartedEvent` | `index: sint64` (Protobuf field number 1; repeated=False) |
| `PauseSolveForRequest` | `solution_event: ansys.api.fluent.v1.events.SolutionEvent` (Protobuf field number 1; repeated=False) |
| `PauseSolveForResponse` | `registration_id: int64` (Protobuf field number 1; repeated=False) |
| `PlotSetChangedEvent` | — |
| `PreInitializeEvent` | — |
| `PreReadCaseEvent` | `case_file_path: string` (Protobuf field number 1; repeated=False) |
| `PreReadDataEvent` | `data_file_path: string` (Protobuf field number 1; repeated=False) |
| `ProgressEvent` | `message: string` (Protobuf field number 1; repeated=False)<br>`percent_complete: sint32` (Protobuf field number 2; repeated=False) |
| `ReportDefinitionChangedEvent` | — |
| `ResidualPlotChangedEvent` | — |
| `ResumeSolveRequest` | `registration_id: int64` (Protobuf field number 1; repeated=False) |
| `ResumeSolveResponse` | — |
| `SolverTimeEstimateEvent` | `hours: double` (Protobuf field number 1; repeated=False)<br>`minutes: double` (Protobuf field number 2; repeated=False)<br>`seconds: double` (Protobuf field number 3; repeated=False) |
| `TimestepEndedEvent` | `index: sint64` (Protobuf field number 1; repeated=False)<br>`size: double` (Protobuf field number 2; repeated=False) |
| `TimestepStartedEvent` | `index: sint64` (Protobuf field number 1; repeated=False)<br>`size: double` (Protobuf field number 2; repeated=False) |

### `ansys.api.fluent.v1.field_data_pb2`

| Message | Fields |
| --- | --- |
| `ActiveField` | `actives: sint64` (Protobuf field number 1; repeated=True) |
| `BeginFieldsStreamingRequest` | `chunk_size: uint32` (Protobuf field number 1; repeated=False)<br>`provide_bytes_stream: bool` (Protobuf field number 2; repeated=False) |
| `BeginFieldsStreamingResponse` | `byte_payload: bytes` (Protobuf field number 1; repeated=False)<br>`double_payload: ansys.api.fluent.v1.field_data.DoublePayload` (Protobuf field number 2; repeated=False)<br>`float_payload: ansys.api.fluent.v1.field_data.FloatPayload` (Protobuf field number 3; repeated=False)<br>`long_payload: ansys.api.fluent.v1.field_data.LongPayload` (Protobuf field number 4; repeated=False)<br>`int_payload: ansys.api.fluent.v1.field_data.IntPayload` (Protobuf field number 5; repeated=False)<br>`payload_info: ansys.api.fluent.v1.field_data.PayloadInfo` (Protobuf field number 6; repeated=False) |
| `Coordinate` | `x: double` (Protobuf field number 1; repeated=False)<br>`y: double` (Protobuf field number 2; repeated=False)<br>`z: double` (Protobuf field number 3; repeated=False) |
| `DataStamping` | `data_stamping_type: ansys.api.fluent.v1.field_data.DataStampingType` (Protobuf field number 1; repeated=False)<br>`doublevalue: double` (Protobuf field number 2; repeated=False)<br>`intvalue: sint64` (Protobuf field number 3; repeated=False) |
| `DataStampingInfo` | `data_stampings: ansys.api.fluent.v1.field_data.DataStamping` (Protobuf field number 1; repeated=True) |
| `DoublePayload` | `payloads: double` (Protobuf field number 1; repeated=True) |
| `Element` | `id: uint64` (Protobuf field number 1; repeated=False)<br>`element_type: ansys.api.fluent.v1.field_data.CellElementType` (Protobuf field number 2; repeated=False)<br>`node_ids: uint64` (Protobuf field number 3; repeated=True)<br>`facets: ansys.api.fluent.v1.field_data.Facet` (Protobuf field number 4; repeated=True) |
| `Empty` | — |
| `Facet` | `nodes: sint32` (Protobuf field number 1; repeated=True) |
| `FieldInfo` | `display_name: string` (Protobuf field number 1; repeated=False)<br>`solver_name: string` (Protobuf field number 2; repeated=False)<br>`section: string` (Protobuf field number 3; repeated=False)<br>`domain: string` (Protobuf field number 4; repeated=False)<br>`quantity_name: string` (Protobuf field number 5; repeated=False) |
| `FieldRequestInfo` | `surface_request: ansys.api.fluent.v1.field_data.SurfaceRequest` (Protobuf field number 1; repeated=False)<br>`scalar_field_request: ansys.api.fluent.v1.field_data.ScalarFieldRequest` (Protobuf field number 2; repeated=False)<br>`vector_field_request: ansys.api.fluent.v1.field_data.VectorFieldRequest` (Protobuf field number 3; repeated=False)<br>`pathlines_field_request: ansys.api.fluent.v1.field_data.PathlinesFieldRequest` (Protobuf field number 4; repeated=False) |
| `FloatPayload` | `payloads: float` (Protobuf field number 1; repeated=True) |
| `GetFieldsInfoRequest` | — |
| `GetFieldsInfoResponse` | `field_info: ansys.api.fluent.v1.field_data.FieldInfo` (Protobuf field number 1; repeated=True) |
| `GetFieldsRequest` | `chunk_size: uint32` (Protobuf field number 1; repeated=False)<br>`provide_bytes_stream: bool` (Protobuf field number 2; repeated=False)<br>`surface_requests: ansys.api.fluent.v1.field_data.SurfaceRequest` (Protobuf field number 3; repeated=True)<br>`scalar_field_requests: ansys.api.fluent.v1.field_data.ScalarFieldRequest` (Protobuf field number 4; repeated=True)<br>`vector_field_requests: ansys.api.fluent.v1.field_data.VectorFieldRequest` (Protobuf field number 5; repeated=True)<br>`pathlines_field_requests: ansys.api.fluent.v1.field_data.PathlinesFieldRequest` (Protobuf field number 6; repeated=True) |
| `GetFieldsResponse` | `byte_payload: bytes` (Protobuf field number 1; repeated=False)<br>`double_payload: ansys.api.fluent.v1.field_data.DoublePayload` (Protobuf field number 2; repeated=False)<br>`float_payload: ansys.api.fluent.v1.field_data.FloatPayload` (Protobuf field number 3; repeated=False)<br>`long_payload: ansys.api.fluent.v1.field_data.LongPayload` (Protobuf field number 4; repeated=False)<br>`int_payload: ansys.api.fluent.v1.field_data.IntPayload` (Protobuf field number 5; repeated=False)<br>`payload_info: ansys.api.fluent.v1.field_data.PayloadInfo` (Protobuf field number 6; repeated=False) |
| `GetParticleTracksFieldRequest` | `release_froms: string` (Protobuf field number 1; repeated=True)<br>`field1: string` (Protobuf field number 2; repeated=False)<br>`field2: string` (Protobuf field number 3; repeated=False)<br>`field3: string` (Protobuf field number 4; repeated=False)<br>`vector_field: string` (Protobuf field number 5; repeated=False)<br>`node_value: bool` (Protobuf field number 6; repeated=False)<br>`skip: sint32` (Protobuf field number 7; repeated=False)<br>`single_stream_id: sint32` (Protobuf field number 8; repeated=False)<br>`coarsen: sint32` (Protobuf field number 9; repeated=False)<br>`free_stream_particles: bool` (Protobuf field number 10; repeated=False)<br>`wall_film_particles: bool` (Protobuf field number 11; repeated=False)<br>`pdf_particles: bool` (Protobuf field number 12; repeated=False)<br>`filter: ansys.api.fluent.v1.field_data.ParticleTracksFilter` (Protobuf field number 13; repeated=False)<br>`data_stamping_info: ansys.api.fluent.v1.field_data.DataStampingInfo` (Protobuf field number 14; repeated=False) |
| `GetParticleTracksFieldResponse` | `particle_track_data: ansys.api.fluent.v1.field_data.ParticleTrackData` (Protobuf field number 1; repeated=False) |
| `GetPathlinesFieldRequest` | `release_froms: ansys.api.fluent.v1.field_data.SurfaceId` (Protobuf field number 1; repeated=True)<br>`field1: string` (Protobuf field number 2; repeated=False)<br>`field2: string` (Protobuf field number 3; repeated=False)<br>`node_value: bool` (Protobuf field number 4; repeated=False)<br>`steps: sint32` (Protobuf field number 5; repeated=False)<br>`step_size: double` (Protobuf field number 6; repeated=False)<br>`skip: sint32` (Protobuf field number 8; repeated=False)<br>`reverse: bool` (Protobuf field number 9; repeated=False)<br>`accuracy_control_enabled: bool` (Protobuf field number 10; repeated=False)<br>`tolerance: double` (Protobuf field number 11; repeated=False)<br>`coarsen: sint32` (Protobuf field number 12; repeated=False)<br>`zone: string` (Protobuf field number 13; repeated=False)<br>`velocity_domain: string` (Protobuf field number 14; repeated=False)<br>`data_stamping_info: ansys.api.fluent.v1.field_data.DataStampingInfo` (Protobuf field number 15; repeated=False)<br>`zones: string` (Protobuf field number 16; repeated=True) |
| `GetPathlinesFieldResponse` | `pathline_data: ansys.api.fluent.v1.field_data.PathlineData` (Protobuf field number 1; repeated=False) |
| `GetRangeRequest` | `field_name: string` (Protobuf field number 1; repeated=False)<br>`surface_ids: ansys.api.fluent.v1.field_data.SurfaceId` (Protobuf field number 2; repeated=True)<br>`node_value: bool` (Protobuf field number 3; repeated=False) |
| `GetRangeResponse` | `minimum: double` (Protobuf field number 1; repeated=False)<br>`maximum: double` (Protobuf field number 2; repeated=False) |
| `GetScalarFieldRequest` | `surface_ids: ansys.api.fluent.v1.field_data.SurfaceId` (Protobuf field number 1; repeated=True)<br>`scalar_field: string` (Protobuf field number 2; repeated=False)<br>`node_value: bool` (Protobuf field number 3; repeated=False)<br>`data_stamping_info: ansys.api.fluent.v1.field_data.DataStampingInfo` (Protobuf field number 4; repeated=False)<br>`available_surfaces: ansys.api.fluent.v1.field_data.SurfaceId` (Protobuf field number 5; repeated=True)<br>`available_scalar_fields: ansys.api.fluent.v1.field_data.SurfaceId` (Protobuf field number 6; repeated=True)<br>`boundary_values: bool` (Protobuf field number 7; repeated=False) |
| `GetScalarFieldResponse` | `scalar_field_data: ansys.api.fluent.v1.field_data.ScalarFieldData` (Protobuf field number 1; repeated=False) |
| `GetSolverMeshElementsRequest` | `domain_id: uint64` (Protobuf field number 1; repeated=False)<br>`thread_id: uint64` (Protobuf field number 2; repeated=False) |
| `GetSolverMeshElementsResponse` | `elements: ansys.api.fluent.v1.field_data.Element` (Protobuf field number 1; repeated=True) |
| `GetSolverMeshNodesDoubleResponse` | `nodes: ansys.api.fluent.v1.field_data.NodeDouble` (Protobuf field number 1; repeated=True) |
| `GetSolverMeshNodesFloatResponse` | `nodes: ansys.api.fluent.v1.field_data.NodeFloat` (Protobuf field number 1; repeated=True) |
| `GetSolverMeshNodesRequest` | `domain_id: uint64` (Protobuf field number 1; repeated=False)<br>`thread_id: uint64` (Protobuf field number 2; repeated=False) |
| `GetSurfacesInfoRequest` | — |
| `GetSurfacesInfoResponse` | `surface_info: ansys.api.fluent.v1.field_data.SurfaceInfo` (Protobuf field number 1; repeated=True) |
| `GetSurfacesRequest` | `surface_ids: ansys.api.fluent.v1.field_data.SurfaceId` (Protobuf field number 1; repeated=True)<br>`overset_mesh: bool` (Protobuf field number 2; repeated=False)<br>`data_stamping_info: ansys.api.fluent.v1.field_data.DataStampingInfo` (Protobuf field number 3; repeated=False)<br>`available_surfaces: ansys.api.fluent.v1.field_data.SurfaceId` (Protobuf field number 4; repeated=True) |
| `GetSurfacesResponse` | `surface_data: ansys.api.fluent.v1.field_data.SurfaceData` (Protobuf field number 1; repeated=False) |
| `GetVectorFieldRequest` | `surface_ids: ansys.api.fluent.v1.field_data.SurfaceId` (Protobuf field number 1; repeated=True)<br>`scalar_field: string` (Protobuf field number 2; repeated=False)<br>`node_value: bool` (Protobuf field number 3; repeated=False)<br>`vector_field: string` (Protobuf field number 4; repeated=False)<br>`data_stamping_info: ansys.api.fluent.v1.field_data.DataStampingInfo` (Protobuf field number 6; repeated=False)<br>`available_surfaces: ansys.api.fluent.v1.field_data.SurfaceId` (Protobuf field number 7; repeated=True)<br>`available_scalar_fields: ansys.api.fluent.v1.field_data.SurfaceId` (Protobuf field number 8; repeated=True)<br>`available_vector_fields: ansys.api.fluent.v1.field_data.SurfaceId` (Protobuf field number 9; repeated=True) |
| `GetVectorFieldResponse` | `vector_field_data: ansys.api.fluent.v1.field_data.VectorFieldData` (Protobuf field number 1; repeated=False) |
| `GetVectorFieldsInfoRequest` | — |
| `GetVectorFieldsInfoResponse` | `vector_field_info: ansys.api.fluent.v1.field_data.VectorFieldInfo` (Protobuf field number 1; repeated=True) |
| `GlobalRange` | `global_min: double` (Protobuf field number 1; repeated=False)<br>`global_max: double` (Protobuf field number 2; repeated=False) |
| `IntPayload` | `payloads: sint32` (Protobuf field number 1; repeated=True) |
| `IsBoundaryValuesEnabledRequest` | — |
| `IsBoundaryValuesEnabledResponse` | `is_boundary_values_enabled: bool` (Protobuf field number 1; repeated=False) |
| `IsDataAvailableRequest` | — |
| `IsDataAvailableResponse` | `is_data_available: bool` (Protobuf field number 1; repeated=False) |
| `LongPayload` | `payloads: sint64` (Protobuf field number 1; repeated=True) |
| `NodeDouble` | `id: uint64` (Protobuf field number 1; repeated=False)<br>`x: double` (Protobuf field number 2; repeated=False)<br>`y: double` (Protobuf field number 3; repeated=False)<br>`z: double` (Protobuf field number 4; repeated=False) |
| `NodeFloat` | `id: uint64` (Protobuf field number 1; repeated=False)<br>`x: float` (Protobuf field number 2; repeated=False)<br>`y: float` (Protobuf field number 3; repeated=False)<br>`z: float` (Protobuf field number 4; repeated=False) |
| `ParticleTrackData` | `particle_track_field_data: ansys.api.fluent.v1.field_data.ParticleTrackFieldData` (Protobuf field number 1; repeated=False)<br>`particle_track_meta_data: ansys.api.fluent.v1.field_data.ParticleTrackMetaData` (Protobuf field number 2; repeated=False) |
| `ParticleTrackFieldData` | `particle_id: sint64` (Protobuf field number 1; repeated=False)<br>`particle_position: ansys.api.fluent.v1.field_data.ScalarField` (Protobuf field number 2; repeated=False)<br>`particle_time: ansys.api.fluent.v1.field_data.ScalarField` (Protobuf field number 3; repeated=False)<br>`field1: ansys.api.fluent.v1.field_data.ScalarField` (Protobuf field number 4; repeated=False)<br>`field2: ansys.api.fluent.v1.field_data.ScalarField` (Protobuf field number 5; repeated=False)<br>`field3: ansys.api.fluent.v1.field_data.ScalarField` (Protobuf field number 6; repeated=False)<br>`particle_velocity: ansys.api.fluent.v1.field_data.VectorField` (Protobuf field number 7; repeated=False)<br>`particle_start_time: double` (Protobuf field number 8; repeated=False)<br>`particle_end_time: double` (Protobuf field number 9; repeated=False) |
| `ParticleTrackMetaData` | `data_stamping_info: ansys.api.fluent.v1.field_data.DataStampingInfo` (Protobuf field number 1; repeated=False)<br>`length_unit: ansys.api.fluent.v1.field_data.UnitInfo` (Protobuf field number 2; repeated=False)<br>`scalar_field_range: ansys.api.fluent.v1.field_data.GlobalRange` (Protobuf field number 3; repeated=False)<br>`scalar_field_unit: ansys.api.fluent.v1.field_data.UnitInfo` (Protobuf field number 4; repeated=False)<br>`twist_range: ansys.api.fluent.v1.field_data.GlobalRange` (Protobuf field number 5; repeated=False)<br>`time_unit: ansys.api.fluent.v1.field_data.UnitInfo` (Protobuf field number 6; repeated=False) |
| `ParticleTracksFilter` | `field: string` (Protobuf field number 1; repeated=False)<br>`filter_range: ansys.api.fluent.v1.field_data.GlobalRange` (Protobuf field number 2; repeated=False)<br>`inside_range: bool` (Protobuf field number 3; repeated=False) |
| `PathlineData` | `pathline_field_data: ansys.api.fluent.v1.field_data.PathlineFieldData` (Protobuf field number 1; repeated=False)<br>`pathline_metadata: ansys.api.fluent.v1.field_data.PathlineMetaData` (Protobuf field number 2; repeated=False) |
| `PathlineFieldData` | `particle_id: sint64` (Protobuf field number 1; repeated=False)<br>`particle_positions: double` (Protobuf field number 2; repeated=True)<br>`particle_times: double` (Protobuf field number 3; repeated=True)<br>`field1s: double` (Protobuf field number 4; repeated=True)<br>`field2s: double` (Protobuf field number 5; repeated=True)<br>`begin_step: sint64` (Protobuf field number 6; repeated=False)<br>`end_step: sint64` (Protobuf field number 7; repeated=False) |
| `PathlineMetaData` | `data_stamping_info: ansys.api.fluent.v1.field_data.DataStampingInfo` (Protobuf field number 1; repeated=False)<br>`length_unit: ansys.api.fluent.v1.field_data.UnitInfo` (Protobuf field number 2; repeated=False)<br>`scalar_field_range: ansys.api.fluent.v1.field_data.GlobalRange` (Protobuf field number 3; repeated=False)<br>`scalar_field_unit: ansys.api.fluent.v1.field_data.UnitInfo` (Protobuf field number 4; repeated=False)<br>`twist_range: ansys.api.fluent.v1.field_data.GlobalRange` (Protobuf field number 5; repeated=False)<br>`time_unit: ansys.api.fluent.v1.field_data.UnitInfo` (Protobuf field number 6; repeated=False) |
| `PathlinesFieldRequest` | `surface_id: uint64` (Protobuf field number 1; repeated=False)<br>`field: string` (Protobuf field number 2; repeated=False)<br>`additional_field: string` (Protobuf field number 3; repeated=False)<br>`provide_particle_time_field: bool` (Protobuf field number 4; repeated=False)<br>`data_location: ansys.api.fluent.v1.field_data.DataLocation` (Protobuf field number 5; repeated=False)<br>`steps: sint32` (Protobuf field number 6; repeated=False)<br>`step_size: double` (Protobuf field number 7; repeated=False)<br>`skip: sint32` (Protobuf field number 8; repeated=False)<br>`reverse: bool` (Protobuf field number 9; repeated=False)<br>`accuracy_control_enabled: bool` (Protobuf field number 10; repeated=False)<br>`tolerance: double` (Protobuf field number 11; repeated=False)<br>`coarsen: sint32` (Protobuf field number 12; repeated=False)<br>`velocity_domain: string` (Protobuf field number 13; repeated=False)<br>`zones: string` (Protobuf field number 14; repeated=True) |
| `PayloadInfo` | `surface_id: uint64` (Protobuf field number 1; repeated=False)<br>`field_name: string` (Protobuf field number 2; repeated=False)<br>`field_type: ansys.api.fluent.v1.field_data.FieldType` (Protobuf field number 3; repeated=False)<br>`field_size: uint64` (Protobuf field number 4; repeated=False)<br>`payload_tags: ansys.api.fluent.v1.field_data.PayloadTag` (Protobuf field number 5; repeated=True)<br>`field_request_info: ansys.api.fluent.v1.field_data.FieldRequestInfo` (Protobuf field number 6; repeated=False) |
| `ScalarField` | `data: double` (Protobuf field number 1; repeated=True) |
| `ScalarFieldData` | `surface_id: ansys.api.fluent.v1.field_data.SurfaceId` (Protobuf field number 1; repeated=False)<br>`surface_data: ansys.api.fluent.v1.field_data.SurfaceData` (Protobuf field number 2; repeated=False)<br>`scalar_field: ansys.api.fluent.v1.field_data.ScalarField` (Protobuf field number 3; repeated=False)<br>`active_field: ansys.api.fluent.v1.field_data.ActiveField` (Protobuf field number 4; repeated=False)<br>`empty_state: ansys.api.fluent.v1.field_data.Empty` (Protobuf field number 5; repeated=False)<br>`scalar_field_metadata: ansys.api.fluent.v1.field_data.ScalarFieldMetaData` (Protobuf field number 6; repeated=False) |
| `ScalarFieldMetaData` | `data_stamping_info: ansys.api.fluent.v1.field_data.DataStampingInfo` (Protobuf field number 1; repeated=False)<br>`length_unit: ansys.api.fluent.v1.field_data.UnitInfo` (Protobuf field number 2; repeated=False)<br>`scalar_field_range: ansys.api.fluent.v1.field_data.GlobalRange` (Protobuf field number 3; repeated=False)<br>`scalar_field_unit: ansys.api.fluent.v1.field_data.UnitInfo` (Protobuf field number 4; repeated=False) |
| `ScalarFieldRequest` | `surface_id: uint64` (Protobuf field number 1; repeated=False)<br>`scalar_field_name: string` (Protobuf field number 2; repeated=False)<br>`data_location: ansys.api.fluent.v1.field_data.DataLocation` (Protobuf field number 3; repeated=False)<br>`provide_boundary_values: bool` (Protobuf field number 4; repeated=False) |
| `SurfaceData` | `surface_id: ansys.api.fluent.v1.field_data.SurfaceId` (Protobuf field number 1; repeated=False)<br>`points: ansys.api.fluent.v1.field_data.Coordinate` (Protobuf field number 2; repeated=True)<br>`facets: ansys.api.fluent.v1.field_data.Facet` (Protobuf field number 3; repeated=True)<br>`empty_state: ansys.api.fluent.v1.field_data.Empty` (Protobuf field number 5; repeated=False)<br>`surface_metadata: ansys.api.fluent.v1.field_data.SurfaceMetaData` (Protobuf field number 6; repeated=False) |
| `SurfaceId` | `id: sint64` (Protobuf field number 1; repeated=False) |
| `SurfaceInfo` | `surface_ids: ansys.api.fluent.v1.field_data.SurfaceId` (Protobuf field number 1; repeated=True)<br>`zone_id: ansys.api.fluent.v1.field_data.SurfaceId` (Protobuf field number 2; repeated=False)<br>`surface_name: string` (Protobuf field number 3; repeated=False)<br>`zone_type: string` (Protobuf field number 4; repeated=False)<br>`type: string` (Protobuf field number 5; repeated=False) |
| `SurfaceMetaData` | `data_stamping_info: ansys.api.fluent.v1.field_data.DataStampingInfo` (Protobuf field number 1; repeated=False)<br>`length_unit: ansys.api.fluent.v1.field_data.UnitInfo` (Protobuf field number 2; repeated=False) |
| `SurfaceRequest` | `surface_id: uint64` (Protobuf field number 1; repeated=False)<br>`overset_mesh: bool` (Protobuf field number 2; repeated=False)<br>`provide_vertices: bool` (Protobuf field number 3; repeated=False)<br>`provide_faces: bool` (Protobuf field number 4; repeated=False)<br>`provide_faces_centroid: bool` (Protobuf field number 5; repeated=False)<br>`provide_faces_normal: bool` (Protobuf field number 6; repeated=False) |
| `UnitInfo` | `name: string` (Protobuf field number 1; repeated=False)<br>`unit: string` (Protobuf field number 2; repeated=False)<br>`factor: double` (Protobuf field number 3; repeated=False)<br>`offset: double` (Protobuf field number 4; repeated=False)<br>`label: string` (Protobuf field number 5; repeated=False) |
| `VectorComponents` | `x: double` (Protobuf field number 1; repeated=False)<br>`y: double` (Protobuf field number 2; repeated=False)<br>`z: double` (Protobuf field number 3; repeated=False) |
| `VectorField` | `vector_components: ansys.api.fluent.v1.field_data.VectorComponents` (Protobuf field number 1; repeated=True) |
| `VectorFieldData` | `surface_id: ansys.api.fluent.v1.field_data.SurfaceId` (Protobuf field number 1; repeated=False)<br>`surface_data: ansys.api.fluent.v1.field_data.SurfaceData` (Protobuf field number 2; repeated=False)<br>`scalar_field: ansys.api.fluent.v1.field_data.ScalarField` (Protobuf field number 3; repeated=False)<br>`active_field: ansys.api.fluent.v1.field_data.ActiveField` (Protobuf field number 4; repeated=False)<br>`empty_state: ansys.api.fluent.v1.field_data.Empty` (Protobuf field number 5; repeated=False)<br>`vector_field_metadata: ansys.api.fluent.v1.field_data.VectorFieldMetaData` (Protobuf field number 6; repeated=False)<br>`base: ansys.api.fluent.v1.field_data.VectorField` (Protobuf field number 7; repeated=False)<br>`vector: ansys.api.fluent.v1.field_data.VectorField` (Protobuf field number 8; repeated=False)<br>`normal: ansys.api.fluent.v1.field_data.VectorField` (Protobuf field number 9; repeated=False)<br>`vector_scale: ansys.api.fluent.v1.field_data.VectorScale` (Protobuf field number 10; repeated=False) |
| `VectorFieldInfo` | `display_name: string` (Protobuf field number 1; repeated=False)<br>`x_component: string` (Protobuf field number 2; repeated=False)<br>`y_component: string` (Protobuf field number 3; repeated=False)<br>`z_component: string` (Protobuf field number 4; repeated=False) |
| `VectorFieldMetaData` | `data_stamping_info: ansys.api.fluent.v1.field_data.DataStampingInfo` (Protobuf field number 1; repeated=False)<br>`length_unit: ansys.api.fluent.v1.field_data.UnitInfo` (Protobuf field number 2; repeated=False)<br>`scalar_field_range: ansys.api.fluent.v1.field_data.GlobalRange` (Protobuf field number 3; repeated=False)<br>`scalar_field_unit: ansys.api.fluent.v1.field_data.UnitInfo` (Protobuf field number 4; repeated=False) |
| `VectorFieldRequest` | `surface_id: uint64` (Protobuf field number 1; repeated=False)<br>`vector_field_name: string` (Protobuf field number 2; repeated=False) |
| `VectorScale` | `data: double` (Protobuf field number 1; repeated=False) |

### `ansys.api.fluent.v1.health_pb2`

| Message | Fields |
| --- | --- |
| `HealthCheckRequest` | `service: string` (Protobuf field number 1; repeated=False) |
| `HealthCheckResponse` | `status: ansys.api.fluent.v1.health.HealthCheckResponse.ServingStatus` (Protobuf field number 1; repeated=False) |

### `ansys.api.fluent.v1.monitor_pb2`

| Message | Fields |
| --- | --- |
| `GetMonitorsRequest` | — |
| `GetMonitorsResponse` | `monitor_sets: ansys.api.fluent.v1.monitor.MonitorSet` (Protobuf field number 1; repeated=True) |
| `MonitorData` | `name: string` (Protobuf field number 1; repeated=False)<br>`value: double` (Protobuf field number 2; repeated=False) |
| `MonitorFilter` | `x_axis_type: ansys.api.fluent.v1.monitor.XAxisType` (Protobuf field number 1; repeated=False)<br>`monitor_names: string` (Protobuf field number 2; repeated=True)<br>`frequency: sint32` (Protobuf field number 3; repeated=False) |
| `MonitorSet` | `name: string` (Protobuf field number 1; repeated=False)<br>`title: string` (Protobuf field number 2; repeated=False)<br>`x_label: string` (Protobuf field number 3; repeated=False)<br>`y_label: string` (Protobuf field number 4; repeated=False)<br>`frequency: sint64` (Protobuf field number 5; repeated=False)<br>`type: ansys.api.fluent.v1.monitor.MonitorType` (Protobuf field number 6; repeated=False)<br>`unit_info: ansys.api.fluent.v1.monitor.UnitData` (Protobuf field number 7; repeated=False)<br>`axis: ansys.api.fluent.v1.monitor.XAxisType` (Protobuf field number 8; repeated=False)<br>`monitors: string` (Protobuf field number 9; repeated=True) |
| `StreamingRequest` | `filters: ansys.api.fluent.v1.monitor.MonitorFilter` (Protobuf field number 1; repeated=True) |
| `StreamingResponse` | `x_axis_data: ansys.api.fluent.v1.monitor.XAxisData` (Protobuf field number 1; repeated=False)<br>`y_axis_values: ansys.api.fluent.v1.monitor.MonitorData` (Protobuf field number 2; repeated=True) |
| `UnitData` | `name: string` (Protobuf field number 1; repeated=False)<br>`unit: string` (Protobuf field number 2; repeated=False)<br>`factor: double` (Protobuf field number 3; repeated=False)<br>`offset: double` (Protobuf field number 4; repeated=False) |
| `XAxisData` | `x_axis_type: ansys.api.fluent.v1.monitor.XAxisType` (Protobuf field number 1; repeated=False)<br>`x_axis_index: sint64` (Protobuf field number 2; repeated=False) |

### `ansys.api.fluent.v1.object_model_pb2`

| Message | Fields |
| --- | --- |
| `AffectedEventRequest` | `path: string` (Protobuf field number 1; repeated=False)<br>`subtype: string` (Protobuf field number 2; repeated=False) |
| `AffectedEventResponse` | `path: string` (Protobuf field number 1; repeated=False)<br>`subtype: string` (Protobuf field number 2; repeated=False) |
| `AttributeChangedEventRequest` | `path: string` (Protobuf field number 1; repeated=False)<br>`attribute: string` (Protobuf field number 2; repeated=False) |
| `AttributeChangedEventResponse` | `path: string` (Protobuf field number 1; repeated=False)<br>`attribute: string` (Protobuf field number 2; repeated=False)<br>`value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 3; repeated=False) |
| `ChildNames` | `names: string` (Protobuf field number 1; repeated=True) |
| `CommandArg` | `type: string` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`info: ansys.api.fluent.v1.object_model.Schema` (Protobuf field number 3; repeated=False)<br>`help_string: string` (Protobuf field number 4; repeated=False)<br>`attrs: ansys.api.fluent.v1.object_model.CommandArg.AttrsEntry` (Protobuf field number 5; repeated=True)<br>`doc_string: string` (Protobuf field number 6; repeated=False) |
| `CommandAttributeChangedEventRequest` | `path: string` (Protobuf field number 1; repeated=False)<br>`command: string` (Protobuf field number 2; repeated=False)<br>`attribute: string` (Protobuf field number 3; repeated=False) |
| `CommandAttributeChangedEventResponse` | `path: string` (Protobuf field number 1; repeated=False)<br>`command: string` (Protobuf field number 2; repeated=False)<br>`attribute: string` (Protobuf field number 3; repeated=False)<br>`value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 4; repeated=False) |
| `CommandExecutedEventRequest` | `path: string` (Protobuf field number 1; repeated=False)<br>`command: string` (Protobuf field number 2; repeated=False) |
| `CommandExecutedEventResponse` | `path: string` (Protobuf field number 1; repeated=False)<br>`command: string` (Protobuf field number 2; repeated=False)<br>`args: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 3; repeated=False) |
| `CommandInfo` | `return_type: string` (Protobuf field number 1; repeated=False)<br>`args: ansys.api.fluent.v1.object_model.CommandArg` (Protobuf field number 2; repeated=True)<br>`doc_string: string` (Protobuf field number 3; repeated=False) |
| `CreateCommandArgumentsRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`command: string` (Protobuf field number 3; repeated=False) |
| `CreateCommandArgumentsResponse` | `command_id: string` (Protobuf field number 1; repeated=False) |
| `CreateObjectRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`name: string` (Protobuf field number 3; repeated=False)<br>`wait: bool` (Protobuf field number 4; repeated=False) |
| `CreateObjectResponse` | `state: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False)<br>`deleted_paths: string` (Protobuf field number 2; repeated=True) |
| `CreatedEventRequest` | `parent_path: string` (Protobuf field number 1; repeated=False)<br>`child_type: string` (Protobuf field number 2; repeated=False) |
| `CreatedEventResponse` | `parent_path: string` (Protobuf field number 1; repeated=False)<br>`child_type: string` (Protobuf field number 2; repeated=False)<br>`child_name: string` (Protobuf field number 3; repeated=False) |
| `DeleteChildObjectsRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`child_names: ansys.api.fluent.v1.object_model.ChildNames` (Protobuf field number 3; repeated=False)<br>`delete_all: bool` (Protobuf field number 4; repeated=False)<br>`wait: bool` (Protobuf field number 5; repeated=False) |
| `DeleteChildObjectsResponse` | `state: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False)<br>`deleted_paths: string` (Protobuf field number 2; repeated=True) |
| `DeleteCommandArgumentsRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`command: string` (Protobuf field number 3; repeated=False)<br>`command_id: string` (Protobuf field number 4; repeated=False) |
| `DeleteCommandArgumentsResponse` | — |
| `DeleteObjectRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`wait: bool` (Protobuf field number 3; repeated=False) |
| `DeleteObjectResponse` | `state: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False)<br>`deleted_paths: string` (Protobuf field number 2; repeated=True) |
| `DeletedEventRequest` | `path: string` (Protobuf field number 1; repeated=False) |
| `DeletedEventResponse` | `path: string` (Protobuf field number 1; repeated=False) |
| `EventSubscription` | `tag: string` (Protobuf field number 1; repeated=False)<br>`status: ansys.api.fluent.v1.object_model.SubscriptionStatus` (Protobuf field number 2; repeated=False) |
| `ExecuteCommandRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`command: string` (Protobuf field number 3; repeated=False)<br>`wait: bool` (Protobuf field number 4; repeated=False)<br>`args: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 5; repeated=False) |
| `ExecuteCommandResponse` | `result: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False)<br>`state: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 2; repeated=False)<br>`deleted_paths: string` (Protobuf field number 3; repeated=True) |
| `ExecuteQueryRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`query: string` (Protobuf field number 3; repeated=False)<br>`args: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 4; repeated=False) |
| `ExecuteQueryResponse` | `result: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |
| `FixStateRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False) |
| `FixStateResponse` | `state: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False)<br>`deleted_paths: string` (Protobuf field number 2; repeated=True) |
| `GetAttributeValueRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`attribute: string` (Protobuf field number 3; repeated=False) |
| `GetAttributeValueResponse` | `result: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |
| `GetObjectNamesRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False) |
| `GetObjectNamesResponse` | `names: string` (Protobuf field number 1; repeated=True) |
| `GetSchemaRequest` | `rules: string` (Protobuf field number 1; repeated=False) |
| `GetSchemaResponse` | `info: ansys.api.fluent.v1.object_model.Schema` (Protobuf field number 1; repeated=False) |
| `GetStateRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False) |
| `GetStateResponse` | `state: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |
| `ModifiedEventRequest` | `path: string` (Protobuf field number 1; repeated=False) |
| `ModifiedEventResponse` | `path: string` (Protobuf field number 1; repeated=False)<br>`value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 2; repeated=False) |
| `ObjectModelEventRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`created_event_request: ansys.api.fluent.v1.object_model.CreatedEventRequest` (Protobuf field number 2; repeated=False)<br>`modified_event_request: ansys.api.fluent.v1.object_model.ModifiedEventRequest` (Protobuf field number 3; repeated=False)<br>`deleted_event_request: ansys.api.fluent.v1.object_model.DeletedEventRequest` (Protobuf field number 4; repeated=False)<br>`affected_event_request: ansys.api.fluent.v1.object_model.AffectedEventRequest` (Protobuf field number 5; repeated=False)<br>`attribute_changed_event_request: ansys.api.fluent.v1.object_model.AttributeChangedEventRequest` (Protobuf field number 6; repeated=False)<br>`command_attribute_changed_event_request: ansys.api.fluent.v1.object_model.CommandAttributeChangedEventRequest` (Protobuf field number 7; repeated=False)<br>`command_executed_event_request: ansys.api.fluent.v1.object_model.CommandExecutedEventRequest` (Protobuf field number 8; repeated=False) |
| `RenameRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`new_name: string` (Protobuf field number 3; repeated=False)<br>`wait: bool` (Protobuf field number 4; repeated=False) |
| `RenameResponse` | `state: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False)<br>`deleted_paths: string` (Protobuf field number 2; repeated=True) |
| `Schema` | `named_objects: ansys.api.fluent.v1.object_model.Schema.NamedObjectsEntry` (Protobuf field number 1; repeated=True)<br>`singletons: ansys.api.fluent.v1.object_model.Schema.SingletonsEntry` (Protobuf field number 2; repeated=True)<br>`parameters: ansys.api.fluent.v1.object_model.Schema.ParametersEntry` (Protobuf field number 3; repeated=True)<br>`commands: ansys.api.fluent.v1.object_model.Schema.CommandsEntry` (Protobuf field number 4; repeated=True)<br>`type: string` (Protobuf field number 5; repeated=False)<br>`command_info: ansys.api.fluent.v1.object_model.CommandInfo` (Protobuf field number 6; repeated=False)<br>`queries: ansys.api.fluent.v1.object_model.Schema.QueriesEntry` (Protobuf field number 7; repeated=True)<br>`query_info: ansys.api.fluent.v1.object_model.CommandInfo` (Protobuf field number 8; repeated=False)<br>`help_string: string` (Protobuf field number 9; repeated=False)<br>`attrs: ansys.api.fluent.v1.object_model.Schema.AttrsEntry` (Protobuf field number 10; repeated=True) |
| `SetStateRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`state: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 3; repeated=False)<br>`wait: bool` (Protobuf field number 4; repeated=False) |
| `SetStateResponse` | `state: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False)<br>`deleted_paths: string` (Protobuf field number 2; repeated=True) |
| `StreamEventsRequest` | — |
| `StreamEventsResponse` | `tag: string` (Protobuf field number 1; repeated=False)<br>`rules: string` (Protobuf field number 2; repeated=False)<br>`created_event_response: ansys.api.fluent.v1.object_model.CreatedEventResponse` (Protobuf field number 3; repeated=False)<br>`modified_event_response: ansys.api.fluent.v1.object_model.ModifiedEventResponse` (Protobuf field number 4; repeated=False)<br>`deleted_event_response: ansys.api.fluent.v1.object_model.DeletedEventResponse` (Protobuf field number 5; repeated=False)<br>`affected_event_response: ansys.api.fluent.v1.object_model.AffectedEventResponse` (Protobuf field number 6; repeated=False)<br>`attribute_changed_event_response: ansys.api.fluent.v1.object_model.AttributeChangedEventResponse` (Protobuf field number 7; repeated=False)<br>`command_attribute_changed_event_response: ansys.api.fluent.v1.object_model.CommandAttributeChangedEventResponse` (Protobuf field number 8; repeated=False)<br>`command_executed_event_response: ansys.api.fluent.v1.object_model.CommandExecutedEventResponse` (Protobuf field number 9; repeated=False) |
| `StreamStateChangesRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`return_state_changes: bool` (Protobuf field number 2; repeated=False)<br>`diff_state: ansys.api.fluent.v1.object_model.DiffState` (Protobuf field number 3; repeated=False) |
| `StreamStateChangesResponse` | `state: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False)<br>`deleted_paths: string` (Protobuf field number 2; repeated=True)<br>`events: string` (Protobuf field number 3; repeated=True) |
| `SubscribeEventsRequest` | `event_requests: ansys.api.fluent.v1.object_model.ObjectModelEventRequest` (Protobuf field number 1; repeated=True) |
| `SubscribeEventsResponse` | `responses: ansys.api.fluent.v1.object_model.EventSubscription` (Protobuf field number 1; repeated=True) |
| `UnsubscribeEventsRequest` | `tags: string` (Protobuf field number 1; repeated=True) |
| `UnsubscribeEventsResponse` | `responses: ansys.api.fluent.v1.object_model.EventSubscription` (Protobuf field number 1; repeated=True) |
| `UpdateDictRequest` | `rules: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False)<br>`merge_dict: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 3; repeated=False)<br>`wait: bool` (Protobuf field number 4; repeated=False)<br>`recursive: bool` (Protobuf field number 5; repeated=False) |
| `UpdateDictResponse` | `state: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False)<br>`deleted_paths: string` (Protobuf field number 2; repeated=True) |

### `ansys.api.fluent.v1.primitives_pb2`

| Message | Fields |
| --- | --- |
| `Point` | `x: double` (Protobuf field number 1; repeated=False)<br>`y: double` (Protobuf field number 2; repeated=False)<br>`z: double` (Protobuf field number 3; repeated=False) |

### `ansys.api.fluent.v1.reduction_pb2`

| Message | Fields |
| --- | --- |
| `AreaAveRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `AreaAveResponse` | `value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |
| `AreaIntRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `AreaIntResponse` | `value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |
| `AreaRequest` | `locations: string` (Protobuf field number 1; repeated=True) |
| `AreaResponse` | `value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |
| `CentroidRequest` | `locations: string` (Protobuf field number 1; repeated=True) |
| `CentroidResponse` | `value: ansys.api.fluent.v1.primitives.Point` (Protobuf field number 1; repeated=False) |
| `CountIfRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `CountIfResponse` | `value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |
| `CountRequest` | `locations: string` (Protobuf field number 1; repeated=True) |
| `CountResponse` | `value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |
| `ForceRequest` | `locations: string` (Protobuf field number 1; repeated=True) |
| `ForceResponse` | `value: ansys.api.fluent.v1.primitives.Point` (Protobuf field number 1; repeated=False) |
| `MassAveRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `MassAveResponse` | `value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |
| `MassFlowAveAbsRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `MassFlowAveAbsResponse` | `value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |
| `MassFlowAveRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `MassFlowAveResponse` | `value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |
| `MassFlowIntRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `MassFlowIntResponse` | `value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |
| `MassIntRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `MassIntResponse` | `value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |
| `MaximumRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `MaximumResponse` | `value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |
| `MinimumRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `MinimumResponse` | `value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |
| `MomentRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `MomentResponse` | `value: ansys.api.fluent.v1.primitives.Point` (Protobuf field number 1; repeated=False) |
| `PressureForceRequest` | `locations: string` (Protobuf field number 1; repeated=True) |
| `PressureForceResponse` | `value: ansys.api.fluent.v1.primitives.Point` (Protobuf field number 1; repeated=False) |
| `SumIfRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`condition: string` (Protobuf field number 2; repeated=False)<br>`locations: string` (Protobuf field number 3; repeated=True)<br>`weight: string` (Protobuf field number 4; repeated=False) |
| `SumIfResponse` | `value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |
| `SumRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`weight: string` (Protobuf field number 3; repeated=False) |
| `SumResponse` | `value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |
| `ViscousForceRequest` | `locations: string` (Protobuf field number 1; repeated=True) |
| `ViscousForceResponse` | `value: ansys.api.fluent.v1.primitives.Point` (Protobuf field number 1; repeated=False) |
| `VolumeAveRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `VolumeAveResponse` | `value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |
| `VolumeIntRequest` | `expression: string` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |
| `VolumeIntResponse` | `value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |
| `VolumeRequest` | `locations: string` (Protobuf field number 1; repeated=True) |
| `VolumeResponse` | `value: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=False) |

### `ansys.api.fluent.v1.scheme_interpreter_pb2`

| Message | Fields |
| --- | --- |
| `ExecRequest` | `commands: string` (Protobuf field number 1; repeated=True)<br>`wait: bool` (Protobuf field number 2; repeated=False)<br>`silent: bool` (Protobuf field number 3; repeated=False) |
| `ExecResponse` | `output: string` (Protobuf field number 1; repeated=False) |
| `SchemeEvalRequest` | `input: ansys.api.fluent.v1.scheme_pointer.SchemePointer` (Protobuf field number 1; repeated=False) |
| `SchemeEvalResponse` | `output: ansys.api.fluent.v1.scheme_pointer.SchemePointer` (Protobuf field number 1; repeated=False) |
| `StringEvalRequest` | `input: string` (Protobuf field number 1; repeated=False) |
| `StringEvalResponse` | `output: string` (Protobuf field number 1; repeated=False) |

### `ansys.api.fluent.v1.scheme_pointer_pb2`

| Message | Fields |
| --- | --- |
| `Empty` | — |
| `SchemePointer` | `empty: ansys.api.fluent.v1.scheme_pointer.Empty` (Protobuf field number 1; repeated=False)<br>`sym: string` (Protobuf field number 2; repeated=False)<br>`pair: ansys.api.fluent.v1.scheme_pointer.SchemePointer.SchemePair` (Protobuf field number 3; repeated=False)<br>`list: ansys.api.fluent.v1.scheme_pointer.SchemePointer.SchemeList` (Protobuf field number 9; repeated=False)<br>`flonum: double` (Protobuf field number 4; repeated=False)<br>`fixednum: sint64` (Protobuf field number 5; repeated=False)<br>`c: string` (Protobuf field number 6; repeated=False)<br>`str: string` (Protobuf field number 7; repeated=False)<br>`b: bool` (Protobuf field number 8; repeated=False) |

### `ansys.api.fluent.v1.settings_pb2`

| Message | Fields |
| --- | --- |
| `AttrInfoMap` | `name: string` (Protobuf field number 1; repeated=False)<br>`value: ansys.api.fluent.v1.settings.GetAttrsResponse` (Protobuf field number 2; repeated=False) |
| `CreateObjectRequest` | `path_info: ansys.api.fluent.v1.settings.PathInfo` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False) |
| `CreateObjectResponse` | — |
| `DeleteObjectRequest` | `path_info: ansys.api.fluent.v1.settings.PathInfo` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False) |
| `DeleteObjectResponse` | — |
| `ExecuteCommandRequest` | `path_info: ansys.api.fluent.v1.settings.PathInfo` (Protobuf field number 1; repeated=False)<br>`command: string` (Protobuf field number 2; repeated=False)<br>`args: ansys.api.fluent.v1.settings.Value` (Protobuf field number 3; repeated=False) |
| `ExecuteCommandResponse` | `reply: ansys.api.fluent.v1.settings.Value` (Protobuf field number 1; repeated=False) |
| `ExecuteQueryRequest` | `path_info: ansys.api.fluent.v1.settings.PathInfo` (Protobuf field number 1; repeated=False)<br>`query: string` (Protobuf field number 2; repeated=False)<br>`args: ansys.api.fluent.v1.settings.Value` (Protobuf field number 3; repeated=False) |
| `ExecuteQueryResponse` | `reply: ansys.api.fluent.v1.settings.Value` (Protobuf field number 1; repeated=False) |
| `GetAttrsRequest` | `path_info: ansys.api.fluent.v1.settings.PathInfo` (Protobuf field number 1; repeated=False)<br>`attrs: string` (Protobuf field number 2; repeated=True)<br>`recursive: bool` (Protobuf field number 3; repeated=False) |
| `GetAttrsResponse` | `values: ansys.api.fluent.v1.settings.Value` (Protobuf field number 1; repeated=False)<br>`group_children: ansys.api.fluent.v1.settings.AttrInfoMap` (Protobuf field number 2; repeated=True) |
| `GetListSizeRequest` | `path_info: ansys.api.fluent.v1.settings.PathInfo` (Protobuf field number 1; repeated=False) |
| `GetListSizeResponse` | `size: int32` (Protobuf field number 1; repeated=False) |
| `GetObjectNamesRequest` | `path_info: ansys.api.fluent.v1.settings.PathInfo` (Protobuf field number 1; repeated=False) |
| `GetObjectNamesResponse` | `names: string` (Protobuf field number 1; repeated=True) |
| `GetSchemaRequest` | `root: string` (Protobuf field number 1; repeated=False)<br>`optional_attrs: string` (Protobuf field number 2; repeated=True) |
| `GetSchemaResponse` | `info: ansys.api.fluent.v1.settings.Schema` (Protobuf field number 1; repeated=False) |
| `GetStateRequest` | `path_info: ansys.api.fluent.v1.settings.PathInfo` (Protobuf field number 1; repeated=False) |
| `GetStateResponse` | `value: ansys.api.fluent.v1.settings.Value` (Protobuf field number 1; repeated=False) |
| `IsWildcardRequest` | `input: string` (Protobuf field number 1; repeated=False) |
| `IsWildcardResponse` | `is_wildcard: bool` (Protobuf field number 1; repeated=False) |
| `OptionalAttrs` | `allowed_values: string` (Protobuf field number 1; repeated=True)<br>`has_migration_adapter: bool` (Protobuf field number 2; repeated=False) |
| `PathInfo` | `root: string` (Protobuf field number 1; repeated=False)<br>`path: string` (Protobuf field number 2; repeated=False) |
| `RenameRequest` | `path_info: ansys.api.fluent.v1.settings.PathInfo` (Protobuf field number 1; repeated=False)<br>`old_name: string` (Protobuf field number 2; repeated=False)<br>`new_name: string` (Protobuf field number 3; repeated=False) |
| `RenameResponse` | — |
| `ResizeListObjectRequest` | `path_info: ansys.api.fluent.v1.settings.PathInfo` (Protobuf field number 1; repeated=False)<br>`size: int32` (Protobuf field number 2; repeated=False) |
| `ResizeListObjectResponse` | — |
| `Schema` | `type: string` (Protobuf field number 1; repeated=False)<br>`children: ansys.api.fluent.v1.settings.SchemaMap` (Protobuf field number 2; repeated=True)<br>`commands: ansys.api.fluent.v1.settings.SchemaMap` (Protobuf field number 3; repeated=True)<br>`arguments: ansys.api.fluent.v1.settings.SchemaMap` (Protobuf field number 4; repeated=True)<br>`object_type: ansys.api.fluent.v1.settings.Schema` (Protobuf field number 5; repeated=False)<br>`help: string` (Protobuf field number 6; repeated=False)<br>`has_allowed_values: bool` (Protobuf field number 7; repeated=False)<br>`include_child_named_objects: bool` (Protobuf field number 8; repeated=False)<br>`list_size: int32` (Protobuf field number 9; repeated=False)<br>`user_creatable: bool` (Protobuf field number 10; repeated=False)<br>`queries: ansys.api.fluent.v1.settings.SchemaMap` (Protobuf field number 11; repeated=True)<br>`return_type: string` (Protobuf field number 12; repeated=False)<br>`deprecated_version: string` (Protobuf field number 13; repeated=False)<br>`api_exposure_level: string` (Protobuf field number 14; repeated=False)<br>`child_aliases: ansys.api.fluent.v1.settings.StringPair` (Protobuf field number 15; repeated=True)<br>`command_aliases: ansys.api.fluent.v1.settings.StringPair` (Protobuf field number 16; repeated=True)<br>`query_aliases: ansys.api.fluent.v1.settings.StringPair` (Protobuf field number 17; repeated=True)<br>`arguments_aliases: ansys.api.fluent.v1.settings.StringPair` (Protobuf field number 18; repeated=True)<br>`file_purpose: string` (Protobuf field number 19; repeated=False)<br>`optional_attrs: ansys.api.fluent.v1.settings.OptionalAttrs` (Protobuf field number 20; repeated=False) |
| `SchemaMap` | `name: string` (Protobuf field number 1; repeated=False)<br>`value: ansys.api.fluent.v1.settings.Schema` (Protobuf field number 2; repeated=False) |
| `SetStateRequest` | `path_info: ansys.api.fluent.v1.settings.PathInfo` (Protobuf field number 1; repeated=False)<br>`value: ansys.api.fluent.v1.settings.Value` (Protobuf field number 2; repeated=False) |
| `SetStateResponse` | — |
| `StringPair` | `key: string` (Protobuf field number 1; repeated=False)<br>`value: string` (Protobuf field number 2; repeated=False) |
| `Value` | `boolean: bool` (Protobuf field number 2; repeated=False)<br>`integer: int64` (Protobuf field number 3; repeated=False)<br>`real: double` (Protobuf field number 4; repeated=False)<br>`string: string` (Protobuf field number 5; repeated=False)<br>`value_list: ansys.api.fluent.v1.settings.Value.ValueList` (Protobuf field number 10; repeated=False)<br>`value_map: ansys.api.fluent.v1.settings.Value.ValueMap` (Protobuf field number 11; repeated=False) |

### `ansys.api.fluent.v1.solution_variable_pb2`

| Message | Fields |
| --- | --- |
| `DomainInfo` | `name: string` (Protobuf field number 1; repeated=False)<br>`domain_id: uint32` (Protobuf field number 2; repeated=False) |
| `GetSolutionVariableDataRequest` | `chunk_size: uint32` (Protobuf field number 1; repeated=False)<br>`provide_bytes_stream: bool` (Protobuf field number 2; repeated=False)<br>`name: string` (Protobuf field number 3; repeated=False)<br>`domain_id: uint32` (Protobuf field number 4; repeated=False)<br>`zones: uint64` (Protobuf field number 5; repeated=True) |
| `GetSolutionVariableDataResponse` | `payload: ansys.api.fluent.v1.solution_variable.Payload` (Protobuf field number 1; repeated=False)<br>`payload_info: ansys.api.fluent.v1.solution_variable.Info` (Protobuf field number 2; repeated=False) |
| `GetSolutionVariableInfoRequest` | `domain_id: uint32` (Protobuf field number 1; repeated=False)<br>`zone_id: uint64` (Protobuf field number 2; repeated=False) |
| `GetSolutionVariableInfoResponse` | `svars_info: ansys.api.fluent.v1.solution_variable.SolutionVariableInfo` (Protobuf field number 1; repeated=True) |
| `GetZonesInfoRequest` | — |
| `GetZonesInfoResponse` | `domains_info: ansys.api.fluent.v1.solution_variable.DomainInfo` (Protobuf field number 1; repeated=True)<br>`zones_info: ansys.api.fluent.v1.solution_variable.ZoneInfo` (Protobuf field number 2; repeated=True) |
| `Info` | `field_type: ansys.api.fluent.v1.field_data.FieldType` (Protobuf field number 1; repeated=False)<br>`field_size: uint64` (Protobuf field number 2; repeated=False)<br>`zone: uint64` (Protobuf field number 3; repeated=False) |
| `PartitionInfo` | `count: uint64` (Protobuf field number 1; repeated=False)<br>`start_index: uint64` (Protobuf field number 2; repeated=False)<br>`end_index: uint64` (Protobuf field number 3; repeated=False) |
| `Payload` | `byte_payload: bytes` (Protobuf field number 1; repeated=False)<br>`double_payload: ansys.api.fluent.v1.field_data.DoublePayload` (Protobuf field number 2; repeated=False)<br>`float_payload: ansys.api.fluent.v1.field_data.FloatPayload` (Protobuf field number 3; repeated=False)<br>`long_payload: ansys.api.fluent.v1.field_data.LongPayload` (Protobuf field number 4; repeated=False)<br>`int_payload: ansys.api.fluent.v1.field_data.IntPayload` (Protobuf field number 5; repeated=False) |
| `SetSolutionVariableDataRequest` | `header: ansys.api.fluent.v1.solution_variable.SolutionVariableHeader` (Protobuf field number 1; repeated=False)<br>`payload: ansys.api.fluent.v1.solution_variable.Payload` (Protobuf field number 2; repeated=False)<br>`payload_info: ansys.api.fluent.v1.solution_variable.Info` (Protobuf field number 3; repeated=False) |
| `SetSolutionVariableDataResponse` | — |
| `SolutionVariableHeader` | `name: string` (Protobuf field number 1; repeated=False)<br>`domain_id: uint32` (Protobuf field number 2; repeated=False) |
| `SolutionVariableInfo` | `name: string` (Protobuf field number 1; repeated=False)<br>`dimension: uint32` (Protobuf field number 2; repeated=False)<br>`field_type: ansys.api.fluent.v1.field_data.FieldType` (Protobuf field number 3; repeated=False) |
| `ZoneInfo` | `name: string` (Protobuf field number 1; repeated=False)<br>`zone_id: uint64` (Protobuf field number 2; repeated=False)<br>`zone_type: string` (Protobuf field number 3; repeated=False)<br>`thread_type: ansys.api.fluent.v1.solution_variable.ThreadType` (Protobuf field number 4; repeated=False)<br>`partitions_info: ansys.api.fluent.v1.solution_variable.PartitionInfo` (Protobuf field number 5; repeated=True) |

### `ansys.api.fluent.v1.text_interface_pb2`

| Message | Fields |
| --- | --- |
| `CompositeGetRequest` | `getters: ansys.api.fluent.v1.text_interface.DataModelGetter` (Protobuf field number 1; repeated=True) |
| `CompositeGetResponse` | `response: google.protobuf.Value` (Protobuf field number 1; repeated=False) |
| `DataModelGetter` | `get_attribute_value_request: ansys.api.fluent.v1.text_interface.GetAttributeValueRequest` (Protobuf field number 1; repeated=False)<br>`get_state_request: ansys.api.fluent.v1.text_interface.GetStateRequest` (Protobuf field number 2; repeated=False) |
| `ExecuteCommandRequest` | `path: string` (Protobuf field number 1; repeated=False)<br>`command: string` (Protobuf field number 2; repeated=False)<br>`args: google.protobuf.Struct` (Protobuf field number 3; repeated=False) |
| `ExecuteCommandResponse` | `result: google.protobuf.Value` (Protobuf field number 1; repeated=False) |
| `ExecuteQueryRequest` | `path: string` (Protobuf field number 1; repeated=False) |
| `ExecuteQueryResponse` | `result: google.protobuf.Value` (Protobuf field number 1; repeated=False) |
| `GetAttributeValueRequest` | `path: string` (Protobuf field number 1; repeated=False)<br>`attribute: ansys.api.fluent.v1.text_interface.Attribute` (Protobuf field number 2; repeated=False)<br>`args: google.protobuf.Struct` (Protobuf field number 3; repeated=False) |
| `GetAttributeValueResponse` | `value: google.protobuf.Value` (Protobuf field number 1; repeated=False) |
| `GetSchemaRequest` | `path: string` (Protobuf field number 1; repeated=False) |
| `GetSchemaResponse` | `info: ansys.api.fluent.v1.text_interface.Schema` (Protobuf field number 1; repeated=False) |
| `GetStateRequest` | `path: string` (Protobuf field number 1; repeated=False) |
| `GetStateResponse` | `state: google.protobuf.Value` (Protobuf field number 1; repeated=False) |
| `NotifyChangesRequest` | `paths: google.protobuf.Value` (Protobuf field number 1; repeated=False)<br>`args: google.protobuf.Struct` (Protobuf field number 2; repeated=False) |
| `NotifyChangesResponse` | `changed_paths: google.protobuf.Value` (Protobuf field number 1; repeated=False)<br>`state_difference: google.protobuf.Value` (Protobuf field number 2; repeated=False) |
| `Schema` | `menus: ansys.api.fluent.v1.text_interface.Schema.MenusEntry` (Protobuf field number 1; repeated=True)<br>`commands: ansys.api.fluent.v1.text_interface.Schema.CommandsEntry` (Protobuf field number 2; repeated=True)<br>`help: string` (Protobuf field number 5; repeated=False) |
| `SetStateRequest` | `path: string` (Protobuf field number 1; repeated=False)<br>`state: google.protobuf.Value` (Protobuf field number 2; repeated=False) |
| `SetStateResponse` | `state: google.protobuf.Value` (Protobuf field number 1; repeated=False) |

### `ansys.api.fluent.v1.transcript_pb2`

| Message | Fields |
| --- | --- |
| `TranscriptRequest` | — |
| `TranscriptResponse` | `transcript: string` (Protobuf field number 1; repeated=False) |

### `ansys.api.fluent.v1.variant_pb2`

| Message | Fields |
| --- | --- |
| `BoolVector` | `items: bool` (Protobuf field number 1; repeated=True) |
| `DoubleVector` | `items: double` (Protobuf field number 1; repeated=True) |
| `Empty` | — |
| `Int64Vector` | `items: sint64` (Protobuf field number 1; repeated=True) |
| `StringVector` | `items: string` (Protobuf field number 1; repeated=True) |
| `Variant` | `empty_state: ansys.api.fluent.v1.variant.Empty` (Protobuf field number 1; repeated=False)<br>`bool_state: bool` (Protobuf field number 2; repeated=False)<br>`int64_state: sint64` (Protobuf field number 3; repeated=False)<br>`double_state: double` (Protobuf field number 5; repeated=False)<br>`string_state: string` (Protobuf field number 6; repeated=False)<br>`bool_vector_state: ansys.api.fluent.v1.variant.BoolVector` (Protobuf field number 7; repeated=False)<br>`int64_vector_state: ansys.api.fluent.v1.variant.Int64Vector` (Protobuf field number 8; repeated=False)<br>`double_vector_state: ansys.api.fluent.v1.variant.DoubleVector` (Protobuf field number 9; repeated=False)<br>`string_vector_state: ansys.api.fluent.v1.variant.StringVector` (Protobuf field number 10; repeated=False)<br>`variant_vector_state: ansys.api.fluent.v1.variant.VariantVector` (Protobuf field number 11; repeated=False)<br>`variant_map_state: ansys.api.fluent.v1.variant.VariantMap` (Protobuf field number 12; repeated=False) |
| `VariantMap` | `item: ansys.api.fluent.v1.variant.VariantMap.ItemEntry` (Protobuf field number 1; repeated=True) |
| `VariantVector` | `items: ansys.api.fluent.v1.variant.Variant` (Protobuf field number 1; repeated=True) |

## Snapshot counts

- RPC methods: 290
- Protocol messages: 813
- Message fields: 1697
