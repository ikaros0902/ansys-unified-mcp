#!/usr/bin/env python3
"""ANSYS MCP Server — Fluent + Mechanical + Geometry (v242).

驅動層:
  - Fluent       → ansys-fluent-core (PyFluent) gRPC
  - Mechanical   → ansys-mechanical-core (PyMechanical) gRPC
  - Geometry     → ansys-geometry-core (PyAnsys Geometry) gRPC
"""

import asyncio
import logging
import math
import os
import sys
import threading
import time
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

GEOMETRY_TOOLS = [
    Tool(name="geometry_launch", description="啟動 Geometry 建模器或連線現有 SpaceClaim 實例",
         inputSchema={"type": "object", "properties": {
             "port": {"type": "integer", "description": "連線已啟動 SpaceClaim 的 gRPC 埠號，不填則自動掃描 50051-50055 尋找已運行實例"},
             "host": {"type": "string", "default": "localhost", "description": "SpaceClaim 主機地址"},
             "transport_mode": {"type": "string", "enum": ["wnua", "insecure", "uds"], "default": "wnua", "description": "gRPC 傳輸模式（Windows 預設 wnua，Linux/Docker 預設 insecure）"},
             "connect_timeout": {"type": "integer", "default": 15, "description": "連線超時秒數，預設15秒"}}}),
    Tool(name="geometry_create_design", description="建立新的幾何設計（⚠️ 注意：若 SpaceClaim 中已有開啟的設計，請勿調用此工具，直接調用 create_block 等即可在當前設計中建模）",
         inputSchema={"type": "object", "properties": {"name": {"type": "string", "default": "Design"}},
             "required": ["name"]}),
    Tool(name="geometry_create_block", description="建立立方體（⚠️ 注意：所有尺寸單位皆為【公尺 m】！若使用者輸入 mm，請務必先除以 1000 轉換為公尺，例如 50mm 必須輸入 0.05）",
         inputSchema={"type": "object", "properties": {
             "name": {"type": "string", "default": "Block", "description": "方塊名稱"},
             "length": {"type": "number", "default": 0.01, "description": "長度（單位：公尺 m。例：50mm 請傳入 0.05）"},
             "width": {"type": "number", "default": 0.01, "description": "寬度（單位：公尺 m。例：30mm 請傳入 0.03）"},
             "height": {"type": "number", "default": 0.01, "description": "高度（單位：公尺 m。例：20mm 請傳入 0.02）"},
             "center_x": {"type": "number", "default": 0, "description": "中心 X 座標（單位：公尺 m）"},
             "center_y": {"type": "number", "default": 0, "description": "中心 Y 座標（單位：公尺 m）"},
             "center_z": {"type": "number", "default": 0, "description": "中心 Z 座標（單位：公尺 m）"}},
             "required": ["name"]}),
    Tool(name="geometry_create_cylinder", description="建立圓柱體（⚠️ 注意：所有尺寸單位皆為【公尺 m】！若使用者輸入 mm，請務必先除以 1000 轉換為公尺，例如 10mm 必須輸入 0.01）",
         inputSchema={"type": "object", "properties": {
             "name": {"type": "string", "default": "Cylinder", "description": "圓柱體名稱"},
             "radius": {"type": "number", "default": 0.005, "description": "半徑（單位：公尺 m。例：5mm 請傳入 0.005）"},
             "height": {"type": "number", "default": 0.01, "description": "高度（單位：公尺 m。例：20mm 請傳入 0.02）"},
             "center_x": {"type": "number", "default": 0, "description": "中心 X 座標（單位：公尺 m）"},
             "center_y": {"type": "number", "default": 0, "description": "中心 Y 座標（單位：公尺 m）"},
             "center_z": {"type": "number", "default": 0, "description": "中心 Z 座標（單位：公尺 m）"}},
             "required": ["name"]}),
    Tool(name="geometry_create_sphere", description="建立球體（⚠️ 注意：尺寸單位為【公尺 m】！例：半徑 10mm 請輸入 0.01）",
         inputSchema={"type": "object", "properties": {
             "name": {"type": "string", "default": "Sphere", "description": "球體名稱"},
             "radius": {"type": "number", "default": 0.005, "description": "半徑（單位：公尺 m。例：5mm 請傳入 0.005）"},
             "center_x": {"type": "number", "default": 0, "description": "中心 X 座標（單位：公尺 m）"},
             "center_y": {"type": "number", "default": 0, "description": "中心 Y 座標（單位：公尺 m）"},
             "center_z": {"type": "number", "default": 0, "description": "中心 Z 座標（單位：公尺 m）"}},
             "required": ["name"]}),
    Tool(name="geometry_export", description="匯出幾何為 STEP/IGES 格式",
         inputSchema={"type": "object", "properties": {
             "file_path": {"type": "string"},
             "format": {"type": "string", "enum": ["step", "iges"], "default": "step"}},
             "required": ["file_path"]}),
    Tool(name="geometry_sketch_and_extrude", description="於指定基準面繪製 2D 點陣列草圖（支援折線 polyline 或 NURBS 樣條曲線 spline 插值）並拉伸成 3D 實體（⚠️ 注意：所有座標與尺寸單位皆為【公尺 m】！若輸入為 mm 請除以 1000）",
         inputSchema={"type": "object", "properties": {
             "name": {"type": "string", "default": "ExtrudedBody", "description": "生成實體之名稱"},
             "points": {"type": "array", "items": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2}, "description": "2D 點陣列座標 [[x1, y1], [x2, y2], ...]（單位：公尺 m）"},
             "plane": {"type": "string", "enum": ["XY", "XZ", "YZ"], "default": "XY", "description": "草圖基準面"},
             "curve_type": {"type": "string", "enum": ["spline", "polyline"], "default": "spline", "description": "曲線連線類型"},
             "distance": {"type": "number", "default": 0.01, "description": "拉伸距離（單位：公尺 m）"},
             "is_closed": {"type": "boolean", "default": True, "description": "是否閉合草圖"},
             "extrude_direction": {"type": "string", "enum": ["+", "-"], "default": "+", "description": "拉伸方向"}},
             "required": ["name", "points"]}),
    Tool(name="geometry_create_enclosure", description="為指定標的實體幾何自動生成外部流體包覆域 (Enclosure) 並執行布林相減扣除標的本體（⚠️ 注意：外擴延伸尺寸單位皆為【公尺 m】！若輸入為 mm 請除以 1000）",
         inputSchema={"type": "object", "properties": {
             "target_body_name": {"type": "string", "description": "標的固體幾何名稱"},
             "enclosure_name": {"type": "string", "default": "FluidDomain", "description": "流體包覆域名稱"},
             "shape": {"type": "string", "enum": ["box", "cylinder"], "default": "box", "description": "流體外流域形狀"},
             "cushion_x_neg": {"type": "number", "default": 0.05, "description": "-X 方向外擴延伸距離（公尺 m）"},
             "cushion_x_pos": {"type": "number", "default": 0.1, "description": "+X 方向外擴延伸距離（公尺 m）"},
             "cushion_y_neg": {"type": "number", "default": 0.05, "description": "-Y 方向外擴延伸距離（公尺 m）"},
             "cushion_y_pos": {"type": "number", "default": 0.05, "description": "+Y 方向外擴延伸距離（公尺 m）"},
             "cushion_z_neg": {"type": "number", "default": 0.05, "description": "-Z 方向外擴延伸距離（公尺 m）"},
             "cushion_z_pos": {"type": "number", "default": 0.05, "description": "+Z 方向外擴延伸距離（公尺 m）"},
             "keep_target_body": {"type": "boolean", "default": False, "description": "布林相減後是否保留標的本體"}},
             "required": ["target_body_name"]}),
    Tool(name="geometry_simplify_ram", description="【呼叫前必須先向使用者索取主機板、RAM、socket 三個 body 名稱，不可猜測或自行從 body 清單推斷】將單一 RAM 卡 + 其 socket 簡化為一座落於主機板頂面的方塊，並在方塊底面（板接合面）建立 named selection。高度軸為 Y；footprint(X-Z)=RAM 與 socket 合併包圍盒；底=主機板頂面，頂=RAM 頂。原始 body 保留不動。",
         inputSchema={"type": "object", "properties": {
             "motherboard": {"type": "string", "description": "主機板 body 名稱（其頂面即方塊底面），例 'JVPCB1074973E'"},
             "ram": {"type": "string", "description": "RAM 卡 body 名稱，例 'DIMM_DDR5_EGS'"},
             "socket": {"type": "string", "description": "RAM socket body 名稱，例 'J33'"},
             "result_name": {"type": "string", "default": "RAM_simplified", "description": "生成簡化方塊 body 名稱"},
             "named_selection": {"type": "string", "default": "ram_bottom", "description": "方塊底面接合面的 named selection 名稱"},
             "move_to_component": {"type": "boolean", "default": True, "description": "是否將簡化方塊移入新 component（名稱見 component_name）"},
             "component_name": {"type": "string", "default": "RAM_simplified", "description": "move_to_component 時新建的 component 名稱"},
             "hide_source": {"type": "boolean", "default": True, "description": "是否抑制 (suppress) 原始 RAM 與 socket body，使其在下游網格/求解被排除"}},
             "required": ["motherboard", "ram", "socket"]}),
    Tool(name="geometry_simplify_ram_batch", description="【呼叫前必須先向使用者索取主機板、RAM、socket 三個 body 名稱，不可猜測或自行從 body 清單推斷】批次簡化所有同名 RAM+socket 配對（依 X 中心位置自動就近配對）。每對成為一座落於主機板頂面的方塊，各自建立底面 named selection，依 X 順序編號 <result_prefix>_01、<ns_prefix>_01…。適用於多條相同 DIMM/socket 陣列。原始 body 保留不動。",
         inputSchema={"type": "object", "properties": {
             "motherboard": {"type": "string", "description": "主機板 body 名稱（頂面=各方塊底面）"},
             "ram": {"type": "string", "description": "RAM 卡 body 名稱（陣列中重複出現）"},
             "socket": {"type": "string", "description": "socket body 名稱（陣列中重複出現）"},
             "result_prefix": {"type": "string", "default": "RAM_simplified", "description": "方塊 body 名稱前綴（自動編號）"},
             "ns_prefix": {"type": "string", "default": "ram_bottom", "description": "底面 named selection 名稱前綴（自動編號）"},
             "tol_mm": {"type": "number", "default": 2.0, "description": "RAM 與 socket 視為一對的最大 X 中心距離（單位：毫米 mm）"},
             "move_to_component": {"type": "boolean", "default": True, "description": "是否將所有簡化方塊移入同一新 component（名稱見 component_name）"},
             "component_name": {"type": "string", "default": "RAM_simplified", "description": "move_to_component 時新建的 component 名稱"},
             "hide_source": {"type": "boolean", "default": True, "description": "是否抑制 (suppress) 配對成功的原始 RAM 與 socket body，使其在下游網格/求解被排除"}},
             "required": ["motherboard", "ram", "socket"]}),
    Tool(name="geometry_simplify_heatsink", description="散熱片 (heatsink) 簡化為凸字形方塊組（擠型/壓鑄/折片/針狀鰭片，單一或多 body 組件皆可）：底板（包圍盒 X-Z，鎖孔所在板底→鰭片根部）＋上凸（最大一排鰭片範圍，鰭片根部→鰭片頂）＋下凸（主接合底面範圍，接觸面→板底），無階梯、無圓角，螺絲/彈簧/推銷不保留；鎖孔（原始完整圓周的 Y 向挖孔）以 Y 向直圓柱貫穿；主接合底面建立 named selection。量測原始體積，以常見散熱片密度（預設鋁 2700 kg/m³，可逐 body 指定）估算質量，於質量守恆下反推簡化體應設定的等效密度（kg/m³），附加於新 body 名稱後綴 _rho<整數>。結果建於原始 body 所屬 component（共用 master 的各 instance 皆會出現），原始 body 預設保留。高度軸為 world Y。",
         inputSchema={"type": "object", "properties": {
             "source": {"type": "string", "description": "散熱片主 body 名稱（決定結果命名與所屬 component），例 'ENDURANCE-POWER-BRICK-HS-241018'"},
             "result_name": {"type": "string", "description": "簡化體 body 名稱（不填則為 <source>_sim，再附加 _rho<密度>；多組時再加 _01、_02…）"},
             "density": {"type": "number", "description": "散熱片材料密度 (kg/m³)，不填則依 material 預設"},
             "material": {"type": "string", "enum": ["aluminum", "aluminum_6063", "copper", "copper_c110"], "default": "aluminum", "description": "常見散熱片材料（決定預設密度，aluminum=2700, copper=8960 kg/m³）"},
             "keep_source": {"type": "boolean", "default": True, "description": "是否保留原始散熱片 body（預設保留）"},
             "named_selection": {"type": "string", "default": "hs_bottom", "description": "簡化體主接合底面的 named selection 名稱（多組時加 _01、_02…）"},
             "name_density_suffix": {"type": "boolean", "default": True, "description": "是否將反推等效密度（kg/m³ 取整數）附加於新 body 名稱後綴（_rho<值>）"},
             "hole_min_dia_mm": {"type": "number", "default": 2.5, "description": "視為鎖孔的最小孔喉直徑（mm）。鎖孔 = 底板上完整圓周、開口於鰭片根部（容許倒角）的內凹 Y 向圓柱，同軸多段取最小半徑（孔喉）；小於門檻者忽略。"},
             "extra_sources": {"type": "array", "items": {"type": "string"}, "description": "多 body 散熱片：額外併入的 body 名稱或 glob（例 ['ICX_HS_1U_FIN_*', '1U_CUBASE']），只比對主 body 同一 component instance 內的實體 body；螺絲/彈簧等不要列入"},
             "body_densities": {"type": "object", "additionalProperties": {"type": ["number", "string"]}, "description": "逐 body 密度：{名稱或 glob: kg/m³ 或材料名}，例 {'1U_CUBASE': 'copper'}；未列者用 density/material"},
             "all_instances": {"type": "boolean", "default": False, "description": "是否處理所有含 source 的 component（同 master 只處理一次）；預設只處理第一個"},
             "contact_body": {"type": "string", "description": "接觸體 body 名稱或 glob（須為 source 或 extra_sources 之一），例 CPU 散熱片的銅底 '1U_CUBASE'：下凸＝其範圍與厚度，底面 named selection 只含其底面。銅底與框架底面齊平時使用"},
             "fin_box": {"type": "string", "enum": ["largest", "all"], "default": "largest", "description": "上凸範圍：largest＝面積最大的一排鰭片；all＝所有鰭片外框（十字形等多排鰭片配置）"},
             "hole_select": {"type": "string", "enum": ["screw", "outer", "all"], "default": "screw", "description": "鎖孔篩選模式：screw（預設）＝只保留真正的外側螺絲鎖孔（優先取同軸有螺絲/彈簧者，否則取外側徑向最遠的一圈），排除中央定位銷孔；outer＝純依距中心徑向距離取外側一圈；all＝保留偵測到的所有孔（舊行為）"},
             "timeout_s": {"type": "number", "default": 600, "description": "整體逾時秒數；超過即在下一個階段邊界中止並清除暫存幾何（預設 600s）"},
             "diagnose_only": {"type": "boolean", "default": False, "description": "僅做幾何偵測與孔診斷（不建立簡化方塊、不做布林運算，秒級回傳）；用於排查孔偵測問題"}},
             "required": ["source"]}),
    Tool(name="geometry_midsurface", description="對 SpaceClaim 中目前「已選取」的 body 批次建立中曲面 (midsurface)。呼叫前請先在 SpaceClaim 視窗選取欲抽中面的鈑金/薄殼 body。採面積最大優先的對向面配對 + 動態相切鏈補強（複雜件強制加入相切面以對抗壓折邊遺失）；可選鈑金件判斷與抽中面後隱藏原始 body。單位：厚度為 mm。",
         inputSchema={"type": "object", "properties": {
             "max_thickness_mm": {"type": "number", "default": 6.0, "description": "判定為薄件/對向面的最大板厚（單位：mm）；對向面間距大於 0 且不超過此值才視為配對"},
             "main_surface_ratio": {"type": "number", "default": 0.7, "description": "鈑金件判斷：主要對向面（含相切鏈）面積占整體面積的最小比例"},
             "area_difference_ratio": {"type": "number", "default": 0.1, "description": "一對對向面可接受的相對面積差上限（0~1）"},
             "complex_area_diff": {"type": "number", "default": 0.05, "description": "面積差超過此值即視為複雜件，改用強制相切鏈模式建立中面"},
             "enable_sheet_metal_check": {"type": "boolean", "default": True, "description": "是否啟用鈑金件判斷（未通過者略過）"},
             "hide_source_bodies": {"type": "boolean", "default": True, "description": "成功抽中面後是否隱藏原始實體 body"}},
             "required": []}),
    Tool(name="geometry_create_hole_groups", description="對 SpaceClaim 中目前「已選取」的 body/edge 偵測圓孔（整圓與半圓）並建立 named selection 群組，再對同軸、距離在門檻內的孔兩兩配對建立 RM 連接群組 (RM group)。呼叫前請先在 SpaceClaim 視窗選取目標。可選同件/跨件配對策略與距離分級（Near/Medium/Far）。單位：直徑與距離皆為 mm。",
         inputSchema={"type": "object", "properties": {
             "diameter_min_mm": {"type": "number", "default": 2.0, "description": "偵測圓孔的最小直徑（mm）"},
             "diameter_max_mm": {"type": "number", "default": 20.0, "description": "偵測圓孔的最大直徑（mm）"},
             "mode": {"type": "integer", "enum": [0, 1], "default": 0, "description": "0=僅圓孔邊（自動偵測整圓/半圓）；1=直接使用選取的任意邊"},
             "pairing_strategy": {"type": "string", "enum": ["Ignore Component", "Within Component"], "default": "Ignore Component", "description": "配對策略：Ignore Component=忽略元件階層（含跨元件）；Within Component=僅同元件內"},
             "distance_min_mm": {"type": "number", "default": 0.0, "description": "兩孔配對的最小間距（mm）"},
             "distance_max_mm": {"type": "number", "default": 10.0, "description": "兩孔配對的最大間距（mm）"},
             "holes_axis_dist_max_mm": {"type": "number", "default": 1.0, "description": "兩孔軸線間最大偏移距離（mm），超過視為不同軸"},
             "deg_max_circles": {"type": "number", "default": 10.0, "description": "非圓曲線孔配對時，兩面法向最大夾角（度）"},
             "grp_name_create": {"type": "string", "default": "Scr_AllHoles", "description": "孔群組 named selection 名稱前綴"},
             "index_grp_start": {"type": "integer", "default": 1, "description": "孔群組名稱起始索引"},
             "rm_grp_create": {"type": "boolean", "default": True, "description": "是否執行孔配對並建立 RM 連接群組"},
             "rm_grp_name_create": {"type": "string", "default": "Scr_RMgrp", "description": "RM 連接群組 named selection 名稱前綴"},
             "index_rm_start": {"type": "integer", "default": 1, "description": "RM 群組名稱起始索引"},
             "grp_name_not_go": {"type": "string", "default": "NOTGoConnections", "description": "排除清單群組名稱：其成員 edge 不參與配對"},
             "enable_distance_grouping": {"type": "boolean", "default": False, "description": "是否依配對間距分級（Near/Medium/Far）為 RM 群組加後綴"},
             "distance_level1_mm": {"type": "number", "default": 5.0, "description": "距離分級門檻 1（mm）：<= 此值為 Near"},
             "distance_level2_mm": {"type": "number", "default": 20.0, "description": "距離分級門檻 2（mm）：<= 此值為 Medium，否則 Far"}},
             "required": []}),
    Tool(name="geometry_screenshot", description="將 SpaceClaim 3D 視窗出圖為影像檔（PNG/JPG/BMP/TIFF/GIF）。透過伺服器端腳本呼叫 Window.Export；可選標準視角、僅顯示指定 body、ZoomExtents 全景縮放，出圖後還原原視角與可見性。需 SpaceClaim 有作用中的 GUI 視窗。",
         inputSchema={"type": "object", "properties": {
             "file_path": {"type": "string", "description": "輸出影像路徑（相對路徑會轉為絕對；目錄不存在會自動建立；無副檔名則依格式補上）"},
             "image_format": {"type": "string", "enum": ["png", "jpg", "jpeg", "bmp", "tif", "tiff", "gif"], "description": "影像格式；省略則依副檔名推斷（無副檔名則 png），與副檔名不一致會報錯"},
             "fit": {"type": "boolean", "default": True, "description": "截圖前是否 ZoomExtents 全景縮放以涵蓋整個模型"},
             "view": {"type": "string", "enum": ["current", "iso", "front", "back", "top", "bottom", "left", "right"], "default": "current", "description": "截圖視角（Y 朝上座標系）；current 為目前視角"},
             "bodies": {"type": "array", "items": {"type": "string"}, "description": "僅顯示這些 body（依名稱），其他暫時隱藏，截圖後還原"}},
             "required": ["file_path"]}),
    Tool(name="geometry_list_bodies", description="列出當前設計中的所有幾何體", inputSchema={"type": "object", "properties": {}}),
    Tool(name="geometry_import_file", description="匯入 CAD 檔案",
         inputSchema={"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}),
    Tool(name="geometry_status", description="Geometry 建模器連線狀態", inputSchema={"type": "object", "properties": {}}),
    Tool(name="geometry_close", description="關閉 Geometry 建模器", inputSchema={"type": "object", "properties": {}}),
]

ALL_TOOLS = FLUENT_TOOLS + GEOMETRY_TOOLS

# ===================================================================
# GEOMETRY HELPERS
# ===================================================================

def _geom_get_design():
    """返回當前設計物件。若 _current_design 為 None，自動調用 read_existing_design() 取得 SpaceClaim 當前視窗設計。"""
    global _current_design
    if _modeler is None:
        raise RuntimeError("Geometry 未連線，請先執行 geometry_launch")
    if _current_design is None:
        try:
            _current_design = _modeler.read_existing_design()
            logger.info(f"自動讀取現有設計成功: {_current_design.name}")
        except Exception as e:
            logger.warning(f"自動讀取現有設計失敗: {e}")
            try:
                _current_design = _modeler.get_active_design()
            except Exception:
                pass
    if _current_design is None:
        raise RuntimeError("無法取得 SpaceClaim 當前作用中設計，請確認 SpaceClaim 視窗中已開啟設計。")
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


def _geom_sketch_and_extrude(name: str, points: list[list[float]], plane: str = "XY",
                             curve_type: str = "spline", distance: float = 0.01,
                             is_closed: bool = True, extrude_direction: str = "+") -> str:
    from ansys.geometry.core.sketch import Sketch
    from ansys.geometry.core.math import Point2D, Plane

    d = _geom_get_design()
    plane_map = {
        "XY": Plane.xy(),
        "XZ": Plane.xz(),
        "YZ": Plane.yz()
    }
    sketch_plane = plane_map.get(plane.upper(), Plane.xy())
    sketch = Sketch(plane=sketch_plane)

    pts_2d = [Point2D([p[0], p[1]]) for p in points]
    if len(pts_2d) < 2:
        return "錯誤：點陣列至少需包含 2 個點。"

    if curve_type.lower() == "spline":
        sketch.nurbs_from_2d_points(pts_2d, tag=f"{name}_spline")
        if is_closed:
            sketch.segment(pts_2d[-1], pts_2d[0])
    else:
        for i in range(len(pts_2d) - 1):
            sketch.segment(pts_2d[i], pts_2d[i + 1])
        if is_closed:
            sketch.segment(pts_2d[-1], pts_2d[0])

    body = d.extrude_sketch(name=name, sketch=sketch, distance=distance, direction=extrude_direction)
    return f"草圖實體 '{name}' 已成功拉伸建立: 點數={len(points)}, 曲線={curve_type}, 距離={distance}m, 基準面={plane}"


def _geom_create_enclosure(target_body_name: str, enclosure_name: str = "FluidDomain",
                           shape: str = "box", cushion_x_neg: float = 0.05,
                           cushion_x_pos: float = 0.1, cushion_y_neg: float = 0.05,
                           cushion_y_pos: float = 0.05, cushion_z_neg: float = 0.05,
                           cushion_z_pos: float = 0.05, keep_target_body: bool = False) -> str:
    d = _geom_get_design()
    target_body = None
    for b in d.bodies:
        if b.name == target_body_name or b.id == target_body_name:
            target_body = b
            break

    if target_body is None:
        all_names = [b.name for b in d.bodies]
        return f"錯誤：找不到標的實體 '{target_body_name}'。當前設計實體清單: {all_names}"

    # ansys-geometry-core 0.18.1：BoundingBox 的角點屬性為 min_corner / max_corner
    # （非 min_point / max_point），且 Point3D 的 .x/.y/.z 為 pint.Quantity（公尺），
    # 需以 m_as(UNITS.m) 取為純數值才能參與算術。
    from ansys.geometry.core.misc import UNITS

    bbox = target_body.bounding_box
    mn, mx = bbox.min_corner, bbox.max_corner
    min_x, min_y, min_z = mn.x.m_as(UNITS.m), mn.y.m_as(UNITS.m), mn.z.m_as(UNITS.m)
    max_x, max_y, max_z = mx.x.m_as(UNITS.m), mx.y.m_as(UNITS.m), mx.z.m_as(UNITS.m)

    enc_min_x = min_x - cushion_x_neg
    enc_max_x = max_x + cushion_x_pos
    enc_min_y = min_y - cushion_y_neg
    enc_max_y = max_y + cushion_y_pos
    enc_min_z = min_z - cushion_z_neg
    enc_max_z = max_z + cushion_z_pos

    len_x = enc_max_x - enc_min_x
    len_y = enc_max_y - enc_min_y
    len_z = enc_max_z - enc_min_z

    # 注意：Design/Component.create_block 需 Ansys >= 27.1，v251 (25.1) 不支援。
    # 改用與本模組其他建盒工具一致的 sketch + extrude 路徑（_make_box_from_bbox），
    # 在 25.1 可用。盒範圍即外擴後的 [lo, hi]（公尺）。
    enc_body = _make_box_from_bbox(
        d,
        enclosure_name,
        (enc_min_x, enc_min_y, enc_min_z),
        (enc_max_x, enc_max_y, enc_max_z),
    )

    # subtract 為就地操作（回傳 None），直接在 enc_body 上扣除標的本體。
    enc_body.subtract(target_body, keep_other=keep_target_body)
    return (f"流體外流域 '{enclosure_name}' 已建立並完成布林扣除: 尺寸={len_x:.4f}x{len_y:.4f}x{len_z:.4f}m, "
            f"扣除標的='{target_body_name}', 保留原固體={keep_target_body}")


# ===================================================================
# GEOMETRY HELPERS — RAM / 元件簡化（移植自 spaceclaim_mcp.py）
# ===================================================================
# 單位約定：PyAnsys Geometry 內部一律以【公尺 m】運算（Point3D/Distance 預設 m）。
# BoundingBox.min_corner / max_corner 為 Point3D，其 .x/.y/.z 為 pint.Quantity。
# 高度軸固定為 Y（PCB 板面法向），footprint 為 X-Z 平面，與 PCB 熱/結構簡化慣例一致。

def _find_bodies_by_name(name: str):
    """回傳當前設計中（遞迴）所有名稱完全相符的 body。"""
    d = _geom_get_design()
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

    y_bottom = mb_top_y        # 主機板頂面（基座底）
    y_mid = sock_hi[1]         # socket 頂（基座/凸柱交界）
    y_top = ram_hi[1]          # RAM 頂（凸柱頂）
    if y_top <= y_bottom:
        raise ValueError(
            f"RAM 頂 (Y={y_top*1000:.3f}mm) 未高於主機板頂面 (Y={y_bottom*1000:.3f}mm)；"
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


def _hide_source_body(body):
    """抑制 (suppress) 原始實體 body，使其在下游（網格/求解）被排除。

    PyAnsys Geometry Python 端無可靠的「視覺隱藏」API；set_suppressed(True)
    是把原始實體排除於下游的正確語意（SpaceClaim 樹中會標為抑制）。
    回傳是否成功。
    """
    try:
        if body is not None and body.is_alive:
            body.set_suppressed(True)
            return True
    except Exception as e:
        logger.warning(f"抑制原始 body '{getattr(body, 'name', '?')}' 失敗: {e}")
    return False


def _geom_simplify_ram(motherboard: str, ram: str, socket: str,
                       result_name: str = "RAM_simplified",
                       named_selection: str = "ram_bottom",
                       move_to_component: bool = True,
                       component_name: str = "RAM_simplified",
                       hide_source: bool = True) -> str:
    """將單一 RAM 卡 + 其 socket 簡化為一座落於主機板上的方塊。"""
    design = _geom_get_design()

    def _first(nm):
        matches = _find_bodies_by_name(nm)
        if not matches:
            raise ValueError(f"找不到名為 '{nm}' 的 body（請先 geometry_list_bodies 確認名稱）。")
        return matches[0]

    ram_b = _first(ram)
    sock_b = _first(socket)
    mb_top_y = _bbox_m(_first(motherboard))[1][1]  # 主機板 max Y

    target = design.add_component(component_name) if move_to_component else None
    info = _build_ram_block(design, ram_b, sock_b, mb_top_y, result_name, named_selection, target=target)

    hidden = 0
    if hide_source:
        hidden += 1 if _hide_source_body(ram_b) else 0
        hidden += 1 if _hide_source_body(sock_b) else 0

    comp_note = f"（已移入新 component '{component_name}'）" if move_to_component else ""
    hide_note = f"，已抑制 {hidden} 個原始實體" if hide_source else ""
    shape_note = "凸字形（socket 寬基座 + RAM 窄凸柱）" if info.get("shape") == "convex" else "單一方塊（退化）"
    tier_line = (
        f"  下段基座 (mm): {info['base_size_mm']}  上段凸柱 (mm): {info['top_size_mm']}\n"
        if info.get("shape") == "convex" else ""
    )
    return (
        f"✓ RAM 簡化完成：'{result_name}' 座落於 '{motherboard}' 頂面，形狀={shape_note}{comp_note}{hide_note}。\n"
        f"  合併來源: {ram} + {socket}\n"
        f"  整體尺寸 (mm): {info['block_size_mm']}  min={info['block_min_mm']} max={info['block_max_mm']}\n"
        f"{tier_line}"
        f"  主機板頂面 Y={_mm(mb_top_y)}mm，RAM 頂 Y={info['block_max_mm'][1]}mm\n"
        f"  底面 named selection: {info['named_selection']} (created={info['named_selection_created']})"
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


def _geom_simplify_ram_batch(motherboard: str, ram: str, socket: str,
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
    design = _geom_get_design()

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
    hidden = 0
    for idx, (_x, ram_b, sock_b) in enumerate(pairs, start=1):
        rn = f"{result_prefix}_{idx:02d}"
        ns = f"{ns_prefix}_{idx:02d}"
        try:
            results.append(_build_ram_block(design, ram_b, sock_b, mb_top_y, rn, ns, target=target))
            if hide_source:
                hidden += 1 if _hide_source_body(ram_b) else 0
                hidden += 1 if _hide_source_body(sock_b) else 0
        except Exception as e:
            errors.append({"index": idx, "result_body": rn, "error": str(e)})

    ns_count = sum(1 for r in results if r["named_selection_created"])
    comp_note = f"，簡化方塊置於新 component '{component_name}'" if move_to_component else ""
    lines = [
        f"✓ RAM 批次簡化完成（主機板 '{motherboard}' 頂面 Y={_mm(mb_top_y)}mm{comp_note}）",
        f"  RAM 數={len(rams)}, socket 數={len(sockets)}, 配對={len(pairs)}, "
        f"建塊={len(results)}, 建立 NS={ns_count}"
        + (f", 抑制原始實體={hidden}" if hide_source else ""),
    ]
    for r in results:
        lines.append(f"  - {r['result_body']}: shape={r.get('shape', 'box')} size(mm)={r['block_size_mm']} NS={r['named_selection']}")
    if errors:
        lines.append(f"  ⚠ {len(errors)} 個配對失敗:")
        for e in errors:
            lines.append(f"    - {e['result_body']}: {e['error']}")
    return "\n".join(lines)


# ===================================================================
# GEOMETRY HELPERS — Heatsink 簡化（等效密度反推）
# ===================================================================
# 適用：擠型/壓鑄/折片(folded fin)/針狀(pin fin)散熱片，單一 body 或多 body 組件皆可。
# 思路：散熱片 = 底板 + 密集鰭片 + 鎖孔（常附彈簧螺絲/推銷）。鰭片對網格極不友善，故：
#   1) 以原始 body 的 copy 為母體 → 底面凸台/階梯/凹槽、上蓋等特徵原樣保留。
#   2) 鰭片區填實：由鰭片【垂直側壁】推得鰭片排的範圍，依鰭片長度分群、群內間距過大處再切分，
#      每群建立實心塊（鰭片根部 → 鰭片頂）與母體聯集；螺絲所在角落因無鰭片而自然保留避讓缺口。
#   3) 鎖孔保留：底板上「完整圓周、開口於鰭片根部」的內凹圓柱為鎖孔，以孔喉半徑貫穿扣除
#      （切斷螺桿/尾端）；鰭片根部以上的同軸外凸圓柱（螺絲頭/墊圈/彈簧，常與底板融合為同一實體）
#      以該半徑的柱體切除；布林後若有不相連殘塊，只留體積最大者。
#   4) 量測原始體積 → 以常見散熱片密度（鋁 2700 kg/m³；可逐 body 指定）算質量 →
#      反推簡化體在質量守恆下應設定的等效密度，附加於新 body 名稱後綴。
# 單位：PyAnsys Geometry 內部一律公尺 m；體積 m³、密度 kg/m³、質量 kg。高度軸固定為 world Y。
# 座標：Face/Edge/BoundingBox 回傳皆為 world 座標；暫存切割/填實幾何建在根設計（world 座標），
#       結果以原始 body 的 copy 為母體 → 落在原始 body 所屬 component（共用 master 的所有
#       instance 都會出現），與手工 '<name>_sim' 的放置方式一致。
# 後端行為（Ansys 25.1）：布林結果若不相連，會被拆成多個名為 'Solid' 的新 body；
#       Component.bodies 於布林後會過期，需從設計樹重新查詢（見 _comp_bodies）。

# 常見散熱片材料密度 (kg/m³)，供質量估算與 fluent/mechanical 材料對照
HEATSINK_DENSITY_PRESETS = {
    "aluminum": 2700.0,       # 鋁合金（最常見擠型/壓鑄散熱片）
    "aluminum_6063": 2700.0,
    "copper": 8960.0,         # 純銅散熱片 / 銅底
    "copper_c110": 8890.0,
}

_HS_EPS = 1e-6               # 1µm：Y 高度比對容差（公尺）
_HS_BOTTOM_AREA_RATIO = 0.10  # 底面層總面積 ≥ 最大朝下層的 10% 才算「實質底面」（排除螺絲尾端）
_HS_ROOT_FILLET_M = 1.5e-3    # 鰭片根部圓角容差：側壁起點可高於根部平面至多 1.5mm


def _q_m(v) -> float:
    """pint.Quantity（或純數）轉為公尺純數值。"""
    from ansys.geometry.core.misc import UNITS

    return v.m_as(UNITS.m) if hasattr(v, "m_as") else float(v)


def _face_extent(face):
    """以 face 各 edge 端點估算其 world 包圍盒 (lo, hi)，單位公尺；取不到則回傳 None。

    Face.bounding_box 需 Ansys 25.2+，25.1 無法使用，故改取 edge 端點。
    部分退化 edge 取端點會丟 ValueError（零長向量），逐條容錯略過。
    """
    pts = []
    for e in face.edges:
        try:
            pts.append(e.start)
            pts.append(e.end)
        except Exception:
            continue
    if not pts:
        return None
    xs = [_q_m(p.x) for p in pts]
    ys = [_q_m(p.y) for p in pts]
    zs = [_q_m(p.z) for p in pts]
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def _face_area_m2(face) -> float:
    from ansys.geometry.core.misc import UNITS

    a = face.area
    return a.m_as(UNITS.m ** 2) if hasattr(a, "m_as") else float(a)


def _horizontal_planes(body):
    """列出 body 所有水平平面：list[(face, y, area, up)]，up=True 表法向朝 +Y。"""
    from ansys.geometry.core.designer.face import SurfaceType

    out = []
    for f in body.faces:
        try:
            if f.surface_type != SurfaceType.SURFACETYPE_PLANE:
                continue
            n = f.normal(0.5, 0.5)
            if abs(float(n.y)) < 0.9:
                continue
            out.append((f, _q_m(f.point(0.5, 0.5).y), _face_area_m2(f), float(n.y) > 0))
        except Exception:
            continue
    return out


def _vertical_walls(body):
    """列出 body 的垂直平面（法向 ±X 或 ±Z）：list[(axis 0=X/2=Z, lo, hi, area)]（world 公尺）。"""
    from ansys.geometry.core.designer.face import SurfaceType

    out = []
    for f in body.faces:
        try:
            if f.surface_type != SurfaceType.SURFACETYPE_PLANE:
                continue
            n = f.normal(0.5, 0.5)
            if abs(float(n.y)) > 0.1:
                continue
            if abs(float(n.x)) > 0.9:
                axis = 0
            elif abs(float(n.z)) > 0.9:
                axis = 2
            else:
                continue
            ext = _face_extent(f)
            if ext is not None:
                out.append((axis, ext[0], ext[1], _face_area_m2(f)))
        except Exception:
            continue
    return out


def _level_areas(planes, up):
    """將同方向水平面依高度彙總：{y: 總面積}（高度以 1µm 量化合併）。"""
    acc = {}
    for _f, y, area, is_up in planes:
        if is_up != up:
            continue
        key = round(y / _HS_EPS)
        acc.setdefault(key, [y, 0.0])
        acc[key][1] += area
    return {v[0]: v[1] for v in acc.values()}


def _main_bottom_plane(planes):
    """主接合底面：總面積 ≥ 最大朝下層 10% 的「最低」朝下層，回傳 (該層最大面, y)；無則 (None, None)。

    - 不取 body 最低 Y：彈簧螺絲/推銷尾端常往下突出（面積極小）。
    - 不只取面積最大層：許多散熱片底部有較小的接觸凸台（pedestal）比底板更低，
      它才是真正貼合晶片的熱接觸面，必須保留並當作底面基準。
    """
    levels = _level_areas(planes, up=False)
    if not levels:
        return None, None
    a_max = max(levels.values())
    y_bot = min(y for y, a in levels.items() if a >= _HS_BOTTOM_AREA_RATIO * a_max)
    faces = [p for p in planes if not p[3] and abs(p[1] - y_bot) <= _HS_EPS]
    return max(faces, key=lambda p: p[2])[0], y_bot


def _fin_root_y(planes, walls, y_bot, y_top):
    """鰭片根部（底板頂面）高度。

    主要依據：鰭片側壁的起點——對每個介於底面與頂面之間的朝上層 L，累計「起點落在
    [L, L+1.5mm]（含根部圓角）」的垂直側壁面積，取最大者（鰭片最多的層）。
    → 可避開上蓋頂面等大面積朝上平面（例如折片鰭片夾在底板與上蓋之間）。
    無任何側壁時退回「朝上層總面積最大者」；仍無則回傳 None（無獨立底板）。
    """
    levels = {y: a for y, a in _level_areas(planes, up=True).items()
              if y_bot + _HS_EPS < y < y_top - _HS_EPS}
    if not levels:
        return None
    score = {y: sum(w[3] for w in walls
                    if y - 1e-5 <= w[1][1] <= y + _HS_ROOT_FILLET_M and w[2][1] - w[1][1] > 1e-3)
             for y in levels}
    best = max(score, key=lambda y: score[y])
    if score[best] > 0:
        return best
    return max(levels, key=lambda y: levels[y])


_HS_CONE_MAX_HALF_ANGLE = math.radians(15.0)  # 拔模錐孔上限；45° 倒角等更陡錐面不視為孔壁


def _y_cylinders(body):
    """列出 body 上軸向沿 Y 的圓柱面：list[dict(cx, cz, r, ylo, yhi, concave, angle)]（公尺/弧度）。

    壓鑄件鎖孔常帶拔模斜度而成為小半錐角的錐面，半錐角 ≤ _HS_CONE_MAX_HALF_ANGLE 者
    一併視為圓柱，半徑取面中點至軸心距離（≈ 中段孔徑）。
    concave（內凹＝孔壁）判定：面外法向指向軸心 → 法向與徑向向量內積 < 0。
    angle：該面涵蓋的圓周角 ≈ 面積 / (r·高)，用於區分完整孔（2π）與圓角（π/2）。
    """
    from ansys.geometry.core.designer.face import SurfaceType

    out = []
    for f in body.faces:
        try:
            is_cone = f.surface_type == SurfaceType.SURFACETYPE_CONE
            if f.surface_type != SurfaceType.SURFACETYPE_CYLINDER and not is_cone:
                continue
            cyl = f.shape.geometry
            if abs(float(cyl.dir_z.y)) < 0.9:
                continue
            cx, cz = _q_m(cyl.origin.x), _q_m(cyl.origin.z)
            p = f.point(0.5, 0.5)
            if is_cone:
                ha = cyl.half_angle
                ha = ha.m_as("radian") if hasattr(ha, "m_as") else float(ha)
                if abs(ha) > _HS_CONE_MAX_HALF_ANGLE:
                    continue
                r = math.hypot(_q_m(p.x) - cx, _q_m(p.z) - cz)
            else:
                r = _q_m(cyl.radius)
            n = f.normal(0.5, 0.5)
            dot = float(n.x) * (_q_m(p.x) - cx) + float(n.z) * (_q_m(p.z) - cz)
            ext = _face_extent(f)
            if ext is None:
                continue
            h = ext[1][1] - ext[0][1]
            angle = _face_area_m2(f) / (r * h) if r > 0 and h > 0 else 0.0
            out.append({"cx": cx, "cz": cz, "r": r, "ylo": ext[0][1], "yhi": ext[1][1],
                        "concave": dot < 0, "angle": angle})
        except Exception:
            continue
    return out


def _detect_mount_holes(cyls, min_radius_m, concentric_tol_m=2e-4):
    """偵測鎖孔：原始 body 上所有挖孔（完整圓周的內凹 Y 向圓柱），簡化為貫穿的 Y 向直圓柱。

    1. 只看內凹、半徑 ≥ min_radius_m 的圓柱面；同 (中心, 半徑) 的分片面累加圓周角，
       ≥ 0.9·2π 才算孔（排除內圓角）。不論高度、盲孔/通孔、開口方向。
    2. 同軸者合併，孔徑取最小半徑（沉孔/倒角等細節捨棄，只留一支直圓柱）。
    3. clearance：同軸所有 Y 向圓柱的最大半徑，用於排除螺絲側面誤判為鰭片。
    4. screw_r：同軸外凸圓柱的最大半徑（與本體融合的螺絲/墊圈/彈簧），0 表示無螺絲。
    回傳 list[dict(cx, cz, radius, clearance, screw_r)]（公尺）。
    """
    import math

    # 以「同軸中心」分群（忽略半徑差異），累加該中心所有內凹 Y 圓柱分片的圓周角。
    # 沉孔/counterbore 的孔會被切成「大徑沉孔環 + 小徑孔喉」兩段不同半徑，各自可能都
    # 不足完整圓周；但同一中心累加後 ≥ 0.9·2π 即視為真實挖孔，孔徑取該中心最小半徑（孔喉）。
    centers = {}
    for c in cyls:
        if not c["concave"] or c["r"] < min_radius_m:
            continue
        key = (round(c["cx"] / concentric_tol_m), round(c["cz"] / concentric_tol_m))
        g = centers.setdefault(key, {"cx": c["cx"], "cz": c["cz"], "angle": 0.0,
                                     "rmin": c["r"], "segs": []})
        g["angle"] += c["angle"]
        g["rmin"] = min(g["rmin"], c["r"])
        g["segs"].append(c)
    full = [g for g in centers.values() if g["angle"] >= 0.9 * 2 * math.pi]

    holes = []
    for g in full:
        holes.append({"cx": g["cx"], "cz": g["cz"], "radius": g["rmin"]})

    for h in holes:
        coax = [c for c in cyls
                if abs(c["cx"] - h["cx"]) <= concentric_tol_m and abs(c["cz"] - h["cz"]) <= concentric_tol_m]
        concave = [c for c in coax if c["concave"]]
        h["ylo"] = min(c["ylo"] for c in concave) if concave else 0.0
        h["yhi"] = max(c["yhi"] for c in concave) if concave else 0.0
        h["clearance"] = max([c["r"] for c in coax] + [h["radius"]])
        h["screw_r"] = max([c["r"] for c in coax if not c["concave"]] + [0.0])
    return holes


def _diag_corner_cylinders(cyls, bbox_lo, bbox_hi, concentric_tol_m=2e-4, near_corner_m=25e-3):
    """[診斷] 統計靠近四角的同軸 Y 圓柱群，回傳每群 (cx,cz,最小/最大半徑,總圓周角,是否完整圓周)。

    用於找出外側螺絲鎖孔為何未被 _detect_mount_holes 偵測（圓周角不足？半徑不符？外凸？）。
    """
    import math
    cx0, cz0 = (bbox_lo[0] + bbox_hi[0]) / 2.0, (bbox_lo[2] + bbox_hi[2]) / 2.0
    corners = [(bbox_lo[0], bbox_lo[2]), (bbox_hi[0], bbox_lo[2]),
               (bbox_hi[0], bbox_hi[2]), (bbox_lo[0], bbox_hi[2])]
    groups = {}
    for c in cyls:
        if not any(abs(c["cx"] - qx) <= near_corner_m and abs(c["cz"] - qz) <= near_corner_m
                   for qx, qz in corners):
            continue
        key = (round(c["cx"] / concentric_tol_m), round(c["cz"] / concentric_tol_m))
        g = groups.setdefault(key, {"cx": c["cx"], "cz": c["cz"], "rmin": c["r"], "rmax": c["r"],
                                    "ang_cc": 0.0, "ang_cx": 0.0})
        g["rmin"] = min(g["rmin"], c["r"])
        g["rmax"] = max(g["rmax"], c["r"])
        if c["concave"]:
            g["ang_cc"] += c["angle"]
        else:
            g["ang_cx"] += c["angle"]
    out = []
    for g in groups.values():
        g["radial"] = ((g["cx"] - cx0) ** 2 + (g["cz"] - cz0) ** 2) ** 0.5
        g["full"] = g["ang_cc"] >= 0.9 * 2 * math.pi
        out.append(g)
    # 內凹（孔壁）優先、再依徑向最外優先，方便診斷真實鎖孔分佈
    out.sort(key=lambda g: (-g["ang_cc"], -g["radial"]))
    return out


def _select_screw_holes(holes, bbox_lo, bbox_hi, hole_select="screw", outer_margin=0.6):
    """從所有偵測到的孔中挑出真正的「螺絲鎖孔」，排除內側定位點 (locating pin) 孔。

    CPU/power 散熱片四角各有一個外側螺絲鎖孔（鎖上主機板/背板），其斜內側常緊貼一個
    較小的定位銷孔。兩孔徑向距離相近，單純用全域徑向門檻無法分離，故改用「角落分群 →
    每群取最外一孔」策略：

    - "all"：不過濾，保留所有孔（原始行為）。
    - "screw"（預設）：優先保留「同軸有外凸螺絲/彈簧/墊圈」(screw_r > 0) 的孔——真實鎖孔
      最可靠的訊號；若模型未建螺絲（全部 screw_r == 0），退回 "outer" 的角落分群判定。
    - "outer"：依孔相對散熱片 X-Z 中心落在哪個象限分成四個角落群，每群只保留「距中心
      徑向距離最遠」的一孔（即最外側螺絲鎖孔），其餘內側孔（定位銷）剔除；再以
      outer_margin × 全域最大徑向距離過濾掉明顯偏內的孤立孔。

    bbox_lo/bbox_hi：散熱片 world 包圍盒（公尺），用以取 X-Z 幾何中心。
    回傳過濾後的 holes（原 list 的子集，順序不變）。
    """
    if not holes or hole_select == "all":
        return holes

    cx0 = (bbox_lo[0] + bbox_hi[0]) / 2.0
    cz0 = (bbox_lo[2] + bbox_hi[2]) / 2.0

    def _radius(h):
        return ((h["cx"] - cx0) ** 2 + (h["cz"] - cz0) ** 2) ** 0.5

    def _outer_by_corner(subset, use_screw_tiebreak=False):
        """四象限分群，每群保留徑向最遠一孔；再剔除明顯偏內的孤立孔。

        use_screw_tiebreak=True 時，同角落內兩孔徑向距離相近（差 < corner_tol）者，
        改以「有無同軸螺絲 (screw_r)」或較大 clearance 作為該角落代表。
        """
        if len(subset) <= 1:
            return subset
        corner_tol = 3e-3  # 3mm：同角落兩孔徑向距離差在此內視為相近
        quads = {}  # (sign_x, sign_z) -> 該象限代表孔
        for h in subset:
            qx = 1 if (h["cx"] - cx0) >= 0 else -1
            qz = 1 if (h["cz"] - cz0) >= 0 else -1
            cur = quads.get((qx, qz))
            if cur is None:
                quads[(qx, qz)] = h
                continue
            dr = _radius(h) - _radius(cur)
            if dr > corner_tol:
                quads[(qx, qz)] = h          # 明顯更外 → 取代
            elif dr < -corner_tol:
                pass                          # 明顯更內 → 保留原本
            elif use_screw_tiebreak:
                # 徑向相近：優先有螺絲者，其次 clearance（含螺頭/墊圈）較大者，再取較外者
                hk = (h.get("screw_r", 0.0) > 0.0, h.get("clearance", h["radius"]), _radius(h))
                ck = (cur.get("screw_r", 0.0) > 0.0, cur.get("clearance", cur["radius"]), _radius(cur))
                if hk > ck:
                    quads[(qx, qz)] = h
            elif _radius(h) > _radius(cur):
                quads[(qx, qz)] = h
        picked = list(quads.values())
        # 剔除明顯偏內的象限代表（例如某角落根本沒有外側鎖孔，只有中央定位孔）
        r_max = max(_radius(h) for h in picked)
        if r_max > 1e-9:
            picked = [h for h in picked if _radius(h) >= outer_margin * r_max]
        # 維持原 holes 順序
        keep = {id(h) for h in picked}
        return [h for h in holes if id(h) in keep]

    if hole_select == "outer":
        return _outer_by_corner(holes, use_screw_tiebreak=False)

    # "screw"：以角落分群取最外一孔為主（紅＝外側螺絲孔，藍＝內側定位孔），
    #           同角落兩孔徑向相近時才以 screw_r / clearance 作決勝。
    return _outer_by_corner(holes, use_screw_tiebreak=True)


def _hole_plate_span(planes, h):
    """鎖孔所在板材的 (下表面 y, 上表面 y)；找不到回傳 None。

    下表面 = 孔壁最低點以下、涵蓋孔中心的最高朝下平面；上表面 = 其上第一個涵蓋孔中心的朝上平面。
    不以孔壁最高點找上表面：孔上方常有同軸的彈簧座/螺頭沉孔，會把範圍誤拉到鰭片頂。
    """
    def _covers(f):
        ext = _face_extent(f)
        return ext is not None and ext[0][0] <= h["cx"] <= ext[1][0] and ext[0][2] <= h["cz"] <= ext[1][2]

    downs = [y for f, y, _a, up in planes if not up and y <= h["ylo"] + 1e-5 and _covers(f)]
    if not downs:
        return None
    yb = max(downs)
    ups = [y for f, y, _a, up in planes if up and y > yb + 1e-5 and _covers(f)]
    if not ups:
        return None
    return yb, min(ups)


def _simple_heatsink_boxes(planes, holes, rects, lo, hi, y_bot, y_root, contact_box=None, fin_box="largest"):
    """凸字形簡化的三個方塊（world 公尺，各為 (lo_xyz, hi_xyz) 或 None）：無階梯、無圓角。

    - plate（底板）：X-Z 取整體包圍盒；Y 從板底到鰭片根部。板底 = 鎖孔所在板材下表面
      （_hole_plate_span，多孔取最低）；無鎖孔則為主接合底面（即無下凸）。
    - top（上凸）：fin_box="largest" 取面積最大的一個鰭片填實矩形；"all" 取所有鰭片矩形的外框
      （十字形鰭片配置）。鰭片根部 → 鰭片頂。
    - bottom（下凸）：主接合底面（面積 ≥ 該層最大面 10% 的面）的 X-Z 包圍盒，主接合底面 → 板底；
      若包圍盒蓋到鎖孔，則裁成與上凸同 X-Z 範圍，避免下凸填到鎖孔下方。
    - contact_box（接觸體包圍盒，例如 CPU 散熱片的銅底）：給定時下凸 = 接觸體範圍與厚度，
      板底改為接觸體頂面（銅底與框架底面齊平時，下凸才能與框架區分，接觸面 named selection 只含銅底）。
    """
    y_mid = y_root if y_root is not None else y_bot
    spans = [s for s in (_hole_plate_span(planes, h) for h in holes) if s is not None]
    y_pb = min(s[0] for s in spans) if spans else y_bot
    if contact_box is not None:
        y_pb = contact_box[1][1]
    y_pb = min(max(y_pb, y_bot), y_mid)

    plate = ((lo[0], y_pb, lo[2]), (hi[0], y_mid, hi[2])) if y_mid - y_pb > 1e-5 else None

    if fin_box == "all":
        x0, x1 = min(r[0] for r in rects), max(r[1] for r in rects)
        z0, z1 = min(r[2] for r in rects), max(r[3] for r in rects)
        yt = max(r[4] for r in rects)
    else:
        x0, x1, z0, z1, yt = max(rects, key=lambda r: (r[1] - r[0]) * (r[3] - r[2]))
    top = ((x0, y_mid, z0), (x1, yt, z1)) if yt - y_mid > 1e-5 else None

    bottom = None
    if contact_box is not None:
        (cx0, cy0, cz0), (cx1, _cy1, cz1) = contact_box
        if y_pb - cy0 > 1e-5:
            bottom = ((cx0, cy0, cz0), (cx1, y_pb, cz1))
    elif y_pb - y_bot > 1e-5:
        faces = [(f, a) for f, y, a, up in planes if not up and abs(y - y_bot) <= _HS_EPS]
        a_max = max((a for _f, a in faces), default=0.0)
        exts = [e for e in (_face_extent(f) for f, a in faces if a >= _HS_BOTTOM_AREA_RATIO * a_max) if e]
        if exts:
            bx0, bx1 = min(e[0][0] for e in exts), max(e[1][0] for e in exts)
            bz0, bz1 = min(e[0][2] for e in exts), max(e[1][2] for e in exts)
            if any(bx0 - h["radius"] < h["cx"] < bx1 + h["radius"] and bz0 - h["radius"] < h["cz"] < bz1 + h["radius"]
                   for h in holes):
                bx0, bx1, bz0, bz1 = max(bx0, x0), min(bx1, x1), max(bz0, z0), min(bz1, z1)
            if bx1 - bx0 > 1e-5 and bz1 - bz0 > 1e-5:
                bottom = ((bx0, y_bot, bz0), (bx1, y_pb, bz1))
    if plate is None and top is None and bottom is None:
        raise ValueError("無法建立凸字形簡化體（底板/上凸/下凸皆為空）")
    return {"plate": plate, "top": top, "bottom": bottom, "y_plate_bot": y_pb}


def _split_by_gap(own, support, ci, cap_tol):
    """將一個長度群的側壁依排列方向切成子群，回傳 list[(cross_lo, cross_hi, [own walls])]。

    support = 長向範圍涵蓋本群的其他（較長）鰭片群側壁：它們在本群長度內同樣有鰭片，
    故一併參與間距判斷——例如外側短鰭片與中央長鰭片之間的空隙不會被誤切成縫。
    間距 > 3×中位間距（且 > cap_tol）處才切分（例如中間夾螺絲的兩排鰭片）；
    子群範圍取該段所有側壁（含 support）的最外範圍。
    """
    pos = sorted([(w, True) for w in own] + [(w, False) for w in support], key=lambda t: t[0][1][ci])
    if len(pos) < 2:
        return [(pos[0][0][1][ci], pos[0][0][2][ci], [pos[0][0]])] if pos else []
    gaps = [pos[i + 1][0][1][ci] - pos[i][0][2][ci] for i in range(len(pos) - 1)]
    med = sorted(gaps)[len(gaps) // 2]
    limit = max(3.0 * med, cap_tol)
    segs, cur = [], [pos[0]]
    for g, t in zip(gaps, pos[1:]):
        if g > limit:
            segs.append(cur)
            cur = []
        cur.append(t)
    segs.append(cur)
    out = []
    for seg in segs:
        mine = [w for w, is_own in seg if is_own]
        if mine:
            out.append((min(w[1][ci] for w, _o in seg), max(w[2][ci] for w, _o in seg), mine))
    return out


def _fin_fill_rects(body, y_root, y_top, holes, bbox_lo, bbox_hi, group_tol_m=2e-4):
    """由鰭片側壁推算鰭片區的填實矩形：(list[(x0, x1, z0, z1, y_top_of_group)], 鰭片走向)（公尺）。

    鰭片頂面常帶端部圓角/倒角而比鰭片短，故以鰭片【垂直側壁平面】取真實長度：
    1. 候選側壁 = 起點在鰭片根部（含根部圓角容差）、高度 ≥ 最高側壁一半的垂直平面；
       排除中心落在鎖孔 clearance 內者（螺絲/彈簧的側平面）。
    2. 鰭片走向：候選面法向多數為 ±X → 鰭片沿 Z 延伸（沿 X 排列），反之沿 X。
    3. 法向垂直於走向的側壁依「長向範圍」分群（容差 group_tol_m）；群內再依排列間距切分
       （間距 > 3×中位間距 → 視為不同鰭片排，例如中間夾螺絲；較長鰭片群在本群長度內的側壁
       也算數，避免長短鰭片交界被切出縫），每子群以其排列範圍成一矩形。
       → 全長鰭片群形成主體，較短鰭片群只在其長度內延伸，螺絲所在角落自然留下避讓缺口。
    4. 法向平行於走向的端蓋面（鰭片端面/外緣側板）若貼齊某子群長向端點且排列範圍相鄰，擴展該子群。
    5. 長向相鄰的子群（例如針狀鰭片的各列）若間隙 ≤ min(兩群長度, 5mm)，於重疊排列範圍補橋接塊。
    找不到鰭片側壁則退回整個 X-Z 包圍盒。
    """
    walls = []
    for w in _vertical_walls(body):
        axis, lo, hi, _area = w
        if lo[1] < y_root - 1e-5 or lo[1] > y_root + _HS_ROOT_FILLET_M:
            continue
        mx, mz = (lo[0] + hi[0]) / 2.0, (lo[2] + hi[2]) / 2.0
        if any(((mx - h["cx"]) ** 2 + (mz - h["cz"]) ** 2) ** 0.5 <= h["clearance"] + 5e-4 for h in holes):
            continue
        walls.append(w)
    if walls:
        h_max = max(w[2][1] - w[1][1] for w in walls)
        walls = [w for w in walls if w[2][1] - w[1][1] >= 0.5 * h_max]

    sides_x = [w for w in walls if w[0] == 0]
    sides_z = [w for w in walls if w[0] == 2]
    if not walls:
        return [(bbox_lo[0], bbox_hi[0], bbox_lo[2], bbox_hi[2], y_top)], "none"

    # 鰭片沿 Z → 側壁法向為 ±X；長向=Z(索引2)、排列向=X(索引0)
    along_z = len(sides_x) >= len(sides_z)
    li, ci = (2, 0) if along_z else (0, 2)
    sides, caps = (sides_x, sides_z) if along_z else (sides_z, sides_x)

    # 3. 依長向範圍分群
    by_len = []  # [long_lo, long_hi, [walls]]
    for w in sides:
        l0, l1 = w[1][li], w[2][li]
        if l1 - l0 < 1e-5:
            continue
        for g in by_len:
            if abs(g[0] - l0) <= group_tol_m and abs(g[1] - l1) <= group_tol_m:
                g[2].append(w)
                break
        else:
            by_len.append([l0, l1, [w]])

    groups = []  # 每子群：[long_lo, long_hi, cross_lo, cross_hi, ytop]
    cap_tol = 2e-3
    for l0, l1, ws in by_len:
        support = [w for g0, g1, gws in by_len if (g0, g1) != (l0, l1)
                   and g0 <= l0 + group_tol_m and g1 >= l1 - group_tol_m for w in gws]
        for c0, c1, sub in _split_by_gap(ws, support, ci, cap_tol):
            groups.append([l0, l1, c0, c1, max(w[2][1] for w in sub)])

    # 4. 端蓋面擴展（需貼齊長向端點，且排列範圍與子群相鄰）
    for _a, lo, hi, _area in caps:
        for g in groups:
            if min(abs(lo[li] - g[0]), abs(lo[li] - g[1])) > group_tol_m:
                continue
            if hi[ci] < g[2] - cap_tol or lo[ci] > g[3] + cap_tol:
                continue
            g[2], g[3] = min(g[2], lo[ci]), max(g[3], hi[ci])

    groups = [g for g in groups if g[3] - g[2] >= 1e-5]

    # 5. 長向相鄰子群之間的橋接（針狀鰭片列與列之間）
    bridges = []
    srt = sorted(groups, key=lambda g: g[0])
    for i, a in enumerate(srt):
        for b in srt[i + 1:]:
            gap = b[0] - a[1]
            if gap <= 1e-6:
                continue
            if gap > min(a[1] - a[0], b[1] - b[0], 5e-3):
                continue
            c0, c1 = max(a[2], b[2]), min(a[3], b[3])
            if c1 - c0 >= 1e-5:
                bridges.append([a[1], b[0], c0, c1, min(a[4], b[4])])
                break  # 只橋接到長向最近的一群

    rects = []
    for l0, l1, c0, c1, y in groups + bridges:
        rects.append((c0, c1, l0, l1, y) if along_z else (l0, l1, c0, c1, y))
    if not rects:
        return [(bbox_lo[0], bbox_hi[0], bbox_lo[2], bbox_hi[2], y_top)], "none"
    return rects, ("Z" if along_z else "X")


def _comp_bodies(design, comp_id):
    """重新從設計樹取得某 component 下的 body（布林運算後 Component 物件快取會過期）。"""
    return [b for b in design.get_all_bodies() if b.parent_component.id == comp_id]


def _master_key(component):
    """component 的 master 識別碼：同一 master 的多個 instance 只需簡化一次。"""
    master = getattr(component, "_master_component", None)
    return getattr(master, "id", None) or component.id


def _safe_delete(body):
    """刪除 body（已不存在則略過），回傳是否成功。"""
    try:
        if body is not None and body.is_alive:
            body.parent_component.delete_body(body)
            return True
    except Exception as e:
        logger.warning(f"刪除暫存 body 失敗: {e}")
    return False


def _make_cylinder_body(design, name, cx, cz, radius, y_bottom, y_top):
    """於 (cx, cz) 建立沿 Y 軸、從 y_bottom 到 y_top 的實心圓柱 body（公尺）。用於扣孔。

    草圖平面取 X-Z 面但方向需使法向指向 +Y，才能沿 +Y 正確拉伸孔高。
    法向 = direction_x × direction_y，故取 direction_x=+Z、direction_y=+X →
    法向 = (0,0,1)×(1,0,0) = (0,1,0) = +Y。此時草圖 local 座標為 (u=Z, v=X)，
    圓心需以 Point2D([cz, cx]) 給定。
    """
    from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D
    from ansys.geometry.core.misc import UNITS, Distance
    from ansys.geometry.core.sketch import Sketch

    plane = Plane(
        origin=Point3D([0, y_bottom, 0], UNITS.m),
        direction_x=UnitVector3D([0, 0, 1]),
        direction_y=UnitVector3D([1, 0, 0]),
    )
    sketch = Sketch(plane).circle(Point2D([cz, cx], UNITS.m), Distance(radius, UNITS.m))
    return design.extrude_sketch(name, sketch, Distance(y_top - y_bottom, UNITS.m))


def _resolve_heatsink_groups(design, source, extra_sources, all_instances):
    """解析要簡化的散熱片：回傳 list[list[Body]]，每個元素為「同一 component instance 內」的一組 body。

    - source：主 body 名稱（決定結果命名與所屬 component）。
    - extra_sources：額外併入的 body 名稱或 glob（例如 'ICX_HS_1U_FIN_*'），只在主 body 的
      同一 component instance 內比對；曲面 body 自動略過。用於鰭片/底座分屬多個 body 的組件。
    - all_instances：True 時處理所有含 source 的 component（同 master 只處理一次）；
      False 時只處理第一個。
    """
    import fnmatch

    matches = [b for b in _find_bodies_by_name(source) if not b.is_surface]
    if not matches:
        return []
    groups, seen = [], set()
    for b in matches:
        comp = b.parent_component
        key = _master_key(comp)
        if key in seen:
            continue
        seen.add(key)
        group = [b]
        if extra_sources:
            for o in _comp_bodies(design, comp.id):
                if o.id == b.id or o.is_surface:
                    continue
                if any(fnmatch.fnmatchcase(o.name, pat) for pat in extra_sources):
                    group.append(o)
        groups.append(group)
        if not all_instances:
            break
    return groups


def _body_density(body, default_rho, body_densities):
    """依 body_densities（{名稱或 glob: kg/m³ 或材料名}）取得該 body 密度，未指定則用 default_rho。"""
    import fnmatch

    for pat, val in (body_densities or {}).items():
        if fnmatch.fnmatchcase(body.name, pat):
            if isinstance(val, str):
                return HEATSINK_DENSITY_PRESETS.get(val.lower(), default_rho)
            return float(val)
    return default_rho


def _simplify_heatsink_group(design, bodies, base_name, default_rho, body_densities,
                             keep_source, named_selection, name_density_suffix, hole_min_dia_mm,
                             contact_body=None, fin_box="largest", hole_select="screw", progress=None,
                             diagnose_only=False):
    """簡化一組散熱片 body（同一 component instance），回傳結果 dict；失敗時清除暫存並拋例外。

    progress(msg)：於各階段開始時呼叫；逾時由其拋 TimeoutError，走既有清除暫存流程。
    """
    import fnmatch

    from ansys.geometry.core.misc import UNITS

    _p = progress or (lambda _msg: None)
    src = bodies[0]
    comp = src.parent_component
    comp_id = comp.id

    # --- 1. 原始體積與質量（逐 body 密度）---
    parts = []
    for b in bodies:
        v = b.volume.m_as(UNITS.m ** 3)
        parts.append((b.name, v, _body_density(b, default_rho, body_densities)))
    v_orig = sum(p[1] for p in parts)
    mass = sum(p[1] * p[2] for p in parts)
    if v_orig <= 0:
        raise ValueError(f"原始 body 體積量測異常 (V={v_orig})")

    before_ids = {b.id for b in _comp_bodies(design, comp_id)}
    temps = []
    pad = 1e-3  # 1mm：暫存切割體外擴量，確保布林乾淨
    try:
        # --- 2. 母體：原始 body 的 copy（多 body 則聯集成一體）---
        _p(f"複製並聯集 {len(bodies)} 個 body")
        work = src.copy(comp, base_name)
        if len(bodies) > 1:
            others = [b.copy(comp, f"{base_name}_tmp_part") for b in bodies[1:]]
            temps.extend(others)
            work.unite(others, keep_other=False)

        # --- 3. 幾何特徵分析（world 座標）---
        _p("分析底面 / 鰭片 / 鎖孔幾何特徵")
        lo, hi = _bbox_m(work)
        y_top = hi[1]
        planes = _horizontal_planes(work)
        _bf, y_bot = _main_bottom_plane(planes)
        if y_bot is None:
            y_bot = lo[1]
        walls = _vertical_walls(work)
        y_root = _fin_root_y(planes, walls, y_bot, y_top)
        cyls = _y_cylinders(work)
        all_holes = _detect_mount_holes(cyls, min_radius_m=max(hole_min_dia_mm, 0.0) / 2000.0)
        # 篩出真正的外側螺絲鎖孔，排除中央定位銷孔（locating pin）
        holes = _select_screw_holes(all_holes, lo, hi, hole_select=hole_select)
        # [診斷] 針對四角統計所有同軸內凹 Y 圓柱（含未達完整圓周門檻者），找出紅色螺絲孔為何漏偵
        corner_diag = _diag_corner_cylinders(cyls, lo, hi)
        if diagnose_only:
            # 僅做幾何偵測與診斷，略過昂貴的方塊重建與布林運算；清除暫存母體後直接回傳。
            for b in temps:
                _safe_delete(b)
            _safe_delete(work)
            return {
                "result_body": "(diagnose_only)", "component": comp.name, "parts": parts,
                "v_orig": v_orig, "mass": mass, "v_sim": v_orig, "rho_equiv": mass / v_orig,
                "lo": lo, "hi": hi, "y_bot": y_bot, "y_root": y_root, "y_top": y_top,
                "shape": {"plate": None, "top": None, "bottom": None}, "fin_axis": "none",
                "holes": holes, "all_holes": all_holes, "corner_diag": corner_diag,
                "removed_count": 0, "removed_vol": 0.0,
                "named_selection": None, "ns_faces": 0,
            }
        fill_from = y_root if y_root is not None else y_bot
        # 鰭片側壁避讓仍以「所有孔」的 clearance 判定，避免被捨棄孔附近的螺絲側平面誤判成鰭片
        rects, fin_axis = _fin_fill_rects(work, fill_from, y_top, all_holes, lo, hi)

        def _largest():
            """布林後母體可能被拆成多塊，且原 handle 不一定留在主體上（可能落在小碎片）→ 重取體積最大者。"""
            temp_ids = {t.id for t in temps}
            cands = [b for b in _comp_bodies(design, comp_id) if b.id not in before_ids and b.id not in temp_ids]
            return max(cands, key=lambda b: b.volume.m_as(UNITS.m ** 3))

        # --- 4. 凸字形方塊組（world 座標，建於根設計）：底板 + 上凸（鰭片）+ 下凸（接觸面），無階梯/圓角 ---
        contact_box = None
        if contact_body:
            cbs = [b for b in bodies if fnmatch.fnmatchcase(b.name, contact_body)]
            if not cbs:
                raise ValueError(f"contact_body '{contact_body}' 不在本組 body 中（需為 source 或 extra_sources 之一）")
            boxes_c = [_bbox_m(b) for b in cbs]
            contact_box = (tuple(min(bx[0][i] for bx in boxes_c) for i in range(3)),
                           tuple(max(bx[1][i] for bx in boxes_c) for i in range(3)))
        shape = _simple_heatsink_boxes(planes, holes, rects, lo, hi, y_bot, y_root,
                                       contact_box=contact_box, fin_box=fin_box)
        _p(f"建立凸字形方塊組並扣 {len(holes)} 個鎖孔")
        boxes = []
        for key in ("plate", "top", "bottom"):
            if shape[key] is not None:
                b = _make_box_from_bbox(design, f"{base_name}_tmp_{key}", *shape[key])
                temps.append(b)
                boxes.append(b)
        blk = boxes[0]
        if len(boxes) > 1:
            blk.unite(boxes[1:], keep_other=False)
        # 鎖孔：Y 向直圓柱貫穿
        for i, h in enumerate(holes, start=1):
            cb = _make_cylinder_body(design, f"{base_name}_tmp_hole_{i:02d}", h["cx"], h["cz"], h["radius"],
                                     lo[1] - pad, hi[1] + pad)
            temps.append(cb)
            try:
                blk.subtract(cb, keep_other=False)
            except Exception as e:
                logger.info(f"鎖孔 {i} 未碰到簡化體，略過: {e}")
                _safe_delete(cb)

        # --- 5. 將方塊組放進原始 body 所屬 component：母體 ∪ 方塊組 → ∩ 方塊組（= 方塊組本身）---
        #        直接 copy 根設計的 body 到 component instance 會套用 instance 變換而錯位，故以布林轉入。
        _p("將方塊組轉入原 component（布林）")
        blk2 = blk.copy(design, f"{base_name}_tmp_shape")
        temps.append(blk2)
        work.unite([blk], keep_other=False)
        work = _largest()
        work.intersect(blk2, keep_other=False)
        work = _largest()
    except Exception:
        for b in temps:
            _safe_delete(b)
        for b in _comp_bodies(design, comp_id):
            if b.id not in before_ids:
                _safe_delete(b)
        raise

    # 只留體積最大者為簡化體；其餘（螺絲頭、彈簧、推銷、墊圈等不相連殘塊）清除
    _p("清除殘塊、建立 named selection 與命名")
    candidates =[b for b in _comp_bodies(design, comp_id) if b.id not in before_ids]
    vols = {b.id: b.volume.m_as(UNITS.m ** 3) for b in candidates}
    main = max(candidates, key=lambda b: vols[b.id])
    leftovers = [b for b in candidates if b.id != main.id]
    removed_vol = sum(vols[b.id] for b in leftovers)
    for b in leftovers:
        _safe_delete(b)

    # --- 7. 底面 named selection（主接合底面：同高度所有朝下平面）---
    ns_created = False
    main_planes = _horizontal_planes(main)
    _bf, y_ns = _main_bottom_plane(main_planes)
    bottom_faces = [p[0] for p in main_planes
                    if not p[3] and y_ns is not None and abs(p[1] - y_ns) <= _HS_EPS]
    if bottom_faces and named_selection:
        try:
            design.create_named_selection(named_selection, faces=bottom_faces)
            ns_created = True
        except Exception as e:
            logger.warning(f"建立底面 named selection '{named_selection}' 失敗: {e}")

    # --- 8. 反推等效密度並命名 ---
    v_sim = vols[main.id]
    if v_sim <= 0:
        raise ValueError(f"簡化體 '{base_name}' 體積量測異常 (V={v_sim})")
    rho_equiv = mass / v_sim  # kg/m³（質量守恆反推）
    final_name = f"{base_name}_rho{rho_equiv:.0f}" if name_density_suffix else base_name
    try:
        main.set_name(final_name)
    except Exception as e:
        logger.warning(f"重新命名簡化體為 '{final_name}' 失敗: {e}")
        final_name = base_name

    if not keep_source:
        for b in bodies:
            _safe_delete(b)

    return {
        "result_body": final_name, "component": comp.name, "parts": parts,
        "v_orig": v_orig, "mass": mass, "v_sim": v_sim, "rho_equiv": rho_equiv,
        "lo": lo, "hi": hi, "y_bot": y_bot, "y_root": y_root, "y_top": y_top,
        "shape": shape, "fin_axis": fin_axis, "holes": holes, "all_holes": all_holes,
        "corner_diag": corner_diag,
        "removed_count": len(leftovers), "removed_vol": removed_vol,
        "named_selection": named_selection if ns_created else None,
        "ns_faces": len(bottom_faces),
    }


def _format_heatsink_result(r, material, default_rho, hole_min_dia_mm):
    """將單組簡化結果整理為人類可讀報告（毫米、g、kg/m³）。"""
    lo, hi = r["lo"], r["hi"]
    size = [hi[i] - lo[i] for i in range(3)]
    root_txt = f"{_mm(r['y_root'])}" if r["y_root"] is not None else "（無獨立底板）"
    lines = [f"✓ '{r['parts'][0][0]}' → '{r['result_body']}'（component '{r['component']}'）"]
    if len(r["parts"]) > 1:
        lines.append(f"  併入 {len(r['parts'])} 個 body：" + ", ".join(
            f"{n}(ρ={rho:.0f})" for n, _v, rho in r["parts"][:12])
            + (" …" if len(r["parts"]) > 12 else ""))
    lines += [
        f"  材料/密度假設: {material} ρ={default_rho:.1f} kg/m³（可由 body_densities 逐 body 覆寫）",
        f"  原始體積 V_orig = {r['v_orig']*1e9:.3f} mm³；估算質量 m = {r['mass']*1000:.3f} g",
        f"  外包圍尺寸 (mm): {[_mm(s) for s in size]}",
        f"  高度層 (Y, mm): 主接合底面={_mm(r['y_bot'])}  鰭片根部={root_txt}  頂={_mm(r['y_top'])}",
        f"  凸字形方塊（鰭片走向={r['fin_axis']}）: "
        + "；".join(f"{label} X[{_mm(b[0][0])},{_mm(b[1][0])}] Y[{_mm(b[0][1])},{_mm(b[1][1])}] Z[{_mm(b[0][2])},{_mm(b[1][2])}]"
                   for label, b in (("底板", r["shape"]["plate"]), ("上凸", r["shape"]["top"]),
                                    ("下凸", r["shape"]["bottom"])) if b is not None),
        f"  鎖孔 {len(r['holes'])} 個（Y 向直圓柱，孔徑 ≥{hole_min_dia_mm}mm）: "
        + ", ".join(f"Ø{_mm(h['radius']*2)}@({_mm(h['cx'])},{_mm(h['cz'])})" for h in r["holes"]),
        f"  [診斷] 偵測到全部孔 {len(r.get('all_holes', []))} 個: "
        + ", ".join(f"Ø{_mm(h['radius']*2)}@({_mm(h['cx'])},{_mm(h['cz'])})"
                    f"[screw_r={_mm(h.get('screw_r',0)*2)},clr={_mm(h.get('clearance',0)*2)}]"
                    for h in r.get("all_holes", [])),
        f"  [診斷] 四角同軸Y圓柱群(僅內凹,凹角大/外側優先): "
        + "; ".join([f"@({_mm(g['cx'])},{_mm(g['cz'])})r={_mm(g['rmin']*2)}~{_mm(g['rmax']*2)}"
                     f"径距{_mm(g['radial'])}凹角{g['ang_cc']/3.14159:.2f}π"
                     f"{'[完整孔]' if g['full'] else '[未達完整]'}"
                     for g in r.get("corner_diag", []) if g.get("ang_cc", 0) > 0.01][:20]),
        f"  簡化後體積 V_sim = {r['v_sim']*1e9:.3f} mm³",
        f"  底面 named selection: {r['named_selection']}（{r['ns_faces']} 面）",
        f"  ★ 反推等效密度 ρ_equiv = m / V_sim = {r['rho_equiv']:.3f} kg/m³",
    ]
    return "\n".join(lines)


def _geom_simplify_heatsink(source: str, result_name: str = None,
                            density: float = None, material: str = "aluminum",
                            keep_source: bool = True,
                            named_selection: str = "hs_bottom",
                            name_density_suffix: bool = True,
                            hole_min_dia_mm: float = 2.5,
                            extra_sources: list[str] | None = None,
                            body_densities: dict | None = None,
                            all_instances: bool = False,
                            contact_body: str | None = None,
                            fin_box: str = "largest",
                            hole_select: str = "screw",
                            progress=None,
                            diagnose_only: bool = False) -> str:
    """將散熱片簡化為凸字形方塊組（底板＋上凸＋下凸＋鎖孔直圓柱），並反推等效密度。

    流程（每組 = 同一 component instance 內的 source + extra_sources）：
      1. 量測原始體積，以密度（material 預設或 body_densities 逐 body）算質量 m。
      2. 分析主接合底面/鰭片根部/鎖孔/鰭片排，以方塊重建（見 _simple_heatsink_boxes）；
         contact_body 指定接觸體（下凸）、fin_box 指定上凸取最大一排或全部鰭片外框。
      3. 鎖孔以 Y 向直圓柱貫穿；主接合底面建立 named selection；ρ_equiv = m / V_sim 附加於 body 名稱。
    """
    _p = progress or (lambda _msg: None)
    design = _geom_get_design()
    _p(f"搜尋散熱片 body '{source}'")
    groups = _resolve_heatsink_groups(design, source, extra_sources, all_instances)
    if not groups:
        all_names = sorted({b.name for b in design.bodies})
        return f"錯誤：找不到散熱片實體 body '{source}'。根層實體: {all_names}"

    rho = density
    if rho is None:
        rho = HEATSINK_DENSITY_PRESETS.get((material or "aluminum").lower(),
                                           HEATSINK_DENSITY_PRESETS["aluminum"])

    reports, errors = [], []
    for idx, bodies in enumerate(groups, start=1):
        base = result_name or f"{source}_sim"
        if len(groups) > 1:
            base = f"{base}_{idx:02d}"
        ns = named_selection
        if ns and len(groups) > 1:
            ns = f"{ns}_{idx:02d}"
        try:
            r = _simplify_heatsink_group(design, bodies, base, rho, body_densities, keep_source,
                                         ns, name_density_suffix, hole_min_dia_mm,
                                         contact_body=contact_body, fin_box=fin_box,
                                         hole_select=hole_select,
                                         progress=lambda m, i=idx: _p(f"[{i}/{len(groups)}] {m}"),
                                         diagnose_only=diagnose_only)
            reports.append(_format_heatsink_result(r, material, rho, hole_min_dia_mm))
        except TimeoutError as e:
            errors.append(f"✗ component '{bodies[0].parent_component.name}': {e}（暫存幾何已清除，其餘組未處理）")
            break
        except Exception as e:
            errors.append(f"✗ component '{bodies[0].parent_component.name}': {e}（暫存幾何已清除）")

    head = f"散熱片簡化完成 {len(reports)}/{len(groups)} 組（'{source}'）"
    return "\n".join([head] + reports + errors)


# ===================================================================
# GEOMETRY HELPERS — SpaceClaim 伺服器端截圖
# ===================================================================
# PyAnsys Geometry 25.1 + 無 graphics 套件環境下，Python 端無法 tessellate/plot
# （get_raw_tessellation 需 26.1；get_vtk_tessellation 需 pyvista）。故改走
# Modeler.run_script_file 送 IronPython 到 SpaceClaim 伺服器端，呼叫
# Window.ActiveWindow.Export(WindowExportFormat.<fmt>, path) 直接出圖。可選標準視角、
# 僅顯示指定 body、ZoomExtents；出圖後還原原視角與 body 可見性。
# API 命名空間（V261/V251/…）優先取實際已載入的組件。

_SCREENSHOT_VIEWS = ("current", "iso", "front", "back", "top", "bottom", "left", "right")
_SCREENSHOT_FORMATS = {"png": "png", "jpg": "jpg", "jpeg": "jpg", "bmp": "bmp",
                       "tif": "tiff", "tiff": "tiff", "gif": "gif"}

_SCREENSHOT_SCRIPT = r'''
# -*- coding: utf-8 -*-
# SpaceClaim server-side IronPython screenshot script (ASCII only).
# script_args: out_path_hex, img_format(png/jpg/bmp/tiff/gif), fit(1/0), view,
#              bodies_hex(newline separated names)
# *_hex = UTF-8 bytes as hex: non-ASCII (e.g. CJK body names / paths) passed directly in
# script_args fails to decode on the server, so they travel as ASCII hex and are decoded via .NET.
import sys
result = {}

def _utf8_hex(h):
    import System
    h = str(h or "")
    n = len(h) // 2
    if n == 0:
        return u""
    arr = System.Array.CreateInstance(System.Byte, n)
    for i in range(n):
        arr[i] = System.Byte(int(h[2 * i:2 * i + 2], 16))
    return System.Text.Encoding.UTF8.GetString(arr)

def _load_api():
    import System
    # Prefer the newest API assembly actually loaded, then fall back to a fixed list
    loaded = []
    for asm in System.AppDomain.CurrentDomain.GetAssemblies():
        try:
            nm = asm.GetName().Name
        except Exception:
            continue
        if nm and nm.startswith("SpaceClaim.Api.V") and nm.count(".") == 2:
            loaded.append(nm.split(".")[-1])
    def _ver(v):
        try:
            return int(v[1:])
        except Exception:
            return 0
    names = sorted(set(loaded), key=_ver, reverse=True)
    names += ["V262", "V261", "V252", "V251", "V242", "V241", "V232", "V231", "V22", "V21", "V20", "V19"]
    for v in names:
        try:
            mod = __import__("SpaceClaim.Api." + v, fromlist=["Window", "WindowExportFormat"])
            mod.Window
            return mod, v
        except Exception:
            continue
    raise RuntimeError("No usable SpaceClaim.Api.Vxxx namespace found")

def _arg(d, k, default):
    # argsDict is a .NET Dictionary[str, object]; it has no Python .get()
    try:
        if d.ContainsKey(k):
            return d[k]
    except Exception:
        try:
            return d[k]
        except Exception:
            pass
    return default

def _warn(key, msg):
    if result.get(key):
        result[key] = result[key] + "; " + str(msg)
    else:
        result[key] = str(msg)

# View definition: (screen right dir, screen up dir); view normal = right x up (Y-up frame)
_VIEW_AXES = {
    "front":  ((1, 0, 0), (0, 1, 0)),
    "back":   ((-1, 0, 0), (0, 1, 0)),
    "top":    ((1, 0, 0), (0, 0, -1)),
    "bottom": ((1, 0, 0), (0, 0, 1)),
    "right":  ((0, 0, -1), (0, 1, 0)),
    "left":   ((0, 0, 1), (0, 1, 0)),
    "iso":    ((1, 0, -1), (-1, 2, -1)),
}

def _set_view(api, w, view):
    Frame, Point, Direction = api.Geometry.Frame, api.Geometry.Point, api.Geometry.Direction
    rx, up = _VIEW_AXES[view]
    frame = Frame.Create(Point.Origin, Direction.Create(*rx), Direction.Create(*up))
    errs = []
    # Window.SetProjection expects a Matrix (V251): the projection maps world -> view,
    # i.e. the inverse of the mapping of the view frame
    try:
        w.SetProjection(_sc(api, "Matrix").CreateMapping(frame).Inverse, True, False)
        return
    except Exception:
        errs.append("Window.SetProjection(Matrix): " + str(sys.exc_info()[1]))
    try:
        w.SetProjection(frame, True, False)
        return
    except Exception:
        errs.append("Window.SetProjection(Frame): " + str(sys.exc_info()[1]))
    raise RuntimeError(" | ".join(errs))

def _sc(api, name):
    # SpaceClaim injects ViewHelper/Selection/Matrix as script globals; fall back to the API namespaces
    g = globals()
    if name in g:
        return g[name]
    for ns in ("Scripting", "Geometry"):
        try:
            return getattr(getattr(api, ns), name)
        except Exception:
            pass
    raise RuntimeError("SpaceClaim API symbol not found: " + name)

def _all_bodies(api, w):
    part = w.Document.MainPart
    try:
        return list(part.GetDescendants[api.IDesignBody]())
    except Exception:
        return list(part.Bodies)

try:
    import System
    out_path = _utf8_hex(_arg(argsDict, "out_path_hex", ""))
    img_format = str(_arg(argsDict, "img_format", "png") or "png").lower()
    fit = str(_arg(argsDict, "fit", "1")) in ("1", "true", "True")
    view = str(_arg(argsDict, "view", "current") or "current").lower()
    body_names = [n for n in _utf8_hex(_arg(argsDict, "bodies_hex", "")).split("\n") if n]

    api, api_ver = _load_api()
    result["api"] = api_ver
    Window = api.Window
    WindowExportFormat = api.WindowExportFormat
    enum_name = {"png": "Png", "jpg": "Jpeg", "bmp": "Bmp", "tiff": "Tiff", "gif": "Gif"}[img_format]
    fmt = getattr(WindowExportFormat, enum_name, None)

    w = Window.ActiveWindow
    if fmt is None:
        result["ok"] = "no"
        result["error"] = "WindowExportFormat of this SpaceClaim version does not support " + enum_name
    elif w is None:
        result["ok"] = "no"
        result["error"] = "no active window (Window.ActiveWindow is None); SpaceClaim may be running without GUI"
    else:
        # Remember the original view so it can be restored
        orig_proj = None
        try:
            orig_proj = w.Projection
        except Exception:
            pass
        hidden = []
        try:
            if body_names:
                bodies = _all_bodies(api, w)
                wanted = set(body_names)
                found = set([b.Name for b in bodies if b.Name in wanted])
                missing = [n for n in body_names if n not in found]
                if missing:
                    raise RuntimeError("body not found: " + ", ".join(missing))
                # Per-body SetVisibility does not hide component occurrences reliably;
                # ViewHelper.HideOthers isolates the selection and ShowAll restores it.
                keep = [b for b in bodies if b.Name in wanted]
                try:
                    _sc(api, "ViewHelper").HideOthers(_sc(api, "Selection").Create(keep))
                    hidden.append("__all__")
                except Exception:
                    _warn("isolate_warn", sys.exc_info()[1])
                result["hidden_count"] = str(len(bodies) - len(keep))

            if view != "current":
                try:
                    _set_view(api, w, view)
                except Exception:
                    _warn("view_warn", sys.exc_info()[1])

            if fit:
                try:
                    w.ZoomExtents()
                except Exception:
                    _warn("fit_warn", sys.exc_info()[1])

            # Delete any old file first so a failed Export is not mistaken for success
            if System.IO.File.Exists(out_path):
                System.IO.File.Delete(out_path)
            w.Export(fmt, out_path)
            result["ok"] = "yes" if System.IO.File.Exists(out_path) else "no"
            if result["ok"] != "yes":
                result["error"] = "Export produced no file"
            result["out_path"] = out_path
            try:
                result["bytes"] = str(System.IO.FileInfo(out_path).Length)
            except Exception:
                pass
        finally:
            if hidden:
                try:
                    _sc(api, "ViewHelper").ShowAll()
                except Exception:
                    _warn("restore_warn", "ShowAll: " + str(sys.exc_info()[1]))
            if orig_proj is not None and (fit or view != "current"):
                try:
                    w.SetProjection(orig_proj, True, False)
                except Exception:
                    _warn("restore_warn", "view restore failed: " + str(sys.exc_info()[1]))
except Exception:
    import sys as _s
    e = _s.exc_info()[1]
    result["ok"] = "no"
    result["error"] = str(e)
'''


def _geom_screenshot(file_path: str, image_format: str | None = None,
                     fit: bool = True, view: str = "current",
                     bodies: list[str] | None = None) -> str:
    """送 IronPython 腳本到 SpaceClaim 伺服器端，將 3D 視窗出圖為影像檔。

    回傳 JSON 字串（由工具層 as_envelope 解析為信封 dict）。

    - file_path: 輸出影像絕對/相對路徑（相對則轉絕對；無副檔名則依格式補上）。
    - image_format: png/jpg/bmp/tiff/gif；省略則依副檔名推斷（無副檔名則 png）。
    - fit: 截圖前是否 ZoomExtents 全景縮放。
    - view: current/iso/front/back/top/bottom/left/right。
    - bodies: 僅顯示這些 body（依名稱）；截圖後還原可見性。
    """
    import json
    import tempfile

    def _err(msg: str) -> str:
        return json.dumps({"ok": False, "error": msg}, ensure_ascii=False)

    if _modeler is None:
        return _err("Geometry 未連線，請先執行 geometry_launch")

    out_path = os.path.abspath(file_path)
    ext = os.path.splitext(out_path)[1].lower().lstrip(".")
    if image_format:
        fmt = _SCREENSHOT_FORMATS.get(image_format.lower())
        if fmt is None:
            return _err(f"不支援的影像格式 '{image_format}'，可用: {sorted(_SCREENSHOT_FORMATS)}")
        if ext and _SCREENSHOT_FORMATS.get(ext) != fmt:
            return _err(f"image_format='{image_format}' 與副檔名 '.{ext}' 不一致")
    elif ext:
        fmt = _SCREENSHOT_FORMATS.get(ext)
        if fmt is None:
            return _err(f"無法由副檔名 '.{ext}' 推斷影像格式，可用: {sorted(_SCREENSHOT_FORMATS)}")
    else:
        fmt = "png"
    if not ext:
        out_path += "." + fmt

    view = (view or "current").lower()
    if view not in _SCREENSHOT_VIEWS:
        return _err(f"不支援的視角 '{view}'，可用: {list(_SCREENSHOT_VIEWS)}")

    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.isdir(out_dir):
        try:
            os.makedirs(out_dir, exist_ok=True)
        except Exception as e:
            return _err(f"無法建立輸出目錄 '{out_dir}': {e}")

    # 非 ASCII（中文 body 名稱/路徑）直接放 script_args 會在 server 端解碼失敗，改傳 UTF-8 hex
    script_args = {
        "out_path_hex": out_path.encode("utf-8").hex(),
        "img_format": fmt,
        "fit": "1" if fit else "0",
        "view": view,
        "bodies_hex": "\n".join(bodies or []).encode("utf-8").hex(),
    }

    tmp = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
    try:
        tmp.write(_SCREENSHOT_SCRIPT)
        tmp.close()
        values, _design = _modeler.run_script_file(tmp.name, script_args=script_args)
    except Exception as e:
        return _err(f"SpaceClaim 截圖腳本執行失敗: {e}")
    finally:
        try:
            os.remove(tmp.name)
        except Exception:
            pass

    values = dict(values or {})
    if str(values.get("ok", "")).lower() != "yes":
        return _err(f"截圖失敗: {values.get('error', '未知錯誤')}（view={view}, fit={fit}）")

    size = str(values.get("bytes", ""))
    out = {
        "ok": True,
        "file_path": out_path,
        "format": fmt,
        "bytes": int(size) if size.isdigit() else None,
        "view": view,
        "fit": fit,
        "api": values.get("api"),
        # server 在遠端/容器時，檔案寫在 server 端，client 端不一定看得到
        "local_file_exists": os.path.isfile(out_path),
    }
    if bodies:
        out["isolated_bodies"] = list(bodies)
    warnings = [f"{k}: {values[k]}" for k in ("view_warn", "fit_warn", "isolate_warn", "restore_warn")
                if values.get(k)]
    if warnings:
        out["warnings"] = warnings
    return json.dumps(out, ensure_ascii=False)


# ===================================================================
# GEOMETRY HELPERS — SpaceClaim 伺服器端中曲面 (midsurface)
# ===================================================================
# 由 SpaceClaim ACT callback (SC_midsurface_Agent.py) 改寫為 MCP 工具：
#   * 原 onupdateStep(step) 讀 step.Properties → 改讀 run_script_file 的 argsDict
#   * 原對 Selection.GetActive() 中已選取的 IDesignBody 批次建立中曲面
#   * 回傳 result dict（成功/略過/失敗計數與逐 body 詳情），不彈 MessageBox
# 入參（script_args 皆為字串）：max_thickness_mm, main_surface_ratio,
#   area_difference_ratio, complex_area_diff, enable_sheet_metal_check(1/0),
#   hide_source_bodies(1/0)

_MIDSURFACE_SCRIPT = r'''
# -*- coding: utf-8 -*-
# SpaceClaim server-side IronPython midsurface script (ASCII only).
import sys
result = {}

def _load_api():
    import System
    loaded = []
    for asm in System.AppDomain.CurrentDomain.GetAssemblies():
        try:
            nm = asm.GetName().Name
        except Exception:
            continue
        if nm and nm.startswith("SpaceClaim.Api.V") and nm.count(".") == 2:
            loaded.append(nm.split(".")[-1])
    def _ver(v):
        try:
            return int(v[1:])
        except Exception:
            return 0
    names = sorted(set(loaded), key=_ver, reverse=True)
    names += ["V262", "V261", "V252", "V251", "V242", "V241", "V232", "V231"]
    for v in names:
        try:
            mod = __import__("SpaceClaim.Api." + v, fromlist=["IDesignBody"])
            mod.IDesignBody
            return mod, v
        except Exception:
            continue
    raise RuntimeError("No usable SpaceClaim.Api.Vxxx namespace found")

def _arg(d, k, default):
    try:
        if d.ContainsKey(k):
            return d[k]
    except Exception:
        try:
            return d[k]
        except Exception:
            pass
    return default

def _f(d, k, default):
    try:
        return float(_arg(d, k, default))
    except Exception:
        return float(default)

def _b(d, k, default):
    return str(_arg(d, k, "1" if default else "0")) in ("1", "true", "True")

try:
    api, api_ver = _load_api()
    result["api"] = api_ver

    IDesignBody = api.IDesignBody
    MidSurfaceOffsetType = api.MidSurfaceOffsetType
    Midsurface = api.Scripting.Commands.Midsurface
    VisibilityType = api.Scripting.Commands.VisibilityType
    MidsurfaceOptions = api.Scripting.Commands.CommandOptions.MidsurfaceOptions
    CreationLocation = api.Scripting.Commands.CommandOptions.CreationLocation
    DesignFaceExtensions = api.Scripting.Extensions.DesignFaceExtensions
    MeasureHelper = api.Scripting.Helpers.MeasureHelper
    ViewHelper = api.Scripting.Helpers.ViewHelper
    BodySelection = api.Scripting.Selection.BodySelection
    FaceSelection = api.Scripting.Selection.FaceSelection
    Selection = api.Scripting.Selection.Selection

    # mm -> m (SpaceClaim API works in meters)
    max_thickness = _f(argsDict, "max_thickness_mm", 6.0) / 1000.0
    main_surface_ratio = _f(argsDict, "main_surface_ratio", 0.7)
    area_difference_ratio = _f(argsDict, "area_difference_ratio", 0.1)
    complex_area_diff = _f(argsDict, "complex_area_diff", 0.05)
    enable_sheet_metal_check = _b(argsDict, "enable_sheet_metal_check", True)
    hide_source_bodies = _b(argsDict, "hide_source_bodies", True)

    if max_thickness <= 0.0:
        result["ok"] = "no"
        result["error"] = "max_thickness_mm must be greater than 0"
        raise SystemExit

    def get_face_area(face):
        try:
            return face.Shape.Area
        except Exception:
            return face.Area

    def get_body_faces(body):
        return [face for face in body.Faces]

    def get_tangent_chain(face):
        return [tf for tf in DesignFaceExtensions.GetTangentChain(face)]

    def get_unique_faces(faces):
        uniq = []
        for face in faces:
            dup = False
            for known in uniq:
                if face == known:
                    dup = True
                    break
            if not dup:
                uniq.append(face)
        return uniq

    def get_total_area(faces):
        return sum(get_face_area(f) for f in faces)

    def get_gap_distance(f1, f2):
        s1 = FaceSelection.Create(f1)
        s2 = FaceSelection.Create(f2)
        return MeasureHelper.DistanceBetweenObjects(s1, s2).Distance

    def are_normals_opposed(f1, f2):
        try:
            n1 = DesignFaceExtensions.GetFaceNormal(f1, 0.5, 0.5)
            n2 = DesignFaceExtensions.GetFaceNormal(f2, 0.5, 0.5)
            return abs(n1.Dot(n2)) > 0.99
        except Exception:
            return True

    def find_primary_face_pair(body):
        faces = get_body_faces(body)
        if len(faces) < 2:
            return None
        faces.sort(key=get_face_area, reverse=True)
        first = faces[0]
        first_area = get_face_area(first)
        for second in faces[1:]:
            if not are_normals_opposed(first, second):
                continue
            second_area = get_face_area(second)
            rad = abs(first_area - second_area) / max(first_area, second_area)
            if rad > area_difference_ratio:
                continue
            try:
                dist = get_gap_distance(first, second)
            except Exception:
                continue
            if 0.0 < dist <= max_thickness:
                return (first, second, dist)
        return None

    def is_sheet_metal_body(body, f1, f2, thickness):
        c1 = get_unique_faces(get_tangent_chain(f1))
        c2 = get_unique_faces(get_tangent_chain(f2))
        primary = get_unique_faces(c1 + c2)
        a1 = get_total_area(c1)
        a2 = get_total_area(c2)
        all_area = get_total_area(get_body_faces(body))
        if all_area <= 0.0:
            return False
        rad = abs(a1 - a2) / max(a1, a2)
        psr = get_total_area(primary) / all_area
        return (thickness <= max_thickness and rad <= area_difference_ratio
                and psr >= main_surface_ratio)

    def create_midsurface(f1, f2, force_tangent):
        opts = MidsurfaceOptions()
        opts.AllowNonManifold = False
        opts.ExtendSurfaces = True
        opts.CreationLocation = CreationLocation.ActiveComponent
        opts.Group = True
        opts.OffsetType = MidSurfaceOffsetType.Middle
        cmd = Midsurface(opts)
        if force_tangent:
            cmd.AddMatchingFacePairs(f1, f2, 1.0e-5, False)
            for fs in get_tangent_chain(f1):
                cmd.AddMatchingFacePairs(None, fs)
            for fs in get_tangent_chain(f2):
                cmd.AddMatchingFacePairs(None, fs)
        else:
            cmd.AddMatchingFacePairs(f1, f2, 1.0e-5, True)
        r = cmd.Execute()
        if not r.Success:
            raise RuntimeError("Midsurface command did not complete successfully")

    def get_body_name(body):
        try:
            return body.Name
        except Exception:
            return "<unnamed body>"

    def hide_body(body):
        ViewHelper.SetObjectVisibility(BodySelection.Create(body),
                                       VisibilityType.Hide, False, False)

    selected = [b for b in Selection.GetActive().GetItems[IDesignBody]()]
    result["selected_count"] = str(len(selected))
    if not selected:
        result["ok"] = "no"
        result["error"] = "no body selected (Selection.GetActive is empty)"
        raise SystemExit

    success = 0
    skipped = 0
    failed = 0
    details = []
    for body in selected:
        bn = get_body_name(body)
        try:
            pair = find_primary_face_pair(body)
            if pair is None:
                failed += 1
                details.append("[" + bn + "] FAIL: no valid primary opposing face pair")
                continue
            f1, f2, thickness = pair
            if enable_sheet_metal_check and not is_sheet_metal_body(body, f1, f2, thickness):
                skipped += 1
                details.append("[" + bn + "] SKIP: sheet-metal check not passed")
                continue
            a1 = get_face_area(f1)
            a2 = get_face_area(f2)
            adiff = abs(a1 - a2) / max(a1, a2)
            is_complex = (adiff > complex_area_diff)
            create_midsurface(f1, f2, is_complex)
            if hide_source_bodies:
                hide_body(body)
            success += 1
            mode = "complex" if is_complex else "simple"
            details.append("[" + bn + "] OK: midsurface created (" + mode
                           + ", area_diff=" + ("%.1f" % (adiff * 100.0)) + "%)")
        except Exception:
            failed += 1
            details.append("[" + bn + "] FAIL: " + str(sys.exc_info()[1]))

    result["ok"] = "yes"
    result["success"] = str(success)
    result["skipped"] = str(skipped)
    result["failed"] = str(failed)
    result["details"] = "\n".join(details)
except SystemExit:
    pass
except Exception:
    e = sys.exc_info()[1]
    result["ok"] = "no"
    result["error"] = str(e)
'''


def _geom_midsurface(max_thickness_mm: float = 6.0, main_surface_ratio: float = 0.7,
                     area_difference_ratio: float = 0.1, complex_area_diff: float = 0.05,
                     enable_sheet_metal_check: bool = True,
                     hide_source_bodies: bool = True) -> str:
    """送 IronPython 腳本到 SpaceClaim 伺服器端，對目前「已選取」的 body 批次建立中曲面。

    由 SC_midsurface_Agent.py (ACT callback) 改寫。呼叫前需在 SpaceClaim 視窗中
    先選取欲抽中面的 body。回傳 JSON 字串（工具層 as_envelope 解析為信封）。
    """
    import json
    import tempfile

    def _err(msg: str) -> str:
        return json.dumps({"ok": False, "error": msg}, ensure_ascii=False)

    if _modeler is None:
        return _err("Geometry 未連線，請先執行 geometry_launch")
    if max_thickness_mm is None or max_thickness_mm <= 0:
        return _err("max_thickness_mm 必須大於 0")

    script_args = {
        "max_thickness_mm": str(max_thickness_mm),
        "main_surface_ratio": str(main_surface_ratio),
        "area_difference_ratio": str(area_difference_ratio),
        "complex_area_diff": str(complex_area_diff),
        "enable_sheet_metal_check": "1" if enable_sheet_metal_check else "0",
        "hide_source_bodies": "1" if hide_source_bodies else "0",
    }

    tmp = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
    try:
        tmp.write(_MIDSURFACE_SCRIPT)
        tmp.close()
        values, _design = _modeler.run_script_file(tmp.name, script_args=script_args)
    except Exception as e:
        return _err(f"SpaceClaim 中曲面腳本執行失敗: {e}")
    finally:
        try:
            os.remove(tmp.name)
        except Exception:
            pass

    values = dict(values or {})
    if str(values.get("ok", "")).lower() != "yes":
        return _err(f"中曲面建立失敗: {values.get('error', '未知錯誤')}")

    def _int(k):
        v = str(values.get(k, "0"))
        return int(v) if v.isdigit() else 0

    out = {
        "ok": True,
        "selected_count": _int("selected_count"),
        "success": _int("success"),
        "skipped": _int("skipped"),
        "failed": _int("failed"),
        "api": values.get("api"),
    }
    details = values.get("details")
    if details:
        out["details"] = details.split("\n")
    return json.dumps(out, ensure_ascii=False)


# ===================================================================
# GEOMETRY HELPERS — SpaceClaim 伺服器端孔配對 RM 群組 (hole pairing)
# ===================================================================
# 由 SpaceClaim ACT callback (SC_RM_grp_creation.py) 改寫為 MCP 工具：
#   * 原 onupdateStep(step) 讀 step.Properties → 改讀 run_script_file 的 argsDict
#   * 移除 MessageBox / log_usage / 到期鎖定；改以 result dict 回報統計
#   * 對 Selection.GetActive() 的選取集 (或既有命名群組) 偵測圓孔/半圓孔並建立
#     named selection 群組，再對同軸、距離在門檻內的孔兩兩配對建立 RM 連接群組。
# 入參（script_args 皆為字串）：diameter_min_mm, diameter_max_mm, mode(0/1),
#   pairing_strategy, distance_min_mm, distance_max_mm, holes_axis_dist_max_mm,
#   deg_max_circles, grp_name_create, index_grp_start, rm_grp_create(1/0),
#   rm_grp_name_create, index_rm_start, grp_name_not_go,
#   enable_distance_grouping(1/0), distance_level1_mm, distance_level2_mm

_RM_GROUP_SCRIPT = r'''
# -*- coding: utf-8 -*-
# SpaceClaim server-side IronPython hole-pairing / RM group script (ASCII only).
import sys
import math
result = {}

def get_spaceclaim_api():
    import System
    loaded = []
    for asm in System.AppDomain.CurrentDomain.GetAssemblies():
        try:
            nm = asm.GetName().Name
        except Exception:
            continue
        if nm and nm.startswith("SpaceClaim.Api.V") and nm.count(".") == 2:
            loaded.append(nm.split(".")[-1])
    def _ver(v):
        try:
            return int(v[1:])
        except Exception:
            return 0
    names = sorted(set(loaded), key=_ver, reverse=True)
    names += ["V262", "V261", "V252", "V251", "V242", "V241", "V232", "V231"]
    import clr
    for ver in names:
        try:
            clr.AddReference("SpaceClaim.Api." + ver)
            clr.AddReference("SpaceClaim.Api." + ver + ".Scripting")
            import SpaceClaim.Api
            sc_api = getattr(SpaceClaim.Api, ver)
            clr.ImportExtensions(sc_api.Scripting.Extensions.DesignFaceExtensions)
            clr.ImportExtensions(sc_api.Scripting.Extensions.DesignEdgeExtensions)
            clr.ImportExtensions(sc_api.Scripting.Extensions.DesignBodyExtensions)
            clr.ImportExtensions(sc_api.Scripting.Extensions.ComponentExtensions)
            clr.ImportExtensions(sc_api.Scripting.Extensions.DocObjectExtensions)
            return sc_api, ver
        except Exception:
            continue
    raise RuntimeError("SpaceClaim API Reference Error: compatible version not found")

def _arg(d, k, default):
    try:
        if d.ContainsKey(k):
            return d[k]
    except Exception:
        try:
            return d[k]
        except Exception:
            pass
    return default

def _f(d, k, default):
    try:
        return float(_arg(d, k, default))
    except Exception:
        return float(default)

def _i(d, k, default):
    try:
        return int(float(_arg(d, k, default)))
    except Exception:
        return int(default)

def _b(d, k, default):
    return str(_arg(d, k, "1" if default else "0")) in ("1", "true", "True", "Yes", "yes")

def _s(d, k, default):
    v = _arg(d, k, default)
    return default if v is None else str(v)

try:
    sc, api_ver = get_spaceclaim_api()
    result["api"] = api_ver
    Selection = sc.Scripting.Selection.Selection
    MeasureHelper = sc.Scripting.Helpers.MeasureHelper
    NamedSelection = sc.Scripting.Commands.NamedSelection

    # mm inputs -> meters
    Diameter_min = _f(argsDict, "diameter_min_mm", 2.0) / 1000.0
    Diameter_max = _f(argsDict, "diameter_max_mm", 20.0) / 1000.0
    mode = _i(argsDict, "mode", 0)
    Pairing_Strategy = _s(argsDict, "pairing_strategy", "Ignore Component")
    Distance_min_check_circle = _f(argsDict, "distance_min_mm", 0.0) / 1000.0
    Distance_max_check_circle = _f(argsDict, "distance_max_mm", 10.0) / 1000.0
    Holes_axis_dist_max = _f(argsDict, "holes_axis_dist_max_mm", 1.0) / 1000.0
    Deg_max_circles = _f(argsDict, "deg_max_circles", 10.0)
    grp_name_create = _s(argsDict, "grp_name_create", "Scr_AllHoles")
    Index_grp_start = _i(argsDict, "index_grp_start", 1)
    RM_grp_create_exe = _b(argsDict, "rm_grp_create", True)
    RM_grp_name_create = _s(argsDict, "rm_grp_name_create", "Scr_RMgrp")
    Index_RM_start = _i(argsDict, "index_rm_start", 1)
    grp_name_NOTGoConnections = _s(argsDict, "grp_name_not_go", "NOTGoConnections")
    Enable_Distance_Grouping = _b(argsDict, "enable_distance_grouping", False)
    Distance_Level1 = _f(argsDict, "distance_level1_mm", 5.0) / 1000.0
    Distance_Level2 = _f(argsDict, "distance_level2_mm", 20.0) / 1000.0

    Groupname_index = 'Scr_AllHoles_0821'
    grp_name_FullCircle_edges = grp_name_create + "_FullCircles"
    grp_name_HalfCircle_edges = grp_name_create + "_HalfCircles"
    Distance_min_check_Line = Distance_min_check_circle
    Distance_max_check_Line = Distance_max_check_circle

    def CheckHierarchicalPairing(e1, e2, strategy):
        try:
            c1 = e1.Parent.Parent
            c2 = e2.Parent.Parent
            if "Ignore Component" in strategy:
                return True
            elif "Within Component" in strategy:
                return c1 == c2
            return True
        except Exception:
            return True

    def GetHierarchyTypeForStats(e1, e2):
        try:
            b1 = e1.Parent
            b2 = e2.Parent
            if b1 == b2:
                return "SameBody"
            if b1.Parent == b2.Parent:
                return "Internal"
            return "External"
        except Exception:
            return ""

    def GetDistanceSuffix(distance, enable):
        if not enable:
            return ""
        if distance <= Distance_Level1:
            return "_Near"
        elif distance <= Distance_Level2:
            return "_Medium"
        return "_Far"

    def ConvertEdgesByShape(selection, ShapeType):
        item_list = []
        t = selection.GetType()
        if (t != Selection and t != sc.Scripting.Selection.EdgeSelection
                and t != sc.Scripting.Selection.FaceSelection):
            return Selection.Empty()
        selection = selection.ConvertToEdges()
        for item in selection.Items:
            if item.Shape.Geometry.GetType() == ShapeType:
                item_list.append(item)
        if len(item_list) == 0:
            return Selection.Empty()
        return Selection.Create(item_list)

    def FindCircles(selection, D_min, D_max, Cmode, Fmode):
        holes_list = []
        edges_sel = selection.ConvertToEdges()
        circles_sel = edges_sel.ConvertByShape(sc.Scripting.Selection.GeometryType.Circle)
        if circles_sel.Count != 0:
            fc = circles_sel.FilterByRadius(D_min / 2, D_max / 2)
            for edge in fc.Items:
                circ = 2 * 3.14 * edge.Shape.Geometry.Radius
                if Cmode == 0:
                    if edge.Shape.Length > circ:
                        holes_list.append(edge)
                elif Cmode == 1:
                    if edge.Shape.Length < circ * 0.51 and edge.Shape.Length > circ * 0.49:
                        holes_list.append(edge)
                elif Cmode == 2:
                    if edge.Shape.Length < circ * 0.5:
                        holes_list.append(edge)
        nurbs = ConvertEdgesByShape(edges_sel, sc.Geometry.NurbsCurve)
        proc = ConvertEdgesByShape(edges_sel, sc.Geometry.ProceduralCurve)
        sel = nurbs + proc
        filter_curve = []
        if sel.Count != 0:
            for i in sel.Items:
                length = i.Shape.Length
                pt1 = i.Shape.StartPoint
                pt2 = i.Shape.EndPoint
                dist_pt12 = sc.Scripting.Helpers.Gap.Create(pt1, pt2).Distance
                if not dist_pt12 == 0:
                    d = dist_pt12
                else:
                    d = length / 3.1415926
                if d <= D_max and d >= D_min:
                    if Cmode == 0:
                        if dist_pt12 == 0:
                            filter_curve.append(i)
                    elif Cmode == 1:
                        if abs(length - 2 * 3.14 * d / 2 * 0.5) / length < 0.01:
                            filter_curve.append(i)
                    elif Cmode == 2:
                        if length < 2 * 3.14 * d / 2 * 0.5:
                            filter_curve.append(i)
        holes_list = holes_list + filter_curve
        for hole in list(holes_list):
            if hole.Parent.Shape.Volume == 0:
                if not hole.Faces.Count == 1 and Fmode == 1:
                    holes_list.remove(hole)
        return holes_list

    def GetGroupNameANDIndex(name_create, idx_start):
        try:
            groups = NamedSelection.GetGroups(sc.Scripting.Helpers.DocumentHelper.GetRootPart())
        except Exception:
            groups = NamedSelection.GetGroups()
        existing = []
        for grp in groups:
            if grp.IsDeleted:
                continue
            if grp.Name == 'Scr_RMgrp_ALL':
                continue
            if grp.Name.IndexOf(name_create) != -1:
                existing.append(grp.Name)
        same = 0
        gn = ''
        while same == 0:
            gn = name_create + "_" + str(idx_start)
            same = 1
            if gn in existing:
                idx_start = idx_start + 1
                same = 0
        return gn, idx_start

    Count_grp_new = 0
    Count_grp_replace = 0
    Count_Hierarchy = {"SameBody": 0, "Internal": 0, "External": 0}
    Count_Distance = {"Near": 0, "Medium": 0, "Far": 0}

    body_sel = Selection.GetActive()
    result["selected_count"] = str(len(body_sel.Items))

    grp_name = ''
    holes = []
    holes_0 = []
    holes_1 = []
    if not body_sel.Count == 0:
        if mode == 0:
            holes_0 = FindCircles(body_sel, Diameter_min, Diameter_max, 0, 1)
            holes_1 = FindCircles(body_sel, Diameter_min, Diameter_max, 1, 1)
            holes = holes_0 + holes_1
        else:
            holes = list(body_sel.Items)

        if len(holes) != 0:
            grp_name, Index_grp_start = GetGroupNameANDIndex(grp_name_create, Index_grp_start)
            hs = Selection.Create(holes)
            hs.CreateAGroup(grp_name)
            hs.SetActive()

        if mode == 0:
            if len(holes_0) != 0:
                g0, _tmp = GetGroupNameANDIndex(grp_name_FullCircle_edges, Index_grp_start)
                Selection.Create(holes_0).CreateAGroup(g0)
            if len(holes_1) != 0:
                g1, _tmp = GetGroupNameANDIndex(grp_name_HalfCircle_edges, Index_grp_start)
                Selection.Create(holes_1).CreateAGroup(g1)

    if RM_grp_create_exe:
        groups = NamedSelection.GetGroups(sc.Scripting.Helpers.DocumentHelper.GetRootPart())
        Edges_NOTGo = []
        for ig in groups:
            if ig.Name.IndexOf(grp_name_NOTGoConnections) != -1:
                Edges_NOTGo = ig.Members
                break
        NS0_RM_names = []
        for i in groups:
            if i.IsDeleted:
                continue
            if i.Name == 'Scr_RMgrp_ALL':
                continue
            if i.Name.find(RM_grp_name_create) != -1:
                NS0_RM_names.append(i.Name)

        edge_types = [sc.Geometry.NurbsCurve, sc.Geometry.ProceduralCurve, sc.Geometry.Circle]
        RM_Edges_all = []

        for grp in groups:
            if grp.IsDeleted:
                continue
            gn2 = grp.Name
            if gn2 == grp_name:
                pass
            elif body_sel.Count == 0 and Groupname_index != '' and gn2.find(Groupname_index) != -1:
                pass
            else:
                continue

            RM_Edges = grp.Members
            if mode == 0:
                rs = Selection.Create(RM_Edges)
                re0 = FindCircles(rs, Diameter_min, Diameter_max, 0, 1)
                re1 = FindCircles(rs, Diameter_min, Diameter_max, 1, 1)
                RM_Edges = re0 + re1

            RM_Edges = list(RM_Edges)
            for ei in list(RM_Edges):
                if ei in Edges_NOTGo:
                    RM_Edges.remove(ei)

            Edge_OnCheck_List = []
            Edge_ToBeMount_List = []
            for ei in range(len(RM_Edges) - 1):
                Edge_OnCheck = RM_Edges[ei]
                Edge_OnCheck_List.append(Edge_OnCheck)
                my_edges = [Edge_OnCheck]
                pt1 = Edge_OnCheck.Shape.StartPoint
                pt2 = Edge_OnCheck.Shape.EndPoint
                if sc.Scripting.Helpers.Gap.Create(pt1, pt2).Distance == 0:
                    pt2 = Edge_OnCheck.EvalMid().Point
                pt3 = sc.Geometry.Point.Create((pt1.X + pt2.X) / 2, (pt1.Y + pt2.Y) / 2, (pt1.Z + pt2.Z) / 2)
                R_on = sc.Scripting.Helpers.Gap.Create(pt1, pt3).Distance
                R_sphere = ((R_on * 3) ** 2 + Distance_max_check_circle ** 2) ** 0.5
                near = Selection.Create(RM_Edges).FilterByBoundingSphere(pt3, R_sphere).Items
                Edge_ToBeMount_List.append(near)
                for i in Edge_OnCheck_List:
                    if i in Edge_ToBeMount_List[ei]:
                        Edge_ToBeMount_List[ei].Remove(i)
                vector1 = Edge_OnCheck.Faces[0].GetFaceNormal(0, 0)

                for Edge_ToBeMount in Edge_ToBeMount_List[ei]:
                    if not CheckHierarchicalPairing(Edge_OnCheck, Edge_ToBeMount, Pairing_Strategy):
                        continue
                    s1 = Selection.Create(Edge_OnCheck, Edge_ToBeMount)
                    l1 = set(Edge_OnCheck.Faces)
                    l2 = set(Edge_ToBeMount.Faces)
                    pt4 = Edge_ToBeMount.Shape.StartPoint
                    pt5 = Edge_ToBeMount.Shape.EndPoint
                    if sc.Scripting.Helpers.Gap.Create(pt4, pt5).Distance == 0:
                        pt5 = Edge_ToBeMount.EvalMid().Point
                    pt6 = sc.Geometry.Point.Create((pt4.X + pt5.X) / 2, (pt4.Y + pt5.Y) / 2, (pt4.Z + pt5.Z) / 2)
                    vector2 = Edge_ToBeMount.Faces[0].GetFaceNormal(0, 0)
                    dot12 = abs(sc.Geometry.Vector.Dot(vector1.UnitVector, vector2.UnitVector)
                                / vector1.UnitVector.Magnitude / vector2.UnitVector.Magnitude)
                    if dot12 > 1:
                        dot12 = 1.0
                    deg12 = 180 / math.pi * math.acos(dot12)
                    vector_pt36 = sc.Scripting.Helpers.Gap.Create(pt3, pt6).GapVector
                    axesdist = sc.Geometry.Vector.Cross(vector_pt36, vector1.UnitVector).Magnitude / vector1.UnitVector.Magnitude

                    if mode == 0:
                        is_circ = (Edge_OnCheck.Shape.Geometry.GetType() == sc.Geometry.Circle
                                   and Edge_ToBeMount.Shape.Geometry.GetType() == sc.Geometry.Circle)
                        mindist = MeasureHelper.MinDistanceBetweenObjects(s1).Distance
                        if is_circ:
                            if mindist < Distance_max_check_circle and mindist > Distance_min_check_circle:
                                if l1.intersection(l2).Count == 0:
                                    if MeasureHelper.MinDistanceBetweenAxes(s1).Distance < Holes_axis_dist_max:
                                        if Edge_OnCheck.Shape.Geometry.Axis.Direction.IsParallel(Edge_ToBeMount.Shape.Geometry.Axis.Direction):
                                            if Edge_OnCheck.Parent.Shape.Volume != 0 and Edge_ToBeMount.Parent.Shape.Volume != 0:
                                                if Edge_OnCheck.Parent == Edge_ToBeMount.Parent:
                                                    continue
                                            my_edges.append(Edge_ToBeMount)
                        elif (edge_types.IndexOf(Edge_OnCheck.Shape.Geometry.GetType()) != -1
                              and edge_types.IndexOf(Edge_ToBeMount.Shape.Geometry.GetType()) != -1):
                            if mindist < Distance_max_check_circle and mindist > Distance_min_check_circle:
                                if l1.intersection(l2).Count == 0:
                                    if axesdist < Holes_axis_dist_max:
                                        if deg12 < Deg_max_circles:
                                            if Edge_OnCheck.Parent.Shape.Volume != 0 and Edge_ToBeMount.Parent.Shape.Volume != 0:
                                                if Edge_OnCheck.Parent == Edge_ToBeMount.Parent:
                                                    continue
                                            my_edges.append(Edge_ToBeMount)
                    else:
                        mindist = MeasureHelper.MinDistanceBetweenObjects(s1).Distance
                        if mindist < Distance_max_check_Line and mindist > Distance_min_check_Line:
                            if l1.intersection(l2).Count == 0:
                                my_edges.append(Edge_ToBeMount)

                if len(my_edges) > 1:
                    for me in my_edges:
                        if me not in RM_Edges_all:
                            RM_Edges_all.append(me)
                    groups2 = NamedSelection.GetGroups(sc.Scripting.Helpers.DocumentHelper.GetRootPart())
                    checked_in_group = 0
                    gn_existing = ''
                    for grp2 in groups2:
                        if checked_in_group == 1:
                            break
                        if grp2.IsDeleted:
                            continue
                        if grp2.Name == 'Scr_RMgrp_ALL':
                            continue
                        if grp2.Name.find(RM_grp_name_create) != -1:
                            members2 = grp2.Members
                            for me in my_edges:
                                if me in members2:
                                    checked_in_group = 1
                                    gn_existing = grp2.Name
                                    RM_Edges2 = members2
                                    break
                    if checked_in_group == 0:
                        base = RM_grp_name_create
                        htype = GetHierarchyTypeForStats(my_edges[0], my_edges[1])
                        if htype in Count_Hierarchy:
                            Count_Hierarchy[htype] += 1
                        if Enable_Distance_Grouping:
                            pd = MeasureHelper.MinDistanceBetweenObjects(Selection.Create(my_edges[0], my_edges[1])).Distance
                            suffix = GetDistanceSuffix(pd, True)
                            base += suffix
                            if "Near" in suffix:
                                Count_Distance["Near"] += 1
                            elif "Medium" in suffix:
                                Count_Distance["Medium"] += 1
                            elif "Far" in suffix:
                                Count_Distance["Far"] += 1
                        gn_new, Index_RM_start = GetGroupNameANDIndex(base, Index_RM_start)
                        sel = Selection.Create(my_edges)
                        sel.CreateAGroup(gn_new)
                        Index_RM_start = Index_RM_start + 1
                        Count_grp_new += 1
                        sel.SetActive()
                    else:
                        Selection.Clear()
                        merged = list(RM_Edges2)
                        for item in my_edges:
                            if item not in merged:
                                merged.append(item)
                        sel = Selection.Create(merged)
                        sel.SetActive()
                        NamedSelection.Delete(gn_existing)
                        sel.CreateAGroup(gn_existing)
                        if gn_existing in NS0_RM_names:
                            NS0_RM_names.remove(gn_existing)
                            Count_grp_replace += 1

        Selection.Create(RM_Edges_all).SetActive()

    # consolidate hole groups
    groups = NamedSelection.GetGroups(sc.Scripting.Helpers.DocumentHelper.GetRootPart())
    Circle_all = []
    FullCircle_all = []
    HalfCircle_all = []
    for ig in groups:
        if (ig.Name.IndexOf(grp_name_create) != -1
                and ig.Name.IndexOf(grp_name_FullCircle_edges) == -1
                and ig.Name.IndexOf(grp_name_HalfCircle_edges) == -1):
            for ie in ig.Members:
                Circle_all.append(ie)
            NamedSelection.Delete(ig.Name)
        elif ig.Name.IndexOf(grp_name_FullCircle_edges) != -1:
            for ie in ig.Members:
                FullCircle_all.append(ie)
            NamedSelection.Delete(ig.Name)
        elif ig.Name.IndexOf(grp_name_HalfCircle_edges) != -1:
            for ie in ig.Members:
                HalfCircle_all.append(ie)
            NamedSelection.Delete(ig.Name)

    def _recreate(name, items):
        s = Selection.Create(items)
        if not s.Count == 0:
            NamedSelection.Delete(name)
            s.CreateAGroup(name)
    _recreate(grp_name_create, Circle_all)
    _recreate(grp_name_FullCircle_edges, FullCircle_all)
    _recreate(grp_name_HalfCircle_edges, HalfCircle_all)

    groups = NamedSelection.GetGroups(sc.Scripting.Helpers.DocumentHelper.GetRootPart())
    RM_grp_list = []
    for ig in groups:
        if ig.IsDeleted:
            continue
        if ig.Name == 'Scr_RMgrp_ALL':
            continue
        if ig.Name.IndexOf(RM_grp_name_create) != -1:
            for ie in ig.Members:
                if ie not in RM_grp_list:
                    RM_grp_list.append(ie)
    s_all = Selection.Create(RM_grp_list)
    if not s_all.Count == 0:
        NamedSelection.Delete('Scr_RMgrp_ALL')
        s_all.CreateAGroup('Scr_RMgrp_ALL')

    result["ok"] = "yes"
    result["holes_found"] = str(len(holes))
    result["rm_group_new"] = str(Count_grp_new)
    result["rm_group_replace"] = str(Count_grp_replace)
    result["hier_same_body"] = str(Count_Hierarchy["SameBody"])
    result["hier_internal"] = str(Count_Hierarchy["Internal"])
    result["hier_external"] = str(Count_Hierarchy["External"])
    result["dist_near"] = str(Count_Distance["Near"])
    result["dist_medium"] = str(Count_Distance["Medium"])
    result["dist_far"] = str(Count_Distance["Far"])
    result["holes_group_name"] = grp_name
except Exception:
    e = sys.exc_info()[1]
    result["ok"] = "no"
    result["error"] = str(e)
'''


def _geom_create_hole_groups(diameter_min_mm: float = 2.0, diameter_max_mm: float = 20.0,
                             mode: int = 0, pairing_strategy: str = "Ignore Component",
                             distance_min_mm: float = 0.0, distance_max_mm: float = 10.0,
                             holes_axis_dist_max_mm: float = 1.0, deg_max_circles: float = 10.0,
                             grp_name_create: str = "Scr_AllHoles", index_grp_start: int = 1,
                             rm_grp_create: bool = True, rm_grp_name_create: str = "Scr_RMgrp",
                             index_rm_start: int = 1, grp_name_not_go: str = "NOTGoConnections",
                             enable_distance_grouping: bool = False,
                             distance_level1_mm: float = 5.0,
                             distance_level2_mm: float = 20.0) -> str:
    """送 IronPython 腳本到 SpaceClaim 伺服器端：偵測圓孔並建立 named selection 群組，
    再對同軸、距離在門檻內的孔兩兩配對建立 RM 連接群組 (RM group)。

    由 SC_RM_grp_creation.py (ACT callback) 改寫。呼叫前需在 SpaceClaim 視窗中
    先選取目標 body/edge。回傳 JSON 字串（工具層 as_envelope 解析為信封）。
    """
    import json
    import tempfile

    def _err(msg: str) -> str:
        return json.dumps({"ok": False, "error": msg}, ensure_ascii=False)

    if _modeler is None:
        return _err("Geometry 未連線，請先執行 geometry_launch")
    if mode not in (0, 1):
        return _err("mode 僅支援 0 (僅圓孔邊) 或 1 (任意邊)")

    script_args = {
        "diameter_min_mm": str(diameter_min_mm),
        "diameter_max_mm": str(diameter_max_mm),
        "mode": str(mode),
        "pairing_strategy": pairing_strategy,
        "distance_min_mm": str(distance_min_mm),
        "distance_max_mm": str(distance_max_mm),
        "holes_axis_dist_max_mm": str(holes_axis_dist_max_mm),
        "deg_max_circles": str(deg_max_circles),
        "grp_name_create": grp_name_create,
        "index_grp_start": str(index_grp_start),
        "rm_grp_create": "1" if rm_grp_create else "0",
        "rm_grp_name_create": rm_grp_name_create,
        "index_rm_start": str(index_rm_start),
        "grp_name_not_go": grp_name_not_go,
        "enable_distance_grouping": "1" if enable_distance_grouping else "0",
        "distance_level1_mm": str(distance_level1_mm),
        "distance_level2_mm": str(distance_level2_mm),
    }

    tmp = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
    try:
        tmp.write(_RM_GROUP_SCRIPT)
        tmp.close()
        values, _design = _modeler.run_script_file(tmp.name, script_args=script_args)
    except Exception as e:
        return _err(f"SpaceClaim 孔配對腳本執行失敗: {e}")
    finally:
        try:
            os.remove(tmp.name)
        except Exception:
            pass

    values = dict(values or {})
    if str(values.get("ok", "")).lower() != "yes":
        return _err(f"孔配對群組建立失敗: {values.get('error', '未知錯誤')}")

    def _int(k):
        v = str(values.get(k, "0"))
        return int(v) if v.lstrip("-").isdigit() else 0

    out = {
        "ok": True,
        "selected_count": _int("selected_count"),
        "holes_found": _int("holes_found"),
        "holes_group_name": values.get("holes_group_name") or None,
        "rm_group_new": _int("rm_group_new"),
        "rm_group_replace": _int("rm_group_replace"),
        "hierarchy": {
            "same_body": _int("hier_same_body"),
            "within_component": _int("hier_internal"),
            "across_component": _int("hier_external"),
        },
        "api": values.get("api"),
    }
    if enable_distance_grouping:
        out["distance_grouping"] = {
            "near": _int("dist_near"),
            "medium": _int("dist_medium"),
            "far": _int("dist_far"),
        }
    return json.dumps(out, ensure_ascii=False)


# ===================================================================
# SERVER
# ===================================================================

_GEOM_LONG_LOCK = threading.Lock()  # 同時只跑一個長時間 geometry 工作（共用同一 SpaceClaim 連線）
_GEOM_LONG_GRACE_S = 60.0           # 超過 timeout_s 後再等多久仍未停下才先行回應客戶端


async def _run_geom_long(fn: Callable[[Callable[[str], None]], str], timeout_s: float,
                         notify: Callable[[str], None] | None = None, label: str = "geometry 工作") -> str:
    """於工作執行緒執行同步的長時間 geometry 工作，避免阻塞 event loop，並提供逾時與進度。

    fn(progress) 需在各階段開始時呼叫 progress(msg)：
      - 記錄 log 並轉交 notify（MCP progress notification）；
      - 超過 timeout_s（或已被取消）時拋 TimeoutError，由 fn 既有的例外流程清除暫存幾何。
    單一布林運算無法中途打斷；若超過 timeout_s + 寬限仍未停下，先回應客戶端逾時，
    工作則於下一個階段邊界自行中止（期間拒絕其他長時間工作）。
    """
    if not _GEOM_LONG_LOCK.acquire(blocking=False):
        return "錯誤：另一個長時間 geometry 工作仍在執行（可能是先前逾時、正在收尾者），請稍候再試"
    t0 = time.monotonic()
    cancelled = threading.Event()

    def progress(msg: str) -> None:
        elapsed = time.monotonic() - t0
        if cancelled.is_set() or elapsed > timeout_s:
            raise TimeoutError(f"{label}超過逾時 {timeout_s:.0f}s，於「{msg}」前中止（已執行 {elapsed:.0f}s）")
        logger.info(f"[{label} {elapsed:6.1f}s] {msg}")
        if notify:
            try:
                notify(f"[{elapsed:.0f}s] {msg}")
            except Exception as e:  # 進度回報失敗不影響主流程
                logger.debug(f"進度回報失敗: {e}")

    def _job():
        try:
            return fn(progress)
        finally:
            _GEOM_LONG_LOCK.release()

    fut = asyncio.get_running_loop().run_in_executor(None, _job)
    # 不用 wait_for：Python 3.11+ 的 asyncio.TimeoutError 即內建 TimeoutError，會與工作自身的逾時混淆
    done, _pending = await asyncio.wait({fut}, timeout=timeout_s + _GEOM_LONG_GRACE_S)
    if not done:
        cancelled.set()
        fut.add_done_callback(lambda f: f.cancelled() or not f.exception()
                              or logger.warning(f"{label}（逾時後背景收尾）: {f.exception()}"))
        return (f"錯誤：{label}逾時（>{timeout_s + _GEOM_LONG_GRACE_S:.0f}s），SpaceClaim 仍卡在單一布林運算；"
                f"工作將於下一個階段邊界自行中止並清除暫存幾何，完成前其他長時間工作會被拒絕")
    result = fut.result()
    return f"{result}\n（耗時 {time.monotonic() - t0:.1f}s）"


async def call_tool(name: str, arguments: dict[str, Any],
                    progress: Callable[[str], None] | None = None) -> list[TextContent]:
    """Plain dispatcher invoked directly by the thin tools/ wrappers.

    progress: 長時間工具（目前為 geometry_simplify_heatsink）的階段進度回呼，
    於工作執行緒中呼叫，需自行處理跨執行緒（見 products/geometry/tools.py）。

    Previously this was a second mcp.server.Server request handler that was
    never actually run; the redundant Server was removed during the
    architecture refactor. Mechanical tools were also moved out to
    products/mechanical.py, so only Fluent and Geometry are dispatched here.
    """
    global _fluent_session, _modeler, _current_design
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

        # ==================== MECHANICAL (moved out) ====================
        # Mechanical is now handled by products/mechanical.py + tools/mechanical.py
        # (single gRPC facade on the shared SessionRegistry). The former inline
        # Mechanical dispatch branch was removed during the architecture refactor.

        # ==================== GEOMETRY ====================
        elif name == "geometry_launch":
            import grpc
            from ansys.geometry.core import Modeler
            loop = asyncio.get_event_loop()
            port = arguments.get("port")
            host = arguments.get("host", "localhost")
            transport_mode = arguments.get("transport_mode", "insecure")
            # 限制內部逾時最多 8 秒，避免觸發 OpenClaw 30 秒中斷
            raw_timeout = int(arguments.get("connect_timeout", 8))
            connect_timeout = max(3, min(raw_timeout, 8))

            def _grpc_ping(h, p, ping_timeout=0.4):
                """快速確認 port 是否存活（探測 0.4s）"""
                ch = grpc.insecure_channel(f"{h}:{p}")
                try:
                    grpc.channel_ready_future(ch).result(timeout=ping_timeout)
                    return True
                except Exception:
                    return False
                finally:
                    ch.close()

            def _make_modeler(h, p, tm, to):
                return Modeler(host=h, port=int(p), transport_mode=tm, timeout=to)

            if port:
                # 模式 1：連接指定 port
                if not _grpc_ping(host, port):
                    return (
                        f"❌ SpaceClaim gRPC 埠號 {port} 無回應。\n"
                        f"請在 SpaceClaim Script Editor 執行啟動腳本（start_api_server.py）。"
                    )
                try:
                    _modeler = await asyncio.wait_for(
                        loop.run_in_executor(None, lambda: _make_modeler(host, port, transport_mode, connect_timeout)),
                        timeout=connect_timeout,
                    )
                    registry.put("geometry", str(port), _modeler)
                    try:
                        _current_design = _modeler.read_existing_design()
                        result = f"已連線 SpaceClaim ({host}:{port})，綁定當前設計 '{_current_design.name}'"
                    except Exception:
                        result = f"已連線 SpaceClaim ({host}:{port})"
                except Exception as e:
                    return f"❌ 連線 SpaceClaim ({host}:{port}) 失敗: {e}"
            else:
                # 自動掃描常用 port（50051-50055）
                scan_ports = [50051, 50052, 50053, 50054, 50055]
                connected = False
                for scan_port in scan_ports:
                    if not _grpc_ping(host, scan_port):
                        continue
                    try:
                        _modeler = await asyncio.wait_for(
                            loop.run_in_executor(None, lambda p=scan_port: _make_modeler(host, p, transport_mode, connect_timeout)),
                            timeout=connect_timeout,
                        )
                        connected = True
                        registry.put("geometry", str(scan_port), _modeler)
                        try:
                            _current_design = _modeler.read_existing_design()
                            result = f"已連線 SpaceClaim ({host}:{scan_port})，綁定當前設計 '{_current_design.name}'"
                        except Exception:
                            result = f"已連線 SpaceClaim ({host}:{scan_port})"
                        logger.info(f"Connected to SpaceClaim on port {scan_port}")
                        break
                    except Exception as e:
                        logger.warning(f"Port {scan_port} failed: {e}")
                        continue

                if not connected:
                    hint_root = os.environ.get("AWP_ROOT251") or r"<ANSYS_ROOT>\v251"
                    dll_hint_path = os.path.join(hint_root, "Addins", "ApiServer", "Presentation.ApiServerAddIn.dll")
                    result = (
                        "❌ 未偵測到 SpaceClaim 服務（已掃描 50051-50055）。\n\n"
                        "請在 SpaceClaim Script Editor 執行啟動腳本：\n"
                        "  import System.Reflection, System\n"
                        "  asm = System.Reflection.Assembly.LoadFrom(\n"
                        f"    r'{dll_hint_path}')\n"
                        "  addon = System.Activator.CreateInstance(asm.GetType('Presentation.ApiServerAddIn.ApiServerAddIn'))\n"
                        "  addon.Initialize(); addon.Connect()\n"
                    )


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
                elif name == "geometry_sketch_and_extrude":
                    result = _geom_sketch_and_extrude(
                        name=arguments.get("name", "ExtrudedBody"),
                        points=arguments.get("points", []),
                        plane=arguments.get("plane", "XY"),
                        curve_type=arguments.get("curve_type", "spline"),
                        distance=arguments.get("distance", 0.01),
                        is_closed=arguments.get("is_closed", True),
                        extrude_direction=arguments.get("extrude_direction", "+"))
                elif name == "geometry_create_enclosure":
                    result = _geom_create_enclosure(
                        target_body_name=arguments["target_body_name"],
                        enclosure_name=arguments.get("enclosure_name", "FluidDomain"),
                        shape=arguments.get("shape", "box"),
                        cushion_x_neg=arguments.get("cushion_x_neg", 0.05),
                        cushion_x_pos=arguments.get("cushion_x_pos", 0.1),
                        cushion_y_neg=arguments.get("cushion_y_neg", 0.05),
                        cushion_y_pos=arguments.get("cushion_y_pos", 0.05),
                        cushion_z_neg=arguments.get("cushion_z_neg", 0.05),
                        cushion_z_pos=arguments.get("cushion_z_pos", 0.05),
                        keep_target_body=arguments.get("keep_target_body", False))
                elif name == "geometry_simplify_ram":
                    result = _geom_simplify_ram(
                        motherboard=arguments["motherboard"],
                        ram=arguments["ram"],
                        socket=arguments["socket"],
                        result_name=arguments.get("result_name", "RAM_simplified"),
                        named_selection=arguments.get("named_selection", "ram_bottom"),
                        move_to_component=arguments.get("move_to_component", True),
                        component_name=arguments.get("component_name", "RAM_simplified"),
                        hide_source=arguments.get("hide_source", True))
                elif name == "geometry_simplify_ram_batch":
                    result = _geom_simplify_ram_batch(
                        motherboard=arguments["motherboard"],
                        ram=arguments["ram"],
                        socket=arguments["socket"],
                        result_prefix=arguments.get("result_prefix", "RAM_simplified"),
                        ns_prefix=arguments.get("ns_prefix", "ram_bottom"),
                        tol_mm=arguments.get("tol_mm", 2.0),
                        move_to_component=arguments.get("move_to_component", True),
                        component_name=arguments.get("component_name", "RAM_simplified"),
                        hide_source=arguments.get("hide_source", True))
                elif name == "geometry_simplify_heatsink":
                    result = await _run_geom_long(lambda prog: _geom_simplify_heatsink(
                        progress=prog,
                        source=arguments["source"],
                        result_name=arguments.get("result_name"),
                        density=arguments.get("density"),
                        material=arguments.get("material", "aluminum"),
                        keep_source=arguments.get("keep_source", True),
                        named_selection=arguments.get("named_selection", "hs_bottom"),
                        name_density_suffix=arguments.get("name_density_suffix", True),
                        hole_min_dia_mm=arguments.get("hole_min_dia_mm", 2.5),
                        extra_sources=arguments.get("extra_sources"),
                        body_densities=arguments.get("body_densities"),
                        all_instances=arguments.get("all_instances", False),
                        contact_body=arguments.get("contact_body"),
                        fin_box=arguments.get("fin_box", "largest"),
                        hole_select=arguments.get("hole_select", "screw"),
                        diagnose_only=arguments.get("diagnose_only", False)),
                        timeout_s=float(arguments.get("timeout_s", 600)), notify=progress,
                        label="散熱片簡化")
                elif name == "geometry_midsurface":
                    result = _geom_midsurface(
                        max_thickness_mm=arguments.get("max_thickness_mm", 6.0),
                        main_surface_ratio=arguments.get("main_surface_ratio", 0.7),
                        area_difference_ratio=arguments.get("area_difference_ratio", 0.1),
                        complex_area_diff=arguments.get("complex_area_diff", 0.05),
                        enable_sheet_metal_check=arguments.get("enable_sheet_metal_check", True),
                        hide_source_bodies=arguments.get("hide_source_bodies", True))
                elif name == "geometry_create_hole_groups":
                    result = _geom_create_hole_groups(
                        diameter_min_mm=arguments.get("diameter_min_mm", 2.0),
                        diameter_max_mm=arguments.get("diameter_max_mm", 20.0),
                        mode=arguments.get("mode", 0),
                        pairing_strategy=arguments.get("pairing_strategy", "Ignore Component"),
                        distance_min_mm=arguments.get("distance_min_mm", 0.0),
                        distance_max_mm=arguments.get("distance_max_mm", 10.0),
                        holes_axis_dist_max_mm=arguments.get("holes_axis_dist_max_mm", 1.0),
                        deg_max_circles=arguments.get("deg_max_circles", 10.0),
                        grp_name_create=arguments.get("grp_name_create", "Scr_AllHoles"),
                        index_grp_start=arguments.get("index_grp_start", 1),
                        rm_grp_create=arguments.get("rm_grp_create", True),
                        rm_grp_name_create=arguments.get("rm_grp_name_create", "Scr_RMgrp"),
                        index_rm_start=arguments.get("index_rm_start", 1),
                        grp_name_not_go=arguments.get("grp_name_not_go", "NOTGoConnections"),
                        enable_distance_grouping=arguments.get("enable_distance_grouping", False),
                        distance_level1_mm=arguments.get("distance_level1_mm", 5.0),
                        distance_level2_mm=arguments.get("distance_level2_mm", 20.0))
                elif name == "geometry_screenshot":
                    result = _geom_screenshot(
                        file_path=arguments["file_path"],
                        image_format=arguments.get("image_format"),
                        fit=arguments.get("fit", True),
                        view=arguments.get("view", "current"),
                        bodies=arguments.get("bodies"))
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
                    # 遞迴列出所有 body（含子元件），並附上所屬 component 路徑，
                    # 以便辨識 RAM / socket / 主機板。頂層 d.bodies 只含最外層，
                    # 裝配體的實體多半位於子 component 內。
                    rows = []

                    def _walk(comp, path):
                        here = path + ("/" if path else "") + getattr(comp, "name", "")
                        for b in getattr(comp, "bodies", []) or []:
                            rows.append((b.name, b.id, here))
                        for sub in getattr(comp, "components", []) or []:
                            _walk(sub, here)

                    try:
                        _walk(d, "")
                    except Exception:
                        # 後備：至少回傳 get_all_bodies（扁平，無路徑）
                        try:
                            flat = d.get_all_bodies()
                        except Exception:
                            flat = d.bodies
                        rows = [(b.name, b.id, "") for b in flat]

                    if rows:
                        lines = [
                            f"  [{i}] {nm} (id={bid})" + (f"  <component: {comp_path}>" if comp_path else "")
                            for i, (nm, bid, comp_path) in enumerate(rows)
                        ]
                        result = f"幾何體 ({len(rows)}):\n" + "\n".join(lines)
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
                    registry.drop("geometry")
                    result = "Geometry 建模器已關閉"

        else:
            result = f"未知工具: {name}"

    except Exception as exc:
        logger.exception(f"Tool [{name}] failed")
        result = f"錯誤 [{name}]: {exc}"

    return [TextContent(type="text", text=result)]
