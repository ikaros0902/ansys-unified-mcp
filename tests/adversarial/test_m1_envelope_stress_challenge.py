"""Milestone 1 Envelope Stress & Extreme Defense Challenge Suite.

Target:
- `src/ansys_unified_mcp/tools/mechanical.py` (_safe_json_response & tool envelopes)

Objective:
1. Adversarial stress testing of `_safe_json_response` and tool output envelopes:
   - Inject IronPython crash strings (NullReferenceException, Traceback, etc.)
   - Inject malformed/non-standard strings (empty, HTML, truncated JSON, noisy logs)
   - Inject boundary dicts (ok: True, ok: False, missing ok, empty dict, etc.)
2. Empirical verification:
   - ZERO FALSE POSITIVES: Under ANY crash/error string, `ok` MUST NEVER be True.
   - 100% COMPLIANT ENVELOPE: Output MUST ALWAYS be valid JSON, root MUST be dict with "ok": bool.
3. Test all 39 Mechanical canonical tools and 39 legacy aliases under adversarial script outputs.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

import asyncio
import json
import pytest
from unittest.mock import patch

import ansys_unified_mcp.tools.mechanical as mechanical_mod
from ansys_unified_mcp.tools.mechanical import _safe_json_response, _is_error_output

# 歷史漏洞探查測試：此檔案用於在修復前證明 14 處漏洞存在。
# 漏洞已於 M1 全數修復完畢，現由 test_final_stress_harness.py 擔任驗收守護。
# 因此 Tier 1 (TestSafeJsonResponseUnitStress) 的防禦斷言現已實際通過，
# 改為正式守門測試（不再標記 xfail）；僅 Tier 2 / Tier 3 兩個「證明漏洞存在」
# 的探查類別維持 xfail（其斷言預期漏洞仍在，修復後必然失敗）。


def run_async(coro):
    return asyncio.run(coro)


# ===========================================================================
# Adversarial Payloads
# ===========================================================================

IRONPYTHON_CRASH_PAYLOADS = [
    (
        "IronPython NullReferenceException",
        "Script error: System.NullReferenceException: Object reference not set to an instance of an object.\n"
        "   at Ansys.ACT.Automation.Mechanical.Model.get_Geometry()\n"
        "   at Microsoft.Scripting.Interpreter.FuncCallInstruction`2.Run(InterpretedFrame frame)",
    ),
    (
        "Standard Python Traceback",
        "Traceback (most recent call last):\n"
        '  File "<string>", line 2, in <module>\n'
        "ZeroDivisionError: integer division or modulo by zero",
    ),
    (
        "IronPython SyntaxError",
        'File "<string>", line 1\n    for body in \n                ^\nSyntaxError: unexpected token',
    ),
    (
        "ACT System.Exception",
        "System.Exception: The Mechanical editor is currently busy or unresponsive.\n"
        "   at Ansys.ACT.Core.Automation.MechanicalAutomationEngine.ExecuteCommand(String command)",
    ),
    (
        "ACT InvalidOperationException",
        "System.InvalidOperationException: Collection was modified; enumeration operation may not execute.\n"
        "   at System.Collections.ArrayList.ArrayListEnumeratorSimple.MoveNext()",
    ),
    (
        "PyMechanical Connection Error",
        "ansys.mechanical.core.errors.MechanicalConnectionError: Connection reset by peer: gRPC channel terminated",
    ),
    (
        "Generic NameError",
        "NameError: name 'ExtAPI' is not defined",
    ),
    (
        "IndexError",
        "IndexError: list index out of range: Analyses[5]",
    ),
    (
        "KeyError",
        "KeyError: 'Model'",
    ),
    (
        "AttributeError",
        "AttributeError: 'NoneType' object has no attribute 'GetGeoBody'",
    ),
]

MALFORMED_NONSTANDARD_PAYLOADS = [
    ("Empty string", ""),
    ("Whitespace only", "   \n\t  \r\n   "),
    (
        "HTML 502 Bad Gateway",
        "<html>\r\n<head><title>502 Bad Gateway</title></head>\r\n<body>\r\n<center><h1>502 Bad Gateway</h1></center>\r\n</body>\r\n</html>",
    ),
    (
        "HTML 500 Internal Server Error",
        "<!DOCTYPE html><html><body><h1>Internal Server Error</h1><p>The server encountered an error.</p></body></html>",
    ),
    ("Truncated JSON dict", '{"status": "running", "elements": 1045, "progress":'),
    ("Truncated JSON list", '["Body1", "Body2", "Body'),
    ("Malformed JSON trailing comma", '{"ok": true, "materials": ["Steel", "Aluminum",],}'),
    ("Single quoted pseudo-JSON", "{'ok': True, 'count': 42}"),
    ("Plain string literal", '"Just a raw string"'),
    ("Plain integer", "98765"),
    ("Plain float", "3.14159265"),
    ("Plain boolean true", "true"),
    ("Plain boolean false", "false"),
    ("JSON null", "null"),
    ("Random binary junk", "\x00\x01\x02\xff\xfe\xfd\x07\x08"),
    ("Unescaped C# snippet", 'public void AddSupport() {\n    Console.WriteLine("Hello");\n}'),
    ("Large spam string 4KB", "CRASH_AND_FAIL_" * 250),
]

NOISY_LOG_PAYLOADS = [
    (
        "Preceding ACT debug logs + valid JSON",
        "[INFO] Initializing Mechanical automation session...\n"
        "[DEBUG] Model loaded successfully.\n"
        '{"status": "ready", "count": 12}',
    ),
    (
        "Valid JSON + trailing ACT shutdown logs",
        '{"status": "completed", "time_s": 1.23}\n'
        "[INFO] Releasing memory...\n"
        "[DEBUG] Session shutdown.",
    ),
    (
        "Multi-line sandwich logs with valid JSON in middle",
        "========================================\n"
        "RUNNING ANALYSIS SCRIPT\n"
        "========================================\n"
        '{"mesh_nodes": 4500, "mesh_elements": 1200}\n'
        "Script finished with exit code 0.\n"
        "Cleaning up temporary buffers.",
    ),
]

BOUNDARY_DICTS = [
    ("Dict with explicit ok True", {"ok": True, "data": "all good", "count": 5}),
    ("Dict with explicit ok False", {"ok": False, "error": "Explicit failure", "code": 404}),
    ("Dict without ok key", {"data": [1, 2, 3], "status": "computed"}),
    ("Empty dict", {}),
    ("Nested dict without root ok", {"result": {"ok": True, "value": 10}}),
]

# 39 Canonical mechanical tools with representative arguments
MECHANICAL_39_TOOL_SPECS = [
    ("mechanical_list_instances", "list_instances", {}),
    ("mechanical_connect", "connect_to_mechanical", {"port": 59999}),
    ("mechanical_launch", "launch_mechanical", {"batch": True}),
    ("mechanical_disconnect", "disconnect_from_mechanical", {}),
    ("mechanical_check_connection", "check_mechanical_connection", {}),
    ("mechanical_get_model_info", "get_model_info", {}),
    ("mechanical_list_materials", "list_materials", {}),
    ("mechanical_assign_material", "assign_material", {"body_name": "Body1", "material_name": "Structural Steel"}),
    ("mechanical_set_mesh_element_size", "set_mesh_element_size", {"element_size_mm": 5.0}),
    ("mechanical_generate_mesh", "generate_mesh", {}),
    ("mechanical_get_mesh_statistics", "get_mesh_statistics", {}),
    ("mechanical_add_fixed_support", "add_fixed_support", {"named_selection": "FixedNS", "analysis_index": 0}),
    ("mechanical_add_force", "add_force", {"named_selection": "ForceNS", "fx_n": 0.0, "fy_n": -100.0, "fz_n": 0.0, "analysis_index": 0}),
    ("mechanical_add_pressure", "add_pressure", {"named_selection": "PressNS", "magnitude_pa": 1000.0, "analysis_index": 0}),
    ("mechanical_list_boundary_conditions", "list_boundary_conditions", {"analysis_index": 0}),
    ("mechanical_solve_analysis", "solve_analysis", {"analysis_index": 0}),
    ("mechanical_get_solve_status", "get_solve_status", {"analysis_index": 0}),
    ("mechanical_add_total_deformation_all_modes", "add_total_deformation_all_modes", {"num_modes": 6, "analysis_index": 0}),
    ("mechanical_add_total_deformation", "add_total_deformation", {"mode": 0, "analysis_index": 0}),
    ("mechanical_get_modal_frequencies", "get_modal_frequencies", {"analysis_index": 0}),
    ("mechanical_generate_report", "generate_report", {"output_path": "report.docx", "analysis_index": 0, "fmt": "docx"}),
    ("mechanical_run_script", "run_mechanical_script", {"script": "print('test')"}),
    ("mechanical_list_named_selections", "list_named_selections", {}),
    ("mechanical_delete_named_selection", "delete_named_selection", {"name": "NS1"}),
    ("mechanical_suppress_bodies", "suppress_bodies", {"name_prefix": "Part", "suppress": True}),
    ("mechanical_list_point_masses", "list_point_masses", {}),
    ("mechanical_add_frictionless_support", "add_frictionless_support", {"named_selection": "FricNS", "analysis_index": 0}),
    ("mechanical_add_displacement", "add_displacement", {"named_selection": "DispNS", "x_mm": 0.0, "y_mm": None, "z_mm": None, "analysis_index": 0}),
    ("mechanical_add_remote_displacement", "add_remote_displacement", {"named_selection": "RDispNS", "x_mm": 0.0, "rot_z_deg": 10.0, "analysis_index": 0}),
    ("mechanical_add_standard_gravity", "add_standard_gravity", {"analysis_index": 0, "x_component": 0.0, "y_component": -1.0, "z_component": 0.0}),
    ("mechanical_add_remote_force", "add_remote_force", {"named_selection": "RForceNS", "fx_n": 50.0, "analysis_index": 0}),
    ("mechanical_add_moment", "add_moment", {"named_selection": "MomNS", "mx_nm": 10.0, "analysis_index": 0}),
    ("mechanical_add_equivalent_stress", "add_equivalent_stress", {"named_selection": "", "analysis_index": 0}),
    ("mechanical_add_directional_deformation", "add_directional_deformation", {"axis": "Y", "named_selection": "", "analysis_index": 0}),
    ("mechanical_add_principal_stress", "add_principal_stress", {"which": "max", "analysis_index": 0}),
    ("mechanical_add_stress_tool", "add_stress_tool", {"analysis_index": 0}),
    ("mechanical_add_reaction_force", "add_reaction_force", {"named_selection": "ReactNS", "analysis_index": 0}),
    ("mechanical_convert_prefix_to_point_mass", "convert_prefix_to_point_mass", {"body_name_prefix": "Bolt", "proximity_multiplier": 3.0}),
    ("mechanical_convert_part_to_point_mass", "convert_part_to_point_mass", {"part_name": "PartA", "proximity_multiplier": 3.0}),
]


# ===========================================================================
# Helper Validation Function
# ===========================================================================

def validate_envelope(output_str: str, expect_ok: bool = None, allow_non_bool_ok: bool = False) -> dict:
    """Validate that output_str complies with the envelope specification:
    1. Valid JSON string
    2. Parsed root object is a dict
    3. Root object contains 'ok' key
    4. data['ok'] is strictly a boolean (unless allow_non_bool_ok=True)
    5. If expect_ok is not None, assert data['ok'] == expect_ok
    """
    assert isinstance(output_str, str), f"Output must be str, got {type(output_str)}"
    try:
        data = json.loads(output_str)
    except Exception as e:
        pytest.fail(f"Output is not valid JSON: {e}\nRaw output:\n{output_str[:500]}")

    assert isinstance(data, dict), f"Root JSON object must be dict, got {type(data)}: {data}"
    assert "ok" in data, f"Envelope missing 'ok' key: {data}"

    if not allow_non_bool_ok:
        assert isinstance(data["ok"], bool), f"'ok' field must be bool, got {type(data['ok'])}: {data['ok']}"

    if expect_ok is not None:
        assert data["ok"] is expect_ok, f"Expected ok={expect_ok}, got ok={data['ok']} in payload: {data}"

    return data


# ===========================================================================
# Tier 1: _safe_json_response Unit-Level Stress Tests
# ===========================================================================

class TestSafeJsonResponseUnitStress:
    """Adversarial stress testing directly against _safe_json_response."""

    @pytest.mark.parametrize("name, payload", IRONPYTHON_CRASH_PAYLOADS)
    def test_ironpython_crashes_never_false_positive(self, name, payload):
        """Under all pure IronPython/ACT crash outputs, _safe_json_response MUST return ok: False."""
        resp = _safe_json_response(payload)
        data = validate_envelope(resp, expect_ok=False)
        assert "error" in data, f"Error payload should contain 'error' message: {data}"
        assert "raw_output" in data, f"Error payload should contain 'raw_output': {data}"
        assert payload in data["raw_output"] or data["raw_output"] == payload

    @pytest.mark.parametrize("name, payload", MALFORMED_NONSTANDARD_PAYLOADS)
    def test_malformed_and_nonstandard_inputs(self, name, payload):
        """Under empty, HTML, broken JSON, scalar JSON literals, _safe_json_response MUST return ok: False."""
        resp = _safe_json_response(payload)
        data = validate_envelope(resp, expect_ok=False)
        assert "error" in data
        assert "raw_output" in data

    @pytest.mark.parametrize("name, payload", NOISY_LOG_PAYLOADS)
    def test_noisy_logs_with_valid_json_embedded(self, name, payload):
        """When logs contain a valid JSON line amidst noisy lines, it extracts it with ok: True."""
        resp = _safe_json_response(payload)
        data = validate_envelope(resp, expect_ok=True)
        if "count" in payload:
            assert data.get("count") == 12
        elif "mesh_nodes" in payload:
            assert data.get("mesh_nodes") == 4500

    @pytest.mark.parametrize("name, payload", BOUNDARY_DICTS)
    def test_boundary_dicts(self, name, payload):
        """Boundary dict inputs must always have root ok: bool and preserve explicit ok values."""
        resp = _safe_json_response(payload)
        if "ok" in payload:
            data = validate_envelope(resp, expect_ok=payload["ok"])
        else:
            data = validate_envelope(resp, expect_ok=True)

    def test_json_list_input_handling(self):
        """When input is a JSON list (e.g. '["Body1", "Body2"]'), it should wrap into {'ok': True, 'data': [...]}."""
        resp = _safe_json_response('["Body1", "Body2", "Body3"]')
        data = validate_envelope(resp, expect_ok=True)
        assert data.get("data") == ["Body1", "Body2", "Body3"]

    def test_non_str_non_dict_inputs(self):
        """When input is neither str nor dict (e.g. int, list, None)."""
        # Python list
        resp_list = _safe_json_response([1, 2, 3])
        data_list = validate_envelope(resp_list, expect_ok=True)
        assert data_list.get("data") == [1, 2, 3]

        # Python int
        resp_int = _safe_json_response(12345)
        validate_envelope(resp_int, expect_ok=False)

        # None
        resp_none = _safe_json_response(None)
        validate_envelope(resp_none, expect_ok=False)


# ===========================================================================
# Tier 2: Vulnerability Hunting Probes (Empirical Proof of Flaws)
# ===========================================================================

@pytest.mark.xfail(
    reason="Historic vulnerability probe: these assertions expect the pre-M1 false-positive behaviour, "
           "which has since been fixed. Regression cover now lives in test_final_stress_harness.py.",
    strict=False,
)
class TestAdversarialVulnerabilityProbes:
    """Targeted adversarial scenarios demonstrating concrete breakthroughs and false positives."""

    def test_vulnerability_probe_crash_after_json_log_line(self):
        """ATTACK: Script outputs a JSON status line, then immediately crashes with IronPython Traceback!
        
        Example payload:
        `{"status": "initializing"}\nScript error: System.NullReferenceException: Object reference not set`
        
        EMPIRICAL OBSERVATION:
        _safe_json_response iterates line by line. Line 1 starts with '{' and ends with '}',
        so it parses line 1 as JSON, blindly adds "ok": True, and returns!
        The deadly crash that occurred afterwards is completely swallowed!
        """
        payload = (
            '{"status": "initializing"}\n'
            'Script error: System.NullReferenceException: Object reference not set to an instance of an object.\n'
            '   at Ansys.ACT.Automation.Mechanical.Model.get_Geometry()'
        )
        resp = _safe_json_response(payload)
        data = json.loads(resp)

        # EMPIRICAL PROOF: data['ok'] is True despite a fatal crash!
        assert data.get("ok") is True, "Confirmed: _safe_json_response yielded false positive ok: True!"
        assert "initializing" in data.get("status")

    def test_vulnerability_probe_error_dict_without_ok_key(self):
        """ATTACK: Backend or script outputs a JSON error dict without "ok": false.
        
        Example:
        `{"error": "Mechanical crashed", "code": 500}`
        
        EMPIRICAL OBSERVATION:
        _safe_json_response checks: if "ok" not in data: data = {"ok": True, **data}
        Result: {"ok": True, "error": "Mechanical crashed", "code": 500}
        An outright error is stamped as ok: True!
        """
        payload = '{"error": "Mechanical crashed", "code": 500}'
        resp = _safe_json_response(payload)
        data = json.loads(resp)

        # EMPIRICAL PROOF: Error dict is falsely stamped as ok: True!
        assert data.get("ok") is True, "Confirmed: error dict was marked as ok: True!"

    def test_vulnerability_probe_non_boolean_ok(self):
        """ATTACK: Input dictionary has "ok": None or "ok": "false".
        
        EMPIRICAL OBSERVATION:
        _safe_json_response only checks if "ok" not in data.
        Since "ok" key exists, it leaves data["ok"] unchanged.
        Thus data["ok"] is None (NoneType) or "false" (str), violating "ok": bool constraint!
        """
        resp_none = _safe_json_response({"ok": None, "message": "unspecified"})
        data_none = json.loads(resp_none)
        assert data_none["ok"] is None
        assert not isinstance(data_none["ok"], bool), "Confirmed: 'ok' is not bool (is NoneType)!"

        resp_str = _safe_json_response({"ok": "false", "message": "failed"})
        data_str = json.loads(resp_str)
        assert data_str["ok"] == "false"
        assert not isinstance(data_str["ok"], bool), "Confirmed: 'ok' is not bool (is str)!"


# ===========================================================================
# Tier 3: All 39 Tools Adversarial Injection Analysis
# ===========================================================================

@pytest.mark.xfail(
    reason="Historic vulnerability probe: these assertions expect the pre-M1 14 false-positive tool entry points, "
           "which have since been fixed. Regression cover now lives in test_final_stress_harness.py.",
    strict=False,
)
class TestAll39MechanicalToolsAdversarialStress:
    """Stress testing all 39 mechanical tools when controller is online but run_script returns crash/garbage."""

    # The 7 canonical tools (and their 7 aliases) that do NOT use _safe_json_response:
    VULNERABLE_NON_SAFE_TOOLS = {
        "mechanical_assign_material", "assign_material",
        "mechanical_set_mesh_element_size", "set_mesh_element_size",
        "mechanical_generate_mesh", "generate_mesh",
        "mechanical_solve_analysis", "solve_analysis",
        "mechanical_add_total_deformation_all_modes", "add_total_deformation_all_modes",
        "mechanical_add_total_deformation", "add_total_deformation",
        "mechanical_run_script", "run_mechanical_script",
    }

    @pytest.fixture(autouse=True)
    def mock_online_controller(self):
        """Mock controller as online/connected."""
        with patch.object(mechanical_mod.controller, "is_connected", return_value=True), \
             patch.object(mechanical_mod.controller, "status", return_value={"connected": True, "port": 59999, "pid": 1234}), \
             patch.object(mechanical_mod.controller, "connect", return_value={"ok": False, "error": "Crash during connect"}), \
             patch.object(mechanical_mod.controller, "launch", return_value={"ok": False, "error": "Crash during launch"}), \
             patch.object(mechanical_mod.controller, "disconnect", return_value={"ok": False, "error": "Crash during disconnect"}):
            yield

    def test_tools_under_ironpython_crash(self):
        """Under IronPython crash string, verify which tools defend and which fail."""
        crash_msg = (
            "Script error: System.NullReferenceException: Object reference not set to an instance of an object.\n"
            "   at Ansys.ACT.Automation.Mechanical.Model.get_Geometry()\n"
            "   at Microsoft.Scripting.Interpreter.FuncCallInstruction`2.Run(InterpretedFrame frame)"
        )

        async def _test():
            with patch.object(mechanical_mod.controller, "run_script", return_value=crash_msg):
                false_positives = []
                for canonical, alias, kwargs in MECHANICAL_39_TOOL_SPECS:
                    for name in (canonical, alias):
                        if name in ("mechanical_list_instances", "list_instances",
                                    "mechanical_connect", "connect_to_mechanical",
                                    "mechanical_launch", "launch_mechanical",
                                    "mechanical_disconnect", "disconnect_from_mechanical",
                                    "mechanical_check_connection", "check_mechanical_connection"):
                            continue

                        res = await mcp.call_tool(name, kwargs)
                        text = res.content[0].text if res.content else ""
                        data = json.loads(text)
                        if data.get("ok") is True:
                            false_positives.append(name)

                # Under explicit IronPython crash keyword, _is_error_output catches it
                assert len(false_positives) == 0, f"False positives under explicit IronPython crash: {false_positives}"

        run_async(_test())

    def test_tools_under_empty_output_reveals_14_vulnerabilities(self):
        """When script output is empty (e.g. silent process crash / broken pipe),
        the 7 tools (14 entry points) using _is_error_output fail to detect error and output ok: True!
        """
        async def _test():
            with patch.object(mechanical_mod.controller, "run_script", return_value=""):
                false_positives = []
                defended_tools = []

                for canonical, alias, kwargs in MECHANICAL_39_TOOL_SPECS:
                    for name in (canonical, alias):
                        if name in ("mechanical_list_instances", "list_instances",
                                    "mechanical_connect", "connect_to_mechanical",
                                    "mechanical_launch", "launch_mechanical",
                                    "mechanical_disconnect", "disconnect_from_mechanical",
                                    "mechanical_check_connection", "check_mechanical_connection"):
                            continue

                        res = await mcp.call_tool(name, kwargs)
                        text = res.content[0].text if res.content else ""
                        data = json.loads(text)
                        if data.get("ok") is True:
                            false_positives.append(name)
                        else:
                            defended_tools.append(name)

                # Exactly 14 tools (7 canonical + 7 aliases) produce false positives!
                assert set(false_positives) == self.VULNERABLE_NON_SAFE_TOOLS, (
                    f"Expected exactly 14 false positive tools, got: {false_positives}"
                )
                print(f"\n[EMPIRICAL PROOF] 14 tools yielded false positives on empty output: {sorted(false_positives)}")

        run_async(_test())

    def test_tools_under_html_502_reveals_14_vulnerabilities(self):
        """When script output is HTML 502 Bad Gateway (e.g. gateway error),
        the same 14 tool entry points fail to detect error and output ok: True!
        """
        html_msg = "<html><body><h1>502 Bad Gateway</h1></body></html>"
        async def _test():
            with patch.object(mechanical_mod.controller, "run_script", return_value=html_msg):
                false_positives = []

                for canonical, alias, kwargs in MECHANICAL_39_TOOL_SPECS:
                    for name in (canonical, alias):
                        if name in ("mechanical_list_instances", "list_instances",
                                    "mechanical_connect", "connect_to_mechanical",
                                    "mechanical_launch", "launch_mechanical",
                                    "mechanical_disconnect", "disconnect_from_mechanical",
                                    "mechanical_check_connection", "check_mechanical_connection"):
                            continue

                        res = await mcp.call_tool(name, kwargs)
                        text = res.content[0].text if res.content else ""
                        data = json.loads(text)
                        if data.get("ok") is True:
                            false_positives.append(name)

                assert set(false_positives) == self.VULNERABLE_NON_SAFE_TOOLS, (
                    f"Expected exactly 14 false positive tools, got: {false_positives}"
                )
                print(f"\n[EMPIRICAL PROOF] 14 tools yielded false positives on HTML 502: {sorted(false_positives)}")

        run_async(_test())
