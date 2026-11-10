import ast

from scripts.api_extraction.extract_geometry_core_api import _class_members


def test_modeler_member_extraction_is_static_and_skips_inherited_and_setters():
    module = ast.parse(
        '''
class Parent:
    def inherited(self):
        """Inherited method."""

class Modeler(Parent):
    @property
    def design(self) -> str:
        """Active design."""
        raise AssertionError("AST extraction must not execute getters")

    @design.setter
    def design(self, value):
        raise AssertionError("AST extraction must not execute setters")

    def create_design(self, name: str):
        """Create a design."""
'''
    )

    methods, properties = _class_members(module.body[1], "modeler.py")

    assert [item["name"] for item in methods] == ["create_design"]
    assert methods[0]["signature"] == "(self, name: str)"
    assert [item["name"] for item in properties] == ["design"]
    assert properties[0]["type"] == "str"
