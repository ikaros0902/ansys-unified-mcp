"""擷取本機 PyAnsys Sound 0.3.0 的 SoundComposer 與 Track API。"""

from __future__ import annotations

import hashlib
import importlib
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
    REPO_ROOT
    / "ANSYS_Document"
    / "Sound"
    / "sdk"
    / "ansys-sound-core"
    / "0.3.0"
    / "api_reference"
)
OUT_PATH = REPO_ROOT / "docs" / "api_inventory" / "sound_api.json"
SDK_VERSION = "0.3.0"
DOC_NAMES = {
    "sound_composer": "9b45b05a8ead-sound_composer",
    "SoundComposer": "5c7582a9a7e5-ansys.sound.core.sound_composer.SoundComposer",
    "Track": "fc1adb720f35-ansys.sound.core.sound_composer.Track",
}
CLASS_MODULES = (
    ("ansys.sound.core.sound_composer.sound_composer", "SoundComposer"),
    ("ansys.sound.core.sound_composer.track", "Track"),
)
DOC_VERSION = re.compile(r'<meta name="docsearch:version" content="([^"]+)"')
SOURCE_URL = re.compile(r"^source_url:\s*(https?://\S+)$", re.MULTILINE)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_path(obj: Any) -> str | None:
    try:
        path = inspect.getsourcefile(obj)
    except (TypeError, OSError):
        return None
    return str(Path(path).resolve()) if path else None


def _extract_class_members(cls: type) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    methods = []
    properties = []
    for name, raw in cls.__dict__.items():
        if name.startswith("_"):
            continue
        value = raw.__func__ if isinstance(raw, (classmethod, staticmethod)) else raw
        if inspect.isfunction(value):
            signature = str(inspect.signature(value))
            methods.append(
                {
                    "name": name,
                    "signature": signature,
                    "doc": inspect.getdoc(value) or "",
                    "sdk_source_path": _source_path(value) or "",
                    "signature_source_path": _source_path(inspect.unwrap(value)) or "",
                }
            )
        elif isinstance(raw, property) and raw.fget is not None:
            getter = raw.fget
            signature = inspect.signature(getter)
            annotation = signature.return_annotation
            properties.append(
                {
                    "name": name,
                    "type": "" if annotation is inspect.Signature.empty else str(annotation),
                    "doc": inspect.getdoc(getter) or "",
                    "sdk_source_path": _source_path(getter) or "",
                    "signature_source_path": _source_path(inspect.unwrap(getter)) or "",
                }
            )
    return methods, properties


def _doc_evidence(label: str, stem: str) -> dict[str, str]:
    markdown = DOC_DIR / f"{stem}.md"
    html = DOC_DIR / f"{stem}.html"
    if not markdown.is_file() or not html.is_file():
        raise FileNotFoundError(f"PyAnsys Sound API reference is missing for {label}")
    html_text = html.read_text(encoding="utf-8")
    match = DOC_VERSION.search(html_text)
    if not match or match.group(1) != SDK_VERSION:
        raise RuntimeError(f"Expected {label} docs {SDK_VERSION}, found {match.group(1) if match else 'unknown'}")
    markdown_text = markdown.read_text(encoding="utf-8")
    url = SOURCE_URL.search(markdown_text)
    if not url:
        raise RuntimeError(f"PyAnsys Sound API reference has no source URL: {markdown}")
    return {
        "name": label,
        "path": markdown.relative_to(REPO_ROOT).as_posix(),
        "url": url.group(1),
        "sha256": _sha256(markdown),
        "html_path": html.relative_to(REPO_ROOT).as_posix(),
        "html_sha256": _sha256(html),
        "html_version": match.group(1),
    }


def extract_sound_api() -> dict[str, Any]:
    actual_version = importlib.metadata.version("ansys-sound-core")
    if actual_version != SDK_VERSION:
        raise RuntimeError(f"Expected ansys-sound-core {SDK_VERSION}, found {actual_version}")

    references = [_doc_evidence(name, stem) for name, stem in DOC_NAMES.items()]
    output_modules: dict[str, Any] = {}
    sdk_files: set[Path] = set()
    total_methods = 0
    total_properties = 0
    for module_name, class_name in CLASS_MODULES:
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        methods, properties = _extract_class_members(cls)
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
        sdk_files.add(Path(module.__file__).resolve())
        sdk_files.update(
            Path(item[key])
            for item in methods + properties
            for key in ("sdk_source_path", "signature_source_path")
            if item.get(key)
        )
        total_methods += len(methods)
        total_properties += len(properties)

    if total_methods == 0 or total_properties == 0:
        raise RuntimeError(
            f"Unexpected PyAnsys Sound extraction result: methods={total_methods}, properties={total_properties}"
        )
    snapshot = {
        "module": "ansys.sound.core.sound_composer",
        "version": "unknown",
        "sdk_package": "ansys-sound-core",
        "sdk_version": SDK_VERSION,
        "interface": "PyAnsys Sound 0.3.0 SoundComposer and Track",
        "scope": (
            "範圍限於 SoundComposer 與 Track 直接宣告的公開方法與屬性，不含繼承成員及其他 Sound modules。"
            "擷取只讀取 SDK 與已核對 0.3.0 的 API reference；不建立物件、不處理訊號、不呼叫 server。"
        ),
        "sources": {
            "api_references": references,
            "sdk_files": [
                {"path": path.as_posix(), "sha256": _sha256(path)} for path in sorted(sdk_files)
            ],
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
    fd, temp_name = tempfile.mkstemp(prefix="sound_api.", suffix=".tmp", dir=OUT_PATH.parent)
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
    result = extract_sound_api()
    print(f"PyAnsys Sound {SDK_VERSION}: {result['statistics']}")
