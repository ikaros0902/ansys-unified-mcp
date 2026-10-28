"""建立 ANSYS 產品的直接 API 快照覆蓋清冊。"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "src" / "ansys_unified_mcp" / "resources" / "manifests" / "document_sources.json"
API_DIR = REPO_ROOT / "docs" / "api_inventory"
OUTPUT_PATH = API_DIR / "api_coverage.json"
DOCUMENT_COVERAGE_PATH = REPO_ROOT / "ANSYS_Document" / "_catalog" / "coverage.json"
REA_EVIDENCE = {
    "mechanical": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Mechanical DataModel; Ansys.Mechanical.Interfaces.dll; Ansys.Mechanical.DataModel.dll",
        "version": "v251",
    },
    "spaceclaim": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "SpaceClaim.Api.V251.dll; SpaceClaim.Api.V251.Scripting.dll",
        "version": "v251",
    },
    "act": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Ansys.ACT.Interfaces.dll; Ansys.ACT.Core.dll",
        "version": "v251",
    },
    "additive": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Ansys.Api.Additive.dll",
        "version": "v251",
    },
    "lsdyna": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Ansys.ACTLSDYNA.Interfaces.dll",
        "version": "v251",
    },
    "ansysem": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Ansys.Ansoft.CoreCOMScripting.dll; Ansys.Ansoft.CoreDotNet.dll",
        "version": "v251",
    },
    "hfss": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Ans.Ansoft.HFSSAddinPlugin.dll",
        "version": "v251",
    },
    "aqwa": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Ans.AQWA.Core.dll",
        "version": "v251",
    },
    "fluent": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Ans.Fluent.dll",
        "version": "v251",
    },
    "icepak": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Ans.Icepak.Core.dll; Ans.Ansoft.IcepakAddinPlugin.dll",
        "version": "v251",
    },
    "polyflow": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Ans.Polyflow.dll",
        "version": "v251",
    },
    "sherlock": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Ans.Sherlock.Addin.dll",
        "version": "v251",
    },
    "dpf": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "23 個 `Ans.Dpf.*` PE 元件（native exports，詳見 REA_EVIDENCE.md）",
        "version": "v251",
    },
    "cfx": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Ans.CFX.CadApi.dll; Ans.CFX.CFXCore.dll",
        "version": "v251",
    },
    "granta_mi": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Ansys.Apip.Client.dll",
        "version": "v251",
    },
    "discovery": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Ansys.Collaboration.Api.dll; Ansys.Gateway.Api.dll; Ansys.Geometry.Api.dll; Ansys.OnScale.Api.dll; Ansys.Physics.Api.dll; Ansys.Project.Api.dll; Ansys.Results.Api.dll",
        "version": "v251",
    },
    "maxwell": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Ans.Ansoft.MaxwellAddinPlugin.dll",
        "version": "v251",
    },
    "q3d": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Ans.Ansoft.Q3DExtractorAddinPlugin.dll",
        "version": "v251",
    },
    "speos": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Optical Products/Speos/bin/ApipWrapper.dll",
        "version": "v251",
    },
    "zemax": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Zemax OpticStudio/ZOSAPI.dll; Zemax OpticStudio/ZOSAPI_Interfaces.dll",
        "version": "v251",
    },
    "lumerical": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Lumerical Python and Tcl interop DLLs (native export evidence)",
        "version": "v251",
    },
    "system_coupling": {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "SysC.AnsRpc.Wrapper.dll; SysC.SystemCouplingParticipant.dll (native PE exports)",
        "version": "v251",
    },
}
API_SUFFIX = "_api.json"
# PyDyna is a distinct SDK under the manifest's existing LS-DYNA product ID.
SNAPSHOT_PRODUCT_ALIASES = {"pydyna": "lsdyna", "mechanical_core": "mechanical", "geometry_core": "geometry", "optislang_core": "optislang", "workbench_protocol": "workbench", "mechanical_protocol": "mechanical", "geometry_protocol": "geometry", "fluent_protocol": "fluent", "mapdl_protocol": "mapdl", "primemesh_protocol": "primemesh", "discovery_protocol": "discovery"}
SHARED_INTERFACES = {"ls_prepost"}


def _load_json(path: Path) -> tuple[bytes, Any]:
    try:
        raw = path.read_bytes()
        data = json.loads(raw.decode("utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"無法讀取有效 JSON：{path}: {exc}") from exc
    return raw, data


def _required_string(record: dict[str, Any], key: str, context: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context} 缺少有效的 {key}")
    return value


def _optional_string(record: dict[str, Any], key: str, context: str) -> str | None:
    value = record.get(key)
    if value is not None and not isinstance(value, str):
        raise ValueError(f"{context} 的 {key} 必須是字串或 null")
    return value


def _load_products() -> list[dict[str, Any]]:
    _, manifest = _load_json(MANIFEST_PATH)
    if not isinstance(manifest, dict) or not isinstance(manifest.get("products"), list):
        raise ValueError("來源清冊格式錯誤：products 必須是陣列")

    products = []
    seen = set()
    for index, item in enumerate(manifest["products"]):
        context = f"來源清冊 products[{index}]"
        if not isinstance(item, dict):
            raise ValueError(f"{context} 必須是物件")
        product_id = _required_string(item, "product", context)
        if product_id in seen:
            raise ValueError(f"來源清冊含重複產品 ID：{product_id}")
        seen.add(product_id)
        products.append(
            {
                "product": product_id,
                "folder": _required_string(item, "folder", context),
                "overview_url": _optional_string(item, "overview_url", context),
                "sdk_package": _optional_string(item, "sdk_package", context),
            }
        )
    if not products:
        raise ValueError("來源清冊沒有產品資料")
    return sorted(products, key=lambda item: item["product"])


def _load_document_coverage() -> dict[str, list[dict[str, Any]]]:
    _, coverage = _load_json(DOCUMENT_COVERAGE_PATH)
    rows = coverage.get("rows") if isinstance(coverage, dict) else None
    if not isinstance(rows, list):
        raise ValueError("文件覆蓋清冊格式錯誤：rows 必須是陣列")

    by_product: dict[str, list[dict[str, Any]]] = {}
    for index, row in enumerate(rows):
        context = f"文件覆蓋清冊 rows[{index}]"
        if not isinstance(row, dict):
            raise ValueError(f"{context} 必須是物件")
        product_id = _required_string(row, "product", context)
        record = {
            key: _required_string(row, key, context)
            for key in ("release", "release_availability", "status")
        }
        for key in (
            "files",
            "indexed_candidates",
            "api_count",
            "guide_count",
            "ready_examples",
            "required_examples",
            "input_pending",
        ):
            value = row.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{context} 的 {key} 必須是非負整數")
            record[key] = value
        missing = row.get("missing")
        failed_sources = row.get("failed_sources")
        if not isinstance(missing, list) or any(not isinstance(item, str) for item in missing):
            raise ValueError(f"{context} 的 missing 必須是字串陣列")
        if not isinstance(failed_sources, list) or any(
            not isinstance(item, str) for item in failed_sources
        ):
            raise ValueError(f"{context} 的 failed_sources 必須是字串陣列")
        record["missing"] = missing
        record["failed_source_count"] = len(failed_sources)
        by_product.setdefault(product_id, []).append(record)

    return {
        product: sorted(items, key=lambda item: (item["release"], item["release_availability"]))
        for product, items in sorted(by_product.items())
    }


def _load_snapshots() -> dict[str, list[dict[str, Any]]]:
    if not API_DIR.is_dir():
        raise ValueError(f"API 快照目錄不存在：{API_DIR}")

    snapshot_paths = set(API_DIR.glob(f"*{API_SUFFIX}"))
    snapshot_paths.update(API_DIR.glob("*_api_v*.json"))
    snapshots: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(snapshot_paths, key=lambda item: item.name):
        versioned_match = re.fullmatch(r"(.+)_api_v.+\.json", path.name)
        if versioned_match:
            product_id = versioned_match.group(1)
        elif path.name.endswith(API_SUFFIX):
            product_id = path.name[: -len(API_SUFFIX)]
        else:
            continue

        product_id = SNAPSHOT_PRODUCT_ALIASES.get(product_id, product_id)
        raw, data = _load_json(path)
        if not isinstance(data, dict):
            raise ValueError(f"API 快照根節點必須是物件：{path}")
        version = data.get("version")
        statistics = data.get("statistics")
        if not isinstance(version, str) or not version.strip():
            raise ValueError(f"API 快照缺少有效的 version：{path}")
        if not isinstance(statistics, dict) or any(
            not isinstance(key, str)
            or not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
            for key, value in statistics.items()
        ):
            raise ValueError(f"API 快照 statistics 格式錯誤：{path}")
        snapshot = {
            "snapshot_path": path.relative_to(REPO_ROOT).as_posix(),
            "snapshot_version": version,
            "statistics": statistics,
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
        if product_id in REA_EVIDENCE and re.search(r"(?<![a-z0-9])v251(?![a-z0-9])", version.lower()):
            snapshot["rea_evidence"] = REA_EVIDENCE[product_id]
        snapshots.setdefault(product_id, []).append(snapshot)

    return {
        product_id: sorted(
            items, key=lambda item: (item["snapshot_version"], item["snapshot_path"])
        )
        for product_id, items in sorted(snapshots.items())
    }


def build_report() -> dict[str, Any]:
    products = _load_products()
    snapshots = _load_snapshots()
    documentation_coverage = _load_document_coverage()
    product_ids = {item["product"] for item in products}
    unmapped_shared = sorted(
        product_id
        for product_id in SHARED_INTERFACES
        if product_id in product_ids and product_id not in snapshots
    )

    entries = []
    for product in products:
        product_id = product["product"]
        product_snapshots = snapshots.get(product_id, [])
        has_snapshot = bool(product_snapshots)
        mapping_status = (
            "direct_product_id"
            if has_snapshot
            else "product_component_evidence_only"
            if product_id in REA_EVIDENCE
            else "unmapped_shared_interface"
            if product_id in SHARED_INTERFACES
            else "not_assessed"
        )
        entries.append(
            {
                **product,
                "has_direct_snapshot": has_snapshot,
                "snapshot_status": "direct_snapshot" if has_snapshot else "no_direct_snapshot",
                "mapping_status": mapping_status,
                "snapshots": product_snapshots,
                "documentation_coverage": documentation_coverage.get(product_id, []),
                "rea_evidence": REA_EVIDENCE.get(product_id, {}),
            }
        )

    return {
        "schema_version": 3,
        "sources": {
            "api_snapshots": "docs/api_inventory/",
            "documentation_coverage": "ANSYS_Document/_catalog/coverage.json",
            "rea_evidence": "docs/api_inventory/REA_EVIDENCE.md",
        },
        "scope": {
            "description": (
                "API 快照只記錄目前可直接或透過明示 alias 對應產品 ID 的快照，不代表 API 完整度。"
                "documentation_coverage 是獨立的本機文件語料盤點，不證明 API 是否存在或完整。"
                "rea_evidence 指向靜態組件 metadata 或 PE export 摘要，不代表公開 API 已分類或完整。"
            ),
            "matching_rule": (
                "API 快照以 docs/api_inventory/<product>_api.json 與 <product>_api_v*.json 命名；"
                "除 SNAPSHOT_PRODUCT_ALIASES 明示對應外，產品 ID 精確配對。文件覆蓋列"
                "仍以 manifest 產品 ID 配對，保留來源版本；不推測版本或共享介面關係。"
            ),
            "snapshot_product_aliases": SNAPSHOT_PRODUCT_ALIASES,
            "unmapped_shared_interfaces": unmapped_shared,
        },
        "products": entries,
    }


def _write_atomic(report: dict[str, Any]) -> None:
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=OUTPUT_PATH.parent,
            prefix=f".{OUTPUT_PATH.name}.",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            json.dump(report, temp_file, ensure_ascii=False, indent=2, sort_keys=True)
            temp_file.write("\n")
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.replace(temp_path, OUTPUT_PATH)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def main() -> int:
    try:
        report = build_report()
        _write_atomic(report)
    except (OSError, ValueError) as exc:
        print(f"API 覆蓋清冊建立失敗：{exc}", file=sys.stderr)
        return 1

    print(f"已建立 API 覆蓋清冊：{OUTPUT_PATH}（{len(report['products'])} 個產品）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
