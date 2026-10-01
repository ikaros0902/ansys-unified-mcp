import os
import re
import yaml
import json

skills_dir = r"F:\Ming_python\ansys-unified-mcp\skills"

results = []

for root, dirs, files in os.walk(skills_dir):
    if ".zvec-grep" in root:
        continue
    for f in files:
        if f.lower() == "skill.md":
            p = os.path.join(root, f)
            rel_path = os.path.relpath(p, skills_dir).replace("\\", "/")
            folder_path = os.path.dirname(p)
            rel_folder = os.path.relpath(folder_path, skills_dir).replace("\\", "/")
            folder_name = os.path.basename(folder_path)
            
            with open(p, 'r', encoding='utf-8', errors='replace') as fp:
                raw_text = fp.read()
                lines = raw_text.splitlines()
                line_count = len(lines)
            
            # Extract frontmatter
            has_fm = False
            fm_text = ""
            fm_valid = False
            fm_data = {}
            fm_parse_error = None
            
            fm_match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n", raw_text, re.DOTALL)
            if fm_match:
                has_fm = True
                fm_text = fm_match.group(1)
                try:
                    loaded = yaml.safe_load(fm_text)
                    if isinstance(loaded, dict):
                        fm_valid = True
                        fm_data = loaded
                    else:
                        fm_parse_error = f"YAML is not a dict, got {type(loaded)}"
                except Exception as e:
                    fm_parse_error = str(e)
            
            name = fm_data.get("name") if fm_valid else None
            desc = fm_data.get("description") if fm_valid else None
            
            # Check name rules
            is_kebab = False
            name_matches_folder = False
            if name:
                name_str = str(name)
                is_kebab = bool(re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name_str))
                name_matches_folder = (name_str == folder_name)
            
            # Check subdirectories in current folder
            child_dirs = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
            child_files = [cf for cf in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, cf))]
            
            has_scripts = "scripts" in child_dirs
            has_references = "references" in child_dirs
            has_reference_singular = "reference" in child_dirs
            
            # Count code block lines in body
            body_text = raw_text[fm_match.end():] if fm_match else raw_text
            code_blocks = re.findall(r"```([a-zA-Z0-9_\-\+]*)\r?\n(.*?)```", body_text, re.DOTALL)
            code_block_count = len(code_blocks)
            code_block_lines = sum(len(c.splitlines()) for _, c in code_blocks)
            
            results.append({
                "rel_path": rel_path,
                "rel_folder": rel_folder,
                "folder_name": folder_name,
                "line_count": line_count,
                "has_fm": has_fm,
                "fm_valid": fm_valid,
                "fm_parse_error": fm_parse_error,
                "name": name,
                "is_kebab": is_kebab,
                "name_matches_folder": name_matches_folder,
                "has_description": bool(desc and str(desc).strip()),
                "description_len": len(str(desc)) if desc else 0,
                "description": desc,
                "child_dirs": child_dirs,
                "child_files": child_files,
                "has_scripts": has_scripts,
                "has_references": has_references,
                "has_reference_singular": has_reference_singular,
                "code_block_count": code_block_count,
                "code_block_lines": code_block_lines
            })

with open(r"F:\Ming_python\ansys-unified-mcp\.agents\teamwork\explorer_survey_2\detailed_audit.json", 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Audited {len(results)} SKILL.md files.")
