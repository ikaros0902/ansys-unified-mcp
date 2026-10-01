# R3 腳本目錄結構與全專案 pytest 基準深度調研報告

## 執行摘要

本報告針對 `ansys-unified-mcp` 專案之「第一階段：止血與排毒 (Detox)」進行全方位只讀探查，聚焦於 **R3 腳本目錄清理** 以及 **全專案 pytest 基準測試環境與現存報錯**。

- **`scripts/` 目錄現況**：根層級無孤立檔案。下轄 3 個子目錄：`_archive_mesh_fix_202609/`（12 個伺服器機箱 CAE 網格除錯歷史腳本）、`deploy/`（ACT 核心外掛資產，不可刪）、`maintenance/`（7 個專案維護與合規審計腳本，不可刪）。
- **網格腳本歸檔定位**：全數 12 個網格除錯腳本皆包含高度特定之模型硬編碼名稱（如 114 個 body、`1F-FRONT-END-GDZ`、`CX7` 等），**強烈建議歸檔至 `examples/mesh_debug/` 作為除錯案例研究**，絕不可直接置入 `skills/ansys-mesh/scripts/` 污染通用工具鏈。
- **測試環境與 pytest 基準**：專案具備完整虛擬環境 `.venv`（Python 3.14.2 + pytest 9.1.1）。在修復虛擬環境依賴缺失（`pydantic==2.13.4` 與 `ansys-dpf-core==0.16.1`）後，全專案 **461 項測試無任何 Collection 錯誤，452 項通過、僅 1 項失敗、2 項跳過、5 項預期失敗、1 項意外通過**，測試健康度高達 99.8%！
- **唯一失敗根因已鎖定**：Commit `0b28e80` 將 `geometry_tools.py` (12 tools) 與 `optislang_tools.py` (5 tools) 從 `tools/` 移至 `products/*/tools.py`，導致 `test_chapter2_adversarial_verification.py` 掃描 `tools/*.py` 時出現 121 vs 138 之數量斷言差額。修復該測試之掃描路徑即可達成全專案 100% 通過。

---

## 一、`scripts/` 目錄結構與檔案功能深度分析

專案根目錄 `scripts/` 下僅有 3 個子目錄，無任何根目錄層級之散落檔案：

```
scripts/
├── _archive_mesh_fix_202609/      # 12 個歷史網格修復腳本 (應清理/遷移)
├── deploy/                        # ACT 外掛部署源碼 (專案核心資產，保留)
│   └── act_plugins/
│       ├── WorkbenchMCP.xml
│       ├── main.py
│       ├── start_api_server.py
│       └── wb_event_listener.py
└── maintenance/                   # 專案級維護與審計腳本 (保留)
    ├── audit_architecture_compliance.py
    ├── preflight_env_check.py
    ├── setup.ps1
    ├── setup_skill_junctions.py
    ├── sync_skills.ps1
    ├── sync_skills_bidirectional.py
    └── verify_connection_manager_isolation.py
```

### 1.1 `_archive_mesh_fix_202609/` 下 12 個檔案功能逐一剖析

經過程式碼逆向與行為審查，該目錄下所有檔案均為 2026 年 9 月針對同一款伺服器機箱（包含 114 個實體零件、連接至 PyMechanical port 10000）的網格劃分排障與除錯腳本：

| 檔案名稱 | 程式碼規模 | 功能與實作特徵 | 幾何/模型相依性 |
|---|---|---|---|
| `check_stuck_geometry.py` | 70 行 | 透過 PyMechanical 連線 port 10000，遍歷所有 Body 檢查單元數為 0 者，並擷取 `ExtAPI.DataModel.Messages` 最新 10 則錯誤警告訊息。 | 連線 10000 埠，檢查幾何未劃分狀態。 |
| `clean_and_collapse_tree.py` | 69 行 | 強制設定所有 114 個 body `Visible = True`；將散落在外的 `Tet_Component1\PDB_STANDOFF_GDZ1` 節點重新分組至 `Component1` 資料夾，並呼叫 TreeHandler 摺疊模型樹至 Level 2。 | **高度硬編碼**（114 bodies, Component1, PDB_STANDOFF_GDZ1）。 |
| `finish_remaining_parts_robust.py` | 105 行 | 依父 Part 分組，啟用視覺顯隱隔離（只顯示當前 Part），先嘗試一般劃分，失敗則刪除既有方法並 fallback 回退為 `AllTriAllTet` 四面體，最終統計節點與單元總數。 | 具備 Part 隔離與 Tet 回退機制。 |
| `inspect_mesh_setup.py` | 85 行 | 掃描 Mesh 樹下的控制項，檢查是否存在未定義控制項（問號 `?` 或 `UnderDefined`/`Invalid` 狀態），並分析是否存在重複作用於相同 Body 的衝突 Scoping。 | 通用檢驗邏輯，但於本除錯會話中使用。 |
| `rebuild_step1.py` | 143 行 | 清除所有 Mesh 控制項，針對 114 個 body 執行 1x1 AutoMesh 重建：Sheet 薄板配置 Prime 3mm；含 PCBA/PCB 關鍵字配置 MultiZone 1.5mm；其餘配置 AllTriAllTet 2.0mm。 | **高度硬編碼**（114 bodies, PCBA 部件關鍵字過濾）。 |
| `rebuild_step1_and_step2.py` | 124 行 | 採用 Transaction 包裹，清除舊控制項後按 Part 自動指派 Method (QuadTri / MultiZone) 與 Sizing，並自動為每個 Part 建立 `TreeGroupingFolder`。 | **硬編碼**（針對 114 個組件按 Part 樹狀分組）。 |
| `reset_methods_to_multizone.py` | 146 行 | 針對除 `1F-FRONT-END-GDZ` 外的所有分組資料夾，刪除原有 Method，重新對實體賦予 MultiZone 方法，並重新分組與摺疊樹狀目錄。 | **高度硬編碼**（排除特定零件 `1F-FRONT-END-GDZ`）。 |
| `run_step3_partitioned_mesh.py` | 118 行 | 依 Part 逐一調用 `GenerateMesh()`，劃分失敗之 Body 自動回退至 `AllTriAllTet`，若仍失敗則微調單元尺寸至 1.5mm 進行二次重試。 | 自動降級回退 (Fallback & Retry) 邏輯。 |
| `step3_partition_mesh_and_fallback.py` | 183 行 | 鎖定 11 個關鍵 Part 清單，進行視覺隔離劃分；若 MultiZone 劃分超時 (> 180s) 或拋錯，自動 fallback 為 `AllTriAllTet`，並使用 `MeshData.MeshRegionById` 進行節點客觀驗證。 | **高度硬編碼**（清單含 `SM-BASEPAN-GDZ`, `Rear_wall`, `CX7`, `OCP`, `DCSCM` 等 11 個 Part）。 |
| `stepped_mesher_with_visibility.py` | 161 行 | 帶視覺顯隱切換與終端日誌輸出的步進式劃分腳本，遇失敗自動回退為 AllTriAllTet，劃分完成後 100% 還原所有 114 個實體的可見性。 | **高度硬編碼**（114 bodies 狀態還原）。 |
| `test_mech_direct.py` | 14 行 | 透過 PyMechanical 連線 port 10000 的極簡連線可用性測試腳本，印出 `Model.Name`。 | 連線探針。 |
| `test_tet_meshing.py` | 48 行 | 測試將 `1F-FRONT-END-GDZ` 中的首個固體 Body 的 Method 動態修改為 `AllTriAllTet` 並單獨劃分的單元測試腳本。 | **高度硬編碼**（特定零件 `1F-FRONT-END-GDZ`）。 |

### 1.2 歸檔評估：歸入 `skills/ansys-mesh/scripts/` 還是 `examples/mesh_debug/`？

**結論：強烈建議歸入 `examples/mesh_debug/`。**

**評估依據**：
1. **技能純度與通用性原則 (Single Responsibility & Generality)**：
   - `skills/ansys-mesh/scripts/` 屬於 Agent 技能標準工具庫，目前已具備通用性極高的工具：
     - `auto_mesh_generator.py`（通用的拓撲特徵分流與 Sizing 配置器）
     - `cfl_mesh_tuner_fast.py`（通用的顯式動力學時間步長優化器）
     - `check_mesh_quality.py`（通用的網格品質指標計算工具）
   - `_archive_mesh_fix_202609/` 中的 12 個腳本充斥著特定機箱零件名稱（`1F-FRONT-END-GDZ`、`SM-BASEPAN-GDZ`、`Component1`、`114 bodies` 等）。若將這些含有特定客戶模型代碼的腳本直接塞進 `skills/ansys-mesh/scripts/`，將嚴重違反 `agentskills.io` 規範，使 Agent 在調用通用技能時產生模型名稱幻覺。
2. **範例與除錯案例價值 (Case Study & Reference Implementation)**：
   - 專案根目錄已存在 `examples/`，包含 `examples/geometry_cleanup`、`examples/pcb_warpage`、`examples/shock_analysis`。
   - 將該批腳本遷移至 `examples/mesh_debug/`，並補上一份 `README.md`（說明此為「114 實體複雜伺服器機箱網格排障案例：視覺隔離、分區處理與四面體超時降級回退手法」），既完整保留了這套實戰除錯手法的歷史資產，又能作為後續開發通用分區劃分演算法的參考依據。

### 1.3 `scripts/` 其他目錄檔案定位與清理建議

1. **`scripts/deploy/act_plugins/`**：
   - 包含 `WorkbenchMCP.xml`、`main.py`、`start_api_server.py`、`wb_event_listener.py`。
   - **定位**：此目錄為 Ansys Workbench / Mechanical ACT 外掛的發布來源。在 `scripts/maintenance/setup.ps1` 中，會自動將此目錄內容複製並部署至 `%APPDATA%\Ansys\v*\ACT\extensions\`；同時在 `pyproject.toml` 的 ruff 設定中亦正式註冊了該目錄的語法白名單。
   - **處置**：**專案級核心部署資產，必須完整保留**。
2. **`scripts/maintenance/`**：
   - 包含 7 個腳本：
     - `setup.ps1`：專案核心一鍵部署與環境設定 PowerShell 腳本。
     - `audit_architecture_compliance.py`：架構合規與 SKILL 語法全面審查工具。
     - `preflight_env_check.py`：預檢 ANSYS 安裝路徑、Python 環境與連接埠。
     - `setup_skill_junctions.py`：建立技能符號連結/聯結點。
     - `sync_skills.ps1` / `sync_skills_bidirectional.py`：專案與全域技能庫雙向同步工具。
     - `verify_connection_manager_isolation.py`：連線管理器單例設計與隔離性驗證。
   - **處置**：**全數為專案級維護/建置腳本，應完整保留**。

---

## 二、Python 虛擬環境與全專案 pytest 基準探查

### 2.1 虛擬環境與相依套件現況

- **虛擬環境位置**：`F:\Ming_python\ansys-unified-mcp\.venv\`
- **解譯器規格**：Python 3.14.2 64-bit (`.venv\Scripts\python.exe`)
- **pytest 版本**：pytest 9.1.1
- **重要發現 1：`uv run` 鎖定阻礙 (os error 5)**
  - 執行 `uv run pytest` 時，uv 會嘗試檢查與同步虛擬環境，但因系統常駐背景進程（PID 32256 / 38668 正在執行 `mcp_server.py`）載入了 `cygrpc.cp314-win_amd64.pyd`，觸發 Windows 檔案鎖定：
    `error: failed to remove file ...\cygrpc.cp314-win_amd64.pyd: 存取被拒。 (os error 5)`
  - **解決對策**：使用 `.venv\Scripts\pytest.exe` 直接執行測試，完全避開 uv 自動同步對已鎖定二進位檔案的衝突。
- **重要發現 2：依賴套件損壞修復與驗證**
  - 初次執行 collection 時，遭遇 22 個模組收集失敗，報錯為 `No module named 'pydantic'`。進一步檢查發現之前 uv 同步中斷導致 `pydantic` 未安裝且 `pydantic_core` 缺少 `__init__.py`。
  - 同時，`pyproject.toml` 中的核心相依套件 `ansys-dpf-core` 未安裝，導致 `tests/unit/test_dpf_reader.py` 4 項測試失敗。
  - **環境補全（完全無修改任何專案原始碼）**：
    - 安裝相容之 `pydantic==2.13.4`（匹配現有 `pydantic-core==2.46.4`）。
    - 安裝 `ansys-dpf-core==0.16.1`。
  - 補全後，測試收集數瞬間由 175 增加至 **461 項，0 collection errors**！

### 2.2 全專案 pytest 執行基準數據 (Baseline Statistics)

執行指令：`.venv\Scripts\pytest.exe -q --tb=short`

| 項目 | 數量 | 佔比 | 備註 |
|---|---|---|---|
| **總收集測試數 (Total Collected)** | **461** | 100% | 涵蓋 unit, adversarial, e2e 全套測試 |
| **通過測試 (Passed)** | **452** | 98.05% | 基礎功能與架構守門全數通過 |
| **失敗測試 (Failed)** | **1** | 0.22% | 僅 1 項工具計數斷言（見下文詳細分析） |
| **跳過測試 (Skipped)** | **2** | 0.43% | 因腳本移至 maintenance/ 導致路徑檢查跳過 |
| **預期失敗 (XFailed)** | **5** | 1.08% | 歷史漏洞驗證挑戰測試（刻意標記驗證漏洞已被修復） |
| **意外通過 (XPassed)** | **1** | 0.22% | 漏洞已修復而不再失敗的防禦測試 |
| **執行總耗時** | **24.96s** | - | 執行效能優異 |

### 2.3 失敗與跳過項目之根因分析

#### 1. 唯一失敗測試：`test_tool_count_136_ast_verification`
- **測試位置**：`tests/adversarial/test_chapter2_adversarial_verification.py:142`
- **錯誤訊息**：`AssertionError: AST 解析工具總數應為 138，實測: 121`
- **追根究底**：
  - 該測試使用 AST 遍歷 `src/ansys_unified_mcp/tools/*.py` 中的工具函數。
  - 統計結果為：`connection_tools: 0, docs_tools: 4, dpf_tools: 2, fluent_tools: 19, intent_tools: 5, mechanical_tools: 39, mechanical_workflow_tools: 3, sentinel_tools: 4, workbench_tools: 45`，合計 **121 個**。
  - 差額：$138 - 121 = 17$ 個。
  - 查閱 Git 歷史，Commit `0b28e80` 執行清理時，從 `tools/` 移除了：
    - `geometry_tools.py`（恰好 12 個工具）
    - `optislang_tools.py`（恰好 5 個工具）
    - 兩者合計正好是 $12 + 5 = 17$ 個工具！
  - 這些工具在垂直切片架構重構中，已遷移至：
    - `src/ansys_unified_mcp/products/geometry/tools.py` (12 tools)
    - `src/ansys_unified_mcp/products/optislang/tools.py` (5 tools)
    - 且已在 `src/ansys_unified_mcp/__main__.py` 註冊。
  - 但該對抗測試只檢查了 `tools/*.py`，未納入 `products/*/tools.py`，導致此項斷言報錯。

#### 2. 兩項跳過測試 (Skipped)
- **測試位置**：
  - `tests/unit/test_skills_audit.py:37` (`test_skills_architecture_audit_passes`)
  - `tests/unit/test_skills_audit.py:73` (`test_sync_does_not_delete_global_only_files_by_default`)
- **跳過原因**：
  - 測試開頭定義：
    `AUDIT_SCRIPT = PROJECT_ROOT / "scripts" / "audit_architecture_compliance.py"`
    `SYNC_SCRIPT = PROJECT_ROOT / "scripts" / "sync_skills_bidirectional.py"`
  - 因兩腳本在 Commit `0b28e80` 中已被統一歸入 `scripts/maintenance/` 目錄，使得 `@pytest.mark.skipif(not AUDIT_SCRIPT.is_file())` 判定檔案不存在而跳過。
  - 經手動執行 `python scripts/maintenance/audit_architecture_compliance.py`，該審查腳本輸出 **100% PASS**（行數、死鏈、繁中、py_compile 全數合規）。

---

## 三、後續達成 100% pytest 通過與 R3 清理之實施建議

為使後續 implementer 能夠一次性達成 100% 綠燈，提供具體步驟如下：

### 步驟 1：執行 R3 腳本目錄遷移
1. 建立 `examples/mesh_debug/` 目錄。
2. 將 `scripts/_archive_mesh_fix_202609/` 下的 12 個檔案遷移至 `examples/mesh_debug/`。
3. 於 `examples/mesh_debug/README.md` 撰寫案例說明，記錄伺服器機箱 114 實體的調優背景。
4. 移除空的 `scripts/_archive_mesh_fix_202609/` 目錄。
5. （結果：根目錄 `scripts/` 僅保留 `deploy/` 與 `maintenance/`）。

### 步驟 2：執行 R1 代碼去重 (Mechanical.py)
1. 刪除 `src/ansys_unified_mcp/products/mechanical.py` 實體檔案（其內容與 `products/mechanical/facade.py` 完全一致）。
2. `src/ansys_unified_mcp/products/mechanical/__init__.py` 已將 `MechanicalController`, `controller`, `_esc` 導出，所有外部引用 `from ansys_unified_mcp.products.mechanical import ...` 均可無痛直接運作。

### 步驟 3：修正測試路徑與工具掃描，達成 100% 通過
1. **修正 `tests/unit/test_skills_audit.py`**：
   - 將 `AUDIT_SCRIPT` 與 `SYNC_SCRIPT` 的路徑改為指向 `scripts/maintenance/`。
   - 2 個 Skipped 測試將全部恢復並順利 PASS。
2. **修正 `tests/adversarial/test_chapter2_adversarial_verification.py`**：
   - 在 `test_tool_count_136_ast_verification` 中，將掃描範圍擴展至同時涵蓋 `products/*/tools.py`（或在 `tools/` 提供符號相容導出），使 AST 總數正確計算為 138。
   - 此舉將徹底消除全專案唯一的 1 項失敗。

完成上述 3 個步驟後，全專案 pytest 將達到 **455 Passed, 0 Failed, 0 Skipped, 5 Xfailed, 1 Xpassed (100% 綠燈)**！
