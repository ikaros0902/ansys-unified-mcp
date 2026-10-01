import os
import sys
import re
import yaml
from pathlib import Path

def run_audit():
    project_root = Path(__file__).resolve().parents[3]
    skills_root = project_root / 'skills'
    print(f"Project root: {project_root}")
    print(f"Skills root: {skills_root}")

    print("\n=== 1. 檢驗 SKILL.md 資料夾與 name 逐字吻合 ===")
    skill_files = sorted(skills_root.rglob('SKILL.md'))
    print(f"找到 {len(skill_files)} 個 SKILL.md 檔案：")
    name_mismatches = []
    shock_subdirs = []
    for sf in skill_files:
        rel_path = sf.relative_to(project_root)
        folder_name = sf.parent.name
        content = sf.read_text(encoding='utf-8')
        fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not fm_match:
            name_mismatches.append((str(rel_path), folder_name, 'NO_FRONTMATTER'))
            continue
        fm_data = yaml.safe_load(fm_match.group(1)) or {}
        name = fm_data.get('name')
        desc = fm_data.get('description', '')
        line_count = len(content.splitlines())
        if 'shock-analysis-workflow' in str(rel_path):
            shock_subdirs.append((folder_name, name))
        print(f"  [{folder_name}] (lines: {line_count}) -> name: {name} | desc_len: {len(desc)}")
        if folder_name != name:
            name_mismatches.append((str(rel_path), folder_name, name))

    print(f"\n名稱不吻合數量: {len(name_mismatches)}")
    for m in name_mismatches:
        print(f"  [MISMATCH] {m}")

    print("\n--- 特別檢視 shock-analysis-workflow 8 個子目錄 ---")
    expected_shock = [
        '01-material-assignment',
        '02-contact-creation',
        '03-mesh-tuning',
        '04-connection-rm',
        '05-section-assignment',
        '06-constraint-load',
        '07-solve-monitor',
        '08-post-process-report',
    ]
    shock_names_found = dict(shock_subdirs)
    all_shock_match = True
    for exp in expected_shock:
        actual = shock_names_found.get(exp)
        matches = (exp == actual)
        if not matches:
            all_shock_match = False
        print(f"  {exp:<25} => actual name: {actual:<25} [{'PASS' if matches else 'FAIL'}]")

    print("\n=== 2. 檢驗 skills/ 下是否殘留單數 reference/ 目錄 ===")
    remaining_singular = []
    references_plural = []
    for root, dirs, files in os.walk(skills_root):
        for d in dirs:
            if d.lower() == 'reference':
                remaining_singular.append(os.path.join(root, d))
            elif d.lower() == 'references':
                references_plural.append(os.path.join(root, d))

    print(f"單數 reference 目錄殘留數: {len(remaining_singular)}")
    for r in remaining_singular:
        print(f"  [STILL_EXISTS] {r}")
    print(f"複數 references 目錄數量: {len(references_plural)}")

    print("\n=== 3. 檢驗 Markdown 檔案中指向 reference/ 的路徑與死鏈 ===")
    ref_pattern = re.compile(r'(\b[\w\-./\\]*reference[/\\][\w\-./\\]*)', re.IGNORECASE)
    md_files = sorted(skills_root.rglob('*.md'))
    markdown_ref_matches = []
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    dead_links = []

    for md in md_files:
        content = md.read_text(encoding='utf-8')
        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            for m in ref_pattern.finditer(line):
                val = m.group(1)
                # 排除複數 references
                if 'references' in val.lower():
                    continue
                markdown_ref_matches.append((str(md.relative_to(project_root)), idx, line.strip()))

        # 死鏈檢查
        for lm in link_pattern.finditer(content):
            target = lm.group(2).strip()
            # 排除外部 url、錨點與 mailto
            if target.startswith('http://') or target.startswith('https://') or target.startswith('#') or target.startswith('mailto:'):
                continue
            clean_target = target.split('#')[0].split('?')[0]
            if not clean_target:
                continue
            resolved = (md.parent / clean_target).resolve()
            if not resolved.exists():
                dead_links.append((str(md.relative_to(project_root)), target, str(resolved)))

    print(f"Markdown 內殘留單數 reference/ 引用數: {len(markdown_ref_matches)}")
    for m in markdown_ref_matches:
        print(f"  [REF_REF] {m[0]}:{m[1]} -> {m[2]}")
    print(f"死鏈數量: {len(dead_links)}")
    for dl in dead_links:
        print(f"  [DEAD_LINK] {dl[0]} -> {dl[1]} (resolved: {dl[2]})")

    print("\n=== 4. 檢驗重複的 skills/ansys-spaceclaim-modeling/ 是否已徹底刪除 ===")
    redundant_skill = skills_root / 'ansys-spaceclaim-modeling'
    print(f"skills/ansys-spaceclaim-modeling 是否存在: {redundant_skill.exists()}")

    print("\n=== 5. 檢驗 pdf-to-md/scripts/convert.py 與 skills/README.md ===")
    convert_py = skills_root / 'pdf-to-md' / 'scripts' / 'convert.py'
    old_convert_py = skills_root / 'pdf-to-md' / 'convert.py'
    print(f"pdf-to-md/scripts/convert.py 是否存在: {convert_py.exists()}")
    print(f"舊位置 pdf-to-md/convert.py 是否存在: {old_convert_py.exists()}")

    readme_file = skills_root / 'README.md'
    readme_exists = readme_file.exists()
    print(f"skills/README.md 是否存在: {readme_exists}")
    readme_table_valid = False
    core_skills_indexed = []
    if readme_exists:
        readme_content = readme_file.read_text(encoding='utf-8')
        # Check if table syntax is valid and phase_gate is gone
        has_phase_gate = 'phase_gate' in readme_content
        print(f"README.md 是否殘留 phase_gate: {has_phase_gate}")
        # Check ansys-mesh and ansys-spaceclaim-modeling in table
        has_ansys_mesh = 'ansys-mesh' in readme_content
        has_spaceclaim_modeling = 'ansys-spaceclaim-modeling' in readme_content
        print(f"README.md 包含 ansys-mesh: {has_ansys_mesh}")
        print(f"README.md 包含已刪除之 ansys-spaceclaim-modeling: {has_spaceclaim_modeling}")

if __name__ == '__main__':
    run_audit()
