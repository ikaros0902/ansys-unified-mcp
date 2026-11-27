import ast
from pathlib import Path
import re
import runpy

import pytest

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "docs" / "examples" / "pcb_warpage"
SKILL_DIR = ROOT / "agents" / "skills" / "materials-reliability" / "pcb-warpage-analysis"
CANONICAL = SKILL_DIR / "scripts"
ODB_WORKFLOW = CANONICAL / "odb_workflow"


def _parse_frontmatter(markdown_text: str) -> dict[str, str]:
    """解析 SKILL.md 開頭之 YAML Frontmatter（必要時降級為鍵值解析）。"""
    match = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", markdown_text, re.DOTALL)
    assert match is not None, "SKILL.md 缺少 YAML Frontmatter 區塊"
    raw_fm = match.group(1)

    if yaml is not None:
        loaded = yaml.safe_load(raw_fm)
        if isinstance(loaded, dict):
            return {k: str(v) if v is not None else "" for k, v in loaded.items()}

    data: dict[str, str] = {}
    for line in raw_fm.splitlines():
        kv = re.match(r"^([a-zA-Z0-9_-]+)\s*:\s*(.*)$", line)
        if kv:
            data[kv.group(1).strip()] = kv.group(2).strip().strip("\"'")
    return data


def _extract_relative_markdown_links(markdown_text: str) -> list[str]:
    """萃取 Markdown 中所有相對路徑連結目標（略過程式碼區塊與外部 URL / 純錨點）。"""
    cleaned = re.sub(r"```.*?```", "", markdown_text, flags=re.DOTALL)
    cleaned = re.sub(r"`[^`\n]+`", "", cleaned)
    targets: list[str] = []
    for raw_target in re.findall(r"\[[^\]]+\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", cleaned):
        if raw_target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        rel_path = raw_target.split("#", 1)[0].strip()
        if rel_path:
            targets.append(rel_path)
    return targets


@pytest.mark.parametrize(
    "name",
    [
        "01_build_pcb_geometry.py",
        "02_calculate_rom_materials.py",
        "run_full_warpage_workflow.py",
    ],
)
def test_example_entrypoint_delegates_to_canonical_skill_script(name, monkeypatch):
    calls = []
    monkeypatch.setattr(runpy, "run_path", lambda path, run_name: calls.append((path, run_name)))
    wrapper = EXAMPLES / name
    namespace = {"__name__": "__main__", "__file__": str(wrapper)}

    exec(compile(wrapper.read_text(encoding="utf-8"), str(wrapper), "exec"), namespace)

    assert calls == [(str(CANONICAL / name), "__main__")]


def test_canonical_workflow_defines_its_script_directory_without_running_workflow(monkeypatch):
    monkeypatch.delenv("PCB_STACKUP_DIR", raising=False)
    namespace = runpy.run_path(
        str(CANONICAL / "run_full_warpage_workflow.py"),
        run_name="pcb_warpage_import_check",
    )

    assert namespace["SCRIPT_DIR"] == str(CANONICAL)
    assert namespace["DEFAULT_FOLDER"] == namespace["SCRIPT_DIR"]


def test_skill_md_intake_gate_and_frontmatter_constraints():
    """驗證 SKILL.md 具備 Intake Gate、行數 <= 150 且 description 單字數 <= 120。"""
    skill_md = SKILL_DIR / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")

    assert "Intake Gate" in content
    assert len(content.splitlines()) <= 150

    frontmatter = _parse_frontmatter(content)
    assert frontmatter.get("name") == "pcb-warpage-analysis"
    description = frontmatter.get("description", "").strip()
    assert description
    assert len(description.split()) <= 120


def test_track1_and_track2_key_files_exist_and_pass_ast_parse():
    """驗證 Track 1 與 Track 2 關鍵檔案皆存在，且 Python 腳本均通過 ast.parse。

    注意：`03_setup_mechanical_bc_and_solution.py` 與 `Mech_py_EquivalentMaterial_v6.py`
    屬於 ANSYS Mechanical 內嵌腳本，因此僅執行 `ast.parse` 語法檢查，不於 repo venv 匯入。
    """
    track1_scripts = [
        CANONICAL / "01_build_pcb_geometry.py",
        CANONICAL / "02_calculate_rom_materials.py",
        CANONICAL / "03_setup_mechanical_bc_and_solution.py",
        CANONICAL / "run_full_warpage_workflow.py",
    ]
    wrapper_and_manifest_files = [
        CANONICAL / "level_wrapper.py",
        CANONICAL / "verify_upstream_snapshot.py",
        CANONICAL / "UPSTREAM_MANIFEST.json",
    ]
    track2_key_files = [
        ODB_WORKFLOW / "run_odb_tool.py",
        ODB_WORKFLOW / "requirements.txt",
        ODB_WORKFLOW / "setup_env.ps1",
        ODB_WORKFLOW / "odbtool" / "__init__.py",
        ODB_WORKFLOW / "1_Scripts" / "LayerBuilder_pyansys.py",
        ODB_WORKFLOW / "1_Scripts" / "level_bga_shadow.py",
        ODB_WORKFLOW / "1_Scripts" / "Mech_py_EquivalentMaterial_v6.py",
        ODB_WORKFLOW / "1_Scripts" / "Compare_TraceMapping_Dat.py",
        ODB_WORKFLOW / "1_Scripts" / "README_TraceMapping.md",
        ODB_WORKFLOW / "3_materials" / "Update_PCB_Material_Library.py",
        ODB_WORKFLOW / "3_materials" / "README_Material_Library.md",
        ODB_WORKFLOW / "4_config" / "project_config.template.json",
    ]

    for path in track1_scripts + wrapper_and_manifest_files + track2_key_files:
        assert path.is_file(), f"缺少必要檔案: {path}"

    # 僅做語法解析之 Mechanical 內嵌腳本清單（不於 repo venv 匯入）
    syntax_only_embedded_scripts = {
        CANONICAL / "03_setup_mechanical_bc_and_solution.py",
        ODB_WORKFLOW / "1_Scripts" / "Mech_py_EquivalentMaterial_v6.py",
    }

    py_targets = sorted(
        set(track1_scripts)
        | {CANONICAL / "level_wrapper.py", CANONICAL / "verify_upstream_snapshot.py"}
        | set(ODB_WORKFLOW.rglob("*.py"))
    )
    assert syntax_only_embedded_scripts.issubset(set(py_targets))

    for py_file in py_targets:
        source = py_file.read_text(encoding="utf-8-sig")
        ast.parse(source, filename=str(py_file))


@pytest.mark.parametrize(
    "md_rel_path",
    [
        "SKILL.md",
        "references/odb_workflow/README.md",
        "references/odb_workflow/mcp_hybrid_checkpoint.md",
    ],
)
def test_self_authored_markdown_relative_links_exist(md_rel_path):
    """驗證自寫 Markdown 檔案之相對連結目標皆存在（不掃描上游快照 docs/）。"""
    md_file = SKILL_DIR / md_rel_path
    assert md_file.is_file(), f"找不到 Markdown 檔案: {md_file}"

    links = _extract_relative_markdown_links(md_file.read_text(encoding="utf-8"))
    for rel_target in links:
        resolved = (md_file.parent / rel_target).resolve()
        assert resolved.exists(), f"{md_rel_path} 中的連結目標不存在: {rel_target} -> {resolved}"

