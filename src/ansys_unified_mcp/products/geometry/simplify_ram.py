"""RAM + socket 幾何簡化（由 call_dispatch.py 拆分，函式本體逐字搬移）。"""

import logging

from ._geom_shared import (
    _find_bodies_by_name,
    _bbox_m,
    _make_box_from_bbox,
    _bottom_face_by_y,
    _mm,
    _source_body_name,
    _suppress_hide_sources,
    _safe_delete,
)

logger = logging.getLogger("ansys-mcp")

__all__ = [
    "_build_ram_block",
    "_geom_simplify_ram",
    "_pair_by_x",
    "_geom_simplify_ram_batch",
]


def _build_ram_block(design, ram_body, socket_body, mb_top_y, result_name, ns_name, target=None):
    """建立單一 RAM+socket 簡化為「凸字形」兩段體（座落於板面），並建立底面 named selection。

    凸字形（高度軸 Y，剖面上寬下窄的相反——下寬上窄）：
      - 下段（寬基座）：socket 的 X-Z footprint，Y 從主機板頂面 (mb_top_y) → socket 頂 (socket max Y)。
      - 上段（窄凸柱）：RAM 的 X-Z footprint，Y 從 socket 頂 → RAM 頂 (RAM max Y)。
      - 兩段聯集成單一 body；底面（基座底）建立 named selection。
    若 socket 頂未落在基座底與 RAM 頂之間（退化情形），退回單一合併包圍盒方塊。
    target 不為 None 時方塊建於該 component。
    """
    ram_lo, ram_hi = _bbox_m(ram_body)
    sock_lo, sock_hi = _bbox_m(socket_body)

    y_bottom = mb_top_y        # 主機板頂面或 socket 底面（基座底）
    y_mid = sock_hi[1]         # socket 頂（基座/凸柱交界）
    y_top = ram_hi[1]          # RAM 頂（凸柱頂）
    if y_top <= y_bottom:
        raise ValueError(
            f"RAM 頂 (Y={y_top*1000:.3f}mm) 未高於基準面 (Y={y_bottom*1000:.3f}mm)；"
            "請確認零件名稱 / 方向（高度軸應為 Y）。"
        )

    # 下段（基座）＝ socket footprint；上段（凸柱）＝ RAM footprint
    base_lo = (sock_lo[0], y_bottom, sock_lo[2])
    base_hi = (sock_hi[0], y_mid, sock_hi[2])
    top_lo = (ram_lo[0], y_mid, ram_lo[2])
    top_hi = (ram_hi[0], y_top, ram_hi[2])

    _EPS = 1e-6  # 1µm：段高容差

    convex = y_bottom + _EPS < y_mid < y_top - _EPS
    if convex:
        # 兩段凸字形：各自建塊再聯集
        base = _make_box_from_bbox(design, result_name, base_lo, base_hi, target=target)
        top = _make_box_from_bbox(design, f"{result_name}_tmp_top", top_lo, top_hi, target=target)
        try:
            base.unite([top], keep_other=False)
            block = base
        except Exception as e:
            logger.warning(f"凸字形聯集失敗，退回合併包圍盒方塊: {e}")
            _safe_delete(top)
            _safe_delete(base)
            convex = False

    if not convex:
        # 退化情形：socket 頂不在有效區間內，退回單一合併包圍盒方塊
        x_min = min(ram_lo[0], sock_lo[0])
        x_max = max(ram_hi[0], sock_hi[0])
        z_min = min(ram_lo[2], sock_lo[2])
        z_max = max(ram_hi[2], sock_hi[2])
        base_lo = (x_min, y_bottom, z_min)
        base_hi = (x_max, y_top, z_max)
        top_lo = top_hi = None
        block = _make_box_from_bbox(design, result_name, base_lo, base_hi, target=target)

    bottom = _bottom_face_by_y(block)
    ns_created = False
    if bottom is not None:
        try:
            design.create_named_selection(ns_name, faces=[bottom])
            ns_created = True
        except Exception as e:
            logger.warning(f"建立 named selection '{ns_name}' 失敗: {e}")

    overall_lo = base_lo
    overall_hi = (base_hi if not convex else top_hi)
    return {
        "result_body": result_name,
        "result_body_obj": block,
        "shape": "convex" if convex else "box",
        "base_size_mm": [_mm(base_hi[i] - base_lo[i]) for i in range(3)],
        "top_size_mm": ([_mm(top_hi[i] - top_lo[i]) for i in range(3)] if convex else None),
        "block_min_mm": [_mm(v) for v in overall_lo],
        "block_max_mm": [_mm(v) for v in overall_hi],
        "block_size_mm": [_mm(overall_hi[i] - overall_lo[i]) for i in range(3)],
        "named_selection": ns_name if ns_created else None,
        "named_selection_created": ns_created,
    }

def _geom_simplify_ram(ram: str, socket: str, motherboard: str = "",
                       result_name: str = "RAM_simplified",
                       named_selection: str = "ram_bottom",
                       move_to_component: bool = True,
                       component_name: str = "RAM_simplified",
                       hide_source: bool = True) -> str:
    """將單一 RAM 卡 + 其 socket 簡化為一座落於主機板（或 socket 底面）上的方塊。"""
    from . import call_dispatch as _cd
    design = _cd._geom_get_design()

    def _first(nm):
        matches = _find_bodies_by_name(nm)
        if not matches:
            raise ValueError(f"找不到名為 '{nm}' 的 body（請先 geometry_list_bodies 確認名稱）。")
        return matches[0]

    ram_b = _first(ram)
    sock_b = _first(socket)
    sock_lo, sock_hi = _bbox_m(sock_b)

    if motherboard:
        mb_top_y = _bbox_m(_first(motherboard))[1][1]  # 主機板 max Y
        mb_desc = f"座落於 '{motherboard}' 頂面"
    else:
        mb_top_y = sock_lo[1]  # 以 socket 自身底面 (min Y) 為基準
        mb_desc = f"座落於 '{socket}' 底面（無主機板模式）"

    target = design.add_component(component_name) if move_to_component else None
    info = _build_ram_block(design, ram_b, sock_b, mb_top_y, result_name, named_selection, target=target)

    hidden = 0
    hide_detail = ""
    if hide_source:
        src_names = [n for n in (_source_body_name(ram_b), _source_body_name(sock_b)) if n]
        ok, hide_detail = _suppress_hide_sources(src_names)
        if ok:
            hidden = len(src_names)

    comp_note = f"（已移入新 component '{component_name}'）" if move_to_component else ""
    hide_note = f"，已抑制+隱藏 {hidden} 個原始實體" if hide_source else ""
    shape_note = "凸字形（socket 寬基座 + RAM 窄凸柱）" if info.get("shape") == "convex" else "單一方塊（退化）"
    tier_line = (
        f"  下段基座 (mm): {info['base_size_mm']}  上段凸柱 (mm): {info['top_size_mm']}\n"
        if info.get("shape") == "convex" else ""
    )
    warn_line = ""
    if hide_source and hidden == 0 and hide_detail:
        warn_line = f"\n  ⚠ 原始實體抑制/隱藏未生效:\n{hide_detail}"

    if motherboard:
        mb_info_line = f"  主機板頂面 Y={_mm(mb_top_y)}mm，RAM 頂 Y={info['block_max_mm'][1]}mm\n"
    else:
        mb_info_line = f"  Socket 底面 Y={_mm(mb_top_y)}mm，RAM 頂 Y={info['block_max_mm'][1]}mm\n"

    return (
        f"✓ RAM 簡化完成：'{result_name}' {mb_desc}，形狀={shape_note}{comp_note}{hide_note}。\n"
        f"  合併來源: {ram} + {socket}\n"
        f"  整體尺寸 (mm): {info['block_size_mm']}  min={info['block_min_mm']} max={info['block_max_mm']}\n"
        f"{tier_line}"
        f"{mb_info_line}"
        f"  底面 named selection: {info['named_selection']} (created={info['named_selection_created']})"
        f"{warn_line}"
    )

def _pair_by_x(rams, sockets, tol_m=0.002):
    """以 X 中心就近配對每個 RAM 與 socket；回傳依 X 排序的 (x_center, ram, socket)。

    tol_m 單位為【公尺】（預設 2mm）。超出容差未配對者略過。
    """
    from ansys.geometry.core.misc import UNITS

    def cx(body):
        bb = body.bounding_box
        return (bb.min_corner.x.m_as(UNITS.m) + bb.max_corner.x.m_as(UNITS.m)) / 2.0

    sock_list = [(cx(s), s) for s in sockets]
    used = [False] * len(sock_list)
    pairs = []
    for r in rams:
        rx = cx(r)
        best_i, best_d = None, None
        for i, (sx, _s) in enumerate(sock_list):
            if used[i]:
                continue
            dd = abs(sx - rx)
            if best_d is None or dd < best_d:
                best_d, best_i = dd, i
        if best_i is not None and best_d is not None and best_d <= tol_m:
            used[best_i] = True
            pairs.append((rx, r, sock_list[best_i][1]))
    pairs.sort(key=lambda t: t[0])
    return pairs

def _geom_simplify_ram_batch(ram: str, socket: str, motherboard: str = "",
                             result_prefix: str = "RAM_simplified",
                             ns_prefix: str = "ram_bottom",
                             tol_mm: float = 2.0,
                             move_to_component: bool = True,
                             component_name: str = "RAM_simplified",
                             hide_source: bool = True) -> str:
    """批次簡化所有同名 RAM+socket 配對（依 X 位置自動配對），各自成塊並建底面 NS。

    move_to_component=True 時所有簡化方塊建於同一新 component；
    hide_source=True 時配對成功的原始 RAM 與 socket body 會被抑制 (suppress)，於下游排除。
    """
    from . import call_dispatch as _cd
    design = _cd._geom_get_design()

    mb_top_y = None
    if motherboard:
        mb_matches = _find_bodies_by_name(motherboard)
        if not mb_matches:
            raise ValueError(f"找不到名為 '{motherboard}' 的主機板 body。")
        mb_top_y = _bbox_m(mb_matches[0])[1][1]

    rams = _find_bodies_by_name(ram)
    sockets = _find_bodies_by_name(socket)
    if not rams:
        raise ValueError(f"找不到名為 '{ram}' 的 RAM body。")
    if not sockets:
        raise ValueError(f"找不到名為 '{socket}' 的 socket body。")

    pairs = _pair_by_x(rams, sockets, tol_m=tol_mm / 1000.0)

    target = design.add_component(component_name) if move_to_component else None

    results, errors = [], []
    src_names = []
    for idx, (_x, ram_b, sock_b) in enumerate(pairs, start=1):
        rn = f"{result_prefix}_{idx:02d}"
        ns = f"{ns_prefix}_{idx:02d}"
        try:
            sock_lo, _ = _bbox_m(sock_b)
            base_y = mb_top_y if mb_top_y is not None else sock_lo[1]
            results.append(_build_ram_block(design, ram_b, sock_b, base_y, rn, ns, target=target))
            if hide_source:
                for b in (ram_b, sock_b):
                    nm = _source_body_name(b)
                    if nm:
                        src_names.append(nm)
        except Exception as e:
            errors.append({"index": idx, "result_body": rn, "error": str(e)})

    hidden = 0
    hide_detail = ""
    if hide_source and src_names:
        ok, hide_detail = _suppress_hide_sources(src_names)
        if ok:
            hidden = len(src_names)

    ns_count = sum(1 for r in results if r["named_selection_created"])
    comp_note = f"，簡化方塊置於新 component '{component_name}'" if move_to_component else ""
    mb_desc = f"主機板 '{motherboard}' 頂面 Y={_mm(mb_top_y)}mm" if motherboard else "無主機板模式（以各 socket 底面為基準）"
    lines = [
        f"✓ RAM 批次簡化完成（{mb_desc}{comp_note}）",
        f"  RAM 數={len(rams)}, socket 數={len(sockets)}, 配對={len(pairs)}, "
        f"建塊={len(results)}, 建立 NS={ns_count}"
        + (f", 抑制+隱藏原始實體={hidden}" if hide_source else ""),
    ]
    for r in results:
        lines.append(f"  - {r['result_body']}: shape={r.get('shape', 'box')} size(mm)={r['block_size_mm']} NS={r['named_selection']}")
    if hide_source and hide_detail and hidden == 0:
        lines.append(f"  ⚠ 原始實體抑制/隱藏未生效:\n{hide_detail}")
    if errors:
        lines.append(f"  ⚠ {len(errors)} 個配對失敗:")
        for e in errors:
            lines.append(f"    - {e['result_body']}: {e['error']}")
    return "\n".join(lines)

