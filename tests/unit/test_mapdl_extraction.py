from scripts.api_extraction.extract_mapdl_api import _extract_class_members


def test_static_member_extraction_preserves_signature_without_calling_property():
    class Probe:
        @property
        def state(self):
            """狀態描述。"""
            raise AssertionError("property getter must not execute")

        def run(self, count=2, *, mode="fast"):
            """執行操作。"""

    links = {name: f"https://example.invalid/{name}" for name in ("run", "state", "instance_flag")}
    methods, properties, unresolved = _extract_class_members(Probe, list(links), links)

    assert methods[0]["signature"] == "(self, count=2, *, mode='fast')"
    assert properties[0]["name"] == "state"
    assert unresolved[0]["name"] == "instance_flag"
