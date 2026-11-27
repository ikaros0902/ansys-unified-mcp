# -*- coding: utf-8 -*-
# ============================================================
# Mechanical Scripting (Ansys 2025 R1 / 2026 R1, IronPython 2.7 and CPython 3)
# PCB Trace Mapping - equivalent copper/FR4 material per element  (v6, all-in-one)
#
# What it does
#   1. Reads the material data from the Engineering Data XML library
#      (PCB_Material_Library.xml, written by Update_PCB_Material_Library.py). The materials of
#      this project are embedded below, so the script is ONE file and runs on any PC.
#   2. Reads every body name  Layer_<N>_<Material>[_<ratio>]  (LayerBuilder naming), finds the
#      material in the library and assigns the Engineering Data material
#      <Model>_RC<nn>_Ortho  (FR4_MODEL = "ORTHO")  or  <Model>_RC<nn>_Iso  (FR4_MODEL = "ISO").
#      No stackup.csv is needed.
#   3. Exports the copper fraction per element from the Imported Trace object(s), puts every
#      element into a 1 % bin (round half up, same as Ansys) and writes one material per
#      (FR4, bin): volume rule of mixtures of copper and FR4 = Ansys "Average" material
#      modeling. CTE can use Turner instead (METHOD_CTE_XY / METHOD_CTE_Z).
#   4. Writes the APDL files and a Command Snippet (EMODIF per element).
#      ALL layer bodies are processed: copper layers, prepreg and core. Bin 0 is not modified
#      (the element keeps the Mechanical material), exactly as Ansys does.
#
# Before running
#   - Engineering Data of this system: import PCB_Material_Library.xml and add the materials
#     of this board (both are needed: the script assigns them, it cannot create them).
#   - Mesh generated, Import Trace Mapping done (not suppressed).
#
# Do not run the template of the tool folder for a project: use the copy that run_odb_tool.py
# writes into  runs\<run>\mechanical\  (materials of that board embedded). To use this file
# by hand, set MATERIAL_XML to the full library file.
# ============================================================

import os
import math
import datetime
import re

# ---------------- User settings ----------------
FR4_MODEL = "ORTHO"            # "ORTHO" = orthotropic FR4 (<name>_Ortho), "ISO" = isotropic elasticity (<name>_Iso)
METHOD_CTE_XY = "ROM"          # "ROM" (= Ansys Average) or "TURNER"
METHOD_CTE_Z  = "ROM"          # "ROM" (= Ansys Average) or "TURNER"
METHOD_G      = "ROM"          # "ROM" = mix the shear moduli linearly (confirmed against Ansys, orthotropic FR4)
                               # "FROM_E_NU" = G from the mixed E and nu (what MAPDL does for an isotropic run)
T_REF = 30.0                   # stress-free / reference temperature [C]
WRITE_TREF = True              # write TREF in the snippet (TUNIF is NOT written)

ASSIGN_MATERIALS = True        # True = assign the Engineering Data material to every layer body
ANALYSIS_NAME = ""             # "" = automatic. Fill in only to force a specific analysis.
SNIPPET_NAME  = "TraceMapping_v6"
MODE = "AUTO"                  # "AUTO" = write files + create the snippet, "FILES_ONLY" = write files only
SOLVER_UNITS = "AUTO"          # "AUTO", "MM_TONNE_N_S" (MPa) or "SI" (Pa)

MATERIAL_XML = r""             # "" = the embedded materials below. Or the full path of PCB_Material_Library.xml
MATERIAL_CHOICE = {}           # only when the library has one model with several resin contents,
                               # e.g. {"EM370Z": "EM-370(Z)_RC51"}
COPPER_NAME = "Copper for Warpage"

out_dir_base = r"C:\temp\trace_mapping"
BASE_MAT_ID = 10000            # material IDs: BASE + fr4_index*NUM_BINS + bin. Must not collide with Mechanical IDs.
NUM_BINS = 101                 # 1 % copper-fraction resolution (same as Ansys)
SKIP_ZERO_BIN = True           # True = bin 0 keeps the Mechanical material (= Ansys)
MARK_PREFIX = "__TRACE_MAPPING_"   # marker written into every snippet; used to find old ones


# ============================================================
# EMBEDDED MATERIALS  (written by run_odb_tool.py - do not edit by hand)
# ============================================================
LIBRARY_INFO = "template of the tool folder: no material embedded"
# BEGIN EMBEDDED_MATERIAL_XML
EMBEDDED_MATERIAL_XML = """
"""
# END EMBEDDED_MATERIAL_XML


# ---------------- Helpers ----------------
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def write_file(path, text):
    f = open(path, "w")
    try:
        f.write(text)
    finally:
        f.close()

def interp(x, xp, fp):
    if x <= xp[0]:
        return fp[0]
    if x >= xp[-1]:
        return fp[-1]
    i = 0
    while i < len(xp) - 1:
        if xp[i] <= x <= xp[i + 1]:
            t = (x - xp[i]) / float(xp[i + 1] - xp[i])
            return fp[i] + t * (fp[i + 1] - fp[i])
        i += 1
    return fp[-1]

def safe_name(s):
    if not s:
        return "Trace"
    out = [ch if ch.isalnum() or ch == '_' else '_' for ch in str(s).strip()]
    s_new = "".join(out)
    while "__" in s_new:
        s_new = s_new.replace("__", "_")
    return s_new.strip("_")

def norm_mat(s):
    """'EM-370(Z)' / 'EM370(Z)' / 'em370z' -> 'EM370Z'"""
    return "".join([c for c in str(s) if c.isalnum()]).upper()

def parse_layer_name(name):
    """Return (layer_no, material token or None). Layer_5, Layer_5_EM892K2, Layer_4_EM370(Z)_0.296."""
    m = re.search(r"Layer[_\-\s]*0*([0-9]+)(?:[_\-\s]+([A-Za-z0-9\(\)\-]+))?", name, re.IGNORECASE)
    if not m:
        return None, None
    tok = m.group(2)
    if tok is not None and not re.search(r"[A-Za-z]", tok):
        tok = None
    return int(m.group(1)), tok

def frac_bin(frac):
    """Copper fraction -> bin 0..NUM_BINS-1, round half up (same as Ansys)."""
    fr = max(0.0, min(1.0, frac))
    return int(math.floor(fr * (NUM_BINS - 1) + 0.5))


# ============================================================
# 1) UNITS
# ============================================================
# Natural values: stress MPa, density kg/m3, K W/m-K, Cp J/kg-K  ->  solver value = natural * factor
UNIT_TABLE = {
    "MM_TONNE_N_S": {"label": "mm-tonne-N-s (MPa)", "stress": 1.0, "dens": 1.0e-12, "k": 1.0, "cp": 1.0e6},
    "SI":           {"label": "m-kg-N-s (Pa)",      "stress": 1.0e6, "dens": 1.0,    "k": 1.0, "cp": 1.0},
}

def detect_solver_units():
    if SOLVER_UNITS != "AUTO":
        if SOLVER_UNITS not in UNIT_TABLE:
            raise Exception("SOLVER_UNITS must be AUTO, MM_TONNE_N_S or SI")
        return SOLVER_UNITS, "manual setting %s" % SOLVER_UNITS
    try:
        raw = str(ExtAPI.Application.ActiveUnitSystem)
    except Exception as e:
        raise Exception("Cannot read the active unit system (%s). Set SOLVER_UNITS manually." % str(e)[:80])
    low = raw.lower()
    if "tonmm" in low or "nmm" in low or "(mm," in low:
        return "MM_TONNE_N_S", "active unit system '%s' -> mm-tonne-N-s" % raw
    if low.endswith("mks") or "(m, kg" in low:
        return "SI", "active unit system '%s' -> SI" % raw
    raise Exception("Unsupported unit system '%s'. Supported: UnitNMM / UnitTONMMKS (mm) and UnitMKS (m). "
                    "Set SOLVER_UNITS manually if you know the solver units." % raw)


# ============================================================
# 2) MATERIAL LIBRARY (Engineering Data XML written by Update_PCB_Material_Library.py)
# ============================================================
def _unesc(s):
    return (s.replace("&lt;", "<").replace("&gt;", ">").replace("&apos;", "'").replace("&quot;", '"')
            .replace("&amp;", "&"))

def parse_material_xml(text):
    """Engineering Data XML -> {material name: {"desc": str, "props": {property name: [ {"q": {}, "v": {}} ]}}}.
    Reads the layout written by Update_PCB_Material_Library.py (parameter values in SI units)."""
    params = {}
    for m in re.finditer(r'<ParameterDetails id="([^"]+)">\s*<Name>([^<]*)</Name>', text):
        params[m.group(1)] = _unesc(m.group(2))
    props = {}
    for m in re.finditer(r'<PropertyDetails id="([^"]+)">(.*?)</PropertyDetails>', text, re.S):
        n = re.search(r"<Name>([^<]*)</Name>", m.group(2))
        if n:
            props[m.group(1)] = _unesc(n.group(1))
    if not params or not props:
        raise Exception("Material XML: no <Metadata> found (not an Engineering Data library?)")
    mats = {}
    order = []
    for m in re.finditer(r"<Material>(.*?)</Material>", text, re.S):
        blk = m.group(1)
        nm = re.search(r"<BulkDetails>\s*<Name>([^<]*)</Name>", blk)
        if not nm:
            continue
        name = _unesc(nm.group(1)).strip()
        d = re.search(r"<Description>([^<]*)</Description>", blk)
        pd = {}
        for p in re.finditer(r'<PropertyData property="([^"]+)">(.*?)</PropertyData>', blk, re.S):
            body = p.group(2)
            head = body.split("<ParameterValue", 1)[0]
            quals = {}
            for q in re.finditer(r'<Qualifier name="([^"]+)">([^<]*)</Qualifier>', head):
                quals[q.group(1)] = _unesc(q.group(2))
            vals = {}
            for q in re.finditer(r'<ParameterValue parameter="([^"]+)" format="float">\s*<Data>([^<]*)</Data>', body):
                vals[params.get(q.group(1), q.group(1))] = [float(x) for x in q.group(2).split(",") if x.strip()]
            pd.setdefault(props.get(p.group(1), p.group(1)), []).append({"q": quals, "v": vals})
        mats[name] = {"desc": _unesc(d.group(1)) if d else "", "props": pd}
        order.append(name)
    return mats, order

def split_material_name(name):
    """'EM-370(Z)_RC51_Ortho' -> (base 'EM-370(Z)_RC51', variant 'ORTHO', key 'EM370Z', rc '51')."""
    base, variant = name, None
    low = name.lower()
    for suf, var in (("_ortho", "ORTHO"), ("_iso", "ISO")):
        if low.endswith(suf):
            base, variant = name[:-len(suf)], var
    m = re.match(r"^(.*)_RC([A-Za-z0-9]+)$", base)
    model, rc = (m.group(1), m.group(2)) if m else (base, "")
    return base, variant, norm_mat(model), rc

def _one(mat, pname, name):
    for p in mat["props"].get(pname, []):
        if p["v"].get(pname):
            return p["v"][pname][0]
    raise Exception("Material '%s': property '%s' not found in the library" % (name, pname))

def _table(vals, key, n, name):
    v = vals.get(key)
    if not v:
        raise Exception("Material '%s': '%s' not found in the library" % (name, key))
    if len(v) == 1 and n > 1:
        v = v * n
    if len(v) != n:
        raise Exception("Material '%s': '%s' has %d values for %d temperatures" % (name, key, len(v), n))
    return v

def build_material(mat, name):
    """One library material on its own temperature points. Natural units (MPa, 1/C, kg/m3, W/m-K, J/kg-K)."""
    MPa = 1.0e-6
    el = mat["props"].get("Elasticity")
    ct = mat["props"].get("Coefficient of Thermal Expansion")
    if not el or not ct:
        raise Exception("Material '%s': elasticity or thermal expansion missing in the library" % name)
    el, ct = el[0], ct[0]
    if ct["q"].get("Definition", "") != "Instantaneous":
        raise Exception("Material '%s': the CTE must be defined as Instantaneous (found '%s')" % (name, ct["q"].get("Definition")))
    te = el["v"].get("Temperature", [0.0])
    n = len(te)
    v = el["v"]
    if el["q"].get("Behavior") == "Orthotropic":
        ex = _table(v, "Young's Modulus X direction", n, name)
        ey = _table(v, "Young's Modulus Y direction", n, name)
        ez = _table(v, "Young's Modulus Z direction", n, name)
        pxy = _table(v, "Poisson's Ratio XY", n, name)
        pyz = _table(v, "Poisson's Ratio YZ", n, name)
        pxz = _table(v, "Poisson's Ratio XZ", n, name)
        gxy = _table(v, "Shear Modulus XY", n, name)
        gyz = _table(v, "Shear Modulus YZ", n, name)
        gxz = _table(v, "Shear Modulus XZ", n, name)
    else:
        ex = _table(v, "Young's Modulus", n, name)
        ey, ez = ex, ex
        pxy = _table(v, "Poisson's Ratio", n, name)
        pyz, pxz = pxy, pxy
        gxy = [ex[i] / (2.0 * (1.0 + pxy[i])) for i in range(n)]
        gyz, gxz = gxy, gxy
    tc = ct["v"].get("Temperature", [0.0])
    m = len(tc)
    c = ct["v"]
    if ct["q"].get("Behavior") == "Orthotropic":
        cx = _table(c, "Coefficient of Thermal Expansion X direction", m, name)
        cy = _table(c, "Coefficient of Thermal Expansion Y direction", m, name)
        cz = _table(c, "Coefficient of Thermal Expansion Z direction", m, name)
    else:
        cx = _table(c, "Coefficient of Thermal Expansion", m, name)
        cy, cz = cx, cx
    grid = []
    if n > 1:
        grid += te
    if m > 1:
        grid += tc
    grid = sorted(set(grid)) or [T_REF]
    def on(ts, vals, scale):
        if len(ts) == 1:
            return [vals[0] * scale] * len(grid)
        return [interp(T, ts, vals) * scale for T in grid]
    return {"name": name, "T": grid,
            "ex": on(te, ex, MPa), "ey": on(te, ey, MPa), "ez": on(te, ez, MPa),
            "pxy": on(te, pxy, 1.0), "pyz": on(te, pyz, 1.0), "pxz": on(te, pxz, 1.0),
            "gxy": on(te, gxy, MPa), "gyz": on(te, gyz, MPa), "gxz": on(te, gxz, MPa),
            "cx": on(tc, cx, 1.0), "cy": on(tc, cy, 1.0), "cz": on(tc, cz, 1.0),
            "dens": _one(mat, "Density", name), "k": _one(mat, "Thermal Conductivity", name),
            "cp": _one(mat, "Specific Heat", name), "behavior": el["q"].get("Behavior", "")}

def load_library():
    """-> (fr4 {key: material dict + 'base', 'ed_name'}, key order, copper dict, source text)."""
    if MATERIAL_XML:
        if not os.path.exists(MATERIAL_XML):
            raise Exception("MATERIAL_XML not found: %s" % MATERIAL_XML)
        f = open(MATERIAL_XML, "r")
        try:
            text = f.read()
        finally:
            f.close()
        source = MATERIAL_XML
    else:
        text = EMBEDDED_MATERIAL_XML
        source = "embedded (%s)" % LIBRARY_INFO
    if "<Material>" not in text:
        raise Exception("No material data. This is the template of the tool folder: run the copy that "
                        "run_odb_tool.py wrote into runs\\<run>\\mechanical, or set MATERIAL_XML to "
                        "PCB_Material_Library.xml.")
    mats, order = parse_material_xml(text)
    want = "ORTHO" if FR4_MODEL == "ORTHO" else "ISO"
    by_key = {}
    key_order = []
    cu = None
    for name in order:
        if norm_mat(name) == norm_mat(COPPER_NAME):
            c = build_material(mats[name], name)
            cu = {"name": name, "e": c["ex"][0], "nu": c["pxy"][0], "g": c["gxy"][0], "cte": c["cx"][0],
                  "dens": c["dens"], "k": c["k"], "cp": c["cp"]}
            continue
        base, variant, key, rc = split_material_name(name)
        if variant != want:
            continue
        if key not in by_key:
            by_key[key] = {}
            key_order.append(key)
        by_key[key][base] = name
    if cu is None:
        raise Exception("Material '%s' is not in the library (%s)" % (COPPER_NAME, source))
    fr4 = {}
    for key in key_order:
        bases = sorted(by_key[key].keys())
        if len(bases) > 1:
            pick = [b for b in bases if norm_mat(b) == norm_mat(MATERIAL_CHOICE.get(key, ""))]
            if not pick:
                raise Exception("Library has several materials for %s: %s. Set MATERIAL_CHOICE = {\"%s\": \"<one of them>\"}."
                                % (key, bases, key))
            bases = pick
        name = by_key[key][bases[0]]
        d = build_material(mats[name], name)
        d["key"] = key
        d["base"] = bases[0]
        fr4[key] = d
    return fr4, key_order, cu, source


# ============================================================
# 3) CORE HOMOGENIZATION (natural units)  -- Ansys "Average" rule
# ============================================================
def _vo(a_cu, a_f, v):
    return a_cu * v + a_f * (1.0 - v)

def _turner(a_cu, e_cu, a_f, e_f, v):
    return (a_cu * e_cu * v + a_f * e_f * (1.0 - v)) / (e_cu * v + e_f * (1.0 - v))

LABELS = ["EX", "EY", "EZ", "PRXY", "PRYZ", "PRXZ", "GXY", "GYZ", "GXZ",
          "CTEX", "CTEY", "CTEZ", "KXX", "KYY", "KZZ"]

def get_inst_properties(i, v, f, cu):
    """Order = LABELS. Volume rule of mixtures for every term; CTE optionally Turner."""
    Ex = _vo(cu["e"], f["ex"][i], v)
    Ey = _vo(cu["e"], f["ey"][i], v)
    Ez = _vo(cu["e"], f["ez"][i], v)
    Pxy = _vo(cu["nu"], f["pxy"][i], v)
    Pyz = _vo(cu["nu"], f["pyz"][i], v)
    Pxz = _vo(cu["nu"], f["pxz"][i], v)
    if METHOD_G == "FROM_E_NU":
        Gxy = 0.5 * (Ex + Ey) / (2.0 * (1.0 + Pxy))
        Gyz = Ez / (2.0 * (1.0 + Pyz))
        Gxz = Ez / (2.0 * (1.0 + Pxz))
    else:
        Gxy = _vo(cu["g"], f["gxy"][i], v)
        Gyz = _vo(cu["g"], f["gyz"][i], v)
        Gxz = _vo(cu["g"], f["gxz"][i], v)
    if METHOD_CTE_XY == "TURNER":
        Cx = _turner(cu["cte"], cu["e"], f["cx"][i], f["ex"][i], v)
        Cy = _turner(cu["cte"], cu["e"], f["cy"][i], f["ey"][i], v)
    else:
        Cx = _vo(cu["cte"], f["cx"][i], v)
        Cy = _vo(cu["cte"], f["cy"][i], v)
    if METHOD_CTE_Z == "TURNER":
        Cz = _turner(cu["cte"], cu["e"], f["cz"][i], f["ez"][i], v)
    else:
        Cz = _vo(cu["cte"], f["cz"][i], v)
    K = _vo(cu["k"], f["k"], v)
    return (Ex, Ey, Ez, Pxy, Pyz, Pxz, Gxy, Gyz, Gxz, Cx, Cy, Cz, K, K, K)

def density_cp(v, f, cu):
    """Density [kg/m3] (volume rule) and mass-weighted specific heat [J/kg-K]."""
    rho = cu["dens"] * v + f["dens"] * (1.0 - v)
    cp = (cu["dens"] * v * cu["cp"] + f["dens"] * (1.0 - v) * f["cp"]) / rho
    return rho, cp

def poisson_stable(p):
    Ex, Ey, Ez, pxy, pyz, pxz = p[0], p[1], p[2], p[3], p[4], p[5]
    nuyx = pxy * Ey / Ex
    nuzy = pyz * Ez / Ey
    nuzx = pxz * Ez / Ex
    d = 1.0 - pxy * nuyx - pyz * nuzy - pxz * nuzx - 2.0 * nuyx * nuzy * pxz
    return d > 0.0

def check_methods():
    if FR4_MODEL not in ("ORTHO", "ISO"):
        raise Exception("FR4_MODEL must be ORTHO or ISO")
    if METHOD_G not in ("ROM", "FROM_E_NU"):
        raise Exception("METHOD_G must be ROM or FROM_E_NU")
    if METHOD_CTE_XY not in ("ROM", "TURNER"):
        raise Exception("METHOD_CTE_XY must be ROM or TURNER")
    if METHOD_CTE_Z not in ("ROM", "TURNER"):
        raise Exception("METHOD_CTE_Z must be ROM or TURNER")
    if MODE not in ("AUTO", "FILES_ONLY"):
        raise Exception("MODE must be AUTO or FILES_ONLY")

def material_apdl(fr4, key_order, used_keys, cu, U, run_tag):
    """APDL text of all (FR4, bin) materials. Returns (lines, number of unstable points)."""
    apdl = ["/PREP7",
            "! Trace mapping materials %s  (FR4 model %s, Ansys Average rule, G=%s, CTE_XY=%s, CTE_Z=%s)" % (
                run_tag, FR4_MODEL, METHOD_G, METHOD_CTE_XY, METHOD_CTE_Z),
            "! Library: %s" % LIBRARY_INFO,
            "! Solver units: %s  (stress x%g, density x%g, K x%g, Cp x%g)" % (U["label"], U["stress"], U["dens"], U["k"], U["cp"]),
            "! ID = %d + fr4_index*%d + bin;  bin = floor(cu_fraction*%d + 0.5);  fr4 index: %s" %
            (BASE_MAT_ID, NUM_BINS, NUM_BINS - 1, ", ".join(["%d=%s" % (i, k) for i, k in enumerate(key_order)]))]
    scale = {"EX": U["stress"], "EY": U["stress"], "EZ": U["stress"],
             "GXY": U["stress"], "GYZ": U["stress"], "GXZ": U["stress"],
             "KXX": U["k"], "KYY": U["k"], "KZZ": U["k"]}
    n_unstable = 0
    for key in used_keys:
        f = fr4[key]
        T = f["T"]
        apdl.append("! ------------------------------------------------------------")
        apdl.append("! FR4 = %s (%s)  density(kg/m3)=%.1f  K=%.3g W/m-K  Cp=%.4g J/kg-K  %d temperature points" %
                    (key, f["name"], f["dens"], f["k"], f["cp"], len(T)))
        apdl.append("MPTEMP")
        for i in range(0, len(T), 6):
            apdl.append("MPTEMP,%d,%s" % (i + 1, ",".join(["%.8E" % x for x in T[i:i + 6]])))
        base = BASE_MAT_ID + key_order.index(key) * NUM_BINS
        for k in range(NUM_BINS):
            v = k / float(NUM_BINS - 1)
            mid = base + k
            rho, cp = density_cp(v, f, cu)
            apdl.append("MPDELE,ALL,%d" % mid)
            apdl.append("TBDELE,ALL,%d" % mid)
            apdl.append("MP,REFT,%d,%.4E" % (mid, T_REF))
            apdl.append("MP,DENS,%d,%.8E" % (mid, rho * U["dens"]))
            props = [get_inst_properties(ti, v, f, cu) for ti in range(len(T))]
            for p in props:
                if not poisson_stable(p):
                    n_unstable += 1
            for l_idx, label in enumerate(LABELS):
                s = scale.get(label, 1.0)
                vals = [p[l_idx] * s for p in props]
                for j in range(0, len(vals), 6):
                    apdl.append("MPDATA,%s,%d,%d,%s" % (label, mid, j + 1, ",".join(["%.8E" % x for x in vals[j:j + 6]])))
            cpv = [cp * U["cp"]] * len(T)
            for j in range(0, len(cpv), 6):
                apdl.append("MPDATA,C,%d,%d,%s" % (mid, j + 1, ",".join(["%.8E" % x for x in cpv[j:j + 6]])))
    apdl.append("MPTEMP")
    return apdl, n_unstable

def library_summary(fr4, key_order, cu, source):
    out = ["Library : %s" % source,
           "Copper  : %s  E=%g MPa nu=%g CTE=%g 1/C rho=%g kg/m3 K=%g Cp=%g" %
           (cu["name"], cu["e"], cu["nu"], cu["cte"], cu["dens"], cu["k"], cu["cp"])]
    for k in key_order:
        f = fr4[k]
        i = 0
        for j, T in enumerate(f["T"]):
            if T <= T_REF:
                i = j
        out.append("FR4 %-8s: %s | %d points %g..%g C | at %g C: Ex=%g Ey=%g Ez=%g MPa nu=%g Gxy=%g "
                   "CTE=%g/%g/%g 1/C | rho=%g" %
                   (k, f["name"], len(f["T"]), f["T"][0], f["T"][-1], f["T"][i], f["ex"][i], f["ey"][i], f["ez"][i],
                    f["pxy"][i], f["gxy"][i], f["cx"][i], f["cy"][i], f["cz"][i], f["dens"]))
    return out


# ============================================================
# 4) ANALYSIS SELECTION
# ============================================================
def _same(a, b):
    if a is b:
        return True
    try:
        return a.ObjectId == b.ObjectId
    except Exception:
        return False

def physics_text(a):
    parts = []
    for attr in ("PhysicsType", "AnalysisType"):
        try:
            parts.append(str(getattr(a, attr)))
        except Exception:
            pass
    try:
        parts.append(a.GetType().Name)
    except Exception:
        pass
    parts.append(str(a.Name))
    return " ".join(parts)

def check_analysis_type(a, warns):
    txt = physics_text(a).lower()
    bad = ["electric", "magnet", "emag", "acoustic", "fluid", "explicit", "rigid"]
    for b in bad:
        if b in txt:
            raise Exception("Analysis '%s' looks like an unsupported type (%s). Only structural and thermal "
                            "analyses are supported. Details: %s" % (a.Name, b, txt[:100]))
    kind = "thermal" if "thermal" in txt else "structural"
    if "thermal" not in txt and "structural" not in txt and "mechanical" not in txt:
        warns.append("Could not confirm the type of analysis '%s' (%s); treated as structural" % (a.Name, txt[:80]))
    return kind

def pick_analysis():
    analyses = [a for a in Model.Analyses if a is not None]
    if not analyses:
        raise Exception("The model has no analysis.")
    names = [a.Name for a in analyses]
    if ANALYSIS_NAME:
        for a in analyses:
            if a.Name == ANALYSIS_NAME:
                return a, "forced by ANALYSIS_NAME"
        raise Exception("Analysis '%s' not found. Available: %s" % (ANALYSIS_NAME, names))
    if len(analyses) == 1:
        return analyses[0], "only analysis in the model"
    found = []
    try:
        active = list(ExtAPI.DataModel.Tree.ActiveObjects)
    except Exception:
        active = []
    for o in active:
        p = o
        depth = 0
        while p is not None and depth < 30:
            hit = [a for a in analyses if _same(p, a)]
            if hit:
                if not [x for x in found if _same(x, hit[0])]:
                    found.append(hit[0])
                break
            try:
                p = p.Parent
            except Exception:
                p = None
            depth += 1
    if len(found) == 1:
        return found[0], "selected in the Outline"
    if len(found) > 1:
        raise Exception("Several analyses are selected %s. Select only one. Available: %s" % ([a.Name for a in found], names))
    raise Exception("The model has %d analyses %s. Select ONE analysis (or an object under it) in the Outline and run again."
                    % (len(analyses), names))


# ============================================================
# 5) MAIN (runs inside Mechanical)
# ============================================================
def body_material_name(b):
    for attr in ("Material", "MaterialName"):
        try:
            v = getattr(b, attr)
            if v:
                return str(v)
        except Exception:
            pass
    return None

def get_body_table(fr4, warns):
    """Every active body -> dict(name, gid, n, key, ed). key = library key from the body name, or None."""
    table = []
    failed = []
    n_assigned = 0
    for b in DataModel.GetObjectsByType(DataModelObjectCategory.Body):
        try:
            if b.Suppressed:
                continue
        except Exception:
            pass
        gid = None
        try:
            gid = b.GetGeoBody().Id
        except Exception:
            try:
                gid = b.GeoBody.Id
            except Exception:
                gid = None
        if gid is None:
            warns.append("Body '%s': geometry id not readable, skipped" % b.Name)
            continue
        n, tok = parse_layer_name(b.Name)
        key = norm_mat(tok) if tok else None
        ed_name = body_material_name(b)
        if n is None:
            warns.append("Body '%s' is not named Layer_<N>_<Material>: left unchanged" % b.Name)
            key = None
        elif key is None:
            warns.append("Body '%s': the name has no material (expected Layer_<N>_<Material>): left unchanged" % b.Name)
        elif key not in fr4:
            warns.append("Body '%s': material %s is not in the library of this script %s: left unchanged"
                         % (b.Name, key, sorted(fr4.keys())))
            key = None
        else:
            target = fr4[key]["name"]
            if ed_name != target:
                if ASSIGN_MATERIALS:
                    try:
                        b.Material = target
                    except Exception as e:
                        failed.append((b.Name, target))
                    now = body_material_name(b)
                    if now == target:
                        n_assigned += 1
                        ed_name = now
                    elif (b.Name, target) not in failed:
                        failed.append((b.Name, target))
                else:
                    warns.append("Body '%s': Mechanical material is '%s', the body name asks for '%s' "
                                 "(ASSIGN_MATERIALS = False: not changed; bin 0 elements keep '%s')"
                                 % (b.Name, ed_name, target, ed_name))
        table.append({"n": n, "name": b.Name, "gid": gid, "key": key, "ed": ed_name})
    if failed:
        need = sorted(set([t for _, t in failed]))
        raise Exception("Could not assign the material of %d bodies (first: '%s'). Engineering Data of this system "
                        "must contain: %s. In Workbench open Engineering Data, import PCB_Material_Library.xml "
                        "(File > Import Engineering Data, or add it as a library under Engineering Data Sources "
                        "and add these materials to the project), refresh the Model cell and run again."
                        % (len(failed), failed[0][0], need))
    table.sort(key=lambda d: (d["n"] is None, d["n"], d["name"]))
    return table, n_assigned

def region_element_ids(mesh, gid):
    reg = mesh.MeshRegionById(gid)
    try:
        return set(int(x) for x in reg.ElementIds)
    except Exception:
        return set(int(e.Id) for e in reg.Elements)

def read_trace_export(path):
    """element id -> copper fraction (header / non-numeric lines are skipped)."""
    frac = {}
    skipped = 0
    f = open(path, "r")
    try:
        for line in f:
            p = line.split()
            if len(p) < 2:
                continue
            try:
                frac[int(float(p[0]))] = float(p[1])
            except ValueError:
                skipped += 1
    finally:
        f.close()
    return frac, skipped


def main():
    check_methods()
    log = []
    def say(s):
        log.append(s)
        print(s)

    warns = []
    analysis, why = pick_analysis()
    kind = check_analysis_type(analysis, warns)
    say("Analysis: '%s' (%s, %s)" % (analysis.Name, kind, why))

    unit_key, unit_txt = detect_solver_units()
    U = UNIT_TABLE[unit_key]
    say("Units   : %s -> solver %s" % (unit_txt, U["label"]))

    TS_TAG = datetime.datetime.now().strftime("%m%d_%H%M%S")
    RUN_TAG = "TM_%s_%s" % (safe_name(analysis.Name), TS_TAG)
    out_dir = os.path.join(out_dir_base, RUN_TAG)
    ensure_dir(out_dir)
    MARK = "%s%s__" % (MARK_PREFIX, RUN_TAG)

    fr4, key_order, cu, source = load_library()
    for line in library_summary(fr4, key_order, cu, source):
        say(line)
    say("Methods : FR4 model=%s | Ansys Average rule (Voigt) | G=%s | CTE_XY=%s CTE_Z=%s | T_REF=%.1f | "
        "bins=%d round-half-up | skip bin 0=%s" %
        (FR4_MODEL, METHOD_G, METHOD_CTE_XY, METHOD_CTE_Z, T_REF, NUM_BINS, SKIP_ZERO_BIN))

    # ---- traces and bodies ----
    traces = [o for o in DataModel.GetObjectsByType(DataModelObjectCategory.ImportedTrace) if not o.Suppressed]
    if not traces:
        raise Exception("No active Imported Trace found. Run Import Trace Mapping first and do not suppress it.")
    body_table, n_assigned = get_body_table(fr4, warns)
    n_ok = len([b for b in body_table if b["key"]])
    say("Imported Trace objects: %d | active bodies: %d | layer bodies with a library material: %d | "
        "material assignments changed: %d" % (len(traces), len(body_table), n_ok, n_assigned))
    try:
        mesh = ExtAPI.DataModel.MeshDataByName("Global")
    except Exception as e:
        raise Exception("Mesh data not available (%s). Generate the mesh first." % str(e)[:80])

    # ---- element fractions from all traces (last trace wins on overlap) ----
    frac_all = {}
    n_overlap = 0
    for t in traces:
        txt_path = os.path.join(out_dir, "Elem_cu_%s.txt" % safe_name(t.Name))
        try:
            t.ExportToTextFile(txt_path)
        except:
            t.ExportToTextFile(True, txt_path)
        frac, skipped = read_trace_export(txt_path)
        if not frac:
            raise Exception("No element data parsed from %s" % txt_path)
        if skipped > 1:
            warns.append("Trace '%s': %d non-numeric lines skipped (expected 1 header)" % (t.Name, skipped))
        for e in frac:
            if e in frac_all:
                n_overlap += 1
        frac_all.update(frac)
        say("Trace '%s': %d elements exported" % (t.Name, len(frac)))
    if n_overlap:
        warns.append("%d elements appear in more than one Imported Trace; the LAST one wins" % n_overlap)

    # ---- per body: bins and EMODIF lines ----
    covered = 0
    mapping_paths = []
    used = []
    summary = ["layer,body_name,mech_material,library_key,n_elem,n_modified,cu_mean_pct,cu_min_pct,cu_max_pct,n_bin0,n_bin100"]
    for b in body_table:
        hits = sorted([e for e in region_element_ids(mesh, b["gid"]) if e in frac_all])
        covered += len(hits)
        if not hits or b["key"] is None:
            if hits and b["key"] is None:
                warns.append("Body '%s': %d mapped elements left unchanged (no library material)" % (b["name"], len(hits)))
            continue
        base = BASE_MAT_ID + key_order.index(b["key"]) * NUM_BINS
        lines = []
        s = 0.0
        mn = 1.0
        mx = 0.0
        nb0 = 0
        nb100 = 0
        nclamp = 0
        for e in hits:
            raw = frac_all[e]
            fr = max(0.0, min(1.0, raw))
            if fr != raw:
                nclamp += 1
            k = frac_bin(fr)
            s += fr
            mn = min(mn, fr)
            mx = max(mx, fr)
            if k == 0:
                nb0 += 1
                if SKIP_ZERO_BIN:
                    continue
            if k == NUM_BINS - 1:
                nb100 += 1
            lines.append("EMODIF,%d,MAT,%d" % (e, base + k))
        if nclamp:
            warns.append("Body '%s': %d fractions outside 0..1 were clamped" % (b["name"], nclamp))
        mean = s / len(hits)
        summary.append("%s,%s,%s,%s,%d,%d,%.3f,%.3f,%.3f,%d,%d" % (
            b["n"], safe_name(b["name"]), b["ed"], b["key"], len(hits), len(lines),
            mean * 100.0, mn * 100.0, mx * 100.0, nb0, nb100))
        say("%-10s %-10s elems=%-7d modified=%-7d Cu mean=%6.2f%% min=%6.2f%% max=%6.2f%%" % (
            "Layer_%d" % b["n"], b["key"], len(hits), len(lines), mean * 100.0, mn * 100.0, mx * 100.0))
        if not lines:
            continue
        if b["key"] not in used:
            used.append(b["key"])
        map_path = os.path.join(out_dir, "apply_%s.inp" % safe_name(b["name"]))
        head = ["/PREP7",
                "! body=%s  Mechanical material=%s  library=%s  ID range %d..%d" % (
                    b["name"], b["ed"], b["key"], base, base + NUM_BINS - 1)]
        write_file(map_path, "\n".join(head + lines + ["ALLSEL"]))
        mapping_paths.append(map_path)
    unmatched = len(frac_all) - covered
    if unmatched:
        warns.append("%d exported elements are not in any active body (left unchanged)" % unmatched)
    if not mapping_paths:
        raise Exception("No element was modified (all fractions in bin 0 or no layer body with a library material).")

    # ---- material file (only the FR4 materials that are used) ----
    used_keys = [k for k in key_order if k in used]
    apdl, n_unstable = material_apdl(fr4, key_order, used_keys, cu, U, RUN_TAG)
    if n_unstable:
        warns.append("%d (material,temperature) points fail the orthotropic Poisson/stiffness check" % n_unstable)
    material_file = os.path.join(out_dir, "user_material_%s.inp" % RUN_TAG)
    write_file(material_file, "\n".join(apdl))

    # ---- snippet text ----
    lines = ["! %s" % MARK, "/PREP7"]
    if WRITE_TREF:
        lines.append("TREF,%.2f" % T_REF)
    md, mf = os.path.split(material_file)
    mn_, me_ = os.path.splitext(mf)
    lines.append("/INPUT,'%s','%s','%s'" % (mn_, me_[1:], md))
    for mp in mapping_paths:
        d, fn = os.path.split(mp)
        n2, e2 = os.path.splitext(fn)
        lines.append("/INPUT,'%s','%s','%s'" % (n2, e2[1:], d))
    lines.append("/SOLU")
    lines.append("! END %s" % MARK)
    snippet_text = "\n".join(lines)
    write_file(os.path.join(out_dir, "snippet_commands.txt"), snippet_text)
    write_file(os.path.join(out_dir, "layer_summary.csv"), "\n".join(summary))

    # ---- Mechanical Command Snippet (old ones are found by marker, whatever their name) ----
    if MODE == "AUTO":
        old = []
        try:
            for c in analysis.GetChildren(DataModelObjectCategory.CommandSnippet, True):
                try:
                    if MARK_PREFIX in str(c.Input):
                        old.append(c)
                except Exception:
                    pass
        except Exception:
            warns.append("Could not search old snippets; delete earlier trace-mapping snippets manually if duplicated")
        for c in old:
            try:
                c.Delete()
            except Exception:
                warns.append("Could not delete an old snippet '%s'; delete it manually" % c.Name)
        snip = analysis.AddCommandSnippet()
        snip.Name = SNIPPET_NAME
        snip.Input = snippet_text
        say("Snippet '%s' created under '%s' (old trace-mapping snippets removed: %d)" % (SNIPPET_NAME, analysis.Name, len(old)))
    else:
        say("FILES_ONLY: paste %s into a Command Snippet under '%s'" % (os.path.join(out_dir, "snippet_commands.txt"), analysis.Name))

    # Trace-mapping snippets left in OTHER analyses (an Ansys-native baseline must not have any)
    try:
        for a in Model.Analyses:
            if _same(a, analysis):
                continue
            for c in a.GetChildren(DataModelObjectCategory.CommandSnippet, True):
                try:
                    if MARK_PREFIX in str(c.Input) and not c.Suppressed:
                        warns.append("Analysis '%s' still has trace-mapping snippet '%s' (active). "
                                     "Suppress/delete it if that analysis is the Ansys baseline." % (a.Name, c.Name))
                except Exception:
                    pass
    except Exception:
        pass

    for w in warns:
        say("WARNING: " + w)
    say("RESULT  : %d bodies, %d elements with a trace value, %d warnings" % (len(mapping_paths), covered, len(warns)))
    write_file(os.path.join(out_dir, "run_log.txt"), "\n".join(log))
    say("Output dir: " + out_dir)


# Run inside Mechanical (DataModel exists there). Outside: print the embedded library only.
try:
    DataModel
    _IN_MECHANICAL = True
except NameError:
    _IN_MECHANICAL = False

if _IN_MECHANICAL:
    main()
elif __name__ == "__main__":
    check_methods()
    _f, _o, _c, _s = load_library()
    print("\n".join(library_summary(_f, _o, _c, _s)))
    print("Not inside Mechanical: library check only.")
