# R2 Agent Skills 規範與漸進式揭露現況調研報告 (Skills Compliance)

- **調研代理**：`explorer_survey_2` (teamwork_preview_explorer)
- **調查對象**：專案根目錄 `F:\Ming_python\ansys-unified-mcp\skills`
- **調研依據**：`agentskills.io` 開放規範、Progressive Disclosure 準則、`ORIGINAL_REQUEST.md`
- **日期**：2026-10-01

---

## 執行摘要 (Executive Summary)

本報告對專案根目錄 `skills/` 進行了全面的只讀探查與靜態合規性分析。整體而言，專案已經具備良好的漸進式揭露意識，**所有 26 份 `SKILL.md` 的行數皆控制在 150 行以內（遠低於 500 行臨界值）**，且均具備語法合法的 YAML frontmatter。

然而，在深入比對 `agentskills.io` 開放標準與實際架構維護性後，發現了 **5 項重大合規性缺陷與技術債**：
1. **命名嚴重不一致（Name-Folder Mismatch）**：`shock-analysis-workflow` 底下的 8 個子 Session，其 YAML frontmatter 中的 `name` 為 `shock-session-*`，與資料夾名稱 `01-*` 至 `08-*` 完全不一致。
2. **目錄結構命名偏離標準（Plural vs Singular）**：全專案 22 處參考資料夾採用了單數 **`reference/`**，違反了 `agentskills.io` 規範要求的複數 **`references/`**。
3. **極高冗餘與幾何技能分裂（Duplication & Triplication）**：`ansys-geometry-modeling` 與 `ansys-spaceclaim-modeling` 兩者的 6 篇參考文檔與 2 個腳本 **100% 逐字重複**；且與 `ansys-spaceclaim` 形成三軌維護。
4. **散落腳本與非標準組織**：`pdf-to-md` 根目錄直接暴露 `convert.py`，未納入 `scripts/`。
5. **異物技能混入**：`antigravity-notebooklm` 為非 ANSYS CAE 技能，違反 `skills/README.md`「保持 100% 純淨 ANSYS CAE 專案庫」的原則。

---

## 第一部分：專案 Skills 完整盤點清單

專案根目錄 `skills/` 下共有 **18 個一級子資料夾**、**26 個 `SKILL.md`** 以及 **112 個 Markdown 檔案**。

### 一級技能目錄清冊與結構狀態

| # | 技能目錄名稱 | SKILL.md 行數 | YAML Name | Name 匹配 | 描述清晰度 | 子目錄結構 | 主要問題標記 |
|---|---|---|---|---|---|---|---|
| 1 | `act-extension-development` | 56 行 | `act-extension-development` | ✅ 匹配 | ✅ 清晰 | `reference/`, `scripts/` | 使用單數 `reference/` |
| 2 | `ansys-error-catalog` | 40 行 | `ansys-error-catalog` | ✅ 匹配 | ✅ 清晰 | `reference/`, `scripts/` | 使用單數 `reference/` |
| 3 | `ansys-fluent` | 101 行 | `ansys-fluent` | ✅ 匹配 | ✅ 清晰 | `reference/`, `scripts/` | 使用單數 `reference/`；內含 20 行示例程式碼 |
| 4 | `ansys-geometry-modeling` | 74 行 | `ansys-geometry-modeling` | ✅ 匹配 | ✅ 清晰 | `reference/`, `scripts/` | 與 `ansys-spaceclaim-modeling` 100% 重複 |
| 5 | `ansys-ls-prepost` | 56 行 | `ansys-ls-prepost` | ✅ 匹配 | ✅ 清晰 | `reference/`, `scripts/` | 使用單數 `reference/` |
| 6 | `ansys-lsdyna` | 67 行 | `ansys-lsdyna` | ✅ 匹配 | ✅ 清晰 | `reference/`, `scripts/` | 使用單數 `reference/` |
| 7 | `ansys-mechanical` | 104 行 | `ansys-mechanical` | ✅ 匹配 | ✅ 清晰 | `reference/`, `scripts/` | 使用單數 `reference/` |
| 8 | `ansys-mesh` | 147 行 | `ansys-mesh` | ✅ 匹配 | ✅ 清晰 | `reference/`, `scripts/` | 使用單數 `reference/`；未列入 `skills/README.md` |
| 9 | `ansys-optislang` | 65 行 | `ansys-optislang` | ✅ 匹配 | ✅ 清晰 | `reference/`, `scripts/` | 使用單數 `reference/` |
| 10 | `ansys-parametric-study` | 54 行 | `ansys-parametric-study` | ✅ 匹配 | ✅ 清晰 | `reference/`, `scripts/` | 使用單數 `reference/` |
| 11 | `ansys-spaceclaim` | 53 行 | `ansys-spaceclaim` | ✅ 匹配 | ✅ 清晰 | `reference/`, `scripts/` | 使用單數 `reference/`；與另兩技能重疊 |
| 12 | `ansys-spaceclaim-modeling` | 74 行 | `ansys-spaceclaim-modeling` | ✅ 匹配 | ✅ 清晰 | `reference/`, `scripts/` | 與 `ansys-geometry-modeling` 100% 重複 |
| 13 | `ansys-submodeling-dpf` | 58 行 | `ansys-submodeling-dpf` | ✅ 匹配 | ✅ 清晰 | `reference/`, `scripts/` | 使用單數 `reference/` |
| 14 | `antigravity-notebooklm` | 66 行 | `antigravity-notebooklm` | ✅ 匹配 | ✅ 清晰 | 無 | 非 CAE 異物技能；缺 `scripts/`、`references/` |
| 15 | `pcb-warpage-analysis` | 39 行 | `pcb-warpage-analysis` | ✅ 匹配 | ✅ 清晰 | `scripts/` | 缺 `references/` |
| 16 | `pdf-to-md` | 64 行 | `pdf-to-md` | ✅ 匹配 | ✅ 清晰 | 無 | 根目錄裸露 `convert.py`；缺 `scripts/` |
| 17 | `pymechanical-operations` | 55 行 | `pymechanical-operations` | ✅ 匹配 | ✅ 清晰 | `reference/`, `scripts/` | 使用單數 `reference/` |
| 18 | `shock-analysis-workflow` | 32 行 | `shock-analysis-workflow` | ✅ 匹配 | ✅ 清晰 | 8 個子目錄, `scripts/` | 子目錄包含 8 個違規子 SKILL.md |

---

## 第二部分：agentskills.io 合規性深度檢核

### 1. YAML Frontmatter 與命名檢查
- **合法性與解析**：全專案 26 份 `SKILL.md` 之 YAML Frontmatter 皆可被標準 PyYAML 解析器正確解析，無語法中斷。
- **`name` 屬性格式**：26 份皆符合全小寫連字號（`^[a-z0-9]+(-[a-z0-9]+)*$`），合規率 100%。
- **`name` 與所在資料夾名稱一致性**：
  - 一級技能目錄（18 個）：100% 一致。
  - **二級子技能目錄（8 個）：100% 不一致（重大違規）**。

#### `shock-analysis-workflow` 子目錄不一致詳表：
| 子目錄相對路徑 | 資料夾名稱 (Folder Name) | YAML Frontmatter `name` | 判定結果 |
|---|---|---|---|
| `shock-analysis-workflow/01-material-assignment/` | `01-material-assignment` | `shock-session-material-assignment` | ❌ 不匹配 |
| `shock-analysis-workflow/02-contact-creation/` | `02-contact-creation` | `shock-session-contact-creation` | ❌ 不匹配 |
| `shock-analysis-workflow/03-mesh-tuning/` | `03-mesh-tuning` | `shock-session-mesh-tuning` | ❌ 不匹配 |
| `shock-analysis-workflow/04-connection-rm/` | `04-connection-rm` | `shock-session-connection-rm` | ❌ 不匹配 |
| `shock-analysis-workflow/05-section-assignment/` | `05-section-assignment` | `shock-session-section-assignment` | ❌ 不匹配 |
| `shock-analysis-workflow/06-constraint-load/` | `06-constraint-load` | `shock-session-constraint-load` | ❌ 不匹配 |
| `shock-analysis-workflow/07-solve-monitor/` | `07-solve-monitor` | `shock-session-solve-monitor` | ❌ 不匹配 |
| `shock-analysis-workflow/08-post-process-report/` | `08-post-process-report` | `shock-session-post-process-report` | ❌ 不匹配 |

### 2. 行數統計與 Progressive Disclosure 瘦身現況
- **大於 500 行的 SKILL.md**：**0 個**（全部通過）。
- **行數分布**：
  - 100 ~ 150 行：3 個（`ansys-mesh` 147 行、`ansys-mechanical` 104 行、`ansys-fluent` 101 行）。
  - 50 ~ 100 行：19 個。
  - < 50 行：4 個（`ansys-error-catalog` 40 行、`pcb-warpage-analysis` 39 行、`shock-analysis-workflow` 32 行）。
- **分析結論**：在主手冊行數控制上，現有技能已經達成漸進式揭露的行數目標（$\le 150$ 行），無須針對主文字進行大規模行數砍半，而是需要針對目錄結構與重複代碼進行標準化。

### 3. Progressive Disclosure 目錄結構偏離：`reference` vs `references`
依據 `agentskills.io` 官方規範，技能目錄之標準階層為：
```
<skill-name>/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```
在專案中，**高達 22 處（所有包含參考資料的技能）皆誤用單數 `reference/`**，標準通用 Agent 載入器將無法自動識別為 `references` 資料集。

---

## 第三部分：專案內代碼重複與架構技術債分析

### 1. 嚴重重複：`ansys-geometry-modeling` 與 `ansys-spaceclaim-modeling`
透過逐位元 (byte-by-byte) 比對，這兩個目錄下除 `SKILL.md` 有極微小文字修飾外，其餘所有參考資料與實作腳本 **100% 相同**：
- `reference/3d_features.md` (完全相同)
- `reference/booleans_enclosures.md` (完全相同)
- `reference/cad_diagnostics.md` (完全相同)
- `reference/named_selections.md` (完全相同)
- `reference/pmdb_export_rules.md` (完全相同)
- `reference/sketching.md` (完全相同)
- `scripts/check_cad_defects.py` (完全相同)
- `scripts/create_enclosure_demo.py` (完全相同)

此外，專案還同時存在 `ansys-spaceclaim`。這導致幾何前處理存在三個平行技能，使用者和 Agent 在選擇幾何工具時會發生混淆與上下文浪費。

### 2. 散落檔案：`pdf-to-md`
- `skills/pdf-to-md/convert.py` 直接放於根目錄下，未置於 `scripts/` 中。依規範應建立 `scripts/` 並將其移入。

### 3. 異物技能：`antigravity-notebooklm`
- 該技能專用於 Google NotebookLM MCP 與 CLI 串接，不屬於 ANSYS CAE 模擬生態系。且 `skills/README.md` 明確宣告：「本倉庫保持 100% 純淨的 ANSYS 模擬、自動化與 MCP 驅動專用架構。全案通用/非 ANSYS 技能保留於全域技能庫，不污染本 CAE 倉庫。」

### 4. `skills/README.md` 索引缺漏與語法損壞
- 表格標頭第 10~14 行夾雜了無效的 `phase_gate` YAML 標籤，破壞了 Markdown 表格渲染。
- 表格內僅索引 16 項技能，遺漏了 `ansys-mesh` 與 `antigravity-notebooklm`。

---

## 第四部分：具體重構建議清單 (Actionable Recommendations)

為落實 R2 與整體重構目標，建議後續實作代理（Implementer）按以下 4 步進行標準化改造：

### 調整一：更名目錄以符合 `agentskills.io` 規範（`reference/` $\rightarrow$ `references/`）
將專案中所有技能內部的 `reference/` 資料夾統一更名為 `references/`，並同步更新各 `SKILL.md` 與文檔內的相對超連結 `[xxx](reference/yyy.md)` $\rightarrow$ `[xxx](references/yyy.md)`。
- 涉及技能：共 14 個一級技能與 8 個 shock 子 session。

### 調整二：重構 `shock-analysis-workflow` 架構
解決資料夾與 YAML `name` 不一致有兩種策略：
- **推薦方案（標準平鋪）**：將 `shock-analysis-workflow` 維持為 Orchestrator 技能，而將 8 個子 Session 平鋪提升至 `skills/` 一級目錄（如 `skills/shock-session-material-assignment`），或將其子目錄更名為 `shock-session-material-assignment`。
- **替代方案（模組內部化）**：若子 Session 不作為獨立對外技能，則移除子目錄中的 `SKILL.md`，轉為 `references/sessions/01-material-assignment.md`，由主 `SKILL.md` 透過 Progressive Disclosure 引導調用。此法最為乾淨，徹底杜絕子目錄 SKILL 命名爭端。

### 調整三：整併幾何前處理技能，消除重複
- 保留 `ansys-geometry-modeling`（代表現代化 PyAnsys Geometry 路線）與 `ansys-spaceclaim`（代表經典 SpaceClaim ACT 腳本路線）。
- 完全移除 `ansys-spaceclaim-modeling`（重複率 100%），其別名與關鍵字併入 `ansys-geometry-modeling` 與 `ansys-spaceclaim` 的 frontmatter `description` 中。

### 調整四：標準化散落腳本與清理異物
1. 在 `skills/pdf-to-md/` 建立 `scripts/` 資料夾，並將 `convert.py` 移入 `scripts/convert.py`。
2. 將非 CAE 的 `antigravity-notebooklm` 自本專案 `skills/` 移除或歸檔移至全域。
3. 配合 R3 需求，將根目錄 `scripts/_archive_mesh_fix_202609/` 的 12 個網格修復腳本整理移入 `skills/ansys-mesh/scripts/`，並在 `ansys-mesh/SKILL.md` 與 `references/` 中補充路由。
4. 修復 `skills/README.md` 的 Markdown 表格語法錯誤，並補齊 `ansys-mesh` 索引。
