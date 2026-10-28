"""擷取本機 PyAnsys product gRPC/protobuf schema snapshots。"""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import json
import os
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "api_inventory"
PRODUCT_APIS = {
    "mechanical": ("ansys-api-mechanical", "0.1.4"),
    "geometry": ("ansys-api-geometry", "0.4.92"),
    "fluent": ("ansys-api-fluent", "0.6.0"),
    "mapdl": ("ansys-api-mapdl", "0.6.0"),
    "primemesh": ("ansys-api-meshing-prime", "0.2.0"),
    "discovery": ("ansys-api-discovery", "1.2.12"),
    "dbu": ("ansys-api-dbu", "0.3.29"),
    "result_explorer": ("ansys-api-result-explorer", "0.1.1"),
    "platform_instance_management": ("ansys-api-platform-instancemanagement", "1.2.0"),
    "filetransfer": ("ansys-api-tools-filetransfer", "0.2.0"),
}
FIELD_TYPES = {
    1: "double", 2: "float", 3: "int64", 4: "uint64", 5: "int32", 6: "fixed64",
    7: "fixed32", 8: "bool", 9: "string", 10: "group", 11: "message", 12: "bytes",
    13: "uint32", 14: "enum", 15: "sfixed32", 16: "sfixed64", 17: "sint32", 18: "sint64",
}


def _field_type(field: Any) -> str:
    if field.message_type:
        return field.message_type.full_name
    if field.enum_type:
        return field.enum_type.full_name
    return FIELD_TYPES.get(field.type, f"protobuf_type_{field.type}")


def _snapshot(product: str, package: str, version: str) -> dict[str, Any]:
    distribution = importlib.metadata.distribution(package)
    modules = {}
    source_paths: set[Path] = set()
    counts = {"total_modules": 0, "total_classes": 0, "total_methods": 0, "total_properties": 0}
    for package_file in sorted(distribution.files or []):
        path = PurePosixPath(package_file.as_posix())
        if path.suffix != ".py" or not path.stem.endswith("_pb2") or path.stem.endswith("_pb2_grpc"):
            continue
        module_name = path.with_suffix("").as_posix().replace("/", ".")
        module = importlib.import_module(module_name)
        descriptor = getattr(module, "DESCRIPTOR", None)
        if descriptor is None:
            continue
        classes = {}
        for message in descriptor.message_types_by_name.values():
            fields = [
                {
                    "name": field.name,
                    "type": _field_type(field),
                    "doc": f"Protobuf field number {field.number}; repeated={field.is_repeated}",
                }
                for field in message.fields
            ]
            counts["total_properties"] += len(fields)
            classes[message.name] = {
                "name": message.name,
                "doc": f"Protocol message {message.full_name}",
                "methods": [],
                "properties": fields,
            }
        for service in descriptor.services_by_name.values():
            methods = [
                {
                    "name": method.name,
                    "signature": (
                        f"({method.input_type.full_name}) -> {method.output_type.full_name} "
                        f"[client_streaming={method.client_streaming}, "
                        f"server_streaming={method.server_streaming}]"
                    ),
                    "doc": "gRPC method declared by the protobuf service descriptor.",
                }
                for method in service.methods
            ]
            counts["total_methods"] += len(methods)
            classes[service.name] = {
                "name": service.name,
                "doc": f"gRPC service {service.full_name}",
                "methods": methods,
                "properties": [],
            }
        source = Path(module.__file__).resolve()
        source_paths.add(source)
        counts["total_modules"] += 1
        counts["total_classes"] += len(classes)
        modules[module_name] = {"doc": descriptor.package, "classes": classes, "functions": []}

    if not modules:
        raise RuntimeError(f"No protobuf descriptor modules found in {package} {version}")
    return {
        "module": "generated protobuf modules",
        "version": "unknown",
        "sdk_package": package,
        "sdk_version": version,
        "interface": f"{product} gRPC protocol schema",
        "scope": (
            "限於套件內 protobuf message 欄位與 gRPC service RPC signatures。"
            "這是傳輸協定 schema，不是產品 scripting API 或支援狀態聲明。"
        ),
        "sources": {
            "sdk_files": [
                {"path": source.as_posix(), "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
                for source in sorted(source_paths)
            ]
        },
        "modules": modules,
        "statistics": {**counts, "total_functions": 0},
    }


def extract_product_protocol_apis() -> dict[str, Any]:
    snapshots = {}
    for product, (package, expected_version) in PRODUCT_APIS.items():
        version = importlib.metadata.version(package)
        if version != expected_version:
            raise RuntimeError(f"Expected {package} {expected_version}, found {version}")
        snapshots[product] = _snapshot(product, package, version)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for product, snapshot in snapshots.items():
        output = OUT_DIR / f"{product}_protocol_api.json"
        fd, temp_name = tempfile.mkstemp(prefix=f"{product}_protocol_api.", suffix=".tmp", dir=OUT_DIR)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
                json.dump(snapshot, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, output)
        except BaseException:
            Path(temp_name).unlink(missing_ok=True)
            raise

    aggregate = {key: sum(snapshot["statistics"][key] for snapshot in snapshots.values())
                 for key in ("total_modules", "total_classes", "total_methods", "total_properties", "total_functions")}
    return {"products": snapshots, "statistics": aggregate}


if __name__ == "__main__":
    results = extract_product_protocol_apis()
    for product, snapshot in results["products"].items():
        print(product, snapshot["sdk_version"], snapshot["statistics"])
