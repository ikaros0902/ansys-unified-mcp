"""Render human-readable dictionaries from captured protobuf snapshots."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
API_DIR = ROOT / "docs" / "api_inventory"
OUTPUT_DIR = API_DIR / "curated" / "protocols"


def cell(value: Any) -> str:
    return str(value or "").replace("|", r"\|").replace("\r", " ").replace("\n", " ")


def render(snapshot_path: Path) -> str:
    raw = snapshot_path.read_bytes()
    snapshot = json.loads(raw.decode("utf-8"))
    source_key = snapshot_path.stem.removesuffix("_api")
    lines = [
        f"# {source_key} protocol dictionary",
        "",
        f"- APIKB source key: `{source_key}`",
        f"- Package: `{snapshot['sdk_package']} {snapshot['sdk_version']}`",
        f"- Interface: {snapshot['interface']}",
        f"- Snapshot: [`{snapshot_path.name}`](../../{snapshot_path.name})",
        f"- Snapshot SHA-256: `{hashlib.sha256(raw).hexdigest()}`",
        "",
        "> This page describes the captured protobuf schema. It does not confirm product support, host compatibility, or runtime behavior.",
        "> This snapshot records enum type names on fields. It does not list enum members.",
        "",
        "## Services and RPC methods",
        "",
    ]

    rpc_count = 0
    message_count = 0
    field_count = 0
    for module_name, module in sorted(snapshot["modules"].items()):
        classes = module.get("classes", {})
        services = [
            (name, record)
            for name, record in sorted(classes.items())
            if str(record.get("doc", "")).startswith("gRPC service ")
        ]
        if services:
            lines.extend([f"### `{module_name}`", "", "| Service | RPC method | Signature |", "| --- | --- | --- |"])
            for service_name, service in services:
                for method in service.get("methods", []):
                    lines.append(
                        f"| `{cell(service_name)}` | `{cell(method.get('name'))}` | `{cell(method.get('signature'))}` |"
                    )
                    rpc_count += 1
            lines.append("")

    lines.extend(["## Messages and fields", ""])
    for module_name, module in sorted(snapshot["modules"].items()):
        messages = [
            (name, record)
            for name, record in sorted(module.get("classes", {}).items())
            if str(record.get("doc", "")).startswith("Protocol message ")
        ]
        if not messages:
            continue
        lines.extend([f"### `{module_name}`", "", "| Message | Fields |", "| --- | --- |"])
        for name, message in messages:
            fields = message.get("properties", [])
            rendered_fields = "<br>".join(
                f"`{cell(field.get('name'))}: {cell(field.get('type'))}` ({cell(field.get('doc'))})"
                for field in fields
            ) or "—"
            lines.append(f"| `{cell(name)}` | {rendered_fields} |")
            message_count += 1
            field_count += len(fields)
        lines.append("")

    lines.extend(
        [
            "## Snapshot counts",
            "",
            f"- RPC methods: {rpc_count}",
            f"- Protocol messages: {message_count}",
            f"- Message fields: {field_count}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for snapshot_path in sorted(API_DIR.glob("*_protocol_api.json")):
        target = OUTPUT_DIR / f"{snapshot_path.stem.removesuffix('_api')}.md"
        target.write_text(render(snapshot_path), encoding="utf-8", newline="\n")
        print(f"Wrote {target.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
