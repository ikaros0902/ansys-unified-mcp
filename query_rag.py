"""Quick interactive tool to search the local ANSYS & CAE RAG knowledge base."""

import sys
import sqlite3
from pathlib import Path

INDEX_PATH = Path(__file__).resolve().parent / "Documentation_clean" / "docs_index.sqlite"

def search_rag(query: str, top_k: int = 3):
    if not INDEX_PATH.exists():
        print(f"錯誤：找不到 RAG 資料庫 ({INDEX_PATH})，請先執行 python build_rag_knowledge.py")
        return

    con = sqlite3.connect(str(INDEX_PATH))
    con.row_factory = sqlite3.Row

    # Format query for trigram matching
    # SQLite FTS5 trigram works best with exact terms or keywords
    sql = """
        SELECT doc, ord, heading, body,
               snippet(chunks, 3, '>>', '<<', '...', 12) AS snip,
               bm25(chunks) AS score
        FROM chunks
        WHERE chunks MATCH ?
        ORDER BY score
        LIMIT ?
    """

    try:
        # Match trigram
        clean_q = f'"{query}"' if " " in query else query
        rows = con.execute(sql, (clean_q, top_k)).fetchall()
        if not rows:
            # Fallback to loose match
            rows = con.execute(sql, (query, top_k)).fetchall()
    except Exception as e:
        print(f"檢索錯誤: {e}")
        con.close()
        return

    print(f"\n=======================================================")
    print(f"[SEARCH] Query: '{query}' (Found {len(rows)} matching chunks)")
    print(f"=======================================================\n")

    for i, r in enumerate(rows, 1):
        print(f"[{i}] Document: {r['doc']}")
        print(f"    Heading: {r['heading']}")
        print(f"    Snippet: {r['snip']}")
        print(f"    Content Preview:\n{'-'*40}\n{r['body'][:400]}...\n{'-'*40}\n")

    con.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query_text = " ".join(sys.argv[1:])
    else:
        query_text = "SpaceClaim"
    search_rag(query_text)
