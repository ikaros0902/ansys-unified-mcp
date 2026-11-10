"""擷取本機 ansys-workbench-core 0.14.0 的公開匯出與 Python signatures。"""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import inspect
import json
import os
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = REPO_ROOT / "docs" / "api_inventory" / "workbench_api.json"
SDK_PACKAGE = "ansys-workbench-core"
SDK_VERSION = "0.14.0"
MODULE_NAMES = ("ansys.workbench.core", "ansys.workbench.core.public_api")


def _source_file(obj: Any) -> Path | None:
    try:
        source = inspect.getsourcefile(obj)
    except (TypeError, OSError):
        return None
    return Path(source).resolve() if source else None


def _callable_info(name: str, obj: Any) -> dict[str, str]:
    try:
        signature = str(inspect.signature(obj))
    except (TypeError, ValueError):
        signature = ""
    source = _source_file(obj)
    return {
        "name": name,
        "signature": signature,
        "doc": inspect.getdoc(obj) or "",
        "sdk_source_path": str(source) if source else "",
        "signature_source_path": str(source) if source else "",
    }


def _extract_module(module_name: str) -> tuple[dict[str, Any], set[Path]]:
    module = importlib.import_module(module_name)
    functions: list[dict[str, str]] = []
    classes: dict[str, dict[str, Any]] = {}
    source_files = {_source_file(module)}
    for name, obj in vars(module).items():
        if name.startswith("_") or not (inspect.isclass(obj) or inspect.isfunction(obj)):
            continue
        source = _source_file(obj)
        if source:
            source_files.add(source)
        if inspect.isfunction(obj):
            functions.append(_callable_info(name, obj))
            continue
        methods = []
        properties = []
        for member_name, raw in vars(obj).items():
            if member_name.startswith("_"):
                continue
            value = raw.__func__ if isinstance(raw, (classmethod, staticmethod)) else raw
            if inspect.isfunction(value):
                methods.append(_callable_info(member_name, value))
            elif isinstance(raw, property) and raw.fget:
                properties.append(
                    {
                        "name": member_name,
                        "type": "",
                        "doc": inspect.getdoc(raw.fget) or "",
                        "sdk_source_path": str(_source_file(raw.fget) or ""),
                        "signature_source_path": str(_source_file(raw.fget) or ""),
                    }
                )
        classes[name] = {
            "name": name,
            "signature": _callable_info(name, obj)["signature"],
            "doc": inspect.getdoc(obj) or "",
            "methods": methods,
            "properties": properties,
        }
    source_files.discard(None)
    return (
        {
            "doc": inspect.getdoc(module) or "",
            "classes": classes,
            "functions": functions,
        },
        source_files,
    )


def extract_workbench_api() -> dict[str, Any]:
    actual_version = importlib.metadata.version(SDK_PACKAGE)
    if actual_version != SDK_VERSION:
        raise RuntimeError(f"Expected {SDK_PACKAGE} {SDK_VERSION}, found {actual_version}")

    modules = {}
    source_files: set[Path] = set()
    total_classes = total_methods = total_properties = total_functions = 0
    for module_name in MODULE_NAMES:
        module_info, module_sources = _extract_module(module_name)
        modules[module_name] = module_info
        source_files.update(module_sources)
        total_classes += len(module_info["classes"])
        total_functions += len(module_info["functions"])
        for cls in module_info["classes"].values():
            total_methods += len(cls["methods"])
            total_properties += len(cls["properties"])

    snapshot = {
        "module": "ansys.workbench.core",
        "version": "unknown",
        "sdk_package": SDK_PACKAGE,
        "sdk_version": SDK_VERSION,
        "interface": "PyWorkbench public module exports",
        "scope": (
            "限於兩個模組直接匯出的 Python 函式、類別及類別直接宣告的公開方法與屬性。"
            "不含繼承成員、動態介面、產品宿主行為或官方支援分類。"
        ),
        "sources": {
            "sdk_files": [
                {
                    "path": path.as_posix(),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
                for path in sorted(source_files)
                if path.is_file()
            ]
        },
        "modules": modules,
        "statistics": {
            "total_modules": len(modules),
            "total_classes": total_classes,
            "total_methods": total_methods,
            "total_properties": total_properties,
            "total_functions": total_functions,
        },
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="workbench_api.", suffix=".tmp", dir=OUT_PATH.parent)
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
    result = extract_workbench_api()
    print(f"PyWorkbench {SDK_VERSION}: {result['statistics']}")
