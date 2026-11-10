# Mechanical API 字典：2025 R1

## AI 檢索指引

Use APIKB for Mechanical v251 symbols and signatures. Use document search for official usage examples. Keep the source and validation status with each result.

先用 APIKB `api_search` 搜尋符號，再用 `api_get` 依產品、release 與完整名稱取得定義和來源。需要操作步驟時，再用 docsearch 搜尋官方文件。只把官方文件明示的內容標成文件確認。

## `Analysis.AddFixedSupport`

| 欄位 | 證據 |
| --- | --- |
| 產品／版本 | Ansys Mechanical，2025 R1 (`v251`) |
| 完整名稱 | `Ansys.ACT.Automation.Mechanical.Analysis.AddFixedSupport` |
| Snapshot 簽名 | `AddFixedSupport() -> Ansys.ACT.Automation.Mechanical.BoundaryConditions.FixedSupport` |
| 官方文件確認 | v251 Analysis object 頁面示範從 `Analysis` 呼叫無參數 `AddFixedSupport()`，並將結果存入變數。頁面沒有確認回傳型別。 |
| Snapshot 來源 | [`mechanical_api.json`](../../mechanical_api.json)，snapshot SHA-256：`ef8c5c515bf8651d1a517068423998209c3fdebcfea153cd33acb470201b1c2b` |
| 狀態 | 呼叫形式：官方文件確認。回傳型別：snapshot-only。宿主執行與支援合約：未驗證。 |

官方來源：[Accessing and Manipulating the Analysis Object](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/act_script/mech_apis_AnalysisObject.html)。此條目只描述官方範例中的呼叫形式，不代表已檢查其他 overload 或所有分析條件。
