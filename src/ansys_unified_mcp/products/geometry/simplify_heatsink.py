"""散熱片 (heatsink) 幾何簡化與等效密度反推（由 call_dispatch.py 拆分，函式本體逐字搬移）。"""

import logging
import math

from ._geom_shared import (
    _find_bodies_by_name,
    _bbox_m,
    _make_box_from_bbox,
    _mm,
    _source_body_name,
    _suppress_hide_sources,
    _safe_delete,
)

logger = logging.getLogger("ansys-mcp")

__all__ = [
    "HEATSINK_DENSITY_PRESETS",
    "_HS_EPS",
    "_HS_BOTTOM_AREA_RATIO",
    "_HS_ROOT_FILLET_M",
    "_HS_CONE_MAX_HALF_ANGLE",
    "_q_m",
    "_face_extent",
    "_face_area_m2",
    "_horizontal_planes",
    "_vertical_walls",
    "_level_areas",
    "_main_bottom_plane",
    "_fin_root_y",
    "_y_cylinders",
    "_detect_mount_holes",
    "_diag_corner_cylinders",
    "_select_screw_holes",
    "_hole_plate_span",
    "_simple_heatsink_boxes",
    "_split_by_gap",
    "_fin_fill_rects",
    "_comp_bodies",
    "_master_key",
    "_make_cylinder_body",
    "_resolve_heatsink_groups",
    "_body_density",
    "_simplify_heatsink_group",
    "_format_heatsink_result",
    "_geom_simplify_heatsink",
]


HEATSINK_DENSITY_PRESETS = {
    "aluminum": 2700.0,       # 鋁合金（最常見擠型/壓鑄散熱片）
    "aluminum_6063": 2700.0,
    "copper": 8960.0,         # 純銅散熱片 / 銅底
    "copper_c110": 8890.0,
}

_HS_EPS = 1e-6               # 1µm：Y 高度比對容差（公尺）
_HS_BOTTOM_AREA_RATIO = 0.10  # 底面層總面積 ≥ 最大朝下層的 10% 才算「實質底面」（排除螺絲尾端）
_HS_ROOT_FILLET_M = 1.5e-3    # 鰭片根部圓角容差：側壁起點可高於根部平面至多 1.5mm


def _q_m(v) -> float:
    """pint.Quantity（或純數）轉為公尺純數值。"""
    from ansys.geometry.core.misc import UNITS

    return v.m_as(UNITS.m) if hasattr(v, "m_as") else float(v)


def _face_extent(face):
    """以 face 各 edge 端點估算其 world 包圍盒 (lo, hi)，單位公尺；取不到則回傳 None。

    Face.bounding_box 需 Ansys 25.2+，25.1 無法使用，故改取 edge 端點。
    部分退化 edge 取端點會丟 ValueError（零長向量），逐條容錯略過。
    """
    pts = []
    for e in face.edges:
        try:
            pts.append(e.start)
            pts.append(e.end)
        except Exception:
            continue
    if not pts:
        return None
    xs = [_q_m(p.x) for p in pts]
    ys = [_q_m(p.y) for p in pts]
    zs = [_q_m(p.z) for p in pts]
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def _face_area_m2(face) -> float:
    from ansys.geometry.core.misc import UNITS

    a = face.area
    return a.m_as(UNITS.m ** 2) if hasattr(a, "m_as") else float(a)


def _horizontal_planes(body):
    """列出 body 所有水平平面：list[(face, y, area, up)]，up=True 表法向朝 +Y。"""
    from ansys.geometry.core.designer.face import SurfaceType

    out = []
    for f in body.faces:
        try:
            if f.surface_type != SurfaceType.SURFACETYPE_PLANE:
                continue
            n = f.normal(0.5, 0.5)
            if abs(float(n.y)) < 0.9:
                continue
            out.append((f, _q_m(f.point(0.5, 0.5).y), _face_area_m2(f), float(n.y) > 0))
        except Exception:
            continue
    return out


def _vertical_walls(body):
    """列出 body 的垂直平面（法向 ±X 或 ±Z）：list[(axis 0=X/2=Z, lo, hi, area)]（world 公尺）。"""
    from ansys.geometry.core.designer.face import SurfaceType

    out = []
    for f in body.faces:
        try:
            if f.surface_type != SurfaceType.SURFACETYPE_PLANE:
                continue
            n = f.normal(0.5, 0.5)
            if abs(float(n.y)) > 0.1:
                continue
            if abs(float(n.x)) > 0.9:
                axis = 0
            elif abs(float(n.z)) > 0.9:
                axis = 2
            else:
                continue
            ext = _face_extent(f)
            if ext is not None:
                out.append((axis, ext[0], ext[1], _face_area_m2(f)))
        except Exception:
            continue
    return out


def _level_areas(planes, up):
    """將同方向水平面依高度彙總：{y: 總面積}（高度以 1µm 量化合併）。"""
    acc = {}
    for _f, y, area, is_up in planes:
        if is_up != up:
            continue
        key = round(y / _HS_EPS)
        acc.setdefault(key, [y, 0.0])
        acc[key][1] += area
    return {v[0]: v[1] for v in acc.values()}


def _main_bottom_plane(planes):
    """主接合底面：總面積 ≥ 最大朝下層 10% 的「最低」朝下層，回傳 (該層最大面, y)；無則 (None, None)。

    - 不取 body 最低 Y：彈簧螺絲/推銷尾端常往下突出（面積極小）。
    - 不只取面積最大層：許多散熱片底部有較小的接觸凸台（pedestal）比底板更低，
      它才是真正貼合晶片的熱接觸面，必須保留並當作底面基準。
    """
    levels = _level_areas(planes, up=False)
    if not levels:
        return None, None
    a_max = max(levels.values())
    y_bot = min(y for y, a in levels.items() if a >= _HS_BOTTOM_AREA_RATIO * a_max)
    faces = [p for p in planes if not p[3] and abs(p[1] - y_bot) <= _HS_EPS]
    return max(faces, key=lambda p: p[2])[0], y_bot


def _fin_root_y(planes, walls, y_bot, y_top):
    """鰭片根部（底板頂面）高度。

    主要依據：鰭片側壁的起點——對每個介於底面與頂面之間的朝上層 L，累計「起點落在
    [L, L+1.5mm]（含根部圓角）」的垂直側壁面積，取最大者（鰭片最多的層）。
    → 可避開上蓋頂面等大面積朝上平面（例如折片鰭片夾在底板與上蓋之間）。
    無任何側壁時退回「朝上層總面積最大者」；仍無則回傳 None（無獨立底板）。
    """
    levels = {y: a for y, a in _level_areas(planes, up=True).items()
              if y_bot + _HS_EPS < y < y_top - _HS_EPS}
    if not levels:
        return None
    score = {y: sum(w[3] for w in walls
                    if y - 1e-5 <= w[1][1] <= y + _HS_ROOT_FILLET_M and w[2][1] - w[1][1] > 1e-3)
             for y in levels}
    best = max(score, key=lambda y: score[y])
    if score[best] > 0:
        return best
    return max(levels, key=lambda y: levels[y])


_HS_CONE_MAX_HALF_ANGLE = math.radians(15.0)  # 拔模錐孔上限；45° 倒角等更陡錐面不視為孔壁


def _y_cylinders(body):
    """列出 body 上軸向沿 Y 的圓柱面：list[dict(cx, cz, r, ylo, yhi, concave, angle)]（公尺/弧度）。

    壓鑄件鎖孔常帶拔模斜度而成為小半錐角的錐面，半錐角 ≤ _HS_CONE_MAX_HALF_ANGLE 者
    一併視為圓柱，半徑取面中點至軸心距離（≈ 中段孔徑）。
    concave（內凹＝孔壁）判定：面外法向指向軸心 → 法向與徑向向量內積 < 0。
    angle：該面涵蓋的圓周角 ≈ 面積 / (r·高)，用於區分完整孔（2π）與圓角（π/2）。
    """
    from ansys.geometry.core.designer.face import SurfaceType

    out = []
    for f in body.faces:
        try:
            is_cone = f.surface_type == SurfaceType.SURFACETYPE_CONE
            if f.surface_type != SurfaceType.SURFACETYPE_CYLINDER and not is_cone:
                continue
            cyl = f.shape.geometry
            if abs(float(cyl.dir_z.y)) < 0.9:
                continue
            cx, cz = _q_m(cyl.origin.x), _q_m(cyl.origin.z)
            p = f.point(0.5, 0.5)
            if is_cone:
                ha = cyl.half_angle
                ha = ha.m_as("radian") if hasattr(ha, "m_as") else float(ha)
                if abs(ha) > _HS_CONE_MAX_HALF_ANGLE:
                    continue
                r = math.hypot(_q_m(p.x) - cx, _q_m(p.z) - cz)
            else:
                r = _q_m(cyl.radius)
            n = f.normal(0.5, 0.5)
            dot = float(n.x) * (_q_m(p.x) - cx) + float(n.z) * (_q_m(p.z) - cz)
            ext = _face_extent(f)
            if ext is None:
                continue
            h = ext[1][1] - ext[0][1]
            angle = _face_area_m2(f) / (r * h) if r > 0 and h > 0 else 0.0
            out.append({"cx": cx, "cz": cz, "r": r, "ylo": ext[0][1], "yhi": ext[1][1],
                        "concave": dot < 0, "angle": angle})
        except Exception:
            continue
    return out


def _detect_mount_holes(cyls, min_radius_m, concentric_tol_m=2e-4):
    """偵測鎖孔：原始 body 上所有挖孔（完整圓周的內凹 Y 向圓柱），簡化為貫穿的 Y 向直圓柱。

    1. 只看內凹、半徑 ≥ min_radius_m 的圓柱面；同 (中心, 半徑) 的分片面累加圓周角，
       ≥ 0.9·2π 才算孔（排除內圓角）。不論高度、盲孔/通孔、開口方向。
    2. 同軸者合併，孔徑取最小半徑（沉孔/倒角等細節捨棄，只留一支直圓柱）。
    3. clearance：同軸所有 Y 向圓柱的最大半徑，用於排除螺絲側面誤判為鰭片。
    4. screw_r：同軸外凸圓柱的最大半徑（與本體融合的螺絲/墊圈/彈簧），0 表示無螺絲。
    回傳 list[dict(cx, cz, radius, clearance, screw_r)]（公尺）。
    """
    import math

    # 以「同軸中心」分群（忽略半徑差異），累加該中心所有內凹 Y 圓柱分片的圓周角。
    # 沉孔/counterbore 的孔會被切成「大徑沉孔環 + 小徑孔喉」兩段不同半徑，各自可能都
    # 不足完整圓周；但同一中心累加後 ≥ 0.9·2π 即視為真實挖孔，孔徑取該中心最小半徑（孔喉）。
    centers = {}
    for c in cyls:
        if not c["concave"] or c["r"] < min_radius_m:
            continue
        key = (round(c["cx"] / concentric_tol_m), round(c["cz"] / concentric_tol_m))
        g = centers.setdefault(key, {"cx": c["cx"], "cz": c["cz"], "angle": 0.0,
                                     "rmin": c["r"], "segs": []})
        g["angle"] += c["angle"]
        g["rmin"] = min(g["rmin"], c["r"])
        g["segs"].append(c)
    full = [g for g in centers.values() if g["angle"] >= 0.9 * 2 * math.pi]

    holes = []
    for g in full:
        holes.append({"cx": g["cx"], "cz": g["cz"], "radius": g["rmin"]})

    for h in holes:
        coax = [c for c in cyls
                if abs(c["cx"] - h["cx"]) <= concentric_tol_m and abs(c["cz"] - h["cz"]) <= concentric_tol_m]
        concave = [c for c in coax if c["concave"]]
        h["ylo"] = min(c["ylo"] for c in concave) if concave else 0.0
        h["yhi"] = max(c["yhi"] for c in concave) if concave else 0.0
        h["clearance"] = max([c["r"] for c in coax] + [h["radius"]])
        h["screw_r"] = max([c["r"] for c in coax if not c["concave"]] + [0.0])
    return holes


def _diag_corner_cylinders(cyls, bbox_lo, bbox_hi, concentric_tol_m=2e-4, near_corner_m=25e-3):
    """[診斷] 統計靠近四角的同軸 Y 圓柱群，回傳每群 (cx,cz,最小/最大半徑,總圓周角,是否完整圓周)。

    用於找出外側螺絲鎖孔為何未被 _detect_mount_holes 偵測（圓周角不足？半徑不符？外凸？）。
    """
    import math
    cx0, cz0 = (bbox_lo[0] + bbox_hi[0]) / 2.0, (bbox_lo[2] + bbox_hi[2]) / 2.0
    corners = [(bbox_lo[0], bbox_lo[2]), (bbox_hi[0], bbox_lo[2]),
               (bbox_hi[0], bbox_hi[2]), (bbox_lo[0], bbox_hi[2])]
    groups = {}
    for c in cyls:
        if not any(abs(c["cx"] - qx) <= near_corner_m and abs(c["cz"] - qz) <= near_corner_m
                   for qx, qz in corners):
            continue
        key = (round(c["cx"] / concentric_tol_m), round(c["cz"] / concentric_tol_m))
        g = groups.setdefault(key, {"cx": c["cx"], "cz": c["cz"], "rmin": c["r"], "rmax": c["r"],
                                    "ang_cc": 0.0, "ang_cx": 0.0})
        g["rmin"] = min(g["rmin"], c["r"])
        g["rmax"] = max(g["rmax"], c["r"])
        if c["concave"]:
            g["ang_cc"] += c["angle"]
        else:
            g["ang_cx"] += c["angle"]
    out = []
    for g in groups.values():
        g["radial"] = ((g["cx"] - cx0) ** 2 + (g["cz"] - cz0) ** 2) ** 0.5
        g["full"] = g["ang_cc"] >= 0.9 * 2 * math.pi
        out.append(g)
    # 內凹（孔壁）優先、再依徑向最外優先，方便診斷真實鎖孔分佈
    out.sort(key=lambda g: (-g["ang_cc"], -g["radial"]))
    return out


def _select_screw_holes(holes, bbox_lo, bbox_hi, hole_select="screw", outer_margin=0.6):
    """從所有偵測到的孔中挑出真正的「螺絲鎖孔」，排除內側定位點 (locating pin) 孔。

    CPU/power 散熱片四角各有一個外側螺絲鎖孔（鎖上主機板/背板），其斜內側常緊貼一個
    較小的定位銷孔。兩孔徑向距離相近，單純用全域徑向門檻無法分離，故改用「角落分群 →
    每群取最外一孔」策略：

    - "all"：不過濾，保留所有孔（原始行為）。
    - "screw"（預設）：優先保留「同軸有外凸螺絲/彈簧/墊圈」(screw_r > 0) 的孔——真實鎖孔
      最可靠的訊號；若模型未建螺絲（全部 screw_r == 0），退回 "outer" 的角落分群判定。
    - "outer"：依孔相對散熱片 X-Z 中心落在哪個象限分成四個角落群，每群只保留「距中心
      徑向距離最遠」的一孔（即最外側螺絲鎖孔），其餘內側孔（定位銷）剔除；再以
      outer_margin × 全域最大徑向距離過濾掉明顯偏內的孤立孔。

    bbox_lo/bbox_hi：散熱片 world 包圍盒（公尺），用以取 X-Z 幾何中心。
    回傳過濾後的 holes（原 list 的子集，順序不變）。
    """
    if not holes or hole_select == "all":
        return holes

    cx0 = (bbox_lo[0] + bbox_hi[0]) / 2.0
    cz0 = (bbox_lo[2] + bbox_hi[2]) / 2.0

    def _radius(h):
        return ((h["cx"] - cx0) ** 2 + (h["cz"] - cz0) ** 2) ** 0.5

    def _outer_by_corner(subset, use_screw_tiebreak=False):
        """四象限分群，每群保留徑向最遠一孔；再剔除明顯偏內的孤立孔。

        use_screw_tiebreak=True 時，同角落內兩孔徑向距離相近（差 < corner_tol）者，
        改以「有無同軸螺絲 (screw_r)」或較大 clearance 作為該角落代表。
        """
        if len(subset) <= 1:
            return subset
        corner_tol = 3e-3  # 3mm：同角落兩孔徑向距離差在此內視為相近
        quads = {}  # (sign_x, sign_z) -> 該象限代表孔
        for h in subset:
            qx = 1 if (h["cx"] - cx0) >= 0 else -1
            qz = 1 if (h["cz"] - cz0) >= 0 else -1
            cur = quads.get((qx, qz))
            if cur is None:
                quads[(qx, qz)] = h
                continue
            dr = _radius(h) - _radius(cur)
            if dr > corner_tol:
                quads[(qx, qz)] = h          # 明顯更外 → 取代
            elif dr < -corner_tol:
                pass                          # 明顯更內 → 保留原本
            elif use_screw_tiebreak:
                # 徑向相近：優先有螺絲者，其次 clearance（含螺頭/墊圈）較大者，再取較外者
                hk = (h.get("screw_r", 0.0) > 0.0, h.get("clearance", h["radius"]), _radius(h))
                ck = (cur.get("screw_r", 0.0) > 0.0, cur.get("clearance", cur["radius"]), _radius(cur))
                if hk > ck:
                    quads[(qx, qz)] = h
            elif _radius(h) > _radius(cur):
                quads[(qx, qz)] = h
        picked = list(quads.values())
        # 剔除明顯偏內的象限代表（例如某角落根本沒有外側鎖孔，只有中央定位孔）
        r_max = max(_radius(h) for h in picked)
        if r_max > 1e-9:
            picked = [h for h in picked if _radius(h) >= outer_margin * r_max]
        # 維持原 holes 順序
        keep = {id(h) for h in picked}
        return [h for h in holes if id(h) in keep]

    if hole_select == "outer":
        return _outer_by_corner(holes, use_screw_tiebreak=False)

    # "screw"：以角落分群取最外一孔為主（紅＝外側螺絲孔，藍＝內側定位孔），
    #           同角落兩孔徑向相近時才以 screw_r / clearance 作決勝。
    return _outer_by_corner(holes, use_screw_tiebreak=True)


def _hole_plate_span(planes, h):
    """鎖孔所在板材的 (下表面 y, 上表面 y)；找不到回傳 None。

    下表面 = 孔壁最低點以下、涵蓋孔中心的最高朝下平面；上表面 = 其上第一個涵蓋孔中心的朝上平面。
    不以孔壁最高點找上表面：孔上方常有同軸的彈簧座/螺頭沉孔，會把範圍誤拉到鰭片頂。
    """
    def _covers(f):
        ext = _face_extent(f)
        return ext is not None and ext[0][0] <= h["cx"] <= ext[1][0] and ext[0][2] <= h["cz"] <= ext[1][2]

    downs = [y for f, y, _a, up in planes if not up and y <= h["ylo"] + 1e-5 and _covers(f)]
    if not downs:
        return None
    yb = max(downs)
    ups = [y for f, y, _a, up in planes if up and y > yb + 1e-5 and _covers(f)]
    if not ups:
        return None
    return yb, min(ups)


def _simple_heatsink_boxes(planes, holes, rects, lo, hi, y_bot, y_root, contact_box=None, fin_box="largest"):
    """凸字形簡化的三個方塊（world 公尺，各為 (lo_xyz, hi_xyz) 或 None）：無階梯、無圓角。

    - plate（底板）：X-Z 取整體包圍盒；Y 從板底到鰭片根部。板底 = 鎖孔所在板材下表面
      （_hole_plate_span，多孔取最低）；無鎖孔則為主接合底面（即無下凸）。
    - top（上凸）：fin_box="largest" 取面積最大的一個鰭片填實矩形；"all" 取所有鰭片矩形的外框
      （十字形鰭片配置）。鰭片根部 → 鰭片頂。
    - bottom（下凸）：主接合底面（面積 ≥ 該層最大面 10% 的面）的 X-Z 包圍盒，主接合底面 → 板底；
      若包圍盒蓋到鎖孔，則裁成與上凸同 X-Z 範圍，避免下凸填到鎖孔下方。
    - contact_box（接觸體包圍盒，例如 CPU 散熱片的銅底）：給定時下凸 = 接觸體範圍與厚度，
      板底改為接觸體頂面（銅底與框架底面齊平時，下凸才能與框架區分，接觸面 named selection 只含銅底）。
    """
    y_mid = y_root if y_root is not None else y_bot
    spans = [s for s in (_hole_plate_span(planes, h) for h in holes) if s is not None]
    y_pb = min(s[0] for s in spans) if spans else y_bot
    if contact_box is not None:
        y_pb = contact_box[1][1]
    y_pb = min(max(y_pb, y_bot), y_mid)

    plate = ((lo[0], y_pb, lo[2]), (hi[0], y_mid, hi[2])) if y_mid - y_pb > 1e-5 else None

    if fin_box == "all":
        x0, x1 = min(r[0] for r in rects), max(r[1] for r in rects)
        z0, z1 = min(r[2] for r in rects), max(r[3] for r in rects)
        yt = max(r[4] for r in rects)
    else:
        x0, x1, z0, z1, yt = max(rects, key=lambda r: (r[1] - r[0]) * (r[3] - r[2]))
    top = ((x0, y_mid, z0), (x1, yt, z1)) if yt - y_mid > 1e-5 else None

    bottom = None
    if contact_box is not None:
        (cx0, cy0, cz0), (cx1, _cy1, cz1) = contact_box
        if y_pb - cy0 > 1e-5:
            bottom = ((cx0, cy0, cz0), (cx1, y_pb, cz1))
    elif y_pb - y_bot > 1e-5:
        faces = [(f, a) for f, y, a, up in planes if not up and abs(y - y_bot) <= _HS_EPS]
        a_max = max((a for _f, a in faces), default=0.0)
        exts = [e for e in (_face_extent(f) for f, a in faces if a >= _HS_BOTTOM_AREA_RATIO * a_max) if e]
        if exts:
            bx0, bx1 = min(e[0][0] for e in exts), max(e[1][0] for e in exts)
            bz0, bz1 = min(e[0][2] for e in exts), max(e[1][2] for e in exts)
            if any(bx0 - h["radius"] < h["cx"] < bx1 + h["radius"] and bz0 - h["radius"] < h["cz"] < bz1 + h["radius"]
                   for h in holes):
                bx0, bx1, bz0, bz1 = max(bx0, x0), min(bx1, x1), max(bz0, z0), min(bz1, z1)
            if bx1 - bx0 > 1e-5 and bz1 - bz0 > 1e-5:
                bottom = ((bx0, y_bot, bz0), (bx1, y_pb, bz1))
    if plate is None and top is None and bottom is None:
        raise ValueError("無法建立凸字形簡化體（底板/上凸/下凸皆為空）")
    return {"plate": plate, "top": top, "bottom": bottom, "y_plate_bot": y_pb}


def _split_by_gap(own, support, ci, cap_tol):
    """將一個長度群的側壁依排列方向切成子群，回傳 list[(cross_lo, cross_hi, [own walls])]。

    support = 長向範圍涵蓋本群的其他（較長）鰭片群側壁：它們在本群長度內同樣有鰭片，
    故一併參與間距判斷——例如外側短鰭片與中央長鰭片之間的空隙不會被誤切成縫。
    間距 > 3×中位間距（且 > cap_tol）處才切分（例如中間夾螺絲的兩排鰭片）；
    子群範圍取該段所有側壁（含 support）的最外範圍。
    """
    pos = sorted([(w, True) for w in own] + [(w, False) for w in support], key=lambda t: t[0][1][ci])
    if len(pos) < 2:
        return [(pos[0][0][1][ci], pos[0][0][2][ci], [pos[0][0]])] if pos else []
    gaps = [pos[i + 1][0][1][ci] - pos[i][0][2][ci] for i in range(len(pos) - 1)]
    med = sorted(gaps)[len(gaps) // 2]
    limit = max(3.0 * med, cap_tol)
    segs, cur = [], [pos[0]]
    for g, t in zip(gaps, pos[1:]):
        if g > limit:
            segs.append(cur)
            cur = []
        cur.append(t)
    segs.append(cur)
    out = []
    for seg in segs:
        mine = [w for w, is_own in seg if is_own]
        if mine:
            out.append((min(w[1][ci] for w, _o in seg), max(w[2][ci] for w, _o in seg), mine))
    return out


def _fin_fill_rects(body, y_root, y_top, holes, bbox_lo, bbox_hi, group_tol_m=2e-4):
    """由鰭片側壁推算鰭片區的填實矩形：(list[(x0, x1, z0, z1, y_top_of_group)], 鰭片走向)（公尺）。

    鰭片頂面常帶端部圓角/倒角而比鰭片短，故以鰭片【垂直側壁平面】取真實長度：
    1. 候選側壁 = 起點在鰭片根部（含根部圓角容差）、高度 ≥ 最高側壁一半的垂直平面；
       排除中心落在鎖孔 clearance 內者（螺絲/彈簧的側平面）。
    2. 鰭片走向：候選面法向多數為 ±X → 鰭片沿 Z 延伸（沿 X 排列），反之沿 X。
    3. 法向垂直於走向的側壁依「長向範圍」分群（容差 group_tol_m）；群內再依排列間距切分
       （間距 > 3×中位間距 → 視為不同鰭片排，例如中間夾螺絲；較長鰭片群在本群長度內的側壁
       也算數，避免長短鰭片交界被切出縫），每子群以其排列範圍成一矩形。
       → 全長鰭片群形成主體，較短鰭片群只在其長度內延伸，螺絲所在角落自然留下避讓缺口。
    4. 法向平行於走向的端蓋面（鰭片端面/外緣側板）若貼齊某子群長向端點且排列範圍相鄰，擴展該子群。
    5. 長向相鄰的子群（例如針狀鰭片的各列）若間隙 ≤ min(兩群長度, 5mm)，於重疊排列範圍補橋接塊。
    找不到鰭片側壁則退回整個 X-Z 包圍盒。
    """
    walls = []
    for w in _vertical_walls(body):
        axis, lo, hi, _area = w
        if lo[1] < y_root - 1e-5 or lo[1] > y_root + _HS_ROOT_FILLET_M:
            continue
        mx, mz = (lo[0] + hi[0]) / 2.0, (lo[2] + hi[2]) / 2.0
        if any(((mx - h["cx"]) ** 2 + (mz - h["cz"]) ** 2) ** 0.5 <= h["clearance"] + 5e-4 for h in holes):
            continue
        walls.append(w)
    if walls:
        h_max = max(w[2][1] - w[1][1] for w in walls)
        walls = [w for w in walls if w[2][1] - w[1][1] >= 0.5 * h_max]

    sides_x = [w for w in walls if w[0] == 0]
    sides_z = [w for w in walls if w[0] == 2]
    if not walls:
        return [(bbox_lo[0], bbox_hi[0], bbox_lo[2], bbox_hi[2], y_top)], "none"

    # 鰭片沿 Z → 側壁法向為 ±X；長向=Z(索引2)、排列向=X(索引0)
    along_z = len(sides_x) >= len(sides_z)
    li, ci = (2, 0) if along_z else (0, 2)
    sides, caps = (sides_x, sides_z) if along_z else (sides_z, sides_x)

    # 3. 依長向範圍分群
    by_len = []  # [long_lo, long_hi, [walls]]
    for w in sides:
        l0, l1 = w[1][li], w[2][li]
        if l1 - l0 < 1e-5:
            continue
        for g in by_len:
            if abs(g[0] - l0) <= group_tol_m and abs(g[1] - l1) <= group_tol_m:
                g[2].append(w)
                break
        else:
            by_len.append([l0, l1, [w]])

    groups = []  # 每子群：[long_lo, long_hi, cross_lo, cross_hi, ytop]
    cap_tol = 2e-3
    for l0, l1, ws in by_len:
        support = [w for g0, g1, gws in by_len if (g0, g1) != (l0, l1)
                   and g0 <= l0 + group_tol_m and g1 >= l1 - group_tol_m for w in gws]
        for c0, c1, sub in _split_by_gap(ws, support, ci, cap_tol):
            groups.append([l0, l1, c0, c1, max(w[2][1] for w in sub)])

    # 4. 端蓋面擴展（需貼齊長向端點，且排列範圍與子群相鄰）
    for _a, lo, hi, _area in caps:
        for g in groups:
            if min(abs(lo[li] - g[0]), abs(lo[li] - g[1])) > group_tol_m:
                continue
            if hi[ci] < g[2] - cap_tol or lo[ci] > g[3] + cap_tol:
                continue
            g[2], g[3] = min(g[2], lo[ci]), max(g[3], hi[ci])

    groups = [g for g in groups if g[3] - g[2] >= 1e-5]

    # 5. 長向相鄰子群之間的橋接（針狀鰭片列與列之間）
    bridges = []
    srt = sorted(groups, key=lambda g: g[0])
    for i, a in enumerate(srt):
        for b in srt[i + 1:]:
            gap = b[0] - a[1]
            if gap <= 1e-6:
                continue
            if gap > min(a[1] - a[0], b[1] - b[0], 5e-3):
                continue
            c0, c1 = max(a[2], b[2]), min(a[3], b[3])
            if c1 - c0 >= 1e-5:
                bridges.append([a[1], b[0], c0, c1, min(a[4], b[4])])
                break  # 只橋接到長向最近的一群

    rects = []
    for l0, l1, c0, c1, y in groups + bridges:
        rects.append((c0, c1, l0, l1, y) if along_z else (l0, l1, c0, c1, y))
    if not rects:
        return [(bbox_lo[0], bbox_hi[0], bbox_lo[2], bbox_hi[2], y_top)], "none"
    return rects, ("Z" if along_z else "X")


def _comp_bodies(design, comp_id):
    """重新從設計樹取得某 component 下的 body（布林運算後 Component 物件快取會過期）。"""
    return [b for b in design.get_all_bodies() if b.parent_component.id == comp_id]


def _master_key(component):
    """component 的 master 識別碼：同一 master 的多個 instance 只需簡化一次。"""
    master = getattr(component, "_master_component", None)
    return getattr(master, "id", None) or component.id

def _make_cylinder_body(design, name, cx, cz, radius, y_bottom, y_top):
    """於 (cx, cz) 建立沿 Y 軸、從 y_bottom 到 y_top 的實心圓柱 body（公尺）。用於扣孔。

    草圖平面取 X-Z 面但方向需使法向指向 +Y，才能沿 +Y 正確拉伸孔高。
    法向 = direction_x × direction_y，故取 direction_x=+Z、direction_y=+X →
    法向 = (0,0,1)×(1,0,0) = (0,1,0) = +Y。此時草圖 local 座標為 (u=Z, v=X)，
    圓心需以 Point2D([cz, cx]) 給定。
    """
    from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D
    from ansys.geometry.core.misc import UNITS, Distance
    from ansys.geometry.core.sketch import Sketch

    plane = Plane(
        origin=Point3D([0, y_bottom, 0], UNITS.m),
        direction_x=UnitVector3D([0, 0, 1]),
        direction_y=UnitVector3D([1, 0, 0]),
    )
    sketch = Sketch(plane).circle(Point2D([cz, cx], UNITS.m), Distance(radius, UNITS.m))
    return design.extrude_sketch(name, sketch, Distance(y_top - y_bottom, UNITS.m))


def _resolve_heatsink_groups(design, source, extra_sources, all_instances):
    """解析要簡化的散熱片：回傳 list[list[Body]]，每個元素為「同一 component instance 內」的一組 body。

    - source：主 body 名稱（決定結果命名與所屬 component）。
    - extra_sources：額外併入的 body 名稱或 glob（例如 'ICX_HS_1U_FIN_*'），只在主 body 的
      同一 component instance 內比對；曲面 body 自動略過。用於鰭片/底座分屬多個 body 的組件。
    - all_instances：True 時處理所有含 source 的 component（同 master 只處理一次）；
      False 時只處理第一個。
    """
    import fnmatch

    matches = [b for b in _find_bodies_by_name(source) if not b.is_surface]
    if not matches:
        return []
    groups, seen = [], set()
    for b in matches:
        comp = b.parent_component
        key = _master_key(comp)
        if key in seen:
            continue
        seen.add(key)
        group = [b]
        if extra_sources:
            for o in _comp_bodies(design, comp.id):
                if o.id == b.id or o.is_surface:
                    continue
                if any(fnmatch.fnmatchcase(o.name, pat) for pat in extra_sources):
                    group.append(o)
        groups.append(group)
        if not all_instances:
            break
    return groups




def _body_density(body, default_rho, body_densities):
    """逐 body 密度：先比對 body_densities（glob，依字典序）；未命中則回傳 default_rho。"""
    import fnmatch

    for pat, val in (body_densities or {}).items():
        if fnmatch.fnmatchcase(body.name, pat):
            if isinstance(val, str):
                return HEATSINK_DENSITY_PRESETS.get(val.lower(), default_rho)
            return float(val)
    return default_rho


def _simplify_heatsink_group(design, bodies, base_name, default_rho, body_densities,
                             keep_source, named_selection, name_density_suffix, hole_min_dia_mm,
                             contact_body=None, fin_box="largest", hole_select="screw", progress=None,
                             diagnose_only=False):
    """簡化一組散熱片 body（同一 component instance），回傳結果 dict；失敗時清除暫存並拋例外。

    progress(msg)：於各階段開始時呼叫；逾時由其拋 TimeoutError，走既有清除暫存流程。
    """
    import fnmatch

    from ansys.geometry.core.misc import UNITS

    _p = progress or (lambda _msg: None)
    src = bodies[0]
    comp = src.parent_component
    comp_id = comp.id

    # --- 1. 原始體積與質量（逐 body 密度）---
    parts = []
    for b in bodies:
        v = b.volume.m_as(UNITS.m ** 3)
        parts.append((b.name, v, _body_density(b, default_rho, body_densities)))
    v_orig = sum(p[1] for p in parts)
    mass = sum(p[1] * p[2] for p in parts)
    if v_orig <= 0:
        raise ValueError(f"原始 body 體積量測異常 (V={v_orig})")

    before_ids = {b.id for b in _comp_bodies(design, comp_id)}
    temps = []
    pad = 1e-3  # 1mm：暫存切割體外擴量，確保布林乾淨
    try:
        # --- 2. 母體：原始 body 的 copy（多 body 則聯集成一體）---
        _p(f"複製並聯集 {len(bodies)} 個 body")
        work = src.copy(comp, base_name)
        if len(bodies) > 1:
            others = [b.copy(comp, f"{base_name}_tmp_part") for b in bodies[1:]]
            temps.extend(others)
            work.unite(others, keep_other=False)

        # --- 3. 幾何特徵分析（world 座標）---
        _p("分析底面 / 鰭片 / 鎖孔幾何特徵")
        lo, hi = _bbox_m(work)
        y_top = hi[1]
        planes = _horizontal_planes(work)
        _bf, y_bot = _main_bottom_plane(planes)
        if y_bot is None:
            y_bot = lo[1]
        walls = _vertical_walls(work)
        y_root = _fin_root_y(planes, walls, y_bot, y_top)
        cyls = _y_cylinders(work)
        all_holes = _detect_mount_holes(cyls, min_radius_m=max(hole_min_dia_mm, 0.0) / 2000.0)
        # 篩出真正的外側螺絲鎖孔，排除中央定位銷孔（locating pin）
        holes = _select_screw_holes(all_holes, lo, hi, hole_select=hole_select)
        # [診斷] 針對四角統計所有同軸內凹 Y 圓柱（含未達完整圓周門檻者），找出紅色螺絲孔為何漏偵
        corner_diag = _diag_corner_cylinders(cyls, lo, hi)
        if diagnose_only:
            # 僅做幾何偵測與診斷，略過昂貴的方塊重建與布林運算；清除暫存母體後直接回傳。
            for b in temps:
                _safe_delete(b)
            _safe_delete(work)
            return {
                "result_body": "(diagnose_only)", "component": comp.name, "parts": parts,
                "v_orig": v_orig, "mass": mass, "v_sim": v_orig, "rho_equiv": mass / v_orig,
                "lo": lo, "hi": hi, "y_bot": y_bot, "y_root": y_root, "y_top": y_top,
                "shape": {"plate": None, "top": None, "bottom": None}, "fin_axis": "none",
                "holes": holes, "all_holes": all_holes, "corner_diag": corner_diag,
                "removed_count": 0, "removed_vol": 0.0,
                "named_selection": None, "ns_faces": 0,
            }
        fill_from = y_root if y_root is not None else y_bot
        # 鰭片側壁避讓仍以「所有孔」的 clearance 判定，避免被捨棄孔附近的螺絲側平面誤判成鰭片
        rects, fin_axis = _fin_fill_rects(work, fill_from, y_top, all_holes, lo, hi)

        def _largest():
            """布林後母體可能被拆成多塊，且原 handle 不一定留在主體上（可能落在小碎片）→ 重取體積最大者。"""
            temp_ids = {t.id for t in temps}
            cands = [b for b in _comp_bodies(design, comp_id) if b.id not in before_ids and b.id not in temp_ids]
            return max(cands, key=lambda b: b.volume.m_as(UNITS.m ** 3))

        # --- 4. 凸字形方塊組（world 座標，建於根設計）：底板 + 上凸（鰭片）+ 下凸（接觸面），無階梯/圓角 ---
        contact_box = None
        if contact_body:
            cbs = [b for b in bodies if fnmatch.fnmatchcase(b.name, contact_body)]
            if not cbs:
                raise ValueError(f"contact_body '{contact_body}' 不在本組 body 中（需為 source 或 extra_sources 之一）")
            boxes_c = [_bbox_m(b) for b in cbs]
            contact_box = (tuple(min(bx[0][i] for bx in boxes_c) for i in range(3)),
                           tuple(max(bx[1][i] for bx in boxes_c) for i in range(3)))
        shape = _simple_heatsink_boxes(planes, holes, rects, lo, hi, y_bot, y_root,
                                       contact_box=contact_box, fin_box=fin_box)
        _p(f"建立凸字形方塊組並扣 {len(holes)} 個鎖孔")
        boxes = []
        for key in ("plate", "top", "bottom"):
            if shape[key] is not None:
                b = _make_box_from_bbox(design, f"{base_name}_tmp_{key}", *shape[key])
                temps.append(b)
                boxes.append(b)
        blk = boxes[0]
        if len(boxes) > 1:
            blk.unite(boxes[1:], keep_other=False)
        # 鎖孔：Y 向直圓柱貫穿
        for i, h in enumerate(holes, start=1):
            cb = _make_cylinder_body(design, f"{base_name}_tmp_hole_{i:02d}", h["cx"], h["cz"], h["radius"],
                                     lo[1] - pad, hi[1] + pad)
            temps.append(cb)
            try:
                blk.subtract(cb, keep_other=False)
            except Exception as e:
                logger.info(f"鎖孔 {i} 未碰到簡化體，略過: {e}")
                _safe_delete(cb)

        # --- 5. 將方塊組放進原始 body 所屬 component：母體 ∪ 方塊組 → ∩ 方塊組（= 方塊組本身）---
        #        直接 copy 根設計的 body 到 component instance 會套用 instance 變換而錯位，故以布林轉入。
        _p("將方塊組轉入原 component（布林）")
        blk2 = blk.copy(design, f"{base_name}_tmp_shape")
        temps.append(blk2)
        work.unite([blk], keep_other=False)
        work = _largest()
        work.intersect(blk2, keep_other=False)
        work = _largest()
    except Exception:
        for b in temps:
            _safe_delete(b)
        for b in _comp_bodies(design, comp_id):
            if b.id not in before_ids:
                _safe_delete(b)
        raise

    # 只留體積最大者為簡化體；其餘（螺絲頭、彈簧、推銷、墊圈等不相連殘塊）清除
    _p("清除殘塊、建立 named selection 與命名")
    candidates =[b for b in _comp_bodies(design, comp_id) if b.id not in before_ids]
    vols = {b.id: b.volume.m_as(UNITS.m ** 3) for b in candidates}
    main = max(candidates, key=lambda b: vols[b.id])
    leftovers = [b for b in candidates if b.id != main.id]
    removed_vol = sum(vols[b.id] for b in leftovers)
    for b in leftovers:
        _safe_delete(b)

    # --- 7. 底面 named selection（主接合底面：同高度所有朝下平面）---
    ns_created = False
    main_planes = _horizontal_planes(main)
    _bf, y_ns = _main_bottom_plane(main_planes)
    bottom_faces = [p[0] for p in main_planes
                    if not p[3] and y_ns is not None and abs(p[1] - y_ns) <= _HS_EPS]
    if bottom_faces and named_selection:
        try:
            design.create_named_selection(named_selection, faces=bottom_faces)
            ns_created = True
        except Exception as e:
            logger.warning(f"建立底面 named selection '{named_selection}' 失敗: {e}")

    # --- 8. 反推等效密度並命名 ---
    v_sim = vols[main.id]
    if v_sim <= 0:
        raise ValueError(f"簡化體 '{base_name}' 體積量測異常 (V={v_sim})")
    rho_equiv = mass / v_sim  # kg/m³（質量守恆反推）
    final_name = f"{base_name}_rho{rho_equiv:.0f}" if name_density_suffix else base_name
    try:
        main.set_name(final_name)
    except Exception as e:
        logger.warning(f"重新命名簡化體為 '{final_name}' 失敗: {e}")
        final_name = base_name

    if not keep_source:
        for b in bodies:
            _safe_delete(b)

    return {
        "result_body": final_name, "component": comp.name, "parts": parts,
        "v_orig": v_orig, "mass": mass, "v_sim": v_sim, "rho_equiv": rho_equiv,
        "lo": lo, "hi": hi, "y_bot": y_bot, "y_root": y_root, "y_top": y_top,
        "shape": shape, "fin_axis": fin_axis, "holes": holes, "all_holes": all_holes,
        "corner_diag": corner_diag,
        "removed_count": len(leftovers), "removed_vol": removed_vol,
        "named_selection": named_selection if ns_created else None,
        "ns_faces": len(bottom_faces),
    }


def _format_heatsink_result(r, material, default_rho, hole_min_dia_mm):
    """將單組簡化結果整理為人類可讀報告（毫米、g、kg/m³）。"""
    lo, hi = r["lo"], r["hi"]
    size = [hi[i] - lo[i] for i in range(3)]
    root_txt = f"{_mm(r['y_root'])}" if r["y_root"] is not None else "（無獨立底板）"
    lines = [f"✓ '{r['parts'][0][0]}' → '{r['result_body']}'（component '{r['component']}'）"]
    if len(r["parts"]) > 1:
        lines.append(f"  併入 {len(r['parts'])} 個 body：" + ", ".join(
            f"{n}(ρ={rho:.0f})" for n, _v, rho in r["parts"][:12])
            + (" …" if len(r["parts"]) > 12 else ""))
    lines += [
        f"  材料/密度假設: {material} ρ={default_rho:.1f} kg/m³（可由 body_densities 逐 body 覆寫）",
        f"  原始體積 V_orig = {r['v_orig']*1e9:.3f} mm³；估算質量 m = {r['mass']*1000:.3f} g",
        f"  外包圍尺寸 (mm): {[_mm(s) for s in size]}",
        f"  高度層 (Y, mm): 主接合底面={_mm(r['y_bot'])}  鰭片根部={root_txt}  頂={_mm(r['y_top'])}",
        f"  凸字形方塊（鰭片走向={r['fin_axis']}）: "
        + "；".join(f"{label} X[{_mm(b[0][0])},{_mm(b[1][0])}] Y[{_mm(b[0][1])},{_mm(b[1][1])}] Z[{_mm(b[0][2])},{_mm(b[1][2])}]"
                   for label, b in (("底板", r["shape"]["plate"]), ("上凸", r["shape"]["top"]),
                                    ("下凸", r["shape"]["bottom"])) if b is not None),
        f"  鎖孔 {len(r['holes'])} 個（Y 向直圓柱，孔徑 ≥{hole_min_dia_mm}mm）: "
        + ", ".join(f"Ø{_mm(h['radius']*2)}@({_mm(h['cx'])},{_mm(h['cz'])})" for h in r["holes"]),
        f"  [診斷] 偵測到全部孔 {len(r.get('all_holes', []))} 個: "
        + ", ".join(f"Ø{_mm(h['radius']*2)}@({_mm(h['cx'])},{_mm(h['cz'])})"
                    f"[screw_r={_mm(h.get('screw_r',0)*2)},clr={_mm(h.get('clearance',0)*2)}]"
                    for h in r.get("all_holes", [])),
        "  [診斷] 四角同軸Y圓柱群(僅內凹,凹角大/外側優先): "
        + "; ".join([f"@({_mm(g['cx'])},{_mm(g['cz'])})r={_mm(g['rmin']*2)}~{_mm(g['rmax']*2)}"
                     f"径距{_mm(g['radial'])}凹角{g['ang_cc']/3.14159:.2f}π"
                     f"{'[完整孔]' if g['full'] else '[未達完整]'}"
                     for g in r.get("corner_diag", []) if g.get("ang_cc", 0) > 0.01][:20]),
        f"  簡化後體積 V_sim = {r['v_sim']*1e9:.3f} mm³",
        f"  底面 named selection: {r['named_selection']}（{r['ns_faces']} 面）",
        f"  ★ 反推等效密度 ρ_equiv = m / V_sim = {r['rho_equiv']:.3f} kg/m³",
    ]
    return "\n".join(lines)


def _geom_simplify_heatsink(source: str, result_name: str = None,
                            density: float = None, material: str = "aluminum",
                            keep_source: bool = True,
                            named_selection: str = "hs_bottom",
                            name_density_suffix: bool = True,
                            hole_min_dia_mm: float = 2.5,
                            extra_sources: list[str] | None = None,
                            body_densities: dict | None = None,
                            all_instances: bool = False,
                            contact_body: str | None = None,
                            fin_box: str = "largest",
                            hole_select: str = "screw",
                            progress=None,
                            diagnose_only: bool = False) -> str:
    """將散熱片簡化為凸字形方塊組（底板＋上凸＋下凸＋鎖孔直圓柱），並反推等效密度。

    流程（每組 = 同一 component instance 內的 source + extra_sources）：
      1. 量測原始體積，以密度（material 預設或 body_densities 逐 body）算質量 m。
      2. 分析主接合底面/鰭片根部/鎖孔/鰭片排，以方塊重建（見 _simple_heatsink_boxes）；
         contact_body 指定接觸體（下凸）、fin_box 指定上凸取最大一排或全部鰭片外框。
      3. 鎖孔以 Y 向直圓柱貫穿；主接合底面建立 named selection；ρ_equiv = m / V_sim 附加於 body 名稱。
    """
    _p = progress or (lambda _msg: None)
    from . import call_dispatch as _cd
    design = _cd._geom_get_design()
    _p(f"搜尋散熱片 body '{source}'")
    groups = _resolve_heatsink_groups(design, source, extra_sources, all_instances)
    if not groups:
        all_names = sorted({b.name for b in design.bodies})
        return f"錯誤：找不到散熱片實體 body '{source}'。根層實體: {all_names}"

    rho = density
    if rho is None:
        rho = HEATSINK_DENSITY_PRESETS.get((material or "aluminum").lower(),
                                           HEATSINK_DENSITY_PRESETS["aluminum"])

    reports, errors = [], []
    src_names = []
    for idx, bodies in enumerate(groups, start=1):
        base = result_name or f"{source}_sim"
        if len(groups) > 1:
            base = f"{base}_{idx:02d}"
        ns = named_selection
        if ns and len(groups) > 1:
            ns = f"{ns}_{idx:02d}"
        # 在簡化（可能刪除/改名原始 body）前，先記錄來源名稱樣式
        grp_src_names = [n for n in (_source_body_name(b) for b in bodies) if n]
        try:
            r = _simplify_heatsink_group(design, bodies, base, rho, body_densities, keep_source,
                                         ns, name_density_suffix, hole_min_dia_mm,
                                         contact_body=contact_body, fin_box=fin_box,
                                         hole_select=hole_select,
                                         progress=lambda m, i=idx: _p(f"[{i}/{len(groups)}] {m}"),
                                         diagnose_only=diagnose_only)
            reports.append(_format_heatsink_result(r, material, rho, hole_min_dia_mm))
            src_names.extend(grp_src_names)
        except TimeoutError as e:
            errors.append(f"✗ component '{bodies[0].parent_component.name}': {e}（暫存幾何已清除，其餘組未處理）")
            break
        except Exception as e:
            errors.append(f"✗ component '{bodies[0].parent_component.name}': {e}（暫存幾何已清除）")

    head = f"散熱片簡化完成 {len(reports)}/{len(groups)} 組（'{source}'）"
    # 預設（keep_source=True）保留原始 body → 以已驗證的伺服器端腳本 suppress-for-physics + 隱藏，
    # 使其在下游網格/求解被排除且不干擾框選；diagnose_only 或 keep_source=False 時不處理。
    if keep_source and not diagnose_only and src_names:
        ok, hide_detail = _suppress_hide_sources(src_names)
        if ok:
            head += f"；已抑制+隱藏 {len(set(src_names))} 種原始 body 名稱"
        else:
            head += "；⚠ 原始 body 抑制/隱藏未生效"
            if hide_detail:
                errors.append(hide_detail)
    return "\n".join([head] + reports + errors)

