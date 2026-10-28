# PyAnsys gRPC/protobuf 協定索引

## 範圍

本索引整理 repo `.venv` 已安裝之產品協定套件。每個 JSON snapshot 記錄 protobuf message 欄位、gRPC RPC 請求與回應型別、串流方向及原始 generated module 檔案雜湊。套件版本不是 ANSYS 產品 release。

這些資料描述傳輸協定，不等於 scripting API、完整產品 API、官方支援狀態或可執行行為。尚未連線產品宿主，也未核對伺服器相容性。不同版本套件可有不同 protocol schema。

## 已擷取協定

| 產品 | 套件版本 | Modules | Services | RPC | Messages | Fields | APIKB 來源鍵、snapshot 與人讀字典 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Mechanical | `ansys-api-mechanical 0.1.4` | 1 | 1 | 5 | 9 | 18 | `mechanical_protocol` · [JSON](../../mechanical_protocol_api.json) · [字典](./mechanical_protocol.md) |
| Geometry | `ansys-api-geometry 0.4.92` | 18 | 17 | 298 | 491 | 1,272 | `geometry_protocol` · [JSON](../../geometry_protocol_api.json) · [字典](./geometry_protocol.md) |
| Fluent | `ansys-api-fluent 0.6.0` | 35 | 28 | 290 | 813 | 1,697 | `fluent_protocol` · [JSON](../../fluent_protocol_api.json) · [字典](./fluent_protocol.md) |
| MAPDL | `ansys-api-mapdl 0.6.0` | 4 | 3 | 84 | 105 | 227 | `mapdl_protocol` · [JSON](../../mapdl_protocol_api.json) · [字典](./mapdl_protocol.md) |
| PrimeMesh | `ansys-api-meshing-prime 0.2.0` | 1 | 1 | 7 | 10 | 11 | `primemesh_protocol` · [JSON](../../primemesh_protocol_api.json) · [字典](./primemesh_protocol.md) |
| Discovery | `ansys-api-discovery 1.2.12` | 142 | 130 | 1,422 | 1,742 | 4,119 | `discovery_protocol` · [JSON](../../discovery_protocol_api.json) · [字典](./discovery_protocol.md) |
| Workbench | `ansys-api-workbench 0.4.0` | 1 | 1 | 3 | 10 | 19 | `workbench_protocol` · [JSON](../../workbench_protocol_api.json) · [字典](./workbench_protocol.md) |

Workbench 的三個 RPC 與訊息欄位另有[人讀協定字典](../workbench/protocol_0_4_0.md)。

## 尚未映射到產品 ID 的已安裝協定

| 套件 | 版本 | APIKB 來源鍵與 snapshot | 映射說明 |
| --- | --- | --- | --- |
| `ansys-api-dbu` | 0.3.29 | `dbu_protocol` · [JSON](../../dbu_protocol_api.json) · [字典](./dbu_protocol.md) | 套件說明為 DBU Service，尚未確認它對應 coverage 清冊中的哪個產品 ID。 |
| `ansys-api-result-explorer` | 0.1.1 | `result_explorer_protocol` · [JSON](../../result_explorer_protocol_api.json) · [字典](./result_explorer_protocol.md) | Result Explorer 不在目前 57 個產品 ID 清冊中，暫不映射為 EnSight。 |
| `ansys-api-platform-instancemanagement` | 1.2.0 | `platform_instance_management_protocol` · [JSON](../../platform_instance_management_protocol_api.json) · [字典](./platform_instance_management_protocol.md) | 共用平台服務 schema，不屬於單一產品 API。 |
| `ansys-api-tools-filetransfer` | 0.2.0 | `filetransfer_protocol` · [JSON](../../filetransfer_protocol_api.json) · [字典](./filetransfer_protocol.md) | 共用檔案傳輸工具 schema，不屬於單一產品 API。 |

這四份 snapshot 供 APIKB 搜尋，未加入 coverage 產品 ID 統計。未確認產品歸屬前，請勿把它們計入任何產品的 API 覆蓋率。

## 重建人讀字典

由已保存的 JSON snapshots 重產這 11 份 Markdown 字典：

```powershell
python scripts/api_extraction/render_protocol_dictionaries.py
```

此命令只讀取 snapshot，寫入 `curated/protocols/`。完整 API snapshot 批次流程也會自動重建這些頁面。APIKB 查詢不依賴 Markdown 頁面。

## 檢索

使用 `api_search` 時以來源鍵限定協定，例如：

- `product="mechanical_protocol"`：Mechanical gRPC schema。
- `product="geometry_protocol"`：Geometry gRPC schema。
- `product="fluent_protocol"`：Fluent gRPC schema。
- `product="mapdl_protocol"`：MAPDL gRPC schema。
- `product="primemesh_protocol"`：PrimeMesh gRPC schema。
- `product="discovery_protocol"`：Discovery gRPC schema。
- `product="workbench_protocol"`：Workbench gRPC schema。
- `product="dbu_protocol"`：未映射產品的 DBU Service schema。
- `product="result_explorer_protocol"`：未映射產品的 Result Explorer schema。
- `product="platform_instance_management_protocol"`：共用平台服務 schema。
- `product="filetransfer_protocol"`：共用檔案傳輸工具 schema。

命中只表示快照包含該名稱。APIKB 不會連線伺服器，也不會推斷服務版本、權限或 runtime 結果。
