from scripts.api_extraction.extract_fluent_api import FUNCTION_NAMES, _function_record


def test_function_record_does_not_call_target():
    def launch(*, mode="solver"):
        raise AssertionError("API target must not be called")

    assert FUNCTION_NAMES == ("connect_to_fluent", "launch_fluent")
    record = _function_record("launch_fluent", launch)
    assert record["signature"] == "(*, mode='solver')"
    assert record["sdk_source_path"] == record["signature_source_path"]
