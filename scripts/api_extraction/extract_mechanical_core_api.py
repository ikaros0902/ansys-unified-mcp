"""以 AST 靜態擷取 PyMechanical 0.13.2 的 Mechanical client API。"""

from __future__ import annotations

import ast
import hashlib
import importlib.metadata
import json
import os
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = REPO_ROOT / "docs" / "api_inventory" / "mechanical_core_api.json"
SDK_VERSION = "0.13.2"
MODULE_NAME = "ansys.mechanical.core.mechanical"
CLASS_NAME = "Mechanical"
FUNCTION_NAMES = {"connect_to_mechanical", "launch_mechanical"}


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


def _members(cls: ast.ClassDef, source_path: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
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


def extract_mechanical_core_api() -> dict[str, Any]:
    actual_version = importlib.metadata.version("ansys-mechanical-core")
    if actual_version != SDK_VERSION:
        raise RuntimeError(f"Expected ansys-mechanical-core {SDK_VERSION}, found {actual_version}")
    source = Path(
        importlib.metadata.distribution("ansys-mechanical-core").locate_file(
            "ansys/mechanical/core/mechanical.py"
        )
    )
    if not source.is_file():
        raise FileNotFoundError(f"PyMechanical SDK source is missing: {source}")
    source_path = source.resolve().as_posix()
    module = ast.parse(source.read_text(encoding="utf-8"))
    cls = next(
        (item for item in module.body if isinstance(item, ast.ClassDef) and item.name == CLASS_NAME),
        None,
    )
    if cls is None:
        raise ValueError(f"Class not found in PyMechanical source: {CLASS_NAME}")
    methods, properties = _members(cls, source_path)
    functions = [
        {
            "name": item.name,
            "signature": _signature(item),
            "doc": ast.get_docstring(item, clean=True) or "",
            "sdk_source_path": source_path,
            "signature_source_path": source_path,
        }
        for item in module.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name in FUNCTION_NAMES
    ]
    if not methods or not properties or {item["name"] for item in functions} != FUNCTION_NAMES:
        raise RuntimeError(
            f"Unexpected PyMechanical extraction: methods={len(methods)}, "
            f"properties={len(properties)}, functions={[item['name'] for item in functions]}"
        )
    snapshot = {
        "module": MODULE_NAME,
        "version": "unknown",
        "sdk_package": "ansys-mechanical-core",
        "sdk_version": SDK_VERSION,
        "interface": "PyMechanical 0.13.2 Mechanical client and launch/connect functions",
        "scope": (
            "範圍限於 Mechanical client 直接宣告的公開方法、屬性及 launch_mechanical/connect_to_mechanical。"
            "本機同步 API reference 為 0.13.4，版次不符而排除；以 AST 靜態讀取 0.13.2 SDK source，"
            "不匯入套件、不連線、不啟動 Mechanical。"
        ),
        "sources": {"sdk_files": [{"path": source_path, "sha256": _sha256(source)}]},
        "modules": {
            MODULE_NAME: {
                "doc": ast.get_docstring(module, clean=True) or "",
                "classes": {
                    CLASS_NAME: {
                        "name": CLASS_NAME,
                        "doc": ast.get_docstring(cls, clean=True) or "",
                        "methods": methods,
                        "properties": properties,
                    }
                },
                "functions": functions,
            }
        },
        "statistics": {
            "total_modules": 1,
            "total_classes": 1,
            "total_methods": len(methods),
            "total_properties": len(properties),
            "total_functions": len(functions),
        },
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix="mechanical_core_api.", suffix=".tmp", dir=OUT_PATH.parent
    )
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
    result = extract_mechanical_core_api()
    print(f"PyMechanical {SDK_VERSION}: {result['statistics']}")
