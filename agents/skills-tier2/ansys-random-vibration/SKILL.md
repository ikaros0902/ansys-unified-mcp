---
name: ansys-random-vibration
description: Plan and assess ANSYS Mechanical random vibration analyses using version-matched modal, PSD, damping, and result evidence. Use for PSD response or random vibration; do not use a transient shock workflow as a substitute.
---

# Mechanical 隨機振動分析

先確認目標版本、宿主介面、模態系統、PSD 定義與實際載荷方向，再建立／讀取 Random Vibration 系統。公式估值、mock 輸出與求解器結果需明確分開。

## 工作順序

1. 確認模態分析與 Random Vibration 的系統連結、支承、材料密度、阻尼及頻率範圍。
2. 核對輸入 PSD 的單位、頻率單位、單邊／雙邊慣例、方向、分段插值和頻帶端點。
3. 取得目標 release 的模態參與資料，核對激振方向與截止頻率；不要在未知分析設定時套用固定參與質量百分比。
4. 求解後記錄 RMS／統計量的種類與單位，抽查 PSD 頻譜和結果位置；可行時把頻域積分或量測資料作獨立對照。
5. 標示產品 build、SDK、宿主、輸入 PSD、阻尼、求解狀態與輸出來源。無實際結果檔及宿主日誌時，不得稱為已求解。

## 依據與限制

- 2026 R1 Mechanical User's Guide：Random Vibration Analysis，目錄約印刷頁 556。
- 2026 R1 Mechanical Scripting Guide：Random Vibration Analysis 範例，印刷頁約 402 起；示範以 Workbench 準備 Modal／Random Vibration 系統後執行 Mechanical 腳本。
- 透過 Mechanical 求解與 DPF 讀取現有 MCP 能力時，先使用 [`ansys-mechanical`](../ansys-mechanical/SKILL.md) 和 [`ansys-submodeling-dpf`](../ansys-submodeling-dpf/SKILL.md) 中適用的介面說明；此 skill 不宣稱 MCP 已註冊獨立的 Random Vibration connector。
- 模態質量、頻率截斷和 RMS 比對須依輸入 PSD、目標方向、分析設定及文件依據判讀；不得以單一百分比或頻率倍數通用阻斷。

參考來源與支援狀態見 [領域來源矩陣](../../../docs/skills/DOMAIN_SOURCE_AND_SUPPORT.md)。


