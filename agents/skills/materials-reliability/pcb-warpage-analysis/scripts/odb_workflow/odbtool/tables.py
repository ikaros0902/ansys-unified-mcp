"""Read .xlsx / .xlsm / .xls / .csv into plain grids (no format assumptions here).

Grid = list of rows, row = list of cell values (str, float or None), 0-based.
Row/column numbers shown to users are 1-based Excel style (row 7, column K).
"""
from __future__ import annotations

import csv
from pathlib import Path

from .util import ToolError


def read_workbook(path: Path) -> dict[str, list[list]]:
    path = Path(path)
    if not path.is_file():
        raise ToolError(f"file not found: {path}")
    ext = path.suffix.lower()
    if ext in (".xlsx", ".xlsm"):
        return _read_xlsx(path)
    if ext == ".xls":
        return _read_xls(path)
    if ext in (".csv", ".txt"):
        return {"csv": _read_csv(path)}
    raise ToolError(f"unsupported table format {ext} ({path.name}); use .xlsx, .xls or .csv")


def _clean(v):
    if v is None:
        return None
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    return s if s else None


def _read_xlsx(path: Path) -> dict[str, list[list]]:
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    out = {}
    for ws in wb.worksheets:
        out[ws.title] = [[_clean(v) for v in row] for row in ws.iter_rows(values_only=True)]
    wb.close()
    return out


def _read_xls(path: Path) -> dict[str, list[list]]:
    import xlrd
    wb = xlrd.open_workbook(str(path))
    out = {}
    for sh in wb.sheets():
        rows = []
        for r in range(sh.nrows):
            row = []
            for c in range(sh.ncols):
                cell = sh.cell(r, c)
                if cell.ctype in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
                    row.append(None)
                elif cell.ctype == xlrd.XL_CELL_NUMBER:
                    row.append(float(cell.value))
                else:
                    row.append(_clean(cell.value))
            rows.append(row)
        out[sh.name] = rows
    return out


def _read_csv(path: Path) -> list[list]:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "cp950", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t") if text.strip() else csv.excel
    rows = []
    for row in csv.reader(text.splitlines(), dialect):
        out = []
        for v in row:
            v = v.strip()
            try:
                out.append(float(v))
            except ValueError:
                out.append(v or None)
        rows.append(out)
    return rows


def cell(grid: list[list], r: int, c: int):
    if r < 0 or r >= len(grid) or c < 0 or c >= len(grid[r]):
        return None
    return grid[r][c]


def ncols(grid: list[list]) -> int:
    return max((len(r) for r in grid), default=0)
