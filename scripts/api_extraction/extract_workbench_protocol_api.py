"""擷取 ansys-api-workbench 0.4.0 的 gRPC service 與 protobuf 訊息 schema。"""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import json
import os
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = REPO_ROOT / "docs" / "api_inventory" / "workbench_protocol_api.json"
SDK_PACKAGE = "ansys-api-workbench"
SDK_VERSION = "0.4.0"
MODULE_NAME = "ansys.api.workbench.v0.workbench_pb2"
GRPC_MODULE_NAME = "ansys.api.workbench.v0.workbench_pb2_grpc"


def _field_type(field: Any) -> str:
    if field.message_type:
        return field.message_type.full_name
    if field.enum_type:
        return field.enum_type.full_name
    return {1: "double", 2: "float", 3: "int64", 4: "uint64", 5: "int32", 6: "fixed64", 7: "fixed32", 8: "bool", 9: "string", 10: "group", 11: "message", 12: "bytes", 13: "uint32", 14: "enum", 15: "sfixed32", 16: "sfixed64", 17: "sint32", 18: "sint64"}.get(field.type, f"protobuf_type_{field.type}")


def extract_workbench_protocol_api() -> dict[str, Any]:
    actual_version = importlib.metadata.version(SDK_PACKAGE)
    if actual_version != SDK_VERSION:
        raise RuntimeError(f"Expected {SDK_PACKAGE} {SDK_VERSION}, found {actual_version}")

    module = importlib.import_module(MODULE_NAME)
    grpc_module = importlib.import_module(GRPC_MODULE_NAME)
    descriptor = module.DESCRIPTOR
    classes: dict[str, dict[str, Any]] = {}
    methods_count = properties_count = 0

    for message in descriptor.message_types_by_name.values():
        properties = [
            {
                "name": field.name,
                "type": _field_type(field),
                "doc": f"Protobuf field number {field.number}; repeated={field.is_repeated}",
            }
            for field in message.fields
        ]
        properties_count += len(properties)
        classes[message.name] = {
            "name": message.name,
            "doc": f"Protocol message {message.full_name}",
            "methods": [],
            "properties": properties,
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
        methods_count += len(methods)
        classes[service.name] = {
            "name": service.name,
            "doc": f"gRPC service {service.full_name}",
            "methods": methods,
            "properties": [],
        }

    source_paths = [Path(module.__file__).resolve(), Path(grpc_module.__file__).resolve()]
    sources = [
        {
            "path": path.as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in sorted(set(source_paths))
        if path.is_file()
    ]
    snapshot = {
        "module": MODULE_NAME,
        "version": "unknown",
        "sdk_package": SDK_PACKAGE,
        "sdk_version": SDK_VERSION,
        "interface": "Workbench gRPC protocol schema",
        "scope": (
            "僅記錄 protobuf message 欄位與 gRPC service RPC signatures。"
            "這是傳輸協定 schema，不是 Workbench Python scripting API 或支援狀態聲明。"
        ),
        "sources": {"sdk_files": sources},
        "modules": {
            MODULE_NAME: {
                "doc": descriptor.package,
                "classes": classes,
                "functions": [],
            }
        },
        "statistics": {
            "total_modules": 1,
            "total_classes": len(classes),
            "total_methods": methods_count,
            "total_properties": properties_count,
            "total_functions": 0,
        },
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="workbench_protocol_api.", suffix=".tmp", dir=OUT_PATH.parent)
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
    result = extract_workbench_protocol_api()
    print(f"Workbench protocol {SDK_VERSION}: {result['statistics']}")
