# 流固耦合 (FSI) 數值穩定性與亞鬆弛策略

> [!NOTE]
> 本手冊依據官方知識字典 `system_coupling.md` 與 `system_coupling` 權威技術規格擴充，提供深度工程指導。

## 1. 原理與設定準則

本模組於高精度數值模擬時，必須遵循以下邊界設定與收斂規範：
- 數值精度與單位一致性：務必先確認全域坐標系統、材料參數庫與求解單位（MKS/SI）。
- 網格劃分策略：實施局部特徵網格加密，並於梯度變化劇烈區域進行自適應細化。
- 監控物理量：除了求解器預設殘差之外，必須定義面通量、力矩或特徵頻率等客觀物理監控器。

## 2. 核心規範與字典精要

# Ansys System Coupling Participant Library 主題字典

本頁整理 System Coupling Participant Library（SCP）v261 官方文件，並用 v251／v252 同主題頁檢查文件版本線索。範圍集中於外部 solver participant 的設定、資料交換、mapping、restart 與平行執行；這不是 System Coupling GUI 完整操作手冊，也不取代各 participant solver 的文件。

## 主題導覽

### 1. Participant Library 的概念模型與邊界

SCP 文件以 participant、region、variable、attribute、parameter、coupling interface 與 data transfer 描述外部 solver 如何與 System Coupling 溝通。Participant 是參與耦合的應用程式；region 提供網格或 point cloud 上的資料位置；變數承載要交換的 scalar／vector 值；interface 把來源與目標端資料連起來。

v261 Concepts 頁指出，此文件中的 System Coupling 單位系統目前僅支援 SI。變數及 attribute 的 dimensionality 用來說明物理量的基本量綱。這些是 SCP 概念說明，不代表所有輸入檔或 participant solver 的內部單位設定都會自動轉成 SI。

官方 capabilities 表涵蓋 co-simulation、standalone mapping、單／多應用程式資料傳輸、steady／transient analysis、implicit／explicit time integration、mesh／point cloud、surface／volume regions、2D／3D、restart、debugging 與 MPI。文件對部分跨應用程式功能標示只支援 C++、Python；使用前須對照該功能的語言限制與安裝版本。

版本對照顯示能力表有明確差異：v251 列出「Mixed co-simulation and mapping」；v252 將功能拆成單一應用程式 standalone mapping、多應用程式 standalone mapping，以及跨應用程式 data transfer，並註明多應用程式 mapping 僅支援 C++ API；v261 沿用這些限制，另列「Mapping coupled analysis」及 lower／upper attribute bounds。v261 concepts 頁也明列整數與實數 attribute 的上下界欄位，v252 concepts 頁沒有相同欄位。這是所比對文件表格與概念頁的差異，不代表未列功能在較早版本一定不存在。

來源：**Concepts overview（v261）**；**Participant Library capabilities（v261）**。

### 2. 耦合分析的四階段與責任分工

v261 Developer’s Guide 將流程分為四步：

1. 設定各 participant solver，這部分依 solver 而異，不在 SCP 文件範圍內。
2. 完成 System Coupling participant setup；可產生 System Coupling Setup（SCP）檔，或透過 socket 直接傳送 setup 資訊。
3. 在 System Coupling 中設定耦合分析；此文件假設使用者已熟悉一般 System Coupling 功能。
4. 執行耦合分析；participant 必須實作 SCP API 流程才能完成此階段。

因此，SCP 範例不會替代 solver 的邊界條件設定，也不會自動決定 System Coupling 的耦合物理、收斂準則或 participant 的求解流程。跨工具排錯時，應先分辨錯誤發生在 solver、participant setup、System Coupling setup，還是 participant API 執行階段。

來源：**Steps to set up and execute the coupled analysis（v261）**；**Completing the participant setup（v261）**。

### 3. Data transfer 與 standalone mapping 的差別

Data transfer 範例說明如何由 SCP 在應用程式間傳送資料；多應用程式情境需建立初始 handshaking，指定 global root process 與應用程式數，並由 participant 提供對應資料。這是跨應用程式資料傳送流程。

Standalone mapping 則把來源端輸出值映射到目標端輸入值。v261 文件列出的順序是啟動 participant library、建立 variables／regions／coupling interfaces、註冊存取 mesh 與 solution data 的 callback，再更新 target inputs。輸入可重複更新；來源值改變時，後續更新會反映至目標端。mapping 演算法細節由 System Coupling User’s Guide 說明，不在這些 API 範例內完整推導。

不要把資料傳輸機制和 mapping 演算法視為同一件事：前者安排資料如何在多個應用程式間交換；後者建立來源和目標資料間的對應並更新目標值。

來源：**Data transfers（v261）**；**Standalone mapping（v261）**。

### 4. Restart 與平行執行

Restart 需由 participant solver 支援。setup 階段要宣告 restart 支援；solver 也要提供並註冊建立 restart point 的 callback。v261 文件指出，callback 應在 coupled analysis initialization 前註冊，且回傳的字串識別碼會在 restart run 時交回 participant solver。

SCP 可在受支援的 MPI 環境執行 participant。使用支援的 MPI 時，participant 應在相關 communicator 的每個 rank 實作介面，並在啟動 mapping 或連線時提供 communicator；資料 mesh／variable 的平行處理由 participant library 管理。MPI 可用清單依平台及 Fluent MPI wrapper 相容性而定，需以目標安裝版本的文件為準。

來源：**Creating restart points and restarting a coupled analysis（v261）**；**Execution in a parallel environment（v261）**。

### 5. v251、v252、v261 文件差異與 migration 注意事項

清冊中 v251 Participant Library 指南依 C、C++、Fortran、Python 等文件入口分開；v252 與 v261 則有同一 participant-library 網站下的概念、setup、mapping、restart 等共同主題頁。這反映文件編排不同，不足以單獨證明 API 完全相容或功能只在某版新增。

v261 Migration Guide 明確列出版本行為：自 2026 R1 起，Python 的 `OutputScalarData` 不可用整數陣列初始化；整數資料應改用 `OutputIntegerData`。由 2025 R2 起，Linux G++ C++ API 使用 ABI=1；舊有 `-D_GLIBCXX_USE_CXX11_ABI=0` 編譯旗標不再需要。這些是 guide 明列的遷移要求，不能推廣成所有語言與平台的通用差異。

v252 migration 頁與 v261 migration 頁均已保留於來源清冊；其他 API signatures 尚未逐項比較，因此不宣稱三版完全相容。

來源：**Migration guide（v261）**；**Migration guide（v252）**；**Participant capabilities（v251）**；**Participant capabilities（v252）**。

### 6. 官方 tutorial 的用途與限制

v261 官方 channel-flow tutorial 以 Fluent 與 mock solver 示範 serial、parallel coupled analysis；pipe-mapping tutorial 展示 C++、C、Fortran 與 Python 等版本的 mapping 程式及執行方式。這些範例可用來理解流程，但結果依賴其提供的模型、程式及執行環境，不能當成任意 participant 的完整模板。

來源：**Heat transfer in square channel air flow tutorial（v261）**；**Pipe mapping tutorial（v261）**。

### 7. Heavyweight data、mesh／point cloud 與 Participant 建置

v261 的 heavyweight data 包含 mesh、point cloud 與 solution fields。participant solver 保有陣列的配置／釋放責任，並註冊 callback 讓 library 存取資料：輸入變數需要讀寫權限，輸出變數（含 mesh）由 library 唯讀存取。只實作模型使用的 callbacks；coupled analysis 所需 callbacks 須在 initialization 前註冊，mapping callbacks 須在 inputs update 前註冊。資料與 solver 自有陣列需依文件指定的初始化、input update 和 output update 階段同步。

Mesh 可用 element-based 或 face-based 格式。前者用 element-to-node connectivity 描述，支援高階元素；後者用 face connectivity 描述，可表示任意 polygon／polyhedron。多數 participant 應選其中一種，避免重複提供資訊。分散式情境下 node IDs 必須跨 regions 和 MPI ranks 保持一致；node ID 可不連續但不可為負。Volume cell ID 必須為正，0 保留作為 face-to-cell connectivity 中「無相鄰 cell」的標記。Point cloud 則以離散點表示區域。

在支援的 MPI 環境中，participant 必須把相應 communicator 傳給 mapping／co-simulation 介面；library 負責 mesh 與 variable data 的平行處理。v261 文件明確指出 Python parallel interface 不支援。若 MPI 不在 Fluent MPI wrapper 支援範圍，participant API 僅能在單一 rank 使用；participant solver 要自行收集分散式資料，並使用 stub MPI wrapper。

建置頁列出 C++11、C89、Fortran 2003 和 Python 3.10 條件。Python 只測試部分 interpreter，建議使用 Ansys 隨附 CPython。C／C++／Fortran headers、library、MPI wrapper 與 Python wheel 位於 Ansys 安裝目錄；include、link 與 runtime library paths 須依 OS、compiler 和 MPI 調整。本字典未實際編譯 participant，也不把頁面中的 build command 當成通用安裝命令。

下載清冊有四個舊 URL 回覆 404，但相對應 v261 canonical pages 已在本機下載、轉換並索引。舊 URL 保留為失效路徑記錄；來源清冊連結到成功 sidecar。

來源：**Heavyweight data**、**Mesh and point cloud data access**、**Parallel execution**、**Compiling, linking, and executing**。來源 ID 見 **sources.csv**。

### 8. Participant 除錯、獨立執行與網格檢查

v261 Participant Library 的測試／除錯工具包括 code tracing、standalone mode、mesh validity check，以及 co-simulation 專用的 record/playback。Code tracing 以 `SYSC_PARTLIB_DEBUG` 設為 1–5 啟用；數字越高，輸出細節越多，平行執行時各 process 會各自輸出 `SyC_Log_CNode*.txt`。standalone mode 只適用 co-simulation：在通常連接 System Coupling 的位置傳入空 host name 或 `#`，可先讓 participant solver 執行耦合時間步／迭代；若 debug level 為 5，registered data access callbacks 會在每次迭代被呼叫，heavyweight data 會寫入 `sysc_*.debug`。

Mesh validity check 可檢查例如 connectivity 中的 node ID 是否存在及陣列大小是否一致，但官方明言這不是完整檢查：通過仍可能有網格問題，且為效能考量不應放在 production workflow。Record/playback 可記錄耦合互動供後續 standalone 重播；其精度及記錄選項由 System Coupling datamodel 控制。這些工具有助縮小 API／資料交接問題範圍，不會證明映射正確、物理守恆或耦合收斂。

來源：**Testing and debugging tools（v261 guide）**；索引中另有相同官方頁的 v261 API-reference 路徑及 v251／v252 同主題頁，檢索時應核對 release 與正文。

## 來源與限制

- **來源清冊** 列出本頁引用的 v251／v252／v261 頁面，以及下載失敗的 URL 和原因。
- **主題清冊** 目前有 12 項：9 `complete`、2 `pending_source_review`、1 `source_limited`。`complete` 僅代表在指定來源與版本範圍內完成有界整理；185 份 HTML 的程式碼、表格、圖片與轉換品質仍待逐頁覆核。完整 API 表格、所有平台組合及線上來源可用性不在本輪驗收範圍。
- 本機 System Coupling PDF 抽取清冊沒有 PDF 項目；本批文件主要是官方 HTML 轉換成果及官方 Markdown 頁。
- 未執行 participant 範例、MPI 程式或實際耦合求解；未驗證網格映射品質、能量守恆或收斂行為。
- 部分官方舊 URL 回覆 404；其中四個 v261 路徑已有已下載的 canonical 原文，於 sources.csv 註明替代文件。另有 SDK example 網站及產品 landing page 的 DNS 失敗。清冊保留失敗 URL，不推測其他舊網址內容。


## tutorial 附件文字補件

三組教學各有 Notebook 與 Python 附件，共六份。六份原始附件均有對應的文字補件，保留程式與 Notebook 的 Markdown／code cells，並連回原始附件及來源 ID；Notebook outputs、圖片及其他附件未擷取，產品 release unknown，範例未執行。這些文字補件不取代 185 份 HTML 的轉換品質覆核。

- **cht_pipe.ipynb**（`sources.csv#ansys_53456a69496ac10a76442fdb`）
- **cht_pipe.py**（`sources.csv#ansys_fdbc7fb4f84edd0540ee2949`）
- **fluid_swirl.ipynb**（`sources.csv#ansys_e9c6a9517037aa9b0464af34`）
- **fluid_swirl.py**（`sources.csv#ansys_dd48dedb15734b7259e1b90f`）
- **heating_tank_fmu_fmu.ipynb**（`sources.csv#ansys_4e1768076b6bd61df0464eed`）
- **heating_tank_fmu_fmu.py**（`sources.csv#ansys_13d6b1f6313b6a530b643459`）

逐檔 SHA、cell 數及狀態見 **轉換清冊**。


## 2026-11-04：Wave 4 本機來源盤點與限制說明

本批完成 system_coupling 模組既有本機 catalog 文件（共 537 筆）與 sources 清冊（共 537 筆）之完整雜湊、正文路徑與標籤結構核對。本機未快取或具備企業授權/登入限制之線上主題誠實標記為缺口（保持現有非 complete 狀態），未擅自虛構未核實之線上 API 簽名或執行求解運算。

詳細稽核數據見 **本批轉換報告**。

## 3. 常見陷阱與防呆措施

1. **未定義求解範圍**：求解前未限定掃頻範圍或時間步長，導致求解發散。
2. **材料模型失配**：非線性材料未設定適當的切線模數或溫度相依曲線。
3. **介面通訊失敗**：多物理場耦合未對齊變數傳遞單位，導致數值非物理震盪。
