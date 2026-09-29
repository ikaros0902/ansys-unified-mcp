# 手動參考文件(非 always-on)

此資料夾存放已被精簡進規則的長文件原文,供需要時手動查閱,不再每次注入。

## 建議搬入此處(手動參考)

精華已抽進 `10-loop-engineering.md`,原文保留備查:

- `loop-engineering-specification.md` — 完整方法論規格
- `design.md` — 設計文件
- `requirements.md` — 需求文件
- `IMPLEMENTATION_GUIDE.md` — 實作指南
- `reference-loop-engineering.md` — 概念指南
- `AGENT_STEERING_RULES.md` — 原 agent 規則
- 8 份 `*.template.md` 樣板(automation-trigger / skill-document / sub-agent-role / memory-file / connector-registry / design-principles-checklist / anti-pattern-checklist / cost-risk-control)

精華已抽進 `20-adhd.md`,原文保留備查:

- `SKILL.md`、`SOURCE-SPEC.md`、`frames.md`

## 建議從 steering 直接刪除(純 GitHub repo boilerplate,非規則)

- `README.md`、`CODE_OF_CONDUCT.md`、`SECURITY.md`、`CONTRIBUTING.md`
- `api.md`、`install.md`、`quickstart.md`、`how-it-works.md`
- `when-to-use.md`、`vs-cot-and-tot.md`、`evals.md`、`EVALS_ADHD.md`

## 已被合併、原檔可刪除

以下原全域規則的精華已進入新規則檔,原檔可移除:

- `workflow.md` → 精華入 `00-behavior.md` / `10-loop-engineering.md`
- `ponytail.md` → 精華入 `00-behavior.md`(懶惰高效)
- `lazy-pack.md` → 精華入 `01-safety.md`(通用安全);其專案專屬的開工/收工流程另行處理
- `GEMINI.md` → 語言與工作模式精華入 `00-behavior.md`

## 移到 ANSYS 專案自己的 `.kiro/steering`(不放全域)

- ACT/Obsidian 專案規範(原 `workflow.md` 開頭那條「寫 ACT 程式碼先查 Obsidian ACT_Project」)
- ANSYS CAE 專家設定與 `contexts/context.md` 讀取慣例(原 `GEMINI.md`)
