# ANSYS MCP 精簡與更新計畫

基準日為 2026-11-17（台北）。本計畫涵蓋自研 MCP、現有 Skill、官方 MCP 與 SDK 的分工。實作前先確認團隊優先工作負載。此版提出執行順序與驗收條件，尚未進入遷移。

## 先精簡日常入口，再逐項採用官方

**官方 MCP 接手已驗證的通用產品操作。自研 MCP 保留 Workbench／ACT、Geometry／SpaceClaim、DPF、團隊專用操作與跨產品交接。Skill 負責選用工具、工況設定原則和工程驗收。**

官方工具清單用來找替代候選，也可參考官方「依連線狀態顯示工具」的設計。採用的依據是使用者工作如何完成。相同名稱需要核對操作對象、執行狀態、輸入格式與輸出；例如官方 `open_project` 開 Mechanical `.mechdb`，自研同名工具走 Workbench 橋接。以三套環境區分升級風險：既有自研環境、官方試點的獨立 Python 環境、之後才可能更新的自研 SDK 環境。[官方 Mechanical 工具](https://mechanical-mcp.docs.pyansys.com/version/stable/user_guide/tools_and_capabilities.html) · [自研 Workbench 開存檔](../../src/ansys_unified_mcp/products/workbench/tools.py#L303)

[218 個工具與 49 個 Skill 逐項清冊](ANSYS_MCP_INVENTORY_AND_DISPOSITION.md) 提供每個名稱的原始碼位置、建議處置與公開方式。推薦優先順序是 **P0 盤點與後端標記 → P1 精簡可見性 → P2 官方 Mechanical 試點 → P3 更新團隊流程 → P4 其他產品試點 → P5 相容退場**。

## 本機基準與證據限制

| 項目 | 本次核對結果 | 用於決策 |
| --- | --- | --- |
| 自研套件 | `ansys-unified-mcp 3.0.0`，自有 FastMCP STDIO 入口，套件宣告 Python ≥3.10。Git HEAD `130208d`。 | 自研與官方分開管理依賴與發行。 |
| MCP 工具 | 18 個產品工具模組共 182 個，另有 8 個共用工具模組共 36 個。靜態列舉與本次 Codex 目錄均為 218 個名稱，集合完全相符。Mechanical 模組 46 個，Workbench 模組 44 個，其中含 `mechanical_run_batch_script`。 | 數量口徑為本次可見的主要工具名稱。別名、動態路由與各客戶端視圖另測。 |
| Skill | `agents/skills` 有 49 個 `SKILL.md`，本機掃描與 Git 追蹤數相符，包括 10 個領域／基礎路由 Skill、38 個專項 Skill、1 個開發審查 Skill。 | 先更新既有技能與入口。Motion、SimAI、Discovery 及 Prime Meshing 等有技能或 SDK 線索，沒有各自的頂層產品工具模組。 |
| 安裝線索 | `AWP_ROOT251`、`AWP_ROOT252`、`AWP_ROOT261` 皆指向存在的目錄。 | 建立 2025 R1／2025 R2／2026 R1 測試欄位。可用產品、Service Pack、gRPC、ACT 和授權仍需各自探測。 |
| 已有工作 | 盤點時，抽中面批次工具、Geometry 派送、IronPython 腳本與 Geometry 工具共有 4 個既有未提交變更。 | 抽中面工作與後續精簡分開交付。其基準先以使用者認可的工作樹版本固定。 |

[套件宣告](../../pyproject.toml) · [啟動入口](../../src/ansys_unified_mcp/__main__.py#L24) · [技能庫](../../agents/skills/README.md) · [既有目錄與知識庫計畫](FOLDER_TREE_REORGANIZATION_PLAN.md)

`uv.lock` 為版本基準，與執行環境實際載入版本分開記錄。此次核對 FastMCP 3.4.8、Mechanical SDK 0.13.2、Fluent 0.42.1、Geometry 0.17.1、DPF 0.16.1、Workbench 0.14.0、MAPDL 0.74.1、optiSLang 1.6.0、LS-DYNA 0.12.1、Prime Mesh 0.10.5、Sherlock 2.1.4。[鎖定檔](../../uv.lock)

## 官方來源與採用順序

官方 `pyansys` 是 Python 套件組合。公開開發主線的 `[mcp]` 目前列六套產品 MCP。PyPI 最新穩定 bundle 為 `2026.1.3`，此版沒有 `[mcp]`。預覽版 `2027.1.0b3` 有 `[mcp]`，要求 Python 3.12 起。下表分別記錄主線鎖定與產品獨立發行版，沒有把主線設定當成任何已發行版的鎖定檔。[官方主線套件清單](https://github.com/ansys/pyansys/blob/main/pyproject.toml) · [穩定版設定](https://github.com/ansys/pyansys/blob/v2026.1.3/pyproject.toml) · [預覽版資料](https://pypi.org/project/pyansys/2027.1.0b3/)

| 產品 MCP | 主線鎖定 → 最新獨立發行 | 官方能力／近期變更 | 自研處置 |
| --- | --- | --- | --- |
| Mechanical | 0.3.1 → 0.3.1 | 模型摘要、分頁物件探索、已安裝的 API 文件、屬性預覽、結果匯出。[發行說明](https://github.com/ansys/pymechanical-mcp/releases/tag/v0.3.1) | P2 第一個試點。先接手唯讀工具，之後才比較求解與腳本狀態。 |
| Fluent | 0.5.0 → 0.8.0 | 0.8.0 加入嵌入擴充點，強化工作階段歸屬、斷線清理與重連。[發行說明](https://github.com/ansys/pyfluent-mcp/releases/tag/v0.8.0) | P4。先比既有 case、狀態和結果。UDF、TUI、Journal 和語義對應各自驗收。 |
| MAPDL | 0.3.2 → 0.3.2 | 工作階段和 APDL 工具。0.3.2 的發行紀錄列文件修正。[發行說明](https://github.com/ansys/pymapdl-mcp/releases/tag/v0.3.2) | P4。用既有輸入檔核對批次流程、日誌、結果與回傳狀態。 |
| AEDT | 0.2.4 → 0.3.2 | 支援 AEDT 工作階段和多項電磁應用。0.3.2 以依賴維護為主。[發行說明](https://github.com/ansys/pyaedt-mcp/releases/tag/v0.3.2) · [產品工具](https://github.com/ansys/pyaedt-mcp) | P4。先比 HFSS／Maxwell，RLCG 與 Q3D 以現有工程樣件另驗。 |
| CFX | 0.2.0 → 0.2.0 | CFX 模型檢查、腳本、求解與 CFD-Post 入口。[產品工具](https://github.com/ansys/pycfx-mcp) · [發行說明](https://github.com/ansys/pycfx-mcp/releases/tag/v0.2.0) | P4。保留 Workbench 建系統。既有 `.def` 批次求解另做替代驗收。 |
| Lumerical | 0.1.0 → 0.1.0 | FDTD、MODE、DEVICE、INTERCONNECT 工作階段及持續 Python 執行。[套件文件](https://pypi.org/project/ansys-lumerical-mcp/) | P4。真實光學工作優先評估官方。自研波導基準另行標明用途。 |

[PyAnsys Common MCP](https://github.com/ansys/pyansys-common-mcp) 是官方共用開發框架。[PyPI](https://pypi.org/project/ansys-common-mcp/) 顯示獨立版 0.3.6。先吸收工作階段與工具可見性的設計，等相容性和維護收益有證據再提案更換自研底層。[PyAnsys Geometry](https://github.com/ansys/pyansys-geometry)、[PyWorkbench](https://github.com/ansys/pyworkbench)、[PyDPF](https://github.com/ansys/pydpf-core)、[PyOptiSLang](https://github.com/ansys/pyoptislang) 和 [PyDYNA](https://github.com/ansys/pydyna) 為可對照的官方 SDK，未列入上述六套產品 MCP。官方 [AALI 文件](https://docs.aali.ansys.com/) 將其定位為供 Ansys 產品與自家工作流程使用的 AI 基礎設施。

Ansys 整體產品亮點頁列 2026 R1。開發者入口已列 **2026 R1 SP03** 文件更新、PyLumerical MCP 與 DPF operator 搜尋。版本遷移優先關注三件事：SpaceClaim 2024 R2 是最後一個使用 ACIS 核心的版本、2025 R1 起使用 Parasolid；2026 R1 加入無圖形介面的 Geometry Service 安裝項；DesignXplorer 已列為棄用，官方建議 optiSLang 容器。幾何驗收以實際後端為單位，新最佳化案例優先評估 optiSLang。[產品亮點](https://ansys.synopsys.com/products/release-highlights) · [開發者更新](https://developer.synopsys.com/whats-new) · [SpaceClaim Release Notes](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/pdf/Ansys_Release_Notes.pdf) · [安裝更新](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/global_releasenotes/globrelnote_install.html) · [DesignXplorer 公告](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/global_releasenotes/ReleaseNotesAdvisories.html)

## 各模組要精簡或更新什麼

| 自研模組 | 工具數 | 保留、精簡與更新 |
| --- | ---: | --- |
| Mechanical | 46 | **保留** BOM 指派、群組接頭、轉質點與團隊報告。**收斂**低頻載荷／拘束／結果變體。**更新**靜力與模態 Skill，定義分析選取、單位、網格和驗收。替代候選先比連線歸屬與讀取，再比較修改、求解、腳本。 |
| Geometry／SpaceClaim | 27 | **保留**抽中面、去特徵、接觸壓印、RAM／散熱器簡化、CAD 匯入匯出。**收斂**建塊、球體、BGA 等工具至對應任務。**更新**抽中面與簡化 Skill，記錄來源、選取、厚度、略過原因、命名群組及重開據點。分開驗證 Desktop、Discovery／Geometry Service。 |
| Workbench | 44 | **保留**桌面橋接、Workbench 開存檔、Journal、Mechanical 啟動和專案交接。**收斂**靜力、熱、模態、振動等建系統工具至按需入口。沿用現有通用建系統入口前，逐項核對參數、命名與預設。CFX、MAPDL、Fluent 批次入口按各試點結果處置。 |
| DPF | 2 | **保留**結果檔模型摘要、結構結果抽取。**更新**回傳結果類型、單位、時間／頻率步、運算子可用性、來源與版本。Skill 負責決定要查哪些量與參考解。 |
| Fluent | 19 | **收斂**一般 case／mesh 讀寫、初始化、迭代和殘差工具到官方候選。**保留按需**UDF、TUI、Journal、語義對應與 Workbench 交接。先比較同一份 case 的模型狀態與分析日誌。 |
| MAPDL | 3 | **比對官方**工作階段、APDL 及既有輸入檔。**保留按需**無法由官方等價接替的批次啟動與輸出收集。Skill 管元素、載荷、巨集與輸出判讀。 |
| LS-DYNA | 7 | **保留按需**Keyword Deck 建立與匯出、求解及 LS-PrePost。**更新**跌落、衝擊 Skill 與輸出檢核。顯式結果檔與 DPF `.rst` 分開。 |
| optiSLang | 6 | **保留按需**連線、專案、腳本、MOP 和 Workbench 交接。**更新**DOE、變數範圍和代理模型驗收。將 DesignXplorer 舊檔當成相容流程盤點。 |
| AEDT | 4 | **試點官方**HFSS／Maxwell 工作階段。**保留按需**已有 RLCG 或檔案特化流程。先釐清每個入口是否連商用引擎或回傳近似值，再判斷取代範圍。 |
| Optics | 4 | **採用候選**官方 Lumerical 處理真實工作階段。Zemax／Speos 各自確認。**更新**波導與光度入口的後端標記。Skill 分開整理有授權的模型流程與教學基準。 |
| Systems | 3 | **保留按需**System Coupling、Twin ROM 入口。**更新**各工具的真實後端或基準模式、時間步、熱量平衡與結果來源。 |
| Granta | 4 | **保留按需**材料查詢、曲線與合規評估。**更新**資料來源、版本、單位、缺值狀態與真實資料存取。 |
| Sherlock | 3 | **保留按需**PCB 熱疲勞／振動壽命。**更新**載入的材料、堆疊與分析條件。用核准的壽命基準或已知案例解，不以工具註冊推論授權。 |
| Icepak | 2 | **保留按需**連線與熱分析。**更新**熱平衡、溫度參考與實際後端。AEDT 支援 Icepak 應用不直接等同自研算例的一致性。 |
| Rocky | 2 | **保留按需**DEM 入口。**更新**接觸模型、時間步、後端與顆粒計算驗證。 |
| Motor-CAD | 2 | **保留按需**效率工作點。**更新**扭矩、轉速、單位、損耗與真實引擎／基準分類。 |
| AQWA | 2 | **保留按需**升沉算例。**更新**波浪條件、質量設定與基準假設。 |
| Chemkin | 2 | **保留按需**零維反應器入口。**更新**機理、單位、初始狀態及執行後端。 |
| 共用工具 | 36 | **保留**版本、連線、路由、知識檢索、作業狀態。**收斂**管理用途的重建索引、重複的安裝診斷入口和低頻 API 查詢。**移到 Skill 主導**五個高階工作流程的決策與驗收，保留必要執行函式。Sound 三個計算工具按需呈現並說明計算來源。 |

合計 218。可見性、後端真實性和物理驗收是三個獨立欄位。含解析或數值基準的 driver 要逐工具查證。凡名稱含 `solve`，執行路徑仍須由程式、日誌或產物確認。[光學 driver 範例](../../src/ansys_unified_mcp/products/optics/driver.py) · [Systems driver 範例](../../src/ansys_unified_mcp/products/systems/driver.py)

其他模組可從下列官方 SDK 或產品 API 尋找接點。這些來源建立整合候選，實際支援範圍依案例驗證。每個 SDK 升級案只在要採用時才確認授權、安裝版本及輸入輸出。

| 本機模組或技能領域 | 已核對的官方參考 |
| --- | --- |
| Systems、Optics | [PySystemCoupling](https://systemcoupling.docs.pyansys.com/) · [PyTwin](https://twin.docs.pyansys.com/) · [PySpeos](https://speos.docs.pyansys.com/) · [Zemax ZOS-API](https://optics.ansys.com/hc/en-us/articles/42661790380179-ZOS-API-NET-An-Overview) |
| Granta、Sherlock、Icepak | [Granta MI／PyGranta](https://developer.synopsys.com/docs/granta-mi) · [PySherlock](https://sherlock.docs.pyansys.com/) · [PyAEDT Icepak 範例](https://examples.aedt.docs.pyansys.com/version/dev/examples/aedt/icepak/index.html) |
| Rocky、Motor-CAD、AQWA、Chemkin | [PyRocky](https://rocky.docs.pyansys.com/) · [PyMotorCAD](https://motorcad.docs.pyansys.com/) · [AQWA 參考手冊](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/pdf/Aqwa_Reference_Manual.pdf) · [PyChemkin](https://github.com/ansys/pychemkin) |
| Sound、Prime Mesh、ACT | [PyAnsys Sound](https://sound.docs.pyansys.com/) · [PyPrimeMesh](https://prime.docs.pyansys.com/) · [Ansys 開發者文件與 ACT 資源](https://developer.synopsys.com/docs) |

## 跨模組要遵守的共同設計

- **工具公開。** 沿用 `all` 作相容基準。用現有 `core` 與領域路由作低工具數試點，用 `ans_session_set_workspace` 當需要跨產品時的選項。舊別名維持按需。逐一驗證 Codex、Kiro、Antigravity 是否會刷新工具清單。可見性屬於介面選項；會話與操作權限由服務端另行驗證。[工具範圍指引](../deployment/MCP_TOOL_SCOPING_GUIDE.md) · [領域探索](../../src/ansys_unified_mcp/tools/meta_router_tools.py#L693) · [別名開關](../../src/ansys_unified_mcp/shared.py#L116)
- **同一工作階段有明確歸屬。** 保存 ANSYS 版本、端點識別、工作階段歸屬和工程檔類型。若兩個 MCP 都可修改同一模型，由工作流程指定單一寫入端。附接既有 GUI 後斷線，檢查原程序與使用者專案仍在。既有專案、來源幾何與結果檔用副本做驗收。
- **結果說清楚來源。** 統一表示商用引擎、內建基準、僅驗參數或不可用。區分提交、執行中、完成、失敗、逾時、取消與清理結果。商用後端、求解器版本、時頻步、單位及輸出檔可從結果或日誌追溯。已有欄位優先重用。
- **工程規則可以重用。** Skill 定義選取、單位、前置條件、警告處置與驗收。需要重複使用的執行邏輯留在工具或版本化腳本。模型修改與求解前後要能辨識目標，任何停用入口都要有替代呼叫和復原說明。
- **依賴分開升級。** 官方試點安裝單一 MCP 並鎖定完整依賴。SDK 升級每次選一項，先做 API、transport、案例和回退驗證。Geometry 優先評估 0.17.1 對 0.18.2；Mechanical SDK 是否由 0.13.2 升至 0.13.5，安排在官方 MCP 對照之後，避免同時變更兩側基準。[Geometry 0.18.2](https://github.com/ansys/pyansys-geometry/releases/tag/v0.18.2) · [PyMechanical 版本紀錄](https://mechanical.docs.pyansys.com/version/stable/changelog.html)
- **沿用既有架構限制。** 遠端 worker、任意腳本跨機調度及文件索引公開，沿用既有專案規劃與授權。官方獨立 MCP 的 HTTP 或 gRPC 能力不直接改變自研 Workbench 橋接的範圍。[遠端設計與限制](../architecture/REMOTE_WORKER_AND_DEBUG_SAFETY.md)

## BMAD 交付階段與工作故事

各階段由執行者交付原始證據，獨立檢查者依下方門檻驗收。P0 與 P1 可各自整理資料；P2 實機比較依賴 P0 的版本矩陣。P3 共通 Skill 可先撰寫，涉及工具切換的故事要等 P2 確認。P4 每次只切換一個產品。P5 按工具批次退場。[BMad 規劃方法](https://docs.bmad-method.org/plan/plan-the-work/)

| 階段 | 工作故事（依序） | 責任角色與交付物 | 完成條件 |
| --- | --- | --- | --- |
| **P0 建立基準** | 01 匯出目前工具、別名、profile、Skill 清單；02 建立本機 251／252／261 的產品、授權、SDK 和案例矩陣；03 盤點疑似基準入口的實際後端。 | 維護者記錄原始工具清單與安裝證據。CAE 負責人指定案例、量測輸出、單位及參考容差。 | 218 個入口都可追溯。每個支援欄位標明實測或待驗。基準、無授權和未知結果可被辨識。 |
| **P1 精簡工具曝光** | 01 記錄三個客戶端的目前工具清單；02 試用 core／workspace，保持相容設定；03 驗證動態發現、呼叫與舊別名；04 更新 guide 與技能路由。 | MCP 維護者實作設定選擇與相容性。檢查者保存三個客戶端啟動後、發現後及呼叫後的 `tools/list`。 | 指定領域前，Core 保持只列共用工具。另一工作階段的清單不受影響。常用流程可查找並呼叫所需工具。相容 profile 的必要流程仍通過。 |
| **P2 官方 Mechanical 試點** | 01 隔離安裝官方 MCP；02 比較既有模型查詢、截圖與匯出；03 核對 Workbench 嵌入、附接與斷線；04 比較屬性預覽與修改；05 比較腳本成功、錯誤與逾時；06 按授權比較正常求解，再列出等價、需轉換及保留項目。 | Mechanical 維護者和 CAE 檢查者交付 A/B 比較表、樣本與輸出。 | 唯讀入口可先通過 B04／B05／B12。腳本與求解等到 B13／B14 通過後才切換。受限或未測者保留原入口或相容設定。 |
| **P3 更新團隊核心流程** | 01 保留 BOM、接頭、質點工具；02 更新 SpaceClaim 抽中面與 STEP 重開證據；03 整理 Workbench → Mechanical → DPF 交接；04 將靜力、模態、衝擊、振動、熱翹曲與訓練的判斷和驗收更新到既有 Skill。 | 各產品維護者交付具版本的工具變更。CAE 檢查者核對模型和輸出。 | 每個核心流程有具名輸入、成功／失敗分支、版本資訊及可重跑案例。錯誤不被標為完成。 |
| **P4 評估其他官方工具／更新 SDK** | 01 Fluent；02 MAPDL；03 CFX；04 AEDT；05 Lumerical。依需求排序各試點。Geometry／DPF／Workbench SDK 分別建立升級故事。 | 各領域維護者記錄工具契約、實例相容性、輸出與保留理由。 | 僅對有工程工作負載、原生環境和比較證據的工具切換。每次可獨立退回原版本。 |
| **P5 相容退場** | 01 更新遷移表及 Skill 呼叫；02 提供相容入口與一個已發行過渡版本；03 確認客戶端與實際工作流用量；04 再決定是否移除。 | 維護者交付遷移表、版本差異、相容證據。檢查者核對例外與回退。 | 受支援呼叫皆有新入口或保留理由。使用量未知的工具先留相容方式。 |

## BDD 驗收情境

以下是可以分別轉成自動測試與實機工單的規格。既有 alias／profile／router tests 優先重用。官方和自研的比較使用相同版本、相同模型副本、相同輸出條件。工程容差由案例和參考解決定。[Gherkin 參考](https://cucumber.io/docs/gherkin/reference/) · [既有路由與 profile 測試](../../tests/unit/test_mcp_resilience_and_profiles.py)

| ID | Given | When | Then／可驗證證據 |
| --- | --- | --- | --- |
| B01 可見性 | A、B 連到同一個以 `core` 啟動、尚未選領域的 MCP 服務 | A 透過領域路由查找 Mechanical，再呼叫一個唯讀工具 | 兩階段均可取得必要工具規格及呼叫結果。保存 A、B 在啟動、發現後、呼叫後的 `tools/list`。兩邊仍只看各自允許的清單。若延遲匯入造成未選領域就增列工具，先修正再推廣 Core。 |
| B02 工作階段 | A、B 為不同 MCP 工作階段 | A 將工具範圍縮到 Geometry | A 的清單遵循 Geometry 與共用工具規則；B 維持自己的清單。實測三種客戶端刷新行為。 |
| B03 呼叫相容 | 有舊名稱、對應的新名稱與實際呼叫者 | 舊客戶端透過相容方式呼叫 | 得到相同後端與等價回傳。新客戶端的日常清單只呈現主要名稱。 |
| B04 官方模型讀取 | 兩套 MCP 分別可連同版本 Mechanical 的相同模型副本 | 查模型摘要、具名選取和必要分析物件 | 必要欄位與識別結果一致；留兩邊回傳與差異；來源模型雜湊一致。 |
| B05 工作階段歸屬 | MCP 附接使用者已開啟的 Mechanical GUI | 讀模型後中斷連線 | 原程序與專案仍開啟。記錄前後 PID、連線及專案狀態。 |
| B06 修改預覽 | 已識別指定物件、目前值和單位 | 預覽變更後，用正確 token 套用；另測舊值變動後的 token | 預覽階段原值一致。有效套用後讀回新值。舊值變動時回傳拒絕及原因。 |
| B07 幾何 | 有已知薄件、小於門檻件、非薄件及接觸參考 | 使用抽中面 Skill 選件，匯出並重開 STEP | 保留來源。核對選件、抽中面範圍、略過原因、厚度、接觸及重開後的幾何。 |
| B08 團隊工具 | 有可正確對應、重複以及找不到對象的 BOM／分組資料 | 在案例副本執行指派或接頭工具 | 成功與略過項可追溯。模糊對應項不被靜默寫入。 |
| B09 結果讀取 | 有版本、單位與時頻步已知的 `.rst` | DPF 讀檔並產出摘要 | 擷取值在該案例容差內；保留運算子、時頻步、單位與來源檔。 |
| B10 後端標記 | 真實商用後端不可用，而且該工具有內建基準 | 執行基準案例 | 回傳清楚標明基準後端和適用範圍。結果不會被用來簽收商用分析。 |
| B11 求解逾時 | 有已授權的長作業與可觀察的程序狀態 | MCP 呼叫超過等待時間 | 回傳等待逾時，並能分辨程序是否仍在執行。取消後核對日誌和程序狀態。 |
| B12 回退 | 完成一個官方工具替換試點 | 還原 MCP 配置和版本鎖定，再走既有流程 | 相容工具可連線，並產出原有格式及必要欄位。 |
| B13 腳本契約 | 有已知回傳值、錯誤與可控制等待時間的 Mechanical 腳本案例 | 在同版引擎分別執行並比較，另測官方 `check_script` | 保存成功回傳、錯誤類型、逾時與後端狀態。替換前核對字串／檔案輸入、輸出解析與取消語意。 |
| B14 正常求解 | 有已授權的案例副本、指定分析索引、參考解和容差 | 分別用兩套工具執行同一分析 | 確認求解完成、分析識別一致、指定結果及單位在案例容差內，輸出可重開。未通過時保留自研入口。 |
| B15 其他官方產品 | Fluent、MAPDL、CFX、AEDT 或 Lumerical 有自研現用的工作負載 | 使用同版產品、同一輸入副本與同一輸出條件逐項比較 | Fluent 核對案例狀態、殘差及 UDF／Journal；MAPDL 核對輸入、日誌與結果檔；CFX 核對 `.def` 與輸出；AEDT 核對 design／setup 與指定結果；Lumerical 核對模擬工作階段與指定輸出。以各案例指定物理量與容差簽收。 |
| B16 跨產品交接 | 有已知的 Workbench 系統、Geometry 樣件和 Mechanical 結果檔 | 依 Skill 交接幾何、開啟對應分析並由 DPF 讀取結果 | Workbench 系統、Mechanical 分析與 `.rst` 均可對應到同一案例。各步驟留版本、輸出識別和可復查的來源紀錄。 |

英文工具說明範例，按 STE 方法寫出單一動作、前置條件與可驗證結果。此處是撰寫範例，尚未修改工具說明。

```text
Read the model summary from the connected Mechanical session.
Return the analysis type and the object counts.
Do not change the model.
```

本次未找到可直接執行的本機 `/bdd`、`/bmad` 定義。計畫採用公開 BMad 的需求、架構、階段與工作故事格式，並用 Gherkin 的 Given／When／Then 編寫驗收。繁中計畫依 ISO 淺白語言方法整理，英文範例依本機 ASD-STE100 技能方法撰寫。

本次驗證範圍為工具清單、原始碼註冊、Skill、安裝目錄存在、鎖定版本及官方公開來源。實際 gRPC、ACT、授權、SDK 連線、求解和工程輸出屬後續階段。
