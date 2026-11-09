# Ansys Solution Application Framework (SAF) 字典

> 2026-11-02 核讀：本機保留兩份 Developer Portal Markdown 快照；本輪另讀取公開的 SAF developer's guide HTML，整理下列有界摘要。官方 URL 使用 `version/stable`，未確認 SAF 套件版號與產品 release，因此維持 unknown。線上指南全文尚未本機快取；完整 API、部署套件與執行相容性仍有缺口。

## 用途與官方入口

SAF SDK 是 Python framework，用於建立自訂 Ansys solution web applications（亦稱 solutions／vertical apps）與 guided-workflow simulation applications；應用範圍可從單一表單到多求解器工作流。官方首頁目前可公開讀取，並提供 Getting started、User guide、Examples 與 Deployment 入口。舊快照列出的 AEDT、ADR、DPF、Discovery、EnSight、Fluent、MAPDL、Mechanical、optiSLang、Prime Mesh、PyGeometry、System Coupling 是可延伸使用的產品 API／library 入口，個別產品版本仍須查其文件。[本機 Overview](../ANSYS_Document/SAF/unknown/guides_and_tutorials/OVERVIEW.md) · `ansys_3b11858ea6a6b3053fa508d8`；[本機 Portal 快照](../ANSYS_Document/SAF/unknown/guide/d891502b6303-saf.md) · `ansys_70b1de82951cb613c81719f7`；[SAF 首頁](https://saf.ansys.com/) · `official_saf_home`

## 1. Scaffold：建立 solution 與命名

`saf new` 由範本建立 solution 目錄，提示輸入 solution name、display name、UI framework 與 namespace；也可用 `--solution-name`、`--solution-display-name`、`--ui-framework`、`--namespace` 提供值。該頁 UI 選項為 `dash`／`none`，namespace 範例為 `saf.solutions`。solution name 不能是路徑，不能包含 `/`、`\`、`:`、`;`、`*`、`?`、`<`、`>`。[Scaffold，Create a solution／Solution naming conventions](https://saf.ansys.com/version/stable/user_guide/scaffold.html) · `official_saf_scaffold`

同一 stable 通道的範例預設名稱有差異：Quick-start 使用 `my-solution`，Scaffold 使用 `my_solution`。兩頁未在正文提供可對照的 SAF 套件版號，本頁保留差異，不認定其中一個是所有版本的固定預設。[Quick-start，Create a solution](https://saf.ansys.com/version/stable/getting_started/quick_start.html) · `official_saf_quick_start`

## 2. CLI 與 solution 環境、安裝清理參數

SAF CLI 的套件為 `ansys-saf-cli`；官方建議將 CLI 放在獨立 `.cli` virtual environment，與 solution 的 `.venv` 區分。`saf --version` 是文件列出的安裝確認入口。[SAF CLI](https://saf.ansys.com/version/stable/getting_started/prerequisites/saf_cli.html) · `official_saf_cli`

`saf install` 在 solution root 建立環境，使用 Poetry 安裝 `pyproject.toml` 定義的相依套件；`.poetry/.venv` 是 Poetry 自身環境，`.venv` 是 solution 環境。清理選項會刪除現有檔案，不能把它們解讀成單純更新依賴：

| 選項 | 官方列出的清理範圍 |
|---|---|
| `-f`／`--force-clear` | `.venv`、`.poetry/.venv`、`.poetry/.cache` |
| `-F`／`--force-clear-all` | 上述目錄及 `poetry.lock` |

兩種清理預設均停用。Quick-start 的 `saf install -f` 範例實際會觸發第一種清理。[Install，saf install options／Virtual environment installation](https://saf.ansys.com/version/stable/user_guide/install.html) · `official_saf_install`

## 3. 本機執行模式與專案建立

`saf run` 呼叫 SAF Desktop Orchestrator 啟動 solution stack。帶 UI 的預設模式會自動建立隨機名稱 project；Windows 使用 PyWebView，Linux 使用瀏覽器。常用選項如下：

| 選項 | 行為 |
|---|---|
| `--browser` | 在預設瀏覽器開啟 UI |
| `--portal` | 開啟專案管理 Portal UI |
| `--no-ui` | 不啟動 UI server |
| `--project <NAME>` | 開啟／建立指定 display name 的 project；Portal 執行時不可使用 |

較底層的 `glow_engine api` 與 `glow_engine ui` 分別啟動 backend／frontend；文件明列這兩種方式不會自動建立 project。兩者的生命週期與 `saf run` 不同。[Run a solution on desktop，Solution execution modes／The saf run command／GLOW CLI](https://saf.ansys.com/version/stable/user_guide/run_locally/run_desktop.html) · `official_saf_run_desktop`

## 4. 套件分工與 meta-package

| 元件 | 文件定義的責任 |
|---|---|
| `ansys-saf-glow-engine` | workflow／state 與 REST API 的核心 runtime；提供 persistence、transactions、telemetry 等功能 |
| `ansys-saf-cli` | scaffold、install、run、build 等開發生命週期入口 |
| `ansys-bdm-api` | 檔案／目錄儲存的抽象介面，以 `EntityHandle` 等型別連結應用與儲存 backend |
| `ansys-saf-product-manager` | 以 PyAnsys 為基礎的 product instance managers |

SAF 套件以協調組合發佈，`ansys-saf-sdk` meta-package 將經過驗證的一組套件版本固定成單一相依項；不能由本頁套件名稱推定個別 Ansys 產品 release。[SAF components，Components／Meta-package](https://saf.ansys.com/version/stable/user_guide/components.html) · `official_saf_components`

## 5. 支援版本快照與 Ubuntu 表格差異

以下是 2026-11-02 可讀官方頁的記載，代表該文件通道的測試範圍；尚未在本機執行確認。

| 項目 | 官方記載 |
|---|---|
| Python | 3.11、3.12、3.13、3.14 |
| Windows | 10、11、Server 2022 |
| Ubuntu：Prerequisites／Operating systems | 20.04、22.04 |
| Ubuntu：Supported software | 22.04、24.04 |
| AEDT、Fluent、Geometry、MAPDL、Mechanical | Supported software 表列 2025R1 SP4、2025R2 SP4 |
| optiSLang | 同表列 2024R2、2025R1 SP4、2025R2 SP4 |

Ubuntu 兩份表格互相不一致，且沒有可辨識的 release 對照；本頁不把兩者合併為 20.04–24.04 全支援。Supported software 將「supported」定義為 CI 已測試／驗證的組合，並要求新產品版本完成整合、測試與 SAF 套件發佈後，solution 才更新相依版本；表列 flagship 產品另需有效 Ansys license。[Python interpreter](https://saf.ansys.com/version/stable/getting_started/prerequisites/python_interpreter.html) · `official_saf_python_interpreter`；[Operating systems](https://saf.ansys.com/version/stable/getting_started/prerequisites/operating_systems.html) · `official_saf_operating_systems`；[Supported software](https://saf.ansys.com/version/stable/user_guide/supported_software.html) · `official_saf_supported_software`

## 6. Desktop 與 on-premises 部署範圍

Desktop deployment 供單一 Windows／Linux 機器的個人使用。安裝到 system-level 位置才需要管理員權限；Windows 指南另列 long paths 與 WebView2 前提。產物安裝器位於 solution root 的 `dist` 目錄。[Desktop deployment，Prerequisites／Installation](https://saf.ansys.com/version/stable/user_guide/deploy/desktop.html) · `official_saf_desktop_deployment`

On-premises deployment 是 enterprise feature，頁面標示限 Ansys customers／Channel Partners，部署套件與詳細文件須取得存取權。三種 flavor 為單台 Windows 的原生 Windows services、單台 Linux 的 Docker Compose containers，以及 K3s cluster／Helm；本頁只整理拓樸，未取得受控套件或驗證部署設定。[On-premises deployment](https://saf.ansys.com/version/stable/user_guide/deploy/on_premise.html) · `official_saf_on_premises_deployment`

## 7. Product Instance Management 的存取與檔案界線

PIM 讓 SAF 在 desktop、container 或遠端產品機器之間管理 product instance，也可在多次 transaction method 呼叫間共用 instance。產品產生的檔案不一定可由 solution 直接存取，程式不能假設產品與 solution 共用本機檔案系統。

該頁將 PIM 標為 enterprise feature，前提含已建立／安裝的 solution 與存取 PIM Light Server package 的 token。desktop PIM server 的兩條安裝途徑為同機 optiSLang `>=261` 內附，或經授權的私有套件來源加入 `ansys-saf-pim-light-server`；repository URL 由 SAF SDK team 提供，文件沒有公開固定值。本頁未建立 token、取得套件或啟動產品。[Instance management，Prerequisites／Install the PIM server](https://saf.ansys.com/version/stable/user_guide/backend/instance_management/index.html) · `official_saf_instance_management`

## 尚未覆蓋的來源範圍

本頁涵蓋入口、上述操作契約與限制；workflow/transaction API 的完整方法、BDM API、frontend callbacks、OIDC／HPS／Minerva 認證設定、project migration 及部署套件均未全量整理。Developer Portal live URL 本輪由 web 工具回覆 Cache miss，不能據此判定服務失效；兩份本機快照仍保留。官方線上來源目前只有本頁摘要進入待整合語料，全文本機快取、版本固定與分享權限仍需另外核對。


## 8. BDM 檔案與目錄生命週期

Blob Data Management（BDM）以 `EntityHandle` 參照已儲存的檔案或目錄；handle 是不可變參照，既有 blob 不應直接原地修改。要更新內容，先以 storage scope 的 `get_copy()` 複製至新檔、修改，再 `store()` 產生新 handle。後端可透過 transaction 的 `self.storage_scope` 操作，Dash client 使用 `project.storage_scope`；step 欄位以 `EntityHandle` 保存參照，尚未指向 blob 時可用 `NO_ENTITY`。檔案路徑是 staging／cache 位置，不能當成跨產品與部署環境的穩定識別。

BDM 範例指出該功能由 GLOW Engine 提供，SAF solution 預設可用。transaction 可以把 staged file／directory store 後寫入 step field；Dash callback 可用 client storage scope 取得或建立 handle，亦可依 step field 呼叫 `get_entity_url()` 取得 UI 可用 URL。method asset 則由 transaction 的 `get_asset_entity_handle()` 取得 handle。這些是官方範例的介面流程，未在本機執行或驗證特定套件版本。

來源：[BDM example](https://saf.ansys.com/version/stable/examples/data_file_management_examples/saf_ex_bdm.html) · `official_saf_bdm_example`；[Use BDM from the client (Dash)](https://saf.ansys.com/version/stable/user_guide/backend/blob_management/bdm_from_dash_client.html) · `official_saf_bdm_dash`。兩頁使用 `version/stable`，未列本機 SDK 版號；範例的 staging path 與應用部署的實體儲存位置不應混為同一種路徑契約。

## 9. API 驗證、角色與本機 API key 邊界

SAF GLOW 的 UI 與 API server（REST、GraphQL、WebSocket）及通往 HPS／Minerva 的互動使用 bearer access token；on-premises 範例以 OIDC／OAuth 2.0 身分提供者驗證 JWT。文件指出 `GLOW_AUTH_REQUIRED_ROLES`／`GLOW_AUTH_BYPASS_ROLES` 是 solution 全域存取角色，並不提供每個 project 的權限或 owner 隔離；獲准進入 solution 的使用者可讀寫其中任何 project。這項限制應納入權限模型設計，不可將登入角色視為 project-level authorization。

文件另列本機 Solution API 的 API key 模式：client 以 `x-api-key` 傳遞；只有來源為 `localhost`、`127.0.0.1` 或 `::1` 的請求才符合此認證方式，其他來源仍走標準 OIDC 驗證。未設定 key 或 key 不符時亦會回到 OIDC。key 可由 `GLOW_API_KEY` 或 `GLOW_API_KEY_FILE` 設定，兩者互斥；key-file 路徑需為存在的絕對路徑。這是限定本機來源的便利方式，不能推成遠端部署免驗證或可替代授權設計。本字典不複製文件中的佔位秘密值，亦未設定或測試任何認證。

來源：[Authentication and authorization](https://saf.ansys.com/version/stable/user_guide/backend/authn_authz/authentication.html) · `official_saf_authentication`。頁面屬 `version/stable`，未提供套件版號；部署變數行為與 project 權限邊界均未在本機環境實測。


## 10. 發佈型態與 IP 保護方式

SAF 的 IP protection 文件將保護方式依交付型態區分：桌面 installer 會分發到使用者機器，可在 `method_assets/obfuscate.txt` 列出需保護的 scripts／data，再以 `saf build --encrypt` 加密後包裝；文件稱這些 assets 在執行時於記憶體中解密，不寫回磁碟。On-premises 部署由客戶管理伺服器，使用者透過 browser／API 操作，不取得 server file system 的原始碼；文件將保護責任放在伺服器權限、network segmentation、containerization 及授權控制。

此頁標示 enterprise feature、限 Ansys customers／Channel Partners。上述是文件描述，不代表已驗證加密實作、保護強度、威脅模型或任何特定部署設定；取得功能及分享範圍須按授權核實。[IP protection](https://saf.ansys.com/version/stable/user_guide/backend/ip_protection.html) · `official_saf_ip_protection`。來源網址為 stable，無數字 SDK 版號；本文未執行 build 或檢查產物。


## 2026-11-04：Wave 10 本機來源盤點與限制說明

本批完成 saf 模組既有本機 catalog 文件（共 2 筆）與 sources 清冊（共 19 筆）之完整雜湊、正文路徑與標籤結構核對。本機未快取或具備企業授權/登入限制之線上主題誠實標記為缺口（保持現有非 complete 狀態），未擅自虛構未核實之線上 API 簽名或執行求解運算。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/saf_module_conversion_report_20261104.md)。
