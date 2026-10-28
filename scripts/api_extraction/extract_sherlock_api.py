"""以 AST 靜態擷取已安裝 PyAnsys Sherlock SDK 的直接宣告。"""

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
OUT_PATH = REPO_ROOT / "docs" / "api_inventory" / "sherlock_core_api.json"
SDK_PACKAGE = "ansys-sherlock-core"
SDK_VERSION = "2.1.4"
PACKAGE_ROOT = Path("ansys/sherlock/core")


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


def _digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def _class_members(
    cls: ast.ClassDef, source_path: str
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    methods = []
    properties = []
    for item in cls.body:
        if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) or item.name.startswith("_"):
            continue
        decorators = [ast.unparse(decorator) for decorator in item.decorator_list]
        if any(name.endswith((".setter", ".getter", ".deleter")) for name in decorators):
            continue
        member = {
            "name": item.name,
            "doc": ast.get_docstring(item, clean=True) or "",
            "sdk_source_path": source_path,
            "signature_source_path": source_path,
        }
        if any(name == "property" or name.endswith(".property") for name in decorators):
            member["type"] = ast.unparse(item.returns) if item.returns else ""
            properties.append(member)
        else:
            member["signature"] = _signature(item)
            methods.append(member)
    return methods, properties


def extract_sherlock_api() -> dict[str, Any]:
    distribution = importlib.metadata.distribution(SDK_PACKAGE)
    if distribution.version != SDK_VERSION:
        raise RuntimeError(
            f"Expected {SDK_PACKAGE} {SDK_VERSION}, found {distribution.version}"
        )

    package_path = Path(distribution.locate_file(PACKAGE_ROOT)).resolve()
    source_files = sorted(package_path.rglob("*.py"))
    if not source_files:
        raise FileNotFoundError(f"No Python source files found under {package_path}")

    modules: dict[str, dict[str, Any]] = {}
    totals = {"total_modules": 0, "total_classes": 0, "total_methods": 0,
              "total_properties": 0, "total_functions": 0}
    sdk_files = []
    for source in source_files:
        source_path = source.as_posix()
        relative = source.relative_to(package_path).as_posix()
        suffix = relative.removesuffix(".py").replace("/", ".")
        module_name = "ansys.sherlock.core" + ("." + suffix.removesuffix(".__init__") if suffix != "__init__" else "")
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=source_path)
        classes: dict[str, dict[str, Any]] = {}
        functions = []
        for item in tree.body:
            if isinstance(item, ast.ClassDef) and not item.name.startswith("_"):
                methods, properties = _class_members(item, source_path)
                classes[item.name] = {
                    "name": item.name,
                    "doc": ast.get_docstring(item, clean=True) or "",
                    "methods": methods,
                    "properties": properties,
                    "sdk_source_path": source_path,
                }
                totals["total_classes"] += 1
                totals["total_methods"] += len(methods)
                totals["total_properties"] += len(properties)
            elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and not item.name.startswith("_"):
                functions.append({
                    "name": item.name,
                    "signature": _signature(item),
                    "doc": ast.get_docstring(item, clean=True) or "",
                    "sdk_source_path": source_path,
                    "signature_source_path": source_path,
                })
                totals["total_functions"] += 1
        modules[module_name] = {
            "doc": ast.get_docstring(tree, clean=True) or "",
            "classes": classes,
            "functions": functions,
        }
        totals["total_modules"] += 1
        sdk_files.append({"path": source_path, "sha256": _digest(source)})

    if not any(totals[key] for key in ("total_classes", "total_methods", "total_functions")):
        raise RuntimeError("The Sherlock SDK source contains no direct public declarations")

    snapshot = {
        "module": "ansys.sherlock.core",
        "version": "unknown",
        "sdk_package": SDK_PACKAGE,
        "sdk_version": SDK_VERSION,
        "interface": "PyAnsys Sherlock SDK 2.1.4",
        "scope": (
            "靜態 AST 擷取 ansys.sherlock.core 原始碼中直接宣告且名稱不以底線開頭的類別、方法、"
            "屬性與函式。不匯入套件、不解析 __all__ re-export、不連線 Sherlock 或執行 ANSYS。"
            "此快照不等同官方支援 API 清單。"
        ),
        "sources": {"sdk_files": sdk_files},
        "modules": modules,
        "statistics": totals,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="sherlock_core_api.", suffix=".tmp", dir=OUT_PATH.parent)
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
    result = extract_sherlock_api()
    print(json.dumps(result["statistics"], ensure_ascii=False))
