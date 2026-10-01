# 5-Component 交付報告 (handoff.md)

- **代理識別碼**：`explorer_survey_2`
- **任務目標**：R2 Agent Skills 規範與漸進式揭露現況只讀探查 (Skills Compliance)
- **交付類型**：Hard Handoff（調研任務完整交付）
- **日期**：2026-10-01

---

## 1. Observation (觀察事實)

透過 Python 靜態腳本、PowerShell 與 `view_file` 工具進行全盤只讀掃描，獲得以下客觀數據：

1. **技能總數與目錄**：
   - 專案根目錄 `F:\Ming_python\ansys-unified-mcp\skills` 下存在 18 個子資料夾（排除 `.zvec-grep`）。
   - 遞迴搜尋共發現 **26 個 `SKILL.md`** 檔案（18 個位於一級目錄，8 個位於 `shock-analysis-workflow` 底下的子目錄）。
   - 統計共包含 **112 個 Markdown (`.md`) 檔案**。
2. **YAML Frontmatter 檢驗**：
   - 26 個 `SKILL.md` 皆具備 `---` 包裹且通過 PyYAML 解析。
   - 所有 `name` 皆符合 `^[a-z0-9]+(-[a-z0-9]+)*$` 連字號小寫規範。
   - 18 個一級技能的 `name` 與資料夾名稱完全吻合。
   - **`shock-analysis-workflow` 的 8 個子目錄存在 100% 命名不符**：
     - `shock-analysis-workflow/01-material-assignment/SKILL.md:2`：`name: shock-session-material-assignment` vs folder `01-material-assignment`
     - `shock-analysis-workflow/02-contact-creation/SKILL.md:2`：`name: shock-session-contact-creation` vs folder `02-contact-creation`
     - `shock-analysis-workflow/03-mesh-tuning/SKILL.md:2`：`name: shock-session-mesh-tuning` vs folder `03-mesh-tuning`
     - `shock-analysis-workflow/04-connection-rm/SKILL.md:2`：`name: shock-session-connection-rm` vs folder `04-connection-rm`
     - `shock-analysis-workflow/05-section-assignment/SKILL.md:2`：`name: shock-session-section-assignment` vs folder `05-section-assignment`
     - `shock-analysis-workflow/06-constraint-load/SKILL.md:2`：`name: shock-session-constraint-load` vs folder `06-constraint-load`
     - `shock-analysis-workflow/07-solve-monitor/SKILL.md:2`：`name: shock-session-solve-monitor` vs folder `07-solve-monitor`
     - `shock-analysis-workflow/08-post-process-report/SKILL.md:2`：`name: shock-session-post-process-report` vs folder `08-post-process-report`
3. **行數與 Progressive Disclosure 現況**：
   - 專案內 **0 個 `SKILL.md` 行數超過 500 行**。最長者僅 147 行（`skills/ansys-mesh/SKILL.md`），全部小於 150 行。
   - 全專案有 **22 處**將參考文檔資料夾命名為單數 **`reference/`**，標準 `agentskills.io` 規範要求為複數 **`references/`**。
4. **檔案重複與三軌分裂**：
   - `filecmp.cmp` 逐位元檢驗證實：`skills/ansys-geometry-modeling` 與 `skills/ansys-spaceclaim-modeling` 兩者底下的 6 個 reference 文檔與 2 個 scripts 腳本 **100% 逐字相同**，僅 `SKILL.md` 有極微小文字修飾。
   - 專案同時存在 `ansys-geometry-modeling`、`ansys-spaceclaim-modeling`、`ansys-spaceclaim` 三個高度重合的幾何技能。
5. **散落與異物檔案**：
   - `skills/pdf-to-md/convert.py` 直接放於根目錄，缺少 `scripts/` 目錄。
   - `skills/antigravity-notebooklm` 屬於通用筆記輔助工具，非 ANSYS CAE 模擬技能。
   - `skills/README.md:10-14` 存在 `phase_gate` 語法錯誤致使表格破裂，且遺漏 `ansys-mesh` 索引。
   - `skills/shock-analysis-workflow/01-material-assignment/SKILL.md:63` 出現大小寫錯誤路徑 `python SKILLs/...`。

---

## 2. Logic Chain (推論邏輯鏈)

1. **依據 Observation 1 & 2**：
   - `agentskills.io` 規範要求 `SKILL.md` 的 YAML frontmatter 中的 `name` 必須與所在目錄名稱一致，否則代理搜尋或載入時會發生索引失效。
   - `shock-analysis-workflow` 底下的 8 個子資料夾命名為 `01-material-assignment`，但 YAML 宣告為 `shock-session-material-assignment`。這破壞了一致性。
2. **依據 Observation 3**：
   - 現有技能的 Markdown 總體積控制良好（皆 $\le 150$ 行），代表主手冊無需大規模刪減文字。
   - 但是 agentskills.io 規範的子目錄名為 `references/`（複數）與 `scripts/`。專案全面使用 `reference/`（單數），會導致標準 agentskills 載入器無法自動識別，必須統一批次更名。
3. **依據 Observation 4**：
   - `ansys-geometry-modeling` 與 `ansys-spaceclaim-modeling` 的重複度達 100%，造成雙軌維護風險。保留 PyAnsys Geometry 現代化路線（`ansys-geometry-modeling`）與 SpaceClaim ACT 路線（`ansys-spaceclaim`），並刪除重複的 `ansys-spaceclaim-modeling`，是消除技術債的最佳途徑。
4. **依據 Observation 5 & ORIGINAL_REQUEST R3**：
   - 散落於 `pdf-to-md` 的 `convert.py` 需規範化移入 `scripts/`。
   - 專案根目錄 `scripts/_archive_mesh_fix_202609/` 的 12 個網格修復腳本應整理移入 `skills/ansys-mesh/scripts/`。
   - 修復 `README.md` 的表格破裂與索引缺漏，使整個 `skills/` 達成乾淨閉環。

---

## 3. Caveats (限制與未探查領域)

1. **只讀探查**：本代理嚴格遵守只讀規範，未對 `skills/` 或原始碼進行任何檔案修改、更名或刪除。
2. **外部依賴性**：若其他專案程式碼（如測試或工具腳本）曾硬編碼引用 `skills/ansys-spaceclaim-modeling` 或 `reference/` 路徑，在實作更名時需一併全局 grep 更新。
3. **全局技能庫覆蓋**：本機 `C:\Users\Ming\.gemini\config\skills` 亦存在全域技能庫，但本報告聚焦於專案根目錄 `F:\Ming_python\ansys-unified-mcp\skills` 之合規。

---

## 4. Conclusion (結論與處置清單)

專案根目錄下的 Skills 已具備良好的結構雛型，但存在幾何三軌分裂、單複數命名偏離、子 Session 命名衝突等技術債。具體處置建議：
1. **目錄更名**：將全專案 22 處 `reference/` 更名為 `references/`，並修正超連結。
2. **重構 shock workflow**：將 `shock-analysis-workflow` 下 8 個子目錄轉為內部 references 文檔或平鋪更名，杜絕命名衝突。
3. **消除冗餘**：刪除完全重複的 `ansys-spaceclaim-modeling`，整合入 `ansys-geometry-modeling`。
4. **規範目錄**：將 `pdf-to-md/convert.py` 移入 `scripts/`；將 `scripts/_archive_mesh_fix_202609/` 遷移至 `skills/ansys-mesh/scripts/`。
5. **異物清理**：將非 CAE 的 `antigravity-notebooklm` 移出專案庫；修復 `skills/README.md` 索引與表格語法。

---

## 5. Verification Method (獨立驗證方法)

後續接手代理可執行以下指令獨立驗證上述發現：

```powershell
# 1. 驗證 shock workflow 命名不匹配
python -c "import os, yaml; [print(d, yaml.safe_load(open(f'skills/shock-analysis-workflow/{d}/SKILL.md', encoding='utf-8').read().split('---')[1])['name']) for d in os.listdir('skills/shock-analysis-workflow') if os.path.isdir(f'skills/shock-analysis-workflow/{d}') and d.startswith('0')]"

# 2. 驗證 ansys-geometry-modeling 與 ansys-spaceclaim-modeling 100% 相同
python -c "import filecmp, os; d1='skills/ansys-geometry-modeling/reference'; d2='skills/ansys-spaceclaim-modeling/reference'; print(all(filecmp.cmp(os.path.join(d1, f), os.path.join(d2, f)) for f in os.listdir(d1)))"

# 3. 驗證所有 SKILL.md 行數是否小於 150 行
python -c "import os; [print(f'{len(open(os.path.join(r, f), encoding=\"utf-8\").readlines()):4d} lines: {r}') for r, d, fs in os.walk('skills') for f in fs if f.lower() == 'skill.md']"

# 4. 檢驗 reference (單數) 的技能數量
python -c "import os; print(len([r for r, ds, fs in os.walk('skills') if 'reference' in ds]))"
```
