"""僅擷取官方文件連結的 PyMAPDL 用戶端範圍，不啟動求解器。"""

from __future__ import annotations

import hashlib
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
    REPO_ROOT / "ANSYS_Document" / "MAPDL" / "sdk" / "ansys-mapdl-core" / "0.74.1" / "api_reference"
)
DOC_INDEX = DOC_DIR / "09d55e454222-mapdl.md"
OUT_PATH = REPO_ROOT / "docs" / "api_inventory" / "mapdl_api.json"
DOC_URL = "https://mapdl.docs.pyansys.com/version/stable/api/mapdl.html"
UNRESOLVED = {
    "finish_job_on_exit": "由 MapdlGrpc.__init__ 設定的 instance 屬性，不是 class descriptor。",
    "remove_temp_dir_on_exit": "由 MapdlGrpc.__init__ 設定的 instance 屬性，不是 class descriptor。",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _annotation(value: Any) -> str:
    return "" if value is inspect.Signature.empty else str(value)


def _source_path(target: Any) -> str:
    try:
        path = inspect.getsourcefile(target)
    except TypeError:
        path = None
    return Path(path).resolve().as_posix() if path else ""


def _signature_source_path(target: Any) -> str:
    try:
        target = inspect.unwrap(target)
    except ValueError:
        return ""
    return _source_path(target)


def _extract_class_members(
    cls: type, names: list[str], links: dict[str, str]
) -> tuple[list[dict], list[dict], list[dict]]:
    methods = []
    properties = []
    unresolved = []
    for name in names:
        member = inspect.getattr_static(cls, name, None)
        if member is None:
            unresolved.append(
                {
                    "name": name,
                    "doc_url": links[name],
                    "reason": UNRESOLVED.get(name, "無法由 class 靜態成員解析。"),
                }
            )
        elif isinstance(member, property):
            getter = member.fget
            annotation = (
                inspect.signature(getter).return_annotation if getter else inspect.Signature.empty
            )
            properties.append(
                {
                    "name": name,
                    "type": _annotation(annotation),
                    "doc": inspect.getdoc(member) or "",
                    "doc_url": links[name],
                    "sdk_source_path": _source_path(getter) if getter else "",
                    "signature_source_path": _signature_source_path(getter) if getter else "",
                }
            )
        else:
            target = member.__func__ if isinstance(member, (staticmethod, classmethod)) else member
            source_path = _source_path(target)
            if not callable(target):
                properties.append(
                    {
                        "name": name,
                        "type": type(target).__name__,
                        "doc": inspect.getdoc(target) or "",
                        "doc_url": links[name],
                        "sdk_source_path": source_path,
                        "signature_source_path": source_path,
                    }
                )
                continue
            signature_source_path = _signature_source_path(target)
            try:
                signature = str(inspect.signature(target))
            except (TypeError, ValueError):
                signature = ""
            methods.append(
                {
                    "name": name,
                    "signature": signature,
                    "doc": inspect.getdoc(target) or "",
                    "doc_url": links[name],
                    "sdk_source_path": source_path,
                    "signature_source_path": signature_source_path,
                }
            )
    return methods, properties, unresolved


def extract_mapdl_api() -> dict[str, Any]:
    if not DOC_INDEX.is_file():
        raise FileNotFoundError(f"PyMAPDL API reference is missing: {DOC_INDEX}")

    from ansys.mapdl.core.mapdl_grpc import MapdlGrpc
    from ansys.mapdl.core.launcher import launch_mapdl

    page = DOC_INDEX.read_text(encoding="utf-8")
    links = {
        name: url
        for name, url in re.findall(r"\[Mapdl\.([A-Za-z][A-Za-z0-9_]*)\]\((https?://[^)]+)\)", page)
    }
    if len(links) != 67:
        raise RuntimeError(f"Expected 67 documented Mapdl members, found {len(links)}")

    methods, properties, unresolved = _extract_class_members(MapdlGrpc, sorted(links), links)
    if not methods or not properties or len(unresolved) != 2:
        raise RuntimeError(
            f"Unexpected MapdlGrpc extraction result: methods={len(methods)}, properties={len(properties)}, unresolved={len(unresolved)}"
        )

    launcher_path = Path(inspect.getsourcefile(launch_mapdl)).resolve()
    grpc_path = Path(inspect.getsourcefile(MapdlGrpc)).resolve()
    sdk_source_paths = {grpc_path, launcher_path}
    sdk_source_paths.update(
        Path(member[key])
        for member in methods + properties
        for key in ("sdk_source_path", "signature_source_path")
        if member.get(key)
    )
    sdk_version = importlib.metadata.version("ansys-mapdl-core")
    if sdk_version != "0.74.1":
        raise RuntimeError(f"Expected ansys-mapdl-core 0.74.1, found {sdk_version}")
    try:
        launch_signature = str(inspect.signature(launch_mapdl))
    except (TypeError, ValueError) as exc:
        raise RuntimeError("Could not read launch_mapdl signature") from exc
    launch_signature_source_path = _signature_source_path(launch_mapdl)
    if not launch_signature_source_path:
        raise RuntimeError("Could not locate the unwrapped launch_mapdl signature source")
    sdk_source_paths.add(Path(launch_signature_source_path))

    snapshot = {
        "module": "ansys.mapdl.core",
        "version": "unknown",
        "sdk_package": "ansys-mapdl-core",
        "sdk_version": sdk_version,
        "interface": "PyMAPDL 文件列出的 MapdlGrpc client 與 launch_mapdl 入口",
        "scope": "範圍只包含本機 PyMAPDL API reference 連結的 Mapdl.* 成員與 launch_mapdl。APDL 動態命令、其他類別／模組及未列文件的成員不在範圍內。",
        "sources": {
            "api_reference": {
                "path": DOC_INDEX.relative_to(REPO_ROOT).as_posix(),
                "url": DOC_URL,
                "sha256": _sha256(DOC_INDEX),
            },
            "sdk_files": [
                {"path": path.as_posix(), "sha256": _sha256(path)}
                for path in sorted(sdk_source_paths)
            ],
        },
        "unresolved_members": unresolved,
        "modules": {
            "ansys.mapdl.core.mapdl_grpc": {
                "doc": "PyMAPDL gRPC client API.",
                "classes": {
                    "MapdlGrpc": {
                        "name": "MapdlGrpc",
                        "doc": inspect.getdoc(MapdlGrpc) or "",
                        "methods": methods,
                        "properties": properties,
                    }
                },
                "functions": [],
            },
            "ansys.mapdl.core.launcher": {
                "doc": "PyMAPDL launcher entry point.",
                "classes": {},
                "functions": [
                    {
                        "name": "launch_mapdl",
                        "signature": launch_signature,
                        "doc": inspect.getdoc(launch_mapdl) or "",
                        "sdk_source_path": _source_path(launch_mapdl),
                        "signature_source_path": launch_signature_source_path,
                    }
                ],
            },
        },
        "statistics": {
            "total_classes": 1,
            "total_methods": len(methods),
            "total_properties": len(properties),
            "total_functions": 1,
            "unresolved_members": len(unresolved),
        },
    }
    if len(methods) != 27 or len(properties) != 38:
        raise RuntimeError(
            f"Unexpected PyMAPDL member counts: methods={len(methods)}, properties={len(properties)}"
        )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="mapdl_api.", suffix=".tmp", dir=OUT_PATH.parent)
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
    data = extract_mapdl_api()
    print(f"PyMAPDL API snapshot written: {OUT_PATH} ({data['statistics']})")
