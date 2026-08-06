"""Rule-based cleaning of PDF-converted ANSYS markdown.

Removes the high-volume conversion noise that dilutes search quality:
- ``<!-- page N -->`` markers
- the per-page ANSYS/Synopsys copyright footer (2 lines, on every page)
- lone page-number lines (arabic and roman numerals)
- table-of-contents dot-leader lines
- cover-page / copyright / trademark / disclaimer boilerplate
- (lstc style) the LS-PrePost revision-history table rows

The rules are deliberately conservative line filters plus blank-line
collapsing; they are idempotent and safe to re-run. Lines inside fenced code
blocks (``` ... ```) are never filtered.
"""

from __future__ import annotations

import re

# ``<!-- page 12 -->``
_PAGE_MARKER = re.compile(r"^\s*<!--\s*page\s+\d+\s*-->\s*$", re.IGNORECASE)

# Per-page footer, e.g.
#   "Release 2026 R1 - © ANSYS, Inc. All rights reserved. - Contains proprietary..."
#   "of Synopsys, Inc., ANSYS, Inc., subsidiaries and affiliates."
_FOOTER_LINE1 = re.compile(
    r"^\s*Release\s+\d{4}\s+R\d+\s*-\s*©\s*ANSYS,\s*Inc\.\s*All rights reserved",
    re.IGNORECASE,
)
_FOOTER_LINE2 = re.compile(
    r"^\s*of\s+Synopsys,\s*Inc\.,\s*ANSYS,\s*Inc\.,\s*subsidiaries and affiliates\.?\s*$",
    re.IGNORECASE,
)

# Lone page number: only digits, or only roman numerals (i, ii, ... xlv ...).
_LONE_ARABIC = re.compile(r"^\s*\d{1,4}\s*$")
_LONE_ROMAN = re.compile(r"^\s*[ivxlcdm]{1,7}\s*$", re.IGNORECASE)

# Table-of-contents dot leaders: "... Something ......... 175"
_TOC_LEADER = re.compile(r"\.{4,}\s*\d+\s*$")
_TOC_UNICODE_LEADER = re.compile(r"…{2,}")

# Cover / legal boilerplate anchors (case-insensitive substring match).
_BOILERPLATE_ANCHORS = (
    "copyright and trademark information",
    "copyright ©",
    "proprietary to ansys",
    "disclaimer notice",
    "this ansys software product",
    "u.s. government rights",
    "for u.s. government users",
    "third-party software",
    "see the legal information",
    "published in the u.s.a",
    "ansysinfo@ansys.com",
    "http://www.ansys.com",
    "southpointe",
    "ansys drive",
    "canonsburg",
    "registered iso",
    "9001:",
    "are ul",
    "companies.",
    "ansys europe",
    "flexlm and flexnet",
    "icem cfd is a trademark",
    "all other brand",
    "names, logos and slogans",
)
_PHONE = re.compile(r"^\s*\((?:T|F)\)\s*\d{3}-\d{3}-\d{4}\s*$")

# Inline page cross-references, e.g. "Joint (p. 485)" -> "Joint". These PDF
# TOC/cross-ref artifacts appear thousands of times in reference docs and add
# pure noise to the search index without carrying any API meaning.
_PAGE_XREF = re.compile(r"\s*\(p\.\s*\d+\)")

# lstc revision-history rows.
_REV_ROW = re.compile(r"^\s*Rev\.?\s*\d+", re.IGNORECASE)
_DATE_ONLY = re.compile(
    r"^\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|"
    r"April|June|July|August|September|October|November|December)\.?\s+\d{1,2}\s*,?\s*\d{4}\s*$",
    re.IGNORECASE,
)


def _is_boilerplate(line: str) -> bool:
    low = line.strip().lower()
    if not low:
        return False
    return any(anchor in low for anchor in _BOILERPLATE_ANCHORS)


def _drop_line(line: str, style: str) -> bool:
    if _PAGE_MARKER.match(line):
        return True
    if _FOOTER_LINE1.match(line) or _FOOTER_LINE2.match(line):
        return True
    if _LONE_ARABIC.match(line) or _LONE_ROMAN.match(line):
        return True
    if _TOC_LEADER.search(line) or _TOC_UNICODE_LEADER.search(line):
        return True
    if _PHONE.match(line):
        return True
    if _is_boilerplate(line):
        return True
    if style == "lstc" and (_REV_ROW.match(line) or _DATE_ONLY.match(line)):
        return True
    return False


def clean_markdown(text: str, style: str = "ansys") -> str:
    """Return a cleaned copy of a PDF-converted markdown document."""
    out: list[str] = []
    in_code = False
    blank_run = 0

    for line in text.splitlines():
        stripped = line.strip()

        # Never filter inside fenced code blocks.
        if stripped.startswith("```"):
            in_code = not in_code
            out.append(line)
            blank_run = 0
            continue
        if in_code:
            out.append(line)
            continue

        if _drop_line(line, style):
            continue

        if not stripped:
            blank_run += 1
            if blank_run <= 1:
                out.append("")
            continue

        blank_run = 0
        # Strip inline page cross-references (noise); keeps the surrounding text.
        out.append(_PAGE_XREF.sub("", line).rstrip())

    # Trim leading/trailing blank lines.
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()

    return "\n".join(out) + "\n"
