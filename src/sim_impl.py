#!/usr/bin/env python3
"""ANSYS MCP Server — Fluent + Mechanical + Geometry (v242).

驅動層:
  - Fluent       → ansys-fluent-core (PyFluent) gRPC
  - Mechanical   → ansys-mechanical-core (PyMechanical) gRPC
  - Geometry     → ansys-geometry-core (PyAnsys Geometry) gRPC
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# ===================================================================
# MCP-TUI 自動對映器（Skill 聯動）
# ===================================================================
_skill_scripts_dir = Path(__file__).resolve().parent / "ansys-fluent-tui-guide" / "scripts"
if _skill_scripts_dir.exists():
    sys.path.insert(0, str(_skill_scripts_dir))
    from mcp_tui_auto_mapper import map_mcp_call, get_mapping_report, reset_mapper
else:
    map_mcp_call = None      # type: ignore[assignment]
    get_mapping_report = None  # type: ignore[assignment]
    reset_mapper = None       # type: ignore[assignment]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ansys-mcp")

# ---------------------------------------------------------------------------
# Global sessions
# ---------------------------------------------------------------------------
_fluent_session = None
_mechanical_session = None
_modeler = None       # PyAnsys Geometry Modeler
_current_design = None  # track active design name

# ===================================================================
# TOOLS
# ===================================================================

FLUENT_TOOLS = [
    Tool(name="fluent_launch", description="啟動 Fluent solver 或連線現有例項",
         inputSchema={"type": "object", "properties": {
             "processors": {"type": "integer", "default": 4, "description": "啟動新例項時的處理器數量"},
             "cwd": {"type": "string", "description": "啟動新例項時的工作目錄"},
             "port": {"type": "integer", "description": "連線現有 Fluent 例項的埠號，不填則啟動新例項"},
             "ip": {"type": "string", "default": "127.0.0.1", "description": "連線現有例項的 IP 地址"},
             "password": {"type": "string", "description": "gRPC連線密碼（連線遠端/非localhost時提供）"},
             "connect_timeout": {"type": "integer", "default": 30, "description": "連線超時時間（秒），預設30秒，超時自動中斷"}}}),
    Tool(name="fluent_read_case", description="載入 .cas 算例檔案",
         inputSchema={"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}),
    Tool(name="fluent_read_mesh", description="載入 .msh 網格檔案",
         inputSchema={"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}),
    Tool(name="fluent_set_solver", description="設定求解器（湍流模型/能量/瞬態）",
         inputSchema={"type": "object", "properties": {
             "viscous_model": {"type": "string", "enum": ["laminar", "k-epsilon", "k-omega", "sst", "spalart-allmaras"]},
             "energy": {"type": "boolean"}, "transient": {"type": "boolean"}}}),
    Tool(name="fluent_set_boundary", description="設定邊界條件",
         inputSchema={"type": "object", "properties": {
             "zone": {"type": "string"}, "bc_type": {"type": "string"}, "params": {"type": "object"}},
             "required": ["zone", "bc_type"]}),
    Tool(name="fluent_set_material", description="設定區域材料",
         inputSchema={"type": "object", "properties": {"zone": {"type": "string"}, "material": {"type": "string"}},
             "required": ["zone", "material"]}),
    Tool(name="fluent_initialize", description="初始化流場（hybrid/standard）",
         inputSchema={"type": "object", "properties": {"method": {"type": "string", "enum": ["hybrid", "standard"], "default": "hybrid"}}}),
    Tool(name="fluent_iterate", description="迭代計算",
         inputSchema={"type": "object", "properties": {"iterations": {"type": "integer", "default": 100}}, "required": ["iterations"]}),
    Tool(name="fluent_get_residuals", description="獲取殘差值", inputSchema={"type": "object", "properties": {}}),
    Tool(name="fluent_save", description="儲存 case/data",
         inputSchema={"type": "object", "properties": {"prefix": {"type": "string"}}, "required": ["prefix"]}),
    Tool(name="fluent_tui", description="執行 Fluent TUI 命令",
         inputSchema={"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}),
    Tool(name="fluent_status", description="Fluent 連線狀態", inputSchema={"type": "object", "properties": {}}),
    Tool(name="fluent_load_udf", description="載入 UDF（自動處理 Windows 磁碟機代號路徑問題，解釋並驗證成功）",
         inputSchema={"type": "object", "properties": {
             "source_file": {"type": "string", "description": "UDF 原始檔絕對路徑（如 E:/path/to/file.c）"},
             "compile": {"type": "boolean", "default": False, "description": "是否編譯（預設 False 即解釋執行）"}},
             "required": ["source_file"]}),
    Tool(name="fluent_hook_udf", description="將已載入的 UDF profile 掛鉤到邊界條件",
         inputSchema={"type": "object", "properties": {
             "zone_name": {"type": "string", "description": "邊界條件區域名稱"},
             "phase_name": {"type": "string", "default": "water", "description": "多相流相名稱"},
             "profile_name": {"type": "string", "description": "UDF profile 函式名"},
             "momentum_field": {"type": "string", "default": "mass_flux", "description": "動量場型別（mass_flux/mass_flow_rate）"}},
             "required": ["zone_name", "profile_name"]}),
    Tool(name="fluent_list_udfs", description="列出已載入的 UDF 和邊界條件掛鉤狀態",
         inputSchema={"type": "object", "properties": {
             "zone_name": {"type": "string", "description": "檢查指定區域的 UDF 掛鉤狀態（可選）"}}}),
    Tool(name="fluent_exit", description="關閉 Fluent", inputSchema={"type": "object", "properties": {}}),
    Tool(name="fluent_get_script", description="獲取當前 MCP 操作序列對應的 .jou 指令碼（Skill 聯動：自動累積 MCP→TUI 對映）",
         inputSchema={"type": "object", "properties": {}}),
    Tool(name="fluent_get_mapping_report", description="獲取 MCP 到 TUI 的完整對映報告",
         inputSchema={"type": "object", "properties": {}}),
    Tool(name="fluent_reset_mapper", description="重置 TUI 對映器（清除歷史記錄）",
         inputSchema={"type": "object", "properties": {}}),
]

MECHANICAL_TOOLS = [
    Tool(name="mechanical_launch", description="連線/啟動 Ansys Mechanical（指定埠則連線現有例項，否則啟動 batch 模式）",
         inputSchema={"type": "object", "properties": {
             "port": {"type": "integer", "description": "連線現有例項的埠號，不填則啟動新 batch 例項"}
         }}),
    Tool(name="mechanical_import", description="匯入幾何檔案",
         inputSchema={"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}),
    Tool(name="mechanical_set_material", description="分配材料",
         inputSchema={"type": "object", "properties": {"body": {"type": "string"}, "material": {"type": "string"}},
             "required": ["body", "material"]}),
    Tool(name="mechanical_mesh", description="劃分網格",
         inputSchema={"type": "object", "properties": {"element_size": {"type": "number"},
             "method": {"type": "string", "enum": ["automatic", "tetrahedrons", "hex_dominant"]}}}),
    Tool(name="mechanical_apply_load", description="施載入荷/約束",
         inputSchema={"type": "object", "properties": {
             "load_type": {"type": "string", "enum": ["force", "pressure", "fixed_support", "displacement"]},
             "location": {"type": "string"}, "magnitude": {"type": "number"},
             "direction": {"type": "array", "items": {"type": "number"}}}, "required": ["load_type", "location"]}),
    Tool(name="mechanical_solve", description="執行求解", inputSchema={"type": "object", "properties": {}}),
    Tool(name="mechanical_get_result", description="提取結果",
         inputSchema={"type": "object", "properties": {
             "result_type": {"type": "string", "enum": ["total_deformation", "equivalent_stress", "equivalent_strain"]}},
             "required": ["result_type"]}),
    Tool(name="mechanical_list", description="列出幾何體/Named Selections",
         inputSchema={"type": "object", "properties": {
             "what": {"type": "string", "enum": ["bodies", "named_selections"], "default": "bodies"}}}),
    Tool(name="mechanical_script", description="執行 IronPython 指令碼",
         inputSchema={"type": "object", "properties": {"script": {"type": "string"}}, "required": ["script"]}),
    Tool(name="mechanical_status", description="Mechanical 連線狀態", inputSchema={"type": "object", "properties": {}}),
    Tool(name="mechanical_exit", description="關閉 Mechanical", inputSchema={"type": "object", "properties": {}}),
]

GEOMETRY_TOOLS = [
    Tool(name="geometry_launch", description="啟動 Geometry 建模器（Discovery/SpaceClaim 後端）",
         inputSchema={"type": "object", "properties": {}}),
    Tool(name="geometry_create_design", description="建立新的幾何設計",
         inputSchema={"type": "object", "properties": {"name": {"type": "string", "default": "Design"}},
             "required": ["name"]}),
    Tool(name="geometry_create_block", description="建立立方體（v242: 用 sketch + extrude 實現）",
         inputSchema={"type": "object", "properties": {
             "name": {"type": "string", "default": "Block"},
             "length": {"type": "number", "default": 0.01}, "width": {"type": "number", "default": 0.01},
             "height": {"type": "number", "default": 0.01},
             "center_x": {"type": "number", "default": 0}, "center_y": {"type": "number", "default": 0},
             "center_z": {"type": "number", "default": 0}}, "required": ["name"]}),
    Tool(name="geometry_create_cylinder", description="建立圓柱體（extrude_sketch 方式）",
         inputSchema={"type": "object", "properties": {
             "name": {"type": "string", "default": "Cylinder"},
             "radius": {"type": "number", "default": 0.005}, "height": {"type": "number", "default": 0.01},
             "center_x": {"type": "number", "default": 0}, "center_y": {"type": "number", "default": 0},
             "center_z": {"type": "number", "default": 0}}, "required": ["name"]}),
    Tool(name="geometry_create_sphere", description="建立球體",
         inputSchema={"type": "object", "properties": {
             "name": {"type": "string", "default": "Sphere"}, "radius": {"type": "number", "default": 0.005},
             "center_x": {"type": "number", "default": 0}, "center_y": {"type": "number", "default": 0},
             "center_z": {"type": "number", "default": 0}}, "required": ["name"]}),
    Tool(name="geometry_export", description="匯出幾何為 STEP/IGES 格式",
         inputSchema={"type": "object", "properties": {
             "file_path": {"type": "string"},
             "format": {"type": "string", "enum": ["step", "iges"], "default": "step"}},
             "required": ["file_path"]}),
    Tool(name="geometry_list_bodies", description="列出當前設計中的所有幾何體", inputSchema={"type": "object", "properties": {}}),
    Tool(name="geometry_import_file", description="匯入 CAD 檔案",
         inputSchema={"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}),
    Tool(name="geometry_status", description="Geometry 建模器連線狀態", inputSchema={"type": "object", "properties": {}}),
    Tool(name="geometry_close", description="關閉 Geometry 建模器", inputSchema={"type": "object", "properties": {}}),
]

ALL_TOOLS = FLUENT_TOOLS + MECHANICAL_TOOLS + GEOMETRY_TOOLS

# ===================================================================
# GEOMETRY HELPERS
# ===================================================================

def _geom_get_design():
    """返回當前設計物件。依據官方文件：create_design 返回 Design，直接持有。"""
    global _current_design
    if _modeler is None:
        raise RuntimeError("Geometry 未連線，請先執行 geometry_launch")
    if _current_design is None:
        raise RuntimeError("無活躍設計，請先執行 geometry_create_design")
    return _current_design


def _geom_create_cylinder(name: str, radius: float, height: float,
                          cx: float = 0, cy: float = 0, cz: float = 0) -> str:
    from ansys.geometry.core.sketch import Sketch
    from ansys.geometry.core.math import Point2D, Plane, Point3D, Vector3D

    d = _geom_get_design()
    sketch = Sketch()

    # If center is not at origin, translate the sketch plane
    if cx != 0 or cy != 0 or cz != 0:
        sketch.plane = Plane(Point3D([cx, cy, cz]))

    sketch.circle(Point2D([0, 0]), radius)
    body = d.extrude_sketch(name=name, sketch=sketch, distance=height)
    return f"圓柱體 '{name}' 已建立: r={radius}m, h={height}m @ ({cx}, {cy}, {cz})"


def _geom_create_block(name: str, length: float, width: float, height: float,
                       cx: float = 0, cy: float = 0, cz: float = 0) -> str:
    from ansys.geometry.core.sketch import Sketch
    from ansys.geometry.core.math import Point2D, Plane, Point3D, Vector3D

    d = _geom_get_design()
    sketch = Sketch()

    if cx != 0 or cy != 0 or cz != 0:
        sketch.plane = Plane(Point3D([cx, cy, cz]))

    # Draw rectangle centered at origin
    sketch.box(Point2D([0, 0]), length, width)
    body = d.extrude_sketch(name=name, sketch=sketch, distance=height)
    return f"方塊 '{name}' 已建立: {length}x{width}x{height}m @ ({cx}, {cy}, {cz})"


def _geom_create_sphere(name: str, radius: float, cx: float = 0, cy: float = 0, cz: float = 0) -> str:
    """v242: create_sphere 需要 v25.1+, 用 revolve_sketch 半圓旋轉實現"""
    from ansys.geometry.core.sketch import Sketch
    from ansys.geometry.core.math import Point2D, Plane, Point3D, Vector3D

    d = _geom_get_design()
    sketch = Sketch()
    if cx != 0 or cy != 0 or cz != 0:
        sketch.plane = Plane(Point3D([cx, cy, cz]))

    # Draw semicircle profile: center (0, radius), from (0, 0) to (0, 2*radius)
    # Then revolve around Y axis
    sketch.arc(Point2D([0, radius]), Point2D([0, 0]), Point2D([0, 2 * radius]))
    body = d.revolve_sketch(name=name, sketch=sketch, axis="Y", angle=360)
    return f"球體 '{name}' 已建立: r={radius}m @ ({cx}, {cy}, {cz})"


# ===================================================================
# SERVER
# ===================================================================

app = Server("ansys-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return ALL_TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    global _fluent_session, _mechanical_session, _modeler, _current_design
    result = ""

    try:
        # ==================== FLUENT ====================
        if name == "fluent_launch":
            import ansys.fluent.core as pyfluent
            port = arguments.get("port")
            if port:
                connect_timeout = arguments.get("connect_timeout", 30)
                loop = asyncio.get_event_loop()

                def _connect():
                    return pyfluent.connect_to_fluent(
                        ip=arguments.get("ip", "127.0.0.1"),
                        port=int(port),
                        cleanup_on_exit=False,
                        start_transcript=False,
                        allow_remote_host=True,
                        insecure_mode=True,
                        password=arguments.get("password"),
                    )

                try:
                    _fluent_session = await asyncio.wait_for(
                        loop.run_in_executor(None, _connect),
                        timeout=connect_timeout,
                    )
                except asyncio.TimeoutError:
                    raise TimeoutError(
                        f"連線 Fluent ({arguments.get('ip', '127.0.0.1')}:{port}) 超時 "
                        f"({connect_timeout}s)，請檢查 Fluent 例項是否在執行、"
                        f"網路是否可達、防火牆是否放行埠 {port}"
                    )
                ver = _fluent_session.get_fluent_version()
                result = f"已連線 Fluent (埠 {port}, 版本: {ver})"
            else:
                _fluent_session = pyfluent.launch_fluent(
                    precision="double", processor_count=arguments.get("processors", 4),
                    dimension=3, cwd=arguments.get("cwd"))
                result = f"Fluent 已啟動 (版本: {_fluent_session.get_fluent_version()})"

        elif name.startswith("fluent_"):
            # --- MCP-TUI 對映器查詢工具（無需 Fluent 會話） ---
            if name == "fluent_get_script":
                if get_mapping_report:
                    result = get_mapping_report()
                else:
                    result = "⚠ MCP-TUI 對映器未載入（Skill 指令碼目錄不存在）"
            elif name == "fluent_get_mapping_report":
                if get_mapping_report:
                    result = get_mapping_report()
                else:
                    result = "⚠ MCP-TUI 對映器未載入（Skill 指令碼目錄不存在）"
            elif name == "fluent_reset_mapper":
                if reset_mapper:
                    reset_mapper()
                    result = "✓ TUI 對映器已重置"
                else:
                    result = "⚠ MCP-TUI 對映器未載入（Skill 指令碼目錄不存在）"

            elif _fluent_session is None:
                result = "Fluent 未連線，請先執行 fluent_launch"
            else:
                s = _fluent_session
                if name == "fluent_read_case":
                    s.file.read(file_type="case", file_name=os.path.abspath(arguments["file_path"]))
                    result = f"已載入: {arguments['file_path']}"
                elif name == "fluent_read_mesh":
                    s.file.read(file_type="mesh", file_name=os.path.abspath(arguments["file_path"]))
                    result = f"已載入網格: {arguments['file_path']}"
                elif name == "fluent_set_solver":
                    changes = []
                    if "viscous_model" in arguments:
                        s.setup.models.viscous.model = arguments["viscous_model"]; changes.append(f"湍流={arguments['viscous_model']}")
                    if "energy" in arguments:
                        s.setup.models.energy.enabled = arguments["energy"]; changes.append(f"能量={'on' if arguments['energy'] else 'off'}")
                    if "transient" in arguments:
                        s.setup.general.time = "transient" if arguments["transient"] else "steady"; changes.append(f"求解={'瞬態' if arguments['transient'] else '穩態'}")
                    result = f"求解器: {', '.join(changes)}" if changes else "無變更"
                elif name == "fluent_set_boundary":
                    s.setup.boundary_conditions.set_zone_type(zone_name=arguments["zone"], zone_type=arguments["bc_type"])
                    for k, v in arguments.get("params", {}).items():
                        try:
                            s.setup.boundary_conditions.set_zone_property(zone_name=arguments["zone"], property_name=k, value=v)
                        except Exception:
                            s.tui.execute(f"/define/boundary-conditions/set/fluid {arguments['zone']} {k} {v}")
                    result = f"邊界 '{arguments['zone']}' → {arguments['bc_type']}"
                elif name == "fluent_set_material":
                    s.setup.cell_zone_conditions.set_zone_property(zone_name=arguments["zone"], property_name="material", value=arguments["material"])
                    result = f"區域 '{arguments['zone']}' 材料 → {arguments['material']}"
                elif name == "fluent_initialize":
                    m = arguments.get("method", "hybrid")
                    s.solution.initialization.hybrid_initialize() if m == "hybrid" else s.solution.initialization.standard_initialize()
                    result = f"已完成 {m} 初始化"
                elif name == "fluent_iterate":
                    s.solution.run_calculation.iterate(iter_count=arguments["iterations"])
                    result = f"已完成 {arguments['iterations']} 步迭代"
                elif name == "fluent_get_residuals":
                    r = s.solution.monitors.get_residuals()
                    result = "殘差:\n" + "\n".join(f"  {eq}: {v[-1]}" for eq, v in r.items()) if r else "無資料"
                elif name == "fluent_save":
                    prefix = os.path.abspath(arguments["prefix"])
                    s.file.write(file_type="case-data", file_name=prefix)
                    result = f"已儲存: {prefix}.cas/dat"
                elif name == "fluent_tui":
                    cmd = arguments["command"]
                    try:
                        result = s.tui.execute(cmd) or "TUI 已執行"
                    except AttributeError:
                        result = s.scheme_eval.string_eval(f"(ti-menu-load-string \"{cmd}\")") or "TUI 已執行"
                elif name == "fluent_load_udf":
                    src = os.path.abspath(arguments["source_file"])
                    if not os.path.exists(src):
                        result = f"UDF 原始檔不存在: {src}"
                    else:
                        if arguments.get("compile"):
                            # Compiled: /define/user-defined/compiled-functions compile "libname" "src" "" ""
                            cmd = f'/define/user-defined/compiled-functions compile "libudf" "{src}" "" ""'
                            s.scheme_eval.string_eval(f'(ti-menu-load-string "{cmd}")')
                            result = f"UDF 已編譯: {src} (libudf)"
                        else:
                            # Interpreted: single-shot to avoid Windows drive-colon parsing bug
                            cmd = f"/define/user-defined/interpreted-functions {src}"
                            s.scheme_eval.string_eval(f'(ti-menu-load-string "{cmd}")')
                            s.scheme_eval.string_eval('(ti-menu-load-string "")')
                            s.scheme_eval.string_eval('(ti-menu-load-string "")')
                            result = f"UDF 已解釋: {src}"

                elif name == "fluent_hook_udf":
                    zone = arguments["zone_name"]
                    phase = arguments.get("phase_name", "water")
                    profile = arguments["profile_name"]
                    field = arguments.get("momentum_field", "mass_flux")
                    bc = s.setup.boundary_conditions[zone]
                    st = bc.get_state()
                    # Find matching phase key (case-insensitive)
                    phase_keys = list(st.get("phase", {}).keys())
                    matched = [k for k in phase_keys if phase.lower() in str(k).lower()]
                    if not matched:
                        result = f"未找到相 '{phase}'，可用相: {phase_keys}"
                    else:
                        pkey = matched[0]
                        bc.set_state({
                            "phase": {
                                pkey: {
                                    "momentum": {
                                        field: {
                                            "option": "profile",
                                            "profile_name": profile,
                                            "field_name": profile,
                                        }
                                    }
                                }
                            }
                        })
                        result = f"UDF '{profile}' 已掛鉤到 {zone} / {pkey} / {field}"

                elif name == "fluent_list_udfs":
                    zone_arg = arguments.get("zone_name")
                    if zone_arg:
                        bc = s.setup.boundary_conditions[zone_arg]
                        st = bc.get_state()
                        lines = [f"區域 '{zone_arg}' UDF 掛鉤狀態:"]
                        for pk, pv in st.get("phase", {}).items():
                            mom = pv.get("momentum", {})
                            for field_name in ["mass_flux", "mass_flow_rate"]:
                                if field_name in mom:
                                    fv = mom[field_name]
                                    if isinstance(fv, dict) and fv.get("option") == "profile":
                                        lines.append(f"  {pk}/{field_name}: profile='{fv.get('profile_name', '')}'")
                        result = "\n".join(lines) if len(lines) > 1 else f"區域 '{zone_arg}' 無 UDF 掛鉤"
                    else:
                        lines = ["已載入區域及其掛鉤狀態:"]
                        for zone_name in s.setup.boundary_conditions:
                            try:
                                bc = s.setup.boundary_conditions[zone_name]
                                st = bc.get_state()
                                for pk, pv in st.get("phase", {}).items():
                                    mom = pv.get("momentum", {})
                                    for fn in ["mass_flux", "mass_flow_rate"]:
                                        if fn in mom:
                                            fv = mom[fn]
                                            if isinstance(fv, dict) and fv.get("option") == "profile":
                                                lines.append(f"  {zone_name}/{pk}/{fn}: {fv.get('profile_name', 'none')}")
                            except Exception:
                                pass
                        result = "\n".join(lines) if len(lines) > 1 else "無 UDF 掛鉤"

                elif name == "fluent_status":
                    result = f"Fluent 已連線 | 版本: {s.get_fluent_version()}"
                elif name == "fluent_exit":
                    s.exit(); _fluent_session = None; result = "Fluent 已關閉"

                # --- MCP-TUI 自動對映（Skill 聯動） ---
                if map_mcp_call:
                    map_mcp_call(name, arguments)

        # ==================== MECHANICAL ====================
        elif name == "mechanical_launch":
            import ansys.mechanical.core as pymechanical
            port = arguments.get("port")
            if port:
                _mechanical_session = pymechanical.connect_to_mechanical(
                    port=int(port), transport_mode="insecure", loglevel="ERROR",
                    connect_timeout=30, cleanup_on_exit=False,
                )
                result = f"已連線 Mechanical (埠 {port}, 版本: {_mechanical_session.version})"
            else:
                _mechanical_session = pymechanical.launch_mechanical(
                    batch=True, transport_mode="insecure", start_timeout=120, loglevel="ERROR"
                )
                result = f"Mechanical 已啟動 (版本: {_mechanical_session.version})"

        elif name.startswith("mechanical_"):
            if _mechanical_session is None:
                result = "Mechanical 未連線，請先執行 mechanical_launch"
            else:
                m = _mechanical_session
                if name == "mechanical_import":
                    path = os.path.abspath(arguments["file_path"])
                    script = f"ExtAPI.DataModel.Project.Model.Geometry.Import(Path=r'{path}')"
                    m.run_python_script(script)
                    result = f"已匯入: {arguments['file_path']}"
                elif name == "mechanical_set_material":
                    body_name = arguments["body"]
                    material = arguments["material"]
                    script = (
                        "for body in ExtAPI.DataModel.Project.Model.Geometry.Children:\n"
                        f"    if body.Name == '{body_name}': body.Material = '{material}'"
                    )
                    m.run_python_script(script)
                    result = f"已分配材料: {body_name} -> {material}"
                elif name == "mechanical_mesh":
                    script_lines = []
                    if "element_size" in arguments:
                        script_lines.append(
                            f"ExtAPI.DataModel.Project.Model.Mesh.ElementSize = "
                            f"Quantity({arguments['element_size']}, 'mm')"
                        )
                    method = arguments.get("method", "automatic")
                    script_lines.append("ExtAPI.DataModel.Project.Model.Mesh.GenerateMesh()")
                    m.run_python_script("\n".join(script_lines))
                    result = f"網格劃分完成 (method={method})"
                elif name == "mechanical_apply_load":
                    lt = arguments["load_type"]
                    loc = arguments["location"]
                    mag = arguments.get("magnitude")
                    script_lines = [
                        "analysis = ExtAPI.DataModel.Project.Model.Analyses[0]",
                    ]
                    if lt == "force":
                        script_lines.append("obj = analysis.AddForce()")
                    elif lt == "pressure":
                        script_lines.append("obj = analysis.AddPressure()")
                    elif lt == "fixed_support":
                        script_lines.append("obj = analysis.AddFixedSupport()")
                    elif lt == "displacement":
                        script_lines.append("obj = analysis.AddDisplacement()")
                    script_lines.append(
                        f'obj.Location = DataModel.GetObjectsByName("{loc}")[0]'
                    )
                    if mag is not None:
                        script_lines.append(f'obj.Magnitude.Input(Quantity({mag}, "N"))')
                    m.run_python_script("\n".join(script_lines))
                    result = f"已施加 {lt} @ {loc}"
                elif name == "mechanical_solve":
                    m.run_python_script(
                        "ExtAPI.DataModel.Project.Model.Solve(WaitForComplete=True)"
                    )
                    result = "求解完成"
                elif name == "mechanical_get_result":
                    rt = arguments["result_type"]
                    mapping = {
                        "total_deformation": "AddTotalDeformation",
                        "equivalent_stress": "AddEquivalentStress",
                        "equivalent_strain": "AddEquivalentStrain",
                    }
                    if rt in mapping:
                        script = (
                            "sol = ExtAPI.DataModel.Project.Model.Analyses[0].Solution\n"
                            f"obj = sol.{mapping[rt]}()\n"
                            "obj.EvaluateAllResults()\n"
                            "str(obj.Maximum) + '||' + str(obj.Minimum)"
                        )
                        raw = m.run_python_script(script)
                        if "||" in raw:
                            parts = raw.split("||")
                            result = f"{rt}: Max={parts[0]}, Min={parts[1]}"
                        else:
                            result = f"{rt}: {raw}"
                    else:
                        result = f"不支援的結果型別: {rt}"
                elif name == "mechanical_list":
                    what = arguments.get("what", "bodies")
                    if what == "bodies":
                        script = (
                            "bodies = ExtAPI.DataModel.Project.Model.Geometry.Children\n"
                            "';'.join([b.Name for b in bodies])"
                        )
                        raw = m.run_python_script(script)
                        if raw:
                            names = raw.split(";")
                            result = "幾何體:\n" + "\n".join(
                                f"  [{i}] {n}" for i, n in enumerate(names)
                            )
                        else:
                            result = "幾何體: 無"
                    else:
                        script = (
                            "ns = ExtAPI.DataModel.Project.Model.NamedSelections\n"
                            "';'.join([n.Name for n in ns.Children]) if ns else ''"
                        )
                        raw = m.run_python_script(script)
                        if raw:
                            names = raw.split(";")
                            result = "Named Selections:\n" + "\n".join(
                                f"  - {n}" for n in names
                            )
                        else:
                            result = "Named Selections: 無"
                elif name == "mechanical_script":
                    result = m.run_python_script(arguments["script"])
                elif name == "mechanical_status":
                    script = (
                        "bodies = ExtAPI.DataModel.Project.Model.Geometry.Children\n"
                        "mesh = ExtAPI.DataModel.Project.Model.Mesh\n"
                        "nc = int(mesh.Nodes) if mesh.Nodes else 0\n"
                        "ec = int(mesh.Elements) if mesh.Elements else 0\n"
                        "str(len(bodies)) + '|' + "
                        "('meshed' if nc > 0 else 'not meshed') + '|' + "
                        "str(nc) + '|' + str(ec)"
                    )
                    raw = m.run_python_script(script)
                    if raw and "|" in raw:
                        parts = raw.split("|")
                        result = (
                            f"Mechanical 已連線 | 幾何體: {parts[0]} 個 | "
                            f"{parts[1]} | {parts[2]} nodes, {parts[3]} elements"
                        )
                    else:
                        result = f"Mechanical 已連線 | {raw}"
                elif name == "mechanical_exit":
                    m.exit(force=True); _mechanical_session = None; result = "Mechanical 已關閉"

        # ==================== GEOMETRY ====================
        elif name == "geometry_launch":
            from ansys.geometry.core import launch_modeler
            _modeler = launch_modeler(mode="spaceclaim", version=251, timeout=180)
            result = "Geometry 建模器已啟動 (SpaceClaim v251)"

        elif name.startswith("geometry_"):
            if _modeler is None:
                result = "Geometry 未連線，請先執行 geometry_launch"
            else:
                if name == "geometry_create_design":
                    _current_design = _modeler.create_design(arguments["name"])
                    result = f"設計 '{_current_design.name}' 已建立"
                elif name == "geometry_create_cylinder":
                    result = _geom_create_cylinder(
                        name=arguments.get("name", "Cylinder"),
                        radius=arguments.get("radius", 0.005),
                        height=arguments.get("height", 0.01),
                        cx=arguments.get("center_x", 0),
                        cy=arguments.get("center_y", 0),
                        cz=arguments.get("center_z", 0))
                elif name == "geometry_create_block":
                    result = _geom_create_block(
                        name=arguments.get("name", "Block"),
                        length=arguments.get("length", 0.01),
                        width=arguments.get("width", 0.01),
                        height=arguments.get("height", 0.01),
                        cx=arguments.get("center_x", 0),
                        cy=arguments.get("center_y", 0),
                        cz=arguments.get("center_z", 0))
                elif name == "geometry_create_sphere":
                    result = _geom_create_sphere(
                        name=arguments.get("name", "Sphere"),
                        radius=arguments.get("radius", 0.005),
                        cx=arguments.get("center_x", 0),
                        cy=arguments.get("center_y", 0),
                        cz=arguments.get("center_z", 0))
                elif name == "geometry_export":
                    path = os.path.abspath(arguments["file_path"])
                    fmt = arguments.get("format", "step")
                    d = _geom_get_design()
                    # export_to_step/export_to_iges 將引數當作目錄，在內部以設計名命名檔案
                    # 直接傳目錄路徑，檔名自動為 <design_name>.stp
                    out_dir = os.path.dirname(path)
                    if not out_dir:
                        out_dir = "."
                    if fmt == "step":
                        actual = d.export_to_step(out_dir)
                    else:
                        actual = d.export_to_iges(out_dir)
                    result = f"已匯出 ({fmt}): {actual}"
                elif name == "geometry_list_bodies":
                    d = _geom_get_design()
                    bodies = d.bodies
                    if bodies:
                        lines = [f"  [{i}] {b.name} (id={b.id})" for i, b in enumerate(bodies)]
                        result = f"幾何體 ({len(bodies)}):\n" + "\n".join(lines)
                    else:
                        result = "當前設計無幾何體"
                elif name == "geometry_import_file":
                    path = os.path.abspath(arguments["file_path"])
                    if not os.path.exists(path):
                        result = f"檔案不存在: {path}"
                    else:
                        d = _geom_get_design()
                        d.insert_file(path)
                        result = f"已匯入: {path}"
                elif name == "geometry_status":
                    result = "Geometry 建模器已連線 (Discovery v242)"
                elif name == "geometry_close":
                    _modeler.close()
                    _modeler = None
                    result = "Geometry 建模器已關閉"

        else:
            result = f"未知工具: {name}"

    except Exception as exc:
        logger.exception(f"Tool [{name}] failed")
        result = f"錯誤 [{name}]: {exc}"

    return [TextContent(type="text", text=result)]


async def main():
    logger.info(f"ANSYS MCP Server — Fluent({len(FLUENT_TOOLS)}) + Mechanical({len(MECHANICAL_TOOLS)}) + Geometry({len(GEOMETRY_TOOLS)})")
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
