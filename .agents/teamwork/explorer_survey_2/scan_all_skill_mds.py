import os
import re
import yaml
import json

skills_dir = r"F:\Ming_python\ansys-unified-mcp\skills"

skill_mds = []
for root, dirs, files in os.walk(skills_dir):
    if ".zvec-grep" in root:
        continue
    for f in files:
        if f.lower() == "skill.md":
            p = os.path.join(root, f)
            rel_dir = os.path.relpath(root, skills_dir).replace("\\", "/")
            folder_name = os.path.basename(root)
            with open(p, 'r', encoding='utf-8', errors='replace') as fp:
                content = fp.read()
                lines = content.splitlines()
                line_count = len(lines)
            
            fm_match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n", content, re.DOTALL)
            has_fm = bool(fm_match)
            yaml_valid = False
            parsed = {}
            if fm_match:
                try:
                    parsed = yaml.safe_load(fm_match.group(1))
                    if isinstance(parsed, dict):
                        yaml_valid = True
                except Exception as e:
                    pass
            
            name = parsed.get("name") if yaml_valid else None
            desc = parsed.get("description") if yaml_valid else None
            name_kebab = bool(re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", str(name))) if name else False
            name_matches = (str(name) == folder_name) if name else False
            
            skill_mds.append({
                "rel_dir": rel_dir,
                "folder_name": folder_name,
                "file_path": os.path.relpath(p, skills_dir).replace("\\", "/"),
                "lines": line_count,
                "has_fm": has_fm,
                "yaml_valid": yaml_valid,
                "name": name,
                "name_kebab": name_kebab,
                "name_matches": name_matches,
                "description": desc
            })

skill_mds.sort(key=lambda x: x["file_path"])

out_path = r"F:\Ming_python\ansys-unified-mcp\.agents\teamwork\explorer_survey_2\all_skill_mds.json"
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(skill_mds, f, ensure_ascii=False, indent=2)

print(f"Total SKILL.md found: {len(skill_mds)}")
for s in skill_mds:
    status = "OK" if (s["has_fm"] and s["yaml_valid"] and s["name_kebab"] and s["name_matches"] and s["description"]) else "WARN"
    print(f"[{status}] {s['file_path']:50s} | lines: {s['lines']:3d} | name: {str(s['name']):30s} | match: {s['name_matches']}")
