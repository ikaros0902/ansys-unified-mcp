# -*- coding: utf-8 -*-
"""Build the Engineering Data material library (XML, ANSYS 2025 R1 format) from the sheet
`Table` of `00_PCB Material Properties Library.xlsx`.

    python Update_PCB_Material_Library.py                 workbook next to this script
    python Update_PCB_Material_Library.py <workbook.xlsx> [--out <folder>] [--check]

Writes, next to the workbook (or into --out):
    PCB_Material_Library.xml          every complete laminate as <Model>_RC<nn>_Ortho and
                                      <Model>_RC<nn>_Iso, plus `Copper for Warpage`
    PCB_Material_Library_report.md    which materials are in, which are not and why,
                                      every assumption and default
    archive\\                          the previous XML / report, when the content changed

--check reads and reports only; nothing is written.
Exit code 0 = done, 3 = the workbook cannot be read.

This file is standalone (CPython 3 + openpyxl). The rules it applies are written in
README_Material_Library.md; change them there and here together.
"""
from __future__ import print_function

import datetime
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid

WORKBOOK_NAME = "00_PCB Material Properties Library.xlsx"
SHEET_NAME = "Table"
XML_NAME = "PCB_Material_Library.xml"
REPORT_NAME = "PCB_Material_Library_report.md"

# ---------------- Rules (agreed 2026-11-25) ----------------
EZ_RATIO = 0.6            # Ez = EZ_RATIO * mean(Ex, Ey) when the library has no Z modulus curve
T_START = 30.0            # every curve must reach down to this temperature [C]
T_EXTEND_MAX = 50.0       # a curve that starts at <= this is extended flat down to T_START
DEFAULT_K = 0.59          # W/m-K, used when the library has no Thermal Conductivity row
DEFAULT_CP = 1100.0       # J/kg-K, used when the library has no Specific Heat row
COPPER = {"name": "Copper for Warpage", "e": 110.0e9, "nu": 0.34, "dens": 8960.0, "k": 400.0, "cp": 380.0,
          "cte": 17.0e-6}

STRESS_UNITS = {"pa": 1.0, "kpa": 1.0e3, "mpa": 1.0e6, "gpa": 1.0e9}
DENS_UNITS = {"kg/m^3": 1.0, "kg/m3": 1.0, "g/cm^3": 1000.0, "g/cm3": 1000.0, "g/cc": 1000.0}
K_UNITS = {"w/m-k": 1.0, "w/mk": 1.0, "w/m.k": 1.0, "w/m-c": 1.0, "w/m/k": 1.0, "w/(m-k)": 1.0}
CP_UNITS = {"j/kg-k": 1.0, "j/kgk": 1.0, "j/kg.k": 1.0, "j/kg-c": 1.0, "j/kg/k": 1.0, "j/(kg-k)": 1.0,
            "j/g-k": 1000.0, "j/g-c": 1000.0}
CTE_UNITS = {"ppm/c": 1.0e-6, "ppm/k": 1.0e-6, "ppm": 1.0e-6, "um/m-c": 1.0e-6, "1/c": 1.0, "1/k": 1.0,
             "/c": 1.0, "/k": 1.0}


class InputError(Exception):
    pass


# ============================================================
# 1) Read the workbook
# ============================================================
def _open_rows(path):
    """Rows of sheet `Table` as lists. Falls back to a copy made by a running Excel when the
    file is locked (OneDrive workbooks that are open in Excel cannot be read directly)."""
    try:
        import openpyxl
    except ImportError:
        raise InputError("Python package 'openpyxl' is missing. Run:  python -m pip install openpyxl")

    def load(p):
        wb = openpyxl.load_workbook(p, data_only=True, read_only=True)
        if SHEET_NAME not in wb.sheetnames:
            raise InputError("sheet '%s' not found in %s (sheets: %s)" % (SHEET_NAME, os.path.basename(p), wb.sheetnames))
        rows = [list(r) for r in wb[SHEET_NAME].iter_rows(values_only=True)]
        wb.close()
        return rows

    if not os.path.isfile(path):
        raise InputError("workbook not found: %s" % path)
    try:
        return load(path), path
    except PermissionError:
        pass
    tmp = os.path.join(tempfile.mkdtemp(prefix="pcb_matlib_"), os.path.basename(path))
    ps = ("$n=[IO.Path]::GetFileName('%s'); $xl=[Runtime.InteropServices.Marshal]::GetActiveObject('Excel.Application'); "
          "$wb=$xl.Workbooks | Where-Object {$_.Name -eq $n}; if(-not $wb){exit 5}; $wb.SaveCopyAs('%s')"
          % (path.replace("'", "''"), tmp.replace("'", "''")))
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True, capture_output=True, timeout=120)
        rows = load(tmp)
        print("NOTE: the workbook is open in Excel; a copy of its CURRENT state (also unsaved edits) was read.")
        return rows, tmp
    except InputError:
        raise
    except Exception:
        raise InputError("the workbook is locked by another program and could not be copied. "
                         "Close it in Excel and run again: %s" % path)


def _norm_head(v):
    return re.sub(r"[^a-z0-9]", "", str(v or "").lower())


def read_table(path):
    rows, read_from = _open_rows(path)
    if not rows:
        raise InputError("sheet '%s' is empty" % SHEET_NAME)
    head = [_norm_head(v) for v in rows[0]]
    want = {"vendor": "vendor", "model": "modelname", "rc": "resincontent", "glass": "glassfiber", "item": "items",
            "unit": "unit", "axis": "axis", "temp": "temperature", "value": "value", "remark": "remark"}
    col = {}
    for k, h in want.items():
        if h in head:
            col[k] = head.index(h)
        elif k in ("rc", "glass", "remark", "vendor"):
            col[k] = None
        else:
            raise InputError("column '%s' not found in the header row of sheet '%s'" % (h, SHEET_NAME))
    out = []
    for i, r in enumerate(rows[1:], 2):
        def g(k):
            c = col[k]
            return r[c] if c is not None and c < len(r) else None
        if g("model") in (None, "") or g("item") in (None, ""):
            continue
        out.append({"row": i, "vendor": g("vendor"), "model": str(g("model")).strip(), "rc": g("rc"),
                    "glass": g("glass"), "item": str(g("item")).strip(), "unit": g("unit"), "axis": g("axis"),
                    "temp": g("temp"), "value": g("value"), "remark": g("remark")})
    with open(read_from, "rb") as fh:
        sha = hashlib.sha256(fh.read()).hexdigest()
    return out, sha


# ============================================================
# 2) Interpret one material
# ============================================================
def ascii_clean(s):
    s = "".join(ch for ch in str(s if s is not None else "") if 32 <= ord(ch) < 127)
    s = re.sub(r"\(\s*\)", "", s)
    return re.sub(r"\s+", " ", s).strip()


def norm_key(s):
    return "".join(c for c in str(s) if c.isalnum()).upper()


def rc_label(v):
    if v is None or str(v).strip() == "":
        return "NA"
    s = str(v).strip().replace("%", "")
    try:
        x = float(s)
    except ValueError:
        return norm_key(s) or "NA"
    if x <= 1.0:
        x *= 100.0
    return ("%g" % round(x, 1)).replace(".", "p")


def _num(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).strip())
    except (ValueError, TypeError):
        return None


def _unit(v):
    u = str(v or "").strip().lower().replace(" ", "").replace("°", "").replace("·", ".")
    return u.replace("℃", "c").replace("*", ".")


def classify(item):
    s = item.lower()
    if s.startswith("cte") or "thermal expansion" in s:
        return "CTE"
    if "storage" in s:
        return "SM"
    if "young" in s:
        return "YM"
    if s.startswith("poi"):
        return "NU"
    if "density" in s:
        return "DENS"
    if "conductivity" in s:
        return "K"
    if "specific heat" in s or "heat capacity" in s:
        return "CP"
    if s.strip() == "tg" or s.startswith("tg"):
        return "TG"
    return None


def interp(x, xp, fp):
    if x <= xp[0]:
        return fp[0]
    if x >= xp[-1]:
        return fp[-1]
    for i in range(len(xp) - 1):
        if xp[i] <= x <= xp[i + 1]:
            t = (x - xp[i]) / float(xp[i + 1] - xp[i])
            return fp[i] + t * (fp[i + 1] - fp[i])
    return fp[-1]


def _t(x):
    return "%g" % x


def build_material(rows):
    """rows of one (model, RC) -> (data dict or None, problems, notes, ignored)."""
    problems, notes, ignored = [], [], []
    series = {}   # (prop, axis) -> {T: (value, row)}
    scal = {}     # prop -> [(T, value, row)]
    tg = []

    def put(prop, axis, T, val, row):
        d = series.setdefault((prop, axis), {})
        if T in d and abs(d[T][0] - val) > 1e-9 * max(1.0, abs(val)):
            problems.append("%s %s at %s C has two different values (rows %d and %d)" % (prop, axis, _t(T), d[T][1], row))
            return
        d[T] = (val, row)

    for r in rows:
        prop = classify(r["item"])
        if prop is None:
            ignored.append("row %d: item '%s' is not used" % (r["row"], ascii_clean(r["item"])))
            continue
        val = _num(r["value"])
        T = _num(r["temp"])
        if prop == "TG":
            if val is not None:
                tg.append(val)
            continue
        if val is None:
            problems.append("row %d: %s value '%s' is not a number" % (r["row"], r["item"], ascii_clean(r["value"])))
            continue
        u = _unit(r["unit"])
        table = {"CTE": CTE_UNITS, "SM": STRESS_UNITS, "YM": STRESS_UNITS, "DENS": DENS_UNITS, "K": K_UNITS,
                 "CP": CP_UNITS}.get(prop)
        if table is not None:
            if u not in table:
                problems.append("row %d: unit '%s' of %s is not known" % (r["row"], ascii_clean(r["unit"]), r["item"]))
                continue
            val *= table[u]
        if prop in ("NU", "DENS", "K", "CP"):
            scal.setdefault(prop, []).append((T if T is not None else 25.0, val, r["row"]))
            continue
        if T is None:
            problems.append("row %d: %s has no temperature" % (r["row"], r["item"]))
            continue
        ax = str(r["axis"] or "").strip().upper().replace(" ", "")
        if ax in ("", "X/Y", "XY", "X,Y"):
            axes = ["X", "Y"]
        elif ax in ("X", "Y", "Z"):
            axes = [ax]
        else:
            problems.append("row %d: axis '%s' is not X, Y, Z, X/Y or empty" % (r["row"], ascii_clean(r["axis"])))
            continue
        for a in axes:
            put(prop, a, T, val, r["row"])

    def curve(prop, a):
        d = series.get((prop, a), {})
        return dict((T, v[0]) for T, v in d.items())

    def one(prop, label, required):
        v = scal.get(prop)
        if not v:
            if required:
                problems.append("%s is missing" % label)
            return None
        vals = sorted(set(round(x[1], 12) for x in v))
        if len(vals) > 1:
            v = sorted(v)
            notes.append("%s: %d values given, the one at %s C is used" % (label, len(v), _t(v[0][0])))
        return sorted(v)[0][1]

    nu = one("NU", "Poisson's Ratio", True)
    dens = one("DENS", "Density", True)
    k = one("K", "Thermal Conductivity", False)
    cp = one("CP", "Specific Heat", False)
    if k is None:
        k = DEFAULT_K
        notes.append("Thermal Conductivity not in the library: default %g W/m-K" % DEFAULT_K)
    if cp is None:
        cp = DEFAULT_CP
        notes.append("Specific Heat not in the library: default %g J/kg-K" % DEFAULT_CP)

    def extend(pts, what):
        """Apply the low-temperature rule. Returns False when the curve is not usable."""
        t0 = min(pts)
        if t0 <= T_START:
            return True
        if t0 <= T_EXTEND_MAX:
            pts[T_START] = pts[t0]
            notes.append("%s starts at %s C: the value is copied to %s C" % (what, _t(t0), _t(T_START)))
            return True
        problems.append("%s starts at %s C; data at or below %s C is needed" % (what, _t(t0), _t(T_EXTEND_MAX)))
        return False

    # ---- modulus: Storage Modulus is E(T); Young's Modulus adds its own temperature point ----
    E = {}
    sm = dict((a, curve("SM", a)) for a in "XYZ")
    ym = dict((a, curve("YM", a)) for a in "XYZ")
    if not sm["X"] and not sm["Y"]:
        problems.append("Storage Modulus (modulus versus temperature) is missing for X / Y")
    else:
        for a, b in (("X", "Y"), ("Y", "X")):
            if not sm[a]:
                sm[a] = dict(sm[b])
                notes.append("Storage Modulus %s not in the library: E%s = E%s" % (a, a.lower(), b.lower()))
            if not ym[a] and ym[b]:
                ym[a] = dict(ym[b])
        for a in "XY":
            pts = dict(sm[a])
            for T, v in sorted(ym[a].items()):
                if T in pts:
                    if a == "X":
                        notes.append("Young's Modulus at %s C (%g MPa) not used: Storage Modulus has that point (%g MPa)"
                                     % (_t(T), v / 1e6, pts[T] / 1e6))
                else:
                    pts[T] = v
                    if a == "X":
                        notes.append("E at %s C is the Young's Modulus (%g MPa); the other points are Storage Modulus"
                                     % (_t(T), v / 1e6))
            if extend(pts, "E%s" % a.lower()):
                E[a] = pts
        if len(sm["Z"]) >= 2:
            pts = dict(sm["Z"])
            for T, v in ym["Z"].items():
                pts.setdefault(T, v)
            if extend(pts, "Ez"):
                E["Z"] = pts
        else:
            if sm["Z"] or ym["Z"]:
                notes.append("single Z modulus value is not a curve and is not used")
            notes.append("Ez not in the library: Ez = %g x mean(Ex, Ey)" % EZ_RATIO)

    # ---- CTE (instantaneous) ----
    C = {}
    ct = dict((a, curve("CTE", a)) for a in "XYZ")
    if not ct["X"] and not ct["Y"]:
        problems.append("CTE X / Y is missing")
    else:
        for a, b in (("X", "Y"), ("Y", "X")):
            if not ct[a]:
                ct[a] = dict(ct[b])
                notes.append("CTE %s not in the library: CTE %s = CTE %s" % (a, a, b))
    if not ct["Z"]:
        problems.append("CTE Z is missing")
    for a in "XYZ":
        if ct[a] and extend(ct[a], "CTE %s" % a):
            C[a] = ct[a]

    if problems:
        return None, problems, notes, ignored

    te = sorted(set(E["X"]) | set(E["Y"]) | set(E.get("Z", {})))

    def on(grid, pts):
        xs = sorted(pts)
        return [interp(T, xs, [pts[x] for x in xs]) for T in grid]

    ex, ey = on(te, E["X"]), on(te, E["Y"])
    mean = [(a + b) / 2.0 for a, b in zip(ex, ey)]
    ez = on(te, E["Z"]) if "Z" in E else [EZ_RATIO * m for m in mean]
    g2 = 2.0 * (1.0 + nu)
    tc = sorted(set(C["X"]) | set(C["Y"]) | set(C["Z"]))
    data = {"te": te, "ex": ex, "ey": ey, "ez": ez, "eiso": mean, "nu": nu,
            "gxy": [m / g2 for m in mean], "gyz": [z / g2 for z in ez],
            "tc": tc, "cx": on(tc, C["X"]), "cy": on(tc, C["Y"]), "cz": on(tc, C["Z"]),
            "dens": dens, "k": k, "cp": cp, "tg": tg[0] if tg else None}
    for i, T in enumerate(te):
        nyx, nzy, nzx = nu * ey[i] / ex[i], nu * ez[i] / ey[i], nu * ez[i] / ex[i]
        if 1.0 - nu * nyx - nu * nzy - nu * nzx - 2.0 * nyx * nzy * nu <= 0.0:
            notes.append("orthotropic stability check fails at %s C" % _t(T))
            break
    notes.append("data above the last point (E %s C, CTE %s C) is held constant" % (_t(te[-1]), _t(tc[-1])))
    return data, problems, notes, ignored


# ============================================================
# 3) Engineering Data XML (same layout as an ANSYS 2025 R1 export)
# ============================================================
def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def g(x):
    return repr(float(x))


def lst(vals):
    return ",".join(g(v) for v in vals)


INTERP = ('            <ParameterValue parameter="pa4" format="string">\n'
          '              <Data>Interpolation Options</Data>\n'
          '              <Qualifier name="AlgorithmType">Linear Multivariate (Qhull)</Qualifier>\n'
          '              <Qualifier name="Normalized">True</Qualifier>\n'
          '              <Qualifier name="Cached">True</Qualifier>\n'
          '              <Qualifier name="ExtrapolationType">Projection to the Bounding Box</Qualifier>\n'
          '              <Qualifier name="Localized Name">Interpolation Options</Qualifier>\n'
          '            </ParameterValue>\n')
NO_T = [7.88860905221012e-31]


def temp_param(vals, field=True):
    q = ""
    if field:
        hi, lo = ("Program Controlled", "Program Controlled") if vals == NO_T else (g(max(vals)), g(min(vals)))
        q = ('              <Qualifier name="Field Variable">Temperature</Qualifier>\n'
             '              <Qualifier name="Default Data">22</Qualifier>\n'
             '              <Qualifier name="Upper Limit">%s</Qualifier>\n'
             '              <Qualifier name="Lower Limit">%s</Qualifier>\n'
             '              <Qualifier name="Field Units">C</Qualifier>\n') % (hi, lo)
    return ('            <ParameterValue parameter="pa6" format="float">\n'
            '              <Data>%s</Data>\n'
            '              <Qualifier name="Variable Type">%s</Qualifier>\n'
            '              <Qualifier name="Localized Name">Temperature</Qualifier>\n%s'
            '            </ParameterValue>\n') % (lst(vals), ",".join(["Independent"] * len(vals)), q)


def dep(pid, vals, lname):
    return ('            <ParameterValue parameter="%s" format="float">\n'
            '              <Data>%s</Data>\n'
            '              <Qualifier name="Variable Type">%s</Qualifier>\n'
            '              <Qualifier name="Localized Name">%s</Qualifier>\n'
            '            </ParameterValue>\n') % (pid, lst(vals), ",".join(["Dependent"] * len(vals)), lname)


def prop(pid, quals, lname, body):
    q = "".join('            <Qualifier name="%s">%s</Qualifier>\n' % kv for kv in quals)
    return ('          <PropertyData property="%s">\n            <Data format="string">-</Data>\n%s'
            '            <Qualifier name="Localized Name">%s</Qualifier>\n%s          </PropertyData>\n'
            % (pid, q, lname, body))


def material_xml(name, desc, cls, color, parts):
    s = ['      <Material>\n        <BulkDetails>\n          <Name>%s</Name>\n' % esc(name),
         '          <Description>%s</Description>\n' % esc(desc),
         '          <Class>\n            <Name>%s</Name>\n          </Class>\n' % cls,
         '          <PropertyData property="pr0">\n            <Data format="string">-</Data>\n'
         '            <Qualifier name="Localized Name">Color</Qualifier>\n']
    for pid, val, ln in (("pa0", color[0], "Red"), ("pa1", color[1], "Green"), ("pa2", color[2], "Blue")):
        s.append('            <ParameterValue parameter="%s" format="float">\n              <Data>%d</Data>\n'
                 '              <Qualifier name="Variable Type">Dependent</Qualifier>\n'
                 '              <Qualifier name="Localized Name">%s</Qualifier>\n            </ParameterValue>\n'
                 % (pid, val, ln))
    s.append('            <ParameterValue parameter="pa3" format="string">\n              <Data>Appearance</Data>\n'
             '            </ParameterValue>\n          </PropertyData>\n')
    s.extend(parts)
    guid = str(uuid.uuid5(uuid.NAMESPACE_URL, "jabil/pcb_material_library/" + name))
    s.append('          <PropertyData property="pr6">\n            <Data format="string">-</Data>\n'
             '            <Qualifier name="guid">%s</Qualifier>\n'
             '            <Qualifier name="Localized Name">Material Unique Id</Qualifier>\n'
             '            <Qualifier name="Display">False</Qualifier>\n          </PropertyData>\n' % guid)
    s.append('          <PropertyData property="pr7">\n            <Data format="string">-</Data>\n'
             '            <Qualifier name="Temperature">Temperature:TEMP</Qualifier>\n'
             '            <Qualifier name="Localized Name">Field Variable</Qualifier>\n          </PropertyData>\n')
    s.append('        </BulkDetails>\n      </Material>\n')
    return "".join(s)


FVC = ("Field Variable Compatible", "Temperature")


def common_parts(dens, k, cp):
    return [prop("pr1", [FVC], "Density", INTERP + dep("pa5", [dens], "Density") + temp_param(NO_T)),
            prop("pr11", [("Behavior", "Isotropic"), FVC], "Isotropic Thermal Conductivity",
                 INTERP + dep("pa20", [k], "Thermal Conductivity") + temp_param(NO_T)),
            prop("pr12", [("Definition", "Constant Pressure"), FVC], "Specific Heat Constant Pressure",
                 INTERP + dep("pa21", [cp], "Specific Heat") + temp_param(NO_T))]


def iso_elastic(T, e, nu):
    n = len(T)
    bulk = [v / (3.0 * (1.0 - 2.0 * nu)) for v in e]
    shear = [v / (2.0 * (1.0 + nu)) for v in e]
    return prop("pr2", [("Behavior", "Isotropic"), ("Derive from", "Young's Modulus and Poisson's Ratio"), FVC],
                "Isotropic Elasticity",
                INTERP + dep("pa39", e, "Young's Modulus") + dep("pa40", [nu] * n, "Poisson's Ratio")
                + dep("pa41", bulk, "Bulk Modulus") + dep("pa42", shear, "Shear Modulus")
                + temp_param(T if n > 1 else NO_T))


def ortho_elastic(d):
    n = len(d["te"])
    nu = [d["nu"]] * n
    return prop("pr2", [("Behavior", "Orthotropic"), FVC], "Orthotropic Elasticity",
                INTERP + dep("pa30", d["ex"], "Young's Modulus X direction")
                + dep("pa31", d["ey"], "Young's Modulus Y direction")
                + dep("pa32", d["ez"], "Young's Modulus Z direction")
                + dep("pa33", nu, "Poisson's Ratio XY") + dep("pa34", nu, "Poisson's Ratio YZ")
                + dep("pa35", nu, "Poisson's Ratio XZ")
                + dep("pa36", d["gxy"], "Shear Modulus XY") + dep("pa37", d["gyz"], "Shear Modulus YZ")
                + dep("pa38", d["gyz"], "Shear Modulus XZ") + temp_param(d["te"]))


def ortho_cte(d):
    return prop("pr5", [("Definition", "Instantaneous"), ("Behavior", "Orthotropic")],
                "Orthotropic Instantaneous Coefficient of Thermal Expansion",
                dep("pa13", d["cx"], "Coefficient of Thermal Expansion X direction")
                + dep("pa14", d["cy"], "Coefficient of Thermal Expansion Y direction")
                + dep("pa15", d["cz"], "Coefficient of Thermal Expansion Z direction")
                + temp_param(d["tc"], field=False))


def iso_cte(T, a):
    return prop("pr5", [("Definition", "Instantaneous"), ("Behavior", "Isotropic")],
                "Isotropic Instantaneous Coefficient of Thermal Expansion",
                dep("pa16", a, "Coefficient of Thermal Expansion") + temp_param(T, field=False))


def unit(name, parts):
    u = "".join('            <Unit%s>\n              <Name>%s</Name>\n            </Unit>\n'
                % ((' power="%d"' % p) if p != 1 else "", n) for n, p in parts)
    return '          <Units name="%s">\n%s          </Units>\n' % (name, u)


_STRESS = unit("Stress", [("Pa", 1)])
_CTE = unit("InvTemp1", [("C", -1)])
PARAMS = [
    ("pa0", "Red", None), ("pa1", "Green", None), ("pa2", "Blue", None), ("pa3", "Material Property", None),
    ("pa4", "Options Variable", None),
    ("pa5", "Density", unit("Density", [("kg", 1), ("m", -3)])),
    ("pa6", "Temperature", unit("Temperature", [("C", 1)])),
    ("pa13", "Coefficient of Thermal Expansion X direction", _CTE),
    ("pa14", "Coefficient of Thermal Expansion Y direction", _CTE),
    ("pa15", "Coefficient of Thermal Expansion Z direction", _CTE),
    ("pa16", "Coefficient of Thermal Expansion", _CTE),
    ("pa20", "Thermal Conductivity", unit("Thermal Conductivity", [("W", 1), ("m", -1), ("C", -1)])),
    ("pa21", "Specific Heat", unit("Specific Heat Capacity", [("J", 1), ("kg", -1), ("C", -1)])),
    ("pa30", "Young's Modulus X direction", _STRESS), ("pa31", "Young's Modulus Y direction", _STRESS),
    ("pa32", "Young's Modulus Z direction", _STRESS),
    ("pa33", "Poisson's Ratio XY", None), ("pa34", "Poisson's Ratio YZ", None), ("pa35", "Poisson's Ratio XZ", None),
    ("pa36", "Shear Modulus XY", _STRESS), ("pa37", "Shear Modulus YZ", _STRESS), ("pa38", "Shear Modulus XZ", _STRESS),
    ("pa39", "Young's Modulus", _STRESS), ("pa40", "Poisson's Ratio", None),
    ("pa41", "Bulk Modulus", _STRESS), ("pa42", "Shear Modulus", _STRESS),
]
PROPS = [("pr0", "Color"), ("pr1", "Density"), ("pr2", "Elasticity"), ("pr5", "Coefficient of Thermal Expansion"),
         ("pr6", "Material Unique Id"), ("pr7", "Field Variable"), ("pr11", "Thermal Conductivity"),
         ("pr12", "Specific Heat")]


def metadata_xml():
    meta = ["      <Metadata>\n"]
    for pid, name, u in PARAMS:
        meta.append('        <ParameterDetails id="%s">\n          <Name>%s</Name>\n%s        </ParameterDetails>\n'
                    % (pid, name, u if u else "          <Unitless />\n"))
    for pid, name in PROPS:
        meta.append('        <PropertyDetails id="%s">\n          <Unitless />\n          <Name>%s</Name>\n'
                    '        </PropertyDetails>\n' % (pid, name))
    meta.append("      </Metadata>\n")
    return "".join(meta)


def color_of(name):
    h = hashlib.md5(name.encode("ascii", "replace")).digest()
    return (130 + h[0] % 100, 150 + h[1] % 90, 150 + h[2] % 90)


# ============================================================
# 4) Main
# ============================================================
def convert(workbook, out_dir=None, check=False):
    rows, sha = read_table(workbook)
    out_dir = out_dir or os.path.dirname(os.path.abspath(workbook))
    src_name = ascii_clean(os.path.basename(workbook))
    groups, order = {}, []
    for r in rows:
        key = (r["model"], rc_label(r["rc"]))
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(r)

    included, excluded, mats, seen = [], [], [], {}
    for key in order:
        model, rc = key
        rs = groups[key]
        base = "%s_RC%s" % (ascii_clean(model), rc)
        vendor = ascii_clean(rs[0]["vendor"])
        glass = sorted(set(ascii_clean(r["glass"]) for r in rs if r["glass"] not in (None, "")))
        data, problems, notes, ignored = build_material(rs)
        if norm_key(base) in seen:
            problems.append("name %s collides with %s" % (base, seen[norm_key(base)]))
            data = None
        if not ascii_clean(model) or '"' in model or "\\" in model:
            problems.append("model name has characters that cannot be used in a material name")
            data = None
        info = {"base": base, "model": model, "rc": rc, "vendor": vendor, "glass": ", ".join(glass), "rows": len(rs),
                "problems": problems, "notes": notes, "ignored": ignored, "data": data}
        if data is None:
            excluded.append(info)
            continue
        seen[norm_key(base)] = base
        included.append(info)
        head = ("Jabil PCB material library. Model %s, vendor %s, resin content %s, glass %s, Tg %s C. "
                % (ascii_clean(model), vendor or "-", (rc + " %") if rc != "NA" else "not stated", info["glass"] or "-",
                   _t(data["tg"]) if data["tg"] is not None else "-"))
        tail = (" Source: %s sha256 %s. Assumptions and defaults: %s." % (src_name, sha[:12], "; ".join(notes)))
        common = common_parts(data["dens"], data["k"], data["cp"])
        mats.append(material_xml(
            base + "_Ortho",
            head + "ORTHOTROPIC elasticity (Ex, Ey from the library; Gxy = mean(Ex,Ey)/(2(1+nu)); "
                   "Gyz = Gxz = Ez/(2(1+nu)); one Poisson's ratio), orthotropic instantaneous CTE." + tail,
            "Laminate", color_of(base), [common[0], ortho_elastic(data), ortho_cte(data)] + common[1:]))
        mats.append(material_xml(
            base + "_Iso",
            head + "ISOTROPIC elasticity (E = mean(Ex, Ey)), orthotropic instantaneous CTE." + tail,
            "Laminate", color_of(base + "i"),
            [common[0], iso_elastic(data["te"], data["eiso"], data["nu"]), ortho_cte(data)] + common[1:]))

    cu = COPPER
    cu_common = common_parts(cu["dens"], cu["k"], cu["cp"])
    mats.append(material_xml(
        cu["name"],
        "Jabil PCB material library. Copper of the traces, fixed values agreed 2026-11-25 (not from the workbook): "
        "E 110 GPa, nu 0.34, density 8960 kg/m3, K 400 W/m-K, Cp 380 J/kg-K, CTE 17 ppm/C, all constant with temperature.",
        "Metal", (208, 146, 88),
        [cu_common[0], iso_elastic([25.0], [cu["e"]], cu["nu"]), iso_cte([25.0], [cu["cte"]])] + cu_common[1:]))

    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<EngineeringData version="25.1.0.203">\n  <Notes>\n  </Notes>\n'
           '  <Materials>\n    <MatML_Doc>\n' + "".join(mats) + metadata_xml() +
           '    </MatML_Doc>\n  </Materials>\n</EngineeringData>\n')
    xml.encode("ascii")                                   # the library must stay plain ASCII
    if '"""' in xml or "\\" in xml:
        raise InputError("the XML would contain a backslash or triple quotes (check model names and remarks)")
    xml_sha = hashlib.sha256(xml.encode("ascii")).hexdigest()
    report = make_report(src_name, sha, xml_sha, included, excluded)

    xml_path = os.path.join(out_dir, XML_NAME)
    rep_path = os.path.join(out_dir, REPORT_NAME)
    state = "check only, nothing written"
    if not check:
        old = None
        if os.path.isfile(xml_path):
            with open(xml_path, "rb") as fh:
                old = fh.read()
        if old is not None and old == xml.encode("ascii"):
            state = "no change: %s is already up to date" % XML_NAME
        else:
            if old is not None:
                arch = os.path.join(out_dir, "archive")
                if not os.path.isdir(arch):
                    os.makedirs(arch)
                stamp = datetime.datetime.fromtimestamp(os.path.getmtime(xml_path)).strftime("%Y%m%d_%H%M%S")
                shutil.move(xml_path, os.path.join(arch, "PCB_Material_Library_%s.xml" % stamp))
                if os.path.isfile(rep_path):
                    shutil.move(rep_path, os.path.join(arch, "PCB_Material_Library_report_%s.md" % stamp))
                state = "updated; the previous version is in archive\\ (%s)" % stamp
            else:
                state = "created"
            with open(xml_path, "w", encoding="ascii", newline="\n") as fh:
                fh.write(xml)
        with open(rep_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(report)
    return {"xml": xml, "xml_path": xml_path, "report": report, "report_path": rep_path, "included": included,
            "excluded": excluded, "state": state, "sha": xml_sha}


def make_report(src_name, sha, xml_sha, included, excluded):
    L = ["# PCB material library - conversion report", "",
         "- Generated: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
         "- Source: `%s`, sheet `%s` (sha256 `%s`)" % (src_name, SHEET_NAME, sha[:12]),
         "- Output: `%s` (sha256 `%s`), Engineering Data format of ANSYS 2025 R1" % (XML_NAME, xml_sha[:12]),
         "- In the library: **%d** laminates (each as `_Ortho` and `_Iso`) and `%s`. Not in the library: **%d**."
         % (len(included), COPPER["name"], len(excluded)), "",
         "## Materials in the library", "",
         "| Material (add `_Ortho` / `_Iso`) | Vendor | RC | E range C | CTE range C | Ex / Ey / Ez at 30 C, MPa | "
         "CTE X / Y / Z at 30 C, ppm/C | nu | Density | K | Cp |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in included:
        d = m["data"]
        at = lambda T, xs, ys: interp(T, xs, ys)
        L.append("| `%s` | %s | %s | %s to %s | %s to %s | %.0f / %.0f / %.0f | %.2f / %.2f / %.2f | %g | %g | %g | %g |" % (
            m["base"], m["vendor"], m["rc"], _t(d["te"][0]), _t(d["te"][-1]), _t(d["tc"][0]), _t(d["tc"][-1]),
            at(30, d["te"], d["ex"]) / 1e6, at(30, d["te"], d["ey"]) / 1e6, at(30, d["te"], d["ez"]) / 1e6,
            at(30, d["tc"], d["cx"]) * 1e6, at(30, d["tc"], d["cy"]) * 1e6, at(30, d["tc"], d["cz"]) * 1e6,
            d["nu"], d["dens"], d["k"], d["cp"]))
    L += ["", "`%s`: E 110000 MPa, nu 0.34, density 8960 kg/m3, K 400 W/m-K, Cp 380 J/kg-K, CTE 17 ppm/C "
              "(fixed values, not from the workbook)." % COPPER["name"], "",
          "### Assumptions and defaults per material", ""]
    for m in included:
        L.append("**%s**" % m["base"])
        L += ["- " + n for n in m["notes"]] + [""]
    L += ["## Materials NOT in the library", ""]
    if not excluded:
        L.append("None.")
    else:
        L.append("A material is left out when a required value is missing or a row cannot be read. "
                 "Add or correct the rows named below in the workbook and run the converter again.")
        L.append("")
        for m in excluded:
            L.append("**%s** (%s, %d rows)" % (m["base"], m["vendor"], m["rows"]))
            L += ["- " + p for p in m["problems"]] + [""]
    ign = [(m["base"], i) for m in included + excluded for i in m["ignored"]]
    if ign:
        L += ["## Rows that were not used", ""] + ["- %s: %s" % x for x in ign] + [""]
    L += ["## Rules", "",
          "- Required per material: Storage Modulus versus temperature (X and/or Y), CTE X and/or Y, CTE Z, "
          "Poisson's Ratio, Density.",
          "- E(T) = Storage Modulus. A Young's Modulus row adds its own temperature point (usually 25 C) "
          "unless the Storage Modulus already has that temperature.",
          "- A curve must start at or below %g C. A curve that starts at or below %g C is extended with a "
          "constant value down to %g C; a later start means the data is incomplete."
          % (T_START, T_EXTEND_MAX, T_START),
          "- X and Y are kept separate; with one in-plane data set, X = Y. Axis empty or `X/Y` = both.",
          "- Ez from the library when it has a Z Storage Modulus curve, otherwise %g x mean(Ex, Ey)." % EZ_RATIO,
          "- Gxy = mean(Ex, Ey) / (2(1+nu)); Gyz = Gxz = Ez / (2(1+nu)); PRXY = PRYZ = PRXZ = nu.",
          "- `_Iso`: isotropic elasticity with E = mean(Ex, Ey); the CTE stays orthotropic. CTE is instantaneous.",
          "- Thermal Conductivity / Specific Heat: from the library when present, otherwise %g W/m-K / %g J/kg-K."
          % (DEFAULT_K, DEFAULT_CP),
          "- Values above the last data point are held constant.",
          "- Each resin content is a separate material (`_RC<nn>`, `_RCNA` when not stated).", ""]
    return "\n".join(L)


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    check = "--check" in argv
    out_dir = None
    if "--out" in argv:
        i = argv.index("--out")
        if i + 1 >= len(argv):
            print("ERROR: --out needs a folder")
            return 3
        out_dir = argv[i + 1]
        args = [a for a in args if a != out_dir]
    here = os.path.dirname(os.path.abspath(__file__))
    workbook = args[0] if args else os.path.join(here, WORKBOOK_NAME)
    try:
        res = convert(workbook, out_dir, check)
    except InputError as e:
        print("ERROR: %s" % e)
        return 3
    print("Workbook : %s" % workbook)
    print("In       : %d laminates x (_Ortho, _Iso) + %s" % (len(res["included"]), COPPER["name"]))
    for m in res["included"]:
        print("  + %s" % m["base"])
    print("Not in   : %d" % len(res["excluded"]))
    for m in res["excluded"]:
        print("  - %s: %s" % (m["base"], "; ".join(m["problems"])[:160]))
    print("XML      : %s" % res["xml_path"])
    print("Report   : %s" % res["report_path"])
    print("RESULT   : %s" % res["state"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
