---
name: ansys-ls-prepost
description: ANSYS LS-PrePost 腳本前處理與後處理精簡主控手冊。涵蓋 SCL 命令語言、命令行檔案 (.cfile) 與 Python DataCenter API，支援 d3plot 結果提取、雲圖繪製與模型建立。
keywords: ls-prepost, lspp, SCL, cfile, command file, runscript, runpython, LsPrePost, execute_command, cmd_result_get_value, DataCenter, get_data, data center, d3plot, fringe, post-processing
phase_gate:
  requires: []
  produces: []
---

# ANSYS LS-PrePost 腳本與前後處理主控手冊

LS-PrePost 具備三層腳本體系，依需求選用：

1. **SCL (Scripting Command Language)** — 運行於 LS-PrePost 內部的類 C 語言，可執行操作指令、提取 LS-DYNA 分析結果與讀取 d3plot / 關鍵字卡。
2. **命令檔 (`.cfile`)** — 記錄 LS-PrePost 命令序列，可透過 `runscript` / `runpython` 傳參調用 SCL 或 Python 腳本。
3. **Python 模組** — LS-PrePost Python API：`LsPrePost` (`execute_command`) 與 `DataCenter` (`get_data`)，用於專業後處理自動化。

## 模組路由表 (Module Router)

| 功能分類 | 參考手冊 | 核心內容要點 |
|---|---|---|
| 會話與命令行檔案 | `references/session_and_cfile.md` | SCL vs cfile vs Python 比較、傳參調用規範 |
| 模型資料查詢 | `references/model_query.md` | DataCenter 提取器、型別代碼、選取緩衝區 |
| 狀態與結果場 | `references/states_and_results.md` | `SCLSwitchStateTo`、應力/應變張量、位移向量、雲圖、binout |
| 模型建立與編輯 | `references/model_build.md` | 建立節點與單元、拉伸實體、曲線建構、部件管理 |
| 輸出與導出 | `references/output_export.md` | 輸出訊息檔案、反向傳回 LSPP 繪製雲圖、部件導出 |
| Python 模組介面 | `references/python_module_interface.md` | `LsPrePost.execute_command`、`DataCenter.get_data` 實作語法 |
