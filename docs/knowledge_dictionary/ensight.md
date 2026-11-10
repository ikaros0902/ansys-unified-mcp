# Ansys EnSight 主題字典

本頁整理本機已取得的官方 EnSight Developer Portal v252（2025 R2）、v261（2026 R1）、PyEnSight SDK 0.12.0，以及三份 release 未知的舊 PDF。範圍包含 gRPC、DVS、影像傳輸、GLTFWriter、Python API 和舊版 Help。它是有來源界線的字典，不是完整 GUI 手冊、API 相容表或執行驗證。

## 主題導覽

### 1. EnSight 與外部程式的整合方式

EnSight 有數種目的不同的介面：內嵌 Python 在 EnSight 程序內操作；PyEnSight 由可攜的 Python wheel 啟動或連接另一個 EnSight 程序；gRPC 提供 client/service 式命令與串流控制；DVS 將 solver 資料送往後處理端；Shared Memory Image Transport 傳送畫面；GLTFWriter 輸出場景幾何。選介面時先確認資料方向、呼叫端和部署位置，不要把畫面串流、幾何輸出與 solver 資料輸入當成同一功能。

PyEnSight 0.12.0 文件說明，內嵌 `ensight` module 僅供 EnSight 內建 interpreter 使用；外部環境安裝的 PyEnSight 使用 `ansys.pyensight`，會啟動另一個 EnSight instance 並透過連線執行內嵌 Python 命令。文件稱兩者 API 大致相同，但須妥善組織程式，且存在明列差異，不能據此認定完全相容。

來源：[PyEnSight 0.12.0 User guide](../ANSYS_Document/EnSight/sdk/ansys-pyensight-core/0.12.0/guide/8ddd44fcd6f5-index.md)；[EnSight gRPC interface v261](../ANSYS_Document/EnSight/v261/guide/c6897f1d048a-index.md)；[DVS Introduction v261](../ANSYS_Document/EnSight/v261/guide/ae6fcb11ed07-index.md)；[Shared Memory Image Transport v261](../ANSYS_Document/EnSight/v261/guide/24bbdb13b975-index.md)；[GLTFWriter interface v261](../ANSYS_Document/EnSight/v261/guide/ecaae07c41e0-index.md)。

### 2. Python API：native、object 與 PyEnSight

EnSight Python 文件區分 native API 與 object API。Native API 是對 journal command language 的 Python binding；command language 可記錄和重播 GUI 操作，但官方頁稱其本身未文件化。Object API 透過 proxy 物件直接存取核心 C++ 物件的屬性和方法，支援屬性 callback、名稱／ID／物件等識別方式；它不涵蓋 native API 的全部功能。

PyEnSight API differences 頁列出兩個具體差異：EnSight 中可建立的 free `ENS_GROUP` 在 PyEnSight 中不合法，因為目標物件不在 EnSight session；PyEnSight 對 `ENS_PART`、`ENS_ANNOT`、`ENS_TOOL` 使用較專門的子類型。跨環境移植前需檢查建立物件及型別假設。

PyEnSight 0.12.0 User guide 的 object API 分類表原本有 5 個 HTML tables；Markdown sidecar 將表格展平，可能無法從格式明確看出每個 class／subclass 對應的描述。補件保留 DOM 順序和欄列：[PyEnSight User Guide tables](ANSYS_Document/ensight_pyensight_user_guide_tables_20261104.md)；原始頁面與逐頁 sidecar 仍見[來源文件](../ANSYS_Document/EnSight/sdk/ansys-pyensight-core/0.12.0/guide/8ddd44fcd6f5-index.md)。補件不涵蓋圖示與視覺版面，內容版次依本機 0.12.0 快照，未執行 API。

來源：[PyEnSight User guide](../ANSYS_Document/EnSight/sdk/ansys-pyensight-core/0.12.0/guide/8ddd44fcd6f5-index.md)；[Command language native Python API](../ANSYS_Document/EnSight/sdk/ansys-pyensight-core/0.12.0/guide/7361ae306c9b-cmdlang_native.md)；[Object API](../ANSYS_Document/EnSight/sdk/ansys-pyensight-core/0.12.0/guide/adc8443b42f3-object_api.md)；[API differences](../ANSYS_Document/EnSight/sdk/ansys-pyensight-core/0.12.0/guide/57deffa5c3b1-api_differences.md)。SDK 版本依本機文件目錄標示為 0.12.0；頁面 `stable` URL 會移動，不代表目前最新版。

### 3. gRPC 啟動、命令控制與 security token

v261 gRPC server 可在 full UI 和 batch mode 啟動，命令列選項為 `-grpc_server {port}`；未提供 port 時預設 18243。文件說明可用共享密鑰 security token 保護呼叫：若啟用，每次 RPC 都須在 metadata 傳 token；建議透過 `ENSIGHT_SECURITY_TOKEN` 環境變數傳入，而非把 token 放在命令列。

官方 command/control 頁包含外部 Python 建立 stub、安裝 gRPC 依賴、連線、執行命令及讀取 image/geometry 的範例。該頁範例不等於本機已具備相同版本套件、網路設定或有效權杖；正式使用需依安裝版文件確認 protocol 和安全設定。

來源：[EnSight command and control API v261](../ANSYS_Document/EnSight/v261/guide/52ec4b601edf-ensight-command.md)；[gRPC interface v261](../ANSYS_Document/EnSight/v261/guide/c6897f1d048a-index.md)。

### 4. DVS 資料流、資料模型與 cache

Dynamic Visualization Store（DVS）是可平行化的後處理資料 API。v261 概覽列出運算中 in-situ 檢視、postprocessor 關閉後重啟時自動重連、分散式 solver/postprocessor 傳輸、cache 寫入後讀取，以及 C/C++/Python API。這是官方列出的能力，不是本字典已執行的行為測試。

DVS data model 將 `dvs_uri` 指向 cache；cache 包含 datasets，dataset 有 object 定義與 timesteps；時間步由依 rank、chunk、object 分割的資料 blobs 組成。Rank 是分給單一 process/MPI rank 的 mesh 區段；chunk 可是 rank 內由 thread 處理的分區。官方說明 rank 分區通常需要 ghost elements，以支援後處理伺服器間免跨機通訊的負載分配；小於 10 million elements 的小 mesh 通常可由單一 EnSight server 檢視而不明確需要 ghost elements。此處保留為文件中的概念說明，不當成通用 sizing 規則。

DVS cache 是可選機制，可快取 API 收到的後處理資料；官方 cache 入口提到可有多種 domain/type，實際格式與 server setup 選項須查對應版本的 Server Options。v261 changelog 記錄 2026 R1 新增 client option API 與 `DVS_CLIENT_TIMEOUT_S`；2025 R2 以 xxHash 取代 MD5sum，release note 報告 hashing 速度約提升 5–10 倍或以上。該效能數字是版本說明中的觀察，不保證特定硬體或工作負載。

來源：[DVS Introduction v261](../ANSYS_Document/EnSight/v261/guides_and_tutorials/dynamic-visualization-store-2026-r1/index.md)；[DVS Data Model v261](../ANSYS_Document/EnSight/v261/guides_and_tutorials/dynamic-visualization-store-2026-r1/user-guide/dvs-data-model.md)；[DVS cache v261](../ANSYS_Document/EnSight/v261/guides_and_tutorials/dynamic-visualization-store-2026-r1/user-guide/dvs-cache.md)；[DVS changelog v261](../ANSYS_Document/EnSight/v261/guides_and_tutorials/dynamic-visualization-store-2026-r1/changelog.md)；[DVS Data Model v252](../ANSYS_Document/EnSight/v252/guide/30b62ae26ecd-group__group__dvs__data__model.md)。

### 5. Shared Memory Image Transport

EnSight gRPC 提供 VNC 與 gRPC stream push/subscribe pull 等畫面傳輸方式；Shared Memory Image Transport 擴充 Subscribe 路徑，透過 memory-mapped file 交換影像。其適用條件是 EnSight 與 client 在同一台 system 執行，故不是跨主機 transport。官方提供 C server/client 與 Python client 參考文件；安裝路徑依 ANSYSROOT、ANSYSVER、ARCH 組成。

v252 與 v261 入口文字都列出同機限制與 C/Python 介面。v261 頁提及 modern hardware 上可達 60 Hz 4K 的能力；硬體、影像格式及負載未指定，因此本字典不將其作為效能承諾。

來源：[Shared Memory Image Transport v261](../ANSYS_Document/EnSight/v261/guide/24bbdb13b975-index.md)；[Shared Memory Image Transport v252](../ANSYS_Document/EnSight/v252/guide/05341e214b38-group__shmem.md)。

### 6. GLTFWriter、AVZ 與 glTF

GLTFWriter 是 C++ API，可輸出 AVZ 或 glTF 2.0 幾何場景，場景可為靜態或隨時間變化；入口頁列出 lines、triangles、spheres。官方把 AVZ 描述為擴充形式，包含時變資料、變換與 2D overlay（例如 annotations、palettes），也支援 spheres 等 meta entities。其他 viewer 是否支援相應 extension，需按 viewer 文件確認。

來源：[GLTFWriter interface v261](../ANSYS_Document/EnSight/v261/guide/ecaae07c41e0-index.md)；[GLTFWriter Interface v252](../ANSYS_Document/EnSight/v252/guide/d4f075733661-group__gltf.md)。本輪只核對入口與部分參考文件，未比較完整 class/API signatures。

### 7. 本機 PDF Help 與舊版工作流程線索

本機 `HowTo.pdf` 共 436 頁，其逐頁 sidecar 可見 client/server、資料讀取、transient data、自訂 reader、輸出及視圖等章節；初始抽查第 1–12 實頁，見第 1 頁「Use Server of Servers／使用者自訂程序（reader）」等目錄文字及第 12 頁遠端登入示例。這份手冊版本未知，內容不得直接視為現行 GUI 操作指引。`HT-Manual.pdf` 共 3 頁，開頭說明 PDF Help 導覽、章節連結與 PDF reader。`LocalHelp.pdf` 共 1 頁，寫明將 `LocalHelp.pdf` 放入 `$CEI_HOME/ensight242/site_preferences` 並由 Help → Local 開啟；這只能作 EnSight 242 路徑線索。

來源：[HowTo 逐頁 Markdown](../ANSYS_Document/EnSight/unknown/manuals/HowTo.md)；[HT-Manual 逐頁 Markdown](../ANSYS_Document/EnSight/unknown/manuals/HT-Manual.md)；[LocalHelp 逐頁 Markdown](../ANSYS_Document/EnSight/unknown/manuals/LocalHelp.md)。三份 release 保持 `unknown`；舊文件敘述不推定適用目前安裝版。

## 來源盤點與缺口

- 本機 EnSight 下載清冊摘要為 96 筆：95 筆成功（90 原生 Markdown、5 HTML），另 1 筆 EnSight portal URL 遇 DNS 解析失敗。本文新增關注的 5 組 PyEnSight 0.12.0 HTML/Markdown 對已以現有 catalog ID 補入來源清冊；產品 release 為 unknown，SDK metadata 為 0.12.0。
- 五份 SDK HTML 均有對應 Markdown；配對檔案 SHA-256 已記錄在本次交付報告。這是檔案身份證據，不等於逐行語意或表格轉換品質驗收。本輪只核讀上述 5 頁的關鍵段落。
- 三份 PDF sidecar 和抽取清冊已存在，PDF/sidecar SHA-256 與 extraction cache 比對先前已有清冊狀態；本輪重新抽查 HowTo 第 1–12 頁及 HT-Manual、LocalHelp 全部可見頁。HowTo 其餘頁未逐頁語意校驗，掃描圖、表格及版面遺失仍可能存在。
- 來源清冊列出 96 筆 EnSight portal 項目中，本文只核讀一小組 DVS/gRPC/transport/GLTFWriter 與 SDK 頁面；未整理所有 v252 API reference、149 個 v261 tutorial/API 頁或完整 GUI 教學。1 筆 DNS 失敗項目的正文不可用，且不在本輪重試。
- 未執行 EnSight、PyEnSight、gRPC、DVS、共享記憶體或 GLTFWriter 範例；未驗證 runtime、連線安全、效能、第三方 viewer 相容性或跨版本 API 相容性。

## 建議 RAG 查詢

1. `EnSight -grpc_server 預設 port 及 ENSIGHT_SECURITY_TOKEN 要放在哪裡？`
2. `PyEnSight 和 EnSight 內嵌 ensight module 有什麼差別？`
3. `ENS_PART 在 PyEnSight 的型別差異是什麼？`
4. `DVS 的 rank、chunk、ghost elements 分別代表什麼？`
5. `DVS cache 是否需要 postprocessor 持續啟動？`
6. `Shared Memory Image Transport 能否跨主機傳影像？`
7. `GLTFWriter 的 AVZ 相對 glTF 2.0 多了哪些場景資訊？`
8. `HowTo PDF 中自訂 reader 和 client/server 手冊在哪些頁？`
9. `LocalHelp.pdf 指向哪個 EnSight 安裝版本目錄？`

搜尋與片段擷取的實際結果記於模組交付報告；代表查詢不代表已覆核全部 API 與手冊。


## 2026-11-04：Wave 6 本機來源盤點與限制說明

本機 catalog 的 249 筆原件與對應正文 SHA-256 均已核對，來源清冊含相同的 249 個 ID。版本分布為 v261 163 筆、v252 75 筆、unknown 11 筆。URL 清冊的 474 個網址均未在這一批擷取，其中 441 個標為官方。三份舊 PDF 共 440 頁，Markdown 頁碼標記完整。頁碼與雜湊只供追溯，PDF 頁內讀序、圖表、表格樣式和完整技術內容仍待覆核。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/ensight_module_conversion_report_20261104.md)。
