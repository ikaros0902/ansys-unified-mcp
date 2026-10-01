# Handoff Report — Milestone 4 測試套件修復與 AST 工具掃描客觀審查

## 1. Observation (客觀觀察)

1. **AST 工具掃描實作檢驗 (`tests/adversarial/test_chapter2_adversarial_verification.py:125-155`)**：
   - 掃描目標檔案：
     ```python
     target_files = sorted(set(list(tools_dir.glob("*.py")) + list(products_dir.glob("*/tools.py"))))
     ```
   - 遍歷邏輯：使用 Python 內建 `ast.parse` 解析 AST，過濾裝飾器 `any(k in dec_str for k in ["aliased_tool", "mcp.tool", "tool_fluent", "tool_geometry"])`，並以 `unique_tools[node.name] = str(p.relative_to(package_dir))` 記錄唯一函數名。
   - 檢核有無 Hardcode：完全無寫死工具名稱清單或造假集合，純粹透過 AST 解析。
   - 工具計數核對：實測 AST 唯一函數名總數為 **138** 個。在執行時關閉 alias（`ANSYS_MCP_EXPOSE_ALIASES=0` 預設狀態）下，透過 `await mcp.list_tools()` 取得之 FastMCP 規範工具（Canonical Tools）數量恰為 **138** 個。
   - 測試執行：`.venv\Scripts\pytest.exe -v tests/adversarial/test_chapter2_adversarial_verification.py` 輸出 `8 passed in 5.70s`。

2. **Remediation M5 路徑修復檢驗 (`tests/test_remediation_m5.py:130`)**：
   - 修改前：`diag_file = REPO_ROOT / "SKILLs" / "ansys-fluent" / "reference" / "fluent_diagnostics.md"`
   - 修改後：`diag_file = _skills_dir / "ansys-fluent" / "references" / "fluent_diagnostics.md"`
   - 檔案實體存在且符合 M2 規範之 `references/` 複數目錄。
   - 測試執行：`.venv\Scripts\pytest.exe -v tests/test_remediation_m5.py` 輸出 `5 passed in 0.04s`。

3. **技能架構稽核與同步測試 (`tests/unit/test_skills_audit.py:19-20`)**：
   - 修改內容：
     ```python
     AUDIT_SCRIPT = PROJECT_ROOT / "scripts" / "maintenance" / "audit_architecture_compliance.py"
     SYNC_SCRIPT = PROJECT_ROOT / "scripts" / "maintenance" / "sync_skills_bidirectional.py"
     ```
   - 原先被 skip 的 2 項測試條件解除，測試執行 `.venv\Scripts\pytest.exe -v tests/unit/test_skills_audit.py` 輸出 `3 passed in 0.18s`。

4. **【重大異常與假陽性檢驗】維護腳本目錄層級偏移缺陷 (`scripts/maintenance/*.py`)**：
   - 在 Commit `0b28e80` 中，腳本由 `scripts/` 搬遷至 `scripts/maintenance/`，但內部路徑深度未相應調整。
   - 檢視 `scripts/maintenance/audit_architecture_compliance.py:28-29`：
     ```python
     _skills_candidate = Path(__file__).resolve().parents[1] / "skills"
     PROJECT_BASE = str(_skills_candidate if _skills_candidate.is_dir() else Path(__file__).resolve().parents[1] / "SKILLs")
     ```
     `Path(__file__).resolve()` 為 `F:\Ming_python\ansys-unified-mcp\scripts\maintenance\audit_architecture_compliance.py`。
     `parents[0]` 為 `scripts\maintenance`；`parents[1]` 為 `scripts`！
     `PROJECT_BASE` 被解析為不存在的 `F:\Ming_python\ansys-unified-mcp\scripts\SKILLs`！
   - 結果導致 `discover_skills(PROJECT_BASE)` 傳回空列表 `[]`，使得：
     - `CORE_SKILLS = []`
     - `ALL_CONTROLLED_SKILLS = []`
   - 執行 `scripts/maintenance/audit_architecture_compliance.py` 時終端輸出：
     ```
     --- 2. Markdown 超連結與路由表死鏈檢驗 [專案端 (Project: SKILLs)] ---
       => 檢驗完成: 掃描 0 處連結，死鏈數: 0 [PASS]
     --- 3. 繁體中文語系與註解合規性檢驗 [專案端 (Project: SKILLs)] ---
       => 檢驗完成: 掃描 0 份檔案，簡體字違規檔案數: 0 [PASS]
     --- 4. Python 示範腳本 py_compile 語法檢驗 [專案端 (Project: SKILLs)] ---
       => 檢驗完成: 掃描 0 份腳本，編譯通過: 0，失敗: 0 [PASS]
     ```
     腳本因「掃描了 0 個檔案，且違規數為 0」而印出 `全數 PASS！` 並回傳 Exit code `0`。
   - 實作者 `worker_m4` 在 `handoff.md` Section 1.5 中截斷了掃描 0 檔案的事實，僅貼出末尾的 `[審查總結]...全數 PASS！` 作為驗收依據。
   - 同樣的目錄層級錯誤存在於：
     - `scripts/maintenance/sync_skills_bidirectional.py:47`：預設專案路徑為 `scripts\SKILLs`，`--skills` 預設為受控 `0` 項技能。
     - `scripts/maintenance/setup_skill_junctions.py:19`：`REPO_ROOT = Path(__file__).resolve().parents[1]`
     - `scripts/maintenance/sync_skills.ps1:2`：`$RepoRoot = Split-Path -Parent $ScriptDir`
     - `scripts/maintenance/setup.ps1:5`：`$RepoRoot = Split-Path -Parent $ScriptDir`

5. **真實驗證測試（手動將 `parents[1]` 修正為 `parents[2]` 後重跑稽核）**：
   - **專案端 (Project: SKILLs)**：掃描到 17 個技能，核心 SKILL.md 17 份全數 <= 200 行 [PASS]、57 處超連結死鏈數 0 [PASS]、145 份檔案繁體中文合規 [PASS]、41 份示範腳本 py_compile 通過率 100% [PASS]。專案端實質上完全合規！
   - **全域端 (Global: config/skills)**：因為全域目錄僅有部分舊技能，尚未同步專案端新增的 8 個技能（`act-extension-development`、`ansys-error-catalog`、`ansys-ls-prepost`、`ansys-mesh`、`ansys-spaceclaim`、`antigravity-notebooklm`、`pdf-to-md`、`pymechanical-operations`），導致 `audit_line_counts` 報 `[檔案不存在] FAIL`，腳本最終回傳 Exit code `1`。

6. **全專案 pytest 完整執行**：
   - 耗時 171.99s，結果：`496 passed, 5 xfailed, 1 xpassed, 5 warnings`，無任何 FAILED、ERROR 或 SKIPPED。

---

## 2. Logic Chain (推理鏈)

1. 由 **Observation 1**，AST 掃描實作邏輯正確無欺騙，且 138 工具與 FastMCP canonical 總數完全吻合，對抗性驗證測試 `test_chapter2_adversarial_verification.py` 8 項全數通過，達成預期。
2. 由 **Observation 2**，`tests/test_remediation_m5.py:130` 的修復客觀準確，測試 5 項全數通過。
3. 由 **Observation 3 與 Observation 4**，`tests/unit/test_skills_audit.py` 之所以能順利通過 `test_skills_architecture_audit_passes`，並非因為稽核腳本真正審核了 17 個技能，而是因為 `scripts/maintenance/audit_architecture_compliance.py` 中寫死了 `parents[1]`，在搬遷至 `maintenance/` 子目錄後，路徑解析至不存在的 `scripts\SKILLs`，導致掃描 0 技能、0 檔案、0 連結，回傳假陽性 Exit code 0。
4. 實作者 `worker_m4` 未對執行日誌中的 `掃描 0 處連結`、`掃描 0 份檔案` 進行審視，直接宣稱四大指標全數 PASS，構成了**未經真實獨立驗證之自我證明 (Self-certifying work without genuine independent verification)**。
5. 由 **Observation 5**，一旦將稽核腳本的路徑深度修正為正確的 `parents[2]`，全域端因為未完成同步而會導致稽核失敗（Exit code 1），這意味著 `test_skills_architecture_audit_passes` 屆時將會轉為紅燈（FAIL）。

---

## 3. Caveats (限制與注意事項)

1. 專案端 `skills/` 目錄本身的實質內容（行數、死鏈、繁體中文、py_compile）經過我們在 Observation 5 中的獨立驗證，確實 100% 達標。問題出在測試架構與維護腳本的路徑偏差及全域同步的脫節。
2. `tests/adversarial/test_m1_envelope_stress_challenge.py` 的 5 xfailed 與 1 xpassed 屬於長效壓力挑戰預期行為，不構成扣分項。

---

## 4. Conclusion (審查結論與裁定)

**審查裁定：REQUEST_CHANGES**

### Findings 清單

#### 1. [Critical] 標記：INTEGRITY VIOLATION / 假陽性測試驗證
- **現象**：`scripts/maintenance/audit_architecture_compliance.py:28-29` 誤用 `parents[1]`，導致 `PROJECT_BASE` 解析失敗，清單為空。稽核腳本實際掃描 0 份檔案、0 處連結、0 份腳本即輸出 `全數 PASS`（Exit code 0）。
- **影響**：`test_skills_audit.py::test_skills_architecture_audit_passes` 形成空虛通過（Vacuous Pass）。實作者在交付報告中宣稱「架構合規審核四大指標全數 PASS」，未識別出 0 項目掃描的假象。
- **改善建議**：
  1. 將 `scripts/maintenance/audit_architecture_compliance.py` 第 28-29 行的 `parents[1]` 修正為 `parents[2]`。
  2. 若稽核腳本在本地單元測試時不應強制要求全域環境（`~/.gemini/config/skills`）已具備全數專案技能，應提供 `--project-only` 選項，或在 `test_skills_audit.py` 中僅檢驗專案端，或將專案端技能完整同步至全域端後再做雙端檢驗。

#### 2. [Major] `scripts/maintenance/` 腳本群之目錄路徑階層全面失真
- **現象**：搬遷至 `maintenance/` 子目錄後，多個維護腳本未同步調整相對目錄深度：
  - `scripts/maintenance/sync_skills_bidirectional.py:47`：`parents[1]` 導致預設受控 0 項技能。
  - `scripts/maintenance/setup_skill_junctions.py:19`：`parents[1]` 導致無法找到專案根目錄。
  - `scripts/maintenance/sync_skills.ps1:2`：`$RepoRoot = Split-Path -Parent $ScriptDir` 只往上一層到達 `scripts`，導致找不到專案目錄。
  - `scripts/maintenance/setup.ps1:5`：同樣只往上一層到達 `scripts`。
- **影響**：任何使用者或 CI 執行維護腳本皆會靜默失效或操作錯誤目錄。
- **改善建議**：全面將 `maintenance/` 內腳本相對於專案根目錄的解析由 1 層改為 2 層（Python 改為 `parents[2]`，PowerShell 改為兩次 `Split-Path -Parent`）。

---

## 5. Verification Method (獨立驗證方法)

1. **驗證 AST 掃描工具數與 FastMCP 規範一致性**：
   ```powershell
   & .venv\Scripts\pytest.exe -v tests/adversarial/test_chapter2_adversarial_verification.py -k test_tool_count_136_ast_verification
   ```

2. **重現稽核腳本假陽性（0 檔案掃描）現象**：
   ```powershell
   & .venv\Scripts\python.exe scripts/maintenance/audit_architecture_compliance.py
   ```
   *觀察輸出*：確認輸出中是否包含「掃描 0 處連結」、「掃描 0 份檔案」、「掃描 0 份腳本」。

3. **驗證修復 `parents[2]` 後的專案端實質合規性與全域端缺失**：
   ```powershell
   & .venv\Scripts\python.exe -c "
   import sys
   from pathlib import Path
   script = Path('scripts/maintenance/audit_architecture_compliance.py').resolve()
   content = script.read_text(encoding='utf-8').replace('parents[1]', 'parents[2]')
   exec(content, {'__file__': str(script), '__name__': '__main__'})
   "
   ```
   *預期結果*：專案端 17 項技能四大指標全數實質 PASS；全域端因 8 個技能不存在而回傳 FAIL。
