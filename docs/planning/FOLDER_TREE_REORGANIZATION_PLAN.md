# ANSYS 專案目錄、API 字典與 RAG 重構

## 目前 checkpoint（2026-10-29）

- 目前 Git tree 的正式資料夾只有 `agents/`、`docs/`、`scripts/`、`src/`、`tests/`；根層另有啟動器與專案設定檔。五個 v251 REA 候選的 APIKB 接線與字典更新已提交於 `4a147cf`。ANSYS_Document HTML/PDF Markdown 與轉換清單在被忽略的本機目錄；追蹤檔工作樹目前沒有未提交變更。本段不代表搬移或 API 行為驗收通過。此分支含有衍生資料，不可直接推送。HEAD 與工作樹狀態以即時 Git 記錄為準，本計畫不固定 HEAD 欄位。
- 目前 APIKB 來源口徑為 113 keys：25 份 API／SDK／protocol snapshots（21 份映射至 12 個產品 ID，4 份未映射）、55 份 REA managed snapshots、33 份 native export snapshots。主候選清冊有 47 份檢查結果，其中 42 份 metadata complete、5 份 absent；APIKB 快照包含這 42 份及 13 個另行分析候選（ACP、AQWA RemoteItf、Motion、SIwave、RSM JobManagement、Engineering Data Core/DataProvider、DesignModeler Core、Material Designer Core、TurboSystem AFDCore/CCDCore/CPDCore/RTDCore）。
- 57 個產品 coverage 狀態為 12 個有直接 snapshot、19 個只有產品組件證據、25 個尚未評估、1 個未映射共用介面。這些計數描述目前清冊，不表示完整 API 覆蓋。
- REA 候選母體仍需重算：`REA_EVIDENCE.md` 記錄 1,172 個檔名候選，而目前 managed assembly inventory 有 14,421 筆組件資料；依 `Ans.*`／`Ansys.*` 名稱規則的另一輪唯讀盤點得到 1,288 筆。篩選條件與去重口徑未對齊，不合併成單一總數。下一批先依 `relative_path` 和產品目錄篩選並保留檔案 hash，再分產品映射或列為未映射。後續候選盤點包括 ROM `Ans.Rom.dll`／`Ans.Rom.Interop.dll`、ACT add-in 組件與其他尚未映射產品目錄；尚未確認來源存在性或授權前不分析。
- 使用者要求目錄與 API/RAG 工作並行，暫不做驗證。Ansys 衍生資料的公開散布權限尚未確認，因此 REA/SDK 原件、快照、字典及其索引留在本機；已追蹤檔案不會因 `.gitignore` 而自動排除。唯讀 Git 歷史盤點顯示目前分支祖先含大量 API/REA/SDK 衍生資料：`9d9aad3` 對 `docs/api_inventory/` 有 120 個路徑變更，`82557c7` 也加入大量 API JSON。`38ba10f` 又更新本機衍生索引。因此目前分支不得直接 push。`origin/master` 已有 5 個 API inventory 檔，不改寫其歷史。公開交付需另從 `origin/master` 建立乾淨分支，逐檔重建可分享的目錄差異；不可整筆 cherry-pick 混有文件、程式及刪除的搬移 commits。
- 使用者已明確授權本機階段 commit 與所有目標完成後評估 push。已建立多筆本機提交，最新階段記錄見 Git 歷史。公開散布權尚未確認，因此不推送含 ANSYS 衍生資料的分支；若後續取得許可，仍須先建立乾淨分支並逐檔審查。
- 本 checkpoint 只核對 Git tree、狀態輸出及現有文件記載；沒有執行測試、驗證器、API/RAG 查詢或 ANSYS 求解。

## 分階段執行計畫（2026-10-29）

> 本計畫涵蓋目錄重構、2025 R1 API/RAG、ANSYS_Document 文件整理，以及後續工具鏈與自動化能力。使用者要求本輪先不做驗證；任何測試、查詢驗收、宿主啟動或跨機執行均延後。所有 ANSYS 衍生內容在公開散布權未釐清前只保存在本機。階段完成以具體產物與證據記錄，不以工具回報成功推論完整性。

| 階段 | 目的與交付物 | 進入條件與停止門檻 | 目前狀態 |
| --- | --- | --- | --- |
| **Stage 0 — Feasibility & Permission Review** | 記錄本機 ANSYS/SDK/REA 工具、可用版本、目標產品清單、資料來源、授權/散布限制與風險；建立可做、需授權、不可公開三類邊界。 | 分清使用者對本機靜態研究的授權、Ansys 條款對衍生物的限制、及 GitHub 發布權；未確認公開散布權前不推送 API/REA/SDK/手冊衍生資料。 | 初步完成；公開散布權仍不明，已限制所有衍生成果留本機。 |
| **Stage 1 — Minimum Toolchain** | 建立並記錄 Git 分支/階段提交、MCP 工具連線狀態、Serena、CodeGraph/codebase-memory、文件與 APIKB/RAG 的知識格式及來源追溯欄位。 | 僅記錄當次可觀察的連線與工具能力；設定檔存在不當作服務已連通。此階段不要求跑測試。 | 部分完成；Serena、CodeGraph 與 codebase-memory 工具在本次工作中有回應。CodeGraph 已於 2026-10-29 全量重建（469 files、7,633 nodes、17,271 edges）。codebase-memory 索引停留於 2026-10-21、watch 關閉，且目前未提供重建工具；不以舊圖宣稱新鮮。MCP 服務端求解器連線未測。 |
| **Stage 2 — ANSYS 2025 R1 API Inventory** | 以 Mechanical、ACT、MAPDL、LS-DYNA 為優先建立版本化 API 來源矩陣、公開文件與 SDK 字典、REA 靜態候選索引、缺口列表及可追溯 AI RAG；整理 ANSYS_Document 全部內容，按產品/主題/章節編目，將 PDF 與 HTML 轉成 Markdown，原件保留。 | 來源要記錄版本、相對路徑、雜湊、公開狀態與分析狀態；疑似受授權限制的原件與衍生 Markdown 均本機保存。沒有來源時標缺口，不推定 API 完整。 | 進行中；APIKB 有 25 個 API/SDK/protocol、55 個 REA、33 個 native source keys。ANSYS_Document 已按產品目錄編目；424,158 個 HTML 中 400,904 個沿用既有 Markdown、23,253 個新增轉換、1 個無法擷取正文；269 個 PDF 中 268 個有 Markdown、1 個掃描型 PDF 未 OCR。轉換清單與原件保留在被忽略的本機 `ANSYS_Document/_catalog/`。API 來源逐產品核對與代表性 RAG 查詢未完成。 |
| **Stage 3 — PyAnsys Source Intelligence** | 對 PyAnsys repos 建立套件/模組/符號/相依圖、上游來源與版本對照，並以 CodeGraph、Serena、codebase-memory 等交叉記錄查詢方式和覆蓋範圍。 | 以目前 checkout 的來源和 lock/package metadata 為準；索引只供導覽，不替代原始程式碼。 | 部分完成；本 repo CodeGraph 已重建。本機 `.venv` 有 49 個 `ansys-*`/`pyaedt` distributions，25 個產品 SDK 套件名中 15 個已安裝，已記錄 142 條套件相依邊；10 個版本化 SDK 字典已存在。未確認上游 PyAnsys 原始碼 checkout，跨 repo 模組/符號圖仍缺。詳見 [PyAnsys Source Intelligence](../architecture/PYANSYS_SOURCE_INTELLIGENCE.md)。 |
| **Stage 4 — Distributed Test Environment** | 設計 Remote ANSYS Worker 的隔離、授權、版本固定、工作目錄/輸入輸出界線、逾時/取消、日誌與證據回傳流程。 | 本階段只寫威脅/資料流與安全設計；未取得遠端主機、Ansys 授權與使用者明確執行許可前，不連線、不執行 ANSYS、不建立 worker。 | 未完成；可先做設計，runtime 與測試延後。 |
| **Stage 5 — Autonomous Debug Loop** | 定義受限制的診斷→最小修復→diff 審查→回歸測試→Evidence 更新流程，含可寫入路徑、命令 allowlist、停止條件與人工接手點。 | 不允許無界命令/檔案寫入、求解或自動提交；尚未完成授權與隔離前，只能文件化流程，不啟動自動除錯或測試。 | 未完成；需等 Stage 4 安全邊界成形。 |
| **Stage 6 — Cross-Agent Handoff** | 定義並記錄跨代理、跨電腦與不同模型可接續的任務包格式，保存來源、hash、版本、決策、未完成項與可重建命令。 | 先用不含 ANSYS 衍生材料的樣例驗證交接格式；跨機/跨模型傳輸須先確認資料可分享與接收端權限。 | 未完成；目前有階段計畫與本機 checkpoint，未做跨機 handoff。 |
| **Stage 7 — Authorized REA Research** | 僅對明確授權的目標，以 REA 做靜態 metadata/PE 分析；另將需宿主、除錯器或 runtime 的研究列為獨立授權工作。 | 每個目標都需可證明的使用權與研究授權；不載入/執行目標程式、不做 runtime research，除非取得相應授權。公開權未明時所有結果只留本機。 | 部分完成：使用者授權本機 v251 靜態 REA 盤點；目前 55 份 REA snapshots。此授權不代表公開散布權或 ANSYS runtime 許可。 |
| **Stage 8 — Ecosystem Expansion** | 依來源可得性擴展到其他 ANSYS 產品與 PyAnsys 套件；每批新增版本化來源、字典、映射與明確缺口。 | 按產品與版本分批；只有取得的來源才納入，不用相似名稱推定產品歸屬或 API 支援。 | 持續進行；候選與尚未分析產品列在 API coverage/REA evidence，尚未達全產品覆蓋。 |

### 階段執行順序與提交界線

- Stage 0 與 Stage 1 的文件盤點可並行；Stage 2 的目錄整理、官方文件分類、API/RAG 擴充可並行處理。
- 每個可獨立審閱的階段以本機 Git commit 保存；使用者已授權階段 commit。此工作分支含 ANSYS 衍生 API/REA/SDK 資料，不可直接 push；公開散布權未確認前不建立含該等資料的遠端分支或 PR。
- Stage 4–6 目前只做安全設計與交接格式，不啟動 Remote Worker、ANSYS、Debug loop、跨機傳輸或測試。
- tests/ 保留能檢查套件入口、技能發現、資源路徑與資料保護的實際測試；依使用者要求暫不執行，也不以測試數量作目標。若項目只重複低價值快照或沒有穩定行為斷言，再於後續審查中判斷是否保留。
- ANSYS_Document 轉換按來源相對路徑/產品/主題編章，PDF/HTML 輸出 .md 與來源清單；原件不刪除。轉換內容是否可公開尚未核定，因此產物留本機並排除於 GitHub 發布。

## 2026-10-28 延續進度

- SIwave REA 靜態候選新增：REA 6.0.0 檢視 v251 `AnsysEM/Ansys.Ansoft.SIwave.LibIronPythonCmd.dll`，取得 96 個 TypeDef、710 個 MethodDef；metadata complete。Evidence JSON 保留於被忽略的 `.audit/repo-restructure/rea-managed-v251/`，來源鍵 `siwave_libironpythoncmd_rea` 已接入 APIKB 與產品清冊。名稱與型別支持 SIwave 候選映射，但官方 API／支援狀態和宿主行為仍未核實。
- 缺口更新：REA 在 `commonfiles/fluids/lib/winx64/Ans.Fluent.CffWrapper.dll` 找到 Fluent namespace 的 wrapper，不能歸屬為 CFF API；LS-PrePost 與 Thermal Desktop 在 v251 managed inventory 中沒有明確命名的組件候選。三者繼續列為待來源項目，不以相似字串或共用元件補成 API 覆蓋。
- 全產品來源缺口摘要：coverage 清冊有 57 個產品 ID；12 個列有直接 snapshot、19 個只有產品組件證據、25 個尚未評估、1 個是未映射共用介面。另有 45 個產品沒有直接 snapshot、25 個產品列出 SDK package。16 個產品目前同時沒有直接 snapshot、REA 組件證據或 SDK package：`ansys_id_portal`、`ansys_id_sso`、`avxcelerate`、`cff`、`edupack`、`fensap_ice`、`icem_cfd`、`installation_and_licensing`、`ls_prepost`、`minerva`、`pyansys`、`reaction_chemkin`、`rigid_body_dynamics`、`saf`、`scade`、`thermal_desktop`。這是清冊狀態摘要，不代表產品沒有 API；每項需另找版本來源或記錄阻礙。
- ACP REA 靜態候選新增：REA 6.0.0 對 v251 `Addins/ACP/bin/win64/ACP.dll` 擷取 211 個 TypeDef、2,172 個 MethodDef；metadata 狀態為 complete。原始 Evidence JSON 留在被忽略的 `.audit/repo-restructure/rea-managed-v251/ACP.Core.json`，快照 source key 為 `acp_core_rea`，並補入 ACP coverage 與產品矩陣。這是組件靜態 metadata，不代表公開支援 API；`ansys-acp-core` 的 SDK 版本仍未確認。
- AQWA REA 靜態候選新增：REA 6.0.0 對 v251 `aisol/bin/winx64/Ans.AQWA.RemoteItf.dll` 擷取 13 個 TypeDef、74 個 MethodDef，metadata 狀態為 complete。原始 Evidence JSON 留在被忽略的 `.audit/repo-restructure/rea-managed-v251/Ans.AQWA.RemoteItf.json`；快照 source key 為 `aqwa_remote_itf_rea`，APIKB 與 REA source index 已更新。此為靜態 metadata，不確認公開支援狀態、宿主行為或完整 AQWA API。
- 前一批 REA 靜態分析新增三個 v251 元件候選：Engineering Data DataProvider（133 TypeDef／656 MethodDef）、DesignModeler Core（263／3,154）及 Material Designer Core（159／1,795）。來源鍵已加入 REA 索引及 APIKB allowlist，產品支援狀態未確認。當時重建輸出為 32,255 symbols、120,756 unique members、203,356 symbol-members、40,074 edges、151,611 FTS entries。未執行 APIKB 查詢。
- 後續批次新增五個 v251 REA 候選：Engineering Data Core（47／604）、TurboSystem AFDCore（6／255）、CCDCore（4／428）、CPDCore（17／276）及 RTDCore（4／278；依序為 TypeDef／MethodDef）。APIKB 共索引 55 份 REA snapshots、113 個來源鍵；最新重建統計為 32,328 symbols、122,597 unique members、205,197 symbol-members、40,074 edges、153,508 FTS entries。這些是靜態候選，未確認公開支援狀態；未執行 APIKB 查詢。
- Python SDK 人讀字典：新增 `scripts/api_extraction/render_sdk_dictionaries.py`，從具版本標記、非 protocol 的 SDK snapshots 產生每個 source key 的模組、類別、方法、屬性、函式與 docstring 頁面。依現有 snapshot 產生 10 份字典及索引，並接入完整 API 擷取批次流程；API Catalog 與 RAG 指南已加入入口。輸出是本機快照的衍生文件，尚未核對官方文件或宿主相容性，依授權決定不加入 GitHub。僅執行文件產生，不跑測試、驗證器或 API 查詢驗收。

- 本輪校正 API/RAG 文件與計畫現況：修正 API Catalog 的來源計數重複及 protocol 索引重複敘述，補足 Workbench 字典範圍；當時將計畫內舊的 13 份快照／8 份 native export 更新為 25 份 API/SDK/protocol 快照、50 份 REA 候選及 33 份 native export，後續批次再擴至 55 份 REA 候選。另新增 `scripts/api_extraction/render_protocol_dictionaries.py`，可從 11 份 protocol JSON 重建 RPC／message 欄位字典；協定索引與 `docs/index.md` 均提供入口，涵蓋 7 個產品協定及 4 個未映射來源。完整 API snapshot 批次流程會自動刷新 protocol 字典、版本化 SDK 字典及 managed REA snapshot 的[REA source index](../api_inventory/curated/rea/index.md)，列出 source key、assembly identity 與 metadata 計數。REA 專用批次也會刷新 REA 索引；[RAG 指南](../api_inventory/API_RAG_GUIDE.md)新增依 source key 查詢 REA 成員的步驟。APIKB 重建屬資料產生，仍不代表 API 查詢驗收。本輪未執行測試、驗證器或查詢驗收。

- 目錄階段歷史狀態：目標正式目錄為 `agents/`、`docs/`、`scripts/`、`src/`、`tests/`；舊 `evaluations/`、`manifests/`、`agents/skills-tier2/`、根層 `INSTALL_SOP.md`、`setup_skill_links.py` 與 `verification_report_stage5.json` 已移出。先前工作樹曾有 417 個 staged 路徑變更；這不是目前狀態。現行提交與工作樹狀態以本文件「目前 checkpoint」及 `git status` 為準。早先 commit 操作遭自動審查拒絕；不以替代方式繞過。此段不代表搬移驗收完成。

- 初版 API 盤點新增[全產品 API 來源與缺口索引](../api_inventory/PRODUCT_API_MATRIX.md)，以 57 個清冊產品 ID 串接當時的 13 份直接 API/SDK 快照及已映射 REA 組件證據。當時清冊有 10 個產品 ID 含直接快照、17 個產品 ID 有映射 REA 組件證據；此統計是初版基線，後續已擴充 API/SDK/protocol snapshots。索引明確標示版本、映射與涵蓋限制，不將缺少快照寫成產品沒有 API。
- 目錄盤點顯示正式 GitHub 根目錄只有五個目標資料夾；`agents/skills-workspace/` 是被忽略的本機評測輸出。名稱相近的 `scripts/maintenance/`、`scripts/verification/`、`scripts/skill_governance/`、`tests/evaluations/` 與技能內 `evals/` 責任不同，本輪沒有將它們合併。此為結構盤點，沒有執行目錄或連結驗證。
- System Coupling API 證據續作：REA 對 v251 `SysC.SystemCouplingParticipant.dll` 找到 x86_64 PE，但沒有 CLI metadata。LLVM 19.1.5 擷取 743 個 native export 名稱，其中 508 個可由 decorated symbol 還原出 symbol-derived signature。新增獨立 APIKB key 和 snapshot；批次建置後目前索引 88 個來源鍵、28,030 symbols、104,308 unique members、186,908 symbol-members、34,370 edges、130,943 FTS entries。此證據不確認 ABI、產品支援或 runtime 行為，也不代表完整 System Coupling API。
- DPF 元件 API 擷取續作：依安裝目錄中的 23 個 `Ans.Dpf.*.dll` 檢查 REA metadata 與 PE exports。23 個檔案均無 CLI metadata；LLVM 擷取 10,947 個具名 exports，其中 9,236 個可解碼符號名稱。23 份來源以 native 候選索引，合計 28,030 symbols、130,943 FTS entries。大型匯出集合可能含內部／執行期符號，未確認公開支援或呼叫慣例。Lumerical 另檢查三個 Python/Tcl interop DLL，加入 39 個 native export 候選並列入產品證據；API signatures 與 runtime 仍未確認。\n- Workbench API 擷取：repo `.venv` 安裝 `ansys-workbench-core 0.14.0`。新增可重建擷取器與 APIKB 快照，涵蓋兩個模組、四個類別、十九個方法、一個屬性及四個函式。快照來源鍵為 `workbench`，並更新產品 coverage 清冊。APIKB 重建回報 31,620 symbols、114,702 unique members、197,302 symbol-members、40,074 edges、144,927 FTS entries，來源鍵共 100 個。已擷取七份有產品映射的 gRPC/protobuf snapshots，另納入 DBU、Result Explorer 與兩個共用服務套件，保留四個未映射來源鍵。這些是協定 schema，不是宿主 API 驗證。此為索引建置結果，未執行 API 查詢驗收。人讀摘要見 [Workbench SDK 摘要](../api_inventory/curated/workbench/sdk_0_14_0_inventory.md)。尚未比對官方文件或於 Workbench 宿主執行。\n- 公開散布審查依使用者回覆暫停發布：目前沒有或不確定是否有可涵蓋 API/REA 衍生資料的公開散布許可。已查閱 Ansys 官方 v251 Legal Notices、v252 Legal Notices PDF 與 Limited Release License Agreement，並在[公開發佈檢查](../maintenance/PUBLICATION_REVIEW.md)記錄適用範圍限制。快照、REA 證據及引用這些來源的全產品索引留在本機工作分支，不推送公開 GitHub；此項待取得適用授權或書面許可後再處理。
- 目前 Git 狀態已確認搬移目的檔存在：評測三檔位於 `tests/evaluations/`，權限與 DAMG manifests 位於 `src/ansys_unified_mcp/resources/manifests/`；原根目錄路徑記為刪除狀態。搬移對照尚未綁定本輪完整目的檔 hash 審查；依使用者要求，本輪不執行驗證器或測試，也不宣稱搬移驗收完成。
- 路徑引用續查：掃描正式目錄、README、pyproject 與根設定，排除 archive/reviews 的歷史提及。將 `eval_report.json` 內舊絕對 `F:\\Ming_python\\ansys-unified-mcp\\evaluations\\ansys_mcp_eval.xml` 改為 `tests/evaluations/ansys_mcp_eval.xml`；並在[根目錄搬移清單](../maintenance/ROOT_REORGANIZATION_MAP.json)補入 12 項搬移的目前使用端。沒有執行測試或連結驗證。
- 技能路徑續查發現評測器仍接受舊 `agents/skills-tier2/<skill>/` 輸入並映射到模組分類後的技能。此解析行為及相應測試案例承接舊呼叫端，本輪保留相容邏輯，並在目錄分工文件說明新引用必須使用 `agents/skills/<module>/<skill>/`。
- 測試文件整理：`docs/testing/TEST_INFRA.md` 原有的四層制度、固定時限與 2026 R1 授權環境，與目前資料夾及 pytest 設定不一致。已改為現行 `tests/` 目錄導覽和選擇性執行原則；保留測試資料與案例，不要求每次執行全套。沒有執行測試。
- REA 範圍盤點：`AWP_ROOT251` 可讀取；本機安裝含 40 個頂層目錄、29,969 個 DLL（55,598,911,966 bytes）。分布及限制見[ANSYS 來源清冊](../maintenance/ANSYS_SOURCE_INVENTORY.md)。其中 `AnsysEM`、`Optical Products`、`AddPrint`、`commonfiles` 分別含 4,514、4,448、3,453、3,014 個 DLL。現有 REA 主清冊選出 47 個檢查結果（42 個 metadata complete、5 個 absent）；APIKB 另索引 55 份 REA snapshots 與 33 份 native export snapshots。兩組數字的母體不同；候選集不等於全安裝組件或完整產品 API。後續須先依產品文件與模組邊界列出可追溯的組件清單，再逐批擷取、映射或標記不可分析原因。這是來源盤點，未載入或執行組件。

- 目錄重構續查：工作樹正式根目錄為 `agents/`、`docs/`、`scripts/`、`src/`、`tests/`；舊根目錄 `evaluations/`、`manifests/` 已移除，目的位置 `tests/evaluations/` 與 `src/ansys_unified_mcp/resources/manifests/` 存在。`agents/skills/` 依模組收納，無 tier 目錄。文件語料、`skills-workspace/`、快取及執行資料仍是被 Git 忽略的本機資料，予以保留。本輪未執行目錄驗證器或測試。
- 對照前兩個 session 的目錄待辦後，將相似命名但用途不同的目錄邊界補入[目錄分工文件](../maintenance/FOLDER_STRUCTURE.md)：技能局部 scripts/evals 與 repo 級維護工具／MCP 評測、範例入口與技能實作、API 字典資料與 APIKB/docsearch 程式，以及產品 driver 與跨產品 bridge。PCB 範例入口仍委派給技能唯一實作；本輪只整理責任說明，未執行測試或驗證器。
- 修正[領域來源矩陣](../skills/DOMAIN_SOURCE_AND_SUPPORT.md)的技能路由與來源路徑：將不存在的舊技能 slug 換成現行模組路徑，將個人磁碟絕對路徑改為 `ANSYS_DOCS_ROOT` 相對位置，並保留未核實版本／支援狀態的限制。它由多個技能引用，屬共用來源索引而非重複技能入口；本輪未執行連結驗證。
- 對 `docs/examples/` 與 `agents/skills/` 共 402 個檔案做 SHA-256 同檔內容盤點，唯一重複群是三個 PCB 範例相容入口；讀取 wrapper 確認目標以來源 basename 對應 canonical skill script，因此保留相同殼檔及現有入口。`docs/` 的 48 個 Markdown／HTML／RST／TXT 文件沒有完全相同副本。另對 `scripts/` 與技能腳本共 130 個 Python／PowerShell／批次檔比對雜湊，沒有跨根完全相同副本。將 `docs/` 的十種子目錄責任補入目錄分工文件，區分歷史快照、審查證據、現行維護知識及操作計畫。這些盤點只涵蓋完全相同檔案，不代表已完成全 repo 語意去重；未執行測試或驗證器。
- 技能樹清理 31 個只含泛用文字的 `assets/README.md`／`references/README.md`，並移除共 41 個空資源目錄（32 個 assets、9 個 references；10 個原先為空）。README 原件及 SHA-256、移除路徑清單保存在被忽略的 `.runtime/folder-tree-reorganization/empty-skill-resource-backup/manifest.json`，技能搬移清單則保留為歷史遷移記錄。獨立 reviewer 確認備份 hash／bytes 相符、44 份 SKILL.md 存在且未發現刪除檔案的直接連結。未執行技能驗證器或測試。
- 對五個正式根目錄下 882 個現存檔案做完全相同的 SHA-256 盤點，發現 7 組重複：三個已知 PCB 相容入口、被忽略 `agents/skills-workspace/` 的評測 timing/grading 輸出，以及兩個空 `__init__.py` package markers。它們分別承載舊入口、本機對照結果與套件結構標記，均保留；此結果不代表語意近似檔已全數排除。

- 延續既有未提交工作與備份，未重置工作樹。使用者已明確要求每階段 commit，並於所有目標完成後 push；但本輪 commit 嘗試遭自動審查拒絕，故不得另用其他方式重試。REA 衍生資料的公開散布審查尚未完成，這些資料及其衍生索引仍留在本機，不納入公開推送。
- 新增[API 與文件檢索指南](../api_inventory/API_RAG_GUIDE.md)，記錄現有 APIKB／docsearch MCP 查詢流程、版本欄位、來源追溯與證據限制，並由 API Catalog 和文件首頁連結。未新增搜尋服務或觸發完整索引重建。
- 延續範圍仍未完成：57 個產品逐項來源與版本盤點、所有可取得模組的官方 API 對照、人讀字典擴充、代表性檢索結果驗收、公開散布審查及 GitHub PR。已整理 Mechanical、SpaceClaim、Workbench 與 10 份版本化 Python SDK 字典；REA 與 protocol 索引仍是靜態清單／schema 字典，不代表官方 API 對照已完成。
- 依使用者要求，本輪不執行測試或驗證器。新增文件尚未以 MCP 實際查詢驗收；文件索引是否已切換到最新正式資料庫仍未確認。上次未能確認的暫存視圖目錄可能仍在背景寫入，不清理該資料。
- 目錄整理續作：將 `src/Documentation_clean/api_kb.sqlite` 舊快取搬到 `.runtime/api-rag/legacy-src-api_kb-20261009.sqlite`，搬移前後 SHA-256 相同。更新目錄說明、整理報告與搬移對照；快取保留，未刪除。
- API 擷取續作：REA 對 CFX v251 `Ans.CFX.CadApi.dll` 和 `Ans.CFX.Acmo.dll` 回報 CLI metadata absent。REA artifact inspection 僅保留 PE root 與檔案 occurrence；LLVM 19.1.5 另擷取 43 與 17 個 export 名稱，沒有解碼簽名。兩個 native export snapshots 已加入 APIKB 來源設定。首次建置統計未增加，程式追查找到建置器 allowlist 未包含兩個新 key；補入後重建，symbols 與 FTS entries 各增加 60。當時 APIKB build 統計為 16,302 symbols、104,308 unique members、186,908 symbol-members、34,370 edges、119,215 FTS entries；來源設定含 62 個來源鍵。這是歷史 checkpoint。API Catalog 與 REA evidence 已更新。此項只證明靜態 export 名稱，不代表可呼叫或受支援 API；依使用者要求尚未跑測試或 API 查詢驗收。
- DPF 擷取續作：REA 對 v251 `Ans.Dpf.MechanicalResults.dll` 回報 CLI metadata absent；artifact evidence 僅記錄 PE root/occurrence。LLVM 19.1.5 發現一個 `LoadOperators` export，無可解碼簽名。快照與 APIKB source key `dpf_mechanicalresults_native` 已加入既有建置器，索引增加 1 symbol 和 1 FTS entry。組件 SHA-256、REA Evidence ID、export snapshot hash 與限制已記入 API Catalog 和 REA evidence。未執行產品宿主或查詢驗收。

## 目標與現況

GitHub 的正式根目錄目標為 `agents/`、`docs/`、`scripts/`、`src/`、`tests/`。官方文件原件與生成索引留在本機忽略目錄。API 範圍涵蓋所有 ANSYS 產品，自 2025 R1 起以可取得來源為限；每項缺口需標記原因，不宣稱完整。

已完成的前置工作：既有技能 tier 根合併、文件去重初篩、API 擷取器與覆蓋清冊擴充、Mechanical/SpaceClaim REA 摘要，以及專用分支建立。當前工作樹將 44 個技能依模組分類，驗證器與技能查找器支援巢狀目錄；`evaluations/` 已搬到 `tests/evaluations/`，執行期 manifests 已搬到 `src/ansys_unified_mcp/resources/manifests/`。最新目錄與技能驗收通過；權限 manifest 存在，DAMG 讀取結果為 73 節點。

## 執行順序與交付界線

1. 目錄與技能整理、API 來源盤點及字典/RAG 工作並行推進。以 `api_coverage.json` 作逐產品狀態來源。現有 schema 已記錄 product、snapshots、REA evidence、SDK package、mapping status 與 documentation coverage；後續需補來源版本、證據狀態、限制及下一步欄位。這些是待擴充欄位，不代表現有資料已齊全。沒有來源時需記錄已查範圍和具體阻礙。
2. 完成人讀字典與 AI 檢索文件。API/RAG 條目需連回可追溯來源，區分官方文件、SDK、managed metadata、native exports 與 protocol schema；不把靜態候選描述為完整或受支援 API。
3. 使用者已明確授權逐階段 commit，並在所有目標完成後 push。每次提交只納入已完成且確認可分享的檔案；REA/SDK/Ansys 衍生資料在權限未確認前留本機。已追蹤資料需從提交範圍明確排除，不能只依賴 ignore 規則。
4. 驗證目前暫緩。未執行測試、驗證器、代表性 API/RAG 查詢、搬移雜湊核對或宿主求解；不可把歷史測試紀錄當作本輪驗收。

目錄收尾：根目錄過時的 `INSTALL_SOP.md` 已移除，由 `docs/deployment/DEPLOYMENT_SOP.md` 作為安裝與操作入口。技能連結工具已歸入 `scripts/skill_governance/`，`setup_skill_links.py` 保存唯一實作，`setup_skill_junctions.py` 保留舊命令列相容入口。README 與文件索引已指向現行部署手冊，README 的目錄與套件說明已更新以移除過時的 `drivers/sim_impl.py` 描述。`mcp_server.py` 仍留根目錄，供既有客戶端相容啟動。

技能搬移對照已發布至 `docs/maintenance/SKILL_MIGRATION_MAP.json`，包含來源路徑、目前模組路徑、SHA-256 與檔案大小。清單涵蓋 44 個技能的 472 個檔案：34 個 tier-root 技能取自本機搬移 manifest，另 10 個原先平鋪於 `agents/skills/` 的 domain router 以搬移前 Git HEAD 記錄；本機原件備份仍保留於被忽略的 `.runtime/folder-tree-reorganization/skill-root-migration/originals/`。

根目錄遷移對照見 `docs/maintenance/ROOT_REORGANIZATION_MAP.json`，記錄評測、manifests、報告、技能連結工具、部署手冊及三支技能治理腳本的來源、目的和搬移前 SHA-256。`document_sources.json` 是新加入的套件資源，並非舊根目錄 manifest 的搬移項目。

API 文件切片已擴展至已安裝的 ANSYS 2025 R1 樹。`.audit/repo-restructure/rea-managed-v251/` 的來源盤點有 47 份檢查結果，其中 42 個 managed metadata complete、5 個 absent；APIKB 索引 55 份 REA snapshots。這兩組數字的母體不同；另有 DPF 與 CFX native PE 證據。APIKB 現索引 55 個 REA 候選來源鍵；這些候選涵蓋 shared、managed 與 add-in 元件。RSM JobManagement 是新增的未映射 shared candidate。新增八個 product add-in 候選來源來自 AQWA、CFX、Fluent、Icepak、Meshing、Polyflow、Sherlock 與 HFSS host add-in；另新增 Discovery 目錄七個 API assembly source keys，以及 Maxwell、Q3D、Icepak 三份 Ansoft add-in key；這些是靜態 implementation metadata，不等同公開或受支援 API。Zemax ZOS-API 兩組件及三個未映射 Ansoft add-in 已由 v251 安裝樹加入 REA 靜態候選；官方簽名對照仍待處理。API Server、Material Designer、TurboSystem、Units、Vista TF 與其他產品映射仍待處理；四個 managed-metadata-absent PE 已新增 native export 候選清冊，但函式本體、呼叫慣例與官方支援狀態尚未分析。完整產品 API 分類與散布權審查未完成；原始 REA JSON 留在忽略的 `.audit/`。

## 已完成工作

本節彙整前兩個 sessions 的成果與本輪新增證據。使用者要求目錄與 API/RAG 工作並行，並暫緩驗證；測試及驗收留在後續階段。

- 專案 GitHub 根目錄已整理為五個正式目錄：`agents/`、`docs/`、`scripts/`、`src/`、`tests/`。本次續接先核對目前工作樹與遷移報告，未執行測試或驗證器。根層的 `INSTALL_SOP.md`、`setup_skill_links.py`、`verification_report_stage5.json` 已移出或刪除。根層 `mcp_server.py`、README、設定及套件管理檔保留作相容入口或必要專案檔。
- 本輪清除工作樹內殘留的 `agents/skills-tier2/` 快取目錄：92 個索引檔、11,194,336 bytes 移至被忽略的 `.runtime/folder-tree-reorganization/archived-caches/skills-tier2-zvec-grep/`，並保存逐檔 SHA-256 清單；本機 `.zvec-grep/`、ANSYS 語料、快取及 wheel/sdist 建置輸出保留並排除於 Git。以目前存在的追蹤檔與非忽略新檔盤點，GitHub 候選根目錄為上述五個正式目錄。
- 44 個技能已移至 `agents/skills/<module>/<skill>/`，分屬 14 個模組。技能只保留實際使用的 `references/`、`scripts/`、`assets/`、`evals/`，不建立 tier 分類或空資源目錄。搬移雜湊表及本機復原副本位置見[技能搬移清單](../maintenance/SKILL_MIGRATION_MAP.json)。
- 續查 Mechanical／SpaceClaim 字典時，從 Python.NET System.Reflection 產生的 v251 `spaceclaim_api.json` 讀出五筆 `DatumPlaneCreator.Create` 反射簽名（含 `ISelection` overload）；先前的四筆摘要不完整，已更正文檔並列出全部 snapshot 參數型別與來源識別。參數預設值和官方 CHM 對照仍未核實。
- `evaluations/` 已併入 `tests/evaluations/`；執行期 manifests 已併入 `src/ansys_unified_mcp/resources/manifests/`；技能治理工具已歸入 `scripts/skill_governance/`。根目錄遷移表見[根目錄搬移清單](../maintenance/ROOT_REORGANIZATION_MAP.json)。
- ANSYS 文件歸位、重複副本處理、備份和當時的雜湊結果記錄於[資料夾清理報告](../maintenance/FOLDER_CLEANUP_REPORT.md)。官方文件原件及完整 REA JSON 保留於本機忽略資料夾，不納入 GitHub 結構。
- 歷史基線：前兩個 sessions 記錄 API 覆蓋清冊 schema 3、57 個產品 ID、13 份產品／SDK API snapshot，以及 SDK 快照、版本標記和 APIKB 接線。這不是現況統計。最新來源鍵與 REA 數量見本文件「目前 checkpoint」；ACT Interfaces、LS-DYNA ACT Interfaces、AnsysEM CoreDotNet、Ansys Additive 等仍須依官方資料確認產品映射及支援狀態。
- 歷史 APIKB checkpoint：較早紀錄曾有 59 個來源鍵，之後又記錄 100 個來源鍵；兩者均已過時。現況以「目前 checkpoint」列出的 113 個來源鍵為準。最新 REA 範圍另記於 [REA 證據摘要](../api_inventory/REA_EVIDENCE.md)。靜態 metadata、native exports 和 protocol schema 不證明官方支援狀態或宿主行為。APIKB 的歷史 build 統計只作時間點記錄，不作本輪驗收依據。
- 技能 evaluator 的舊 tier 相容路徑已修正為從舊路徑辨識技能名稱，再於巢狀模組目錄唯一解析；legacy Markdown 路徑回歸測試通過。獨立複查確認 44 個技能、14 個模組、兩份搬移對照的來源雜湊／檔案數與目的路徑相符，正式根目錄為五個目錄。此複查是靜態目錄／對照審查，未執行 ANSYS。
- 先前 session 曾記錄 APIKB build、APIKB MCP tools 及技能 evaluator discovery 各 7 項定向測試通過。這些是歷史結果，本輪沒有重跑，也不代表 ANSYS host runtime 或完整產品 API 覆蓋。
- 前兩個 sessions 留有目錄、技能、APIKB、文件索引及套件封裝等既有檢查紀錄。個別結果與限制應以 checkpoint 和相關報告為準；本輪沒有重跑。

## 歷史驗收紀錄

- 五個正式根目錄、技能分類、評測與 manifests 搬移、引用修正及 44 個技能掃描已完成。`verify_directory_topology.py` 通過；wheel 建置成功，拆包後可載入 permission manifest（5 類）與 DAMG（73 節點）。Windows 暫存目錄 ACL 阻止 pip `--target` 安裝，因此未驗證乾淨環境 pip 安裝。
- 技能驗證 44 個通過；技能完整性 90 項通過；鏡像同步 dry-run 為 370/370 檔案雜湊相同。API inventory/APIKB 測試 31 項、文件同步 34 項、phase-4/evaluation 22 項、M5 remediation 5 項及技能驗證 3 項曾分組通過。
- 人讀導覽為 `docs/api_inventory/API_CATALOG.md`；新增 Mechanical 與 SpaceClaim v251 條目頁，並清楚區分官方文件確認與 snapshot-only 簽名。AI 檢索沿用 APIKB 查詢簽名與來源，docsearch 查詢官方文件。字典頁目前未納入 docsearch 索引。API 覆蓋清冊列 57 個產品 ID，25 份 API／SDK／protocol snapshot（21 份映射至 12 個產品 ID，4 份未映射）。產品 ID、文件版本、SDK snapshot 和 REA 組件是不同證據層，不能互相替代。官方文件、SDK、REA 與版本覆蓋尚未逐產品完整核實。
- 已記錄 22,987 個文件歸位操作、45,984 個來源／目的雜湊比對且 0 不一致；16 份確認重複的文件副本移除，清理報告與本機可回復備份索引保留於 `docs/maintenance/FOLDER_CLEANUP_REPORT.md` 及被忽略的 `.runtime/folder-document-cleanup/`。

## 尚未完成

1. **目錄收尾**：五個正式根目錄和現行目的路徑已整理。搬移對照目前保存來源 hash、大小和使用端；待補目的檔 hash、完整語意去重和獨立搬移審查。已做文字層級的目前路徑引用盤點並修正評測報告的舊絕對路徑；連結目標是否可用尚未驗證。依使用者要求，暫不執行測試或驗證器。
2. **API 來源盤點**：`api_coverage.json` 列 57 個產品 ID。APIKB 索引 113 個來源鍵：25 份 API／SDK／protocol 快照（21 份映射至 12 個產品 ID、4 份協定來源未映射）、55 份 REA 靜態候選及 33 份 native export 快照。人讀[產品 API 來源與缺口索引](../api_inventory/PRODUCT_API_MATRIX.md)列出來源與缺口。仍需逐產品核對 2025 R1 起可取得的官方文件、SDK、REA 和版本；不可將候選證據標成完整或受支援 API。
3. **人讀字典與 AI RAG**：Mechanical／SpaceClaim v251 有整理型 API 使用字典；Workbench SDK 有來源摘要；10 份有版本標記的 Python SDK snapshots 已產生模組／成員字典；11 份 protocol snapshots 已產生逐 RPC、message 與 field 的人讀索引，enum 成員未包含在原始 snapshot。55 份 managed REA snapshot 另有 source key、組件身分與 metadata 計數索引，完整 member 檢索仍使用 APIKB。Mechanical `AddFixedSupport()` 有官方文件呼叫形式佐證，回傳型別仍來自 snapshot；SpaceClaim 五個 `DatumPlaneCreator.Create` overload 仍是反射 snapshot，尚未逐項比對官方 CHM。APIKB 已依目前來源重建，但代表性 API 查詢驗收、官方文件交叉核對與 docsearch 索引切換狀態仍待確認。其他產品的來源差異、版本追溯和官方文件對照須分批擴充。
4. **獨立審查與驗收**：資源佔位清理曾經過獨立 reviewer；完整根目錄搬移與本輪路徑修正尚未完成獨立審查。使用者要求先不做驗證，因此定向測試、連結目標檢查、搬移目的檔 hash 對照及代表性 API/RAG 查詢均待後續安排。APIKB 重建已作為資料產生步驟完成，但不代表查詢行為已驗收。既有測試結果只保留為歷史證據。
5. **公開發布**：使用者表示沒有或不確定公開散布許可。Ansys 軟體、組件與文件的適用條款須按實際授權判斷；在取得授權或書面許可前，REA/SDK 快照、衍生字典及其來源索引留在本機，不提交或 push 這些資料。純目錄文件及不含衍生內容的工具程式，需逐檔確認後才可納入階段提交。已追蹤的 API 清冊與證據文件仍須排除在公開變更之外。完整風險記錄見[公開發佈檢查](../maintenance/PUBLICATION_REVIEW.md)。

## 驗收與限制（歷史紀錄與待辦）

- 根目錄正式目錄恰為五個，忽略的本機語料、快取和建置輸出不計入 GitHub 結構。
- 歷史驗收：當時技能驗證器發現 44 個技能，並記錄舊技能路徑、tier manifest 引用及死連結清零。本輪未重跑，不作目前驗收證據。
- 目前已執行的分組測試和 wheel 建置結果如上；全套單元測試與 pip 乾淨安裝尚未通過驗收。代表性 API 查詢及各產品 RAG 覆蓋仍需續驗。
- 不執行 ANSYS 求解。依賴授權或特定宿主的項目明確標示未驗證。



