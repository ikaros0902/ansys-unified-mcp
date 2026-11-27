# -*- coding: utf-8 -*-
"""Step 9 - level the BGA-shadow Z displacement and report the warpage.

Input per case (both come from the same Mechanical solve):
  * the exported result file  : node number + Z displacement (Directional Deformation Z,
                                right-click > Export > Text File; .txt / .csv / .xls text)
  * ds.dat                    : solver input file; its NBLOCK holds X, Y, Z of every node

What it does
  1. looks up X, Y of every exported node in the NBLOCK of ds.dat (by node number)
  2. optional: subtracts one case from another (difference between two temperatures)
  3. fits the plane z = a*x + b*y + c through the nodes (least squares by default)
  4. removes the plane  ("detrend": z - plane;  "rotate": rigid rotation of the point cloud)
  5. writes   <case>_leveled.csv, <case>_report.md, <case>.html (interactive, self-contained),
              <case>_contour.png, <case>_3d.png   and   leveling_summary.csv

How to use
  All settings live in the "leveling" section of the project JSON
  (see 4_config/project_config.template.json). Then either
      python level_bga_shadow.py <project.json> [--case NAME]
  or set CONFIG_FILE below and press Run in VS Code.

Exit codes: 0 done, 2 done but a WARNING needs a human decision, 3 input error.
"""
from __future__ import annotations

import csv
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

# ----------------------------------------------------------------------------------------
CONFIG_FILE = r""          # e.g. r"C:\Projects\TH5\TH5_SYE.json"  ("" = use the command line)
# ----------------------------------------------------------------------------------------

EXIT_OK, EXIT_WARN, EXIT_INPUT = 0, 2, 3
UNIT_TO_MM = {"m": 1000.0, "mm": 1.0, "um": 1e-3}
MIL_PER_MM = 1000.0 / 25.4

# robust fits (only used when leveling.method is not OLS)
RANSAC_MAX_TRIALS, RANSAC_RESID_THRESH_MM, RANSAC_SEED = 2000, 0.003, 42
IRLS_MAX_ITERS, IRLS_TOL, HUBER_K, TUKEY_C, MAD_SCALE = 50, 1e-12, 1.345, 4.685, 1.4826

# sanity limits for a BGA-shadow area (a value outside raises a WARNING, never a silent fix)
MAX_ABS_UZ_MM = 20.0         # raw displacement larger than this -> unit mistake?
MAX_WARPAGE_UM = 2000.0      # leveled warpage larger than this -> unit mistake?
MIN_WARPAGE_UM = 0.01        # leveled warpage smaller than this -> unit mistake / wrong result?
MAX_TILT_DEG = 2.0           # fitted plane steeper than this -> wrong column / wrong unit?
MIN_NODES = 9


class InputError(Exception):
    pass


# ======================================================================================
# reading
# ======================================================================================
def _read_table(path: Path):
    """Exported result file -> (header list, rows as lists of str). Tab, comma, semicolon or blanks."""
    raw = None
    for enc in ("utf-8-sig", "utf-8", "cp950", "latin-1"):
        try:
            raw = path.read_text(encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    if raw is None:
        raise InputError(f"cannot decode {path}")
    lines = [l for l in raw.splitlines() if l.strip()]
    if len(lines) < 2:
        raise InputError(f"{path.name}: no data rows")
    head = lines[0]
    sep = "\t" if "\t" in head else ("," if "," in head else (";" if ";" in head else None))
    split = (lambda s: [c.strip() for c in s.split(sep)]) if sep else (lambda s: s.split())
    return split(head), [split(l) for l in lines[1:]]


def _num(tok: str) -> float:
    return float(tok.strip().replace("D", "E").replace("d", "e"))


def read_displacement(path: Path, value_column: str | None):
    """-> (node ids int array, values float array, value header, unit found in the header or None)."""
    if not path.is_file():
        raise InputError(f"result file not found: {path}")
    header, rows = _read_table(path)
    norm = [re.sub(r"[\s_]+", "", h.lower()) for h in header]
    node_i = next((i for i, h in enumerate(norm) if h in ("nodenumber", "node", "nodeid", "nodeno", "id")), 0)
    cand = [i for i in range(len(header)) if i != node_i]
    if value_column:
        want = re.sub(r"[\s_]+", "", value_column.lower())
        hit = [i for i in cand if norm[i] == want] or [i for i in cand if want in norm[i]]
        if len(hit) != 1:
            raise InputError(f"{path.name}: leveling value_column '{value_column}' matches {len(hit)} columns "
                             f"of {header}")
        val_i = hit[0]
    elif len(cand) == 1:
        val_i = cand[0]
    else:
        hit = [i for i in cand if "deformation" in norm[i] or norm[i].startswith("uz")]
        if len(hit) != 1:
            raise InputError(f"{path.name}: several value columns {[header[i] for i in cand]}. "
                             f"Ask which one is the Z displacement and set leveling 'value_column'.")
        val_i = hit[0]
    nodes, vals = [], []
    for r in rows:
        if len(r) <= max(node_i, val_i):
            continue
        try:
            nodes.append(int(round(_num(r[node_i]))))
            vals.append(_num(r[val_i]))
        except ValueError:
            continue
    if not nodes:
        raise InputError(f"{path.name}: no numeric rows in columns '{header[node_i]}', '{header[val_i]}'")
    m = re.search(r"\(\s*(mm|m|um|µm|μm)\s*\)", header[val_i], re.I)
    unit = None if not m else m.group(1).lower().replace("µ", "u").replace("μ", "u")
    return np.array(nodes), np.array(vals, float), header[val_i], unit


def read_nblock(dat: Path, wanted: set[int]):
    """Coordinates of the wanted nodes from the NBLOCK(s) of a MAPDL input file.
    -> ({node: (x, y, z)}, unit system text found in the file or None)"""
    if not dat.is_file():
        raise InputError(f"ds.dat not found: {dat}")
    found: dict[int, tuple[float, float, float]] = {}
    units = None
    in_block = False
    fmt = None
    fmt_re = re.compile(r"\(\s*(\d+)\s*i\s*(\d+)\s*,\s*\d+\s*e\s*(\d+)", re.I)
    with open(dat, "r", encoding="latin-1", errors="replace") as fh:
        for line in fh:
            if not in_block:
                low = line[:8].lower()
                if low.startswith("nblock"):
                    in_block, fmt = True, None
                elif units is None and line.startswith("/com") and "consistent" in line.lower():
                    m = re.search(r"consistent\s+(\S+)\s+units", line, re.I)
                    units = m.group(1).upper() if m else None
                continue
            if fmt is None and "(" in line:
                m = fmt_re.search(line)
                if m:
                    fmt = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
                    continue
            s = line.strip()
            if s.startswith("-1") or s[:1].isalpha():
                in_block = False
                if len(found) == len(wanted):
                    break
                continue
            if not s:
                continue
            xyz = None
            try:
                if fmt:                                   # fixed width: n ints of width w, then floats
                    n_int, iw, ew = fmt                   # (trailing zero coordinates may be left out)
                    nid = int(line[:iw])
                    if nid not in wanted:
                        continue
                    st = n_int * iw
                    xyz = [(_num(line[st + k * ew: st + (k + 1) * ew]) if line[st + k * ew: st + (k + 1) * ew].strip()
                            else 0.0) for k in range(3)]
            except (ValueError, IndexError):
                xyz = None
            if xyz is None:                               # free format: node [ints] x y z
                try:
                    p = s.split()
                    nid = int(p[0])
                    if nid not in wanted:
                        continue
                    v = p[fmt[0]:] if fmt else p[-3:]
                    xyz = [_num(t) for t in v[:3]] + [0.0] * (3 - len(v[:3]))
                except (ValueError, IndexError):
                    continue
            found[nid] = (xyz[0], xyz[1], xyz[2])
    return found, units


# ======================================================================================
# plane fit and leveling
# ======================================================================================
def _ols(A, z):
    return np.linalg.lstsq(A, z, rcond=None)[0]


def _irls(A, z, kind):
    coef = _ols(A, z)
    for _ in range(IRLS_MAX_ITERS):
        r = z - A @ coef
        s = MAD_SCALE * np.median(np.abs(r - np.median(r)))
        if not np.isfinite(s) or s < 1e-15:
            break
        if kind == "huber":
            u = np.abs(r) / (HUBER_K * s)
            w = np.where(u <= 1.0, 1.0, 1.0 / np.maximum(u, 1e-12))
        else:
            w = np.square(np.clip(1.0 - np.square(r / (TUKEY_C * s)), 0.0, None))
        sw = np.sqrt(w)
        new = _ols(A * sw[:, None], z * sw)
        done = np.max(np.abs(new - coef)) < IRLS_TOL
        coef = new
        if done:
            break
    return coef


def _ransac(A, z):
    rng = np.random.default_rng(RANSAC_SEED)
    best, best_n = None, -1
    for _ in range(RANSAC_MAX_TRIALS):
        idx = rng.choice(len(z), 3, replace=False)
        try:
            c = np.linalg.solve(A[idx], z[idx])
        except np.linalg.LinAlgError:
            continue
        inl = np.abs(z - A @ c) <= RANSAC_RESID_THRESH_MM
        if inl.sum() > best_n:
            best, best_n = inl, int(inl.sum())
            if best_n >= 0.98 * len(z):
                break
    if best is None or best_n < 3:
        raise InputError("RANSAC found no plane; use method OLS")
    return _ols(A[best], z[best])


def fit_plane(x, y, z, method="OLS"):
    """z = a*x + b*y + c -> (a, b, c)."""
    A = np.column_stack([x, y, np.ones_like(x)])
    m = method.strip().lower()
    if m == "ols":
        coef = _ols(A, z)
    elif m in ("huber", "tukey"):
        coef = _irls(A, z, m)
    elif m == "ransac":
        coef = _ransac(A, z)
    else:
        raise InputError(f"leveling method '{method}' unknown (OLS, RANSAC, Huber, Tukey)")
    return float(coef[0]), float(coef[1]), float(coef[2])


def level(x, y, z, method="OLS", mode="detrend"):
    """All lengths in mm. -> (x_out, y_out, z_leveled, info). x_out/y_out start at 0."""
    a, b, c = fit_plane(x, y, z, method)
    tilt = math.degrees(math.atan(math.hypot(a, b)))
    mode = mode.strip().lower()
    if mode == "detrend":
        xo, yo, zo = x.copy(), y.copy(), z - (a * x + b * y + c)
    elif mode == "rotate":                       # rigid rotation: plane normal (-a, -b, 1) -> +Z
        n = np.array([-a, -b, 1.0]) / math.sqrt(a * a + b * b + 1.0)
        v = np.cross(n, [0.0, 0.0, 1.0])
        s, cth = np.linalg.norm(v), n[2]
        if s < 1e-15:
            R = np.eye(3)
        else:
            k = v / s
            K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
            R = np.eye(3) + s * K + (1.0 - cth) * (K @ K)
        P = R @ np.vstack([x - x.mean(), y - y.mean(), z - (a * x.mean() + b * y.mean() + c)])
        xo, yo, zo = P[0], P[1], P[2]
    else:
        raise InputError(f"leveling mode '{mode}' unknown (detrend, rotate)")
    return xo - xo.min(), yo - yo.min(), zo, {"a": a, "b": b, "c": c, "tilt_deg": tilt, "mode": mode,
                                              "method": method.upper()}


def warpage_shape(x, y, z):
    """Warpage = max - min of the leveled Z. Shape: the extreme nearer to the area centre decides.
    Max nearer to the centre -> 'Cry' (centre high, signed warpage negative); min nearer -> 'Smile'."""
    cx, cy = (x.min() + x.max()) / 2.0, (y.min() + y.max()) / 2.0
    d2 = (x - cx) ** 2 + (y - cy) ** 2

    def pick(val):
        cand = np.where(z == val)[0]
        return int(cand[np.argmin(d2[cand])])
    i_max, i_min = pick(z.max()), pick(z.min())
    d_max, d_min = math.sqrt(d2[i_max]), math.sqrt(d2[i_min])
    w = float(z[i_max] - z[i_min])
    if abs(d_max - d_min) <= 1e-9:
        shape, signed = "Undetermined", 0.0
    elif d_max < d_min:
        shape, signed = "Cry", -w
    else:
        shape, signed = "Smile", w
    return {"warpage_mm": w, "signed_mm": signed, "shape": shape, "i_max": i_max, "i_min": i_min,
            "center": (cx, cy), "d_max": d_max, "d_min": d_min}


# ======================================================================================
# outputs
# ======================================================================================
def _grid(x, y, z, n=140):
    """Scattered nodes -> regular grid (linear interpolation on the Delaunay triangles, NaN outside)."""
    import matplotlib.tri as mtri
    tri = mtri.Triangulation(x, y)
    xi = np.linspace(x.min(), x.max(), n)
    yi = np.linspace(y.min(), y.max(), max(2, int(round(n * (np.ptp(y) / max(np.ptp(x), 1e-12))))))
    X, Y = np.meshgrid(xi, yi)
    Z = mtri.LinearTriInterpolator(tri, z)(X, Y)
    return xi, yi, np.ma.filled(Z, np.nan), tri


def write_png(base: Path, title: str, x, y, z_um):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    xi, yi, Z, tri = _grid(x, y, z_um)
    fig, ax = plt.subplots(figsize=(7.2, 6.0), dpi=160)
    cf = ax.tricontourf(tri, z_um, levels=24, cmap="jet")
    ax.set_aspect("equal")
    ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)"); ax.set_title(title, fontsize=10)
    fig.colorbar(cf, ax=ax, label="Leveled Z (um)")
    fig.tight_layout(); fig.savefig(f"{base}_contour.png"); plt.close(fig)
    fig = plt.figure(figsize=(7.6, 6.0), dpi=160)
    ax = fig.add_subplot(111, projection="3d")
    sf = ax.plot_trisurf(tri, z_um, cmap="jet", linewidth=0.1, antialiased=True)
    ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)"); ax.set_zlabel("Leveled Z (um)")
    ax.set_title(title, fontsize=10)
    fig.colorbar(sf, ax=ax, shrink=0.6, label="Leveled Z (um)")
    fig.tight_layout(); fig.savefig(f"{base}_3d.png"); plt.close(fig)


def write_html(path: Path, title: str, x, y, z_um):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    xi, yi, Z, _ = _grid(x, y, z_um)
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "surface"}, {"type": "xy"}]],
                        subplot_titles=("3D surface", "Contour"), horizontal_spacing=0.06)
    fig.add_trace(go.Surface(x=xi, y=yi, z=Z, colorscale="Jet", colorbar=dict(title="Z (um)", x=0.46, len=0.8),
                             hovertemplate="X %{x:.2f} mm<br>Y %{y:.2f} mm<br>Z %{z:.2f} um<extra></extra>"),
                  row=1, col=1)
    fig.add_trace(go.Contour(x=xi, y=yi, z=Z, colorscale="Jet", ncontours=24, showscale=False,
                             hovertemplate="X %{x:.2f} mm<br>Y %{y:.2f} mm<br>Z %{z:.2f} um<extra></extra>"),
                  row=1, col=2)
    fig.add_trace(go.Scatter(x=x, y=y, mode="markers", marker=dict(size=3, color="rgba(0,0,0,0.35)"),
                             name="nodes", hovertemplate="node X %{x:.2f} Y %{y:.2f}<extra></extra>"), row=1, col=2)
    fig.update_xaxes(title_text="X (mm)", row=1, col=2)
    fig.update_yaxes(title_text="Y (mm)", scaleanchor="x2", scaleratio=1, row=1, col=2)
    fig.update_layout(title=title, height=720, showlegend=False,
                      scene=dict(xaxis_title="X (mm)", yaxis_title="Y (mm)", zaxis_title="Leveled Z (um)",
                                 aspectmode="manual", aspectratio=dict(x=1, y=float(np.ptp(y) / max(np.ptp(x), 1e-12)),
                                                                       z=0.45)))
    fig.write_html(str(path), include_plotlyjs=True, full_html=True)      # self-contained: opens offline


def write_case(out_dir: Path, name: str, src: list[str], nodes, xb, yb, raw_mm, xo, yo, z_mm, info, res, warns, opts):
    out_dir.mkdir(parents=True, exist_ok=True)
    base = out_dir / name
    z_um = z_mm * 1000.0
    with open(f"{base}_leveled.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["node", "X_board_mm", "Y_board_mm", "X_local_mm", "Y_local_mm", "UZ_input_mm",
                    "Z_leveled_um", "Z_leveled_mil"])
        for i in range(len(nodes)):
            w.writerow([int(nodes[i]), f"{xb[i]:.6f}", f"{yb[i]:.6f}", f"{xo[i]:.6f}", f"{yo[i]:.6f}",
                        f"{raw_mm[i]:.9f}", f"{z_um[i]:.4f}", f"{z_mm[i] * MIL_PER_MM:.5f}"])
    w_um, w_mil = res["warpage_mm"] * 1000.0, res["warpage_mm"] * MIL_PER_MM
    title = f"{name}: warpage {w_um:.2f} um ({w_mil:.3f} mil), {res['shape']}"
    if opts["png"]:
        write_png(base, title, xo, yo, z_um)
    if opts["html"]:
        write_html(Path(f"{base}.html"), title, xo, yo, z_um)
    i1, i2 = res["i_max"], res["i_min"]
    L = [f"# BGA-shadow leveling report - {name}", "",
         f"Result: **warpage {w_um:.2f} um = {w_mil:.3f} mil, shape {res['shape']}** "
         f"(signed {res['signed_mm'] * 1000:.2f} um)", "",
         "| Item | Value |", "|---|---|"]
    L += [f"| Source | {s} |" for s in src]
    L += [f"| Nodes | {len(nodes)} |",
          f"| Area (board coordinates) | X {xb.min():.3f} .. {xb.max():.3f} mm, Y {yb.min():.3f} .. {yb.max():.3f} mm |",
          f"| Input unit / sign | {opts['z_unit']} / {'flipped (x -1)' if opts['flip_z'] else 'as exported'} |",
          f"| Input UZ range | {raw_mm.min() * 1000:.2f} .. {raw_mm.max() * 1000:.2f} um |",
          f"| Plane fit | {info['method']}, z = {info['a']:.6e}*x + {info['b']:.6e}*y + {info['c']:.6e} (mm) |",
          f"| Tilt removed | {info['tilt_deg']:.5f} deg, mode {info['mode']} |",
          f"| Leveled max | {z_um[i1]:.2f} um at local ({xo[i1]:.2f}, {yo[i1]:.2f}) mm, "
          f"{res['d_max']:.2f} mm from the centre |",
          f"| Leveled min | {z_um[i2]:.2f} um at local ({xo[i2]:.2f}, {yo[i2]:.2f}) mm, "
          f"{res['d_min']:.2f} mm from the centre |",
          "",
          "Shape rule: the extreme that lies nearer to the centre of the area decides. Maximum nearer to the "
          "centre = **Cry** (centre high, signed value negative); minimum nearer = **Smile** (centre low, signed "
          "value positive). The sign follows the Z values after the optional flip.", ""]
    if warns:
        L += ["## Warnings (a human must confirm before the result is used)", ""] + [f"- {t}" for t in warns] + [""]
    files = [f"`{name}_leveled.csv`"] + ([f"`{name}.html`"] if opts["html"] else []) \
        + ([f"`{name}_contour.png`", f"`{name}_3d.png`"] if opts["png"] else [])
    L += ["Files: " + ", ".join(files), ""]
    Path(f"{base}_report.md").write_text("\n".join(L), encoding="utf-8")
    return w_um, w_mil


# ======================================================================================
# driver
# ======================================================================================
def run(config_path: Path, only_case: str | None = None) -> int:
    config_path = Path(config_path).resolve()
    try:
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
        lv = cfg.get("leveling")
        if not lv or not lv.get("cases"):
            raise InputError(f"{config_path.name}: section 'leveling' with at least one entry in 'cases' is missing "
                             f"(see 4_config/project_config.template.json)")
        base = config_path.parent
        rel = lambda p: p if Path(p).is_absolute() else (base / p).resolve()   # noqa: E731
        z_unit = str(lv.get("z_unit") or "mm").lower()
        xy_unit = str(lv.get("xy_unit") or "mm").lower()
        if z_unit not in UNIT_TO_MM or xy_unit not in UNIT_TO_MM:
            raise InputError("leveling z_unit / xy_unit must be one of m, mm, um")
        opts = {"z_unit": z_unit, "flip_z": bool(lv.get("flip_z", False)), "html": bool(lv.get("html", True)),
                "png": bool(lv.get("png", True))}
        mode, method = lv.get("mode") or "detrend", lv.get("method") or "OLS"
        out_root = Path(rel(lv.get("output_dir") or "leveling"))
        print(f"leveling: mode {mode}, method {method}, z_unit {z_unit}, flip_z {opts['flip_z']}, output {out_root}")

        data = {}                       # case name -> dict(nodes, x, y, zc, raw_mm, src, warns)
        for c in lv["cases"]:
            name = str(c.get("name") or "").strip()
            if not name or not c.get("result") or not c.get("dat"):
                raise InputError("every leveling case needs 'name', 'result' (exported file) and 'dat' (ds.dat)")
            if not re.fullmatch(r"[A-Za-z0-9_.\-]+", name):
                raise InputError(f"case name '{name}': use letters, digits, _ . - only")
            res_p, dat_p = Path(rel(c["result"])), Path(rel(c["dat"]))
            nodes, vals, col, head_unit = read_displacement(res_p, c.get("value_column") or lv.get("value_column"))
            warns = []
            if head_unit and head_unit != z_unit:
                raise InputError(f"{res_p.name}: header says '{col}' but leveling z_unit is '{z_unit}'. "
                                 f"Ask which is right and fix the JSON.")
            if not head_unit:
                warns.append(f"{res_p.name}: column '{col}' states no unit; z_unit '{z_unit}' from the JSON was used. "
                             f"Confirm the unit of the export.")
            xyz, dat_units = read_nblock(dat_p, set(int(n) for n in nodes))
            if dat_units and {"NMM": "mm", "MKS": "m", "UMKS": "um"}.get(dat_units, xy_unit) != xy_unit:
                raise InputError(f"{dat_p.name} says consistent {dat_units} units but leveling xy_unit is '{xy_unit}'")
            keep = np.array([int(n) in xyz for n in nodes])
            if not keep.any():
                raise InputError(f"none of the {len(nodes)} nodes of {res_p.name} is in the NBLOCK of {dat_p.name}: "
                                 f"the two files are not from the same solve")
            if not keep.all():
                warns.append(f"{int((~keep).sum())} of {len(nodes)} nodes are not in {dat_p.name} and were dropped: "
                             f"are both files from the same solve?")
            nodes, vals = nodes[keep], vals[keep]
            P = np.array([xyz[int(n)] for n in nodes]) * UNIT_TO_MM[xy_unit]
            raw_mm = vals * UNIT_TO_MM[z_unit] * (-1.0 if opts["flip_z"] else 1.0)
            if np.ptp(P[:, 2]) > 1e-3:
                warns.append(f"node Z coordinates span {np.ptp(P[:, 2]):.4f} mm: the selection is not one flat surface")
            data[name] = {"nodes": nodes, "x": P[:, 0], "y": P[:, 1], "raw": raw_mm, "warns": warns,
                          "src": [f"`{res_p.name}` column `{col}`", f"`{dat_p.name}`"
                                  + (f" ({dat_units} units)" if dat_units else "")]}
            print(f"  case {name}: {len(nodes)} nodes, column '{col}'")

        jobs = [(n, d) for n, d in data.items()]
        for dd in lv.get("differences") or []:               # optional: A minus B, node by node, then leveled
            name, a, b = dd.get("name"), dd.get("minuend"), dd.get("subtrahend")
            if not name or a not in data or b not in data:
                raise InputError(f"leveling difference {dd}: needs 'name', 'minuend', 'subtrahend' = case names")
            A, B = data[a], data[b]
            common, ia, ib = np.intersect1d(A["nodes"], B["nodes"], return_indices=True)
            if len(common) == 0:
                raise InputError(f"difference {name}: cases {a} and {b} share no node")
            w = list(A["warns"]) + list(B["warns"])
            if len(common) != len(A["nodes"]) or len(common) != len(B["nodes"]):
                w.append(f"difference {name}: only {len(common)} common nodes ({a}: {len(A['nodes'])}, "
                         f"{b}: {len(B['nodes'])})")
            jobs.append((name, {"nodes": common, "x": A["x"][ia], "y": A["y"][ia], "raw": A["raw"][ia] - B["raw"][ib],
                                "warns": w, "src": [f"difference **{a} minus {b}** (node by node, before leveling)"]
                                + A["src"] + B["src"]}))
            print(f"  difference {name} = {a} - {b}: {len(common)} nodes")

        summary, any_warn = [], False
        for name, d in jobs:
            if only_case and name != only_case:
                continue
            warns = list(d["warns"])
            if len(d["nodes"]) < MIN_NODES:
                warns.append(f"only {len(d['nodes'])} nodes: too few for a warpage map")
            xo, yo, z_mm, info = level(d["x"], d["y"], d["raw"], method, mode)
            res = warpage_shape(xo, yo, z_mm)
            w_um = res["warpage_mm"] * 1000.0
            if np.abs(d["raw"]).max() > MAX_ABS_UZ_MM:
                warns.append(f"input displacement up to {np.abs(d['raw']).max():.3f} mm: is z_unit '{z_unit}' right?")
            if not (MIN_WARPAGE_UM <= w_um <= MAX_WARPAGE_UM):
                warns.append(f"leveled warpage {w_um:.4g} um is outside {MIN_WARPAGE_UM}..{MAX_WARPAGE_UM} um: "
                             f"is z_unit '{z_unit}' right?")
            if info["tilt_deg"] > MAX_TILT_DEG:
                warns.append(f"fitted plane is tilted {info['tilt_deg']:.3f} deg: wrong column or unit?")
            w_um, w_mil = write_case(out_root / name, name, d["src"], d["nodes"], d["x"], d["y"], d["raw"], xo, yo,
                                     z_mm, info, res, warns, opts)
            for t in warns:
                print(f"  WARNING [{name}]: {t}")
            any_warn = any_warn or bool(warns)
            print(f"  {name}: warpage {w_um:.2f} um = {w_mil:.3f} mil, {res['shape']}, tilt {info['tilt_deg']:.5f} deg")
            summary.append([name, len(d["nodes"]), f"{w_um:.3f}", f"{w_mil:.4f}", res["shape"],
                            f"{res['signed_mm'] * 1000:.3f}", f"{info['tilt_deg']:.6f}", info["mode"], info["method"],
                            z_unit, opts["flip_z"], len(warns)])
        if not summary:
            raise InputError(f"no case named '{only_case}'")
        out_root.mkdir(parents=True, exist_ok=True)
        with open(out_root / "leveling_summary.csv", "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["case", "nodes", "warpage_um", "warpage_mil", "shape", "signed_warpage_um", "tilt_deg",
                        "mode", "method", "z_unit", "flip_z", "warnings"])
            w.writerows(summary)
        print(f"written: {out_root}")
        if any_warn and not lv.get("accept_warnings", False):
            print("RESULT: DONE WITH WARNINGS - a human must confirm them (then set leveling.accept_warnings = true)")
            return EXIT_WARN
        print("RESULT: DONE")
        return EXIT_OK
    except InputError as e:
        print(f"INPUT ERROR: {e}")
        return EXIT_INPUT
    except (OSError, json.JSONDecodeError) as e:
        print(f"INPUT ERROR: {type(e).__name__}: {e}")
        return EXIT_INPUT


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    case = None
    if "--case" in argv:
        i = argv.index("--case")
        case = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if not argv and CONFIG_FILE:
        argv = [CONFIG_FILE]
    if not argv:
        print("usage: level_bga_shadow.py <project.json> [--case NAME]")
        return EXIT_INPUT
    return run(Path(argv[0]), case)


if __name__ == "__main__":
    sys.exit(main())
