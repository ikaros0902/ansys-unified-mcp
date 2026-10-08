# -*- coding: utf-8 -*-
"""optiSLang MOP (Metamodel of Optimal Prognosis) 腳本生成與配置單元測試。"""

import pytest
from ansys_unified_mcp.products.optislang import controller
from ansys_unified_mcp.products.optislang.tools import optislang_setup_mop


def test_optislang_generate_mop_script():
    """驗證 MOP 腳本模板生成完整性。"""
    params = [
        {"name": "width", "min": 10.0, "max": 50.0, "default": 25.0},
        {"name": "height", "min": 5.0, "max": 20.0, "default": 10.0},
    ]
    responses = ["equivalent_stress", "total_deformation"]

    script = controller.generate_mop_script(
        input_parameters=params,
        output_responses=responses,
        samples=150,
    )

    assert "import optislang" in script
    assert "width" in script
    assert "height" in script
    assert "equivalent_stress" in script
    assert "total_deformation" in script
    assert "150 samples" in script


def test_optislang_setup_mop_without_execution():
    """驗證在未連線時產生腳本但不直接執行 (execute_now=False)。"""
    params = [{"name": "radius", "min": 1.0, "max": 10.0}]
    responses = ["mass"]

    res = controller.setup_mop(
        input_parameters=params,
        output_responses=responses,
        samples=50,
        execute_now=False,
    )

    assert res["ok"] is True
    assert "script" in res
    assert "radius" in res["script"]


def test_optislang_setup_mop_with_execution_disconnected():
    """驗證在未連線狀態下若強行要求 execute_now=True 會優雅回報錯誤。"""
    params = [{"name": "thickness", "min": 0.5, "max": 2.0}]
    responses = ["stiffness"]

    res = controller.setup_mop(
        input_parameters=params,
        output_responses=responses,
        samples=30,
        execute_now=True,
    )

    assert res["ok"] is False
    assert "尚未連線" in res["error"]
    assert "script" in res


def test_optislang_setup_mop_mcp_tool():
    """驗證 optislang_setup_mop 工具的回傳信封封裝。"""
    params = [{"name": "force", "min": 100.0, "max": 1000.0}]
    responses = ["max_disp"]

    envelope = optislang_setup_mop(
        input_parameters=params,
        output_responses=responses,
        samples=80,
        execute_now=False,
    )

    assert envelope["ok"] is True
    assert "force" in envelope["script"]

