"""以 AST 擷取 PyOptiSLang 1.6.0 Optislang client 的直接成員。"""

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
OUT_PATH = REPO_ROOT / "docs" / "api_inventory" / "optislang_core_api.json"
DOC_HTML = (
    REPO_ROOT
    / "ANSYS_Document"
    / "optiSLang"
    / "sdk"
    / "ansys-optislang-core"
    / "1.7.0"
    / "api_reference"
    / "96168993a608-ansys.optislang.core.optislang.Optislang.html"
)
DOC_MARKDOWN = DOC_HTML.with_suffix(".md")
SDK_VERSION = "1.6.0"
DOC_VERSION = "1.7.0"
MODULE_NAME = "ansys.optislang.core.optislang"
CLASS_NAME = "Optislang"


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


def _class_members(
    cls: ast.ClassDef, source_path: str
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
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
    return methods, properties


def _excluded_docs() -> dict[str, Any]:
    if not DOC_HTML.is_file() or not DOC_MARKDOWN.is_file():
        raise FileNotFoundError("Expected local PyOptiSLang 1.7.0 API reference is missing")
    html = DOC_HTML.read_text(encoding="utf-8")
    match = re.search(r'<meta name="docsearch:version" content="([^"]+)"', html)
    if not match or match.group(1) != DOC_VERSION:
        raise ValueError("Local PyOptiSLang API reference version metadata changed")
    return {
        "version": DOC_VERSION,
        "reason": "本機 API reference 為 1.7.0，與 SDK 1.6.0 不同版，僅列為排除證據。",
        "files": [
            {"path": path.relative_to(REPO_ROOT).as_posix(), "sha256": _sha256(path)}
            for path in (DOC_MARKDOWN, DOC_HTML)
        ],
    }


def extract_optislang_core_api() -> dict[str, Any]:
    actual_version = importlib.metadata.version("ansys-optislang-core")
    if actual_version != SDK_VERSION:
        raise RuntimeError(f"Expected ansys-optislang-core {SDK_VERSION}, found {actual_version}")
    source = Path(
        importlib.metadata.distribution("ansys-optislang-core").locate_file(
            "ansys/optislang/core/optislang.py"
        )
    )
    if not source.is_file():
        raise FileNotFoundError(f"PyOptiSLang SDK source is missing: {source}")
    source_path = source.resolve().as_posix()
    tree = ast.parse(source.read_text(encoding="utf-8"))
    cls = next(
        (item for item in tree.body if isinstance(item, ast.ClassDef) and item.name == CLASS_NAME),
        None,
    )
    if cls is None:
        raise ValueError("PyOptiSLang Optislang class source is missing")
    methods, properties = _class_members(cls, source_path)
    if len(methods) != 18 or len(properties) != 9:
        raise RuntimeError(
            f"Unexpected PyOptiSLang Optislang API: methods={len(methods)}, properties={len(properties)}"
        )
    snapshot = {
        "module": MODULE_NAME,
        "version": "unknown",
        "sdk_package": "ansys-optislang-core",
        "sdk_version": SDK_VERSION,
        "interface": "PyOptiSLang 1.6.0 Optislang client",
        "scope": (
            "範圍限於 Optislang 直接宣告的公開方法與屬性；以 AST 靜態讀取 SDK 1.6.0 原始碼，"
            "不匯入套件、不建立 client、不啟動或連線 optiSLang。"
        ),
        "sources": {
            "sdk_files": [{"path": source_path, "sha256": _sha256(source)}],
            "excluded_api_references": [_excluded_docs()],
        },
        "modules": {
            MODULE_NAME: {
                "doc": ast.get_docstring(tree, clean=True) or "",
                "classes": {
                    CLASS_NAME: {
                        "name": CLASS_NAME,
                        "doc": ast.get_docstring(cls, clean=True) or "",
                        "methods": methods,
                        "properties": properties,
                    }
                },
                "functions": [],
            }
        },
        "statistics": {
            "total_modules": 1,
            "total_classes": 1,
            "total_methods": len(methods),
            "total_properties": len(properties),
            "total_functions": 0,
        },
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="optislang_core_api.", suffix=".tmp", dir=OUT_PATH.parent)
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
    result = extract_optislang_core_api()
    print(
        "PyOptiSLang core API extraction complete: "
        f"{result['statistics']['total_methods']} methods, "
        f"{result['statistics']['total_properties']} properties"
    )
