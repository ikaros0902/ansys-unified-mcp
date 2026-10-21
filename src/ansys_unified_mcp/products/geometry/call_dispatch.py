#!/usr/bin/env python3
"""ANSYS MCP Server — Geometry call_tool 分派實作。

驅動層: Geometry → ansys-geometry-core (PyAnsys Geometry) gRPC

此模組由 drivers/sim_impl.py 拆分而來（原為 geometry + fluent 共用的單一檔案），
現歸位至 products/geometry/，僅保留 Geometry 相關的工具定義、全域 session、
幾何輔助函式與分派邏輯。
"""

import asyncio
import logging
import math
import os
import threading
import time
from typing import Any, Callable

from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ansys-mcp")

from ansys_unified_mcp.core.sessions import registry
from ansys_unified_mcp.products.geometry.spaceclaim_scripts import load_script

# 共用 helper 與 RAM / Heatsink 簡化函式已搬移至獨立檔案，此處顯式匯入內部使用函式，
# 並透過 star import 保持命名空間相容性供既有測試存取。
from ._geom_shared import *  # noqa: F401,F403
from ._geom_shared import _make_box_from_bbox, _bbox_m
from .simplify_ram import *  # noqa: F401,F403
from .simplify_ram import _geom_simplify_ram, _geom_simplify_ram_batch
from .simplify_heatsink import *  # noqa: F401,F403
from .simplify_heatsink import _geom_simplify_heatsink

# ---------------------------------------------------------------------------
# Global sessions (backed by SessionRegistry)
# ---------------------------------------------------------------------------
_modeler = None       # PyAnsys Geometry Modeler
_current_design = None  # track active design name

# ===================================================================
# TOOLS
# ===================================================================

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
    Tool(name="geometry_simplify_ram", description="【呼叫前必須先確認 RAM、socket body 名稱】將單一 RAM 卡 + 其 socket 簡化為一座落於主機板頂面（或 socket 底面）的「凸字形」兩段體，並於底面（板接合面）建立 named selection。高度軸為 Y；下段寬基座＝socket 的 X-Z footprint（基準面→socket 頂），上段窄凸柱＝RAM 的 X-Z footprint（socket 頂→RAM 頂），兩段聯集為單一 body；socket 頂落在無效區間時退回單一合併包圍盒方塊。預設將結果移入新 component，並抑制 (suppress for physics) + 隱藏原始 RAM/socket body。",
         inputSchema={"type": "object", "properties": {
             "motherboard": {"type": "string", "default": "", "description": "主機板 body 名稱（其頂面即方塊底面），例 'JVPCB1074973E'；若無主機板可留空，將自動以 socket 自身底面為基準"},
             "ram": {"type": "string", "description": "RAM 卡 body 名稱，例 'DIMM_DDR5_EGS'"},
             "socket": {"type": "string", "description": "RAM socket body 名稱，例 'J33'"},
             "result_name": {"type": "string", "default": "RAM_simplified", "description": "生成簡化方塊 body 名稱"},
             "named_selection": {"type": "string", "default": "ram_bottom", "description": "方塊底面接合面的 named selection 名稱"},
             "move_to_component": {"type": "boolean", "default": True, "description": "是否將簡化方塊移入新 component（名稱見 component_name）"},
             "component_name": {"type": "string", "default": "RAM_simplified", "description": "move_to_component 時新建的 component 名稱"},
             "hide_source": {"type": "boolean", "default": True, "description": "是否抑制 (suppress for physics) 並隱藏原始 RAM 與 socket body，使其在下游網格/求解被排除且不干擾框選"}},
             "required": ["ram", "socket"]}),
    Tool(name="geometry_simplify_ram_batch", description="【呼叫前必須先確認 RAM、socket body 名稱】批次簡化所有同名 RAM+socket 配對（依 X 中心位置自動就近配對）。每對成為一座落於主機板頂面（或 socket 底面）的「凸字形」兩段體（下段寬基座＝socket footprint；上段窄凸柱＝RAM footprint），各自建立底面 named selection，依 X 順序編號 <result_prefix>_01、<ns_prefix>_01…。適用於多條相同 DIMM/socket 陣列。配對成功的原始 body 預設會被抑制 (suppress for physics) 並隱藏。",
         inputSchema={"type": "object", "properties": {
             "motherboard": {"type": "string", "default": "", "description": "主機板 body 名稱（頂面=各方塊底面）；若無主機板可留空，將自動以各 socket 自身底面為基準"},
             "ram": {"type": "string", "description": "RAM 卡 body 名稱（陣列中重複出現）"},
             "socket": {"type": "string", "description": "socket body 名稱（陣列中重複出現）"},
             "result_prefix": {"type": "string", "default": "RAM_simplified", "description": "方塊 body 名稱前綴（自動編號）"},
             "ns_prefix": {"type": "string", "default": "ram_bottom", "description": "底面 named selection 名稱前綴（自動編號）"},
             "tol_mm": {"type": "number", "default": 2.0, "description": "RAM 與 socket 視為一對的最大 X 中心距離（單位：毫米 mm）"},
             "move_to_component": {"type": "boolean", "default": True, "description": "是否將所有簡化方塊移入同一新 component（名稱見 component_name）"},
             "component_name": {"type": "string", "default": "RAM_simplified", "description": "move_to_component 時新建的 component 名稱"},
             "hide_source": {"type": "boolean", "default": True, "description": "是否抑制 (suppress for physics) 並隱藏配對成功的原始 RAM 與 socket body，使其在下游網格/求解被排除且不干擾框選"}},
             "required": ["ram", "socket"]}),
    Tool(name="geometry_simplify_heatsink", description="散熱片 (heatsink) 簡化為凸字形方塊組（擠型/壓鑄/折片/針狀鰭片，單一或多 body 組件皆可）：底板（包圍盒 X-Z，鎖孔所在板底→鰭片根部）＋上凸（最大一排鰭片範圍，鰭片根部→鰭片頂）＋下凸（主接合底面範圍，接觸面→板底），無階梯、無圓角，螺絲/彈簧/推銷不保留；鎖孔（原始完整圓周的 Y 向挖孔）以 Y 向直圓柱貫穿；主接合底面建立 named selection。量測原始體積，以常見散熱片密度（預設鋁 2700 kg/m³，可逐 body 指定）估算質量，於質量守恆下反推簡化體應設定的等效密度（kg/m³），附加於新 body 名稱後綴 _rho<整數>。結果建於原始 body 所屬 component（共用 master 的各 instance 皆會出現），原始 body 預設保留並設定 Suppress for Physics ＋ 隱藏（下游排除、不干擾框選）。高度軸為 world Y。",
         inputSchema={"type": "object", "properties": {
             "source": {"type": "string", "description": "散熱片主 body 名稱（決定結果命名與所屬 component），例 'ENDURANCE-POWER-BRICK-HS-241018'"},
             "result_name": {"type": "string", "description": "簡化體 body 名稱（不填則為 <source>_sim，再附加 _rho<密度>；多組時再加 _01、_02…）"},
             "density": {"type": "number", "description": "散熱片材料密度 (kg/m³)，不填則依 material 預設"},
             "material": {"type": "string", "enum": ["aluminum", "aluminum_6063", "copper", "copper_c110"], "default": "aluminum", "description": "常見散熱片材料（決定預設密度，aluminum=2700, copper=8960 kg/m³）"},
             "keep_source": {"type": "boolean", "default": True, "description": "是否保留原始散熱片 body（預設保留）；保留時會自動對原始 body 設定 Suppress for Physics 並隱藏，使其在下游網格/求解被排除且不干擾框選"},
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
    Tool(name="geometry_suppress_and_hide",
         description="依 body 名稱（支援 glob 萬用字元）批次設定『Suppress for Physics』並隱藏，用於簡化完成後排除原始實體。走 SpaceClaim 伺服器端腳本（50051 gRPC），不需 Workbench 橋接器。",
         inputSchema={"type": "object", "properties": {
             "patterns": {"type": "array", "items": {"type": "string"},
                          "description": "要抑制/隱藏的 body 名稱樣式，支援 glob（例 ['ICX_HS_1U_FIN_*','DIMM_DDR5_EGS']）"},
             "exclude": {"type": "array", "items": {"type": "string"},
                         "description": "排除樣式；符合者不處理（例 ['*_simplified_*'] 以保護簡化結果）"},
             "suppress": {"type": "boolean", "default": True, "description": "是否設定 Suppress for Physics"},
             "hide": {"type": "boolean", "default": True, "description": "是否隱藏（取消可見性）"}},
             "required": ["patterns"]}),
    Tool(name="geometry_list_bodies", description="列出當前設計中的所有幾何體", inputSchema={"type": "object", "properties": {}}),
    Tool(name="geometry_get_bounding_box",
         description="查詢指定實體 (Body) 或設計中所有實體的軸對齊包圍盒 (Bounding Box)、尺寸與中心座標。回傳 min/max (X, Y, Z)、尺寸與中心點，支援毫米 (mm) 與公尺 (m)。可用於量測實體尺寸、定位基準或手動建構簡化方塊。",
         inputSchema={"type": "object", "properties": {
             "body_name": {"type": "string", "default": "", "description": "要查詢的 Body 名稱；若留空則回傳當前設計中所有實體的包圍盒清單"}},
             "required": []}),
    Tool(name="geometry_run_script",
         description="透過當前已連線的 gRPC (Port 50051) 通道，直接在作用中的 SpaceClaim / Discovery 視窗中執行 Python 幾何腳本。支援直接傳入腳本內容 (script_content) 或腳本檔案路徑 (script_path)，並可回傳腳本中定義的 result 字典。",
         inputSchema={"type": "object", "properties": {
             "script_content": {"type": "string", "default": "", "description": "欲執行的 Python 腳本內容字串"},
             "script_path": {"type": "string", "default": "", "description": "本機既有腳本檔案路徑 (.py / .scscript)"},
             "import_design": {"type": "boolean", "default": True, "description": "腳本執行後是否同步更新 MCP 的作用中幾何設計快取"}},
             "required": []}),
    Tool(name="geometry_list_named_selections", description="列出當前設計中的所有具名選擇 (Named Selection)", inputSchema={"type": "object", "properties": {}}),
    Tool(name="geometry_import_file", description="匯入 CAD 檔案",
         inputSchema={"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}),
    Tool(name="geometry_status", description="Geometry 建模器連線狀態", inputSchema={"type": "object", "properties": {}}),
    Tool(name="geometry_close", description="關閉 Geometry 建模器", inputSchema={"type": "object", "properties": {}}),
]

ALL_TOOLS = GEOMETRY_TOOLS

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


def _geom_get_bounding_box(body_name: str = "") -> str:
    """查詢指定 Body 或設計中所有 Body 的軸對齊包圍盒 (Bounding Box) 與尺寸。"""
    d = _geom_get_design()
    body_entries = []

    def _walk(comp, path):
        here = path + ("/" if path else "") + getattr(comp, "name", "")
        for b in getattr(comp, "bodies", []) or []:
            body_entries.append((b, here))
        for sub in getattr(comp, "components", []) or []:
            _walk(sub, here)

    try:
        _walk(d, "")
    except Exception:
        body_entries = [(b, "") for b in getattr(d, "bodies", []) or []]

    if not body_entries:
        return "當前設計無任何實體 (Body)。"

    def _format_entry(b, path):
        try:
            lo, hi = _bbox_m(b)
            dx = hi[0] - lo[0]
            dy = hi[1] - lo[1]
            dz = hi[2] - lo[2]
            cx = (lo[0] + hi[0]) / 2.0
            cy = (lo[1] + hi[1]) / 2.0
            cz = (lo[2] + hi[2]) / 2.0
            return {
                "name": b.name,
                "id": getattr(b, "id", ""),
                "path": path,
                "min_m": [round(v, 6) for v in lo],
                "max_m": [round(v, 6) for v in hi],
                "size_m": [round(dx, 6), round(dy, 6), round(dz, 6)],
                "center_m": [round(cx, 6), round(cy, 6), round(cz, 6)],
                "min_mm": [round(v * 1000.0, 3) for v in lo],
                "max_mm": [round(v * 1000.0, 3) for v in hi],
                "size_mm": [round(dx * 1000.0, 3), round(dy * 1000.0, 3), round(dz * 1000.0, 3)],
                "center_mm": [round(cx * 1000.0, 3), round(cy * 1000.0, 3), round(cz * 1000.0, 3)],
            }
        except Exception as e:
            return {"name": b.name, "id": getattr(b, "id", ""), "path": path, "error": str(e)}

    if body_name:
        matches = [(b, p) for b, p in body_entries if b.name == body_name]
        if not matches:
            avail = [b.name for b, _ in body_entries]
            return f"找不到名為 '{body_name}' 的實體。當前設計中的實體有: {', '.join(avail[:25])}"

        lines = [f"實體 '{body_name}' 包圍盒與尺寸資訊 (共找到 {len(matches)} 處匹配):"]
        for b, p in matches:
            info = _format_entry(b, p)
            if "error" in info:
                lines.append(f"  - 路徑: {p or '(根目錄)'} -> 讀取失敗: {info['error']}")
            else:
                lines.append(f"  - 所屬組件路徑: {p or '(根目錄)'}")
                lines.append(f"  - 尺寸 (mm): X={info['size_mm'][0]}, Y={info['size_mm'][1]}, Z={info['size_mm'][2]}")
                lines.append(f"  - 最小座標 min (mm): [{info['min_mm'][0]}, {info['min_mm'][1]}, {info['min_mm'][2]}]")
                lines.append(f"  - 最大座標 max (mm): [{info['max_mm'][0]}, {info['max_mm'][1]}, {info['max_mm'][2]}]")
                lines.append(f"  - 中心座標 center (mm): [{info['center_mm'][0]}, {info['center_mm'][1]}, {info['center_mm'][2]}]")
                lines.append(f"  - 尺寸 (m): X={info['size_m'][0]}, Y={info['size_m'][1]}, Z={info['size_m'][2]}")
                lines.append(f"  - 最小座標 min (m): [{info['min_m'][0]}, {info['min_m'][1]}, {info['min_m'][2]}]")
                lines.append(f"  - 最大座標 max (m): [{info['max_m'][0]}, {info['max_m'][1]}, {info['max_m'][2]}]")
        return "\n".join(lines)
    else:
        lines = [f"當前設計共有 {len(body_entries)} 個實體 (Body) 之包圍盒清單:"]
        for b, p in body_entries:
            info = _format_entry(b, p)
            if "error" in info:
                lines.append(f"  - {b.name} ({p or '/'}): 讀取失敗 ({info['error']})")
            else:
                lines.append(
                    f"  - {b.name} [{p or '/'}]: size(mm)=[{info['size_mm'][0]}, {info['size_mm'][1]}, {info['size_mm'][2]}] "
                    f"min(mm)=[{info['min_mm'][0]}, {info['min_mm'][1]}, {info['min_mm'][2]}] "
                    f"max(mm)=[{info['max_mm'][0]}, {info['max_mm'][1]}, {info['max_mm'][2]}]"
                )
        return "\n".join(lines)


def _geom_run_script(script_content: str = "", script_path: str = "", import_design: bool = True) -> str:
    """透過當前連線的 gRPC 執行 SpaceClaim / Discovery Python 幾何腳本。"""
    from ansys_unified_mcp.products.geometry import controller
    res = controller.run_script(
        script_content=script_content,
        script_path=script_path,
        import_design=import_design,
    )
    if not res.get("ok"):
        return f"腳本執行失敗: {res.get('error')}"
    values = res.get("values")
    val_str = f"\n腳本回傳值 (result): {values}" if values else ""
    return f"✓ 腳本已成功透過 PyAnsys Geometry gRPC 在 SpaceClaim 執行完成。{val_str}"


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
# GEOMETRY HELPERS — 已拆分模組的 re-export
# ===================================================================
# 共用 helper 與 RAM / Heatsink 簡化函式已搬移至同套件下的獨立檔案
# （_geom_shared / simplify_ram / simplify_heatsink），此處以 re-export 匯入，
# 確保 call_tool 與既有測試（以 call_dispatch 命名空間存取 helper）行為不變。
# 三個新檔對本模組的 _geom_get_design / _geom_suppress_hide 依賴皆於函式內
# 以 `from . import call_dispatch as _cd` 延遲存取，避免模組載入期循環 import。
# （相關函式已在檔案開頭統一匯入與 re-export）




# ===================================================================
# GEOMETRY HELPERS — SpaceClaim 伺服器端 suppress / hide
# ===================================================================
# 以 Modeler.run_script_file 送 IronPython 到 SpaceClaim 伺服器端，依 body 名稱
# （支援 glob）批次設定「Suppress for Physics」與可見性。走已驗證可靠的 50051
# gRPC 通道，不依賴 Workbench journal 橋接器或 ACT 情境。
# 不同 SpaceClaim 版本的抑制屬性命名不一致，腳本會依序嘗試多個候選名稱並回報
# 實際生效者，避免因 API 命名差異而靜默失敗。

_SUPPRESS_HIDE_SCRIPT = load_script("suppress_hide")


def _geom_suppress_hide(patterns, exclude=None, suppress=True, hide=True):
    """依 body 名稱（glob）批次 suppress-for-physics 與隱藏，走 SpaceClaim 伺服器端腳本。"""
    import tempfile

    pats = [p for p in (patterns or []) if str(p).strip()]
    if not pats:
        return "錯誤: 未提供任何 body 名稱樣式 (patterns)"

    script_args = {
        "patterns_hex": "\n".join(pats).encode("utf-8").hex(),
        "exclude_hex": "\n".join(exclude or []).encode("utf-8").hex(),
        "do_suppress": "1" if suppress else "0",
        "do_hide": "1" if hide else "0",
    }

    tmp = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
    try:
        tmp.write(_SUPPRESS_HIDE_SCRIPT)
        tmp.close()
        values, _design = _modeler.run_script_file(tmp.name, script_args=script_args)
    except Exception as e:
        return f"SpaceClaim suppress/hide 腳本執行失敗: {e}"
    finally:
        try:
            os.remove(tmp.name)
        except Exception:
            pass

    values = dict(values or {})
    if str(values.get("ok", "")).lower() != "yes":
        return f"suppress/hide 失敗: {values.get('error', '未知錯誤')}"

    lines = [
        "✓ SpaceClaim suppress/hide 完成",
        f"  掃描 body 總數: {values.get('total_bodies')}",
        f"  符合樣式: {values.get('matched')}",
        f"  已抑制 (suppress for physics): {values.get('suppressed')}"
        + (f"（屬性: {values.get('suppress_attr')}）" if values.get("suppress_attr") else ""),
        f"  已隱藏: {values.get('hidden')}"
        + (f"（屬性: {values.get('hide_attr')}）" if values.get("hide_attr") else ""),
    ]
    if values.get("failed"):
        lines.append(f"  ⚠ 失敗項: {values.get('failed')}")
    if values.get("names"):
        lines.append("  處理清單:")
        for n in str(values["names"]).split("\n"):
            lines.append("    - " + n)
    return "\n".join(lines)


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

_SCREENSHOT_SCRIPT = load_script("screenshot")


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

_MIDSURFACE_SCRIPT = load_script("midsurface")


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

_RM_GROUP_SCRIPT = load_script("rm_group")
_DEFEATURE_SCRIPT = load_script("defeature")
_BGA_ARRAY_SCRIPT = load_script("bga_array")
_IMPRINT_CONTACTS_SCRIPT = load_script("imprint_contacts")


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




def _geom_defeature_features(defeature_face_exe: bool = True, defeature_edge_exe: bool = True,
                             max_edges_at_once: int = 3000, r_max_cylinder: float = 3.5,
                             r_min_circle: float = 0.0, r_max_circle: float = 3.5,
                             fs_grp_sizefilter: float = 1.5,
                             grp_dont_defeature: str = "Scr_UserInput_DONT_DEFEATURE_GRP",
                             target_body_name: str = "") -> str:
    """送 IronPython 腳本至 SpaceClaim 伺服器端：自動消除圓柱孔、小圓弧邊與倒角特徵。"""
    import json
    import tempfile

    def _err(msg: str) -> str:
        return json.dumps({"ok": False, "error": msg}, ensure_ascii=False)

    if _modeler is None:
        return _err("Geometry 未連線，請先執行 geometry_launch")

    script_args = {
        "defeature_face_exe": "1" if defeature_face_exe else "0",
        "defeature_edge_exe": "1" if defeature_edge_exe else "0",
        "max_edges_at_once": str(max_edges_at_once),
        "r_max_cylinder": str(r_max_cylinder),
        "r_min_circle": str(r_min_circle),
        "r_max_circle": str(r_max_circle),
        "fs_grp_sizefilter": str(fs_grp_sizefilter),
        "grp_dont_defeature": grp_dont_defeature,
        "target_body_name": target_body_name,
    }

    tmp = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
    try:
        tmp.write(_DEFEATURE_SCRIPT)
        tmp.close()
        values, _design = _modeler.run_script_file(tmp.name, script_args=script_args)
    except Exception as e:
        return _err(f"SpaceClaim 去特徵腳本執行失敗: {e}")
    finally:
        try:
            os.remove(tmp.name)
        except Exception:
            pass

    values = dict(values or {})
    if str(values.get("ok", "")).lower() != "yes":
        return _err(f"去特徵失敗: {values.get('error', '未知錯誤')}")

    return json.dumps({
        "ok": True,
        "message": values.get("message", "Defeature completed"),
        "elapsed_sec": values.get("elapsed_sec"),
        "api": values.get("api")
    }, ensure_ascii=False)


def _geom_create_bga_array(bga_diameter_mm: float = 0.65, bga_height_mm: float = 0.51,
                           low_pad_d_mm: float = 0.50, low_pad_h_mm: float = 0.02,
                           high_pad_d_mm: float = 0.50, high_pad_h_mm: float = 0.02,
                           n_dir1: int = 10, n_dir2: int = 10,
                           pitch_dir1_mm: float = 1.0, pitch_dir2_mm: float = 1.0,
                           array_type: int = 0, mating_face: str = "bottom") -> str:
    """送 IronPython 腳本至 SpaceClaim 伺服器端：自動建立 BGA 錫球與陣列幾何。"""
    import json
    import tempfile

    def _err(msg: str) -> str:
        return json.dumps({"ok": False, "error": msg}, ensure_ascii=False)

    if _modeler is None:
        return _err("Geometry 未連線，請先執行 geometry_launch")

    script_args = {
        "bga_diameter_mm": str(bga_diameter_mm),
        "bga_height_mm": str(bga_height_mm),
        "low_pad_d_mm": str(low_pad_d_mm),
        "low_pad_h_mm": str(low_pad_h_mm),
        "high_pad_d_mm": str(high_pad_d_mm),
        "high_pad_h_mm": str(high_pad_h_mm),
        "n_dir1": str(n_dir1),
        "n_dir2": str(n_dir2),
        "pitch_dir1_mm": str(pitch_dir1_mm),
        "pitch_dir2_mm": str(pitch_dir2_mm),
        "array_type": str(array_type),
        "mating_face": mating_face,
    }

    tmp = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
    try:
        tmp.write(_BGA_ARRAY_SCRIPT)
        tmp.close()
        values, _design = _modeler.run_script_file(tmp.name, script_args=script_args)
    except Exception as e:
        return _err(f"SpaceClaim BGA 陣列腳本執行失敗: {e}")
    finally:
        try:
            os.remove(tmp.name)
        except Exception:
            pass

    values = dict(values or {})
    if str(values.get("ok", "")).lower() != "yes":
        return _err(f"BGA 陣列建立失敗: {values.get('error', '未知錯誤')}")

    def _int(k):
        v = str(values.get(k, "0"))
        return int(v) if v.lstrip("-").isdigit() else 0

    return json.dumps({
        "ok": True,
        "total_balls": _int("total_balls"),
        "message": values.get("message"),
        "elapsed_sec": values.get("elapsed_sec"),
        "api": values.get("api")
    }, ensure_ascii=False)


def _geom_imprint_contacts(distance_range_mm: float = 0.51, imprint_curves: bool = True,
                           imprint_distance_range_mm: float = 0.01) -> str:
    """送 IronPython 腳本至 SpaceClaim 伺服器端：自動執行面壓印與距離共拓撲 Named Selection。"""
    import json
    import tempfile

    def _err(msg: str) -> str:
        return json.dumps({"ok": False, "error": msg}, ensure_ascii=False)

    if _modeler is None:
        return _err("Geometry 未連線，請先執行 geometry_launch")

    script_args = {
        "distance_range_mm": str(distance_range_mm),
        "imprint_curves": "1" if imprint_curves else "0",
        "imprint_distance_range_mm": str(imprint_distance_range_mm),
    }

    tmp = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
    try:
        tmp.write(_IMPRINT_CONTACTS_SCRIPT)
        tmp.close()
        values, _design = _modeler.run_script_file(tmp.name, script_args=script_args)
    except Exception as e:
        return _err(f"SpaceClaim 壓印與接觸腳本執行失敗: {e}")
    finally:
        try:
            os.remove(tmp.name)
        except Exception:
            pass

    values = dict(values or {})
    if str(values.get("ok", "")).lower() != "yes":
        return _err(f"接觸壓印失敗: {values.get('error', '未知錯誤')}")

    return json.dumps({
        "ok": True,
        "message": values.get("message"),
        "elapsed_sec": values.get("elapsed_sec"),
        "api": values.get("api")
    }, ensure_ascii=False)


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
    """Plain dispatcher invoked directly by the thin tools/ wrappers (Geometry only).

    progress: 長時間工具（目前為 geometry_simplify_heatsink）的階段進度回呼，
    於工作執行緒中呼叫，需自行處理跨執行緒（見 products/geometry/tools.py）。
    """
    global _modeler, _current_design
    result = ""

    try:
        # ==================== GEOMETRY ====================
        if name == "geometry_launch":
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
                        ram=arguments["ram"],
                        socket=arguments["socket"],
                        motherboard=arguments.get("motherboard", ""),
                        result_name=arguments.get("result_name", "RAM_simplified"),
                        named_selection=arguments.get("named_selection", "ram_bottom"),
                        move_to_component=arguments.get("move_to_component", True),
                        component_name=arguments.get("component_name", "RAM_simplified"),
                        hide_source=arguments.get("hide_source", True))
                elif name == "geometry_simplify_ram_batch":
                    result = _geom_simplify_ram_batch(
                        ram=arguments["ram"],
                        socket=arguments["socket"],
                        motherboard=arguments.get("motherboard", ""),
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
                elif name == "geometry_defeature_features":
                    result = _geom_defeature_features(
                        defeature_face_exe=arguments.get("defeature_face_exe", True),
                        defeature_edge_exe=arguments.get("defeature_edge_exe", True),
                        max_edges_at_once=arguments.get("max_edges_at_once", 3000),
                        r_max_cylinder=arguments.get("r_max_cylinder", 3.5),
                        r_min_circle=arguments.get("r_min_circle", 0.0),
                        r_max_circle=arguments.get("r_max_circle", 3.5),
                        fs_grp_sizefilter=arguments.get("fs_grp_sizefilter", 1.5),
                        grp_dont_defeature=arguments.get("grp_dont_defeature", "Scr_UserInput_DONT_DEFEATURE_GRP"),
                        target_body_name=arguments.get("target_body_name", ""))
                elif name == "geometry_create_bga_array":
                    result = _geom_create_bga_array(
                        bga_diameter_mm=arguments.get("bga_diameter_mm", 0.65),
                        bga_height_mm=arguments.get("bga_height_mm", 0.51),
                        low_pad_d_mm=arguments.get("low_pad_d_mm", 0.50),
                        low_pad_h_mm=arguments.get("low_pad_h_mm", 0.02),
                        high_pad_d_mm=arguments.get("high_pad_d_mm", 0.50),
                        high_pad_h_mm=arguments.get("high_pad_h_mm", 0.02),
                        n_dir1=arguments.get("n_dir1", 10),
                        n_dir2=arguments.get("n_dir2", 10),
                        pitch_dir1_mm=arguments.get("pitch_dir1_mm", 1.0),
                        pitch_dir2_mm=arguments.get("pitch_dir2_mm", 1.0),
                        array_type=arguments.get("array_type", 0),
                        mating_face=arguments.get("mating_face", "bottom"))
                elif name == "geometry_imprint_contacts":
                    result = _geom_imprint_contacts(
                        distance_range_mm=arguments.get("distance_range_mm", 0.51),
                        imprint_curves=arguments.get("imprint_curves", True),
                        imprint_distance_range_mm=arguments.get("imprint_distance_range_mm", 0.01))
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
                elif name == "geometry_suppress_and_hide":
                    result = _geom_suppress_hide(
                        patterns=arguments.get("patterns") or [],
                        exclude=arguments.get("exclude"),
                        suppress=arguments.get("suppress", True),
                        hide=arguments.get("hide", True))
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
                elif name == "geometry_get_bounding_box":
                    result = _geom_get_bounding_box(arguments.get("body_name", ""))
                elif name == "geometry_run_script":
                    result = _geom_run_script(
                        script_content=arguments.get("script_content", ""),
                        script_path=arguments.get("script_path", ""),
                        import_design=arguments.get("import_design", True),
                    )
                elif name == "geometry_list_named_selections":
                    d = _geom_get_design()
                    named_selections = d.named_selections
                    if named_selections:
                        lines = [f"  [{i}] {ns.name} (id={ns.id})" for i, ns in enumerate(named_selections)]
                        result = f"具名選擇 ({len(named_selections)}):\n" + "\n".join(lines)
                    else:
                        result = "當前設計無具名選擇"
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
