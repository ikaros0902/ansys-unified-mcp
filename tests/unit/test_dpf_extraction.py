from scripts.api_extraction.extract_dpf_api import _extract_members


def test_member_extraction_is_static_and_excludes_inherited_methods():
    class Parent:
        def inherited(self):
            """繼承方法。"""

    class Probe(Parent):
        @property
        def state(self):
            """狀態屬性。"""
            raise AssertionError("property getter must not execute")

        def run(self, count=2):
            """執行操作。"""

    methods, properties = _extract_members(Probe)

    assert [item["name"] for item in methods] == ["run"]
    assert methods[0]["signature"] == "(self, count=2)"
    assert [item["name"] for item in properties] == ["state"]
