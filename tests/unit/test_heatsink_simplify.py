# -*- coding: utf-8 -*-
"""散熱片簡化 (geometry_simplify_heatsink) 幾何特徵偵測的單元測試。

以 ENDURANCE-POWER-BRICK-HS-241018 實測數據（單位 mm → 換算公尺）建立假 face，
驗證：主接合底面、鰭片根部、鎖孔孔喉、鰭片填實矩形（含螺絲角落避讓缺口）。
不需連線 SpaceClaim。
"""
import math
from types import SimpleNamespace

import pytest

pytest.importorskip("ansys.geometry.core")

from ansys.geometry.core.designer.face import SurfaceType  # noqa: E402

from ansys_unified_mcp.products.geometry import call_dispatch as S  # noqa: E402

MM = 1e-3


def _pt(x, y, z):
    return SimpleNamespace(x=x * MM, y=y * MM, z=z * MM)


def _plane_face(n, x0, x1, y0, y1, z0, z1):
    """建立假平面 face：法向 n，edge 端點覆蓋 [x0,x1]×[y0,y1]×[z0,z1]（mm）。"""
    edges = [SimpleNamespace(start=_pt(x0, y0, z0), end=_pt(x1, y1, z1))]
    area = max(x1 - x0, z1 - z0) * (y1 - y0) * 1e-6
    return SimpleNamespace(
        surface_type=SurfaceType.SURFACETYPE_PLANE,
        normal=lambda u, v, n=n: SimpleNamespace(x=n[0], y=n[1], z=n[2]),
        edges=edges,
        area=area,
    )


def _plane(y_mm, area_mm2, up):
    return (None, y_mm * MM, area_mm2 * 1e-6, up)


FULL, QUARTER = 2 * math.pi, math.pi / 2


def _cyl(cx, cz, r, ylo, yhi, concave, angle=FULL):
    return {"cx": cx * MM, "cz": cz * MM, "r": r * MM, "ylo": ylo * MM, "yhi": yhi * MM,
            "concave": concave, "angle": angle}


# 實測水平面（螺絲尾 20.895 面積極小；主接合底面 23.595；鰭片間隙根部 26.095）
PLANES = [
    _plane(20.895, 3.2, False),
    _plane(23.595, 1400.0, False), _plane(23.595, 92.5, False),
    _plane(24.095, 184.7, False),
    _plane(25.095, 25.0, False),
    _plane(26.095, 213.8, True), _plane(26.095, 215.6, True),
    *[_plane(26.095, 36.8, True) for _ in range(11)],
    _plane(27.095, 11.5, True),
    _plane(44.895, 29.5, True),
    _plane(49.095, 26.0, True),
]

# 單一鎖孔位置的同軸圓柱：螺絲本體（外凸）、底面沉孔 r3.6（不通到根部）、孔喉 r2.5、彈簧座 r2.6
CYLS = [
    _cyl(-212.62, -348.28, 1.5, 21.395, 23.895, False),
    _cyl(-212.62, -348.28, 2.35, 25.095, 43.395, False),
    _cyl(-212.62, -348.28, 3.6, 24.845, 25.095, True),
    _cyl(-212.62, -348.28, 4.5, 24.845, 25.095, False),
    _cyl(-212.62, -348.28, 2.5, 25.095, 26.095, True),
    _cyl(-212.62, -348.28, 2.6, 26.095, 27.095, True),
    _cyl(-212.62, -348.28, 4.0, 43.395, 44.395, False),
    _cyl(-217.20, -343.96, 1.0, 25.095, 26.095, True),   # 底板圓角（Ø2 < 門檻）
    _cyl(-190.00, -360.00, 3.0, 23.595, 26.095, True, QUARTER),  # 內圓角（非完整圓周）
]


def test_main_bottom_plane_ignores_screw_tip():
    _f, y = S._main_bottom_plane(PLANES)
    assert y == pytest.approx(23.595 * MM)


def _wall(y0, y1, area_mm2=500.0):
    return (0, (0.0, y0 * MM, 0.0), (0.0, y1 * MM, 0.01), area_mm2 * 1e-6)


def test_fin_root_is_level_where_fin_walls_start():
    walls = [_wall(26.595, 49.095)] * 10
    y = S._fin_root_y(PLANES, walls, 23.595 * MM, 49.095 * MM)
    assert y == pytest.approx(26.095 * MM)


def test_fin_root_prefers_fin_walls_over_bigger_cover_plane():
    """折片鰭片夾在底板與上蓋之間：上蓋頂面面積較大，但鰭片側壁起於底板頂面。"""
    planes = [_plane(9.0, 1400.0, False), _plane(11.0, 1000.0, True), _plane(17.7, 1200.0, True),
              _plane(22.0, 40.0, True)]
    walls = [_wall(11.0, 17.3)] * 30
    y = S._fin_root_y(planes, walls, 9.0 * MM, 22.0 * MM)
    assert y == pytest.approx(11.0 * MM)


def test_fin_root_falls_back_to_largest_level_without_walls():
    planes = [_plane(10.0, 100.0, False), _plane(12.0, 80.0, True), _plane(15.0, 20.0, True),
              _plane(20.0, 100.0, True)]
    assert S._fin_root_y(planes, [], 10.0 * MM, 20.0 * MM) == pytest.approx(12.0 * MM)


def test_fin_root_none_without_inner_upward_planes():
    planes = [_plane(10.0, 100.0, False), _plane(20.0, 100.0, True)]
    assert S._fin_root_y(planes, [], 10.0 * MM, 20.0 * MM) is None


def test_main_bottom_keeps_lower_contact_pedestal():
    """底板下方較小的接觸凸台（≥10% 面積）才是熱接觸面，不可被當作雜訊截掉。"""
    planes = [_plane(10.595, 9.0, False), _plane(11.595, 105.0, False), _plane(12.095, 213.4, False)]
    _f, y = S._main_bottom_plane(planes)
    assert y == pytest.approx(11.595 * MM)


def test_mount_hole_uses_min_coaxial_radius_and_clearance():
    holes = S._detect_mount_holes(CYLS, min_radius_m=2.0 * MM)
    assert len(holes) == 1
    h = holes[0]
    assert h["radius"] == pytest.approx(2.5 * MM)          # 同軸最小孔徑 Ø5，沉孔細節捨棄
    assert h["clearance"] == pytest.approx(4.5 * MM)       # 同軸最大半徑
    assert h["screw_r"] == pytest.approx(4.5 * MM)         # 同軸外凸最大＝螺頭/墊圈
    assert (h["cx"], h["cz"]) == pytest.approx((-212.62 * MM, -348.28 * MM))


def test_mount_hole_any_original_hole_regardless_of_height():
    """不論孔在哪個高度、是否開口於鰭片根部（例如底部盲孔），只要是原始挖孔都保留。"""
    cyls = [_cyl(0.0, 0.0, 1.5, 12.1, 13.6, True), _cyl(0.0, 0.0, 2.5, 23.1, 23.9, False),
            _cyl(10.0, 0.0, 2.0, 0.0, 1.0, True)]
    holes = sorted(S._detect_mount_holes(cyls, min_radius_m=1.25 * MM), key=lambda h: h["cx"])
    assert [round(h["radius"] / MM, 3) for h in holes] == [1.5, 2.0]
    assert (holes[0]["ylo"], holes[0]["yhi"]) == pytest.approx((12.1 * MM, 13.6 * MM))


def test_mount_hole_counterbore_split_across_radii():
    """沉孔(counterbore)被切成大徑沉孔環+小徑孔喉兩段不同半徑，各自不足完整圓周，
    但同一中心累加 >= 0.9*2π 即視為真實挖孔，孔徑取孔喉(最小半徑)。
    （對應 CPU 散熱片外側紅色螺絲鎖孔之前漏偵的情況）"""
    cyls = [
        _cyl(-87.68, -634.03, 5.0, 24.0, 26.0, True, math.pi * 1.5),   # 大徑沉孔環 1.5π
        _cyl(-87.68, -634.03, 2.5, 20.0, 24.0, True, math.pi * 1.5),   # 小徑孔喉 1.5π（單獨皆不足2π）
    ]
    holes = S._detect_mount_holes(cyls, min_radius_m=2.0 * MM)
    assert len(holes) == 1
    assert holes[0]["radius"] == pytest.approx(2.5 * MM)   # 孔喉
    assert holes[0]["clearance"] == pytest.approx(5.0 * MM)


def test_hole_plate_span_ignores_coaxial_recesses_above_plate():
    """孔上方的彈簧座/沉孔（同軸內凹）不可把板厚上界拉到鰭片頂。"""
    cover = lambda y, up: (_plane_face((0, 1 if up else -1, 0), -220, -160, y, y, -380, -340), y * MM, 1e-4, up)
    planes = [cover(23.595, False), cover(24.095, False), cover(26.095, True), cover(49.095, True)]
    h = {"cx": -212.62 * MM, "cz": -348.28 * MM, "ylo": 24.845 * MM, "yhi": 44.0 * MM}
    yb, yt = S._hole_plate_span(planes, h)
    assert (yb, yt) == pytest.approx((24.095 * MM, 26.095 * MM))


def _hplane(y, up, x0, x1, z0, z1, area_mm2):
    face = _plane_face((0, 1 if up else -1, 0), x0, x1, y, y, z0, z1)
    return (face, y * MM, area_mm2 * 1e-6, up)


def test_simple_boxes_t_shape_with_bottom_pedestal_clipped_off_holes():
    """凸字形：底板全包圍盒、上凸取最大鰭片矩形、下凸裁到上凸範圍以避開角落鎖孔。"""
    planes = [_hplane(23.595, False, -218.2, -159.8, -379.76, -342.96, 1400.0),  # 十字形接觸面（範圍蓋到角落）
              _hplane(25.095, False, -218.2, -159.8, -379.76, -342.96, 300.0),   # 鎖孔所在法蘭下表面
              _hplane(26.095, True, -218.2, -159.8, -379.76, -342.96, 400.0)]
    holes = [{"cx": -212.62 * MM, "cz": -348.28 * MM, "radius": 2.5 * MM, "ylo": 25.095 * MM, "yhi": 26.095 * MM}]
    rects = [(-218.2 * MM, -159.8 * MM, -368.76 * MM, -353.96 * MM, 49.095 * MM),   # 短鰭片 864 mm²
             (-206.0 * MM, -172.0 * MM, -379.76 * MM, -342.96 * MM, 49.095 * MM)]   # 全長鰭片 1251 mm²
    lo, hi = (-218.2 * MM, 23.0 * MM, -379.76 * MM), (-159.8 * MM, 49.095 * MM, -342.96 * MM)
    s = S._simple_heatsink_boxes(planes, holes, rects, lo, hi, 23.595 * MM, 26.095 * MM)
    mm = lambda box: tuple(round(v / MM, 3) for p in box for v in p)
    assert mm(s["plate"]) == (-218.2, 25.095, -379.76, -159.8, 26.095, -342.96)
    assert mm(s["top"]) == (-206.0, 26.095, -379.76, -172.0, 49.095, -342.96)
    assert mm(s["bottom"]) == (-206.0, 23.595, -379.76, -172.0, 25.095, -342.96)


def test_simple_boxes_no_holes_has_no_bottom_pedestal():
    planes = [_hplane(10.0, False, 0, 30, 0, 20, 600.0), _hplane(12.0, True, 0, 30, 0, 20, 300.0)]
    rects = [(5 * MM, 25 * MM, 0.0, 20 * MM, 30 * MM)]
    s = S._simple_heatsink_boxes(planes, [], rects, (0, 10 * MM, 0), (30 * MM, 30 * MM, 20 * MM),
                                 10 * MM, 12 * MM)
    assert s["bottom"] is None
    assert s["plate"][0][1] == pytest.approx(10 * MM) and s["plate"][1][1] == pytest.approx(12 * MM)


def test_simple_boxes_contact_body_and_all_fins():
    """CPU 散熱片：銅底與框架底面齊平 → 以銅底為下凸、底板從銅底頂面起；十字形鰭片取全部外框。"""
    planes = [_hplane(14.735, False, -93.0, -14.1, -638.1, -520.1, 9000.0),
              _hplane(19.235, True, -93.0, -14.1, -638.1, -520.1, 3000.0)]
    rects = [(-90.62 * MM, -16.50 * MM, -617.05 * MM, -541.05 * MM, 38.835 * MM),   # 76 長兩側＋中間
             (-71.10 * MM, -36.60 * MM, -634.60 * MM, -523.60 * MM, 39.435 * MM)]   # 111 長中間鰭片
    lo, hi = (-93.0 * MM, 14.735 * MM, -638.1 * MM), (-14.1 * MM, 39.435 * MM, -520.1 * MM)
    cbox = ((-80.7 * MM, 14.73 * MM, -618.3 * MM), (-26.4 * MM, 16.23 * MM, -539.8 * MM))
    s = S._simple_heatsink_boxes(planes, [], rects, lo, hi, 14.735 * MM, 19.235 * MM,
                                 contact_box=cbox, fin_box="all")
    mm = lambda box: tuple(round(v / MM, 3) for p in box for v in p)
    assert mm(s["bottom"]) == (-80.7, 14.73, -618.3, -26.4, 16.23, -539.8)
    assert mm(s["plate"]) == (-93.0, 16.23, -638.1, -14.1, 19.235, -520.1)
    assert mm(s["top"]) == (-90.62, 19.235, -634.6, -16.5, 39.435, -523.6)


def test_mount_hole_rejects_split_but_partial_faces():
    """兩片半圓孔壁累加為完整圓周 → 孔；單片四分之一圓 → 圓角。"""
    half = [_cyl(0.0, 0.0, 2.0, 0.0, 2.0, True, math.pi)] * 2
    assert len(S._detect_mount_holes(half, 1.0 * MM)) == 1
    quarter = [_cyl(0.0, 0.0, 2.0, 0.0, 2.0, True, QUARTER)]
    assert S._detect_mount_holes(quarter, 1.0 * MM) == []


def test_mount_hole_threshold_filters_small_holes():
    holes = S._detect_mount_holes(CYLS, min_radius_m=4.0 * MM)
    assert holes == []


def _cone_face(cx, cz, r_mid, ylo, yhi, half_angle, area_mm2):
    """建立假 Y 向錐面 face（內凹孔壁）：面中點位於軸心 +Z 側 r_mid 處、法向指向軸心。"""
    geom = SimpleNamespace(origin=_pt(cx, (ylo + yhi) / 2, cz), dir_z=SimpleNamespace(x=0.0, y=-1.0, z=0.0),
                           radius=r_mid * MM, half_angle=half_angle)
    edges = [SimpleNamespace(start=_pt(cx, ylo, cz - r_mid), end=_pt(cx, yhi, cz - r_mid))]
    return SimpleNamespace(
        surface_type=SurfaceType.SURFACETYPE_CONE,
        shape=SimpleNamespace(geometry=geom),
        point=lambda u, v: _pt(cx, (ylo + yhi) / 2, cz + r_mid),
        normal=lambda u, v: SimpleNamespace(x=0.0, y=-0.02, z=-1.0),
        edges=edges,
        area=area_mm2 * 1e-6,
    )


def test_y_cylinders_accepts_draft_cone_holes_rejects_chamfers():
    """EGS CPU 散熱片框架實測：拔模錐孔（半錐角 1.27°，Ø5.3）視為孔壁；45° 倒角錐面排除。"""
    draft = _cone_face(-82.36, -527.803, 2.65, 14.735, 19.235, 0.02225, 74.948)
    chamfer = _cone_face(-79.46, -541.103, 1.65, 14.735, 15.235, math.pi / 4, 1.833)
    cyls = S._y_cylinders(SimpleNamespace(faces=[draft, chamfer]))
    assert len(cyls) == 1
    c = cyls[0]
    assert c["concave"] and c["r"] == pytest.approx(2.65 * MM)
    assert c["angle"] == pytest.approx(FULL, rel=0.01)
    holes = S._detect_mount_holes(cyls, min_radius_m=1.25 * MM)
    assert [(round(h["cx"] / MM, 2), round(h["radius"] * 2 / MM, 1)) for h in holes] == [(-82.36, 5.3)]


# --- 螺絲鎖孔 vs 中央/內側定位銷孔篩選（角落分群：每角取最外一孔）---------------

# 散熱片 X-Z 包圍盒：四角外側螺絲孔 + 內側定位銷孔
_HS_LO = (-100.0 * MM, 0.0, -100.0 * MM)
_HS_HI = (100.0 * MM, 20.0 * MM, 100.0 * MM)


def _hole(cx, cz, radius_mm, screw_r_mm=0.0):
    return {"cx": cx * MM, "cz": cz * MM, "radius": radius_mm * MM,
            "clearance": max(radius_mm, screw_r_mm) * MM, "screw_r": screw_r_mm * MM}


def test_select_screw_holes_corner_keeps_outer_drops_inner_pin():
    """每角兩孔：外側螺絲孔（紅）+ 斜內側定位孔（藍，更靠中心）→ 僅保留四個外角孔。"""
    corners = [(-90, -90), (90, -90), (90, 90), (-90, 90)]
    holes = []
    for cx, cz in corners:
        holes.append(_hole(cx, cz, 2.5))                      # 紅：外角螺絲孔
        holes.append(_hole(cx * 0.78, cz * 0.78, 1.5))       # 藍：斜內側定位孔（更靠中心）
    picked = S._select_screw_holes(holes, _HS_LO, _HS_HI, hole_select="screw")
    assert len(picked) == 4
    # 全部為外角（|cx| 與 |cz| 皆接近 90），非內側 0.78 倍者
    assert all(abs(abs(h["cx"]) - 90 * MM) < 1e-6 for h in picked)


def test_select_screw_holes_inner_pin_has_screw_outer_still_wins():
    """關鍵情境：內側定位孔帶 screw_r，外角螺絲孔不帶 → 仍須保留外角孔，不被 screw_r 誤導。"""
    holes = [
        _hole(-90, -90, 2.5),                 # 紅：外角螺絲孔，無建模螺絲
        _hole(-70, -70, 1.5, screw_r_mm=4.5), # 藍：內側定位孔，帶同軸銷/螺絲
        _hole(90, 90, 2.5),
        _hole(70, 70, 1.5, screw_r_mm=4.5),
    ]
    picked = S._select_screw_holes(holes, _HS_LO, _HS_HI, hole_select="screw")
    assert len(picked) == 2
    assert all(abs(abs(h["cx"]) - 90 * MM) < 1e-6 for h in picked)


def test_select_screw_holes_close_pair_screw_tiebreak():
    """同角兩孔徑向相近（差 < 3mm）→ 以 screw_r 決勝取有螺絲者。"""
    holes = [
        _hole(-90, -90, 2.5),                 # 無螺絲
        _hole(-89, -89, 2.5, screw_r_mm=4.5), # 幾乎同位置但帶螺絲 → 應取此
    ]
    picked = S._select_screw_holes(holes, _HS_LO, _HS_HI, hole_select="screw")
    assert len(picked) == 1
    assert picked[0]["screw_r"] == pytest.approx(4.5 * MM)


def test_select_screw_holes_outer_mode_corner_based():
    """outer 模式：角落分群，每角取最外一孔，不理會 screw_r。"""
    holes = [
        _hole(-90, -90, 2.5),
        _hole(-60, -60, 2.5, screw_r_mm=4.5),  # 內側即使有螺絲也不取
        _hole(90, 90, 2.5),
    ]
    picked = S._select_screw_holes(holes, _HS_LO, _HS_HI, hole_select="outer")
    assert len(picked) == 2
    assert all(abs(abs(h["cx"]) - 90 * MM) < 1e-6 for h in picked)


def test_select_screw_holes_all_mode_keeps_everything():
    holes = [_hole(-90, -90, 2.5), _hole(-70, -70, 1.5), _hole(0, 0, 1.5)]
    picked = S._select_screw_holes(holes, _HS_LO, _HS_HI, hole_select="all")
    assert len(picked) == 3


def test_select_screw_holes_empty_and_single():
    assert S._select_screw_holes([], _HS_LO, _HS_HI) == []
    one = [_hole(0, 0, 2.5)]
    assert S._select_screw_holes(one, _HS_LO, _HS_HI, hole_select="outer") == one


def _fin_body():
    """兩組鰭片：全長鰭片 X[-206,-172]、短鰭片 X[-218,-160] 僅在 Z[-368.76,-353.96]，
    外緣端蓋側板延伸到 -218.2 / -159.8；另有一片螺絲側平面（應被 clearance 排除）。"""
    faces = []
    # 實測側壁位置：鰭片厚 1mm、間隙 2mm（-206/-205, -203/-202, …, -173/-172）
    for k in range(12):
        for x in (-206.0 + 3 * k, -205.0 + 3 * k):
            faces.append(_plane_face((1, 0, 0), x, x, 26.595, 49.095, -379.76, -342.96))
    for x0 in (-218.0, -215.0, -212.0, -209.0, -170.0, -167.0, -164.0, -161.0):
        for x in (x0, x0 + 1.0):
            faces.append(_plane_face((1, 0, 0), x, x, 26.595, 49.095, -368.76, -353.96))
    for z in (-368.76, -353.96):
        faces.append(_plane_face((0, 0, 1), -218.2, -216.5, 26.095, 48.095, z, z))
        faces.append(_plane_face((0, 0, 1), -161.5, -159.8, 26.095, 48.095, z, z))
    # 底板外牆：自 24.095 起（低於鰭片根部）→ 不得擴展全長群而填掉角落缺口
    faces.append(_plane_face((0, 0, 1), -217.2, -160.8, 24.095, 48.095, -379.76, -379.76))
    # 螺絲側平面（中心落在鎖孔 clearance 內）
    faces.append(_plane_face((1, 0, 0), -214.1, -213.6, 26.095, 49.0, -350.0, -346.0))
    return SimpleNamespace(faces=faces)


def test_fin_fill_rects_keeps_screw_corner_notches():
    holes = [{"cx": -212.62 * MM, "cz": -348.28 * MM, "radius": 2.5 * MM, "clearance": 4.5 * MM}]
    lo = (-218.198 * MM, 20.895 * MM, -379.762 * MM)
    hi = (-159.798 * MM, 49.095 * MM, -342.962 * MM)
    rects, axis = S._fin_fill_rects(_fin_body(), 26.095 * MM, 49.095 * MM, holes, lo, hi)
    assert axis == "Z"
    got = sorted(tuple(round(v / MM, 2) for v in r[:4]) for r in rects)
    assert got == [
        (-218.2, -159.8, -368.76, -353.96),   # 短鰭片群（端蓋擴至外緣）
        (-206.0, -172.0, -379.76, -342.96),   # 全長鰭片群
    ]


def test_fin_fill_rects_splits_banks_around_center_screw():
    """同長度鰭片分成兩排、中間夾螺絲（無更長鰭片支撐）→ 兩塊，不可把螺絲區填死。"""
    faces = []
    for x in (0.0, 1.0, 3.0, 4.0, 6.0, 7.0, 30.0, 31.0, 33.0, 34.0, 36.0, 37.0):
        faces.append(_plane_face((1, 0, 0), x, x, 2.5, 20.0, 0.0, 40.0))
    rects, _axis = S._fin_fill_rects(SimpleNamespace(faces=faces), 2.0 * MM, 20.0 * MM, [],
                                     (0, 0, 0), (37 * MM, 20 * MM, 40 * MM))
    got = sorted(tuple(round(v / MM, 2) for v in r[:2]) for r in rects)
    assert got == [(0.0, 7.0), (30.0, 37.0)]


def test_fin_fill_rects_bridges_pin_fin_rows():
    """針狀鰭片：每列為一長度群，列間 1mm 間隙需補橋接塊。"""
    faces = []
    for z0 in (0.0, 2.0, 4.0):
        for x in (0.0, 1.0, 2.0, 3.0):
            faces.append(_plane_face((1, 0, 0), x, x, 1.0, 10.0, z0, z0 + 1.0))
    rects, axis = S._fin_fill_rects(SimpleNamespace(faces=faces), 1.0 * MM, 10.0 * MM, [],
                                    (0, 0, 0), (3 * MM, 10 * MM, 5 * MM))
    covered = sorted((round(r[2] / MM, 2), round(r[3] / MM, 2)) for r in rects)
    assert covered == [(0.0, 1.0), (1.0, 2.0), (2.0, 3.0), (3.0, 4.0), (4.0, 5.0)]


def test_fin_fill_rects_falls_back_to_bbox():
    lo, hi = (0.0, 0.0, 0.0), (0.01, 0.02, 0.03)
    rects, axis = S._fin_fill_rects(SimpleNamespace(faces=[]), 0.0, 0.02, [], lo, hi)
    assert axis == "none"
    assert rects == [(0.0, 0.01, 0.0, 0.03, 0.02)]
