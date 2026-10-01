import os
import json

skills_dir = r"F:\Ming_python\ansys-unified-mcp\skills"

all_md_files = []
for root, dirs, files in os.walk(skills_dir):
    if ".zvec-grep" in root:
        continue
    for f in files:
        if f.endswith(".md"):
            p = os.path.join(root, f)
            rel_path = os.path.relpath(p, skills_dir)
            with open(p, 'r', encoding='utf-8', errors='replace') as fp:
                lines = fp.readlines()
                line_count = len(lines)
            all_md_files.append({
                "rel_path": rel_path.replace("\\", "/"),
                "lines": line_count,
                "bytes": os.path.getsize(p)
            })

all_md_files.sort(key=lambda x: x["lines"], reverse=True)

out_path = r"F:\Ming_python\ansys-unified-mcp\.agents\teamwork\explorer_survey_2\all_md_files.json"
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(all_md_files, f, ensure_ascii=False, indent=2)

print(f"Total MD files: {len(all_md_files)}")
for item in all_md_files[:20]:
    print(f"{item['lines']:5d} lines | {item['rel_path']}")
