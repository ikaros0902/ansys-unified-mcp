# TurboGrid／PyTurboGrid 知識字典

> 範圍：本字典依本機來源清冊收錄的 PyTurboGrid 0.9.4 stable 文件及其範例整理。`stable` 網址會隨官方文件更新；清冊的產品版本欄為 `unknown`，不可據此推定 TurboGrid 桌面版版本。未執行任何範例或求解。

## 主題與來源狀態

| 主題 | 狀態 | 已核對來源 | 範圍／缺口 |
| --- | --- | --- | --- |
| 安裝、Python 與 TurboGrid 需求 | 已整理 | Getting started | 文件明列 Python 3.9–3.12、Windows/Linux、TurboGrid 2023 R2 或更新；沒有驗證其他版本。 |
| 啟動、讀取 INF、產生與保存網格 | 已整理 | Basic mesh generation | 一個 Rotor 37 示範流程；未執行，也不代表生產模型的完整流程。 |
| 多列葉片與 MBR | 部分整理 | MBR from TGInit、STAC | 覆蓋 NDF 到 TGInit 範例及 STAC TGMachine 工作流；完整 MBR API／生命週期缺少參考。 |
| 網格統計 | 部分整理 | Basic mesh generation | 範例只呼叫 `query_mesh_statistics()` 並列印回傳值；欄位定義、單位及品質門檻未收錄。 |
| API 參考 | 部分整理 | 官方 launcher、multi_blade_row、mesh_statistics 與 PyTurboGrid API 頁 | 本機只有索引 HTML/Markdown；線上模組頁已抽查但未下載納入本機索引。 |
| 其他範例 | 待補 | Examples 索引 | 官方索引列六項，目前本機只收錄其中三項正文及對應附件；另外三項是缺口。 |

## 安裝與執行前提

官方 PyTurboGrid 0.9.4 Getting started 指南表示：`ansys-turbogrid-core` 支援 Python 3.9、3.10、3.11、3.12，平台為 Windows 與 Linux；執行時需要本機安裝且具有合法授權的 Ansys TurboGrid 2023 R2 或更新版本。Windows 安裝程式會設定 `AWP_ROOTxxx`；Linux 範例需自行設定，例如 TurboGrid 2023 R2 使用 `AWP_ROOT232`。上述是該版指南記載的需求，不構成對每一個較新宿主版本的相容性驗證。

安裝命令（官方文件原文）：

```console
python -m pip install -U pip
python -m pip install ansys-turbogrid-core
```

PyTurboGrid 採 client-server 架構，指南稱通訊基於 plain TCP/IP；使用者透過 Python API 操作，不需自行實作通訊。PyTurboGrid 採 MIT 授權，但 TurboGrid 本體使用仍需合法授權。授權說明不能延伸為對原始文件或範例內容可任意再散佈的許可。

## 基本網格生成：Rotor 37

官方 `Basic mesh generation` 範例描述一條簡化流程：啟動 TurboGrid、定位安裝目錄內的 `examples`、讀取 Rotor 37 的 BladeGen INF、解除 `/TOPOLOGY SET` 暫停以產生預設網格、查詢統計、存成 `.gtm`，最後結束工作階段。

```python
from ansys.turbogrid.core.launcher.launcher import (
    get_turbogrid_exe_path,
    launch_turbogrid,
)

turbogrid = launch_turbogrid()
turbogrid.read_inf("<TurboGrid examples>/rotor37/BladeGen.inf")
turbogrid.unsuspend(object="/TOPOLOGY SET")
stats = turbogrid.query_mesh_statistics()
turbogrid.save_mesh(filename="rotor37.gtm")
turbogrid.quit()
```

範例還示範用 `get_turbogrid_exe_path()` 找出安裝位置，再組合 `examples/rotor37/BladeGen.inf` 路徑。上述範例以安裝隨附範例檔為前提；實際路徑與輸出需依環境確認。文件沒有給出通用網格品質門檻，因此本字典不提供面角、縱橫比或膨脹率的判定值。

## 多列葉片工作流

### 從 NDF 取得 TGInit

`Multi blade row meshing example` 使用 `multi_blade_row` 類別別名 `MBR`，以安裝包中的 `tests/ndf/AxialFanMultiRow.ndf` 呼叫 `convert_ndf_to_tginit()`，並呼叫 `get_blade_rows_from_ndf()` 取得列資訊。頁面稱此例會平行執行多列網格作業，但本機保存的正文只展示初始化與 NDF 轉換/列出 blade rows 片段；沒有後續網格呼叫、效能數據或同步行為細節。

### 由 TGMachine 初始化與尺寸設定

`Multi-blade STAC example` 以 `MBR()` 建立物件，使用 `init_from_tgmachine(tgmachine_path=...)` 載入 STAC 的 `.TGMachine`。範例說明該檔案列出各列 INF 路徑（順序需正確），INF 中提供曲線路徑。其後透過 `mbr.tg_worker_instances["S1.inf"].pytg` 等列別物件呼叫 `set_obj_param()`，設定 `/MESH DATA` 的 spanwise element 選項與元素數，再解除 `/TOPOLOGY SET`。

同一範例示範 `MachineSizingStrategy.MIN_FACE_AREA`、`set_machine_size_factor(0.2)`、`get_element_counts()` 與 `save_meshes()`。原文描述此策略嘗試讓各列元素尺寸一致，並允許列間網格平順轉換；也提及可改用目標節點數。這是範例用法，不足以推導所有模型適用的策略或品質保證。

該頁註記 `mbr.tg_worker_instances = None` 是當時範例為了關閉 worker 的 workaround，並說預期後續版本修正為 `mbr.quit()`。這是版本敏感且有副作用的操作，不宜直接當作通用清理 API；應先查目標版本的正式 API 文件，必要時以受控範例驗證。

## API 快速參照（官方線上模組頁抽查）

本機 HTML/Markdown 只含 API 索引導言，但索引連到官方模組頁。抽查 `launcher`、`multi_blade_row`、`mesh_statistics` 和 `pyturbogrid_core` 後，可確認以下有限資訊：

- `get_turbogrid_exe_path(**launch_argvals)` 的安裝路徑搜尋順序為：參數 `turbogrid_path`、環境變數 `PYTURBOGRID_TURBOGRID_ROOT`、參數 `product_version` 對應的 `AWP_ROOTxxx`、最新已安裝版本的 `AWP_ROOTxxx`。
- `launch_turbogrid()` 的官方簽章含 `product_version`、`turbogrid_path`、logging 及 host/port 等參數；`port=None` 時文件稱會自動選用可用連接埠，預設 host 為 `127.0.0.1`。需依目標版 API 頁確認完整簽章，不宜把啟動的內部通訊實作當成用戶設定需求。
- `TurboGridVersion` 列出 23R2、24R1、24R2、25R1、25R2、26R1、27R1。這反映目前 stable API 文件的 enum 清單，不代表每一組宿主/API/作業系統組合都已驗證相容。Getting started 仍以「TurboGrid 2023 R2 或更新」描述需求。
- `MachineSizingStrategy.NONE` 代表不套用自動策略，需人工控制列尺寸；`MIN_FACE_AREA` 以最小面積 blade row 作目標嘗試讓元素尺寸一致，官方也警告較大列可能因此產生大量元素。`multi_blade_row` API 還列出 `init_from_ndf`、`init_from_tgmachine`、`get_all_worker_errors`、`get_element_counts`、`quit` 等方法；本文未逐一整理其所有參數。
- `MeshStatistics` 可針對目前 session/domain 取得統計、產生 histogram、將表格輸出 CSV；部分方法讀取快取統計，`update_mesh_statistics()` 會重新讀取。變數清單與品質閾值未在本次確認。

官方 module URL：[launcher](https://turbogrid.docs.pyansys.com/version/stable/api_reference/launcher.html)、[multi_blade_row](https://turbogrid.docs.pyansys.com/version/stable/api_reference/multi_blade_row.html)、[mesh_statistics](https://turbogrid.docs.pyansys.com/version/stable/api_reference/mesh_statistics.html)、[pyturbogrid_core](https://turbogrid.docs.pyansys.com/version/stable/api_reference/pyturbogrid_core.html)。`ndf_parser` 頁在 stable 網址下回報 PyTurboGrid 0.6.0 文件標頭，而其他抽查頁標示 0.9.4；此版本標示不一致列為來源缺口，不能默認其內容就是 0.9.4 契約。

## API 與範例覆蓋界線

本機 API reference 頁只有索引簡介；目前線上 API 模組頁有進一步說明，但尚未抓取成可離線檢索的正文。因此 `launch_turbogrid`、`read_inf`、`unsuspend`、`query_mesh_statistics`、`save_mesh` 等只能按已查核的官方範例或模組頁內容解讀，不可據此補出未檢查方法的完整簽章、例外或跨版本契約。

官方 Examples 索引列出六項：Basic mesh generation、Multi-blade STAC example、Multi blade row meshing example、MBR sweep、Mesh statistics report、Multi blade row batch example。本機只保存前三項的 HTML/Markdown 正文；其餘三項正文與下載附件未在清冊中，列為待補。另本機保存的附件為前三個已收錄範例的 `.py` 與 `.ipynb`；本次沒有執行。

## 來源與追溯

主要來源均為官方 PyAnsys TurboGrid 文件站 `https://turbogrid.docs.pyansys.com/version/stable/`，來源 ID、原始 HTML、sidecar、SHA-256 與處理狀態見同目錄的 `docs/maintenance/knowledge_dictionary_passes/2026-11-02/turbogrid_sources.csv`。

| 主題 | 官方頁面 |
| --- | --- |
| 入門、安裝及需求 | [Getting started](https://turbogrid.docs.pyansys.com/version/stable/getting_started/index.html) |
| API 索引 | [API reference](https://turbogrid.docs.pyansys.com/version/stable/api_reference/index.html) |
| 範例索引 | [Examples](https://turbogrid.docs.pyansys.com/version/stable/examples/index.html) |
| Rotor 37 | [Basic mesh generation](https://turbogrid.docs.pyansys.com/version/stable/examples/basic_read_inf_rotor37.html) |
| TGInit / NDF | [Multi blade row meshing example](https://turbogrid.docs.pyansys.com/version/stable/examples/mbr_from_tginit_example.html) |
| STAC / TGMachine | [Multi-blade STAC example](https://turbogrid.docs.pyansys.com/version/stable/examples/mbr_STAC_Example.html) |

官方頁另連到 [PyAnsys](https://docs.pyansys.com)、[PyAnsys Developer's Guide](https://dev.docs.pyansys.com/)、[PyTurboGrid GitHub repository](https://github.com/ansys/pyturbogrid)、[Ansys TurboGrid 產品頁](https://www.ansys.com/products/fluids/ansys-turbogrid) 及 STAC 案例頁 [University of Stuttgart ITSM](https://www.itsm.uni-stuttgart.de/en/research/test-cases/STAC/)（DOI: [10.1177/0957650919833207](https://doi.org/10.1177/0957650919833207)）。這些連結只作來源導覽；外部頁面未納入本文逐頁整理。

## 驗證紀錄與尚未完成

- 已核對 13 個 catalog 項目及 13 個原始檔 SHA-256：7 個 HTML 正文均有非空 Markdown sidecar；6 個 Python/Jupyter 附件均存在且雜湊符合清冊。
- PDF：TurboGrid 本批清冊未列 PDF，故無 PDF 轉換項目。
- HTML：7 個本機正文皆為 HTML 轉換內容。已逐份確認文件標題與正文主旨，並以 Getting started 和兩個 MBR 頁面對照可讀取的官方頁；沒有對所有 HTML 節點作逐字比對。圖片只以 HTML 的 alt/連結線索保留，圖像內容未轉成文字。
- 附件：6 個範例附件有原始程式碼，但未建立其 Markdown 衍生檔，也未執行；Jupyter 輸出或隱含資料未另行核對。
- 網站擴展：本次由官方索引向其列出的已知頁面整理；沒有全面爬取其他官方技術頁。清冊已有的來源皆官方站點，未發現第三方正文。
- 搜尋與片段擷取：以唯讀 SQLite FTS 查詢現有索引，`AWP_ROOT232`、`query_mesh_statistics`、`set_machine_size_factor`、`convert_ndf_to_tginit` 四項均命中相符的 TurboGrid catalog 文件；逐筆取回命中 chunk 並確認內含查詢詞及可追溯的官方 `source_url`。此為索引資料庫唯讀查核，沒有呼叫可能重建資料庫的工具入口。索引快照早於本次字典修訂，故新字典尚未被索引；線上 API 模組頁也尚未進入本機 catalog/索引。細節見 pass 記錄。
- 未整理 API 詳細頁、MBR sweep、mesh statistics report、MBR batch example；沒有驗證各產品版本差異或範例在現場安裝環境中的可執行性。


## 線上補讀：三個官方範例（2026-11-03）

以下內容依官方 stable 範例頁整理；頁面標示 PyTurboGrid 0.9.4。這些頁面正文可線上讀取，但本次未將 HTML 或範例附件下載到本機 catalog／索引，也未執行程式。`stable` 網址會更新，使用時應再核對目標 SDK 版本。

### MBR 尺寸參數 sweep

[Multi blade row meshing example — sweep](https://turbogrid.docs.pyansys.com/version/stable/examples/mbr_sweep_example.html) 以 `MBR()` 及 `init_from_ndf()` 載入 Concepts NREC 的 `AxialFanMultiRow.ndf`，取得 blade row 名稱與平均 base-face area，套用 `MachineSizingStrategy.MIN_FACE_AREA`。範例依序將 global size factor 設為 `1`、`1.5`、`2`，讀取各列平均 base-face area 與 element counts，並列印執行時間與結果。這是參數掃描示範，未提供通用最佳值或品質門檻；程式呼叫與執行時間未實測。

### 網格統計 HTML 報告

[Mesh statistics report](https://turbogrid.docs.pyansys.com/version/stable/examples/mesh_statistics_report.html) 示範以 Rotor 37 網格建立報告：用 CCL `DOMAIN` 物件查詢域名稱，逐域及 `ALL` 呼叫 `update_mesh_statistics()`，讀取統計與 `get_table_rows()`；再針對 `Minimum Face Angle`、`Skewness` 產生百分比 histogram。Jinja2 讀取 `report_template.html`，把 case details、各域統計、表格資料和圖檔路徑帶入模板，輸出 `tg_report.html`。原文要求先安裝 Jinja2，且模板須從 PyTurboGrid 原始碼 examples 取得或下載；本地尚無該範例頁連結的模板／附件副本。範例列出量測欄位，並未給出可普遍適用的合格門檻。

### 多列批次網格

[Multi blade row meshing example — batch](https://turbogrid.docs.pyansys.com/version/stable/examples/multi_blade_row_batch_example.html) 使用 `MultiBladeRow`（`multi_blade_row_batch` 模組），以工作目錄、測試資料目錄與 `AxialFanMultiRow.ndf` 建立執行個體；範例設定 spanwise counts `56, 73`、global size factor `1.5`、blade boundary layer offsets `6e-6`，最後呼叫 `execute()`。範例描述為平行執行多列網格，但頁面沒有在這段程式中展示 worker 設定、錯誤復原或效能比較；上述數值只是範例輸入，不是建議值。



## 本機 tutorial 附件文字補件

三組教學的 Notebook 與 Python 原始檔各有一份，共六份；以下補件保留原始程式及 Notebook 的 Markdown／code cells，並連回原始附件與來源 ID。Notebook 的執行輸出、圖片及其他附件未擷取；版本欄仍為 unknown，未執行範例。

- [basic_read_inf_rotor37.ipynb](ANSYS_Document/turbogrid_example_inputs_20261104/tutorial/ansys_213e2c51b26c7b9e5680e1b8/turbogrid.md)（`sources.csv#ansys_213e2c51b26c7b9e5680e1b8`）
- [basic_read_inf_rotor37.py](ANSYS_Document/turbogrid_example_inputs_20261104/tutorial/ansys_0f221ff88b61c79b703d08e3/turbogrid.md)（`sources.csv#ansys_0f221ff88b61c79b703d08e3`）
- [mbr_from_tginit_example.ipynb](ANSYS_Document/turbogrid_example_inputs_20261104/tutorial/ansys_7bd8e0f82a11dff42413083b/turbogrid.md)（`sources.csv#ansys_7bd8e0f82a11dff42413083b`）
- [mbr_from_tginit_example.py](ANSYS_Document/turbogrid_example_inputs_20261104/tutorial/ansys_10fe5c536b46b3b2934e0530/turbogrid.md)（`sources.csv#ansys_10fe5c536b46b3b2934e0530`）
- [mbr_STAC_Example.ipynb](ANSYS_Document/turbogrid_example_inputs_20261104/tutorial/ansys_a7477f532e26fcfa62d1a94d/turbogrid.md)（`sources.csv#ansys_a7477f532e26fcfa62d1a94d`）
- [mbr_STAC_Example.py](ANSYS_Document/turbogrid_example_inputs_20261104/tutorial/ansys_65afd18022a1fce7b9b5ed94/turbogrid.md)（`sources.csv#ansys_65afd18022a1fce7b9b5ed94`）

逐檔來源與補件 SHA、cell 數見 [轉換清冊](../maintenance/knowledge_dictionary_passes/2026-11-04/turbogrid_attachment_text_recovery.csv)；其他三個僅在線上索引中列出的範例仍未完整取得。


## 2026-11-04：官方範例與 API 正文轉換

本批 13 筆 catalog（7 HTML、6 附件，沒有 PDF）原件 hash 及 7 正文 metadata 已核對；7 HTML 的程式區塊逐字保留。六個既有附件補件的來源 hash、Notebook 15 code／17 Markdown cells 及 Python 全文核對後沿用，不重新轉檔。圖片、Notebook outputs 與範例執行未驗收。

原先三個範例及五個 API 線上來源現已保存原始 HTML／Markdown 並索引，下表更新前文「尚未快取」的狀態。SDK 版本以取得頁面的 title 為準，產品 release 仍 unknown；`stable` 不是固定版本快照，0.6.0 與 0.9.4 不視為可互換契約。

| 文件 | SDK 頁標 | 本機正文 | 來源 ID |
| --- | --- | --- | --- |
| [launcher — PyTurboGrid 0.9.4 documentation](https://turbogrid.docs.pyansys.com/version/stable/api_reference/launcher.html) | 0.9.4 | [launcher](ANSYS_Document/TurboGrid/sdk_0.9.4/official_body_20261104/launcher.md) | `sources.csv#web_api_launcher` |
| [mesh_statistics — PyTurboGrid 0.9.4 documentation](https://turbogrid.docs.pyansys.com/version/stable/api_reference/mesh_statistics.html) | 0.9.4 | [mesh_statistics](ANSYS_Document/TurboGrid/sdk_0.9.4/official_body_20261104/mesh_statistics.md) | `sources.csv#web_api_mesh_statistics` |
| [multi_blade_row — PyTurboGrid 0.9.4 documentation](https://turbogrid.docs.pyansys.com/version/stable/api_reference/multi_blade_row.html) | 0.9.4 | [multi_blade_row](ANSYS_Document/TurboGrid/sdk_0.9.4/official_body_20261104/multi_blade_row.md) | `sources.csv#web_api_multi_blade_row` |
| [pyturbogrid_core — PyTurboGrid 0.9.4 documentation](https://turbogrid.docs.pyansys.com/version/stable/api_reference/pyturbogrid_core.html) | 0.9.4 | [pyturbogrid_core](ANSYS_Document/TurboGrid/sdk_0.9.4/official_body_20261104/pyturbogrid_core.md) | `sources.csv#web_api_pyturbogrid_core` |
| [ndf_parser — PyTurboGrid 0.9.4 documentation](https://turbogrid.docs.pyansys.com/version/stable/api_reference/ndf_parser.html) | 0.9.4 | [ndf_parser](ANSYS_Document/TurboGrid/sdk_0.9.4/official_body_20261104/ndf_parser.md) | `sources.csv#web_api_ndf_parser` |
| [Multi blade row meshing example — PyTurboGrid 0.9.4 documentation](https://turbogrid.docs.pyansys.com/version/stable/examples/mbr_sweep_example.html) | 0.9.4 | [mbr_sweep_example](ANSYS_Document/TurboGrid/sdk_0.9.4/official_body_20261104/mbr_sweep_example.md) | `sources.csv#official_turbogrid_094_mbr_sweep_example` |
| [Mesh statistics report — PyTurboGrid 0.9.4 documentation](https://turbogrid.docs.pyansys.com/version/stable/examples/mesh_statistics_report.html) | 0.9.4 | [mesh_statistics_report](ANSYS_Document/TurboGrid/sdk_0.9.4/official_body_20261104/mesh_statistics_report.md) | `sources.csv#official_turbogrid_094_mesh_statistics_report` |
| [Multi blade row meshing example — PyTurboGrid 0.9.4 documentation](https://turbogrid.docs.pyansys.com/version/stable/examples/multi_blade_row_batch_example.html) | 0.9.4 | [multi_blade_row_batch_example](ANSYS_Document/TurboGrid/sdk_0.9.4/official_body_20261104/multi_blade_row_batch_example.md) | `sources.csv#official_turbogrid_094_multi_blade_row_batch_example` |

本批八頁 title 均顯示 SDK 0.9.4；先前線上摘要記錄 ndf_parser 為 0.6.0，本輪同一 stable URL 已顯示 0.9.4。歷史摘要保留，因沒有舊原頁快照，不能判定差異原因或推定兩版本相容。上述保存全文不代表完整 API 契約、版本相容矩陣或現場可執行性已驗證。三個新範例的下載 Python／Notebook／zip、報告模板和外連圖片仍未下載；既有六附件之外的資料需求列缺口。詳[批次報告](../maintenance/knowledge_dictionary_passes/2026-11-04/turbogrid_module_conversion_report_20261104.md)。
