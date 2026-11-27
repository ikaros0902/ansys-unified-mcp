# -*- coding: utf-8 -*-
"""Element-by-element comparison of the FINAL material of two Mechanical ds.dat runs
(e.g. Ansys Imported Trace "ROM" vs. the Jabil v6 snippet).

Normal CPython 3 (not inside Mechanical):
    python Compare_TraceMapping_Dat.py <caseA_dir_or_ds.dat> <caseB_dir_or_ds.dat> [out_dir] [--tol 1e-4]

What is reproduced for each case, in MAPDL order up to the first SOLVE:
  * eblock material of every element (Mechanical body material)
  * MP / MPTEMP / MPDATA / MPDELE material definitions (temperature tables included)
  * Ansys trace mapping  CMBLOCK + EMOD,_cm_xxx,MAT,id
  * Command Snippet /INPUT files (searched first at the written path, then under the case folder)
    with EMODIF,elem,MAT,id
Isotropic data are expanded to orthotropic (EY=EZ=EX, PRYZ=PRXZ=PRXY, G=E/(2(1+nu)), CTEY=CTEZ=CTEX);
NUXY is read as PRXY and ALPX (secant) as CTEX (identical when the CTE is constant, e.g. copper).

Outputs (CSV) in out_dir:
  summary.txt            headline numbers and the worst difference per property
  by_body.csv            per body: elements, elements with a difference, max relative difference per property
  elements_diff.csv      elements whose material differs by more than tol (worst property / temperature)
  material_pairs.csv     every (matA, matB, property, T) with a difference above tol
  mixing_check_A.csv / mixing_check_B.csv
                         for every mixed material of the case: copper fraction from the density, then the
                         error of Voigt (ROM), Reuss and Turner predictions per property -> tells which rule
                         the case really uses (use it on the Ansys dat to confirm the Ansys formula)
"""
import os
import re
import sys
import csv
import math
import collections

PROPS = ["EX", "EY", "EZ", "PRXY", "PRYZ", "PRXZ", "GXY", "GYZ", "GXZ", "CTEX", "CTEY", "CTEZ", "DENS"]
SEARCH_DIRS = []   # extra folders searched for /INPUT files (--search <dir>)
V6_BASE_ID, V6_BINS = 10000, 101   # Jabil v5/v6 material IDs: bin = (id - base) % bins
T_GRID = [30.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0, 170.0,
          180.0, 190.0, 200.0, 210.0, 220.0, 230.0, 240.0, 250.0]


def fnum(s):
    s = s.strip()
    return float(s) if s else None


class MatDB(object):
    """MAPDL material tables: mats[mid][label] = ('C', value) or ('T', {loc: (T, value)})."""

    def __init__(self):
        self.mats = {}
        self.tab = {}          # current MPTEMP table loc -> T
        self.next_loc = {}     # (mid, lab) -> next MPDATA location

    def mptemp(self, f):
        if len(f) <= 1 or all(x.strip() == "" for x in f[1:]):
            self.tab = {}
            return
        loc = int(float(f[1])) if f[1].strip() else 1
        for i, x in enumerate(f[2:]):
            if x.strip():
                self.tab[loc + i] = float(x)

    def mp(self, f):
        lab, mid = f[1].strip().upper(), int(float(f[2]))
        if lab in ("UVID", "UMID") or len(f) < 4 or not f[3].strip():
            return
        try:
            self.mats.setdefault(mid, {})[lab] = ("C", float(f[3]))
        except ValueError:
            return
        self.next_loc.pop((mid, lab), None)

    def mpdata(self, f):
        lab, mid = f[1].strip().upper(), int(float(f[2]))
        loc = int(float(f[3])) if len(f) > 3 and f[3].strip() else self.next_loc.get((mid, lab), 1)
        d = self.mats.setdefault(mid, {})
        if loc == 1 or lab not in d or d[lab][0] != "T":
            d[lab] = ("T", {})
        vals = [float(x) for x in f[4:] if x.strip()]
        for i, v in enumerate(vals):
            L = loc + i
            if L not in self.tab:
                raise ValueError("MPDATA %s mat %d loc %d has no MPTEMP temperature" % (lab, mid, L))
            d[lab][1][L] = (self.tab[L], v)
        self.next_loc[(mid, lab)] = loc + len(vals)

    def mpdele(self, f):
        lab = f[1].strip().upper() if len(f) > 1 else "ALL"
        mid = int(float(f[2])) if len(f) > 2 and f[2].strip() else None
        if mid is None:
            return
        if lab in ("ALL", ""):
            self.mats.pop(mid, None)
            for k in [k for k in self.next_loc if k[0] == mid]:
                self.next_loc.pop(k)
        elif mid in self.mats:
            self.mats[mid].pop(lab, None)
            self.next_loc.pop((mid, lab), None)


def value_at(entry, T):
    kind, data = entry
    if kind == "C":
        return data
    pts = sorted(data.values())
    if T <= pts[0][0]:
        return pts[0][1]
    if T >= pts[-1][0]:
        return pts[-1][1]
    for (t0, v0), (t1, v1) in zip(pts[:-1], pts[1:]):
        if t0 <= T <= t1:
            return v0 + (T - t0) / (t1 - t0) * (v1 - v0)
    return pts[-1][1]


def effective(md):
    """Material dict -> {prop: [values on T_GRID]} expanded to orthotropic."""
    m = dict(md)
    if "PRXY" not in m and "NUXY" in m:
        m["PRXY"] = m["NUXY"]
    if "CTEX" not in m and "ALPX" in m:
        m["CTEX"] = m["ALPX"]
    out = {}
    for p in ("EX", "PRXY", "CTEX", "DENS"):
        if p not in m:
            return None
    ex = [value_at(m["EX"], T) for T in T_GRID]
    out["EX"] = ex
    out["EY"] = [value_at(m["EY"], T) for T in T_GRID] if "EY" in m else ex
    out["EZ"] = [value_at(m["EZ"], T) for T in T_GRID] if "EZ" in m else ex
    pr = [value_at(m["PRXY"], T) for T in T_GRID]
    out["PRXY"] = pr
    out["PRYZ"] = [value_at(m["PRYZ"], T) for T in T_GRID] if "PRYZ" in m else pr
    out["PRXZ"] = [value_at(m["PRXZ"], T) for T in T_GRID] if "PRXZ" in m else pr
    g_iso = [e / (2.0 * (1.0 + n)) for e, n in zip(ex, pr)]
    for g in ("GXY", "GYZ", "GXZ"):
        out[g] = [value_at(m[g], T) for T in T_GRID] if g in m else g_iso
    cx = [value_at(m["CTEX"], T) for T in T_GRID]
    out["CTEX"] = cx
    out["CTEY"] = [value_at(m["CTEY"], T) for T in T_GRID] if "CTEY" in m else cx
    out["CTEZ"] = [value_at(m["CTEZ"], T) for T in T_GRID] if "CTEZ" in m else cx
    out["DENS"] = [value_at(m["DENS"], T_GRID[0])] * len(T_GRID)
    out["_explicit"] = set(k for k in m)
    return out


def split_cmd(line):
    s = line.split("!")[0].strip()
    return [x.strip() for x in s.split(",")]


def parse_case(path, log):
    case_dir = path if os.path.isdir(path) else os.path.dirname(path)
    dat = os.path.join(path, "ds.dat") if os.path.isdir(path) else path
    db = MatDB()
    elem_body, elem_mat = {}, {}
    comps = {}
    inputs = []
    state = {"body": None}

    def find_input(fname, ext, d):
        """written path, then a folder with the same name as the written one, then any folder."""
        full = fname + ("." + ext if ext else "")
        if d and os.path.exists(os.path.join(d, full)):
            return os.path.join(d, full)
        want = os.path.basename(d.rstrip("\\/")) if d else ""
        hits = []
        for top in [case_dir] + SEARCH_DIRS:
            for root, _, files in os.walk(top):
                if full in files:
                    hits.append(os.path.join(root, full))
        for h in hits:
            if want and os.path.basename(os.path.dirname(h)) == want:
                return h
        return hits[0] if hits else None

    def emodify(target, mid):
        try:
            elem_mat[int(float(target))] = mid
        except ValueError:
            for e in comps.get(target.upper(), []):
                elem_mat[e] = mid

    def run(lines_iter, src):
        it = iter(lines_iter)
        for line in it:
            s = line.strip()
            if not s:
                continue
            low = s.lower()
            if s.startswith("/com,*********** Elements for Body"):
                m = re.search(r"Body (\d+) '([^']+)'", s)
                state["body"] = m.group(2) if m else s
                continue
            if low.startswith("eblock"):
                next(it)
                for l2 in it:
                    p = l2.split()
                    if p and p[0] == "-1":
                        break
                    if len(p) >= 11:
                        e = int(p[10])
                        elem_body[e] = state["body"]
                        elem_mat[e] = int(p[0])
                        nn = int(p[8])
                        extra = int(math.ceil(max(0, nn - 8) / 19.0)) if nn > 8 else 0
                        for _ in range(extra):
                            next(it)
                continue
            if low.startswith("cmblock"):
                f = [x.strip() for x in s.split(",")]
                name, kind, n = f[1].upper(), f[2].upper(), int(f[3])
                next(it)
                ids = []
                while len(ids) < n:
                    ids += [int(x) for x in next(it).split()]
                if kind.startswith("ELEM"):
                    out = []
                    for k, v in enumerate(ids):
                        if v < 0:
                            out += list(range(abs(ids[k - 1]) + 1, -v + 1))
                        else:
                            out.append(v)
                    comps[name] = out
                continue
            if low.startswith("solve"):
                return True
            if low.startswith("/inp"):
                f = [x.strip().strip("'\"") for x in split_cmd(s)]
                fname, ext = f[1], (f[2] if len(f) > 2 else "")
                d = f[3] if len(f) > 3 else ""
                p = find_input(fname, ext, d)
                inputs.append((src, fname + "." + ext, p))
                if p is None:
                    log.append("MISSING /INPUT file %s.%s (written dir %s)" % (fname, ext, d))
                    continue
                with open(p, "r", errors="ignore") as fh:
                    if run(fh, os.path.basename(p)):
                        return True
                continue
            f = split_cmd(s)
            c = f[0].upper()
            try:
                if c == "MPTEMP":
                    db.mptemp(f)
                elif c == "MPDATA":
                    db.mpdata(f)
                elif c == "MP":
                    db.mp(f)
                elif c == "MPDELE":
                    db.mpdele(f)
                elif c in ("EMOD", "EMODI", "EMODIF") and len(f) >= 4 and f[2].upper() == "MAT":
                    emodify(f[1], int(float(f[3])))
            except (ValueError, IndexError) as ex:
                log.append("%s: cannot parse '%s' (%s)" % (src, s[:80], ex))
        return False

    with open(dat, "r", errors="ignore") as fh:
        run(fh, "ds.dat")
    return {"dir": case_dir, "db": db, "elem_body": elem_body, "elem_mat": elem_mat, "inputs": inputs}


def rel(a, b):
    d = max(abs(a), abs(b))
    return 0.0 if d == 0.0 else abs(b - a) / d


def fraction(rho, rho_base, rho_cu):
    if rho_base is None or abs(rho_cu - rho_base) < 1e-30:
        return None
    return (rho - rho_base) / (rho_cu - rho_base)


def cu_fraction(mid, E, eff, eb_mid, rho_cu):
    """Copper fraction of an element material: Jabil IDs decode the bin, otherwise density vs. the
    Mechanical (eblock) material of the element."""
    if mid >= V6_BASE_ID:
        return ((mid - V6_BASE_ID) % V6_BINS) / float(V6_BINS - 1)
    if mid == eb_mid:
        return 0.0
    if E is None or eb_mid not in eff or eff[eb_mid] is None:
        return None
    return fraction(E["DENS"][0], eff[eb_mid]["DENS"][0], rho_cu)


def best_rule(p, r):
    if not r["n"]:
        return ""
    keys = ["VOIGT", "REUSS"] + (["TURNER"] if p.startswith("CTE") else []) + (["FROM_E_NU"] if p.startswith("G") else [])
    return min(keys, key=lambda k: r[k])


def mixing_check(case, eblock_mat, eff_cache, out_csv):
    """For every mixed material: v from DENS, then error of Voigt / Reuss / Turner per property."""
    db = case["db"]
    # copper = material with the largest density that is used by some element
    used = set(case["elem_mat"].values())
    cu_mid = max((m for m in used if m in db.mats and eff_cache.get(m)), key=lambda m: eff_cache[m]["DENS"][0])
    CU = eff_cache[cu_mid]
    rho_cu = CU["DENS"][0]
    pairs = collections.Counter()
    for e, m in case["elem_mat"].items():
        pairs[(eblock_mat[e], m)] += 1
    err = collections.defaultdict(lambda: {"VOIGT": 0.0, "REUSS": 0.0, "TURNER": 0.0, "FROM_E_NU": 0.0, "n": 0})
    for (mb, m), n in pairs.items():
        if mb == m or m == cu_mid:
            continue
        C = CU
        if m >= V6_BASE_ID:
            # Jabil material: FR4 base = bin 0, copper = bin 100 of the same FR4 block
            b0 = V6_BASE_ID + ((m - V6_BASE_ID) // V6_BINS) * V6_BINS
            F, M, C = eff_cache.get(b0), eff_cache.get(m), eff_cache.get(b0 + V6_BINS - 1)
            v = ((m - V6_BASE_ID) % V6_BINS) / float(V6_BINS - 1)
            if not F or not M or not C:
                continue
        else:
            F, M = eff_cache.get(mb), eff_cache.get(m)
            if not F or not M:
                continue
            v = fraction(M["DENS"][0], F["DENS"][0], rho_cu)
        if v is None or v <= 1e-6 or v >= 1 - 1e-6:
            continue
        CUv = C
        grp = "jabil_id" if m >= V6_BASE_ID else "ansys_native"
        for p in PROPS:
            if p not in M["_explicit"]:
                continue      # derived value (e.g. G of an isotropic material), not mixed by itself
            for i in range(len(T_GRID)):
                a_c, a_f, val = CUv[p][i], F[p][i], M[p][i]
                voigt = v * a_c + (1 - v) * a_f
                reuss = 1.0 / (v / a_c + (1 - v) / a_f) if a_c and a_f else voigt
                if p.startswith("CTE"):
                    ec = CUv["EZ" if p == "CTEZ" else "EX"][i]
                    ef = F["EZ" if p == "CTEZ" else "EX"][i]
                    turner = (a_c * ec * v + a_f * ef * (1 - v)) / (ec * v + ef * (1 - v))
                else:
                    turner = voigt
                if p.startswith("G"):
                    em = M["EX" if p == "GXY" else "EZ"][i]
                    from_e_nu = em / (2.0 * (1.0 + M["PRXY"][i]))
                else:
                    from_e_nu = None
                r = err[(grp, p)]
                if from_e_nu is not None:
                    r["FROM_E_NU"] = max(r["FROM_E_NU"], rel(from_e_nu, val))
                r["VOIGT"] = max(r["VOIGT"], rel(voigt, val))
                r["REUSS"] = max(r["REUSS"], rel(reuss, val))
                r["TURNER"] = max(r["TURNER"], rel(turner, val))
                r["n"] += 1
    with open(out_csv, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["material_group", "property", "n_points", "max_rel_err_voigt_ROM", "max_rel_err_reuss",
                    "max_rel_err_turner", "max_rel_err_G_from_E_nu", "best"])
        for grp in ("ansys_native", "jabil_id"):
            for p in PROPS:
                r = err[(grp, p)]
                if not r["n"]:
                    continue
                w.writerow([grp, p, r["n"], "%.3e" % r["VOIGT"], "%.3e" % r["REUSS"], "%.3e" % r["TURNER"],
                            "%.3e" % r["FROM_E_NU"] if p.startswith("G") else "", best_rule(p, r)])
    return cu_mid, err


def main():
    argv = sys.argv[1:]
    tol = 1e-4
    args = []
    i = 0
    while i < len(argv):
        if argv[i] == "--tol":
            tol = float(argv[i + 1])
            i += 2
        elif argv[i] == "--search":
            SEARCH_DIRS.append(argv[i + 1])
            i += 2
        else:
            args.append(argv[i])
            i += 1
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)
    pa, pb = args[0], args[1]
    out = args[2] if len(args) > 2 else os.path.join(os.getcwd(), "compare_out")
    os.makedirs(out, exist_ok=True)
    log = []
    cases = []
    for tag, p in (("A", pa), ("B", pb)):
        print("Parsing case %s: %s" % (tag, p))
        lg = []
        c = parse_case(p, lg)
        log += ["[%s] %s" % (tag, x) for x in lg]
        cases.append(c)
    A, B = cases
    # eblock (Mechanical) material per element, needed to back-calculate the copper fraction
    def eblock_materials(path):
        dat = os.path.join(path, "ds.dat") if os.path.isdir(path) else path
        res = {}
        with open(dat, "r", errors="ignore") as fh:
            it = iter(fh)
            for line in it:
                if line.lower().startswith("eblock"):
                    next(it)
                    for l2 in it:
                        p = l2.split()
                        if p and p[0] == "-1":
                            break
                        if len(p) >= 11:
                            res[int(p[10])] = int(p[0])
                            if int(p[8]) > 8:
                                next(it)
                elif line.startswith("/wb,mat,start"):
                    break
        return res
    ebA, ebB = eblock_materials(pa), eblock_materials(pb)
    if set(A["elem_body"]) != set(B["elem_body"]):
        log.append("WARNING: element sets differ (A %d, B %d)" % (len(A["elem_body"]), len(B["elem_body"])))
    effA, effB = {}, {}
    for c, eff in ((A, effA), (B, effB)):
        for mid, md in c["db"].mats.items():
            eff[mid] = effective(md)
    # copper density from each case (densest used material)
    def rho_cu_of(c, eff):
        used = set(c["elem_mat"].values())
        return max(eff[m]["DENS"][0] for m in used if eff.get(m))
    rcuA, rcuB = rho_cu_of(A, effA), rho_cu_of(B, effB)

    pair_cache = {}
    by_body = collections.OrderedDict()
    worst = {p: (0.0, None) for p in PROPS}
    n_diff = 0
    n_bin_diff = 0
    elems = sorted(set(A["elem_body"]) & set(B["elem_body"]))
    fe = open(os.path.join(out, "elements_diff.csv"), "w", newline="")
    we = csv.writer(fe)
    we.writerow(["element", "body", "matA", "matB", "cu_pct_A", "cu_pct_B", "worst_property", "worst_T_C",
                 "valueA", "valueB", "max_rel_diff"])
    for e in elems:
        body = A["elem_body"][e]
        ma, mb = A["elem_mat"][e], B["elem_mat"][e]
        key = (ma, mb)
        if key not in pair_cache:
            EA, EB = effA.get(ma), effB.get(mb)
            res = {}
            if EA is None or EB is None:
                res = None
            else:
                for p in PROPS:
                    best = (0.0, 0)
                    for i in range(len(T_GRID)):
                        r = rel(EA[p][i], EB[p][i])
                        if r > best[0]:
                            best = (r, i)
                    res[p] = best
            pair_cache[key] = res
        res = pair_cache[key]
        bb = by_body.setdefault(body, {"n": 0, "nd": 0, "nbin": 0, "max": dict((p, 0.0) for p in PROPS)})
        bb["n"] += 1
        EA, EB = effA.get(ma), effB.get(mb)
        fa = cu_fraction(ma, EA, effA, ebA.get(e), rcuA)
        fb = cu_fraction(mb, EB, effB, ebB.get(e), rcuB)
        if fa is not None and fb is not None and round(fa * 100) != round(fb * 100):
            bb["nbin"] += 1
            n_bin_diff += 1
        if res is None:
            log.append("element %d: material %s/%s undefined" % (e, ma, mb))
            continue
        mx = max(res.values(), key=lambda t: t[0])
        for p in PROPS:
            if res[p][0] > bb["max"][p]:
                bb["max"][p] = res[p][0]
            if res[p][0] > worst[p][0]:
                worst[p] = (res[p][0], e)
        if mx[0] > tol:
            n_diff += 1
            bb["nd"] += 1
            wp = max(PROPS, key=lambda p: res[p][0])
            i = res[wp][1]
            we.writerow([e, body, ma, mb, "" if fa is None else "%.2f" % (fa * 100), "" if fb is None else "%.2f" % (fb * 100),
                         wp, T_GRID[i], "%.8g" % EA[wp][i], "%.8g" % EB[wp][i], "%.3e" % mx[0]])
    fe.close()

    with open(os.path.join(out, "by_body.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["body", "n_elem", "n_elem_diff", "n_elem_bin_diff"] + ["max_rel_%s" % p for p in PROPS])
        for body, bb in by_body.items():
            w.writerow([body, bb["n"], bb["nd"], bb["nbin"]] + ["%.3e" % bb["max"][p] for p in PROPS])

    with open(os.path.join(out, "material_pairs.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["matA", "matB", "n_elem", "property", "T_C", "valueA", "valueB", "rel_diff"])
        cnt = collections.Counter((A["elem_mat"][e], B["elem_mat"][e]) for e in elems)
        for (ma, mb), n in sorted(cnt.items()):
            EA, EB = effA.get(ma), effB.get(mb)
            if not EA or not EB:
                continue
            for p in PROPS:
                for i, T in enumerate(T_GRID):
                    r = rel(EA[p][i], EB[p][i])
                    if r > tol:
                        w.writerow([ma, mb, n, p, T, "%.8g" % EA[p][i], "%.8g" % EB[p][i], "%.3e" % r])

    mix = {}
    for tag, c, eff, ebm in (("A", A, effA, ebA), ("B", B, effB, ebB)):
        try:
            mix[tag] = mixing_check(c, ebm, eff, os.path.join(out, "mixing_check_%s.csv" % tag))
        except Exception as ex:
            log.append("mixing check %s failed: %s" % (tag, ex))

    S = []
    S.append("Case A: %s" % pa)
    S.append("Case B: %s" % pb)
    for tag, c in (("A", A), ("B", B)):
        S.append("Case %s /INPUT files: %d (%d missing)" % (tag, len(c["inputs"]), len([x for x in c["inputs"] if x[2] is None])))
        for src, f, p in c["inputs"]:
            S.append("    %s -> %s" % (f, p if p else "MISSING"))
    S.append("Elements compared: %d | with any property difference > %.1e: %d | different 1%% bin: %d" %
             (len(elems), tol, n_diff, n_bin_diff))
    S.append("Worst relative difference per property (element):")
    for p in PROPS:
        r, e = worst[p]
        S.append("    %-5s %.3e  (element %s, body %s)" % (p, r, e, A["elem_body"].get(e) if e else ""))
    for tag in ("A", "B"):
        if tag in mix:
            cu_mid, err = mix[tag]
            for grp in ("ansys_native", "jabil_id"):
                if not any(err[(grp, p)]["n"] for p in PROPS):
                    continue
                S.append("Mixing rule check case %s, %s materials (copper = mat %d): best rule per property"
                         % (tag, grp, cu_mid))
                for p in PROPS:
                    r = err[(grp, p)]
                    if not r["n"]:
                        continue
                    extra = ""
                    if p.startswith("CTE"):
                        extra = ", Turner %.2e" % r["TURNER"]
                    if p.startswith("G"):
                        extra = ", G=E/(2(1+nu)) %.2e" % r["FROM_E_NU"]
                    S.append("    %-5s %-9s (Voigt %.2e, Reuss %.2e%s)" % (p, best_rule(p, r), r["VOIGT"], r["REUSS"], extra))
    S.append("Note: mixing check base = Mechanical (eblock) material for Ansys materials; for Jabil IDs (>= %d) "
             "base = bin 0 and copper = bin 100 of the same FR4 block (config data)." % V6_BASE_ID)
    S += ["LOG: " + x for x in log[:200]]
    if len(log) > 200:
        S.append("LOG: ... %d more lines" % (len(log) - 200))
    txt = "\n".join(S)
    open(os.path.join(out, "summary.txt"), "w").write(txt)
    print(txt)
    print("Output: %s" % out)


if __name__ == "__main__":
    main()
