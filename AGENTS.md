# 全域與專案 Agent 指導核心規範 (AGENTS.md)

本專案遵循精簡路由器（Router）與漸進式揭露架構，提供 AI Agent 開發本專案時的唯一最小規則入口：

---

## 1. 核心規範導引 (Steering & Rules)

- **最高專案指導原則**：參閱 [`.clinerules`](./.clinerules)（規範繁中原生、雙軌註解、自主執行邊界與客觀驗收標準）。
- **詳細行為與安全模組**：
  - 行為準則與閉環推進：[`steering/00-behavior.md`](./steering/00-behavior.md)
  - 雙軌權限與安全邊界：[`steering/01-safety.md`](./steering/01-safety.md)
  - 自動化閉環工程：[`steering/10-loop-engineering.md`](./steering/10-loop-engineering.md)

---

## 2. 專案架構與技術脈絡 (按需載入)

日常開發無需一次性通讀全專案長篇文檔，依任務性質查閱專責文件：
- **專案心智模型與分層**：[`contexts/context.md`](./contexts/context.md)
- **系統架構與工具命名信封慣例**：[`ARCHITECTURE.md`](./ARCHITECTURE.md)
- **PyAnsys 與 ANSYS 映射路線**：[`contexts/pyansys-mapping-and-roadmap.md`](./contexts/pyansys-mapping-and-roadmap.md)
- **測試基礎設施與執行指令**：[`TEST_INFRA.md`](./TEST_INFRA.md)

---

## 3. 領域技能庫 (Domain Skills)

- **專案 CAE 技能目錄**：[`SKILLs/`](./SKILLs/)（依工況動態載入對應主控手冊，細節推入 `reference/`）。
- **全域技能庫**：[`~/.gemini/config/skills/`](~/.gemini/config/skills)（長尾專業知識透過向量檢索按需調用）。
