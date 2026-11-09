"""以 AST 靜態擷取 PyDyna 0.12.1 的 Deck 類別 API。"""

from __future__ import annotations

import ast
import hashlib
import importlib.metadata
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DOC_DIR = REPO_ROOT / "docs" / "ANSYS_Document" / "LS-DYNA" / "sdk" / "ansys-dyna-core" / "0.12.1" / "api_reference"
DOC_MARKDOWN = DOC_DIR / "899655182e59-index.md"
DOC_HTML = DOC_DIR / "899655182e59-index.html"
OUT_PATH = REPO_ROOT / "docs" / "api_inventory" / "pydyna_api.json"
SDK_VERSION = "0.12.1"
MODULE_NAME = "ansys.dyna.core.lib.deck"
CLASS_NAME = "Deck"
DOC_VERSION = re.compile(r'<meta name="docsearch:version" content="([^"]+)"')
SOURCE_URL = re.compile(r"^source_url:\s*(https?://\S+)$", re.MULTILINE)
CLASS_URL = re.compile(r"\[Deck\]\((https?://[^)]+)\)")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    function = ast.FunctionDef(
        name=node.name,
        args=node.args,
        body=[ast.Pass()],
        decorator_list=[],
        returns=node.returns,
        type_comment=None,
    )
    source = ast.unparse(ast.fix_missing_locations(function)).splitlines()[0]
    return source[len(f"def {node.name}") : -1]


def _extract_class_members(
    module: ast.Module, class_name: str, source_path: str
) -> tuple[dict[str, Any], list[dict[str, str]], list[dict[str, str]]]:
    cls = next(
        (item for item in module.body if isinstance(item, ast.ClassDef) and item.name == class_name),
        None,
    )
    if cls is None:
        raise ValueError(f"Class not found in SDK source: {class_name}")

    methods = []
    properties = []
    for item in cls.body:
        if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) or item.name.startswith("_"):
            continue
        decorators = [ast.unparse(decorator) for decorator in item.decorator_list]
        if "property" in decorators:
            properties.append(
                {
                    "name": item.name,
                    "type": ast.unparse(item.returns) if item.returns else "",
                    "doc": ast.get_docstring(item, clean=True) or "",
                    "sdk_source_path": source_path,
                    "signature_source_path": source_path,
                }
            )
        elif any(decorator.endswith((".setter", ".getter", ".deleter")) for decorator in decorators):
            continue
        else:
            methods.append(
                {
                    "name": item.name,
                    "signature": _signature(item),
                    "doc": ast.get_docstring(item, clean=True) or "",
                    "sdk_source_path": source_path,
                    "signature_source_path": source_path,
                }
            )
    return (
        {"name": class_name, "doc": ast.get_docstring(cls, clean=True) or ""},
        methods,
        properties,
    )


def _doc_evidence() -> dict[str, str]:
    if not DOC_MARKDOWN.is_file() or not DOC_HTML.is_file():
        raise FileNotFoundError("PyDyna Deck API reference is missing")
    html_text = DOC_HTML.read_text(encoding="utf-8")
    version = DOC_VERSION.search(html_text)
    if not version or version.group(1) != SDK_VERSION:
        raise RuntimeError(f"Expected PyDyna docs {SDK_VERSION}, found {version.group(1) if version else 'unknown'}")
    markdown_text = DOC_MARKDOWN.read_text(encoding="utf-8")
    source_url = SOURCE_URL.search(markdown_text)
    class_url = CLASS_URL.search(markdown_text)
    if not source_url or not class_url:
        raise RuntimeError("PyDyna Deck API reference link or source URL is missing")
    return {
        "name": "Deck",
        "path": DOC_MARKDOWN.relative_to(REPO_ROOT).as_posix(),
        "url": class_url.group(1),
        "index_url": source_url.group(1),
        "sha256": _sha256(DOC_MARKDOWN),
        "html_path": DOC_HTML.relative_to(REPO_ROOT).as_posix(),
        "html_sha256": _sha256(DOC_HTML),
        "html_version": version.group(1),
    }


def extract_pydyna_api() -> dict[str, Any]:
    actual_version = importlib.metadata.version("ansys-dyna-core")
    if actual_version != SDK_VERSION:
        raise RuntimeError(f"Expected ansys-dyna-core {SDK_VERSION}, found {actual_version}")
    source = Path(importlib.metadata.distribution("ansys-dyna-core").locate_file("ansys/dyna/core/lib/deck.py"))
    if not source.is_file():
        raise FileNotFoundError(f"PyDyna SDK source is missing: {source}")
    source_path = source.resolve().as_posix()
    class_info, methods, properties = _extract_class_members(
        ast.parse(source.read_text(encoding="utf-8")), CLASS_NAME, source_path
    )
    if not methods or not properties:
        raise RuntimeError(f"Unexpected PyDyna Deck API: methods={len(methods)}, properties={len(properties)}")
    module = {
        "doc": class_info["doc"],
        "classes": {CLASS_NAME: {**class_info, "methods": methods, "properties": properties}},
        "functions": [],
    }
    snapshot = {
        "module": MODULE_NAME,
        "version": "unknown",
        "sdk_package": "ansys-dyna-core",
        "sdk_version": SDK_VERSION,
        "interface": "PyDyna 0.12.1 Deck class",
        "scope": "範圍限於 PyDyna Deck 直接宣告的公開方法與屬性；以 AST 讀取 SDK 原始碼，不匯入套件、不建立 Deck、不讀寫模型或執行 solver。",
        "sources": {
            "api_references": [_doc_evidence()],
            "sdk_files": [{"path": source_path, "sha256": _sha256(source)}],
        },
        "modules": {MODULE_NAME: module},
        "statistics": {
            "total_modules": 1,
            "total_classes": 1,
            "total_methods": len(methods),
            "total_properties": len(properties),
            "total_functions": 0,
        },
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="pydyna_api.", suffix=".tmp", dir=OUT_PATH.parent)
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
    result = extract_pydyna_api()
    print(f"PyDyna {SDK_VERSION}: {result['statistics']}")
