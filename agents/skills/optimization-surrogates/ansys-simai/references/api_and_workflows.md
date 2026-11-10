# Ansys SimAI 物理人工智慧代理模型 核心 API 與工作流指南

> [!NOTE]
> 本文件由知識字典 `simai.md` 精煉而成，提供標準工程流程與自動化腳本簽名。
> 可調用 MCP 工具 `ans_get_knowledge_dictionary(product='simai')` 查閱完整章節。

## 1. 模組架構與工作流說明

本模組遵循 ANSYS 現代自動化架構與雙軌工程標準：
1. **初始化與通訊連線**：支援本地 gRPC / 批次執行以及遠端伺服器程序掛載。
2. **參數配置與資料交換**：透過結構化物件或日誌檔精準傳遞幾何、材料與網格控制項。
3. **求解監控與非同步等待**：使用 Sentinel 工具或狀態輪詢器追蹤計算收斂情況。
4. **結果匯出與報告整合**：產出結構化數值報表與 3D 視覺化資料。

## 2. 知識字典精華摘錄

# Ansys SimAI／PySimAI 知識字典

> 本頁依本機 PySimAI 文件整理，英文 API 名稱保留原樣。文件首頁標示 release `v0.4.8`；本機清冊另有版本 `unknown` 的內容，以下只在來源明示時標版本，不把 stable URL 當作永久版本識別。此頁是文件摘要，不取代官方說明。

## 文件範圍與閱讀方式

- PySimAI 是 Python 用戶端，可由 Python 程式管理與存取 SimAI 平台資料。官方首頁將資料分為 User guide、API reference、Examples，並標示需要 Python 3.9 以上。
- 官方入口：[PySimAI documentation（stable）](https://simai.docs.pyansys.com/version/stable/)；本機起始頁：**PySimAI 文件**。首頁當前標示 `v0.4.8`。
- 本機來源清冊與轉換狀態：**simai_sources.csv**。清冊列出 85 個原始項目（62 HTML、23 Markdown、0 PDF）；62 個 HTML 均有配套 Markdown 轉換。本輪未重轉 HTML，以免覆寫既有成果。23 個 Markdown 項目的清冊 `text_exists=false` 是因其本身就是正文來源，不代表轉換失敗。85 個原始檔均存在且 SHA-256 與 catalog 相符；這些檢查不等同於轉換內容的語義校閱。尚未逐頁核對所有圖表及表格。

## 1. 用戶端設定與登入

`SimAIClient` 可直接用建構參數建立；未提供的必要參數可能觸發互動提示。設定指南列有 `access_token`（預先取得的 OIDC access token）、`credentials`、`offline_token`、`https_proxy`、`interactive` 等欄位。`interactive` 預設為 `True`，意指允許與終端互動；CI 中如何登入應依其身份提供方式選擇 token，不能把密碼或長效 token 寫入程式碼或版控。

TOML 設定檔支援多個 profile，也可指定路徑；預設檔案位置會依作業系統而異。實際設定名稱與登入流程請對照指定版本的 configuration guide，不要照抄範例中的示意憑證。

來源：**`Client configuration`**（stable URL）；**`Configuration file`**（stable URL）；**`Client API`**（清冊 SDK 0.4.8）。

## 2. 訓練資料、專案與模型建置

- `TrainingData` 管理上傳的模擬資料；`upload_folder()` 可上傳資料夾，逐一管理資料檔則使用其 parts API。資料上傳／抽取是平台工作流程的一部分，完成與否要查物件狀態，不能只依呼叫已返回判定。
- `Project` 將資料與模型設定組織在一起。官方建置指南流程為建立 project、上傳並關聯 training data、指定 `ModelInput` 與 `ModelOutput`，建立 `ModelConfiguration`，然後呼叫 `simai.models.build()`。
- 模型輸入輸出包含不同資料型態（例如 surface、volume、scalars）；`DomainOfAnalysis` 與 `global_coefficients` 是設定選項。實際欄位、可用物理量及限制以相同 SDK 版本的 API reference 為準。
- 官方建置指南註明建模功能仍屬 experimental，且 API 可能變動。指南示例出現 `build_on_top=False`，故不能單憑其他版本文件推定其棄用或不可用；應以目標 SDK API 參考確認。

來源：**`Building a model`**（stable URL）；**`TrainingData API`**（0.4.8）；**`Projects API`**（0.4.8）；**`Model configuration`**（0.4.8）。

## 3. 幾何與預測

`Geometry` 是平台上用於預測的幾何物件；`Prediction` 表示對幾何與模型輸入條件執行的數值預測。預測輸入依模型而定，指南範例以 `geometry.run_prediction(Vx=velocity)` 示範；API 亦提供 prediction directory 管理操作。不要把示例中的 `Vx` 當作任意模型都支援的欄位。

預測工作可透過 `wait()` 等待工作完成，再以 `is_ready`／`has_failed` 等屬性確認結果；等待返回本身不代表成功。0.4.8 API 將 `confidence_score` 描述為 high／low 類別，另列 `raw_confidence_score` 為浮點數。欄位可用時機與這些值的統計意義不能超出官方定義推論。

來源：**`Predictions API`**（0.4.8）；**`Geometries API`**（0.4.8）；本機相同頁的未標明 SDK 版本內容也在清冊中，使用時須留意版本標籤。

## 4. 後處理與全域係數

後處理資料由獨立 API 類別管理，包含 post-processing、global coefficients 等相關項目。其輸入、輸出與完成狀態應查對應 API 頁面；不同後處理類型不能只因名稱相似而假設資料格式相同。本輪已確認本機有相應 HTML/Markdown 來源，但未逐類核對所有欄位、圖表及數值單位。

來源：**`Postprocessings API`**（0.4.8）；**`Global coefficients`**（0.4.8）。

## 5. GeomAI 與非參數最佳化

本機 stable URL 文件清冊另含 GeomAI workspace、training data、model、prediction、selection 與 optimization 頁面。它們與傳統 PySimAI 頁面分屬不同 API 路徑；本輪未完成各自的版本對照及全量主題整理，不能把其類別或行為直接套用至 PySimAI API。

來源：`docs/ANSYS_Document/SimAI/sdk/ansys-simai-core/unknown/api_reference/` 下的 GeomAI 頁面（版本標示 unknown）；入口以 [官方 stable API reference](https://simai.docs.pyansys.com/version/stable/api_reference.html) 查閱。

## 待補與可信度界線

- 官方首頁確認 PySimAI 文件版本為 0.4.8；Synopsys developer portal 的本機來源 URL 無法由目前網頁讀取工具取回，因此該入口文件的現行內容與可存取性未核實。
- 來源清冊共 85 筆：62 筆 HTML、23 筆 Markdown；62 筆 HTML 均已有清冊指定的 Markdown 轉換文字。catalog 的 `sdk_version` 欄有 42 筆標示 0.4.8、43 筆 unknown；`release` 欄則 85 筆均為 unknown。首頁正文自行標示 release v0.4.8，因此可用它描述首頁及相關有明確版本的指南/API，不能據此將所有 unknown 路徑一律定版。未發現 PDF。清冊中多筆 HTML 與 Markdown 代表同一頁，不應當成不同主題來源重複整理。
- 既有字典內容曾含未能由目前列出的來源證實的精確數字、API 棄用結論與不可逆刪除描述。本輪以官方文件可追溯內容取代這些確定語氣；需逐條回查完整 API reference 後才能恢復更細的操作主張。
- 未完成：GeomAI/NPO 全面整理、範例執行與雲端服務驗證、所有 API 參數表逐欄校閱、HTML 轉換的圖表與表格對照、版本差異矩陣。下載的範例未執行，也未進行任何模型求解。

抽查依據：首頁正文確認 release v0.4.8、Python 3.9+；`configuration.md` 列出 access token、credentials、GeomAI 預設專案/工作區、proxy、interactive 與 offline token 等選項；`config_file.md` 說明 TOML 與 profile；`building_a_model.md` 明示建模仍屬 experimental；`predictions.md` 區分分類型 `confidence_score` 與浮點 `raw_confidence_score`。原始檔與配套轉換均保留，無 PDF 待轉。HTML/Markdown 轉換未做逐頁視覺或表格等價驗收。


## 2026-11-04：Wave 1 本機來源盤點與限制說明

本批完成 Ansys SimAI / PySimAI 模組 catalog 既有 85 筆核心文件（包含 62 筆 HTML 與 23 筆 Markdown 正文，涵蓋 SDK 0.4.8 Client、TrainingData、Projects、Geometries、Predictions、PostProcessing 與 Global Coefficients 等完整模組）之 SHA-256 完整性與標籤結構核對。SimAI 雲端平台需專屬企業 OIDC / API 授權；外部未快取之線上主題誠實標記為缺口（`source_limited` / `pending_source_review`），不擅自虛構未核實之線上主題或執行即時模型推論。

詳細稽核數據見 **本批轉換報告**。


## 2026-11-05：官方正文、版本與轉換補核

本節更新前面較早批次的存取與版本判讀。此批核對 85 個 catalog 原件：62 HTML、23 Markdown、無 PDF。62 HTML 共有 171 個程式片段（34,434 字元）與一張表格、四個儲存格；各片段與儲存格文字都能在既有 Markdown 找到。這證明本批程式／表格文字未遺漏，圖片、版面與公式的全面語意驗收仍待處理。

從現存清冊的官方 URL 取得 42 HTML 和一份 Markdown，保存 raw bytes 與轉換稿；這 43 份正文與既有 catalog 原件一致，因此沿用既有正文索引。官方文件引用的六張唯一圖片已另存原檔，尚未做圖片語意整理。另有一筆無來源 URL 的重複 HTML 使用相對圖片路徑，保留為無法獨立定位的別名，不把它算成第七張已確認圖。

### 文件版本如何判讀

| 來源欄位 | 本批核對 | 使用範圍 |
|---|---|---|
| catalog `sdk_version` | 42 筆 `0.4.8`、43 筆 `unknown` | 原 catalog 標籤保留，不因網址 stable 而回填 |
| 原 HTML `docsearch:version` | 62／62 明示 `0.4.8` | 可用於這些 HTML 正文的文件版本判讀 |
| 重新取得的官方 HTML | 42／42 明示 `0.4.8`，正文與既有 HTML 相同 | 這是 2026-11-05 的靜態文件核對，並非伺服器／安裝套件版本探測 |
| catalog `release` | 85 筆均為 `unknown` | 不推定 SimAI 雲端服務 release |

GeomAI 與 NPO 文件的上述 HTML 版本標籤已核對；未標版本的 Markdown 或重複 catalog 路徑仍保留 `unknown`。本批未執行 SDK，也未連線 SimAI 帳戶。

### GeomAI 模型評估與 NPO 的閱讀順序

GeomAI 訓練完成後可取得 Model Evaluation Report（MER）。文件列有重建幾何的 Chamfer distance、品質直方圖、幾何插值及 latent dimension 的 Parameter Importance。較小的 Chamfer distance 表示重建幾何較接近原幾何；MER 內的 threshold 是模型的判讀依據，不是可跨模型通用的驗收數字。直方圖離群值可能與網格孔洞、非流形邊或資料分布差異有關，仍需回看幾何與資料集。

來源：**Evaluation and workflow integration**（`Evaluate your model with the Model Evaluation Report`、`Quantitative assessment`）。

NPO 指南把流程分成取得合適模型、配置最佳化、產生幾何並評估、solver verification、增加訓練資料再建模。設定指南說明 server-side 最佳化需提供 offline token，該頁的有效期敘述為 30 天；這個範圍限定在該版 NPO 設定指南，不能推廣為所有 token 的固定有效期。NPO 結果仍要依官方流程回到工程 solver 驗證，文件整理並不代表任何幾何已求解或通過工程驗收。

來源：**Non-parametric optimization**（`Step 4. Solver verification`）；**Configure the non-parametric optimization**（`Offline token`、`Bounding boxes`）。

### Geometry 刪除與後處理生命週期

Geometry API 明載，刪除 geometry 會連同相關 predictions 與 postprocessings 一起刪除；以不存在的 ID 操作時列有 `NotFoundError`。該段沒有提供還原程序，因此實務操作前應先確認所選 geometry 及相關結果是否仍需保存。本批只核對文件，未送出刪除請求。

來源：**Geometries**（`GeometryDirectory.delete`、`Geometry.delete`）。

| 項目 | 文件中的用途 | 查閱時注意 |
|---|---|---|
| `PostProcessing.wait(timeout)` | 等待相關工作完成或失敗 | 返回不等於結果成功；續查 `has_failed`、`failure_reason` 與 readiness |
| `GlobalCoefficientDefinition` | 定義 `formula`、`name`、`gc_location` | `gc_location` 是 `'cells'` 或 `'points'`，不可僅憑名稱推定數值單位 |
| `ProcessGlobalCoefficient` | 將公式檢查及計算包成請求流程 | 公式語言及執行是否成功仍以對應請求結果為準 |
| `SimAIError`／`ProcessingError` | 前者為用戶端預期錯誤的基底；後者表示資料無法處理 | 這是 API 文件分類，沒有在本批觸發或驗證服務端錯誤 |

來源：**Postprocessings**；**Model configuration**（`GlobalCoefficientDefinition`）；**Global coefficients**；**Errors**。

### 公開 portal 與平台使用指南的缺口

`https://developer.synopsys.com/docs/simai.md` 這次回傳 HTTP 200、`text/markdown`，內容與本機原件完全相同；前面「portal 本輪無法取得」的限制已由這次直接取得原件補正。該頁只提供產品概述、Windows／Linux Python 用戶端與 PySimAI 連結，不足以代替完整平台操作手冊。

來源：**Ansys SimAI for developers 原件**（版本 `unknown`）。

PySimAI 首頁列出的 Ansys SimAI User’s guide 入口雖回傳 HTTP 200，但取得的是含 `Customer Sign In` 的 Ansys Help 入口外殼，沒有目標章節正文。該平台指南仍列來源受限；HTTP 成功不能視為正文已下載。公開文件可下載也不代表團隊分享權限已確認。

逐 URL 狀態、原件／正文 hash、圖片保留狀態及無法取得內容見 **本批 URL 清冊** 與本批轉換報告。既有 `INDEX_SPHINX` 是 template，不加入正式全文檢索；其來源檔繼續保留。

## 3. 雙軌數值基準與驗收標準

- **商業求解軌**：連線正式求解器執行高保真模擬。
- **無授權基準軌**：執行 `scripts/verify_simai_baseline.py` 驗證解析數值正確性（Exit Code 0）。
