"""Build a unified RAG Knowledge Base from all skills, guides, and references in the repo."""

import os
import sqlite3
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
CLEAN_DIR = REPO_ROOT / "Documentation_clean"
INDEX_PATH = CLEAN_DIR / "docs_index.sqlite"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150

def chunk_markdown(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks = []
    i, n = 0, len(text)
    while i < n:
        end = min(i + size, n)
        if end < n:
            nl = text.rfind("\n", i + size - overlap, end)
            if nl > i:
                end = nl
        chunk = text[i:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        i = max(end - overlap, i + 1)
    return chunks

def extract_heading(chunk: str) -> str:
    for line in chunk.splitlines():
        s = line.strip().lstrip("#").strip()
        if s:
            return s[:120]
    return "Untitled"

def build_knowledge_base():
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    if INDEX_PATH.exists():
        try:
            INDEX_PATH.unlink()
        except Exception:
            pass

    con = sqlite3.connect(str(INDEX_PATH))
    con.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5("
        "doc UNINDEXED, ord UNINDEXED, heading, body, tokenize='trigram')"
    )
    con.execute(
        "CREATE TABLE IF NOT EXISTS docs_meta ("
        "name TEXT PRIMARY KEY, title TEXT, category TEXT, product TEXT, "
        "chunks INTEGER, chars INTEGER)"
    )

    # Gather all markdown files
    scan_paths = [
        (REPO_ROOT / ".kiro" / "skills", "skill"),
        (REPO_ROOT / "steering" / "reference", "architecture"),
        (REPO_ROOT / "Documentation_md", "manual"),
    ]

    total_docs = 0
    total_chunks = 0

    for base_dir, category in scan_paths:
        if not base_dir.exists():
            continue
        for md_file in base_dir.rglob("*.md"):
            rel_name = md_file.relative_to(REPO_ROOT).as_posix().replace("/", "_").replace(".md", "")
            title = md_file.stem.replace("_", " ").replace("-", " ").title()
            
            # Identify product
            product = "general"
            lower_path = md_file.as_posix().lower()
            if "spaceclaim" in lower_path:
                product = "spaceclaim"
            elif "mechanical" in lower_path:
                product = "mechanical"
            elif "lsdyna" in lower_path or "ls-dyna" in lower_path or "ls-prepost" in lower_path:
                product = "lsdyna"
            elif "optislang" in lower_path:
                product = "optislang"
            elif "pcb" in lower_path:
                product = "pcb_warpage"
            elif "error" in lower_path:
                product = "error_catalog"

            raw_text = md_file.read_text(encoding="utf-8", errors="replace")
            if not raw_text.strip():
                continue

            chunks = chunk_markdown(raw_text)
            if not chunks:
                continue

            for ord_idx, chunk in enumerate(chunks):
                heading = extract_heading(chunk)
                con.execute(
                    "INSERT INTO chunks(doc, ord, heading, body) VALUES(?, ?, ?, ?)",
                    (rel_name, ord_idx, heading, chunk),
                )

            con.execute(
                "INSERT OR REPLACE INTO docs_meta(name, title, category, product, chunks, chars) "
                "VALUES(?, ?, ?, ?, ?, ?)",
                (rel_name, title, category, product, len(chunks), len(raw_text)),
            )

            total_docs += 1
            total_chunks += len(chunks)

    con.commit()
    con.close()

    print(f"[OK] RAG Knowledge Base built successfully!")
    print(f"[PATH] Database: {INDEX_PATH}")
    print(f"[STATS] Total Documents: {total_docs}")
    print(f"[STATS] Total Chunks: {total_chunks}")

if __name__ == "__main__":
    build_knowledge_base()
