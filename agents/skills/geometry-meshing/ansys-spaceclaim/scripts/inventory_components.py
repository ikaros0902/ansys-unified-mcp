import json
import traceback

result = {}
try:
    root = GetRootPart()
    raw_terms = argsDict.get("name_contains", "")
    terms = [term.strip().upper() for term in raw_terms.split(",") if term.strip()]
    raw_limit = argsDict.get("max_results", "500")
    limit = int(raw_limit)
    if limit < 1 or limit > 5000:
        raise Exception("max_results must be between 1 and 5000")

    matches = []
    total = [0]

    def walk(part, parent_path):
        for component in part.Components:
            name = component.GetName()
            path = parent_path + [name]
            upper_name = name.upper()
            matched = not terms
            for term in terms:
                if term in upper_name:
                    matched = True
                    break
            if matched:
                total[0] += 1
                if len(matches) < limit:
                    matches.append({
                        "name": name,
                        "path": path,
                        "bodies": component.GetAllBodies().Count,
                        "children": component.Content.Components.Count
                    })
            walk(component.Content, path)

    walk(root, [])
    result["matches"] = json.dumps(matches)
    result["match_count"] = str(total[0])
    result["returned_count"] = str(len(matches))
    result["truncated"] = str(total[0] > len(matches))
    result["root_name"] = root.GetName()
    result["root_bodies"] = str(root.GetAllBodies().Count)
except Exception:
    result["error"] = traceback.format_exc()
