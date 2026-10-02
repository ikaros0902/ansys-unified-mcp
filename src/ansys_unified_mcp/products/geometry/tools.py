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


@mcp.resource("ansys://geometry/model-tree")
async def geometry_model_tree_resource() -> str:
    """唯讀讀取 SpaceClaim/Geometry 目前設計中的組裝件與實體清單，不觸發任何 Tool 呼叫額度。

    對應 Phase 3 任務 3.3（docs/reviews/2026-10-02-phase2-3-feasibility-assessment.md）。
    內部委派既有 geometry_list_bodies 工具邏輯，不重複實作。
    """
    res = await sim_impl.call_tool('geometry_list_bodies', {})
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
