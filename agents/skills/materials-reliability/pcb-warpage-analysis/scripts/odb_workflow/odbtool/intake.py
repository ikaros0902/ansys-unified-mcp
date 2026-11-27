"""Intake: find the stackup inside vendor / design tables whatever their layout.

Detection rules (documented in docs/02_input_standard.md and docs/08_vendor_table_formats.md):
  * kind column  = the column with the most cells reading copper / pp / p.p / prepreg / core
  * name column  = the column with the most cells reading TOP / BOT / L<n>
  * a row is copper if the kind column says copper OR the name column holds a copper name;
    a row is dielectric if the kind column says pp / prepreg / core / dielectric;
    solder mask rows are never part of the stackup
  * the stackup = the longest run of consecutive classified rows that starts and ends
    with copper and alternates copper / dielectric (consecutive dielectric rows between
    two coppers are merged into one dielectric, after confirmation)
  * thickness column = header match against the name the user gave (all words must
    match); anything less certain is asked
  * material column (design table) = the column whose dielectric cells match the
    material library keys
Copper layers get the FR4 material of the adjacent prepreg (resin fills the copper
gaps from the prepreg).  Two different prepregs or no prepreg next to a copper layer
-> asked (typical case: the N+M lamination layer).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import matlib
from .asker import Asker, Question
from .tables import cell, ncols, read_workbook
from .util import ToolError, col_letter, norm_material, norm_token, to_float, words

KIND_TOKENS = {"copper": "cu", "cu": "cu",
               "pp": "prepreg", "prepreg": "prepreg", "prepeg": "prepreg", "bondply": "prepreg",
               "core": "core", "laminate": "core",
               "dielectric": "diel", "diel": "diel"}
MASK_TOKENS = {"soldermask", "sm", "mask", "coverlay", "solderresist"}
NAME_RE = re.compile(r"^(top|bot|bottom|l\d{1,3}|layer\d{1,3}|lay\d{1,3})$")
FUNC_TOKENS = {"sig", "signal", "gnd", "ground", "pwr", "power", "mix", "mixed"}
FOIL_RE = re.compile(r"\b(std|rtf|hvlp\d?|vlp|hte|ulp)\b", re.I)
GLASS_RE = re.compile(r"(^|\b)(pp|core)\s*\(|^\d{3,4}\s*([x*]\s*\d)?", re.I)


@dataclass
class SheetRow:
    r: int                    # 0-based grid row
    kind: str                 # cu | prepreg | core | diel
    name: str | None = None   # copper name as written in the sheet


@dataclass
class StackTable:
    source: str               # file name
    sheet: str
    grid: list
    kind_col: int | None
    name_col: int | None
    groups: list[list[SheetRow]]   # one group per stackup layer (dielectric groups may hold >1 row)

    @property
    def first_row(self) -> int:
        return self.groups[0][0].r

    def n_cu(self) -> int:
        return sum(1 for g in self.groups if g[0].kind == "cu")

    def rows_label(self) -> str:
        return f"rows {self.groups[0][0].r + 1}-{self.groups[-1][-1].r + 1}"


@dataclass
class Layer:
    seq: int
    kind: str                         # 'copper' | 'dielectric'
    thickness_mil: float
    material: str = ""                # normalized FR4 key (copper: paired FR4)
    material_raw: str = ""
    design_fr4: str = ""              # copper only: FR4 written on the copper row of the design table
    diel_type: str = ""               # prepreg | core | diel
    ecad_name: str = ""               # design-table copper name (TOP, L2 ... BOT)
    vendor_sheet_name: str = ""
    vendor_odb_name: str = ""
    copper_oz: str = ""
    func: str = ""
    foil: str = ""
    glass: str = ""
    vendor_row: str = ""
    design_row: str = ""
    design_thickness_mil: float | None = None
    coverage: float | None = None     # 0..1, copper only (filled by coverage step)
    coverage_region: dict = field(default_factory=dict)

    @property
    def layer_name(self) -> str:      # body / CSV name
        return f"Layer_{self.seq}_{self.material}"

    @property
    def odb_name(self) -> str:        # ODB++ matrix name
        return f"LAYER_{self.seq}_{self.material}"


@dataclass
class IntakeResult:
    layers: list[Layer]
    notes: list[tuple[str, str]]      # (level, text) level: INFO | DIFF | WARN
    sources: list[str]
    material_choice: dict = field(default_factory=dict)   # EM370Z -> 'EM-370(Z)_RC51' (library material)


# ---------------------------------------------------------------- table detection
def _kind_of(v) -> str | None:
    return KIND_TOKENS.get(norm_token(v))


def _is_name(v) -> bool:
    return bool(NAME_RE.match(norm_token(v)))


def _best_col(grid, pred, min_hits=3) -> int | None:
    best, best_n = None, 0
    for c in range(ncols(grid)):
        n = sum(1 for row in grid if c < len(row) and pred(row[c]))
        if n > best_n:
            best, best_n = c, n
    return best if best_n >= min_hits else None


def find_stack_table(source: str, sheet: str, grid: list) -> StackTable | None:
    kind_col = _best_col(grid, lambda v: _kind_of(v) is not None)
    name_col = _best_col(grid, _is_name)
    if kind_col is None and name_col is None:
        return None
    if name_col == kind_col:
        name_col = None
    cls = []
    for r, row in enumerate(grid):
        if any(norm_token(v) in MASK_TOKENS for v in row if isinstance(v, str)):
            cls.append(None)
            continue
        k = _kind_of(cell(grid, r, kind_col)) if kind_col is not None else None
        nm = cell(grid, r, name_col) if name_col is not None else None
        if k is None and nm is not None and _is_name(nm):
            k = "cu"
        if k == "cu":
            cls.append(SheetRow(r, "cu", str(nm).strip() if nm is not None and _is_name(nm) else None))
        elif k:
            cls.append(SheetRow(r, k))
        else:
            cls.append(None)
    best = None
    run: list[SheetRow] = []
    for item in cls + [None]:
        if item is not None:
            run.append(item)
            continue
        groups = _group(run)
        if groups and (best is None or len(groups) > len(best)):
            best = groups
        run = []
    if not best:
        return None
    return StackTable(source, sheet, grid, kind_col, name_col, best)


def _group(run: list[SheetRow]) -> list[list[SheetRow]] | None:
    while run and run[0].kind != "cu":
        run = run[1:]
    while run and run[-1].kind != "cu":
        run = run[:-1]
    if sum(1 for x in run if x.kind == "cu") < 2:
        return None
    groups: list[list[SheetRow]] = []
    for x in run:
        if x.kind == "cu":
            if groups and groups[-1][0].kind == "cu":
                return None                       # two coppers in a row: not a stackup
            groups.append([x])
        elif groups and groups[-1][0].kind != "cu":
            groups[-1].append(x)                  # consecutive dielectric rows
        else:
            groups.append([x])
    return groups


def locate_table(path, role: str, expected_cu: int, cfg_sheet: str | None, asker: Asker,
                 notes: list) -> StackTable:
    book = read_workbook(path)
    found = []
    for sheet, grid in book.items():
        t = find_stack_table(path.name, sheet, grid)
        if t:
            found.append(t)
    if cfg_sheet:
        sel = [t for t in found if t.sheet == cfg_sheet]
        if not sel:
            raise ToolError(f"{role}: sheet {cfg_sheet!r} in {path.name} has no recognisable stackup "
                            f"(sheets: {list(book)})")
        t = sel[0]
    else:
        match = [t for t in found if t.n_cu() == expected_cu]
        if len(match) == 1:
            t = match[0]
        elif not found:
            raise ToolError(f"{role}: no stackup table found in {path.name} (sheets: {list(book)}). "
                            "See docs/08_vendor_table_formats.md")
        else:
            cands = match or found
            a = asker.choose(Question(
                f"{role}.sheet",
                f"{role}: which sheet of {path.name} holds the stackup? The ODB++ has {expected_cu} copper layers.",
                [(c.sheet, f"{c.n_cu()} copper layers, {c.rows_label()}") for c in cands]))
            t = next(c for c in cands if c.sheet == a)
    if t.n_cu() != expected_cu:
        raise ToolError(f"{role}: sheet {t.sheet!r} has {t.n_cu()} copper layers, the ODB++ has {expected_cu}. "
                        "Layer counts must match (layers are matched by order).")
    merged = [g for g in t.groups if len(g) > 1]
    if merged:
        txt = "; ".join(f"rows {', '.join(str(x.r + 1) for x in g)}" for g in merged)
        a = asker.choose(Question(
            f"{role}.merge_dielectric_rows",
            f"{role}: {len(merged)} places have several dielectric rows between two copper layers ({txt}). "
            "Merge each group into ONE dielectric layer (thicknesses added)?",
            [("yes", "merge (one PP layer per copper pair)"), ("no", "stop")]))
        if a != "yes":
            raise ToolError(f"{role}: stopped - dielectric rows not merged")
    notes.append(("INFO", f"{role}: {t.source} / sheet '{t.sheet}', {t.rows_label()}, "
                          f"kind column {col_letter(t.kind_col) if t.kind_col is not None else '-'}, "
                          f"name column {col_letter(t.name_col) if t.name_col is not None else '-'}"))
    return t


# ---------------------------------------------------------------- columns
def header_text(t: StackTable, c: int, depth: int = 12) -> str:
    parts = []
    for r in range(max(0, t.first_row - depth), t.first_row):
        v = cell(t.grid, r, c)
        if isinstance(v, str):
            parts.append(v.replace("\n", " "))
    return " | ".join(parts)


def _numeric_everywhere(t: StackTable, c: int) -> bool:
    return all(to_float(cell(t.grid, x.r, c)) is not None for g in t.groups for x in g)


def _group_value(t: StackTable, g: list[SheetRow], c: int) -> float:
    return sum(to_float(cell(t.grid, x.r, c)) for x in g)


def _unit_of(t: StackTable, c: int) -> str | None:
    w = set(words(header_text(t, c)))
    if "mil" in w or "mils" in w:
        return "mil"
    if "um" in w or "micron" in w or "µm" in header_text(t, c):
        return "um"
    if "mm" in w:
        return "mm"
    return None


def pick_thickness_column(t: StackTable, role: str, requested: str | None, unit_cfg: str | None,
                          asker: Asker, notes: list, required: bool = True) -> tuple[int, float] | None:
    cands = [c for c in range(ncols(t.grid)) if _numeric_everywhere(t, c)]
    if not cands:
        if required:
            raise ToolError(f"{role}: no column has a number on every stackup row of sheet '{t.sheet}'")
        return None
    letter_req = requested.strip().upper() if requested and re.fullmatch(r"[A-Za-z]{1,2}", requested.strip()) else None
    full, scored = [], []
    for c in cands:
        hw = set(words(header_text(t, c)))
        if letter_req:
            sc = 1.0 if col_letter(c) == letter_req else 0.0
        elif requested:
            rw = set(words(requested))
            sc = len(rw & hw) / len(rw) if rw else 0.0
        else:
            sc = 1.0 if any(w.startswith("thick") for w in hw) else 0.0
        scored.append((sc, c))
        if sc == 1.0 and requested:
            full.append(c)
    scored.sort(key=lambda x: (-x[0], x[1]))
    if len(full) == 1:
        c = full[0]
    else:
        if not requested and not required:
            return None
        opts = []
        for sc, c in scored:
            if requested and sc == 0 and len(scored) > 6:
                continue
            tot = sum(_group_value(t, g, c) for g in t.groups)
            opts.append((col_letter(c), f"header '{header_text(t, c)[:70]}', first values "
                         f"{[round(_group_value(t, g, c), 3) for g in t.groups[:3]]}, sum {tot:.2f}"))
        why = (f"several columns match '{requested}'" if len(full) > 1 else
               f"no column header contains all words of '{requested}'" if requested else
               "no thickness column was given in the config")
        a = asker.choose(Question(f"{role}.thickness_column",
                                  f"{role}: which column of sheet '{t.sheet}' is the thickness to use? ({why})",
                                  opts))
        c = next(c for _, c in scored if col_letter(c) == a)
    unit = unit_cfg or _unit_of(t, c)
    if unit is None:
        unit = asker.choose(Question(f"{role}.thickness_unit",
                                     f"{role}: unit of column {col_letter(c)} ('{header_text(t, c)[:60]}')?",
                                     [("mil", "mil"), ("um", "micrometre"), ("mm", "millimetre")]))
    factor = {"mil": 1.0, "um": 1 / 25.4, "mm": 1000 / 25.4}[unit]
    notes.append(("INFO", f"{role}: thickness column {col_letter(c)} '{header_text(t, c)[:80]}', unit {unit}"))
    return c, factor


def _best_value_col(t: StackTable, rows: list[SheetRow], pred) -> int | None:
    best, best_n = None, 0
    for c in range(ncols(t.grid)):
        n = sum(1 for x in rows if pred(cell(t.grid, x.r, c)))
        if n > best_n:
            best, best_n = c, n
    return best if best_n >= max(1, len(rows) // 2) else None


def pick_material_column(t: StackTable, role: str, requested: str | None, library_keys: set[str],
                         asker: Asker, notes: list) -> int:
    diel_rows = [x for g in t.groups if g[0].kind != "cu" for x in g]
    if requested:
        rw = set(words(requested))
        hits = [c for c in range(ncols(t.grid)) if rw and rw <= set(words(header_text(t, c)))]
        if len(hits) == 1:
            return hits[0]
    if library_keys:
        pred = lambda v: isinstance(v, str) and norm_material(v) in library_keys   # noqa: E731
    else:
        pred = lambda v: isinstance(v, str) and re.match(r"^[A-Za-z]{1,6}[- ]?\d", v.strip()) is not None  # noqa: E731
    c = _best_value_col(t, diel_rows, pred)
    if c is None:
        opts = [(col_letter(c), f"header '{header_text(t, c)[:60]}', values "
                 f"{[cell(t.grid, x.r, c) for x in diel_rows[:3]]}")
                for c in range(ncols(t.grid)) if any(isinstance(cell(t.grid, x.r, c), str) for x in diel_rows)]
        a = asker.choose(Question(f"{role}.material_column",
                                  f"{role}: which column of sheet '{t.sheet}' holds the dielectric material name?",
                                  opts))
        c = next(i for i in range(ncols(t.grid)) if col_letter(i) == a)
    notes.append(("INFO", f"{role}: material column {col_letter(c)} '{header_text(t, c)[:60]}'"))
    return c


def _text(t, r, c) -> str:
    v = cell(t.grid, r, c) if c is not None else None
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:g}"
    return str(v).replace("\n", " ").strip()


# ---------------------------------------------------------------- main
def run_intake(cfg: dict, odb_copper: list[str], asker: Asker, log) -> IntakeResult:
    from pathlib import Path
    notes: list[tuple[str, str]] = []
    n_cu = len(odb_copper)
    lib_keys = set()
    lib_path = cfg["inputs"].get("material_library", {}).get("path")
    lib = None
    if lib_path:
        lib = matlib.load(Path(lib_path))
        lib_keys = lib.keys
        notes.append(("INFO", f"material library: {Path(lib_path).name} (sha256 {lib.sha[:12]}), "
                              f"materials {sorted(b for v in lib.by_key.values() for b in v)}"))
        stale = matlib.stale_note(lib)
        if stale:
            notes.append(("WARN", stale))

    vcfg = cfg["inputs"]["vendor_stackup"]
    dcfg = cfg["inputs"]["design_material_table"]
    vt = locate_table(Path(vcfg["path"]), "vendor_stackup", n_cu, vcfg.get("sheet"), asker, notes)
    dt = locate_table(Path(dcfg["path"]), "design_material_table", n_cu, dcfg.get("sheet"), asker, notes)
    if len(vt.groups) != len(dt.groups):
        raise ToolError(f"vendor stackup has {len(vt.groups)} layers, design table {len(dt.groups)}")

    vc, vfac = pick_thickness_column(vt, "vendor_stackup", vcfg.get("thickness_column"),
                                     vcfg.get("thickness_unit"), asker, notes)
    dthick = pick_thickness_column(dt, "design_material_table", dcfg.get("thickness_column"),
                                   dcfg.get("thickness_unit"), asker, notes, required=False) \
        if dcfg.get("thickness_column") else None
    mc = pick_material_column(dt, "design_material_table", dcfg.get("material_column"), lib_keys, asker, notes)
    vmc = None
    if lib_keys:
        vrows = [x for g in vt.groups if g[0].kind != "cu" for x in g]
        vmc = _best_value_col(vt, vrows, lambda v: isinstance(v, str) and norm_material(v) in lib_keys)

    cu_rows = [x for g in dt.groups if g[0].kind == "cu" for x in g]
    di_rows = [x for g in dt.groups if g[0].kind != "cu" for x in g]
    oz_c = _best_value_col(dt, cu_rows, lambda v: isinstance(v, str) and "oz" in v.lower())
    fn_c = _best_value_col(dt, cu_rows, lambda v: norm_token(v) in FUNC_TOKENS)
    fo_c = _best_value_col(dt, cu_rows, lambda v: isinstance(v, str) and FOIL_RE.search(v) is not None)
    gl_c = _best_value_col(dt, di_rows, lambda v: isinstance(v, str) and GLASS_RE.search(v.strip()) is not None)
    if oz_c is None:
        vcu = [x for g in vt.groups if g[0].kind == "cu" for x in g]
        oz_v = _best_value_col(vt, vcu, lambda v: isinstance(v, str) and "oz" in v.lower())
    else:
        oz_v = None

    layers: list[Layer] = []
    cu_i = 0
    for i, (vg, dg) in enumerate(zip(vt.groups, dt.groups), 1):
        vk, dk = vg[0].kind, dg[0].kind
        if (vk == "cu") != (dk == "cu"):
            raise ToolError(f"layer {i}: vendor row {vg[0].r + 1} is {vk}, design row {dg[0].r + 1} is {dk}")
        th = _group_value(vt, vg, vc) * vfac
        if th <= 0:
            raise ToolError(f"layer {i}: thickness {th} mil at vendor row {vg[0].r + 1}")
        L = Layer(seq=i, kind="copper" if vk == "cu" else "dielectric", thickness_mil=round(th, 6),
                  vendor_row=",".join(str(x.r + 1) for x in vg), design_row=",".join(str(x.r + 1) for x in dg))
        if dthick:
            L.design_thickness_mil = round(_group_value(dt, dg, dthick[0]) * dthick[1], 6)
        if vk == "cu":
            L.ecad_name = dg[0].name or f"L{cu_i + 1}"
            L.vendor_sheet_name = vg[0].name or ""
            L.vendor_odb_name = odb_copper[cu_i]
            L.copper_oz = _text(dt, dg[0].r, oz_c) or _text(vt, vg[0].r, oz_v)
            L.func = _text(dt, dg[0].r, fn_c).upper()
            L.foil = _text(dt, dg[0].r, fo_c)
            # a library material written on the copper row itself is the design team's explicit pairing
            on_row = {norm_material(_text(dt, x.r, mc)) for x in dg} & lib_keys
            if len(on_row) == 1:
                L.design_fr4 = on_row.pop()
            cu_i += 1
        else:
            mats = {norm_material(_text(dt, x.r, mc)) for x in dg} - {""}
            raws = [_text(dt, x.r, mc) for x in dg if _text(dt, x.r, mc)]
            if len(mats) != 1:
                opts = sorted(lib_keys or mats) or ["?"]
                a = asker.choose(Question(f"dielectric_material.Layer_{i}",
                                          f"Layer_{i} (design rows {L.design_row}): material is "
                                          f"{'missing' if not mats else 'ambiguous ' + str(sorted(mats))}. Which FR4?",
                                          [(m, "") for m in opts]))
                mats = {norm_material(a)}
            L.material = mats.pop()
            L.material_raw = raws[0] if raws else L.material
            if lib_keys and L.material not in lib_keys:
                raise ToolError(f"Layer_{i}: material {L.material_raw!r} (design row {L.design_row}) is not in "
                                f"the material library {sorted(lib_keys)}." + matlib.why_missing(lib, L.material_raw))
            L.diel_type = dk if dk != "diel" else (vk if vk != "diel" else "diel")
            L.glass = " + ".join(_text(dt, x.r, gl_c) for x in dg if _text(dt, x.r, gl_c))
            if vmc is not None:
                vm = {norm_material(_text(vt, x.r, vmc)) for x in vg} - {""}
                if vm and vm != {L.material}:
                    notes.append(("DIFF", f"Layer_{i}: vendor material {sorted(vm)} vs design {L.material} "
                                          f"(design table is used)"))
            if vk != dk and "diel" not in (vk, dk):
                notes.append(("DIFF", f"Layer_{i}: vendor says {vk}, design says {dk} (design is used)"))
        if L.design_thickness_mil is not None and abs(L.design_thickness_mil - L.thickness_mil) > 1e-6:
            notes.append(("DIFF", f"Layer_{i}: vendor {L.thickness_mil:g} mil vs design {L.design_thickness_mil:g} mil "
                                  "(vendor is used)"))
        layers.append(L)

    pair_copper_materials(layers, asker, notes, sorted(lib_keys))
    names_differ = [(L.ecad_name, L.vendor_sheet_name, L.vendor_odb_name) for L in layers if L.kind == "copper"
                    and len({norm_token(L.ecad_name), norm_token(L.vendor_sheet_name or L.ecad_name)}) > 1]
    if names_differ:
        notes.append(("INFO", f"copper names differ between sources for {len(names_differ)} layers "
                              f"(matched by order), e.g. {names_differ[:3]}"))
    total = sum(L.thickness_mil for L in layers)
    if not 10 <= total <= 1000:
        a = asker.choose(Question("vendor_stackup.total_thickness_ok",
                                  f"Total thickness is {total:.2f} mil, outside 10..1000 mil. Unit wrong?",
                                  [("yes", "the value is right, continue"), ("no", "stop")]))
        if a != "yes":
            raise ToolError("stopped: total thickness not confirmed")
    notes.append(("INFO", f"total thickness {total:.3f} mil = {total * 0.0254:.4f} mm, {len(layers)} layers"))
    choice = {}
    if lib is not None:
        for L in layers:
            if L.material in choice:
                continue
            bases = lib.by_key.get(L.material, [])
            if len(bases) > 1:
                a = asker.choose(Question(f"material_variant.{L.material}",
                                          f"The material library has {len(bases)} materials for {L.material} "
                                          f"(different resin content). Which one is used on this board?",
                                          [(b, "") for b in bases], allow_free_text=False))
                bases = [b for b in bases if b == a] or [a]
            if bases:
                choice[L.material] = bases[0]
        notes.append(("INFO", "library materials of this board: " + ", ".join(choice.values())))
    return IntakeResult(layers, notes, [str(vcfg["path"]), str(dcfg["path"])], choice)


def pair_copper_materials(layers: list[Layer], asker: Asker, notes: list, lib: list[str]) -> None:
    """Copper layer FR4: the design table's copper row when it states one, else the material of
    the adjacent prepreg; ambiguous cases are asked."""
    for i, L in enumerate(layers):
        if L.kind != "copper":
            continue
        nb = [layers[j] for j in (i - 1, i + 1) if 0 <= j < len(layers)]
        pp = {n.material for n in nb if n.diel_type == "prepreg"}
        if L.design_fr4:
            L.material = L.design_fr4
            if len(pp) == 1 and pp != {L.material}:
                notes.append(("DIFF", f"copper {L.ecad_name} (Layer_{L.seq}): design table copper row says "
                                      f"{L.material}, the adjacent prepreg is {sorted(pp)[0]} (design table is used)"))
            elif len(pp) != 1:
                notes.append(("INFO", f"copper {L.ecad_name} (Layer_{L.seq}) FR4 = {L.material} "
                                      f"(stated on the copper row of the design table, design row {L.design_row})"))
            continue
        if len(pp) == 1:
            L.material = pp.pop()
            continue
        if not pp:
            why = "no prepreg next to it (" + ", ".join(f"Layer_{n.seq} {n.diel_type} {n.material}" for n in nb) + ")"
        else:
            why = ("prepregs of different material on both sides ("
                   + ", ".join(f"Layer_{n.seq} {n.material}" for n in nb) + ") - typical for an N+M lamination layer")
        opts = sorted({n.material for n in nb} | set(lib))
        a = asker.choose(Question(f"copper_fr4.{L.ecad_name}",
                                  f"Copper {L.ecad_name} (Layer_{L.seq}): which FR4 material pairs with this "
                                  f"copper layer? Reason for asking: {why}.",
                                  [(m, "") for m in opts], allow_free_text=False))
        L.material = norm_material(a)
        notes.append(("INFO", f"copper {L.ecad_name} (Layer_{L.seq}) FR4 = {L.material} (answer: {why})"))


def load_library_keys(path) -> set[str]:
    return matlib.load(path).keys
