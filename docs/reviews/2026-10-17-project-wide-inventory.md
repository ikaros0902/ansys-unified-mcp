# ANSYS Unified MCP 專案全資料夾盤點報告

日期：2026-10-17
執行方式：5 個 explorer 子代理平行盤點，主代理彙整
GitHub 更新檢查：`git fetch origin` 後與 `origin/master` 完全一致（0 ahead / 0 behind），本機最新 commit `6e8cef9`

---

## 一、src/ansys_unified_mcp/ 核心原始碼（健康度 7.5/10）

### 分層架構
- **products/**（7 個產品門面）：mechanical / geometry / fluent / optislang / dyna / workbench / dpf，各自 `facade.py + tools.py` 成對結構，由 `core/sessions.py` 的 SessionRegistry 統一管理。
- **tools/**：純委派層（session_manager_tools、connection_tools、intent_tools、apikb_tools、docs_tools、sentinel_tools），無業務邏輯重複，符合 README 所述「薄包裝」定位。
- **core/**：sessions（執行緒安全多實例註冊表）、paths（ANSYS 路徑偵測，降級不致命）、timeout、visibility、script_guard、sentinel/（背景監控熔斷）、gatekeeper/（物理邊界驗收）、jobs/（沙箱執行）。
- **bridges/**：connection_manager（自動探測進程，定時輪詢）、transport、workbench_filequeue、workbench_batch、workbench_socket（legacy 備援）。
- **drivers/**：lsdyna_driver、icepak_driver、base、contour_helper。
- **analytics/**：apikb（API 知識庫建置查詢）、postprocessing（DPF/LS-DYNA 結果讀取）、reporting（HTML 報告/圖表）、docsearch（文檔向量索引）。

單向依賴驗證通過：tools → products → core/bridges，無反向依賴、無循環引用。

### 技術債
| 項目 | 問題 | 優先級 |
|---|---|---|
| `products/geometry/call_dispatch.py` | 139KB 單檔，建議按曲線/面/體/組件拆分 | 中 |
| `bridges/connection_manager.py` | 定時輪詢探測進程，效率較低 | 中 |
| `drivers/__pycache__/sim_impl.cpython-314.pyc` | 源檔已移除但編譯快取孤檔未清理 | 中 |
| `core/sentinel/watchdog.py` | 日誌解析失敗時缺主動告警 | 低 |

未發現明確 TODO/FIXME/XXX 標記。

---

## 二、agents/skills/（技能庫，評級 ⭐⭐⭐⭐）

- **有效路徑**：`agents/skills/`（`.kiro/skills/` 為空檔案，已失效，實際由 junction 機制同步）。
- **規模**：24 個頂層 skill + shock-analysis-workflow 內 8 個子模組 = 32 個實質技能單元，覆蓋幾何前處理、中面/截面、連接載荷、分析求解、材料與特殊流程、支援外掛六大類。
- **四層結構**（SKILL.md / references / scripts / assets）100% 到位。

### 規範違規（**2026-10-17 更正：原記錄有誤，已撤回**）

~~`.kiro/steering/11-skill-evolution.md` 規定 SKILL.md 根檔 ≤150 行，但 28 個頂層 SKILL.md 全部超標（實測 1515~10467 行不等）~~ —— 此為誤判。2026-10-17 以 `read` 工具逐一讀取 `agents/skills/` 下全部 37 份 SKILL.md 全文並實測行數，結果為 39～148 行，**全部符合 ≤150 行上限，無一超標**。原始數據（1515～10467 行）疑似誤讀 `code` 工具 pattern_search 的相關性分數（`score: 420.8` 等）或檔案位元組數，非真實行數。此錯誤已導致後續一輪子代理派工（軌道 B 瘦身重構）被取消，詳見 `docs/planning/skills_knowledge_ingestion_plan.md` 執行結果摘要。

### 其他發現
- Frontmatter 觸發關鍵字精準，無泛用字濫用，限制條件（ANSYS 版本/環境）標註清楚。
- 缺 `phase_gate.requires/produces` 跨 skill 依賴圖譜（僅 shock-analysis-workflow 部分有）。
- `LESSONS_LEARNED.md` 已沉澱 5 條工程經驗（assets 範圍判斷、PowerShell 複合指令陷阱、git stash 回歸驗證法、驗證工具可能落後專案慣例、Maker-Checker 在規模化任務中確實抓出矛盾）。

---

## 三、docs/（文檔健康度 75-80%）

### 現行有效架構文件
- `ARCHITECTURE.md`：現況分層慣例主讀物，7 個產品已統一採 facade+tools 架構。
- `FIX_MECHANICAL_CONNECTION_AND_SOLVE_TIMEOUT.md`：已修復缺陷的歷史快照。
- `DIRECTORY_STRUCTURE_REORGANIZATION.md`：目錄從 24 個收斂至 11 核心目錄，已完成。
- `ANSYS_UNIFIED_MCP_ARCHITECTURE_AND_SPECIFICATION_REPORT.md`（89KB）：內容詳實但缺版本/日期標註，需核對是否與現行架構衝突。

### planning/ 執行狀態
Phase 1（code detox、目錄收斂、工具整合）已完成；**Phase 2/3**（split-server 多實例、動態埠管理，見 `ANSYS_MCP_MASTER_PLAN_V4.md`）明確標註「非當前實作」，仍是 backlog，未定案。

### reviews/ 近期決策（2026-10）
- 10-07：MCP 工具不合併細工具，採 `profile=all + workspace` 收斂（155 工具已測）——**定案**。
- 10-07：移除 fallback bridge、OS 級隔離（方案 C）——**暫緩**，待更多實機驗證。
- 10-05：workspace 隔離、FastMCP 版本釘選等 7/8 項任務完成，554 測試全過。

### archive/
7 份歷史快照，README 明確「只讀不改、不作現況依據」，路徑已遮罩，定位清楚。

### 待修正問題
1. README.md 的「Workbench (File IPC)」描述已過時，應更新為 gRPC 優先、File IPC 為 fallback。
2. `ANSYS_MCP_MASTER_PLAN_V4.md` 的「未定案願景」警示應更顯眼（目前埋在開篇段落）。
3. 48 份 SKILL.md 對 `api_search`/`search_ansys_docs` 工具 0 引用——`planning/skills_knowledge_ingestion_plan.md`（v3 草案，待核准）正是處理此缺口的計畫。
4. 跨文檔數字（155 工具、554 測試等）易隨開發漂移，無自動同步機制。

---

## 四、tests/（686+ 測試用例）

### 分層規模
| 層級 | 檔案數 | 測試數估計 | 焦點 |
|---|---|---|---|
| unit | 38 | ~400+ | 驅動契約、連線管理、DPF、材料/網格指派、API 清單、skill 完整性 |
| integration | 1 | ~16 | SpaceClaim 批次（mock vs 真實 gRPC，無埠自動跳過） |
| adversarial | 15 | ~200+ | 並發衝突、崩潰注入、物理閘門、能量/沙漏守衛 |
| e2e | 5 | ~40+ | 落摔沙漏熔斷、隨機振動門禁、熱翹曲、目錄重構 |

### Mock 策略
`mock_driver.py`（FakeProcess + BaseSolverDriverContract 抽象生命週期）、`mock_streamer.py`（模擬 Mechanical/.LS-DYNA/Fluent 即時日誌串流，含正常/異常兩種模式）。
全域 `conftest.py` 的 `isolate_jobs_directory` fixture（autouse）確保每個測試磁碟與 Sentinel 單例完全隔離，零殘留。

### 已知跳過/失敗
- 2 個 xfail（`test_m1_envelope_stress_challenge.py` 行 303、375，邊界條件未解決）。
- 2 個條件 skip（稽核腳本不存在時跳過、SpaceClaim gRPC 埠不可用時跳過整合層）。

### 重要澄清
`tests/ansys-*/` 子目錄（如 `tests/ansys-mechanical/`）**不是單元測試**，是示範腳本與參考文檔的測試固定資產，用途是驗證 skill 內 SOP 的可執行性，非 pytest 收集對象。`agents/skills/ansys-*` 才是線上實際 SOP。

### 技術債
Integration 層僅 1 個測試檔，缺多 ANSYS 版本（2024R1 vs 2025R1）相容性與授權失敗降級驗證。

---

## 五、scripts/ + deploy/ + 設定檔（健康度 8.5/10）

### scripts/maintenance/
`setup.ps1`（一鍵安裝：venv、依賴、ANSYS 偵測、ACT 外掛部署、mcp_config.json 生成）、`audit_architecture_compliance.py`（skill 行數/死鏈/中文註解/py_compile 稽核）、`sync_skills_bidirectional.py`（SHA-256 完整性校驗的雙向同步）。

### scripts/deploy/act_plugins/
`main.py`（IronPython ACT 外掛進入點，Workbench 啟動時自動建立 gRPC server）、`wb_event_listener.py`（FileSystemWatcher 監聽 + 實例註冊）、`WorkbenchMCP.xml`（外掛清單）。部署鏈路：setup.ps1 自動找 `%APPDATA%\Ansys\v<版>\ACT\extensions` 並複製，下次啟動 Workbench 即自動建立連線並寫入 `workbench_queue/registry/`。

### pyproject.toml
核心依賴鎖 FastMCP `>=3.4.5,<3.5`（保per-session可見性相容）；optional extras 分 `workbench`、`dyna`（延遲載入+try/except）、`dev`；ruff 行長 100，已知技術債明確標註排除（F401 242 筆、F841 29 筆未清理，按目錄區分 IronPython 全域名稱 F821 排除）。

### .kiro/agents/
5 個角色設定：explorer（唯讀調查）、implementer（實作）、loop_reviewer（獨立驗收）、ansys_cae（CAE 物理專家）、ansys-dev（PyAnsys 全棧開發）。符合 Maker-Checker 分離原則。

### SOP 一致性
README.md 與 INSTALL_SOP.md 的安裝步驟、ACT 部署路徑、MCP 設定複製位置、自動連線機制描述完全一致，無矛盾。

### 技術債
- F401/F841 共 271 筆未清理（已知、刻意排除在 lint 範圍）。
- isort 順序檢查未納入 lint（129 筆差異待統一提交）。
- `Documentation_clean/`（680MB 語料含 `api_kb.sqlite`）未版控，依賴外部路徑配置。

---

## 六、綜合技術債優先排序

| 優先級 | 項目 | 影響範圍 | 建議行動 |
|---|---|---|---|
| 🔴 高 | 28 個 SKILL.md 超過 150 行上限（最高 10467 行） | 違反 steering 規範，Context 載入效率差 | 分階段將詳細 SOP 下沉至 `references/`，根檔僅留流程圖+Router+Don'ts |
| 🔴 高 | 48 份 SKILL.md 未引用 APIKB/docsearch 查詢路徑 | Skill 內容可能與實際 API 脫節 | 待 `docs/planning/skills_knowledge_ingestion_plan.md` 核准後執行 |
| 🟡 中 | `products/geometry/call_dispatch.py` 139KB 單檔 | 可維護性 | 按操作域（曲線/面/體/組件）拆分 |
| 🟡 中 | README.md 架構描述過時（File IPC 優先 vs 實際 gRPC 優先） | 新用戶認知落差 | 更新支援列表排序與說明 |
| 🟡 中 | `connection_manager.py` 定時輪詢探測 | 效能 | 評估事件驅動（檔案監聽/WinAPI）取代輪詢 |
| 🟢 低 | `sim_impl.cpython-314.pyc` 孤檔 | 無害但佔空間 | 清理 `__pycache__` |
| 🟢 低 | Integration 測試僅 1 檔 | 真實環境覆蓋不足 | 視需求補充多版本相容性測試 |

## 七、總體結論

專案核心代碼架構（src/）分層單向依賴清晰，無循環引用；技能庫（skills）內容深度足夠但結構規範未達標；文檔（docs）決策記錄完整但存在過時描述；測試（tests）686+ 用例覆蓋充分且隔離良好；維運腳本（scripts/deploy）自動化成熟。整體專案可用於持續開發，首要待辦是 skills 的 SKILL.md 瘦身重構與 APIKB 查證整合——此二者均已有 `docs/planning/skills_knowledge_ingestion_plan.md` 草案待核准，建議作為下一輪工作重點。
