"""擷取本機 PyFluent 0.42.1 文件列出的 launcher 入口。"""

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
OUT_PATH = REPO_ROOT / "docs" / "api_inventory" / "fluent_api.json"
SDK_VERSION = "0.42.1"
FUNCTION_NAMES = ("connect_to_fluent", "launch_fluent")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_path(obj: Any) -> str | None:
    try:
        path = inspect.getsourcefile(obj)
    except (TypeError, OSError):
        return None
    return str(Path(path).resolve()) if path else None


def _function_record(name: str, function: Any) -> dict[str, str]:
    try:
        signature = str(inspect.signature(function))
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Could not read {name} signature") from exc
    source_path = _source_path(function)
    signature_source_path = _source_path(inspect.unwrap(function))
    if not source_path or not signature_source_path:
        raise RuntimeError(f"Could not locate {name} SDK source")
    return {
        "name": name,
        "signature": signature,
        "doc": inspect.getdoc(function) or "",
        "sdk_source_path": source_path,
        "signature_source_path": signature_source_path,
    }


def extract_fluent_api() -> dict[str, Any]:
    actual_version = importlib.metadata.version("ansys-fluent-core")
    if actual_version != SDK_VERSION:
        raise RuntimeError(f"Expected ansys-fluent-core {SDK_VERSION}, found {actual_version}")

    public_api = importlib.import_module("ansys.fluent.core")
    launcher = importlib.import_module("ansys.fluent.core.launcher.launcher")
    functions = {
        "connect_to_fluent": getattr(launcher, "connect_to_fluent"),
        "launch_fluent": getattr(public_api, "launch_fluent"),
    }
    if any(not inspect.isfunction(function) for function in functions.values()):
        raise RuntimeError("Expected PyFluent launcher exports to be functions")
    records = [_function_record(name, functions[name]) for name in FUNCTION_NAMES]
    sdk_files = {Path(public_api.__file__).resolve(), Path(launcher.__file__).resolve()}
    sdk_files.update(
        Path(record[key])
        for record in records
        for key in ("sdk_source_path", "signature_source_path")
    )

    snapshot = {
        "module": "ansys.fluent.core.launcher.launcher",
        "version": "unknown",
        "sdk_package": "ansys-fluent-core",
        "sdk_version": SDK_VERSION,
        "interface": "PyFluent 0.42.1 launcher functions",
        "scope": (
            "範圍限於本機 0.42.1 SDK 中的 connect_to_fluent 與 launch_fluent。"
            "本機同步文件目錄中的 launcher HTML 標示 0.40.3，不作為 0.42.1 版本證據。"
            "擷取只讀取函式 docstring、簽章與來源 hash，不呼叫函式、不啟動 Fluent 或建立連線。"
        ),
        "sources": {
            "sdk_files": [
                {"path": path.as_posix(), "sha256": _sha256(path)} for path in sorted(sdk_files)
            ],
        },
        "modules": {
            "ansys.fluent.core.launcher.launcher": {
                "doc": inspect.getdoc(launcher) or "",
                "classes": {},
                "functions": records,
            }
        },
        "statistics": {"total_modules": 1, "total_functions": len(records)},
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="fluent_api.", suffix=".tmp", dir=OUT_PATH.parent)
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
    result = extract_fluent_api()
    print(f"PyFluent {SDK_VERSION}: {result['statistics']}")
