# -*- coding: utf-8 -*-
from ansys_unified_mcp.shared import mcp
from ansys_unified_mcp import sim_impl
from typing import Any, List, Dict

@mcp.tool(name='fluent_launch')
async def fluent_launch(processors: int = 4, cwd: str = None, port: int = None, ip: str = '127.0.0.1', password: str = None, connect_timeout: int = 30) -> str:
    """啟動 Fluent solver 或連線現有例項
    :param processors: 啟動新例項時的處理器數量
    :param cwd: 啟動新例項時的工作目錄
    :param port: 連線現有 Fluent 例項的埠號，不填則啟動新例項
    :param ip: 連線現有例項的 IP 地址
    :param password: gRPC連線密碼（連線遠端/非localhost時提供）
    :param connect_timeout: 連線超時時間（秒），預設30秒，超時自動中斷
    """
    args = {}
    if processors is not None:
        args['processors'] = processors
    if cwd is not None:
        args['cwd'] = cwd
    if port is not None:
        args['port'] = port
    if ip is not None:
        args['ip'] = ip
    if password is not None:
        args['password'] = password
    if connect_timeout is not None:
        args['connect_timeout'] = connect_timeout
    res = await sim_impl.call_tool('fluent_launch', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='fluent_read_case')
async def fluent_read_case(file_path: str) -> str:
    """載入 .cas 算例檔案
    :param file_path: 
    """
    args = {}
    if file_path is not None:
        args['file_path'] = file_path
    res = await sim_impl.call_tool('fluent_read_case', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='fluent_read_mesh')
async def fluent_read_mesh(file_path: str) -> str:
    """載入 .msh 網格檔案
    :param file_path: 
    """
    args = {}
    if file_path is not None:
        args['file_path'] = file_path
    res = await sim_impl.call_tool('fluent_read_mesh', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='fluent_set_solver')
async def fluent_set_solver(viscous_model: str = None, energy: bool = None, transient: bool = None) -> str:
    """設定求解器（湍流模型/能量/瞬態）
    :param viscous_model: 
    :param energy: 
    :param transient: 
    """
    args = {}
    if viscous_model is not None:
        args['viscous_model'] = viscous_model
    if energy is not None:
        args['energy'] = energy
    if transient is not None:
        args['transient'] = transient
    res = await sim_impl.call_tool('fluent_set_solver', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='fluent_set_boundary')
async def fluent_set_boundary(zone: str, bc_type: str, params: dict = None) -> str:
    """設定邊界條件
    :param zone: 
    :param bc_type: 
    :param params: 
    """
    args = {}
    if zone is not None:
        args['zone'] = zone
    if bc_type is not None:
        args['bc_type'] = bc_type
    if params is not None:
        args['params'] = params
    res = await sim_impl.call_tool('fluent_set_boundary', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='fluent_set_material')
async def fluent_set_material(zone: str, material: str) -> str:
    """設定區域材料
    :param zone: 
    :param material: 
    """
    args = {}
    if zone is not None:
        args['zone'] = zone
    if material is not None:
        args['material'] = material
    res = await sim_impl.call_tool('fluent_set_material', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='fluent_initialize')
async def fluent_initialize(method: str = 'hybrid') -> str:
    """初始化流場（hybrid/standard）
    :param method: 
    """
    args = {}
    if method is not None:
        args['method'] = method
    res = await sim_impl.call_tool('fluent_initialize', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='fluent_iterate')
async def fluent_iterate(iterations: int) -> str:
    """迭代計算
    :param iterations: 
    """
    args = {}
    if iterations is not None:
        args['iterations'] = iterations
    res = await sim_impl.call_tool('fluent_iterate', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='fluent_get_residuals')
async def fluent_get_residuals() -> str:
    """獲取殘差值
    """
    args = {}
    res = await sim_impl.call_tool('fluent_get_residuals', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='fluent_save')
async def fluent_save(prefix: str) -> str:
    """儲存 case/data
    :param prefix: 
    """
    args = {}
    if prefix is not None:
        args['prefix'] = prefix
    res = await sim_impl.call_tool('fluent_save', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='fluent_tui')
async def fluent_tui(command: str) -> str:
    """執行 Fluent TUI 命令
    :param command: 
    """
    args = {}
    if command is not None:
        args['command'] = command
    res = await sim_impl.call_tool('fluent_tui', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='fluent_status')
async def fluent_status() -> str:
    """Fluent 連線狀態
    """
    args = {}
    res = await sim_impl.call_tool('fluent_status', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='fluent_load_udf')
async def fluent_load_udf(source_file: str, compile: bool = False) -> str:
    """載入 UDF（自動處理 Windows 磁碟機代號路徑問題，解釋並驗證成功）
    :param source_file: UDF 原始檔絕對路徑（如 E:/path/to/file.c）
    :param compile: 是否編譯（預設 False 即解釋執行）
    """
    args = {}
    if source_file is not None:
        args['source_file'] = source_file
    if compile is not None:
        args['compile'] = compile
    res = await sim_impl.call_tool('fluent_load_udf', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='fluent_hook_udf')
async def fluent_hook_udf(zone_name: str, profile_name: str, phase_name: str = 'water', momentum_field: str = 'mass_flux') -> str:
    """將已載入的 UDF profile 掛鉤到邊界條件
    :param zone_name: 邊界條件區域名稱
    :param profile_name: UDF profile 函式名
    :param phase_name: 多相流相名稱
    :param momentum_field: 動量場型別（mass_flux/mass_flow_rate）
    """
    args = {}
    if zone_name is not None:
        args['zone_name'] = zone_name
    if profile_name is not None:
        args['profile_name'] = profile_name
    if phase_name is not None:
        args['phase_name'] = phase_name
    if momentum_field is not None:
        args['momentum_field'] = momentum_field
    res = await sim_impl.call_tool('fluent_hook_udf', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='fluent_list_udfs')
async def fluent_list_udfs(zone_name: str = None) -> str:
    """列出已載入的 UDF 和邊界條件掛鉤狀態
    :param zone_name: 檢查指定區域的 UDF 掛鉤狀態（可選）
    """
    args = {}
    if zone_name is not None:
        args['zone_name'] = zone_name
    res = await sim_impl.call_tool('fluent_list_udfs', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='fluent_exit')
async def fluent_exit() -> str:
    """關閉 Fluent
    """
    args = {}
    res = await sim_impl.call_tool('fluent_exit', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='fluent_get_script')
async def fluent_get_script() -> str:
    """獲取當前 MCP 操作序列對應的 .jou 指令碼（Skill 聯動：自動累積 MCP→TUI 對映）
    """
    args = {}
    res = await sim_impl.call_tool('fluent_get_script', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='fluent_get_mapping_report')
async def fluent_get_mapping_report() -> str:
    """獲取 MCP 到 TUI 的完整對映報告
    """
    args = {}
    res = await sim_impl.call_tool('fluent_get_mapping_report', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='fluent_reset_mapper')
async def fluent_reset_mapper() -> str:
    """重置 TUI 對映器（清除歷史記錄）
    """
    args = {}
    res = await sim_impl.call_tool('fluent_reset_mapper', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='mechanical_launch')
async def mechanical_launch(port: int = None) -> str:
    """連線/啟動 Ansys Mechanical（指定埠則連線現有例項，否則啟動 batch 模式）
    :param port: 連線現有例項的埠號，不填則啟動新 batch 例項
    """
    args = {}
    if port is not None:
        args['port'] = port
    res = await sim_impl.call_tool('mechanical_launch', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='mechanical_import')
async def mechanical_import(file_path: str) -> str:
    """匯入幾何檔案
    :param file_path: 
    """
    args = {}
    if file_path is not None:
        args['file_path'] = file_path
    res = await sim_impl.call_tool('mechanical_import', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='mechanical_set_material')
async def mechanical_set_material(body: str, material: str) -> str:
    """分配材料
    :param body: 
    :param material: 
    """
    args = {}
    if body is not None:
        args['body'] = body
    if material is not None:
        args['material'] = material
    res = await sim_impl.call_tool('mechanical_set_material', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='mechanical_mesh')
async def mechanical_mesh(element_size: float = None, method: str = None) -> str:
    """劃分網格
    :param element_size: 
    :param method: 
    """
    args = {}
    if element_size is not None:
        args['element_size'] = element_size
    if method is not None:
        args['method'] = method
    res = await sim_impl.call_tool('mechanical_mesh', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='mechanical_apply_load')
async def mechanical_apply_load(load_type: str, location: str, magnitude: float = None, direction: list = None) -> str:
    """施載入荷/約束
    :param load_type: 
    :param location: 
    :param magnitude: 
    :param direction: 
    """
    args = {}
    if load_type is not None:
        args['load_type'] = load_type
    if location is not None:
        args['location'] = location
    if magnitude is not None:
        args['magnitude'] = magnitude
    if direction is not None:
        args['direction'] = direction
    res = await sim_impl.call_tool('mechanical_apply_load', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='mechanical_solve')
async def mechanical_solve() -> str:
    """執行求解
    """
    args = {}
    res = await sim_impl.call_tool('mechanical_solve', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='mechanical_get_result')
async def mechanical_get_result(result_type: str) -> str:
    """提取結果
    :param result_type: 
    """
    args = {}
    if result_type is not None:
        args['result_type'] = result_type
    res = await sim_impl.call_tool('mechanical_get_result', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='mechanical_list')
async def mechanical_list(what: str = 'bodies') -> str:
    """列出幾何體/Named Selections
    :param what: 
    """
    args = {}
    if what is not None:
        args['what'] = what
    res = await sim_impl.call_tool('mechanical_list', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='mechanical_script')
async def mechanical_script(script: str) -> str:
    """執行 IronPython 指令碼
    :param script: 
    """
    args = {}
    if script is not None:
        args['script'] = script
    res = await sim_impl.call_tool('mechanical_script', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='mechanical_status')
async def mechanical_status() -> str:
    """Mechanical 連線狀態
    """
    args = {}
    res = await sim_impl.call_tool('mechanical_status', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='mechanical_exit')
async def mechanical_exit() -> str:
    """關閉 Mechanical
    """
    args = {}
    res = await sim_impl.call_tool('mechanical_exit', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='geometry_launch')
async def geometry_launch(port: int = None, host: str = "localhost", transport_mode: str = "wnua", connect_timeout: int = 60) -> str:
    """啟動 Geometry 建模器或連線現有 SpaceClaim 實例

    :param port: 連線已啟動 SpaceClaim 的 gRPC 埠號，不填則啟動新實例（啟動前會自動掃描 50051-50055 尋找已運行實例）
    :param host: SpaceClaim 主機地址
    :param transport_mode: gRPC 傳輸模式（Windows 預設 wnua）
    :param connect_timeout: 連線/啟動超時秒數，預設60秒
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


@mcp.tool(name='geometry_create_design')
async def geometry_create_design(name: str) -> str:
    """建立新的幾何設計
    :param name: 
    """
    args = {}
    if name is not None:
        args['name'] = name
    res = await sim_impl.call_tool('geometry_create_design', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='geometry_create_block')
async def geometry_create_block(name: str, length: float = 0.01, width: float = 0.01, height: float = 0.01, center_x: float = 0, center_y: float = 0, center_z: float = 0) -> str:
    """建立立方體（v242: 用 sketch + extrude 實現）
    :param name: 
    :param length: 
    :param width: 
    :param height: 
    :param center_x: 
    :param center_y: 
    :param center_z: 
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

@mcp.tool(name='geometry_create_cylinder')
async def geometry_create_cylinder(name: str, radius: float = 0.005, height: float = 0.01, center_x: float = 0, center_y: float = 0, center_z: float = 0) -> str:
    """建立圓柱體（extrude_sketch 方式）
    :param name: 
    :param radius: 
    :param height: 
    :param center_x: 
    :param center_y: 
    :param center_z: 
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

@mcp.tool(name='geometry_create_sphere')
async def geometry_create_sphere(name: str, radius: float = 0.005, center_x: float = 0, center_y: float = 0, center_z: float = 0) -> str:
    """建立球體
    :param name: 
    :param radius: 
    :param center_x: 
    :param center_y: 
    :param center_z: 
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

@mcp.tool(name='geometry_export')
async def geometry_export(file_path: str, format: str = 'step') -> str:
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

@mcp.tool(name='geometry_list_bodies')
async def geometry_list_bodies() -> str:
    """列出當前設計中的所有幾何體
    """
    args = {}
    res = await sim_impl.call_tool('geometry_list_bodies', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='geometry_import_file')
async def geometry_import_file(file_path: str) -> str:
    """匯入 CAD 檔案
    :param file_path: 
    """
    args = {}
    if file_path is not None:
        args['file_path'] = file_path
    res = await sim_impl.call_tool('geometry_import_file', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='geometry_status')
async def geometry_status() -> str:
    """Geometry 建模器連線狀態
    """
    args = {}
    res = await sim_impl.call_tool('geometry_status', args)
    return "\n".join([c.text for c in res])

@mcp.tool(name='geometry_close')
async def geometry_close() -> str:
    """關閉 Geometry 建模器
    """
    args = {}
    res = await sim_impl.call_tool('geometry_close', args)
    return "\n".join([c.text for c in res])
