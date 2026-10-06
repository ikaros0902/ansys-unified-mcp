#!/usr/bin/env python3
"""ANSYS MCP Server — Fluent call_tool 分派實作。

驅動層: Fluent → ansys-fluent-core (PyFluent) gRPC

此模組由 drivers/sim_impl.py 拆分而來（原為 geometry + fluent 共用的單一檔案），
現歸位至 products/fluent/，僅保留 Fluent 相關的工具定義、全域 session 與分派邏輯。
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Callable

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

from ansys_unified_mcp.core.sessions import registry

# ---------------------------------------------------------------------------
# Global sessions (backed by SessionRegistry)
# ---------------------------------------------------------------------------
_fluent_session = None

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

ALL_TOOLS = FLUENT_TOOLS


async def call_tool(name: str, arguments: dict[str, Any],
                    progress: Callable[[str], None] | None = None) -> list[TextContent]:
    """Plain dispatcher invoked directly by the thin tools/ wrappers (Fluent only).

    progress: 保留與 geometry 版本一致的簽名，但 Fluent 分支目前不使用階段進度回呼。
    """
    global _fluent_session
    result = ""

    try:
        # ==================== FLUENT ====================
        if name == "fluent_launch":
            import ansys.fluent.core as pyfluent
            port = arguments.get("port")
            loop = asyncio.get_event_loop()
            if port:
                connect_timeout = arguments.get("connect_timeout", 30)

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
                registry.put("fluent", str(port), _fluent_session)
                result = f"已連線 Fluent (埠 {port}, 版本: {ver})"
            else:
                _fluent_session = await loop.run_in_executor(
                    None,
                    lambda: pyfluent.launch_fluent(
                        precision="double", processor_count=arguments.get("processors", 4),
                        dimension=3, cwd=arguments.get("cwd")
                    )
                )
                registry.put("fluent", "default", _fluent_session)
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
                    s.exit(); _fluent_session = None; registry.drop("fluent"); result = "Fluent 已關閉"

                # --- MCP-TUI 自動對映（Skill 聯動） ---
                if map_mcp_call:
                    map_mcp_call(name, arguments)

        else:
            result = f"未知工具: {name}"

    except Exception as exc:
        logger.exception(f"Tool [{name}] failed")
        result = f"錯誤 [{name}]: {exc}"

    return [TextContent(type="text", text=result)]
