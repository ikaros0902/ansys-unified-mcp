"""Minimal STEP reader: extents of the 2D drawing (CARTESIAN_POINT bounding box) in mm."""
from __future__ import annotations

import re
from pathlib import Path

from .util import ToolError

_PT = re.compile(r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)")


def stp_bbox_mm(path: Path) -> tuple[float, float, float, float]:
    t = Path(path).read_text(encoding="latin-1", errors="replace")
    pts = []
    for m in _PT.finditer(t):
        v = [float(x) for x in m.group(1).split(",") if x.strip()]
        if len(v) >= 2:
            pts.append(v)
    if not pts:
        raise ToolError(f"{Path(path).name}: no CARTESIAN_POINT found")
    k = 1.0
    if re.search(r"SI_UNIT\s*\(\s*\$\s*,\s*\.METRE\.", t):
        k = 1000.0                        # metres
    elif re.search(r"CONVERSION_BASED_UNIT\s*\(\s*'INCH'", t, re.I):
        k = 25.4
    xs = [p[0] * k for p in pts]
    ys = [p[1] * k for p in pts]
    return min(xs), min(ys), max(xs), max(ys)
