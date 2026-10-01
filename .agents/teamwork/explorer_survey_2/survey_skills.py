import os
import re
import yaml
import json

skills_dir = r"F:\Ming_python\ansys-unified-mcp\skills"
items = [d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d)) and not d.startswith('.')]
items.sort()

results = []

for folder_name in items:
    folder_path = os.path.join(skills_dir, folder_name)
    skill_md_path = os.path.join(folder_path, "SKILL.md")
    
    subdirs = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
    has_scripts = "scripts" in subdirs
    has_references = "references" in subdirs
    has_reference_singular = "reference" in subdirs
    
    has_skill_md = os.path.isfile(skill_md_path)
    line_count = 0
    raw_frontmatter = ""
    parsed_yaml = {}
    yaml_valid = False
    has_frontmatter = False
    name_in_yaml = None
    desc_in_yaml = None
    name_kebab = False
    name_matches_folder = False
    has_code_blocks = False
    code_block_lines = 0
    large_code_blocks = []
    
    if has_skill_md:
        with open(skill_md_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            line_count = len(lines)
            content = "".join(lines)
        
        # Check YAML frontmatter
        fm_match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n", content, re.DOTALL)
        if fm_match:
            has_frontmatter = True
            raw_frontmatter = fm_match.group(1)
            try:
                parsed_yaml = yaml.safe_load(raw_frontmatter)
                if isinstance(parsed_yaml, dict):
                    yaml_valid = True
                    name_in_yaml = parsed_yaml.get("name")
                    desc_in_yaml = parsed_yaml.get("description")
                    if name_in_yaml is not None:
                        name_str = str(name_in_yaml)
                        name_kebab = bool(re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name_str))
                        name_matches_folder = (name_str == folder_name)
            except Exception as e:
                yaml_valid = False
        
        # Check code blocks inside SKILL.md
        code_blocks = re.findall(r"```([a-zA-Z0-9_\-\+]*)\r?\n(.*?)```", content, re.DOTALL)
        if code_blocks:
            has_code_blocks = True
            for lang, code in code_blocks:
                b_lines = len(code.splitlines())
                code_block_lines += b_lines
                if b_lines >= 15:
                    large_code_blocks.append({
                        "lang": lang,
                        "lines": b_lines,
                        "preview": code.splitlines()[:3]
                    })

    results.append({
        "folder": folder_name,
        "has_skill_md": has_skill_md,
        "line_count": line_count,
        "has_frontmatter": has_frontmatter,
        "yaml_valid": yaml_valid,
        "name_in_yaml": name_in_yaml,
        "name_kebab": name_kebab,
        "name_matches_folder": name_matches_folder,
        "desc_in_yaml": desc_in_yaml,
        "subdirs": subdirs,
        "has_scripts": has_scripts,
        "has_references": has_references,
        "has_reference_singular": has_reference_singular,
        "code_block_lines": code_block_lines,
        "large_code_blocks_count": len(large_code_blocks),
        "large_code_blocks": large_code_blocks
    })

out_path = r"F:\Ming_python\ansys-unified-mcp\.agents\teamwork\explorer_survey_2\skills_inventory.json"
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Successfully written {len(results)} items to {out_path}")
