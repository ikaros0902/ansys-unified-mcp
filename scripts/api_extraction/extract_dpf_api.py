"""擷取本機 PyDPF-Core 0.16.1 的有界核心資料類別快照。"""

from __future__ import annotations

import hashlib
import importlib.metadata
import inspect
import json
import os
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = REPO_ROOT / "docs" / "api_inventory" / "dpf_api.json"
SDK_VERSION = "0.16.1"
CLASS_MODULES = (
    ("ansys.dpf.core.model", "Model"),
    ("ansys.dpf.core.data_sources", "DataSources"),
    ("ansys.dpf.core.fields_container", "FieldsContainer"),
    ("ansys.dpf.core.field", "Field"),
    ("ansys.dpf.core.meshed_region", "MeshedRegion"),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_path(obj: Any) -> str | None:
    try:
        path = inspect.getsourcefile(obj)
    except (TypeError, OSError):
        return None
    return str(Path(path).resolve()) if path else None


def _extract_members(cls: type) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    methods = []
    properties = []
    for name, raw in cls.__dict__.items():
        if name.startswith("_"):
            continue
        value = raw.__func__ if isinstance(raw, (classmethod, staticmethod)) else raw
        if inspect.isfunction(value):
            try:
                signature = str(inspect.signature(value))
            except (TypeError, ValueError):
                continue
            methods.append(
                {
                    "name": name,
                    "signature": signature,
                    "doc": inspect.getdoc(value) or "",
                    "sdk_source_path": _source_path(value),
                    "signature_source_path": _source_path(inspect.unwrap(value)),
                }
            )
        elif isinstance(raw, property):
            getter = raw.fget
            if getter is None:
                continue
            try:
                signature = inspect.signature(getter)
            except (TypeError, ValueError):
                continue
            annotation = signature.return_annotation
            properties.append(
                {
                    "name": name,
                    "type": "" if annotation is inspect.Signature.empty else str(annotation),
                    "doc": inspect.getdoc(getter) or "",
                    "sdk_source_path": _source_path(getter),
                    "signature_source_path": _source_path(inspect.unwrap(getter)),
                }
            )
    return methods, properties


def extract_dpf_api() -> dict[str, Any]:
    if importlib.metadata.version("ansys-dpf-core") != SDK_VERSION:
        actual = importlib.metadata.version("ansys-dpf-core")
        raise RuntimeError(f"Expected ansys-dpf-core {SDK_VERSION}, found {actual}")

    from ansys.dpf.core import data_sources, field, fields_container, meshed_region, model

    modules = {
        "ansys.dpf.core.model": model,
        "ansys.dpf.core.data_sources": data_sources,
        "ansys.dpf.core.fields_container": fields_container,
        "ansys.dpf.core.field": field,
        "ansys.dpf.core.meshed_region": meshed_region,
    }
    sdk_files: set[Path] = set()
    output_modules: dict[str, Any] = {}
    total_methods = 0
    total_properties = 0

    for module_name, class_name in CLASS_MODULES:
        module = modules[module_name]
        cls = getattr(module, class_name)
        module_path = Path(module.__file__).resolve()
        sdk_files.add(module_path)
        methods, properties = _extract_members(cls)
        for member in methods + properties:
            for key in ("sdk_source_path", "signature_source_path"):
                if member.get(key):
                    sdk_files.add(Path(member[key]))
        output_modules[module_name] = {
            "doc": inspect.getdoc(module) or "",
            "classes": {
                class_name: {
                    "name": class_name,
                    "doc": inspect.getdoc(cls) or "",
                    "methods": methods,
                    "properties": properties,
                }
            },
            "functions": [],
        }
        total_methods += len(methods)
        total_properties += len(properties)

    if total_methods == 0 or total_properties == 0:
        raise RuntimeError(
            f"Unexpected DPF API extraction result: methods={total_methods}, properties={total_properties}"
        )

    snapshot = {
        "module": "ansys.dpf.core",
        "version": "unknown",
        "sdk_package": "ansys-dpf-core",
        "sdk_version": SDK_VERSION,
        "interface": "PyDPF-Core 0.16.1 core data classes",
        "scope": (
            "範圍限於 Model、DataSources、FieldsContainer、Field、MeshedRegion 五個類別直接宣告的公開方法與屬性。"
            "不含繼承成員、動態產生的 operators、其他模組、伺服器行為及 0.16.3 文件語料。"
        ),
        "sources": {
            "sdk_files": [
                {"path": path.as_posix(), "sha256": _sha256(path)} for path in sorted(sdk_files)
            ]
        },
        "modules": output_modules,
        "statistics": {
            "total_modules": len(output_modules),
            "total_classes": len(CLASS_MODULES),
            "total_methods": total_methods,
            "total_properties": total_properties,
            "total_functions": 0,
        },
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="dpf_api.", suffix=".tmp", dir=OUT_PATH.parent)
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
    result = extract_dpf_api()
    print(f"PyDPF-Core {SDK_VERSION}: {result['statistics']}")
