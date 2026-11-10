# Ansys Speos 與 PySpeos 主題字典

本頁整理本機 `ansys-speos-core 0.9.2` 文件所述的 PySpeos client、Speos service 啟動方式及連線模式。清冊中的 Speos 產品 release 為 `unknown`；`version='251'` 是啟動範例，不能當作 SDK 0.9.2 的完整產品相容性聲明。

## PySpeos client 與 service backend
### SDK 與 Speos 產品版本界線

本機 HTML／Markdown 頁面標題顯示 ansys-speos-core 0.9.2，但 source URL 使用 version/stable；來源清冊的產品 release 為 unknown。因此可確認本機鏡像的 SDK 文件目錄版本，不能確認 stable URL 現在指向的 SDK 版本，也不能由此建立 SDK 與 Speos 產品 release 的相容矩陣。啟動指南的 version=251 範例表示 Ansys 2025 R1 服務版本示範，不等於 ansys-speos-core 0.9.2 的支援範圍。Launcher API 說明服務版本可由呼叫參數指定；未指定時依 launcher 類型由伺服器選擇，或在本機嘗試選用最新已安裝版本。這些是該 API 頁的行為說明，目標環境仍需核對實際安裝版本。

來源：[Getting started（本機 0.9.2 HTML／Markdown）](../ANSYS_Document/Speos/sdk/ansys-speos-core/0.9.2/guide/fcc92cbc5f0b-index.md)（[清冊](sources.csv#ansys_d7d772ed3b0b99b4a1e346b7)）；[launcher API（本機 0.9.2 HTML／Markdown）](../ANSYS_Document/Speos/sdk/ansys-speos-core/0.9.2/api_reference/ee132fdab849-index.md)（[清冊](sources.csv#ansys_5391299c7a8e23dc63f7ef74)）。


PySpeos 是 Python client library，透過 Speos service backend 使用 Speos 功能。Getting Started 列出三種服務取得方式：以 Docker container 啟動服務、透過 launcher 在本機或遠端啟動服務，或連接已經運行的服務。該文件將 Docker 列為偏好的高效能模式；部署方式仍須依支援的平台、授權及服務位置選擇。

| 模式 | 文件描述 | 核對事項 |
| --- | --- | --- |
| 本機 launcher | `launch_local_speos_rpc_server()` 啟動本機 RPC server，回傳 `Speos` session；文件範例以 `speos.close()` 結束 session。 | 範例的 `version='251'` 是版本參數示範，依實際安裝核對。 |
| Product Instance Management（PIM） | `launch_speos()`／`launch_remote_speos()` 透過產品執行個體管理啟動服務。 | 需先設定 PIM；遠端 launcher 文件要求 PyPIM 已設定。 |
| 既有服務 | 建立 `Speos()` client 連線到服務，提供正確 host／port 後可檢視 `speos.client` 狀態。 | 連線成功與服務健康狀態需由實際 client 回應確認。 |
| Docker service | PySpeos 可連接 Docker 中的 Speos service；本機文件描述 Linux service image。 | 官方頁指出映像檔下載僅提供給 Ansys organization 成員。 |

### Linux Docker service 前置、連接埠與傳輸安全

PySpeos 0.9.2 的 Linux Docker 指南要求服務端設定 `ANSYSLMD_LICENSE_FILE` 指向 license server；`SPEOS_LOG_LEVEL` 是選用項，預設值 `2` 對應 `INFO`。指南範例將 Docker host port `50098` 綁在 `127.0.0.1`，client 預設連到 `localhost:50098`；若更改 host 或 port，需同時調整 Docker port mapping 與 client 的 `default_docker_channel`。網路連接位置是 service host 的資訊，不因 client 在本機就保證遠端 service 可達。

| 傳輸模式 | 指南所列條件 | client／server 配對注意 |
|---|---|---|
| Mutual TLS (`--transport_tls`) | server 需提供 private key、certificate、server/client CA 路徑。 | client 端也須建立 TLS transport；兩端模式需相同。 |
| Unix Domain Socket (`--transport_uds`) | 用於本機 server/client 通訊，可指定 socket 路徑。 | 適用範圍受限於可共用該本機 socket 的環境。 |
| Windows Named User Authentication (`--transport_wnua`) | 僅 Windows 可用；指南說明未指定 transport 時為 Windows 預設，且 host 必須是 localhost。 | 只依該 Windows 條件使用；不可推定 Linux container 可提供 WNUA。 |
| gRPC insecure (`--transport_insecure`) | 指南 Docker 啟動範例使用此模式。 | 文件將其與 TLS 分列；範例的 insecure 設定不代表可安全暴露至不可信網路。 |

指南要求 PySpeos client 與 service server 使用相同 transport mode。另有兩處文件文字需保留為來源疑義：Docker overview 將 Linux service backend 連到一個「Build a Windows Docker container」連結；Linux container 頁稱範例為 Speos 2025.2，但示例 image tag 是 `261`，並另說可把 `252` 改成對應產品版本。本文不據這些文字推定 `261`、`252` 與 Speos release 的映射；取得映像權限及選標籤前，應核對目標版本的官方發布資訊。Linux service image 頁並限制下載給 Ansys organization 成員，且需 GitHub Container Registry package read 權限；本文不複製 token 操作範例或任何憑證。

來源：[Docker containers（PySpeos 0.9.2 頁面）](../ANSYS_Document/Speos/sdk/ansys-speos-core/0.9.2/guide/67ee07248ebf-index.md)；[Linux Docker container（PySpeos 0.9.2 頁面）](../ANSYS_Document/Speos/sdk/ansys-speos-core/0.9.2/guide/c55642e11494-linux_container.md)；[Getting started：security considerations（PySpeos 0.9.2 頁面）](../ANSYS_Document/Speos/sdk/ansys-speos-core/0.9.2/guide/fcc92cbc5f0b-index.md)（[來源清冊](sources.csv#ansys_31cc9aa9a62268e2acf893be)、[Linux image](sources.csv#ansys_c0ee4d996dec4541f9190df5)、[Getting started](sources.csv#ansys_d7d772ed3b0b99b4a1e346b7)）。

## 連線與生命週期

服務啟動與 client 連線是不同步驟。由 launcher 建立的 Speos 物件同時作為 session；工作結束後依文件呼叫 close() 關閉 channel 並清除 Speos objects。既有服務則須另建立 client 並檢查 client status。

### Launcher 與 Product Instance Management（PIM）

PySpeos 0.9.2 文件列出三條啟動路徑：Python launcher 在本機啟動 RPC server、使用 SpeosRPC_Server 命令列啟停服務，或透過 PIM 在遠端建立服務 session。launch_local_speos_rpc_server() 回傳 Speos 物件供後續操作；API 參數包含可選服務版本、port 與 RPC executable path。指南範例使用 version=251（Ansys 2025 R1），不可視為目前安裝的預設版本。

| 路徑 | 文件要求與行為 | 存取或版本界線 |
| --- | --- | --- |
| 本機 Python launcher | launch_local_speos_rpc_server() 啟動 RPC server，回傳 Speos session；version 可省略，API 頁說明本機會嘗試使用最新安裝版本。工作完成後呼叫 speos.close()。 | 可指定 port、speos_rpc_path 等參數；啟動可執行檔路徑及相關環境變數有安全影響。 |
| 命令列 launcher | 使用 SpeosRPC_Server executable 啟動、停止或查詢 help；指南提供 Windows 與 Linux 命令示例。 | 範例路徑引用 AWP_ROOT251，應按實際安裝調整；不要將範例路徑視為固定安裝位置。 |
| PIM launcher | launch_speos()／launch_remote_speos() 透過 Product Instance Management 啟動遠端服務。需先設定 PIM；API 頁提供 pypim.is_configured 作為檢查入口。 | Getting Started 的 PIM ZIP／AnsysLAB 範例限 Ansys 員工及具 Artifact Repository Browser 權限者。此限制屬文件頁面的服務存取條件。 |

launch_speos() 與 launch_remote_speos() 的 version 為可選三位數字字串；API 頁表示省略時由 server 選擇。launch_remote_speos() 頁另明示呼叫前需處於 PyPIM 已設定環境。兩者均回傳 Speos instance。來源僅說明 launcher 行為與前置條件，未在本機建立連線或驗證 PIM 帳號。

來源：[Launch a service（PySpeos 0.9.2 guide）](../ANSYS_Document/Speos/sdk/ansys-speos-core/0.9.2/guide/75ac414fb5f7-index.md)；[launcher API（PySpeos 0.9.2）](../ANSYS_Document/Speos/sdk/ansys-speos-core/0.9.2/api_reference/ee132fdab849-index.md)（[來源清冊](sources.csv#ansys_69c14c00697daa4e2935317f)、[API reference](sources.csv#ansys_5391299c7a8e23dc63f7ef74)）。兩份頁面均有本機 HTML 與 Markdown sidecar；來源服務端 release 仍未知。

### 連接既有服務與檢查 client 狀態

PySpeos 0.9.2 的既有服務指南說明，連線需知道 host 與 port。指南範例以 Speos() 建立 client，並指出沒有錯誤訊息表示連線成功；狀態範例則透過 speos.client 顯示目標 localhost:50098 與 Connection: Healthy。localhost:50098 是該範例輸出，不能據此假設所有安裝的服務都使用相同位置。

同版 Speos API reference 補充了 channel 用法：預設 Speos() 等同 Speos(channel=default_local_channel())；若本機 RPC server 用自訂 port 啟動，可用 default_local_channel(port=..., message_size=...) 建立 channel，再傳入 Speos(channel=...)。這個 local channel 範例不代表任意遠端 host 設定方式。

API reference 另示範 insecure gRPC channel：TransportOptions 設為 INSECURE，以 host、port 與 allow_remote_host=True 建立 channel，並傳入 Speos(channel=...)；該例要求 server 以 --transport-insecure 啟動。這是來源中的示例，不構成安全部署建議；傳輸模式須與 server 相符，外部網路部署應依 Docker service 傳輸安全說明及目標環境的安全要求設定。

來源：[Use an existing service（PySpeos 0.9.2 guide）](../ANSYS_Document/Speos/sdk/ansys-speos-core/0.9.2/guide/447c4add4643-index.md)（[來源清冊](sources.csv#ansys_1b840aa54eae4d16ac45db10)）；[Speos API reference（PySpeos 0.9.2）](../ANSYS_Document/Speos/sdk/ansys-speos-core/0.9.2/api_reference/1c7c6c1edbfe-Speos.md)（[來源清冊](sources.csv#ansys_1502e49f477054e42a479085)）。stable URL 的服務端版本未知，產品 release 維持 unknown。

## 安裝、授權與安全

Getting Started 說明 PySpeos 可透過 pip 安裝 ansys-speos-core；FAQ 指出啟動 Speos service 需要 Speos license。

### API 輸入與 launcher 安全界線

官方 security considerations 指出，函式警告連到該頁表示不當使用可能帶來安全風險。使用者輸入應先驗證；特別檢查 function arguments 中的任意 file path、shell command、serialized data，以及影響函式行為的環境變數。

launcher API 對 launch_local_speos_rpc_server() 有額外警告：該函式依參數及環境變數設定並啟動 executable，可能使不可信呼叫者啟動任意程式。若將此函式暴露給不可信使用者，須驗證 RPC executable path 及環境變數（文件舉例 AWP_ROOT）；文件建議在應用程式中固定安全路徑。遵循最小權限，且不要把未審查輸入直接交給 launcher。這是 API 文件的安全告誡摘要，沒有實際利用或執行測試。

來源：[Getting started — Security considerations（PySpeos 0.9.2）](../ANSYS_Document/Speos/sdk/ansys-speos-core/0.9.2/guide/fcc92cbc5f0b-index.md)及 [FAQ — Speos license](../ANSYS_Document/Speos/sdk/ansys-speos-core/0.9.2/guide/17ce0e5be1db-faq.md)（[來源清冊](sources.csv#ansys_d7d772ed3b0b99b4a1e346b7)、[FAQ](sources.csv#ansys_a992006eb5a46effdc9ae738)）；launcher 函式警告見 [launcher API](../ANSYS_Document/Speos/sdk/ansys-speos-core/0.9.2/api_reference/ee132fdab849-index.md)（[來源清冊](sources.csv#ansys_5391299c7a8e23dc63f7ef74)）。HTML 與 Markdown 中的安全要點一致。

## 本機光學標準與材料參考的使用界線

SPEOS 文件庫另收錄汽車與航太照明標準、材料／色票及驗證報告。這些文件適合作為工程師按專案要求查找的參考入口；檔名或存在於本機不代表已確認其版本適用性、官方授權來源、或可對外分享。引用前應核對標準版次、專案要求與取得權利。此字典不轉錄受限制標準的條文，也不以文件名稱推定符合性。

例如，本機 `GB+5920-2024` PDF 的 Markdown sidecar 有 31 個頁面標記，`GB+4599-2024` 有 59 個；其內容涵蓋範圍只能依原文件與有效標準確認。`RAL DESIGN StandardRGB (RGB)` 是單頁圖片型 PDF，沒有可檢索正文，不能從索引驗證色票或色度數值。SAE／ECE 等文件亦應回到原始 PDF 查頁面與適用版本，不應把索引片段當作正式標準引用。

來源：[GB+5920-2024（PDF）](../ANSYS_Document/Speos/unknown/manuals/GB%2B5920-2024.pdf)（[清冊](sources.csv#ansys_038e8285c89f7bd7f3704218)）；[GB+4599-2024（PDF）](../ANSYS_Document/Speos/unknown/manuals/GB%2B4599-2024.pdf)（[清冊](sources.csv#ansys_6470a505a6e66a2c16420457)）；[RAL DESIGN StandardRGB（PDF）](../ANSYS_Document/Speos/unknown/manuals/RAL%20DESIGN%20StandardRGB%20%28RGB%29.pdf)（[清冊](sources.csv#ansys_c0335fbc1d4d28c0748604f1)）。

## 來源與限制

- [PySpeos Getting Started](../ANSYS_Document/Speos/sdk/ansys-speos-core/0.9.2/guide/fcc92cbc5f0b-index.md)（`ansys_d7d772ed3b0b99b4a1e346b7`）與 [FAQ／license 說明](../ANSYS_Document/Speos/sdk/ansys-speos-core/0.9.2/guide/17ce0e5be1db-faq.md)（`ansys_a992006eb5a46effdc9ae738`）
- [Launch a service](../ANSYS_Document/Speos/sdk/ansys-speos-core/0.9.2/guide/75ac414fb5f7-index.md)（`ansys_69c14c00697daa4e2935317f`）與 [launcher API](../ANSYS_Document/Speos/sdk/ansys-speos-core/0.9.2/api_reference/ee132fdab849-index.md)（`ansys_5391299c7a8e23dc63f7ef74`）
- [Connect to an existing service](../ANSYS_Document/Speos/sdk/ansys-speos-core/0.9.2/guide/447c4add4643-index.md)（`ansys_1b840aa54eae4d16ac45db10`）
- [Docker service overview](../ANSYS_Document/Speos/sdk/ansys-speos-core/0.9.2/guide/67ee07248ebf-index.md)（`ansys_31cc9aa9a62268e2acf893be`）及 [Linux Docker container](../ANSYS_Document/Speos/sdk/ansys-speos-core/0.9.2/guide/c55642e11494-linux_container.md)（`ansys_c0ee4d996dec4541f9190df5`）

Speos 目錄另有大量光學標準與材料 PDF；[RAL DESIGN StandardRGB (RGB) 色票](../ANSYS_Document/Speos/unknown/manuals/RAL%20DESIGN%20StandardRGB%20%28RGB%29.md) 是單頁影像附件，正文無法可靠辨識，僅可抽取標題與 sRGB 標示，詳見 [來源清冊](sources.csv#ansys_c0335fbc1d4d28c0748604f1)。這些不納入本頁的 PySpeos API 摘要；主題狀態見 [主題清冊](topics.csv)。未啟動服務、執行 Speos API 或進行光學求解。


## 2026-11-04：Wave 4 本機來源盤點與限制說明

本批完成 speos 模組既有本機 catalog 文件（共 994 筆）與 sources 清冊（共 66 筆）之完整雜湊、正文路徑與標籤結構核對。本機未快取或具備企業授權/登入限制之線上主題誠實標記為缺口（保持現有非 complete 狀態），未擅自虛構未核實之線上 API 簽名或執行求解運算。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/speos_module_conversion_report_20261104.md)。
