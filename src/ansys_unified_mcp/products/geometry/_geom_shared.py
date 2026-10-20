"""Geometry 共用 helper（由 call_dispatch.py 結構性拆分而來，函式本體逐字搬移）。

本檔只收納純函式與對 session 全域的延遲存取 helper；對 call_dispatch 的依賴
（_geom_get_design / _geom_suppress_hide）一律於函式內以 `from . import
call_dispatch as _cd` 延遲取得，避免模組載入期的循環 import。
"""

import logging

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


