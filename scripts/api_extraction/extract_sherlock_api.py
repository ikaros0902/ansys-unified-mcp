"""以 AST 靜態擷取已安裝 PyAnsys SDK 的直接宣告。"""

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
SDK_TARGETS = {
    "sherlock_core": {
        "package": "ansys-sherlock-core",
        "version": "2.1.4",
        "package_root": Path("ansys/sherlock/core"),
        "module_root": "ansys.sherlock.core",
        "interface": "PyAnsys Sherlock SDK 2.1.4",
    },
    "rocky": {
        "package": "ansys-rocky-core",
        "version": "0.6.2",
        "package_root": Path("ansys/rocky/core"),
        "module_root": "ansys.rocky.core",
        "interface": "PyAnsys Rocky SDK 0.6.2",
    },
    "cfx": {
        "package": "ansys-cfx-core",
        "version": "0.3.0",
        "package_root": Path("ansys/cfx/core"),
        "module_root": "ansys.cfx.core",
        "interface": "PyAnsys CFX SDK 0.3.0 direct AST declarations",
        "scope_note": (
            "CFX flobject and TUI interfaces use dynamic attribute resolution and are not "
            "represented by this direct AST snapshot."
        ),
        "include_distribution_metadata": True,
        "support_statement_marker": "PyCFX supports CFX ",
    },
    "speos": {
        "package": "ansys-speos-core",
        "version": "0.9.2",
        "package_root": Path("ansys/speos/core"),
        "module_root": "ansys.speos.core",
        "interface": "PyAnsys Speos SDK 0.9.2 direct AST declarations",
        "scope_note": (
            "This snapshot covers the Python client source only. The package metadata README "
            "shows conflicting product-version examples (2025.1, Docker tag 261, and local "
            "AWP_ROOT251 paths), so it does not establish product compatibility. The RPC "
            "schema is provided by a separate ansys-api-speos package."
        ),
        "include_distribution_metadata": True,
        "metadata_evidence_markers": (
            "product version 2025.1",
            "ghcr.io/ansys/speos-rpc:261",
            "%AWP_ROOT251%",
        ),
    },
}


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


def extract_python_sdk_api(target: str) -> dict[str, Any]:
    if target not in SDK_TARGETS:
        raise ValueError(f"Unsupported SDK target: {target}")

    config = SDK_TARGETS[target]
    package = config["package"]
    version = config["version"]
    distribution = importlib.metadata.distribution(package)
    if distribution.version != version:
        raise RuntimeError(f"Expected {package} {version}, found {distribution.version}")

    package_path = Path(distribution.locate_file(config["package_root"])).resolve()
    source_files = sorted(package_path.rglob("*.py"))
    if not source_files:
        raise FileNotFoundError(f"No Python source files found under {package_path}")

    module_root = config["module_root"]
    modules: dict[str, dict[str, Any]] = {}
    totals = {
        "total_modules": 0,
        "total_classes": 0,
        "total_methods": 0,
        "total_properties": 0,
        "total_functions": 0,
    }
    sdk_files = []
    metadata_evidence = []
    support_evidence = None
    for source in source_files:
        source_path = source.as_posix()
        relative = source.relative_to(package_path).as_posix()
        suffix = relative.removesuffix(".py").replace("/", ".")
        module_name = module_root + (
            "." + suffix.removesuffix(".__init__") if suffix != "__init__" else ""
        )
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

    if config.get("include_distribution_metadata"):
        metadata_file = next(
            (
                file
                for file in distribution.files or []
                if str(file).endswith(".dist-info/METADATA")
            ),
            None,
        )
        if metadata_file is None:
            raise FileNotFoundError(f"No distribution METADATA found for {package}")
        metadata_path = Path(distribution.locate_file(metadata_file)).resolve()
        metadata_hash = _digest(metadata_path)
        sdk_files.append({"path": metadata_path.as_posix(), "sha256": metadata_hash})
        metadata_text = distribution.read_text("METADATA") or ""
        for marker in config.get("metadata_evidence_markers", ()):
            statement = next(
                (line.strip() for line in metadata_text.splitlines() if marker in line),
                None,
            )
            if not statement:
                raise RuntimeError(f"No metadata evidence matching {marker!r} for {package}")
            metadata_evidence.append({
                "marker": marker,
                "statement": statement,
                "source_path": metadata_path.as_posix(),
                "sha256": metadata_hash,
            })
        support_marker = config.get("support_statement_marker")
        if support_marker:
            statement = next(
                (line.strip() for line in metadata_text.splitlines() if support_marker in line),
                None,
            )
            if not statement:
                raise RuntimeError(f"No metadata support statement matching {support_marker!r}")
            support_evidence = {
                "statement": statement,
                "source_path": metadata_path.as_posix(),
                "sha256": metadata_hash,
            }

    if not any(totals[key] for key in ("total_classes", "total_methods", "total_functions")):
        raise RuntimeError(f"The {package} SDK source contains no direct public declarations")

    output_path = REPO_ROOT / "docs" / "api_inventory" / f"{target}_api.json"
    snapshot = {
        "module": module_root,
        "version": "unknown",
        "sdk_package": package,
        "sdk_version": version,
        "interface": config["interface"],
        "product_support_statement": (
            support_evidence["statement"] if support_evidence else "Not established by this snapshot."
        ),
        "support_evidence": support_evidence,
        "metadata_evidence": metadata_evidence,
        "scope": (
            f"Static AST extraction of direct declarations under {module_root}. "
            "Includes classes, methods, properties, and functions whose names do not start "
            "with an underscore. Does not import the package, resolve __all__ re-exports, "
            "connect to or run the ANSYS product, or establish official API support. "
            + config.get("scope_note", "")
        ),
        "sources": {"sdk_files": sdk_files},
        "modules": modules,
        "statistics": totals,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f"{target}_api.", suffix=".tmp", dir=output_path.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(snapshot, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, output_path)
    except BaseException:
        Path(temp_name).unlink(missing_ok=True)
        raise
    return snapshot


def extract_sherlock_api() -> dict[str, Any]:
    return extract_python_sdk_api("sherlock_core")


def extract_rocky_api() -> dict[str, Any]:
    return extract_python_sdk_api("rocky")


def extract_cfx_api() -> dict[str, Any]:
    return extract_python_sdk_api("cfx")


def extract_speos_api() -> dict[str, Any]:
    return extract_python_sdk_api("speos")


if __name__ == "__main__":
    result = extract_sherlock_api()
    print(json.dumps(result["statistics"], ensure_ascii=False))
