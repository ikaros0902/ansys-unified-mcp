#!/usr/bin/env python
"""PDF -> Markdown converter (token-lean, text-only, fast).

Uses plain PyMuPDF text extraction. ~0.9s per 350-page manual.
Images are ignored on purpose (see ponytail note below).

Usage:
    python convert.py <input>            # single .pdf OR a folder of PDFs
    python convert.py <input> -o <dir>   # choose output dir
    python convert.py <input> --force    # overwrite existing .md

Default output dir: sibling "<folder>_md" for a folder, or "<pdf_dir>_md" for a file.
Each PDF becomes one .md with per-page markers:  <!-- page N -->
so the file stays human-readable and can later be chunked by page for search.

ponytail: uses PyMuPDF get_text() (plain text) instead of ML layout analysis.
Ceiling = tables lose pipe-table formatting (content is kept as text) and
image-only/scanned pages yield no text (no OCR). Upgrade path = pymupdf4llm for
tables, or an OCR pass (pytesseract) for scanned pages -- both far slower.
"""
import argparse
import sys
from pathlib import Path

import pymupdf


def convert_one(pdf: Path, out_dir: Path, force: bool) -> tuple[str, str]:
    """Convert a single PDF to Markdown. Returns (status, message)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / (pdf.stem + ".md")
    if md_path.exists() and not force:
        return ("skip", f"{md_path.name} (exists, use --force)")

    doc = pymupdf.open(str(pdf))
    parts = [f"# {pdf.stem}\n"]
    for i, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        if not text:  # image-only / empty page -> skip (ponytail: no OCR)
            continue
        parts.append(f"\n<!-- page {i} -->\n\n{text}\n")
    doc.close()

    md_path.write_text("".join(parts), encoding="utf-8")
    kb = md_path.stat().st_size / 1024
    return ("ok", f"{md_path.name} ({kb:.0f} KB)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Convert PDF(s) to Markdown.")
    ap.add_argument("input", help="A .pdf file or a folder containing PDFs")
    ap.add_argument("-o", "--out", help="Output directory")
    ap.add_argument("--force", action="store_true", help="Overwrite existing .md")
    args = ap.parse_args()

    src = Path(args.input).resolve()
    if not src.exists():
        print(f"ERROR: not found: {src}", file=sys.stderr)
        return 1

    if src.is_dir():
        pdfs = sorted(src.glob("*.pdf"))
        out_dir = Path(args.out).resolve() if args.out else src.parent / f"{src.name}_md"
    else:
        if src.suffix.lower() != ".pdf":
            print(f"ERROR: not a PDF: {src}", file=sys.stderr)
            return 1
        pdfs = [src]
        out_dir = Path(args.out).resolve() if args.out else src.parent / f"{src.parent.name}_md"

    if not pdfs:
        print(f"No PDFs found in {src}", file=sys.stderr)
        return 1

    print(f"Converting {len(pdfs)} PDF(s) -> {out_dir}", flush=True)
    ok = skip = fail = 0
    for pdf in pdfs:
        try:
            status, msg = convert_one(pdf, out_dir, args.force)
        except Exception as e:  # keep going on a bad file
            fail += 1
            print(f"  [FAIL] {pdf.name}: {e}", file=sys.stderr, flush=True)
            continue
        if status == "ok":
            ok += 1
            print(f"  [OK]   {msg}", flush=True)
        else:
            skip += 1
            print(f"  [SKIP] {msg}", flush=True)

    print(f"Done. ok={ok} skip={skip} fail={fail}", flush=True)
    return 0 if fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
