# ANSYS API 與文件檢索指南

本指南說明如何以現有 MCP 工具查找 ANSYS API 與官方文件。APIKB 保存 API 符號快照。文件檢索索引保存本機整理的 ANSYS 文件片段。兩種來源各自回答不同問題，查詢時應交叉比對。

## 查詢流程

1. 先用 `list_ansys_docs` 查看目前可搜尋的文件、產品、版本、分類和片段數。
2. 用 `api_search` 搜尋類別、方法或屬性。可提供 `product` 限定來源鍵，也可提供 `kind` 限定符號種類。
3. 用 `api_get` 取得指定符號的完整名稱、成員、關聯型別和來源資訊。若結果有多個候選，提供 `product`、`release` 或 `interface` 再查一次。
4. 用 `search_ansys_docs` 查找官方 API reference、scripting guide 或教學。優先提供英文 API 名稱，並用 `product`、`release`、`category` 或 `sdk_version` 限定版本與文件類型。
5. 對照文件片段與 APIKB 結果。以 `get_ansys_doc_chunk` 讀取命中片段和相鄰上下文，並記錄文件名稱、版本與 chunk ID。
6. 回答時標示來源種類、產品版本、介面版本、snapshot SHA-256、組件 SHA-256、REA Evidence ID（若有）、公開狀態和驗證狀態。不要把缺少的欄位推測成已知事實。

## Workbench and product protocol routing

- Query the Python SDK snapshot with `api_search(query="launch_workbench", product="workbench")`.
- Query the Sherlock SDK snapshot with `api_search(query="<member name>", product="sherlock_core")`; its package version is 2.1.4, while the ANSYS product release and host behavior remain unverified.
- Query the Rocky SDK snapshot with `api_search(query="<member name>", product="rocky")`; its package version is 0.6.2, while the ANSYS product release and host behavior remain unverified.
- Query the PyAnsys Speos SDK snapshot with `api_search(query="<member name>", product="speos")` and its gRPC schema with `product="speos_protocol"`. The package README shows conflicting 2025.1, Docker tag 261, and AWP_ROOT251 examples; do not infer release support from them.
- Query the PyAnsys CFX snapshot with `api_search(query="<member name>", product="cfx")`; it captures direct AST declarations only. Package metadata requires a licensed local CFX installation and states support for CFX 2025 R2 SP3 and later; do not infer v251 compatibility. The dynamic flobject/TUI surface is omitted.
- Query the Workbench gRPC protocol with `api_search(query="RunScript", product="workbench_protocol")`.
- Query other mapped protocol sources with `mechanical_protocol`, `geometry_protocol`, `fluent_protocol`, `mapdl_protocol`, `primemesh_protocol`, or `discovery_protocol` as the `product` value.
- Query an unclassified source only by its own key, such as `dbu_protocol` or `result_explorer_protocol`. Do not map it to a product without evidence.
- Use [the protocol index](./curated/protocols/index.md) to select the source and read the RPC or field summary.
- A hit shows that the indexed source contains the symbol. It does not prove product support, server compatibility, or runtime behavior.

## 查詢 REA managed snapshots

1. 先讀[REA managed snapshot 索引](./curated/rea/index.md)，依產品矩陣選擇 APIKB source key。
2. 用 `api_search(query="<member name>", product="<source_key>")` 找成員，再用 `api_get` 讀取完整名稱與來源欄位。
3. 用[REA 組件證據摘要](./REA_EVIDENCE.md)比對組件 SHA-256、MVID、REA Evidence ID 和分析限制。

例如，可用 `api_search(query="<member name>", product="aqwa_remote_itf_rea")` 查找 AQWA RemoteItf、用 `product="acp_core_rea"` 查找 ACP、用 `product="motion_api_rea"` 查找 ANSYS Motion，或用 `product="siwave_libironpythoncmd_rea"` 查找 SIwave、用 `product="rsm_jobmanagement_rea"` 查找未映射的 RSM JobManagement 靜態候選；也可用 `engineeringdata_dataprovider_rea`、`designmodeler_core_rea` 與 `materialdesigner_core_rea`、`engineeringdata_core_rea`、`turbosystem_afd_core_rea`、`turbosystem_ccd_core_rea`、`turbosystem_cpd_core_rea`、`turbosystem_rtd_core_rea` 查找其他尚未核實支援狀態的元件 metadata。先確認來源索引中的組件身分，再判讀命中內容；結果不代表公開支援 API 或可在宿主呼叫。

REA metadata 可包含非公開成員。`public_status` 和 `validation_status` 是證據欄位，不代表 Ansys 支援承諾或 runtime 可用性。

## 工具用途

| 工具 | 用途 | 主要限制 |
| --- | --- | --- |
| `list_ansys_docs` | 列出文件索引中的可用文件 | 只反映目前索引，不表示本機文件庫已完整匯入 |
| `search_ansys_docs` | 搜尋文件片段 | 關鍵字檢索；不是語意搜尋。`scope="api"` 無命中時會擴大到全部文件 |
| `get_ansys_doc_chunk` | 讀取命中片段與相鄰片段 | 必須使用搜尋結果中的文件名稱和 chunk ID |
| `api_search` | 搜尋已索引的 API、SDK、REA 符號 | 命中代表來源有此記錄，不代表官方支援或 runtime 可用 |
| `api_get` | 讀取指定符號的定義、成員與關聯 | 同名符號可能需要產品、release 或 interface 才能消歧 |
| `api_path` | 查詢型別間的物件導覽路徑 | 只反映已建置的知識圖關係 |
| `api_validate_script` | 依 Mechanical 或 SpaceClaim 快照檢查腳本中的 API 名稱 | 靜態檢查不能證明宿主版本、權限、模型狀態或 runtime 行為 |

不要在一般查詢中呼叫 `rebuild_ansys_docs_index`。重建會掃描文件來源並改寫本機索引；只在確認來源目錄及索引目標後，由維護流程執行。

## 證據標籤

| 標籤 | 解讀 |
| --- | --- |
| 官方文件 | 文件直接描述的 API 或行為。仍須確認文件所屬產品、release 和介面 |
| SDK snapshot | 從指定 SDK 版本的 Python 套件或公開介面擷取的快照。只涵蓋記錄範圍 |
| REA static metadata | 從指定組件讀取的靜態 .NET metadata。型別可見性和方法旗標不代表產品支援承諾 |
| Native export | PE export table 中的名稱。通常不含可用的參數、回傳型別或呼叫慣例 |
| `runtime_unverified` | 尚未在相應產品宿主中執行驗證 |
| `not_classified` | 公開狀態尚未由官方來源分類 |

`release` 和 `sdk_version` 是不同欄位。SDK 版本不可改寫成 ANSYS 產品 release。若官方文件、SDK snapshot 與 REA 結果不同，分列各自證據及來源雜湊，不要合併成單一簽名。

## 已整理的人讀字典

- [Mechanical v251 API 字典](./curated/mechanical/api_reference_v251.md)
- [SpaceClaim v251 API 字典](./curated/spaceclaim/api_reference_v251.md)
- [全產品 API 來源與缺口索引](./PRODUCT_API_MATRIX.md)
- [Workbench SDK 0.14.0 簽名摘要](./curated/workbench/sdk_0_14_0_inventory.md)
- [Workbench gRPC protocol 0.4.0 字典](./curated/workbench/protocol_0_4_0.md)
- [有版本標記的 Python SDK 人讀字典](./curated/sdk/index.md)
- [PyAnsys gRPC/protobuf 協定索引](./curated/protocols/index.md)（含 11 份服務、RPC、訊息與欄位字典）
- [REA managed snapshot 索引](./curated/rea/index.md)（55 個來源 key、assembly identity 與 metadata 計數）
- [產品與來源覆蓋清冊](./api_coverage.json)
- [REA 組件證據摘要](./REA_EVIDENCE.md)
- [REA managed snapshot source index](./curated/rea/index.md)
- [API 快照目錄](./API_CATALOG.md)

Mechanical 與 SpaceClaim 有整理型 API 使用字典。Workbench SDK 與其他有版本標記的 Python SDK 快照另有摘要及人讀字典；14 份版本化 Python SDK 字典，以及 12 份 protocol snapshot 另有逐 RPC／欄位字典。這些字典由 snapshot 產生，尚未逐項對照官方文件，也不代表宿主 API。APIKB 的來源鍵數不等於產品數，也不等於完整公開 API。57 個 manifest 產品 ID 的來源、版本、介面和缺口請以覆蓋清冊為準。
