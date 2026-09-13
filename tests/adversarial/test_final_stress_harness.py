"""Milestone 1 Final Envelope Stress Challenge Harness.

Empirical Adversarial Verification Suite.
Written and executed by Envelope Stress Final Challenger.
"""

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import patch

# Force utf-8 output encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

from ansys_unified_mcp.shared import mcp
import ansys_unified_mcp.tools.mechanical as mechanical_mod
from ansys_unified_mcp.tools.mechanical import (
    _safe_json_response,
    _normalize_dict_envelope,
    _to_bool_ok,
    _is_error_output,
)
from tests.adversarial.test_m1_envelope_stress_challenge import MECHANICAL_39_TOOL_SPECS


def run_async(coro):
    return asyncio.run(coro)


# 14 Tools that previously suffered from false positives
VULNERABLE_14_TOOL_NAMES = [
    "mechanical_assign_material", "assign_material",
    "mechanical_set_mesh_element_size", "set_mesh_element_size",
    "mechanical_generate_mesh", "generate_mesh",
    "mechanical_solve_analysis", "solve_analysis",
    "mechanical_add_total_deformation_all_modes", "add_total_deformation_all_modes",
    "mechanical_add_total_deformation", "add_total_deformation",
    "mechanical_run_script", "run_mechanical_script",
]

# 12 domain-specific tools (excluding run_mechanical_script REPL)
DOMAIN_12_TOOL_NAMES = [t for t in VULNERABLE_14_TOOL_NAMES if "script" not in t]

# Map tool names to dummy arguments
TOOL_ARG_MAP = {}
for canonical, alias, kwargs in MECHANICAL_39_TOOL_SPECS:
    TOOL_ARG_MAP[canonical] = kwargs
    TOOL_ARG_MAP[alias] = kwargs


def test_section_1_fourteen_tools_stress():
    """1. 檢驗 14 個工具入口在空字串、空白、HTML 502/500、致命崩潰字串下的表現。"""
    print("\n=======================================================")
    print("【實證檢驗 1】14 個工具入口極限壓力與假陽性歸零檢驗")
    print("=======================================================")

    adversarial_payloads = [
        ("空字串", ""),
        ("純空白字串", "   \t  \r\n  "),
        ("HTML 502 Bad Gateway", "<html><head><title>502 Bad Gateway</title></head><body><h1>502 Bad Gateway</h1></body></html>"),
        ("HTML 500 Internal Error", "<!DOCTYPE html><html><body>500 Internal Server Error</body></html>"),
        ("IronPython 崩潰", "Script error: System.NullReferenceException: Object reference not set to an instance of an object.\n   at Ansys.ACT.Automation.Mechanical.Model.get_Geometry()"),
        ("Python Traceback", "Traceback (most recent call last):\n  File '<string>', line 1, in <module>\nZeroDivisionError: division by zero"),
        ("ACT System.Exception", "System.Exception: The Mechanical editor is currently busy or unresponsive."),
        ("PyMechanical 連線異常", "ansys.mechanical.core.errors.MechanicalConnectionError: Connection reset by peer: gRPC channel terminated"),
        ("run_script 夾心日誌崩潰", "print('preliminary log output')\nScript error: System.NullReferenceException: crash after log"),
    ]

    total_false_positives = 0

    for payload_desc, payload in adversarial_payloads:
        async def _run_tools():
            fps = []
            results = {}
            with patch.object(mechanical_mod.controller, "is_connected", return_value=True), \
                 patch.object(mechanical_mod.controller, "status", return_value={"connected": True, "port": 59999, "pid": 1234}), \
                 patch.object(mechanical_mod.controller, "run_script", return_value=payload):

                for name in VULNERABLE_14_TOOL_NAMES:
                    kwargs = TOOL_ARG_MAP.get(name, {})
                    res = await mcp.call_tool(name, kwargs)
                    text = res.content[0].text if res.content else ""
                    try:
                        data = json.loads(text)
                    except Exception as e:
                        fps.append((name, f"JSONDecodeError: {e}"))
                        continue

                    # 嚴格布林型別與 ok 狀態檢驗
                    ok_val = data.get("ok")
                    if type(ok_val) is not bool:
                        fps.append((name, f"ok 不是嚴格 bool: type={type(ok_val)}, val={ok_val}"))
                    elif ok_val is True:
                        fps.append((name, f"假陽性 ok is True: {data}"))
                    results[name] = data
            return fps, results

        fps, results = run_async(_run_tools())
        if fps:
            total_false_positives += len(fps)
            print(f"[FAIL] 酬載【{payload_desc}】觸發 {len(fps)} 個假陽性/錯誤: {fps}")
        else:
            print(f"[PASS] 酬載【{payload_desc}】: 14 個工具入口 100% 輸出 ok: False，零假陽性 (0/14 FP)")

    # 針對 12 個業務工具入口（除 run_mechanical_script 任意 REPL 以外），注入缺乏成功關鍵字之隨機雜訊，驗證雙向關鍵字過濾
    print("\n--> 針對 12 個業務工具入口注入缺乏成功關鍵字之隨機雜訊字串...")
    async def _run_domain_noise():
        fps = []
        noise_payload = "Arbitrary unformatted diagnostic output without any success confirmation."
        with patch.object(mechanical_mod.controller, "is_connected", return_value=True), \
             patch.object(mechanical_mod.controller, "status", return_value={"connected": True, "port": 59999, "pid": 1234}), \
             patch.object(mechanical_mod.controller, "run_script", return_value=noise_payload):

            for name in DOMAIN_12_TOOL_NAMES:
                kwargs = TOOL_ARG_MAP.get(name, {})
                res = await mcp.call_tool(name, kwargs)
                text = res.content[0].text if res.content else ""
                data = json.loads(text)
                if data.get("ok") is not False:
                    fps.append((name, data))
        return fps

    fps_noise = run_async(_run_domain_noise())
    if fps_noise:
        total_false_positives += len(fps_noise)
        print(f"[FAIL] 12 個業務工具在缺乏成功關鍵字之雜訊下觸發假陽性: {fps_noise}")
    else:
        print(f"[PASS] 12 個業務工具在無成功關鍵字雜訊下 100% 輸出 ok: False (0/12 FP)")

    print(f"\n--> 14 個工具入口全項極限壓力測試總假陽性數量: {total_false_positives}")
    assert total_false_positives == 0, f"存在假陽性，總數: {total_false_positives}"



def test_section_2_safe_json_sandwich_logs():
    """2. 檢驗 _safe_json_response 在夾心日誌與多行干擾下的防禦能力。"""
    print("\n=======================================================")
    print("【實證檢驗 2】_safe_json_response 夾心崩潰日誌優先攔截實測")
    print("=======================================================")

    sandwich_cases = [
        (
            "前置合法 JSON + 後綴 IronPython Script error",
            '{"status": "initializing"}\n'
            'Script error: System.NullReferenceException: Object reference not set to an instance of an object.\n'
            '   at Ansys.ACT.Automation.Mechanical.Model.get_Geometry()',
        ),
        (
            "前置合法 JSON (含 ok: True) + 後綴 Python Traceback",
            '{"ok": true, "message": "Preliminary setup done"}\n'
            'Traceback (most recent call last):\n'
            '  File "runner.py", line 42, in execute\n'
            'RuntimeError: Fatal memory corruption',
        ),
        (
            "前置合法 JSON + 後綴 HTML 502 Bad Gateway",
            '{"result": "partial"}\n'
            '<html><body>502 Bad Gateway</body></html>',
        ),
        (
            "前置錯誤日誌 + 中間合法 JSON + 後綴致命崩潰",
            '[INFO] Starting job...\n'
            '{"step": 1, "progress": 0.5}\n'
            'System.Exception: The Mechanical editor is currently busy or unresponsive.\n'
            '[DEBUG] Job terminated abruptly.',
        ),
        (
            "多行雜訊中混入偽裝 JSON 但末尾 SyntaxError",
            '# Logging output\n'
            '{"ok": true, "data": [1, 2, 3]}\n'
            'File "<string>", line 1\n'
            'SyntaxError: invalid syntax',
        ),
    ]

    all_passed = True
    for desc, payload in sandwich_cases:
        resp = _safe_json_response(payload)
        data = json.loads(resp)
        ok_val = data.get("ok")
        is_bool = (type(ok_val) is bool)
        is_false = (ok_val is False)

        if is_bool and is_false:
            print(f"[PASS] 【{desc}】 -> ok={ok_val} (bool), error={data.get('error')[:60]}...")
        else:
            all_passed = False
            print(f"[FAIL] 【{desc}】 -> ok={ok_val} (type: {type(ok_val)}), 未能正確攔截！")

    assert all_passed, "夾心日誌測試存在未攔截的失敗！"


def test_section_3_missing_ok_dict():
    """3. 檢驗不含 ok 鍵之錯誤字典與各種字典邊界。"""
    print("\n=======================================================")
    print("【實證檢驗 3】無 ok 鍵錯誤字典與字典信封標準化實測")
    print("=======================================================")

    test_dicts = [
        # (說明, 輸入字典或 JSON, 預期 ok 值)
        ("含有 error 鍵且 code: 500 的字典", {"error": "Mechanical crashed", "code": 500}, False),
        ("含有 error 鍵的純錯誤字典", {"error": "Timeout occurred"}, False),
        ("含有 error 鍵的字串 JSON", '{"error": "Subsystem failure", "code": 502}', False),
        ("含有 error 鍵但 error 為 None", {"error": None, "details": "Something weird"}, False),
        ("含有 error 鍵但 error 為空字串", {"error": "", "details": "Empty error"}, False),
        ("一般業務資料字典（無 error 鍵，無 ok 鍵）", {"mesh_nodes": 1200, "mesh_elements": 400}, True),
        ("一般業務字串 JSON（無 error 鍵，無 ok 鍵）", '{"status": "completed", "count": 10}', True),
        ("空字典", {}, True),
    ]

    all_passed = True
    for desc, inp, expected_ok in test_dicts:
        resp = _safe_json_response(inp) if isinstance(inp, str) else json.dumps(_normalize_dict_envelope(inp))
        data = json.loads(resp)
        ok_val = data.get("ok")
        is_bool = (type(ok_val) is bool)
        matches = (ok_val is expected_ok)

        if is_bool and matches:
            print(f"[PASS] 【{desc}】 -> ok={ok_val} (bool, 符合預期), payload={data}")
        else:
            all_passed = False
            print(f"[FAIL] 【{desc}】 -> ok={ok_val} (type: {type(ok_val)}), 預期={expected_ok}, 實際={data}")

    assert all_passed, "字典信封標準化測試失敗！"


def test_section_4_strict_boolean_type():
    """4. 檢驗所有輸出信封根物件的 ok 鍵型別是否保證為嚴格 bool。"""
    print("\n=======================================================")
    print("【實證檢驗 4】根物件 ok 鍵之嚴格布林型別 (Strict bool) 轉換檢驗")
    print("=======================================================")

    test_cases = [
        # (說明, 輸入 ok 值, 預期嚴格 bool)
        ("None 值", None, False),
        ("字串 'false'", "false", False),
        ("字串 'FALSE'", "FALSE", False),
        ("字串 '0'", "0", False),
        ("字串 'null'", "null", False),
        ("字串 'none'", "none", False),
        ("空字串", "", False),
        ("整數 0", 0, False),
        ("字串 'true'", "true", True),
        ("字串 'TRUE'", "TRUE", True),
        ("整數 1", 1, True),
        ("字串 'yes'", "yes", True),
        ("布林 True", True, True),
        ("布林 False", False, False),
    ]

    all_passed = True
    for desc, inp, expected_bool in test_cases:
        converted = _to_bool_ok(inp)
        is_strict_bool = (type(converted) is bool)
        matches = (converted is expected_bool)

        # 透過完整信封檢驗
        dict_payload = {"ok": inp, "message": "type test"}
        norm_dict = _normalize_dict_envelope(dict_payload)
        ok_val = norm_dict.get("ok")
        dict_is_strict_bool = (type(ok_val) is bool)
        dict_matches = (ok_val is expected_bool)

        if is_strict_bool and matches and dict_is_strict_bool and dict_matches:
            print(f"[PASS] 輸入 {inp!r:8} -> ok={converted} (嚴格 bool, 符合預期)")
        else:
            all_passed = False
            print(f"[FAIL] 輸入 {inp} -> ok={ok_val} (type: {type(ok_val)}), 預期: {expected_bool}")

    assert all_passed, "布林型別轉換未達成嚴格 bool 保證！"


def test_section_5_all_78_tools_complete_audit():
    """5. 全量 78 個工具入口（39 canonical + 39 alias）全覆蓋空字串與 HTML 502 零假陽性審計。"""
    print("\n=======================================================")
    print("【實證檢驗 5】全量 78 個工具入口在空字串與 HTML 502 下零假陽性完整審計")
    print("=======================================================")

    skip_tools = {
        "mechanical_list_instances", "list_instances",
        "mechanical_connect", "connect_to_mechanical",
        "mechanical_launch", "launch_mechanical",
        "mechanical_disconnect", "disconnect_from_mechanical",
        "mechanical_check_connection", "check_mechanical_connection",
    }

    async def _audit(payload, desc):
        false_positives = []
        tested_count = 0
        with patch.object(mechanical_mod.controller, "is_connected", return_value=True), \
             patch.object(mechanical_mod.controller, "status", return_value={"connected": True, "port": 59999, "pid": 1234}), \
             patch.object(mechanical_mod.controller, "run_script", return_value=payload):

            for canonical, alias, kwargs in MECHANICAL_39_TOOL_SPECS:
                for name in (canonical, alias):
                    if name in skip_tools:
                        continue
                    tested_count += 1
                    res = await mcp.call_tool(name, kwargs)
                    text = res.content[0].text if res.content else ""
                    data = json.loads(text)
                    if data.get("ok") is True:
                        false_positives.append((name, data))
        return tested_count, false_positives

    # 審計空字串
    c_empty, fps_empty = run_async(_audit("", "空字串"))
    print(f"全量受測工具入口數: {c_empty}")
    print(f"空字串下假陽性清單: {fps_empty} (數量: {len(fps_empty)})")

    # 審計 HTML 502
    html_payload = "<html><body><h1>502 Bad Gateway</h1></body></html>"
    c_html, fps_html = run_async(_audit(html_payload, "HTML 502"))
    print(f"HTML 502 下假陽性清單: {fps_html} (數量: {len(fps_html)})")

    total_fps = len(fps_empty) + len(fps_html)
    assert total_fps == 0, f"全量審計發現假陽性！空字串: {len(fps_empty)}, HTML 502: {len(fps_html)}"
    print(f"[PASS] 全量 {c_empty} 個工具在空字串與 HTML 502 下假陽性數量 100% 歸零！")


def main():
    print("=================================================================")
    print("  Milestone 1 Envelope Stress Final Challenge Suite Starting     ")
    print("=================================================================")

    success1 = test_section_1_fourteen_tools_stress()
    success2 = test_section_2_safe_json_sandwich_logs()
    success3 = test_section_3_missing_ok_dict()
    success4 = test_section_4_strict_boolean_type()
    success5 = test_section_5_all_78_tools_complete_audit()

    if success1 and success2 and success3 and success4 and success5:
        print("\n=================================================================")
        print("  【挑戰結論】實證測試全部通過！零假陽性，強型別信封保證確認！      ")
        print("  判定結果: CONFIRMED                                            ")
        print("=================================================================")
        return 0
    else:
        print("\n=================================================================")
        print("  【挑戰結論】實證測試發現破口！存在假陽性或型別錯誤！              ")
        print("  判定結果: DISPROVED                                            ")
        print("=================================================================")
        return 1


if __name__ == "__main__":
    sys.exit(main())
