---
name: ansys-thermal-analysis
description: Set up or review ANSYS thermal and thermal-structural workflows, mapping, and result validity. Use for steady or transient thermal, thermal stress, and warpage tasks; route Icepak-specific workflows to its separate product guidance.
---

# ANSYS 熱分析與熱結構耦合

分清熱求解器、結構求解器、幾何與結果傳遞介面。Mechanical／Workbench 內的 Thermal analysis、Icepak 電子散熱模型與 Thermal Desktop 是不同產品工作流；不可因都涉及溫度便假設 API、網格或邊界相同。

## 工作順序

1. 確認產品／宿主、版本、穩態或暫態、時間點、單位及熱模型範圍。
2. 盤點材料熱物性及其溫度相依性、熱源、熱流、對流、輻射、接觸熱阻與環境條件；量值需有來源。
3. 熱應力／翹曲另核對結構材料、CTE 定義、無應力參考溫度、支承及所匯入溫度場的時間與幾何映射。
4. 寫入前先檢查將修改的系統與來源檔；寫入／求解後讀回系統連結、邊界值、映射覆蓋及求解器日誌。
5. 報告需區分解析估算、mock、Workbench journal 建立結果及真實 solver 結果。只有真實溫度場／求解日誌能支持已求解聲明。

## 路由

- Mechanical 熱分析、CTE／邊界條件：讀取 [`ansys-mechanical`](../ansys-mechanical/SKILL.md) 的材料、邊界與多物理場參考。
- PCB stackup／ROM 熱翹曲：讀取 [`pcb-warpage-analysis`](../pcb-warpage-analysis/SKILL.md)，並核對它的輸入和估算假設。
- 電子設備空氣冷卻／Icepak：讀取 [`ansys-icepak`](../ansys-icepak/SKILL.md)。
- Thermal Desktop：本 MCP 沒有列為已支援產品；按其 OpenTD／.NET API 文件走獨立支援評估，不沿用 Mechanical Thermal 工具。

文件來源與目前執行支援界線見 [領域來源矩陣](../../../docs/skills/DOMAIN_SOURCE_AND_SUPPORT.md)。


