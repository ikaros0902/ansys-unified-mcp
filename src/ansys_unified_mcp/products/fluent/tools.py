# -*- coding: utf-8 -*-
import os
from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.drivers import sim_impl
from typing import Any, List, Dict
import functools

def tool_fluent(name=None):
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

@tool_fluent(name='fluent_launch')
async def fluent_launch(processors: int = 4, cwd: str = None, port: int = None, ip: str = '127.0.0.1', password: str = None, connect_timeout: int = 30) -> dict:
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

@tool_fluent(name='fluent_read_case')
async def fluent_read_case(file_path: str) -> dict:
    """載入 .cas 算例檔案
    :param file_path: 
    """
    args = {}
    if file_path is not None:
        args['file_path'] = file_path
    res = await sim_impl.call_tool('fluent_read_case', args)
    return "\n".join([c.text for c in res])

@tool_fluent(name='fluent_read_mesh')
async def fluent_read_mesh(file_path: str) -> dict:
    """載入 .msh 網格檔案
    :param file_path: 
    """
    args = {}
    if file_path is not None:
        args['file_path'] = file_path
    res = await sim_impl.call_tool('fluent_read_mesh', args)
    return "\n".join([c.text for c in res])

@tool_fluent(name='fluent_set_solver')
async def fluent_set_solver(viscous_model: str = None, energy: bool = None, transient: bool = None) -> dict:
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

@tool_fluent(name='fluent_set_boundary')
async def fluent_set_boundary(zone: str, bc_type: str, params: dict = None) -> dict:
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

@tool_fluent(name='fluent_set_material')
async def fluent_set_material(zone: str, material: str) -> dict:
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

@tool_fluent(name='fluent_initialize')
async def fluent_initialize(method: str = 'hybrid') -> dict:
    """初始化流場（hybrid/standard）
    :param method: 
    """
    args = {}
    if method is not None:
        args['method'] = method
    res = await sim_impl.call_tool('fluent_initialize', args)
    return "\n".join([c.text for c in res])

@tool_fluent(name='fluent_iterate')
async def fluent_iterate(iterations: int) -> dict:
    """迭代計算
    :param iterations: 
    """
    args = {}
    if iterations is not None:
        args['iterations'] = iterations
    res = await sim_impl.call_tool('fluent_iterate', args)
    return "\n".join([c.text for c in res])

@tool_fluent(name='fluent_get_residuals')
async def fluent_get_residuals() -> dict:
    """獲取殘差值
    """
    args = {}
    res = await sim_impl.call_tool('fluent_get_residuals', args)
    return "\n".join([c.text for c in res])

@tool_fluent(name='fluent_save')
async def fluent_save(prefix: str) -> dict:
    """儲存 case/data
    :param prefix: 
    """
    args = {}
    if prefix is not None:
        args['prefix'] = prefix
    res = await sim_impl.call_tool('fluent_save', args)
    return "\n".join([c.text for c in res])

@tool_fluent(name='fluent_tui')
async def fluent_tui(command: str) -> dict:
    """執行 Fluent TUI 命令
    :param command: 
    """
    args = {}
    if command is not None:
        args['command'] = command
    res = await sim_impl.call_tool('fluent_tui', args)
    return "\n".join([c.text for c in res])

@tool_fluent(name='fluent_status')
async def fluent_status() -> dict:
    """Fluent 連線狀態
    """
    args = {}
    res = await sim_impl.call_tool('fluent_status', args)
    return "\n".join([c.text for c in res])

@tool_fluent(name='fluent_load_udf')
async def fluent_load_udf(source_file: str, compile: bool = False) -> dict:
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

@tool_fluent(name='fluent_hook_udf')
async def fluent_hook_udf(zone_name: str, profile_name: str, phase_name: str = 'water', momentum_field: str = 'mass_flux') -> dict:
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

@tool_fluent(name='fluent_list_udfs')
async def fluent_list_udfs(zone_name: str = None) -> dict:
    """列出已載入的 UDF 和邊界條件掛鉤狀態
    :param zone_name: 檢查指定區域的 UDF 掛鉤狀態（可選）
    """
    args = {}
    if zone_name is not None:
        args['zone_name'] = zone_name
    res = await sim_impl.call_tool('fluent_list_udfs', args)
    return "\n".join([c.text for c in res])

@tool_fluent(name='fluent_exit')
async def fluent_exit() -> dict:
    """關閉 Fluent
    """
    args = {}
    res = await sim_impl.call_tool('fluent_exit', args)
    return "\n".join([c.text for c in res])

@tool_fluent(name='fluent_get_script')
async def fluent_get_script() -> dict:
    """獲取當前 MCP 操作序列對應的 .jou 指令碼（Skill 聯動：自動累積 MCP→TUI 對映）
    """
    args = {}
    res = await sim_impl.call_tool('fluent_get_script', args)
    return "\n".join([c.text for c in res])

@tool_fluent(name='fluent_get_mapping_report')
async def fluent_get_mapping_report() -> dict:
    """獲取 MCP 到 TUI 的完整對映報告
    """
    args = {}
    res = await sim_impl.call_tool('fluent_get_mapping_report', args)
    return "\n".join([c.text for c in res])

@tool_fluent(name='fluent_reset_mapper')
async def fluent_reset_mapper() -> dict:
    """重置 TUI 對映器（清除歷史記錄）
    """
    args = {}
    res = await sim_impl.call_tool('fluent_reset_mapper', args)
    return "\n".join([c.text for c in res])

