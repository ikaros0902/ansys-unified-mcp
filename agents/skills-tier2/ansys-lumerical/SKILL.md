---
name: ansys-lumerical
description: Route Ansys Lumerical Python and scripting work to the installed product and solver documentation. Use for FDTD, MODE, and Lumerical optical simulations; this skill does not provide a live MCP connector.
---

# Ansys Lumerical 光子模擬

先識別 FDTD、MODE、INTERCONNECT 或其他 solver、產品版本、GUI／batch 宿主及 `lumapi` Python／腳本介面。使用產品目標版本的 `lumapi` 文件與範例，不因能匯入 Python 模組便視為 solver 可連線。

修改模型前先保存可回復副本。逐項核對 geometry／mesh order、材料及色散資料、source、monitor、邊界條件、solver region、頻率／波長與單位。執行後讀回實際 monitor 資料與 solver 狀態；將網格／時間步長收斂與插值設定納入比較。

目前本 MCP 無 Lumerical controller。文件來源與版本限制見 [領域來源矩陣](../../../docs/skills/DOMAIN_SOURCE_AND_SUPPORT.md)。


