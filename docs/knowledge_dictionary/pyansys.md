# PyAnsys 生態系字典

本頁是 PyAnsys umbrella 文件與套件選擇導覽。官方 stable 安裝頁的 **Online installation** 明示 metapackage **2026.1.3**；這是頁面所列版號，不能推作本機已安裝版本。官方 umbrella 網頁和本機 Developer Portal 快照沒有可套用到所有 Ansys 產品的 release，因此本地來源清冊對這些文件保留 `unknown`。各 client library 的 API、產品版本與執行協定仍依產品字典和套件自己的文件判定。官方網站內容於 2026-11-03 線上核讀；以下是章節摘要，官方 HTML 未保存成本機全文，stable/dev 頁面可能變動。

## 本機來源與 PDF／HTML 轉換狀態

PyAnsys 資料夾只有 Markdown：兩份來自同一 Developer Portal URL 的正文快照，以及一份 `INDEX_SPHINX.md` 模板，另有 README。三筆 catalog 檔案 SHA-256 都與原件相符，沒有本機 PDF／HTML 輸入可補轉。README 顯示 3 files／1 body；catalog 實際列 2 筆 `body_present`、1 筆 `template`，兩種計數口徑差異保留。

`INDEX_SPHINX.md` 含 Jinja、raw HTML、`toctree` 和尚未代入的 `project_context` metadata，不能把它視為已渲染的離線 Projects/API 手冊。官方網站本輪只核對下列有界章節摘要；HTML 全文、圖表、動態清單均沒有本機快取，無法視為可離線全文檢索或逐字核對。

來源：[Portal 快照](../ANSYS_Document/PyAnsys/unknown/guide/a6de8909a528-pyansys.md)（[清冊](sources.csv#ansys_b6f5b288bcbc7efd8e1ea099)）、[Overview](../ANSYS_Document/PyAnsys/unknown/guides_and_tutorials/OVERVIEW.md)（[清冊](sources.csv#ansys_153f7207a7229ed89e2a59fb)）、[Sphinx 模板](../ANSYS_Document/PyAnsys/unknown/guides_and_tutorials/PyAnsys_Docs/INDEX_SPHINX.md)（[清冊](sources.csv#ansys_26629b48eddf9c4b87303fbc)）。原 Portal URL 直接開啟回 Cache miss，本機快照保留。

## PyAnsys、wrappers 與 tools

PyAnsys 是多套 Python libraries／tools 的集合，提供模擬自動化、資料處理與跨產品工作流入口。About 將生態分成 **wrappers**（產品介面）與 **tools**（附加功能），並以 gRPC 說明 wrapper 的遠端連線模型。這是 umbrella 頁的分類描述；本頁未逐一核驗所有 client 的通訊方式，不能由它推定每個 library 都使用 gRPC。

About 也說 metapackage 協調旗下專案的安裝相容性；這段敘述不是逐產品 server／license／平台支援矩陣。

來源：[About／The PyAnsys ecosystem](https://docs.pyansys.com/version/stable/getting-started/about.html#the-pyansys-ecosystem)（`Wrappers`、`Tools` 段落；[清冊](sources.csv#official_pyansys_about_stable)）、[首頁](https://docs.pyansys.com/version/stable/)（只作入口定位；[清冊](sources.csv#official_pyansys_home_stable)）。頁面將 wrappers 描述為直接連接 Ansys products 並經 gRPC 通訊；該段不構成每個獨立 library API 或傳輸方式的逐項驗證。

## Projects 的產品路由與開源工具

Projects 頁提供 **Product families** 與 **Tags**。以下只保留入口示例，不當作全部套件清單，也不固定網站 stars 或 project 數量。

| 想找的產品／工作 | Projects 入口示例 | 本機產品字典 |
| --- | --- | --- |
| MAPDL | PyMAPDL | [MAPDL](mapdl.md) |
| Fluent | PyFluent | [Fluent](fluent.md) |
| Electronics Desktop | PyAEDT | [AEDT](aedt.md) |
| DPF 資料處理 | PyDPF - Core | [DPF](dpf.md) |
| Mechanical | PyMechanical | [Mechanical](mechanical.md) |
| Geometry service | PyAnsys Geometry | [Geometry](geometry.md) |
| optiSLang | PyOptislang | [optiSLang](optislang.md) |

Open-source contributions 頁另外列開發工具和 shared infrastructure，例如 Sphinx Theme、GitHub Actions、repository templates；頁面明確區別這些工具與 simulation interfaces。某個工具出現在 umbrella 網站，不表示它提供產品求解 API。

來源：[Projects](https://docs.pyansys.com/version/stable/projects.html#projects)（`Product families`／`Tags` 以及各 project 卡片；[清冊](sources.csv#official_pyansys_projects_stable)）、[Open-source contributions](https://docs.pyansys.com/version/stable/other-contribs.html#open-source-contributions)（頁首說明及工具清單；[清冊](sources.csv#official_pyansys_open_source_contribs_stable)）。網站會更新項目與卡片內容，此處不記 stars 或宣稱為完整產品清單。

## Getting started 與 Python 前置條件

Getting started 入口依序連到 About、Prerequisites、Install。Prerequisites 的一般前提包括可用 Python 與合法 Ansys 授權；實際 library 需要的產品安裝、服務、授權及平台仍查該套件文件。

Prerequisites 表格的 metapackage **2026.1** 宣告 Python 範圍為 `>=3.10, <4`。同頁說明 SPEC-0 支援政策，也提醒第三方相依可能延後支援／淘汰；本頁不把寬鬆版本範圍視為每個 SDK 已測試 Python 版本。

本次於 2026-11-03 重讀官方 stable 頁面：圖表把 Python 3.10–3.14 列為支援中，Python 3.15 列為尚未支援。頁面明示新版本採用及淘汰時間僅屬暫定，可能因第三方相依延後；不要只以 metapackage 宣告的 `<4` 推定 Python 3.15 已支援，也不要將 umbrella 範圍外推到個別 SDK。這是頁面當次狀態，不是對所有 PyAnsys 套件逐一測試。

來源：[Getting started](https://docs.pyansys.com/version/stable/getting-started.html#getting-started)（入口的 About／Prerequisites／Install 導覽；[清冊](sources.csv#official_pyansys_getting_started_stable)）、[Prerequisites](https://docs.pyansys.com/version/stable/getting-started/prerequisites.html#prerequisites)（Python、Ansys 授權前提）、[Supported Python versions](https://docs.pyansys.com/version/stable/getting-started/prerequisites.html#supported-python-versions)（SPEC-0 圖與 metapackage 表；[清冊](sources.csv#official_pyansys_prerequisites_stable)）。

## metapackage 2026.1.3 與 additional targets

安裝頁以 `python -m pip install pyansys` 安裝 metapackage，並明示 2026.1.3 的 dependency 清單。四個 pin 樣本為 `ansys-mapdl-core 0.73.1`、`ansys-fluent-core 0.39.0`、`ansys-mechanical-core 0.12.10`、`ansys-optislang-core 1.5.0`；它們不是本機安裝結果，也不能取代各產品字典記錄的 SDK 版本。

| Additional target | 本頁核對的用途 |
| --- | --- |
| `mapdl-all` | 加入 MAPDL Reader |
| `fluent-all` | 加入 Fluent Visualization |
| `tools` | 加入 tools／units 等附加套件 |
| `all` | 加入該頁所有額外 targets 的附加項 |

來源：[Online installation](https://docs.pyansys.com/version/stable/getting-started/install.html#online-installation)（安裝指令及 2026.1.3 dependency 表）、[Additional targets](https://docs.pyansys.com/version/stable/getting-started/install.html#additional-targets)（targets 及其套件表；[清冊](sources.csv#official_pyansys_install_stable_2026_1_3)）。所列 pin 僅為 2026-11-03 線上頁面內容；本輪沒有安裝或更新任何套件。

## 離線 wheelhouse 流程

安裝頁的離線步驟是依 OS／Python 版本挑 wheelhouse artifact、解壓、再讓 pip 從本機 wheelhouse 以 `-f` 與 `--no-index` 取套件。該頁的 artifact 表列 Windows、macOS、Linux 及 Python 3.10–3.14。這是下載入口範圍，沒有證明每個 Ansys 產品或每個 SDK 都支援該組合。

來源：[Offline installation](https://docs.pyansys.com/version/stable/getting-started/install.html#offline-installation)（平台／Python wheelhouse 表及 `pip -f wheelhouse --no-index` 指令；[清冊](sources.csv#official_pyansys_install_stable_2026_1_3)）。wheelhouse 未下載，離線安裝未執行；表格列出下載 artifact 的組合，不代表所有套件已對每個組合驗證。

## 專案、套件與產品版本

命名指南區別 project name（如 `PyMAPDL`）、repository name（如 `pymapdl`）和 distribution name（如 `ansys-mapdl-core`）；namespace 以 `ansys` 組織。低階 gRPC API package 另採 `ansys-api-<product/service>` 規則，不能把它與高階 client 當成同一 API 層。

Releasing 頁說明 library 採 Semantic Versioning 並在產品週期外發行。因此本字典分開記錄 metapackage、client library 與產品 release，不用 SDK 版號猜測 Ansys 安裝版號。

來源：[Project structure／Naming convention](https://dev.docs.pyansys.com/packaging/structure.html#naming-convention)（PyAnsys library 與 gRPC interface package 命名；[清冊](sources.csv#official_pyansys_project_structure)）、[Releasing／Semantic versioning](https://dev.docs.pyansys.com/how-to/releasing.html#semantic-versioning)（X.Y.Z 定義、0.x API 穩定性提醒，以及 library 版號不應匹配產品版號；[清冊](sources.csv#official_pyansys_releasing)）。

## stable／dev 文件與相容性檢查

有 multi-version 文件的 library 可用 `version/stable` 查穩定版、`version/dev` 查開發版，並可用版本選單挑特定版本。`stable` 是會變動的文件通道；閱讀 API 時仍核對頁面版號。

Product compatibility 指南用 minimum version data、`VERSIONS_MAP`、`version_requires` 說明部分 library 的 server 功能檢查模式，並討論 maximum-version 邏輯。這是建庫建議與示例，不是所有 libraries 已採用的保證；方法存在與否仍查個別 API。

來源：[Documenting](https://dev.docs.pyansys.com/how-to/documenting.html#documenting)（文件來源、建立與部署說明；個別 multi-version 文件的 version URL 按各 library 設定而異，不能僅由本頁推定所有 library 都有 `stable`／`dev`；[清冊](sources.csv#official_pyansys_documenting)）、[Product compatibility](https://dev.docs.pyansys.com/how-to/compatibility.html#product-compatibility)（`check_version.py`、`VERSIONS_MAP`、`version_requires` 的建議示例；頁面明說目前尚無 maximum-version 實作，故不應表述成已具備功能；[清冊](sources.csv#official_pyansys_product_compatibility)）。

## Developer guide 與 CLA 入口

Developer guide 面向維護 library 的開發者、外部貢獻者和想理解專案組織的讀者；首頁列出 project organization、how-to、packaging、coding、documentation 等入口。各 PyAnsys project 的 user guide／API reference／examples 需從該 project 文件進入；本 umbrella guide 不是個別 API 參考。

本機 Developer Portal 快照及線上 Individual CLA 頁均說明：貢獻需有已簽署、存檔的 CLA。此處只摘要是否需 CLA，不摘要完整授權條款，也未簽署或提交貢獻。

來源：[Developer guide](https://dev.docs.pyansys.com/#pyansys-developer-s-guide)（首頁適用對象與指南範圍；[清冊](sources.csv#official_pyansys_developer_guide)）、[Individual CLA](https://cla.developer.synopsys.com/)（頁首 CLA on file 條件；[清冊](sources.csv#official_pyansys_individual_cla)）。CLA 是法律文件摘要，使用前應閱讀現行完整條款。

## 尚未覆蓋

完整 library API、逐套件 Python／OS 支援矩陣、每一個 client 的協定、所有 tutorials／圖表和 live stable 全文尚未離線整理。官方網頁雖在線核讀，來源清冊沒有對應 HTML 正文與 hash，無法本地重現每個細節；上述版本、平台表與產品卡片均以核讀日期為限。這些缺口保留在 `PyAnsys libraries 生態與用途` 的 `source_limited` 主題，不能由本頁路由示例視為完成。


## 2026-11-04：Wave 10 本機來源盤點與限制說明

本批完成 pyansys 模組既有本機 catalog 文件（共 3 筆）與 sources 清冊（共 16 筆）之完整雜湊、正文路徑與標籤結構核對。本機未快取或具備企業授權/登入限制之線上主題誠實標記為缺口（保持現有非 complete 狀態），未擅自虛構未核實之線上 API 簽名或執行求解運算。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/pyansys_module_conversion_report_20261104.md)。
