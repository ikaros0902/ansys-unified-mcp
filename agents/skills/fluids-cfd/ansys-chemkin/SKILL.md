---
name: ansys-chemkin
description: Ansys Chemkin-Pro reaction kinetics 0D and 1D reactor ignition and combustion analysis.
---

# Ansys Chemkin 化學反應動力學與燃燒分析

本技能指導工程師與 Agent 執行 Ansys Chemkin 化學反應動力學與燃燒分析 之標準化模擬工作流。遵循雙軌架構，支援商業求解器連線與離線數值基準驗收。

## 核心工作流規範

1. **API 查詢與校驗**：使用 `api_search(query='...', product='reaction_chemkin')` 搜尋符號，調用 `api_validate_script` 進行靜態檢查。
2. **知識字典檢索**：呼叫 `ans_get_knowledge_dictionary(product='reaction_chemkin')` 查閱最新版本規範與限制。
3. **官方範例對齊**：檢閱 [official_examples.md](references/official_examples.md) 與調用 `ans_search_official_examples` 獲取權威流程。
4. **客觀驗收條件**：執行 `scripts/verify_chemkin_baseline.py` 確認數值基準完全吻合（Exit Code 0）。

## 參考文檔與雙軌腳本

- 詳細技術指南：[api_and_workflows.md](references/api_and_workflows.md)
- 官方範例庫：[official_examples.md](references/official_examples.md)
- 數值基準腳本：`scripts/verify_chemkin_baseline.py`
