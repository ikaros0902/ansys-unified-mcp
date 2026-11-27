"""The material library = PCB_Material_Library.xml (Engineering Data format), written by
3_materials/Update_PCB_Material_Library.py from the workbook of the material owners.

This module only finds names in the XML and cuts out the materials of one project. The
property values are interpreted in ONE place: the Mechanical v6 script.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from .util import ToolError

COPPER_NAME = "Copper for Warpage"
REPORT_NAME = "PCB_Material_Library_report.md"
WORKBOOK_NAME = "00_PCB Material Properties Library.xlsx"
_MAT = re.compile(r"[ \t]*<Material>.*?</Material>\n?", re.S)
_NAME = re.compile(r"<BulkDetails>\s*<Name>([^<]*)</Name>")


def norm(s) -> str:
    return "".join(c for c in str(s) if c.isalnum()).upper()


def _unesc(s: str) -> str:
    return s.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


def split_name(name: str) -> tuple[str, str | None, str]:
    """'EM-370(Z)_RC51_Ortho' -> ('EM-370(Z)_RC51', 'ORTHO', 'EM370Z')"""
    base, variant = name, None
    for suf, var in (("_ortho", "ORTHO"), ("_iso", "ISO")):
        if name.lower().endswith(suf):
            base, variant = name[:-len(suf)], var
    m = re.match(r"^(.*)_RC([A-Za-z0-9]+)$", base)
    return base, variant, norm(m.group(1) if m else base)


@dataclass
class Library:
    path: Path
    text: str
    sha: str
    blocks: dict[str, str] = field(default_factory=dict)          # material name -> XML block
    by_key: dict[str, list[str]] = field(default_factory=dict)    # EM370Z -> ['EM-370(Z)_RC51']

    @property
    def keys(self) -> set[str]:
        return set(self.by_key)


def load(path: Path) -> Library:
    path = Path(path)
    if path.suffix.lower() != ".xml":
        raise ToolError(f"inputs.material_library.path must be PCB_Material_Library.xml (Engineering Data "
                        f"library written by Update_PCB_Material_Library.py), not {path.name}. "
                        f"The CSV extract is no longer used.")
    raw = path.read_bytes()
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError:
        raise ToolError(f"{path.name} is not plain ASCII; it was not written by Update_PCB_Material_Library.py")
    text = text.replace("\r\n", "\n")
    if "<EngineeringData" not in text or "<Metadata>" not in text:
        raise ToolError(f"{path.name} is not an Engineering Data material library")
    if '"""' in text or "\\" in text:
        raise ToolError(f"{path.name} contains a backslash or triple quotes; it cannot be embedded")
    lib = Library(path, text, hashlib.sha256(raw).hexdigest())
    for m in _MAT.finditer(text):
        n = _NAME.search(m.group(0))
        if n:
            lib.blocks[_unesc(n.group(1)).strip()] = m.group(0)
    if COPPER_NAME not in lib.blocks:
        raise ToolError(f"{path.name}: material '{COPPER_NAME}' is missing")
    variants: dict[str, set] = {}
    for name in lib.blocks:
        base, variant, key = split_name(name)
        if variant:
            variants.setdefault(base, set()).add(variant)
            if base not in lib.by_key.setdefault(key, []):
                lib.by_key[key].append(base)
    bad = sorted(b for b, v in variants.items() if v != {"ORTHO", "ISO"})
    if bad:
        raise ToolError(f"{path.name}: materials without both _Ortho and _Iso: {bad}")
    if not lib.by_key:
        raise ToolError(f"{path.name}: no laminate material (<Model>_RC<nn>_Ortho / _Iso) found")
    return lib


def stale_note(lib: Library) -> str | None:
    """The workbook next to the XML is newer than the XML -> the converter should be run again."""
    tool = Path(__file__).resolve().parents[1]
    try:
        if tool in lib.path.resolve().parents:
            return (f"{lib.path.name} is the reference copy inside the tool folder and may be out of date: "
                    f"point inputs.material_library.path at the file in the 'Material vendor' folder of the "
                    f"Suppliers share (next to {WORKBOOK_NAME})")
    except OSError:
        pass
    wb = lib.path.parent / WORKBOOK_NAME
    try:
        if wb.is_file() and wb.stat().st_mtime > lib.path.stat().st_mtime + 2:
            return (f"{WORKBOOK_NAME} is newer than {lib.path.name}: run Update_PCB_Material_Library "
                    f"next to it if material data was changed")
    except OSError:
        pass
    return None


def why_missing(lib: Library, written: str) -> str:
    """Text of the conversion report about a material that is not in the XML."""
    rep = lib.path.parent / REPORT_NAME
    key = norm(written)
    if rep.is_file():
        lines = rep.read_text(encoding="utf-8", errors="replace").splitlines()
        for i, l in enumerate(lines):
            m = re.match(r"\*\*(.+?)\*\*", l)
            if m and split_name(m.group(1))[2] == key:
                why = [x[2:] for x in lines[i + 1:i + 12] if x.startswith("- ")]
                stop = next((j for j, x in enumerate(lines[i + 1:i + 12]) if not x.startswith("- ")), len(why))
                if "NOT in the library" in "\n".join(lines[:i]):
                    return (f" The workbook has {m.group(1)} but it was left out of the XML: "
                            f"{'; '.join(why[:stop])}. See {rep.name}.")
        return f" It is not in the workbook either (see {rep.name}); the material owner has to add it."
    return ""


def subset_xml(lib: Library, bases: list[str]) -> str:
    """Engineering Data XML with only these laminates (_Ortho and _Iso) and the copper."""
    keep = []
    for b in bases:
        keep += [b + "_Ortho", b + "_Iso"]
    keep.append(COPPER_NAME)
    missing = [n for n in keep if n not in lib.blocks]
    if missing:
        raise ToolError(f"{lib.path.name}: materials not found: {missing}")
    first = _MAT.search(lib.text)
    last = None
    for last in _MAT.finditer(lib.text):
        pass
    return lib.text[:first.start()] + "".join(lib.blocks[n] for n in keep) + lib.text[last.end():]
