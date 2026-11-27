"""Small shared helpers: normalization, number formatting, logging, hashing."""
from __future__ import annotations

import datetime as _dt
import hashlib
import re
import sys
from pathlib import Path

MIL_PER_UM = 1 / 25.4
UM_PER_MIL = 25.4
MIL_PER_OZ = 1.4            # copper thickness per oz used by the ANSYS ODB++ reader (verified)


class ToolError(Exception):
    """A problem the user must fix in the inputs. The message says what and where."""


class NeedAnswer(Exception):
    """Raised in non-interactive mode when a question has no recorded answer."""


def norm_token(s) -> str:
    """'p.p' -> 'pp', 'Solder mask' -> 'soldermask', 'Core ' -> 'core'."""
    return re.sub(r"[^a-z0-9]", "", str(s or "").lower())


def norm_material(s) -> str:
    """Material key used everywhere: upper case, letters and digits only. 'EM370(Z)' -> 'EM370Z'."""
    return re.sub(r"[^A-Za-z0-9]", "", str(s or "")).upper()


def words(s) -> list[str]:
    return re.findall(r"[a-z]+|\d+(?:\.\d+)?", str(s or "").lower())


def to_float(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def fmt(v: float, nd: int = 3) -> str:
    """Fixed decimals with trailing zeros removed: 74.930 -> '74.93', 2.0 -> '2'."""
    s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def timestamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def sha256(path: Path, chunk: int = 1 << 22) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def col_letter(idx0: int) -> str:
    s, n = "", idx0 + 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


class Log:
    """Print to the console and keep a copy in run.log."""

    def __init__(self, path: Path | None = None):
        self.path = path
        self.lines: list[str] = []

    def __call__(self, *parts) -> None:
        msg = " ".join(str(p) for p in parts)
        self.lines.append(msg)
        try:
            print(msg, flush=True)
        except UnicodeEncodeError:
            print(msg.encode(sys.stdout.encoding or "ascii", "replace").decode(), flush=True)
        if self.path:
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(msg + "\n")
