# ANTIGRAVITY.md

開工先讀 [`AGENTS.md`](./AGENTS.md) 與 README，透過 `/skills` 選擇最小需要的技能。

## 核心工作準則與安全防線
1. **語言與環境**：原生繁體中文，Windows 指令優先使用 PowerShell。
2. **外部服務保護**：所有外部服務（API、CLI、Git、雲端）一律先做唯讀或 dry-run 診斷；登入、安裝、寫入、公開與刪除前先取得使用者確認。
3. **零機密外洩**：嚴禁提交 API Key、Token、Cookie、憑證、個人/學生個資或私有路徑。
4. **防循環安全守門**：互動登入最多一次，驗證失敗立即中斷並分類回報，禁止反覆盲目重試與大量安裝。
5. **詳細規範引導**：核心規則請見 [`AGENTS.md`](./AGENTS.md) 與 [`.clinerules`](./.clinerules)。
