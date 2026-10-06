---
name: pdf-to-md
description: ANSYS 技術手冊與說明文檔 PDF 轉 Markdown 精簡轉換技能。基於 pymupdf / pymupdf4llm 高速抽取純文字與表格，生成帶有逐頁標記、適合 RAG 與檢索索引的輕量 Markdown。
keywords: pdf, markdown, md, convert, documentation, docs, pymupdf, pymupdf4llm, extract text, rag, ANSYS documentation
phase_gate:
  requires: []
  produces: []
---

# PDF 轉 Markdown 文檔處理技能

將文字型 PDF 高速轉換為乾淨、輕量且低 Token 消耗的 Markdown 格式，專門供 RAG 知識庫與 MCP 搜尋索引使用（基於 `pymupdf`，350 頁手冊約 1 秒完成）。

## 適用情境
- 需將 ANSYS 官方 PDF 技術手冊轉換為 Markdown。
- 為搜尋型 MCP 伺服器或檢索索引準備文檔語料。
- 批次轉換整批手冊資料夾。

## 產出規範
- 每個 PDF 產生單一 `.md` 檔案，檔名與來源對稱（`Guide.pdf` -> `Guide.md`）。
- 每一頁由 `<!-- page N -->` 註記分隔，便於後續分頁 Chunk 切分並保留頁碼引用。
- 圖片與純掃描頁面自動跳過，保持輕量低 Token。

## 執行方式
轉換腳本位於 `scripts/convert.py`：

```powershell
# 轉換整個資料夾
& ".venv\Scripts\python.exe" "skills\pdf-to-md\scripts\convert.py" "Documentation"

# 轉換單一檔案並指定輸出目錄
& ".venv\Scripts\python.exe" "skills\pdf-to-md\scripts\convert.py" "Documentation\Ansys_Mechanical_Users_Guide.pdf" -o "Documentation_md" --force
```
