"""
腳本 API 靜態校驗器單元測試
"""
import pytest
from ansys_unified_mcp.analytics.apikb.validate import validate_script, extract_accessed_attributes

def test_extract_attributes():
    code = """
model = ExtAPI.DataModel.Project.Model
mesh = model.Mesh
mesh.ElementSize = 2.5
mesh.GenerateMesh()
"""
    attrs = extract_accessed_attributes(code)
    assert "ElementSize" in attrs
    assert "GenerateMesh" in attrs
    assert "Mesh" in attrs

def test_validate_valid_script():
    valid_script = """
analysis = ExtAPI.DataModel.Project.Model.Analyses[0]
fixed = analysis.AddFixedSupport()
eqv = analysis.Solution.AddEquivalentStress()
eqv.EvaluateAllResults()
val = eqv.Maximum.Value
"""
    res = validate_script(valid_script, "mechanical")
    assert res["valid"] is True
    assert res["error_count"] == 0

def test_validate_hallucinated_script():
    bad_script = """
analysis = ExtAPI.DataModel.Project.Model.Analyses[0]
fixed = analysis.AddNonExistentSupportFeature()
val = eqv.Maximum.Val
"""
    res = validate_script(bad_script, "mechanical")
    assert res["valid"] is False
    assert res["error_count"] >= 1
    err_names = [e["attribute"] for e in res["errors"]]
    assert "Val" in err_names or "AddNonExistentSupportFeature" in err_names
    # 檢查是否有給出建議
    val_err = next((e for e in res["errors"] if e["attribute"] == "Val"), None)
    if val_err:
        assert "Value" in val_err["suggestions"]
