# ANSYS 文件來源清冊

`scripts/maintenance/inventory_ansys_sources.py` 可對多個文件根目錄遞迴盤點，產生 JSON 清冊，原始文件維持在原路徑。每筆記錄包含來源路徑、檔案大小、SHA-256、產品與文件類型的路徑推定、版本線索及內容品質初判。版本及產品欄位是啟發式線索，需以文件正文／封面核實；清冊不代表內容已完整擷取或 API 已驗證。

範例：

```powershell
python scripts/maintenance/inventory_ansys_sources.py `
  --root D:\ansys-docs-local `
  --root D:\Ikaros\ACT_Test\3.documents `
  --output .runtime\ansys-source-inventory.json
```

輸出可能包含大量路徑與雜湊，屬本機衍生資料；不要將完整手冊或大型清冊提交至版本庫。重建索引仍以 `analytics/docsearch/config.py` 中明確策展的文件集合為準。

額外 Markdown 語料可透過 `ANSYS_DOCS_EXTRA_ROOTS` 環境變數加入（多個根目錄以 Windows 分號分隔），之後呼叫 `rebuild_ansys_docs_index` 重建。PDF、HTML、空檔、模板與下載入口會出現在清冊，但不會直接進入 FTS 索引；PDF 須先轉成保留頁碼的 Markdown，再加入語料根目錄。索引中的 release 是正文文字線索，需回查封面或版本說明後才能作版本依據。
