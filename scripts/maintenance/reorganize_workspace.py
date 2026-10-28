"""歸位文件並以內容驗證去重；預設只輸出計畫，原件備份不納入版控。"""
from __future__ import annotations

import argparse
from collections import defaultdict
import filecmp
import hashlib
import json
from pathlib import Path
import re
import shutil
from urllib.parse import unquote, urlsplit


MOVES = {
    "docs/ARCHITECTURE.md": "docs/architecture/ARCHITECTURE.md",
    "docs/PCB_WARPAGE_AUTOMATION_LOG.md": "docs/examples/pcb_warpage/AUTOMATION_LOG.md",
    "docs/mesh_classification_heuristics.md": "docs/examples/mesh_debug/mesh_classification_heuristics.md",
    "docs/session_learnings_and_troubleshooting.md": "docs/maintenance/session_learnings_and_troubleshooting.md",
    "verification_report_stage5.json": "tests/evaluations/reports/verification_report_stage5.json",
}


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inside(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root.resolve()) or candidate == root.resolve():
        raise ValueError(f"路徑超出工作區：{relative}")
    return candidate


def copy_verified(source: Path, target: Path, expected: str) -> None:
    """以同目錄暫存檔及排他建立，避免中斷留下半份正式檔。"""
    import os
    import tempfile
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".relocate-", dir=target.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as out, source.open("rb") as stream:
            shutil.copyfileobj(stream, out)
        if digest(temporary) != expected:
            raise OSError(f"複製校驗失敗：{source}")
        if os.name == "nt":
            os.rename(temporary, target)
        else:
            os.link(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def release_of(text: str) -> str:
    match = re.search(r"(?:Release\s*)?(20\d{2})[ _/-]*R([12])\b|\bv(\d{3})\b", text, re.I)
    if not match:
        return "unknown"
    if match[3]:
        return "v" + match[3]
    return f"v{int(match[1]) % 100:02}{match[2]}"


def destination(relative: Path, sample: str, pdf_metadata: dict) -> tuple[Path, str, str]:
    """保留附件子樹，只改產品、已核實版本與分類層。"""
    parts = relative.parts
    product = parts[0]
    if len(parts) < 2 or product.startswith("_") or parts[-1] == "README.md":
        return relative, "unknown", ""
    if re.fullmatch(r"v\d{3}|legacy|unknown|sdk", parts[1]):
        return relative, parts[1], ""
    source = re.search(r"(?:source_url|source):\s*[`\"']?(https?://[^\s`\"']+)", sample, re.I)
    metadata = pdf_metadata.get(relative.as_posix(), {})
    source_url = source[1] if source else metadata.get("source_url", "")
    release = metadata.get("release", "unknown") if relative.suffix.lower() == ".pdf" else release_of(source_url)
    if release == "unknown" and relative.suffix.lower() != ".pdf":
        # 只採來源或明示Release，不以API正文提到的其他版本當本文件版本。
        match = re.search(r"Release\s*20\d{2}\s*R[12]", sample, re.I)
        if match:
            release = release_of(match[0])
        elif product == "ACT":
            release = release_of(relative.as_posix())
    tail = Path(*parts[1:])
    if product in {"md", "pdf"}:
        name = relative.name.lower()
        product = next((p for key, p in (("spaceclaim", "SpaceClaim"), ("mechanical", "Mechanical"),
                                       ("workbench", "Workbench")) if key in name), "ACT")
        tail = Path("manuals") / relative.name
    elif product == "Mechanical" and "LS-DYNA" in parts:
        product = "LS-DYNA"
        tail = Path("manuals") / Path(*parts[parts.index("LS-DYNA") + 1:])
    elif product == "Discovery" and "SpaceClaim_API" in parts:
        product = "SpaceClaim"
        tail = Path("api_reference") / Path(*parts[parts.index("SpaceClaim_API") + 1:])
    elif product == "AnsysEM":
        product = next((p for key, p in (("icepak", "Icepak"), ("hfss", "HFSS"), ("maxwell", "Maxwell"),
                                       ("q3d", "Q3D"), ("siwave", "SIwave"), ("emit", "EMIT"),
                                       ("circuit", "Circuit")) if key in relative.name.lower()), product)
    category = tail.parts[0]
    if category.startswith("manuals"):
        tail = Path("manuals", *tail.parts[1:])
    elif category == "tutorials":
        tail = Path("guides_and_tutorials", *tail.parts[1:])
    return Path(product) / release / tail, release, source_url


def duplicate_pairs(corpus: Path) -> list[tuple[Path, Path]]:
    pairs = [
        (corpus / "AnsysEM/manuals_and_training/UsersGuide_1.62.pdf", corpus / "TwinAI/manuals/UsersGuide_1.62.pdf"),
        *[(corpus / "SCADE/archives" / name, corpus / "SCADE/manuals_and_guides" / name)
          for name in ("Metamodels_SCF-API-TRC-26.pdf", "PythonAPIGuide_SCF-APG-26.pdf")],
    ]
    styles = sorted((corpus / "Discovery/manuals_and_guides").rglob("Style Guide_V*.pdf"))
    if styles:
        pairs.extend((path, styles[0]) for path in styles[1:])
    # 其他同內容檔只有來源URL、產品、版本及檔名也一致時才可合併。
    groups: dict[tuple, list[Path]] = defaultdict(list)
    for path in corpus.rglob("*.md"):
        if "_catalog" in path.parts or path.name in {"README.md", "INDEX.md"}:
            continue
        with path.open("r", encoding="utf-8", errors="replace") as stream:
            head = stream.read(1800)
        url = re.search(r"source_url:\s*(https?://\S+)", head)
        if url:
            groups[(path.relative_to(corpus).parts[0], path.name, url[1], path.stat().st_size)].append(path)
    for paths in groups.values():
        for path in paths[1:]:
            if digest(paths[0]) == digest(path) and filecmp.cmp(paths[0], path, shallow=False):
                pairs.append((path, paths[0]))
    return [(a, b) for a, b in pairs if a.exists() and b.exists()]


def apply_operations(root: Path, operations: list[dict], backup: Path) -> None:
    """先備份，再逐筆套用；已完成操作以目的hash驗證，允許中斷後續跑。"""
    for op in operations:
        if op.get("action") not in {"move", "deduplicate"} or not re.fullmatch(r"[a-f0-9]{64}", op.get("sha256", "")):
            raise ValueError("搬移紀錄格式無效")
        source, target = inside(root, op["source"]), inside(root, op["target"])
        saved = inside(backup, op["source"])
        expected = op["sha256"]
        if not source.exists():
            if not saved.is_file() or digest(saved) != expected or not target.is_file() or digest(target) != op.get("final_sha256", expected):
                raise OSError(f"已完成操作無法驗證，停止續跑：{source}")
            continue
        if digest(source) != expected:
            raise FileExistsError(f"來源在計畫後變更：{source}")
        saved.parent.mkdir(parents=True, exist_ok=True)
        if not saved.exists():
            copy_verified(source, saved, expected)
        if digest(saved) != expected:
            raise OSError(f"備份校驗失敗：{source}")
    for op in operations:
        source, target = inside(root, op["source"]), inside(root, op["target"])
        if not source.exists():
            continue
        if digest(source) != op["sha256"]:
            raise OSError(f"來源在備份後變更：{source}")
        if op["action"] == "move" and not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            copy_verified(source, target, op["sha256"])
        if not target.is_file() or digest(target) != op["sha256"]:
            raise OSError(f"目的校驗失敗，保留來源：{source}")
        source.unlink()


def repair_links(root: Path, operations: list[dict]) -> int:
    """依原路徑解讀相對連結，再指向新位置；外部URL及正文不變。"""
    import os
    mapping = {inside(root, op["source"]): inside(root, op["target"]) for op in operations}
    original = {target: source for source, target in mapping.items()}
    directories: dict[Path, set[Path]] = defaultdict(set)
    for source, target in mapping.items():
        directories[source.parent].add(target.parent)
    changed = 0
    issues = []
    paths = set((root / "ANSYS_Document").rglob("*.md"))
    paths.update(inside(root, op["target"]) for op in operations if op["target"].endswith(".md") and op["action"] == "move")
    for path in sorted(paths):
        if "_catalog" in path.parts:
            continue
        old_path = original.get(path.resolve(), path.resolve())
        saved = inside(root / ".runtime/folder-document-cleanup/link-originals", path.relative_to(root).as_posix())
        try:
            current_text = path.read_text(encoding="utf-8")
            text = saved.read_text(encoding="utf-8") if saved.exists() else current_text
        except UnicodeDecodeError:
            issues.append({"path": path.relative_to(root).as_posix(), "reason": "encoding_not_utf8", "action": "preserved"})
            continue
        def replace(match):
            value = match[1]
            wrapped = value.startswith("<") and value.endswith(">")
            url = value[1:-1] if wrapped else value
            parts = urlsplit(url)
            if parts.scheme or parts.netloc or not parts.path:
                return match[0]
            old_target = (old_path.parent / unquote(parts.path)).resolve()
            new_target = mapping.get(old_target)
            if new_target is None and len(directories.get(old_target, set())) == 1:
                new_target = next(iter(directories[old_target]))
            if new_target is None:
                if old_path == path.resolve() or not old_target.is_file():
                    return match[0]
                new_target = old_target
            relative = Path(os.path.relpath(new_target, path.parent)).as_posix()
            if parts.query:
                relative += "?" + parts.query
            if parts.fragment:
                relative += "#" + parts.fragment
            if wrapped or " " in relative:
                relative = "<" + relative + ">"
            return "](" + relative + ")"
        new_text = re.sub(r"\]\((<[^>]+>|[^)\r\n]+)\)", replace, text)
        if current_text not in (text, new_text):
            raise FileExistsError(f"連結修復後有其他變更，保留原檔：{path}")
        if new_text != current_text:
            saved.parent.mkdir(parents=True, exist_ok=True)
            if not saved.exists():
                shutil.copy2(path, saved)
            path.write_text(new_text, encoding="utf-8")
            changed += 1
    if (root / "ANSYS_Document").is_dir():
        issue_path = inside(root, "ANSYS_Document/_catalog/link_repair_issues.json")
        issue_path.parent.mkdir(parents=True, exist_ok=True)
        issue_path.write_text(json.dumps(issues, ensure_ascii=False, indent=2), encoding="utf-8")
    for op in operations:
        target = inside(root, op["target"])
        if target.is_file():
            op["final_sha256"] = digest(target)
    return changed


def execute(root: Path, *, apply: bool, corpus_layout: bool, pdf_metadata: dict) -> dict:
    root = root.resolve()
    corpus = inside(root, "ANSYS_Document")
    backup = inside(root, ".runtime/folder-document-cleanup/originals")
    report = inside(root, ".runtime/folder-document-cleanup/relocations.json")
    if apply and report.exists():
        saved = json.loads(report.read_text(encoding="utf-8"))
        apply_operations(root, saved["operations"], backup)
        catalog = corpus / "_catalog"
        catalog.mkdir(exist_ok=True)
        if not (catalog / "relocations.json").exists():
            aliases = {op["source"].removeprefix("ANSYS_Document/"): op["target"].removeprefix("ANSYS_Document/")
                       for op in saved["operations"] if op["source"].startswith("ANSYS_Document/")}
            moves = [{"original_path": old, "new_path": new,
                      "release": new.split("/")[1] if len(new.split("/")) > 2 else "unknown", "source_url": ""}
                     for old, new in aliases.items()]
            (catalog / "relocations.json").write_text(json.dumps({"moves": moves, "aliases": aliases}, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"applied": True, "resumed": True, "operations_verified": len(saved["operations"])}
    operations = []
    duplicates = duplicate_pairs(corpus)
    removed = {a for a, _ in duplicates}
    mapping = dict(MOVES)
    metadata = {}
    if corpus_layout:
        for path in sorted(corpus.rglob("*")):
            if not path.is_file() or path in removed or "_catalog" in path.parts:
                continue
            rel = path.relative_to(corpus)
            sample = ""
            if path.suffix.lower() in {".md", ".html", ".txt"}:
                with path.open("r", encoding="utf-8", errors="replace") as stream:
                    sample = stream.read(2500)
            new_rel, release, source_url = destination(rel, sample, pdf_metadata)
            if path.name.startswith("Style Guide_V"):
                new_rel = Path("SpaceClaim/legacy/manuals/Add-in_Style_Guide_2014-11.pdf")
                release = "legacy"
            if new_rel != rel:
                old = path.relative_to(root).as_posix()
                mapping[old] = (Path("ANSYS_Document") / new_rel).as_posix()
                metadata[old] = {"original_path": rel.as_posix(), "new_path": new_rel.as_posix(),
                                 "release": release, "source_url": source_url}
    for old, new in mapping.items():
        source, target = inside(root, old), inside(root, new)
        if not source.exists():
            continue
        if target.exists() and not filecmp.cmp(source, target, shallow=False):
            raise FileExistsError(f"目的已有不同內容，停止：{new}")
        operations.append({"action": "move", "source": old, "target": new, "sha256": digest(source)})
    planned_targets = {}
    for op in operations:
        key = op["target"].casefold()
        if key in planned_targets and planned_targets[key] != op["sha256"]:
            raise FileExistsError(f"多個不同來源指向同一目的：{op['target']}")
        planned_targets[key] = op["sha256"]
    for redundant, kept in duplicates:
        if digest(redundant) != digest(kept) or not filecmp.cmp(redundant, kept, shallow=False):
            raise ValueError(f"不是完全重複：{redundant}")
        operations.append({"action": "deduplicate", "source": redundant.relative_to(root).as_posix(),
                           "target": mapping.get(kept.relative_to(root).as_posix(), kept.relative_to(root).as_posix()),
                           "sha256": digest(redundant), "size": redundant.stat().st_size})
    summary = {"moves": sum(o["action"] == "move" for o in operations),
               "duplicates": sum(o["action"] == "deduplicate" for o in operations),
               "duplicate_bytes": sum(o.get("size", 0) for o in operations), "applied": apply}
    if not apply:
        return {**summary, "operations": operations}
    report = inside(root, ".runtime/folder-document-cleanup/relocations.json")
    report.parent.mkdir(parents=True, exist_ok=True)
    if report.exists() and operations:
        raise FileExistsError("已存在搬移紀錄，請先核對，避免覆寫回復證據。")
    if not operations:
        return summary
    report.write_text(json.dumps({"operations": operations}, ensure_ascii=False, indent=2), encoding="utf-8")
    apply_operations(root, operations, backup)
    catalog = corpus / "_catalog"
    catalog.mkdir(exist_ok=True)
    aliases = {o["source"].removeprefix("ANSYS_Document/"): o["target"].removeprefix("ANSYS_Document/")
               for o in operations if o["source"].startswith("ANSYS_Document/")}
    (catalog / "relocations.json").write_text(json.dumps({"moves": list(metadata.values()), "aliases": aliases},
                                                          ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--corpus", action="store_true", help="將既有產品文件加入版本層")
    parser.add_argument("--repair-links", action="store_true", help="依已完成清單修正相對連結")
    parser.add_argument("--pdf-metadata", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    pdf = json.loads(args.pdf_metadata.read_text(encoding="utf-8")) if args.pdf_metadata else {}
    if args.repair_links:
        if not args.apply:
            parser.error("--repair-links 需要 --apply；請先檢查既有搬移紀錄")
        report = inside(args.workspace.resolve(), ".runtime/folder-document-cleanup/relocations.json")
        data = json.loads(report.read_text(encoding="utf-8"))
        changed = repair_links(args.workspace.resolve(), data["operations"])
        report.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        result = {"links_repaired_files": changed}
    else:
        result = execute(args.workspace, apply=args.apply, corpus_layout=args.corpus, pdf_metadata=pdf)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "operations"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
