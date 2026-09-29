# 資料夾架構重整、資安遮罩與 ruff 閘門導入（chore/restructure 未提交變更）

這次變更做三件事：把根目錄 9 份 md + 1 html 收進 `docs/` 六個分類子目錄、刪除一份公司內部提案逐字稿與兩支零引用的 RAG 腳本、把追蹤檔內的員工編號絕對路徑遮罩為 `%USERPROFILE%`；同時把 684 MB 的 ANSYS 文件語料以 `ANSYS_DOCS_ROOT` 環境變數移出 repo，並補上 `[tool.ruff]` 讓 `TEST_INFRA.md` 宣稱的 Tier 1 閘門有實體設定。14 筆 `git mv` 被 git 正確識別為 rename，全套測試 449 passed / 6 xfailed，`config.py` 的路徑改碼經執行期實測全數正確。

**Watch for:**
- **資安止血只完成一半（confirmed）**：被刪的 `slides_detailed.md` 與被遮罩的員工編號 `REDACTED_UID` 仍完整存在於 `origin/master` 的已推送歷史中，公開可取。工作區清乾淨不等於 GitHub 上清乾淨。
- **`docs/archive/README.md:22` 技能數寫 20，實測 16（confirmed）**，與同次變更的 `SKILLs/README.md:7`「16 項」自相矛盾。
- **遮罩動作引入 6 條新死鏈（confirmed）**：`%USERPROFILE%` 被放進了 markdown 連結目標位置而非程式碼區間。
- **新 ruff 閘門紅燈上線（confirmed）**：`ruff check .` exit 1 / 27 errors，而 `TEST_INFRA.md` 仍宣稱 Tier 1「0 錯誤、通過率 100%」。

**Verdict**: NEEDS_CHANGES

## High-level view

資安面，工作區的遮罩本身做得徹底：全庫 528 個掃描檔案中 `C:\Users\` 零殘留、`F:\Ming_python` 只剩 `.clinerules:52` 一處（與預期相符）。但這次操作的假設有個缺口——repo 是 public，`docs/presentations/slides_detailed.md` 所在的 commit `341bed8` 已經在 `origin/master` 上，員工編號同樣仍可從 `origin/master` 的兩個檔案直接 grep 出來。刪檔與遮罩只約束未來的 commit，對已推送的歷史沒有作用。

文件歸檔本身執行得乾淨：188 條追蹤 markdown 連結有 178 條解析成功，扣掉 1 條掃描器誤判（`](True)` 是程式碼）與 3 條 vendored 上游文件的既有死鏈，由這次變更引入的死鏈是 6 條，全部集中在 `ANSYS_MCP_DELIVERY_WALKTHROUGH.md`：遮罩把 `file:///C:/Users/REDACTED_UID/...` 換成 `%USERPROFILE%/...` 卻留在 `[...](...)` 的括號裡。同一檔案的另一行改成了反引號程式碼區間——正確的做法與錯誤的做法在同一次提交裡並存。

archive 警示區塊的數字大多可靠：81 個 `src/` py 檔、37 個 `test_*.py`、`requirements.txt` 不存在，三項實測全中。錯的是技能目錄數：`SKILLs/` 有 17 個子目錄，其中 `.obsidian` 不是技能，帶 `SKILL.md` 的恰為 16 個。archive 寫 20，是刪 3 個 stub 前的舊數字再加算錯。

`config.py` 的改碼沒有問題。`REPO_ROOT` 仍解析到 repo 根，`index.py:119-120,127` 掃 `SKILLs/` 與 `steering/reference/` 的兩處用法不受影響，`DOCS_ROOT` 正確落在 `D:\ansys-docs-local`。`load_dotenv` 的疑慮可以放下：`override` 預設為 `False`（已驗簽名），shell 變數優先權確實高於 `.env`，而且 `config.py:16`、`workbench_bridge.py:17`、`connection_doctor.py:29` 早就是同一個模式，這次只是第 4 個呼叫點。

`.gitignore` 沒有誤傷。`git ls-files -i -c --exclude-standard` 回 0，五個白名單全數生效。要留意的是三段新增註解描述的都不是當前狀態：`*.下載` 說「Documentation/ 底下現有 13 個」，但語料已搬走、`Documentation/` 不存在、`*.下載` 實測 0 個；`logs/*` 說「底下數百筆 audit log」，實測只有 `.gitkeep`。規則本身是防禦性的、留著合理，但註解把理由寫在一個已消失的現象上。

ruff 設定的取捨是誠實的——F821 沒有被掃進地毯下，被 ignore 的是 F401（242）、F841（29）與純格式類，理由與實測數字相符。問題在另一頭：這個閘門紅燈上線。27 個 errors 全部來自這次 diff **沒有碰過**的檔案，屬既有缺陷，但 `TEST_INFRA.md` §1.1 與 §3 仍寫著 Tier 1「語法與型別 0 錯誤」「通過率必須為 100%」，文件與現實對不上。

使用者對 F821 的獨立結論我複驗過，方向正確但有兩處要修正。漏了 `_json`（3 處），所以 `src/` 的 F821 是 21 處不是 18 處；而 `Optional` 因為 `from __future__ import annotations` 讓註解惰性化，實測 plain call 正常返回，不構成執行期 NameError。真正嚴重的比描述更嚴重：`optislang_driver.py:93` 的 `{i}` 位於 `f"""` 模板內，會被外層 f-string 插值，`prepare_job()` 每次呼叫都必然 `NameError`（已實測證明）；`_ensure_dirs` 的呼叫點之一是 `_send_command`（L175），那是整個 Workbench file-bridge 的中央派發函式。

<details>
<summary>Issues (13)</summary>

**必須修正**

1. **已推送歷史未清除** — `slides_detailed.md` 位於已在 `origin/master` 的 commit `341bed8`；員工編號 `REDACTED_UID` 仍可從 `origin/master` 的 `ORIGINAL_REQUEST.md:183` 與 `SKILLs/ansys-error-catalog/reference/workbench_act.md:14` 取得。需以 `git filter-repo` 重寫歷史並 force push，或接受洩漏已發生、改為輪替該編號相關的一切關聯資訊。
2. **`docs/archive/README.md:22` 技能數錯誤** — 寫「`SKILLs/` 有 20 個技能目錄」，實測 16（17 個子目錄減去 `.obsidian`）。與 `SKILLs/README.md:7` 的「16 項」矛盾，改為 16。
3. **遮罩引入 6 條死鏈** — `docs/archive/ANSYS_MCP_DELIVERY_WALKTHROUGH.md` L25、L30（2 條）、L36、L46、L77 把 `%USERPROFILE%/...` 放進連結目標。比照同檔 `.agents/victory_auditor_4/audit_report.md` 那行的做法，改為反引號程式碼區間。L77 同時外流一個 antigravity brain session UUID（`217dfbf0-ec55-4217-8d54-b24151b2d816`），一併移除。

**建議修正**

4. **ruff 閘門紅燈上線** — `ruff check .` exit 1 / 27 errors，`TEST_INFRA.md:48` 記載的 `--select E9,F63,F7,F82` 亦 exit 1，但 §1.1/§3 宣稱 Tier 1「0 錯誤、通過率 100%」。先修 27 errors，或在 TEST_INFRA.md 明確記錄 baseline 與豁免期。
5. **`TEST_INFRA.md` 與 `pyproject.toml` 對 Tier 1 的定義不一致** — 文件用 `--select E9,F63,F7,F82`（CLI 會覆蓋 pyproject 的 `select`），config 用 `select = ["E","F","W"]`；文件走 `uvx ruff`，pyproject 走 `dev` extras 的 `ruff`。統一為單一呼叫路徑。
6. **F821 清單漏掉 `_json`** — `workbench_filebridge.py` L355、L361、L362，位於 `check_workbench_connection()`。`src/` 的 F821 實為 21 處（`_as_path` 13 + `_ensure_dirs` 3 + `_json` 3 + `Optional` 1 + `i` 1 = 21）。該函式另有契約問題：宣告回傳 `dict` 卻三條路徑都 `return` 字串，不符專案 `{"ok": ...}` 信封慣例。
7. **`optislang_driver.py:93` 的嚴重度被低估** — 不是「風險」而是必然失敗：`prepare_job()` 已實測拋 `NameError: name 'i' is not defined`。`{i}` 落在 `f"""` 模板的插值位置，應改為 `{{i}}` 或把模板改為非 f-string 的 `.format()`。
8. **`_ensure_dirs` 位於中央派發函式** — `workbench_filebridge.py:175` 在 `_send_command()` 內，該函式是所有 bridge 工具的共同入口，等於整個 file-bridge 子系統無法執行。優先級應高於其餘 F821。
9. **F541 修了 3 個留 2 個** — `contour_helper.py:162-163`、`shock_analysis.py:129`、`test_final_stress_harness.py:135` 已修，但 `SKILLs/{ansys-geometry-modeling,ansys-spaceclaim-modeling}/scripts/create_enclosure_demo.py:166` 仍在。且此 3 處修改超出「補 `[tool.ruff]`」的宣稱意圖，屬夾帶變更。
10. **`.gitignore` 新增註解描述已消失的現象** — `*.下載` 註解稱「Documentation/ 底下現有 13 個」，實測 `Documentation/` 不存在、`*.下載` 為 0；`logs/*` 註解稱「數百筆 audit log」，實測僅 `.gitkeep`。規則保留，註解改寫為防禦性理由。
11. **`.clinerules:52` 未遮罩** — 仍有 `file:///F:/Ming_python/ansys-unified-mcp/SKILLs/`，是全庫唯一殘留（與預期相符），但它是第 4 個追蹤檔，不在「3 個追蹤檔」的宣稱範圍內。
12. **`TEST_INFRA.md` §2.3～§2.5 仍硬編碼 `C:\Python314\python.exe`** — 該檔的 repo 路徑已改用 `%WORKBENCH_MCP_ROOT%`，python 解譯器路徑卻沒有，與意圖 1 的方向不一致。
13. **家目錄全域技能鏡射殘留 3 個已刪 stub** — `$HOME\.gemini\config\skills` 下仍有 `ansys-lsdyna-explicit`、`ansys-mechanical-multiphysics`、`ansys-optislang-optimization`。在 repo 之外、不影響本次正確性，但下次跑 `scripts/setup_skill_junctions.py` 或雙向同步可能把它們帶回來。

</details>

<details>
<summary>Details</summary>

## 資安止血的邊界：工作區 vs 已推送歷史

工作區的遮罩結果乾淨。掃描 528 個檔案（排除 `.venv`、`.git`、`jobs`、`logs`、`workbench_queue`、`node_modules`、`.pytest_cache`、`.ruff_cache`、`Documentation*`）：

```
=== C:\Users\<7 碼> ===        NO_MATCH_CUsers7digit
=== C:\Users\ 任意使用者 ===    none
=== F:\Ming_python ===         .clinerules:52
```

`git grep` 對追蹤檔的結果一致：`C:.Users.[0-9]{7}` exit 1（無匹配），`Ming_python` 僅 `.clinerules:1` 筆。`file:///` 三筆中兩筆是 archive 文件在敘述「曾有 `file:///` 連結」的散文，只有 `.clinerules:52` 是真實連結。

問題在 repo 的可見性假設。remote 是 `https://github.com/ikaros0902/ANSYS-unified-MCP.git`，`git branch -r --contains master` 回 `origin/master`，代表 master 已推送：

```
=== slides_detailed in master? ===
docs/presentations/slides_detailed.md
=== commits touching it ===
341bed8 feat(core,skills): ...

=== 員工編號仍在 origin/master ===
origin/master:ORIGINAL_REQUEST.md:183                                    ... C:\Users\REDACTED_UID\.gemini\config\skills ...
origin/master:SKILLs/ansys-error-catalog/reference/workbench_act.md:14    ... "C:\Users\REDACTED_UID\AppData\Roaming\Ansys\v251\ACT\..." ...
```

26 頁內部提案逐字稿與員工編號目前都能從 GitHub 的 commit 檢視頁直接取得。這次變更把它們從 HEAD 移除，對已存在的 blob 沒有影響。要真正止血只有兩條路：`git filter-repo` 重寫歷史後 force push（會使所有既有 clone 失效，且 GitHub 端可能需要聯繫支援才能回收 unreachable objects），或者認定洩漏已發生、轉為輪替該編號的關聯資訊並接受現狀。無論選哪條，現在的 diff 不足以達成意圖 1 所宣稱的效果。

## 遮罩與連結語法的衝突

遮罩在 `ANSYS_MCP_DELIVERY_WALKTHROUGH.md` 內有兩種處理方式並存。正確的一種把整個連結降級成程式碼區間：

```diff
-  - 獨立驗收審計報告：[`F:\...\audit_report.md`](file:///F:/Ming_python/.../audit_report.md)
+  - 獨立驗收審計報告：`%WORKBENCH_MCP_ROOT%\.agents\victory_auditor_4\audit_report.md`
```

另一種把 `%USERPROFILE%` 留在括號裡，產生一個指向名為 `%USERPROFILE%` 的相對目錄的連結：

```
- **檔案**：[`AGENTS.md`](%USERPROFILE%/.gemini/config/AGENTS.md)
- **檔案**：[`.gitignore`](%USERPROFILE%/.gemini/config/.gitignore) 與 [`mcp_config.template.json`](%USERPROFILE%/.gemini/config/mcp_config.template.json)
```

全庫連結解析結果：

```
ALL TRACKED MARKDOWN -- files=151  links=188  OK=178  MISS=10
  MISS -> SKILLs/ansys-mechanical/reference/act_scripting_foundation.md : L50 : True
  MISS -> docs/archive/ANSYS_MCP_DELIVERY_WALKTHROUGH.md : L25 : %USERPROFILE%/.gemini/config/AGENTS.md
  MISS -> docs/archive/ANSYS_MCP_DELIVERY_WALKTHROUGH.md : L30 : %USERPROFILE%/.gemini/config/.gitignore
  MISS -> docs/archive/ANSYS_MCP_DELIVERY_WALKTHROUGH.md : L30 : %USERPROFILE%/.gemini/config/mcp_config.template.json
  MISS -> docs/archive/ANSYS_MCP_DELIVERY_WALKTHROUGH.md : L36 : %USERPROFILE%/.gemini/config/bootstrap.ps1
  MISS -> docs/archive/ANSYS_MCP_DELIVERY_WALKTHROUGH.md : L46 : %USERPROFILE%/.gemini/config/sync.ps1
  MISS -> docs/archive/ANSYS_MCP_DELIVERY_WALKTHROUGH.md : L77 : %USERPROFILE%/.gemini/antigravity/brain/217dfbf0-.../ansys_mcp_evaluation_and_optimization_plan.md
  MISS -> steering/reference/frames.md : L3 : ../README.md
  MISS -> steering/reference/frames.md : L34 : ../src/frames.ts
  MISS -> steering/reference/frames.md : L40 : ../CONTRIBUTING.md#authoring-a-new-frame
```

`act_scripting_foundation.md:L50` 是掃描器誤判——實際內容是 `Model.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)`，C# 泛型語法碰巧符合 `](...)`。`steering/reference/frames.md` 的 3 條經 `git diff master --name-only` 確認本次未觸碰，是 vendored 上游文件帶進來的既有死鏈，超出本次 scope。

指定的 7 個檔案 + `contexts/*.md` 單獨解析結果為 **71 條連結、70 OK、1 MISS**，唯一的 MISS 是 `AGENTS.md:30` 的 `~/.gemini/config/skills`——刻意指向使用者家目錄，`Test-Path "$HOME\.gemini\config\skills"` 回 `True`，不是死鏈。

## archive 警示數字的實測核對

四項中三項正確：

```
=== src py only ===       81      → archive 寫 81  ✓
=== test_*.py ===         37      → archive 寫 37  ✓
=== requirements.txt ===  False   → archive 稱不存在  ✓
=== SKILLs subdirs ===    17      （含非技能的 `.obsidian`）
=== dirs with SKILL.md === 16     → archive 寫 20  ✗
```

`docs/archive/README.md:22` 原文：「早期自動化藍圖；稱「10 項技能」（現 `SKILLs/` 有 20 個技能目錄）」。20 既不等於刪 stub 前的 19（16 + 3），也不等於現在的 16，來源不明。同一次變更的 `SKILLs/README.md:7` 已正確更新為「(16 項)」，兩份新寫的文件互相矛盾。

六個 archive 檔案與 `README.md` 的警示區塊皆已就位。

`docs/archive/ORIGINAL_REQUEST.md` L201、L212 仍提到 `docs/presentations/slides_detailed.md` 成功歸檔，而該目錄已刪。兩處是反引號而非連結，且檔案已標 ARCHIVED、header 明示「數據與連結均已過期」，可接受；若要更嚴謹可在 archive README 對該檔補一句「其驗收條目指向已刪除的交付物」。

## `config.py` 路徑解耦

執行期實測：

```
REPO_ROOT  = D:\Ikaros\ANSYS-unified-MCP
DOCS_ROOT  = D:\ansys-docs-local
SOURCE_DIR = D:\ansys-docs-local\Documentation_md      | exists: True
CLEAN_DIR  = D:\ansys-docs-local\Documentation_clean   | exists: True
INDEX_PATH = D:\ansys-docs-local\Documentation_clean\docs_index.sqlite | exists: True
SKILLs     = True
steering/reference = True
```

`REPO_ROOT = parents[3]` 從 `src/ansys_unified_mcp/docs/config.py` 往上四層落在 repo 根，正確。`index.py` 對 `cfg.REPO_ROOT` 的兩處用法（L119 `SKILLs`、L120 `steering/reference`，加上 L127 的 `relative_to`）都仰賴這個語意，不受 `DOCS_ROOT` 外移影響。`SOURCE_DIR` / `CLEAN_DIR` 改跟 `DOCS_ROOT`，`index.py:66,74,92,99` 隨之指向外部語料。repo 內無 `Documentation*` 殘留。

`load_dotenv` 的副作用疑慮可以排除。簽名確認 `override: bool = False`，實測 shell 變數優先：

```
--- A) plain import ---
env vars injected by importing docs.config: ['ANSYS_DOCS_ROOT', 'ANSYS_ROOT', 'ANSYS_VERSION',
  'WORKBENCH_MCP_HOST', 'WORKBENCH_MCP_PORT', 'WORKBENCH_MCP_QUEUE_ROOT', 'WORKBENCH_MCP_ROOT']
DOCS_ROOT = D:\ansys-docs-local
--- B) shell var set ---
DOCS_ROOT = X:\override_probe        ← shell 勝出，.env 未覆蓋
```

import 這個模組確實會注入 7 個環境變數（不只 `ANSYS_DOCS_ROOT`），比註解描述的範圍廣。但這不是新行為——`src/ansys_unified_mcp/config.py:16`、`bridges/workbench_bridge.py:17`、`tools/connection_doctor.py:29` 早就在 import 時做同樣的事，這次只是第 4 個呼叫點，且 `override=False` 保證不改動已存在的值。屬既有專案慣例，可接受。

一個操作面的提醒：`load_dotenv` 無條件載入 `.env`，而 `.env` 已設 `ANSYS_DOCS_ROOT`，所以想回到 repo-local fallback 不能只 unset shell 變數，必須編輯 `.env`。

## `.gitignore` 白名單與誤傷

決定性檢查——列出「被追蹤且被忽略」的檔案：

```
=== AUTHORITATIVE: tracked(cached) files that are ignored ===
count = 0
```

353 個追蹤檔無一變成被忽略。五個白名單逐一實測：

```
OK(not ignored)  samples
OK(not ignored)  jobs/.gitkeep
OK(not ignored)  logs/.gitkeep
OK(not ignored)  src/ansys_unified_mcp/scripts/ansys_workbench_bridge.wbjn
OK(not ignored)  workbench_queue/.gitkeep
```

`logs/*` + `!logs/.gitkeep` 的寫法與註解對「不能寫 `logs/`」的解釋都無誤。

`Documentation*/` 的誤傷面實測極小。全庫唯一名稱符合的目錄是 `.venv\Lib\site-packages\ansys\dpf\core\documentation`，而 `.venv` 本身已被忽略。`core.ignorecase = true` 表示這個 pattern 在本機會不分大小寫匹配，所以未來任何位置出現 `documentation/` 都會被靜默忽略；風險存在但很低，值得在註解裡加一句提醒而非改 pattern。

## ruff 閘門：取捨誠實，但紅燈上線

`ignore` 清單的理由與實測數字相符，且關鍵決策是對的——**F821 沒有被 ignore**，真問題沒有被掃進地毯下。被排除的是 F401（242）、F841（29）與 E501/E402/E702/W29x 純格式類，都屬存量債務或格式範疇，各自附了筆數與清理方式。`SKILLs/**` 等目錄的 F821 per-file-ignore 有充分理由（ACT/IronPython 的 `ExtAPI`、`DataModel` 等為求解器注入的全域名）。

問題是閘門本身的狀態：

```
=== plain 'ruff check .' (the new gate) ===
Found 27 errors.
EXITCODE=1

=== documented Tier-1 command from TEST_INFRA.md L48 ===
EXITCODE=1

24  F821  [ ] undefined-name
 2  F541  [*] f-string-missing-placeholders
 1  F811  [*] redefined-while-unused
```

`TEST_INFRA.md` §1.1 定義 Tier 1 為「語法與型別 0 錯誤」，§3 要求「Tier 1 ~ Tier 3 測試通過率必須為 100%」。兩個指令都 exit 1。意圖 5 說要「讓宣稱成真」——設定確實補上了，但宣稱仍然不成立，而文件沒有同步記錄這個事實。

還有兩處定義漂移：文件的 `--select E9,F63,F7,F82` 在 CLI 會覆蓋 pyproject 的 `select = ["E","F","W"]`，兩者對 Tier 1 的範圍定義不同；文件用 `uvx ruff`，pyproject 把 `ruff` 加進 `dev` extras，兩條安裝路徑並存。

## F821 的獨立複驗：三處修正

先確認這些檔案本次未被觸碰——`git diff master --name-only -- src/.../workbench_filebridge.py src/.../optislang_driver.py` 回空，所以 27 個 errors 全是既有缺陷，不是這次引入的。以下屬既有問題的性質釐清，不是對本次 diff 的指控。

定義檢索確認 `_as_path`、`_ensure_dirs`、`_json` 全庫只有呼叫點、無定義，`workbench_filebridge.py` 的 import 只有 `from typing import Any`（L23），沒有 `Optional`。執行期驗證：

```
PROVEN BUG optislang prepare_job: NameError -> name 'i' is not defined
hasattr(_as_path) = False
hasattr(_ensure_dirs) = False
hasattr(_json) = False
get_type_hints RAISES: NameError name 'Optional' is not defined
_get_active_project_path() -> None
```

**修正一：漏了 `_json`。** L355、L361、L362，全在 `check_workbench_connection()` 內。`src/` 的 F821 是 21 處而非 18 處。這三處還連帶暴露一個契約問題：該函式宣告回傳 `dict`，但三條路徑都 `return` 字串，與專案的 `{"ok": ...}` 信封慣例不符。

**修正二：`Optional` 不構成執行期 NameError。** L128 的 `-> Optional[Path]` 是註解，而檔案 L14 有 `from __future__ import annotations`，註解被延遲為字串。實測 `_get_active_project_path()` 正常回傳 `None`，只有 `typing.get_type_hints()` 會拋。這一處是潛在問題而非執行期風險。

**修正三：`optislang_driver.py:93` 是必然失敗，不是風險。** L79 的 `py_content = f"""` 是三引號 **f-string**，所以模板內每個 `{...}` 都會被外層插值：

```python
py_content = f"""...
    for i in range(1, {num_samples} + 1):
        f.write(f"DESIGN_EVALUATION [{i}/{num_samples}] Finished successfully.\\n")
"""
```

`{num_samples}` 是刻意的插值，`{i}` 則被當成外層作用域的變數——而外層沒有 `i`。`OptislangDriver.prepare_job()` 每次呼叫都拋 `NameError`（上方已實測）。順帶一提 L91 內層 `f"..."` 的 `{sampling_method}` / `{num_samples}` 也被外層吃掉，生成腳本會拿到字面值而非插值。

**嚴重度排序建議：** `_ensure_dirs` 應排第一。L175 的呼叫點在 `_send_command()` 內，而 `__main__.py:36` 會 import 此模組註冊工具：

```
L175   fn=_send_command              :: _ensure_dirs      ← 中央派發，所有 bridge 工具共用
L293   fn=start_workbench_bridge     :: _ensure_dirs
L355-362 fn=check_workbench_connection :: _json
L817-1183 fn=run_workbench_journal / create_workbench_analysis_system /
          create_steady_state_thermal_system / run_mapdl_input /
          run_fluent_journal / run_cfx_solver / create_and_run_thermal_bar_demo :: _as_path
```

`_send_command` 是 file-IPC bridge 的唯一出口，等於 `execute_workbench_script`、`check_workbench_connection`、`get_project_info`、`open_project`、`save_project`、`update_project`、`execute_mechanical_script_live`、`execute_spaceclaim_script_live` 全數無法執行。

## 夾帶變更：F541 修了 3 個留 2 個

意圖 5 只說「補 `[tool.ruff]`」，但 diff 另外改了三個檔案移除多餘的 `f` 前綴：

```diff
-    draw.text(..., f"Solver: ANSYS Mechanical / Unified MCP 2.0", ...)   # contour_helper.py:162
+    draw.text(..., "Solver: ANSYS Mechanical / Unified MCP 2.0", ...)
-                f.write(f" FORCE CONVERGENCE VALUE = 1.25E-04 ...\n")    # shock_analysis.py:129
+                f.write(" FORCE CONVERGENCE VALUE = 1.25E-04 ...\n")
-        print(f"[PASS] 12 個業務工具在無成功關鍵字雜訊下 ...")             # test_final_stress_harness.py:135
+        print("[PASS] 12 個業務工具在無成功關鍵字雜訊下 ...")
```

改動本身無害且正確，但 `SKILLs/{ansys-geometry-modeling,ansys-spaceclaim-modeling}/scripts/create_enclosure_demo.py:166` 的同類問題留著沒動（那兩個目錄的 per-file-ignore 只豁免 F821，不含 F541）。同一類問題在同一次提交裡處理到一半，且未列入宣稱的意圖範圍。

## rename 保留：14 筆而非 15 筆

```
=== rename count === 14
```

14 筆全部被 git 識別為 rename，相似度 54%～100%。兩個低相似度的案例已核對內容：`ANSYS_MCP_DELIVERY_WALKTHROUGH.md`（54%）與 `ANSYS_MCP_SESSION_OPTIMIZATION_PLAN.md`（73%）的差異來自把每個 `file:///F:/Ming_python/...` 連結改寫為相對路徑，加上 ARCHIVED 警示區塊，沒有內容遺失。

第 15 個項目是 `docs/diagrams/act_workflow_comparison.html`（394 行，顯示為 create）。`git log --all --diff-filter=A -- "*act_workflow_comparison*"` 回空，`git ls-tree -r master` 也沒有——它從未被追蹤，所以沒有歷史可保留。這不是遺漏，只是「15 筆 rename」的說法要修正為「14 筆 rename + 1 個原本未追蹤的新檔」。

## 冗餘刪除與遺漏項掃描

`build_rag_knowledge.py`、`query_rag.py` 刪除後全庫零引用（`git grep` 無匹配），刪除安全。`presentations` 只剩 archive 文件內的兩處反引號敘述。

根目錄收斂達標——只剩 `AGENTS.md`、`ARCHITECTURE.md`、`README.md` 三個 md，零個 html。`slide_dump.txt`、`act_workflow_comparison.html`（根）、`docs/presentations/` 皆已不存在於磁碟。

三個 stub 技能目錄在 repo 內已完全移除，`.kiro/skills`、`.cline/skills` 無殘留，`tests/unit/test_skills_integrity.py` 通過。但家目錄的全域技能鏡射仍有舊 stub：

```
MIRROR_STALE: ansys-lsdyna-explicit
MIRROR_STALE: ansys-mechanical-multiphysics
MIRROR_STALE: ansys-optislang-optimization
```

位於 `$HOME\.gemini\config\skills`，在 repo 之外，不影響本次變更的正確性，但下次跑 `scripts/setup_skill_junctions.py` 或雙向同步時可能把它們帶回來。

`scripts/audit_architecture_compliance.py:6` 的 docstring 提到 `PROJECT.md` 與 `ORIGINAL_REQUEST.md`（兩者已移入 `docs/archive/`），但該腳本只讀 `PROJECT_BASE = .../SKILLs`，從未開啟這兩個檔案，不構成失效引用。`.clinerules` 除了 L52 的 `file:///F:/Ming_python/` 外，沒有指向任何被移動檔案的失效路徑。

`TEST_INFRA.md` §2.3～§2.5 仍有硬編碼的 `C:\Python314\python.exe`。不是資安問題，但與意圖 1「把失效絕對路徑改為變數」的方向不一致，該檔的 repo 路徑已改用 `%WORKBENCH_MCP_ROOT%`，python 路徑卻沒有。

## 回歸驗證

```
449 passed, 6 xfailed in 35.90s
```

全套測試綠燈。移入 `docs/diagrams/` 的四個 HTML 檔經掃描確認沒有任何相對 `href`/`src`（自包含），移動後不會斷鏈。

</details>

<details>
<summary>檔案地圖</summary>

| 檔案 | 變更 |
| --- | --- |
| `.gitignore` | 新增 `.pytest_cache/`、`.ruff_cache/`、`logs/*` + negation、`Documentation*/` 通配、`*.下載`/`*.crdownload`/`*.part` |
| `.env.example` | 新增 `ANSYS_DOCS_ROOT` 說明區塊 |
| `pyproject.toml` | 新增 `[tool.ruff]` / `[tool.ruff.lint]` / per-file-ignores；`dev` extras 加 `ruff` |
| `src/ansys_unified_mcp/docs/config.py` | 新增 `load_dotenv` + `ANSYS_DOCS_ROOT` → `DOCS_ROOT`，`SOURCE_DIR`/`CLEAN_DIR` 改跟 `DOCS_ROOT` |
| `AGENTS.md` / `README.md` / `docs/README.md` / `docs/index.md` | 連結改指新路徑；`docs/index.md` 重寫為六目錄索引 |
| `SKILLs/README.md` | `file:///F:/...` → 相對路徑；技能數 10 → 16；補 stub 移除說明 |
| `SKILLs/ansys-error-catalog/reference/workbench_act.md` | 員工編號路徑遮罩為 `%USERPROFILE%` |
| `docs/archive/README.md` | 新增（歸檔清單與落差說明；技能數有誤） |
| 14 筆 `git mv` | 根目錄與 `docs/` 平鋪檔案 → `architecture`/`planning`/`deployment`/`testing`/`diagrams`/`archive` |
| `docs/diagrams/act_workflow_comparison.html` | 新增（原為未追蹤檔） |
| 已刪除 | `docs/presentations/slides_detailed.md`、`ansys_mcp_architecture.html`（根）、`build_rag_knowledge.py`、`query_rag.py`、3 個 stub `SKILL.md` |
| `contour_helper.py` / `shock_analysis.py` / `test_final_stress_harness.py` | F541 修正（夾帶變更） |

完整 diff：`git diff master` on `chore/restructure`（36 files, +766 / -1457）

</details>
