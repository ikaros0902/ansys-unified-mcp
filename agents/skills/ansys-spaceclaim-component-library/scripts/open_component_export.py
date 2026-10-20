import json
import os
import traceback

result = {}
try:
    raw_path = argsDict.get("component_path", "")
    output_path = argsDict.get("output_path", "")
    path_parts = json.loads(raw_path)
    if not isinstance(path_parts, list) or not path_parts:
        raise Exception("component_path must be a non-empty JSON array of exact component names")
    if not all(isinstance(part, basestring) and part for part in path_parts):
        raise Exception("every component_path item must be a non-empty string")
    if not output_path or not os.path.isabs(output_path):
        raise Exception("output_path must be an absolute path")
    if os.path.splitext(output_path)[1].lower() not in [".step", ".stp"]:
        raise Exception("output_path must use a .step or .stp extension")
    if os.path.exists(output_path):
        raise Exception("output_path already exists; inspect it before replacing")

    source_root = GetRootPart()
    current_part = source_root
    component = None
    for segment in path_parts:
        candidates = [item for item in current_part.Components if item.GetName() == segment]
        if len(candidates) != 1:
            raise Exception("component path segment is missing or ambiguous: " + segment)
        component = candidates[0]
        current_part = component.Content

    expected_bodies = component.GetAllBodies().Count
    if expected_bodies <= 0:
        raise Exception("selected component contains no bodies")
    source_root_bodies = source_root.GetAllBodies().Count
    opened = ComponentHelper.OpenComponentDocument(ComponentSelection.Create(component), None)
    if not opened:
        raise Exception("SpaceClaim did not open the selected component document")
    actual_bodies = GetRootPart().GetAllBodies().Count
    if actual_bodies != expected_bodies:
        raise Exception("opened body count does not match the selected component")

    save_result = DocumentSave.Execute(output_path)
    if not os.path.isfile(output_path):
        raise Exception("save returned but output file was not created")
    size = os.path.getsize(output_path)
    if size <= 0:
        raise Exception("output file is empty")

    result["component_path"] = json.dumps(path_parts)
    result["source_root_bodies_before_open"] = str(source_root_bodies)
    result["expected_bodies"] = str(expected_bodies)
    result["opened_bodies"] = str(actual_bodies)
    result["open_result"] = str(opened)
    result["save_result"] = str(save_result)
    result["output_path"] = output_path
    result["output_bytes"] = str(size)
except Exception:
    result["error"] = traceback.format_exc()
