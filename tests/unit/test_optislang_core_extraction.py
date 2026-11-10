from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "api_extraction" / "extract_optislang_core_api.py"
SPEC = importlib.util.spec_from_file_location("extract_optislang_core_api", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_optislang_core_snapshot_uses_exact_sdk_and_excludes_mismatched_docs(tmp_path, monkeypatch):
    monkeypatch.setattr(MODULE, "OUT_PATH", tmp_path / "optislang_core_api.json")
    snapshot = MODULE.extract_optislang_core_api()
    assert MODULE.OUT_PATH.is_file()
    assert json.loads(MODULE.OUT_PATH.read_text(encoding="utf-8")) == snapshot
    record = snapshot["modules"][MODULE.MODULE_NAME]["classes"]["Optislang"]

    assert snapshot["sdk_version"] == "1.6.0"
    assert snapshot["statistics"] == {
        "total_modules": 1,
        "total_classes": 1,
        "total_methods": 18,
        "total_properties": 9,
        "total_functions": 0,
    }
    assert snapshot["sources"]["excluded_api_references"][0]["version"] == "1.7.0"
    assert len(record["methods"]) == 18
    assert len(record["properties"]) == 9
    assert all(member["sdk_source_path"].endswith("/ansys/optislang/core/optislang.py") for member in record["methods"])


def test_optislang_class_member_parser_does_not_run_properties_or_include_inherited_members():
    tree = ast.parse(
        """
class Parent:
    def inherited(self):
        pass

class Optislang(Parent):
    @property
    def project(self) -> str:
        raise AssertionError("AST extraction must not execute getters")

    @project.setter
    def project(self, value):
        raise AssertionError("AST extraction must not execute setters")

    def open(self, path: str):
        pass
"""
    )
    methods, properties = MODULE._class_members(tree.body[1], "optislang.py")

    assert [item["name"] for item in methods] == ["open"]
    assert methods[0]["signature"] == "(self, path: str)"
    assert [item["name"] for item in properties] == ["project"]
