import ast

from scripts.api_extraction.extract_pydyna_api import _extract_class_members


def test_deck_member_extraction_is_static_and_omits_inherited_and_setter_members():
    module = ast.parse(
        '''
class Parent:
    def inherited(self):
        """Inherited API."""

class Deck(Parent):
    @property
    def title(self) -> str:
        """Deck title."""
        raise AssertionError("AST extraction must not execute property getters")

    @title.setter
    def title(self, value: str):
        raise AssertionError("AST extraction must not execute property setters")

    def append(self, keyword, check=False):
        """Append a keyword."""
'''
    )

    class_info, methods, properties = _extract_class_members(module, "Deck", "deck.py")

    assert class_info == {"name": "Deck", "doc": ""}
    assert [item["name"] for item in methods] == ["append"]
    assert methods[0]["signature"] == "(self, keyword, check=False)"
    assert [item["name"] for item in properties] == ["title"]
    assert properties[0]["type"] == "str"
