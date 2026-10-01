import json

with open(r"F:\Ming_python\ansys-unified-mcp\.agents\teamwork\explorer_survey_2\detailed_audit.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"總共找到 {len(data)} 個 SKILL.md")
print("=" * 60)

# 1. 檢查 Frontmatter 有效性
invalid_fm = [d for d in data if not d["has_fm"] or not d["fm_valid"]]
print(f"1. YAML frontmatter 無效或缺失: {len(invalid_fm)} 個")
for d in invalid_fm:
    print(f"   - {d['rel_path']}: error={d['fm_parse_error']}")

# 2. 檢查 name 欄位
no_name = [d for d in data if not d["name"]]
print(f"\n2. 缺少 name 欄位: {len(no_name)} 個")

not_kebab = [d for d in data if d["name"] and not d["is_kebab"]]
print(f"\n3. name 非 kebab-case: {len(not_kebab)} 個")
for d in not_kebab:
    print(f"   - {d['rel_path']}: name={d['name']}")

not_matching_folder = [d for d in data if d["name"] and not d["name_matches_folder"]]
print(f"\n4. name 與所在資料夾名稱不一致: {len(not_matching_folder)} 個")
for d in not_matching_folder:
    print(f"   - {d['rel_path']}: name='{d['name']}' vs folder='{d['folder_name']}'")

# 5. 檢查 description 欄位
no_desc = [d for d in data if not d["has_description"]]
print(f"\n5. 缺少 description 欄位: {len(no_desc)} 個")

# 6. 行數大於 500 行
over_500 = [d for d in data if d["line_count"] > 500]
print(f"\n6. 行數 > 500 行的 SKILL.md: {len(over_500)} 個")
for d in over_500:
    print(f"   - {d['rel_path']}: {d['line_count']} 行")

# 7. 行數介於 100~500 行
between_100_500 = [d for d in data if 100 <= d["line_count"] <= 500]
print(f"\n7. 行數介於 100~500 行的 SKILL.md: {len(between_100_500)} 個")
for d in between_100_500:
    print(f"   - {d['rel_path']}: {d['line_count']} 行")

# 8. 目錄結構檢查：reference (單數) vs references (複數)
has_singular_ref = [d for d in data if d["has_reference_singular"]]
has_plural_ref = [d for d in data if d["has_references"]]
print(f"\n8. 目錄結構規範:")
print(f"   - 使用 reference (單數) 的技能: {len(has_singular_ref)} 個")
print(f"   - 使用 references (標準複數) 的技能: {len(has_plural_ref)} 個")

# 9. 缺少 scripts 目錄的技能
no_scripts = [d for d in data if not d["has_scripts"]]
print(f"\n9. 缺少 scripts/ 目錄: {len(no_scripts)} 個")
for d in no_scripts:
    print(f"   - {d['rel_path']}")

# 10. 資料夾中包含非標準散落檔案
extra_files = [d for d in data if len([f for f in d["child_files"] if f.lower() != "skill.md"]) > 0]
print(f"\n10. 技能根目錄包含額外散落檔案: {len(extra_files)} 個")
for d in extra_files:
    extras = [f for f in d["child_files"] if f.lower() != "skill.md"]
    print(f"   - {d['rel_folder']}: {extras}")
