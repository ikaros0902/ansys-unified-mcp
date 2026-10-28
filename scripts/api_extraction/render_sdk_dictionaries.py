"""Render human-readable dictionaries from versioned Python SDK snapshots."""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
API_DIR = ROOT / "docs" / "api_inventory"
OUTPUT_DIR = API_DIR / "curated" / "sdk"


def _doc(value: Any) -> str:
    value = str(value or "").strip()
    if not value:
        return ""
    return f"<details><summary>說明</summary>\n\n<pre>{html.escape(value)}</pre>\n\n</details>"


def _members(snapshot: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    modules = snapshot.get("modules")
    if not isinstance(modules, dict):
        raise ValueError("Snapshot 'modules' must be an object.")

    rendered: list[dict[str, Any]] = []
    counts = {"modules": len(modules), "classes": 0, "methods": 0, "properties": 0, "functions": 0}
    for module_name, module in sorted(modules.items()):
        if not isinstance(module, dict):
            raise ValueError(f"Module {module_name!r} must be an object.")
        classes = module.get("classes", {})
        functions = module.get("functions", [])
        if not isinstance(classes, dict) or not isinstance(functions, list):
            raise ValueError(f"Module {module_name!r} has an unsupported member layout.")
        module_record = {"name": module_name, "doc": module.get("doc", ""), "classes": [], "functions": functions}
        for class_name, record in sorted(classes.items()):
            if not isinstance(record, dict):
                raise ValueError(f"Class {module_name}.{class_name} must be an object.")
            methods = record.get("methods", [])
            properties = record.get("properties", [])
            if not isinstance(methods, list) or not isinstance(properties, list):
                raise ValueError(f"Class {module_name}.{class_name} has an unsupported member layout.")
            module_record["classes"].append(
                {"name": class_name, "doc": record.get("doc", ""), "methods": methods, "properties": properties}
            )
            counts["classes"] += 1
            counts["methods"] += len(methods)
            counts["properties"] += len(properties)
        counts["functions"] += len(functions)
        rendered.append(module_record)
    return rendered, counts


def render(snapshot_path: Path) -> tuple[str, dict[str, Any]]:
    raw = snapshot_path.read_bytes()
    snapshot = json.loads(raw.decode("utf-8"))
    package = snapshot.get("sdk_package")
    version = snapshot.get("sdk_version")
    interface = snapshot.get("interface") or "SDK snapshot"
    if not package or not version:
        raise ValueError(f"{snapshot_path.name} is not a versioned SDK snapshot.")
    modules, counts = _members(snapshot)
    digest = hashlib.sha256(raw).hexdigest()
    source_key = snapshot_path.stem.removesuffix("_api")
    lines = [
        f"# {package} {version} API dictionary",
        "",
        f"- APIKB source key: `{source_key}`",
        f"- Interface: {interface}",
        f"- Snapshot: [`{snapshot_path.name}`](../../{snapshot_path.name})",
        f"- Snapshot SHA-256: `{digest}`",
        f"- Scope: {snapshot.get('scope') or 'See the captured modules and members listed below.'}",
        "",
        "> This page describes the captured SDK snapshot. It does not confirm ANSYS product support, server compatibility, or runtime behavior.",
        "",
        "## Captured modules and members",
        "",
    ]
    for module in modules:
        lines.extend([f"### `{module['name']}`", ""])
        module_doc = _doc(module["doc"])
        if module_doc:
            lines.extend([module_doc, ""])
        for cls in module["classes"]:
            lines.extend([f"#### `{cls['name']}`", ""])
            class_doc = _doc(cls["doc"])
            if class_doc:
                lines.extend([class_doc, ""])
            for heading, members in (("Methods", cls["methods"]), ("Properties", cls["properties"])):
                if not members:
                    continue
                lines.extend([f"**{heading}**", ""])
                for member in members:
                    name = str(member.get("name", "(unnamed)"))
                    signature = str(member.get("signature", ""))
                    detail = str(member.get("type", ""))
                    suffix = f": `{detail}`" if detail else ""
                    lines.extend([f"- `{name}{signature}`{suffix}", ""])
                    description = _doc(member.get("doc"))
                    if description:
                        lines.extend([description, ""])
        if module["functions"]:
            lines.extend(["**Functions**", ""])
            for function in module["functions"]:
                name = str(function.get("name", "(unnamed)"))
                signature = str(function.get("signature", ""))
                lines.extend([f"- `{name}{signature}`", ""])
                description = _doc(function.get("doc"))
                if description:
                    lines.extend([description, ""])
    lines.extend(
        [
            "## Captured counts",
            "",
            *(f"- {label.title()}: {count}" for label, count in counts.items()),
            "",
        ]
    )
    return "\n".join(lines), {"source_key": source_key, "package": package, "version": version, **counts}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    entries = []
    for snapshot_path in sorted(API_DIR.glob("*_api.json")):
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        interface = str(snapshot.get("interface") or "")
        if not snapshot.get("sdk_package") or not snapshot.get("sdk_version"):
            continue
        if "protocol schema" in interface.lower():
            continue
        document, entry = render(snapshot_path)
        target = OUTPUT_DIR / f"{entry['source_key']}.md"
        target.write_text(document, encoding="utf-8", newline="\n")
        entries.append(entry)
        print(f"Wrote {target.relative_to(ROOT).as_posix()}")

    if not entries:
        raise RuntimeError("No versioned non-protocol SDK snapshots were found.")
    index = [
        "# Versioned Python SDK dictionaries",
        "",
        "Each page lists the modules and members present in its captured SDK snapshot.",
        "A package version is not an ANSYS product release. Captured signatures and docstrings do not prove host compatibility or runtime behavior.",
        "",
        "| Source key | Package | Version | Modules | Classes | Methods | Properties | Functions | Dictionary |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for entry in entries:
        index.append(
            f"| `{entry['source_key']}` | `{entry['package']}` | `{entry['version']}` | "
            f"{entry['modules']} | {entry['classes']} | {entry['methods']} | "
            f"{entry['properties']} | {entry['functions']} | [{entry['source_key']}.md]({entry['source_key']}.md) |"
        )
    (OUTPUT_DIR / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {len(entries)} SDK dictionaries and index")


if __name__ == "__main__":
    main()
