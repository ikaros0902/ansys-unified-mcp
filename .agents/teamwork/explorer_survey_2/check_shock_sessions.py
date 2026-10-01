import os
import yaml

shock_dir = r"F:\Ming_python\ansys-unified-mcp\skills\shock-analysis-workflow"
sessions = sorted([d for d in os.listdir(shock_dir) if os.path.isdir(os.path.join(shock_dir, d)) and d.startswith("0")])

for s in sessions:
    skill_file = os.path.join(shock_dir, s, "SKILL.md")
    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()
    # parse frontmatter
    fm = content.split("---")[1]
    data = yaml.safe_load(fm)
    print(f"Folder: {s:25s} | name: {data.get('name'):35s} | match? {s == data.get('name')}")
