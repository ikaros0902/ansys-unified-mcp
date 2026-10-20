"""CADWorld FreeCAD .FCStd 專案檔免安裝純 Python 解析器。

遵循安全零磁碟解壓原則，不需安裝 FreeCAD / Linux VM 即可直接讀取 .FCStd
（本質為 ZIP 壓縮包，內含 Document.xml 與 BRep/Mesh 等資產），防禦 Zip Slip 與 Zip Bomb。
"""

from __future__ import annotations

import logging
import os
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# 單一檔案解壓上限 50MB (防禦 Zip Bomb 解壓炸彈)
MAX_FCSTD_MEMBER_BYTES = 50 * 1024 * 1024


def validate_fcstd_archive(path: str | Path) -> Dict[str, Any]:
    """檢驗 .FCStd 檔案結構完整性與安全邊界。

    回傳：
        dict: {"ok": bool, "archive_ok": bool, "document_xml_present": bool,
               "document_xml_parses": bool, "size_bytes": int, "members": dict, "error": str | None}
    """
    detail: Dict[str, Any] = {
        "ok": False,
        "archive_ok": False,
        "document_xml_present": False,
        "document_xml_parses": False,
        "size_bytes": 0,
        "members": {},
        "error": None,
    }

    p = Path(path)
    if not p.exists() or not p.is_file():
        detail["error"] = f"File does not exist: {path}"
        return detail

    try:
        detail["size_bytes"] = p.stat().st_size
        if detail["size_bytes"] == 0:
            detail["error"] = "File is empty (0 bytes)"
            return detail

        with zipfile.ZipFile(p, "r") as zf:
            # 1. 完整性校驗
            if zf.testzip() is not None:
                detail["error"] = "Corrupted zip archive (CRC check failed)"
                return detail
            detail["archive_ok"] = True

            # 2. 安全掃描 (防禦 Zip Slip 與 Zip Bomb)
            infolist = zf.infolist()
            for info in infolist:
                # 拒絕路徑遍歷
                if ".." in info.filename or info.filename.startswith(("/", "\\")):
                    detail["error"] = f"Malicious zip member detected (Zip Slip): {info.filename}"
                    detail["archive_ok"] = False
                    return detail
                # 拒絕超大單一檔案
                if info.file_size > MAX_FCSTD_MEMBER_BYTES:
                    detail["error"] = f"Zip member exceeds size limit ({info.file_size} > {MAX_FCSTD_MEMBER_BYTES}): {info.filename}"
                    detail["archive_ok"] = False
                    return detail

                detail["members"][info.filename] = {
                    "file_size": info.file_size,
                    "compress_size": info.compress_size,
                }

            if "Document.xml" not in detail["members"]:
                detail["error"] = "Missing Document.xml in archive"
                return detail
            detail["document_xml_present"] = True

            # 3. 記憶體流式解析 Document.xml (零磁碟寫入)
            with zf.open("Document.xml", "r") as doc_fp:
                xml_data = doc_fp.read(MAX_FCSTD_MEMBER_BYTES)
                ET.fromstring(xml_data)
                detail["document_xml_parses"] = True

    except (zipfile.BadZipFile, OSError, ET.ParseError, ValueError) as exc:
        detail["error"] = f"Parse failed: {exc}"
        return detail

    detail["ok"] = (
        detail["archive_ok"]
        and detail["document_xml_present"]
        and detail["document_xml_parses"]
    )
    return detail


def parse_fcstd_metadata(path: str | Path) -> Dict[str, Any]:
    """解析 .FCStd 之 Document.xml，提取物件樹、類型、標籤、材料與邊界條件。

    轉換為標準化中繼字典，供 Staged Diagnostics 與 ANSYS Mechanical 結構樹映射使用。
    """
    valid_res = validate_fcstd_archive(path)
    if not valid_res["ok"]:
        return {
            "ok": False,
            "error": valid_res["error"],
            "failure_class": "corrupted_artifact",
            "objects": [],
            "object_count": 0,
            "types": [],
            "labels": [],
            "archive_files": {},
        }

    p = Path(path)
    objects_meta: List[Dict[str, Any]] = []
    types_set: set[str] = set()
    labels_set: set[str] = set()
    materials: List[Dict[str, Any]] = []
    constraints: List[Dict[str, Any]] = []
    mesh_info: Dict[str, Any] = {}

    try:
        with zipfile.ZipFile(p, "r") as zf:
            with zf.open("Document.xml", "r") as doc_fp:
                tree = ET.parse(doc_fp)
                root = tree.getroot()

            # 解析 <Objects> 區塊
            objects_node = root.find("Objects")
            if objects_node is not None:
                for obj_el in objects_node.findall("Object"):
                    obj_name = obj_el.get("name", "")
                    obj_type = obj_el.get("type", "")
                    types_set.add(obj_type)

                    # 讀取 properties 中的 Label
                    label = obj_name
                    props_node = obj_el.find("Properties")
                    prop_map: Dict[str, Any] = {}
                    if props_node is not None:
                        for prop_el in props_node.findall("Property"):
                            prop_name = prop_el.get("name", "")
                            # 提取文字或數值
                            str_child = prop_el.find("String")
                            if str_child is not None and str_child.get("value") is not None:
                                prop_map[prop_name] = str_child.get("value")
                            float_child = prop_el.find("Float")
                            if float_child is not None and float_child.get("value") is not None:
                                try:
                                    prop_map[prop_name] = float(float_child.get("value"))
                                except ValueError:
                                    pass

                    if "Label" in prop_map:
                        label = str(prop_map["Label"])
                    labels_set.add(label)

                    obj_data = {
                        "name": obj_name,
                        "type": obj_type,
                        "label": label,
                        "properties": prop_map,
                    }
                    objects_meta.append(obj_data)

                    # 針對材料 (MaterialObject / MaterialSolid)
                    if "Material" in obj_type or "Material" in label:
                        materials.append(obj_data)

                    # 針對約束 (ConstraintFixed / ConstraintForce)
                    if "Constraint" in obj_type or "Constraint" in label:
                        constraints.append(obj_data)

                    # 針對 Gmsh 網格
                    if "Mesh" in obj_type or "Gmsh" in label:
                        mesh_info[label] = obj_data

    except Exception as exc:
        return {
            "ok": False,
            "error": f"Failed extracting metadata: {exc}",
            "failure_class": "corrupted_artifact",
            "objects": [],
            "object_count": 0,
            "types": [],
            "labels": [],
            "archive_files": {},
        }

    return {
        "ok": True,
        "error": None,
        "object_count": len(objects_meta),
        "types": sorted(list(types_set)),
        "labels": sorted(list(labels_set)),
        "objects": objects_meta,
        "materials": materials,
        "constraints": constraints,
        "mesh_info": mesh_info,
        "archive_files": valid_res["members"],
    }
