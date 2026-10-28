# geometry_protocol protocol dictionary

- APIKB source key: `geometry_protocol`
- Package: `ansys-api-geometry 0.4.92`
- Interface: geometry gRPC protocol schema
- Snapshot: [`geometry_protocol_api.json`](../../geometry_protocol_api.json)
- Snapshot SHA-256: `8e824d2063f6695761c7429dfa6025f0e49dfa3f24a04af55233b5db8ef778e0`

> This page describes the captured protobuf schema. It does not confirm product support, host compatibility, or runtime behavior.
> This snapshot records enum type names on fields. It does not list enum members.

## Services and RPC methods

### `ansys.api.geometry.v0.bodies_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Bodies` | `Get` | `(ansys.api.geometry.v0.bodies.GetRequest) -> ansys.api.geometry.v0.Body [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetMaster` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.Body [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetOriginal` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.Body [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetParent` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.Part [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetAll` | `(ansys.api.geometry.v0.bodies.GetAllRequest) -> ansys.api.geometry.v0.bodies.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetAssignedMaterial` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.Material [client_streaming=False, server_streaming=False]` |
| `Bodies` | `SetAssignedMaterial` | `(ansys.api.geometry.v0.bodies.SetAssignedMaterialRequest) -> ansys.api.geometry.v0.bodies.SetAssignedMaterialResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `RemoveAssignedMaterial` | `(ansys.api.geometry.v0.bodies.RemoveAssignedMaterialRequest) -> ansys.api.geometry.v0.bodies.RemoveAssignedMaterialResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `Translate` | `(ansys.api.geometry.v0.bodies.TranslateRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetFaces` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.bodies.GetFacesResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `CreateBodyFromFace` | `(ansys.api.geometry.v0.bodies.CreateBodyFromFaceRequest) -> ansys.api.geometry.v0.Body [client_streaming=False, server_streaming=False]` |
| `Bodies` | `CreateBodyFromLoftWithGuides` | `(ansys.api.geometry.v0.bodies.CreateBodyFromLoftWithGuidesRequest) -> ansys.api.geometry.v0.bodies.CreateBodyFromLoftWithGuidesResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `CreateExtrudedBodyFromFaceProfile` | `(ansys.api.geometry.v0.bodies.CreateExtrudedBodyFromFaceProfileRequest) -> ansys.api.geometry.v0.Body [client_streaming=False, server_streaming=False]` |
| `Bodies` | `CreateExtrudedBodyFromLoftProfiles` | `(ansys.api.geometry.v0.bodies.CreateExtrudedBodyFromLoftProfilesRequest) -> ansys.api.geometry.v0.Body [client_streaming=False, server_streaming=False]` |
| `Bodies` | `Delete` | `(ansys.api.dbu.v0.EntityIdentifier) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Bodies` | `CreatePlanarBody` | `(ansys.api.geometry.v0.bodies.CreatePlanarBodyRequest) -> ansys.api.geometry.v0.Body [client_streaming=False, server_streaming=False]` |
| `Bodies` | `CreateSphereBody` | `(ansys.api.geometry.v0.bodies.CreateSphereBodyRequest) -> ansys.api.geometry.v0.Body [client_streaming=False, server_streaming=False]` |
| `Bodies` | `CreateExtrudedBody` | `(ansys.api.geometry.v0.bodies.CreateExtrudedBodyRequest) -> ansys.api.geometry.v0.Body [client_streaming=False, server_streaming=False]` |
| `Bodies` | `CreateSweepingProfile` | `(ansys.api.geometry.v0.bodies.CreateSweepingProfileRequest) -> ansys.api.geometry.v0.Body [client_streaming=False, server_streaming=False]` |
| `Bodies` | `CreateSweepingChain` | `(ansys.api.geometry.v0.bodies.CreateSweepingChainRequest) -> ansys.api.geometry.v0.Body [client_streaming=False, server_streaming=False]` |
| `Bodies` | `SweepWithGuide` | `(ansys.api.geometry.v0.bodies.SweepWithGuideRequest) -> ansys.api.geometry.v0.bodies.SweepWithGuideResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetVolume` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.bodies.GetVolumeResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetTessellation` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.bodies.GetTessellationResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetTessellationStream` | `(ansys.api.geometry.v0.bodies.GetTessellationRequest) -> ansys.api.geometry.v0.bodies.GetTessellationResponse [client_streaming=False, server_streaming=True]` |
| `Bodies` | `GetEdges` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.bodies.GetEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetName` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.bodies.GetNameResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `SetName` | `(ansys.api.geometry.v0.bodies.SetNameRequest) -> ansys.api.geometry.v0.bodies.SetNameResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetFillStyle` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.bodies.GetFillStyleResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `SetFillStyle` | `(ansys.api.geometry.v0.bodies.SetFillStyleRequest) -> ansys.api.geometry.v0.bodies.SetFillStyleResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetColor` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.bodies.GetColorResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `SetColor` | `(ansys.api.geometry.v0.bodies.SetColorRequest) -> ansys.api.geometry.v0.bodies.SetColorResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `Copy` | `(ansys.api.geometry.v0.bodies.CopyRequest) -> ansys.api.geometry.v0.Body [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetUpdateState` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.UpdateState [client_streaming=False, server_streaming=False]` |
| `Bodies` | `Boolean` | `(ansys.api.geometry.v0.bodies.BooleanRequest) -> ansys.api.geometry.v0.bodies.BooleanResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetVertices` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.bodies.GetVerticesResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetBoundingBox` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.bodies.GetBoundingBoxResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetSurfaceBodyThickness` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.bodies.GetSurfaceBodyThicknessResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `IsEnclosureBody` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.bodies.IsEnclosureBodyResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `IsSuppressed` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.bodies.IsSuppressedResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `SetSuppressed` | `(ansys.api.geometry.v0.bodies.SetSuppressedRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Bodies` | `Rotate` | `(ansys.api.geometry.v0.bodies.RotateRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetCollision` | `(ansys.api.geometry.v0.bodies.GetCollisionRequest) -> ansys.api.geometry.v0.bodies.GetCollisionResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `Scale` | `(ansys.api.geometry.v0.bodies.ScaleRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Bodies` | `Map` | `(ansys.api.geometry.v0.bodies.MapRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Bodies` | `Mirror` | `(ansys.api.geometry.v0.bodies.MirrorRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Bodies` | `CreateSurfaceBody` | `(ansys.api.geometry.v0.bodies.CreateSurfaceBodyRequest) -> ansys.api.geometry.v0.Body [client_streaming=False, server_streaming=False]` |
| `Bodies` | `SeparatePieces` | `(ansys.api.geometry.v0.bodies.SeparatePiecesRequest) -> ansys.api.geometry.v0.bodies.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `CreateBlockBody` | `(ansys.api.geometry.v0.bodies.CreateBlockBodyRequest) -> ansys.api.geometry.v0.Body [client_streaming=False, server_streaming=False]` |
| `Bodies` | `CreateSurfaceBodyFromTrimmedCurves` | `(ansys.api.geometry.v0.bodies.CreateSurfaceBodyFromTrimmedCurvesRequest) -> ansys.api.geometry.v0.Body [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetClosestSeparation` | `(ansys.api.geometry.v0.bodies.GetClosestSeparationRequest) -> ansys.api.geometry.v0.Separation [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetTessellationWithOptions` | `(ansys.api.geometry.v0.bodies.GetTessellationRequest) -> ansys.api.geometry.v0.bodies.GetTessellationResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `ExportAndDownloadBody` | `(ansys.api.geometry.v0.bodies.ExportAndDownloadBodyRequest) -> ansys.api.geometry.v0.bodies.ExportAndDownloadBodyResponse [client_streaming=False, server_streaming=False]` |
| `Bodies` | `GetFullTessellation` | `(ansys.api.geometry.v0.bodies.GetFullTessellationRequest) -> ansys.api.geometry.v0.bodies.GetFullTessellationResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.geometry.v0.commands_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Commands` | `RenameMany` | `(ansys.api.geometry.v0.commands.RenameManyRequest) -> ansys.api.geometry.v0.commands.RenameManyResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `Rename` | `(ansys.api.geometry.v0.commands.RenameRequest) -> ansys.api.geometry.v0.commands.RenameResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `ProjectCurves` | `(ansys.api.geometry.v0.commands.ProjectCurvesRequest) -> ansys.api.geometry.v0.commands.ProjectCurvesResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `ImprintCurves` | `(ansys.api.geometry.v0.commands.ImprintCurvesRequest) -> ansys.api.geometry.v0.EntitiesCollection [client_streaming=False, server_streaming=False]` |
| `Commands` | `ImprintProjectedCurves` | `(ansys.api.geometry.v0.commands.ProjectCurvesRequest) -> ansys.api.geometry.v0.EntitiesCollection [client_streaming=False, server_streaming=False]` |
| `Commands` | `PowerSelectFacesByAreaRange` | `(ansys.api.geometry.v0.commands.PowerSelectFacesByAreaRangeRequest) -> ansys.api.geometry.v0.commands.PowerSelectFacesByAreaRangeResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreateBeamCircularProfile` | `(ansys.api.geometry.v0.commands.CreateBeamCircularProfileRequest) -> ansys.api.geometry.v0.commands.CreateBeamCircularProfileResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreateBeamSegment` | `(ansys.api.geometry.v0.commands.CreateBeamSegmentRequest) -> ansys.api.geometry.v0.commands.CreateBeamSegmentResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreateBeamSegments` | `(ansys.api.geometry.v0.commands.CreateBeamSegmentsRequest) -> ansys.api.geometry.v0.commands.CreateBeamSegmentsResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreateDescriptiveBeamSegment` | `(ansys.api.geometry.v0.commands.CreateBeamSegmentRequest) -> ansys.api.geometry.v0.commands.CreateBeamSegmentResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreateDescriptiveBeamSegments` | `(ansys.api.geometry.v0.commands.CreateBeamSegmentsRequest) -> ansys.api.geometry.v0.commands.CreateBeamSegmentsResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `FillFaces` | `(ansys.api.geometry.v0.commands.FillFacesRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreateDesignPoint` | `(ansys.api.geometry.v0.commands.CreateDesignPointRequest) -> ansys.api.geometry.v0.commands.CreateDesignPointResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreateDesignPoints` | `(ansys.api.geometry.v0.commands.CreateDesignPointsRequest) -> ansys.api.geometry.v0.commands.CreateDesignPointsResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreateCurvesFromProfile` | `(ansys.api.geometry.v0.commands.CreateCurvesFromProfileRequest) -> ansys.api.geometry.v0.commands.CreateCurvesFromProfileResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `AssignMidSurfaceThickness` | `(ansys.api.geometry.v0.commands.AssignMidSurfaceThicknessRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Commands` | `AssignMidSurfaceOffsetType` | `(ansys.api.geometry.v0.commands.AssignMidSurfaceOffsetTypeRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Commands` | `DownloadFile` | `(google.protobuf.Empty) -> ansys.api.geometry.v0.commands.DownloadFileResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `UploadFile` | `(ansys.api.geometry.v0.commands.UploadFileRequest) -> ansys.api.geometry.v0.commands.UploadFileResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `StreamFileUpload` | `(ansys.api.geometry.v0.commands.UploadFileRequest) -> ansys.api.geometry.v0.commands.UploadFileResponse [client_streaming=True, server_streaming=False]` |
| `Commands` | `CreateSphere` | `(ansys.api.geometry.v0.commands.CreateSphereRequest) -> ansys.api.geometry.v0.commands.CreateSphereResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreateTorus` | `(ansys.api.geometry.v0.commands.CreateTorusRequest) -> ansys.api.geometry.v0.commands.CreateTorusResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `DeleteBeam` | `(ansys.api.dbu.v0.EntityIdentifier) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Commands` | `DeleteBeamProfile` | `(ansys.api.dbu.v0.EntityIdentifier) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Commands` | `GetAssembly` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.commands.GetAssemblyResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `GetBeamProfileName` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.commands.GetBeamProfileNameResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `GetBeamProfileParts` | `(google.protobuf.Empty) -> ansys.api.geometry.v0.commands.GetBeamProfilePartsResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `GetBeamProperties` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.BeamProperties [client_streaming=False, server_streaming=False]` |
| `Commands` | `GetBeamCrossSectionInfo` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.BeamCrossSectionInfo [client_streaming=False, server_streaming=False]` |
| `Commands` | `GetAllSpotWelds` | `(google.protobuf.Empty) -> ansys.api.geometry.v0.commands.GetAllSpotWeldsResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `GetAllCADWelds` | `(google.protobuf.Empty) -> ansys.api.geometry.v0.commands.GetAllCADWeldsResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreateSketchLine` | `(ansys.api.geometry.v0.commands.CreateSketchLineRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Commands` | `IntersectCurves` | `(ansys.api.geometry.v0.commands.IntersectCurvesRequest) -> ansys.api.geometry.v0.commands.IntersectCurvesResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `RevolveCurves` | `(ansys.api.geometry.v0.commands.RevolveCurvesRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Commands` | `Chamfer` | `(ansys.api.geometry.v0.commands.ChamferRequest) -> ansys.api.geometry.v0.commands.ChamferResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `Fillet` | `(ansys.api.geometry.v0.commands.FilletRequest) -> ansys.api.geometry.v0.commands.ChamferResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `FaceOffset` | `(ansys.api.geometry.v0.commands.FaceOffsetRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `OffsetFacesSetRadius` | `(ansys.api.geometry.v0.commands.OffsetFacesSetRadiusRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `FullFillet` | `(ansys.api.geometry.v0.commands.FullFilletRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `ThickenFaces` | `(ansys.api.geometry.v0.commands.ThickenFacesRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `DraftFaces` | `(ansys.api.geometry.v0.commands.DraftFacesRequest) -> ansys.api.geometry.v0.commands.DraftFacesResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `ExtrudeEdges` | `(ansys.api.geometry.v0.commands.ExtrudeEdgesRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `ExtrudeEdgesUpTo` | `(ansys.api.geometry.v0.commands.ExtrudeEdgesUpToRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `ExtrudeFaces` | `(ansys.api.geometry.v0.commands.ExtrudeFacesRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `ExtrudeFacesUpTo` | `(ansys.api.geometry.v0.commands.ExtrudeFacesUpToRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `Scale` | `(ansys.api.geometry.v0.commands.ScaleRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `ScaleNonUniform` | `(ansys.api.geometry.v0.commands.ScaleNonUniformRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `OffsetEdges` | `(ansys.api.geometry.v0.commands.OffsetEdgesRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `MoveImprintEdges` | `(ansys.api.geometry.v0.commands.MoveImprintEdgesRequest) -> ansys.api.geometry.v0.commands.MoveImprintEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `OffsetFaceCurves` | `(ansys.api.geometry.v0.commands.OffsetFaceCurvesRequest) -> ansys.api.geometry.v0.commands.CreatedCurvesCommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `RevolveFaces` | `(ansys.api.geometry.v0.commands.RevolveFacesRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `RevolveFacesUpTo` | `(ansys.api.geometry.v0.commands.RevolveFacesUpToRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `RevolveFacesByHelix` | `(ansys.api.geometry.v0.commands.RevolveFacesByHelixRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `SweepFaces` | `(ansys.api.geometry.v0.commands.SweepFacesRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `SweepPoints` | `(ansys.api.geometry.v0.commands.SweepPointsRequest) -> ansys.api.geometry.v0.commands.CreatedCurvesCommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `RevolvePoints` | `(ansys.api.geometry.v0.commands.RevolvePointsRequest) -> ansys.api.geometry.v0.commands.CreatedCurvesCommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `RevolvePointsByHelix` | `(ansys.api.geometry.v0.commands.RevolvePointsByHelixRequest) -> ansys.api.geometry.v0.commands.CreatedCurvesCommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `CombineIntersectBodies` | `(ansys.api.geometry.v0.commands.CombineIntersectBodiesRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `CombineMergeBodies` | `(ansys.api.geometry.v0.commands.CombineMergeBodiesRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `MergeBodies` | `(ansys.api.geometry.v0.commands.MergeBodiesRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `ProjectToSolid` | `(ansys.api.geometry.v0.commands.ProjectToSolidRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `SplitBody` | `(ansys.api.geometry.v0.commands.SplitBodyRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreateLinearPattern` | `(ansys.api.geometry.v0.commands.CreateLinearPatternRequest) -> ansys.api.geometry.v0.commands.PatternCommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `ModifyLinearPattern` | `(ansys.api.geometry.v0.commands.ModifyLinearPatternRequest) -> ansys.api.geometry.v0.commands.PatternCommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreateCircularPattern` | `(ansys.api.geometry.v0.commands.CreateCircularPatternRequest) -> ansys.api.geometry.v0.commands.PatternCommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `ModifyCircularPattern` | `(ansys.api.geometry.v0.commands.ModifyCircularPatternRequest) -> ansys.api.geometry.v0.commands.PatternCommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreateFillPattern` | `(ansys.api.geometry.v0.commands.CreateFillPatternRequest) -> ansys.api.geometry.v0.commands.PatternCommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `UpdateFillPattern` | `(ansys.api.geometry.v0.commands.PatternRequest) -> ansys.api.geometry.v0.commands.PatternCommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `RemovePatterns` | `(ansys.api.geometry.v0.commands.PatternRequest) -> ansys.api.geometry.v0.commands.PatternCommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `RemovePatternMember` | `(ansys.api.geometry.v0.commands.PatternRequest) -> ansys.api.geometry.v0.commands.PatternCommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `SetPatternValue` | `(ansys.api.geometry.v0.commands.SetPatternValueRequest) -> ansys.api.geometry.v0.commands.PatternCommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `DetachFaces` | `(ansys.api.geometry.v0.commands.DetachFacesRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `PullCurvePoint` | `(ansys.api.geometry.v0.commands.PullCurvePointRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `RenameObject` | `(ansys.api.geometry.v0.commands.RenameObjectRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `ReplaceFace` | `(ansys.api.geometry.v0.commands.ReplaceFaceRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `Shell` | `(ansys.api.geometry.v0.commands.ShellRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `RemoveFaces` | `(ansys.api.geometry.v0.commands.RemoveFacesRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `MoveTranslate` | `(ansys.api.geometry.v0.commands.MoveTranslateRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `MoveRotate` | `(ansys.api.geometry.v0.commands.MoveRotateRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `Mirror` | `(ansys.api.geometry.v0.commands.MirrorRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `SplitFace` | `(ansys.api.geometry.v0.commands.SplitFaceRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `SplitEdge` | `(ansys.api.geometry.v0.commands.SplitEdgeRequest) -> ansys.api.geometry.v0.commands.CommandResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreatePlane` | `(ansys.api.geometry.v0.commands.CreatePlaneRequest) -> ansys.api.geometry.v0.commands.CreatePlaneResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `EvaluateNurbsCurve` | `(ansys.api.geometry.v0.commands.EvaluateNurbsCurveRequest) -> ansys.api.geometry.v0.CurveEvaluation [client_streaming=False, server_streaming=False]` |
| `Commands` | `ProjectPoint` | `(ansys.api.geometry.v0.commands.ProjectPointRequest) -> ansys.api.geometry.v0.CurveEvaluation [client_streaming=False, server_streaming=False]` |
| `Commands` | `GetRoundInfo` | `(ansys.api.geometry.v0.commands.RoundInfoRequest) -> ansys.api.geometry.v0.commands.RoundInfoResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `ImprintCurvesAndSync` | `(ansys.api.geometry.v0.commands.ImprintCurvesRequest) -> ansys.api.geometry.v0.commands.ImprintCurvesAndSyncResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `DeleteEntities` | `(ansys.api.geometry.v0.commands.DeleteEntitiesRequest) -> ansys.api.geometry.v0.commands.DeleteEntitiesResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `SetAutomaticTrackingState` | `(ansys.api.geometry.v0.commands.SetAutomaticTrackingStateRequest) -> ansys.api.geometry.v0.commands.SetAutomaticTrackingStateResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `GetTracker` | `(ansys.api.geometry.v0.commands.GetTrackerRequest) -> ansys.api.geometry.v0.commands.GetTrackerResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `GetTrackerChanges` | `(ansys.api.geometry.v0.commands.GetTrackerChangesRequest) -> ansys.api.geometry.v0.commands.GetTrackerChangesResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `DisposeTracker` | `(ansys.api.geometry.v0.commands.DisposeTrackerRequest) -> ansys.api.geometry.v0.commands.DisposeTrackerResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreateAlignCondition` | `(ansys.api.geometry.v0.commands.CreateAlignTangentOrientGearConditionRequest) -> ansys.api.geometry.v0.AlignCondition [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreateTangentCondition` | `(ansys.api.geometry.v0.commands.CreateAlignTangentOrientGearConditionRequest) -> ansys.api.geometry.v0.TangentCondition [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreateOrientCondition` | `(ansys.api.geometry.v0.commands.CreateAlignTangentOrientGearConditionRequest) -> ansys.api.geometry.v0.OrientCondition [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreateRigidCondition` | `(ansys.api.geometry.v0.commands.CreateRigidConditionRequest) -> ansys.api.geometry.v0.RigidCondition [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreateAnchorCondition` | `(ansys.api.geometry.v0.commands.CreateAnchorConditionRequest) -> ansys.api.geometry.v0.AnchorCondition [client_streaming=False, server_streaming=False]` |
| `Commands` | `CreateGearCondition` | `(ansys.api.geometry.v0.commands.CreateAlignTangentOrientGearConditionRequest) -> ansys.api.geometry.v0.GearCondition [client_streaming=False, server_streaming=False]` |
| `Commands` | `RayFire` | `(ansys.api.geometry.v0.commands.RayFireRequest) -> ansys.api.geometry.v0.commands.RayFireResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `RayFireOrdered` | `(ansys.api.geometry.v0.commands.RayFireOrderedRequest) -> ansys.api.geometry.v0.commands.RayFireOrderedResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `RayFireFaces` | `(ansys.api.geometry.v0.commands.RayFireFacesRequest) -> ansys.api.geometry.v0.commands.RayFireFacesResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `RayFireOrderedUV` | `(ansys.api.geometry.v0.commands.RayFireOrderedUVRequest) -> ansys.api.geometry.v0.commands.RayFireOrderedUVResponse [client_streaming=False, server_streaming=False]` |
| `Commands` | `IntersectCurveAndSurface` | `(ansys.api.geometry.v0.commands.IntersectCurveAndSurfaceRequest) -> ansys.api.geometry.v0.commands.IntersectCurveAndSurfaceResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.geometry.v0.components_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Components` | `Get` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.Component [client_streaming=False, server_streaming=False]` |
| `Components` | `GetAll` | `(ansys.api.geometry.v0.components.GetAllRequest) -> ansys.api.geometry.v0.components.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `Components` | `GetBodies` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.components.GetBodiesResponse [client_streaming=False, server_streaming=False]` |
| `Components` | `Delete` | `(ansys.api.dbu.v0.EntityIdentifier) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Components` | `Create` | `(ansys.api.geometry.v0.components.CreateRequest) -> ansys.api.geometry.v0.components.CreateResponse [client_streaming=False, server_streaming=False]` |
| `Components` | `SetSharedTopology` | `(ansys.api.geometry.v0.components.SetSharedTopologyRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Components` | `GetRootComponent` | `(google.protobuf.Empty) -> ansys.api.geometry.v0.components.GetRootComponentResponse [client_streaming=False, server_streaming=False]` |
| `Components` | `GetName` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.components.GetComponentNameResponse [client_streaming=False, server_streaming=False]` |
| `Components` | `SetName` | `(ansys.api.geometry.v0.SetObjectNameRequest) -> ansys.api.dbu.v0.RequestResult [client_streaming=False, server_streaming=False]` |
| `Components` | `GetUpdateState` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.UpdateState [client_streaming=False, server_streaming=False]` |
| `Components` | `SetPlacement` | `(ansys.api.geometry.v0.components.SetPlacementRequest) -> ansys.api.geometry.v0.components.SetPlacementResponse [client_streaming=False, server_streaming=False]` |
| `Components` | `GetBeamBodies` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.components.GetBeamBodiesResponse [client_streaming=False, server_streaming=False]` |
| `Components` | `GetPart` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.Part [client_streaming=False, server_streaming=False]` |
| `Components` | `MakeIndependent` | `(ansys.api.geometry.v0.components.MakeIndependentRequest) -> ansys.api.geometry.v0.components.MakeIndependentResponse [client_streaming=False, server_streaming=False]` |
| `Components` | `ImportGroups` | `(ansys.api.geometry.v0.components.ImportGroupsRequest) -> ansys.api.geometry.v0.components.ImportGroupsResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.geometry.v0.coordinatesystems_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `CoordinateSystems` | `Get` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.CoordinateSystem [client_streaming=False, server_streaming=False]` |
| `CoordinateSystems` | `GetAll` | `(ansys.api.geometry.v0.coordinatesystems.GetAllRequest) -> ansys.api.geometry.v0.coordinatesystems.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `CoordinateSystems` | `Create` | `(ansys.api.geometry.v0.coordinatesystems.CreateRequest) -> ansys.api.geometry.v0.CoordinateSystem [client_streaming=False, server_streaming=False]` |
| `CoordinateSystems` | `Delete` | `(ansys.api.geometry.v0.coordinatesystems.DeleteRequest) -> ansys.api.geometry.v0.coordinatesystems.DeleteResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.geometry.v0.curves_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Curves` | `Get` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.Curve [client_streaming=False, server_streaming=False]` |
| `Curves` | `GetAll` | `(ansys.api.geometry.v0.curves.GetAllRequest) -> ansys.api.geometry.v0.curves.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `Curves` | `Delete` | `(ansys.api.geometry.v0.curves.DeleteRequest) -> ansys.api.geometry.v0.curves.DeleteResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.geometry.v0.datumplanes_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `DatumPlanes` | `Get` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.DatumPlane [client_streaming=False, server_streaming=False]` |
| `DatumPlanes` | `GetAll` | `(google.protobuf.Empty) -> ansys.api.geometry.v0.datumplanes.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `DatumPlanes` | `IsDeleted` | `(ansys.api.geometry.v0.datumplanes.IsDeletedRequest) -> ansys.api.geometry.v0.datumplanes.IsDeletedResponse [client_streaming=False, server_streaming=False]` |
| `DatumPlanes` | `GetUpdateState` | `(ansys.api.geometry.v0.datumplanes.GetUpdateStateRequest) -> ansys.api.geometry.v0.datumplanes.UpdateStateResponse [client_streaming=False, server_streaming=False]` |
| `DatumPlanes` | `Delete` | `(ansys.api.geometry.v0.datumplanes.DeleteRequest) -> ansys.api.geometry.v0.datumplanes.DeleteResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.geometry.v0.edges_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Edges` | `Get` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.Edge [client_streaming=False, server_streaming=False]` |
| `Edges` | `GetAll` | `(ansys.api.geometry.v0.edges.GetAllRequest) -> ansys.api.geometry.v0.edges.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `Edges` | `GetFaces` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.edges.GetFacesResponse [client_streaming=False, server_streaming=False]` |
| `Edges` | `GetVertices` | `(ansys.api.geometry.v0.edges.GetVerticesRequest) -> ansys.api.geometry.v0.edges.GetVerticesResponse [client_streaming=False, server_streaming=False]` |
| `Edges` | `GetLength` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.edges.GetLengthResponse [client_streaming=False, server_streaming=False]` |
| `Edges` | `IsDeleted` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.edges.IsDeletedResponse [client_streaming=False, server_streaming=False]` |
| `Edges` | `GetUpdateState` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.UpdateState [client_streaming=False, server_streaming=False]` |
| `Edges` | `GetStartAndEndPoints` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.edges.GetStartAndEndPointsResponse [client_streaming=False, server_streaming=False]` |
| `Edges` | `GetInterval` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.edges.GetIntervalResponse [client_streaming=False, server_streaming=False]` |
| `Edges` | `GetCurve` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.CurveGeometry [client_streaming=False, server_streaming=False]` |
| `Edges` | `GetBoundingBox` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.Box [client_streaming=False, server_streaming=False]` |
| `Edges` | `Delete` | `(ansys.api.geometry.v0.edges.DeleteRequest) -> ansys.api.geometry.v0.edges.DeleteResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.geometry.v0.faces_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Faces` | `Get` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.Face [client_streaming=False, server_streaming=False]` |
| `Faces` | `GetAll` | `(ansys.api.geometry.v0.faces.GetAllRequest) -> ansys.api.geometry.v0.faces.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `Faces` | `GetNormal` | `(ansys.api.geometry.v0.faces.GetNormalRequest) -> ansys.api.geometry.v0.faces.GetNormalResponse [client_streaming=False, server_streaming=False]` |
| `Faces` | `GetArea` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.faces.GetAreaResponse [client_streaming=False, server_streaming=False]` |
| `Faces` | `Evaluate` | `(ansys.api.geometry.v0.faces.EvaluateRequest) -> ansys.api.geometry.v0.faces.EvaluateResponse [client_streaming=False, server_streaming=False]` |
| `Faces` | `GetEdges` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.faces.GetEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Faces` | `IsDeleted` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.faces.IsDeletedResponse [client_streaming=False, server_streaming=False]` |
| `Faces` | `GetExternalEdges` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.faces.GetExternalEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Faces` | `GetInternalEdges` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.faces.GetInternalEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Faces` | `GetLoops` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.faces.GetLoopsResponse [client_streaming=False, server_streaming=False]` |
| `Faces` | `GetUpdateState` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.UpdateState [client_streaming=False, server_streaming=False]` |
| `Faces` | `GetBoxUV` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.faces.GetBoxUVResponse [client_streaming=False, server_streaming=False]` |
| `Faces` | `GetSurface` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.Surface [client_streaming=False, server_streaming=False]` |
| `Faces` | `CreateIsoParamCurves` | `(ansys.api.geometry.v0.faces.CreateIsoParamCurvesRequest) -> ansys.api.geometry.v0.faces.CreateIsoParamCurvesResponse [client_streaming=False, server_streaming=False]` |
| `Faces` | `GetBoundingBox` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.Box [client_streaming=False, server_streaming=False]` |
| `Faces` | `GetClosestSeparation` | `(ansys.api.geometry.v0.faces.GetClosestSeparationRequest) -> ansys.api.geometry.v0.Separation [client_streaming=False, server_streaming=False]` |
| `Faces` | `GetColor` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.faces.GetColorResponse [client_streaming=False, server_streaming=False]` |
| `Faces` | `SetColor` | `(ansys.api.geometry.v0.faces.SetColorRequest) -> ansys.api.geometry.v0.faces.SetColorResponse [client_streaming=False, server_streaming=False]` |
| `Faces` | `GetVertices` | `(ansys.api.geometry.v0.faces.GetVerticesRequest) -> ansys.api.geometry.v0.faces.GetVerticesResponse [client_streaming=False, server_streaming=False]` |
| `Faces` | `OffsetFaces` | `(ansys.api.geometry.v0.faces.OffsetFacesRequest) -> ansys.api.geometry.v0.faces.OffsetFacesResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.geometry.v0.facettools_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `FacetTools` | `ShrinkWrapBody` | `(ansys.api.geometry.v0.facettools.ShrinkWrapBodyRequest) -> ansys.api.geometry.v0.facettools.ShrinkWrapBodyResponse [client_streaming=False, server_streaming=False]` |
| `FacetTools` | `ShrinkWrapMesh` | `(ansys.api.geometry.v0.facettools.ShrinkWrapMeshRequest) -> ansys.api.geometry.v0.facettools.ShrinkWrapMeshResponse [client_streaming=False, server_streaming=False]` |
| `FacetTools` | `FacetAutoFix` | `(ansys.api.geometry.v0.facettools.FacetAutoFixRequest) -> ansys.api.geometry.v0.facettools.FacetAutoFixResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.geometry.v0.materials_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Materials` | `GetAllNames` | `(google.protobuf.Empty) -> ansys.api.geometry.v0.materials.GetAllNamesResponse [client_streaming=False, server_streaming=False]` |
| `Materials` | `AddToDocument` | `(ansys.api.geometry.v0.materials.AddToDocumentRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Materials` | `RemoveFromDocument` | `(ansys.api.geometry.v0.materials.RemoveFromDocumentRequest) -> ansys.api.geometry.v0.materials.RemoveFromDocumentResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.geometry.v0.measuretools_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `MeasureTools` | `MinDistanceBetweenObjects` | `(ansys.api.geometry.v0.measuretools.MinDistanceBetweenObjectsRequest) -> ansys.api.geometry.v0.measuretools.MinDistanceBetweenObjectsResponse [client_streaming=False, server_streaming=False]` |
| `MeasureTools` | `MinDistanceBetweenSelectionObjects` | `(ansys.api.geometry.v0.measuretools.MinDistanceBetweenObjectsRequest) -> ansys.api.geometry.v0.measuretools.MinDistanceBetweenObjectsResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.geometry.v0.meshes_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Meshes` | `Get` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.Mesh [client_streaming=False, server_streaming=False]` |
| `Meshes` | `GetAll` | `(ansys.api.geometry.v0.meshes.GetAllRequest) -> ansys.api.geometry.v0.meshes.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.geometry.v0.namedselections_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `NamedSelections` | `Get` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.NamedSelection [client_streaming=False, server_streaming=False]` |
| `NamedSelections` | `Create` | `(ansys.api.geometry.v0.namedselections.CreateRequest) -> ansys.api.geometry.v0.NamedSelection [client_streaming=False, server_streaming=False]` |
| `NamedSelections` | `GetAll` | `(google.protobuf.Empty) -> ansys.api.geometry.v0.namedselections.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `NamedSelections` | `Delete` | `(ansys.api.dbu.v0.EntityIdentifier) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `NamedSelections` | `DeleteByName` | `(ansys.api.geometry.v0.namedselections.DeleteByNameRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `NamedSelections` | `SetName` | `(ansys.api.geometry.v0.namedselections.SetNameRequest) -> ansys.api.geometry.v0.namedselections.SetNameResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.geometry.v0.parts_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Parts` | `Get` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.geometry.v0.Part [client_streaming=False, server_streaming=False]` |
| `Parts` | `GetAll` | `(ansys.api.geometry.v0.parts.GetAllRequest) -> ansys.api.geometry.v0.parts.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `Parts` | `GetBeams` | `(ansys.api.geometry.v0.parts.GetBeamsRequest) -> ansys.api.geometry.v0.parts.GetBeamsResponse [client_streaming=False, server_streaming=False]` |
| `Parts` | `ExportLargeSize` | `(ansys.api.geometry.v0.parts.ExportRequest) -> ansys.api.dbu.v0.StreamPackage [client_streaming=False, server_streaming=True]` |
| `Parts` | `Export` | `(ansys.api.geometry.v0.parts.ExportRequest) -> ansys.api.geometry.v0.parts.ExportResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.geometry.v0.preparetools_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `PrepareTools` | `FixInterference` | `(ansys.api.geometry.v0.preparetools.FixInterferenceRequest) -> ansys.api.geometry.v0.preparetools.FixInterferenceResponse [client_streaming=False, server_streaming=False]` |
| `PrepareTools` | `FixShortEdges` | `(ansys.api.geometry.v0.preparetools.FixShortEdgesRequest) -> ansys.api.geometry.v0.preparetools.FixShortEdgesResponse [client_streaming=False, server_streaming=False]` |
| `PrepareTools` | `ShareTopology` | `(ansys.api.geometry.v0.preparetools.ShareTopologyRequest) -> ansys.api.geometry.v0.preparetools.ShareTopologyResponse [client_streaming=False, server_streaming=False]` |
| `PrepareTools` | `UnshareTopology` | `(ansys.api.geometry.v0.preparetools.UnshareTopologyRequest) -> ansys.api.geometry.v0.preparetools.UnshareTopologyResponse [client_streaming=False, server_streaming=False]` |
| `PrepareTools` | `RemoveRounds` | `(ansys.api.geometry.v0.preparetools.RemoveRoundsRequest) -> ansys.api.geometry.v0.preparetools.RemoveRoundsResponse [client_streaming=False, server_streaming=False]` |
| `PrepareTools` | `RemoveFaces` | `(ansys.api.geometry.v0.preparetools.RemoveFacesRequest) -> ansys.api.geometry.v0.preparetools.RemoveFacesResponse [client_streaming=False, server_streaming=False]` |
| `PrepareTools` | `ExtractVolumeFromFaces` | `(ansys.api.geometry.v0.preparetools.ExtractVolumeFromFacesRequest) -> ansys.api.geometry.v0.preparetools.VolumeExtractionResponse [client_streaming=False, server_streaming=False]` |
| `PrepareTools` | `ExtractVolumeFromEdgeLoops` | `(ansys.api.geometry.v0.preparetools.ExtractVolumeFromEdgeLoopsRequest) -> ansys.api.geometry.v0.preparetools.VolumeExtractionResponse [client_streaming=False, server_streaming=False]` |
| `PrepareTools` | `EnhancedShareTopology` | `(ansys.api.geometry.v0.preparetools.ShareTopologyRequest) -> ansys.api.geometry.v0.EnhancedRepairToolMessage [client_streaming=False, server_streaming=False]` |
| `PrepareTools` | `CreateEnclosureBox` | `(ansys.api.geometry.v0.preparetools.CreateEnclosureBoxRequest) -> ansys.api.geometry.v0.preparetools.CreateEnclosureResponse [client_streaming=False, server_streaming=False]` |
| `PrepareTools` | `CreateEnclosureSphere` | `(ansys.api.geometry.v0.preparetools.CreateEnclosureSphereRequest) -> ansys.api.geometry.v0.preparetools.CreateEnclosureResponse [client_streaming=False, server_streaming=False]` |
| `PrepareTools` | `CreateEnclosureCylinder` | `(ansys.api.geometry.v0.preparetools.CreateEnclosureCylinderRequest) -> ansys.api.geometry.v0.preparetools.CreateEnclosureResponse [client_streaming=False, server_streaming=False]` |
| `PrepareTools` | `FindLogos` | `(ansys.api.geometry.v0.preparetools.FindLogosRequest) -> ansys.api.geometry.v0.preparetools.FindLogosResponse [client_streaming=False, server_streaming=False]` |
| `PrepareTools` | `FindAndRemoveLogos` | `(ansys.api.geometry.v0.preparetools.FindLogosRequest) -> ansys.api.geometry.v0.preparetools.RemoveLogoResponse [client_streaming=False, server_streaming=False]` |
| `PrepareTools` | `RemoveLogo` | `(ansys.api.geometry.v0.preparetools.RemoveLogoRequest) -> ansys.api.geometry.v0.preparetools.RemoveLogoResponse [client_streaming=False, server_streaming=False]` |
| `PrepareTools` | `DetectHelixes` | `(ansys.api.geometry.v0.preparetools.DetectHelixesRequest) -> ansys.api.geometry.v0.preparetools.DetectHelixesResponse [client_streaming=False, server_streaming=False]` |
| `PrepareTools` | `DetectSweepableBodies` | `(ansys.api.geometry.v0.preparetools.DetectSweepableBodiesRequest) -> ansys.api.geometry.v0.preparetools.DetectSweepableBodiesResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.geometry.v0.repairtools_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `RepairTools` | `FindInterference` | `(ansys.api.geometry.v0.repairtools.FindInterferenceRequest) -> ansys.api.geometry.v0.repairtools.FindInterferenceResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FixInterference` | `(ansys.api.geometry.v0.repairtools.FixInterferenceRequest) -> ansys.api.geometry.v0.repairtools.FixInterferenceResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FindSplitEdges` | `(ansys.api.geometry.v0.repairtools.FindSplitEdgesRequest) -> ansys.api.geometry.v0.repairtools.FindSplitEdgesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FixSplitEdges` | `(ansys.api.geometry.v0.repairtools.FixSplitEdgesRequest) -> ansys.api.geometry.v0.repairtools.FixSplitEdgesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FindExtraEdges` | `(ansys.api.geometry.v0.repairtools.FindExtraEdgesRequest) -> ansys.api.geometry.v0.repairtools.FindExtraEdgesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FixExtraEdges` | `(ansys.api.geometry.v0.repairtools.FixExtraEdgesRequest) -> ansys.api.geometry.v0.repairtools.FixExtraEdgesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FindInexactEdges` | `(ansys.api.geometry.v0.repairtools.FindInexactEdgesRequest) -> ansys.api.geometry.v0.repairtools.FindInexactEdgesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FixInexactEdges` | `(ansys.api.geometry.v0.repairtools.FixInexactEdgesRequest) -> ansys.api.geometry.v0.repairtools.FixInexactEdgesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FindShortEdges` | `(ansys.api.geometry.v0.repairtools.FindShortEdgesRequest) -> ansys.api.geometry.v0.repairtools.FindShortEdgesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FixShortEdges` | `(ansys.api.geometry.v0.repairtools.FixShortEdgesRequest) -> ansys.api.geometry.v0.repairtools.FixShortEdgesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FindStitchFaces` | `(ansys.api.geometry.v0.repairtools.FindStitchFacesRequest) -> ansys.api.geometry.v0.repairtools.FindStitchFacesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FixStitchFaces` | `(ansys.api.geometry.v0.repairtools.FixStitchFacesRequest) -> ansys.api.geometry.v0.repairtools.FixStitchFacesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FindMissingFaces` | `(ansys.api.geometry.v0.repairtools.FindMissingFacesRequest) -> ansys.api.geometry.v0.repairtools.FindMissingFacesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FixMissingFaces` | `(ansys.api.geometry.v0.repairtools.FixMissingFacesRequest) -> ansys.api.geometry.v0.repairtools.FixMissingFacesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FindDuplicateFaces` | `(ansys.api.geometry.v0.repairtools.FindDuplicateFacesRequest) -> ansys.api.geometry.v0.repairtools.FindDuplicateFacesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FixDuplicateFaces` | `(ansys.api.geometry.v0.repairtools.FixDuplicateFacesRequest) -> ansys.api.geometry.v0.repairtools.FixDuplicateFacesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FindSmallFaces` | `(ansys.api.geometry.v0.repairtools.FindSmallFacesRequest) -> ansys.api.geometry.v0.repairtools.FindSmallFacesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FixSmallFaces` | `(ansys.api.geometry.v0.repairtools.FixSmallFacesRequest) -> ansys.api.geometry.v0.repairtools.FixSmallFacesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FindGaps` | `(ansys.api.geometry.v0.repairtools.FindGapsRequest) -> ansys.api.geometry.v0.repairtools.FindGapsResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FixGaps` | `(ansys.api.geometry.v0.repairtools.FixGapsRequest) -> ansys.api.geometry.v0.repairtools.FixGapsResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FindSmallCurves` | `(ansys.api.geometry.v0.repairtools.FindSmallCurvesRequest) -> ansys.api.geometry.v0.repairtools.FindSmallCurvesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FixSmallCurves` | `(ansys.api.geometry.v0.repairtools.FixSmallCurvesRequest) -> ansys.api.geometry.v0.repairtools.FixSmallCurvesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FindCurveGaps` | `(ansys.api.geometry.v0.repairtools.FindCurveGapsRequest) -> ansys.api.geometry.v0.repairtools.FindCurveGapsResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FixCurveGaps` | `(ansys.api.geometry.v0.repairtools.FixCurveGapsRequest) -> ansys.api.geometry.v0.repairtools.FixCurveGapsResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FindDuplicateCurves` | `(google.protobuf.Empty) -> ansys.api.geometry.v0.repairtools.FindDuplicateCurvesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FixDuplicateCurves` | `(ansys.api.geometry.v0.repairtools.FixDuplicateCurvesRequest) -> ansys.api.geometry.v0.repairtools.FixDuplicateCurvesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FindAdjustMergeFaces` | `(ansys.api.geometry.v0.repairtools.FindAdjustMergeFacesRequest) -> ansys.api.geometry.v0.repairtools.FindAdjustMergeFacesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `AdjustMergeFaces` | `(ansys.api.geometry.v0.repairtools.AdjustMergeFacesRequest) -> ansys.api.geometry.v0.repairtools.AdjustMergeFacesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FindAdjustSimplify` | `(ansys.api.geometry.v0.repairtools.FindAdjustSimplifyRequest) -> ansys.api.geometry.v0.repairtools.FindAdjustSimplifyResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FixAdjustSimplify` | `(ansys.api.geometry.v0.repairtools.FixAdjustSimplifyRequest) -> ansys.api.geometry.v0.repairtools.FixAdjustSimplifyResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FitCurves` | `(ansys.api.geometry.v0.repairtools.FitCurvesRequest) -> ansys.api.geometry.v0.repairtools.FitCurvesResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `InspectGeometry` | `(ansys.api.geometry.v0.repairtools.InspectGeometryRequest) -> ansys.api.geometry.v0.repairtools.InspectGeometryResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `RepairGeometry` | `(ansys.api.geometry.v0.repairtools.RepairGeometryRequest) -> ansys.api.geometry.v0.repairtools.RepairGeometryResponse [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FindAndFixExtraEdges` | `(ansys.api.geometry.v0.repairtools.FindExtraEdgesRequest) -> ansys.api.geometry.v0.EnhancedRepairToolMessage [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FindAndFixSplitEdges` | `(ansys.api.geometry.v0.repairtools.FindSplitEdgesRequest) -> ansys.api.geometry.v0.EnhancedRepairToolMessage [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FindAndFixShortEdges` | `(ansys.api.geometry.v0.repairtools.FindShortEdgesRequest) -> ansys.api.geometry.v0.EnhancedRepairToolMessage [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FindAndSimplify` | `(ansys.api.geometry.v0.repairtools.FindAdjustSimplifyRequest) -> ansys.api.geometry.v0.EnhancedRepairToolMessage [client_streaming=False, server_streaming=False]` |
| `RepairTools` | `FindAndFixStitchFaces` | `(ansys.api.geometry.v0.repairtools.FindStitchFacesRequest) -> ansys.api.geometry.v0.EnhancedRepairToolMessage [client_streaming=False, server_streaming=False]` |

### `ansys.api.geometry.v0.unsupported_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Unsupported` | `SetSoundEnabled` | `(ansys.api.geometry.v0.unsupported.SoundEnabledRequest) -> ansys.api.dbu.v0.RequestResult [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `GetImportIdMap` | `(ansys.api.geometry.v0.unsupported.ImportIdRequest) -> ansys.api.geometry.v0.unsupported.ImportIdResponse [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `SetExportId` | `(ansys.api.geometry.v0.unsupported.ExportIdRequest) -> ansys.api.dbu.v0.RequestResult [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `SetExportIds` | `(ansys.api.geometry.v0.unsupported.SetExportIdsRequest) -> ansys.api.dbu.v0.RequestResult [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `GetFacetedBodies` | `(ansys.api.geometry.v0.unsupported.GetFacetedBodiesRequest) -> ansys.api.geometry.v0.unsupported.GetFacetedBodiesResponse [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `GetFacetedBodiesStream` | `(ansys.api.geometry.v0.unsupported.GetFacetedBodiesRequest) -> ansys.api.geometry.v0.unsupported.GetFacetedBodiesResponse [client_streaming=False, server_streaming=True]` |
| `Unsupported` | `CreateFacetedBodies` | `(ansys.api.geometry.v0.unsupported.CreateFacetedBodiesRequest) -> ansys.api.geometry.v0.unsupported.CreateFacetedBodiesResponse [client_streaming=False, server_streaming=False]` |

## Messages and fields

### `ansys.api.geometry.v0.bodies_pb2`

| Message | Fields |
| --- | --- |
| `BooleanRequest` | `body1: string` (Protobuf field number 1; repeated=False)<br>`body2: string` (Protobuf field number 2; repeated=False)<br>`method: string` (Protobuf field number 3; repeated=False)<br>`tool_bodies: string` (Protobuf field number 4; repeated=True)<br>`keep_other: bool` (Protobuf field number 5; repeated=False) |
| `BooleanResponse` | `empty_result: int32` (Protobuf field number 1; repeated=False)<br>`response: ansys.api.geometry.v0.TrackerCommandResponse` (Protobuf field number 2; repeated=False) |
| `CopyRequest` | `id: string` (Protobuf field number 1; repeated=False)<br>`parent: string` (Protobuf field number 2; repeated=False)<br>`name: string` (Protobuf field number 3; repeated=False) |
| `CreateBlockBodyRequest` | `start_point: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=False)<br>`end_point: ansys.api.geometry.v0.Point` (Protobuf field number 2; repeated=False) |
| `CreateBodyFromFaceRequest` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent: string` (Protobuf field number 2; repeated=False)<br>`face: string` (Protobuf field number 3; repeated=False) |
| `CreateBodyFromLoftWithGuidesRequest` | `request_data: ansys.api.geometry.v0.bodies.CreateBodyFromLoftWithGuidesRequestData` (Protobuf field number 1; repeated=True) |
| `CreateBodyFromLoftWithGuidesRequestData` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`profiles: ansys.api.geometry.v0.TrimmedCurveList` (Protobuf field number 3; repeated=True)<br>`guides: ansys.api.geometry.v0.TrimmedCurveList` (Protobuf field number 6; repeated=False) |
| `CreateBodyFromLoftWithGuidesResponse` | `created_bodies: ansys.api.geometry.v0.Body` (Protobuf field number 1; repeated=True) |
| `CreateExtrudedBodyFromFaceProfileRequest` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent: string` (Protobuf field number 2; repeated=False)<br>`face: string` (Protobuf field number 3; repeated=False)<br>`distance: double` (Protobuf field number 4; repeated=False) |
| `CreateExtrudedBodyFromLoftProfilesRequest` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent: string` (Protobuf field number 2; repeated=False)<br>`profiles: ansys.api.geometry.v0.TrimmedCurveList` (Protobuf field number 3; repeated=True)<br>`periodic: bool` (Protobuf field number 4; repeated=False)<br>`ruled: bool` (Protobuf field number 5; repeated=False) |
| `CreateExtrudedBodyRequest` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent: string` (Protobuf field number 2; repeated=False)<br>`plane: ansys.api.geometry.v0.Plane` (Protobuf field number 3; repeated=False)<br>`geometries: ansys.api.geometry.v0.Geometries` (Protobuf field number 4; repeated=False)<br>`distance: double` (Protobuf field number 5; repeated=False) |
| `CreatePlanarBodyRequest` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent: string` (Protobuf field number 2; repeated=False)<br>`plane: ansys.api.geometry.v0.Plane` (Protobuf field number 3; repeated=False)<br>`geometries: ansys.api.geometry.v0.Geometries` (Protobuf field number 4; repeated=False) |
| `CreateSphereBodyRequest` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent: string` (Protobuf field number 2; repeated=False)<br>`center: ansys.api.geometry.v0.Point` (Protobuf field number 3; repeated=False)<br>`radius: double` (Protobuf field number 4; repeated=False) |
| `CreateSurfaceBodyFromTrimmedCurvesRequest` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent: string` (Protobuf field number 2; repeated=False)<br>`trimmed_curves: ansys.api.geometry.v0.TrimmedCurve` (Protobuf field number 3; repeated=True) |
| `CreateSurfaceBodyRequest` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent: string` (Protobuf field number 2; repeated=False)<br>`trimmed_surface: ansys.api.geometry.v0.TrimmedSurface` (Protobuf field number 3; repeated=False) |
| `CreateSweepingChainRequest` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent: string` (Protobuf field number 2; repeated=False)<br>`chain: ansys.api.geometry.v0.TrimmedCurve` (Protobuf field number 3; repeated=True)<br>`path: ansys.api.geometry.v0.TrimmedCurve` (Protobuf field number 4; repeated=True) |
| `CreateSweepingProfileRequest` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent: string` (Protobuf field number 2; repeated=False)<br>`plane: ansys.api.geometry.v0.Plane` (Protobuf field number 3; repeated=False)<br>`geometries: ansys.api.geometry.v0.Geometries` (Protobuf field number 4; repeated=False)<br>`path: ansys.api.geometry.v0.TrimmedCurve` (Protobuf field number 5; repeated=True) |
| `ExportAndDownloadBodyRequest` | `id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`format: ansys.api.dbu.v0.BodyExportFormat` (Protobuf field number 2; repeated=False) |
| `ExportAndDownloadBodyResponse` | `data: bytes` (Protobuf field number 1; repeated=False) |
| `GetAllRequest` | `parent: string` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `bodies: ansys.api.geometry.v0.Body` (Protobuf field number 1; repeated=True) |
| `GetBoundingBoxResponse` | `box: ansys.api.geometry.v0.Box` (Protobuf field number 1; repeated=False) |
| `GetClosestSeparationRequest` | `body_1: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`body_2: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=False) |
| `GetCollisionRequest` | `body_1_id: string` (Protobuf field number 1; repeated=False)<br>`body_2_id: string` (Protobuf field number 2; repeated=False) |
| `GetCollisionResponse` | `collision: ansys.api.geometry.v0.CollisionType` (Protobuf field number 1; repeated=False) |
| `GetColorResponse` | `color: string` (Protobuf field number 1; repeated=False) |
| `GetEdgesResponse` | `edges: ansys.api.geometry.v0.Edge` (Protobuf field number 1; repeated=True) |
| `GetFacesResponse` | `faces: ansys.api.geometry.v0.Face` (Protobuf field number 1; repeated=True) |
| `GetFillStyleResponse` | `name: string` (Protobuf field number 1; repeated=False) |
| `GetFullTessellationRequest` | `request_data: ansys.api.geometry.v0.bodies.GetFullTessellationRequestData` (Protobuf field number 1; repeated=True) |
| `GetFullTessellationRequestData` | `id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`options: ansys.api.geometry.v0.TessellationOptions` (Protobuf field number 2; repeated=False)<br>`include_faces: bool` (Protobuf field number 3; repeated=False)<br>`include_edges: bool` (Protobuf field number 4; repeated=False) |
| `GetFullTessellationResponse` | `response_data: ansys.api.geometry.v0.bodies.GetFullTessellationResponseData` (Protobuf field number 1; repeated=True) |
| `GetFullTessellationResponseData` | `id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`edge_tessellation: ansys.api.geometry.v0.bodies.GetFullTessellationResponseData.EdgeTessellationEntry` (Protobuf field number 2; repeated=True)<br>`face_tessellation: ansys.api.geometry.v0.bodies.GetFullTessellationResponseData.FaceTessellationEntry` (Protobuf field number 3; repeated=True) |
| `GetNameResponse` | `name: string` (Protobuf field number 1; repeated=False) |
| `GetRequest` | `id: string` (Protobuf field number 1; repeated=False)<br>`body_type: ansys.api.geometry.v0.bodies.GetType` (Protobuf field number 2; repeated=False) |
| `GetSurfaceBodyThicknessResponse` | `result: double` (Protobuf field number 1; repeated=False) |
| `GetTessellationRequest` | `id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`options: ansys.api.geometry.v0.TessellationOptions` (Protobuf field number 2; repeated=False)<br>`include_faces: bool` (Protobuf field number 3; repeated=False)<br>`include_edges: bool` (Protobuf field number 4; repeated=False) |
| `GetTessellationResponse` | `face_tessellation: ansys.api.geometry.v0.bodies.GetTessellationResponse.FaceTessellationEntry` (Protobuf field number 1; repeated=True)<br>`edge_tessellation: ansys.api.geometry.v0.bodies.GetTessellationResponse.EdgeTessellationEntry` (Protobuf field number 2; repeated=True) |
| `GetVerticesResponse` | `vertices: ansys.api.geometry.v0.Vertex` (Protobuf field number 1; repeated=True) |
| `GetVolumeResponse` | `volume: double` (Protobuf field number 1; repeated=False) |
| `IsEnclosureBodyResponse` | `result: bool` (Protobuf field number 1; repeated=False) |
| `IsSuppressedResponse` | `result: bool` (Protobuf field number 1; repeated=False) |
| `MapRequest` | `id: string` (Protobuf field number 1; repeated=False)<br>`frame: ansys.api.geometry.v0.Frame` (Protobuf field number 2; repeated=False) |
| `MirrorRequest` | `id: string` (Protobuf field number 1; repeated=False)<br>`plane: ansys.api.geometry.v0.Plane` (Protobuf field number 2; repeated=False) |
| `RemoveAssignedMaterialRequest` | `ids: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `RemoveAssignedMaterialResponse` | `successfully_removed: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `RotateRequest` | `id: string` (Protobuf field number 1; repeated=False)<br>`axis_origin: ansys.api.geometry.v0.Point` (Protobuf field number 2; repeated=False)<br>`axis_direction: ansys.api.geometry.v0.Direction` (Protobuf field number 3; repeated=False)<br>`angle: double` (Protobuf field number 4; repeated=False) |
| `ScaleRequest` | `id: string` (Protobuf field number 1; repeated=False)<br>`scale: double` (Protobuf field number 2; repeated=False) |
| `SeparatePiecesRequest` | `body: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `SetAssignedMaterialRequest` | `id: string` (Protobuf field number 1; repeated=False)<br>`material: string` (Protobuf field number 2; repeated=False) |
| `SetAssignedMaterialResponse` | `material: ansys.api.geometry.v0.Material` (Protobuf field number 1; repeated=False) |
| `SetColorRequest` | `body_id: string` (Protobuf field number 1; repeated=False)<br>`color: string` (Protobuf field number 2; repeated=False) |
| `SetColorResponse` | `result: bool` (Protobuf field number 1; repeated=False) |
| `SetFillStyleRequest` | `body_id: string` (Protobuf field number 1; repeated=False)<br>`fill_style: ansys.api.geometry.v0.BodyFillStyle` (Protobuf field number 2; repeated=False) |
| `SetFillStyleResponse` | `result: bool` (Protobuf field number 1; repeated=False) |
| `SetNameRequest` | `body_id: string` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False) |
| `SetNameResponse` | `result: bool` (Protobuf field number 1; repeated=False) |
| `SetSuppressedRequest` | `bodies: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`is_suppressed: bool` (Protobuf field number 2; repeated=False) |
| `SweepWithGuideRequest` | `request_data: ansys.api.geometry.v0.bodies.SweepWithGuideRequestData` (Protobuf field number 1; repeated=True) |
| `SweepWithGuideRequestData` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`plane: ansys.api.geometry.v0.Plane` (Protobuf field number 3; repeated=False)<br>`geometries: ansys.api.geometry.v0.Geometries` (Protobuf field number 4; repeated=False)<br>`path: ansys.api.geometry.v0.TrimmedCurve` (Protobuf field number 5; repeated=False)<br>`guide: ansys.api.geometry.v0.TrimmedCurve` (Protobuf field number 6; repeated=False)<br>`tight_tolerance: bool` (Protobuf field number 7; repeated=False) |
| `SweepWithGuideResponse` | `bodies: ansys.api.geometry.v0.Body` (Protobuf field number 1; repeated=True) |
| `TranslateRequest` | `ids: string` (Protobuf field number 1; repeated=True)<br>`direction: ansys.api.geometry.v0.Direction` (Protobuf field number 2; repeated=False)<br>`distance: float` (Protobuf field number 3; repeated=False) |

### `ansys.api.geometry.v0.commands_pb2`

| Message | Fields |
| --- | --- |
| `AssignMidSurfaceOffsetTypeRequest` | `bodies_or_faces: string` (Protobuf field number 1; repeated=True)<br>`offset_type: ansys.api.geometry.v0.MidSurfaceOffsetType` (Protobuf field number 2; repeated=False) |
| `AssignMidSurfaceThicknessRequest` | `bodies_or_faces: string` (Protobuf field number 1; repeated=True)<br>`thickness: double` (Protobuf field number 2; repeated=False) |
| `ChamferRequest` | `ids: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`distance: double` (Protobuf field number 2; repeated=False) |
| `ChamferResponse` | `success: bool` (Protobuf field number 1; repeated=False)<br>`created_faces: ansys.api.geometry.v0.Face` (Protobuf field number 2; repeated=True)<br>`created_edges: ansys.api.geometry.v0.Edge` (Protobuf field number 3; repeated=True)<br>`created_surfaces: ansys.api.geometry.v0.Body` (Protobuf field number 4; repeated=True) |
| `CombineIntersectBodiesRequest` | `target_selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tool_selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`keep_cutter: bool` (Protobuf field number 3; repeated=False)<br>`subtract_from_target: bool` (Protobuf field number 4; repeated=False)<br>`transfer_named_selections: bool` (Protobuf field number 5; repeated=False) |
| `CombineMergeBodiesRequest` | `target_selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `CommandResponse` | `success: bool` (Protobuf field number 1; repeated=False)<br>`created_bodies: ansys.api.geometry.v0.Body` (Protobuf field number 2; repeated=True)<br>`modified_bodies: ansys.api.geometry.v0.Body` (Protobuf field number 3; repeated=True)<br>`deleted_bodies: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 4; repeated=True)<br>`created_faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 5; repeated=True)<br>`modified_faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 6; repeated=True)<br>`deleted_faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 7; repeated=True)<br>`created_edges: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 8; repeated=True)<br>`modified_edges: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 9; repeated=True)<br>`deleted_edges: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 10; repeated=True)<br>`created_components: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 11; repeated=True)<br>`modified_components: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 12; repeated=True)<br>`deleted_components: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 13; repeated=True) |
| `CoordinateSystemList` | `coordinate_systems: ansys.api.geometry.v0.CoordinateSystem` (Protobuf field number 1; repeated=True) |
| `CreateAlignTangentOrientGearConditionRequest` | `parent: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`geometric_a: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`geometric_b: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 3; repeated=False) |
| `CreateAnchorConditionRequest` | `parent: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`component: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=False) |
| `CreateBeamCircularProfileRequest` | `plane: ansys.api.geometry.v0.Plane` (Protobuf field number 1; repeated=False)<br>`radius: double` (Protobuf field number 2; repeated=False)<br>`origin: ansys.api.geometry.v0.Point` (Protobuf field number 3; repeated=False)<br>`name: string` (Protobuf field number 4; repeated=False) |
| `CreateBeamCircularProfileResponse` | `id: string` (Protobuf field number 1; repeated=False) |
| `CreateBeamSegmentRequest` | `profile: string` (Protobuf field number 1; repeated=False)<br>`line: ansys.api.geometry.v0.Line` (Protobuf field number 2; repeated=False)<br>`arc: ansys.api.geometry.v0.Arc` (Protobuf field number 3; repeated=False)<br>`circle: ansys.api.geometry.v0.Circle` (Protobuf field number 4; repeated=False)<br>`plane: ansys.api.geometry.v0.Plane` (Protobuf field number 5; repeated=False)<br>`parent: string` (Protobuf field number 6; repeated=False) |
| `CreateBeamSegmentResponse` | `id: string` (Protobuf field number 1; repeated=False)<br>`created_beam: ansys.api.geometry.v0.Beam` (Protobuf field number 2; repeated=False) |
| `CreateBeamSegmentsRequest` | `profile: string` (Protobuf field number 1; repeated=False)<br>`lines: ansys.api.geometry.v0.Line` (Protobuf field number 2; repeated=True)<br>`arcs: ansys.api.geometry.v0.Arc` (Protobuf field number 3; repeated=True)<br>`circles: ansys.api.geometry.v0.Circle` (Protobuf field number 4; repeated=True)<br>`planes: ansys.api.geometry.v0.Plane` (Protobuf field number 5; repeated=True)<br>`parent: string` (Protobuf field number 7; repeated=False) |
| `CreateBeamSegmentsResponse` | `ids: string` (Protobuf field number 1; repeated=True)<br>`created_beams: ansys.api.geometry.v0.Beam` (Protobuf field number 2; repeated=True) |
| `CreateCircularPatternRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`circular_angle: double` (Protobuf field number 2; repeated=False)<br>`circular_axis: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 3; repeated=False)<br>`circular_count: int32` (Protobuf field number 4; repeated=False)<br>`linear_count: int32` (Protobuf field number 5; repeated=False)<br>`linear_pitch: double` (Protobuf field number 6; repeated=False)<br>`two_dimensional: bool` (Protobuf field number 7; repeated=False)<br>`radial_direction: ansys.api.geometry.v0.Direction` (Protobuf field number 8; repeated=False)<br>`axis: ansys.api.geometry.v0.Line` (Protobuf field number 9; repeated=False) |
| `CreateCurvesFromProfileRequest` | `geometries: ansys.api.geometry.v0.Geometries` (Protobuf field number 1; repeated=False)<br>`parent: string` (Protobuf field number 2; repeated=False)<br>`plane: ansys.api.geometry.v0.Plane` (Protobuf field number 3; repeated=False) |
| `CreateCurvesFromProfileResponse` | `design_curves: string` (Protobuf field number 1; repeated=True) |
| `CreateDesignPointRequest` | `point: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=False)<br>`parent: string` (Protobuf field number 2; repeated=False) |
| `CreateDesignPointResponse` | `id: string` (Protobuf field number 1; repeated=False) |
| `CreateDesignPointsRequest` | `points: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=True)<br>`parent: string` (Protobuf field number 2; repeated=False) |
| `CreateDesignPointsResponse` | `ids: string` (Protobuf field number 1; repeated=True) |
| `CreateFillPatternRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`column_x_offset: double` (Protobuf field number 2; repeated=False)<br>`column_y_offset: double` (Protobuf field number 3; repeated=False)<br>`fill_pattern_type: ansys.api.geometry.v0.FillPatternType` (Protobuf field number 4; repeated=False)<br>`linear_direction: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 5; repeated=False)<br>`margin: double` (Protobuf field number 6; repeated=False)<br>`row_x_offset: double` (Protobuf field number 7; repeated=False)<br>`row_y_offset: double` (Protobuf field number 8; repeated=False)<br>`x_spacing: double` (Protobuf field number 9; repeated=False)<br>`y_spacing: double` (Protobuf field number 10; repeated=False) |
| `CreateLinearPatternRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`two_dimensional: bool` (Protobuf field number 2; repeated=False)<br>`linear_direction: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 3; repeated=False)<br>`count_x: int32` (Protobuf field number 4; repeated=False)<br>`count_y: int32` (Protobuf field number 5; repeated=False)<br>`pitch_x: double` (Protobuf field number 6; repeated=False)<br>`pitch_y: double` (Protobuf field number 7; repeated=False) |
| `CreateNurbsFromControlPointsRequest` | `nurbs_data: ansys.api.geometry.v0.NurbsData` (Protobuf field number 1; repeated=False)<br>`control_points: ansys.api.geometry.v0.ControlPoint` (Protobuf field number 2; repeated=True) |
| `CreatePlaneRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `CreatePlaneResponse` | `planes: ansys.api.geometry.v0.DatumPlane` (Protobuf field number 1; repeated=True) |
| `CreateRigidConditionRequest` | `parent: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`component_a: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`component_b: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 3; repeated=False) |
| `CreateSketchLineRequest` | `point1: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=False)<br>`point2: ansys.api.geometry.v0.Point` (Protobuf field number 2; repeated=False) |
| `CreateSphereRequest` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent: string` (Protobuf field number 2; repeated=False)<br>`point: ansys.api.geometry.v0.Point` (Protobuf field number 3; repeated=False)<br>`radius: double` (Protobuf field number 4; repeated=False) |
| `CreateSphereResponse` | `id: string` (Protobuf field number 1; repeated=False) |
| `CreateTorusRequest` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent: string` (Protobuf field number 2; repeated=False)<br>`major_radius: double` (Protobuf field number 3; repeated=False)<br>`minor_radius: double` (Protobuf field number 4; repeated=False)<br>`frame: ansys.api.geometry.v0.Frame` (Protobuf field number 5; repeated=False) |
| `CreateTorusResponse` | `id: string` (Protobuf field number 1; repeated=False) |
| `CreatedCurvesCommandResponse` | `result: ansys.api.dbu.v0.RequestResult` (Protobuf field number 1; repeated=False)<br>`created_curves: ansys.api.geometry.v0.Curve` (Protobuf field number 2; repeated=True) |
| `DeleteEntitiesRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `DeleteEntitiesResponse` | `deleted_entities: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `DetachFacesRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `DisposeTrackerRequest` | `design_id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `DisposeTrackerResponse` | `success: bool` (Protobuf field number 1; repeated=False) |
| `DownloadFileResponse` | `data: bytes` (Protobuf field number 1; repeated=False) |
| `DraftFacesRequest` | `faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`reference_faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`draft_side: ansys.api.geometry.v0.DraftSide` (Protobuf field number 3; repeated=False)<br>`draft_angle: double` (Protobuf field number 4; repeated=False)<br>`extrude_type: ansys.api.geometry.v0.ExtrudeType` (Protobuf field number 5; repeated=False) |
| `DraftFacesResponse` | `created_faces: ansys.api.geometry.v0.Face` (Protobuf field number 1; repeated=True) |
| `EvaluateNurbsCurveRequest` | `curve: ansys.api.geometry.v0.NurbsCurve` (Protobuf field number 1; repeated=False)<br>`parameter: double` (Protobuf field number 2; repeated=False) |
| `ExtrudeEdgesRequest` | `edges: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`face: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`point: ansys.api.geometry.v0.Point` (Protobuf field number 3; repeated=False)<br>`direction: ansys.api.geometry.v0.Direction` (Protobuf field number 4; repeated=False)<br>`distance: double` (Protobuf field number 5; repeated=False)<br>`extrude_type: ansys.api.geometry.v0.ExtrudeType` (Protobuf field number 6; repeated=False)<br>`pull_symmetric: bool` (Protobuf field number 7; repeated=False)<br>`copy: bool` (Protobuf field number 8; repeated=False)<br>`natural_extension: bool` (Protobuf field number 9; repeated=False) |
| `ExtrudeEdgesUpToRequest` | `edges: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`up_to_selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`seed_point: ansys.api.geometry.v0.Point` (Protobuf field number 3; repeated=False)<br>`direction: ansys.api.geometry.v0.Direction` (Protobuf field number 4; repeated=False)<br>`extrude_type: ansys.api.geometry.v0.ExtrudeType` (Protobuf field number 5; repeated=False) |
| `ExtrudeFacesRequest` | `faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`distance: double` (Protobuf field number 2; repeated=False)<br>`direction: ansys.api.geometry.v0.Direction` (Protobuf field number 3; repeated=False)<br>`extrude_type: ansys.api.geometry.v0.ExtrudeType` (Protobuf field number 4; repeated=False)<br>`pull_symmetric: bool` (Protobuf field number 5; repeated=False)<br>`offset_mode: ansys.api.geometry.v0.OffsetMode` (Protobuf field number 6; repeated=False)<br>`copy: bool` (Protobuf field number 7; repeated=False)<br>`force_do_as_extrude: bool` (Protobuf field number 8; repeated=False) |
| `ExtrudeFacesUpToRequest` | `faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`up_to_selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`direction: ansys.api.geometry.v0.Direction` (Protobuf field number 3; repeated=False)<br>`extrude_type: ansys.api.geometry.v0.ExtrudeType` (Protobuf field number 4; repeated=False)<br>`pull_symmetric: bool` (Protobuf field number 5; repeated=False)<br>`offset_mode: ansys.api.geometry.v0.OffsetMode` (Protobuf field number 6; repeated=False)<br>`copy: bool` (Protobuf field number 7; repeated=False)<br>`force_do_as_extrude: bool` (Protobuf field number 8; repeated=False)<br>`seed_point: ansys.api.geometry.v0.Point` (Protobuf field number 9; repeated=False) |
| `FaceOffsetRequest` | `face1: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`face2: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`set_baselines: bool` (Protobuf field number 3; repeated=False)<br>`process_adjacent_faces: bool` (Protobuf field number 4; repeated=False) |
| `FillFacesRequest` | `faces: ansys.api.geometry.v0.Face` (Protobuf field number 1; repeated=True) |
| `FilletRequest` | `ids: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`radius: double` (Protobuf field number 2; repeated=False) |
| `FullFilletRequest` | `faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `GetAllCADWeldsResponse` | `welds: ansys.api.geometry.v0.Weld` (Protobuf field number 1; repeated=True) |
| `GetAllSpotWeldsResponse` | `welds: ansys.api.geometry.v0.SpotWeld` (Protobuf field number 1; repeated=True) |
| `GetAssemblyResponse` | `parts: ansys.api.geometry.v0.Part` (Protobuf field number 1; repeated=True)<br>`transformed_parts: ansys.api.geometry.v0.Component` (Protobuf field number 2; repeated=True)<br>`components: ansys.api.geometry.v0.Component` (Protobuf field number 3; repeated=True)<br>`bodies: ansys.api.geometry.v0.Body` (Protobuf field number 4; repeated=True)<br>`materials: ansys.api.geometry.v0.Material` (Protobuf field number 5; repeated=True)<br>`named_selections: ansys.api.geometry.v0.NamedSelection` (Protobuf field number 6; repeated=True)<br>`component_coord_systems: ansys.api.geometry.v0.commands.GetAssemblyResponse.ComponentCoordSystemsEntry` (Protobuf field number 7; repeated=True)<br>`component_shared_topologies: ansys.api.geometry.v0.commands.GetAssemblyResponse.ComponentSharedTopologiesEntry` (Protobuf field number 8; repeated=True)<br>`beams: ansys.api.geometry.v0.Beam` (Protobuf field number 9; repeated=True)<br>`design_points: ansys.api.geometry.v0.Curve` (Protobuf field number 10; repeated=True) |
| `GetBeamProfileNameResponse` | `name: string` (Protobuf field number 1; repeated=False) |
| `GetBeamProfilePartsResponse` | `parts: ansys.api.geometry.v0.Part` (Protobuf field number 1; repeated=True) |
| `GetTrackerChangesRequest` | `design_id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `GetTrackerChangesResponse` | `changes: ansys.api.geometry.v0.TrackerCommandResponse` (Protobuf field number 1; repeated=False) |
| `GetTrackerRequest` | `design_id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `GetTrackerResponse` | `tracker: ansys.api.geometry.v0.TrackerDefinition` (Protobuf field number 1; repeated=False) |
| `ImprintCurvesAndSyncResponse` | `created_entities: ansys.api.geometry.v0.EntitiesCollection` (Protobuf field number 1; repeated=False)<br>`deleted_faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `ImprintCurvesRequest` | `body: string` (Protobuf field number 1; repeated=False)<br>`curves: ansys.api.geometry.v0.Geometries` (Protobuf field number 2; repeated=False)<br>`faces: string` (Protobuf field number 3; repeated=True)<br>`plane: ansys.api.geometry.v0.Plane` (Protobuf field number 4; repeated=False)<br>`trimmed_curves: ansys.api.geometry.v0.TrimmedCurve` (Protobuf field number 5; repeated=True) |
| `IntersectCurveAndSurfaceRequest` | `request_data: ansys.api.geometry.v0.commands.IntersectCurveAndSurfaceRequestData` (Protobuf field number 1; repeated=True) |
| `IntersectCurveAndSurfaceRequestData` | `curve: ansys.api.geometry.v0.CurveGeometry` (Protobuf field number 1; repeated=False)<br>`surface: ansys.api.geometry.v0.Surface` (Protobuf field number 2; repeated=False)<br>`surface_type: ansys.api.geometry.v0.SurfaceType` (Protobuf field number 3; repeated=False) |
| `IntersectCurveAndSurfaceResponse` | `response_data: ansys.api.geometry.v0.commands.IntersectCurveAndSurfaceResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.geometry.v0.commands.CommandResponse` (Protobuf field number 2; repeated=False) |
| `IntersectCurveAndSurfaceResponseData` | `points: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=True)<br>`intersect: bool` (Protobuf field number 2; repeated=False) |
| `IntersectCurvesRequest` | `first: ansys.api.geometry.v0.TrimmedCurve` (Protobuf field number 1; repeated=False)<br>`second: ansys.api.geometry.v0.TrimmedCurve` (Protobuf field number 2; repeated=False) |
| `IntersectCurvesResponse` | `points: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=True)<br>`intersect: bool` (Protobuf field number 2; repeated=False) |
| `MergeBodiesRequest` | `target_selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`abort_on_error: bool` (Protobuf field number 2; repeated=False)<br>`can_make_independent: bool` (Protobuf field number 3; repeated=False)<br>`create_imprints: bool` (Protobuf field number 4; repeated=False) |
| `MirrorRequest` | `mirror_plane: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `ModifyCircularPatternRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`circular_count: int32` (Protobuf field number 2; repeated=False)<br>`linear_count: int32` (Protobuf field number 3; repeated=False)<br>`step_angle: double` (Protobuf field number 4; repeated=False)<br>`step_linear: double` (Protobuf field number 5; repeated=False) |
| `ModifyLinearPatternRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`count_x: int32` (Protobuf field number 2; repeated=False)<br>`count_y: int32` (Protobuf field number 3; repeated=False)<br>`pitch_x: double` (Protobuf field number 4; repeated=False)<br>`pitch_y: double` (Protobuf field number 5; repeated=False)<br>`new_seed_index: int32` (Protobuf field number 6; repeated=False)<br>`old_seed_index: int32` (Protobuf field number 7; repeated=False) |
| `MoveImprintEdgesRequest` | `edges: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`direction: ansys.api.geometry.v0.Direction` (Protobuf field number 2; repeated=False)<br>`distance: double` (Protobuf field number 3; repeated=False) |
| `MoveImprintEdgesResponse` | `result: ansys.api.dbu.v0.RequestResult` (Protobuf field number 1; repeated=False)<br>`created_edges: ansys.api.geometry.v0.Edge` (Protobuf field number 2; repeated=True)<br>`created_faces: ansys.api.geometry.v0.Face` (Protobuf field number 3; repeated=True) |
| `MoveRotateRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`axis: ansys.api.geometry.v0.Line` (Protobuf field number 2; repeated=False)<br>`angle: double` (Protobuf field number 3; repeated=False) |
| `MoveTranslateRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`direction: ansys.api.geometry.v0.Direction` (Protobuf field number 2; repeated=False)<br>`distance: double` (Protobuf field number 3; repeated=False)<br>`named_selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 4; repeated=False) |
| `NurbsCurveResponse` | `result: ansys.api.dbu.v0.RequestResult` (Protobuf field number 1; repeated=False)<br>`created_curve: ansys.api.geometry.v0.NurbsCurve` (Protobuf field number 2; repeated=False) |
| `OffsetEdgesRequest` | `edges: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`value: double` (Protobuf field number 2; repeated=False) |
| `OffsetFaceCurvesRequest` | `objects: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`offset: double` (Protobuf field number 2; repeated=False) |
| `OffsetFacesSetRadiusRequest` | `face: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`radius: double` (Protobuf field number 2; repeated=False)<br>`copy: bool` (Protobuf field number 3; repeated=False)<br>`offset_mode: ansys.api.geometry.v0.OffsetMode` (Protobuf field number 4; repeated=False)<br>`extrude_type: ansys.api.geometry.v0.ExtrudeType` (Protobuf field number 5; repeated=False)<br>`faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 6; repeated=True) |
| `PatternCommandResponse` | `result: ansys.api.dbu.v0.RequestResult` (Protobuf field number 1; repeated=False)<br>`created_faces: ansys.api.geometry.v0.Face` (Protobuf field number 2; repeated=True)<br>`created_edges: ansys.api.geometry.v0.Edge` (Protobuf field number 3; repeated=True)<br>`modified_bodies: ansys.api.geometry.v0.Body` (Protobuf field number 4; repeated=True) |
| `PatternRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `PowerSelectFacesByAreaRangeRequest` | `body: string` (Protobuf field number 1; repeated=False)<br>`area1: double` (Protobuf field number 2; repeated=False)<br>`area2: double` (Protobuf field number 3; repeated=False) |
| `PowerSelectFacesByAreaRangeResponse` | `faces: ansys.api.geometry.v0.Face` (Protobuf field number 1; repeated=True) |
| `ProjectCurvesRequest` | `body: string` (Protobuf field number 1; repeated=False)<br>`curves: ansys.api.geometry.v0.Geometries` (Protobuf field number 2; repeated=False)<br>`direction: ansys.api.geometry.v0.Direction` (Protobuf field number 3; repeated=False)<br>`closest_face: bool` (Protobuf field number 4; repeated=False)<br>`plane: ansys.api.geometry.v0.Plane` (Protobuf field number 5; repeated=False) |
| `ProjectCurvesResponse` | `faces: ansys.api.geometry.v0.Face` (Protobuf field number 1; repeated=True) |
| `ProjectPointRequest` | `curve: ansys.api.geometry.v0.NurbsCurve` (Protobuf field number 1; repeated=False)<br>`point: ansys.api.geometry.v0.Point` (Protobuf field number 2; repeated=False) |
| `ProjectToSolidRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`target_faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`direction_selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 3; repeated=False) |
| `PullCurvePointRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`distance: double` (Protobuf field number 2; repeated=False)<br>`linear: bool` (Protobuf field number 3; repeated=False)<br>`reversed: bool` (Protobuf field number 4; repeated=False) |
| `RayFireAddtionalOptions` | `radius: double` (Protobuf field number 1; repeated=False)<br>`direction: ansys.api.geometry.v0.Direction` (Protobuf field number 2; repeated=False)<br>`max_distance: double` (Protobuf field number 3; repeated=False)<br>`min_distance: double` (Protobuf field number 4; repeated=False)<br>`tight_tolerance: bool` (Protobuf field number 5; repeated=False)<br>`pick_back_faces: bool` (Protobuf field number 6; repeated=False)<br>`max_hits: int32` (Protobuf field number 7; repeated=False)<br>`request_params: bool` (Protobuf field number 8; repeated=False)<br>`request_secondary: bool` (Protobuf field number 9; repeated=False) |
| `RayFireFacesRequest` | `request_data: ansys.api.geometry.v0.commands.RayFireFacesRequestData` (Protobuf field number 1; repeated=True) |
| `RayFireFacesRequestData` | `body: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`points: ansys.api.geometry.v0.Point` (Protobuf field number 3; repeated=True)<br>`options: ansys.api.geometry.v0.commands.RayFireAddtionalOptions` (Protobuf field number 4; repeated=False) |
| `RayFireFacesResponse` | `response_data: ansys.api.geometry.v0.commands.RayFireFacesResponseData` (Protobuf field number 1; repeated=True) |
| `RayFireFacesResponseData` | `faces_ray_fire_impacts: ansys.api.geometry.v0.RayFireFaceImpacts` (Protobuf field number 1; repeated=True) |
| `RayFireOrderedRequest` | `request_data: ansys.api.geometry.v0.commands.RayFireOrderedRequestData` (Protobuf field number 1; repeated=True) |
| `RayFireOrderedRequestData` | `body: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`direction: ansys.api.geometry.v0.Direction` (Protobuf field number 3; repeated=False)<br>`ray_radius: double` (Protobuf field number 4; repeated=False)<br>`points: ansys.api.geometry.v0.Point` (Protobuf field number 5; repeated=True)<br>`max_distance: double` (Protobuf field number 6; repeated=False)<br>`tight_tolerance: bool` (Protobuf field number 7; repeated=False) |
| `RayFireOrderedResponse` | `response_data: ansys.api.geometry.v0.commands.RayFireOrderedResponseData` (Protobuf field number 1; repeated=True) |
| `RayFireOrderedResponseData` | `ordered_ray_fire_impacts: ansys.api.geometry.v0.RayFireImpacts` (Protobuf field number 1; repeated=True) |
| `RayFireOrderedUVRequest` | `request_data: ansys.api.geometry.v0.commands.RayFireOrderedUVRequestData` (Protobuf field number 1; repeated=True) |
| `RayFireOrderedUVRequestData` | `body: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`direction: ansys.api.geometry.v0.Direction` (Protobuf field number 3; repeated=False)<br>`ray_radius: double` (Protobuf field number 4; repeated=False)<br>`points: ansys.api.geometry.v0.Point` (Protobuf field number 5; repeated=True)<br>`max_distance: double` (Protobuf field number 6; repeated=False)<br>`tight_tolerance: bool` (Protobuf field number 7; repeated=False) |
| `RayFireOrderedUVResponse` | `response_data: ansys.api.geometry.v0.commands.RayFireOrderedUVResponseData` (Protobuf field number 1; repeated=True) |
| `RayFireOrderedUVResponseData` | `ordered_ray_fire_impacts: ansys.api.geometry.v0.RayFireUVImpacts` (Protobuf field number 1; repeated=True) |
| `RayFireRequest` | `request_data: ansys.api.geometry.v0.commands.RayFireRequestData` (Protobuf field number 1; repeated=True) |
| `RayFireRequestData` | `body: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`direction: ansys.api.geometry.v0.Direction` (Protobuf field number 3; repeated=False)<br>`points: ansys.api.geometry.v0.Point` (Protobuf field number 4; repeated=True)<br>`max_distance: double` (Protobuf field number 5; repeated=False) |
| `RayFireResponse` | `response_data: ansys.api.geometry.v0.commands.RayFireResponseData` (Protobuf field number 1; repeated=True) |
| `RayFireResponseData` | `single_ray_fire_impacts: ansys.api.geometry.v0.RayFireImpacts` (Protobuf field number 1; repeated=False) |
| `RemoveFacesRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`offset: double` (Protobuf field number 2; repeated=False) |
| `RenameManyRequest` | `ids_updates: ansys.api.geometry.v0.commands.RenameManyRequest.IdsUpdatesEntry` (Protobuf field number 1; repeated=True) |
| `RenameManyResponse` | `results: ansys.api.geometry.v0.commands.RenameManyResponse.ResultsEntry` (Protobuf field number 1; repeated=True) |
| `RenameObjectRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`name: string` (Protobuf field number 2; repeated=False) |
| `RenameRequest` | `id: string` (Protobuf field number 1; repeated=False)<br>`type: ansys.api.geometry.v0.EntityType` (Protobuf field number 2; repeated=False)<br>`new_name: string` (Protobuf field number 3; repeated=False) |
| `RenameResponse` | `result: string` (Protobuf field number 1; repeated=False) |
| `ReplaceFaceRequest` | `target_selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`replacement_selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `RevolveCurvesRequest` | `curves: ansys.api.geometry.v0.TrimmedCurve` (Protobuf field number 1; repeated=True)<br>`axis: ansys.api.geometry.v0.Line` (Protobuf field number 2; repeated=False)<br>`angle: double` (Protobuf field number 3; repeated=False)<br>`symmetric: bool` (Protobuf field number 4; repeated=False) |
| `RevolveFacesByHelixRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`direction: ansys.api.geometry.v0.Direction` (Protobuf field number 2; repeated=False)<br>`axis: ansys.api.geometry.v0.Line` (Protobuf field number 3; repeated=False)<br>`height: double` (Protobuf field number 4; repeated=False)<br>`pitch: double` (Protobuf field number 5; repeated=False)<br>`taper_angle: double` (Protobuf field number 6; repeated=False)<br>`right_handed: bool` (Protobuf field number 7; repeated=False)<br>`both_sides: bool` (Protobuf field number 8; repeated=False)<br>`extrude_type: ansys.api.geometry.v0.ExtrudeType` (Protobuf field number 9; repeated=False) |
| `RevolveFacesRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`axis: ansys.api.geometry.v0.Line` (Protobuf field number 2; repeated=False)<br>`angle: double` (Protobuf field number 3; repeated=False)<br>`alternate_axis: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 4; repeated=True)<br>`alternate_direction: ansys.api.geometry.v0.Direction` (Protobuf field number 5; repeated=False)<br>`extrude_type: ansys.api.geometry.v0.ExtrudeType` (Protobuf field number 6; repeated=False) |
| `RevolveFacesUpToRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`up_to_selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`direction: ansys.api.geometry.v0.Direction` (Protobuf field number 3; repeated=False)<br>`axis: ansys.api.geometry.v0.Line` (Protobuf field number 4; repeated=False)<br>`extrude_type: ansys.api.geometry.v0.ExtrudeType` (Protobuf field number 5; repeated=False) |
| `RevolvePointsByHelixRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`axis: ansys.api.geometry.v0.Line` (Protobuf field number 2; repeated=False)<br>`height: double` (Protobuf field number 3; repeated=False)<br>`pitch: double` (Protobuf field number 4; repeated=False)<br>`taper_angle: double` (Protobuf field number 5; repeated=False)<br>`right_handed: bool` (Protobuf field number 6; repeated=False)<br>`pull_symmetric: bool` (Protobuf field number 7; repeated=False) |
| `RevolvePointsRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`axis: ansys.api.geometry.v0.Line` (Protobuf field number 2; repeated=False)<br>`angle: double` (Protobuf field number 3; repeated=False) |
| `RoundInfoRequest` | `face: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `RoundInfoResponse` | `along_u: bool` (Protobuf field number 1; repeated=False)<br>`radius: double` (Protobuf field number 2; repeated=False) |
| `ScaleNonUniformRequest` | `objects: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`frame: ansys.api.geometry.v0.Frame` (Protobuf field number 2; repeated=False)<br>`scale_vector: ansys.api.geometry.v0.Direction` (Protobuf field number 3; repeated=False)<br>`keep_holes: bool` (Protobuf field number 4; repeated=False) |
| `ScaleRequest` | `objects: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`point: ansys.api.geometry.v0.Point` (Protobuf field number 2; repeated=False)<br>`optional_direction: ansys.api.geometry.v0.Direction` (Protobuf field number 3; repeated=False)<br>`scale: double` (Protobuf field number 4; repeated=False)<br>`keep_holes: bool` (Protobuf field number 5; repeated=False) |
| `SetAutomaticTrackingStateRequest` | `state: ansys.api.geometry.v0.AutomaticTrackingState` (Protobuf field number 1; repeated=False) |
| `SetAutomaticTrackingStateResponse` | `success: bool` (Protobuf field number 1; repeated=False) |
| `SetPatternValueRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`modification_type: ansys.api.geometry.v0.PatternModificationType` (Protobuf field number 2; repeated=False)<br>`value: double` (Protobuf field number 3; repeated=False) |
| `ShellRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`offset: double` (Protobuf field number 2; repeated=False) |
| `SingleRenamedObject` | `new_name: string` (Protobuf field number 1; repeated=False)<br>`type: ansys.api.geometry.v0.EntityType` (Protobuf field number 2; repeated=False) |
| `SplitBodyRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`split_by_plane: ansys.api.geometry.v0.Plane` (Protobuf field number 2; repeated=False)<br>`split_by_slicer: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 3; repeated=True)<br>`split_by_faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 4; repeated=True)<br>`extend_surfaces: bool` (Protobuf field number 5; repeated=False) |
| `SplitEdgeRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`split_type: ansys.api.geometry.v0.commands.SplitEdgeType` (Protobuf field number 2; repeated=False)<br>`proportions: double` (Protobuf field number 3; repeated=True)<br>`points: ansys.api.geometry.v0.Point` (Protobuf field number 4; repeated=True)<br>`lengths: double` (Protobuf field number 5; repeated=True)<br>`reference: ansys.api.geometry.v0.commands.SplitEdgeReference` (Protobuf field number 6; repeated=False) |
| `SplitFaceRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`split_parameter: ansys.api.geometry.v0.Point` (Protobuf field number 2; repeated=False)<br>`split_start: ansys.api.geometry.v0.Point` (Protobuf field number 3; repeated=False)<br>`split_end: ansys.api.geometry.v0.Point` (Protobuf field number 4; repeated=False)<br>`face_cutter: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 5; repeated=False)<br>`split_curves: ansys.api.geometry.v0.TrimmedCurve` (Protobuf field number 6; repeated=True)<br>`split_type: ansys.api.geometry.v0.commands.SplitFaceType` (Protobuf field number 7; repeated=False)<br>`parameter_type: ansys.api.geometry.v0.commands.SplitFaceParameterType` (Protobuf field number 8; repeated=False) |
| `SweepFacesRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`trajectories: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`optional_distance: double` (Protobuf field number 3; repeated=False) |
| `SweepPointsRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`trajectories: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`distance: double` (Protobuf field number 3; repeated=False) |
| `ThickenFacesRequest` | `faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`direction: ansys.api.geometry.v0.Direction` (Protobuf field number 2; repeated=False)<br>`value: double` (Protobuf field number 3; repeated=False)<br>`extrude_type: ansys.api.geometry.v0.ExtrudeType` (Protobuf field number 4; repeated=False)<br>`pull_symmetric: bool` (Protobuf field number 5; repeated=False)<br>`select_direction: bool` (Protobuf field number 6; repeated=False) |
| `UploadFileRequest` | `data: bytes` (Protobuf field number 1; repeated=False)<br>`file_name: string` (Protobuf field number 2; repeated=False)<br>`open: bool` (Protobuf field number 3; repeated=False)<br>`import_options: ansys.api.geometry.v0.commands.UploadFileRequest.ImportOptionsEntry` (Protobuf field number 4; repeated=True)<br>`import_options_definitions: ansys.api.geometry.v0.commands.UploadFileRequest.ImportOptionsDefinitionsEntry` (Protobuf field number 5; repeated=True) |
| `UploadFileResponse` | `file_path: string` (Protobuf field number 1; repeated=False)<br>`document_id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=False) |

### `ansys.api.geometry.v0.components_pb2`

| Message | Fields |
| --- | --- |
| `CreateRequest` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent: string` (Protobuf field number 2; repeated=False)<br>`template: string` (Protobuf field number 3; repeated=False)<br>`instance_name: string` (Protobuf field number 4; repeated=False) |
| `CreateResponse` | `component: ansys.api.geometry.v0.Component` (Protobuf field number 1; repeated=False)<br>`template: string` (Protobuf field number 2; repeated=False) |
| `GetAllRequest` | `parent: string` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `components: ansys.api.geometry.v0.Component` (Protobuf field number 1; repeated=True) |
| `GetBeamBodiesResponse` | `beams: string` (Protobuf field number 1; repeated=True) |
| `GetBodiesResponse` | `bodies: ansys.api.geometry.v0.Body` (Protobuf field number 1; repeated=True) |
| `GetComponentNameResponse` | `name: string` (Protobuf field number 1; repeated=False) |
| `GetRootComponentResponse` | `id: string` (Protobuf field number 1; repeated=False) |
| `ImportGroupsRequest` | `id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `ImportGroupsResponse` | — |
| `MakeIndependentRequest` | `ids: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `MakeIndependentResponse` | — |
| `SetPlacementRequest` | `id: string` (Protobuf field number 1; repeated=False)<br>`translation: ansys.api.geometry.v0.Direction` (Protobuf field number 2; repeated=False)<br>`rotation_axis_origin: ansys.api.geometry.v0.Point` (Protobuf field number 3; repeated=False)<br>`rotation_axis_direction: ansys.api.geometry.v0.Direction` (Protobuf field number 4; repeated=False)<br>`rotation_angle: double` (Protobuf field number 5; repeated=False) |
| `SetPlacementResponse` | `matrix: ansys.api.geometry.v0.Matrix` (Protobuf field number 1; repeated=False) |
| `SetSharedTopologyRequest` | `id: string` (Protobuf field number 1; repeated=False)<br>`share_type: ansys.api.geometry.v0.ShareType` (Protobuf field number 2; repeated=False) |

### `ansys.api.geometry.v0.coordinatesystems_pb2`

| Message | Fields |
| --- | --- |
| `CreateRequest` | `parent: string` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`frame: ansys.api.geometry.v0.Frame` (Protobuf field number 3; repeated=False) |
| `CreateResponse` | `coordinate_system: ansys.api.geometry.v0.CoordinateSystem` (Protobuf field number 1; repeated=False) |
| `DeleteRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `DeleteResponse` | `deleted_coordinates_systems: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `GetAllRequest` | `parent: string` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `coordinate_systems: ansys.api.geometry.v0.CoordinateSystem` (Protobuf field number 1; repeated=True) |

### `ansys.api.geometry.v0.curves_pb2`

| Message | Fields |
| --- | --- |
| `DeleteRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `DeleteResponse` | `deleted_curves: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `GetAllRequest` | `parent: string` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `curves: ansys.api.geometry.v0.Curve` (Protobuf field number 1; repeated=True) |

### `ansys.api.geometry.v0.datumplanes_pb2`

| Message | Fields |
| --- | --- |
| `DeleteRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `DeleteResponse` | `deleted_planes: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `GetAllResponse` | `planes: ansys.api.geometry.v0.DatumPlane` (Protobuf field number 1; repeated=True) |
| `GetUpdateStateRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `IsDeletedRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `IsDeletedResponse` | `deleted: ansys.api.geometry.v0.datumplanes.IsDeletedResponse.DeletedEntry` (Protobuf field number 1; repeated=True) |
| `UpdateStateResponse` | `update_states: ansys.api.geometry.v0.datumplanes.UpdateStateResponse.UpdateStatesEntry` (Protobuf field number 1; repeated=True) |

### `ansys.api.geometry.v0.edges_pb2`

| Message | Fields |
| --- | --- |
| `DeleteRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `DeleteResponse` | `deleted_edges: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `GetAllRequest` | `parent: string` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `edges: ansys.api.geometry.v0.Edge` (Protobuf field number 1; repeated=True) |
| `GetFacesResponse` | `faces: ansys.api.geometry.v0.Face` (Protobuf field number 1; repeated=True) |
| `GetIntervalResponse` | `start: double` (Protobuf field number 1; repeated=False)<br>`end: double` (Protobuf field number 2; repeated=False) |
| `GetLengthResponse` | `length: double` (Protobuf field number 1; repeated=False) |
| `GetStartAndEndPointsResponse` | `start: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=False)<br>`end: ansys.api.geometry.v0.Point` (Protobuf field number 2; repeated=False) |
| `GetVerticesRequest` | `edge: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `GetVerticesResponse` | `vertices: ansys.api.geometry.v0.Vertex` (Protobuf field number 1; repeated=True) |
| `IsDeletedResponse` | `deleted: bool` (Protobuf field number 1; repeated=False) |

### `ansys.api.geometry.v0.faces_pb2`

| Message | Fields |
| --- | --- |
| `CreateIsoParamCurvesRequest` | `id: string` (Protobuf field number 1; repeated=False)<br>`u_dir_curve: bool` (Protobuf field number 2; repeated=False)<br>`proportion: double` (Protobuf field number 3; repeated=False) |
| `CreateIsoParamCurvesResponse` | `curves: ansys.api.geometry.v0.TrimmedCurve` (Protobuf field number 1; repeated=True) |
| `EvaluateRequest` | `id: string` (Protobuf field number 1; repeated=False)<br>`u: double` (Protobuf field number 2; repeated=False)<br>`v: double` (Protobuf field number 3; repeated=False) |
| `EvaluateResponse` | `point: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=False) |
| `GetAllRequest` | `parent: string` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `faces: ansys.api.geometry.v0.Face` (Protobuf field number 1; repeated=True) |
| `GetAreaResponse` | `area: double` (Protobuf field number 1; repeated=False) |
| `GetBoxUVResponse` | `start_u: double` (Protobuf field number 1; repeated=False)<br>`end_u: double` (Protobuf field number 2; repeated=False)<br>`start_v: double` (Protobuf field number 3; repeated=False)<br>`end_v: double` (Protobuf field number 4; repeated=False) |
| `GetClosestSeparationRequest` | `face_1: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`face_2: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=False) |
| `GetColorResponse` | `color: string` (Protobuf field number 1; repeated=False) |
| `GetEdgesResponse` | `edges: ansys.api.geometry.v0.Edge` (Protobuf field number 1; repeated=True) |
| `GetExternalEdgesResponse` | `edges: ansys.api.geometry.v0.Edge` (Protobuf field number 1; repeated=True) |
| `GetInternalEdgesResponse` | `edges: ansys.api.geometry.v0.Edge` (Protobuf field number 1; repeated=True) |
| `GetLoopsResponse` | `loops: ansys.api.geometry.v0.Loop` (Protobuf field number 1; repeated=True) |
| `GetNormalRequest` | `id: string` (Protobuf field number 1; repeated=False)<br>`u: double` (Protobuf field number 2; repeated=False)<br>`v: double` (Protobuf field number 3; repeated=False) |
| `GetNormalResponse` | `direction: ansys.api.geometry.v0.Direction` (Protobuf field number 1; repeated=False) |
| `GetVerticesRequest` | `face_id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `GetVerticesResponse` | `vertices: ansys.api.geometry.v0.Vertex` (Protobuf field number 1; repeated=True) |
| `IsDeletedResponse` | `deleted: bool` (Protobuf field number 1; repeated=False) |
| `OffsetFacesRequest` | `request_data: ansys.api.geometry.v0.faces.OffsetFacesRequestData` (Protobuf field number 1; repeated=True) |
| `OffsetFacesRequestData` | `faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`offset: double` (Protobuf field number 2; repeated=False)<br>`direction: ansys.api.geometry.v0.Direction` (Protobuf field number 3; repeated=False)<br>`extrude_type: ansys.api.geometry.v0.ExtrudeType` (Protobuf field number 4; repeated=False) |
| `OffsetFacesResponse` | `response_data: ansys.api.geometry.v0.faces.OffsetFacesResponseData` (Protobuf field number 1; repeated=True) |
| `OffsetFacesResponseData` | `new_faces: ansys.api.geometry.v0.Face` (Protobuf field number 1; repeated=True) |
| `SetColorRequest` | `face_id: string` (Protobuf field number 1; repeated=False)<br>`color: string` (Protobuf field number 2; repeated=False) |
| `SetColorResponse` | `success: bool` (Protobuf field number 1; repeated=False) |

### `ansys.api.geometry.v0.facettools_pb2`

| Message | Fields |
| --- | --- |
| `FacetAutoFixRequest` | `selection: ansys.api.geometry.v0.Mesh` (Protobuf field number 1; repeated=True) |
| `FacetAutoFixResponse` | `result: bool` (Protobuf field number 1; repeated=False) |
| `ShrinkWrapBodyRequest` | `selection: ansys.api.geometry.v0.Body` (Protobuf field number 1; repeated=True)<br>`options: ansys.api.geometry.v0.ShrinkWrapOptions` (Protobuf field number 2; repeated=False) |
| `ShrinkWrapBodyResponse` | `result: bool` (Protobuf field number 1; repeated=False) |
| `ShrinkWrapMeshRequest` | `selection: ansys.api.geometry.v0.Mesh` (Protobuf field number 1; repeated=True)<br>`options: ansys.api.geometry.v0.ShrinkWrapOptions` (Protobuf field number 2; repeated=False) |
| `ShrinkWrapMeshResponse` | `result: bool` (Protobuf field number 1; repeated=False) |

### `ansys.api.geometry.v0.materials_pb2`

| Message | Fields |
| --- | --- |
| `AddToDocumentRequest` | `material: ansys.api.geometry.v0.Material` (Protobuf field number 1; repeated=False) |
| `GetAllNamesResponse` | `materials: string` (Protobuf field number 1; repeated=True) |
| `RemoveFromDocumentRequest` | `request_data: ansys.api.geometry.v0.Material` (Protobuf field number 1; repeated=True) |
| `RemoveFromDocumentResponse` | `successfully_removed: string` (Protobuf field number 1; repeated=True) |

### `ansys.api.geometry.v0.measuretools_pb2`

| Message | Fields |
| --- | --- |
| `MinDistanceBetweenObjectsRequest` | `bodies: string` (Protobuf field number 1; repeated=True)<br>`selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `MinDistanceBetweenObjectsResponse` | `gap: ansys.api.geometry.v0.Gap` (Protobuf field number 1; repeated=False) |

### `ansys.api.geometry.v0.meshes_pb2`

| Message | Fields |
| --- | --- |
| `GetAllRequest` | `parent: string` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `meshes: ansys.api.geometry.v0.Mesh` (Protobuf field number 1; repeated=True) |

### `ansys.api.geometry.v0.models_pb2`

| Message | Fields |
| --- | --- |
| `AdjustSimplifyProblemArea` | `id: int32` (Protobuf field number 1; repeated=False)<br>`body_monikers: string` (Protobuf field number 2; repeated=True) |
| `AlignCondition` | `condition: ansys.api.geometry.v0.MatingCondition` (Protobuf field number 1; repeated=False)<br>`offset: double` (Protobuf field number 2; repeated=False)<br>`is_reversed: bool` (Protobuf field number 3; repeated=False)<br>`is_valid: bool` (Protobuf field number 4; repeated=False) |
| `AnchorCondition` | `condition: ansys.api.geometry.v0.MatingCondition` (Protobuf field number 1; repeated=False)<br>`component: ansys.api.geometry.v0.Component` (Protobuf field number 2; repeated=False) |
| `Arc` | `center: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=False)<br>`start: ansys.api.geometry.v0.Point` (Protobuf field number 2; repeated=False)<br>`end: ansys.api.geometry.v0.Point` (Protobuf field number 3; repeated=False)<br>`axis: ansys.api.geometry.v0.Direction` (Protobuf field number 4; repeated=False) |
| `Beam` | `name: string` (Protobuf field number 1; repeated=False)<br>`can_suppress: bool` (Protobuf field number 2; repeated=False)<br>`is_deleted: bool` (Protobuf field number 3; repeated=False)<br>`is_reversed: bool` (Protobuf field number 4; repeated=False)<br>`is_rigid: bool` (Protobuf field number 5; repeated=False)<br>`material: ansys.api.geometry.v0.Material` (Protobuf field number 6; repeated=False)<br>`id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 7; repeated=False)<br>`parent: ansys.api.geometry.v0.Part` (Protobuf field number 8; repeated=False)<br>`cross_section: ansys.api.geometry.v0.BeamCrossSectionInfo` (Protobuf field number 9; repeated=False)<br>`properties: ansys.api.geometry.v0.BeamProperties` (Protobuf field number 10; repeated=False)<br>`shape: ansys.api.geometry.v0.TrimmedCurve` (Protobuf field number 11; repeated=False)<br>`type: ansys.api.geometry.v0.BeamType` (Protobuf field number 12; repeated=False) |
| `BeamCrossSectionInfo` | `section_anchor: int32` (Protobuf field number 1; repeated=False)<br>`section_angle: double` (Protobuf field number 2; repeated=False)<br>`section_frame: ansys.api.geometry.v0.Frame` (Protobuf field number 3; repeated=False)<br>`section_profile: ansys.api.geometry.v0.TrimmedCurveList` (Protobuf field number 4; repeated=True) |
| `BeamProperties` | `area: double` (Protobuf field number 1; repeated=False)<br>`centroid_x: double` (Protobuf field number 2; repeated=False)<br>`centroid_y: double` (Protobuf field number 3; repeated=False)<br>`warping_constant: double` (Protobuf field number 4; repeated=False)<br>`ixx: double` (Protobuf field number 5; repeated=False)<br>`ixy: double` (Protobuf field number 6; repeated=False)<br>`iyy: double` (Protobuf field number 7; repeated=False)<br>`torsional_constant: double` (Protobuf field number 8; repeated=False)<br>`shear_center_x: double` (Protobuf field number 9; repeated=False)<br>`shear_center_y: double` (Protobuf field number 10; repeated=False) |
| `Body` | `id: string` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`can_suppress: bool` (Protobuf field number 3; repeated=False)<br>`is_deleted: bool` (Protobuf field number 4; repeated=False)<br>`is_suppressed: bool` (Protobuf field number 5; repeated=False)<br>`transform_to_master: ansys.api.geometry.v0.Matrix` (Protobuf field number 6; repeated=False)<br>`master: ansys.api.geometry.v0.BodyMasterNullable` (Protobuf field number 7; repeated=False)<br>`master_id: string` (Protobuf field number 8; repeated=False)<br>`parent_id: string` (Protobuf field number 9; repeated=False)<br>`is_surface: bool` (Protobuf field number 10; repeated=False) |
| `BodyMaster` | `update_state: string` (Protobuf field number 6; repeated=False)<br>`text_attributes: ansys.api.geometry.v0.BodyMaster.TextAttributesEntry` (Protobuf field number 7; repeated=True)<br>`number_attributes: ansys.api.geometry.v0.BodyMaster.NumberAttributesEntry` (Protobuf field number 8; repeated=True)<br>`material: ansys.api.geometry.v0.Material` (Protobuf field number 9; repeated=False)<br>`surface_material: ansys.api.geometry.v0.Material` (Protobuf field number 10; repeated=False)<br>`shape: ansys.api.geometry.v0.Shape` (Protobuf field number 11; repeated=False) |
| `BodyMasterNullable` | `null: google.protobuf.NullValue` (Protobuf field number 1; repeated=False)<br>`props: ansys.api.geometry.v0.BodyMaster` (Protobuf field number 2; repeated=False) |
| `Box` | `min: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=False)<br>`max: ansys.api.geometry.v0.Point` (Protobuf field number 2; repeated=False)<br>`center: ansys.api.geometry.v0.Point` (Protobuf field number 3; repeated=False) |
| `Circle` | `center: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=False)<br>`radius: double` (Protobuf field number 2; repeated=False) |
| `Component` | `id: string` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`part_occurrence: ansys.api.geometry.v0.Part` (Protobuf field number 3; repeated=False)<br>`placement: ansys.api.geometry.v0.Matrix` (Protobuf field number 4; repeated=False)<br>`master_id: string` (Protobuf field number 5; repeated=False)<br>`parent_id: string` (Protobuf field number 6; repeated=False)<br>`part_master: ansys.api.geometry.v0.Part` (Protobuf field number 7; repeated=False)<br>`display_name: string` (Protobuf field number 8; repeated=False)<br>`instance_name: string` (Protobuf field number 9; repeated=False) |
| `ControlPoint` | `position: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=False)<br>`weight: double` (Protobuf field number 2; repeated=False) |
| `CoordinateSystem` | `id: string` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`frame: ansys.api.geometry.v0.Frame` (Protobuf field number 3; repeated=False) |
| `Curve` | `id: string` (Protobuf field number 1; repeated=False)<br>`owner_name: string` (Protobuf field number 2; repeated=False)<br>`length: double` (Protobuf field number 3; repeated=False)<br>`points: ansys.api.geometry.v0.Point` (Protobuf field number 4; repeated=True)<br>`parent_id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 5; repeated=False) |
| `CurveEvaluation` | `curvature: double` (Protobuf field number 1; repeated=False)<br>`derivative: ansys.api.geometry.v0.Direction` (Protobuf field number 2; repeated=False)<br>`derivative2: ansys.api.geometry.v0.Direction` (Protobuf field number 3; repeated=False)<br>`param: double` (Protobuf field number 4; repeated=False)<br>`point: ansys.api.geometry.v0.Point` (Protobuf field number 5; repeated=False)<br>`tangent: ansys.api.geometry.v0.Direction` (Protobuf field number 6; repeated=False) |
| `CurveGapProblemArea` | `id: int32` (Protobuf field number 1; repeated=False)<br>`curve_point_monikers: string` (Protobuf field number 2; repeated=True) |
| `CurveGeometry` | `origin: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=False)<br>`radius: double` (Protobuf field number 2; repeated=False)<br>`major_radius: double` (Protobuf field number 3; repeated=False)<br>`minor_radius: double` (Protobuf field number 4; repeated=False)<br>`direction: ansys.api.geometry.v0.Direction` (Protobuf field number 5; repeated=False)<br>`reference: ansys.api.geometry.v0.Direction` (Protobuf field number 6; repeated=False)<br>`axis: ansys.api.geometry.v0.Direction` (Protobuf field number 7; repeated=False)<br>`nurbs_curve: ansys.api.geometry.v0.NurbsCurve` (Protobuf field number 8; repeated=False) |
| `DatumPlane` | `id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`plane: ansys.api.geometry.v0.Plane` (Protobuf field number 2; repeated=False)<br>`name: string` (Protobuf field number 3; repeated=False)<br>`is_suppressed: bool` (Protobuf field number 4; repeated=False)<br>`is_deleted: bool` (Protobuf field number 5; repeated=False)<br>`can_suppress: bool` (Protobuf field number 6; repeated=False)<br>`master_id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 7; repeated=False)<br>`parent_id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 8; repeated=False)<br>`curves: ansys.api.geometry.v0.Curve` (Protobuf field number 9; repeated=True) |
| `DetectHelixesOptions` | `min_radius: double` (Protobuf field number 1; repeated=False)<br>`max_radius: double` (Protobuf field number 2; repeated=False)<br>`fit_radius_error: double` (Protobuf field number 3; repeated=False) |
| `Direction` | `x: double` (Protobuf field number 1; repeated=False)<br>`y: double` (Protobuf field number 2; repeated=False)<br>`z: double` (Protobuf field number 3; repeated=False) |
| `DuplicateCurveProblemArea` | `id: int32` (Protobuf field number 1; repeated=False)<br>`curve_point_monikers: string` (Protobuf field number 2; repeated=True) |
| `DuplicateFaceProblemArea` | `id: int32` (Protobuf field number 1; repeated=False)<br>`face_monikers: string` (Protobuf field number 2; repeated=True) |
| `Edge` | `id: string` (Protobuf field number 1; repeated=False)<br>`parent: ansys.api.geometry.v0.Body` (Protobuf field number 2; repeated=False)<br>`curve_type: ansys.api.geometry.v0.CurveType` (Protobuf field number 10; repeated=False)<br>`owner_name: string` (Protobuf field number 11; repeated=False)<br>`export_id: string` (Protobuf field number 12; repeated=False)<br>`length: double` (Protobuf field number 13; repeated=False)<br>`owner_id: string` (Protobuf field number 14; repeated=False)<br>`is_reversed: bool` (Protobuf field number 15; repeated=False) |
| `EdgeTessellation` | `vertices: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=True) |
| `Ellipse` | `center: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=False)<br>`majorradius: double` (Protobuf field number 2; repeated=False)<br>`minorradius: double` (Protobuf field number 3; repeated=False)<br>`angle: double` (Protobuf field number 4; repeated=False) |
| `EnhancedRepairToolMessage` | `success: bool` (Protobuf field number 1; repeated=False)<br>`found: int32` (Protobuf field number 2; repeated=False)<br>`repaired: int32` (Protobuf field number 3; repeated=False)<br>`created_bodies_monikers: string` (Protobuf field number 4; repeated=True)<br>`modified_bodies_monikers: string` (Protobuf field number 5; repeated=True)<br>`deleted_bodies_monikers: string` (Protobuf field number 6; repeated=True)<br>`complete_command_response: ansys.api.geometry.v0.TrackerCommandResponse` (Protobuf field number 7; repeated=False) |
| `EntitiesCollection` | `curves: ansys.api.geometry.v0.Curve` (Protobuf field number 1; repeated=True)<br>`edges: ansys.api.geometry.v0.Edge` (Protobuf field number 2; repeated=True)<br>`faces: ansys.api.geometry.v0.Face` (Protobuf field number 3; repeated=True)<br>`bodies: ansys.api.geometry.v0.Body` (Protobuf field number 4; repeated=True) |
| `ExtraEdgeProblemArea` | `id: int32` (Protobuf field number 1; repeated=False)<br>`edge_monikers: string` (Protobuf field number 2; repeated=True) |
| `Face` | `id: string` (Protobuf field number 1; repeated=False)<br>`parent: ansys.api.geometry.v0.Body` (Protobuf field number 2; repeated=False)<br>`surface_type: ansys.api.geometry.v0.SurfaceType` (Protobuf field number 10; repeated=False)<br>`owner_name: string` (Protobuf field number 11; repeated=False)<br>`export_id: string` (Protobuf field number 12; repeated=False)<br>`area: double` (Protobuf field number 13; repeated=False)<br>`is_reversed: bool` (Protobuf field number 14; repeated=False)<br>`parent_id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 15; repeated=False) |
| `FindLogoOptions` | `min_height: double` (Protobuf field number 1; repeated=False)<br>`max_height: double` (Protobuf field number 2; repeated=False)<br>`max_fillet_radio_as_sharp: double` (Protobuf field number 3; repeated=False)<br>`fit_error: double` (Protobuf field number 4; repeated=False) |
| `FixInterferenceProblemArea` | `id: int32` (Protobuf field number 1; repeated=False)<br>`body_monikers: string` (Protobuf field number 2; repeated=True) |
| `FixSplitEdgeOptions` | `max_edge_length: double` (Protobuf field number 1; repeated=False)<br>`min_edge_angle: double` (Protobuf field number 2; repeated=False) |
| `Frame` | `origin: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=False)<br>`dir_x: ansys.api.geometry.v0.Direction` (Protobuf field number 2; repeated=False)<br>`dir_y: ansys.api.geometry.v0.Direction` (Protobuf field number 3; repeated=False)<br>`dir_z: ansys.api.geometry.v0.Direction` (Protobuf field number 4; repeated=False) |
| `Gap` | `distance: double` (Protobuf field number 1; repeated=False) |
| `GapProblemArea` | `id: int32` (Protobuf field number 1; repeated=False)<br>`edge_monikers: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `GearCondition` | `condition: ansys.api.geometry.v0.MatingCondition` (Protobuf field number 1; repeated=False)<br>`is_belt: bool` (Protobuf field number 2; repeated=False)<br>`is_reversed: bool` (Protobuf field number 3; repeated=False)<br>`is_valid: bool` (Protobuf field number 4; repeated=False) |
| `GenericProblemArea` | `id: int32` (Protobuf field number 1; repeated=False)<br>`monikers: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `Geometries` | `points: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=True)<br>`lines: ansys.api.geometry.v0.Line` (Protobuf field number 2; repeated=True)<br>`arcs: ansys.api.geometry.v0.Arc` (Protobuf field number 3; repeated=True)<br>`circles: ansys.api.geometry.v0.Circle` (Protobuf field number 4; repeated=True)<br>`ellipses: ansys.api.geometry.v0.Ellipse` (Protobuf field number 5; repeated=True)<br>`polygons: ansys.api.geometry.v0.Polygon` (Protobuf field number 6; repeated=True)<br>`nurbs_curves: ansys.api.geometry.v0.NurbsCurve` (Protobuf field number 7; repeated=True) |
| `InexactEdgeProblemArea` | `id: int32` (Protobuf field number 1; repeated=False)<br>`edge_monikers: string` (Protobuf field number 2; repeated=True) |
| `InspectGeometryOptions` | `level: ansys.api.geometry.v0.InspectGeometryLevel` (Protobuf field number 1; repeated=False)<br>`max_number_of_issues: int32` (Protobuf field number 2; repeated=False)<br>`check_self_intersections: bool` (Protobuf field number 3; repeated=False)<br>`find_g1_discontinuities: bool` (Protobuf field number 4; repeated=False)<br>`sliver_edge_tolerance: double` (Protobuf field number 5; repeated=False)<br>`sliver_face_tolerance: double` (Protobuf field number 6; repeated=False) |
| `InspectGeometryResult` | `body: ansys.api.geometry.v0.Body` (Protobuf field number 1; repeated=False)<br>`issues: ansys.api.geometry.v0.InspectGeometryResultIssue` (Protobuf field number 2; repeated=True) |
| `InspectGeometryResultIssue` | `message_type: ansys.api.geometry.v0.InspectGeometryMessageType` (Protobuf field number 1; repeated=False)<br>`message_id: ansys.api.geometry.v0.InspectGeometryMessageId` (Protobuf field number 2; repeated=False)<br>`faces: ansys.api.geometry.v0.Face` (Protobuf field number 3; repeated=True)<br>`edges: ansys.api.geometry.v0.Edge` (Protobuf field number 4; repeated=True)<br>`message: string` (Protobuf field number 5; repeated=False)<br>`scalar_value: double` (Protobuf field number 6; repeated=False) |
| `Knot` | `multiplicity: int32` (Protobuf field number 1; repeated=False)<br>`parameter: double` (Protobuf field number 2; repeated=False) |
| `Line` | `start: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=False)<br>`end: ansys.api.geometry.v0.Point` (Protobuf field number 2; repeated=False) |
| `Loop` | `type: string` (Protobuf field number 1; repeated=False)<br>`length: double` (Protobuf field number 2; repeated=False)<br>`bounding_box: ansys.api.geometry.v0.Box` (Protobuf field number 3; repeated=False)<br>`edges: string` (Protobuf field number 4; repeated=True) |
| `Material` | `name: string` (Protobuf field number 1; repeated=False)<br>`material_properties: ansys.api.geometry.v0.MaterialProperty` (Protobuf field number 2; repeated=True) |
| `MaterialProperty` | `id: string` (Protobuf field number 1; repeated=False)<br>`display_name: string` (Protobuf field number 2; repeated=False)<br>`value: double` (Protobuf field number 3; repeated=False)<br>`units: string` (Protobuf field number 4; repeated=False) |
| `MatingCondition` | `moniker: string` (Protobuf field number 1; repeated=False)<br>`is_deleted: bool` (Protobuf field number 2; repeated=False)<br>`is_enabled: bool` (Protobuf field number 3; repeated=False)<br>`is_satisfied: bool` (Protobuf field number 4; repeated=False) |
| `Matrix` | `m00: double` (Protobuf field number 1; repeated=False)<br>`m01: double` (Protobuf field number 2; repeated=False)<br>`m02: double` (Protobuf field number 3; repeated=False)<br>`m03: double` (Protobuf field number 4; repeated=False)<br>`m10: double` (Protobuf field number 5; repeated=False)<br>`m11: double` (Protobuf field number 6; repeated=False)<br>`m12: double` (Protobuf field number 7; repeated=False)<br>`m13: double` (Protobuf field number 8; repeated=False)<br>`m20: double` (Protobuf field number 9; repeated=False)<br>`m21: double` (Protobuf field number 10; repeated=False)<br>`m22: double` (Protobuf field number 11; repeated=False)<br>`m23: double` (Protobuf field number 12; repeated=False)<br>`m30: double` (Protobuf field number 13; repeated=False)<br>`m31: double` (Protobuf field number 14; repeated=False)<br>`m32: double` (Protobuf field number 15; repeated=False)<br>`m33: double` (Protobuf field number 16; repeated=False) |
| `Mesh` | `id: string` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False) |
| `MissingFaceProblemArea` | `id: int32` (Protobuf field number 1; repeated=False)<br>`edge_monikers: string` (Protobuf field number 2; repeated=True) |
| `NamedSelection` | `id: string` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 3; repeated=True)<br>`bodies: ansys.api.geometry.v0.Body` (Protobuf field number 4; repeated=True)<br>`faces: ansys.api.geometry.v0.Face` (Protobuf field number 5; repeated=True)<br>`edges: ansys.api.geometry.v0.Edge` (Protobuf field number 6; repeated=True)<br>`beams: ansys.api.geometry.v0.Beam` (Protobuf field number 7; repeated=True)<br>`design_points: ansys.api.geometry.v0.Curve` (Protobuf field number 8; repeated=True)<br>`vertices: ansys.api.geometry.v0.Vertex` (Protobuf field number 9; repeated=True)<br>`components: ansys.api.geometry.v0.Component` (Protobuf field number 10; repeated=True) |
| `NurbsCurve` | `control_points: ansys.api.geometry.v0.ControlPoint` (Protobuf field number 1; repeated=True)<br>`nurbs_data: ansys.api.geometry.v0.NurbsData` (Protobuf field number 2; repeated=False)<br>`is_rational: bool` (Protobuf field number 3; repeated=False)<br>`parameterization: ansys.api.geometry.v0.Parameterization` (Protobuf field number 4; repeated=False) |
| `NurbsData` | `degree: int32` (Protobuf field number 1; repeated=False)<br>`is_closed: bool` (Protobuf field number 2; repeated=False)<br>`is_periodic: bool` (Protobuf field number 3; repeated=False)<br>`knots: ansys.api.geometry.v0.Knot` (Protobuf field number 4; repeated=True)<br>`order: int32` (Protobuf field number 5; repeated=False) |
| `NurbsSurface` | `control_points: ansys.api.geometry.v0.ControlPoint` (Protobuf field number 1; repeated=True)<br>`nurbs_data_u: ansys.api.geometry.v0.NurbsData` (Protobuf field number 2; repeated=False)<br>`nurbs_data_v: ansys.api.geometry.v0.NurbsData` (Protobuf field number 3; repeated=False)<br>`is_rational: bool` (Protobuf field number 4; repeated=False)<br>`parameterization_u: ansys.api.geometry.v0.Parameterization` (Protobuf field number 5; repeated=False)<br>`parameterization_v: ansys.api.geometry.v0.Parameterization` (Protobuf field number 6; repeated=False) |
| `OrientCondition` | `condition: ansys.api.geometry.v0.MatingCondition` (Protobuf field number 1; repeated=False)<br>`offset: double` (Protobuf field number 2; repeated=False)<br>`is_reversed: bool` (Protobuf field number 3; repeated=False)<br>`is_valid: bool` (Protobuf field number 4; repeated=False) |
| `Parameterization` | `bounds: ansys.api.geometry.v0.ParameterizationBounds` (Protobuf field number 1; repeated=False)<br>`form: ansys.api.geometry.v0.ParameterizationForm` (Protobuf field number 2; repeated=False) |
| `ParameterizationBounds` | `infinite_start: bool` (Protobuf field number 1; repeated=False)<br>`start: double` (Protobuf field number 2; repeated=False)<br>`infinite_end: bool` (Protobuf field number 3; repeated=False)<br>`end: double` (Protobuf field number 4; repeated=False) |
| `Part` | `id: string` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False) |
| `Plane` | `frame: ansys.api.geometry.v0.Frame` (Protobuf field number 1; repeated=False) |
| `Point` | `x: double` (Protobuf field number 1; repeated=False)<br>`y: double` (Protobuf field number 2; repeated=False)<br>`z: double` (Protobuf field number 3; repeated=False) |
| `Polygon` | `center: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=False)<br>`radius: double` (Protobuf field number 2; repeated=False)<br>`numberofsides: int32` (Protobuf field number 3; repeated=False)<br>`angle: double` (Protobuf field number 4; repeated=False) |
| `RayFireFaceImpact` | `face: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`point: ansys.api.geometry.v0.Point` (Protobuf field number 2; repeated=False) |
| `RayFireFaceImpacts` | `impacts: ansys.api.geometry.v0.RayFireFaceImpact` (Protobuf field number 1; repeated=True) |
| `RayFireImpact` | `body: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`point: ansys.api.geometry.v0.Point` (Protobuf field number 2; repeated=False) |
| `RayFireImpacts` | `impacts: ansys.api.geometry.v0.RayFireImpact` (Protobuf field number 1; repeated=True) |
| `RayFireUVImpact` | `body: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`point: ansys.api.geometry.v0.Point` (Protobuf field number 2; repeated=False)<br>`u: double` (Protobuf field number 3; repeated=False)<br>`v: double` (Protobuf field number 4; repeated=False) |
| `RayFireUVImpacts` | `impacts: ansys.api.geometry.v0.RayFireUVImpact` (Protobuf field number 1; repeated=True) |
| `RepairToolMessage` | `success: bool` (Protobuf field number 1; repeated=False)<br>`created_bodies_monikers: string` (Protobuf field number 2; repeated=True)<br>`modified_bodies_monikers: string` (Protobuf field number 3; repeated=True)<br>`deleted_bodies_monikers: string` (Protobuf field number 4; repeated=True)<br>`complete_command_response: ansys.api.geometry.v0.TrackerCommandResponse` (Protobuf field number 5; repeated=False) |
| `RigidCondition` | `condition: ansys.api.geometry.v0.MatingCondition` (Protobuf field number 1; repeated=False)<br>`component_a: ansys.api.geometry.v0.Component` (Protobuf field number 2; repeated=False)<br>`component_b: ansys.api.geometry.v0.Component` (Protobuf field number 3; repeated=False) |
| `Separation` | `distance: double` (Protobuf field number 1; repeated=False)<br>`point_a: ansys.api.geometry.v0.Point` (Protobuf field number 2; repeated=False)<br>`point_b: ansys.api.geometry.v0.Point` (Protobuf field number 3; repeated=False) |
| `SetObjectNameRequest` | `id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False) |
| `Shape` | `is_surface_body: bool` (Protobuf field number 1; repeated=False)<br>`surface_area: double` (Protobuf field number 2; repeated=False)<br>`volume: double` (Protobuf field number 3; repeated=False)<br>`bounding_box_size: ansys.api.geometry.v0.Direction` (Protobuf field number 4; repeated=False) |
| `ShortEdgeProblemArea` | `id: int32` (Protobuf field number 1; repeated=False)<br>`edge_monikers: string` (Protobuf field number 2; repeated=True) |
| `ShrinkWrapOptions` | `size: double` (Protobuf field number 2; repeated=False)<br>`keep_original_bodies: bool` (Protobuf field number 3; repeated=False)<br>`preserve_features: bool` (Protobuf field number 4; repeated=False)<br>`angle_tolerance: double` (Protobuf field number 5; repeated=False)<br>`secondary_size_enabled: bool` (Protobuf field number 6; repeated=False)<br>`secondary_size: double` (Protobuf field number 7; repeated=False)<br>`max_size_enabled: bool` (Protobuf field number 8; repeated=False)<br>`max_size: double` (Protobuf field number 9; repeated=False)<br>`curvature_angle: double` (Protobuf field number 10; repeated=False) |
| `SmallCurveProblemArea` | `id: int32` (Protobuf field number 1; repeated=False)<br>`curve_monikers: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `SmallFaceProblemArea` | `id: int32` (Protobuf field number 1; repeated=False)<br>`face_monikers: string` (Protobuf field number 2; repeated=True) |
| `SplitEdgeProblemArea` | `id: int32` (Protobuf field number 1; repeated=False)<br>`edge_monikers: string` (Protobuf field number 2; repeated=True) |
| `SpotWeld` | `weld_points: ansys.api.geometry.v0.SpotWeld.WeldPointsEntry` (Protobuf field number 1; repeated=True) |
| `StitchFaceProblemArea` | `id: int32` (Protobuf field number 1; repeated=False)<br>`body_monikers: string` (Protobuf field number 2; repeated=True) |
| `Surface` | `origin: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=False)<br>`radius: double` (Protobuf field number 2; repeated=False)<br>`half_angle: double` (Protobuf field number 3; repeated=False)<br>`major_radius: double` (Protobuf field number 4; repeated=False)<br>`minor_radius: double` (Protobuf field number 5; repeated=False)<br>`reference: ansys.api.geometry.v0.Direction` (Protobuf field number 6; repeated=False)<br>`axis: ansys.api.geometry.v0.Direction` (Protobuf field number 7; repeated=False)<br>`nurbs_surface: ansys.api.geometry.v0.NurbsSurface` (Protobuf field number 8; repeated=False) |
| `SurfaceEvaluation` | `derivative_u: ansys.api.geometry.v0.Direction` (Protobuf field number 1; repeated=False)<br>`derivative_uu: ansys.api.geometry.v0.Direction` (Protobuf field number 2; repeated=False)<br>`derivative_uv: ansys.api.geometry.v0.Direction` (Protobuf field number 3; repeated=False)<br>`derivative_v: ansys.api.geometry.v0.Direction` (Protobuf field number 4; repeated=False)<br>`derivative_vv: ansys.api.geometry.v0.Direction` (Protobuf field number 5; repeated=False)<br>`max_curvature: double` (Protobuf field number 6; repeated=False)<br>`max_curvature_direction: ansys.api.geometry.v0.Direction` (Protobuf field number 7; repeated=False)<br>`min_curvature: double` (Protobuf field number 8; repeated=False)<br>`min_curvature_direction: ansys.api.geometry.v0.Direction` (Protobuf field number 9; repeated=False)<br>`normal: ansys.api.geometry.v0.Direction` (Protobuf field number 10; repeated=False)<br>`param_u: double` (Protobuf field number 11; repeated=False)<br>`param_v: double` (Protobuf field number 12; repeated=False)<br>`point: ansys.api.geometry.v0.Point` (Protobuf field number 13; repeated=False) |
| `TangentCondition` | `condition: ansys.api.geometry.v0.MatingCondition` (Protobuf field number 1; repeated=False)<br>`offset: double` (Protobuf field number 2; repeated=False)<br>`is_reversed: bool` (Protobuf field number 3; repeated=False)<br>`is_valid: bool` (Protobuf field number 4; repeated=False) |
| `Tessellation` | `vertices: double` (Protobuf field number 1; repeated=True)<br>`faces: int32` (Protobuf field number 2; repeated=True)<br>`facecolor: int32` (Protobuf field number 3; repeated=False) |
| `TessellationOptions` | `surface_deviation: double` (Protobuf field number 1; repeated=False)<br>`angle_deviation: double` (Protobuf field number 2; repeated=False)<br>`maximum_aspect_ratio: double` (Protobuf field number 3; repeated=False)<br>`maximum_edge_length: double` (Protobuf field number 4; repeated=False)<br>`watertight: bool` (Protobuf field number 5; repeated=False)<br>`curve_deviation: double` (Protobuf field number 6; repeated=False) |
| `TrackerCommandResponse` | `success: bool` (Protobuf field number 1; repeated=False)<br>`created_bodies: ansys.api.geometry.v0.Body` (Protobuf field number 2; repeated=True)<br>`modified_bodies: ansys.api.geometry.v0.Body` (Protobuf field number 3; repeated=True)<br>`deleted_bodies: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 4; repeated=True)<br>`created_faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 5; repeated=True)<br>`modified_faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 6; repeated=True)<br>`deleted_faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 7; repeated=True)<br>`created_edges: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 8; repeated=True)<br>`modified_edges: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 9; repeated=True)<br>`deleted_edges: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 10; repeated=True)<br>`created_components: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 11; repeated=True)<br>`modified_components: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 12; repeated=True)<br>`deleted_components: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 13; repeated=True)<br>`created_parts: ansys.api.geometry.v0.Part` (Protobuf field number 14; repeated=True)<br>`modified_parts: ansys.api.geometry.v0.Part` (Protobuf field number 15; repeated=True)<br>`deleted_parts: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 16; repeated=True) |
| `TrackerDefinition` | `design_id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `TrimmedCurve` | `curve: ansys.api.geometry.v0.CurveGeometry` (Protobuf field number 1; repeated=False)<br>`start: ansys.api.geometry.v0.Point` (Protobuf field number 2; repeated=False)<br>`end: ansys.api.geometry.v0.Point` (Protobuf field number 3; repeated=False)<br>`interval_start: double` (Protobuf field number 4; repeated=False)<br>`interval_end: double` (Protobuf field number 5; repeated=False)<br>`length: double` (Protobuf field number 6; repeated=False) |
| `TrimmedCurveList` | `curves: ansys.api.geometry.v0.TrimmedCurve` (Protobuf field number 1; repeated=True) |
| `TrimmedSurface` | `surface: ansys.api.geometry.v0.Surface` (Protobuf field number 1; repeated=False)<br>`type: ansys.api.geometry.v0.SurfaceType` (Protobuf field number 2; repeated=False)<br>`u_min: double` (Protobuf field number 3; repeated=False)<br>`u_max: double` (Protobuf field number 4; repeated=False)<br>`v_min: double` (Protobuf field number 5; repeated=False)<br>`v_max: double` (Protobuf field number 6; repeated=False) |
| `UpdateState` | `state: int32` (Protobuf field number 1; repeated=False) |
| `Vertex` | `position: ansys.api.geometry.v0.Point` (Protobuf field number 1; repeated=False)<br>`edges: ansys.api.geometry.v0.Edge` (Protobuf field number 2; repeated=True)<br>`id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 3; repeated=False) |
| `Weld` | `geometry: ansys.api.geometry.v0.TrimmedCurveList` (Protobuf field number 1; repeated=True)<br>`display_name: string` (Protobuf field number 2; repeated=False)<br>`length: double` (Protobuf field number 3; repeated=False)<br>`volume: double` (Protobuf field number 4; repeated=False)<br>`mass: double` (Protobuf field number 5; repeated=False)<br>`time: double` (Protobuf field number 6; repeated=False)<br>`rod_length: double` (Protobuf field number 7; repeated=False)<br>`is_intermittent: bool` (Protobuf field number 8; repeated=False)<br>`sequence_id: int32` (Protobuf field number 9; repeated=False)<br>`size1: double` (Protobuf field number 10; repeated=False)<br>`size2: double` (Protobuf field number 11; repeated=False)<br>`is_angular: bool` (Protobuf field number 12; repeated=False)<br>`is_at_center: bool` (Protobuf field number 13; repeated=False)<br>`intermittent_length: double` (Protobuf field number 14; repeated=False)<br>`number_of_welds: int32` (Protobuf field number 15; repeated=False)<br>`pitch: double` (Protobuf field number 16; repeated=False) |

### `ansys.api.geometry.v0.namedselections_pb2`

| Message | Fields |
| --- | --- |
| `CreateRequest` | `name: string` (Protobuf field number 1; repeated=False)<br>`members: string` (Protobuf field number 2; repeated=True)<br>`parent: string` (Protobuf field number 3; repeated=False) |
| `DeleteByNameRequest` | `name: string` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `named_selections: ansys.api.geometry.v0.NamedSelection` (Protobuf field number 1; repeated=True) |
| `SetNameRequest` | `id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`new_name: string` (Protobuf field number 2; repeated=False) |
| `SetNameResponse` | — |

### `ansys.api.geometry.v0.parts_pb2`

| Message | Fields |
| --- | --- |
| `ExportRequest` | `id: string` (Protobuf field number 1; repeated=False)<br>`format: ansys.api.dbu.v0.PartExportFormat` (Protobuf field number 2; repeated=False) |
| `ExportResponse` | `data: bytes` (Protobuf field number 1; repeated=False) |
| `GetAllRequest` | `parent: string` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `parts: ansys.api.geometry.v0.Part` (Protobuf field number 1; repeated=True) |
| `GetBeamsRequest` | `part: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `GetBeamsResponse` | `beams: ansys.api.geometry.v0.Beam` (Protobuf field number 1; repeated=True) |

### `ansys.api.geometry.v0.preparetools_pb2`

| Message | Fields |
| --- | --- |
| `CreateEnclosureBoxRequest` | `bodies: ansys.api.geometry.v0.Body` (Protobuf field number 1; repeated=True)<br>`x_low: double` (Protobuf field number 2; repeated=False)<br>`x_high: double` (Protobuf field number 3; repeated=False)<br>`y_low: double` (Protobuf field number 4; repeated=False)<br>`y_high: double` (Protobuf field number 5; repeated=False)<br>`z_low: double` (Protobuf field number 6; repeated=False)<br>`z_high: double` (Protobuf field number 7; repeated=False)<br>`enclosure_options: ansys.api.geometry.v0.preparetools.EnclosureOptions` (Protobuf field number 8; repeated=False) |
| `CreateEnclosureCylinderRequest` | `bodies: ansys.api.geometry.v0.Body` (Protobuf field number 1; repeated=True)<br>`axial_distance_low: double` (Protobuf field number 2; repeated=False)<br>`axial_distance_high: double` (Protobuf field number 3; repeated=False)<br>`radial_distance: double` (Protobuf field number 4; repeated=False)<br>`enclosure_options: ansys.api.geometry.v0.preparetools.EnclosureOptions` (Protobuf field number 5; repeated=False) |
| `CreateEnclosureResponse` | `success: bool` (Protobuf field number 1; repeated=False)<br>`created_bodies: ansys.api.geometry.v0.Body` (Protobuf field number 2; repeated=True)<br>`command_response: ansys.api.geometry.v0.TrackerCommandResponse` (Protobuf field number 3; repeated=False) |
| `CreateEnclosureSphereRequest` | `bodies: ansys.api.geometry.v0.Body` (Protobuf field number 1; repeated=True)<br>`radial_distance: double` (Protobuf field number 2; repeated=False)<br>`enclosure_options: ansys.api.geometry.v0.preparetools.EnclosureOptions` (Protobuf field number 3; repeated=False) |
| `DetectHelixesRequest` | `body_ids: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`options: ansys.api.geometry.v0.DetectHelixesOptions` (Protobuf field number 2; repeated=False) |
| `DetectHelixesResponse` | `helixes: ansys.api.geometry.v0.preparetools.DetectHelixesResponseData` (Protobuf field number 1; repeated=True) |
| `DetectHelixesResponseData` | `trimmed_curve: ansys.api.geometry.v0.TrimmedCurve` (Protobuf field number 1; repeated=False)<br>`edges: ansys.api.geometry.v0.Edge` (Protobuf field number 2; repeated=True) |
| `DetectSweepableBodiesRequest` | `bodies: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`get_source_target_faces: bool` (Protobuf field number 2; repeated=False) |
| `DetectSweepableBodiesResponse` | `response_data: ansys.api.geometry.v0.preparetools.DetectSweepableBodiesResponseData` (Protobuf field number 1; repeated=True) |
| `DetectSweepableBodiesResponseData` | `result: bool` (Protobuf field number 1; repeated=False)<br>`face_ids: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `EnclosureOptions` | `create_shared_topology: bool` (Protobuf field number 1; repeated=False)<br>`subtract_bodies: bool` (Protobuf field number 2; repeated=False)<br>`frame: ansys.api.geometry.v0.Frame` (Protobuf field number 3; repeated=False)<br>`cushion_proportion: double` (Protobuf field number 4; repeated=False) |
| `ExtractVolumeFromEdgeLoopsRequest` | `sealing_edges: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`inside_faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `ExtractVolumeFromFacesRequest` | `sealing_faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`inside_faces: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `FindLogosRequest` | `bodies: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`options: ansys.api.geometry.v0.FindLogoOptions` (Protobuf field number 2; repeated=False) |
| `FindLogosResponse` | `id: string` (Protobuf field number 1; repeated=False)<br>`logo_faces: ansys.api.geometry.v0.Face` (Protobuf field number 2; repeated=True) |
| `FixInterferenceRequest` | `selection: ansys.api.geometry.v0.Body` (Protobuf field number 1; repeated=True)<br>`cut_smaller_body: google.protobuf.BoolValue` (Protobuf field number 2; repeated=False) |
| `FixInterferenceResponse` | `result: bool` (Protobuf field number 1; repeated=False)<br>`changes: ansys.api.geometry.v0.TrackerCommandResponse` (Protobuf field number 2; repeated=False) |
| `FixShortEdgesRequest` | `selection: ansys.api.geometry.v0.Edge` (Protobuf field number 1; repeated=True)<br>`max_edge_length: google.protobuf.DoubleValue` (Protobuf field number 2; repeated=False) |
| `FixShortEdgesResponse` | `result: bool` (Protobuf field number 1; repeated=False)<br>`changes: ansys.api.geometry.v0.TrackerCommandResponse` (Protobuf field number 2; repeated=False) |
| `RemoveFacesRequest` | `selection: ansys.api.geometry.v0.Face` (Protobuf field number 1; repeated=True) |
| `RemoveFacesResponse` | `result: bool` (Protobuf field number 1; repeated=False)<br>`changes: ansys.api.geometry.v0.TrackerCommandResponse` (Protobuf field number 2; repeated=False) |
| `RemoveLogoRequest` | `face_ids: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `RemoveLogoResponse` | `success: bool` (Protobuf field number 1; repeated=False) |
| `RemoveRoundsRequest` | `selection: ansys.api.geometry.v0.Face` (Protobuf field number 1; repeated=True)<br>`auto_shrink: google.protobuf.BoolValue` (Protobuf field number 2; repeated=False) |
| `RemoveRoundsResponse` | `result: bool` (Protobuf field number 1; repeated=False)<br>`changes: ansys.api.geometry.v0.TrackerCommandResponse` (Protobuf field number 2; repeated=False) |
| `ShareTopologyRequest` | `selection: ansys.api.geometry.v0.Body` (Protobuf field number 1; repeated=True)<br>`tolerance: google.protobuf.DoubleValue` (Protobuf field number 2; repeated=False)<br>`preserve_instances: google.protobuf.BoolValue` (Protobuf field number 3; repeated=False) |
| `ShareTopologyResponse` | `result: bool` (Protobuf field number 1; repeated=False) |
| `UnshareTopologyRequest` | `include_groups: google.protobuf.BoolValue` (Protobuf field number 1; repeated=False)<br>`unshare_lower_topology: google.protobuf.BoolValue` (Protobuf field number 2; repeated=False) |
| `UnshareTopologyResponse` | `result: bool` (Protobuf field number 1; repeated=False) |
| `VolumeExtractionResponse` | `success: bool` (Protobuf field number 1; repeated=False)<br>`created_bodies: ansys.api.geometry.v0.Body` (Protobuf field number 2; repeated=True)<br>`changes: ansys.api.geometry.v0.TrackerCommandResponse` (Protobuf field number 3; repeated=False) |

### `ansys.api.geometry.v0.repairtools_pb2`

| Message | Fields |
| --- | --- |
| `AdjustMergeFacesRequest` | `selection: ansys.api.geometry.v0.Face` (Protobuf field number 1; repeated=True)<br>`tangent_faces: ansys.api.geometry.v0.Face` (Protobuf field number 2; repeated=True)<br>`allow_multi_patch: google.protobuf.BoolValue` (Protobuf field number 3; repeated=False)<br>`fail_if_can_fill: google.protobuf.BoolValue` (Protobuf field number 4; repeated=False)<br>`enforce_closed_loop_check: google.protobuf.BoolValue` (Protobuf field number 5; repeated=False) |
| `AdjustMergeFacesResponse` | `result: bool` (Protobuf field number 1; repeated=False) |
| `FindAdjustMergeFacesRequest` | `selection: ansys.api.geometry.v0.Face` (Protobuf field number 1; repeated=True)<br>`tangent_faces: ansys.api.geometry.v0.Face` (Protobuf field number 2; repeated=True)<br>`allow_multi_patch: google.protobuf.BoolValue` (Protobuf field number 3; repeated=False)<br>`fail_if_can_fill: google.protobuf.BoolValue` (Protobuf field number 4; repeated=False)<br>`enforce_closed_loop_check: google.protobuf.BoolValue` (Protobuf field number 5; repeated=False) |
| `FindAdjustMergeFacesResponse` | `result: ansys.api.geometry.v0.SplitEdgeProblemArea` (Protobuf field number 1; repeated=True) |
| `FindAdjustSimplifyRequest` | `selection: string` (Protobuf field number 1; repeated=True)<br>`comprehensive: bool` (Protobuf field number 2; repeated=False) |
| `FindAdjustSimplifyResponse` | `result: ansys.api.geometry.v0.AdjustSimplifyProblemArea` (Protobuf field number 1; repeated=True) |
| `FindCurveGapsRequest` | `distance: google.protobuf.DoubleValue` (Protobuf field number 1; repeated=False) |
| `FindCurveGapsResponse` | `result: ansys.api.geometry.v0.CurveGapProblemArea` (Protobuf field number 1; repeated=True) |
| `FindDuplicateCurvesResponse` | `result: ansys.api.geometry.v0.DuplicateCurveProblemArea` (Protobuf field number 1; repeated=True) |
| `FindDuplicateFacesRequest` | `faces: string` (Protobuf field number 1; repeated=True)<br>`max_gap: google.protobuf.DoubleValue` (Protobuf field number 2; repeated=False) |
| `FindDuplicateFacesResponse` | `result: ansys.api.geometry.v0.DuplicateFaceProblemArea` (Protobuf field number 1; repeated=True) |
| `FindExtraEdgesRequest` | `selection: string` (Protobuf field number 1; repeated=True)<br>`comprehensive: bool` (Protobuf field number 2; repeated=False) |
| `FindExtraEdgesResponse` | `result: ansys.api.geometry.v0.ExtraEdgeProblemArea` (Protobuf field number 1; repeated=True) |
| `FindGapsRequest` | `bodies: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`angle: google.protobuf.DoubleValue` (Protobuf field number 2; repeated=False)<br>`distance: google.protobuf.DoubleValue` (Protobuf field number 3; repeated=False)<br>`fix_method: ansys.api.geometry.v0.repairtools.SolidifyFixMethodType` (Protobuf field number 4; repeated=False)<br>`allow_multi_patch: google.protobuf.BoolValue` (Protobuf field number 5; repeated=False) |
| `FindGapsResponse` | `result: ansys.api.geometry.v0.GapProblemArea` (Protobuf field number 1; repeated=True) |
| `FindInexactEdgesRequest` | `selection: string` (Protobuf field number 1; repeated=True) |
| `FindInexactEdgesResponse` | `result: ansys.api.geometry.v0.InexactEdgeProblemArea` (Protobuf field number 1; repeated=True) |
| `FindInterferenceRequest` | `bodies: string` (Protobuf field number 1; repeated=True)<br>`cut_smaller_body: google.protobuf.BoolValue` (Protobuf field number 2; repeated=False) |
| `FindInterferenceResponse` | `result: ansys.api.geometry.v0.FixInterferenceProblemArea` (Protobuf field number 1; repeated=True) |
| `FindMissingFacesRequest` | `faces: string` (Protobuf field number 1; repeated=True)<br>`angle: google.protobuf.DoubleValue` (Protobuf field number 2; repeated=False)<br>`distance: google.protobuf.DoubleValue` (Protobuf field number 3; repeated=False)<br>`null: google.protobuf.NullValue` (Protobuf field number 4; repeated=False)<br>`data: ansys.api.geometry.v0.repairtools.SolidifyFixMethodType` (Protobuf field number 5; repeated=False)<br>`allow_multi_patch: google.protobuf.BoolValue` (Protobuf field number 6; repeated=False) |
| `FindMissingFacesResponse` | `result: ansys.api.geometry.v0.MissingFaceProblemArea` (Protobuf field number 1; repeated=True) |
| `FindShortEdgesRequest` | `selection: string` (Protobuf field number 1; repeated=True)<br>`max_edge_length: google.protobuf.DoubleValue` (Protobuf field number 2; repeated=False)<br>`comprehensive: bool` (Protobuf field number 3; repeated=False) |
| `FindShortEdgesResponse` | `result: ansys.api.geometry.v0.ShortEdgeProblemArea` (Protobuf field number 1; repeated=True) |
| `FindSmallCurvesRequest` | `bodies: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`max_curve_length: google.protobuf.DoubleValue` (Protobuf field number 2; repeated=False) |
| `FindSmallCurvesResponse` | `result: ansys.api.geometry.v0.SmallCurveProblemArea` (Protobuf field number 1; repeated=True) |
| `FindSmallFacesRequest` | `selection: string` (Protobuf field number 1; repeated=True)<br>`area: google.protobuf.DoubleValue` (Protobuf field number 2; repeated=False)<br>`width: google.protobuf.DoubleValue` (Protobuf field number 3; repeated=False) |
| `FindSmallFacesResponse` | `result: ansys.api.geometry.v0.SmallFaceProblemArea` (Protobuf field number 1; repeated=True) |
| `FindSplitEdgesRequest` | `bodies_or_faces: string` (Protobuf field number 1; repeated=True)<br>`angle: google.protobuf.DoubleValue` (Protobuf field number 2; repeated=False)<br>`distance: google.protobuf.DoubleValue` (Protobuf field number 3; repeated=False)<br>`comprehensive: bool` (Protobuf field number 4; repeated=False) |
| `FindSplitEdgesResponse` | `result: ansys.api.geometry.v0.SplitEdgeProblemArea` (Protobuf field number 1; repeated=True) |
| `FindStitchFacesRequest` | `faces: string` (Protobuf field number 1; repeated=True)<br>`maximum_distance: google.protobuf.DoubleValue` (Protobuf field number 2; repeated=False)<br>`check_for_coincidence: google.protobuf.BoolValue` (Protobuf field number 3; repeated=False)<br>`allow_multiple_bodies: google.protobuf.BoolValue` (Protobuf field number 4; repeated=False)<br>`maintain_components: google.protobuf.BoolValue` (Protobuf field number 5; repeated=False)<br>`comprehensive: bool` (Protobuf field number 6; repeated=False) |
| `FindStitchFacesResponse` | `result: ansys.api.geometry.v0.StitchFaceProblemArea` (Protobuf field number 1; repeated=True) |
| `FitCurvesRequest` | `selection: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`arcs: bool` (Protobuf field number 2; repeated=False)<br>`lines: bool` (Protobuf field number 3; repeated=False)<br>`splines: bool` (Protobuf field number 4; repeated=False)<br>`tangentize: bool` (Protobuf field number 5; repeated=False)<br>`tolerance: double` (Protobuf field number 6; repeated=False) |
| `FitCurvesResponse` | `result: ansys.api.geometry.v0.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixAdjustSimplifyRequest` | `adjust_simplify_problem_area_id: google.protobuf.Int32Value` (Protobuf field number 1; repeated=False) |
| `FixAdjustSimplifyResponse` | `result: ansys.api.geometry.v0.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixCurveGapsRequest` | `curve_gap_problem_area_id: google.protobuf.Int32Value` (Protobuf field number 1; repeated=False)<br>`distance: google.protobuf.DoubleValue` (Protobuf field number 2; repeated=False) |
| `FixCurveGapsResponse` | `result: ansys.api.geometry.v0.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixDuplicateCurvesRequest` | `duplicate_curve_problem_area_id: google.protobuf.Int32Value` (Protobuf field number 1; repeated=False) |
| `FixDuplicateCurvesResponse` | `result: ansys.api.geometry.v0.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixDuplicateFacesRequest` | `duplicate_face_problem_area_id: google.protobuf.Int32Value` (Protobuf field number 1; repeated=False) |
| `FixDuplicateFacesResponse` | `result: ansys.api.geometry.v0.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixExtraEdgesRequest` | `extra_edge_problem_area_id: google.protobuf.Int32Value` (Protobuf field number 1; repeated=False) |
| `FixExtraEdgesResponse` | `result: ansys.api.geometry.v0.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixGapsRequest` | `gap_problem_area_id: google.protobuf.Int32Value` (Protobuf field number 1; repeated=False) |
| `FixGapsResponse` | `result: ansys.api.geometry.v0.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixInexactEdgesRequest` | `inexact_edge_problem_area_id: google.protobuf.Int32Value` (Protobuf field number 1; repeated=False) |
| `FixInexactEdgesResponse` | `result: ansys.api.geometry.v0.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixInterferenceRequest` | `interference_problem_area_id: google.protobuf.Int32Value` (Protobuf field number 1; repeated=False) |
| `FixInterferenceResponse` | `result: ansys.api.geometry.v0.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixMissingFacesRequest` | `missing_face_problem_area_id: google.protobuf.Int32Value` (Protobuf field number 1; repeated=False) |
| `FixMissingFacesResponse` | `result: ansys.api.geometry.v0.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixShortEdgesRequest` | `short_edge_problem_area_id: google.protobuf.Int32Value` (Protobuf field number 1; repeated=False) |
| `FixShortEdgesResponse` | `result: ansys.api.geometry.v0.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixSmallCurvesRequest` | `small_curve_problem_area_id: google.protobuf.Int32Value` (Protobuf field number 1; repeated=False) |
| `FixSmallCurvesResponse` | `result: ansys.api.geometry.v0.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixSmallFacesRequest` | `small_face_problem_area_id: google.protobuf.Int32Value` (Protobuf field number 1; repeated=False) |
| `FixSmallFacesResponse` | `result: ansys.api.geometry.v0.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixSplitEdgesRequest` | `split_edge_problem_area_id: google.protobuf.Int32Value` (Protobuf field number 1; repeated=False) |
| `FixSplitEdgesResponse` | `result: ansys.api.geometry.v0.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixStitchFacesRequest` | `stitch_face_problem_area_id: google.protobuf.Int32Value` (Protobuf field number 1; repeated=False) |
| `FixStitchFacesResponse` | `result: ansys.api.geometry.v0.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `InspectGeometryRequest` | `bodies: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`options: ansys.api.geometry.v0.InspectGeometryOptions` (Protobuf field number 2; repeated=False) |
| `InspectGeometryResponse` | `issues_by_body: ansys.api.geometry.v0.InspectGeometryResult` (Protobuf field number 1; repeated=True) |
| `RepairGeometryRequest` | `bodies: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `RepairGeometryResponse` | `result: ansys.api.geometry.v0.RepairToolMessage` (Protobuf field number 1; repeated=False) |

### `ansys.api.geometry.v0.unsupported_pb2`

| Message | Fields |
| --- | --- |
| `CreateFacetedBodiesRequest` | `tessellation_data: ansys.api.geometry.v0.unsupported.CreateFacetedBodiesRequest.TessellationDataEntry` (Protobuf field number 1; repeated=True) |
| `CreateFacetedBodiesResponse` | `created_bodies: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `ExportIdRequest` | `moniker: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`id: string` (Protobuf field number 2; repeated=False)<br>`type: ansys.api.dbu.v0.PersistentIdType` (Protobuf field number 3; repeated=False) |
| `GetFacetedBodiesRequest` | `parts_ids: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `GetFacetedBodiesResponse` | `faceted_bodies: ansys.api.geometry.v0.unsupported.GetFacetedBodiesResponse.FacetedBodiesEntry` (Protobuf field number 1; repeated=True) |
| `ImportIdRequest` | `type: ansys.api.dbu.v0.PersistentIdType` (Protobuf field number 1; repeated=False) |
| `ImportIdResponse` | `id_map: ansys.api.geometry.v0.unsupported.ImportIdResponse.IdMapEntry` (Protobuf field number 1; repeated=True) |
| `SetExportIdsRequest` | `export_data: ansys.api.geometry.v0.unsupported.ExportIdRequest` (Protobuf field number 1; repeated=True) |
| `SoundEnabledRequest` | `enabled: bool` (Protobuf field number 1; repeated=False) |

## Snapshot counts

- RPC methods: 298
- Protocol messages: 491
- Message fields: 1272
