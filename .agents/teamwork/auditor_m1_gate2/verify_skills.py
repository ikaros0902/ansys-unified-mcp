from pathlib import Path
import re

skills_dir = Path("skills")
mismatches = []
checked = 0
for d in sorted(skills_dir.iterdir()):
    if d.is_dir() and not d.name.startswith("."):
        skill_file = d / "SKILL.md"
        if skill_file.exists():
            checked += 1
            txt = skill_file.read_text(encoding="utf-8")
            m = re.search(r"^name:\s*['\"]?([a-zA-Z0-9_-]+)['\"]?", txt, re.MULTILINE)
            if not m:
                mismatches.append(f"{d.name}: No name in YAML frontmatter")
            elif m.group(1) != d.name:
                mismatches.append(f"{d.name} != {m.group(1)}")

print(f"Total skills checked: {checked}")
if mismatches:
    print("Mismatches found:", mismatches)
    exit(1)
else:
    print("ALL SKILLS FOLDER NAMES MATCH SKILL.MD NAME ATTRIBUTE: 100% OK")
    exit(0)
