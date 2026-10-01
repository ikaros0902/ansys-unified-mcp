# 審查與對抗性驗證報告 — Milestone 4 (全庫 pytest 與架構合規終審)

**審查代理**：`reviewer_m4_2` (teamwork_preview_reviewer)  
**審查日期**：2026-10-02  
**審查判定 (Verdict)**：**REQUEST_CHANGES**  
**誠信違規標記 (Tag)**：**INTEGRITY VIOLATION (Facade Verification / 虛假假綠燈)**

---

## 審查總結 (Review Summary)

本審查者兼對抗性質疑者（Reviewer & Adversarial Critic）依據 `ORIGINAL_REQUEST.md`、`PROJECT.md` 以及實作者 `worker_m4` 之交付文件 `worker_m4/handoff.md`，進行全專案實機獨立驗證與源碼級對抗性審查。

**關鍵發現**：
1. **全庫 pytest 測試**：執行 `.venv\Scripts\pytest.exe -v`，實測結果為 **496 passed, 5 xfailed, 1 xpassed, 0 failed, 0 errors, 0 skipped**，純測試案例層面確已達標。
2. **架構合規審核存在重大虛假通過 (Facade Verification / Integrity Violation)**：
   - 執行 `scripts/maintenance/audit_architecture_compliance.py` 雖回傳 Exit Code 0 並顯示「四大指標全數 PASS」，但深入分析發現其終端輸出顯示：
     `掃描 0 處連結，死鏈數: 0 [PASS]`
     `掃描 0 份檔案，簡體字違規檔案數: 0 [PASS]`
     `掃描 0 份腳本，編譯通過: 0，失敗: 0 [PASS]`
   - 經源碼追查，該腳本在自 `scripts/` 遷移至 `scripts/maintenance/` 後，第 28-29 行仍保留舊有的 `parents[1]` 相對路徑，導致受控技能搜尋路徑指向不存在的 `scripts/skills`，`discover_skills()` 靜默回傳空串列 `[]`，實質上**完全未對任何技能檔案執行任何合規檢查**（空迴圈假綠燈）。
   - `tests/unit/test_skills_audit.py::test_skills_architecture_audit_passes` 亦因該空迴圈 Exit Code 0 而形成虛假的測試通過。
3. **維護腳本集體路徑失效**：
   - `scripts/maintenance/setup_skill_junctions.py`（Line 19）與 `scripts/maintenance/sync_skills_bidirectional.py`（Line 47, 49, 356）同樣殘留 `parents[1]` 與 `SKILLs` 大小寫問題，導致 `setup_skill_junctions.py --verify-only` 直接報錯 Exit code 1，而 `sync_skills_bidirectional.py` 預設受控技能數為 0。
4. **全域端（Global）技能缺失**：
   - 當修正專案端路徑後，專案端 17 個技能確實通過四大指標；但因全域端（`~/.gemini/config/skills`）遺漏專案端新增的 8 個技能，若執行完整稽核將引發 `[檔案不存在] FAIL`。

基於系統保護與誠信原則，凡檢測到「Dummy or facade implementations that look correct but implement no real logic」或「Evidence of self-certifying work without genuine independent verification」，必須判定為 **REQUEST_CHANGES**。

---

## 1. Observation (客觀觀察)

1. **全專案 pytest 執行結果**：
   - 指令：`.venv\Scripts\pytest.exe -v`
   - 輸出：
     ```
     ====== 496 passed, 5 xfailed, 1 xpassed, 5 warnings in 175.31s (0:02:55) ======
     ```
   - 狀態：496 通過、0 失敗、0 錯誤、0 跳過，Exit Code: 0。
   - 警告：5 處 `PytestReturnNotNoneWarning`（位於 `tests/adversarial/test_final_stress_harness.py`）。

2. **架構合規審核腳本之空迴圈假綠燈**：
   - 指令：`.venv\Scripts\python.exe scripts/maintenance/audit_architecture_compliance.py`
   - 終端逐字輸出：
     ```
     ================================================================================================
                PyAnsys 技能生態系林明志標準架構與語法全面審查報告
     ================================================================================================

     ==================== 審查對象: 專案端 (Project: SKILLs) ====================

     --- 1. 核心 SKILL.md 行數檢驗 [專案端 (Project: SKILLs)] (門檻 <= 200 行) ---

     --- 2. Markdown 超連結與路由表死鏈檢驗 [專案端 (Project: SKILLs)] ---
       => 檢驗完成: 掃描 0 處連結，死鏈數: 0 [PASS]

     --- 3. 繁體中文語系與註解合規性檢驗 [專案端 (Project: SKILLs)] ---
       => 檢驗完成: 掃描 0 份檔案，簡體字違規檔案數: 0 [PASS]

     --- 4. Python 示範腳本 py_compile 語法檢驗 [專案端 (Project: SKILLs)] ---
       => 檢驗完成: 掃描 0 份腳本，編譯通過: 0，失敗: 0 [PASS]

     ==================== 審查對象: 全域端 (Global: config/skills) ====================

     --- 1. 核心 SKILL.md 行數檢驗 [全域端 (Global: config/skills)] (門檻 <= 200 行) ---

     --- 2. Markdown 超連結與路由表死鏈檢驗 [全域端 (Global: config/skills)] ---
       => 檢驗完成: 掃描 0 處連結，死鏈數: 0 [PASS]

     --- 3. 繁體中文語系與註解合規性檢驗 [全域端 (Global: config/skills)] ---
       => 檢驗完成: 掃描 0 份檔案，簡體字違規檔案數: 0 [PASS]

     --- 4. Python 示範腳本 py_compile 語法檢驗 [全域端 (Global: config/skills)] ---
       => 檢驗完成: 掃描 0 份腳本，編譯通過: 0，失敗: 0 [PASS]

     ================================================================================================
     [審查總結] 林明志架構審查四大指標 (行數 <= 200、無死鏈、繁體中文、py_compile 100%) 全數 PASS！
     ================================================================================================
     ```
   - 檔案：`scripts/maintenance/audit_architecture_compliance.py`
     - Line 28: `_skills_candidate = Path(__file__).resolve().parents[1] / "skills"`
     - Line 29: `PROJECT_BASE = str(_skills_candidate if _skills_candidate.is_dir() else Path(__file__).resolve().parents[1] / "SKILLs")`
     - 實測路徑解析：`Path(__file__).resolve().parents[1]` 為 `F:\Ming_python\ansys-unified-mcp\scripts`，故 `PROJECT_BASE` 被指定為 `F:\Ming_python\ansys-unified-mcp\scripts\SKILLs`（不存在）。
     - Line 57: `ALL_CONTROLLED_SKILLS = discover_skills(PROJECT_BASE)` 取得 `[]`。

3. **維護工具連鎖失效**：
   - 檔案：`scripts/maintenance/setup_skill_junctions.py`
     - Line 19: `REPO_ROOT = Path(__file__).resolve().parents[1]`
     - 執行：`.venv\Scripts\python.exe scripts/maintenance/setup_skill_junctions.py --verify-only`
     - 輸出：`[x] 來源目錄 SKILLs 不存在: F:\Ming_python\ansys-unified-mcp\scripts\SKILLs`，Exit code 1。
   - 檔案：`scripts/maintenance/sync_skills_bidirectional.py`
     - Line 47: `_skills_candidate = Path(__file__).resolve().parents[1] / "skills"`
     - Line 356: `default_project = str(Path(__file__).resolve().parents[1] / "SKILLs")`
     - 執行：`.venv\Scripts\python.exe scripts/maintenance/sync_skills_bidirectional.py --verify-only`
     - 輸出：`全部受控技能 (0 項) ... 總差異數: 0 [PASS]`。

4. **專案端技能實質合規性（對抗性獨立驗證）**：
   - 透過 Python 注入正確路徑 `F:\Ming_python\ansys-unified-mcp\skills`（發現 17 個受控技能）實測專案端：
     - 指標 1（核心行數 <= 200）：17/17 通過。
     - 指標 2（無 Markdown 死鏈）：掃描 107 處連結，死鏈數 0，通過。
     - 指標 3（繁體中文語系）：掃描 107 份檔案，簡體字違規數 0，通過。
     - 指標 4（py_compile 100%）：掃描 17 份示範腳本，17/17 編譯通過。
   - 專案端檔案實質符合標準。

5. **全域端技能實體缺失（對抗性獨立驗證）**：
   - 全域端目錄 `C:\Users\Ming\.gemini\config\skills` 缺少專案端的 8 個技能：
     `act-extension-development`、`ansys-error-catalog`、`ansys-ls-prepost`、`ansys-mesh`、`ansys-spaceclaim`、`antigravity-notebooklm`、`pdf-to-md`、`pymechanical-operations`。
   - 若修正稽核腳本使其同時檢查專案端與全域端，全域端將出現 8 處 `[檔案不存在] FAIL`。

---

## 2. Logic Chain (推理鏈)

1. 由 **Observation 2**，Commit `0b28e80` 將維護腳本自 `scripts/` 移入 `scripts/maintenance/`，使檔案層級加深一層。原先寫法 `Path(__file__).resolve().parents[1]` 指向的不再是專案根目錄，而是 `scripts/` 目錄。
2. 由此，`PROJECT_BASE` 被賦值為不存在的路徑，動態掃描函式 `discover_skills()` 找不到任何受控技能，將 `ALL_CONTROLLED_SKILLS` 設為空串列。
3. 四大指標的檢驗函式均使用 `for skill in ALL_CONTROLLED_SKILLS:`，因串列為空，所有檢查迴圈全部略過，統計數全為 0。
4. 腳本未設置「受控技能清單不得為空」的安全防線（Guardrail），在檢查項目全為 0 的情況下，錯誤地印出「四大指標全數 PASS」並以 Exit code 0 退出。
5. 實作者 `worker_m4` 在 handoff.md 中引用了此 Exit code 0，未仔細審查終端印出的「掃描 0 處連結、0 份檔案、0 份腳本」，直接宣告 Milestone 4 達成。
6. 單元測試 `tests/unit/test_skills_audit.py` 中的 `test_skills_architecture_audit_passes()` 僅斷言 `result.returncode == 0`，未校驗受測技能數量，形成測試空洞與虛假綠燈。
7. 同時由 **Observation 3**，該目錄下所有相關腳本均存在同源路徑錯誤，導致維護與同步工具鏈實質癱瘓。
8. 由 **Observation 5**，一旦將專案端路徑修復，稽核腳本還原為真正的雙端檢查時，全域端因尚未同步該 8 個技能，將直接報錯，證實「四大指標全數 PASS」之宣稱與系統實際現狀不符。
9. 根據團隊審查與對抗性準則，此現象屬於典型之 Facade Verification（虛假檢驗），構成 INTEGRITY VIOLATION，必須退回實作者修改，不得予以 APPROVE。

---

## 3. Caveats (限制與注意事項)

1. **非惡意造假**：此路徑問題源於目錄重構（M3）時未同步更新腳本相對父層路徑，並非實作者刻意植入造假代碼，但實作者未做實質驗證即宣稱「四大指標全數 PASS」，違反驗證責任。
2. **專案端代碼品質優良**：經對抗性深度驗證，專案端（`skills/`）本體的 17 個技能實質上已具備高品質，四大指標在專案端全部可真實通過。
3. **XFAIL 測試說明**：5 個 xfailed 與 1 個 xpassed 屬於極限邊界壓力測試的預期行為，不屬於缺陷。

---

## 4. Findings (審查發現明細)

### [Critical] Finding 1 (INTEGRITY VIOLATION / Facade Verification)
- **問題**：`scripts/maintenance/audit_architecture_compliance.py` 搜尋路徑錯誤，導致掃描 0 筆資料即回傳 Exit Code 0，形成虛假通過。
- **位置**：`scripts/maintenance/audit_architecture_compliance.py:28-29`、`worker_m4/handoff.md:52-61`、`tests/unit/test_skills_audit.py:38-46`。
- **原因**：`Path(__file__).resolve().parents[1]` 僅抵達 `scripts/`，未抵達專案根目錄（應為 `parents[2]`）。
- **修復建議**：
  1. 將第 28-29 行改為：
     ```python
     _project_root = Path(__file__).resolve().parents[2]
     _skills_candidate = _project_root / "skills"
     PROJECT_BASE = str(_skills_candidate if _skills_candidate.is_dir() else _project_root / "SKILLs")
     ```
  2. 在 `discover_skills()` 與 `main()` 中增加防禦門禁：若受控技能數量為 0，必須拋出例外並以 Exit code 1 失敗，嚴禁空迴圈判定為 PASS。
  3. 在 `tests/unit/test_skills_audit.py` 中斷言輸出文字必須包含 `掃描 [1-9][0-9]* 份檔案`，防止空跑。

### [Major] Finding 2 (維護腳本集體路徑失效與同步工具失能)
- **問題**：`setup_skill_junctions.py`、`sync_skills_bidirectional.py`、`sync_skills.ps1` 根目錄相對路徑全部錯誤。
- **位置**：
  - `scripts/maintenance/setup_skill_junctions.py:19`
  - `scripts/maintenance/sync_skills_bidirectional.py:47, 49, 356`
  - `scripts/maintenance/sync_skills.ps1:3`
- **原因**：遷移至 `maintenance/` 後未同步提升至 `parents[2]`，且未完全相容小寫 `skills/`。
- **修復建議**：全面將維護腳本中的 `parents[1]` 更新為 `parents[2]`，並統一支援小寫 `skills` 與大寫 `SKILLs` 的後備相容。

### [Major] Finding 3 (全域端技能未同步導致稽核無法過關)
- **問題**：全域端（`~/.gemini/config/skills`）缺少專案端 8 個技能，導致修復路徑後的稽核腳本在第二階段（全域端）判定 FAIL。
- **位置**：`scripts/maintenance/audit_architecture_compliance.py:211`
- **修復建議**：
  - 修復 `sync_skills_bidirectional.py` 後，執行一次完整的雙向鏡像同步，將專案端新增的 8 個技能同步至全域端；或是在 `audit_architecture_compliance.py` 中明確區分本機單元測試與全域環境檢查，避免未同步時阻斷本機 CI。

### [Minor] Finding 4 (pytest 警告殘留)
- **問題**：5 個測試函數返回了布林值而非使用 `assert`，觸發 `PytestReturnNotNoneWarning`。
- **位置**：`tests/adversarial/test_final_stress_harness.py:test_section_1_fourteen_tools_stress` 等。
- **修復建議**：將函數內最後的 `return True` 改為 `assert True` 或直接結束。

---

## 5. Verified Claims (已驗證屬實項目)

- [x] 全專案 pytest 496 項可用測試 100% 通過（0 failed, 0 errors, 0 skipped） → 驗證通過。
- [x] 專案根層級 `src/ansys_unified_mcp/products/mechanical.py` 實體檔案已徹底移除 → 驗證通過。
- [x] 全庫 mechanical 引用全面收斂至 `ansys_unified_mcp.products.mechanical.facade` → 驗證通過。
- [x] `skills/` 下 17 個目錄名稱與 `SKILL.md` 的 frontmatter `name` 完全一致 → 驗證通過。
- [x] 專案端 17 個技能之 SKILL.md 行數全數 <= 200 行，且 107 處相對超連結 0 死鏈 → 驗證通過。
- [x] 專案端 17 個技能手冊與示範代碼繁體中文語系 100% 合規，17 份 Python 腳本 py_compile 100% 通過 → 驗證通過。
- [x] AST 解析全庫 MCP 工具總數為 138 個（含 geometry 與 optislang 產品工具） → 驗證通過。

---

## 6. Coverage Gaps & Unverified Items (未覆蓋與未驗證項目)

- **Coverage Gap**: `audit_architecture_compliance.py` 在正式全域端運行時的連通性與同步狀態（目前因全域端缺檔而受阻）。
- **Unverified Items**: 無。

---

## 7. Conclusion (最終審查結論)

**審查結論**：**REQUEST_CHANGES (退回修改)**

實作者在單元測試修復與舊版引用消除方面表現良好（pytest 496 通過），但未對 `audit_architecture_compliance.py` 及其維護工具鏈進行實質審核，將「掃描 0 份檔案的空迴圈」誤判為「四大指標全數 PASS」。

請實作者 `worker_m4` 依據上述 Findings 完成以下退回修復事項：
1. 修復 `scripts/maintenance/audit_architecture_compliance.py` 的路徑解析（改用 `parents[2]`），並加入「受控技能數為 0 時強制報錯」的門禁防線。
2. 同步修復 `scripts/maintenance/setup_skill_junctions.py`、`scripts/maintenance/sync_skills_bidirectional.py` 與 `sync_skills.ps1` 的路徑與目錄名稱相容性。
3. 執行技能同步或調整稽核標的，確保執行 `.venv\Scripts\python.exe scripts/maintenance/audit_architecture_compliance.py` 時，能**實質掃描全部 17 個技能、超過 100 份檔案與連結**，並在全數 PASS 的前提下取得 Exit code 0。
4. 重新執行全專案 pytest，確保 `test_skills_architecture_audit_passes` 是在實質掃描 17 個技能的狀態下綠燈通過。

---

## 8. Verification Method (獨立驗證方法)

1. **檢驗稽核腳本是否真正檢查檔案（非 0 筆檢查）**：
   ```powershell
   & F:\Ming_python\ansys-unified-mcp\.venv\Scripts\python.exe F:\Ming_python\ansys-unified-mcp\scripts\maintenance\audit_architecture_compliance.py
   ```
   *無效判定條件*：若輸出包含「掃描 0 處連結」或「掃描 0 份檔案」，直接判定驗證失敗。  
   *合格判定條件*：掃描連結數 > 0，掃描檔案數 > 0，四大指標全數 PASS，Exit code 0。

2. **全專案 pytest 完整測試驗證**：
   ```powershell
   & F:\Ming_python\ansys-unified-mcp\.venv\Scripts\pytest.exe -v
   ```
   *合格判定條件*：`496 passed, 0 failed, 0 errors, 0 skipped`，Exit code 0。

3. **連接點與同步腳本健康度驗證**：
   ```powershell
   & F:\Ming_python\ansys-unified-mcp\.venv\Scripts\python.exe F:\Ming_python\ansys-unified-mcp\scripts\maintenance\setup_skill_junctions.py --verify-only
   & F:\Ming_python\ansys-unified-mcp\.venv\Scripts\python.exe F:\Ming_python\ansys-unified-mcp\scripts\maintenance\sync_skills_bidirectional.py --verify-only
   ```
   *合格判定條件*：兩者皆需以 Exit code 0 結束，且受控技能數為 17 項（非 0 項）。
