import json

with open(r"F:\Ming_python\ansys-unified-mcp\.agents\teamwork\explorer_survey_2\skills_file_tree.json", 'r', encoding='utf-8') as f:
    tree = json.load(f)

for skill, files in tree.items():
    print(f"=== {skill} ({len(files)} files) ===")
    for f in files:
        print(f"  - {f['path']} ({f['size']} bytes)")
