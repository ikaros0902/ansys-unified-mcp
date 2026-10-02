# -*- coding: utf-8 -*-
import os
from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.drivers import sim_impl
from typing import Any, List, Dict
import functools

def tool_geometry(name=None):
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            try:
                res = await fn(*args, **kwargs)
                return _envelope(res)
            except Exception as exc:
                return _envelope({"ok": False, "error": str(exc)})
        return mcp.tool(name=name)(wrapper) if name else mcp.tool()(wrapper)
    return decorator

@tool_geometry(name='geometry_launch')
async def geometry_launch(port: int = None, host: str = "127.0.0.1", transport_mode: str = "insecure", connect_timeout: int = 30) -> dict:
    """啟動 Geometry 建模器或連線現有 SpaceClaim 實例

    :param port: 連線已啟動 SpaceClaim 的 gRPC 埠號，不填則啟動新實例（啟動前會自動掃描 50051-50055 尋找已運行實例）
    :param host: SpaceClaim 主機地址（預設 127.0.0.1）
    :param transport_mode: gRPC 傳輸模式（預設 insecure）
    :param connect_timeout: 連線超時秒數，預設30秒
    """
    args = {}
    if port is not None:
        args['port'] = port
    if host is not None:
        args['host'] = host
    if transport_mode is not None:
        args['transport_mode'] = transport_mode
    if connect_timeout is not None:
        args['connect_timeout'] = connect_timeout
    res = await sim_impl.call_tool('geometry_launch', args)
    return "\n".join([c.text for c in res])


@tool_geometry(name='geometry_create_design')
async def geometry_create_design(name: str) -> dict:
    """建立新的幾何設計（⚠️ 注意：若 SpaceClaim 中已有開啟的設計，請勿調用此工具，直接調用 create_block 等即可在當前設計中建模）
    :param name: 設計名稱
    """
    args = {}
    if name is not None:
        args['name'] = name
    res = await sim_impl.call_tool('geometry_create_design', args)
    return "\n".join([c.text for c in res])

@tool_geometry(name='geometry_create_block')
async def geometry_create_block(name: str, length: float = 0.01, width: float = 0.01, height: float = 0.01, center_x: float = 0, center_y: float = 0, center_z: float = 0) -> dict:
    """建立立方體（⚠️ 注意：所有尺寸單位皆為【公尺 m】！若使用者輸入 mm，請務必先除以 1000 轉換為公尺，例如 50mm 必須傳入 0.05，30mm 傳入 0.03，20mm 傳入 0.02）
    :param name: 方塊名稱（例如 Block1）
    :param length: 長度（單位：公尺 m。例：50mm 請傳入 0.05）
    :param width: 寬度（單位：公尺 m。例：30mm 請傳入 0.03）
    :param height: 高度（單位：公尺 m。例：20mm 請傳入 0.02）
    :param center_x: 中心 X 座標（單位：公尺 m）
    :param center_y: 中心 Y 座標（單位：公尺 m）
    :param center_z: 中心 Z 座標（單位：公尺 m）
    """
    args = {}
    if name is not None:
        args['name'] = name
    if length is not None:
        args['length'] = length
    if width is not None:
        args['width'] = width
    if height is not None:
        args['height'] = height
    if center_x is not None:
        args['center_x'] = center_x
    if center_y is not None:
        args['center_y'] = center_y
    if center_z is not None:
        args['center_z'] = center_z
    res = await sim_impl.call_tool('geometry_create_block', args)
    return "\n".join([c.text for c in res])

@tool_geometry(name='geometry_create_cylinder')
async def geometry_create_cylinder(name: str, radius: float = 0.005, height: float = 0.01, center_x: float = 0, center_y: float = 0, center_z: float = 0) -> dict:
    """建立圓柱體（⚠️ 注意：所有尺寸單位皆為【公尺 m】！例：半徑 5mm 傳入 0.005，高度 20mm 傳入 0.02）
    :param name: 圓柱體名稱
    :param radius: 半徑（單位：公尺 m。例：5mm 請傳入 0.005）
    :param height: 高度（單位：公尺 m。例：20mm 請傳入 0.02）
    :param center_x: 中心 X 座標（單位：公尺 m）
    :param center_y: 中心 Y 座標（單位：公尺 m）
    :param center_z: 中心 Z 座標（單位：公尺 m）
    """
    args = {}
    if name is not None:
        args['name'] = name
    if radius is not None:
        args['radius'] = radius
    if height is not None:
        args['height'] = height
    if center_x is not None:
        args['center_x'] = center_x
    if center_y is not None:
        args['center_y'] = center_y
    if center_z is not None:
        args['center_z'] = center_z
    res = await sim_impl.call_tool('geometry_create_cylinder', args)
    return "\n".join([c.text for c in res])

@tool_geometry(name='geometry_create_sphere')
async def geometry_create_sphere(name: str, radius: float = 0.005, center_x: float = 0, center_y: float = 0, center_z: float = 0) -> dict:
    """建立球體（⚠️ 注意：尺寸單位皆為【公尺 m】！例：半徑 10mm 請輸入 0.01）
    :param name: 球體名稱
    :param radius: 半徑（單位：公尺 m。例：5mm 請傳入 0.005）
    :param center_x: 中心 X 座標（單位：公尺 m）
    :param center_y: 中心 Y 座標（單位：公尺 m）
    :param center_z: 中心 Z 座標（單位：公尺 m）
    """
    args = {}
    if name is not None:
        args['name'] = name
    if radius is not None:
        args['radius'] = radius
    if center_x is not None:
        args['center_x'] = center_x
    if center_y is not None:
        args['center_y'] = center_y
    if center_z is not None:
        args['center_z'] = center_z
    res = await sim_impl.call_tool('geometry_create_sphere', args)
    return "\n".join([c.text for c in res])

@tool_geometry(name='geometry_sketch_and_extrude')
async def geometry_sketch_and_extrude(name: str, points: list[list[float]], plane: str = 'XY', curve_type: str = 'spline', distance: float = 0.01, is_closed: bool = True, extrude_direction: str = '+') -> dict:
    """於指定基準面繪製 2D 點陣列草圖並拉伸成 3D 實體（⚠️ 注意：所有座標與尺寸單位皆為【公尺 m】！若輸入為 mm 請除以 1000）
    :param name: 生成實體之名稱
    :param points: 2D 點陣列座標清單，格式為 [[x1, y1], [x2, y2], ...]（單位：公尺 m）
    :param plane: 草圖繪製之基準面 ('XY', 'XZ', 'YZ')
    :param curve_type: 曲線連線類型 ('spline' 或 'polyline')
    :param distance: 沿法向拉伸之距離/厚度（單位：公尺 m）
    :param is_closed: 是否將最後一點連回第一點以形成封閉實體輪廓
    :param extrude_direction: 沿基準面法向量的拉伸方向 ('+' 或 '-')
    """
    args = {}
    if name is not None:
        args['name'] = name
    if points is not None:
        args['points'] = points
    if plane is not None:
        args['plane'] = plane
    if curve_type is not None:
        args['curve_type'] = curve_type
    if distance is not None:
        args['distance'] = distance
    if is_closed is not None:
        args['is_closed'] = is_closed
    if extrude_direction is not None:
        args['extrude_direction'] = extrude_direction
    res = await sim_impl.call_tool('geometry_sketch_and_extrude', args)
    return "\n".join([c.text for c in res])

@tool_geometry(name='geometry_create_enclosure')
async def geometry_create_enclosure(target_body_name: str, enclosure_name: str = 'FluidDomain', shape: str = 'box', cushion_x_neg: float = 0.05, cushion_x_pos: float = 0.1, cushion_y_neg: float = 0.05, cushion_y_pos: float = 0.05, cushion_z_neg: float = 0.05, cushion_z_pos: float = 0.05, keep_target_body: bool = False) -> dict:
    """為指定標的實體幾何自動生成外部流體包覆域 (Enclosure) 並執行布林相減扣除標的本體
    :param target_body_name: 標的固體幾何名稱
    :param enclosure_name: 生成的流體包覆域名稱
    :param shape: 流體外流域幾何形狀 ('box' 或 'cylinder')
    :param cushion_x_neg: -X 方向外擴延伸距離（公尺 m）
    :param cushion_x_pos: +X 方向外擴延伸距離（公尺 m）
    :param cushion_y_neg: -Y 方向外擴延伸距離（公尺 m）
    :param cushion_y_pos: +Y 方向外擴延伸距離（公尺 m）
    :param cushion_z_neg: -Z 方向外擴延伸距離（公尺 m）
    :param cushion_z_pos: +Z 方向外擴延伸距離（公尺 m）
    :param keep_target_body: 布林相減後是否保留標的本體
    """
    args = {}
    if target_body_name is not None:
        args['target_body_name'] = target_body_name
    if enclosure_name is not None:
        args['enclosure_name'] = enclosure_name
    if shape is not None:
        args['shape'] = shape
    if cushion_x_neg is not None:
        args['cushion_x_neg'] = cushion_x_neg
    if cushion_x_pos is not None:
        args['cushion_x_pos'] = cushion_x_pos
    if cushion_y_neg is not None:
        args['cushion_y_neg'] = cushion_y_neg
    if cushion_y_pos is not None:
        args['cushion_y_pos'] = cushion_y_pos
    if cushion_z_neg is not None:
        args['cushion_z_neg'] = cushion_z_neg
    if cushion_z_pos is not None:
        args['cushion_z_pos'] = cushion_z_pos
    if keep_target_body is not None:
        args['keep_target_body'] = keep_target_body
    res = await sim_impl.call_tool('geometry_create_enclosure', args)
    return "\n".join([c.text for c in res])

@tool_geometry(name='geometry_simplify_ram')
async def geometry_simplify_ram(motherboard: str, ram: str, socket: str, result_name: str = 'RAM_simplified', named_selection: str = 'mb_bonded') -> dict:
    """將單一 RAM 卡 + 其 socket 簡化為一座落於主機板頂面的方塊，並於方塊底面（板接合面）建立 named selection【呼叫前必須先向使用者索取主機板、RAM、socket 三個 body 名稱，不可猜測或自行從 body 清單推斷】

    規則（高度軸為 Y）：footprint(X-Z)=RAM 與 socket 的合併包圍盒；方塊底=主機板頂面（板 max Y），方塊頂=RAM 頂（RAM max Y）。原始 body 保留不動，僅新增一個方塊 body。單位內算為公尺、回報為毫米。
    :param motherboard: 主機板 body 名稱（其頂面即方塊底面），例如 'JVPCB1074973E'
    :param ram: RAM 卡 body 名稱，例如 'DIMM_DDR5_EGS'
    :param socket: RAM socket body 名稱，例如 'J33'
    :param result_name: 生成的簡化方塊 body 名稱
    :param named_selection: 方塊底面接合面的 named selection 名稱
    """
    args = {}
    if motherboard is not None:
        args['motherboard'] = motherboard
    if ram is not None:
        args['ram'] = ram
    if socket is not None:
        args['socket'] = socket
    if result_name is not None:
        args['result_name'] = result_name
    if named_selection is not None:
        args['named_selection'] = named_selection
    res = await sim_impl.call_tool('geometry_simplify_ram', args)
    return "\n".join([c.text for c in res])

@tool_geometry(name='geometry_simplify_ram_batch')
async def geometry_simplify_ram_batch(motherboard: str, ram: str, socket: str, result_prefix: str = 'RAM_simplified', ns_prefix: str = 'mb_bonded', tol_mm: float = 2.0) -> dict:
    """批次簡化所有同名 RAM+socket 配對（依 X 中心位置自動就近配對）【呼叫前必須先向使用者索取主機板、RAM、socket 三個 body 名稱，不可猜測或自行從 body 清單推斷】

    每一對成為一座落於主機板頂面的方塊，各自建立底面 named selection，依 X 順序編號（<result_prefix>_01、<ns_prefix>_01…）。適用於同一板上多條相同的 DIMM/socket 陣列（例如 32× DIMM + 32× socket）。原始 body 保留不動。
    :param motherboard: 主機板 body 名稱（頂面=各方塊底面）
    :param ram: RAM 卡 body 名稱（陣列中重複出現）
    :param socket: socket body 名稱（陣列中重複出現）
    :param result_prefix: 方塊 body 名稱前綴（自動編號）
    :param ns_prefix: 底面 named selection 名稱前綴（自動編號）
    :param tol_mm: 將 RAM 與 socket 視為一對的最大 X 中心距離（單位：毫米 mm）
    """
    args = {}
    if motherboard is not None:
        args['motherboard'] = motherboard
    if ram is not None:
        args['ram'] = ram
    if socket is not None:
        args['socket'] = socket
    if result_prefix is not None:
        args['result_prefix'] = result_prefix
    if ns_prefix is not None:
        args['ns_prefix'] = ns_prefix
    if tol_mm is not None:
        args['tol_mm'] = tol_mm
    res = await sim_impl.call_tool('geometry_simplify_ram_batch', args)
    return "\n".join([c.text for c in res])

@tool_geometry(name='geometry_simplify_heatsink')
async def geometry_simplify_heatsink(source: str, result_name: str = None, density: float = None, material: str = 'aluminum', keep_source: bool = True, named_selection: str = 'hs_bottom', name_density_suffix: bool = True, hole_min_dia_mm: float = 2.5, extra_sources: List[str] = None, body_densities: Dict[str, Any] = None, all_instances: bool = False) -> dict:
    """將散熱片 (heatsink) 簡化為凸字形方塊組（底板＋上凸＋下凸＋鎖孔直圓柱），並反推等效密度

    適用擠型/壓鑄/折片/針狀鰭片，單一或多 body 組件。流程（高度軸為 world Y）：
      1. 量測原始體積，以常見散熱片密度（預設鋁 2700 kg/m³；body_densities 可逐 body 指定）估算質量 m。
      2. 分析原始幾何：主接合底面、鰭片根部、鰭片排（取最大一排）、鎖孔位置與孔徑。
      3. 以方塊重建：底板（包圍盒 X-Z，板底→鰭片根部）、上凸（最大鰭片排，根部→鰭片頂）、
         下凸（主接合底面範圍，接觸面→板底）；無階梯、無圓角，螺絲/彈簧/推銷不保留。
      4. 鎖孔以 Y 向直圓柱貫穿。
      5. 主接合底面建立 named selection；ρ_equiv = m / V_sim 附加於新 body 名稱後綴（_rho<整數 kg/m³>）。
    結果建於原始 body 所屬 component；原始 body 預設保留。單位內算為公尺、回報為毫米。
    :param source: 散熱片主 body 名稱，例如 'ENDURANCE-POWER-BRICK-HS-241018'
    :param result_name: 簡化體 body 名稱（不填則為 <source>_sim）
    :param density: 散熱片材料密度 (kg/m³)，不填則依 material 預設
    :param material: 常見散熱片材料（aluminum=2700, copper=8960 kg/m³），決定預設密度
    :param keep_source: 是否保留原始散熱片 body（預設保留）
    :param named_selection: 簡化體主接合底面的 named selection 名稱
    :param name_density_suffix: 是否將反推等效密度附加於新 body 名稱後綴
    :param hole_min_dia_mm: 視為鎖孔的最小孔喉直徑 (mm)；預設 2.5mm
    :param extra_sources: 多 body 散熱片額外併入的 body 名稱或 glob（例 ['ICX_HS_1U_FIN_*', '1U_CUBASE']），限主 body 同一 component instance；螺絲/彈簧勿列入
    :param body_densities: 逐 body 密度 {名稱或 glob: kg/m³ 或材料名}，例 {'1U_CUBASE': 'copper'}
    :param all_instances: 是否處理所有含 source 的 component（同 master 只處理一次）
    """
    args = {}
    for key, val in (('source', source), ('result_name', result_name), ('density', density),
                     ('material', material), ('keep_source', keep_source),
                     ('named_selection', named_selection), ('name_density_suffix', name_density_suffix),
                     ('hole_min_dia_mm', hole_min_dia_mm), ('extra_sources', extra_sources),
                     ('body_densities', body_densities), ('all_instances', all_instances)):
        if val is not None:
            args[key] = list(val) if key == 'extra_sources' else val
    res = await sim_impl.call_tool('geometry_simplify_heatsink', args)
    return "\n".join([c.text for c in res])

@tool_geometry(name='geometry_midsurface')
async def geometry_midsurface(max_thickness_mm: float = 6.0, main_surface_ratio: float = 0.7,
                              area_difference_ratio: float = 0.1, complex_area_diff: float = 0.05,
                              enable_sheet_metal_check: bool = True,
                              hide_source_bodies: bool = True) -> dict:
    """對目前「已選取」的 body 批次建立中曲面 (midsurface)【呼叫前請先在 SpaceClaim 視窗選取欲抽中面的鈑金/薄殼 body】

    採面積最大優先的對向面配對，並以動態相切鏈補強：面積差超過 complex_area_diff 時改用強制相切鏈模式，對抗壓折邊遺失。可選鈑金件判斷（未通過者略過）與抽中面後隱藏原始 body。單位：厚度為毫米 mm。
    :param max_thickness_mm: 判定為薄件/對向面的最大板厚（mm）；對向面間距 >0 且 <= 此值才視為配對
    :param main_surface_ratio: 鈑金件判斷：主要對向面（含相切鏈）面積占整體面積的最小比例
    :param area_difference_ratio: 一對對向面可接受的相對面積差上限（0~1）
    :param complex_area_diff: 面積差超過此值即視為複雜件，改用強制相切鏈模式建立中面
    :param enable_sheet_metal_check: 是否啟用鈑金件判斷
    :param hide_source_bodies: 成功抽中面後是否隱藏原始實體 body
    """
    args = {}
    for key, val in (('max_thickness_mm', max_thickness_mm),
                     ('main_surface_ratio', main_surface_ratio),
                     ('area_difference_ratio', area_difference_ratio),
                     ('complex_area_diff', complex_area_diff),
                     ('enable_sheet_metal_check', enable_sheet_metal_check),
                     ('hide_source_bodies', hide_source_bodies)):
        if val is not None:
            args[key] = val
    res = await sim_impl.call_tool('geometry_midsurface', args)
    return "\n".join([c.text for c in res])

@tool_geometry(name='geometry_create_hole_groups')
async def geometry_create_hole_groups(diameter_min_mm: float = 2.0, diameter_max_mm: float = 20.0,
                                      mode: int = 0, pairing_strategy: str = "Ignore Component",
                                      distance_min_mm: float = 0.0, distance_max_mm: float = 10.0,
                                      holes_axis_dist_max_mm: float = 1.0, deg_max_circles: float = 10.0,
                                      grp_name_create: str = "Scr_AllHoles", index_grp_start: int = 1,
                                      rm_grp_create: bool = True, rm_grp_name_create: str = "Scr_RMgrp",
                                      index_rm_start: int = 1, grp_name_not_go: str = "NOTGoConnections",
                                      enable_distance_grouping: bool = False,
                                      distance_level1_mm: float = 5.0,
                                      distance_level2_mm: float = 20.0) -> dict:
    """偵測圓孔並建立 named selection 群組，再對同軸、距離在門檻內的孔兩兩配對建立 RM 連接群組【呼叫前請先在 SpaceClaim 視窗選取目標 body/edge】

    mode=0 時自動偵測整圓與半圓孔；mode=1 直接使用選取的任意邊。可選同件/跨件配對策略與距離分級（Near/Medium/Far）。單位：直徑與距離皆為毫米 mm。
    :param diameter_min_mm: 偵測圓孔的最小直徑（mm）
    :param diameter_max_mm: 偵測圓孔的最大直徑（mm）
    :param mode: 0=僅圓孔邊（自動偵測整圓/半圓）；1=直接使用選取的任意邊
    :param pairing_strategy: 配對策略 'Ignore Component'（忽略元件階層，含跨元件）或 'Within Component'（僅同元件內）
    :param distance_min_mm: 兩孔配對的最小間距（mm）
    :param distance_max_mm: 兩孔配對的最大間距（mm）
    :param holes_axis_dist_max_mm: 兩孔軸線間最大偏移距離（mm），超過視為不同軸
    :param deg_max_circles: 非圓曲線孔配對時兩面法向最大夾角（度）
    :param grp_name_create: 孔群組 named selection 名稱前綴
    :param index_grp_start: 孔群組名稱起始索引
    :param rm_grp_create: 是否執行孔配對並建立 RM 連接群組
    :param rm_grp_name_create: RM 連接群組 named selection 名稱前綴
    :param index_rm_start: RM 群組名稱起始索引
    :param grp_name_not_go: 排除清單群組名稱：其成員 edge 不參與配對
    :param enable_distance_grouping: 是否依配對間距分級（Near/Medium/Far）為 RM 群組加後綴
    :param distance_level1_mm: 距離分級門檻 1（mm）：<= 此值為 Near
    :param distance_level2_mm: 距離分級門檻 2（mm）：<= 此值為 Medium，否則 Far
    """
    args = {}
    for key, val in (('diameter_min_mm', diameter_min_mm), ('diameter_max_mm', diameter_max_mm),
                     ('mode', mode), ('pairing_strategy', pairing_strategy),
                     ('distance_min_mm', distance_min_mm), ('distance_max_mm', distance_max_mm),
                     ('holes_axis_dist_max_mm', holes_axis_dist_max_mm),
                     ('deg_max_circles', deg_max_circles),
                     ('grp_name_create', grp_name_create), ('index_grp_start', index_grp_start),
                     ('rm_grp_create', rm_grp_create), ('rm_grp_name_create', rm_grp_name_create),
                     ('index_rm_start', index_rm_start), ('grp_name_not_go', grp_name_not_go),
                     ('enable_distance_grouping', enable_distance_grouping),
                     ('distance_level1_mm', distance_level1_mm),
                     ('distance_level2_mm', distance_level2_mm)):
        if val is not None:
            args[key] = val
    res = await sim_impl.call_tool('geometry_create_hole_groups', args)
    return "\n".join([c.text for c in res])

# 回傳給模型的影像長邊上限（超過則縮圖；需 Pillow，缺少時回傳原圖）
_SCREENSHOT_MAX_EDGE = 1568


def _screenshot_image_content(path: str):
    """讀取本機截圖檔並轉為 MCP ImageContent；必要時縮圖。回傳 (content, note)。"""
    from fastmcp.utilities.types import Image
    try:
        from PIL import Image as PILImage
    except ImportError:
        PILImage = None

    if PILImage is None:
        ext = os.path.splitext(path)[1].lower().lstrip('.')
        if ext not in ('png', 'jpg', 'jpeg', 'gif'):
            return None, f"未安裝 Pillow，無法將 .{ext} 轉為可回傳的影像"
        return Image(path=path).to_image_content(), None

    import io
    with PILImage.open(path) as im:
        im.load()
        note = None
        if max(im.size) > _SCREENSHOT_MAX_EDGE:
            orig = im.size
            im.thumbnail((_SCREENSHOT_MAX_EDGE, _SCREENSHOT_MAX_EDGE))
            note = f"回傳影像已由 {orig[0]}x{orig[1]} 縮為 {im.size[0]}x{im.size[1]}（檔案為原尺寸）"
        buf = io.BytesIO()
        im.convert('RGB').save(buf, format='PNG')
    return Image(data=buf.getvalue(), format='png').to_image_content(), note


@mcp.tool(name='geometry_screenshot')
async def geometry_screenshot(file_path: str, image_format: str = None, fit: bool = True,
                              view: str = 'current', bodies: List[str] = None,
                              return_image: bool = True):
    """將 SpaceClaim 3D 視窗出圖為影像檔，並（預設）把影像一併回傳供目視確認幾何或簡化結果

    透過 Modeler.run_script_file 送伺服器端腳本呼叫 Window.Export 出圖（PyAnsys Geometry 25.1 無 graphics 套件時仍可用）。需 SpaceClaim 有作用中的 GUI 視窗；出圖後會還原原視角與 body 可見性。
    :param file_path: 輸出影像路徑（相對路徑會轉絕對；目錄不存在自動建立；無副檔名則依格式補上）
    :param image_format: 影像格式 png/jpg/jpeg/bmp/tif/tiff/gif；省略則依副檔名推斷，與副檔名不一致會報錯
    :param fit: 截圖前是否 ZoomExtents 全景縮放
    :param view: 視角 current/iso/front/back/top/bottom/left/right（Y 朝上座標系）
    :param bodies: 僅顯示這些 body（依名稱），其他暫時隱藏，截圖後還原
    :param return_image: 是否把影像內容一併回傳（檔案需在本機可讀；過大會縮圖）
    """
    from fastmcp.tools.base import ToolResult
    from mcp.types import TextContent
    import json

    args = {'file_path': file_path, 'fit': fit, 'view': view}
    if image_format:
        args['image_format'] = image_format
    if bodies:
        args['bodies'] = list(bodies)
    try:
        res = await sim_impl.call_tool('geometry_screenshot', args)
        env = _envelope("\n".join([c.text for c in res]))
    except Exception as exc:
        env = _envelope({"ok": False, "error": str(exc)})

    content = []
    if env.get("ok") and return_image:
        path = env.get("file_path")
        if path and os.path.isfile(path):
            try:
                img, note = _screenshot_image_content(path)
                if img is not None:
                    content.append(img)
                    env["image_returned"] = True
                if note:
                    env.setdefault("warnings", []).append(note)
            except Exception as exc:
                env.setdefault("warnings", []).append(f"影像讀取失敗: {exc}")
        else:
            env.setdefault("warnings", []).append(
                "截圖檔不在本機（SpaceClaim 可能在遠端/容器執行），未回傳影像")
        env.setdefault("image_returned", False)

    content.insert(0, TextContent(type="text", text=json.dumps(env, ensure_ascii=False)))
    return ToolResult(content=content, structured_content=env, is_error=not env.get("ok"))

@tool_geometry(name='geometry_export')
async def geometry_export(file_path: str, format: str = 'step') -> dict:
    """匯出幾何為 STEP/IGES 格式
    :param file_path: 
    :param format: 
    """
    args = {}
    if file_path is not None:
        args['file_path'] = file_path
    if format is not None:
        args['format'] = format
    res = await sim_impl.call_tool('geometry_export', args)
    return "\n".join([c.text for c in res])

@tool_geometry(name='geometry_list_bodies')
async def geometry_list_bodies() -> dict:
    """列出當前設計中的所有幾何體
    """
    args = {}
    res = await sim_impl.call_tool('geometry_list_bodies', args)
    return "\n".join([c.text for c in res])

@tool_geometry(name='geometry_import_file')
async def geometry_import_file(file_path: str) -> dict:
    """匯入 CAD 檔案
    :param file_path: 
    """
    args = {}
    if file_path is not None:
        args['file_path'] = file_path
    res = await sim_impl.call_tool('geometry_import_file', args)
    return "\n".join([c.text for c in res])

@tool_geometry(name='geometry_status')
async def geometry_status() -> dict:
    """Geometry 建模器連線狀態
    """
    args = {}
    res = await sim_impl.call_tool('geometry_status', args)
    return "\n".join([c.text for c in res])

@tool_geometry(name='geometry_close')
async def geometry_close() -> dict:
    """關閉 Geometry 建模器
    """
    args = {}
    res = await sim_impl.call_tool('geometry_close', args)
    return "\n".join([c.text for c in res])
