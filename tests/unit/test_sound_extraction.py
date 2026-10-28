from scripts.api_extraction.extract_sound_api import _extract_class_members


def test_class_member_extraction_is_static_and_keeps_direct_members():
    class Parent:
        def inherited(self):
            """父類別方法。"""

    class SoundComposer(Parent):
        @property
        def name(self):
            """曲目名稱。"""
            raise AssertionError("property getter must not execute")

        def process(self):
            """處理音訊。"""

    methods, properties = _extract_class_members(SoundComposer)

    assert [item["name"] for item in methods] == ["process"]
    assert [item["name"] for item in properties] == ["name"]
