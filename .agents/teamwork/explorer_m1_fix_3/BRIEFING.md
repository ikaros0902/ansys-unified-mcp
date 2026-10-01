# BRIEFING — 2026-10-01T14:21:20Z

## Mission
探查與制定 facade.py 併發競爭、斷線重連與快取盲區修復策略，提供可供實作者無痛落地的具體建議與分析報告。

## 🔒 My Identity
- Archetype: explorer
- Roles: investigator, synthesizer
- Working directory: F:\Ming_python\ansys-unified-mcp\.agents\teamwork\explorer_m1_fix_3
- Original parent: b64f9ba5-0d28-4ac0-a95d-862e7b398eaf
- Milestone: M1 Concurrency Reconnect & Cache Fix Strategy

## 🔒 Key Constraints
- Read-only investigation — do NOT implement / modify source code directly
- 嚴格全繁體中文輸出（除代碼、路徑、專有名詞）
- 確保修復方案不破壞現有測試（7個Controller單元測試、5個別名測試、42個壓力測試）

## Current Parent
- Conversation ID: b64f9ba5-0d28-4ac0-a95d-862e7b398eaf
- Updated: 2026-10-01T14:18:30Z

## Investigation State
- **Explored paths**:
  - `tests/adversarial/test_m1_concurrency_reconnect_challenge.py`
  - `src/ansys_unified_mcp/products/mechanical/facade.py`
  - `src/ansys_unified_mcp/core/sessions.py`
  - `tests/test_mechanical_controller.py`
  - `tests/adversarial/test_m1_alias_challenge.py`
  - `tests/adversarial/test_m1_envelope_stress_challenge.py`
  - `tests/adversarial/test_final_stress_harness.py`
  - `challenger_m1_2/handoff.md`
- **Key findings**:
  1. `run_script` 併發碰撞：因共用 `os.getpid()`，改用 `uuid.uuid4().hex` 具備 100% 隔離性且無鎖。
  2. `connect()` 盲目復用死 Session：缺乏存活探針，應先 `_probe_session(existing)`，死亡則 `drop` 並重建連線。
  3. `run_script` 執行中斷線：外層 exception 區塊未清除 `_PROBE_CACHE` 與 `registry.drop`。
  4. **重大關鍵洞察**：`test_m1_concurrency_reconnect_challenge.py` 的第 4 個測試為修復前的漏洞證明 PoC，內含 `assert cached_session is not None`。若修復了死 Session 驅逐，該 PoC 測試反而會報錯，因此實作修復時該測試必須同步轉型為驗證死 Session 驅逐與假陽性消除之綠燈防護測試。
  5. 現有 7 個 Controller 單元測試、5 個別名測試、42 個壓力測試均已實測驗證，修復方案 100% 向後相容，不會造成任何回歸損壞。
- **Unexplored areas**:
  - 無，所有相關模組、測試與依賴皆已全數探查與實測完畢。

## Key Decisions Made
- 採納 `uuid.uuid4().hex` 作為唯一臨時檔案標識符。
- 在 `connect()` 中採用「探針驗證 -> 失敗即驅逐 -> 建立新連線」閉環。
- 在 `run_script` 外層 exception 區塊中同時執行快取清理 (`_PROBE_CACHE.pop`) 與註冊表驅逐 (`registry.drop`)。
- 在報告中明確揭露對抗測試的脆弱斷言問題，指導實作者同步調整測試為綠燈驗證。

## Artifact Index
- `DISPATCH.md` — 任務分派紀錄
- `BRIEFING.md` — 態勢感知持久檔案
- `progress.md` — 執行心跳進度
- `handoff.md` — 完整調研與修復策略報告
