"""以 AST 靜態擷取 PyAnsys Geometry 0.17.1 的 Modeler API。"""

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
OUT_PATH = REPO_ROOT / "docs" / "api_inventory" / "geometry_core_api.json"
DOC_DIR = REPO_ROOT / "docs" / "ANSYS_Document" / "Geometry" / "sdk" / "ansys-geometry-core" / "0.18.2" / "api_reference"
DOC_MARKDOWN = DOC_DIR / "d3ab5ac63cc0-Modeler.md"
DOC_HTML = DOC_DIR / "d3ab5ac63cc0-Modeler.html"
SDK_VERSION = "0.17.1"
DOC_VERSION = "0.18.2"
CLASS_MODULE = "ansys.geometry.core.modeler"
LAUNCHER_MODULE = "ansys.geometry.core.connection.launcher"
CLASS_NAME = "Modeler"
FUNCTION_NAME = "launch_modeler"
HTML_VERSION = re.compile(r'<meta name="docsearch:version" content="([^"]+)"')
SOURCE_URL = re.compile(r"^source_url:\s*(https?://\S+)$", re.MULTILINE)


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


def _excluded_docs() -> dict[str, str]:
    if not DOC_MARKDOWN.is_file() or not DOC_HTML.is_file():
        raise FileNotFoundError("PyAnsys Geometry Modeler API reference is missing")
    html_version = HTML_VERSION.search(DOC_HTML.read_text(encoding="utf-8"))
    url = SOURCE_URL.search(DOC_MARKDOWN.read_text(encoding="utf-8"))
    if not html_version or html_version.group(1) != DOC_VERSION or not url:
        raise RuntimeError("PyAnsys Geometry local docs evidence is malformed")
    if DOC_VERSION == SDK_VERSION:
        raise RuntimeError("Expected a version mismatch for excluded PyAnsys Geometry docs")
    return {
        "name": "Modeler",
        "path": DOC_MARKDOWN.relative_to(REPO_ROOT).as_posix(),
        "url": url.group(1),
        "sha256": _sha256(DOC_MARKDOWN),
        "html_path": DOC_HTML.relative_to(REPO_ROOT).as_posix(),
        "html_sha256": _sha256(DOC_HTML),
        "html_version": html_version.group(1),
        "reason": f"本機文件版次 {DOC_VERSION} 與 SDK {SDK_VERSION} 不同，不用作 API 來源。",
    }


def extract_geometry_core_api() -> dict[str, Any]:
    actual_version = importlib.metadata.version("ansys-geometry-core")
    if actual_version != SDK_VERSION:
        raise RuntimeError(f"Expected ansys-geometry-core {SDK_VERSION}, found {actual_version}")
    distribution = importlib.metadata.distribution("ansys-geometry-core")
    modeler_source = Path(distribution.locate_file("ansys/geometry/core/modeler.py"))
    launcher_source = Path(
        distribution.locate_file("ansys/geometry/core/connection/launcher.py")
    )
    if not modeler_source.is_file() or not launcher_source.is_file():
        raise FileNotFoundError("PyAnsys Geometry SDK source is missing")
    modeler_path = modeler_source.resolve().as_posix()
    launcher_path = launcher_source.resolve().as_posix()
    modeler_tree = ast.parse(modeler_source.read_text(encoding="utf-8"))
    launcher_tree = ast.parse(launcher_source.read_text(encoding="utf-8"))
    cls = next(
        (item for item in modeler_tree.body if isinstance(item, ast.ClassDef) and item.name == CLASS_NAME),
        None,
    )
    function = next(
        (
            item
            for item in launcher_tree.body
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            and item.name == FUNCTION_NAME
        ),
        None,
    )
    if cls is None or function is None:
        raise ValueError("PyAnsys Geometry Modeler or launch_modeler source is missing")
    methods, properties = _class_members(cls, modeler_path)
    functions = [
        {
            "name": FUNCTION_NAME,
            "signature": _signature(function),
            "doc": ast.get_docstring(function, clean=True) or "",
            "sdk_source_path": launcher_path,
            "signature_source_path": launcher_path,
        }
    ]
    if not methods or not properties:
        raise RuntimeError(
            f"Unexpected PyAnsys Geometry extraction: methods={len(methods)}, properties={len(properties)}"
        )
    snapshot = {
        "module": CLASS_MODULE,
        "version": "unknown",
        "sdk_package": "ansys-geometry-core",
        "sdk_version": SDK_VERSION,
        "interface": "PyAnsys Geometry 0.17.1 Modeler and launch_modeler",
        "scope": (
            "範圍限於 Modeler 直接宣告的公開方法、屬性與 launch_modeler。"
            "本機同步文件為 0.18.2，版次不符而排除；以 AST 靜態讀取 SDK 0.17.1 source，"
            "不匯入套件、不建立 Modeler、不連線 geometry service。"
        ),
        "sources": {
            "sdk_files": [
                {"path": path.as_posix(), "sha256": _sha256(path)}
                for path in (modeler_source, launcher_source)
            ],
            "excluded_api_references": [_excluded_docs()],
        },
        "modules": {
            CLASS_MODULE: {
                "doc": ast.get_docstring(modeler_tree, clean=True) or "",
                "classes": {
                    CLASS_NAME: {
                        "name": CLASS_NAME,
                        "doc": ast.get_docstring(cls, clean=True) or "",
                        "methods": methods,
                        "properties": properties,
                    }
                },
                "functions": [],
            },
            LAUNCHER_MODULE: {
                "doc": ast.get_docstring(launcher_tree, clean=True) or "",
                "classes": {},
                "functions": functions,
            },
        },
        "statistics": {
            "total_modules": 2,
            "total_classes": 1,
            "total_methods": len(methods),
            "total_properties": len(properties),
            "total_functions": 1,
        },
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="geometry_core_api.", suffix=".tmp", dir=OUT_PATH.parent)
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
    result = extract_geometry_core_api()
    print(f"PyAnsys Geometry {SDK_VERSION}: {result['statistics']}")
