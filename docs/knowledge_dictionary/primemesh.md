# Ansys Prime Mesh／PyPrimeMesh 主題字典

本頁整理 Prime Mesh Python client library 的基本概念與操作。主要依據 2026 R1 SP01（v261）開發者文件及 v252 入門頁；API 選項與預設值應以使用中的產品／套件版本文件為準。

## 產品與版本

Prime Mesh Python client library 將 Ansys Prime Server 的網格能力透過 Python API 提供給 client application；文件描述 client 以 gRPC 與 server 溝通。2026 R1 SP01 入門頁標示其基礎為 PyPrimeMesh 0.10.2 的修改版本；2025 R2 入門頁則列為 PyPrimeMesh 0.9.0。文件清冊另有 `ansys-meshing-prime 0.10.5` SDK 頁面，這是 SDK 文件版本，不能與 Ansys 產品 release 混為一談。

文件概述的能力包含 CAD 輸入、表面與體積網格、網格品質檢查、幾何診斷，以及 solver 格式輸出。實際 API 是否存在、參數預設與並行限制需按所用 release 核對。

## Client、模型與檔案

官方 quick code 以 `with prime.launch_prime() as prime_client` 啟動 client 並取得 `client.model`；`Client` API 也可連線至指定 Prime Server。v261 `Client` 簽章列出 `ip=127.0.0.1`、`port=50055`、`timeout=20.0`、`connection_type=GRPC_SECURE`；`client_certs_dir` 用於提供 mutual TLS client certificates。`Client.exit()` 關閉 server 連線，`Client.model` 取得關聯模型。上述預設值是 `Client` API 文件值，不推定所有啟動入口相同。

v261 SP01 的 `FileIO.read_pmdat(file_name, file_read_params)` 讀取 PyPrimeMesh data（PMDAT）檔並回傳 `FileReadResults`。該 API 頁明確註記此方法不支援 Unicode 路徑；含非 ASCII 字元的路徑應先確認環境相容性。入門頁範例亦以 `FileIO` 與 `FileReadParams` 讀檔。

- [PyPrimeMesh SDK API index（SDK docs version 0.10.5）](../ANSYS_Document/PrimeMesh/sdk/ansys-meshing-prime/0.10.5/api_reference/f6bcf6e95799-index.md)：這是 SDK 文件版本，不代表 Ansys Prime Mesh release。

## CAD 匯入、拓樸與 solver 檔案流程（SDK 0.10.5 範例）

SDK 0.10.5 的「Convert data when importing and exporting mesh and CAD formats」範例示範一條匯入與輸出流程：以 `prime.lucid.Mesh` 載入 CAD，檢視 `TopoPart`、`TopoEdge`、`TopoFace`、`TopoVolume`；CAD 中的 named selections/groups 會成為 PyPrimeMesh labels；再產生表面網格及 tetrahedral volume mesh，輸出 PMDAT、CDB 或 CAS，並重新匯入 solver 檔案檢視實體。這是範例流程，不代表每種 CAD／solver 格式均支援相同資料映射。

範例中的 SpaceClaim 單一 solid body 匯入後成為 `Volume Zone`；surface body、edge body 則分別對應 `Face Zone`、`Edge Zone`。這些是範例模型所見的對應關係，遇到多實體、命名衝突或格式差異時應檢查匯入後的 model summary 與 labels。

## 依分析目的組織網格工作流程（SDK 0.10.5 範例）

- **結構支架範例**：先由 SpaceClaim 匯入 bracket 幾何，再以 topology-based connection 對 topofaces／topoedges 執行 scaffold，生成 conformal quad surface mesh，最後輸出 CDB 供 APDL 使用。範例依指定 tolerance 建立連接；tolerance 與網格尺寸是範例設定，不能直接當作其他幾何的建議值。
- **流體混合彎管範例**：從匯入幾何的 labels 建立 `inlet`、`outlet` zones，以 `surface_mesh(min_size=5, max_size=20)` 做曲率尺寸控制；以 `VolumeFillType.POLY` 生成 polyhedral volume mesh，並在 `"* !inlet !outlet"` 範圍配置 3 層 prism layers，最後輸出 Fluent CAS。範例的長層範圍排除 inlet/outlet；尺寸、層數及邊界條件命名均屬特定範例，使用前需按實際模型確認 labels、單位和 solver 要求。

以上兩個 tutorial 來自 PyPrimeMesh SDK 0.10.5 的 stable 文件站；本地清冊的 release 欄為 `unknown`，因此不將其歸入 v261 或其他 Ansys release。程式碼與畫面僅供流程理解，未在本次執行；HTML 轉換稿中有空白圖片替代文字、Python 型別註記被轉成外連，以及執行環境輸出等呈現瑕疵，應以原始網頁及其下載範例為準。

## 表面網格

v261 SP01 `Mesh.surface_mesh()` 在指定 scope 上產生表面網格，可設定 `min_size`、`max_size` 與 `generate_quads`：

| 設定 | 文件所述行為 |
| --- | --- |
| `min_size` 與 `max_size` 都提供 | 依曲率在兩個尺寸間生成變尺寸網格。 |
| 只提供其中一項 | 使用指定尺寸生成等尺寸網格。 |
| 兩項皆省略 | 使用 global maximum setting 生成等尺寸網格。 |
| `generate_quads=False`（預設） | 生成三角形表面網格。 |
| `generate_quads=True` | 生成 quad-dominant 表面網格。 |

參數值要和目標幾何、scope 及版本預設一起檢查；此 API 說明不構成特定分析的網格尺寸建議。

## 體積網格與 prism layers

v261 SP01 `Mesh.volume_mesh()` 的頁面列出 `volume_fill_type`、`quadratic`、`prism_layers`、prism surface／volume expressions、`growth_rate` 與 scope。文件所列預設包含 `volume_fill_type=TET`、`quadratic=False`、`prism_layers=None`、surface／volume expression 為 `"*"`、`growth_rate=1.2`。設定 prism layer 時，surface 與 volume expression 決定長層的面和體積範圍。

同一 API 頁指出二次網格（`quadratic=True`）不支援 parallel meshing，且只支援純 tetrahedral mesh。這是 v261 SP01 頁面記載的限制；套用至其他版本前需重新查對該版本 API。

## 幾何診斷與品質檢查

產品入門文件列出 free edges、multi-connected edges、self-intersections、overlapping faces 等幾何診斷。v261 API 的 `SurfaceDiagnosticSummaryParams` 提供是否計算 free edges、multi-edges、self-intersections、duplicate faces 等選項；結果物件例如 `SurfaceDiagnosticSummaryResults.n_free_edges` 回報找到的 free face edges 數量。

這些診斷結果用於定位幾何拓樸問題，不能直接等同網格品質通過，也沒有在本頁設定通用 skewness、orthogonal quality 或 solver 硬門檻。應把診斷、元素品質與目標 solver／分析需求分開判讀。

## 版本差異與網格品質判讀

目前可直接比較的版本證據限於官方 Introduction 與本字典引用的 v261 SP01 API：

| Ansys release | 官方頁標示的隨附 PyPrimeMesh 基礎版本 | 本批來源可支持的範圍 |
| --- | --- | --- |
| 2025 R2（v252） | 修改版 PyPrimeMesh 0.9.0 | 入門頁所列能力與 quick code；未收集同一組 API 的 v252 參數頁。 |
| 2026 R1 SP01（v261） | 修改版 PyPrimeMesh 0.10.2 | 入門頁能力，以及本字典引用的 Client、表面／體積網格和診斷 API。 |
| SDK 文件 0.10.5 | 獨立 SDK 文件版本 | 文件索引本身的版本標籤；不等於 v261 的隨附 SDK 版本。 |

兩版 Introduction 都提及網格品質檢查及幾何診斷能力；v261 API 範例中的 free edges、multi-edges、self-intersections 與 duplicate faces 是拓樸診斷項目，不是元素品質通過判準。這批來源未提供跨版本 API 參數差異表，也未給出可通用於所有 solver 的品質門檻。**實務判讀（依來源範圍推論）**：先依目標 solver 與分析需求選用品質指標和允收值，再將幾何診斷結果另行檢視；不可把「沒有 free edges」直接當成網格品質合格。

## 來源

- [v261／2026 R1 SP01 Introduction](../ANSYS_Document/PrimeMesh/v261/guide/a9c2588c97d0-index.md)（`ansys_b89f2a8dd8092ded5ab730c9`）
- [v252／2025 R2 Introduction](../ANSYS_Document/PrimeMesh/v252/guide/7a004d61c811-index.md)（`ansys_c2350c6b838d5ccee9aa8168`）
- [SDK 文件索引 0.10.5](../ANSYS_Document/PrimeMesh/sdk/ansys-meshing-prime/0.10.5/api_reference/f6bcf6e95799-index.html)（`ansys_5144e41faac4bf655dbaff4d`）：僅表示 SDK 文件版本。
- [v261 `Client`](../ANSYS_Document/PrimeMesh/v261/api_reference/prime-mesh-python-client-library-2026-r1-sp01/api/_autosummary/ansys.meshing.prime.Client.md)（`ansys_bc8a3623e8b0b90b00742c47`）與 [`FileIO.read_pmdat`](../ANSYS_Document/PrimeMesh/v261/api_reference/prime-mesh-python-client-library-2026-r1-sp01/api/_autosummary/ansys.meshing.prime.FileIO.read_pmdat.md)（`ansys_edd7416509d3e70314a27280`）
- [`Mesh.surface_mesh`](../ANSYS_Document/PrimeMesh/v261/api_reference/prime-mesh-python-client-library-2026-r1-sp01/api/_autosummary/ansys.meshing.prime.lucid.Mesh.surface_mesh.md)（`ansys_7113e3a447074adf741acb06`）及 [`Mesh.volume_mesh`](../ANSYS_Document/PrimeMesh/v261/api_reference/prime-mesh-python-client-library-2026-r1-sp01/api/_autosummary/ansys.meshing.prime.lucid.Mesh.volume_mesh.md)（`ansys_4c08b7d6ccefe8a137ca21fb`）
- [`SurfaceDiagnosticSummaryParams.compute_free_edges`](../ANSYS_Document/PrimeMesh/v261/api_reference/prime-mesh-python-client-library-2026-r1-sp01/api/_autosummary/ansys.meshing.prime.SurfaceDiagnosticSummaryParams.compute_free_edges.md)（`ansys_257a0db15cc1839596f594c9`）、[`compute_duplicate_faces`](../ANSYS_Document/PrimeMesh/v261/api_reference/prime-mesh-python-client-library-2026-r1-sp01/api/_autosummary/ansys.meshing.prime.SurfaceDiagnosticSummaryParams.compute_duplicate_faces.md)（`ansys_38a63682d5a415a4e7355ff4`）、[`compute_multi_edges`](../ANSYS_Document/PrimeMesh/v261/api_reference/prime-mesh-python-client-library-2026-r1-sp01/api/_autosummary/ansys.meshing.prime.SurfaceDiagnosticSummaryParams.compute_multi_edges.md)（`ansys_350239f43a2c93cd04839f75`）、[`compute_self_intersections`](../ANSYS_Document/PrimeMesh/v261/api_reference/prime-mesh-python-client-library-2026-r1-sp01/api/_autosummary/ansys.meshing.prime.SurfaceDiagnosticSummaryParams.compute_self_intersections.md)（`ansys_081b5f21103e22eb789a4527`）
- [`SurfaceDiagnosticSummaryResults.n_free_edges`](../ANSYS_Document/PrimeMesh/v261/api_reference/prime-mesh-python-client-library-2026-r1-sp01/api/_autosummary/ansys.meshing.prime.SurfaceDiagnosticSummaryResults.n_free_edges.md)（`ansys_adca02b71e83f6fe022c9205`）
- [SDK 0.10.5 檔案匯入／匯出範例](../ANSYS_Document/PrimeMesh/sdk/ansys-meshing-prime/0.10.5/tutorial/10d7edef8293-00_lucid_file_IO.md)（`ansys_4e82b4d3a65717d32721d5f9`）、[支架 scaffold 範例](../ANSYS_Document/PrimeMesh/sdk/ansys-meshing-prime/0.10.5/tutorial/18a0c38fd5c3-01_bracket_scaffold.md)（`ansys_87b88a9f0a77729f6ff7f3a3`）、[混合彎管範例](../ANSYS_Document/PrimeMesh/sdk/ansys-meshing-prime/0.10.5/tutorial/218dff955f6b-02_lucid_mixing_elbow.md)（`ansys_03008bdbe43623979ed092b7`）。三者均為 SDK 0.10.5 stable 文件；不推定其對應的 Ansys release。

## 待補與限制

- 未逐項比較 2,500 餘筆 API，也未收集相同 API 的 v252 參數頁；詳細參數仍限於本頁標明的 v261 API 原文，不能據此推定跨版相容。
- 目前摘要涵蓋主要工作流程與一組 v261 SP01 API；未整理所有 2,500 餘筆 API 條目、演算法專章、CAD 修復流程及 solver 匯出細節。
- 本地來源清冊目前列出 4 份 SDK 官方 HTML（1 份 API index、3 份 tutorial），均有同名 Markdown；另有 11 份 v252／v261 Markdown API／guide 頁。SDK 0.10.5 API index 的 HTML 約 23,785 bytes，但 Markdown 僅 460 bytes，僅可作索引而不能視為完整內容轉換。3 份 tutorial 的 Markdown 有 20–32 個 fenced code blocks，未見 Markdown 圖片標記；HTML 各有 4–13 個 `<img>`。三篇教程曾抽查流程內容，但未逐頁核對所有圖、程式碼、表格及錨點保真度。PrimeMesh 來源清冊沒有 PDF；本機 3 組 `.ipynb`／`.py` 範例已有文字補件，Notebook outputs 與圖片未擷取，未執行範例。
- 七個主題均限於各自引用的來源範圍；未啟動 Prime Server、未執行網格生成或幾何診斷，也未驗證實際求解器品質。


## PyPrimeMesh tutorial 附件文字補件

三組教學的 Notebook 與 Python 原始檔各一份，共六份。補件保留程式與 Notebook 的 Markdown／code cells，並連回原始附件及來源 ID；Notebook 執行輸出、圖片及其他附件未擷取，產品 release unknown，範例未執行。

- [00_lucid_file_IO.ipynb](ANSYS_Document/primemesh_example_inputs_20261104/tutorial/ansys_6c338fe95efdd92d2aaf334c/primemesh.md)（`sources.csv#ansys_6c338fe95efdd92d2aaf334c`）
- [00_lucid_file_IO.py](ANSYS_Document/primemesh_example_inputs_20261104/tutorial/ansys_95830c49791110a7eccffc5d/primemesh.md)（`sources.csv#ansys_95830c49791110a7eccffc5d`）
- [01_bracket_scaffold.ipynb](ANSYS_Document/primemesh_example_inputs_20261104/tutorial/ansys_307357a2effd30bb0fac4b6a/primemesh.md)（`sources.csv#ansys_307357a2effd30bb0fac4b6a`）
- [01_bracket_scaffold.py](ANSYS_Document/primemesh_example_inputs_20261104/tutorial/ansys_c2058be19c881550ecf364b1/primemesh.md)（`sources.csv#ansys_c2058be19c881550ecf364b1`）
- [02_lucid_mixing_elbow.ipynb](ANSYS_Document/primemesh_example_inputs_20261104/tutorial/ansys_6d9ac45b7af1fa4f1157f5b4/primemesh.md)（`sources.csv#ansys_6d9ac45b7af1fa4f1157f5b4`）
- [02_lucid_mixing_elbow.py](ANSYS_Document/primemesh_example_inputs_20261104/tutorial/ansys_b11f80e3f391d9564b9ecac2/primemesh.md)（`sources.csv#ansys_b11f80e3f391d9564b9ecac2`）

逐檔 SHA、cell 數及狀態見 [轉換清冊](../maintenance/knowledge_dictionary_passes/2026-11-04/primemesh_attachment_text_recovery.csv)。


## 2026-11-04：Wave 8 本機來源盤點與限制說明

本批完成 primemesh 模組既有本機 catalog 文件（共 2576 筆）與 sources 清冊（共 21 筆）之完整雜湊、正文路徑與標籤結構核對。本機未快取或具備企業授權/登入限制之線上主題誠實標記為缺口（保持現有非 complete 狀態），未擅自虛構未核實之線上 API 簽名或執行求解運算。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/primemesh_module_conversion_report_20261104.md)。
