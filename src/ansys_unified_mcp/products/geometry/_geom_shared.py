"""Geometry 共用 helper（由 call_dispatch.py 結構性拆分而來，函式本體逐字搬移）。

本檔只收納純函式與對 session 全域的延遲存取 helper；對 call_dispatch 的依賴
（_geom_get_design / _geom_suppress_hide）一律於函式內以 `from . import
call_dispatch as _cd` 延遲取得，避免模組載入期的循環 import。
"""

import logging
import math
from typing import Any, Mapping

logger = logging.getLogger("ansys-mcp")

__all__ = [
    "_find_bodies_by_name",
    "_bbox_m",
    "_make_box_from_bbox",
    "_bottom_face_by_y",
    "_mm",
    "_source_body_name",
    "_SIMPLIFIED_PROTECT",
    "_suppress_hide_sources",
    "_safe_delete",
    "_normalize_bbox_bounds",
    "compute_bbox_iou",
    "compute_com_distance",
    "compute_continuous_geometry_metrics",
]


def _find_bodies_by_name(name: str):
    """回傳當前設計中（遞迴）所有名稱完全相符的 body。"""
    from . import call_dispatch as _cd
    d = _cd._geom_get_design()
    try:
        bodies = d.get_all_bodies()
    except Exception:
        bodies = d.bodies
    return [b for b in bodies if b.name == name]


def _bbox_m(body):
    """回傳 body 軸對齊包圍盒的 (min_xyz, max_xyz)，單位【公尺 m】。

    已正規化成 lo <= hi（逐分量），避免後端回傳順序不定造成負尺寸。
    """
    from ansys.geometry.core.misc import UNITS

    bb = body.bounding_box
    mn, mx = bb.min_corner, bb.max_corner
    lo = (mn.x.m_as(UNITS.m), mn.y.m_as(UNITS.m), mn.z.m_as(UNITS.m))
    hi = (mx.x.m_as(UNITS.m), mx.y.m_as(UNITS.m), mx.z.m_as(UNITS.m))
    lo2 = tuple(min(a, b) for a, b in zip(lo, hi))
    hi2 = tuple(max(a, b) for a, b in zip(lo, hi))
    return lo2, hi2


def _make_box_from_bbox(design, name, lo, hi, target=None):
    """以軸對齊包圍盒 [lo, hi]（公尺）建立實心方塊並回傳 Body。

    於 z = lo_z 平面草繪 X-Y footprint，再沿 +Z 拉伸盒高。
    （延續 spaceclaim_mcp.py 的建盒策略；此處所有座標皆為公尺。）
    target 不為 None 時將方塊建於該 component（否則建於 design 根）。
    """
    from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D
    from ansys.geometry.core.misc import UNITS, Distance
    from ansys.geometry.core.sketch import Sketch

    cx = (lo[0] + hi[0]) / 2.0
    cy = (lo[1] + hi[1]) / 2.0
    width = hi[0] - lo[0]   # X span
    height = hi[1] - lo[1]  # Y span
    depth = hi[2] - lo[2]   # Z span

    plane = Plane(
        origin=Point3D([0, 0, lo[2]], UNITS.m),
        direction_x=UnitVector3D([1, 0, 0]),
        direction_y=UnitVector3D([0, 1, 0]),
    )
    sketch = Sketch(plane).box(
        Point2D([cx, cy], UNITS.m),
        width=Distance(width, UNITS.m),
        height=Distance(height, UNITS.m),
    )
    owner = target if target is not None else design
    return owner.extrude_sketch(name, sketch, Distance(depth, UNITS.m))


def _bottom_face_by_y(body):
    """回傳 body 的底面（朝 -Y / Y 最低者），用於建立接合面 named selection。

    乾淨方塊的 Face.bounding_box 可能不可用，故改以 Face.point(0.5,0.5) 取樣
    最低 Y；同高時優先選法向朝下 (0,-1,0) 者。
    """
    from ansys.geometry.core.misc import UNITS

    best = None
    best_y = None
    for f in body.faces:
        try:
            p = f.point(0.5, 0.5)
            y = p.y.m_as(UNITS.m)
        except Exception:
            continue
        downward = False
        try:
            n = f.normal(0.5, 0.5)
            downward = float(n.y) < -0.9
        except Exception:
            pass
        if best_y is None or y < best_y - 1e-9 or (abs(y - best_y) <= 1e-9 and downward):
            best_y = y
            best = f
    return best


def _mm(v):
    """公尺轉毫米並四捨五入到 4 位，供人類可讀報告使用。"""
    return round(v * 1000.0, 4)


def _source_body_name(body):
    """取得原始 body 名稱（供後續走伺服器端腳本精確 suppress/hide 之用）。

    PyAnsys Geometry Python 端的 body.set_suppressed(True) 在實務上會靜默失效
    （尤其 add_component 之後 body 物件失聯），且無可靠的視覺隱藏 API。因此此處
    僅回傳名稱，真正的 suppress-for-physics + 隱藏改由 _suppress_hide_sources()
    透過已驗證的 SpaceClaim 伺服器端腳本（_geom_suppress_hide）完成。
    """
    try:
        if body is not None and getattr(body, "is_alive", True):
            nm = getattr(body, "name", None)
            if nm:
                return str(nm)
    except Exception as e:
        logger.warning(f"取得原始 body 名稱失敗: {e}")
    return None


_SIMPLIFIED_PROTECT = ["*_simplified_*", "*_rho*", "RAM_simplified*"]


def _suppress_hide_sources(names, extra_exclude=None):
    """簡化完成後，對原始 body 以其名稱樣式執行 suppress-for-physics + 隱藏。

    走已驗證可靠的 SpaceClaim 伺服器端腳本（_geom_suppress_hide），取代先前
    靜默失效的 PyAnsys 端 body.set_suppressed(True)。

    names: 原始 body 名稱清單（可重複，會自動去重並當作 glob 樣式）。
    回傳 (ok: bool, detail: str)；names 為空時回傳 (False, "")。
    """
    pats = sorted({str(n) for n in (names or []) if n})
    if not pats:
        return False, ""
    exclude = list(_SIMPLIFIED_PROTECT) + list(extra_exclude or [])
    from . import call_dispatch as _cd
    detail = _cd._geom_suppress_hide(pats, exclude=exclude, suppress=True, hide=True)
    ok = detail.startswith("✓")
    return ok, detail


def _safe_delete(body):
    """刪除 body（已不存在則略過），回傳是否成功。"""
    try:
        if body is not None and body.is_alive:
            body.parent_component.delete_body(body)
            return True
    except Exception as e:
        logger.warning(f"刪除暫存 body 失敗: {e}")
    return False


# ===================================================================
# CONTINUOUS GEOMETRY METRICS (CADWorld Staged Diagnostics)
# ===================================================================

def _normalize_bbox_bounds(
    bbox: Any,
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """將各類包圍盒結構正規化為 (lo, hi)，且保證逐軸 lo <= hi。

    支援輸入：
      - ((x0, y0, z0), (x1, y1, z1))
      - [ [x0, y0, z0], [x1, y1, z1] ]
      - {'xmin': ..., 'ymin': ..., 'zmin': ..., 'xmax': ..., 'ymax': ..., 'zmax': ...}
      - {'min': [..], 'max': [..]}
      - {'x': dx, 'y': dy, 'z': dz}
    """
    if bbox is None:
        return ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))

    if isinstance(bbox, (list, tuple)) and len(bbox) >= 2:
        p0, p1 = bbox[0], bbox[1]
        if isinstance(p0, (list, tuple)) and isinstance(p1, (list, tuple)):
            lo = (float(p0[0]), float(p0[1]), float(p0[2]))
            hi = (float(p1[0]), float(p1[1]), float(p1[2]))
            lo_norm = tuple(min(a, b) for a, b in zip(lo, hi))
            hi_norm = tuple(max(a, b) for a, b in zip(lo, hi))
            return lo_norm, hi_norm

    if isinstance(bbox, Mapping):
        if all(k in bbox for k in ("xmin", "ymin", "zmin", "xmax", "ymax", "zmax")):
            lo = (float(bbox["xmin"]), float(bbox["ymin"]), float(bbox["zmin"]))
            hi = (float(bbox["xmax"]), float(bbox["ymax"]), float(bbox["zmax"]))
            lo_norm = tuple(min(a, b) for a, b in zip(lo, hi))
            hi_norm = tuple(max(a, b) for a, b in zip(lo, hi))
            return lo_norm, hi_norm
        if "min" in bbox and "max" in bbox:
            p0, p1 = bbox["min"], bbox["max"]
            lo = (float(p0[0]), float(p0[1]), float(p0[2]))
            hi = (float(p1[0]), float(p1[1]), float(p1[2]))
            lo_norm = tuple(min(a, b) for a, b in zip(lo, hi))
            hi_norm = tuple(max(a, b) for a, b in zip(lo, hi))
            return lo_norm, hi_norm
        if all(k in bbox for k in ("x", "y", "z")):
            dx = max(0.0, float(bbox["x"]))
            dy = max(0.0, float(bbox["y"]))
            dz = max(0.0, float(bbox["z"]))
            return ((0.0, 0.0, 0.0), (dx, dy, dz))

    return ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))


def compute_bbox_iou(
    bbox_a: Any,
    bbox_b: Any,
) -> float:
    """計算兩個 3D 軸對齊包圍盒之體積交並比 (3D Volumetric IoU, 0.0 ~ 1.0)。

    包含四層數學防禦：
      1. 座標自動正規化 (lo <= hi)；
      2. 逐軸交集非負截斷 max(0.0, ...) 防止雙負軸相乘產生偽交集；
      3. 退化盒除零防護 (兩退化盒完全重合回傳 1.0，否則 vol_union <= 1e-12 回傳 0.0)；
      4. 數值裁切至閉區間 [0.0, 1.0]。
    """
    (ax0, ay0, az0), (ax1, ay1, az1) = _normalize_bbox_bounds(bbox_a)
    (bx0, by0, bz0), (bx1, by1, bz1) = _normalize_bbox_bounds(bbox_b)

    vol_a = max(0.0, ax1 - ax0) * max(0.0, ay1 - ay0) * max(0.0, az1 - az0)
    vol_b = max(0.0, bx1 - bx0) * max(0.0, by1 - by0) * max(0.0, bz1 - bz0)

    # 逐軸交集跨度（嚴格非負截斷）
    dx = max(0.0, min(ax1, bx1) - max(ax0, bx0))
    dy = max(0.0, min(ay1, by1) - max(ay0, by0))
    dz = max(0.0, min(az1, bz1) - max(az0, bz0))
    vol_inter = dx * dy * dz

    vol_union = vol_a + vol_b - vol_inter
    if vol_union <= 1e-12:
        # 退化盒防護：若兩盒完全重疊（點或平面位置相同）則視為 1.0，否則 0.0
        if (
            math.isclose(ax0, bx0, abs_tol=1e-7)
            and math.isclose(ay0, by0, abs_tol=1e-7)
            and math.isclose(az0, bz0, abs_tol=1e-7)
            and math.isclose(ax1, bx1, abs_tol=1e-7)
            and math.isclose(ay1, by1, abs_tol=1e-7)
            and math.isclose(az1, bz1, abs_tol=1e-7)
        ):
            return 1.0
        return 0.0

    iou = vol_inter / vol_union
    return float(max(0.0, min(1.0, iou)))


def compute_com_distance(
    com_a: Any,
    com_b: Any,
) -> float:
    """計算兩個 3D 質心座標之歐氏距離。"""
    def _extract_pt(p: Any) -> tuple[float, float, float]:
        if isinstance(p, Mapping):
            return (float(p.get("x", 0.0)), float(p.get("y", 0.0)), float(p.get("z", 0.0)))
        if isinstance(p, (list, tuple)) and len(p) >= 3:
            return (float(p[0]), float(p[1]), float(p[2]))
        return (0.0, 0.0, 0.0)

    p1 = _extract_pt(com_a)
    p2 = _extract_pt(com_b)
    return float(math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2))))


def compute_continuous_geometry_metrics(
    actual: Mapping[str, Any],
    expected: Mapping[str, Any],
    similar_volume_rel_tol: float = 0.10,
    similar_area_rel_tol: float = 0.10,
    similar_bbox_iou_min: float = 0.70,
) -> dict[str, Any]:
    """對齊 CADWorld diagnostics.py 之連續幾何指標計算。

    比對實際幾何與預期幾何的：體積、表面積、BBox 軸向跨度誤差、BBox IoU、質心距離，
    並綜合給出 loose 的 similar 判定（用於區分 F6 DISSIMILAR 與 F7 SIMILAR_OUT_OF_TOLERANCE）。
    """
    out: dict[str, Any] = {}

    # 1. 體積相對誤差
    act_vol = actual.get("total_volume", actual.get("volume"))
    exp_vol = expected.get("total_volume", expected.get("volume"))
    if act_vol is not None and exp_vol is not None:
        try:
            av, ev = float(act_vol), float(exp_vol)
            rel_err = abs(av - ev) / abs(ev) if abs(ev) > 1e-12 else 0.0
            out["volume"] = {
                "actual": av,
                "expected": ev,
                "ratio": round(av / ev, 6) if abs(ev) > 1e-12 else None,
                "relative_error": round(rel_err, 6),
            }
        except (ValueError, TypeError):
            pass

    # 2. 表面積相對誤差
    act_area = actual.get("total_area", actual.get("surface_area"))
    exp_area = expected.get("total_area", expected.get("surface_area"))
    if act_area is not None and exp_area is not None:
        try:
            aa, ea = float(act_area), float(exp_area)
            rel_err = abs(aa - ea) / abs(ea) if abs(ea) > 1e-12 else 0.0
            out["surface_area"] = {
                "actual": aa,
                "expected": ea,
                "ratio": round(aa / ea, 6) if abs(ea) > 1e-12 else None,
                "relative_error": round(rel_err, 6),
            }
        except (ValueError, TypeError):
            pass

    # 3. BBox 跨度與 IoU
    act_bbox = actual.get("bbox")
    exp_bbox = expected.get("bbox")
    if act_bbox is not None and exp_bbox is not None:
        out["bbox_iou"] = round(compute_bbox_iou(act_bbox, exp_bbox), 6)
        (ax0, ay0, az0), (ax1, ay1, az1) = _normalize_bbox_bounds(act_bbox)
        (ex0, ey0, ez0), (ex1, ey1, ez1) = _normalize_bbox_bounds(exp_bbox)
        out["bbox_extent_error"] = {
            "x": round((ax1 - ax0) - (ex1 - ex0), 6),
            "y": round((ay1 - ay0) - (ey1 - ey0), 6),
            "z": round((az1 - az0) - (ez1 - ez0), 6),
        }

    # 4. 質心偏移
    act_com = actual.get("center_of_mass", actual.get("com"))
    exp_com = expected.get("center_of_mass", expected.get("com"))
    if act_com is not None and exp_com is not None:
        out["center_of_mass_distance"] = round(compute_com_distance(act_com, exp_com), 6)

    # 5. similar 判定
    signals = []
    if "volume" in out:
        signals.append(out["volume"]["relative_error"] <= similar_volume_rel_tol)
    if "surface_area" in out:
        signals.append(out["surface_area"]["relative_error"] <= similar_area_rel_tol)
    if "bbox_iou" in out:
        signals.append(out["bbox_iou"] >= similar_bbox_iou_min)

    out["similar"] = all(signals) if signals else None
    return out
