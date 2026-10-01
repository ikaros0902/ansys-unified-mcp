# -*- coding: utf-8 -*-
"""Milestone 2 自檢驗證腳本"""
import os
import re
import sys
from pathlib import Path
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

skills_root = Path(r"F:\Ming_python\ansys-unified-mcp\skills")
errors = []

# 1. 檢驗資料夾名稱與 SKILL.md name 一致性及 description
skills_count = 0
for skill_md in skills_root.rglob("SKILL.md"):
    skills_count += 1
    folder_name = skill_md.parent.name
    content = skill_md.read_text(encoding="utf-8")
    parts = content.split("---")
    if len(parts) < 3:
        errors.append(f"{skill_md}: 缺少 YAML frontmatter")
        continue
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        errors.append(f"{skill_md}: YAML frontmatter 格式不正確")
        continue
    name = data.get("name")
    desc = data.get("description")
    if name != folder_name:
        errors.append(f"{skill_md}: name '{name}' != folder '{folder_name}'")
    if not desc or not str(desc).strip():
        errors.append(f"{skill_md}: description 為空")

print(f"[檢驗 1] 掃描 {skills_count} 個 SKILL.md，名稱與資料夾 100% 一致性檢查完成。")

# 2. 檢驗 skills/ 下無任何單數 reference 目錄
single_refs = [str(p.relative_to(skills_root)) for p in skills_root.rglob("reference") if p.is_dir()]
if single_refs:
    errors.append(f"殘留單數 reference 目錄: {single_refs}")
else:
    print("[檢驗 2] skills/ 下完全無單數 reference 目錄殘留。")

# 3. 檢驗死鏈
link_pattern = re.compile(r"\]\((?!https?://|#)([^)]+)\)")
dead_links = []
total_links = 0
for skill_md in skills_root.rglob("SKILL.md"):
    content = skill_md.read_text(encoding="utf-8", errors="replace")
    for rel_target in link_pattern.findall(content):
        target = rel_target.split("#", 1)[0].strip()
        if not target:
            continue
        total_links += 1
        if not (skill_md.parent / target).exists():
            dead_links.append(f"{skill_md.relative_to(skills_root)} => {target}")
if dead_links:
    errors.append(f"發現死鏈: {dead_links}")
else:
    print(f"[檢驗 3] 所有 SKILL.md 內部相對超連結 100% 有效（共檢驗 {total_links} 處連結）。")

# 4. 檢驗 ansys-spaceclaim-modeling 已刪除
if (skills_root / "ansys-spaceclaim-modeling").exists():
    errors.append("skills/ansys-spaceclaim-modeling 仍然存在")
else:
    print("[檢驗 4] 冗餘技能 ansys-spaceclaim-modeling 已成功移除。")

# 5. 檢驗 convert.py 已移至 scripts/
if (skills_root / "pdf-to-md" / "convert.py").exists():
    errors.append("pdf-to-md/convert.py 仍存在於根目錄")
if not (skills_root / "pdf-to-md" / "scripts" / "convert.py").exists():
    errors.append("pdf-to-md/scripts/convert.py 不存在")
if not errors:
    print("[檢驗 5] pdf-to-md 腳本已正確歸位至 scripts/convert.py。")

# 6. 檢驗 SKILL.md 行數 <= 200 行
over_lines = []
for skill_md in skills_root.rglob("SKILL.md"):
    lines = len(skill_md.read_text(encoding="utf-8").splitlines())
    if lines > 200:
        over_lines.append(f"{skill_md.relative_to(skills_root)}: {lines} 行")
if over_lines:
    errors.append(f"SKILL.md 行數超標: {over_lines}")
else:
    print("[檢驗 6] 所有 SKILL.md 行數均符合 <= 200 行規範。")

print("\n=== 總結 ===")
if errors:
    print(f"❌ 發現 {len(errors)} 個問題:")
    for err in errors:
        print("  -", err)
    sys.exit(1)
else:
    print("✅ 所有客觀驗收指標 100% 通過！")
