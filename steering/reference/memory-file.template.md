# Memory_File 定義樣板

> 用途：定義一個 Loop 的持久記憶格式，記錄跨輪執行的進行中事項、已完成事項與待分類事項，供每輪執行後更新任務狀態並在下一輪載入為上下文。
> 建議存放位置：專案根目錄或 Loop 設計文件旁（例如 `loops/<loop-name>/AGENTS.md`、`TODO.md`、`PROGRESS.md`）。
> 填寫說明：以純 Markdown 撰寫，不要寫入任何特定工具的指令、API 語法或設定欄位。將 `<...>` 佔位符替換為實際內容即可。
> 更新規則：每輪執行後更新任務狀態；進行中事項每筆須記錄負責 Sub_Agent_Role、所屬 Isolated_Workspace（若有，否則填 N/A）、Verification_Condition 達成狀態。

本樣板含三份 Memory_File 骨架，可依需要單獨或搭配使用：

- `AGENTS.md`：以三區塊（進行中事項 / 已完成事項 / 待分類事項）記錄總體記憶。
- `TODO.md`：以任務清單語法（`- [ ]` / `- [x]`）追蹤待辦與完成狀態。
- `PROGRESS.md`：以 ISO 8601 時間戳逐筆記錄進度，由新到舊逆序排列。

---

## AGENTS.md 骨架

```markdown
# 記憶檔（AGENTS.md）

## 進行中事項
- [ ] <事項描述> | 負責角色: <Sub_Agent_Role> | Workspace: <Isolated_Workspace 或 N/A> | Verification: <Verification_Condition 達成狀態>

## 已完成事項
- [x] <已完成的事項描述>

## 待分類事項
- <尚未歸類的想法、待釐清的問題或未排程的工作>
```

---

## TODO.md 骨架

> 使用任務清單語法：未完成以 `- [ ]`、已完成以 `- [x]` 標記。

```markdown
# 待辦清單（TODO.md）

## 待辦
- [ ] <尚未開始的任務>

## 進行中
- [ ] <進行中的任務> | 負責角色: <Sub_Agent_Role> | Workspace: <Isolated_Workspace 或 N/A> | Verification: <Verification_Condition 達成狀態>

## 已完成
- [x] <已完成的任務>
```

---

## PROGRESS.md 骨架

> 每筆紀錄以 ISO 8601 時間戳（例如 `2026-04-04T09:30:00Z`）開頭；整份由新到舊逆序排列，最新的一筆置於最上方。

```markdown
# 進度紀錄（PROGRESS.md）

## 進度紀錄
- <YYYY-MM-DDThh:mm:ssZ> | <本輪執行的變更或結果摘要>
- <較早的時間戳> | <較早一輪的變更或結果摘要>
```

---

## 填寫檢查

- [ ] 三區塊（進行中事項 / 已完成事項 / 待分類事項）皆已建立。
- [ ] 每筆進行中事項皆已記錄負責 Sub_Agent_Role、所屬 Isolated_Workspace（若有，否則為 N/A）與 Verification_Condition 達成狀態。
- [ ] `TODO.md` 的任務皆以 `- [ ]` 或 `- [x]` 標記其完成狀態。
- [ ] `PROGRESS.md` 每筆以 ISO 8601 時間戳開頭，且整份由新到舊逆序排列。
- [ ] 已於本輪執行後更新任務狀態。
- [ ] 內容以純 Markdown 撰寫，未寫入任何工具專屬的指令、API 語法或設定。
