# Loop Engineering 實作指南

針對想把框架落地到實際專案的團隊。

---

## 一、快速選型

### 我的工作性質是？

| 場景 | 是否適合 Loop | 理由 |
|------|------------|------|
| 日常 1-2 次的臨時工作 | ❌ | 一次性，無重複執行價值 |
| 週期性、每天/每週都跑 | ✅ | 定時觸發 Loop 最佳用途 |
| 程式碼推送後自動檢查 | ✅ | 事件觸發 Loop |
| PR 審查、自動化測試 | ✅ | 高頻、需製造/檢查分離 |
| 需要人工介入的複雜決策 | ⚠️ | 可用 Loop，但需保留審查點 |
| 完全自主決策、無人干預 | ❌ | 違反「驗證責任歸屬於人」原則 |

### 我有多少時間？

| 投入 | 預期產出 | 建議層級 |
|------|---------|---------|
| < 1 小時 | 快速試驗現有 Loop | 使用 Scaffolder + templates 直接填寫 |
| 1–4 小時 | 設計一個生產就緒 Loop | 走完六大組件 + 設計原則清單 |
| 4–8 小時 | 多個 Loop 體系 + 反模式回檢 | 建完後定期用反模式清單體檢 |
| 8+ 小時 | 客製工具 / 擴展框架 | 讀 design.md，修改 Validator / Adapter |

---

## 二、五分鐘快速開始

### Step 0：檢查環境
```powershell
# Windows PowerShell 5.1+
$PSVersionTable.PSVersion

# Node.js 14+ (若需編譯 TypeScript 版本)
node --version
npm --version
```

### Step 1：Scaffolder 一鍵生成
```powershell
cd "loop-engineering-framework"
.\scaffold\Invoke-LoopScaffold.ps1 -Path "C:\your\project"
```

產生物：
- `loop.yaml` - Loop 定義（填空範本）
- `AGENTS.md` / `TODO.md` / `PROGRESS.md` - 三個 Memory 檔
- `.kiro/skills/sample.skill.md` - 技能文件範本
- `.kiro/agents/sub-agent-role.md` - 四個預設角色

### Step 2：填寫 loop.yaml
```yaml
# 模板中已有註解，按指示填空
trigger:
  type: "schedule"        # 定時或事件
  cron: "0 9 * * 1"       # 若為 schedule，用五欄位 cron
discover: "..."           # 發現階段描述
classify: "..."           # 分類階段
assign: [...]             # 分配角色與工作
verify:
  conditions: [...]       # 客觀完成條件
record: "..."             # 記錄階段（至少一個 Memory_File）
budget:
  max_runs_per_day: 10    # 成本上限
```

### Step 3：向 Agent 傳達規則
```
# 複製 AGENT_STEERING_RULES.md 到 IDE config
# Kiro: .kiro/steering/loop-engineering.md
# Cursor: .cursor/rules/loop-engineering.mdc
```

### Step 4：驗證 loop.yaml
```powershell
# (若使用 TypeScript 版本)
npm run validate -- path/to/loop.yaml
# 或在 Kiro 內置驗證 (見下一段)
```

---

## 三、用 Kiro Spec 工作流

### 與 Spec 結合
```yaml
---
title: "設計 PR 檢查 Loop"
requirements: requirements.md
design: design.md
tasks: tasks.md
steering: loop-engineering    # 自動載入 Agent 規則
---
```

### Spec 中的三部分
```markdown
## Requirements
描述六大組件需求

## Design
fill: templates/design-principles-checklist.template.md

## Tasks（Kiro 自動執行）
### Task 1：填寫 loop.yaml
...
### Task 2：驗證與產生
...
### Task 3：記憶初始化
...
```

### Kiro 內建驗證 Hook
```json
{
  "name": "Validate Loop Definition",
  "version": "1.0.0",
  "when": { "type": "fileEdited", "patterns": ["loop.yaml"] },
  "then": {
    "type": "runCommand",
    "command": "npm run validate -- ${file.path}"
  }
}
```

---

## 四、常見場景範例

### 範例 1：每日程式碼檢查 Loop
```yaml
trigger:
  type: schedule
  cron: "0 8 * * 1-5"           # 每個工作日早上8點

discover: |
  掃描昨天合併回主線的所有 PR
  蒐集其中涉及測試變更的清單

classify: |
  依測試類型分為 unit / integration / e2e
  依風險等級分為 critical / normal / trivial

assign:
  - role: explorer
    work: "列舉所有需要複檢的測試"
  - role: tester
    work: "執行複檢測試，確保覆蓋率 ≥ 85%"
  - role: reviewer
    work: "驗證測試邏輯是否完善、有無遺漏邊界"

verify:
  conditions:
    - "所指定測試全數通過"
    - "新增測試覆蓋率 ≥ 85%"
    - "Reviewer 核准"

record: |
  更新 PROGRESS.md 記錄昨日成果
  未通過項目進入 TODO.md 待處理

budget:
  max_runs_per_day: 1
```

### 範例 2：事件觸發的 PR 自動檢查
```yaml
trigger:
  type: event
  event_source: "GitHub"
  event_type: "pull_request.opened"

discover: "讀取 PR diff，識別涉及的模組"

classify: "按改動範圍分為 core / feature / infra"

assign:
  - role: implementer
    work: "執行自動化測試與 lint"
  - role: reviewer
    work: "比對完成條件，回覆檢查結果"

verify:
  conditions:
    - "所有測試通過"
    - "靜態檢查無錯誤"
    - "Reviewer 核准"

record: "寫入 GitHub PR 評論"

budget:
  max_runs_per_day: 100  # 事件觸發無日上限，此為預警門檻
```

---

## 五、進階：客製 Adapter

### Adapter 檔結構
```yaml
# adapters/my-custom-tool.yaml
target_tool: "my_custom_tool"
verified_version: "1.0.0"

mappings:
  trigger:   { primitive: "MyTool.Schedule" }
  discover:  { primitive: "MyTool.Explorer" }
  classify:  { primitive: "MyTool.Classifier" }
  assign:    { primitive: "MyTool.SubAgent" }
  verify:    { primitive: "MyTool.Verify" }
  record:    { primitive: null, gap: { field: "record", fallback: "自訂記錄方式" } }
```

### 新增 Adapter 步驟
1. 複製 `adapters/kiro.yaml` 為 `adapters/my-tool.yaml`
2. 替換 `target_tool` 與 `verified_version`
3. 修改各階段對應的原生原語名稱
4. 執行 Setup 產生器：`npm run generate -- loop.yaml --tool my_custom_tool`

---

## 六、代理角色預設配置

### 四個預設角色

#### Explorer（唯讀製造者）
職責：探索、蒐集情境、回報發現  
存取：唯讀  
模型層級：輕量至主力  
輸出：觀察清單、問題單、情境描述

#### Implementer（可寫製造者）
職責：撰寫或修改程式碼  
存取：可寫  
模型層級：主力  
輸出：程式碼變更、提交

#### Tester（可寫製造者）
職責：撰寫或執行測試  
存取：可寫  
模型層級：輕量至主力  
輸出：測試程式碼、測試結果報告

#### Reviewer（唯讀檢查者）
職責：檢查、核准  
存取：唯讀  
模型層級：強推理  
輸出：核准 / 退回判斷、審查意見

### 客製角色
若預設四個角色不足，可在 `.kiro/agents/sub-agent-role.md` 新增，但遵循原則：
- 製造者與檢查者分離
- 製造者可寫、檢查者唯讀
- 角色數不超過 4 個（超過易過度複雜，見反模式 A）

---

## 七、Memory_File 三檔說明

### AGENTS.md - 任務進度
```markdown
## 進行中事項
- [ ] 實作登入功能 | 角色: implementer | 驗證: 部分達成

## 已完成事項
- [x] 設計登入 UI

## 待分類事項
- 密碼重設功能建議
```

### TODO.md - 待辦清單
```markdown
## 待辦
- [ ] 編寫測試
- [ ] 程式碼審查

## 進行中
- [x] 實作

## 已完成
- [x] 需求分析
```

### PROGRESS.md - 時間序列日誌
```markdown
## 2025-01-15T09:00Z
- Explorer: 掃描 PR #234，發現 3 個邏輯疑點
- Tester: 執行新增測試，86% 通過

## 2025-01-15T08:30Z
- Loop trigger: 自動啟動

...（按時間遞減排列）
```

---

## 八、Skill_Document 漸進式載入

### Skill 何時該寫？
- 代理需要知道專案特定的慣例
- 同一知識會被多個 Loop 複用
- 知識體量超過單個 Prompt 上下文

### Skill 結構
```markdown
---
name: "React Component 撰寫慣例"
description: "本專案 React 元件的設計與測試標準"
---

## 適用場景
Implementer 或 Tester 涉及 React 組件開發時

## 專案慣例
- 函式組件優於 Class 組件
- 必須用 TypeScript
- Props 使用介面定義
- useCallback 包所有事件處理器

## 常見陷阱
- 直接修改 state（應用 Immer）
- 未 memoize 大開銷計算
- 過度層級的 Provider wrapping
```

---

## 九、成本與風險評估表

設計 Loop 時填此表：

| 項目 | 建議值 | 你的設定 | 理由 |
|------|------|--------|------|
| 觸發類型 | 事件優先 | ? | 減少空轉 |
| 執行頻率 | 低頻起步 | ? | 驗證品質 |
| 單輪成本估計 | < $0.1 | ? | 控制整體支出 |
| 日上限 (budget) | 10–50 次 | ? | 防失控 |
| 模型層級 | 見分層表 | ? | 成本與品質平衡 |
| 製造/檢查分離 | 必須 | ✅/❌ | 維持品質把關 |
| Memory_File | 至少一個 | ✅/❌ | 跨會話銜接 |

---

## 十、問題排查

### Q1：Validator 回報「weak-verify-condition」
**原因**：完成條件全部都是主觀描述  
**解決**：改為「測試通過」「lint 無錯誤」「指標達門檻」「人工核准」四類之一

### Q2：Loop 執行一段時間後，產出品質下降
**可能原因**：
1. Verification_Condition 過弱（第一時間未攔截問題）
2. 頻率過高（降低質量）
3. 代理角色職責重疊（製造/檢查混淆）

**排查**：
- 用反模式檢查清單逐項對照
- 隨機抽查 3–5 個「通過」的產出
- 檢視 Memory_File 是否有線索

### Q3：成本超支
**可能原因**：
1. 頻率設定過高
2. 用了強推理模型進行輕量工作
3. 無效觸發（定時觸發但無變化）

**改善**：
- 改事件觸發
- 按任務難度採用模型分層
- 降低觸發頻率

---

**版本**：1.0  
**更新日期**：2025 年 1 月
