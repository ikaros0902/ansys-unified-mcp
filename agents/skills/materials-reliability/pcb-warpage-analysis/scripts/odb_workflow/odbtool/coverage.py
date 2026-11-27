"""Copper coverage of each copper layer, rendered from the ODB++ features.

coverage = copper area inside the region / region area      (0..1)
region   = the step profile (default) and, if given, the 2D-drawing rectangle

Rendering: anti-aliased (aggdraw) into an 8-bit image; area = sum(gray)/255.
  * lines/arcs with round or square symbols -> pen strokes + caps
  * pads: r, s, rect (incl. rounded/chamfered), oval, di, oct, donut_r/donut_s, el,
    hex_l/hex_s, tri; thermal symbols are drawn as a full donut (slight overestimate);
    user symbols from <job>/symbols/<name>/features are drawn recursively
  * surfaces: islands and holes in one path (non-zero winding, orientation enforced)
  * negative polarity erases
Brush fills of the renderer grow every edge by a constant fraction of a pixel; it is
measured at start-up and removed by offsetting each filled outline inwards, so the
result does not depend on the resolution.  Unrendered features (text, barcodes,
unknown symbols) are counted and reported; they are never silently ignored.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from .odb import file_units

_BIAS: float | None = None


def measure_bias() -> float:
    """Outward growth (px) of one brush-filled edge."""
    import aggdraw
    from PIL import Image
    img = Image.new("L", (1200, 200), 0)
    d = aggdraw.Draw(img)
    b = aggdraw.Brush(255)
    w, n = 6.0, 10
    for i in range(n):
        y = 10.3 + i * 17.7
        d.polygon((50.3, y, 1050.3, y, 1050.3, y + w, 50.3, y + w), None, b)
    d.flush()
    a = sum(i * c for i, c in enumerate(img.histogram())) / 255.0 / n
    return (-(1000 + w) + math.sqrt((1000 + w) ** 2 - 4 * (1000 * w - a))) / 4


# ---------------------------------------------------------------- geometry helpers
def _circle_pts(cx, cy, r, tol):
    if r <= 0:
        return []
    n = max(8, min(512, int(math.ceil(math.pi / math.acos(max(-1.0, 1 - tol / r)))) if r > tol else 8))
    rr = r * math.sqrt(2 * math.pi / (n * math.sin(2 * math.pi / n)))      # same area as the circle
    return [(cx + rr * math.cos(2 * math.pi * k / n), cy + rr * math.sin(2 * math.pi * k / n)) for k in range(n)]


def _arc_pts(xs, ys, xe, ye, xc, yc, cw, tol):
    r = math.hypot(xs - xc, ys - yc)
    a0 = math.atan2(ys - yc, xs - xc)
    a1 = math.atan2(ye - yc, xe - xc)
    if cw:
        da = a0 - a1
        if da <= 1e-12:
            da += 2 * math.pi
        da = -da
    else:
        da = a1 - a0
        if da <= 1e-12:
            da += 2 * math.pi
    step = 2 * math.acos(max(-1.0, 1 - tol / r)) if r > tol else math.pi / 4
    n = max(2, int(math.ceil(abs(da) / max(step, 1e-3))))
    return [(xc + r * math.cos(a0 + da * k / n), yc + r * math.sin(a0 + da * k / n)) for k in range(n + 1)]


def _area(pts):
    s = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        s += x0 * y1 - x1 * y0
    return s / 2


def _offset(pts, d):
    """Move every edge of a closed polygon by d towards its left side (miter, clamped)."""
    n = len(pts)
    if n < 3 or d == 0:
        return pts
    out = []
    for i in range(n):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        e1 = (x1 - x0, y1 - y0)
        e2 = (x2 - x1, y2 - y1)
        l1, l2 = math.hypot(*e1), math.hypot(*e2)
        if l1 < 1e-12 or l2 < 1e-12:
            out.append((x1, y1))
            continue
        n1 = (-e1[1] / l1, e1[0] / l1)
        n2 = (-e2[1] / l2, e2[0] / l2)
        bx, by = n1[0] + n2[0], n1[1] + n2[1]
        bl = math.hypot(bx, by)
        if bl < 1e-9:
            out.append((x1 + n1[0] * d, y1 + n1[1] * d))
            continue
        cosh = bl / 2
        m = min(d / max(cosh, 0.5), 2 * d)
        out.append((x1 + bx / bl * m, y1 + by / bl * m))
    return out


def _poly_rect(w, h):
    return [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]


def _poly_round_rect(w, h, r, tol, corners="1234"):
    if r <= 0:
        return _poly_rect(w, h)
    r = min(r, w / 2, h / 2)
    pts = []
    spec = [(w / 2 - r, h / 2 - r, 0, "1"), (-w / 2 + r, h / 2 - r, 90, "2"),
            (-w / 2 + r, -h / 2 + r, 180, "3"), (w / 2 - r, -h / 2 + r, 270, "4")]
    for cx, cy, a, c in spec:
        if c in corners:
            pts += [(cx + r * math.cos(math.radians(a + t)), cy + r * math.sin(math.radians(a + t)))
                    for t in range(0, 91, 10)]
        else:
            ex = cx + (r if a in (0, 270) else -r)
            ey = cy + (r if a in (0, 90) else -r)
            pts.append((ex, ey))
    return pts


def _poly_chamfer_rect(w, h, c, corners="1234"):
    c = min(c, w / 2, h / 2)
    x, y = w / 2, h / 2
    pts = []
    for (px, py, k) in ((x, y, "1"), (-x, y, "2"), (-x, -y, "3"), (x, -y, "4")):
        if k in corners:
            sx = -1 if px > 0 else 1
            sy = -1 if py > 0 else 1
            if k in "13":
                pts += [(px, py + sy * c), (px + sx * c, py)]
            else:
                pts += [(px + sx * c, py), (px, py + sy * c)]
        else:
            pts.append((px, py))
    return pts


def _poly_oval(w, h, tol):
    if w >= h:
        r = h / 2
        a = _arc_pts(w / 2 - r, -r, w / 2 - r, r, w / 2 - r, 0, False, tol)
        b = _arc_pts(-w / 2 + r, r, -w / 2 + r, -r, -w / 2 + r, 0, False, tol)
    else:
        r = w / 2
        a = _arc_pts(r, h / 2 - r, -r, h / 2 - r, 0, h / 2 - r, False, tol)
        b = _arc_pts(-r, -h / 2 + r, r, -h / 2 + r, 0, -h / 2 + r, False, tol)
    return a + b


# ---------------------------------------------------------------- symbols
_NUM = r"(\d+(?:\.\d+)?)"
STD = [
    ("r", re.compile(rf"^r{_NUM}$")),
    ("s", re.compile(rf"^s{_NUM}$")),
    ("rect", re.compile(rf"^rect{_NUM}x{_NUM}(?:x(r|c){_NUM}(?:x(\d+))?)?$")),
    ("oval", re.compile(rf"^oval{_NUM}x{_NUM}$")),
    ("di", re.compile(rf"^di{_NUM}x{_NUM}$")),
    ("oct", re.compile(rf"^oct{_NUM}x{_NUM}x{_NUM}$")),
    ("donut_r", re.compile(rf"^donut_r{_NUM}x{_NUM}$")),
    ("donut_s", re.compile(rf"^donut_s{_NUM}x{_NUM}$")),
    ("el", re.compile(rf"^el{_NUM}x{_NUM}$")),
    ("hex_l", re.compile(rf"^hex_l{_NUM}x{_NUM}x{_NUM}$")),
    ("hex_s", re.compile(rf"^hex_s{_NUM}x{_NUM}x{_NUM}$")),
    ("tri", re.compile(rf"^tri{_NUM}x{_NUM}$")),
    ("thermal", re.compile(rf"^(?:ths|thr|s_ths|s_tho|s_thr|sr_ths|rc_ths|rc_tho|o_ths|oblong_ths){_NUM}x{_NUM}")),
]


@dataclass
class Shape:
    """Symbol geometry in symbol-local inch: closed outlines (outer, holes) or stroke info."""
    kind: str                      # 'poly' | 'stroke_r' | 'stroke_s' | 'user' | 'none'
    outlines: list = field(default_factory=list)      # list of (pts, is_hole)
    width: float = 0.0             # for strokes (inch)
    approx: bool = False


class Renderer:
    def __init__(self, job_dir: Path, res_in: float, x0: float, y1: float, w_px: int, h_px: int,
                 default_units: str, bias_px: float):
        import aggdraw
        from PIL import Image
        self.aggdraw = aggdraw
        self.job_dir = job_dir
        self.res = res_in
        self.x0, self.y1 = x0, y1
        self.img = Image.new("L", (w_px, h_px), 0)
        self.d = aggdraw.Draw(self.img)
        self.d.setantialias(True)
        self.default_units = default_units
        self.bias = bias_px
        self.tol = 0.05                      # px, chord tolerance
        self.stats = Counter()
        self.unrendered = Counter()
        self.approx = Counter()
        self._brush = {255: aggdraw.Brush(255), 0: aggdraw.Brush(0)}
        self._pens = {}
        self._user = {}

    # -------- low level, coordinates in inch
    def px(self, x, y):
        return (x - self.x0) / self.res, (self.y1 - y) / self.res

    def pen(self, color, w_px):
        k = (color, round(w_px, 4))
        p = self._pens.get(k)
        if p is None:
            p = self._pens[k] = self.aggdraw.Pen(color, max(w_px, 0.01))
        return p

    def fill(self, outlines_px, color):
        """outlines_px: list of (pts_px, is_hole).  Orientation enforced, then offset inwards."""
        path = self.aggdraw.Path()
        any_pts = False
        for pts, hole in outlines_px:
            if len(pts) < 3:
                continue
            a = _area(pts)
            # in image coords (y down) a > 0 means clockwise on screen; make islands a > 0, holes a < 0
            if (a < 0) != hole:
                pts = pts[::-1]
            # with positive shoelace area the left side of every edge is the inside, so moving
            # edges left by +bias shrinks islands; holes run the other way and grow by the same
            # amount - both remove the renderer's outward growth from the copper
            pts = _offset(pts, self.bias)
            path.moveto(*pts[0])
            for p in pts[1:]:
                path.lineto(*p)
            path.close()
            any_pts = True
        if any_pts:
            self.d.path(path, None, self._brush[color])

    def stroke(self, pts_in, w_in, color, square=False):
        w = w_in / self.res
        P = [self.px(*p) for p in pts_in]
        if len(P) == 1 or all(abs(p[0] - P[0][0]) < 1e-9 and abs(p[1] - P[0][1]) < 1e-9 for p in P):
            cx, cy = P[0]
            if square:
                pts = [(cx - w / 2, cy - w / 2), (cx + w / 2, cy - w / 2), (cx + w / 2, cy + w / 2),
                       (cx - w / 2, cy + w / 2)]
            else:
                pts = _circle_pts(cx, cy, w / 2, self.tol)
            self.fill([(pts, False)], color)
            return
        if square:
            (ax, ay), (bx, by) = P[0], P[-1]
            L = math.hypot(bx - ax, by - ay)
            ux, uy = (bx - ax) / L, (by - ay) / L
            ext = w / 2
            P = [(ax - ux * ext, ay - uy * ext)] + P[1:-1] + [(bx + ux * ext, by + uy * ext)]
        flat = [c for p in P for c in p]
        self.d.line(flat, self.pen(color, w))
        if not square:
            for cx, cy in (P[0], P[-1]):
                self.fill([(_circle_pts(cx, cy, w / 2, self.tol), False)], color)

    # -------- symbols
    def std_shape(self, name: str, mil_units: bool) -> Shape | None:
        k = 0.001 if mil_units else 1 / 25400.0          # symbol dims: mil or micron -> inch
        tol = self.tol * self.res
        for fam, rx in STD:
            m = rx.match(name)
            if not m:
                continue
            v = [float(x) * k if x and re.fullmatch(r"\d+(\.\d+)?", x) else x for x in m.groups()]
            if fam == "r":
                return Shape("poly", [(_circle_pts(0, 0, v[0] / 2, tol), False)], width=v[0])
            if fam == "s":
                return Shape("poly", [(_poly_rect(v[0], v[0]), False)], width=v[0])
            if fam == "rect":
                w, h, mode, rr, corners = v
                corners = str(int(float(corners) / k)) if isinstance(corners, float) else (corners or "1234")
                if mode == "r":
                    return Shape("poly", [(_poly_round_rect(w, h, rr, tol, corners), False)])
                if mode == "c":
                    return Shape("poly", [(_poly_chamfer_rect(w, h, rr, corners), False)])
                return Shape("poly", [(_poly_rect(w, h), False)])
            if fam == "oval":
                return Shape("poly", [(_poly_oval(v[0], v[1], tol), False)])
            if fam == "di":
                w, h = v
                return Shape("poly", [([(w / 2, 0), (0, h / 2), (-w / 2, 0), (0, -h / 2)], False)])
            if fam == "oct":
                w, h, c = v
                return Shape("poly", [(_poly_chamfer_rect(w, h, c), False)])
            if fam == "donut_r":
                od, idd = v
                return Shape("poly", [(_circle_pts(0, 0, od / 2, tol), False), (_circle_pts(0, 0, idd / 2, tol), True)])
            if fam == "donut_s":
                od, idd = v
                return Shape("poly", [(_poly_rect(od, od), False), (_poly_rect(idd, idd), True)])
            if fam == "el":
                w, h = v
                n = 96
                return Shape("poly", [([(w / 2 * math.cos(2 * math.pi * i / n), h / 2 * math.sin(2 * math.pi * i / n))
                                        for i in range(n)], False)])
            if fam in ("hex_l", "hex_s"):
                w, h, c = v
                if fam == "hex_l":
                    pts = [(w / 2, 0), (w / 2 - c, h / 2), (-w / 2 + c, h / 2), (-w / 2, 0), (-w / 2 + c, -h / 2),
                           (w / 2 - c, -h / 2)]
                else:
                    pts = [(0, h / 2), (w / 2, h / 2 - c), (w / 2, -h / 2 + c), (0, -h / 2), (-w / 2, -h / 2 + c),
                           (-w / 2, h / 2 - c)]
                return Shape("poly", [(pts, False)])
            if fam == "tri":
                b, h = v
                return Shape("poly", [([(-b / 2, -h / 2), (b / 2, -h / 2), (0, h / 2)], False)])
            if fam == "thermal":
                od, idd = v[0], v[1]
                return Shape("poly", [(_circle_pts(0, 0, od / 2, tol), False), (_circle_pts(0, 0, idd / 2, tol), True)],
                             approx=True)
        return None

    def user_shape(self, name: str):
        if name in self._user:
            return self._user[name]
        f = self.job_dir / "symbols" / name / "features"
        z = self.job_dir / "symbols" / name / "features.Z"
        text = None
        if f.exists():
            text = f.read_text(encoding="latin-1")
        elif z.exists():
            import unlzw3
            text = unlzw3.unlzw(z.read_bytes()).decode("latin-1")
        self._user[name] = text
        return text

    # -------- features file
    def draw_features(self, text: str, T=None, depth=0, negative_pad=False):
        """Draw one features file.

        T: callable (x, y) -> (x, y) in inch, the pad transform when drawing a user symbol.
        negative_pad: the user symbol is placed with negative polarity -> its positive
        features erase, its negative features are skipped.
        """
        units = file_units(text, self.default_units)
        k = 1 / 25.4 if units == "MM" else 1.0
        sym_units_default = "M" if units == "MM" else "I"
        table: dict[str, tuple[str, bool]] = {}
        surf: list = []
        surf_col = None
        cur: list = []
        cur_hole = False
        tolin = self.tol * self.res
        T = T or (lambda x, y: (x, y))

        def color(pol):
            if negative_pad:
                return 0 if pol == "P" else None
            return 255 if pol == "P" else 0

        for raw in text.splitlines():
            if not raw or raw[0] == "#":
                continue
            line = raw.split(";", 1)[0].strip()
            if not line:
                continue
            tok = line.split()
            t0 = tok[0]
            if t0.startswith("$"):
                if len(tok) >= 2:
                    u = tok[2].upper() if len(tok) > 2 else sym_units_default
                    table[t0[1:]] = (tok[1], u != "M")
                continue
            try:
                if t0 == "L":
                    self.stats["L"] += 1
                    col = color(tok[6])
                    if col is not None:
                        self._draw_stroke([T(float(tok[1]) * k, float(tok[2]) * k),
                                           T(float(tok[3]) * k, float(tok[4]) * k)], table.get(tok[5]), col)
                elif t0 == "A":
                    self.stats["A"] += 1
                    col = color(tok[8])
                    if col is not None:
                        xs, ys, xe, ye, xc, yc = (float(v) * k for v in tok[1:7])
                        cw = len(tok) > 10 and tok[10].upper() == "Y"
                        pts = [T(*p) for p in _arc_pts(xs, ys, xe, ye, xc, yc, cw, tolin)]
                        self._draw_stroke(pts, table.get(tok[7]), col)
                elif t0 == "P":
                    self.stats["P"] += 1
                    if tok[3] == "-1":
                        sym, pol, rest = tok[4], tok[6], tok[8:]
                        self.approx["resized pad (drawn at nominal size)"] += 1
                    else:
                        sym, pol, rest = tok[3], tok[4], tok[6:]
                    col = color(pol)
                    if col is not None:
                        angle, mirror = _orientation(rest[0] if rest else "0", rest[1] if len(rest) > 1 else "0")
                        self._draw_pad(T(float(tok[1]) * k, float(tok[2]) * k), table.get(sym), col,
                                       angle, mirror, depth)
                elif t0 in ("T", "B"):
                    self.unrendered["text/barcode"] += 1
                elif t0 == "S":
                    self.stats["S"] += 1
                    surf, surf_col = [], color(tok[1])
                elif t0 == "OB":
                    cur = [(float(tok[1]) * k, float(tok[2]) * k)]
                    cur_hole = len(tok) > 3 and tok[3].upper() == "H"
                elif t0 == "OS":
                    cur.append((float(tok[1]) * k, float(tok[2]) * k))
                elif t0 == "OC":
                    xe, ye, xc, yc = (float(v) * k for v in tok[1:5])
                    cw = len(tok) > 5 and tok[5].upper() == "Y"
                    cur += _arc_pts(cur[-1][0], cur[-1][1], xe, ye, xc, yc, cw, tolin)[1:]
                elif t0 == "OE":
                    surf.append((cur, cur_hole))
                    cur = []
                elif t0 == "SE":
                    if surf_col is not None:
                        self.fill([([self.px(*T(*p)) for p in pts], hole) for pts, hole in surf], surf_col)
                    surf = []
            except (IndexError, ValueError):
                self.unrendered["unparsed record"] += 1

    def _draw_stroke(self, pts, sym, col):
        if sym is None:
            self.unrendered["line: unknown symbol"] += 1
            return
        name, mil = sym
        sh = self.std_shape(name, mil)
        if sh is None:
            self.unrendered[f"line symbol {re.sub(r'[0-9.x]+', '#', name)}"] += 1
            return
        if name.startswith("s"):
            self.stroke(pts, sh.width, col, square=True)
        elif name.startswith("r"):
            self.stroke(pts, sh.width, col)
        else:
            self.approx["line with non-round symbol"] += 1
            self.stroke(pts, sh.width or 0.001, col)

    def _draw_pad(self, xy, sym, col, angle, mirror, depth):
        if sym is None:
            self.unrendered["pad: unknown symbol index"] += 1
            return
        name, mil = sym
        sh = self.std_shape(name, mil)
        cx, cy = xy
        ca, sa = math.cos(math.radians(-angle)), math.sin(math.radians(-angle))   # ODB: clockwise positive

        def place(x, y):
            if mirror:
                x = -x
            return cx + x * ca - y * sa, cy + x * sa + y * ca

        if sh is not None:
            if sh.approx:
                self.approx[f"pad {re.sub(r'[0-9.x]+', '#', name)}"] += 1
            self.fill([([self.px(*place(x, y)) for x, y in pts], hole) for pts, hole in sh.outlines], col)
            return
        text = self.user_shape(name)
        if text is None or depth > 4:
            self.unrendered[f"pad symbol {re.sub(r'[0-9.]+', '#', name)}"] += 1
            return
        self.stats["user symbol pads"] += 1
        self.draw_features(text, T=place, depth=depth + 1, negative_pad=(col == 0))

    def area_px(self, box=None) -> float:
        self.d.flush()
        img = self.img.crop(box) if box else self.img
        return sum(i * c for i, c in enumerate(img.histogram())) / 255.0


def _orientation(code: str, angle_tok: str) -> tuple[float, bool]:
    try:
        c = int(code)
    except ValueError:
        return 0.0, False
    if c <= 7:
        return (c % 4) * 90.0, c >= 4
    try:
        a = float(angle_tok)
    except ValueError:
        a = 0.0
    return a, c == 9


# ---------------------------------------------------------------- per layer worker
def _layer_job(args):
    (job_dir, layer_dir, res_mil, region_in, extra_regions, default_units, bias, preview_png, poly_px) = args
    from PIL import Image, ImageChops, ImageDraw
    Image.MAX_IMAGE_PIXELS = None            # a 420 x 400 mm board at 1 mil is ~260 Mpx (not a "bomb")
    res = res_mil / 1000.0
    x0, y0, x1, y1 = region_in
    w = int(math.ceil((x1 - x0) / res))
    h = int(math.ceil((y1 - y0) / res))
    R = Renderer(Path(job_dir), res, x0, y1, w, h, default_units, bias)
    f = Path(layer_dir) / "features"
    text = f.read_text(encoding="latin-1") if f.exists() else ""
    R.draw_features(text)
    R.d.flush()
    if poly_px:                       # non-rectangular profile: clear copper outside it
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).polygon(poly_px, fill=255)
        R.img = ImageChops.multiply(R.img, mask)
        region_px = sum(i * c for i, c in enumerate(mask.histogram())) / 255.0
    else:
        region_px = w * h
    a = sum(i * c for i, c in enumerate(R.img.histogram())) / 255.0
    out = {"profile": {"coverage": a / region_px, "copper_in2": a * res * res, "region_in2": region_px * res * res}}
    for label, (rx0, ry0, rx1, ry1) in extra_regions.items():
        box = (int(round((rx0 - x0) / res)), int(round((y1 - ry1) / res)),
               int(round((rx1 - x0) / res)), int(round((y1 - ry0) / res)))
        box = (max(0, box[0]), max(0, box[1]), min(w, box[2]), min(h, box[3]))
        sub = R.img.crop(box)
        ar = sum(i * c for i, c in enumerate(sub.histogram())) / 255.0
        npx = (box[2] - box[0]) * (box[3] - box[1])
        out[label] = {"coverage": ar / npx if npx else None, "copper_in2": ar * res * res,
                      "region_in2": npx * res * res}
    if preview_png:
        f = max(1, int(math.ceil(max(w, h) / 1600)))
        R.img.reduce(f).save(preview_png)
    return {"layer": Path(layer_dir).name, "regions": out, "stats": dict(R.stats),
            "unrendered": dict(R.unrendered), "approx": dict(R.approx)}


def compute(job_dir: Path, step_dir: Path, layer_names: list[str], profile_text: str, res_mil: float,
            extra_regions_in: dict, default_units: str, preview_dir: Path | None, workers: int, log) -> dict:
    """Coverage per copper layer.  Returns {layer_name_lower: result dict}."""
    from .odb import profile_bbox
    bias = measure_bias()
    log(f"  renderer edge growth measured: {bias:+.3f} px (removed by inward offset)")
    x0, y0, x1, y1 = profile_bbox(profile_text)
    pts = _profile_outline(profile_text)
    rect = len(pts) <= 6 and all(abs(px - x0) < 1e-6 or abs(px - x1) < 1e-6 for px, _ in pts) \
        and all(abs(py - y0) < 1e-6 or abs(py - y1) < 1e-6 for _, py in pts)
    res = res_mil / 1000.0
    poly_px = None if rect else [((px - x0) / res, (y1 - py) / res) for px, py in pts]
    if preview_dir:
        preview_dir.mkdir(parents=True, exist_ok=True)
    args = [(str(job_dir), str(step_dir / "layers" / n.lower()), res_mil, (x0, y0, x1, y1), extra_regions_in,
             default_units, bias, str(preview_dir / f"{n.lower()}.png") if preview_dir else None, poly_px)
            for n in layer_names]
    out = {}
    with ProcessPoolExecutor(max_workers=max(1, workers)) as ex:
        for r in ex.map(_layer_job, args):
            out[r["layer"]] = r
            un = sum(r["unrendered"].values())
            log(f"  {r['layer']:<20} coverage {r['regions']['profile']['coverage']:.4f}"
                + "".join(f", {k} {v['coverage']:.4f}" for k, v in r["regions"].items() if k != "profile")
                + (f"  (unrendered {un}: {r['unrendered']})" if un else ""))
    return out


def _profile_outline(text: str) -> list[tuple[float, float]]:
    k = 1 / 25.4 if file_units(text) == "MM" else 1.0
    pts = []
    for line in text.splitlines():
        tok = line.split()
        if not tok:
            continue
        if tok[0] in ("OB", "OS"):
            pts.append((float(tok[1]) * k, float(tok[2]) * k))
        elif tok[0] == "OC" and pts:
            xs, ys = pts[-1]
            pts += _arc_pts(xs, ys, float(tok[1]) * k, float(tok[2]) * k, float(tok[3]) * k, float(tok[4]) * k,
                            len(tok) > 5 and tok[5].upper() == "Y", 0.0005)[1:]
        elif tok[0] == "OE":
            break
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    return pts
