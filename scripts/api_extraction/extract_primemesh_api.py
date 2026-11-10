"""擷取本機 PyPrimeMesh 0.10.5 的 Client 與 launch_prime API。"""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import inspect
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DOC_DIR = (
    REPO_ROOT
    / "docs" / "ANSYS_Document"
    / "Primemesh"
    / "sdk"
    / "ansys-meshing-prime"
    / "0.10.5"
    / "api_reference"
)
OUT_PATH = REPO_ROOT / "docs" / "api_inventory" / "primemesh_api.json"
SDK_VERSION = "0.10.5"
DOC_NAMES = {
    "launch_prime": "8c777aa89711-ansys.meshing.prime.launch_prime",
    "Client": "ef19d6c98b8a-ansys.meshing.prime.Client",
    "Client.model": "fe7831a5971b-ansys.meshing.prime.Client.model",
    "Client.run_on_server": "7b49ba52a5b7-ansys.meshing.prime.Client.run_on_server",
    "Client.exit": "5d2aacca5459-ansys.meshing.prime.Client.exit",
}
DOC_VERSION = re.compile(r'<meta name="docsearch:version" content="([^"]+)"')
SOURCE_URL = re.compile(r"^source_url:\s*(https?://\S+)$", re.MULTILINE)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_path(obj: Any) -> str | None:
    try:
        path = inspect.getsourcefile(obj)
    except (TypeError, OSError):
        return None
    return str(Path(path).resolve()) if path else None


def _method_record(name: str, function: Any) -> dict[str, str]:
    signature = str(inspect.signature(function))
    return {
        "name": name,
        "signature": signature,
        "doc": inspect.getdoc(function) or "",
        "sdk_source_path": _source_path(function) or "",
        "signature_source_path": _source_path(inspect.unwrap(function)) or "",
    }


def _extract_client_members(cls: type) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    methods = []
    properties = []
    for name, raw in cls.__dict__.items():
        if name.startswith("_"):
            continue
        value = raw.__func__ if isinstance(raw, (classmethod, staticmethod)) else raw
        if inspect.isfunction(value):
            methods.append(_method_record(name, value))
        elif isinstance(raw, property) and raw.fget is not None:
            getter = raw.fget
            signature = inspect.signature(getter)
            annotation = signature.return_annotation
            properties.append(
                {
                    "name": name,
                    "type": "" if annotation is inspect.Signature.empty else str(annotation),
                    "doc": inspect.getdoc(getter) or "",
                    "sdk_source_path": _source_path(getter) or "",
                    "signature_source_path": _source_path(inspect.unwrap(getter)) or "",
                }
            )
    return methods, properties


def _doc_evidence(label: str, stem: str) -> dict[str, str]:
    markdown = DOC_DIR / f"{stem}.md"
    html = DOC_DIR / f"{stem}.html"
    if not markdown.is_file() or not html.is_file():
        raise FileNotFoundError(f"PyPrimeMesh API reference is missing for {label}")
    html_text = html.read_text(encoding="utf-8")
    match = DOC_VERSION.search(html_text)
    if not match or match.group(1) != SDK_VERSION:
        raise RuntimeError(f"Expected {label} docs {SDK_VERSION}, found {match.group(1) if match else 'unknown'}")
    markdown_text = markdown.read_text(encoding="utf-8")
    url = SOURCE_URL.search(markdown_text)
    if not url:
        raise RuntimeError(f"PyPrimeMesh API reference has no source URL: {markdown}")
    return {
        "name": label,
        "path": markdown.relative_to(REPO_ROOT).as_posix(),
        "url": url.group(1),
        "sha256": _sha256(markdown),
        "html_path": html.relative_to(REPO_ROOT).as_posix(),
        "html_sha256": _sha256(html),
        "html_version": match.group(1),
    }


def extract_primemesh_api() -> dict[str, Any]:
    actual_version = importlib.metadata.version("ansys-meshing-prime")
    if actual_version != SDK_VERSION:
        raise RuntimeError(f"Expected ansys-meshing-prime {SDK_VERSION}, found {actual_version}")

    references = [_doc_evidence(name, stem) for name, stem in DOC_NAMES.items()]
    public_api = importlib.import_module("ansys.meshing.prime")
    client = getattr(public_api, "Client")
    launch_prime = getattr(public_api, "launch_prime")
    if not inspect.isclass(client) or not inspect.isfunction(launch_prime):
        raise RuntimeError("Expected PyPrimeMesh Client class and launch_prime function")

    methods, properties = _extract_client_members(client)
    method_names = {item["name"] for item in methods}
    property_names = {item["name"] for item in properties}
    if method_names != {"run_on_server", "exit"} or property_names != {"model"}:
        raise RuntimeError(
            f"Unexpected Client API members: methods={sorted(method_names)}, properties={sorted(property_names)}"
        )

    function = _method_record("launch_prime", launch_prime)
    sdk_files = {Path(public_api.__file__).resolve()}
    sdk_files.update(
        Path(item[key])
        for item in methods + properties + [function]
        for key in ("sdk_source_path", "signature_source_path")
        if item.get(key)
    )
    snapshot = {
        "module": "ansys.meshing.prime",
        "version": "unknown",
        "sdk_package": "ansys-meshing-prime",
        "sdk_version": SDK_VERSION,
        "interface": "PyPrimeMesh 0.10.5 Client and launch_prime",
        "scope": (
            "範圍限於 Client 直接宣告的 run_on_server、exit、model 及 launch_prime。"
            "本擷取只讀取 SDK 與已核對 0.10.5 的 API reference，不建立 Client、不呼叫成員、不啟動 Prime Server。"
        ),
        "sources": {
            "api_references": references,
            "sdk_files": [
                {"path": path.as_posix(), "sha256": _sha256(path)} for path in sorted(sdk_files)
            ],
        },
        "modules": {
            "ansys.meshing.prime": {
                "doc": inspect.getdoc(public_api) or "",
                "classes": {
                    "Client": {
                        "name": "Client",
                        "doc": inspect.getdoc(client) or "",
                        "methods": methods,
                        "properties": properties,
                    }
                },
                "functions": [function],
            }
        },
        "statistics": {
            "total_modules": 1,
            "total_classes": 1,
            "total_methods": len(methods),
            "total_properties": len(properties),
            "total_functions": 1,
        },
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="primemesh_api.", suffix=".tmp", dir=OUT_PATH.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(snapshot, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, OUT_PATH)
    except BaseException:
        Path(temp_name).unlink(missing_ok=True)
        raise
    return snapshot


if __name__ == "__main__":
    result = extract_primemesh_api()
    print(f"PyPrimeMesh {SDK_VERSION}: {result['statistics']}")
