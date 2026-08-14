---
name: ansys-error-catalog
description: >-
  ANSYS 開發中遇到的錯誤分類目錄，按模組（Workbench/Mechanical/SpaceClaim/ACT）
  和 function 分類，包含根因分析與解決方案。遇到 ANSYS 相關錯誤時載入此 skill。
keywords: error, NameError, StandardError, gRPC, IronPython, Workbench, Mechanical, ACT, debug, troubleshooting
---

# ANSYS 錯誤分類目錄

本目錄來自實際開發 session 中遭遇的錯誤，按模組與 function 分類。
每筆紀錄包含：觸發場景、錯誤訊息、根因、解決方案。

載入對應的 `reference/<module>.md` 來查閱詳細錯誤清單。

---

## 分類索引

| 模組 | 檔案 | 涵蓋錯誤類型 |
|---|---|---|
| Workbench ACT Plugin | `reference/workbench_act.md` | `_PROJECT_ROOT` NameError, `exec` closure SyntaxError, FileSystemWatcher 事件重複觸發 |
| Mechanical Scripting | `reference/mechanical_scripting.md` | Scoping 未指定 (❓ 圖示), `Quantity` 未定義, gRPC 連線失敗, `run_python_script` 環境差異 |
| SpaceClaim / PyGeometry | `reference/spaceclaim_pygeometry.md` | gRPC TLS 警告, `rename_object` 限制, `read_existing_design` 空回傳 |
| IronPython 2.7 通用 | `reference/ironpython_general.md` | `exec` 閉包限制, `__name__` 差異, `clr.AddReference` 重複, `reload()` 必要性 |

---

## 快速查找

遇到錯誤時，依據以下關鍵字快速定位：

- **NameError: global name '...' is not defined** → 先查 `ironpython_general.md`，再查對應模組
- **StandardError: Exception has been thrown by the target** → 查 `workbench_act.md`（通常是 .NET 內部呼叫失敗）
- **gRPC / connection refused** → 查 `mechanical_scripting.md` 的連線段
- **Scoping 黃色 ❓** → 查 `mechanical_scripting.md` 的 Location 段
- **SyntaxError in exec** → 查 `ironpython_general.md` 的閉包段
