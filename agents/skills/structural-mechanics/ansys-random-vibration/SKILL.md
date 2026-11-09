---
name: ansys-random-vibration
description: Random vibration PSD analysis and Miles equation fatigue assessment in Mechanical.
---

# 隨機振動 PSD 分析與 Miles 方程評估

本技能指導工程師與 Agent 執行 隨機振動 PSD 分析與 Miles 方程評估 之標準化模擬工作流。遵循雙軌架構，支援商業求解器連線與離線數值基準驗收。

## 核心工作流規範

1. **API 查詢與校驗**：使用 `api_search(query='...', product='mechanical')` 搜尋符號，調用 `api_validate_script` 進行靜態檢查。
2. **知識字典檢索**：呼叫 `ans_get_knowledge_dictionary(product='mechanical')` 查閱最新版本規範與限制。
3. **官方範例對齊**：檢閱 **official_examples.md** 與調用 `ans_search_official_examples` 獲取權威流程。
4. **客觀驗收條件**：執行 `scripts/verify_random_vibration_baseline.py` 確認數值基準完全吻合（Exit Code 0）。

## 參考文檔與雙軌腳本

- 詳細技術指南：[api_and_workflows.md](references/api_and_workflows.md)
- 官方範例庫：**official_examples.md**
- 數值基準腳本：`scripts/verify_random_vibration_baseline.py`
