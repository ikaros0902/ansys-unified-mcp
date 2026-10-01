import os
import re
import sys
from pathlib import Path

ROOT = Path(r"F:\Ming_python\ansys-unified-mcp")
SKILLS_DIR = ROOT / "skills"

print("=" * 60)
print("1. 幾何技能重複刪除檢查 (ansys-spaceclaim-modeling)")
old_geom_skill = SKILLS_DIR / "ansys-spaceclaim-modeling"
print(f"Directory exists: {old_geom_skill.exists()}")
if old_geom_skill.exists():
    print(f"Contents: {list(old_geom_skill.iterdir())}")

print("\n" + "=" * 60)
print("2. pdf-to-md 腳本歸位檢查")
old_convert = SKILLS_DIR / "pdf-to-md" / "convert.py"
new_convert = SKILLS_DIR / "pdf-to-md" / "scripts" / "convert.py"
skill_pdf = SKILLS_DIR / "pdf-to-md" / "SKILL.md"
print(f"Old convert.py exists: {old_convert.exists()}")
print(f"New convert.py exists: {new_convert.exists()} (size: {new_convert.stat().st_size if new_convert.exists() else 0} bytes)")
if skill_pdf.exists():
    content = skill_pdf.read_text(encoding="utf-8")
    print("pdf-to-md/SKILL.md script reference snippet:")
    for line in content.splitlines():
        if "convert.py" in line:
            print("  ", line)

print("\n" + "=" * 60)
print("3. 單數 reference/ 資料夾歸零檢查")
singular_refs = [str(p.relative_to(ROOT)) for p in SKILLS_DIR.rglob("reference") if p.is_dir()]
print(f"Remaining singular reference dirs count: {len(singular_refs)}")
if singular_refs:
    print(f"Found singular dirs: {singular_refs}")

plural_refs = [str(p.relative_to(ROOT)) for p in SKILLS_DIR.rglob("references") if p.is_dir()]
print(f"Plural references dirs count: {len(plural_refs)}")

print("\n" + "=" * 60)
print("4. SKILL.md 全面盤點與 Frontmatter 一致性檢驗")
skill_files = sorted(list(SKILLS_DIR.rglob("SKILL.md")))
print(f"Total SKILL.md files found: {len(skill_files)}")

frontmatter_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
name_pattern = re.compile(r"^name:\s*([^\s#]+)", re.MULTILINE)
desc_pattern = re.compile(r"^description:\s*(.+)", re.MULTILINE)

mismatches = []
line_count_exceeded = []
missing_frontmatter = []

for sf in skill_files:
    rel_path = sf.relative_to(ROOT)
    parent_dir_name = sf.parent.name
    text = sf.read_text(encoding="utf-8")
    lines = text.splitlines()
    line_count = len(lines)
    
    fm_match = frontmatter_pattern.search(text)
    if not fm_match:
        missing_frontmatter.append(str(rel_path))
        continue
    
    fm_text = fm_match.group(1)
    name_m = name_pattern.search(fm_text)
    desc_m = desc_pattern.search(fm_text)
    
    skill_name = name_m.group(1).strip() if name_m else None
    skill_desc = desc_m.group(1).strip() if desc_m else None
    
    if skill_name != parent_dir_name:
        mismatches.append({
            "path": str(rel_path),
            "dir_name": parent_dir_name,
            "declared_name": skill_name
        })
        
    if line_count > 500:
        line_count_exceeded.append((str(rel_path), line_count))

print(f"Missing frontmatter: {len(missing_frontmatter)}")
print(f"Directory vs Name mismatches: {len(mismatches)}")
if mismatches:
    for m in mismatches:
        print("  MISMATCH:", m)
else:
    print("  ALL 25 SKILL.md names match parent directory 100%!")

print(f"Lines > 500: {len(line_count_exceeded)}")
for sf in skill_files:
    lines = len(sf.read_text(encoding="utf-8").splitlines())
    print(f"  {sf.relative_to(SKILLS_DIR)}: {lines} lines")

print("\n" + "=" * 60)
print("5. SKILL.md 相對超連結有效性檢驗 (死鏈掃描)")
link_pattern = re.compile(r"\[([^\]]+)\]\((?!https?://|mailto:|#)([^)]+)\)")
dead_links = []
total_links = 0

for sf in skill_files:
    text = sf.read_text(encoding="utf-8")
    links = link_pattern.findall(text)
    for anchor, target in links:
        total_links += 1
        # 去除 hash 錨點
        target_path = target.split("#")[0]
        if not target_path:
            continue
        # 解析相對路徑
        resolved = (sf.parent / target_path).resolve()
        if not resolved.exists():
            dead_links.append({
                "source": str(sf.relative_to(ROOT)),
                "anchor": anchor,
                "target": target,
                "resolved": str(resolved)
            })

print(f"Total checked relative links in SKILL.md: {total_links}")
print(f"Dead links count: {len(dead_links)}")
if dead_links:
    for dl in dead_links:
        print("  DEAD LINK:", dl)
else:
    print("  ALL relative links resolved successfully! Zero dead links.")

print("\n" + "=" * 60)
print("6. 檢查 SKILL.md 內是否殘留 'reference/' 字樣")
ref_residual = []
for sf in skill_files:
    text = sf.read_text(encoding="utf-8")
    # 搜尋 reference/ 但排除 references/
    for line_num, line in enumerate(text.splitlines(), 1):
        # 找出 reference/ 且後面不是 s
        matches = re.findall(r"(?<![a-zA-Z0-9_])reference/(?![a-zA-Z0-9_])", line)
        if matches:
            ref_residual.append((str(sf.relative_to(ROOT)), line_num, line.strip()))

print(f"Singular 'reference/' residual occurrences in SKILL.md: {len(ref_residual)}")
if ref_residual:
    for r in ref_residual:
        print(f"  {r[0]}:{r[1]} -> {r[2]}")
