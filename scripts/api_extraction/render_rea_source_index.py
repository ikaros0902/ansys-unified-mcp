"""Render a human-readable index for captured REA managed snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
API_DIR = ROOT / "docs" / "api_inventory"
OUTPUT = API_DIR / "curated" / "rea" / "index.md"


def _cell(value: Any) -> str:
    return str(value or "").replace("|", r"\|").replace("\r", " ").replace("\n", " ")


def _source_key(path: Path) -> str:
    return path.stem.removesuffix("_api")


def main() -> None:
    snapshots = []
    for path in sorted(API_DIR.glob("*_rea_api.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        stats = data.get("statistics", {})
        assembly = data.get("sources", {}).get("assembly", {})
        snapshots.append((path, data, stats, assembly))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    total_classes = sum(item[2].get("total_classes", 0) for item in snapshots)
    total_methods = sum(item[2].get("total_methods", 0) for item in snapshots)
    lines = [
        "# REA v251 managed candidate index",
        "",
        f"This index covers {len(snapshots)} captured REA JSON snapshots. Together, they contain {total_classes:,} class records and {total_methods:,} MethodDef rows.",
        "",
        "> These are static metadata rows. They can include non-public members. They do not establish product ownership, public API status, vendor support, or runtime behavior.",
        "> Use [the product matrix](../../PRODUCT_API_MATRIX.md) for current product mapping and gaps. Use APIKB for member-level search.",
        "",
        "## Snapshot summary",
        "",
        "| APIKB source key | Assembly | Modules | Class records | MethodDef rows | Snapshot |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for path, data, stats, assembly in snapshots:
        key = _source_key(path)
        lines.append(
            f"| `{key}` | `{_cell(assembly.get('file') or data.get('module'))}` | "
            f"{stats.get('total_modules', len(data.get('modules', {})))} | "
            f"{stats.get('total_classes', 0)} | {stats.get('total_methods', 0)} | "
            f"[JSON](../../{path.name}) |"
        )

    lines.extend(["", "## Assembly evidence", ""])
    for path, data, _, assembly in snapshots:
        key = _source_key(path)
        lines.append(
            f"- `{key}` — SHA-256 `{assembly.get('sha256', 'not recorded')}`; "
            f"MVID `{assembly.get('mvid', 'not recorded')}`; "
            f"REA Evidence ID `{assembly.get('rea_evidence_id', 'not recorded')}`."
        )

    lines.extend(
        [
            "",
            "## Regenerate this index",
            "",
            "```powershell",
            "python scripts/api_extraction/render_rea_source_index.py",
            "```",
            "",
        ]
    )
    OUTPUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT.relative_to(ROOT).as_posix()} from {len(snapshots)} REA snapshots")


if __name__ == "__main__":
    main()
