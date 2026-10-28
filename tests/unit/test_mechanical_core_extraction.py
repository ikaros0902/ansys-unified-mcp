import ast

from scripts.api_extraction.extract_mechanical_core_api import _members, _signature


def test_mechanical_member_extraction_is_static_and_skips_property_setters():
    module = ast.parse(
        '''
class Mechanical:
    @property
    def name(self) -> str:
        """Instance name."""
        raise AssertionError("AST extraction must not execute property getters")

    @name.setter
    def name(self, value: str):
        raise AssertionError("AST extraction must not execute property setters")

    def exit(self, force=False):
        """Close the client."""
'''
    )
    cls = module.body[0]

    methods, properties = _members(cls, "mechanical.py")

    assert [item["name"] for item in methods] == ["exit"]
    assert methods[0]["signature"] == "(self, force=False)"
    assert [item["name"] for item in properties] == ["name"]
    assert properties[0]["type"] == "str"
    function = ast.parse("def launch_mechanical(port=10000): pass").body[0]
    assert _signature(function) == "(port=10000)"
