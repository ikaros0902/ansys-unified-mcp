# SpaceClaim API 字典：2025 R1

## AI 檢索指引

Use APIKB for SpaceClaim v251 symbols and signature candidates. Use document search for official guides. Keep snapshot-only signatures separate from documented behavior.

先用 APIKB `api_search` 搜尋符號，再用 `api_get` 依產品、release 與完整名稱取得定義和來源。需要操作步驟時，再用 docsearch 搜尋官方指南。不要把反射或 REA metadata 當成官方支援合約。

## `DatumPlaneCreator.Create`

| 欄位 | 證據 |
| --- | --- |
| 產品／版本 | Ansys SpaceClaim Scripting API，2025 R1 (`v251`) |
| 完整名稱 | `SpaceClaim.Api.V251.Scripting.Commands.DatumPlaneCreator.Create` |
| Snapshot 來源 | [`spaceclaim_api.json`](../../spaceclaim_api.json)，snapshot SHA-256：`842645f05a06a1097c364648cf9370f1432d2a56c748124ddee7c0c3a5144219`；組件 SHA-256：`9f5f3d03675bfc1d62e6fbf0244c9473c5e861fcacc3242028b329350e268261` |
| 官方文件確認 | 官方 SpaceClaim API 頁面說明安裝目錄提供 `API_Scripting_Class_Library.chm`，用於查閱類別、方法與屬性。該頁未列出下表簽名。 |
| 狀態 | 五筆 overload 來自 Python.NET 反射 snapshot。尚未逐筆對照官方 CHM；預設參數、執行條件與宿主行為未確認。 |

| Overload | Snapshot 簽名 |
| --- | --- |
| 1 | `Create(Point origin, Direction zDir, Boolean select, ICommandInfo info) -> DatumPlaneResult` |
| 2 | `Create(Point origin, Direction xDir, Direction yDir, Boolean select, ICommandInfo info) -> DatumPlaneResult` |
| 3 | `Create(Plane plane, Boolean select, ICommandInfo info) -> DatumPlaneResult` |
| 4 | `Create(Frame frame, Boolean select, ICommandInfo info) -> DatumPlaneResult` |
| 5 | `Create(ISelection selection, Boolean select, ICommandInfo info) -> DatumPlaneResult` |

官方來源：[SpaceClaim API 文件說明](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/spaceclaim/Discovery/user_manual/spaceclaim_api.html)。這是 v252 說明頁，只用於確認官方文件類型與安裝位置。v251 release notes 記錄 scripting 版本及 API V22 棄用狀態：[Release 2025 R1](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/pdf/Ansys_Release_Notes.pdf)。

## 來源與缺口

- `SpaceClaim.Api.V251.Scripting.dll` 反射 snapshot 提供上述簽名。REA 靜態 metadata 尚未逐方法交叉比對。
- 本機 v251 `API_Scripting_Class_Library.chm` 原件留在 ANSYS 安裝目錄。本文不複製 CHM 或 PDF 原件。
- 未在 SpaceClaim 宿主執行呼叫，未求解，也未確認衍生簽名與手冊內容的公開散布權。
