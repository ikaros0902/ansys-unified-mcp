# ANSYS 文件來源清冊

`scripts/maintenance/inventory_ansys_sources.py` 可對多個文件根目錄遞迴盤點，產生 JSON 清冊，原始文件維持在原路徑。每筆記錄包含來源路徑、檔案大小、SHA-256、產品與文件類型的路徑推定、版本線索及內容品質初判。版本及產品欄位是啟發式線索，需以文件正文／封面核實；清冊不代表內容已完整擷取或 API 已驗證。

範例：

```powershell
python scripts/maintenance/inventory_ansys_sources.py `
  --root ANSYS_Document `
  --output .runtime\ansys-source-inventory.json
```

輸出可能包含大量路徑與雜湊，屬本機衍生資料；不要將完整手冊或大型清冊提交至版本庫。重建索引仍以 `analytics/docsearch/config.py` 中明確策展的文件集合為準。

產品文件庫由 `ANSYS_Document/_catalog/documents.json` 提供來源、產品版本與 SDK metadata；維護流程見 [文件庫維護](ANSYS_DOCUMENT_MAINTENANCE.md)。PDF、HTML 先建立正文視圖，只有 `body_present` 資料進入 FTS 索引。其他 Markdown 語料仍可透過 `ANSYS_DOCS_EXTRA_ROOTS` 加入（Windows 用分號分隔），再呼叫 `rebuild_ansys_docs_index`。版本須有封面或官方來源證據，不能以檔名取代查證。

## ANSYS 2025 R1 本機二進位來源盤點

2026-10-28 對 `$env:AWP_ROOT251` 遞迴盤點到 40 個頂層目錄、29,969 個 `.dll` 檔，合計 55,598,911,966 bytes（約 51.8 GiB）。下表只按頂層路徑分組。它包含共用 runtime、第三方元件、外掛和 native library，不能視為 40 個產品或 29,969 個 API。主 REA 候選清冊記錄 47 個檢查結果（42 份 metadata complete、5 份 absent），另完成 23 個 `Ans.Dpf.*` 元件的 REA/PE sweep；APIKB 收錄 42 份 managed snapshot 與 33 份 native export snapshot。另檢查 Lumerical 的兩個 Python interop DLL 與一個 Tcl DLL，建立 39 個 native export 候選。這不是全安裝樹的逐檔 API 分析。產品歸屬和 API 是否公開／受支援，仍須逐來源核對官方文件與產品模組。

| 安裝樹頂層目錄 | DLL 數 | 安裝樹頂層目錄 | DLL 數 |
|---|---:|---|---:|
| `AnsysEM` | 4,514 | `Optical Products` | 4,448 |
| `AddPrint` | 3,453 | `commonfiles` | 3,014 |
| `RSM` | 1,755 | `scdm` | 1,697 |
| `optiSLang` | 1,593 | `Discovery` | 989 |
| `CEI` | 804 | `aisol` | 775 |
| `fluent` | 673 | `Additive` | 639 |
| `Motion` | 613 | `tp` | 573 |
| `Addins` | 411 | `CFX` | 365 |
| `ansys` | 349 | `Lumerical` | 348 |
| `TwinAI` | 327 | `TurboGrid` | 321 |
| `CFD-Post` | 318 | `Zemax OpticStudio` | 308 |
| `Acoustics` | 287 | `ACP` | 284 |
| `Artemis` | 211 | `SystemCoupling` | 179 |
| `Electronics` | 167 | `Framework` | 158 |
| `reaction` | 65 | `meshing` | 53 |
| `dpf` | 48 | `fensapice` | 46 |
| `aqwa` | 41 | `OpticsLauncher` | 39 |
| `polyflow` | 29 | `icemcfd` | 23 |
| `DistortionCompensation` | 22 | `installer` | 17 |
| `licensingclient` | 7 | `sherlock` | 6 |
