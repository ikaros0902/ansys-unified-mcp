# -*- coding: utf-8 -*-
"""ANSYS Granta MI MCP 工具層：暴露材料情報檢索、物性隨溫度退化與環保管規評估工具。"""

from __future__ import annotations

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.products.granta.driver import GrantaDriver


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def granta_check_connection() -> dict:
    """檢查 ANSYS Granta MI 服務與材料情報數據庫連接狀態。"""
    driver = GrantaDriver()
    valid, message = driver.validate_prerequisites()
    return _envelope({
        "available": valid,
        "message": message,
    })


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def granta_search_material(
    query_name: str = "steel",
    category: str = "all",
    dry_run: bool = False,
) -> dict:
    """在 ANSYS Granta MI 材料庫中檢索材料物性常數 (彈性模數、降伏強度、熱傳導係數等)。

    Args:
        query_name: 材料名稱或牌號關鍵字 (例如 'steel', '6061', 'copper', 'fr4', 'ti')。
        category: 材料分類篩選 ('all', 'metal', 'composite', 'plastic')。
        dry_run: 僅驗證查詢字串。
    """
    if dry_run:
        return _envelope({"ok": True, "dry_run": True, "query": query_name})

    driver = GrantaDriver()
    results = driver.search_materials(query=query_name, category=category)
    return _envelope(driver.with_backend_metadata({"ok": True, "count": len(results), "materials": results}))


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def granta_evaluate_compliance(
    material_id: str = "structural_steel",
    regulation: str = "RoHS",
    dry_run: bool = False,
) -> dict:
    """調度 ANSYS Granta MI BoM Analytics 評估材料之國際環保管規遵從性 (RoHS / REACH / Conflict Minerals)。

    Args:
        material_id: 材料代碼 (如 'structural_steel', 'al_6061_t6', 'copper_c11000', 'fr4')。
        regulation: 評估法規 ('RoHS', 'REACH', 'Conflict_Minerals')。
        dry_run: 僅驗證法規代碼。
    """
    if dry_run:
        return _envelope({"ok": True, "dry_run": True, "material": material_id, "regulation": regulation})

    driver = GrantaDriver()
    result = driver.evaluate_compliance(material_id=material_id, regulation=regulation)
    result = driver.with_backend_metadata(result)
    return _envelope({"ok": True, **result})


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def granta_get_temperature_curve(
    material_id: str = "structural_steel",
    temperature_c: float = 250.0,
    property_name: str = "youngs_modulus_gpa",
    dry_run: bool = False,
) -> dict:
    """計算高溫環境下材料物性之熱軟化退化值與折減係數。

    Args:
        material_id: 材料代碼。
        temperature_c: 工作環境溫度 (攝氏度 C)。
        property_name: 評估物理屬性 (預設 'youngs_modulus_gpa')。
        dry_run: 僅驗證參數。
    """
    if dry_run:
        return _envelope({"ok": True, "dry_run": True, "temp": temperature_c})

    driver = GrantaDriver()
    result = driver.compute_temperature_degradation(
        material_id=material_id,
        temperature_c=temperature_c,
        property_name=property_name,
    )
    result = driver.with_backend_metadata(result)
    return _envelope({"ok": True, **result})
