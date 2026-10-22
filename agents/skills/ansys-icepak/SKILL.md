---
name: ansys-icepak
description: Route and review Ansys Icepak electronics-cooling workflows against Icepak-specific guides and scripting APIs. Use for Icepak thermal models; current MCP execution support is limited and does not imply a validated solver connector.
---

# Ansys Icepak 產品路由

Icepak 電子冷卻模型不是 Mechanical Thermal analysis 的別名。核對幾何、功耗、流體區域、材料、風扇、熱接觸、外部邊界、網格及 energy balance 時，依 Icepak 產品版本與介面查閱專屬手冊。

## 查證流程

1. 從 `D:\Ikaros\ACT_Test\3.documents\AnsysEM\manuals_and_training\` 讀取版本相符的 Icepak Scripting Guide；GUI 設定使用 Getting Started 範例對照。
2. 區分 standalone Icepak 腳本、AEDT／PyAEDT 路線與 Workbench Mechanical Thermal 流程，僅採用目標環境已提供並可核實的介面。
3. 求解前讀回熱源功率、風扇／進出口邊界、材料、網格和既有求解器設定；不得把僅產生 `.py`、日誌或 CSV 的骨架當成真實求解。
4. 執行前確認目標 solver 路徑、版本、license 及輸入模型。結果需包含真實 solver 狀態、log 及溫度／熱流等 solver output。

## 支援狀態

本 MCP 目前只有 Icepak batch driver 骨架，並無經三版驗證的 Icepak connector。此 skill 供官方文件查證與支援狀態路由；禁止將骨架輸出宣告為已解算溫度場。

來源路徑與版本待核清單見 [領域來源矩陣](../../../docs/skills/DOMAIN_SOURCE_AND_SUPPORT.md)。


