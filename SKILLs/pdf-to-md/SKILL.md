---
name: pdf-to-md
description: Convert PDF documents to token-lean Markdown for downstream RAG/search. Extracts clean text, tables, and per-page markers using pymupdf4llm. Skips images (no OCR). Use when the user wants to turn PDFs (manuals, docs, guides) into Markdown, prepare documentation for an MCP/search index, or asks to "convert PDF to md".
keywords: pdf, markdown, md, convert, documentation, docs, pymupdf, pymupdf4llm, extract text, rag, ANSYS documentation
---

# PDF to Markdown Skill

Convert text-based PDFs into clean, token-lean Markdown suitable for search
indexing and RAG. Built on plain `pymupdf` text extraction — fast (~1s per
350-page manual), no ML, no heavy deps.

## When to use

- User wants PDFs converted to Markdown.
- Preparing documentation for a search MCP / index.
- Any "pdf -> md" batch job over a folder of manuals.

## What it produces

- One `.md` per PDF, filename mirrors the source (`Guide.pdf` -> `Guide.md`).
- Each page separated by a `<!-- page N -->` marker, so the output stays
  human-readable AND can be chunked by page later (keeps citations/page numbers).
- Table content kept as plain text (no pipe-table formatting).
- Images/scanned pages skipped (token-lean, no OCR).

## How to run

The converter lives next to this file: `convert.py`. Run it with the project's
venv Python so `pymupdf4llm` is available.

Convert a whole folder (default output = sibling `<folder>_md`):

```powershell
& ".venv\Scripts\python.exe" ".kiro\skills\pdf-to-md\convert.py" "Documentation"
```

Convert a single file, custom output dir, overwrite existing:

```powershell
& ".venv\Scripts\python.exe" ".kiro\skills\pdf-to-md\convert.py" "Documentation\Ansys_Mechanical_Users_Guide.pdf" -o "Documentation_md" --force
```

Options:
- `-o, --out <dir>`  output directory (default: `<input_folder>_md`)
- `--force`          overwrite existing `.md` (default: skip already-converted)

## Requirements

- `pymupdf` installed in the active environment (`pip install pymupdf`).

## Notes / limits

- Text-based PDFs only. Image-only or scanned pages produce no text and are
  skipped. To handle those, add an OCR pass (e.g. `pytesseract`) — not included
  to keep the skill lightweight.
- Tables come through as plain text, not Markdown pipe tables. If you need
  proper table markup, `pymupdf4llm` does it but is ~400x slower (ML layout);
  not worth it for keyword search.
- Runs in seconds even for large manuals; the script prints progress and keeps
  going if one file fails.
