from scripts.api_extraction.extract_primemesh_api import _extract_client_members


def test_client_member_extraction_is_static_and_excludes_inherited_members():
    class Parent:
        def inherited(self):
            """繼承方法。"""

    class Client(Parent):
        @property
        def model(self):
            """用戶端模型。"""
            raise AssertionError("property getter must not execute")

        def exit(self):
            """關閉用戶端。"""

    methods, properties = _extract_client_members(Client)

    assert [item["name"] for item in methods] == ["exit"]
    assert [item["name"] for item in properties] == ["model"]
