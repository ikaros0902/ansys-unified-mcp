# 審查紀錄與工作交接歸檔規範

本目錄是審查結論、門禁會審裁決與工作交接記錄的唯一版控歸檔位置。

## 一、為何不放 `.agents/`

`.agents/` 被 `.git/info/exclude` 本機排除，寫在其中的審查紀錄僅存本機、不入版控，一旦 session 清理或換機即遺失。先前的 Teamwork M2 門禁會審紀錄（原存 `.agents/teamwork/`）即因此無法復原。

因此，凡需跨 session、跨機器留存的審查結論，一律寫入本目錄 `docs/reviews/`。

## 二、歸檔對象

| 類型 | 說明 |
| --- | --- |
| 門禁會審裁決 | 多代理獨立審查（reviewer / challenger / auditor）的最終裁決與客觀證據摘要 |
| 工作交接記錄 | 跨日 / 跨 session 的已完成事項、未完成事項與下一步 |
| 方案對比評估 | 重大架構決策的方案比較與拍板理由 |
| 待驗證任務卡 | 需實機或外部環境才能驗證的任務（如 PyWorkbench 連線） |

## 三、命名規則

```
YYYY-MM-DD-<kebab-case-主題>.md
```

例：`2026-10-06-directory-consolidation-handover.md`、`2026-10-05-workspace-session-isolation-options.md`。

## 四、審查裁決必備欄位

門禁會審或獨立審查的結論檔，須包含客觀可查證的證據綁定（對應 `10-loop-engineering.md` 第六節）：

- **宣稱（Claims）**：1~5 條具體完成宣稱。
- **證據（Evidence）**：終端 exit code、pytest 統計（passed/failed）、`git diff` 行、驗證腳本輸出。
- **判決（Verdict）**：每條宣稱標記 `supports` / `contradicts` / `says_nothing`。
- **結論**：PASS / NEEDS_CHANGES / ESCALATE。

## 五、現存紀錄索引

- `2026-10-05-session-handover.md`：10-05 工作交接（含任務 7 收斂）
- `2026-10-05-workspace-session-isolation-options.md`：多工作區隔離方案對比
- `2026-10-05-engineering-lessons.md`：工程經驗沉澱
- `2026-10-06-directory-consolidation-handover.md`：目錄收斂交接
- `2026-10-02-phase2-3-feasibility-assessment.md`：Phase 2/3 可行性評估
- `2026-10-02-docs-structure-audit.md`：文檔結構稽核
- `2026-09-24-153530-chore-restructure.md`：早期重構紀錄
- `2026-10-07-pyworkbench-verification-done.md`：PyWorkbench 實機驗證任務卡（✅ 已驗證）
- `2026-10-07-backlog-decisions.md`：Backlog 技術決策記錄（fallback bridge 移除、OS 級隔離方案 C）
