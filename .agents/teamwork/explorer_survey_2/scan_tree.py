import os
import json

skills_dir = r"F:\Ming_python\ansys-unified-mcp\skills"

tree = {}
for item in sorted(os.listdir(skills_dir)):
    if item.startswith('.'):
        continue
    item_path = os.path.join(skills_dir, item)
    if os.path.isdir(item_path):
        dir_contents = []
        for root, dirs, files in os.walk(item_path):
            if "__pycache__" in root:
                continue
            rel = os.path.relpath(root, item_path).replace("\\", "/")
            for f in files:
                f_rel = (rel + "/" + f) if rel != "." else f
                full_f = os.path.join(root, f)
                dir_contents.append({
                    "path": f_rel,
                    "size": os.path.getsize(full_f)
                })
        tree[item] = dir_contents

out_path = r"F:\Ming_python\ansys-unified-mcp\.agents\teamwork\explorer_survey_2\skills_file_tree.json"
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(tree, f, ensure_ascii=False, indent=2)

print(f"Scanned {len(tree)} skill directories.")
for k, v in tree.items():
    print(f"{k:30s}: {len(v)} files")
