# mapdl_protocol protocol dictionary

- APIKB source key: `mapdl_protocol`
- Package: `ansys-api-mapdl 0.6.0`
- Interface: mapdl gRPC protocol schema
- Snapshot: [`mapdl_protocol_api.json`](../../mapdl_protocol_api.json)
- Snapshot SHA-256: `09f2a79a4ab77cf986073cf43da541a5159a92aa7574fc97f85ffc0d26a0dd12`

> This page describes the captured protobuf schema. It does not confirm product support, host compatibility, or runtime behavior.
> This snapshot records enum type names on fields. It does not list enum members.

## Services and RPC methods

### `ansys.api.mapdl.v0.C_StreamGrpc_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `C_StreamGrpcService` | `Open` | `(ansys.api.grpcstream.v0.OpenRequest) -> ansys.api.grpcstream.v0.OpenResponse [client_streaming=False, server_streaming=False]` |
| `C_StreamGrpcService` | `Close` | `(ansys.api.grpcstream.v0.CloseRequest) -> ansys.api.grpcstream.v0.CloseResponse [client_streaming=False, server_streaming=False]` |
| `C_StreamGrpcService` | `Seek` | `(ansys.api.grpcstream.v0.SeekRequest) -> ansys.api.grpcstream.v0.SeekResponse [client_streaming=False, server_streaming=False]` |
| `C_StreamGrpcService` | `Tell` | `(ansys.api.grpcstream.v0.TellRequest) -> ansys.api.grpcstream.v0.TellResponse [client_streaming=False, server_streaming=False]` |
| `C_StreamGrpcService` | `Read` | `(ansys.api.grpcstream.v0.ReadRequest) -> ansys.api.kernel.v0.Chunk [client_streaming=False, server_streaming=True]` |
| `C_StreamGrpcService` | `Write` | `(ansys.api.kernel.v0.Chunk) -> ansys.api.grpcstream.v0.WriteResponse [client_streaming=True, server_streaming=False]` |

### `ansys.api.mapdl.v0.mapdl_db_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `MapdlDbService` | `NodNext` | `(ansys.api.mapdl_db.v0.NodRequest) -> ansys.api.mapdl_db.v0.NodResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `NodPrev` | `(ansys.api.mapdl_db.v0.NodRequest) -> ansys.api.mapdl_db.v0.NodResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `NodNextDefined` | `(ansys.api.mapdl_db.v0.NodRequest) -> ansys.api.mapdl_db.v0.NodResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `NodSel` | `(ansys.api.mapdl_db.v0.NodSelRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `ElmNext` | `(ansys.api.mapdl_db.v0.ElmRequest) -> ansys.api.mapdl_db.v0.ElmResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `ElmPrev` | `(ansys.api.mapdl_db.v0.ElmRequest) -> ansys.api.mapdl_db.v0.ElmResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `ElmNextDefined` | `(ansys.api.mapdl_db.v0.ElmRequest) -> ansys.api.mapdl_db.v0.ElmResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `ElmSel` | `(ansys.api.mapdl_db.v0.ElmSelRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `NodInqr` | `(ansys.api.mapdl_db.v0.NodInqrRequest) -> ansys.api.mapdl_db.v0.NodInqrResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `getNod` | `(ansys.api.mapdl_db.v0.getnodRequest) -> ansys.api.mapdl_db.v0.getnodResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `putNod` | `(ansys.api.mapdl_db.v0.putnodRequest) -> ansys.api.kernel.v0.EmptyResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `getAllNod` | `(ansys.api.kernel.v0.EmptyRequest) -> ansys.api.mapdl_db.v0.getnodResponse [client_streaming=False, server_streaming=True]` |
| `MapdlDbService` | `getAllNodC` | `(ansys.api.kernel.v0.EmptyRequest) -> ansys.api.kernel.v0.Chunk [client_streaming=False, server_streaming=True]` |
| `MapdlDbService` | `putAllNod` | `(ansys.api.mapdl_db.v0.putnodRequest) -> ansys.api.kernel.v0.EmptyResponse [client_streaming=True, server_streaming=False]` |
| `MapdlDbService` | `NodGall` | `(ansys.api.mapdl_db.v0.NodGallRequest) -> ansys.api.mapdl_db.v0.NodGallResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `NodSpgt` | `(ansys.api.mapdl_db.v0.NodSpgtRequest) -> ansys.api.mapdl_db.v0.NodSpgtResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `ElmIqr` | `(ansys.api.mapdl_db.v0.ElmIqrRequest) -> ansys.api.mapdl_db.v0.ElmIqrResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `getElm` | `(ansys.api.mapdl_db.v0.getelmRequest) -> ansys.api.mapdl_db.v0.getelmResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `putElm` | `(ansys.api.mapdl_db.v0.putelmRequest) -> ansys.api.kernel.v0.EmptyResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `getAllElm` | `(ansys.api.kernel.v0.EmptyRequest) -> ansys.api.mapdl_db.v0.getelmResponse [client_streaming=False, server_streaming=True]` |
| `MapdlDbService` | `getAllElmC` | `(ansys.api.kernel.v0.EmptyRequest) -> ansys.api.kernel.v0.Chunk [client_streaming=False, server_streaming=True]` |
| `MapdlDbService` | `putAllElm` | `(ansys.api.mapdl_db.v0.putelmRequest) -> ansys.api.kernel.v0.EmptyResponse [client_streaming=True, server_streaming=False]` |
| `MapdlDbService` | `iqrEty` | `(ansys.api.mapdl_db.v0.iqretyRequest) -> ansys.api.mapdl_db.v0.iqretyResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `getEty` | `(ansys.api.mapdl_db.v0.getetyRequest) -> ansys.api.mapdl_db.v0.getetyResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `putEty` | `(ansys.api.mapdl_db.v0.putetyRequest) -> ansys.api.kernel.v0.EmptyResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `getAllEty` | `(ansys.api.kernel.v0.EmptyRequest) -> ansys.api.mapdl_db.v0.getetyResponse [client_streaming=False, server_streaming=True]` |
| `MapdlDbService` | `getAllEtyC` | `(ansys.api.kernel.v0.EmptyRequest) -> ansys.api.kernel.v0.Chunk [client_streaming=False, server_streaming=True]` |
| `MapdlDbService` | `putAllEty` | `(ansys.api.mapdl_db.v0.putetyRequest) -> ansys.api.kernel.v0.EmptyResponse [client_streaming=True, server_streaming=False]` |
| `MapdlDbService` | `iqrMp` | `(ansys.api.mapdl_db.v0.iqrmpRequest) -> ansys.api.mapdl_db.v0.iqrmpResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `getMp` | `(ansys.api.mapdl_db.v0.getmpRequest) -> ansys.api.mapdl_db.v0.getmpResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `putMp` | `(ansys.api.mapdl_db.v0.putmpRequest) -> ansys.api.kernel.v0.EmptyResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `delMp` | `(ansys.api.mapdl_db.v0.getmpRequest) -> ansys.api.kernel.v0.EmptyResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `iqrCsy` | `(ansys.api.mapdl_db.v0.iqrcsyRequest) -> ansys.api.mapdl_db.v0.iqrcsyResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `getCsy` | `(ansys.api.mapdl_db.v0.getcsyRequest) -> ansys.api.mapdl_db.v0.getcsyResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `putCsy` | `(ansys.api.mapdl_db.v0.putcsyRequest) -> ansys.api.kernel.v0.EmptyResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `delCsy` | `(ansys.api.mapdl_db.v0.getcsyRequest) -> ansys.api.kernel.v0.EmptyResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `NodResIqr` | `(ansys.api.mapdl_db.v0.NodResIqrRequest) -> ansys.api.mapdl_db.v0.NodResIqrResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `NodResGet` | `(ansys.api.mapdl_db.v0.NodResGetRequest) -> ansys.api.mapdl_db.v0.NodResGetResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `NodResPut` | `(ansys.api.mapdl_db.v0.NodResPutRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `NodResDel` | `(ansys.api.mapdl_db.v0.NodResDelRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `ElmResIqr` | `(ansys.api.mapdl_db.v0.ElmResIqrRequest) -> ansys.api.mapdl_db.v0.ElmResIqrResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `ElmResGet` | `(ansys.api.mapdl_db.v0.ElmResGetRequest) -> ansys.api.mapdl_db.v0.ElmResGetResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `ElmResPut` | `(ansys.api.mapdl_db.v0.ElmResPutRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `ElmResDel` | `(ansys.api.mapdl_db.v0.ElmResDelRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `getElmInfo` | `(ansys.api.mapdl_db.v0.GetElmInfoRequest) -> ansys.api.mapdl_db.v0.GetElmInfoResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `getElmData` | `(ansys.api.mapdl_db.v0.GetElmDataRequest) -> ansys.api.mapdl_db.v0.GetElmDataResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `putElmData` | `(ansys.api.mapdl_db.v0.PutElmDataRequest) -> ansys.api.mapdl_db.v0.PutElmDataResponse [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `putElmMatRec1` | `(ansys.api.mapdl_db.v0.putElmMatRec1Request) -> ansys.api.mapdl_db.v0.putElmMatRec1Response [client_streaming=False, server_streaming=False]` |
| `MapdlDbService` | `INISIsNewVersionUsed` | `(ansys.api.mapdl_db.v0.INISIsNewVersionUsedRequest) -> ansys.api.mapdl_db.v0.INISIsNewVersionUsedResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.mapdl.v0.mapdl_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `MapdlService` | `SendCommand` | `(ansys.api.mapdl.v0.CmdRequest) -> ansys.api.mapdl.v0.CmdResponse [client_streaming=False, server_streaming=False]` |
| `MapdlService` | `SendCommandS` | `(ansys.api.mapdl.v0.CmdRequest) -> ansys.api.mapdl.v0.CmdOutput [client_streaming=False, server_streaming=True]` |
| `MapdlService` | `InputFileLocal` | `(ansys.api.mapdl.v0.CmdRequest) -> ansys.api.kernel.v0.Chunk [client_streaming=True, server_streaming=True]` |
| `MapdlService` | `InputFile` | `(ansys.api.mapdl.v0.InputFileRequest) -> ansys.api.kernel.v0.Chunk [client_streaming=False, server_streaming=True]` |
| `MapdlService` | `InputFileS` | `(ansys.api.mapdl.v0.InputFileRequest) -> ansys.api.mapdl.v0.CmdOutput [client_streaming=False, server_streaming=True]` |
| `MapdlService` | `FctCall` | `(ansys.api.mapdl.v0.FctCallRequest) -> ansys.api.mapdl.v0.FctCallResponse [client_streaming=False, server_streaming=False]` |
| `MapdlService` | `GetNodes` | `(ansys.api.kernel.v0.EmptyRequest) -> ansys.api.kernel.v0.Node [client_streaming=False, server_streaming=True]` |
| `MapdlService` | `GetNode` | `(ansys.api.mapdl.v0.NodeRequest) -> ansys.api.mapdl.v0.NodeResponse [client_streaming=False, server_streaming=False]` |
| `MapdlService` | `SetNode` | `(ansys.api.mapdl.v0.setNodeRequest) -> ansys.api.mapdl.v0.setNodeResponse [client_streaming=False, server_streaming=False]` |
| `MapdlService` | `Nodes` | `(ansys.api.kernel.v0.EmptyRequest) -> ansys.api.kernel.v0.Chunk [client_streaming=False, server_streaming=True]` |
| `MapdlService` | `GetElements` | `(ansys.api.kernel.v0.EmptyRequest) -> ansys.api.mapdl.v0.Element [client_streaming=False, server_streaming=True]` |
| `MapdlService` | `GetElement` | `(ansys.api.mapdl.v0.ElementRequest) -> ansys.api.mapdl.v0.ElementResponse [client_streaming=False, server_streaming=False]` |
| `MapdlService` | `LoadElements` | `(ansys.api.kernel.v0.EmptyRequest) -> ansys.api.kernel.v0.Chunk [client_streaming=False, server_streaming=True]` |
| `MapdlService` | `GetElementType` | `(ansys.api.mapdl.v0.ElementRequest) -> ansys.api.mapdl.v0.ElementType [client_streaming=False, server_streaming=False]` |
| `MapdlService` | `LoadElementTypeDescription` | `(ansys.api.kernel.v0.EmptyRequest) -> ansys.api.kernel.v0.Chunk [client_streaming=False, server_streaming=True]` |
| `MapdlService` | `GetParameter` | `(ansys.api.mapdl.v0.ParameterRequest) -> ansys.api.mapdl.v0.ParameterResponse [client_streaming=False, server_streaming=False]` |
| `MapdlService` | `GetVariable` | `(ansys.api.mapdl.v0.VariableRequest) -> ansys.api.mapdl.v0.VariableResponse [client_streaming=False, server_streaming=False]` |
| `MapdlService` | `Get` | `(ansys.api.mapdl.v0.GetRequest) -> ansys.api.mapdl.v0.GetResponse [client_streaming=False, server_streaming=False]` |
| `MapdlService` | `VGet` | `(ansys.api.mapdl.v0.GetRequest) -> ansys.api.mapdl.v0.VariableResponse [client_streaming=False, server_streaming=False]` |
| `MapdlService` | `VGet2` | `(ansys.api.mapdl.v0.GetRequest) -> ansys.api.kernel.v0.Chunk [client_streaming=False, server_streaming=True]` |
| `MapdlService` | `Ctrl` | `(ansys.api.kernel.v0.CtrlRequest) -> ansys.api.kernel.v0.CtrlResponse [client_streaming=False, server_streaming=False]` |
| `MapdlService` | `GetVtkGeometry` | `(ansys.api.kernel.v0.EmptyRequest) -> ansys.api.kernel.v0.Chunk [client_streaming=False, server_streaming=True]` |
| `MapdlService` | `GetDataInfo` | `(ansys.api.mapdl.v0.ParameterRequest) -> ansys.api.mapdl.v0.DataResponse [client_streaming=False, server_streaming=False]` |
| `MapdlService` | `GetVecData` | `(ansys.api.mapdl.v0.ParameterRequest) -> ansys.api.kernel.v0.Chunk [client_streaming=False, server_streaming=True]` |
| `MapdlService` | `GetMatData` | `(ansys.api.mapdl.v0.ParameterRequest) -> ansys.api.kernel.v0.Chunk [client_streaming=False, server_streaming=True]` |
| `MapdlService` | `SetVecData` | `(ansys.api.mapdl.v0.SetVecDataRequest) -> ansys.api.kernel.v0.EmptyResponse [client_streaming=True, server_streaming=False]` |
| `MapdlService` | `SetMatData` | `(ansys.api.mapdl.v0.SetMatDataRequest) -> ansys.api.kernel.v0.EmptyResponse [client_streaming=True, server_streaming=False]` |
| `MapdlService` | `UploadFile` | `(ansys.api.mapdl.v0.UploadFileRequest) -> ansys.api.mapdl.v0.UploadFileReply [client_streaming=True, server_streaming=False]` |
| `MapdlService` | `DownloadFile` | `(ansys.api.mapdl.v0.DownloadFileRequest) -> ansys.api.kernel.v0.Chunk [client_streaming=False, server_streaming=True]` |

## Messages and fields

### `ansys.api.mapdl.v0.C_StreamGrpc_pb2`

| Message | Fields |
| --- | --- |
| `CloseRequest` | `filename: string` (Protobuf field number 1; repeated=False) |
| `CloseResponse` | `succeed: bool` (Protobuf field number 1; repeated=False)<br>`msg: string` (Protobuf field number 2; repeated=False) |
| `OpenRequest` | `filename: string` (Protobuf field number 1; repeated=False)<br>`mode: int32` (Protobuf field number 2; repeated=False) |
| `OpenResponse` | `succeed: bool` (Protobuf field number 1; repeated=False)<br>`msg: string` (Protobuf field number 2; repeated=False) |
| `ReadRequest` | `filename: string` (Protobuf field number 1; repeated=False)<br>`streamreq: ansys.api.kernel.v0.StreamRequest` (Protobuf field number 2; repeated=False)<br>`size: int64` (Protobuf field number 3; repeated=False) |
| `SeekRequest` | `filename: string` (Protobuf field number 1; repeated=False)<br>`offset: int64` (Protobuf field number 2; repeated=False)<br>`whence: int32` (Protobuf field number 3; repeated=False) |
| `SeekResponse` | `offset: int64` (Protobuf field number 1; repeated=False) |
| `TellRequest` | `filename: string` (Protobuf field number 1; repeated=False) |
| `TellResponse` | `offset: int64` (Protobuf field number 1; repeated=False) |
| `WriteRequest` | `filename: string` (Protobuf field number 1; repeated=False)<br>`size: int64` (Protobuf field number 2; repeated=False) |
| `WriteResponse` | — |

### `ansys.api.mapdl.v0.ansys_kernel_pb2`

| Message | Fields |
| --- | --- |
| `Chunk` | `array_name: string` (Protobuf field number 1; repeated=False)<br>`payload: bytes` (Protobuf field number 2; repeated=False)<br>`value_type: ansys.api.kernel.v0.ValueType` (Protobuf field number 3; repeated=False)<br>`shape: string` (Protobuf field number 4; repeated=False)<br>`size: int64` (Protobuf field number 5; repeated=False) |
| `CtrlRequest` | `ctrl: string` (Protobuf field number 1; repeated=False)<br>`opt1: string` (Protobuf field number 2; repeated=False) |
| `CtrlResponse` | `response: string` (Protobuf field number 1; repeated=False)<br>`status: int32` (Protobuf field number 2; repeated=False) |
| `DenseMatrix` | `mat: ansys.api.kernel.v0.Matrix` (Protobuf field number 1; repeated=False)<br>`values: double` (Protobuf field number 2; repeated=True) |
| `EmptyRequest` | — |
| `EmptyResponse` | — |
| `Matrix` | `nrow: int32` (Protobuf field number 1; repeated=False)<br>`ncol: int32` (Protobuf field number 2; repeated=False)<br>`vtype: ansys.api.kernel.v0.ValueType` (Protobuf field number 3; repeated=False)<br>`Storage: ansys.api.kernel.v0.Matrix.StorageOption` (Protobuf field number 4; repeated=False)<br>`side: ansys.api.kernel.v0.Matrix.SideOption` (Protobuf field number 5; repeated=False) |
| `Node` | `id: int32` (Protobuf field number 1; repeated=False)<br>`x: double` (Protobuf field number 2; repeated=False)<br>`y: double` (Protobuf field number 3; repeated=False)<br>`z: double` (Protobuf field number 4; repeated=False) |
| `SparseMatrix` | `mat: ansys.api.kernel.v0.Matrix` (Protobuf field number 1; repeated=False)<br>`maxlen: int32` (Protobuf field number 2; repeated=False)<br>`nval: int64` (Protobuf field number 3; repeated=False)<br>`sym: bool` (Protobuf field number 4; repeated=False)<br>`rows: int64` (Protobuf field number 5; repeated=True)<br>`colsIdx: int32` (Protobuf field number 6; repeated=True)<br>`values: double` (Protobuf field number 7; repeated=True) |
| `StreamRequest` | `chunk_size: int32` (Protobuf field number 1; repeated=False)<br>`rec_name: string` (Protobuf field number 2; repeated=False) |

### `ansys.api.mapdl.v0.mapdl_db_pb2`

| Message | Fields |
| --- | --- |
| `ElmIqrRequest` | `ielem: int32` (Protobuf field number 1; repeated=False)<br>`key: int32` (Protobuf field number 2; repeated=False) |
| `ElmIqrResponse` | `elmiqr: int32` (Protobuf field number 1; repeated=False) |
| `ElmRequest` | `next: int32` (Protobuf field number 1; repeated=False) |
| `ElmResDelRequest` | `type: ansys.api.mapdl_db.v0.ElmResult` (Protobuf field number 1; repeated=False)<br>`ielem: int32` (Protobuf field number 2; repeated=False) |
| `ElmResGetRequest` | `type: ansys.api.mapdl_db.v0.ElmResult` (Protobuf field number 1; repeated=False)<br>`ielem: int32` (Protobuf field number 2; repeated=False) |
| `ElmResGetResponse` | `get: int32` (Protobuf field number 1; repeated=False)<br>`value: double` (Protobuf field number 2; repeated=True) |
| `ElmResIqrRequest` | `type: ansys.api.mapdl_db.v0.ElmResult` (Protobuf field number 1; repeated=False)<br>`ielem: int32` (Protobuf field number 2; repeated=False)<br>`key: int32` (Protobuf field number 3; repeated=False) |
| `ElmResIqrResponse` | `iqr: int32` (Protobuf field number 1; repeated=False) |
| `ElmResPutRequest` | `type: ansys.api.mapdl_db.v0.ElmResult` (Protobuf field number 1; repeated=False)<br>`ielem: int32` (Protobuf field number 2; repeated=False)<br>`nval: int32` (Protobuf field number 3; repeated=False)<br>`value: double` (Protobuf field number 4; repeated=True) |
| `ElmResponse` | `inum: int32` (Protobuf field number 1; repeated=False) |
| `ElmSelRequest` | `inum: int32` (Protobuf field number 1; repeated=False)<br>`ksel: int32` (Protobuf field number 2; repeated=False) |
| `GetElmDataRequest` | `kchar: string` (Protobuf field number 1; repeated=False)<br>`elemId: int32` (Protobuf field number 2; repeated=False)<br>`kMatRecPt: int32` (Protobuf field number 3; repeated=False)<br>`ncomp: int32` (Protobuf field number 4; repeated=False) |
| `GetElmDataResponse` | `vect: double` (Protobuf field number 1; repeated=True) |
| `GetElmInfoRequest` | `inquire: string` (Protobuf field number 1; repeated=False) |
| `GetElmInfoResponse` | `value: int32` (Protobuf field number 1; repeated=False) |
| `INISIsNewVersionUsedRequest` | — |
| `INISIsNewVersionUsedResponse` | `ret: int32` (Protobuf field number 1; repeated=False) |
| `NodGallRequest` | `node: int32` (Protobuf field number 1; repeated=False) |
| `NodGallResponse` | `ret: int32` (Protobuf field number 1; repeated=False)<br>`xyz: double` (Protobuf field number 2; repeated=True) |
| `NodInqrRequest` | `node: int32` (Protobuf field number 1; repeated=False)<br>`key: int32` (Protobuf field number 2; repeated=False) |
| `NodInqrResponse` | `ret: int32` (Protobuf field number 1; repeated=False) |
| `NodRequest` | `next: int32` (Protobuf field number 1; repeated=False) |
| `NodResDelRequest` | `inode: int32` (Protobuf field number 1; repeated=False)<br>`ndf: int32` (Protobuf field number 2; repeated=False)<br>`idf: int32` (Protobuf field number 3; repeated=True) |
| `NodResGetRequest` | `inode: int32` (Protobuf field number 1; repeated=False)<br>`ndf: int32` (Protobuf field number 2; repeated=False)<br>`idf: int32` (Protobuf field number 3; repeated=True) |
| `NodResGetResponse` | `value: double` (Protobuf field number 1; repeated=True) |
| `NodResIqrRequest` | `inode: int32` (Protobuf field number 1; repeated=False)<br>`key: int32` (Protobuf field number 2; repeated=False) |
| `NodResIqrResponse` | `iqr: int32` (Protobuf field number 1; repeated=False) |
| `NodResPutRequest` | `inode: int32` (Protobuf field number 1; repeated=False)<br>`ndf: int32` (Protobuf field number 2; repeated=False)<br>`idf: int32` (Protobuf field number 3; repeated=True)<br>`value: double` (Protobuf field number 4; repeated=True) |
| `NodResponse` | `inum: int32` (Protobuf field number 1; repeated=False) |
| `NodSelRequest` | `inum: int32` (Protobuf field number 1; repeated=False)<br>`ksel: int32` (Protobuf field number 2; repeated=False) |
| `NodSpgtRequest` | `node: int32` (Protobuf field number 1; repeated=False)<br>`dofs: int32` (Protobuf field number 2; repeated=True)<br>`ndof: int32` (Protobuf field number 3; repeated=False)<br>`nrot: int32` (Protobuf field number 4; repeated=False)<br>`xyzang: double` (Protobuf field number 5; repeated=True)<br>`nuvect: int32` (Protobuf field number 6; repeated=False) |
| `NodSpgtResponse` | `unode: double` (Protobuf field number 1; repeated=True) |
| `PutElmDataRequest` | `inquire: string` (Protobuf field number 1; repeated=False)<br>`elemId: int32` (Protobuf field number 2; repeated=False)<br>`kIntg: int32` (Protobuf field number 3; repeated=False)<br>`nvect: int32` (Protobuf field number 4; repeated=False)<br>`vect: double` (Protobuf field number 5; repeated=True) |
| `PutElmDataResponse` | — |
| `getcsyRequest` | `ncsy: int32` (Protobuf field number 1; repeated=False)<br>`csyinx: int32` (Protobuf field number 2; repeated=True) |
| `getcsyResponse` | `ret: int32` (Protobuf field number 1; repeated=False)<br>`csydpx: double` (Protobuf field number 2; repeated=True) |
| `getelmRequest` | `ielem: int32` (Protobuf field number 1; repeated=False) |
| `getelmResponse` | `ielem: int32` (Protobuf field number 1; repeated=False)<br>`elmdat: int32` (Protobuf field number 2; repeated=True)<br>`nnod: int32` (Protobuf field number 3; repeated=False)<br>`nodes: int32` (Protobuf field number 4; repeated=True) |
| `getetyRequest` | `itype: int32` (Protobuf field number 1; repeated=False) |
| `getetyResponse` | `itype: int32` (Protobuf field number 1; repeated=False)<br>`ielx_sz: int32` (Protobuf field number 2; repeated=False)<br>`ielx: int32` (Protobuf field number 3; repeated=True) |
| `getmpRequest` | `mat: int32` (Protobuf field number 1; repeated=False)<br>`iprop: int32` (Protobuf field number 2; repeated=False) |
| `getmpResponse` | `ret: int32` (Protobuf field number 1; repeated=False)<br>`temp: double` (Protobuf field number 2; repeated=True)<br>`prop: double` (Protobuf field number 3; repeated=True) |
| `getnodRequest` | `node: int32` (Protobuf field number 1; repeated=False)<br>`kerr: int32` (Protobuf field number 2; repeated=False)<br>`kcrot: int32` (Protobuf field number 3; repeated=False) |
| `getnodResponse` | `kerr: int32` (Protobuf field number 1; repeated=False)<br>`v: double` (Protobuf field number 2; repeated=True) |
| `iqrcsyRequest` | `ncsy: int32` (Protobuf field number 1; repeated=False)<br>`key: int32` (Protobuf field number 2; repeated=False) |
| `iqrcsyResponse` | `ret: int32` (Protobuf field number 1; repeated=False) |
| `iqretyRequest` | `itype: int32` (Protobuf field number 1; repeated=False)<br>`key: int32` (Protobuf field number 2; repeated=False) |
| `iqretyResponse` | `iqr: int32` (Protobuf field number 1; repeated=False) |
| `iqrmpRequest` | `mat: int32` (Protobuf field number 1; repeated=False)<br>`iprop: int32` (Protobuf field number 2; repeated=False)<br>`key: int32` (Protobuf field number 3; repeated=False) |
| `iqrmpResponse` | `ret: int32` (Protobuf field number 1; repeated=False) |
| `putElmMatRec1Request` | `matRecordIndex: int32` (Protobuf field number 1; repeated=False)<br>`kMatRecPt: int32` (Protobuf field number 2; repeated=False)<br>`elemId: int32` (Protobuf field number 3; repeated=False)<br>`ncomp: int32` (Protobuf field number 4; repeated=False)<br>`vect: double` (Protobuf field number 5; repeated=True) |
| `putElmMatRec1Response` | — |
| `putcsyRequest` | `ncsy: int32` (Protobuf field number 1; repeated=False)<br>`csyinx: int32` (Protobuf field number 2; repeated=True)<br>`csydpx: double` (Protobuf field number 3; repeated=True) |
| `putelmRequest` | `ielem: int32` (Protobuf field number 1; repeated=False)<br>`elmdat: int32` (Protobuf field number 2; repeated=True)<br>`nnod: int32` (Protobuf field number 3; repeated=False)<br>`nodes: int32` (Protobuf field number 4; repeated=True) |
| `putetyRequest` | `itype: int32` (Protobuf field number 1; repeated=False)<br>`n: int32` (Protobuf field number 2; repeated=False)<br>`ielx: int32` (Protobuf field number 3; repeated=True) |
| `putmpRequest` | `mat: int32` (Protobuf field number 1; repeated=False)<br>`iprop: int32` (Protobuf field number 2; repeated=False)<br>`ntab: int32` (Protobuf field number 3; repeated=False)<br>`temp: double` (Protobuf field number 4; repeated=True)<br>`prop: double` (Protobuf field number 5; repeated=True) |
| `putnodRequest` | `node: int32` (Protobuf field number 1; repeated=False)<br>`vctn: double` (Protobuf field number 2; repeated=True)<br>`kcrot: int32` (Protobuf field number 3; repeated=False) |

### `ansys.api.mapdl.v0.mapdl_pb2`

| Message | Fields |
| --- | --- |
| `CmdOutput` | `msgtype: int32` (Protobuf field number 1; repeated=False)<br>`cmdout: string` (Protobuf field number 2; repeated=True) |
| `CmdRequest` | `command: string` (Protobuf field number 1; repeated=False)<br>`opt: string` (Protobuf field number 2; repeated=False) |
| `CmdResponse` | `response: string` (Protobuf field number 1; repeated=False)<br>`status: int32` (Protobuf field number 2; repeated=False)<br>`error_msg: string` (Protobuf field number 3; repeated=False) |
| `DataResponse` | `stype: ansys.api.kernel.v0.ValueType` (Protobuf field number 1; repeated=False)<br>`objtype: ansys.api.mapdl.v0.DataType` (Protobuf field number 2; repeated=False)<br>`size1: int32` (Protobuf field number 3; repeated=False)<br>`size2: int32` (Protobuf field number 4; repeated=False)<br>`mattype: ansys.api.mapdl.v0.MatType` (Protobuf field number 5; repeated=False) |
| `DownloadFileRequest` | `name: string` (Protobuf field number 1; repeated=False) |
| `Element` | `id: int32` (Protobuf field number 1; repeated=False)<br>`mat: int32` (Protobuf field number 2; repeated=False)<br>`type: int32` (Protobuf field number 3; repeated=False)<br>`real: int32` (Protobuf field number 4; repeated=False)<br>`sect: int32` (Protobuf field number 5; repeated=False)<br>`cs: int32` (Protobuf field number 6; repeated=False)<br>`node_count: int32` (Protobuf field number 7; repeated=False)<br>`nodes_ids: int32` (Protobuf field number 8; repeated=True) |
| `ElementRequest` | `num: int32` (Protobuf field number 1; repeated=False) |
| `ElementResponse` | `elm: ansys.api.mapdl.v0.Element` (Protobuf field number 1; repeated=False) |
| `ElementType` | `ielc: int32` (Protobuf field number 1; repeated=True) |
| `FctArg` | `type: ansys.api.kernel.v0.ValueType` (Protobuf field number 1; repeated=False)<br>`val: string` (Protobuf field number 2; repeated=True) |
| `FctCallRequest` | `fct_name: string` (Protobuf field number 1; repeated=False)<br>`args: ansys.api.mapdl.v0.FctArg` (Protobuf field number 2; repeated=True)<br>`returns_arg: bool` (Protobuf field number 3; repeated=False) |
| `FctCallResponse` | `feedback: ansys.api.mapdl.v0.FctArg` (Protobuf field number 1; repeated=False) |
| `GetRequest` | `getcmd: string` (Protobuf field number 1; repeated=False) |
| `GetResponse` | `dval: double` (Protobuf field number 1; repeated=False)<br>`sval: string` (Protobuf field number 2; repeated=False)<br>`type: int32` (Protobuf field number 3; repeated=False) |
| `InputFileRequest` | `filename: string` (Protobuf field number 1; repeated=False)<br>`opt: string` (Protobuf field number 2; repeated=False) |
| `NodeRequest` | `num: int32` (Protobuf field number 1; repeated=False) |
| `NodeResponse` | `node: ansys.api.kernel.v0.Node` (Protobuf field number 1; repeated=False) |
| `ParameterRequest` | `name: string` (Protobuf field number 1; repeated=False)<br>`array: bool` (Protobuf field number 2; repeated=False) |
| `ParameterResponse` | `val: double` (Protobuf field number 1; repeated=True)<br>`sval: string` (Protobuf field number 2; repeated=False)<br>`type: int32` (Protobuf field number 3; repeated=False) |
| `SetMatDataRequest` | `mname: string` (Protobuf field number 1; repeated=False)<br>`stype: ansys.api.kernel.v0.ValueType` (Protobuf field number 2; repeated=False)<br>`nrow: int32` (Protobuf field number 3; repeated=False)<br>`ncol: int32` (Protobuf field number 4; repeated=False)<br>`chunk: ansys.api.kernel.v0.Chunk` (Protobuf field number 5; repeated=False) |
| `SetVecDataRequest` | `vname: string` (Protobuf field number 1; repeated=False)<br>`stype: ansys.api.kernel.v0.ValueType` (Protobuf field number 2; repeated=False)<br>`size: int32` (Protobuf field number 3; repeated=False)<br>`chunk: ansys.api.kernel.v0.Chunk` (Protobuf field number 4; repeated=False) |
| `UploadFileReply` | `length: int32` (Protobuf field number 1; repeated=False) |
| `UploadFileRequest` | `file_name: string` (Protobuf field number 1; repeated=False)<br>`chunk: ansys.api.kernel.v0.Chunk` (Protobuf field number 2; repeated=False) |
| `VariableRequest` | `inum: int32` (Protobuf field number 1; repeated=False) |
| `VariableResponse` | `val: double` (Protobuf field number 1; repeated=True) |
| `setNodeRequest` | `node: ansys.api.kernel.v0.Node` (Protobuf field number 1; repeated=False) |
| `setNodeResponse` | `num: int32` (Protobuf field number 1; repeated=False) |

## Snapshot counts

- RPC methods: 84
- Protocol messages: 105
- Message fields: 227
